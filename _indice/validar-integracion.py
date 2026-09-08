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

USO
    python3 _indice/validar-integracion.py              # capas 1 y 2 (unos segundos)
    python3 _indice/validar-integracion.py --compilar    # + capa 3, TODOS los grupos
    python3 _indice/validar-integracion.py --compilar --grupo guardado
    python3 _indice/validar-integracion.py --compilar --keep   # no borra el proyecto temporal

Sale con 0 si no hay ninguna duplicación 🔴 GRAVE (capas 1 y 2 nunca bloquean por sí
solas más que por eso) y, con `--compilar`, si además todos los grupos compilan juntos.
"""
import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

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
OBJETO_EN_CABECERA = re.compile(r"\bobj(?:_\w+|[A-Z]\w*)\b")
SCRIPT_EN_CABECERA = re.compile(r"\bscr_\w+\b")
LINEA_COMENTARIO = re.compile(r"^[ \t]*//[^\n]*$", re.M)


def indice_de_ambitos(original):
    """Lista ordenada de (posición, objeto_o_None) — cada comentario de cabecera
    que nombra un obj_X/objX abre ese ámbito; uno que nombra un scr_X (o cualquier
    otro comentario sin objeto) lo cierra de vuelta a "sin ámbito" (script/global)."""
    eventos = []
    for m in LINEA_COMENTARIO.finditer(original):
        linea = m.group(0)
        om = OBJETO_EN_CABECERA.search(linea)
        if om:
            eventos.append((m.start(), om.group(0)))
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


GLOBAL_REF = re.compile(r"\bglobal\.([A-Za-z_]\w*)")
GLOBAL_ESCRITURA = re.compile(r"\s*(\+\+|--|\?\?=|[+\-*/]?=(?!=))")


def extraer_globals(limpio):
    """Devuelve (lecturas, escrituras): sets de nombres `global.NOMBRE` según cómo
    aparecen en el texto ya enmascarado (comentarios/cadenas fuera, solo bloques ```gml)."""
    lecturas, escrituras = set(), set()
    for m in GLOBAL_REF.finditer(limpio):
        nombre = m.group(1)
        resto = limpio[m.end():m.end() + 12]
        if GLOBAL_ESCRITURA.match(resto):
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

    if medios:
        print(f"\n🟠 {len(medios)} duplicación(es) MEDIA(S) (misma aridad, cuerpo distinto — una gana en silencio):")
        for tipo, nombre, ocs in medios:
            print(f"  ⚠ {tipo} `{nombre}`")
            _imprimir_ocurrencias(ocs)

    if menores:
        print(f"\n🟡 {len(menores)} duplicación(es) menor(es) (firma y cuerpo idénticos, sin excepción documentada):")
        for tipo, nombre, ocs in menores:
            docs_ = ", ".join(sorted({o["doc"] for o in ocs}))
            print(f"  · {tipo} `{nombre}` — {docs_}")
            print("    → si es intencionado, añade el nombre a EXCEPCIONES_DUPLICADOS en la "
                  "cabecera de este script; si no, enlaza en vez de repetir.")

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

    codigo_salida = 1 if graves else 0

    if args.compilar:
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


if __name__ == "__main__":
    sys.exit(main())
