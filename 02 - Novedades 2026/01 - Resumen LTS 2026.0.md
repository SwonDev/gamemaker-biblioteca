# Resumen ejecutivo: GameMaker LTS 2026.0

> Documento de referencia personal. Fecha del snapshot: **agosto de 2026**.
> Versión estable documentada: **GameMaker LTS 2026.0.0 (Minor Update 1)** — IDE **2026.0.0.16**, runtime **GMS2 RT 23**.
> Beta más reciente consultada: **2026.100.0 Release 5** (IDE 1139 / GMS2 RT 1090, 27/08/2026).
> GMRT más reciente: **0.21.0** (julio 2026).

---

## 1. Qué es LTS y por qué cambia el modelo

Hasta ahora GameMaker convivía con dos canales: *Monthly* (cada dos meses) y *LTS* (congelado). Eso desaparece.

A partir de 2026 **LTS es la versión principal** y todo el desarrollo se concentra en ella, acompañada de una corriente de **Betas frecuentes** para testers tempranos. La serie *Monthly* se da por terminada: `2024.14.4` (octubre 2025) fue la última.

Diferencia clave respecto al LTS anterior: el LTS anterior se basaba en una versión de **2022**; este se basa en la versión más reciente de 2026, así que incluye *años* de cambios acumulados de golpe.

### Instalación separada

- LTS 2026.0 es **una instalación nueva e independiente**: no reemplaza tus instalaciones previas de LTS 2022, Monthly o Beta.
- Antes de migrar un proyecto: **backup o control de versiones**. Obligatorio.
- Tras instalar tendrás que **reaplicar las reglas de permisos/antivirus** del firewall, porque es una ruta nueva. Ver la guía de permisos en el wiki oficial.

---

## 2. Ciclo de vida planificado (2026 → Q1 2028)

| Versión | Ventana prevista |
|---|---|
| **2026.0** | Q2 2026 (publicada, 21/05/2026) |
| **2026.1** | Q4 2026 |
| **2026.2** | Q1 2027 |
| **2026.3** | Q4 2027 |
| **2026.4** | Q1 2028 |

### Qué pasa con el runtime GMS2 (VM / YYC)

> **LTS 2026 marca el runtime GMS2 como *feature complete*.**

Esto es lo más importante del release:

- **Todas las peticiones de funcionalidad nuevas y pendientes solo se considerarán para GMRT.** Ni una más en GMS2.
- El runtime GMS2 seguirá recibiendo soporte **hasta al menos Q1 2028**, pero **solo actualizaciones de SDK y correcciones de bugs críticos**.
- Los suscriptores **Enterprise** tienen acceso al código fuente del runtime y pueden recibir parches y actualizaciones de SDK al margen del ciclo LTS26.
- En la IDE, "VM" pasa a llamarse **GMS2 VM** y "YYC" pasa a llamarse **GMS2 YYC**, precisamente para dejar claro que lo nuevo va a GMRT.

Además, durante el ciclo LTS26 se publicará una **Beta con todos los fixes** cada vez que haya cambios y pasen los tests automáticos, para no tener que esperar a las versiones programadas.

---

## 3. Novedades de la IDE

### 3.1 Flujo de arranque y cuentas

- **Ya no hay que iniciar sesión obligatoriamente.** Puedes entrar como "guest" y trabajar con normalidad; solo te pedirá login cuando hagas algo que requiera licencia (Run, Create Exe, subir a GX Community…).
- Si configuras preferencias como invitado y luego te logueas **sin carpeta de usuario previa**, GM copia tus ajustes de invitado a la cuenta nueva.
- Cerrar sesión y volver a invitado **resetea** preferencias, lista de dispositivos y proyectos recientes.
- Nuevo panel **Account** en la barra de herramientas (antes "Logout"/"My Account" estaban en File). "My Account" se divide en *GameMaker Account* y *Opera Account*.
- Se elimina la UI de login "Legacy": ahora **todo el mundo inicia sesión por el navegador** (allí sigue existiendo la opción Legacy junto a SSO).
- Los controles de **proxy** se mueven a `Preferences > General Settings > Proxy Settings`.

### 3.2 Actualizador integrado

- GameMaker comprueba versiones nuevas al arrancar; la notificación aparece cuando la Start Page ya ha cargado (no al inicio).
- Puedes forzar la comprobación desde el menú **Help**.
- Descarga el instalador en segundo plano mientras sigues trabajando y luego pregunta si reiniciar para instalar.
- El propio actualizador se descarga silenciosamente en el primer arranque, igual que los runtimes, y **se puede actualizar desde el Package Manager**.
- Disponible en **Windows y macOS**. No en las Betas de Ubuntu.

### 3.3 Runtimes descargables por módulos

- Al instalar/actualizar aparece el diálogo **Runtime Modules**, donde eliges qué módulos descargar (solo tu SO, lo que necesites ahora, o todo).
- El módulo "Base" ya no incluye herramientas de los tres SOs: solo las del tuyo → descargas más pequeñas.
- Se modifica desde el botón en `Preferences > Runtime Feeds`. **El diálogo instala módulos nuevos pero no borra los existentes**: para quitarlos hay que cambiar el ajuste y borrar la carpeta de runtimes a mano.
- Ya no se te obliga a tener el runtime original de una IDE si hay uno más nuevo activo (debe ser de la misma "familia": un runtime 2026.1 no vale para la IDE 2026.0).
- Target Manager muestra iconos de estado de qué runtimes hay instalados.
- Nueva preferencia para el **target por defecto** (por defecto, el SO donde corres GameMaker).

### 3.4 Asset Browser y proyectos

- Los proyectos nuevos **ya no crean los grupos por defecto** (Sprites, Objects…): Asset Browser limpio. Se puede reactivar en las preferencias del Asset Browser.
- **ProjectTool**: nueva herramienta de carga/guardado/importación/exportación que hace chequeos de upgrade/downgrade al abrir. Permite abrir proyectos muy antiguos (pre-2020, 2.2.5 con mucho DnD) y proyectos creados en IDEs más nuevas (ignora lo que no conoce). Se actualiza por Package Manager.
- **Project Health**: avisa de imágenes de sprites perdidas, sonidos sin fichero de audio y shaders sin sus ficheros vertex/fragment.
- **Nuevo serializador de proyecto**: se acabó el "por qué git me marca todo el .yyp". El orden de los campos de los `.yy` ya no cambia; además separa el orden del Asset Browser en un fichero aparte para que git pueda ignorarlo. Efecto secundario: proyectos que cargan más rápido y compilan más rápido.
- Se elimina la lista "Options" del `.yyp` (redundante desde 2022.9 y fuente de conflictos entre licencias distintas).
- **Tile layers**: nuevo formato de almacenado mucho más rápido y ligero. **No compatible con IDEs antiguas** (sube la versión de proyecto a 1.6 y bloquea la apertura en versiones previas).
- **Pestaña Welcome** para nuevos usuarios, mostrada una vez; se reabre desde Help.
- **Notas "Readme"**: una Note en la raíz del Asset Browser que se llame `readme` se abre automáticamente la primera vez que alguien abre el proyecto. Otras notas pueden marcarse con "Open On First Load".
- El **Inspector** permite ver/editar más tipos de asset, incluidos Extensions e Included Files.
- Se elimina **Laptop Mode** (lo sustituye "Redefine Keys" en preferencias) y se elimina la **integración con Marketplace**.
- Mejor soporte **DPI** al mover GameMaker entre monitores con distinta resolución.
- El editor de sonido se ha revisado para reflejar mejor cómo se usan sus propiedades.
- Rooms y Sequences ahora permiten colocar y editar **texto** (en Rooms, dentro de Asset Layers).
- Sistema de **"Emergency Restart"**: si se detecta un error de driver GPU (y solo eso), la IDE intenta guardar el proyecto antes de reiniciarse.
- Aviso en arranque si **YYAL** no carga (antes crasheaba); sin YYAL no hay previsualización de audio.

---

## 4. Novedades del runtime (GMS2)

### 4.1 GML

Cambio crítico: **los Handles sustituyen a los IDs numéricos**. Consecuencias:

- Assets, data structures, surfaces, buffers, instancias, time sources, layers, tilemaps, flexpanels… guardan **tipo + índice** en un entero de 64 bits.
- Las funciones **validan el tipo** del argumento: ya no puedes pasar por descuido una DS List a una función de DS Grid.
- **Ya no se puede incrementar el ID de un asset** para "encontrar el siguiente".
- `json_stringify()` / `json_parse()` serializan y parsean handles correctamente.

Detalle completo en `02 - Cambios en GML 2026.md`.

Otras novedades de lenguaje:

- **Template strings**: `$"Hola {variable}"`, equivalentes a `string()` y `string_ext()`.
- Nuevas funciones de **structs** y **arrays**.
- Nuevas funciones de **strings**.

### 4.2 Colisiones

- Todas las funciones de colisión que toman un objeto/instancia **aceptan también Tile Maps y arrays** mezclando tipos: `place_meeting(x, y, [obj_rock, tilemap])`.
- Las cajas de colisión (**bounding boxes**) se usan sin redondear y son **inclusivas**: una máscara de 16×16 va de (0.0, 0.0) a (16.0, 16.0). Antes se redondeaban a enteros y eran exclusivas (0,0)–(15,15).
- Se puede volver al comportamiento antiguo con **Collision Compatibility Mode** en Game Options.

### 4.3 Descarte automático de assets y "Deprecated Behaviours"

- El compilador **descarta automáticamente los assets no referenciados** directamente. Se desactiva en General Game Options.
- Para conservar assets que cargas dinámicamente: `gml_pragma("MarkTagAsUsed", "mi_tag")`.
- Nueva sección **Deprecated Behaviours** en General Game Options para reactivar comportamientos antiguos: `instance_change`/`position_change`, el cambio de colisiones, los cambios de JSON, conversión string→number, tratamiento de `other`, errores estrictos de audio.

### 4.4 Otros cambios de runtime

- **Vsync** activado por defecto en todos los targets.
- **"Interpolate colours between pixels"** activado por defecto en Windows (antes no coincidía con el manual ni con el resto de targets).
- Export de Windows con opciones **ARM64** (Run/Run debug detecta arquitectura solo; Create Exe permite elegir Zip ARM64 o NSIS ARM64).
- El nombre de producto/display ya no es "Created in GameMaker" por defecto: usa el nombre del proyecto.
- `part_system_depth()` ya no hace nada si le pasas la profundidad actual (fix en Beta 2026.100).
- `room_restart()` vuelve a funcionar (fix en Beta 2026.100).

### 4.5 Spine

- El Sprite Editor deja elegir entre **mallas de colisión de Spine** o **máscaras de colisión de GameMaker** por sprite.
- Soporte para **"Mixed-Skin"** de Spine.
- Ajuste automático del blend mode para sprites Spine con alfa premultiplicado (desactivable con `draw_enable_skeleton_blend_override()`).
- Nuevas funciones de **attachments** de Spine.

---

## 5. Grandes features nuevas (resumen)

| Feature | Qué es | Dónde se documenta |
|---|---|---|
| **UI Layers + Flexpanels** | Capas de UI globales basadas en flexbox para HUDs y menús responsivos | `04 - UI Layers y Flexpanels.md` |
| **Particle Editor + asset Particle System** | Editor visual de partículas + nuevo tipo de asset | `05 - Sistema de partículas nuevo.md` |
| **Package Manager + Prefabs** | IDE modular; librería de bloques de contenido versionados | `08 - Package Manager y Prefabs.md` |
| **Code Editor 2** | Editor nuevo con eventos unificados y ventanas divididas | `09 - Code Editor 2 y Feather.md` |
| **Feather activado por defecto** | Análisis de tipos y nombre de assets en el editor legacy | `09 - Code Editor 2 y Feather.md` |
| **SVG, SDF, FX nuevos, formatos de superficie** | Gráficos | `06 - Gráficos - SVG, SDF, FX y superficies.md` |
| **Buses y efectos de audio** | Audio | `07 - Audio - buses y efectos.md` |
| **Debug Overlay nuevo** | `show_debug_overlay()` + vistas personalizadas con `dbg_*()` | Manual: The Debug Overlay |
| **GMRT** | Runtime nuevo (codename Cronus) | `03 - GMRT - El nuevo runtime.md` |

---

## 6. Plataformas

- **Nintendo Switch 2**: nuevo target. Setup muy similar a Switch 1.
- **Reddit**: nuevo target basado en **Devvit**. Funciona distinto a todos los demás: hay que montar el proyecto de Reddit y ejecutar las herramientas Devvit **fuera de GameMaker**. Ver la guía antes de tocar nada.
- **GX.games**: ahora soporta exportar **Game Strips** (banners jugables para Opera GX) y **Live Wallpapers** (fondos interactivos de escritorio con app compañera), además de exportar el build WASM como ZIP.
- Las guías de setup y los SDKs requeridos de todas las plataformas están ahora en el **GameMaker Wiki** (`Help > Required SDKs` desde la IDE).

---

## 7. Extensiones

- **Extension Options**: el desarrollador de una extensión declara campos en una ventana "Options" del Extension Editor, y quien la usa los rellena como si fueran Instance Variables. Se guardan **por configuración**.
- Se puede excluir funciones del autocompletado y marcar ajustes como ocultos.
- Acceso a los valores de las opciones desde extensiones nativas de Android e iOS.
- Inyección de código ahora se guarda **por configuración**; en Android se puede inyectar en `gradle.properties` y en macOS (Beta 2026.100 R5) ya es posible inyectar código en builds de macOS (útil para activar Hardened Runtime).

---

## 8. Qué hay en la Beta 2026.100 (julio–agosto 2026)

La Beta es la antesala de **2026.1**. Lo más relevante hasta Release 5 (27/08/2026):

### Features

- **Prefab Builder** ya disponible (R5): por fin puedes crear tus propios Prefabs. Es una primera versión, con problemas de UI conocidos.
- **Workspaces con pestañas scrollables** (R3): desplegable para saltar entre workspaces, menú contextual para cerrar selecciones y scroll horizontal cuando se llenan.
- **Validación y reparación de paquetes** en el Package Manager (R2): puede reinstalar paquetes corruptos.
- **Soporte de split windows** en Code Editor 2 / Workspaces: la infraestructura ya está en R2, la función se activará después.
- **Eliminado GmlSpec Rollback** (R2): la funcionalidad de rollback multiplayer desaparece. Si tu juego lo usa, **quédate en 2026.0** hasta tener alternativa.
- `layer_sequence_get_alpha()` y `layer_sequence_get_blend()`: getters para los setters de color de Sequence añadidos en 2026.0 (R2).
- Switch 1+2: opción para **desactivar el touchscreen** en Game Options (R4).
- Compilar con verbose y errores de paquetes: el Package Manager muestra el log de salida cuando hay errores estando en la Start Page (R5).
- Prefab Library: puede eliminar enlaces a colecciones que ya no existen (R5), y al cargar un proyecto ofrece elegir entre quitar el enlace o subir a la última versión disponible (R1).

### Fixes relevantes

- `texturegroup_add()` corregido: ya afecta a referencias de asset y dinámicas, y hace fallback correcto cuando la textura se descarga (R4).
- `collision_rectangle_*()` con tiles usa las mismas reglas que con instancias (R3) — **puede obligarte a refactorizar**.
- `part_system_angle()` ya funciona en sistemas no globales (R2).
- `json_stringify()` ya no convierte funciones en basura (`"function":{"toString":...}`) (R1).
- `ref_create()` ya no petlea silenciosamente si le pasas una ref inexistente (R1).
- Numerosos fixes de estabilidad en Code Editor 2, Workspaces, Mac IDE y Ubuntu IDE.

---

## 9. Checklist de migración de un proyecto a 2026.0

1. **Backup + git.** Sin excepción.
2. Instala LTS 2026.0 como instalación separada y **reaplica permisos de antivirus/firewall** para la carpeta nueva.
3. Lee la guía de SDKs requeridos para 2026.0 y la guía de permisos.
4. Abre el proyecto; deja que **ProjectTool** haga la conversión. Si falla, **actualiza ProjectTool desde el Package Manager** antes de reportar nada.
5. Compila y revisa errores relacionados con **Handles** (aritmética sobre IDs, IDs pasados como números).
6. Comprueba colisiones: si algo se comporta raro, prueba **Collision Compatibility Mode** antes de reescribir media física.
7. Comprueba que no cargas assets dinámicos que el **descarte automático** se haya llevado por delante; si es así, usa tags + `gml_pragma("MarkTagAsUsed", ...)`.
8. Revisa `json_parse()`/`json_stringify()` si guardabas IDs numéricos de assets en saves.
9. Si usas notas de proyecto, aprovecha el `readme` automático para documentar.
10. No migres a GMRT todavía si el proyecto es serio: lee `03 - GMRT - El nuevo runtime.md` primero.

---

## Fuentes

- Blog oficial LTS 2026.0 — https://gamemaker.io/en/blog/lts-2026-release
- Release notes completos 2026.0.0 — https://releases.gamemaker.io/release-notes/2026/0
- Release notes Beta 2026.100 — https://releases.gamemaker.io/release-notes/2026/100
- Índice de versiones — https://releases.gamemaker.io/
- Roadmap / update primavera 2026 — https://gamemaker.io/en/blog/update-spring-2026
- Wiki de SDKs requeridos para 2026.0 — https://github.com/YoYoGames/GameMaker-Bugs/wiki/2026.0
- Guía de permisos — https://github.com/YoYoGames/GameMaker-Bugs/wiki/Permissions-Guide
