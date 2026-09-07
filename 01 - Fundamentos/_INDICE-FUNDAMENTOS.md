# Índice · Fundamentos de GML (GameMaker LTS 2026)

> **Material de estudio** construido extrayendo y traduciendo el **manual oficial de GameMaker** (versión LTS 2026).
> Base documental: <https://manual.gamemaker.io/lts/en/>
> Apoyo offline: `gm-cli manual read "<tema>"` (consulta el manual *monthly* en local).

---

## Cómo usar este material

Cada archivo:

1. **Cita la URL exacta** del manual de la que se extrajo la información (al principio del documento).
2. Está escrito en **español** con tildes, eñes y signos de apertura (`¿`, `¡`). Codificación UTF-8.
3. Incluye **código `gml` comentado** en cada tema.
4. Se centra en el **«por qué»**, no solo en el «qué»: cada decisión de diseño está explicada.
5. Marca con ⚠️ las **trampas y cambios** que rompen código antiguo.

### Convención de iconos

| Icono | Significado |
|---|---|
| ⚠️ | Advertencia, trampa o error común |
| 💡 | Consejo práctico |
| ⭐ | Recomendación oficial del manual |
| 🆕 | Novedad relevante de versiones recientes |
| ❌ / ✅ | Código incorrecto / correcto |

---

## Tabla de contenidos

| # | Archivo | Temas |
|---|---|---|
| **01** | [El IDE y el flujo de trabajo](./01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md) | Asset Browser, Inspector, Output, editores, convenciones de nombres, VM vs YYC, YYZ, Git |
| **02** | [Tipos de datos y variables](./02%20-%20Tipos%20de%20datos%20y%20variables.md) | real, string, bool, int64, array, struct, method, handle, pointer, undefined, noone, NaN, infinity; ámbitos; `#macro` vs `enum`; conversión |
| **03** | [Handles — el cambio clave de 2026](./03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) | ⭐ **El capítulo crítico si vienes de 2023 o antes**. Qué es un handle, comparación, reciclado de índices, migración |
| **04** | [Structs y constructores (POO en GML)](./04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) | Struct literales, `constructor` + `new`, herencia con `:`, `static`, static chain, `delete`, `method()`, JSON |
| **05** | [Arrays y estructuras de datos](./05%20-%20Arrays%20y%20estructuras%20de%20datos.md) | Arrays 1D/2D, `array_*`, accessors, DS lists/maps/grids/stacks/queues/priority, cuándo usar cada uno |
| **06** | [Eventos y ciclo del juego](./06%20-%20Eventos%20y%20ciclo%20del%20juego.md) | Orden EXACTO de eventos, Create/Destroy/Clean Up, alarms, draw events, `delta_time`, Time Sources, vsync y frame pacing (`display_set_timing_method`) |
| **07** | [Funciones, métodos y ámbito](./07%20-%20Funciones,%20métodos%20y%20ámbito.md) | Script functions vs methods, argumentos, opcionales, `static`, closures, recursión, `method()`, JSDoc/Feather |
| **08** | [Movimiento y colisiones](./08%20-%20Movimiento%20y%20colisiones.md) | `move_and_collide()`, `place_meeting`, `instance_place`, máscaras, bounding boxes, collision space, physics |
| **09** | [Instancias, objetos y herencia](./09%20-%20Instancias,%20objetos%20y%20herencia.md) | `instance_create_*`, `with()`, `other`, desactivación, parent objects, `instance_change` ⚠️ deprecada, cuándo NO usar una instancia (partículas/asset layers/tilemap) |
| **10** | [Rooms, capas, cámaras y viewports](./10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md) | Rooms, navegación, persistencia, layers, tilemaps, cámaras, viewports, transiciones |
| **11** | [Dibujo y renderizado](./11%20-%20Dibujo%20y%20renderizado.md) | Draw targets, application surface, surfaces y sus formatos, shaders, blend modes, draw GUI, batching |
| **12** | [Input — teclado, ratón y gamepad](./12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md) | `keyboard_check`, mouse, gamepad, Device Input, librería **Input** |
| **13** | [Audio](./13%20-%20Audio.md) | `audio_play_sound_ext`, buses, efectos, grupos, 3D (emitters/listeners), sync, web audio |
| **14** | [Persistencia y archivos](./14%20-%20Persistencia%20y%20archivos.md) | Sandbox, working_directory/game_save_id, INI, JSON, buffers, guardado de structs, Test Framework |
| **15** | [Depuración y rendimiento](./15%20-%20Depuración%20y%20rendimiento.md) | Feather, debugger, Debug Overlay, GC, optimización, overdraw, checklist de limpieza, herramientas externas de perfilado (RenderDoc/Instruments/Android Profiler) |
| **16** | [Exportar y publicar](./16%20-%20Exportar%20y%20publicar.md) | Targets, opciones por plataforma, firma, empaquetado, requisitos de cada tienda |
| **17** | [GML Visual (Drag and Drop)](./17%20-%20GML%20Visual%20%28Drag%20and%20Drop%29.md) | Qué es y para quién, cómo se lee un bloque, las 27 familias de acciones, **tabla de equivalencias acción → GML**, `Convert to GML`, limitaciones reales, depuración |

---

## Orden de lectura recomendado

### 🟢 Ruta A — Vienes de otro lenguaje (Python, JS, C#)

```
01  El IDE y el flujo de trabajo      ← cómo se organiza un proyecto
02  Tipos de datos y variables        ← la base
04  Structs y constructores           ← la "POO" de GML
05  Arrays y estructuras de datos     ← colecciones
07  Funciones, métodos y ámbito       ← tu código, organizado
06  Eventos y ciclo del juego         ← CUÁNDO se ejecuta tu código ⭐
09  Instancias, objetos y herencia    ← el modelo de GameMaker
08  Movimiento y colisiones           ← tu primer juego que se mueve
10  Rooms, capas, cámaras y viewports ← el mundo
11  Dibujo y renderizado
12  Input
13  Audio
14  Persistencia y archivos
03  Handles  ← ⚠️ léelo SIEMPRE, pero si eres nuevo puede ir al final
15  Depuración y rendimiento
```

### 🔴 Ruta B — Vienes de GameMaker 2023 o anterior

**Empieza por el 03.** Es el cambio que rompe código silenciosamente.

```
03  Handles — el cambio clave de 2026   ← ⭐ PRIMERO, sin excusas
    ↳ Después salta a los puntos que te afectan:
      · 02  (tipos: los assets ya no son números)
      · 04  (structs: static, static_get/static_set, herencia)
      · 05  (arrays: Copy on Write deprecado)
      · 06  (Collision Compatibility Mode, Time Sources)
      · 08  (bounding boxes inclusivas, tilemaps en colisiones)
      · 09  (instance_change DEPRECADA, collision space en desactivación)
      · 11  (nuevos formatos de surface)
      · 14  (JSON y handles en guardados)
```

### 🟡 Ruta C — Quiero hacer un juego YA

```
06  Eventos y ciclo del juego          ← imprescindible
09  Instancias, objetos y herencia     ← imprescindible
08  Movimiento y colisiones            ← imprescindible
12  Input                              ← imprescindible
10  Rooms, capas, cámaras y viewports
11  Dibujo y renderizado
13  Audio
03  Handles                            ← antes de que te muerda
14  Persistencia y archivos
15  Depuración y rendimiento
```

### 🔵 Ruta D — Referencia rápida (consultar según necesidad)

Los archivos **02, 05, 07 y 15** funcionan bien como consulta puntual:
- **02** → tabla resumen de tipos y ámbitos.
- **05** → tabla comparativa y guía de decisión «¿qué uso?».
- **07** → tabla de reglas de funciones y errores típicos.
- **15** → checklist de rendimiento y tabla de limpieza de recursos.

---

## Los cinco conceptos que más bugs evitan

Si solo retienes cinco cosas de todo este material:

### 1. ⚠️ Los handles: compara contra `noone` / `-1`, nunca contra `0`

```gml
var _e = instance_nearest(x, y, obj_enemigo);
if (_e != noone) { with (_e) { vida -= 10; } }

// ❌ with(-1) NO se salta: se ejecuta sobre self
```

> 📄 [Tema 03](./03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md)

### 2. ⚠️ Los índices se reciclan: resetea tras destruir

```gml
ds_list_destroy(mi_lista);
mi_lista = -1;          // si no, apuntará a la lista que ocupe ese índice
```

> 📄 [Tema 03](./03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md)

### 3. ⚠️ Puedes confiar en el orden de los EVENTOS, no en el de las INSTANCIAS

Usa Begin Step / Step / End Step para garantizar precedencia.

> 📄 [Tema 06](./06%20-%20Eventos%20y%20ciclo%20del%20juego.md)

### 4. ⭐ `static` en los métodos de los constructores

```gml
function Arma() constructor
{
    static atacar = function() { /* una sola copia para todas */ }
}
```

> 📄 [Tema 04](./04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md)

### 5. ⚠️ Limpia los recursos dinámicos en **Clean Up**, no en Destroy

Clean Up también cubre fin de room y fin de juego.

> 📄 [Tema 15](./15%20-%20Depuración%20y%20rendimiento.md)

---

## Mapa de dependencias entre temas

```
                    ┌──────────────────┐
                    │  01 El IDE       │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
│ 02 Tipos y   │──▶│ 03 HANDLES ⚠️    │◀──│ 05 Arrays y  │
│    variables │   │  (transversal)   │   │      DS      │
└──────┬───────┘   └────────┬─────────┘   └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    │
┌──────────────┐   ┌──────────────────┐          │
│ 04 Structs   │   │ 09 Instancias    │          │
│      y POO   │──▶│      y herencia  │          │
└──────┬───────┘   └────────┬─────────┘          │
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
│ 07 Funciones │   │ 08 Movimiento    │   │ 06 Eventos   │
│   y métodos  │   │      colisiones  │   │  y ciclo     │
└──────────────┘   └────────┬─────────┘   └──────┬───────┘
                            │                    │
                            ▼                    ▼
                   ┌──────────────────┐  ┌──────────────┐
                   │ 10 Rooms, capas  │  │ 11 Dibujo    │
                   │     y cámaras    │─▶│      render  │
                   └──────────────────┘  └──────┬───────┘
                                                 │
     ┌──────────────┬──────────────┬─────────────┤
     ▼              ▼              ▼             ▼
┌─────────┐  ┌───────────┐  ┌──────────┐  ┌──────────────┐
│ 12 Input│  │ 13 Audio  │  │ 14 Persis│  │ 15 Depuración │
└─────────┘  └───────────┘  │  tencia  │  │      y perf   │
                            └──────────┘  └──────────────┘
```

**Leyenda:** el **tema 03 (Handles)** es transversal: afecta a casi todos los demás. El **tema 06 (Eventos)** es el que define *cuándo* se ejecuta todo lo demás.

---

## Apéndices rápidos

### Prefijos de nombres

| Prefijo | Tipo | | Prefijo | Tipo |
|---|---|---|---|---|
| `spr_` | Sprite | | `snd_` | Sound |
| `obj_` | Object | | `fnt_` | Font |
| `rm_` | Room | | `ts_` | Tile Set |
| `scr_` | Script | | `shd_` | Shader |
| `path_` | Path | | `seq_` | Sequence |

> 💡 Activa la regla **GM2017** en *Feather Preferences* para que el IDE los aplique solo a los assets nuevos.

### Valores «inválidos» que debes memorizar

| Tipo | Valor inválido |
|---|---|
| Handle genérico (surface, buffer, DS, time source, cámara…) | `-1` |
| Handle de **instancia** | `noone` (que vale `-4`) |
| Puntero sin sentido | `pointer_null` |
| Sin valor | `undefined` |

### Orden de los eventos de un step (resumen)

```
Begin Step → Timelines → Time Sources → Alarms → Step
  → Movimiento → Colisiones → End Step
  → Pre-Draw → Draw Begin → Draw → Draw End → Post-Draw
  → Draw GUI Begin → Draw GUI → Draw GUI End
```

### Cuándo usar VM vs YYC

| Situación | Salida |
|---|---|
| Desarrollo / iteración rápida | **VM** |
| Build final de juego pequeño | **VM** (suficiente) |
| Build final de juego grande o con mucha lógica | **YYC** (×2–×3 en CPU) |
| Web | **JavaScript** (ES6) |

---

## Lo que NO encontrarás aquí (y por qué)

Este material cubre los **fundamentos**. Quedan fuera, deliberadamente:

- **GML Visual** (drag & drop) — es otra forma de lo mismo, pero este material es de GML Code.
- **Networking / multijugador** — tema avanzado, merece su propia sección.
- **Shaders en profundidad** — apenas se mencionan sus lenguajes y aplicación básica (tema 11).
- **Secuencias y curvas de animación** — se mencionan, pero no se desarrollan.
- **Extensiones y plataformas específicas** (Steam, Google Play, App Store…).
- **Partículas en detalle** — se listan, pero no se explican a fondo.

---

## Fuentes

Todo el contenido se ha extraído de:

- **Manual LTS (principal):** <https://manual.gamemaker.io/lts/en/>
- **Manual monthly (apoyo, vía `gm-cli`):** <https://manual.gamemaker.io/monthly/en/>
- **Repositorios:** <https://github.com/YoYoGames> (gm-cli, GM-TestFramework, GMEXT-*)
- **Librería Input** (comunidad, recomendada por YoYo): <https://codeberg.org/offalynne/Input> · documentación en <https://offalynne.grebedoc.dev/Input/>

### Páginas consultadas

```
Introduction/The_Asset_Browser.htm
Introduction/Compiling.htm
Introduction/The_Output_Window.htm
Additional_Information/The_File_System.htm

GameMaker_Language/GML_Overview/Data_Types.htm
GameMaker_Language/GML_Overview/Variables_And_Variable_Scope.htm
GameMaker_Language/GML_Overview/Arrays.htm
GameMaker_Language/GML_Overview/Structs.htm
GameMaker_Language/GML_Overview/Structs/Static_Structs.htm
GameMaker_Language/GML_Overview/Script_Functions.htm
GameMaker_Language/GML_Overview/Method_Variables.htm
GameMaker_Language/GML_Overview/Functions/Static_Variables.htm
GameMaker_Language/GML_Overview/Variables/Constants.htm
GameMaker_Language/GML_Overview/Instance_Keywords.htm
GameMaker_Language/GML_Overview/Accessors.htm
GameMaker_Language/GML_Overview/Language_Features/new.htm
GameMaker_Language/GML_Overview/Language_Features/delete.htm

GameMaker_Language/GML_Reference/Variable_Functions/Variable_Functions.htm
GameMaker_Language/GML_Reference/Variable_Functions/Array_Functions.htm
GameMaker_Language/GML_Reference/Variable_Functions/handle.htm
GameMaker_Language/GML_Reference/Variable_Functions/is_handle.htm
GameMaker_Language/GML_Reference/Data_Structures/Data_Structures.htm
GameMaker_Language/GML_Reference/Strings/Strings.htm

GameMaker_Language/GML_Reference/Asset_Management/Instances/Instances.htm
GameMaker_Language/GML_Reference/Asset_Management/Instances/instance_change.htm
GameMaker_Language/GML_Reference/Asset_Management/Instances/instance_id_get.htm
GameMaker_Language/GML_Reference/Asset_Management/Instances/Deactivating_Instances/Deactivating_Instances.htm
GameMaker_Language/GML_Reference/Asset_Management/Instances/Instance_Variables/collision_space.htm
GameMaker_Language/GML_Reference/Asset_Management/Rooms/Rooms.htm
GameMaker_Language/GML_Reference/Asset_Management/Rooms/General_Layer_Functions/General_Layer_Functions.htm
GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/Tile_Map_Layers.htm
GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio.htm

GameMaker_Language/GML_Reference/Movement_And_Collisions/Movement/Movement.htm
GameMaker_Language/GML_Reference/Movement_And_Collisions/Movement/move_and_collide.htm
GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/Collisions.htm
GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/Collision_Compatibility_Mode.htm

GameMaker_Language/GML_Reference/Drawing/Drawing.htm
GameMaker_Language/GML_Reference/Drawing/Surfaces/Surfaces.htm
GameMaker_Language/GML_Reference/Drawing/Surfaces/surface_create.htm
GameMaker_Language/GML_Reference/Cameras_And_Display/Cameras_And_Display.htm
GameMaker_Language/GML_Reference/Cameras_And_Display/Cameras_And_Viewports/Cameras_And_View_Ports.htm

GameMaker_Language/GML_Reference/Game_Input/Game_Input.htm
GameMaker_Language/GML_Reference/Game_Input/Keyboard_Input/Keyboard_Input.htm
GameMaker_Language/GML_Reference/Game_Input/Mouse_Input/Mouse_Input.htm
GameMaker_Language/GML_Reference/Game_Input/GamePad_Input/Gamepad_Input.htm

GameMaker_Language/GML_Reference/Time_Sources/Time_Sources.htm
GameMaker_Language/GML_Reference/Time_Sources/time_source_create.htm
GameMaker_Language/GML_Reference/Buffers/Buffers.htm
GameMaker_Language/GML_Reference/File_Handling/File_Handling.htm
GameMaker_Language/GML_Reference/Garbage_Collection/Garbage_Collection.htm
GameMaker_Language/GML_Reference/Debugging/Debugging.htm
GameMaker_Language/GML_Reference/Debugging/The_Debug_Overlay.htm

The_Asset_Editors/Object_Properties/Object_Events.htm
The_Asset_Editors/Object_Properties/Event_Order.htm
The_Asset_Editors/Object_Properties/Draw_Events.htm
The_Asset_Editors/Object_Properties/Parent_Objects.htm
```

---

*Material de estudio · GameMaker LTS 2026 · Agosto de 2026*
