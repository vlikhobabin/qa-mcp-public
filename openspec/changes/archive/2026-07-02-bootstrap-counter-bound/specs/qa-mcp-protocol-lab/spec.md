## ADDED Requirements

### Requirement: Synthesized bootstrap random counters fit every generated frame
The synthesized bootstrap generator SHALL choose a default random `counter_base` whose derived counters fit the fixed
counter field for every generated bootstrap frame. The maximum random base MUST be computed from the bootstrap template
counter deltas rather than by assuming that any five-digit base is safe.

#### Scenario: Maximum default base renders all frames
- **WHEN** the default random generator selects the highest allowed base offset
- **THEN** frames 1 through 4 render their counters without raising a fixed-width counter `ValueError`
- **AND** frame 4's sequence is still the selected base plus its template delta.

#### Scenario: Explicit invalid base still fails loudly
- **WHEN** a caller passes an explicit `counter_base` whose derived frame counter exceeds the fixed-width field
- **THEN** bootstrap synthesis raises `ValueError`
- **AND** the invalid explicit value is not silently clamped.
