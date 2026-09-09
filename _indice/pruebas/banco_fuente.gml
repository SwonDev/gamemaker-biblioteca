// Banco de pruebas de la fuente de sprite — la tercera salida de la Trampa 12
// (12 · 09 §0). Comprueba lo que `font glyphlist` no puede decir de una fuente de
// sprite: que los glifos están, que el espacio mide lo que tú decidiste y que los
// caracteres españoles no se caen por el camino.
//
// El `string_map` tiene que coincidir CARÁCTER A CARÁCTER con el orden en que se
// importaron las sub-imágenes. Si divergen, el juego dibuja letras cambiadas y
// compila igual de limpio: por eso el primer comprobante compara las dos longitudes.

#macro GLIFOS_MAPA " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;!?-+()áéíóúüñÁÉÍÓÚÜÑ¿¡"

function banco_fuente()
{
    comprobar("el sprite de glifos tiene tantas sub-imagenes como caracteres el mapa",
              sprite_get_number(spr_glifos) == string_length(GLIFOS_MAPA),
              string(sprite_get_number(spr_glifos)) + " vs " + string(string_length(GLIFOS_MAPA)));

    var _f = font_add_sprite_ext(spr_glifos, GLIFOS_MAPA, true, 1);
    comprobar("font_add_sprite_ext devuelve una fuente valida", font_exists(_f), _f);

    draw_set_font(_f);

    var _a = string_width("A");
    comprobar("una letra normal mide algo", _a > 0, _a);

    // Lo que motiva la barra sólida: con la sub-imagen del espacio vacía, el ancho
    // del espacio lo decide el motor. Con barra, lo decides tú.
    var _esp = string_width(" ");
    show_debug_message("MEDIDO · string_width(\" \") con barra solida = " + string(_esp));
    comprobar("el espacio mide mas que cero", _esp > 0, _esp);

    // Los caracteres españoles: la razón de existir de font_add_sprite_ext frente a
    // font_add_sprite, que exige códigos consecutivos.
    var _acentos = ["á", "é", "í", "ó", "ú", "ü", "ñ", "Á", "Ñ", "¿", "¡"];
    var _fallan = "";
    for (var _i = 0; _i < array_length(_acentos); _i++)
    {
        if (string_width(_acentos[_i]) <= 0) _fallan += _acentos[_i];
    }
    comprobar("los once caracteres españoles del mapa miden algo", _fallan == "",
              "no miden: " + _fallan);

    // Una frase entera con tildes y eñes mide más que la misma sin ellas: si el motor
    // estuviera descartando los acentos en silencio (Trampa 12), no lo haría.
    var _con = string_width("¡Añádeme más peón!");
    var _sin = string_width("Ademe ms pen!");
    comprobar("la frase con tildes mide mas que la mutilada", _con > _sin,
              string(_con) + " vs " + string(_sin));

    // Un carácter que NO está en el mapa no debe inventarse un ancho.
    var _fuera = string_width("%");
    show_debug_message("MEDIDO · string_width de un caracter fuera del mapa = " + string(_fuera));

    // --- Y lo que esto abre: detectar la Trampa 12 SIN capturar la pantalla ------
    // Si un carácter que la fuente no tiene mide 0, entonces `string_width()` puede
    // decir, desde dentro del juego, si una fuente dibuja español — sin mirar un
    // píxel. Se mide contra la fuente POR DEFECTO del motor, que es la que la
    // Trampa 12 acusa de comerse los acentos en silencio.
    draw_set_font(-1);
    var _def_a = string_width("a");
    var _def_acento = string_width("á");
    var _def_ene = string_width("ñ");
    var _def_apertura = string_width("¿");
    show_debug_message("MEDIDO · fuente por defecto: a=" + string(_def_a)
        + " á=" + string(_def_acento) + " ñ=" + string(_def_ene)
        + " ¿=" + string(_def_apertura));

    comprobar("la letra sin acento SI existe en la fuente por defecto", _def_a > 0, _def_a);
    comprobar("los acentos NO existen en la fuente por defecto (Trampa 12)",
              _def_acento == 0 && _def_ene == 0 && _def_apertura == 0,
              string(_def_acento) + "," + string(_def_ene) + "," + string(_def_apertura));

    // Y el detector reutilizable que sale de ahí, de 06 · scr_debug.gml.
    var _faltan_def = debug_fuente_sin_glifos(-1, "áéíóúüñÁÉÍÓÚÜÑ¿¡");
    comprobar("debug_fuente_sin_glifos caza los 16 que faltan en la fuente del motor",
              array_length(_faltan_def) == 16, array_length(_faltan_def));

    var _faltan_nuestra = debug_fuente_sin_glifos(_f, "áéíóúüñÁÉÍÓÚÜÑ¿¡");
    comprobar("y no encuentra ninguno en la fuente de sprite que acabamos de hacer",
              array_length(_faltan_nuestra) == 0, _faltan_nuestra);

    comprobar("debug_exigir_fuente_con_acentos dice false con la del motor",
              !debug_exigir_fuente_con_acentos(-1));
    comprobar("y true con la nuestra", debug_exigir_fuente_con_acentos(_f));

    font_delete(_f);
}
