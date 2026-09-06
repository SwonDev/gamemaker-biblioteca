# 17 · Ficheros y directorios en GML

> Referencia exhaustiva de **GameMaker LTS 2026** (IDE 2026.0.0.16 · Runtime 2026.0.0.23).

> Todas las firmas han sido verificadas contra el manual oficial LTS.

---

## ⚠ El sandbox: lo que condiciona todo lo demás

**GameMaker está en un entorno aislado (sandbox) por defecto.** Esto significa que no
puedes escribir en cualquier sitio del disco: solo en determinadas áreas que el sistema
autoriza para tu juego.

En los targets de escritorio (**Windows, macOS y Ubuntu**) se puede **desactivar** el
sandbox desde las *Game Options* de la plataforma, y entonces sí se puede guardar y
cargar desde cualquier ruta, dentro de los permisos del sistema operativo.

### Diferencias entre plataformas que importan

- **iOS y Android**: el acceso está limitado al área de datos de la aplicación. Usa
  `working_directory` o `game_save_id`.
- **macOS y Ubuntu**: los nombres de fichero y las rutas **distinguen mayúsculas y
  minúsculas**. GameMaker convierte automáticamente las rutas a minúsculas por defecto
  para evitar problemas.
- **HTML5**: se puede guardar y cargar en el *local storage*, pero **no** se pueden crear
  ni destruir directorios. Para cargar un fichero desde el servidor hay que usar
  **obligatoriamente** `buffer_load_async()`, porque la carga síncrona está obsoleta en
  los navegadores.
- **GX.games**: no se pueden crear ni destruir directorios.

### Dónde guardar las partidas en cada plataforma

```gml
// Directorio de guardado portable y correcto en todas las plataformas
var _dir = game_save_id;                    // identificador único del juego
if (!directory_exists(_dir)) directory_create(_dir);

var _ruta = _dir + "partida01.sav";
```

| Constante / variable | Uso recomendado |
| --- | --- |
| `game_save_id` | **El recomendado** para partidas: es único por juego, así que no pisas a otros títulos. |
| `working_directory` | Directorio de trabajo. En escritorio coincide con la carpeta del ejecutable; en móvil, con el área de datos. |
| `program_directory` | **Solo lectura práctica**: donde están los assets incluidos en el juego. No escribas ahí. |
| `temp_directory` | Datos temporales. El sistema puede borrarlos **en cualquier momento**. |
| `cache_directory` | Caché regenerable que el sistema puede purgar. |

```gml
// Patrón de guardado robusto
function ruta_partida(_slot)
{
    var _dir = game_save_id;
    if (!directory_exists(_dir)) directory_create(_dir);
    return _dir + "save" + string(_slot) + ".sav";
}
```

> **Regla de oro:** nunca escribas en `program_directory`. En muchas plataformas está
> montado como solo lectura y el juego fallará.

---

## Constantes de atributos de fichero

| Constante | Significado |
| --- | --- |
| `fa_none` | Sin atributos |
| `fa_readonly` | Ficheros de solo lectura |
| `fa_hidden` | Ficheros ocultos |
| `fa_sysfile` | Ficheros de sistema |
| `fa_volumeid` | Ficheros de id de volumen |
| `fa_directory` | Directorios |
| `fa_archive` | Ficheros archivados |

> Los atributos **solo funcionan en Windows**. En el resto de plataformas hay que usar
> `0` o `fa_none`.

---

## Ficheros de texto


### `file_text_open_read(fname)`

- **Devuelve:** Text File ID or -1
- **Qué hace:** Abre un fichero de texto en modo **lectura**. Devuelve el id del fichero, o `-1` si no se ha podido abrir.
- **Ejemplo:**

```gml
file = file_text_open_read(working_directory + "level.txt");
```

### `file_text_open_write(fname)`

- **Devuelve:** Text File ID or -1
- **Qué hace:** Abre un fichero de texto en modo **escritura**. Si el fichero existe, **lo sobrescribe**; si no, lo crea. Devuelve `-1` si falla.
- **Ejemplo:**

```gml
// ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
// es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
// 14 - Persistencia y archivos.md §1.
var file;
file = file_text_open_write(game_save_id + "level.txt");
file_text_write_string(file, level_data);
file_text_close(file);
```

### `file_text_open_append(fname)`

- **Devuelve:** Text File ID or -1
- **Qué hace:** Abre un fichero de texto en modo **añadido**: lo crea si no existe y, si existe, escribe a continuación del contenido actual.
- **Ejemplo:**

```gml
// ⚠️ game_save_id, NO working_directory: ver 01 - Fundamentos/
// 14 - Persistencia y archivos.md §1.
file = file_text_open_append(game_save_id + "save.txt");
```

### `file_text_open_from_string(string)`

- **Devuelve:** Text File ID or -1
- **Qué hace:** Abre un **string** como si fuera un fichero de texto en modo lectura. Permite usar todas las funciones de lectura sobre una cadena en memoria.
- **Ejemplo:**

```gml
file = file_text_open_from_string(reset_str);
```

- **Notas:** Devuelve un id de fichero que se cierra igual que cualquier otro con `file_text_close`.

### `file_text_close(fileid)`

- **Devuelve:** Booleano
- **Qué hace:** Cierra el fichero de texto abierto. **Obligatorio**: mientras un fichero está abierto, los datos pueden no haberse volcado a disco.
- **Ejemplo:**

```gml
// ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
// es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
// 14 - Persistencia y archivos.md §1.
var file = file_text_open_write(game_save_id + "Game_Data.txt");
while (!file_text_eof(file))
{
    file_text_readln(file);
}
file_text_write_string(file, level_data);
file_text_close(file);
```

- **Notas:** ⚠ Muy importante: mientras un fichero está abierto, los datos pueden no haberse escrito en disco. Ciérralo siempre.

### `file_text_read_string(fileid)`

- **Devuelve:** String
- **Qué hace:** Lee un string del fichero hasta el primer carácter de **espacio en blanco** o salto de línea.
- **Ejemplo:**

```gml
var file = file_text_open_read(working_directory + "hiscore.txt");
for (var i = 0; i < 10; ++i)
{
    scr[i] = file_text_read_real(file);
    file_text_readln(file);
    scr_name[i] = file_text_read_string(file);
    file_text_readln(file);
}
file_text_close(file);
```

### `file_text_read_real(fileid)`

- **Devuelve:** Real
- **Qué hace:** Lee un número del fichero, deteniéndose en el primer carácter que no pueda formar parte de un número.
- **Ejemplo:**

```gml
var file = file_text_open_read(working_directory + "hiscore.txt");
for (var i = 0; i < 10; ++i)
{
    scr[i] = file_text_read_real(file);
    file_text_readln(file);
    scr_name[i] = file_text_read_string(file);
    file_text_readln(file);
}
file_text_close(file);
```

### `file_text_readln(fileid)`

- **Devuelve:** String
- **Qué hace:** Lee una **línea completa** del fichero, incluyendo el salto de línea final, y avanza a la siguiente.
- **Ejemplo:**

```gml
var file = file_text_open_read(working_directory + "hiscore.txt");
for (var i = 0; i < 10; ++i)
{
    scr[i] = file_text_read_real(file);
    file_text_readln(file);
    scr_name[i] = file_text_read_string(file);
    file_text_readln(file);
}
file_text_close(file);
```

### `file_text_write_string(fileid, str)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Escribe un string en el fichero sin añadir salto de línea.
- **Ejemplo:**

```gml
// ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
// es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
// 14 - Persistencia y archivos.md §1.
var file = file_text_open_write(game_save_id + "hiscore.txt");
for (var i = 0; i < 10; ++i)
{
    file_text_write_real(file, scr[i]);
    file_text_writeln(file);
    file_text_write_string(file, scr_name[i]);
    file_text_writeln(file);
}
file_text_close(file);
```

### `file_text_write_real(fileid, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Escribe un número en el fichero sin añadir salto de línea.
- **Ejemplo:**

```gml
// ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
// es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
// 14 - Persistencia y archivos.md §1.
var file = file_text_open_write(game_save_id + "hiscore.txt");
for (var i = 0; i < 10; ++i)
{
    file_text_write_real(file, scr[i]);
    file_text_writeln(file);
    file_text_write_string(file, scr_name[i]);
    file_text_writeln(file);
}
file_text_close(file);
```

### `file_text_writeln(fileid)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Escribe un **salto de línea** en el fichero.
- **Ejemplo:**

```gml
// ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
// es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
// 14 - Persistencia y archivos.md §1.
var file = file_text_open_write(game_save_id + "hiscore.txt");
for (var i = 0; i < 10; ++i)
{
    file_text_write_real(file, scr[i]);
    file_text_writeln(file);
    file_text_write_string(file, scr_name[i]);
    file_text_writeln(file);
}
file_text_close(file);
```

### `file_text_eof(fileid)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si se ha llegado al **final del fichero** (end of file).
- **Ejemplo:**

```gml
var num = 0;
var file = file_text_open_read(working_directory + "Game_Data.txt");
while (!file_text_eof(file))
{
    str[num++] = file_text_readln(file);
}
file_text_close(file);
```

### `file_text_eoln(fileid)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la posición actual está al **final de una línea** (end of line).
- **Ejemplo:**

```gml
var file = file_text_open_read(working_directory + "Game_Data.txt");
var num = 0; while (!file_text_eoln(file))
{
    score_array[num] = file_text_read_real(file);
    num++;
}
file_text_close(file);
```

---

## Sistema de ficheros


### `file_exists(fname)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el fichero existe en la ruta indicada.
- **Ejemplo:**

```gml
if (file_exists("level.txt"))
{
    file = file_text_open_read("level.txt");
}
```

### `file_delete(fname)`

- **Devuelve:** Booleano
- **Qué hace:** Elimina el fichero indicado. Devuelve `true` si lo ha conseguido.
- **Ejemplo:**

```gml
if (file_exists("level.txt"))
{
    file_delete("level.txt");
}
```

### `file_rename(oldname, newname)`

- **Devuelve:** Booleano
- **Qué hace:** Renombra (o mueve) el fichero indicado. Devuelve `true` si lo ha conseguido.
- **Ejemplo:**

```gml
if (file_exists("level1.txt"))
{
    file_rename("level1.txt", "level.txt");
}
```

### `file_copy(fname, newname)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia el fichero de origen en la ruta de destino.
- **Ejemplo:**

```gml
if (file_exists("level1.txt"))
{
    file_copy("level1.txt", "level2.txt");
}
```

### `file_attributes(fname, attr)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el fichero tiene el **atributo** indicado. **Solo Windows.**
- **Ejemplo:**

```gml
if (!file_attributes(file, fa_hidden))
{
    file_delete(file);
}
```

- **Notas:** **Solo Windows.**

---

## Búsqueda de ficheros


### `file_find_first(mask, attr)`

- **Devuelve:** String
- **Qué hace:** Inicia una búsqueda de ficheros con la máscara y atributos dados, y devuelve el nombre del primero. Hay que cerrar la búsqueda con `file_find_close`.
- **Ejemplo:**

```gml
if (directory_exists("/User Content"))
{
    fileA = file_find_first("/User Content/*.doc", fa_readonly);
    fileB = file_find_next();
    fileC = file_find_next();
    file_find_close();
}
```

```gml
var _files = [];
var _file_name = file_find_first("/User Content/*.doc", fa_readonly);

while (_file_name != "")
{
    array_push(_files, _file_name);

    _file_name = file_find_next();
}

file_find_close();
```

- **Notas:** Los atributos solo funcionan en **Windows**; en el resto de plataformas usa `0` o `fa_none`. No funciona en HTML5 ni GX.games.

### `file_find_next()`

- **Devuelve:** String
- **Qué hace:** Devuelve el nombre del **siguiente** fichero de la búsqueda en curso, o un string vacío si no hay más.
- **Ejemplo:**

```gml
if (directory_exists("/User Content"))
{
    fileA = file_find_first("/User Content/*.doc", fa_readonly);
    fileB = file_find_next();
    fileC = file_find_next();
    file_find_close();
}
```

```gml
var _files = [];
var _file_name = file_find_first("/User Content/*.doc", fa_readonly);

while (_file_name != "")
{
    array_push(_files, _file_name);

    _file_name = file_find_next();
}

file_find_close();
```

- **Notas:** Devuelve un string vacío `""` cuando no quedan ficheros. Cierra siempre con `file_find_close`.

### `file_find_close()`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Cierra la búsqueda iniciada con `file_find_first`. **Obligatorio** antes de iniciar otra.
- **Ejemplo:**

```gml
if (directory_exists("/User Content"))
{
    fileA = file_find_first("/User Content/*.doc", fa_readonly);
    fileB = file_find_next();
    fileC = file_find_next();
    file_find_close();
}
```

```gml
var _files = [];
var _file_name = file_find_first("/User Content/*.doc", fa_readonly);

while (_file_name != "")
{
    array_push(_files, _file_name);

    _file_name = file_find_next();
}

file_find_close();
```

---

## Manipulación de rutas (solo strings)


### `filename_name(fname)`

- **Devuelve:** String
- **Qué hace:** Devuelve solo el **nombre** del fichero, sin la ruta ni la extensión.
- **Ejemplo:**

```gml
name = filename_name(file_find_first("C:/Games/*.doc", 0));
```

### `filename_path(fname)`

- **Devuelve:** String
- **Qué hace:** Devuelve solo la **ruta** (directorio) del fichero, con la barra final incluida.
- **Ejemplo:**

```gml
path = filename_path(working_directory + "Test.ini");
```

### `filename_dir(fname)`

- **Devuelve:** String
- **Qué hace:** Devuelve el directorio del fichero, **sin** la barra final.
- **Ejemplo:**

```gml
dir = filename_dir("Test.ini");
```

### `filename_drive(fname)`

- **Devuelve:** String
- **Qué hace:** Devuelve la **letra de unidad** del fichero. Solo tiene sentido en Windows.
- **Ejemplo:**

```gml
drive = filename_drive(file_find_first(working_directory + "*.doc", 0));
```

### `filename_ext(fname)`

- **Devuelve:** String
- **Qué hace:** Devuelve la **extensión** del fichero, incluido el punto.
- **Ejemplo:**

```gml
ext = filename_ext(file_find_first("*.*", 0));
```

### `filename_change_ext(fname, newext)`

- **Devuelve:** String
- **Qué hace:** Devuelve la ruta del fichero con la **extensión cambiada**.
- **Ejemplo:**

```gml
ext = filename_change_ext(file_find_first(working_directory + "*.*", 0), "");
```

---

## Diálogos del sistema


### `get_open_filename(filter, fname)`

- **Devuelve:** String
- **Qué hace:** Abre el diálogo del sistema para **abrir** un fichero y devuelve la ruta elegida, o `""` si se cancela. **Solo Windows y macOS.**
- **Ejemplo:**

```gml
var file;
file = get_open_filename("text file|*.txt", "");
if (file != "")
{
    file_text_open_read(file);
}
```

- **Notas:** **Solo Windows y macOS.** Abre una ventana del explorador, así que el juego pierde el foco. Si lo usas en un evento de teclado, hazlo en **key up**, no en *pressed* ni *down*.

### `get_open_filename_ext(filter, fname, directory, caption)`

- **Devuelve:** String
- **Qué hace:** Igual que `get_open_filename`, pero permite fijar el directorio inicial y el título del diálogo. **Solo Windows y macOS.**
- **Ejemplo:**

```gml
var file;
file = get_open_filename_ext("text file|*.txt", "", working_directory, "Open a saved level");
if (file != "")
{
    file_text_open_read(file);
}
```

- **Notas:** **Solo Windows y macOS.**

### `get_save_filename(filter, fname)`

- **Devuelve:** String
- **Qué hace:** Abre el diálogo del sistema para **guardar** un fichero y devuelve la ruta elegida, o `""` si se cancela. **Solo Windows y macOS.**
- **Ejemplo:**

```gml
var _file = get_save_filename("screenshot|*.png", "");
if (_file != "")
{
    screen_save(_file);
}
```

- **Notas:** **Solo Windows y macOS.**

### `get_save_filename_ext(filter, fname, directory, caption)`

- **Devuelve:** String
- **Qué hace:** Igual que `get_save_filename`, pero permite fijar el directorio inicial y el título. **Solo Windows y macOS.**
- **Ejemplo:**

```gml
var _file = get_save_filename_ext("screenshot|*.png", "", working_directory, "Save a level here");
if (_file != "")
{
    screen_save(_file);
}
```

- **Notas:** **Solo Windows y macOS.**

---

## Directorios


### `directory_exists(dname)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el directorio existe.
- **Ejemplo:**

```gml
if (directory_exists(working_directory + "Saves/"))
{
    file = file_find_first(working_directory + "Saves/*.doc", fa_readonly);
}
```

### `directory_create(dname)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Crea el directorio indicado. En la mayoría de plataformas solo puede crear un nivel de profundidad.
- **Ejemplo:**

```gml
if (!directory_exists("Games"))
{
    directory_create("Games");
}
```

- **Notas:** Suele crear **un solo nivel**: crea los padres por separado si no existen.

### `directory_destroy(dname)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Elimina el directorio indicado. Solo funciona si está **vacío**.
- **Ejemplo:**

```gml
if (directory_exists("DLC"))
{
    directory_destroy("DLC");
}
```

- **Notas:** Solo elimina directorios **vacíos**.

---

## Variables de ruta


### `working_directory`

- **Devuelve:** String
- **Qué hace:** Ruta del directorio de **trabajo**: donde vive el ejecutable (o, en algunos targets, el área de guardado).
- **Ejemplo:**

```gml
ini_open(working_directory + "temp_ini.ini");
```

### `program_directory`

- **Devuelve:** String
- **Qué hace:** Ruta del directorio donde está instalado el **programa**, es decir, donde residen los assets incluidos.
- **Ejemplo:**

```gml
dir = program_directory;
```

### `temp_directory`

- **Devuelve:** String
- **Qué hace:** Ruta del directorio **temporal** del sistema. Su contenido puede borrarse en cualquier momento.
- **Ejemplo:**

```gml
ini_open(temp_directory + "temp_ini.ini");
```

- **Notas:** El sistema puede borrar su contenido en cualquier momento: nunca guardes ahí datos que no puedas regenerar.

### `cache_directory`

- **Devuelve:** String
- **Qué hace:** Ruta del directorio de **caché** de la plataforma: apto para datos regenerables que el sistema puede purgar.
- **Ejemplo:**

```gml
ini_open(cache_directory + "cache_ini.ini");
```

- **Notas:** Igual que `temp_directory`: el sistema puede purgarlo.

### `game_save_id`

- **Devuelve:** String
- **Qué hace:** Identificador **único** del juego, pensado para usarlo como nombre del directorio donde guardar las partidas en el área del usuario.
- **Ejemplo:**

```gml
save_dir = game_save_id;
```

- **Notas:** Es la forma recomendada de no pisar los datos de otro juego al guardar en el área del usuario.

---

## Ficheros INI


### `ini_open(name)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Abre un fichero `.ini` para lectura y escritura. Si no existe, se crea al escribir. Debe cerrarse con `ini_close`.
- **Ejemplo:**

```gml
ini_open("Settings/savedata.ini");
score = ini_read_real("save1", "score", 0);
ini_close();
```

- **Notas:** ⚠ No se puede usar el nombre **options.ini**: todos los proyectos de GameMaker ya tienen ese fichero y la compilación falla con un error de UID.

### `ini_open_from_string(string)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Abre un **string** con formato ini como si fuera un fichero, para leerlo sin tocar el disco.
- **Ejemplo:**

```gml
ini_open_from_string(str);
global.sound = ini_read_string("Options", "Sound", true);
ini_close();
```

### `ini_close()`

- **Devuelve:** String
- **Qué hace:** Cierra el fichero ini abierto y **vuelca los cambios a disco**. Devuelve el contenido como string.
- **Ejemplo:**

```gml
ini_open("savedata.ini");
score = ini_read_real("save1", "score", 0);
ini_close();
```

### `ini_write_real(section, key, value)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Escribe un número en la sección y clave indicadas.
- **Ejemplo:**

```gml
score = 1000;
 ini_open("savedata.ini");

 ini_write_real("save1", "Score", score );
 score2 = ini_read_real("save1", "Score", 0 );
 ini_close();
```

### `ini_write_string(section, key, value)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Escribe un string en la sección y clave indicadas.
- **Ejemplo:**

```gml
ini_open("savedata.ini");
ini_write_string("Save", "Player", global.Name);
ini_close();
```

### `ini_read_real(section, key, default)`

- **Devuelve:** Real
- **Qué hace:** Lee un número de la sección y clave indicadas. Si no existe, devuelve el valor por defecto.
- **Ejemplo:**

```gml
ini_open("savedata.ini");
 score = ini_read_real("save1", "score", 0 );
 ini_close();
```

### `ini_read_string(section, key, default)`

- **Devuelve:** String
- **Qué hace:** Lee un string de la sección y clave indicadas. Si no existe, devuelve el valor por defecto.
- **Ejemplo:**

```gml
ini_open("savedata.ini");
global.name = ini_read_string("player", "name", "Player1");
ini_close();
```

### `ini_key_exists(section, key)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la clave existe dentro de la sección indicada.
- **Ejemplo:**

```gml
ini_open("savedata.ini");
if (!ini_key_exists("save1", "name"))
{
    global.name = "Player1";
}
ini_close();
```

### `ini_section_exists(section)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la sección existe en el fichero ini.
- **Ejemplo:**

```gml
ini_open("savedata.ini");
if (!ini_section_exists("save1"))
{
    global.savegame = "1";
}
ini_close();
```

### `ini_key_delete(section, key)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Elimina la clave indicada de la sección.
- **Ejemplo:**

```gml
ini_open("savedata.ini");
 ini_write_real("save1","Score",score);

 ini_key_delete("save1","Score");

 ini_close();
```

### `ini_section_delete(section)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Elimina la sección completa, con todas sus claves.
- **Ejemplo:**

```gml
ini_open("savedata.ini");
ini_write_real("save1", "Score", score );
ini_section_delete("save1");
ini_close();
```

---

## Ficheros binarios (heredado)


### `file_bin_open(fname, mode)`

- **Devuelve:** Binary File ID or -1
- **Qué hace:** Abre un fichero en modo **binario** con el modo indicado (0 = lectura, 1 = escritura, 2 = lectura y escritura). Devuelve `-1` si falla.
- **Ejemplo:**

```gml
file = file_bin_open("myfile.bin", 2);
```

- **Notas:** Estas funciones no funcionan en HTML5. En general, para binario es mejor usar **buffers**.

### `file_bin_rewrite(binfile)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Vacía el fichero binario abierto y deja la posición al principio, listo para escribir de nuevo.
- **Ejemplo:**

```gml
file = file_bin_open("myfile.bin", 2);
 file_bin_rewrite(file);
```

### `file_bin_close(binfile)`

- **Devuelve:** Booleano
- **Qué hace:** Cierra el fichero binario abierto. **Obligatorio**.
- **Ejemplo:**

```gml
file = file_bin_open("myfile.bin", 2);
file_bin_rewrite(file);
file_bin_close(file);
```

### `file_bin_size(binfile)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el tamaño del fichero binario en bytes.
- **Ejemplo:**

```gml
file = file_bin_open("myfile.bin", 2);
 size = file_bin_size(file);
 file_bin_close(file);
```

### `file_bin_position(binfile)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la posición actual de lectura/escritura dentro del fichero binario.
- **Ejemplo:**

```gml
pos = file_bin_position(file);
```

### `file_bin_seek(binfile, pos)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Mueve la posición de lectura/escritura dentro del fichero binario.
- **Ejemplo:**

```gml
file = file_bin_open("myfile.bin", 2);
 size = file_bin_size(file);
 file_bin_seek(file, size);
```

### `file_bin_write_byte(binfile, byte)`

- **Devuelve:** Real
- **Qué hace:** Escribe un **byte** en el fichero binario. Devuelve `0` si ha funcionado.
- **Ejemplo:**

```gml
file_bin_write_byte(file, data);
```

### `file_bin_read_byte(binfile)`

- **Devuelve:** Real
- **Qué hace:** Lee un **byte** del fichero binario.
- **Ejemplo:**

```gml
file = file_bin_open("myfile.bin", 2);
 data = file_bin_read_byte(file);
 file_bin_close(file);
```

---

## Codificación y hashing


### `json_stringify(val, [pretty_print], [filter_func])`

- **Devuelve:** String
- **Qué hace:** Convierte un struct o array en un **string JSON**. Es la forma moderna de serializar.
- **Ejemplo:**

*Ejemplo 1*


```gml
var _contents =
{
    version : "1.0.0",
    data:
    {
        coins : 4,
        mana : 15,
        playername : "Gurpreet",
        items :
        [
            ITEM.SWORD,
            ITEM.BOW,
            ITEM.GUITAR
        ]
    }
};

var _json_string = json_stringify(_contents);
```

```gml
{ "data": { "items": [ 0.0, 1.0, 2.0 ], "coins": 4.0, "mana": 15.0, "playername": "Gurpreet" }, "version": "1.0.0" }
```

*Ejemplo 2: impresión formateada*


```gml
var _contents =
{
    version: "1.0.0",
    data:
    {
        coins : 5,
        mana : 0,
        playername : "Bart",
        items :
        [
            ITEM.SWORD,
            ITEM.BOW,
            ITEM.PIANO
        ]
    }
}
var _json_string = json_stringify(_contents, true);
```

```gml
{
  "data":{
    "mana":0.0,
    "playername":"Bart",
    "items":[
      0,
      1,
      2
    ],
    "coins":5.0
  },
  "version":"1.0.0"
}
```

*Ejemplo 3: función de filtro*


```gml
var data =
{
    x: 5.2344,
    y: 10.601,
    last_clicked: undefined,
    values :  [ 2000.1, 30.56, undefined, { slot : 10, skin : undefined } ]
}

var json = json_stringify(data, true, function(key, value)
{
    if (is_real(value)) return round(value);
    if (is_undefined(value)) return 0;
    return value;
});

show_debug_message(json);
```

### `json_parse(json, [filter_func], [inhibit_string_convert])`

- **Devuelve:** Struct or Array
- **Qué hace:** Convierte un string JSON en un **struct o array**. Es la forma moderna de deserializar.
- **Ejemplo:**

*Ejemplo 1*


```gml
var json = "{\"myObj\": { \"apples\":10, \"oranges\":12, \"potatoes\":100000, \"avocados\":0 }, \"myArray\":[0, 1, 2, 2, 4, 0, 1, 5, 1]}";

var data = json_parse(json);
show_debug_message(data);
```

```gml
var data = json_parse(json);

// Check if the struct has myObj variable
if (struct_exists(data, "myObj"))
{
    // Check if it's a struct
    if (is_struct(data.myObj))
    {
        // Print all struct members to the log
        var _names = struct_get_names(data.myObj);
        var _str = "";
        for (var i = 0; i < array_length(_names); i++)
        {
            _str = _names[i] + ": " + string(struct_get(data.myObj, _names[i]));
            show_debug_message(_str);
        }
    }
}

// Check if the struct has myArray variable
if (struct_exists(data, "myArray"))
{
    // Check if it's an array
    if (is_array(data.myArray))
    {
        show_debug_message(data.myArray);
    }
}
```

```gml
oranges: 12
potatoes: 100000
avocados: 0
apples: 10
[ 0,1,2,2,4,0,1,5,1 ]
```

*Ejemplo 2: función de filtro*


```gml
var json = "{\"myObj\": { \"apples\":10, \"oranges\":12, \"potatoes\":100000, \"avocados\":0 }, \"myArray\":[0, 1, 2, 2, 4, 0, 1, 5, 1]}";

var data = json_parse(json, function (key, value)
{
    show_debug_message($"Key: {key}, Value: {value}");
    return value;
});
```

```gml
Key: apples, Value: 10
Key: oranges, Value: 12
Key: potatoes, Value: 100000
Key: avocados, Value: 0
Key: myObj, Value: { apples : 10, oranges : 12, potatoes : 100000, avocados : 0 }
Key: 8, Value: 1
Key: 7, Value: 5
Key: 6, Value: 1
Key: 5, Value: 0
Key: 4, Value: 4
Key: 3, Value: 2
Key: 2, Value: 2
Key: 1, Value: 1
Key: 0, Value: 0
Key: myArray, Value: [ 0,1,2,2,4,0,1,5,1 ]
Key: , Value: { myObj : { apples : 10, oranges : 12, potatoes : 100000, avocados : 0 }, myArray : [ 0,1,2,2,4,0,1,5,1 ] }
```

*Ejemplo 3: sobrescribir valores*


```gml
var json = "{\"prices\": [2, 5, 1, 2, 4, 5]}";

var data = json_parse(json, function (key, value)
{
    return is_real(value) ? value * 1000 : value;
});

show_debug_message(data);
```

```gml
{ prices : [ 2000,5000,1000,2000,4000,5000 ] }
```

### `json_encode(map, [prettify])`

- **Devuelve:** String
- **Qué hace:** Convierte un **DS map** en un string JSON. **Heredada**: usa `json_stringify`.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _hiscore_map, _json;
_hiscore_map = ds_map_create();
for (var i = 0; i < 10; i++)
{
    ds_map_add(_hiscore_map, name[i], score[i]);
}
_json = json_encode(_hiscore_map);
ds_map_destroy(_hiscore_map);

post_request_id = http_post_string($"http://www.angusgames.com/game?game_id={global.game_id}", _json);
```

*Ejemplo 2: jerarquía de tipos de datos mixtos*


```gml
var _map = ds_map_create();
var _list = ds_list_create();

ds_map_add_list(_map, "seasoning", _list);
ds_list_add(_list, "pepper", "salt", "thyme");

_map[? "greeting"] = {parts: ["Hello", "World!"], separator: ", "};
_map[? "food"] = ["bread", "coconut", "mango"];

var _json = json_encode(_map, true);
// ds_map_destroy(_map);

show_debug_message(_json);
```

- **Notas:** Solo acepta **DS maps**. Para structs usa `json_stringify`.

### `json_decode(string)`

- **Devuelve:** DS Map
- **Qué hace:** Convierte un string JSON en un **DS map** que hay que destruir. **Heredada**: usa `json_parse`.
- **Ejemplo:**

```gml
var resultMap = json_decode(requestResult);
var list = ds_map_find_value(resultMap, "default");
var size = ds_list_size(list);
for (var n = 0; n < ds_list_size(list); n++)
{
    var map = ds_list_find_value(list, n);
    var curr = ds_map_find_first(map);
    while (is_string(curr))
    {
        global.Name[n] = ds_map_find_value(map, "name");
        curr = ds_map_find_next(map, curr);
    }
}
ds_map_destroy(resultMap);
```

- **Notas:** Devuelve un **DS map**: destrúyelo con `ds_map_destroy` o tendrás una fuga de memoria.

### `base64_encode(string)`

- **Devuelve:** String
- **Qué hace:** Codifica un string en **base64**. Ofusca, pero **no cifra**: cualquiera puede revertirlo.
- **Ejemplo:**

```gml
var _str, _file;
_str = base64_encode(game_data);
_file = file_text_open_write("save.txt");
file_text_write_string(_file, _str);
file_text_close(_file);
```

- **Notas:** Codificar **no** es cifrar. Si necesitas protección real, añade tu propia capa de cifrado.

### `base64_decode(string)`

- **Devuelve:** String
- **Qué hace:** Decodifica un string en base64.
- **Ejemplo:**

```gml
var _str, _file;
_str = base64_encode(game_data);
_file = file_text_open_read("save.txt");
_str = file_text_read_string(_file);
level_data = base64_decode(_str);
file_text_close(_file);
```

---

## Hashes MD5 y SHA-1


### `md5_string_utf8(string)`

- **Devuelve:** String
- **Qué hace:** Devuelve el hash MD5 del string, tratándolo como **UTF-8**.
- **Ejemplo:**

```gml
var _hash, _str;
_str = json_encode(hiscore_map);
_hash = md5_string_utf8(_str);
ini_open("local.ini");
ini_write_string("info", "0", _hash);
ini_close();
get[0] = http_post_string("http://www.macsweeneygames.com/CatchTheHaggis?game_hiscores=" + string(global.game_id), _str);
```

### `md5_string_unicode(string)`

- **Devuelve:** String
- **Qué hace:** Devuelve el hash MD5 del string, tratándolo como **Unicode**.
- **Ejemplo:**

```gml
var _hash, _str;
_str = base64_encode(game_data);
_hash = md5_string_unicode(_str);
http_get("http://www.macsweeneygames.com/catchthehaggis/gamedata?hash=" + _hash);
http_get("http://www.macsweeneygames.com/CatchTheHaggis/gamedata?data=" + _str);
```

### `md5_file(filename)`

- **Devuelve:** String
- **Qué hace:** Devuelve el hash MD5 del contenido del fichero indicado.
- **Ejemplo:**

```gml
hash = md5_file(working_directory + "game_data.ini");
```

### `sha1_string_utf8(string)`

- **Devuelve:** String
- **Qué hace:** Devuelve el hash SHA-1 del string, tratándolo como **UTF-8**.
- **Ejemplo:**

```gml
var _hash, _str;
_str = json_encode(hiscore_map);
_hash = sha1_string_utf8(_str);
ini_open("local.ini");
ini_write_string("info", "0", _hash);
ini_close();
get[0] = http_post_string("http://www.macsweeneygames.com/CatchTheHaggis?game_hiscores=" + string(global.game_id), _str);
```

### `sha1_string_unicode(string)`

- **Devuelve:** String
- **Qué hace:** Devuelve el hash SHA-1 del string, tratándolo como **Unicode**.
- **Ejemplo:**

```gml
var _hash, _str;
_str = base64_encode(game_data);
_hash = sha1_string_unicode(_str);
http_get("http://www.macsweeneygames.com/CatchTheHaggis/gamedata?hash=" + _hash);
http_get("http://www.macsweeneygames.com/CatchTheHaggis/gamedata?data=" + _str);
```

### `sha1_file(filename)`

- **Devuelve:** String
- **Qué hace:** Devuelve el hash SHA-1 del contenido del fichero indicado.
- **Ejemplo:**

```gml
hash = sha1_file(working_directory + "game_data.ini");
```

---

## CSV y ZIP


### `load_csv(filename)`

- **Devuelve:** DS Grid
- **Qué hace:** Carga un fichero **CSV** y devuelve una **DS grid** con su contenido. Esa grid hay que destruirla con `ds_grid_destroy`.
- **Ejemplo:**

```gml
file_grid = load_csv("spreadsheet.csv");
var ww = ds_grid_width(file_grid);
var hh = ds_grid_height(file_grid);
var xx = 32;
var yy = 32;
for (var i = 0; i < ww; i++)
{
    for (var j = 0; j < hh; j++)
    {
        draw_text(xx, yy, file_grid[# i, j]);
        yy += 32;
    }
    yy = 32;
    xx += 32;
}
```

- **Notas:** La DS grid devuelta **no** se recolecta: destrúyela con `ds_grid_destroy`.

### `zip_create()`

- **Devuelve:** ZIP File
- **Qué hace:** Crea un objeto ZIP **en memoria** al que se le pueden añadir ficheros.
- **Ejemplo:**

```gml
var _zip = zip_create();

zip_add_file(_zip, "new.txt", "new.txt");
zip_add_file(_zip, "sounds/snd_attack_arc_01.wav", "snd_attack_arc_01.wav");

zip_save(_zip, "upload.zip");
```

### `zip_add_file(zip_object, dest, src)`

- **Devuelve:** Real
- **Qué hace:** Añade un fichero al objeto ZIP, indicando la ruta interna que tendrá dentro del comprimido y la ruta real en disco.
- **Ejemplo:**

```gml
var _zip = zip_create();

zip_add_file(_zip, "new.txt", "new.txt");
zip_add_file(_zip, "sounds/snd_attack_arc_01.wav", "snd_attack_arc_01.wav");

zip_save(_zip, "upload.zip");
```

### `zip_save(zip_object, path)`

- **Devuelve:** Real
- **Qué hace:** Escribe el objeto ZIP a disco en la ruta indicada y devuelve el resultado.
- **Ejemplo:**

```gml
var _zip = zip_create();

zip_add_file(_zip, "new.txt", "new.txt");
zip_add_file(_zip, "sounds/snd_attack_arc_01.wav", "snd_attack_arc_01.wav");

zip_save(_zip, "upload.zip");
```

### `zip_unzip(zip_file, target_directory)`

- **Devuelve:** Real
- **Qué hace:** Descomprime un fichero ZIP en el directorio indicado y devuelve el número de ficheros extraídos.
- **Ejemplo:**

```gml
var num = zip_unzip("/downloads/level_data.zip", working_directory + "extracted/");
if (num <= 0)
{
    show_debug_message("Extraction Failed!");
}
```

- **Notas:** Devuelve el número de ficheros extraídos.

### `zip_unzip_async(zip_file, target_directory)`

- **Devuelve:** Real
- **Qué hace:** Descomprime un fichero ZIP de forma **asíncrona**. El resultado llega al evento asíncrono.
- **Ejemplo:**

```gml
level_data_request = zip_unzip_async("/downloads/level_data.zip", working_directory + "extracted/");
```

```gml
Async Save/Load event
```

```gml
var _id = async_load[? "id"];

if (_id == level_data_request)
{
    var _status = async_load[? "status"];

    if (_status < 0)
    {
        show_debug_message("ZIP file extraction failed.");
    }
}
```

- **Notas:** El resultado llega al evento asíncrono con `async_load[? "id"]`.

---

## Receta: guardar y cargar con ficheros de texto

```gml
// Guardar
var _f = file_text_open_write(ruta_partida(1));
file_text_write_real(_f, global.nivel);
file_text_writeln(_f);
file_text_write_string(_f, global.nombre);
file_text_writeln(_f);
file_text_close(_f);          // ¡imprescindible!

// Cargar
if (file_exists(ruta_partida(1)))
{
    var _f = file_text_open_read(ruta_partida(1));
    global.nivel  = file_text_read_real(_f);
    file_text_readln(_f);
    global.nombre = file_text_read_string(_f);
    file_text_close(_f);
}
```

## Receta: guardar con INI

```gml
ini_open("opciones.ini");
ini_write_real("video", "brillo", 0.8);
ini_write_string("audio", "idioma", "es");
ini_close();

ini_open("opciones.ini");
var _brillo = ini_read_real("video", "brillo", 1.0);
var _idioma = ini_read_string("audio", "idioma", "en");
ini_close();
```

> ⚠ **Nunca** llames a un fichero `options.ini`: todos los proyectos de GameMaker ya
> tienen ese fichero y la compilación falla con un error de UID.

## Receta: listar todos los ficheros de un directorio

```gml
var _lista = [];
var _f = file_find_first(game_save_id + "*.sav", fa_none);

while (_f != "")
{
    array_push(_lista, _f);
    _f = file_find_next();
}
file_find_close();     // ¡imprescindible antes de iniciar otra búsqueda!
```

---

## Texto vs. INI vs. Buffers

| Necesitas… | Usa |
| --- | --- |
| Preferencias sencillas (opciones, récords) | **INI** |
| Muchos datos estructurados legibles | **Ficheros de texto** |
| Datos binarios, compactos o difíciles de trucar | **Buffers** (`buffer_save` / `buffer_load`) |
| Structs y arrays | **JSON** (`json_stringify` / `json_parse`) |

Se pueden tener abiertos hasta **32 ficheros de texto** simultáneamente.

---

## Fuentes

- [GML Code Reference — GameMaker LTS 2026](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/GML_Reference.htm)
- [File Handling (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/File_Handling/File_Handling.htm)
- [The File System (LTS)](https://manual.gamemaker.io/lts/en/Additional_Information/The_File_System.htm)
- [Encoding And Hashing (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/File_Handling/Encoding_And_Hashing/Encoding_And_Hashing.htm)
- Verificación de cada firma con `gm-cli manual read "<función>"` y contra el manual LTS (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
