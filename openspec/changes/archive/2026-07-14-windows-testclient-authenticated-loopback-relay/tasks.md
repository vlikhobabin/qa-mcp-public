## 1. Regression first

- [x] 1.1 Add Go RED tests for unauthorized/malformed/oversized/busy relay
      connections and fixed-target transparent binary forwarding.
- [x] 1.2 Add Python RED tests for exact-endpoint preface routing, partial
      configuration, direct compatibility and launch endpoint separation.

## 2. Relay implementation

- [x] 2.1 Implement the opt-in host-agent relay, health/status and
      installer/startup flags using the existing host-agent token.
- [x] 2.2 Implement the shared Python connector and migrate every TestClient
      socket consumer to it.
- [x] 2.3 Separate remote launch TPort from the routed protocol endpoint,
      preserve sanitized attachment metadata and keep readiness/reattach probes
      from consuming the single-manager loopback target.
- [x] 2.4 Wire qa compose and root station/T4 M9 configuration to the relay.
- [x] 2.5 Keep host-agent display/window resolution on the real TestClient
      TPort when protocol sockets use the relay listener.

## 3. Verification

- [x] 3.1 Run focused/full Go and offline Python suites, direct/relay matrices,
      Windows artifact build, strict OpenSpec validation, secret scan and diff.
- [x] 3.2 Run root T4 M9 through launch → attach → descriptor → non-empty
      `Валюты` grid and retain only bounded evidence plus owned cleanup.

## Verification Evidence

- Focused relay authentication/forwarding and Python connector matrices passed.
- Focused readiness tests prove that relay listener checks and repeated product
  attach do not authenticate/dial the target before the first protocol tool.
- Full Go, Windows cross-build and 829-test offline Python suites passed.
- The protected `ai-suite-qa:dev` image was rebuilt from the current sources
  with a rotated local-only bundled-data key; both team Help and QA containers
  report healthy.
- Final root T4 M9 returned a 46-element descriptor and 20-row `Валюты` grid
  through authenticated relay port 15382 while display targeting used real
  TPort 15381:
  `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260713T200946Z-release-ready-rerun/matrix/M09/solo-regression.json`.
