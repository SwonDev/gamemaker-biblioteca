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

El primer comando deriva firmas del runtime real. El segundo debe mostrar la ficha. Para comprobar toda la biblioteca ejecuta `python _indice/actualizar.py`; puede compilar ejemplos y tarda más.

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

El destino genérico `~/.agents/skills` se instala siempre; los demás se activan al encontrar el comando del agente en el PATH. Es compatibilidad de formato y rutas, no una prueba de todos los CLI. Verifica la versión y el descubrimiento de skills de tu agente.

Para otro agente, referencia `_indice/skills/gamemaker-biblioteca/AGENTS.md` desde sus instrucciones. **Integra su contenido sin sobrescribir un AGENTS.md existente.** Aider puede referenciarlo mediante `read`; el instalador no cambia su configuración.

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
