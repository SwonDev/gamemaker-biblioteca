var _sub = (current_time div 120) mod sprite_get_number(sprite_index);
if (destello > 0) {
    // Destello blanco al recibir: sin él no se sabe si la bala ha entrado.
    gpu_set_fog(true, c_white, 0, 0);
    draw_sprite_ext(sprite_index, _sub, x, y, 1, 1, 0, c_white, 1);
    gpu_set_fog(false, c_white, 0, 0);
} else {
    draw_sprite_ext(sprite_index, _sub, x, y, 1, 1, 0, c_white, 1);
}
