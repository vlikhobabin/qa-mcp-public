## Context

The current expanded read-only corpus matrix emits explicit unsupported rows
for `Button`, `Table`, `CommandBar`, `Page`, `Label` and `CheckBox` because
the active demo form does not expose those families safely. The protocol lab
also has accepted read-only active-window and active-form mappings, but action
or write semantics remain out of scope until read-only classification and
recovery behavior are better understood.

This change plans the controlled fixture surface needed to cover those
families. The plan may use EDT/meta tooling to design or validate a fixture
form, but the resulting protocol claims still require capture plus replay or
direct Python-manager proof.

## Goals / Non-Goals

**Goals:**

- Create a fixture coverage plan for the missing read-only element families.
- Define case ids, expected state, expected response markers, safety class and
  evidence paths for each family.
- Specify how optional EDT workspace authoring and validation stay outside
  git while curated summaries are retained.
- Feed planned fixture surfaces into the corpus runner through explicit case
  manifests or seeded matrix updates.
- Require retained evidence for capture, normalization and replay/probe
  confirmation before any new family is accepted.

**Non-Goals:**

- Do not click buttons, execute commands, input text or mutate business data.
- Do not promote write/action protocol semantics.
- Do not commit full infobases, EDT workspaces, generated fixture exports, raw
  capture streams or full provider logs.
- Do not make EDT/meta providers mandatory for raw capture/replay.

## Decisions

- Plan each family as a row with status. A family can be `planned`,
  `covered`, `blocked` or `out_of_scope`, with concrete evidence paths or
  residual risk. Alternative: one generic fixture task. That would be too easy
  to mark done while leaving families uncovered.
- Use explicit corpus case ids and expected response markers before capture.
  This makes future evidence review deterministic and avoids inferring case
  identity from metadata after the fact. Alternative: capture broadly and label
  later. That would repeat the current gap.
- Keep fixture authoring optional and externally bounded. EDT/meta services may
  help author or validate form shape, but the capture runner and Python manager
  must not depend on those providers to execute read-only wire probes.
- Route provider gaps by owner. EDT validation gaps go to `/opt/edt-lab`,
  metadata graph gaps to `/opt/finshtab-1c`, Vanessa UI/capture gaps to
  `/opt/vanessa-mcp-stack`, and project fixture data gaps to `project:qa-mcp`.

## Risks / Trade-offs

- Read-only-looking UI properties can still require opening forms or navigating
  state. Mitigation: keep only non-mutating form-open/navigation assumptions in
  scope and route action semantics to the later safe-action card.
- Fixture authoring can become an implementation project by itself. Mitigation:
  permit `blocked` or `out_of_scope` family rows when the provider or fixture
  shape is unavailable, but require a concrete reason.
- New fixture captures may diverge from current accepted hashes. Mitigation:
  write new compact evidence under a new run id and do not rewrite historical
  accepted mappings.

## Migration Plan

Implementation should first add the plan and any static manifest/schema
updates, then run Windows-native checks. Live capture or EDT validation can be
done during delivery if the operator environment is ready; otherwise the plan
must record provider gaps and residual risk. No existing evidence needs to be
rewritten.

## Open Questions

- Which exact external EDT workspace or exported demo configuration will be
  used for fixture authoring may remain unresolved until the source inventory
  is completed.
