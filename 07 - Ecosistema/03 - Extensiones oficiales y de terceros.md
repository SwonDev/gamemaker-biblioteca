# 03 · Extensiones oficiales y de terceros

> Verificado el **31 de agosto de 2026** contra la API de GitHub.
> **44 extensiones oficiales `GMEXT-*`** en la organización YoYoGames + Extension Generator + catálogo de terceros.
> Las plataformas indicadas son las que declara el README de cada repositorio.

---

## 1. Cómo funciona una extensión en GameMaker en 2026

Una extensión («*extension*») es un paquete que añade funciones a GML. Hay tres sabores:

| Tipo | Cómo se instala | Dónde vive |
|---|---|---|
| **GML puro** | Importar un `.yymps` | En tu proyecto, como scripts normales |
| **Nativa** (C++, Java, ObjC…) | Importar el `.yymps` + configurar el SDK de la plataforma | Binarios por plataforma + *glue* GML |
| **Generada con `extgen`** | Ver sección 2 | Definida por un fichero **GMIDL** |

El formato de distribución es el **`.yymps`** («local package»), que se importa con *Tools > Import Local Package*.

> ⚠️ **Regla de oro sobre licencias:** la mayoría de las `GMEXT-*` figuran como **`NOASSERTION`** en GitHub. Eso **no significa que sean libres**: significa que GitHub no reconoce un fichero de licencia estándar. Lee el `LICENSE` dentro del repo antes de usarlas. Las que sí son abiertas (Apache-2.0, MIT) están marcadas explícitamente en las tablas siguientes.

---

## 2. Extension Generator (`extgen`) — la novedad de 2026

- **Enlace:** <https://github.com/YoYoGames/GM-ExtensionGenerator>
- **Licencia:** **Apache-2.0** · 26 ★ · push 2026-08-27 · creado en enero de 2026.
- **Binarios:** <https://github.com/YoYoGames/GM-ExtensionGenerator/releases/tag/nightly>
- **Requisitos:** **.NET 9 SDK** · Windows, macOS o Linux.
- **Estado declarado por YoYoGames:** *«Actively developed · Production-ready core · Open to contributions»*.
- **Documentación:** en la Wiki del repositorio.

### Qué hace exactamente

`extgen` es un **generador de código dirigido por esquema**. Partes de **un único fichero GMIDL** (*GameMaker Interface Definition Language*) y genera:

- Bindings **GML**.
- *Glue* **C++ nativo**.
- **Android**: Java / Kotlin / JNI.
- **iOS y tvOS**: Objective-C / Swift.
- **Consolas**: Xbox, PS4, PS5, Switch.
- Proyectos y *presets* **CMake** completos.
- Documentación opcional.

Todo el comportamiento se controla desde un **`config.json`** validado por un JSON Schema generado automáticamente.

```sh
# Crear el esqueleto de una extensión nueva
extgen --init ./mi-extension

# Generar absolutamente todo
extgen --config ./mi-extension/config.json
```

### Por qué importa

La documentación de GMRT lo dice literalmente: uno de los objetivos del nuevo runtime es

> *«Provide tools to easily convert a native library into an extension using a single IDL declaration file»*

Es decir: **`extgen` es la vía oficial para envolver cualquier librería nativa** (tuya o de terceros) y usarla desde GML. Antes de 2026 esto se hacía a mano y era uno de los puntos más dolorosos del desarrollo en GameMaker.

> **Regla práctica:** si necesitas integrar una librería nativa en 2026, **no copies el `GameMakerStudio_ExtensionExample`** (obsoleto, 2023). Usa `extgen`.

---

## 3. Catálogo completo de extensiones oficiales (`GMEXT-*`)

> 📋 **Nota metodológica sobre la columna «Plataformas»:** se ha rellenado con lo que declara literalmente el README de cada repositorio, consultado uno a uno. **Ocho extensiones no declaran sus plataformas de forma explícita** en el README; en esos casos la plataforma se ha inferido del nombre y del SDK que envuelven, y se marca a continuación: **GMEXT-GooglePlayBilling** (Android), **GMEXT-GooglePlayServices** (Android), **GMEXT-InAppUpdate** (Android), **GMEXT-GooglePlayLicensing** (Android), **GMEXT-GooglePlayInstant** (Android), **GMEXT-HuaweiPaidApps** (Android), **GMEXT-GameJolt** (todas vía REST, como el resto de integraciones REST). Confirma la plataforma en la documentación del marketplace antes de comprometerte con una de ellas.

### 3.1 Escritorio, PC y multiplataforma

| Extensión | Qué hace | Plataformas | Licencia | Push | ★ |
|---|---|---|---|---:|---:|
| [GMEXT-Steamworks](https://github.com/YoYoGames/GMEXT-Steamworks) | Logros, leaderboards, estadísticas, Workshop, autenticación de **Steam** | Windows, macOS, Linux | NOASSERTION | 2026-08-25 | 123 |
| [GMEXT-GDK](https://github.com/YoYoGames/GMEXT-GDK) | **GDK** → Microsoft Store y **Xbox Live** | Windows / Xbox | NOASSERTION | 2026-08-14 | 20 |
| [GMEXT-EpicOnlineServices](https://github.com/YoYoGames/GMEXT-EpicOnlineServices) | **Epic Online Services**: sesiones, matchmaking, logros | Windows, macOS | NOASSERTION | 2026-08-25 | 16 |
| [GMEXT-GOG](https://github.com/YoYoGames/GMEXT-GOG) | **GOG Galaxy** | Windows, macOS | NOASSERTION | 2026-04-24 | 10 |
| [GMEXT-Discord](https://github.com/YoYoGames/GMEXT-Discord) | **Discord** (Social SDK / Rich Presence) | Windows, macOS, Linux, iOS, Android | NOASSERTION | 2026-08-25 | 13 |
| [GMEXT-Photon](https://github.com/YoYoGames/GMEXT-Photon) | **Photon**: multijugador en tiempo real, chat y voz (envuelve el SDK C++ de Photon: Realtime/LoadBalancing, Chat, Voice). **Nueva en 2026** | Windows, macOS, Linux, Android, iOS | NOASSERTION | 2026-08-25 | 8 |
| [GMEXT-FMOD](https://github.com/YoYoGames/GMEXT-FMOD) | Motor de audio **FMOD** | Escritorio, móvil, **consolas** | **Apache-2.0** | 2026-08-12 | 74 |
| [GMEXT-WebView](https://github.com/YoYoGames/GMEXT-WebView) | Visor **web** incrustado | Android, iOS, Windows, macOS, Linux | NOASSERTION | 2026-08-04 | 7 |
| [GMEXT-Bluetooth](https://github.com/YoYoGames/GMEXT-Bluetooth) | **Bluetooth** (winrt en Windows 10+) | Windows, macOS, iOS, Android | **Apache-2.0** | 2025-06-20 | 8 |
| [GMEXT-mod.io](https://github.com/YoYoGames/GMEXT-mod.io) | **Modding** alojado (REST) | Todas vía REST | NOASSERTION | 2026-04-24 | 12 |
| [GMEXT-Twitch](https://github.com/YoYoGames/GMEXT-Twitch) | Integración con **Twitch** (REST) | Todas vía REST | **Apache-2.0** | 2025-12-29 | 21 |
| [GMEXT-GameJolt](https://github.com/YoYoGames/GMEXT-GameJolt) | API de **GameJolt** | Todas vía REST | **Apache-2.0** | 2025-11-20 | 7 |
| [GMEXT-Interhaptics-Main](https://github.com/YoYoGames/GMEXT-Interhaptics-Main) | **Háptica** (Interhaptics) | Windows (más plataformas «más adelante») | **Apache-2.0** | 2026-04-24 | 5 |
| [GMEXT-Medal](https://github.com/YoYoGames/GMEXT-Medal) | Envía eventos a la app **Medal** para guardar clips. **GML puro**, sin librerías nativas. **Nueva en 2026** | Todas | NOASSERTION | 2026-08-26 | 0 |
| [GMEXT-Elements](https://github.com/YoYoGames/GMEXT-Elements) | Extensión **Elements**. **Nueva en 2026** | Todas | NOASSERTION | 2026-08-26 | 7 |

### 3.2 Monetización y publicidad

| Extensión | Qué hace | Plataformas | Licencia | Push | ★ |
|---|---|---|---|---:|---:|
| [GMEXT-AdMob](https://github.com/YoYoGames/GMEXT-AdMob) | **Google AdMob** (`play-services-ads` 25.4.0 + `user-messaging-platform` 4.x) | Android, iOS | NOASSERTION | 2026-08-25 | 14 |
| [GMEXT-LevelPlay](https://github.com/YoYoGames/GMEXT-LevelPlay) | **LevelPlay**: mediación de anuncios. **Nueva en 2026** | Android, iOS | NOASSERTION | 2026-08-26 | 0 |
| [GMEXT-IronSource](https://github.com/YoYoGames/GMEXT-IronSource) | ironSource clásico — ⚠️ **LevelPlay es la sucesora**; requiere CocoaPods en iOS | Android, iOS | NOASSERTION | 2025-06-13 | 2 |
| [GMEXT-OperaAds](https://github.com/YoYoGames/GMEXT-OperaAds) | **Opera Ads**. **Nueva en 2026** | Android, iOS | NOASSERTION | 2026-08-25 | 0 |
| [GMEXT-H5GamesAds](https://github.com/YoYoGames/GMEXT-H5GamesAds) | Anuncios para **HTML5** | HTML5 | NOASSERTION | 2025-06-20 | 2 |
| [GMEXT-CrazyGames](https://github.com/YoYoGames/GMEXT-CrazyGames) | Publicar en **CrazyGames** | HTML5 | NOASSERTION | 2026-04-24 | 2 |
| [GMEXT-Adjust](https://github.com/YoYoGames/GMEXT-Adjust) | Atribución y analítica **Adjust** | iOS, Android | **Apache-2.0** | 2025-08-26 | 1 |

### 3.3 Compras integradas (IAP) y licencias

| Extensión | Qué hace | Plataformas | Licencia | Push | ★ |
|---|---|---|---|---:|---:|
| [GMEXT-AppleIAP](https://github.com/YoYoGames/GMEXT-AppleIAP) | **IAP de Apple** | macOS, iOS/tvOS | **Apache-2.0** | 2026-08-25 | 5 |
| [GMEXT-GooglePlayBilling](https://github.com/YoYoGames/GMEXT-GooglePlayBilling) | **Google Play Billing** | Android | NOASSERTION | 2026-08-28 | 12 |
| [GMEXT-GooglePlayLicensing](https://github.com/YoYoGames/GMEXT-GooglePlayLicensing) | Verificación de licencia **LVL** | Android | NOASSERTION | 2026-05-04 | 5 |
| [GMEXT-GooglePlayPassLicensing](https://github.com/YoYoGames/GMEXT-GooglePlayPassLicensing) | Licencia de **Google Play Pass** | Android | NOASSERTION | 2026-04-24 | 4 |
| [GMEXT-HuaweiPaidApps](https://github.com/YoYoGames/GMEXT-HuaweiPaidApps) | **Huawei AppGallery** | Android | **Apache-2.0** | 2026-06-19 | 1 |

### 3.4 Backend, analítica y redes sociales

| Extensión | Qué hace | Plataformas | Licencia | Push | ★ |
|---|---|---|---|---:|---:|
| [GMEXT-Firebase](https://github.com/YoYoGames/GMEXT-Firebase) | **Firebase**: Analytics, Auth, Firestore, Remote Config, Crashlytics. SDK nativo en Android/iOS/Web; REST en el resto | Android, iOS, Web (+REST) | NOASSERTION | 2026-08-27 | 20 |
| [GMEXT-Facebook](https://github.com/YoYoGames/GMEXT-Facebook) | SDK de **Facebook** | Android, iOS, HTML5 | **Apache-2.0** | 2026-08-27 | 0 |
| [GMEXT-Reddit](https://github.com/YoYoGames/GMEXT-Reddit) | **Reddit / Devvit**. Requiere **node.js** instalado | WASM (GX.games) | **Apache-2.0** | 2026-08-14 | 0 |
| [GMEXT-GX.games](https://github.com/YoYoGames/GMEXT-GX.games) | Funciones de la plataforma **GX.games** | GX.games | NOASSERTION | 2025-06-20 | 8 |

### 3.5 Móvil (Android / iOS)

| Extensión | Qué hace | Plataformas | Licencia | Push | ★ |
|---|---|---|---|---:|---:|
| [GMEXT-MobileUtils](https://github.com/YoYoGames/GMEXT-MobileUtils) | Utilidades móviles (permisos, estado del dispositivo…) | Android, iOS | NOASSERTION | 2026-08-25 | 13 |
| [GMEXT-GooglePlayServices](https://github.com/YoYoGames/GMEXT-GooglePlayServices) | **Google Play Services** | Android | NOASSERTION | 2026-08-25 | 10 |
| [GMEXT-GameCenter](https://github.com/YoYoGames/GMEXT-GameCenter) | **Game Center** de Apple | iOS, macOS | NOASSERTION | 2026-08-25 | 7 |
| [GMEXT-GoogleSignIn](https://github.com/YoYoGames/GMEXT-GoogleSignIn) | Inicio de sesión con **Google** | Android, iOS/tvOS, HTML5 | NOASSERTION | 2026-06-30 | 3 |
| [GMEXT-AppleSignIn](https://github.com/YoYoGames/GMEXT-AppleSignIn) | Inicio de sesión con **Apple** | macOS, iOS/tvOS | NOASSERTION | 2026-06-30 | 2 |
| [GMEXT-InAppUpdate](https://github.com/YoYoGames/GMEXT-InAppUpdate) | **Actualizaciones in-app** de Google Play | Android | **Apache-2.0** | 2026-07-31 | 3 |
| [GMEXT-GooglePlayInstant](https://github.com/YoYoGames/GMEXT-GooglePlayInstant) | **Google Play Instant** | Android | **Apache-2.0** | 2025-10-01 | 2 |
| [GMEXT-GooglePlayIntegrity](https://github.com/YoYoGames/GMEXT-GooglePlayIntegrity) | **Play Integrity API** (anti-trampas). **Nueva en 2026** | Android | NOASSERTION | 2026-08-25 | 0 |
| [GMEXT-PlayAgeSignals](https://github.com/YoYoGames/GMEXT-PlayAgeSignals) | Señales de **edad** de Google Play. **Nueva en 2026** | Android | NOASSERTION | 2026-08-25 | 0 |
| [GMEXT-DeclaredAgeRange](https://github.com/YoYoGames/GMEXT-DeclaredAgeRange) | Rango de edad declarado (normativa de **iOS**). **Nueva en 2026** | iOS | NOASSERTION | 2026-08-25 | 0 |
| [GMEXT-MLKit](https://github.com/YoYoGames/GMEXT-MLKit) | **ML Kit**: traducción e identificación de idioma en el dispositivo. En el resto de plataformas las funciones son **no-op** | Android, iOS | **Apache-2.0** | 2026-08-25 | 2 |
| [GMEXT-MobileReview](https://github.com/YoYoGames/GMEXT-MobileReview) | Pedir valoración con el flujo **nativo** del sistema | Android, iOS | NOASSERTION | 2026-08-25 | 7 |
| [GMEXT-AppTrackingTransparency](https://github.com/YoYoGames/GMEXT-AppTrackingTransparency) | **ATT** de Apple. **Requisito para que AdMob funcione bien** en iOS | iOS | NOASSERTION | 2026-06-18 | 3 |

### 3.6 Consolas

> ⚠️ **No hay repos públicos de consola.** PlayStation, Nintendo Switch y Xbox (más allá de GDK) se distribuyen bajo **NDA** a través de los programas de desarrolladores de cada fabricante. Si encuentras un repo «oficial» de consola en abierto, es una filtración: no lo uses.

### 3.7 Generación de código (relacionada)

| Repo | Qué hace | Licencia | Push | ★ |
|---|---|---|---:|---:|
| [GM-OpenAPIGenerator](https://github.com/YoYoGames/GM-OpenAPIGenerator) | Genera un cliente GML a partir de una especificación **OpenAPI** (REST) | **Apache-2.0** | 2026-08-26 | 0 |

---

## 4. Extensiones y librerías de terceros (verificadas)

### 4.1 Activas en 2026

| Nombre | Enlace | Qué hace | Licencia | Push | ★ |
|---|---|---|---|---:|---:|
| **BBMOD** | [blueburncz/BBMOD](https://github.com/blueburncz/BBMOD) | Motor **3D** completo: modelos, materiales, animaciones, partículas, sombras. Docs en <https://blueburn.cz/bbmod/docs/3> | MIT | 2026-08-04 | 119 |
| **BBMOD-Blender** | [blueburncz/BBMOD-Blender](https://github.com/blueburncz/BBMOD-Blender) | Addon de **Blender** para exportar assets a BBMOD. Imprescindible si usas BBMOD | — | — | — |
| **Crochet** | [FaultyFunctions/Crochet](https://github.com/FaultyFunctions/Crochet) | **Editor visual de diálogo** para Chatterbox. Windows/macOS/Ubuntu + versión web | MIT | 2026-05-28 | 121 |
| **LineAudio** | [WangleLine/LineAudio](https://github.com/WangleLine/LineAudio) | Motor de audio pequeño (*wrapper*) | MIT | 2026-07-25 | 5 |
| **Unic** | [TabularElf/Unic](https://github.com/TabularElf/Unic) | Implementación del **estándar Unicode** para GameMaker (lo usa lexicon para fechas, números y monedas) | MIT | 2026-03-29 | 8 |
| **GMSentry** | Marketplace ([asset 7917](https://marketplace.yoyogames.com/assets/7917/gmsentry)) | Integración con **Sentry** (reporte de errores). Citado por Juju Adams como alternativa a Snitch | ⚠️ Revisar | — | — |
| **Quack Dialogue System** | Marketplace ([asset 8789](https://marketplace.yoyogames.com/assets/8789/quack-dialogue-system)) | Sistema de diálogo. Citado por Juju Adams | ⚠️ Revisar | — | — |

### 4.2 Inactivas (sin push en más de un año) — úsalas bajo tu responsabilidad

| Nombre | Enlace | Último push | ★ | Licencia |
|---|---|---:|---:|---|
| **Bard Audio** | [gl326/bard-audio](https://github.com/gl326/bard-audio) | 2024-09-16 | 40 | MIT |
| **gmdialogue** | [danielpancake/gmdialogue](https://github.com/danielpancake/gmdialogue) | 2024-06-10 | 18 | ⚠️ **sin licencia** |
| **PXLUI** | [1pxlchibs/PXLUI](https://github.com/1pxlchibs/PXLUI) | 2024-06-25 | 19 | MIT |
| **SimpleUI** | [evolutionleo/SimpleUI](https://github.com/evolutionleo/SimpleUI) | 2024-05-07 | 9 | MIT |
| **Sonus** | [tabularelf/Sonus](https://github.com/tabularelf/Sonus) | 2024-05-26 | 5 | MIT |
| **Emu** | [DragoniteSpam/Emu](https://github.com/DragoniteSpam/Emu) | 2026-02-18 | 43 | ⚠️ **sin licencia** |
| **Input-Dog** | [messhof/Input-Dog](https://github.com/messhof/Input-Dog) | **2016-05-19** | 39 | MIT — ⚠️ **abandonada** |

### 4.3 No son extensiones (y conviene saberlo)

| Nombre | Qué es realmente |
|---|---|
| **YYToolkit** | [AurieFramework/YYToolkit](https://github.com/AurieFramework/YYToolkit) — herramienta de **modding externo** que inyecta código en juegos GameMaker ya compilados. No se importa en tu proyecto. Push 2026-03-03. |
| **GMEdit** | [YellowAfterlife/GMEdit](https://github.com/YellowAfterlife/GMEdit) — **editor de código** independiente, no una extensión. 369 ★, MIT, push 2026-07-22. |

---

## 5. Árbol de decisión: ¿qué extensión necesito?

```
¿Qué quieres hacer?
│
├─ Publicar en una tienda de PC
│  ├─ Steam ........................ GMEXT-Steamworks
│  ├─ Epic ......................... GMEXT-EpicOnlineServices
│  ├─ GOG .......................... GMEXT-GOG
│  ├─ Microsoft Store / Xbox ....... GMEXT-GDK
│  └─ itch.io ...................... No necesitas extensión
│
├─ Multijugador online
│  ├─ Solución gestionada (cloud) .. GMEXT-Photon  (lo más rápido en 2026)
│  ├─ Peer-to-peer con cuentas Epic  GMEXT-EpicOnlineServices
│  └─ Rollback / determinista ...... GGPO no existe para GM; mira Gang Garrison 2 (ejemplo abierto)
│
├─ Monetizar
│  ├─ Anuncios móviles ............. GMEXT-AdMob
│  ├─ Anuncios mediados ............ GMEXT-LevelPlay
│  ├─ Compras en iOS/macOS ......... GMEXT-AppleIAP
│  ├─ Compras en Android ........... GMEXT-GooglePlayBilling
│  └─ Anuncios en HTML5 ............ GMEXT-H5GamesAds
│
├─ Backend
│  ├─ Firebase (auth, datos, config) GMEXT-Firebase
│  └─ Tu propia API REST ........... GM-OpenAPIGenerator
│
├─ Audio avanzado
│  ├─ Motor FMOD completo .......... GMEXT-FMOD
│  └─ Patrones, ducking, BPM ....... Vinyl (librería GML, ver archivo 02)
│
├─ Mods de la comunidad ............ GMEXT-mod.io
│
├─ 3D en serio
│  ├─ Motor completo ............... BBMOD
│  └─ Colisiones 3D ................ Bonk (librería GML)
│
└─ Envolver una librería nativa propia
   └─ .............................. GM-ExtensionGenerator (extgen + GMIDL)
```

---

## 6. Dependencias obligatorias a vigilar

Algunas extensiones tienen requisitos ocultos (verificados en sus README):

| Extensión | Requisito |
|---|---|
| GMRT / GMEXT sobre GMRT | **.NET 8.0** · **EMSDK 5.0.4** para WASM |
| GMEXT-IronSource | **CocoaPods** instalado para iOS |
| GMEXT-Reddit | **node.js** instalado |
| GMEXT-AppTrackingTransparency | Necesario en iOS para que **AdMob** funcione correctamente |
| GM-ExtensionGenerator | **.NET 9 SDK** |
| GMEXT-Interhaptics | Solo Windows por ahora |
| GMEXT-MLKit | En plataformas no móviles las funciones son **no-op** (no hacen nada, pero no crashean) |
