// Evento Step del objeto de pruebas. Hace falta porque hay dos cosas que NO se
// pueden medir dentro de un solo evento:
//   · la desactivación de una instancia no surte efecto hasta el final del evento;
//   · `keyboard_key_press()` no llega a `keyboard_check_pressed()` hasta el paso
//     siguiente, así que el diálogo de confirmación se prueba frame a frame.
paso++;

if (paso == 1) banco_desactivadas_preparar();

if (paso == 4)
{
    banco_desactivadas_comprobar();
    banco_fuente();
    confirmar_prueba_abrir();
}
if (paso == 5) confirmar_prueba_cancelar();
if (paso == 6) confirmar_prueba_no_se_reabre();
if (paso == 7) confirmar_prueba_mover_foco();
if (paso == 8) confirmar_prueba_aceptar();

if (paso == 9)
{
    confirmar_prueba_cerrar();
    tween_prueba_lanzar();
    banco_camara_preparar();
    banco_audio_preparar();
}

// Los tweens avanzan con `delta_time`, así que hay que dejarles frames de verdad.
// 0,1 s a 60 fps son ~6 frames; se les dan 12 para que no dependa del ritmo exacto.
if (paso == 10) confirmar_prueba_lector_inyectado();
if (paso == 11) confirmar_prueba_lector_elige_si();
if (paso == 12) confirmar_prueba_lector_por_defecto();
if (paso == 13) confirmar_prueba_lector_limpiar();

if (paso >= 10) { tween_update(); audio_step(); }

if (paso == 22)
{
    tween_prueba_comprobar();
    banco_camara_comprobar();
    banco_audio_comprobar();

    show_debug_message("=========================================");
    show_debug_message("RESULTADO: " + string(global.ok) + " correctas, " + string(global.ko) + " fallidas");
    show_debug_message("=========================================");
    game_end();
}
