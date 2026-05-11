<!--
doc: CONTRIBUTING
last-refreshed: 2026-05-11
generated-by: doc-refresh skill
-->

# Contributing

Thanks for taking a look! This is a small Unmanic plugin with a single
hook, but contributions are welcome.

> **SECURITY:** Never commit secrets, API keys, or credentials. None
> are needed to develop or run this plugin. If you suspect a
> vulnerability, follow [`SECURITY.md`](./SECURITY.md) — do **not**
> open a public issue.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Running the test suite

```bash
pytest
```

## Linting and formatting

```bash
ruff check .
ruff format .
```

CI runs `ruff check`, `ruff format --check`, and `pytest` against
Python 3.10, 3.11, and 3.12 on every push and pull request.

## Workflow

1. Branch from `main`:
   ```bash
   git checkout main && git pull
   git checkout -b fix/short-description
   ```
2. Make your change.
3. Run the local checks:
   ```bash
   ruff check . && ruff format --check . && pytest
   ```
4. If user-visible behavior changed, bump `version` in `info.json`
   and add a `changelog.md` entry.
5. If you made a non-obvious decision, record it in
   `docs/assumptions.md`.
6. Open a PR. CI must be green before merge.

## PR Checklist

- [ ] Tests pass locally (`pytest`)
- [ ] `ruff check .` and `ruff format --check .` clean
- [ ] No new secrets or credentials added
- [ ] Docs updated if behavior changed
- [ ] `info.json` version bumped + changelog entry, if user-visible
