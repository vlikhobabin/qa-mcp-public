## ADDED Requirements

### Requirement: A date value commits on an open-link create form

The open-link date write SHALL commit a `DD.MM.YYYY` value into a managed-form date field on a create
form so that the value reads back from the field, rather than only opening the calendar picker and
leaving the field empty. The date write SHALL drive the field input (masked-input typing or a
deterministic calendar pick) without getting stuck on the calendar button.

#### Scenario: Дата договора reads back committed

- **WHEN** `write_form_date(open_link="e1cib/data/Справочник.ДоговорыКонтрагентов", field="ДатаДоговора",
  date="30.06.2026")` runs on the demo10413 create form
- **THEN** the field reads back the committed date (not an empty mask)
- **AND** the calendar picker is not left open
- **AND** the run retains a screenshot / read-back as evidence

#### Scenario: Date write does not stall on the calendar button

- **WHEN** the date write targets the date field
- **THEN** the value is entered into the field's text input
- **AND** clicking the field's calendar button is not the mechanism that determines the value
