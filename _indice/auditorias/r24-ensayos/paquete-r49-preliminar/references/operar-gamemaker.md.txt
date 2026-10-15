# Operar GameMaker

Lee antes de init, recursos, compilación, ejecución o empaquetado; no ejecutes nada si hay pausa vigente.

Contenido: trampas del entorno documentado · operaciones y comprobación · CLI, MCP e IDE.

## Las diecinueve trampas que hacen fracasar a un agente

Verificadas en vivo contra `gm-cli` 2.3.0 y el runtime 2026.0.0.23. Son resultados del entorno indicado, no garantías para cualquier versión. Léelas **antes** de ejecutar
el primer comando de operación; el detalle y las tablas completas están en
`12 - Utilidades e integraciones/09 - Manual del agente de IA - operar GameMaker con gm-cli.md`.

1. **`resourcetool` y `compile` se cuelgan bajo el sandbox del Bash de Claude Code.** La causa es
   la capa `npx` interna que descarga del registro de GameMaker. Si un comando se queda colgado
   sin salida, no es que tarde: diagnostica la descarga y usa la vía permitida por el harness (solicita su excepción si procede), o invoca el binario
   `ResourceTool` cacheado directamente (responde en 0,3 s).
2. **9 de las 18 plantillas de `gm-cli init` fallan en macOS** con `PREFABS RESTORE exited with
   code 1`. Por defecto usa una de las que funcionan —*Space Rocks*, *Blank Pixel Game*, *Tower
   Defense*, *RPG Starter Pack*—. **Pero sí tienen arreglo**: la culpa no es de la plantilla sino
   de un `gmpm.dll` desparejado con `PackageTool@2024.14.29`, y basta con pisarlo con el del IDE
   sobre una `--cache-dir` propia (o arrastrar un `.gmcache/prefabs` ya resuelto, que no necesita
   IDE y es la vía de CI). Receta y tabla completa en la Trampa 1 de `12/09`.
3. **El ResourceTool numera mal dos eventos**: pedir «GUI Begin»/«GUI End» crea *Draw Begin*/*Draw
   End*, y pedir «Room End» crea *Game End*. Sin ningún error. Comprueba siempre el `.yy` después
   de crear un evento, y corrige el evento mediante el ResourceTool o el IDE con el número correcto de la tabla de `12/09`; no edites `.yy` a mano.
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
13. **`screen_save()` NO invierte la imagen — y esta advertencia, al revés, ya ha hecho daño.**
    Se midió invertida en una sesión anterior; **re-comprobado el 2026-09-10 sobre el runtime
    2026.0.0.23 en macOS arm64, sale derecha**. Un agente se creyó el aviso, volteó su captura
    para «corregirla» y le quedó boca abajo. **No la voltees.** Lo que sí sigue valiendo, porque
    es barato: contrasta **una vez por sesión** una captura de `screen_save()` contra una de
    `screencapture` del sistema sobre el mismo fotograma. Si coinciden, ninguna trampa; si
    difieren solo en el eje vertical, ha vuelto. Detalle y la historia fechada, en `12/09`
    trampa 13.
14. **Escribir un solo índice de `project.RoomOrderNodes` duplica una sala y tumba el
    compilador.** Reasignar `[i].roomId` sin recolocar la sala que estaba ahí deja el array con
    una repetida, y el `AssetCompiler` revienta con una excepción de .NET en bruto, sin decir la
    causa. **Trátalo siempre como una permutación completa**: si mueves una sala, coloca también
    la desplazada. Receta en `12/09 §9.3 ter`.

15. **🔴 `RESOURCE CREATE TYPE=shape` rompe el proyecto para siempre.** `shape` es uno de los 17
    tipos que anuncia `RESOURCE TYPES`, y crearlo registra el recurso con la ruta vacía **antes**
    de fallar: a partir de ahí no carga nada —ni `compile`— y **no hay comando que lo deshaga**.
    En aquella prueba solo se logró reparar editando el `.yyp` a mano: es un antecedente,
    no autorización para repetirlo. Preserva la copia previa y usa una recuperación válida
    o el IDE; mantén la regla de no editar recursos manualmente. Que un tipo esté en la lista no significa que sea
    creable. Y de paso: `PREFABS RESTORE exited with code 1` es un mensaje **genérico** de «no
    pude cargar el proyecto»; el diagnóstico de verdad lo da `gm-cli compile`, con archivo, línea
    y el enlace que no resuelve.
16. **🔴 `cache clean --project` borra también la caché COMPARTIDA**, la de los *runtimes*, pese a
    lo que sugiere el nombre del flag. El siguiente `compile` se descarga `runtimes-gms2` entero.
    Si solo quieres limpiar un proyecto, `--cache-dir`. Y no lo ejecutes para «probar algo» sin
    avisar al usuario del coste.
17. **Tres subcomandos que se adivinan mal, y uno miente.** `sound set`/`sound import` **no
    existen** —es `sound setfile`— y aun así la salida contiene «Success» (del guardado del
    proyecto), así que un script que busque esa palabra da por importados sonidos que dejaron
    la carpeta vacía. Los eventos **sin subtipo** (Create, CleanUp, Destroy) se piden **sin el
    argumento**: `type=create subtype=create` no crea nada y no da error legible. Y `options
    set` usa `property=`, no `name=`. Ante la duda, **pásale un valor inventado**: el comando
    imprime la lista exacta de lo que acepta (`Expected draw_normal | draw_begin | …`).
18. **`keyboard_key_release()` genera un SEGUNDO borde de `keyboard_check_pressed`.** Medido en
    el runner de Mac: pulsar y soltar cuenta como dos pulsaciones. Importa cuando un agente
    ejerce su propio juego para probarlo —que es cómo se pasa de «compila» a «se navega»—:
    con `ESC`, que suele ser pausa **y** atrás, la primera abre la pausa y la segunda la cierra,
    y la captura sale con el juego corriendo. Pulsa y no sueltes, o deja pasar un fotograma.
19. **Desde un Mac se COMPILA para Windows, pero no se EMPAQUETA.** `compile --target windows`
    funciona; `package --target windows` escupe treinta líneas de traza de C# porque el último
    paso sella la versión dentro del `.exe` con `BeginUpdateResource`, una función de la API
    de Windows que en macOS no existe. **No es que la exportación esté rota**: el `.exe` y el
    `data.win` ya están hechos en `.gmcache/build-gms2-windows-VM/output/` y se ejecutan. Para
    un `.zip` distribuible hace falta Windows o un *runner* de CI. Y ojo: bajo Wine,
    `screen_save()` devuelve un PNG **negro** aunque el juego se vea corriendo en el log — si
    verificas por captura y sale negra, comprueba por otra vía antes de creértelo.

**Y cuatro trampas del propio GML**, que no están en el manual y solo aparecen al compilar:
`1e10` (notación científica) **no compila** · el ternario anidado **necesita paréntesis**
(`a ? x : (b ? y : z)`) · `const` no existe (es `#macro`) · y `function Hijo() : Padre()
constructor {}` con el padre no definido **no da error: crashea el compilador entero** y se traga
los errores de todo lo que venga después.

## Operaciones y comprobación

| Necesito | Comando o contrato |
|---|---|
| **Escribir un campo del `.yy` que no conoces** | Dos trampas juntas: el truco de pasar un valor inventado para que el comando **liste los válidos** NO es universal (con `collisionKind` responde `not found` y no lista nada), y el **`.yy` guarda un NÚMERO mientras `resourcetool` acepta un NOMBRE** — se escribe `Ellipse`, se lee `2`. Quien verifique buscando la cadena que escribió concluye que falló cuando ha funcionado. `12/09` trampas 24 y 25 |
| **`gm-cli run` que no termina** | Un error de EJECUCIÓN abre un **diálogo modal** en el runner de Mac y la ejecución **no acaba jamás** — en una sesión sin manos no es «falla», es «no termina». Observado dos veces: 600 s sin una línea de salida, y dos runners zombis. **Pon SIEMPRE un tope de tiempo** (macOS no trae `timeout`: lánzalo en segundo plano, sondea, y mata **solo tu proceso** — `pkill -f` se lleva los de otro rol). Y **se acumulan**: medido, dos procesos de 47 y 36 minutos envenenando cada ejecución nueva por la `.gmcache` compartida. Detéctalos con `ps -eo pid,etime,command | grep "gm-cli run"` — una ejecución sana dura segundos. Y antes de ejecutar, `validar-proyecto.py --todo`, que caza la causa más común. `12/09` trampa 22 |
| **Colocar piezas por casilla** | `nivel_mapa_construir()` crea cada instancia en la **esquina** de su casilla, así que **todo sprite de rejilla lleva el origen en (0,0)**. Medido: un origen centrado-abajo (9,18) desplazó la pieza media celda a la izquierda y una entera arriba, **sin un solo error** — el nivel parece mal diseñado en vez de mal montado. Y muerde en lote: tres piezas más lo habrían hecho el día que alguien montara el primer nivel. Criterio en `06 · README` |
| **Varios agentes trabajando en el MISMO proyecto** | `resourcetool` **reescribe el `.yyp` entero**: dos procesos creando recursos a la vez se pisan y **el que pierde no se entera** — el recurso desaparece del `.yyp`, su carpeta se queda en disco y `gm-cli compile` sale con **0 sin decir nada**. Aquí el consejo de «mira el disco» da un falso verde: hay que mirar el **`.yyp`**. **Y `compile`/`run`/`package` comparten la carpeta `.gmcache`**: dos a la vez hacen que el runner SEGFAULTEE leyendo un `options.ini` a medio escribir — medido, tres informes de fallo de `Mac_Runner` en dos minutos, traza en `IniFile::GetSection`. Parece un bug de GameMaker y es una colisión. **Un escritor a la vez por proyecto**, y después `auditar-juego-completo.py`, que lista los recursos huérfanos y hace fallar. Medido y reproducido en `12/09` trampa 19 |
| **Verificar con `resource info` es ESCRIBIR** | Cualquier llamada a `resourcetool` guarda el proyecto — **medido incluso con `HELP`**, que no consulta nada: el `.yyp` cambia de `mtime` y la salida dice `Saving..........Success`. Así que «verifica leyendo de vuelta» **se contradice a sí mismo con dos agentes**: la verificación provoca la carrera. Verifica leyendo el `.yy` con `cat`/`grep`: no escribe, no arranca `npx` y mide el archivo que decide. `12/09` trampa 20 |
| **Cambiar el origen o la velocidad de un sprite** | `xorigin`, `yorigin` y `playbackSpeed` **cuelgan de `sequence`**, no del sprite: `spr.xorigin` falla con `Member 'xorigin' not found`. Y el sprite **sí** tiene un `origin`, que es el enum (Automatic/Custom), no la coordenada — quien lo vea en la lista se lo cree. La ruta buena es `spr.sequence.xorigin`. Ojo: el intento fallido **también imprime `Saving...Success`**, así que un `grep success` da verde sobre un comando que falló. `12/09` trampa 21 |
| Compilar (desde la carpeta del `.yyp`) | `gm-cli compile` · ejecutar: `gm-cli run` |
| Crear o editar recursos (objetos, sprites, rooms, eventos) | `gm-cli resourcetool eval "<comando>"` o el MCP `gamemaker-resource-tool` del proyecto |
| Proyecto nuevo | `gm-cli init --no-interactive -n <nombre> -t "<plantilla>" --ai --toolchain <engine>@<runtime_del_proyecto>` — el `-n` **solo admite letras, números, guiones y guiones bajos**: «Cripta de las Placas» falla con `Use only letters, numbers, dashes, and underscores`. El nombre bonito del juego se pone luego en `options set … property=display_name value="Cripta de las Placas"`, entrecomillado |
| Plantillas que funcionaron en el entorno documentado | `Space Rocks` · `Blank Pixel Game` · `Tower Defense Template` · `RPG Starter Pack` · `Scrolling Shooter Game Template` · `Survivor Game Template` · `Brick Breaker Template` · `Puzzle Slider Template` · `Fire Jump Template` — las otras 9 fallan, y `init` **no las lista** al fallar |

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
   escritorio debería poder hacerlas. Antes: copia del proyecto. Después: verifica el resultado en archivos y, con exclusión de escritura, por CLI
   (`options get`, `resource info`, `font glyphlist`); después prueba el efecto real. Los comandos
   del ResourceTool también guardan el proyecto, incluso `HELP`. Una lectura de pantalla no basta.
   ⚠️ **Razonado, no medido**: nadie ha ejecutado aún ninguna de las nueve conduciendo el IDE.
   Trátalo como vía plausible y sin rodar (`12/09 §0 bis`).
4. **El humano, solo para sus sentidos y sus cuentas.** Si se ve bien, si se oye bien, si se
   siente bien, el rendimiento en hardware real, y lo que exija su firma o su cuenta de tienda.
   Esa lista es **más corta de lo que parece**: rellenar un campo en un diálogo ya no está en ella.

- `.yy` y `.yyp` no se editan a mano: `gm-cli resourcetool eval` o el MCP. El `.gml` sí.

- El asset **Extensión** requiere la vía del IDE: `resourcetool` no puede crearlo
  (`Resource type 'extension' is not creatable`), solo el IDE. Ver `07 - Ecosistema/22 - Crear una extensión nativa (guía en español).md`.

- **`Successful`, `Saved successfully` y `exit 0` NO son verificación.** Tras escribir cualquier
  cosa con `resourcetool` o `ProjectTool`, **léela de vuelta** directamente del `.yy`/`.yyp`; `resource info` y `options get`
  solo con exclusión de escritura, pues también guardan el proyecto. Van ya tres casos medidos en los que la herramienta dice que
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
