#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validar-compilacion-docs.py — compila DE VERDAD el GML de los ~245 documentos.

`validar-compilacion.sh` solo compila los 11 scripts reutilizables de
`06 - Assets y Scripts/`. `validar-codigo-gml.py` comprueba que las funciones que
se llaman en los bloques ```gml de TODOS los documentos existen — pero nunca los
compila: un paréntesis sin cerrar, una coma de más o un `var` mal puesto pasa
desapercibido si la función que se llama sí existe. Este script cierra ese hueco:
extrae cada bloque ```gml de las carpetas de contenido, los mete en un proyecto
GameMaker real y los COMPILA con gm-cli contra el runtime instalado.

    python3 _indice/validar-compilacion-docs.py

Por qué .py y no .sh (a diferencia de validar-compilacion.sh)
---------------------------------------------------------------
El trabajo real aquí es parsear ~3100 bloques, decidir para cada uno si es GML
compilable o un fragmento/pseudocódigo, y reescribirlo para que compile sin
falsos positivos (ver «Filtro» abajo). Eso es análisis de texto con regex,
diccionarios y aritmética de líneas — el terreno de validar-codigo-gml.py, no
el de un bucle `for` en bash. El script sigue orquestando gm-cli exactamente
igual que el .sh: la diferencia es dónde vive la lógica de extracción.

Por qué NO se generan stubs de assets (a diferencia de validar-compilacion.sh)
---------------------------------------------------------------------------------
Comprobado en vivo (ver sesión que escribió este script): GameMaker con
gm-cli 2.3.0 / runtime 2026.0.0.23 NO resuelve identificadores en tiempo de
compilación. `var _s = obj_que_no_existe;`, `instance_create_layer(0,0,"L",
obj_x)` o incluso `foo_no_definida(1,2)` compilan sin error: la resolución de
variables, assets y llamadas a función es dinámica, en tiempo de ejecución.
Lo único que SÍ es un error de compilación real: sintaxis inválida, y símbolos
de ámbito de PROYECTO duplicados (`#macro`/`enum` redeclarados, una función
declarada dos veces con el mismo nombre). Por eso aquí no hace falta crear ni
un solo recurso de mentira — y por eso cada bloque se envuelve en una función
anónima autoejecutada `(function() { ... })();`: aísla su `return`, sus `var`
locales Y sus `function nombre() {}` anidadas (comprobado en vivo: una función
declarada DENTRO de un IIFE no colisiona con otra del mismo nombre en otro
IIFE, ni en el mismo archivo ni en otro). `#macro` y `enum` en cambio SÍ son
de ámbito global al proyecto pase lo que pase (comprobado: colisionan incluso
entre recursos de script distintos), así que sus nombres se renombran por
bloque SIEMPRE, aparezcan una vez o varias, antes de escribirlos — y una
función se renombra solo en el caso raro en que el propio bloque la declare
dos veces (el patrón pedagógico «opción A / opción B» dentro del mismo
fragmento, que cae en el mismo IIFE y sí colisiona consigo mismo).

Filtro: qué bloque se descarta, cuál se envuelve y por qué
---------------------------------------------------------------------------
Bloques descartados (no se compilan; se cuentan y se listan sus motivos):
  · «solo comentario»      — tras quitar comentarios no queda código (una
                              cabecera de evento suelta, un aviso). No hay
                              nada que compilar.
  · «elipsis»              — usa `...` fuera de comentarios/cadenas para
                              representar código omitido u opcional
                              (`{ ... }`, `func(x, ...)` como plantilla). No
                              es GML real y NUNCA compilaría, sea cual sea el
                              documento.
  · «plantilla `<...>`»    — usa un marcador `<nombre>` para explicar una
                              sintaxis general (`<variable> = <expresión>;`).
                              Tampoco es GML real.
  · «usa «→»»              — tablas o notas ilustrativas escritas dentro del
                              fence («bit 30 → rotate», «11406 → $2c8e»): la
                              flecha no es un operador de GML, nunca compila.
  · «usa #define»          — sintaxis de fichero de Extensión (`#define
                              nombre` en vez de `function nombre() {}`): solo
                              es válida dentro de un recurso de tipo
                              Extensión, no en un script normal.
  · «fx_create()/font_enable_sdf() de Marketplace» — GML real y válido (está
                              en GmlSpec y en el manual), pero esos
                              identificadores son efectos del Marketplace:
                              `gm-cli compile` detecta la llamada y antes de
                              compilar intenta DESCARGAR el prefab
                              correspondiente desde gmpm.gamemaker.io.
                              Comprobado en vivo: la descarga falla en este
                              entorno («Still Missing Prefabs» / «ProjectTool
                              Failed») y no hay flag para desactivarla — no es
                              un fallo de sintaxis del documento, es una
                              dependencia de red del propio gm-cli ajena a lo
                              que este script comprueba.
  · «gml_pragma Texgroup.Scale» — esta directiva la resuelve el propio
                              compilador contra los grupos de textura reales
                              del proyecto; el nombre de ejemplo del manual
                              («level1») nunca va a existir en un proyecto de
                              prueba vacío. También ajeno a la sintaxis.
  · «::paquete::asset»     — sintaxis real del Package Manager (02/08) para
                              desambiguar un asset de un paquete instalado.
                              El compilador la valida contra los paquetes
                              REALES del proyecto («Unknown scope asset ...
                              found in expression», comprobado en vivo): no
                              hay paquete que fabricar en un proyecto vacío.
  · «cadena con salto de línea sin @» — un salto de línea literal dentro de
                              `"…"`/`$"…"` sin el prefijo `@` (que sí admite
                              líneas reales) es SIEMPRE inválido en GML — lo
                              escriba quien lo escriba a propósito (un
                              contraejemplo de «esto no se puede hacer», como
                              02/02 §2.1) o por descuido.
  · «listado/tabla»        — una línea de nivel superior que no es ni
                              asignación, ni llamada, ni el inicio de una
                              construcción reconocida (`if`, `for`, `var`…).
                              Comprobado en vivo: GML exige que toda sentencia
                              sea una de esas dos cosas — un identificador
                              suelto («direction»), dos nombres separados solo
                              por un espacio («bbox_left   bbox_right») o una
                              comparación suelta («$2c8edd != #2c8edd») dan
                              SIEMPRE «Assignment operator expected». Es la
                              firma de una chuleta de nombres colada en el
                              fence, no de una sentencia real. Un `{` suelto
                              de nivel superior cuenta igual salvo que la
                              línea anterior sea la cabecera de un
                              if/for/while/función: si no, es un literal de
                              struct sin asignar («el struct position
                              acepta: {x, y, z, ...}»), y eso tampoco
                              compila sin asignarlo a algo.
  · «case repetido de varios switches» — el mismo valor de `case` aparece
    dos veces en el bloque: son remiendos para switches DISTINTOS (p.ej.
    «añade esto al switch (_new)» y, más abajo, «al switch (state)», los dos
    con `case PlayerState.slide`) fundidos en un fragmento. Envolverlos en
    un único switch de prueba juntaría ambos y «duplicate case statement
    found» sería un artefacto de la prueba, no del documento.
  · «hereda de un constructor padre no definido en el mismo bloque» —
    `function Hijo() : Padre() constructor { ... }` donde `Padre` no se
    declara en ese mismo bloque. Comprobado en vivo (reproducido de forma
    aislada): a diferencia de una llamada normal, el nombre en `: Padre()`
    SÍ se resuelve en tiempo de COMPILACIÓN, y si no lo encuentra el
    compilador no da un error limpio — CRASHEA el AssetCompiler entero
    (`System.ArgumentNullException: Value cannot be null (Parameter
    'key')` en `GML2VM.AddFuncAndPatch`) y ese «Fatal Error while compiling
    - bailing» se traga cualquier error real de TODOS los bloques
    restantes del build, no solo el de este. Como cada bloque vive en su
    propio `(function() {...})();`, un padre definido en OTRO bloque
    tampoco es visible aquí (aunque en el proyecto real sí lo sería, ahí
    los scripts son globales) — no hay forma honesta de verificar la
    herencia sin arriesgar el crash, así que se salta.

Bloques que SÍ se compilan pero se envuelven primero:
  · `case`/`default:` sueltos sin `switch` que los contenga (y sin case
    repetidos: ver arriba) → se envuelven en `switch (0) { ... }`. Son
    remiendos pensados para pegarse dentro de un switch que ya existe en
    otro sitio del documento: la prosa ya avisa de que son parciales, pero
    el fragmento en sí es GML válido si se le da un switch alrededor.
  · `break;`/`continue;` sueltos sin `switch`/`with`/`for`/`while`/`repeat`/
    `do` que los contenga → se envuelven en un bucle inerte
    `for (var _i = 0; _i < 1; _i++) { ... }`. IMPORTANTE: `with (obj) { ... }`
    SÍ es contexto válido para `break`/`continue` en GML (itera instancias
    igual que un bucle) — confirmado en vivo; de no reconocerlo, el filtro
    marcaría en falso decenas de bloques `with` que son código real y
    correcto.

Lo que este script NO hace
---------------------------------------------------------------------------
No sustituye a validar-codigo-gml.py (funciones inventadas) ni a
validar-compilacion.sh (los 11 scripts reutilizables, con sus stubs de
recursos porque ESE código sí necesita objetos/sprites reales para que la
receta tenga sentido). Es la tercera pata: sintaxis.

Uso
---------------------------------------------------------------------------
    python3 _indice/validar-compilacion-docs.py [--grupo N] [--conservar]

    --grupo N     bloques compilables por recurso de script (por defecto 10).
                  Un valor más bajo aísla mejor los errores (un bloque roto no
                  arrastra falsos errores en los bloques que le siguen en el
                  mismo archivo) a costa de crear más recursos.
    --conservar   no borra ~/gm_prueba_docs al terminar (para inspeccionar
                  el proyecto de prueba a mano).

El proyecto de prueba se crea en ~/gm_prueba_docs (NUNCA bajo /tmp o
/private/tmp: gm-cli init no admite ruta de destino, crea en el directorio de
trabajo actual) y se borra siempre al terminar, incluso si el script falla a
medias.

Medido en vivo con los ~3200 bloques compilables actuales: 17-25 s (extracción
+ `gm-cli init` + creación de recursos + `gm-cli compile`). Por debajo del
límite de 3 minutos que justificaría dejarlo fuera, así que SÍ es el paso 9 de
`actualizar.py` (ver ese script) y se ejecuta en cada pasada normal, no solo a
mano antes de una release.

Sale con 0 solo si todos los bloques compilables compilan sin error real.
"""
import argparse
import bisect
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter

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
HOME = os.path.expanduser("~")
PROY = os.path.join(HOME, "gm_prueba_docs")
YYP = os.path.join(PROY, "gm_prueba_docs.yyp")

# Las mismas carpetas de contenido que pide el pendiente. «06» ya tiene su
# propio validador de scripts reutilizables (validar-compilacion.sh); aquí
# entran igualmente sus bloques ```gml *dentro de documentos* (README, notas),
# que son un conjunto distinto de los .gml sueltos que compila ese script.
CARPETAS = [
    "01 - Fundamentos",
    "02 - Novedades 2026",
    "04 - Recetas por género",
    "05 - Referencia",
    "06 - Assets y Scripts",
    "07 - Ecosistema",
    "08 - Referencia GML completa",
    "10 - Cursos en español",
    "12 - Utilidades e integraciones",
    "13 - Diseño y producción de videojuegos",
]

BLOQUE = re.compile(r"```gml\n(.*?)```", re.S)
COMENTARIO = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)
CADENA = re.compile(r'"(?:[^"\\]|\\.)*"|\$"(?:[^"\\]|\\.)*"')

ELIPSIS = re.compile(r"\.\.\.")
PLANTILLA = re.compile(r"<[A-Za-zÀ-ÿ_][A-Za-zÀ-ÿ0-9_ ]{0,40}>")
FLECHA = re.compile(r"→")
DEFINE_EXTENSION = re.compile(r"(?m)^\s*#define\b")
# Dos formas de red/Marketplace que gm-cli intenta resolver AL COMPILAR (no al
# ejecutar): un `fx_create()` de un efecto empaquetado, o `font_enable_sdf()`
# (dispara la descarga del prefab "io.gamemaker.sdfshaders"). Ambos, GML real.
MARKETPLACE = re.compile(r'fx_create\s*\(\s*[\'"]_(?:effect|filter)_|font_enable_sdf\s*\(')
# `gml_pragma("Texgroup.Scale", "grupo", "n")` es una directiva que el propio
# compilador resuelve contra los grupos de textura DEL PROYECTO: con nombres
# de ejemplo ("level1") nunca va a encontrar ese grupo real.
PRAGMA_TEXGROUP = re.compile(r'gml_pragma\s*\(\s*[\'"]Texgroup\.Scale[\'"]')
# `::paquete::asset` / `::paquete-1.0.3::asset` — sintaxis real del Package
# Manager (02/08) para desambiguar assets de un paquete instalado. El propio
# compilador la resuelve contra los paquetes REALES del proyecto («Unknown
# scope asset ... found in expression», comprobado en vivo): no se puede
# fabricar un paquete instalado en un proyecto de prueba vacío.
PAQUETE_SCOPE = re.compile(r"::[\w.\-]+::")
# `function Hijo() : Padre() constructor { ... }` — herencia de constructor.
# Comprobado en vivo (System.ArgumentNullException, "Value cannot be null
# (Parameter 'key')" en GML2VM.AddFuncAndPatch): a diferencia de una llamada
# normal (resuelta en tiempo de EJECUCIÓN, ver cabecera del script), el
# nombre del padre en `: Padre()` SÍ se resuelve en tiempo de COMPILACIÓN. Si
# `Padre` no existe en ningún sitio visible, el compilador no da un error de
# sintaxis limpio: crashea el AssetCompiler ENTERO («Fatal Error while
# compiling - bailing») y eso oculta cualquier error real de los bloques
# restantes — un efecto mucho peor que un falso rojo aislado. Como cada
# bloque vive en su propio `(function() {...})();` (ver cabecera: aísla
# funciones anidadas), un padre definido en OTRO bloque tampoco es visible
# aquí aunque en el proyecto real sí lo sería (ahí los scripts son globales).
# Sin crear una biblioteca de padres de mentira, la única forma honesta de
# no arriesgar el crash es saltar el bloque cuando el padre no está
# definido DENTRO del mismo bloque.
HERENCIA_CONSTRUCTOR = re.compile(
    r"\bfunction\s+[A-Za-z_]\w*\s*\([^)]*\)\s*:\s*([A-Za-z_]\w*)\s*\(\s*\)\s*constructor\b")
def cadena_con_salto_roto(codigo):
    """¿Hay una cadena `"…"`/`$"…"` (sin el `@` que sí admite líneas reales)
    que no se cierra antes de un salto de línea? SIEMPRE es inválida en GML,
    la escriba quien la escriba a propósito (un contraejemplo de «esto no se
    puede hacer», como 02/02 §2.1) o por descuido — en los dos casos no
    compila tal cual. Recorre el texto a mano en vez de con una sola regex
    porque hay que distinguir la parte LITERAL de un `$"…"` (ahí un salto
    real SÍ rompe la cadena) de sus interpolaciones `{ ... }` (ahí un salto
    real es una expresión normal, válida): una regex sin ese seguimiento de
    profundidad marcaba en falso casi cualquier bloque con una cadena
    corriente (comprobado en vivo: sin esto, ~1200 de 3100 bloques saltaban).
    """
    i, n = 0, len(codigo)
    while i < n:
        c = codigo[i]
        if c == "@" and i + 1 < n and codigo[i + 1] in "\"'":
            cierre = codigo[i + 1]
            i += 2
            while i < n and codigo[i] != cierre:
                i += 1
            i += 1
            continue
        if c == '"':
            es_template = i > 0 and codigo[i - 1] == "$"
            i += 1
            profundidad = 0
            cerrada = False
            while i < n:
                ch = codigo[i]
                if ch == "\\" and i + 1 < n:
                    i += 2
                    continue
                if es_template and ch == "{":
                    profundidad += 1
                elif es_template and ch == "}" and profundidad > 0:
                    profundidad -= 1
                elif ch == '"' and profundidad == 0:
                    cerrada = True
                    i += 1
                    break
                elif ch == "\n" and profundidad == 0:
                    return True
                i += 1
            if not cerrada:
                return True
            continue
        i += 1
    return False
CASE_O_DEFAULT = re.compile(r"(?m)^\s*(case\s+.+:|default\s*:)")
BREAK_CONTINUE = re.compile(r"\b(break|continue)\s*;")
CONTEXTO_VALIDO = re.compile(r"\b(switch\s*\(|with\s*\(|for\s*\(|while\s*\(|repeat\s*\(|do\b)")
TIENE_SWITCH = re.compile(r"\bswitch\s*\(")

# Patrones de DECLARACIÓN cuyo nombre puede colisionar con otro bloque no
# relacionado al compilarlos todos juntos en un único proyecto de prueba:
#   · `#macro` y `enum` son de ámbito GLOBAL AL PROYECTO — comprobado en vivo:
#     colisionan incluso entre dos recursos de script distintos. TODA
#     declaración se renombra, aparezca una vez o varias.
#   · `function nombre() {}` NO necesita esto casi nunca: cada bloque vive en
#     su propio `(function() {...})();` y una función anidada declarada
#     dentro de un IIFE no colisiona con la de otro IIFE (comprobado en vivo,
#     mismo archivo o archivo distinto). La ÚNICA vez que hace falta
#     renombrarla es si el PROPIO bloque declara el mismo nombre dos veces
#     (patrón pedagógico «opción A / opción B» dentro del mismo fragmento):
#     ahí las dos declaraciones caen en el mismo IIFE y si no se renombran
#     colisionan entre sí.
# (patrón, índice del grupo con el nombre, ¿se renombra SIEMPRE?)
DECL_MACRO = (re.compile(r"(?m)^(\s*#macro\s+(?:[A-Za-z_]\w*:)?)([A-Za-z_]\w*)\b"), 2, True)
DECL_ENUM = (re.compile(r"\benum\s+([A-Za-z_]\w*)\s*\{"), 1, True)
DECL_FUNC = (re.compile(r"\bfunction\s+([A-Za-z_]\w*)\s*\("), 1, False)

# GML exige que toda sentencia de nivel superior sea una asignación, una
# llamada, o el inicio de una construcción reconocida (if/for/var/...) —
# comprobado en vivo: un identificador suelto («direction»), dos nombres
# separados solo por un espacio («bbox_left   bbox_right») o una comparación
# suelta («$2c8edd != #2c8edd») son SIEMPRE «Assignment operator expected»,
# nunca un error de sintaxis benigno. Eso es la firma de una tabla de
# referencia o un listado de nombres colado en el fence, no GML real.
_PALABRAS_INICIO = ("if", "for", "while", "var", "return", "switch", "case",
    "default", "enum", "function", "with", "repeat", "do", "break", "continue",
    "globalvar", "static", "try", "catch", "finally", "new", "delete", "else",
    "#macro", "until", "throw", "exit", "constructor")
_TIENE_ASIGNACION = re.compile(r"(?<![=!<>])=(?!=)")
# «is_string()   is_real()    is_numeric()» — dos «llamadas» pegadas solo por
# espacio, sin coma/operador entre ellas: es un catálogo de nombres con
# paréntesis vacíos de adorno, no una sentencia real (una llamada de verdad
# nunca deja OTRA llamada suelta a continuación sin separador).
_LLAMADAS_PEGADAS = re.compile(r"[A-Za-z_]\w*\s*\([^()]*\)\s+[A-Za-z_]\w*\s*\(")
# líneas que, si aparecen ANTES de un `{` de nivel superior, hacen que ese
# `{` sea el cuerpo de un if/for/while/función/etc. — y no un literal de
# struct suelto usado como sentencia (que tampoco compila: ver más abajo).
_PRECEDE_BLOQUE_VALIDO = (")", "=", "else", "do", "try", "finally")


def parece_listado(codigo_limpio):
    """¿Hay alguna línea de nivel superior (fuera de paréntesis/corchetes/
    llaves abiertos por una línea anterior) que no es ni asignación, ni
    llamada, ni inicio de una construcción reconocida? Entonces el bloque no
    es GML ejecutable: es una tabla o un listado de nombres.

    Dos casos especiales, ambos comprobados en vivo:
      · un `{` de nivel superior CUYA LÍNEA ANTERIOR no es la cabecera de un
        if/for/while/función (no termina en `)`, `=`, `else`, `do`...) es un
        literal de struct suelto sin asignar — «Assignment operator
        expected», igual que un identificador suelto. Es la forma de
        documentar la FORMA de un struct («el struct position acepta: {x,
        y, z, ...}») sin que sea una sentencia real.
      · dos llamadas de función pegadas solo por un espacio en la misma
        línea («is_string()   is_real()») es un catálogo de nombres, no una
        sentencia: una llamada real nunca deja otra llamada suelta detrás.
    """
    profundidad = 0
    anterior = ""
    for linea in codigo_limpio.split("\n"):
        l = linea.strip()
        if l and profundidad == 0:
            if l.startswith("{"):
                if not anterior.endswith(_PRECEDE_BLOQUE_VALIDO):
                    return True
            else:
                m = re.match(r"[A-Za-z_#]\w*", l)
                es_palabra_clave = m and (l.startswith(_PALABRAS_INICIO) or m.group(0) in _PALABRAS_INICIO)
                if es_palabra_clave:
                    pass
                elif _LLAMADAS_PEGADAS.search(l):
                    return True
                elif ("(" not in l and not l.startswith("}")
                        and not _TIENE_ASIGNACION.search(l)):
                    return True
            anterior = l
        profundidad += l.count("(") + l.count("[") + l.count("{")
        profundidad -= l.count(")") + l.count("]") + l.count("}")
        profundidad = max(profundidad, 0)
    return False


def limpiar(codigo):
    """Quita comentarios y literales de cadena para detectar patrones reales."""
    codigo = COMENTARIO.sub(" ", codigo)
    codigo = CADENA.sub('""', codigo)
    return codigo


class Bloque:
    __slots__ = ("id", "ruta", "linea", "codigo", "estado", "motivo",
                 "necesita_switch", "necesita_bucle", "recurso",
                 "linea_en_recurso", "prefijo_lineas", "renombres")

    def __init__(self, id_, ruta, linea, codigo):
        self.id = id_
        self.ruta = ruta
        self.linea = linea          # línea (1-index) de la primera línea de código real en el .md
        self.codigo = codigo
        self.estado = None          # "salta" | "ok"
        self.motivo = None          # motivo del salto, si aplica
        self.necesita_switch = False
        self.necesita_bucle = False
        self.recurso = None
        self.linea_en_recurso = None
        self.prefijo_lineas = 0
        self.renombres = {}         # nombre_ofuscado -> nombre_original (para el reporte)


BLOCKQUOTE = re.compile(r"^\s*>\s?", re.M)


def sin_blockquote(codigo):
    """Si el bloque entero vive dentro de una cita `>` de Markdown (un consejo
    con código embebido), el `> ` de cada línea queda DENTRO del contenido
    capturado por `BLOQUE` — el cierre ``` también lleva `> ` delante, así que
    la regex de extracción no tiene forma de excluirlo por sí sola. Sin este
    paso, ese `> ` se compila como un token real y revienta con «unexpected
    symbol ">" in expression»: no es un error del documento, es de la
    extracción. Solo se toca si TODAS las líneas no vacías están citadas
    (si sólo algunas lo están, no es este patrón y se deja tal cual)."""
    lineas = codigo.split("\n")
    no_vacias = [l for l in lineas if l.strip() != ""]
    if no_vacias and all(re.match(r"^\s*>", l) for l in no_vacias):
        return "\n".join(BLOCKQUOTE.sub("", l) for l in lineas)
    return codigo


def extraer_bloques():
    bloques = []
    id_ = 0
    for carpeta in CARPETAS:
        base = os.path.join(RAIZ, carpeta)
        if not os.path.isdir(base):
            continue
        for raiz, dirs, files in os.walk(base):
            dirs.sort()
            for f in sorted(files):
                if not f.endswith(".md"):
                    continue
                fp = os.path.join(raiz, f)
                try:
                    txt = open(fp, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                for m in BLOQUE.finditer(txt):
                    id_ += 1
                    linea_fence = txt.count("\n", 0, m.start()) + 1
                    linea_codigo = linea_fence + 1
                    codigo = sin_blockquote(m.group(1))
                    bloques.append(Bloque(id_, os.path.relpath(fp, RAIZ), linea_codigo, codigo))
    return bloques


def clasificar(b):
    """Decide si el bloque se descarta, y si no, si necesita envoltorio."""
    limpio = limpiar(b.codigo)
    # FX_MARKETPLACE mira el literal de cadena ("_effect_glow"), así que se
    # busca solo quitando comentarios, NUNCA sobre `limpio` (ese ya sustituye
    # toda cadena por "" y el marcador desaparecería).
    sin_comentarios = COMENTARIO.sub(" ", b.codigo)

    if not limpio.strip():
        b.estado, b.motivo = "salta", "solo comentario (sin código real que compilar)"
        return

    if ELIPSIS.search(limpio):
        b.estado, b.motivo = "salta", "usa «...» para representar código omitido/opcional (pseudocódigo)"
        return

    if PLANTILLA.search(limpio):
        b.estado, b.motivo = "salta", "plantilla de sintaxis con marcador «<...>» (no es GML real)"
        return

    if FLECHA.search(limpio):
        b.estado, b.motivo = "salta", "usa «→» para una tabla o notación ilustrativa (no es GML real)"
        return

    if DEFINE_EXTENSION.search(limpio):
        b.estado, b.motivo = "salta", "usa #define: sintaxis de archivo de Extensión, no compila como script normal"
        return

    if MARKETPLACE.search(sin_comentarios):
        b.estado, b.motivo = "salta", "fx_create()/font_enable_sdf() de un efecto de Marketplace (gm-cli lo descarga por red al compilar)"
        return

    if PRAGMA_TEXGROUP.search(sin_comentarios):
        b.estado, b.motivo = "salta", "gml_pragma(\"Texgroup.Scale\", ...) valida el grupo de texturas contra el proyecto; el nombre del ejemplo no existe aquí"
        return

    if PAQUETE_SCOPE.search(sin_comentarios):
        b.estado, b.motivo = "salta", "sintaxis ::paquete::asset del Package Manager; el compilador la valida contra paquetes instalados reales"
        return

    if cadena_con_salto_roto(sin_comentarios):
        b.estado, b.motivo = "salta", "cadena sin @ con un salto de línea sin escapar dentro (no compila; a menudo un contraejemplo deliberado)"
        return

    if parece_listado(limpio):
        b.estado, b.motivo = "salta", "listado/tabla de nombres o comparación suelta (no es una sentencia GML ejecutable)"
        return

    padres = HERENCIA_CONSTRUCTOR.findall(limpio)
    if padres:
        definidas_aqui = set(DECL_FUNC[0].findall(limpio))
        huerfanos = sorted({p for p in padres if p not in definidas_aqui})
        if huerfanos:
            b.estado, b.motivo = "salta", (
                f"hereda de un constructor padre no definido en el mismo bloque "
                f"({', '.join(huerfanos)}): la resolución de `: Padre()` SÍ es en tiempo "
                f"de compilación y un padre inexistente CRASHEA el compilador entero "
                f"(System.ArgumentNullException), no solo ese bloque — comprobado en vivo"
            )
            return

    tiene_switch = bool(TIENE_SWITCH.search(limpio))
    if CASE_O_DEFAULT.search(limpio) and not tiene_switch:
        # Un mismo `case X:` repetido dentro del bloque significa que son
        # remiendos para VARIOS switches distintos (p.ej. «añade esto al
        # switch (_new)» y, más abajo, «añade esto al switch (state)», cada
        # uno con su propio case PlayerState.slide) fundidos en un solo
        # fragmento. Envolverlos en un único `switch (0) {}` de prueba junta
        # ambos y provoca «duplicate case statement found» — un artefacto de
        # la prueba, no del documento: en el código real cada `case` vive en
        # su propio switch. No hay forma honesta de compilar esto como una
        # sola unidad.
        valores = [m.group(1) for m in re.finditer(r"(?m)^\s*case\s+(.+?):", limpio)]
        if len(valores) != len(set(valores)):
            b.estado, b.motivo = "salta", "trae remiendos para varios switches distintos (case repetidos); envolverlo en uno solo crearía colisiones falsas"
            return

    b.estado = "ok"
    if CASE_O_DEFAULT.search(limpio) and not tiene_switch:
        b.necesita_switch = True
    elif BREAK_CONTINUE.search(limpio) and not CONTEXTO_VALIDO.search(limpio):
        b.necesita_bucle = True


def renombrar_declaraciones(codigo, patron, grupo, siempre, b):
    """Da nombres únicos a las declaraciones de `patron` que lo necesiten.

    `siempre=True` (macro, enum): TODA declaración se renombra, aparezca una
    vez o varias — son de ámbito global al PROYECTO y colisionan incluso
    entre bloques de recursos de script distintos (comprobado en vivo). El
    renombrado es un `\\b...\\b` global: también cambia cualquier referencia
    suelta al nombre dentro del MISMO bloque (p.ej. `PlayerState.idle`).

    `siempre=False` (function): gracias al `(function() {...})();` que
    envuelve cada bloque entero, una función declarada UNA sola vez ya vive
    aislada de cualquier otro bloque (comprobado en vivo: el mismo nombre en
    dos IIFEs distintos, mismo archivo o archivo distinto, no colisiona). Solo
    hace falta desambiguar cuando el PROPIO bloque declara el mismo nombre
    más de una vez.

    Y ESE es el caso que se trata igual en ambos modos: cuando el PROPIO
    bloque repite el mismo nombre — el patrón pedagógico «opción A / opción
    B» dentro del mismo fragmento (comprobado en vivo: `#macro TOTAL_ARMAS`
    declarado dos veces en el mismo bloque, una vez «✗ inválido» y otra «✓»,
    con un solo nombre ofuscado para las dos SIGUE colisionando) — no basta
    con un renombrado global: cada aparición necesita su PROPIO sufijo, y
    solo se toca el sitio de la declaración, no las llamadas o referencias
    sueltas — una referencia a un nombre que ya no existe compila igual (ver
    cabecera del script: la resolución de funciones/macros no declarados es
    en tiempo de ejecución, no de compilación).
    """
    coincidencias = list(patron.finditer(codigo))
    if not coincidencias:
        return codigo
    conteo = Counter(m.group(grupo) for m in coincidencias)

    if siempre:
        for nombre in {n for n, c in conteo.items() if c == 1}:
            nuevo = f"{nombre}__v{b.id}"
            b.renombres[nuevo] = nombre
            codigo = re.sub(rf"\b{re.escape(nombre)}\b", nuevo, codigo)

    repetidos = {n for n, c in conteo.items() if c > 1}
    if not repetidos:
        return codigo
    # los conteos de arriba son del texto ORIGINAL: si `siempre` ya reescribió
    # nombres únicos, hay que releer las coincidencias sobre el código actual
    # para que los spans de `sustituir` sean correctos.
    if siempre:
        coincidencias = list(patron.finditer(codigo))
    contador = Counter()

    def sustituir(m):
        nombre = m.group(grupo)
        if nombre not in repetidos:
            return m.group(0)
        contador[nombre] += 1
        nuevo = f"{nombre}__v{b.id}_{contador[nombre]}"
        b.renombres[nuevo] = nombre
        ini, fin = m.span(grupo)
        completo, inicio_m = m.group(0), m.start()
        return completo[:ini - inicio_m] + nuevo + completo[fin - inicio_m:]

    return patron.sub(sustituir, codigo)


def envolver(b):
    """Construye el texto final del bloque (renombrado + envuelto en IIFE)."""
    codigo = b.codigo
    for patron, grupo, siempre in (DECL_MACRO, DECL_ENUM, DECL_FUNC):
        codigo = renombrar_declaraciones(codigo, patron, grupo, siempre, b)

    # envolver en switch/bucle si el bloque tenía case/break/continue sueltos
    prefijo = ["(function() {"]
    sufijo = ["})();"]
    if b.necesita_switch:
        prefijo += ["switch (0)", "{"]
        sufijo = ["}"] + sufijo
    elif b.necesita_bucle:
        prefijo += ["for (var _wrap_i = 0; _wrap_i < 1; _wrap_i++)", "{"]
        sufijo = ["}"] + sufijo

    b.prefijo_lineas = len(prefijo)
    return "\n".join(prefijo) + "\n" + codigo + "\n" + "\n".join(sufijo)


def agrupar_y_escribir(bloques_ok, tam_grupo):
    """Agrupa bloques en recursos de script y devuelve (comandos_batch, escrituras, indice)."""
    comandos = []
    escrituras = {}   # nombre_recurso -> contenido completo del .gml
    indice = {}        # nombre_recurso -> lista ordenada de (linea_inicio, bloque)

    for i in range(0, len(bloques_ok), tam_grupo):
        grupo = bloques_ok[i:i + tam_grupo]
        nombre = f"scr_v_grp{i // tam_grupo:04d}"
        comandos.append(f"RESOURCE CREATE TYPE=script NAME={nombre}")

        partes = []
        linea_actual = 1
        entradas = []
        for b in grupo:
            b.recurso = nombre
            texto = envolver(b)
            b.linea_en_recurso = linea_actual
            entradas.append((linea_actual, b))
            partes.append(texto)
            linea_actual += texto.count("\n") + 1 + 1  # +1 línea en blanco separadora
        escrituras[nombre] = "\n\n".join(partes) + "\n"
        indice[nombre] = entradas

    return comandos, escrituras, indice


ERROR_RE = re.compile(r"gml_(?:GlobalScript|Script)_([A-Za-z0-9_]+)\((\d+)\)\s*:\s*(.*)")


def localizar_bloque(indice, recurso, linea):
    entradas = indice.get(recurso)
    if not entradas:
        return None
    lineas = [e[0] for e in entradas]
    pos = bisect.bisect_right(lineas, linea) - 1
    if pos < 0:
        return None
    return entradas[pos][1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grupo", type=int, default=10,
                     help="bloques compilables por recurso de script (por defecto 10)")
    ap.add_argument("--conservar", action="store_true",
                     help="no borrar ~/gm_prueba_docs al terminar")
    args = ap.parse_args()

    # Este script COMPILA de verdad: necesita el binario `gm-cli` en el PATH (lo instala
    # `npm i -g @gamemaker/gm-cli`, o el paquete equivalente). Sin él, `subprocess.run`
    # lanzaría FileNotFoundError a mitad de un análisis de ~3700 bloques — un traceback
    # crudo en vez de decir qué falta. Se comprueba ANTES de hacer ese trabajo.
    if not shutil.which("gm-cli"):
        print("✗ No encuentro el comando «gm-cli» en el PATH.")
        print("  Este script compila de verdad los bloques ```gml con gm-cli, así que lo")
        print("  necesita instalado: npm i -g @gamemaker/gm-cli (o el instalador oficial")
        print("  de GameMaker). Sin él no se puede comprobar la compilación real; el resto")
        print("  de `actualizar.py` (enlaces, índices, símbolos inventados…) no depende de esto.")
        return 2

    t0 = time.time()
    print("Extrayendo bloques ```gml de los documentos…")
    bloques = extraer_bloques()
    print(f"  {len(bloques)} bloques encontrados en {len(CARPETAS)} carpetas.")

    for b in bloques:
        clasificar(b)

    saltados = [b for b in bloques if b.estado == "salta"]
    compilables = [b for b in bloques if b.estado == "ok"]
    envueltos_switch = [b for b in compilables if b.necesita_switch]
    envueltos_bucle = [b for b in compilables if b.necesita_bucle]

    print(f"\n{len(compilables)} bloques se van a compilar; "
          f"{len(saltados)} se saltan:")
    motivos = Counter(b.motivo for b in saltados)
    for motivo, n in sorted(motivos.items(), key=lambda kv: -kv[1]):
        print(f"    {n:3}  {motivo}")
    if envueltos_switch:
        print(f"  {len(envueltos_switch)} bloques envueltos en `switch (0) {{ }}` "
              f"(case/default sueltos sin switch propio):")
        for b in envueltos_switch:
            print(f"      {b.ruta}:{b.linea}")
    if envueltos_bucle:
        print(f"  {len(envueltos_bucle)} bloques envueltos en un bucle inerte "
              f"(break/continue sueltos sin contexto):")
        for b in envueltos_bucle:
            print(f"      {b.ruta}:{b.linea}")

    if not compilables:
        print("\nNada que compilar.")
        return 0

    print(f"\nAgrupando en recursos de {args.grupo} bloques cada uno…")
    comandos, escrituras, indice = agrupar_y_escribir(compilables, args.grupo)
    print(f"  {len(comandos)} recursos de script.")

    shutil.rmtree(PROY, ignore_errors=True)   # por si quedó de una ejecución anterior interrumpida

    try:
        print(f"\nCreando proyecto de prueba en {PROY}…")
        r = subprocess.run(
            ["gm-cli", "init", "--no-interactive", "--name", "gm_prueba_docs",
             "--template", "blank", "--no-ai", "--no-actions",
             "--toolchain", "GMS2@2026.0.0.23"],
            cwd=HOME, capture_output=True, text=True)
        if not os.path.isfile(YYP):
            print("✗ no se pudo crear el proyecto de prueba:")
            print(r.stdout[-2000:])
            print(r.stderr[-2000:])
            return 2

        batch_path = os.path.join(PROY, "_batch_crear.txt")
        with open(batch_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(comandos) + "\n")

        print("Creando los recursos de script…")
        r = subprocess.run(["gm-cli", "resourcetool", "script", batch_path, YYP],
                            capture_output=True, text=True)
        creados = r.stdout.count("ResourceTool Successful")
        if creados == 0:
            print("✗ no se pudieron crear los recursos de script:")
            print(r.stdout[-3000:])
            print(r.stderr[-2000:])
            return 2

        for nombre, contenido in escrituras.items():
            ruta_gml = os.path.join(PROY, "scripts", nombre, f"{nombre}.gml")
            if not os.path.isfile(ruta_gml):
                print(f"✗ falta el .gml de {nombre} (¿no se creó el recurso?)")
                return 2
            with open(ruta_gml, "w", encoding="utf-8") as fh:
                fh.write(contenido)

        print("Compilando…")
        r = subprocess.run(["gm-cli", "compile"], cwd=PROY, capture_output=True, text=True)
        salida = r.stdout + "\n" + r.stderr

    finally:
        if not args.conservar:
            shutil.rmtree(PROY, ignore_errors=True)
        else:
            print(f"\n(--conservar: el proyecto de prueba se queda en {PROY})")

    # --- interpretar la salida --------------------------------------------------
    errores_atribuidos = []   # (bloque, linea_real, mensaje)
    errores_sueltos = []      # líneas de error que no se pudieron atribuir a un bloque
    for linea in salida.splitlines():
        if "Error :" not in linea and '"message"' not in linea:
            continue
        m = ERROR_RE.search(linea)
        if not m:
            if "Error :" in linea:
                errores_sueltos.append(linea.strip())
            continue
        recurso, linea_recurso, mensaje = m.group(1), int(m.group(2)), m.group(3)
        b = localizar_bloque(indice, recurso, linea_recurso)
        if b is None:
            errores_sueltos.append(linea.strip())
            continue
        linea_local = linea_recurso - b.linea_en_recurso - b.prefijo_lineas + 1
        linea_real = b.linea + linea_local - 1
        for ofusc, orig in b.renombres.items():
            mensaje = mensaje.replace(ofusc, orig)
        errores_atribuidos.append((b, linea_real, mensaje))

    compilo_bien = "Compilation finished" in salida

    print(f"\n{'='*70}")
    if compilo_bien and not errores_atribuidos and not errores_sueltos:
        print(f"✓ Los {len(compilables)} bloques compilables de los documentos "
              f"compilan sin errores de sintaxis.")
    else:
        print("✗ Se encontraron errores de compilación:\n")
        vistos = set()
        for b, linea_real, mensaje in sorted(errores_atribuidos, key=lambda t: (t[0].ruta, t[1])):
            clave = (b.ruta, linea_real, mensaje)
            if clave in vistos:
                continue
            vistos.add(clave)
            print(f"  ✗ {b.ruta}:{linea_real}")
            print(f"      {mensaje}")
        if errores_sueltos:
            print("\n  Errores del compilador sin atribuir a un bloque concreto:")
            for l in errores_sueltos:
                print(f"    {l}")

    print(f"\nTiempo total: {time.time() - t0:.1f}s")

    if not compilo_bien or errores_sueltos or errores_atribuidos:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
