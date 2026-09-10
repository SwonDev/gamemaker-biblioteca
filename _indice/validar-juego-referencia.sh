#!/usr/bin/env bash
# Reconstruye el juego de referencia desde CERO siguiendo su propia receta, y comprueba
# que el resultado compila y tiene dentro lo que dice tener.
#
# **Por qué existe.** `14 - Juego de referencia` publica la fuente de «Enjambre» y una
# receta de seis comandos para reconstruirlo. Una receta que nadie ejecuta se pudre en
# silencio: la primera vez que se probó de verdad, faltaban la hoja de glifos, el tamaño
# de la sala, las instancias y el orden de salas — y `registrar.py` usaba `sound set`,
# que NO existe, así que el juego compilaba con ocho «Failed to convert audio file».
# Todo eso había pasado por «✓ registrados y verificados», porque la verificación miraba
# la salida del comando en vez del disco.
#
# Este script es la garantía de que no vuelva a pasar. Comprueba el DISCO, no lo que
# digan los comandos.
#
#   bash _indice/validar-juego-referencia.sh
#
# Sale con 0 si el juego se reconstruye y compila · 1 si algo falta · 2 si no se pudo
# comprobar (sin gm-cli, sin Pillow, sin fuente publicada).

set -u

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
REF="$RAIZ/14 - Juego de referencia/enjambre"
PROY="$HOME/gm_prueba_referencia"

. "$(cd "$(dirname "$0")" && pwd)/cerrojo.sh"

if ! command -v gm-cli >/dev/null 2>&1; then
  echo "✗ No encuentro «gm-cli» en el PATH. NO se ha comprobado nada."
  exit 2
fi
if ! python3 -c "import PIL" >/dev/null 2>&1; then
  echo "✗ Falta Pillow: el generador de arte no puede correr. NO se ha comprobado nada."
  echo "  python3 -m pip install --user Pillow"
  exit 2
fi
if [ ! -d "$REF/objects" ] || [ ! -d "$REF/herramientas" ]; then
  echo "✗ No está la fuente del juego de referencia en «$REF»."
  echo "  Eso NO es «el juego está bien»: es que no hay nada que comprobar."
  exit 2
fi

cerrojo_tomar "$PROY" || exit 2
limpiar() { rm -rf "$PROY"; cerrojo_soltar "$PROY"; }
trap limpiar EXIT

fallos=0
paso() { printf "  %-52s " "$1"; }
bien() { echo "✓ $1"; }
mal()  { echo "✗ $1"; fallos=$((fallos + 1)); }

echo "Reconstruyendo «Enjambre» desde la receta publicada…"
rm -rf "$PROY"
( cd "$HOME" && gm-cli init --no-interactive --name "$(basename "$PROY")" \
    --template "blank" --no-ai --no-actions --toolchain "GMS2@2026.0.0.23" ) >/dev/null 2>&1

if [ ! -f "$PROY/$(basename "$PROY").yyp" ]; then
  echo "✗ `gm-cli init` no creó el proyecto. NO se ha comprobado nada."
  exit 2
fi

cp -R "$REF/objects" "$REF/scripts" "$REF/herramientas" "$PROY/" 2>/dev/null
cp "$REF/ESPECIFICACION.md" "$PROY/" 2>/dev/null

cd "$PROY" || exit 2
python3 herramientas/generar_arte.py arte    >/dev/null 2>&1 || fallos=$((fallos + 1))
python3 herramientas/generar_sonido.py sonido >/dev/null 2>&1 || fallos=$((fallos + 1))
python3 "$RAIZ/_indice/pruebas/generar_glifos.py" glifos >/dev/null 2>&1 || fallos=$((fallos + 1))
python3 herramientas/generar_icono.py arte icono >/dev/null 2>&1 || fallos=$((fallos + 1))
python3 herramientas/crear_objetos.py . >/dev/null 2>&1 || fallos=$((fallos + 1))
python3 herramientas/registrar.py .      >/dev/null 2>&1 || fallos=$((fallos + 1))

echo
echo "Lo que hay EN EL DISCO (no lo que digan los comandos):"

paso "8 archivos de audio dentro de sounds/"
n_wav=$(find sounds -name "*.wav" 2>/dev/null | wc -l | tr -d ' ')
[ "$n_wav" = "8" ] && bien "$n_wav" || mal "$n_wav (la trampa de «sound set», que no existe)"

paso "la hoja de glifos, con sus 89 caracteres"
n_gl=$(find sprites/spr_glifos -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
[ "$n_gl" -ge 80 ] 2>/dev/null && bien "$n_gl" || mal "$n_gl (sin ella el juego no dibuja letras)"

paso "30 sprites de pixel art generados"
n_png=$(find arte -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
[ "$n_png" -ge 30 ] 2>/dev/null && bien "$n_png" || mal "$n_png"

paso "se entra por la portada, no por el nivel"
primera=$(grep -o '"roomId":{"name":"[a-z_0-9]*"' *.yyp 2>/dev/null | head -1 | sed 's/.*"name":"//;s/"//')
[ "$primera" = "rm_titulo" ] && bien "$primera" || mal "primera sala: ${primera:-ninguna}"

paso "la sala de juego mide 683×384 (cámara a escala 2)"
ancho=$(grep -o '"Width":[0-9]*' rooms/rm_juego/rm_juego.yy 2>/dev/null | head -1 | tr -dc 0-9)
[ "$ancho" = "683" ] && bien "$ancho" || mal "ancho: ${ancho:-desconocido}"

paso "las dos salas tienen sus instancias"
n_inst=$(grep -c '"%Name":"inst_' rooms/rm_titulo/rm_titulo.yy rooms/rm_juego/rm_juego.yy 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')
[ "$n_inst" -ge 4 ] 2>/dev/null && bien "$n_inst" || mal "$n_inst (sin instancias la sala está vacía)"

echo
paso "el icono llegó a options/ (lo exige el auditor)"
n_ico=$(find options -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
[ "$n_ico" -ge 1 ] 2>/dev/null && bien "$n_ico" || mal "ninguno (`property=`, no `name=`)"

paso "el GML no inventa ninguna función"
if python3 "$RAIZ/_indice/validar-proyecto.py" "$PROY" >/dev/null 2>&1; then bien "limpio"; else mal "hay funciones inventadas o aridades mal"; fi

paso "compila contra el runtime real"
salida_compile="$(gm-cli compile 2>&1)"
if echo "$salida_compile" | grep -q "Compilation finished"; then
  bien "exit 0"
else
  mal "NO compila"
  echo "$salida_compile" | grep -iE "Error :" | head -4 | sed 's/^/        /'
fi

paso "el auditor de juego completo lo da por bueno"
if python3 "$RAIZ/_indice/auditar-juego-completo.py" "$PROY" >/dev/null 2>&1; then
  bien "exit 0"
else
  mal "faltan piezas del envoltorio"
fi

# --- Y AHORA lo que de verdad decide: EJECUTARLO -----------------------------------
#
# 🔴 Este bloque existe porque su ausencia dejó pasar el peor fallo de todos. La primera
# versión de este guión compilaba y daba diez ✓ sobre un juego que **reventaba en el
# primer fotograma**: `crear_objetos.py` no registraba el script `scr_enjambre` en el
# `.yyp`, así que para el runtime `cargar_datos()` no existía. El compilador no dice
# nada de eso (trampa 4) y el archivo estaba en su carpeta, así que todo «parecía» bien.
#
# «Compilar no es ejecutar» es la doctrina de esta biblioteca, y el guardián escrito
# para hacerla cumplir era el primero que se la saltaba.
paso "ARRANCA sin reventar (el juego se ejecuta de verdad)"
GUARDADO="$HOME/Library/Application Support/com.yoyogames.macyoyorunner"
mkdir -p "$GUARDADO"
# Esa carpeta la comparten TODOS los juegos del runner: nunca se borra con comodines,
# solo lo propio y por nombre exacto.
rm -f "$GUARDADO"/enjambre_*_05_juego.png
printf "05_juego" > "$GUARDADO/modo_captura.txt"

salida_run="$(gm-cli run 2>&1)"
if echo "$salida_run" | grep -q "###CAPTURA###"; then
  bien "llegó a la pantalla de juego y se fotografió"
elif echo "$salida_run" | grep -qE "ERROR in action|not set before reading"; then
  mal "REVIENTA al arrancar (compilaba limpio)"
  echo "$salida_run" | grep -A 3 "ERROR in action" | head -6 | sed 's/^/        /'
else
  mal "no llegó a la captura y no dio un error reconocible"
  echo "$salida_run" | tail -4 | sed 's/^/        /'
fi

paso "y la captura tiene contenido, no un PNG negro"
foto="$(ls -t "$GUARDADO"/enjambre_*_05_juego.png 2>/dev/null | head -1)"
if [ -n "$foto" ] && [ -f "$foto" ]; then
  tam=$(wc -c < "$foto" | tr -d ' ')
  # Un fotograma negro de 1366×768 comprime a ~6 KB; uno con juego dentro pasa de 20 KB.
  if [ "$tam" -gt 15000 ]; then bien "$tam bytes"; else mal "$tam bytes (parece negro)"; fi
  rm -f "$foto"
else
  mal "no se escribió ninguna captura"
fi
rm -f "$GUARDADO/modo_captura.txt"

echo
if [ "$fallos" -gt 0 ]; then
  echo "✗ $fallos comprobación(es) fallan: la receta de «14 - Juego de referencia» ya no"
  echo "  reconstruye el juego. Arréglala ahí, no aquí — el juego es el entregable."
  exit 1
fi
echo "✓ El juego de referencia se reconstruye entero desde su receta, compila Y SE EJECUTA."
exit 0
