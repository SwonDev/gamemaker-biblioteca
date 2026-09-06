// ============================================================================
// scr_tiempo.gml
// Tres piezas de tiempo que se reescriben en cada receta: un `Cooldown` para
// habilidades con barra de recarga, un `Temporizador` independiente del
// framerate y un reloj de juego con escala de tiempo.
//
// POR QUÉ ESTE FICHERO
//   `delta_time` viene en MICROsegundos y no se pausa ni respeta un tiempo
//   bala; `alarm` cuenta en pasos, no en segundos; y cada receta de esta
//   biblioteca que necesita "cuánto falta" o "cada cuánto" vuelve a escribir
//   el mismo contador en segundos. Este script lo deja hecho una vez.
//
// CÓMO ENCAJAN LAS TRES PIEZAS
//   - `Reloj`         → UNO por juego. Calcula el delta de este frame, ya
//                       saneado (recorta picos) y multiplicado por
//                       `global.time_scale` si el proyecto lo usa. Todo lo
//                       demás se alimenta de su salida.
//   - `Cooldown`      → uno por HABILIDAD ("¿puedo disparar ya?", con una
//                       fracción 0..1 lista para pintar la barra de recarga).
//   - `Temporizador`  → uno por EVENTO periódico o retardado ("cada 30 s,
//                       genera una oleada"; "dentro de 2 s, abre la puerta"),
//                       con callback opcional y modo repetible.
//
// USO RÁPIDO
//   // objReloj (persistente, depth muy negativo: debe ir ANTES que nada
//   // que use su salida)
//   // Create:
//   reloj_iniciar();
//   // Begin Step:
//   reloj_actualizar();
//
//   // Create de obj_player — un Cooldown por habilidad
//   disparo_cd = new Cooldown(0.18);       // 180 ms entre disparos
//
//   // Step de obj_player
//   disparo_cd.actualizar(reloj_dt());     // respeta el tiempo bala
//   if (input_disparo && disparo_cd.usar()) { disparar(); }
//
//   // Draw GUI — barra de recarga
//   draw_rectangle(x, y, x + 64 * disparo_cd.fraccion(), y + 8, false);
//
//   // Create de obj_control — un Temporizador repetible con callback
//   oleada_timer = new Temporizador(30, true, function() { generar_oleada(); });
//
//   // Step de obj_control
//   oleada_timer.actualizar(reloj_dt());
//
// Funciones nativas usadas (verificadas con gm-cli manual read / buscar.py):
//   delta_time, variable_global_exists, is_undefined, is_method, max, min,
//   clamp
//
// Dependencias: ninguna. Funciona sin `global.time_scale`: si el proyecto no
// lo define, el reloj usa una escala de 1 (tiempo normal) por defecto.
//
// LO QUE ESTE SCRIPT NO CUBRE (y dónde está)
//   - Hit stop y tiempo bala en sí (subir/bajar `global.time_scale`, congelar
//     N frames): eso ya lo resuelve
//     "04 - Recetas por género/15 - Game feel y juice.md" §5.0. Este script
//     LEE esa variable si existe; no la sustituye ni la reimplementa.
//   - Pausar de verdad (time sources, alarmas, audio, partículas al pausar
//     el juego): fuera de alcance de un contador en segundos.
// ============================================================================


// ═══════════════════════════════ Reloj de juego ═════════════════════════════

/// @function reloj_iniciar()
/// @desc    Prepara el reloj global. Llámala UNA vez, desde el Create de un
///          objeto persistente con depth muy negativo (debe actualizarse
///          antes que cualquier cosa que lea su salida).
///          Si el proyecto ya define `global.time_scale` (ver 04·15 §5.0),
///          el reloj lo respeta desde el primer frame; si no, arranca en 1.
function reloj_iniciar()
{
    if (!variable_global_exists("time_scale")) { global.time_scale = 1.0; }

    global.reloj_dt      = 0;   // segundos de este frame, YA escalados
    global.reloj_dt_real = 0;   // segundos reales de este frame, sin escalar
    global.reloj_tiempo  = 0;   // segundos de juego acumulados (respeta la escala)
}

/// @function reloj_actualizar()
/// @desc    Calcula el delta de este frame. Llámala UNA vez por frame, lo
///          primero de todo (Begin Step), para que el resto del juego lea ya
///          el valor saneado.
///          `delta_time` mide tiempo REAL: no se pausa con un hit stop ni
///          respeta ninguna escala por sí solo, y puede dar un pico enorme
///          al minimizar la ventana o cargar un recurso. Por eso se recorta
///          a un máximo de 1/30 s antes de usarlo.
function reloj_actualizar()
{
    if (!variable_global_exists("reloj_dt")) { reloj_iniciar(); }

    global.reloj_dt_real = min(delta_time / 1000000, 1 / 30);

    var _escala = variable_global_exists("time_scale") ? global.time_scale : 1.0;
    global.reloj_dt = global.reloj_dt_real * _escala;

    global.reloj_tiempo += global.reloj_dt;
}

/// @function reloj_dt()
/// @desc    Segundos transcurridos este frame, saneados y multiplicados por
///          `global.time_scale`. Es el que hay que pasar a `Cooldown` y
///          `Temporizador` en el 99 % de los casos: en tiempo bala, las
///          recargas y los eventos periódicos también se ralentizan.
/// @returns {Real}
function reloj_dt()
{
    return variable_global_exists("reloj_dt") ? global.reloj_dt : 0;
}

/// @function reloj_dt_real()
/// @desc    Segundos transcurridos este frame, saneados pero SIN escalar.
///          Úsalo para lo que no debe frenarse en tiempo bala: la cuenta
///          atrás de un menú, un cronómetro de partida, la música.
/// @returns {Real}
function reloj_dt_real()
{
    return variable_global_exists("reloj_dt_real") ? global.reloj_dt_real : 0;
}

/// @function reloj_tiempo()
/// @desc    Segundos de juego acumulados desde `reloj_iniciar()`, respetando
///          la escala de tiempo (se congela si `time_scale` vale 0).
/// @returns {Real}
function reloj_tiempo()
{
    return variable_global_exists("reloj_tiempo") ? global.reloj_tiempo : 0;
}


// ═════════════════════════════════ Cooldown ═════════════════════════════════

/// @function Cooldown(_duracion)
/// @desc    Recarga de una habilidad: "¿está lista?", "gástala" y "cuánto le
///          falta para pintar la barra de recarga". Arranca YA lista.
/// @param   {Real} _duracion  Segundos que tarda en recargar tras usarse.
function Cooldown(_duracion) constructor
{
    duracion = max(_duracion, 0.0001);   // evita la división por cero en fraccion()
    restante = 0;                        // 0 = lista desde el primer frame

    /// @desc Gasta la recarga SI está lista. No hace nada si no lo está.
    /// @returns {Bool}  True si se ha podido usar (y por tanto ahora está
    ///                  recargando); false si todavía estaba recargando.
    static usar = function()
    {
        if (restante > 0) { return false; }
        restante = duracion;
        return true;
    };

    /// @desc Consulta sin gastar: ¿ya se puede volver a usar?
    /// @returns {Bool}
    static listo = function()
    {
        return (restante <= 0);
    };

    /// @desc Progreso de la recarga para pintar una barra de UI: 0 justo
    ///       después de usarla, 1 cuando ya está lista.
    /// @returns {Real}  Entre 0 y 1.
    static fraccion = function()
    {
        return clamp(1 - (restante / duracion), 0, 1);
    };

    /// @desc Descuenta tiempo de la recarga. Llámala una vez por frame,
    ///       pasándole `reloj_dt()` (o cualquier delta en segundos propio).
    /// @param {Real} _dt  Segundos transcurridos este frame.
    static actualizar = function(_dt)
    {
        if (restante > 0) { restante = max(0, restante - _dt); }
    };

    /// @desc Reinicia la recarga. Con `_duracion` cambia también el tiempo
    ///       de recarga (útil para mejoras que lo acortan a mitad de partida).
    /// @param {Real} [_duracion]  Nueva duración, si se quiere cambiar.
    static reiniciar = function(_duracion = undefined)
    {
        if (!is_undefined(_duracion)) { duracion = max(_duracion, 0.0001); }
        restante = 0;
    };
}


// ═══════════════════════════════ Temporizador ═══════════════════════════════

/// @function Temporizador(_duracion, [_repetir], [_callback])
/// @desc    Cuenta atrás independiente del framerate (la fórmula del
///          contador en segundos de "13/13" §12.3): sobrevive a los cambios
///          de velocidad del juego y se puede pausar por su cuenta. Para
///          eventos únicos ("dentro de 2 s") o periódicos ("cada 30 s").
/// @param   {Real}     _duracion   Segundos hasta que se cumple.
/// @param   {Bool}     [_repetir]  Si al cumplirse debe reiniciarse solo
///                                 (false por defecto: un solo disparo).
/// @param   {Function} [_callback] Función a llamar al cumplirse (opcional).
function Temporizador(_duracion, _repetir = false, _callback = undefined) constructor
{
    duracion = max(_duracion, 0.0001);
    repetir  = _repetir;
    callback = _callback;
    restante = duracion;
    pausado  = false;

    /// @desc Descuenta tiempo y, si se cumple, llama al callback (si hay) y
    ///       decide si se reinicia. Si `_dt` es mayor que `duracion` (una
    ///       bajada brusca de fps), como mucho se dispara UNA vez por
    ///       llamada: nunca varios ticks de golpe.
    /// @param {Real} _dt  Segundos transcurridos este frame.
    /// @returns {Bool}    True el frame exacto en que se cumple.
    static actualizar = function(_dt)
    {
        if (pausado) { return false; }

        restante -= _dt;
        if (restante > 0) { return false; }

        if (is_method(callback)) { callback(); }

        // Conserva el sobrante en vez de resetear a `duracion` a secas: así
        // un Temporizador repetible no acumula deriva con el paso del tiempo.
        restante = repetir ? (restante + duracion) : 0;
        return true;
    };

    /// @desc Para uno de un solo disparo: ¿ya se cumplió? (Un repetible
    ///       nunca "termina": siempre vuelve a contar.)
    /// @returns {Bool}
    static terminado = function()
    {
        return (!repetir && restante <= 0);
    };

    /// @desc Segundos que quedan hasta que se cumpla (nunca negativo).
    /// @returns {Real}
    static restante_segundos = function()
    {
        return max(0, restante);
    };

    /// @desc Progreso transcurrido para una barra de UI: 0 al empezar, 1 al
    ///       cumplirse.
    /// @returns {Real}  Entre 0 y 1.
    static fraccion = function()
    {
        return clamp(1 - (restante / duracion), 0, 1);
    };

    /// @desc Reinicia la cuenta. Con `_duracion` cambia también la duración.
    /// @param {Real} [_duracion]  Nueva duración, si se quiere cambiar.
    static reiniciar = function(_duracion = undefined)
    {
        if (!is_undefined(_duracion)) { duracion = max(_duracion, 0.0001); }
        restante = duracion;
        pausado  = false;
    };

    /// @desc Pausa la cuenta: `actualizar()` deja de descontar tiempo.
    static pausar = function()
    {
        pausado = true;
    };

    /// @desc Reanuda una cuenta pausada.
    static reanudar = function()
    {
        pausado = false;
    };

    /// @desc Consulta si está pausado.
    /// @returns {Bool}
    static esta_pausado = function()
    {
        return pausado;
    };
}
