"""仅做AM内存/物理布局接收；取整算术、指令字和golden全部来自inline-asm。"""
import csv
import re
import struct


def add_dma_trace(code, bindings):
    """一次扫描插入诊断点，避免大RNS程序按每条DMA重复扫描整份C；不改指令字。"""
    by_instruction = {int(row["instruction_index"]): row for row in bindings}
    if len(by_instruction) != len(bindings):
        raise ValueError("duplicate DMA trace instruction")
    seen = set()

    def insert(match):
        index = int(match[1])
        row = by_instruction.get(index)
        if row is None:
            return match[0]
        if index in seen:
            raise ValueError("duplicate producer instruction marker")
        seen.add(index)
        return match[0] + f"    trace_issue({index}U, {row['dma_index']}U, {row['word_hex']}U);\n"

    result = re.sub(r"^    /\* (\d+): [^\n]+ \*/\n", insert, code, flags=re.M)
    if seen != set(by_instruction):
        raise ValueError("missing DMA trace insertion marker")
    return result


def coefficients_to_physical(data, degree):
    values = struct.unpack(f"<{degree}I", data)
    bits = degree.bit_length() - 1
    physical = [values[int(f"{i:0{bits}b}"[::-1], 2)] for i in range(degree)]
    return struct.pack(f"<{degree}I", *physical)


def adapt_bfv_image(image, allocations, degree):
    for allocation in allocations:
        # BFV ciphertext/plaintext 是 SEAL 自然系数顺序；NTT/key/twiddle 已是物理域。
        if allocation["kind"] not in ("ciphertext", "plaintext"):
            continue
        first = int(allocation["line_offset"]) * 256
        if int(allocation["payload_words"]) != degree:
            raise ValueError("BFV coefficient allocation shape changed")
        image[first:first + degree * 4] = coefficients_to_physical(
            image[first:first + degree * 4], degree)


def preserve_ckks_inputs(files, image, allocations, operations):
    """只重定位会覆盖只读输入/逐节点golden的DMA，不新增或重编码HPU指令。"""
    code = files["program_source"].read_text()
    with files["dma_relocation_manifest"].open() as stream:
        dma = list(csv.DictReader(stream))
    by_id = {row["allocation_id"]: row for row in allocations}
    shadows, diverted = {}, set()
    for binding in dma:
        if not binding["operation_index"]:
            continue
        operation = operations[int(binding["operation_index"])]
        name = binding["allocation_id"]
        if operation["kind"] not in ("relinearize", "rescale") or not any(
                name.startswith(value + "/") for value in operation["inputs"]):
            continue
        original = by_id[name]
        # 上游明确声明的mutable workspace允许原地写回，不另造一份数据。
        # 只读输入和已作为golden保存的output则必须保持原值。
        if original["read_only"] != "true" and original["kind"] != "output":
            continue
        key = (binding["operation_index"], name)
        if binding["direction"] == "dstore":
            if key not in shadows:
                first = len(image) // 256
                image += b"\0" * (int(original["line_count"]) * 256)
                shadows[key] = {**original, "allocation_id": f"am/shadow/step{key[0]}/{name}",
                                "kind": "workspace", "read_only": "false",
                                "line_offset": str(first), "initialization": "zero_reserved"}
                allocations.append(shadows[key])
            diverted.add(key)
        if key in diverted:
            # 首次INTT仍读原NTT输入；系数写回及之后的系数读取走私有workspace。
            binding.update({field: shadows[key][field] for field in
                            ("allocation_id", "line_offset", "line_count")})
    if not shadows:
        return None

    spans = "\n".join(f"    {{ UINT32_C({row['line_offset']}), UINT32_C({row['line_count']}) }},"
                      for row in dma)
    code, count = re.subn(
        r"(static const hpu_dma_span_t \w+_resolved_spans\[\] = \{)\n.*?\n};",
        lambda match: match[1] + "\n" + spans + "\n};", code, flags=re.S)
    if count != 1:
        raise ValueError("resolved span declaration changed")
    code, count = re.subn(r"#define HPU_MEM_LINE_COUNT UINT64_C\(\d+\)",
                          f"#define HPU_MEM_LINE_COUNT UINT64_C({len(image)//256})", code)
    if count != 1:
        raise ValueError("window line count declaration changed")
    # Native ASM/INST32/CMD26/header原样保留，变化仅限DDR地址和window上界。
    return {"code": code, "dma": dma, "instructions_added": 0,
            "input_shadow_count": len(shadows)}
