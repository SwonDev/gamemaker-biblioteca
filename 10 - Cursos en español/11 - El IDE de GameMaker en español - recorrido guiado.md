# 11 · El IDE de GameMaker en español — recorrido guiado

> **Fuente de partida:** [*Interfaz General [Game Maker 2024]*](https://youtu.be/KRJhX4YgcHo)
> de [Altair_AML](https://www.youtube.com/channel/UCMP5XWWzhJ_A6DPNKNfQVOw) · 17:08 · marzo de 2024.
>
> Apuntes propios: el recorrido del vídeo, **actualizado a LTS 2026** y con cada zona del IDE
> enlazada a **su página del manual oficial en español**, que ya está completo en esta
> biblioteca.

---

## Para qué sirve este documento

Es el **mapa de «dónde está cada cosa»** en el IDE, en español. Si un agente necesita explicar
a alguien dónde se cambia un ajuste, esta es la ruta corta; y desde cada punto se salta al
manual oficial para el detalle.

---

## 1 · El navegador de recursos (Asset Browser)

El panel de la derecha. Es el índice de todo lo que contiene tu juego.

📘 [El navegador de recursos](../09%20-%20Manual%20oficial/manual-lts-2026-es/Introduction/The_Asset_Browser.md)

**Lo que conviene saber desde el primer día:**

- **Clic derecho → Create** para cualquier recurso nuevo.
- **Las carpetas por defecto son solo una sugerencia.** Puedes borrarlas y montar tu propia
  estructura; el `.yyp` no depende de ellas.
- **Colores de carpeta** (clic derecho): separar visualmente enemigos, UI y sistemas ahorra
  mucho tiempo cuando el proyecto crece.
- **Orden**: alfabético o **Custom Order** (arrastrar a mano). El orden personalizado se guarda
  en el archivo `.resource_order`, no en el `.yyp`.
- **Etiquetas (tags)**: clasificación transversal, independiente de las carpetas. Y —esto es lo
  interesante— **se pueden consultar desde código** con
  [`asset_has_tags`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Assets_And_Tags/asset_has_tags.md)
  y `tag_get_assets`. Sirven para agrupar en tiempo de ejecución.
- **Favoritos** para los cuatro recursos que abres cincuenta veces al día.
- **Room Order**: qué room arranca primero. El juego empieza siempre por la primera de la lista.

---

## 2 · Los tipos de recurso, uno por uno

| Recurso | Para qué | Manual (español) |
|---|---|---|
| **Objects** | El núcleo: aquí va el código y los eventos | [Objetos](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Objects.md) |
| **Sprites** | Imagen, animación **y máscara de colisión** | [Sprites](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sprites.md) |
| **Rooms** | Los niveles: capas, cámaras, instancias | [Rooms](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Rooms.md) |
| **Sounds** | Audio, con opciones de compresión y calidad | [Sonidos](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sounds.md) |
| **Scripts** | Funciones globales reutilizables | [Scripts](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Scripts.md) |
| **Fonts** | Fuentes del sistema o de archivo | [Fuentes](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Fonts.md) |
| **Tile Sets** | Mosaicos para construir escenarios | [Tile sets](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Tile_Sets.md) |
| **Paths** | Rutas que un objeto puede seguir | [Rutas](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Paths.md) |
| **Sequences** | Editor de animación y escenas | [Secuencias](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sequences.md) |
| **Animation Curves** | Curvas de interpolación (easing) | [Curvas de animación](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Animation_Curves.md) |
| **Particle Systems** | Editor visual de partículas | [Sistemas de partículas](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Particle_Systems.md) |
| **Shaders** | GLSL para efectos gráficos | [Shaders](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Shaders.md) |
| **Extensions** | Código nativo y SDKs externos | [Extensiones](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Extensions.md) |
| **Notes** | Notas de texto dentro del proyecto | [Notas](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Notes.md) |
| **Timelines** | Secuencias de acciones por tiempo | [Líneas de tiempo](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Timelines.md) |

### Los tres que la gente descubre tarde

**Sistemas de partículas.** Antes había que montar las partículas a mano en código. Ahora hay
**editor visual** con vista previa en tiempo real, y un botón **Copy GML to Clipboard** que te
da el código equivalente. Está explicado en
[10 · Cursos, apuntes de partículas](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Particle_Systems.md).

**Secuencias.** Un editor de animación por líneas de tiempo: mueves sprites, disparas sonidos y
montas escenas cinemáticas sin programarlas. Para intros y cutscenes ahorra muchísimo.

**Curvas de animación.** Curvas de easing reutilizables. Se combinan con secuencias y se leen
desde código para que un movimiento acelere y frene con criterio en vez de ser lineal.

---

## 3 · El editor de sprites

Doble clic en la imagen de un sprite y entras a un editor de pixel art **integrado**. No
sustituye a Aseprite, pero para retoques, pruebas y prototipos evita el viaje de ida y vuelta a
un programa externo.

📘 [Editor de imagen](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sprites.md)

**Los dos ajustes que más problemas causan si se ignoran:**

1. **El origen.** Determina el punto sobre el que el sprite rota y escala, y qué significan `x`
   e `y` para el objeto. Para un personaje de plataformas: **abajo y centrado**. Ver
   [por qué](./09%20-%20Plataformas%20para%20principiantes%20-%20apuntes%20de%20Alas%20de%20reptil%202025.md#1--antes-del-código-sprites-origen-y-room).
   📘 [Origen del sprite](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sprites.md)
2. **La máscara de colisión.** Por defecto se calcula del propio dibujo. Para personajes casi
   siempre quieres una **máscara rectangular propia y estable**, no una que cambie con cada
   animación.
   📘 [Máscara de colisión](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sprites.md)

También aquí: **FPS de la animación** (los sprites nuevos vienen rápidos; bájalo) y
**Nine Slice** para marcos de interfaz que se estiran sin deformarse.

---

## 4 · El editor de rooms

Donde montas los niveles. Lo esencial es entender que **todo va por capas**:

| Tipo de capa | Contiene |
|---|---|
| **Instances** | Instancias de objetos |
| **Tiles** | Mosaicos de un tile set |
| **Backgrounds** | Fondos, con repetición y desplazamiento |
| **Assets** | Sprites, secuencias y sistemas de partículas sueltos |
| **Paths** | Rutas |
| **Effects (FX)** | Filtros y efectos aplicados a todo lo que hay debajo |
| **UI Layers** 🆕 | Interfaces con Flex Panels — **novedad de 2026** |

📘 [Rooms](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Rooms.md) ·
📘 [Propiedades de capa](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Room_Properties/Layer_Properties.md)

> 🔺 **Novedad de 2026 que el vídeo no puede tener:** las **capas de UI** con
> [Flex Panels](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Flex_Panels/Flex_Panels.md)
> permiten montar interfaces con un sistema tipo flexbox, que se adapta solo a la resolución.
> Es el cambio más grande del editor de rooms en años. Ver
> [02 - Novedades 2026](../02%20-%20Novedades%202026/).

**Capas de efecto (FX):** el vídeo las destaca con razón. Aplican un shader a todas las capas
inferiores sin escribir GLSL: viñeta, desenfoque, corrección de color.
📘 [Filtros y efectos](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Room_Properties/Filters_and_Effects.md)

---

## 5 · Menús y ventanas que vas a usar

| Dónde | Para qué | Manual |
|---|---|---|
| **File → Preferences** | Ajustes del IDE, atajos, tema | [Preferencias](../09%20-%20Manual%20oficial/manual-lts-2026-es/Setting_Up_And_Version_Information/IDE_Preferences.md) |
| **Game Options** | Ajustes **del juego** por plataforma | [Opciones del juego](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Game_Options.md) |
| **Tools → Import Local Package** | Instalar librerías `.yymps` | [Paquetes locales](../09%20-%20Manual%20oficial/manual-lts-2026-es/IDE_Navigation/Menus/The_Tools_Menu.md) |
| **Windows → Output** | Errores de compilación y `show_debug_message` | [Ventana de salida](../09%20-%20Manual%20oficial/manual-lts-2026-es/Introduction/The_Output_Window.md) |
| **Windows → Package Manager** 🆕 | Paquetes e IDE (GMRT, prefabs) | [Gestor de paquetes](../09%20-%20Manual%20oficial/manual-lts-2026-es/IDE_Tools/Package_Manager.md) |
| **Windows → Prefab Library** 🆕 | Recursos compartidos entre proyectos | [Biblioteca de prefabs](../09%20-%20Manual%20oficial/manual-lts-2026-es/IDE_Tools/Prefab_Library.md) |
| **Debugger** | Puntos de interrupción, variables en vivo | [El depurador](../09%20-%20Manual%20oficial/manual-lts-2026-es/IDE_Tools/The_Debugger.md) |

> ⚠️ **No confundas Preferences con Game Options.** *Preferences* configura **tu IDE** (no viaja
> con el proyecto). *Game Options* configura **el juego** (resolución, iconos, permisos, firma)
> y sí viaja con él. Es un error muy común.

---

## 6 · Lo que ha cambiado desde el vídeo (2024 → LTS 2026)

| Novedad | Qué es |
|---|---|
| **Capas de UI + Flex Panels** | Interfaces adaptables en el editor de rooms |
| **Code Editor 2** | Editor nuevo: minimapa, multicursor, corchetes arcoíris. Opcional: se activa en preferencias |
| **Gestor de paquetes** | Instalación de componentes del IDE y de GMRT |
| **Biblioteca de prefabs** | Recursos referenciados entre proyectos, no copiados |
| **Handles en vez de IDs** | Los recursos ya no son enteros: no hagas aritmética con ellos |
| **GMRT (beta)** | Runtime nuevo, en paralelo al GMS2 de siempre |

Detalle completo en [02 - Novedades 2026](../02%20-%20Novedades%202026/).

---

## Atajos que compensa memorizar

| Atajo | Qué hace |
|---|---|
| `F5` | Ejecutar el juego |
| `F6` | Ejecutar con depurador |
| `Ctrl/Cmd + Shift + F` | Buscar en **todo** el proyecto |
| `Ctrl/Cmd + K` / `+ Shift + K` | Comentar / descomentar |
| `F1` | Ir a la declaración, o al manual si es una función integrada |
| `Ctrl/Cmd + G` | Ir a línea |

📘 [Atajos de teclado](../09%20-%20Manual%20oficial/manual-lts-2026-es/Setting_Up_And_Version_Information/IDE_Preferences/Redefine_Keys_Preferences.md)

> 💡 **`F1` es el atajo más infravalorado del IDE.** Con el cursor sobre cualquier función
> integrada te lleva a su página del manual. Y como en esta biblioteca el manual **está
> completo en español**, puedes leer esa misma página en tu idioma:
> `python3 "_indice/buscar.py" <función>`.

---

Fuente original: canal [Altair_AML](https://www.youtube.com/channel/UCMP5XWWzhJ_A6DPNKNfQVOw).
