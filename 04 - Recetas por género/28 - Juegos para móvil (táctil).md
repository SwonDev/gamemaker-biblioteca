# 28 · Juegos para móvil (táctil)

> Todo lo que cambia cuando el destino es **Android o iOS**: orientación, ciclo de vida, pantallas
> de proporción variable, botones que se tocan con el pulgar, batería, permisos y pruebas en un
> teléfono de verdad.
>
> **Aquí NO está el input táctil en sí.** Gestos (`tap`, `drag`, `flick`, `pinch`), teclado
> virtual y `device_mouse_*` los cubre
> [01 · 12 — Input](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md) §5
> y §8 bis. Anuncios, compras y logros están en
> [20 · Servicios de plataforma](./20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md).
> Publicar en las tiendas, en
> [01 · 16](../01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md) y
> [05 · 02](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md).

---

## 1 · El móvil no es un PC pequeño

Un juego de escritorio portado tal cual a un teléfono falla por seis motivos, y ninguno es
técnico:

| Diferencia | Qué implica en el diseño |
|---|---|
| **La sesión dura minutos** | Jugable en 90 segundos y guardado solo. Nada de «guarda en la hoguera» |
| **El sistema puede matarte** | Android descarta procesos de fondo: si no guardas al perder el foco, se pierde la partida |
| **El dedo tapa lo que toca** | Los botones van en los bordes; el contenido, en el centro |
| **No existe el *hover*** | Ni tooltips ni «resaltado» previo al clic: todo es pulsado/soltado |
| **La pantalla no tiene forma fija** | De 4:3 (iPad) a 21:9 (móviles alargados). El HUD tiene que respirar |
| **La batería es un recurso** | 60 fps con partículas vacían el móvil en 40 minutos y el jugador desinstala |

### 1.1 Un pulgar o dos pulgares

Es la primera decisión y condiciona el género entero.

| Modo | Zona cómoda | Géneros |
|---|---|---|
| **Un pulgar** (vertical, una mano) | arco inferior del lado dominante | puzzle, *idle*, cartas, un botón, *match-3* |
| **Dos pulgares** (apaisado) | esquinas inferiores izquierda y derecha | plataformas, twin-stick, arcade, carreras |
| **Toda la mano** (tableta) | toda la pantalla | estrategia, gestión, *tower defense* |

> 💡 **Regla del arco del pulgar:** con el teléfono en una mano, el pulgar barre un arco cuyo
> centro está en la esquina inferior del lado que sujetas. Lo que caiga en la esquina superior
> **contraria** es casi inalcanzable: ahí van los elementos informativos (puntuación, vidas),
> nunca los interactivos.

### 1.2 Vertical u horizontal: elige una y quédate ahí

**Vertical** se juega con una mano de pie, cabe el HUD arriba y abajo, y descarga más en casual;
es malo para plataformas y *twin-stick*. **Horizontal** da campo de visión e inmersión, pero el
HUD compite con el espacio del pulgar y los menús largos sufren.

**Soportar las dos duplica el trabajo de UI y no lo hace mejor.** Elige una, bloquéala y punto
(§2). La excepción razonable: menús en vertical y partida en horizontal, en un juego de tableta.

---

## 2 · Orientación: decidirla y fijarla

Hay **dos capas**: las casillas de las Opciones de Juego y las funciones de GML.

**En el IDE** — *Game Options → Android* (o *iOS*) → sección **General**: cuatro casillas
(*Portrait*, *Portrait flipped*, *Landscape*, *Landscape flipped*). Es la lista blanca: el
sistema solo permitirá las que marques. Márcalas también en iOS, son ajustes independientes.

**En GML**, tres funciones (y una que **no existe**):

```gml
/// rm_init — fijar la orientación al arrancar
if (os_type == os_android || os_type == os_ios) {
    os_set_orientation_lock(true, false);   // (landscape_enable, portrait_enable)
}

/// Congelar la orientación ACTUAL (una cinemática, un minijuego) y devolverla después
os_lock_orientation(true);
os_lock_orientation(false);

/// obj_pantalla · Step — leer la orientación y reaccionar cuando cambia
var _orient = display_get_orientation();
if (_orient != orientacion_previa) {
    orientacion_previa = _orient;
    ajustar_pantalla();                 // recolocar cámara y GUI · ver §4
    switch (_orient) {
        case display_portrait:
        case display_portrait_flipped:  colocar_hud_vertical();   break;
        case display_landscape:
        case display_landscape_flipped: colocar_hud_apaisado();   break;
    }
}
```

> 🔺 **`display_set_orientation` NO EXISTE.** Es la invención más habitual al escribir código
> móvil de GameMaker: la familia `display_*` solo tiene el *getter*. Para cambiar orientación se
> usa `os_set_orientation_lock()`; para congelar la actual, `os_lock_orientation()`.
> Compruébalo tú: `python3 _indice/buscar.py --listar display_`.
>
> 🔺 **`os_set_orientation_lock()` apaga las variantes *flipped*.** Lo dice el manual: llamarla
> desactiva las orientaciones invertidas que hubieras marcado en las Opciones de Juego. Si
> quieres apaisado en los dos sentidos, tendrás que confiar en las casillas del IDE y no llamar
> a esta función.

> 💡 **Si soportas las dos orientaciones, reacciona al cambio, no lo ignores.** Rotar el
> dispositivo cambia el tamaño de la pantalla y con él el de la GUI y el de la cámara: sin
> recalcularlos, el HUD se queda con las medidas de la orientación anterior.

---

## 3 · El ciclo de vida: pausa, foco y muerte súbita

En escritorio, perder el foco es una molestia. En móvil, es el momento más peligroso del juego:
una llamada entrante, una notificación o el botón de inicio pueden **terminar el proceso** sin
darte otra oportunidad de escribir en disco.

`os_is_paused()` es el aviso, y se comporta distinto según la plataforma: en **Android e iOS**
devuelve `true`, ejecuta tu bloque de código y **entonces** el sistema congela el juego como
proceso en segundo plano; en Windows, macOS, Ubuntu y HTML5 devuelve `true` **un solo paso** al
perder el foco y vuelve a `false`, porque el juego sigue corriendo detrás.

```gml
/// obj_ciclo_vida · Create — un controlador persistente creado en rm_init
persistent     = true;
estaba_pausado = false;
if (os_type == os_android || os_type == os_ios) {
    os_powersave_enable(false);   // que la pantalla no se apague sola durante la partida
}

/// obj_ciclo_vida · Step
var _pausado = os_is_paused();

if (_pausado && !estaba_pausado) {
    // Nos mandan a segundo plano. Esto es lo ÚLTIMO que se ejecuta con seguridad.
    guardar_partida();          // ver §7
    audio_pause_all();
    global.en_pausa = true;
}

if (!_pausado && estaba_pausado) {
    // Volvemos. En móvil el audio NO se reanuda solo: hay que arrancarlo a mano.
    audio_resume_all();
    // Y NO quitas la pausa automáticamente: que el jugador pulse «Continuar».
}

estaba_pausado = _pausado;
```

> ⚠️ **Trampa fina que avisa el manual:** en móvil, el código dentro del `if (os_is_paused())` se
> ejecuta, pero el juego se congela **inmediatamente después**; una instancia creada ahí no
> correrá ningún evento hasta que el jugador vuelva. Por eso el menú de pausa se construye **al
> volver**, no al irse: al irse solo se **guarda** y se **para el audio**.
>
> 🔺 **`os_powersave_enable(false)` solo existe en Android e iOS.** Es para juegos que no generan
> toques (inclinación, esperar, *idle*): sin ella el sistema apaga la pantalla en mitad de la
> partida. Vuelve a `true` en los menús largos — forzar la pantalla encendida gasta batería.

---

## 3 bis · Audio: latencia, llamadas e interrupciones

### Una llamada entrante no es un caso especial

Una llamada entrante, un banner de notificación o el botón de inicio le llegan todos a GameMaker
por el **mismo** camino que ya viste en §3: `os_is_paused()` se pone a `true` y es tu código el
que decide qué hacer, incluido el audio. **GameMaker no pausa el audio por ti** cuando suena el
teléfono: si no llamas a `audio_pause_all()` en ese `if`, tu música sigue reproduciéndose por
detrás mientras el sistema atiende la llamada, y al volver puede sonar desde un punto distinto de
donde el jugador la dejó de percibir (la pista no se detiene: sigue avanzando en segundo plano).
El bloque de §3 ya lo resuelve; esta sección solo deja explícito que «llamada entrante» **no**
necesita un camino de código aparte.

> 🔺 **Pruébalo con una llamada real, no la simules.** El emulador no dispara el evento de
> interrupción del sistema operativo igual que una llamada de verdad; es uno de los pasos que ya
> pide la fila «Ciclo de vida» de la checklist del §11.

### Latencia de salida: por qué el móvil no es un PC con altavoces pequeños

La latencia entre que el código llama a `audio_play_sound()` y el jugador oye algo de verdad
**varía mucho más en móvil que en escritorio**, y varía sobre todo con la salida elegida:
auriculares con cable y altavoz interno suelen ir bien; **auriculares Bluetooth añaden un salto
extra** (la codificación del propio protocolo) que en el peor caso llega a los 100-200 ms. ⚠️ No
hay una cifra fija por SO que GameMaker publique ni que puedas leer desde GML: es una
característica del hardware de audio del dispositivo y del códec Bluetooth activo, no algo que
controles con una función.

Para casi todos los juegos esto no importa —un salto no crítico de milisegundos no lo nota
nadie—, pero en cuanto el timing es parte de la mecánica (un juego de ritmo, un QTE muy ajustado)
la latencia deja de ser transparente. Ahí no inventes nada nuevo: usa la **pantalla de
calibración** de [04 · 19 §3](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md),
que ya resuelve esto midiendo la latencia real del dispositivo del jugador en vez de asumir una.

### Silenciar o convivir con la música que el jugador ya tenía puesta

Si el jugador entra a tu juego con Spotify sonando, ¿tu juego la corta o suena encima? Esto **no**
es un ajuste de GML: el motor no expone desde código la categoría de sesión de audio de iOS
(`AVAudioSession`, que decide si tu app calla al resto o convive con él) ni el foco de audio de
Android. ⚠️ Sin tocar nada, el comportamiento por defecto de la mayoría de juegos es **exclusivo**:
al arrancar tu audio, el sistema pausa la música que hubiera puesta, y es lo que la mayoría de
jugadores espera de un juego con música propia.

Si tu diseño necesita lo contrario —una app de puzles relajante, un juego pensado para jugarse con
el podcast del jugador de fondo—, la única vía es una **extensión nativa** que cambie la categoría
de sesión antes de que GameMaker reproduzca nada: ver
[07 · 22 — Crear una extensión nativa](../07%20-%20Ecosistema/22%20-%20Crear%20una%20extensión%20nativa%20%28guía%20en%20español%29.md).
No hay atajo en GML puro para esta decisión.

---

## 4 · Resolución y escalado en móvil

En escritorio hay dos o tres relaciones de aspecto. En móvil hay una decena, y ninguna es
negociable.

| Relación | Dónde aparece |
|---|---|
| 4:3 · 3:2 | iPad clásicos y iPad Pro modernos, tabletas Android |
| 16:9 | Android de gama media, la referencia histórica |
| 19,5:9 | iPhone con *notch* o isla dinámica, del X en adelante |
| 20:9 · 21:9 | Android alargados, de 2022 en adelante |

### 4.1 Altura fija, anchura variable: la estrategia que funciona

En vez de fijar una resolución y meterla en una caja negra (*letterbox*), **fijas la altura del
diseño y dejas que la anchura crezca**. El jugador con un móvil alargado ve más mundo a los
lados; el de un iPad ve menos. Nadie ve barras negras y nada se deforma.

```gml
/// obj_pantalla · Create
alto_base          = 360;                       // el juego se diseña a esta altura
orientacion_previa = display_get_orientation();
ajustar_pantalla();

/// scr_pantalla — altura fija, anchura según la pantalla real
function ajustar_pantalla() {
    var _ancho_fisico = display_get_width();
    var _alto_fisico  = display_get_height();
    if (_alto_fisico <= 0) return;              // por si la ventana aún no existe

    var _relacion   = _ancho_fisico / _alto_fisico;
    var _ancho_base = round(alto_base * _relacion);
    if (_ancho_base mod 2 == 1) _ancho_base += 1;   // par: evita el medio píxel al centrar

    surface_resize(application_surface, _ancho_base, alto_base);
    camera_set_view_size(view_camera[0], _ancho_base, alto_base);
    display_set_gui_size(_ancho_base, alto_base);
}
```

> 🔺 **Los tres tienen que ir juntos.** Si redimensionas `application_surface` pero no la cámara,
> el mundo se estira; sin `display_set_gui_size()`, la GUI toma el tamaño de la ventana y el HUD
> sale a otra escala. Desglose completo en
> [13 · 03 §6.3–6.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/03%20-%20Pixel%20art%20y%20resolución.md)
> y en la serie de [PixelatedPope](../03%20-%20Cursos%20%28YouTube%29/41%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%201%20-%20Principiante.md).

**La alternativa es el *letterbox*, y no necesita código**: *Game Options → Android/iOS →
Graphics → Scale* ofrece «mantener la relación de aspecto añadiendo relleno» o «estirar hasta
llenar la pantalla». La primera da barras negras; la segunda deforma. Úsala solo si el diseño
exige **exactamente** el mismo encuadre en todos los dispositivos (un puzzle de tablero fijo).

### 4.2 Zonas seguras: el *notch* y la barra de gestos

> ⚠️ **GameMaker no tiene ninguna función de *safe area*.** No existe `display_get_safe_area`,
> ni equivalente: la búsqueda en el manual espejado no devuelve nada. Se resuelve **con márgenes
> por porcentaje**, y por eso esta sección va marcada: los valores de abajo son un criterio
> razonable de esta biblioteca, no una medida oficial.

```gml
/// scr_pantalla — márgenes en los que NO se coloca nada interactivo ni crítico
function margenes_seguros() {
    var _ancho = display_get_gui_width();
    var _alto  = display_get_gui_height();
    var _m = { izq: 0, der: 0, arriba: 0, abajo: 0 };

    if (os_type != os_android && os_type != os_ios) return _m;

    var _orient = display_get_orientation();
    if (_orient == display_portrait || _orient == display_portrait_flipped) {
        _m.arriba = _alto * 0.06;      // barra de estado + notch / isla
        _m.abajo  = _alto * 0.04;      // barra de gestos de iOS y Android
    } else {
        _m.izq   = _ancho * 0.05;      // en apaisado el notch cae a un lado…
        _m.der   = _ancho * 0.05;      // …y no sabes a cuál: reserva los dos
        _m.abajo = _alto  * 0.05;
    }
    return _m;
}
```

```gml
/// obj_hud · Draw GUI — usar los márgenes en vez de pegar el HUD al borde
var _m = margenes_seguros();
draw_text(_m.izq + 16, _m.arriba + 16, "Monedas: " + string(global.monedas));

/// Modo inmersivo en Android: recupera la franja de la barra de navegación
/// (SYSTEM_UI_FLAG_IMMERSIVE_STICKY | SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN)
if (os_type == os_android) display_set_ui_visibility(4096 | 1024);
```

> 🔺 **`display_set_ui_visibility()` es exclusiva de Android** y recibe las banderas de
> `android.view.View` como enteros, fusionadas con `|`. No hay constantes de GML para ellas:
> los números salen de la documentación de Android. En iOS, el equivalente es la casilla
> *«Aplazar la salida del indicador de inicio»* de las Opciones de Juego.

### 4.3 Densidad de píxeles (DPI)

Dos móviles con la misma resolución pueden tener pantallas de 5" y de 7". Lo que importa para
que un botón se pueda pulsar no son los píxeles, son los **milímetros**:

```gml
/// scr_pantalla — convertir milímetros físicos a píxeles de la capa GUI
function milimetros_a_gui(_mm) {
    var _ppmm = display_get_dpi_x() / 25.4;                     // píxeles físicos por mm
    var _fisico = max(1, display_get_width());
    var _factor = display_get_gui_width() / _fisico;            // GUI por píxel físico
    return _mm * _ppmm * _factor;
}
```

> ⚠️ **`display_get_dpi_x()` está documentada, pero lo que reporta depende del fabricante:**
> algunos dispositivos devuelven la densidad nominal del *bucket* de Android (160/240/320/480 dpi)
> en vez de la real. Úsala para dimensionar, pero **aplica siempre un mínimo absoluto** (§5.1).
>
> 💡 **Pixel art en móvil**: la escala entera casi nunca cuadra con la altura de un teléfono. Las
> tres salidas —escala fraccionaria con filtrado apagado, altura base que divida bien, o dibujar
> a resolución doble— están en
> [13 · 03](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/03%20-%20Pixel%20art%20y%20resolución.md).

---

## 5 · UI táctil

### 5.1 El tamaño mínimo de un botón

Las dos plataformas dan la misma respuesta con unidades distintas, y coinciden en unos **9 mm**:

| Plataforma | Mínimo | Equivalencia física | Fuente |
|---|---|---|---|
| **iOS** | 44 × 44 pt | ≈ 7 mm | Apple Human Interface Guidelines |
| **Android** | 48 × 48 dp | ≈ 9 mm | Material Design 3 / Accesibilidad Android |
| Separación entre objetivos | 8 dp mínimo | ≈ 1,5 mm | Material Design 3 |

> Material Design lo dice literalmente: *«Consider making touch targets at least 48x48dp,
> separated by 8dp of space or more… A touch target of 48x48dp results in a physical size of
> about 9mm, regardless of screen size.»*

**Toma 48 dp como norma y 44 pt como suelo.** Y aprovecha la distinción que hacen las dos guías:
el **área que se toca** puede ser mayor que el **dibujo que se ve**. Un icono de 32 px con zona
sensible de 9 mm se ve elegante y se pulsa bien.

```gml
/// scr_tactil — ¿algún dedo acaba de tocar dentro de este círculo?
function toque_en_circulo(_cx, _cy, _radio) {
    for (var _i = 0; _i < 5; _i++) {
        if (device_mouse_check_button_pressed(_i, mb_left)) {
            var _tx = device_mouse_x_to_gui(_i);
            var _ty = device_mouse_y_to_gui(_i);
            if (point_distance(_cx, _cy, _tx, _ty) <= _radio) return true;
        }
    }
    return false;
}

/// obj_boton_salto · Create — el radio táctil sale de los milímetros, no de la imagen
radio_tactil = max(48, milimetros_a_gui(9) * 0.5);   // suelo de 48 px de GUI, por si el DPI miente

/// obj_boton_salto · Step
if (toque_en_circulo(x, y, radio_tactil)) global.saltar = true;

/// obj_boton_salto · Draw GUI — se ve más pequeño de lo que se toca
draw_sprite_ext(spr_boton_salto, 0, x, y, 1, 1, 0, c_white, 0.75);
```

### 5.2 Multi-touch: cada dedo es un «dispositivo»

GameMaker numera los toques simultáneos de `0` en adelante y los lee con la familia
`device_mouse_*`, explicada en
[01 · 12 §5](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md). Lo que
importa aquí es la disciplina: **recorre los índices en bucle** y nunca asumas el `0` (el jugador
puede soltar el primer dedo y quedarse con el 1 activo); **usa las variantes `_to_gui`** en la
interfaz, porque mezclar coordenadas de mundo y de GUI es el bug táctil número uno; y **guarda
qué dedo controla qué** en vez de recalcularlo, porque si dos dedos entran en el mismo botón uno
tiene que ganar. `mb_left` es el botón que reportan todos los toques.

### 5.3 Un joystick virtual completo

El que aparece donde plantas el pulgar, con zona muerta, y cuya base «camina» detrás del dedo si
te alejas del radio. Es el patrón del tutorial oficial de GameMaker sobre multi-touch, escrito
aquí con los nombres y el estilo de esta biblioteca.

```gml
/// obj_joystick · Create
zona_x     = 0;                                  // mitad izquierda de la pantalla
zona_y     = 0;
zona_ancho = display_get_gui_width()  * 0.5;
zona_alto  = display_get_gui_height();

dedo        = -1;                                // índice de dispositivo que lo controla
base_x      = 0;   base_y  = 0;                  // dónde se plantó el pulgar
punta_x     = 0;   punta_y = 0;                  // dónde está el pulgar ahora
radio       = max(64, milimetros_a_gui(12));     // recorrido máximo de la palanca
zona_muerta = 0.20;                              // el 20 % central no cuenta

eje_h = 0;   eje_v = 0;                          // la salida: dos valores de -1 a 1
```

```gml
/// obj_joystick · Step
// 1 · Sin dedo asignado: buscar uno que ACABE de tocar dentro de la zona
if (dedo == -1) {
    for (var _i = 0; _i < 5; _i++) {
        if (device_mouse_check_button_pressed(_i, mb_left)) {
            var _tx = device_mouse_x_to_gui(_i);
            var _ty = device_mouse_y_to_gui(_i);
            if (_tx >= zona_x && _tx <= zona_x + zona_ancho
             && _ty >= zona_y && _ty <= zona_y + zona_alto) {
                dedo    = _i;
                base_x  = _tx;    base_y  = _ty;   // el joystick NACE donde tocas
                punta_x = _tx;    punta_y = _ty;
                break;
            }
        }
    }
}

// 2 · Con dedo asignado: seguirlo
if (dedo != -1) {
    if (device_mouse_check_button(dedo, mb_left)) {
        var _tx    = device_mouse_x_to_gui(dedo);
        var _ty    = device_mouse_y_to_gui(dedo);
        var _bruto = point_distance(base_x, base_y, _tx, _ty);
        var _ang   = point_direction(base_x, base_y, _tx, _ty);
        var _dist  = min(_bruto, radio);

        punta_x = base_x + lengthdir_x(_dist, _ang);
        punta_y = base_y + lengthdir_y(_dist, _ang);

        // 3 · Zona muerta, reescalada para que el eje llegue a 1 justo en el borde
        var _fuerza = _dist / radio;
        if (_fuerza < zona_muerta) {
            eje_h = 0;
            eje_v = 0;
        } else {
            _fuerza = (_fuerza - zona_muerta) / (1 - zona_muerta);
            eje_h = lengthdir_x(_fuerza, _ang);
            eje_v = lengthdir_y(_fuerza, _ang);
        }

        // 4 · Si el dedo se sale del radio, la base lo persigue: el joystick "camina"
        if (_bruto > radio) {
            base_x = _tx - lengthdir_x(radio, _ang);
            base_y = _ty - lengthdir_y(radio, _ang);
        }
    } else {
        dedo  = -1;                    // el dedo se ha levantado
        eje_h = 0;
        eje_v = 0;
    }
}
```

```gml
/// obj_joystick · Draw GUI — solo se ve mientras hay un dedo encima
if (dedo != -1) {
    draw_circle_color(base_x,  base_y,  radio,        c_white, c_white, true);
    draw_circle_color(punta_x, punta_y, radio * 0.35, c_white, c_white, false);
}

/// obj_jugador · Step — consumir el joystick
var _vel = 3.5;
x += obj_joystick.eje_h * _vel;
y += obj_joystick.eje_v * _vel;
```

> 💡 **Por qué «nace donde tocas»:** el jugador mira el juego, no el pulgar. Un joystick pintado
> en un sitio fijo obliga a apuntar a ciegas; uno que aparece bajo el dedo acierta siempre.
>
> 🔺 **`lengthdir_y()` devuelve negativo hacia arriba**, igual que la convención de ángulos de
> GameMaker: por eso `eje_v` vale −1 al empujar hacia arriba y `y += eje_v * vel` funciona sin
> invertir nada.

### 5.4 La alternativa barata: teclas virtuales

Si el juego ya funciona con teclado, `virtual_key_add()` mapea un rectángulo de la pantalla a
una tecla y **no tienes que tocar la lógica de input**:

```gml
/// obj_controles · Create — botones táctiles que disparan eventos de teclado
global.tecla_izq  = virtual_key_add(32,  240, 96, 96, vk_left);
global.tecla_der  = virtual_key_add(144, 240, 96, 96, vk_right);
global.tecla_salt = virtual_key_add(512, 240, 96, 96, vk_space);
```

> 🔺 **Se definen por *room* y GameMaker las borra al cambiar de room.** Sus coordenadas son **de
> pantalla**, no de room: defínelas en el Create y dibuja los sprites en Draw GUI, con la capa GUI
> del tamaño de la pantalla. `virtual_key_show/hide/delete` las gestionan después.

### 5.5 Texto y teclado del sistema

`keyboard_virtual_show()` y compañía están explicadas en
[01 · 12 §8 bis](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md).
Lo que falta ahí es **cómo evitar que el teclado tape el campo**:

```gml
/// obj_campo_nombre · Async - System — el sistema avisa cuando el teclado aparece
if (async_load[? "event_type"] == "virtual keyboard status") {
    alto_teclado = async_load[? "screen_height"];    // 0 si el teclado está oculto
    campo_y = display_get_gui_height() - alto_teclado - 80;   // subirlo por encima
}
```

`device_is_keypad_open()` responde lo mismo en `true`/`false`, pero **no dice cuántos píxeles
ocupa**: para eso están `keyboard_virtual_height()` y el evento asíncrono de arriba.

### 5.6 Lo que no se puede hacer

Nada de ***hover*** (ni tooltips ni resaltado previo: todo pasa a «mantener pulsado»), nada de
clic derecho ni rueda (el zoom es *pinch*), nada de esquinas de 1 px para arrastrar y nada de
texto de 8 px — si no se lee a un brazo de distancia, no está. Contraste y tamaño mínimo, en
[27 · Accesibilidad](./27%20-%20Accesibilidad.md).

### 5.7 Feedback consciente del dedo y silencioso por defecto

Dos reglas de §1 que el resto de §5 nunca terminó de aplicar al feedback en sí (solo al layout
de botones, §5.1, y a la vibración como canal aparte, §8.2): **el dedo tapa lo que toca**, y
**una parte real de los jugadores juega sin sonido**.

- **La confirmación de un toque se dibuja lejos del punto de contacto**, nunca debajo del dedo:
  un borde que se ilumina en el HUD, un contador que sube en una esquina, un marco que
  parpadea — no un destello justo donde está el pulgar, porque ahí no lo ve nadie hasta que lo
  levanta.
  [`fx_floating_text()`](./15%20-%20Game%20feel%20y%20juice.md#56-flash-de-impacto-y-texto-flotante)
  de 04 · 15 §5.6 sirve igual en móvil, con un desplazamiento en Y mayor (24-32 px en vez de los
  16 de escritorio) para que el texto salga de debajo del dedo desde el primer fotograma
  visible.
- **Todo feedback crítico tiene equivalente visual Y háptico, nunca solo sonoro por defecto.**
  El toggle de vibración (§8.2) y el de sonido de
  [04 · 25](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md) son ajustes independientes: un
  jugador puede tener los dos desactivados a la vez sin que el juego deje de decirle si acertó,
  falló o subió de nivel. Diséñalo asumiendo volumen cero desde el primer prototipo — pruébalo
  con el móvil en silencio, no lo compruebes al final como una comprobación de accesibilidad
  aparte.

Las dos son la misma restricción que §1.1 ya aplica al layout (nada interactivo en la esquina
que el pulgar no alcanza): el dedo y el silencio son propiedades del dispositivo, no casos
límite que se resuelven después.

---

## 6 · Rendimiento y batería

### 6.1 ¿60 o 30 fps?

En móvil no es una cuestión de suavidad, es de **batería y temperatura**. Un juego a 60 fps
constantes calienta el teléfono, el sistema baja la frecuencia del procesador y el juego pasa
a ir a 45 con tirones: peor que 30 estables.

**60 fps** para plataformas, *twin-stick* y acción rápida; **30** para puzzle, cartas, estrategia
por turnos, *idle* y para cualquier cosa en gama baja.

```gml
/// obj_control · Create — arrancar en 60 y medir si el móvil aguanta de verdad
game_set_speed(60, gamespeed_fps);
muestras = [];   medido = false;
alarm[0] = 60 * 3;                        // tres segundos de margen antes de juzgar

/// obj_control · Step
if (!medido) array_push(muestras, fps_real);

/// obj_control · Alarm 0
var _suma = 0;
for (var _i = 0; _i < array_length(muestras); _i++) _suma += muestras[_i];
// fps_real es cuántos fotogramas PODRÍA hacer el dispositivo, no cuántos hace.
// Si no supera holgadamente el objetivo, va justo: 30 estables es mejor trato.
if (_suma / max(1, array_length(muestras)) < 75) {
    game_set_speed(30, gamespeed_fps);
    global.calidad_baja = true;           // y de paso, menos partículas
}
medido = true;   muestras = [];
```

> ⚠️ **El umbral de 75 es criterio de esta biblioteca, no una cifra oficial**: ajústalo midiendo
> en tus dispositivos objetivo. Lo que sí es del manual es la diferencia entre `fps` (fotogramas
> dibujados) y `fps_real` (los que podrían dibujarse): la segunda es la que mide el margen.

### 6.2 Páginas de textura

Es el ajuste que más cuelgues provoca en gama baja. Está en *Game Options → Android/iOS →
Graphics → Texture Page Size*.

| Tamaño | Veredicto en móvil |
|---|---|
| **2048 × 2048** | **El valor por defecto y el más compatible. Quédate aquí.** |
| 4096 × 4096 | Menos páginas, pero muchos dispositivos antiguos no lo soportan y la app revienta al cargar |
| 1024 × 1024 | Para gama muy baja; genera más páginas y más cambios de textura |

El manual lo dice sin rodeos: *«cuanto mayor sea el tamaño de la página de texturas, menos
compatible será tu juego con los distintos navegadores y dispositivos»*. Dos ajustes más del
**gestor de grupos de texturas** que solo importan en móvil: el **formato del grupo** (por
defecto *BZ2 + QOI*; el manual recomienda **QOI a secas si BZ2 afecta a la velocidad, y nombra
Android explícitamente** — BZ2 comprime más a costa de descomprimir al cargar) y **Permitir
escala**, que conviene desactivar en el grupo de las fuentes: el manual avisa de aplicaciones
**rechazadas en la App Store por imágenes borrosas** a causa del escalado de texturas.

Y el ajuste que decide si el juego se ve nítido o suave:

```gml
/// Pixel art: filtrado apagado. Arte con bordes suaves: encendido.
gpu_set_texfilter(false);
```

Equivale a la casilla *«Interpolate colours between pixels»* de las Opciones de Juego, que en
Android viene **activada** por defecto y en iOS **desactivada**. Compruébalo en las dos.

### 6.3 Lo demás que se paga caro

| Coste | Regla en móvil |
|---|---|
| **Superficies** | Cada `surface_set_target()` es un cambio de destino de render. Una para todo el juego, no una por efecto. Y siempre `if (!surface_exists(...))` |
| **Partículas** | Recorta el número con `global.calidad_baja`. Mil partículas que en un PC no se notan aquí bajan 15 fps |
| **`draw_text` con fuentes grandes** | Cada fuente ocupa su zona de textura: una de 72 px se come media página. Escala una de 24 con `draw_text_transformed` |
| **Audio** | OGG comprimido para la música (una pista), WAV para efectos cortos, y pocos sonidos a la vez: el mezclador de un móvil no es el de un PC. Y recuerda que al pausar se detiene y **no vuelve solo** |
| **RAM total del proceso** ⚠️ | El sistema operativo mata el juego por presión de memoria mucho antes de agotar la RAM del dispositivo — no hay una cifra única, oficial ni fija (ver abajo), pero el techo real en gama baja está muy por debajo de lo que parece «poco» en un PC de desarrollo |

**Sobre esa última fila: iOS y Android no publican un número oficial fijo.** Lo que hacen ambos
sistemas es matar procesos **por presión relativa de memoria**, no por una cifra en MB clavada
en la documentación:

- **iOS** usa **Jetsam**, que aplica un presupuesto de memoria por app que depende del **modelo
  concreto del dispositivo**, no de una constante — Apple no publica la tabla. Lo que sí es
  observable (reportes de desarrolladores, no un dato de Apple) es que el presupuesto ronda una
  fracción de la RAM total del teléfono: un iPhone con 3 GB de RAM total deja un margen muchísimo
  más estrecho a tu app que uno con 8 GB, incluso proporcionalmente. Es el mismo espíritu que
  [`05 · 02 §3.8/§3.8bis`](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md)
  ya aplica a las consolas bajo NDA: aquí no hay NDA, pero tampoco hay tabla oficial de Apple —
  trátalo con el mismo respeto por lo que no se puede afirmar sin fuente.
- **Android** usa el **Low Memory Killer** (`lmkd`), documentado oficialmente en
  <https://developer.android.com/games/optimize/vitals/lmk> (consultado 2026-09-07): mata
  procesos por prioridad (`oom_adj_score`) cuando la RAM libre cae por debajo de un umbral que
  **la propia documentación de Google confirma que escala con la RAM total del dispositivo** —
  hay tres juegos de umbrales distintos según el dispositivo tenga menos de 3 GB, entre 3 y 5 GB,
  o más de 5 GB de RAM, pero **Google tampoco publica las cifras exactas en MB** de cada nivel.

**Qué hacer con esto, en la práctica** (no hay número que citar, pero sí una forma honesta de
trabajar):

- **Prueba en el dispositivo Android/iOS más modesto de tu lista de compatibilidad**, no en el
  tuyo de desarrollo — la misma regla de §6.5 más abajo, aplicada a memoria en vez de a fps.
- **Mide el consumo real con las herramientas de la plataforma**, no adivines: Instruments
  (Allocations/memory gauge) en iOS y `adb shell dumpsys meminfo <paquete>` o el Android
  Profiler en Android — ambas cubiertas con más detalle en
  [`01 · 15 §11`](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#11-herramientas-externas-de-perfilado).
- **El mismo checklist de limpieza de recursos dinámicos** de
  [`01 · 15 §8`](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#8-checklist-de-limpieza-de-recursos-dinámicos)
  (surfaces, buffers, estructuras de datos sin destruir) es lo primero que reduce el pico de
  memoria en gama baja — antes de tocar nada de arte o audio.
- `os_get_info()` (ver
  [`01 · 15 §11.2`](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#112-instruments-macos-e-ios))
  da `totalMemory`/`userMemory` en iOS/tvOS — no hay una clave equivalente documentada para
  Android en el propio manual de GameMaker.

```gml
/// display_set_sleep_margin: el ajuste contra el micro-tartamudeo
// Por defecto Android e iOS usan 4 ms (el escritorio, 10).
// Subirlo a 5-10 reduce el tirón en dispositivos con muchos procesos de fondo,
// a costa de más uso de CPU y más batería. En caso de duda, no lo toques.
if (global.calidad_baja) display_set_sleep_margin(8);
```

### 6.4 YYC en móvil

**Sí está disponible en Android y en iOS**: genera código máquina en vez de código interpretado
por la VM, compila más lento y ejecuta más rápido. Pide una licencia que lo incluya y los SDK
bien configurados (Android SDK/NDK/JDK, o Xcode); se activa cambiando la salida de *VM* a *YYC*
en la ventana de compilación. Como en escritorio: **desarrolla en VM y publica en YYC**. Detalle
en [05 · 02 §4.3](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md).

### 6.5 Medir en el dispositivo, no en el PC

`show_debug_overlay(true, true, 2)` pinta fps, memoria y tiempos **en el propio teléfono**; el
tercer argumento es la escala, y sin subirla la superposición se dibuja a tamaño de escritorio y
resulta ilegible. Compila una build de depuración con esto activo, juega media hora seguida y
mira si el gráfico de fotogramas se degrada con el calor. Más herramientas en
[01 · 15](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md).

---

## 7 · Almacenamiento, permisos y peso

### 7.1 Las dos carpetas

En móvil el sandbox no es opcional: la aplicación vive en su propia caja.

| Variable | Qué es | ¿Se puede escribir? |
|---|---|---|
| `working_directory` | La carpeta del paquete instalado: tus **Included Files** | **No** en Android/iOS |
| `game_save_id` | La carpeta privada de guardado de la aplicación | **Sí**, y es la única |

**Un nombre de archivo sin ruta se resuelve solo**: GameMaker busca primero en el área de
guardado y luego en el paquete, así que `buffer_save(_b, "partida.json")` escribe donde debe. El
mecanismo completo, con sus excepciones, en
[01 · 14 §1](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md).

```gml
/// scr_guardado — guardado que sobrevive a que Android mate el proceso
function guardar_partida() {
    var _datos = {
        version:     1,
        sala:        room_get_name(room),
        vida:        global.vida,
        monedas:     global.monedas,
        desbloqueos: global.desbloqueos
    };

    var _b = buffer_create(1024, buffer_grow, 1);
    buffer_write(_b, buffer_text, json_stringify(_datos));
    buffer_save(_b, "partida.json");        // → game_save_id
    buffer_delete(_b);
}

function cargar_partida() {
    if (!file_exists("partida.json")) return false;
    var _b = buffer_load("partida.json");
    var _datos = json_parse(buffer_read(_b, buffer_text));
    buffer_delete(_b);

    if (_datos.version != 1) return false;   // guardado de otra versión: no lo cargues a ciegas
    global.vida        = _datos.vida;
    global.monedas     = _datos.monedas;
    global.desbloqueos = _datos.desbloqueos;
    return true;
}
```

> 🔺 **Los ajustes van en INI, la partida en JSON.** `ini_open` / `ini_write_real` /
> `ini_read_real` valen para media docena de valores sueltos (volumen, idioma, vibración) y ya
> están montados en [25 · §4](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md). Para el estado del
> juego, JSON en un buffer: más rápido y sin el límite de tipos de INI.
>
> ⚠️ **Guarda a menudo y guarda barato.** En móvil el momento no lo eliges tú (§3): un guardado
> que tarda 300 ms es un guardado que a veces no llega a escribirse.

### 7.2 Permisos

Solo Android los pide en tiempo de ejecución. `os_check_permission()` devuelve una de tres
constantes y la respuesta del jugador llega por el **evento Async System**:

```gml
/// scr_permisos
function permiso_pedir(_nombre) {
    if (os_type != os_android) return true;

    switch (os_check_permission(_nombre)) {
        case os_permission_granted:
            return true;

        case os_permission_denied:
            os_request_permission(_nombre);     // se puede volver a preguntar
            return false;

        case os_permission_denied_dont_request:
            // El jugador marcó "no volver a preguntar": la única salida son los Ajustes
            mostrar_aviso("Activa el permiso desde los Ajustes del sistema");
            return false;
    }
    return false;
}

/// obj_permisos · Async - System — la respuesta del jugador llega aquí
if (async_load[? "type"] == "permission_request_result") {
    var _clave = "android.permission.RECORD_AUDIO";
    if (async_load[? _clave] == os_permission_granted) {
        activar_microfono();
    }
}
```

Los permisos «peligrosos» que GameMaker soporta de forma nativa y que **hay que pedir sí o sí**
son `WRITE_EXTERNAL_STORAGE`, `READ_PHONE_STATE` y `RECORD_AUDIO`. El resto (`INTERNET`,
`ACCESS_NETWORK_STATE`, `BLUETOOTH`) se marcan en *Game Options → Android → Permissions* y no
requieren diálogo.

> 💡 **Pide el permiso cuando haga falta, no al arrancar.** Un juego que en el primer segundo pide
> micrófono y almacenamiento se desinstala: pídelo justo antes de la función que lo necesita, y
> explica para qué en una pantalla propia antes de lanzar el diálogo del sistema.

### 7.3 Peso de la aplicación

- **Google Play publica AAB, no APK**: reconstruye el APK que toca para cada dispositivo, así que
  el usuario descarga bastante menos que el paquete completo.
- **Cada arquitectura de CPU suma al tamaño final** (*Game Options → Android → General*). Para
  Google Play necesitas ARM64; ARMv7 solo si aún soportas dispositivos viejos; x86 y Mips casi
  nunca. Y los **Included Files** pesan siempre: un CSV de traducción es gratis, un vídeo de
  intro de 40 MB se paga en la conversión de la ficha.
- **Contenido bajo demanda**: cada capítulo en su propio **grupo de texturas**, cargado con
  `texturegroup_load()` / `texturegroup_unload()` — familia completa en
  [08 · 08](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md).

---

## 8 · Sensores y hardware

### 8.1 Inclinación (acelerómetro)

```gml
/// obj_nave · Create — calibrar el reposo con el móvil como lo sostiene el jugador
inclinacion_reposo = device_get_tilt_y();     // en apaisado, el eje útil es Y

/// obj_nave · Step — control por inclinación con calibración y zona muerta
var _inc = device_get_tilt_y() - inclinacion_reposo;
if (abs(_inc) < 0.08) _inc = 0;               // zona muerta: la mano tiembla
x += clamp(_inc * 3, -1, 1) * velocidad;
```

> 🔺 **`device_get_tilt_x/y/z()` devuelven de −1 a 1**, y el manual advierte de que *«la
> correlación real entre los grados de inclinación y el valor devuelto depende del dispositivo y
> del sistema operativo»*: aproximadamente, 1 equivale a ±90°. **El eje útil cambia con la
> orientación**: en apaisado es el Y, en vertical el X. Calibra siempre el reposo al empezar la
> partida: nadie juega con el móvil perfectamente plano.
>
> 🔺 **Un juego de inclinación no genera toques.** Sin `os_powersave_enable(false)` (§3), el
> sistema apagará la pantalla a mitad de partida.

### 8.2 Vibración

> ⚠️ **GameMaker NO tiene función nativa de vibración en móvil.** `gamepad_set_vibration()`
> existe, pero es para **mandos**, no para el motor háptico del teléfono. Las búsquedas
> `--listar vibra` y `--listar haptic` no devuelven nada.

Se resuelve con la extensión oficial **GMEXT-MobileUtils**, verificado en el código fuente
descargado en `11 - Código descargado/extensiones_oficiales/GMEXT-MobileUtils`:

```gml
/// Vibración con la extensión oficial GMEXT-MobileUtils (Android e iOS)
if (MobileUtils_Vibrate_Is_Available()) {
    MobileUtils_Vibrate_Shot(60, -1);                              // 60 ms, amplitud por defecto
    // o un efecto predefinido del sistema:
    MobileUtils_Vibrate_Predefined(MobileUtils_VIBRATE_KIND_ANDROID_HEAVY_CLICK);
}
```

`MobileUtils_Vibrate_Is_Available()` devuelve `0` (no disponible), `1` (disponible) o `2` (con
funcionalidad extra). En Android hace falta el permiso `android.permission.VIBRATE`, que el
propio ejemplo de la extensión pide con `os_check_permission` / `os_request_permission`; en iOS
anteriores a la 13 el parámetro de milisegundos se ignora y suena un impacto medio.

> 💡 **La vibración se apaga en Opciones.** Es la primera opción de accesibilidad que busca la
> gente, y en un juego de muchos golpes es también un consumo de batería serio.

### 8.3 Saber en qué estás corriendo

```gml
/// Detección de plataforma: lo mínimo, y siempre con os_type
global.es_movil   = (os_type == os_android || os_type == os_ios);
global.es_android = (os_type == os_android);

/// Detalle del dispositivo — devuelve un ds_map que HAY QUE DESTRUIR
/// Claves de Android: MODEL, SDK_INT, MANUFACTURER, GL_MAX_TEXTURE_SIZE, VERSION_NAME…
/// Claves de iOS:     model, systemVersion, totalMemory, freeDiskSpace, cpuCount…
var _info = os_get_info();
show_debug_message("Textura máx.: " + string(_info[? "GL_MAX_TEXTURE_SIZE"]));
ds_map_destroy(_info);

/// Antes de pedir un anuncio, una tabla de puntuación o una sincronización
if (!os_is_network_connected()) {
    mostrar_aviso("Sin conexión: se guardará y se enviará más tarde");
    exit;
}
```

> 🔺 **`os_device` está OBSOLETA** y sus constantes (`device_ios_iphone6`, `device_tablet`,
> `device_emulator`…) se quedaron en 2015: no distinguen un iPhone 15 de un iPhone 6. El manual
> remite explícitamente a `os_get_info()`. **`os_version`** sí sirve (devuelve un `Real` con la
> versión del sistema) y `GL_MAX_TEXTURE_SIZE` es la forma honesta de saber si el dispositivo
> aguanta páginas de textura de 4096.

`os_get_language()` y `os_get_region()` dan el idioma y la región del sistema, para arrancar en
el idioma del jugador sin preguntar. El sistema completo de textos está en
[21 · Localización](./21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md).

---

## 9 · Probar de verdad

### 9.1 El emulador no sirve para juzgar

**Vale para comprobar que el juego arranca y que la UI cabe. Para nada más.** Usa la GPU del PC
(miente sobre el rendimiento), el multi-touch es torpe, el acelerómetro es simulado, la batería y
el calor no se pueden medir, y los anuncios y las compras suelen fallar. Un juego que va a 60 fps
en un AVD puede ir a 22 en un teléfono de 120 €.

### 9.2 Cómo se llega al dispositivo

En el IDE, la **lista de objetivos** tiene un botón de lápiz que abre el **Gestor de
Dispositivos**. En **Android**: activa las *opciones de desarrollador* y la *depuración por USB*
en el teléfono, conéctalo por cable y pulsa **Detect Device** (GameMaker lo encuentra por ADB);
**Test Connection** confirma que responde y *Run* (F5) compila, instala y lanza. Para un
emulador, el mismo gestor tiene **Run AVD**: crea uno en Android Studio, arráncalo y vuelve a
*Detect Device*.

En **iOS** no hay atajo: un **Mac con Xcode** configurado, una **cuenta de desarrollador de
Apple** de pago para probar en dispositivo físico y publicar, y el **Team Identifier** de firma en
*Game Options → iOS → General*. En el Gestor de Dispositivos, primero se añade y se prueba **el
Mac**; solo entonces se seleccionan desde él los dispositivos iOS conectados, simuladores
incluidos. Guías oficiales por plataforma en
[05 · 02 §3.7](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md).

### 9.3 Requisitos de las tiendas (a 2026)

| Tienda | Requisito vigente | Fecha |
|---|---|---|
| **Google Play** | Apps nuevas y actualizaciones: **Android 16 (API 36)** o superior | desde el 31-08-2026 (prórroga posible al 01-11-2026) |
| **Google Play** | Apps existentes: al menos **Android 15 (API 35)** o dejan de verse para usuarios nuevos en dispositivos recientes | desde el 31-08-2026 |
| **App Store** | Compilar con **Xcode 26 o superior** y el SDK de **iOS 26** | desde el 28-04-2026 |

Estos números se ponen en *Game Options → Android → General* (**Target SDK**, **Minimum SDK**,
**Build SDK**), y el botón *Pre-populate SDK values* los rellena por nivel de API. Sin las
APIs correspondientes instaladas en el SDK Manager de Android, la compilación falla.

> ⚠️ **Estas fechas caducan.** Google y Apple mueven el listón cada año; verifica antes de
> publicar en las páginas oficiales enlazadas en *Fuentes*.

### 9.4 Distribución interna antes de publicar

En Android, el canal de *pruebas internas* de Google Play (hasta 100 testers, disponible en
minutos) o pasar el APK a mano — con AAB conviene el canal, porque prueba el paquete real. En
iOS, **TestFlight**. Y en los dos casos: **prueba la build firmada de *release***, no la de
depuración; el sandbox, el rendimiento y las rutas de guardado cambian entre ellas.

---

## 10 · Monetización y servicios

Anuncios (AdMob, LevelPlay), compras integradas, logros y guardado en la nube **no se repiten
aquí**: están completos, con el ciclo de vida y las trampas de cada uno, en
[20 · Servicios de plataforma](./20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md).
Las extensiones oficiales móviles, con su estado y su última actualización, están catalogadas en
[07 · 01 §3](../07%20-%20Ecosistema/01%20-%20GitHub%20-%20organización%20YoYoGames.md): `GMEXT-AdMob`,
`GMEXT-LevelPlay`, `GMEXT-GooglePlayBilling`, `GMEXT-AppleIAP`, `GMEXT-GooglePlayServices`,
`GMEXT-GameCenter`, `GMEXT-MobileUtils`, `GMEXT-MobileReview`, `GMEXT-InAppUpdate`,
`GMEXT-GooglePlayIntegrity`, `GMEXT-PlayAgeSignals` y `GMEXT-DeclaredAgeRange`.

> ⚠️ **Dos extensiones nuevas obligatorias de facto:** `GMEXT-PlayAgeSignals` (señales de edad de
> Google Play) y `GMEXT-DeclaredAgeRange` (rango de edad declarado, normativa de iOS). Las tiendas
> exigen declarar el público objetivo antes de aceptar la ficha.

---

## 11 · Checklist móvil antes de publicar

| | Comprobación |
|---|---|
| **Control** | Orientación decidida, marcada en Game Options de **las dos** plataformas y bloqueada por código |
| | Todo lo interactivo mide **48 dp / 9 mm** o más y está separado 8 dp |
| | Nada crítico ni pulsable dentro de los márgenes de *notch* y barra de gestos |
| | Ningún control depende de *hover*, clic derecho o rueda |
| **Ciclo de vida** | `os_is_paused()` guarda la partida y para el audio; al volver, el audio se reanuda a mano |
| | Probado de verdad: llamada entrante, botón de inicio, notificación, matar la app y volver |
| **Pantalla** | Probado en 16:9, 19,5:9 y 4:3 como mínimo; nada se sale ni se solapa |
| | `surface_resize`, `camera_set_view_size` y `display_set_gui_size` se actualizan juntos |
| | La interpolación (`gpu_set_texfilter`) está como debe en Android **y** en iOS |
| **Rendimiento** | Páginas de textura en 2048 (o justificado por qué no) |
| | Medido en un dispositivo de gama baja, no solo en el tuyo, y media hora seguida sin degradación por calor |
| | Build de *release* en YYC si la licencia lo permite |
| **Sistema** | Los permisos se piden cuando hacen falta, con explicación, y las tres respuestas se manejan |
| | Icono adaptativo (Android) e iconos completos (iOS), y pantalla de carga en cada orientación soportada |
| | Target/Minimum/Build SDK al día con los requisitos vigentes de la tienda; ARM64 sí, lo que no uses fuera |
| | Probada la build **firmada** por el canal de pruebas internas / TestFlight |

---

## Las trampas

| Trampa | Consecuencia |
|---|---|
| Botón de 24 px porque «se ve bien en el PC» | En el móvil no se acierta; el jugador cree que el juego está roto |
| El teclado virtual tapa el campo de texto | El jugador escribe a ciegas; usa el evento **Async System** o `keyboard_virtual_height()` |
| Dejar las cuatro orientaciones marcadas | El juego rota en mitad de un salto; bloquea la orientación en `rm_init` |
| No guardar al perder el foco | Android mata el proceso y la partida desaparece sin más |
| No reanudar el audio al volver | El juego vuelve mudo y parece colgado |
| Página de textura de 4096 | Se ve perfecto en tu móvil y **casca al arrancar** en la gama baja |
| Usar `mouse_x`/`mouse_y` para multi-touch | Solo lee el primer dedo; usa `device_mouse_x_to_gui(i)` en bucle |
| Mezclar coordenadas de mundo y de GUI al tocar | El botón responde a 200 px de donde se ve |
| Publicar HTML5 «porque es más fácil» que nativo | Sin IAP nativas, sin logros, sin rendimiento y sin presencia en las tiendas |
| Suponer que `display_set_orientation` existe | No existe. Ese código no compila |
| Suponer que hay vibración nativa | No la hay: es `GMEXT-MobileUtils` |
| Probar solo en emulador | El rendimiento del emulador no tiene ninguna relación con el del teléfono |
| Pedir todos los permisos al arrancar | Desinstalación inmediata |
| 60 fps «porque es mejor» en un puzzle | Batería a la mitad sin ganar nada jugable |

---

## Ver también

- [01 · 12 — Input: teclado, ratón y gamepad](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md) — §5 multi-touch y §8 bis gestos y teclado virtual
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — el sandbox, buffers, JSON e INI
- [01 · 16 — Exportar y publicar](../01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md) — el resumen corto de la exportación
- [05 · 02 — Publicar y exportar](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md) — la referencia larga: licencias, SDK, guías por plataforma, CI
- [20 · Servicios de plataforma](./20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md) — anuncios, IAP, logros y nube
- [25 · Menú de opciones y ajustes](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md) — dónde vive el interruptor de vibración
- [27 · Accesibilidad](./27%20-%20Accesibilidad.md) — tamaños de texto, contraste y alternativas al gesto
- [13 · 03 — Pixel art y resolución](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/03%20-%20Pixel%20art%20y%20resolución.md) — escala entera, `application_surface` y filtrado; y el curso de cámaras de [PixelatedPope](../03%20-%20Cursos%20%28YouTube%29/41%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%201%20-%20Principiante.md) (partes 1 a 4)
- [08 · 08 — Texturas y grupos de texturas](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md) — carga y descarga de grupos, y [07 · 01 §3](../07%20-%20Ecosistema/01%20-%20GitHub%20-%20organización%20YoYoGames.md) — las extensiones `GMEXT-*` móviles
- [01 · 15 — Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md) — medir antes de optimizar, y [00 · Anatomía de un juego completo](./00%20-%20Anatomía%20de%20un%20juego%20completo.md) — dónde encaja todo esto en el arco

---

## Fuentes

Consultadas el **6 de septiembre de 2026**.

**Manual oficial de GameMaker**, leído en el espejo local `09 - Manual oficial/manual-lts-2026-es/`:

- [Opciones de juego · Android](https://manual.gamemaker.io/lts/es/Settings/Game_Options/Android.htm) — orientaciones, arquitecturas de CPU, escala, tamaño de página de textura, permisos, margen de reposo, iconos adaptativos, AAB. Y [· iOS](https://manual.gamemaker.io/lts/es/Settings/Game_Options/iOS.htm) — orientaciones, soporte de dispositivos, interpolación, pantallas de lanzamiento, Team Identifier.
- [Grupos de texturas](https://manual.gamemaker.io/lts/es/Settings/Texture_Groups.htm) — BZ2+QOI frente a QOI en Android, «Permitir escala» y el rechazo de apps por texturas borrosas. [Compilador YoYo](https://manual.gamemaker.io/lts/es/Settings/YoYo_Compiler.htm) — YYC en Android e iOS y los SDK que exige.
- [`os_is_paused`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/OS_And_Compiler/os_is_paused.htm) (comportamiento distinto en móvil y escritorio; el audio no se reanuda solo), [`os_lock_orientation`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/OS_And_Compiler/os_lock_orientation.htm), [`os_set_orientation_lock`](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/OS_And_Compiler/os_set_orientation_lock.htm), [`os_powersave_enable`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/OS_And_Compiler/os_powersave_enable.htm), [`os_request_permission`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/OS_And_Compiler/os_request_permission.htm), [`os_get_info`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/OS_And_Compiler/os_get_info.htm) y [`os_device`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/OS_And_Compiler/os_device.htm) (obsoleta).
- [`display_set_ui_visibility`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Cameras_And_Display/display_set_ui_visibility.htm), [`display_set_sleep_margin`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Cameras_And_Display/display_set_sleep_margin.htm) (4 ms en móvil, 10 en escritorio), [`device_get_tilt_x`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Game_Input/Device_Input/device_get_tilt_x.htm) y [`virtual_key_add`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Game_Input/Virtual_Keys_And_Keyboards/virtual_key_add.htm).
- [Evento asíncrono de sistema](https://manual.gamemaker.io/lts/es/The_Asset_Editors/Object_Properties/Async_Events/System.htm) — claves `virtual keyboard status`, `screen_height` y `permission_request_result`. [El gestor de dispositivos](https://manual.gamemaker.io/lts/es/Setting_Up_And_Version_Information/The_Device_Manager.htm) — *Detect Device*, *Run AVD* y el Mac como paso previo a iOS.

**Guías de plataforma y requisitos de las tiendas**

- [Touch target size — Android Accessibility Help](https://support.google.com/accessibility/android/answer/7101858?hl=en): *«Consider making touch targets at least 48x48dp, separated by 8dp of space or more… A touch target of 48x48dp results in a physical size of about 9mm»*. Lo mismo en [Material Design 3](https://m3.material.io/foundations/designing/structure).
- **Apple Human Interface Guidelines** — mínimo de **44 × 44 pt**, con distinción entre tamaño visual y área sensible. ⚠️ Las páginas de `developer.apple.com/design/human-interface-guidelines/` se renderizan con JavaScript y no se pudieron descargar en texto plano; la cifra está contrastada con varias referencias secundarias que la citan textualmente y es coherente con los 48 dp de Material.
- [Target API level requirements for Google Play apps](https://support.google.com/googleplay/android-developer/answer/11926878?hl=en) — API 36 para apps nuevas y actualizaciones, API 35 para seguir visible; 31-08-2026, con prórroga hasta el 01-11-2026.
- [Upcoming requirements — Apple Developer](https://developer.apple.com/news/upcoming-requirements/) — *«Since April 28, 2026 · Apps uploaded to App Store Connect must be built with Xcode 26 or later using an SDK for iOS 26…»*.

**GameMaker, fuera del manual**

- [How To Add Multi-touch and Virtual Joystick Controls](https://gamemaker.io/en/tutorials/multi-touch-joystick) — tutorial oficial. ⚠️ `gamemaker.io` responde **403** a la descarga automática; su enfoque (cada toque es un «dispositivo» leído en bucle) se confirmó por búsqueda y coincide con la documentación de `device_mouse_*` del manual.
- [GMEXT-MobileUtils](https://github.com/YoYoGames/GMEXT-MobileUtils) — vibración, verificada leyendo el código descargado en `11 - Código descargado/extensiones_oficiales/GMEXT-MobileUtils/docs/vibration.js`.
