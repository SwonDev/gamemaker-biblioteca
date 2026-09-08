# 02 · Publicar y exportar un juego de GameMaker (2026)

> **Referencia**: GameMaker **LTS 2026.0** (IDE 2026.0.0.16 / GMS2 Runtime 2026.0.0.23).
> Documento redactado el 31 de agosto de 2026 con datos comprobados en el CLI instalado y en las
> fuentes oficiales citadas al final.
>
> **Regla de oro**: cuando un dato viene del CLI está marcado como verificado; cuando viene de
> documentación oficial se cita la fuente; cuando es una valoración o un vacío de información
> oficial se dice explícitamente.

---

## 1. Mapa de plataformas

### 1.1 Las 13 plataformas con Game Options

Verificado ejecutando `gm-cli resourcetool eval "options list"` sobre un proyecto real:

```
main
android
html5
ios
linux
mac
operagx
ps4
ps5
switch
tvos
windows
xboxseriesxs
```

**Re-verificado en vivo el 07-09-2026, con `ResourceTool@2026.0.17`: el comando sigue
funcionando exactamente así — no es una regresión.** Lo que cambia el resultado es si el
proyecto tiene la carpeta `options/` generada en disco, algo que depende de cómo se creó el
proyecto, no de la versión del ResourceTool:

- Sobre un proyecto **Blank Pixel Project** (la plantilla oficial de `gm-cli init`) y sobre
  **Towers Vs. Monsters**/**Puzzle Slider** (plantillas oficiales de la Marketplace), `options
  list` imprime la lista completa sin problema — en dos de los tres casos, con un **14.º nodo,
  `reddit`**, que esta tabla no recoge (coherente con el target Reddit/Devvit nuevo de 2026.0,
  §3.3).
- Sobre un proyecto creado desde **Space Rocks - Starter Pack** (uno de los ejemplos que cita
  `AGENTS.md` §5 para `gm-cli init`), la carpeta `options/` **no existe en absoluto** en el
  paquete del asset: `options list` no imprime nada (ni error, exit 0) y `options info
  platform=<cualquiera>` — incluso con un nombre de plataforma inventado — responde siempre
  `No licensed options for platform 'X'. Available: `. El mismo síntoma se reprodujo con otras
  plantillas GML-code de la Marketplace (Brick Breaker, Firejump, RPG Starter Pack, Scrolling
  Shooter, Farm Survivor): ninguna trae `options/` de fábrica.
- **No hay ningún flag que regenere esa carpeta desde el CLI** (comprobado con `gm-cli
  resourcetool eval --help` y `options` sin argumentos, 07-09-2026): si te pasa esto, la
  alternativa que funciona es abrir el proyecto una vez en el IDE (que crea los recursos de
  Options por defecto al guardar) o copiar la carpeta `options/` de un proyecto que sí la
  tenga.

Este hallazgo también resuelve, con evidencia en vivo, una pregunta pendiente para consolas:
en los tres proyectos que sí tienen `options/`, aparece **`switch` pero nunca `switch2`** —
detalle completo en [06 · 3.5](./06%20-%20Publicar%20en%20consolas%20-%20Nintendo%2C%20PlayStation%20y%20Xbox.md#35-la-pregunta-pendiente-resuelta-switch-2-comparte-nodo-con-switch).

### 1.2 Plataformas que el CLI puede compilar hoy

| Target del CLI | Soportado en 2.2.0 | Soportado en 2.3.0 | Notas |
|---|---|---|---|
| `windows` | ✅ | ✅ | Incluye ARM64 desde 2026.0 |
| `mac` | ✅ | ✅ | |
| `linux` | ✅ | ✅ | Ubuntu; también ARM64 (corregido en 2026.0) |
| `operagx` | ✅ | ✅ | GX.games (HTML5 + WASM) |
| `android` | ❌ | ✅ | Novedad de la 2.3.0 |
| `ios`, `tvos`, `html5`, `switch`, `ps4`, `ps5`, `xboxseriesxs`, `reddit` | ❌ | ❌ | El CLI responde: *«Support for target 'X' is coming soon to GameMaker CLI.»* |

```bash
gm-cli compile --target reddit
# Command failed:
# Support for target 'reddit' is coming soon to GameMaker CLI.
```

> **Traducción práctica**: en agosto de 2026 el CLI sirve para escritorio, GX.games y
> (en la 2.3.0) Android. Todo lo demás —iOS, consolas, Reddit, HTML5 genérico— se hace
> **desde el IDE**.

### 1.3 Guías oficiales de configuración por plataforma

YoYo Games mantiene un wiki público con las guías de setup (**no consolas**):

| Plataforma | Guía oficial |
|---|---|
| Windows | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/Windows-GMS2> |
| macOS | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/macOS-GMS2> |
| Ubuntu / Linux | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/Ubuntu-GMS2> |
| Android | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/Android-GMS2> |
| iOS | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/iOS-GMS2> |
| tvOS | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/tvOS-GMS2> |
| HTML5 | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/HTML5-GMS2> |
| GX.games | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/GX.Games-GMS2> |
| Reddit (Devvit) | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/Reddit-GMS2> |
| Requisitos de instalación | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/Install-Requirements> |
| Permisos y antivirus | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/Permissions-Guide> |
| SDKs requeridos para LTS 2026.0 | <https://github.com/YoYoGames/GameMaker-Bugs/wiki/2026.0> |

**Importante**: accede siempre a las guías **desde la página de SDKs de tu versión**, no desde el
menú lateral. El lateral muestra siempre la última versión del contenido, que puede no corresponder
a tu GameMaker.

### 1.4 Consolas: wikis privadas

Las consolas **no** se documentan públicamente por confidencialidad. Sólo son accesibles si la
compañía te ha aprobado como desarrollador:

| Consola | Wiki privada |
|---|---|
| Microsoft Xbox One / Series | <https://github.com/GameMakerEnterprise/GMS2-Runner-Xbox/wiki/> |
| Nintendo Switch | <https://github.com/GameMakerEnterprise/GMS2-Runner-Switch/wiki/> |
| **Nintendo Switch 2** | <https://github.com/GameMakerEnterprise/GMS2-Runner-Switch2/wiki/> |
| Sony PlayStation 4 | <https://github.com/GameMakerEnterprise/GMS2-Runner-PS4/wiki/> |
| Sony PlayStation 5 | <https://github.com/GameMakerEnterprise/GMS2-Runner-PS5/wiki/> |

Proceso de solicitud: <https://gamemaker.io/en/help/articles/application-process-for-console-access>

> El trámite completo de acceso —URLs de registro, contactos regionales de Nintendo, el paso a
> paso de PlayStation y Xbox verificado contra ese mismo artículo, y qué hacer cuando el detalle
> exacto vive dentro del NDA— está desarrollado en
> [06 · Publicar en consolas: Nintendo, PlayStation y Xbox §2](./06%20-%20Publicar%20en%20consolas%20-%20Nintendo%2C%20PlayStation%20y%20Xbox.md#2--el-trámite-público-antes-del-devkit).

---

## 2. Licencias: qué permite cada una

Fuente: <https://gamemaker.io/en/get>

| Capacidad | **Free** | **Professional** | **Enterprise** |
|---|---|---|---|
| Precio | Gratis | **Pago único de 99,99 USD** | Suscripción mensual o anual — **67,99 €/mes o 679,99 €/12 meses**, verificado en Steam el 07-09-2026 (detalle y fuente en [06 · 3.1](./06%20-%20Publicar%20en%20consolas%20-%20Nintendo%2C%20PlayStation%20y%20Xbox.md#31-la-licencia-enterprise-el-precio-real)) |
| Licencia | **No comercial** | **Comercial** | **Comercial** |
| Export a GX.games | ✅ | ✅ | ✅ |
| Export de escritorio (Windows/macOS/Linux) | ✅ | ✅ | ✅ |
| Export web (HTML5) | ✅ | ✅ | ✅ |
| Export móvil (Android/iOS) | ✅ | ✅ | ✅ |
| **Export a consolas** | ❌ | ❌ | ✅ |
| **Acceso al código fuente del runtime** | ❌ | ❌ | ✅ |
| Marca de agua obligatoria | ❌ No | ❌ No | ❌ No |

### Aclaraciones oficiales relevantes

- **GameMaker no impone marca de agua ni splash screen** en ningún nivel, incluido el gratuito.
  «Whether you're on the Free tier, or one of our two paid tiers, GameMaker does not force a
  watermark or splash screen on your games.»
- **Todo es gratis e ilimitado salvo dos cosas**: ganar dinero con el juego y exportar a consolas.
  > «If you want to make money from your game, you need to buy a Commercial License for $99.99.
  > If you want to export to Console you need the Enterprise subscription. Other than that,
  > everything else is free and unlimited!»
- **GMRT (el runtime nuevo)**: será gratis para uso no comercial. Para publicar comercialmente con
  GMRT hace falta licencia Professional.
  > «When we release the new GMRT […] it will be free for non-commercial use. If you wish to use
  > GMRT for a commercial release, we ask that you purchase a Professional licence.»
- **Licencias antiguas**: si compraste en su día una licencia permanente de GMS2 Desktop/Web/Mobile,
  puedes seguir publicando comercialmente con el runtime GMS2. Las suscripciones antiguas
  (Creator/Indie) no se renuevan; al caducar conviene Professional (con descuento por lo ya pagado)
  o Enterprise.
- **Enterprise incluye** acceso al código fuente del runtime y, durante el ciclo LTS26, la
  posibilidad de recibir correcciones y actualizaciones de SDK fuera del calendario de releases.

### Dónde se gestiona

- Cuenta y licencias: <https://gamemaker.io/account>
- Claves de acceso para el CLI: <https://gamemaker.io/en/account/access-keys>
- Descargas (LTS, Beta, Ubuntu): <https://gamemaker.io/en/download>

---

## 3. Plataforma por plataforma

### 3.1 GX.games (web) — el camino más corto

**Qué es**: la plataforma de publicación web de GameMaker, integrada en el ecosistema Opera GX.
Tu juego corre en el navegador como HTML5 + WASM.

**Novedades de la LTS 2026.0** (fuente: release notes oficiales):

- **Game Strip**: juego en formato banner (publicidad, plataformas, mascotas virtuales) que se
  ejecuta durante la navegación web o en la página de inicio de **Opera GX**.
- **Live Wallpaper**: proyecto que corre como **fondo de escritorio** en Windows o macOS, y puede
  reaccionar a tus interacciones o al sistema. Requiere una pequeña app complementaria para
  cargarlo en local.
- **Export del build WASM como ZIP**.

**Licencia**: disponible ya en el nivel **Free**. Es la forma de publicar sin pagar nada.

**Flujo con el CLI** (verificado: genera un ZIP de 2,1 MB en el proyecto de prueba):

```bash
# 1. Empaquetar para GX.games
gm-cli package --target operagx --toolchain GMS2@2026.0.0.23 --output ./package.zip

# 2. Vincular el proyecto a un estudio y juego de GX.games
gm-cli gxgames link --studioid <ID> --gameid <ID>

# 3. Subir el bundle (versión en formato X.Y.Z.B)
gm-cli gxgames upload --file ./package.zip --version 1.0.0.0

# 4. Metadatos obligatorios (16:9 exacto para las imágenes)
gm-cli gxgames meta \
  --title "Mi Juego" \
  --age-rating EVERYONE \
  --description "Descripción corta que se ve en la página del juego" \
  --platforms DESKTOP,MOBILE \
  --cover ./cover.png \
  --graphic ./screenshot.png

# 5. Publicar (abre la página en el navegador al terminar)
gm-cli gxgames publish
```

`publish` exige tener **todo** esto: bundle subido, portada, captura, descripción, clasificación
por edad y plataformas.

**Tutoriales oficiales**:
[Publish Your Game to GX.games In 5 Minutes](https://gamemaker.io/tutorials/publish-to-gxgames-tutorial) ·
[How to Publish a Mobile Game on GX.games](https://gamemaker.io/tutorials/publish-mobile-games-for-free) ·
[How to Get Noticed on GX.games](https://gamemaker.io/tutorials/gxgames-get-noticed) ·
[Challenges](https://gamemaker.io/tutorials/gxgames-challenges) ·
[Leaderboards](https://gamemaker.io/tutorials/gxgames-in-game-leaderboards) ·
[Avatares](https://gamemaker.io/tutorials/gxgames-in-game-avatars)

### 3.2 Opera GX

No es un target aparte: es el **navegador** donde mejor funcionan los Game Strips y el público
natural de GX.games (<https://gx.games/>). Publicar en GX.games ya te hace visible ahí. GameMaker
es propiedad de Opera (figura «Part of Opera» en el pie de la web).

### 3.3 Reddit (Devvit) — NUEVO en 2026.0

**Qué es**: target para publicar juegos jugables dentro de Reddit, usando las herramientas
**Devvit** de Reddit. **Sustituye** a la antigua extensión de Reddit que proporcionaba GameMaker.

**Estado**: disponible en el **IDE** desde la LTS 2026.0. **No disponible en el CLI**
(«coming soon»).

**Cómo funciona (y por qué es raro)**: según las release notes oficiales, este target funciona
bastante distinto de todos los demás:

- Tienes que **crear tú el proyecto de Reddit** por tu cuenta.
- Debes **ejecutar las herramientas de Devvit tú mismo, fuera de GameMaker**, para que tus cambios
  se construyan y se envíen a Reddit cada vez.
- Por eso la documentación insiste en leer la guía antes de usarlo.

**Recursos oficiales**
- Guía de setup del target: <https://github.com/YoYoGames/GameMakerRedditTemplate/blob/main/docs/HowToBuild.md>
- Plantilla: <https://github.com/YoYoGames/GameMakerRedditTemplate>
- Demo: <https://github.com/YoYoGames/GM-RedditDemo>
- Extensión: <https://github.com/YoYoGames/GMEXT-Reddit>
- Guía en el wiki: <https://github.com/YoYoGames/GameMaker-Bugs/wiki/Reddit-GMS2>
- Documentación de Devvit: <https://developers.reddit.com/docs/>

**Flujo resumido** (según el log de build que publica la comunidad y la guía oficial):

```bash
# GameMaker exporta el juego y copia los ficheros al proyecto Devvit
# (src/client/public/), y luego TÚ ejecutas:
cd <proyecto_devvit>
npm run dev      # levanta cliente, servidor y el playtest de Devvit
```

`npm run dev` arranca en paralelo el build del cliente (Vite), el del servidor y
`devvit playtest`, y da una URL del tipo
`https://www.reddit.com/r/<subreddit_dev>/?playtest=<proyecto>`.

> **Problema conocido** (reportado en el foro oficial en febrero de 2026): el servidor de Devvit
> no detecta los cambios que exporta GameMaker mientras `npm run dev` está en marcha, y hay que
> reiniciarlo o tocar un fichero que sí esté vigilando (por ejemplo `src/client/splash.html`) para
> forzar el refresco. Tenlo presente: **ralentiza la iteración**.

### 3.4 itch.io

**No existe un target «itch.io» en GameMaker.** itch.io es una tienda, no una plataforma de
ejecución. El flujo es: **exportar un ZIP y subirlo a mano**.

**Dos formatos posibles**

| Formato | Cómo | Cuándo conviene |
|---|---|---|
| **HTML5 (web)** | Exporta como HTML5 y sube el ZIP para que itch.io lo ejecute en el navegador | Máximo alcance, cero instalación. Es lo habitual en game jams |
| **Windows** | `gm-cli package --target windows` y sube el ZIP/EXE | Cuando quieras descargable de escritorio |

```bash
# Opción recomendada para itch.io: build web
gm-cli package --target operagx --output ./itch-web.zip     # HTML5+WASM del runtime operagx
# Para escritorio:
gm-cli package --target windows --output ./itch-windows.zip
```

> **Matiz**: el target `operagx` es la variante HTML5/WASM que empaqueta GameMaker para su propia
> plataforma. Si vas a publicar el juego web **fuera** de GX.games (itch.io, tu propia web), usa el
> target **HTML5** del IDE (`html5` está en `options list`), que es el export web genérico.

**Recurso oficial para el paso final**:
[Quickstart On Exporting And Sharing Your Game](https://gamemaker.io/tutorials/quickstart-on-exporting-and-sharing-your-game)

### 3.5 Steam

**No hay export nativo a Steam**: Steam es una tienda. Lo que publicas es un **build de Windows
(más Linux y macOS si quieres)** y lo subes con Steamworks.

**La extensión oficial**: [`GMEXT-Steamworks`](https://github.com/YoYoGames/GMEXT-Steamworks) —
logros, estadísticas, cifrado de Steam, talleres, etc. Novedades anunciadas para 2026: soporte de
**ISteamParties**.

**Multijugador** (el blog oficial Spring 2026 recomienda socios externos):
- [Namazu Elements](https://github.com/YoYoGames/GMEXT-Elements)
- [Colyseus](https://docs.colyseus.io/getting-started/gamemaker)
- [Photon](https://www.photonengine.com) (anunciado como próximo)
- Steamworks (soporte oficial continuado)

**Flujo**:

```bash
# 1. Build de release de Windows (usa YYC / native para rendimiento)
gm-cli compile --target windows --runtime native --config Release --errors-only

# 1 bis. Antes de subir a Steam, repite el build SIN --errors-only y lee los WARNING —
#        el flag anterior silencia avisos reales (p. ej. un included file que no se copió).
gm-cli compile --target windows --runtime native --config Release

# 2. Empaquetar
gm-cli package --target windows --output ./steam-windows.zip

# 3. Subir con las herramientas de Steamworks (SteamPipe / steamcmd), fuera de GameMaker
```

> ⚠️ `--errors-only` sirve para iterar, no para el build final: silencia los `WARNING` de
> compilación, incluido el de un *included file* creado por `resourcetool` que no llegó al
> paquete. Antes de subir un build a cualquier tienda, compílalo también sin ese flag — detalle
> en [`12 · 09` §0 Trampa 8](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-8--resource-create-typeincludedfile-deja-filepath-fuera-de-datafiles-y---errors-only-no-lo-detecta).
>
> El alta de la app en Steamworks (Steam Direct, ~100 USD), el `app_build.vdf`/`depot_build.vdf`
> reales, el comando exacto de `steamcmd` y las ramas beta están desarrollados con detalle en
> [05 · 05 §4](./05%20-%20Entregar%20el%20juego%20-%20firmar%2C%20notarizar%20y%20subir%20a%20las%20tiendas.md#4--steam-alta-de-la-aplicación-depósitos-y-subida).
> Y antes de distribuir un build de macOS fuera de la Mac App Store hace falta firmarlo y
> notarizarlo — proceso completo en [05 · 05 §2](./05%20-%20Entregar%20el%20juego%20-%20firmar%2C%20notarizar%20y%20subir%20a%20las%20tiendas.md#2--macos-firma-y-notarización).

### 3.6 Steam Deck

**No existe un target «Steam Deck» y no hay mención oficial de Steam Deck en las release notes de
la LTS 2026.0** (se buscó literalmente el término en el texto completo de las notas: cero
coincidencias).

En la práctica funciona por dos vías:

1. **Build nativo de Linux** (`--target linux`): Steam Deck corre SteamOS, que es Linux.
   Es la vía limpia.
2. **Build de Windows + Proton** (la capa de compatibilidad de Valve): es la vía más común y
   normalmente la que mejor resultado da sin trabajo extra.

Recomendación pragmática: construye para **Windows** con `--runtime native`, prueba bajo Proton y,
si quieres exprimirlo, añade el build de Linux.

#### Los criterios de UX de Steam Deck Verified

Lo de arriba es solo cómo se **compila** el binario. **Verified** es una insignia de experiencia de
usuario, completamente independiente del target: la otorga una revisión manual de Valve contra un
checklist público, y GameMaker no tiene ninguna casilla propia para marcarlo. Fuente primaria —
`partner.steamgames.com/doc/steamdeck/compat`, abierta con `curl -sL -A "Mozilla/5.0"` el 6 de
septiembre de 2026—:

| Criterio del checklist | Qué exige exactamente |
|---|---|
| **Legibilidad de texto** | El carácter más pequeño en pantalla no puede bajar de **9 px de altura a la resolución 1280×800** (la nativa recomendada de Deck). Valve recomienda apuntar a 12 px cuando se pueda; por debajo de 9 px, falla |
| **Glifos de mando** | Los iconos en pantalla deben coincidir con la entrada activa (Deck, Steam Controller o Xbox); nunca mostrar iconos de teclado/ratón mientras el jugador usa el mando. Usar la **API de Steam Input** lo resuelve automáticamente, según la propia recomendación de Valve |
| **Configuración de mando por defecto** | Tiene que dar acceso a **todo** el contenido del juego sin que el jugador toque un ajuste antes |
| **Entrada de texto** | Cualquier campo de texto (nombre de personaje, partida) debe abrir el **teclado en pantalla de Steam** vía la API de Steamworks para quien juega solo con mando, o traer un teclado propio navegable sin teclado físico |
| **Configuración por defecto jugable** | 30 fps a 800p como mínimo aceptable en la configuración con la que arranca el juego |

⚠️ **Suspensión/reanudación no aparece en este checklist** tal y como está publicado hoy: se
revisó el texto íntegro de la página el 6 de septiembre de 2026 y no hay ninguna mención a
«suspend» ni «resume». Se cita a menudo como requisito de Steam Deck Verified, pero en la fuente
primaria actual **no forma parte de los criterios documentados**; no lo des por hecho sin volver a
comprobar esta misma página antes de depender de él. (Si buscas ese comportamiento de todos modos,
es una exigencia real y documentada de las **consolas de sobremesa** — ver §3.8 bis.)

Nada de esto tiene una función propia de GameMaker: los glifos y el teclado en pantalla se
resuelven con la extensión **Steamworks** — `steam_show_gamepad_text_input(...)` y
`steam_show_floating_gamepad_text_input(...)` están verificadas en el código real de
`GMEXT-Steamworks` (no en `buscar.py`: son de extensión, no del runtime) — y el tamaño de fuente
mínimo es una decisión de tu propio sistema de UI escalable, no un ajuste del IDE.

### 3.7 Móviles: Android e iOS

| Requisito | Detalle |
|---|---|
| Android | Guía oficial: <https://github.com/YoYoGames/GameMaker-Bugs/wiki/Android-GMS2>. En 2026.0 se actualizaron **todas las comprobaciones de rutas del toolchain de Android** para coincidir con la estructura de carpetas de **NDK 23+** |
| iOS | Guía oficial: <https://github.com/YoYoGames/GameMaker-Bugs/wiki/iOS-GMS2> |
| tvOS | Guía oficial: <https://github.com/YoYoGames/GameMaker-Bugs/wiki/tvOS-GMS2> |
| Licencia | Los exports móviles están incluidos en el nivel **Free** (aunque sin uso comercial) |
| IAPs | Extensiones oficiales `GMEXT-AppleIAP` y `GMEXT-GooglePlayBilling`, ambas con actualizaciones anunciadas |
| CLI | `android` es target válido **a partir de la 2.3.0**; iOS no está soportado |

> Estas guías cubren el **export**, no el trámite de la tienda: firma con Play App Signing, el
> `.aab` frente al `.apk`, la ficha de privacidad de Google Play, los certificados de distribución
> de Apple y el proceso de revisión de la App Store están en
> [05 · 05 §5 y §6](./05%20-%20Entregar%20el%20juego%20-%20firmar%2C%20notarizar%20y%20subir%20a%20las%20tiendas.md#5--google-play-app-bundle-firma-ficha-y-pruebas).

### 3.8 Consolas

| Consola | Estado en 2026.0 |
|---|---|
| **Nintendo Switch 2** | **NUEVO target en la LTS 2026.0.** Configuración muy similar a Switch 1, pero con guía propia. Wiki privada: `GMS2-Runner-Switch2` |
| Nintendo Switch | Soportado. Wiki privada: `GMS2-Runner-Switch` |
| PlayStation 4 / 5 | Soportados. Wikis privadas: `GMS2-Runner-PS4`, `GMS2-Runner-PS5` |
| Xbox One / Series | Soportado. Wiki privada: `GMS2-Runner-Xbox` |

**Requisito de licencia**: **Enterprise**. Además, cada fabricante debe aprobarte como
desarrollador (el proceso está en el artículo de ayuda enlazado en la sección 1.4).

**Sobre Switch 2**, las release notes dicen literalmente: «This uses a very similar setup to
Switch 1, but please do see the setup guides before attempting any builds or filing any bugs.»
El foro oficial recuerda además que los detalles de consola están **bajo NDA** y sólo se discuten
en el foro privado de desarrolladores verificados.

> El trámite de acceso a cada fabricante (con URLs y contactos reales), el vocabulario del
> oficio (*lotcheck*, TRC, XR, Gamerscore…) y lo que sí es público sobre cada consola están en
> [06 · Publicar en consolas: Nintendo, PlayStation y Xbox](./06%20-%20Publicar%20en%20consolas%20-%20Nintendo%2C%20PlayStation%20y%20Xbox.md) —
> no se repite aquí.

### 3.8 bis · Qué exige una consola aunque no puedas contarlo

El detalle técnico de cada consola (las wikis `GMS2-Runner-*` de arriba) está bajo NDA: no se
puede citar aquí ni aunque se tuviera acceso. Pero las **categorías** de lo que certifica cada
fabricante son de conocimiento público — repetidas en charlas GDC, en la documentación pública de
otros motores y en la experiencia compartida de la industria durante décadas. Lo que cambia de una
consola a otra son los umbrales exactos (segundos, píxeles, redacción legal), no la lista de qué se
revisa. ⚠️ Esta tabla describe **categorías públicas**, no el contenido de ninguna wiki privada de
YoYo Games ni de ningún acuerdo de desarrollador; los números exactos están fuera de esta
biblioteca.

| Categoría | Qué exige, en general | Por qué existe |
|---|---|---|
| **Mapeo de botones consistente** | El botón que confirma/cancela en tu juego tiene que significar lo mismo en todas tus pantallas, y coincidir con la convención del sistema — no con la tuya | Un jugador que sale al dashboard y vuelve no puede tener que reaprender qué hace cada botón |
| **El botón de confirmar cambia por región** | En PlayStation, el botón físico que confirma un diálogo del sistema depende de la región: «✕» confirma en Occidente, «○» confirma en Japón (configurable como ajuste de accesibilidad desde PS4). Xbox tuvo una convención regional parecida en generaciones anteriores | Herencia de la convención de mandos japonesa; los certificadores comprueban que respetas el mapeo del sistema activo, no que impongas el tuyo |
| **Suspensión y reanudación** | El juego tiene que sobrevivir a que la consola entre en reposo (tapa cerrada, botón de energía) y seguir exactamente donde estaba al volver, sin recargar ni perder estado | Es el comportamiento por defecto que el sistema operativo de la consola le garantiza al usuario en cualquier app |
| **Desconexión de mando y cambio de usuario** | El juego debe pausar y avisar si el mando se desconecta a mitad de partida, y tolerar que cambie el perfil de usuario activo (otro jugador se loguea) sin crashear ni mezclar guardados de perfiles distintos | Garantía de plataforma, no opcional: el fabricante responde ante el usuario si un juego la rompe |
| **Tiempos de arranque** | Cada fabricante certifica un tiempo máximo desde «pulsar Jugar» hasta que el juego es interactivo, con cifras concretas bajo NDA | En consola el arranque lento es un fallo de certificación, no solo una queja de reseña |
| **Guardado que no puede fallar** | El progreso no puede perderse por un corte de luz, un disco lleno o retirar el mando a mitad de escritura — el mismo patrón de escritura atómica (temporal + reemplazo) de [13 · 06 §3.10](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#310-estado-global-guardado-y-migraciones) | Un guardado corrupto es un caso de soporte que recae también sobre el fabricante, no solo sobre ti |
| **Textos legales y avisos de salud** | Cada plataforma exige sus propios textos legales (marcas del fabricante, número de certificación) en pantallas de carga o créditos, y un aviso de fotosensibilidad/epilepsia antes de la primera pantalla jugable | Requisito legal del fabricante, no una sugerencia de diseño |

Nada de esto se traduce en una función de GML: son requisitos de **proceso y contenido**, no de
API. Lo único que sí tocas en código ya está documentado en esta biblioteca: el guardado atómico
de la fila de arriba, y para suspensión/reanudación el ciclo de vida normal de `obj_game` — sala
persistente y reconexión de servicios al volver — en
[13 · 06 §3.2](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#32-obj_game-el-controlador-persistente),
más las llamadas de suspensión propias del SDK de cada consola, que sí están bajo NDA.

### 3.9 Windows ARM64 — NUEVO en 2026.0

Según las release notes oficiales:

- Puedes crear juegos que apunten a **dispositivos Windows ARM64**.
- En **Run/Debug** no hay que elegir nada: el juego detecta al arrancar la arquitectura del
  dispositivo y ejecuta el runner correcto (x64 o ARM64).
- En **Create Exe** hay nuevas opciones en el diálogo de tipo de paquete: además de los tipos
  existentes, puedes construir un **ARM64 Zip** o un **ARM64 NSIS .exe**.
- Para confirmar que estás ejecutando la versión ARM64, el Administrador de tareas tiene una
  columna «Arquitectura» oculta por defecto en la pestaña *Detalles*: hay que habilitarla.

---

## 4. Game Options que importan en un build de release

### 4.1 Cambios de 2026.0 que afectan a tu publicación

Fuente: release notes oficiales de la LTS 2026.0.

| Opción | Qué cambió y por qué te afecta |
|---|---|
| **Nombre del producto / display** | Antes todo se llamaba «Created in GameMaker». Ahora se usa el **nombre inicial del proyecto**. Esto es crítico: con el valor por defecto antiguo, **las subidas a GX.games fallaban porque el nombre ya estaba cogido**, y los instaladores creaban carpetas llamadas «Created In GameMaker». Si renombras el proyecto más tarde, actualiza estos valores a mano |
| **Vsync** | Ahora **activo por defecto** en todos los targets compatibles |
| **Interpolate colours between pixels** (Windows) | Ahora **activo por defecto**, para coincidir con el manual y con el resto de targets |
| **Descarte automático de assets** | El compilador **descarta automáticamente** cualquier asset no referenciado directamente (ni usado en una room/secuencia ni referenciado en código). Se puede desactivar en General Game Options |
| **`gml_pragma("MarkTagAsUsed")`** | Permite marcar ciertos tags como «usados» para que **siempre** se incluyan en el paquete final, burla del punto anterior |
| **Sección «Deprecated Behaviours»** | Nueva sección en General Game Options para reactivar comportamientos antiguos cambiados o deprecados: `instance_change`, `position_change`, el cambio de colisiones, los cambios de parseo de JSON, conversión string→número, tratamiento de `other`, errores estrictos de audio, etc. |
| **Mipmaps** | Se eliminó la entrada redundante «Generate Mipmaps For Separate Texture Pages»; ahora se gestiona en el editor de **Texture Groups** |
| **Texture pages** | Game Options exporta los valores de texture pages como `.json` al pulsar *Preview*, para poder editarlos y usarlos en el juego |
| **Cuenta usada para registrar** | Game Options te dice siempre **qué cuenta** usará GameMaker para registrar/subir, evitando fallos por tener iniciada otra cuenta SSO en el navegador |

### 4.2 Configuraciones (configs)

Verificado con `gm-cli resourcetool eval "config list"`:

```
┌─────────────┬────────────┐
│ Config name │ Is active? │
╞═════════════╪════════════╡
│ Default     │ (active)   │
└─────────────┴────────────┘
```

Puedes crear una configuración `Release` y construir con ella:

```bash
gm-cli resourcetool eval "config create name=Release"
gm-cli compile --config Release --target windows --runtime native
```

Todos los flags de `--config` están disponibles en `run`, `compile`, `package` y `resourcetool`.

### 4.3 VM vs YYC (native)

```bash
gm-cli compile --runtime vm      # por defecto: GMS2 VM, compila rápido, ejecuta algo más lento
gm-cli compile --runtime native  # YYC: compilación anticipada, build más lento, juego más rápido
```

Regla práctica: **VM durante el desarrollo**, **YYC para el build de release**.

### 4.4 Checklist previa a un build de release

- [ ] **Nombre de producto/display** correcto en Game Options (ya no vale «Created in GameMaker»)
      — la propiedad de `resourcetool` es `display_name` (en el `.yy` se llama `option_windows_display_name`), `option_windows_product_info`
      para el nombre de producto; nombres equivalentes por plataforma en
      [07 · 24 §2.2](../07%20-%20Ecosistema/24%20-%20Logotipo%2C%20icono%20del%20ejecutable%20y%20capsule%20de%20tienda.md#22-la-vía-nativa-de-gamemaker-resourcetool-options-set-hallazgo-verificado).
- [ ] **Icono** y **splash** propios por plataforma — `icon` en Windows para `resourcetool` (`option_windows_icon` dentro del `.yy`) — ruta a un
      `.ico`, tabla completa por plataforma en [07 · 24 §2.2](../07%20-%20Ecosistema/24%20-%20Logotipo%2C%20icono%20del%20ejecutable%20y%20capsule%20de%20tienda.md#22-la-vía-nativa-de-gamemaker-resourcetool-options-set-hallazgo-verificado)).
- [ ] **Versión** en formato `X.Y.Z.B`. ⚠️ Hay DOS campos de versión distintos, no uno: `option_version`
      (Main Options, un entero plano — no es `X.Y.Z.B`) y `version` para `resourcetool` (`option_windows_version` en el `.yy`; por plataforma, un
      struct `{major, minor, revision, build}` — este sí lo es). Detalle y el hallazgo completo en
      [13 · 11 §4.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/11%20-%20Producción,%20alcance%20y%20lanzamiento.md#43-numerar-las-versiones).
- [ ] **Configuración Release** activa o pasada por `--config Release`.
- [ ] Compilar con **`--runtime native`** (YYC).
- [ ] Revisar el **descarte automático de assets**: si cargas algo por nombre en tiempo de
      ejecución, márcalo con `gml_pragma("MarkTagAsUsed", ...)`.
- [ ] **Texture Groups** revisados (tamaño de páginas, mipmaps).
- [ ] **Vsync** e **interpolación de color** según el resultado visual que busques.
- [ ] **Sin `show_debug_message()` de depuración sobrante.** El patrón correcto (niveles de log
      que se apagan solos en release) está en
      [13 · 10 §7.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md);
      revisa en concreto el código propio del proyecto, no solo el copiado de esta biblioteca —
      `show_debug_message` aparece en decenas de recetas como ejemplo de depuración, no como algo
      que deba sobrevivir al build final.
- [ ] Probar el **build empaquetado**, no sólo el Run del IDE: es lo que se instala el jugador.
- [ ] **Probar el instalador/paquete en una máquina que NUNCA tuvo GameMaker instalado** (una VM
      limpia basta): DLLs y redistribuibles ausentes son el fallo clásico de un build de Windows
      que «funciona en mi máquina» y falla en la del jugador — el Run del IDE y una máquina de
      desarrollo perdonan dependencias que el instalador real no trae solo.
- [ ] Comprobar el **tamaño del paquete** y los tiempos de carga (cómo medirlo y qué es
      razonable: §4.5).
- [ ] Si publicas en GX.games: portada y capturas **16:9 exactos**, clasificación por edad y
      plataformas definidas antes de `publish`.
- [ ] Si distribuyes fuera de GX.games: el `.exe` de Windows y el `.app` de macOS van **firmados**
      (y el de macOS, además, **notarizado**) antes de llegar a un jugador —
      [05 · 05 §2 y §3](./05%20-%20Entregar%20el%20juego%20-%20firmar%2C%20notarizar%20y%20subir%20a%20las%20tiendas.md).

> ⚠️ **Si `resourcetool options set/get/info` te devuelve `No licensed options for platform 'X'`,
> no es tu licencia: es la red.** Bajo el *sandbox* del Bash de un agente, Igor no puede validar la
> licencia y el mensaje que acaba viendo el agente es ese, que despista. Verificado el 08-09-2026:
> con el sandbox desactivado el comando funciona y hasta valida las dimensiones del icono.
> Si te pasa, comprueba `gm-cli login status` primero (puede ser la licencia, no un bug), y si
> sigue sin funcionar, **usa el IDE**: la ventana de *Game Options* por plataforma edita los
> mismos campos de esta lista directamente, y *Herramientas → Project Image Generator* rellena el
> icono en todas las plataformas de una vez
> ([07 · 24 §2.6](../07%20-%20Ecosistema/24%20-%20Logotipo%2C%20icono%20del%20ejecutable%20y%20capsule%20de%20tienda.md#26-la-alternativa-desde-el-ide-project-image-generator)).
> Nunca edites el `.yy` de las Game Options a mano (`AGENTS.md §4`).

### 4.5. Presupuesto de build: tamaño y arranque

El checklist de arriba pide «comprobar el tamaño del paquete y los tiempos de carga» desde hace
tiempo, sin decir cómo ni contra qué cifra. Esto es cómo.

#### 4.5.1 De qué está hecho el tamaño de un build

No es un número: son piezas distintas, y cada una se ataca de una forma distinta.

| Componente | Dónde se ve | Qué lo controla |
|---|---|---|
| **Texture pages** (sprites, tiles, fuentes) | Ventana **Texture** del Debug Overlay ([01 · 15 §4](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#4-nivel-3-el-debug-overlay)) | Tamaño de página y compresión en el **Texture Group Editor**; catálogo completo de funciones en [08 · 08](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md) |
| **Audio** | Tamaño de archivo por *sound asset* en el editor | Atributo de importación (comprimido / sin comprimir / *streamed*) — ya cubierto en detalle en [13 · 09 §7](<../13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md#7--formatos-y-ajustes-de-importación>), no se repite aquí |
| **Included Files** | Carpeta `datafiles/` del proyecto | Todo lo que metas ahí a mano: `.json` de localización, guiones, `.ttf` no usados como *font asset*, vídeos |
| **El *runtime* en sí** | Peso fijo del ejecutable/paquete vacío | No lo controlas tú: es el coste base de VM o YYC para esa plataforma |
| **Assets sin usar** | Se descartan solos desde 2026.0 | Ver §4.1 arriba (descarte automático) — si cargas algo por nombre en tiempo de ejecución y desaparece del build, es esto, no un bug |

> **El tope de 4 GB del paquete final** ([01 · 01](<../01 - Fundamentos/01 - El IDE y el flujo de trabajo.md#checklist-antes-de-compilar-el-build-definitivo>))
> **no cuenta** sonidos en *streaming*, texturas dinámicas ni *Included Files* — así que un
> proyecto puede sentirse «pequeño» según ese límite y aun así pesar varios gigas de verdad en
> disco por lo que ese tope no mide. Mide siempre el tamaño real de la carpeta exportada, no solo
> si compila por debajo del tope.

#### 4.5.2 Cómo ver qué ocupa, de verdad

1. **La ventana Texture del Debug Overlay** ([01 · 15 §4](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#4-nivel-3-el-debug-overlay))
   lista cada *texture page* con su ancho, alto, grupo y número de mipmaps — es la vía más directa
   para ver qué páginas pesan más sin adivinar. La ventana **Memory** de al lado da la memoria
   asignada y libre del proceso, útil para VRAM, no para el tamaño del paquete en disco.
2. **`texture_debug_messages(true)`** ([08 · 08](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md))
   informa por consola de cada carga y descarga de página de textura en tiempo real: útil para ver
   *cuándo* entra cada grupo, no solo cuánto pesa.
3. **El tamaño real es el de la carpeta que genera `gm-cli package`**, no una estimación: en
   macOS/Linux, `du -sh ./builds/mi-juego/`; en Windows, propiedades de la carpeta. Es el número
   que de verdad se descarga el jugador, y el único que no depende de estar interpretando bien un
   contador interno.
4. **Grupos de texturas dinámicos** (`texturegroup_get_status`, `texture_is_ready`,
   [08 · 08](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md))
   te dicen en runtime qué parte del contenido está cargada; no miden bytes en disco, pero sí
   cuánto de ese contenido puedes **diferir** en vez de meterlo en el arranque (§4.5.3).

#### 4.5.3 Qué reduce el tamaño de verdad, y qué no

| Hace algo | No hace casi nada |
|---|---|
| Ajustar el tamaño de página y la compresión de los **Texture Groups** (menos relleno, mejor empaquetado de sprites) | Comprimir un `.png` fuera de GameMaker antes de importarlo: el IDE lo vuelve a procesar igual |
| Elegir **Comprimido** o **Comprimido - Streamed** en audio largo, en vez de sin comprimir ([13 · 09 §7](<../13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md#7--formatos-y-ajustes-de-importación>)) | Bajar la calidad de audio de un SFX corto: el ahorro es de kilobytes, y ya se paga con latencia (mismo documento) |
| Sacar de `datafiles/` lo que no se usa: un asset copiado «por si acaso» pesa igual que uno que sí se usa | Confiar en el descarte automático de assets (§4.1) para algo que cargas por nombre sin `gml_pragma("MarkTagAsUsed", ...)`: eso lo hace desaparecer, no lo comprime |
| **Compresión de texturas GPU (ASTC/DDS)** vía la extensión oficial `GM-GPUTextureCompression` ([02 · 06 §7](<../02 - Novedades 2026/06 - Gráficos - SVG, SDF, FX y superficies.md#7-compresión-de-texturas-gpu>)) — reduce mucho el consumo de VRAM, no tanto el tamaño del paquete en disco | Reducir la resolución de las texturas «un poco»: si el ahorro importa, se nota mejor bajando el número de variantes/frames que la resolución de cada uno |
| `texture_global_scale()` en dispositivos con poca VRAM ([08 · 08](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md)) — baja memoria en tiempo de ejecución | Lo mismo, esperando que también baje el tamaño del paquete: escala en runtime, no recomprime el archivo exportado |

> ⚠️ **La extensión de compresión de texturas GPU no va en el core** ([02 · 06 §7](<../02 - Novedades 2026/06 - Gráficos - SVG, SDF, FX y superficies.md#7-compresión-de-texturas-gpu>)):
> es un repositorio aparte de YoYo Games, con soporte que varía por plataforma. Pruébala en tu
> plataforma objetivo antes de depender de ella para el presupuesto final.

#### 4.5.4 Objetivos razonables por plataforma

⚠️ GameMaker no publica una cifra oficial de «tamaño razonable» — el vacío que ya reconoce §6 más
abajo—, así que esto combina lo que sí está verificado (los límites duros de las propias tiendas)
con criterio de producto, marcado aparte:

| Plataforma | Cifra verificada | Fuente |
|---|---|---|
| **iOS/iPadOS** (App Store Connect) | Tamaño máximo de app sin comprimir: **4 GB** desde iOS 9.0 | developer.apple.com, *Maximum build file sizes* (06-09-2026) |
| **Android** (Google Play) | Módulo base: **500 MB**. **Por encima de 200 MB, el usuario ve un aviso antes de descargar con datos móviles** | support.google.com, *App size limits* (06-09-2026) |
| **Escritorio (Windows/macOS/Linux)** | Sin límite de tienda salvo el genérico de GameMaker (4 GB, §4.5.1) | — |

⚠️ **Criterio de producto, no cifra oficial de ninguna tienda**: en **web (HTML5/GX.games)**, el
tamaño condiciona directamente cuánto tarda alguien en empezar a jugar desde un enlace — cuantos
menos megas antes del primer frame jugable, menos abandono en la carga inicial; en **móvil**, el
umbral de los 200 MB de Google Play de la tabla es el que de verdad importa para no perder a quien
navega con datos, más que ningún «tamaño ideal» abstracto. No hay una cifra universal correcta:
la referencia es la propia categoría de tu juego en la tienda a la que apuntas, no un número de
esta biblioteca.

#### 4.5.5 Medir el tiempo hasta el primer frame

«Tiempo de carga» no es una sola cosa: es el tiempo hasta que aparece **algo** en pantalla (splash
o pantalla de título) y, aparte, el tiempo hasta que la sala **jugable** responde a un input.

- **`get_timer()` alrededor de tu propio arranque** —del Create de tu controlador persistente
  ([13 · 06 §3.2](<../13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md#32-obj_game-el-controlador-persistente>),
  `obj_game`) al primer `room_goto` a una sala jugable— mide microsegundos reales de arranque. Es
  la misma técnica que ya usa la pantalla de carga real de
  [04 · 41 §3.3](<../04 - Recetas por género/41 - Transiciones, carga y pausa.md#33-la-pantalla-de-carga-real>)
  para medir el progreso de `texturegroup_get_status()`, aplicada aquí al arranque completo del
  juego en vez de a un cambio de sala.
- **Mide el build empaquetado, no el Run del IDE.** El IDE mantiene cosas en caché entre
  ejecuciones que un jugador que instala por primera vez no tiene: el primer arranque real es
  siempre más lento que el décimo en tu máquina de desarrollo.
- **Diferir con grupos de texturas es la palanca principal para bajar ese tiempo**, no comprimir
  más: `texturegroup_load(nombre, false)` al arrancar solo pide a disco lo que hace falta para el
  menú, y el resto se carga bajo demanda con la pantalla de carga de
  [04 · 41 §3.3](<../04 - Recetas por género/41 - Transiciones, carga y pausa.md#33-la-pantalla-de-carga-real>)
  cuando el jugador entra en la sala que de verdad lo necesita.
- **En web, el primer frame incluye la descarga del propio WASM** antes de que se ejecute una sola
  línea de tu GML: eso pesa en el tiempo total mucho más que cualquier optimización de texturas, y
  no hay función de GML que lo acelere — es exactamente el terreno de §4.5.4 (tamaño del paquete
  web) más que del código.

---

## 5. Automatizar la publicación (CI)

`gm-cli init --actions` genera dos workflows listos para usar. El de empaquetado es manual
(`workflow_dispatch`) y define una matriz de runner + target:

```yaml
strategy:
  matrix:
    include:
      - runner: ubuntu-latest
        target: operagx
      # - runner: ubuntu-latest
      #   target: linux
      # - runner: ubuntu-latest
      #   target: windows
      # - runner: macos-latest
      #   target: mac

steps:
  - uses: actions/checkout@v6
  - uses: actions/cache@v5
    with:
      path: .gmcache
      key: ${{ runner.os }}-gmcache-${{ matrix.target }}
  # ffmpeg es obligatorio en Linux (issue #4977)
  - name: Install FFmpeg if not cached
    run: |
      VERSION=6.0.1
      RELEASE_NAME=ffmpeg-${VERSION}-amd64-static
      mkdir -p ~/.local/share/ffmpeg-bin
      wget --timeout=8 --tries=10 https://www.johnvansickle.com/ffmpeg/old-releases/${RELEASE_NAME}.tar.xz
      tar -xf ${RELEASE_NAME}.tar.xz
      mv ${RELEASE_NAME}/ffmpeg ${RELEASE_NAME}/ffprobe ~/.local/share/ffmpeg-bin/
      echo "$HOME/.local/share/ffmpeg-bin" >> $GITHUB_PATH
  - run: npx "$GM_COMMAND" login "$GAMEMAKER_PAT"     # sólo si defines el secret
  - run: npx "$GM_COMMAND" package --target ${{ matrix.target }} --output ./package.zip
  - uses: actions/upload-artifact@v7
    with:
      name: ${{ env.ARTIFACT_NAME }}                   # nombre-target-commit.zip
      path: ./package.zip
```

Notas:

- Cachea **`.gmcache`**: es lo que hace rápidas las ejecuciones siguientes.
- **FFmpeg es obligatorio en Linux** (referencia al issue #4977 de GameMaker-Bugs).
- El secreto `GAMEMAKER_PAT` se crea en *Settings → Secrets and variables → Actions*, y el valor
  sale de <https://gamemaker.io/en/account/access-keys>. El paso de login se salta si el secreto no
  está definido (se usa la licencia guest).
- Con la **2.3.0** puedes añadir `- target: android` a la matriz.

Publicar en GX.games desde CI es encadenar los comandos de `gm-cli gxgames` al final del job.

---

## 6. Vacíos de información (honestidad)

| Tema | Qué consta y qué no |
|---|---|
| **Steam Deck** | No hay target oficial ni mención en las release notes de 2026.0. Funciona vía Linux nativo o Windows + Proton |
| **itch.io** | No hay integración oficial: es exportar un ZIP y subirlo a mano |
| **Duración/tamaño de builds** | No hay cifras oficiales publicadas por plataforma |
| **Consolas** | Todo el detalle técnico está bajo NDA en wikis privadas; no se puede documentar públicamente |
| **Targets del CLI** | iOS, tvOS, HTML5, consolas y Reddit están explícitamente «coming soon»; no hay fecha pública |
| **Discord Activities** | Son apps web embebidas en un `iframe` dentro de un canal de voz/texto de Discord, vía el *Embedded App SDK* de Discord (con su proxy de red obligatorio: nada de peticiones a dominios no declarados). GameMaker **no tiene target ni extensión oficial para esto hoy**. El roadmap 2026-2028 solo menciona el **«Discord Social SDK»** como extensión próxima ([`02 - Novedades 2026/10`](../02%20-%20Novedades%202026/10%20-%20Futuro%20-%20roadmap%202026-2028.md)) — es presencia/amigos/invitaciones para juegos de escritorio o consola, **no** Activities. Lo único de Discord ya en el ecosistema es [`Discord.gml`](../11%20-%20Código%20descargado/_CATALOGO.md) (Rich Presence de escritorio vía RPC nativo), ajeno a Activities. ⚠️ En teoría el export **HTML5** genérico (§3) podría envolverse a mano con el SDK de Discord, pero nadie en esta biblioteca lo ha probado ni hay guía oficial de YoYo: sería trabajo de integración desde cero |
| **AR (realidad aumentada) móvil** | GameMaker no expone la cámara del dispositivo ni tracking del mundo real en ninguna función del runtime (`buscar.py --listar device_camera` → 0 resultados) y no hay ninguna extensión, oficial o de comunidad, tipo ARKit/ARCore en el catálogo de `11 - Código descargado/_CATALOGO.md`. **No hay soporte, ni parcial.** Haría falta escribir una extensión nativa (GMEXT) que envuelva ARKit (iOS) y ARCore (Android) por separado y puentee cada frame de cámara y cada pose de tracking a GML — un desarrollo grande, sin nada reutilizable hoy en el ecosistema |
| ***Serious games*** (entrenamiento, educación, simulación corporativa) | Es una etiqueta de **propósito**, no un target técnico: cualquier receta de esta biblioteca sirve igual, y no exige nada especial del motor. Lo que sí falta es la pieza que estos proyectos suelen necesitar para integrarse con un LMS: **SCORM o xAPI/Tin Can** (registrar progreso y notas en una plataforma de formación externa). No hay ninguna mención, extensión ni ejemplo de SCORM/xAPI en toda la biblioteca ni en el código descargado. Se podría construir a mano sobre `http_request()` hablando con un *Learning Record Store* xAPI, pero es integración propia, no algo que GameMaker resuelva |

---

## 7. Fuentes

**Oficiales**
- Notas de versión LTS 2026.0 (IDE 16 / Runtime 23): <https://releases.gamemaker.io/release-notes/2026/0>
- Índice de notas de versión: <https://releases.gamemaker.io/>
- Precios y licencias: <https://gamemaker.io/en/get>
- Descargas (LTS / Beta / Ubuntu): <https://gamemaker.io/en/download>
- Centro de ayuda: <https://gamemaker.io/en/help>
- GX.games: <https://gx.games/>
- Wiki de SDKs y guías de plataforma: <https://github.com/YoYoGames/GameMaker-Bugs/wiki>
- Página de SDKs de la LTS 2026.0: <https://github.com/YoYoGames/GameMaker-Bugs/wiki/2026.0>
- Blog «GameMaker LTS 2026.0: New Features, GMRT and Much More»: <https://gamemaker.io/en/blog/lts-2026-release>
- Blog «GameMaker Update Spring 2026» (roadmap, extensiones, multijugador): <https://gamemaker.io/en/blog/update-spring-2026>
- Marketplace de assets: <https://marketplace.gamemaker.io/>

**Extensiones oficiales (GitHub)**
- Steamworks: <https://github.com/YoYoGames/GMEXT-Steamworks>
- Namazu Elements (multijugador): <https://github.com/YoYoGames/GMEXT-Elements>
- Apple IAP: <https://github.com/YoYoGames/GMEXT-AppleIAP>
- Google Play Billing: <https://github.com/YoYoGames/GMEXT-GooglePlayBilling>
- GX.games: <https://github.com/YoYoGames/GMEXT-GX.games>
- Reddit: <https://github.com/YoYoGames/GMEXT-Reddit>

**Reddit / Devvit**
- Guía de build del target: <https://github.com/YoYoGames/GameMakerRedditTemplate/blob/main/docs/HowToBuild.md>
- Plantilla: <https://github.com/YoYoGames/GameMakerRedditTemplate>
- Documentación de Devvit: <https://developers.reddit.com/docs/>

**Presupuesto de build (§4.5)**
- Apple Developer, *Maximum build file sizes* — <https://developer.apple.com/help/app-store-connect/reference/maximum-build-file-sizes/> (06-09-2026) · tamaño máximo de app sin comprimir en iOS/iPadOS: 4 GB desde iOS 9.0
- Google Play, *App size limits* (soporte) — <https://support.google.com/googleplay/android-developer/answer/9859372> (06-09-2026) · módulo base 500 MB; aviso al usuario con datos móviles por encima de 200 MB; APK heredado limitado a 100 MB

**Comunidad**
- Foro oficial: <https://forum.gamemaker.io/>
- Hilo sobre el problema de refresco en Devvit: <https://forum.gamemaker.io/index.php?threads/reddit-playtesting-not-updating.122411/>
- Hilo sobre portar a Switch 2 (y el NDA): <https://forum.gamemaker.io/index.php?threads/what-do-i-need-to-know-about-porting-to-switch-2.120064/>
