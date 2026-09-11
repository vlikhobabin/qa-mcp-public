## ADDED Requirements

### Requirement: Lifecycle-bound Windows display proof is retained safely

The protocol lab SHALL verify the remote lifecycle-window target contract through focused Python and Go tests plus Windows-native host-agent evidence. The proof SHALL cover an empty-title TestClient target, implicit lifecycle/client targeting for screenshot, key, text, click, and visible-list-cell routes, explicit-selector precedence, unrelated-foreground refusal, typed desktop-session diagnostics, and cleanup. Reviewed/card evidence MUST retain only sanitized booleans, reason codes, capability/version facts, and test outcomes; raw screenshots, HWNDs, PIDs, titles, credentials, host-agent logs, and infobase contents MUST remain ignored and uncommitted.

#### Scenario: Empty-title target and unrelated foreground are distinguished

- **WHEN** the Windows proof runs with an owned or attached TestClient target whose caption is empty and another application is foreground
- **THEN** lifecycle-bound screenshot and safe key delivery report the TestClient target as selected
- **AND** the retained summary records only target-matched and unrelated-foreground-untouched booleans.

#### Scenario: Display primitive matrix is evidenced

- **WHEN** the lifecycle-window verification bundle is completed
- **THEN** it records outcomes for `capture_screenshot`, `send_keys`, `type_text`, `click`, and visible-list-cell reads
- **AND** each row names its command/test route and passed, blocked, or not-applicable outcome.

#### Scenario: Session failures remain typed and bounded

- **WHEN** locked, disconnected, and non-interactive states are exercised through native tests or an accepted typed-probe fallback
- **THEN** the evidence records a distinct expected/observed reason-code match for each state
- **AND** contains no raw desktop or host-agent payload.

#### Scenario: Runtime artifacts stay ignored

- **WHEN** Windows verification produces screenshots, binaries, temporary payloads, or logs
- **THEN** those artifacts remain under ignored `.runtime/` paths and cleanup is audited
- **AND** only sanitized command outcomes are summarized in the card and delivery manifest.
