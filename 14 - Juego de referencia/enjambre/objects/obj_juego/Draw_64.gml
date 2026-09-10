/// HUD y pantallas superpuestas, en Draw GUI.
var _w = display_get_gui_width();
var _h = display_get_gui_height();
draw_set_font(global.fnt);
draw_set_valign(fa_top);

// --- barra de energía -------------------------------------------------------
var _nave = instance_exists(obj_nave) ? instance_find(obj_nave, 0) : noone;
if (_nave != noone) {
    var _bx = 20, _by = _h - 40, _bw = 260, _bh = 16;
    draw_set_colour(make_colour_rgb(20, 24, 40));
    draw_rectangle(_bx - 2, _by - 2, _bx + _bw + 2, _by + _bh + 2, false);
    var _f = _nave.energia / _nave.energia_max;
    var _col = (_f > 0.3) ? make_colour_rgb(126, 214, 234) : make_colour_rgb(240, 108, 62);
    draw_rectangle_colour(_bx, _by, _bx + _bw * _f, _by + _bh, _col, _col, _col, _col, false);
    draw_set_colour(make_colour_rgb(150, 166, 200));
    draw_text_transformed(_bx, _by - 22, txt("energia"), 1.4, 1.4, 0);
}

// --- marcadores -------------------------------------------------------------
draw_set_colour(make_colour_rgb(238, 244, 255));
draw_text_transformed(20, 18, txt("puntos") + ": " + string(global.puntos), 2, 2, 0);
draw_set_halign(fa_center);
draw_text_transformed(_w / 2, 18, txt("oleada") + " " + string(global.oleada), 2.2, 2.2, 0);
draw_set_halign(fa_right);
draw_set_colour(make_colour_rgb(250, 196, 84));
draw_text_transformed(_w - 20 - max(0, global.vidas) * 34, 18, txt("vidas") + ":", 2, 2, 0);
// Las vidas se dibujan con el SPRITE de la nave, no con un carácter. La primera
// versión usaba «▮», que no está en la hoja de glifos: la fuente lo omitió en
// silencio y el marcador salió vacío — la Trampa 12 otra vez, ahora con un símbolo
// en vez de una tilde. Un icono no depende de ninguna fuente.
for (var i = 0; i < max(0, global.vidas); i++) {
    draw_sprite_ext(spr_nave, 0, _w - 34 - i * 34, 30, 1.1, 1.1, 0, c_white, 1);
}
draw_set_halign(fa_left);

// --- aviso de oleada --------------------------------------------------------
if (aviso_oleada > 0) {
    var _a = min(1, aviso_oleada / 30);
    draw_set_halign(fa_center);
    draw_set_alpha(_a);
    draw_set_colour(make_colour_rgb(250, 196, 84));
    draw_text_transformed(_w / 2, _h * 0.32, txt("oleada") + " " + string(global.oleada), 5, 5, 0);
    draw_set_alpha(1);
    draw_set_halign(fa_left);
}

// --- ayuda al empezar -------------------------------------------------------
if (tiempo < 60 * 7 && global.oleada == 1) {
    draw_set_halign(fa_center);
    draw_set_colour(make_colour_rgb(150, 166, 200));
    var _e = entrada_leer();
    draw_text_transformed(_w / 2, _h - 90, _e.usa_mando ? txt("ayuda_mando") : txt("ayuda_mov"), 1.5, 1.5, 0);
    draw_set_halign(fa_left);
}

// --- pausa ------------------------------------------------------------------
if (estado == "pausa") {
    draw_set_alpha(0.78);
    draw_set_colour(make_colour_rgb(8, 10, 20));
    draw_rectangle(0, 0, _w, _h, false);
    draw_set_alpha(1);
    draw_set_halign(fa_center);
    draw_set_colour(make_colour_rgb(250, 196, 84));
    draw_text_transformed(_w / 2, _h * 0.26, txt("pausa"), 4.5, 4.5, 0);
    for (var i = 0; i < array_length(opciones_pausa); i++) {
        var _sel = (i == opcion);
        draw_set_colour(_sel ? make_colour_rgb(250, 196, 84) : make_colour_rgb(150, 166, 200));
        var _es = _sel ? 2.6 : 2.1;
        draw_text_transformed(_w / 2, _h * 0.45 + i * 46,
            (_sel ? "> " : "") + txt(opciones_pausa[i]), _es, _es, 0);
    }
    draw_set_halign(fa_left);
}

// --- derrota ----------------------------------------------------------------
if (estado == "derrota") {
    draw_set_alpha(0.85);
    draw_set_colour(make_colour_rgb(12, 6, 14));
    draw_rectangle(0, 0, _w, _h, false);
    draw_set_alpha(1);
    draw_set_halign(fa_center);
    draw_set_colour(make_colour_rgb(240, 108, 62));
    draw_text_transformed(_w / 2, _h * 0.24, txt("fin"), 4.5, 4.5, 0);
    draw_set_colour(make_colour_rgb(238, 244, 255));
    draw_text_transformed(_w / 2, _h * 0.40, txt("oleada") + " " + string(global.oleada), 2.4, 2.4, 0);
    draw_text_transformed(_w / 2, _h * 0.48, txt("puntos") + ": " + string(global.puntos), 2.4, 2.4, 0);
    if (record_nuevo) {
        draw_set_colour(make_colour_rgb(250, 196, 84));
        draw_text_transformed(_w / 2, _h * 0.58, txt("nuevo_record"), 3, 3, 0);
    } else {
        draw_set_colour(make_colour_rgb(150, 166, 200));
        draw_text_transformed(_w / 2, _h * 0.58, txt("record") + ": " + string(global.record), 2, 2, 0);
    }
    draw_set_colour(make_colour_rgb(200, 214, 240));
    draw_text_transformed(_w / 2, _h * 0.74, txt("reintentar"), 2, 2, 0);
    draw_set_halign(fa_left);
}
draw_set_valign(fa_top);
