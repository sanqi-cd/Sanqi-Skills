# Carousel Data Contract

Use `carousel.json` as the single source of truth for page copy and visual roles:

```json
{
  "topic": "主题",
  "audience": "目标人群",
  "angle": "唯一叙事角度",
  "visual_system": {
    "style": "editorial utility",
    "background": "#F6F4EE",
    "foreground": "#1D2420",
    "accent": "#E5484D"
  },
  "pages": [
    {
      "number": 1,
      "role": "cover",
      "title": "主标题",
      "subtitle": "副标题",
      "bullets": [],
      "visual_note": "可检验的画面说明",
      "source_note": "事实来源或留空"
    }
  ]
}
```

## Constraints

- Include 6-10 pages with consecutive `number` values starting at 1.
- Use one `cover` page and one final `cta` or `summary` page.
- Keep titles at 28 Chinese characters or fewer, subtitles at 44, and each bullet at 48.
- Use at most six bullets per page and one dominant information goal per page.
- Preserve factual claims in `source_note`; do not invent data, testimonials, or product capabilities.
- Keep colors as six-digit hex values so the deterministic renderer can use them safely.
