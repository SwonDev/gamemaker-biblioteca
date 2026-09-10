// La explosión NO se congela con el hit-stop: si se parara, el golpe se vería muerto.
cuadro += 0.34;
x += lengthdir_x(rapidez, dir);
y += lengthdir_y(rapidez, dir);
rapidez *= 0.9;
ang += giro;
if (cuadro >= 6) instance_destroy();
