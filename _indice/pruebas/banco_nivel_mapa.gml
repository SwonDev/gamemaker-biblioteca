// Banco de pruebas de scr_nivel_mapa.gml. Todo lo que comprueba cabe en un solo
// evento: no hace falta esperar a ningún frame.
function banco_nivel_mapa()
{
var _leyenda = {
    "#" : { objeto: obj_solido,  solido: true  },
    "o" : { objeto: obj_moneda,  solido: false },
    "@" : { objeto: noone,       papel:  "aparicion" },
    "!" : { objeto: obj_salida,  papel:  "salida" }
};

// --- 1 · Mapa bien formado --------------------------------------------------
var _m = ["#####",
          "#@o!#",
          "#####"];

var _r = nivel_mapa_construir(_m, _leyenda, { celda: 16, capa: "Instances", nombre: "n1" });

comprobar("mapa correcto: sin problemas", array_length(_r.problemas) == 0, _r.problemas);
comprobar("ancho y alto", _r.ancho == 5 && _r.alto == 3, string(_r.ancho) + "x" + string(_r.alto));
comprobar("aparicion detectada", _r.hay_aparicion && _r.aparicion_x == 16 && _r.aparicion_y == 16,
          string(_r.aparicion_x) + "," + string(_r.aparicion_y));
comprobar("papel salida registrado",
          struct_exists(_r.papeles, "salida") && array_length(_r.papeles.salida) == 1);
comprobar("creadas = 12 solidos + moneda + salida", _r.creadas == 14,
          "creadas=" + string(_r.creadas) + " saltadas=" + string(_r.saltadas));
comprobar("ninguna enterrada en un marco hueco", _r.saltadas == 0, _r.saltadas);

// --- 2 · Roca enterrada -----------------------------------------------------
var _macizo = ["@!#####",
               "#######",
               "#######",
               "#######",
               "#######"];
var _r2 = nivel_mapa_construir(_macizo, _leyenda, { capa: "Instances", nombre: "n2" });
show_debug_message("  (macizo: creadas=" + string(_r2.creadas) + " saltadas=" + string(_r2.saltadas) + ")");
comprobar("hay roca enterrada que se salta", _r2.saltadas > 0, _r2.saltadas);
comprobar("invariante: cada casilla o se crea o se salta", _r2.creadas + _r2.saltadas == 34,
          string(_r2.creadas) + "+" + string(_r2.saltadas));
comprobar("el centro del macizo esta enterrado",
          nivel_mapa_enterrada(_macizo, _leyenda, 3, 2, { fuera_es_solido: true }));
comprobar("la esquina esta enterrada si fuera cuenta como solido",
          nivel_mapa_enterrada(_macizo, _leyenda, 6, 4, { fuera_es_solido: true }));
comprobar("la esquina NO esta enterrada si fuera cuenta como vacio",
          !nivel_mapa_enterrada(_macizo, _leyenda, 6, 4, { fuera_es_solido: false }));
comprobar("una casilla junto a la salida no esta enterrada",
          !nivel_mapa_enterrada(_macizo, _leyenda, 2, 0, { fuera_es_solido: true }));

// --- 3 · Bitmask y el borde del mapa ---------------------------------------
var _b_solido = nivel_mapa_bitmask(_m, _leyenda, 0, 0, { fuera_es_solido: true });
var _b_vacio  = nivel_mapa_bitmask(_m, _leyenda, 0, 0, { fuera_es_solido: false });
comprobar("bitmask esquina, fuera solido = 15", _b_solido == 15, _b_solido);
comprobar("bitmask esquina, fuera vacio = 6 (E+S)", _b_vacio == 6, _b_vacio);

// --- 4 · Clave estable en la instancia -------------------------------------
comprobar("la moneda existe", instance_number(obj_moneda) >= 1, instance_number(obj_moneda));
var _moneda = instance_find(obj_moneda, 0);
with (_moneda)
{
    comprobar("la instancia lleva su clave estable, leida por su nombre desnudo",
              nivel_clave == "n1_x2_y1", nivel_clave);
    comprobar("y su caracter", nivel_char == "o", nivel_char);
    comprobar("la instancia lleva col y fila", nivel_col == 2 && nivel_fila == 1,
              string(nivel_col) + "," + string(nivel_fila));

    // --- La colision que obligo a renombrar las funciones, MEDIDA -----------
    // Una variable de instancia con el mismo nombre que una funcion global.
    variable_instance_set(id, "nivel_mapa_clave", "VALOR_DE_LA_VARIABLE");
    comprobar("colision: la variable de instancia SI existe",
              variable_instance_exists(id, "nivel_mapa_clave"));
    comprobar("colision: variable_instance_get() SI devuelve el valor",
              variable_instance_get(id, "nivel_mapa_clave") == "VALOR_DE_LA_VARIABLE",
              variable_instance_get(id, "nivel_mapa_clave"));
    comprobar("colision: el nombre DESNUDO devuelve la funcion, no el valor",
              is_callable(nivel_mapa_clave), nivel_mapa_clave);
}
comprobar("colision: desde fuera, instancia.nombre devuelve...",
          _moneda.nivel_mapa_clave == "VALOR_DE_LA_VARIABLE",
          _moneda.nivel_mapa_clave);

// --- 4 bis · El Create ya ve las variables de la casilla --------------------
with (instance_find(obj_solido, 0))
{
    comprobar("el Create del objeto ya ve nivel_col (5o argumento)", vio_col >= 0, vio_col);
    comprobar("y tambien nivel_clave", string_pos("_x", vio_clave) > 0, vio_clave);
}

// --- 4 ter · El gancho al_crear --------------------------------------------
var _vistos = { n: 0 };
nivel_mapa_construir(_m, _leyenda, {
    nombre: "n4b",
    al_crear: method(_vistos, function(_inst, _c, _col, _fila) { n++; })
});
comprobar("al_crear se llama una vez por instancia creada", _vistos.n == 14, _vistos.n);

// --- 5 · El filtro `omitir` -------------------------------------------------
var _r3 = nivel_mapa_construir(_m, _leyenda, {
    nombre: "n3",
    omitir: function(_c, _clave, _col, _fila) { return (_c == "o"); }
});
comprobar("omitir descarta la moneda", _r3.creadas == 13, "creadas=" + string(_r3.creadas));

// --- 6 · Mapas mal formados: cada uno se detecta ---------------------------
comprobar("fila corta detectada",
          array_length(nivel_mapa_validar(["#####", "###", "#@!##"], _leyenda)) > 0);
comprobar("caracter sin leyenda detectado",
          array_length(nivel_mapa_validar(["#@Z!#"], _leyenda)) > 0);
comprobar("sin aparicion detectada",
          array_length(nivel_mapa_validar(["##!##"], _leyenda)) > 0);
comprobar("dos apariciones detectadas",
          array_length(nivel_mapa_validar(["#@@!#"], _leyenda)) > 0);
comprobar("sin salida detectada",
          array_length(nivel_mapa_validar(["#@###"], _leyenda)) > 0);
comprobar("capa inexistente detectada",
          array_length(nivel_mapa_validar(["#@!##"], _leyenda, { capa: "Capa_Que_No_Existe" })) > 0);
comprobar("leyenda con un caracter que tambien es aire",
          array_length(nivel_mapa_validar(["#@!##"], { ".": { objeto: obj_solido } })) > 0);
comprobar("objeto inexistente en la leyenda detectado",
          array_length(nivel_mapa_validar(["#@!##"], {
              "#": { objeto: 999999, solido: true },
              "@": { objeto: noone, papel: "aparicion" },
              "!": { objeto: obj_salida, papel: "salida" }
          })) > 0);
comprobar("mapa correcto no da problemas", array_length(nivel_mapa_validar(["#@!##"], _leyenda)) == 0,
          nivel_mapa_validar(["#@!##"], _leyenda));

// --- 7 · Con el mapa mal, NO se crea nada ----------------------------------
var _fallo = { visto: false, texto: "" };
var _antes = instance_number(obj_solido);
var _r4 = nivel_mapa_construir(["#####", "###"], _leyenda, {
    nombre: "n4",
    al_fallar: method(_fallo, function(_t, _p) { visto = true; texto = _t; })
});
comprobar("al_fallar se llamo", _fallo.visto);
comprobar("no se creo ni una instancia con el mapa mal",
          instance_number(obj_solido) == _antes,
          string(instance_number(obj_solido)) + " vs " + string(_antes));
comprobar("devuelve la lista de problemas", array_length(_r4.problemas) > 0);
comprobar("el texto del fallo nombra el nivel", string_pos("n4", _fallo.texto) > 0, _fallo.texto);

// --- 8 · Parsear texto ------------------------------------------------------
var _filas = nivel_mapa_filas_de_cadena("\n#####\r\n#@..!#\n\n");
comprobar("filas_de_cadena quita los extremos vacios y respeta CRLF",
          array_length(_filas) == 2 && _filas[0] == "#####" && _filas[1] == "#@..!#",
          string(array_length(_filas)) + " -> " + string(_filas));
comprobar("una fila vacia EN MEDIO sobrevive para que la validacion la vea",
          array_length(nivel_mapa_filas_de_cadena("###\n\n###")) == 3);

// --- 9 · Autotile ----------------------------------------------------------
var _r5 = nivel_mapa_construir(["###", "#@#", "#!#"], _leyenda,
                          { nombre: "n5", autotile: true, saltar_enterradas: false });
comprobar("autotile no rompe la construccion", array_length(_r5.problemas) == 0, _r5.problemas);

}
