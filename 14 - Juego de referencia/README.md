# 14 · Juego de referencia — «Enjambre»

> **Qué es esto**: un juego **completo, que compila y se ejecuta**, construido siguiendo el
> flujo de la skill de punta a punta. No es un fragmento ni una receta: es el arco entero de
> [`04 · 00`](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md)
> con su especificación previa, su arte, su sonido y su envoltorio.
>
> **Por qué faltaba**: la biblioteca tenía recetas por género y scripts reutilizables, pero
> ningún juego propio que un agente pudiera **leer entero** para ver cómo encajan las piezas.
> Una receta enseña un sistema; esto enseña un juego.

---

## 1 · Qué contiene, y qué NO

Aquí viaja **solo la fuente**: 1 559 líneas en 33 archivos.

| Carpeta | Qué es |
|---|---|
| `enjambre/ESPECIFICACION.md` | La especificación escrita **antes** de crear el proyecto, con las ocho preguntas de `13 · 28` y cada valor asumido marcado `[DEFAULT]` |
| `enjambre/objects/` | Los nueve objetos, con su GML por evento |
| `enjambre/scripts/` | `scr_enjambre.gml`: idiomas, guardado con versión y checksum, entrada unificada, sacudida y *hit-stop* |
| `enjambre/herramientas/` | Los cuatro generadores: arte, sonido, registro de recursos y creación de objetos |

**No viajan el arte ni el sonido ni los `.yy`**, y es a propósito:

- El arte (30 PNG) y el sonido (8 WAV) **se regeneran** con los generadores de
  `herramientas/`. Guardar 1 MB de binarios que un script reproduce en dos segundos es
  guardar el resultado en vez de la receta.
- Los `.yy` los escribe `resourcetool`, nunca una persona
  ([regla dura](../AGENTS.md)). Copiarlos aquí invitaría a editarlos a mano.

## 2 · Cómo reconstruirlo entero

```bash
gm-cli init --no-interactive --name enjambre --template blank \
            --no-ai --no-actions --toolchain "GMS2@2026.0.0.23"
cd enjambre
cp -R <esta carpeta>/enjambre/{objects,scripts,herramientas,ESPECIFICACION.md} .

python3 herramientas/generar_arte.py arte        # 30 PNG de pixel art
python3 herramientas/generar_sonido.py sonido    # 8 WAV sintetizados
python3 "$BIB/_indice/pruebas/generar_glifos.py" glifos   # 89 glifos con tildes
python3 herramientas/crear_objetos.py .          # objetos, eventos y salas
python3 herramientas/registrar.py .              # sprites y sonidos al .yyp

gm-cli compile        # exit 0
gm-cli run            # se juega
```

Los dos scripts de `herramientas/` que tocan el `.yyp` **verifican leyendo el disco**, no
buscando «Success» en la salida — que es como se descubrió que `sound set` no existe y dejaba
las carpetas de sonido vacías (`12 · 09 §0` trampa 16).

## 3 · Qué enseña cada pieza

| Si buscas… | Míralo en |
|---|---|
| Un envoltorio completo de pantallas | `obj_titulo` (portada, menú, opciones, créditos) y `obj_juego` (pausa, derrota) |
| Guardado con versión de esquema y checksum | `scr_enjambre.gml` → `guardar_datos()` / `cargar_datos()` |
| Entrada unificada teclado + mando **en una sola función** | `scr_enjambre.gml` → `entrada_leer()` |
| Texto por clave, sin una cadena suelta en un `draw_text` | `scr_enjambre.gml` → `txt()` |
| Fuente con tildes sin `.ttf` que licenciar | `obj_control/Create_0.gml` → `font_add_sprite_ext` |
| Cámara a escala 2 sobre una sala pequeña | `obj_juego/Create_0.gml` |
| *Hit-stop* y sacudida de cámara | `sacudir()`, `congelar()`, y su uso en `obj_enemigo` |
| Copiar los datos **antes** de `instance_destroy()` | `obj_enemigo/Step_0.gml` → `morir()` |
| Un juego que se conduce solo para poder fotografiarlo | `obj_control/Step_0.gml`, modo captura |

## 4 · Lo que este juego demostró al construirse

Está entero en [`_indice/auditorias/r18-prueba-visual.md`](../_indice/auditorias/r18-prueba-visual.md):
siete defectos que **solo aparecen ejecutando y mirando** —las tildes que desaparecen, el
marcador de vidas vacío, el juego que se ve diminuto— y tres fallos de la propia prueba visual.

De ahí salieron las **cuatro decisiones que cuestan reescribir si las tomas tarde** que hoy
encabezan el flujo de la skill. Se descubrieron cayendo en ellas **con la biblioteca delante**:
documentar una trampa no basta si el flujo no obliga a esquivarla antes de que muerda.

## 5 · Qué NO es

No es un juego bueno. Es un juego **completo y correcto**: arranca, se navega, se juega, se
guarda y se cierra, con arte propio en vez de rectángulos. Si buscas diseño, las recetas de
`04` y los documentos de `13` son el sitio. Esto es el esqueleto, montado y funcionando.
