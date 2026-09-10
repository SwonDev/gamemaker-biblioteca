/// Fondo de estrellas con parallax: tres capas a distinta velocidad. Es lo que
/// convierte un fondo negro en un espacio por el que te mueves.
if (!variable_instance_exists(id, "capa")) capa = 0;
sprite_index = (capa == 0) ? spr_estrella : spr_estrella2;
rapidez = 0.25 + capa * 0.55;
brillo = [0.45, 0.7, 1][capa];
image_speed = 0;
