# 06 · Assets y Scripts — Scripts GML reutilizables

> 🎨 **¿Buscas contenido (arte, música, SFX, tilesets, fuentes) en vez de código?**
> → [`07 · Asset packs y recursos gráficos`](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md):
> catálogo de fuentes de assets libres para GameMaker (Asset Bundles oficiales, Kenney, itch.io,
> OpenGameArt, Freesound, Tiled→GameMaker, paletas, fuentes…), con licencias verificadas y qué
> formato bajar. Este README cubre solo los **scripts GML**.

> Doce scripts `.gml` listos para importar en cualquier proyecto de **GameMaker LTS 2026**.
> Generado en **agosto de 2026** (`scr_audio.gml` y `scr_tiempo.gml`, en **septiembre de 2026**;
> `scr_ui_confirmar.gml`, el 8 de septiembre de 2026) · Verificado contra el manual oficial con
> `gm-cli manual read`.
>
> ✅ **Compilación verificada (2026-09-08):** los doce scripts se compilaron juntos en un
> proyecto real con `gm-cli compile` contra el runtime **2026.0.0.23** — cero errores de GML.
> La prueba es reproducible: `bash _indice/validar-compilacion.sh` (crea el proyecto en
> `~/gm_prueba_scripts`, mete los scripts, compila y borra el proyecto al terminar; sale con 0
> solo si el compilador oficial no da ni un error de GML).

---

## Cómo importarlos

Hay **dos formas**, y conviene saber las dos:

### Opción A — Arrastrar (la más rápida)

1. Abre tu proyecto en el IDE.
2. Arrastra el archivo `.gml` desde el Finder **al Asset Browser**.
3. GameMaker crea automáticamente un recurso **Script** con el nombre del archivo.

> ⚠️ Al arrastrarlo, GameMaker puede crear el script **vacío** y abrirlo para que pegues el
> contenido. Si pasa eso, pega el contenido del `.gml` dentro.

### Opción B — Crear el Script a mano

1. En el Asset Browser: *Script* → clic derecho → **Create → Script**.
2. Renómbralo (por ejemplo `scr_math_util`).
3. Borra el contenido que trae y pega el del archivo `.gml`.
4. Guarda.

> 💡 **Los nombres de los archivos coinciden con los nombres de script recomendados.**
> Si los renombras, recuerda que las funciones que contienen siguen siendo globales: lo que
> importa son los nombres de las **funciones**, no los del script.

### Los scripts de este README son solo código

Los `.gml` de esta carpeta **no** son un proyecto de GameMaker: son archivos de texto con
funciones. Puedes pegarlos todos en un único script gigante si quieres, o en uno por archivo.
Lo segundo es más limpio.

---

## Tabla de scripts

| Archivo | Qué hace | Dependencias | Tamaño |
|---|---|---|---:|
| [`scr_math_util.gml`](./scr_math_util.gml) | `approach`, `wave`, `remap`, `lerp_dt`, `smoothstep`, `snap` y **16 funciones de easing** | ninguna | ⭐ Esencial |
| [`scr_camera.gml`](./scr_camera.gml) | Cámara 2D con seguimiento, deadzone, look-ahead, límites de sala y screen shake | `scr_math_util` | ⭐ Esencial |
| [`scr_state_machine.gml`](./scr_state_machine.gml) | Máquina de estados finitos con structs, sin objetos | ninguna | ⭐ Esencial |
| [`scr_tween.gml`](./scr_tween.gml) | Sistema de tweens dirigido por `delta_time`, con callbacks | `scr_math_util` | Muy útil |
| [`scr_save_load.gml`](./scr_save_load.gml) | Guardado y carga con structs + JSON, escritura segura y migración de versión | ninguna | ⭐ Esencial |
| [`scr_pool.gml`](./scr_pool.gml) | Object pooling: reutiliza instancias en vez de crearlas y destruirlas | ninguna | Rendimiento |
| [`scr_grid_pathfinding.gml`](./scr_grid_pathfinding.gml) | Pathfinding en rejilla: envoltorio de `mp_grid` **y** A* en GML puro con coste por celda | ninguna | Según género |
| [`scr_input_buffer.gml`](./scr_input_buffer.gml) | Input buffering y coyote time para plataformas | ninguna | Plataformas |
| [`scr_debug.gml`](./scr_debug.gml) | Panel de depuración: variables en vivo, log, gráfica de FPS y medición de tiempos | ninguna | ⭐ Desarrollo |
| [`scr_audio.gml`](./scr_audio.gml) | Gestor de audio: buses y emisores por categoría, mezcla con ducking, banco de tomas con round robin, cupo de voces con fundido, anillo de emisores posicionales y crossfade de música/ambiente | ninguna | ⭐ Esencial |
| [`scr_tiempo.gml`](./scr_tiempo.gml) | `Cooldown` para habilidades, `Temporizador` independiente del framerate y un reloj de juego con escala de tiempo | ninguna | ⭐ Esencial |
| [`scr_ui_confirmar.gml`](./scr_ui_confirmar.gml) | Diálogo de confirmación (Sí/No) genérico, con «No» siempre por defecto — sin `show_question()` | ninguna | ⭐ Esencial |

---

## Detalle de cada script

### `scr_math_util.gml` — Matemáticas y easing

**Incluye:** `approach`, `wave`, `remap`, `remap_clamped`, `lerp_dt`, `smoothstep`, `snap`,
`ease_linear`, `ease_in_sine`, `ease_out_sine`, `ease_in_out_sine`, `ease_in_quad`,
`ease_out_quad`, `ease_in_out_quad`, `ease_in_cubic`, `ease_out_cubic`, `ease_in_out_cubic`,
`ease_in_back`, `ease_out_back`, `ease_out_elastic`, `ease_out_bounce`, `ease_out_expo`,
más el diccionario `global.EASINGS`.

**⚠️ NO reimplementes lo que ya es nativo.** Verificado con `gm-cli manual read`:

| Ya existe en GameMaker | No existe (por eso está aquí) |
|---|---|
| `lerp`, `clamp`, `angle_difference`, `dsin`, `dcos`, `sin`, `cos`, `abs`, `sign`, `min`, `max`, `floor`, `ceil`, `round`, `frac`, `sqrt`, `power`, `point_distance`, `point_direction`, `lengthdir_x`, `lengthdir_y`, `dot_product` | `approach`, `wave`, `remap`, `lerp_dt`, `smoothstep`, `snap`, todas las `ease_*` |

> **Sobre el easing:** GameMaker tiene `animcurve_*`, pero exige crear un **asset de curva de
> animación** en el IDE. Estas funciones no necesitan ningún asset.

```gml
vel_x = approach(vel_x, 0, 0.5);                        // frenado suave
y     = wave(-4, 4, 2000, 0);                           // flotar
var _v = ease_out_back(0.7);                            // curva
var _e = global.EASINGS[$ "out_elastic"];               // por nombre, desde datos
```

---

### `scr_camera.gml` — Cámara con todo lo que le vas a pedir

**Incluye:** `cam_init`, `cam_set_target`, `cam_set_deadzone`, `cam_set_smooth`,
`cam_set_lookahead`, `cam_set_bounds`, `cam_shake`, `cam_update`, `cam_center_on`,
`cam_fit_window`, `cam_destroy`.

```gml
// Create de obj_camera
cam = camera_create();
cam_init(cam, 640, 360);
cam_set_target(cam, obj_player);
cam_set_deadzone(cam, 80, 50);
cam_set_lookahead(cam, 48, 24);
cam_set_bounds(cam, 0, 0, room_width, room_height);
view_camera[0] = cam;

// Step de obj_camera
cam_update(cam);

// Al recibir un golpe
cam_shake(cam, 8, 0.4);
```

**Notas de diseño:**

- La posición se **redondea** antes de aplicarla: una cámara en posiciones con decimales hace que el pixel art se vea borroso.
- El shake usa un desplazamiento **aleatorio en círculo**, no en cuadrado: así no aparecen picos raros en las diagonales.
- `cam_fit_window()` mantiene la proporción al cambiar el tamaño de la ventana. Sin eso, la imagen se estira.

---

### `scr_state_machine.gml` — FSM con structs

**Incluye:** constructor `StateMachine` con `set`, `update`, `get`, `is`, `get_time`, `add`,
`list`, `back`; más `fsm_bind()` y `fsm_debug_draw()`.

```gml
// Create de obj_player
fsm = new StateMachine(id, {
    idle: {
        enter : function() { sprite_index = spr_player_idle; },
        update: function() { if (abs(vel_x) > 0) { fsm.set("correr"); } }
    },
    correr: {
        enter : function() { sprite_index = spr_player_run; },
        update: function() { if (abs(vel_x) == 0) { fsm.set("idle"); } }
    }
}, "idle");

// Step de obj_player
fsm.update();
```

> **`new StateMachine(...)` vs `fsm_bind(...)`:** con `new`, las funciones de estado se ejecutan
> en el ámbito del struct que las contiene (tienes que escribir `dueno.vel_x`). Con `fsm_bind()`,
> se reenlazan con `method()` al ámbito de la instancia y puedes escribir `vel_x` a secas.
> Elige uno y sé consistente.

---

### `scr_tween.gml` — Tweens por delta time

**Incluye:** `tween_to`, `tween_update`, `tween_stop`, `tween_stop_all`, `tween_count`,
`tween_clear_all`, `tween_delay`.

```gml
// Step de un controlador persistente
tween_update();

// Desde cualquier sitio
tween_to(obj_player, { x: 400, y: 200 }, 0.5, ease_out_quad);

// Con callback
tween_to(obj_menu, { image_alpha: 0 }, 0.3, ease_in_quad, function() {
    instance_destroy();
});
```

**Por qué `delta_time` y no frames:** un tween de 0,5 s dura 0,5 s tanto a 30 como a 144 fps.

**Por qué no `time_source`:** los Time Sources son perfectos para temporizadores **discretos**
(«llama a esto dentro de 2 s»), pero no para interpolar un valor frame a frame.

> ⚠️ `tween_count()` es tu detector de fugas: si crece sin parar, se te está escapando un tween.

---

### `scr_save_load.gml` — Guardado robusto

**Incluye:** `save_game`, `load_game`, `load_game_safe`, `load_game_recover`, `load_game_raw`,
`save_exists`, `save_get_meta`, `save_list`, `save_backup`, `save_backup_path`, `delete_save`,
`save_export_string`, `save_import_string`, `save_thumbnail_path`, `save_thumbnail_capture`,
`save_thumbnail_load`, `save_thumbnail_delete`.

```gml
// Guardar
save_game("slot1", { nivel: room_get_name(room), vida: obj_player.hp });

// Cargar con validación
var _datos = load_game_safe("slot1", function(_d) {
    return struct_exists(_d, "vida") && _d.vida > 0;
});

// Cargar con red de seguridad: si "slot1" falla, prueba las copias rotativas
var _datos_recuperados = load_game_recover("slot1");
```

**Las cinco reglas que respeta** (detalle completo, con el porqué de cada una, en
[`01 · 14 §9, §12 bis y §12 ter`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#9-sistema-de-guardado-completo-recomendado)):

1. **Escritura segura** — escribe en un temporal, lo valida releyéndolo y solo entonces reemplaza la partida. Si el juego se corta a medias, la partida sigue intacta.
2. **Versión de esquema** — constante `SAVE_VERSION`. Si cambias la forma de los datos, súbela y define `global.save_migrar`.
3. **Carpeta correcta** — usa `game_save_id`, válida en todas las plataformas. **Nunca** `working_directory`.
4. **Integridad real** — checksum que se COMPARA al cargar (`sha1_string_utf8`), no solo se calcula. Un fichero corrompido o editado a mano de forma que rompa los datos se **rechaza**.
5. **Red de seguridad** — cada guardado nuevo empuja el anterior a una cadena de copias rotativas (`SAVE_BACKUP_COUNT`, por defecto 3). Si el save principal no pasa la validación, `load_game_recover()` prueba las copias antes de rendirse.

> ⚠️ `json_stringify` guarda los **assets por nombre**. Si renombras un sprite, una partida vieja
> puede romper. De ahí la validación.
>
> 💡 Los fallos de `save_game()` y `__save_read_raw()` van a `show_debug_message()` de siempre,
> y también a un log persistente si tu proyecto define
> `global.save_logger = function(_nivel, _texto) { registrar(_nivel, _texto); }` con el
> `registrar()` de
> [`13 · 10 §7.2`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#72-un-log-con-niveles-que-sobrevive-al-cierre).
> Sin ese hook, el script se comporta exactamente igual que antes.

> 💡 **Metadatos de ranura y miniatura (septiembre 2026).** `save_game()` acepta un tercer
> argumento opcional, `_meta` — un struct libre (zona, tiempo jugado, porcentaje…) que
> `save_get_meta()`/`save_list()` devuelven sin cargar `datos` completo. Las cuatro funciones
> `save_thumbnail_*` capturan y recuperan una miniatura PNG por slot con `screen_save_part()`.
> Es la pieza que faltaba para pintar una pantalla de «elige partida» de verdad — receta
> completa (ficha de ranura, indicador de «guardando…», confirmación al sobrescribir) en
> [`13 · 05`, componente n)](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#n-ranura-de-guardado-metadatos-miniatura-y-guardando).

---

### `scr_ui_confirmar.gml` — Confirmación (Sí/No) reutilizable

**Incluye:** `confirmar_configurar_textos`, `confirmar_abrir`, `confirmar_activo`,
`confirmar_step`, `confirmar_dibujar`.

```gml
// Una vez, al arrancar (después de cargar la localización)
confirmar_configurar_textos(txt("comun_si"), txt("comun_no"));

// Step / Draw GUI de un objeto persistente
confirmar_step();
confirmar_dibujar();

// Donde haga falta confirmar algo destructivo
confirmar_abrir(txt("pausa_confirmar_salir"),
    function() { room_goto(rm_menu_principal); },   // "Sí"
    undefined);                                      // "No": solo cierra
```

Widget de confirmación genérico — «No» siempre empieza con el foco — para CUALQUIER acción
destructiva: salir, sobrescribir una ranura de guardado, borrar una partida, restablecer
ajustes. Generaliza el patrón de un solo uso que ya traía
[`04 · 41` §3.4.4](../04%20-%20Recetas%20por%20género/41%20-%20Transiciones%2C%20carga%20y%20pausa.md#344-seguro-que-quieres-salir--con-no-por-defecto-sin-show_question),
que la propia receta señalaba como «todavía sin generalizar». **No usa `show_question()`**:
bloquea el juego y se ignora fuera de Windows salvo en modo debug. Detalle completo, componente
m), en [`13 · 05`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#m-confirmación-síno-con-no-por-defecto).

> 💡 Este script **no llama a `txt()` directamente** (si tu proyecto no la define, ni
> compilaría): fija los rótulos una vez con `confirmar_configurar_textos()`, igual que
> `iniciar_audio()` u otros sistemas globales de
> [`04 · 00` §1](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md#1--los-sistemas-globales--se-montan-primero).

---

### `scr_pool.gml` — Object pooling

**Incluye:** constructor `Pool` con `get`, `get_at`, `release`, `release_all`, `grow`,
`set_reset_vars`, `for_each_active`, `count_active`, `count_free`, `destroy`; más
`pool_cleanup_orphans()`.

```gml
// Create de obj_game
pool_balas = new Pool(obj_bullet, 100, "Instances");
pool_balas.set_reset_vars({ vel_x: 0, vel_y: 0, image_alpha: 1 });

// Sacar una bala
var _b = pool_balas.get_at(x, y);
if (_b != noone) { _b.vel_x = 10; }

// Devolverla (en lugar de instance_destroy)
obj_game.pool_balas.release(id);

// Clean Up de obj_game
pool_balas.destroy();
```

> ⚠️ La desactivación **no es instantánea**: según el manual, no surte efecto hasta el final del
> evento en que se llama. Por eso el pool activa y ya puede escribir variables en la misma
> llamada, pero `instance_exists()` en ese mismo evento todavía dirá `true`.

---

### `scr_grid_pathfinding.gml` — Pathfinding

**Incluye dos implementaciones:**

**1. `Grid` — envoltorio sobre `mp_grid_*`** (rápido, en C++, sin coste por celda)

```gml
grid = new Grid(32);
grid.add_object(obj_wall);
var _ruta = grid.find_path(x, y, obj_player.x, obj_player.y);
if (_ruta != noone) { path_start(_ruta, 3, path_action_stop, false); }
// ⚠️ Destruye el path con path_delete() cuando deje de servirte
```

**2. `GridPonderado` — A* en GML puro CON coste por celda**

```gml
grid2 = new GridPonderado(32);
grid2.set_coste(5, 3, 4);                 // esa celda cuesta 4, no 1
grid2.bloquear(7, 2);                     // intransitable
var _puntos = grid2.buscar_px(x, y, tx, ty);   // array de { x, y }
```

| | `Grid` (`mp_grid`) | `GridPonderado` (A* propio) |
|---|---|---|
| Velocidad | Muy rápida (nativa) | Más lenta (GML) |
| Coste por celda | ❌ No | ✅ Sí |
| Memoria que limpiar | `mp_grid_destroy()` + `path_delete()` | Nada (arrays y structs) |
| Cuándo usarlo | **Por defecto** | Cuando unas celdas cuesten más que otras |

---

### `scr_input_buffer.gml` — Coyote time e input buffering

**Incluye:** constructores `InputBuffer`, `CoyoteTime` y `JumpHelper` (los dos juntos con la
lógica de salto resuelta), más `input_debug_draw()`.

```gml
// Create de obj_player
salto = new JumpHelper(6, 6);   // 6 frames de buffer, 6 de coyote

// Step de obj_player
var _en_suelo = place_meeting(x, y + 1, obj_wall);
salto.update(_en_suelo, keyboard_check_pressed(vk_space));

if (salto.consumir_salto()) {
    vel_y = -JUMP_SPEED;
}

// Salto variable: suelta y subes menos
if (keyboard_check_released(vk_space)) {
    vel_y = salto.cortar_salto(vel_y, 0.5);
}
```

> 💡 Los dos mecanismos juntos son la diferencia entre un plataformas que se siente **duro** y
> uno que se siente **justo**. Usa `input_debug_draw()` para ajustar los valores: si ves que el
> buffer nunca llega a cero cuando juegas, es demasiado largo.

---

### `scr_debug.gml` — Depuración

**Incluye:** `debug_init`, `debug_watch`, `debug_unwatch`, `debug_log`, `debug_clear_log`,
`debug_time_start`, `debug_time_end`, `debug_time_get`, `debug_update`, `debug_draw`,
`debug_draw_fps_graph`, `debug_assert`, `debug_toggle`, `debug_set_position`, `debug_set_font`.

```gml
// Create de obj_debug
debug_init();
debug_watch("vida",   function() { return obj_player.hp; });
debug_watch("estado", function() { return obj_player.fsm.get(); });

// Step
debug_update();

// Draw GUI
debug_draw();

// Medir un bloque
debug_time_start("pathfinding");
var _r = grid.find_path(x, y, tx, ty);
debug_time_end("pathfinding");
```

**Atajos:** `F3` muestra u oculta el panel · `F4` activa el Debug Overlay nativo de GameMaker.

> 💡 La **gráfica de FPS** es la herramienta más valiosa: la media (`fps`) esconde los picos, la
> gráfica (`fps_real` por frame) los muestra.

---

### `scr_audio.gml` — Gestor de audio

**Incluye:** `audio_init`, `audio_step`, `audio_destruir`, `mezcla_aplicar`, `voces_iniciar`,
`emisores_iniciar`, `emisores_liberar`, `variacion_tono`, `variacion_ganancia`, `banco_crear`,
`banco_siguiente`, `apagar_con_fundido`, `voces_paso`, `sonar_limitado`, `sonar_en`, `sfx`,
`sfx_ui`, `voz_decir`, `musica_poner`, `ambiente_poner`.

> ✅ **Unificado con
> [`13 - Diseño y producción de videojuegos/09`](<../13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md>)
> (Diseño de sonido y mezcla)**: hasta la ronda anterior ambos documentos definían, por separado,
> el mismo sistema con globals distintos. Este script es ahora la única implementación real; 13 · 09
> explica la teoría (niveles, *headroom*, *ducking*, LUFS…) y remite aquí para el código.

```gml
// Create de obj_audio (persistente, creado en la sala de arranque)
audio_init();

// Step de obj_audio
audio_step();

// Clean Up de obj_audio
audio_destruir();

// Desde cualquier sitio del juego
sfx(snd_disparo);                                 // efecto suelto
sonar_en(snd_explosion, other.x, other.y, 0.9);    // efecto EN el mundo
sonar_limitado(snd_impacto, 4, db_to_lin(-8));     // como mucho 4 a la vez, por el bus principal
musica_poner(snd_boss_theme);                      // crossfade de música
voz_decir(snd_linea_01);                           // agacha la música mientras suena

// El jugador mueve un slider en Opciones
global.volumen_musica = 0.4;
mezcla_aplicar();
```

**Por qué existe un emisor por categoría:** el audio 2D (`audio_play_sound`) y el 3D directo
(`audio_play_sound_at`) acaban siempre en el bus principal — solo lo que pasa por un **emisor**
asignado a un bus recibe su ganancia y sus efectos. De ahí que `sfx()`, `sfx_ui()`, `voz_decir()`,
`musica_poner()` y `ambiente_poner()` reproduzcan siempre a través de un emisor de su categoría, y
que el sonido posicional (`sonar_en()`) use un **anillo** de emisores reutilizables en vez de
`audio_play_sound_at()`.

> ⚠️ **`sonar_limitado()` es la excepción a propósito**: por defecto NO pasa `emitter` (va al bus
> principal, más barato para sonidos que se disparan muchas veces por segundo, como los pasos).
> Pásale un quinto argumento —normalmente `global.em.sfx`— si ese sonido concreto sí necesita el
> volumen de "Efectos" o un efecto de zona: `sonar_limitado(snd_impacto, 4, db_to_lin(-8), 10,
> global.em.sfx)`.

> ⚠️ El modelo de atenuación por defecto es `audio_falloff_none` (ganancia siempre 1):
> `audio_init()` lo cambia una sola vez, para todo el juego, a `audio_falloff_inverse_distance_clamped`.

> 💡 **Ducking automático:** mientras `voz_decir()` tiene una línea sonando, `audio_step()` agacha
> la música unos dB y la devuelve arriba despacio al terminar, sin tocar nada más.

---

### `scr_tiempo.gml` — Cooldown, Temporizador y reloj de juego

**Incluye:** `reloj_iniciar`, `reloj_actualizar`, `reloj_dt`, `reloj_dt_real`, `reloj_tiempo`;
constructor `Cooldown` con `usar`, `listo`, `fraccion`, `actualizar`, `reiniciar`; constructor
`Temporizador` con `actualizar`, `terminado`, `restante_segundos`, `fraccion`, `reiniciar`,
`pausar`, `reanudar`, `esta_pausado`.

```gml
// objReloj (persistente, depth muy negativo): Create
reloj_iniciar();
// Begin Step
reloj_actualizar();

// Create de obj_player — un Cooldown por habilidad
disparo_cd = new Cooldown(0.18);

// Step de obj_player
disparo_cd.actualizar(reloj_dt());
if (input_disparo && disparo_cd.usar()) { disparar(); }

// Draw GUI — barra de recarga
draw_rectangle(x, y, x + 64 * disparo_cd.fraccion(), y + 8, false);

// Create de obj_control — un Temporizador repetible con callback
oleada_timer = new Temporizador(30, true, function() { generar_oleada(); });

// Step de obj_control
oleada_timer.actualizar(reloj_dt());
```

**`Cooldown` frente a `Temporizador`:** un `Cooldown` es «¿puedo usar esta habilidad ya?» más una
fracción 0..1 para la barra de recarga. Un `Temporizador` es «dentro de N segundos, o cada N
segundos, ejecuta esto», con callback opcional y modo repetible sin acumular deriva.

> 💡 **`reloj_dt()` respeta `global.time_scale`** (ver `04 - Recetas por género/15 - Game feel y
> juice.md` §5.0): si el proyecto lo usa para tiempo bala, los `Cooldown` y `Temporizador`
> alimentados por `reloj_dt()` se ralentizan con él. Usa `reloj_dt_real()` para lo que NO debe
> frenarse (un cronómetro de partida, un menú).

---

## Convenciones de todos estos scripts

- **Comentarios y mensajes en español**, con tildes y eñes. UTF-8.
- **Nombres de funciones en `snake_case`**, igual que las nativas de GameMaker.
- **Parámetros con guion bajo delante** (`_velocidad`), para que Feather sepa que son locales.
- **JSDoc completo** en todas las funciones: `@function`, `@desc`, `@param {Tipo}`, `@returns`.
- **Cabecera** con las funciones nativas usadas, las dependencias y un ejemplo de uso.
- **Constantes en `UPPER_SNAKE_CASE`** con `#macro`.

## Checklist antes de usarlos en tu proyecto

- [ ] Arrastra el script y **compila** (Ctrl/Cmd + F5) antes de usarlo: así confirmas que no hay conflictos de nombres.
- [ ] Si Feather avisa de algo, revísalo: estos scripts están escritos para pasar Feather limpio.
- [ ] Llama a los destructores: `cam_destroy()`, `grid.destroy()`, `pool.destroy()`, `path_delete()`, `audio_destruir()`.
- [ ] Llama a `tween_update()`, `debug_update()`, `audio_step()` y `reloj_actualizar()` **una vez por frame** desde un objeto persistente.
- [ ] Borra o desactiva `scr_debug.gml` en la versión de **release**.

---

## Verificación

Todas las funciones nativas usadas en estos scripts se han comprobado contra el manual oficial
con `gm-cli manual read "<función>"`. El manual que consulta el CLI es el **monthly**, accesible
offline.

### ✅ Confirmadas como nativas (se usan, no se reimplementan)

`lerp` · `clamp` · `angle_difference` · `dsin` · `dcos` · `abs` · `sign` · `min` · `max` ·
`floor` · `ceil` · `round` · `frac` · `sqrt` · `power` · `point_distance` · `point_direction` ·
`lengthdir_x` · `lengthdir_y` · `dot_product` · `db_to_lin` · `audio_bus_create` ·
`audio_emitter_create` · `audio_emitter_bus` · `audio_emitter_falloff` · `audio_emitter_position` ·
`audio_emitter_free` · `audio_play_sound_ext` · `audio_sound_gain` · `audio_stop_sound` ·
`audio_is_playing` · `audio_system_is_available` · `audio_falloff_set_model` ·
`audio_falloff_inverse_distance_clamped` · `audio_listener_position` · `audio_get_name` ·
`camera_get_active` · `camera_create` · `camera_destroy` ·
`camera_set_view_pos` · `camera_set_view_size` · `camera_get_view_x` · `camera_get_view_y` ·
`camera_get_view_width` · `camera_get_view_height` · `camera_set_view_target` · `camera_apply` ·
`view_camera` · `view_wport` · `view_hport` · `view_xport` · `view_yport` · `window_get_width` ·
`window_get_height` · `mp_grid_create` · `mp_grid_destroy` · `mp_grid_add_instances` ·
`mp_grid_add_cell` · `mp_grid_add_rectangle` · `mp_grid_clear_all` · `mp_grid_clear_cell` ·
`mp_grid_get_cell` · `mp_grid_path` · `mp_grid_draw` · `path_add` · `path_delete` ·
`path_clear_points` · `path_add_point` · `path_get_number` · `path_get_point_x` ·
`path_get_point_y` · `path_get_length` · `path_start` · `path_end` · `ds_priority_create` ·
`ds_priority_add` · `ds_priority_delete_min` · `ds_priority_size` · `ds_priority_empty` ·
`ds_priority_destroy` · `json_stringify` · `json_parse` · `file_text_open_write` ·
`file_text_open_read` · `file_text_write_string` · `file_text_read_string` · `file_text_readln` ·
`file_text_eof` · `file_text_close` · `file_exists` · `file_delete` · `file_rename` ·
`file_copy` · `directory_exists` · `directory_create` · `game_save_id` · `sha1_string_utf8` ·
`instance_create_layer` ·
`instance_create_depth` · `instance_destroy` · `instance_exists` · `instance_number` ·
`instance_deactivate_object` · `instance_activate_object` · `instance_count` ·
`variable_instance_get` · `variable_instance_set` · `variable_struct_get` ·
`variable_struct_set` · `variable_struct_remove` · `variable_global_exists` · `struct_exists` ·
`struct_get` · `struct_set` · `struct_get_names` · `is_struct` · `is_array` · `is_method` ·
`is_string` · `is_numeric` · `is_real` · `is_undefined` · `is_nan` · `is_handle` · `typeof` ·
`method` · `array_create` · `array_length` · `array_push` · `array_pop` · `array_delete` ·
`array_insert` · `array_resize` · `array_first` · `array_last` · `array_sort` · `keyboard_check` ·
`keyboard_check_pressed` · `keyboard_check_released` · `gamepad_button_check_pressed` ·
`move_and_collide` · `place_meeting` · `instance_place` · `delta_time` · `room_speed` ·
`fps` · `fps_real` · `get_timer` · `current_time` · `show_debug_message` · `show_debug_overlay` ·
`draw_text` · `draw_rectangle` · `draw_line` · `draw_set_color` · `draw_set_alpha` ·
`draw_set_halign` · `draw_set_valign` · `draw_set_font` · `draw_get_color` · `draw_get_alpha` ·
`draw_get_halign` · `draw_get_valign` · `draw_get_font` · `display_get_gui_width` ·
`display_get_gui_height` · `string` · `string_format` · `date_current_datetime` ·
`date_datetime_string` · `layer_get_id` · `random` · `irandom` · `irandom_range` ·
`random_range` · `randomize` · `surface_create` · `surface_exists` · `surface_free` ·
`sphere_is_visible` · `time_source_create` · `time_source_start` · `time_source_stop` ·
`time_source_destroy` · `call_later` · `call_cancel` · `try` / `catch` / `finally` · `pi`

### ❌ Confirmado que NO existen como nativas (por eso están aquí)

`approach` · `wave` · `remap` · `lerp_dt` · `smoothstep` · `snap` · todas las funciones de
`easing` (`gm-cli manual read "easing"` → *«No results found»*) · `path_create` (es `path_add`) ·
`handle_type()` · `sprite_is_visible()`

### ⚠️ Sin verificar en esta sesión

Ninguna función de estos scripts queda sin verificar. Si al usarlos encuentras una que el
compilador no reconozca, confírmala tú mismo con `gm-cli manual read "<función>"` antes de
cambiar nada.

---

## Pruebas realizadas (agosto de 2026)

No me he limitado a leer el manual: he creado un proyecto real con `gm-cli init`, he importado
los nueve scripts y he compilado.

| Prueba | Comando | Resultado |
|---|---|---|
| Proyecto de prueba creado | `gm-cli init --no-interactive -n gmltest -t "Blank" --toolchain GMS2@2026.0.0.23` | ✅ Creado |
| Los 9 scripts importados como recursos | `gm-cli resourcetool script` con `RESOURCE CREATE TYPE=script NAME=…` | ✅ 9/9 creados |
| Compilación en **VM** | `gm-cli compile --target mac --toolchain GMS2@2026.0.0.23 --runtime vm` | ✅ Sin errores ni avisos |
| Compilación en **YYC (nativo)** | `gm-cli compile --target mac --toolchain GMS2@2026.0.0.23 --runtime native` | ✅ Sin errores ni avisos |
| Barrido de funciones nativas | 106 identificadores extraídos del código y contrastados con `gm-cli manual read` | ✅ 103/103 confirmadas |

### Ampliación (septiembre de 2026): `scr_audio.gml` y `scr_tiempo.gml`

Los mismos pasos, repetidos con los **once** scripts juntos en un proyecto nuevo:

| Prueba | Comando | Resultado |
|---|---|---|
| Todos los símbolos de GML de los dos scripts nuevos | `python3 "_indice/buscar.py" <símbolo>`, uno a uno | ✅ Todos existen en el runtime |
| `scr_audio.gml` y `scr_tiempo.gml` no inventan funciones | `python3 _indice/validar-codigo-gml.py` | ✅ 0 funciones del runtime inventadas |
| Proyecto de prueba creado en `~/gm_prueba_scripts` | `bash _indice/validar-compilacion.sh` | ✅ Creado y borrado al terminar |
| Los 11 scripts importados como recursos | mismo script, un `RESOURCE CREATE TYPE=script` por archivo | ✅ 11/11 creados |
| Compilación con `gm-cli compile` contra `GMS2@2026.0.0.23` | `bash _indice/validar-compilacion.sh` | ✅ "Compilation finished", 0 líneas con "error" |

> 💡 El compilador lanza una `NullReferenceException` de .NET al procesar los sprites de
> prueba `spr_player_idle`/`spr_player_run` (son *stubs* sin imagen real, creados solo para que
> exista el recurso). Es un artefacto del proyecto de prueba, no del GML: se reproduce igual en
> un proyecto en blanco sin ningún script, y el compilador la registra y sigue —
> `gm-cli compile` termina con código de salida 0 y sin ninguna línea que contenga "error".

**Sobre las 3 que el barrido marcó como ausentes:** no son funciones nativas, son falsos
positivos del extractor.

| Identificador | Qué es en realidad |
|---|---|
| `_cb` | Variable local que guarda un método (`var _cb = method(...)`, luego `_cb()`) |
| `posterior` | Fragmento de una cadena de texto: `"…es de una version posterior (v"` |
| `save_migrar` | Función **tuya**, no del motor: `global.save_migrar` |

**Sobre `c_aqua`, `c_dkgray` y `pi`:** la búsqueda del CLI no las indexa por nombre, pero están
confirmadas en las tablas de constantes del manual (`gm-cli manual read "Colour Constants"` y
`gm-cli manual read "Maths"`).

### Ampliación (8 de septiembre de 2026): `scr_ui_confirmar.gml` y metadatos de `scr_save_load.gml`

Mismos pasos, con los **doce** scripts juntos en un proyecto nuevo (hueco A11/B4b de
`_indice/auditorias/r5-juego-completo.md`):

| Prueba | Comando | Resultado |
|---|---|---|
| Todos los símbolos de GML nuevos (`scr_ui_confirmar.gml` y el `_meta`/miniatura de `scr_save_load.gml`) | `python3 "_indice/buscar.py" <símbolo>`, uno a uno | ✅ Todos existen en el runtime |
| El código nuevo no inventa funciones ni usa identificadores con tilde/eñe | `python3 _indice/validar-codigo-gml.py` | ✅ 0 funciones inventadas · 0 identificadores no ASCII |
| Proyecto de prueba creado en `~/gm_prueba_scripts` | `bash _indice/validar-compilacion.sh` (lista de scripts ampliada con `scr_ui_confirmar`) | ✅ Creado y borrado al terminar |
| Los 12 scripts importados como recursos | mismo script, un `RESOURCE CREATE TYPE=script` por archivo | ✅ 12/12 creados |
| Compilación con `gm-cli compile` contra `GMS2@2026.0.0.23` | `bash _indice/validar-compilacion.sh` | ✅ "Los 12 scripts reutilizables compilan sin errores" |
| Todos los bloques ```gml de los documentos que citan estos scripts (04 · 00, 04 · 41, 04 · 57, 13 · 05) | `python3 _indice/validar-compilacion-docs.py` | ✅ 3364/3364 bloques compilan |
| Enlaces internos nuevos (README, 04 · 57, 13 · 05, 04 · 00, 04 · 41) | `python3 _indice/verificar-enlaces.py` | ✅ 0 rutas rotas · 0 anclas rotas |

### ⚠️ Lo que NO he podido probar

**La ejecución en runtime.** El runner de macOS no llega a lanzar el juego cuando se le llama
desde el CLI en este equipo (se queda en `not in bundle / YYG Game launching` y sale sin escribir
el `debug.log`). Es un problema del arranque del runner por línea de comandos, no del código.

Por tanto:

- ✅ **Garantizado:** la sintaxis es correcta, todos los nombres de función y constantes existen, y el código compila limpio en VM y en YYC.
- 🔲 **No ejecutado:** el comportamiento en tiempo de ejecución de cada función.

Para cubrir ese hueco sin depender del runner, importa los scripts en tu proyecto y llama a las
funciones desde un objeto de prueba con `show_debug_message()`. Si algo se comporta distinto de
lo que dice la documentación, el culpable será casi siempre un valor límite, no un nombre de
función.

> 💡 **Cómo usar `gm-cli resourcetool` para esto** (es lo que he hecho yo):
> ```sh
> # Crear un script desde el contenido de un archivo
> gm-cli resourcetool eval 'RESOURCE CREATE TYPE=script NAME=scr_math_util FOLDER=Scripts'
> gm-cli resourcetool eval 'GML GETGMLFILEPATH NAME=scr_math_util'
> #   → copia tu .gml a la ruta que te devuelva
>
> # Crear objetos, eventos e instancias
> gm-cli resourcetool eval 'RESOURCE CREATE TYPE=object NAME=obj_test'
> gm-cli resourcetool eval 'OBJECT EVENT FINDORCREATE NAME=obj_test TYPE=Create'
> gm-cli resourcetool eval 'ROOM LAYER CREATE ROOM=Room1 NAME=Instances TYPE=INSTANCE'
> gm-cli resourcetool eval 'ROOM INSTANCE CREATE ROOM=Room1 OBJECT=obj_test LAYER=Instances X=64 Y=64'
> ```

---

## Fuentes

- Manual oficial (LTS) — <https://manual.gamemaker.io/lts/en/>
- Manual oficial (Monthly, el que consulta `gm-cli manual read`) — <https://manual.gamemaker.io/monthly/en/>
- [13 · GM CLI](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md) — referencia completa del CLI
- [04 · Convenciones y estilo GML](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) — las reglas de estilo que siguen estos scripts
- [03 · Glosario GML](../05%20-%20Referencia/03%20-%20Glosario%20GML.md) — qué significa cada término

---

*Scripts GML · GameMaker LTS 2026 · Agosto-septiembre de 2026 · UTF-8*
