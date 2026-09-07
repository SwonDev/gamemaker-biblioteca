#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""descargar_manual.py — espeja manual.gamemaker.io a Markdown, bajo demanda y con caché.

Uso normal (lo llama reconstruir.sh manual):

    python3 descargar_manual.py --idiomas es,en
    python3 descargar_manual.py --idiomas es,en --limite 50   # prueba rápida
    python3 descargar_manual.py --idiomas es --forzar         # re-descarga aunque exista

Qué hace:
  1. Descarga `sitemap.xml` de cada idioma (rama LTS) → la lista completa de páginas.
  2. Por cada página, si el `.md` de destino YA EXISTE, la salta (caché: reanudable sin
     coste). Si no existe, descarga el `.htm` y lo convierte a Markdown.
  3. Dos peticiones seguidas del mismo idioma esperan un poco (cortesía con el servidor) y
     van repartidas en 4 hilos como máximo, igual que hacía la herramienta original de esta
     biblioteca (ver `09 - Manual oficial/README.md`). Un 429 (demasiadas peticiones) se
     reintenta con espera creciente.
  4. Escribe el `.md` en `09 - Manual oficial/manual-lts-2026-<idioma>/<misma ruta que la
     URL oficial>`, que es exactamente la estructura que esperan `buscar.py` y
     `_indice/construir-indices.py` (cruzan por nombre de archivo, no por metadatos).

Limitación conocida y asumida (ver PUBLICAR.md): el conversor HTML→Markdown de este script
es una reimplementación — el original que generó el espejo publicado en su día ya no está en
este repositorio (se perdió; no hay copia). Sigue el mismo criterio documentado en
`09 - Manual oficial/README.md` (párrafos `<p class="code">` consecutivos → bloque ```gml,
`inline`/`inline2`/`inline3_func` → código en línea, notas → cita, tablas → tabla Markdown,
enlaces `.htm`→`.md`) y se ha probado contra páginas reales en inglés y en español, pero NO
es una reconstrucción byte a byte del espejo original: no reproduce el aviso de copyright
línea a línea, no reescribe conref al detalle y no descarga imágenes (igual que el original).
Es intencionadamente honesto: mejor un conversor más simple que funciona, que fingir que se
recuperó el original.

Sin dependencias externas: solo la biblioteca estándar de Python (así funciona en cualquier
máquina que ya tenga python3, sin `pip install`).
"""
import argparse
import html
import html.parser
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_URL = "https://manual.gamemaker.io"
RAMA = "lts"  # la que corresponde a GameMaker LTS 2026.0 (ver CLAUDE.md)
CARPETA_POR_IDIOMA = {"es": "manual-lts-2026-es", "en": "manual-lts-2026-en"}
AGENTE = ("Mozilla/5.0 (compatible; gamemaker-biblioteca-reconstruccion/1.0; "
          "uso personal sin conexion, ver 09 - Manual oficial/README.md)")
HILOS = 4          # más de 4 hilos simultáneos devuelve 429 (ver memoria del proyecto)
ESPERA_ENTRE = 0.25  # segundos de cortesía entre peticiones de un mismo hilo
REINTENTOS_429 = 5


def _pedir(url, intento=1):
    """GET con reintento con espera creciente ante un 429."""
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 429 and intento <= REINTENTOS_429:
            espera = (2 ** intento) + random.uniform(0, 1)
            time.sleep(espera)
            return _pedir(url, intento + 1)
        raise


def sitemap(idioma):
    """Lista de rutas relativas (`Carpeta/Página.htm`) del idioma dado.

    El sitemap es XML, pero se lee con una expresión regular en vez de un parser
    XML: es una lista plana de `<loc>ruta</loc>` sin DTD ni entidades, así que un
    parser completo no aporta nada y sí abre la puerta a XXE si algún día el
    servidor sirviera un XML manipulado. Más simple es aquí más seguro.
    """
    xml_bruto = _pedir(f"{BASE_URL}/{RAMA}/{idioma}/sitemap.xml")
    return [html.unescape(m.strip()) for m in re.findall(r"<loc>\s*(.*?)\s*</loc>", xml_bruto, re.S)]


# --------------------------------------------------------------------------
# Conversor HTML (RoboHelp) → Markdown. Solo biblioteca estándar.
# --------------------------------------------------------------------------

_CLASES_CODIGO_INLINE = ("inline",)  # cubre inline, inline2, inline3_func…
_BLOQUE = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "table", "hr", "ul", "ol", "li", "div"}


def _atributo(attrs, nombre):
    for k, v in attrs:
        if k == nombre:
            return v or ""
    return ""


def _es_codigo_inline(clase):
    return any(c.startswith(_CLASES_CODIGO_INLINE) for c in clase.split())


def _recortar_codigo(texto):
    """Recorta un bloque de código: quita líneas en blanco sobrantes al
    principio/final y los espacios finales de cada línea, pero conserva la
    indentación de cada línea tal cual — es la que da sentido al GML."""
    lineas = [l.rstrip() for l in texto.split("\n")]
    while lineas and not lineas[0].strip():
        lineas.pop(0)
    while lineas and not lineas[-1].strip():
        lineas.pop()
    return "\n".join(lineas)


_RE_ENLACE_UNICO = re.compile(r"^\[([^\]]+)\]\([^)]*\)$")


def _texto_codigo(t):
    """Formatea el interior de un span de código en línea.

    Cuando ese span envuelve un único enlace entero (`<span class="inline3_func">
    <a href="…">nombre</a></span>`, patrón real del manual en inglés), el
    resultado deseado es código en línea sin enlace — no un enlace Markdown
    metido dentro de comillas invertidas, que no se renderiza como enlace y
    queda feo. Se desenvuelve antes de envolver en backticks.
    """
    t = t.strip()
    if not t:
        return t
    m = _RE_ENLACE_UNICO.match(t)
    if m:
        t = m.group(1)
    return f"`{t}`"


class ConversorManual(html.parser.HTMLParser):
    """Recorre el HTML de una página del manual y produce Markdown.

    Estrategia «marca y sustituye»: al abrir una etiqueta que aporta formato
    (enlace, negrita, cursiva, código en línea) se anota la posición del buffer;
    al cerrarla, el texto acumulado desde esa marca se envuelve con el formato
    correspondiente. Así da igual el orden de anidamiento (`<a><span>` o
    `<span><a>`, ambos aparecen en el manual real): siempre compone bien.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.en_body = False
        self.omitir_profundidad = 0     # >0 mientras se descarta contenido (cabecera, pie, script…)
        self.buffer = []                # texto acumulado del bloque actual
        self.salida = []                # líneas Markdown ya cerradas
        self.marcas = {"a": [], "b": [], "i": [], "codigo": [], "nota": []}
        self.pila_span_tipo = []        # qué cerrar en cada </span>: "codigo" | "nota" | None
        self.href_actual = []
        self.clase_p_actual = None
        self.en_celda = False
        self.fila_actual = None
        self.filas_tabla = []
        self.cabecera_vista = False
        self.codigo_pendiente = []      # líneas de <p class="code"> consecutivos sin volcar
        self.en_comentario_kw = None    # "KEYWORDS" | "TAGS" | None
        self.palabras_clave = []
        self.etiquetas = []
        self.pila_listas = []           # listas <ul>/<ol> anidadas: [{"tipo","contador","items"}]

    # -- utilidades internas -------------------------------------------------
    def _texto(self):
        return "".join(self.buffer)

    def _texto_prosa(self):
        """Texto acumulado, para contextos que NO son código: colapsa el
        exceso de saltos de línea que puede meter una imagen incrustada."""
        return re.sub(r"\n{3,}", "\n\n", self._texto().strip())

    def _marcar(self, tipo, extra=None):
        self.marcas[tipo].append((len(self.buffer), extra))

    def _cerrar(self, tipo, formatear):
        if not self.marcas[tipo]:
            return
        inicio, extra = self.marcas[tipo].pop()
        texto = "".join(self.buffer[inicio:])
        del self.buffer[inicio:]
        self.buffer.append(formatear(texto, extra))

    def _flush_codigo_pendiente(self):
        if self.codigo_pendiente:
            cuerpo = "\n".join(self.codigo_pendiente)
            self.salida.append("```gml\n" + cuerpo + "\n```")
            self.codigo_pendiente = []

    # -- ciclo de vida del parser ---------------------------------------------
    def handle_starttag(self, tag, attrs):
        clase = _atributo(attrs, "class")
        idatr = _atributo(attrs, "id")

        if tag == "body":
            self.en_body = True
            return
        if not self.en_body:
            return

        if self.omitir_profundidad > 0:
            self.omitir_profundidad += 1
            return

        # Cabecera/pie/nav de RoboHelp y cualquier script/style dentro del body:
        # se descartan enteros (no aportan contenido, solo navegación del sitio).
        if (tag == "script" or tag == "style"
                or idatr in ("rh-topic-header", "rh-topic-header-shadow")
                or "footer" in clase.split()
                or "topic-header" in clase):
            self.omitir_profundidad = 1
            return

        # Un <p class="code"> NO corta el bloque de código pendiente: varios
        # <p class="code"> seguidos son un único ejemplo partido en varios
        # párrafos y deben fundirse en un solo ```gml. Solo un bloque de otro
        # tipo (encabezado, tabla, párrafo normal…) cierra el que hubiera.
        if tag == "p" and "code" not in clase.split():
            self._flush_codigo_pendiente()
        elif tag != "p" and tag in _BLOQUE:
            self._flush_codigo_pendiente()

        if tag == "p":
            self.clase_p_actual = clase
            self.buffer = []
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.buffer = []
            return
        if tag == "table":
            self.filas_tabla = []
            self.cabecera_vista = False
            return
        if tag == "tr":
            self.fila_actual = []
            return
        if tag in ("td", "th"):
            self.en_celda = True
            self.buffer = []
            return
        if tag in ("ul", "ol"):
            self.pila_listas.append({"tipo": tag, "contador": 0, "items": []})
            return
        if tag == "li":
            self.buffer = []
            return
        if tag == "br":
            # Dentro de un párrafo de código, el HTML de origen ya trae un
            # salto de línea real justo después de cada <br/> (es como el
            # RoboHelp de YoYo formatea el propio código fuente, indentado
            # igual que el GML). Añadir aquí OTRO salto lo duplicaría y cada
            # línea de código saldría separada por una línea en blanco.
            # Fuera de código (prosa) sí hace falta insertarlo: ahí el salto
            # de línea del HTML de origen es solo maquetación y se colapsa
            # a un espacio en `handle_data`.
            if not (self.clase_p_actual and "code" in self.clase_p_actual.split()):
                self.buffer.append("\n")
            return
        if tag == "img":
            # Las imágenes no se descargan (ver README de «09 - Manual
            # oficial»): igual que el 99 % del corpus ya publicado, que no
            # trae ni una referencia ![alt](src), se omiten del todo en vez
            # de dejar un enlace roto a un binario que no está en el disco.
            return
        if tag == "a":
            href = _atributo(attrs, "href")
            self.href_actual.append(href)
            self._marcar("a")
            return
        if tag in ("b", "strong"):
            self._marcar("b")
            return
        if tag in ("i", "em"):
            self._marcar("i")
            return
        if tag == "span" and _es_codigo_inline(clase):
            self._marcar("codigo")
            self.pila_span_tipo.append("codigo")
            return
        if tag == "span" and ("note" in clase.split() or "warning" in clase.split()):
            # <span class="note">NOTE</span> / <span class="warning">WARNING</span>
            # — la palabra que abre el aviso; en el manual real va en negrita.
            self._marcar("nota")
            self.pila_span_tipo.append("nota")
            return
        if tag == "span":
            # span genérico (data-field, data-conref, data-keyref, notranslate…):
            # transparente, su texto simplemente fluye. Se registra igualmente
            # en la pila para que el </span> que le corresponda no cierre por
            # error el marcador de un span de otro tipo que esté abierto fuera.
            self.pila_span_tipo.append(None)
            return
        # div genérico: transparente, igual que un span sin clase reconocida.

    def handle_startendtag(self, tag, attrs):
        # <br/>, <img .../> autocontenidos
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if not self.en_body:
            return
        if self.omitir_profundidad > 0:
            self.omitir_profundidad -= 1
            return

        if tag == "a":
            href = self.href_actual.pop() if self.href_actual else ""

            def fmt(texto, _extra, href=href):
                return _enlazar(texto, href)
            self._cerrar("a", fmt)
            return
        if tag in ("b", "strong"):
            self._cerrar("b", lambda t, _e: f"**{t}**" if t.strip() else t)
            return
        if tag in ("i", "em"):
            self._cerrar("i", lambda t, _e: f"*{t}*" if t.strip() else t)
            return
        if tag == "span":
            tipo = self.pila_span_tipo.pop() if self.pila_span_tipo else None
            if tipo == "codigo":
                self._cerrar("codigo", lambda t, _e: _texto_codigo(t))
            elif tipo == "nota":
                self._cerrar("nota", lambda t, _e: f"**{t.strip()}**" if t.strip() else t)
            return
        if tag == "li":
            texto = self._texto_prosa().replace("\n", " ")
            if texto and self.pila_listas:
                ctx = self.pila_listas[-1]
                if ctx["tipo"] == "ol":
                    ctx["contador"] += 1
                    prefijo = f"{ctx['contador']}. "
                else:
                    prefijo = "- "
                ctx["items"].append(prefijo + texto)
            self.buffer = []
            return
        if tag in ("ul", "ol"):
            if self.pila_listas:
                ctx = self.pila_listas.pop()
                if ctx["items"]:
                    # un único bloque (líneas unidas por \n): la lista no debe
                    # quedar partida por las líneas en blanco entre bloques
                    self.salida.append("\n".join(ctx["items"]))
            return
        if tag == "p":
            if self.clase_p_actual and "code" in self.clase_p_actual.split():
                texto = _recortar_codigo(self._texto())
                if texto:
                    self.codigo_pendiente.append(texto)
            else:
                texto = self._texto_prosa()
                if self.clase_p_actual and "note" in self.clase_p_actual.split():
                    if texto:
                        self.salida.append("> " + texto)
                elif texto:
                    self.salida.append(texto)
            self.clase_p_actual = None
            self.buffer = []
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            nivel = int(tag[1])
            texto = self._texto_prosa().replace("\n", " ")
            if texto:
                self.salida.append("#" * nivel + " " + texto)
            self.buffer = []
            return
        if tag in ("td", "th"):
            self.en_celda = False
            texto = self._texto_prosa().replace("|", "\\|").replace("\n", " ")
            if self.fila_actual is None:
                self.fila_actual = []
            self.fila_actual.append(texto)
            if tag == "th":
                self.cabecera_vista = True
            self.buffer = []
            return
        if tag == "tr":
            if self.fila_actual:
                self.filas_tabla.append(self.fila_actual)
            self.fila_actual = None
            return
        if tag == "table":
            self._flush_tabla()
            return
        if tag == "body":
            self.en_body = False
            return

    def handle_data(self, data):
        if not self.en_body or self.omitir_profundidad > 0:
            return
        if self.clase_p_actual and "code" in self.clase_p_actual.split():
            # código: la indentación es significativa, se conserva tal cual
            self.buffer.append(data)
        else:
            # prosa: el HTML colapsa cualquier tira de espacios/tabs/saltos de
            # línea de maquetación a un único espacio (así se comporta un
            # navegador fuera de <pre>); los saltos de línea *reales* los
            # aporta un <br/> explícito, no el texto. El espacio de no
            # separación (\xa0, &nbsp;) se normaliza también a un espacio
            # normal: el propio espejo ya publicado es inconsistente con él
            # (unas páginas lo conservan, otras no — no hay regla fiable que
            # extraer), y un carácter invisible distinto de un espacio normal
            # solo estorba a una búsqueda de texto literal (`buscar.py`).
            self.buffer.append(re.sub(r"\s+", " ", data))

    def handle_comment(self, data):
        cabecera = data.strip().splitlines()[0].strip().upper() if data.strip() else ""
        if cabecera in ("KEYWORDS", "TAGS"):
            lineas = [l.strip() for l in data.strip().splitlines()[1:] if l.strip()]
            if cabecera == "KEYWORDS":
                self.palabras_clave.extend(lineas)
            else:
                self.etiquetas.extend(lineas)

    def _flush_tabla(self):
        if not self.filas_tabla:
            return
        cab, *resto = self.filas_tabla
        ancho = len(cab)
        lineas = ["| " + " | ".join(cab) + " |", "|" + "|".join(["---"] * ancho) + "|"]
        for fila in resto:
            fila = (fila + [""] * ancho)[:ancho]
            lineas.append("| " + " | ".join(fila) + " |")
        # una sola entrada en `salida` (líneas unidas por \n) para que la tabla
        # no quede partida por las líneas en blanco que separan los demás bloques
        self.salida.append("\n".join(lineas))
        self.filas_tabla = []

    def cuerpo(self):
        self._flush_codigo_pendiente()
        return "\n\n".join(p for p in self.salida if p.strip())

    def bloque_claves(self):
        """Palabras clave + etiquetas en el mismo formato que ya usa el resto del
        espejo: una línea cada una, sin línea en blanco entre ambas, unidas por
        un espacio y en el mismo orden que trae el HTML (no alfabético — así es
        como aparecen en el corpus ya publicado). Ver `_indice/traduccion/tm.py`,
        que las reconoce con ese patrón exacto para no traducirlas."""
        lineas = []
        if self.palabras_clave:
            lineas.append("**Palabras clave:** " + " ".join(self.palabras_clave))
        if self.etiquetas:
            lineas.append("**Etiquetas:** " + " ".join(self.etiquetas))
        return "\n".join(lineas)


def _enlazar(texto, href):
    if not texto.strip():
        return texto
    if not href or href == "#":
        return texto
    if href.startswith(("http://", "https://", "mailto:")):
        return f"[{texto}]({href})"
    # enlace interno del manual: .htm -> .md, conservando ruta relativa y ancla
    destino = re.sub(r"\.html?(?=$|#)", ".md", href)
    return f"[{texto}]({destino})"


def convertir(html_bruto):
    """Devuelve (cuerpo, bloque_claves) — ver `ConversorManual`."""
    c = ConversorManual()
    c.feed(html_bruto)
    c.close()
    return c.cuerpo(), c.bloque_claves()


# --------------------------------------------------------------------------
# Descarga de una página + escritura en disco
# --------------------------------------------------------------------------

def _ruta_destino(destino_base, idioma, ruta_relativa):
    carpeta = CARPETA_POR_IDIOMA[idioma]
    sin_ext = re.sub(r"\.htm$", "", ruta_relativa)
    return os.path.join(destino_base, carpeta, sin_ext + ".md")


def descargar_pagina(idioma, ruta_relativa, destino_base, forzar):
    destino = _ruta_destino(destino_base, idioma, ruta_relativa)
    if os.path.exists(destino) and not forzar:
        return "saltada", ruta_relativa, None

    url = f"{BASE_URL}/{RAMA}/{idioma}/{ruta_relativa}"
    try:
        time.sleep(ESPERA_ENTRE + random.uniform(0, 0.15))
        bruto = _pedir(url)
        cuerpo, bloque_claves = convertir(bruto)
        if not cuerpo.strip():
            return "vacia", ruta_relativa, "el conversor no extrajo contenido"
        # mismo formato exacto que ya usa el resto del espejo publicado (lo
        # reconoce `_indice/traduccion/tm.py` para no traducir esta parte):
        # cuerpo, [claves/etiquetas,] «---», «Fuente oficial: <url>»
        partes = [cuerpo]
        if bloque_claves:
            partes.append(bloque_claves)
        partes.append(f"---\n\nFuente oficial: <{url}>")
        contenido = "\n\n".join(partes) + "\n"
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            f.write(contenido)
        return "ok", ruta_relativa, None
    except Exception as e:  # noqa: BLE001 — se reporta y se sigue con las demás páginas
        return "error", ruta_relativa, str(e)


def procesar_idioma(idioma, destino_base, limite, forzar):
    print(f"\n→ {idioma}: descargando el mapa del sitio…")
    rutas = sitemap(idioma)
    if limite:
        rutas = rutas[:limite]
    print(f"  {len(rutas)} página(s) en el sitemap de «{idioma}».")

    ok = saltadas = vacias = 0
    errores = []
    hecho = 0
    with ThreadPoolExecutor(max_workers=HILOS) as pool:
        futuros = {pool.submit(descargar_pagina, idioma, r, destino_base, forzar): r
                   for r in rutas}
        for fut in as_completed(futuros):
            estado, ruta, detalle = fut.result()
            hecho += 1
            if estado == "ok":
                ok += 1
            elif estado == "saltada":
                saltadas += 1
            elif estado == "vacia":
                vacias += 1
                errores.append((ruta, detalle))
            else:
                errores.append((ruta, detalle))
            if hecho % 100 == 0 or hecho == len(rutas):
                print(f"  [{idioma}] {hecho}/{len(rutas)} — {ok} nuevas, {saltadas} en caché, "
                      f"{len(errores)} con problemas")

    print(f"  «{idioma}» terminado: {ok} descargadas, {saltadas} ya estaban en caché, "
          f"{vacias} vacías, {len(errores) - vacias} con error.")
    return ok, saltadas, errores


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--idiomas", default="es,en",
                     help="lista separada por comas: es,en (por defecto ambos)")
    ap.add_argument("--limite", type=int, default=0,
                     help="descarga como mucho N páginas por idioma (pruebas)")
    ap.add_argument("--destino", default=os.path.join(RAIZ, "09 - Manual oficial"),
                     help="carpeta base de destino (por defecto «09 - Manual oficial»)")
    ap.add_argument("--forzar", action="store_true",
                     help="re-descarga aunque el .md ya exista (por defecto se salta)")
    args = ap.parse_args()

    idiomas = [i.strip() for i in args.idiomas.split(",") if i.strip()]
    for i in idiomas:
        if i not in CARPETA_POR_IDIOMA:
            print(f"✗ Idioma desconocido: {i!r} (válidos: {', '.join(CARPETA_POR_IDIOMA)})")
            return 2

    total_ok = total_saltadas = 0
    todos_los_errores = []
    for idioma in idiomas:
        ok, saltadas, errores = procesar_idioma(idioma, args.destino, args.limite, args.forzar)
        total_ok += ok
        total_saltadas += saltadas
        todos_los_errores.extend((idioma, r, d) for r, d in errores)

    print(f"\n✓ Total: {total_ok} páginas nuevas, {total_saltadas} ya en caché.")
    if todos_los_errores:
        print(f"⚠ {len(todos_los_errores)} página(s) con problemas (se pueden reintentar "
              f"volviendo a lanzar el mismo comando: las que sí se guardaron no se repiten):")
        for idioma, ruta, detalle in todos_los_errores[:20]:
            print(f"    [{idioma}] {ruta} — {detalle}")
        if len(todos_los_errores) > 20:
            print(f"    … y {len(todos_los_errores) - 20} más")
    return 0


if __name__ == "__main__":
    sys.exit(main())
