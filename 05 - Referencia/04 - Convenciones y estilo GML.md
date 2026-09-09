# 04 · Convenciones y estilo GML

> **Las reglas de nombrado, organización y revisión** para tus proyectos de GameMaker.
> Generado en **agosto de 2026** · Contexto: **GameMaker LTS 2026.0** (IDE 2026.0.0.16 · GMS2 Runtime 23).
>
> **Por qué existe este archivo:** porque GameMaker no te obliga a nada. Puedes llamar a un
> objeto `asdf` y funcionará. Seis meses después, ni tú sabrás qué hacía. Estas reglas son el
> mínimo que evita ese futuro.

---

## 1. Prefijos de recursos (obligatorio)

GameMaker no tiene espacios de nombres. El prefijo **es** tu espacio de nombres: te dice qué
tipo de cosa es un identificador antes de buscarlo en el Asset Browser.

| Prefijo | Recurso | Ejemplo |
|---|---|---|
| `spr_` | Sprite | `spr_player_idle`, `spr_enemy_slime` |
| `obj_` | Objeto | `obj_player`, `obj_bullet`, `obj_wall` |
| `rm_` | Room | `rm_menu`, `rm_level_01`, `rm_boss` |
| `scr_` | Script | `scr_math_util`, `scr_save_load` |
| `snd_` | Sonido / música | `snd_jump`, `snd_music_boss` |
| `fnt_` | Fuente | `fnt_ui`, `fnt_dialogue` |
| `bg_` | Fondo / background | `bg_sky`, `bg_parallax_far` |
| `shd_` | Shader | `shd_outline`, `shd_water` |
| `ts_` | Tileset | `ts_dungeon`, `ts_overworld` |
| `tl_` | Tilemap layer | `tl_collision`, `tl_decor` |
| `an_` | Animación / Sequence | `an_intro`, `an_death` |
| `ps_` | Particle system (asset) | `ps_explosion`, `ps_dust` |
| `pt_` | Particle type | `pt_spark` |
| `path_` | Path | `path_patrol_01` |
| `sh_` | Script de shader (alternativo) | — |
| `enum_` | — | ❌ No: los enums van en `UPPER_SNAKE_CASE` |

**Reglas de los prefijos:**

- Siempre en **minúsculas**, con guion bajo, sin excepciones.
- El prefijo va **pegado** al nombre: `spr_player_idle`, no `spr_Player_Idle`.
- Nunca uses un prefijo para otra cosa. `obj_` en un sprite confunde a Feather y a ti.
- Los **nombres propios** del recurso van en `PascalCase` después del prefijo.

```gml
// ✅ Correcto
spr_player_run
obj_enemy_bat
rm_level_01
scr_camera
snd_music_boss

// ❌ Incorrecto
PlayerRun            // sin prefijo: ¿sprite, objeto, sonido?
obj_enemybat         // palabra compuesta ilegible
obj_Enemy_Bat        // prefijo con mayúscula
sprite_player_run    // prefijo inventado
```

---

## 2. Cómo nombrar cada cosa

| Qué | Estilo | Ejemplo |
|---|---|---|
| **Recursos** (sprites, objetos, rooms, scripts…) | `prefijo_PascalCase` | `obj_enemy_slime` |
| **Scripts / funciones globales** | `snake_case` o `prefijo_snake_case` | `scr_calcular_dano`, `calcular_dano` |
| **Variables de instancia** | `snake_case` | `move_speed`, `coyote_timer`, `hp` |
| **Variables locales** | `_snake_case` (guion bajo delante) | `var _velocidad`, `var _input_x` |
| **Constantes y macros** | `UPPER_SNAKE_CASE` | `GRAVITY`, `MAX_HEALTH`, `TILE_SIZE` |
| **Enums** (el tipo) | `PascalCase` | `Estado`, `TipoDano` |
| **Miembros de enum** | `UPPER_SNAKE_CASE` | `Estado.MUERTO`, `TipoDano.FUEGO` |
| **Constructores** | `PascalCase` | `Enemigo`, `Inventario` |
| **Miembros de instancia de struct** | `snake_case` | `_e.vida`, `_e.velocidad` |
| **Miembros «privados» de struct** | `__snake_case` (doble guion bajo) | `__timer`, `__cache` |
| **Funciones `static` de struct** | `snake_case` | `static recibir_dano = function() {}` |

**El guion bajo de las locales no es decoración.** Es lo que le dice a Feather «esta variable
solo existe dentro de este evento» y te avisa si la usas fuera. Úsalo siempre.

```gml
// ✅ Correcto
var _vel = 4;
var _dir = point_direction(x, y, mouse_x, mouse_y);

// ❌ Incorrecto: sin guion bajo, Feather no puede ayudarte
var vel = 4;
```

### 2 bis. Una función global y una variable de instancia NO pueden llamarse igual

Y no da error. Es la trampa de nombres más silenciosa de GML, porque las tres cosas que
comprobarías dicen que todo va bien:

```gml
// Un script global:
function nivel_clave(_nombre, _col, _fila) { return _nombre + "_x" + string(_col); }

// Y una variable de instancia con el mismo nombre:
_inst.nivel_clave = "n1_x2_y1";        // ✅ la asignación funciona
variable_instance_exists(_inst, "nivel_clave")   // ✅ true: la variable está ahí
variable_instance_get(_inst, "nivel_clave")      // ✅ "n1_x2_y1": el valor está ahí
_inst.nivel_clave                                // ✅ "n1_x2_y1" DESDE FUERA, con punto

// Pero dentro de la propia instancia, leyendo el nombre desnudo:
with (_inst) {
    if (nivel_clave == "n1_x2_y1") { … }         // ❌ NUNCA entra
}
// `nivel_clave` ahí devuelve LA FUNCIÓN, no el valor. La comparación es siempre falsa.
```

**Está medido**, no deducido del manual: sale de ejecutar el banco de pruebas de
[`06 · scr_nivel_mapa.gml`](../06%20-%20Assets%20y%20Scripts/scr_nivel_mapa.gml) dentro de un juego
real (`bash _indice/validar-ejecucion.sh`). El script **compilaba sin un solo aviso** y Feather
no dijo nada: por eso la comprobación vive en una prueba que se ejecuta, no en una regla escrita.

**La regla que se sigue de ahí**, y que ese script cumple: si un sistema tuyo reparte variables a
las instancias que crea, dale a las funciones un prefijo **más largo** que a las variables, para
que ningún nombre aparezca en las dos listas.

| | Prefijo | Ejemplo |
|---|---|---|
| Funciones del sistema | `nivel_mapa_…` | `nivel_mapa_construir()`, `nivel_mapa_clave()` |
| Variables que pone en cada instancia | `nivel_…` | `nivel_col`, `nivel_fila`, `nivel_clave` |

Es el mismo razonamiento de §1 —el prefijo **es** tu espacio de nombres— aplicado a un choque
que §1 no cubría: no entre dos recursos, sino entre una función y una variable.

---

## 3. Nombres reservados — NO los uses

GameMaker ya los usa para sus propias variables de instancia. Si los redefines, rompes el motor
de formas que cuestan horas de depurar.

### Posición y movimiento

`x` · `y` · `xprevious` · `yprevious` · `xstart` · `ystart` · `hspeed` · `vspeed` · `speed` ·
`direction` · `gravity` · `gravity_direction` · `friction`

### Identidad y orden

`id` · `object_index` · `depth` · `persistent` · `visible` · `solid` · `layer` · `mask_index`

### Sprite y dibujo

`sprite_index` · `image_index` · `image_speed` · `image_xscale` · `image_yscale` ·
`image_angle` · `image_alpha` · `image_blend` · `sprite_width` · `sprite_height` ·
`sprite_xoffset` · `sprite_yoffset`

### Colisión

`bbox_left` · `bbox_right` · `bbox_top` · `bbox_bottom`

### Sistema y legacy

`score` · `lives` · `health` · `alarm` · `room` · `room_speed` · `room_width` · `room_height` ·
`room_persistent` · `mouse_x` · `mouse_y` · `delta_time` · `fps` · `fps_real` ·
`application_surface` · `view_camera` · `current_time` · `current_second` · `os_type` ·
`async_load` · `event_type` · `other` · `self` · `noone` · `all` · `global` · `undefined` ·
`pointer_null` · `path_index` · `path_position` · `path_speed` · `timeline_index` ·
`phy_*` (todo el prefijo)

### Alternativas recomendadas

| Reservado | Usa en su lugar |
|---|---|
| `speed` | `vel`, `move_speed`, `spd` |
| `direction` | `dir`, `angulo`, `facing` |
| `gravity` | `grav`, `gravedad` |
| `health` | `hp`, `vida`, `salud` |
| `score` | `puntos`, `puntuacion` |
| `lives` | `vidas` |
| `depth` | `depth_sort` (o usa layers y no lo toques) |
| `id` | `id_instancia`, `mi_id` |

> ⚠️ **Cómo pillarlos a tiempo:** activa **Feather**. Te marcará la redefinición de variables
> reservadas como aviso antes de que se convierta en un bug.

---

## 4. Organización de carpetas en el Asset Browser

Estructura recomendada para un proyecto que va a crecer:

```
Sprites/
  Player/
  Enemies/
  UI/
  Tilesets/
  FX/
Objects/
  Player/
  Enemies/
  System/          ← controladores, managers, cámaras
  UI/
  Collision/       ← muros, suelos, zonas de trigger
Rooms/
  Menus/
  Levels/
  Test/            ← rooms de prueba desechables
Scripts/
  Utils/           ← matemáticas, helpers puros
  Systems/         → cámaras, guardado, pooling, FSM
  Data/            ← enums, tablas de datos, constantes
Shaders/
Sounds/
  SFX/
  Music/
Fonts/
Tilesets/
Notes/
```

**Reglas:**

1. **Carpetas por tipo de recurso y luego por dominio**, no al revés. `Sprites/Enemies` es mejor que `Enemies/Sprites` porque el Asset Browser ya agrupa por tipo.
2. **Carpeta `Test/` o `_scratch/` para lo desechable.** Y bórrala antes de exportar.
3. **Una carpeta `System/` para los objetos sin representación visual**: `obj_game`, `obj_camera`, `obj_input`. Así sabes qué toca la lógica global.
4. **No anides más de tres niveles.** Si necesitas más, tu proyecto pide a gritos un prefab o una extensión.

---

## 5. Comentarios y JSDoc para Feather

Feather está **activado por defecto en 2026**. Le das información con JSDoc y él te devuelve
detección de errores antes de compilar. Es el mejor retorno de inversión de todo este documento.

```gml
/// @function calcular_dano(base, multiplicador, critico)
/// @desc    Calcula el daño final aplicando multiplicador y crítico.
/// @param   {Real}   base          Daño base del arma.
/// @param   {Real}   multiplicador Multiplicador por tipo de enemigo.
/// @param   {Bool}   critico       Si el golpe es crítico.
/// @returns {Real}   Daño final, ya redondeado.
function calcular_dano(_base, _multiplicador, _critico) {
    var _dano = _base * _multiplicador;
    if (_critico) { _dano *= 2; }
    return round(_dano);
}
```

### Etiquetas que más vas a usar

| Etiqueta | Para qué |
|---|---|
| `/// @function nombre(args)` | Declara la firma |
| `/// @desc` | Descripción en una línea |
| `/// @param {Tipo} nombre  Descripción` | Cada argumento, con su tipo |
| `/// @returns {Tipo}` | Qué devuelve |
| `/// @deprecated Usa X` | Marca una función como obsoleta |
| `/// @ignore` | Le dice a Feather que no la analyse |
| `/// @context {Id.Instance}` | Indica el ámbito esperado de un método |

### Tipos que reconoce Feather

`Real` · `String` · `Bool` · `Array` · `Struct` · `Id.Instance` · `Id.DsGrid` · `Asset.GMSprite` ·
`Asset.GMObject` · `Asset.GMRoom` · `Constant.Color` · `Function` · `Any` · `Enum.Nombre`

Usa `Any` con moderación: es la forma de decirle a Feather «no mires aquí», que es renunciar a
su ayuda.

### Cuándo comentar

```gml
// ❌ No comentes lo obvio
vida -= 1;              // resto 1 a vida
x += _vel;              // muevo el personaje

// ✅ Comenta el POR QUÉ, no el QUÉ
// El coyote time da 6 frames de gracia tras salir del borde:
// sin él, los saltos al borde de una plataforma se sienten injustos.
if (!en_suelo) { coyote_timer--; }

// ✅ Comenta las decisiones no evidentes
// Usamos mp_grid con celdas de 32 px: con 16 px el pathfinding
// tardaba 12 ms en el peor caso y provocaba tirones en las oleadas.
var _grid = mp_grid_create(0, 0, room_width div 32, room_height div 32, 32, 32);
```

**Regla:** si el código necesita un comentario para entenderse, primero intenta renombrar las
variables. Si sigue necesitándolo, el comentario explica **por qué**, nunca **qué**.

---

## 6. Structs vs objetos — cuándo usar cada uno

Esta es la decisión de diseño más importante del GML moderno.

| Usa un **objeto** cuando… | Usa un **struct** cuando… |
|---|---|
| Necesite **eventos** (Step, Draw, Collision) | Solo guarde **datos** |
| Exista **en la room** y tenga posición | Sea una configuración, un ítem, una entrada de tabla |
| Colisione con otras instancias | Sea un nodo de un grafo, una celda de un grid, una estadística |
| Se dibuje a sí mismo | Sea el resultado de un cálculo o un valor de retorno |
| Necesite herencia de objetos | Necesite herencia de constructores |

```gml
// ✅ Objeto: vive en la room, tiene eventos, colisiona
// obj_enemy → Create / Step / Draw / Collision

// ✅ Struct: son datos puros
function Item(_nombre, _precio, _tipo) constructor {
    nombre = _nombre;
    precio = _precio;
    tipo   = _tipo;

    static es_equipable = function() { return tipo == "arma" || tipo == "armadura"; };
}

var _espada = new Item("Espada corta", 50, "arma");
```

**El caso intermedio — el más común:** un objeto del motor que **contiene** un struct con sus
datos. Así separas configuración (struct, serializable a JSON) de comportamiento (objeto, con
eventos).

```gml
// obj_enemy · Create
stats = new Stats(10, 3, 1.5);   // struct: datos, serializable
// el comportamiento (perseguir, atacar) vive en los eventos del objeto
```

> ⚠️ **No serialices objetos.** Un struct se guarda con `json_stringify()`. Una instancia, no.
> Guarda el struct y reconstruye la instancia a partir de él.

---

## 7. Gestión de errores y aserciones

GML no lanza excepciones. Si una función recibe basura, o devuelve basura, o se cierra el juego.
Tu única defensa es **comprobar**.

### Comprueba las entradas en las fronteras

```gml
/// @param {Struct} _datos  Datos cargados del disco.
/// @returns {Bool}         ¿Son válidos?
function validar_partida(_datos) {
    if (!is_struct(_datos)) { return false; }
    if (!struct_exists(_datos, "version")) { return false; }
    if (!struct_exists(_datos, "jugador")) { return false; }
    return true;
}
```

### Aserciones: falla ruidosamente en desarrollo, calla en release

```gml
#macro DEBUG true

/// @desc Lanza un error en tiempo de ejecución si la condición es falsa.
///       En builds de release no hace nada.
/// @param {Bool}   _condicion
/// @param {String} _mensaje
function assert(_condicion, _mensaje) {
    if (DEBUG && !_condicion) {
        show_debug_message("### ASSERT FALLIDO: " + _mensaje);
        show_error("ASSERT: " + _mensaje, false);
    }
}

// Uso
function aplicar_dano(_objetivo, _cantidad) {
    assert(instance_exists(_objetivo), "aplicar_dano recibió una instancia inexistente");
    assert(_cantidad >= 0, "daño negativo: " + string(_cantidad));
    _objetivo.hp -= _cantidad;
}
```

### Comprueba lo que se puede perder

| Recurso | Comprobación obligatoria |
|---|---|
| **Surface** | `surface_exists(surf)` antes de usarla. Puede desaparecer al perder el foco |
| **Buffer** | Comprueba que no es `undefined` antes de `buffer_read()` |
| **Fichero** | `file_exists(ruta)` antes de abrirlo |
| **Instancia** | `instance_exists(inst)` antes de acceder a sus variables |
| **Handle** | `is_handle(h)` antes de pasarlo a una función de asset |
| **Asset cargado dinámicamente** | Comprueba que no es `undefined`; el compilador puede haberlo descartado |

### El patrón de guardado seguro

Nunca escribas directamente sobre tu único fichero de partida. Escribe en uno temporal,
verifica y **luego** reemplaza. Si el proceso se corta a medias, la partida sigue intacta.

```gml
// Ver `scr_save_load.gml` para la implementación completa.
guardar_a_temporal();
if (validar_temporal()) { reemplazar_partida(); }
else { descartar_temporal(); }
```

---

## 8. Checklist de revisión antes de compilar

Recorre esta lista antes de cada commit y antes de cada build de release.

### Código

- [ ] **Feather sin avisos nuevos.** Si hay uno que no entiendes, no lo silencies: investígalo.
- [ ] Ninguna variable local sin `_` delante.
- [ ] Ninguna variable reservada redefinida (`speed`, `health`, `depth`, `gravity`, `score`).
- [ ] Todos los recursos con su prefijo correcto.
- [ ] Ninguna función pública sin JSDoc con `@param` / `@returns`.
- [ ] Ningún `magic number` suelto: todo en constantes o enums.
- [ ] Ningún bloque de código comentado sin explicación (bórralo: para eso está Git).

### Memoria

- [ ] Todas las `surface_create()` tienen su `surface_free()` en Clean Up.
- [ ] Todos los `buffer_create()` tienen su `buffer_delete()`.
- [ ] Todos los `ds_*_create()` tienen su `ds_*_destroy()`.
- [ ] Todos los `time_source_create()` tienen su `time_source_destroy()` cuando dejan de servir.
- [ ] Todos los `path_add()` tienen su `path_delete()`.
- [ ] Los structs y arrays **no** necesitan limpieza: el GC se encarga.

### Eventos

- [ ] El código que lee input está en **Begin Step** o **Step**, nunca en **Draw**.
- [ ] El código que dibuja está en un evento **Draw**, nunca en Step.
- [ ] `draw_set_*()` siempre se restaura (color, alpha, fuente, halign, valign).
- [ ] No hay lógica de negocio dentro de bloques `with()` innecesarios.

### Rooms

- [ ] Ninguna instancia duplicada por accidente en el Room Editor.
- [ ] Las layers están en el orden de dibujado correcto.
- [ ] Las cámaras y viewports están asignados en todas las rooms que lo necesitan.

### Assets

- [ ] Ningún asset huérfano sin usar (bórralo o márcalo).
- [ ] Los assets que cargas **dinámicamente** por nombre están marcados con `MarkTagAsUsed`.
- [ ] Los sprites tienen el origen y la máscara correctos.

### Antes de release

- [ ] Compila en **YYC**, no en VM.
- [ ] Prueba el build **fuera del IDE** (el runner del IDE perdona cosas que el ejecutable no).
- [ ] Prueba en la resolución más baja que vayas a soportar.
- [ ] Prueba a perder el foco de la ventana y volver (ahí mueren las surfaces).

---

## 9. Plantilla de cabecera para tus scripts

Copia y adapta esto en cada script nuevo:

```gml
// ============================================================================
// scr_nombre_del_script.gml
// Descripción: una línea de qué hace este script.
// Dependencias: scr_math_util (opcional)
// Verificado contra el manual: LTS 2026.0 (agosto 2026)
// ============================================================================

#macro NOMBRE_CONSTANTE 10

/// @function hacer_algo(argumento)
/// @desc    Qué hace, en una frase.
/// @param   {Real} _argumento  Qué significa.
/// @returns {Bool}             Qué devuelve.
function hacer_algo(_argumento) {
    return _argumento > 0;
}
```

---

## 10. Resumen en una pegatina

```
Recursos    → prefijo_PascalCase    obj_enemy_slime
Instancia   → snake_case            move_speed, coyote_timer
Local       → _snake_case           var _input_x
Constante   → UPPER_SNAKE_CASE      GRAVITY, TILE_SIZE
Constructor → PascalCase            Enemigo, Inventario
Privado     → __snake_case          __timer

NO uses:  speed direction gravity health score lives depth id

Prefijos: spr_ obj_ rm_ scr_ snd_ fnt_ bg_ shd_ ts_ tl_ an_ ps_ pt_ path_

Siempre:  JSDoc en funciones públicas · limpiar surfaces/buffers/ds_/time sources
          Feather sin avisos · compilar en YYC para release
```

---

## Fuentes

- Manual oficial (LTS) · Data Types — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Data_Types.htm>
- Manual oficial (LTS) · Variable Functions (structs) — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Variable_Functions.htm>
- Manual oficial (LTS) · Feather — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Feather.htm>
- Manual oficial (LTS) · Garbage Collection — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Garbage_Collection/Garbage_Collection.htm>
- [01 - Fundamentos/02 · Tipos de datos y variables](../01%20-%20Fundamentos/02%20-%20Tipos%20de%20datos%20y%20variables.md)
- [01 - Fundamentos/04 · Structs y constructores](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md)
- [01 - Fundamentos/15 · Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md)

---

*Convenciones y estilo GML · GameMaker LTS 2026 · Agosto de 2026 · UTF-8*
