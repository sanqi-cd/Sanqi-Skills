#!/usr/bin/env python3
"""Run optional model-backed routing simulations or grade saved skill outputs."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = (
    "learning-path-designer",
    "paper-explainer",
    "skill-builder",
    "xhs-image-text-generator",
    "youtube-podcast-to-md",
)


def skill_description(skill: str) -> str:
    content = (ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"^description:\s*>\s*\n((?:[ \t]+.*\n)+)", content, re.M)
    if match is None:
        raise ValueError(f"{skill}: folded description not found")
    return " ".join(line.strip() for line in match.group(1).splitlines())


def load_cases(skill: str, mode: str, submissions: Path | None = None) -> list[dict]:
    path = ROOT / skill / "evals" / ("trigger-evals.json" if mode == "routing" else "evals.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("skill_name") != skill:
        raise ValueError(f"{path}: skill_name mismatch")
    cases = data["cases" if mode == "routing" else "evals"]
    if mode == "output":
        if submissions is None:
            raise ValueError("--submissions is required for output evaluation")
        records = json.loads(submissions.read_text(encoding="utf-8"))
        if records.get("skill_name") != skill:
            raise ValueError(f"{submissions}: skill_name mismatch")
        responses = {str(item["id"]): item["response"] for item in records["cases"]}
        for case in cases:
            case["response"] = responses.get(str(case["id"]), "")
    return cases


def select_cases(cases: list[dict], limit: int | None, case_index: int | None) -> list[dict]:
    if case_index is not None:
        if not 1 <= case_index <= len(cases):
            raise ValueError(f"--case-index must be between 1 and {len(cases)}")
        return [cases[case_index - 1]]
    return cases[:limit]


def response_schema(mode: str) -> dict:
    if mode == "routing":
        properties = {"should_trigger": {"type": "boolean"}, "evidence": {"type": "string"}}
    else:
        properties = {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"passed": {"type": "boolean"}, "evidence": {"type": "string"}},
                    "required": ["passed", "evidence"],
                    "additionalProperties": False,
                },
            }
        }
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def ask_model(prompt: str, mode: str, timeout: int = 300) -> dict:
    with tempfile.TemporaryDirectory(prefix="sanqi-eval-") as tmp:
        root = Path(tmp)
        schema_path = root / "schema.json"
        answer_path = root / "answer.json"
        schema_path.write_text(json.dumps(response_schema(mode)), encoding="utf-8")
        result = subprocess.run(
            [
                "codex", "exec", "--ephemeral", "--ignore-user-config",
                "--skip-git-repo-check", "--sandbox", "read-only",
                "--output-schema", str(schema_path), "--output-last-message", str(answer_path),
                "--cd", str(root), "-",
            ],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(f"codex exec failed ({result.returncode}): {result.stderr[-1200:]}")
        return json.loads(answer_path.read_text(encoding="utf-8"))


def evaluate_case(skill: str, mode: str, case: dict) -> dict:
    if mode == "routing":
        prompt = (
            "You are simulating skill routing from metadata only. Decide whether the user request "
            "matches this skill's description. Do not execute the request. Return one boolean and "
            "a short evidence statement.\n\n"
            f"Skill: {skill}\nDescription: {skill_description(skill)}\n"
            f"User request: {case['prompt']}"
        )
        answer = ask_model(prompt, mode)
        actual = answer["should_trigger"]
        expected = case["should_trigger"]
        return {"prompt": case["prompt"], "expected": expected, "actual": actual,
                "passed": actual is expected, "evidence": answer["evidence"]}

    response = case["response"]
    if not response:
        return {"id": case["id"], "passed": False, "error": "missing saved response"}
    prompt = (
        "Grade the SAVED RESPONSE against each assertion in order. Use only evidence visible in "
        "the response. A promised but absent artifact does not pass. Missing evidence fails. "
        "Return exactly one result per assertion, in order. Do not execute the task.\n\n"
        f"Task: {case['prompt']}\nExpected output: {case['expected_output']}\n"
        f"Assertions: {json.dumps(case['assertions'], ensure_ascii=False)}\n"
        f"Saved response:\n{response}"
    )
    answer = ask_model(prompt, mode)
    results = answer["results"]
    if len(results) != len(case["assertions"]):
        raise ValueError(f"case {case['id']}: model returned {len(results)} results for {len(case['assertions'])} assertions")
    checks = [dict(assertion=assertion, **result) for assertion, result in zip(case["assertions"], results)]
    return {"id": case["id"], "passed": all(check["passed"] for check in checks), "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("routing", "output"))
    parser.add_argument("--skill", required=True, choices=SKILLS)
    parser.add_argument("--submissions", type=Path, help="JSON with skill_name and cases [{id, response}]")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--limit", type=int, help="Evaluate only the first N cases")
    selection.add_argument("--case-index", type=int, help="Evaluate one 1-based case index")
    parser.add_argument("--report", type=Path, help="Write a machine-readable report")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    try:
        cases = load_cases(args.skill, args.mode, args.submissions)
        results = [evaluate_case(args.skill, args.mode, case) for case in select_cases(cases, args.limit, args.case_index)]
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as exc:
        parser.exit(2, f"evaluation failed: {exc}\n")
    report = {"kind": "metadata_routing_simulation" if args.mode == "routing" else "saved_output_grading",
              "skill_name": args.skill, "passed": sum(item["passed"] for item in results),
              "total": len(results), "results": results}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
