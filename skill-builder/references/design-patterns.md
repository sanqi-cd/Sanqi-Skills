# Skill 设计模式参考

生成 SKILL.md 时，根据任务性质推荐适用的设计模式：

| 模式 | 适用场景 | 示例 |
|------|---------|------|
| **Tool Wrapper** | 封装特定框架/工具的最佳实践 | "React 组件生成 Skill" |
| **Generator** | 需要一致的结构化输出 | "API 文档生成 Skill" |
| **Reviewer** | 自动化检查/审查 | "代码审查 Skill""文章核验 Skill" |
| **Inversion** | 需求不明确，先收集再动手 | "项目脚手架 Skill" |
| **Pipeline** | 多步骤严格顺序，有检查点 | "多阶段内容生产 Skill" |
| **Inversion + Generator** | 先收集需求再填充模板 | **skill-builder 使用的模式** |
| **Pipeline + Reviewer** | 多步流程最后自动审查 | "文档生成+自动质检 Skill" |
