# UI Layers y Flexpanels (LTS 2026.0)

> Sistema nuevo de interfaces. Se diseña en el **Room Editor**, pero sus capas son **globales a todo el proyecto**.
> Objetivo: matar la necesidad de usar el evento **Draw GUI** para la mayoría de HUDs y menús.

---

## 1. Qué son las UI Layers

Una **UI Layer** es una capa especial que contiene **Flex Panels** (paneles flexibles) y, dentro de ellos, assets de GameMaker (Sprites, Objects, Sequences, Fonts, texto…). Su contenido se dibuja **encima del juego** y **escala automáticamente** para adaptarse al tamaño de la pantalla o de un viewport.

Casos de uso: HUDs, menús de ajustes, barras de vida, inventarios, diálogos, pantallas de pausa.

### 1.1 Cómo crear una

En el Room Editor, desde el menú **"Create Layer"** (icono de añadir capa). La primera vez se crea la carpeta global **"UI Folder"**.

### 1.2 Globales: la gran diferencia

> **La carpeta UI y todas las UI layers dentro de ella se comparten entre TODAS las rooms del proyecto.**

Esto significa:

- Las diseñas **una vez**, en cualquier room, y aparecen en todas las demás (tanto en la IDE como en el juego).
- Para mostrarlas u ocultarlas según la pantalla, **no las recreas**: cambias su visibilidad.
- La UI Folder **no es una capa**: solo agrupa visualmente en el editor. **No se puede recuperar ni operar como capa en runtime**.
- El **nombre de cada UI layer debe ser único**.

### 1.3 Game View: Display o Viewports

Cada UI layer tiene una propiedad **"Game View"** que decide dónde se dibuja:

| Valor | Dónde se dibuja | Cuándo |
|---|---|---|
| **Display** | sobre toda la pantalla, usando el tamaño de la **GUI layer** | entre *Draw GUI Begin* y *Draw GUI* |
| **Viewports** | dentro de cada viewport, usando su posición y tamaño | justo después del evento *Draw*, por viewport |

En la Element List, las capas con "Display" aparecen primero y las de "Viewports" bajo un encabezado propio.

---

## 2. Flexpanels: flexbox en GameMaker

Los **Flex Panels** son la implementación de GameMaker de **flexbox** (CSS Flexible Box Layout), usando la librería **Yoga** (https://yogalayout.dev).

### 2.1 Modelo mental

- La **UI layer en sí es un Flex Panel** (el nodo raíz).
- Un Flex Panel puede contener **otros Flex Panels** y también **assets** (Objects, Sprites, Sequences, Fonts).
- Cada panel tiene propiedades de estilo que definen: su tamaño, su posición relativa dentro del contenedor, y cómo se comportan sus hijos.

```
UI Layer (Panel raíz)
└── Panel contenedor (flexDirection: "row", gap: 16, padding: 20)
    ├── Panel corazones   → Sprite spr_corazon
    ├── Panel puntuacion  → Texto
    └── Panel minimapa    → Object obj_minimapa
```

### 2.2 Propiedades clave (las que más vas a usar)

| Propiedad | Equivalente CSS | Qué hace |
|---|---|---|
| `flexDirection` | `flex-direction` | `"row"` (horizontal) o `"column"` (vertical): define el **eje principal** |
| `justifyContent` | `justify-content` | alineación en el **eje principal** (`"center"`, `"flex-start"`, `"flex-end"`, `"space-between"`…) |
| `alignItems` | `align-items` | alineación en el **eje cruzado** |
| `flex` | `flex-grow/shrink/basis` | cuánto crece el hijo respecto a sus hermanos |
| `flexShrink` | `flex-shrink` | permite que el hijo se encoja si desborda al padre |
| `width` / `height` | `width` / `height` | puede ser número (puntos) o porcentaje (`"60%"`) |
| `padding` | `padding` | espacio interior |
| `margin` | `margin` | espacio exterior |
| `gapRow` / `gapColumn` | `row-gap` / `column-gap` | separación entre hijos |
| `position` | `position` | `"relative"` (por defecto) o `"absolute"` |
| `aspectRatio` | `aspect-ratio` | mantiene proporción |
| `left` / `top` / `right` / `bottom` | — | posición cuando es absoluto |
| `wrap` | `flex-wrap` | permite salto de línea de los hijos |

### 2.3 Editing en el canvas

- Los **Flex Panels** se pueden mover y redimensionar en el canvas, **con restricciones**:
  - Solo puedes mover los que tengan posición **"Absolute"** (los demás se posicionan según el padre).
  - No puedes redimensionar los que tengan tamaño **"Auto"** (lo calcula el layout).
- **Padding** (azul) y **margin** (verde) se arrastran con los selectores de color en los bordes.
  - **ALT** modifica el borde opuesto a la vez.
  - Clic en el selector abre un cuadro para escribir el valor exacto.
- Al arrastrar un panel puedes:
  - mantener **R** para sacarlo y colocarlo en otro contenedor;
  - mantener **C** para clonarlo.

### 2.4 Selección

- Clic normal: selecciona el **primer panel padre** bajo el cursor.
- **ALT + clic**: selecciona el panel más profundo bajo el cursor.
- Doble clic: selecciona el siguiente panel de la jerarquía bajo el cursor.
- Clic derecho: menú con **todos** los paneles bajo el cursor, de arriba a abajo.
- Se puede invertir el comportamiento por defecto en `Preferences > Room Editor > UI layers` con **"Canvas selection selects deepest element by default"**.

### 2.5 Toolbox extra que aparece al usar UI layers

- **Toggle UI canvas preview**: lienzo de previsualización con tamaño personalizado o presets, orientación, offset y **"Clip Contents"**. Solo afecta a la previsualización, no al juego.
- **Show UI Layer node outlines**: contornos de color para cada layer/panel; el color coincide con el de la Element List.
- En el Layer Toolbox aparece el botón de **texto** para colocar elementos de texto.

---

## 3. Comportamiento en runtime

### 3.1 Creación

Las UI Layers se inicializan cuando **empieza la primera room del juego**. Todos sus elementos, **incluidas las instancias**, son **persistentes durante todo el juego**, sin importar cuántas rooms cambies.

Puedes modificar el orden de creación de las instancias de UI en el menú **Instance Creation Order** de la *primera room* (la que esté primera en el Room Manager).

### 3.2 Orden de dibujado (importante saberlo)

```
Draw Event
  └─ Contenido de todas las capas + Draw Begin + Draw de instancias de la room
Viewport UI Layers        ← las de Game View = "Viewports", por viewport
Draw End Event
──────────────────────────
Draw GUI Begin
Display UI Layers         ← las de Game View = "Display", a toda la pantalla
Draw GUI
Draw GUI End
```

### 3.3 Cambios para las instancias dentro de una UI Layer

| Aspecto | Comportamiento |
|---|---|
| `x` / `y` | Devuelven la posición en el **espacio GUI o del viewport**, no en la room. **No les afectan las cámaras.** |
| `bbox_*` | Igual: en espacio GUI/viewport |
| Eventos de ratón | Funcionan con coordenadas en **espacio UI** |
| `mouse_x` / `mouse_y` | En **espacio UI**, no de room |
| Evento **Draw** | Dibuja en el mismo espacio donde está la UI, a la "depth" definida en la Element List |
| Eventos **Draw GUI** | **No hacen nada** |
| Colisiones | Limitadas al **espacio** en que está la instancia: una instancia en una UI layer "Display" **no puede** colisionar con instancias de una capa de room ni de una UI layer "Viewport" |

```gml
// En una instancia colocada en una UI Layer "Display":
// x/y ya están en coordenadas GUI, así que puedes comparar contra el ratón directamente
if (point_in_rectangle(mouse_x, mouse_y, bbox_left, bbox_top, bbox_right, bbox_bottom))
{
    image_index = 1;   // hover
}
```

> TIP del manual: para instancias en UI layers "Display" puedes usar `x`/`y` o los `bbox_*` para hacer comprobaciones manuales contra `mouse_x`/`mouse_y`.

### 3.4 Ocultar una UI layer

```gml
// La forma más simple de "cambiar de pantalla" de UI
layer_set_visible("UI_HUD", false);
layer_set_visible("UI_Pausa", true);
```

> ⚠️ **Desactivar una Object Instance de una UI layer la desactiva** (no se ejecuta ninguno de sus eventos). Igual que si ocultas la capa con el ojo del editor o con `layer_set_visible()`.

---

## 4. Funciones de runtime

### 4.1 `layer_get_flexpanel_node()`

Devuelve el **Flex Panel Node raíz** de una UI layer. Si la capa no es una UI layer, devuelve `undefined`.

```gml
layer_get_flexpanel_node(layer_name);
// layer_name: String
// devuelve: Flex Panel Node o undefined
```

```gml
var _ui_layer = layer_get_flexpanel_node("UILayer_1");

var _hearts_flex = flexpanel_node_get_child(_ui_layer, "Hearts");

flexpanel_node_style_set_width(_hearts_flex, 200, flexpanel_unit.point);
```

### 4.2 `layer_get_type()`

Permite saber el tipo de una capa en runtime (útil para detectar si una capa es de UI).

### 4.3 `on_ui_layer`

Variable de instancia: `true` si la instancia está en una UI layer.

```gml
if (on_ui_layer)
{
    // esta instancia vive en espacio GUI / viewport
}
```

### 4.4 `layer_x()` / `layer_y()`

Desplazan **colectivamente** todos los elementos de una UI layer.

```gml
// Efecto de "sacudida" del HUD
layer_x("UI_HUD", random_range(-3, 3));
layer_y("UI_HUD", random_range(-3, 3));
```

### 4.5 Editar elementos

**La forma fácil**: usa la función `_get_id()` del tipo de elemento.

```gml
// Texto: buscar por nombre y cambiarlo
var _elm = layer_text_get_id("UI_Layer1", "Text1");
layer_text_text(_elm, keyboard_string);
```

```gml
// Girar un sprite del HUD
var _spr = layer_sprite_get_id("UI_Layer1", "Image1");
layer_sprite_xscale(_spr, dsin(-current_time / 10));

// Girar una instancia (se usa su nombre de elemento directamente)
Button1.image_xscale = dsin(current_time / 10);
```

**La forma "larga"** (útil en escenarios grandes): navegar el árbol de nodos.

```gml
// Suponiendo UI_Layer1 > FlexPanel "TextPanel" > Texto
var _node      = layer_get_flexpanel_node("UI_Layer1");
var _text_node = flexpanel_node_get_child(_node, "TextPanel");
var _struct    = flexpanel_node_get_struct(_text_node);
var _text_elm  = _struct.layerElements[0].elementId;

layer_text_text(_text_elm, keyboard_string);
```

El array `layerElements` del struct del nodo contiene los elementos de ese panel; cada uno con su `elementId`.

> **Recomendación del manual:** obtén y guarda los nodos, structs y elementos en el **Create event** (o en otro evento/script de una sola ejecución) y opéralos después donde haga falta. No los busques cada frame.

Para obtener el handle de una **instancia** a partir de su elemento: `layer_instance_get_instance()`.

---

## 5. Flex Panels por código (sin IDE)

Las funciones de Flex Panel **no incluyen renderizado ni soporte de assets**: calculan rectángulos y tú decides qué hacer con esos datos.

### 5.1 Ciclo básico

1. `flexpanel_create_node(struct_o_json)` — crea el árbol
2. `flexpanel_calculate_layout()` — calcula el layout para un tamaño dado
3. `flexpanel_node_layout_get_position()` — obtén posiciones y tamaños
4. Usa esos datos como quieras

```gml
// Create Event
n_root = flexpanel_create_node({
    width: "80%", height: 200, padding: 20,
    nodes: [
        { height: 20 },
        {
            flex: 1, flexDirection: "row",
            nodes: [
                { aspectRatio: 1 },
                { aspectRatio: 1 },
                { aspectRatio: 1 },
            ]
        },
        { height: 20 },
    ]
});
```

### 5.2 Ejemplo: columna con hijos que se encogen

```gml
// Create Event
n_root = flexpanel_create_node({
    left: 20, top: 20,
    width: 400, height: 600,
    flexDirection: "column",
    padding: 20,
    gapRow: 10,
    alignItems: "flex-end"
});

var i = 0;
repeat (6)
{
    flexpanel_node_insert_child(n_root, flexpanel_create_node({
        width: "70%", height: 100, flexShrink: 1,
    }), i);

    i++;
}
```

- `flexDirection: "column"` → los hijos se apilan verticalmente (eje principal).
- `alignItems: "flex-end"` → alineados al final del eje cruzado (a la derecha).
- `flexShrink: 1` → se encogen si desbordan al padre.

### 5.3 Ejemplo: hijo centrado + hijo absoluto

```gml
n_root = flexpanel_create_node({
    left: 20, top: 20,
    width: 800, height: 600,
    justifyContent: "center",
    alignItems: "center",
    nodes: [
        {
            width: "60%", height: "60%",
            nodes: [
                {
                    width: 200, height: 200,
                    right: 20, bottom: 20,
                    position: "absolute"
                }
            ]
        }
    ]
});
```

- El primer hijo se centra por el `justifyContent` + `alignItems` del padre.
- El segundo usa `position: "absolute"` y se coloca en la esquina inferior derecha, independientemente del flujo.

### 5.4 Usar los datos de layout

```gml
// Tras crear el árbol:
flexpanel_calculate_layout(n_root, display_get_gui_width(), display_get_gui_height());

var _pos = flexpanel_node_layout_get_position(n_hijo);

// _pos contiene, entre otros: left, top, width, height
draw_rectangle(_pos.left, _pos.top, _pos.left + _pos.width, _pos.top + _pos.height, true);
```

### 5.5 Containing Block

Algunas propiedades de estilo dependen del **Containing Block** del nodo, que **no siempre es su padre directo**:

- un nodo con `position: "relative"` se posiciona dentro de su **padre directo**;
- un nodo con `position: "absolute"` se posiciona respecto a su **Containing Block**.

Detalle en la documentación de Yoga: https://www.yogalayout.dev/docs/advanced/containing-block

### 5.6 Previsualización en el Debug Overlay

El **Debug Overlay** (`show_debug_overlay()`) incluye una ventana para **probar layouts en tiempo real** con el mismo JSON que le pasarías a `flexpanel_create_node()`. Es la forma rápida de iterar antes de escribir el código. Ese JSON también sirve directamente como struct literal.

---

## 6. Cómo maquetar un HUD responsive (receta práctica)

### Paso 1 — Crea la UI layer

Room Editor → **Create Layer** → UI Layer. Ponle nombre, p. ej. `UI_HUD`, y Game View = **Display**.

### Paso 2 — Estructura de paneles

```
UI_HUD (raíz, Display)
└── HUD_Top (row, width: "100%", padding: 16, justifyContent: "space-between")
    ├── Panel_Vidas   (row, gap: 8)      → 3 sprites spr_corazon
    └── Panel_Puntos                     → texto "Puntos: 0"
└── HUD_Bottom (width: "100%", alignItems: "center")
    └── Barra_Energia (width: "60%", height: 24)  → object obj_barra_energia
```

Claves del responsive:

- Usa **porcentajes** en los anchos para que se adapten.
- Usa `justifyContent: "space-between"` para separar extremos sin números mágicos.
- Usa `flexShrink` en los hijos que puedan desbordar.
- Deja que el tamaño de los iconos sea **fijo** y el de los contenedores **flexible**.

### Paso 3 — Instancias para la interacción

Coloca **Objects** (no solo sprites) donde necesites detectar clics o actualizar valores: los eventos de ratón funcionan en espacio UI y `mouse_x`/`mouse_y` te vienen ya en esas coordenadas.

### Paso 4 — Código de actualización

```gml
// obj_hud_controller — Create Event (una sola vez)
ui_hud       = layer_get_flexpanel_node("UI_HUD");
nodo_vidas   = flexpanel_node_get_child(ui_hud, "Panel_Vidas");
elm_puntos   = layer_text_get_id("UI_HUD", "Texto_Puntos");

// obj_hud_controller — Step Event
layer_text_text(elm_puntos, $"Puntos: {global.puntos}");

// obj_barra_energia (instancia dentro de la UI layer) — Draw Event
var _w = 200;
draw_rectangle(x, y, x + _w, y + 24, true);
draw_rectangle(x, y, x + _w * (energia / energia_max), y + 24, false);
```

### Paso 5 — Cambiar de pantalla

```gml
function ui_mostrar(_nombre)
{
    layer_set_visible("UI_HUD",   _nombre == "UI_HUD");
    layer_set_visible("UI_Menu",  _nombre == "UI_Menu");
    layer_set_visible("UI_Pausa", _nombre == "UI_Pausa");
}
```

### Errores comunes

1. **Usar Draw GUI dentro de una instancia de UI layer** — no hace nada. Usa el evento **Draw**.
2. **Comparar posiciones de room con la UI** — las `x`/`y` de una UI layer están en espacio GUI. No mezcles con coordenadas de cámara.
3. **Esperar colisiones entre UI y mundo** — están en espacios distintos, no colisionan.
4. **Buscar nodos cada frame** — cachea en el Create.
5. **Poner tamaño fijo en todo** — entonces no hay responsive: usa porcentajes y `flex`.

---

## Fuentes

- Manual: UI Layers — https://manual.gamemaker.io/lts/en/The_Asset_Editors/Room_Properties/UI_Layers.htm
- Manual: UI Layers At Runtime — https://manual.gamemaker.io/lts/en/The_Asset_Editors/Room_Properties/UI_Layers_At_Runtime.htm
- Manual: Flex Panels — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Flex_Panels/Flex_Panels.htm
- Manual: `layer_get_flexpanel_node()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/UI_Layers/layer_get_flexpanel_node.htm
- Yoga (librería subyacente) — https://yogalayout.dev
- Containing block (Yoga) — https://www.yogalayout.dev/docs/advanced/containing-block
- Release notes 2026.0.0 (UI Layers y Flexpanels) — https://releases.gamemaker.io/release-notes/2026/0
- Release notes GMRT 0.20.0 (compatibilidad UI Layers) — https://releases.gamemaker.io/release-notes/2026/GMRT_MS_20.html
