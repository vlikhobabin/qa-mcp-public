## ADDED Requirements

### Requirement: Focused V2 safe-action subset is reviewed before live capture
The protocol lab SHALL select a reviewed focused subset before the first live
manager fixture V2 safe-action proof executes any action.

#### Scenario: Complete row is selected
- **WHEN** a manager fixture V2 safe-action row has an allowlisted action
  family, target marker, pre-state, post-state, recovery expectation,
  `mutates_business_data=false` and expected action result markers
- **THEN** the row may be included in the first focused proof subset
- **AND** the selection output records the row id, target id, target marker,
  action family and recovery expectation

#### Scenario: Unsafe row is excluded
- **WHEN** a candidate row is incomplete, mutating, button-like, a text input or
  value toggle, a business command or outside the V2 allowlist
- **THEN** the row is excluded from the focused proof subset
- **AND** the exclusion records reason, owner and residual risk when retained
  for review

#### Scenario: Subset stays narrow
- **WHEN** the first focused proof subset is prepared
- **THEN** it contains no more than two executable rows
- **AND** the preferred order is `switch_page` before `focus_element` when both
  rows are complete and safe
