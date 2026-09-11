## 1. Protocol handshake

- [x] 1.1 Add the stable display protocol id to authenticated host-agent
  `/version` and cover it in Go tests.
- [x] 1.2 Replace default exact-label gating with protocol compatibility plus
  the bounded legacy allowlist fallback.
- [x] 1.3 Preserve exact explicit version and SHA pin behavior.

## 2. Diagnostics

- [x] 2.1 Return a bounded version relationship from handshake and surface it
  in doctor host-agent data.
- [x] 2.2 Update host-agent documentation and absorb the satellite backlog card.

## 3. Verify and archive

- [x] 3.1 Run focused display-backend/doctor and Go tests plus the repository
  verification floor.
- [x] 3.2 Sync both modified capabilities, validate strict OpenSpec and archive
  the change with retained summaries.
