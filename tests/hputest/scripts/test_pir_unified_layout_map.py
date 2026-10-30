"""The producer's logical mapping must bind exactly to the imported image."""

from pathlib import Path
import struct
import tempfile
import unittest

from pir_unified_layout import N, read_dynamic_input_map


class DynamicInputMapTests(unittest.TestCase):
    def test_explicit_bindings_reject_permuted_and_duplicate_input(self):
        with tempfile.TemporaryDirectory(prefix="pir-dynamic-map-") as temporary:
            directory = Path(temporary)
            rows = []
            image = bytearray(102 * N * 4)
            for identity in range(34):
                for basis in range(3):
                    slot = identity * 3 + basis
                    payload = struct.pack("<I", slot + 1) * N
                    image[slot * N * 4:(slot + 1) * N * 4] = payload
                    rows.append({"allocation_id": f"frontend/plains/plain_{identity}"
                                  f"/multiply/level_2/c0/mod{basis}",
                                 "line_offset": str(slot * N // 64),
                                 "payload_words": str(N), "read_only": "true"})
            entries = []
            for rank in range(96):
                slot = 6 + rank
                name = f"dynamic_{rank}.u32.bin"
                (directory / name).write_bytes(image[slot * N * 4:(slot + 1) * N * 4])
                entries.append([rows[slot]["allocation_id"], name])
            mapping = directory / "dynamic_inputs.tsv"

            def write():
                mapping.write_text("".join("\t".join(row) + "\n" for row in entries),
                                   encoding="utf-8")

            write()
            bindings = read_dynamic_input_map(mapping, rows, image, [17, 19, 23])
            self.assertEqual([rank for _, rank, _ in bindings], list(range(96)))
            entries[0][0], entries[3][0] = entries[3][0], entries[0][0]
            write()
            with self.assertRaisesRegex(ValueError, "bytes differ"):
                read_dynamic_input_map(mapping, rows, image, [17, 19, 23])
            entries[0][0], entries[3][0] = entries[3][0], entries[0][0]
            entries[3][1] = entries[0][1]
            write()
            with self.assertRaisesRegex(ValueError, "repeats a binding"):
                read_dynamic_input_map(mapping, rows, image, [17, 19, 23])


if __name__ == "__main__":
    unittest.main()
