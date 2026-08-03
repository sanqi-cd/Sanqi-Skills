#!/usr/bin/env python3
"""Validate all skills and release-critical repository invariants."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

try:
    from scripts.sync_readme import parse_frontmatter, scan_skills
except ModuleNotFoundError:  # Direct execution can place scripts/ first on sys.path.
    from sync_readme import parse_frontmatter, scan_skills


ROOT = Path(__file__).resolve().parent.parent
ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
REQUIRED_METADATA_KEYS = {
    "author",
    "version",
    "emoji",
    "description_zh",
    "description_en",
    "overview_zh",
    "overview_en",
    "platforms",
}
FORBIDDEN_NAMES = {".DS_Store", "__pycache__", ".pytest_cache"}


def top_level_keys(content: str) -> set[str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return set()
    return {
        key
        for key in re.findall(r"^([A-Za-z0-9_-]+):", match.group(1), re.MULTILINE)
    }


def load_json(path: Path, errors: list[str]) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)}: root must be an object")
        return None
    return value


def validate_eval_files(skill_dir: Path, skill_name: str, errors: list[str]) -> None:
    output_path = skill_dir / "evals" / "evals.json"
    trigger_path = skill_dir / "evals" / "trigger-evals.json"
    for path in (output_path, trigger_path):
        if not path.is_file():
            errors.append(f"{path.relative_to(ROOT)}: required eval dataset is missing")

    if output_path.is_file():
        data = load_json(output_path, errors)
        if data is not None:
            if data.get("skill_name") != skill_name:
                errors.append(f"{output_path.relative_to(ROOT)}: skill_name must be {skill_name!r}")
            evals = data.get("evals")
            if not isinstance(evals, list) or len(evals) < 3:
                errors.append(f"{output_path.relative_to(ROOT)}: evals must contain at least 3 cases")
            else:
                for index, case in enumerate(evals, 1):
                    if not isinstance(case, dict) or not all(case.get(k) for k in ("prompt", "expected_output", "assertions")):
                        errors.append(f"{output_path.relative_to(ROOT)}: case {index} is incomplete")
                    elif not isinstance(case["assertions"], list):
                        errors.append(f"{output_path.relative_to(ROOT)}: case {index} assertions must be a list")

    if trigger_path.is_file():
        data = load_json(trigger_path, errors)
        if data is not None:
            if data.get("skill_name") != skill_name:
                errors.append(f"{trigger_path.relative_to(ROOT)}: skill_name must be {skill_name!r}")
            cases = data.get("cases")
            if not isinstance(cases, list) or len(cases) < 12:
                errors.append(f"{trigger_path.relative_to(ROOT)}: cases must contain at least 12 examples")
            else:
                labels = {case.get("should_trigger") for case in cases if isinstance(case, dict)}
                if labels != {True, False}:
                    errors.append(f"{trigger_path.relative_to(ROOT)}: include positive and negative cases")
                for index, case in enumerate(cases, 1):
                    if not isinstance(case, dict) or not isinstance(case.get("prompt"), str) or not isinstance(case.get("reason"), str):
                        errors.append(f"{trigger_path.relative_to(ROOT)}: case {index} is incomplete")


def validate_local_references(skill_dir: Path, content: str, errors: list[str]) -> None:
    paths = set(re.findall(r"\]\((?!https?://|mailto:|#)([^)]+)\)", content))
    paths.update(re.findall(r"`((?:scripts|references|assets|evals)/[^`\s]+)`", content))
    for raw_path in sorted(paths):
        normalized = raw_path.split("#", 1)[0].rstrip(".,;:")
        if not normalized or any(token in normalized for token in ("<", ">", "*", "$")):
            continue
        if normalized.startswith("references/") and normalized.count("/") > 1:
            errors.append(f"{skill_dir.name}/SKILL.md: reference must be one level deep: {normalized}")
        if not (skill_dir / normalized).exists():
            errors.append(f"{skill_dir.name}/SKILL.md: missing referenced path {normalized}")


def validate_openai_yaml(skill_dir: Path, skill_name: str, errors: list[str]) -> None:
    path = skill_dir / "agents" / "openai.yaml"
    if not path.is_file():
        errors.append(f"{path.relative_to(ROOT)}: missing client metadata")
        return
    content = path.read_text(encoding="utf-8")
    for key in ("display_name", "short_description", "default_prompt"):
        if not re.search(rf"^\s{{2}}{key}:\s+\".+\"\s*$", content, re.MULTILINE):
            errors.append(f"{path.relative_to(ROOT)}: missing quoted interface.{key}")
    if f"${skill_name}" not in content:
        errors.append(f"{path.relative_to(ROOT)}: default_prompt must mention ${skill_name}")


def validate_skill(skill_dir: Path, errors: list[str]) -> None:
    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(content)
    keys = top_level_keys(content)
    if not keys:
        errors.append(f"{skill_md.relative_to(ROOT)}: missing YAML frontmatter")
        return
    unknown = keys - ALLOWED_FRONTMATTER_KEYS
    if unknown:
        errors.append(f"{skill_md.relative_to(ROOT)}: unsupported top-level keys: {sorted(unknown)}")

    name = frontmatter.get("name")
    if name != skill_dir.name:
        errors.append(f"{skill_md.relative_to(ROOT)}: name must match directory {skill_dir.name!r}")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append(f"{skill_md.relative_to(ROOT)}: invalid skill name")

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        errors.append(f"{skill_md.relative_to(ROOT)}: description must contain 1-1024 characters")
    compatibility = frontmatter.get("compatibility")
    if not isinstance(compatibility, str) or not compatibility.strip() or len(compatibility) > 500:
        errors.append(f"{skill_md.relative_to(ROOT)}: compatibility must contain 1-500 characters")
    if frontmatter.get("license") != "MIT":
        errors.append(f"{skill_md.relative_to(ROOT)}: license must be MIT")

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(f"{skill_md.relative_to(ROOT)}: metadata must be a mapping")
    else:
        missing = REQUIRED_METADATA_KEYS - metadata.keys()
        if missing:
            errors.append(f"{skill_md.relative_to(ROOT)}: missing metadata keys: {sorted(missing)}")
        non_strings = [key for key, value in metadata.items() if not isinstance(value, str)]
        if non_strings:
            errors.append(f"{skill_md.relative_to(ROOT)}: metadata values must be strings: {non_strings}")

    if len(content.splitlines()) > 500:
        errors.append(f"{skill_md.relative_to(ROOT)}: SKILL.md exceeds 500 lines")
    validate_openai_yaml(skill_dir, str(name), errors)
    validate_local_references(skill_dir, content, errors)
    validate_eval_files(skill_dir, str(name), errors)


def validate_hygiene(errors: list[str]) -> None:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        errors.append("unable to inspect tracked files with git ls-files")
        return
    for raw_path in result.stdout.splitlines():
        path = Path(raw_path)
        if any(part in FORBIDDEN_NAMES for part in path.parts) or path.suffix == ".pyc":
            errors.append(f"{raw_path}: generated file must not be tracked")


def validate_readmes(errors: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sync_readme.py"), "--check", "--repo-root", str(ROOT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        errors.append("README.md or README.en.md is out of sync; run python3 scripts/sync_readme.py")


def main() -> int:
    errors: list[str] = []
    skills = scan_skills(ROOT)
    if not skills:
        errors.append("no skills found")
    for skill in skills:
        validate_skill(ROOT / skill["dir_name"], errors)
    validate_hygiene(errors)
    validate_readmes(errors)

    if errors:
        print(f"FAIL: {len(errors)} validation error(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS: validated {len(skills)} skills and repository release gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
