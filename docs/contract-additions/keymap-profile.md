# KeymapProfile contract addition

`KeymapProfile` is the typed mapping profile for keyboard-first interaction in SourceOS and SociOS.

It records:
- platform and modifier strategy
- GUI profile
- terminal profile
- launcher and overlay references
- remap-engine reference
- protected namespaces

Placement rule:
- canonical schema lives in `sourceos-spec`
- Linux-side implementations bind to it downstream
- donor/remap repositories may inform values but do not own the contract
