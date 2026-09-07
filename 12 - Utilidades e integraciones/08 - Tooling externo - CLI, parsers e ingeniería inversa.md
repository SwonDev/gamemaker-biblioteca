# 08 · Tooling externo: CLI, parsers, TypeScript e ingeniería inversa

> Más allá del IDE y de `gm-cli`, existe un **ecosistema de herramientas de línea de comandos**
> (npm, PyPI) que manipulan proyectos de GameMaker desde fuera: parsers de GML, lectores de
> `.yy`/`.yyp`, transpiladores, linters y herramientas para **estudiar juegos compilados**. Son
> la base de cualquier pipeline serio y del desarrollo asistido por IA.
>
> **Búsqueda sistemática** de PyPI, npm y GitHub, verificada en vivo el 2 de septiembre de 2026.
> Comprueba la versión antes de instalar; todo esto evoluciona rápido.

---

## 1 · Stitch (@bscotch) — el kit de pipeline más serio

**Butterscotch Shenanigans** (el estudio de *Crashlands* y *Levelhead*) mantiene **Stitch**, un
conjunto de paquetes npm para automatizar proyectos de GameMaker:

| Paquete | Versión | Qué hace |
|---|---|---|
| `@bscotch/stitch` | 11.1.13 | El SDK de pipeline: importar assets en lote, generar recursos, automatizar builds |
| `@bscotch/yy` | 2.7.0 | **Leer y escribir `.yy`/`.yyp` de forma segura** desde Node — sin corromperlos |
| `@bscotch/gml-parser` | 1.17.2 | Parser de GML: analizar código GML programáticamente (para linters, refactors, herramientas) |
| `@bscotch/stitch-launcher` | — | Gestionar varias instalaciones de IDE/runtime y cambiar entre ellas rápido |

```sh
# instalar (pnpm, el gestor de este equipo)
pnpm add -D @bscotch/stitch @bscotch/yy
```

> 🔺 **`@bscotch/yy` es la pieza clave para tooling.** El formato `.yy` es frágil y editarlo a
> mano lo corrompe (por eso [`gm-cli resourcetool`](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md)
> existe). `@bscotch/yy` hace lo mismo desde Node/JS: lo lee, lo modifica y lo reescribe bien.
> Es la alternativa cuando tu tooling vive en JavaScript en vez de en el CLI oficial.

### `@bscotch/gml-parser` en detalle: analizar y refactorizar GML programáticamente

El catálogo de arriba lo resume en una frase; esto es lo que hace de verdad, sacado de su README
real (`packages/parser/README.md` del monorepo de Stitch, verificado el 07-09-2026 — ★158 el
repo, sin archivar, último *push* 2026-06-15). No es un simple *parser* de texto: cuando carga un
proyecto **modela el `.yyp` entero** —cada asset, cada referencia entre ellos— y mantiene ese
modelo sincronizado mientras lo manipulas con sus propios métodos.

```sh
pnpm add -D @bscotch/gml-parser
```

```ts
import { Project } from '@bscotch/gml-parser';

// Carga el proyecto completo: parsea cada línea de GML y modela cada asset.
// En un proyecto grande tarda; una vez cargado, se mantiene sincronizado solo
// mientras uses los métodos del propio Project (no si tocas archivos por fuera).
const project = await Project.initialize('ruta/al/proyecto.yyp');

// Leer un .gml ya parseado (métodos para consultar/modificar su AST)
const codigo = project.getGmlFile('scripts/scr_dano/scr_dano.gml');

// Buscar un asset por nombre
const activo = project.getAssetByName('obj_enemigo_arquero');

// Renombrar un asset y TODAS sus referencias en código y en otros assets
await project.renameAsset('obj_enemigo_viejo', 'obj_enemigo_arquero');

// Recuperar un recurso huérfano: un .yy que existe en disco pero que el .yyp
// ya no lista (el caso exacto de un merge mal resuelto, ver 13 · 06 §3.13)
await project.addAssetToYyp('objects/obj_enemigo_arquero/obj_enemigo_arquero.yy');
```

**Requisitos, según el propio README**: Node.js 20+, y **desarrollado y probado solo en
Windows** —«*might partially work on other operating systems*»—. El propio paquete se declara
de alcance estrecho de versiones de GameMaker compatibles y avisa de que **puede corromper el
proyecto**: es una herramienta de meta-programación, úsala con control de versiones y revisa el
diff antes de confiar en el resultado. No trae CLI propia: se usa importándolo en un script de
Node — para tooling desde terminal sin escribir JavaScript, la opción es
[`gm-cli resourcetool`](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md),
que sigue siendo la vía oficial de esta biblioteca.

---

## 2 · Lenguajes y calidad de código

- **`@odemian/gamemaker-typescript`** (0.0.11) — **transpila TypeScript a GML**. Escribes con
  tipos y las herramientas de TS, y sale GML. Experimental, pero interesante si vienes de
  TypeScript.
- **`@turlututu-games/gml-linter`** (0.0.6) — **linter de GML**: detecta problemas de estilo y
  errores comunes en el código. Complementa el formateo (ver [*Just a formatter*](./06%20-%20itch.io%20-%20assets,%20herramientas%20y%20jams.md)
  de itch.io).
- **`@ovipakla/gm-cli`** (**2.3.0**, verificado en npm 07-09-2026; no oficial, no confundir con el
  `@gamemaker/gm-cli` de YoYo Games) — *watch & sync* de fuentes GML con el `.yyp`.

### `gamemaker-typescript` (`gmts`) en detalle

Verificado el 07-09-2026 contra su repositorio real
([`OleksandrDemian/gamemaker-typescript`](https://github.com/OleksandrDemian/gamemaker-typescript),
★10, sin archivar, último *push* 2026-04-18): **transpila clases de TypeScript a objetos de
GameMaker**, con soporte de tipos y autocompletado en el editor que uses (VS Code, WebStorm…).
Cada objeto GameMaker se crea igual que siempre en el IDE; el `.ts` vive **junto a su `.yy`**
—`objects/obj_player/code.ts`— para no tocar nunca el `.yyp` (evita el mismo problema de
corrupción que ya explica `13 · 06` §3.13).

```typescript
// objects/obj_player/code.ts
class Player extends GMObject {
  _movement_speed: number;

  onCreate() {
    this._movement_speed = 2;
  }

  onStep() {
    var _hspd = keyboard_check(vk_right) - keyboard_check(vk_left);
    var _vspd = keyboard_check(vk_down) - keyboard_check(vk_up);

    if (_hspd != 0 || _vspd != 0) {
      var _dir = point_direction(0, 0, _hspd, _vspd);
      this.x = this.x + lengthdir_x(this._movement_speed, _dir);
      this.y = this.y + lengthdir_y(this._movement_speed, _dir);
    }
  }
}
```

Uso real, según el README:

```sh
npm install -g @odemian/gamemaker-typescript
gmts setup      # crea tsconfig.json, copia los tipos, configura la compilación
gmts compile    # compila los .ts a .gml manualmente
```

⚠️ **La compilación automática (sin `gmts compile` manual) exige GameMaker `2024.14.4` (abril de
2026) o superior**, versión en la que YoYo Games añadió el *hook* de extensión
`pre_project_step` que este transpilador usa para compilar antes de que el proyecto recoja los
assets. **No está verificado contra LTS 2026.0.0.23** de esta biblioteca —el README no menciona
esa versión ni el runtime `2026.0.0.23` en concreto—: pruébalo en un proyecto de prueba antes de
adoptarlo.

**Limitaciones, literales del propio README**: en fase de *Proof of Concept*; tipos incompletos
y no todos los tipos de objeto soportados; los **enums no están soportados**; las **funciones
constructoras no están soportadas**; y extender una clase **no** asigna el padre en GameMaker
automáticamente — hay que hacerlo a mano en el editor, como con cualquier objeto normal.

### `gml-linter` en detalle

El README publicado en npm es de una línea; el resto se ha verificado el 07-09-2026 inspeccionando
el propio paquete (`npm pack @turlututu-games/gml-linter@0.0.6`, versión más reciente en el
registro a esa fecha, publicada 2026-06-25). Es un binario Node (`bin/gml-linter`) con dos
comandos —**`lint <archivo>`** (el que se ejecuta por defecto) y **`extract <archivo|carpeta>`**,
para extraer la estructura del código— y **17 reglas** activas, deducidas de sus propios ficheros
de tipos: `functionName`, `functionParamName`, `noGlobal`, `noTabAsSpace`, `noTrailingSpace`,
`noMultiEmptyLines`, `missingEnumValue`, `missingEventDescription`, y seis reglas sobre el
formato del JSDoc de una función (`functionComment`, `functionCommentDescription`,
`functionCommentParamsExists`, `functionCommentParamsDescription`,
`functionCommentReturns`/`ReturnsDescription`, `functionCommentTags`,
`functionCommentCommentParamsCoherence`). Se configura con un fichero **`.gml-linter.json`** en
la raíz del proyecto, validado contra un esquema generado con `typescript-json-schema`.

⚠️ **No se ha encontrado un repositorio público** para este paquete (el paquete de npm no declara
`repository`, y la organización `Turlututu-Games` de GitHub no tiene un repo llamado
`gml-linter` entre los suyos, verificado el 07-09-2026): lo anterior sale de inspeccionar el
`.tgz` real descargado del registro de npm, no de un README extenso. Trátalo como una herramienta
de nicho, activa a juzgar por la fecha de publicación, pero sin la superficie de verificación
(issues, estrellas, licencia visible) que sí tienen Gobo o duck.

> ⚠️ **Distingue el `gm-cli` OFICIAL** (`@gamemaker/gm-cli`, de YoYo Games, el que usa este
> equipo) de los homónimos no oficiales (`@ovipakla/gm-cli`). El oficial es el de la regla del
> [CLAUDE.md](../CLAUDE.md).

---

## 3 · Servidores MCP (para agentes de IA)

Recopilados y comparados en detalle en [IA y GameMaker §6 bis](../07%20-%20Ecosistema/14%20-%20IA%20y%20GameMaker.md).
En resumen, el ecosistema MCP (verificado en npm/PyPI):

| MCP | Registro | Qué hace |
|---|---|---|
| `gamemaker-resource-tool` | oficial (gm-cli) | Crear/editar recursos del proyecto |
| `gms-mcp` | PyPI | Assets + símbolos + compilar + ejecutar |
| `gamemaker-mcp` / `@petah/gamemaker-mcp` | npm | Documentación GML |
| **`utmt-mcp`** | npm (0.3.2) | **Leer archivos de datos de GameMaker compilados** (ver §4) |

---

## 4 · Ingeniería inversa: estudiar juegos de GameMaker compilados

El usuario pide «juegos hechos para tenerlos como referencias». Los [21 juegos descargados](../11%20-%20Código%20descargado/juegos_y_motores)
son de **código abierto**. Pero muchos juegos comerciales de GameMaker (Undertale, Deltarune,
Hyper Light Drifter, Katana ZERO…) solo se distribuyen **compilados** en un `data.win`. Para
estudiarlos, se **descompilan**:

- **[UndertaleModTool](https://github.com/UnderminersTeam/UndertaleModTool)** (⭐2024, del
  UnderminersTeam) — «la herramienta más completa para modear, descompilar y desempaquetar»
  juegos de GameMaker. Abre un `data.win` y te muestra sus objetos, scripts (GML descompilado),
  sprites, rooms y sonidos.
- **`utmt-mcp`** (npm) — expone UndertaleModTool a un agente de IA por MCP: un LLM puede leer la
  estructura de un juego compilado y aprender de ella.

> ⚖️ **Legalidad, que es lo primero:** descompilar un juego para **estudiar cómo está hecho** es
> aprendizaje legítimo; **redistribuir** su código, arte o assets, o publicar un juego con ellos,
> **no lo es**. Estudia la técnica, no copies los recursos. La misma regla que rige el
> [corpus de código descargado](../07%20-%20Ecosistema/15%20-%20Qué%20hacen%20de%20verdad%20los%20proyectos%20reales.md):
> licencia libre = úsalo; sin licencia = solo mirar.

> 🔧 **Marco de trabajo:** para el análisis de binarios en este equipo está la skill
> **`reverse-skill`** (instalada en `~/.claude/skills/reverse-skill`), pensada para ingeniería
> inversa en general. Para GameMaker en concreto, **UndertaleModTool es la vía directa** —
> entiende el formato `data.win` nativamente, cosa que las herramientas genéricas de RE no hacen.

### 4 ter · Juegos de la era GameMaker 8.x (formato `.gmk`/`.exe`, anterior a `data.win`)

UndertaleModTool solo entiende el formato `data.win` de GameMaker: Studio 1.x en adelante. Los
juegos hechos con **GameMaker 8.0/8.1** (2009-2011, formato `.gmk` de proyecto y ejecutables
`.exe` autocontenidos) son un binario distinto y necesitan herramientas propias:

| Herramienta | Qué resuelve | ★ | Licencia | Último *push* | Verificado |
|---|---|---:|---|---|---|
| [`OpenGMK/OpenGMK`](https://github.com/OpenGMK/OpenGMK) | Reimplementación *open source* del **runner** de GameMaker 8.x — ejecuta juegos `.exe`/`.gmk` de esa era fuera del runtime original de YoYo, con herramientas adicionales de inspección | 406 | GPL-2.0 | 2026-07-16 | 2026-09-07 |
| [`OpenGMK/GM8Decompiler`](https://github.com/OpenGMK/GM8Decompiler) | **Descompilador** de ejecutables GameMaker 8.x — recupera el proyecto `.gmk` (código, sprites, rooms) a partir del `.exe` compilado, el mismo papel que UndertaleModTool cumple para `data.win` | 200 | GPL-2.0 | 2024-02-12 ⚠️ sin *push* desde hace más de dos años | 2026-09-07 |
| [`skyfloogle/gm8x_fix`](https://github.com/skyfloogle/gm8x_fix) | **Parche** que corrige bugs conocidos del runner original de GameMaker 8.0/8.1 (no descompila ni reimplementa nada, solo arregla el binario original) | 58 | MIT | 2026-04-09 | 2026-09-07 |

**Para qué le sirve a alguien hoy: casi para nada, salvo curiosidad histórica o preservación.**
GameMaker 8.x lleva más de una década descontinuado y ningún proyecto nuevo se hace con ese
formato. Este trío solo interesa si necesitas **estudiar o ejecutar** un juego concreto hecho en
GameMaker 8.0/8.1 (proyectos de archivo, preservación de un juego indie antiguo, investigación
histórica del motor) — no aporta nada al desarrollo con GameMaker LTS 2026.

> ⚖️ Misma regla de legalidad que UndertaleModTool más arriba: **estudiar sí, redistribuir
> assets no.** Descompilar para entender cómo está hecho un juego es aprendizaje legítimo;
> redistribuir su código o arte sin permiso, no lo es.

---

## 4 bis · Anatomía de un binario de GameMaker (análisis real)

Antes de descompilar con herramientas, conviene saber **qué hay dentro** de un juego de
GameMaker compilado. Análisis real hecho el 2 de septiembre de 2026 sobre un `data.win` generado
con `gm-cli compile` (en macOS el archivo se llama `game.ios`; en Windows, `data.win`):

```sh
# el formato: un contenedor IFF/FORM
$ file game.ios          # → IFF data
$ xxd game.ios | head -1
00000000: 464f 524d ...  # "FORM" — la firma de todo binario de GameMaker
```

**El binario es un contenedor `FORM` con chunks nombrados.** Los reales, extraídos con `strings`:

| Chunk | Contiene |
|---|---|
| `GEN8` | Datos generales (nombre, versión, resolución) |
| `STRG` | **Todas las cadenas de texto** del juego |
| `CODE` | El bytecode GML compilado |
| `FUNC` / `VARI` | Tablas de funciones y variables |
| `SPRT` `BGND` `FONT` `TXTR` `TPAG` | Gráficos y páginas de textura |
| `OBJT` `ROOM` `PATH` `TMLN` | Objetos, salas, caminos, timelines |
| `SOND` `AUDO` | Sonidos y audio |
| `SHDR` `EXTN` | Shaders y extensiones |

> 🔺 **Hallazgo clave (verificado): los nombres de recursos y scripts sobreviven en CLARO.** En
> el binario analizado aparecen literalmente `gml_Script_approach`, `gml_Script_lerp_dt`,
> `gml_Script_smoothstep`, `scr_math_util`… con un simple `strings`. Implicaciones:
> - **Para estudiar un juego:** un descompilador (UndertaleModTool) recupera la estructura y los
>   nombres, no solo bytecode anónimo. Se puede leer cómo está organizado.
> - **Para tu propio juego:** «ofuscar» el código no oculta los **nombres**. No pongas secretos
>   (claves de API, endpoints privados) en nombres de recurso ni, sobre todo, en **cadenas de
>   texto** —el chunk `STRG` las guarda—. Los secretos van en el servidor, nunca en el binario
>   (misma regla que en [17 · Interoperabilidad web](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md)).

**El flujo de análisis, resumido:** `file` (confirmar FORM) → `strings` (nombres y cadenas) →
UndertaleModTool (descompilar el `CODE` a GML legible y explorar rooms/sprites). Las dos primeras
las hace cualquier herramienta Unix; la tercera entiende el formato GameMaker de verdad.

---

## Qué usar según lo que quieras hacer

| Quiero… | Herramienta |
|---|---|
| Automatizar imports de assets / builds | `@bscotch/stitch` |
| Manipular `.yy`/`.yyp` desde código | `@bscotch/yy` o `gm-cli resourcetool` |
| Analizar/refactorizar GML programáticamente | `@bscotch/gml-parser` |
| Escribir con tipos (TS→GML) | `@odemian/gamemaker-typescript` |
| Detectar problemas de estilo | `@turlututu-games/gml-linter` |
| Que un agente de IA toque el proyecto | `gms-mcp` / `gamemaker-resource-tool` |
| Estudiar un juego compilado | UndertaleModTool + `utmt-mcp` |
| Compilar/ejecutar desde terminal | **`gm-cli`** (oficial) |

---

## Ver también

- [07 · GM CLI — la línea de comandos](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20línea%20de%20comandos.md) — el CLI oficial
- [14 · IA y GameMaker](../07%20-%20Ecosistema/14%20-%20IA%20y%20GameMaker.md) — los MCP en detalle
- [15 · Qué hacen de verdad los proyectos reales](../07%20-%20Ecosistema/15%20-%20Qué%20hacen%20de%20verdad%20los%20proyectos%20reales.md) — el análisis del corpus y la situación legal
