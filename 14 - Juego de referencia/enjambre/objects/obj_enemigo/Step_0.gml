if (global.congelado > 0) exit;

var _nave = instance_nearest(x, y, obj_nave);
if (_nave != noone && instance_exists(_nave)) {
    var _dir = point_direction(x, y, _nave.x, _nave.y);
    // El veloz zigzaguea: si los tres persiguieran en línea recta, esquivarlos sería
    // el mismo gesto siempre y el juego se acabaría en dos oleadas.
    if (tipo == 1) _dir += sin(current_time / 180 + fase) * 38;
    x += lengthdir_x(velocidad, _dir);
    y += lengthdir_y(velocidad, _dir);
}

if (destello > 0) destello -= 1;

// Impacto de bala del jugador
var _b = instance_place(x, y, obj_bala);
if (_b != noone && !_b.de_enemigo) {
    instance_destroy(_b);
    vida -= 1;
    destello = 4;
    sonar(snd_impacto, random_range(0.9, 1.15));
    sacudir(2.5);
    if (vida <= 0) morir();
}

function morir() {
    // Copiar antes de destruir: después, este `id` ya no sirve para nada.
    var _x = x, _y = y, _t = tipo, _g = generacion;
    global.puntos += puntos;
    sonar(snd_estallido, random_range(0.92, 1.08));
    sacudir(7);
    congelar(3);
    repeat (6) {
        instance_create_layer(_x, _y, "Instances", obj_explosion,
            { escala : 1, tono : c_white });
    }
    // El divisor se parte en dos veloces. Una sola regla, y la oleada 5 cambia de
    // carácter entera.
    if (_t == 2 && _g < 1) {
        repeat (2) {
            instance_create_layer(_x + irandom_range(-12, 12), _y + irandom_range(-12, 12),
                "Instances", obj_enemigo, { tipo : 1, generacion : _g + 1 });
        }
    }
    if (irandom(99) < 34) {
        instance_create_layer(_x, _y, "Instances", obj_celda, {});
    }
    instance_destroy();
}
