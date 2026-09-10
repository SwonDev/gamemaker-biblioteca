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

> ⚠️ **`idioma_cargar()` va en un script, no en el `Create` de ningún objeto.** §3 la llama de
> nuevo desde donde arranca el juego y, por separado, desde el menú de Opciones cuando el
> jugador cambia de idioma — objetos distintos casi con toda seguridad. No lee ni escribe
> ninguna variable de instancia (solo `global.idioma`/`global.textos`), así que no tiene ninguna
> razón para vivir ligada a un objeto concreto: declararla en un evento la limitaría a ese
> objeto y reventaría con `Variable X.idioma_cargar(...) not set before reading it` en cuanto
> otro la llamara — el mismo mecanismo que
> [`04 · 19` §1](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md#1--el-conductor).
> Va en el mismo script que `txt()` (§2, `scr_idioma`).

```gml
/// scr_idioma — cargar el idioma (misma familia que txt(), §2)
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
/// uso — "nombre" y "zona" son ejemplo: sustitúyelos por los datos reales de tu partida
draw_text(x, y, txt("dialogo_bienvenida", { nombre: nombre_jugador, zona: "el Bosque" }));
draw_text(x, y, txt_n("monedas", global.monedas));    // "Tienes 1 moneda" / "Tienes 5 monedas"
```

> 🔺 **Devolver `[[clave]]` cuando falta no es un adorno.** Al jugar en un idioma a medio
> traducir, ves de un vistazo qué falta, en vez de un texto en blanco o el juego caído.
>
> ⚠️ **Los plurales NO son "+s".** En español «1 moneda / 2 monedas» parece trivial, pero en
> ruso hay tres formas y en árabe seis. Por eso cada cantidad tiene su clave, no una regla
> hardcodeada. Para idiomas con plurales complejos, amplía `txt_n` con las claves que haga
> falta (`_pocas`, `_muchas`).

**El error que nadie ve hasta que traduce: concatenar la frase.**

```gml
/// ❌ da por hecho el orden de palabras del español
draw_text(x, y, "Has encontrado " + item.nombre + ".");
```

```gml
/// ✅ la frase COMPLETA vive en la clave; la variable solo rellena un hueco
draw_text(x, y, txt("obtuviste_objeto", { objeto: item.nombre }));
```

```json
// es.json
{ "obtuviste_objeto": "Has encontrado {objeto}." }
```

En alemán o en japonés el objeto puede necesitar ir **antes** del verbo, o la frase entera
reordenarse alrededor de él; una concatenación en español asume que ese orden es universal y no
lo es. Con `{variables}` dentro de la clave, cada idioma reordena la frase entera como le haga
falta — el código nunca decide el orden, solo rellena el hueco.

---

## 2 bis · Género gramatical

`txt_n` resuelve la cantidad; nada en este documento resolvía todavía el **género**. «Estás
listo» / «Estás lista» es el mismo problema con otro eje: sin un patrón, cada traductor decide
por su cuenta cómo nombrar la clave alternativa, y las claves dejan de ser consistentes entre
idiomas.

```gml
/// scr_idioma — sufijo de género: la misma idea que txt_n(), para masculino/femenino/neutro
function txt_g(_base, _genero) {
    var _clave = _base + "_" + _genero;   // "estado_listo_m" / "estado_listo_f" / "estado_listo_n"

    // si el idioma no distingue género (inglés, por ejemplo), la clave con sufijo no existe:
    // cae a la clave base sin más, sin que haga falta una tabla de qué idioma sí distingue
    if (!variable_struct_exists(global.textos, _clave)) return txt(_base);
    return txt(_clave);
}
```

```json
// es.json
{
    "estado_listo_m": "Estás listo",
    "estado_listo_f": "Estás lista",
    "estado_listo_n": "Todo listo"
}
```

```gml
/// uso: el género del PERSONAJE (no una regla gramatical automática) decide la clave
draw_text(x, y, txt_g("estado_listo", jugador.genero));   // jugador.genero = "m" / "f" / "n"
```

> 💡 **`_m`/`_f`/`_n` son una convención de este documento, no una norma de GameMaker.** Úsala
> tal cual o cambia las letras; lo que importa es que sea **la misma** en todas las claves y en
> todos los idiomas, para que un traductor sepa qué añadir sin preguntar.

---

## 2 ter · Números y fechas por región

⚠️ **GameMaker no tiene ningún soporte de configuración regional en el runtime.** Verificado:

```sh
python3 "_indice/buscar.py" --listar locale_
# 0 símbolos empiezan por «locale_»
```

`string_format(val, tot, dec)` siempre usa el **punto** como separador decimal y nunca inserta
separador de miles (`string_format(1234.5, 1, 1)` → `"1234.5"`, no `"1.234,5"`). Y
`date_date_string(date)` imprime la fecha en un orden fijo del motor, no en el orden del
idioma activo. Si tu juego se traduce, esto se construye a mano, con una tabla de datos propia:

```gml
/// scr_idioma_formato — separador de miles, separador decimal y orden de fecha,
/// por idioma. GameMaker no ofrece nada de esto: es una tabla propia.
global.formato_regional = {
    es: { separador_miles: ".", separador_decimal: ",", orden_fecha: "d/m/a" },
    en: { separador_miles: ",", separador_decimal: ".", orden_fecha: "m/d/a" },
    de: { separador_miles: ".", separador_decimal: ",", orden_fecha: "d.m.a" },
    ja: { separador_miles: ",", separador_decimal: ".", orden_fecha: "a/m/d" },
};

/// @func numero_formatear(_valor, [_decimales])
/// @desc Aplica el separador de miles y decimal del idioma activo sobre lo que
///       devuelve string_format() (que siempre usa punto y nunca separa miles).
function numero_formatear(_valor, _decimales = 0) {
    var _cfg   = global.formato_regional[$ global.idioma];
    var _bruto = string_format(_valor, 1, _decimales);   // "1234.5" — sin miles, con punto

    var _punto   = string_pos(".", _bruto);
    var _entera  = (_punto > 0) ? string_copy(_bruto, 1, _punto - 1) : _bruto;
    var _decimal = (_punto > 0) ? string_copy(_bruto, _punto + 1, string_length(_bruto) - _punto) : "";

    // insertar el separador de miles cada tres cifras, recorriendo de derecha a izquierda
    var _con_miles = "";
    var _total     = string_length(_entera);
    for (var _i = _total; _i >= 1; _i--) {
        _con_miles = string_char_at(_entera, _i) + _con_miles;
        var _restantes = _total - _i + 1;
        if ((_restantes mod 3 == 0) && (_i > 1)) _con_miles = _cfg.separador_miles + _con_miles;
    }

    return (_decimal == "") ? _con_miles : _con_miles + _cfg.separador_decimal + _decimal;
}

/// @func fecha_formatear(_fecha)
/// @desc date_date_string() imprime en un orden fijo; esto respeta orden_fecha del idioma.
function fecha_formatear(_fecha) {
    var _cfg = global.formato_regional[$ global.idioma];
    var _d = string(date_get_day(_fecha));
    var _m = string(date_get_month(_fecha));
    var _a = string(date_get_year(_fecha));

    switch (_cfg.orden_fecha) {
        case "d/m/a": return $"{_d}/{_m}/{_a}";
        case "m/d/a": return $"{_m}/{_d}/{_a}";
        case "a/m/d": return $"{_a}/{_m}/{_d}";
        case "d.m.a": return $"{_d}.{_m}.{_a}";
        default:      return date_date_string(_fecha);   // fallback: el formato fijo del motor
    }
}
```

```gml
/// uso
draw_text(x, y, numero_formatear(1234.5, 1));   // es → "1.234,5"  ·  en → "1,234.5"
draw_text(x, y, fecha_formatear(date_current_datetime()));   // es → "7/9/2026" · en → "9/7/2026"
```

> 🔺 **`global.formato_regional` es una tabla de este documento, no una API de GameMaker.**
> Amplíala con cada idioma que soportes; los cuatro valores de arriba son ejemplo, no norma.

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

> 🔺 **Los glifos son necesarios, pero no bastan.** Con árabe y hebreo, además del glifo hace
> falta que la letra cambie de forma según su posición en la palabra (*shaping* contextual) y
> que el texto se reordene de derecha a izquierda (BiDi). Esto **no** es un límite de
> GameMaker: **Scribble ya lo resuelve solo, sin llamar a nada**, y el ajuste de línea en
> chino/japonés/coreano ya funciona sin espacios. Verificado en el código de la librería →
> [`07 · 18` §6 — Escritura de derecha a izquierda (RTL) y CJK](../07%20-%20Ecosistema/18%20-%20Scribble%20-%20texto%20rico%20%28guía%20en%20español%29.md#6--escritura-de-derecha-a-izquierda-rtl-y-cjk).
> Este apartado cubre solo la parte que sí sigue siendo tuya: qué glifos tiene la fuente.

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

## 4 bis · ¿Cabe? — la regla del «idioma más largo» no se puede aplicar en bloque

Todo el mundo repite la misma regla: *diseña la caja con el idioma más largo y los demás
caben solos*. Aplicada en bloque, esa regla **deja texto fuera de pantalla**, y lo hace en
silencio: no hay error, no hay excepción, no aparece en las pruebas del idioma en que se
escribió el juego. Aparece en una captura, ya publicado.

**Medido sobre una tabla real de 79 claves, español e inglés, con una fuente de sprite:**

| Qué | Resultado |
|---|---|
| El español, **en total** | un 9,1 % más largo que el inglés |
| Pero **cadena a cadena** | **el inglés gana en 23 de las 79**, hasta 26 px más |
| Con la caja diseñada «para el español» | tres cadenas se salían igual |

La media no protege a la cadena concreta. `menu_options` puede ser más corto en español y
`pause_resume` más largo, y basta una para que el menú se vea roto. **La regla es correcta;
lo que está mal es aplicarla al idioma en vez de a cada cadena.**

### La herramienta que lo mide

```sh
python3 "$BIB/_indice/medir-caja-de-texto.py" idiomas/es.json idiomas/en.json \
    --hoja fuente.png --celda 8x11 --mapa-archivo mapa.txt --caja 356 --sep 1
```

Reproduce exactamente lo que hace `font_add_sprite_ext(spr, mapa, prop, sep)`: parte la
hoja en celdas iguales, cada celda es el glifo del carácter que ocupa esa posición en el
mapa, y con `prop = true` el avance es **la anchura pintada + `sep`**. No aplica kerning,
porque esa función tampoco. Lee el PNG él mismo, sin depender de Pillow. Sale con 0, 1 o 2
y **no escribe nada**.

Devuelve cuatro cosas, y las cuatro son fallos que no dan error en ejecución:

1. **Qué cadenas no caben**, con su anchura y en qué idioma.
2. **Qué palabra suelta es más ancha que la caja** — ahí partir la línea no arregla nada.
3. **Qué caracteres no están en el mapa de la fuente.** Cada uno **mide cero**: la palabra
   sale mutilada *y la propia cuenta de anchura se queda corta*, mintiendo a tu favor.
4. **Qué idioma gana cadena a cadena**, con el reparto. Si no gana siempre el mismo, la
   regla de oro no se puede aplicar en bloque y te lo dice.

> ✅ **Verificado contra una verdad de referencia.** El «Pixel Font Megapack» publica en su
> `.json` el avance (`adv`) de cada glifo. La medida de esta herramienta coincidió con la
> suya en **177 de 177**, lo que confirma de paso que `adv = anchura pintada + 1`.

### El espacio es el caso peor, y hay que mirarlo siempre

Si la hoja **no trae celda para el espacio**, `font_add_sprite_ext` no usa la anchura del
espacio: usa **la del carácter más ancho** ([`08 · 03`](../08%20-%20Referencia%20GML%20completa/03%20-%20Texto%20y%20fuentes.md#font_add_sprite_extspr-string_map-prop-sep)).
En la fuente medida eso convierte un espacio de 3 px en 9, y una frase de ocho palabras se
ensancha 48 px de golpe.

Medido sobre esa misma tabla de 79 claves:

- **Sin la celda del espacio: tres cadenas desbordan.**
- **Con la celda añadida: cabe todo, cero problemas.**

No es un detalle cosmético: es la diferencia entre publicar con texto cortado o no. La
opción `--espacio N` responde a «¿y si la añadimos?» antes de dibujarla, y el informe
avisa de que ese número está forzado y no es lo que hará GameMaker hoy.

> ⚠️ **Y una tercera trampa del español que no tiene que ver con la caja:** `string_upper()`
> y `string_lower()` **solo cubren de la A a la Z** — el manual lo dice literalmente.
> `string_upper("La Última Raíz")` devuelve `"LA úLTIMA RAíZ"`. Si un título va en
> mayúsculas, va escrito así **en la clave**, no convertido en tiempo de ejecución. El
> aviso completo y las tres salidas están en
> [`08 · 12`](../08%20-%20Referencia%20GML%20completa/12%20-%20Strings.md#string_upperstring).

---

## 4 ter · El texto que NO es un literal, y por eso no lo caza nadie

La regla de oro de este documento —«ni un texto suelto en el código»— se comprueba buscando
cadenas escritas a pelo dentro de un `draw_text`. **Hay un segundo camino que ese `grep` no
ve**: una **función** que devuelve el texto ya hecho, en su idioma.

**Medido, y encontrado mirando una captura del juego corriendo — no leyendo código ni logs.**
`InputVerbGetBindingName()`, de la librería **Input 10.2.2**, devuelve los nombres de tecla en
inglés: `arrow left`, `arrow up`, `space`, `escape`, `backspace`. Las teclas de un solo carácter
(`A`, `Z`, `X`) salen bien, que es lo que hace que el problema se vea tarde.

En un juego en español eso es **el único texto que llega a pantalla sin pasar por `txt()`**, y
no lo detecta nada:

- el `grep` de literales no lo ve — **no hay ninguna cadena escrita**, es un valor devuelto;
- el compilador no dice nada, porque no hay ningún error;
- y se ve perfectamente… en inglés, en medio de una frase en español.

La propia documentación de esa función lo avisa: la recomienda solo *«for debugging or
alpha-quality games»* y remite al complemento **Binding Icons** para lo demás.

### Cómo se comprueba

```sh
python3 "$BIB/_indice/auditar-juego-completo.py" <proyecto>
```

Lista las funciones cuyo valor se dibuja tal cual en un `draw_text`, saltándose las que sí son
seguras: `txt()` y cualquier `txt_*` propia, y las que convierten números (`string`,
`string_format`, `real`, `chr`…). Es un **aviso**, no un error: componer con una función propia
que ya devuelve algo traducido es correcto. Lo que persigue es el caso en que esa función
devuelve texto en otro idioma **y nadie se entera**.

### Qué hacer si tu juego enseña asignaciones de teclas

Una pantalla de reasignación o el panel recordatorio de
[`04 · 27` §6](./27%20-%20Accesibilidad.md) necesitan **una tabla de claves `tecla_*` propia**
—`tecla_flecha_izquierda`, `tecla_espacio`, `tecla_escape`— o el complemento de iconos de la
propia librería. Nunca el nombre que devuelve la función, tal cual, dentro de una frase.

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

## 6 · Coste real de localizar y qué idiomas priorizar

⚠️ **Criterio de negocio, no verificado contra una fuente primaria en esta sesión** — trátalo
como punto de partida, no como dato cerrado.

Traducir no es gratis ni instantáneo aunque el borrador salga de un LLM: cada idioma añade
revisión humana (§5, paso 3), una hoja de grabación si hay voz
([`13 · 24` §2.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/24%20-%20Voz%2C%20diálogo%20y%20localización%20de%20audio.md#23-la-hoja-de-grabación-generada-no-escrita-a-mano)),
QA de que la UI no revienta (§5) y mantenimiento cada vez que el guion cambia. Ninguno de esos
costes desaparece por traducir con IA; lo único que se abarata es el primer borrador.

El orden habitual del sector para un juego indie que sale primero en inglés es:

```
inglés → EFIGS (español, francés, italiano, alemán) → chino simplificado
       → japonés / coreano → portugués de Brasil → ruso
```

Es el orden que maximiza jugadores alcanzados por idioma añadido, **no** una regla fija para tu
juego: un shooter competitivo y una visual novel tienen audiencias distintas. La decisión real
debe apoyarse en los **datos de wishlist por región de la propia página de Steam del juego**
(Steamworks los da desglosados por país), no en esta tabla genérica.

> 💡 **Traducir es la parte barata; sostener la traducción es la cara.** Una traducción que
> nadie revisa cuando el guion cambia se desincroniza sola. `[[clave]]` (§2) y la hoja de
> grabación regenerada ([`13 · 24` §2.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/24%20-%20Voz%2C%20diálogo%20y%20localización%20de%20audio.md#23-la-hoja-de-grabación-generada-no-escrita-a-mano))
> son lo que hace visible el desfase antes de que llegue a producción.

---

## Las trampas

| Trampa | Consecuencia |
|---|---|
| Un texto escrito a pelo en el código | Nunca se traduce; se queda en español para todos |
| Concatenar la frase en vez de usar `{variables}` | Roto en alemán/japonés: el orden de palabras no es universal |
| Plurales con "+s" | Roto en ruso, árabe, polaco… |
| Género sin sufijo de clave (`_m`/`_f`/`_n`) | Cada traductor lo resuelve distinto; las claves dejan de ser consistentes |
| `string_format`/`date_date_string` sin tabla regional | Números y fechas en el orden y separador equivocados para ese idioma |
| La IA traduce `{variables}` | La interpolación deja de funcionar |
| Fuente sin los glifos del idioma | Texto en blanco en ruso/CJK |
| Un botón o logo con texto quemado en el sprite | Se traduce todo el juego menos ESE texto, y nadie se acuerda |
| Probar solo en tu idioma | La UI revienta en alemán (30 % más largo) |
| Re-traducir todo cada vez | Tiempo y dinero tirados; usa memoria de traducción |
| Texto faltante = pantalla en blanco | Devuelve `[[clave]]` para verlo |

---

## Ver también

- [`_indice/traduccion/README.md`](../_indice/traduccion/README.md) — el sistema de traducción por IA de esta biblioteca, aplicable a tu juego
- [16 · Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — para refrescar la UI al cambiar de idioma
- [10 · Visual Novel y narrativa](./10%20-%20Visual%20Novel%20y%20narrativa.md) — donde el texto es el 90 % del juego
- [14 · Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — guardar el idioma elegido
- [`07 · 18` §6 — Scribble: RTL y CJK](../07%20-%20Ecosistema/18%20-%20Scribble%20-%20texto%20rico%20%28guía%20en%20español%29.md#6--escritura-de-derecha-a-izquierda-rtl-y-cjk) — árabe, hebreo y chino/japonés/coreano ya resueltos por la librería de texto
- [`12 · 05` §8 — Catálogo de librerías de localización](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte%2C%20audio%20y%20niveles.md#8-localización) — destaca **Unic** (mayúsculas y orden correcto con ñ) y **small_pp_localization_tool** (exporta la hoja de traducción a hoja de cálculo, sin reimplementar `13 · 24` §2.3)

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
