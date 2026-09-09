#!/usr/bin/env bash
# verificar-trampas.sh — vuelve a comprobar, contra el CLI instalado HOY, las
# trampas de `12 · 09 §0` que se pueden comprobar sin tocar nada del usuario.
#
# POR QUÉ EXISTE. Cada trampa lleva su fecha: «verificado el 08-09-2026». Esa
# fecha envejece sola, y una trampa que YoYo arregle se convierte en una
# advertencia falsa — que enseña a desconfiar de las otras catorce, que es peor
# que no advertir. Esto la comprueba en cada pasada, contra el CLI de verdad.
#
#   bash _indice/verificar-trampas.sh
#
# Sale con 0 si todas las trampas comprobables SIGUEN siendo ciertas, y con 1 si
# alguna ya no lo es — que es una buena noticia, pero hay que actualizar el texto.
#
# NO se comprueban aquí, y se dice por qué:
#   · Trampa 1  (9 de 18 plantillas fallan) — 18 `init` son minutos y red.
#   · Trampa 2  (cuelgues bajo sandbox) — depende del entorno de quien ejecute.
#   · Trampa 4  (el compilador no ve una función inventada) — es conceptual.
#   · Trampa 6  (directory_exists bajo `run`) y 13 (screen_save invertido) — piden `run`.
#   · Trampa 11 (AccessViolation no determinista) — no se puede afirmar en una pasada.
#   · Trampa 12 (la fuente por defecto se come los acentos) — ya se mide, y mejor,
#     dentro del juego: `validar-ejecucion.sh`, banco de fuente.
#   · Trampa 15 (`cache clean --project` borra la caché COMPARTIDA) — comprobarla
#     destruiría la caché del usuario. Se deja sin comprobar A PROPÓSITO.
set -u

command -v gm-cli >/dev/null 2>&1 || { echo "✗ falta gm-cli en el PATH"; exit 2; }

PROY="$HOME/gm_prueba_trampas"
YYP="$PROY/gm_prueba_trampas.yyp"
FALLOS=0
CAMBIADAS=()

limpiar() { rm -rf "$PROY"; }
trap limpiar EXIT
rm -rf "$PROY"

decir() {  # decir <sigue|cambió> <trampa> <detalle>
    if [ "$1" = "sigue" ]; then
        echo "  ✓ $2 — sigue siendo cierta"
    else
        echo "  ⚠ $2 — YA NO se reproduce: $3"
        CAMBIADAS+=("$2")
        FALLOS=$((FALLOS + 1))
    fi
}

echo "Creando proyecto de usar y tirar en ${PROY}…"
( cd "$HOME" && gm-cli init --no-interactive --name "gm_prueba_trampas" --template "blank" \
    --no-ai --no-actions --toolchain "GMS2@2026.0.0.23" >/dev/null 2>&1 )
[ -f "$YYP" ] || { echo "✗ no se pudo crear el proyecto de prueba"; exit 2; }

R() { gm-cli resourcetool eval "$1" "$YYP" 2>&1; }

# ── Trampa 3 · el evento que se crea NO es el que pides ──────────────────────
R "resource create type=object name=obj_t3" >/dev/null
R "object event findorcreate name=obj_t3 type=draw subtype=gui_end" >/dev/null
if [ -f "$PROY/objects/obj_t3/Draw_73.gml" ] && [ ! -f "$PROY/objects/obj_t3/Draw_75.gml" ]; then
    decir sigue "Trampa 3 (gui_end da Draw_73, no Draw_75)"
else
    decir cambió "Trampa 3 (gui_end da Draw_73, no Draw_75)" \
        "$(ls "$PROY/objects/obj_t3/" | tr '\n' ' ')"
fi

# ── Trampa 5 · una fuente creada por CLI se queda sin glifos ─────────────────
R "resource create type=font name=fnt_t5" >/dev/null
R "font addrange name=fnt_t5 lower=32 upper=255" >/dev/null
if grep -q '"glyphs":{}' "$PROY/fonts/fnt_t5/fnt_t5.yy" 2>/dev/null \
   || grep -q '"glyphs": *{ *}' "$PROY/fonts/fnt_t5/fnt_t5.yy" 2>/dev/null; then
    decir sigue "Trampa 5 (la fuente se queda con glyphs vacío)"
else
    decir cambió "Trampa 5 (la fuente se queda con glyphs vacío)" \
        "$(grep -o '"glyphs":[^,]*' "$PROY/fonts/fnt_t5/fnt_t5.yy" 2>/dev/null | head -1)"
fi

# ── Trampa 8 · un included file no llega a datafiles/ ────────────────────────
R "resource create type=includedfile name=datos.json" >/dev/null
RUTA_IF="$(R 'resource info expr=project.IncludedFiles LIST' | grep -io "datafiles" | head -1)"
if [ -z "$RUTA_IF" ]; then
    decir sigue "Trampa 8 (el includedfile no apunta a datafiles/)"
else
    decir cambió "Trampa 8 (el includedfile no apunta a datafiles/)" "ya apunta a datafiles"
fi

# ── Trampa 10 · OPTIONS SET trunca el valor en el primer espacio ─────────────
R "options set platform=windows property=display_name value=Con Dos Palabras" >/dev/null
LEIDO="$(R 'options get platform=windows property=display_name' | grep -o 'display_name = .*' | head -1)"
if echo "$LEIDO" | grep -q "display_name = Con$"; then
    decir sigue "Trampa 10 (OPTIONS SET trunca en el primer espacio)"
else
    decir cambió "Trampa 10 (OPTIONS SET trunca en el primer espacio)" "«$LEIDO»"
fi

# …y que entrecomillar SIGUE siendo la salida (es una promesa de la skill).
R 'options set platform=windows property=display_name value="Con Dos Palabras"' >/dev/null
LEIDO2="$(R 'options get platform=windows property=display_name' | grep -o 'display_name = .*' | head -1)"
if echo "$LEIDO2" | grep -q "display_name = Con Dos Palabras"; then
    echo "  ✓ y el rodeo de las comillas dobles sigue funcionando"
else
    echo "  ✗ EL RODEO DE LAS COMILLAS YA NO FUNCIONA: «$LEIDO2»"
    FALLOS=$((FALLOS + 1))
fi

# ── Trampa 10 bis · la versión sigue siendo de solo lectura ──────────────────
if R "options set platform=windows property=version value=1.2.3.4" | grep -qi "read-only"; then
    decir sigue "Trampa 10 bis (version es de solo lectura)"
else
    decir cambió "Trampa 10 bis (version es de solo lectura)" "ya deja escribirla"
fi

# ── ProjectTool IMPORT YY · dice que importa y no registra nada (§3 ter.1) ───
# No es una trampa numerada, pero es la misma familia y la más cara: anuncia
# «Adding resource… Successful», copia la carpeta al disco y jamás la mete en el
# .yyp. La auditoría original la dio por buena porque el destino COMPILABA —
# precisamente porque no se había importado nada.
mkdir -p "$PROY/_suelto/spr_suelto"
cat > "$PROY/_suelto/spr_suelto/spr_suelto.yy" <<'YYEOF'
{"$GMSprite":"","%Name":"spr_suelto","name":"spr_suelto","resourceType":"GMSprite","resourceVersion":"2.0",}
YYEOF
gm-cli projecttool eval "import yy path=$PROY/_suelto/spr_suelto/spr_suelto.yy" "$YYP" >/dev/null 2>&1
if grep -q "spr_suelto" "$YYP"; then
    decir cambió "IMPORT YY (dice que importa y no registra en el .yyp)" "ya lo registra"
else
    decir sigue "IMPORT YY (dice que importa y no registra en el .yyp)"
fi

# ── Trampa 14 · RESOURCE CREATE TYPE=shape deja el proyecto irrecuperable ────
# Va la ÚLTIMA a propósito: rompe el proyecto de prueba.
R "resource create type=shape name=sh_t14" >/dev/null
if R "resource list type=object" | grep -qi "obj_t3"; then
    decir cambió "Trampa 14 (type=shape deja el proyecto irrecuperable)" "el proyecto sigue leyéndose"
else
    decir sigue "Trampa 14 (type=shape deja el proyecto irrecuperable)"
fi

echo
if [ "$FALLOS" -eq 0 ]; then
    echo "✓ Las 7 trampas comprobables siguen siendo ciertas con el CLI instalado hoy."
    exit 0
else
    echo "⚠ $FALLOS comprobación(es) han cambiado. Es una BUENA noticia —el CLI ha mejorado—,"
    echo "  pero hay que actualizar «12 · 09 §0» y la skill: una advertencia falsa enseña a"
    echo "  desconfiar de las que sí son ciertas."
    exit 1
fi
