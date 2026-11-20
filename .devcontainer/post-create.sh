#!/usr/bin/env bash
set -euo pipefail

export ELAN_HOME="${HOME}/.elan"
export PATH="${ELAN_HOME}/bin:${PATH}"
workspace_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -x "${ELAN_HOME}/bin/elan" ]]; then
    installer="$(mktemp)"
    trap 'rm -f "${installer}"' EXIT
    curl --proto '=https' --tlsv1.2 -fsSL \
        https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
        -o "${installer}"
    sh "${installer}" -y --no-modify-path --default-toolchain none
fi

find "${workspace_root}" -type f -name lean-toolchain \
    -not -path '*/.git/*' \
    -not -path '*/.lake/*' \
    -exec awk 'NF { print $1; exit }' {} \; \
    | sort -u \
    | while IFS= read -r toolchain; do
        [[ -n "${toolchain}" ]] || continue
        echo "Installing Lean toolchain ${toolchain} (cached in ${ELAN_HOME})"
        elan toolchain install "${toolchain}"
    done

requirements="${workspace_root}/mahjong-wait-classification/scripts/remote-compute-requirements.txt"
if [[ -f "${requirements}" ]]; then
    python3 -m venv "${HOME}/.venv"
    "${HOME}/.venv/bin/python" -m pip install -r "${requirements}"
fi

elan --version
