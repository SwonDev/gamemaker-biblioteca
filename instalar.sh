#!/usr/bin/env bash
# Instala la skill «gamemaker-biblioteca» para los CLI de IA que haya en esta máquina.
#
#   ./instalar.sh            instala (o reinstala) la skill
#   ./instalar.sh --enlace   igual, pero con enlaces simbólicos en vez de copias
#                            (para quien desarrolle la propia biblioteca)
#
# La skill necesita saber dónde vive la biblioteca. Eso se resuelve en este orden:
#   1. la variable de entorno $GM_BIBLIOTECA
#   2. el archivo ~/.config/gamemaker-biblioteca/ruta   ← lo escribe este script
# Así la skill funciona igual en cualquier máquina y con cualquier ruta.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORIGEN="$RAIZ/_indice/skills/gamemaker-biblioteca"
MODO="${1:-}"

[ -f "$ORIGEN/SKILL.md" ] || { echo "✗ No encuentro la skill en $ORIGEN"; exit 1; }

# --- 1. Registrar la ruta de la biblioteca ------------------------------------
mkdir -p ~/.config/gamemaker-biblioteca
printf '%s' "$RAIZ" > ~/.config/gamemaker-biblioteca/ruta
echo "✓ Ruta registrada: $RAIZ"

# --- 2. Instalar la skill en cada CLI presente --------------------------------
# ~/.agents/skills es el directorio común que leen Codex, Copilot CLI y Gemini CLI.
DESTINOS=(
  "$HOME/.claude/skills"      # Claude Code
  "$HOME/.codex/skills"       # Codex
  "$HOME/.agents/skills"      # Codex · Copilot CLI · Gemini CLI (alias común)
  "$HOME/.config/opencode/skills"
)

instalados=0
for base in "${DESTINOS[@]}"; do
  padre="$(dirname "$base")"
  # Solo instala donde el CLI está de verdad instalado, salvo el alias común.
  if [ ! -d "$padre" ] && [ "$base" != "$HOME/.agents/skills" ]; then continue; fi
  mkdir -p "$base"
  destino="$base/gamemaker-biblioteca"
  rm -rf "$destino"
  if [ "$MODO" = "--enlace" ]; then
    ln -s "$ORIGEN" "$destino"
    echo "✓ Enlazada en $destino"
  else
    cp -R "$ORIGEN" "$destino"
    echo "✓ Instalada en $destino"
  fi
  instalados=$((instalados + 1))
done

[ "$instalados" -gt 0 ] || echo "⚠ No se detectó ningún CLI compatible."

# --- 3. Derivar los símbolos del runtime instalado ----------------------------
# El índice de símbolos sale del GmlSpec.xml del GameMaker de ESTA máquina, así que
# se regenera aquí: es lo que hace que la skill no invente funciones.
if command -v python3 >/dev/null 2>&1; then
  echo
  echo "→ Regenerando los índices contra el runtime instalado…"
  python3 "$RAIZ/_indice/actualizar.py" || echo "⚠ Revisa la salida de actualizar.py"
else
  echo "⚠ Sin python3: no puedo regenerar los índices. Instálalo y ejecuta:"
  echo "  python3 \"$RAIZ/_indice/actualizar.py\""
fi

cat <<FIN

Listo. Comprueba que responde:

  python3 "$RAIZ/_indice/buscar.py" draw_sprite_ext

En Claude Code y Codex la skill se activa sola al hablar de GameMaker, GML o .yyp.
FIN
