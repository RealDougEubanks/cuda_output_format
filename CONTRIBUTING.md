# Contributing

Thanks for taking a look! This is a small Unmanic plugin with a single
hook, but contributions are welcome.

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

- Never commit directly to `main`. Branch as `feature/`, `fix/`, or
  `hotfix/` and open a PR.
- CI must pass before merge.
- Document any non-obvious decision in `docs/assumptions.md`.
- Bump `info.json` `version` and add a `changelog.md` entry on any
  user-visible change.
