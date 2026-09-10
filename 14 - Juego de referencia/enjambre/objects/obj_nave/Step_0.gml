// El hit-stop congela el mundo, no la interfaz: si esto no estuviera, el golpe no
// se sentiría y el juego iría a tirones sin motivo aparente.
if (global.congelado > 0) exit;

var _e = entrada_leer();

// --- movimiento con inercia -------------------------------------------------
var _mx = _e.mover_x, _my = _e.mover_y;
var _lon = point_distance(0, 0, _mx, _my);
if (_lon > 1) { _mx /= _lon; _my /= _lon; }
propulsando = (_lon > 0.1);
vel_x = (vel_x + _mx * acel) * roce;
vel_y = (vel_y + _my * acel) * roce;
var _v = point_distance(0, 0, vel_x, vel_y);
if (_v > vel_max) { vel_x = vel_x / _v * vel_max; vel_y = vel_y / _v * vel_max; }
x += vel_x;
y += vel_y;

// Los bordes empujan de vuelta en vez de frenar en seco: se siente mejor y evita
// que el jugador se quede pegado a una pared.
var _m = 24;
if (x < _m)              { x = _m;              vel_x = abs(vel_x) * 0.4; }
if (x > room_width - _m) { x = room_width - _m; vel_x = -abs(vel_x) * 0.4; }
if (y < _m)              { y = _m;              vel_y = abs(vel_y) * 0.4; }
if (y > room_height - _m){ y = room_height - _m; vel_y = -abs(vel_y) * 0.4; }

// --- apuntado ---------------------------------------------------------------
var _ax, _ay;
if (global.captura) {
    // Apunta al enemigo más cercano. Es exactamente lo que hace el ratón de una
    // persona; se automatiza para que la captura muestre combate real —impactos,
    // explosiones, puntos— y no una nave disparando al vacío.
    var _obj_cerca = instance_nearest(x, y, obj_enemigo);
    if (_obj_cerca != noone && instance_exists(_obj_cerca)) {
        _ax = _obj_cerca.x; _ay = _obj_cerca.y;
    } else {
        _ax = room_width / 2; _ay = room_height / 2;
    }
} else if (_e.usa_mando && point_distance(0, 0, _e.apuntar_x, _e.apuntar_y) > 0.3) {
    _ax = x + _e.apuntar_x * 100;
    _ay = y + _e.apuntar_y * 100;
} else {
    _ax = mouse_x; _ay = mouse_y;
}
// La nave gira hacia donde apunta, pero no de golpe: el giro suave se lee mejor.
var _obj = point_direction(x, y, _ax, _ay) - 90;
image_angle += angle_difference(_obj, image_angle) * 0.35;

// --- disparo ----------------------------------------------------------------
if (enfriamiento > 0) enfriamiento -= 1;
if (_e.disparar && enfriamiento <= 0 && energia >= 6) {
    enfriamiento = 7;
    energia -= 6;
    repeat (2) {
        var _lado = (enfriamiento mod 2) ? 10 : -10;
        var _b = instance_create_layer(
            x + lengthdir_x(10, image_angle + 90 + _lado * 2),
            y + lengthdir_y(10, image_angle + 90 + _lado * 2),
            "Instances", obj_bala,
            { direccion : image_angle + 90 + random_range(-2, 2), de_enemigo : false });
        _lado = -_lado;
    }
    // Retroceso: la nave se echa atrás al disparar. Un detalle de dos líneas que
    // hace que el arma pese (04 · 15).
    vel_x -= lengthdir_x(0.8, image_angle + 90);
    vel_y -= lengthdir_y(0.8, image_angle + 90);
    sonar(snd_disparo, random_range(0.94, 1.06));
    sacudir(1.2);
}

// La energía se recarga sola, despacio: obliga a moverse a por celdas en vez de
// quedarse en una esquina disparando.
energia = min(energia_max, energia + 0.35);
if (invulnerable > 0) invulnerable -= 1;

// --- daño -------------------------------------------------------------------
if (invulnerable <= 0) {
    var _golpe = instance_place(x, y, obj_enemigo);
    if (_golpe != noone) {
        instance_destroy(_golpe);
        herido();
    }
    var _bala = instance_place(x, y, obj_bala);
    if (_bala != noone && _bala.de_enemigo) {
        instance_destroy(_bala);
        herido();
    }
}

// Recoger celdas: se copian los datos ANTES de destruir (13 · 10 §12 bis.4).
var _celda = instance_place(x, y, obj_celda);
if (_celda != noone) {
    var _cx = _celda.x, _cy = _celda.y;
    instance_destroy(_celda);
    energia = min(energia_max, energia + 28);
    global.puntos += 25;
    sonar(snd_recoger, random_range(0.97, 1.05));
    repeat (4) {
        instance_create_layer(_cx, _cy, "Instances", obj_explosion,
            { escala : 0.35, tono : make_colour_rgb(250, 196, 84) });
    }
}

function herido() {
    global.vidas -= 1;
    invulnerable = 90;
    energia = energia_max;
    sonar(snd_herido, 1);
    sacudir(14);
    congelar(8);
    repeat (10) {
        instance_create_layer(x, y, "Instances", obj_explosion,
            { escala : 0.8, tono : make_colour_rgb(240, 108, 62) });
    }
}
