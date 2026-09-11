## Context

The retained Linux proof contains an extension-bearing disposable 1CD and a
target-bound CFE, but the raw directory copied during S50-160 was captured from
a live Linux-created file infobase. Although one elevated Windows run briefly
opened its TPort, later runs exited before a usable lifecycle. S50 acceptance
therefore needs a reproducible platform-supported transfer boundary and a full
qa-mcp UI mutation/readback/recovery proof.

The protocol source remains the existing 8.3.27.2130 capture corpus. No new
frame semantics are claimed. Runtime-specific GUIDs, PIDs, ports, item name,
window handles and screenshot paths are dynamic evidence fields.

## Goals / Non-Goals

**Goals:**

- Produce a portable backup from the retained deployed Linux disposable
  infobase, create a fresh Windows file infobase, and restore that backup on
  Windows with platform 8.3.27.2130.
- Launch through the source-built host agent and obtain one usable owned
  TestClient lifecycle target.
- Create and read back one unique S50 catalog item through qa-mcp and retain
  ignored screenshots.
- Prove exact recovery and a clean rerun boundary.

**Non-Goals:**

- Copy or mutate a customer/protected infobase.
- Declare arbitrary raw 1CD directory copying supported.
- Install a persistent host-agent/service or leave reusable credentials on the
  station.
- Clean unrelated Docker resources, user files, 1C sessions, tasks or ports.

## Decisions

### The acceptance path is Windows create plus portable restore

Linux Designer exports a `.dt` from the retained deployed proof infobase.
Windows 1C creates the exact run-owned file infobase directory and restores that
portable backup before TestClient launch. This makes the platform own the
Windows database files and avoids relying on the state of a copied live 1CD.
The backup and restored base remain ignored disposable evidence.

The target user's ignored launcher configuration disables hardware-license
search and the station has no software-license file. Restore and TestClient
launch therefore use an explicit, caller-controlled `/UseHWLicenses+` opt-in;
the default qa-mcp launch contract remains unchanged.

### One lifecycle owns all UI operations

The first manager/UI action uses the lifecycle-bound endpoint returned by
`launch_test_client`; no generic TCP readiness probe consumes the socket.
Navigation opens `Справочник.S50ProofItems`, creates a unique run-labelled item,
reads it back from the visible catalog list/cells, and captures screenshots
before cleanup. If the protocol route fails, the implementation may use only
existing qa-mcp lifecycle-bound Windows display/input tools, not an unrelated
automation product.

The retained protocol template acknowledged the catalog link without changing
the visible window, so the accepted proof uses the same lifecycle target with
the native 1C `Shift+F11` link dialog and `Insert` create shortcut. The host
agent's bounded key map now includes `Insert`; save, form-visible value and final
list-visible code/name are all retained before stop and recovery.

### Cleanup is inventory-driven and exact

Before mutation, retain hostname plus exact stage/task/process/listener
inventory for the run namespace. Cleanup resolves and removes only the exact
stage directory, exact scheduled tasks, source-built host-agent process, owned
TestClient lifecycle, run-owned SSH tunnels and proof ports. A post-cleanup
inventory and a second clean preflight constitute recovery/rerun evidence.

## Risks / Trade-offs

- [Portable backup/restore rejects the source] → Retain Designer exit/log
  evidence and stop before TestClient launch; do not fall back to customer data.
- [A first protocol connection consumes or exits TestClient] → Retain the typed
  lifecycle/protocol result and fix only card-owned qa-mcp behavior before a
  fresh restored-base rerun.
- [Cleanup target cannot be proven run-owned] → Leave it untouched and record a
  blocker rather than broadening the cleanup selector.
- [Network/device access disappears] → Record the `.200` infrastructure blocker
  and do not use `.201` or another station.

## Migration Plan

This is a disposable proof, not a persistent migration. Create/export, stage,
restore, prove, inventory, remove exact resources, and rerun the clean preflight.
Tracked artifacts contain only contracts, code/tests and summarized evidence.

## Open Questions

None. The supported transfer choice is Windows create plus portable restore.
