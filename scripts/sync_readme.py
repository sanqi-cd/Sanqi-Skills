#!/usr/bin/env python3
"""
自动同步 Skills 到 README.md 和 README.en.md

功能：
1. 扫描所有 skill 目录（包含 SKILL.md 的目录）
2. 读取每个 SKILL.md 的 frontmatter 元信息
3. 自动更新 README.md / README.en.md 中的：
   - Skills 徽章数量
   - Skills 表格
   - Skills 详细区块（自动生成）

使用方法：
    python scripts/sync_readme.py [--dry-run | --check]

参数：
    --dry-run    只预览变更，不实际修改文件
    --check      检查 README 是否已同步，未同步时返回非零状态
"""

import re
import argparse
from pathlib import Path
from typing import Optional


README_CONFIGS = {
    'zh': {
        'filename': 'README.md',
        'table_pattern': r'(### Skills\s*\n\s*\n\| 名字 \| 一句话 \| 平台 \|\s*\n\|---\|---\|---\|\s*\n)(.*?)(\s*\n---)',
        'workflow_label': '**工作流程：**',
        'trigger_label': '**怎么触发：**',
        'preview_label': '📄 预览 README.md 变更:',
        'updated_label': '✅ 已更新 README.md',
        'missing_label': '❌ README.md 不存在',
        'unchanged_label': 'ℹ️ README.md 无需更新',
        'description_limit': 50,
    },
    'en': {
        'filename': 'README.en.md',
        'table_pattern': r'(### Skills\s*\n\s*\n\| Name \| One-liner \| Platforms \|\s*\n\|---\|---\|---\|\s*\n)(.*?)(\s*\n---)',
        'workflow_label': '**Workflow:**',
        'trigger_label': '**How to trigger:**',
        'preview_label': '📄 Preview README.en.md changes:',
        'updated_label': '✅ Updated README.en.md',
        'missing_label': '❌ README.en.md does not exist',
        'unchanged_label': 'ℹ️ README.en.md no changes needed',
        'description_limit': 90,
    },
}


def parse_frontmatter(content: str) -> dict:
    """解析仓库使用的 YAML frontmatter 子集，包括一级嵌套映射。"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}

    frontmatter_text = match.group(1)
    result: dict = {}
    lines = frontmatter_text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or line.startswith((' ', '\t')):
            i += 1
            continue
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if value in ('>', '|', '>-', '|-', '>+', '|+'):
                block_style = value[0]
                block_lines = []
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.strip()
                    if next_stripped and not next_line.startswith((' ', '\t')) and ':' in next_line:
                        break
                    block_lines.append(next_stripped)
                    i += 1

                if block_style == '>':
                    result[key] = ' '.join(part for part in block_lines if part).strip()
                else:
                    result[key] = '\n'.join(block_lines).strip()
                continue

            if not value:
                nested = {}
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.strip() and not next_line.startswith((' ', '\t')):
                        break
                    nested_match = re.match(r'^\s+([A-Za-z0-9_-]+):\s*(.*?)\s*$', next_line)
                    if nested_match:
                        nested_key, nested_value = nested_match.groups()
                        nested[nested_key] = nested_value.strip('"').strip("'")
                    i += 1
                result[key] = nested
                continue

            result[key] = value.strip('"').strip("'")
        i += 1

    return result


def parse_existing_table_metadata(content: str, language: str) -> dict:
    """读取现有 README 表格元数据，用于保留 README.en.md 的人工英文文案"""
    table_pattern = README_CONFIGS[language]['table_pattern']
    match = re.search(table_pattern, content, flags=re.DOTALL)
    if not match:
        return {}

    metadata = {}
    for row in match.group(2).splitlines():
        columns = [column.strip() for column in row.strip().strip('|').split('|')]
        if len(columns) < 3:
            continue
        name_match = re.search(r'^(?P<emoji>.*?)\s*\[\*\*(?P<name>.+?)\*\*\]', columns[0])
        if name_match:
            name = name_match.group('name')
            metadata[name] = {
                'emoji': name_match.group('emoji').strip(),
                'description': columns[1],
            }

    return metadata


def parse_existing_detail_bodies(content: str) -> dict:
    """读取现有详情块正文，用于保留 README.en.md 的人工英文详情"""
    detail_start = '<!-- SKILLS_DETAIL_START -->'
    detail_end = '<!-- SKILLS_DETAIL_END -->'
    if detail_start not in content or detail_end not in content:
        return {}

    detail_content = content.split(detail_start, 1)[1].split(detail_end, 1)[0]
    blocks = {}
    block_pattern = r'<table>\s*<tr><td>\s*###\s+\S+\s+(.+?)\s*\n\n(.*?)\n\n→ \[SKILL\.md\]'
    for name, body in re.findall(block_pattern, detail_content, flags=re.DOTALL):
        body = body.strip()
        if body:
            blocks[name.strip()] = body

    return blocks


def extract_sections(content: str) -> dict:
    """从 SKILL.md 内容中提取各区块"""
    # 移除 frontmatter
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

    sections = {}

    # 提取概述；新 skill 常用“目标”作为一句话说明
    for heading in ['概述', '目标', '简介', 'Overview', 'Goal']:
        overview_match = re.search(rf'^##\s*{heading}\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.MULTILINE)
        if overview_match:
            sections['overview'] = overview_match.group(1).strip()
            break

    # 提取工作流（简化版）
    workflow_match = re.search(r'^##\s*工作流.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.MULTILINE)
    if workflow_match:
        workflow_text = workflow_match.group(1).strip()
        # 提取步骤标题
        steps = re.findall(r'^###\s*(.+)$', workflow_text, re.MULTILINE)
        if steps:
            sections['steps'] = steps[:5]  # 最多取5个步骤

    # 提取触发方式
    trigger_match = re.search(r'\*\*怎么触发[：:]\*\*\s*```.*?\n(.*?)```', content, re.DOTALL)
    if trigger_match:
        sections['trigger'] = trigger_match.group(1).strip()

    return sections


def get_skill_info(skill_dir: Path) -> Optional[dict]:
    """获取单个 skill 的信息"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None

    content = skill_md.read_text(encoding='utf-8')
    frontmatter = parse_frontmatter(content)
    sections = extract_sections(content)
    metadata = frontmatter.get('metadata', {})
    if not isinstance(metadata, dict):
        metadata = {}

    # 从 frontmatter 获取基本信息
    name = frontmatter.get('name', skill_dir.name)
    description = metadata.get('description_zh') or frontmatter.get('description', '')
    description_en = metadata.get('description_en', '')
    emoji = metadata.get('emoji', '📦')
    platforms = metadata.get('platforms', 'Claude Code · Codex · OpenCode · OpenClaw')
    overview = metadata.get('overview_zh', '') or sections.get('overview', '')
    overview_en = metadata.get('overview_en', '')

    # 尝试从内容中提取一句话描述（如果 frontmatter 没有提供）
    if not description:
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('>') and not line.startswith('---'):
                description = line[:80] + ('...' if len(line) > 80 else '')
                break

    return {
        'name': name,
        'dir_name': skill_dir.name,
        'description': description,
        'description_en': description_en,
        'emoji': emoji,
        'emoji_explicit': bool(metadata.get('emoji')),
        'platforms': platforms,
        'skill_md_path': f"./{skill_dir.name}/SKILL.md",
        'overview': overview,
        'overview_en': overview_en,
        'steps': sections.get('steps', []),
        'trigger': sections.get('trigger', '')
    }


def clean_table_cell(value: str) -> str:
    """清理 Markdown 表格单元格，避免换行和竖线破坏表格"""
    return value.replace('\n', ' ').replace('|', '\\|').strip()


def scan_skills(repo_root: Path) -> list[dict]:
    """扫描所有 skill 目录"""
    skills = []

    for item in repo_root.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            if item.name in ['scripts', 'prompts', 'references']:
                continue
            skill_info = get_skill_info(item)
            if skill_info:
                skills.append(skill_info)

    # 按名称排序
    skills.sort(key=lambda x: x['name'])
    return skills


def generate_detail_block(
    skill: dict,
    language: str = 'zh',
    existing_body: str = '',
    display_emoji: str = '',
) -> str:
    """生成单个 skill 的详细区块 HTML"""
    anchor = skill['name'].lower().replace(' ', '-').replace('_', '-')
    config = README_CONFIGS[language]
    emoji = display_emoji or skill['emoji']

    lines = [
        '<table>',
        '<tr><td>',
        '',
        f'### {emoji} {skill["name"]}',
        ''
    ]

    if existing_body:
        lines.append(existing_body)
        lines.append('')

    elif language == 'en' and skill.get('overview_en'):
        overview = skill['overview_en'][:200]
        if len(skill['overview_en']) > 200:
            overview += '...'
        lines.append(overview)
        lines.append('')

    # 添加概述
    elif skill['overview']:
        # 截取前200字
        overview = skill['overview'][:200]
        if len(skill['overview']) > 200:
            overview += '...'
        lines.append(overview)
        lines.append('')

    # 添加工作流步骤
    if not existing_body and skill['steps']:
        lines.append(config['workflow_label'])
        for i, step in enumerate(skill['steps'], 1):
            lines.append(f'{i}. {step}')
        lines.append('')

    # 添加触发方式
    if not existing_body and skill['trigger']:
        lines.append(config['trigger_label'])
        lines.append('```')
        lines.append(skill['trigger'])
        lines.append('```')
        lines.append('')

    # 添加链接
    lines.append(f'→ [SKILL.md]({skill["skill_md_path"]})')
    lines.append('')
    lines.append('</td></tr>')
    lines.append('</table>')
    lines.append('')

    return '\n'.join(lines)


def update_readme(readme_path: Path, skills: list[dict], dry_run: bool = False, language: str = 'zh') -> bool:
    """更新 README.md"""
    if not readme_path.exists():
        print(f"{README_CONFIGS[language]['missing_label']}: {readme_path}")
        return False

    content = readme_path.read_text(encoding='utf-8')
    original_content = content
    existing_metadata = parse_existing_table_metadata(content, language) if language == 'en' else {}
    existing_detail_bodies = parse_existing_detail_bodies(content) if language == 'en' else {}
    config = README_CONFIGS[language]

    # 1. 更新徽章数量
    badge_pattern = r'\[!\[Skills\]\(https://img\.shields\.io/badge/Skills-\d+-'
    new_badge = f'[![Skills](https://img.shields.io/badge/Skills-{len(skills)}-'
    content = re.sub(badge_pattern, new_badge, content)

    # 2. 更新 Skills 表格
    table_rows = []
    for skill in skills:
        anchor = skill['name'].lower().replace(' ', '-').replace('_', '-')
        existing_skill_metadata = existing_metadata.get(skill['name'], {})
        if language == 'en':
            description = (
                clean_table_cell(skill.get('description_en', ''))
                or existing_skill_metadata.get('description')
                or clean_table_cell(skill['description'])
            )
        else:
            description = clean_table_cell(skill['description'])
        limit = config['description_limit']
        short_description = description[:limit] + ('...' if len(description) > limit else '')
        display_emoji = skill['emoji'] if skill['emoji_explicit'] else existing_skill_metadata.get('emoji') or skill['emoji']
        row = f"| {display_emoji} [**{skill['name']}**](#-{anchor}) | {short_description} | {skill['platforms']} |"
        table_rows.append(row)

    new_table = '\n'.join(table_rows)
    content = re.sub(config['table_pattern'], rf'\1{new_table}\3', content, flags=re.DOTALL)

    # 3. 更新 Skills 详细区块
    # 查找标记位
    detail_start = '<!-- SKILLS_DETAIL_START -->'
    detail_end = '<!-- SKILLS_DETAIL_END -->'

    if detail_start in content and detail_end in content:
        # 生成所有 skill 的详细区块
        detail_blocks = [
            generate_detail_block(
                skill,
                language,
                '' if language == 'en' and skill.get('overview_en') else existing_detail_bodies.get(skill['name'], ''),
                skill['emoji'] if skill['emoji_explicit'] else existing_metadata.get(skill['name'], {}).get('emoji', ''),
            )
            for skill in skills
        ]
        new_details = f'{detail_start}\n' + '\n'.join(detail_blocks) + detail_end

        # 替换标记位之间的内容
        detail_pattern = rf'{re.escape(detail_start)}.*?{re.escape(detail_end)}'
        content = re.sub(detail_pattern, new_details, content, flags=re.DOTALL)

    if dry_run:
        print(config['preview_label'])
        print("-" * 50)
        if content != original_content:
            print("✅ 检测到以下变更:")
            print(f"  - Skills 数量: {len(skills)}")
            print(f"  - Skills 列表: {', '.join([s['name'] for s in skills])}")
            print(f"  - 详细区块: 已自动生成")
        else:
            print("ℹ️ 没有检测到变更")
        return content != original_content

    if content != original_content:
        readme_path.write_text(content, encoding='utf-8')
        print(config['updated_label'])
        print(f"   - Skills 数量: {len(skills)}")
        print(f"   - 详细区块: 已自动生成")
        return True
    else:
        print(config['unchanged_label'])
        return False


def sync_readmes(repo_root: Path, dry_run: bool = False) -> bool:
    """扫描一次 skill，并同步中英文 README"""
    skills = scan_skills(repo_root)
    print(f"🔍 发现 {len(skills)} 个 Skill:")
    for skill in skills:
        print(f"   - {skill['emoji']} {skill['name']}: {skill['description'][:40]}...")

    changed = False
    for language, config in README_CONFIGS.items():
        readme_path = repo_root / config['filename']
        changed = update_readme(readme_path, skills, dry_run, language) or changed

    return changed


def main():
    parser = argparse.ArgumentParser(description='自动同步 Skills 到 README.md 和 README.en.md')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true', help='只预览变更，不实际修改')
    mode.add_argument('--check', action='store_true', help='检查 README 是否已同步')
    parser.add_argument('--repo-root', type=str, default=None, help='仓库根目录路径')
    args = parser.parse_args()

    # 确定仓库根目录
    if args.repo_root:
        repo_root = Path(args.repo_root)
    else:
        # 脚本在 scripts/ 目录下，仓库根目录是上一级
        repo_root = Path(__file__).parent.parent

    print(f"📁 扫描目录: {repo_root}")

    changed = sync_readmes(repo_root, args.dry_run or args.check)
    if args.check and changed:
        print('❌ README 文件与 SKILL.md 元数据不同步，请运行 python3 scripts/sync_readme.py')
        raise SystemExit(1)


if __name__ == '__main__':
    main()
