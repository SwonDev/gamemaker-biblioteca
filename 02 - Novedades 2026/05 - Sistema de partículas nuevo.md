# El nuevo sistema de partículas (LTS 2026.0)

> LTS 2026.0 añade un **editor visual de partículas** y un **nuevo tipo de asset: Particle System**.
> El sistema legacy (`part_system` / `part_type` / `part_emitter`) **sigue existiendo y funcionando igual**. Lo nuevo es una capa por encima.

---

## 1. Qué es exactamente lo nuevo

Dos cosas distintas y complementarias:

1. **El Particle System Editor**: un editor visual dentro de la IDE donde montas efectos de partículas y los **previsualizas en tiempo real**, tal como se verán en el juego.
2. **El asset "Particle System"**: un nuevo tipo de asset en el Asset Browser que guarda ese efecto, reutilizable en rooms, sequences y código.

El blog oficial lo define así: «basado en las partículas existentes de GameMaker, es una forma visual de trabajar con un sistema conocido».

Es decir: **no es un motor de partículas nuevo**. Por debajo siguen siendo `part_system`, `part_type` y `part_emitter`. Lo que cambia es que puedes definirlos visualmente en vez de a base de código y builds de prueba.

---

## 2. El Particle System Editor

Se abre haciendo doble clic en un asset de tipo **Particle System** en el Asset Browser.

### 2.1 Anatomía de un Particle System

```
Particle System (asset)
├── Emitter 1  → emite UN tipo de partícula
├── Emitter 2  → emite OTRO tipo
└── Emitter 3  → ...
```

- Un **Particle System** contiene varios **emitters**.
- Cada emitter emite **un único tipo de partícula**.
- Cada emitter tiene una **región** y una **forma** (rectángulo, elipse, diamante o línea) dentro de la cual se crean las partículas.

### 2.2 Efectos predefinidos (Library)

El editor trae una biblioteca de **presets** con los que partir. Los listados en los release notes son:

`Electricity`, `Embers`, `Embers 2`, `Fire`, `Flame Intensity`, `Rain`, `Smoke`, `Smoke 2`, `Sparks`, `Warp Centre`, `Warp Lines`.

Los presets incorporados **no se pueden modificar**: en cuanto cambias un ajuste del emitter, se **desenlaza** automáticamente.

### 2.3 Presets propios (compartidos entre assets)

Puedes guardar tus propios emitters como presets y compartirlos entre Particle Systems **del mismo proyecto**.

- **Save as Preset**: tras configurar un emitter, guárdalo con un nombre. El emitter queda **enlazado** al preset.
- **Enlazar un emitter a un preset**: en el panel *Library*, pulsa "Select Particles" y elige. Sobrescribe los ajustes actuales (pide confirmación).
- **Qué se guarda en el preset y qué no**:
  - Los **Emitter Settings** (distribución, forma, región) se guardan **al crear** el preset. Si los cambias después, **no** se guardan en el preset.
  - El resto de propiedades (texturas, color, vida, escala…) **se guardan cada vez que las cambias**.
  - Cuando modificas un preset, el cambio se aplica a **todos** los emitters enlazados, incluso en otros assets.
- **Desenlazar**: botón Link/Unlink. El emitter conserva las propiedades del preset pero ya puede cambiarse de forma independiente, y la biblioteca muestra "Custom Particles".
- ⚠️ Los shared emitters son **por proyecto**: no se comparten entre proyectos distintos.

### 2.4 Canvas y Toolbox

**Esquina superior izquierda:**

- **Origin**: punto alrededor del cual se hacen las transformaciones (como el origen de un sprite). Si añades el sistema a una sequence o a un asset layer, su X/Y corresponderán a este origen.
- **Draw Order**: orden de dibujado de las partículas.

| Orden | Comportamiento |
|---|---|
| **Default (old to new)** | Las partículas antiguas se dibujan primero; las nuevas encima |
| **Reversed (new to old)** | Las nuevas primero; las antiguas encima |

- **Copy GML to Clipboard** (icono de GML): copia **el código GML necesario para crear ese sistema en runtime**, con sus emitters y tipos de partícula incluidos. Lo pegas donde quieras y sale exactamente igual.

**Toolbox (esquina superior derecha):**

- **Toggle Canvas Grid**: rejilla de 32×32 por defecto, con opciones de color, alfa, tamaño de celda y snapping. Atajos: `G` (visibilidad) y `Shift + G` (snapping).
- **Canvas Zoom Controls**: zoom in/out, reset a 1:1 (`Ctrl/Cmd + Enter`) y "Window Fit". También con `Ctrl/Cmd` + rueda del ratón.
- **Canvas Settings**: marco del canvas, origen y dimensiones (por defecto **1366×768**), e imagen de fondo como referencia.

**Barra lateral de emitters:**

- Lista de todos los emitters con su región y forma.
- Botones **Add** / **Delete**.
- Clic derecho: delete, cut, copy, duplicate, rename, unlink.
- Icono de **ojo** → desactiva (pausa) el emitter. Icono de **candado** → bloquea sus propiedades.
- Menú de **Docking** para desacoplar/mover la lista.

---

## 3. Formas de usar un Particle System

Hay **tres**, y cada una tiene sus implicaciones.

### 3.1 En una Room (Asset Layer)

Arrastra el asset al canvas del Room Editor con un **Asset Layer** seleccionado.

- El sistema completo, con sus emitters, se añade como un elemento de la capa.
- Previsualízalo en el editor con el botón **Play Animation**.
- Al ejecutar el juego, el sistema se instancia en la capa y **empieza a reproducirse de inmediato**.
- El tipo del elemento es `layerelementtype_particlesystem` (verificable con `layer_get_element_type()`).

> ⚠️ **No puedes obtener el ID del particle system** de los sistemas añadidos así.

### 3.2 En una Sequence

Arrastra el asset al canvas del Sequence Editor.

- Añade una pista (track) de tipo `seqtracktype_particlesystem`.
- ⚠️ **Se añade UNA sola pista para todo el sistema.** Los emitters individuales **no se pueden animar por separado** dentro de la sequence.

### 3.3 En runtime, por código

Usa `part_system_create()` o `part_system_create_layer()` **pasándole el asset** como argumento `partsys` (opcional):

```gml
// Create Event
p_sys = part_system_create(ps_MiEfectoBonito);
```

Al pasar el asset, **GameMaker inicializa el sistema según lo que configuraste en el editor**.

También existe el nodo GML Visual **"Create Particle System"**, que tiene un selector para elegir un asset de particle system opcional.

---

## 4. `particle_add()` y `particle_delete()`

Las dos funciones nuevas para **crear y destruir assets de Particle System en runtime**.

### 4.1 `particle_add(info)`

Crea un nuevo asset de particle system a partir de un **info struct** y lo devuelve.

```gml
particle_add(info);
// info: Particle System Info Struct
// devuelve: Particle System Asset
```

Puedes obtener el struct de tres formas:

- de un asset existente con `particle_get_info()`;
- de una instancia existente con `part_system_get_info()`;
- **escribiéndolo a mano**.

**Notas de uso importantes:**

- Todas las entradas del struct son **opcionales**; las que omitas usan su valor por defecto.
- Todas las entradas se **validan por tipo**: un tipo inválido lanza error.
- La entrada `ind` se **ignora** tanto en emitters como en tipos de partícula.
- La entrada `name` solo se admite en **emitters**; se ignora en el sistema.
- `parttype` de un emitter puede ser:
  - un **ref** a un Particle Type existente (creado con `part_type_create()`), o
  - un **Particle Type Info Struct**, en cuyo caso se crea un tipo nuevo con esas propiedades.
- **Los tipos de partícula creados por esta función pertenecen al asset y se destruyen con él.**

### 4.2 `particle_delete(asset)`

Elimina de memoria un asset creado con `particle_add()`.

### 4.3 Funciones de información

- `particle_exists(asset)` — comprueba si existe
- `particle_get_info(asset)` — devuelve el info struct (incluye emitters y tipos)

---

## 5. Ejemplos

### Ejemplo 1 — Variante de un asset existente

```gml
// Create Event
var _info = particle_get_info(ps_fuente);

// Modifico los tres colores y alfas del tipo del primer emitter
var _type_info = _info.emitters[0].parttype;
_type_info.color1 = c_aqua;
_type_info.color2 = c_blue;
_type_info.color3 = c_white;
_type_info.alpha1 = 1.0;
_type_info.alpha2 = 0.3;
_type_info.alpha3 = 0.0;

// Creo un asset nuevo a partir del modificado
ps_fuente_brillante = particle_add(_info);

// Y una instancia de ese asset
ps_instance = part_system_create_layer("Particles", ps_fuente_brillante);

// Clean Up Event
part_system_destroy(ps_instance);
particle_delete(ps_fuente_brillante);
```

### Ejemplo 2 — Asset creado desde cero en código

```gml
// Create Event
var _info =
{
    emitters:
    [
        {
            mode: ps_mode_stream,
            enabled: true,
            number: 2,
            relative: false,
            xmin: -10,
            xmax: 10,
            ymin: -10,
            ymax: 10,
            distribution: ps_distr_invgaussian,
            shape: ps_shape_rectangle,
            parttype:
            {
                shape: pt_shape_flare,
                life_min: 80,
                life_max: 120,
                dir_min: 0,
                dir_max: 360,
                speed_min: 1,
                speed_max: 1,
                additive: true
            }
        }
    ]
};

ps_blob = particle_add(_info);
ps_instance = part_system_create(ps_blob);
```

Los parámetros no especificados usan valores por defecto. **Tanto el asset como la instancia deben liberarse al terminar.**

### Ejemplo 3 — Reutilizar tipos de partícula existentes

```gml
// Create Event
var _info = particle_get_info(ps_asset_del_ide);
var _type = _info.emitters[0].type;

mi_tipo_custom = part_type_create();

ps_custom = particle_add({
    emitters:
    [
        { parttype: _type },           // reutiliza el tipo del asset del IDE
        { parttype: mi_tipo_custom }   // usa el nuestro
    ]
});

// Clean Up Event
part_type_destroy(mi_tipo_custom);   // este SÍ: lo creamos nosotros
particle_delete(ps_custom);
// El otro tipo NO se destruye: pertenece a un asset del editor y podría
// estar en uso en otro sitio.
```

### Ejemplo 4 — Spawnear partículas sueltas de un asset del editor

```gml
var _info = particle_get_info(ps_explosion);
var _tipo = _info.emitters[0].parttype;

// Crear partículas individuales en un sistema que ya tengas
part_particles_create(mi_sistema, x, y, _tipo, 20);
```

---

## 6. Novedades también en el sistema legacy

El editor no es lo único nuevo: hay funciones nuevas para el sistema de siempre.

### `part_emitter_delay()`

Retrasa la **primera** emisión de un emitter en modo *stream*. El valor se elige al azar entre `delay_min` y `delay_max`.

```gml
part_emitter_delay(ps, ind, delay_min, delay_max, delay_unit);
// delay_unit: constante de Time Source Units (time_source_units_seconds, ...)
```

El temporizador se **pausa** si el emitter está desactivado con `part_emitter_enable()`.

### `part_emitter_interval()`

Define cada cuánto se emiten partículas en modo *stream* (el intervalo entre "ráfagas").

```gml
part_emitter_interval(ps, ind, interval_min, interval_max, interval_unit);
```

### Ejemplo completo

```gml
// Create Event
ps = part_system_create();
part_system_position(ps, x, y);

pe = part_emitter_create(ps);
part_emitter_region(ps, pe, 100, 200, 100, 200, ps_shape_ellipse, ps_distr_linear);

// Espera 1 segundo antes de empezar...
part_emitter_delay(ps, pe, 1, 1, time_source_units_seconds);
// ...y luego emite cada entre 0.4 y 1.1 segundos
part_emitter_interval(ps, pe, 0.4, 1.1, time_source_units_seconds);

pt = part_type_create();
part_emitter_stream(ps, pe, pt, 20);

// Clean Up Event
part_emitter_destroy(ps, pe);
part_system_destroy(ps);
part_type_destroy(pt);
```

> Estas dos funciones son las que usa internamente el editor cuando configuras un temporizador de ráfagas repetidas para previsualizar: el resultado es el mismo que si las llamas tú en código.

### Otras correcciones recientes

- `part_system_angle()` ya funciona correctamente en sistemas **no globales** (Beta 2026.100 R2).
- `part_system_depth()` ya no hace nada si le pasas la profundidad que ya tiene el sistema (Beta 2026.100 R5).

---

## 7. Cuándo usar cada uno

| Situación | Usa |
|---|---|
| Efecto que quieres **diseñar visualmente** e iterar rápido | **Particle System asset** (editor) |
| Efecto que va en una room o sequence sin código | **Particle System asset** |
| Necesitas **variar** un efecto según el juego (color según el jugador, escala según el nivel) | **asset + `particle_get_info()` + `particle_add()`** |
| Efecto totalmente **procedural** generado en runtime | **`part_type_create()` / `part_emitter_create()`** directamente |
| Efectos de un solo uso muy simples (humo, chispas sueltas) | **built-in effects**: `effect_create_depth()` / `effect_create_layer()` |
| Necesitas **interacción** (que las partículas choquen con algo) | **Ninguno**: las partículas no interactúan. Usa instancias. |

```gml
// Built-in effect: lo más rápido para algo simple
effect_create_depth(depth, ef_smoke, x, y, 1, c_gray);
effect_clear();   // limpia todas
```

Regla práctica:

1. **Empieza por el editor** siempre. Es más rápido y el botón *Copy GML to Clipboard* te da el código si luego lo necesitas.
2. **Si necesitas parámetros dinámicos**, parte del asset, modifica el struct con `particle_get_info()` y crea la variante con `particle_add()`.
3. **Solo baja a `part_type_*` a mano** para cosas muy procedurales.

---

## 7 bis. Partículas colocadas en el editor de rooms (`layer_particle_*`)

Además de crear sistemas de partículas por código, puedes **colocar un elemento de partículas
en una capa del editor de rooms** (visualmente) y luego **controlarlo por código** con las 17
funciones `layer_particle_*`. Útil para efectos ambientales fijos: la niebla de una zona, las
chispas de una hoguera que ya está en el nivel.

```gml
/// obtener el elemento de partículas que colocaste en la capa "Efectos"
var _humo = layer_particle_get_id("Efectos", "part_humo");

/// ajustarlo en vivo: color, ángulo, escala, alfa
layer_particle_blend(_humo, c_gray);
layer_particle_angle(_humo, 90);
layer_particle_alpha(_humo, 0.5);

/// llegar al sistema y a la instancia subyacentes para control fino
var _sistema = layer_particle_get_system(_humo);
```

> 💡 **Dos formas de partículas, dos usos:** `part_system_create_layer(capa, ...)` por código
> para efectos dinámicos (una explosión donde muere un enemigo); `layer_particle_*` para
> retocar un efecto **que ya pusiste en el editor** (la atmósfera de una sala). No compiten.

---

## 8. Limitaciones y avisos importantes

### De las partículas en general (siguenvigentes)

- **Las partículas no interactúan con nada**: son puramente gráficas. Si necesitas interacción, usa instancias.
- Cada sistema, emitter y partícula consume memoria: es muy fácil provocar una fuga que degrade y acabe petando el juego.
  - Opción segura: **un sistema global** definido al inicio y destruido al final.
  - Si es dinámico: destruye cada partícula, emitter y sistema **en el momento en que dejen de ser necesarios**.
- No tengas 40.000 partículas a la vez.
- Si defines tu propio sprite de partícula (en vez de uno de los 14 incluidos), que sea **lo más pequeño posible**.
- En **móvil**, dibujar partículas que cubren mucha pantalla es lento (over-draw es la causa principal de tirones).
- En **HTML5** no hay blending aditivo, y sin WebGL tampoco hay blending de color.

### Específicas del nuevo sistema

- ⚠️ **Las IDEs y runtimes antiguos no conocen este tipo de asset.** Si abres o creas un proyecto con este release, **no será editable en versiones anteriores**: se abrirá en modo solo lectura (y en IDEs mucho más antiguas dará error directamente).
- En una **sequence** no puedes animar emitters por separado.
- Si añades el sistema a un **Asset Layer de una room**, no puedes obtener su ID.
- Los presets de emitter son **por proyecto**, no compartidos entre proyectos.
- Si arrastras un Particle System a un proyecto y luego borras la colección (solo aplica si viene de un Prefab), tendrás errores de carga.
  - Fix en Beta 2026.100 R1: ya se puede exportar Particle Systems en paquetes locales e importarlos desde los asset bundles oficiales.

---

## Fuentes

- Manual: The Particle System Editor — https://manual.gamemaker.io/lts/en/The_Asset_Editors/Particle_Systems.htm
- Manual: Particles (índice) — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Particles/Particles.htm
- Manual: `particle_add()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Particles/particle_add.htm
- Manual: `part_emitter_delay()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Particles/Particle_Emitters/part_emitter_delay.htm
- Manual: `part_emitter_interval()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Particles/Particle_Emitters/part_emitter_interval.htm
- Blog LTS 2026.0 — https://gamemaker.io/en/blog/lts-2026-release
- Release notes 2026.0.0 — https://releases.gamemaker.io/release-notes/2026/0
- Release notes Beta 2026.100 — https://releases.gamemaker.io/release-notes/2026/100
