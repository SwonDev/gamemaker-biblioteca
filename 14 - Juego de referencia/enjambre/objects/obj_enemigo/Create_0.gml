/// Tres tipos en un objeto, decididos por `tipo`. Tres objetos separados con el 90 %
/// del código repetido es la otra opción, y envejece peor.
if (!variable_instance_exists(id, "tipo")) tipo = 0;   // 0 rastreador · 1 veloz · 2 divisor
if (!variable_instance_exists(id, "generacion")) generacion = 0;

switch (tipo) {
    case 0: sprite_index = spr_rastreador; velocidad = 1.15; vida = 3; puntos = 10; break;
    case 1: sprite_index = spr_veloz;      velocidad = 2.9;  vida = 1; puntos = 15; break;
    case 2: sprite_index = spr_divisor;    velocidad = 1.5;  vida = 4; puntos = 20; break;
}
velocidad *= 1 + (global.oleada - 1) * 0.06;   // la oleada aprieta, no solo llena
image_speed = 0;
fase = random(6.28);
destello = 0;
