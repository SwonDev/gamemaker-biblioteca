# 54 · Metajuego transversal — logros, galería, speedrun y espectador

> Cuatro sistemas que no pertenecen a ningún género: un plataformas, un RPG y un *shoot 'em up*
> pueden llevar los cuatro sin cambiar una línea de su lógica de juego. Cada uno reutiliza algo
> que ya existe en la biblioteca en vez de reinventarlo — este documento es el pegamento, no una
> reescritura.
>
> **Qué NO cubre**: los logros de **plataforma** (Steam, Xbox) están en
> [`04 · 20` §1 y §6.3](./20%20-%20Servicios%20de%20plataforma%20%28logros%2C%20anuncios%2C%20compras%29.md);
> aquí solo el sistema **interno**, previo o alternativo a ellos. El guardado en sí — checksum,
> copias de seguridad, escritura segura — está en
> [`scr_save_load.gml`](<../06 - Assets y Scripts/scr_save_load.gml>); este documento lo reutiliza
> tal cual, no lo repite. Todo el netcode de salas, snapshots e interpolación está en
> [`04 · 14`](./14%20-%20Multijugador.md); aquí solo el rol nuevo de espectador sobre esa base. El
> *position-averaging*/*zoom-to-fit* de cámara está en
> [`13 · 19` §3.10](<../13 - Diseño y producción de videojuegos/19 - Cámaras de juego - encuadre, seguimiento y control.md>);
> aquí solo se filtra su entrada. El New Game+ y los *flags* planos ya están resueltos en
> [`04 · 40` §2.3/§3.3](./40%20-%20Tutorial%2C%20onboarding%20y%20prompts%20en%20pantalla.md); si tu
> metajuego debe sobrevivir a un NG+, esa es la sección que decide qué se conserva.

---

## 1 · Visión general

### 1.1 · Qué tienen en común estos cuatro sistemas

Ninguno de los cuatro toca la simulación del juego: un logro se desbloquea al recibir un evento
("mataste al jefe"), una entrada de galería se desbloquea igual, un split se marca al cruzar un
punto del nivel, un espectador ni siquiera simula — solo mira lo que otros simulan. Son
**transversales**: se enchufan por fuera, con una llamada desde el código de juego que ya tienes
(`logro_desbloquear(...)`, `galeria_desbloquear(...)`, `crono_marcar_split(...)`), sin exigir un
género concreto. Y comparten una misma decisión de diseño: **reutilizan la infraestructura que ya
existe** en vez de crear la suya — cada uno se apoya en un sistema distinto de la biblioteca, sin
tocarlo.

### 1.2 · Cómo se relacionan entre sí (y con qué no)

| Sistema | Depende de | No repite |
|---|---|---|
| (a) Logros internos | `save_game`/`load_game` | El checksum, el backup rotativo, la escritura segura — todo en `scr_save_load.gml` |
| (b) Galería | `global.flags`, `flag_leer`/`flag_poner` (13 · 12 §6.2) | El propio sistema de flags, ni el New Game+ (04 · 40 §2.3/§3.3) |
| (c) Splits/speedrun | `save_game`/`load_game`, `get_timer()` | El guardado; solo añade UN struct más dentro de los mismos datos |
| (d) Espectador | El protocolo, las salas y `objNetEntity` de 04 · 14 | El snapshot, la interpolación, el modelo de sala — se **usan**, no se rehacen |

Los cuatro son independientes entre sí — monta solo la galería, o solo el cronómetro, si es lo
que necesitas. El orden (a → b → c → d) va de menor a mayor dependencia de otro sistema: de
"solo necesitas el guardado" a "necesitas todo el netcode de `04 · 14` ya construido".

---

## 2 · Logros internos, desacoplados de plataforma

Un sistema de logros que funciona **sin Steam, sin Xbox, sin conexión y sin cuenta**: para un
juego que todavía no está publicado en una tienda con logros propios, o como capa que sigue
funcionando aunque el jugador tenga Steam desactivado (`04 · 20` §1 ya avisa: "el juego debe
funcionar igual sin Steam"). Es también la capa que, cuando publiques, sigue siendo tu fuente de
verdad interna mientras espeja hacia la plataforma real — ver la nota al final de esta sección.

### 2.1 · El catálogo: datos, no código repartido

Igual que el catálogo de pasos de tutorial en `04 · 40` §2.1, el catálogo de logros es una lista
de structs definida una vez, no una serie de `if` repartidos por el juego:

```gml
// ═══════════ scr_logros ═══════════
// Símbolos verificados: struct_exists, variable_global_exists, array_length,
// clamp, max, is_undefined, show_debug_message, is_struct, struct_exists,
// variable_struct_get_names (no usada aquí, ver §2.3), is_method

/// @func logro_definir(_id_logro, _nombre, _descripcion, _meta)
/// @desc Una entrada del catálogo. _meta == 1 -> logro booleano; _meta > 1 ->
///       incremental (progreso 0.._meta, p. ej. "mata 50 enemigos"). _id_logro
///       es la clave de guardado: estable, no la cambies una vez publicada.
/// @returns {Struct}
function logro_definir(_id_logro, _nombre, _descripcion, _meta = 1)
{
    return {
        id_logro    : _id_logro,
        nombre      : _nombre,
        descripcion : _descripcion,
        meta        : _meta
    };
}

// obj_control · Create — el catálogo se define UNA vez, al arrancar el juego.
global.logros_catalogo = [
    logro_definir("primera_victoria", "Primera victoria",  "Gana tu primera partida"),
    logro_definir("coleccionista",    "Coleccionista",     "Encuentra 10 objetos raros", 10),
    logro_definir("sin_danio",        "Intachable",        "Termina un nivel sin recibir daño")
];
```

### 2.2 · El progreso: un struct plano por logro

```gml
/// @func logros_inicializar()
/// @desc Crea global.logros_estado a partir del catálogo, todo en 0/false.
///       Llamarla UNA vez en partida nueva, como flags_iniciar() (13 · 12 §6.2).
function logros_inicializar()
{
    global.logros_estado = {};

    for (var _i = 0; _i < array_length(global.logros_catalogo); _i++)
    {
        var _l = global.logros_catalogo[_i];
        global.logros_estado[$ _l.id_logro] = { desbloqueado: false, progreso: 0 };
    }
}

/// @func logro_definicion_obtener(_id_logro)
/// @returns {Struct|Undefined}
function logro_definicion_obtener(_id_logro)
{
    for (var _i = 0; _i < array_length(global.logros_catalogo); _i++)
    {
        if (global.logros_catalogo[_i].id_logro == _id_logro) return global.logros_catalogo[_i];
    }
    return undefined;
}

/// @func logro_progreso_obtener(_id_logro)
/// @returns {Struct|Undefined}  { desbloqueado, progreso }, o undefined si no existe.
function logro_progreso_obtener(_id_logro)
{
    if (!variable_global_exists("logros_estado")) return undefined;
    if (!struct_exists(global.logros_estado, _id_logro)) return undefined;
    return global.logros_estado[$ _id_logro];
}
```

### 2.3 · Desbloquear y sumar progreso

```gml
/// @func logro_desbloquear(_id_logro)
/// @desc Desbloquea un logro booleano (o cierra uno incremental de golpe).
///       No hace nada si ya estaba desbloqueado: evita notificar dos veces.
/// @returns {Bool}  true si esta llamada lo desbloqueó de verdad.
function logro_desbloquear(_id_logro)
{
    var _estado = logro_progreso_obtener(_id_logro);
    if (is_undefined(_estado) || _estado.desbloqueado) return false;

    _estado.desbloqueado = true;

    var _def = logro_definicion_obtener(_id_logro);
    if (!is_undefined(_def)) _estado.progreso = _def.meta;

    logro_notificar(_id_logro);
    return true;
}

/// @func logro_progreso_sumar(_id_logro, _cantidad)
/// @desc Para logros incrementales: suma progreso y desbloquea solo al llegar
///       a la meta. `_cantidad` negativa se recorta a 0 — esta función es
///       solo para sumar, no para restar progreso.
function logro_progreso_sumar(_id_logro, _cantidad)
{
    var _estado = logro_progreso_obtener(_id_logro);
    var _def    = logro_definicion_obtener(_id_logro);
    if (is_undefined(_estado) || is_undefined(_def) || _estado.desbloqueado) return;

    _estado.progreso = clamp(_estado.progreso + max(_cantidad, 0), 0, _def.meta);

    if (_estado.progreso >= _def.meta) logro_desbloquear(_id_logro);
}

/// @func logro_notificar(_id_logro)
/// @desc Aviso propio: Steam pinta el suyo con su overlay (`04 · 20` §1 —
///       `steam_set_achievement` no dibuja nada), esto es el tuyo, igual en
///       cualquier plataforma, con o sin Steam.
function logro_notificar(_id_logro)
{
    var _def = logro_definicion_obtener(_id_logro);
    if (is_undefined(_def)) return;

    show_debug_message("Logro desbloqueado: " + _def.nombre);

    // Opcional: si ya tienes las señales de 04 · 16 montadas (senales_init()
    // llamado al arrancar), un toast propio (13 · 05 §3.5i) en vez de un log.
    if (variable_global_exists("__senales"))
    {
        senal_emitir("logro_desbloqueado", { id_logro: _id_logro, nombre: _def.nombre });
    }
}
```

### 2.4 · Guardado: una línea dentro del `_datos` que ya tienes

La regla de esta sección: **no se reescribe nada de `scr_save_load.gml`**. El struct de logros
es un campo más dentro del mismo `_datos` que ya construyes para `save_game()` — igual que
`13 · 12` §6.2 mete `flags` dentro de ese mismo struct para guardar la partida narrativa.

```gml
/// @func logros_guardar(_slot)
/// @desc Ejemplo AISLADO para que sea copiable. En tu juego, "logros:
///       global.logros_estado" va DENTRO del struct grande que ya construyes
///       con el nivel, la vida, el inventario... — una llamada por partida.
function logros_guardar(_slot)
{
    return save_game(_slot, {
        logros: global.logros_estado
        // ...el resto de tu partida va aquí, junto a esto.
    });
}

/// @func logros_cargar(_slot)
function logros_cargar(_slot)
{
    var _datos = load_game(_slot);   // scr_save_load.gml — checksum y validación ya resueltos ahí

    if (!is_struct(_datos) || !struct_exists(_datos, "logros"))
    {
        logros_inicializar();        // partida sin logros previos (o de un formato viejo): arranca en 0
        return;
    }

    global.logros_estado = _datos.logros;
}
```

> 💡 **Cuando publiques en una tienda con logros propios, este sistema no desaparece.** Sigue
> siendo tu fuente de verdad interna — funciona sin conexión, sin cuenta y en cualquier
> plataforma — y en el mismo punto donde llamas a `logro_desbloquear()` añades una línea más que
> espeja hacia la plataforma real: `steam_set_achievement()` de `04 · 20` §1 (mapeando tu
> `id_logro` interno al *API name* de Steam) o el bloque de logros de Xbox de `04 · 20` §6.3. Ese
> código de plataforma no se repite aquí: está en `04 · 20`.

---

## 3 · Galería reutilizable: CG, arte y música

`04 · 10` §8 (*Cómo escalarlo*) ya apunta la idea en dos líneas — "Galería de CG y música —
desbloquea imágenes al verlas" — sin desarrollarla; es solo una sugerencia de ampliación, no un
sistema. Esta sección la construye, y de forma que sirva para **cualquier** género, no solo para
una *visual novel*: una galería de bocetos en un metroidvania, de música en cualquier juego con
banda sonora original, de CG en cualquier historia con arte dedicado.

### 3.1 · El catálogo y el desbloqueo: los mismos *flags* que el tutorial

Este documento asume `global.flags` / `flag_leer()` / `flag_poner()` de
[`13 · 12` §6.2](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md#62-los-flags-un-struct-global-plano-y-guardable>) —
el **mismo** sistema que ya reutiliza `04 · 40` §3.3 para `tutorial_visto_*`. Si tu juego no
lleva sistema narrativo, esas ~20 líneas son independientes: cópialas de `13 · 12` §6.2 tal cual,
no hace falta el resto del guion. El namespace de esta sección sigue el mismo espíritu de prefijo
que `tutorial_visto_*`: **`galeria_desbloqueada_<id_entrada>`**.

```gml
// ═══════════ scr_galeria ═══════════
// Símbolos verificados: array_length, array_push, point_in_rectangle,
// draw_sprite_ext, draw_circle_color, draw_roundrect_color_ext, draw_set_alpha,
// draw_set_halign, draw_set_valign, fa_left, fa_top, mouse_x, mouse_y,
// mouse_check_button_pressed, mb_left, audio_play_sound, c_white, c_black

/// @func galeria_entrada_definir(_id_entrada, _tipo, _titulo, _spr_miniatura, _spr_completo, _snd_pista)
/// @desc _tipo: "cg" | "musica" | "arte". _spr_completo/-1 = sin imagen ampliada
///       (música sin CG propia); _snd_pista/-1 = sin audio asociado (cg/arte).
function galeria_entrada_definir(_id_entrada, _tipo, _titulo, _spr_miniatura, _spr_completo = -1, _snd_pista = -1)
{
    return {
        id_entrada    : _id_entrada,
        tipo          : _tipo,
        titulo        : _titulo,
        spr_miniatura : _spr_miniatura,
        spr_completo  : _spr_completo,
        snd_pista     : _snd_pista
    };
}

// obj_control · Create — el catálogo, una vez. Los sprites/sonidos son
// ejemplos: créalos en tu proyecto con esos nombres, o cambia los nombres.
global.galeria_catalogo = [
    galeria_entrada_definir("cg_final_bueno",       "cg",     "Un nuevo amanecer",        spr_cg_final_bueno_mini, spr_cg_final_bueno),
    galeria_entrada_definir("arte_boceto_prota",    "arte",   "Boceto: la protagonista",  spr_arte_boceto_prota_mini, spr_arte_boceto_prota),
    galeria_entrada_definir("musica_tema_principal","musica", "Tema principal",           spr_galeria_icono_musica, -1, mus_tema_principal)
];

/// @func galeria_desbloquear(_id_entrada)
function galeria_desbloquear(_id_entrada)
{
    flag_poner("galeria_desbloqueada_" + _id_entrada, true);
}

/// @func galeria_esta_desbloqueada(_id_entrada)
/// @returns {Bool}
function galeria_esta_desbloqueada(_id_entrada)
{
    return flag_leer("galeria_desbloqueada_" + _id_entrada, false);
}
```

Desbloquear una entrada es entonces una sola línea desde donde corresponda en tu juego —
`galeria_desbloquear("cg_final_bueno")` al terminar la historia, `galeria_desbloquear("arte_boceto_prota")`
al derrotar a un jefe — sin tocar nada de esta sección.

### 3.2 · El grid: miniaturas, candado o silueta

```gml
/// obj_galeria — Create
galeria_columnas  = 4;
galeria_celda_w   = 96;
galeria_celda_h   = 72;
galeria_margen    = 16;
galeria_origen_x  = 32;
galeria_origen_y  = 48;
galeria_seleccion = -1;   // índice de la entrada ampliada en el catálogo; -1 = ninguna
```

```gml
/// obj_galeria — Draw
draw_set_halign(fa_left);
draw_set_valign(fa_top);

for (var _i = 0; _i < array_length(global.galeria_catalogo); _i++)
{
    var _entrada = global.galeria_catalogo[_i];
    var _col  = _i mod galeria_columnas;
    var _fila = _i div galeria_columnas;

    var _cx = galeria_origen_x + _col  * (galeria_celda_w + galeria_margen);
    var _cy = galeria_origen_y + _fila * (galeria_celda_h + galeria_margen);

    if (galeria_esta_desbloqueada(_entrada.id_entrada))
    {
        draw_sprite_ext(_entrada.spr_miniatura, 0, _cx, _cy, 1, 1, 0, c_white, 1);
    }
    else
    {
        // Silueta: la misma miniatura, tintada de negro y semitransparente,
        // insinúa la forma sin enseñar el contenido — más el candado encima.
        draw_sprite_ext(_entrada.spr_miniatura, 0, _cx, _cy, 1, 1, 0, c_black, 0.6);
        galeria_dibujar_candado(_cx + galeria_celda_w / 2, _cy + galeria_celda_h / 2);
    }
}

if (galeria_seleccion != -1) galeria_dibujar_ampliada(global.galeria_catalogo[galeria_seleccion]);

/// @func galeria_dibujar_candado(_cx, _cy)
/// @desc Candado a mano, sin sprite propio: un círculo hueco (el grillete)
///       tapado a medias por un rectángulo redondeado (el cuerpo), dibujado
///       ENCIMA. Con arte de candado propio, sustituye el cuerpo por un
///       draw_sprite_ext() y el resto de la sección no cambia.
function galeria_dibujar_candado(_cx, _cy)
{
    draw_set_alpha(0.9);

    draw_circle_color(_cx, _cy - 6, 7, c_white, c_white, true);
    draw_roundrect_color_ext(_cx - 9, _cy - 2, _cx + 9, _cy + 12, 3, 3, c_white, c_white, false);

    draw_set_alpha(1);
}
```

### 3.3 · Vista ampliada al seleccionar una entrada desbloqueada

```gml
/// obj_galeria — Step
if (mouse_check_button_pressed(mb_left))
{
    var _indice = galeria_indice_bajo_raton(mouse_x, mouse_y);

    if (_indice != -1 && galeria_esta_desbloqueada(global.galeria_catalogo[_indice].id_entrada))
    {
        galeria_seleccion = _indice;

        var _snd = global.galeria_catalogo[_indice].snd_pista;
        if (_snd != -1) audio_play_sound(_snd, 5, false);
    }
    else if (galeria_seleccion != -1)
    {
        galeria_seleccion = -1;   // clic fuera de una miniatura desbloqueada: cerrar la vista ampliada
    }
}
```

```gml
/// @func galeria_indice_bajo_raton(_mx, _my)
/// @returns {Real}  Índice en el catálogo bajo esas coordenadas, o -1.
function galeria_indice_bajo_raton(_mx, _my)
{
    for (var _i = 0; _i < array_length(global.galeria_catalogo); _i++)
    {
        var _col  = _i mod galeria_columnas;
        var _fila = _i div galeria_columnas;
        var _cx = galeria_origen_x + _col  * (galeria_celda_w + galeria_margen);
        var _cy = galeria_origen_y + _fila * (galeria_celda_h + galeria_margen);

        if (point_in_rectangle(_mx, _my, _cx, _cy, _cx + galeria_celda_w, _cy + galeria_celda_h))
        {
            return _i;
        }
    }
    return -1;
}

/// @func galeria_dibujar_ampliada(_entrada)
/// @desc Panel a pantalla completa con el sprite grande. Si la entrada es de
///       tipo "musica" sin spr_completo (-1), pinta el icono genérico en su
///       lugar: la música ya se oye, la imagen es solo contexto.
function galeria_dibujar_ampliada(_entrada)
{
    draw_set_alpha(0.85);
    draw_rectangle_color(0, 0, room_width, room_height, c_black, c_black, c_black, c_black, false);
    draw_set_alpha(1);

    var _spr = (_entrada.spr_completo != -1) ? _entrada.spr_completo : _entrada.spr_miniatura;
    draw_sprite_ext(_spr, 0, room_width / 2, room_height / 2, 1, 1, 0, c_white, 1);

    draw_set_halign(fa_center);
    draw_text_color(room_width / 2, room_height - 32, _entrada.titulo, c_white, c_white, c_white, c_white, 1);
    draw_set_halign(fa_left);
}
```

`room_width`/`room_height` centran el panel sobre la room actual; si tu galería vive en su propia
room dedicada (lo habitual), esos valores ya son los correctos sin tocar nada más.

---

## 4 · Cronómetro de splits comparado con un PB (speedrun)

Un cronómetro con marcas de segmento — *checkpoints* del nivel, cada uno con su propio tiempo
parcial — y comparación contra el mejor tiempo guardado (*Personal Best*), al estilo de
[LiveSplit](https://livesplit.org/) (abierta en vivo el 2026-09-07): *"you are able to
dynamically switch between multiple comparisons (...) compare your run to comparisons that you
define yourself or (...) your Sum of Best Segments"* — la idea de comparar un segmento en curso
contra una referencia guardada es exactamente la de esta sección, con una diferencia que se
explica en §4.3.

### 4.1 · `get_timer()` frente a `current_time`: por qué este documento usa el primero

Ambos verificados: `current_time` (manual, es) devuelve **"el número de milisegundos que han
pasado desde que se inició el juego"**; `get_timer()` devuelve **"el tiempo que tu juego ha
estado funcionando (...) en microsegundos"** — mil veces más fino. En un cronómetro de *splits*
esa resolución importa: en un segmento de pocos segundos, `current_time` ya redondea a la décima
de segundo perceptible; `get_timer()` no. La conversión a `ms` para mostrarlo es la única vez que
se pierde esa precisión, al final de cada cálculo — por eso esta sección usa `get_timer()` como
fuente y solo formatea a milisegundos al dibujar.

### 4.2 · El cronómetro: iniciar, pausar, marcar

```gml
// ═══════════ scr_speedrun ═══════════
// Símbolos verificados: get_timer, array_push, array_length, variable_global_exists,
// struct_exists, is_struct, is_undefined, floor, abs, string, string_length,
// string_format, clamp

#macro CRONO_SLOT_PB "pb_"   // + id de nivel: un PB independiente por nivel/categoría

/// @func crono_iniciar()
/// @desc Arranca el cronómetro desde cero. Llamarla al entrar en la sala que
///       se está cronometrando, cuando el jugador ya tiene el control.
function crono_iniciar()
{
    global.crono_activo             = true;
    global.crono_inicio_us          = get_timer();
    global.crono_pausado_desde_us   = -1;
    global.crono_pausa_acumulada_us = 0;
    global.crono_splits             = [];   // [{ nombre, tiempo_ms }], en orden de captura
}

/// @func crono_pausar()
/// @desc Detiene el reloj sin perder lo acumulado. Llamarla al abrir el menú
///       de pausa (04 · 41) si tu categoría de carrera cuenta tiempo de
///       partida y no tiempo real de reloj de pared.
function crono_pausar()
{
    if (!global.crono_activo || global.crono_pausado_desde_us != -1) return;
    global.crono_pausado_desde_us = get_timer();
}

/// @func crono_reanudar()
function crono_reanudar()
{
    if (global.crono_pausado_desde_us == -1) return;
    global.crono_pausa_acumulada_us += get_timer() - global.crono_pausado_desde_us;
    global.crono_pausado_desde_us = -1;
}

/// @func crono_tiempo_transcurrido_ms()
/// @returns {Real}  Milisegundos de carrera reales, sin contar el tiempo en pausa.
function crono_tiempo_transcurrido_ms()
{
    if (!global.crono_activo) return 0;

    var _hasta_us = (global.crono_pausado_desde_us != -1) ? global.crono_pausado_desde_us : get_timer();
    var _transcurrido_us = (_hasta_us - global.crono_inicio_us) - global.crono_pausa_acumulada_us;

    return _transcurrido_us / 1000;
}

/// @func crono_marcar_split(_nombre_split)
/// @desc Registra el tiempo acumulado en este checkpoint. Llamarla desde el
///       trigger del checkpoint del nivel (su propio Collision, o la señal
///       que ya use tu progreso de nivel).
/// @param {String} _nombre_split
/// @returns {Real|Undefined}  Delta en ms contra el PB en ESTE split (negativo
///                            = vas por delante). undefined si no hay PB.
function crono_marcar_split(_nombre_split)
{
    var _tiempo_ms = crono_tiempo_transcurrido_ms();
    array_push(global.crono_splits, { nombre: _nombre_split, tiempo_ms: _tiempo_ms });

    var _indice = array_length(global.crono_splits) - 1;
    if (!variable_global_exists("crono_pb") || is_undefined(global.crono_pb)) return undefined;
    if (_indice >= array_length(global.crono_pb.splits)) return undefined;

    return _tiempo_ms - global.crono_pb.splits[_indice].tiempo_ms;
}
```

### 4.3 · La comparación en vivo, y por qué es más conservadora que LiveSplit

Para un split **ya cerrado** el delta es exacto: `mi_tiempo - tiempo_del_pb_en_ese_split`. Pero
mientras el jugador está **dentro** de un segmento —antes del siguiente checkpoint— no hay forma
de saber si acabará por delante o por detrás sin inventar un supuesto sobre su ritmo. Este
documento no lo inventa: solo afirma lo único que SÍ puede afirmar con certeza en cualquier
instante — que ya se ha gastado, en este tramo, más tiempo del que el PB entero tardó en
completarlo:

```gml
/// @func crono_segmento_en_curso_va_por_detras()
/// @desc Indicador EN VIVO para el segmento sin cerrar: solo puede confirmar
///       "por detrás" (ya se gastó más tiempo en este tramo que el PB
///       completo), nunca "por delante" con la misma certeza — podrías
///       seguir gastando tiempo y perder el tramo igual antes de cerrarlo.
///       ⚠️ No es el algoritmo de LiveSplit (que combina varias comparaciones
///       — Sum of Best, Balanced PB — con datos que este documento no tiene
///       verificados); es la versión honesta y simple: solo avisa cuando el
///       "por detrás" es un hecho, no una proyección.
/// @returns {Bool}
function crono_segmento_en_curso_va_por_detras()
{
    if (!variable_global_exists("crono_pb") || is_undefined(global.crono_pb)) return false;

    var _indice = array_length(global.crono_splits);   // el segmento que se corre AHORA MISMO
    if (_indice >= array_length(global.crono_pb.splits)) return false;

    var _mi_split_anterior = (_indice == 0) ? 0 : global.crono_splits[_indice - 1].tiempo_ms;
    var _pb_split_anterior = (_indice == 0) ? 0 : global.crono_pb.splits[_indice - 1].tiempo_ms;
    var _pb_duracion_segmento = global.crono_pb.splits[_indice].tiempo_ms - _pb_split_anterior;

    var _mi_duracion_segmento_hasta_ahora = crono_tiempo_transcurrido_ms() - _mi_split_anterior;

    return (_mi_duracion_segmento_hasta_ahora > _pb_duracion_segmento);
}
```

### 4.4 · Guardar y cargar el PB — reutilizando `scr_save_load.gml`

```gml
/// @func crono_cargar_pb(_id_nivel)
/// @desc Llamarla al entrar en el nivel, ANTES de crono_iniciar(), para tener
///       algo contra lo que comparar en vivo.
function crono_cargar_pb(_id_nivel)
{
    var _datos = load_game(CRONO_SLOT_PB + _id_nivel);
    global.crono_pb = (is_struct(_datos) && struct_exists(_datos, "crono_pb")) ? _datos.crono_pb : undefined;
}

/// @func crono_finalizar_y_guardar_pb(_id_nivel)
/// @desc Llamarla al cruzar la meta. Sobrescribe el PB SOLO si mejora (o si
///       todavía no había ninguno) — nunca guarda una marca peor encima.
/// @returns {Bool}  true si esta carrera dejó un PB nuevo.
function crono_finalizar_y_guardar_pb(_id_nivel)
{
    global.crono_activo = false;
    var _tiempo_total_ms = crono_tiempo_transcurrido_ms();

    var _pb_previo = variable_global_exists("crono_pb") ? global.crono_pb : undefined;
    var _mejora = is_undefined(_pb_previo) || (_tiempo_total_ms < _pb_previo.tiempo_total_ms);
    if (!_mejora) return false;

    global.crono_pb = { tiempo_total_ms: _tiempo_total_ms, splits: global.crono_splits };

    // Aislado aquí para que el ejemplo sea copiable — en tu juego, mete
    // "crono_pb: global.crono_pb" en el MISMO _datos de tu guardado normal,
    // igual que logros_guardar() en la §2.4.
    save_game(CRONO_SLOT_PB + _id_nivel, { crono_pb: global.crono_pb });
    return true;
}
```

### 4.5 · Dibujar la lista de splits, con el delta de cada uno

```gml
/// @func crono_rellenar_ceros(_valor, _digitos)
/// @desc string_format() (verificado) rellena el hueco con ESPACIOS, no con
///       ceros — no sirve para pintar "05" en un reloj. Este helper sí.
function crono_rellenar_ceros(_valor, _digitos)
{
    var _texto = string(floor(_valor));
    while (string_length(_texto) < _digitos)
    {
        _texto = "0" + _texto;
    }
    return _texto;
}

/// @func crono_formatear_ms(_ms)
/// @returns {String}  "m:ss.mmm"
function crono_formatear_ms(_ms)
{
    var _total_seg = floor(_ms / 1000);
    var _minutos   = floor(_total_seg / 60);
    var _segundos  = _total_seg mod 60;
    var _milis     = floor(_ms mod 1000);

    return string(_minutos) + ":" + crono_rellenar_ceros(_segundos, 2) + "." + crono_rellenar_ceros(_milis, 3);
}

/// @func crono_formatear_delta_ms(_delta_ms)
/// @returns {String}  "-1.234" (por delante) o "+0.842" (por detrás)
function crono_formatear_delta_ms(_delta_ms)
{
    var _signo = (_delta_ms <= 0) ? "-" : "+";
    return _signo + string_format(abs(_delta_ms) / 1000, 1, 3);   // string_format SÍ rellena de ceros los decimales
}

/// @func crono_dibujar_splits(_x, _y)
/// @desc Reloj principal + un renglón por split ya cerrado (verde = por
///       delante, rojo = por detrás) + el indicador del segmento en curso.
function crono_dibujar_splits(_x, _y)
{
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);

    draw_text_color(_x, _y, crono_formatear_ms(crono_tiempo_transcurrido_ms()), c_white, c_white, c_white, c_white, 1);

    var _fila_y = _y + 24;
    for (var _i = 0; _i < array_length(global.crono_splits); _i++)
    {
        var _split = global.crono_splits[_i];
        var _delta_ms = undefined;

        if (variable_global_exists("crono_pb") && !is_undefined(global.crono_pb)
            && _i < array_length(global.crono_pb.splits))
        {
            _delta_ms = _split.tiempo_ms - global.crono_pb.splits[_i].tiempo_ms;
        }

        var _color = is_undefined(_delta_ms) ? c_white : (_delta_ms <= 0 ? c_lime : c_red);
        var _texto_delta = is_undefined(_delta_ms) ? "" : crono_formatear_delta_ms(_delta_ms);

        draw_text_color(_x, _fila_y,
            _split.nombre + "  " + crono_formatear_ms(_split.tiempo_ms) + "  " + _texto_delta,
            _color, _color, _color, _color, 1);

        _fila_y += 16;
    }

    if (global.crono_activo && variable_global_exists("crono_pb") && !is_undefined(global.crono_pb)
        && array_length(global.crono_splits) < array_length(global.crono_pb.splits))
    {
        var _color_en_curso = crono_segmento_en_curso_va_por_detras() ? c_red : c_ltgray;
        draw_text_color(_x, _fila_y, "(en curso)", _color_en_curso, _color_en_curso, _color_en_curso, _color_en_curso, 1);
    }
}
```

---

## 5 · Modo espectador

Sobre la base de red de `04 · 14`: `§10.1` (el modelo de sala —
`SalaMultijugador`/`sala_crear`/`sala_listar`/`sala_unirse`), `§5.5` (`recibir_snapshot()`) y
`§5.6` (la interpolación de `objNetEntity`) no se repiten aquí, se reutilizan enteros. Lo único
que falta —comprobado: ni "espectador" ni "spectator" aparecen en ese documento— es un rol de
cliente que **nunca envía input**, solo recibe *snapshots* e interpola exactamente como ya hace
`objNetEntity` para el resto de entidades remotas.

### 5.1 · Un valor nuevo en el protocolo, no un protocolo nuevo

El `enum NetMsg` de `04 · 14` §5.0 ya se amplió una vez en §10.1 con los mensajes de sala (hasta
`room_kicked = 65`). Se amplía otra vez aquí, con el mismo criterio que dice esa sección — "los
números de mensaje comparten un solo espacio", así que es el mismo enum, no uno nuevo: GameMaker
no permite declarar `enum NetMsg` una tercera vez, así que este bloque **reemplaza** al de
`04 · 14` §10.1, no lo añade:

```gml
// enum NetMsg completo — REEMPLAZA al de 04 · 14 §10.1, no lo declares dos veces.
enum NetMsg
{
    // --- de 04 · 14 §5.0 -----------------------------------------------------
    ping            = 1,
    pong            = 2,
    client_input    = 10,
    server_snapshot = 20,
    spawn_entity    = 30,
    kill_entity     = 31,
    chat            = 40,
    client_hello    = 50,
    server_welcome  = 51,
    // --- de 04 · 14 §10.1: gestión de salas -----------------------------------
    room_create        = 60,
    room_list_request  = 61,
    room_list          = 62,
    room_join          = 63,
    room_join_denied   = 64,
    room_kicked        = 65,
    // --- nuevo aquí ------------------------------------------------------------
    spectator_join = 66   // cliente -> servidor: quiero VER la sala, no jugar en ella
}
```

```gml
/// @func net_unirse_como_espectador(_id_sala)
/// @desc Como sala_unirse() (04 · 14 §10.1), pero por red y marcando el rol.
///       A partir de esta llamada, este cliente NO debe llamar nunca a
///       cliente_enviar_input() (04 · 14 §5.3) — ver §5.3 más abajo para la
///       comprobación del lado servidor, que no se fía de que el cliente lo
///       respete.
function net_unirse_como_espectador(_id_sala)
{
    var _b = net_buffer_nuevo(NetMsg.spectator_join);
    buffer_write(_b, buffer_u32, real(_id_sala));
    net_enviar(objNetManager.socket, _b);

    objNetManager.rol = "espectador";   // valor nuevo de "rol", junto a "servidor"/"cliente"/"ninguno" (04 · 14 §5.1)
}
```

### 5.2 · El servidor no crea entidad de jugador para un espectador

El manejador de `network_type_connect` de `04 · 14` §5.4 ya crea un struct de cliente por socket
conectado. Se amplía con un campo más — no se sustituye:

```gml
// En objNetManager — Async: Networking, case network_type_connect (04 · 14 §5.4):
// el mismo struct que ya se crea ahí, con un campo más.
clientes[$ string(_sock)] = {
    id               : _nuevo_id,
    ip               : _ip,
    ultimo_input_sec : 0,
    es_espectador    : false   // se pone a true al recibir spectator_join, abajo
};
```

Dos *case* nuevos en el mismo `switch (_msg)` del servidor, dentro de `network_type_data`
(`04 · 14` §5.4): el que marca a un cliente como espectador, y el que faltaba en ese `switch`
para procesar `client_input` — es el punto exacto donde hay que rechazar el input si un
espectador lo manda por error.

```gml
// Dos case nuevos en el switch (_msg) del servidor, dentro de network_type_data
// (04 · 14 §5.4). Ambos necesitan saber QUIÉN envió el paquete: en un evento de
// datos disparado en un socket de SERVIDOR, async_load[? "id"] es el socket del
// CLIENTE que mandó los datos (verificado: manual oficial, Eventos Asíncronos →
// Red → "Recepción de datos").

case NetMsg.spectator_join:
    var _id_sala_pedida = buffer_read(_buffer, buffer_u32);
    var _sock_origen    = async_load[? "id"];

    if (variable_struct_exists(clientes, string(_sock_origen)))
    {
        clientes[$ string(_sock_origen)].es_espectador = true;
    }

    // A propósito, NO se llama a sala_unirse() (04 · 14 §10.1): un espectador
    // no ocupa hueco de jugador, no cuenta para max_jugadores ni para
    // todos_listos() (04 · 14 §6). Basta con que su socket esté en
    // "clientes": servidor_enviar_snapshot() (§5.2) ya manda el snapshot a
    // TODOS los sockets registrados por igual, jueguen o miren.
    break;

case NetMsg.client_input:
    var _sock_origen = async_load[? "id"];
    var _cliente = variable_struct_exists(clientes, string(_sock_origen))
        ? clientes[$ string(_sock_origen)] : undefined;

    if (is_undefined(_cliente) || _cliente.es_espectador)
    {
        // Defensa en profundidad: el cliente espectador de §5.1 no debería
        // enviar client_input nunca, pero el servidor no puede fiarse de
        // eso — 04 · 14 §2.2, "nunca confíes en el cliente".
        break;
    }

    var _sec      = buffer_read(_buffer, buffer_u32);
    var _ix       = buffer_read(_buffer, buffer_s8);
    var _iy       = buffer_read(_buffer, buffer_s8);
    var _disparo  = buffer_read(_buffer, buffer_bool);
    // Aplicar (_sec, _ix, _iy, _disparo) al jugador de _cliente.id ya es
    // simulación de juego concreta, no red: no es parte de este documento.
    break;
```

### 5.3 · La cámara del espectador: sigue a un jugador, o al grupo

El espectador no tiene una instancia "propia" que la cámara pueda perseguir — todo lo que ve
llega por red y ya vive en `objNetEntity` (`04 · 14` §5.6). Dos modos, uno simple y uno que
reutiliza el *position-averaging*/*zoom-to-fit* de
[`13 · 19` §3.10](<../13 - Diseño y producción de videojuegos/19 - Cámaras de juego - encuadre, seguimiento y control.md#310-cámara-multijugador-con-zoom-dinámico>):

```gml
#macro TIPO_ENTIDAD_JUGADOR 1   // el valor de tipo_entidad (04 · 14 §5.5) que tu
                                // juego usa para personajes controlables: ese
                                // campo es un u8 genérico "para spawnear", el
                                // significado de cada número lo decide tu juego.

/// obj_camara_espectador — Create
espectador_modo        = "seguir";   // "seguir" | "libre" | "grupo"
espectador_objetivo_id = -1;         // net_id del jugador seguido en modo "seguir"

/// @func espectador_listar_jugadores()
/// @desc Instancias de objNetEntity (04 · 14 §5.6) que son JUGADORES, no
///       decorado sincronizado — filtradas por TIPO_ENTIDAD_JUGADOR.
/// @returns {Array<Id.Instance>}
function espectador_listar_jugadores()
{
    var _lista = [];
    with (objNetEntity)
    {
        if (tipo_entidad == TIPO_ENTIDAD_JUGADOR) array_push(_lista, id);
    }
    return _lista;
}

/// @func espectador_grupo_bbox()
/// @desc Igual que camara_grupo_bbox() de 13 · 19 §3.10, pero sobre
///       objNetEntity filtrado en vez de sobre un único obj_jugador local —
///       en un espectador no hay instancias propias, todo llega por red.
/// @returns {Struct|Undefined}  { izq, der, arr, aba, cx, cy }, o undefined si no hay nadie.
function espectador_grupo_bbox()
{
    var _jugadores = espectador_listar_jugadores();
    if (array_length(_jugadores) == 0) return undefined;

    var _izq = infinity, _der = -infinity, _arr = infinity, _aba = -infinity;

    for (var _i = 0; _i < array_length(_jugadores); _i++)
    {
        var _j = _jugadores[_i];
        _izq = min(_izq, _j.x);
        _der = max(_der, _j.x);
        _arr = min(_arr, _j.y);
        _aba = max(_aba, _j.y);
    }

    return { izq: _izq, der: _der, arr: _arr, aba: _aba, cx: (_izq + _der) / 2, cy: (_arr + _aba) / 2 };
}

/// obj_camara_espectador — Step
switch (espectador_modo)
{
    case "libre":
        // Cámara libre: paneo manual con teclado, sin física de personaje.
        x += (keyboard_check(vk_right) - keyboard_check(vk_left)) * 8;
        y += (keyboard_check(vk_down)  - keyboard_check(vk_up))   * 8;
        break;

    case "seguir":
        var _jugadores = espectador_listar_jugadores();

        if (keyboard_check_pressed(vk_tab) && array_length(_jugadores) > 0)
        {
            var _indice_actual = 0;
            for (var _i = 0; _i < array_length(_jugadores); _i++)
            {
                if (_jugadores[_i].net_id == espectador_objetivo_id) { _indice_actual = _i; break; }
            }
            espectador_objetivo_id = _jugadores[(_indice_actual + 1) mod array_length(_jugadores)].net_id;
        }

        var _objetivo = noone;
        for (var _i = 0; _i < array_length(_jugadores); _i++)
        {
            if (_jugadores[_i].net_id == espectador_objetivo_id) { _objetivo = _jugadores[_i]; break; }
        }
        if (_objetivo == noone && array_length(_jugadores) > 0)
        {
            _objetivo = _jugadores[0];
            espectador_objetivo_id = _objetivo.net_id;
        }

        if (_objetivo != noone)
        {
            x = lerp(x, _objetivo.x, 0.1);
            y = lerp(y, _objetivo.y, 0.1);
        }
        break;

    case "grupo":
        // El zoom-to-fit (zoom_actual, zoom_cuantizar…) es exactamente el de
        // 13 · 19 §3.10: solo cambia de dónde sale el bbox. No se repite aquí.
        var _bbox = espectador_grupo_bbox();
        if (!is_undefined(_bbox))
        {
            x = lerp(x, _bbox.cx, 0.08);
            y = lerp(y, _bbox.cy, 0.08);
        }
        break;
}

camera_set_view_pos(view_camera[0],
    x - camera_get_view_width(view_camera[0])  / 2,
    y - camera_get_view_height(view_camera[0]) / 2);
```

> 💡 **`vk_tab` cicla entre jugadores; el modo se cambia aparte** (un botón de UI, o `vk_1`/`vk_2`/`vk_3`
> para "seguir"/"libre"/"grupo") — no se incluye ese *binding* aquí porque `04 · 40` §3.5 ya
> resuelve la asignación real de controles y este documento no debe duplicarla.

---

## Checklist

- [ ] **Logros**: el catálogo (`global.logros_catalogo`) está definido una sola vez, en el
      arranque — no repartido en `if` por el código de juego.
- [ ] **Logros**: `logros_inicializar()` se llama en partida nueva; `logros_cargar()`, al cargar
      una existente. Ninguna partida arranca con `global.logros_estado` sin definir.
- [ ] **Logros**: el struct de logros va DENTRO del mismo `_datos` de `save_game()` que el resto
      de la partida — no hay una llamada a `save_game()` aparte solo para logros.
- [ ] **Logros**: si el juego se publica en una tienda, cada `logro_desbloquear()` interno tiene
      su espejo hacia `04 · 20` §1/§6.3 en el mismo punto de llamada.
- [ ] **Galería**: las claves de `global.flags` llevan el prefijo `galeria_desbloqueada_` — nunca
      se reutiliza el nombre de un flag de otro sistema (`tutorial_visto_*`, narrativos...).
- [ ] **Galería**: una entrada bloqueada nunca revela su sprite completo, ni por accidente al
      seleccionarla (`galeria_dibujar_ampliada` solo se llama sobre entradas desbloqueadas).
- [ ] **Speedrun**: `crono_cargar_pb()` se llama ANTES de `crono_iniciar()` — si se invierte el
      orden, la primera comparación en vivo del nivel sale vacía.
- [ ] **Speedrun**: `crono_finalizar_y_guardar_pb()` compara contra el PB anterior antes de
      sobrescribir — nunca se guarda una marca peor encima de una mejor.
- [ ] **Speedrun**: si el juego tiene menú de pausa, `crono_pausar()`/`crono_reanudar()` están
      conectados a él — si no, el tiempo en el menú cuenta como tiempo de carrera.
- [ ] **Espectador**: el servidor rechaza `client_input` de cualquier socket con
      `es_espectador == true`, no solo confía en que el cliente no lo mande.
- [ ] **Espectador**: `sala_unirse()` (`04 · 14` §10.1) nunca se llama para un espectador — no
      ocupa hueco de `max_jugadores` ni bloquea `todos_listos()`.
- [ ] **Espectador**: la cámara del espectador nunca lee input de movimiento del jugador local
      (no lo hay) — solo teclas propias de cámara (`vk_tab`, flechas en modo libre).

---

## Errores clásicos y cómo evitarlos

| Error | Consecuencia | Corrección |
|---|---|---|
| Llamar a `save_game()` una vez por sistema (logros, PB, partida...) | Varias escrituras a disco por evento, más lento y con más ventanas para un corte a medias | Un único `_datos` con todos los campos, una sola llamada a `save_game()` |
| Reescribir el checksum/backup de `scr_save_load.gml` "a medida" para los logros | Divergencia con el resto de la partida; dos formatos de guardado que mantener | Reutilizar `save_game`/`load_game` tal cual, como en §2.4 y §4.4 |
| Namespace de galería sin prefijo (`"cg_final_bueno"` en vez de `"galeria_desbloqueada_cg_final_bueno"`) | Colisión con un flag narrativo o de tutorial que use el mismo nombre corto | Prefijo `galeria_desbloqueada_` siempre, igual que `tutorial_visto_*` |
| Comparar el segmento en curso contra la duración total del PB del NIVEL, no la del SEGMENTO | El indicador en vivo casi nunca se pone en rojo hasta el final de la carrera | Comparar contra `pb.splits[i].tiempo_ms - pb.splits[i-1].tiempo_ms` (§4.3), no contra `pb.tiempo_total_ms` |
| Mostrar el delta en vivo como si fuera tan fiable como el de un split cerrado | El jugador confía en un "vas ganando" que puede revertirse al cerrar el split | Un color/símbolo distinto para "(en curso)" frente a un split ya cerrado (§4.5) |
| El servidor confía en que el cliente espectador no mande `client_input` | Un cliente modificado puede controlar una entidad ajena sin que el juego lo note | El `case NetMsg.client_input` del servidor comprueba `es_espectador` SIEMPRE (§5.2) |
| Meter al espectador en `sala_unirse()` para "que aparezca en la lista" | Ocupa un hueco de `max_jugadores`, y `todos_listos()` se queda esperando a alguien que nunca pulsará "listo" | El espectador se registra solo en `clientes`, nunca en `jugadores` (§5.2) |
| `crono_iniciar()` llamado después del primer input del jugador | El primer tramo del split 1 pierde unos frames — el PB de esa carrera arranca "regalado" | Llamarlo en el mismo evento que da el control al jugador, no un frame después |

---

## Ver también

- [04 · 20 — Servicios de plataforma](./20%20-%20Servicios%20de%20plataforma%20%28logros%2C%20anuncios%2C%20compras%29.md) —
  logros de Steam (§1) y de Xbox (§6.3): la capa de plataforma que este documento no repite
- [06 · scr_save_load.gml](<../06 - Assets y Scripts/scr_save_load.gml>) — `save_game()`/`load_game()`,
  reutilizados enteros en §2.4 y §4.4
- [04 · 40 §2.3 y §3.3 — Tutorial, onboarding y prompts en pantalla](./40%20-%20Tutorial%2C%20onboarding%20y%20prompts%20en%20pantalla.md#23-persistencia-y-qué-pasa-en-new-game)
  — qué le pasa a `global.flags` (y por tanto a la galería de §3) en un New Game+
- [13 · 12 §6.2 — Los flags narrativos](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md#62-los-flags-un-struct-global-plano-y-guardable>) —
  `flag_leer`/`flag_poner`, la base de §3.1
- [04 · 10 §8 — Visual Novel y narrativa](./10%20-%20Visual%20Novel%20y%20narrativa.md#8-cómo-escalarlo) —
  donde se apuntaba, sin desarrollar, la idea de galería que §3 construye
- [04 · 14 — Multijugador](./14%20-%20Multijugador.md) §5.4-§5.6 (snapshot, async, interpolación) y
  §10.1 (salas) — la base de red completa sobre la que se monta §5
- [13 · 19 §3.10 — Cámaras de juego](<../13 - Diseño y producción de videojuegos/19 - Cámaras de juego - encuadre, seguimiento y control.md#310-cámara-multijugador-con-zoom-dinámico>) —
  `camara_grupo_bbox()` y el zoom-to-fit que reutiliza el modo "grupo" de §5.3
- [04 · 16 — Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — para las
  notificaciones propias de logro (§2.3) y de split (opcional)
- [04 · 41 — Transiciones, carga y pausa](./41%20-%20Transiciones%2C%20carga%20y%20pausa.md) — dónde
  conectar `crono_pausar()`/`crono_reanudar()` (§4.2) al menú de pausa real

---

## Fuentes

Consultadas el **2026-09-07**.

- [livesplit.org](https://livesplit.org/) (abierta con `curl -A "Mozilla/5.0"`) — cita literal
  usada en §4: *"you are able to dynamically switch between multiple comparisons (...) compare
  your run to comparisons that you define yourself or compare it to multiple automatically
  generated comparisons, like your Sum of Best Segments"*. Confirma que comparar un segmento en
  curso contra una referencia guardada es la idea central de un cronómetro de *splits* — la base
  de §4.2-§4.3. ⚠️ El algoritmo EXACTO de la comparación en vivo de LiveSplit ("Sum of Best" /
  "Balanced PB") no está documentado en esa página ni se verificó en otra fuente primaria: §4.3
  no lo imita, implementa una versión propia, más simple y deliberadamente conservadora, y lo
  dice explícitamente en el código.
- Manual oficial de GameMaker (espejo local): [`get_timer`](<../09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Date_And_Time/get_timer.md>) y
  [`current_time`](<../09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Date_And_Time/current_time.md>) —
  citas de §4.1. [`string_format`](<../09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Strings/string_format.md>) —
  confirma el relleno con espacios (no ceros) que motiva `crono_rellenar_ceros()` en §4.5.
  [El evento Async → Red](<../09 - Manual oficial/manual-lts-2026-es/The_Asset_Editors/Object_Properties/Async_Events/Networking.md>) —
  confirma que `async_load[? "id"]` es el socket del cliente emisor en un evento de datos del
  servidor, la base de §5.2.
- `_indice/simbolos.json` (extraído del `GmlSpec.xml` del runtime GMS2 2026.0.0.23) — fuente de
  verdad para cada símbolo citado, consultado con `buscar.py <símbolo>` uno por uno antes de
  escribirlo.
- `scr_save_load.gml`, `04 · 14`, `04 · 40`, `13 · 12`, `13 · 19` — código y prosa propios de
  esta biblioteca, leídos enteros en las secciones citadas antes de escribir este documento, para
  no repetir ni una línea de lo que ya resuelven.
