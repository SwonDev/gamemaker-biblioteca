# 01 · Herramientas del flujo de trabajo

> Programas y utilidades que trabajan **sobre el proyecto o sobre el IDE**, no dentro del
> juego. Editores, formateadores, analizadores, compilación por línea de comandos, tests y
> documentación.
>
> Datos de GitHub verificados por API el 1 de septiembre de 2026 (★ estrellas · fecha del
> último cambio · licencia). Lo que está descargado lleva su ruta local.

---

## 1. Editar código fuera del IDE

### GMEdit ★369 · MIT · 2026-07-22 · [repo](https://github.com/YellowAfterlife/GMEdit) · [itch](https://yellowafterlife.itch.io/gmedit)

**El editor alternativo de referencia.** Autocompletado, navegación por definición, búsqueda
global, plegado, múltiples cursores y soporte de proyectos de GameMaker 1.4, 2.x y actuales.

📁 Descargado: `11 - Código descargado/herramientas/GMEdit/`

**Plugin recomendado:** [GMEdit-Constructor](https://www.gamemakerkitchen.com/plugins) —
compilación con Igor directamente desde GMEdit, sin volver al IDE.

> 💡 En LTS 2026 el motivo para usar GMEdit se ha reducido: el **Code Editor 2** del IDE
> (activable en Preferencias, marcado como Beta) trae plegado, diagnósticos y un servidor de
> lenguaje propio. Ver [`02 - Novedades 2026/09`](../02%20-%20Novedades%202026/09%20-%20Code%20Editor%202%20y%20Feather.md).
> Prueba primero el editor nuevo; si te falta algo, entonces GMEdit.

### Stitch for VSCode · Bscotch · [repo](https://github.com/bscotch/stitch) ★158 · 2026-06-15

Editar proyectos de GameMaker **desde Visual Studio Code**. Parte del ecosistema *Stitch* de
Butterscotch Shenanigans (los de *Crashlands*), que además incluye una CLI para automatizar
tareas sobre el `.yyp`.

📁 Descargado: `11 - Código descargado/librerias/herramientas-externas/stitch/`
🔗 Extensión: <https://marketplace.visualstudio.com/items?itemName=bscotch.bscotch-stitch-vscode>

### vim-gml · MIT · [repo](https://github.com/JafarDakhan/vim-gml)

Resaltado de sintaxis de GML para Vim y Neovim.
📁 `11 - Código descargado/librerias/herramientas-externas/vim-gml/`

---

## 2. Formatear y analizar el código

### Gobo ★33 · MIT · 2025-11-21 · [repo](https://github.com/Pizzaandy/Gobo)

**Formateador de GML con opinión propia**, al estilo de Prettier. Le pasas el archivo y te lo
devuelve con un estilo consistente. Se acabó discutir dónde va la llave.

📁 `11 - Código descargado/librerias/depuracion/Gobo/`

**Fork con más opciones:** [GoboCat](https://github.com/EttyKitty/GoboCat) (MIT, 2026-07-22) —
menos dogmático, más configurable.
📁 `11 - Código descargado/librerias/depuracion/GoboCat/`

### duck ★14 · Apache-2.0 · 2025-06-05 · [repo](https://github.com/imlazyeye/duck)

**Analizador estático de GML**: aplica reglas de estilo y detecta errores antes de compilar.
Complementa a Feather, no lo sustituye.
📁 `11 - Código descargado/librerias/depuracion/duck/`

> 💡 **Antes de instalar ninguno de los dos**, activa **Feather** (viene activado por defecto
> en LTS 2026) y configura sus *reglas de nomenclatura* en Preferencias. Cubre buena parte de
> lo que hacen estas herramientas, sin dependencias.

---

## 3. Compilar y automatizar

### El CLI oficial: `gm-cli` ★39 · Apache-2.0 · 2026-08-17 · [repo](https://github.com/YoYoGames/gm-cli)

Es **la vía oficial** y la que usa esta biblioteca. Documentado al detalle en
[`07 - Ecosistema/13 · GM CLI`](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md).

```sh
gm-cli init | run | compile | package
gm-cli manual read "<tema>"
gm-cli resourcetool eval | repl | mcp
```

📁 `11 - Código descargado/plantillas_y_ejemplos/gm-cli/`

### Rubber ★33 · MIT · 2021-02-20 · [repo](https://github.com/GameMakerDiscord/Rubber)

Compilación desde línea de comandos anterior al CLI oficial, escrita en JavaScript.
⚠️ **Sin cambios desde 2021.** Hoy usa `gm-cli`. Se conserva por valor histórico y porque
explica bien cómo funciona **Igor**, el compilador real que hay debajo.
📁 `11 - Código descargado/librerias/herramientas-externas/Rubber/`

### YYP Maker · Sohom Sahaun · [itch](https://sahaun.itch.io/yyp-maker) · gratis

Herramienta de **reparación de proyectos**: regenera y limpia el `.yyp` cuando se corrompe.
Muy útil tras un conflicto de *merge* mal resuelto en Git.

> ⚠️ Recuerda la regla de esta biblioteca: **nunca edites `.yy` ni `.yyp` a mano.** Si están
> rotos, usa YYP Maker o `gm-cli resourcetool`.

### GM Code Exporter · Sohom Sahaun · [Kitchen](https://www.gamemakerkitchen.com/tools)

Exporta todo el código de un proyecto a un fichero de texto. Útil para revisiones, para
buscar con `grep` o para pasarle el proyecto entero a un modelo de lenguaje.

---

## 4. Probar el código

| Herramienta | ★ | Licencia | Estado | Qué es |
|---|---:|---|---|---|
| [**GM-TestFramework**](https://github.com/YoYoGames/GM-TestFramework) | 25 | propia | 2026-08-25 | **El oficial de YoYo Games.** Es el que usa el propio equipo del motor |
| [**crispy**](https://github.com/bfrymire/crispy) | 40 | MIT | 2025-11-26 | Framework de pruebas unitarias escrito en GML, específico para LTS |
| [**gm-verrific**](https://github.com/Alphish/gm-verrific) | 5 | MIT | 2025-10-12 | Pruebas automatizadas, el más ambicioso de los de la comunidad |
| [**olympus**](https://github.com/bscotch/olympus) | 21 | MIT | 2024-05-13 | Framework de pruebas de Bscotch |
| [**ganary**](https://github.com/bscotch/ganary) | 10 | — | 2026-08-31 | Pruebas de regresión sobre Olympus |
| [**gms2-test**](https://github.com/pmarincak/gms2-test) | 28 | MIT | 2022-12-27 | Pruebas unitarias, sencillo |
| [**GMBenchmark**](https://github.com/DragoniteSpam/GMBenchmark) | 34 | MIT | 2026-08-18 | **Mide el coste real** de una función. Úsalo antes de optimizar a ciegas |

📁 Todos descargados en `11 - Código descargado/` (los cuatro últimos bajo
`librerias/depuracion/`, el oficial bajo `plantillas_y_ejemplos/`).

> **Recomendación:** empieza por **GM-TestFramework** (es oficial y se mantiene) o **crispy**
> (es el más vivo de los de la comunidad).

---

## 5. Depurar en tiempo de ejecución

| Herramienta | ★ | Qué hace |
|---|---:|---|
| [**rt-shell**](https://github.com/daikon-games/rt-shell) | 96 | **Consola dentro del juego**: comandos propios, historial, sugerencias y metadatos. Lo más útil de esta lista |
| [**Snitch**](https://github.com/JujuAdams/Snitch) | 39 | Captura de *crashes* y registro para juegos ya publicados |
| [**Lookout**](https://github.com/glebtsereteli/Lookout) | 21 | Vistas de depuración superpuestas |
| [**Inspectron**](https://github.com/shdwcat/Inspectron) | 16 | API fluida para construir vistas de depuración |
| [**meta**](https://github.com/nommiin/meta) | 8 | Inspector de assets en tiempo de ejecución |
| [**Debug log server**](https://yellowafterlife.itch.io/gamemaker-netlog) | — | Ventana externa de log (gratis, itch.io) |

📁 En `11 - Código descargado/librerias/depuracion/`.

> El motor ya trae **Debug Overlay** y depurador propio. Ver
> [`01 - Fundamentos/15 · Depuración y rendimiento`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md).
> `rt-shell` añade lo que el motor no da: ejecutar comandos tuyos con el juego corriendo.

---

## 6. Documentar el proyecto

### Tome ★14 · MIT · 2026-05-12 · [repo](https://github.com/CataclysmicStudios/Tome)

Genera **sitios de documentación automáticamente** a partir del JSDoc de tu código GML. Si
escribes una librería para otros, es lo que quieres.
📁 `11 - Código descargado/librerias/extras/Tome/`

> Escribir JSDoc en GML dejó de ser opcional en 2026: Feather lo usa para inferir tipos.
> Ver [`05 - Referencia/04 · Convenciones y estilo GML`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md).

---

## 7. Ejecutar código en tiempo de ejecución (scripting y modding)

**Antes de traer un lenguaje embebido, pregúntate si te hace falta de verdad.** Un intérprete es
una superficie de ataque permanente (código de un tercero corriendo dentro de tu proceso), una
pieza más que mantener actualizada, y varias semanas de trabajo si lo escribes tú. Lo necesitas
cuando el contenido tiene que **cambiar sin recompilar y con lógica propia**: reglas que el
jugador edita a mano (mods de verdad, no solo reskins), contenido de temporada que publicas entre
builds sin pasar por `gm-cli compile` cada vez, o un sistema de modding donde terceros distribuyen
scripts ([04 · 43](../04%20-%20Recetas%20por%20g%C3%A9nero/43%20-%20Modding%20y%20contenido%20externo.md),
ya escrito). Si lo único que cambia son **números y estructuras** —una tabla de
stats, un árbol de diálogo, un catálogo de objetos, un nivel entero descrito como datos— **basta
con JSON**: lo carga tu propio código con `json_parse` sobre un catálogo dirigido por datos, cero
sandboxing, cero superficie de ataque, y ya está documentado y verificado en
[13 · 06 §3.8 — Datos dirigidos: definir el juego en JSON](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#38-datos-dirigidos-definir-el-juego-en-json).
Entre ambos extremos hay un escalón intermedio para aritmética condicional sin variables con
nombre ni bucles: el intérprete **Bytecode** de
[13 · 23 §3.7](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/23%20-%20Cat%C3%A1logo%20de%20patrones%20en%20GML.md#37-bytecode-un-intérprete-mínimo),
que cabe en un script propio y no puede colgarse porque el lenguaje no tiene forma de expresar un
bucle infinito.

| Herramienta | ★ | Qué es |
|---|---:|---|
| [**catspeak-lang**](https://github.com/katsaii/catspeak-lang) | 133 | **Lenguaje de modding multiplataforma** para juegos de GameMaker. Es la opción seria si quieres que tus jugadores escriban scripts |
| [**JITSpeak**](https://github.com/BenjaminUrquhart/JITSpeak) | 3 | Compilador *just-in-time* de Catspeak a bytecode de la VM |
| [**GMLC**](https://github.com/tinkerer-red/GMLC) | 18 | VM y compilador de GML escritos **en GML** |
| [**GMLVM**](https://github.com/erkan612/GMLVM) | 5 | Intérprete de GML en tiempo de ejecución |
| [**RunGML**](https://github.com/sdelaughter/RunGML) | 10 | Lenguaje tipo Lisp embebido en GameMaker |
| [**Apollo**](https://yellowafterlife.itch.io/gamemaker-lua) 💸 $14,95 | — | Ejecutar **Lua** en Win/Mac/Linux |
| [**LuaMancer**](https://progrstick.itch.io/luamancer) gratis | — | Extensión de **Luau** para GameMaker |

📁 En `11 - Código descargado/librerias/utilidades/` (catspeak-lang, RunGML, JITSpeak) y `11 - Código descargado/librerias/herramientas-externas/` (GMLC, GMLVM).

**Ejemplo mínimo de catspeak-lang** (API externa, no aparece en `buscar.py`: no es GML del
motor — verificado contra su documentación pública 3.2.0, no contra código local, como ya explica
`04 · 43 §3.6`):

```gml
var _entorno = new CatspeakEnvironment();
_entorno.interface.exposeFunction("duplicar", function(_n) { return _n * 2; });

var _ir  = _entorno.parseString("duplicar(21)");
var _fn  = _entorno.compile(_ir);
show_debug_message(_fn());   // 42
```

Esto es solo el arranque del lenguaje: qué exponer y qué no exponer nunca a ese entorno, el límite
de tiempo por script y el resto del sandboxing real están en
[04 · 43 §3.6 — Ejecutar código del jugador sin abrir un agujero](../04%20-%20Recetas%20por%20g%C3%A9nero/43%20-%20Modding%20y%20contenido%20externo.md#36-ejecutar-código-del-jugador-sin-abrir-un-agujero-catspeak-lang).

---

## 8. Recarga en caliente (*live coding*)

### GMLive.gml 💸 $29,95 · YellowAfterlife · [itch](https://yellowafterlife.itch.io/gamemaker-live)

**Recarga de código y assets sin recompilar.** Cambias una función, guardas, y el juego que
está corriendo la coge al vuelo. Es de pago y es, con diferencia, la herramienta que más
tiempo ahorra en un proyecto grande.

⚠️ No está descargada (es comercial). Es la única recomendación de pago de esta biblioteca
junto con los assets de itch.io.

---

## 9. Temas del IDE

| Tema | Repo |
|---|---|
| **Dracula** | <https://github.com/dracula/gamemaker-studio> |
| **Gruvbox** | <https://github.com/heygleeson/Gruvbox-GMTheme> |

📁 Gruvbox descargado en `11 - Código descargado/librerias/extras/Gruvbox-GMTheme/`.

---

## 10. Utilidades sueltas que resuelven un dolor concreto

| Utilidad | Dolor que quita |
|---|---|
| [**GM-RoomInspector**](https://github.com/heygleeson/GM-RoomInspector) | Vuelca los datos de una room a JSON para leerlos fuera del IDE |
| [**MultiClient**](https://github.com/tabularelf/MultiClient) | Lanza **varias instancias del juego a la vez** para probar red sin dos ordenadores |
| [**GMRuntimeLock**](https://chamaeleon.itch.io/gmruntimelock) | Impide que se abran dos copias del juego |
| [**GMSDLL**](https://github.com/YAL-GameMaker/GMSDLL) / [**GMSDLL.rs**](https://github.com/YAL-GameMaker/GMSDLL.rs) | Plantillas para escribir extensiones nativas en **C++** y en **Rust** |
| [**Shadertoy2GM**](https://github.com/jfkn1ght/Shadertoy2GM) | Convierte GLSL de Shadertoy a shaders de GameMaker |
| [**Xpanda**](https://github.com/GameMakerDiscord/Xpanda) | `#include` en shaders: reutilizar código GLSL entre ficheros |
| [**Win7 patcher**](https://yellowafterlife.itch.io/gm2024-win7-patcher) | Hace que los juegos de GM 2024.11+ arranquen en Windows 7 |
| [**GMS2_RPC / GameMaker Companion**](https://github.com/Mtax-Development/GMS2_RPC) | Discord Rich Presence mientras desarrollas |

📁 Rutas exactas de cada uno en [`11 - Código descargado/_RUTAS.json`](../11%20-%20C%C3%B3digo%20descargado/_RUTAS.json): `GM-RoomInspector` → `niveles-y-mapas`, `MultiClient` → `red-y-multijugador`, `GMSDLL` y `GMSDLL.rs` → `extensiones-nativas`, `Shadertoy2GM` y `Xpanda` → `shaders`, `GMS2_RPC` → `integraciones`.

---

## Fuentes

- awesome-gamemaker: <https://github.com/bytecauldron/awesome-gamemaker> (501 ★, 2026-08-23)
- GameMaker Kitchen · Tools: <https://www.gamemakerkitchen.com/tools>
- GameMaker Kitchen · Plugins: <https://www.gamemakerkitchen.com/plugins>
- itch.io · herramientas: <https://itch.io/tools/tag-gamemaker>
- Metadatos de cada repositorio: API de GitHub, 1 de septiembre de 2026
