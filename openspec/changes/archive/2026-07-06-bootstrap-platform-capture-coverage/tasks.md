## 1. Bootstrap Selection

- [x] 1.1 Replace bootstrap's lexicographic executable selection with parsed version sorting and direct-capture-family preference.
- [x] 1.2 Add bootstrap diagnostics for explicit or detected platform families without direct bundled captures, including the 8.5 validated-fallback warning and unsupported-family stop.
- [x] 1.3 Add focused script contract tests for mixed 8.3/8.5 selection and the warning/`QA_MCP_PLATFORM_VERSION` behavior.

## 2. Runtime Capture Fallback

- [x] 2.1 Add a central `_bundled` helper for capture-data family resolution, mapping 8.5 to the validated 8.3 corpus and leaving unsupported families fail-closed.
- [x] 2.2 Route `resolve_capture_dir()` and accepted-mapping default resolution through the helper.
- [x] 2.3 Update bundled-version tests to prove 8.5 resolves capture-backed reads through bundled 8.3 data without changing active-version selection.
- [x] 2.4 Stamp full captured replay frames with the live platform version before GUID rebinding so 8.5 fallback uses 8.3 bytes without declaring an 8.3 session.

## 3. Docs And Verification

- [x] 3.1 Update delivery and bundled-corpus documentation to state the 8.5 validate-first fallback rule and default direct-covered auto-selection.
- [x] 3.2 Run focused pytest for bootstrap/versioning behavior plus OpenSpec validation and diff checks.
- [x] 3.3 Run Linux-native 8.5 read-only grid smoke after runtime preflight and retain sanitized row-count/cleanup evidence.
- [x] 3.4 Record why Windows model-B live bootstrap/grid-read evidence is not produced in this Linux delivery and where the next release smoke transcript must be retained.
