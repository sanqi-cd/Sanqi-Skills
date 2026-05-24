#!/usr/bin/env python3
"""
自动同步 Skills 到 README.md

功能：
1. 扫描所有 skill 目录（包含 SKILL.md 的目录）
2. 读取每个 SKILL.md 的 frontmatter 元信息
3. 自动更新 README.md 中的：
   - Skills 徽章数量
   - Skills 表格
   - Skills 详细区块（自动生成）

使用方法：
    python scripts/sync_readme.py [--dry-run]

参数：
    --dry-run    只预览变更，不实际修改文件
"""

import os
import re
import argparse
from pathlib import Path
from typing import Optional


def parse_frontmatter(content: str) -> dict:
    """解析 SKILL.md 的 YAML frontmatter"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}

    frontmatter_text = match.group(1)
    result = {}

    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip().strip('"').strip("'")

    return result


def extract_sections(content: str) -> dict:
    """从 SKILL.md 内容中提取各区块"""
    # 移除 frontmatter
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

    sections = {}

    # 提取概述
    overview_match = re.search(r'^##\s*概述\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.MULTILINE)
    if overview_match:
        sections['overview'] = overview_match.group(1).strip()

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

    # 从 frontmatter 获取基本信息
    name = frontmatter.get('name', skill_dir.name)
    description = frontmatter.get('description', '')
    emoji = frontmatter.get('emoji', '📦')
    platforms = frontmatter.get('platforms', 'Claude Code · Codex · OpenCode · OpenClaw')

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
        'emoji': emoji,
        'platforms': platforms,
        'skill_md_path': f"./{skill_dir.name}/SKILL.md",
        'overview': sections.get('overview', ''),
        'steps': sections.get('steps', []),
        'trigger': sections.get('trigger', '')
    }


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


def generate_detail_block(skill: dict) -> str:
    """生成单个 skill 的详细区块 HTML"""
    anchor = skill['name'].lower().replace(' ', '-').replace('_', '-')

    lines = [
        '<table>',
        '<tr><td>',
        '',
        f'### {skill["emoji"]} {skill["name"]}',
        ''
    ]

    # 添加概述
    if skill['overview']:
        # 截取前200字
        overview = skill['overview'][:200]
        if len(skill['overview']) > 200:
            overview += '...'
        lines.append(overview)
        lines.append('')

    # 添加工作流步骤
    if skill['steps']:
        lines.append('**工作流程：**')
        for i, step in enumerate(skill['steps'], 1):
            lines.append(f'{i}. {step}')
        lines.append('')

    # 添加触发方式
    if skill['trigger']:
        lines.append('**怎么触发：**')
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


def update_readme(readme_path: Path, skills: list[dict], dry_run: bool = False) -> bool:
    """更新 README.md"""
    if not readme_path.exists():
        print(f"❌ README.md 不存在: {readme_path}")
        return False

    content = readme_path.read_text(encoding='utf-8')
    original_content = content

    # 1. 更新徽章数量
    badge_pattern = r'\[!\[Skills\]\(https://img\.shields\.io/badge/Skills-\d+-'
    new_badge = f'[![Skills](https://img.shields.io/badge/Skills-{len(skills)}-'
    content = re.sub(badge_pattern, new_badge, content)

    # 2. 更新 Skills 表格
    table_pattern = r'(### Skills\s*\n\s*\n\| 名字 \| 一句话 \| 平台 \|\s*\n\|---\|---\|---\|\s*\n)(.*?)(\s*\n---)'
    table_rows = []
    for skill in skills:
        anchor = skill['name'].lower().replace(' ', '-').replace('_', '-')
        row = f"| {skill['emoji']} [**{skill['name']}**](#-{anchor}) | {skill['description'][:50]}{'...' if len(skill['description']) > 50 else ''} | {skill['platforms']} |"
        table_rows.append(row)

    new_table = '\n'.join(table_rows)
    content = re.sub(table_pattern, rf'\1{new_table}\3', content, flags=re.DOTALL)

    # 3. 更新 Skills 详细区块
    # 查找标记位
    detail_start = '<!-- SKILLS_DETAIL_START -->'
    detail_end = '<!-- SKILLS_DETAIL_END -->'

    if detail_start in content and detail_end in content:
        # 生成所有 skill 的详细区块
        detail_blocks = [generate_detail_block(skill) for skill in skills]
        new_details = f'{detail_start}\n' + '\n'.join(detail_blocks) + detail_end

        # 替换标记位之间的内容
        detail_pattern = rf'{re.escape(detail_start)}.*?{re.escape(detail_end)}'
        content = re.sub(detail_pattern, new_details, content, flags=re.DOTALL)

    if dry_run:
        print("📄 预览 README.md 变更:")
        print("-" * 50)
        if content != original_content:
            print("✅ 检测到以下变更:")
            print(f"  - Skills 数量: {len(skills)}")
            print(f"  - Skills 列表: {', '.join([s['name'] for s in skills])}")
            print(f"  - 详细区块: 已自动生成")
        else:
            print("ℹ️ 没有检测到变更")
        return True

    if content != original_content:
        readme_path.write_text(content, encoding='utf-8')
        print(f"✅ 已更新 README.md")
        print(f"   - Skills 数量: {len(skills)}")
        print(f"   - 详细区块: 已自动生成")
        return True
    else:
        print("ℹ️ README.md 无需更新")
        return False


def main():
    parser = argparse.ArgumentParser(description='自动同步 Skills 到 README.md')
    parser.add_argument('--dry-run', action='store_true', help='只预览变更，不实际修改')
    parser.add_argument('--repo-root', type=str, default=None, help='仓库根目录路径')
    args = parser.parse_args()

    # 确定仓库根目录
    if args.repo_root:
        repo_root = Path(args.repo_root)
    else:
        # 脚本在 scripts/ 目录下，仓库根目录是上一级
        repo_root = Path(__file__).parent.parent

    print(f"📁 扫描目录: {repo_root}")

    # 扫描 skills
    skills = scan_skills(repo_root)
    print(f"🔍 发现 {len(skills)} 个 Skill:")
    for skill in skills:
        print(f"   - {skill['emoji']} {skill['name']}: {skill['description'][:40]}...")

    # 更新 README
    readme_path = repo_root / "README.md"
    update_readme(readme_path, skills, args.dry_run)


if __name__ == '__main__':
    main()
