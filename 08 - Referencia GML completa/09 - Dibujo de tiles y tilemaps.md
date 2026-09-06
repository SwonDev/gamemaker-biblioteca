# 09 — Dibujo de tiles y tilemaps

> Referencia completa de GML para **GameMaker LTS 2026.0** (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
> Áreas: `Asset_Management/Rooms/Tile_Map_Layers/`, `Asset_Management/Tilsets/` y
> `Drawing/Sprites_And_Tiles/`.
> **46 funciones documentadas.**

---

## Índice

1. [Conceptos: tile set, tilemap y tile data](#conceptos-tile-set-tilemap-y-tile-data)
2. [Dibujo manual](#dibujo-manual)
3. [Obtención del tilemap desde una capa](#obtención-del-tilemap-desde-una-capa)
4. [Lectura y escritura de tiles](#lectura-y-escritura-de-tiles)
5. [Conversión entre píxeles y celdas](#conversión-entre-píxeles-y-celdas)
6. [Propiedades del tilemap](#propiedades-del-tilemap)
7. [Manipulación de tile data](#manipulación-de-tile-data)
8. [Máscaras de bits](#máscaras-de-bits)
9. [Animación y limpieza](#animación-y-limpieza)
10. [Máscara de colisión](#máscara-de-colisión)
11. [Información de tile sets](#información-de-tile-sets)
12. [Tabla resumen](#tabla-resumen)
13. [Fuentes](#fuentes)

---

## Conceptos: tile set, tilemap y tile data

| Concepto | Qué es |
|---|---|
| **Tile set** | El recurso gráfico que contiene todos los tiles (baldosas) disponibles |
| **Tile map** (tilemap) | Una **capa** de la room que organiza los tiles en una rejilla de celdas |
| **Tile data** | Un «bloque» de datos (hasta 19 bits utilizables) que describe un tile concreto: su índice, rotación, volteo, espejo y si está vacío |

Los tiles se dibujan **automáticamente** según los datos que contienen, el tile set usado y las
propiedades del tile map. El dibujo manual con `draw_tile` / `draw_tilemap` solo es necesario cuando
quieres controlar el orden o el destino.

**Estructura de los tile data:** los datos de un tile son un entero cuyos bits codifican:

- El **índice** del tile dentro del tile set.
- Bit de **rotación** (`tile_rotate`).
- Bit de **volteo** (`tile_flip`).
- Bit de **espejo** (`tile_mirror`).
- Bit de **vacío**.

---

## Dibujo manual

### `draw_tile(tileset, tiledata, frame, x, y)`
- **Devuelve:** `Real`
- **Qué hace:** dibuja un **tile individual** en la posición indicada de la room.
- **Argumentos:** `tileset` (asset de tile set), `tiledata` (los datos del tile), `frame` (número de
  frame para tiles animados; usa `0` para tiles sin animación), `x` e `y` (posición en la room).
- **Ejemplo:**
```gml
// Dibujar el tile 14 de un tile set, sin transformaciones, en la posición del objeto
var _datos = tile_set_index(0, 14);        // índice 14, resto a 0
draw_tile(tls_mundo, _datos, 0, x, y);

// Dibujar el mismo tile rotado y en espejo
var _datos2 = tile_set_index(0, 14);
_datos2 = tile_set_rotate(_datos2, true);
_datos2 = tile_set_mirror(_datos2, true);
draw_tile(tls_mundo, _datos2, 0, x + 32, y);
```
- **Notas / trampas:** recuerda que `tile_set_*` **devuelve** un tile data modificado; no modifica
  el valor in situ.

### `draw_tilemap(tilemap_element_id, x, y)`
- **Devuelve:** `N/A`
- **Qué hace:** dibuja un tile map **completo** en la posición indicada de la room.
- **Ejemplo:**
```gml
// Redibujar el tilemap del suelo por encima de todo (efecto de superposición)
var _lay = layer_get_id("Tiles_suelo");
var _map = layer_tilemap_get_id(_lay);
draw_tilemap(_map, 0, 0);
```
- **Notas / trampas:** ten en cuenta que dibujar dos veces el mismo tilemap duplica el coste de
  dibujo.

---

## Obtención del tilemap desde una capa

### `layer_tilemap_get_id(layer_id)`
- **Devuelve:** `Tile Map Element ID`
- **Qué hace:** devuelve el ID del elemento tile map de la capa indicada. Acepta el **handle de la
  capa o su nombre como cadena**.
- **Ejemplo:**
```gml
// Evento Create
var _lay = layer_get_id("Tiles_solido");
mapa_solido = layer_tilemap_get_id(_lay);
```

### `layer_tilemap_create(layer_id, x, y, tileset, width, height)`
- **Devuelve:** `Tile Map Element ID`
- **Qué hace:** crea un tile map nuevo en la capa indicada.
- **Argumentos:** `layer_id` (handle o nombre), `x` / `y` (posición en la room), `tileset` (asset de
  tile set), `width` / `height` (tamaño **en celdas**).
- **Ejemplo:**
```gml
// Crear una capa de tiles nueva para una mazmorra generada proceduralmente
var _capa = layer_create(1000, "Tiles_generados");
var _ancho_celdas = 40;
var _alto_celdas  = 30;

mapa = layer_tilemap_create(_capa, 0, 0, tls_masmorra, _ancho_celdas, _alto_celdas);
```

### `layer_tilemap_exists(layer_id, tilemap_element_id)`
- **Devuelve:** `Boolean`
- **Qué hace:** comprueba si el elemento tile map existe en la capa indicada.
- **Ejemplo:**
```gml
if (layer_tilemap_exists(_capa, mapa))
{
    show_debug_message("El tilemap sigue ahí");
}
```

### `layer_tilemap_destroy(tilemap_element_id)`
- **Devuelve:** `N/A`
- **Qué hace:** destruye el elemento tile map indicado.
- **Ejemplo:**
```gml
// Evento Cleanup / al cambiar de nivel
layer_tilemap_destroy(mapa);
```

### `layer_tilemap_get_colmask(tilemap_element_id)`
- **Devuelve:** `Sprite Asset`
- **Qué hace:** devuelve el sprite que se usa como **máscara de colisión** del tile map.
- **Ejemplo:**
```gml
var _mascara = layer_tilemap_get_colmask(mapa);
```

### `layer_tilemap_set_colmask(tilemap_element_id, sprite)`
- **Devuelve:** `N/A`
- **Qué hace:** fija el sprite que se usará como máscara de colisión del tile map.
- **Ejemplo:**
```gml
// Usar un sprite propio como máscara de colisión del nivel
layer_tilemap_set_colmask(mapa, spr_mascara_nivel);
```

---

## Lectura y escritura de tiles

### `tilemap_get(tilemap_element_id, cell_x, cell_y)`
- **Devuelve:** `Tile Data` (o `-1` si hay error)
- **Qué hace:** devuelve los datos del tile en la **celda** indicada.
- **Ejemplo:**
```gml
// Comprobar si la celda bajo el jugador es sólida
var _celda_x = tilemap_get_cell_x_at_pixel(mapa, x, y);
var _celda_y = tilemap_get_cell_y_at_pixel(mapa, x, y);
var _datos   = tilemap_get(mapa, _celda_x, _celda_y);

if (!tile_get_empty(_datos)) show_debug_message("¡Sólido!");
```

### `tilemap_set(tilemap_element_id, tiledata, xcell, ycell)`
- **Devuelve:** `Boolean`
- **Qué hace:** fija los datos del tile en la celda indicada.
- **Ejemplo:**
```gml
// Colocar un tile de suelo en la celda (5, 8)
var _datos = tile_set_index(0, 3);
tilemap_set(mapa, _datos, 5, 8);
```

### `tilemap_get_at_pixel(tilemap_element_id, x, y)`
- **Devuelve:** `Tile Data` (o `-1` si hay error)
- **Qué hace:** devuelve los datos del tile en la posición indicada, medida en **píxeles de la room**.
- **Ejemplo:**
```gml
// Detección de colisión por tile en la posición del jugador
var _datos = tilemap_get_at_pixel(mapa_solido, x, y + 1);
var _solido = !tile_get_empty(_datos);
```

### `tilemap_set_at_pixel(tilemap_element_id, tiledata, x, y)`
- **Devuelve:** `Boolean`
- **Qué hace:** fija los datos del tile en la posición indicada, en **píxeles de la room**.
- **Ejemplo:**
```gml
// Destruir el tile que hay justo donde impacta la bala
tilemap_set_at_pixel(mapa, 0, x, y);
```
- **Notas / trampas:** es más cómoda que `tilemap_set` pero ligeramente más costosa, porque debe
  convertir píxeles a celdas.

---

## Conversión entre píxeles y celdas

### `tilemap_get_cell_x_at_pixel(tilemap_element_id, x, y)`
- **Devuelve:** `Real` (posición de celda en el eje X, o `-1` si hay error)
- **Qué hace:** convierte una posición en píxeles de la room a la **columna de celda** que le
  corresponde.
- **Ejemplo:**
```gml
var _celda_x = tilemap_get_cell_x_at_pixel(mapa, mouse_x, mouse_y);
```

### `tilemap_get_cell_y_at_pixel(tilemap_element_id, x, y)`
- **Devuelve:** `Real` (posición de celda en el eje Y, o `-1` si hay error)
- **Qué hace:** convierte una posición en píxeles de la room a la **fila de celda** que le
  corresponde.
- **Ejemplo:**
```gml
// Editor de nivel en tiempo real: pintar tile donde hace clic el ratón
if (mouse_check_button(mb_left))
{
    var _cx = tilemap_get_cell_x_at_pixel(mapa, mouse_x, mouse_y);
    var _cy = tilemap_get_cell_y_at_pixel(mapa, mouse_x, mouse_y);
    tilemap_set(mapa, tile_set_index(0, tile_seleccionado), _cx, _cy);
}
```

---

## Propiedades del tilemap

### `tilemap_get_width(tilemap_element_id)`
- **Devuelve:** `Real` (en celdas)
- **Qué hace:** devuelve la anchura del tile map.
- **Ejemplo:**
```gml
var _ancho = tilemap_get_width(mapa);
```

### `tilemap_get_height(tilemap_element_id)`
- **Devuelve:** `Real` (en celdas)
- **Qué hace:** devuelve la altura del tile map.
- **Ejemplo:**
```gml
var _alto = tilemap_get_height(mapa);
```

### `tilemap_set_width(tilemap_element_id, width)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la anchura del tile map **en celdas**.
- **Ejemplo:**
```gml
tilemap_set_width(mapa, 64);
```

### `tilemap_set_height(tilemap_element_id, height)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la altura del tile map **en celdas**.
- **Ejemplo:**
```gml
tilemap_set_height(mapa, 48);
```

### `tilemap_get_tileset(tilemap_element_id)`
- **Devuelve:** `Tile Set Asset`
- **Qué hace:** devuelve el tile set que usa el tile map.
- **Ejemplo:**
```gml
var _tls = tilemap_get_tileset(mapa);
```

### `tilemap_tileset(tilemap_element_id, tileset_index)`
- **Devuelve:** `N/A`
- **Qué hace:** cambia el tile set que usa el tile map.
- **Ejemplo:**
```gml
// Cambiar de tile set para la conversión de verano a invierno
tilemap_tileset(mapa, tls_mundo_nieve);
```

### `tilemap_get_tile_width(tilemap_element_id)`
- **Devuelve:** `Real` (píxeles)
- **Qué hace:** devuelve la anchura de **una celda** del tile map.
- **Ejemplo:**
```gml
var _ancho_celda = tilemap_get_tile_width(mapa);
```

### `tilemap_get_tile_height(tilemap_element_id)`
- **Devuelve:** `Real` (píxeles)
- **Qué hace:** devuelve la altura de **una celda** del tile map.
- **Ejemplo:**
```gml
var _alto_celda = tilemap_get_tile_height(mapa);
```

### `tilemap_x(tilemap_element_id, x)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la posición **X** del tile map dentro de la room.
- **Ejemplo:**
```gml
// Scroll de parallax del tilemap de fondo
tilemap_x(mapa_fondo, camara_x * 0.5);
```

### `tilemap_y(tilemap_element_id, y)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la posición **Y** del tile map dentro de la room.
- **Ejemplo:**
```gml
tilemap_y(mapa_fondo, camara_y * 0.5);
```

---

## Manipulación de tile data

Todas estas funciones toman un bloque de tile data y **devuelven** una versión modificada. Después
debes aplicarla con `tilemap_set()`.

### `tile_get_index(tiledata)` / `tile_set_index(tiledata, index)`
- **Devuelven:** `Real` / `Tile Data`
- **Qué hacen:** leen o fijan el **índice** del tile: la posición del tile dentro de la imagen del
  tile set.
- **Ejemplo:**
```gml
var _datos = tilemap_get(mapa, 3, 4);
var _indice = tile_get_index(_datos);            // leer
_datos = tile_set_index(_datos, 20);             // cambiar al tile 20
tilemap_set(mapa, _datos, 3, 4);
```

### `tile_get_empty(tiledata)` / `tile_set_empty(tiledata)`
- **Devuelven:** `Boolean` / `Tile Data`
- **Qué hacen:** comprueban o fijan si el tile está **vacío**.
- **Ejemplo:**
```gml
// Borrar todos los tiles no vacíos del mapa
for (var _i = 0; _i < tilemap_get_width(mapa); _i++)
{
    for (var _j = 0; _j < tilemap_get_height(mapa); _j++)
    {
        var _datos = tilemap_get(mapa, _i, _j);
        if (!tile_get_empty(_datos))
        {
            _datos = tile_set_empty(_datos);
            tilemap_set(mapa, _datos, _i, _j);
        }
    }
}
```

### `tile_get_rotate(tiledata)` / `tile_set_rotate(tiledata, rotate)`
- **Devuelven:** `Boolean` / `Tile Data`
- **Qué hacen:** comprueban o fijan si el tile está **rotado 90 grados**.
- **Ejemplo:**
```gml
var _datos = tilemap_get(mapa, 2, 2);
_datos = tile_set_rotate(_datos, true);
tilemap_set(mapa, _datos, 2, 2);
```

### `tile_get_flip(tiledata)` / `tile_set_flip(tiledata, flip)`
- **Devuelven:** `Boolean` / `Tile Data`
- **Qué hacen:** comprueban o fijan si el tile está **volteado**.
- **Ejemplo:**
```gml
var _datos = tilemap_get(mapa, 2, 2);
if (!tile_get_flip(_datos))
{
    _datos = tile_set_flip(_datos, true);
    tilemap_set(mapa, _datos, 2, 2);
}
```

### `tile_get_mirror(tiledata)` / `tile_set_mirror(tiledata, mirror)`
- **Devuelven:** `Boolean` / `Tile Data`
- **Qué hacen:** comprueban o fijan si el tile está **en espejo**.
- **Ejemplo:**
```gml
// Generar variedad visual: espejo aleatorio en cada tile de césped
var _datos = tilemap_get(mapa, _i, _j);
_datos = tile_set_mirror(_datos, irandom(1) == 1);
tilemap_set(mapa, _datos, _i, _j);
```

---

## Máscaras de bits

El enmascarado por bits (*bit masking*) es una **característica avanzada** que permite usar bits del
bloque de tile data para tus propios fines.

**La idea:** si tienes un tile set pequeño de 16 × 16 tiles, eso son 256 tiles distintos, que solo
consumen **8 bits** del índice (de los **19 bits** disponibles). Los bits restantes pueden
«enmascararse» y usarse para guardar valores adicionales.

En la práctica, **la máscara se combina con AND contra los tile data cuando el tile map se dibuja**,
así que **no afecta al resto de funcionalidad**: los bits que no están en la máscara se ignoran al
dibujar, pero puedes leerlos y escribirlos tú.

**Constantes de bits de transformación:** `tile_mirror`, `tile_flip`, `tile_rotate`.

### `tilemap_set_global_mask(mask)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la máscara de bits **para todos los tile maps del juego**.
- **Ejemplo:**
```gml
// Máscara global de 8 bits para el índice, conservando espejo, volteo y rotación
var _mascara = tile_mirror | tile_flip | tile_rotate | 255;
tilemap_set_global_mask(_mascara);

// Equivalente en binario explícito: 8 bits de índice (0b11111111)
var _transform = tile_mirror | tile_flip | tile_rotate;
tilemap_set_global_mask(_transform | 0b11111111);
```
- **Notas / trampas — IMPORTANTE:**
  Debes asegurarte de tener **al menos los mismos bits activos en la máscara global** que en las
  máscaras por tile map (`tilemap_set_mask`), porque las dos máscaras se combinan con AND. Por
  ejemplo, una máscara global de `0b0000111111111101` **forzará el bit 1 a 0** en cualquier máscara
  de tile map, con independencia de que ese bit esté activo ahí.

### `tilemap_get_global_mask()`
- **Devuelve:** `Real` (el valor de la máscara global, o `-1` si hay error)
- **Qué hace:** devuelve la máscara de bits global actual.
- **Ejemplo:**
```gml
var _mascara_global = tilemap_get_global_mask();
```

### `tilemap_set_mask(tilemap_element_id, mask)`
- **Devuelve:** `N/A`
- **Qué hace:** fija la máscara de bits **de un tile map concreto**.
- **Ejemplo:**
```gml
// Este tilemap usa un tile set muy pequeño: solo 4 bits de índice (0b1111)
var _transform = tile_mirror | tile_flip | tile_rotate;
var _mascara_pequena = _transform | 0b1111;
tilemap_set_mask(mapa_decorativo, _mascara_pequena);
```

### `tilemap_get_mask(tilemap_element_id)`
- **Devuelve:** `Real` (la máscara del tile map, o `-1` si hay error)
- **Qué hace:** devuelve la máscara de bits del tile map indicado.
- **Ejemplo:**
```gml
if (tilemap_get_mask(mapa) == -1) show_debug_message("Sin máscara propia");
```

**Ejemplo completo — usar un bit libre como marca de «sólido»:**
```gml
// Evento Create: reservar el bit 9 para «sólido»
var _transform = tile_mirror | tile_flip | tile_rotate;
tilemap_set_global_mask(_transform | 0b11111111);

const BIT_SOLIDO = (1 << 9);

// Marcar un tile como sólido
var _datos = tilemap_get(mapa, 5, 5);
_datos |= BIT_SOLIDO;               // activar el bit
tilemap_set(mapa, _datos, 5, 5);

// Consultarlo después: rapidísimo
function tile_es_solido(_mapa, _cx, _cy)
{
    var _datos = tilemap_get(_mapa, _cx, _cy);
    return (_datos & BIT_SOLIDO) != 0;
}
```

---

## Animación y limpieza

### `tilemap_get_frame(tilemap_element_id)`
- **Devuelve:** `Real` (entre `0` inclusive y el número máximo de frames de animación, exclusivo)
- **Qué hace:** devuelve el **índice de frame** actual de la animación del tile map.
- **Ejemplo:**
```gml
// Sincronizar un efecto con el frame de animación del agua
var _frame = tilemap_get_frame(mapa_agua);
if (_frame == 0) reproducir_sonido_agua();
```

### `tilemap_clear(tilemap_element_id, tiledata)`
- **Devuelve:** `N/A`
- **Qué hace:** rellena **todo el tile map** con los tile data indicados. Es la forma de vaciarlo o
  inicializarlo por completo.
- **Ejemplo:**
```gml
// Vaciar el mapa por completo
tilemap_clear(mapa, 0);

// Rellenar todo con el tile 1
tilemap_clear(mapa, tile_set_index(0, 1));
```
- **Notas / trampas:** es mucho más rápido que recorrer todas las celdas con `tilemap_set`.

---

## Máscara de colisión

### `layer_tilemap_get_colmask(tilemap_element_id)`
- **Devuelve:** `Sprite Asset`
- **Qué hace:** devuelve el sprite asignado como máscara de colisión del tile map.
- **Ejemplo:**
```gml
var _col = layer_tilemap_get_colmask(mapa);
```

### `layer_tilemap_set_colmask(tilemap_element_id, sprite)`
- **Devuelve:** `N/A`
- **Qué hace:** asigna un sprite como máscara de colisión del tile map.
- **Ejemplo:**
```gml
// Colisión personalizada para la mazmorra generada
layer_tilemap_set_colmask(mapa, spr_mascara_masmorra);
```
- **Notas / trampas:** la máscara de colisión permite definir exactamente qué partes de cada tile son
  sólidas, en lugar de usar el tile completo.

---

## Información de tile sets

### `tileset_get_texture(tileset)`
- **Devuelve:** `Texture`
- **Qué hace:** devuelve la textura del tile set, para usarla en primitivas o shaders.
- **Ejemplo:**
```gml
var _tex = tileset_get_texture(tls_mundo);
texture_set_stage(u_sampler_tiles, _tex);
```

### `tileset_get_uvs(tileset)`
- **Devuelve:** `Array`
- **Qué hace:** devuelve las coordenadas UV del tile set dentro de su página de textura.
- **Ejemplo:**
```gml
var _uv = tileset_get_uvs(tls_mundo);
var _u0 = _uv[0], _v0 = _uv[1], _u1 = _uv[2], _v1 = _uv[3];
```
- **Notas / trampas:** imprescindible si quieres mapear un tile set sobre un **vertex buffer**,
  donde `(0,0)`–`(1,1)` cubre la página de textura completa (ver archivo **07**).

### `tileset_get_name(tileset)`
- **Devuelve:** `String`
- **Qué hace:** devuelve el nombre del recurso de tile set.
- **Ejemplo:**
```gml
show_debug_message($"Tile set: {tileset_get_name(tls_mundo)}");
```

### `tileset_get_info(tileset)`
- **Devuelve:** `Struct`
- **Qué hace:** devuelve información completa del tile set en forma de struct.
- **Ejemplo:**
```gml
var _info = tileset_get_info(tls_mundo);
show_debug_message(_info);
```

---

## Tabla resumen

### Dibujo (2)

| Función | Devuelve |
|---|---|
| `draw_tile(tileset, tiledata, frame, x, y)` | `Real` |
| `draw_tilemap(tilemap_element_id, x, y)` | `N/A` |

### Capas (6)

| Función | Devuelve |
|---|---|
| `layer_tilemap_get_id(layer_id)` | `Tile Map Element ID` |
| `layer_tilemap_create(layer_id, x, y, tileset, width, height)` | `Tile Map Element ID` |
| `layer_tilemap_exists(layer_id, tilemap_element_id)` | `Boolean` |
| `layer_tilemap_destroy(tilemap_element_id)` | `N/A` |
| `layer_tilemap_get_colmask(tilemap_element_id)` | `Sprite Asset` |
| `layer_tilemap_set_colmask(tilemap_element_id, sprite)` | `N/A` |

### Lectura y escritura (4)

| Función | Devuelve |
|---|---|
| `tilemap_get(tilemap_element_id, cell_x, cell_y)` | `Tile Data` |
| `tilemap_set(tilemap_element_id, tiledata, xcell, ycell)` | `Boolean` |
| `tilemap_get_at_pixel(tilemap_element_id, x, y)` | `Tile Data` |
| `tilemap_set_at_pixel(tilemap_element_id, tiledata, x, y)` | `Boolean` |

### Conversión (2)

| Función | Devuelve |
|---|---|
| `tilemap_get_cell_x_at_pixel(tilemap_element_id, x, y)` | `Real` |
| `tilemap_get_cell_y_at_pixel(tilemap_element_id, x, y)` | `Real` |

### Propiedades (10)

| Función | Devuelve |
|---|---|
| `tilemap_get_width(tilemap_element_id)` | `Real` |
| `tilemap_get_height(tilemap_element_id)` | `Real` |
| `tilemap_set_width(tilemap_element_id, width)` | `N/A` |
| `tilemap_set_height(tilemap_element_id, height)` | `N/A` |
| `tilemap_get_tileset(tilemap_element_id)` | `Tile Set Asset` |
| `tilemap_tileset(tilemap_element_id, tileset_index)` | `N/A` |
| `tilemap_get_tile_width(tilemap_element_id)` | `Real` |
| `tilemap_get_tile_height(tilemap_element_id)` | `Real` |
| `tilemap_x(tilemap_element_id, x)` | `N/A` |
| `tilemap_y(tilemap_element_id, y)` | `N/A` |

### Tile data (10)

| Función | Devuelve |
|---|---|
| `tile_get_index(tiledata)` / `tile_set_index(tiledata, index)` | `Real` / `Tile Data` |
| `tile_get_empty(tiledata)` / `tile_set_empty(tiledata)` | `Boolean` / `Tile Data` |
| `tile_get_rotate(tiledata)` / `tile_set_rotate(tiledata, rotate)` | `Boolean` / `Tile Data` |
| `tile_get_flip(tiledata)` / `tile_set_flip(tiledata, flip)` | `Boolean` / `Tile Data` |
| `tile_get_mirror(tiledata)` / `tile_set_mirror(tiledata, mirror)` | `Boolean` / `Tile Data` |

### Máscaras de bits (4)

| Función | Devuelve |
|---|---|
| `tilemap_set_global_mask(mask)` | `N/A` |
| `tilemap_get_global_mask()` | `Real` |
| `tilemap_set_mask(tilemap_element_id, mask)` | `N/A` |
| `tilemap_get_mask(tilemap_element_id)` | `Real` |

### Animación y limpieza (2)

| Función | Devuelve |
|---|---|
| `tilemap_get_frame(tilemap_element_id)` | `Real` |
| `tilemap_clear(tilemap_element_id, tiledata)` | `N/A` |

### Tile sets (4)

| Función | Devuelve |
|---|---|
| `tileset_get_texture(tileset)` | `Texture` |
| `tileset_get_uvs(tileset)` | `Array` |
| `tileset_get_name(tileset)` | `String` |
| `tileset_get_info(tileset)` | `Struct` |

**Total: 44 funciones documentadas** (2 + 6 + 4 + 2 + 10 + 10 + 4 + 2 + 4).

---

## Fuentes

- Sprites And Tiles — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/Sprites_And_Tiles.htm
- `draw_tile` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_tile.htm
- `draw_tilemap` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_tilemap.htm
- Tile Map Layers — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/Tile_Map_Layers.htm
- `layer_tilemap_get_id` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/layer_tilemap_get_id.htm
- `layer_tilemap_create` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/layer_tilemap_create.htm
- `layer_tilemap_exists` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/layer_tilemap_exists.htm
- `layer_tilemap_destroy` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/layer_tilemap_destroy.htm
- `layer_tilemap_get_colmask` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/layer_tilemap_get_colmask.htm
- `layer_tilemap_set_colmask` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/layer_tilemap_set_colmask.htm
- `tilemap_get` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get.htm
- `tilemap_set` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_set.htm
- `tilemap_get_at_pixel` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_at_pixel.htm
- `tilemap_set_at_pixel` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_set_at_pixel.htm
- `tilemap_get_cell_x_at_pixel` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_cell_x_at_pixel.htm
- `tilemap_get_cell_y_at_pixel` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_cell_y_at_pixel.htm
- `tilemap_get_width` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_width.htm
- `tilemap_get_height` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_height.htm
- `tilemap_set_width` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_set_width.htm
- `tilemap_set_height` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_set_height.htm
- `tilemap_get_tileset` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_tileset.htm
- `tilemap_tileset` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_tileset.htm
- `tilemap_get_tile_width` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_tile_width.htm
- `tilemap_get_tile_height` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_tile_height.htm
- `tilemap_x` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_x.htm
- `tilemap_y` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_y.htm
- `tilemap_clear` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_clear.htm
- `tilemap_get_frame` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_frame.htm
- `tilemap_set_global_mask` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_set_global_mask.htm
- `tilemap_get_global_mask` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_global_mask.htm
- `tilemap_set_mask` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_set_mask.htm
- `tilemap_get_mask` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_mask.htm
- `tile_get_index` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tile_get_index.htm
- `tile_set_index` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tile_set_index.htm
- `tile_get_empty` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tile_get_empty.htm
- `tile_set_empty` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tile_set_empty.htm
- `tile_get_rotate` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tile_get_rotate.htm
- `tile_set_rotate` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tile_set_rotate.htm
- `tile_get_flip` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tile_get_flip.htm
- `tile_set_flip` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tile_set_flip.htm
- `tile_get_mirror` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tile_get_mirror.htm
- `tile_set_mirror` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tile_set_mirror.htm
- `tileset_get_texture` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Tilsets/tileset_get_texture.htm
- `tileset_get_uvs` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Tilsets/tileset_get_uvs.htm
- `tileset_get_name` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Tilsets/tileset_get_name.htm
- `tileset_get_info` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Tilsets/tileset_get_info.htm
