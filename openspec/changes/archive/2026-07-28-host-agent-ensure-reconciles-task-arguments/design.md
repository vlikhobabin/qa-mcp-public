## Context

`host-agent/install-windows-host-agent.ps1` is both the installer and the
operator-facing ensure surface for Windows host-agent deployments. Today it
rewrites task state and stops the owned task/process whenever the task exists.
That makes the installer non-idempotent and still does not explicitly prove
that the already running process uses the same BSL profile as the desired task
action.

The root solo activation flow can detect effective BSL argument mismatch, but
the owning remediation belongs in qa-mcp because the scheduled task and Windows
process lifecycle are host-agent installer responsibilities.

## Goals / Non-Goals

**Goals:**

- Build one desired state model after all installer defaults are resolved.
- Compare existing task action, running owned process command line and staged
  artifact hashes to that desired state.
- Restart the task only when drift is detected or the task is absent/not
  running.
- Keep output secret-safe by hashing file contents and comparing command-line
  arguments that contain file paths rather than token values.
- Preserve existing fail-closed validation for BSL, registry, onboarding,
  firewall and artifact inputs.

**Non-Goals:**

- Do not add a separate `ensure-host-agent.ps1` entrypoint.
- Do not inspect token file contents beyond existing token-file write/read
  behavior.
- Do not implement a live Windows Task Scheduler test in the Linux delivery
  gate; the component test covers the script contract and the final Windows
  contour remains the runtime proof.

## Decisions

1. **Use a secret-safe profile fingerprint rather than raw log comparison.**

   The installer computes a SHA-256 digest over normalized executable path,
   scheduled-task arguments, copied artifact hashes and task identity fields.
   This keeps restart decisions stable while allowing logs to print only reason
   labels and digest prefixes.

2. **Compare running command line after rendering desired task arguments.**

   The scheduled task can be correct while the running process is stale. The
   installer queries the owned `qa-mcp-host-agent.exe` process at the installed
   target path and compares its command line to the desired action string. A
   mismatch restarts the scheduled task.

3. **Separate file replacement from process restart.**

   Local files may be rewritten for ACL or content freshness. Process restart is
   controlled by artifact hash drift, task action drift, running-process drift,
   missing task or missing running process. This makes identical reruns no-op
   for the task while still repairing local file state.

4. **Clean only owned child state when restarting.**

   A restart first stops the scheduled task and the installed host-agent process
   at `$TargetExe`, then stops only `bsl-agent.exe` at `$TargetBslAgent`. It does
   not name-wide kill BSL helpers.

## Risks / Trade-offs

- **PowerShell command-line normalization can differ from Task Scheduler text.**
  Mitigation: compare the exact rendered `$ActionArgs -join " "` string against
  the existing task action and process command line suffix after executable
  normalization, and keep tests pinned to those markers.
- **Linux cannot execute Task Scheduler/WMI semantics.** Mitigation: assert the
  installer contract text offline and record the runtime Windows proof as a
  required external contour, not as a claimed local pass.
- **Artifact copy timing can affect hash drift decisions.** Mitigation: capture
  pre-copy installed hashes for restart decisions, then copy and ACL-protect
  files before registering/starting the task.
