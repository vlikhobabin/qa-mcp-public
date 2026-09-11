## 1. RED Contract

- [x] 1.1 Add focused hostile tests for bounded opaque identity, reserved
  environment replacement, malformed/oversized input and forbidden global
  input APIs; retain the exact failing RED command and expected missing
  foundation behavior.
- [x] 1.2 Add a Windows-native focused lifecycle test that proves exact desktop
  creation/closure and windowless child placement without exposing UI or
  environment contents.

## 2. Dormant Foundation

- [x] 2.1 Implement cross-platform internal run-identity, desktop-name and
  deterministic reserved-environment policy with fail-closed bounds.
- [x] 2.2 Implement Windows-only exact named-desktop and windowless-process
  primitives with windowless creation and exact handle cleanup.
- [x] 2.3 Prove there is no existing non-test call site, public route, wire-field
  change, desktop activation or global-input API in S1 scope.

## 3. Verification And Evidence

- [x] 3.1 Run the exact focused suite, full Go suite, Windows test cross-build
  and Windows host-agent cross-build; retain bounded outputs.
- [x] 3.2 Run the focused test natively on the authorized Windows host and
  retain sanitized identity/result/cleanup evidence only.
- [x] 3.3 Prove canonical added production LOC is `<=300`, run strict OpenSpec,
  manifest scope-check and `git diff --check`, and index the reproducible
  evidence without raw captures or secrets.
