# Assumptions

This file records non-obvious decisions made in the `cuda_output_format` plugin.

---

- **Assumption:** When `-hwaccel_device <value>` is present, the value is exactly one token immediately following the flag, so the safe insertion point for `-hwaccel_output_format cuda` is `index('-hwaccel_device') + 2`.
- **Why:** ffmpeg's CLI grammar treats `-hwaccel_device` as a flag taking exactly one argument. Inserting before the device pair would leave `-hwaccel_output_format` between `-hwaccel cuda` and the device selection, which is legal but reorders related options; inserting after keeps all `-hwaccel*` options grouped.
- **Recorded by:** Claude (golden-rules audit)
- **Date:** 2026-05-11

---

- **Assumption:** When `-hwaccel_device` is absent but `-hwaccel cuda` is present, inserting at `index('-hwaccel') + 2` is safe — i.e., the token after `cuda` is either an input flag (`-i`, `-c:v`, etc.) or end-of-args.
- **Why:** Per ffmpeg docs, `-hwaccel` takes exactly one argument (the method name).
- **Recorded by:** Claude (golden-rules audit)
- **Date:** 2026-05-11

---

- **Assumption:** Errors during injection must never break the Unmanic worker. On any unexpected exception, we log and return `data` unchanged so the original ffmpeg command runs.
- **Why:** A plugin failure should degrade to "no optimization" rather than failing the user's transcode job.
- **Recorded by:** Claude (golden-rules audit)
- **Date:** 2026-05-11

---

- **Assumption:** String `exec_command` values are tokenized with `str.split()` (whitespace split, no shell quoting).
- **Why:** Unmanic passes ffmpeg invocations as lists in practice; the string branch is a defensive fallback. Filenames containing whitespace would be misparsed, but Unmanic does not produce such strings. If this changes, switch to `shlex.split` and re-quote on output.
- **Recorded by:** Claude (golden-rules audit)
- **Date:** 2026-05-11
