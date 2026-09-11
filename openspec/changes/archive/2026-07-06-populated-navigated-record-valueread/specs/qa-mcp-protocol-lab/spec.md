## ADDED Requirements

### Requirement: Populated navigated record values are read capture-free
The protocol lab SHALL read back the actual object-attribute VALUES of an
EXISTING POPULATED catalog or document RECORD form that is opened capture-free
(no Vanessa, no per-form capture) by navigation, and SHALL prove at least one
non-empty value against an independent oracle.

#### Scenario: A populated record value is read back and matches OData
- **WHEN** an existing populated catalog or document record on a real config is
  opened capture-free — by record ref nav-link (`e1cib/data/Справочник.X?ref=<guid>`)
  or by row-drill (`open_card` from a positioned `read_list_row(where=…)` row) —
  and its object-attribute fields are value-read against the navigated form's `S.F`
- **THEN** at least one non-empty object-attribute value (for example `Код` or
  `Наименование`) is returned from the `e0 4b 53` «стал равен» envelope
- **AND** that value matches the same field read from OData for the same record
- **AND** the read performs no mutation on the record or infobase

#### Scenario: An empty or unreadable record is reported, not faked
- **WHEN** the opened record form carries no value envelope for a queried field
  (for example a create-form or a genuinely empty attribute)
- **THEN** the reader returns an explicit empty/absent value for that field
  rather than fabricating a value
- **AND** the result distinguishes "read succeeded, value empty" from
  "read failed / form not reached" so a populated-record proof is not claimed
  from an empty form

### Requirement: Populated record value-read retains live verification evidence
The protocol lab SHALL retain compact evidence for the populated-record
value-read proof, including the config and record identity, the open route used
(ref nav-link or row-drill), the fields read, and the OData oracle comparison.

#### Scenario: Evidence records the populated-record proof
- **WHEN** the populated-record value-read is verified live
- **THEN** the retained evidence records the config/infobase, record ref or list
  row used, the open route, each read field with its value, and the matching
  OData value
- **AND** the evidence notes the cold-client boundary and the navigated-form
  `S.F` retarget used so the run is reproducible
