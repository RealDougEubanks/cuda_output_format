<!--
doc: CONTRIBUTING
last-refreshed: 2026-05-11
generated-by: doc-refresh skill
-->

# Contributing

Contributions welcome.

The upstream encoder plugin ([Josh5/unmanic.plugin.encoder_video_hevc_nvenc](https://github.com/Josh5/unmanic.plugin.encoder_video_hevc_nvenc)) is **archived** (read-only), so this fork is the active line of development. The vendored `lib/ffmpeg/` helpers module ([Josh5/unmanic.plugin.helpers.ffmpeg](https://github.com/Josh5/unmanic.plugin.helpers.ffmpeg)) is still open; hardening fixes there should still be proposed upstream as well as patched here.

> **SECURITY:** Never commit secrets, API keys, or credentials. None
> are required to develop or run this plugin. If you suspect a
> vulnerability, follow [`SECURITY.md`](./SECURITY.md) — do **not**
> open a public issue.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

For reproducible installs with verified hashes (release prep, supply-chain audits), use the lockfile instead:

```bash
pip install --require-hashes -r requirements-dev.lock
```

Regenerate the lockfile after changing `requirements-dev.txt`:

```bash
pip install pip-tools
pip-compile --allow-unsafe --generate-hashes --output-file=requirements-dev.lock requirements-dev.txt
```

## Running the test suite

```bash
pytest
```

39 tests cover the NVDEC argument-building logic, output-container
remux logic, the advanced/simple option branches, stream-mapping
codec gating, both Unmanic hook entry points, the `Settings` form
visibility toggles, and the security-critical `eval` removal in
`lib/ffmpeg/parser.py`. Unmanic's plugin runtime is mocked at the
test boundary via `tests/conftest.py`; the suite does not require a
live Unmanic install. Coverage gate: ≥ 85% (currently 93%).

## Linting, formatting, and type checking

```bash
ruff check .
ruff format .
mypy
```

CI runs `ruff check`, `ruff format --check`, `mypy`, `pytest` (with
coverage), and `pip-audit --strict` on every push and pull request,
against Python 3.10, 3.11, and 3.12. CodeQL Python data-flow
analysis runs on push, PR, and weekly. A separate weekly
`security-scan` workflow runs `pip-audit` + `bandit` and
auto-creates issues for high/critical findings.

## Workflow

1. Branch from `main`:
   ```bash
   git checkout main && git pull
   git checkout -b fix/short-description
   ```
2. Make your change.
3. Run the local checks:
   ```bash
   ruff check . && ruff format --check . && mypy && pytest
   ```
4. If user-visible behavior changed, bump `version` in `info.json`
   and add a `changelog.md` entry.
5. If you made a non-obvious decision, record it in
   `docs/assumptions.md`.
6. Open a PR. CI must be green before merge.

## PR Checklist

- [ ] Tests pass locally (`pytest`) — coverage stays ≥ 85%
- [ ] `ruff check .` and `ruff format --check .` clean
- [ ] `mypy` clean
- [ ] `pip-audit -r requirements-dev.txt --strict` clean
- [ ] No new secrets or credentials added
- [ ] Docs updated if behavior changed
- [ ] `info.json` version bumped + changelog entry, if user-visible

## Releasing a new version

1. Bump `version` in `info.json`.
2. Add a `**X.Y.Z**` section at the top of `changelog.md`.
3. Open a PR, get CI green, and merge to `main`.
4. Tag the merge commit and push:
   ```bash
   git checkout main && git pull
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
5. Two workflows fire automatically:
   - `release.yml` — builds the plugin zip, creates a GitHub
     Release at `vX.Y.Z`, and attaches the zip as an asset.
   - `publish-repo.yml` — rebuilds the `repo` branch so Unmanic
     installs pick up the new version. (Triggered by the merge to
     `main`, not the tag.)

## License

By contributing, you agree your contributions are licensed under the
GPL-3.0, the same license as the rest of the project.
