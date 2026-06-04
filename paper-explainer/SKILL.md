---
name: paper-explainer
emoji: 📄
description: >
  当用户上传论文 PDF 或提供 arXiv 链接并请求解读时使用。
  触发："帮我解读这篇论文""解读论文""解读下这篇 paper""论文解读"。
  不要用于：事实查询（"这篇论文发在哪""作者是谁"）、非学术论文（新闻/博客/报道）、
  内容不足 2 页的短文。
description_en: >
  When the user uploads a paper PDF or provides an arXiv link and requests interpretation.
  Triggers: "explain this paper" "paper summary" "summarize this paper" "break down this paper".
  Do NOT use for: factual queries ("where was this paper published" "who is the author"),
  non-academic content (news / blog posts), content shorter than 2 pages.
overview: >
  按「引言/方法/实验/结论」拆解论文，用通俗类比解读核心思想，标注可复现细节
  （数据集、超参、环境），输出结构化 Markdown 笔记。
overview_en: >
  Breaks down papers into Introduction / Method / Experiment / Conclusion sections,
  explains core ideas with layman analogies, annotates reproducibility details
  (datasets, hyperparameters, environment), and outputs a structured Markdown note.
platforms: Claude Code · Codex · OpenCode · OpenClaw
---

# 论文解读

## 目标

按「引言/方法/实验/结论」拆解论文，用通俗语言解读核心思想，标注可复现细节，输出一份结构化 Markdown 笔记。

## 开始前准备

- [ ] 确认用户提供了 PDF 文件或 arXiv 链接
- [ ] 仅给论文标题时，先搜索论文再让用户确认是哪篇，不要盲猜
- [ ] 论文超过 50 页时，询问用户是否需要完整解读还是只解读核心部分
- [ ] PDF 扫描件 OCR 质量太差无法提取正文时，告知用户并停止
- [ ] 用户给多篇但未指定时，停下来确认

## 工作流程

### Step 1: 获取论文全文

- 如果是 PDF：提取正文（含标题、作者、摘要、所有章节）
- 如果是 arXiv 链接：获取论文元数据和 PDF，提取正文
- 仅给标题时：搜索 arXiv / Google Scholar，列出候选，请用户确认后再获取全文
- 提取失败时明确告知原因，不编造内容

**产出**：论文完整正文 + 元数据（标题、作者、发表年份/会议、链接）

### Step 2: 识别论文结构

通读全文，识别各章节对应关系。常见结构映射：

- Introduction / 引言 / 背景 → **引言**
- Method / Proposed Approach / 方法 / 模型 → **方法**
- Experiment / Evaluation / Results / 实验 / 结果 → **实验**
- Conclusion / Discussion / 结论 / 讨论 → **结论**

如果论文结构不标准，按最接近的逻辑归类，并在笔记中说明归类依据。

**产出**：章节映射表 + 每个章节的核心要点速记

### Step 3: 逐章解读

对每个章节完成以下四项任务：

**A. 核心内容简述**：用 3-5 句话概括本章做了什么，不用术语堆砌
**B. 通俗类比**：至少给 1 个生活化类比帮助理解。如"注意力机制就像一个读者在翻译句子时，每写一个词都会回看原文中最相关的部分"
**C. 术语解释**：本章首次出现的专业术语给出简明解释（一句话），后续出现不重复
**D. 可复现标注**（重点在方法&实验章节）：标注数据集名称/规模、超参设置、硬件环境、关键实现细节。如缺信息则注明"论文未提及"

**产出**：四个章节的解读草稿，每章含 A/B/C/D 四项

### Step 4: 质量检查

对照质量标准逐项自检，不通过的章节回修：

- [ ] 每个 section 有至少 1 个通俗类比
- [ ] 方法章节标注了数据集、超参、环境等可复现细节
- [ ] 结论章节区分了"作者声称"与"客观实验结果"
- [ ] 首次出现的术语有简明解释
- [ ] 实验局限性已标注（如有）

**产出**：自检通过的解读终稿

### Step 5: 输出 Markdown 笔记

按以下格式输出最终笔记：

```
# [论文标题]

**作者**: [作者] | **发表**: [会议/期刊, 年份] | **链接**: [arXiv/DOI]

## 一句话速读
[不超过 80 字的核心贡献概括]

## 引言
[核心内容简述]
[通俗类比]
[关键术语解释]

## 方法
[核心内容简述]
[通俗类比]
[关键术语解释]
[可复现细节：数据集 | 超参 | 环境 | 实现要点]
[未提及的细节]

## 实验
[核心内容简述]
[通俗类比]
[主要结果]
[可复现细节]
[实验局限性（如有）]

## 结论
[作者声称的贡献]
[客观实验结果支撑了什么]
[未解决的问题/未来方向]

## 一句话总结
[论文最值得记住的一个点]
```

**产出**：符合格式的结构化 Markdown 笔记

## 质量标准

- [ ] 每个章节（引言/方法/实验/结论）至少包含 1 个通俗类比
- [ ] 方法章节标注数据集名称/规模、超参、硬件环境、关键实现细节；缺失项标注"论文未提及"
- [ ] 结论明确区分"作者声称"与"客观实验结果"
- [ ] 首次出现的专业术语有括号内简明解释
- [ ] 实验局限性已标注
- [ ] 不直接翻译摘要充当解读，不堆砌术语

## 最终反馈

解读完成后，向用户报告以下内容即任务结束：

| 项目 | 内容 |
|------|------|
| 章节覆盖 | 实际覆盖了几个章节（引言/方法/实验/结论） |
| 可复现细节 | 标注了几项、其中几项论文提及、几项缺失 |
| 实验局限性 | 是否已标注 |
| 需复核 | 内容中不确定的部分（如模糊的公式、OCR 可能误读的字符） |

以上四项全部报告完毕即退出，不额外追问。
