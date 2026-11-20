# Mahjong workspace

This repository contains workspace and Dev Container configuration only. The
Lean source projects remain independent repositories:

- `mahjong-domain-core`
- `mahjong-shanten-calculation`
- `mahjong-wait-classification`

Clone those repositories as sibling directories under this workspace, then open
`mahjong.code-workspace` in VS Code. Their source directories are ignored by
this repository so their Git histories remain independent.

The workspace Dev Container persists the Lean toolchain in a Docker volume and
shares Mathlib's downloaded cache through the host's `~/.cache/mathlib`.
Mathlib cache data is reused on the same host; a new host downloads it once.
Individual projects also provide Dev Container configurations for standalone
development.
