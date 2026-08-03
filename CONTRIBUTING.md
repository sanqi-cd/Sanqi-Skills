# Contributing

Thanks for helping improve Sanqi Skills. Keep contributions focused on a concrete user workflow and preserve the repository's cross-client portability.

## Skill requirements

- Use a lowercase hyphenated folder name that exactly matches frontmatter `name`.
- Keep top-level frontmatter within the Agent Skills standard. Put repository display fields under `metadata` as strings.
- Write a precise `description` with positive triggers, useful boundaries, and the expected outcome.
- Keep `SKILL.md` concise and link directly to any scripts, references, assets, or evals it needs.
- Add `agents/openai.yaml`, at least 12 balanced trigger cases, and at least 3 output eval cases.
- Test deterministic scripts with normal and failure inputs. Never commit credentials, generated outputs, caches, or operating-system files.
- Keep public examples deterministic. When a renderer or example source changes, run `python3 scripts/capture_examples.py` and review every refreshed screenshot.

## Verification

Run before opening a pull request:

```bash
python3 scripts/sync_readme.py
python3 -m unittest discover -s tests -v
python3 scripts/validate_repository.py
git diff --check
```

The same deterministic checks run in GitHub Actions. Model-based and external-service evals may require credentials; report those results and limitations explicitly in the pull request instead of storing secrets in the repository.

CI additionally installs a commit-pinned copy of the official `skills-ref` reference validator and checks every Skill. Pin updates should be deliberate pull requests so upstream changes cannot silently break releases.
