import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


render_growth_map = load_module(
    "render_growth_map", ROOT / "learning-path-designer" / "scripts" / "render_growth_map.py"
)
validate_growth_map = load_module(
    "validate_growth_map", ROOT / "learning-path-designer" / "scripts" / "validate_growth_map.py"
)


def sample_plan():
    return {
        "title": "四周学习路径",
        "learner": "零基础学习者",
        "start_state": "尚未入门",
        "goal_state": "能完成独立作品",
        "time_budget": "每周 6 小时",
        "methodologies": ["项目制学习"],
        "knowledge_tree": ["核心概念", "常见模式"],
        "task_tree": ["完成练习", "交付作品"],
        "final_deliverables": ["知识地图", "独立作品"],
        "phases": [
            {
                "id": f"phase-{index}",
                "title": f"阶段 {index}",
                "duration": f"第 {index} 周",
                "ability": "获得可观察能力",
                "tasks": ["完成练习"],
                "deliverable": "一个作品",
                "pass_criteria": "能够独立演示",
            }
            for index in range(1, 5)
        ],
        "today_win": "完成第一个练习",
        "review_rules": ["每周复盘作品"],
    }


class LearningPathToolsTest(unittest.TestCase):
    def test_rendered_map_passes_validation(self):
        plan = sample_plan()
        self.assertEqual(render_growth_map.validate_plan(plan), [])
        output = render_growth_map.render(plan)
        self.assertEqual(validate_growth_map.validate_html(output), [])
        self.assertIn("四周学习路径", output)
        self.assertIn("全周期行动卡", output)
        self.assertIn("成果展台", output)

    def test_rejects_too_few_phases(self):
        plan = sample_plan()
        plan["phases"] = plan["phases"][:2]
        self.assertIn("phases must contain 4-6 items", render_growth_map.validate_plan(plan))

    def test_rejects_missing_learning_trees(self):
        plan = sample_plan()
        del plan["knowledge_tree"]
        self.assertIn(
            "knowledge_tree must contain non-empty strings",
            render_growth_map.validate_plan(plan),
        )

    def test_cli_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "plan.json"
            output = root / "map.html"
            source.write_text(json.dumps(sample_plan(), ensure_ascii=False), encoding="utf-8")
            plan = json.loads(source.read_text(encoding="utf-8"))
            output.write_text(render_growth_map.render(plan), encoding="utf-8")
            self.assertTrue(output.is_file())
            self.assertEqual(validate_growth_map.validate_html(output.read_text(encoding="utf-8")), [])


if __name__ == "__main__":
    unittest.main()
