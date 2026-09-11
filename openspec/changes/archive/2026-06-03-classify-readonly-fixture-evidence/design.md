## Context

The capture/probe change can produce several evidence outcomes: complete wire
rows, probe-only rows, incomplete hashes, timeouts, unsupported families or
runner/provider gaps. The lab needs a separate classification step so evidence
review remains explicit and repeatable.

## Goals / Non-Goals

Goals:

- Compare one or more fixture corpus runs and attach compact probe evidence.
- Classify each planned fixture case with a reviewable reason.
- Generate accepted-mapping evidence only for rows with stable wire evidence
  and replay/probe support.
- Preserve unresolved cases with enough detail for the next protocol pass.

Non-goals:

- Do not run new live capture unless needed to obtain a second repeated input.
- Do not alter raw captures.
- Do not update public docs or accepted mapping summaries beyond compact
  classification evidence; publication is the next ordered change.

## Classification Rules

- `accepted`: repeated rows have a non-null stable normalized hash and accepted
  replay or direct-probe evidence for the same read-only operation.
- `partial`: response data or probe output exists, but request-frame evidence,
  hash stability or marker join is incomplete.
- `pending`: the family is planned but no live evidence was produced.
- `unsupported`: the runner or current fixture surface cannot exercise the
  family in a read-only way.
- `timeout`: the live run timed out before a reviewable result.
- `rejected`: replay/probe evidence contradicts expected markers or operation.
- `blocked`: source or provider gap prevents evidence collection.

## Evidence Strategy

Use reviewed corpus directories or `corpus_cases.jsonl` files as inputs. When
two fixture runs exist, compare them directly. When only one run exists,
produce a classification summary that keeps rows non-accepted unless probe
evidence and project policy justify a provisional status. Accepted output must
remain compact and link source evidence paths rather than embedding raw
payloads.

## Safety Constraints

Classification is offline over reviewed compact evidence unless a second live
run is explicitly needed. If a second run is required, the capture/probe safety
rules from `run-readonly-fixture-capture-probes` apply unchanged.
