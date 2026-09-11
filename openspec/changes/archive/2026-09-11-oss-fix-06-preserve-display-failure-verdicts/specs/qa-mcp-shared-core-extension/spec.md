## ADDED Requirements

### Requirement: Window-list primitive failures preserve operation verdicts
The trusted window-list adapter MUST translate backend failures into a typed
non-success operation result before public reconstruction. A typed display
exception MUST NOT become success with an empty value. Ordinary exceptions MUST
also remain failures through the composed operation.

#### Scenario: Registered window-list backend fails
- **WHEN** an admitted bound or unbound composed get_window_list call encounters a controlled typed display error or ordinary backend exception
- **THEN** the real default executor returns a failure using existing fixed error vocabulary
- **AND** the bound public result does not claim success or a successful empty inventory.

### Requirement: Window inventory and generic successful data remain distinct from failure
Successful window inventories MUST retain an exact count, including zero for an
empty inventory. Generic handlers MUST NOT infer failure from arbitrary successful
dictionary keys; translation belongs to the trusted primitive adapter.

#### Scenario: Inventory succeeds empty or nonempty
- **WHEN** the registered window-list backend returns an empty or nonempty inventory
- **THEN** the composed result succeeds with the exact count of windows returned.

#### Scenario: Generic successful value resembles an error
- **WHEN** an unrelated generic handler returns successful data containing error, ok or verdict-like keys
- **THEN** the generic executor preserves success and the original value
- **AND** an explicit typed operation result retains its supplied verdict.

### Requirement: Window-list failures retain bound privacy and direct compatibility
Bound window-list results MUST expose fixed safe failure diagnostics without
arbitrary backend prose, private UI strings, credentials or physical paths.
Deliberate direct legacy calls MUST retain their typed error dictionary and
successful inventory shape while composed adapters preserve typed verdicts.

#### Scenario: Bound error contains hostile diagnostic fields
- **WHEN** a local or Windows-host bound window-list backend raises an error with secret-bearing text or metadata
- **THEN** the serialized result contains only the existing fixed public failure code/message and admitted provenance
- **AND** backend secret fragments, captions and paths are absent.

#### Scenario: Direct legacy window inventory is called
- **WHEN** a deliberate direct legacy call receives a typed backend error or valid inventory
- **THEN** its documented error dictionary or inventory fields/count remain compatible.
