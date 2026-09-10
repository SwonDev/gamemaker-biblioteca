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

Aquí viaja **solo la fuente**: unas 1 700 líneas en 34 archivos.

| Carpeta | Qué es |
|---|---|
| `enjambre/ESPECIFICACION.md` | La especificación escrita **antes** de crear el proyecto, con las ocho preguntas de `13 · 28` y cada valor asumido marcado `[DEFAULT]` |
| `enjambre/objects/` | Los nueve objetos, con su GML por evento |
| `enjambre/scripts/` | `scr_enjambre.gml`: idiomas, guardado con versión y checksum, entrada unificada, sacudida y *hit-stop* |
| `enjambre/herramientas/` | Los seis: generadores de arte, sonido e icono, las dos herramientas que montan el proyecto (`crear_objetos.py`, `registrar.py`) y el importador opcional de audio CC0 |

**No viajan el arte ni el sonido ni los `.yy`**, y es a propósito:

- El arte (30 PNG) y el sonido (8 WAV) **se regeneran** con los generadores de
  `herramientas/`. Guardar 1 MB de binarios que un script reproduce en dos segundos es
  guardar el resultado en vez de la receta.
- Los `.yy` los escribe `resourcetool`, nunca una persona
  ([regla dura](../AGENTS.md)). Copiarlos aquí invitaría a editarlos a mano.

## 2 · Cómo reconstruirlo entero

> Esta receta la ejecutó un auditor externo **siguiéndola al pie de la letra**, y encontró
> siete cosas que no estaban dichas: `$BIB` sin definir, Pillow sin mencionar, los nombres
> de carpeta que parecen libres y no lo son, y el icono que no se generaba —así que quien
> la seguía sacaba un ✗ en el auditor de la propia biblioteca—. Están todas corregidas
> aquí. Es la diferencia entre «funciona si ya sabes» y «funciona a ciegas».

**Antes de empezar** — dos cosas que la receta necesita y no puede darte:

```sh
python3 -m pip install --user Pillow      # los generadores de arte y glifos lo exigen
BIB="/ruta/donde/clonaste/gamemaker-biblioteca"   # esta biblioteca
```

`generar_glifos.py` además rasteriza los caracteres con una **tipografía del sistema** y
busca, por este orden: *Verdana Bold*, *Arial Bold* y *DejaVuSans-Bold*. En macOS y en la
mayoría de Linux hay alguna; si no, el script lo dice y no genera nada — no falla en
silencio.

```sh
# 1 · el proyecto. `gm-cli init` crea la subcarpeta `enjambre/` DENTRO del directorio actual.
cd ~                       # o donde quieras que viva el juego
gm-cli init --no-interactive --name enjambre --template blank \
            --no-ai --no-actions --toolchain "GMS2@2026.0.0.23"
cd enjambre

# 2 · la fuente publicada
cp -R "$BIB/14 - Juego de referencia/enjambre/"{objects,scripts,herramientas} .
cp    "$BIB/14 - Juego de referencia/enjambre/ESPECIFICACION.md" .

# 3 · generar arte, sonido, glifos e icono
#     ⚠ Los nombres «arte», «sonido», «glifos» e «icono» NO son libres: `registrar.py`
#     los tiene cableados y los espera DENTRO de la carpeta del proyecto. Generar en
#     otro sitio hace que aborte diciendo qué falta.
python3 herramientas/generar_arte.py arte
python3 herramientas/generar_sonido.py sonido
python3 "$BIB/_indice/pruebas/generar_glifos.py" glifos
python3 herramientas/generar_icono.py arte icono

# 4 · montar el proyecto (objetos, eventos, salas, sprites, sonidos, icono)
python3 herramientas/crear_objetos.py .
python3 herramientas/registrar.py .

# 5 · comprobar
gm-cli compile                                        # exit 0
python3 "$BIB/_indice/validar-proyecto.py" .          # ninguna función inventada
python3 "$BIB/_indice/auditar-juego-completo.py" .    # exit 0, envoltorio completo
gm-cli run                                            # y se juega
```

Los dos scripts que tocan el `.yyp` **verifican leyendo el disco**, no buscando «Success»
en la salida — que es como se descubrió que `sound set` no existe y dejaba las carpetas de
sonido vacías (`12 · 09 §0` trampa 16). `registrar.py` cuenta los `.wav` que hay dentro de
`sounds/`; `crear_objetos.py` lee el orden de salas del `.yyp` en crudo.

### Peldaño opcional: sonido CC0 de verdad

El sonido por defecto está **sintetizado con el módulo `wave` de Python**: ondas cuadradas
con envolvente. Suena a lo que es. Si tienes una biblioteca de assets a mano, hay un peldaño
más:

```sh
python3 herramientas/importar_audio_cc0.py . "/ruta/a/tu/Biblioteca de Assets"
```

Sustituye los ocho sonidos por audio de **Kenney**, y hace tres cosas que importan más que
la sustitución en sí:

1. **Comprueba la licencia pack a pack antes de copiar nada.** Lee el `License.txt` de cada
   pack y solo usa los que dicen CC0. No se fía del nombre de la carpeta ni de un índice.
   El texto que busca está literal en los packs de Kenney: *«License: (Creative Commons Zero,
   CC0) — This content is free to use in personal, educational and commercial projects»*.
2. **Verifica en el disco** que el audio llegó a `sounds/<nombre>/`, no que el comando dijera
   «Success» (trampa 16 otra vez).
3. **Escribe `CREDITOS-ASSETS.md`.** La atribución no es obligatoria en CC0; se pone porque
   cuesta una línea y es lo que hace que la gente siga publicando assets libres.

**Y si no tienes esa biblioteca, no pasa nada**: el script lo dice, sale con **2** —«no se ha
podido», no «ha fallado»— y el juego se queda con su sonido generado, que funciona. Esa es la
razón de que el sonido por defecto se genere: un juego de referencia que solo se reconstruye
en el disco de una persona no es una referencia.

> ⚠️ **Lo que NO se sustituye, y por qué.** Los sprites se quedan como están aunque la
> biblioteca tenga naves de sobra. Las que son CC0 (`Pixel Shmup`) son **aviones de hélice de
> la Segunda Guerra Mundial**: metidos en una arena espacial no leen como nave y enemigos,
> leen como otro juego. Y las que sí son sci-fi pixel art a la resolución exacta son
> justamente las que **no tienen licencia localizable** — así que no se usan. Un asset sin
> licencia no entra por muy bien que encaje.

### Lo que queda dentro y no estorba

`gm-cli init` deja una sala `room1` del andamiaje que el juego no usa: es inalcanzable
—solo hay `room_goto` explícitos a `rm_titulo` y `rm_juego`— pero viaja en el build. Puedes
borrarla desde el IDE cuando publiques. Las carpetas `herramientas/`, `arte/`, `sonido/`,
`glifos/` e `icono/` también se quedan: son el andamiaje que permite regenerar todo, y
GameMaker no las empaqueta.

### Si algo de esto deja de funcionar, saltará solo

```sh
bash "$BIB/_indice/validar-juego-referencia.sh"
```

Reconstruye el juego entero desde esta receta en una carpeta desechable y comprueba **en el
disco** que están los 8 audios, los 89 glifos, los 30 sprites, el icono, que se entra por la
portada, que la sala mide 683×384, que las salas tienen instancias, que el GML no inventa
funciones, que compila y que el auditor lo da por bueno. Si alguien rompe la receta, esto lo
dice antes de que lo descubra quien la siga.

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
