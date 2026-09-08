# AGENTS.md — Biblioteca GameMaker (generado desde la skill)

> **Generado por `_indice/sincronizar-skill.py` a partir del cuerpo real de**
> **`SKILL.md`. No lo edites a mano:** se reescribe en cada `python3 _indice/actualizar.py`
> o `./instalar.sh`. Existe para los CLI de IA que solo leen `AGENTS.md` en la raíz
> de un proyecto y no tienen un directorio de skills en formato `SKILL.md` — copia
> este archivo (o enlázalo) como `AGENTS.md` en la raíz de tu proyecto de GameMaker.
> Si tu CLI sí lee skills, usa directamente la carpeta
> `_indice/skills/gamemaker-biblioteca/` — no hace falta este archivo.

**Cuándo aplica esto:** Fuente fidedigna para desarrollar con GameMaker LTS 2026 y GML. Úsala antes de escribir o revisar GML, ante cualquier duda de API (¿existe esta función?, firma, obsoleta, manual), y al planificar o construir un juego con GameMaker en cualquiera de sus disciplinas: diseño de juego y GDD, niveles, mundo, pixel art, animación, VFX y shaders, UI/UX y accesibilidad, cámaras, arquitectura y patrones, generación procedural, físicas y fluidos, combate y enemigos, IA, pathfinding, progresión, sonido y voz, testing, producción, negocio, narrativa, matemáticas, móvil y 3D; y para publicar: firmar, notarizar, subir a Steam, Play, App Store y consolas (Nintendo, PlayStation, Xbox). Dispara con GameMaker, GML, gm-cli, resourcetool, archivos .yyp/.yy/.gml, «hazme un juego», «publicar mi juego», y con «no compila» o «se comporta raro» en un proyecto GameMaker.

# GameMaker · biblioteca fidedigna

Una base de conocimiento local, en español, verificada contra el runtime instalado. Existe
para que el GML que escribas **no invente nada** y para que cada decisión de diseño tenga
detrás un documento contrastado.

```sh
BIB="${GM_BIBLIOTECA:-$(cat ~/.config/gamemaker-biblioteca/ruta 2>/dev/null)}"
```

Esa línea abre **cada** comando de esta skill: la biblioteca está donde la instalaron, no en una
ruta fija. La escribe `instalar.sh` al copiar la skill; `$GM_BIBLIOTECA` la pisa si hace falta.

Si `$BIB` sale vacío, la biblioteca no está instalada en esta máquina: dilo, y cae a
`gm-cli manual read "<símbolo>"` para cada duda. **Nunca a la memoria.**

## La regla que gobierna todo

**Cada símbolo de GML se verifica antes de escribirlo — la firma ENTERA, no solo que exista**:
confirmar el nombre y adivinar los argumentos «porque suenan razonables» es el fallo que cuela
código roto (caso real en `_indice/auditorias/r5-revalidacion.md`).

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

## Las diez trampas que hacen fracasar a un agente

Verificadas en vivo contra `gm-cli` 2.3.0 y el runtime 2026.0.0.23. Léelas **antes** de ejecutar
el primer comando; el detalle y las tablas completas están en
`12 - Utilidades e integraciones/09 - Manual del agente de IA - operar GameMaker con gm-cli.md`.

1. **`resourcetool` y `compile` se cuelgan bajo el sandbox del Bash de Claude Code.** La causa es
   la capa `npx` interna que descarga del registro de GameMaker. Si un comando se queda colgado
   sin salida, no es que tarde: ejecútalo con el sandbox desactivado, o invoca el binario
   `ResourceTool` cacheado directamente (responde en 0,3 s).
2. **9 de las 18 plantillas de `gm-cli init` fallan en macOS** con `PREFABS RESTORE exited with
   code 1`, y actualizar no lo arregla. Usa una de las que funcionan —*Space Rocks*, *Blank Pixel
   Game*, *Tower Defense*, *RPG Starter Pack*—; la tabla completa está en `12/09`.
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
| Compilar (desde la carpeta del `.yyp`) | `gm-cli compile` · ejecutar: `gm-cli run` |
| Crear o editar recursos (objetos, sprites, rooms, eventos) | `gm-cli resourcetool eval "<comando>"` o el MCP `gamemaker-resource-tool` del proyecto |
| Proyecto nuevo | `gm-cli init --no-interactive -n <nombre> -t "Space Rocks" --ai --toolchain GMS2@2026.0.0.23` |

Las plantillas con *prefabs* fallan en `gm-cli` 2.3.0 en macOS: usa *Space Rocks* o *Blank
Pixel Game*. El manual `monthly` está discontinuado; la rama vigente es **LTS 2026.0**.

## Qué leer según la tarea

El detalle por disciplina, en orden de lectura, está en
[`references/mapa-disciplinas.md`](references/mapa-disciplinas.md). El índice completo de
documentos, generado del disco, en [`references/indice-documentos.md`](references/indice-documentos.md).

| Te piden… | Empieza por |
|---|---|
| Escribir GML que haga X | `buscar.py` por cada símbolo → `11 - Código descargado/_CATALOGO.md` (¿ya hay librería?) → `05 - Referencia/04 - Convenciones y estilo GML.md` |
| Un juego completo, de principio a fin | `04 - Recetas por género/00 - Anatomía de un juego completo.md` y después la receta del género |
| Un juego de género X | `04 - Recetas por género/` — 46 recetas: los 15 géneros clásicos más combate (cuerpo a cuerpo, a distancia, por turnos), daño y estados, enemigos y director, habilidades, traversal, pathfinding, VFX, tutorial, transiciones y pausa, audio reactivo, modding, bullet heaven/autobattler/deckbuilder, y sigilo/horror/granja/idle |
| Diseñar: mecánicas, niveles, arte, UI, sonido, historia | `13 - Diseño y producción de videojuegos/` (mapa en `references/mapa-disciplinas.md`) |
| Estructurar el proyecto para que crezca | `13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md` |
| Explicar un concepto del motor | `01 - Fundamentos/` → la página del manual en `09 - Manual oficial/manual-lts-2026-es/` |
| «No compila» o «se comporta raro» con código antiguo | `01 - Fundamentos/03 - Handles - el cambio clave de 2026.md` → `02 - Novedades 2026/02 - Cambios en GML 2026.md` → `buscar.py` (¿obsoleta?) → github.com/YoYoGames/GameMaker-Bugs |
| Qué librería, extensión o herramienta usar | `12 - Utilidades e integraciones/_INDICE-UTILIDADES.md` → `11 - Código descargado/_CATALOGO.md` → `07 - Ecosistema/` |
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
- Nada está «hecho» sin `gm-cli compile` limpio y su salida real reportada. `--errors-only`
  sirve para iterar rápido, pero **antes de dar un juego por terminado, compílalo al menos una
  vez sin ese flag y lee los avisos**: es el único modo que muestra el `WARNING` de un
  *included file* sin copiar (trampa 8). Y **compilar limpio no es funcionar**: la fuente muda y
  el guardado roto de las trampas 5 y 6 compilan sin una queja (`13/10 §8.6` da las dos
  comprobaciones que sí los cazan).
- No declares un juego «terminado» sin compararlo punto por punto con el checklist maestro de
  `04/00`. Si algo falta o no aplica, dilo; el silencio no vale.

## Flujo para un desarrollo real

0. **Especificación**: si el encargo es «hazme un juego» y no trae ya género, alcance y
   plataforma decididos, pregúntalos en un único turno (nunca un interrogatorio secuencial) y
   completa con los valores por defecto lo que el usuario no conteste — preguntas, criterio de
   parada, defaults y plantilla en `13/28`. Escribe la especificación y **enséñasela al usuario
   antes de crear el proyecto**: no hay paso 2 sin este documento escrito primero.
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
7. **Antes de decir «terminado»**: compara el resultado, pantalla por pantalla, contra el
   checklist maestro de `04/00 - Anatomía de un juego completo` (menú, pausa, opciones, guardado,
   fin de partida, créditos, icono y versión del build) y contra `13/05 §4`. Lo que recortes, se
   dice; no se omite en silencio.
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
