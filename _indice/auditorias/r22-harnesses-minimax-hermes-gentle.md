# r22 — Carga portable de la skill en MiniMax Code, Hermes y Gentle Shell

**Fecha de comprobación:** 2026-10-11. **Alcance:** descubrimiento y lectura nativos de `gamemaker-biblioteca`, usando instalaciones existentes y directorios temporales. No se instalaron agentes, dependencias ni modelos; no se cambió configuración global ni se invocó un LLM. La pausa de proyectos ajenos continúa vigente.

## 1. Identidad comprobada

| Harness | Identidad local observada | Fuente de versión |
|---|---|---|
| MiniMax Code | `mcode` 0.6.5; paquete `@minimax-ai/code` | `mcode --version` y `package.json` instalado |
| Hermes Agent | Base 0.21.5; intérprete seleccionado Python 3.14.7 | `install-stamp.json`, clave `baseVersion`, y `--version` del intérprete del launcher |
| Gentle Shell | `gentle-shell` 4.0.0; paquete `gentle-pi`; Pi 1.1.0 | `gentle-shell --version` y metadatos de ambos paquetes |

No apareció un binario `minimax` en la búsqueda local; el comando disponible es `mcode`. En Hermes, el `0.0.0` de `pyproject.toml` es un marcador y no reemplaza la identidad del sello de instalación. Las versiones observadas delimitan esta prueba; no constituyen una recomendación de actualización.

Los wrappers locales de MiniMax y Gentle Shell tienen operaciones adicionales en el arranque habitual. Se usaron únicamente sus ramas de ayuda/versión, comprobadas por lectura, y después módulos de los loaders. No se ejecutaron `init`, `setup`, actualización, autenticación ni sesiones interactivas.

## 2. Directorios que el loader reconoce

En todas las filas, el paquete termina en `gamemaker-biblioteca/SKILL.md`. Un destino personalizado debe señalar la carpeta de skills que el harness utiliza realmente.

| Harness y ámbito | Directorio nativo | Condición |
|---|---|---|
| MiniMax, usuario | `<dataDir>/skills` | `MINIMAX_DATA_DIR`; después el alias legado `MAVIS_DATA_DIR`; sin personalización, `~/.minimax/skills`. Un perfil o argumento de directorio puede seleccionar otro `dataDir` |
| MiniMax, proyecto | `.minimax/skills`, `.claude/skills`, `.agents/skills` | Fuentes externas habilitadas y fuente concreta habilitada; el ascenso de carpetas depende de `walkUp` |
| MiniMax, compartido de usuario | `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills` | Mismas condiciones de fuentes externas; no son sustitutos de `<dataDir>/skills` |
| Hermes, perfil | `<HERMES_HOME>/skills` | `HERMES_HOME` selecciona el perfil; en POSIX el valor predeterminado es `~/.hermes`; en Windows es `<LOCALAPPDATA>/hermes`, con alternativa `~/AppData/Local/hermes`. `HERMES_DATA_DIR_SUFFIX` se concatena literalmente a `.hermes` o `hermes`; el loader no añade un guion |
| Hermes, proyecto | `.hermes/skills`, `.agents/skills` bajo la raíz Git | Descubrimiento habilitado y raíz confiable; copiar una skill no concede esa confianza |
| Hermes, compartido | Rutas de `skills.external_dirs` | Configuración explícita; admite expansión de variables y `~` |
| Gentle Shell, aislado | `<GENTLE_SHELL_HOME>/skills` | Sin selección persistida ni bandera que cambie el modo, el home es `~/.gentle-shell/agent` |
| Gentle Shell, enlazado | `<PI_CODING_AGENT_DIR>/skills` | Modo `--link`; sin esa variable usa `~/.pi/agent` |
| Gentle Shell, ruta explícita | `<home seleccionado>/skills` | `--home` o selección persistida del launcher |
| Pi, proyecto o ruta adicional | `.pi/skills`; rutas configuradas o explícitas | El resolvedor completo aplica confianza a recursos de proyecto; también contempla `.agents/skills` compartidas |

MiniMax admite enlaces de directorio en las fuentes indicadas; `SKILL.md` debe ser un archivo regular. La documentación actual de [MiniMax sobre enlaces de skills](https://github.com/MiniMax-AI/minimax-code/blob/main/docs/tui-capabilities.md#skill-directory-links) coincide con la inspección del paquete 0.6.5; sus otras cifras históricas no se trasladan a esta prueba.

Hermes distingue skills de perfil, externas y de proyecto; sus reglas de confianza y precedencia se documentan en [Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/). Aquí se probó la carpeta del perfil aislado, no la concesión de confianza a un repositorio real.

## 3. Gentle Shell selecciona el home de Pi

`resolveHome` del launcher 4.0.0 resuelve una selección por bandera antes de la selección persistida, y esta antes del modo aislado predeterminado. En modo aislado utiliza `GENTLE_SHELL_HOME`; en modo enlazado utiliza `PI_CODING_AGENT_DIR`. `buildPiInvocation` entrega el home resultante al proceso Pi mediante `PI_CODING_AGENT_DIR` y `GENTLE_PI_AGENT_HOME`. `GENTLE_SHELL_PI` selecciona el ejecutable de Pi, no la carpeta de skills. Fuente: [launcher 4.0.0](https://github.com/Gentleman-Programming/gentle-shell/blob/v4.0.0/runtime/gentle-shell-launcher.mjs).

El registro `.atl/skill-registry.md` enumera otras carpetas para orientar la resolución, pero no equivale a inyectar todos sus cuerpos en Pi. No hay evidencia para inventar `~/.gentle-shell/skills`. La [referencia de Gentle Shell 4.0.0](https://github.com/Gentleman-Programming/gentle-shell/blob/v4.0.0/docs/readme-reference.md#skill-registry) distingue ese registro del catálogo inyectado. Para un home personalizado, el instalador debe aceptar un destino explícito; esta investigación no inspeccionó la configuración personal para adivinarlo.

## 4. Formato y fuentes locales utilizadas

La skill de esta biblioteca mantiene `name: gamemaker-biblioteca`, `description` y cuerpo Markdown en UTF-8. Las tres instalaciones aceptaron su formato. Pi separa el catálogo de nombre, descripción y ubicación de la expansión posterior del cuerpo; `/skill:gamemaker-biblioteca` fuerza esa expansión. Fuente: [skills de Pi 1.1.0](https://github.com/earendil-works/pi/blob/v1.1.0/packages/coding-agent/docs/skills.md).

Fuentes instaladas inspeccionadas, con rutas relativas a cada paquete:

- MiniMax: `cli.js`, `chunks/data-dir-KFZIXVT7.js`, `chunks/chunk-OSA3A5UV.js`, `chunks/chunk-TWO6GIVD.js`, `chunks/chunk-JIWEZSQY.js` y `chunks/chunk-2XPMNZVR.js`: resolución del directorio, fuentes, registro, lectura y diagnósticos.
- Hermes: `hermes_constants.py`, `agent/skill_utils.py`, `tools/skills_tool.py`, `hermes_cli/version_info.py` y `pm/environments.py`: home, descubrimiento, lectura e identidad. No se activó el bootstrap que puede reparar la instalación.
- Gentle Shell: `bin/gentle-shell.mjs` y `runtime/gentle-shell-launcher.mjs`; Pi: `dist/config.js`, `dist/core/skills.js`, `dist/core/package-manager.js` y `dist/core/agent-session.js`.

Los alias minificados del bundle de MiniMax son detalles de esa instalación, no una API pública estable para un futuro instalador. Los derechos y archivos de esos paquetes se conservaron; el informe describe su comportamiento sin redistribuirlos.

## 5. Evidencia de carga aislada

Se copiaron los archivos de la skill a tres fixtures temporales. Los procesos recibieron un entorno mínimo, sin credenciales heredadas. No se reasignó `HOME`: se utilizaron las variables propias de cada harness. Las conexiones y los subprocesos se bloquearon antes de importar los loaders.

| Prueba | Resultado observado |
|---|---|
| MiniMax, constructor nativo del registro | Una skill disponible, cero diagnósticos; `readByLocationUri` devuelve exactamente el archivo original |
| Pi, `loadSkills` nativo | Una skill disponible, cero diagnósticos; entrada en `formatSkillsForPrompt`; archivo idéntico |
| Pi, `_expandSkillCommand` nativo | Cuerpo completo conservado, tras retirar el frontmatter como hace el harness; argumento de prueba conservado |
| Gentle Shell, `resolveHome` nativo | Cinco escenarios correctos: predeterminado, variable de aislado, enlazado, bandera de ruta y selección persistida |
| Gentle Shell, `buildPiInvocation` nativo | El home seleccionado llega a las dos variables del proceso Pi |
| Hermes, descubrimiento y `skill_view(preprocess=False)` | Una skill disponible; `success: true`; contenido idéntico |

Los dos procesos de la pasada final salieron con código **0**. En Hermes, el primer intento con el intérprete seleccionado sin su generación de dependencias falló por `ruamel`; se repitió añadiendo únicamente al `sys.path` las dependencias ya seleccionadas. No se instaló nada ni se cambió esa selección. Durante la importación final, seis sondas de plugins encontraron el bloqueo de subprocesos; la lectura de la skill pasó. Ese límite se conserva en el resultado y no se presenta como validación de los proveedores.

## 6. Consecuencias para la instalación portable

El instalador de la biblioteca puede copiar el mismo paquete a la carpeta nativa del harness elegido. Debe respetar sus variables de directorio y ofrecer un destino explícito para perfiles, selecciones persistidas o rutas personalizadas. No necesita ejecutar el agente, iniciar sesión, configurar modelos, instalar dependencias del harness ni conceder confianza a proyectos.

Detectar `mcode`, `hermes` o `gentle-shell` demuestra que hay un comando disponible. Copiar el paquete demuestra instalación de archivos. Las pruebas anteriores añaden evidencia de catálogo y lectura para estas versiones; el comportamiento de un modelo siguiendo la skill requiere otra prueba y autorización para invocarlo.

## 7. Límites y recuperación

Comprobado en macOS con Node 26.7.0 y el Python 3.14.7 seleccionado por Hermes. Los valores de Windows proceden de lectura de código, no de una ejecución en Windows. Tampoco se probó una sesión interactiva completa, autenticación, elección automática de la skill por un modelo, consumo de tokens ni ahorro de costes. Context7 no pudo responder por cuota agotada; se recurrió a código instalado y fuentes oficiales públicas.

Después de actualizar un harness hay que volver a comprobar versión, directorio efectivo, catálogo y lectura. Cambiar el nombre de una carpeta o encontrarla en un registro auxiliar no sustituye esas comprobaciones. Esta auditoría no instala ni reactiva ningún proyecto y no contiene recibos, rutas personales ni hashes de proyectos privados.

## 8. Reproducción con instalaciones existentes

Sustituye los siete marcadores por rutas absolutas verificadas: biblioteca, paquetes instalados de MiniMax, Gentle Shell y Pi, código de Hermes, intérprete seleccionado por Hermes y ejecutable de Node. Los directorios de paquete contienen su `package.json`; el de Hermes contiene `hermes_constants.py`. No son directorios de autenticación. El ejemplo no descarga ni instala paquetes y rechaza versiones distintas de las probadas antes de importar los cargadores.

La carga directa evita los wrappers personales y la preparación de una sesión. En Hermes se lee la selección de dependencias existente y se añade al `sys.path`; no se activa su bootstrap, no se repara ni se cambia la selección. Los objetos mínimos de la prueba de Pi sustituyen exclusivamente al contenedor de la sesión; el método de expansión invocado es el instalado. Los hooks de red y subprocesos cubren las llamadas utilizadas por estos probes, no constituyen un aislamiento de sistema operativo.

```sh
python3 - '<BIBLIOTECA>' '<PAQUETE_MINIMAX>' '<PAQUETE_GENTLE>' '<PAQUETE_PI>' '<CODIGO_HERMES>' '<PYTHON_HERMES>' '<NODE>' <<'PY'
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile

biblioteca, minimax, gentle, pi, hermes, python_hermes, node = map(Path, sys.argv[1:])
for paquete, version in ((minimax, '0.6.5'), (gentle, '4.0.0'), (pi, '1.1.0')):
    assert json.loads((paquete / 'package.json').read_text())['version'] == version
assert json.loads((hermes / 'install-stamp.json').read_text())['baseVersion'] == '0.21.5'
origen = biblioteca / '_indice/skills/gamemaker-biblioteca'
archivos = [p.relative_to(origen) for p in origen.rglob('*') if p.is_file()]
prueba = Path(tempfile.mkdtemp(prefix='gm-harness-loaders-'))
for nombre in ('minimax', 'pi', 'hermes'):
    destino = prueba / nombre / 'skills/gamemaker-biblioteca'
    shutil.copytree(origen, destino)
    assert all((destino / p).read_bytes() == (origen / p).read_bytes() for p in archivos)
(prueba / 'proyecto/.git').mkdir(parents=True)
print('Archivos copiados por fixture:', len(archivos))

js = r'''
import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import {createRequire, syncBuiltinESMExports} from 'node:module';
const require = createRequire(import.meta.url);
require('node:net').Socket.prototype.connect = () => {throw new Error('Red bloqueada');};
globalThis.fetch = async () => {throw new Error('Red bloqueada');};
const procesos = require('node:child_process');
for (const nombre of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])
  procesos[nombre] = () => {throw new Error('Subprocesos bloqueados');};
syncBuiltinESMExports();
const [minimax, gentle, pi, prueba] = process.argv.slice(2);
const leer = ruta => readFileSync(ruta, 'utf8');
const original = leer(prueba+'/pi/skills/gamemaker-biblioteca/SKILL.md');
const moduloPi = await import(pathToFileURL(pi+'/dist/core/skills.js').href);
const catalogo = moduloPi.loadSkills({cwd:prueba+'/proyecto',agentDir:prueba+'/pi',skillPaths:[],includeDefaults:true});
const encontrada = catalogo.skills.find(s => s.name === 'gamemaker-biblioteca');
if (!encontrada || leer(encontrada.filePath) !== original || catalogo.diagnostics.length)
  throw new Error('Catálogo o lectura Pi incorrectos');
if (!moduloPi.formatSkillsForPrompt(catalogo.skills).includes('<name>gamemaker-biblioteca</name>'))
  throw new Error('Skill ausente del catálogo para el prompt');
const {AgentSession} = await import(pathToFileURL(pi+'/dist/core/agent-session.js').href);
const sesion = {resourceLoader:{getSkills:()=>catalogo},_extensionRunner:{emitError:()=>{throw new Error('Expansión fallida');}}};
const expansion = AgentSession.prototype._expandSkillCommand.call(sesion,'/skill:gamemaker-biblioteca prueba-aislada');
const cuerpo = original.replace(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/,'').trim();
if (!expansion.includes(cuerpo) || !expansion.endsWith('prueba-aislada'))
  throw new Error('Cuerpo o argumento Pi incompletos');
console.log('Pi: catálogo, prompt y expansión completos');
const launcher = await import(pathToFileURL(gentle+'/runtime/gentle-shell-launcher.mjs').href);
const vacios = {link:false,isolated:false,home:undefined};
const casos = [
  [vacios,{},undefined,'/fixture/.gentle-shell/agent'],
  [vacios,{GENTLE_SHELL_HOME:'/aislado'},undefined,'/aislado'],
  [{...vacios,link:true},{PI_CODING_AGENT_DIR:'/enlazado'},undefined,'/enlazado'],
  [{...vacios,home:'/explicito'},{},undefined,'/explicito'],
  [vacios,{GENTLE_SHELL_HOME:'/aislado'},{mode:'path',dir:'/persistido'},'/persistido']
];
for (const [args,env,config,esperado] of casos)
  if (launcher.resolveHome({args,env,config,homedir:'/fixture'}).dir !== esperado)
    throw new Error('Selección de home incorrecta');
const invocacion = launcher.buildPiInvocation({runtime:{command:'pi',args:[]},home:{dir:'/seleccionado'},baseEnv:{},homedir:'/fixture',packageRoot:'/paquete',passthrough:[],otherPackagePaths:[],takeOver:false,declaration:undefined});
if (invocacion.env.PI_CODING_AGENT_DIR !== '/seleccionado' || invocacion.env.GENTLE_PI_AGENT_HOME !== '/seleccionado')
  throw new Error('Home no propagado a Pi');
console.log('Gentle Shell: cinco selecciones y propagación del home correctas');
const moduloMiniMax = await import(pathToFileURL(minimax+'/chunks/chunk-2XPMNZVR.js').href);
const registro = await moduloMiniMax.Af([{id:'fixture',kind:'global',rootPath:prueba+'/minimax/skills'}]);
const skill = registro.getAvailableSkills().find(s => s.name === 'gamemaker-biblioteca');
if (!skill || registro.readByLocationUri(skill.locationUri) !== original || registro.getSnapshot().diagnostics.length)
  throw new Error('Catálogo o lectura MiniMax incorrectos');
console.log('MiniMax: catálogo y lectura completos');
'''
py = r'''
import sys
from pathlib import Path
import json
def auditoria(evento, args):
    if evento in ('subprocess.Popen', 'socket.connect'):
        raise RuntimeError('Red y subprocesos bloqueados')
sys.addaudithook(auditoria)
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
from pm.environments import selected_venv, site_packages
dependencias = site_packages(selected_venv(Path(sys.argv[1])))
assert dependencias.is_dir()
sys.path.insert(1, str(dependencias))
from tools.skills_tool import _find_all_skills, skill_view
assert any(s['name'] == 'gamemaker-biblioteca' for s in _find_all_skills())
carga = json.loads(skill_view('gamemaker-biblioteca', preprocess=False))
original = (Path(sys.argv[2]) / 'skills/gamemaker-biblioteca/SKILL.md').read_text(encoding='utf-8')
assert carga.get('success') and carga['content'] == original
print('Hermes: catálogo y lectura completos')
'''
(prueba / 'probar.mjs').write_text(js, encoding='utf-8')
(prueba / 'probar.py').write_text(py, encoding='utf-8')
entorno = {k:os.environ[k] for k in ('PATH','LANG','LC_ALL','TMPDIR') if k in os.environ}
entorno_node = {**entorno, 'MINIMAX_DATA_DIR':str(prueba/'minimax'),
                'PI_CODING_AGENT_DIR':str(prueba/'pi'),
                'DO_NOT_TRACK':'1', 'MCODE_DISABLE_TELEMETRY':'1'}
entorno_hermes = {**entorno, 'HERMES_HOME':str(prueba/'hermes'),
                  'HERMES_BUNDLED_SKILLS':str(prueba/'hermes/skills'),
                  'HERMES_OPTIONAL_SKILLS':str(prueba/'opcionales'),
                  'PYTHONDONTWRITEBYTECODE':'1'}
resultados = []
for comando, ambiente in (
    ([str(node),str(prueba/'probar.mjs'),str(minimax),str(gentle),str(pi),str(prueba)], entorno_node),
    ([str(python_hermes),'-I',str(prueba/'probar.py'),str(hermes),str(prueba/'hermes')], entorno_hermes)
):
    resultado = subprocess.run(comando, env=ambiente, cwd=prueba/'proyecto',
                               capture_output=True, text=True, timeout=45)
    print(resultado.stdout)
    print(resultado.stderr)
    print('Código de salida:', resultado.returncode)
    resultados.append(resultado.returncode)
raise SystemExit(0 if resultados == [0,0] else 1)
PY
```

Resultado esperado: los dos procesos salen con **0**, la skill aparece y su cuerpo coincide con el paquete copiado. En la instalación inspeccionada, Hermes emite además los avisos de sondas de plugins bloqueadas descritos antes. Un error, un timeout o una versión distinta no debe reinterpretarse como carga válida. Las fixtures quedan en el directorio temporal para inspección; el ejemplo no elimina datos ni modifica homes reales.

El bloque anterior se extrajo de este documento y se volvió a ejecutar tras la sincronización final de r47 el 2026-10-11: **entrada de 86 líneas, 12 archivos copiados por fixture y comparados byte a byte, ambos procesos con salida 0**, conservando los seis avisos de Hermes. Esta repetición cubre también el código de reproducción publicado; su resultado corresponde al paquete leído en esa pasada, no a futuros cambios del árbol.
