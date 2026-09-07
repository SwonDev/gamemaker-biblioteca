# 06 · Plantillas y starters

> Verificado el **31 de agosto de 2026** consultando la API oficial (`https://api.gamemaker.io/api/gamemaker/project-templates`) y **creando proyectos de prueba reales** con `gm-cli`.
> `gm-cli` instalado en este Mac: **2.3.0**, al día con la última publicada (verificado 07-09-2026).

---

## 1. Las plantillas oficiales

YoYoGames publica **31 plantillas** a través de su API. Se usan tanto desde el IDE (*New Project*) como desde `gm-cli init`. Distribución verificada:

| Tipo | Cantidad |
|---|---:|
| **Game** (juego completo) | 18 |
| **Live Wallpaper** (fondo animado de Opera) | 12 |
| **GameStrip** (minijuego integrable en el navegador Opera) | 1 |

### 1.1 Plantillas de juego (las 18)

| Plantilla | Género | Cuándo elegirla |
|---|---|---|
| **Space Rocks** | Arcade espacial | ⭐ **La mejor para empezar.** El «Hola mundo» jugable: disparo, asteroides, puntuación, vidas. Se lee entera en una tarde. |
| **Platformer Template** | Plataformas | El género por defecto si quieres un *platformer* serio. ⚠️ Ver la incidencia documentada en la sección 4. |
| **Arcade Action Game Template** | Acción arcade | Similar a Space Rocks pero con más sistemas. |
| **Scrolling Shooter Game Template** | *Shoot 'em up* vertical | Si tu juego es un *shmup*. |
| **Twin Stick Shooter Template** | *Twin-stick* | Disparo con dos sticks (mando) o WASD + ratón. |
| **Tower Defense Template** | Defensa de torres | Aprender oleadas, economía y colocación. |
| **Endless Runner Template** | *Runner* infinito | Scroll forzado, puntuación sin fin. |
| **Survivor Game Template** | Supervivencia (estilo *Vampire Survivors*) | Muchos enemigos, mejoras automáticas. **El género de moda.** |
| **Idle Game Template** | Incremental / *clicker* | Economía y progresión pasiva. |
| **Match 3 Template** | Puzzle *match-3* | Lógica de rejilla y cascadas. |
| **Card Game Template** | Solitario | Cartas, arrastre, reglas por pilas. |
| **Brick Breaker Template** | *Arkanoid* | Física de rebote simple. |
| **Puzzle Slider Template** | Puzzle deslizante | Rejilla + movimiento con restricciones. |
| **Fire Jump Template** |Arcade de salto infinito | Incluye: jugador que salta, obstáculos infinitos. |
| **Cover Assault** | *Shooter* con coberturas | Buen ejemplo de IA que usa coberturas. |
| **RPG Starter Pack** | Assets para RPG | ⚠️ **No es un juego**: trae los *sprites* de los tutoriales de Action RPG y Turn-Based RPG. Úsalo si vas a seguir esos tutoriales. |
| **Hero's Trail Base - GML Visual** | Hack-and-slash en **GML Visual** | Si trabajas en GML Visual (por nodos) en lugar de GML a mano. |
| **Blank Pixel Game** | Proyecto vacío | Igual que «Blank» pero con **suavizado de imagen desactivado**. ⭐ **La correcta para pixel art.** |

### 1.2 Live Wallpapers (12)

Fractal Sky · Enchanted Forest · Ocean Waves · Opera Glitch · Opera Colours · Colour Splash · Wizardly Workshop · Weather Station · Fairy Flocking · Shader · Rain · Fire.

Son plantillas para fondos animados de **Opera GX**. Solo te interesan si publicas en GX.games.

### 1.3 GameStrip (1)

**Idle Clicker Game Strip Template** — un *Game Strip* es un minijuego integrable en el navegador Opera.

---

## 2. Cómo crear un proyecto en 2026

### Opción A: `gm-cli init` (recomendada, verificada)

```sh
# Modo interactivo: te pregunta nombre, plantilla, IA y Actions
npx @gamemaker/gm-cli@latest init

# Sin interacción: todo por flags
gm-cli init \
  --no-interactive \
  -n mi-juego \
  -t "Space Rocks" \
  --ai \
  --actions \
  --toolchain GMS2@2026.0.0.23
```

Flags verificados con `gm-cli init --help`:

| Flag | Por defecto | Para qué |
|---|---|---|
| `--interactive` / `--no-interactive` | `true` | Asistente paso a paso |
| `-n`, `--name` | — | Nombre del proyecto (**obligatorio** con `--no-interactive`) |
| `-t`, `--template` | — | ID o **coincidencia parcial del nombre** de la plantilla (**obligatorio** con `--no-interactive`) |
| `--ai` / `--no-ai` | `true` | Andamiaje para agentes de IA: `AGENTS.md`, `CLAUDE.md`, `.mcp.json`, `.claude/` |
| `--actions` / `--no-actions` | `true` | Workflows de GitHub Actions para compilar y empaquetar |
| `--toolchain` | — | Fija el toolchain: `GMS2`, `GMS2@2024.14.4`, `GMRT@0.18`… |
| `--cache-dir` | — | Directorio de caché |

> 💡 `-t` admite **coincidencia parcial**, así que `-t "Space"` funciona igual que `-t "Space Rocks"`.

### Opción B: desde el IDE

*New Project > GameMaker >* elegir plantilla. Equivalente, pero **no** genera el andamiaje de IA ni los workflows de CI.

---

## 3. Qué genera el andamiaje (`--ai --actions`) — verificado

He creado un proyecto real con `gm-cli init -n prueba-ai -t "Space Rocks" --no-interactive --ai --actions`. Esto es exactamente lo que aparece:

```
prueba-ai/
├── .claude/                    # configuración para Claude Code
├── .gitattributes
├── .github/
│   └── workflows/
│       ├── compile.yml         # compila en cada PR y push a main
│       └── package.yml         # empaqueta
├── .gitignore
├── .gmcache/                   # caché del runtime (no subir a git)
├── .mcp.json                   # servidor MCP del proyecto
├── AGENTS.md                   # reglas para agentes de IA
├── CLAUDE.md                   # idem para Claude Code
├── gm-options.json             # opciones del proyecto
├── notes/                      # notas de la plantilla
├── prueba-ai.resource_order
├── prueba-ai.yyp               # el proyecto
├── rooms/
└── sprites/
```

### `.mcp.json` (literal)

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

Esto hace que el MCP de GameMaker esté **disponible por proyecto**. Recuerda: el MCP exige un `.yyp`, así que solo funciona dentro de un proyecto creado.

### `AGENTS.md` (extracto literal)

Empieza así:

> *«Do not make changes to `.yy` or `.yyp` files yourself. It's very hard to correctly edit these manually! You MUST use commands exposed by the `gamemaker-resource-tool` MCP server.»*

Y continúa con:

- **Convenciones de nombres:** `snake_case` para variables y funciones; `_` como prefijo de variables locales (`var _valor`); prefijos por tipo de recurso (`obj_`, `spr_`…).
- **Nombres reservados que NO puedes usar:** `score`, `lives`, `health`, `x`, `y`, `sprite_index`, `image_index`, `image_speed`, `image_xscale`, `image_yscale`, `image_angle`, `image_alpha`, `image_blend`, `speed`, `direction`, `friction`, `gravity`, `gravity_direction`, `bbox_left/right/top/bottom`, `id`, `object_index`, `layer`, `depth`, `visible`, `persistent`.
- **GML moderno:** structs, `constructor`, métodos.

### GitHub Actions (extracto de `compile.yml`)

```yaml
name: Compile

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main]

env:
  GM_COMMAND: "@gamemaker/gm-cli@latest"

jobs:
  compile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/cache@v5
        with:
          path: .gmcache
```

> ⚠️ **Nota del propio workflow:** en Linux hace falta **ffmpeg** (referencia: `YoYoGames/GameMaker-Bugs` issue 4977). El workflow ya lo tiene en cuenta.

---

## 4. ⚠️ Incidencia encontrada al probar (importante)

Al intentar crear la **Platformer Template** con `gm-cli`, el proceso **falló**:

```
Command failed:
Failed to restore project. "ProjectTool PREFABS RESTORE" exited with code 1
```

**Diagnóstico:** las plantillas que usan **prefabs** (como Platformer Template) dependen de la herramienta `PREFABS RESTORE`, que falla. ⚠️ **No es un problema de versión del CLI**: se probó primero en 2.2.0 y **se reverificó en 2.3.0 el 02-09-2026 — sigue fallando igual**. Detalle completo y matriz de pruebas en [`07 · 13` §12](./13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md#12-bug-conocido-las-plantillas-con-prefabs-fallan-al-crear-el-proyecto).

⚠️ **No es solo Platformer Template.** De las 18 plantillas de juego de §1.1, **9 fallan y 9
funcionan** — siete más de las que fallan sin ningún aviso previo aquí. La tabla completa con
las 18 verificadas una a una está en [`12 · 09` §0, Trampa
1](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-1--9-de-las-18-plantillas-de-gm-cli-init-fallan-hoy-en-macos)
— no se repite aquí para no desincronizarse con ella.

Con **Space Rocks** (que no usa prefabs) el comando funciona perfectamente en cualquiera de las dos versiones, y genera el árbol completo mostrado en la sección 3.

> **Conclusión práctica:** si `gm-cli init` te falla con «PREFABS RESTORE», **no es tu instalación ni tu versión del CLI** — no pierdas tiempo actualizando. Usa una de las 9 plantillas que sí funcionan (`12 · 09` §0), crea el proyecto desde el IDE, o usa una plantilla sin prefabs.

---

## 5. Plantillas de la comunidad

He buscado específicamente repos de plantillas GameMaker en GitHub. **Resultado sincero: no hay ninguna que merezca la pena en 2026.**

Los únicos resultados tienen **0–1 estrellas**, sin licencia declarada y sin actividad reciente:

| Repo | ★ | Último push | Licencia |
|---|---:|---|---|
| `Manwithacape/Gamemaker-Template` | 0 | 2025-02-02 | sin licencia |
| `YakovDavis/GM-JamTemplate` | 1 | 2024-10-05 | sin licencia |
| `dylanlep/491A-Gamemaker-Example` | 0 | 2026-02-25 | sin licencia |
| `lucmsilva651/spacerocks-gml` | 1 | 2024-05-26 | sin licencia |
| `Krapin2000/playgama-bridgeGamemakerTemplate` | 0 | 2025-07-01 | sin licencia |

**Recomendación:** no pierdas tiempo con plantillas de terceros sin licencia. Usa las oficiales y apóyate en **librerías con licencia limpia** (ver archivo 02) para lo que la plantilla no cubra.

---

## 6. Cómo estructurar tu proyecto desde cero

Ni el IDE ni `gm-cli` te imponen una estructura de carpetas; la plantilla **Space Rocks** trae solo `sprites/`, `rooms/` y `notes/`. Tú decides el resto.

### 6.1 Estructura recomendada

```
mi-juego/
├── mi-juego.yyp
├── gm-options.json
├── AGENTS.md / CLAUDE.md        # generados por gm-cli init --ai
│
├── scripts/                     # TODO el código GML
│   ├── ScrUtilidades/
│   │   └── ScrUtilidades.gml
│   ├── ScrEasing/
│   │   └── ScrEasing.gml
│   ├── Config/                  # constantes y macros globales
│   │   └── ScrConfig.gml
│   ├── Datos/                   # structs con datos (armas, enemigos, niveles)
│   │   └── ScrDatosEnemigos.gml
│   └── Sistemas/                # sistemas transversales (guardado, audio, input)
│       ├── ScrGuardado/
│       └── ScrAudio/
│
├── objects/
│   ├── Jugador/
│   ├── Enemigos/
│   ├── UI/
│   └── Sistemas/                # obj_controlador_juego, obj_camara…
│
├── sprites/
│   ├── jugador/
│   ├── enemigos/
│   └── ui/
│
├── rooms/
│   ├── rm_menu/
│   ├── rm_nivel_01/
│   └── rm_plantillas/           # rooms que NO se juegan: plantillas para
│                                # GMRoomLoader o generación procedural
│
├── tilesets/
├── fonts/
├── sounds/
├── shaders/
├── datafiles/                   # JSON/CSV incluidos en el juego
└── notes/                       # notas de diseño (la plantilla ya lo trae)
```

**Regla para `scripts/`:** en GameMaker cada script vive en su propia carpeta (`scripts/NombreScript/NombreScript.gml`). **No** pongas dos scripts sueltos en `scripts/`.

### 6.2 Convenciones de nombres

| Tipo | Convención | Ejemplo |
|---|---|---|
| Script / función | `Scr` + PascalCase, o `snake_case` | `ScrGuardado` · `ruido_perlin` |
| Objeto | `obj_` + snake_case | `obj_jugador` |
| Sprite | `spr_` | `spr_jugador_correr` |
| Room | `rm_` | `rm_nivel_01` |
| Tileset | `ts_` | `ts_bosque` |
| Font | `fnt_` | `fnt_dialogo` |
| Sonido | `snd_` | `snd_disparo` |
| Shader | `shd_` | `shd_agua` |
| Variable local | `_` + snake_case | `var _velocidad` |
| Constante / macro | `MAYUSCULAS` | `VELOCIDAD_MAXIMA` |
| Constructor (struct) | PascalCase | `function Tween() constructor` |
| Método de struct | PascalCase | `.Actualizar()` |

### 6.3 Orden de arranque (evita el clásico «la variable no existe»)

Usa un **objeto controlador persistente** creado en la primera room, y centraliza la inicialización:

```gml
// obj_controlador_juego · Create  (marcado como Persistent)
// Se crea en rm_inicio y viaja por todas las rooms.

// 1) Constantes y macros
#macro VERSION_GUARDADO 1
#macro TAMANO_TILE 32

// 2) Estado global del juego
global.nivel_actual   = 1;
global.vidas          = 3;
global.volumen_musica = 1;
global.partida        = GuardadoCargar();

// 3) Sistemas transversales
global.pool_balas = new Pool(obj_bala, "Instances", 64);
global.camara     = new CamaraShake();

// 4) Ir al menú
room_goto(rm_menu);
```

### 6.4 Checklist de un proyecto bien empezado

- [ ] Creado con `gm-cli init --ai --actions` (te regala CI, MCP y reglas para agentes).
- [ ] `.gitignore` incluye `.gmcache/` (ya viene en el generado por `gm-cli`).
- [ ] Toolchain fijado con `--toolchain` para que CI y local compilen igual.
- [ ] Un solo objeto controlador persistente como punto de entrada.
- [ ] Ninguna variable global inicializada «por casualidad» en el Create de un objeto que no existe en todas las rooms.
- [ ] Nombres de recursos con prefijos (`obj_`, `spr_`, `rm_`…).
- [ ] Sin nombres reservados (`speed`, `score`, `health`, `id`…).
- [ ] Si trabajas con agentes de IA: **nunca edites `.yy`/`.yyp` a mano**, usa `gm-cli resourcetool eval|repl|mcp`.

---

## 7. Resumen: ¿qué plantilla elijo?

```
¿Es tu primer proyecto en GameMaker?
├─ SÍ  → Space Rocks (léelo entero, modifícalo, rómpelo)
└─ NO
   ├─ ¿Pixel art?           → Blank Pixel Game (suavizado desactivado)
   ├─ ¿Plataformas?         → Platformer Template   ⚠️ falla con `gm-cli init` (§4) — créalo desde el IDE
   ├─ ¿Shooter?             → Scrolling Shooter / Twin Stick Shooter
   ├─ ¿Supervivencia?       → Survivor Game Template
   ├─ ¿Puzzle?              → Match 3 / Puzzle Slider
   ├─ ¿GML Visual (nodos)?  → Hero's Trail Base
   ├─ ¿Publicas en Opera?   → Live Wallpaper * / GameStrip
   └─ ¿Quieres aprender?    → Space Rocks + los repos del archivo 04
```

> **Y recuerda:** la plantilla solo te da el esqueleto. Para todo lo demás (input, texto, audio, guardado, niveles modulares) tira de las librerías del **archivo 02**, que son las que de verdad te ahorran semanas.
