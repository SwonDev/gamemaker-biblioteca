# Auditoría r6 · Prueba narrativa — ¿guía la skill la parte de historia, o solo la de mecánica?

> **Encargo**: actuar como un agente cualquiera al que un usuario le pide «hazme un juego de
> aventura con una historia, con diálogos y varios finales», usando `gamemaker-biblioteca` como
> única fuente. La prueba anterior (`r5-revalidacion.md`) ya validó un juego de acción **sin**
> historia; esta ataca deliberadamente lo que aún no se había probado: si la skill guía de verdad
> la parte narrativa, o si un agente acaba improvisando estructura de diálogos, ramas y finales
> por su cuenta — que es justo lo que el usuario del proyecto dice que los agentes se saltan.
> Restricción de esta sesión (no de la biblioteca): **nunca se ejecutó el juego** (`gm-cli run`
> prohibido). Trabajado en `~/gm_prueba_narrativa` (fuera de la biblioteca), borrado al terminar.
>
> Verificado en vivo el **8 de septiembre de 2026**, con `gm-cli` `2.3.0` sobre GameMaker LTS
> 2026.0 (runtime `2026.0.0.23`), la misma combinación que documenta la skill. macOS 26.6.2
> (Darwin 25.6.0).

## Veredicto adelantado

**Sí — para la parte narrativa, la skill guía de verdad, no solo la mecánica.** El documento
`13 · 12 — Diseño narrativo y diálogos` le dio a este agente una teoría del oficio (estructura de
tres actos, elecciones que importan, ramificar-cuesta-converger-es-la-solución) **y** un modelo de
datos GML completo y listo para adaptar (flags, nodos, opciones, guardado, validador de grafo).
El juego que salió — *El Faro Silencioso*, tres personajes con voz distinta, 14 nodos de diálogo,
tres finales genuinamente distintos por combinación de decisiones, guardado que preserva el
estado — compila limpio (`exit 0`), pasa el validador de símbolos inventados sobre 751 llamadas y
pasa el validador de alcanzabilidad del propio grafo narrativo sin un solo destino roto ni un
nodo huérfano.

Dicho esto, **no fue gratis, y hay un fallo real de la skill que hay que corregir** (§6): un
`RESOURCE CREATE TYPE=includedfile` de `resourcetool` deja el `filePath` mal puesto para la
convención `datafiles/` que la propia skill enseña en quince sitios distintos — y el error es
**silencioso**: no lo detecta `gm-cli compile --errors-only` (el comando que la skill recomienda
en su tabla del ciclo del agente), solo aparece como un `WARNING` si se compila sin ese flag. Sin
comprobarlo, el juego habría compilado «limpio» y habría sido enteramente mudo — el guion nunca
se carga — sin ningún síntoma hasta la primera vez que alguien lo jugara.

---

## 1 · ¿Te guió la skill para la narrativa, o tuviste que improvisar la estructura?

**Me guió, con un documento entero dedicado a esto — no tuve que inventar ni la estructura de
ramas ni el modelo de datos.**

`13 · 12 — Diseño narrativo y diálogos` (2455 líneas) cubre, en este orden, exactamente lo que
hacía falta para construir el juego:

- **§1**: la distinción historia/trama/tema, y la regla de oro de agencia de Janet Murray, citada
  literalmente: «**Es mejor una elección con tres consecuencias que tres elecciones sin
  ninguna.**» (línea 83). Usé esto para decidir el alcance: en vez de un árbol grande y superficial,
  tres decisiones reales (esconder o no a Tobías, creerle o no, mentir o no a Reyes) que se
  acumulan hacia tres finales distintos.
- **§2.6 y §4.7**: el catálogo de Ashwell/Short de estructuras narrativas, con la aritmética
  explícita del coste de ramificar sin converger («Una elección binaria en cada uno de 10 nodos da
  2¹⁰ = 1024 finales... son más de 300 000 palabras», línea 276-278) y los tres patrones que sí se
  usan de verdad: **cuello de botella**, **ramas que convergen con memoria** y **abanico final**
  (líneas 645-675). Construí *El Faro Silencioso* exactamente así: todas las decisiones del acto
  II convergen en el hub de Reyes (cuello de botella), y solo al final se abre en abanico hacia
  tres desenlaces (patrón ③, mi `scr_finales.gml`).
- **§6.1 y §6.1 bis**: el modelo de datos completo en GML — `Linea`, `Opcion`, `Nodo`, `Guion`,
  `dialogo_empezar()`, y el patrón de *hub* («un `Opcion` cuyo `destino` es el mismo `Nodo` que la
  contiene ya es un hub», línea 1100-1101) — que adapté directamente para `tobias_hub` y
  `reyes_hub`: el jugador puede preguntarle a Tobías por su herida o por su hermana en cualquier
  orden, sin que la conversación se cierre sola.
- **§8.3-8.4**: la «hoja de escena» (intención/obstáculo/resultado/flags/salidas) y el «mapa de
  ramas» en texto. Los usé tal cual para diseñar la escena antes de escribir una sola línea, tal
  y como pide `§9`, primer punto del checklist: «La premisa cabe en una frase» — la mía: *«Eres
  la guardiana de un faro que debe decidir si ayuda a un náufrago fugitivo antes de que llegue la
  patrulla.»*

Lo único que la skill **no** trae — y lo dice ella misma — es el motor de la caja de diálogo (eso
remite a `04 · 10` y a `07 · 19 — Chatterbox`, ver §4 más abajo). Todo lo demás, la estructura de
la historia, el modelo de flags, el patrón de nodos, salió de `13 · 12`, no de mi criterio.

---

## 2 · ¿Te dijo cómo guardar el estado narrativo y evitar una partida en estado imposible?

**Sí, con el patrón exacto y la advertencia explícita del bug que provoca — lo apliqué literal.**

`13 · 12` §6.2 da el modelo de flags (`flags_iniciar`, `flag_leer`, `flag_poner`, `flag_sumar`,
`flag_una_vez`) y, sobre todo, una regla marcada con 🔺 que es la que de verdad evita un estado
imposible (línea 1241-1244):

> «**Reinicia primero, superpone después.** Si asignas `global.flags = _d.flags` de golpe, una
> partida guardada antes de que existiera `flags.acto` se carga **sin** `acto`, y el primer
> `global.flags.acto` revienta. Reiniciando y superponiendo, los flags nuevos aparecen con su
> valor por defecto y los viejos se respetan.»

Mi `narrativa_cargar()` (`scripts/scr_narrativa_guardado/scr_narrativa_guardado.gml`) hace
exactamente esto: `flags_iniciar()` primero, y luego copia clave a clave lo que traiga el save
encima. También seguí el aviso de la misma sección sobre no guardar *handles* de asset — mi save
solo guarda strings (`room_actual`, nombres de nodo) y números, nunca un `sprite_index` ni un
`object_index`.

Para el guardado en sí, la skill remite a `scr_save_load.gml` de `06 - Assets y Scripts`
(⭐ Esencial, «✅ Compilación verificada» en sus propios registros) — lo copié **sin tocar una
línea**, incluida su defensa contra la Trampa 6 (`directory_exists()`/`directory_create()`
devolviendo `false` siempre bajo `gm-cli run --target mac`) que ya trae escrita, con checksum de
integridad, escritura segura (temporal → validar → reemplazar) y copias de seguridad rotativas.
No reinventé nada de esto: es exactamente el caso de «sistemas ya resueltos por terceros» del
paso 4 del flujo de la skill.

**Sobre «evitar un estado imposible» específicamente de la narrativa** (no solo del guardado): la
propia `13 · 12` no tiene una función de «validar consistencia de flags», pero el diseño que
propone —flags booleanos planos, condiciones declarativas (`requiere`/`requiere_falso` en mi
extensión, ver §4), y la regla de «reiniciar y superponer»— hace estructuralmente imposible que
una partida cargada quede en un estado que el juego no sepa interpretar: cualquier flag que falte
se lee como `false` por defecto (`flag_leer`, con su comentario explícito «NUNCA revienta»), así
que un nodo que pregunte por un flag que aún no existía en una partida vieja simplemente no
encuentra nada raro, no crashea.

---

## 3 · ¿Te avisó de los callejones sin salida narrativos y de cómo comprobar la alcanzabilidad?

**Sí — dos veces, en dos documentos distintos, con una herramienta ejecutable en cada caso.**

**(a) Destinos rotos y nodos huérfanos.** `13 · 12` §6.10, «Validar el grafo antes de jugarlo»,
empieza diciendo exactamente el problema que un agente puede introducir sin darse cuenta (línea
1935-1938):

> «Un `id` mal escrito en un `destino`... no revienta al compilar — revienta en mitad de la
> partida de un jugador, o peor, deja una opción que no lleva a ningún sitio.»

Y da el script completo, `validar_grafo_narrativo.py`, que recorre el JSON del guion y falla con
la lista exacta de problemas si hay un destino que no existe o un nodo al que nada llega. Lo copié
tal cual (sin modificar una línea) y lo ejecuté sobre mis 14 nodos, con los cinco puntos de
entrada reales que dispara mi GML (`orilla_hallazgo`, `tobias_hub`, `decision_esconder`,
`reyes_hub`, `amanecer_decision` — el propio documento avisa, línea 1989-1993, de que las entradas
son un argumento, no un descubrimiento automático, y que sin decírselas el script marca huérfano
a un nodo de entrada legítimo):

```
14 nodos, todos los destinos resuelven y todos son alcanzables.
Entradas declaradas: ['amanecer_decision', 'decision_esconder', 'orilla_hallazgo', 'reyes_hub', 'tobias_hub']
```

**(b) Callejones sin salida de diseño** (no de datos: decisiones que dejan al jugador sin poder
avanzar). Esto lo cubre `04 · 48 — Aventura gráfica y point and click` §3.11, «La regla de oro del
género», con las dos reglas de Ron Gilbert citadas literalmente («*Live and learn*»: nunca forzar
morir/recargar para aprender qué no hacer; «*I forgot to pick it up*»: nunca exigir un objeto que
luego no se puede recuperar) y, sobre todo, un patrón de código que usé de verdad:
`punto_de_no_retorno_verificar(_flags_requeridos)` (§3.11.2, línea 1277-1284), que bloquea una
transición que cierra el paso hacia atrás hasta que el diseño confirma que el jugador ya tiene lo
que hace falta.

Lo apliqué tal cual en `scr_utilidades.gml` y lo até al bote del alba (`obj_bote`): no aparece ni
es interactuable hasta que `reyes_resuelto` es verdadero, así que el jugador nunca puede llegar al
desenlace con una conversación pendiente a medias. Y diseñé el resto del grafo con la misma
disciplina que pide la sección: **cada decisión del acto II tiene dos opciones y las dos llevan a
algún sitio** — esconder a Tobías o no, darle provisiones o no, decirle la verdad a Reyes o
mentirle — nunca una opción muerta ni una que deje sin continuar. Lo comprobé a mano, nodo por
nodo (tabla en el propio informe de construcción de esta sesión), siguiendo el «ejercicio de
Gilbert» que describe la misma sección: contar la secuencia como una historia y mirar dónde el
protagonista sabría algo que no pudo haber aprendido. No encontré ninguno.

---

## 4 · ¿Encontraste la librería adecuada para diálogos, o escribiste el sistema desde cero sin saber que existía una?

**La encontré, la leí, y decidí NO usarla — con la propia skill dándome el criterio exacto para
esa decisión, no a ciegas.**

`13 · 12` §5 tiene una tabla completa de herramientas de escritura, con **Chatterbox + Crochet**
marcado explícitamente como «✅ La opción por defecto» (línea 737). Comprobé que existe de verdad:
está descargada en `11 - Código descargado/librerias/dialogos-y-narrativa/Chatterbox`, con su guía
completa en `07 · 19` (bucle `ChatterboxIsWaiting`/`ChatterboxContinue`/`ChatterboxSelect`,
variables compartidas con Yarn, `ChatterboxAddFunction` para exponer funciones del juego al
guion). No es una librería que «no sabía que existía»: la leí entera antes de decidir.

La misma §5, en su fila de «JSON / CSV propios», y con más detalle en §5.4, da el criterio para
**no** usarla (línea 843-844):

> «Si tu juego tiene **menos de ~200 líneas de diálogo y ninguna ramificación profunda**, montar
> Chatterbox es traer un camión para una caja. Una tabla basta.»

Mi guion tiene 14 nodos y 95 claves de texto en total (diálogo + interfaz) — bien por debajo del
umbral que la propia skill fija. Además, §5.4 da la regla estructural exacta que apliqué:
«el texto nunca vive en el nodo, vive en la tabla de idiomas» — separé `datafiles/nodos.json`
(la estructura, con `requiere`/`efectos`) de `datafiles/es.json` (el texto), tal cual pide esa
sección.

**Lo que la skill no trae, y tuve que añadir yo**: su propio `guion_cargar()` de ejemplo (§6.1)
solo resuelve una condición (`requiere`) en las opciones, porque en su ejemplo los efectos son
*métodos* GML y «los métodos no se serializan» (línea 1035-1036) — cita literal del propio
documento. Mi juego necesitaba que **elegir una opción escriba flags** (esconder a Tobías, mentir
a Reyes...), así que añadí al JSON tres piezas de dato puro no documentadas por la skill:
`requiere_falso` (negación de una condición), `efectos` (una lista de `{flag, poner}` /
`{flag, sumar}`) — nada de código en el JSON, solo datos que mi `aplicar_efectos()` interpreta.
Es exactamente el hueco que el propio §6.10 admite que existe («si te hace falta esa garantía, es
la primera señal de que las misiones deberían tener su propio archivo de datos», línea 1999-2003)
aplicado a las opciones en vez de a las misiones. En ningún momento de esto la skill me dejó
tirado: me dio el 90 % del modelo y señaló ella misma, por escrito, exactamente el 10 % que
faltaba.

---

## 5 · ¿Los textos y los personajes tienen voz propia, o son marcadores de posición sin personalidad?

**Voz propia, con la prueba de tapar el nombre aplicada de verdad — pero con un límite honesto: es
poca cantidad de texto para juzgar una voz con solidez.**

`13 · 12` §4.1 da la prueba: «tapa los nombres de quien habla... si no puedes decir quién dice
qué, todos tus personajes son la misma persona» — y la regla operativa: dale a cada personaje
**una regla de habla inviolable**. Diseñé tres:

- **Mara** (protagonista): nunca usa signos de exclamación; narra en frases cortas y
  declarativas, nunca hace preguntas en voz alta (sus preguntas son las opciones del jugador).
  *"La tormenta ha tirado algo a la playa. No es un tablón."* — *"Un candil sin aceite no
  calienta a nadie."*
- **Tobías** (náufrago): nunca dice «no» directamente; responde con otra pregunta o minimiza.
  *"¿Vas a rematarme o me ayudas a levantarme?"* — sobre su herida, dos veces seguidas: *"No es
  nada que no cure el tiempo"* → *"No es nada, ya te lo he dicho."* — deflexión consistente, no
  una respuesta sincera en ningún momento hasta la confesión.
- **Sargento Reyes**: cada intervención relevante cita el reglamento o el procedimiento, nunca una
  opinión personal directa. *"El reglamento exige un parte completo antes del mediodía."* —
  *"Es el procedimiento, señorita, no una opinión mía."*

Aplicado el filtro real: si tapo los nombres en el guion completo (ver el volcado de nodos del
informe de construcción), sigo pudiendo decir quién habla en cada línea, incluidas las de Mara sin
etiqueta explícita de personaje. Eso es lo que pide la prueba.

**El límite, con honestidad**: son ~30 líneas por personaje en total. Es suficiente para que la
voz se note y se sostenga, pero no es la cantidad de texto con la que se pondría a prueba de
verdad una voz a lo largo de un juego más largo — no quiero venderlo como más de lo que es. Lo que
sí puedo afirmar con solidez: **no hay ni una sola línea de relleno tipo "Diálogo del NPC 1"** ni
texto placeholder — cada línea existe porque hace avanzar la trama, revela carácter o cambia según
un flag (13/12 §4.8, «reactividad barata»: la reacción de Tobías a la pregunta por su hermana
cambia la segunda vez que se le pregunta; la de Reyes menciona la luz del pañol **solo** si Mara
escondió a Tobías — consecuencia diferida real, no decorativa).

---

## 6 · ¿Hubo algún punto donde la skill te dejó tirado, o te dijo algo falso?

**Un fallo real y grave que corregir en la skill (bug de `filePath` en Included Files), y una
ambigüedad de sintaxis que me costó tiempo pero cuya causa última fui yo, no la skill.**

### 6.1 · El fallo real: `RESOURCE CREATE TYPE=includedfile` no deja el archivo donde la skill dice que vive

La skill repite en al menos quince sitios (`13 · 12` §5.4/§6.1, `13 · 06` §3.8, `04 · 21`,
`13 · 16`...) que los `.json` de datos van en **`datafiles/`** — nunca en la raíz del proyecto.
Creé mis dos archivos (`nodos.json`, `es.json`) con `gm-cli resourcetool eval "resource create
type=includedfile name=nodos.json"`, tal como enseña el inventario de comandos de `12 · 09` §3.
El recurso se registró, pero con `"filePath":""` en el `.yyp` — **la raíz del proyecto, no
`datafiles/`**.

`gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only` — el comando exacto que `12 · 09` §1
recomienda en la tabla del ciclo del agente para el paso «Compilar» — dio `exit 0` **sin ninguna
salida**, como si todo estuviera bien. Solo compilando **sin** `--errors-only` aparece la prueba
real:

```
WARNING :: datafile .../es.json was NOT copied skipped - reason File does not exist
WARNING :: datafile .../nodos.json was NOT copied skipped - reason File does not exist
```

Es decir: el juego habría compilado «limpio» según el propio criterio que la skill enseña a usar,
y habría sido **enteramente mudo** — `guion_cargar()` habría encontrado `file_exists() == false`
y devuelto un `Guion` vacío, sin un solo error visible hasta que alguien lo jugara. Es exactamente
la clase de fallo silencioso que las Trampas 4 y 5 de `12 · 09` avisan que existe para funciones
y fuentes — pero **nadie había documentado que también le pasa a los Included Files creados por
`resourcetool`**, y con el añadido de que ni siquiera `--errors-only` lo delata.

**Cómo lo encontré y lo arreglé** (con el mismo método que ya modela la propia Trampa 2 de
`12 · 09`: leer un proyecto real descargado en vez de suponer): busqué un `.yyp` de la carpeta
`11 - Código descargado` con `IncludedFiles` de verdad
(`GMEXT-GameCenter/source/GameCenter_gml/GameCenter.yyp`) y comparé — el suyo tiene
`"filePath":"datafiles"`, no `""`. Corregí el campo en mi `.yyp` (edición directa, justificada
como el último recurso de `12 · 09` §9.5, verificada inmediatamente con `resourcetool eval
"check"` antes de tocar nada más), recompilé, y el `WARNING` desapareció. Verificación final, sin
ejecutar el juego: **abrí el `game.zip` compilado y confirmé que `assets/es.json` (6895 bytes) y
`assets/nodos.json` (9519 bytes) están dentro del paquete.**

**Corrección recomendada para la skill**: documentar en `12 · 09` §3 (o en un nuevo apartado de
Trampas) que `RESOURCE CREATE TYPE=includedfile` deja `filePath` vacío, que hay que fijarlo a
`datafiles` a mano tras crearlo, y que **compilar sin `--errors-only` al menos una vez** es la
única forma de detectar un Included File que no se copió — el flag que la propia skill recomienda
para el ciclo normal lo esconde.

### 6.2 · Lo que no fue un fallo de la skill, aunque lo pareció al principio

Antes de encontrar el bug de arriba, perdí tiempo real (varias vueltas de diagnóstico, con
`System.AccessViolationException` nativas en `ProjectTool`, capturadas también en
`~/Library/Logs/DiagnosticReports/`) porque invoqué `gm-cli resourcetool eval "resource list"
"projectpath=$(pwd)/mi-proyecto.yyp"` — mezclando la sintaxis del binario `ResourceTool` sin
`gm-cli` (que sí usa argumentos `CLAVE=valor` como `projectpath=`, documentada en la vía de
emergencia de la Trampa 2) con la del propio `gm-cli resourcetool eval <comando> [project]`, cuyo
segundo argumento es una **ruta plana**, sin prefijo. La sintaxis correcta
(`gm-cli resourcetool eval "resource list" mi-proyecto.yyp`) funcionó a la primera, en dos
plantillas distintas (RPG Starter Pack y Blank Pixel Game), así que **no puedo sostener que
hubiera un bug de plantilla real** — abandoné RPG Starter Pack a mitad de este diagnóstico y no
volví a probarla con la sintaxis correcta, así que lo dejo dicho como lo que es: una ambigüedad
de la que la skill no advierte explícitamente (las dos convenciones de argumentos conviven sin una
nota que las diferencie), pero cuya causa fue mi propio error, no una mentira de la skill.

---

## Evidencia técnica

### Salida real de `gm-cli compile`

```
$ gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only
(sin salida)
$ echo $?
0
```

Salida completa (sin `--errors-only`, para que conste sin recortar), última pasada tras corregir
el `filePath` de los Included Files — sin ningún `WARNING`:

```
│  Compile Rooms...
│  finished..... 0 CC empty
│  finished..... 0 CC empty
│  Compile Objects...
│  finished.... 3 empty events
│  Compile Timelines...finished.
│  Compile Triggers...finished.
│  Compile Extensions...
│  Compile UI Layers...finished.
│  Global scripts...finished.
│  collapsing enums.
│  Final Compile...
│  Final Compile finished.
│  Saving IFF file... .../game.zip
│  [... Writing Chunk × 27, incluido DAFL sin avisos ...]
│  Stats : GMA : sp=8,au=0,bk=0,pt=0,sc=73,sh=0,fo=2,tl=0,ob=14,ro=7,da=2,ex=0,ma=6,...
│  Igor complete.
◆  Compilation finished
```

(«3 empty events» son eventos Step vacíos a propósito en `obj_escondite`, que es un *prop*
estático sin lógica propia — comentado así en el `.gml`, no un descuido.)

### `validar-proyecto.py --todo` (caza funciones inventadas que el compilador no detecta — Trampa 4)

```
49 archivos .gml · 751 llamadas analizadas · runtime del índice 2026.0.0.23

✓ Ninguna llamada a una función del runtime que no exista.
```

Sin ninguna «desconocida» listada tampoco (se listan solo con `--todo`, que se usó): cada símbolo
propio del proyecto (`dialogo_empezar`, `flag_leer`, `txt`, `calcular_final`...) está definido en
algún `.gml` del propio proyecto.

### `validar_grafo_narrativo.py` (13/12 §6.10, copiado sin modificar)

```
14 nodos, todos los destinos resuelven y todos son alcanzables.
Entradas declaradas: ['amanecer_decision', 'decision_esconder', 'orilla_hallazgo', 'reyes_hub', 'tobias_hub']
```

### Verificación del `.yy` de fuente (Trampa 5 — fuentes mudas)

`gm-cli resourcetool eval "font glyphlist name=fnt_dialogo"` → *«All table rows have Height =
23»* (glifos reales, no el `{}` vacío que deja `resourcetool` por sí solo). Las dos fuentes
(`fnt_dialogo`, Verdana 18pt; `fnt_titulo`, Verdana Bold 26pt) se hornearon con Pillow siguiendo
la técnica de `12 · 09` §0 Trampa 5 (partir de un `.yy` de fuente real con glifos poblados,
reescribir el bloque `"glyphs"`), cubriendo ASCII 32-126 más Latin-1 160-255 (á é í ó ú ñ Á É Í Ó
Ú Ñ ¿ ¡ ü completos). Verificado **visualmente**, sin abrir GameMaker: se generó el atlas, se
reconstruyó una frase completa píxel a píxel a partir de los propios metadatos de glifo (`x, y,
w, h, offset, shift`) exactamente como lo haría el motor, y se inspeccionó la imagen resultante —
el texto sale legible y con el baseline alineado.

### El paquete compilado, inspeccionado directamente (sin ejecutar el juego)

```
$ unzip -l .gmcache/build-gms2-mac-VM/output/game.zip | grep -E "es.json|nodos.json"
     6895  09-08-2026 12:37   assets/es.json
     9519  09-08-2026 12:37   assets/nodos.json
```

---

## El juego construido: ficha

- **Título**: *El Faro Silencioso*. Premisa (una frase, `13/12` §1.5): «Eres la guardiana de un
  faro que debe decidir si ayuda a un náufrago fugitivo antes de que llegue la patrulla.» Tema (la
  pregunta, no la respuesta): «¿Qué le debes a un desconocido que huye, y qué le debes a la ley
  que te da de comer?»
- **Estructura**: 3 actos (planteamiento → confrontación → resolución, `13/12` §2.1), cuello de
  botella en el acto II (todo converge en el hub de Reyes), abanico final en el III.
- **14 nodos de diálogo**, 95 claves de texto (diálogo + interfaz), **3 personajes con regla de
  habla propia**, **3 finales genuinamente distintos** por combinación de 6 flags de decisión
  (`escondio_a_tobias`, `crees_historia`, `le_dio_provisiones`, `mintio_a_reyes`,
  `conto_verdad_reyes`, `decidio_ayudar`).
- **Guardado de una ranura** que preserva flags, sala y posición del jugador
  (`scr_narrativa_guardado.gml` sobre `scr_save_load.gml`, copiado sin tocar de `06 - Assets y
  Scripts`).
- **Assets propios, ninguno un rectángulo**: 8 sprites (siluetas biped de dos personajes-tipo con
  paleta distinta por categoría + 2 fondos pintados a mano por código con Pillow, faro y amanecer)
  siguiendo la escalera de `12 · 09` §5.2 (Peldaño 1); 2 fuentes horneadas con glifos reales
  (Trampa 5). **Sin audio** — recorte explícito, ver checklist.
- **7 salas**: `rm_splash → rm_menu → rm_opciones → rm_intro → rm_faro → rm_epilogo →
  rm_creditos`, en ese orden de arranque (verificado con el método CLI-only de `12 · 09` §9.2:
  crear en el orden final, sin comando de reordenar).
- **14 objetos, 7 scripts**. Compila limpio, 751 llamadas validadas, grafo narrativo validado.

## Checklist maestro (`04 · 00`), punto por punto

| Punto | Estado | Nota |
|---|---|---|
| Splash saltable | ✅ | 3 s o cualquier tecla |
| Menú: Jugar/Continuar(cond.)/Opciones/Créditos/Salir | ✅ | «Continuar» solo si hay partida |
| Selección de nivel/capítulo | ➖ No aplica | Declarado: juego lineal de una sesión |
| Pantalla de opciones | ⚠️ Parcial | Solo velocidad de texto — sin audio que ajustar (ver abajo) |
| Intro/prólogo saltable | ✅ | ESC salta el prólogo entero |
| Pausa que congela el mundo | ⚠️ Parcial | `instance_deactivate_all` real, pero panel sólido en vez de capturar el frame (versión avanzada de `04/41` fuera de alcance, declarado en el propio `.gml`) |
| Confirmación "No" por defecto en acciones destructivas | ❌ No implementado | No se copió `scr_ui_confirmar.gml`; el guardado de ranura única se sobrescribe sin confirmar |
| Créditos → vuelta al menú | ✅ | |
| Bucle de juego con las zonas del género | ✅ | Una zona (`rm_faro`), suficiente para el alcance |
| HUD en Draw GUI | ✅ | Prompt de interacción y caja de diálogo, ambos en GUI |
| Guardado y carga | ✅ | Ranura única — decisión consciente, no ranuras múltiples |
| Ficha de ranura con miniatura | ➖ No aplica | Ranura única, sin selector |
| Muerte → Game Over | ➖ No aplica | Género narrativo sin *fail-state* de combate |
| Endgame: cierre final | ✅ | 3 finales en `rm_epilogo` |
| Todo el texto por `txt(clave)` | ✅ | 95 claves, cero literales de contenido |
| Sonido y música por escena | ❌ No implementado | Recorte explícito por alcance de tiempo — la escalera de `13/09` §8bis estaba disponible y no se usó |
| Funciona con teclado y mando | ❌ Solo teclado | Sin soporte de mando |
| Sin `show_debug_message` sobrante | ⚠️ Parcial | Quedan mensajes de diagnóstico (carga de guion, fallos de `txt()`); útiles pero no limpiados para un build de release |
| Icono, nombre, versión del build | ➖ No aplica | Paso de publicación, fuera del alcance de esta prueba |

Los recortes están dichos aquí, no omitidos en silencio, tal como exige la propia checklist.

## Veredicto final, sin adornos

**Un agente cualquiera con esta skill entrega hoy un juego con historia de verdad — no mecánicas
con texto de relleno —, siempre que lea `13 · 12` antes de escribir la primera línea de diálogo.**
La prueba no encontró un solo punto en el que la skill guiara peor la narrativa que la mecánica:
tiene teoría del oficio, un modelo de datos GML listo para adaptar, un validador de grafo
ejecutable, y avisa explícitamente de sus propios huecos (efectos en JSON, coste de ramificar) en
vez de fingir que no existen.

Lo que sí falló, y hay que arreglar, es operativo, no narrativo: el `filePath` de
`RESOURCE CREATE TYPE=includedfile` deja el archivo de datos fuera de `datafiles/`, en silencio,
y el propio `--errors-only` que la skill recomienda para el ciclo normal del agente **esconde el
aviso**. Sin la comprobación deliberada de compilar sin ese flag y de abrir el `.zip` compilado,
este informe habría dicho «compila limpio» sobre un juego mudo. Queda documentado aquí para que
`12 · 09` lo incorpore.

**Sobre la voz de los personajes, con la honestidad que pedía el encargo**: tienen voz propia y
pasan la prueba de tapar el nombre, pero son ~30 líneas por personaje — suficiente para demostrar
que la skill guía hacia una voz real y no hacia relleno, no suficiente para afirmar que sostendría
esa voz en un juego de horas. Eso lo decide el alcance de la prueba, no la skill.
