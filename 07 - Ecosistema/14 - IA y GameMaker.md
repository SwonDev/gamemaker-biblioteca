# 14 · IA y GameMaker (estado real en agosto de 2026)

> ✅ **Reverificado el 2 de septiembre de 2026** con `gm-cli` **2.3.0** (la última publicada):
>
> | Afirmación de este documento | Estado |
> |---|---|
> | El flag `--ai` de `gm-cli init` genera el andamiaje (MCP, `CLAUDE.md`…) | ✅ Sigue existiendo y **está activado por defecto** |
> | `GMEXT-MLKit` es la única IA que publica YoYo Games | ✅ Repo vivo, sin archivar, último cambio 25-08-2026 |
> | No hay funciones de IA generativa en el motor | ✅ Sin cambios |

> **Advertencia metodológica**: este documento distingue en todo momento entre
> **(A) lo que el motor trae integrado**, **(B) lo que se puede hacer con extensiones oficiales**,
> **(C) lo que requiere herramientas externas** y **(D) lo que se ha anunciado pero no es
> verificable en el software instalado**. Cada afirmación lleva su evidencia.

---

## Conclusión honesta, en corto

1. **GameMaker NO tiene integración de IA en el motor.** No existe ninguna función GML de
   inteligencia artificial, machine learning ni LLM. Verificado: el manual oficial no devuelve
   resultados para «AI», «machine learning», «artificial intelligence» ni «neural network».
2. **Lo que sí hay son dos cosas distintas y reales**:
   - **Motion Planning** (`mp_grid` y compañía): IA *clásica de videojuegos* — pathfinding,
     evitación de obstáculos. No es machine learning.
   - **`GMEXT-MLKit`**: extensión **oficial de YoYo Games** que expone ML real (Google ML Kit):
     traducción de texto e identificación de idioma, en dispositivo, sólo Android e iOS.
3. **GameMaker no ejecuta ningún servidor de IA propio.** No hay agentes, ni modelos, ni
   asistentes dentro del IDE.
4. **Lo que sí hay es andamiaje para que TÚ uses tu agente de IA** (Claude Code, Codex,
   OpenCode…) contra tu proyecto: `gm-cli init --ai` genera `CLAUDE.md`, `AGENTS.md`, `.mcp.json`
   y un servidor MCP por proyecto. La IA la pones tú; GameMaker sólo abre la puerta.
5. **Sobre «Claude Code integrado en GM-CLI»**: lo anuncia la nota de prensa oficial de Opera,
   pero **no existe tal subcomando en el paquete npm** (verificado en la 2.2.0 instalada y en la
   2.3.0 descargada). Lo que sí está ahí, y es verificable, es el andamiaje de agente. Detalle
   completo en la sección 4.

---

## 1. ¿Existen funciones de IA en el motor? NO

### Evidencia 1: el manual oficial, consultado en la terminal

```bash
gm-cli manual read "AI"
gm-cli manual read "machine learning neural network"
gm-cli manual read "artificial intelligence"
gm-cli manual read "neural network"
```

Las cuatro devuelven exactamente:

```
Command failed:
No results found
```

`gm-cli manual read` hace una búsqueda semántica sobre el manual completo de GameMaker. Que
cuatro consultas distintas sobre IA/ML devuelvan cero resultados es una evidencia sólida de que
**no hay ninguna página del manual dedicada a IA**.

### Evidencia 2: lo que SÍ devuelve — Motion Planning (IA clásica)

```bash
gm-cli manual read "mp_grid pathfinding"
```

```
Motion Planning

In many games you want opponents, NPC's, enemies, etc., to interact with the
player and show certain intelligence when moving around, i.e. you want them to
avoid obstacles, plan routes and generally not bump into everything in their
path! To aid in this GameMaker has a series of functions that deal with motion
planning. ...
```

Es decir: GameMaker trae **algoritmos de IA de toda la vida** (mallas de navegación, rutas,
evasión), que en el manual se agrupan bajo «Motion Planning». Esto **no** es machine learning ni
IA generativa: son funciones deterministas de pathfinding (`mp_grid_create`, `mp_grid_path`,
`mp_potential_step`, etc.).

### Lo que NO encontrarás en ninguna parte del motor

| Qué | ¿Existe en GameMaker 2026.0? |
|---|---|
| Funciones GML de machine learning | ❌ No |
| Inferencia de redes neuronales en GML | ❌ No |
| Cliente de LLM integrado (tipo `ai_chat()`) | ❌ No |
| Generación procedural de assets con IA en el IDE | ❌ No |
| Asistente de código dentro del IDE | ❌ No (Feather es análisis estático, no IA) |
| Traducción / idioma en dispositivo (ML real) | ✅ Sí, vía `GMEXT-MLKit`, sólo Android/iOS |
| Pathfinding / IA de enemigos | ✅ Sí, `mp_grid` y compañía |
| MCP para agentes externos | ✅ Sí, `gm-cli resourcetool mcp` |

> **Feather no es IA.** Es el analizador estático de código de GameMaker (errores de sintaxis,
> tipos, convenciones de nombres). Se basa en reglas, no en modelos. En 2026.0 está activado por
> defecto y es lo más parecido a un «asistente» que hay dentro del IDE.

---

## 2. `GMEXT-MLKit`: la única IA «de verdad» que publica YoYo Games

| Dato | Valor verificado (GitHub API) |
|---|---|
| Repositorio | <https://github.com/YoYoGames/GMEXT-MLKit> |
| Descripción | *Repository for GameMaker's Machine Learning Extension* |
| Creado / último push | 2024-04-01 / **2026-08-25** (activo) |
| Última versión | **2.0.2**, publicada el 2026-08-25 |
| Versiones publicadas | `0.0.1` (2024-05-10), `1.0.0` (2025-07-30), `2.0.0` (2026-06-23), `2.0.2` (2026-08-25) |
| Estado | Público, no archivado |

### Qué hace

Envuelve **Google ML Kit**, con APIs **en el dispositivo** para:

- **Traducción de texto** (`GMMLKit`)
- **Identificación de idioma** (`GMMLKitLanguageIdentification`)

### Limitaciones importantes (del README oficial)

- **Sólo funciona en Android e iOS.** En el resto de plataformas las funciones son *no-ops*
  (no hacen nada). No sirve para Windows, macOS, Linux, HTML5 ni consolas.
- **Los modelos de idioma se descargan bajo demanda en tiempo de ejecución**, así que hace falta
  conexión a red la primera vez que se usa un modelo de traducción.
- Para compilar en **iOS** hace falta **CocoaPods**; si no está, GameMaker lo instala
  automáticamente al construir desde el IDE o desde línea de comandos. Si prefieres el tuyo,
  debe estar instalado en modo `sudoless` y disponible en el PATH.

### Valoración

Es ML **real y oficial**, pero **muy acotado**: dos capacidades (traducir y detectar idioma),
dos plataformas móviles, sin entrenamiento, sin modelos propios, sin visión ni voz. Sirve para
localizar un juego sobre la marcha; no sirve para construir un NPC conversacional.

---

## 3. El andamiaje de IA que genera `gm-cli init --ai`

Esto **sí está verificado en la 2.2.0 instalada**: se creó un proyecto de prueba con
`gm-cli init -n PruebaCLI -t "Blank Pixel Game" --no-interactive` y esto es lo que apareció.

### 3.1 `.mcp.json` (en la raíz del proyecto)

```json
{
  "mcpServers": {
    "gamemaker-resource-tool": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "@gamemaker/gm-cli@latest",
        "resourcetool",
        "mcp"
      ],
      "env": {}
    }
  }
}
```

- Servidor MCP **por proyecto**, arrancado con `npx` sobre `@gamemaker/gm-cli@latest`.
- **No hay ninguna variable de entorno de API key**: la IA no la pone GameMaker, la pones tú.
- Sin `.yyp` en el directorio, el servidor se cierra al arrancar.

### 3.2 `CLAUDE.md` y `AGENTS.md`

Ambos ficheros se generan con **contenido idéntico** (`diff CLAUDE.md AGENTS.md` → vacío). Uno
apunta a Claude Code; el otro es la convención agnóstica que entienden Codex, OpenCode y
similares. Contenido literal:

```markdown
# Editing GameMaker project files

Do not make changes to `.yy` or `.yyp` files yourself.
It's very hard to correctly edit these manually!
You MUST use commands exposed by the `gamemaker-resource-tool` MCP server.

# GameMaker Language (GML) Guidance

Make changes to `.gml` files using your built-in tools, if you so wish.

## GML Naming conventions

- Use `snake_case` for all variables and functions
- Prefix local variables with `_` (e.g., `var _temp_value`, `var _effect`)
- Prefix resource names based on their type, e.g. obj_player, spr_player, etc.

## GML reserved names

Your own names must avoid clashing with these:

- `score`, `lives`, `health`
- Position: `x`, `y`
- Sprite: `sprite_index`, `image_index`, `image_speed`, `image_xscale`, `image_yscale`, `image_angle`, `image_alpha`, `image_blend`
- Physics: `speed`, `direction`, `friction`, `gravity`, `gravity_direction`
- Collision: `bbox_left`, `bbox_right`, `bbox_top`, `bbox_bottom`
- Instance: `id`, `object_index`, `layer`, `depth`, `visible`, `persistent`

## Modern idiomatic GML

GML has support for **structs** (dynamic objects similar to JavaScript).

    var _mystruct =
    {
        a : 20,
        b : "Hello World"
    };

    function Vector2(_x, _y) constructor
    {
        x = _x;
        y = _y;

        static Add = function(_vec2)
        {
            x += _vec2.x;
            y += _vec2.y;
        }
    }

    v2 = new Vector2(10, 10);

GML *script* files now requires one or more function definitions

    // in move script
    function move(spd, dir)
    {
        speed = spd;
        direction = dir;
    }

## Library Functions

- Prefer `instance_create_layer()` over deprecated `instance_create()`

# Running / debugging games

To help users debug and play games you can make use of:

    npx @gamemaker/gm-cli compile --errors-only
    npx @gamemaker/gm-cli run --errors-only
```

> ⚠️ Esto es lo que genera GameMaker por sí solo — no lo que recomienda esta biblioteca sin
> matices. `--errors-only` sirve para iterar, pero silencia los `WARNING` de compilación
> (incluido el de un *included file* que `resourcetool` no llegó a copiar al paquete) y algún
> *crash* real del `AssetCompiler`. Antes de dar un juego por terminado, compila al menos una
> vez sin ese flag — detalle en
> [`12 · 09` §0 Trampa 8](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-8--resource-create-typeincludedfile-deja-filepath-fuera-de-datafiles-y---errors-only-no-lo-detecta).

### 3.3 `.claude/settings.local.json` — la barrera de seguridad

```json
{
  "permissions": {
    "allow": [
      "mcp__gamemaker-resource-tool"
    ],
    "deny": [
      "Edit(*.yy)",
      "Edit(*.yyp)"
    ]
  },
  "enabledMcpjsonServers": [
    "gamemaker-resource-tool"
  ],
  "enableAllProjectMcpServers": true
}
```

Esto es lo más interesante del andamiaje: **GameMaker le prohíbe explícitamente al agente editar
`.yy` y `.yyp`** y le obliga a pasar por el MCP. Es una decisión de diseño deliberada de
YoYo Games, no una sugerencia.

### 3.4 Por qué NO hay que editar `.yy` / `.yyp` a mano

- Son **ficheros generados** por el serializador del proyecto. Su estructura interna cambia entre
  versiones de GameMaker (en 2026.0 se introdujo un **nuevo serializador de proyectos**).
- Contienen referencias cruzadas (GUIDs, rutas de recursos, orden de campos) que deben mantenerse
  coherentes. Un error manual deja el proyecto **corrupto o ilegible para el IDE**.
- Las capas de tiles y el orden de assets se guardan con formatos comprimidos propios.
- El ResourceTool (`gm-cli resourcetool`) aplica las migraciones y validaciones correctas.

**Lo que sí puedes editar a mano**: los ficheros `.gml` (lógica). El propio `CLAUDE.md` lo dice:
*«Make changes to `.gml` files using your built-in tools, if you so wish.»*

---

## 4. El caso «Claude Code en GM-CLI»: qué se anunció y qué hay realmente

Esta es la parte que más cuidado requiere. Hay dos afirmaciones públicas y una realidad
comprobable que no coincide del todo.

### 4.1 Lo que se anunció

**Nota de prensa oficial de Opera** (30 de abril de 2026), propietaria de GameMaker:

> «Alongside GMRT, GameMaker is launching GM-CLI […] as well as **Claude Code, Anthropic's AI
> developer agent**, making GameMaker one of the first game engines with AI-assisted workflows
> built in.»
>
> Sección «AI in the toolchain»: «With Claude Code in the CLI, developers can now query project
> structures, hunt down bugs, and manage build configurations through natural language prompts in
> the terminal.»

También se hizo eco la prensa del sector (Outlook Respawn, 1 de mayo de 2026).

### 4.2 Lo que dice el blog oficial de GameMaker

El post oficial «GameMaker Update Spring 2026: LTS Roadmap, GMRT, and the Future» (Russell Kay,
30 de abril de 2026) describe GM-CLI, GMRT, los lenguajes nuevos y las extensiones.

**No menciona IA ni Claude Code en ningún apartado.** Cero menciones en todo el artículo.

### 4.3 Lo que hay realmente en el software (verificado)

Se descargó el tarball npm de la **2.3.0** y se comparó con la **2.2.0** instalada:

| Comprobación | Resultado |
|---|---|
| ¿Existe un subcomando `claude` en `gm-cli --help`? | **No.** Los subcomandos son `init`, `run`, `compile`, `package`, `manual`, `resourcetool`, `login`, `gxgames`, `cache` |
| ¿Aparece la palabra «claude» en el código 2.3.0? | Sí, **4 veces**, todas en el andamiaje: `Set up AI scaffolding (MCP, CLAUDE.md, etc.)` y la escritura de `CLAUDE.md` |
| ¿Hay credenciales o cliente de Anthropic en el paquete? | **No** aparece ninguna referencia a Anthropic ni a API keys de modelo |
| ¿El README de la 2.3.0 cambia respecto a la 2.2.0? | **No** — `diff` vacío |
| ¿Hay releases en el repo de GitHub? | **0 releases publicados**, así que no hay changelog oficial |

Fragmento literal del bundle de la 2.3.0 donde aparece «claude»:

```js
useAi:()=>d({message:"Set up AI scaffolding (MCP, CLAUDE.md, etc.)",initialValue:e.ai??!0})
// ...
if(t.useAi){ await this.fs.writeFile(this.path.join(a,"CLAUDE.md"),w),
             await this.fs.writeFile(this.path.join(a,"AGENTS.md"),w); ... }
```

### 4.4 Conclusión rigurosa

| Afirmación | Veredicto |
|---|---|
| «GameMaker tiene IA integrada en el motor» | ❌ **Falso** |
| «GameMaker ejecuta servidores de IA» | ❌ **Falso** (Russell Kay lo niega explícitamente en la cobertura del anuncio) |
| «GM-CLI incluye un subcomando/agente Claude Code» | ⚠️ **No verificable en el paquete npm 2.2.0 ni 2.3.0.** La nota de prensa lo afirma; el software no lo trae |
| «GM-CLI prepara el proyecto para usar agentes de IA» | ✅ **Verdadero y verificado**: `init --ai` + MCP + `CLAUDE.md`/`AGENTS.md` |
| «Puedo usar Claude Code / Codex / OpenCode con GameMaker hoy» | ✅ **Verdadero**, montando tú el agente contra el MCP del proyecto |

**Lectura práctica**: la integración con Claude Code que se anunció es, en el software que hoy se
puede instalar, **habilitación de herramientas, no un producto empaquetado**. GameMaker no te da
una IA; te da el MCP, las reglas y los permisos para que la tuya trabaje con seguridad sobre el
proyecto. Puede que una futura versión del CLI añada el subcomando anunciado.

---

## 5. Cómo usar un agente de IA con GameMaker (lo que sí funciona hoy)

> 📖 Esta sección da lo mínimo para arrancar. El manual completo, con las cuatro trampas que
> hacen fracasar a un agente hoy (plantillas que fallan, `resourcetool`/`compile` colgados bajo
> sandbox, el evento equivocado sin avisar, funciones inventadas que el compilador no detecta),
> el ciclo completo del agente y el mapa exacto de qué `.gml` va en cada archivo, está en
> [`12 · 09` — Manual del agente de IA: operar GameMaker con `gm-cli`](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md).

### 5.1 Requisitos

```bash
# Node 24 o superior (el paquete lo declara en "engines")
node --version

# gm-cli global
npm install -g @gamemaker/gm-cli@latest    # usa npm: es el gestor con el que ya está instalado
```

### 5.2 Preparar el proyecto

```bash
# Proyecto nuevo (el andamiaje viene activado por defecto)
gm-cli init -n MiJuego -t "Platformer Template"

# Proyecto existente: crea el .mcp.json a mano en la raíz del .yyp
```

Contenido del `.mcp.json` (idéntico al que genera `init`):

```json
{
  "mcpServers": {
    "gamemaker-resource-tool": {
      "type": "stdio",
      "command": "npx",
      "args": ["@gamemaker/gm-cli@latest", "resourcetool", "mcp"],
      "env": {}
    }
  }
}
```

### 5.3 Flujo de trabajo recomendado

```
1. El agente inspecciona el proyecto vía MCP
   gm-cli resourcetool eval "resource list"
   gm-cli resourcetool eval "room item list room=Room1"

2. Crea recursos SIEMPRE por ResourceTool
   gm-cli resourcetool eval "resource create type=object name=obj_enemigo"
   gm-cli resourcetool eval "object event findorcreate name=obj_enemigo type=create"

3. Escribe la lógica editando los .gml (con su editor de ficheros normal)

4. Verifica compilando — nunca des por buena una respuesta sin compilar
   gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only
```

> ⚠️ `--errors-only` vale para este bucle de iteración rápida, pero no para la última
> verificación de una tarea: silencia los `WARNING` (por ejemplo, un *included file* que no
> llegó al paquete compilado). Antes de cerrar la tarea, compila una vez sin el flag — ver
> [`12 · 09` §0 Trampa 8](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-8--resource-create-typeincludedfile-deja-filepath-fuera-de-datafiles-y---errors-only-no-lo-detecta).

### 5.4 Reglas que debes imponer al agente

- **Nunca** editar `.yy` ni `.yyp`. En Claude Code esto ya viene forzado por
  `.claude/settings.local.json` con `deny: ["Edit(*.yy)", "Edit(*.yyp)"]`.
- Los `.gml` sí se editan directamente.
- Antes de inventar una función de GML: `gm-cli manual read "<función>"`.
- Convenciones: `snake_case`, locales con prefijo `_`, recursos con prefijo de tipo
  (`obj_`, `spr_`, `snd_`, `rm_`, `scr_`).
- Evitar nombres reservados: `x`, `y`, `speed`, `direction`, `id`, `depth`, `score`, `health`,
  `lives`, `bbox_*`, `image_*`, `sprite_index`, `object_index`, `layer`, `visible`, `persistent`.
- Preferir `instance_create_layer()` sobre `instance_create()` (obsoleta).
- **Compilar antes de declarar terminada cualquier tarea.**

### 5.5 El MCP es por proyecto

Abre el agente **dentro de la carpeta del `.yyp`**. Si abres el agente en la carpeta padre, el
servidor MCP arranca y se cierra: `resourcetool mcp` no encuentra proyecto y termina.

---

## 6. Extensiones de IA de terceros

### 6.1 Marketplace oficial — categoría IA

<https://marketplace.gamemaker.io/category/18/ai>

Lo que hay ahí es **IA clásica de videojuegos**, no machine learning generativo. Ejemplos reales
del listado:

| Asset | Tipo |
|---|---|
| Swarm | Comportamiento de enjambre |
| Advanced Targeting System | Selección de objetivos |
| Fish AI - Schooling | Bancos de peces |
| **Multi-Layer Neural Network** | Red neuronal multicapa (implementada en GML) |
| IceyAI | Framework de IA (gratuito) |
| NPC A.I | IA de personajes no jugables |
| Gesture Recognition Engine | Reconocimiento de gestos |
| Pathfinding Engine for GMS 2.3 | Pathfinding avanzado |
| Blockade AI, Optimized Path, Grid path, Manhattan Distance | Utilidades de rutas |

> Ojo con «Multi-Layer Neural Network»: es una implementación en GML puro de una red neuronal
> pequeña. Útil para experimentos o para NPCs adaptativos simples; no es un runtime de ML moderno
> ni ejecuta modelos preentrenados.

### 6.2 Integración con APIs de LLM (por HTTP)

Existen assets del marketplace que conectan GameMaker con APIs de terceros mediante peticiones
HTTP asíncronas. El más conocido:

- **API integration - Chat GPT & DALL-E** —
  <https://marketplace.gamemaker.io/assets/11758/api-integration-chat-gpt-dall-e>
  (publicado el 2024-02-16). Colección de scripts para hablar con la API de OpenAI por HTTP
  Async: genera textos e imágenes en cualquier idioma.

**Consideraciones antes de usar este camino**:

- La **clave de API viaja en el juego**. En un build de escritorio o móvil cualquiera puede
  extraerla y usarla a tu costa. La práctica correcta es **interponer tu propio backend** que
  guarde la clave y haga de proxy.
- Cada llamada es una petición de red: latencia, fallos, y coste por token.
- Revisa los términos del proveedor y la normativa de la plataforma donde publiques
  (clasificación por edad, contenido generado por IA).
- Para GameMaker, la mecánica es simplemente `http_request()` + parseo de JSON: no hay nada
  específico del motor para LLMs.

### 6.3 Herramientas de la comunidad

- **GML-Assistant** (<https://github.com/RMDomingos20/GML-Assistant>): aplicación de escritorio
  de código abierto pensada para proyectos `.yyp` medianos y grandes. Actúa como compañero de
  espacio de trabajo, no como un chatbot genérico desconectado de tu código.
  *Es un proyecto de terceros, no de YoYo Games.*

---

## 6 bis. El ecosistema de servidores MCP para GameMaker (oficial + terceros)

El **Model Context Protocol (MCP)** es cómo un agente de IA (Claude, Codex, Cursor) manipula
un proyecto de GameMaker sin tocar el IDE. Hay uno oficial y varios de terceros, y conviene
saber cuál usar. *(Investigado en vivo el 2 de septiembre de 2026; verifica versiones antes de
instalar.)*

| Servidor MCP | Lenguaje | Qué hace | Cuándo usarlo |
|---|---|---|---|
| **`gamemaker-resource-tool`** (oficial) | — | Lo que lanza `gm-cli resourcetool mcp`: crear y editar recursos (objetos, sprites, rooms, eventos) del proyecto. Es el que traen los proyectos de `gm-cli init` | **Por defecto.** Es oficial, va con tu runtime y no añade dependencias |
| **`gms-mcp`** (PyPI, terceros) | Python 3.10+ | Crear/renombrar assets, **indexar símbolos GML** (definición y referencias), texture groups, **seleccionar runtime, compilar y ejecutar**, health checks. Trabaja dentro de un «project boundary» de seguridad | Cuando quieras indexado de símbolos y control de compilación desde el agente, más allá de los recursos |
| **`gamemaker-mcp`** (Petah, GitHub) | Node.js ≥22 | Solo **documentación**: buscar funciones GML, búsqueda de texto, navegar la referencia. No toca el proyecto | Si tu agente solo necesita consultar la API (aunque esta biblioteca ya cubre eso offline con `buscar.py`) |

> 🔺 **`gms-mcp` está en desarrollo activo** (v0.0.7 publicada el **2 de septiembre de 2026**,
> con CI contra GameMaker 2024 y 2026 LTS reales). Es de terceros: instálalo con
> `pip install gms-mcp` **revisando antes** que la versión soporta tu runtime.
> Fuentes: <https://pypi.org/project/gms-mcp/> · <https://github.com/Petah/gamemaker-mcp>
>
> 💡 **¿MCP de docs de terceros vs esta biblioteca?** `gamemaker-mcp` hace lo mismo que hace el
> `buscar.py` de este proyecto —dar la API de GML a un LLM— pero como servidor MCP en vez de
> como archivos indexados. Esta biblioteca funciona sin conexión, sin instalar nada y sin un
> proceso aparte, y además trae recetas, cursos y código real. El MCP es un complemento, no un
> sustituto.

### Editar desde VS Code en vivo: GMSync

**[GMSync](https://marketplace.visualstudio.com/items?itemName=atennebris.gmsync)** (Atenebris,
extensión de VS Code, también en itch.io) permite **editar un proyecto de GameMaker desde VS
Code sin reiniciar el IDE**: crear recursos, modificar eventos, gestionar rooms y capas, y
controlar el juego en marcha por un puente TCP. Útil si prefieres el editor de VS Code (con su
copiloto de IA) al del IDE, manteniendo el proyecto sincronizado.

> ⚠️ **Es de terceros y toca el proyecto en vivo.** Haz copia de seguridad (o usa git) antes de
> dejar que una herramienta externa sincronice cambios en tu `.yyp`.

### 6 bis.2 · Más tooling de IA de terceros — descargado en este repo (2026)

Auditoría del 2 de septiembre de 2026: se han **descargado** a `11 - Código descargado/librerias/`
estos proyectos recientes (2025-2026), para poder estudiarlos sin conexión. **Todo esto es de
terceros**: revisa su licencia y su compatibilidad con tu runtime antes de usarlo.

| Proyecto | Ruta local | Qué hace | Licencia |
|---|---|---|---|
| **`gamemaker-mcp`** (yearningss) ⚠️ *homónimo del de Petah, pero distinto* | `librerias/ia-y-mcp/gamemaker-mcp` | Servidor MCP **project-aware con ~190 tools**: análisis estático de GML, refactor y builds automáticos. Va mucho más allá que el de docs de Petah | MIT |
| **`GameMaker-MCP-Server`** (darkw3bb) | `librerias/ia-y-mcp/GameMaker-MCP-Server` | Servidor MCP pensado para **Cursor**: construir proyectos GameMaker asistidos por IA | NOASSERTION (revisa LICENSE) |
| **`gm-forge-mcp`** (nicklesimba) | `librerias/ia-y-mcp/gm-forge-mcp` | Servidor MCP para **crear y editar** proyectos GameMaker | MIT |
| **`gamemaker-skills`** (leihaht) | `librerias/ia-y-mcp/gamemaker-skills` | **Skills de Claude Code** para GMS2/GML (objetos, shaders, red, optimización). Ejemplo de cómo empaquetar conocimiento GML para un agente | MIT |
| **`gamemaker-typescript`** (OleksandrDemian) | `librerias/herramientas-externas/gamemaker-typescript` | Extensión que **transpila TypeScript → GML**: escribir con tipos y tooling de TS | MIT |
| **`GML-formatter`** (GanjaViruss) | `librerias/herramientas-externas/GML-formatter` | Formateador de GML offline (estilos Allman/K&R), cero dependencias | MIT |
| **`gml_lsp`** (Okerew) ⚠️ *archivado* | `librerias/herramientas-externas/gml_lsp` | Servidor **LSP** para GML (autocompletado/diagnóstico en editores). Repo archivado: referencia, no producción | MIT |

> 🔎 **Distinción clave de nombres:** hay **dos** proyectos llamados `gamemaker-mcp`. El de
> **Petah** (arriba, en la tabla de la sección 6 bis) solo sirve **documentación** de la API. El de
> **yearningss** (esta tabla) es **project-aware** y edita/compila. No los confundas.
>
> 💡 Estos MCP de terceros **editan y compilan** el proyecto, a diferencia del `buscar.py` offline
> de esta biblioteca (que solo da la API). El MCP oficial `gamemaker-resource-tool` sigue siendo el
> punto de partida recomendado; estos son alternativas más potentes pero de terceros.

---

## 7. Roadmap oficial: ¿hay IA prevista?

El roadmap público está en <https://github.com/orgs/YoYoGames/projects/17/views/48>
(en el pie de gamemaker.io aparece como *Roadmap*).

### Lo que el blog oficial Spring 2026 sí anuncia

| Área | Contenido |
|---|---|
| **LTS26** | Cinco versiones: 2026.0 (Q2 2026), 2026.1 (Q4 2026), 2026.2 (Q1 2027), 2026.3 (Q4 2027), 2026.4 (Q1 2028). El runtime GMS2 queda **feature complete**: todas las funciones nuevas van a GMRT |
| **GMRT v0.20** | 99 % de compatibilidad, target Android, target Switch, funciones 3D |
| **Código abierto** | El código fuente de GMRT será accesible para **todos** en escritorio, móvil y web; los suscriptores Enterprise también tendrán las versiones de consola |
| **3D** | Carga de modelos glTF (desde Blender), scene graph, matemáticas 3D (matrices, cuaterniones), animación desde glTF |
| **Lenguajes** | JavaScript (ES2020) en Q2 2026 · TypeScript en Q3 2026 · C# en preview en Q4 2026 |
| **Plugins del IDE** | Code Editor 2, Start Page, ProjectTool, Prefab Builder |
| **Extensiones previstas** | ISteamParties, Switch 2 para FMOD, Discord Social SDK, Reddit Devvit SDK, Apple y Google IAP, Opera Ads, Photon, Razer Wyvrn |
| **Multijugador** | Namazu Elements, Colyseus, Steamworks, Photon (próximamente) |
| **Room Editor** | Replanteamiento completo en los próximos meses |

### ¿IA en el roadmap?

**En el blog oficial del roadmap no aparece la palabra IA en ningún apartado.** La única mención
de IA en comunicación oficial de GameMaker/Opera es la nota de prensa del lanzamiento de GMRT
(30 de abril de 2026) descrita en la sección 4.

Traducción honesta: **no hay una hoja de ruta pública de funciones de IA en el motor**. Lo que
hay es una apuesta porque el ecosistema (CLI + MCP + APIs) sea utilizable por agentes externos.

---

## 8. Resumen operativo

| Quiero… | Camino real |
|---|---|
| Que mi agente de IA cree objetos, rooms y eventos | MCP `gamemaker-resource-tool` por proyecto (`gm-cli resourcetool mcp`) |
| Que mi agente escriba lógica | Editar los `.gml` directamente |
| Que mi agente no rompa el proyecto | `AGENTS.md`/`CLAUDE.md` + `deny Edit(*.yy)/Edit(*.yyp)` |
| Pathfinding para enemigos | Funciones `mp_grid` del motor (Motion Planning) |
| Traducción o detección de idioma en móvil | `GMEXT-MLKit` (oficial, Android/iOS) |
| Un NPC que hable como un LLM | API externa por HTTP **a través de tu propio backend**; no hay nada nativo |
| IA dentro del IDE | No existe. Fuera del IDE, con agentes externos |

---

## 9. Fuentes

**Fuentes primarias consultadas**
- Manual oficial de GameMaker: <https://manual.gamemaker.io/> (consultado vía `gm-cli manual read`)
- Paquete npm `@gamemaker/gm-cli` (2.2.0 instalada y 2.3.0 descargada e inspeccionada):
  <https://www.npmjs.com/package/@gamemaker/gm-cli>
- Repositorio de gm-cli: <https://github.com/YoYoGames/gm-cli>
- `GMEXT-MLKit` (extensión oficial de ML): <https://github.com/YoYoGames/GMEXT-MLKit>
- Blog oficial «GameMaker Update Spring 2026: LTS Roadmap, GMRT, and the Future»:
  <https://gamemaker.io/en/blog/update-spring-2026>
- Blog oficial «GameMaker LTS 2026.0: New Features, GMRT and Much More»:
  <https://gamemaker.io/en/blog/lts-2026-release>
- Notas de versión LTS 2026.0: <https://releases.gamemaker.io/release-notes/2026/0>
- Roadmap público: <https://github.com/orgs/YoYoGames/projects/17/views/48>
- Marketplace, categoría IA: <https://marketplace.gamemaker.io/category/18/ai>
- Marketplace, «API integration - Chat GPT & DALL-E»:
  <https://marketplace.gamemaker.io/assets/11758/api-integration-chat-gpt-dall-e>

**Sobre el anuncio de Claude Code**
- Nota de prensa oficial de Opera (30-04-2026): <https://press.opera.com/2026/04/30/gamemaker-gmrt>
- Cobertura de prensa (Outlook Respawn, 01-05-2026):
  <https://respawn.outlookindia.com/gaming/gaming-news/gamemaker-launches-gmrt-brings-anthropics-claude-ai-to-game-dev>
- Cobertura de gamedev.net: <https://gamedev.net/news/3046-gamemaker-update-spring-2026-lts-roadmap-gmrt-and-the-future>

**Comunidad**
- Foro oficial: <https://forum.gamemaker.io/>
- Seguimiento de bugs y peticiones: <https://github.com/YoYoGames/GameMaker-Bugs/issues>
- Hilo sobre integrar la API de ChatGPT: <https://forum.gamemaker.io/index.php?threads/chatgpt-api.102747/>
- GML-Assistant (terceros): <https://github.com/RMDomingos20/GML-Assistant>
