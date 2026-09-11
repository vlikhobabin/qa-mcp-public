## 1. Bind Legal And Publication Policy

- [x] 1.1 Add canonical Apache License 2.0 text, NOTICE/trademark attribution
  and exact PEP 639 `Apache-2.0` package metadata.
- [x] 1.2 Add machine-readable and human-readable publication policies with an
  audited-snapshot history boundary, role-based contacts and explicit OSS-08/09
  exclusions.
- [x] 1.3 Bind the exact published I2 surface and 23-mutation command while
  rejecting any I1 restoration or reconstruction.

## 2. Verify Policy

- [x] 2.1 Add and run offline exact-license/contact/history/I2 policy checks,
  including `verify_matrix.py --run-mutations`.
- [x] 2.2 Run strict change validation and `git diff --check`; record Windows,
  SSH, 1C, TestClient, live and network verification as not applicable and do
  not run them because this change affects repository policy only.
