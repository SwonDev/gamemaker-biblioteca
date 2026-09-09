#!/usr/bin/env bash
# validar-compilacion.sh — compila DE VERDAD los scripts reutilizables de la biblioteca.
#
# El validador de símbolos (validar-codigo-gml.py) comprueba que las funciones existen;
# esto va un paso más allá: crea un proyecto GameMaker real, mete los scr_*.gml y los
# COMPILA con gm-cli contra el runtime instalado. Es la prueba definitiva de que el código
# reutilizable de la biblioteca no solo usa funciones reales, sino que compila.
#
#   bash _indice/validar-compilacion.sh
#
# Sale con 0 solo si la compilación termina sin errores de GML.
#
# El proyecto de prueba se crea en ~/gm_prueba_scripts (gm-cli init no admite ruta de
# destino: crea en el directorio de trabajo actual) y se borra siempre al terminar,
# incluso si el script falla a medias.
set -u

if ! command -v gm-cli >/dev/null 2>&1; then
  echo "✗ No encuentro el comando «gm-cli» en el PATH."
  echo "  Este script compila de verdad contra GameMaker: instala gm-cli"
  echo "  (npm i -g @gamemaker/gm-cli, o el instalador oficial) y vuelve a intentarlo."
  exit 2
fi

BIB="$(cd "$(dirname "$0")/.." && pwd)/06 - Assets y Scripts"
PROY="$HOME/gm_prueba_scripts"
YYP="$PROY/gm_prueba_scripts.yyp"

# Cerrojo: dos ejecuciones a la vez sobre la misma carpeta se pisan y
# producen errores que no existen. Ver `_indice/cerrojo.sh`.
. "$(cd "$(dirname "$0")" && pwd)/cerrojo.sh"
cerrojo_tomar "$PROY" || exit 2

limpiar() { rm -rf "$PROY"; cerrojo_soltar "$PROY"; }
trap limpiar EXIT

rm -rf "$PROY"   # por si quedó de una ejecución anterior interrumpida

echo "Creando proyecto de prueba en ${PROY}..."
( cd "$HOME" && gm-cli init --no-interactive --name "gm_prueba_scripts" --template "blank" \
    --no-ai --no-actions --toolchain "GMS2@2026.0.0.23" >/dev/null 2>&1 )
[ -f "$YYP" ] || { echo "✗ no se pudo crear el proyecto"; exit 2; }

echo "Creando stubs de assets…"
for obj in obj_bullet obj_camera obj_game obj_menu obj_player obj_torre obj_wall obj_x_prev obj_y_prev; do
    gm-cli resourcetool eval "resource create type=object name=$obj" "$YYP" >/dev/null 2>&1
done
for spr in spr_player_idle spr_player_run; do
    gm-cli resourcetool eval "resource create type=sprite name=$spr" "$YYP" >/dev/null 2>&1
done

echo "Añadiendo y compilando los scripts de la biblioteca…"
# Se recorre la carpeta, NO una lista escrita a mano: un script nuevo que nadie
# añadiera a la lista se quedaría fuera y la prueba seguiría saliendo en verde.
N=0
for ruta in "$BIB"/scr_*.gml; do
    [ -f "$ruta" ] || { echo "✗ no hay ni un scr_*.gml en «$BIB»"; exit 2; }
    scr="$(basename "$ruta" .gml)"
    gm-cli resourcetool eval "resource create type=script name=$scr" "$YYP" >/dev/null 2>&1
    if ! cp "$ruta" "$PROY/scripts/$scr/$scr.gml" 2>/dev/null; then
        # Sin esto, un `resource create` fallido dejaba el script FUERA del
        # proyecto y la compilación salía en verde sin haberlo compilado.
        echo "✗ no se pudo copiar $scr: el recurso no se creó en el proyecto"
        exit 2
    fi
    N=$((N + 1))
done
echo "  ($N scripts)"

SALIDA="$(cd "$PROY" && gm-cli compile 2>&1)"
ERRS="$(echo "$SALIDA" | grep -icE "compile error|syntax error|Error : |expecting|malformed")"

if echo "$SALIDA" | grep -q "Compilation finished" && [ "$ERRS" -eq 0 ]; then
    echo "✓ Los $N scripts reutilizables compilan sin errores contra el runtime 2026.0.0.23."
    exit 0
else
    echo "✗ La compilación falló:"
    echo "$SALIDA" | grep -iE "error|expecting|does not" | head
    exit 1
fi
