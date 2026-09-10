/// Draw GUI: el menú vive en coordenadas de pantalla, no de mundo. Dibujarlo en el
/// Draw normal es como se acaba con un menú que se mueve con la cámara.
var _w = display_get_gui_width();
var _h = display_get_gui_height();
draw_set_font(global.fnt);

// Fondo con degradado vertical, no un color plano: cuesta una llamada y cambia la
// sensación de la pantalla entera.
draw_sprite_stretched_ext(spr_estrella, 0, 0, 0, 1, 1, c_black, 0);
for (var i = 0; i < 24; i++) {
    var _y = _h * i / 24;
    var _c = merge_colour(make_colour_rgb(10, 12, 24), make_colour_rgb(28, 22, 52), i / 24);
    draw_rectangle_colour(0, _y, _w, _y + _h / 24 + 1, _c, _c, _c, _c, false);
}

draw_set_halign(fa_center);
draw_set_valign(fa_middle);

if (estado == "portada") {
    var _p = 1 + sin(tiempo / 24) * 0.04;
    draw_set_colour(make_colour_rgb(250, 196, 84));
    draw_text_transformed(_w / 2, _h * 0.36, txt("titulo"), 6 * _p, 6 * _p, 0);
    draw_set_colour(make_colour_rgb(176, 196, 232));
    draw_text_transformed(_w / 2, _h * 0.48, txt("sub"), 2, 2, 0);
    if ((tiempo div 30) mod 2 == 0) {
        draw_set_colour(make_colour_rgb(238, 244, 255));
        draw_text_transformed(_w / 2, _h * 0.72, txt("pulsa"), 1.6, 1.6, 0);
    }
} else if (estado == "menu") {
    draw_set_colour(make_colour_rgb(250, 196, 84));
    draw_text_transformed(_w / 2, _h * 0.20, txt("titulo"), 4, 4, 0);
    draw_set_colour(make_colour_rgb(126, 214, 234));
    draw_text_transformed(_w / 2, _h * 0.30, txt("record") + ": " + string(global.record), 1.8, 1.8, 0);
    for (var i = 0; i < array_length(opciones_menu); i++) {
        var _sel = (i == opcion);
        draw_set_colour(_sel ? make_colour_rgb(250, 196, 84) : make_colour_rgb(150, 166, 200));
        var _e = _sel ? 2.6 : 2.1;
        var _y = _h * 0.45 + i * 46;
        draw_text_transformed(_w / 2, _y, (_sel ? "> " : "") + txt(opciones_menu[i]) + (_sel ? " <" : ""), _e, _e, 0);
    }
} else if (estado == "opciones") {
    draw_set_colour(make_colour_rgb(250, 196, 84));
    draw_text_transformed(_w / 2, _h * 0.16, txt("opciones"), 3.4, 3.4, 0);
    for (var i = 0; i < array_length(opciones_ajustes); i++) {
        var _a = opciones_ajustes[i];
        var _sel = (i == opcion);
        draw_set_colour(_sel ? make_colour_rgb(250, 196, 84) : make_colour_rgb(150, 166, 200));
        var _y = _h * 0.32 + i * 46;
        var _valor = "";
        switch (_a) {
            case "idioma":   _valor = (global.idioma == "es") ? "Español" : "English"; break;
            case "musica":   _valor = string(round(global.op_musica * 100)) + " %"; break;
            case "efectos":  _valor = string(round(global.op_efectos * 100)) + " %"; break;
            case "sacudida": _valor = global.op_sacudida ? txt("si") : txt("no"); break;
            case "pantalla": _valor = window_get_fullscreen() ? txt("si") : txt("no"); break;
        }
        draw_set_halign(fa_right);
        draw_text_transformed(_w / 2 - 16, _y, (_sel ? "> " : "") + txt(_a), 2, 2, 0);
        draw_set_halign(fa_left);
        if (_valor != "") draw_text_transformed(_w / 2 + 16, _y, _valor, 2, 2, 0);
        draw_set_halign(fa_center);
    }
} else if (estado == "creditos") {
    draw_set_colour(make_colour_rgb(250, 196, 84));
    draw_text_transformed(_w / 2, _h * 0.18, txt("creditos"), 3.4, 3.4, 0);
    draw_set_colour(make_colour_rgb(200, 214, 240));
    draw_text_transformed(_w / 2, _h * 0.48, txt("creditos_txt"), 1.7, 1.7, 0);
    draw_set_colour(make_colour_rgb(150, 166, 200));
    draw_text_transformed(_w / 2, _h * 0.84, txt("volver"), 1.6, 1.6, 0);
}
draw_set_halign(fa_left);
draw_set_valign(fa_top);
