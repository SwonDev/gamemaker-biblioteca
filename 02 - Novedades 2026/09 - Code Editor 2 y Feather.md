# Code Editor 2 y Feather (LTS 2026.0)

---

## 1. Code Editor 2

### 1.1 Qué es y estado actual

**Code Editor 2 (CE2)** es el nuevo editor de texto de GameMaker. Trae:

- **eventos unificados** (todos los eventos de un objeto en un mismo editor, en vez de ventanas separadas);
- **ventanas divididas** (split views);
- una experiencia de edición mucho más completa y accesible.

> ⚠️ **Está marcado como Beta dentro de GameMaker.** Tanto el editor como su *language server* tienen todavía bastantes bugs conocidos y cambios por venir.
> Es **opt-in**: desactivado por defecto. Si no lo activas en Preferencias, los assets con documentos de texto (Objects, Scripts, Notes…) seguirán abriendo sus editores respectivos con el **Legacy Code Editor**.

### 1.2 Cómo activarlo

`Preferences > Code Editor 2` (en el manual aparece como *Text Editor 2 Preferences*).

### 1.3 Qué puede editar

Además de **Object Events** y **Scripts**, CE2 edita:

- **Shaders**
- **Timelines**
- **Notes**
- Ficheros de **Extension**
- **Creation code** de una room y de una instancia de room

Y si tu juego tiene **Included Files** o ficheros de extensión de estos formatos, se pueden editar desde el menú derecho:

| Formato | Extensiones |
|---|---|
| JSON | `.json` |
| YAML | `.yml` |
| INI | `.ini`, `.conf` |
| XML | `.xml`, `.xsd`, `.tld`, `.jsp`, `.pt`, `.cpt`, `.dtml`, `.rss`, `.opml` |
| CSV | `.csv` |
| Markdown | `.txt`, `.md` |
| C, C++ | `.c`, `.cpp`, `.cxx`, `.cc`, `.c++`, `.h`, `.hh`, `.hpp`, `.hxx`, `.h++` |
| Objective-C, Objective-C++ | `.m`, `.mm`, `.h`, `.hh` |
| Java | `.java`, `.bsh` |

Cada fichero que el editor abre se llama **"document"**: cada evento de un objeto es un documento distinto, los shaders vertex y fragment son dos documentos, el Creation Code de una room es otro, etc.

### 1.4 Anatomía del editor

#### Barra de navegación (la parte importante)

| Elemento | Qué hace | Atajo |
|---|---|---|
| **Asset Selection** | Cambia el asset que estás editando; el botón `+` crea assets nuevos | `ALT/OPT + 1` (y `+SHIFT` para el menú "Create Asset") |
| **Document Selection** | Cambia el documento: en objetos, el **evento**; en shaders, vertex/fragment; en timelines, los moments. El `+` añade un documento (es decir, añade un evento) | `ALT/OPT + 2` |
| **Declaration Selection** | Salta a una declaración dentro del documento (variable o función). Las declaraciones dentro de un constructor aparecen **indentadas** bajo el nombre del constructor | `ALT/OPT + 3` |
| **Orientation** | Desacopla la barra a su propia ventana o la acopla a cualquiera de los cuatro lados | — |
| **Splitter** | Arrastrándolo divides CE2 en una vista duplicada que muestra el mismo documento. Clic derecho → dividir **verticalmente** | — |

Iconos de declaración:

- icono de variable local → variable local
- icono de función → función
- icono de variable → cualquier otro tipo de variable

Los eventos **heredados de objetos padre** se muestran con un icono especial, **en gris** si están heredados directamente y no sobrescritos.

> ⚠️ Cambiar el documento activo **cierra** las vistas divididas y vuelve a una sola vista.

#### Gutter (márgenes)

De izquierda a derecha:

- **Togglables**: bookmarks y breakpoints. En un documento GML, hacer clic crea un breakpoint.
- **Contextual**: muestra el botón de **Quick Fixes** de Feather cuando el cursor está sobre un error de sintaxis.
- **Line Numbers**: números de línea.
- **Folding**: botones para plegar el documento, bloques `{}` y regions. También se pueden plegar los **casos de `switch`** y los **comentarios multilínea**.

#### Barra de desplazamiento vertical

- **Minimap** junto a la barra (desactivable/redimensionable en preferencias): vista previa del código; al pasar el ratón muestra el código de esa posición.
- Preferencia **"Show diagnostics on scrollbar"**: muestra errores, warnings y sugerencias como líneas pequeñas en la barra.
- **Overscroll**: permite pasar del final del documento. Se activa en preferencias.

#### Barra de desplazamiento horizontal

- Desplegable de **zoom** (afecta a todos los CE2 de la sesión; **no persiste** entre sesiones — para permanente, cambia el tamaño de texto en preferencias o el DPI general).
- Indicador **OVR** si estás en modo sobrescribir.
- **Ln Y, Col X** → clic abre el diálogo "Go To Line" (`CTRL/CMD + G`).
- Desplegable de **lenguaje** del documento (p. ej. "GML"). Al cambiar entre GML Code y GML Visual, **solo se modifica el evento enfocado**.

### 1.5 Ventanas divididas en Workspaces

En la Beta 2026.100 Release 2 ya está la infraestructura para **dividir ventanas de workspace**, pero la función **no está activada todavía** (quedan bugs). Cuando lo esté permitirá cosas como tener dos editores lado a lado en el mismo workspace.

### 1.6 Snippets personalizados

Puedes añadir ficheros `*.tmSnippet` a tu directorio de usuario con **el nombre de un snippet incorporado** para **sobrescribirlo**.

Sirve para:

- dar soporte a estilos de formato alternativos;
- hacer que el código generado incluya siempre tus comentarios;
- lo que quieras.

> ⚠️ Los snippets basados en struct requieren **escapar el carácter `$`** (que normalmente es el salto de línea) con una barra invertida: escribiendo `\$` en el fichero.

### 1.7 Consejo de estilo del equipo de GameMaker

Si pones la llave de apertura **en la línea siguiente** a la declaración, prueba el modo **"Braces"** en lugar de "Full". El modo "Full" hace mucho más y está pensado para estilos populares que llevan la llave **en la misma línea** de la declaración.

### 1.8 Guardado

Cerrar una ventana del editor **guarda automáticamente** los cambios sin guardar de los documentos abiertos.

### 1.9 Bugs corregidos en la Beta 2026.100

- El plegado de regions ya no termina en comentarios multilínea cerrados (R5).
- Renombrar un Script con el mismo nombre que un constructor del script ya no pierde el contenido del constructor al reabrir (R5).
- `#region` en medio de la cabecera JSDoc ya no rompe la declaración (R5).
- "Edit All" y "Open Editors" ya abren **todos** los objetos/scripts de tu selección múltiple, no solo el primero (R4).
- El caret ya no salta al final de la línea al pegar texto con líneas en blanco (R4).
- Duplicar o eliminar *moments* en Timelines ahora funciona de forma fiable (R4).
- Ya no se inestabiliza al escribir caracteres chinos que no estén en la fuente configurada (R4).
- Los cambios hechos **fuera** de GameMaker ya se reflejan en las pestañas de evento abiertas (R3).
- Cambiar un evento al tipo que ya es ya no borra el evento ni su código (R2).
- El ajuste de escala de fuente ya se conserva al cerrar GameMaker (R2).

---

## 2. Feather

### 2.1 Activado por defecto

> **Feather ahora está activado por defecto** si usas **Code Editor 1** (el legacy). Code Editor 2 usa el sistema nuevo de **"Diagnostics"**, que hace lo mismo y más.

Qué aporta: detecta problemas antes de compilar, sugiere mejoras (a menudo aplicables automáticamente vía **Quick Rules**) y comprueba la consistencia de los nombres de assets.

### 2.2 Niveles de severidad

Configurable en `Preferences > Feather Settings`. Controla cuántos warnings ves:

| Nivel | Qué muestra |
|---|---|
| **None** | Solo errores de compilación |
| **Syntax Errors** | Errores de sintaxis + errores de compilación |
| **Type Errors** | Añade warnings de **comprobación de tipos de variables** |
| **All** | Todo lo que Feather ofrece |

También hay preferencia para el modo **"relaxed"** o **"strict"**.

### 2.3 Reglas de nomenclatura

Puedes suministrar **reglas de convención de nombres** en Preferencias, y Feather las usará al revisar tu código para asegurarse de que sigues tus propios estándares.

Esto además alimenta otra novedad: **al crear assets nuevos, el nombre inicial usa los valores de nomenclatura de Feather**.

> Requisito: solo funciona si el valor de *Message Severity* de la regla **2017** **no** está en su valor por defecto "Ignore". Tienes que cambiarlo tú.
>
> Excepciones: algunos tipos de asset (Notes, Extensions…) tienen valores por defecto distintos a propósito, porque normalmente no querrás que cumplan nombres fijos. Y **"Room1" siempre se llamará "Room1"** porque viene del proyecto base.

### 2.4 Novedades de Feather en 2026.0

**Type narrowing básico.** Feather ahora entiende el narrowing con:

- `object_index`
- `typeof`
- `instanceof`
- las funciones integradas `is_*`

```gml
if (is_string(a) && typeof(b) == "number")
{
    // aquí Feather ya sabe que a es string y b es number
}
```

**Tooltips combinados.** Ya no se solapan los tooltips de autocompletado, contenido JSDoc y reglas: se combinan en uno solo.

**Límite de campos de struct en tooltips.** Si un struct tiene demasiados campos, se limitan. Hay preferencia para decir cuántos son "demasiados".

**Autocompletado más inteligente.** Las variables **en ámbito** se resaltan y se priorizan al principio de la lista de sugerencias.

**Reparsed de scripts externos.** Feather reanaliza los scripts cuando se editan **fuera** de GameMaker.

**Rendimiento.** Mejoras importantes en los tiempos de *"Analysing Project…"* al abrir proyectos.

**Errores de sintaxis más fiables.** Si apagas Feather, los "errores antiguos" funcionan mejor y el diálogo se rellena automáticamente al abrirlo.

### 2.5 Cambios de nomenclatura en los TIPOS de Feather

Esto te va a aparecer en los mensajes y tooltips:

| Antes | Ahora |
|---|---|
| **Resource** | **Asset** |
| **Mixed** | **Any** |
| **ArgumentIdentity** | **Any\*** |

Además, los **tipos de elemento** se muestran ahora entre **ángulos de cierre**:

```
Array<Real>
Id.DsList
```

### 2.6 Directivas `// feather` con sufijo `in`

Las directivas se pueden aplicar ahora a **rutas concretas**. El sufijo `in` toma una **ruta de fichero** (insensible a mayúsculas, con la estructura de carpetas del Asset Browser) más la regla o reglas a ignorar.

```gml
// feather ignore GM2017 in *: ignora todas las violaciones de Naming Rules en todo el proyecto
// feather ignore GM1064 in ./*: ignora GM1064 en la carpeta actual y subcarpetas
// feather use type-errors in /Objects/System/*: perfil type-errors solo en Objects/System
// feather use all in /Objects/System/obj_controller: perfil all solo para obj_controller
```

Recomendación del manual: crea un **script vacío en la raíz** del Asset Browser y pon ahí estas directivas.

⚠️ Advertencias:

- Si dos reglas afectan al mismo path/objeto, **no hay garantía** de cuál se aplica.
- Si tienes muchas reglas custom o reglas que afectan a muchos scripts, **puede haber coste de rendimiento**.
- **No puedes usar `..`** para subir de carpeta de forma relativa.

### 2.7 Bugs corregidos en la Beta 2026.100

- Ya no corrompe macros que usan **template strings** al renombrar scripts desde el Asset Browser (R1).
- GameMaker ya no se congela al cambiar rápidamente de configuración antes de que Feather termine de reanalizar (R2).

---

## 3. Novedades de GML relacionadas con el editor

### 3.1 Struct shorthand

GML admite ahora la forma abreviada para construir structs, al estilo de JavaScript:

```gml
// Forma completa
var _datos = { nombre: nombre, vida: vida, nivel: nivel };

// Struct shorthand: si la clave y la variable se llaman igual
var _datos = { nombre, vida, nivel };
```

```gml
// Útil al devolver structs desde funciones
function crear_enemigo(_tipo, _vida)
{
    return { _tipo, _vida, alive: true };
}
```

> ⚠️ No he podido verificar la sintaxis exacta del struct shorthand contra el manual LTS. Confírmala en la sección de Structs antes de usarla en producción:
> https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Structs.htm

### 3.2 Colores CSS en hexadecimal

Puedes escribir colores en formato `#RRGGBB`, igual que en CSS.

```gml
draw_set_colour(#ff8800);
```

> ⚠️ **Cuidado:** `#ff8800` **no** es lo mismo que `$ff8800`. Para que representen el mismo valor hay que intercambiar los pares de bytes:
>
> ```gml
> $2c8edd == #dd8e2c
> ```
>
> Y al escribir hex en un **array literal**, deja un espacio entre `[` y `#`:
> ```gml
> var _cols = [ #ff0000, #00ff00 ];
> ```

### 3.3 Literales binarios

Prefijo `0b`:

```gml
var _seis = 0b0010 | 0b0100;   // 0b0110 → 6
```

### 3.4 Guiones bajos en números

Se ignoran al compilar; solo son separadores visuales:

```gml
var _entero = 100_000_000;           // 100000000
var _flotan = 3_141.59;              // 3141.59
var _hex    = 0xDEAD_BEEF;           // 0xDEADBEEF
var _bin    = 0b01101000_01101001;   // 0b0110100001101001
```

### 3.5 Template strings

Prefijo `$` en un literal de string; lo que va entre `{}` es GML ejecutable:

```gml
var _mundo = "Tierra";
var _t = $"Hola {_mundo}!";

// Equivalentes:
var _t2 = string("Hola {0}!", _mundo);
var _t3 = string_ext("Hola {0}!", [_mundo]);
```

Reglas:

- Todo lo que está entre llaves es GML normal: `$"Resultado: {5 * power(pi, 3) + 37.84094}"`
- El editor **resalta** ese código como GML y **Feather lo analiza**: si metes un accessor incorrecto te lo marca.
- Escapa las llaves con `\` para usarlas como caracteres literales: `\{`
- Solo puedes partir el template en varias líneas **dentro** de las partes de expresión.

Detalle completo en `02 - Cambios en GML 2026.md`.

---

## 4. Recomendaciones de configuración

1. **Activa Code Editor 2**, pero sabiendo que es Beta. Si te encuentras con un bloqueo grave, puedes volver al legacy desde Preferencias.
2. **Antes de reportar un bug de CE2**, busca si ya está reportado y añade un comentario o un thumbs-up en lugar de crear un duplicado. Lo pide explícitamente el equipo de GameMaker.
3. **Sube Feather a "Type Errors" o "All"** en proyectos nuevos. En proyectos heredados grandes, empieza por "Syntax Errors" o tendrás miles de avisos de golpe.
4. **Configura las reglas de nomenclatura** en Preferencias antes de empezar un proyecto nuevo: así los nombres iniciales de assets ya te salen bien.
5. **Usa las directivas `// feather` con `in`** en un script raíz para silenciar reglas por zonas sin apagar Feather entero.
6. **Personaliza los snippets** con `*.tmSnippet` si tienes un estilo de llaves/comentarios propio.

---

## Fuentes

- Manual: Code Editor 2 (Beta) — https://manual.gamemaker.io/lts/en/The_Asset_Editors/The_Text_Editor.htm
- Manual: Feather Settings — https://manual.gamemaker.io/lts/en/Setting_Up_And_Version_Information/IDE_Preferences/Feather_Settings.htm
- Manual: Data Types (literales, colores hex) — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Data_Types.htm
- Manual: Strings (template strings) — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/Strings.htm
- Blog LTS 2026.0 — https://gamemaker.io/en/blog/lts-2026-release
- Release notes 2026.0.0 (Code Editor 2 y Feather) — https://releases.gamemaker.io/release-notes/2026/0
- Release notes Beta 2026.100 — https://releases.gamemaker.io/release-notes/2026/100
