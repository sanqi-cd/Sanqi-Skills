# Learning Plan Data Contract

Before rendering the growth map, write a UTF-8 JSON object with this shape:

```json
{
  "title": "30 天从零到能独立完成数据分析报告",
  "learner": "运营专员，零编程基础",
  "start_state": "依赖手工整理 Excel",
  "goal_state": "能用 Python 自动清洗并汇总周报数据",
  "time_budget": "每天 1 小时，共 30 天",
  "methodologies": ["项目制学习", "刻意练习", "检索练习"],
  "phases": [
    {
      "id": "phase-1",
      "title": "建立最小基础",
      "duration": "第 1-5 天",
      "ability": "读写表格并理解变量与循环",
      "tasks": ["完成两个小练习", "整理一页错题笔记"],
      "deliverable": "可运行的数据读取脚本",
      "pass_criteria": "用新文件运行脚本并解释输出"
    }
  ],
  "today_win": "安装环境并成功读取一个真实 Excel 文件",
  "review_rules": ["连续两次未通过时缩小任务粒度", "每周用作品而非学习时长复盘"]
}
```

## Constraints

- Include 4-6 phases in chronological order.
- Give every phase at least one task, one observable deliverable, and one binary pass criterion.
- Make `id` values unique lowercase slugs.
- Cover the user's complete requested period, not only the first week.
- Put only user-facing content in the JSON. Do not include HTML, JavaScript, comments, or secrets.
