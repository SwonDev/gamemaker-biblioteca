# r12 · Prueba de encargo real — un plataformas 2D con historia, menú y guardado

> **Qué es esto.** El diario de fricción de una sesión que construyó un juego completo siguiendo
> la skill `gamemaker-biblioteca` de punta a punta, con dos restricciones nuevas respecto a las
> auditorías anteriores: **`gm-cli run` estaba prohibido** (solo `compile`) y el encargo llegó
> **cerrado, sin canal de vuelta con el usuario**. Encargo literal: «Hazme un juego de
> plataformas 2D con una historia pequeña. Que tenga menú, que se pueda guardar la partida y que
> se vea bien. Para Mac.»
>
> El objetivo del diario **no es evaluar al agente**: es encontrar los huecos de la
> documentación. Por eso se anota también lo que el agente hizo mal, y lo que se saltó.
>
> Fecha: **8 de septiembre de 2026** · `gm-cli` 2.3.0 · `ResourceTool@2026.0.17` ·
> runtime `GMS2@2026.0.0.23` · macOS (Darwin 25.6.0) · proyecto en
> `~/prueba_r12_plataformas/LaUltimaChispa`.

---

## 0 · Qué se construyó

**«La Última Chispa»** — plataformas 2D de tres niveles para macOS, unos 15 minutos de
recorrido. Vera, la farera de Punta Ceniza, recupera las tres chispas que la tormenta arrancó de
la lámpara del faro.

| Pieza | Qué hay |
|---|---|
| Arco completo (`04 · 00`) | rm_init → splash → menú → prólogo → 3 niveles → epílogo → créditos |
| Movimiento | Aceleración por `lerp`, gravedad asimétrica, coyote time, buffer de salto, salto variable, squash & stretch (`04 · 01 §5`) |
| Mundo | Bloques con *autotile* de 4 bits, plataformas de un sentido, plataformas móviles en los dos ejes, pinchos, cangrejos que patrullan, medusas que flotan |
| Envoltura | Menú por datos, selector de **3 ranuras** con metadatos, opciones (3 volúmenes, pantalla completa, sacudida de cámara, texto rápido), pausa, game over, confirmaciones con «No» por defecto |
| Guardado | `scr_save_load` de la biblioteca **sin modificar** + `scr_partida` propio. Autoguardado al encender un farol y al terminar un nivel |
| Texto | Todo por `txt(clave)` (`scr_idioma`), un idioma completo (español), fuente `.ttf` propia cargada con `font_add()` |
| Assets | 32 sprites / 104 fotogramas de pixel art generados con Pillow · 15 efectos y 3 pistas de música PCM generados con el módulo `wave` de Python · icono de 1024×1024 |
| Reutilizado de la biblioteca | `scr_math_util`, `scr_camera`, `scr_save_load`, `scr_ui_confirmar` (los cuatro sin tocar una línea) |
| Recuento del proyecto | 68 archivos `.gml` · 236 funciones · 21 objetos · 9 salas · 32 sprites · 18 sonidos · 3 *included files* |

Documentos del proyecto: `ESPECIFICACION.md` (plantilla de `13 · 28 §3.1`), `CHECKLIST.md`
(comparación punto por punto con `04 · 00`) y `README.md`.

### Salida real del último `gm-cli compile`

Sin `--errors-only`, que es el único modo que enseña los `WARNING` (Trampa 8):

```
$ gm-cli compile --toolchain GMS2@2026.0.0.23
…
│  Writing Chunk... TGIN size ... 0.00 MB
│  Writing Chunk... CODE size ... 0.00 MB
│  Writing Chunk... VARI size ... 0.08 MB
│  Writing Chunk... FUNC size ... 0.01 MB
│  Writing Chunk... FEAT size ... 0.00 MB
│  Writing Chunk... STRG size ... 0.00 MB
│  Writing Chunk... TXTR size ... 0.04 MB
│  0 Compressing texture...
│  writing texture __yy__0fallbacktexture.png_yyg_auto_gen_tex_group_name__0.yytex...
│  1 Compressing texture... writing texture default_0.yytex...
│  Writing Chunk... AUDO size ... 0.02 MB
│  Stats : GMA : Elapsed=596.694
│  Stats : GMA : sp=32,au=18,bk=0,pt=0,sc=236,sh=0,fo=0,tl=0,ob=21,ro=9,da=3,ex=0,ma=6,fm=0x929D6DFE24B4
│  Igor complete.
◆  Compilation finished
exit=0
```

**Ni un solo `WARNING`.** `da=3` confirma que los tres *included files* (las dos `.ttf` y la
licencia) llegaron al paquete; `unzip -l` sobre `game.zip` los enseña en `assets/`.

Y el validador, con el flag obligatorio:

```
$ python3 "$BIB/_indice/validar-proyecto.py" . --todo
68 archivos .gml · 1764 llamadas analizadas · runtime del índice 2026.0.0.23

✓ Ninguna llamada a una función del runtime que no exista.
✓ Ninguna llamada a una función del runtime con un número de argumentos que no cuadre con su firma.
```

**Compilar limpio no es funcionar** (`12 · 09` Trampa 4): el juego **no se ha ejecutado ni una
vez**. Lo que eso deja sin verificar está en `CHECKLIST.md` del proyecto, dicho en voz alta.

---

## 1 · Lo que costó más de lo razonable

### 1.1 · El validador se queda ciego con una comilla escapada dentro de un literal — y miente hacia el lado peligroso

**Severidad: alta.** Es el hallazgo más importante de la sesión.

`validar-proyecto.py --todo` reportó tres nombres «desconocidos»:

```
· 3 nombres que el proyecto no define ni el runtime declara:
  cangrejo_aplastar()  en objects/obj_jugador/Step_0.gml
  nivel_ficha()        en objects/obj_nivel/Create_0.gml, scripts/scr_niveles/scr_niveles.gml
  niveles_total()      en objects/obj_final/Create_0.gml, objects/obj_nivel/Draw_64.gml, …
```

El primero era **un error real mío** (una función que nunca llegué a escribir; el compilador la
tragó con `exit 0`, exactamente como describe la Trampa 4 — el validador se ganó el sueldo ahí).

Los otros dos eran **falsos positivos**, y la causa es un bug reproducible de
`validar-codigo-gml.py::limpiar()`. Mi mapa de niveles usaba el carácter `"` como símbolo de
una plataforma móvil larga, así que el `.gml` generado tenía literales con una comilla escapada:

```gml
"...####......\".......*..",
```

Reproducción mínima, ejecutada en esta sesión:

```python
import importlib.util
spec = importlib.util.spec_from_file_location("vcg", "_indice/validar-codigo-gml.py")
vcg = importlib.util.module_from_spec(spec); spec.loader.exec_module(vcg)
cod = vcg.limpiar(open("scripts/scr_niveles/scr_niveles.gml", encoding="utf-8").read())
print([m.group(1) for m in vcg.DEFINE.finditer(cod)])
# ['nivel_sala', 'nivel_reanudar', 'nivel_reintentar', 'nivel_reiniciar',
#  'mapa_es_solido', 'mapa_mascara', 'nivel_esquirlas_del_juego']
#  ↑ faltan niveles_total y nivel_ficha, que están DEFINIDAS en ese mismo archivo
print(cod.find("function niveles_total"))   # -1
```

`limpiar()` no reconoce `\"` como comilla escapada, cierra la cadena donde no toca y a partir de
ahí el mapeo de qué es código y qué es literal se descuadra: se comió dos definiciones reales.

**Por qué importa más de lo que parece.** El daño no es el falso positivo en sí, es que
**enseña a desconfiar de la lista**. La salida mezclaba un error de verdad
(`cangrejo_aplastar`) con dos falsos positivos, y el flujo de la skill pide «revisar a mano la
lista de `desconocida`». Un agente con menos paciencia mira tres nombres, comprueba que dos
están definidos, concluye «el validador exagera» y **se salta el tercero**, que era el único que
iba a reventar el juego en tiempo de ejecución. El fallo de la herramienta no crea el bug: crea
la excusa para no mirarlo.

**Corrección propuesta**: que `limpiar()` trate `\\` y `\"` como caracteres escapados dentro de
una cadena. Y mientras tanto, una línea en `12 · 09 §7.5`: «si un nombre sale como
`desconocida` y lo puedes ver definido con `grep -n "function <nombre>"`, comprueba si el
archivo tiene alguna cadena con `\"` antes de dar el aviso por bueno».

*(Yo lo esquivé cambiando el carácter del mapa de `"` a `>`, que además hace el mapa más legible
— pero eso es rodearlo, no arreglarlo.)*

### 1.2 · `OPTIONS SET` trunca el valor en el primer espacio, y dice «Success»

**Severidad: alta, y es un fallo silencioso nuevo de la misma familia que la Trampa 10.**

```bash
$ gm-cli resourcetool eval "options set platform=mac property=display_name value=La Ultima Chispa"
Set mac.display_name = La
Saved successfully
ResourceTool Successful
```

Se quedó con `La`. Con `Saved successfully` y `ResourceTool Successful`: **ni un aviso**. El
juego habría salido llamándose «La» en el Finder y en el conmutador de aplicaciones, y no hay
ninguna forma de enterarse salvo releer con `options get`.

La solución es entrecomillar el valor, y funciona incluso con tildes:

```bash
$ gm-cli resourcetool eval 'options set platform=mac property=display_name value="La Última Chispa"'
Set mac.display_name = La Última Chispa
$ xxd  # sobre options/mac/options_mac.yy → "La \xc3\x9altima Chispa": UTF-8 intacto
```

No está en `12 · 09 §9 quater` (que es donde vive todo lo de `OPTIONS`), ni en la tabla de
comandos de `07 · 13`. **Cualquier propiedad de texto con un espacio está afectada**:
`display_name`, y en las plataformas donde sí son escribibles, `company_info`, `copyright_info`,
`description_info`, `product_info`.

### 1.3 · La Trampa 10 está escrita con la tabla de Windows, y Mac tiene otra

`12 · 09 §9 quater` dice que solo cinco propiedades son escribibles: `interpolate_pixels`,
`start_fullscreen`, `display_name`, `icon` y `splash_screen`. En **Mac** los nombres no son esos
y la lista tampoco es la misma. `options info platform=mac` devuelve 29 propiedades:

```
allow_fullscreen allow_incoming_network allow_outgoing_network app_category app_id
apple_sign_in build_app_store build_number copyright disable_sandbox display_cursor
display_name enable_retina icon_png installer_background_png interpolate_pixels menu_dock
min_version output_dir resize_window scale signing_identity splash_png start_fullscreen
team_id texture_page version vsync
```

`icon` no existe en Mac: es **`icon_png`**. `splash_screen` es **`splash_png`**. Y confirmado en
vivo que `version` y `copyright` **también son de solo lectura aquí**:

```
$ gm-cli resourcetool eval "options set platform=mac property=version value=1.0.0.0"
Property 'version' cannot be set on 'mac' because it is read-only.
```

Un agente que prepare una entrega para Mac —y este encargo decía «Para Mac»— sigue la tabla de
la trampa, prueba `property=icon`, se lo rechazan, y se queda con la impresión de que el icono
tampoco se puede. **Sí se puede**, con el nombre correcto.

**Además, un detalle que ninguna doc da**: `icon_png` exige **exactamente 1024×1024**, y lo dice
con un error limpio (a su favor):

```
Image '.../icono.png' dimensions (512 x 512) do not match the expected dimensions (1024 x 1024).
```

Costó una iteración. Una línea en `12 · 09 §9 quater` la ahorra.

### 1.4 · Cómo dejar una sala lista para pixel art por CLI: no está escrito en ningún sitio

**Severidad: media-alta.** Fue lo que más tiempo me costó razonar sin ayuda de la biblioteca.

El juego dibuja a 480×270 y escala a la ventana. La plantilla *Blank Pixel Game* deja las salas
con `viewSettings.enableViews: false` y `views[0]` en **1366×768** (tanto `wview`/`hview` como
`wport`/`hport`), heredado del tamaño de `Room1`.

Si solo se activa la vista en tiempo de ejecución (`view_enabled = true; view_camera[0] = cam;`,
que es lo que enseña `04 · 01 §5.7` y `scr_camera`), la superficie de aplicación se queda al
tamaño de la **sala** —2400×352 en mi primer nivel— y el puerto de vista al de la plantilla. El
resultado es una vista estirada y recortada. Y **compila limpio**, claro.

La biblioteca documenta `project.RoomOrderNodes` con lujo de detalle (`12 · 09 §9` y §9 bis) y no
dice una palabra de `viewSettings` ni de `views[N]`, que es la otra mitad de «dejar una sala
lista». Lo deduje probando. Funciona y queda verificado:

```bash
gm-cli resourcetool eval "resource set expr=rm_nivel1.viewSettings.enableViews value=true"
gm-cli resourcetool eval "resource set expr=rm_nivel1.views[0].visible value=true"
gm-cli resourcetool eval "resource set expr=rm_nivel1.views[0].wview value=480"
gm-cli resourcetool eval "resource set expr=rm_nivel1.views[0].hview value=270"
gm-cli resourcetool eval "resource set expr=rm_nivel1.views[0].wport value=480"
gm-cli resourcetool eval "resource set expr=rm_nivel1.views[0].hport value=270"
gm-cli resourcetool eval "resource set expr=rm_nivel1.roomSettings.Width  value=2400"
gm-cli resourcetool eval "resource set expr=rm_nivel1.roomSettings.Height value=352"
```

Los ocho persisten y se leen en el `.yy`. **Propuesta**: una sub-sección en `12 · 09 §9` —
«§9.5 · Tamaño de sala y vistas por CLI» — con esta receta y el aviso de que la plantilla deja
el puerto a 1366×768.

Efecto secundario que también hay que documentar: con la vista activada en el `.yy`, **GameMaker
ya crea una cámara para la vista 0 al entrar en la sala**. Si el objeto de cámara hace
`camera_create()` y la asigna a `view_camera[0]`, la del motor se queda viva y sin dueño — una
por cada entrada al nivel. La forma correcta es reutilizar la que ya hay:

```gml
cam = view_camera[0];
camara_propia = false;
if (cam == -1) { cam = camera_create(); camara_propia = true; }
```

…y en Clean Up destruirla **solo** si es propia. `06 · scr_camera.gml` enseña
`cam = camera_create(); … view_camera[0] = cam;` en su bloque de uso rápido, que es el caso
correcto **solo** si la sala no trae vistas activadas — y no lo dice.

### 1.5 · `save_get_meta()` devuelve el sobre, no los metadatos

**Severidad: media. Fallo silencioso, no lo caza nada.**

Escribí la ficha de la pantalla de ranuras leyendo `_meta.nivel`, `_meta.esquirlas`,
`_meta.segundos` de lo que devuelve `save_get_meta()`. Compila. `validar-proyecto.py` pasa. Y la
pantalla de «elige partida» habría dicho **«Nivel 1 · 0 esquirlas · 0 m 00 s» en todas las
ranuras, siempre**, porque `save_get_meta()` devuelve el sobre entero:

```gml
return {
    version : _sobre.version,
    fecha   : …,
    meta    : …          // ← aquí está lo que guardó el juego
};
```

El docblock del script lo dice («Devuelve version, fecha y los metadatos opcionales»), pero es
fácil leerlo como «devuelve los metadatos, y de paso versión y fecha». Lo detecté leyendo el
código del script, no usándolo.

**Propuesta**: añadir el acceso al ejemplo de uso, tanto en la cabecera de
`06 - Assets y Scripts/scr_save_load.gml` como en `13 · 05` componente n):

```gml
var _sobre = save_get_meta("ranura1");
if (is_struct(_sobre) && is_struct(_sobre.meta)) {
    var _zona = _sobre.meta.zona;      // lo que TU juego metió en save_game(_slot, _datos, _meta)
}
```

Es el mismo tipo de error que la biblioteca ya persigue en otros sitios: compila, no truena, y
la pantalla enseña un dato falso.

### 1.6 · La receta de plataformas (`04 · 01`) no es copiable tal cual

Dos cosas, y las dos en «§5 · Código base», que es justo la sección que un agente copia:

1. **Los nombres violan las convenciones de la propia skill.** La receta usa `objPlayer`,
   `objSolid`, `objPlatformMoving`, `objCamera`. `SKILL.md` §«Convenciones del código que
   generes» exige `snake_case` con prefijo `obj_`. Un agente que copie el bloque de §5.3 tal
   cual entrega código que su propia guía de estilo rechaza. Tuve que traducir cada nombre
   mientras leía.

2. **§5.3 tiene código muerto que se presenta como código base.** El bloque de colisión trae
   esto literalmente:

   ```gml
   if (vel_y > 0 && is_undefined(_hit[1])) {}      // cayendo y nada debajo
   if (vel_y > 0) {}                                // placeholder
   if (_hit[1] != noone && vel_y > 0) { … }
   ```

   Dos condicionales vacíos y un `// placeholder` dentro de la rama que decide el aterrizaje. No
   está claro qué hace `move_and_collide` con el eje y hay que resolverlo por tu cuenta. Acabé
   deduciendo el eje del choque con `place_meeting()` **después** de mover, que es más simple y
   no depende de cómo se interprete el array de retorno:

   ```gml
   move_and_collide(vel_x, vel_y, obj_solido, 4, 0, 0, VEL_MAX, -1);
   if (vel_y > 0 && place_meeting(x, y + 1, obj_solido)) { vel_y = 0; en_suelo = true; }
   else if (vel_y < 0 && place_meeting(x, y - 1, obj_solido)) { vel_y = 0; }
   if (vel_x != 0 && place_meeting(x + sign(vel_x), y, obj_solido)) { vel_x = 0; }
   ```

   **Propuesta**: sustituir el bloque de §5.3 por algo que funcione, o marcarlo explícitamente
   como pseudocódigo. Una sección titulada «Código base» dentro de una biblioteca cuya regla
   número uno es «no inventes» no debería tener un `// placeholder`.

### 1.7 · La pausa: `04 · 00` enseña el patrón malo y avisa dos párrafos después

`04 · 00 §5` da `instance_deactivate_all(true)` como «pausa robusta», con su explicación del
`true`… y **después** un recuadro rojo diciendo que ese patrón deja la pantalla en negro detrás
del menú, que lo bueno está en `04 · 41 §3.1.1`, y que hace falta capturar el fotograma en una
superficie.

Un agente que lea linealmente escribe la pausa mal y se entera al párrafo siguiente. El orden
correcto sería: el patrón bueno primero, el mínimo después y marcado como mínimo.

Y hay una tercera vía que no menciona ninguno de los dos documentos, y que para un juego pequeño
es más simple **y** más correcta: un interruptor global (`global.juego_activo`) que todos los
objetos del mundo consultan al empezar su Step. Congela el mundo de verdad, lo sigue dibujando
sin superficies de por medio, y no tiene los cuatro agujeros de `instance_deactivate_all`
(alarmas, *time sources*, partículas, Sequences, Box2D). El precio es disciplina: hay que
acordarse de consultarlo en cada objeto. Es la vía que usé.

### 1.8 · No hay receta de «un nivel como mapa de texto»

Esta es la decisión estructural más grande del juego y la tomé sin apoyo de la biblioteca.

Colocar el nivel con instancias en la sala significa cientos de `ROOM INSTANCE CREATE` (mis tres
niveles tienen 1 424 instancias de bloque). Además, `12 · 09 §9.2` avisa de que borrar o recrear
una sala se lleva su contenido, así que iterar sobre el diseño sería carísimo. La alternativa
obvia —el nivel como un array de cadenas y un constructor en el Create del gestor— **no está en
ninguna parte de la biblioteca**: `04 · 01 §2` habla de «Rooms y capas» y da por hecho el editor
de salas; `13 · 02 - Diseño de niveles` habla de diseño, no de cómo materializarlo sin IDE.

Es un hueco raro, porque toda la biblioteca está escrita para un agente que no abre el IDE, y
esta es **la** técnica que hace posible diseñar un nivel sin él.

**Propuesta**: una sección en `04 · 01` (o mejor, un documento propio en `04`) con el patrón
completo: leyenda de caracteres, verificación de que todas las filas miden lo mismo, cálculo del
*autotile* de 4 bits, índices estables para los coleccionables (que es de lo que depende el
guardado), y la optimización de no crear las casillas rodeadas de roca por los ocho lados
—en mis mapas eso quita entre el 33 % y el 64 % de las instancias:

```
nivel1: 758 bloques -> 272 instancias (64% menos)
nivel2: 1793 bloques -> 716 instancias (60% menos)
nivel3: 646 bloques -> 436 instancias (33% menos)
```

### 1.9 · `draw_sprite_tiled_ext()` repite en los dos ejes: no sirve para una banda

Fricción propia, pero apunta a un hueco. Quería una franja de mar repetida en horizontal para el
*parallax* y usé `draw_sprite_tiled_ext()`, que **repite también en vertical** y llena la
pantalla entera. Lo pillé releyendo, no ejecutando (no podía ejecutar).

La biblioteca tiene cámara (`04 · 01 §4.9`, `06 · scr_camera.gml`, `13 · 19`) y dibujo
(`01 · 11`), pero **ninguna receta de fondos con parallax**: ni la fórmula, ni el problema de
repetir en un solo eje. Acabé escribiendo `ui_banda()` y dejando escrita la fórmula en el
comentario, porque tampoco estaba en ningún sitio:

> una capa que se mueve a factor `f` respecto al mundo se dibuja, en coordenadas de sala, en
> `x_mundo + camara_x * (1 - f)`.

`04 · 01 §1` promete un plataformas que «se vea bien» y el fondo es la mitad de eso.

### 1.10 · Los *included files* se pasan a minúsculas en el paquete

Confirmado en `unzip -l` sobre `game.zip`:

```
   137052  assets/fuente_titulo.ttf
   139512  assets/fuente_ui.ttf
     4414  assets/licencia_fuentes.txt      ← el recurso se llama LICENCIA_FUENTES.txt
```

Tuve suerte: mis dos `.ttf` ya estaban en minúsculas, así que `font_add("fuente_ui.ttf", …)`
encuentra el archivo. Si hubiera llamado al recurso `Fuente_UI.ttf` y luego pedido
`font_add("Fuente_UI.ttf")`, habría fallado **en silencio** (`font_add` devuelve -1 y el juego
cae a la fuente por defecto, que se come las tildes: Trampa 12 por la puerta de atrás).

La Trampa 8 explica muy bien cómo hacer que el archivo llegue al paquete, y no dice nada de que
el nombre cambie por el camino. **Una línea basta**: «los *included files* se escriben en
minúsculas en el paquete: nombra el recurso en minúsculas y úsalo así desde GML».

*(Defensa que sí puse, y que recomiendo a cualquiera: comprobar el retorno de `font_add()` y
soltar un `show_debug_message` si es -1. Es lo único que delata este fallo sin mirar la
pantalla.)*

### 1.11 · La receta de resolución existía en `13 · 03` y no la encontré hasta el final

**Esta entrada es sobre encaminamiento, no sobre contenido: el documento estaba bien escrito y
aun así no llegué a él.**

Monté la resolución a ojo: `window_set_size(1280, 720)` con el mundo a 480×270 y la GUI a
960×540. Es decir, escala de mundo 2,67× — **no entera**, que en pixel art significa que unos
píxeles del arte miden dos y otros tres, y el movimiento «hierve». Justo lo que `13 · 03` existe
para evitar.

La receta correcta estaba en **`13 · 03 §1.6`**, con las dos funciones ya escritas
(`escala_entera_maxima()` y `aplicar_resolucion()`), el aviso de reservar sitio para la barra de
título y la recomendación de poner la GUI a `base × 2` cuando el HUD lleva texto. Las copié tal
cual y sustituí mi apaño.

**Por qué no llegué antes.** Mis puntos de entrada fueron los que da `SKILL.md`: la tabla «Te
piden… → Empieza por», que para «un juego de género X» manda a `04 - Recetas por género/`, y
`12 · 09` para operar el CLI. `13 · 03 - Pixel art y resolución` aparece en esa tabla bajo
«Diseñar: mecánicas, niveles, arte, UI, sonido, historia», y yo lo leí como «cómo dibujar pixel
art» — una tarea de artista, no de programador. La palabra «resolución» está en el título y aun
así no la vi, porque estaba buscando cómo programar el juego, no cómo dibujarlo.

**Propuesta concreta**: una fila más en la tabla de `SKILL.md`:

| Te piden… | Empieza por |
|---|---|
| Fijar resolución, escala de ventana, tamaño de la GUI o pantalla completa | `13 · 03 §1` — antes de escribir el primer `window_set_size()` |

Y en `04 · 01` (la receta de plataformas), un enlace a `13 · 03 §1.6` junto a la sección de
cámara: quien monta una cámara de plataformas está a un paso de tener que decidir la escala, y
`04 · 01 §4.9` no lo menciona.

**Un matiz que sí falta como contenido**, y que descubrí al aplicar la receta: con
`gpu_set_texfilter(false)` —que la propia receta manda para el pixel art— **el texto de una
fuente `.ttf` también se dibuja sin filtrar**. Si la GUI se escala a la ventana por un factor no
entero (GUI a `base × 2` y ventana a `base × 3` da 1,5×, que es el caso normal), las letras
salen con los bordes rotos. La solución es encender el filtrado solo alrededor de las llamadas
de texto:

```gml
gpu_set_texfilter(true);
draw_text(_x, _y, _texto);
gpu_set_texfilter(false);
```

Ni `13 · 03 §1.6` ni `13 · 05 §3.6` (tipografía) mencionan esta interacción, y aparece siempre
que se mezcla pixel art con tipografía real — que es exactamente lo que obliga a hacer la
Trampa 12.

### 1.12 · El checklist de pausa y transiciones de `04 · 41 §4` existía, estaba enlazado, y no lo abrí

**La entrada más incómoda del diario, y la más útil.**

Marqué «Menú de pausa que congela el mundo de verdad» como hecho en mi checklist. El punto de
`04 · 00` dice, literalmente:

> - [ ] Menú de pausa que congela el mundo de verdad, no solo el dibujo (detalle: `04 · 41 §4`)

Traté ese «(detalle: …)» como opcional —ya tenía la pausa hecha y me parecía bien resuelta— y no
abrí `04 · 41`. Cuando después revisé el código contra ese checklist, **fallaba dos de sus
puntos**, y uno era un fallo de verdad:

- «**Está decidido dónde NO se puede pausar (transición en curso, …)**» → mi gestor de nivel era
  el único objeto de pantalla **sin** la guarda `if (escena_cambiando()) { exit; }` que sí tenían
  los otros cinco. Durante los 20 frames del fundido de salida al menú, el menú de pausa seguía
  aceptando entrada: se podía abrir la pantalla de opciones o un diálogo de confirmación cuyas
  funciones son **métodos ligados a la instancia del nivel**, que muere en el cambio de sala.
  Resultado: las opciones del nivel dibujadas encima del menú principal, con sus lecturas
  apuntando a una instancia destruida.
- «**La transición congela el mundo mientras dura**» → tampoco. El jugador seguía cayendo (y
  muriendo) mientras la pantalla ya se iba a negro.
- «**`pausar_de_verdad()` cubre … y audio**» → mi pausa no tocaba el audio. Lo cerré atenuando la
  música a un tercio en vez de con `audio_pause_all()`, que dejaría mudos los sonidos del propio
  menú de pausa.

Los tres estaban en una lista de seis puntos, en un documento que `04 · 00` enlaza en la misma
línea del checklist que yo marqué.

**Qué pediría a la documentación.** No es un hueco de contenido: el contenido estaba y era bueno.
Es de **fuerza del enlace**. La casilla de `04 · 00` se puede marcar sin abrir `04 · 41 §4`, y eso
es exactamente lo que hice. Dos cambios pequeños lo arreglarían:

1. Que la casilla de `04 · 00` diga qué hay que haber comprobado, no dónde está: «*Menú de pausa
   que congela el mundo de verdad — **los 6 puntos de `04 · 41 §4`, incluido dónde NO se puede
   pausar y que la transición congele el mundo***».
2. Que el paso 7 del flujo de `SKILL.md` («compara contra el checklist maestro de `04 · 00`») diga
   explícitamente que **las tres listas enlazadas desde ahí —`04 · 41 §4`, `13 · 05 §4` y
   `05 · 02 §4.4`— también se comparan**, no solo la maestra. Hoy la tabla las presenta como «si
   necesitas el detalle de…», que se lee como opcional.

Es el mismo problema que la biblioteca ya diagnosticó una vez en otro sitio: un aviso que vive en
un documento que el flujo normal no visita acaba sin leerse. Aquí el documento sí está enlazado —
pero desde una casilla que se puede marcar sin seguirlo.

### 1.13 · Sin poder ejecutar, la única red es leer el código — y para eso no hay checklist

Con `gm-cli run` prohibido, el flujo de la skill se queda cojo por diseño: el paso 8 («Ejecutar»)
de `12 · 09 §1` no existe, y `13 · 10 §8.6` —«compilar limpio no es lo mismo que funcionar»—
propone exactamente los dos procedimientos que necesitan ejecutar el juego.

Lo sustituí por una revisión de código deliberada, línea a línea, buscando **solo** las familias
de fallo que ni el compilador ni `validar-proyecto.py` ven. Encontró cuatro errores reales que
habrían llegado al usuario:

1. El gestor del nivel era el único objeto de pantalla **sin** la guarda `escena_cambiando()`
   (§1.12): se podían abrir las opciones durante el fundido de salida, con sus funciones ligadas
   a una instancia que muere en el cambio de sala.
2. `montado` se quedaba pegado al bajarse de una plataforma móvil a suelo firme. La condición era
   `if (hay_plataforma && en_suelo) { … } else if (!en_suelo) { montado = noone; }`: el caso «no
   hay plataforma debajo **y** estoy en el suelo» no entraba en ninguna rama, así que la
   plataforma seguía arrastrando al jugador estando de pie sobre la roca.
3. Las partículas se congelaban **para siempre** en la pantalla de derrota y en la de nivel
   completado: su guarda era `if (!global.juego_activo) exit;`, así que su contador de vida no
   bajaba y nunca se destruían. Justo en las dos pantallas que más se miran.
4. Un cangrejo pisado seguía contando su temporizador de KO durante la pausa, porque la guarda de
   pausa estaba **después** del bloque de KO en su Step.

Los cuatro comparten forma: **una guarda de pausa o de transición mal colocada, o una rama que se
olvida de un caso**. Ninguno es un símbolo inventado ni un error de sintaxis, así que las dos
herramientas de la biblioteca pasan por encima sin verlos.

**Lo que falta**: `13 · 10` tiene el mini-framework de pruebas, el guion de humo y cómo
interpretar los errores del compilador, todo apoyado en ejecutar. No tiene una lista de
**qué mirar leyendo** cuando no se puede ejecutar. Sería corta y muy rentable:

- ¿Toda global que se lee está inicializada en **todos** los caminos de sala? (variante de la
  Trampa 4)
- ¿Cada objeto del mundo consulta el interruptor de pausa, y **antes** de cualquier otra cosa de
  su Step?
- ¿Cada objeto de pantalla corta la entrada mientras hay una transición en curso?
- ¿Cada `if/else if` sobre un estado cubre el caso «ninguna de las dos»?
- ¿Alguna global (diálogo abierto, pantalla de opciones) guarda un método ligado a una instancia
  que puede morir antes de que se llame?
- ¿Algún contador de vida o de temporizador está detrás de una guarda que puede quedarse en
  `false` para siempre?

Las seis se comprueban leyendo, y las seis cazaron algo real en esta sesión.

---

## 2 · Cosas pequeñas que costaron un minuto cada una

- **`buscar.py --help` no da ayuda.** La trata como un símbolo: «`--help` NO existe en el
  runtime». Los flags están en `SKILL.md`, así que no bloquea, pero es el primer sitio donde uno
  mira. Un `if "--help" in sys.argv` de tres líneas lo arregla.
- **`SKILL.md` dice «46 recetas» en `04 - Recetas por género/`; hay 58** (`00` a `57`). Detalle,
  pero es el número que un agente usa para decidir si merece la pena mirar la carpeta.
- **El modo por lotes acepta `#` como comentario y `//` no.** Probado a propósito, porque la
  documentación de `12 · 09 §10` no lo dice y un archivo de lote es justo donde quieres poner
  comentarios:

  ```
  $> # esto es un comentario
  $> RESOURCE LIST TYPE=room        ← se ejecuta
  $> // y esto otro
  Unknown Command: // y esto otro
  ResourceTool Failed
  ```

  Las líneas en blanco sí se ignoran. Dos líneas en §10.1 lo cierran. Yo los quité
  preventivamente y me quedé sin comentarios en un lote de 440 líneas.
- **`options info platform=mac` devuelve 82 KB** de tabla con bordes, que desborda la salida del
  Bash de Claude Code y hay que filtrar con `grep -oE`. `12 · 09 §9 quater` enseña la salida de
  Windows recortada; convendría avisar de que la tabla completa no cabe y dar el `grep`.
- **En zsh, `set -- $variable` no separa por palabras** (a diferencia de bash). Me comí una
  iteración con un bucle de `resourcetool` que construía rutas como
  `rooms/rm_nivel1 2400 352/`. No es culpa de la biblioteca; lo anoto porque toda la
  documentación da ejemplos de shell y el shell por defecto de este Mac es zsh.

---

## 3 · Lo que me vi tentado de hacer mal, y por qué no lo hice

Esto no es autocrítica decorativa: cada tentación es una señal de dónde la documentación tiene
que apretar más.

1. **Usar `draw_set_font(-1)` y no meterme con fuentes.** Es la salida cómoda, y `08 · 03` la
   sugiere como alternativa segura al horneado roto de la Trampa 5. Habría entregado un juego
   entero en un castellano sin tildes ni eñes, compilando limpio. La Trampa 12 lo dice tan claro
   que no hubo duda — **funcionó exactamente como estaba pensada**. Es la trampa mejor escrita de
   las trece.
2. **Compilar solo con `--errors-only`.** Es más rápido y es lo que la tabla de §1 recomienda
   para iterar. La nota de la Trampa 8 («antes de cerrar una tarea, compila al menos una vez sin
   el flag») me hizo hacerlo, y la salida completa confirmó que `da=3` y que no había ningún
   `WARNING` de *datafile*. También funcionó.
3. **Entregar cuadrados de colores como sprites.** Con `gm-cli run` prohibido, nadie iba a ver la
   diferencia hasta que el usuario abriera el juego. La prohibición de `SKILL.md` («un rectángulo
   de color no es un sprite») y la escalera de `12 · 09 §5.2` son explícitas, y la tabla de
   «calidad mínima exigible» da un criterio comprobable sin ejecutar nada: silueta legible en
   escala de grises, paleta por categoría, origen correcto, dos fotogramas en lo que se mueve.
   La usé como lista de comprobación real, ampliando los PNG ×6 y mirándolos.
   **Y me sirvió**: la primera versión de la protagonista no pasaba el filtro —las piernas eran
   del mismo color que el abrigo y el ciclo de carrera no se leía— y la rehíce.
4. **Saltarme el ciclo «un sistema, compilar»** y escribir los 21 objetos antes de compilar una
   sola vez. Lo hice a medias: compilé por primera vez con el proyecto entero escrito. Salió
   bien, pero fue suerte; `12 · 09 §1` avisa de que el primer error de sintaxis esconde los
   demás. Lo anoto como incumplimiento.

---

## 4 · Lo que me salté del flujo de la skill, dicho sin adornos

**Me salté el paso 0.** El flujo de `SKILL.md` dice: «escribe la especificación y **enséñasela al
usuario antes de crear el proyecto**: no hay paso 2 sin este documento escrito primero». Yo
ejecuté `gm-cli init` **antes** de escribir `ESPECIFICACION.md`.

El motivo real: el encargo llegó como una tarea cerrada, sin canal de vuelta, y `13 · 28 §2.2`
—el criterio de parada— está escrito para una conversación («pregunta todo en un turno, como
máximo una repregunta»). Con un encargo de un solo sentido, la regla «pregunta y enseña antes de
crear» **no tiene una forma definida**: no hay a quién preguntar ni a quién enseñar.

Lo resolví aplicando los valores por defecto de `13 · 28 §2.3` a las seis preguntas sin respuesta
y marcándolos `[DEFAULT]` en el bloque 0, que es lo que manda el documento. Pero el orden lo
rompí, y lo dejé anotado en un recuadro dentro de la propia especificación.

**Hueco real de la documentación**: `13 · 28` no cubre el caso «encargo cerrado, sin canal de
vuelta», que es exactamente el caso de un agente lanzado como tarea en vez de como conversación.
Bastaría un párrafo: si no hay canal, se aplican los defaults, se escribe la especificación
igual, y se entrega **con el juego** en vez de antes.

---

## 5 · Lo que funcionó bien (para que no se toque)

Un diario que solo se queja no sirve para decidir qué conservar.

- **Las trece trampas del `§0` de `12 · 09` son el documento más rentable de la biblioteca.**
  Leerlas antes de tocar nada evitó, como mínimo: la fuente muda (12), el *included file*
  fantasma (8), fiarme del `exit 0` (4), y el `--errors-only` que esconde avisos.
- **`buscar.py` con la firma completa.** Verifiqué unos 150 símbolos en cinco lotes. Salvo por lo
  del `--help`, la ficha da exactamente lo que hace falta: firma con los opcionales entre
  corchetes, obsolescencia y la página del manual. **Ni una sola función inventada llegó al
  código**, y las que dudé (`draw_sprite_tiled_ext`, `view_wport`, `save_get_meta`) existían y
  eran lo que decía la ficha.
- **`validar-proyecto.py --todo` cazó un error real** que el compilador tragó con `exit 0`
  (`cangrejo_aplastar()`, una función que nunca escribí). Es la demostración en vivo de por qué
  no es opcional — a pesar del bug de §1.1.
- **Los cuatro scripts de `06 - Assets y Scripts` entraron sin tocar una línea** y compilaron a
  la primera junto al resto. `scr_save_load` en particular es mucho más de lo que yo habría
  escrito: temporal + checksum + copias rotativas + el parche de la Trampa 6.
- **`13 · 09 §8 ter`** (generar `.wav` con el módulo `wave` de Python) resolvió el audio entero
  en veinte minutos, con el código listo para copiar. Los 18 archivos entraron con
  `SOUND SETFILE` a la primera.
- **Ninguna de las dos trampas «de entorno» se manifestó**: `resourcetool` y `compile` no se
  colgaron ni una vez bajo el sandbox desactivado (Trampa 2), y no hubo ni un
  `AccessViolationException` en unas 30 llamadas (Trampa 11). No es prueba de que estén
  arregladas —seguí la mitigación desde el principio—, pero conviene dejarlo escrito.
- **La plantilla *Blank Pixel Game* funcionó** (Trampa 1), en 4,9 s, con su `.mcp.json` y su
  andamiaje.

---

## 6 · Resumen priorizado de los huecos

| # | Hueco | Dónde tocaría | Severidad |
|---|---|---|---|
| 1 | `limpiar()` de `validar-codigo-gml.py` no entiende `\"` y pierde definiciones de función | `_indice/validar-codigo-gml.py` + nota en `12 · 09 §7.5` | **Alta** |
| 2 | `OPTIONS SET` trunca el valor en el primer espacio, sin avisar | `12 · 09 §9 quater`, `07 · 13` | **Alta** |
| 3 | Tamaño de sala y vistas por CLI: sin documentar (y la plantilla deja el puerto a 1366×768) | `12 · 09 §9` (nueva §9.5) | **Alta** |
| 4 | La Trampa 10 solo cubre Windows: en Mac son `icon_png`/`splash_png` y `version` también es de solo lectura | `12 · 09 §9 quater` | Media-alta |
| 5 | No hay receta de «nivel como mapa de texto + constructor», que es la única vía sin IDE | `04 · 01` o documento propio en `04` | Media-alta |
| 6 | `save_get_meta()` devuelve el sobre, no los metadatos: falta el ejemplo de acceso | `06 · scr_save_load.gml`, `13 · 05` n) | Media |
| 7 | `04 · 01 §5` usa camelCase contra la convención de la skill y trae `// placeholder` en el código base | `04 · 01` | Media |
| 8 | No hay receta de fondos con parallax ni la fórmula; `draw_sprite_tiled_ext` repite en dos ejes | `04 · 01 §4.9` o `01 · 11` | Media |
| 9 | `04 · 00 §5` enseña la pausa mala primero y la buena después; falta la vía del interruptor global | `04 · 00 §5` | Media |
| 10 | Reutilizar la cámara de la sala en vez de crear otra, cuando la vista viene activada del `.yy` | `06 · scr_camera.gml` (uso rápido) | Media |
| 11 | Los *included files* se pasan a minúsculas en el paquete | `12 · 09` Trampa 8 | Media |
| 11 bis | `13 · 03 §1.6` (resolución y escala entera) no se alcanza desde la tabla de `SKILL.md` ni desde `04 · 01`; y falta el aviso de que `gpu_set_texfilter(false)` también rompe el texto `.ttf` | `SKILL.md`, `04 · 01 §4.9`, `13 · 03 §1.6` | Media |
| 12 | `13 · 28` no cubre el encargo cerrado sin canal de vuelta | `13 · 28 §2.2` | Media |
| 12 ter | `13 · 10` no tiene lista de «qué mirar leyendo» cuando no se puede ejecutar el juego | `13 · 10 §8` | Media |
| 12 bis | La casilla de pausa de `04 · 00` se puede marcar sin abrir `04 · 41 §4`; el paso 7 de `SKILL.md` no dice que las tres listas enlazadas también se comparan | `04 · 00`, `SKILL.md` §Flujo paso 7 | Media |
| 13 | El lote de `resourcetool script` acepta `#` y no `//` | `12 · 09 §10.1` | Baja |
| 14 | `icon_png` exige exactamente 1024×1024 | `12 · 09 §9 quater` | Baja |
| 15 | `buscar.py --help` no da ayuda | `_indice/buscar.py` | Baja |
| 16 | `SKILL.md` dice 46 recetas; hay 58 | `SKILL.md` | Baja |
| 17 | `options info` devuelve 82 KB y desborda la salida del Bash tool | `12 · 09 §9 quater` | Baja |
