# 21 · Localización e idiomas — con traducción por IA

> Que tu juego hable el idioma del jugador. No es "traducir los textos": es un **sistema** —
> tabla de cadenas, cambio en caliente, fuentes con los glifos correctos, plurales,
> interpolación de variables— y, hoy, un **flujo de traducción asistida por IA** que convierte
> tu español en diez idiomas sin copiar y pegar en mil sitios.
>
> **Hueco detectado:** la biblioteca solo tenía menciones sueltas de «ten un `items_es.json`».
> Este documento monta el sistema entero.

---

## La regla de oro: ni un texto suelto en el código

```gml
/// ❌ imposible de traducir
draw_text(x, y, "Pulsa ESPACIO para saltar");

/// ✅ el texto vive en la tabla, el código solo tiene la CLAVE
draw_text(x, y, txt("hud_saltar"));
```

**Todo texto que ve el jugador pasa por `txt(clave)`.** Es la única regla que hace posible
todo lo demás. Un texto escrito a pelo es un texto que nunca se traducirá.

---

## 1 · La tabla de cadenas

Un archivo JSON por idioma, con las mismas claves. El español es la fuente.

```
datafiles/idiomas/
    es.json      ← el original que escribes tú
    en.json      ← generados por IA a partir de es.json
    fr.json
    de.json
    ...
```

```json
// es.json
{
    "hud_saltar":     "Pulsa ESPACIO para saltar",
    "menu_jugar":     "Jugar",
    "menu_opciones":  "Opciones",
    "dialogo_bienvenida": "Hola, {nombre}. Bienvenido a {zona}.",
    "monedas_una":    "Tienes {n} moneda",
    "monedas_varias": "Tienes {n} monedas"
}
```

```gml
/// obj_control · Create — cargar el idioma
function idioma_cargar(_codigo) {
    var _ruta = $"idiomas/{_codigo}.json";
    if (!file_exists(_ruta)) _ruta = "idiomas/es.json";   // fallback al original

    var _f = file_text_open_read(_ruta);
    var _txt = "";
    while (!file_text_eof(_f)) _txt += file_text_read_string(_f) + file_text_readln(_f);
    file_text_close(_f);

    global.idioma = _codigo;
    global.textos = json_parse(_txt);   // struct clave → texto
}
```

> 💡 **Los `.json` van en Included Files (`datafiles/`)**, no incrustados en el código. Así un
> traductor (o tú mismo) puede editarlos sin recompilar, y la IA puede regenerarlos.

---

## 2 · La función `txt()` — con variables y plurales

```gml
/// scr_idioma — el corazón del sistema
function txt(_clave, _vars = undefined) {
    // 1 · buscar la clave; si falta, devolver la clave misma (así se ve el hueco)
    if (!variable_struct_exists(global.textos, _clave)) {
        return $"[[{_clave}]]";     // «[[hud_saltar]]» grita que falta traducir
    }
    var _s = global.textos[$ _clave];

    // 2 · interpolar {variables}
    if (!is_undefined(_vars)) {
        var _nombres = variable_struct_get_names(_vars);
        for (var _i = 0; _i < array_length(_nombres); _i++) {
            var _k = _nombres[_i];
            _s = string_replace_all(_s, "{" + _k + "}", string(_vars[$ _k]));
        }
    }
    return _s;
}

/// plurales: elige la clave según la cantidad
function txt_n(_base, _n) {
    var _clave = (_n == 1) ? _base + "_una" : _base + "_varias";
    return txt(_clave, { n: _n });
}
```

```gml
/// uso
draw_text(x, y, txt("dialogo_bienvenida", { nombre: global.jugador, zona: "el Bosque" }));
draw_text(x, y, txt_n("monedas", global.monedas));    // "Tienes 1 moneda" / "Tienes 5 monedas"
```

> 🔺 **Devolver `[[clave]]` cuando falta no es un adorno.** Al jugar en un idioma a medio
> traducir, ves de un vistazo qué falta, en vez de un texto en blanco o el juego caído.
>
> ⚠️ **Los plurales NO son "+s".** En español «1 moneda / 2 monedas» parece trivial, pero en
> ruso hay tres formas y en árabe seis. Por eso cada cantidad tiene su clave, no una regla
> hardcodeada. Para idiomas con plurales complejos, amplía `txt_n` con las claves que haga
> falta (`_pocas`, `_muchas`).

---

## 3 · Detectar el idioma del jugador y cambiarlo en caliente

```gml
/// Create — arrancar en el idioma del sistema si lo tenemos
var _sys = os_get_language();          // "es", "en", "fr"… (ISO 639-1)
var _disponibles = ["es", "en", "fr", "de", "pt", "it"];
idioma_cargar(array_contains(_disponibles, _sys) ? _sys : "en");
```

```gml
/// el jugador elige otro idioma en Opciones
function cambiar_idioma(_codigo) {
    idioma_cargar(_codigo);
    ini_open("ajustes.ini");
    ini_write_string("general", "idioma", _codigo);   // recordarlo
    ini_close();
    senal_emitir("idioma_cambiado", { idioma: _codigo });  // que la UI se redibuje
}
```

> 💡 **Cambiar de idioma es recargar la tabla, nada más.** Como los textos se leen con `txt()`
> en cada frame de dibujo, el cambio es instantáneo. Emite una [señal](./16%20-%20Señales%20y%20desacoplamiento.md)
> para que los menús que cachean texto se refresquen.

---

## 4 · Fuentes y glifos — la trampa de los alfabetos no latinos

Tu fuente `.ttf` probablemente **no incluye** cirílico, griego, chino, japonés o coreano. Si
traduces al ruso y tu fuente no tiene sus glifos, sale todo en blanco.

```gml
/// cargar una fuente con el rango de glifos que el idioma necesita
// latín + acentos + ñ + ¿¡  → rango 32..255 basta para es/en/fr/de/pt/it
fnt_latino = font_add("NotoSans.ttf", 24, false, false, 32, 255);

// cirílico añade el rango 0x0400..0x04FF
fnt_cirilico = font_add("NotoSans.ttf", 24, false, false, 0x0400, 0x04FF);
```

> ⚠️ **CJK (chino/japonés/coreano) son miles de glifos.** No se cargan por rango: se usa una
> fuente que ya los traiga (Noto Sans CJK) y se activa el cacheado por glifo con
> [`font_cache_glyph`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Fonts/font_cache_glyph.md)
> para no meter 20.000 glifos en la página de textura de golpe.
>
> 💡 **Elige una fuente por familia de idiomas** y cámbiala junto con el idioma. La familia
> **Noto** de Google cubre casi todos los alfabetos con el mismo estilo, y es de uso libre.

---

## 5 · Traducción asistida por IA — el flujo moderno

Aquí está lo que hace 2026 distinto de 2010: **no contratas diez traductores para el borrador,
generas los diez idiomas con un LLM y luego los revisas.** Es exactamente el método con el que
esta biblioteca tradujo el manual de GameMaker (ver
[`_indice/traduccion/README.md`](../_indice/traduccion/README.md)).

**Paso 1 — tu `es.json` es la única fuente.** Escribes solo en español.

**Paso 2 — un script pide al LLM que traduzca las claves que falten**, conservando las
`{variables}` intactas. El patrón, en Python, con el CLI que tengas (aquí `codex`, pero vale
cualquiera):

```python
# traducir_idioma.py — es.json → en.json, respetando {variables} y claves
import json, subprocess, sys

idioma_destino = sys.argv[1]          # "en", "fr", "de"…
es = json.load(open("datafiles/idiomas/es.json", encoding="utf-8"))
try:
    ya = json.load(open(f"datafiles/idiomas/{idioma_destino}.json", encoding="utf-8"))
except FileNotFoundError:
    ya = {}

# solo las claves que aún no están traducidas: reanudable y barato
faltan = {k: v for k, v in es.items() if k not in ya}
if not faltan:
    print("nada que traducir"); sys.exit(0)

prompt = (
    f"Traduce estos textos de un videojuego del español al idioma '{idioma_destino}'. "
    "Devuelve SOLO un JSON con las mismas claves. Conserva intactas las {variables} "
    "entre llaves y no traduzcas nombres propios. Textos:\n"
    + json.dumps(faltan, ensure_ascii=False, indent=1)
)
# … llamar al LLM, parsear su JSON, fusionar con `ya`, guardar {idioma}.json …
```

**Paso 3 — revisas.** La IA acierta el 90 %; el 10 % (tono, términos del juego, longitud que
rompe la UI) lo ajustas a mano. La clave: **el LLM hace el trabajo mecánico, tú decides.**

> 🔺 **Lo que la IA NO debe tocar, y por eso va en el prompt:**
> - Las `{variables}` — si traduce `{nombre}` a `{name}`, la interpolación se rompe.
> - Los nombres propios del juego (personajes, zonas, hechizos).
> - El formato JSON y las claves.
>
> ⚠️ **La longitud cambia.** El alemán es ~30 % más largo que el español; el chino, más corto.
> Un botón que cabe en español revienta en alemán. Prueba la UI en el idioma más largo, no solo
> en el tuyo. Diseña con holgura o con texto que se autoescala.
>
> 💡 **Guarda una memoria de traducción** (las claves ya traducidas) para no re-traducir —y no
> re-pagar— lo que no ha cambiado. Es lo que hace `_indice/traduccion/tm.py` con el manual:
> reanudable, solo toca lo nuevo.

---

## Las trampas

| Trampa | Consecuencia |
|---|---|
| Un texto escrito a pelo en el código | Nunca se traduce; se queda en español para todos |
| Plurales con "+s" | Roto en ruso, árabe, polaco… |
| La IA traduce `{variables}` | La interpolación deja de funcionar |
| Fuente sin los glifos del idioma | Texto en blanco en ruso/CJK |
| Probar solo en tu idioma | La UI revienta en alemán (30 % más largo) |
| Re-traducir todo cada vez | Tiempo y dinero tirados; usa memoria de traducción |
| Texto faltante = pantalla en blanco | Devuelve `[[clave]]` para verlo |

---

## Ver también

- [`_indice/traduccion/README.md`](../_indice/traduccion/README.md) — el sistema de traducción por IA de esta biblioteca, aplicable a tu juego
- [16 · Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — para refrescar la UI al cambiar de idioma
- [10 · Visual Novel y narrativa](./10%20-%20Visual%20Novel%20y%20narrativa.md) — donde el texto es el 90 % del juego
- [14 · Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — guardar el idioma elegido

---

## Localización de audio y voz

Este documento monta la tabla de idiomas y `txt()`, pero **no dice nada del audio**: la voz
grabada tiene su propio sistema, construido encima de la misma clave que usa este documento.
[`13 · 24` — Voz, diálogo y localización de audio](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/24%20-%20Voz%2C%20diálogo%20y%20localización%20de%20audio.md)
cubre: la convención `voz_<clave>_<idioma>` que hace que la MISMA clave de este documento
nombre también el fichero de voz; la resolución en runtime con `voz_localizada_obtener()` y su
caída a solo subtítulos cuando un idioma no está doblado; los *audio groups* por idioma
(`audio_group_load`/`unload`) y su impacto real en memoria frente al tamaño del paquete; y la
decisión de cuándo doblar, doblar parcialmente o solo subtitular cada idioma.
