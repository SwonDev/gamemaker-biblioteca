# Instalar la biblioteca y la skill

[Portada](README.md) · [Biblioteca](GUIA.md)

Una **skill** es una carpeta de instrucciones que tu agente carga al trabajar con GameMaker. La biblioteca contiene la documentación y las herramientas que consulta. Necesitas ambas en tu equipo.

## Instala con un comando

Necesitas [Python 3.10 o posterior](https://www.python.org/downloads/). En macOS/Linux,
copia este comando en tu terminal:

```sh
python3 -c "import hashlib,urllib.request; b=urllib.request.urlopen('https://raw.githubusercontent.com/SwonDev/gamemaker-biblioteca/r50/instalar-remoto.py').read(); exec(compile(b,'instalar-remoto.py','exec')) if hashlib.sha256(b).hexdigest()=='585fec194d4768d30437cbbf4133670eeb134ef0057a3f7211cea23c6937faf1' else exit('Descarga no válida')"
```

En **Windows, PowerShell**:

```powershell
py -3 -c "import hashlib,urllib.request; b=urllib.request.urlopen('https://raw.githubusercontent.com/SwonDev/gamemaker-biblioteca/r50/instalar-remoto.py').read(); exec(compile(b,'instalar-remoto.py','exec')) if hashlib.sha256(b).hexdigest()=='585fec194d4768d30437cbbf4133670eeb134ef0057a3f7211cea23c6937faf1' else exit('Descarga no válida')"
```

Si tu Python se llama `python`, usa ese nombre. La descarga está fijada a **r50** y el comando
comprueba el bootstrap por SHA-256 antes de ejecutarlo. El bootstrap resuelve el commit,
descarga la distribución pública y comprueba el paquete. HTTPS y el repositorio oficial son
la fuente de confianza; el manifiesto detecta alteraciones, no constituye una firma independiente.

La biblioteca queda en `~/.local/share/gamemaker-biblioteca`; las instrucciones se instalan
en los destinos compatibles de la tabla. No se necesita Git, Bash, PyYAML, Pillow, una clave
API ni GameMaker para este paso. Para ejecutar juegos necesitas [GameMaker](https://gamemaker.io/download).
El manual completo y los clones de terceros son [opcionales](PUBLICAR.md).

El instalador guarda la ruta de biblioteca junto a cada destino y un fallback global; comprueba las copias y conserva
las anteriores. No cambia modelos, proveedores, claves, permisos ni configuración del agente.
No instala hooks o servicios residentes. El recibo local identifica el commit descargado.

## Si prefieres un checkout o una descarga manual

Descarga el [ZIP r50](https://github.com/SwonDev/gamemaker-biblioteca/archive/refs/tags/r50.zip),
extráelo y ejecuta dentro `python3 instalar.py` (Windows: `py -3 instalar.py`). Con Git:

```sh
git clone https://github.com/SwonDev/gamemaker-biblioteca.git
cd gamemaker-biblioteca
python3 instalar.py
```

`./instalar.sh` y `./instalar.ps1` delegan en la misma implementación Python.
Para elegir una biblioteca distinta en el bootstrap descargado, usa `--biblioteca /ruta`.
El modo local funciona sin conexión con un paquete completo y su manifiesto.

## Úsala en tu proyecto

Abre tu agente en la carpeta donde trabajarás y escribe:

> Quiero hacer un juego con GameMaker. Será de plataformas 2D para ordenador.

No necesitas nombrar la skill ni elegir capas. El agente sitúa los requisitos, usa asesoría
para decisiones de peso y prepara la especificación antes de crear recursos. Para una duda
GML consulta las fuentes de esa API, sin asesor arquitectónico por rutina. La documentación,
las herramientas y las skills de método externas no se cargan todas en cada conversación.

La selección automática depende del modelo y del soporte del agente. Si la acabas de instalar
con una conversación ya abierta, actualiza su catálogo o abre una conversación nueva; en Claude,
`/reload-skills` puede recargarla. Si no aparece, comprueba la ruta impresa y el catálogo del
agente. La invocación explícita por nombre sigue disponible para diagnosticar problemas.
[Pruebas observadas y límites](./_indice/auditorias/r25-validacion.md).

## Mantenimiento de la biblioteca (opcional)

Para regenerar índices o editar el paquete, prepara un entorno separado dentro del checkout:

```sh
python3 -m venv .venv
```

Actívalo con `source .venv/bin/activate` en Bash/zsh o `.venv\Scripts\Activate.ps1` en
PowerShell. Después instala `python -m pip install -r _indice/requirements.txt`.
PyYAML valida YAML durante mantenimiento; Pillow sirve para comprobar imágenes.
La instalación normal consume el manifiesto ya generado y no requiere esas dependencias.

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

`python3 instalar.py --indices` solicita generación de índices antes de instalar. Si falla, sale con error y conserva tus instalaciones.

Sin GameMaker puedes leer documentación e instalar la skill. Contrasta las firmas con el manual oficial o `gm-cli manual read`; un índice ausente no implica que una función no exista.

## Qué CLI de IA están soportados

| Agente | Destino | Fuente |
|---|---|---|
| Claude Code | `~/.claude/skills` | [Skills](https://code.claude.com/docs/en/skills) |
| Codex | `~/.agents/skills` (canónica) | [Agent Skills](https://developers.openai.com/codex/skills) |
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

Por defecto se preparan **todos los destinos de esta tabla**, aunque la app o extensión
no tenga CLI en el PATH. Las rutas compartidas se deduplican. No se instalan los agentes.
Puedes limitarlo a uno o detectar solo comandos/directorios existentes:

```sh
python3 instalar.py --listar-harnesses
python3 instalar.py --harness codex
python3 instalar.py --detectar
```

Nombres: `agents`, `claude`, `codex`, `opencode`, `qwen`, `kimi`, `gemini`, `copilot`,
`cursor`, `cline`, `pi`, `omp`, `minimax`, `dsh`, `hermes`, `gentle-shell`. La instalación
normal y `--harness` registran la biblioteca; no necesitan exportar `GM_BIBLIOTECA`.

El instalador respeta `CLAUDE_CONFIG_DIR`, `OPENCODE_CONFIG_DIR`, `PI_CODING_AGENT_DIR`, `PI_CONFIG_DIR`, `OMP_PROFILE`/`PI_PROFILE`, `MINIMAX_DATA_DIR`, `DSH_HOME`, `HERMES_HOME` y `GENTLE_SHELL_HOME`. Revisa los destinos impresos. Un perfil MiniMax, una opción `--home`, una configuración de gentle-shell con otro home o directorios personalizados en Qwen requieren `--destino /ruta/efectiva/skills`. El instalador conserva la configuración existente.

Hermes usa en Windows `%LOCALAPPDATA%/hermes/skills` (sin esa variable, `~/AppData/Local/hermes/skills`); respeta además `HERMES_DATA_DIR_SUFFIX`. Para OMP, `PI_CONFIG_DIR` es relativo al home: una ruta absoluta o con `~` se rechaza y requiere un `PI_CODING_AGENT_DIR` absoluto o `--destino`. Los wrappers pueden seleccionar otro home al arrancar: confirma la ubicación efectiva en el catálogo.

**Copiado, descubierto y utilizado son estados distintos.** Pi/OMP pueden condicionar skills de proyecto a confianza; MiniMax puede desactivar fuentes externas; Hermes requiere confianza para fuentes de proyecto; `dsh` necesita su proveedor filesystem y consumidor de skills activos. Las pruebas de cargadores usan el código instalado en macOS, sin peticiones a modelos. No certifican todos los CLI, proveedores o instalaciones Windows/Linux. Consulta los recibos en `_indice/auditorias/` y confirma el catálogo de tu agente.

`dsh` es DeepSeek Harness. `codex-deepseek` conserva la carga de skills de Codex; usar un modelo DeepSeek dentro de otro agente no lo convierte en `dsh`.

Para otro agente, referencia `_indice/skills/gamemaker-biblioteca/AGENTS.md` desde sus instrucciones. **Integra su contenido sin sobrescribir un AGENTS.md existente.** Conserva acceso a la biblioteca y las referencias del paquete. Aider puede referenciarlo mediante `read`; el instalador no cambia su configuración. Un agente que no cargue instrucciones ni pueda consultar archivos necesita adaptación propia: el formato por sí solo no habilita herramientas, ejecución o verificación.

## Actualizar o comprobar

Repite el comando de instalación de la revisión que quieras instalar. Una distribución
idéntica no se recopia; una diferente conserva la biblioteca anterior completa, incluidos
los cambios locales, antes de promoverla. No borra backups automáticamente. En un checkout
Git conserva tus cambios, ejecuta `git pull --ff-only` y después `python3 instalar.py`.

```sh
python3 instalar.py --comprobar
python3 instalar.py --destino /ruta/a/skills --registrar
```

`--comprobar` valida paquete y plan sin instalar, registrar ni regenerar derivados. El segundo
comando instala solo en ese destino y registra la biblioteca; sin `--registrar`, escribe solo su ruta adyacente y no cambia el fallback global. El agente
localiza los documentos igualmente, sin exportar variables.
`--enlace` es opcional para mantenedores; en Windows requiere soporte/permiso de symlinks.
En el bootstrap remoto, `--comprobar` descarga y valida **solo la distribución**: no promueve
la biblioteca y todavía no puede evaluar los enlaces contra su futura ubicación estable.
Para comprobar destinos y aliases usa el comando local anterior. Una instalación remota
normal sí comprueba ese plan antes de modificar las copias de skills.

Las copias anteriores quedan junto al destino en `.gamemaker-biblioteca-backups`.
Conserva el recibo: identifica cada copia y backup. Si falla una promoción, se restaura ese
destino; un fallo posterior puede dejar otros ya actualizados y lo indica la salida.
Los aliases a una copia compartida se conservan cuando el referente está dentro del plan;
si queda fuera, el instalador pide seleccionar explícitamente ese destino.

## Si algo falla

| Síntoma | Qué comprobar |
|---|---|
| Falta PyYAML o Pillow durante mantenimiento | Activa `.venv` e instala `_indice/requirements.txt`; la instalación normal no los necesita |
| No encuentra Python | `python3 --version` o `python --version`: 3.10 o posterior |
| No hay índice de símbolos | Instala el runtime y ejecuta `python _indice/construir-indices.py` |
| No encuentra la biblioteca | Reinstala desde la ubicación actual o establece `GM_BIBLIOTECA` |
| La skill sigue antigua | Actualiza el catálogo o abre una conversación nueva; coteja la versión de su copia |
| Búsqueda de código/manual vacía | [Reconstruye el corpus opcional](PUBLICAR.md) |

[Abre un issue](https://github.com/SwonDev/gamemaker-biblioteca/issues) con sistema, versiones, comando y salida sin rutas personales, claves ni contenido privado.
