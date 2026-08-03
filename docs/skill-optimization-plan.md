# Skill Repository Optimization Plan

This document turns the repository review into an executable release program. The phases are intentionally ordered so each gate can run automatically after the previous one succeeds.

## Target

Bring every published skill to a consistent, portable, testable level aligned with the Agent Skills open standard. A release is ready only when metadata, instructions, deterministic helpers, evaluation data, documentation, and CI all pass the same local validation command.

## Phase 1: Standardize discovery metadata

- Keep only standard top-level frontmatter fields: `name`, `description`, `license`, `compatibility`, and `metadata`.
- Put repository-specific bilingual display fields under `metadata` as strings.
- Make every primary description include the task, positive triggers, boundaries, and expected outcome.
- Add `agents/openai.yaml` for every skill with a concise display name, description, and `$skill-name` default prompt.

Exit gate: all metadata parses successfully, folder names match skill names, and client metadata is complete.

## Phase 2: Add repository-level quality gates

- Upgrade README synchronization to understand nested standard metadata.
- Add a read-only `--check` mode for CI.
- Add a dependency-free repository validator for structure, references, metadata, client files, eval datasets, generated-file hygiene, and README drift.
- Add trigger and output eval datasets for every skill.

Exit gate: `python3 scripts/validate_repository.py` passes locally.

## Phase 3: Strengthen execution reliability

- `learning-path-designer`: separate structured plan data from deterministic HTML rendering and validation.
- `paper-explainer`: add source/evidence requirements, a quality rubric, and Markdown output validation.
- `skill-builder`: align its creation workflow with current skill structure, progressive disclosure, validation, and evaluation practices.
- `xhs-image-text-generator`: add a canonical carousel schema, deterministic HTML card renderer, and delivery validator.
- `youtube-podcast-to-md`: document reproducible dependencies, improve provenance requirements, and validate final Markdown.

Exit gate: each helper has focused unit tests and every referenced resource exists.

## Phase 4: Automate regression and release checks

- Run all standard-library unit tests in CI.
- Run the repository validator and README drift check on pushes and pull requests.
- Document a single local verification command and a release checklist.

Exit gate: a clean checkout can run all required checks without private credentials.

## Phase 5: Final verification

- Remove generated operating-system and Python cache files.
- Regenerate both READMEs from source metadata.
- Run syntax compilation, unit tests, repository validation, and a final Git diff review.
- Record any capability that still requires external credentials or model-based evaluation as a transparent residual limitation.

Exit gate: all deterministic checks pass and the worktree contains only intentional source changes.

## Release commands

```bash
python3 scripts/sync_readme.py
python3 -m unittest discover -s tests -v
python3 scripts/validate_repository.py
# CI also runs the pinned official skills-ref validator against every skill.
```
