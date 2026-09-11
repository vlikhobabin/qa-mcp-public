## REMOVED Requirements

### Requirement: The thin delivery image ships the protocol engine compiled to native code
**Reason**: The protocol engine becomes fully readable open-source code in all
deployments.
**Migration**: Ship and test the normal `qa_mcp/protocol/*.py` modules.

### Requirement: Bundled protocol data ships encrypted at rest and decrypts at runtime
**Reason**: Curated protocol assets become open plaintext package data and no
runtime data key remains.
**Migration**: Load reviewed JSON/JSONL assets directly and verify their hashes,
provenance and parsability.

### Requirement: The released GHCR image is the protected build
**Reason**: GHCR will publish the source-visible standalone image.
**Migration**: Build the public image from the tagged open-source revision and
record its digest in the public release manifest.
