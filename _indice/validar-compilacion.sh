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
BIB="$(cd "$(dirname "$0")/.." && pwd)/06 - Assets y Scripts"
PROY="$HOME/gm_prueba_scripts"
YYP="$PROY/gm_prueba_scripts.yyp"

limpiar() { rm -rf "$PROY"; }
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
for scr in scr_audio scr_camera scr_debug scr_grid_pathfinding scr_input_buffer scr_math_util \
           scr_pool scr_save_load scr_state_machine scr_tiempo scr_tween; do
    gm-cli resourcetool eval "resource create type=script name=$scr" "$YYP" >/dev/null 2>&1
    cp "$BIB/$scr.gml" "$PROY/scripts/$scr/$scr.gml" 2>/dev/null
done

SALIDA="$(cd "$PROY" && gm-cli compile 2>&1)"
ERRS="$(echo "$SALIDA" | grep -icE "compile error|syntax error|Error : |expecting|malformed")"

if echo "$SALIDA" | grep -q "Compilation finished" && [ "$ERRS" -eq 0 ]; then
    echo "✓ Los 11 scripts reutilizables compilan sin errores contra el runtime 2026.0.0.23."
    exit 0
else
    echo "✗ La compilación falló:"
    echo "$SALIDA" | grep -iE "error|expecting|does not" | head
    exit 1
fi
