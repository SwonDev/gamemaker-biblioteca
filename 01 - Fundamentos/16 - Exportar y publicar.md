# 16 · Exportar y publicar

> Cómo sacar tu juego de GameMaker y ponerlo delante de alguien. Verificado contra el manual
> LTS 2026 el **2 de septiembre de 2026**.

---

## Lo básico: `Create Executable`

**File → Create Executable** (o el botón de compilar con el target elegido). GameMaker pide
dónde guardar y con qué formato según la plataforma.

Antes, elige la **plataforma de destino** en el selector de la barra superior. Cada una tiene su
propia sección en **Game Options**, y ahí está casi todo lo que importa.

📘 [Opciones del juego](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Game_Options.md)

---

## HTML5 — el más fácil de compartir

Un juego HTML5 se juega en el navegador sin que nadie descargue nada. Es el formato de itch.io
y el más rápido para enseñar algo.

### ⚠️ El error que todo el mundo comete

**Síntoma:** exportas a HTML5 y el juego aparece **pegado a un lado** del navegador en vez de
centrado, o se ve a un tamaño raro.

Circula por tutoriales una solución a base de código: un objeto de control que lee
`browser_width` / `browser_height` en el Create, y en el Step compara con las dimensiones
guardadas para llamar a `camera_set_view_size`, `camera_set_view_pos`, `surface_resize`,
`window_set_size` y `window_center`. Son unas cuarenta líneas.

**No hace falta nada de eso.** GameMaker lo resuelve con dos ajustes:

**Game Options → HTML5 → Graphics**

| Ajuste | Qué hace |
|---|---|
| **Center the game in the browser** | Centra el lienzo en la página. **Viene desactivado por defecto** — de ahí el problema |
| **Scaling** | `Maintain aspect ratio` (por defecto, respeta la proporción) o `Full scale` (estira hasta el tamaño del lienzo definido en la primera room) |

📘 [Opciones HTML5](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Game_Options/HTML5.md)

> 💡 **Marca la casilla antes de escribir código.** Si después de activarla el juego sigue sin
> encajar, el problema no es el centrado sino **el tamaño de tu primera room y tus viewports**:
> esa room define el lienzo. Ver
> [10 · Rooms, capas, cámaras y viewports](./10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md).

### Cuándo sí necesitas código

Solo si quieres que el juego **se reajuste al redimensionar la ventana** en vivo. Para eso sí
sirven `browser_width` y `browser_height`, pero el patrón correcto es más corto:

```gml
/// obj_control · Create
ancho_previo = browser_width;
alto_previo  = browser_height;

/// obj_control · Step
if (browser_width != ancho_previo || browser_height != alto_previo) {
    ancho_previo = browser_width;
    alto_previo  = browser_height;
    surface_resize(application_surface, browser_width, browser_height);
    display_set_gui_size(browser_width, browser_height);
}
```

📘 [`browser_width`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Web_And_HTML5/browser_width.md) ·
[`browser_height`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Web_And_HTML5/browser_height.md)

### Empaquetado

Al exportar HTML5, GameMaker pregunta entre **archivos sueltos** o **un `.zip`**.

- **`.zip`** → es lo que pide **itch.io**. Súbelo tal cual y marca «This file will be played in
  the browser».
- **Archivos sueltos** → para servirlo tú desde tu propio hosting.

### Limitaciones que te van a morder

| Limitación | Detalle |
|---|---|
| **Sin sandbox de archivos real** | El guardado va a `localStorage` del navegador. Se borra al limpiar datos |
| **Audio bloqueado hasta interactuar** | Los navegadores no dejan sonar nada hasta el primer clic o tecla |
| **Sin grupos de texturas dinámicos** | `texturegroup_*` no está disponible en HTML5 |
| **Mezcla en degradado limitada** | Sin WebGL, `draw_text_colour` degrada a un solo color |
| **Sin extensiones nativas** | Nada de DLL ni código C++ |

📘 [Web y HTML5](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Web_And_HTML5/Web_And_HTML5.md)

---

## Escritorio: Windows, macOS y Ubuntu

| Plataforma | Salida | Notas |
|---|---|---|
| **Windows** | `.exe` con instalador (NSIS) o carpeta ZIP | Lo más directo |
| **macOS** | `.app`, `.pkg` o `.zip` | Para distribuir fuera de la Mac App Store hace falta **firma y notarización** de Apple |
| **Ubuntu** | `.AppImage` o `.deb` | |

> 🔺 **En escritorio puedes desactivar el sandbox** (Game Options → *Disable file system
> sandbox*), lo que permite leer y escribir en cualquier ruta permitida por el sistema
> operativo. Consulta [`GM_is_sandboxed`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/OS_And_Compiler/GM_is_sandboxed.md).

---

## Móvil: Android e iOS

Necesitan **SDK externos instalados y configurados** (Android SDK/NDK/JDK; Xcode para iOS) y,
para publicar, cuentas de desarrollador de pago. Es el salto más costoso.

📘 [Preferencias por plataforma](../09%20-%20Manual%20oficial/manual-lts-2026-es/Setting_Up_And_Version_Information/Platform_Preferences.md)

> ⚠️ **Requisito nuevo de las tiendas:** hay una extensión oficial
> `GMEXT-DeclaredAgeRange` para declarar el rango de edad. Está en
> [`11 - Código descargado`](../11%20-%20Código%20descargado/_CATALOGO.md).

---

## Antes de publicar: la lista corta

1. **Icono y splash** por plataforma (Game Options).
2. **Nombre, versión y compañía** — la versión se usa para las actualizaciones.
3. **Compila en modo `Release`, no `Debug`** — el modo debug es más lento y expone información.
4. **Prueba el ejecutable final**, no solo el `F5` desde el IDE: el sandbox y las rutas cambian.
5. **Comprueba el guardado** en la build final. Es donde más falla.
6. **Prueba en una máquina limpia** sin GameMaker instalado.

---

## Publicar en itch.io

El camino más corto para un juego HTML5 o de escritorio. El flujo detallado, incluida la subida
por línea de comandos con `butler`, está en
[07 · Ecosistema — itch.io](../07%20-%20Ecosistema/08%20-%20itch.io%20-%20jams%2C%20assets%20y%20juegos.md).

---

## Compilar desde la línea de comandos

Para CI o para automatizar builds, el CLI oficial:

```sh
gm-cli compile           # compilar
gm-cli package           # empaquetar
gm-cli run               # ejecutar
```

Detalle completo en [13 · GM CLI](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20línea%20de%20comandos.md).

---

**Fuente del caso HTML5:** [*Cómo exportar un juego HTML5 en GameMaker Studio 2026*](https://youtu.be/8RdDApalTvE)
(Tutoriales && Gamedev, abril 2026) — el vídeo **más reciente en español** que se ha encontrado
sobre GameMaker. La corrección de la casilla es aportación de esta biblioteca.
