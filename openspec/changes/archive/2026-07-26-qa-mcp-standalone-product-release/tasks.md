## 1. Product staging

- [x] 1.1 Bind the staged release URL to the authenticated
  `/qa-mcp/download/versions/<version>/` product path.
- [x] 1.2 Retire component-side public-link/server activation before mutation.
- [x] 1.3 Preserve signed frozen component-manifest and sidecar generation.

## 2. Standalone guidance

- [x] 2.1 Add current solo-only human/agent guidance and reject team mode.
- [x] 2.2 Ensure staged bootstrap/guidance contains no active legacy release
  or license origin.
- [x] 2.3 Record the non-overlap dependency on
  `license-activation-bootstrap`.
- [x] 2.4 Select license product `qa-mcp` in the staged bootstrap and strip
  tracked shared license/decryption defaults without editing their source
  owner.
- [x] 2.5 Accept the 1C password, activation material, and bundled-data key
  only through caller-created ACL-protected files in the staged bootstrap.
- [x] 2.6 Vendor the source-pinned product-aware broker and require the
  protected image to select product `qa-mcp`.

## 3. Verification

- [x] 3.1 Add and run focused offline release-script/manifest tests.
- [x] 3.2 Run shell syntax, strict OpenSpec and diff checks.
- [x] 3.3 Parse and inspect the rendered PowerShell artifact with Windows
  PowerShell on the authorized architect workstation, then remove the exact
  owned temporary directory.
