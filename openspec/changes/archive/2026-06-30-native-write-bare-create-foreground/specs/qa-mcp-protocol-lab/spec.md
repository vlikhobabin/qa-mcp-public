## ADDED Requirements

### Requirement: Native write tools foreground bare-create links
The qa-mcp native write path SHALL foreground `e1cib/data/<metadata>` links
without a `?ref=` parameter before label-based write input begins.

#### Scenario: Bare-create link foregrounds for label input
- **WHEN** a caller invokes `write_form_fields_by_label` with
  `open_link="e1cib/data/Справочник.Валюты"`
- **THEN** qa-mcp uses a create-scoped foreground route that accepts the
  list-read replay tail as partial only after the create form renders
- **AND** the result identifies the foreground method and the opened form or a
  structured foreground failure reason

#### Scenario: Existing foreground modes remain isolated
- **WHEN** a caller provides a list link or a `?ref=` data link
- **THEN** qa-mcp keeps the existing list/record foreground replay behavior
- **AND** the create-form foreground route is not selected

### Requirement: Bare-create foreground proof is retained
New live claims about bare-create write foregrounding SHALL retain UI evidence
for the active form without committing raw captures or platform logs.

#### Scenario: Create foreground evidence names target forms
- **WHEN** live TestClient proof is run for bare-create foregrounding
- **THEN** retained evidence records the target nav-link, foreground method,
  active window or form tree, screenshot or fallback diagnostic and result
  status
- **AND** raw captures, screenshots and platform logs remain under ignored
  runtime or artifact paths unless curated explicitly
