## ADDED Requirements

### Requirement: Team bridge bootstrap registration evidence
The component SHALL provide offline contract coverage and a supervised
Linux-manager/Windows-host smoke that proves bootstrap redemption, protected
refresh, per-user/project/server attribution, restart recovery and exact owned
process cleanup.

#### Scenario: Windows bridge survives refresh and restart
- **WHEN** component preflight passes and a Windows host agent consumes the
  Linux fixture through the protected onboarding client
- **THEN** initial registration, repeated heartbeats and a task restart all use
  fresh one-time registration credentials
- **AND** the registered user/project/server attribution remains unchanged

#### Scenario: Registered bridge serves an approved QA probe
- **WHEN** the restarted bridge reports registered health
- **THEN** an authenticated read-only window-list probe succeeds through the
  built Windows artifact
- **AND** retained evidence contains only its response digest and count, not
  window titles or raw protocol data

#### Scenario: Smoke cleanup is complete
- **WHEN** the supervised live smoke ends
- **THEN** only the uniquely named scheduled task, staged installation,
  temporary inputs, fixture and tunnel owned by that run are stopped or removed
- **AND** post-cleanup checks show no owned process or listening port remains

### Requirement: Team bridge bootstrap registration evidence safety
The component MUST use only approved read-only probes, clean only resources the
run owns and retain no secret-bearing raw capture or business-data mutation.

#### Scenario: Invalid or unsafe input fails closed
- **WHEN** offline tests exercise expired, replayed, revoked, mismatched,
  unprotected or unsafe-transport inputs
- **THEN** every case fails closed without usable partial state or credential
  fallback and exposes only bounded diagnostics

#### Scenario: Evidence is retained
- **WHEN** offline and live verification completes
- **THEN** tracked tests and ignored delivery evidence retain only contract
  source/version, identifiers, statuses, counts, timestamps and SHA-256 digests
- **AND** secret scans find no raw grant, Git authorization, registration
  credential or bridge callback token
