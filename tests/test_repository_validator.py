import importlib.util
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
