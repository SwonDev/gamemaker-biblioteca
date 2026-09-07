# 18 · Scribble — texto rico y con efectos (guía en español)

> **Scribble** (de @jujuadams) es la librería de texto de GameMaker: formato en línea (colores,
> tamaños), **efectos animados** (temblor, arcoíris, onda), efecto máquina de escribir,
> auto-ajuste de línea y fuentes de calidad. Su documentación está solo en inglés; esta es una
> **guía en español** con la API verificada contra el código descargado en
> `11 - Código descargado/librerias/texto-y-tipografia/Scribble`.
>
> **También resuelve de fábrica el árabe y el hebreo** (formas contextuales y reordenamiento
> BiDi) **y el ajuste de línea en chino/japonés/coreano sin espacios**, sin que llames a nada
> especial — ver [§6](#6--escritura-de-derecha-a-izquierda-rtl-y-cjk).

---

## Por qué Scribble y no `draw_text`

`draw_text` dibuja una cadena de un color y una fuente. Scribble te da, en una sola línea:
texto multicolor, palabras que tiemblan, un typewriter que escribe letra a letra, y ajuste
automático de ancho. Es lo que usan casi todos los juegos de GameMaker con diálogo o UI seria.

```gml
/// lo mínimo: una cadena con formato, ajustada a 400 px, dibujada
scribble("Hola [c_yellow]mundo[/c]!").wrap(400).draw(x, y);
```

**El patrón es una cadena de métodos:** `scribble(texto).wrap(...).draw(...)`. Cada método
devuelve el mismo objeto, así los encadenas.

---

## 1 · Formato en línea (los comandos entre corchetes)

Dentro del texto, `[comando]` cambia el formato hasta el siguiente `[/]` (reset) o `[/comando]`.

```gml
scribble("Texto normal [c_red]rojo[/c] y [scale,2]grande[/scale] otra vez normal").draw(x, y);
```

| Comando | Efecto |
|---|---|
| `[c_red]` `[c_blue]` `[#ff8800]` | Color (constante GML o hex) |
| `[scale,1.5]` | Tamaño (multiplicador) |
| `[alpha,0.5]` | Transparencia |
| `[fnt_titulo]` | Cambiar de fuente |
| `[/]` | **Resetear todo** al formato base |
| `[/c]` `[/scale]` | Resetear solo un aspecto |

---

## 2 · Efectos animados

Aquí Scribble brilla: palabras que se mueven, sin que tú animes nada.

```gml
scribble("Un jefe [shake]TIEMBLA[/shake] y un tesoro [rainbow]brilla[/rainbow]").draw(x, y);
```

Los efectos disponibles (funciones `scribble_anim_*`, verificadas en el código):

| Comando | Movimiento |
|---|---|
| `[wave]` | Ondea arriba y abajo |
| `[shake]` | Tiembla (nervios, daño) |
| `[rainbow]` | Colores que fluyen |
| `[jitter]` | Vibración fina |
| `[pulse]` | Late (crece y encoge) |
| `[wobble]` | Se bambolea |
| `[blink]` | Parpadea |
| `[cycle]` | Cicla colores |
| `[wheel]` | Rueda el color por rueda cromática |

> 🔺 **Los efectos se ajustan globalmente** con `scribble_anim_wave(...)`, `scribble_anim_shake(...)`,
> etc. — velocidad, amplitud. Ver `python3 _indice/buscar.py --codigo scribble_anim_shake`.

---

## 3 · Efecto máquina de escribir (typewriter)

Para diálogos que aparecen letra a letra. Se usa un **typist** (mecanógrafo):

```gml
/// Create — crear el mecanógrafo una vez
typista = scribble_typist();

/// Draw — dibujar el texto revelándose progresivamente
scribble("Bienvenido, aventurero...").wrap(400).draw(x, y, typista);

/// avanzar el typewriter (en Step): velocidad de escritura
typista.in(0.5);    // 0.5 caracteres por frame; sube para ir más rápido

/// saltar al final (el jugador pulsa para ver todo de golpe)
if (input_confirmar) typista.skip();
```

> 💡 **El typewriter de Scribble entiende los efectos y colores**: el texto se revela letra a
> letra Y con sus animaciones. Es lo que hace que un diálogo se sienta vivo. Ver
> [10 · Visual Novel](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md).

---

## 4 · Ajuste, alineación y medida

```gml
var _texto = scribble("Un párrafo largo que se ajusta solo").wrap(300);
_texto.align(fa_center, fa_top);        // alineación horizontal y vertical
var _alto = _texto.get_height();         // medir para colocar cosas debajo
var _ancho = _texto.get_width();
_texto.draw(x, y);
```

> ⚠️ **`scribble(...)` construye un modelo de texto y lo cachea por la cadena exacta.** Dibujar
> la misma cadena cada frame es barato (se reutiliza el modelo). Pero construir cadenas
> **distintas** cada frame (concatenando un número que cambia) llena la caché: para texto que
> cambia mucho (un contador), usa `draw_text` normal o cachea con cabeza.

---

## 5 · Fuentes y macros

```gml
/// las fuentes de GameMaker se usan DIRECTAMENTE por su nombre en el texto,
/// no hace falta registrarlas: [fnt_titulo] cambia a esa fuente
scribble("[fnt_titulo]TÍTULO[/font] texto normal").draw(x, y);

/// «hornear» un contorno o sombra en una fuente (efecto permanente y barato)
scribble_font_bake_outline_4dir("fnt_titulo", "fnt_titulo_borde", c_black, false);

/// una macro: un atajo reutilizable ([enfado] en vez de escribir [c_red][shake] cada vez)
scribble_add_macro("enfado", "[c_red][shake]");
scribble("¡[enfado]FUERA DE AQUÍ[/]!").draw(x, y);
```

---

## 6 · Escritura de derecha a izquierda (RTL) y CJK

> **La biblioteca daba a entender, por omisión, que el árabe, el hebreo o el chino eran «solo
> cuestión de fuente»** ([`04 · 21` §4](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md#4--fuentes-y-glifos--la-trampa-de-los-alfabetos-no-latinos)).
> Es falso. Cargar los glifos correctos es necesario, pero un alfabeto RTL además necesita que
> cada letra cambie de **forma** según su posición en la palabra (*shaping* contextual) y que el
> **orden visual** se invierta (BiDi, *bidirectional text*). **Scribble ya hace las dos cosas,
> sin que llames a nada.** Verificado en el propio código de la librería, dentro de
> `11 - Código descargado/librerias/texto-y-tipografia/Scribble/`.

### 6.1 `scribble(...)` ya aplica *shaping* y BiDi

```gml
/// Create — una fuente con el rango Unicode árabe (0x0600-0x06FF), como usa
/// obj_test_arabic, el propio objeto de pruebas de Scribble para este caso
scribble_font_set_default("fnt_noto_arabic");

/// Draw — nada más. Scribble decide las formas inicial/media/final/aislada de
/// cada letra y reordena visualmente de derecha a izquierda por su cuenta
scribble("توقف مؤقت").wrap(400).draw(x, y);
```

Esto es, literalmente, lo que hace `obj_test_arabic` (`Create_0.gml` fija la fuente,
`Draw_0.gml` construye el elemento con `scribble(...)` y lo dibuja con `.draw()`): no hay
ninguna llamada a una función de *shaping* ni de reordenamiento a mano. Por dentro, el
generador de Scribble pasa el texto por su *pipeline* de finalización BiDi
(`__scribble_gen_5_finalize_bidi.gml`, verificado) antes de decidir en qué orden se dibujan los
glifos. Con hebreo es igual de directo — sin *shaping* contextual (el hebreo no lo necesita),
pero con la misma reordenación BiDi automática:

```gml
scribble_font_set_default("fnt_noto_hebrew");
scribble("שלום עולם").draw(x, y);
```

> 🔺 **Lo único que sigue siendo cosa tuya es la fuente.** Necesita los glifos del alfabeto
> (rango Unicode correcto en `font_add`, o una fuente que ya los traiga) — eso es
> [`04 · 21` §4](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md#4--fuentes-y-glifos--la-trampa-de-los-alfabetos-no-latinos).
> Pero la **dirección** de escritura y la **forma** de cada letra ya no son tu problema.

### 6.2 `StringArabicParse` y `StringHebrewParse`: para cuando NO usas Scribble

Si por lo que sea dibujas con `draw_text` nativo en vez de con Scribble, las mismas dos
transformaciones existen sueltas, verificadas en su propio código fuente:

```gml
/// StringArabicParse(_string) — aplica el shaping contextual árabe Y reordena BiDi;
/// devuelve la cadena YA lista para draw_text
draw_set_font(fnt_noto_arabic);
draw_text(x, y, StringArabicParse("توقف مؤقت"));

/// StringHebrewParse(_string) — solo reordena BiDi (el hebreo no tiene shaping contextual)
draw_set_font(fnt_noto_hebrew);
draw_text(x, y, StringHebrewParse("שלום עולם"));
```

Las dos llaman por dentro a `GlyphArrayBiDiReorder(_glyphArray, _rightToLeftHint, _copy)`, la
primitiva de reordenamiento que comparten — verificado en `GlyphArrayBiDiReorder.gml`,
`StringArabicParse.gml` y `StringHebrewParse.gml`. No hace falta llamarla directamente salvo
que construyas tu propio *pipeline* de texto.

> ⚠️ **`StringArabicParse`, `StringHebrewParse` y `GlyphArrayBiDiReorder` son de Scribble, no
> del runtime**: no aparecen en `buscar.py`. Sus firmas se verificaron leyendo el `.gml` real,
> como pide `AGENTS.md` para el código de librerías de terceros.
>
> 🔺 **Los `__scribble_gen_*` (con doble guion bajo) son el motor interno de Scribble.** Se
> citan aquí solo como evidencia de que el comportamiento existe de verdad en el código — no se
> llaman desde fuera de la librería.

### 6.3 CJK: el ajuste de línea ya funciona sin espacios

Chino, japonés y coreano no separan palabras con espacios, así que el `.wrap()` que corta por
espacios en español o inglés no tendría dónde cortar. Scribble ya lo resuelve: por dentro, cada
carácter CJK se marca con la constante `ISOLATED_CJK` (verificado en
`__scribble_gen_4_build_words.gml`) y se trata como una «palabra» independiente, rompible en
cualquier punto — así que `.wrap()` puede cortar la línea entre dos caracteres CJK
cualesquiera, igual que cortaría entre dos palabras separadas por un espacio en español.

```gml
/// el mismo .wrap() de siempre; nada especial que llamar para que ajuste CJK
scribble("これはテストです。長い文章でも自動的に折り返されます。").wrap(400).draw(x, y);
```

> 💡 **Las fuentes CJK y su cacheado siguen siendo tu problema** (miles de glifos: ver
> [`04 · 21` §4](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md#4--fuentes-y-glifos--la-trampa-de-los-alfabetos-no-latinos)
> y `font_cache_glyph`). Lo que Scribble ya resuelve es **dónde se puede cortar la línea**, no
> qué glifos tiene la fuente.

---

## Las trampas

| Trampa | Consecuencia |
|---|---|
| Construir cadenas distintas cada frame | Llena la caché de modelos; ralentiza |
| Olvidar `[/]` al cerrar formato | El color/efecto se «derrama» al resto |
| Usar `draw_text` para diálogo con estilo | Pierdes efectos, typewriter y ajuste |
| No llamar a `typista.in()` en Step | El typewriter no avanza |
| Asumir que árabe/hebreo/CJK son «solo cuestión de fuente» | No pruebas `scribble()` con ese texto y crees que GameMaker no puede — sí puede (§6) |

> 🔺 **Estos métodos NO están en `buscar.py`** (son de la librería, no del runtime). Verifica una
> firma en `11 - Código descargado/librerias/texto-y-tipografia/Scribble/scripts/`.

---

## Ver también

- [10 · Visual Novel y narrativa](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md) — el diálogo con typewriter
- [19 · Chatterbox — diálogos ramificados](./19%20-%20Chatterbox%20-%20diálogos%20Yarn%20%28guía%20en%20español%29.md) — Scribble dibuja, Chatterbox decide qué se dice
- [03 · Texto y fuentes](../08%20-%20Referencia%20GML%20completa/03%20-%20Texto%20y%20fuentes.md) — el `draw_text` nativo
- [21 · Localización e idiomas](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md) §4 — fuentes y glifos por idioma, complemento del §6 de aquí
- Repo oficial: <https://github.com/JujuAdams/Scribble>
