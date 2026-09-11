## ADDED Requirements

### Requirement: Research tools reuse package protocol APIs
The protocol lab SHALL keep exploratory protocol tools aligned with promoted
`qa_mcp.protocol` APIs after package promotion.

#### Scenario: Probe tool imports package session API
- **WHEN** a protocol research script needs promoted frame, template or
  read-only session behavior
- **THEN** it imports the package API instead of maintaining a divergent copy
- **AND** any remaining script-local logic is limited to CLI parsing,
  evidence file layout or research-specific orchestration

### Requirement: Existing protocol research CLIs remain compatible
The protocol lab SHALL preserve existing Windows-native protocol research CLI
entrypoints during package promotion.

#### Scenario: Research CLI is invoked after package promotion
- **WHEN** an operator runs an existing protocol research command such as
  `python_manager_probe.py`, `protocol_corpus_runner.py` or
  `compare_corpus_runs.py`
- **THEN** documented arguments and output schemas continue to work or a
  documented migration note explains the change
- **AND** compatibility is covered by offline tests or smoke commands

### Requirement: Wrapper changes do not rewrite historical evidence
The protocol lab SHALL avoid silently replacing committed protocol evidence
when research tools are refactored around package APIs.

#### Scenario: Wrapper refactor affects evidence generation
- **WHEN** a wrapper refactor changes generated compact evidence
- **THEN** new evidence is written under a new reviewed evidence id
- **AND** `docs/protocol-research/evidence-index.md` records the new output
- **AND** raw runtime output remains ignored
