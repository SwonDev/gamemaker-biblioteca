# AGENTS.md — cómo usar esta biblioteca si eres un agente de IA

> **Léeme entero antes de escribir una sola línea de GML.**
> Este repositorio no es un proyecto de GameMaker: es una **base de conocimiento** sobre
> GameMaker, en español, pensada para que un modelo de lenguaje pueda desarrollar cualquier
> proyecto con el motor sin inventarse nada.

**Versión de referencia:** GameMaker **LTS 2026.0** · IDE `2026.0.0.16` · runtime GMS2 `2026.0.0.23`
**Canal Beta vigente:** `2026.100.0` (IDE 1142 / runtime 1093, 02-09-2026, verificado 07-09-2026) · **GMRT** Beta `0.21`

---

## 1. La regla que lo gobierna todo

**No inventes funciones de GML.** El motor tiene exactamente **2 357 funciones**, **886
constantes**, **210 variables**, **33 structs incorporados** y **13 enumeraciones**. Están
todas listadas aquí, extraídas del `GmlSpec.xml` del runtime instalado.

Antes de usar cualquier símbolo:

```sh
python3 "_indice/buscar.py" nombre_de_la_funcion
```

- Si aparece → te da la firma exacta, el tipo de retorno, si está obsoleta, la página del
  manual (en español y en inglés) y **dónde se usa de verdad** en código real descargado.
- Si no aparece → **no existe**. No la escribas. El buscador te sugiere alternativas parecidas.

Comprobación cruzada con el manual oficial offline:

```sh
gm-cli manual read "nombre_de_la_funcion"
```

---

## 1 bis · Los tres ficheros que te orientan

| Fichero | Qué es | Cuándo lo lees |
|---|---|---|
| [`_indice/COMO-BUSCAR.md`](./_indice/COMO-BUSCAR.md) | **Árbol de decisión completo**: qué te piden → dónde mirar → en qué orden | Si no sabes por dónde empezar |
| [`_indice/MAPA.json`](./_indice/MAPA.json) | El mismo mapa **legible por máquina**: cada carpeta con su propósito, cuándo usarla, para qué no, y todos sus documentos con título. Se sincroniza solo: no lo edites para añadir un documento | Si prefieres parsearlo |
| [`_indice/simbolos.json`](./_indice/simbolos.json) | Todos los símbolos de GML cruzados con el manual, la documentación y el código real. El recuento exacto está en su propio `meta` | Lo consulta `buscar.py` por ti |

**Orden de autoridad cuando las fuentes se contradicen** (de mayor a menor):

```
1. _indice/simbolos.json   → sale del GmlSpec.xml del runtime instalado
2. 09 - Manual oficial/    → espejo de manual.gamemaker.io, rama LTS
3. 02 - Novedades 2026/    → release notes y blog oficial, con fecha
4. 01, 04, 05, 08, 13      → documentación propia, verificada
5. 11 - Código descargado  → código real: muestra la práctica, no la norma
6. 03, 10 - Cursos         → pueden estar desfasados; llevan aviso
```

Un tutorial de YouTube **nunca** gana a `simbolos.json`.

---

## 2. Mapa de decisión: dónde buscar según lo que necesites

| Necesito… | Voy a… |
|---|---|
| Saber si una función existe y cómo se llama | `python3 "_indice/buscar.py" <símbolo>` |
| La página oficial completa de una función | `09 - Manual oficial/manual-lts-2026-es/…` (y `-en` si no está traducida) |
| Entender un concepto desde cero, en español | `01 - Fundamentos/` |
| Saber qué cambió en 2026 y qué me va a romper | `02 - Novedades 2026/` |
| Aprender siguiendo un curso | `03 - Cursos (YouTube)/` · `10 - Cursos en español/` |
| Construir un juego de un género concreto | `04 - Recetas por género/` |
| Consulta rápida: glosario, estilo, publicación | `05 - Referencia/` |
| Código listo para copiar, escrito para esta biblioteca | `06 - Assets y Scripts/` |
| Qué librería/extensión existe para X | `07 - Ecosistema/` · `11 - Código descargado/_CATALOGO.md` |
| Assets libres: arte, música, SFX, tilesets, fuentes | `07 - Ecosistema/09 - Asset packs y recursos gráficos.md` |
| La API completa agrupada por familias | `08 - Referencia GML completa/_API del runtime/` |
| Ver cómo lo resuelve gente real | `python3 "_indice/buscar.py" --codigo "<lo que sea>"` |
| Herramientas y utilidades para integrar | `12 - Utilidades e integraciones/` |
| Diseñar el juego, no solo programarlo: mecánicas y balance, niveles, pixel art, animación, UI/UX, arquitectura, procgen avanzada, físicas a mano y fluidos, sonido, testing, producción, narrativa, matemáticas | `13 - Diseño y producción de videojuegos/` |
| Comprobar TODO el GML de un proyecto real antes de compilar | `python3 "_indice/validar-proyecto.py" <ruta-del-proyecto>` |
| Saber si lo que entregas es un juego o solo su bucle | `python3 "_indice/auditar-juego-completo.py" <ruta-del-proyecto>` |
| Usar esta biblioteca desde OTRO proyecto (Claude Code o Codex) | la skill `gamemaker-biblioteca`, en `_indice/skills/gamemaker-biblioteca/SKILL.md` (enlazada desde `~/.claude/skills` y `~/.codex/skills`) |
| Aprender en español, o consultar un curso sin verlo | `10 - Cursos en español/` (los documentos 06 y 07 son transcripciones completas) |
| No sé por dónde empezar | [`_indice/COMO-BUSCAR.md`](./_indice/COMO-BUSCAR.md) |

---

## 3. Cómo está montado el índice

```
_indice/
  buscar.py             Buscador CLI. Funciona sin conexión. Es tu primera parada.
  actualizar.py         El único comando de mantenimiento (ver más abajo).
  simbolos.json         Cada símbolo → firma, manual (es/en), documentos que lo
                        explican, repositorios donde se usa de verdad.
  documentos.json       Todos los documentos de la biblioteca con su título.
  MAPA.json             El mapa legible por máquina. Se sincroniza solo.
  validar-proyecto.py   Valida el GML de un PROYECTO real: funciones inventadas y obsoletas.
  auditar-juego-completo.py
                        Detecta qué piezas del envoltorio (menú, opciones, pausa, guardado,
                        créditos, fin de partida, sonido, mando, arranque por portada) NO
                        aparecen en un proyecto, y qué objetos sin sprite pintan rectángulos.
  skills/gamemaker-biblioteca/
                        La skill para Claude Code y Codex: cómo usar esta biblioteca
                        desde cualquier proyecto. Su índice de documentos se genera solo.
  verificar-enlaces.py  Comprueba las rutas internas.  ─┐ los llama
  construir-indices.py  Regenera los índices y el mapa. ─┤ actualizar.py
  sincronizar-skill.py  Regenera el índice de la skill  ─┘ y comprueba sus rutas.
```

Los recuentos exactos están en el `meta` de cada índice, no escritos en esta prosa: **una
cifra a mano en un documento se queda vieja y nadie se entera.**

Modos de `buscar.py`:

```sh
python3 "_indice/buscar.py" draw_sprite_ext        # ficha de un símbolo
python3 "_indice/buscar.py" --listar audio_        # todos los símbolos de una familia
python3 "_indice/buscar.py" --texto "coyote time"  # busca en la biblioteca en español
python3 "_indice/buscar.py" --manual "surface"     # busca en el manual oficial espejado
python3 "_indice/buscar.py" --codigo "state"       # busca en el código GML descargado
```

---

## 3 bis. Si añades o cambias contenido: un solo comando

```sh
python3 _indice/actualizar.py
```

Eso es todo. Hace, en orden y parando al primer fallo real:

0. **Se comprueba a sí mismo primero.** Las tres herramientas que dan garantías
   —`verificar-enlaces.py`, `validar-codigo-gml.py`, `auditar-juego-completo.py`,
   `validar-proyecto.py`, `puerta-pixel-art.py` y `validar-integracion.py`— pasan sus propias
   autopruebas (**67 casos** que
   ya han mordido de verdad) **antes** de que nadie se fíe de lo que digan. Un validador que deja de validar no falla: calla, y un aviso que no salta se lee
   igual que «está todo bien». Si el metro está mal, da igual lo que mida. Cada una se puede
   correr suelta con `--autoprueba`.
1. **Verifica los enlaces internos** — cero rotos o no sigue. Y con ellos, dos cosas que
   no son enlaces y nadie comprobaba: que ningún documento **repita un número de sección**
   (una cita «§N» ahí es ambigua) y que las **2 272 citas por número** del tipo
   «`13 · 10 §8.7`» resuelvan a una sección que existe de verdad.
2. **Regenera** `documentos.json` y `simbolos.json` desde el disco, incluido el cruce
   «qué documento explica este símbolo».
3. **Sincroniza `MAPA.json`**: descubre los documentos nuevos, actualiza títulos y recuentos.
4. **Comprueba** que el mapa no apunte a nada que ya no exista.
5. **Revisa la ortografía española** (tildes ausentes), ignorando el código y los títulos
   citados literalmente.
6. …y sigue con la cobertura de la API, la prueba de descubrimiento, el código GML de los
   documentos y, por último, **la skill `gamemaker-biblioteca`**: regenera su índice de
   documentos y comprueba que cada ruta que cita existe.

Sale con **0** solo si no queda deuda. Si algo necesita a una persona, lo dice por su nombre.

**Tres comprobaciones más viven aparte porque tardan y necesitan GameMaker instalado.**
Córrelas antes de publicar:

| Comando | Qué demuestra |
|---|---|
| `bash _indice/validar-compilacion.sh` | Los 13 scripts de `06` compilan contra el runtime real |
| `bash _indice/validar-ejecucion.sh` | Y además **hacen lo que dicen**: 189 comprobaciones dentro de un juego que se ejecuta |
| `bash _indice/verificar-trampas.sh` | Las 7 trampas comprobables de `12 · 09 §0` **siguen** siendo ciertas con el CLI de hoy |

### Qué pasa cuando YoYo publica un runtime nuevo

Los símbolos **se re-derivan del `GmlSpec.xml` del runtime instalado** en cada ejecución. No
son una copia congelada: si aparece un runtime nuevo, `actualizar.py` lee su spec y **te dice
qué símbolos se han añadido y cuáles se han retirado**, para que revises si algún documento
usa los que ya no existen.

Y mientras tanto, `buscar.py` **no se calla**: en cada consulta compara el runtime instalado
con el que generó el índice y, si no coinciden, avisa antes de dar la ficha:

```
⚠ ÍNDICE CADUCADO: se generó con el runtime 2026.0.0.23 pero el instalado es 2026.1.0.0.
  La API puede haber cambiado. Regenera antes de fiarte de esta ficha:
      python3 _indice/actualizar.py
```

**Un índice caducado que calla es peor que no tener índice**: el LLM se cree la respuesta
vieja. Por eso el aviso sale siempre, incluso al decir que algo no existe.

> ⚠️ **No añadas documentos a `MAPA.json` a mano.** Los descubre el comando. Lo único que
> escribe una persona es la prosa de criterio —`proposito`, `usar_cuando`, `no_usar_para`—
> y solo al crear una carpeta nueva, momento en el que el comando avisa.

---

## 4. Prohibiciones duras

- ❌ **No edites `.yy` ni `.yyp` a mano.** El formato es frágil y se corrompe. Los recursos
  (objetos, sprites, rooms, eventos) se crean con el MCP `gamemaker-resource-tool` o con
  `gm-cli resourcetool eval "<comando>"`. El código `.gml` sí se edita con normalidad.
  **Excepción verificada el 2026-09-06**: el asset **Extensión** no se puede crear con
  `gm-cli resourcetool` — `resource types` devuelve 17 tipos y `extension` no es uno de ellos, y
  forzarlo (`resource create type=extension`) responde `Resource type 'extension' is not
  creatable`. Solo se crea desde el IDE. Guía completa en
  [`07 - Ecosistema/22 - Crear una extensión nativa (guía en español).md`](./07%20-%20Ecosistema/22%20-%20Crear%20una%20extensi%C3%B3n%20nativa%20%28gu%C3%ADa%20en%20espa%C3%B1ol%29.md).
- ❌ **No supongas una firma.** «Creo que era así» no es una fuente. Consulta `buscar.py`.
- ❌ **No uses eñes ni tildes en identificadores de GML.** El compilador exige **ASCII puro**:
  `function añadir()` no compila (`invalid token`). Los nombres propios van sin acentuar
  (`function anadir`, `var _numero_niveles`); el texto en español, que sí lleva ortografía
  completa, va en cadenas y comentarios, nunca en el propio identificador.
  `python3 _indice/validar-codigo-gml.py` ya detecta estos identificadores y los marca en rojo.
- ❌ **No uses aritmética con IDs de assets.** En 2026 son *handles*, no enteros.
  `sprite_index + 1` está muerto. Lee `01 - Fundamentos/03 - Handles`.
- ❌ **No uses funciones marcadas como obsoletas** (hay 171). `buscar.py` te avisa.
- ❌ **No copies código de los juegos comerciales extraídos** (Pizza Tower, Deltarune, AM2R,
  Hotline Miami, Kirby). Están para leer y aprender, no son libres.
- ❌ **No des una tarea por terminada sin compilar.** `gm-cli compile` y reporta el resultado real.

---

## 5. Flujo recomendado para desarrollar un proyecto

0. **Especificación primero.** «Hazme un juego de X» **es** un encargo que incluye diseñar,
   aunque no lo diga con esas palabras: si no trae ya una especificación (un GDD, una ficha de
   sistema, o las respuestas a las preguntas de arranque), pregúntalas en un único turno y
   escribe la especificación antes de seguir — preguntas, criterio de parada, valores por
   defecto y plantilla en
   [`13 - Diseño y producción de videojuegos/28`](./13%20-%20Diseño%20y%20producción%20de%20videojuegos/28%20-%20De%20hazme%20un%20juego%20a%20una%20especificación%20-%20el%20protocolo%20de%20elicitación%20del%20agente.md).
   No se crea el proyecto (paso 3) sin ese documento escrito y enseñado al usuario.
1. **Lee la receta del género** en `04 - Recetas por género/`. Te dice qué sistemas construir
   y en qué orden. Si el encargo incluye diseñar (mecánicas, niveles, arte, UI, sonido,
   historia) o producir (alcance, hitos, lanzamiento), pasa antes por
   `13 - Diseño y producción de videojuegos/`.
2. **Mira si ya existe una librería** que resuelva cada sistema: `11 - Código descargado/_CATALOGO.md`.
   Entrada, texto, diálogos, audio, guardado y UI ya están resueltos por terceros.
3. **Crea el proyecto**:
   ```sh
   gm-cli init --no-interactive -n mi-juego -t "Space Rocks" --ai --toolchain GMS2@2026.0.0.23
   ```
   ⚠️ Las plantillas con *prefabs* fallan en `gm-cli` 2.3.0 en macOS: de las 18 plantillas de
   juego, **9 fallan y 9 funcionan** (no solo *Platformer*). Usa *Space Rocks* o
   *Blank Pixel Game* — ambas funcionan —, o crea el proyecto desde el IDE. Tabla completa de
   las 18, verificada una a una, y las otras doce trampas que hacen fracasar a un agente hoy
   (`resourcetool`/`compile` colgados bajo sandbox, el evento equivocado sin avisar, funciones
   inventadas que el compilador no detecta, fuentes que compilan y no dibujan texto, guardado
   que falla en silencio bajo `gm-cli run`, dar un comando por imposible sin haber probado la
   raíz de expresión `project`, un *included file* de `resourcetool` que no llega al paquete
   compilado sin que `--errors-only` lo delate, una *whitelist* cerrada de un subcomando
   (`OBJECT EVENT FINDORCREATE`) que no significa que la propiedad cruda del recurso sea
   inalcanzable por `RESOURCE SET`, **la fuente por defecto del motor, que no tiene glifos de
   `á é í ó ú ñ ¿ ¡` y los omite en silencio** — grave para una biblioteca entera en español —,
   y `screen_save()`, que en Mac invierte la imagen verticalmente mientras la ventana real se ve
   bien) en
   [`12 - Utilidades e integraciones/09 - Manual del agente de IA`](./12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#0--las-quince-trampas-que-hacen-fracasar-a-un-agente-hoy)
   — léelo entero si vas a operar este repo por terminal, es la guía específica para agentes.
4. **Escribe GML** verificando cada símbolo con `buscar.py` antes de usarlo. Al terminar,
   `python3 "_indice/validar-proyecto.py" <ruta-del-proyecto>` lista cualquier función
   inventada u obsoleta que se haya colado, con la parecida que sí existe.
5. **Sigue las convenciones** de `05 - Referencia/04 - Convenciones y estilo GML.md`:
   `snake_case`, locales con `_` (`var _speed`), prefijos `obj_ spr_ snd_ rm_ scr_`.
   Nada de nombres reservados (`x`, `y`, `speed`, `direction`, `id`, `depth`, `score`, `health`).
6. **Compila y corrige** hasta que salga limpio: `gm-cli compile`. Pero **compilar limpio no es
   funcionar**: una fuente sin glifos y un guardado roto compilan sin una queja. Las dos
   comprobaciones que sí los cazan —capturar la pantalla y mirarla, y verificar el guardado
   matando el proceso y reabriéndolo— están en
   [`13 - Diseño y producción de videojuegos/10 - Testing y QA.md §8.6`](./13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/10%20-%20Testing%20y%20QA.md).
7. **Antes de decir «terminado»**, compara el resultado punto por punto con el checklist maestro
   de [`04 - Recetas por género/00 - Anatomía de un juego completo.md`](./04%20-%20Recetas%20por%20g%C3%A9nero/00%20-%20Anatom%C3%ADa%20de%20un%20juego%20completo.md):
   menú, pausa, opciones, guardado, fin de partida, créditos, icono y versión del build. Un juego
   sin envoltura es un prototipo, no un juego. **Lo que recortes, se dice**; omitirlo en silencio
   es lo que convierte un encargo en una entrega a medias.

---

## 5 ter. El índice cubre DOS fuentes del runtime

`buscar.py` indexa **3 486 símbolos** procedentes de dos archivos del runtime instalado:

- **`GmlSpec.xml`** — la lista que usan el IDE y Feather (3 452 símbolos).
- **`fnames`** — una segunda lista del mismo runtime con **34 símbolos que `GmlSpec.xml` no
  declara**, entre ellos las 19 constantes `*_CHARSET` (juegos de caracteres para `font_add`
  con alfabetos no latinos) y las funciones `flexpanel_node_set_data` y `rollback_use_late_join`.

Los de `fnames` salen marcados con **⚠️ SOLO EN `fnames`**. Significa que **existen en el
runtime pero Feather no los reconoce**: no hay autocompletado y conviene probarlos antes de
apoyarse en ellos. No son invenciones y no hay que descartarlos.

Detalle en
[`08 - Referencia GML completa/20`](./08%20-%20Referencia%20GML%20completa/20%20-%20Lo%20que%20el%20manual%20no%20documenta.md).

---

## 5 bis. Situar el nivel del usuario antes de enseñar

Si el usuario está **aprendiendo** (no resolviendo una duda puntual), lee
**[`RUTA.md`](./RUTA.md)** y sitúalo por **lo que sabe hacer**, no por lo que dice saber.
Después dale **solo material de su nivel y del siguiente**.

Dar contenido de nivel 4 (shaders, optimización) a alguien de nivel 1 (aún no mueve un
personaje) es la forma más rápida de bloquearlo. Cada nivel de `RUTA.md` trae una **prueba
concreta** que sirve para diagnosticar sin preguntar.

---

## 6. Qué está verificado y qué no

- Los **3 119 documentos del manual en inglés** y los **3 033 en español** son espejo directo
  de `manual.gamemaker.io`, descargados el 1 de septiembre de 2026. Cada página lleva al final
  la URL oficial de la que procede.
- ✅ **El manual está completo en español.** La traducción oficial de YoYo Games llegaba al
  86 %: dejó **431 páginas en inglés**, justo las de las funciones de 2026, y además **3 181
  celdas de tablas de argumentos en inglés** dentro de páginas que sí había traducido. Todo
  eso está traducido para esta biblioteca; las **401 páginas** que se rehicieron enteras
  llevan la marca `<!-- traducido-por-la-biblioteca -->`. **No queda ni una página en inglés
  dentro de `manual-lts-2026-es/`**, así que puedes citar el espejo español directamente. El
  inglés sigue disponible en `manual-lts-2026-en/` en la misma ruta para contrastar. Detalle
  del método y de cómo reanudarlo si YoYo publica páginas nuevas:
  `_indice/traduccion/README.md`.
- El **catálogo de la API** sale del `GmlSpec.xml` del runtime real instalado. No es una
  recopilación de internet.
- Los **608 repositorios** se han clonado del GitHub original y llevan sus estrellas, licencia
  y fecha de último cambio reales, consultadas por la API de GitHub.
- Lo **no verificado** se marca con ⚠️ en el texto. Si algo no lleva marca, es porque se
  comprobó contra una fuente primaria.

---

## 7. Credenciales

**Nunca copies una credencial a un archivo.** Ni a `/tmp`, ni al scratchpad, ni al repositorio,
ni a un script. Si necesitas un token —de GitHub, de una tienda, de un servicio— léelo de la
variable de entorno en el momento de usarlo y no lo escribas en ningún sitio:

```sh
curl -H "Authorization: Bearer $GH_TOKEN" ...     # bien
echo "$GH_TOKEN" > /tmp/token.txt                 # nunca
```

Un archivo en `/tmp` lo lee cualquier proceso de la máquina. Tampoco pegues credenciales en los
ejemplos de la documentación: usa marcadores evidentes (`<TU_TOKEN>`) y di que el secreto vive
fuera del código.

---

## 8. Idioma

Todo el texto propio de la biblioteca está en **español con ortografía completa** (tildes,
eñes, ¿ ¡). Los **nombres de funciones, constantes y argumentos se respetan en inglés**: son
la API real y traducirlos rompería el código.

Cuando generes código, los **comentarios van en español** y los identificadores propios del
proyecto también, salvo que el usuario indique otra cosa.
