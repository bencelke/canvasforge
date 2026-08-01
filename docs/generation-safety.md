# Generation Safety

1. Manifest remains the source of truth.
2. Generated files must not be edited manually — regenerate instead.
3. Unknown controls/properties fail closed.
4. No silent omission of unsupported sections (unless `--allow-partial` with explicit warnings).
5. Output is Candidate until Studio evidence exists.
6. `generated/` is gitignored (except `.gitkeep`).
7. Reports store manifest basenames, not absolute paths.
8. No secrets, telemetry, network, auth, or `.msapp` packaging.
9. OnSelect / Notify omitted until Studio-exported evidence exists.
10. Deterministic build IDs exclude wall-clock timestamps.
