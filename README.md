# Mahjong workspace

This repository contains workspace configuration and shared documentation.
The Lean source projects remain independent repositories:

- `mahjong-domain-core`
- `mahjong-hand-hash`
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

The shared [Lean module policy](docs/lean-module-policy.md) describes the
module system, incremental migration, and import analysis across the projects.
The [Dev Container Git authentication notes](docs/git-authentication-devcontainer.md)
describe credential sharing and the observed local configuration.
The [hand perfect-hash plan](docs/hand-perfect-hash-plan.md) specifies
reversible keys for tile collections and hands with fixed melds.
The [HandSnapshot review](docs/hand-snapshot-review-2026-11-26.md) assesses
the shared hand model and its boundaries for decision-record databases.
The [CI metrics dashboard](https://bgnori.github.io/mahjong-workspace/dashboard/)
reads the public `/ci/` data published by each source repository.
