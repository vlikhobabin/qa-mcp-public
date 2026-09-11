## ADDED Requirements

### Requirement: Corpus semantic mappings link to primary evidence

The protocol lab SHALL keep semantic mappings between corpus case ids and
help/meta/EDT references as compact supporting artifacts that identify the
primary wire evidence path, mapping status, semantic source and unresolved
reason when applicable.

#### Scenario: Corpus case receives a semantic mapping

- **WHEN** a reviewed corpus case is linked to a form, element, object-model
  term or help topic from help, metadata or EDT tooling
- **THEN** the semantic mapping records the `case_id`, target family or object,
  provider source, mapping status and primary protocol evidence path
- **AND** the mapping states that capture frames, normalized hashes and
  replay/probe status remain the protocol evidence of record

#### Scenario: Corpus case cannot be mapped

- **WHEN** a corpus row has no stable metadata object, form element, GUID,
  name or help topic that can be linked safely
- **THEN** the semantic mapping records the row as unresolved or partial with a
  reason and residual risk
- **AND** the unresolved mapping remains visible instead of being omitted from
  reviewed coverage notes
