# R10 (continuación) — Verificación en Linux real

**Fecha:** 2026-09-08
**Metodología:** máquina virtual Linux efímera y aislada (`lima`, no la instancia `regression-dxvk`
del usuario), levantada, usada y destruida en esta sesión. Dentro de ella: instalación mínima de
herramientas, `git clone` real desde `https://github.com/SwonDev/gamemaker-biblioteca.git`, y
ejecución literal de cada comando que documenta el README — sin GameMaker instalado, que es el
caso real de cualquiera que clone esto por primera vez en Linux. Cuando algo falló, el arreglo se
hizo en el repositorio anfitrión (este Mac) y se volvió a probar en la VM antes de darlo por
bueno. Cierre con `python3 _indice/actualizar.py` en el Mac (con GameMaker instalado) para
confirmar que nada se rompió.

Este informe **continúa** `r10-portabilidad.md`, que arregló nueve supuestos de sistema operativo
pero terminó diciendo, honestamente, que nada estaba verificado en una máquina real fuera de
macOS. Esta sesión cierra esa verificación para Linux — no para Windows, que sigue sin máquina
disponible.

## Veredicto en una frase

La auditoría anterior acertó en todo lo que revisó (rutas de caché, símbolos Unicode, avisos de
herramienta ausente, finales de línea): **confirmado en vivo, sin excepciones**. Pero había dos
fallos reales que esa auditoría no vio porque nunca se ejecutó el flujo completo con un intérprete
Python distinto al de este Mac ni con `simbolos.json` realmente ausente de principio a fin: un
`SyntaxError` de sintaxis-solo-3.12 que rompía un script entero en cualquier Python 3.11 o
anterior (Debian 12 estable incluido), y una cascada de `Traceback` sin capturar —incluida una que
mataba `actualizar.py` entero, abortando 8 de sus 13 pasos— en cuanto `simbolos.json` no existía
todavía. **Los dos están arreglados y reverificados de punta a punta en la misma VM.**

---

## Entorno de prueba

```
$ limactl start --name=gmbib-linux --plain template://debian-12 --tty=false
[…]
READY. Run `ssh -F …/gmbib-linux/ssh.config` lima-gmbib-linux` to open the shell.
```

VM efímera Debian 12 (bookworm), arm64, arrancada en ~25 s desde la plantilla oficial de Lima.
`--plain`: sin montajes automáticos del Mac, sin nada compartido — todo lo que hay dentro se
clonó de verdad desde GitHub, nada se copió del host salvo los tres archivos ya corregidos para
la prueba de reverificación final (ver más abajo, están claramente marcados).

```
$ cat /etc/os-release | head -2
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
$ python3 --version
Python 3.11.2
$ echo $LANG
C.UTF-8
$ which bash python3 curl grep sed
/usr/bin/bash /usr/bin/python3 /usr/bin/curl /usr/bin/grep /usr/bin/sed
$ git --version
bash: git: command not found        ← no viene en la imagen cloud mínima
```

`git` no está en la imagen base (esperado: es una imagen «cloud», no un escritorio). Se instaló
con `sudo apt-get install -y git` — es exactamente lo que haría cualquiera siguiendo «instala lo
mínimo» del encargo, y es lo único que hizo falta instalar además de lo que ya trae Debian.

**Importante para lo que sigue: `python3` en esta VM es la 3.11.2, la versión de sistema de Debian
12 estable (soportada hasta 2028). En el Mac de este proyecto, `python3` resuelve a la 3.12.14 (por
alias interactivo) o a la 3.14.7 (symlink de Homebrew, la que usan los scripts no interactivos) —
nunca por debajo de 3.12. Esa diferencia de versión, no de sistema operativo, es la causa del
primer hallazgo.**

---

## Hallazgo 1 (nuevo, no visto en r10): `SyntaxError` en cualquier Python < 3.12

`_indice/validar-codigo-gml.py` no compilaba en absoluto en esta VM:

```
$ python3 -m py_compile _indice/validar-codigo-gml.py
  File "_indice/validar-codigo-gml.py", line 376
    f"extensiones/librerías: {len(externas) if corpus_instalado else "sin instalar"}")
                                                                      ^^^
SyntaxError: f-string: expecting '}'
```

La causa: comillas dobles anidadas dentro de un f-string delimitado también con comillas dobles
(`f"... {expr if cond else "texto"}"`). Esa sintaxis solo es válida desde **Python 3.12** (PEP 701,
que relaja la gramática de f-strings). Con Python 3.11 o anterior es un error de sintaxis, no de
tipo ni de runtime: el archivo ni siquiera se parsea.

Por qué no se vio en `r10-portabilidad.md` ni en ninguna sesión anterior: el `python3` de este Mac
nunca resuelve a nada por debajo de 3.12 (alias `python3.12` en el shell interactivo, symlink a
`python3.14` de Homebrew en cualquier proceso no interactivo). El bug era invisible en la única
máquina donde se había probado. Python 3.11 sigue siendo el `python3` de fábrica de Debian 12
(soporte hasta 2028) y de otras distribuciones activas — no es una versión exótica.

**Barrido completo:** se compilaron con `py_compile`, uno a uno, los 20 scripts del alcance de
`r10-portabilidad.md` (`_indice/*.py`, `_indice/traduccion/*.py`, `_indice/reconstruccion/*.py`)
con el Python 3.11.2 de esta VM. Solo falló ese archivo:

```
$ for f in $(find _indice -name "*.py"); do python3 -m py_compile "$f" 2>&1 | grep -q . && echo "FALLA: $f"; done
FALLA: _indice/validar-codigo-gml.py
```

**Arreglo** (`_indice/validar-codigo-gml.py:376`): comillas simples para el literal anidado en vez
de comillas dobles repetidas — válido desde Python 3.6, sin cambio de comportamiento:

```diff
-          f"extensiones/librerías: {len(externas) if corpus_instalado else "sin instalar"}")
+          f"extensiones/librerías: {len(externas) if corpus_instalado else 'sin instalar'}")
```

Reverificado con `py_compile` en la propia VM (Python 3.11.2): compila limpio.

**Alcance del daño real, antes del arreglo:** este archivo no es un script suelto. Tres cosas lo
usan:
- Se ejecuta solo (`python3 _indice/validar-codigo-gml.py`) → `SyntaxError` crudo.
- Lo importa `_indice/validar-proyecto.py` como módulo (para reutilizar sus regex y funciones) →
  el `SyntaxError` se propaga y **`validar-proyecto.py` tampoco arrancaba**, aunque su propio
  código no tuviera ningún problema. `validar-proyecto.py` es uno de los tres comandos que el
  README pone como ejemplo destacado (`python3 _indice/validar-proyecto.py ~/MiJuego`).
- Lo invoca `_indice/actualizar.py` en su paso 9 (vía `subprocess`) → con `capture_output=True`,
  el traceback iba a `stderr` capturado y **`actualizar.py` no lo imprime en ningún sitio** (solo
  reenvía líneas de `stdout` que empiezan por ciertos patrones): el paso 9 fallaba en silencio,
  con un mensaje de «problemas» que ni siquiera apuntaba a la causa real (ver Hallazgo 2).

## Hallazgo 2 (nuevo, no visto en r10): tracebacks al derivarse `simbolos.json` sin runtime

Sin GameMaker instalado —el estado normal y esperado de un clon en Linux, documentado desde
`r10-portabilidad.md`—, `_indice/simbolos.json` nunca se genera. `construir-indices.py` (paso 2 de
`actualizar.py`) ya lo detecta y falla con un mensaje ejemplar:

```
[1m2. Índices y MAPA.json[0m
✗ No hay ningún runtime de GameMaker instalado en esta máquina, y
  _indice/simbolos.json no existe todavía: no hay nada
  que conservar de una ejecución anterior.
  […]
```

El problema es que **cuatro sitios más** abren ese mismo archivo sin comprobar antes que existe, y
tres de ellos no se descubrieron en `r10-portabilidad.md` porque esa auditoría nunca llegó a
ejecutar el flujo completo con el archivo realmente ausente de principio a fin (se centró en
supuestos de SO, no en este encadenamiento). El primero es el más grave con diferencia:

```
[1m5. Cobertura de la API[0m
Traceback (most recent call last):
  File ".../actualizar.py", line 457, in <module>
    sys.exit(main())
  File ".../actualizar.py", line 358, in main
    vigentes, invisibles = revisar_cobertura()
  File ".../actualizar.py", line 169, in revisar_cobertura
    simb = json.load(open(os.path.join(IND, "simbolos.json"), encoding="utf-8"))["simbolos"]
FileNotFoundError: [Errno 2] No such file or directory: '.../_indice/simbolos.json'
```

`revisar_cobertura()` se llama **directamente dentro del propio proceso** de `actualizar.py`, no
por `subprocess`: el `FileNotFoundError` sin capturar mata el intérprete entero. El docstring del
propio script promete «parando al primer fallo real» (es decir: sigue adelante con lo que no sea
un fallo real, como ya hace con el paso 2) — pero esto abortaba **los pasos 6 a 13 completos**, sin
que ninguno de ellos llegara a ejecutarse. Es la regresión más seria de las dos: no es un mensaje
feo, es que la herramienta deja de hacer la mitad de su trabajo sin decirlo.

Los otros tres sitios, mismo patrón, confirmados uno a uno con el script corregido del Hallazgo 1
ya en su sitio:

```
$ python3 _indice/validar-codigo-gml.py
Traceback (most recent call last):
  […] File ".../validar-codigo-gml.py", line 77, in cargar_simbolos
    d = json.load(open(os.path.join(IND, "simbolos.json"), encoding="utf-8"))
FileNotFoundError: […] '_indice/simbolos.json'

$ python3 _indice/validar-proyecto.py .
⚠ En […] no hay ningún .yyp: se analizan igualmente los .gml que haya.
Traceback (most recent call last):
  […] File ".../validar-proyecto.py", line 72, in cargar_simbolos
    d = json.load(open(os.path.join(IND, "simbolos.json"), encoding="utf-8"))
FileNotFoundError: […] '_indice/simbolos.json'
```

`revisar_cobertura_familias()` (paso 8 de `actualizar.py`, línea 239) tiene el mismo bug sin
guardia — no llegó a manifestarse en la prueba porque el paso 5 ya había matado el proceso antes,
pero el código es idéntico y se arregló igual.

**Arreglo, con el mismo criterio que ya usa `buscar.py::cargar()`** (mensaje claro + salida
limpia, sin traceback, en vez de dejar que la excepción suba):

- `_indice/validar-codigo-gml.py::cargar_simbolos()` y `_indice/validar-proyecto.py::cargar_simbolos()`:
  comprueban `os.path.exists()` antes de abrir; si falta, imprimen el mismo mensaje de tres líneas
  que ya usa `buscar.py` («✗ No existe _indice/simbolos.json todavía…») y `sys.exit(1)`.
- `_indice/actualizar.py::revisar_cobertura()` y `::revisar_cobertura_familias()`: devuelven un
  centinela (`(None, None)` y `None` respectivamente — no una lista vacía, que significaría «cero
  huérfanas», un resultado real y distinto) cuando el archivo no existe.
- Los pasos 5 y 8 de `main()` comprueban ese centinela y **saltan la comprobación con un aviso**
  (`⚠ sin _indice/simbolos.json (no hay runtime instalado, ver el paso 2 de arriba): no se puede
  calcular…`) en vez de operar sobre `None`.
- Los pasos 2 y 9 de `main()` distinguían mal la causa de un fallo: el paso 2 decía siempre
  «MAPA.json tiene entradas que hay que describir a mano» aunque la razón real fuera «no hay
  runtime»; el paso 9 decía siempre «hay código que llama a funciones del runtime que no existen»
  aunque la razón real fuera la misma. Los dos ahora comprueban `os.path.exists(simbolos.json)`
  —una señal robusta, no analizan el texto que imprimió el subproceso— para dar el mensaje que de
  verdad describe lo que pasó.

## Reverificación de punta a punta: clon real + `instalar.sh`, con los tres archivos corregidos

Clon nuevo desde GitHub (no una copia del host) dentro de la misma VM, con los tres archivos ya
parcheados aplicados encima, ejecutando exactamente el primer bloque de comandos del README:

```
$ git clone -q https://github.com/SwonDev/gamemaker-biblioteca.git ~/repo-final
$ cd ~/repo-final && git log --oneline -1
c675dff Todo se construyó en un Mac, y el repositorio es para cualquiera
$ ./instalar.sh
```

Salida completa (recortada donde se repite el patrón, íntegra en lo que importa):

```
✓ Ruta registrada: /home/…/repo-final
✓ Genérico ~/.agents — […]: instalada en /home/…/.agents/skills/gamemaker-biblioteca

CLI no detectados en esta máquina (se han saltado, sin tocar nada suyo):
  · Claude Code (no encuentro «claude» en el PATH)
  […7 más, todas con el mismo formato…]

→ Regenerando los índices contra el runtime instalado…

1. Enlaces internos          → 1903 rutas correctas · 0 rotas · 1549 anclas correctas · 0 rotas
2. Índices y MAPA.json        → ✗ No hay ningún runtime de GameMaker instalado… (mensaje limpio)
3. Coherencia MAPA.json/disco → 267 entradas, todas existen en el disco.
4. Ortografía española        → Sin palabras españolas escritas sin tilde.
5. Cobertura de la API        → ⚠ sin _indice/simbolos.json (…): no se puede calcular la cobertura.
6. Nombres de archivo          → Todos los nombres de archivo están bien escritos.
7. Prueba de descubrimiento    → 10 de 49 tareas sin resolver. (contenido, no portabilidad — ver nota)
8. Cobertura por familias      → ⚠ sin _indice/simbolos.json (…): no se puede calcular.
9. Código GML                  → ✗ No existe _indice/simbolos.json todavía.
10. Compilación real (gm-cli)  → ✗ No encuentro el comando «gm-cli» en el PATH.
11. Integración entre docs     → ✓ Sin duplicaciones graves. 🟠 4 MEDIAS (contenido real, no bug).
12. Skill para agentes         → índice regenerado; rutas de los 9 CLI no instalados avisadas, claro.
13. Espejo español del manual  → 0 páginas comparadas · 0 ausentes · 0 incompletas (carpeta opcional).

Queda trabajo:
  · no hay _indice/simbolos.json: instala GameMaker/gm-cli y repite (ver el mensaje del paso 2)
  · hay tareas de ejemplo que la biblioteca no resuelve
  · no se pudo comprobar el código GML: falta _indice/simbolos.json (sin runtime instalado, paso 2)
  · hay bloques ```gml de la documentación que no compilan (…)
⚠ Revisa la salida de actualizar.py

Listo. Comprueba que responde:
  python3 "/home/…/repo-final/_indice/buscar.py" draw_sprite_ext
```

**Cero tracebacks en las 13 pasadas.** Cada fallo trae su causa y, cuando aplica, el comando
exacto para resolverla. `actualizar.py` sale con código 1 (correcto: hay trabajo pendiente — sin
GameMaker/gm-cli no puede haber otra cosa), pero **completa los 13 pasos**, no los 4 primeros.

Comprobación final que el propio instalador sugiere:

```
$ python3 "_indice/buscar.py" draw_sprite_ext
✗ No existe _indice/simbolos.json todavía.
  Se genera (desde el GmlSpec.xml de tu runtime instalado) con:
      python3 _indice/actualizar.py
$ echo $?
1
```

Exactamente lo que pedía el encargo: **falla con un mensaje claro y accionable, no con un
traceback.**

## Lo que la auditoría anterior arregló «a ciegas»: confirmado en Linux real, uno por uno

| Pregunta del encargo | Verificación en esta VM | Resultado |
|---|---|---|
| ¿La ruta del runtime detecta Linux y busca donde debe? | `platform.system()` → `"Linux"`; ruta calculada → `~/.cache/GameMakerCLI/runtimes-gms2` sin `XDG_CACHE_HOME`, y `/tmp/xdgcache/GameMakerCLI/runtimes-gms2` con `XDG_CACHE_HOME=/tmp/xdgcache` fijado | **Confirmado.** Coincide exactamente con la lógica que describe `r10-portabilidad.md`, y con el estándar XDG real |
| ¿Los símbolos `✗ ⚠ →` se imprimen bien, también canalizados? | `python3 _indice/actualizar.py \| cat` y `> archivo.txt`: los tres símbolos aparecen intactos, el archivo decodifica como UTF-8 válido (`python3 -c 'open(...).read()'`, 0 errores) | **Confirmado.** Además: ni siquiera hizo falta el `reconfigure()` — Debian con Python 3.11 ya fuerza UTF-8 al canalizar incluso bajo `LANG=C LC_ALL=C` forzado a propósito (PEP 538/540 del propio Python, activo en Linux desde 3.7). El `reconfigure()` es inofensivo aquí (no cambia nada) y sigue siendo necesario para Windows, que es donde de verdad hace falta |
| ¿Los `.sh` arrancan (shebang correcto, sin CRLF)? | `file instalar.sh reconstruir.sh` → `ASCII/UTF-8 text executable`; `grep -c $'\r'` → 0 en los tres `.sh` del repo; `od -c` del primer byte → `#!/usr/bin/env bash\n` limpio; `./instalar.sh` ejecuta sin `bad interpreter` | **Confirmado.** `.gitattributes` (de `r10-portabilidad.md`) cumple su función también en un `git clone` real desde GitHub, no solo en el repo local |
| ¿Los avisos de herramienta ausente salen claros? | `grep` ausente (`buscar.py --texto`), `curl` ausente (`validar-enlaces-externos.py`), `git` ausente (`clonar_codigo.py`), `gm-cli` ausente (`validar-compilacion-docs.py`, paso 10) — los cuatro, con `PATH` restringido de verdad | **Confirmado, los cuatro.** Mensaje de una frase, sin traceback, diciendo qué falta y en qué se distingue de «sin red» donde aplica |
| ¿`instalar.sh` se comporta razonablemente sin ningún CLI de IA? | Los 9 CLI (`claude`, `codex`, `opencode`, `qwen`, `kimi`, `gemini`, `copilot`, `cursor-agent`, `cline`) ausentes de verdad en esta VM | **Confirmado.** Instala solo en `~/.agents/skills` (el directorio genérico que no depende de tener ningún CLI concreto), lista los 9 saltados con el motivo exacto, no toca nada de otro programa, y sigue con el resto del script |
| ¿`reconstruir.sh` funciona en Linux, con red real? | `./reconstruir.sh codigo --limite 1 --destino /tmp/prueba-clonar` (con `git` ya instalado): comprobó conectividad contra `github.com`, clonó `1PassBlur` de verdad, reportó `✓ Clonados ahora: 1` | **Confirmado**, extremo a extremo, con red real, no simulada |

Ninguno de los nueve arreglos de `r10-portabilidad.md` falló en Linux real. Los dos hallazgos de
esta sesión son **nuevos**, no regresiones de esos nueve.

## Nota sobre el paso 7 (49 tareas de ejemplo, 10 sin resolver)

No es un bug de portabilidad: son las mismas 10 tareas sin resolver que ya darían en macOS con
`simbolos.json`/`09 - Manual oficial`/`11 - Código descargado` sin instalar (varias apuntan a
páginas del manual o del corpus, ambos ausentes por diseño en un clon recién hecho). Es contenido
pendiente de la biblioteca, no algo que dependa de Linux — se deja fuera del alcance de este
informe a propósito, igual que las 4 duplicaciones MEDIAS del paso 11 (ver `PENDIENTE-r3.md` si
procede tocarlas).

## Verificación: nada se rompió en el Mac

Con los tres archivos corregidos, `python3 _indice/actualizar.py` en este Mac (con GameMaker LTS
2026 instalado, como siempre) — la comprobación que pedía explícitamente el encargo antes de dar
esto por cerrado:

```
9. Código GML                    → 106 funciones propias · 0 INVENTADAS
10. Compilación real (gm-cli)    → 3409/3409 bloques compilan, 25.5s
13. Espejo español del manual    → 3119 páginas comparadas · 0 ausentes/incompletas

Biblioteca coherente. Índices al día y sin deuda pendiente.
$ echo $?
0
```

`git status --short` tras la ejecución: solo los tres archivos tocados por este informe
(`_indice/actualizar.py`, `_indice/validar-codigo-gml.py`, `_indice/validar-proyecto.py`) —
`simbolos.json`/`documentos.json` están en `.gitignore`, no aparecen. Ningún efecto colateral.

## Veredicto final: ¿qué le pasa hoy, de verdad, a alguien que clone esto en Linux?

**Antes de esta sesión:** dependiendo de qué versión de Python trajera su distribución, podía no
llegar ni a la primera ejecución de `_indice/validar-codigo-gml.py` (`SyntaxError` con cualquier
Python 3.11 o anterior — Debian 12 estable, entre otras, todavía soportada hasta 2028). Y aunque
tuviera Python 3.12+, el primer `python3 _indice/actualizar.py` sin GameMaker instalado —el caso
normal en Linux, donde `gm-cli`/GameMaker no tiene vía de instalación oficial confirmada—
terminaba con un `Traceback` de Python a los pocos segundos, en el paso 5 de 13, sin completar el
resto ni decir con claridad que la causa real era «no hay runtime, instala GameMaker».

**Después de esta sesión, verificado con un `git clone` real desde GitHub en una Debian 12 limpia,
con Python 3.11.2, sin GameMaker instalado:** los 20 scripts del alcance compilan; `./instalar.sh`
completa sus 13 pasadas sin ningún traceback; cada fallo esperable (sin runtime, sin `gm-cli`, sin
CLI de IA instalado) da un mensaje de una o dos líneas que dice qué falta y, cuando aplica, el
comando exacto para resolverlo; `reconstruir.sh codigo` clona de verdad contra GitHub. Lo único que
sigue faltando —y no es arreglable desde este repositorio— es GameMaker Studio 2 / `gm-cli` mismos:
sin ellos, `simbolos.json` no puede derivarse por primera vez en ninguna plataforma, Linux
incluido, y eso ya estaba dicho con claridad tanto en el README como en el propio mensaje del
paso 2. **Linux, con esta corrección aplicada, sigue el mismo comportamiento honesto por diseño
que ya tenía macOS: sin GameMaker, la biblioteca en español funciona entera y solo lo que depende
del runtime lo dice explícitamente en vez de fingir que funciona o reventar.**

Windows sigue sin verificación en máquina real — fuera del alcance de este informe, que era
específicamente Linux.

## Limpieza

VM efímera detenida y borrada al cerrar esta sesión (`limactl stop gmbib-linux && limactl delete
gmbib-linux`), confirmado con `limactl list`. No se tocó en ningún momento la instancia
`regression-dxvk` del usuario.
