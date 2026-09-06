# Package Manager y Prefabs (LTS 2026.0)

> Dos caras de lo mismo: el **Package Manager** hace la IDE modular, y los **Prefabs** son el contenido que distribuye.
> Por el Package Manager te llegan también **GMRT**, **Code Editor 2**, **Start Page** y **ProjectTool**.

---

## 1. Package Manager

### 1.1 Qué es y qué resuelve

El Package Manager permite **instalar paquetes que GameMaker usa en la IDE y durante la compilación**. Antes, cualquier actualización de una parte de la IDE exigía una versión nueva entera de GameMaker. Ahora no.

Qué se distribuye por aquí:

- **Prefabs** (incluye todos los filtros/efectos del Room Editor, el soporte SDF de fuentes, y todo lo de la Prefab Library)
- Actualizaciones de herramientas: **ProjectTool**, **Code Editor 2**, **Start Page**, **Prefab Builder**
- **Los paquetes de build de GMRT**
- Cualquier otro plugin

### 1.2 Cómo abrirlo

Está en el menú **Windows** (y en `Tools > Package Manager` según la documentación de GMRT).

> ⚠️ **Necesitas tener un proyecto abierto.** La salida del Package Manager va a la ventana *Output*, que solo existe con un proyecto abierto.
>
> ⚠️ Está **ligado a tu cuenta**: si no aparece al pulsarlo, cierra y reabre la IDE y vuelve a loguearte.

### 1.3 Interfaz

- **Lista izquierda**: todos los paquetes del *source* seleccionado.
- **Panel derecho**: información del paquete, selector de versión y botón **Install**.
- **Búsqueda** arriba a la izquierda: filtra por **descripción corta** y por **keywords** (no todos los paquetes oficiales tienen keywords todavía).
- **Arriba a la derecha**: desplegable para cambiar el **source** de los paquetes.

### 1.4 Tipos de paquete

| Tipo | Qué es |
|---|---|
| **Regular** | Contiene ficheros y recursos |
| **Meta Package** | Paquete vacío que **arrastra otros paquetes como dependencias**. Simplifica la instalación y garantiza que te llega todo lo necesario |

El ejemplo típico de metapaquete es **`GMRT - <Plataforma>`**: al instalarlo se instalan automáticamente las herramientas de terceros del SO y las librerías de runtime.

### 1.5 Notificaciones y actualizaciones automáticas

Con el **botón derecho** sobre un paquete puedes activar/desactivar:

- las **notificaciones de actualización** — activadas por defecto para los paquetes de **GMRT**, desactivadas para el resto;
- la **actualización automática** del paquete.

Si hay varias actualizaciones, llegan como **una sola notificación**. Al pulsarla se abre una ventana **"Update All"** desde la que puedes encolar y actualizar todos los paquetes de una vez.

### 1.6 Restricciones al desinstalar

- No puedes desinstalar un paquete si **otro paquete instalado lo usa como dependencia**.
- No puedes desinstalar un paquete **requerido por la IDE** (por ejemplo, Filters and Effects).
- Al desinstalar, según el paquete, puede desinstalar sus dependencias, no hacerlo, o **preguntarte**.

### 1.7 Package Sources

Un *source* es una **URL a un registro remoto**. Al seleccionarlo cambia lo que ves listado, en función de la URL **y de los scopes** del source, que actúan como filtro.

Puedes añadir tus propios sources con el botón `+` junto al desplegable. Para cada source defines:

- nombre en la lista
- URL
- scopes
- usuario / contraseña
- subdirectorio de instalación (bajo la ruta del Package Manager)
- forzar que **todos** los paquetes sean visibles si el registro contiene paquetes ocultos

> Nota: GMPM es un frontend sobre **npm** y **conan**. Para builds por línea de comandos con GM-CLI hay un control para decidir si los scripts remotos de tu nodo custom se ejecutan durante builds de consola (por defecto **no** se ejecutan).

### 1.8 Novedades recientes (Beta 2026.100)

- **R5**: el Package Manager muestra el log de salida cuando hay errores estando en la **Start Page**, para que veas la información útil aunque aún no hayas abierto un proyecto.
- **R2**: capacidad de **validar todos los paquetes instalados y reparar/reinstalar** los que haga falta. Esto evita que un prefab corrupto se quede "atascado".
- Correcciones: paquetes de GMRT que faltaban en Mac y Linux; cuelgue temporal al desinstalar el metapaquete GMRT win-x64; botón "Update" que se quedaba atascado en progreso tras un error.

---

## 2. Prefabs y Prefab Library

### 2.1 Qué es un Prefab

Un **Prefab** es un **proyecto completo e independiente** que aporta contenido listo para usar: personajes, packs de sonido, librerías de gameplay, interfaces…

Un *source project* que contiene assets de Prefab se llama **Collection**.

La clave:

> Cuando usas un asset de la Prefab Library, **no se copia a tu proyecto**: se **referencia**. El asset real se carga desde su Collection **solo cuando compilas el juego**.

Consecuencias:

- Tu juego se mantiene al día con los cambios de la Collection **sin reimportar nada**.
- Puedes usar los mismos assets en varios proyectos y que todos se actualicen a la vez.
- No ocupan espacio en el directorio de tu proyecto.

### 2.2 Cómo abrir la librería

`Windows > Prefab Library` → se abre como panel inferior acoplado. La primera vez estará vacía.

> Puede que ya veas Collections instaladas que la IDE necesita para funcionar, p. ej. **Filters and Effects**.

Para añadir contenido: botón **"Package Manager"**, que abre el Package Manager con el source ya puesto en **"Prefabs"**.

### 2.3 Dónde puedes usar los assets de un Prefab

| Asset de Prefab | Se puede usar en |
|---|---|
| **Sprite** | Object Editor, Sequence Editor, Room Editor, Tile Set Editor, Particle System Editor |
| **Sound** | Sequence Editor |
| **Tile Set** | Room Editor |

### 2.4 Cómo se ven en el proyecto

- Los assets de Prefab **no aparecen en el Asset Browser**, salvo que los customices.
- Sí aparecen en los **Asset Explorers** de los editores (p. ej. al elegir sprite para un objeto).
- Cuando un asset de Prefab está en uso, se muestra con **resaltado naranja**.
- En un Object, el botón "Edit Sprite" se sustituye por **"Open Prefab"**, que abre la Prefab Library con ese asset seleccionado.

### 2.5 Referenciar assets de Prefab en código

Para poder usarlos en código, tu proyecto necesita una **referencia a la Collection**. Se consigue de dos formas:

1. usando uno de sus assets desde la IDE (añade la referencia automáticamente);
2. manualmente, con **"Add Collection Reference"** en el menú derecho de la Prefab Library.

Una vez referenciada, puedes usar sus assets por nombre. Si hay colisiones de nombres, usa la sintaxis:

```
::paquete-version::asset
```

Puedes especificar solo lo que necesites:

```gml
// Nombre simple: tira del Collection referenciado, si no hay colisión
var _s = spr_ui_corazon;

// Última parte del package ID
var _s = ::uiicons::spr_ui_corazon;

// Package ID completo
var _s = ::io.gamemaker.uiicons::spr_ui_corazon;

// Versión major
var _s = ::io.gamemaker.uiicons-1::spr_ui_corazon;

// Versión exacta
var _s = ::io.gamemaker.uiicons-1.0.3::spr_ui_corazon;
```

> ⚠️ Tu proyecto **debe** tener una referencia a la versión que intentas usar, o tendrás error de compilación.
>
> TIP: el package ID se copia desde el Inspector seleccionando la Collection en la Prefab Library.

### 2.6 Símbolos de código exportados

Los Scripts de una Collection pueden exportar **Enums, Macros y Script Functions** con:

```gml
#export simbolo1,simbolo2,simbolo3,...
```

Cualquier proyecto con referencia a esa Collection puede usar esos símbolos.

### 2.7 Modificar macros de un Prefab

```gml
#macro ::<prefab>::[<config>:]<macro> <valor>
```

```gml
// Un Prefab exporta IS_DEBUG como false; lo pongo a true
#macro ::io.gamemaker.platformer::IS_DEBUG true

// Solo para la configuración Release y una versión concreta
#macro ::io.gamemaker.platformer-1.0.0::Release:IS_DEBUG true
```

### 2.8 Modificar Prefabs: Customise vs Duplicate

| Opción | Qué pasa | Cuándo |
|---|---|---|
| **Customise** | Mantiene el enlace con el Collection base y añade una entrada en el Asset Browser (bajo "Prefabs") donde puedes editar **propiedades inspeccionables** | Lo normal: quieres cambiar cosas sin perder las actualizaciones |
| **Duplicate into Project** | **Rompe el enlace** y copia el asset a tu proyecto. Ya no recibe actualizaciones, pero es **totalmente editable** | Cuando vas a reescribir el asset a fondo |

- Al compilar, el asset se saca del Collection **pero se usan tus propiedades modificadas**. Es decir: sigue recibiendo las actualizaciones del original.
- La customización es **por proyecto**: usar el mismo asset en otro proyecto no se ve afectado.
- Puedes customizar **carpetas o colecciones enteras** de una vez (operación recursiva).
- ⚠️ **No todo se puede customizar**: Scripts, Shaders y Notes no (no tienen propiedades personalizables más allá del contenido). Rooms, Extensions y Tile Sets tampoco, por cómo funciona su edición.
- Los **Included Files** que dupliques van directos a la carpeta `datafiles`, así que no aparecen en el Asset Browser.
- Todos tus prefabs **customizados** (no los simplemente enlazados) aparecen en una sección propia del panel **Quick Access** del Asset Browser.

### 2.9 Reinstalar una Collection

Menú derecho sobre la Collection → **"Reinstall Prefab Collection"**. Sirve para "deshacer" customizaciones que ya no quieras y volver al estado original limpio.

### 2.10 Exportar un proyecto con Prefabs

Al exportar como **.yyz**, GameMaker pregunta si quieres incluir las Collections:

| Opción | Efecto |
|---|---|
| **Sí** | Copia las Collections usadas al paquete y **redirige** todas las referencias a la copia, desvinculándolas de las instaladas |
| **No** | Mantiene las referencias pero no copia las Collections; al importar, el usuario necesitará tenerlas instaladas (se le pedirá si no) |

### 2.11 Interfaz de la Prefab Library

**Sección izquierda (Folder List):**

- **Barra de búsqueda** (busca en todas las Collections instaladas)
- **Sort/Filter**: A-Z/Z-A, *Used Collections*, *Used Prefabs Only*, *Customised Prefabs Only*, *Filters & Effects*, *Recent Prefabs*, *Favourites*, *Authors*, *Asset Type*, *Tags*
- **View Menu**: Horizontal (por defecto), Vertical, Simple (sin lista de carpetas), Tree (solo lista de carpetas, mostrando assets para arrastrar)
- **Package Manager**
- **Folder List**: si tienes varias versiones del mismo paquete, aparecen todas y eliges cuál usar (solo una versión por proyecto)
  - Navegación: flechas ↑↓ y ENTER para expandir/colapsar
  - CTRL+clic o SHIFT+clic para selección múltiple

**Sección derecha (Content View):**

- **Path**: jerarquía de carpetas abiertas, navegable
- **View Toggle**: grid o lista
- **Contents**: doble clic en un asset muestra su información (nombre, descripción, icono); arrastra a cualquier editor compatible

**Menú derecho**, opciones destacadas:

- **Make Favourite**
- **Add/Remove Collection Reference**
- **Customise**
- **Reinstall Prefab Collection**
- **Upgrade Prefab Collection** (si hay una versión más nueva instalada)
- **Uninstall Prefab Collection** (no disponible si el proyecto abierto la usa)
- **Duplicate into Project** (recursivo en carpetas)
- **Show In Inspector**
- **Change Prefab Collection Versions**
- **Show in Package Manager**

### 2.12 Novedades de Prefabs en la Beta 2026.100

- **Prefab Builder ya disponible (R5)**: por fin puedes **crear tus propios Prefabs**. Si habías creado Local Packages o publicado en el Marketplace en versiones anteriores, te resultará familiar. Es una primera versión: hay problemas de UI ya reportados, búscalos antes de reportar otros nuevos.
- **R5**: la Prefab Library ya puede **eliminar enlaces a Collections que ya no existen** (si una Collection se despublica y tu proyecto depende de ella, antes quedabas bloqueado sin poder abrir el proyecto).
- **R1**: al abrir un proyecto que usa una versión de Prefab que ya no está disponible, se muestra un **diálogo para elegir** entre quitar el enlace o apuntar a la última versión.
- **R1**: doble clic en un asset ahora hace **Preview** (antes solo por menú derecho).
- **R2**: los prefabs podían figurar como instalados en el Package Manager pero no aparecer en la librería si borrabas el contenido de ProgramData.
- **R2**: ProjectTool exportaba **todos** los Included Files si seleccionabas alguno. Corregido (necesita la última versión de ProjectTool).

---

## 3. Instalar GMRT (resumen operativo)

Detalle completo en `03 - GMRT - El nuevo runtime.md`. Aquí el mínimo:

1. Instala **dotnet 8.0** (obligatorio).
2. Si vas a compilar a WebAssembly, instala **EMSDK 5.0.4** con `emsdk.bat install 5.0.4`.
3. Abre un proyecto cualquiera.
4. `Tools > Package Manager`.
5. Busca **`GMRT - <Tu plataforma>`** e instálalo (es un metapaquete).
6. Para otros targets, instala el **`GMRT Runtime - <Target>`** correspondiente.
7. Cambia el target a `GMRT VM` o `GMRT` y ejecuta.

> Debes estar **logueado** para ver los targets de GMRT. Si tenías GameMaker instalado y ya habías iniciado sesión, puede que necesites pulsar **"Update Licence"** en el panel de cuenta para que aparezcan.

---

## 4. Cómo afecta esto a tu flujo de trabajo

### Cambios prácticos

| Antes | Ahora |
|---|---|
| Actualizar la IDE entera para tener Code Editor 2 al día | **Code Editor 2 se actualiza por Package Manager**, independientemente de la IDE |
| Actualizar la IDE entera para arreglar una conversión de proyecto | **ProjectTool** se actualiza solo; si una importación falla, actualízalo y reintenta |
| Marketplace para contenido externo | **Prefab Library** con versionado y actualizaciones automáticas |
| Filtros y efectos fijos en la IDE | Los **Filters & Effects son un Prefab**, actualizable |
| Runtime fijo por versión de IDE | **GMRT** se instala y versiona por Package Manager |

### Recomendaciones

1. **Abre el Package Manager cada cierto tiempo.** Las notificaciones vienen desactivadas para todo salvo GMRT: actívalas a mano en los paquetes que te importen.
2. **Usa la ventana "Update All"** cuando haya varias actualizaciones pendientes; encola todo de una vez.
3. **Actualiza ProjectTool antes de reportar un fallo de importación.** Es la causa más común.
4. **No dupliques Prefabs por sistema.** Empieza con *Customise*; solo duplica si vas a reescribir el asset entero.
5. **Cuidado con borrar Collections.** Si borras una Collection que tu proyecto usa, tendrás un error de *"Resource load failure"* al abrir el proyecto y posibles errores en runtime.
6. **Al compartir un proyecto**, decide conscientemente si incluyes las Collections en el `.yyz`: incluirlas hace el paquete autocontenido pero más grande.
7. **Añade tus propios sources** con cuidado: los scripts remotos de nodos custom **no** se ejecutan en builds por línea de comandos salvo que lo actives explícitamente.

---

## Fuentes

- Manual: Package Manager — https://manual.gamemaker.io/lts/en/IDE_Tools/Package_Manager.htm
- Manual: Prefab Library — https://manual.gamemaker.io/lts/en/IDE_Tools/Prefab_Library.htm
- Manual: Preferences del Package Manager — https://manual.gamemaker.io/lts/en/Setting_Up_And_Version_Information/IDE_Preferences/Package_Manager_Preferences.htm
- Setup de GMRT (GitHub) — https://github.com/YoYoGames/GMRT-Beta/blob/main/docs/introduction/GMRT-intro-and-setup-instructions.md
- Blog LTS 2026.0 — https://gamemaker.io/en/blog/lts-2026-release
- Release notes 2026.0.0 — https://releases.gamemaker.io/release-notes/2026/0
- Release notes Beta 2026.100 — https://releases.gamemaker.io/release-notes/2026/100
