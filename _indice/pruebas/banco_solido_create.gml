// Create de obj_solido. Existe para medir una sola cosa: si las variables que
// `nivel_mapa_construir()` pasa en el QUINTO argumento de `instance_create_layer()`
// ya están puestas cuando corre el Create. De eso depende que un objeto de rejilla
// pueda deducir su posición de su casilla (r15 §2.5).
vio_col   = variable_instance_exists(id, "nivel_col")   ? nivel_col   : -1;
vio_clave = variable_instance_exists(id, "nivel_clave") ? nivel_clave : "(no estaba)";
