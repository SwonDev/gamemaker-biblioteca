#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""actualizar.py — el ÚNICO comando que hay que ejecutar tras tocar la biblioteca.

    python3 _indice/actualizar.py

Hace, en orden y parando al primer fallo real:

  1. Verifica que todos los enlaces internos existen.
  2. Regenera documentos.json y simbolos.json desde el disco.
  3. Sincroniza MAPA.json: añade los documentos nuevos, actualiza títulos y
     recuentos, y avisa de lo único que necesita una persona (describir una
     carpeta nueva).
  4. Comprueba que MAPA.json no apunta a nada inexistente.
  5. Comprueba la ortografía española en los documentos nuevos.
  … y varias comprobaciones más (cobertura, descubrimiento, código GML, compilación) hasta la 11:
 11. Integración entre documentos (ver validar-integracion.py): nombres duplicados con
     distinta aridad o macro/enum redeclarado entre DOS documentos — lo que ningún otro
     paso ve porque cada uno compila/valida un documento a la vez, nunca la combinación.
     Solo las capas estáticas (segundos); la compilación conjunta real con gm-cli
     (`--compilar`) es manual, documentada en la cabecera de ese script.
 12. Regenera el índice de la skill `gamemaker-biblioteca` y comprueba sus rutas.
 13. Compara el espejo español del manual con el inglés (ver verificar-espejo.py):
     páginas ausentes, incompletas o con literales de la API traducidos.

Sale con 0 solo si todo está correcto. Cualquier otra cosa es trabajo pendiente
y lo dice explícitamente.
"""
import os, re, subprocess, sys, json, time

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
PY = sys.executable

# «09 - Manual oficial» y «11 - Código descargado» son opcionales por diseño (se
# reconstruyen con ./reconstruir.sh): en un clon limpio no están, y eso es su estado
# normal, no trabajo pendiente. Varios pasos de abajo comparan estas dos carpetas con
# lo que citan MAPA.json / _RUTAS.json / la skill; todos usan este mismo criterio para
# no confundir "no instalada" con "rota".
CARPETAS_OPCIONALES = ("09 - Manual oficial", "11 - Código descargado")


def carpeta_instalada(nombre):
    """¿Hay contenido real en esta carpeta opcional, o solo está vacía / con el catálogo?"""
    ruta = os.path.join(RAIZ, nombre)
    if not os.path.isdir(ruta):
        return False
    return bool([e for e in os.listdir(ruta) if e not in ("_RUTAS.json", "_CATALOGO.md")])


def paso(n, titulo):
    print(f"\n\033[1m{n}. {titulo}\033[0m")


def correr(script):
    r = subprocess.run([PY, os.path.join(IND, script)],
                       capture_output=True, text=True)
    print(r.stdout.rstrip())
    if r.stderr.strip():
        print(r.stderr.rstrip(), file=sys.stderr)
    return r.returncode


# Palabras españolas escritas sin tilde.
#
# Solo entran las INEQUÍVOCAS: si la forma sin tilde también es una palabra
# española válida, queda fuera aunque a veces sea un error. Un detector que
# grita en falso se acaba ignorando, y «corregir» un falso positivo es peor
# que no detectarlo: «Practica la navegación» es un imperativo correcto y
# ponerle tilde lo estropea.
#
# Excluidas a propósito por ser también verbos: practica, publico, numero,
# titulo, critico, calculo, continuo, domino, limite, termino, valido.
SIN_TILDE = ["camara", "maquina", "posicion", "animacion", "configuracion",
             "colision", "direccion", "rotacion", "interpolacion", "descripcion",
             "informacion", "duracion", "creacion", "destruccion", "funcion",
             "tamano", "matematicas", "minimo", "maximo", "ultimo",
             "parametro", "parametros", "graficos", "automatico", "codigo",
             "tambien", "segun", "deberia", "aqui", "asi", "facil", "rapido",
             "pagina", "linea", "tecnica", "logica", "basico", "dinamico",
             "angulo", "angulos", "metodo", "metodos", "modulo", "modulos",
             "simbolo", "simbolos", "analisis", "fisica", "estatico", "unico",
             "proximo", "arbol", "arboles", "catalogo", "clasico",
             # la ñ sustituida por n: es la falta más fea y la más fácil de colar
             "espanol", "ano", "anos", "nino", "ninos", "senal", "senales",
             "diseno", "disenar", "companero", "manana", "sueno", "pequeno",
             # sufijo -ción escrito -cion: familia entera, sin ambigüedad posible
             "instalacion", "transcripcion", "documentacion", "informacion",
             "configuracion", "integracion", "migracion", "traduccion",
             "compilacion", "ejecucion", "depuracion", "explicacion",
             "publicacion", "distribucion", "resolucion", "generacion",
             "optimizacion", "programacion", "aplicacion", "comunicacion",
             "introduccion", "conclusion", "revision", "gestion", "seccion",
             "edicion", "iluminacion", "colision",  # el plural «colisiones» NO lleva tilde: el acento se desplaza
             # «video» queda FUERA a propósito: la RAE admite «vídeo» y «video»,
             # y además es prefijo de identificadores GML (video_open, video_draw).
             "basicas", "basicos"]
PAT_TILDE = re.compile(r"\b(" + "|".join(SIN_TILDE) + r")\b", re.I)

# Zonas que NO se revisan, por orden de importancia:
#  · bloques de código y acentos graves → ahí «funcion» puede ser un identificador
#  · etiquetas de enlaces externos      → son títulos citados literalmente
#    (un vídeo llamado «juego de naves basico» se cita tal cual: cambiarlo
#     falsearía la fuente)
# El código inline a veces se parte en dos líneas (las rutas de esta biblioteca
# llevan espacios y se envuelven): se permite UN salto, no más — con más, un
# acento grave suelto se comería medio documento.
COD = re.compile(r"```.*?```|`[^`\n]*(?:\n[^`\n]*)?`", re.S)
CITA = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def revisar_ortografia():
    malos = []
    for raiz, dirs, files in os.walk(RAIZ):
        dirs[:] = [d for d in dirs
                   if d not in {".git", "09 - Manual oficial", "11 - Código descargado",
                                "node_modules", ".ruff_cache", "Lumbre", "GameMaker_Fuentes",
                                # Los informes citan literalmente la salida de este
                                # script, con la palabra que marca incluida.
                                "auditorias"}
                   and not d.startswith(".")]
        for f in files:
            if not f.endswith(".md"):
                continue
            fp = os.path.join(raiz, f)
            # Los volcados de _API del runtime son listados de identificadores
            # ingleses generados desde GmlSpec.xml, no prosa española.
            if "_API del runtime" in fp:
                continue
            try:
                txt = open(fp, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            limpio = CITA.sub(" ", COD.sub(" ", txt))
            hits = sorted({m.group(0) for m in PAT_TILDE.finditer(limpio)})
            if hits:
                malos.append((os.path.relpath(fp, RAIZ), hits[:6]))
    return malos


# Sin mínimo de longitud: «pi», «id», «x» y «y» también son símbolos de GML,
# y exigir 3 caracteres hacía que «pi» pareciera indocumentada.
TOK = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def revisar_cobertura():
    """Símbolos del runtime que no aparecen EN NINGÚN SITIO.

    Ni con página propia en el manual español, ni mencionados en el texto de
    ninguna página, ni explicados por un documento de la biblioteca. Son los
    que un LLM concluiría que no existen.

    Es la métrica que convierte «alguien tendrá que documentarlo» en «el
    comando dice exactamente qué falta, por su nombre».

    Devuelve (None, None) si _indice/simbolos.json no existe todavía (clon sin
    runtime de GameMaker instalado): el paso 2 ya lo explica, esto solo evita
    un traceback en vez de repetir el mensaje.
    """
    ruta_simb = os.path.join(IND, "simbolos.json")
    if not os.path.exists(ruta_simb):
        return None, None
    simb = json.load(open(ruta_simb, encoding="utf-8"))["simbolos"]
    mencionados = set()
    base = os.path.join(RAIZ, "09 - Manual oficial", "manual-lts-2026-es")
    for raiz, _d, files in os.walk(base):
        for f in files:
            if not f.endswith(".md"):
                continue
            try:
                txt = open(os.path.join(raiz, f), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for tk in set(TOK.findall(txt)):
                if tk in simb:
                    mencionados.add(tk)

    invisibles, vigentes = [], 0
    for nom, v in sorted(simb.items()):
        if v.get("obsoleta"):
            continue
        vigentes += 1
        if v.get("manual_es") or v.get("docs_es") or nom in mencionados:
            continue
        invisibles.append(nom)
    return vigentes, invisibles


def revisar_nombres():
    """Los nombres de archivo también son texto en español: llevan tilde.

    Se revisan aparte del contenido porque un nombre mal escrito no lo detecta
    ningún corrector: sale en el índice, en el mapa y en la URL del enlace.
    """
    malos = []
    for raiz, dirs, files in os.walk(RAIZ):
        dirs[:] = [d for d in dirs
                   if d not in {".git", "09 - Manual oficial", "11 - Código descargado",
                                "node_modules", ".ruff_cache", "Lumbre", "GameMaker_Fuentes",
                                # informes de trabajo: nombres ASCII a propósito, como los índices
                                "auditorias"}
                   and not d.startswith(".")]
        for f in files:
            if not f.endswith((".md", ".gml")):
                continue
            base = os.path.splitext(f)[0]
            # Los índices en MAYÚSCULAS son ASCII a propósito (COMO-BUSCAR.md,
            # MAPA.json, README.md, AGENTS.md): se escriben así para poder
            # teclearlos y citarlos sin acentos. No son una falta.
            if base.isupper() or base.replace("-", "").replace("_", "").isupper():
                continue
            hits = sorted({m.group(0) for m in PAT_TILDE.finditer(base)})
            if hits:
                malos.append((os.path.relpath(os.path.join(raiz, f), RAIZ), hits))
    return malos


def revisar_cobertura_familias(umbral=8):
    """Familias de símbolos (>=umbral, no obsoletas) que NINGÚN documento explica.

    No todo símbolo necesita doc didáctico —los getters sueltos los cubre el
    manual y buscar.py—, pero una FAMILIA grande sin ni un documento propio suele
    ser un sistema entero sin cubrir. Informativo: señala dónde mirar, no falla.

    Devuelve None (no una lista vacía: eso significaría «sin huérfanas») si
    _indice/simbolos.json no existe todavía (clon sin runtime instalado).
    """
    import json as _json, collections as _c
    ruta_simb = os.path.join(IND, "simbolos.json")
    if not os.path.exists(ruta_simb):
        return None
    simb = _json.load(open(ruta_simb, encoding="utf-8"))["simbolos"]
    fam = _c.defaultdict(lambda: {"total": 0, "con": 0, "getters": 0, "vars": 0})
    for n, v in simb.items():
        if v.get("obsoleta"):
            continue
        p = n.split("_")
        clave = "_".join(p[:2]) if len(p) > 1 else p[0]
        fam[clave]["total"] += 1
        if v.get("docs_es"):
            fam[clave]["con"] += 1
        # un getter/accessor no es un "sistema": es una consulta que resuelve el manual
        if "_get_" in n or n.endswith("_get") or v.get("tipo") == "variable":
            fam[clave]["getters"] += 1
    huerf = []
    for f, d in fam.items():
        if d["total"] < umbral or d["con"] > 0:
            continue
        # si >60% de la familia son getters/variables, es una familia de accessors,
        # no un sistema sin cubrir: el manual y buscar.py bastan
        if d["getters"] / d["total"] > 0.6:
            continue
        huerf.append((d["total"], f))
    huerf.sort(reverse=True)
    return huerf


def revisar_rutas_codigo():
    """¿_RUTAS.json refleja los repos de 11 - Código descargado?

    El catálogo de código se mantiene a mano; este chequeo avisa si se descargó
    un repo nuevo y no se registró (o si una ruta ya no existe), para que no
    quede fuera de la búsqueda por olvido.

    En un clon limpio «11 - Código descargado» solo trae el catálogo (`_RUTAS.json` +
    `_CATALOGO.md`), sin los ~600 repos reales: comparar entonces cada entrada contra el
    disco produciría cientos de avisos falsos («ya no existe») por algo que nunca se ha
    instalado, no por algo que se borró. Se compara de verdad solo si la carpeta SÍ tiene
    contenido descargado (ver ./reconstruir.sh codigo).
    """
    import json as _json
    base = os.path.join(RAIZ, "11 - Código descargado")
    rutas_p = os.path.join(base, "_RUTAS.json")
    if not os.path.isfile(rutas_p):
        return []
    if not carpeta_instalada("11 - Código descargado"):
        return []
    d = _json.load(open(rutas_p, encoding="utf-8"))
    avisos = []
    catalogadas = {os.path.normpath(r) for r in d.values()}
    for r in d.values():
        if not os.path.isdir(os.path.join(base, r)):
            avisos.append(f"_RUTAS.json apunta a un repo que ya no existe: {r}")
    # repos con .yyp en disco no reflejados
    for raiz, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if not x.startswith(".git")]
        if any(f.endswith((".yyp", ".yyz")) for f in files):
            rel = os.path.normpath(os.path.relpath(raiz, base))
            if not any(rel == c or rel.startswith(c + os.sep) or c.startswith(rel + os.sep)
                       for c in catalogadas):
                avisos.append(f"repo en disco sin registrar en _RUTAS.json: {rel}")
    return avisos


def _bajo_carpeta_opcional_no_instalada(ruta_rel):
    """¿`ruta_rel` cae dentro de 09/11 y esa carpeta no está instalada ahora mismo?"""
    for c in CARPETAS_OPCIONALES:
        if (ruta_rel == c or ruta_rel.startswith(c + "/")) and not carpeta_instalada(c):
            return True
    return False


def revisar_mapa():
    m = json.load(open(os.path.join(IND, "MAPA.json"), encoding="utf-8"))
    falta = []
    for c in m["carpetas"]:
        for d in c.get("documentos", []):
            if os.path.exists(os.path.join(RAIZ, d["ruta"])):
                continue
            if _bajo_carpeta_opcional_no_instalada(d["ruta"]):
                continue
            falta.append(d["ruta"])
    for k in m.get("puntos_de_entrada", {}):
        if os.path.exists(os.path.join(RAIZ, k)):
            continue
        if _bajo_carpeta_opcional_no_instalada(k):
            continue
        falta.append(k)
    return falta, sum(len(c.get("documentos", [])) for c in m["carpetas"])


def main():
    problemas = []

    paso(0, "Las herramientas, antes de fiarse de lo que digan")
    # Un validador que deja de validar no falla: calla. Y un aviso que no salta se
    # lee igual que «está todo bien». Cada uno de los tres se autocomprueba con los
    # casos que ya le han mordido de verdad, y eso va PRIMERO: si el metro está mal,
    # da igual lo que mida.
    _autopruebas = [
        ("verificar-enlaces.py",      "enlaces y anclas"),
        ("validar-codigo-gml.py",     "cadenas sin cerrar"),
        ("auditar-juego-completo.py", "auditor de juego completo"),
        ("validar-proyecto.py",       "validador del proyecto de un agente"),
        ("puerta-pixel-art.py",       "puerta antes de reparar pixel art"),
        ("validar-integracion.py",    "extractor de declaraciones entre documentos"),
        ("atlas-a-gamemaker.py",      "puente de atlas de sprite-gen a GameMaker"),
        # Estas dos tenían autoprueba desde el principio y nadie la ejecutaba: la
        # lista se escribió a mano y se quedaron fuera. Una autoprueba que no corre
        # no protege de nada. El paso 0 bis comprueba ahora que no falte ninguna.
        ("validar-enlaces-externos.py", "recorte de URLs y 404 esperados"),
        ("cerrojo.py",                "cerrojo de las carpetas de trabajo"),
        ("verificar-espejo.py",       "espejo español del manual"),
        ("argumentos.py",             "guardián de argumentos de sobra"),
        ("sincronizar-skill.py",      "etiqueta de versión de la skill"),
        # `buscar.py` es la herramienta de la que se fía todo lo demás y era la
        # única sin autoprueba. Su contrato 0/1/2 —encontrado, buscado y no está,
        # no se ha podido buscar— es lo que separa «no lo escribas» de «no lo sé».
        ("buscar.py",                "contrato de códigos de salida del buscador"),
        ("auditar-cobertura.py",     "cobertura de géneros, recursos y herramientas"),
        # La API de Retro Diffusion cobra por generación, y casi todos sus errores
        # caros se ven sin red y sin clave. Si este metro se estropea, el aviso deja
        # de saltar justo donde cuesta dinero.
        ("validar-peticion-retrodiffusion.py", "petición a la API de Retro Diffusion"),
    ]
    _aplazadas = []       # las que necesitan algo que aún no existe en este clon

    def _correr_autoprueba(_script, _que, _reintento=False):
        _r = subprocess.run([PY, os.path.join(IND, _script), "--autoprueba"],
                            capture_output=True, text=True)
        if _r.returncode == 2 and "Pillow" in _r.stdout:
            # Sin Pillow no se puede ejecutar esa autoprueba. Decirlo, y no
            # confundirlo con «falla»: son cosas distintas.
            print(f"  · {_script}: sin Pillow, autoprueba no ejecutada (no es un fallo)")
        elif _r.returncode == 2 and "simbolos.json" in _r.stdout:
            # Necesita el índice, que lo genera el paso 2. Se reintenta después.
            if _reintento:
                print(f"  · {_script}: sigue sin _indice/simbolos.json (¿sin runtime instalado?)")
            else:
                _aplazadas.append((_script, _que))
                print(f"  · {_script}: aplazada hasta que el paso 2 genere simbolos.json")
        elif _r.returncode != 0:
            for _l in _r.stdout.splitlines():
                if _l.strip().startswith("✗"):
                    print("  " + _l.strip())
            problemas.append(f"la autoprueba de {_script} falla ({_que})")
        else:
            _ultima = [l for l in _r.stdout.splitlines() if l.strip().startswith("✓")]
            print("  " + (_ultima[-1].strip() if _ultima else f"{_script}: correcta"))

    for _script, _que in _autopruebas:
        _correr_autoprueba(_script, _que)

    # 0 bis · ¿Se ha quedado alguna autoprueba fuera de la lista de arriba? Esa lista
    # se escribe a mano, y a mano se olvidan cosas: `validar-enlaces-externos.py` y
    # `cerrojo.py` tenían decenas de casos que no corría nadie. Una autoprueba que no
    # se ejecuta da la misma seguridad que no tenerla, con el agravante de que
    # parece que sí.
    _listadas = {_s for _s, _ in _autopruebas} | {_s for _s, _ in _aplazadas}
    _sueltas = []
    for _f in sorted(os.listdir(IND)):
        if not _f.endswith(".py") or _f in _listadas or _f == "actualizar.py":
            continue
        try:
            _txt = open(os.path.join(IND, _f), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if '"--autoprueba"' in _txt:
            _sueltas.append(_f)
    if _sueltas:
        print("  ⚠ con autoprueba pero SIN ejecutar en este paso: " + ", ".join(_sueltas))
        problemas.append("hay herramientas con --autoprueba fuera del paso 0: "
                         + ", ".join(_sueltas))
    else:
        print(f"  ✓ ninguna herramienta con autoprueba se queda fuera "
              f"({len(_autopruebas)} ejecutadas).")

    # 0 ter · ¿Sobrevive cada herramienta a una consola de Windows?
    # En Windows, `sys.stdout` usa la página de códigos ANSI en cuanto la salida no es
    # una consola interactiva, y un `✓` la revienta con UnicodeEncodeError. **Medido**
    # el 2026-09-09 ejecutando las autopruebas con un Python 3.12.7 de Windows bajo
    # Wine: seis herramientas morían en la primera línea que imprimían. Las seis líneas
    # que lo arreglan estaban ya en doce de ellas, copiadas a mano — y a mano se olvidan.
    _sin_guarda = []
    for _f in sorted(os.listdir(IND)):
        if not _f.endswith(".py"):
            continue
        try:
            _txt = open(os.path.join(IND, _f), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if "reconfigure(encoding" not in _txt:
            _sin_guarda.append(_f)
    if _sin_guarda:
        print("  ⚠ sin protección de codificación para Windows: " + ", ".join(_sin_guarda))
        problemas.append("estas herramientas revientan en una consola de Windows: "
                         + ", ".join(_sin_guarda))
    else:
        print("  ✓ todas resisten una consola de Windows (medido con Python de Windows).")

    paso(1, "Enlaces internos")
    if correr("verificar-enlaces.py") != 0:
        print("→ hay enlaces rotos: corrígelos antes de seguir.")
        return 1

    paso(2, "Índices y MAPA.json")
    if correr("construir-indices.py") != 0:
        # construir-indices.py devuelve 1 por dos motivos distintos (ver su propio
        # mensaje arriba): sin runtime de GameMaker y sin un simbolos.json previo
        # que conservar, o con runtime pero con MAPA.json necesitando una persona.
        # Se distinguen por si el archivo que genera ese primer caso existe, no
        # analizando el texto que imprimió (más frágil).
        if os.path.exists(os.path.join(IND, "simbolos.json")):
            problemas.append("MAPA.json tiene entradas que hay que describir a mano")
        else:
            problemas.append("no hay _indice/simbolos.json: instala GameMaker/gm-cli "
                              "y repite (ver el mensaje del paso 2 de arriba)")

    if _aplazadas:
        print("\n  Autopruebas aplazadas, ahora que ya hay índice de símbolos:")
        for _script, _que in _aplazadas:
            _correr_autoprueba(_script, _que, _reintento=True)

    paso(3, "Coherencia de MAPA.json y del catálogo de código con el disco")
    for a in revisar_rutas_codigo():
        print("  ⚠", a)
        problemas.append("el catálogo de código (_RUTAS.json) no cuadra con el disco")
    falta, total = revisar_mapa()
    if falta:
        problemas.append(f"{len(falta)} rutas de MAPA.json no existen")
        for f in falta[:10]:
            print("  ✗", f)
    else:
        print(f"{total} entradas, todas existen en el disco.")

    paso(4, "Ortografía española")
    malos = revisar_ortografia()
    if malos:
        problemas.append(f"{len(malos)} documentos con tildes ausentes")
        for ruta, hits in malos[:10]:
            print(f"  ✗ {ruta}\n      {', '.join(hits)}")
        if len(malos) > 10:
            print(f"  … y {len(malos) - 10} más")
    else:
        print("Sin palabras españolas escritas sin tilde.")

    paso(5, "Cobertura de la API")
    vigentes, invisibles = revisar_cobertura()
    if vigentes is None:
        print("⚠ sin _indice/simbolos.json (no hay runtime instalado, ver el paso 2 "
              "de arriba): no se puede calcular la cobertura.")
    else:
        cubiertos = vigentes - len(invisibles)
        print(f"{cubiertos} de {vigentes} símbolos vigentes son localizables "
              f"({100 * cubiertos // vigentes} %).")
        if invisibles:
            # El espejo del manual NO se publica (es obra de YoYo Games), así que un
            # clon recién hecho no lo tiene. Sin este matiz, el mensaje de abajo decía
            # «852 símbolos sin documentar» a alguien que acababa de clonar — y era
            # falso: están documentados, lo que falta es el espejo. Un mensaje cierto
            # en una máquina y falso en otra es exactamente lo que este proyecto caza.
            hay_espejo = os.path.isdir(os.path.join(RAIZ, "09 - Manual oficial"))
            print(f"  {len(invisibles)} no aparecen en el manual ni en la biblioteca:")
            print("    " + ", ".join(invisibles[:20])
                  + (" …" if len(invisibles) > 20 else ""))
            if hay_espejo:
                print("  → no es un error: es la lista de lo que queda por documentar.")
            else:
                print("  ⚠ PERO ESTE CLON NO TIENE EL ESPEJO DEL MANUAL (`09 - Manual oficial/`),")
                print("    que no se publica porque es obra de YoYo Games. Así que esa cifra")
                print("    NO es «lo que falta por documentar»: es sobre todo lo que estaría")
                print("    en el manual. Genéralo en tu máquina y vuelve a mirar:")
                print("        ./reconstruir.sh manual")
                print("    Con el espejo puesto, la cobertura de esta biblioteca es del 100 %.")

    paso(6, "Nombres de archivo")
    nombres = revisar_nombres()
    if nombres:
        problemas.append(f"{len(nombres)} archivos con tildes ausentes en el nombre")
        for ruta, hits in nombres[:10]:
            print(f"  ✗ {ruta}\n      {', '.join(hits)}")
        print("  → renombrar exige actualizar los enlaces (van con %20): hazlo de una vez")
    else:
        print("Todos los nombres de archivo están bien escritos.")

    paso(7, "Prueba de descubrimiento (¿un LLM encuentra lo que necesita?)")
    r = subprocess.run([PY, os.path.join(IND, "probar-descubrimiento.py")],
                       capture_output=True, text=True)
    ultimas = [l for l in r.stdout.splitlines() if l.strip()]
    print(ultimas[-1] if ultimas else "(sin salida)")
    if r.returncode != 0:
        for l in r.stdout.splitlines():
            if l.startswith("✗") or l.strip().startswith("no apareció"):
                print("  " + l)
        problemas.append("hay tareas de ejemplo que la biblioteca no resuelve")

    paso(8, "Cobertura por familias de símbolos (dónde falta doc didáctico)")
    huerf = revisar_cobertura_familias()
    if huerf is None:
        print("  ⚠ sin _indice/simbolos.json (no hay runtime instalado, ver el paso 2 "
              "de arriba): no se puede calcular.")
    elif huerf:
        print(f"  {len(huerf)} familias grandes sin documento propio (informativo, no es error):")
        for total, f in huerf[:8]:
            print(f"    {total:3}  {f}_*")
        print("  → getters sueltos los cubre el manual; una familia grande suele ser un sistema.")
    else:
        print("  Todas las familias grandes de símbolos tienen algún documento propio.")

    paso(9, "Código GML (¿inventa alguna función del runtime?)")
    # La autoprueba del detector de cadenas ya corrió en el paso 0, con las de las
    # otras dos herramientas: si el metro está mal, da igual lo que mida.
    r = subprocess.run([PY, os.path.join(IND, "validar-codigo-gml.py")],
                       capture_output=True, text=True)
    for l in r.stdout.splitlines():
        # El `⚠` y su `→` también pasan: son la EXPLICACIÓN de la cifra. Sin ellos, en
        # un clon sin corpus el informe enseñaba «2 posibles funciones INVENTADAS» y
        # «el código no inventa funciones» seguidas, escondiendo la línea del medio que
        # dice por qué. Dos líneas visibles que se contradicen enseñan a no creerse
        # ninguna de las dos.
        if ("INVENTADAS" in l or "no inventa" in l
                or l.strip().startswith(("✗", "⚠", "→"))):
            print("  " + l.strip())
    if r.returncode != 0:
        # Igual que en el paso 2: sin _indice/simbolos.json, validar-codigo-gml.py no
        # puede comprobar nada y termina con ese mensaje (ya impreso arriba, empieza
        # por «✗»); el problema real no es código inventado, es runtime sin instalar.
        if os.path.exists(os.path.join(IND, "simbolos.json")):
            problemas.append("hay código que llama a funciones del runtime que no existen")
        else:
            problemas.append("no se pudo comprobar el código GML: falta "
                              "_indice/simbolos.json (sin runtime instalado, ver el paso 2)")

    paso(10, "Compilación real del GML de los documentos (¿es sintaxis válida?)")
    r = subprocess.run([PY, os.path.join(IND, "validar-compilacion-docs.py")],
                       capture_output=True, text=True)
    for l in r.stdout.splitlines():
        if (l.strip().startswith(("✗", "✓")) or "bloques se van a compilar" in l
                or l.strip().startswith("Tiempo total")):
            print("  " + l.strip())
    if r.returncode == 2:
        # 2 es «no he podido compilar», no «no compila»: el extractor no encontró
        # bloques, o falló el montaje del proyecto. Distinguirlo importa.
        problemas.append("no se pudo comprobar la compilación de los bloques ```gml "
                          "(python3 _indice/validar-compilacion-docs.py para ver por qué)")
    elif r.returncode != 0:
        # Un fallo que no deja rastro no se puede perseguir. Este paso ya falló una vez
        # de forma intermitente —exit 1 en un clon, y al repetirlo pasó— y no quedó ni
        # una línea del error: `actualizar.py` filtra la salida del hijo a las líneas
        # que empiezan por ✓/✗, y un fallo del compilador no empieza por ninguna de las
        # dos. Ahora la salida completa se guarda, y el mensaje dice dónde.
        _reg = os.path.join(IND, "ultimo-fallo-compilacion.txt")
        try:
            with open(_reg, "w", encoding="utf-8") as _f:
                _f.write("# Salida completa de validar-compilacion-docs.py (exit %d)\n"
                         "# Guardada por actualizar.py el %s\n\n"
                         % (r.returncode, time.strftime("%Y-%m-%d %H:%M")))
                _f.write(r.stdout or "")
                if r.stderr:
                    _f.write("\n--- stderr ---\n" + r.stderr)
            _donde = " · salida completa en _indice/ultimo-fallo-compilacion.txt"
        except OSError:
            _donde = ""
        problemas.append("hay bloques ```gml de la documentación que no compilan "
                          "(python3 _indice/validar-compilacion-docs.py para el detalle)"
                          + _donde)

    paso(11, "Integración entre documentos (¿dos recetas definen lo mismo distinto?)")
    r = subprocess.run([PY, os.path.join(IND, "validar-integracion.py")],
                       capture_output=True, text=True)
    for l in r.stdout.splitlines():
        if (l.strip().startswith(("✗", "✓", "⚠", "🔴", "🟠", "🟡")) or "duplicación(es)" in l
                or "leído(s) sin" in l or "GameMaker no permite" in l):
            print("  " + l.strip())
    if r.returncode != 0:
        problemas.append("hay nombres duplicados con distinta aridad, o macro/enum redeclarado, entre "
                          "documentos (python3 _indice/validar-integracion.py para el detalle; "
                          "--compilar añade la prueba de compilación conjunta real, no la corre este paso)")

    paso(12, "Skill para agentes (gamemaker-biblioteca): índice generado y rutas citadas")
    r = subprocess.run([PY, os.path.join(IND, "sincronizar-skill.py")],
                       capture_output=True, text=True)
    print("\n".join("  " + l for l in r.stdout.splitlines()))
    if r.returncode != 0:
        # `sincronizar-skill.py` falla por tres motivos distintos y decirlos todos
        # como «rutas que no existen» es un diagnóstico engañoso — que es justo lo
        # que este proyecto persigue en las herramientas ajenas.
        if "no hay SKILL.md" in r.stdout.lower() or "No hay SKILL.md" in r.stdout:
            problemas.append("falta SKILL.md: la skill es el entregable y no está donde debería")
        elif "cifra desfasada" in r.stdout:
            desfasadas = [l.strip() for l in r.stdout.splitlines() if "cifra desfasada" in l]
            problemas.append("la skill o el README afirman cifras que ya no cuadran — "
                              + "; ".join(d.split("cifra desfasada:")[-1].strip() for d in desfasadas))
        else:
            problemas.append("la skill cita rutas que ya no existen "
                              "(actualiza references/mapa-disciplinas.md)")

    paso(13, "Espejo español del manual (¿va a la par del inglés?)")
    r = subprocess.run([PY, os.path.join(IND, "verificar-espejo.py"), "--resumen"],
                       capture_output=True, text=True)
    print("  " + r.stdout.strip().replace("\n", "\n  "))
    if r.returncode == 1:
        problemas.append("el espejo español del manual tiene páginas ausentes, incompletas o con "
                          "literales traducidos (python3 _indice/verificar-espejo.py para el detalle)")
    elif r.returncode != 0:
        # 2 = no se ha podido comparar. En un clon de GitHub es lo normal: el manual
        # no viaja en el repositorio, se reconstruye. No es deuda, pero tampoco es una
        # comprobación superada, y decir «0 ausentes» ahí sería un falso verde.
        print("  (el paso 13 no ha comprobado nada; `./reconstruir.sh` trae el manual)")

    print()
    if problemas:
        print("\033[1mQueda trabajo:\033[0m")
        for p in problemas:
            print("  ·", p)
        return 1
    print("\033[1mBiblioteca coherente.\033[0m Índices al día y sin deuda pendiente.")
    return 0


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argumentos import exigir_sin_rutas  # noqa: E402

if __name__ == "__main__":
    # `actualizar.py` no tenía guardián: `--autoprueba` se ignoraba en silencio y
    # lanzaba el mantenimiento ENTERO —medio minuto, y reescribe simbolos.json,
    # documentos.json y MAPA.json—. Es la trampa perfecta para quien descubra las
    # herramientas con el `grep '"--autoprueba"'` que la propia documentación sugiere:
    # cree estar haciendo un self-test y está ejecutando el mantenimiento completo.
    # Encontrado por un auditor externo, no por nosotros.
    _sobra = exigir_sin_rutas(
        "Es el mantenimiento completo de ESTA biblioteca y no toma argumentos. "
        "Las autopruebas de las herramientas las ejecuta él solo, en su paso 0.", ())
    if _sobra:
        sys.exit(_sobra)
    sys.exit(main())
