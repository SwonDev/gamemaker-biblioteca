# 05 · Entregar el juego: firmar, notarizar y subir a las tiendas

> El trámite que viene **después** de compilar. [05 · 02](./02%20-%20Publicar%20y%20exportar.md) ya
> explica cómo `gm-cli package` produce el `.exe`, el `.app`, el `.aab` o el `.ipa`; este documento
> explica qué hacer con ese archivo para que un jugador de verdad pueda instalarlo sin que el
> sistema operativo lo bloquee, y cómo llega a Steam, Google Play y la App Store. No repite el
> ciclo de marketing y lanzamiento (fechas, wishlists, press kit): eso está en
> [13 · 11 §6](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#6--lanzamiento>).
> Tampoco repite `butler`/itch.io, ya resuelto en
> [07 · 08 §2.2](<../07 - Ecosistema/08 - itch.io - jams, assets y juegos.md#22-subir-con-butler-cli--recomendable-para-builds-grandes-e-iterativas>).

---

## 1 · Los principios

### 1.1 Gatekeeper, SmartScreen y la revisión de tienda son la misma lógica

Un ejecutable que nadie conoce es, por defecto, sospechoso. Cada sistema operativo y cada tienda
resuelve esa desconfianza con una combinación de tres mecanismos que no son intercambiables:

| Mecanismo | Qué demuestra | Quién lo hace |
|---|---|---|
| **Firma** (`codesign`, `signtool`, el KeyStore de Android) | «Este binario lo hizo la identidad X y nadie lo ha tocado desde entonces» | Tú, con un certificado o clave privada |
| **Notarización/reputación** (`notarytool` en macOS, SmartScreen en Windows) | «Un sistema automático ya escaneó este binario concreto y no encontró nada malicioso» | Apple o Microsoft, de forma automática |
| **Revisión humana** (Steam, App Store, Google Play) | «Una persona ha mirado el contenido, no solo el binario» | Un revisor de la tienda |

Firmar sin notarizar en macOS **no** evita el bloqueo de Gatekeeper (§2.1). Un certificado de
firma de código nuevo en Windows **no** evita el aviso de SmartScreen (§3.2): son pasos
independientes que se acumulan, no alternativas.

### 1.2 La regla de oro: hay claves que si pierdes, pierdes el juego

Antes de tocar un solo comando, entiende qué pasa si un archivo o una contraseña desaparece.
Tres niveles de gravedad real, de menor a mayor:

| Si pierdes… | Consecuencia | Se recupera |
|---|---|---|
| El certificado **Developer ID** de macOS o el certificado de firma de Windows | No puedes firmar builds nuevas con esa identidad | **Sí** — se revoca y se genera uno nuevo desde la cuenta de desarrollador (§2.2, §3.2) |
| La **upload key** de Android (Play App Signing activado) | No puedes subir la siguiente actualización con esa clave | **Sí** — Google la resetea desde Play Console (§5.4) |
| El **KeyStore** de Android si NO usas Play App Signing, o la **app signing key** en cualquier caso | No puedes volver a actualizar esa app **nunca más**: hay que publicarla como una app nueva, con reseñas y posición a cero | **No** |

El manual oficial de GameMaker lo dice en la propia ventana de creación del KeyStore, con la misma
contundencia: *«ten en cuenta que este archivo será necesario para crear y actualizar todas tus
aplicaciones de Android en el futuro […] si pierdes este archivo **no** podrás actualizar ningún
juego existente que haya sido subido a la tienda»* — verificado en el espejo local del manual,
[`09 - Manual oficial/manual-lts-2026-es/Setting_Up_And_Version_Information/Platform_Preferences/Android.md`](<../09 - Manual oficial/manual-lts-2026-es/Setting_Up_And_Version_Information/Platform_Preferences/Android.md>).
Haz copia de seguridad del `.jks`/`.keystore` **fuera** del proyecto (un gestor de contraseñas o un
almacén cifrado aparte, nunca el repositorio Git) en el momento en que lo generes, no cuando lo
necesites.

⚠️ En ninguno de los ejemplos de este documento va una contraseña, clave o ruta de llavero real:
donde haga falta un secreto aparece un marcador evidente (`<TU_CONTRASEÑA>`, `<TU_APPLE_ID>`) que
se sustituye desde fuera del código — variable de entorno, secreto de CI o el propio llavero del
sistema, nunca escrito en un archivo que se vaya a commitear.

---

## 2 · macOS: firma y notarización

### 2.1 Por qué sin esto el juego no abre

Desde macOS 10.15 (Catalina), **Gatekeeper exige que todo software que no venga de la Mac App
Store esté notarizado** para ejecutarse sin fricción. Un `.app` sin notarizar muestra al jugador
un aviso de que «no se puede verificar el desarrollador» o directamente lo manda a la papelera al
primer intento; el jugador tiene que rescatarlo a mano desde *Preferencias del Sistema → Privacidad
y seguridad*, un paso que la inmensa mayoría abandona ahí. Fuente: documentación oficial de Apple,
*Notarizing macOS software before distribution* —
<https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution>
(consultado 07-09-2026).

### 2.2 Lo que ya firma GameMaker por ti

GameMaker **no te deja sin firma**: al compilar para macOS, el IDE invoca a Xcode para construir
el `.app`/`.pkg`, y esa invocación ya firma el binario con la identidad que configures en
*Game Options → macOS → General*:

- **Identificador de equipo** (*Team Identifier*): tu Team ID de Apple Developer. Anula el que
  tengas puesto en las Preferencias de macOS del IDE si lo defines aquí.
- **Identificador de Firma** (*Signing Identifier*): el nombre exacto del certificado —
  «requerido por Apple para todas las aplicaciones que no son de la tienda de aplicaciones (como
  los juegos de Steam, por ejemplo)», en palabras del propio manual.

Fuente (primaria, local): espejo del manual oficial,
[`09 - Manual oficial/manual-lts-2026-es/Settings/Game_Options/macOS.md`](<../09 - Manual oficial/manual-lts-2026-es/Settings/Game_Options/macOS.md>)
§ General. Con esos dos campos rellenados y un certificado **Developer ID Application** válido
instalado en tu llavero, la exportación ya sale firmada con `codesign` internamente.

**Lo que GameMaker no hace por ti es notarizar.** Esa parte, hoy, es 100 % manual y externa al
IDE — es justo el hueco que reconocía `01 · 16` con una sola frase («hace falta firma y
notarización de Apple») y que este documento cierra.

### 2.3 `codesign`: hardened runtime y entitlements

Aunque GameMaker ya firma el `.app` al compilar, **la notarización de Apple exige el Hardened
Runtime activado** (`--options runtime`), y conviene volver a firmar explícitamente tras cualquier
retoque manual al paquete (añadir un `Info.plist` extra, meter un binario de terceros sin firmar
dentro de `Contents/Resources`, etc.), porque cualquier cambio posterior a la firma original la
invalida:

```bash
# Firma (o re-firma) recursiva con Hardened Runtime y una lista de entitlements
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Tu Nombre o Estudio (EQUIPOID)" \
  --options runtime \
  --entitlements entitlements.plist \
  MiJuego.app
```

`entitlements.plist` mínimo razonable para un juego GameMaker (acceso a red para leaderboards,
Steamworks, anuncios o multijugador; memoria ejecutable sin firmar, que muchos motores —GameMaker
incluido, por su VM/YYC— necesitan para el hardened runtime):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
</dict>
</plist>
```

⚠️ Esta lista de entitlements es una base razonable, no una receta cerrada: si tu build usa
extensiones nativas propias (`.dylib` de terceros, Steamworks, un SDK de anuncios), añade el
entitlement que esa librería documente y vuelve a firmar. Fuente: *Hardened Runtime* —
<https://developer.apple.com/documentation/security/hardened-runtime> (07-09-2026).

Comandos verificados con la documentación oficial citada arriba; flags confirmados: `--deep`,
`--force`, `--verify`, `--verbose`, `--sign`, `--options runtime`, `--entitlements`.

### 2.4 `notarytool submit`

Comprime el `.app` ya firmado en un `.zip` (Apple no acepta el `.app` suelto para este paso) y
envíalo al servicio de notarización:

```bash
# Guarda las credenciales una sola vez en un perfil del llavero (no hace falta repetir la contraseña cada vez)
xcrun notarytool store-credentials "mi-perfil-notarizacion" \
  --apple-id "<TU_APPLE_ID>" \
  --team-id "<TU_TEAM_ID>"
# Pide una contraseña específica de aplicación (no la de tu Apple ID): se genera en appleid.apple.com

# Comprime el .app ya firmado
ditto -c -k --keepParent MiJuego.app MiJuego.zip

# Envía a notarizar y espera el resultado (--wait bloquea hasta terminar)
xcrun notarytool submit MiJuego.zip \
  --keychain-profile "mi-perfil-notarizacion" \
  --wait
```

`--wait` es bloqueante: el comando no vuelve al prompt hasta que Apple resuelve (normalmente unos
minutos). El resultado es `Accepted` o `Invalid`; con `Invalid`, pide el registro detallado:

```bash
xcrun notarytool log <ID_DE_LA_PETICIÓN> --keychain-profile "mi-perfil-notarizacion"
```

Fuentes: *Notarizing macOS software before distribution* y *Customizing the notarization
workflow* — <https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution>
y <https://developer.apple.com/documentation/security/customizing-the-notarization-workflow>
(ambas 07-09-2026). Flags verificados: `store-credentials`, `--apple-id`, `--team-id`, `submit`,
`--keychain-profile`, `--wait`, `log`.

### 2.5 `stapler` y verificar con `spctl`

Notarizar no basta si el jugador va a instalar sin conexión (o Apple tarda en responder la próxima
vez que Gatekeeper consulte online): **grapa el ticket de notarización al propio paquete** para
que la comprobación funcione siempre, incluso sin red.

```bash
# Grapa el ticket de notarización al .app original (no al .zip: al paquete real)
xcrun stapler staple MiJuego.app

# Verifica que Gatekeeper lo acepta, exactamente como lo haría en la máquina de un jugador
spctl --assess --type execute --verbose MiJuego.app
# Salida esperada: "MiJuego.app: accepted" / "source=Notarized Developer ID"
```

Ahora sí: `MiJuego.zip`/`MiJuego.dmg` con el `.app` grapado dentro está listo para distribuirse por
tu web, itch.io o cualquier sitio fuera de la Mac App Store.

### 2.6 Fuera de la Mac App Store: qué implica exactamente

*Game Options → macOS → Empaquetado* trae una casilla **«Build for Mac App Store»**: actívala solo
si vas a vender dentro de la Mac App Store (exige cuenta de desarrollador y certificados de
distribución de la tienda, un circuito de firma distinto al de Developer ID) — y el propio manual
avisa de que, si activas esa casilla, **el soporte de mandos (gamepads) debe estar desactivado**.
Fuente (primaria, local):
[`09 - Manual oficial/manual-lts-2026-es/Settings/Game_Options/macOS.md`](<../09 - Manual oficial/manual-lts-2026-es/Settings/Game_Options/macOS.md>)
§ Embalaje.

Distribuir **fuera** de la Mac App Store (Steam, itch.io, tu propia web) es el camino que cubren
§2.2-§2.5: certificado Developer ID Application, no Mac App Store; firma con Hardened Runtime;
notarización; grapado. Es el camino que usa cualquier juego de Steam en macOS — el propio manual lo
nombra como ejemplo explícito de cuándo hace falta el Identificador de Firma.

---

## 3 · Windows: firma de código y SmartScreen

### 3.1 `signtool sign`

GameMaker **no firma** el `.exe`/instalador de Windows: lo que sale de `gm-cli package --target
windows` está sin firmar, y hay que firmarlo tú aparte con `signtool`, incluido en el Windows SDK.

```bash
signtool sign /f "MiCertificado.pfx" /p "<TU_CONTRASEÑA>" ^
  /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 ^
  MiJuego.exe
```

| Flag | Qué hace |
|---|---|
| `/f` | Ruta al certificado (`.pfx`, con clave privada) |
| `/p` | Contraseña del `.pfx` |
| `/fd` | Algoritmo de resumen del archivo — usa **SHA256**, es el que recomienda Microsoft |
| `/tr` | URL de un servidor de sellado de tiempo RFC 3161 (`/t` es la variante antigua, sin RFC 3161; usa `/tr`) |
| `/td` | Algoritmo de resumen para el sellado de tiempo — también SHA256 |

**El sellado de tiempo no es opcional en la práctica**: sin él, la firma caduca el mismo día que
caduque tu certificado, y todas las copias ya distribuidas empiezan a fallar la verificación. Con
`/tr`, la firma queda fechada por un tercero de confianza y sigue siendo válida después de que el
certificado expire. Fuente: Microsoft Learn, *SignTool* —
<https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool> (07-09-2026), verificado ahí
el listado completo de flags de `sign` y los ejemplos con `/tr`/`/td`.

### 3.2 OV vs EV, y la verdad sobre el aviso de SmartScreen en 2026

Aquí hay una creencia extendida que **ya no es cierta**, y merece la pena decirlo con la fecha de
verificación por delante: durante años, un certificado **EV** (Extended Validation) daba
reputación de SmartScreen inmediata — el primer usuario que descargaba el `.exe` no veía el aviso
«Windows protegió su PC». **Eso cambió.** Microsoft confirma que **los certificados EV ya no
conceden reputación instantánea**: cualquier binario nuevo, firmado con OV o con EV, tiene que
**construir reputación con el volumen real de descargas y ejecuciones** antes de que el aviso deje
de aparecer, y cada actualización del binario (nuevo hash) vuelve a empezar de cero. Fuente
(secundaria, pero corroborada por dos artículos técnicos independientes con cita directa a
comunicaciones de Microsoft): *«EV code signing certificates no longer grant instant SmartScreen
reputation […] must build reputation organically, just like OV-signed apps»* — verificado por
búsqueda cruzada el 07-09-2026 (ToDesktop *Windows Apps PSA*, Microsoft Q&A *How can a small
software publisher build SmartScreen reputation?*). ⚠️ No hay contacto directo ni lista blanca
manual para acelerarlo: la única palanca es distribuir de forma consistente con el mismo
certificado y acumular descargas.

Consecuencia práctica: para un estudio pequeño, **no compensa pagar el sobrecoste de un
certificado EV solo por SmartScreen** — el aviso va a aparecer igual las primeras semanas. Compensa
un certificado **OV** (Organization Validation), más barato, firmado siempre con la misma
identidad para que la reputación se vaya acumulando build tras build.

### 3.3 La alternativa barata: Azure Artifact Signing

Comprar un certificado OV/EV tradicional de una autoridad de certificación (DigiCert, Sectigo,
GlobalSign…) suele costar varios cientos de dólares al año y exige custodiar tú mismo la clave
privada. Microsoft ofrece desde 2026 una alternativa gestionada, **Azure Artifact Signing**
(antes llamado *Azure Trusted Signing*):

| | Certificado OV/EV comprado a una CA | Azure Artifact Signing |
|---|---|---|
| Custodia de la clave privada | Tuya (USB con protección hardware, o el `.pfx`) | De Microsoft, en un HSM certificado FIPS 140-3 nivel 3 — nunca la ves ni la exportas |
| Coste orientativo | Varios cientos de USD/año | **Plan Basic: ~9,99 USD/mes** (5 000 firmas incluidas); **Premium: ~99,99 USD/mes** (100 000 firmas) — ⚠️ cifras de fuentes secundarias cruzadas (Hacker News, foro 4D, devclass.com), la página oficial de precios no cargó el importe en esta sesión: confirma en <https://azure.microsoft.com/en-us/pricing/details/artifact-signing/> antes de presupuestar |
| Elegibilidad | Cualquiera que pase la validación de la CA | Empresas o **autónomos individuales** de EE. UU., Canadá, UE o Reino Unido, con suscripción de Azure de pago (no vale una suscripción gratuita/de prueba) — ya sin exigir 3 años de historial, requisito que sí existía en la fase de vista previa |
| Emite certificados EV | Sí, si lo pagas | **No.** Azure Artifact Signing no emite EV — y no compensa, según §3.2 |
| Integración | `signtool sign /f cert.pfx /p ...` | `signtool sign /dlib AzureCodeSigning.dll /dmdf metadata.json /fd SHA256` (un plugin de firma remota) |

Requiere registrar el proveedor de recursos `Microsoft.CodeSigning`, validar tu identidad (incluye
verificación facial con Microsoft Authenticator / AU10TIX) y crear un *Certificate Profile* de
confianza pública antes de firmar el primer binario. Fuentes: *What is Artifact Signing?* y
*Artifact Signing FAQ* — <https://learn.microsoft.com/en-us/azure/artifact-signing/overview> y
<https://learn.microsoft.com/en-us/azure/artifact-signing/faq> (ambas 07-09-2026; la FAQ confirma
explícitamente «Artifact Signing doesn't issue Extended Validation (EV) certificates» y la
elegibilidad para autónomos sin exigir 3 años de historial).

---

## 4 · Steam: alta de la aplicación, depósitos y subida

### 4.1 Alta de la aplicación (Steam Direct)

Registrar una app nueva en Steamworks exige la **cuota de Steam Direct**: **100 USD** por
aplicación. No es reembolsable, pero **es recuperable**: Valve la descuenta de tu primer pago una
vez que el producto genere al menos **1 000 USD de ingresos brutos ajustados**, y aparece como una
línea aparte en tu liquidación mensual. Fuente: Steamworks, *Steam Direct Fee* —
<https://partner.steamgames.com/doc/gettingstarted/appfee> (07-09-2026), cita textual: *«The
Steam Direct Fee is not refundable, but will be recoupable in the payment made after your product
has at least $1,000.00 Adjusted Gross Revenue»*.

El registro se hace desde el panel de Steamworks (*partner.steamgames.com → Steamworks →
Register a New App*). Una vez pagada la cuota y aprobado el registro obtienes el **AppID**: un
número que vas a usar en todos los comandos de este apartado.

### 4.2 Depots: qué son y cuándo separarlos

Un **depot** es la unidad de contenido de SteamPipe — un paquete de archivos con su propio
identificador (`DepotID`) dentro de tu app. Un depot típico se corresponde con **una plataforma**
(Windows, macOS, Linux) o con contenido opcional (idiomas grandes, DLC). La mayoría de juegos
pequeños hechos con GameMaker necesitan como mucho un depot por plataforma que publiquen; no hace
falta partir nada más hasta que el tamaño o los idiomas lo justifiquen.

### 4.3 `app_build.vdf` y `depot_build.vdf`

Dos archivos de configuración en formato VDF (el formato propio de Valve, parecido a JSON con
sintaxis Valve). `app_build.vdf` describe **la build completa**:

```vdf
"AppBuild"
{
    "AppID" "480"                        // tu AppID real, no el de ejemplo
    "Desc"  "Build automática desde CI"   // texto libre, solo visible en tu panel

    "BuildOutput" "..\output\"           // logs, manifiestos y caché de esta compilación
    "ContentRoot" "..\content\"          // carpeta raíz por defecto (cada depot puede sobrescribirla)

    "SetLive" ""                         // rama a la que promocionar tras compilar (vacío = ninguna)

    "Depots"
    {
        "481" "depot_build_481.vdf"      // DepotID -> su propio archivo de configuración
    }
}
```

Y `depot_build.vdf`, uno por cada depot, describe **qué archivos entran** en ese depot concreto:

```vdf
"DepotBuild"
{
    "DepotID" "481"
    "ContentRoot" "..\content\windows\"  // sobrescribe el ContentRoot del app_build.vdf para este depot

    "FileMapping"
    {
        "LocalPath"  "*"                 // todo lo que haya en ContentRoot (admite comodines * y ?)
        "DepotPath"  "."                 // "." = la raíz del depot
        "recursive"  "1"                 // incluye subcarpetas
    }

    "FileExclusion" "*.pdb"              // excluye símbolos de depuración, por ejemplo
}
```

`ContentRoot` **tiene que apuntar directamente a la carpeta que contiene el `.exe`** (o el `.app`,
o el ejecutable de Linux), no a una carpeta que lo contenga a su vez dentro de otra subcarpeta —
ver el error clásico en §4.7. Fuente: Steamworks, *Uploading Content via Steamworks (SteamPipe)*
— <https://partner.steamgames.com/doc/sdk/uploading> (07-09-2026); campos verificados:
`AppID`, `Desc`, `BuildOutput`, `ContentRoot`, `SetLive`, `Depots`, `DepotID`, `FileMapping`,
`LocalPath`, `DepotPath`, `recursive`, `FileExclusion`.

### 4.4 `steamcmd`: el comando de subida

`steamcmd` es la herramienta de línea de comandos de Valve — se descarga aparte, **fuera de
GameMaker** (`developer.valvesoftware.com/wiki/SteamCMD`). El flujo completo, encadenando el
`package` de GameMaker con la subida:

```bash
# 1. GameMaker ya produjo el build de release (ver 05 · 02 §3.5)
gm-cli compile --target windows --runtime native --config Release --errors-only
gm-cli package --target windows --output ./content/windows/

# 2. Firma el .exe antes de subirlo (§3.1) — Steam no firma nada por ti
signtool sign /f "MiCertificado.pfx" /p "<TU_CONTRASEÑA>" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 ./content/windows/MiJuego.exe

# 3. Sube con steamcmd, apuntando al app_build.vdf de §4.3
steamcmd +login <TU_USUARIO_DE_BUILD> +run_app_build ../scripts/app_build.vdf +quit
```

`steamcmd` pide la contraseña de forma interactiva la primera vez (no la pases en texto plano en
el comando) y, si tu cuenta tiene verificación en dos pasos de Steam Guard, pedirá también el
código. **Usa una cuenta de build dedicada**, no tu cuenta personal, para poder revocarle acceso
sin afectar al resto de tu perfil de Steam. Fuente: mismo documento de §4.3; sintaxis verificada de
`+login`, `+run_app_build`, `+quit`.

### 4.5 Ramas beta y la rama `default`

Una **rama** (*branch*, también llamada *beta* en la jerga de Steam) es una versión concreta de tu
app disponible pública o privadamente. La rama **`default`** es la que reciben los jugadores que
compraron el juego sin tocar nada — «*the version of your game delivered to your customers on
Steam*», en palabras de Valve.

- **Crear una rama de pruebas**: en *App Admin → Builds → Create new app branch*, con un nombre
  sin espacios y, opcionalmente, una **contraseña** — quien no la conozca no puede ni ver que la
  rama existe.
- **Subir a esa rama sin tocar `default`**: pon el nombre de la rama en `SetLive` dentro de
  `app_build.vdf` (§4.3). Así pruebas la build con un grupo reducido antes de que la vea nadie más.
- **Promocionar a `default` es un paso manual**, y así lo quiere Valve a propósito: no puedes
  automatizarlo poniendo `"SetLive" "default"` a la ligera en un `app_build.vdf` de CI sin
  revisión — el flujo previsto es subir a una rama de pruebas, mirarla, y solo entonces ir a
  *Builds*, elegir esa build en el desplegable, **Preview Change** y **Set Build Live Now**. Es la
  misma clase de guardarraíl que ya usa Google Play con sus canales de prueba (§5.7): nada
  llega a producción sin un clic humano de por medio.

Fuente: Steamworks, *Branches* — <https://partner.steamgames.com/doc/store/application/branches>
(07-09-2026); citas verificadas: *«The default branch is the version of your game delivered to
your customers on Steam»* y el flujo de creación de rama con contraseña.

### 4.6 Las imágenes de la ficha

Los tamaños exactos de cápsulas, cabecera y capturas ya están verificados y tabulados en
[13 · 11 §6.2](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#62-los-activos-de-la-página-tamaños-verificados>) —
no se repiten aquí para no desincronizarlos si Valve cambia una cifra.

### 4.7 El error clásico: subir la carpeta equivocada

El fallo más repetido al automatizar la subida a Steam no es de sintaxis del VDF, es de **rutas**:

1. **`ContentRoot` apunta un nivel demasiado alto.** Si tu build queda en
   `./content/windows/MiJuego.exe` pero `ContentRoot` apunta a `./content/` en vez de a
   `./content/windows/`, el depot sube con `MiJuego.exe` metido dentro de una subcarpeta
   `windows/` que Steam no espera — el cliente de Steam busca el ejecutable en la ruta de
   *Installation → General* del panel y no lo encuentra, y el juego «no arranca» aunque la subida
   haya terminado sin errores.
2. **Subir el build de depuración (VM) en vez del de release.** `gm-cli compile --runtime native
   --config Release` (§4.4) es el que corresponde a una build pública; una build de VM sin
   optimizar arranca más lento y expone mensajes de depuración que no deberían llegar a un
   jugador.

⚠️ La estructura exacta de carpetas que produce `gm-cli package --target windows` no se pudo
verificar de extremo a extremo en este equipo (compilar el target Windows en macOS falló por un
componente de Igor ausente, `kernel32.dll.dylib`, no relacionado con el flujo de Steam). **Antes
de fijar `ContentRoot` en un script de CI, comprueba a mano, una vez, cuál es la carpeta que
contiene directamente el `.exe`** en tu build real, y apunta ahí — no lo des por hecho copiando
este ejemplo literalmente.

---

## 5 · Google Play: App Bundle, firma, ficha y pruebas

### 5.1 Por qué el `.aab` sustituyó al APK

El **Android App Bundle** (`.aab`) es, desde agosto de 2021, el formato **obligatorio** para
publicar apps nuevas en Google Play — un APK universal sigue sirviendo para otras tiendas, pero no
para Play. La diferencia de fondo: el `.aab` no es lo que descarga el jugador, es lo que **Google
Play usa para generar** APKs optimizados por dispositivo (arquitectura de CPU, densidad de
pantalla, idioma), de forma que cada usuario baja solo lo que su teléfono necesita, en vez de un
único APK con absolutamente todo (todas las arquitecturas, todas las densidades, todos los
idiomas) empaquetado a la vez. Fuente: Android Developers, *Android App Bundle* —
<https://developer.android.com/guide/app-bundle> (07-09-2026).

### 5.2 Cómo lo genera GameMaker: KeyStore y el diálogo apk/aab

GameMaker exporta **directamente** en cualquiera de los dos formatos: la ventana de *Create
Executable* para Android deja elegir entre `.apk` y `.aab` — «*el archivo `.aab` [es] necesario
para Google Play, mientras que el archivo `.apk` puede utilizarse en otras tiendas*». Fuente
(primaria, local):
[`09 - Manual oficial/manual-lts-2026-es/Introduction/Compiling.md`](<../09 - Manual oficial/manual-lts-2026-es/Introduction/Compiling.md>)
§ Formatos de destino.

La firma del `.aab`/`.apk` sale del **KeyStore** que configuras una sola vez en *Preferencias de
Android* (o lo anulas por proyecto en *Game Options → Android*): nombre del archivo, contraseña,
alias y contraseña del alias — GameMaker genera el `.jks` por ti con el botón **Generar almacén de
claves**, o importa uno que ya tuvieras. Detalle completo, con la advertencia textual sobre
perder el archivo, en §1.2 de este documento y en
[`09 - Manual oficial/manual-lts-2026-es/Setting_Up_And_Version_Information/Platform_Preferences/Android.md`](<../09 - Manual oficial/manual-lts-2026-es/Setting_Up_And_Version_Information/Platform_Preferences/Android.md>).

```bash
# Empaquetado por CLI: el CLI no expone un flag propio para elegir apk/aab (verificado con
# `gm-cli package --help`, 2.3.0: no aparece); en este equipo, con --output test.aab y con
# --output test.apk, el CLI aceptó ambas extensiones sin queja hasta la fase de compilación
# real de Android (que aquí falló antes, por falta del SDK/NDK/JDK — no relacionado con el
# formato de salida). ⚠️ No verificado de extremo a extremo: confírmalo generando ambos formatos
# una vez en tu máquina con el SDK de Android instalado antes de fiarte de este flujo en CI.
gm-cli package --target android --output ./builds/mi-juego.aab
```

### 5.3 Play App Signing: clave de la app vs. clave de subida

Desde que Google lo hizo el flujo por defecto para apps nuevas, hay **dos claves**, no una:

| | Clave de firma de la app (*app signing key*) | Clave de subida (*upload key*) |
|---|---|---|
| Quién la custodia | **Google**, en su infraestructura segura | **Tú** — es el `.jks` que genera GameMaker (§5.2) |
| Para qué sirve | Firma el APK final que de verdad llega al dispositivo del jugador | Firma el `.aab` que subes a Play Console, para que Google verifique que eres tú |
| Si la pierdes | No la pierdes tú: la tiene Google. Con Play App Signing activo, Google puede rotarla | La app **no** queda bloqueada: se resetea (ver §5.4) |

Play App Signing se activa la primera vez que subes un `.aab` firmado con tu clave de subida —
Google conserva entonces la clave de firma real y solo te pide, de ahí en adelante, la clave de
subida. Fuente: Google Play Console Help, *About app signing* —
<https://support.google.com/googleplay/android-developer/answer/9842756> (07-09-2026).

### 5.4 Qué se pierde si pierdes cada clave

Si pierdes o sospechas que se ha filtrado la **upload key**: genera una nueva en Android Studio o
con `keytool`, exporta el certificado en formato PEM y **pide el reseteo directamente en Play
Console** — no te quedas fuera de tu propia app. La documentación oficial de Google lo dice sin
rodeos: *«If you lose your upload key or suspect it's been compromised, you are not locked out of
your app»*. Fuente: misma página de §5.3.

Lo que **no** tiene vuelta atrás es perder la **app signing key** cuando gestionas la firma tú
mismo sin Play App Signing (una configuración cada vez más residual, pero que algunos proyectos
antiguos migrados a GameMaker todavía arrastran): sin esa clave no puedes firmar ninguna
actualización futura de esa app con la identidad que Google ya tiene registrada, y la única salida
es publicar el juego como una **app nueva**, perdiendo reseñas, historial de instalaciones y
posición en el buscador. Es exactamente el caso que tabula §1.2.

### 5.5 Ficha de privacidad: *Data safety*

La sección **Data safety** de Play Console (*App content → Data safety*) es obligatoria antes de
publicar o actualizar cualquier app (con la única excepción de apps de sistema y las que están
únicamente en pruebas internas): declaras **qué datos recoge tu app y sus SDK de terceros**
(anuncios, analítica), **si los comparte** con otros y **cómo los protege** (cifrado en tránsito,
si el usuario puede pedir que se borren). Fuente: Google Play Console Help, *Data safety* —
<https://support.google.com/googleplay/android-developer/answer/10787469> (07-09-2026).

Para un juego con AdMob o cualquier SDK de mediación de anuncios (ya cubiertos en
[04 · 20 §3](<../04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md#3--anuncios-admob>)),
esto **no es opcional**: el propio SDK recoge identificadores de dispositivo con fines
publicitarios, y eso hay que declararlo aunque tú no toques directamente esos datos en tu código.

### 5.6 Cuestionario de contenido y público objetivo

Dos formularios distintos de *App content*, que se confunden con facilidad:

- **Clasificación de contenido**: el cuestionario **IARC**, ya explicado en detalle (qué es, cómo
  funciona, qué organismos participan) en
  [13 · 11 §9.4](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#94-clasificación-por-edades-pegi-esrb-e-iarc>) —
  no se repite aquí. Lo que añade este documento es **dónde**: se rellena en *Play Console → App
  content → Content rating*, no en un sitio aparte.
- **Público objetivo y contenido** (*Target audience and content*): un formulario **distinto**,
  donde declaras el **rango de edad** al que se dirige tu app. Si ese rango incluye menores de 13
  años, tu app queda sujeta a la **política de Familias de Google Play**, con requisitos
  adicionales de contenido y de anuncios (anuncios no personalizados, entre otros) — la misma
  lógica de fondo que COPPA en EE. UU. Fuente: Google Play Console Help, *Target audience and
  content* — <https://support.google.com/googleplay/android-developer/answer/9859455>
  (07-09-2026); cita verificada: *«Any apps that include children in their target audience must
  comply with Google Play's Families policy requirements»*.

### 5.7 Canales de prueba

Tres niveles, pensados para ampliar el círculo de prueba de forma progresiva:

| Canal | Límite de testers | Cómo se distribuye |
|---|---|---|
| **Interna** (*internal testing*) | Hasta 100 | Lista de correos, disponible en minutos — la vía más rápida para validar un `.aab` real antes de nada |
| **Cerrada** (*closed testing*) | Hasta 200 listas, ~2 000 usuarios por lista | Correos electrónicos o Grupos de Google |
| **Abierta** (*open testing*) | Sin límite práctico (mínimo recomendado 1 000 si lo restringes) | Cualquiera puede unirse encontrando la app en Play |

Empieza siempre por **interna**: es la única que prueba el `.aab` firmado de verdad (no un APK de
depuración) sin exponerlo a nadie fuera de tu equipo. Fuente: Google Play Console Help, *Set up
open, closed, or internal testing* —
<https://support.google.com/googleplay/android-developer/answer/9845334> (07-09-2026).

---

## 6 · App Store: certificados, subida, revisión y privacidad

### 6.1 Del `xarchive` de GameMaker a Xcode

GameMaker no produce un `.ipa` directamente: al compilar para iOS genera un **`xarchive`**, que
**se abre en Xtools (Xcode)** para terminar el proceso — firma de distribución, empaquetado final
y subida. Fuente (primaria, local):
[`09 - Manual oficial/manual-lts-2026-es/Introduction/Compiling.md`](<../09 - Manual oficial/manual-lts-2026-es/Introduction/Compiling.md>)
§ Formatos de destino, entrada «iOS». Hace falta un Mac con Xcode, cuenta de desarrollador de pago
y el Team Identifier configurado en *Game Options → iOS* (ya documentado, con el resto del flujo
de dispositivo, en
[04 · 28 §9.2](<../04 - Recetas por género/28 - Juegos para móvil (táctil).md#92-cómo-se-llega-al-dispositivo>) —
no se repite aquí).

### 6.2 Certificados y perfiles de aprovisionamiento

Para subir a App Store Connect necesitas, dentro de tu cuenta de Apple Developer:

- Un certificado **Apple Distribution** (distinto del Developer ID de macOS de §2.2: este es
  específico para distribuir a través de las tiendas de Apple).
  <https://developer.apple.com/documentation/xcode/certificates>
- Un **perfil de aprovisionamiento** (*provisioning profile*) de tipo *App Store*, que vincula tu
  App ID, el certificado de distribución y (si tu juego usa alguna) las *capabilities* (Game
  Center, notificaciones push).

Xcode puede gestionar ambos automáticamente (*Automatically manage signing*) si tienes acceso de
administrador o de gestión de certificados en el equipo de desarrollador; para CI, se generan a
mano una vez y se guardan como secretos (§8.2 usa el mismo patrón de llavero temporal que macOS,
porque el mecanismo de firma es el mismo sistema de Keychain).

### 6.3 Subir el build: Organizer, Transporter o `altool`

Tres caminos válidos, de más manual a más automatizable:

1. **Xcode Organizer**: abre el `.xcarchive`, *Distribute App → App Store Connect → Upload*. El
   camino recomendado si lo haces a mano.
2. **Transporter** (app de macOS, gratuita, en la Mac App Store): arrastra el `.ipa` exportado y
   súbelo sin abrir Xcode — útil si generas el `.ipa` en otra máquina.
3. **`xcrun altool --upload-app`** (línea de comandos, para scripts y CI):

```bash
xcrun altool --upload-app \
  -f MiJuego.ipa \
  -t ios \
  --apiKey <TU_API_KEY_ID> \
  --apiIssuer <TU_ISSUER_ID>
```

⚠️ **Matiz importante que confunde con frecuencia**: Apple retiró `altool` **solo para
notarización** (sustituido por `notarytool`, §2.4) desde noviembre de 2023 — la nota técnica
*TN3147, Migrating to the latest notarization tool*, existe justamente para esa migración.
**`altool` sigue siendo válido para subir builds a App Store Connect**, que es un flujo distinto
al de notarización de macOS. Preferible autenticar con una **clave de API de App Store Connect**
(`--apiKey`/`--apiIssuer`) en vez de usuario y contraseña, porque las claves de API no dependen de
verificación en dos pasos interactiva y son las que de verdad funcionan sin intervención humana en
CI. Fuente: Apple Developer Technical Notes, título verificado —
<https://developer.apple.com/documentation/technotes/tn3147-migrating-to-the-latest-notarization-tool>
(07-09-2026; el contenido íntegro de la nota no cargó en esta sesión — el título y el alcance
—migración del *notarization tool*, no de la subida a la tienda— sí están confirmados) y discusión
técnica corroborada en la comunidad de `fastlane` sobre el alcance exacto de la depreciación
(07-09-2026).

### 6.4 TestFlight

Ya documentado con el flujo completo (invitar testers, builds de prueba, caducidad de 90 días) en
[04 · 28 §9.4](<../04 - Recetas por género/28 - Juegos para móvil (táctil).md#94-distribución-interna-antes-de-publicar>) —
no se repite aquí. Lo único que añade este documento: TestFlight usa la **misma subida** de §6.3,
solo que sin enviarla a revisión pública.

### 6.5 El proceso de revisión y los rechazos típicos

Apple revisa cada envío contra las *App Review Guidelines* — el motivo real de rechazo casi
siempre cae en una de estas categorías, verificadas contra el texto oficial:

| Motivo | Qué exige la guía |
|---|---|
| **Pagos fuera de In-App Purchase** (Guideline 3.1.1) | Cualquier desbloqueo de contenido o funcionalidad dentro del juego **tiene que** pasar por StoreKit/IAP — nada de códigos de licencia externos, QR o criptomonedas como atajo |
| **Metadatos engañosos** (Guideline 2.3.1) | La ficha no puede prometer una función que el juego no tiene, ni ocultar una que sí tiene |
| **Build incompleta** (Guideline 2.1) | *Crashes*, texto de relleno (*placeholder*), URLs rotas o servicios de backend sin activar en el momento de la revisión — probar en dispositivo real antes de enviar, no solo en el simulador |
| **Cajas de botín sin probabilidades** (Guideline 3.1.1) | Si el juego tiene *loot boxes*, hay que **revelar las probabilidades de cada tipo de objeto antes de la compra** |

Fuente: *App Store Review Guidelines* — <https://developer.apple.com/app-store/review/guidelines/>
(07-09-2026). Apple no publica un tiempo fijo de revisión en la propia guía; en la práctica suele
resolverse en uno o dos días si la build está completa, y se alarga si hay idas y venidas por un
rechazo — así que **enviar con margen** respecto a la fecha de lanzamiento (ver el calendario de
§6 de [13 · 11](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md>))
no es opcional.

### 6.6 App Tracking Transparency y la etiqueta de privacidad

Dos piezas relacionadas, con las que un juego con anuncios se topa siempre:

- **App Tracking Transparency (ATT)**: si tu juego (o el SDK de anuncios que integres) accede al
  **IDFA** para publicidad dirigida entre apps, tienes que pedir permiso explícito con
  `ATTrackingManager.requestTrackingAuthorization()` **antes** de leerlo. Si el jugador lo
  rechaza, el IDFA vuelve como una cadena de ceros y no hay forma de sortearlo — hay que diseñar el
  juego para funcionar igual sin publicidad personalizada. Añade `NSUserTrackingUsageDescription`
  al `Info.plist` con el motivo. Fuente: *App Tracking Transparency* —
  <https://developer.apple.com/documentation/apptrackingtransparency> (07-09-2026).
- **Ficha de privacidad** (*App Privacy*, la llamada *nutrition label*): un formulario en App
  Store Connect donde declaras, por categoría (contacto, ubicación, identificadores, diagnósticos,
  etc.), qué datos recoge tu app —y los SDK que integra— y si cada dato está **vinculado a la
  identidad** del usuario o se usa para **rastrearlo** entre apps de terceros (*tracking*, en el
  sentido estricto que define Apple, distinto de recoger datos solo para tu propio uso). Fuente:
  *App Privacy Details on the App Store* — <https://developer.apple.com/app-store/app-privacy-details/>
  (07-09-2026).

Para un juego GameMaker con AdMob o Steamworks Cloud, la pieza técnica correspondiente
(`GMEXT-AppTrackingTransparency`) ya está catalogada, con la advertencia de que no está confirmado
el nombre exacto de su función de llamada en esta biblioteca, en
[07 · 03 §3.5 — Móvil (Android / iOS)](<../07 - Ecosistema/03 - Extensiones oficiales y de terceros.md#35-móvil-android--ios>) —
no se repite aquí.

---

## 7 · itch.io

Sin hueco que cerrar: el flujo completo —export manual, `butler push`, canales por plataforma,
buenas prácticas de versión— ya está resuelto con detalle en
[07 · 08 §2](<../07 - Ecosistema/08 - itch.io - jams, assets y juegos.md#2-cómo-publicar-un-juego-de-gamemaker-en-itchio>)
y ampliado en
[12 · 06](<../12 - Utilidades e integraciones/06 - itch.io - assets, herramientas y jams.md>).
itch.io no exige firma de código, notarización ni revisión previa: es el camino más corto de todo
este documento, precisamente porque no tiene ninguno de los trámites de los apartados anteriores.

---

## 8 · Automatizar esto en CI

### 8.1 Lo que ya se automatiza sin nada especial

`gm-cli init --actions` ya genera los workflows de compilación y empaquetado, documentados en
[05 · 02 §5](./02%20-%20Publicar%20y%20exportar.md#5-automatizar-la-publicación-ci). A partir de
ahí, **firmar** (macOS, Windows) y **subir** (Steam, Google Play, App Store) se añaden como pasos
extra en ese mismo workflow — con matices distintos según la tienda.

| Se puede automatizar sin más que un secreto | Exige una máquina con licencia y llavero propios |
|---|---|
| Firmar Windows con Azure Artifact Signing (§8.3) | Compilar iOS/macOS (necesitan un runner **macOS** real con Xcode — GitHub Actions lo ofrece como `macos-latest`, pero sigue siendo una máquina con su propio coste) |
| Firmar y notarizar macOS con un runner `macos-latest` de GitHub Actions (§8.2) | Subir a Steam desde una cuenta con Steam Guard activo la primera vez (requiere aprobar el nuevo dispositivo a mano una vez; después, con el `sentry file` guardado como secreto, sí es automatizable) |
| Subir a Google Play por la API (§8.4) | Promocionar una build a la rama `default` de Steam (§4.5 — deliberadamente manual) |
| Subir a App Store Connect con una clave de API (§6.3) | Pasar la revisión humana de Steam o de la App Store (ninguna herramienta te la salta) |

### 8.2 macOS: llavero temporal en el runner

El patrón estándar en GitHub Actions para firmar sin dejar el certificado suelto en disco entre
ejecuciones: crear un llavero temporal solo para ese job, importar el `.p12` desde un secreto en
Base64, y borrar el llavero al terminar.

```bash
# Secretos del repositorio: BUILD_CERTIFICATE_BASE64, P12_PASSWORD, KEYCHAIN_PASSWORD
KEYCHAIN_PATH="$RUNNER_TEMP/firma-macos.keychain-db"

echo -n "$BUILD_CERTIFICATE_BASE64" | base64 --decode -o certificado.p12

security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"
security set-keychain-settings -lut 21600 "$KEYCHAIN_PATH"
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"

security import certificado.p12 -P "$P12_PASSWORD" -A -t cert -f pkcs12 -k "$KEYCHAIN_PATH"
security set-key-partition-list -S apple-tool:,apple: -k "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"
security list-keychain -d user -s "$KEYCHAIN_PATH"

# A partir de aquí, codesign (§2.3) y notarytool (§2.4) encuentran el certificado sin más
```

Fuente: GitHub Docs, *Installing an Apple certificate on macOS runners for Xcode development* —
<https://docs.github.com/en/actions/use-cases-and-examples/deploying/installing-an-apple-certificate-on-macos-runners-for-xcode-development>
(07-09-2026); comandos verificados: `create-keychain`, `set-keychain-settings -lut`,
`unlock-keychain`, `import ... -A -t cert -f pkcs12`, `set-key-partition-list -S apple-tool:,apple:`,
`list-keychain -d user -s`.

### 8.3 Windows: firmar en el runner

Con **Azure Artifact Signing** (§3.3), el paso de CI no maneja ningún `.pfx`: se autentica contra
Azure con un *service principal* y firma en remoto.

```yaml
# Secretos: AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_ENDPOINT,
# AZURE_CODE_SIGNING_NAME, AZURE_CERT_PROFILE_NAME
- name: Firmar el ejecutable de Windows
  uses: azure/artifact-signing-action@v1
  with:
    endpoint: ${{ secrets.AZURE_ENDPOINT }}
    signing-account-name: ${{ secrets.AZURE_CODE_SIGNING_NAME }}
    certificate-profile-name: ${{ secrets.AZURE_CERT_PROFILE_NAME }}
    azure-tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    azure-client-id: ${{ secrets.AZURE_CLIENT_ID }}
    azure-client-secret: ${{ secrets.AZURE_CLIENT_SECRET }}
    files-folder: ./builds/windows
    files-folder-filter: exe
```

Con un `.pfx` tradicional, el equivalente es guardar el certificado en Base64 como secreto,
decodificarlo en el runner y llamar a `signtool sign /f` (§3.1) apuntando a ese archivo temporal —
el mismo patrón que §8.2, sin llavero porque Windows no lo necesita. ⚠️ La *action* concreta del
YAML (`azure/artifact-signing-action@v1`) sale de una fuente secundaria (guía práctica de
melatonin.dev, 07-09-2026): verifica el nombre exacto y la versión publicada en el Marketplace de
GitHub Actions antes de fijarla en un pipeline real.

### 8.4 Google Play: subida por API

Google Play expone la **Play Developer API**, que acepta subir un `.aab` firmado y publicarlo
directamente en un canal (interno, cerrado, abierto o producción) sin pasar por la interfaz web —
es lo que usan herramientas como `fastlane supply`. Requiere una cuenta de servicio con permisos
en Play Console y su clave JSON como secreto de CI. GameMaker no trae ninguna extensión propia
para esto: es tooling externo a la Google Play API, no del motor. ⚠️ No se ha verificado en esta
sesión el flujo paso a paso de `fastlane supply` ni de la API REST directa: si lo necesitas,
contrasta contra la documentación oficial de Google (*Play Developer API*) antes de escribir el
paso de CI.

### 8.5 Lo que exige una máquina con licencia (Steam, App Store)

Dos límites reales que ninguna receta de YAML sortea:

- **Steam** pide, la primera vez que `steamcmd` inicia sesión desde una máquina nueva, aprobar
  ese dispositivo (Steam Guard por email o por app). Una vez aprobado, `steamcmd` guarda un
  *sentry file* que sí puede persistirse como secreto de CI (o en la caché del runner) para que
  las siguientes ejecuciones no vuelvan a pedirlo — pero ese primer paso es manual, con nombre y
  apellidos de quien lo aprueba.
- **App Store y macOS/iOS en general** exigen una **cuenta de Apple Developer de pago** vinculada
  a una entidad concreta (persona o empresa), y compilar iOS o macOS de verdad necesita un runner
  **macOS** — no hay forma de compilar esos targets en un runner Linux barato. El coste de
  licencia y de máquina no desaparece por automatizar el resto del pipeline.

---

## 9 · Checklist

- [ ] **macOS**: `.app` firmado con `codesign --options runtime` + entitlements, notarizado con
      `notarytool submit --wait` → `Accepted`, y grapado con `stapler staple`. Verificado con
      `spctl --assess --type execute`.
- [ ] **Windows**: `.exe`/instalador firmado con `signtool sign /fd SHA256 /tr <servidor> /td
      SHA256`, con la misma identidad de certificado que las builds anteriores (para no reiniciar
      la reputación de SmartScreen).
- [ ] **Steam**: AppID registrado y cuota pagada; `app_build.vdf`/`depot_build.vdf` con
      `ContentRoot` apuntando **directamente** a la carpeta del ejecutable; build probada en una
      rama beta antes de promocionarla a `default`.
- [ ] **Google Play**: `.aab` (no `.apk`) firmado con el KeyStore de GameMaker; copia de seguridad
      del `.jks` guardada fuera del repositorio; *Data safety*, clasificación de contenido y
      público objetivo rellenados en Play Console; probado primero en el canal interno.
- [ ] **App Store**: certificado de distribución y perfil de aprovisionamiento vigentes; ficha de
      privacidad y, si aplica, el aviso de ATT completados; build probada de verdad en dispositivo
      (no solo simulador) antes de enviar a revisión.
- [ ] **Secretos**: ningún certificado, contraseña ni clave de API vive en el repositorio ni en un
      archivo commiteado — todos como secretos de CI o en el llavero/gestor de secretos del
      sistema.

---

## 10 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Cómo evitarlo |
|---|---|---|
| «El desarrollador no se puede verificar» en macOS pese a estar firmado | Se firmó pero no se notarizó, o se notarizó pero no se grapó el ticket (§2.1, §2.4, §2.5) | Los tres pasos son obligatorios y en ese orden: firma → notariza → grapa |
| SmartScreen sigue avisando con un certificado EV recién comprado | Creencia desfasada: los EV ya no dan reputación instantánea (§3.2) | No pagues de más por EV solo por esto; firma siempre con la misma identidad y deja que la reputación se acumule |
| El juego «no arranca» en Steam tras una subida sin errores | `ContentRoot` apuntaba a la carpeta equivocada (§4.7) | Verifica a mano, una vez, la ruta real del `.exe` en tu build antes de fijarla en un script |
| Una actualización de Android queda bloqueada para siempre | Se perdió el KeyStore y no se usaba Play App Signing (§5.4) | Activa Play App Signing desde la primera subida, y haz copia de seguridad del `.jks` de todas formas |
| La build de Steam sube a `default` sin querer desde CI | Se puso el nombre de la rama pública en `SetLive` de un `app_build.vdf` automatizado (§4.5) | Sube siempre a una rama de pruebas desde CI; promociona a `default` a mano, desde App Admin |
| Rechazo de App Store por «metadatos engañosos» | La ficha promete una función que el build enviado no tiene todavía | No escribas la ficha de tienda antes de que la build que la acompaña la cumpla de verdad |
| El juego se rechaza por un `crash` que «en mi Mac no pasaba» | Se probó solo en el simulador de Xcode, no en dispositivo físico (§6.5) | Prueba en un iPhone/iPad real antes de enviar a revisión, con la build de release, no la de depuración |

---

## Ver también

- [05 · 02 — Publicar y exportar](./02%20-%20Publicar%20y%20exportar.md) — cómo se compilan y empaquetan los builds que este documento firma y sube
- [13 · 11 §6 — Lanzamiento](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#6--lanzamiento>) — el calendario de marketing y el día 1, con este documento como su paso técnico
- [13 · 11 §9 — Legal y administrativo mínimo](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#9--legal-y-administrativo-mínimo>) — licencias, privacidad, clasificación por edades e impuestos de las tiendas
- [07 · 08 — itch.io: jams, assets y juegos](<../07 - Ecosistema/08 - itch.io - jams, assets y juegos.md>) · [12 · 06 — itch.io: assets, herramientas y jams](<../12 - Utilidades e integraciones/06 - itch.io - assets, herramientas y jams.md>) — el flujo con `butler`, no repetido aquí
- [04 · 20 — Servicios de plataforma](<../04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md>) — la integración GML de Steamworks, AdMob e IAP; este documento cubre el trámite de tienda, no el código
- [04 · 28 — Juegos para móvil (táctil) §9](<../04 - Recetas por género/28 - Juegos para móvil (táctil).md#9--probar-de-verdad>) — cómo se llega al dispositivo, TestFlight y los requisitos de SDK vigentes por tienda
- [07 · 13 — GM CLI](<../07 - Ecosistema/13 - GM CLI - la línea de comandos.md>) — `compile`, `package` y los workflows de GitHub Actions que este documento extiende con firma y subida
- [01 · 16 — Exportar y publicar](<../01 - Fundamentos/16 - Exportar y publicar.md>) — la tabla de salidas por plataforma, ahora con el trámite completo de firma/notarización enlazado desde aquí

---

## Fuentes

Todas consultadas el **7 de septiembre de 2026**, salvo que se indique otra fecha junto a la cita.

**Steamworks (documentación oficial para socios)**
- Steam Direct Fee — <https://partner.steamgames.com/doc/gettingstarted/appfee> · cuota de 100 USD, no reembolsable pero recuperable tras 1 000 USD de ingresos brutos ajustados
- Uploading Content via Steamworks (SteamPipe) — <https://partner.steamgames.com/doc/sdk/uploading> · estructura de `app_build.vdf`/`depot_build.vdf`, sintaxis de `steamcmd +run_app_build`
- Branches — <https://partner.steamgames.com/doc/store/application/branches> · rama `default`, creación de ramas beta con contraseña, promoción manual con «Set Build Live Now»
- Store assets (tamaños de cápsulas y capturas) — ya citado y tabulado en `13 - Diseño y producción de videojuegos/11` §6.2, no se repite aquí

**Apple Developer (documentación oficial)**
- Notarizing macOS software before distribution — <https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution>
- Hardened Runtime — <https://developer.apple.com/documentation/security/hardened-runtime>
- Customizing the notarization workflow — <https://developer.apple.com/documentation/security/customizing-the-notarization-workflow>
- Certificates — <https://developer.apple.com/documentation/xcode/certificates>
- App Store Review Guidelines — <https://developer.apple.com/app-store/review/guidelines/>
- App Privacy Details on the App Store — <https://developer.apple.com/app-store/app-privacy-details/>
- App Tracking Transparency — <https://developer.apple.com/documentation/apptrackingtransparency>
- TN3147, Migrating to the latest notarization tool — <https://developer.apple.com/documentation/technotes/tn3147-migrating-to-the-latest-notarization-tool> · título y alcance confirmados; contenido íntegro no accesible en esta sesión

**Microsoft Learn / Azure (documentación oficial)**
- SignTool - Win32 apps — <https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool> · flags completos de `sign`, `/fd`, `/tr`, `/td`
- What is Artifact Signing? — <https://learn.microsoft.com/en-us/azure/artifact-signing/overview>
- Artifact Signing FAQ — <https://learn.microsoft.com/en-us/azure/artifact-signing/faq> · confirma que no emite certificados EV, y la elegibilidad de autónomos sin el histórico de 3 años de la vista previa
- Azure Artifact Signing, pricing — <https://azure.microsoft.com/en-us/pricing/details/artifact-signing/> · ⚠️ el importe exacto no cargó en esta sesión (contenido dinámico); la cifra citada en §3.3 procede de fuentes secundarias cruzadas, no de esta página directamente

**Reputación de SmartScreen (fuentes secundarias cruzadas, 07-09-2026)**
- ToDesktop Blog, *Windows Apps PSA: EV Certs do not grant immediate reputation anymore* — <https://www.todesktop.com/blog/posts/windows-apps-psa-ev-certs-do-not-grant-immediate-reputation-anymore>
- Microsoft Q&A, *How can a small software publisher build SmartScreen reputation?* — <https://learn.microsoft.com/en-au/answers/questions/5857071/how-can-a-small-software-publisher-build-smartscre>

**Google Play Console Help (documentación oficial)**
- Android App Bundle — <https://developer.android.com/guide/app-bundle>
- About app signing (Play App Signing, clave de subida vs. clave de la app) — <https://support.google.com/googleplay/android-developer/answer/9842756>
- Data safety — <https://support.google.com/googleplay/android-developer/answer/10787469>
- Set up open, closed, or internal testing — <https://support.google.com/googleplay/android-developer/answer/9845334>
- Target audience and content — <https://support.google.com/googleplay/android-developer/answer/9859455>

**GitHub Docs (documentación oficial)**
- Installing an Apple certificate on macOS runners for Xcode development — <https://docs.github.com/en/actions/use-cases-and-examples/deploying/installing-an-apple-certificate-on-macos-runners-for-xcode-development>

**Manual oficial de GameMaker (espejo local, fuente primaria según `AGENTS.md` §1.bis)**
- `09 - Manual oficial/manual-lts-2026-es/Setting_Up_And_Version_Information/Platform_Preferences/Android.md` — creación del KeyStore, advertencia sobre perder el archivo
- `09 - Manual oficial/manual-lts-2026-es/Settings/Game_Options/macOS.md` — Team Identifier, Signing Identifier, «Build for Mac App Store»
- `09 - Manual oficial/manual-lts-2026-es/Settings/Game_Options/iOS.md` — Team Identifier de iOS
- `09 - Manual oficial/manual-lts-2026-es/Introduction/Compiling.md` — formatos de salida por plataforma (`.aab`/`.apk`, `.app`/`.pkg`, `xarchive`)

**Verificado en local (07-09-2026)**
- `gm-cli package --help` (2.3.0): no expone un flag propio para elegir `.apk`/`.aab` en Android — se controla por la extensión de `--output` o por las Game Options del proyecto
- `gm-cli resourcetool eval "options info platform=android"` sobre un proyecto de prueba (`Space Rocks`, `--toolchain GMS2@2026.0.0.23`): `No licensed options for platform 'android'` — misma limitación de licencia ya documentada en `13 - Diseño y producción de videojuegos/11` §4.3 para `windows`
- `gm-cli package --target android --output ./test.aab` y `--output ./test.apk` sobre el mismo proyecto: ambas extensiones aceptadas sin queja hasta el punto en que el CLI exige el argumento `uf`/`local_settings.json` del toolchain de Android (ausente en este equipo) — no se pudo verificar el resultado final del empaquetado
- `gm-cli package --target windows --runtime vm --output ./steam-windows.zip` sobre un proyecto de prueba: falló por `System.DllNotFoundException: kernel32.dll.dylib` (componente de compatibilidad de Igor ausente en este Mac) — no se pudo verificar la estructura interna real del `.zip` de Windows citada en §4.7
