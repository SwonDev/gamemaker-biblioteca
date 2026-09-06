# 18 · Menús con scroll y navegación

> Una lista de opciones más larga que la pantalla: selector de niveles, inventario, ajustes,
> lista de partidas guardadas. El problema no es dibujarla, es que **el cursor y la ventana
> visible se muevan de forma coherente** con teclado, mando y ratón a la vez.
>
> **Hueco detectado** al cruzar el [catálogo de tutoriales del foro](../07%20-%20Ecosistema/16%20-%20Cat%C3%A1logo%20de%20la%20secci%C3%B3n%20Tutorials%20del%20foro.md)
> con esta biblioteca.

---

## El error de partida

Casi todo el mundo escribe el menú así:

```gml
/// ❌ obj_menu · Draw
draw_text(100, 100, "Jugar");
draw_text(100, 130, "Opciones");
draw_text(100, 160, "Salir");

if (seleccion == 0) draw_text(80, 100, ">");
// …y ahora añade una opción y toca cuatro sitios
```

**El menú son datos, no código de dibujo.** En cuanto lo separas, el scroll, el mando, el
ratón y la traducción salen casi solos.

---

## 1 · Los datos

```gml
/// obj_menu · Create
opciones = [
    { texto: "Continuar",   accion: menu_continuar,  activa: global.hay_partida },
    { texto: "Nueva partida", accion: menu_nueva,    activa: true },
    { texto: "Opciones",    accion: menu_opciones,   activa: true },
    { texto: "Créditos",    accion: menu_creditos,   activa: true },
    { texto: "Salir",       accion: menu_salir,      activa: true },
];

seleccion   = 0;      // índice de la opción marcada
alto_fila   = 32;
visibles    = 6;      // cuántas filas caben en la ventana
desplaz     = 0;      // primera fila visible (entero)
desplaz_pix = 0;      // el mismo valor, en píxeles y suavizado
```

> 💡 **`accion` guarda una función, no una cadena.** En GML las funciones son valores: puedes
> meterlas en un struct y llamarlas con `opciones[seleccion].accion()`. Eso elimina el
> `switch (seleccion)` gigante que crece con cada opción nueva.

---

## 2 · Mover el cursor saltándose las opciones inactivas

```gml
/// scr_menu — mover el cursor _dir posiciones, ignorando las opciones desactivadas
function menu_mover(_opciones, _desde, _dir) {
    var _n = array_length(_opciones);
    var _i = _desde;

    // como mucho damos una vuelta completa: si todas están inactivas, no colgamos
    repeat (_n) {
        _i = (_i + _dir + _n) mod _n;
        if (_opciones[_i].activa) return _i;
    }
    return _desde;
}
```

> ⚠️ **El `repeat (_n)` es la parte importante.** Un `while (!activa)` sin tope se cuelga en
> bucle infinito el día que todas las opciones estén desactivadas — y ese día llega, porque
> «Continuar» está desactivada en la primera partida.

---

## 3 · La entrada, unificada

```gml
/// obj_menu · Step
var _arriba = keyboard_check_pressed(vk_up)
           || gamepad_button_check_pressed(0, gp_padu)
           || mouse_wheel_up();

var _abajo  = keyboard_check_pressed(vk_down)
           || gamepad_button_check_pressed(0, gp_padd)
           || mouse_wheel_down();

var _aceptar = keyboard_check_pressed(vk_enter)
            || gamepad_button_check_pressed(0, gp_face1);

if (_arriba) { seleccion = menu_mover(opciones, seleccion, -1); audio_play_sound(snd_menu_mover, 1, false); }
if (_abajo)  { seleccion = menu_mover(opciones, seleccion,  1); audio_play_sound(snd_menu_mover, 1, false); }

if (_aceptar) {
    audio_play_sound(snd_menu_aceptar, 1, false);
    opciones[seleccion].accion();       // aquí se ejecuta la función guardada
}
```

> 🔺 **`mouse_wheel_up()` es una función, no una variable** — lleva paréntesis. Y solo
> funciona en el evento Step, no en Draw.
>
> 💡 En lugar de estas tres comprobaciones encadenadas, un proyecto serio usa una capa de
> input. Ver [Input, la librería de JujuAdams](../07%20-%20Ecosistema/02%20-%20Librerías%20esenciales%20de%20la%20comunidad.md)
> y [12 · Input](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md).

---

## 4 · El scroll: mantener el cursor dentro de la ventana

Esta es la parte que la gente resuelve mal. La regla es sencilla: **el desplazamiento solo se
mueve cuando el cursor se sale de la ventana**, y se mueve lo justo.

```gml
/// obj_menu · Step (después de mover la selección)
var _n = array_length(opciones);

// el cursor se salió por arriba
if (seleccion < desplaz)                desplaz = seleccion;
// se salió por abajo
if (seleccion >= desplaz + visibles)    desplaz = seleccion - visibles + 1;

// nunca desplazar más allá del final de la lista
desplaz = clamp(desplaz, 0, max(0, _n - visibles));

// suavizado: el valor en píxeles persigue al entero
desplaz_pix = lerp(desplaz_pix, desplaz * alto_fila, 0.25);
```

> 💡 **Los dos valores separados son el truco.** `desplaz` es un entero y decide **qué filas
> se dibujan**; `desplaz_pix` es un flotante suavizado y decide **dónde se dibujan**. Si usas
> uno solo, o el scroll va a saltos o dibujas filas a medias fuera de la ventana.
>
> 🔺 **`lerp(a, b, 0.25)` depende de los fotogramas.** A 30 fps se mueve la mitad de rápido
> que a 60. Si tu juego no fija la velocidad, usa
> [`delta_time`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Date_And_Time/delta_time.md):
> `lerp(a, b, 1 - power(0.75, delta_time / 16667))`.

---

## 5 · Dibujar solo lo visible

```gml
/// obj_menu · Draw GUI
var _x = 120, _y = 80;
var _n = array_length(opciones);

// recorte: nada se dibuja fuera de la ventana del menú
var _alto_ventana = visibles * alto_fila;

// dibujamos una fila de más arriba y otra de más abajo, para que entren deslizándose
var _desde = max(0, desplaz - 1);
var _hasta = min(_n - 1, desplaz + visibles);

draw_set_valign(fa_top);

for (var _i = _desde; _i <= _hasta; _i++) {
    var _fila = opciones[_i];
    var _fy   = _y + (_i * alto_fila) - desplaz_pix;

    // fuera de la ventana: ni se dibuja
    if (_fy < _y - alto_fila || _fy > _y + _alto_ventana) continue;

    var _col = c_white;
    if (!_fila.activa)      _col = c_gray;
    else if (_i == seleccion) _col = c_yellow;

    draw_text_color(_x, _fy, _fila.texto, _col, _col, _col, _col, 1);

    if (_i == seleccion) draw_text(_x - 24, _fy, ">");
}

// indicadores de que hay más lista fuera de la pantalla
if (desplaz > 0)                    draw_text(_x, _y - 20, "▲");
if (desplaz + visibles < _n)        draw_text(_x, _y + _alto_ventana + 4, "▼");
```

> 💡 **Las flechas ▲▼ no son decoración.** Sin ellas, el jugador no sabe que hay más opciones
> y no las busca. Es el fallo de usabilidad más habitual de los menús con scroll.
>
> 💡 **Draw GUI, no Draw.** El menú no debe moverse con la cámara. Ver
> [11 · Dibujo y renderizado](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md).

---

## 6 · La barra de scroll (opcional, pero ayuda)

```gml
/// dentro del mismo Draw GUI
if (_n > visibles) {
    var _bx = _x + 300;
    var _bh = _alto_ventana;

    // canal
    draw_rectangle_color(_bx, _y, _bx + 4, _y + _bh, c_dkgray, c_dkgray, c_dkgray, c_dkgray, false);

    // pulgar: su alto es la proporción visible, su posición la proporción desplazada
    var _alto_pulgar = max(16, _bh * (visibles / _n));
    var _py = _y + (_bh - _alto_pulgar) * (desplaz / max(1, _n - visibles));

    draw_rectangle_color(_bx, _py, _bx + 4, _py + _alto_pulgar, c_white, c_white, c_white, c_white, false);
}
```

---

## Las trampas

| Trampa | Qué pasa | Solución |
|---|---|---|
| `while` buscando opción activa | Cuelgue si todas están inactivas | `repeat (array_length(...))` |
| Dibujar las N opciones siempre | Se dibujan 400 textos fuera de pantalla | `continue` fuera de la ventana |
| Un solo valor de scroll | O va a saltos o dibuja filas cortadas | `desplaz` entero + `desplaz_pix` suavizado |
| `switch (seleccion)` para las acciones | Crece con cada opción y se desincroniza | Guardar la función en el struct |
| Sin flechas ▲▼ | El jugador no sabe que hay más | Dibujarlas siempre que haya recorte |
| Menú en el evento Draw | Se mueve con la cámara | Draw GUI |

---

## Ver también

- [12 · Input — teclado, ratón y gamepad](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md)
- [16 · Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — para que las acciones del menú no llamen a media base de código
- [15 · Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) — el sonido y el retardo que hacen que un menú se sienta bien
