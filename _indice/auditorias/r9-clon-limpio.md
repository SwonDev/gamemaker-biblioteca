# R9 — Auditoría del clon limpio

**Fecha:** 2026-09-08
**Metodología:** `git clone https://github.com/SwonDev/gamemaker-biblioteca.git` de verdad, en
`~/gm_clon_limpio`, en una máquina que tiene GameMaker LTS 2026 instalado y **nada más** de este
proyecto (sin `09 - Manual oficial/`, sin `11 - Código descargado/` con contenido, sin
`_indice/simbolos.json` previo). A partir de ahí, trabajo exclusivamente dentro del clon,
siguiendo el README como lo seguiría alguien que llega nuevo, con la salida real de cada comando.
La copia original (`~/Documents/GameMaker_Aprendizaje`) no se tocó salvo un efecto colateral
documentado y revertido en la sección final.

## Veredicto en una frase

**No.** Un desarrollador que clone hoy este repositorio y siga el README al pie de la letra —
`git clone` → `cd` → `./instalar.sh` → `python3 _indice/buscar.py draw_sprite_ext` — obtiene un
`Traceback` de Python sin gestionar, no una ficha de función. La promesa central del proyecto
("los símbolos salen del `GmlSpec.xml` de tu runtime, `./instalar.sh` los genera") es **falsa** en
un clon limpio: existe un bug real, reproducible y no documentado que impide generar
`_indice/simbolos.json` la primera vez, sin importar que GameMaker esté instalado. El propio
`PUBLICAR.md` del repositorio afirma explícitamente que esto funciona, y no es cierto.

Dicho esto, **no es un despropósito ni un timo**: el diagnóstico exacto del fallo es trivial de dar
(un `try/except` de tres líneas lo arregla), el resto de la maquinaria (`reconstruir.sh`,
`validar-compilacion-docs.py`, la instalación de la skill en los CLIs) funciona exactamente como
se documenta, y una vez se sortea el bug a mano, `buscar.py` y `validar-proyecto.py` cumplen lo
que prometen — incluido detectar `instance_create()`, el ejemplo exacto de función inventada que
usa el propio README en su primer párrafo.

---

## 1. Clonado y primer vistazo

```sh
$ git clone https://github.com/SwonDev/gamemaker-biblioteca.git ~/gm_clon_limpio
Cloning into '/Users/adrianpereradelgado/gm_clon_limpio'...
$ du -sh ~/gm_clon_limpio
 22M
$ find ~/gm_clon_limpio -type f | wc -l
     389
```

22 MB, 389 archivos. Coincide con lo que promete `PUBLICAR.md` ("Total publicable: 363 archivos ·
14 MB más los dos ficheros de catálogo" — la diferencia son `.git/`, `LICENSE`, `PUBLICAR.md`,
`RUTA.md` y el propio `.gitignore`, que no cuentan como "publicable" en esa tabla pero sí están en
el repo). El `.gitignore` excluye exactamente lo que el README dice que excluye: `09 - Manual
oficial/`, `11 - Código descargado/*` (con `_RUTAS.json` y `_CATALOGO.md` publicados aparte),
`Lumbre/` y `GameMaker_Fuentes/`. Nada roto aquí: la promesa de "qué NO incluye, y por qué" se
cumple al 100 %.

## 2. Hallazgo crítico — `simbolos.json` no se puede generar en un clon limpio

### 2.1 Lo que dice el README

> «Eso instala la skill (...) **y genera los índices contra tu GameMaker**.»

Y en `PUBLICAR.md` (líneas 20-24), con estas palabras exactas:

> «## Lo que le pasa a quien clone el repositorio
>
> Al ejecutar `./instalar.sh`, `actualizar.py` deriva `simbolos.json` del `GmlSpec.xml` **del
> runtime que esa persona tenga instalado**. Eso no es un apaño: es lo que garantiza que la
> biblioteca no le mienta sobre una versión que no es la suya.»

### 2.2 Lo que pasa de verdad

Justo tras clonar, siguiendo el segundo bloque de comandos del README:

```
$ python3 _indice/buscar.py draw_sprite_ext
Traceback (most recent call last):
  File ".../_indice/buscar.py", line 331, in <module>
    sys.exit(ficha(a))
  File ".../_indice/buscar.py", line 96, in ficha
    d = cargar()
  File ".../_indice/buscar.py", line 52, in cargar
    with open(os.path.join(IDX, "simbolos.json"), encoding="utf-8") as f:
FileNotFoundError: [Errno 2] No such file or directory: '.../_indice/simbolos.json'
```

Un `Traceback` en crudo, no un mensaje en español como el resto del proyecto cuida tanto (compárese
con `validar-proyecto.py`, que si le das una ruta que no existe dice limpiamente «No existe la
carpeta: ...»). Es la primerísima impresión que se lleva un recién llegado.

Siguiendo el README con más paciencia: se ejecuta `./instalar.sh`, que en su paso final llama a
`actualizar.py` para «regenerar los índices contra el runtime instalado». La salida real:

```
→ Regenerando los índices contra el runtime instalado…

1. Enlaces internos
1905 rutas correctas · 239 rotas
  ✗ README.md
      → ./09 - Manual oficial/README.md
  ✗ AGENTS.md
      → ./_indice/simbolos.json
  [... 237 líneas más, todas hacia «09 - Manual oficial/…» o «11 - Código descargado/…» ...]
1549 anclas correctas · 0 rotas
→ hay enlaces rotos: corrígelos antes de seguir.
⚠ Revisa la salida de actualizar.py

Listo. Comprueba que responde:
  python3 ".../_indice/buscar.py" draw_sprite_ext
```

`actualizar.py` **aborta en el paso 1 de 13** (`_indice/actualizar.py:275-278`: `return 1`
inmediatamente si `verificar-enlaces.py` falla) y **nunca llega al paso 2**, que es
`construir-indices.py` — el único script que escribe `_indice/simbolos.json`
(`_indice/actualizar.py:280-281`). Es decir: `./instalar.sh` no genera los índices que promete, ni
en el README ni en `PUBLICAR.md`.

Y por si el aborto en el paso 1 pasara desapercibido entre el ruido de 239 líneas de enlaces rotos:
`instalar.sh:145` hace `python3 actualizar.py || echo "⚠ Revisa la salida de actualizar.py"` y a
continuación, **sin condicionar nada al resultado**, `instalar.sh:153` imprime igualmente «Listo.
Comprueba que responde: `python3 .../buscar.py draw_sprite_ext`» — la instrucción exacta que, tal
cual, devuelve el `Traceback` de arriba. El script dice «Listo» inmediatamente después de avisar
de que algo falló.

### 2.3 Por qué falla — causa raíz confirmada, no una hipótesis

Confirmé que el bloqueo de `actualizar.py` en el paso 1 (239/238 enlaces "rotos", ver §4: el 100 %
apunta a `09 - Manual oficial/` y `11 - Código descargado/`, exactamente lo que el `.gitignore`
excluye a propósito) **no es la única causa**. Hay un segundo bug, independiente, en
`_indice/construir-indices.py`. Ejecutándolo directamente (saltándome `actualizar.py`):

```
$ python3 _indice/construir-indices.py
Traceback (most recent call last):
  File ".../_indice/construir-indices.py", line 473, in <module>
    sys.exit(main())
  File ".../_indice/construir-indices.py", line 407, in main
    previo = json.load(open(os.path.join(IND, "simbolos.json"), encoding="utf-8"))
FileNotFoundError: [Errno 2] No such file or directory: '.../_indice/simbolos.json'
```

`_indice/construir-indices.py:407` abre `simbolos.json` **sin comprobar que existe y sin
`try/except`**, para leer un `previo` del que reutiliza `previo["meta"]` (línea 425) y
`previo["simbolos"].get(nom, {}).get("ejemplos_en_codigo")` (línea 418-420) — datos que en la
copia de trabajo del autor ya existen porque `simbolos.json` lleva generándose y actualizándose
desde hace meses. **En el mundo real donde ese fichero nunca ha existido, no hay ningún camino en
todo el repositorio que lo cree desde cero.** Es un bug de arranque en frío: el script solo sabe
*actualizar* un índice, nunca *crearlo* la primera vez.

Comprobé que es exactamente eso y no otra cosa, sembrando manualmente el mínimo previo posible:

```
$ echo '{"meta": {}, "simbolos": {}}' > _indice/simbolos.json
$ python3 _indice/construir-indices.py
documentos en español : 253
manual (inglés)       : 0
manual (español)      : 0
archivos .gml          : 0
símbolos explicados    : 2387  (cruce símbolo → documento)
símbolos de la API     : 3486  (de ellos 34 solo en fnames)
runtime leído          : 2026.0.0.23
[...]
MAPA.json sincronizado con el disco.
```

Con esa única línea de JSON sembrada a mano, el script sí deriva los 3 486 símbolos del
`GmlSpec.xml` real del runtime instalado — la promesa se cumple **una vez se evita el bug**, pero
nada en el README, `AGENTS.md`, `instalar.sh` ni `PUBLICAR.md` menciona este paso. No es
descubrible sin leer el *source* de `construir-indices.py` línea a línea, cosa que ningún
desarrollador que solo quiere escribir GML va a hacer.

Con `simbolos.json` ya sembrado, `buscar.py` funciona exactamente como se documenta:

```
$ python3 _indice/buscar.py draw_sprite_ext
# draw_sprite_ext  (función)
  firma:     draw_sprite_ext(sprite, subimg, x, y, xscale, yscale, rot, colour, alpha)
  devuelve:  Undefined
  explicada en la biblioteca:
    - 01 - Fundamentos/08 - Movimiento y colisiones.md
    [... 50 documentos más ...]
```

Y la prueba de fuego — el ejemplo textual del propio README ("le pides a un agente... y te
devuelve `instance_create()`... no existe"):

```
$ python3 _indice/validar-proyecto.py <proyecto de prueba con instance_create() inventado>
✗ 1 funciones INVENTADAS (no existen en el runtime):
  instance_create()
      en scripts/scr_test/scr_test.gml
      ¿quisiste decir? instance_create_layer, instance_create_depth, instance_change
      ficha: python3 "_indice/buscar.py" instance_create_layer
```

Detecta exactamente el caso que el README usa como gancho de venta, con la sugerencia correcta.
**El motor de detección funciona de verdad. El problema no es la idea, es que el arranque en frío
está roto y nadie lo ha probado.**

## 3. El "un solo comando" tampoco es tal, en un clon limpio

El README y `AGENTS.md` presentan `python3 _indice/actualizar.py` como *el* comando que hay que
correr, con la promesa «Sale con 0 solo si no queda deuda». En un clon limpio **nunca puede salir
con 0**, porque el paso 1 lo aborta antes de intentarlo siquiera, y el paso 1 solo puede pasar tras
`./reconstruir.sh manual` (≈6 150 páginas, «bien más de una hora») y `./reconstruir.sh codigo`
(≈3,8 GB). No hay forma de que un recién llegado obtenga «Biblioteca coherente» sin antes bajarse
gigas de contenido — y mientras tanto, ni siquiera llega al paso 2, que es el que de verdad importa
para poder escribir GML sin alucinar funciones.

Esto contradice el propio `PUBLICAR.md`, que en su sección "Lo que le pasa a quien clone el
repositorio" da a entender que solo el manual y el corpus de código quedan pendientes de
`reconstruir.sh` — no la generación de `simbolos.json`, que la misma sección da por hecha al
ejecutar `./instalar.sh`.

## 4. Los 238-239 enlaces rotos: ni un solo falso, pero mal gestionados

Repetí `python3 _indice/verificar-enlaces.py` de forma aislada para clasificar los 238 destinos
rotos que reportó (`actualizar.py` había contado 239 en su primera pasada; la diferencia de uno es
ruido entre pasadas, no relevante):

```
141  →  09 - Manual oficial/…
 97  →  11 - Código descargado/…
  0  →  cualquier otro destino
```

**El 100 % de los enlaces rotos apunta a las dos carpetas que el propio `.gitignore` excluye a
propósito.** Cero enlaces rotos "de verdad" (typos, archivos renombrados, rutas mal escritas). La
documentación en sí está limpia. El problema no es la calidad de los enlaces: es que
`verificar-enlaces.py` no distingue "roto porque alguien escribió mal una ruta" de "roto porque
apunta a contenido que el propio proyecto documenta como opcional y reconstruible" — y
`actualizar.py` trata ambos casos como igual de fatales, deteniendo TODO lo demás (incluida la
generación de símbolos, que no depende en nada del manual ni del código descargado).

## 5. Otro efecto colateral menor: `--manual` sin la carpeta 09

Con `09 - Manual oficial/` ausente (el estado normal de un clon limpio sin reconstruir), probé:

```
$ python3 _indice/buscar.py --manual "surface"
./07 - Ecosistema/05 - Scripts y utilidades GML.md:1257:2. **¿Libera memoria?**...
./07 - Ecosistema/04 - Proyectos de ejemplo para estudiar.md:152:| **Gráficos 2D** ...
[...]
```

Nada indica que esto NO son resultados del manual. Causa: `_indice/buscar.py:324` llama
`grep(["09 - Manual oficial"], patron, [".md"])`, y como esa carpeta no existe, la lista de rutas
pasadas al proceso `grep` queda vacía (`_indice/buscar.py:172-173` filtra con
`os.path.exists`). El `grep` de este sistema (macOS), invocado con `-r` y **sin ningún argumento de
ruta**, no falla ni dice "sin resultados": **recorre el directorio de trabajo actual completo**
(confirmado de forma aislada, reproduciendo la llamada exacta con `subprocess.run`). El resultado:
`--manual` devuelve contenido real pero de la carpeta equivocada, sin avisar de que el manual
mirror no está instalado. `--codigo` no tiene este problema porque `11 - Código descargado/` sí
existe en el clon (con solo `_RUTAS.json` y `_CATALOGO.md`), así que el `grep` real no encuentra
`.gml` y contesta «Sin resultados.» correctamente.

Es un hallazgo menor comparado con el de §2, pero es del mismo género: el código no comprueba
explícitamente "¿existe la fuente que se supone que voy a buscar?" antes de buscar en ella.

## 6. Lo que SÍ funciona exactamente como se documenta

- **`validar-compilacion-docs.py`** — no depende del manual ni del código descargado. Extrajo 3 713
  bloques ` ```gml `, descartó 304 con motivo explicado uno a uno, compiló los 3 409 restantes con
  `gm-cli` de verdad y **los 3 409 compilan sin errores de sintaxis**, en 20,9 s. Crea y borra su
  propio proyecto de prueba (`~/gm_prueba_docs`) sin dejar rastro. Es la comprobación más pesada de
  todas y la única que corre sobre un clon limpio sin ningún workaround.
- **`validar-codigo-gml.py`** — corrió igualmente sin el corpus descargado (usa solo el runtime +
  el índice, no los 608 repos) y encontró 3 posibles funciones inventadas *dentro de la propia
  documentación* (`draw_polygon()`, `display_write_all_specs()`,
  `camera_set_view_pos_subpixel()`) — un hallazgo de contenido real, ajeno al alcance de esta
  auditoría, pero prueba que el detector funciona incluso contra el propio material del repo.
- **`reconstruir.sh`** — el diseño es sólido y está bien documentado en su propia cabecera. Probado
  de verdad con `./reconstruir.sh codigo --limite 3 --destino <ruta de prueba>`: clonó 3
  repositorios reales (`1PassBlur`, `3D-2D`, `A-Star-Pathing`), no tocó la carpeta real `11 -
  Código descargado/` del clon, y `python3 _indice/reconstruccion/clonar_codigo.py
  --listar-excluidos` lista correctamente los 13 repositorios excluidos con su motivo (juego
  comercial / sin licencia libre), sin descargar nada. `./reconstruir.sh` sin argumentos imprime la
  ayuda sin tocar nada. Pide confirmación por stdin antes de cualquier operación real.
- **`./instalar.sh`** — instaló la skill correctamente en los 6 CLIs de IA detectados en esta
  máquina (Claude Code, Codex, `~/.agents/skills`, opencode, Qwen Code, Kimi Code CLI) y saltó
  limpiamente los 4 no instalados (Gemini CLI, Copilot CLI, Cursor CLI, Cline), listándolos por
  nombre sin tocar nada suyo. Registró `~/.config/gamemaker-biblioteca/ruta` correctamente. Lo
  único que falla es el paso final de regenerar índices, ya documentado en §2.
- **`gm-cli manual read "<símbolo>"`** — funciona de forma totalmente independiente del espejo
  local, contra la rama *monthly* en línea. Es el respaldo real que sí tiene un recién llegado
  mientras no reconstruye el manual — pero el README no lo presenta como el paso obligatorio que
  en la práctica es hasta que se corrige el bug de §2.
- **`validar-proyecto.py`** — una vez existe `simbolos.json` (por el workaround manual), detecta
  funciones inventadas con la sugerencia correcta, tal y como se documenta. Con una ruta
  inexistente falla limpio («No existe la carpeta: ...», exit 2), sin traceback.

## 7. Recomendaciones concretas

1. **`_indice/construir-indices.py:407`** — envolver la lectura de `simbolos.json` en algo como
   `previo = json.load(open(...)) if os.path.exists(...) else {"meta": {}, "simbolos": {}}`. Es el
   arreglo que de verdad importa: sin él, ningún clon limpio puede arrancar nunca, con o sin
   `reconstruir.sh`.
2. **`_indice/actualizar.py`** — que el paso 1 (`verificar-enlaces.py`) no aborte todo lo demás
   cuando el 100 % de los enlaces rotos apunta a `09 - Manual oficial/` o `11 - Código
   descargado/`: son "pendiente esperado", no "roto". Al menos permitir que el paso 2 (generación
   de `simbolos.json`) corra igualmente, ya que no depende de esas carpetas.
3. **`instalar.sh:145-153`** — no imprimir «Listo. Comprueba que responde: ...» de forma
   incondicional justo después de avisar «⚠ Revisa la salida de actualizar.py». Si `actualizar.py`
   falló, decirlo con claridad antes de sugerir el comando de verificación.
4. **`_indice/buscar.py:324`** (y la rama `--manual` de `buscar_todo`) — comprobar explícitamente
   `os.path.exists(RAIZ/"09 - Manual oficial")` antes de llamar a `grep`, e imprimir algo como «El
   manual no está instalado: ejecuta `./reconstruir.sh manual` (o usa `gm-cli manual read`)» en vez
   de dejar que un `grep -r` sin ruta busque en el directorio de trabajo entero.
5. **README / `PUBLICAR.md`** — documentar el workaround real (sembrar `simbolos.json` con
   `{"meta": {}, "simbolos": {}}` antes de `construir-indices.py`) como solución temporal *mientras
   no se aplique el arreglo del punto 1*, y corregir la frase de `PUBLICAR.md` que afirma sin
   matices que `./instalar.sh` deriva los índices — hoy es falsa en un clon limpio.

## 8. Restauración del entorno

Antes de tocar nada se guardó el estado exacto de los enlaces de skills (`~/.claude/skills`,
`~/.codex/skills`, `~/.agents/skills`, `~/.config/opencode/skills`, `~/.qwen/skills`,
`~/.kimi-code/skills`, `~/.gemini/skills`, `~/.copilot/skills`, `~/.cursor/skills`,
`~/.cline/skills`) y de `~/.config/gamemaker-biblioteca/ruta`. `./instalar.sh` (sin `--enlace`)
sustituyó los 6 enlaces simbólicos existentes por copias reales apuntando al clon. Tras terminar
las pruebas, los 6 se restauraron a sus symlinks originales exactos (verificado con `readlink`
contra el manifiesto guardado antes de empezar) y `~/.config/gamemaker-biblioteca/ruta` se
devolvió a `/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje`.

Efectos colaterales detectados y revertidos, ninguno causado por un comando mío contra el
repositorio original:

- El sistema de skills, al recargar `_indice/skills/gamemaker-biblioteca/SKILL.md` de la copia
  original, normalizó su frontmatter YAML (añadió comillas a la `description`) dos veces —
  comportamiento del propio cargador de skills. Revertido ambas veces con
  `git checkout -- SKILL.md AGENTS.md`.
- Un proceso en segundo plano de este equipo (hay un LaunchAgent `ai.adrian.codex-perfil.plist`)
  re-enlazó `~/.codex/skills/gamemaker-biblioteca` directamente a
  `Documents/GameMaker_Aprendizaje/_indice/skills/gamemaker-biblioteca`, saltándose la
  indirección por `~/.codex/skills-pool/` que tenía antes de esta auditoría (ambas rutas resuelven
  al mismo contenido, pero no es el enlace exacto que había). Corregido de vuelta a
  `~/.codex/skills-pool/gamemaker-biblioteca` para que coincida con el manifiesto tomado antes de
  empezar.

`git status` en el repositorio original queda limpio (solo aparece este informe nuevo, sin
seguimiento hasta que se añada).

`~/gm_clon_limpio` se borra al terminar esta auditoría.
