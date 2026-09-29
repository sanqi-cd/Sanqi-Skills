# 评测运行说明

`scripts/validate_repository.py` 只检查评测数据集结构，不执行模型评测。以下命令需要本机安装并登录 Codex CLI，会发起模型调用，因此不纳入无凭据的 GitHub Actions。

## 触发边界模拟

```bash
python3 scripts/run_evals.py routing --skill learning-path-designer --report /tmp/learning-routing.json
```

该模式逐条读取 `trigger-evals.json`，用 `SKILL.md` 的 description 模拟元数据路由，输出每条正负例的判断与总体通过率。它**不是** Codex、Claude Code 或其他客户端真实安装后的自动触发测试；发布前仍应在目标客户端抽测边界请求。

## 实际输出评分

先在目标客户端执行 `evals/evals.json` 的案例，并将每条真实执行结果保存为 JSON。输入形状：

```json
{
  "skill_name": "skill-builder",
  "cases": [
    {"id": 1, "response": "实际运行后保存的完整回复和交付证据"}
  ]
}
```

然后运行：

```bash
python3 scripts/run_evals.py output --skill skill-builder --submissions /path/to/submissions.json --report /tmp/skill-builder-output.json
```

缺少的案例计为失败。评分器仅依据保存的文本判断 assertions；文件存在性、视觉质量、来源真实性和端到端工具调用仍要分别验证。案例提示词若依赖未附上的“这篇文章”等外部输入，应先补齐真实输入再执行，不能用想象的产物充数。`--limit N` 可试运行前 N 条，`--case-index N` 可单独测试第 N 条边界案例。
