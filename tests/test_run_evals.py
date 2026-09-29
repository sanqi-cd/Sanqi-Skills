import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("run_evals", ROOT / "scripts" / "run_evals.py")
run_evals = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_evals)


class RunEvalsTest(unittest.TestCase):
    def test_loads_routing_cases_and_metadata(self):
        cases = run_evals.load_cases("learning-path-designer", "routing")
        self.assertEqual(len(cases), 12)
        self.assertIn("学习路径", run_evals.skill_description("learning-path-designer"))

    def test_routing_compares_boolean_labels(self):
        case = {"prompt": "规划学习路径", "should_trigger": True}
        with patch.object(run_evals, "ask_model", return_value={"should_trigger": True, "evidence": "roadmap"}):
            self.assertTrue(run_evals.evaluate_case("learning-path-designer", "routing", case)["passed"])

    def test_output_requires_saved_response_and_grades_each_assertion(self):
        case = {"id": 1, "prompt": "Do the task", "expected_output": "An artifact",
                "assertions": ["Has A", "Has B"], "response": "A complete result"}
        with patch.object(run_evals, "ask_model", return_value={"results": [
            {"passed": True, "evidence": "A"}, {"passed": False, "evidence": "B missing"}
        ]}):
            result = run_evals.evaluate_case("skill-builder", "output", case)
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["checks"]), 2)
        case["response"] = ""
        self.assertEqual(run_evals.evaluate_case("skill-builder", "output", case)["error"], "missing saved response")

    def test_output_loads_submissions_by_case_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "submissions.json"
            path.write_text(json.dumps({"skill_name": "skill-builder", "cases": [
                {"id": 1, "response": "saved run"}
            ]}), encoding="utf-8")
            cases = run_evals.load_cases("skill-builder", "output", path)
        self.assertEqual(cases[0]["response"], "saved run")
        self.assertEqual(cases[1]["response"], "")

    def test_selects_one_negative_case_by_index(self):
        cases = run_evals.load_cases("learning-path-designer", "routing")
        selected = run_evals.select_cases(cases, None, 7)
        self.assertEqual(len(selected), 1)
        self.assertFalse(selected[0]["should_trigger"])


if __name__ == "__main__":
    unittest.main()
