#!/usr/bin/env python3
"""接收器只保留受保护输入，不再产生取整数据或数学指令。"""
import csv
from pathlib import Path
import tempfile
import unittest

from program_adaptation import preserve_ckks_inputs

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '''#define HPU_MEM_LINE_COUNT UINT64_C(1)
int body(void) {
    __asm__ volatile(".word 0x00B5202B");
    __asm__ volatile(".word 0x7000005B");
    return 0;
}
static const hpu_dma_span_t probe_resolved_spans[] = {
    { UINT32_C(0), UINT32_C(1) },
    { UINT32_C(0), UINT32_C(1) },
    { UINT32_C(0), UINT32_C(1) },
};
'''


class PreservationTests(unittest.TestCase):
    def check_kind(self, kind, readonly, protect):
        parent = ROOT / "build/input-preservation-tests"
        parent.mkdir(parents=True, exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix="case-", dir=parent))
        code, manifest = root / "probe.c", root / "dma.csv"
        try:
            code.write_text(SOURCE)
            bindings = [{"operation_index": "0", "operation_id": "tested", "allocation_id": "input/x/c0/mod0",
                         "direction": direction, "line_offset": "0", "line_count": "1", "word_hex": "0x00B5202B"}
                        for direction in ("dload", "dstore", "dload")]
            with manifest.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(bindings[0]))
                writer.writeheader(); writer.writerows(bindings)
            allocations = [{"allocation_id": "input/x/c0/mod0", "kind": kind, "read_only": readonly,
                            "line_offset": "0", "line_count": "1", "initialization": "payload"}]
            image = bytearray(b"\x11" * 256)
            result = preserve_ckks_inputs({"program_source": code, "dma_relocation_manifest": manifest},
                                          image, allocations, [{"kind": "relinearize", "inputs": ["input/x"]}])
            if protect:
                self.assertEqual(result["instructions_added"], 0)
                self.assertEqual(result["input_shadow_count"], 1)
                self.assertEqual([row["line_offset"] for row in result["dma"]], ["0", "1", "1"])
                self.assertEqual([row["word_hex"] for row in result["dma"]], ["0x00B5202B"] * 3)
                self.assertIn(SOURCE.split("static const")[0].replace("UINT64_C(1)", "UINT64_C(2)"), result["code"])
                self.assertEqual(image, b"\x11" * 256 + b"\0" * 256)
            else:
                self.assertIsNone(result)
                self.assertEqual(image, b"\x11" * 256)
        finally:
            if code.exists(): code.unlink()
            if manifest.exists(): manifest.unlink()
            root.rmdir()

    def test_readonly_input_is_preserved_without_reencoding(self):
        self.check_kind("ciphertext", "true", True)

    def test_previous_output_checkpoint_is_preserved(self):
        self.check_kind("output", "false", True)

    def test_upstream_mutable_workspace_is_used_natively(self):
        self.check_kind("workspace", "false", False)


if __name__ == "__main__":
    unittest.main()
