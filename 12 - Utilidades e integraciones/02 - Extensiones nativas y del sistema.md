# 02 · Extensiones nativas y del sistema

> Todo lo que GameMaker **no puede hacer solo** porque necesita hablar con el sistema
> operativo: ventana, ratón, ficheros fuera del *sandbox*, cámara, MIDI, portapapeles, VR.
>
> Verificado el 1 de septiembre de 2026. 💸 marca las de pago.

---

## Antes de nada: ¿lo hace ya el motor?

En 2026 hay funciones nativas para muchas cosas que antes exigían una DLL. Compruébalo:

```sh
python3 "_indice/buscar.py" --listar window_
python3 "_indice/buscar.py" --listar clipboard_
python3 "_indice/buscar.py" --listar os_
python3 "_indice/buscar.py" --listar display_
```

Solo si no aparece lo que necesitas, busca extensión.

---

## 1. YellowAfterlife — el catálogo de referencia

Es el autor de extensiones nativas más prolífico del ecosistema. Casi todas son de Windows,
muchas gratis y las de pago son baratas. Página: <https://yellowafterlife.itch.io/>

### Gratis

| Extensión | Qué hace |
|---|---|
| [**Window Commands**](https://yellowafterlife.itch.io/gamemaker-window-commands) | Interceptar, desactivar y lanzar comandos de ventana (minimizar, cerrar, mover) |
| [**window_taskbar**](https://yellowafterlife.itch.io/gamemaker-window-taskbar) | Parpadeo del icono, notificaciones y **barra de progreso** en la barra de tareas |
| [**Screenshot save dialog**](https://yellowafterlife.itch.io/screenshot-save-dialog) | Diálogo nativo para que el jugador elija dónde guardar la captura |
| [**zlib functions**](https://yellowafterlife.itch.io/gamemaker-zlib) | Compresión y descompresión estándar |
| [**Debug log server**](https://yellowafterlife.itch.io/gamemaker-netlog) | Ventana externa donde volcar el log del juego |
| [**HTML5 loading screen**](https://yellowafterlife.itch.io/gamemaker-loadbar) | Pantalla de carga configurable para exportaciones web |
| [**JS click event handler**](https://yellowafterlife.itch.io/gamemaker-js-click-events) | Abrir pestañas y hacer acciones que el navegador exige que nazcan de un clic real |
| [**file_dragger**](https://github.com/YAL-GameMaker/file_dragger) | Arrastrar ficheros **fuera** de la ventana del juego (MIT, en GitHub) |
| [**window_mouse_queue**](https://github.com/YAL-GameMaker/window_mouse_queue) | Datos de movimiento del ratón de **alta precisión** en Windows (MIT) |
| [**gameframe**](https://github.com/YAL-GameMaker/gameframe) | Marco de ventana personalizado |
| [**GMSDLL**](https://github.com/YAL-GameMaker/GMSDLL) · [**GMSDLL.rs**](https://github.com/YAL-GameMaker/GMSDLL.rs) | **Plantillas para escribir tus propias extensiones** en C++ y en Rust |

📁 Las de GitHub están descargadas en `11 - Código descargado/librerias/extensiones-nativas/`.

### De pago 💸

| Extensión | Precio | Qué hace |
|---|---:|---|
| [**GMLive.gml**](https://yellowafterlife.itch.io/gamemaker-live) | $29,95 | **Recarga de código y assets sin recompilar.** La de mayor impacto de todas |
| [**Apollo**](https://yellowafterlife.itch.io/gamemaker-lua) | $14,95 | Ejecutar **Lua** en Windows, macOS y Linux |
| [**Native cursors**](https://yellowafterlife.itch.io/gamemaker-native-cursors) | $6,95 | Cursores personalizados con la latencia mínima del sistema |
| [**Non-sandboxed filesystem**](https://yellowafterlife.itch.io/gamemaker-nsfs) | $3,95 | Trabajar con ficheros fuera de la carpeta del juego |
| [**TJSON**](https://yellowafterlife.itch.io/gamemaker-tjson) | $3,95 | Funciones JSON más seguras y con mejor manejo de tipos |
| [**Native mouselock**](https://yellowafterlife.itch.io/gamemaker-native-mouselock) | $2,95 | Confinar el cursor a un rectángulo a nivel de sistema |
| [**screen_refresh**](https://yellowafterlife.itch.io/screen-refresh) | $2,95 | Devuelve el dibujado síncrono |

---

## 2. Giavapps — extensiones de Windows y multimedia 💸

Catálogo comercial centrado en Windows: <https://giavapps.itch.io/>

| Extensión | Precio | Qué hace |
|---|---:|---|
| Giavapps MIDI 2 | $49,99 | Entrada y salida **MIDI** |
| Giavapps Windows API | $29,99 | Acceso amplio a la API de Windows |
| Giavapps ProAudio | $29,99 | Audio profesional |
| Giavapps 3D | $14,99 | Utilidades 3D |
| Giavapps Game Jolt API · Lens Flare · Controller · CC | $9,99 c/u | Servicios y efectos |
| Giavapps File | gratis | Operaciones de ficheros |

---

## 3. Ficheros, sistema y hardware

| Extensión | Autor | Precio | Qué hace |
|---|---|---|---|
| [**ZFile**](https://zekronz.itch.io/zfile) | Zekronz | $1,99 | Sistema de ficheros sin *sandbox* |
| [**Folder Browser Dialog**](https://zekronz.itch.io/folder-browser-dialog) | Zekronz | $1,99 | Diálogo nativo para elegir carpeta |
| [**gm-sysinfo**](https://github.com/SpikeHD/gm-sysinfo) | SpikeHD | gratis (MIT) | Información del sistema, multiplataforma |
| [**GMRuntimeLock**](https://chamaeleon.itch.io/gmruntimelock) | chamaeleon | gratis | Impide abrir dos instancias del juego |
| [**FileDropper**](https://hippyman.itch.io/hm-gms-filedropper) | hippyman | gratis | Arrastrar ficheros **dentro** de la ventana |
| [**show_message_native**](https://girkovarpa.itch.io/show-message-native) | Girkov Arpa | gratis | Diálogos nativos de Win32 |
| [**MouseTrap**](https://girkovarpa.itch.io/mousetrap) | Girkov Arpa | gratis | Bloquear el cursor en la ventana |
| [**AnimIcon**](https://girkovarpa.itch.io/animicon-extension) | Girkov Arpa | gratis | Animar el icono de la ventana |
| [**Window Border Colour**](https://aj-studio-com.itch.io/window-border-colour-for-gamemaker) | Alex | $1 | Color del borde de la ventana |

📁 `gm-sysinfo` descargado en `11 - Código descargado/librerias/extensiones-nativas/gm-sysinfo/`.

---

## 4. Cámara, sensores y móvil

| Extensión | Plataforma | Precio | Qué hace |
|---|---|---|---|
| [**GMESCAPI**](https://nkrapivindev.itch.io/gmescapi) | Windows | gratis | Webcam |
| [**JavaCam-GMS2**](https://mikames.itch.io/javacam-gms2) | Android | $10 | Cámara y lectura de **QR** |
| [**GPS Location iOS & Android**](https://xyzlab.itch.io/gps-location-ios-android) | Móvil | $10 | Geolocalización |
| [**GMEXT-MobileUtils**](https://github.com/YoYoGames/GMEXT-MobileUtils) | Móvil | oficial | Utilidades varias de móvil |
| [**The Ultimate Toast Extension**](https://harpwood.itch.io/the-ultimate-toast-extension-for-android) | Android | gratis | Notificaciones *toast* |
| [**GameMaker Studio Virtual Keyboard**](https://poblano.itch.io/gamemaker-studio-virtual-keyboard) | Móvil | $5 | Teclado virtual |
| [**GMCardboard**](https://maddestudios.itch.io/mmk-gmcardboard) | Android | $50 | **VR** con Google Cardboard |
| [**GMEXT-Bluetooth**](https://github.com/YoYoGames/GMEXT-Bluetooth) | Móvil | oficial | Bluetooth |

📁 Las oficiales `GMEXT-*` están descargadas en `11 - Código descargado/extensiones_oficiales/`.

---

## 5. Web y WebAssembly

| Extensión | Qué hace |
|---|---|
| [**wasm-bridge**](https://github.com/Sidorakh/wasm-bridge) | Incluir extensiones de **JavaScript** en juegos de GX/WASM (MIT) |
| [**GX Types**](https://www.gamemakerkitchen.com/libraries) | Clases de TypeScript para la API de GML expuesta en el runner WASM |
| [**GMNest**](https://github.com/TimVN/GMNest) | Extensión de **Socket.IO** para HTML5 |

📁 `wasm-bridge` en `11 - Código descargado/librerias/extensiones-nativas/wasm-bridge/`.

---

## 6. Escribir tu propia extensión

Si nada de lo anterior te sirve, GameMaker permite escribir extensiones nativas:

| Recurso | Qué es |
|---|---|
| [**GM-ExtensionGenerator**](https://github.com/YoYoGames/GM-ExtensionGenerator) (oficial, Apache-2.0) | Genera el esqueleto de una extensión |
| [**GameMakerStudio_ExtensionExample**](https://github.com/YoYoGames/GameMakerStudio_ExtensionExample) (oficial) | Ejemplo mínimo |
| [**GMSDLL**](https://github.com/YAL-GameMaker/GMSDLL) | Plantilla en **C++** |
| [**GMSDLL.rs**](https://github.com/YAL-GameMaker/GMSDLL.rs) | Plantilla en **Rust** |
| [**GM-OpenAPIGenerator**](https://github.com/YoYoGames/GM-OpenAPIGenerator) (oficial) | Genera cliente GML desde una especificación OpenAPI |

📁 Las cuatro primeras descargadas; las oficiales en `plantillas_y_ejemplos/`, las de YAL en
`librerias/extensiones-nativas/`.

🆕 **Novedad de la Beta 2026.100 (27-08-2026):** el **Editor de Extensiones permite inyectar
código durante las compilaciones de macOS** (`#15809`). Sirve, por ejemplo, para activar
*Hardened Runtime* automáticamente. Ver
[`02 - Novedades 2026`](../02%20-%20Novedades%202026/_INDICE-NOVEDADES.md).

---

## Fuentes

- itch.io · extensiones GameMaker: <https://itch.io/game-assets/tag-extension/tag-gamemaker>
- YellowAfterlife: <https://yellowafterlife.itch.io/>
- Giavapps: <https://giavapps.itch.io/>
- awesome-gamemaker · Native Extensions: <https://github.com/bytecauldron/awesome-gamemaker>
- Notas de la versión 2026.100.0: <https://releases.gamemaker.io/release-notes/2026/100>
