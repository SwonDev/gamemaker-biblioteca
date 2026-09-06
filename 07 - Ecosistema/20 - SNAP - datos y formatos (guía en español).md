# 20 · SNAP — convertir datos entre formatos (guía en español)

> **SNAP** (de @jujuadams) convierte structs y arrays de GameMaker **a y desde** JSON, CSV, XML,
> YAML, INI, VDF (Valve), QML y GML, y formatos binarios (MessagePack, BSON) vía búfer. Es la
> navaja suiza de la serialización: guardar partidas legibles, leer datos de diseño (niveles,
> objetos), hablar con servidores. Guía en español con la API verificada contra el código en
> `11 - Código descargado/librerias/datos-y-estructuras/SNAP`.

---

## Por qué SNAP y no solo `json_stringify`

GameMaker trae `json_stringify`/`json_parse` para JSON, y basta para muchos casos. SNAP añade
**todos los demás formatos** con el mismo patrón, y un JSON/YAML **legible** (con sangría) que un
humano puede editar a mano —clave para archivos de diseño que tocan diseñadores, no solo código.

---

## 1 · El patrón: `SnapTo<formato>` y `SnapFrom<formato>`

Cada formato es un par simétrico. Le pasas un struct/array de GameMaker y te da texto, o al revés.

```gml
/// un struct de datos del juego
var _datos = { nivel: 3, vida: 100, inventario: ["espada", "escudo"] };

/// a JSON legible (con sangría, para guardar/leer a mano)
var _json = SnapToJSON(_datos, true);      // true = "pretty" (con formato)

/// de vuelta a struct
var _otra_vez = SnapFromJSON(_json);
```

**Formatos disponibles** (pares `SnapTo`/`SnapFrom` verificados en el código):

| Formato | Para qué |
|---|---|
| **JSON** | Universal, servidores, guardado |
| **YAML** | Config legible, archivos de diseño |
| **CSV** | Tablas: enemigos, objetos, balance (se edita en Excel) |
| **XML** | Interoperar con herramientas que lo exigen |
| **VDF** | Formato de Valve (Steam) |
| **QML** | Interfaces Qt |
| **GML** | Serializar como código GML ejecutable |

```gml
/// leer una tabla de enemigos desde CSV (el diseñador la edita en una hoja de cálculo)
var _csv = SnapBufferReadCSV(buffer);   // o SnapFromCSV(texto)
// _csv[0] = { nombre: "goblin", hp: "20", ataque: "5" }  (cada fila un struct)
```

> 💡 **CSV + SNAP es la forma de sacar el balance del código.** El diseñador ajusta el daño de
> cada enemigo en una hoja de cálculo, la exporta a CSV, y el juego la lee con
> `SnapFromCSV`/`SnapBufferReadCSV`. Cambiar el balance no recompila el juego.

---

## 2 · Formatos binarios (compactos, vía búfer)

Para guardado eficiente o red, los formatos binarios pesan mucho menos que el texto:

```gml
/// escribir un struct a MessagePack en un búfer (compacto)
var _buf = buffer_create(1024, buffer_grow, 1);
SnapBufferWriteMessagePack(_buf, _datos);
// … guardar el búfer a archivo o enviarlo por red …

/// leerlo de vuelta
buffer_seek(_buf, buffer_seek_start, 0);
var _leido = SnapBufferReadMessagePack(_buf);
```

También: `SnapBufferWriteBinary`/`ReadBinary` (serialización binaria propia de SNAP, la más
compacta), BSON, Grid (para `ds_grid`), Tilemap.

> ⚠️ **Elige texto o binario según el uso.** Texto (JSON/YAML) para lo que un humano edita o
> depura; binario (MessagePack/Binary) para guardado y red donde el tamaño y la velocidad
> importan. No uses XML para un guardado que nadie va a leer: pesa el triple.

---

## 3 · Casos de uso típicos

| Quiero… | Función |
|---|---|
| Guardar la partida legible | `SnapToJSON(datos, true)` → archivo |
| Guardar la partida compacta | `SnapBufferWriteBinary` → búfer → archivo |
| Leer tabla de balance de CSV | `SnapFromCSV` / `SnapBufferReadCSV` |
| Config editable a mano | `SnapToYAML` / `SnapFromYAML` |
| Hablar con un servidor | `SnapToJSON` (sin pretty) |
| Leer un archivo de Steam (VDF) | `SnapFromVDF` |

---

## La API esencial (verificada en el código)

- **Texto:** `SnapToJSON`/`SnapFromJSON`, `SnapToYAML`/`From`, `SnapToCSV`/`From`, `SnapToXML`/`From`,
  `SnapToVDF`/`From`, `SnapToQML`/`From`, `SnapToGML`/`From`.
- **Búfer/binario:** `SnapBufferWrite/Read` + `Binary`, `MessagePack`, `BSON`, `JSON`, `CSV`,
  `INI`, `YAML`, `XML`, `Grid`, `Tilemap`.
- **Utilidad:** `Snap2DArrayToStructArray` (convertir una tabla en array de structs).

> 🔺 **No están en `buscar.py`** (librería, no runtime). Verifica en
> `11 - Código descargado/librerias/datos-y-estructuras/SNAP/scripts/`.

---

## Ver también

- [14 · Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — el guardado nativo con structs + JSON
- [13 · Estructuras de datos (DS)](../08%20-%20Referencia%20GML%20completa/13%20-%20Estructuras%20de%20datos%20%28DS%29.md) — los ds_* que SNAP serializa
- [16 · Buffers](../08%20-%20Referencia%20GML%20completa/16%20-%20Buffers.md) — los búferes que usan los formatos binarios
- Repo oficial: <https://github.com/JujuAdams/SNAP>
