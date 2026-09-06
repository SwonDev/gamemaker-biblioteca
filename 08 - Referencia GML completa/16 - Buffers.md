# 16 · Buffers en GML

> Referencia exhaustiva de **GameMaker LTS 2026** (IDE 2026.0.0.16 · Runtime 2026.0.0.23).

> Todas las firmas han sido verificadas contra el manual oficial LTS.

---

## Qué es un buffer

Un **buffer** es una región de memoria física que se usa para guardar datos de forma
temporal mientras se mueven de un sitio a otro o se manipulan. Es la herramienta
fundamental para:

- **Serializar** el estado de una partida a binario.
- Enviar y recibir **paquetes de red**.
- Intercambiar datos con **extensiones** y shaders.
- Volcar el contenido de una **surface**.

### Reglas que hay que tener claras

1. Al crear un buffer se **rellena por completo con ceros**.
2. El argumento `size` siempre se expresa en **bytes**.
3. El argumento `alignment` indica cómo se almacenan los datos: con alineación 4, escribir
   un byte y luego otro deja la posición en **5**, porque el segundo byte se ha rellenado
   hasta el múltiplo de 4.
4. Algunas funciones **crean** un buffer nuevo (`buffer_load`, `buffer_compress`,
   `buffer_base64_decode`…). Esos buffers **también** hay que destruirlos.
5. Los buffers **no** los recolecta el recolector de basura: hay que llamar a
   `buffer_delete` y, después, poner la variable a `-1`.
6. ⚠ **No se pueden crear buffers de 2 GiB (2.147.483.648 bytes) o más.**

---

## Tipos de buffer (constantes para `buffer_create`)

| Constante | Comportamiento |
| --- | --- |
| `buffer_fixed` | Tamaño fijo en bytes: se fija al crearlo y ya no se puede cambiar. |
| `buffer_grow` | Crece dinámicamente a medida que añades datos. Empieza con un tamaño aproximado y se expande si te pasas. |
| `buffer_wrap` | Al llegar al final, la escritura **vuelve al principio** sobrescribiendo lo que había. |
| `buffer_fast` | Buffer «desnudo» extremadamente rápido. Solo admite el tipo `buffer_u8` y debe estar alineado a **1 byte**. |
| `buffer_vbuffer` | Buffer especial para vértices, usado por la construcción de primitivas. |
| `buffer_network` | Buffer optimizado para envío por red (lo usan las funciones de networking). |

### Alineación recomendada según el tipo de dato

| Dato | Alineación |
| --- | --- |
| Strings | 1 byte |
| Enteros de 8 bits (con o sin signo) | cualquiera (pero 1 si es `buffer_fast`) |
| Enteros de 16 bits | 2 bytes |
| Enteros de 32 bits | 4 bytes |
| Float de 16 bits | 2 bytes |
| Float de 32 bits | 4 bytes |
| Float de 64 bits | 8 bytes |

> **Cuando dudes, usa alineación 1.** Una alineación incorrecta puede arruinar el
> rendimiento o provocar errores.

---

## Tipos de datos (constantes para `buffer_write` / `buffer_read`)

| Constante | Descripción |
| --- | --- |
| `buffer_u8` | Entero de 8 bits **sin** signo: de 0 a 255. |
| `buffer_s8` | Entero de 8 bits **con** signo: de -128 a 127. |
| `buffer_u16` | Entero de 16 bits sin signo: de 0 a 65.535. |
| `buffer_s16` | Entero de 16 bits con signo: de -32.768 a 32.767. |
| `buffer_u32` | Entero de 32 bits sin signo: de 0 a 4.294.967.295. |
| `buffer_s32` | Entero de 32 bits con signo: de -2.147.483.648 a 2.147.483.647. |
| `buffer_u64` | Entero de 64 bits sin signo: de 0 a 18.446.744.073.709.551.615. |
| `buffer_f16` | Float de 16 bits: ±65.504. |
| `buffer_f32` | Float de 32 bits: ±16.777.216. |
| `buffer_f64` | Float de 64 bits (doble precisión). |
| `buffer_bool` | Booleano: 1 o 0. Ocupa **un byte**. |
| `buffer_string` | String de cualquier tamaño, **con** carácter nulo final. |
| `buffer_text` | String de cualquier tamaño, **sin** carácter nulo final. |

> Los tipos de varios bytes se leen y escriben con el **endianness** de la plataforma:
> *little endian* en todas las plataformas que soporta GameMaker.

---

## Constantes de posicionamiento (`buffer_seek`)

| Constante | Significado |
| --- | --- |
| `buffer_seek_start` | El principio del buffer. |
| `buffer_seek_relative` | Posición relativa a la actual de lectura/escritura. |
| `buffer_seek_end` | El final del buffer. |

---

## Creación, consulta y destrucción


### `buffer_exists(buffer)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el identificador corresponde a un buffer válido.
- **Ejemplo:**

```gml
if (buffer_exists(buff))
{
    buffer_delete(buff);
}
```

### `buffer_create(size, type, alignment)`

- **Devuelve:** Buffer
- **Qué hace:** Crea un buffer del tamaño y tipo indicados y devuelve su **id**. El parámetro `alignment` fija la alineación de bytes con la que se escribirán los datos.
- **Ejemplo:**

```gml
player_buffer = buffer_create(16384, buffer_fixed, 2);
```

- **Notas:** ⚠ No se pueden crear buffers de **2 GiB** (2.147.483.648 bytes) o más. Tras destruir un buffer, pon su variable a `-1`.

### `buffer_delete(buffer)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Destruye el buffer y **libera su memoria**. Es obligatorio: los buffers **no** los recolecta el recolector de basura.
- **Ejemplo:**

```gml
buffer_delete(player_buffer);
player_buffer = -1;
```

- **Notas:** Obligatorio. Los buffers **no** se recolectan solos. Tras destruirlo, asigna `-1` a la variable.

### `buffer_create_from_vertex_buffer(vertex_buffer, type, alignment)`

- **Devuelve:** Buffer
- **Qué hace:** Crea un buffer a partir de un **vertex buffer** existente, copiando todos sus vértices.
- **Ejemplo:**

```gml
player_buffer = buffer_create_from_vertex_buffer(model_buffer, buffer_grow, 1);
```

### `buffer_create_from_vertex_buffer_ext(vertex_buffer, type, alignment, start_vertex, num_vertices)`

- **Devuelve:** Buffer
- **Qué hace:** Igual que `buffer_create_from_vertex_buffer`, pero copiando solo un rango de vértices (`start_vertex`, `num_vertices`).
- **Ejemplo:**

```gml
var _v_num = vertex_get_number(model_buff);
player_buffer = buffer_create_from_vertex_buffer_ext(model_buffer, buffer_grow, 1, 0, _v_num - 1);
```

### `buffer_get_type(buffer)`

- **Devuelve:** Buffer Type Constant
- **Qué hace:** Devuelve el **tipo** del buffer (`buffer_fixed`, `buffer_grow`, `buffer_wrap`, `buffer_fast`…).
- **Ejemplo:**

```gml
type = buffer_get_type(buff);
```

### `buffer_get_alignment(buffer)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la **alineación de bytes** con la que se creó el buffer.
- **Ejemplo:**

```gml
alignment = buffer_get_alignment(buff);
```

### `buffer_get_address(buffer)`

- **Devuelve:** Pointer
- **Qué hace:** Devuelve la **dirección de memoria** del buffer como puntero. Se usa sobre todo con extensiones y con `buffer_get_surface`.
- **Ejemplo:**

```gml
var _address = buffer_get_address(buff_model);
var _end_address = _address + buffer_get_size(buff_model);
```

- **Notas:** La dirección puede cambiar si el buffer es de tipo `buffer_grow` y se redimensiona.

### `buffer_get_size(buffer)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el tamaño **total** del buffer en bytes, reservado en memoria.
- **Ejemplo:**

```gml
var _size = buffer_get_size(player_data);
var _temp = buffer_create(_size, buffer_fixed, 0);
```

### `buffer_get_used_size(buffer)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el tamaño **realmente usado** del buffer, es decir, cuántos bytes se han escrito.
- **Ejemplo:**

```gml
var _buffer = buffer_create(16, buffer_grow, 1);
repeat(6)
{
    buffer_write(_buffer, buffer_f32, 4);
}
var _used_size = buffer_get_used_size(_buffer);
var _size = buffer_get_size(_buffer);

show_debug_message($"size: {_size}, used: {_used_size}");
```

### `buffer_set_used_size(buffer, size)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Fija a mano el tamaño usado del buffer. Solo se puede reducir respecto al tamaño reservado.
- **Ejemplo:**

```gml
buffer_write(_bufferAddress, buffer_u8, 1);
buffer_write(_bufferAddress, buffer_u8, 2);
buffer_write(_bufferAddress, buffer_u16, 400);

buffer_set_used_size(_bufferAddress, 4);
```

### `buffer_resize(buffer, newsize)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Cambia el tamaño reservado del buffer. Al agrandarlo, los bytes nuevos se rellenan con `0`.
- **Ejemplo:**

```gml
if (buffer_get_size(buff) < 16384)
{
    buffer_resize(buff, 16384);
}
```

### `buffer_sizeof(type)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántos **bytes** ocupa el tipo de datos indicado. Muy útil para calcular offsets a mano.
- **Ejemplo:**

```gml
var _bytesize = 12 * buffer_sizeof(buffer_u8);
buff = buffer_create(_bytesize, buffer_fixed, 1);
```

- **Notas:** Para `buffer_string` el tamaño depende de la longitud del string.

---

## Lectura y escritura


### `buffer_write(buffer, type, value)`

- **Devuelve:** Real (0 if success) or Buffer Error Constant (if it fails)
- **Qué hace:** Escribe un valor del tipo indicado en la posición actual del buffer y **avanza** la posición. Devuelve `0` si todo va bien o una constante de error.
- **Ejemplo:**

```gml
buffer_seek(buff, buffer_seek_start, 0);
buffer_write(buff, buffer_s16, 0);
buffer_write(buff, buffer_s16, x);
buffer_write(buff, buffer_s16, y);
```

- **Notas:** Los tipos de varios bytes usan el **endianness de la plataforma**: *little endian* en todas las plataformas que soporta GameMaker.

### `buffer_read(buffer, type)`

- **Devuelve:** Real, Boolean or String
- **Qué hace:** Lee un valor del tipo indicado desde la posición actual del buffer y **avanza** la posición.
- **Ejemplo:**

```gml
buffer = buffer_create(10240, buffer_grow, 1);

// buffer_seek(buffer, buffer_seek_start, 0);
buffer_write(buffer, buffer_string, "Hello World");

buffer_seek(buffer, buffer_seek_start, 0);
result = buffer_read(buffer, buffer_string);

show_debug_message("Result = " + result);
```

- **Notas:** Debes leer los tipos **en el mismo orden** en que los escribiste, o los datos saldrán corruptos.

### `buffer_peek(buffer, offset, type)`

- **Devuelve:** Real, Boolean, String or undefined (if it fails)
- **Qué hace:** Lee un valor del tipo indicado desde una posición concreta, **sin mover** la posición de lectura/escritura.
- **Ejemplo:**

```gml
var _red = buffer_peek(buff, 1, buffer_u8);
var _green = buffer_peek(buff, 2, buffer_u8);
var _blue = buffer_peek(buff, 3, buffer_u8);
image_blend = make_colour_rgb(_red, _green, _blue);
```

### `buffer_poke(buffer, offset, type, value)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Escribe un valor del tipo indicado en una posición concreta, **sin mover** la posición de lectura/escritura.
- **Ejemplo:**

```gml
buffer_poke(buff, 3, buffer_u8, colour_get_blue(image_blend));
```

### `buffer_fill(buffer, offset, type, value, size)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Rellena una región del buffer repitiendo el mismo valor del tipo indicado.
- **Ejemplo:**

```gml
map_buffer = buffer_create(16384, buffer_fixed, 0);
buffer_fill(map_buffer, 0, buffer_u16, 0, 16384);
```

### `buffer_seek(buffer, base, offset)`

- **Devuelve:** Real (the new seek position)
- **Qué hace:** Mueve la posición de lectura/escritura del buffer, relativa al principio, al final o a la posición actual. Devuelve la nueva posición.
- **Ejemplo:**

```gml
buffer_seek(buff, buffer_seek_start, 0);
buffer_write(buff, buffer_s16, 0);
buffer_write(buff, buffer_s16, x);
buffer_write(buff, buffer_s16, y);
```

- **Notas:** Con buffers que no son `buffer_wrap`, el seek se **satura** al principio o al final, aunque el offset se salga de los límites.

### `buffer_tell(buffer)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la posición actual de lectura/escritura del buffer, en bytes desde el principio.
- **Ejemplo:**

```gml
var _pos = buffer_tell(buff); buffer_seek(buff, buffer_seek_start, 0);
val[0] = buffer_read(buff, buffer_s16);
val[1] = buffer_read(buff, buffer_s16);
val[2] = buffer_read(buff, buffer_s16);
buffer_seek(buff, buffer_seek_start, _pos);
```

---

## Copia entre buffers


### `buffer_copy(src_buffer, src_offset, size, dest_buffer, dest_offset)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia un bloque de bytes de un buffer a otro.
- **Ejemplo:**

*Ejemplo 1: copiar el contenido entero de un búfer*


```gml
buff1 = buffer_create(2048, buffer_grow, 1);
buff2 = buffer_create(2048, buffer_grow, 1);
repeat(2048)
{
    buffer_write(buff1, buffer_u8, irandom(255));
}
buffer_copy(buff1, 0, 2048, buff2, 0);
```

*Ejemplo 2: copiar de un búfer empezando en un desplazamiento*


```gml
buff1 = buffer_create(2048, buffer_fixed, 1);
buff2 = buffer_create(2048, buffer_fixed, 1);
repeat(2048)
{
    buffer_write(buff1, buffer_u8, irandom(255));
}
var _offset = 273;
var _size = buffer_get_size(buff1) - _offset;
buffer_copy(buff1, _offset, _size, buff2, 0);
```

### `buffer_copy_stride(src_buffer, src_offset, src_size, src_stride, src_count, dest_buffer, dest_offset, dest_stride)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia datos de un buffer a otro **con paso (stride)**, es decir, saltando bytes entre elemento y elemento. Pensada para copiar datos entrelazados (vértices, partículas…).
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _num_items = 200;
var _attribute_size = buffer_sizeof(buffer_u16);
var _itemsize_source = buffer_sizeof(buffer_f32) + _attribute_size;
buff_source = buffer_create(_num_items * _itemsize_source, buffer_fixed, 1);
buff_destination = buffer_create(_num_items * _attribute_size, buffer_fixed, 1);

var _i = 0;
repeat(_num_items)
{
    buffer_write(buff_source, buffer_f32, random_range(-100, 100));
    buffer_write(buff_source, buffer_u16, _i++);
}

buffer_copy_stride(buff_source, 4, _attribute_size, _itemsize_source, _num_items, buff_destination, 0, _attribute_size);
```

*Ejemplo 2: desplazamiento y paso negativos*


```gml
var _item_size = buffer_sizeof(buffer_f32);
var _num_items = 100;

var _i = 0;
buff_numbers = buffer_create(_num_items * _item_size, buffer_fixed, 4);
repeat(_num_items) buffer_write(buff_numbers, buffer_f32, _i++);

buff_data = buffer_create(2048, buffer_fixed, 4);
buffer_copy_stride(buff_numbers, -_item_size, _item_size, -_item_size, _num_items, buff_data, 0, 12);
```

*Ejemplo 3: paso fijado a 0*


```gml
var _item_size = buffer_sizeof(buffer_f32);
buff_source = buffer_create(_item_size, buffer_fixed, 4);
buff_destination = buffer_create(16 * _item_size, buffer_fixed, 4);

buffer_write(buff_source, buffer_f32, 1);

buffer_copy_stride(buff_source, 0, _item_size, 0, 4, buff_destination, 0, 5 * _item_size);
```

*Ejemplo 4: intercalar datos de varios búferes*


*Create Event*


```gml
vertex_format_begin();
array_foreach([vertex_format_add_position_3d, vertex_format_add_colour, vertex_format_add_texcoord], script_execute);
vertex_format = vertex_format_end();

buff_positions_xyz = buffer_base64_decode("JqwCQwuLi0J5DIBBcQc3Q27Ar0NNpBZD+WSqQ8B9OEPB0YtD");
buff_colours_rgba = buffer_base64_decode("Ud93/wghI//D2cr/");
buff_uvs = buffer_base64_decode("9KQyP69/UT9Uxak+ybENPzKNZzwxS1A9");

buff_vertex_data = buffer_create(3 * 24, buffer_fixed, 1);
buffer_copy_stride(buff_positions_xyz, 0, 3 * 4, 3 * 4, 3, buff_vertex_data, 0, 24);
buffer_copy_stride(buff_colours_rgba, 0, 4 * 1, 4 * 1, 3, buff_vertex_data, 12, 24);
buffer_copy_stride(buff_uvs, 0, 2 * 4, 2 * 4, 3, buff_vertex_data, 16, 24);
vb = vertex_create_buffer_from_buffer(buff_vertex_data, vertex_format);
```

*Draw Event*


```gml
vertex_submit(vb, pr_trianglelist, -1);
```

### `buffer_copy_from_vertex_buffer(vertex_buffer, start_vertex, num_vertices, dest_buffer, dest_offset)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia vértices de un vertex buffer dentro de un buffer normal.
- **Ejemplo:**

```gml
var _v_num = vertex_get_number(model_buff);
buffer_copy_from_vertex_buffer(model_buffer, 0, _v_num - 1, player_buffer, 0);
```

---

## Guardar y cargar


### `buffer_save(buffer, filename)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Guarda el buffer completo en un fichero.
- **Ejemplo:**

```gml
buffer_save(buff, "Player_Save.sav");
```

### `buffer_save_ext(buffer, filename, offset, size)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Guarda en un fichero solo una porción del buffer, definida por `offset` y `size`.
- **Ejemplo:**

```gml
buffer_save_ext(buff, "Player_Save.sav", 0, 16384);
```

### `buffer_save_async(buffer, filename, offset, size)`

- **Devuelve:** Async Request ID
- **Qué hace:** Guarda una porción del buffer en un fichero de forma **asíncrona**. Devuelve un id de petición que se recibe en el evento Asynchronous Save/Load.
- **Ejemplo:**

```gml
saveid = buffer_save_async(buff, "Player_Save.sav", 0, 16384);
```

```gml
if (ds_map_find_value(async_load, "id") == saveid)
{
    if (ds_map_find_value(async_load, "status") == false)
    {
        show_debug_message("Save failed!");
    }
}
```

- **Notas:** La respuesta llega al evento **Asynchronous Save/Load**.

### `buffer_load(filename)`

- **Devuelve:** Buffer
- **Qué hace:** Carga un fichero completo en un buffer **nuevo** y lo devuelve. Ese buffer también hay que destruirlo con `buffer_delete`.
- **Ejemplo:**

```gml
player_buffer = buffer_load("Player_Save.sav");
```

- **Notas:** El buffer devuelto es nuevo: destrúyelo con `buffer_delete` cuando termines.

### `buffer_load_ext(buffer, filename, offset)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Carga un fichero dentro de un buffer ya existente, a partir del offset indicado.
- **Ejemplo:**

```gml
var _pos = buffer_seek(player_buffer, buffer_seek_end, 0);
buffer_load_ext(player_buffer, "Data_Save.sav", _pos);
```

### `buffer_load_async(buffer, filename, offset, size)`

- **Devuelve:** Async Request ID
- **Qué hace:** Carga un fichero de forma **asíncrona** dentro de un buffer existente. Devuelve un id de petición.
- **Ejemplo:**

```gml
loadid = buffer_load_async(buff, "Player_Save.sav", 0, 16384);
```

```gml
if (ds_map_find_value(async_load, "id") == loadid)
{
    if (ds_map_find_value(async_load, "status") == false)
    {
        show_debug_message("Load failed!");
    }
}
```

- **Notas:** La respuesta llega al evento **Asynchronous Save/Load**. En HTML5 es la **única** forma soportada de cargar.

### `buffer_load_partial(buffer, filename, offset, src_len, dest_offset)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Carga solo una parte de un fichero (`src_len` bytes desde el principio del fichero) dentro de un buffer, en la posición `dest_offset`.
- **Ejemplo:**

```gml
buff = buffer_create(256, buffer_grow, 1);
var _file = "save.dat";
var _so = 6;
var _sl = 5;
var _do = 0;
buffer_load_partial(buff, _file, _so, _sl, _do);
```

---

## Grupos asíncronos


### `buffer_async_group_begin(groupname)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Inicia un **grupo de operaciones asíncronas** con el nombre indicado. Todas las peticiones que se hagan hasta `buffer_async_group_end` se agrupan y se reciben juntas en el evento asíncrono.
- **Ejemplo:**

```gml
buffer_async_group_begin("SaveGame");
save1 = buffer_save_async(buff1, "Player_Save1.sav", 0, 16384);
save2 = buffer_save_async(buff2, "Player_Save2.sav", 0, 16384);
save3 = buffer_save_async(buff3, "Player_Save3.sav", 0, 16384);
save4 = buffer_save_async(buff4, "Player_Save4.sav", 0, 16384);
buffer_async_group_end();
```

### `buffer_async_group_option(option, value)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Configura una opción del grupo asíncrono: si debe mostrarse el cuadro de progreso, el texto del título, el de guardado, el de error, etc.
- **Ejemplo:**

```gml
buffer_async_group_begin("save_folder_name");
buffer_async_group_option("showdialog", false);
buffer_async_group_option("slottitle", "Catch The Haggis Save");
buffer_async_group_option("subtitle", "All your haggis are saved here!");
save = buffer_save_async(buff, "Player_Save.sav", 0, 16384);
buffer_async_group_end();
```

### `buffer_async_group_end()`

- **Devuelve:** Async Request ID
- **Qué hace:** Cierra el grupo asíncrono y **lanza** todas las operaciones. Devuelve el id de la petición.
- **Ejemplo:**

```gml
buffer_async_group_begin("SaveGame");
save1 = buffer_save_async(buff1, "Player_Save1.sav", 0, 16384);
save2 = buffer_save_async(buff2, "Player_Save2.sav", 0, 16384);
save3 = buffer_save_async(buff3, "Player_Save3.sav", 0, 16384);
save4 = buffer_save_async(buff4, "Player_Save4.sav", 0, 16384);
save_id = buffer_async_group_end();
```

```gml
if (ds_map_find_value(async_load, "id") == saveid)
{
    if (ds_map_find_value(async_load, "status") == false)
    {
        show_debug_message("Save failed!");
    }
}
```

- **Notas:** La respuesta llega al evento **Asynchronous Save/Load**, con `async_load[? "id"]` igual al id devuelto.

---

## Compresión


### `buffer_compress(buffer, offset, size)`

- **Devuelve:** Buffer or -1 in case anything went wrong
- **Qué hace:** Comprime una región del buffer y devuelve un buffer **nuevo** con los datos comprimidos, o `-1` si algo falla.
- **Ejemplo:**

```gml
var _srcBuff = buffer_create(1024, buffer_grow, 1);
buffer_write(_srcBuff, buffer_string, global.DataString);
var _cmpBuff = buffer_compress(_srcBuff, 0, buffer_tell(_srcBuff));
buffer_save(_cmpBuff, "Player_Save.sav");
buffer_delete(_srcBuff);
buffer_delete(_cmpBuff);
```

- **Notas:** Devuelve `-1` en caso de error. El buffer devuelto es nuevo: destrúyelo.

### `buffer_decompress(buffer)`

- **Devuelve:** Buffer (or an invalid buffer handle -1 in case the buffer couldn't be decompressed)
- **Qué hace:** Descomprime un buffer creado con `buffer_compress` y devuelve un buffer **nuevo**.
- **Ejemplo:**

```gml
var _cmpBuff = buffer_load("Player_Save.sav");
var _srcBuff = buffer_decompress(_cmpBuff);
global.DataString = buffer_read(_srcBuff, buffer_string);
```

- **Notas:** El buffer devuelto es nuevo: destrúyelo con `buffer_delete`.

---

## Hashes y sumas de comprobación


### `buffer_md5(buffer, offset, size)`

- **Devuelve:** String
- **Qué hace:** Devuelve el **hash MD5** de la región indicada del buffer, como string hexadecimal.
- **Ejemplo:**

```gml
check_string = buffer_md5(buff, 0, buffer_get_size(buff));
```

### `buffer_sha1(buffer, offset, size)`

- **Devuelve:** String
- **Qué hace:** Devuelve el **hash SHA-1** de la región indicada del buffer, como string hexadecimal.
- **Ejemplo:**

```gml
check_string = buffer_sha1(buff, 0, buffer_get_size(buff));
```

### `buffer_crc32(buffer, offset, size)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **CRC32** de la región indicada del buffer, como número real.
- **Ejemplo:**

```gml
check_val = buffer_crc32(buff, 0, buffer_get_size(buff));
```

---

## Codificación base64


### `buffer_base64_encode(buffer, offset, size)`

- **Devuelve:** String
- **Qué hace:** Codifica en **base64** una región del buffer y devuelve el string resultante.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _b_str = buffer_base64_encode(buff, 0, buffer_get_size(buff));
```

*Ejemplo 2: convertir una imagen en una URL de datos*


```gml
var _path = "player_walk_5.png";
var _buff = buffer_load(_path);
var _base64_data = buffer_base64_encode(_buff, 0, buffer_get_size(_buff));
buffer_delete(_buff);
var _data_url = $"data:image/png;base64,{_base64_data}";
show_debug_message(_data_url);
```

### `buffer_base64_decode(string)`

- **Devuelve:** Buffer
- **Qué hace:** Decodifica un string en base64 y devuelve un buffer **nuevo** con los datos. Hay que destruirlo después.
- **Ejemplo:**

```gml
ini_open("Save.ini");
buff = buffer_base64_decode(ini_read_string("Save", "Slot1", ""));
ini_close();
```

- **Notas:** El buffer devuelto es nuevo: destrúyelo con `buffer_delete`.

### `buffer_base64_decode_ext(buffer, string, offset)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Decodifica un string en base64 directamente dentro de un buffer existente, a partir del offset indicado.
- **Ejemplo:**

```gml
buff = buffer_create(16384, buffer_grow, 2);
ini_open("Save.ini");
var _str = ini_read_string("Save", "Slot1", "");
buffer_base64_decode_ext(buff, _str, 0);
ini_close();
```

---

## Surfaces


### `buffer_get_surface(buffer, surface, offset)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia el contenido de una **surface** dentro del buffer, a partir del offset indicado.
- **Ejemplo:**

```gml
var _surf_width = surface_get_width(surf1);
var _surf_height = surface_get_height(surf1);

buff1 = buffer_create(_surf_width * _surf_height * 4, buffer_fixed, 1);
buffer_get_surface(buff1, surf1, 0);
```

```gml
// rgba16float - 16 bits or 2 bytes per channel, RGBA - hence 8 bytes per pixel
buff2 = buffer_create(_surf_width * _surf_height * 8, buffer_fixed, 1)

// r8unorm - 8 bits or 1 byte per pixel, only R channel - hence 1 byte per pixel
buff3 = buffer_create(_surf_width * _surf_height, buffer_fixed, 1)
```

### `buffer_set_surface(buffer, surface, offset)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia el contenido del buffer dentro de una **surface**, a partir del offset indicado.
- **Ejemplo:**

```gml
if (!surface_exists(surf1))
{
    surf1 = surface_create(200, 200);
    surface_set_target(surf1);
    draw_clear_alpha(c_white, 0);
    surface_reset_target();

    if (buffer_exists(buff1))
    {
        buffer_set_surface(buff1, surf1, 0)
    }
}
```

### `buffer_get_surface_depth(buffer, surface, offset)`

- **Devuelve:** Booleano (whether the copy was successful)
- **Qué hace:** Copia el **buffer de profundidad** de una surface dentro del buffer. Devuelve `true` si ha funcionado.
- **Ejemplo:**

*Create Event*


```gml
size = 256;
row_bytesize = 4 * size;

surface = -1;
buffer = buffer_create(4 * size * size, buffer_fixed, 4);

gpu_set_ztestenable(true);
```

*Draw Event*


```gml
if (!surface_exists(surface))
{
    surface = surface_create(size, size);
}

surface_set_target(surface);
draw_clear_ext(c_teal, 1, 1);
gpu_set_depth(10000);
draw_rectangle(100, 100, 150, 150, false);
gpu_set_depth(0);
draw_rectangle(150, 150, 200, 200, true);
surface_reset_target();

buffer_get_surface_depth(buffer, surface, 0);
buffer_fill(buffer, row_bytesize * 112, buffer_f32, 0.7, row_bytesize * 20);
buffer_set_surface_depth(buffer, surface, 0);

surface_set_target(surface);
gpu_set_depth(8000);
draw_circle_color(120, 120, 20, c_red, c_red, false);
surface_reset_target();
```

*Draw GUI Event*


```gml
var _texture = surface_get_texture_depth(surface);
draw_primitive_begin_texture(pr_trianglestrip, _texture);
draw_vertex_texture(0, 0, 0, 0);
draw_vertex_texture(size, 0, 1, 0);
draw_vertex_texture(0, size, 0, 1);
draw_vertex_texture(size, size, 1, 1);
draw_primitive_end();

draw_surface(surface, size, 0);
```

### `buffer_set_surface_depth(buffer, surface, offset)`

- **Devuelve:** Booleano (whether the copy was successful)
- **Qué hace:** Escribe el **buffer de profundidad** de una surface a partir de los datos del buffer. Devuelve `true` si ha funcionado.
- **Ejemplo:**

*Create Event*


```gml
size = 256;
row_bytesize = 4 * size;

surface = -1;
buffer = buffer_create(4 * size * size, buffer_fixed, 4);

gpu_set_ztestenable(true);
```

*Draw Event*


```gml
if (!surface_exists(surface))
{
    surface = surface_create(size, size);
}

surface_set_target(surface);
draw_clear_ext(c_teal, 1, 1);
gpu_set_depth(10000);
draw_rectangle(100, 100, 150, 150, false);
gpu_set_depth(0);
draw_rectangle(150, 150, 200, 200, true);
surface_reset_target();

buffer_get_surface_depth(buffer, surface, 0);
buffer_fill(buffer, row_bytesize * 112, buffer_f32, 0.7, row_bytesize * 20);
buffer_set_surface_depth(buffer, surface, 0);

surface_set_target(surface);
gpu_set_depth(8000);
draw_circle_color(120, 120, 20, c_red, c_red, false);
surface_reset_target();
```

*Draw GUI Event*


```gml
var _texture = surface_get_texture_depth(surface);
draw_primitive_begin_texture(pr_trianglestrip, _texture);
draw_vertex_texture(0, 0, 0, 0);
draw_vertex_texture(size, 0, 1, 0);
draw_vertex_texture(0, size, 0, 1);
draw_vertex_texture(size, size, 1, 1);
draw_primitive_end();

draw_surface(surface, size, 0);
```

---

## Ejemplo práctico: serialización binaria completa

Este ejemplo guarda y carga el estado de un jugador usando un buffer de tamaño fijo,
con la disciplina de **escribir y leer en el mismo orden**.

```gml
// ---------- GUARDAR ----------
function guardar_partida(_ruta)
{
    var _b = buffer_create(1024, buffer_grow, 1);

    buffer_write(_b, buffer_string, global.nombre_jugador);
    buffer_write(_b, buffer_u16,    global.nivel);
    buffer_write(_b, buffer_u32,    global.puntos);
    buffer_write(_b, buffer_f32,    global.pos_x);
    buffer_write(_b, buffer_f32,    global.pos_y);
    buffer_write(_b, buffer_bool,   global.musica_on);
    buffer_write(_b, buffer_u8,     array_length(global.inventario));

    array_foreach(global.inventario, function(_item, _i)
    {
        // closure sobre _b
    });

    buffer_save(_b, _ruta);
    buffer_delete(_b);
}

// ---------- CARGAR ----------
function cargar_partida(_ruta)
{
    if (!file_exists(_ruta)) return false;

    var _b = buffer_load(_ruta);

    global.nombre_jugador = buffer_read(_b, buffer_string);
    global.nivel          = buffer_read(_b, buffer_u16);
    global.puntos         = buffer_read(_b, buffer_u32);
    global.pos_x          = buffer_read(_b, buffer_f32);
    global.pos_y          = buffer_read(_b, buffer_f32);
    global.musica_on      = buffer_read(_b, buffer_bool);
    var _n               = buffer_read(_b, buffer_u8);

    global.inventario = [];
    repeat (_n)
    {
        array_push(global.inventario, buffer_read(_b, buffer_string));
    }

    buffer_delete(_b);
    return true;
}
```

### Variante con `buffer_grow` y recuento de objetos

El patrón recomendado cuando el número de elementos es variable es escribir primero
**cuántos** vienen y luego cada uno:

```gml
var _b = buffer_create(256, buffer_grow, 1);

buffer_write(_b, buffer_u16, array_length(global.enemigos));
for (var i = 0; i < array_length(global.enemigos); i++)
{
    var _e = global.enemigos[i];
    buffer_write(_b, buffer_string, _e.nombre);
    buffer_write(_b, buffer_s16,    _e.vida);
    buffer_write(_b, buffer_f32,    _e.x);
    buffer_write(_b, buffer_f32,    _e.y);
}

buffer_save(_b, "enemigos.sav");
buffer_delete(_b);
```

### Integridad con CRC32

```gml
var _b = buffer_create(64, buffer_grow, 1);
buffer_write(_b, buffer_u32, global.puntos);

var _crc = buffer_crc32(_b, 0, buffer_tell(_b));
buffer_write(_b, buffer_u32, _crc);   // se guarda al final

buffer_save(_b, "puntos.sav");
buffer_delete(_b);
```

---

## Buenas prácticas con buffers

| Práctica | Motivo |
| --- | --- |
| Destruir siempre con `buffer_delete` | Los buffers no se recolectan solos. |
| Poner la variable a `-1` tras destruir | Evita usar un id inválido. |
| Crear el buffer una vez en el evento **Create** y reutilizarlo | Crear buffers en el Step provoca fugas y pérdida de rendimiento. |
| Leer en el mismo orden en que se escribió | Los datos binarios no llevan metadatos. |
| Usar `buffer_sizeof` para calcular offsets | Evita errores al cambiar de tipo de dato. |
| En HTML5, usar siempre `buffer_load_async` | La carga síncrona está obsoleta en los navegadores. |

---

## Fuentes

- [GML Code Reference — GameMaker LTS 2026](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/GML_Reference.htm)
- [Buffers (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Buffers/Buffers.htm)
- [Guide To Using Buffers (LTS)](https://manual.gamemaker.io/lts/en/Additional_Information/Guide_To_Using_Buffers.htm)
- Verificación de cada firma con `gm-cli manual read "<función>"` y contra el manual LTS (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
