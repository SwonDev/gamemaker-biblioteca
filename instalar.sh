#!/usr/bin/env bash
# Entrada compatible: toda la instalación vive en instalar.py.
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
for candidato in python3 python; do
  if command -v "$candidato" >/dev/null 2>&1 &&
     "$candidato" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
    exec "$candidato" "$RAIZ/instalar.py" "$@"
  fi
done
if command -v py >/dev/null 2>&1 &&
   py -3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
  exec py -3 "$RAIZ/instalar.py" "$@"
fi
printf '%s\n' 'Falta Python 3.10 o posterior. Instálalo desde https://www.python.org/downloads/.' >&2
exit 1
