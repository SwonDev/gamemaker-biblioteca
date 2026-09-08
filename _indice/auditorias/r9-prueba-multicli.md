# R9 — ¿La skill funciona de verdad fuera de Claude Code?

**Fecha:** 8 de septiembre de 2026. **Máquina:** esta misma, con `codex`, `qwen`, `kimi` y
`opencode` instalados junto a Claude Code. **Metodología:** para cada CLI — comprobar que arranca
en modo no interactivo, hacerle la pregunta trampa «¿existe `instance_create` en GameMaker LTS
2026?» (la respuesta correcta, que solo la skill fuerza, es que **no** existe: es
`instance_create_layer`/`instance_create_depth`) y, con el que mejor respondió, pedirle una tarea
real pequeña. Trabajado en `~/gm_prueba_codex` (fuera de la biblioteca), borrado al terminar.

## Veredicto en una frase

**Funciona de verdad en `codex` — de forma ejemplar, con evidencia línea por línea de que lee la
skill y sigue su procedimiento exacto —, funciona pero de forma no concluyente en `opencode`
(responde bien, pero un `AGENTS.md` global ya le decía cómo verificarlo, así que el mérito no es
solo de la skill), estaba genuinamente rota en `kimi` por un bug de YAML que este informe
encontró, arregló y verificó en vivo, y no se pudo ni probar en `qwen` por falta de autenticación
en esta máquina.** Que un archivo esté copiado en `~/.qwen/skills/` o `~/.kimi-code/skills/` no
garantizaba nada — en `kimi` era, literalmente, papel mojado: el propio CLI lo descartaba con un
aviso silencioso en su log en cada una de las tres carpetas donde lo busca.

---

## Tabla resumen

| CLI | Instalado | Carga la skill | La aplica | Veredicto |
|---|---|---|---|---|
| `codex` (OpenAI) 0.153.4 | Sí | **Sí** — leyó el `SKILL.md` completo antes de responder | **Sí** — verificó cada símbolo con `buscar.py`, una llamada por símbolo | Funciona de verdad |
| `opencode` 1.18.14 | Sí | Parseada sin error (a diferencia de kimi) | Responde bien, pero no aislable de un `AGENTS.md` global que ya cubre el mismo caso | Zona gris — no concluyente |
| `qwen` (Alibaba) 0.21.6 | Sí | No se pudo probar | No se pudo probar | Bloqueado — sin autenticación en esta máquina |
| `kimi` (Moonshot) 0.36.1 | Sí | **No, hasta el arreglo de este informe** — bug de YAML real y reproducible | No se pudo observar (backend caído durante la prueba) | Bug real, encontrado y arreglado; efecto en una respuesta real sin confirmar por caída del proveedor |
| `gemini`, `cursor-agent`, `aider`, `cline` | No instalados en esta máquina | — | — | Fuera de alcance |

---

## 1 · Qué hay instalado

```
codex          codex          → codex-cli 0.153.4, acepta `codex exec` no interactivo
qwen           /opt/homebrew/bin/qwen    → 0.21.6, acepta `qwen -p`
kimi           /Users/.../.kimi-code/bin/kimi → 0.36.1, acepta `kimi -p`
opencode       /opt/homebrew/bin/opencode → 1.18.14, acepta `opencode run`
gemini         no instalado
cursor-agent   no instalado
aider          no instalado
cline          no instalado
```

Los cuatro CLI a probar arrancan y aceptan un prompt no interactivo sin problema — la barrera no
está ahí.

Ubicaciones donde `instalar.sh` deja la skill (comprobadas una por una): `~/.claude/skills/`,
`~/.codex/skills/` (+ `~/.codex/skills-pool/`), `~/.agents/skills/` (genérico: Codex canónico,
Copilot CLI, Gemini CLI, Cursor CLI, Kimi Code), `~/.config/opencode/skills/`, `~/.qwen/skills/`
y `~/.kimi-code/skills/`. Las seis existían como enlaces simbólicos a la carpeta canónica del
repo al empezar esta auditoría.

---

## 2 · `codex` — funciona de verdad

### Prueba de carga (pregunta trampa)

Antes de responder, `codex` ejecutó por su cuenta:

```
cat /Users/adrianpereradelgado/.agents/skills/gamemaker-biblioteca/SKILL.md
```

— el archivo **completo**, no solo el frontmatter — y a continuación, siguiendo al pie de la letra
la instrucción de la skill (`python3 "$BIB/_indice/buscar.py" nombre_de_la_funcion`), ejecutó:

```
$ python3 "$BIB/_indice/buscar.py" instance_create
«instance_create» NO existe en el runtime 2026.0.0.23.

¿Quizá buscabas?
  - instance_create_depth
  - instance_create_layer
```

Respuesta final literal:

> No: `instance_create()` no existe en GameMaker LTS 2026, confirmado en el índice del runtime
> 2026.0.0.23 instalado. Usa `instance_create_layer()` para crear en una capa o
> `instance_create_depth()` para indicar la profundidad, según el manual oficial.

Correcta, verificada, con la fuente citada. También leyó `~/.codex/skills/gamemaker-expert/SKILL.md`
por su cuenta, porque la propia `gamemaker-biblioteca` dice «si también está cargada la skill
`gamemaker-expert`…» — es decir, siguió una referencia cruzada entre dos skills sin que se lo
pidiera.

### Prueba de aplicación

Encargo: «Escríbeme el código GML del evento Step de un objeto `obj_jugador` que mueva al jugador
con las flechas del teclado, usando la biblioteca `gamemaker-biblioteca` para verificar cada
función antes de escribirla. No hace falta crear un proyecto ni compilar.»

Verificó **cada símbolo, uno por uno**, antes de usarlo:

```
for simbolo in keyboard_check vk_left vk_right vk_up vk_down x y sqrt; do
    python3 "$BIB/_indice/buscar.py" "$simbolo"
done
```

y además leyó las páginas del manual español de `keyboard_check` y `sqrt`. Código final:

```gml
// Evento Step de obj_jugador
var _velocidad = 4; // Píxeles por paso.

var _horizontal = keyboard_check(vk_right) - keyboard_check(vk_left);
var _vertical = keyboard_check(vk_down) - keyboard_check(vk_up);

// Mantener la misma velocidad al moverse en diagonal.
if (_horizontal != 0 && _vertical != 0) {
    _horizontal /= sqrt(2);
    _vertical /= sqrt(2);
}

x += _horizontal * _velocidad;
y += _vertical * _velocidad;
```

> Verifiqué con `gamemaker-biblioteca` las firmas completas de `keyboard_check(key)` y `sqrt(val)`,
> las cuatro constantes de flechas y las variables de instancia `x` e `y`. […] Movimiento libre,
> sin colisiones. No creé un proyecto ni compilé, como pediste.

Cumple las convenciones de la biblioteca sin que se le pidieran explícitamente: `obj_` en el
nombre del objeto, `snake_case`, locales con prefijo `_` (`_velocidad`, `_horizontal`,
`_vertical`), ningún nombre reservado pisado. No mencionó las «catorce trampas» de la skill
(`resourcetool`, numeración de eventos, plantillas de `gm-cli init`…) porque ninguna aplicaba a
una tarea de solo-código sin proyecto — correcto no forzarlas.

**Conclusión sobre `codex`: la skill le cambia el comportamiento de forma verificable y
reproducible.** No es una coincidencia de memoria de entrenamiento: la secuencia
leer-SKILL.md → ejecutar-buscar.py-por-símbolo → responder-citando-el-resultado está grabada en el
log, comando por comando.

---

## 3 · `opencode` — responde bien, pero la prueba no aísla la causa

### Prueba de carga

`opencode run "..."` respondió correctamente:

> No, `instance_create` ya no existe en GameMaker LTS 2026. Fue sustituida en GMS2 por
> `instance_create_layer` (asignando la instancia a una capa) y `instance_create_depth` (con
> profundidad). El manual oficial solo documenta estas dos versiones modernas.

Antes de responder ejecutó `gm-cli manual read "instance_create"` (que devuelve la ficha de
`instance_create_layer`) y `gm-cli manual search` (que falló, «No command registered for
`search`», y lo descartó sin problema). El log de opencode (`~/.local/share/opencode/log/opencode.log`)
confirma que el frontmatter de `gamemaker-biblioteca` se parseó **sin error** — a diferencia de
`kimi` (ver §5), no aparece en ningún `Skipping invalid skill`, y tampoco en la lista de
`duplicate skill name` que sí reporta decenas de veces para otras skills instaladas por partida
doble en `~/.claude/skills` y `~/.config/opencode/skills` (prueba de que el logger sí marca esos
casos cuando existen; para `gamemaker-biblioteca` no lo hizo, luego no hubo conflicto ni error).

**Pero hay un matiz importante que hay que decir con honestidad**: `~/.config/opencode/opencode.json`
ya carga como instrucción global `~/.config/opencode/AGENTS.md`, un espejo del `CLAUDE.md` personal
del usuario que **por sí solo** ya contiene el bloque «GameMaker — CLI OBLIGATORIO» con la
instrucción «ANTE CUALQUIER DUDA de una función […]: `gm-cli manual read "<tema>"` ANTES de
escribir código. No inventes nombres de funciones ni supongas firmas». El log no muestra ninguna
lectura del cuerpo de `SKILL.md` (solo llamadas de `bash`), así que **no se puede afirmar con
certeza si el comportamiento correcto vino de la skill `gamemaker-biblioteca` o del `AGENTS.md`
genérico que ya trae el mismo mensaje**. Es un resultado bueno, pero contaminado por una segunda
fuente de grounding que ya existía independientemente de la skill.

**Conclusión sobre `opencode`: no alucina y responde bien — pero esta prueba concreta no demuestra
que sea la skill `gamemaker-biblioteca` (y no el `AGENTS.md` ya presente) quien lo esté logrando.**

---

## 4 · `qwen` — bloqueado por falta de autenticación

```
$ qwen -p "¿Existe la función instance_create en GameMaker LTS 2026?..."
No auth type is selected. Please configure an auth type (e.g. via settings or
--auth-type) before running in non-interactive mode.
```

No hay credenciales de `qwen` en esta máquina (ni en `~/.qwen/`, ni variables de entorno, ni en
`~/.config/swon/secrets.env`), y `qwen auth` está deshabilitado («Configure authentication
(removed)»). No se pudo ejecutar ni un solo prompt no interactivo: **ni la carga ni la aplicación
de la skill se pudieron probar**.

**Hallazgo adicional, independiente del bloqueo de autenticación**: `~/.qwen/settings.json`
declara:

```json
"skills": { "directories": ["~/.claude/skills"] }
```

— es decir, la configuración activa de `qwen` en esta máquina **no** apunta a `~/.qwen/skills/`
(que es exactamente donde `instalar.sh` coloca el enlace de esta skill), sino a
`~/.claude/skills/`. Hoy «funciona por casualidad»: la skill también vive ahí porque Claude Code
la instala en la misma carpeta. Pero si el usuario alguna vez desinstala Claude Code o limpia
`~/.claude/skills/`, `qwen` se quedaría sin `gamemaker-biblioteca` aunque
`~/.qwen/skills/gamemaker-biblioteca` siga presente y correcto — el CLI, según su propia
configuración, no mira ahí. No se pudo confirmar en vivo si `qwen` de verdad respeta ese ajuste o
si además indexa su propia carpeta por defecto (no hay forma de comprobarlo sin autenticación), así
que queda como hallazgo de configuración, no como hecho verificado en ejecución.

**Recomendación**: autenticar `qwen` a mano (`qwen` interactivo, flujo de login) y, una vez dentro,
repetir la pregunta trampa; y revisar si conviene añadir `~/.qwen/skills` a `settings.json` para no
depender de que Claude Code esté instalado.

---

## 5 · `kimi` — bug real, encontrado y arreglado en esta sesión

### El fallo

`kimi -p "..."` no daba la respuesta trampa — directamente **no cargaba la skill**, en silencio.
`~/.kimi-code/logs/kimi-code.log` lo confirma en las tres carpetas donde kimi la busca
(`~/.claude/skills`, `~/.kimi-code/skills`, `~/.agents/skills`):

```
WARN  Skipping invalid skill at /Users/adrianpereradelgado/.kimi-code/skills/gamemaker-biblioteca/SKILL.md:
Invalid frontmatter in .../SKILL.md: bad indentation of a mapping entry (2:277)
  SkillParseError: ...
    at parseSkillText (.../main.cjs:234539:48)
```

### Causa raíz

La línea `description:` del frontmatter YAML no llevaba comillas, y su texto contiene dos
secuencias «`: `» (dos puntos + espacio) — exactamente en la columna 277, donde dice «…cualquiera
de sus disciplinas: diseño de juego…» — y otra vez más adelante en «…y para publicar: firmar…».
Un escalar YAML plano (sin comillas) no puede contener `": "` en mitad del valor: la especificación
lo reserva para separar clave de valor en un mapeo. Verificado con `python3 -c "import yaml;
yaml.safe_load(...)"`: el YAML original, en efecto, es inválido de forma estricta. El parser de
`kimi` lo rechaza; los de Claude Code y `opencode` son más tolerantes y lo aceptan igual — por eso
el mismo archivo, sin tocar nada, «funciona» en unos CLI y no en otros. No es un problema de rutas
ni de instalación: **el contenido del `SKILL.md` es YAML inválido según la especificación**, y
esta auditoría es la primera vez que se prueba contra un parser que sí lo hace cumplir.

### Arreglo aplicado

Envolví el valor completo de `description` entre comillas dobles en la fuente canónica
(`_indice/skills/gamemaker-biblioteca/SKILL.md`) — no hacía falta escapar nada, el texto no
contiene comillas dobles internas. Regeneré `AGENTS.md` con `_indice/sincronizar-skill.py` y
repropagué a los seis destinos con `./instalar.sh --enlace` (enlaces simbólicos: una futura edición
del `SKILL.md` llega sola a todos los CLI, sin reinstalar).

**Verificado en vivo**: tras el arreglo, una nueva ejecución de `kimi` deja de mencionar
`gamemaker-biblioteca` en la lista de skills descartadas — el log solo sigue quejándose de
`physics-3d-collision` (una skill ajena a esta biblioteca, con el mismo bug de fondo, fuera del
alcance de este arreglo). El parseo funciona.

**Lo que no se pudo verificar**: una respuesta real de `kimi` a la pregunta trampa. Su backend
(Moonshot) devolvió tres veces seguidas, en distintos momentos de la sesión:

```
error: failed to run prompt: provider.api_error: 500 The server had an error while processing your request
```

— un fallo de servicio del proveedor, no relacionado con la skill ni con el arreglo (persistió
igual antes y después de corregir el YAML). No insistí más allá de tres intentos cortos para no
alargar la prueba contra un servicio caído.

**Conclusión sobre `kimi`: antes de esta auditoría, la skill NUNCA llegaba a cargarse — el archivo
estaba «copiado» pero era papel mojado. Ahora el parseo está arreglado y confirmado; falta
confirmar el efecto en una respuesta real cuando el backend de Moonshot vuelva a estar disponible.**

---

## 6 · Advertencia operativa: esta máquina tiene otra sesión trabajando en el mismo repositorio

Durante esta auditoría detecté que **otro agente está trabajando de forma concurrente sobre este
mismo checkout de git**, en paralelo: mi edición del `SKILL.md` (sin comitear) fue revertida dos
veces por operaciones de git ajenas — el `HEAD` avanzó a commits que yo no hice (`2e2a1cc "Cuatro
perfiles más…"`, entre otros) y el árbol volvía a estar limpio con el contenido original. Al
terminar esta sesión, el árbol de trabajo tiene además cambios sin comitear en `_indice/buscar.py`,
`_indice/construir-indices.py` y `_indice/verificar-enlaces.py` que **no son míos** — coinciden
exactamente con el bug que describe la auditoría paralela `_indice/auditorias/r9-clon-limpio.md`
(un `try/except` para el `Traceback` de `simbolos.json` en un clon limpio), escrita por esa otra
sesión durante esta misma ventana de tiempo. No toqué esos tres archivos.

Mi arreglo del `SKILL.md` está aplicado y verificado **en el momento de escribir esto**, pero
**no está comiteado** — por las reglas de esta sesión solo comiteo si el usuario lo pide
explícitamente, y comitear ahora mezclaría mi cambio con el trabajo en curso de la otra sesión sin
que nadie lo haya revisado. Antes de dar esto por definitivamente resuelto: comprobar
`git status`, confirmar con la otra sesión (o esperar a que termine) y comitear todo junto cuando
el usuario lo decida.

---

## 7 · Qué haría falta para que los cuatro funcionaran hoy

- **`qwen`**: autenticar el CLI en esta máquina (no es un problema de la skill) y, si conviene,
  añadir `~/.qwen/skills` junto a `~/.claude/skills` en `~/.qwen/settings.json` para no depender
  de que Claude Code esté instalado.
- **`kimi`**: arreglo ya aplicado (comillas en `description`); pendiente confirmar con una
  respuesta real en cuanto el backend de Moonshot se recupere, y comitear el cambio.
- **`opencode`**: nada que arreglar — funciona —, pero si se quiere una prueba que aísle la skill
  de verdad, habría que repetirla en una máquina sin el `AGENTS.md` global del usuario, o pedir
  algo que solo la biblioteca sepa (p. ej. una función marcada «obsoleta» en su ficha, que
  `gm-cli manual read` por sí solo no señala tan bien como `buscar.py`).
- **`codex`**: nada — es la prueba más limpia y positiva de las cuatro.
