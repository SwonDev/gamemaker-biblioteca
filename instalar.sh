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
#
# ── Qué CLI soporta esto y cómo ────────────────────────────────────────────────
# Investigado en vivo contra documentación oficial el 07-09-2026 (no contra memoria del
# modelo). Casi todos convergen hoy en el mismo formato que usa Claude Code: una carpeta
# con `SKILL.md` (frontmatter YAML `name`+`description`) que el CLI descubre solo y activa
# cuando la tarea encaja — así que instalar de más no molesta, el CLI decide cuándo usarla.
#
#   Claude Code            ~/.claude/skills/                       code.claude.com/docs/en/skills
#   Codex (OpenAI)          ~/.codex/skills/       (funciona, "legacy" según un mantenedor)
#                            ~/.agents/skills/      (ruta CANÓNICA documentada hoy)
#                                                                    developers.openai.com/codex/skills
#   opencode                 ~/.config/opencode/skills/ (además lee ~/.claude/skills y
#                             ~/.agents/skills directamente, sin copiarlos)  opencode.ai/docs/skills
#   Qwen Code (Alibaba)       ~/.qwen/skills/                       github.com/QwenLM/qwen-code
#                                                                     /docs/users/features/skills.md
#   Kimi Code CLI (Moonshot)  ~/.kimi-code/skills/ (+ ~/.agents/skills)
#                                                          moonshotai.github.io/kimi-code/…/skills.html
#   Gemini CLI (Google)       ~/.gemini/skills/ (alias ~/.agents/skills)
#                                                          github.com/google-gemini/gemini-cli/…/skills.md
#   GitHub Copilot CLI        ~/.copilot/skills/ (alias ~/.agents/skills)
#                                                          docs.github.com/…/copilot-cli/…/add-skills
#   Cursor CLI (cursor-agent) ~/.cursor/skills/ (alias ~/.agents/skills; también lee
#                              ~/.claude/skills y ~/.codex/skills)          cursor.com/docs/skills
#   Cline (CLI oficial)       ~/.cline/skills/                             docs.cline.bot/…/skills
#
# Los cinco marcados "alias ~/.agents/skills" comparten un directorio genérico: es el
# estándar abierto Agent Skills (agentskills.io, origen Anthropic). Una sola copia ahí
# sirve para varios CLI a la vez, incluso los que aún no estén instalados.
#
# Quedan fuera, investigados y sin soporte de skills que se pueda instalar:
#   - GLM / Zhipu (Z.ai): NO tiene CLI de terminal propio y dedicado. Su «GLM Coding Plan»
#     se usa DENTRO de Claude Code, Codex, Cline u opencode (cambiando el endpoint de la
#     API a la suya) — esos ya quedan cubiertos arriba, con independencia de qué modelo
#     tengan detrás. Su producto propio, ZCode, es una app de escritorio Electron con
#     terminal embebida, no un binario de terminal: fuera del alcance de este script.
#   - Aider: sin directorio de skills propio (solo un paquete de terceros no oficial) y sin
#     lectura de AGENTS.md confirmada en su documentación oficial. Si está instalado, este
#     script no le toca ningún archivo: solo señala el AGENTS.md ya generado para que lo
#     referencie a mano (ver el paso 4 más abajo).
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORIGEN="$RAIZ/_indice/skills/gamemaker-biblioteca"
AGENTS_GENERADO="$ORIGEN/AGENTS.md"
MODO="${1:-}"

[ -f "$ORIGEN/SKILL.md" ] || { echo "✗ No encuentro la skill en $ORIGEN"; exit 1; }

# --- 1. Registrar la ruta de la biblioteca ------------------------------------
mkdir -p ~/.config/gamemaker-biblioteca
printf '%s' "$RAIZ" > ~/.config/gamemaker-biblioteca/ruta
echo "✓ Ruta registrada: $RAIZ"

# --- 2. Regenerar el AGENTS.md derivado, antes de copiar la skill -------------
# Si alguien tocó SKILL.md y no corrió `actualizar.py`, la copia de abajo debe llevar el
# AGENTS.md al día — no el de la última vez que se generó. sincronizar-skill.py es rápido
# (no toca GmlSpec.xml ni el runtime): no hace falta esperar al paso 5 para esto.
if command -v python3 >/dev/null 2>&1; then
  python3 "$RAIZ/_indice/sincronizar-skill.py" >/dev/null || true
fi

# --- 3. Instalar la skill (formato SKILL.md) en cada CLI que la soporte -------
# Cada entrada: «nombre visible|comando que confirma que el CLI está instalado|destino».
# Un comando vacío significa «instala siempre»: el directorio genérico ~/.agents/skills lo
# leen varios CLI a la vez y no cuesta nada tenerlo listo antes de instalar cualquiera de
# ellos.
DESTINOS=(
  "Claude Code|claude|$HOME/.claude/skills"
  "Codex (ruta activa; funciona, aunque OpenAI la describe como 'legacy')|codex|$HOME/.codex/skills"
  "Genérico ~/.agents — estándar Agent Skills: ruta canónica de Codex y también la que leen Copilot CLI, Gemini CLI, Cursor CLI y Kimi Code||$HOME/.agents/skills"
  "opencode|opencode|$HOME/.config/opencode/skills"
  "Qwen Code|qwen|$HOME/.qwen/skills"
  "Kimi Code CLI|kimi|$HOME/.kimi-code/skills"
  "Gemini CLI|gemini|$HOME/.gemini/skills"
  "GitHub Copilot CLI|copilot|$HOME/.copilot/skills"
  "Cursor CLI|cursor-agent|$HOME/.cursor/skills"
  "Cline|cline|$HOME/.cline/skills"
)

instalados=0
saltados=()
for entrada in "${DESTINOS[@]}"; do
  IFS='|' read -r nombre comando base <<< "$entrada"
  if [ -n "$comando" ] && ! command -v "$comando" >/dev/null 2>&1; then
    saltados+=("$nombre (no encuentro «${comando}» en el PATH)")
    continue
  fi
  mkdir -p "$base"
  destino="$base/gamemaker-biblioteca"
  rm -rf "$destino"
  if [ "$MODO" = "--enlace" ]; then
    ln -s "$ORIGEN" "$destino"
    echo "✓ $nombre: enlazada en $destino"
  else
    cp -R "$ORIGEN" "$destino"
    echo "✓ $nombre: instalada en $destino"
  fi
  instalados=$((instalados + 1))
done

[ "$instalados" -gt 0 ] || echo "⚠ No se detectó ningún CLI compatible con skills en formato SKILL.md."

# --- Aviso específico de Qwen Code ------------------------------------------
# Qwen declara sus carpetas de skills en settings.json. Si solo tiene ~/.claude/skills,
# la skill le llega de rebote: funciona hoy, pero dejaría de funcionar si se desinstala
# Claude Code. No tocamos la configuración del usuario; le damos el comando.
if command -v qwen >/dev/null 2>&1 && [ -f "$HOME/.qwen/settings.json" ]; then
  if ! grep -q '"~/.qwen/skills"' "$HOME/.qwen/settings.json" 2>/dev/null; then
    echo
    echo "⚠ Qwen Code no declara ~/.qwen/skills en su settings.json."
    echo "  La skill le funciona solo porque también lee ~/.claude/skills."
    echo "  Para que sea independiente, añade \"~/.qwen/skills\" a la lista \"skills\" de:"
    echo "  $HOME/.qwen/settings.json"
  fi
fi

if [ "${#saltados[@]}" -gt 0 ]; then
  echo
  echo "CLI no detectados en esta máquina (se han saltado, sin tocar nada suyo):"
  for s in "${saltados[@]}"; do echo "  · $s"; done
fi

# --- 4. CLI que no tienen directorio de skills: AGENTS.md a mano --------------
# Aider no tiene, a día de hoy, ni un directorio de skills en formato SKILL.md ni lectura
# confirmada de AGENTS.md en su documentación oficial (aider.chat) — investigado en vivo,
# no supuesto. Si está instalado, no le tocamos ningún archivo global suyo: solo le
# señalamos el AGENTS.md ya generado desde la skill, listo para que lo referencie él mismo.
if command -v aider >/dev/null 2>&1; then
  echo
  echo "⚠ Aider está instalado. No tiene un directorio de skills (SKILL.md) ni confirma"
  echo "  leer AGENTS.md por defecto, así que no se instala nada ahí automáticamente."
  echo "  Para usarlo en un proyecto de GameMaker, añade a su .aider.conf.yml de ese"
  echo "  proyecto (no se toca por ti — hazlo tú, es de Aider, no de esta biblioteca):"
  echo "    read: [\"$AGENTS_GENERADO\"]"
fi
echo
echo "Cualquier otro CLI que solo entienda AGENTS.md en la raíz de un proyecto (y no un"
echo "directorio de skills) puede usar el mismo archivo generado:"
echo "  $AGENTS_GENERADO"
echo "Cópialo o enlázalo como AGENTS.md en la raíz de tu proyecto de GameMaker."

# --- 5. Derivar los símbolos del runtime instalado ----------------------------
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

Cada CLI decide solo cuándo usar la skill al hablar de GameMaker, GML o .yyp — no hace
falta invocarla a mano.
FIN
