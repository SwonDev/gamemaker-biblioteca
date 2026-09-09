#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validar-integracion.py — ¿el código de la biblioteca encaja CONSIGO MISMO?

`validar-codigo-gml.py` comprueba que cada llamada a función sea real (no inventada).
`validar-compilacion-docs.py` comprueba que cada bloque ```gml compile SOLO. Ninguna de
las dos puede ver lo que solo aparece cuando DOS documentos, escritos por agentes
distintos en momentos distintos, resuelven el mismo problema (guardar partida, sacudir
la cámara…) sin saber que el otro existe. Ese fallo es estructuralmente invisible para
ambas: cada bloque, por separado, es perfectamente correcto. Solo revienta cuando se
juntan — que es justo lo que la auditoría `_indice/auditorias/r5-integracion.md` encontró
copiando código de verdad a un proyecto GameMaker real y compilando: 3 errores de
compilación reales y 2 excepciones reales en ejecución, con el código de cada documento
impecable por su cuenta.

Este script tiene TRES capas, de más barata a más cara:

  1. NOMBRES DUPLICADOS ENTRE DOCUMENTOS (estática, unos segundos, sin GameMaker).
     Extrae toda declaración de nivel superior (`function NOMBRE(...)`, `#macro NOMBRE`,
     `enum NOMBRE`) de los bloques ```gml de la biblioteca y de 06 - Assets y Scripts/, y
     agrupa por nombre. GameMaker compila TODOS los scripts de un proyecto en un único
     espacio de nombres: si dos documentos definen `camera_shake()` — con dos argumentos
     en uno, con uno en otro — GML solo detecta el choque cuando alguien pega los DOS
     bloques en el mismo proyecto real, no antes. Es exactamente lo que le pasó a
     `camera_shake()` (04 · 01/02 con dos argumentos, 04 · 15 con uno, y encima duplicada
     DENTRO del propio 04 · 15) y a `save_game()`/`load_game()`/`delete_save()` (04 · 04
     con su propio sistema sin argumentos, incompatible con el estándar de
     `06 - Assets y Scripts/scr_save_load.gml`) — los hallazgos #1 y #2 de la auditoría r5,
     y esta capa los habría cazado a los dos sin tocar GameMaker para nada.
     Clasificación (igual que el método de la auditoría):
       🔴 GRAVE   — mismo nombre, ARIDAD distinta → siempre rompe si ambos bloques
                     conviven en el mismo proyecto («duplicate script name»/«macro ya
                     definido»). Falla el script (exit 1).
       🟠 MEDIO   — misma aridad, CUERPO distinto → compila, pero una de las dos
                     implementaciones "gana" en silencio y la otra deja de aplicarse.
                     Aviso, no bloquea.
       🟡 MENOR   — firma Y cuerpo idénticos → duplicación literal, intencionada casi
                     siempre (un documento reutiliza tal cual el código de otro para ser
                     autocontenible). Aviso informativo salvo que ya esté documentada en
                     `EXCEPCIONES_DUPLICADOS` (ver más abajo), en cuyo caso ni eso.
     Los macros y enums no tienen aridad: CUALQUIER nombre repetido es 🔴 GRAVE — GameMaker
     rechaza un macro o un enum redeclarado aunque el valor sea idéntico byte a byte (no es
     como un `#define` de C, que tolera una redefinición igual). Así se cazó `#macro
     SAVE_VERSION` definido con OTRO significado en `04 · 04` y en `scr_save_load.gml`.

     MATIZ IMPORTANTE, confirmado con `gm-cli compile` en un proyecto real (no es una
     suposición): «un único espacio de nombres» es cierto para `#macro`/`enum` y para
     funciones de SCRIPT suelto, pero NO para una `function nombre(){}` declarada dentro
     del evento de un OBJETO — ahí GameMaker la trata como una variable de instancia, y
     dos objetos DISTINTOS pueden declarar la misma función sin chocar (es el patrón
     Subclass Sandbox de `13 · 23`, y `set_state()` en `objBattleManager` de `04 · 04`
     frente a `objBoard` de `04 · 07`). Solo colisionan de verdad los scripts sueltos
     entre sí, o el MISMO objeto recibiendo dos declaraciones (el caso real de
     `camera_shake()` en `objCamera`). Por eso esta capa rastrea, para cada función, el
     objeto más cercano nombrado en un comentario de cabecera antes de la declaración
     (ver `OBJETO_EN_CABECERA` más abajo) y solo compara ocurrencias del mismo ámbito.

  2. `global.X` LEÍDO SIN ESCRITURA VISIBLE (estática, con más ruido: AVISO, no fallo).
     Para cada `global.NOMBRE` que aparece SOLO en lecturas (`global.NOMBRE.campo`,
     `global.NOMBRE[i]`, como argumento…) en TODA la biblioteca — nunca en un
     `global.NOMBRE = …` liso — se avisa. No es un fallo automático porque hay falsos
     positivos legítimos: variables que se crean en `04 · 00` (el esqueleto que casi
     ningún documento cita porque se da por hecho) o en el propio motor de GameMaker.
     Es exactamente el patrón de los hallazgos #4 y #5 de la auditoría r5:
     `04 · 15` (Game feel y juice) LEÍA `global.feel.shake_enabled` en `camera_shake()` y
     `global.feel.hitstop_enabled` en `hit_stop()` sin que ningún punto del documento
     escribiera `global.feel = new FeelSettings()` — confirmado en ejecución real:
     "EXCEPCIÓN real al llamar camera_shake(): global variable name 'feel' index (…) not
     set before reading it." El primer golpe del juego colgaba. `validar-compilacion-docs.py`
     nunca lo habría visto: el bloque compila perfectamente solo, revienta al EJECUTARSE.
     Esta capa lo encuentra sin necesidad de `gm-cli run`: basta con que NINGÚN documento
     de la biblioteca contenga `global.feel = …` en ningún sitio.

  3. COMPILACIÓN CONJUNTA REAL (`--compilar`, cara: minutos, necesita `gm-cli` y GameMaker).
     Las dos capas de arriba son estáticas: pueden decir "esto debería chocar", pero solo
     compilar los documentos JUNTOS en un proyecto GameMaker real confirma que chocan de
     verdad — es la única prueba que no admite duda, y la que usó la propia auditoría r5
     (`gm-cli resourcetool eval` + `gm-cli compile` sobre un proyecto real). Monta un
     proyecto temporal con `gm-cli`, vuelca en scripts separados los bloques ```gml de un
     grupo de documentos que se citan mucho entre sí (ver `GRUPOS` más abajo — empezando
     por los nodos de mayor grado del grafo de reutilización: `scr_save_load.gml`,
     `04 · 15`, `13 · 12`, `GestorFichas`, tal y como propone la auditoría r5) y compila.
     No corre en cada `actualizar.py`: tarda minutos, no segundos, y necesita el
     instalador de GameMaker. Es un paso manual, documentado aquí y en `AGENTS.md`.

  4. FUNCIÓN DECLARADA EN EL EVENTO DE UN OBJETO, LLAMADA DESDE OTRO OBJETO (estática,
     unos segundos, AVISO no bloqueante). `04 · 19` definía `conductor_arrancar()`,
     `conductor_error()` y `conductor_juzgar()` dentro del `Create` de `obj_conductor`:
     compilaba limpio y reventaba en tiempo de ejecución («Variable X.Y(...) not set
     before reading it») en cuanto CUALQUIER otro objeto los llamaba sin cualificar — un
     `function nombre() {...}` declarado dentro de un evento queda ligado a `self` como
     una variable más de esa instancia, nunca como identificador global (eso solo pasa si
     vive en un script). Encontrado por `_indice/auditorias/r8-prueba-ritmo.md`, y al
     buscarlo a mano por el resto de la biblioteca aparecieron 7 recetas más con el mismo
     patrón (ver esa auditoría y el historial de `git log` de este fichero para el
     recuento completo). Esta capa reutiliza el mismo rastreo de ámbito de la capa 1
     (`indice_de_ambitos`/`ambito_en`) para saber, de cada `function` declarada con un
     objeto concreto en su cabecera, DÓNDE se llama después dentro del MISMO documento —
     nunca entre documentos distintos: son recetas independientes, y cruzarlas explotaría
     en falsos positivos por nombres genéricos reutilizados a propósito (`ejecutar`,
     `item`…), el mismo problema que ya evita `DIRS_INCLUIDAS` en la capa 1.
     Una llamada NO se avisa si:
       - ocurre dentro del MISMO ámbito donde se declaró (uso interno legítimo, el
         patrón *controller singleton*: `conductor_error()` llamada desde otro evento del
         propio `obj_conductor`);
       - está cualificada con punto (`obj_camera.set_target(...)`): quien escribe el
         código ya decidió explícitamente a qué instancia llama, no hay ambigüedad que
         `self` pueda resolver mal;
       - ocurre dentro de un `with (obj_x) { ... }` cuyo objetivo es el mismo objeto
         donde se declaró la función (`with (obj_transicion) { ir_a(rm_nivel_2); }`,
         `01 · 10` §9): dentro del bloque, `self` YA es esa instancia, así que la llamada
         sin cualificar es exactamente tan segura como si viviera en un script.
     Lo que esta capa NO puede verificar solo con texto, y por eso es AVISO y no bloqueo:
     la herencia con `event_inherited()` (el patrón *Subclass Sandbox* de `13 · 23`, o
     `obj_enemigo`/`obj_jugador` heredando de `obj_entidad` en `01 · 09`) hace que una
     función declarada en el padre SÍ sea alcanzable sin cualificar desde el hijo — pero
     detectarlo con fiabilidad exigiría entender la jerarquía real de objetos del
     proyecto, no solo grep sobre texto. Los casos ya verificados a mano quedan en
     `EXCEPCIONES_LLAMADAS_EXTERNAS`, con la misma disciplina que las otras dos listas de
     excepciones de este fichero: si aparece un caso NUEVO no listado, revísalo a mano
     antes de silenciarlo — la regla dura de siempre es que, ante la duda, es bug.

FRONTERA: LO QUE ESTE SCRIPT NO PUEDE VER, CON EJEMPLOS REALES
    Las tres capas de arriba comparan NOMBRES y SINTAXIS: mismo identificador, misma
    aridad, misma global sin escribir, mismo proyecto que no compila. Ninguna de las tres
    entiende SIGNIFICADO ni COMPORTAMIENTO. La prueba `r7-prueba-gestion.md` (juego de
    gestión completo, granja + tienda, el perfil que más sistemas entrelaza) construyó un
    proyecto real con este código y encontró SIETE incompatibilidades reales entre
    documentos — este script, ejecutado sobre la biblioteca completa antes y después,
    no cazó NINGUNA de las siete. Quedan aquí como ejemplo permanente de lo que
    "sale limpio" no garantiza — que nadie se confíe con un 0 de salida:

      1. DOS NOMBRES PARA EL MISMO CONCEPTO (semántica, no sintaxis). `13 · 05 §3.5k`
         leía y escribía `global.monedas`; `04 · 04 §5.2` guarda el oro en
         `Inventory.oro`. La capa 2 pregunta «¿se escribe esta global EN ALGÚN SITIO de
         la biblioteca?» — y `global.monedas` SÍ se escribía, dentro del propio
         documento que la leía. El fallo no es «variable sin escribir»: es «dos
         variables MODELAN EL MISMO CONCEPTO sin saberlo». Ninguna capa compara
         conceptos, solo nombres. (Corregido: ver el aviso de §3.5k en `13 · 05`.)

      2-3. DOS MODELOS DE DATOS INCOMPATIBLES, SIN NI UN NOMBRE EN COMÚN. El inventario
         en cuadrícula de `13 · 05 §3.5e` (`objetos[]`) y el `Inventory` de `04 · 04
         §5.2` (`slots[]`) resuelven "un inventario" con vocabularios que no comparten
         ni un identificador — la capa 1 solo dispara ante un NOMBRE repetido con
         aridad o cuerpo distinto; aquí no hay ningún nombre que choque, así que no
         tiene ninguna señal que comparar. Mismo caso con las dos "tiendas" que no se
         citaban (`13 · 05 §3.5k` de interfaz, `TiendaNPC` de `13 · 01 §9.8` de datos):
         `tienda_comprar()` frente a `TiendaNPC.vender_a_jugador()`, cero solapamiento
         léxico. Es, con diferencia, la incompatibilidad más difícil de cazar de forma
         estática: dos soluciones al mismo problema que no comparten ni una palabra.

      4. UN BUG DE LÓGICA DE NEGOCIO DENTRO DE UNA FUNCIÓN SINTÁCTICAMENTE PERFECTA.
         `cultivo_plantar()` (`04 · 45 §5.3`) compilaba limpio y nunca descontaba la
         semilla del inventario del jugador — planta gratis. Ninguna capa audita QUÉ
         hace el cuerpo de una función, solo que exista y que su firma no choque.

      5. UN ACOPLAMIENTO IMPLÍCITO CON UN ASSET, NO CON CÓDIGO. `panel_dibujar(_spr,
         ...)` (`13 · 05 §3.4`) exige un sprite con nine slice activado que ningún
         documento avisaba que hacía falta crear. No es un símbolo de GML que
         `validar-codigo-gml.py` pueda validar, ni una colisión de nombres: es un
         requisito de PRODUCCIÓN DE ARTE oculto dentro de una firma de función.

      6-7. BUGS QUE SOLO EXISTEN EN EJECUCIÓN, NUNCA EN COMPILACIÓN. `Inventory.
         deserialize()` (`04 · 04 §5.2`) revienta con «Variable <unknown_object>.
         deserialize(...) not set before reading it» si es la primera vez que el
         proceso toca ese constructor — un `static` de un constructor no existe como
         miembro accesible hasta el primer `new`, un comportamiento de GML que ningún
         documento de la biblioteca mencionaba antes de esta corrección. Y
         `global.nombres_estacion` (`04 · 45 §5.2`) se quedaba sin rellenar en la ruta
         de «Continuar» porque vivía dentro del Create de un objeto que solo se crea
         al empezar partida nueva. La capa 3 (`--compilar`) es la única que toca
         GameMaker de verdad — pero **solo llama a `gm-cli compile`, nunca a
         `gm-cli run`** (léase el código: el `cmd` que arma `_compilar_grupo()` es
         siempre `compile`). Los dos bugs compilan limpio, exit 0, las dos veces:
         solo revientan JUGANDO. Ninguna cantidad de análisis estático los encuentra;
         hace falta ejecutar el juego y pulsar los botones, que es exactamente lo que
         hizo la prueba r7 y lo que este script, por diseño, no hace.

    EN UNA FRASE: capas 1-2 cazan SÍMBOLOS que chocan o que nadie escribe; capa 3 caza
    que un GRUPO de documentos compile junto. Ninguna de las tres caza que dos símbolos
    DISTINTOS signifiquen lo mismo, que un modelo de datos sea incompatible con otro sin
    colisionar, que una función tenga un bug de lógica, que una firma dependa de un
    asset no declarado, o que algo solo falle EJECUTANDO el juego. Para eso no hay
    atajo estático: hace falta construir algo real con las piezas y jugarlo — el método
    de las auditorías `r5-integracion.md`/`r7-prueba-gestion.md`, no de este script.

    ¿MERECE LA PENA UNA CUARTA CAPA SEMÁNTICA (detectar automáticamente pares como
    monedas/oro o vida/salud)? Se evaluó y la respuesta es NO, por diseño, no por
    pereza:
      - La única heurística estáticamente viable —una lista de sinónimos conocidos a
        mano («monedas» ~ «oro», «vida» ~ «salud»)— solo detecta pares que YA SE
        CONOCEN, es decir, pares que ya se han encontrado y corregido. Su valor
        prospectivo (encontrar el PRÓXIMO par, el que nadie ha visto todavía, que es
        el problema real) es cero: es una lista de "cosas que ya arreglamos",
        disfrazada de detector.
      - Una heurística más amplia (dos `global.X` de nombre distinto que aparecen en
        documentos que se citan entre sí) explota en falsos positivos: el patrón
        "Ver también" cruza CIENTOS de pares de documentos en esta biblioteca a
        propósito (es la arquitectura, no un accidente — `AGENTS.md` §3 bis lo pide
        expresamente), y la inmensa mayoría de esos pares de globals son conceptos
        genuinamente distintos que conviven sin problema (`global.dia_actual` y
        `global.tiempo_anterior`, `global.stock` y `global.inventario`…). Sin
        entender significado, no hay forma barata de separar «duplicado real» de
        «dos cosas que no tienen nada que ver y solo coinciden en aparecer cerca».
      - Una herramienta ruidosa se acaba ignorando — es la advertencia que motivó
        esta misma investigación. Diluir la señal limpia de las capas 1-2 (que SÍ
        cazan colisiones reales, con cero ruido hasta ahora) con avisos de baja
        confianza sería peor que no tener la capa: erosiona la confianza en las dos
        que sí funcionan.
    La detección de este tipo de fricción sigue siendo trabajo de REVISIÓN — humana o de
    un agente que construya algo real con las piezas y lo ejecute (el método de r5/r7),
    no de un script estático. Si en el futuro se automatiza, que sea como una prueba de
    integración que COMPILA Y EJECUTA un proyecto de ejemplo que cruza sistemas (capa 3
    ya sienta la base de "montar un proyecto real con gm-cli"), nunca como un matcher de
    nombres por similitud textual.

USO
    python3 _indice/validar-integracion.py              # capas 1, 2 y 4 (unos segundos)
    python3 _indice/validar-integracion.py --compilar    # + capa 3, TODOS los grupos
    python3 _indice/validar-integracion.py --compilar --grupo guardado
    python3 _indice/validar-integracion.py --compilar --keep   # no borra el proyecto temporal

Sale con 0 si no hay ninguna duplicación 🔴 GRAVE (capas 1 y 2 nunca bloquean por sí
solas más que por eso; capa 4 avisa pero no bloquea, ver su docstring) y, con
`--compilar`, si además todos los grupos compilan juntos.
"""
import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

# Windows: en cuanto la salida no es una consola interactiva (pipes, «> archivo», o el
# propio actualizar.py capturando la salida de este script vía subprocess), sys.stdout
# usa la página de códigos ANSI del sistema en vez de UTF-8 — y los símbolos ✗/⚠/→/…
# de este código no caben ahí: UnicodeEncodeError a mitad de ejecución. No verificado
# en Windows de verdad; aplica la solución estándar de Python 3.7+ (PEP 528 cubre la
# consola interactiva sola, no pipes ni redirecciones).
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IND = os.path.join(RAIZ, "_indice")


def _cargar_validar_compilacion_docs():
    """Importa validar-compilacion-docs.py (guion en el nombre → no es un módulo
    normal) para reutilizar SU extracción y clasificación de bloques: ya sabe
    distinguir GML real de pseudocódigo/fragmentos ilustrativos (elipsis,
    plantillas `<...>`, citas `>` de Markdown, `case` sueltos de switches
    distintos, herencia de un padre no definido en el mismo bloque…) sin
    reinventar esa lógica aquí. Lo que SÍ se evita a propósito es su
    `envolver()`: esa función mete cada bloque en un IIFE `(function(){...})()`
    y renombra `#macro`/`enum`/`function` por bloque JUSTO para que dos
    bloques con el mismo nombre NO choquen entre sí — que es exactamente lo
    contrario de lo que la capa 3 necesita comprobar."""
    ruta = os.path.join(IND, "validar-compilacion-docs.py")
    spec = importlib.util.spec_from_file_location("validar_compilacion_docs", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# A diferencia de validar-codigo-gml.py (que sí escanea TODA la biblioteca: ahí solo
# importa si un nombre de función es real), esta comprobación solo tiene sentido sobre
# el código pensado para COMBINARSE en un proyecto real: recetas de género, diseño y
# producción, y los scripts base de 06/. `01 - Fundamentos`, `05 - Referencia`,
# `07 - Ecosistema`, `08 - Referencia GML completa` y `10 - Cursos` están llenos de
# fragmentos pedagógicos aislados y deliberadamente redundantes (`Enemigo`, `item`,
# `hijo`, `padre`, `f`, `ejecutar`… nombres de ejemplo repetidos a propósito para
# explicar un concepto de lenguaje) que un agente nunca copia dos veces al mismo
# proyecto — escanearlos solo produce ruido que ahoga los hallazgos reales. Es
# exactamente el alcance que usó la propia auditoría r5 (ver su método, paso 2).
DIRS_INCLUIDAS = {"04 - Recetas por género", "13 - Diseño y producción de videojuegos",
                   "06 - Assets y Scripts"}

# La capa 4 (función declarada en un evento, llamada desde OTRO objeto) es distinta: es
# un análisis DENTRO de cada documento, nunca entre documentos — así que el problema de
# "nombres de ejemplo repetidos a propósito" de arriba no se aplica (`item` en el
# documento A nunca se compara contra `item` en el documento B). Puede permitirse un
# alcance mucho más amplio sin ruido extra: toda la biblioteca de contenido propio,
# excepto el espejo del manual oficial (`09`, no es código nuestro), el código
# descargado de terceros (`11`, no son recetas de esta biblioteca) y los índices.
DIRS_INCLUIDAS_LLAMADAS = {
    "01 - Fundamentos", "02 - Novedades 2026", "03 - Cursos (YouTube)",
    "04 - Recetas por género", "05 - Referencia", "06 - Assets y Scripts",
    "07 - Ecosistema", "08 - Referencia GML completa", "10 - Cursos en español",
    "12 - Utilidades e integraciones", "13 - Diseño y producción de videojuegos",
}

FENCE = re.compile(r"```gml\n(.*?)```", re.S)


# ---------------------------------------------------------------------------
# Duplicaciones DELIBERADAS: firma y cuerpo idénticos, copiadas a propósito para que
# cada documento sea autocontenible (no un enlace a mitad de lectura). Confirmadas
# a mano en la auditoría r5 (hallazgo #10) — no son un bug, así que capa 1 no las
# marca como problema mientras el conjunto de documentos siga siendo EXACTAMENTE
# este. Si aparece un TERCER documento con el mismo nombre, o si dos de estos
# documentos empiezan a divergir en el cuerpo, la excepción deja de aplicar y capa 1
# vuelve a avisar — es a propósito: una excepción que nunca caduca es la manera más
# fácil de que un duplicado real se cuele sin que nadie lo note.
# ---------------------------------------------------------------------------
EXCEPCIONES_DUPLICADOS = {
    "AzarReproducible": {
        "13 - Diseño y producción de videojuegos/10 - Testing y QA.md",
        "13 - Diseño y producción de videojuegos/21 - Balance por simulación - Monte Carlo, Machinations y estrategias dominantes.md",
    },
    "calcular_dano": {
        "13 - Diseño y producción de videojuegos/10 - Testing y QA.md",
        "13 - Diseño y producción de videojuegos/21 - Balance por simulación - Monte Carlo, Machinations y estrategias dominantes.md",
    },
    # NOTA sobre `set_state` (04 · 04 vs 04 · 07): comprobado a mano, NO son cuerpos
    # idénticos — 04 · 04 hace trabajo extra al entrar en `enemy_turn` — así que NO
    # entra aquí como excepción: capa 1 lo marca 🟠 medio correctamente (misma aridad,
    # cuerpo distinto) y así debe quedarse. `tablero_nuevo` (04 · 31 → renombrada
    # `tres_en_raya_tablero_nuevo`) y `simular_combate` (04 · 44 → `equipos_simular_combate`)
    # de la lista de vigilancia de la auditoría r5 se resolvieron renombrando, no aquí.
    # NetMsg y PlayerState NO son duplicados accidentales: son un enum que CRECE a lo
    # largo de varios documentos, con cada bloque posterior mostrando el conjunto
    # COMPLETO (base + lo añadido) y una nota explícita de "esto REEMPLAZA al de
    # arriba, no lo declares dos veces" — porque GameMaker no permite ampliar un enum
    # ya declarado, así que la única forma honesta de documentarlo es repetir el
    # enum entero en cada parada. Un grep no puede distinguir eso de un choque real;
    # por eso está aquí, con la razón escrita, en vez de silenciado sin más.
    "NetMsg": {
        "04 - Recetas por género/14 - Multijugador.md",
        "04 - Recetas por género/54 - Metajuego transversal - logros, galería, speedrun y espectador.md",
    },
    "PlayerState": {
        "04 - Recetas por género/01 - Plataformas 2D.md",
        "04 - Recetas por género/37 - Traversal en plataformas - pendientes, paredes, escaleras y bordes.md",
    },
    # BattleState SÍ es un choque real si conviven — pero es a propósito: 04 · 04 es el
    # "mínimo viable" (inglés, 6 estados) que su propio texto dice sustituir por el
    # sistema completo de 04 · 35 (español, con orden de turnos e IA) en cuanto haga
    # falta más que "el enemigo siempre ataca al mismo objetivo". Ambos documentos ya
    # avisan de que son alternativas, no piezas que se combinan — ver 04 · 04 §5.6.
    "BattleState": {
        "04 - Recetas por género/04 - RPG _ Action RPG.md",
        "04 - Recetas por género/35 - Combate por turnos y táctico en rejilla.md",
    },
    # camera_shake_basico ya NO está aquí a propósito: capa 3 confirmó con gm-cli
    # compile que, aunque el cuerpo es idéntico, SÍ choca de verdad si 04 · 01 y
    # 04 · 02 acaban en el mismo proyecto (las dos usan el nombre de objeto
    # "objCamera") — se cerró renombrando la de 04 · 02 a `camera_shake_basico_td`
    # en vez de con una excepción. Ejemplo de por qué capa 3 hace falta: capa 1
    # por sí sola lo había clasificado como 🟡 menor (firma y cuerpo iguales) y
    # esa excepción lo habría silenciado para siempre sin capa 3.
    # banco_siguiente/variacion_ganancia/variacion_tono: utilidades pequeñas que las
    # DOS implementaciones independientes de audio (ver el aviso en
    # 06/scr_audio.gml y en 13 · 09) resolvieron igual sin querer. El resto de esa
    # familia (mezcla_aplicar, sonar_en…) SÍ diverge y se queda como aviso 🟠 visible
    # a propósito: es el choque grande, sin reconciliar, documentado en ambos sitios.
    "banco_siguiente": {
        "06 - Assets y Scripts/scr_audio.gml",
        "13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md",
    },
    "variacion_ganancia": {
        "06 - Assets y Scripts/scr_audio.gml",
        "13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md",
    },
    "variacion_tono": {
        "06 - Assets y Scripts/scr_audio.gml",
        "13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md",
    },
}


# ---------------------------------------------------------------------------
# `global.X` LEÍDO SIN ESCRIBIRSE EN LA BIBLIOTECA — pero NO es un bug.
#
# La auditoría 2026-09 clasificó a mano los 59 avisos que esta capa emitía ese día
# (ver `_indice/auditorias/` para el detalle completo). De esos 59: 42 eran BUGS
# REALES (arreglados: se instanció la global donde correspondía, casi siempre en
# el Create del objeto que va primero, siguiendo el patrón ya establecido por
# `global.feel` en 04 · 15) y 17 caían en dos categorías que NO son bugs:
#
#   1. CONVENCIÓN DEL LECTOR — la global es evidentemente del PROYECTO DE CADA
#      LECTOR (su puntuación, su flag de consentimiento, el layout de tiles de SU
#      room), usada como EJEMPLO de algo que cada juego define a su manera. La
#      biblioteca no puede rellenar ese hueco sin inventar contenido que no le
#      corresponde. Casi siempre delatado por uno de estos rasgos: (a) el propio
#      texto dice explícitamente "esto es tuyo, ajústalo" (a veces en una cita
#      `>` FUERA de un bloque ```gml, que por diseño esta capa no cuenta como
#      escritura real — ver `mascara_solo_fences`); (b) es una de varias claves
#      de ejemplo intercambiables dentro de un contrato ya declarado como "struct
#      cualquiera"; (c) aparece en un documento de referencia/interoperabilidad
#      que ilustra CÓMO usar una API, no QUÉ sistema construir.
#   2. DEFINIDA FUERA DEL ALCANCE ESCANEADO — se escribe de verdad en un
#      documento real (con su propio `global.X = …` en un bloque ```gml), pero
#      vive fuera de `DIRS_INCLUIDAS` (por ejemplo en `01 - Fundamentos/`), que
#      esta capa excluye a propósito para no ahogarse en el código pedagógico de
#      esas carpetas (ver el comentario de `DIRS_INCLUIDAS`, arriba). La
#      remisión al documento real ya está en el texto que lee la global.
#
# Cada entrada de abajo es una decisión tomada leyendo el documento a mano, no un
# silenciador genérico: si en el futuro esa MISMA global empieza a leerse también
# en un documento nuevo que NO está en `docs`, la excepción NO cubre ese caso —
# `docs` es la lista exacta de sitios donde ya se revisó y se decidió que no era
# bug, igual que `EXCEPCIONES_DUPLICADOS` de arriba. Si te encuentras añadiendo
# una entrada aquí para acallar un aviso sin haber podido justificar por qué es
# imposible que sea un bug real, es casi seguro que SÍ es un bug real: arréglalo
# en el documento en vez de silenciarlo (la regla dura de la auditoría: ante la
# duda, es bug, porque el coste de arreglarlo es bajo y el de dejarlo pasar es
# alto — ya se demostró con `global.feel`, `global.gestor_jugador` y una docena
# de casos más en esta misma auditoría).
# ---------------------------------------------------------------------------
EXCEPCIONES_GLOBALS_LECTOR = {
    "tilemap_terreno": {
        "docs": {
            "04 - Recetas por género/09 - Survival y crafting.md",
            "04 - Recetas por género/51 - Colonia y constructor de bases - trabajadores autónomos.md",
        },
        "motivo": "El ID de la capa de tiles del terreno depende del layout de la room de CADA "
                  "proyecto (nombre de capa, room de mundo). 04 · 09 §5.4 lo advierte en una cita "
                  "`>` explícita, con la línea exacta a copiar (`layer_tilemap_get_id(...)`) — "
                  "a propósito FUERA de un bloque ```gml: no es código de la biblioteca, es la "
                  "instrucción de qué escribir en tu Room Start. 04 · 51 reutiliza la misma "
                  "convención con remisión explícita a 04 · 09.",
    },
    "hp": {
        "docs": {"04 - Recetas por género/17 - Interoperabilidad con la web (HTML5).md"},
        "motivo": "Placeholder de ejemplo en guardar_web() (§ interoperabilidad JS↔GML): "
                  "'lo que sea que tu juego trackee' al serializar el estado para localStorage, "
                  "no un sistema de vida que la biblioteca deba proporcionar.",
    },
    "nivel": {
        "docs": {"04 - Recetas por género/17 - Interoperabilidad con la web (HTML5).md"},
        "motivo": "Mismo ejemplo que 'hp' en guardar_web(): placeholder del progreso de CADA "
                  "juego, no un sistema de niveles de la biblioteca.",
    },
    "nombre": {
        "docs": {"04 - Recetas por género/17 - Interoperabilidad con la web (HTML5).md"},
        "motivo": "Ejemplo de § 'Comunicarte con tu propio servidor' (POST HTTP): la identidad "
                  "del jugador de CADA proyecto, no algo que la biblioteca defina.",
    },
    "puntos": {
        "docs": {
            "04 - Recetas por género/17 - Interoperabilidad con la web (HTML5).md",
            "04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md",
        },
        "motivo": "Marcador de 'donde sea que viva tu puntuación': ejemplo de POST HTTP en 04 · 17 "
                  "y de subida a un leaderboard de Steam en 04 · 20. Ningún documento de la "
                  "biblioteca define un sistema de puntuación canónico al que redirigir estos dos.",
    },
    "save_logger": {
        "docs": {"06 - Assets y Scripts/scr_save_load.gml"},
        "motivo": "Hook opcional documentado en la cabecera del propio script y protegido con "
                  "variable_global_exists('save_logger') && is_method(...) en su única lectura: "
                  "sin definirlo, el script se comporta exactamente igual (solo show_debug_message).",
    },
    "telemetria_consentida": {
        "docs": {"13 - Diseño y producción de videojuegos/01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md"},
        "motivo": "Guardado con variable_global_exists() antes de leerse: sin consentimiento "
                  "explícito, telemetria_enviar() no envía nada por defecto. La pantalla de "
                  "consentimiento y cómo se guarda la respuesta son responsabilidad legal de "
                  "cada juego, no un sistema GDPR genérico que la biblioteca deba imponer.",
    },
    "datos_partida_recolectar": {
        "docs": {"13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md"},
        "motivo": "Hook opcional del manejador de caídas (caidas_instalar_manejador), guardado con "
                  "variable_global_exists() && is_method() antes de llamarse: cada proyecto "
                  "recolecta los datos de su guardado de emergencia de forma distinta.",
    },
    "clima": {
        "docs": {"13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md"},
        "motivo": "Una de varias claves de ejemplo del struct `_hechos` que consume "
                  "BancoBarks.elegir() — el propio texto declara ese struct como 'cualquiera'. "
                  "No hay ningún sistema de clima en el resto de la biblioteca al que remitir.",
    },
    "zona_actual": {
        "docs": {"13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md"},
        "motivo": "Mismo struct de ejemplo `_hechos` que 'clima', misma justificación: clave "
                  "intercambiable de un contrato 'struct cualquiera', no un sistema que falte.",
    },
    "paredes": {
        "docs": {"13 - Diseño y producción de videojuegos/13 - Matemáticas aplicadas al juego.md"},
        "motivo": "Ejemplo de uso de cortan_segmentos() (función matemática pura) en un documento "
                  "de referencia de matemáticas de juego: la lista de segmentos de pared es del "
                  "sistema de colisión de CADA proyecto, no algo que la biblioteca deba instanciar.",
    },
    "xp_total": {
        "docs": {"13 - Diseño y producción de videojuegos/13 - Matemáticas aplicadas al juego.md"},
        "motivo": "Ejemplo de uso de nivel_desde_xp() (función pura, recibe la XP como parámetro): "
                  "la XP acumulada es del sistema de progresión de CADA juego (13 · 01/13 · 16, "
                  "que no usan ni escriben este nombre), no un dato que la biblioteca deba dar.",
    },
    "gamepad_slot": {
        "docs": {"13 - Diseño y producción de videojuegos/19 - Cámaras de juego - encuadre, seguimiento y control.md"},
        "motivo": "Se escribe de verdad en 01 · 12 — Input (`obj_game · Create` y su `Async - "
                  "System`), fuera de `DIRS_INCLUIDAS` a propósito (esa carpeta es Fundamentos, "
                  "no recetas/diseño/scripts). La remisión ya está en el texto de 13 · 19.",
    },
}


# ---------------------------------------------------------------------------
# Capa 4 — función declarada en el evento de un objeto, llamada desde OTRO objeto sin
# `with()` ni cualificación de punto. Verificados a mano, uno por uno, los únicos casos
# de la biblioteca donde eso pasa y NO es un bug: herencia real con `event_inherited()`.
# Misma disciplina que las dos listas de arriba: si aparece un nombre nuevo aquí sin que
# puedas justificar por qué la instancia SIEMPRE tiene la función (jerarquía de objetos
# verificada, no una suposición), es casi seguro que es un bug real — arréglalo en el
# documento, no lo silencies aquí.
# ---------------------------------------------------------------------------
EXCEPCIONES_LLAMADAS_EXTERNAS = {
    # Subclass Sandbox (13 · 23 §3.3): obj_habilidad_dash/obj_habilidad_gancho llaman a
    # empujar()/invocar_particulas()/reproducir_sonido()/ejecutar() declaradas en el
    # Create de obj_habilidad_base — y cada hija llama a `event_inherited();` en su
    # propio Create, así que las cuatro SÍ son variables de instancia de la hija también,
    # no solo del padre. Verificado leyendo las tres declaraciones de objeto del
    # documento: las tres llaman a event_inherited().
    "empujar": {"13 - Diseño y producción de videojuegos/23 - Catálogo de patrones en GML.md"},
    "invocar_particulas": {"13 - Diseño y producción de videojuegos/23 - Catálogo de patrones en GML.md"},
    "reproducir_sonido": {"13 - Diseño y producción de videojuegos/23 - Catálogo de patrones en GML.md"},
    "ejecutar": {"13 - Diseño y producción de videojuegos/23 - Catálogo de patrones en GML.md"},
    # 01 · 09 §13: obj_enemigo (y sus hijos obj_slime/obj_murcielago/obj_jefe) y
    # obj_jugador heredan recibir_danio()/al_morir() de obj_entidad por la misma vía:
    # cada uno llama a event_inherited() en su propio Create. obj_jugador se corrigió
    # el 2026-09-08 para dejarlo explícito en el árbol de herencia del documento — antes
    # de esa corrección, la instancia sí revenía (mismo bug, verificado leyendo el texto
    # anterior a la corrección; no era una excepción legítima hasta que se arregló).
    "recibir_danio": {"01 - Fundamentos/09 - Instancias, objetos y herencia.md"},
    "al_morir": {"01 - Fundamentos/09 - Instancias, objetos y herencia.md"},
    # 04 · 12 §2: objPlayerCar/objAICar son hijos de objVehicle (jerarquía en §2) y
    # objAICar llama a event_inherited() en su Create — leer_terreno() (declarada en el
    # Create de objVehicle, corregido el 2026-09-08 para decir explícitamente
    # "Create (añadir)" y evitar que se confunda con el Step) queda heredada.
    "leer_terreno": {"04 - Recetas por género/12 - Carreras y vehículos.md"},
}


# ---------------------------------------------------------------------------
# Capa 1 y 2 — extracción estática
# ---------------------------------------------------------------------------

def enmascarar(texto):
    """Sustituye comentarios y el CONTENIDO de las cadenas por espacios, conservando la
    longitud y los saltos de línea exactos del original — así cualquier posición de
    coincidencia en el texto enmascarado sigue siendo la línea real del documento.
    Evita que un `{`/`}` dentro de una cadena, o un nombre de función mencionado dentro
    de un comentario, se cuenten como código de verdad."""
    out = []
    i, n = 0, len(texto)
    while i < n:
        c = texto[i]
        if c == "/" and texto[i:i + 2] == "//":
            j = texto.find("\n", i)
            j = n if j == -1 else j
            out.append(" " * (j - i))
            i = j
        elif c == "/" and texto[i:i + 2] == "/*":
            j = texto.find("*/", i + 2)
            j = n - 2 if j == -1 else j
            seg = texto[i:j + 2]
            out.append(re.sub(r"[^\n]", " ", seg))
            i = j + 2
        elif c == '"':
            j = i + 1
            while j < n and texto[j] != '"':
                j += 2 if texto[j] == "\\" else 1
            j = min(j + 1, n)
            seg = texto[i:j]
            out.append(re.sub(r"[^\n]", " ", seg))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def mascara_solo_fences(texto):
    """Todo lo que hay FUERA de los bloques ```gml se sustituye por espacios (conserva
    saltos de línea): así una mención en prosa a `global.feel` o a `camera_shake(` —
    fuera de un bloque de código real— no cuenta como código."""
    resultado = list(re.sub(r"[^\n]", " ", texto))
    for m in FENCE.finditer(texto):
        ini, fin = m.start(1), m.end(1)
        resultado[ini:fin] = texto[ini:fin]
    return "".join(resultado)


def contar_parametros(texto):
    texto = texto.strip()
    if not texto:
        return 0
    profundidad = 0
    n = 1
    for ch in texto:
        if ch in "([{":
            profundidad += 1
        elif ch in ")]}":
            profundidad -= 1
        elif ch == "," and profundidad == 0:
            n += 1
    return n


def normalizar_cuerpo(texto):
    return re.sub(r"\s+", " ", texto).strip()


# ---------------------------------------------------------------------------
# ÁMBITO de una función: confirmado con gm-cli compile en un proyecto real (no es
# una suposición). Dos `function nombre(){}` colisionan («duplicate script name»)
# SOLO si ambas viven en un script suelto (project-wide) o en el MISMO objeto —
# es justo lo que demostró la auditoría r5 pegando 04·02 y 04·15 en el MISMO
# `objCamera`. Pero declaradas dentro del Create de DOS OBJETOS DISTINTOS —el
# patrón Subclass Sandbox de `13 · 23` (ejecutar() en obj_habilidad_dash y en
# obj_habilidad_gancho), o `set_state()` en objBattleManager (04 · 04) y objBoard
# (04 · 07)— NO colisionan: GameMaker las trata como variables de instancia
# distintas, una por objeto. Verificado con `gm-cli compile` (exit 0) sobre un
# proyecto real con dos objetos hermanos que definen `ejecutar()` cada uno con
# `event_inherited()`, y con otro par de objetos NO emparentados que definen
# `set_state()` cada uno. Por eso capa 1 rastrea, para cada función, el objeto
# más cercano nombrado en un comentario de cabecera («// objX — Evento», «/// obj_x
# · Create»…) ANTES de la declaración, y solo compara aridad/cuerpo entre
# ocurrencias que comparten ámbito (el mismo objeto, o ninguno — scripts sueltos).
# ANCLADO al principio de la línea (tras el marcador `//`/`///` y adornos típicos de
# separador: espacios, guiones, `═`/`─` de caja, flechas, viñetas, `=`) — a propósito,
# NO en cualquier parte de la línea. Encontrado en vivo el 2026-09-08 preparando la
# capa 4 (ver más abajo): con `\b...\b` sin anclar, un comentario de una sola línea que
# solo MENCIONA un objeto de pasada — `// El retorno a 1.0 es automático por el lerp de
# objTime` (04 · 15), en mitad del cuerpo de `time_slow()` — se leía como si abriera el
# ámbito «objTime», y la declaración de `time_delta()` que venía después, en la MISMA
# `scr_time`, heredaba ese ámbito falso en vez de quedarse en `None` (script). Anclarlo
# exige que el nombre del objeto sea la PRIMERA palabra de la cabecera, que es como se
# escriben las cabeceras reales en toda la biblioteca (`/// obj_conductor · Create`,
# `// objCamera — Create`, `// ═══════════ obj_entidad (Create) — PADRE BASE ═══════`),
# y ya no se confunde con una mención al pasar en mitad de una frase.
#
# SEGUNDO refinamiento, mismo día: anclar al principio de línea no basta cuando el
# nombre del objeto cae al principio de una línea de CONTINUACIÓN de un `@desc` largo
# partido en varias líneas `///` — cada una empieza igual de "al principio de línea"
# que una cabecera real. Caso real: `estructura_derrumbar()` (04 · 51) tiene
# `/// @desc Destruye y suelta... — mismo patrón de\n///       objItemDrop que 04 · 09
# §5.2 romper()...`: la SEGUNDA línea, sangrada, empieza con `objItemDrop` tras solo
# espacios — pasaba el ancla de arriba igual que una cabecera real. La señal que sí
# distingue una cabecera real de una mención cualquiera (anclada o no): en TODA cabecera
# real de esta biblioteca, el nombre del objeto va seguido de inmediato — con, como
# mucho, un espacio de por medio — de un separador de etiqueta (`·`, `—`, `-`, `(`, `:`);
# una mención dentro de una frase sigue con una palabra normal («que», «no», «es»…) o
# con el fin de línea. Por eso exige ese separador nada más terminar el nombre.
OBJETO_EN_CABECERA = re.compile(
    r"^[ \t]*/{2,3}[ \t\-─═►▶·•=_]*(obj(?:_\w+|[A-Z]\w*))(?=[ \t]*[·—:(-])"
)
SCRIPT_EN_CABECERA = re.compile(r"\bscr_\w+\b")
LINEA_COMENTARIO = re.compile(r"^[ \t]*//[^\n]*$", re.M)


def indice_de_ambitos(original):
    """Lista ordenada de (posición, objeto_o_None) — cada comentario de cabecera
    que nombra un obj_X/objX abre ese ámbito; uno que nombra un scr_X (o cualquier
    otro comentario sin objeto) lo cierra de vuelta a "sin ámbito" (script/global).

    Cada bloque ```gml NUEVO empieza sin heredar el ámbito del bloque anterior: si no
    repite su propia cabecera `obj_x`, no hay ninguna razón para asumir que sigue
    perteneciendo al mismo objeto que el bloque previo — es exactamente el caso de un
    `/// @func nombre(...)` de propósito general que aparece justo después del ejemplo
    de un objeto (p.ej. `girar_hacia()` en `13 · 13` §3.2, declarada sin cabecera de
    objeto justo tras el bloque de `obj_bala` de §2.4: sin este reinicio, capa 4 la
    creía "de obj_bala" y avisaba de un falso cruce con `obj_torreta`, que sí la llama —
    correctamente, porque es una función de ángulos de propósito general). Esto no
    afecta a un `.gml` suelto (sin fences): ahí no hay bloques que reiniciar."""
    eventos = [(m.start(1), None) for m in FENCE.finditer(original)]
    for m in LINEA_COMENTARIO.finditer(original):
        linea = m.group(0)
        om = OBJETO_EN_CABECERA.match(linea)
        if om:
            eventos.append((m.start(), om.group(1)))
        elif SCRIPT_EN_CABECERA.search(linea):
            eventos.append((m.start(), None))
    eventos.sort(key=lambda e: e[0])
    return eventos


def ambito_en(pos, eventos):
    resultado = None
    for p, nombre in eventos:
        if p > pos:
            break
        resultado = nombre
    return resultado


def particionar_por_ambito(ocurrencias):
    """Agrupa ocurrencias de una misma función en los subconjuntos que SÍ acabarían
    chocando si se pegan juntas en un proyecto real: todas las de ámbito None
    (scripts sueltos/global) entre sí, y cada objeto con nombre contra ESAS MISMAS
    globales (sin verificar si cruzarlas es realmente seguro: se avisa igual, por
    cautela) — pero nunca un objeto contra otro objeto de nombre distinto."""
    globales = [o for o in ocurrencias if o.get("ambito") is None]
    por_objeto = {}
    for o in ocurrencias:
        amb = o.get("ambito")
        if amb is not None:
            por_objeto.setdefault(amb, []).append(o)

    grupos = []
    if len(globales) >= 2:
        grupos.append(list(globales))
    for lst in por_objeto.values():
        grupos.append(list(lst) + list(globales))
    return grupos


DECL_FUNCION = re.compile(r"\bfunction\s+([A-Za-z_]\w*)\s*\(")
# `#macro NOMBRE valor` normal, o `#macro Config:NOMBRE valor` — la sobrescritura por
# CONFIGURACIÓN del propio manual (Settings/Configurations): NO es el mismo macro que
# el de fuera, es una variante que solo se activa al compilar con esa config. Dos
# `#macro Debug:NIVEL_REGISTRO` y `#macro Release:NIVEL_REGISTRO` conviven sin chocar;
# lo que sí chocaría es la MISMA config repetida, o el mismo nombre sin config repetido.
DECL_MACRO = re.compile(r"#macro\s+(?:([A-Za-z_]\w*):)?([A-Za-z_]\w*)\b([^\n]*)")
DECL_ENUM = re.compile(r"\benum\s+([A-Za-z_]\w*)\s*\{")


def extraer_declaraciones(doc_rel, original, es_gml_suelto):
    """Recorre el documento y devuelve las declaraciones de NIVEL SUPERIOR: funciones
    (con aridad y cuerpo), macros y enums. Solo dentro de bloques ```gml salvo que sea
    un .gml suelto (06 - Assets y Scripts/), que es código de principio a fin."""
    visible = original if es_gml_suelto else mascara_solo_fences(original)
    limpio = enmascarar(visible)
    ambitos = indice_de_ambitos(original)

    funciones, macros, enums = [], [], []
    n = len(limpio)
    profundidad = 0
    i = 0
    while i < n:
        ch = limpio[i]
        if ch == "{":
            profundidad += 1
            i += 1
            continue
        if ch == "}":
            profundidad -= 1
            i += 1
            continue

        if profundidad == 0:
            m = DECL_FUNCION.match(limpio, i)
            if m:
                nombre = m.group(1)
                linea = limpio.count("\n", 0, m.start()) + 1
                # localizar el paréntesis de apertura y su cierre
                p_ini = m.end() - 1
                pd, j = 0, p_ini
                while j < n:
                    if limpio[j] == "(":
                        pd += 1
                    elif limpio[j] == ")":
                        pd -= 1
                        if pd == 0:
                            break
                    j += 1
                params = original[p_ini + 1:j]
                aridad = contar_parametros(params)
                # saltar hasta '{' (puede haber `constructor` de por medio) o ';' (forward decl, no debería darse)
                k = j + 1
                while k < n and limpio[k] not in "{;":
                    k += 1
                if k < n and limpio[k] == "{":
                    bd, z = 0, k
                    while z < n:
                        if limpio[z] == "{":
                            bd += 1
                        elif limpio[z] == "}":
                            bd -= 1
                            if bd == 0:
                                break
                        z += 1
                    # Comparamos sobre `limpio` (comentarios ya en blanco), no sobre el texto
                    # original: dos cuerpos que solo difieren en un comentario `///` son el
                    # MISMO código en tiempo de ejecución, y contarlos como "cuerpo distinto"
                    # sería un falso 🟠 (p.ej. AzarReproducible en 13 · 10 vs 13 · 21, que solo
                    # difieren en la documentación de sus métodos, no en el código).
                    cuerpo = normalizar_cuerpo(limpio[k:z + 1])
                    funciones.append(dict(nombre=nombre, doc=doc_rel, linea=linea,
                                           aridad=aridad, firma=params.strip(), cuerpo=cuerpo,
                                           ambito=ambito_en(m.start(), ambitos)))
                    i = z + 1
                    continue
            m = DECL_MACRO.match(limpio, i)
            if m:
                config = m.group(1) or ""
                nombre = m.group(2)
                linea = limpio.count("\n", 0, m.start()) + 1
                valor = normalizar_cuerpo(m.group(3))
                macros.append(dict(nombre=nombre, config=config, doc=doc_rel, linea=linea, valor=valor))
                i = m.end()
                continue
            m = DECL_ENUM.match(limpio, i)
            if m:
                nombre = m.group(1)
                linea = limpio.count("\n", 0, m.start()) + 1
                bd, z = 0, m.end() - 1
                while z < n:
                    if limpio[z] == "{":
                        bd += 1
                    elif limpio[z] == "}":
                        bd -= 1
                        if bd == 0:
                            break
                    z += 1
                enums.append(dict(nombre=nombre, doc=doc_rel, linea=linea))
                i = z + 1
                continue
        i += 1
    return funciones, macros, enums, visible, limpio


# ---------------------------------------------------------------------------
# Capa 4 — llamadas: dónde se INVOCA cada función, no dónde se declara.
# ---------------------------------------------------------------------------

# Palabras reservadas de GML que aparecen como `palabra (` y no son una llamada a una
# función con ese nombre (control de flujo, declaraciones). `with` se procesa aparte
# (ver WITH_RE) porque sí nos interesa su argumento, solo que no como "llamada".
PALABRAS_CLAVE_GML = {
    "if", "else", "while", "for", "switch", "case", "catch", "repeat", "do",
    "return", "function", "with", "new", "throw", "try", "finally", "break",
    "continue", "exit", "static", "var", "enum", "constructor",
}

# `nombre(` que NO esté precedido de un punto (`obj_x.nombre(` ya es una llamada
# explícita a esa instancia: nunca ambigua, capa 4 no la toca) ni de otro carácter de
# identificador (evita capturar solo el sufijo de un nombre más largo).
LLAMADA_RE = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")
# `with (obj_x) { ... }` — dentro de las llaves, `self` YA es esa instancia: una función
# declarada en el Create de obj_x es alcanzable sin cualificar ahí dentro, tan segura
# como si viviera en un script. Exige la llave de apertura en la misma expresión (con,
# como mucho, un salto de línea entremedias) — es el estilo que usa toda la biblioteca.
WITH_RE = re.compile(r"\bwith\s*\(\s*([A-Za-z_]\w*)\s*\)\s*\n?\s*\{")


def extraer_llamadas(limpio, ambitos):
    """Recorre `limpio` (comentarios/cadenas ya en blanco, MISMA longitud que el
    original — así que sus posiciones sirven directamente para `ambito_en`) en una sola
    pasada y devuelve una lista de dicts `{nombre, pos, linea, ambito, with_activos}`
    para cada llamada `nombre(...)` real: `ambito` es el objeto (o None) bajo cuya
    cabecera ocurre la llamada; `with_activos` es el conjunto de objetos de todos los
    `with (obj_x) { ... }` que envuelven esa posición en ese momento del recorrido."""
    with_por_llave = {m.end() - 1: m.group(1) for m in WITH_RE.finditer(limpio)}

    llamadas = []
    with_stack = []       # (profundidad_en_la_que_se_abrió, nombre_objeto)
    profundidad = 0
    patron = re.compile(r"[{}]|(?<![.\w])([A-Za-z_]\w*)\s*\(")
    for m in patron.finditer(limpio):
        pos = m.start()
        primero = limpio[pos]
        if primero == "{":
            if pos in with_por_llave:
                with_stack.append((profundidad, with_por_llave[pos]))
            profundidad += 1
        elif primero == "}":
            profundidad -= 1
            while with_stack and with_stack[-1][0] >= profundidad:
                with_stack.pop()
        else:
            nombre = m.group(1)
            if nombre in PALABRAS_CLAVE_GML:
                continue
            # excluir declaraciones (`function nombre(`): no son una llamada
            previo = limpio[max(0, pos - 24):pos]
            if re.search(r"\bfunction\s*$", previo):
                continue
            llamadas.append(dict(
                nombre=nombre, pos=pos,
                linea=limpio.count("\n", 0, pos) + 1,
                ambito=ambito_en(pos, ambitos),
                with_activos={w[1] for w in with_stack},
            ))
    return llamadas


GLOBAL_REF = re.compile(r"\bglobal\.([A-Za-z_]\w*)")
GLOBAL_ESCRITURA = re.compile(r"\s*(\+\+|--|\?\?=|[+\-*/]?=(?!=))")


def extraer_globals(limpio):
    """Devuelve (lecturas, escrituras): sets de nombres `global.NOMBRE` según cómo
    aparecen en el texto ya enmascarado (comentarios/cadenas fuera, solo bloques ```gml).

    IMPORTANTE: `GLOBAL_ESCRITURA` se compara con `.match(limpio, m.end())` — directamente
    sobre el texto completo, sin recortar antes una ventana de caracteres fija. Hasta la
    r4 se usaba `resto = limpio[m.end():m.end()+12]` (12 caracteres), y una asignación con
    espacios de alineación de columna (`global.pool_enemigos            = ...`, un estilo
    que esta biblioteca usa mucho para que varias líneas queden alineadas visualmente) caía
    fuera de esa ventana: el `=` quedaba en la posición 13 o más, `GLOBAL_ESCRITURA` nunca lo
    veía, y la escritura real se clasificaba como lectura — falso positivo confirmado en
    `global.salas` (04·14), `global.pool_enemigos` (04·44) y `global.crono_splits` (04·54),
    los tres con alineación de columna. Al quitar el recorte, `\\s*` en `GLOBAL_ESCRITURA`
    consume cualquier cantidad de espacio en blanco hasta encontrar el operador — o hasta
    tropezar con el primer carácter que no sea espacio, momento en el que `.match()` falla
    igual que antes (sigue sin colar un `=` que esté varias líneas más abajo por casualidad,
    porque en cuanto aparece código real que no es espacio en blanco ni el operador, el
    match se detiene ahí)."""
    lecturas, escrituras = set(), set()
    for m in GLOBAL_REF.finditer(limpio):
        nombre = m.group(1)
        if GLOBAL_ESCRITURA.match(limpio, m.end()):
            escrituras.add(nombre)
        else:
            lecturas.add(nombre)
    return lecturas, escrituras


def documentos():
    """(ruta_relativa, texto, es_gml_suelto) de los documentos con código REUTILIZABLE:
    las recetas de género (04), el diseño y producción (13) y los scripts base (06)."""
    docs = []
    for base in sorted(DIRS_INCLUIDAS):
        for raiz, dirs, files in os.walk(os.path.join(RAIZ, base)):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if not f.endswith((".md", ".gml")):
                    continue
                fp = os.path.join(raiz, f)
                try:
                    txt = open(fp, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                rel = os.path.relpath(fp, RAIZ)
                docs.append((rel, txt, f.endswith(".gml")))
    return docs


def documentos_llamadas():
    """Como `documentos()`, pero con el alcance más amplio de `DIRS_INCLUIDAS_LLAMADAS`
    (ver su comentario): la capa 4 no sufre el problema de nombres de ejemplo repetidos
    entre documentos porque nunca compara dos documentos entre sí."""
    docs = []
    for base in sorted(DIRS_INCLUIDAS_LLAMADAS):
        for raiz, dirs, files in os.walk(os.path.join(RAIZ, base)):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if not f.endswith((".md", ".gml")):
                    continue
                fp = os.path.join(raiz, f)
                try:
                    txt = open(fp, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                rel = os.path.relpath(fp, RAIZ)
                docs.append((rel, txt, f.endswith(".gml")))
    return docs


def capa_4():
    """Para cada documento, por separado: ¿alguna `function` declarada con un objeto
    concreto en su cabecera se llama después, sin cualificar y sin un `with()` que la
    cubra, desde el ámbito de un objeto DISTINTO? Devuelve una lista de avisos
    `(doc, nombre, decl, llamada)` — ver el docstring de este módulo, sección 4, para
    qué cuenta como seguro y qué no."""
    avisos = []
    for rel, txt, es_gml in documentos_llamadas():
        funcs, _, _, _, limpio = extraer_declaraciones(rel, txt, es_gml)
        # Solo nos interesan las declaradas dentro de un objeto concreto: las de
        # ámbito None ya son scripts (o el propio .gml suelto), llamables desde
        # cualquier sitio por diseño — no hay nada que avisar ahí.
        por_nombre = {}
        for f in funcs:
            if f["ambito"] is not None:
                por_nombre.setdefault(f["nombre"], []).append(f)
        if not por_nombre:
            continue

        ambitos = indice_de_ambitos(txt)
        llamadas = extraer_llamadas(limpio, ambitos)
        llamadas_por_nombre = {}
        for l in llamadas:
            llamadas_por_nombre.setdefault(l["nombre"], []).append(l)

        for nombre, decls in por_nombre.items():
            ambitos_declarados = {d["ambito"] for d in decls}
            excepcion = EXCEPCIONES_LLAMADAS_EXTERNAS.get(nombre)
            if excepcion and rel in excepcion:
                continue
            for l in llamadas_por_nombre.get(nombre, []):
                if l["ambito"] in ambitos_declarados:
                    continue                                   # mismo objeto: uso interno
                if l["with_activos"] & ambitos_declarados:
                    continue                                   # with(obj_x) { ... }: self ya es obj_x
                avisos.append((rel, nombre, decls, l))
    return avisos


def capa_1_y_2():
    todas_funciones, todas_macros, todos_enums = [], [], []
    lecturas_por_doc = {}
    escrituras_totales = set()

    for rel, txt, es_gml in documentos():
        funcs, macros, enums, _, limpio = extraer_declaraciones(rel, txt, es_gml)
        todas_funciones += funcs
        todas_macros += macros
        todos_enums += enums

        lecturas, escrituras = extraer_globals(limpio)
        lecturas_por_doc[rel] = lecturas - escrituras   # lo que ESTE doc lee sin escribir él mismo
        escrituras_totales |= escrituras

    # --- capa 1a: funciones -------------------------------------------------
    por_nombre = {}
    for f in todas_funciones:
        por_nombre.setdefault(f["nombre"], []).append(f)

    graves, medios, menores = [], [], []
    for nombre, todas_ocs in sorted(por_nombre.items()):
        if len(todas_ocs) < 2:
            continue
        # Solo comparamos ocurrencias que REALMENTE colisionarían al compilar juntas
        # (ver ámbito más arriba): scripts sueltos entre sí, y cada objeto contra los
        # scripts sueltos (no verificado que sea seguro cruzarlos: cautela). Objetos
        # DISTINTOS entre sí no se comparan — confirmado con gm-cli compile.
        for ocs in particionar_por_ambito(todas_ocs):
            if len(ocs) < 2:
                continue
            docs_involucrados = {o["doc"] for o in ocs}
            aridades = {o["aridad"] for o in ocs}
            cuerpos = {o["cuerpo"] for o in ocs}
            excepcion = EXCEPCIONES_DUPLICADOS.get(nombre)
            if excepcion and docs_involucrados == excepcion and len(aridades) == 1 and len(cuerpos) == 1:
                continue   # duplicación documentada y sin cambios: no es ruido
            if len(aridades) > 1:
                graves.append(("función", nombre, ocs))
            elif len(cuerpos) > 1:
                medios.append(("función", nombre, ocs))
            else:
                menores.append(("función", nombre, ocs))

    # --- capa 1b: macros y enums (cualquier duplicado es grave) -------------
    # Los macros se agrupan por (nombre, config): `#macro NIVEL_REGISTRO` y
    # `#macro Debug:NIVEL_REGISTRO` son variantes que NO chocan (la de Debug solo se
    # activa al compilar con esa configuración) — solo choca la MISMA config repetida.
    # Los enums no tienen ese mecanismo: se agrupan solo por nombre.
    for d in todas_macros:
        d.setdefault("config", "")
    por_clave_macro = {}
    for d in todas_macros:
        por_clave_macro.setdefault((d["nombre"], d["config"]), []).append(d)
    for (nombre, config), ocs in sorted(por_clave_macro.items()):
        if len(ocs) < 2:
            continue
        docs_involucrados = {o["doc"] for o in ocs}
        excepcion = EXCEPCIONES_DUPLICADOS.get(nombre)
        if excepcion and docs_involucrados == excepcion:
            continue
        etiqueta = "macro" if not config else f"macro ({config}:…)"
        graves.append((etiqueta, nombre, ocs))

    por_nombre_enum = {}
    for d in todos_enums:
        por_nombre_enum.setdefault(d["nombre"], []).append(d)
    for nombre, ocs in sorted(por_nombre_enum.items()):
        if len(ocs) < 2:
            continue
        docs_involucrados = {o["doc"] for o in ocs}
        excepcion = EXCEPCIONES_DUPLICADOS.get(nombre)
        if excepcion and docs_involucrados == excepcion:
            continue
        graves.append(("enum", nombre, ocs))

    # --- capa 2: global.X leído sin escritura en TODA la biblioteca ---------
    avisos_globals = []
    for rel, huerfanos in sorted(lecturas_por_doc.items()):
        for nombre in sorted(huerfanos):
            if nombre in escrituras_totales:
                continue   # algún OTRO documento sí lo instancia (p.ej. el esqueleto 04 · 00)
            excepcion = EXCEPCIONES_GLOBALS_LECTOR.get(nombre)
            if excepcion and rel in excepcion["docs"]:
                continue   # convención del lector o definida fuera del alcance escaneado — ver cabecera
            avisos_globals.append((rel, nombre))

    return graves, medios, menores, avisos_globals


def _imprimir_ocurrencias(ocs):
    for o in sorted(ocs, key=lambda x: (x["doc"], x["linea"])):
        extra = f"({o['aridad']} arg.)" if "aridad" in o else (f"= {o['valor']}" if "valor" in o else "")
        print(f"      {o['doc']}:{o['linea']}  {extra}")


def reportar_capas_1_2():
    graves, medios, menores, avisos_globals = capa_1_y_2()

    if graves:
        print(f"\n\033[1m🔴 {len(graves)} duplicación(es) GRAVE(S) — arreglar antes de seguir:\033[0m")
        for tipo, nombre, ocs in graves:
            print(f"  ✗ {tipo} `{nombre}` — {len(ocs)} definiciones incompatibles")
            _imprimir_ocurrencias(ocs)
    else:
        print("\n✓ Sin duplicaciones graves (mismo nombre, distinta aridad, o macro/enum repetido).")

    # Un patrón pedagógico legítimo: el MISMO documento enseña una versión y luego la
    # sustituye por otra mejor, diciéndolo en el texto. No es una colisión entre recetas
    # —nadie va a copiar las dos— y marcarlo como problema entrena a ignorar la lista,
    # que es justo lo que no queremos (r12-prueba-plataformas.md §1.1). Se separa, no se
    # silencia: sigue saliendo, pero en su propio apartado y sin ruido.
    RELEVOS = ("reemplaza", "sustituye", "versión ampliada", "version ampliada",
               "no lo declares dos veces", "en vez de la de", "sustituto de")

    def _es_relevo(ocs):
        docs_ = {o["doc"] for o in ocs}
        if len(docs_) != 1:
            return False          # en documentos distintos NO es un relevo: es una colisión
        try:
            texto = open(os.path.join(RAIZ, list(docs_)[0]), encoding="utf-8").read().lower()
        except OSError:
            return False
        return any(r in texto for r in RELEVOS)

    relevos = [m for m in medios if _es_relevo(m[2])]
    medios = [m for m in medios if m not in relevos]

    if medios:
        print(f"\n🟠 {len(medios)} duplicación(es) MEDIA(S) (misma aridad, cuerpo distinto — una gana en silencio):")
        for tipo, nombre, ocs in medios:
            print(f"  ⚠ {tipo} `{nombre}`")
            _imprimir_ocurrencias(ocs)

    if relevos:
        print(f"\n· {len(relevos)} relevo(s) dentro de un mismo documento (una versión sustituye "
              f"a otra y el texto lo dice):")
        for tipo, nombre, ocs in relevos:
            print(f"    {tipo} `{nombre}` — {list({o['doc'] for o in ocs})[0]}")

    if menores:
        print(f"\n🟡 {len(menores)} duplicación(es) menor(es) (firma y cuerpo idénticos, sin excepción documentada):")
        for tipo, nombre, ocs in menores:
            docs_ = ", ".join(sorted({o["doc"] for o in ocs}))
            print(f"  · {tipo} `{nombre}` — {docs_}")
            print("    → si es intencionado, añade el nombre a EXCEPCIONES_DUPLICADOS en la "
                  "cabecera de este script; si no, enlaza en vez de repetir.")


def reportar_capa_4():
    avisos = capa_4()
    if not avisos:
        print("\n✓ Ninguna función declarada en el evento de un objeto parece llamarse "
              "desde otro objeto sin with()/cualificar (capa 4 — ver docstring §4).")
        return avisos

    print(f"\n🟣 {len(avisos)} llamada(s) a una función declarada en el evento de OTRO "
          f"objeto — probable «Variable X.Y(...) not set before reading it» en tiempo de "
          f"ejecución (revisa a mano; no bloquea el exit code):")
    for rel, nombre, decls, l in sorted(avisos, key=lambda a: (a[0], a[3]["linea"])):
        declarada_en = ", ".join(sorted({d["ambito"] for d in decls}))
        print(f"  ⚠ `{nombre}()` declarada en {declarada_en} ({rel}:{decls[0]['linea']}) "
              f"— llamada desde {l['ambito'] or 'un script/ámbito sin objeto'} "
              f"en {rel}:{l['linea']}")
    print("    → si la instancia que llama SIEMPRE hereda la función con event_inherited() "
          "(verificado, no supuesto), añade el nombre a EXCEPCIONES_LLAMADAS_EXTERNAS en la "
          "cabecera de este script; si no, mueve la función a un script (04 · 19 §1 es el "
          "ejemplo de referencia).")
    return avisos

    if avisos_globals:
        print(f"\n🟠 {len(avisos_globals)} `global.X` leído(s) sin que NINGÚN documento lo escriba:")
        for doc, nombre in avisos_globals:
            print(f"  ⚠ global.{nombre}  —  leído en {doc}")
        print("  → o falta el `global." + (avisos_globals[0][1] if avisos_globals else "X") +
              " = …` en algún Create, o lo escribe un documento fuera de esta biblioteca "
              "(p. ej. el esqueleto del proyecto del usuario): revísalo a mano.")
    else:
        print("\n✓ Todo `global.X` leído en la biblioteca se escribe en algún sitio de la biblioteca.")

    return graves


# ---------------------------------------------------------------------------
# Capa 3 — compilación conjunta real con gm-cli
# ---------------------------------------------------------------------------

# Grupos de documentos que se citan mucho entre sí (nodos de mayor grado del grafo de
# reutilización de la auditoría r5). Añade un grupo nuevo aquí cuando detectes — a mano
# o porque capa 1/2 avisó de algo dudoso — dos documentos muy citados que podrían acabar
# en el mismo proyecto real.
GRUPOS = {
    "guardado": [
        "06 - Assets y Scripts/scr_save_load.gml",
        "04 - Recetas por género/04 - RPG _ Action RPG.md",
        "04 - Recetas por género/54 - Metajuego transversal - logros, galería, speedrun y espectador.md",
        "13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md",
        "13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md",
    ],
    "camara_y_juice": [
        "04 - Recetas por género/01 - Plataformas 2D.md",
        "04 - Recetas por género/02 - Top-Down _ Twin-Stick.md",
        "04 - Recetas por género/15 - Game feel y juice.md",
        "04 - Recetas por género/34 - Combate a distancia - armas, munición y balística.md",
    ],
    "combate_y_director": [
        "04 - Recetas por género/30 - Combate cuerpo a cuerpo - hitboxes, hurtboxes y combos.md",
        "04 - Recetas por género/32 - Sistema de daño y efectos de estado.md",
        "04 - Recetas por género/33 - Diseño de enemigos, encuentros y director de combate.md",
    ],
}

TOOLCHAIN_POR_DEFECTO = "GMS2@2026.0.0.23"


def _slug(rel):
    base = os.path.splitext(os.path.basename(rel))[0]
    base = re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_").lower()
    return base[:40] or "doc"


def _codigo_de_doc(rel, vcd):
    """GML "real" de un documento para la capa 3: bloques completos (ver
    `_cargar_validar_compilacion_docs`), sin los fragmentos/pseudocódigo que
    `clasificar()` ya sabe reconocer, y con el `switch`/bucle mínimo que un
    bloque con `case`/`break` sueltos necesita para ser sintaxis válida —
    pero SIN el IIFE ni el renombrado que aíslan cada bloque en
    validar-compilacion-docs.py (eso ocultaría la propia colisión que esta
    capa quiere confirmar)."""
    fp = os.path.join(RAIZ, rel)
    if rel.endswith(".gml"):
        return open(fp, encoding="utf-8", errors="replace").read()

    txt = open(fp, encoding="utf-8", errors="replace").read()
    partes = []
    id_ = 0
    for m in vcd.BLOQUE.finditer(txt):
        id_ += 1
        linea = txt.count("\n", 0, m.start()) + 2
        codigo = vcd.sin_blockquote(m.group(1))
        b = vcd.Bloque(id_, rel, linea, codigo)
        vcd.clasificar(b)
        if b.estado != "ok":
            continue   # fragmento/pseudocódigo (elipsis, plantilla, cita, case suelto…)
        # `static NOMBRE = function(){}` a nivel superior del bloque ("añadido al
        # constructor de arriba", un patrón real de esta biblioteca) es válido en
        # validar-compilacion-docs.py porque SU envoltorio es un IIFE — cualquier
        # función sirve de contenedor para un `static`. Aquí no hay IIFE (a propósito:
        # ver la cabecera de este módulo), así que ese mismo bloque no es código
        # independiente: es una instrucción de "pega esto dentro de otro bloque", no
        # una declaración nueva que pueda chocar con nada. Se descarta para esta capa.
        if re.match(r"^\s*static\s", vcd.limpiar(codigo)):
            continue
        cuerpo = b.codigo
        if b.necesita_switch:
            cuerpo = "switch (0)\n{\n" + cuerpo + "\n}"
        elif b.necesita_bucle:
            cuerpo = "for (var _wrap_i = 0; _wrap_i < 1; _wrap_i++)\n{\n" + cuerpo + "\n}"
        partes.append(f"// --- {rel}:{linea} ---\n{cuerpo}")
    return "\n\n".join(partes)


def _run(cmd, cwd=None, timeout=300):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def compilar_grupo(nombre_grupo, docs_rel, toolchain, proyecto_dir, verbose=True):
    vcd = _cargar_validar_compilacion_docs()
    slug_proyecto = "IntegGrupo_" + _slug(nombre_grupo).title().replace("_", "")
    if verbose:
        print(f"\n\033[1m→ grupo «{nombre_grupo}»\033[0m ({len(docs_rel)} documentos)")

    r = _run(["gm-cli", "init", "--no-interactive", "-n", slug_proyecto,
              "-t", "Blank Pixel Game", "--toolchain", toolchain],
             cwd=proyecto_dir, timeout=180)
    proyecto_path = os.path.join(proyecto_dir, slug_proyecto)
    if not os.path.isdir(proyecto_path):
        return False, f"no se pudo crear el proyecto de prueba:\n{r.stdout}\n{r.stderr}"

    for rel in docs_rel:
        nombre_script = "scr_integ_" + _slug(rel)
        r = _run(["gm-cli", "resourcetool", "eval",
                  f"resource create type=script name={nombre_script}"],
                 cwd=proyecto_path, timeout=60)
        gml_path = os.path.join(proyecto_path, "scripts", nombre_script, f"{nombre_script}.gml")
        if not os.path.exists(gml_path):
            return False, f"no se pudo crear el script para {rel}:\n{r.stdout}\n{r.stderr}"
        codigo = _codigo_de_doc(rel, vcd)
        with open(gml_path, "w", encoding="utf-8") as fh:
            fh.write(f"// volcado de {rel} para validar-integracion.py --compilar\n\n")
            fh.write(codigo)

    r = _run(["gm-cli", "compile", "--toolchain", toolchain, "--errors-only"],
              cwd=proyecto_path, timeout=300)
    ok = (r.returncode == 0)
    salida = (r.stdout + "\n" + r.stderr).strip()
    return ok, salida


def capa_3(grupos_a_correr, toolchain, mantener):
    tmp = tempfile.mkdtemp(prefix="gm_validar_integracion_")
    resultados = []
    try:
        for nombre_grupo in grupos_a_correr:
            docs_rel = GRUPOS[nombre_grupo]
            ok, salida = compilar_grupo(nombre_grupo, docs_rel, toolchain, tmp)
            resultados.append((nombre_grupo, ok, salida))
            if ok:
                print(f"  ✓ compila junto ({len(docs_rel)} documentos)")
            else:
                print(f"  ✗ NO compila junto:")
                for linea in salida.splitlines():
                    if linea.strip():
                        print(f"      {linea}")
    finally:
        if mantener:
            print(f"\n(proyecto(s) de prueba conservados en {tmp} — bórralo a mano cuando termines)")
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    return resultados


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--compilar", action="store_true",
                     help="además de las capas 1 y 2, monta proyecto(s) reales con gm-cli "
                          "y compila cada grupo JUNTO (minutos, necesita GameMaker instalado)")
    ap.add_argument("--grupo", action="append", dest="grupos",
                     help=f"con --compilar, limita a este grupo (repetible). Grupos: "
                          f"{', '.join(GRUPOS)}. Por defecto: todos.")
    ap.add_argument("--toolchain", default=TOOLCHAIN_POR_DEFECTO)
    ap.add_argument("--keep", action="store_true",
                     help="no borrar el/los proyecto(s) temporales de --compilar")
    args = ap.parse_args()

    print("\033[1mvalidar-integracion.py\033[0m — capas 1 y 2 (nombres duplicados · global.X sin escribir)")
    graves = reportar_capas_1_2()

    print("\n\033[1mCapa 4\033[0m — función declarada en el evento de un objeto, llamada "
          "desde otro objeto")
    reportar_capa_4()   # siempre AVISO: no suma a codigo_salida, ver docstring §4

    codigo_salida = 1 if graves else 0

    if args.compilar:
        if not shutil.which("gm-cli"):
            print("\n✗ No encuentro el comando «gm-cli» en el PATH: --compilar necesita "
                  "GameMaker instalado (npm i -g @gamemaker/gm-cli). Las capas 1, 2 y 4 de "
                  "arriba ya han corrido sin él.")
            return 1
        grupos_a_correr = args.grupos or list(GRUPOS)
        desconocidos = [g for g in grupos_a_correr if g not in GRUPOS]
        if desconocidos:
            print(f"\n✗ grupo(s) desconocido(s): {', '.join(desconocidos)}. "
                  f"Grupos válidos: {', '.join(GRUPOS)}")
            return 1
        print(f"\n\033[1mCapa 3 — compilación conjunta real con gm-cli\033[0m "
              f"({len(grupos_a_correr)} grupo(s), toolchain {args.toolchain})")
        resultados = capa_3(grupos_a_correr, args.toolchain, args.keep)
        if any(not ok for _, ok, _ in resultados):
            codigo_salida = 1

    print()
    if codigo_salida:
        print("\033[1mHay incompatibilidades de integración que arreglar.\033[0m")
    else:
        print("\033[1mSin incompatibilidades de integración detectadas.\033[0m")
    return codigo_salida


def autoprueba():
    """Los invariantes del extractor, con texto conocido.

    Este validador decide si dos documentos definen lo mismo de dos formas
    incompatibles, y sus dos errores son opuestos y caros: callarse una colisión
    real (dos recetas que no se pueden usar juntas) o inventarse una, y entonces
    se renombra algo que estaba bien. Los casos de abajo son los que han moldeado
    su lógica.
    """
    fallos = []

    def revisar(nombre, condicion, detalle=""):
        if condicion:
            print("  \u2713 " + nombre)
        else:
            fallos.append(nombre)
            print("  \u2717 %s  ->  %s" % (nombre, detalle))

    def declara(texto, suelto=False):
        f, m, e, _limpio, _amb = extraer_declaraciones("prueba.md", texto, suelto)
        return f, m, e

    doc = ("# D\n\n```gml\nfunction si_cuenta(_a, _b) { return _a; }\n```\n\n"
           "```text\nfunction no_cuenta(_x) { }\n```\n")
    f, _m, _e = declara(doc)
    nombres = [d["nombre"] for d in f]
    revisar("una función dentro de un bloque ```gml se extrae", "si_cuenta" in nombres, nombres)
    revisar("y una dentro de un bloque ```text NO", "no_cuenta" not in nombres, nombres)
    revisar("la aridad se cuenta bien", bool(f) and f[0]["aridad"] == 2,
            f[0]["aridad"] if f else "sin función")

    f, _m, _e = declara("```gml\nfunction con_defecto(_a, _b = 3, _c = []) { }\n```")
    revisar("los parámetros con valor por defecto cuentan",
            bool(f) and f[0]["aridad"] == 3, f[0]["aridad"] if f else "sin función")

    f, _m, _e = declara("```gml\nfunction fuera() {\n  var _f = function dentro() { };\n}\n```")
    nombres = [d["nombre"] for d in f]
    revisar("una función anidada no cuenta como declaración de nivel superior",
            "fuera" in nombres and "dentro" not in nombres, nombres)

    f, m, e = declara("```gml\n#macro TOPE 10\nenum Estado { QUIETO, ANDANDO }\n```")
    revisar("un #macro se extrae", [d["nombre"] for d in m] == ["TOPE"], m)
    revisar("un enum se extrae", any(d["nombre"] == "Estado" for d in e), e)

    revisar("dos cuerpos iguales salvo espacios normalizan igual",
            normalizar_cuerpo("{ return 1; }") == normalizar_cuerpo("{\n  return 1;\n}"))
    revisar("y dos distintos, no",
            normalizar_cuerpo("{ return 1; }") != normalizar_cuerpo("{ return 2; }"))

    f, _m, _e = declara("function de_un_gml(_a) { return _a; }\n", suelto=True)
    revisar("en un .gml suelto no hacen falta vallas",
            [d["nombre"] for d in f] == ["de_un_gml"], f)

    if fallos:
        print("\n\u2717 %d comprobación(es) de la autoprueba fallan." % len(fallos))
        return 1
    print("\n\u2713 Las 10 comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(main())
