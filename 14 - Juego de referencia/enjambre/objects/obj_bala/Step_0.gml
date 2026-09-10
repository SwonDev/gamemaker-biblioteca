if (global.congelado > 0) exit;
x += lengthdir_x(rapidez, direccion);
y += lengthdir_y(rapidez, direccion);
vida -= 1;
// Fuera de la sala o agotada: se destruye. Una bala inmortal es una fuga con patas.
if (vida <= 0 || x < -16 || y < -16 || x > room_width + 16 || y > room_height + 16) {
    instance_destroy();
}
