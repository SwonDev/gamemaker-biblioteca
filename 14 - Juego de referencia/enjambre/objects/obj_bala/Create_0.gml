if (!variable_instance_exists(id, "direccion")) direccion = 0;
if (!variable_instance_exists(id, "de_enemigo")) de_enemigo = false;
rapidez = de_enemigo ? 5 : 11;
sprite_index = de_enemigo ? spr_bala_enemiga : spr_bala;
vida = 120;
