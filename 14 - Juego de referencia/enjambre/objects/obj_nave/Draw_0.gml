// Parpadeo al ser invulnerable: la única forma de que el jugador sepa que está
// protegido sin escribírselo en la pantalla.
if (invulnerable > 0 && (invulnerable div 4) mod 2 == 0) exit;

var _spr = propulsando ? spr_nave_prop : spr_nave;
var _sub = propulsando ? ((current_time div 60) mod 3) : 0;
draw_sprite_ext(_spr, _sub, x, y, 1, 1, image_angle, c_white, 1);
