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

---

## 2 · Lenguajes y calidad de código

- **`@odemian/gamemaker-typescript`** (0.0.11) — **transpila TypeScript a GML**. Escribes con
  tipos y las herramientas de TS, y sale GML. Experimental, pero interesante si vienes de
  TypeScript.
- **`@turlututu-games/gml-linter`** (0.0.6) — **linter de GML**: detecta problemas de estilo y
  errores comunes en el código. Complementa el formateo (ver [*Just a formatter*](./06%20-%20itch.io%20-%20assets,%20herramientas%20y%20jams.md)
  de itch.io).
- **`@ovipakla/gm-cli`** (2.1.3, no oficial) — *watch & sync* de fuentes GML con el `.yyp`.

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
