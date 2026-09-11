## Why

The accepted read-only mappings are blocked from richer element-family
coverage by fixture gaps for `Button`, `Table`, `CommandBar`, `Page`, `Label`
and `CheckBox`. The lab needs a controlled fixture plan before adding action
or write cases, and that plan must keep generated EDT workspaces and raw
fixture output outside git.

## What Changes

- Identify or author a controlled read-only fixture coverage plan for the
  missing element families, including case ids, expected response markers,
  safety class and out-of-scope reasons when a family cannot be covered yet.
- Define how optional EDT usage may author or validate fixture form shapes
  while raw protocol capture and replay remain independent from EDT/meta
  services.
- Feed controlled fixture surfaces back into the corpus runner as explicit
  case manifests or seeded matrix updates, not as inferred protocol claims.
- Record compact evidence expectations for fixture authoring, EDT validation,
  corpus captures, replay/probe confirmation and retained runtime-output
  boundaries.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require controlled read-only fixture coverage plans
  for missing element families before those families can become accepted
  protocol mappings.

## Impact

- Touches protocol research docs, optional corpus runner manifests or seeded
  case definitions, and compact fixture/evidence artifacts.
- May require EDT/meta snapshots for fixture authoring and validation, and may
  require live 1C runtime plus Vanessa or direct Python-manager probing during
  implementation verification.
- Does not promote click/input/write/action behavior and does not commit full
  infobases, generated EDT workspaces, raw captures or raw fixture output.
- Depends on `document-edt-meta-semantic-sources` and
  `link-protocol-corpus-semantic-mapping`.
