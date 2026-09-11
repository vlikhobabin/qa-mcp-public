## Context

The installed build is a same-family Case A candidate. The active project
profile cannot drive the fixture-specific OData assertion from the retired
platform-support lab, so that RED result is an environment mismatch rather than
a wire-protocol verdict.

## Decisions

1. Use Vanessa Automation `1.2.043.18` as a genuine TestManager on platform
   `8.3.27.2214` and capture a thick TestClient opening
   `e1cib/list/Справочник.Валюты`.
2. Use the existing bundled 8.3 templates, with synthesized platform identity
   `8.3.27.2214`, for the compatibility leg.
3. Require all four read-only UI regression checks to pass: assert semantics,
   two-object navigation, live descriptor enumeration and dirty-state list
   reading.
4. Do not replace committed templates when the existing corpus replays green.
5. Keep raw pcap, normalized traffic, screenshots, logs and the disposable
   infobase under ignored runtime paths. Commit only a compact outcome and
   artifact hashes.
6. Use the explicit platform-support force path to admit the build because the
   legacy full verdict depends on a retired OData publication; the retained
   report must state that the proof is read-only and must not claim a write
   roundtrip.

## Risks

- The compatibility run does not execute a persistent business-data write.
  This is intentional because no write intent was requested; the read-only
  protocol surface and genuine manager handshake are covered.
- Raw evidence remains machine-local. Content hashes and normalized counts make
  accidental substitution detectable while keeping captures out of Git.
