# R10 — Auditoría de portabilidad

**Fecha:** 2026-09-08
**Metodología:** lectura completa de los 20 scripts en alcance (`_indice/*.py`, `_indice/*.sh`,
`_indice/traduccion/*.py`, `_indice/reconstruccion/*.py`, `instalar.sh`, `reconstruir.sh`; ~7 400
líneas), grep sistemático de patrones de riesgo (rutas absolutas, comandos macOS, dependencias de
terceros, supuestos de red), y **verificación en vivo en esta máquina** de cada hallazgo antes y
después del arreglo — incluida una lectura del bundle real de `@gamemaker/gm-cli` 2.3.0
(`chunk-GBMHU7PM.js`) para replicar su lógica exacta de resolución de caché por sistema operativo,
en vez de adivinarla. Cierre con una ejecución completa de `./instalar.sh` (que a su vez ejecuta
`_indice/actualizar.py`) para confirmar que nada quedó roto.

No hay máquina Windows ni Linux disponible en esta sesión: **ningún arreglo de este informe está
verificado fuera de macOS**. Donde el código ahora se adapta al sistema operativo, lo hace
replicando lógica de fuentes primarias (el propio `gm-cli`, la documentación de Python) o
degradando con un aviso claro en vez de fallar en silencio o con un traceback — no por haberlo
probado en esas plataformas.

## Veredicto en una frase

Antes de esta auditoría, seguir el README en Windows tenía **varios puntos de fallo real**
—alguno con traceback crudo, otro con un cuelgue potencial de horas— y ninguno estaba documentado.
Después: los puntos de fallo conocidos están arreglados o degradan con un mensaje claro, y los que
no se pueden arreglar desde este repositorio (necesitas bash para los `.sh`, necesitas GameMaker
para lo que depende de `gm-cli`) están dichos explícitamente en el README. Sigue sin haber
confirmación real en Windows o Linux — ver la valoración honesta al final.

---

## Tabla: script → supuesto encontrado → arreglado o documentado

| Script | Supuesto encontrado | Categoría | Resultado |
|---|---|---|---|
| `_indice/buscar.py`, `_indice/construir-indices.py`, `_indice/validar-proyecto.py` | `RUNTIMES` apuntaba a fuego a `~/Library/Caches/GameMakerCLI/runtimes-gms2` (ruta de macOS) | Supuesto de SO | **Arreglado.** `_ruta_cache_gamemakercli()` detecta el SO y replica la lógica real de `gm-cli` (leída de su bundle JS): macOS → `~/Library/Caches`, Windows → `%LOCALAPPDATA%\GameMakerCLI\cache`, resto → `$XDG_CACHE_HOME` o `~/.cache`. Verificado que coincide con `gm-cli cache info` en esta Mac. |
| `_indice/buscar.py` | Las 4 llamadas a `grep` (para `--texto`/`--manual`/`--codigo`/`--todo` y el "¿es un prefijo del lenguaje?") no comprobaban que `grep` existe; una de las 4 ni siquiera atrapaba el `OSError` | Supuesto de herramienta instalada | **Arreglado.** `_grep_disponible()` comprueba con `shutil.which` y avisa una sola vez por ejecución, distinguiendo "no hay grep" de "sin resultados". La ficha de un símbolo conocido (`buscar.py <nombre>`, el caso del README) no depende de `grep` y sigue funcionando entera sin él — verificado con `PATH` restringido. |
| `_indice/validar-compilacion-docs.py` | `subprocess.run(["gm-cli", ...])` sin comprobar que existe — crash con traceback crudo, y solo **después** de extraer y clasificar ~3 700 bloques de código (segundos de trabajo tirados) | Supuesto de herramienta instalada | **Arreglado.** `shutil.which("gm-cli")` al principio de `main()`, antes de tocar nada: mensaje claro y salida en <1 s en vez de un traceback a mitad de proceso. Este script lo ejecuta `actualizar.py` en su paso 10 por defecto (no es opcional), así que el bug afectaba al flujo principal del README. |
| `_indice/validar-integracion.py` | `--compilar` (opcional, no se ejecuta por defecto) invocaba `gm-cli` sin comprobarlo | Supuesto de herramienta instalada | **Arreglado.** Mismo `shutil.which` antes de `capa_3()`. Prioridad baja: no forma parte del flujo por defecto. |
| `_indice/validar-compilacion.sh` | Igual que arriba, en bash: sin `gm-cli`, `gm-cli init` fallaba en silencio (stderr a `/dev/null`) y el mensaje genérico "no se pudo crear el proyecto" no decía la causa | Supuesto de herramienta instalada | **Arreglado.** `command -v gm-cli` al principio con mensaje explícito. Script manual, no está en el flujo del README ni de `actualizar.py`. |
| `_indice/reconstruccion/clonar_codigo.py` | `subprocess.run(["git", "clone", ...])` sin comprobar que `git` existe; y sin comprobar red antes de lanzar hasta 608 `git clone` con timeout de 300 s cada uno (en un cortafuegos que descarta paquetes en vez de rechazarlos, hasta ~50 h en el peor caso) | Supuesto de herramienta instalada + supuesto de red | **Arreglado.** Comprobación de `git` con `shutil.which`, y `hay_red()` contra `github.com` antes de clonar nada — mismo patrón que `validar-enlaces-externos.py` (ver más abajo). `--listar-excluidos` (no clona nada) se salta ambas comprobaciones. |
| `_indice/reconstruccion/descargar_manual.py` | Sin comprobación de red: sin conexión, el primer `sitemap()` revienta con un `urllib.error.URLError` sin atrapar, a mitad de "descargando el mapa del sitio…" | Supuesto de red | **Arreglado.** `hay_red()` contra `manual.gamemaker.io` antes de procesar cualquier idioma; un `HTTPError` cuenta como "hay red" (el servidor respondió). |
| `_indice/validar-enlaces-externos.py` | Ya comprobaba la red (auditoría r4-frescura), pero no comprobaba que `curl` existe: sin él, `hay_red()` devolvía silenciosamente "sin red" — mensaje engañoso (no es que no haya red, es que falta la herramienta) | Supuesto de herramienta instalada | **Arreglado.** Comprobación explícita de `curl` con `shutil.which`, mensaje distinto de "sin red". |
| Los 20 scripts `.py` del alcance | `sys.stdout`/`sys.stderr` sin forzar UTF-8: en Windows, en cuanto la salida no es una consola interactiva (pipes de `actualizar.py`, `> archivo`, MinTTY de Git Bash), Python usa la página de códigos ANSI del sistema — y los símbolos `✗ ⚠ → 🔴 🟡 …` que usa este código no caben ahí (`UnicodeEncodeError`) | Supuesto de SO / codificación | **Arreglado.** `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` (con `errors="replace"` de red de seguridad) al principio de cada script. Verificado que compilan y siguen funcionando igual en macOS (que ya usaba UTF-8, sin cambio de comportamiento aquí). **No verificado en Windows real.** |
| `instalar.sh`, `reconstruir.sh` | Asumían `python3` en el PATH. El instalador oficial de python.org para Windows registra `python.exe`, no `python3.exe` (solo la app de Microsoft Store trae ambos) | Supuesto de SO | **Arreglado.** `elegir_python()` prueba `python3` y, si falta, cae a `python` comprobando que sea Python 3 (por si un `python` residual fuera Python 2). Verificado con un `python3.exe` simulado ausente. |
| Repositorio (raíz) | Sin `.gitattributes`: un Windows con `core.autocrlf=true` (la opción que sugiere el propio instalador de Git for Windows) convertiría los LF de `instalar.sh`/`reconstruir.sh`/`validar-compilacion.sh` a CRLF al clonar — bash lee el CRLF como parte del shebang y falla con `bad interpreter: /bin/bash^M` | Supuesto de SO | **Arreglado.** `.gitattributes` con `* text=auto eol=lf` (más reglas explícitas para `.sh/.py/.gml/.md/.json` y `binary` para los PNG de `_indice/auditorias/`). Verificado que `git status` no renormaliza nada existente (todo el repo ya estaba en LF). |
| `_indice/sincronizar-skill.py` | Usa PyYAML (paquete de terceros, no viene con Python) para validar el frontmatter de `SKILL.md` | Supuesto de herramienta instalada | **Ya estaba bien manejado** (`try`/`except ImportError`, degrada a un extractor simple con aviso «⚠ Sin PyYAML…»). Solo se corrigió un comentario engañoso («PyYAML viene con el sistema en este entorno») que sugería una garantía que no existe — **confirmado en vivo en esta misma Mac**: el `python3` que resuelve un script no interactivo (`command -v python3` → `/opt/homebrew/bin/python3`) NO tiene PyYAML instalado; solo lo tiene el alias interactivo del shell (`python3.12`). El aviso se disparó de verdad durante la ejecución final de `./instalar.sh` de este informe, sin que nada se rompiera. |
| `_indice/traduccion/tm.py`, `_indice/traduccion/cola_traduccion.py` | Rutas absolutas del autor (`P = "/Users/adrianpereradelgado/..."`) — el motivo original de este encargo | Ruta absoluta | **Ya arreglado** en el commit `cd2b1e1` ("Prohibir el rectángulo, y quitar las rutas del autor de lo que viaja"), anterior a esta sesión. Verificado con `grep -r "/Users/" _indice/` (0 resultados) y con la fecha del commit en el log: sigue arreglado, no se ha reintroducido nada. |
| README.md | Sin ninguna nota sobre en qué se ha probado esto ni qué hace falta en Windows | Documentación | **Documentado.** Párrafo «Compatibilidad» añadido tras el bloque de instalación: dice explícitamente «desarrollado y probado a diario en macOS… no verificado fuera de macOS», qué hace falta en Windows (Git Bash o WSL para los `.sh`) y qué herramientas externas se asumen (`python3`/`python`, `git`, `grep`, `curl`). |

## Lo que ya estaba bien (comprobado, no tocado)

- **Codificación de lectura.** Los ~90 `open(...)` de los 20 scripts especifican `encoding="utf-8"`
  explícito, sin excepción (comprobado programáticamente, no a ojo: 0 llamadas sin `encoding=`).
  Esto evita el otro problema típico de Windows — decodificar los acentos del propio contenido con
  la codepage ANSI al leer — que es distinto del problema de escritura que sí hizo falta arreglar.
- **Separadores de ruta.** Ninguna ruta se construye partiendo cadenas por `"/"` escrito a mano;
  todo pasa por `os.path.join`/`os.sep`. Las claves de texto tipo `"13 - Diseño…/01 - archivo.md"`
  que usa `validar-integracion.py` para sus grupos de compilación conjunta se pasan tal cual a
  `os.path.join(RAIZ, rel)` — válido en Windows, que acepta `/` dentro de una ruta igual que `\`.
- **Nombres de archivo.** Los 365 archivos versionados no usan ninguno de los caracteres prohibidos
  en Windows (`< > : " | ? *`) — comprobado sobre los nombres reales vía `git ls-files -z`, no sobre
  la salida con comillas de `git ls-files` a secas, que da falsos positivos (envuelve en `"…"`
  cualquier nombre con bytes no-ASCII y el grep ingenuo confunde esas comillas con el carácter
  prohibido `"`).
- **Longitud de ruta.** La ruta relativa versionada más larga son 127 caracteres reales (no bytes
  UTF-8). Sumada a una ruta de clonado típica (~45-50 caracteres), se queda bien por debajo del
  límite clásico de 260 caracteres de Windows (`MAX_PATH`). Riesgo real solo si alguien clona muy
  anidado (varias carpetas de OneDrive/Nextcloud sincronizadas, por ejemplo) — no es nada que este
  repositorio pueda arreglar acortando títulos de documentos sin dañar su contenido.
- **`validar-enlaces-externos.py`** ya tenía su comprobación de red (`hay_red()`, auditoría
  r4-frescura) desde antes de este encargo; ha sido el patrón que se replicó en
  `clonar_codigo.py` y `descargar_manual.py`.
- **El motor de traducción** (`tm.py`, `celdas.py`, `etiquetas.py`, `cola_traduccion.py`,
  `anadir_celdas.py`, `anadir_tm.py`) es Python puro: sin comandos externos, sin dependencias de
  terceros, rutas derivadas de `__file__`.
- **`construir-indices.py`** ya distinguía correctamente "no hay runtime instalado, pero hay un
  `simbolos.json` previo que conservar" de "no hay ni lo uno ni lo otro: falla con un mensaje
  claro" — arreglado en la auditoría r9, sigue así.

## Verificación: nada se rompió

Cada arreglo se probó individualmente en esta máquina (con y sin la herramienta en cuestión en el
`PATH`, usando entornos restringidos: `env -i PATH=... python3 script.py`) y, al cerrar el informe,
se ejecutó `./instalar.sh` completo de principio a fin — que instala la skill en los 6 CLI de IA
detectados en esta máquina y ejecuta las 13 pasadas de `_indice/actualizar.py`:

```
[1m1. Enlaces internos[0m               → 2142 rutas correctas · 0 rotas · 1550 anclas · 0 rotas
[1m2. Índices y MAPA.json[0m             → 254 documentos, 3486 símbolos, runtime 2026.0.0.23
[1m4. Ortografía española[0m             → sin palabras sin tilde
[1m5. Cobertura de la API[0m             → 3213/3213 símbolos localizables (100 %)
[1m6. Nombres de archivo[0m              → todos bien escritos
[1m7. Descubrimiento[0m                  → las 49 tareas de ejemplo se resuelven
[1m9. Código GML[0m                     → 0 funciones inventadas
[1m10. Compilación real (gm-cli)[0m      → 3409/3409 bloques compilan, 25.9 s
[1m11. Integración entre documentos[0m   → sin duplicaciones graves
[1m12. Skill para agentes[0m             → índice y rutas al día
[1m13. Espejo del manual[0m              → 3119 páginas, 0 ausentes/incompletas

Biblioteca coherente. Índices al día y sin deuda pendiente.
```

`exit 0`. Ningún cambio de este informe rompió el flujo normal en esta máquina.

## Valoración honesta: ¿qué le pasaría hoy a alguien que clone esto en Windows o en Linux?

### Windows

Con Git Bash o WSL instalado (imprescindible: `instalar.sh` y `reconstruir.sh` son bash, no hay
forma de que `cmd.exe` o PowerShell los ejecuten directamente — esto ya estaba así y sigue estando
así; es una limitación real, no un bug, y ahora está dicha en el README):

- `git clone` funciona igual que en cualquier sistema — sin caracteres de archivo prohibidos, y con
  `.gitattributes` el checkout ya no puede llegar con CRLF a los `.sh`.
- `./instalar.sh` debería completar sus 5 pasos: registra la ruta, resuelve `python3` o `python`,
  instala la skill en los CLI de IA detectados, y lanza `actualizar.py`.
- Si GameMaker (y con él `gm-cli`) **todavía no está instalado**: el paso 2 de `actualizar.py`
  (`construir-indices.py`) lo dice con un mensaje claro y termina con `return 1` para ese paso
  concreto, pero `actualizar.py` sigue con el resto de pasos (no aborta salvo que fallen los
  enlaces internos, que no dependen de GameMaker) — el usuario ve qué instalar, no un traceback.
  Los pasos que sí necesitan `gm-cli` de verdad (10, y `--compilar` de 11) fallan igual de claro.
- Si GameMaker **sí está instalado**: `RUNTIMES` ahora apunta a
  `%LOCALAPPDATA%\GameMakerCLI\cache\runtimes-gms2`, replicando la lógica real que usa el propio
  `gm-cli` (leída de su código, no adivinada) — con confianza alta, pero sin confirmación real en
  Windows.
- Los símbolos `✗/⚠/→/…` deberían verse bien tanto en la consola nativa (Python ya los maneja bien
  ahí desde la PEP 528) como en MinTTY/Git Bash y en cualquier redirección, gracias al
  `reconfigure(encoding="utf-8")` añadido a los 20 scripts.

Lo que sigue sin poder afirmarse sin una máquina Windows real: si `command -v python3`/`python`
resuelve como se espera en todas las variantes de Git Bash y WSL, si algún antivirus interfiere con
`git clone --depth 1` de 608 repositorios, y el caso límite de rutas muy anidadas (`MAX_PATH`)
mencionado arriba. **Veredicto: probablemente funciona hoy, con matices no verificados —
sensiblemente mejor que antes de este informe, no una garantía.**

### Linux

Bash es nativo, `python3` casi siempre está en el PATH de fábrica (o es un `apt install python3`
de un comando), y `grep`/`curl`/`git` vienen preinstalados o son triviales de instalar en cualquier
distribución mayor. El locale UTF-8 es el valor por defecto en la inmensa mayoría de distribuciones
modernas, así que el problema de codificación que sí afecta a Windows no debería aparecer aquí en
absoluto. La incógnita real no está en estos scripts, sino en `gm-cli`/GameMaker Studio 2 mismo:
esta auditoría no ha comprobado si el propio motor tiene una vía de instalación oficial y estable en
Linux — es una pregunta sobre el ecosistema de YoYo Games, no sobre este repositorio, y queda fuera
de lo que estos scripts pueden arreglar o garantizar. Con `gm-cli` instalado, `RUNTIMES` cae en la
rama `$XDG_CACHE_HOME`/`~/.cache/GameMakerCLI`, la misma que usa `gm-cli` de verdad. **Veredicto:
alta confianza de que funciona, con la misma salvedad de "no verificado en la práctica" que el
resto de este informe, y con GameMaker/gm-cli en Linux como la única pieza realmente fuera del
control de este repositorio.**

## Alcance no cubierto a propósito

Por instrucción explícita del encargo, no se ha tocado nada de `11 - Código descargado/*/`
(extensiones oficiales de YoYo Games con sus propios `.sh` de build para Linux/macOS —
`GMEXT-AppleIAP`, `GMEXT-CrazyGames`, `GMEXT-Discord`, `GMEXT-EpicOnlineServices`…): son scripts de
terceros, versionados solo como catálogo de referencia, no forman parte de la herramienta de esta
biblioteca y no los mantiene este repositorio.
