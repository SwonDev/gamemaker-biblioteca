# 27 · Accesibilidad

> Que tu juego lo pueda jugar más gente: daltónicos, personas con baja visión, con dificultades
> motrices, o que juegan con el sonido apagado. No es caridad: amplía tu público, y en consola
> es **requisito de certificación** de varias plataformas.
>
> **Cobertura parcial detectada:** solo había un toggle de screen shake. Aquí está el sistema.

---

## La regla: cada ajuste es una opción, y el juego la respeta

Todo lo de aquí vive en la [pantalla de Opciones](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md)
como un ajuste más, y se guarda con los demás. La accesibilidad no es un modo aparte: es un
puñado de opciones que el resto del código consulta.

```gml
/// global.a11y — el struct de accesibilidad, cargado al arrancar
global.a11y = {
    daltonismo: "ninguno",     // "ninguno" | "protanopia" | "deuteranopia" | "tritanopia"
    daltonismo_modo: "corregir", // "corregir" (el que usa el jugador) | "simular" (herramienta de depuración, §1)
    subtitulos: true,
    escala_texto: 1.0,         // 1.0 … 1.5 — el texto de la UI en general
    reduce_motion: false,      // menos flashes, menos shake, menos partículas
    shake: true,
    hold_para_toggle: false,   // los "mantén pulsado" se vuelven "pulsa una vez"

    // --- ampliado en esta revisión: ver el número de sección de cada bloque ---
    subtitulos_estilo: {       // personalización de la CAJA de subtítulos, aparte de escala_texto (§2)
        fondo_alpha: 0.6,      // opacidad de la caja: 0 = sin caja, 1 = opaca
        escala: 1.0,           // tamaño del TEXTO del subtítulo, independiente de escala_texto
        color: c_white,
    },
    audio_mono: false,         // §5 — el sonido posicional deja de venir "de un lado"
    indicador_sonido: true,    // §5 — flecha en el borde de pantalla hacia la fuente
    haptics: 1.0,              // §4 — 0 = sin vibración, 1 = intensidad completa
    narracion_menus: false,    // §8 — voz pregrabada al mover el foco (NO es un lector de pantalla)
    tipografia: "por_defecto", // §6 bis — "por_defecto" | "alta_legibilidad" (sans-serif alternativa)

    // --- modo asistido: cada variable es una asistencia independiente (§7) ---
    asistencia_punteria: false,  // ya la consume 04 · 34 §aim_assist_corregir()
    velocidad_juego: 1.0,        // 0.5 … 1.0 — multiplica game_set_speed()
    invencibilidad: false,
    recursos_infinitos: false,
};
```

---

## 1 · Daltonismo: no comuniques SOLO con color

El error más común: «los enemigos rojos hacen daño, los verdes te curan». Un 8 % de los hombres
no distingue rojo de verde. **Regla: el color nunca es la única señal.**

```gml
/// ❌ solo color
draw_sprite_ext(spr_orbe, 0, x, y, 1, 1, 0, es_bueno ? c_green : c_red, 1);

/// ✅ color + FORMA/ICONO (se entiende sin ver el color)
draw_sprite(es_bueno ? spr_orbe_cruz : spr_orbe_calavera, 0, x, y);
```

Y ofrece **paletas para cada tipo de daltonismo**, aplicadas con un shader de intercambio de
color sobre `application_surface`:

> 💡 **Lo más barato y efectivo no es el shader, es el diseño:** añade una forma, un icono o un
> patrón a lo que hoy distingues solo por color. Un shader de simulación de daltonismo (para
> probar) o de corrección es la segunda capa. Ver el palette swap en
> [08 · 06 — Shaders](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md).

> ⚠️ **Steam lo dice explícito para la etiqueta *Color Alternatives*: «no dependas solo de
> filtros de pantalla completa».** Si además de este shader ofreces modos predefinidos de
> daltonismo, deja también la opción de elegir colores concretos por elemento — el *palette
> swap* de [08 · 06](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md#palette-swap-intercambio-de-paleta)
> es la herramienta para eso. Ver §Steamworks, más abajo.

### 1.1 · El shader real: simulador y corrector por matrices

Un shader de daltonismo de verdad no es un tinte a ojo: es una **matriz 3×3** que transforma
cada píxel del color que ve una persona con visión típica al color que percibiría alguien con
protanopia, deuteranopia o tritanopia (modo **simular**, para que el equipo compruebe su propio
juego) — o, al revés, que **redistribuye** hacia los canales que la persona SÍ distingue el
color que perdería (modo **corregir**, el que activa el jugador). Las tres matrices de cada
modo se han compuesto a partir de las matrices RGB↔LMS y de colapso de cono publicadas en
`daltonize.py` (Joerg Dietrich, GPL-2, adaptación de Fidaner, Lin y Ozguven 2005 sobre el
modelo de Viénot, Brettel y Mollon 1999) — ver Fuentes. Se comprobaron dos invariantes antes de
usarlas: `rgb→lms` y `lms→rgb` son inversas (su producto da la identidad) y **cada matriz
conserva el blanco** (la suma de cada fila da 1, así que `(1,1,1)` sigue siendo blanco).

```gml
// scr_daltonismo — matrices reales de simulación y corrección, listas para el shader
// Verificado: no hay una función `shader_set_uniform_matrix` de propósito general para un
// uniform CUALQUIERA (esa firma es para las matrices integradas de GameMaker); por eso cada
// matriz se manda como tres uniforms `vec3` (una fila cada uno) con shader_set_uniform_f.

/// @func daltonismo_iniciar()
/// @desc Llamar una vez, en el Create del controlador persistente.
function daltonismo_iniciar() {
    global.daltonismo_matrices = {
        // "simular": cómo LO VE una persona con esa condición (herramienta de depuración)
        simular: {
            protanopia:   [[0.0686,  0.9314,  0.0000], [0.0686,  0.9314,  0.0000], [ 0.0137, -0.0137, 1.0000]],
            deuteranopia: [[0.4156,  0.5844,  0.0000], [0.4156,  0.5844,  0.0000], [-0.0424,  0.0424, 1.0000]],
            tritanopia:   [[1.0000, -0.0232,  0.0232], [0.0000,  1.0003, -0.0003], [ 0.0000,  1.0003,-0.0003]],
        },
        // "corregir": desplaza a los canales que SÍ distingue lo que perdería (daltonización)
        corregir: {
            protanopia:   [[1.0000,  0.0000, 0.0000], [ 0.5834,  0.4166, 0.0000], [0.6383, -0.6383, 1.0000]],
            deuteranopia: [[1.0000,  0.0000, 0.0000], [-0.0066,  1.0066, 0.0000], [0.4515, -0.4515, 1.0000]],
            tritanopia:   [[1.0000,  0.0000, 0.0000], [ 0.0000,  1.0160,-0.0160], [0.0000, -0.9840, 1.9840]],
        },
    };

    u_fila0  = shader_get_uniform(shd_daltonismo, "u_fila0");
    u_fila1  = shader_get_uniform(shd_daltonismo, "u_fila1");
    u_fila2  = shader_get_uniform(shd_daltonismo, "u_fila2");
}

/// @func daltonismo_dibujar(_pos, _ancho, _alto)
/// @desc Llamar en el Draw GUI del controlador de efectos, envolviendo (o no) a los demás
///       shaders de pantalla completa de 08 · 23 §1.2. Si el ajuste está en "ninguno", dibuja
///       sin shader: coste cero.
function daltonismo_dibujar(_pos, _ancho, _alto) {
    if (global.a11y.daltonismo == "ninguno") {
        draw_surface_stretched(application_surface, _pos[0], _pos[1], _ancho, _alto);
        return;
    }

    var _m = global.daltonismo_matrices[$ global.a11y.daltonismo_modo][$ global.a11y.daltonismo];
    shader_set(shd_daltonismo);
    shader_set_uniform_f(u_fila0, _m[0][0], _m[0][1], _m[0][2]);
    shader_set_uniform_f(u_fila1, _m[1][0], _m[1][1], _m[1][2]);
    shader_set_uniform_f(u_fila2, _m[2][0], _m[2][1], _m[2][2]);
    draw_surface_stretched(application_surface, _pos[0], _pos[1], _ancho, _alto);
    shader_reset();
}
```

**Fragment shader** (`shd_daltonismo.fsh`) — el vertex shader es el estándar de
[08 · 06 §Anatomía de un shader](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md#anatomía-de-un-shader-de-gamemaker),
no se repite:

```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

// Cada uniform es UNA FILA de la matriz 3x3, para no depender de cómo GLSL
// construye un mat3 a partir de vectores (columnas, no filas: es la trampa habitual).
uniform vec3 u_fila0;
uniform vec3 u_fila1;
uniform vec3 u_fila2;

void main()
{
    vec4 color_base = texture2D(gm_BaseTexture, v_vTexcoord) * v_vColour;

    vec3 transformado = vec3(
        dot(u_fila0, color_base.rgb),
        dot(u_fila1, color_base.rgb),
        dot(u_fila2, color_base.rgb)
    );

    gl_FragColor = vec4(clamp(transformado, 0.0, 1.0), color_base.a);
}
```

Uso, siguiendo el envoltorio de pantalla completa de
[08 · 23 §1.2](../08%20-%20Referencia%20GML%20completa/23%20-%20Recetario%20de%20shaders%20de%20efecto.md#12-dónde-vive-cada-shader-por-instancia-o-de-pantalla-completa):

```gml
// Create de objFxController
application_surface_draw_enable(false);
daltonismo_iniciar();

// Draw GUI de objFxController
var _pos   = application_get_position();
var _ancho = _pos[2] - _pos[0];
var _alto  = _pos[3] - _pos[1];
daltonismo_dibujar(_pos, _ancho, _alto);
```

> 🔺 **El "simulador" no es para el jugador.** `daltonismo_modo: "simular"` es una herramienta
> de depuración: actívala tú desde una tecla de *debug* o una escena de pruebas para comprobar
> cómo se ve tu paleta con cada tipo de daltonismo, y desactívala antes de publicar. Lo único
> que expone la pantalla de Opciones al jugador es la lista de la §1 (`daltonismo`), que
> siempre usa el modo `"corregir"`.
>
> ⚠️ **Estas matrices son un modelo aproximado de percepción, no una garantía.** El propio
> Machado et al. (2009) avisan de que sus parámetros se ajustaron para dicromacía completa y
> con datos de un puñado de personas; alguien con tricromacia anómala (la mayoría de los casos
> reales) verá el efecto **demasiado fuerte**. Ofrece siempre la opción de desactivarlo
> (`"ninguno"`) y no sustituyas nunca la forma/icono de la §1 por el shader: son complementarios,
> no alternativos.

---

## 2 · Subtítulos y texto legible

```gml
/// todo lo hablado, también escrito — respetando la escala de texto
if (global.a11y.subtitulos) {
    draw_set_font(fnt_subtitulo);
    var _escala = global.a11y.escala_texto;
    draw_text_transformed(x, y, txt(clave_dialogo), _escala, _escala, 0);
}
```

- **Escala de texto** (1.0–1.5): multiplica el tamaño con `draw_text_transformed`. Diseña los
  cuadros de texto con holgura para que quepa al 150 %.
- **Contraste**: texto claro sobre una **caja oscura semitransparente**, nunca directamente
  sobre el escenario (ilegible sobre fondos claros).
- **Subtítulos para efectos importantes**: `[puerta crujiendo]`, `[pasos detrás]` ayudan a quien
  juega sin sonido.

> ⚠️ **Prueba tu texto al 150 % de escala**, no solo al 100 %. Es donde revienta la UI, igual
> que con los idiomas largos ([21 · Localización](./21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md)).

### 2.1 · Nombre del hablante, personalización y «antes de que suene»

La duración y el *typewriter* de un subtítulo ya están resueltos en
[13 · 12 §6.9](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md#69-subtítulos-velocidad-de-texto-y-voces>)
(`subtitulo_duracion()`) y no se repiten aquí. Lo que falta es **quién habla** y **cómo se ve**
la caja — las dos cosas que pide Game Accessibility Guidelines *Hearing, Intermediate* y que
Steam agrupa bajo la etiqueta *Subtitle Options* (ver §Steamworks):

```gml
/// obj_dialogo · Draw GUI — subtítulo con nombre del hablante y caja personalizable
/// Verificado: draw_set_font, draw_set_alpha, draw_set_colour, draw_rectangle,
///             draw_text_ext_color, string_height
if (global.a11y.subtitulos) {
    var _estilo  = global.a11y.subtitulos_estilo;
    var _escala  = _estilo.escala;             // NO global.a11y.escala_texto: son ajustes distintos
    var _x = 120, _y_caja = display_get_gui_height() - 160;
    var _ancho_caja = display_get_gui_width() - 240;

    draw_set_font(fnt_subtitulo);
    var _alto_texto = string_height_ext(txt(clave_dialogo), -1, _ancho_caja - 40) * _escala;
    var _alto_caja = _alto_texto + (hablante_actual != "" ? 36 : 0) + 32;

    // caja de fondo: opacidad configurable, nunca el escenario desnudo detrás del texto
    if (_estilo.fondo_alpha > 0) {
        draw_set_alpha(_estilo.fondo_alpha);
        draw_set_colour(c_black);
        draw_rectangle(_x, _y_caja, _x + _ancho_caja, _y_caja + _alto_caja, false);
        draw_set_alpha(1);
    }

    var _texto_y = _y_caja + 16;
    if (hablante_actual != "") {
        // GAG Hearing Intermediate: «indicación visual de quién habla ahora mismo»
        draw_set_colour(c_yellow);                     // destacado, no solo el color por defecto
        draw_text(_x + 20, _texto_y, hablante_actual);
        draw_set_colour(_estilo.color);
        _texto_y += 30;
    }

    draw_text_ext_color(_x + 20, _texto_y, txt(clave_dialogo), -1, _ancho_caja - 40,
                         _estilo.color, _estilo.color, _estilo.color, _estilo.color, 1);
}
```

> 🔺 **`hablante_actual` es el nombre visible del personaje que habla**, guardado junto al resto
> del estado del diálogo (`texto_actual`, `clave_voz_actual` de 13 · 12 §6.9). Si tu ficha de
> diálogo ya tiene un campo `hablante` como la de
> [13 · 12 §7.1](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md#71-la-ficha-de-personaje-cinco-casillas-no-cinco-páginas>),
> es ese mismo valor: no crees un segundo sistema de nombres.

**Activos antes del primer sonido.** GAG lo pide literalmente («ensure subtitles are or can be
turned on before any sound is played»): si tu juego abre con un vídeo o una cinemática con
diálogo, el ajuste `global.a11y.subtitulos` tiene que estar **cargado y aplicado** antes de esa
escena, no leído perezosamente la primera vez que se abre Opciones. Ver el orden de arranque de
[00 · Anatomía de un juego completo](./00%20-%20Anatomía%20de%20un%20juego%20completo.md): los
ajustes se cargan en `rm_init`, antes de cualquier sala jugable.

**Personalización, en la pantalla de Opciones** — tres widgets más en la lista de
[04 · 25](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md), con el mismo patrón `slider`/`toggle`
que ya usa esa pantalla:

```gml
{ tipo: "slider", clave: "subtitulos_fondo",  etiqueta: txt("op_sub_fondo"),
  val: 0.6, min: 0, max: 1 },
{ tipo: "slider", clave: "subtitulos_escala", etiqueta: txt("op_sub_escala"),
  val: 1.0, min: 0.75, max: 2.0 },
```

Y en `aplicar_ajuste()` de esa misma pantalla:

```gml
case "subtitulos_fondo":  global.a11y.subtitulos_estilo.fondo_alpha = _w.val; break;
case "subtitulos_escala": global.a11y.subtitulos_estilo.escala      = _w.val; break;
```

> 💡 **El rango de la escala del subtítulo llega a 2.0, no a 1.5** como `escala_texto` general
> (§Legibilidad, [13 · 05 §1.2](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#12-legibilidad-el-tamaño-mínimo-de-texto-no-es-una-opinión>)):
> quien depende del subtítulo para seguir la trama entera necesita más margen que quien solo
> agranda un menú.

---

## 3 · Reduce motion — menos movimiento agresivo

Flashes rápidos y sacudidas fuertes provocan mareo, y a algunas personas, **convulsiones**. Un
ajuste que las atenúa:

```gml
/// el screen shake respeta el ajuste (ya en la receta 15)
function shake(_fuerza) {
    if (!global.a11y.shake || global.a11y.reduce_motion) return;
    // … aplicar el shake …
}

/// los flashes de pantalla se suavizan o se quitan
function flash_pantalla(_alpha) {
    if (global.a11y.reduce_motion) _alpha = min(_alpha, 0.3);   // tope suave
    // … dibujar el flash …
}
```

> ⚠️ **Nunca hagas flashes de pantalla completa a más de 3 por segundo.** Es el umbral de
> riesgo de convulsiones fotosensibles (norma WCAG). Con `reduce_motion`, quítalos del todo.

> 💡 **Esto es lo que Steam etiqueta *Camera Comfort*** en la ficha de tienda: la lista exacta
> que pide es *screen shake*, *motion blur* y *camera bob/sway* ajustables o desactivables. El
> *screen shake* ya pasa por `reduce_motion` (arriba, y en
> [13 · 05](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md>)); si tu
> [cámara](<../13 - Diseño y producción de videojuegos/19 - Cámaras de juego - encuadre, seguimiento y control.md>)
> añade *bob* al caminar o desenfoque de movimiento, pásalos por el mismo ajuste antes de
> marcar la etiqueta. Ver §Cómo declararlo en la ficha de Steam.

---

## 4 · Accesibilidad motriz

- **Hold-to-toggle**: los «mantén pulsado para correr/agacharte» se vuelven «pulsa para
  activar/desactivar». Quien no puede mantener una tecla sigue jugando.
- **Rebinding completo**: reasignar cualquier control (ver
  [25 · Opciones](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md) §5). Imprescindible para mandos
  adaptados.
- **Sin quick-time events con ventanas imposibles**, o con la ventana ajustable.

```gml
/// un "mantener para correr" que respeta hold_para_toggle
if (global.a11y.hold_para_toggle) {
    if (InputPressed("correr")) corriendo = !corriendo;   // conmuta (API de Input: PascalCase)
} else {
    corriendo = InputCheck("correr");                       // mantener
}
```

### 4.1 · El slider de vibración: no es opcional, es la pauta *Basic*

Game Accessibility Guidelines lo pone en **Motor, Basic** y otra vez en **Cognitive,
Intermediate**, con el mismo texto exacto: *«include toggle/slider for any haptics»*. Un juego
que solo tiene «vibración: sí/no» ya cumple lo mínimo; un slider de intensidad es mejor. La
tabla de *qué* debería vibrar y con qué fuerza según el tipo de golpe es de
[04 · 15 §game feel](./15%20-%20Game%20feel%20y%20juice.md); aquí solo va el **ajuste** y el
límite que la accesibilidad exige: nunca vibración en bucle indefinido.

```gml
// scr_haptics — el ajuste, y un pulso con decaimiento que respeta el slider
// Verificado: gamepad_set_vibration, gamepad_is_supported, gamepad_is_connected,
//             gamepad_get_device_count, array_create

/// @func haptics_iniciar()
/// @desc Llamar una vez, en el Create del controlador persistente.
function haptics_iniciar() {
    var _n = gamepad_get_device_count();
    global.__haptics_fuerza          = array_create(_n, 0);
    global.__haptics_restante        = array_create(_n, 0);
    global.__haptics_duracion_inicial = array_create(_n, 1);
}

/// @func haptics_pulso(_slot, _fuerza, _duracion_pasos)
/// @desc Un pulso de vibración que decae solo y nunca se queda encendido.
///       _fuerza va de 0 a 1 ANTES de aplicar el slider de accesibilidad.
function haptics_pulso(_slot, _fuerza, _duracion_pasos) {
    if (global.a11y.haptics <= 0)   return;   // el toggle/slider en 0 es "apagado", de verdad
    if (!gamepad_is_supported())    return;
    if (!gamepad_is_connected(_slot)) return;

    global.__haptics_fuerza[_slot]           = _fuerza * global.a11y.haptics;
    global.__haptics_restante[_slot]         = _duracion_pasos;
    global.__haptics_duracion_inicial[_slot] = _duracion_pasos;
}

/// obj_juego · Step — decae el pulso activo de cada mando conectado
for (var _slot = 0; _slot < array_length(global.__haptics_restante); _slot++) {
    if (global.__haptics_restante[_slot] <= 0) continue;

    global.__haptics_restante[_slot]--;
    var _t = global.__haptics_restante[_slot] / global.__haptics_duracion_inicial[_slot];
    gamepad_set_vibration(_slot, global.__haptics_fuerza[_slot] * _t,
                                  global.__haptics_fuerza[_slot] * _t);

    if (global.__haptics_restante[_slot] <= 0) gamepad_set_vibration(_slot, 0, 0);
}
```

En la pantalla de Opciones, un `slider` más de [04 · 25](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md)
(`clave: "haptics"`, `min: 0, max: 1`) que escribe directamente en `global.a11y.haptics` —
aplicado en vivo, como todos los demás.

> ⚠️ **Nunca reactives la vibración sin dejar que decaiga antes.** Un golpe que llega mientras
> el pulso anterior sigue activo no debe sumar fuerza indefinidamente: sustituye el pulso, no lo
> acumula. Y respeta el mismo umbral de las convulsiones fotosensibles de §3 en espíritu: la
> vibración continua y fuerte puede resultar tan hostil como el flash que ya limitas ahí.

---

## 5 · Sonido: toggle mono/estéreo e indicador visual de dirección

Esto es **Hearing, Intermediate** en Game Accessibility Guidelines, con dos pautas separadas que
van juntas en la práctica: *«provide a stereo/mono toggle»* (crítico para sordera unilateral: si
un disparo suena solo por el canal derecho, quien no oye de ese lado no lo oye nunca) y *«ensure
that all important supplementary information — eg. the direction you are being shot from —
conveyed by audio is replicated in text/visuals»*. La mezcla y el volumen posicional en general
son de [13 · 09](<../13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md>)
y no se repiten; esto es la capa de accesibilidad **encima** de esa mezcla.

### 5.1 · Por qué no hay un «modo mono» de una sola llamada

⚠️ **Verificado: el runtime no tiene un efecto de bus que colapse estéreo a mono.**
`AudioEffectType` (`08 · 06` y
[`02 · 07`](<../02 - Novedades 2026/07 - Audio - buses y efectos.md>)) solo declara
`Bitcrusher`, `Compressor`, `Delay`, `EQ`, `Gain`, `HiShelf`, `HPF2`, `LoShelf`, `LPF2`,
`PeakEQ`, `Reverb1` y `Tremolo` — ninguno toca el paneo o el ancho estéreo. Tampoco existe una
función tipo «`audio_master_downmix`». Lo que SÍ hay, y es lo que genera el paneo del sonido
posicional, es el sistema de oyente + emisor de
[13 · 09 §5.2](<../13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md#52-un-anillo-de-emisores-y-dónde-va-el-oyente>)
(`audio_listener_position`, `audio_emitter_position`): el paneo sale de dónde está el emisor
**respecto al oyente**, no de un parámetro aparte.

### 5.2 · La técnica: mismo volumen, sin desplazamiento lateral

La idea, verificada y propia de esta biblioteca (no es una función del manual): en modo mono, en
vez de mover el emisor a su posición real, se le coloca **a la misma distancia real del
oyente** (así el volumen por caída no cambia) pero **sobre la línea de mirada del oyente** (así
no hay componente lateral que produzca paneo). El sonido deja de "venir de un lado" sin sonar ni
más alto ni más bajo.

```gml
// scr_audio_mono — reposiciona el emisor sobre el eje de mirada si el toggle está activo
// Verificado: point_direction, lengthdir_x, lengthdir_y, audio_emitter_position

/// @func emisor_posicionar(_emisor, _ex, _ey, _ox, _oy, _mirada_dir)
/// @param {Id.SoundEmitter} _emisor      El emisor ya creado con audio_emitter_create()
/// @param {Real} _ex,_ey                 Posición REAL de la fuente del sonido
/// @param {Real} _ox,_oy                 Posición del oyente (normalmente la cámara)
/// @param {Real} _mirada_dir             Ángulo de mirada del oyente, en grados
function emisor_posicionar(_emisor, _ex, _ey, _ox, _oy, _mirada_dir) {
    if (!global.a11y.audio_mono) {
        audio_emitter_position(_emisor, _ex, _ey, 0);
        return;
    }

    var _dist = point_distance(_ox, _oy, _ex, _ey);       // misma distancia real: mismo volumen
    var _fx = _ox + lengthdir_x(_dist, _mirada_dir);      // pero siempre "de frente": sin paneo
    var _fy = _oy + lengthdir_y(_dist, _mirada_dir);
    audio_emitter_position(_emisor, _fx, _fy, 0);
}
```

> ⚠️ **Esto es paneo posicional, no un downmix del máster.** La música y el ambiente en
> estéreo (los que `13 · 09 §7` manda importar como estéreo, no como emisores) siguen sonando
> con su anchura estéreo original: el toggle no los toca, porque no transportan información de
> juego que se pueda perder — es exactamente la distinción que hace la pauta (*«important
> supplementary information»*, no «cualquier sonido»). Si tu juego panea manualmente algo fuera
> del sistema de emisores (por ejemplo con un efecto de `Gain` por canal), pásalo también por
> `global.a11y.audio_mono` a mano.

### 5.3 · El indicador visual: la otra mitad de la pauta

Para el sonido que SÍ importa (de dónde viene el disparo, el rugido del jefe fuera de cámara),
Steam lo dice igual de explícito en la etiqueta *Stereo Sound*: *«for critical gameplay sounds,
consider also providing an option for a visual indicator as to the direction the sound came
from»*. Un anillo simple sobre el borde de la GUI, reutilizando el ángulo que ya calcula
`emisor_posicionar()`:

```gml
// scr_indicador_sonido — flecha en el borde de la GUI hacia una fuente de sonido importante
// Verificado: array_push, array_length, array_delete, point_direction, lengthdir_x,
//             lengthdir_y, display_get_gui_width, display_get_gui_height, draw_sprite_ext

/// @func indicador_sonido_iniciar()
function indicador_sonido_iniciar() { global.__indicadores_sonido = []; }

/// @func indicador_sonido_mostrar(_wx, _wy, _duracion_pasos = 45)
/// @desc Llamar en el MISMO sitio donde se reproduce el sonido informativo
///       (disparo fuera de pantalla, rugido de jefe, puerta que se abre a tu espalda).
function indicador_sonido_mostrar(_wx, _wy, _duracion_pasos = 45) {
    if (!global.a11y.indicador_sonido) return;
    array_push(global.__indicadores_sonido, { x: _wx, y: _wy, vida: _duracion_pasos });
}

/// obj_juego · Draw GUI
function indicador_sonido_dibujar(_ox, _oy) {
    var _radio = min(display_get_gui_width(), display_get_gui_height()) * 0.42;

    for (var _i = array_length(global.__indicadores_sonido) - 1; _i >= 0; _i--) {
        var _s = global.__indicadores_sonido[_i];
        _s.vida--;
        if (_s.vida <= 0) { array_delete(global.__indicadores_sonido, _i, 1); continue; }

        var _dir = point_direction(_ox, _oy, _s.x, _s.y);
        var _gx = display_get_gui_width()  * 0.5 + lengthdir_x(_radio, _dir);
        var _gy = display_get_gui_height() * 0.5 + lengthdir_y(_radio, _dir);
        draw_sprite_ext(spr_indicador_sonido, 0, _gx, _gy, 1, 1, _dir, c_white,
                         min(1, _s.vida / 15));   // se apaga suave en los últimos 15 pasos
    }
}
```

> 💡 **Este es el mismo hueco que ya señala [13 · 09 §5.4](<../13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md#54-dentro-y-fuera-de-pantalla>):**
> ese documento sube el volumen de lo que suena fuera de cámara; esta sección es el widget
> visual que le faltaba. Llama a `indicador_sonido_mostrar()` en el mismo punto donde ese
> documento decide reforzar el sonido (`en_pantalla(x, y, 0)` es `false`).

En Opciones: un `toggle` («Sonido mono») y otro («Indicador de dirección»), ambos escribiendo en
`global.a11y.audio_mono` / `global.a11y.indicador_sonido` con el patrón ya conocido de
[04 · 25](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md).

---

## 6 · Recordatorio de controles y de objetivo

GAG lo pide dos veces en *Cognitive, Intermediate*: *«indicate/allow reminder of controls
during gameplay»* e *«indicate/allow reminder of current objectives during gameplay»*. **Esto
ya está resuelto entero** en
[04 · 40 §2.5 y §3.7](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md#37-el-panel-de-objetivo-y-controles) —
`panel_ayuda_dibujar()`, `objetivo_actual_texto()` y `control_tecla()`/`control_boton_mando()`
leyendo la asignación real tras el rebinding — así que no se repite aquí. Lo único que añade
esta sección es la conexión con el resto del sistema: el panel de ayuda **no depende** de
`global.a11y.hold_para_toggle` ni de ningún otro ajuste de este documento salvo, indirectamente,
de que los iconos de sus controles reflejen el rebinding de [04 · 25 §5](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#5--reasignar-controles-rebinding).

---

## 6 bis · Accesibilidad cognitiva

Game Accessibility Guidelines dedica una categoría entera a esto —**Cognitive (Thought / memory
/ processing information)**— y hasta esta revisión la biblioteca no tenía ni una sola mención a
dislexia ni a TDAH (`buscar.py --todo "dislexia"` y `--todo "TDAH"`: cero en las once carpetas de
contenido). No hay una función de GML que "active el modo dislexia": es, otra vez, diseño + un
puñado de ajustes que el resto del código respeta, igual que todo lo anterior.

### 6 bis.1 · Tipografía: legible por defecto, y con alternativa

GAG lo pide en *Cognitive, Basic* y otra vez en *Vision, Basic*, con el mismo texto exacto:
**«use an easily readable default font size»** y **«use simple clear text formatting»**. Para
dislexia en concreto —GAG no la nombra por su nombre, pero es la razón práctica más citada del
oficio para este ajuste— la recomendación habitual es una **tipografía sans-serif humanista, sin
cursiva en texto largo y con buen espaciado entre letras**: evita fuentes decorativas o con
serifas finas en cualquier texto que no sea puramente ornamental (un logo, un título de portada).

```gml
/// global.a11y.tipografia — "por_defecto" | "alta_legibilidad" (definida arriba, «La regla»)
/// Verificado: font_add, draw_set_font, asset_get_index. fnt_ui_defecto y fnt_ui_legible son
/// DOS fuentes ya creadas en el editor de fuentes del IDE, mismo tamaño en punto — una es la
/// de marca del juego y la otra una sans-serif de alta legibilidad — no se generan en runtime.

/// @func fuente_ui()
/// @desc La fuente que debe usar CUALQUIER texto de interfaz. Sustituye a escribir
///       `fnt_ui_defecto` a pelo en cada draw_set_font del proyecto.
function fuente_ui() {
    return (global.a11y.tipografia == "alta_legibilidad") ? fnt_ui_legible : fnt_ui_defecto;
}
```

> 💡 **Un ajuste, un sitio.** Como con la escala de texto (§2), el resto del juego no necesita
> saber que este ajuste existe: cualquier `draw_set_font(fnt_ui_defecto)` pasa a ser
> `draw_set_font(fuente_ui())`, y el cambio queda resuelto en un solo sitio. En Opciones, un
> `toggle` más de [04 · 25](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md) con el mismo
> patrón que todos los demás.
>
> ⚠️ **Esta biblioteca no ha verificado hoy ninguna fuente concreta como «la» fuente para
> dislexia.** Tipos de letra como «OpenDyslexic» circulan mucho en foros de accesibilidad, pero
> su eficacia frente a una buena sans-serif convencional está discutida en la literatura y no se
> ha comprobado aquí contra un estudio primario — no la des por una solución verificada. Lo que
> sí es una recomendación sólida y barata, con o sin esa fuente concreta: sans-serif, sin cursiva
> en texto largo, tamaño ajustable (§2) y alto contraste (§1, y §Legibilidad de
> [13 · 05](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#12-legibilidad-el-tamaño-mínimo-de-texto-no-es-una-opinión>)).

### 6 bis.2 · Longitud de línea, interlineado y texto sin justificar

Tres decisiones de maquetación que no piden código nuevo, solo disciplina al construir el cuadro
de texto — la misma pauta de formato simple y claro de arriba, aplicada al párrafo entero y no
solo a la tipografía:

- **Líneas cortas.** Un cuadro de diálogo o de tutorial que fuerza líneas de más de 60-70
  caracteres cuesta más de seguir para cualquiera, y bastante más con dislexia o con dificultades
  de atención. `draw_text_ext` ya envuelve el texto al ancho que le des (es lo que usan §2.1 de
  este documento y [04 · 40](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md)):
  la palanca real es **cuánto ancho le das a la caja**, no una función nueva.
- **Interlineado generoso.** El parámetro `sep` de `draw_text_ext`/`string_height_ext` (la
  separación entre líneas) admite subirlo por encima del mínimo que cabe; en texto largo
  (tutoriales, diálogos, créditos) un 30-50 % más de interlineado que el ajustado se lee sin
  esfuerzo extra.
- **Nunca justificado.** GameMaker no tiene una función de "justificar texto" —verificado:
  `--listar draw_text` no devuelve nada parecido a `draw_text_justify`—, así que lo fácil es
  cumplir esto por omisión: **no construyas tú mismo un justificado a mano** metiendo espacios
  extra para que el borde derecho cuadre. El texto alineado a la izquierda, con el borde derecho
  irregular, es además lo que recomienda la literatura de tipografía accesible para dislexia: el
  ojo no tiene que recalcular el espaciado entre palabras en cada línea nueva.

### 6 bis.3 · Iconos junto al color, otra vez, y por qué aquí también

§1 ya exige forma o icono además de color, para daltonismo. La misma regla protege a alguien con
dificultades de procesamiento por un motivo distinto: **un icono con forma fija se reconoce de un
vistazo tras un par de repeticiones; un color por sí solo hay que recordar qué significaba cada
vez**. Es la misma pauta general de GAG —*«ensure no essential information is conveyed by a fixed
colour alone»* (Vision, Basic)— haciendo doble trabajo: sirve a quien no distingue el color y a
quien lo distingue perfectamente pero no quiere memorizar un código. No hay nada nuevo que
implementar aquí — es una razón más para no relajar §1.

### 6 bis.4 · Ritmo y pausas: nada esencial contra reloj

*«Do not make precise timing essential to gameplay — offer alternatives, actions that can be
carried out while paused, or a skip mechanism»* es, en el listado de GAG, una pauta de **Motor,
Advanced** — no de Cognitive—, pero su efecto es tan cognitivo como motriz: una ventana de
reacción exigida bloquea igual a quien no llega con el mando a tiempo que a quien necesita más
segundos para procesar qué está pasando en pantalla. **«Include an option to adjust the game
speed»** sí está listada dos veces, en *Motor, Basic* y en *Cognitive, Intermediate* — el mismo
patrón de doble cita que ya usa §4.1 para la vibración—, y ya está resuelta en `velocidad_juego`
de §7 de este mismo documento (`game_set_speed`): no se repite el código aquí.

Lo que añade esta sección es la lectura que falta: **una pausa real** —el menú de pausa de
[04 · 41 §3.4](./41%20-%20Transiciones,%20carga%20y%20pausa.md#34-el-menú-de-pausa-completo), que
congela temporizadores, IA y patrones de ataque, no solo la interfaz— es en sí misma una
asistencia cognitiva: le da a cualquiera el tiempo que necesite para releer un objetivo, un
cuadro de diálogo o el propio HUD sin perder progreso ni recibir daño mientras lo hace.

### 6 bis.5 · Recordatorio de objetivo: no se repite, solo se enlaza

Esto ya está resuelto entero en **§6** de este mismo documento —`panel_ayuda_dibujar()` y
`objetivo_actual_texto()`, ambos de
[04 · 40 §2.5 y §3.7](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md#37-el-panel-de-objetivo-y-controles)—.
La pauta de GAG que lo exige (*«indicate/allow reminder of current objectives during gameplay»*)
es *Cognitive, Intermediate*, así que pertenece aquí en espíritu; el código ya está escrito
arriba y no hay nada que añadir salvo el enlace.

### 6 bis.6 · El marco legal europeo: qué dice, y qué no dice, sobre videojuegos

⚠️ **Verificado hoy solo el texto del artículo citado, sin interpretación jurídica ni
jurisprudencia posterior, y esto no es asesoramiento legal** — misma reserva que el resto de
[13 · 11 §9](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#9--legal-y-administrativo-mínimo>).

La **European Accessibility Act** (Directiva (UE) 2019/882) fija requisitos de accesibilidad para
ciertos productos y servicios en la Unión Europea, exigibles desde el **28 de junio de 2025**. Se
leyó el texto consolidado en EUR-Lex el 06-09-2026 y **el videojuego, como producto, no aparece
en absoluto en la lista de su artículo 2** (ámbito de aplicación): ni «video game», ni «juego»,
ni ninguna categoría que lo nombre directamente — a diferencia de, por ejemplo, los servicios de
comercio electrónico, la banca de consumo o el acceso a servicios de comunicaciones electrónicas,
que sí están listados explícitamente en ese mismo artículo.

Lo que sí puede alcanzar a un juego, indirectamente, según ese mismo artículo 2:

| Elemento del artículo 2 que SÍ está en la Directiva | Cómo podría tocar a un juego |
|---|---|
| `e-commerce services` (art. 2.2.f) | Si vendes el juego o su DLC desde tu propia tienda web —no desde Steam o itch.io, que gestionan su propia conformidad—, esa tienda puede entrar en el ámbito |
| Terminales de consumo con capacidad informática interactiva usados para acceder a servicios de comunicaciones electrónicas o audiovisuales (art. 2.1.c-d) | No es el juego: es el hardware o el sistema operativo en el que corre, ya cubierto por su fabricante |
| El juego en sí, como producto de software independiente | **No listado** |

**No lo des por hecho sin comprobarlo tú antes de depender de ello.** Esta tabla resume una
lectura del texto legal de la Directiva a fecha 06-09-2026, no la interpretación de una autoridad
ni la trasposición concreta de tu país —cada Estado miembro traspone la Directiva a su propia ley,
con matices—, y no cubre si existe otra norma nacional sobre videojuegos al margen de esta
Directiva en concreto.

---

## 7 · Dificultad ajustable y modo asistido, como ajuste real

[13 · 01 §3.3](<../13 - Diseño y producción de videojuegos/01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md#33--dificultad-dinámica-las-dos-familias-y-cuál-elegir>)
ya explica **por qué** conviene la asistencia explícita sobre la dificultad dinámica oculta, con
el caso de *Celeste* y su «Modo Asistido». Esto es la traducción a variables: GAG lo llama
*«offer a wide choice of difficulty levels»* (General, Basic) e *«include assist modes such as
auto-aim and assisted steering»* + *«allow difficulty level to be altered during gameplay»*
(General, Intermediate).

```gml
/// Cada asistencia es UNA variable independiente en global.a11y (definidas arriba, «La regla»):
///   asistencia_punteria  — YA consumida por 04 · 34 §aim_assist_corregir(); no la reimplementes
///   velocidad_juego      — 0.5 … 1.0, multiplica la velocidad de simulación
///   invencibilidad       — el jugador no puede morir
///   recursos_infinitos   — munición/objetos consumibles no bajan de su valor actual

/// @func asistencia_aplicar_velocidad()
/// @desc Llamar al cambiar el ajuste, no cada Step: game_set_speed no hace falta repetirlo.
function asistencia_aplicar_velocidad() {
    game_set_speed(room_speed * global.a11y.velocidad_juego, gamespeed_fps);
}

/// en el sistema de daño (04 · 32), ANTES de aplicar el golpe
function recibir_dano(_cantidad) {
    if (global.a11y.invencibilidad) return;      // el golpe no cuenta: ni daño ni i-frames gastados
    // ... el pipeline normal de 04 · 32 ...
}

/// al consumir munición u objetos (04 · 34 / 04 · 09)
function consumir_recurso(_cantidad) {
    if (global.a11y.recursos_infinitos) return;  // no baja
    // ... descontar normalmente ...
}
```

**Las tres reglas de cómo se presenta**, tomadas literalmente de 13 · 01 §3.3 y de la cita de
Maddy Thorson sobre *Celeste* («rompe el juego, y aun así...»):

1. **Cambiable en caliente, desde el menú de pausa**, no solo antes de empezar la partida — es
   la pauta explícita de GAG. Vive en Opciones igual que cualquier otro ajuste
   ([04 · 25](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md)), accesible también desde el
   [menú de pausa](./41%20-%20Transiciones,%20carga%20y%20pausa.md#34-el-menú-de-pausa-completo).
2. **Nunca bloquea logros ni el final** por estar activa. Si tu juego reparte logros por
   Steamworks (`04 · 20`), no añadas una condición `!global.a11y.invencibilidad` a ninguno.
3. **El texto no lleva la palabra «trampa».** «Modo asistido» o «Ayudas de accesibilidad», nunca
   «Cheats» ni «Modo fácil vergonzoso».

> 🔺 **`asistencia_punteria` no la implementa este documento.** Ya existe en
> [04 · 34 — Combate a distancia](./34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md)
> (`aim_assist_corregir()`), que ya la lee de `global.a11y`. Esta sección solo confirma dónde
> vive el interruptor y añade sus tres compañeras.

---

## 8 · Lo que GameMaker no puede hacer

Esta sección existe para que ningún LLM futuro intente inventarse una API que no está. Se
verificó con `python3 _indice/buscar.py --listar <prefijo>` contra el índice de símbolos del
runtime **GMS2 2026.0.0.23**, generado a partir de su `GmlSpec.xml` real:

| Se buscó | Resultado |
|---|---|
| `speech_` | **0 símbolos** |
| `tts_` | **0 símbolos** |
| `narrator` | **0 símbolos** |
| `accessib` | **0 símbolos** |
| `screenreader` / «screen reader» | Sin resultados |

**No existe lector de pantalla ni texto-a-voz nativos en GameMaker.** Tampoco hay una extensión
que lo aporte catalogada en
[07 · 03](<../07 - Ecosistema/03 - Extensiones oficiales y de terceros.md>) ni en
[12 · 02](<../12 - Utilidades e integraciones/02 - Extensiones nativas y del sistema.md>) — se
comprobó buscando «screen reader», «text to speech», «narrator» y «accesib» en ambos documentos:
cero coincidencias. Esto cierra la puerta a dos etiquetas concretas de la ficha de Steam:
*Narrated Game Menus* en su forma plena y *Playable without Vision* (ver §Steamworks). Si tu
proyecto necesita de verdad soporte de lector de pantalla del sistema operativo, la única vía
real es una **extensión nativa por plataforma** que tú mismo escribas contra la API de
accesibilidad de Windows/macOS/Linux — fuera del alcance de GML puro, y de esta biblioteca.

**Lo que SÍ se puede construir con GML real, sin inventar nada:**

- **Voz pregrabada de menús** (lo que Steam llama *Narrated Game Menus*, y GAG *Vision,
  Advanced*: *«provide pre-recorded voiceovers for all text, including menus and
  installers»*). No es un lector de pantalla — es un clip grabado por elemento, disparado
  cuando el foco cambia. Reutiliza el sistema de foco de
  [13 · 05 §2.2](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#22-navegación-con-mando-y-teclado-foco-orden-envolvente-y-repetición>):

```gml
// scr_narracion_menus — voz pregrabada al cambiar el foco, NO texto-a-voz
// Verificado: asset_get_index, audio_exists, audio_is_playing, audio_stop_sound,
//             audio_play_sound

global.__voz_menu_actual = -1;

/// @func narracion_foco(_elementos, _indice_nuevo, _indice_anterior)
/// @desc Llamar justo después de que menu_mover() (04 · 18) cambie el índice de foco.
function narracion_foco(_elementos, _indice_nuevo, _indice_anterior) {
    if (!global.a11y.narracion_menus)          return;
    if (_indice_nuevo == _indice_anterior)     return;

    if (global.__voz_menu_actual != -1 && audio_is_playing(global.__voz_menu_actual)) {
        audio_stop_sound(global.__voz_menu_actual);
    }

    var _snd = asset_get_index($"voz_menu_{_elementos[_indice_nuevo].clave}");
    if (_snd != -1 && audio_exists(_snd)) global.__voz_menu_actual = audio_play_sound(_snd, 10, false);
}
```

- **Alto contraste, iconos grandes y forma+color** (§1, y §Legibilidad de 13 · 05) siguen siendo
  válidos y gratuitos aunque no haya narración: no sustituyen al lector de pantalla, pero
  reducen cuánto lo necesita alguien con baja visión (no ceguera total).
- **Declara el límite, no lo escondas**: si alguien pregunta en el foro de Steam o en una reseña
  por soporte de lector de pantalla, la respuesta honesta es que el motor no lo ofrece de forma
  nativa — mejor decirlo en la ficha de accesibilidad (§Cómo declararlo en la ficha de Steam)
  que dejar que alguien lo descubra jugando.

---

## Checklist por niveles: Basic / Intermediate / Advanced

Game Accessibility Guidelines organiza sus ~100 pautas en tres niveles: **Basic** (fácil, aplica
a casi todos los juegos), **Intermediate** (requiere algo de planificación) y **Advanced**
(adaptaciones complejas, casos concretos). Este checklist es la parte de esa lista que este
documento y sus hermanos ya cubren — no la lista entera de GAG, que tiene pautas de multijugador
por voz, VR y otras que no aplican a la mayoría de proyectos de esta biblioteca.

### Basic

- [ ] Nada se comunica solo por color (forma/icono además) — §1
- [ ] Subtítulos activables para diálogo y efectos importantes — §2
- [ ] Texto escalable y sobre fondo con contraste — §2, [13 · 05 §1.2](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#12-legibilidad-el-tamaño-mínimo-de-texto-no-es-una-opinión>)
- [ ] Reduce motion: menos shake, menos flashes (nunca >3/s) — §3
- [ ] Toggle/slider de vibración (no solo sí/no) — §4.1
- [ ] Rebinding completo de controles — §4, [04 · 25 §5](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#5--reasignar-controles-rebinding)
- [ ] Todos los ajustes de accesibilidad se guardan y se recuerdan — «La regla», arriba
- [ ] Sin QTE de ventana imposible, o con alternativa — §4
- [ ] Al menos un nivel de dificultad ajustable — §7
- [ ] Tipografía legible por defecto, con alternativa de alta legibilidad — §6 bis.1

### Intermediate

- [ ] Hold-to-toggle para acciones sostenidas — §4
- [ ] Volúmenes separados (música/efectos/voz) — [04 · 25 §2](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#2--aplicar-de-verdad-cada-ajuste)
- [ ] Nombre del hablante en los subtítulos — §2.1
- [ ] Subtítulos personalizables (fondo, escala propia) — §2.1
- [ ] Subtítulos activos ANTES del primer sonido del juego — §2.1
- [ ] Toggle mono/estéreo — §5.1-5.2
- [ ] Indicador visual de dirección para sonido crítico — §5.3
- [ ] Recordatorio de controles y de objetivo en partida — §6, [04 · 40 §3.7](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md#37-el-panel-de-objetivo-y-controles)
- [ ] Líneas cortas, interlineado amplio y texto nunca justificado en cuadros largos — §6 bis.2
- [ ] Pausa real que congela temporizadores e IA, no solo la interfaz — §6 bis.4, [04 · 41 §3.4](./41%20-%20Transiciones,%20carga%20y%20pausa.md#34-el-menú-de-pausa-completo)
- [ ] Modo asistido cambiable en caliente, sin bloquear logros — §7
- [ ] Tutoriales interactivos y ayuda contextual — [04 · 40](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md)

### Advanced

- [ ] El límite del lector de pantalla está declarado, no escondido — §8
- [ ] Voz pregrabada de menús donde el presupuesto lo permita — §8
- [ ] Simulador de daltonismo disponible para el equipo en depuración — §1.1
- [ ] Playtesting con participantes con discapacidad, aunque sea un grupo pequeño — [13 · 10](<../13 - Diseño y producción de videojuegos/10 - Testing y QA.md>)

---

## Cómo declararlo en la ficha de Steam

Steam tiene un **Accessibility Feature Wizard** en la pestaña *Basic Info* de la ficha de
tienda: un cuestionario que marca etiquetas visibles al jugador y buscables en la tienda —
*Store Search* las indexa. La tabla cruza cada etiqueta con lo que este documento (y sus
hermanos) implementan de verdad; márcala solo si tu juego concreto cumple la recomendación real,
no solo por tener el código de este documento pegado.

| Etiqueta (categoría Steam) | ¿Cubierta aquí? | Dónde |
|---|---|---|
| Adjustable Difficulty (Gameplay) | ✅ si expones el modo asistido | §7 |
| Custom Volume Controls (Audio) | ✅ | [04 · 25 §2](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#2--aplicar-de-verdad-cada-ajuste) |
| Narrated Game Menus (Audio) | 🟡 parcial — voz pregrabada, no lector de pantalla del sistema | §8 |
| Stereo Sound (Audio) | ✅ | §5.1-5.2 |
| Adjustable Text Size (Visual) | ✅ — Steam pide poder escalar hasta **38 px a 1080p / 76 px a 4K** | §2, [13 · 05 §1.2](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#12-legibilidad-el-tamaño-mínimo-de-texto-no-es-una-opinión>) |
| Subtitle Options (Visual) | ✅ | §2.1 |
| Color Alternatives (Visual) | ✅ | §1 |
| Camera Comfort (Visual) | ✅ si el shake es el único efecto de cámara agresivo | §3 |
| Playable without Vision (Visual) | ❌ — exige lector de pantalla o audio-only completo | §8 |
| Playable without Quick Time Events (Input) | ✅ | §4 |
| Playable at Your Own Pace (Input) | ✅ — subtítulos sin límite de tiempo forzado, hold-to-toggle | §2, §4 |
| Save Anytime (Gameplay) | Fuera de este documento | [01 · 14](<../01 - Fundamentos/14 - Persistencia y archivos.md>) |
| Keyboard/Mouse/Touch Only Option (Input) | Depende del juego, no de este documento | [04 · 28](./28%20-%20Juegos%20para%20móvil%20%28táctil%29.md) para táctil |
| Surround Sound (Audio) | No evaluado en esta biblioteca | — |
| Chat Text-to-speech / Speech-to-text (Input) | Fuera de alcance — multijugador con chat de voz | [04 · 14 — Multijugador](./14%20-%20Multijugador.md) |

> ⚠️ **No marques una etiqueta que no cumples de verdad.** El wizard es una promesa pública al
> jugador que busca ese juego específicamente por tenerla; una etiqueta falsa es peor que no
> tenerla. Ver Fuentes para el enlace directo a la página de Steamworks con las recomendaciones
> completas de cada una.

También en el propio juego: **declara las funciones de accesibilidad dentro de un menú propio**
(GAG *General, Basic*: «provide details of accessibility features in-game»), no solo en la
tienda — la ficha de Steam no la ve nadie que ya haya comprado el juego.

---

## Ver también

- [25 · Menú de opciones y ajustes](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md) — donde viven estos toggles, y el rebinding de §4
- [40 · Tutorial, onboarding y prompts en pantalla](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md) — el recordatorio de controles y objetivo de §6, y los iconos que leen la asignación real
- [41 · Transiciones, carga y pausa](./41%20-%20Transiciones,%20carga%20y%20pausa.md) — dónde vive el interruptor del modo asistido durante la partida (§7)
- [15 · Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) — el shake que hay que poder desactivar (§3)
- [08 · 06 — Shaders](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md) — anatomía del shader y palette swap, base del shader de daltonismo (§1.1)
- [08 · 23 — Recetario de shaders de efecto](../08%20-%20Referencia%20GML%20completa/23%20-%20Recetario%20de%20shaders%20de%20efecto.md) — el envoltorio de pantalla completa que usa §1.1, y cómo encadenarlo con otros efectos
- [13 · 05 — UI y UX de juego](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md>) — legibilidad, contraste, foco y navegación de los que dependen §1-§2 y §8
- [13 · 09 — Diseño de sonido y mezcla](<../13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md>) — la mezcla y el «dentro/fuera de pantalla» sobre los que se apoya §5
- [13 · 12 — Diseño narrativo y diálogos](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md>) — `subtitulo_duracion()`, que §2.1 amplía sin repetir
- [13 · 01 — Diseño de juego](<../13 - Diseño y producción de videojuegos/01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md>) — la teoría del modo asistido que §7 traduce a variables
- [34 · Combate a distancia](./34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md) — `aim_assist_corregir()`, que ya consume `global.a11y.asistencia_punteria` de §7

---

## Fuentes

Consultadas el **2026-09-06**.

- Game Accessibility Guidelines, listado completo —
  <https://gameaccessibilityguidelines.com/full-list/> (abierta con
  `curl -A "Mozilla/5.0" ...`; el sitio bloquea el user-agent por defecto). Fuente de la
  categorización Basic/Intermediate/Advanced y de las citas literales: *«include toggle/slider
  for any haptics»* (Motor Basic / Cognitive Intermediate, base de §4.1), *«provide a
  stereo/mono toggle»* y *«ensure that all important supplementary information [...] conveyed
  by audio is replicated in text/visuals»* (Hearing Intermediate, base de §5), *«provide a
  visual indication of who is currently speaking»* y *«allow subtitle/caption presentation to
  be customised»* (Hearing Intermediate, base de §2.1), *«include assist modes such as
  auto-aim and assisted steering»* y *«allow difficulty level to be altered during gameplay»*
  (General Intermediate, base de §7), *«ensure screen reader support, including menus &
  installers»* y *«provide pre-recorded voiceovers for all text, including menus and
  installers»* (Vision Advanced, base de §8), *«don't rely on full-screen filters [for
  colour-blindness]»* no aparece en esta lista con esas palabras exactas — es la guía de Steam,
  citada aparte.
- Xbox Accessibility Guidelines, índice oficial —
  <https://learn.microsoft.com/en-us/gaming/accessibility/guidelines/> (Microsoft Learn,
  versión 3.2, «last updated on 2026-08-14»; abierta con `curl`). Confirma la numeración y el
  título de cada guía citada: **104 Subtitles and captions** (base de §2.1), **106 Screen
  narration** (base de §8 — no 103, que es *«additional channels for visual and audio cues»* y
  encaja mejor con §1), **110 Haptic feedback** (§4.1), **111 Audio description**. ⚠️ Solo se
  abrió el índice/TOC de cada guía: el contenido detallado de las páginas individuales devolvió
  404 con las rutas probadas, así que aquí solo se cita número + título, no el cuerpo completo
  de cada XAG. La cifra de 26 px/18 px de XAG 101 ya estaba citada con URL en
  [13 · 05 §1.2](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#12-legibilidad-el-tamaño-mínimo-de-texto-no-es-una-opinión>)
  antes de esta ampliación: no se ha vuelto a verificar aquí, se hereda tal cual.
- Steamworks, *Accessibility Features* —
  <https://partner.steamgames.com/doc/accessibility_features> (abierta con `curl`). Fuente
  completa de la tabla de §Cómo declararlo en la ficha de Steam: las 18 etiquetas exactas del
  *Accessibility Feature Wizard*, sus categorías (Gameplay/Audio/Visual/Input) y sus
  recomendaciones textuales — entre ellas la cifra de **38 px a 1080p / 76 px a 4K** para
  *Adjustable Text Size* (una cifra de Steam, distinta y con un propósito distinto a los 26/18 px
  de XAG 101: aquélla es el mínimo legible, ésta es hasta dónde debe poder escalar el texto) y
  la advertencia contra depender solo de filtros de pantalla completa en *Color Alternatives*,
  citada en §1.
- `daltonize.py` (Joerg Dietrich, licencia GPL-2; adaptación de Fidaner, Lin y Ozguven 2005
  sobre el modelo de Viénot, Brettel y Mollon 1999) —
  <https://raw.githubusercontent.com/joergdietrich/daltonize/master/daltonize/daltonize.py>
  (descargado con `curl`). Fuente de las matrices RGB→LMS, de colapso de cono por tipo de
  daltonismo y LMS→RGB que §1.1 compone en una única matriz RGB→RGB por modo; la composición y
  la comprobación de las dos invariantes (`rgb2lms · lms2rgb ≈ identidad`; cada matriz conserva
  el blanco) se hizo con NumPy en esta misma sesión, no viene ya calculada en la fuente.
- DaltonLens, *Open-source color blindness simulation* —
  <https://daltonlens.org/opensource-cvd-simulation/> (abierta con `curl`). Revisión técnica que
  contextualiza `daltonize.py`: confirma que el enfoque Viénot/Machado es el recomendado frente
  al «ColorMatrix» de una noche que circula sin control por muchos tutoriales de shaders, y que
  ninguno de los modelos es perfecto para tricromacía anómala (la advertencia de §1.1).
- `_indice/simbolos.json` de esta biblioteca (extraído del `GmlSpec.xml` del runtime GMS2
  2026.0.0.23) — fuente de verdad para cada símbolo citado en este documento, verificado uno por
  uno con `python3 _indice/buscar.py <símbolo>` antes de escribirlo, incluida la comprobación
  negativa de §8 (`--listar speech_`, `--listar tts_`, `--listar narrator`, `--listar accessib`:
  las cuatro, cero resultados) y la lista de tipos de `AudioEffectType` de §5.1
  (ya documentada en [02 · 07](<../02 - Novedades 2026/07 - Audio - buses y efectos.md>) y
  [13 · 09](<../13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md>), no
  vuelta a verificar contra el manual: se hereda de esos dos documentos).
- Game Accessibility Guidelines, categoría **Cognitive**, listado completo —
  <https://gameaccessibilityguidelines.com/full-list/> (abierta con `curl -A "Mozilla/5.0" ...`
  el 06-09-2026; fuente de §6 bis). Citas literales verificadas: *«use an easily readable default
  font size»* y *«use simple clear text formatting»* (Cognitive Basic, también Vision Basic; base
  de §6 bis.1-2), *«ensure no essential information is conveyed by a fixed colour alone»* (Vision
  Basic; base de §6 bis.3), *«include an option to adjust the game speed»* (listada dos veces:
  Motor Basic y Cognitive Intermediate; base de §6 bis.4), *«do not make precise timing essential
  to gameplay — offer alternatives, actions that can be carried out while paused, or a skip
  mechanism»* (Motor Advanced; base de §6 bis.4), *«indicate/allow reminder of current objectives
  during gameplay»* (Cognitive Intermediate; base de §6 bis.5, ya resuelta en §6/`04 · 40`).
- `--listar draw_text` de `_indice/buscar.py` — comprobación negativa de §6 bis.2: las 13
  funciones de la familia `draw_text*` no incluyen ninguna variante de justificado de texto.
- Directiva (UE) 2019/882 (European Accessibility Act), texto consolidado — EUR-Lex,
  <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019L0882> (leída completa el
  06-09-2026; 742 KB de texto, artículo 1 «Subject matter» y artículo 2 «Scope» revisados letra
  por letra). Fuente de la tabla de §6 bis.6: el artículo 2 no menciona videojuegos ni software
  de entretenimiento como producto o servicio en el ámbito de la Directiva; sí lista, entre
  otros, `e-commerce services` (art. 2.2.f) y los terminales de consumo de los apartados 2.1.c-d.

---

**Anti-alucinación — símbolos que se comprobaron y NO existen** (para que ningún LLM futuro
los vuelva a intentar): `speech_synthesize`, `speech_to_text`, `tts_speak`, `tts_say`,
`narrator_speak`, `accessibility_enable`, `screenreader_enable` (las siete formas obvias de
pedirle al runtime narración o reconocimiento de voz — ninguna existe: de ahí §8 completo),
`audio_effect_pan`, `audio_bus_set_pan`, `audio_master_downmix`, `AudioEffectType.Pan`,
`AudioEffectType.StereoWidth` (no hay ningún efecto de paneo o de ancho estéreo en
`AudioEffectType`: de ahí la técnica de reposicionar el emisor de §5.2 en vez de un ajuste de
mezcla), `shader_set_uniform_mat3`, `shader_get_uniform_matrix` (ninguna de las dos existe;
la que sí existe, `shader_set_uniform_matrix(handle)`, no sirve para un `uniform mat3` propio:
según su propia página del manual asigna «la matriz de transformación actual», es decir, las
matrices integradas de GameMaker — por eso §1.1 manda la matriz de daltonismo como tres `vec3`
con `shader_set_uniform_f`, no como una matriz).
