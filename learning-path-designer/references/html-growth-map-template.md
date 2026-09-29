# HTML Growth Map Contract

Use `scripts/render_growth_map.py` as the single source of HTML, CSS, and JavaScript. Do not copy an alternate page template into a response: it may drift from the renderer and its validator.

## Data to prepare

Write a UTF-8 `learning-plan.json` following `learning-plan-schema.md`. The JSON must include a diagnosis, 4-6 stages, full-period action groups, task outputs and checks, final deliverables, toolbelt, validation standards, and daily/weekly review questions.

For each action group, choose a short label and a consecutive day range. Prefer groups of no more than one week when the period is long. Each task should be concrete enough to check off and should specify effort in minutes, an observable output, and a check.

## Render and validate

```bash
python3 scripts/render_growth_map.py learning-plan.json learning-path-outputs/growth-map.html
python3 scripts/validate_growth_map.py learning-path-outputs/growth-map.html
```

Both commands must succeed before delivery. Keep generated files in the user's working area, not inside the skill package.

## Resulting map

The renderer provides a standalone responsive page with no external assets. It shows the learner's starting and goal states, diagnosis and method combination, stage navigation, weekly action cards with persistent completion state, knowledge and task trees, deliverables, toolbelt, validation standards, and review prompts. Test the page in a browser when one is available, including stage switching, task checking, refresh persistence, and a narrow viewport.

Examples of valid source data and generated pages live under `examples/learning-path-designer/` in this repository.
