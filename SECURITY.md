<!--
doc: SECURITY
last-refreshed: 2026-05-11
generated-by: doc-refresh skill
-->

# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report privately via GitHub's
[private vulnerability reporting](https://github.com/RealDougEubanks/cuda_output_format/security/advisories/new).
You will receive an acknowledgement within a few days. Fixes for
confirmed issues are released as patch versions and credited in
`changelog.md` unless you ask to remain anonymous.

## Scope

This plugin runs inside an Unmanic worker process and only mutates an
in-memory `data['exec_command']` list. It does not open network
connections, read user files, execute subprocesses, or handle
credentials.

In scope:

- Defects that cause the plugin to corrupt an ffmpeg command in a way
  that could be exploited (e.g., argument injection via crafted input).
- Defects that cause the plugin to leak information from the worker
  process.

Out of scope:

- Vulnerabilities in Unmanic itself — please report those upstream at
  https://github.com/Unmanic/unmanic.
- Vulnerabilities in ffmpeg, NVENC, or your operating system.

## Supported versions

Only the latest released version (see `info.json` `version`) receives
security fixes.

## Automated scanning

This repository runs `pip-audit` (dependency CVEs) and `bandit`
(Python static analysis) on every push and on a weekly schedule. Any
high or critical finding automatically opens a tracking issue with
the `security` label.
