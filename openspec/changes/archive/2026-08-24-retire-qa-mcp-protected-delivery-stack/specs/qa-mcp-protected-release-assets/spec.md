## REMOVED Requirements

### Requirement: Release manifest declares protected baked protocol assets
**Reason**: Curated protocol assets are shipped openly as normal package data.
**Migration**: Record plaintext asset paths, hashes and provenance in the public
release manifest.

### Requirement: Protected image verification remains the release gate
**Reason**: Protection is retired for every product deployment.
**Migration**: Gate release on clean source builds, imports, tool contracts,
asset parsing and artifact integrity.

### Requirement: Protected image archives are scanned at the saved-layer level
**Reason**: Readable source and plaintext curated assets in layers are now
required rather than rejected.
**Migration**: Scan saved images for credentials, private inputs, unexpected
binaries and manifest/digest integrity instead of source confidentiality.

### Requirement: Self-hosted publish gates on the archive scanner
**Reason**: The private self-hosted protected release path is retired.
**Migration**: The public GitHub/GHCR workflow performs normal image and supply
chain verification before publication.
