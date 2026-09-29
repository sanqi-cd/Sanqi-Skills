# Learning Plan Data Contract (v2)

Write a UTF-8 JSON object before rendering. The canonical, complete examples are `examples/learning-path-designer/ai-content-creator/learning-plan.json` and `examples/learning-path-designer/data-analyst-transition/learning-plan.json` at the repository root.

## Required fields

| Field | Shape | Purpose |
| --- | --- | --- |
| `schema_version` | integer `2` | Prevents rendering old, incomplete plans. |
| `total_days` | positive integer | Length of the entire path. |
| `title`, `learner`, `start_state`, `goal_state`, `time_budget`, `today_win` | non-empty strings | Learner context and first action. |
| `methodologies`, `diagnosis`, `knowledge_tree`, `task_tree`, `final_deliverables`, `toolbelt`, `validation_standards`, `review_rules` | non-empty arrays of non-empty strings | Diagnosis, route, evidence and adaptation. |
| `review_questions` | object with non-empty `daily` and `weekly` strings | Prompts for review. |
| `phases` | array of 4-6 stage objects | Growth route. |
| `action_groups` | non-empty array of action-group objects | Executable plan covering days 1 through `total_days`. |

Each `phases` item needs unique `id`, `title`, `duration`, `ability`, `deliverable`, `pass_criteria`, and a non-empty string array `tasks`. Phase tasks summarize the route; the detailed checkable tasks belong in `action_groups`.

Each `action_groups` item needs a `label`, integer `start_day` and `end_day`, and non-empty `tasks`. Day ranges must be consecutive, non-overlapping, and cover the whole period. Each task is an object with non-empty `title`, `output`, `check`, and positive integer `minutes`.

Example action group:

```json
{
  "label": "第 1 周",
  "start_day": 1,
  "end_day": 7,
  "tasks": [
    {
      "title": "整理受众真实问题",
      "minutes": 60,
      "output": "10 条原话记录",
      "check": "每条记录可回到留言或访谈来源"
    }
  ]
}
```

Keep only user-facing plan data in JSON. Do not include HTML, JavaScript, comments, secrets or private source material without the user's authorization. Validate with `scripts/render_growth_map.py` before delivery.
