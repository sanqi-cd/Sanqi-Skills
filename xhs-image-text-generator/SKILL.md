---
name: xhs-image-text-generator
emoji: 📦
description: >
  当用户想把 HTML 网页、Markdown 文章、纯文本、访谈记录、产品资料或一个主题改造成可直接发布的小红书/RedNote 图文时使用。
  用户可能会说“帮我生成小红书图文”“把这篇文章做成小红书”“生成可发布的图文笔记”“直接生图并给我发布文案”。
  如果用户只是想做普通摘要、公众号长文、微博/推文、视频脚本，或明确不需要小红书图文交付包，则不应触发。
description_en: >
  Use when the user wants to turn an HTML page, Markdown article, plain text, interview notes, product material, or topic into a publish-ready Xiaohongshu/RedNote image-text carousel.
  Users may ask to “make this into a RedNote post”, “generate Xiaohongshu graphics”, or “create publish-ready images and caption”.
  Do not trigger for generic summaries, long-form WeChat articles, tweets, video scripts, or cases where the user explicitly does not need a RedNote-style image-text delivery package.
overview: >
  这个 Skill 帮用户从素材中提炼选题、人群、卖点和视觉结构，生成一套最终可交付的小红书图文发布包。
  核心产出包括标题、封面方案、分页脚本、可复制正文、标签、置顶评论/回复、生图提示词、图片页和发布前质量检查。
  执行过程中会在必要时询问缺失上下文；需要生图时默认直接调用可用生图模型。
overview_en: >
  This Skill helps users extract the topic, audience, hook, and visual structure from source material and produce a publish-ready Xiaohongshu/RedNote carousel package.
  The final output includes titles, cover concepts, page-by-page scripts, copy-ready caption, hashtags, pinned comments/replies, image prompts, generated image pages, and a pre-publish quality check.
  During execution it asks for missing context only when needed; when images are required, it uses the available image generation model by default.
platforms: Claude Code · Codex · OpenCode · OpenClaw
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
   - 默认 6-9 页
   - 每页包含页面标题、页面文案、视觉建议

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

### Step 5：整理最终交付包

最终交付必须包含：

- `manifest.md`：标题、选题、页面列表、发布说明
- `caption.txt`：可直接复制的小红书正文
- `hashtags.txt`：标签
- `comments.txt`：置顶评论和常见回复
- `image-prompts.md`：每页生图提示词
- 图片页：`page-01` 到 `page-08`，或工具实际返回的图片引用
- `quality-check.md`：质量评分和发布前检查清单

可用脚本初始化交付目录：

```bash
python3 scripts/init_delivery_package.py "<topic>" --output-root "<output_root>" --pages 8
```

如果无法保存图片文件，也要在最终回复中逐张展示或引用生成图片，并说明哪些文本文件已保存。

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
