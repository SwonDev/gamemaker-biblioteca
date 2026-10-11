#!/usr/bin/env bash
# Instala instrucciones GameMaker sin cambiar modelos ni configuración de proveedores.
set -euo pipefail

ayuda() {
  cat <<'FIN'
Uso: ./instalar.sh [--comprobar] [--enlace] [--indices] [--destino <carpeta>]
  --comprobar  valida el paquete, sin instalación ni registro global.
  --enlace     enlaza el paquete en vez de copiarlo.
  --indices    deriva índices del runtime antes de instalar; un fallo aborta.
  --destino    instala solo en esa carpeta, sin registrar rutas globales.
FIN
}
comprobar=0
enlace=0
indices=0
base_elegida=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --comprobar) comprobar=1 ;;
    --enlace) enlace=1 ;;
    --indices) indices=1 ;;
    --destino)
      [ "$#" -ge 2 ] && [ -n "$2" ] && [[ "$2" != --* ]] || { ayuda; exit 2; }
      base_elegida="$2"; shift ;;
    --help|-h) ayuda; exit 0 ;;
    *) echo "✗ Opción desconocida: $1"; ayuda; exit 2 ;;
  esac
  shift
done

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
ORIGEN="$RAIZ/_indice/skills/gamemaker-biblioteca"
PY=""
for candidato in python3 python; do
  if command -v "$candidato" >/dev/null 2>&1 &&
     "$candidato" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
    PY="$candidato"; break
  fi
done
[ -n "$PY" ] || { echo "✗ Falta Python 3.10 o posterior."; exit 1; }
"$PY" "$RAIZ/_indice/sincronizar-skill.py" || {
  echo "✗ Paquete no válido. No se ha instalado ni registrado nada."; exit 1;
}
if [ "$comprobar" -eq 1 ]; then
  echo "✓ Paquete validado; sin instalación ni registro global."
  exit 0
fi
if [ "$indices" -eq 1 ]; then
  "$PY" "$RAIZ/_indice/construir-indices.py" || {
    echo "✗ Índices no generados. Se conservan las instalaciones anteriores."; exit 1;
  }
fi

instalar_en() {
  local base="$1" destino temporal copia_previa=""
  destino="$base/gamemaker-biblioteca"
  # No mover el propio paquete si el destino ya resuelve al origen.
  if [ "$("$PY" -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$destino")" = "$ORIGEN" ]; then
    echo "✓ Paquete canónico ya accesible desde $destino"
    return
  fi
  if "$PY" - "$ORIGEN" "$destino" <<'PY'
from pathlib import Path
import sys
origen,destino=map(lambda p:Path(p).resolve(),sys.argv[1:])
sys.exit(0 if origen in destino.parents else 1)
PY
  then
    echo "✗ El destino está dentro del paquete canónico."; return 2
  fi
  mkdir -p "$base"
  temporal="$(mktemp -d "$base/.gm-skill.XXXXXX")"
  if [ "$enlace" -eq 1 ]; then
    ln -s "$ORIGEN" "$temporal/gamemaker-biblioteca"
  else
    cp -R "$ORIGEN" "$temporal/gamemaker-biblioteca"
    "$PY" - "$ORIGEN" "$temporal/gamemaker-biblioteca" <<'PY'
from pathlib import Path
import sys
a,b=map(Path,sys.argv[1:])
for p in a.rglob("*"):
    if p.is_file() and p.read_bytes() != (b/p.relative_to(a)).read_bytes():
        raise SystemExit("✗ Copia incompleta; se conserva el destino anterior.")
PY
  fi
  if [ -e "$destino" ] || [ -L "$destino" ]; then
    mkdir -p "$base/.gamemaker-biblioteca-backups"
    copia_previa="$(mktemp -d "$base/.gamemaker-biblioteca-backups/copia.XXXXXX")/gamemaker-biblioteca"
    mv "$destino" "$copia_previa"
  fi
  if ! mv "$temporal/gamemaker-biblioteca" "$destino"; then
    [ -z "$copia_previa" ] || mv "$copia_previa" "$destino"
    echo "✗ No se pudo instalar; el destino anterior se ha restaurado."; exit 1
  fi
  rmdir "$temporal"
  echo "✓ Skill instalada: $destino"
  [ -z "$copia_previa" ] || echo "  Copia anterior conservada: $copia_previa"
}

if [ -n "$base_elegida" ]; then
  # Destino canónico solicitado como instalación es una equivocación; no alterarlo.
  if [ "$("$PY" -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$base_elegida/gamemaker-biblioteca")" = "$ORIGEN" ]; then
    echo "✗ El destino es el propio paquete canónico."; exit 2
  fi
  instalar_en "$base_elegida"
  echo "Establece GM_BIBLIOTECA con la ubicación de esta biblioteca para ese agente."
else
  DESTINOS=(
    "claude|$HOME/.claude/skills"
    "codex|$HOME/.codex/skills"
    "|$HOME/.agents/skills"
    "opencode|$HOME/.config/opencode/skills"
    "qwen|$HOME/.qwen/skills"
    "kimi|$HOME/.kimi-code/skills"
    "gemini|$HOME/.gemini/skills"
    "copilot|$HOME/.copilot/skills"
    "cursor-agent|$HOME/.cursor/skills"
    "cline|$HOME/.cline/skills"
  )
  for entrada in "${DESTINOS[@]}"; do
    IFS='|' read -r comando base <<< "$entrada"
    if [ -z "$comando" ] || command -v "$comando" >/dev/null 2>&1; then
      instalar_en "$base"
    fi
  done
  mkdir -p "$HOME/.config/gamemaker-biblioteca"
  printf '%s' "$RAIZ" > "$HOME/.config/gamemaker-biblioteca/ruta"
  echo "✓ Ruta local registrada."
fi
if [ "$indices" -eq 0 ]; then
  echo "Skill instalada; no se han regenerado los índices de GML."
  echo "Con GameMaker instalado: $PY _indice/construir-indices.py"
else
  echo "Skill instalada e índices derivados del runtime."
fi
echo "Reabre tu agente y pide usar gamemaker-biblioteca. Guía: INSTALACION.md"
