"""只缩减中间DDR输出，不缩减mark_output声明的golden验收。"""
import copy
import unittest

from import_package import exported_steps


class ExportedOutputTests(unittest.TestCase):
    def setUp(self):
        self.graph = {
            "operations": [
                {"id": "mul", "kind": "multiply", "output": "tensor", "exported": False},
                {"id": "reline", "kind": "relinearize", "output": "result", "exported": True,
                 "golden_object_id": "step_1"}],
            "final_output": "result",
            "marked_outputs": [{"id": "answer", "physical_output": "result"}]}

    def test_hmul_tensor_can_remain_internal_but_reline_result_is_required(self):
        self.assertEqual(exported_steps(self.graph), {1})

    def test_marked_intermediate_output_is_preserved_as_a_separate_check(self):
        self.graph["operations"][0].update(exported=True, golden_object_id="step_0")
        self.graph["marked_outputs"].append({"id": "tensor", "physical_output": "tensor"})
        self.assertEqual(exported_steps(self.graph), {0, 1})

    def test_plan_example_can_declare_only_its_final_export_without_frontend_labels(self):
        del self.graph["marked_outputs"]
        self.assertEqual(exported_steps(self.graph), {1})

    def test_missing_string_or_integer_export_flags_are_not_accepted(self):
        for value in (None, "false", 0, 1):
            graph = copy.deepcopy(self.graph)
            graph["operations"][0]["exported"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "boolean"):
                exported_steps(graph)

    def test_removed_final_output_or_fake_golden_metadata_is_rejected(self):
        for index in (0, 1):
            graph = copy.deepcopy(self.graph)
            graph["operations"][index]["golden_object_id"] = "wrong"
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, "golden object"):
                exported_steps(graph)
        self.graph["operations"][1].update(exported=False)
        with self.assertRaisesRegex(ValueError, "final output"):
            exported_steps(self.graph)

    def test_marked_outputs_cannot_be_missing_duplicated_or_redirected(self):
        for marked in ([], [{"id": "answer", "physical_output": "tensor"}],
                       self.graph["marked_outputs"] * 2):
            graph = copy.deepcopy(self.graph)
            graph["marked_outputs"] = marked
            with self.subTest(marked=marked), self.assertRaises(ValueError):
                exported_steps(graph)


if __name__ == "__main__":
    unittest.main()
