import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "validate_repository", ROOT / "scripts" / "validate_repository.py"
)
validate_repository = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validate_repository)


class RepositoryValidatorTest(unittest.TestCase):
    def test_top_level_keys_ignore_nested_metadata(self):
        content = """---
name: demo
description: Demo
metadata:
  author: "demo"
---
"""
        self.assertEqual(
            validate_repository.top_level_keys(content),
            {"name", "description", "metadata"},
        )

    def test_all_repository_skills_are_discoverable(self):
        names = {skill["name"] for skill in validate_repository.scan_skills(ROOT)}
        self.assertEqual(
            names,
            {
                "learning-path-designer",
                "paper-explainer",
                "skill-builder",
                "xhs-image-text-generator",
                "youtube-podcast-to-md",
            },
        )

    def test_eval_fixture_requirements(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill_dir = root / "demo"
            eval_dir = skill_dir / "evals"
            eval_dir.mkdir(parents=True)
            cases = [
                {
                    "prompt": "Test prompt",
                    "expected_output": "Test output",
                    "assertions": ["Test assertion"],
                    "input_status": "self_contained",
                }
                for _ in range(3)
            ]
            cases[1]["input_status"] = "needs_fixture"
            (eval_dir / "evals.json").write_text(
                json.dumps({"skill_name": "demo", "evals": cases}), encoding="utf-8"
            )
            (eval_dir / "trigger-evals.json").write_text(
                json.dumps({"skill_name": "demo", "cases": [
                    {"prompt": "Test", "reason": "Test", "should_trigger": index % 2 == 0}
                    for index in range(12)
                ]}),
                encoding="utf-8",
            )

            with patch.object(validate_repository, "ROOT", root):
                errors = []
                validate_repository.validate_eval_files(skill_dir, "demo", errors)
                self.assertTrue(any("case 2 must describe its missing fixture" in error for error in errors))

                cases[1]["fixture_requirements"] = "Attach a readable source document."
                (eval_dir / "evals.json").write_text(
                    json.dumps({"skill_name": "demo", "evals": cases}), encoding="utf-8"
                )
                errors = []
                validate_repository.validate_eval_files(skill_dir, "demo", errors)
                self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
