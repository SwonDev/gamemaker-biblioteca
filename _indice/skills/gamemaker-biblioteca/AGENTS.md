# AGENTS.md — Biblioteca GameMaker (generado desde la skill)

> **Generado por `_indice/sincronizar-skill.py` a partir del cuerpo real de**
> **`SKILL.md`. No lo edites a mano:** se reescribe en cada `python3 _indice/actualizar.py`
> o `./instalar.sh`. Existe para los CLI de IA que solo leen `AGENTS.md` en la raíz
> de un proyecto y no tienen un directorio de skills en formato `SKILL.md` — copia
> este archivo (o enlázalo) como `AGENTS.md` en la raíz de tu proyecto de GameMaker.
> Si tu CLI sí lee skills, usa directamente la carpeta
> `_indice/skills/gamemaker-biblioteca/` — no hace falta este archivo.

**Cuándo aplica esto:** Úsala ante cualquier cosa de GameMaker o GML: «hazme un juego», «no compila», «se comporta raro», archivos .yyp/.yy/.gml, gm-cli, resourcetool, publicar un juego. Fuente fidedigna para LTS 2026: verifica cada símbolo antes de escribirlo (¿existe?, firma, obsoleta, manual) y trae las trampas del CLI que hacen fracasar a un agente. Cubre el desarrollo entero — diseño y GDD, niveles, arte y animación, VFX y shaders, UI/UX y accesibilidad, cámaras, arquitectura, procedural, físicas, combate, IA, pathfinding, progresión, sonido, narrativa, testing, producción, móvil y 3D — y la publicación: firmar, notarizar, Steam, Play, App Store y consolas.

# GameMaker · biblioteca fidedigna

<!-- SKILL-VERSION: r44 · 2026-09-10 -->
`r23 · 2026-09-10` — GameMaker LTS 2026 (IDE 2026.0.0.16 · runtime 2026.0.0.23).

Una base de conocimiento local, en español, verificada contra el runtime instalado. Existe
para que el GML que escribas **no invente nada** y para que cada decisión de diseño tenga
detrás un documento contrastado.

> 🏷️ **Para qué sirve esa etiqueta.** Una skill instalada es una **copia**: puede llevar meses
> desfasada sin que se note, porque responde igual de convencida. `sincronizar-skill.py` compara
> la versión de cada copia instalada con la de esta carpeta y **te dice cuál va atrasada y por
> cuánto**. Si en una sesión ves un `r` distinto del que tiene el repositorio, reinstala con
> `./instalar.sh` antes de fiarte de lo que diga.

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
  Los 272 documentos, las recetas y los validadores funcionan; lo que no funciona es
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

## Las diecinueve trampas que hacen fracasar a un agente

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
    Solo se repara editando el `.yyp` a mano. Que un tipo esté en la lista no significa que sea
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

## Comandos

| Necesito | Comando |
|---|---|
| Ficha de una función, constante o variable | `python3 "$BIB/_indice/buscar.py" draw_sprite_ext` |
| Toda una familia | `python3 "$BIB/_indice/buscar.py" --listar audio_` |
| No sé si es símbolo, concepto o ejemplo | `python3 "$BIB/_indice/buscar.py" --todo "coyote time"` |
| Un concepto en la biblioteca | `python3 "$BIB/_indice/buscar.py" --texto "delta_time"` |
| Cómo lo resuelve código real | `python3 "$BIB/_indice/buscar.py" --codigo "state machine"` |
| La página oficial completa | `gm-cli manual read "surface_create"` o el archivo `manual (es)` que da la ficha, bajo `$BIB/09 - Manual oficial/manual-lts-2026-es/` |
| Validar todo el GML de un proyecto | `python3 "$BIB/_indice/validar-proyecto.py" /ruta/al/proyecto` — **sale con 1** si alguien llama a un nombre que no existe en ninguna parte, que es lo que compila limpio y revienta al arrancar. Distingue la función inventada del método de struct: si un nombre se llama y **no se le asigna nada** en todo el proyecto, no es un método. Las de plataforma (`steam_*`, `ps5_*`…) van aparte y no hacen fallar |
| **¿Es un juego o solo un bucle de juego?** | `python3 "$BIB/_indice/auditar-juego-completo.py" /ruta/al/proyecto` |
| **Escribir una maqueta o simulación** | Una simulación es tan buena como su calibración, y **escribirla con cuidado NO es calibrarla**. La forma robusta: que **reproduzca al arrancar unas mediciones independientes** y, si no lo consigue, **se declare descalibrada y no analice nada**. Así deja de ser fiable «hoy porque alguien lo comprobó» y pasa a serlo cada vez que se ejecuta — si el balance cambia, se calla en vez de dar un APTO falso. Con controles que TIENEN que fallar. Y aun así su veredicto es el peldaño 2: decide el juego corriendo. `13/10 §8.6 quater` |
| **Escribir código que otros van a copiar** | **Un ejemplo que ya hace lo correcto vale más que la nota que lo explica: la nota se salta, el código de al lado se copia.** Medido en esta biblioteca: `scr_ui_confirmar.gml` leía el teclado a pelo y rompía la doctrina de «toda la entrada por UNA función» en cuanto lo pegabas — un defecto del script, no del proyecto. Antes de escribir una regla, mira si puedes hacer que **el ejemplo más cercano ya la cumpla**; y si no se puede, que al menos **no la contradiga**. Criterio en `06 · README` |
| **Cuando el resultado sale raro** | Sospecha del **instrumento** antes que de lo medido: cuatro veces en un día el fallo estaba en la herramienta. Los cuatro los cazó el mismo hábito — **saber qué número tiene que salir ANTES de ejecutar** — y la frase que los resume es *«un control que nunca toca no es un control»*. Mete siempre un caso que TIENE que fallar: una comprobación que solo mira casos buenos no distingue «todo bien» de «no estoy mirando». Y si una medición contradice a la documentación, **sospecha primero que miden variables distintas**. `13/10 §8.6 bis` |
| **`place_meeting()` y compañía** | Usan **la máscara de QUIEN LLAMA**, no la del objeto que les pasas — la firma `place_meeting(x, y, obj)` invita a leerlo al revés. Medido: llamarla desde un objeto **sin sprite** devuelve `false` SIEMPRE, contra todo y en todos los ángulos. Para comprobar la colisión de otra instancia, `with (esa) { … }`. `01/08` |
| **Escribir un campo del `.yy` que no conoces** | Dos trampas juntas: el truco de pasar un valor inventado para que el comando **liste los válidos** NO es universal (con `collisionKind` responde `not found` y no lista nada), y el **`.yy` guarda un NÚMERO mientras `resourcetool` acepta un NOMBRE** — se escribe `Ellipse`, se lee `2`. Quien verifique buscando la cadena que escribió concluye que falló cuando ha funcionado. `12/09` trampas 24 y 25 |
| **Un sprite que GIRA y mata** | Con máscara `Rectangle`, girar el sprite **agranda la hitbox**: el manual dice que es *«an axis-aligned bounding box around the (rotated and scaled) instance»*, así que envuelve al sprite ya girado y crece **√2 a 45°** — 18 px pasan a **25,46**. Un engranaje mata 3,7 px más lejos en unos ángulos que en otros y el dibujo no cambia: **la víctima no puede aprenderlo**. Salidas: `Rectangle With Rotation` (la más barata, solo desde el editor o el `.yy`), `Ellipse` (invariante, mejor para lo redondo), o dejar `image_angle = 0` y girar solo en el `draw_sprite_ext`. Criterio en `01/08` |
| **Cómo se verifica de verdad** | **Tres peldaños, y los dos primeros son los baratos**: el comando dice que sí → el archivo dice que sí → **el juego corriendo dice que sí**. Medido: alguien verificó nueve valores leyendo los `.yy` (`fallos = 0`, honesto) y en esa misma línea iba impreso el origen que desplazaba cuatro piezas una celda — comprobó la escritura, no el efecto. Y cuidado con el **verde por omisión**: una lista de objetos escrita a mano da ✓ sin mirar los nuevos, y una guarda mal elegida (`is_struct` sobre un id de instancia) sale callando. **Una comprobación que no dice cuántas cosas ha mirado no vale.** `13/10 §8.6 quater` |
| **`gm-cli run` que no termina** | Un error de EJECUCIÓN abre un **diálogo modal** en el runner de Mac y la ejecución **no acaba jamás** — en una sesión sin manos no es «falla», es «no termina». Observado dos veces: 600 s sin una línea de salida, y dos runners zombis. **Pon SIEMPRE un tope de tiempo** (macOS no trae `timeout`: lánzalo en segundo plano, sondea, y mata **solo tu proceso** — `pkill -f` se lleva los de otro rol). Y **se acumulan**: medido, dos procesos de 47 y 36 minutos envenenando cada ejecución nueva por la `.gmcache` compartida. Detéctalos con `ps -eo pid,etime,command | grep "gm-cli run"` — una ejecución sana dura segundos. Y antes de ejecutar, `validar-proyecto.py`, que caza la causa más común. `12/09` trampa 22 |
| **`other` dentro de un `with`** | **No ve las `var` locales** de la función de fuera: `other._local` revienta con «not set before reading it» — y al ser error de ejecución, **cuelga la sesión** (trampa 22). Usa una variable de instancia, o un struct, que sí viaja por referencia. `12/09` trampa 23 |
| **Colocar piezas por casilla** | `nivel_mapa_construir()` crea cada instancia en la **esquina** de su casilla, así que **todo sprite de rejilla lleva el origen en (0,0)**. Medido: un origen centrado-abajo (9,18) desplazó la pieza media celda a la izquierda y una entera arriba, **sin un solo error** — el nivel parece mal diseñado en vez de mal montado. Y muerde en lote: tres piezas más lo habrían hecho el día que alguien montara el primer nivel. Criterio en `06 · README` |
| **Un estado que se pierde y no sabes por qué** | Si usas `image_index` para elegir un ESTADO (encendido/apagado, abierto/cerrado) y el sprite tiene `playbackSpeed` distinto de 0, **la animación lo reescribe cada paso**: medido, un estado perdido **30 veces por segundo**. Es de los peores de diagnosticar porque **no está en el código ni en el sprite por separado**, solo en la combinación. Salida: `image_speed = 0` en el objeto, o `playbackSpeed = 0` en el sprite cuando sus fotogramas son variantes y no un ciclo. `auditar-juego-completo.py` lo caza y hace fallar; criterio en `08/01` |
| **Varios agentes trabajando en el MISMO proyecto** | `resourcetool` **reescribe el `.yyp` entero**: dos procesos creando recursos a la vez se pisan y **el que pierde no se entera** — el recurso desaparece del `.yyp`, su carpeta se queda en disco y `gm-cli compile` sale con **0 sin decir nada**. Aquí el consejo de «mira el disco» da un falso verde: hay que mirar el **`.yyp`**. **Y `compile`/`run`/`package` comparten la carpeta `.gmcache`**: dos a la vez hacen que el runner SEGFAULTEE leyendo un `options.ini` a medio escribir — medido, tres informes de fallo de `Mac_Runner` en dos minutos, traza en `IniFile::GetSection`. Parece un bug de GameMaker y es una colisión. **Un escritor a la vez por proyecto**, y después `auditar-juego-completo.py`, que lista los recursos huérfanos y hace fallar. Medido y reproducido en `12/09` trampa 19 |
| **Verificar con `resource info` es ESCRIBIR** | Cualquier llamada a `resourcetool` guarda el proyecto — **medido incluso con `HELP`**, que no consulta nada: el `.yyp` cambia de `mtime` y la salida dice `Saving..........Success`. Así que «verifica leyendo de vuelta» **se contradice a sí mismo con dos agentes**: la verificación provoca la carrera. Verifica leyendo el `.yy` con `cat`/`grep`: no escribe, no arranca `npx` y mide el archivo que decide. `12/09` trampa 20 |
| **Cambiar el origen o la velocidad de un sprite** | `xorigin`, `yorigin` y `playbackSpeed` **cuelgan de `sequence`**, no del sprite: `spr.xorigin` falla con `Member 'xorigin' not found`. Y el sprite **sí** tiene un `origin`, que es el enum (Automatic/Custom), no la coordenada — quien lo vea en la lista se lo cree. La ruta buena es `spr.sequence.xorigin`. Ojo: el intento fallido **también imprime `Saving...Success`**, así que un `grep success` da verde sobre un comando que falló. `12/09` trampa 21 |
| **Necesito el sprite FINAL, animado y de producción** | La cadena de `07/23 §5 bis`, en este orden: **`codex` con `gpt-imagegen-2.5`** genera cualquier asset (hoja, iconset, con fondo o sin él) → **`puerta-pixel-art.py`** dictamina → **`pixel-art-fixer`** (MIT) lo devuelve a una rejilla real, porque lo que sale de un modelo **no es pixel art** aunque lo parezca → **`sprite-gen`** (Apache-2.0) anima desde **UNA base con la identidad bloqueada** y entrega atlas + `manifest.json` con rectángulos y fps por estado → `python3 "$BIB/_indice/atlas-a-gamemaker.py" <run> --salida <carpeta>` lo registra. Pedirle «una hoja de sprites» a un modelo en crudo sigue sin servir, y `07/23 §2` dice por qué |
| Tengo un dibujo y necesito la hoja de sprites animada | `sprite-gen` (Apache-2.0, skill de Codex/Claude + CLI) monta el atlas y su `manifest.json`; el paso a GameMaker, que él no trae, lo hace `python3 "$BIB/_indice/atlas-a-gamemaker.py" <run> --salida <carpeta>` → `gm-cli resourcetool script`. Receta en `12/09 §5.2` peldaño 2 ter |
| ¿Este PNG hay que repararlo, o repararlo lo destruye? | `python3 "$BIB/_indice/puerta-pixel-art.py" <carpeta de PNG>` — **antes** de pasarle `pixel-art-fixer` a nada |
| **El usuario me dice dónde tiene sus assets** | `python3 "$BIB/_indice/auditar-biblioteca-assets.py" "<la RAÍZ de su biblioteca>" [--profundidad 3] [--json informe.json] [--solo-fuentes]` — **antes de copiar nada**. Es de solo lectura. Busca cinco señales estructurales, no corazonadas: medios sin licencia (ni heredada ni dentro del `.zip`), varias **familias** de licencia bajo un solo nombre, el **runtime del motor** (un pack no trae `UnityEngine.*.dll`: eso es un juego descompilado), un **extractor guardado junto a los medios**, y el binario de cada tipografía (`fsType`, licencia embebida y los glifos `áéíóúüñ¿¡`, que si faltan **no dan error**: miden cero). **Un bloqueo suyo no es un veredicto y su silencio no es un aprobado**, y apúntala a la RAÍZ: si le das una subcarpeta no puede ver el `.zip` con la licencia que está en otra. Criterio y casos medidos en `07/09 §10 bis.9` |
| **¿Cabe el texto traducido?** | `python3 "$BIB/_indice/medir-caja-de-texto.py" idiomas/*.json --hoja fuente.png --celda 8x11 --mapa-archivo mapa.txt --caja 356 --sep 1 [--espacio 4] [--escala 1.5]` — reproduce `font_add_sprite_ext` y mide **cadena a cadena**. «Diseña con el idioma más largo» NO se aplica en bloque: medido, el español era un 9,1 % más largo en total y aun así **el inglés ganaba en 23 de 79 cadenas**. Caza además los caracteres que faltan en el mapa —**miden cero**, así que mutilan la palabra Y falsean la cuenta— y el espacio sin celda, que GameMaker sustituye por **la anchura del carácter más ancho**. Criterio en `04/21 §4 bis` |
| **Texto en otro idioma que NINGÚN linter caza** | Una **función** que devuelve el texto ya hecho no es un literal, así que el `grep` de «cero cadenas en `draw_text`» no la ve. Medido: `InputVerbGetBindingName()` devuelve «arrow left», «space» y «escape» **en inglés**, en medio de una frase en español — y se descubrió mirando una captura del juego, no el código. `auditar-juego-completo.py` lista ahora las funciones cuyo valor se dibuja tal cual, saltándose `txt()`, las `txt_*` propias y las de número. Criterio en `04/21 §4 ter` |
| Voy a pedirle un sprite a **Retro Diffusion** y cuesta dinero | `python3 "$BIB/_indice/validar-peticion-retrodiffusion.py" peticion.json [--imagen inicio.png] [--presupuesto 0.50]` — **antes de mandarla**. Comprueba el estilo contra el catálogo, el tamaño contra los límites de ese estilo concreto (no los de la API), el lote, las referencias, los prefijos `data:`, y mide el fotograma de partida **en disco**. No usa red ni clave: no puede gastar. Las nueve trampas caras, en `07/23 §1 bis.1` — la primera es que **el POST de v2 no devuelve la imagen** y quien lea `base64_images` de esa respuesta se queda sin nada y con el cargo hecho |
| ¿Las trampas del CLI siguen siendo ciertas hoy? | `bash "$BIB/_indice/verificar-trampas.sh"` — las reproduce contra el CLI instalado. Si alguna ya no se cumple, este documento está desfasado |
| ¿El código reutilizable de la biblioteca hace lo que dice? | `bash "$BIB/_indice/validar-ejecucion.sh"` — monta un juego real y lo **ejecuta**: **200 comprobaciones** sobre los 13 scripts de `06`. Compilar no es ejecutar: sacó cuatro fallos que compilaban limpios. **Valida el banco antes de arrancarlo**, porque un nombre inventado ahí dentro compila con exit 0 y CUELGA la ejecución sin decir nada |
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
`$BIB/_indice/skills/gamemaker-biblioteca/references/mapa-disciplinas.md`. El índice completo de
documentos, generado del disco, en `$BIB/_indice/skills/gamemaker-biblioteca/references/indice-documentos.md`. Las rutas abreviadas de este documento (`13/28`, `04/00`, `12/09`…) siguen el mismo patrón: `$BIB/NN - <carpeta>/MM - <archivo>.md` — primero la carpeta por su número, luego el archivo dentro de ella por el suyo.

| Te piden… | Empieza por |
|---|---|
| Escribir GML que haga X | `buscar.py` por cada símbolo → `11 - Código descargado/_CATALOGO.md` (¿ya hay librería?) → `05 - Referencia/04 - Convenciones y estilo GML.md` |
| Un juego completo, de principio a fin | `04 - Recetas por género/00 - Anatomía de un juego completo.md` y después la receta del género |
| Un juego de género X | `04 - Recetas por género/` — **59 recetas**: los géneros clásicos (plataformas, RPG, roguelike, metroidvania, tower defense, puzle, shoot'em up, carreras, gestión, ritmo, sigilo, horror, granja, idle) más beat'em up, aventura gráfica, deportes, lucha, souls-like, colonia, party games y bullet heaven/autobattler/deckbuilder; y los sistemas transversales: **el nivel como mapa de texto** (la única vía de montar un nivel sin abrir el editor de salas), **puertas, llaves y placas de presión** (el puzle de sala), combate (cuerpo a cuerpo, a distancia, por turnos, no letal), daño y estados, enemigos y director, habilidades, traversal, pathfinding, VFX, tutorial, transiciones y pausa, audio reactivo, modding, eje Z falso, selección de nivel, metajuego y live-ops |
| Diseñar: mecánicas, niveles, arte, UI, sonido, historia | `13 - Diseño y producción de videojuegos/` (mapa en `$BIB/_indice/skills/gamemaker-biblioteca/references/mapa-disciplinas.md`) |
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

> 🎮 **Y si lo que quieres es ver un juego ENTERO montado**, no una pieza suelta:
> `14 - Juego de referencia/` trae «Enjambre» completo —especificación previa, arte y
> sonido generados por código, portada, menú, opciones, pausa, derrota, guardado con
> versión y checksum, dos idiomas y mando—, con la fuente entera y los generadores
> para reconstruirlo. Compila y se ejecuta. Su README dice qué mirar para cada cosa.

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

> 🖥️ **Y lo que NO está verificado, dicho por delante para que no lo descubras tú.**
> El desarrollo de juegos de esta skill se ha ejecutado entero en **macOS arm64**. Las
> **herramientas de `_indice/` sí se han ejecutado en Windows** (Python 3.12.7 de Windows
> sobre Wine): 12 de 14 pasan y las otras 2 dicen «falta Pillow, no he mirado nada», que es
> la respuesta correcta. Por el camino salieron cuatro fallos —`os.kill` en Windows no
> pregunta, **mata**; un proceso muerto parece vivo si solo miras `OpenProcess`; sin `grep`
> las búsquedas decían «no existe» en vez de «no he mirado»; y seis herramientas reventaban
> al imprimir un `✓`—, todos corregidos.
> **En Windows también se ha ejecutado el JUEGO**: compilado con `--target windows` desde
> el Mac y corrido bajo Wine — DirectX11 por hardware, menús navegados y partida guardada
> con su checksum correcto. Lo que sigue sin probarse ahí es el **IDE** y el empaquetado
> final (`package --target windows` necesita Windows de verdad, Trampa 19). El peldaño de *computer use* está **razonado, nunca medido**. Y de **Kimi y Qwen**
> solo está comprobado que reciben la skill íntegra, no que la activen — Qwen, además,
> declara `~/.claude/skills` y no `~/.qwen/skills` en su `settings.json`.
> Detalle en `_indice/auditorias/r19-cobertura-y-portabilidad.md`.

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
3 bis. **Las cuatro decisiones que cuestan REESCRIBIR si las tomas tarde.** Las cuatro parecen
   detalles de pulido y las cuatro son arquitectura. Todas se descubrieron cayendo en ellas al
   construir «Enjambre» (`_indice/auditorias/r18-prueba-visual.md`) **con esta skill delante**:
   documentar una trampa no basta si el flujo no obliga a esquivarla antes de que muerda.

   **a · La fuente, antes de la primera línea de interfaz.** `draw_set_font(-1)` compila limpio
   y **se come las tildes en silencio**: «Créditos» sale «Crditos» (trampa 12). La salida buena
   para un agente es una fuente de sprite:

   ```sh
   python3 "$BIB/_indice/pruebas/generar_glifos.py" <carpeta>   # 89 PNG + mapa.txt
   ```
   ```gml
   global.fnt = font_add_sprite_ext(spr_glifos, "<el contenido de mapa.txt>", true, 1);
   draw_set_font(global.fnt);   // y NUNCA draw_set_font(-1) en un juego en español
   ```

   Y lo mismo vale para **los símbolos que no son letras**: el marcador de vidas usaba «▮», que
   tampoco está en la hoja, y salió vacío. Para iconos, dibuja un sprite.

   **b · La resolución y la escala de cámara.** Una sala del tamaño de la ventana —1366×768—
   con naves de 24 px produce un juego que **parece vacío**: se ven motas de color. Decidirlo
   después de dibujar los sprites significa rehacerlos.

   ```gml
   // sala de 683×384 en ventana de 1366×768 = cada píxel del mundo ocupa cuatro
   var _cam = camera_create_view(0, 0, room_width, room_height, 0, noone, -1, -1, 0, 0);
   view_set_camera(0, _cam); view_set_visible(0, true); view_enabled = true;
   ```

   El HUD **no** se escala con eso —vive en Draw GUI, en coordenadas de pantalla— y es justo lo
   que se quiere. Detalle en `13/03` y `04/24`.

   **c · El texto, por clave desde el primer `draw_text`.** Escribir `draw_text(x, y, "Puntos")`
   y traducir después significa tocar cada llamada de dibujo del juego. Con una función
   `txt("puntos")` desde el principio, el segundo idioma cuesta una tabla y cero refactor —
   y `auditar-juego-completo.py` lo comprueba, porque es un fallo que se repite.

   **d · La entrada, en UNA función.** `keyboard_check` esparcido por diez objetos convierte
   «que funcione con mando» en una reescritura. Una sola `entrada_leer()` que devuelva un
   struct con las acciones —no con las teclas— lo hace gratis. **Y hay un segundo beneficio que
   no es obvio**: con la entrada en un solo sitio, el juego se puede **conducir solo** para
   probarlo. La prueba visual de `r18` —siete pantallas recorridas y fotografiadas— existe
   porque había una única puerta por la que inyectar la entrada simulada; con diez, no habría
   sido viable.

3 quater. **Si el usuario te dice dónde tiene SUS assets, hay un método y no es «buscar
   lo que encaje».** Es el encargo real —«tengo packs en este disco, úsalos»— y tiene una
   trampa: los assets libres traen su licencia declarada, pero una biblioteca personal es
   una mezcla de packs comprados, bundles y carpetas sin origen. Todo está en
   `07 - Ecosistema/09 - Asset packs y recursos gráficos.md` §10 bis.
   El resumen que no puedes saltarte:

   - **Licencia primero, encaje después.** Si buscas por lo que te gusta, acabas
     enamorado de un pack que no puedes tocar. Y **el índice de la biblioteca NO es la
     licencia**: hay que abrirla pack a pack.
   - **Tres filtros, no uno**: licencia · **estilo** (¿se dibuja como mi juego?) ·
     **encaje** (¿mi tema y mi resolución?). Los dos últimos se subestiman siempre y son
     los que hacen que un juego con arte comprado se vea peor que uno con arte propio:
     un pack CC0 impecable de «naves» resultó ser aviones de la Segunda Guerra Mundial.
   - **«Usarlo» y «redistribuirlo» no son lo mismo.** Muchas licencias permiten meterlo en
     tu juego compilado y prohíben subir el archivo suelto a un repositorio público.
   - **Tipografías: dos comprobaciones.** Que tenga `á é í ó ú ñ ¿ ¡` —GameMaker omite en
     silencio el glifo que falta— y qué dice **el binario**, que puede contradecir al pack.
   - **Si no encuentras la licencia, no entra — y lo dices.** Separando «lo prohíbe» de
     «no la he encontrado»: lo segundo el usuario sí puede resolver buscando su factura, y
     callarlo puede costarle el mejor arte de su juego.
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
      sin un solo error. Y de **sprites de personaje que son un color plano**, que son el
      rectángulo prohibido guardado como PNG en vez de dibujado — el detector de rectángulos no
      los ve porque el objeto sí tiene sprite. Y de tres cosas más del checklist de `04/00` que
      una máquina sí puede mirar: si **alguien dibuja en Draw GUI** (donde viven el HUD y los
      menús), si hay **texto escrito a pelo en un `draw_text`** —que no se puede traducir— y si
      el **splash o la intro se pueden saltar**.
      **Y te lista los recursos que creas y no destruyes nunca**: `ds_*`, superficies,
      buffers, partículas, *vertex buffers*, emisores de audio y *time sources*. GameMaker
      no los recoge solo —los structs y los arrays sí, estos no—, así que cada entrada en
      la sala deja otro y el juego que va fino en dos minutos se arrastra a la media hora.
      Es la clase de fallo que no sale probando cada mecánica por separado, solo cuando dos
      estados se cruzan: la lista entera, con la tanda para cazarlos, está en `13/10 §12 bis`.
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
   d. **Si no puedes ejecutar el juego** (sin `run`, sin pantalla, tarea de fondo), quedan dos
      redes, y conviene tender las dos:
      · **Recompón la pantalla fuera del motor** —los mismos PNG, la misma rejilla, el mismo
        orden de dibujo, unas 150 líneas con Pillow— y **mírala**: `13/10 §8.6`, procedimiento
        1 bis. Es lo que más ha cazado: un signo invertido en el encaje de cámara y un panel que
        se salía de pantalla, dos cosas que ni el compilador ni las preguntas de abajo ven.
        **Y di que es una maqueta**, no una captura: reproduce tu lectura del código, no el
        código, y no vale para dar por buena la trampa 5.
      · Las **seis preguntas de `13/10 §8.8`**, que se responden leyendo y cazan la otra clase
        de fallo — guardas de pausa mal colocadas, ramas que olvidan un caso, métodos ligados a
        instancias que mueren.
      Y di explícitamente qué quedó sin comprobar por no poder ejecutar.
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
