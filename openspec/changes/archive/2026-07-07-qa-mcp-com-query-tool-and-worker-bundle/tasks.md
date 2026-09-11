## 1. COM MCP Tooling

- [x] 1.1 Add a qa-mcp host-agent COM helper that builds authenticated `/com/execute` and `/com/doctor` requests, parses JSON responses, redacts structured errors, and honors configured timeout.
- [x] 1.2 Add `query_com` MCP tool with `infobase_path`, `user`, `password`, `query`, `timeout_sec`, and row-limit arguments, returning `{ok, rows, transport:"com", platform, bitness}` style metadata.
- [x] 1.3 Add `assert_com_count` MCP tool that executes a read-only COM query and compares the first numeric result using the existing count comparator vocabulary.
- [x] 1.4 Add local read-only query rejection for obvious write or side-effecting 1C query text before host-agent transport.
- [x] 1.5 Add `com_connector_doctor` MCP tool that calls host-agent doctor diagnostics and preserves TypeLib repair guidance.

## 2. Windows Host-Agent Diagnostics

- [x] 2.1 Add authenticated host-agent `/com/doctor` endpoint with semantic request decoding, timeout normalization, secret redaction, and execution-capacity limiting.
- [x] 2.2 Implement Windows COMConnector doctor checks for bitness, ProgID/CLSID/InprocServer32, TypeLib win64 path, elevated `System32\regsvr32.exe` guidance, CreateObject/Connect, and optional read-query smoke.
- [x] 2.3 Provide non-Windows/fake-test behavior that is deterministic in Linux tests while real COM execution remains Windows-only.
- [x] 2.4 Update host-agent `com_worker` health metadata to include warning severity and affected COM feature names when the worker is missing.

## 3. Release Bundling And Docs

- [x] 3.1 Teach `publish_self_hosted.sh` to accept `COM_WORKER_EXE` from ignored release defaults while preserving explicit `--com-worker-exe` precedence.
- [x] 3.2 Update delivery/runbook docs so missing `ai-com-worker.exe` is described as a feature-impact warning for host-side COM query and doctor read-smoke flows.
- [x] 3.3 Update relevant self-hosted release tests for release-default worker staging and warning wording.

## 4. Verification

- [x] 4.1 Add offline Python tests for `query_com`, `assert_com_count`, read-only rejection, missing host-agent config, and doctor wrapper response handling.
- [x] 4.2 Add Go tests for `/com/doctor` authentication/policy, fake green smoke, TypeLib-missing repair guidance, and COM worker health feature-impact metadata.
- [x] 4.3 Run matrix preflight and retain output under `.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/`.
- [x] 4.4 Run focused Python, Go, release-script, OpenSpec, and suite regression checks required by the changed files.
- [x] 4.5 Retain bounded evidence JSON summaries for COM query, release/health, doctor, and the Windows COM live-smoke provider gap.
- [x] 4.6 Run matrix archive-gate and record the retained evidence paths before sync/archive.
