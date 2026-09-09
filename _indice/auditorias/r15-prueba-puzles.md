# r15 · Prueba a ciegas: un juego de puzles cenital, y once cosas que rozaron

> **Encargo, literal**: «Quiero un juego de puzles cenital, tipo mazmorra: empujar bloques,
> placas de presión, llaves y puertas. Con varios niveles y que se vea bien. Para Mac.»
> Sin más información y sin canal de vuelta.
>
> **Fecha**: 2026-09-09 · **Herramientas**: `gm-cli` 2.3.0 · `ResourceTool@2026.0.17` ·
> runtime GMS2 2026.0.0.23 · macOS arm64. **`gm-cli run` estaba prohibido**: el juego no se ha
> ejecutado ni una vez.
>
> **Encargo de método**: usar de verdad el material nuevo y poco rodado —`04 · 58` (el nivel
> como mapa de texto), `04 · 04 §5.2 bis` (interactuar con lo de delante), `04 · 02 §5.9` (la
> máquina de estados), `12 · 09 §5.2` peldaño 2 bis (reparación de assets) y `12 · 09 §3 bis`
> (construir una sala por CLI)— y decir si hace lo que promete.

---

## 1 · Qué se construyó

**«Cripta de las Placas»**, en `~/prueba_r15_puzles/`. Juego completo, no un bucle de juego:

- **Diez cámaras** de puzle, con su curva enseñada por *kishōtenketsu* (`13 · 17 §2.2`):
  la placa (1-3), la llave (4-5), el pozo (6-8) y el examen (9-10). Vocabulario de siete
  piezas: escalera, bloque empujable, placa de presión, puerta de runas, llave, cerradura,
  pozo rellenable, más el cofre con la reliquia opcional.
- **Deshacer ilimitado** (`Z`) por estado completo, reinicio (`R`), contador de pasos contra el
  óptimo real, y una reliquia opcional por cámara.
- **El arco entero de `04 · 00`**: portada saltable, menú con «Continuar» condicionada en
  estado y no en presencia, prólogo saltable, selector de cámaras con marcas y reliquias,
  bucle de juego, pantalla de derrota («Has caído», con deshacer), cierre y créditos.
- **Envoltorio**: pausa que congela el mundo de verdad, opciones (dos volúmenes, pantalla
  completa, idioma, reducir destellos, mostrar pista, borrar progreso), guardado con checksum,
  español e inglés completos, teclado **y** mando.
- **Arte y sonido propios, generados**: 230 fotogramas de pixel art dibujados con Pillow y dos
  fuentes de sprite con tildes y eñes; 16 efectos y un ambiente sintetizados en el arranque.
  Ni un rectángulo de color plano.
- **Un pipeline reproducible** en `herramientas/`: generador de arte, puerta de reparación,
  los diez niveles como mapa de texto, un **solver BFS** que demuestra que son resolubles y
  da su óptimo, el generador que escribe `scr_niveles.gml`, y una maqueta de pantalla.

Recuento: 25 objetos · 16 scripts · 22 sprites · 9 salas · 74 archivos `.gml` · 4 985 líneas.
Cuatro de los scripts son de `06 - Assets y Scripts` copiados **sin tocar una línea**
(`scr_save_load`, `scr_state_machine`, `scr_ui_confirmar`, `scr_math_util`).

### La salida real del último `gm-cli compile` (sin `--errors-only`)

```console
$ cd ~/prueba_r15_puzles/cripta_placas && gm-cli compile
◇  Compiling for mac
│  Options: …/runtime-2026.0.0.23/bin/platform_setting_defaults.json
│  Options: …/cripta_placas/local_settings.json
│  Failed to load Options from …/cripta_placas/local_settings.json
│  Setting up the Asset compiler
│  Found Project Format 2
│  Core Resources : Info - +++ GMSC serialisation:  SUCCESSFUL LOAD AND LINK TIME: 146.105ms
│  Success
│  finished adding assets from …/cripta_placas.yyp.
│  Release build
│  [Compile] Run asset compiler
│  Compile Constants... finished.
│  Remove DnD... finished.
│  Compile Scripts... finished.
│  Compile Rooms... finished..... 0 CC empty
│  Compile Objects... finished.... 0 empty events
│  Global scripts... finished.
│  Final Compile... Final Compile finished.
│  Saving IFF file... …/.gmcache/build-gms2-mac-VM/output/game.zip
│  Stats : GMA : Elapsed=303.972
│  Stats : GMA : sp=22,au=0,bk=0,pt=0,sc=304,sh=0,fo=0,tl=0,ob=25,ro=9,da=0,ex=0,ma=6
│  Igor complete.
◆  Compilation finished

EXIT=0
```

Ni un `error`, ni un `warning`, ni un `WARNING :: datafile … was NOT copied`. La única línea
que un `grep -i error` recoge es la de `local_settings.json`, que es informativa: el archivo no
existe porque nadie ha abierto el proyecto en el IDE.

Y las otras dos comprobaciones, con su salida:

```console
$ python3 "$BIB/_indice/validar-proyecto.py" ~/prueba_r15_puzles/cripta_placas --todo
74 archivos .gml · 1932 llamadas analizadas · runtime del índice 2026.0.0.23
✓ Ninguna llamada a una función del runtime que no exista.
✓ Ninguna llamada a una función del runtime con un número de argumentos que no cuadre con su firma.

$ python3 "$BIB/_indice/auditar-juego-completo.py" ~/prueba_r15_puzles/cripta_placas
… ✓ Menú principal · ✓ Opciones · ✓ Pausa que congela el mundo · ✓ Guardar y cargar ·
  ✓ Créditos · ✓ Muerte / Game Over / cierre · ✓ Sonido · ✓ Mando ·
  ✓ El jugador entra por una sala de portada · ✓ Icono o splash propios ·
  ✓ Todos los objetos que leen entrada consultan alguna guarda
```

---

## 2 · Diario de fricción

Ordenado por lo que más costó, no por lo que más se nota.

### 2.1 🔴 El peldaño 2 bis, aplicado como está escrito, DESTRUYE el arte del peldaño 1

Es el hallazgo más caro de esta sesión, y es una contradicción **dentro de la misma sección**.

`12 · 09 §5.2` dice, en el peldaño 1(b), que dibuje los sprites con Pillow. Y dice, en el
peldaño 2 bis, en negrita y con llave:

> 🔑 **Regla: nada que salga de un generador entra en el juego sin pasar por aquí.** Es un
> comando, no cuesta nada, y es la diferencia entre un sprite que se ve nítido a tamaño real y
> uno que se ve emborronado sin causa aparente.

Un sprite dibujado con Pillow **sale de un generador**. Obedecer esa regla literalmente lo
destruye. Medido sobre `spr_jugador_0.png`, 16×20 px, pixel art a 1:1 con 12 colores:

```console
$ python3 -c "... from pixelfixer import detect ..."
spr_jugador_0 (20, 16, 4) {'step_x': 2.5356891078611556, 'step_y': 2.8464481150110994,
                           'cols': 6, 'rows': 7} 0.86s
spr_muro_0    (16, 16, 4) {'step_x': 2.148, 'step_y': 2.070, 'cols': 7, 'rows': 8}
spr_reliquia_1(16, 16, 4) {'step_x': 3.476, 'step_y': 3.476, 'cols': 5, 'rows': 5}
```

`detect()` afirma que un sprite de 16×20 es en realidad una imagen de 6×7 ampliada ×2,5. Y la
reconstrucción hace lo que dice:

```console
$ ... reconstruct(rgba, r["step_x"], r["step_y"], r["cols"], r["rows"], ...)
entrada (20, 16, 4) -> salida (7, 6, 4)

$ python3 pixeldetector.py -i spr_jugador_0.png -o rep_detector.png
Size detected and reduced from 16x20 to 4x10 in 403 milliseconds
```

Puestas las tres imágenes al lado (original, `pixel-art-fixer`, `pixeldetector`) el resultado no
admite discusión: el original es un personaje con capucha, cara, cinturón y botas; las dos
reparaciones son manchas de 6×7 y de 4×10 píxeles. **Las herramientas no están rotas** —hacen
exactamente lo que anuncian, buscar la rejilla oculta de una imagen ampliada— es la regla la que
no distingue los dos casos.

**Lo que falta en §5.2**: una puerta delante del peldaño 2 bis. Y es barata y determinista:
buscar el mayor `k` tal que reducir la imagen por `k` y volver a ampliarla la reproduce **exacta**.
Si `k == 1`, ya es pixel art de verdad y no hay nada que reparar. Añadiendo dos síntomas más
—número de colores por encima de una paleta, proporción de alfa intermedio— y exigiendo la
**conjunción** (un PNG salido de un modelo trae las tres cosas a la vez), la puerta pasa de
teoría a comando:

```console
$ python3 herramientas/reparar_arte.py
Peldaño 2 bis · 230 fotogramas analizados
  a escala real 1:1 ............ 229 / 230
  máximo de colores por PNG .... 14
  máximo de alfa intermedio .... 80.95 %
  fotogramas que piden reparación: 0
```

Con la disyunción daba dos falsos positivos legítimos: la sombra (81 % de alfa intermedio **a
propósito**) y una puerta de bloques grandes que resulta ser, por casualidad, un aumento exacto
×2. Los dos habrían acabado triturados. Está implementado en
`~/prueba_r15_puzles/herramientas/reparar_arte.py`, listo para copiarse a la sección.

**Dónde arreglarlo**: `12 · 09 §5.2`, peldaño 2 bis. **Severidad: alta.**

---

### 2.2 🔴 `pixel-art-fixer` no arranca por la vía que documenta su propio README

Antes de descubrir lo anterior, hubo que descubrir esto:

```console
$ python3 -m pixelfixer.cli ~/prueba_r15_puzles/assets_fuente/sprites/spr_jugador_0.png
Traceback (most recent call last):
  File "…/pixelfixer/cli.py", line 19, in <module>
    from detector import detect
ModuleNotFoundError: No module named 'detector'
```

El paquete se llama `pixelfixer` y su `__init__.py` exporta `detect`, pero `cli.py` sigue
importando del nombre viejo (`detector`) en sus tres sitios (líneas 19, 34 y 41). El README del
propio repositorio anuncia `python -m pixelfixer.cli input.png` y esa orden no funciona. La
biblioteca lo cita por nombre en `12 · 09 §5.2` y en `07 · 23 §1 bis` sin avisar.

**Rodeo**: la API sí funciona — `from pixelfixer import detect` y
`from pixelfixer.reconstruct import reconstruct`.

**Dónde arreglarlo**: nota en `12 · 09 §5.2` peldaño 2 bis y en `07 · 23 §1 bis`.
**Severidad: media** (la herramienta se recomienda por su CLI y su CLI está rota).

---

### 2.3 🔴 `validar-codigo-gml.py` da por rota una cadena perfecta si el código contiene `case "@":`

Y `"@"` es exactamente el carácter que usa la leyenda de `04 · 58 §2` para el punto de
aparición del jugador. Es decir: **la receta recomendada por la biblioteca dispara un falso
positivo en el validador de la biblioteca.**

Caso mínimo, seis líneas:

```gml
var _c = "x";
switch (_c)
{
    case "@": a++;  break;
    case "S": b++;  break;
}
```

```console
comillas_descuadradas -> [4, 5]
lo que se traga: '@": a++;  break;\n    case "'
```

La causa está en `comillas_descuadradas()`: para no contar las cadenas verbatim usa
`re.sub(r'@"[^"]*"|@\'[^\']*\'', …)`, y ese regex **no comprueba que el `@` no venga precedido
de una comilla**. En `case "@":` lee el `@` pegado a la comilla de cierre como el comienzo de un
`@"…"` y se traga todo hasta la siguiente comilla, dos líneas más abajo. El resultado en el
proyecto real fue:

```console
⚠ 1 archivo(s) con una cadena que NO cierra. GameMaker no
  los compilará, y mientras tanto este análisis pierde lo que venga después:
  scripts/scr_reglas/scr_reglas.gml  ·  línea(s) 72, 73
```

Nada de eso es cierto: el archivo compila y las cadenas están bien. Y el daño no es el aviso,
es que **el análisis del archivo entero se descarta**, justo del archivo donde vive toda la
lógica del juego. Es el mismo tipo de daño que describe el propio docstring de esa función
sobre el caso de `r12`.

**El arreglo es un lookbehind**: `(?<!")@"[^"]*"`. **Rodeo aplicado aquí**: cambiar el carácter
de aparición de `@` a `J` en la leyenda del juego. Es una derrota, no una solución: el `@` es la
convención del género y lo dice la propia receta.

**Dónde arreglarlo**: `_indice/validar-codigo-gml.py`, función `comillas_descuadradas()`.
**Severidad: alta.**

---

### 2.4 🔴 `instance_exists()` devuelve `false` sobre una instancia DESACTIVADA — y la pausa de `04 · 41` desactiva todo

Escribí este código, que parece obviamente correcto, en la acción «Reiniciar cámara» del menú de
pausa:

```gml
if (instance_exists(global.nivel)) reiniciar_nivel(global.nivel);
pausa_cerrar();
```

Y **no hace nada**. Durante la pausa, `pausar_de_verdad()` ha llamado a
`instance_deactivate_all(true)`, y una instancia desactivada existe pero `instance_exists()`
responde que no. El botón se pulsa, suena, el menú se cierra y el nivel sigue exactamente igual,
sin un error ni un aviso. Es la misma familia que las Trampas 5, 6 y 8: compila, corre, y miente.

El arreglo es invertir dos líneas —reactivar primero, comprobar después— pero eso hay que
saberlo. `04 · 41 §3.1.1` describe lo que `instance_deactivate_all` hace (deja de procesar, deja
de dibujar) y no menciona el efecto sobre `instance_exists`, que es el que muerde: **cualquier
acción del menú de pausa que empiece con una guarda `instance_exists` es un no-op silencioso.**

Y hay más superficie de la que parece, porque `buscar_en()`, `placas_evaluar()` y media docena
de funciones de rejilla de este juego usan `instance_exists` internamente: cualquiera de ellas
llamada desde el menú de pausa habría devuelto un mundo vacío.

**Dónde arreglarlo**: `04 · 41 §3.1.1`, un recuadro; y una casilla en su checklist §4.
**Severidad: alta.**

---

### 2.5 🟠 `04 · 58` no dice cómo colocar una instancia cuyo `Create` inicializa su posición

El constructor de la receta hace esto:

```gml
var _inst = instance_create_layer(_px, _py, _capa, obj_moneda);
_inst.indice = _res.creadas_coleccionables++;
```

Funciona porque `indice` no se usa hasta después. En un juego de rejilla, lo natural es que el
objeto derive su posición de su casilla, y ahí se rompe: el `Create` de `obj_bloque` corre
**antes** de que el constructor le escriba `gx`/`gy`, así que se coloca en 0,0 y ahí se queda.
El bloque aparece en la esquina superior izquierda del nivel, encima del muro.

Y el rodeo que uno prueba primero **tampoco vale**: `instance_create_layer` acepta un struct de
variables como quinto argumento, se aplica antes del `Create`… y el propio `Create` lo pisa con
su `gx = 0`. Hay que llamar a un método de recolocación después:

```gml
case "bloque":
    _inst.colocar_ya();          // su Create ya corrió con gx/gy a cero
    array_push(_niv.bloques, _inst);
    break;
```

Media hora entre verlo en la maqueta y entender por qué.

**Dónde arreglarlo**: `04 · 58 §4`, una nota junto al constructor.
**Severidad: media.**

---

### 2.6 🟠 `OPTIONS SET` truncando en el primer espacio SÍ tiene rodeo: comillas dobles

Las «Prohibiciones duras» de la skill listan tres casos medidos en los que la herramienta dice
que sí y no hizo nada, y el primero es «`OPTIONS SET` truncando un nombre en el primer espacio».
Es cierto, y aquí volvió a pasar:

```console
$ gm-cli resourcetool eval "options set platform=mac property=display_name value=Cripta de las Placas"
Set mac.display_name = Cripta
Saved successfully
   -> option_mac_display_name = 'Cripta'
```

Pero **tiene arreglo**, y no está escrito en ningún sitio. Probadas cuatro variantes leyendo el
`.yy` de vuelta cada vez:

| `value=` | Resultado en el `.yy` |
|---|---|
| `Cripta de las Placas` | `'Cripta'` — truncado |
| `"Cripta de las Placas"` | ✅ `'Cripta de las Placas'` |
| `'Cripta de las Placas'` | `"'Cripta"` — peor: se queda la comilla simple |
| `Cripta\ de\ las\ Placas` | `'Cripta\\'` |

**La comilla doble alrededor del valor funciona.** Es una buena noticia que la biblioteca no da.

**Dónde arreglarlo**: `12 · 09` Trampa 10 y §9 quater, y la lista de prohibiciones duras de
`SKILL.md`. **Severidad: media** (corrige una limitación documentada que no lo es).

---

### 2.7 🟠 `OPTIONS GET/SET` usa `PROPERTY=`, no `NAME=`, y equivocarse no da ningún diagnóstico

Cuatro llamadas seguidas fallaron así:

```console
$ gm-cli resourcetool eval "options set platform=mac name=icon_png value=/ruta/icono.png"
Command failed:
npm exec failed with code 1
```

`npm exec failed with code 1` no dice nada. El argumento correcto es `PROPERTY=`, que sí figura
en `help options` — pero la biblioteca, que dedica a `OPTIONS SET` una trampa entera (la 10) y
una sección (§9 quater), habla siempre de **nombres de propiedad** equivocados y nunca del
**nombre del argumento**. Y hay una variante peor, silenciosa:

```console
$ gm-cli resourcetool eval "options get platform=mac name=display_name"
… vuelca las ~30 propiedades de la plataforma, 65 KB …
ResourceTool Successful
```

`OPTIONS GET` **ignora** `name=` sin decir nada y se comporta como si no se hubiera pedido
ninguna propiedad. Con `PROPERTY=`, las tres asignaciones que necesitaba el juego funcionaron a
la primera y se verificaron leyendo `options/mac/options_mac.yy`:

```
option_mac_display_name = 'Cripta de las Placas'
option_mac_icon_png     = '${options_dir}/mac/icons/1024.png'
option_mac_splash_png   = '${options_dir}/mac/splash/splash.png'
```

Y se confirma lo que ya avisaba `05 · 02 §4.4`, con su mensaje exacto:

```console
$ gm-cli resourcetool eval "options set platform=mac property=version value=1.0.0.0"
Property 'version' cannot be set on 'mac' because it is read-only.
```

**Dónde arreglarlo**: `12 · 09 §9 quater` y `05 · 02 §4.4`. **Severidad: media.**

---

### 2.8 🟠 La tercera salida de la Trampa 12 es la buena, y no trae receta

`12 · 09` Trampa 12 propone `font_add_sprite_ext()` como «la que suele ser mejor para un
agente», dice que la hoja de glifos «se puede dibujar con Pillow»… y ahí acaba. Todo lo demás
hubo que resolverlo:

- **Un PNG por sub-imagen**, no una tira: `SPRITE ADDFRAME` añade un fotograma por archivo.
  154 archivos entre las dos fuentes, y **el lote de `resourcetool script` los importó en 2,1 s**
  (230 fotogramas de sprite en total). Por `eval` habrían sido minutos.
- **El espacio necesita una barra sólida**. El manual lo dice de pasada —«puede definir el
  espacio como cualquier carácter que desee, por ejemplo una sola línea del tamaño que desee»,
  y la imagen elegida *nunca* se renderiza— pero si la sub-imagen del espacio va vacía, la
  anchura del espacio la decide el motor y no tú.
- **El `string_map` no puede llevar `"` ni `\`** sin escaparlos, y la propia trampa lo avisa;
  lo que no dice es lo fácil que es evitarlo: se excluyen del mapa y ya. Aquí el mapa son 102
  glifos sin ninguno de los dos caracteres.
- **El mapa del `.gml` y la hoja de glifos tienen que coincidir carácter a carácter.** Si
  divergen, el juego dibuja letras cambiadas y compila igual de limpio. Se comprueba
  programáticamente comparando el `#macro` con la constante del generador:
  `UI gen=102 gml=102 iguales=True`.
- **Rasterizar de una `.ttf` del sistema con umbral duro funciona.** Probadas seis candidatas
  a tamaño pequeño y comparadas mirando el PNG ampliado ×5: *Verdana Bold* a 10 px (UI) y a
  16 px (titulares) da glifos limpios con `á é í ó ú ü ñ Á É Í Ó Ú Ü Ñ ¿ ¡` legibles.
  `» º ª` salieron mal al umbralizar y se quitaron del mapa.

Es la vía correcta y no tiene ni un ejemplo completo. **Dónde arreglarlo**: `12 · 09` Trampa 12,
un bloque de receta; y `13 · 03` si se quiere el detalle de rasterizado.
**Severidad: media.**

---

### 2.9 🟠 Hueco de contenido: no hay nada sobre placas de presión

Buscado como manda la skill, con la salida real:

```console
$ python3 "$BIB/_indice/buscar.py" --todo "placa de presion"
Sin resultados para «placa de presion» en ninguna de las cuatro fuentes.
    Por separado sí aparecen:
      «presion» → 28 documento(s)
      «placa» → 1 documento(s)

$ python3 "$BIB/_indice/buscar.py" --todo "empujar bloques"
Sin resultados para «empujar bloques» en ninguna de las cuatro fuentes.
```

Lo que **sí** hay, y es mucho, aparece buscando por el nombre del género:
`--todo "sokoban"` lleva a `13 · 17 §3` (implementación completa con estado inmutable, empuje,
detección de bloqueos de esquina, solver BFS y A\*, generación validada y deshacer) y a
`04 · 37 §3.10` (una segunda versión más ligera, enganchada a un `objPlayer` real). El deshacer
de `13 · 17 §3.6` se usó tal cual y es exactamente el patrón correcto.

Lo que no existe es la otra mitad del encargo: **placa de presión, puerta que abre un circuito
de placas, llave y cerradura**. Se generalizan sin dificultad desde el concepto de «meta» de
Sokoban —una placa es una meta que acepta caja **o** jugador y dispara un evento en vez de
contar para la victoria— pero eso lo tuvo que decidir el agente.

Y hay un segundo hueco más pequeño, señalado también por la búsqueda: **no existe receta de
«reiniciar el nivel»**. Es una línea con el patrón de estado inmutable, pero no está escrita.

**Dónde arreglarlo**: una sección en `04 · 07` o un documento nuevo en `04`, enlazado desde
`13 · 17 §1.2` (que ya nombra la familia «espacial / empuje»). **Severidad: media.**

---

### 2.10 🟡 Sin `run`, falta el escalón intermedio entre «compila» y «se ve bien»

`13 · 10 §8.6` procedimiento 1 dice: dispara la captura, **abre el PNG y míralo**. Sin `run` no
hay PNG. `§8.7` da la red de las seis preguntas, que es una lectura del código. Entre las dos
falta un escalón, y resultó ser el más productivo de la sesión.

Lo que hice fue **componer la pantalla en Python** con los mismos PNG, la misma rejilla, el mismo
bitmask del muro, el mismo orden de dibujo, la misma fuente de sprite y el mismo encaje de
cámara que `obj_nivel` — `herramientas/maqueta.py`, 150 líneas. No es una captura del juego y el
propio archivo lo dice en su cabecera: no comparte una sola línea de GML. Pero **cazó dos fallos
reales que ni el compilador, ni `validar-proyecto.py`, ni las seis preguntas vieron**:

1. **El nivel no quedaba centrado.** En `camara_encajar()`, el término que descuenta la franja
   del HUD iba **sumando** cuando tiene que restar. El tablero quedaba pegado al HUD con una
   banda vacía de 45 px abajo. Es un signo, y leyendo el código pasa desapercibido.
2. **La pista del nivel se salía de la pantalla por los dos lados.** La más larga son 58
   caracteres y el panel se dibujaba a `string_width(texto) + 14` sin acotar contra los 320 px
   de ancho. Se ve de un vistazo en la maqueta y no se ve leyendo.

Ninguno de los dos es un símbolo inventado ni un error de sintaxis, que es justo el punto de
`§8.7`. Propongo documentarlo como **procedimiento 1 bis**: cuando no se puede ejecutar,
reconstruir la pantalla con los assets desde fuera del motor, mirarla, y decir con todas las
letras que es una maqueta.

**Dónde arreglarlo**: `13 · 10 §8.6`. **Severidad: media** (es una oportunidad, no un defecto).

---

### 2.11 🟡 `gm-cli compile --errors-only` no distingue «compiló bien» de «no hizo nada»

Sobre un proyecto recién creado, la primera compilación devolvió esto:

```console
$ gm-cli compile --errors-only ; echo "EXIT=$?"
EXIT=0
```

Ni una línea. Siete segundos. Con 2 000 líneas de GML nuevo, «no ha dicho nada» y «no ha mirado
nada» se leen igual, y `§7.7` ya avisa de que ese flag esconde cosas. La única forma de saberlo
fue **romperlo a propósito**:

```console
$ printf 'function prueba() { var _x = ; }\n' >> scripts/scr_ui/scr_ui.gml
$ gm-cli compile --errors-only
Command failed:
gml_GlobalScript_scr_ui(279) : unexpected symbol ";" in expression
GMAssetCompiler.dll exited with non-zero status (1)
```

Confirmado: el compilador sí ve el código, y el silencio anterior era silencio de éxito. Merece
estar escrito, porque el reflejo contrario —dar por bueno un `exit 0` mudo— es exactamente lo
que la biblioteca lleva cuatro trampas intentando desactivar.

**Dónde arreglarlo**: `12 · 09 §7.7`, un párrafo. **Severidad: baja.**

---

### 2.12 🟡 Dos falsos positivos de `auditar-juego-completo.py`, y uno que no lo era

Con la salida real, para que se pueda calibrar el detector:

- **`obj_seleccion` marcado como «objeto SIN sprite que pinta figuras en su Draw».** Es la
  pantalla de selección de cámara: una rejilla de paneles de UI. El propio script clasificó bien
  a `obj_creditos`, `obj_intro`, `obj_nivel` y `obj_splash` como «objetos de interfaz», y a este
  no. Falso positivo, comprobado. **Severidad: baja.**
- **«11 llamadas a `show_debug_message`».** Después de montar el registro por niveles de
  `13 · 10 §7.2`, las que quedan están dentro de `scr_save_load` (rutas de error), de
  `scr_state_machine` y del propio `registrar()`, que es quien las apaga. Contar ocurrencias del
  nombre no distingue una traza de depuración de un canal de error. **Severidad: baja.**
- **«`obj_jugador` lee entrada SIN ninguna guarda de pausa/transición»** — este **no** era un
  falso positivo del todo. Es cierto que hoy no puede pasar (la pausa desactiva instancias), pero
  la invariante era global y frágil: si mañana alguien llama a `ir_a_escena` desde el propio
  jugador, `instance_deactivate_all(true)` lo dejaría activo. Se añadió la guarda. **El detector
  tenía razón por un motivo distinto del que dice.**

---

## 3 · Sobre el material que el encargo pedía estrenar

| Material | ¿Hace lo que promete? |
|---|---|
| **`04 · 58` · el nivel como mapa de texto** | **Sí, y es lo mejor de la sesión.** Diez niveles rediseñados decenas de veces sin tocar una sala. La validación previa (`nivel_validar`) cazó tres mapas mal formados antes de que existiera el proyecto. El ahorro de roca enterrada es real. Le falta la nota de 2.5. |
| **`04 · 04 §5.2 bis` · usar lo de delante** | **Sí, tal cual.** El punto a distancia fija en la dirección de mirada se comporta como el jugador espera; el aviso de que un interactuable sin sprite es invisible para `instance_position()` evitó el bug antes de escribirlo; y el patrón `recien_cerrado` es lo que impide que la misma pulsación cierre y reabra un cartel. Cinco clases de interactuable colgando de un solo padre, y la función no cambió ni una vez. |
| **`04 · 02 §5.9` · la máquina de estados** | **Sí, con un matiz.** `fsm_bind` sobre `06 · scr_state_machine.gml` funciona sin tocarlo, y el azúcar de `self` es real. El matiz: la receta propone un estado `transicion`, y aquí **no hace falta** porque la transición desactiva instancias (`04 · 41`). Dos mecanismos para lo mismo; convendría que `§5.9` dijera cuál usar cuándo. |
| **`12 · 09 §5.2` peldaño 2 bis** | **No.** Ver 2.1 y 2.2. La herramienta principal no arranca por su CLI y la regla, obedecida, destruye el arte. |
| **`12 · 09 §3 bis` · construir una sala por CLI** | **Sí, exactamente.** 34 líneas de lote y la sala quedó con 480×320, `enableViews`, el viewport de 320×180, los bordes y `objectId = obj_jugador`, todo verificado leyendo el `.yy`. Las tres reglas del árbol de expresiones se cumplen. Lo único que el seguimiento del motor no sabe hacer es **centrar un nivel más pequeño que la vista**, así que hubo que quitarle el objetivo con `camera_set_view_target(cam, noone)` y calcular la cámara a mano; el viewport por CLI sigue siendo el que define la sala. |

Y dos herramientas más que funcionaron sin fricción: **`resourcetool script`** (230 fotogramas
en 2,1 s; sin él esto no se acaba) y el **orden de las salas por orden de creación** (`§9.2`),
que salió bien a la primera y evitó tocar `RoomOrderNodes`.

---

## 4 · Dónde me salté un paso de la skill

Lo digo yo, no lo ha detectado nadie.

1. **Paso 0 · la especificación antes del proyecto.** No la enseñé antes de crear nada. El
   encargo llegó cerrado y sin canal de vuelta, que es el único caso en que `13 · 28 §2.2 bis`
   autoriza el cambio de orden: apliqué los valores por defecto, escribí la especificación
   igual, marqué cada asunción con `[DEFAULT]` y la entrego **con** el juego, en
   `~/prueba_r15_puzles/ESPECIFICACION.md`. Está declarado ahí y aquí.
2. **Paso 4 · `11 - Código descargado/_CATALOGO.md` antes de escribir un sistema. Este sí me lo
   salté.** Fui directo a `06 - Assets y Scripts` —de donde reutilicé cuatro scripts sin tocar
   una línea— y escribí de cero `scr_input`, `scr_idioma` y `scr_ui`. Mirando el catálogo
   después: **`Input`** (offalynne, MIT, el estándar de facto) cubre lo que hace mi `scr_input`
   con muchísimo más alcance, y hay una carpeta `interfaz-de-usuario` y otra `localizacion` que
   no abrí. Para un juego de 320×180 con seis acciones, 150 líneas propias frente a una
   dependencia de 344 archivos me sigue pareciendo la decisión correcta — pero **la decisión no
   la tomé, me la salté**, que es distinto.
3. **No ejecuté el juego** porque estaba prohibido, y eso deja sin comprobar todo lo que
   `12 · 09 §4.2` clasifica como dependiente de vista, oído o hardware. En concreto y por
   nombre: que la fuente de sprite dibuje de verdad las tildes en pantalla (el fallo de la
   Trampa 12 solo se ve mirando), que el guardado sobreviva a cerrar el proceso (procedimiento 2
   de `13 · 10 §8.6`), que el sonido sintetizado no chasque en la costura del bucle, y que el
   deslizamiento de 7 fotogramas se sienta bien. Todo eso está sin verificar y así consta en
   `~/prueba_r15_puzles/DIARIO-DE-CIERRE.md`.

---

## 5 · Comprobación de símbolos

Cada función de GML nombrada en este documento y en el código se pasó por `buscar.py` **antes**
de escribirla, en lotes: `instance_create_layer`, `instance_position`, `instance_activate_object`,
`instance_deactivate_all`, `font_add_sprite_ext`, `font_delete`, `audio_create_buffer_sound`,
`audio_free_buffer_sound`, `audio_sound_pitch`, `audio_is_playing`, `buffer_create`,
`buffer_write`, `buffer_delete`, `camera_set_view_target`, `camera_set_view_pos`,
`view_get_camera`, `camera_get_view_width`, `surface_copy`, `surface_resize`,
`sprite_create_from_surface`, `display_set_gui_size`, `window_set_fullscreen`,
`gpu_set_texfilter`, `game_get_speed`, `string_height_ext`, `draw_text_ext`,
`draw_line_width_color`, `draw_sprite_ext`, `merge_color`, `os_get_language`, `string_lower`,
`string_upper`, `variable_global_exists`, `draw_get_valign`, `event_inherited`, `array_delete`,
`array_pop`, `is_callable`, `struct_get_names`, `keyboard_clear`, `gamepad_axis_value`,
`randomize`, `frac`, `window_center`, `display_get_width`, `layer_exists`, `sprite_get_number`,
más las constantes `gp_axislh`, `gp_axislv`, `gp_face1`, `gp_padr`, `gp_start`, `vk_backspace`,
`buffer_fast`, `audio_mono`.

**Y sí: estuve a punto de escribir una que no existe.** Al montar el gestor de escenas iba a
apoyarme en una función de transición del motor, del tipo `transition_define`/`transition_set`,
por analogía con otros motores. No llegó al código porque `04 · 00 §2` lo dice en un recuadro
—«GameMaker no tiene una función de transición entre salas (`transition_define` **no existe** en
este runtime)»— y esa frase estaba en el mismo documento que estaba leyendo para montar el arco.
El fundido se dibuja a mano, que es lo que hace `scr_escenas.gml`.

Comprobado también que no existe: `sprite_set_interpolation`, la que el propio `SKILL.md` usa
como ejemplo del fallo que esta biblioteca existe para impedir.

---

## 6 · Tabla priorizada de huecos

| # | Hueco | Dónde arreglarlo | Severidad |
|---|---|---|---|
| 1 | El peldaño 2 bis, obedecido, **destruye** el arte del peldaño 1(b). Falta la puerta que distingue «pixel art falso» de «pixel art a 1:1» — implementada y lista para copiar en `herramientas/reparar_arte.py` | `12 · 09 §5.2`, peldaño 2 bis | **Alta** |
| 2 | `comillas_descuadradas()` da por rota una cadena perfecta si el código contiene `case "@":` — y `"@"` es la leyenda que recomienda `04 · 58 §2`. Arreglo: lookbehind `(?<!")@"[^"]*"` | `_indice/validar-codigo-gml.py` | **Alta** |
| 3 | `instance_exists()` responde `false` sobre una instancia **desactivada**, y la pausa recomendada desactiva todo: cualquier acción del menú de pausa con esa guarda es un no-op silencioso | `04 · 41 §3.1.1` + casilla en su §4 | **Alta** |
| 4 | `pixel-art-fixer` no arranca por su CLI (`from detector import detect`, paquete renombrado a `pixelfixer`). La API sí funciona | `12 · 09 §5.2` y `07 · 23 §1 bis` | Media |
| 5 | La tercera salida de la Trampa 12 (`font_add_sprite_ext`) es la buena para un agente y no trae receta: un PNG por glifo, barra sólida en el espacio, mapa sin `"` ni `\`, y verificar que mapa y hoja coinciden | `12 · 09` Trampa 12 | Media |
| 6 | No hay nada sobre **placas de presión** ni sobre **reiniciar un nivel**; Sokoban sí está bien cubierto (`13 · 17 §3`, `04 · 37 §3.10`) | `04 · 07` o documento nuevo en `04`, enlazado desde `13 · 17 §1.2` | Media |
| 7 | El truncamiento de `OPTIONS SET` en el primer espacio **sí tiene rodeo**: comillas dobles alrededor del valor. Documentado hoy como limitación sin salida | `12 · 09` Trampa 10 y §9 quater; prohibiciones de `SKILL.md` | Media |
| 8 | `OPTIONS GET/SET` usa `PROPERTY=`, no `NAME=`; equivocarse da `npm exec failed with code 1`, y `GET` **ignora** `name=` en silencio y vuelca 65 KB | `12 · 09 §9 quater` | Media |
| 9 | Falta el escalón entre «compila» y «se ve bien» cuando no se puede ejecutar: componer la pantalla desde fuera del motor con los mismos assets. Cazó dos fallos reales aquí | `13 · 10 §8.6`, procedimiento 1 bis | Media |
| 10 | `04 · 58 §4` no avisa de que el `Create` de la instancia corre **antes** de que el constructor le escriba `gx`/`gy` — y de que el struct de `instance_create_layer` tampoco salva, porque el `Create` lo pisa | `04 · 58 §4` | Media |
| 11 | `04 · 02 §5.9` propone un estado `transicion` que se solapa con la pausa de `04 · 41`: dos mecanismos para lo mismo, sin decir cuál usar cuándo | `04 · 02 §5.9` | Baja |
| 12 | `gm-cli compile --errors-only` con éxito es indistinguible de un no-op: cero salida, `exit 0` | `12 · 09 §7.7` | Baja |
| 13 | `auditar-juego-completo.py`: `obj_seleccion` clasificado como «objeto sin sprite que pinta figuras» siendo UI; y el recuento de `show_debug_message` no distingue traza de canal de error | `_indice/auditar-juego-completo.py` | Baja |
| 14 | `gm-cli init -n` rechaza nombres con espacios («Use only letters, numbers, dashes, and underscores») y la tabla de comandos de `SKILL.md` no lo dice | `SKILL.md`, tabla de comandos | Baja |
