# 03 · Integraciones con servicios y plataformas

> Steam, Discord, Twitch, GOG, Epic, tiendas móviles, anuncios, analíticas y compras.
> **Casi todo tiene extensión oficial de YoYo Games**, y esa debe ser tu primera opción: se
> mantienen al día con los SDK nativos y están descargadas en
> [`11 - Código descargado/extensiones_oficiales/`](../11%20-%20C%C3%B3digo%20descargado/extensiones_oficiales/).
>
> Estado verificado por API de GitHub el 1 de septiembre de 2026.

---

## 1. Tiendas de PC y consola

| Servicio | Extensión oficial | Último cambio | Alternativa de la comunidad |
|---|---|---|---|
| **Steam** | [GMEXT-Steamworks](https://github.com/YoYoGames/GMEXT-Steamworks) ★123 | 2026-08-25 | [steamworks.gml](https://github.com/YAL-GameMaker/steamworks.gml) ★90 · [Parworks](https://github.com/nkrapivin/Parworks) ★3 |
| **Epic Games** | [GMEXT-EpicOnlineServices](https://github.com/YoYoGames/GMEXT-EpicOnlineServices) ★16 | 2026-08-25 | — |
| **GOG** | [GMEXT-GOG](https://github.com/YoYoGames/GMEXT-GOG) ★10 | 2026-04-24 | [GOG.gml](https://github.com/GameMakerDiscord/GOG.gml) ★11 |
| **Xbox / GDK** | [GMEXT-GDK](https://github.com/YoYoGames/GMEXT-GDK) ★20 | 2026-08-14 | — |
| **GX.games** | [GMEXT-GX.games](https://github.com/YoYoGames/GMEXT-GX.games) ★8 | 2025-06-20 | — |
| **mod.io** | [GMEXT-mod.io](https://github.com/YoYoGames/GMEXT-mod.io) ★12 | 2026-04-24 | — |
| **Game Jolt** | [GMEXT-GameJolt](https://github.com/YoYoGames/GMEXT-GameJolt) ★7 | 2025-11-20 | [Giavapps Game Jolt API](https://giavapps.itch.io/giavapps-game-jolt-api) 💸 |

> **Steam en concreto:** empieza por la extensión oficial. `steamworks.gml` de
> YellowAfterlife añade funciones que la oficial no expone (⚠️ sin cambios desde 2023) y
> `Parworks` la complementa. Para logros multiplataforma,
> [Allchievements](https://github.com/JujuAdams/Allchievements) unifica la API sobre varios
> back-ends.
> 📁 `librerias/integraciones/` contiene `steamworks.gml`, `Parworks`, `GOG.gml` y `Allchievements`.

---

## 2. Comunidad y redes

| Servicio | Opciones |
|---|---|
| **Discord** | Oficial: [GMEXT-Discord](https://github.com/YoYoGames/GMEXT-Discord) ★13 (2026-08-25). 🆕 **Actualizada el 4 de junio de 2026 con el Discord Social SDK.** Comunidad: [DHook](https://github.com/tabularelf/DHook) ★6 (webhooks) · [GMHook](https://github.com/Kruger0/GMHook) ★11 (webhooks) · [GMS2_RPC](https://github.com/Mtax-Development/GMS2_RPC) ★11 (Rich Presence) |
| **Twitch** | Oficial: [GMEXT-Twitch](https://github.com/YoYoGames/GMEXT-Twitch) ★21 (2025-12-29). Comunidad: [GMTwitch](https://github.com/GameMakerDiscord/GMTwitch) ★69 · [MM's Twitch IRC](https://maddestudios.itch.io/mms-twitchtv-irc-interface-for-gamemaker) 💸 $2 (funciona incluso en HTML5) |
| **Reddit (Devvit)** | Oficial: [GMEXT-Reddit](https://github.com/YoYoGames/GMEXT-Reddit) · [GM-RedditDemo](https://github.com/YoYoGames/GM-RedditDemo) · [GameMakerRedditTemplate](https://github.com/YoYoGames/GameMakerRedditTemplate). 🆕 Reddit es un **target nuevo** en 2026 |
| **Facebook** | [GMEXT-Facebook](https://github.com/YoYoGames/GMEXT-Facebook) |
| **Medal** | [GMEXT-Medal](https://github.com/YoYoGames/GMEXT-Medal) (clips de partida) |
| **GitHub** | [GitHub.gml](https://github.com/AlubJ/GitHub.gml) ★3 — envoltorio de la API REST de GitHub desde GML |

📁 Todas descargadas: oficiales en `extensiones_oficiales/`, comunidad en `librerias/integraciones/`.

---

## 3. Móvil: tiendas, compras y servicios

| Plataforma | Extensiones oficiales |
|---|---|
| **Google Play** | [GooglePlayServices](https://github.com/YoYoGames/GMEXT-GooglePlayServices) · [GooglePlayBilling](https://github.com/YoYoGames/GMEXT-GooglePlayBilling) · [GooglePlayLicensing](https://github.com/YoYoGames/GMEXT-GooglePlayLicensing) · [GooglePlayInstant](https://github.com/YoYoGames/GMEXT-GooglePlayInstant) · [GooglePlayIntegrity](https://github.com/YoYoGames/GMEXT-GooglePlayIntegrity) · [GooglePlayPassLicensing](https://github.com/YoYoGames/GMEXT-GooglePlayPassLicensing) · [GoogleSignIn](https://github.com/YoYoGames/GMEXT-GoogleSignIn) · [InAppUpdate](https://github.com/YoYoGames/GMEXT-InAppUpdate) |
| **Apple** | [AppleIAP](https://github.com/YoYoGames/GMEXT-AppleIAP) · [AppleSignIn](https://github.com/YoYoGames/GMEXT-AppleSignIn) · [GameCenter](https://github.com/YoYoGames/GMEXT-GameCenter) · [AppTrackingTransparency](https://github.com/YoYoGames/GMEXT-AppTrackingTransparency) |
| **Huawei** | [HuaweiPaidApps](https://github.com/YoYoGames/GMEXT-HuaweiPaidApps) |
| **Ambas** | [MobileUtils](https://github.com/YoYoGames/GMEXT-MobileUtils) · [MobileReview](https://github.com/YoYoGames/GMEXT-MobileReview) (pedir valoración) · [WebView](https://github.com/YoYoGames/GMEXT-WebView) · [Bluetooth](https://github.com/YoYoGames/GMEXT-Bluetooth) |
| **Cumplimiento legal** | [DeclaredAgeRange](https://github.com/YoYoGames/GMEXT-DeclaredAgeRange) · [PlayAgeSignals](https://github.com/YoYoGames/GMEXT-PlayAgeSignals) — 🆕 obligatorias en varias tiendas desde 2026 |

---

## 4. Anuncios y monetización

| Red | Extensión oficial | Notas |
|---|---|---|
| **AdMob** (Google) | [GMEXT-AdMob](https://github.com/YoYoGames/GMEXT-AdMob) ★14 | La más usada en móvil |
| **LevelPlay** (ironSource/Unity) | [GMEXT-LevelPlay](https://github.com/YoYoGames/GMEXT-LevelPlay) | **Sustituye a ironSource**: si empiezas hoy, usa esta |
| **ironSource** | [GMEXT-IronSource](https://github.com/YoYoGames/GMEXT-IronSource) | ⚠️ Sin cambios desde 2025-06. Migra a LevelPlay |
| **Opera Ads** | [GMEXT-OperaAds](https://github.com/YoYoGames/GMEXT-OperaAds) | Para GX.games |
| **H5 Games Ads** | [GMEXT-H5GamesAds](https://github.com/YoYoGames/GMEXT-H5GamesAds) | Web |
| **CrazyGames** | [GMEXT-CrazyGames](https://github.com/YoYoGames/GMEXT-CrazyGames) | Portal web |
| **Adjust** | [GMEXT-Adjust](https://github.com/YoYoGames/GMEXT-Adjust) | Atribución de instalaciones |

---

## 5. Back-end, datos y analíticas

| Servicio | Opción |
|---|---|
| **Firebase** | [GMEXT-Firebase](https://github.com/YoYoGames/GMEXT-Firebase) ★20 — oficial, actualizada 2026-09-01. Autenticación, Firestore, Realtime DB, Cloud Functions, Analytics |
| **HTTP genérico** | Funciones nativas (`http_get`, `http_request`…) + [http.gml](https://github.com/Sidorakh/http.gml) ★19 para servir peticiones y subir ficheros desde GML |
| **OpenAPI** | [GM-OpenAPIGenerator](https://github.com/YoYoGames/GM-OpenAPIGenerator) — genera cliente GML desde una spec |
| **Crash reporting** | [Snitch](https://github.com/JujuAdams/Snitch) ★39 |
| **Guardado en la nube** | Vía Steam Cloud (Steamworks) o Firebase |

---

## 6. Otros SDK oficiales

| Extensión | Para qué |
|---|---|
| [GMEXT-FMOD](https://github.com/YoYoGames/GMEXT-FMOD) ★74 | Audio profesional con **FMOD Studio** |
| [GMEXT-MLKit](https://github.com/YoYoGames/GMEXT-MLKit) | **La única extensión oficial de IA**: visión y texto en dispositivo |
| [GMEXT-Interhaptics-Main](https://github.com/YoYoGames/GMEXT-Interhaptics-Main) | Haptics avanzados |
| [GMEXT-Elements](https://github.com/YoYoGames/GMEXT-Elements) | Componentes de plataforma |
| [GMEXT-Photon](https://github.com/YoYoGames/GMEXT-Photon) | Multijugador — ver [`04 · Multijugador y red`](./04%20-%20Multijugador%20y%20red.md) |

> ℹ️ Sobre IA: el motor **no lleva IA integrada**. `GMEXT-MLKit` es lo único oficial.
> Detalle en [`07 - Ecosistema/14 · IA y GameMaker`](../07%20-%20Ecosistema/14%20-%20IA%20y%20GameMaker.md).

---

## 7. Cómo se instalan

Desde LTS 2026 hay dos vías:

1. **Package Manager** (recomendado) — las extensiones oficiales se instalan como paquetes
   versionados desde el propio IDE. Ver
   [`02 - Novedades 2026/08 · Package Manager y Prefabs`](../02%20-%20Novedades%202026/08%20-%20Package%20Manager%20y%20Prefabs.md).
2. **Importar el `.yymps`** del repositorio, como se hacía antes.

⚠️ Cada `GMEXT-*` tiene **requisitos de SDK nativo por plataforma** (Android SDK, Xcode,
certificados). Están documentados en su propio README y en la
[wiki de SDK requeridos](https://github.com/YoYoGames/GameMaker-Bugs/wiki#required-sdks).

---

## Fuentes

- Repositorios `GMEXT-*` de YoYo Games: <https://github.com/YoYoGames>
- awesome-gamemaker · Integrations: <https://github.com/bytecauldron/awesome-gamemaker>
- Blog oficial · *Discord Social SDK Extension Update* (04-06-2026): <https://gamemaker.io/en/blog>
- Metadatos de cada repositorio: API de GitHub, 1 de septiembre de 2026
