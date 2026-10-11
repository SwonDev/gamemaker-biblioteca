# Instalar la biblioteca y la skill

[Portada](README.md) · [Biblioteca](GUIA.md)

Una **skill** es una carpeta de instrucciones que tu agente carga al trabajar con GameMaker. La biblioteca contiene la documentación y las herramientas que consulta. Necesitas ambas en tu equipo.

## Prepara tu equipo

Instala [Git](https://git-scm.com/downloads) y [Python 3.10 o posterior](https://www.python.org/downloads/). En Windows, usa Git Bash; los scripts `.sh` requieren Bash. Para ejecutar juegos necesitas además [GameMaker](https://gamemaker.io/download).

Esta revisión verifica ejecución real en macOS. Los scripts Python contemplan rutas Windows/Linux, pero no se certifican sus instalaciones nativas. Un agente sin soporte de skills puede leer el `AGENTS.md` generado.

## Descarga e instala

```bash
git clone https://github.com/SwonDev/gamemaker-biblioteca.git
cd gamemaker-biblioteca
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r _indice/requirements.txt
./instalar.sh
```

En **Git Bash**, cambia la cuarta línea por `source .venv/Scripts/activate`. Si `python3` no existe y `python --version` muestra 3.10 o posterior, usa `python -m venv .venv`.

`.venv` separa las dependencias del Python del sistema. PyYAML verifica las instrucciones; Pillow permite comprobar imágenes. No necesitas pagar una API para instalar la biblioteca.

El instalador valida el paquete, copia la skill a los destinos detectados y registra la ruta local en `~/.config/gamemaker-biblioteca/ruta`. Conserva cada copia anterior en `.gamemaker-biblioteca-backups` junto a su directorio de skills. No modifica proveedores, claves ni modelos.

## Úsala en tu proyecto

Reabre tu agente, entra en la carpeta del juego y pide:

> Usa gamemaker-biblioteca. Lee sus reglas, sitúa el estado actual y verifica las funciones contra mi runtime antes de escribir GML.

El agente debe localizar la biblioteca y declarar si el índice está disponible. Si no activa la skill automáticamente, invócala por nombre o consulta la documentación de skills de tu CLI.

## Activar las herramientas de GML

Con GameMaker y su runtime instalados, activa `.venv` y ejecuta:

```bash
python _indice/construir-indices.py
python _indice/buscar.py draw_sprite_ext
```

El primer comando deriva firmas de la fuente seleccionada. El segundo debe mostrar la ficha. **La caché no acredita qué runtime usa tu proyecto.** Comprueba ese dato en el IDE o configuración de compilación y selecciona la misma versión:

```bash
export GM_BIBLIOTECA_RUNTIME=2026.0.0.23
python _indice/construir-indices.py
```

También admite la carpeta de un runtime del IDE que contenga `GmlSpec.xml`. En PowerShell: `$env:GM_BIBLIOTECA_RUNTIME = '2026.0.0.23'`. No cambia el runtime del proyecto. Una selección inválida aborta. Sin selector se usa la versión numéricamente más alta disponible en la caché de GameMakerCLI; compara siempre `meta.runtime` con el proyecto.

Para comprobar toda la biblioteca ejecuta `python _indice/actualizar.py`; puede compilar ejemplos y tarda más.

`./instalar.sh --indices` solicita generación de índices antes de instalar. Si falla, sale con error y conserva tus instalaciones.

Sin GameMaker puedes leer documentación e instalar la skill. Contrasta las firmas con el manual oficial o `gm-cli manual read`; un índice ausente no implica que una función no exista.

## Qué CLI de IA están soportados

| Agente | Destino | Fuente |
|---|---|---|
| Claude Code | `~/.claude/skills` | [Skills](https://code.claude.com/docs/en/skills) |
| Codex | `~/.agents/skills` y heredada `~/.codex/skills` | [Agent Skills](https://developers.openai.com/codex/skills) |
| OpenCode | `~/.config/opencode/skills` | [Skills](https://opencode.ai/docs/skills/) |
| Qwen Code | `~/.qwen/skills` | [Skills](https://github.com/QwenLM/qwen-code/blob/main/docs/users/features/skills.md) |
| Kimi Code CLI | `~/.kimi-code/skills` | [Skills](https://moonshotai.github.io/kimi-cli/en/customization/skills.html) |
| Gemini CLI | `~/.gemini/skills` | [Skills](https://geminicli.com/docs/cli/skills/) |
| Copilot CLI | `~/.copilot/skills` | [Skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-skills) |
| Cursor CLI | `~/.cursor/skills` | [Skills](https://cursor.com/docs/context/skills) |
| Cline | `~/.cline/skills` | [Skills](https://docs.cline.bot/features/skills) |
| Pi | `~/.pi/agent/skills` | [Skills](https://github.com/earendil-works/pi/blob/v1.1.0/packages/coding-agent/docs/skills.md) |
| OMP (Oh My Pi) | `~/.omp/agent/skills` | [Skills](https://github.com/can1357/oh-my-pi/blob/main/docs/skills.md) |
| MiniMax Code (`mcode`) | `~/.minimax/skills` | [Repositorio oficial](https://github.com/MiniMax-AI/MiniMax-Code) |
| DeepSeek Harness (`dsh`) | `~/.dsh/skills` | [Cargador oficial](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md) |
| Hermes Agent | `~/.hermes/skills` | [Skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/) |
| gentle-shell | `~/.gentle-shell/agent/skills`, modo aislado | [Repositorio oficial](https://github.com/Gentleman-Programming/gentle-shell) |

El destino genérico `~/.agents/skills` se instala siempre; los demás se activan al encontrar el comando del agente en el PATH. Para elegir solo uno, incluso antes de instalar el agente:

```bash
./instalar.sh --listar-harnesses
./instalar.sh --harness dsh
```

Nombres: `agents`, `claude`, `codex`, `opencode`, `qwen`, `kimi`, `gemini`, `copilot`, `cursor`, `cline`, `pi`, `omp`, `minimax`, `dsh`, `hermes`, `gentle-shell`. Con `--harness`, establece `GM_BIBLIOTECA` para que el agente localice también los documentos; ese modo instala un único destino sin registrar rutas globales.

El instalador respeta `CODEX_HOME`, `PI_CODING_AGENT_DIR`, `PI_CONFIG_DIR`, `OMP_PROFILE`/`PI_PROFILE`, `MINIMAX_DATA_DIR`, `DSH_HOME`, `HERMES_HOME` y `GENTLE_SHELL_HOME`. Revisa los destinos impresos. Un perfil MiniMax, una opción `--home`, una configuración de gentle-shell con otro home o directorios personalizados en Qwen requieren `--destino /ruta/efectiva/skills`. El instalador conserva la configuración existente.

Hermes usa en Windows `%LOCALAPPDATA%/hermes/skills` (sin esa variable, `~/AppData/Local/hermes/skills`); respeta además `HERMES_DATA_DIR_SUFFIX`. Para OMP, `PI_CONFIG_DIR` es relativo al home: una ruta absoluta o con `~` se rechaza y requiere un `PI_CODING_AGENT_DIR` absoluto o `--destino`. Los wrappers pueden seleccionar otro home al arrancar: confirma la ubicación efectiva en el catálogo.

**Copiado, descubierto y utilizado son estados distintos.** Pi/OMP pueden condicionar skills de proyecto a confianza; MiniMax puede desactivar fuentes externas; Hermes requiere confianza para fuentes de proyecto; `dsh` necesita su proveedor filesystem y consumidor de skills activos. Las pruebas de cargadores usan el código instalado en macOS, sin peticiones a modelos. No certifican todos los CLI, proveedores o instalaciones Windows/Linux. Consulta los recibos en `_indice/auditorias/` y confirma el catálogo de tu agente.

`dsh` es DeepSeek Harness. `codex-deepseek` conserva la carga de skills de Codex; usar un modelo DeepSeek dentro de otro agente no lo convierte en `dsh`.

Para otro agente, referencia `_indice/skills/gamemaker-biblioteca/AGENTS.md` desde sus instrucciones. **Integra su contenido sin sobrescribir un AGENTS.md existente.** Conserva acceso a la biblioteca y las referencias del paquete. Aider puede referenciarlo mediante `read`; el instalador no cambia su configuración. Un agente que no cargue instrucciones ni pueda consultar archivos necesita adaptación propia: el formato por sí solo no habilita herramientas, ejecución o verificación.

## Actualizar o comprobar

```bash
git pull --ff-only
source .venv/bin/activate
python -m pip install -r _indice/requirements.txt
./instalar.sh
```

Conserva tus cambios locales antes de actualizar. `--comprobar` valida y regenera derivados de la skill en el checkout, sin instalar ni registrar rutas. `--enlace` usa enlaces simbólicos para quien mantiene la biblioteca.

Para un destino propio: `./instalar.sh --destino /ruta/a/skills`. Instala solo ahí y no registra rutas globales; establece `GM_BIBLIOTECA` con la ubicación de la biblioteca en el entorno del agente.

## Si algo falla

| Síntoma | Qué comprobar |
|---|---|
| Falta PyYAML o Pillow | Activa `.venv` e instala `_indice/requirements.txt` |
| No encuentra Python | `python3 --version` o `python --version`: 3.10 o posterior |
| No hay índice de símbolos | Instala el runtime y ejecuta `python _indice/construir-indices.py` |
| No encuentra la biblioteca | Reinstala desde la ubicación actual o establece `GM_BIBLIOTECA` |
| La skill sigue antigua | Reabre el agente y coteja la versión de su copia |
| Búsqueda de código/manual vacía | [Reconstruye el corpus opcional](PUBLICAR.md) |

[Abre un issue](https://github.com/SwonDev/gamemaker-biblioteca/issues) con sistema, versiones, comando y salida sin rutas personales, claves ni contenido privado.
