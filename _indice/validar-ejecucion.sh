#!/usr/bin/env bash
# validar-ejecucion.sh — EJECUTA el código reutilizable de la biblioteca.
#
# `validar-codigo-gml.py` comprueba que las funciones existen.
# `validar-compilacion.sh` comprueba que el código compila.
# Esto va un paso más allá: crea un proyecto de GameMaker real, mete el script
# y los bancos de pruebas, y LO CORRE. Sale con 0 solo si todas las comprobaciones
# pasan dentro del juego.
#
#   bash _indice/validar-ejecucion.sh
#
# POR QUÉ HACE FALTA, con un caso real: `scr_nivel_mapa.gml` compilaba sin un
# solo aviso y tenía un fallo que ninguna de las otras dos herramientas podía
# ver — una variable de instancia se llamaba igual que una función global, así
# que leer su nombre devolvía la función en vez del valor. Apareció en la
# primera ejecución del banco. Compilar no es ejecutar.
#
# ⚠️ ABRE UNA VENTANA de juego durante uno o dos segundos: el banco termina con
# `game_end()`. No hay modo sin cabeza en `gm-cli run`.
set -u

if ! command -v gm-cli >/dev/null 2>&1; then
  echo "✗ No encuentro el comando «gm-cli» en el PATH."
  exit 2
fi

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
PROY="$HOME/gm_prueba_ejecucion"
YYP="$PROY/gm_prueba_ejecucion.yyp"

limpiar() { rm -rf "$PROY"; }
trap limpiar EXIT
rm -rf "$PROY"

echo "Creando proyecto de prueba en ${PROY}…"
crear_proyecto() {
    rm -rf "$PROY"
    ( cd "$HOME" && gm-cli init --no-interactive --name "gm_prueba_ejecucion" --template "blank" \
        --no-ai --no-actions --toolchain "GMS2@2026.0.0.23" 2>&1 )
}
INIT_SALIDA="$(crear_proyecto)"
if [ ! -f "$YYP" ]; then
    # `gm-cli init` baja la plantilla de api.gamemaker.io y ese servidor devuelve
    # 429 cuando se le pega mucho seguido. Un reintento resuelve casi siempre.
    echo "  el primer intento falló; reintentando en 20 s…"
    sleep 20
    INIT_SALIDA="$(crear_proyecto)"
fi
if [ ! -f "$YYP" ]; then
    echo "✗ no se pudo crear el proyecto. Lo que dijo gm-cli:"
    echo "$INIT_SALIDA" | tail -5
    exit 2
fi

echo "Montando el banco de pruebas…"
# obj_puerta, obj_caja, obj_placa, obj_llave, obj_jugador y obj_muro existen para
# que se puedan EJECUTAR las funciones de la receta 04 · 59 que los nombran. Sin
# ellos el código compila igual —GML no resuelve el objeto hasta ejecutarlo— y dos
# de las once funciones no se probarían nunca: pasarían por «verde» sin correr.
for obj in obj_solido obj_moneda obj_salida obj_bala obj_test \
           obj_puerta obj_caja obj_placa obj_llave obj_jugador obj_muro; do
    gm-cli resourcetool eval "resource create type=object name=$obj" "$YYP" >/dev/null 2>&1
done

# Scripts de la biblioteca que se ponen a prueba, y los bancos que los prueban.
# La pareja es <nombre del script en el proyecto>:<ruta del .gml de origen>.
PIEZAS=(
  "scr_nivel_mapa:$RAIZ/06 - Assets y Scripts/scr_nivel_mapa.gml"
  "scr_pool:$RAIZ/06 - Assets y Scripts/scr_pool.gml"
  "scr_debug:$RAIZ/06 - Assets y Scripts/scr_debug.gml"
  "scr_pruebas_ayuda:$RAIZ/_indice/pruebas/banco_ayuda.gml"
  "scr_banco_nivel_mapa:$RAIZ/_indice/pruebas/banco_nivel_mapa.gml"
  "scr_banco_desactivadas:$RAIZ/_indice/pruebas/banco_desactivadas.gml"
  "scr_banco_fuente:$RAIZ/_indice/pruebas/banco_fuente.gml"
  "scr_math_util:$RAIZ/06 - Assets y Scripts/scr_math_util.gml"
  "scr_state_machine:$RAIZ/06 - Assets y Scripts/scr_state_machine.gml"
  "scr_grid_pathfinding:$RAIZ/06 - Assets y Scripts/scr_grid_pathfinding.gml"
  "scr_tiempo:$RAIZ/06 - Assets y Scripts/scr_tiempo.gml"
  "scr_save_load:$RAIZ/06 - Assets y Scripts/scr_save_load.gml"
  "scr_ui_confirmar:$RAIZ/06 - Assets y Scripts/scr_ui_confirmar.gml"
  "scr_input_buffer:$RAIZ/06 - Assets y Scripts/scr_input_buffer.gml"
  "scr_tween:$RAIZ/06 - Assets y Scripts/scr_tween.gml"
  "scr_camera:$RAIZ/06 - Assets y Scripts/scr_camera.gml"
  "scr_audio:$RAIZ/06 - Assets y Scripts/scr_audio.gml"
  "scr_banco_scripts:$RAIZ/_indice/pruebas/banco_scripts.gml"
  "scr_banco_circuitos:$RAIZ/_indice/pruebas/banco_circuitos.gml"
)
for pieza in "${PIEZAS[@]}"; do
    nombre="${pieza%%:*}"
    origen="${pieza#*:}"
    gm-cli resourcetool eval "resource create type=script name=$nombre" "$YYP" >/dev/null 2>&1
    cp "$origen" "$PROY/scripts/$nombre/$nombre.gml" \
      || { echo "✗ no se pudo copiar $nombre (¿se creó el recurso?)"; exit 2; }
done

for ev in create:Create_0 step:Step_0; do
    tipo="${ev%%:*}"
    if [ "$tipo" = "create" ]; then
        gm-cli resourcetool eval "object event findorcreate name=obj_test type=create" "$YYP" >/dev/null 2>&1
    else
        gm-cli resourcetool eval "object event findorcreate name=obj_test type=step subtype=step_normal" "$YYP" >/dev/null 2>&1
    fi
done
cp "$RAIZ/_indice/pruebas/banco_create.gml" "$PROY/objects/obj_test/Create_0.gml" \
  || { echo "✗ no se pudo copiar el evento Create"; exit 2; }
cp "$RAIZ/_indice/pruebas/banco_step.gml" "$PROY/objects/obj_test/Step_0.gml" \
  || { echo "✗ no se pudo copiar el evento Step"; exit 2; }

# obj_solido lleva Create para poder medir si el quinto argumento de
# instance_create_layer() llega antes que el Create (r15 §2.5).
gm-cli resourcetool eval "object event findorcreate name=obj_solido type=create" "$YYP" >/dev/null 2>&1
cp "$RAIZ/_indice/pruebas/banco_solido_create.gml" "$PROY/objects/obj_solido/Create_0.gml" \
  || { echo "✗ no se pudo copiar el Create de obj_solido"; exit 2; }

# obj_puerta necesita su `canal` para que `circuitos_validar()` de la receta 59
# tenga algo que leer.
gm-cli resourcetool eval "object event findorcreate name=obj_puerta type=create" "$YYP" >/dev/null 2>&1
printf 'canal   = "puerta_norte";\nmodo    = "todos";\ncuantos = 1;\nabierta = false;\n' \
  > "$PROY/objects/obj_puerta/Create_0.gml"

# La hoja de glifos de la fuente de sprite (Trampa 12, tercera salida). Un PNG por
# carácter, importados EN LOTE: `resourcetool script` mete los 89 en poco más de un
# segundo; por `eval`, uno a uno, serían minutos.
GLIFOS="$PROY/_glifos"
if python3 "$RAIZ/_indice/pruebas/generar_glifos.py" "$GLIFOS" >/dev/null 2>&1; then
    gm-cli resourcetool eval "resource create type=sprite name=spr_glifos" "$YYP" >/dev/null 2>&1
    LOTE="$PROY/_lote_glifos.txt"
    : > "$LOTE"
    for g in "$GLIFOS"/g_*.png; do
        echo "sprite addframe name=spr_glifos path=$g" >> "$LOTE"
    done
    gm-cli resourcetool script "$LOTE" "$YYP" >/dev/null 2>&1
    # Leer de vuelta: «Saved successfully» no es verificación.
    N_PNG="$(ls "$GLIFOS"/g_*.png | wc -l | tr -d ' ')"
    N_YY="$(grep -o '"\$GMSpriteFrame"' "$PROY/sprites/spr_glifos/spr_glifos.yy" 2>/dev/null | wc -l | tr -d ' ')"
    if [ "$N_PNG" != "$N_YY" ]; then
        echo "✗ la hoja de glifos no se importó entera: $N_YY de $N_PNG fotogramas"
        exit 2
    fi
    echo "  (hoja de glifos: $N_YY fotogramas importados en lote)"
else
    echo "✗ no se pudo generar la hoja de glifos (¿falta Pillow?). El banco de fuente"
    echo "  NO se puede ejecutar, y eso no es lo mismo que que pase."
    exit 2
fi

# Un sprite de 16x16 para los objetos de rejilla. NO es decoración: un objeto sin
# sprite no tiene máscara de colisión, así que ni `place_meeting()` ni
# `instance_position()` lo encuentran — y un muro invisible que además no choca es
# un fallo silencioso perfecto.
python3 - "$PROY/_celda.png" <<'PYEOF'
import sys
try:
    from PIL import Image
    Image.new("RGBA", (16, 16), (120, 120, 140, 255)).save(sys.argv[1])
except ImportError:
    sys.exit(1)
PYEOF
if [ -f "$PROY/_celda.png" ]; then
    gm-cli resourcetool eval "resource create type=sprite name=spr_celda" "$YYP" >/dev/null 2>&1
    gm-cli resourcetool eval "sprite addframe name=spr_celda path=$PROY/_celda.png" "$YYP" >/dev/null 2>&1
    # No hay `OBJECT SET sprite=`: el sprite de un objeto se asigna con
    # `resource set expr=<objeto>.spriteId value=<sprite>`.
    for o in obj_muro obj_puerta obj_caja obj_placa obj_llave obj_jugador; do
        gm-cli resourcetool eval "resource set expr=$o.spriteId value=spr_celda" "$YYP" >/dev/null 2>&1
    done
    # Leer de vuelta: sin máscara, media receta no se probaría y saldría en verde.
    if ! grep -q "spr_celda" "$PROY/objects/obj_muro/obj_muro.yy"; then
        echo "✗ obj_muro se quedó sin sprite: sin máscara no hay colisión que probar"
        exit 2
    fi
fi

# El código de la receta 04 · 59 se EXTRAE del documento, no se copia: así lo que
# se ejecuta es lo que un lector va a copiar, y no una versión que se separó.
RECETA59="$RAIZ/04 - Recetas por género/59 - Puertas, llaves y placas de presión - el puzle de sala.md"
gm-cli resourcetool eval "resource create type=script name=scr_receta_59" "$YYP" >/dev/null 2>&1
if ! python3 "$RAIZ/_indice/pruebas/extraer_funciones.py" "$RECETA59" \
        "$PROY/scripts/scr_receta_59/scr_receta_59.gml"; then
    echo "✗ no se pudieron extraer las funciones de la receta 59"
    exit 2
fi

# Tres sonidos para el banco de audio: era el único script reutilizable que no
# se podía ejecutar, porque sus funciones reciben ids de sonido. El WAV lo
# fabrica Python con su biblioteca estándar — ni descargas ni licencias ajenas.
WAV="$PROY/_tono.wav"
if python3 "$RAIZ/_indice/pruebas/generar_sonido.py" "$WAV" >/dev/null 2>&1; then
    for snd in snd_prueba snd_prueba2 snd_prueba3; do
        gm-cli resourcetool eval "resource create type=sound name=$snd" "$YYP" >/dev/null 2>&1
        gm-cli resourcetool eval "sound setfile name=$snd path=$WAV" "$YYP" >/dev/null 2>&1
    done
    # Leer de vuelta: un sonido sin archivo compila y no suena.
    if ! ls "$PROY/sounds/snd_prueba/"*.wav >/dev/null 2>&1; then
        echo "✗ snd_prueba se creó sin archivo de audio: el banco de audio no probaría nada"
        exit 2
    fi
    echo "  (3 sonidos de prueba generados y enlazados)"
else
    echo "✗ no se pudo generar el WAV de prueba"
    exit 2
fi

gm-cli resourcetool eval \
  "room instance create room=room1 object=obj_test name=inst_test layer=Instances x=0 y=0" \
  "$YYP" >/dev/null 2>&1

# Leer de vuelta: «Success» no es verificación.
grep -q "inst_test" "$PROY/rooms/room1/room1.yy" \
  || { echo "✗ la instancia de prueba no llegó a la sala"; exit 2; }

echo "Ejecutando…"
SALIDA="$(cd "$PROY" && gm-cli run --toolchain "GMS2@2026.0.0.23" 2>&1)"
LINEA="$(echo "$SALIDA" | grep -o "RESULTADO: [0-9]* correctas, [0-9]* fallidas" | tail -1)"

if [ -z "$LINEA" ]; then
    echo "✗ el banco no llegó a terminar. Últimas líneas:"
    echo "$SALIDA" | grep -iE "error|FALLA" | tail -10
    exit 1
fi

echo "$SALIDA" | grep -E "MEDIDO ·" | sed "s/^[^M]*/  /" || true
echo "$SALIDA" | grep -E "FALLA ·" || true

if echo "$LINEA" | grep -q ", 0 fallidas"; then
    echo "✓ $LINEA — el código se ejecutó de verdad, no solo compiló."
    # Se deja constancia del número real para que la skill no lo lleve a mano:
    # decía «162 comprobaciones» cuando ya eran 189, y una cifra que envejece sola
    # enseña que las cifras de la skill son aproximadas.
    echo "$LINEA" | grep -oE "^RESULTADO: [0-9]+" | grep -oE "[0-9]+" \
        > "$RAIZ/_indice/pruebas/ultimo-resultado.txt"
    exit 0
else
    echo "✗ $LINEA"
    exit 1
fi
