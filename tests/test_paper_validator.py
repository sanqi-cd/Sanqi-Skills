import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "paper_validate_note", ROOT / "paper-explainer" / "scripts" / "validate_note.py"
)
validate_note = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validate_note)


VALID_NOTE = """# Demo Paper

**作者**: A. Researcher | **链接**: https://example.org/paper

## 来源与证据边界
使用论文全文。

## 一句话速读
论文提出一个方法。

## 引言
作者陈述：现有方法存在问题。[p. 1]

## 方法
解读：该模块可以理解为过滤器。[§3.2]

## 实验
论文证据：表格显示基线差异。[Table 2]

## 局限与边界
样本范围有限。
"""


class PaperValidatorTest(unittest.TestCase):
    def test_accepts_evidence_bounded_note(self):
        self.assertEqual(validate_note.validate_note(VALID_NOTE), [])

    def test_rejects_abstract_only_shape(self):
        errors = validate_note.validate_note("# Paper\n\n## 一句话速读\n只有摘要。")
        self.assertIn("missing section: 证据边界", errors)
        self.assertTrue(any("locators" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
