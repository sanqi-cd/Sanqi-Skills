---
name: xhs-image-text-generator
description: >
  将 HTML、Markdown、文章、访谈记录、产品资料或主题转化为可直接发布的 6-10 页小红书/RedNote 图文轮播，完成内容提炼、分页、视觉设计、生图、失败重试和交付校验。适用于“小红书配图”“把文章做成卡片”“直接生图并给发布文案”等请求。Use when the user needs final carousel assets, not only prompts or generic summaries.
license: MIT
compatibility: Requires Python 3; URL inputs need network access, and full delivery requires image generation plus local file writing.
metadata:
  author: "sanqi-cd"
  version: "1.0.0"
  emoji: "📦"
  description_zh: "将主题或文章转化为内容清晰、视觉统一、可直接发布的小红书图文轮播。"
  description_en: "Turn source content into a coherent, publication-ready Xiaohongshu image carousel."
  overview_zh: "覆盖内容提炼、分页编排、视觉设计、批量生图与交付校验。"
  overview_en: "Cover content distillation, pagination, visual design, batch generation, and delivery validation."
  platforms: "Claude Code · Codex · OpenCode · OpenClaw"
---

# 小红书图文生成器

## 适用场景

当用户提供以下任一输入，并希望生成小红书图文笔记时，优先使用本技能：

- HTML 网页 URL 或 HTML 文件
- Markdown 文章
- 纯文本内容、访谈记录、产品资料、研究笔记
- 一个主题、想法、工具清单或案例素材

本技能的目标不是只写文案，而是生成一套最终用户可以直接发小红书的交付包。

## 默认工作流

### Step 1：统一输入素材

如果用户提供的是 URL、HTML、Markdown 文件或较长文本，优先使用脚本抽取正文：

```bash
python3 scripts/normalize_input.py "<input>" --output "<normalized.md>"
```

说明：
- `<input>` 可以是 URL、本地文件路径，或 `-` 表示从标准输入读取
- 脚本会自动识别 `html`、`markdown`、`text`
- 如果当前目录不是本 skill 根目录，请使用脚本的实际路径

短主题或一句话需求可以不运行脚本，直接进入 Step 2。

### Step 2：补齐关键上下文

先从素材中推断：

- 目标人群：例如打工人、内容创作者、职场新人、读书博主、AI 初学者
- 核心收益：省时间、涨粉、赚钱、效率提升、审美提升、认知提升
- 内容类型：工具清单、教程步骤、方法复盘、模板分享、观点拆解、案例拆解
- 可视化素材：数据、步骤、工具图标、前后对比、截图、金句、清单
- 评论区需求：领取资料、是否免费、怎么安装、国内能否用、适合谁

如果以下信息缺失且会影响成品，直接问用户 1-3 个短问题后继续：

- 发布账号/人设：例如 AI 工具号、个人成长号、职场干货号、读书号
- 目标人群：默认从素材推断
- 期望风格：默认选择最适合赛道的爆款风格
- 是否需要真实品牌/头像/个人照片：默认不用
- 是否允许直接生图：默认允许，除非用户明确只要文案
- 交付数量：默认 1 篇，8 页图文

不要为可合理默认的信息反复追问。

### Step 3：生成发布方案

输出必须包含以下模块：

1. **选题角度**
   - 给 3-5 个角度
   - 标注适合人群、核心钩子、保存价值

2. **标题候选**
   - 生成 10 个标题
   - 覆盖结果型、痛点型、清单型、反常识型、教程型

3. **封面方案**
   - 给 3 个封面方案
   - 每个包含主标题、副标题、视觉元素、配色、构图建议

4. **分页脚本**
   - 默认 8 页，可按素材调整为 6-10 页
   - 每页包含页面标题、页面文案、视觉建议
   - 按 `references/carousel-schema.md` 保存为 `carousel.json`，它是页面文字的唯一数据源

5. **正文**
   - 适合小红书发布的短段落
   - 包含收益、适合谁、怎么用、避坑、互动引导

6. **标签**
   - 12-18 个标签
   - 覆盖核心词、人群词、场景词、长尾搜索词

7. **评论运营**
   - 置顶评论
   - 资料/模板领取评论
   - 3-5 条常见问题回复

8. **质量评分**
   - 按 6 个维度打分并给修改建议

### Step 4：生成图片页

如果用户需要可直接发布的结果，必须生成图片页：

- 默认生成 8 张竖版图文页，比例 3:4 或 4:5，适合小红书图文
- 每张图必须有明确页面角色：封面、痛点、总览、步骤、案例、避坑、总结
- 先写 `image-prompts.md`，再直接调用生图模型生成图片
- 如果生图模型一次只能生成单张，就按页逐张生成
- 图片必须避免文字过密；每页只放一个主信息点
- 生成后检查：文字是否可读、是否跑题、是否适合小红书首图/分页

先生成可校验的排版基准：

```bash
python3 scripts/render_carousel_html.py "<package>/carousel.json" "<package>/cards.html"
```

`cards.html` 用于锁定逐页文字、层级和页数，也可以由浏览器逐页截图。使用生图模型时，以它作为内容基准：模型负责视觉素材，中文文字必须和 `carousel.json` 一致；发现乱码、缺字或文字溢出时应重试或改用浏览器排版截图。

### Step 5：整理最终交付包

最终交付必须包含：

- `manifest.md`：标题、选题、页面列表、发布说明
- `caption.txt`：可直接复制的小红书正文
- `hashtags.txt`：标签
- `comments.txt`：置顶评论和常见回复
- `image-prompts.md`：每页生图提示词
- 图片页：`page-01` 到 `page-08`，或工具实际返回的图片引用
- `quality-check.md`：质量评分和发布前检查清单
- `carousel.json`：分页文案、角色、视觉系统和事实来源

可用脚本初始化交付目录：

```bash
python3 scripts/init_delivery_package.py "<topic>" --output-root "<output_root>" --pages 8
```

如果无法保存图片文件，也要在最终回复中逐张展示或引用生成图片，并说明哪些文本文件已保存。

交付前运行：

```bash
python3 scripts/validate_delivery.py "<package>"
```

只有用户明确接受 HTML 预览而非最终图片时，才可使用 `--allow-html`。校验失败时修复后重跑，不要把只有提示词或空占位文件的目录当作完成。

## 生成原则

- 封面先卖结果，不先讲背景
- 标题必须有明确人群、痛点、数字或收益中的至少两项
- 每页只承载一个核心信息点
- 图文要有保存价值：清单、步骤、模板、工具、对比、避坑
- 正文负责补充关键词和信任，不能写成公众号长文
- 评论区要承接需求，不要只写“欢迎评论”
- 避免夸大承诺；涉及赚钱、医疗、法律、投资等高风险主题时，加边界说明
- 不要替用户实际发布、点赞、评论或私信，除非用户明确要求且完成发布前确认

## 推荐分页结构

默认使用 8 页结构：

1. 封面：结果钩子
2. 痛点：用户正在遇到的问题
3. 总览：方法/框架/工具清单
4. 关键步骤 1
5. 关键步骤 2
6. 案例/前后对比
7. 避坑/注意事项
8. 总结 + 评论引导

如果素材更适合其他结构，参考 `references/playbook.md` 中的模板。

## 质量评分

最终必须给出 0-5 分评分：

- 封面点击力
- 标题吸引力
- 保存价值
- 可信度
- 搜索价值
- 评论转化

每个低于 4 分的维度必须给出具体修改建议。

## 按需读取的参考文件

- `references/playbook.md`
  当需要标题公式、封面模板、分页模板、评论引导和评分细则时读取。
- `references/delivery.md`
  当用户要“最终可交付”“直接发小红书”“生成图片页”时读取，用于询问策略、生图策略和交付包结构。
- `references/carousel-schema.md`
  生成分页文案、渲染排版基准或校验交付包时读取。
