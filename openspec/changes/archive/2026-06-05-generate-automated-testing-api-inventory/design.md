## Context

The roadmap expects the corpus pipeline to start from a finite API matrix. The
initial inventory should capture the automated-testing and client-agent object
surface with enough structure to plan manifests, fixture requirements and
safety classes.

## Goals / Non-Goals

**Goals:**

- Produce a machine-readable API inventory JSON.
- Record source platform version and help source metadata.
- Classify members into read-only, safe UI action, mutation, agent runtime or
  unsupported-initial where evidence supports it.
- Publish a compact Markdown summary with counts and unresolved gaps.

**Non-Goals:**

- No live TestClient capture.
- No protocol mapping acceptance.
- No full semantic parser for every platform help topic if the source cannot
  provide it in one pass.

## Decisions

1. Name the inventory by source platform version.
   Rationale: platform help and lab runtime versions can differ, and the
   evidence must remain reproducible.

2. Preserve unresolved topics as gap rows.
   Rationale: missing help coverage should not silently shrink the API matrix.

3. Keep safety classification conservative.
   Rationale: read-only cases are allowed first; action and mutation classes
   need separate fixture and recovery evidence.

## Verification Matrix

This is documentation/source-inventory work with platform-help provider
evidence. Detailed rows are in `tasks.md`.

## Risks / Trade-offs

- Help source version may differ from the lab platform
  `8.3.27.2130`. The inventory must record the actual source version and any
  mismatch.
- Some methods may require manual safety review after initial extraction.
