---
name: gamemaker-biblioteca
description: "Úsala ante cualquier cosa de GameMaker o GML: «hazme un juego», «no compila», «se comporta raro», archivos .yyp/.yy/.gml, gm-cli, resourcetool, publicar un juego. Fuente fidedigna para LTS 2026: verifica cada símbolo antes de escribirlo (¿existe?, firma, obsoleta, manual) y trae las trampas del CLI que hacen fracasar a un agente. Cubre el desarrollo entero — diseño y GDD, niveles, arte y animación, VFX y shaders, UI/UX y accesibilidad, cámaras, arquitectura, procedural, físicas, combate, IA, pathfinding, progresión, sonido, narrativa, testing, producción, móvil y 3D — y la publicación: firmar, notarizar, Steam, Play, App Store y consolas."
---

# GameMaker · biblioteca fidedigna

Una base de conocimiento local, en español, verificada contra el runtime instalado. Existe
para que el GML que escribas **no invente nada** y para que cada decisión de diseño tenga
detrás un documento contrastado.

**Lo primero de todo, una sola vez por sesión**, y no solo la asignación: también la
comprobación. Copia las dos líneas tal cual.

```sh
BIB="${GM_BIBLIOTECA:-$(cat ~/.config/gamemaker-biblioteca/ruta 2>/dev/null)}"
if   [ ! -f "$BIB/_indice/buscar.py" ];   then echo "✗ SIN biblioteca (BIB=«$BIB») → usa gm-cli manual read para cada duda de API, y NUNCA la memoria."
elif [ ! -f "$BIB/_indice/simbolos.json" ]; then echo "⚠ biblioteca en $BIB, pero SIN índice de símbolos → los documentos sirven; para verificar firmas, gm-cli manual read."
else echo "✓ biblioteca completa en $BIB"; fi
```

`$BIB` abre **cada** comando de esta skill: la biblioteca está donde la instalaron, no en una
ruta fija. La escribe `instalar.sh` al copiar la skill; `$GM_BIBLIOTECA` la pisa si hace falta.

**La segunda línea existe porque sin ella el fallo es mudo.** Si la ruta está vacía —o guardada
pero ya no existe, que es peor— el primer `python3 "$BIB/_indice/buscar.py"` responde
`can't open file '/_indice/buscar.py'`: un error de Python que no dice nada sobre qué hacer, y
que un agente interpreta como «la herramienta está rota» en vez de «la biblioteca no está aquí».

- **`✓`** → todo lo de abajo funciona tal cual.
- **`⚠`** → la biblioteca está, pero le falta el índice de símbolos, que se genera del
  **runtime instalado** (un clon recién bajado de GitHub sin GameMaker en la máquina está así).
  Los 270 documentos, las recetas y los validadores funcionan; lo que no funciona es
  `buscar.py <símbolo>`. Para verificar una firma usa `gm-cli manual read "<símbolo>"`, y si
  hay GameMaker instalado arréglalo de una vez con `python3 "$BIB/_indice/actualizar.py"`.
- **`✗`** → **dilo en tu respuesta** y cae a `gm-cli manual read "<símbolo>"` para cada duda de
  API. **Nunca a la memoria.** Todo lo que esta skill dice sobre trampas del CLI, convenciones y
  flujo sigue siendo válido; lo que pierdes es el buscador y los documentos.

La distinción entre `⚠` y `✓` no es cosmética: comprobar solo que existe `buscar.py` daba un
`✓` sobre un clon donde el comando principal no podía responder.

## La regla que gobierna todo

**Cada símbolo de GML se verifica antes de escribirlo — la firma ENTERA, no solo que exista**:
confirmar el nombre y adivinar los argumentos «porque suenan razonables» es el fallo que cuela
código roto (caso real en `_indice/auditorias/r5-revalidacion.md`).

> 🔴 **Y esto vale también cuando NO estás escribiendo código.** Nombrar una función en una frase
> —«desactívalo con `sprite_set_interpolation`»— cuenta como escribirla: el usuario la va a
> copiar igual. **Antes de enviar cualquier respuesta que mencione una función de GML, pasa por
> `buscar.py` todas las que hayas nombrado**, aunque estés seguro y aunque sea una sola línea de
> conversación.
>
> No es una precaución teórica. El 09-09-2026, un CLI con esta skill cargada respondió a «mi
> sprite se ve emborronado» recomendando `sprite_set_interpolation()`. **Esa función no existe.**
> Había consultado la biblioteca para el resto de la respuesta y aun así añadió ese nombre de
> memoria, que es exactamente el fallo que esta skill existe para impedir. Si te descubres
> escribiendo un nombre sin haberlo buscado en este turno, bórralo y búscalo.

```sh
python3 "$BIB/_indice/buscar.py" nombre_de_la_funcion
```

- Aparece → cuenta los argumentos de la línea `firma:` — cada `[nombre]` entre corchetes es
  opcional, el resto obligatorio, siempre en ese orden (p. ej. `audio_play_sound(index, priority,
  loop, [gain], [offset], [pitch], [listener_mask])` exige 3 como mínimo y admite hasta 7) — más si
  está obsoleta, la página del manual (es/en) y dónde se usa en código real. Escríbela tal cual.
- No aparece → **no existe en este runtime**. No la escribas. El buscador sugiere parecidas.
- `⚠ ÍNDICE CADUCADO` → el runtime instalado cambió: `python3 "$BIB/_indice/actualizar.py"`
  antes de fiarte de ninguna ficha.
- `⚠️ SOLO EN fnames` → existe pero Feather no la autocompleta; pruébala antes de apoyarte en ella.
- «obsoleta» → usa la alternativa que indica la ficha.
- **Structs y enumeraciones incorporados** (`AudioBus`, `AudioEffectType`, `AnimCurveChannel`…)
  no son símbolos de `GmlSpec.xml`: la ficha lo dice y da su página del manual. Sus propiedades
  y valores (`AudioBus.gain`, `AudioEffectType.LPF2`) se leen ahí o con `--manual "AudioBus"`.

Antes de compilar, pasa el validador sobre el proyecto entero: lista por nombre cada llamada a
una función del runtime que no existe, dónde está y cuál parecida sí existe. Funciona también
sobre una carpeta suelta de `.gml` sin `.yyp`; en ese caso dilo en el reporte, porque no habrá
compilación que lo confirme.

```sh
python3 "$BIB/_indice/validar-proyecto.py" /ruta/al/proyecto --todo
```

**Usa `--todo`.** Sin ese flag, el validador solo falla con nombres que llevan prefijo de familia
del runtime (`draw_`, `audio_`, `ds_`…). Una función de dominio inventada —`calcular_ruta()`,
`aplicar_dano()`— cae en «desconocida» y **no hace fallar el comando**.

## Las dieciséis trampas que hacen fracasar a un agente

Verificadas en vivo contra `gm-cli` 2.3.0 y el runtime 2026.0.0.23. Léelas **antes** de ejecutar
el primer comando; el detalle y las tablas completas están en
`12 - Utilidades e integraciones/09 - Manual del agente de IA - operar GameMaker con gm-cli.md`.

1. **`resourcetool` y `compile` se cuelgan bajo el sandbox del Bash de Claude Code.** La causa es
   la capa `npx` interna que descarga del registro de GameMaker. Si un comando se queda colgado
   sin salida, no es que tarde: ejecútalo con el sandbox desactivado, o invoca el binario
   `ResourceTool` cacheado directamente (responde en 0,3 s).
2. **9 de las 18 plantillas de `gm-cli init` fallan en macOS** con `PREFABS RESTORE exited with
   code 1`. Por defecto usa una de las que funcionan —*Space Rocks*, *Blank Pixel Game*, *Tower
   Defense*, *RPG Starter Pack*—. **Pero sí tienen arreglo**: la culpa no es de la plantilla sino
   de un `gmpm.dll` desparejado con `PackageTool@2024.14.29`, y basta con pisarlo con el del IDE
   sobre una `--cache-dir` propia (o arrastrar un `.gmcache/prefabs` ya resuelto, que no necesita
   IDE y es la vía de CI). Receta y tabla completa en la Trampa 1 de `12/09`.
3. **El ResourceTool numera mal dos eventos**: pedir «GUI Begin»/«GUI End» crea *Draw Begin*/*Draw
   End*, y pedir «Room End» crea *Game End*. Sin ningún error. Comprueba siempre el `.yy` después
   de crear un evento, o escribe el archivo con el número correcto de la tabla de `12/09`.
4. **El compilador NO detecta funciones inventadas ni variables sin declarar.** Compila con
   `exit 0` y revienta al ejecutar. Por eso `validar-proyecto.py --todo` **no es opcional**: es
   quien caza lo que el compilador deja pasar.
5. **Una fuente creada con `resourcetool` compila limpio y no dibuja ni una letra.** Rasterizar
   glifos es trabajo del IDE, no del CLI: el `.yy` se queda con `"glyphs":{}` pase lo que pase.
   Hornéalo con Pillow a partir de un `.yy` de referencia, o abre el IDE una vez — y valida el
   JSON antes: uno mal formado no falla limpio, tumba `resourcetool` y `compile` con un
   `AccessViolationException` nativo.
6. **`directory_exists()`/`directory_create()` pueden devolver `false` siempre** bajo `gm-cli run
   --target mac`, incluso sobre la carpeta de guardado que ya existe, y rompen en silencio el
   *gate* de `save_ensure_dir()`. No te fíes de esas dos funciones: intenta escribir de verdad y
   deja que la escritura decida — ya parcheado en `06 - Assets y Scripts/scr_save_load.gml`.
7. **El `HELP` de `resourcetool` nunca lista las raíces de expresión disponibles** — solo
   documenta comandos. Antes de dar «esto no se puede por `resourcetool`» por bueno, prueba
   `resource info expr=project`: es una segunda raíz válida con 18 miembros (configuraciones de
   build, grupos de audio/textura, archivos incluidos, metadatos, el orden de las salas…) que
   ningún ejemplo del `HELP` menciona. Tabla completa de los 18 en `12/09` §9 bis.
8. **`RESOURCE CREATE TYPE=includedfile` deja `filePath` vacío** — la raíz del proyecto, no
   `datafiles/` — sin copiar el archivo físico a ningún sitio. `gm-cli compile --errors-only`,
   el flag que esta misma tabla recomienda, sale con `exit 0` y ni una línea; solo compilando
   **sin** el flag aparece `WARNING :: datafile ... was NOT copied skipped - reason File does
   not exist`. Crea `datafiles/` a mano, copia el archivo dentro, y fija `filePath` con
   `resource set expr=project.IncludedFiles[N].filePath value=datafiles` — no por el nombre del
   recurso si lleva un punto (`datos.json.filePath` falla: el punto se lee como acceso a
   miembro). Detalle completo en `12/09` §0 Trampa 8.
9. **`OBJECT EVENT FINDORCREATE` no acepta todos los eventos, pero eso no significa que no se
   puedan crear.** Su lista de subtipos deja fuera GUI Begin/End, los Async y los User Events; la
   vía real es crear un evento cualquiera y parchear su número con
   `resource set expr=obj_x.eventList[N].eventNum value=<num>`. **Y renombra después el `.gml` al
   número real** (`Draw_74.gml`, `Other_62.gml`): si no, compila limpio y el código queda donde
   el evento no lo busca. Números y receta en `12/09 §9 ter`.
10. **Y la excepción a la trampa 9: `OPTIONS SET` no tiene rescate.** Solo deja escribir 5 de las
    ~30 propiedades de plataforma, y aquí **no** vale parchear el campo crudo — las opciones no
    cuelgan del árbol de recursos. Su propio `HELP` además da nombres equivocados
    (`interpolation` y `fullscreen`; los reales son `interpolate_pixels` y `start_fullscreen`).
    Para el resto, el IDE. Detalle en `12/09 §9 quater`.
11. **`resourcetool` revienta a veces sin motivo.** El mismo comando, sobre el mismo proyecto
    sano, responde bien unas veces y otras lanza un `AccessViolationException` nativo — 2 de cada
    5 llamadas idénticas en la medición. **Reintenta antes de buscar la causa en tus datos**: no
    lo confundas con el `.yy` mal formado de la trampa 5 ni con el `%Name`/`parent` mal fijado al
    hornear una fuente, que dan la misma excepción pero sí tienen arreglo. Detalle en `12/09`.
12. **La fuente por defecto no dibuja tildes ni eñes.** Con `draw_set_font(-1)` —o sin fijar
    ninguna—, «¡Añádeme más peón!» sale como «Ademe ms pen!»: los glifos `á é í ó ú ñ ¿ ¡` se
    omiten **en silencio**, sin caja de glifo ausente, y compila limpio. Como todo lo que escribas
    va en español, esto te afecta siempre. Solución verificada: una fuente propia con `font_add()`
    cargando un `.ttf` por *Included File* (trampa 8), o una fuente del proyecto con sus glifos
    horneados (trampa 5). Ver `01/11` y `12/09`.
13. **`screen_save()` invierte la imagen verticalmente en el runner de Mac.** La ventana real se
    ve bien; el archivo, del revés. Si verificas mirando capturas —y el guion de humo de `13/10`
    se apoya en ellas—, contrasta al menos una vez con `screencapture` del sistema antes de sacar
    conclusiones sobre dónde está cada cosa en pantalla.
14. **Escribir un solo índice de `project.RoomOrderNodes` duplica una sala y tumba el
    compilador.** Reasignar `[i].roomId` sin recolocar la sala que estaba ahí deja el array con
    una repetida, y el `AssetCompiler` revienta con una excepción de .NET en bruto, sin decir la
    causa. **Trátalo siempre como una permutación completa**: si mueves una sala, coloca también
    la desplazada. Receta en `12/09 §9.3 ter`.

15. **🔴 `RESOURCE CREATE TYPE=shape` rompe el proyecto para siempre.** `shape` es uno de los 17
    tipos que anuncia `RESOURCE TYPES`, y crearlo registra el recurso con la ruta vacía **antes**
    de fallar: a partir de ahí no carga nada —ni `compile`— y **no hay comando que lo deshaga**.
    Solo se repara editando el `.yyp` a mano. Que un tipo esté en la lista no significa que sea
    creable. Y de paso: `PREFABS RESTORE exited with code 1` es un mensaje **genérico** de «no
    pude cargar el proyecto»; el diagnóstico de verdad lo da `gm-cli compile`, con archivo, línea
    y el enlace que no resuelve.
16. **🔴 `cache clean --project` borra también la caché COMPARTIDA**, la de los *runtimes*, pese a
    lo que sugiere el nombre del flag. El siguiente `compile` se descarga `runtimes-gms2` entero.
    Si solo quieres limpiar un proyecto, `--cache-dir`. Y no lo ejecutes para «probar algo» sin
    avisar al usuario del coste.

**Y cuatro trampas del propio GML**, que no están en el manual y solo aparecen al compilar:
`1e10` (notación científica) **no compila** · el ternario anidado **necesita paréntesis**
(`a ? x : (b ? y : z)`) · `const` no existe (es `#macro`) · y `function Hijo() : Padre()
constructor {}` con el padre no definido **no da error: crashea el compilador entero** y se traga
los errores de todo lo que venga después.

## Comandos

| Necesito | Comando |
|---|---|
| Ficha de una función, constante o variable | `python3 "$BIB/_indice/buscar.py" draw_sprite_ext` |
| Toda una familia | `python3 "$BIB/_indice/buscar.py" --listar audio_` |
| No sé si es símbolo, concepto o ejemplo | `python3 "$BIB/_indice/buscar.py" --todo "coyote time"` |
| Un concepto en la biblioteca | `python3 "$BIB/_indice/buscar.py" --texto "delta_time"` |
| Cómo lo resuelve código real | `python3 "$BIB/_indice/buscar.py" --codigo "state machine"` |
| La página oficial completa | `gm-cli manual read "surface_create"` o el archivo `manual (es)` que da la ficha, bajo `$BIB/09 - Manual oficial/manual-lts-2026-es/` |
| Validar todo el GML de un proyecto | `python3 "$BIB/_indice/validar-proyecto.py" /ruta/al/proyecto` |
| **¿Es un juego o solo un bucle de juego?** | `python3 "$BIB/_indice/auditar-juego-completo.py" /ruta/al/proyecto` |
| ¿Este PNG hay que repararlo, o repararlo lo destruye? | `python3 "$BIB/_indice/puerta-pixel-art.py" <carpeta de PNG>` — **antes** de pasarle `pixel-art-fixer` a nada |
| ¿Las trampas del CLI siguen siendo ciertas hoy? | `bash "$BIB/_indice/verificar-trampas.sh"` — las reproduce contra el CLI instalado. Si alguna ya no se cumple, este documento está desfasado |
| ¿El código reutilizable de la biblioteca hace lo que dice? | `bash "$BIB/_indice/validar-ejecucion.sh"` — monta un juego real y lo **ejecuta**: **162 comprobaciones** sobre los 13 scripts de `06`. Compilar no es ejecutar: sacó cuatro fallos que compilaban limpios |
| Compilar (desde la carpeta del `.yyp`) | `gm-cli compile` · ejecutar: `gm-cli run` |
| Crear o editar recursos (objetos, sprites, rooms, eventos) | `gm-cli resourcetool eval "<comando>"` o el MCP `gamemaker-resource-tool` del proyecto |
| Proyecto nuevo | `gm-cli init --no-interactive -n <nombre> -t "<plantilla>" --ai --toolchain GMS2@2026.0.0.23` — el `-n` **solo admite letras, números, guiones y guiones bajos**: «Cripta de las Placas» falla con `Use only letters, numbers, dashes, and underscores`. El nombre bonito del juego se pone luego en `options set … property=display_name value="Cripta de las Placas"`, entrecomillado |
| Plantillas que **sí** funcionan hoy | `Space Rocks` · `Blank Pixel Game` · `Tower Defense Template` · `RPG Starter Pack` · `Scrolling Shooter Game Template` · `Survivor Game Template` · `Brick Breaker Template` · `Puzzle Slider Template` · `Fire Jump Template` — las otras 9 fallan, y `init` **no las lista** al fallar |

9 de las 18 plantillas fallan al crear el proyecto (`PREFABS RESTORE exited with code 1`): por
defecto usa *Space Rocks* o *Blank Pixel Game*. **Si necesitas una de las que fallan, sí hay
arreglo** —la causa es un `gmpm.dll` desparejado, no la plantilla—: receta en la Trampa 1 de
`12/09`. El manual `monthly` está discontinuado; la rama vigente es **LTS 2026.0**.

## Qué vía usar: CLI → MCP → computer use → humano

1. **El CLI oficial, siempre que llegue.** `gm-cli` + `resourcetool` construyen un juego entero:
   recursos, eventos, salas, capas, cámaras, viewports, físicas, tilesets, tilemaps desde CSV,
   orígenes de sprite, renombrados, compilación y empaquetado (`12/09 §3 bis`).
2. **El MCP oficial NO puede más que el CLI: es el mismo motor.** `gamemaker-resource-tool` es el
   mismo ResourceTool expuesto como herramientas, y de hecho le **faltan cinco** operaciones que
   `eval` sí tiene. Se usa por comodidad, nunca por capacidad. **Si algo no se puede por CLI,
   tampoco por el MCP oficial** — buscarlo ahí es perder el tiempo.
3. **Computer use, para lo que es exclusivo del IDE.** Hay una lista corta y medida de cosas que
   el CLI no hace: rasterizar los glifos de una fuente, la versión y el nombre de producto del
   ejecutable, las *Variable Definitions* de un objeto, el `nineSlice`, mover un recurso de
   carpeta, anidar capas, el código de creación de una instancia, crear una Extensión y los Flex
   Panels. **Todas son clics en diálogos, no juicios humanos**: un agente con control del
   escritorio debería poder hacerlas. Antes: copia del proyecto. Después: **verifica por CLI**
   (`options get`, `resource info`, `font glyphlist`), nunca por lo que se vio en pantalla.
   ⚠️ **Razonado, no medido**: nadie ha ejecutado aún ninguna de las nueve conduciendo el IDE.
   Trátalo como vía plausible y sin rodar (`12/09 §0 bis`).
4. **El humano, solo para sus sentidos y sus cuentas.** Si se ve bien, si se oye bien, si se
   siente bien, el rendimiento en hardware real, y lo que exija su firma o su cuenta de tienda.
   Esa lista es **más corta de lo que parece**: rellenar un campo en un diálogo ya no está en ella.

## Qué leer según la tarea

El detalle por disciplina, en orden de lectura, está en
[`references/mapa-disciplinas.md`](references/mapa-disciplinas.md). El índice completo de
documentos, generado del disco, en [`references/indice-documentos.md`](references/indice-documentos.md).

| Te piden… | Empieza por |
|---|---|
| Escribir GML que haga X | `buscar.py` por cada símbolo → `11 - Código descargado/_CATALOGO.md` (¿ya hay librería?) → `05 - Referencia/04 - Convenciones y estilo GML.md` |
| Un juego completo, de principio a fin | `04 - Recetas por género/00 - Anatomía de un juego completo.md` y después la receta del género |
| Un juego de género X | `04 - Recetas por género/` — **59 recetas**: los géneros clásicos (plataformas, RPG, roguelike, metroidvania, tower defense, puzle, shoot'em up, carreras, gestión, ritmo, sigilo, horror, granja, idle) más beat'em up, aventura gráfica, deportes, lucha, souls-like, colonia, party games y bullet heaven/autobattler/deckbuilder; y los sistemas transversales: **el nivel como mapa de texto** (la única vía de montar un nivel sin abrir el editor de salas), **puertas, llaves y placas de presión** (el puzle de sala), combate (cuerpo a cuerpo, a distancia, por turnos, no letal), daño y estados, enemigos y director, habilidades, traversal, pathfinding, VFX, tutorial, transiciones y pausa, audio reactivo, modding, eje Z falso, selección de nivel, metajuego y live-ops |
| Diseñar: mecánicas, niveles, arte, UI, sonido, historia | `13 - Diseño y producción de videojuegos/` (mapa en `references/mapa-disciplinas.md`) |
| Estructurar el proyecto para que crezca | `13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md` |
| Explicar un concepto del motor | `01 - Fundamentos/` → la página del manual en `09 - Manual oficial/manual-lts-2026-es/` |
| «No compila» o «se comporta raro» con código antiguo | `01 - Fundamentos/03 - Handles - el cambio clave de 2026.md` → `02 - Novedades 2026/02 - Cambios en GML 2026.md` → `buscar.py` (¿obsoleta?) → github.com/YoYoGames/GameMaker-Bugs |
| Qué librería, extensión o herramienta usar | `12 - Utilidades e integraciones/_INDICE-UTILIDADES.md` → `11 - Código descargado/_CATALOGO.md` → `07 - Ecosistema/` |
| Fijar resolución, escala de ventana, tamaño de la GUI o pantalla completa | `13 - …/03 - Pixel art y resolución.md` §1.6 — **antes** de escribir el primer `window_set_size()`; a ojo sale una escala no entera y el pixel art «hierve» |
| Assets libres (arte, audio, tiles, fuentes) | `07 - Ecosistema/09 - Asset packs y recursos gráficos.md` |
| **Operar GameMaker siendo un agente** (crear recursos, eventos, compilar, depurar sin ver la pantalla) | `12 - Utilidades e integraciones/09 - Manual del agente de IA - operar GameMaker con gm-cli.md` |
| Publicar, exportar, tiendas | `05 - Referencia/02 - Publicar y exportar.md` → `05 - Referencia/05 - Entregar el juego…` (firmar, notarizar, `steamcmd`, Play, App Store) → `13 - …/11 - Producción, alcance y lanzamiento.md` |
| Publicar en **consola** (Nintendo, PlayStation, Xbox) | `05 - Referencia/06 - Publicar en consolas…` — trámite, licencia, *lotcheck*, TRC/XR, y dónde empieza el NDA |
| Marcas, *fan games*, EULA, menores | `13 - …/25 - Legal de terceros…` y `13 - …/20 - Modelo de negocio…` |
| No tengo sprites ni sonidos | `12 - …/09 §5.2` (gráficos) y `13 - …/09 §8 bis` (sonido sintetizado por código) |
| Qué cambió en 2026, qué versión usar | `02 - Novedades 2026/01 - Resumen LTS 2026.0.md` → `README.md` §2 |
| Enseñar a alguien que aprende | `RUTA.md`: sitúa el nivel por lo que sabe hacer y da solo material de su nivel y el siguiente |
| No sé por dónde empezar | `_indice/COMO-BUSCAR.md` |

## Orden de autoridad cuando las fuentes se contradicen

```
1. _indice/simbolos.json   → sale del GmlSpec.xml del runtime instalado
2. 09 - Manual oficial/    → espejo de manual.gamemaker.io, rama LTS, completo en español
3. 02 - Novedades 2026/    → release notes y blog oficial, con fecha
4. 01, 04, 05, 08, 13      → documentación propia, verificada
5. 11 - Código descargado  → código real: muestra la práctica, no la norma
6. 03, 10 - Cursos         → pueden estar desfasados; llevan aviso
```

Un tutorial nunca gana a `simbolos.json`. Lo no verificado lleva ⚠️ en el texto.

## Prohibiciones duras

- `.yy` y `.yyp` no se editan a mano: `gm-cli resourcetool eval` o el MCP. El `.gml` sí.
- Una firma no se supone: se consulta. «Creo que era así» no es una fuente.
- Los IDs de assets son *handles* en 2026: `sprite_index + 1` está muerto.
- Nada de funciones obsoletas (hay 171): la ficha avisa y da la alternativa.
- El código de los juegos comerciales de `11 - Código descargado/juegos_y_motores/` (Pizza
  Tower, Deltarune, AM2R, Hotline Miami, Kirby) se lee, no se copia.
- Los **identificadores de GML son ASCII puro**: `function añadir()` no compila («invalid token ñ»).
  Nombra en español sin tildes ni eñes; `validar-codigo-gml.py` lo detecta.
- El asset **Extensión** es la única excepción a lo anterior: `resourcetool` no puede crearlo
  (`Resource type 'extension' is not creatable`), solo el IDE. Ver `07 - Ecosistema/22 - Crear una extensión nativa (guía en español).md`.
- **`Successful`, `Saved successfully` y `exit 0` NO son verificación.** Tras escribir cualquier
  cosa con `resourcetool` o `ProjectTool`, **léela de vuelta** (`resource info`, `options get`,
  o directamente el `.yy`/`.yyp`). Van ya tres casos medidos en los que la herramienta dice que
  sí y no hizo nada: `OPTIONS SET` truncando un nombre en el primer espacio, el *included file*
  que nunca llega al paquete, y `ProjectTool IMPORT YY`, que anuncia «Adding resource… to
  <proyecto>», copia la carpeta al disco y **jamás la registra en el `.yyp`**. Y ojo con la
  variante peor: un proyecto que **compila** después de una operación fallida puede estar
  compilando precisamente *porque* la operación no se hizo.
  ⚠️ **Que mienta no significa que no se pueda**: el truncado del primer espacio se resuelve
  entrecomillando el valor —`value="Cripta de las Placas"`, verificado leyendo el `.yy`— y la
  comilla simple o la barra invertida NO valen (dejan `'Cripta` y `Con\`). Un agente lo leyó
  aquí como «imposible» y renunció al nombre del juego; la salida estaba en `12/09` Trampa 10 y
  esta línea no la mencionaba.
- Nada está «hecho» sin `gm-cli compile` limpio y su salida real reportada. `--errors-only`
  sirve para iterar rápido, pero **antes de dar un juego por terminado, compílalo al menos una
  vez sin ese flag y lee los avisos**: es el único modo que muestra el `WARNING` de un
  *included file* sin copiar (trampa 8). Y **compilar limpio no es funcionar**: la fuente muda y
  el guardado roto de las trampas 5 y 6 compilan sin una queja (`13/10 §8.6` da las dos
  comprobaciones que sí los cazan).
- No declares un juego «terminado» sin compararlo punto por punto con el checklist maestro de
  `04/00`. Si algo falta o no aplica, dilo; el silencio no vale.
- **Un rectángulo de color no es un sprite.** Ni un cuadrado, ni un círculo liso, ni un SVG
  improvisado: si entregas eso como personaje, enemigo u objeto, el juego parece un prototipo por
  mucho que el código sea bueno. La escalera de `12/09 §5.2` da la salida digna —silueta por
  código con paleta coherente, assets libres, o generación por IA— y para el sonido está
  `13/09 §8 bis`. **Baja un peldaño antes de rendirte, nunca entregues el rectángulo.**

## Flujo para un desarrollo real

0. **Especificación**: si el encargo es «hazme un juego» y no trae ya género, alcance y
   plataforma decididos, pregúntalos en un único turno (nunca un interrogatorio secuencial) y
   completa con los valores por defecto lo que el usuario no conteste — preguntas, criterio de
   parada, defaults y plantilla en `13/28`. Escribe la especificación y **enséñasela al usuario
   antes de crear el proyecto**: no hay paso 2 sin este documento escrito primero.
   **Si el encargo llegó cerrado y no tienes canal de vuelta** (tarea de fondo, *issue*, otro
   agente): no preguntes al vacío — aplica los defaults, escribe la especificación igual,
   marca cada valor asumido con `[DEFAULT]` y **entrégala con el juego**, diciendo en el mensaje
   final qué asumiste y por qué. Es el único cambio de orden permitido, y está en `13/28 §2.2 bis`.
1. **Plano**: `04/00 - Anatomía` + receta del género + `13/01 - Diseño de juego` (core loop) +
   `13/14 - El documento de diseño` (el GDD que un agente puede implementar) + `13/11 - Producción`
   (alcance, vertical slice) — el material que alimenta la especificación del paso 0.
2. **Proyecto**: `gm-cli init` (o el `.yyp` existente; `gm-mcp-setup .` si falta el MCP).
3. **Arquitectura**: `13/06` (gestores, escenas, datos) + convenciones `05/04`.
4. **Sistemas**: antes de escribir uno, `11 - Código descargado/_CATALOGO.md`. Entrada, texto,
   diálogos, audio, guardado y UI ya están resueltos por terceros.
5. **GML**: `buscar.py` por símbolo mientras escribes; `validar-proyecto.py` al terminar.
6. **Compila**: `gm-cli compile`; corrige hasta salida limpia; repórtala. Recuerda que
   compilar limpio **no** significa que el código sea correcto (trampa 4).
7. **Antes de decir «terminado»**, en este orden:
   a. `python3 "$BIB/_indice/auditar-juego-completo.py" <proyecto>` — mira el `.yyp`, los `.yy`
      y todo el `.gml`, y te dice qué piezas del envoltorio **no encuentra**: menú, opciones,
      pausa, guardado, créditos, fin de partida, sonido, mando, si el jugador entra por una
      portada o directo al nivel, y qué objetos sin sprite están pintando rectángulos. Sale con
      código 1 mientras falte algo, para que no se pueda pasar por alto. También avisa de
      **objetos contra los que colisiona tu código y que no tienen máscara** —sin sprite ni
      `maskSpriteId`, `place_meeting()` no los encuentra nunca: son invisibles Y atravesables,
      sin un solo error.
      **También te dice qué sistemas has escrito que ya existían hechos** —entrada, texto,
      diálogo, serialización, guardado, tweens, pathfinding, idiomas—: tres agentes seguidos
      escribieron su propio sistema de entrada teniendo `Input` en el catálogo, así que el paso
      «mira `11 · _CATALOGO.md` antes de escribir un sistema» dejó de ser una frase y pasó a
      ser una comprobación.
   b. Cada ✗ es **una pregunta, no una acusación**: puede ser un falso positivo (un menú que vive
      dentro de otra sala) o puede faltar de verdad. Compruébalo tú.
   c. Compara además, pantalla por pantalla, contra el checklist maestro de
      `04/00 - Anatomía de un juego completo` **y contra las tres listas que enlaza**:
      `04/41 §4` (transiciones, carga y pausa), `13/05 §4` (UI antes de publicar) y
      `05/02 §4.4` (build de release). **No son opcionales**: la tabla de `04/00` las presenta
      como «detalle», y una casilla marcada sin abrir la lista que enlaza no está marcada — es
      un fallo real y medido, no una hipótesis (`_indice/auditorias/r12-prueba-plataformas.md`
      §1.12). El script cubre lo que una máquina puede ver; el resto —si el menú se entiende, si
      la historia se sostiene— no lo cubre nadie más que tú.
   d. **Si no puedes ejecutar el juego** (sin `run`, sin pantalla, tarea de fondo): la red que
      queda son las **seis preguntas de `13/10 §8.8`**, que se responden leyendo y cazan la clase
      de fallo que el compilador y `validar-proyecto.py` no ven — guardas de pausa mal colocadas,
      ramas que olvidan un caso, métodos ligados a instancias que mueren. Y di explícitamente qué
      quedó sin comprobar por no poder ejecutar.
   e. **Lo que recortes, se dice**; no se omite en silencio.
8. **Antes de publicar**: `13/10 - Testing y QA` → `05/02 - Publicar y exportar` →
   `05/05 - Entregar el juego` (firmar y subir) → `05/06` si va a consola.

## Convenciones del código que generes

`snake_case`; locales con `_` (`var _velocidad`); prefijos `obj_ spr_ snd_ rm_ scr_ fnt_ tset_`;
sin nombres reservados (`x`, `y`, `speed`, `direction`, `id`, `depth`, `score`, `health`,
`lives`) para variables propias; comentarios en español; identificadores de la API en inglés.
Funciones propias sin prefijo de familia del runtime (`draw_`, `audio_`, `ds_`…): confunden
al validador y a Feather.

## Si también está cargada la skill `gamemaker-expert`

Sus patrones de arquitectura sirven. Sus enlaces al manual apuntan al canal `monthly`, que ya
no existe: usa el espejo LTS de `$BIB/09 - Manual oficial/`. Cualquier función que cite se
verifica con `buscar.py` igual que las demás.
