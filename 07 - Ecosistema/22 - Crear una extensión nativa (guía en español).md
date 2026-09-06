# 22 · Crear una extensión nativa (guía en español)

> Cómo hablar con código que GameMaker **no expone**: una SDK del sistema operativo, una
> librería en C/C++, una API de Android o de iOS que no tiene equivalente en GML. El manual
> oficial documenta el proceso entero, en inglés y en un español a veces incompleto; esta guía
> lo recorre de punta a punta con la terminología exacta del IDE y código verificado.
>
> **No cubre:** el catálogo de extensiones ya escritas por otros —eso es
> [07 · 01 §3](./01%20-%20GitHub%20-%20organización%20YoYoGames.md#3-las-extensiones-gmext-44-en-total)
> (las 44 `GMEXT-*` oficiales) y
> [12 · 02](../12%20-%20Utilidades%20e%20integraciones/02%20-%20Extensiones%20nativas%20y%20del%20sistema.md)
> (el mercado de terceros)—, ni la comunicación JavaScript↔GML dentro del propio juego HTML5,
> que ya tiene guía propia en
> [04 · 17 §2](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md#2--javascript--gml)
> (el prefijo `gmcallback_`). Esta guía es el **cómo se construye** una extensión desde cero.
>
> Fuente principal: espejo local
> `09 - Manual oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/` (leído entero,
> es y en) + código fuente real de extensiones oficiales de YoYoGames en
> `11 - Código descargado/extensiones_oficiales/` + el repositorio oficial
> [GM-ExtensionGenerator](https://github.com/YoYoGames/GM-ExtensionGenerator). Verificado el
> 2026-09-06 contra GameMaker LTS 2026.0 (IDE 2026.0.0.16 · runtime 2026.0.0.23).

---

## 0 · ¿Te hace falta de verdad una extensión nativa?

Antes de escribir una línea de C++, comprueba que el runtime no lo resuelve ya. En 2026 hay
funciones nativas para casi todo lo que antes exigía una DLL:

```sh
python3 "_indice/buscar.py" --listar window_
python3 "_indice/buscar.py" --listar clipboard_
python3 "_indice/buscar.py" --listar os_
```

Una extensión nativa solo se justifica cuando necesitas **hablar con el sistema operativo o
con un SDK de terceros** que GML no expone: Bluetooth, cámara, pagos, notificaciones nativas,
una librería de físicas en C++ que ya tienes escrita. Si lo que buscas es una librería de GML
ya hecha (máquina de estados, texto, diálogos), eso es
[07 · 02](./02%20-%20Librerías%20esenciales%20de%20la%20comunidad.md), no esta guía.

---

## 1 · Crear el asset y elegir «Copies To»

1. Clic derecho en cualquier parte del **Navegador de Activos** → **Crear → Extensión**.
2. Nombra la extensión: solo letras, números y `_` (sin espacios ni símbolos).
3. En **«Copies To»** eliges a qué plataformas se exporta este asset. Para una extensión GML
   pura no importa (se ejecuta en todas). Para una específica de plataforma (Android, iOS…)
   **desmarca las que no aplican** — exportarla a una plataforma que no soporta sus ficheros
   rompe el build.

> ⚠️ **Este es el único tipo de recurso que se crea desde el IDE, no desde `gm-cli
> resourcetool`.** Verificado en vivo el 2026-09-06 (`ResourceTool@2026.0.17`, proyecto de
> prueba real):
>
> ```
> $ gm-cli resourcetool eval "resource types" ./Prueba.yyp
> There are 17 resource types:
> animcurve  audiogroup  font  includedfile  notes  object  particlesystem  path
> room  script  shader  shape  sound  sprite  texturegroup  tileset  timeline
> ```
>
> `extension` **no está en la lista**. Y si lo fuerzas:
>
> ```
> $ gm-cli resourcetool eval "resource create type=extension name=ext_prueba" ./Prueba.yyp
> Resource type 'extension' is not creatable
> ```
>
> No es un descuido de esta biblioteca: la propia herramienta lo rechaza. Para este único
> recurso, la regla de «nunca edites `.yy`/`.yyp` a mano, usa `resourcetool`» de
> [`AGENTS.md`](../AGENTS.md) tiene una excepción explícita — usa el IDE, que es el camino
> soportado. Lo que sí puedes automatizar es rellenar sus funciones una vez creada (§6).

---

## 2 · Placeholders, archivos reales y proxies

Un **placeholder** («Add Placeholder») es un fichero vacío que solo sirve para **agrupar**
funciones y macros bajo un nombre — no contiene código real de ninguna plataforma. Se usa
sobre todo para Android e iOS (§7), donde las funciones no viven en el propio placeholder sino
en ficheros fuente aparte.

Un **archivo real** («Add File») sí contiene el código, y su extensión determina la plataforma:

| Fichero | Plataforma | Lenguaje |
|---|---|---|
| `.gml` | Todas | GameMaker Language |
| `.js` | HTML5, GX.games | JavaScript |
| `.dll` | Windows, UWP, Xbox | C/C++ (biblioteca de enlace dinámico) |
| `.dylib` | macOS (no iOS) | C/C++ |
| `.so` | Ubuntu/Linux | C/C++ |
| `.prx` | PlayStation | C/C++ |

> ⚠️ **Al añadir un archivo se copia dentro del proyecto.** Editar el original no cambia nada:
> edita la copia (clic derecho en la extensión → *Abrir en el explorador*).

### Archivos proxy: una extensión, varias plataformas

Si tienes el mismo conjunto de funciones compilado para varios sistemas (una `Haggis.dll` de
Windows y su equivalente `libHaggis.dylib` de macOS), no hace falta duplicar la extensión: la
librería «principal» va como archivo normal y el resto van a **Archivos Proxy**, con nombres
que sigan la convención exacta para que GameMaker los enlace solo:

| Plataforma | Nombres válidos |
|---|---|
| Windows 64 bits | `<Nombre>_x64.dll`, `lib<Nombre>_x64.dll` |
| Ubuntu (Linux) | `<Nombre>.so`, `lib<Nombre>.so`, `<Nombre>_linux.so`, `<Nombre>_arm64.so`… |
| macOS | `<Nombre>.dylib`, `lib<Nombre>.dylib` |
| HTML5, GX.games | `<Nombre>.js` |
| PS4 / PS5 | `<Nombre>_ps4.prx` / `<Nombre>_ps5.prx` |
| Xbox One / Series X\|S | `<Nombre>_xboxone.dll` / `<Nombre>_xboxseriesxs.dll` |

Si el nombre no sigue la convención, GameMaker no sabe qué archivo usar y el juego falla en
runtime sin avisar en compilación. Tabla completa (UWP incluida) en el
[manual oficial](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/Creating_An_Extension.md).

---

## 3 · Escribir el código de la extensión

### 3.1 · Extensión pura en GML (`#define`)

La forma más simple: un fichero de texto `.gml` donde cada función empieza con `#define`. No
hace falta compilar nada — es GML normal, solo que vive en un asset «Extensión» en vez de en
un script.

```gml
/// mi_extension.gml — cada #define es una función que el editor detecta sola

#define c_alice_blue
    return make_color_rgb(240, 248, 255);

#define ext_distancia_2d
    var _dx = argument2 - argument0;
    var _dy = argument3 - argument1;
    return sqrt(_dx * _dx + _dy * _dy);
```

- `#define <nombre>` abre una función; el código que sigue usa `argument0`, `argument1`… para
  leer los parámetros (el sistema de argumentos posicionales clásico de GML, sigue funcionando
  dentro de una extensión aunque en scripts normales prefieras nombrar los parámetros).
- Termina con `return` para devolver un valor a GML.
- Después de crear el fichero, **Add File** lo añade a la extensión; el editor detecta las
  funciones solo, o las añades a mano con **Add Function** (§4).

```gml
/// desde cualquier evento del juego, una vez declarada la función en el editor
draw_set_color(c_alice_blue());
var _distancia = ext_distancia_2d(x, y, other.x, other.y);
```

> 💡 El manual usa como segundo ejemplo una función `instance_create_colour` que mezcla
> `instance_create_layer` con un argumento reciclado como color, de una forma que confunde más
> de lo que enseña. El ejemplo de arriba (`ext_distancia_2d`) demuestra lo mismo —función
> propia, con parámetros y `return`— sin esa ambigüedad.
>
> 🔺 Para una **constante** (sin lógica), un `#macro` normal de GML es más simple que envolverla
> en una función de extensión — el `#define c_alice_blue` de arriba solo tiene sentido si la
> extensión ya existe por otro motivo (agrupar varias plataformas, por ejemplo).

### 3.2 · Extensión nativa — la firma clásica (`double` / `char*`)

Para Windows (`.dll`), macOS (`.dylib`) y Linux (`.so`) escribes C o C++ real. La firma que el
editor de GameMaker espera para cada función exportada es simple a propósito: solo dos tipos
de dato, **`double`** (real) y **`char*`**/cadena. Ejemplo oficial de YoYoGames, íntegro
(`11 - Código descargado/plantillas_y_ejemplos/GameMakerStudio_ExtensionExample/ExampleExtension.cpp`):

```cpp
#if !defined( _MSC_VER)
#define EXPORTED_FN __attribute__((visibility("default")))
#else
#define EXPORTED_FN __declspec(dllexport)
#endif

extern "C" {

// una función que toma un double y devuelve un double
EXPORTED_FN double MyExtension_Function( double _value )
{
    return _value * 100.0;
}

// una función que toma un char* y un double, devuelve un char* (cadena)
EXPORTED_FN char* MyExtension_StringReturn( char* _text, double _value )
{
    char s[1024];
    snprintf(&s[0], 1023, "%s%f", _text, (float)_value);
    return strdup(s);   // GameMaker copia la cadena; no la liberes tú
}

}
```

Reglas de esta firma, verificadas en el manual:

- **Tipo de retorno**: solo `double` o cadena. Si la función no devuelve nada, da igual el tipo.
- **Argumentos**: `double` o cadena, en el orden en que los declares en el editor (§4).
- **Más de 4 argumentos → todos del mismo tipo.** Es una restricción real de esta firma clásica,
  no un capricho: si necesitas mezclar tipos con más de 4 parámetros, o necesitas devolver algo
  que no sea un número o una cadena (un array, un struct), esta firma se queda corta — pasa a §3.3.
- `EXPORTED_FN` (o `__declspec(dllexport)` / `__attribute__((visibility("default")))`) es
  obligatorio: sin él, el símbolo no es visible fuera de la librería y GameMaker no lo encuentra.
- **Funciones Init/Final**: se pueden marcar en el editor para que se llamen solas al empezar y
  al terminar el juego. ⚠️ **Init se llama en todas las plataformas; Final NO** — iOS, Android,
  HTML5, PlayStation y Xbox pueden matar el proceso sin darle tiempo a tu función Final. No
  bases en ella nada crítico (como guardar datos).

### 3.3 · Extensión nativa — la firma moderna, «Called by Reference» con `RValue`

El manual solo documenta la firma clásica de §3.2, pero **las extensiones oficiales de
YoYoGames no la usan**: usan una firma más rica, con acceso directo al tipo interno de GameMaker
(`RValue`), que admite cualquier número y tipo de argumentos, y puede devolver arrays, structs
y no solo `double`/cadena. Esto **no está en el manual mirror de esta biblioteca** — es código
real, verificado abriendo el propio repo oficial descargado en
`11 - Código descargado/extensiones_oficiales/GMEXT-Bluetooth/source/Bluetooth_vs/`. Trátalo
como nivel 5 de autoridad (código, no manual) aunque el autor sea la propia YoYoGames.

La firma de toda función exportada así es siempre la misma:

```cpp
// firma fija: el nombre cambia, la forma no
YYEXPORT void mi_funcion(RValue& Result, CInstance* selfinst, CInstance* otherinst,
                          int argc, RValue* arg)
```

- `Result` — dónde escribes el valor de retorno (con `YYCreateString`, o asignando directamente
  si es un real).
- `argc` / `arg` — cuántos argumentos llegaron y el array de `RValue` para leerlos.
- `selfinst` / `otherinst` — la instancia que llamó a la función (equivalentes a `self`/`other`).

Antes de nada, la extensión tiene que recibir la **tabla de funciones del runtime**
(`YYRunnerInterface`) una vez, al cargar:

```cpp
YYRunnerInterface gs_runnerInterface;
YYRunnerInterface* g_pYYRunnerInterface;

YYEXPORT void YYExtensionInitialise(const struct YYRunnerInterface* _pFunctions, size_t _functions_size)
{
    memcpy(&gs_runnerInterface, _pFunctions, sizeof(YYRunnerInterface));
    g_pYYRunnerInterface = &gs_runnerInterface;
}
```

Esa tabla trae los helpers para leer y crear `RValue` sin tocar su estructura interna a mano:
`YYGetReal`, `YYGetString`, `YYGetBool`, `YYCreateString`, `YYCreateArray`, `CreateDsMap`… Un
ejemplo real y completo, adaptado de `bt_get_address` en `BluetoothCore.cpp`:

```cpp
YYEXPORT void ext_bt_get_address(RValue& Result, CInstance* selfinst, CInstance* otherinst,
                                  int argc, RValue* arg)
{
    YYCreateString(&Result, "");          // valor por defecto: cadena vacía

    HANDLE hRadio = getRadioHandle(__FUNCTION__);
    if (hRadio == nullptr) return;

    BLUETOOTH_RADIO_INFO radioInfo = { sizeof(BLUETOOTH_RADIO_INFO), 0, };
    if (BluetoothGetRadioInfo(hRadio, &radioInfo) == ERROR_SUCCESS) {
        YYCreateString(&Result, AddressToString(radioInfo.address.rgBytes).c_str());
    }
}

// una función con argumentos: se leen con YYGet* e índice de posición
YYEXPORT void ext_sumar(RValue& Result, CInstance* selfinst, CInstance* otherinst,
                         int argc, RValue* arg)
{
    double _a = YYGetReal(arg, 0);
    double _b = YYGetReal(arg, 1);
    Result.val = _a + _b;
    Result.kind = VALUE_REAL;
}
```

**Cuándo usar cada firma:**

| | §3.2 clásica (`double`/`char*`) | §3.3 moderna (`RValue`) |
|---|---|---|
| Complejidad de implementación | Baja | Media (hay que enlazar `YYRunnerInterface`) |
| Argumentos | Máx. 4 tipos mezclados; ilimitados si todos iguales | Cualquier número y tipo |
| Retorno | Solo `double` o cadena | Real, cadena, array, struct, `undefined`… |
| Es lo que usa el manual oficial | Sí (único ejemplo documentado) | No — es lo que usan las `GMEXT-*` reales |
| Referencia | `Extended_Examples.md` del manual | `11 - Código descargado/extensiones_oficiales/` (cualquier `GMEXT-*`, carpeta `source/`) |

Para un ejemplo mínimo con un tipo, tres funciones y un retorno simple, la firma clásica basta
y es lo que documenta el manual. Para algo del tamaño de una integración con Bluetooth, Steam o
un SDK de pagos —lo que hacen de verdad las `GMEXT-*`— vas a necesitar la firma con `RValue`
tarde o temprano.

---

## 4 · Declarar la función en el editor

Tanto si el editor detecta la función sola (extensiones `.gml`) como si la añades a mano
(**Add Function**), estos son los campos:

| Campo | Qué es |
|---|---|
| **Nombre** | Cómo la llamas desde GML. No tiene que coincidir con el símbolo real. |
| **Nombre externo** | El símbolo tal cual está exportado en el binario/fichero. |
| **Ayuda** | Texto del autocompletado y de la ayuda al pie del editor de código. |
| **Tipo de retorno** | `double` o cadena (firma clásica, §3.2). |
| **Argumentos** | Lista ordenada de `double`/cadena. |
| **Argumentos de longitud variable** | Marca esta casilla si hay parámetros opcionales; dentro de la función lees con `argument_count` y `argument[i]`. |
| **Función Init** / **Función Final** | Se llaman solas al empezar/terminar el juego (ver el aviso de Final en §3.2). |

Una vez declarada, la función aparece en el autocompletado de GML como cualquier función
nativa, con su color de sintaxis correspondiente.

---

## 5 · Macros y opciones de extensión

**Macros**: un valor constante o una línea corta de código, definidos en el botón «Macros» de
las propiedades de la extensión — el equivalente a un `#macro` de GML pero empaquetado con la
extensión. Si la macro es una línea de código, **se evalúa cada vez que se usa**.

**Opciones de extensión** (el icono de engranaje junto a «Opciones de extensión»): valores que
el usuario final de tu extensión (o tú, en otro proyecto) configura desde el editor sin tocar
código. Tipos disponibles: **Booleano, Número, Cadena, FilePath, FolderPath, Lista**. Se pueden
agrupar en secciones.

Para leerlas desde GML en tiempo de ejecución:

```gml
var _num_opciones = extension_get_option_count("MiExtension");
var _nombres = extension_get_option_names("MiExtension");
var _valor = extension_get_option_value("MiExtension", "modo_debug");
```

- Solo están disponibles en runtime si la extensión tiene funciones usadas en el juego.
- Si activas «exportar a `options.ini`», el valor también sale en ese fichero, y en los
  [scripts de compilación por lotes](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Runner_Details/Compiler_Batch_Files.md)
  con el nombre `YYEXTOPT_<Extension>_<Opción>`.
- Antes de llamar a cualquier función de una extensión que podría no estar presente en la
  plataforma actual, comprueba con la función real `extension_exists("MiExtension")` — evita
  un crash por «función no encontrada» en la plataforma equivocada.

---

## 6 · `GM-ExtensionGenerator`: generar el esqueleto multiplataforma

Escribir a mano los *bindings* de GML, el *glue* nativo, el proyecto Android y el proyecto iOS
para la misma función es trabajo repetitivo y es exactamente lo que **`extgen`**
(el `GM-ExtensionGenerator` oficial, ver
[07 · 01](./01%20-%20GitHub%20-%20organización%20YoYoGames.md#gm-extensiongenerator)) automatiza
a partir de **un solo fichero de esquema**.

### Instalación

```sh
# .NET 9 SDK · Windows, macOS o Linux
# binarios: https://github.com/YoYoGames/GM-ExtensionGenerator/releases/tag/nightly
extgen --init ./mi-extension/source     # crea el esqueleto de config + esquema
extgen --config ./mi-extension/source/config.json    # genera todo
```

`--init` deja esta estructura (verificado contra la wiki oficial, 2026-09-06):

```
source/
  config.json
  spec.gmidl
  CMakeLists.txt
  CMakePresets.json
  code_gen/            ← generado, no se edita a mano
  src/
    native/
      MiExtension_native.cpp   ← AQUÍ escribes tu lógica
```

### `config.json`: qué genera y dónde lo coloca

```json
{
  "$schema": "./extgen.schema.json",
  "root": "./",
  "input": "spec.gmidl",
  "targets": {
    "windows": { "enabled": true }
  },
  "gamemaker": {
    "wrappers": {
      "outputFile": "../../../scripts/Contador_api/Contador_api.gml",
      "extensionName": "Contador",
      "extensionFileName": "Contador.ext"
    },
    "extension": {
      "mode": "patch",
      "path": "../../../extensions/Contador.yy"
    }
  }
}
```

`"mode": "patch"` es la pieza clave: `extgen` **no crea el asset Extensión** (no puede, §1) —
**rellena uno que ya existe**, apuntando `path` al `.yy` que tú creaste desde el IDE. `targets`
controla para qué plataformas genera código nativo (Windows, Android, iOS/tvOS, consolas), y
`build.emitCmake` si además quieres el proyecto CMake completo.

### `spec.gmidl`: el esquema de la API

GMIDL declara **funciones, clases (structs) y enumeraciones** con tipos explícitos:

```
[gml_api]
module Contador;

[global, bind = typed_gml]
enum ContadorEstado {
    Ok = 0,
    Saturado = 1,
    Error = 2,
}

[global]
class `[[ContadorResultado]]` prototype Object {
    [field]
    property total : int32 { get; set; }
}

[global, bind = typed_gml]
function contador_reset() : unit;

[global, bind = typed_gml, type_hint = `ContadorResultado`]
function contador_sumar(cantidad : int32) : gmval;
```

Tipos directos (sin `type_hint`): `double, float, int32, uint32, int64, bool, string, object,
array, gmval, func, unit` (`unit` solo para retornos). Tipos que sí necesitan `type_hint`:
`uint8, int8, uint16, int16, uint64, buffer`, enumeraciones y clases propias, y colecciones
(`[]`, `[N]`, `?`).

### El flujo completo (verificado contra la wiki oficial, caso iOS/tvOS)

1. **Editar el `.gmidl`** — la API pública, en un sitio.
2. **Ejecutar `extgen --config …`** — regenera bindings GML + proyecto nativo.
3. **Implementar la lógica** en `src/native/*.cpp` — lo único que escribes a mano.
4. **Exportar desde GameMaker** (Suppress Run) — genera el proyecto Xcode/nativo del juego.
5. **`cmake --build <carpeta> --target integrate_gamemaker`** — integra la extensión en ese
   proyecto exportado.
6. **Abrir el IDE nativo (Xcode…) y compilar/depurar.**

> ⚠️ Cada vez que cambies el proyecto de GameMaker hay que repetir 4 y 5 — el paso de
> integración no es automático. El esquema completo de `config.json` (todos los campos de
> `targets`, perfiles `Full`/`BindingsOnly`/`BuildOnly`) solo está documentado en la
> [wiki del repo](https://github.com/YoYoGames/GM-ExtensionGenerator/wiki) — no está reflejada
> en esta biblioteca más allá de lo citado aquí; consúltala si necesitas un campo que no
> aparece en este documento.

---

## 7 · Las plataformas con reglas propias

Android, iOS/tvOS y HTML5 no usan los ficheros de §2: se configuran en su propia pestaña de
propiedades, marcando la casilla correspondiente en **«Plataformas Extra»**.

### 7.1 · Android

1. Marca **Android** en «Plataformas Extra» → se abre la ventana de propiedades Android.
2. **Nombre de clase**: tu extensión puede tener varias clases Java/Kotlin, cada una con sus
   funciones.
3. **Permisos de Android**: los que necesite tu SDK, consultando la
   [documentación de `Manifest.permission`](https://developer.android.com/reference/android/Manifest.permission.html).
4. **Add SDK** / **Add Source**: añaden los ficheros de tu librería o tu código fuente Java al
   directorio `AndroidSource` del proyecto. ⚠️ El manual (es y en, verificado en vivo el
   2026-09-06 contra `manual.gamemaker.io`) **no nombra el formato exacto** que espera «Add
   SDK» — en la práctica del ecosistema Android eso es un `.jar` o un `.aar`, pero esa
   afirmación no está en la fuente oficial, así que trátala como inferencia razonable, no como
   cita textual.
5. **Funciones y macros** se añaden con un **placeholder** normal (§2), como en cualquier
   extensión — Android no tiene un tipo de fichero propio para eso.

**Inyección de código** (pestaña de la extensión): grupos XML con etiquetas `YYAndroid*` que se
insertan en el `build.gradle`, el `AndroidManifest.xml`, `strings.xml` o `proguard-rules.pro`
generados. Las más usadas:

```xml
<YYAndroidManifestApplicationAttributes>
    android:usesCleartextTraffic="true"
</YYAndroidManifestApplicationAttributes>

<YYAndroidGradleDependencies>
    implementation 'com.google.android.gms:play-services-location:21.0.1'
</YYAndroidGradleDependencies>
```

| Grupo de etiqueta | Va a parar a |
|---|---|
| `YYAndroidTopLevelGradle*` | `build.gradle` raíz del proyecto Android |
| `YYAndroidGradle*` | `build.gradle` del módulo |
| `YYAndroidManifest*` | `AndroidManifest.xml` |
| `YYAndroidStringValuesInjection` | `strings.xml` |
| `YYAndroidLayout` | `layout/main.xml` |
| `YYAndroidProguard` | `proguard-rules.pro` |

Dentro de un grupo puedes referenciar variables del proyecto con `${NOMBRE}`
(`applicationId`, `YYAndroidPackageName`…) e **inyección condicional** ligada a una opción de
extensión (§5):

```xml
<YYAndroidManifestApplicationInject>
    <toExpand condition='${YYEXTOPT_MiExtension_UsaAnalitica}'>
        <meta-data android:name="analytics_enabled" android:value="true"/>
    </toExpand>
</YYAndroidManifestApplicationInject>
```

Tabla completa de etiquetas y de valores inyectables (más larga que lo citado aquí) en el
[manual oficial (en)](../09%20-%20Manual%20oficial/manual-lts-2026-en/The_Asset_Editors/Extension_Creation/Android_Extensions.md)
— la traducción española de esta página **es más corta** que la inglesa y omite «Escaping XML
Characters», «Injecting Values» e «Inyección condicional»; para Android, lee la versión en
inglés.

**Callbacks disponibles** en tu clase `.java` (verificado en `Extended_Examples.md`):

```java
public void onStart()
public void onPause()
public void onResume()
public void onActivityResult(int requestCode, int resultCode, Intent data)
public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults)
public void onNewIntent(android.content.Intent newIntent)
```

Ejemplo completo real de una función Android (`Source_Files/GenericTest.md` del manual):

```java
public double AddTwoNumbers(double arg0, double arg1)
{
    double value = arg0 + arg1;
    Log.i("yoyo", arg0 + "+" + arg1 + " = " + value);
    return value;
}
```

Se declara igual que una función clásica de §3.2 (nombre externo `AddTwoNumbers`, dos
argumentos `double`, retorno `double`) y se llama igual desde GML:
`AddTwoNumbers(irandom(100), 50)`.

### 7.2 · iOS / tvOS

1. Marca **iOS** y/o **tvOS** en «Plataformas Extra» (la ventana es idéntica para las dos).
2. **Nombre de clase**, **Compiler/Linker Flags** si el SDK los pide.
3. **System Frameworks**: frameworks de Apple; puedes marcar cada uno como **Referencia
   débil** (lo añade como *Optional* en vez de *Required* en Xcode).
4. **Frameworks de terceros + Bundles**: con opción de **no incrustar**, **incrustar y
   firmar**, o **incrustar sin firmar** — el mismo control que «Frameworks, Librerías y
   Contenido Incrustado» de Xcode.
5. **Add Source**: tus ficheros `.h`/`.mm` van al directorio `iOSSource` de la extensión.
6. **CocoaPods**: si tu SDK se distribuye por Pod, actívalo desde las
   [opciones de juego de iOS](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Game_Options/iOS.md)
   (requiere un `Podfile.lock`).

**App Delegate personalizado**: si necesitas interceptar el ciclo de vida de la app (no solo
las funciones de tu extensión), defines una clase delegada propia y usas dos variables de
entorno que GameMaker sustituye en compilación:

```objectivec
// ${YYExtAppDelegateIncludes} va arriba del .h de tu delegado
// ${YYExtAppDelegateBaseClass} es la clase base de la que heredas
- (BOOL)application:(UIApplication *)application willFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
    if ([[self superclass] instancesRespondToSelector:@selector(application:willFinishLaunchingWithOptions:)])
        return [super application:application willFinishLaunchingWithOptions:launchOptions];
    return TRUE;
}
```

Ejemplo real completo (`Source_Files/GenericTest-iOS.md`, dos funciones de `GenericTest.mm`):

```objectivec
@interface GenericTest : NSObject
{ }
- (double) AddTwoNumbers:(double)arg0 Arg2:(double)arg1;
- (NSString *) BuildAString:(char *)arg0 Arg2:(char *)arg1;
@end

@implementation GenericTest

- (double) AddTwoNumbers:(double)arg0 Arg2:(double)arg1
{
    double value = arg0 + arg1;
    NSLog(@"yoyo: %f + %f = %f", arg0, arg1, value);
    return value;
}

- (NSString *) BuildAString:(char *)arg0 Arg2:(char *)arg1
{
    return [NSString stringWithFormat:@"%s%s", arg0, arg1];
}

@end
```

Callbacks de ciclo de vida disponibles en el `.mm`:

```objectivec
-(void) Init
-(void) onResume
-(void) onPause
-(void) applicationDidEnterBackground:(UIApplication *)application
-(void) applicationWillEnterForeground:(UIApplication *)application
```

**Inyección de código** funciona igual que en Android (§7.1), con sus propias etiquetas
`YYIosPlist`, `YYIosEntitlements`, `YYIosCocoaPods`, `YYIosBuildSettingsInjection`… y sus
equivalentes `YYTvos*`. Tabla completa en el
[manual (es)](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/iOS_Extensions.md).

### 7.3 · HTML5

Para **llamar funciones entre GML y JavaScript dentro del juego** (la extensión `.js` de §2),
la guía es [04 · 17 §1-2](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md):
cubre el mecanismo completo, incluido `gmcallback_`, y no se repite aquí.

Lo que sí es propio de una extensión con destino HTML5 y no está en 04/17 es **inyectar HTML
directo en el `index.html`** del build (distinto de llamar funciones): en la pestaña «HTML5»
de la extensión, con etiquetas de posición:

| Etiqueta | Dónde inserta |
|---|---|
| `GM_HTML5_PreHead` / `GM_HTML5_PostHead` | Antes/después de `<head>` |
| `GM_HTML5_BodyStart` / `GM_HTML5_BodyEnd` | Justo tras `<body>` / antes de `</body>` |
| `GM_HTML5_PreCanvas` / `GM_HTML5_PostCanvas` | Alrededor del `<canvas>` del juego |

Variables disponibles dentro del HTML inyectado, con la sintaxis `${VARIABLE}`:
`GM_HTML5_BrowserTitle`, `GM_HTML5_GameWidth`, `GM_HTML5_GameHeight`, `GM_HTML5_GameFolder`.
También puedes copiar y modificar la plantilla completa (`runtime-[versión]/html5/index.html`)
y usarla como [archivo incluido](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Included_Files.md).

---

## 8 · Varias extensiones, varias plataformas: `Configurations`

Dos extensiones pensadas para el mismo propósito en plataformas distintas (Steamworks y GDK,
por ejemplo) **no deben compilarse a la vez**: si exportas para Steam con el GDK activo, el
build puede fallar o publicar algo que Valve rechace.

La solución del manual: una [configuración](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Configurations.md)
por plataforma de destino, y desactivar el **«Copies To»** (§1) de la extensión que no toca en
cada una:

1. Selecciona la configuración **GDK** → abre la extensión **Steamworks** → desmarca todos sus
   destinos en «Copies To».
2. Cambia a la configuración **Steamworks** → abre la extensión **GDK** → desmarca los suyos.

Repite el mismo patrón con cualquier par de extensiones que se pisen. El detalle completo está
en [`Disabling_Extensions`](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/Disabling_Extensions.md).

---

## 9 · Ejemplos reales para estudiar

No hace falta adivinar cómo se estructura una extensión seria: las **44 `GMEXT-*` de
YoYoGames son código abierto** y están descargadas en
`11 - Código descargado/extensiones_oficiales/`. Catálogo completo en
[07 · 01 §3](./01%20-%20GitHub%20-%20organización%20YoYoGames.md#3-las-extensiones-gmext-44-en-total).
Las usadas como fuente para esta guía:

| Extensión | Qué enseña |
|---|---|
| `GMEXT-Bluetooth/source/Bluetooth_vs/` | La firma `RValue` completa (§3.3), Windows nativo |
| `GMEXT-Bluetooth/source/Bluetooth_xcode/` | La misma extensión, lado macOS |
| `GMEXT-AppleIAP/source/AppleIAP_xcode/` | `RValue` + integración con StoreKit |

Plantillas de terceros, ya descargadas y catalogadas en
[12 · 02 §6](../12%20-%20Utilidades%20e%20integraciones/02%20-%20Extensiones%20nativas%20y%20del%20sistema.md#6-escribir-tu-propia-extensión):
`GMSDLL` (C++) y `GMSDLL.rs` (Rust), de YellowAfterlife.

---

## 10 · Checklist antes de compilar

- [ ] El asset Extensión existe y tiene el **Copies To** correcto (§1) — si es específica de
      plataforma, todas las demás están desmarcadas.
- [ ] Cada función tiene **nombre**, **nombre externo** y **tipo de retorno** declarados (§4).
- [ ] Si usas la firma clásica (§3.2) y tienes más de 4 argumentos: **todos del mismo tipo**.
- [ ] Si usas la firma `RValue` (§3.3): `YYExtensionInitialise` guarda la tabla de funciones
      antes de que se llame a ninguna otra.
- [ ] Ninguna lógica crítica depende de la **función Final** en iOS/Android/HTML5/consolas.
- [ ] Antes de llamar a una función específica de plataforma, compruebas
      `extension_exists(...)` u `os_type`.
- [ ] Si hay dos extensiones que se pisan (Steam/GDK…), cada configuración tiene desactivada
      la que no toca (§8).
- [ ] `gm-cli compile` sin errores en cada plataforma de destino real.

---

## 11 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Cómo evitarlo |
|---|---|---|
| «Function not found» en runtime, funcionaba en el IDE | El archivo no se copió al proyecto o editaste el original, no la copia | Edita siempre la copia (§2); reimporta con «Add File» si dudas |
| Un `.jar`/librería Android no aparece en el build | Añadido con «Add Source» en vez de «Add SDK», o al revés | Revisa qué botón corresponde a tu tipo de fichero (§7.1) |
| El juego se cierra al salir sin ejecutar tu limpieza | Confiaste en la función Final en una plataforma que no la llama | Guarda datos críticos en el evento normal del juego, no en Final (§3.2) |
| Función con 5 argumentos de tipos distintos no compila | Firma clásica: límite de 4 argumentos si son de tipos distintos | Cambia a la firma `RValue` (§3.3) o agrupa en menos parámetros (un struct/JSON serializado como cadena) |
| Un archivo proxy no se usa nunca | El nombre no sigue la convención exacta de la plataforma | Compara contra la tabla de §2 letra por letra, incluido el `lib` inicial |
| Dos extensiones truncan el build al exportar para una plataforma | Ambas tienen «Copies To» activo para el mismo destino | Configurations + desactivar la que no toca (§8) |
| `extgen` no toca tu extensión | `config.json` con `"mode": "patch"` apunta a un `.yy` que no existe todavía | Crea primero el asset vacío desde el IDE (§1), luego ejecuta `extgen` |

---

## Ver también

- [07 · 01 §3 — Las 44 `GMEXT-*` oficiales](./01%20-%20GitHub%20-%20organización%20YoYoGames.md#3-las-extensiones-gmext-44-en-total) — ejemplos reales completos para leer
- [07 · 01 — `GM-ExtensionGenerator`](./01%20-%20GitHub%20-%20organización%20YoYoGames.md#gm-extensiongenerator) — la ficha del repo
- [12 · 02 — Extensiones nativas y del sistema](../12%20-%20Utilidades%20e%20integraciones/02%20-%20Extensiones%20nativas%20y%20del%20sistema.md) — el catálogo: qué ya existe antes de escribir la tuya
- [04 · 17 — Interoperabilidad con la web (HTML5)](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md) — JS↔GML dentro del juego, con `gmcallback_`
- [13 · 06 — Arquitectura de un proyecto GameMaker](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) — dónde encaja una extensión en la arquitectura general
- Manual oficial: [Creating an Extension](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/Creating_An_Extension.md) · [Android Extensions](../09%20-%20Manual%20oficial/manual-lts-2026-en/The_Asset_Editors/Extension_Creation/Android_Extensions.md) · [iOS/tvOS Extensions](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/iOS_Extensions.md) · [HTML5 Extensions](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/HTML5_Extensions.md) · [Disabling Extensions](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/Disabling_Extensions.md) · [Extended Examples](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/Extended_Examples.md)

---

## Fuentes

- Manual oficial de GameMaker, espejo local (leído entero para esta guía, es y en):
  `09 - Manual oficial/manual-lts-2026-es/The_Asset_Editors/Extension_Creation/` — páginas
  `Creating_An_Extension`, `Android_Extensions`, `iOS_Extensions`, `HTML5_Extensions`,
  `Disabling_Extensions`, `Extended_Examples` y sus `Source_Files/`.
- `manual.gamemaker.io/lts/en/The_Asset_Editors/Extension_Creation/Android_Extensions.htm` —
  verificado en vivo con `curl -A "Mozilla/5.0"` el 2026-09-06 (HTTP 200) para confirmar que el
  texto sobre «Add SDK» no menciona `.jar`/`.aar`.
- Código fuente real de extensiones oficiales de YoYoGames:
  `11 - Código descargado/extensiones_oficiales/GMEXT-Bluetooth/source/Bluetooth_vs/`
  (`YYRValue.h`, `Extension_Interface.h`, `BluetoothCore.cpp`) y
  `GMEXT-AppleIAP/source/AppleIAP_xcode/` — repos oficiales en
  <https://github.com/YoYoGames/GMEXT-Bluetooth> y <https://github.com/YoYoGames/GMEXT-AppleIAP>.
- Ejemplo oficial mínimo: `11 - Código descargado/plantillas_y_ejemplos/GameMakerStudio_ExtensionExample/ExampleExtension.cpp`.
- <https://github.com/YoYoGames/GM-ExtensionGenerator> — README, leído el 2026-09-06.
- Wiki de GM-ExtensionGenerator, páginas `getting_started_sample`, `user_gmidl_docs` y
  `user_impl_workflow` en <https://github.com/YoYoGames/GM-ExtensionGenerator/wiki> —
  consultadas vía WebFetch el 2026-09-06.
- Verificación en vivo de `gm-cli resourcetool` (`ResourceTool@2026.0.17`) sobre un proyecto de
  prueba real, 2026-09-06: `resource types` (17 tipos, sin `extension`) y
  `resource create type=extension` (`Resource type 'extension' is not creatable`).
