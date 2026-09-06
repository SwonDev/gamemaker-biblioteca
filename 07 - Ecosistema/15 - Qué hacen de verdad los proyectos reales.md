# 15 · Qué hacen de verdad los proyectos reales

> **Análisis del corpus descargado**, hecho el **1 de septiembre de 2026** sobre los
> **21 juegos y motores** de [`11 - Código descargado`](../11%20-%20Código%20descargado/_CATALOGO.md):
> **1 333 953 líneas de GML**.
>
> No es opinión ni recomendación de nadie: es **qué usa realmente** el código que ya funciona.
> Se midió con un analizador que recorre cada `.gml` buscando marcadores de técnica y contando
> llamadas a función.

---

## ⚠️ Antes de nada: la situación legal del corpus

**No todos estos proyectos se pueden reutilizar.** Hay tres grupos y conviene no mezclarlos:

| Grupo | Proyectos | Qué puedes hacer |
|---|---|---|
| ✅ **Licencia libre** | `Pixel-Composer`, `DyNode`, `NoteBlockStudio`, `tldr-engine`, `Harmony-Framework`, `UndertaleEngine` (MIT) · `FVM-Reborn`, `nt-recreated-public`, `DeltaruneChinese` (GPL) · `Gang-Garrison-2` (MPL) | Estudiar y reutilizar **respetando la licencia**. GPL y MPL son contagiosas: léelas antes |
| 🟡 **Sin licencia declarada** | `MegamixEngine`, `OrbinautFramework`, `ChapterMaster`, `Mine-imator` | **Sin licencia = todos los derechos reservados.** Se pueden leer y estudiar; **no** copiar sin permiso del autor |
| 🔴 **Juegos comerciales descompilados** | `Pizza-Tower-EXtracted`, `HotlineMiami.gmx`, `Kirby-Soft-and-Wet`, `AM2R-Re-Splashed`, `Undertale-Engine-modded` | **Solo lectura, para entender cómo se hizo.** Copiar su código o sus assets a un proyecto tuyo no es una opción |

> 💡 **Por eso este documento no reproduce código de ninguno de ellos.** Lo que se extrae son
> **patrones y estadísticas**, y los ejemplos están escritos aquí desde cero para LTS 2026.

---

## Adopción de técnicas: cuántos de los 21 usan cada cosa

| Proyectos | Técnica | Lectura |
|---:|---|---|
| **21/21** | **Surfaces** | Universal. Cualquier proyecto serio acaba dibujando fuera de pantalla |
| **21/21** | **Estructuras `ds_*`** | Universal… y en gran parte **inercia histórica** (ver abajo) |
| **20/21** | **Máquina de estados** | Prácticamente obligatorio en cuanto hay un personaje |
| **19/21** | **Buffers** | Guardado, red y manipulación binaria |
| **19/21** | **Structs** | Ya adoptados de forma masiva |
| **17/21** | **`lerp`** | Suavizado de cámara, UI y movimiento |
| **16/21** | **JSON** | El formato de guardado por defecto en la práctica |
| **15/21** | **Cámara** (`camera_*`) | |
| **14/21** | **Shaders** | Mucho más común de lo que se suele suponer |
| **14/21** | Arrays modernos (`array_push`, `array_foreach`…) | |
| **11/21** | **Métodos estáticos** | Adopción a medias |
| **11/21** | **`delta_time`** | ⚠️ Menos de la mitad |
| 8/21 | Gestión de capas por código | |
| 6/21 | Red | |
| 5/21 | Partículas | |
| 4/21 | Tilemaps por código | |
| 4/21 | Colisión por ejes (`hsp`/`vsp`) | Bajo porque **la mayoría del corpus son herramientas y motores, no plataformas** |
| **1/21** | **Motor de físicas integrado** | ⚠️ **Prácticamente nadie lo usa** |

---

## Las cinco conclusiones que cambian cómo programas

### 1. El motor de físicas integrado está abandonado en la práctica

**1 de 21.** De más de un millón de líneas de GML en producción, el sistema `physics_*` de
GameMaker aparece en un solo proyecto.

**Qué hacer con eso:** si tu juego no es específicamente de físicas (cajas que ruedan, cuerdas,
ragdolls), **no actives las físicas de la room**. Lleva tú la velocidad y resuelve colisiones
por ejes. Es lo que hace el mundo real, y es la técnica que explica
[10 · Megaman X](../10%20-%20Cursos%20en%20español/08%20-%20Plataformas%20estilo%20Megaman%20X%20-%20apuntes%20de%20la%20serie%20de%20Altair.md#1--el-núcleo-colisión-por-ejes).

### 2. `delta_time` sigue siendo minoritario — y es una decisión, no un descuido

Solo **11 de 21**. La alternativa es fijar el juego a una tasa constante y contar en fotogramas.

**Cuándo cada uno:**

| Enfoque | Cuándo conviene |
|---|---|
| **Contar fotogramas** (sin `delta_time`) | Juegos de precisión: plataformas, lucha, bullet hell. La física es **reproducible** y los saltos siempre miden lo mismo |
| **`delta_time`** | Cuando el ritmo puede variar: interfaz, cámaras, animación, juegos con vsync variable o pantallas de 144 Hz |

Muchos proyectos hacen lo sensato: **fotogramas para la lógica, `delta_time` para lo visual.**

### 3. Las `ds_*` están en todas partes, pero es inercia

**21/21 usan `ds_list`/`ds_map`… y a la vez 19/21 usan structs y 14/21 arrays modernos.**
Conviven porque el código viejo no se reescribe.

> 🔺 **En código nuevo para LTS 2026:** usa **arrays y structs**. Se recolectan solos, se
> serializan con
> [`json_stringify`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/File_Handling/Encoding_And_Hashing/json_stringify.md)
> sin conversiones, y no hay que acordarse de destruirlos. Las `ds_*` **hay que liberarlas a
> mano** y son la causa clásica de fugas de memoria en GameMaker.
>
> Las `ds_*` siguen justificadas en dos casos: **`ds_grid`** (no hay equivalente moderno) y
> **`ds_priority`** para pathfinding A\*.

### 4. Los shaders no son cosa de expertos

**14 de 21** los usan. No es una técnica minoritaria: es equipamiento estándar para paletas,
contornos, transiciones y postprocesado.

Si te frenaba la barrera de entrada, en la biblioteca tienes
[`Shady.gml`](../11%20-%20Código%20descargado/_CATALOGO.md) (preprocesador con `#include`) y
varios shaders listos.

### 5. `with` es la instrucción más infrautilizada por los principiantes

**8 539 usos** en el corpus, la tercera construcción más frecuente después de `function` y
`array_length`. Los proyectos reales la usan constantemente, y los principiantes casi nunca.

```gml
// En vez de un bucle sobre todas las instancias…
for (var _i = 0; _i < instance_number(obj_enemigo); _i++) {
    var _e = instance_find(obj_enemigo, _i);
    _e.hp -= 10;
}

// …with hace lo mismo y además cambia el ámbito
with (obj_enemigo) hp -= 10;
```

Y lo que de verdad la hace imprescindible: **te mete dentro de la otra instancia**, que es como
se resuelven las colisiones precisas (`other` apunta a quien llamó). Ver
[07 · Eventos](../10%20-%20Cursos%20en%20español/07%20-%20Curso%20de%20eventos%20en%20v%C3%ADdeo%20-%20transcripci%C3%B3n%20estructurada.md).

---

## Las funciones más llamadas del corpus

| Llamadas | Función | Nota |
|---:|---|---|
| 16 180 | `function` | Declaraciones: el corpus está muy modularizado |
| 8 802 | `array_length` | |
| 8 539 | `with` | Ver arriba |
| 6 905 | `instance_create` | ⚠️ **Nombre antiguo.** Hoy: `instance_create_layer` / `_depth` |
| 5 111 | `instance_destroy` | |
| 4 518 | `draw_set_color` | |
| 4 212 | `instance_exists` | **Comprobar antes de usar** un handle guardado |
| 3 251 | `floor` | Redondeo para píxel perfecto |
| 2 748 | `array_push` | |
| 2 624 | `draw_sprite_ext` | La versión con escala, rotación, color y alfa |
| 1 657 | `place_meeting` | La colisión que de verdad se usa |
| 1 527 | `event_inherited` | **Herencia de objetos padre**, muy usada |
| 1 180 / 1 139 | `lengthdir_x` / `lengthdir_y` | Convertir ángulo + distancia en desplazamiento |

> 💡 **`instance_create` con 6 905 llamadas es un fósil:** desapareció en GameMaker Studio 2.
> Mide la edad del corpus, no lo que debes escribir. Si copias código de estos proyectos,
> **espera encontrar nombres que ya no existen** y compruébalos con
> `python3 "_indice/buscar.py" <función>`.

---

## Detalle por proyecto

| Proyecto | Líneas GML | Estados | Structs | `static` | `delta_time` | Shaders | Buffers |
|---|---:|:-:|:-:|:-:|:-:|:-:|:-:|
| `Pixel-Composer` | 342 319 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Pizza-Tower-EXtracted` | 155 830 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `ChapterMaster` | 136 506 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Mine-imator` | 98 840 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `FVM-Reborn` | 81 437 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `DeltaruneChinese` | 67 962 | ✅ | ✅ | — | — | ✅ | ✅ |
| `nt-recreated-public` | 66 691 | ✅ | ✅ | ✅ | — | — | ✅ |
| `Kirby-Soft-and-Wet` | 57 540 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `SpelunkyClassicHD` | 52 387 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `DyNode` | 45 471 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `tldr-engine` | 45 397 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `NoteBlockStudio` | 30 806 | — | ✅ | — | ✅ | — | ✅ |
| `MegamixEngine` | 25 329 | ✅ | ✅ | — | — | ✅ | — |
| `renex2-engine` | 20 255 | ✅ | ✅ | — | — | ✅ | ✅ |
| `Harmony-Framework` | 19 585 | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| `OrbinautFramework` | 19 054 | ✅ | ✅ | — | — | ✅ | ✅ |
| `Undertale-Engine-modded-by-Zhazha` | 16 966 | ✅ | ✅ | — | ✅ | — | ✅ |
| `HotlineMiami.gmx` | 15 394 | ✅ | — | — | — | — | — |
| `AM2R-Re-Splashed` | 14 486 | ✅ | — | — | — | — | ✅ |
| `Gang-Garrison-2` | 11 987 | ✅ | ✅ | — | — | — | ✅ |
| `UndertaleEngine` | 9 711 | ✅ | ✅ | — | — | — | ✅ |

---

## Qué proyecto mirar según lo que quieras aprender

| Quiero entender… | Mira… | Licencia |
|---|---|---|
| Una herramienta grande y bien organizada | `Pixel-Composer` (342 k líneas) | ✅ MIT |
| Un motor de plataformas de precisión | `OrbinautFramework` (Sonic) · `MegamixEngine` (Mega Man) | 🟡 sin licencia |
| Arquitectura de RPG por turnos | `tldr-engine` · `UndertaleEngine` | ✅ MIT |
| Multijugador en red | `Gang-Garrison-2` · `nt-recreated-public` | ✅ MPL / GPL |
| Estrategia con mucha simulación | `ChapterMaster` (136 k líneas) | 🟡 sin licencia |
| Aplicación de escritorio con GameMaker | `Mine-imator` · `NoteBlockStudio` | 🟡 / ✅ MIT |
| Cómo se hizo un juego comercial | `Pizza-Tower-EXtracted` | 🔴 **solo lectura** |

---

## Cómo repetir este análisis

El analizador está en el scratchpad de la sesión, pero es corto y se rehace en cinco minutos:
recorre cada `.gml`, cuenta llamadas con una expresión regular y marca técnicas con otra.

```sh
# ver qué proyectos usan una técnica concreta
grep -rl "physics_world_create" "11 - Código descargado/juegos_y_motores/" | head

# contar cuántas veces se llama a una función en todo el corpus
grep -rho "\bshader_set\b" "11 - Código descargado/" | wc -l
```

Y para buscar un patrón concreto con el buscador de la biblioteca:

```sh
python3 "_indice/buscar.py" --codigo "camera_set_view_pos"
```
