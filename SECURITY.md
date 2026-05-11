<!--
doc: SECURITY
last-refreshed: 2026-05-11
generated-by: doc-refresh skill
-->

# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report privately via GitHub's
[private vulnerability reporting](https://github.com/RealDougEubanks/unmanic.plugin.encoder_video_hevc_nvenc_gpu/security/advisories/new).
You will receive an acknowledgement within a few days. Fixes for
confirmed issues are released as patch versions and credited in
`changelog.md` unless you ask to remain anonymous.

## Scope

This plugin runs inside an Unmanic worker process. It probes the
media file with `ffprobe` and constructs an ffmpeg argument list
that Unmanic then executes. It does not open network connections,
write to disk outside Unmanic-managed paths, or handle
credentials.

In scope:

- Defects that allow argument injection into the ffmpeg command via
  crafted file paths, file names, or media metadata.
- Defects that cause the plugin to read or write paths outside the
  Unmanic-supplied `file_in` / `file_out` boundaries.
- Defects that leak information from the worker process or its
  environment.
- Vulnerabilities in vendored `lib/ffmpeg/` code (a snapshot of
  Josh5/unmanic.plugin.helpers.ffmpeg). We will accept and patch
  these here while also reporting them upstream.

Out of scope:

- Vulnerabilities in Unmanic itself — please report those upstream
  at https://github.com/Unmanic/unmanic.
- Vulnerabilities in ffmpeg, ffprobe, NVENC, NVDEC, or your operating
  system.
- Vulnerabilities in the upstream Josh5 encoder plugin that are not
  present in this fork's modifications.

## Supported versions

Only the latest released version (see `info.json` `version`) receives
security fixes. Older releases will not be patched.

## Automated scanning

This repository runs the following automated security tooling:

- **pip-audit** (dependency CVEs) — on every push, PR, and weekly.
- **bandit** (Python SAST rules) — weekly.
- **CodeQL** (Python data-flow analysis) — on push, PR, and weekly.
- **GitHub secret scanning** and **Dependabot alerts** — enabled at
  the repository level.

Any High or Critical finding from `pip-audit` or `bandit` opens (or
appends to) a tracking issue labeled `security` + `automated`.
CodeQL findings appear under the repository's Security tab.

## Source code

This repository is the complete corresponding source for the
installable plugin zip, per
[GPL-3.0 §6](https://www.gnu.org/licenses/gpl-3.0.html#section6).
Each release on the
[Releases](https://github.com/RealDougEubanks/unmanic.plugin.encoder_video_hevc_nvenc_gpu/releases)
page mirrors this repository's contents at the matching `vX.Y.Z` tag.
