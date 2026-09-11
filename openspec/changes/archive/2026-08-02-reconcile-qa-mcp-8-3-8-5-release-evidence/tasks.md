## 1. Evidence Inventory And Route Selection

- [x] 1.1 Audit the retained 8.3 Windows model-B release evidence, record its image/release identity and command outcomes, and accept it only if it proves HTTP/MCP attach/read with the full `8.3.27.2130` version plus cleanup or retained-runtime disposition.
- [x] 1.2 Audit the retained 8.5 Linux-native grid evidence, record which protocol/version claims it proves, and do not count it as the release-equivalent HTTP/MCP proof unless its transcript actually crosses that boundary.
- [x] 1.3 Select the smallest missing runtime route (Windows model-B or Linux host-platform model-A), run the project runtime preflight before live execution, and retain the route/preflight decision under `.artifacts/openspec/reconcile-qa-mcp-8-3-8-5-release-evidence/<run-id>/`.

## 2. Multi-Version Release Evidence

- [x] 2.1 Reuse a qualifying 8.3 Windows-native release run or execute one bounded current-artifact model-A/model-B attach/read smoke; retain a sanitized summary naming `/mcp`, `8.3.27.2130`, model, attach/read outcomes, artifact identity, and cleanup/disposition.
- [x] 2.2 Execute exactly one bounded 8.5 release-equivalent attach/read smoke when no qualifying evidence exists; prove the full live version `8.5.1.1343`, the validated 8.3 protocol-data fallback, canonical `/mcp`, model, outcomes, and cleanup.
- [x] 2.3 If the 8.5 proof uses Linux model-A, run `ldd` against `/opt/1cv8/x86_64/8.5.1.1343/1cv8` and retain a zero-missing result or explicit runtime gap; otherwise record model-A and `ldd` as N/A with residual risk.
- [x] 2.4 Sanitize the reconciled evidence summary so it contains no credentials, raw business rows, full infobases, raw captures, or large platform logs; stop and route a separate protocol change if validate-first goes red.
- [x] 2.5 Add a RED regression for the UTF-8 middleware's post-body ASGI receive lifecycle, then forward the original receive channel after the one validated body replay so Streamable HTTP can deliver and close its response.
- [x] 2.6 Add a RED regression for installed/container ownership-root resolution, then make stateless cleanup prefer an explicit override and otherwise follow `QA_MCP_HOME` before the source-checkout fallback.

## 3. Active Delivery Contract And Documentation

- [x] 3.1 Add or extend a focused documentation contract test and record the RED result for stale active `/mcp/` examples or missing multi-version/full-version guidance.
- [x] 3.2 Update active release/delivery docs and package notes to use `/mcp`, name `8.3.27.2130` and `8.5.1.1343`, distinguish live platform identity from protocol-data family, and reserve 8.5 recapture/bundle population for a red capability.
- [x] 3.3 Record the qualifying 8.3/8.5 evidence paths, model and observed outcomes in the card and ChangeRail delivery manifest without tracking raw runtime evidence.

## 4. Verification And Handoff

- [x] 4.1 Run the focused documentation/release tests and record why they fail on stale or missing active guidance.
- [x] 4.2 Run `python3 scripts/public-surface-scan.py`, the affected focused test set, and any runtime evidence validators; record commands and observed outcomes.
- [x] 4.3 Run `openspec status --change reconcile-qa-mcp-8-3-8-5-release-evidence --json`, `openspec instructions apply --change reconcile-qa-mcp-8-3-8-5-release-evidence --json`, `openspec validate reconcile-qa-mcp-8-3-8-5-release-evidence --strict`, `openspec validate --all --strict`, and `git diff --check`.
- [x] 4.4 Reconcile the delivery manifest against the working tree, sync the delta spec, archive the change, move the card to `3.inprogress`, and leave the payload ready for independent review.
