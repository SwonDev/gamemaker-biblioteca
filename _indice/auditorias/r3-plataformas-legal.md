# Auditoría r3 · Plataformas, publicación, monetización y legal

> 2026-09-06 · 81 temas evaluados · 51 cubiertos · 14 parciales · 16 faltan

## Resumen ejecutivo

El núcleo técnico de este dominio es excepcional: `05 - Referencia/02` (exportar) y
`13 - Diseño y producción de videojuegos/11` y `/20` (producción, lanzamiento, modelo de negocio)
están al nivel de un consultor senior — con citas primarias fechadas, vacíos declarados con
honestidad y hasta código GML para auditar patrones oscuros en el propio catálogo de tienda. Lo
que falta no es teoría de diseño de negocio (eso está resuelto), sino el **trámite concreto de
cada tienda que no es Steam**: nadie en la biblioteca explica cómo se firma un `.aab` para Google
Play, cómo se notariza un `.app` de macOS, ni qué exige la App Store en su ficha de privacidad. El
segundo hueco, más grave por ser transversal, es **legal de terceros**: no hay una sola línea
sobre marcas registradas, *fan games* o parodia — un agente que reciba «hazme un homenaje a X»
no tiene ninguna barrera doctrinal en esta biblioteca que se lo señale.

## Tabla tema por tema

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| **A · Exportaciones** | | | | |
| 1 | Windows (instalador, ARM64) | ✅ | `05-02` §1.2, §3.9, §4.4 | — |
| 2 | macOS export y notarización | 🟡 | `01-16` líneas 97-105 (tabla de salidas); `05-02` no la trata | Solo dice «hace falta firma y notarización de Apple» en una fila de tabla. Cero proceso: Developer ID, `codesign`, `notarytool`, *stapling*, qué falla si no se hace (Gatekeeper bloquea el `.app`) |
| 3 | Linux (Ubuntu, ARM64, AppImage/deb) | ✅ | `05-02` §1.2; `01-16` | — |
| 4 | HTML5 y sus límites reales | ✅ | `04-17` §3 «Lo que NO puedes hacer en web» | — |
| 5 | Android: SDK/NDK, Target/Min/Build SDK | ✅ | `05-02` §3.7; `04-28` §9.3 | — |
| 6 | Android: firma de la app (keystore, Play App Signing) | 🔴 | — | Ningún documento menciona `keystore`, clave de subida vs clave de firma de la app, ni qué pasa si se pierde |
| 7 | Google Play: App Bundle (`.aab`) | 🔴 | — | `buscar.py --todo "AAB"` no aparece en ningún doc de plataformas/legal; ni una línea sobre por qué el AAB sustituyó al APK ni cómo se genera desde GameMaker |
| 8 | iOS: Xcode, cuenta de desarrollador, Team Identifier | ✅ | `04-28` §9.2 | — |
| 9 | iOS: TestFlight | ✅ | `04-28` §9.4 | — |
| 10 | App Store: proceso de revisión y motivos de rechazo | 🔴 | — | Cero contenido sobre *App Review Guidelines*, tiempos de revisión, apelación de un rechazo |
| 11 | App Store: ficha de privacidad (*App Privacy* / nutrition labels) | 🔴 | — | No aparece «privacy label» ni «nutrition» en ningún doc |
| 12 | ATT (App Tracking Transparency) e IDFA | 🟡 | `07-03` §3.5 (cataloga `GMEXT-AppTrackingTransparency` como «requisito para que AdMob funcione bien en iOS») | Es una fila de catálogo, no una receta: falta cuándo pedirlo, qué pasa si el usuario lo rechaza, y verificar el nombre real de la función de la extensión (no confirmado en esta sesión: el `.yy` de la extensión no está en el espejo local, solo docs/README) |
| 13 | Opera GX (navegador, Game Strip, Live Wallpaper) | ✅ | `05-02` §3.2 | — |
| 14 | GX.games (CLI, metadatos, publish) | ✅ | `05-02` §3.1 | — |
| 15 | Consolas: requisitos generales bajo NDA | ✅ | `05-02` §3.8, §3.8 bis | — |
| 16 | Nintendo Switch 2 | ✅ | `05-02` §3.8 | — |
| 17 | Reddit/Devvit | ✅ | `05-02` §3.3 | — |
| 18 | Windows ARM64 | ✅ | `05-02` §3.9 | — |
| 19 | Steam Deck (compilar y criterios de Verified) | ✅ | `05-02` §3.6 | — |
| 20 | Licencias de GameMaker (Free/Pro/Enterprise) y qué habilitan | ✅ | `05-02` §2; `13-11` §9.1 | — |
| **B · Ciclo de publicación** | | | | |
| 21 | Página de tienda como hito de marketing (*timing*) | ✅ | `13-11` §6.1 | — |
| 22 | Cápsulas y capturas (tamaños exactos) | ✅ | `13-11` §6.2 | — |
| 23 | Tráiler | 🟡 | `13-11` §6.2 («que empiece con gameplay en los 3 primeros segundos») | Una frase, no una estructura (duración, ritmo, dónde poner el logo/fecha) |
| 24 | Demo (duración, corte, congelada) | ✅ | `13-11` §6.6 | — |
| 25 | Steam Next Fest | ✅ | `13-11` §6.4 | — |
| 26 | Wishlist como métrica | ✅ | `13-11` §6.3 | — |
| 27 | Fecha de lanzamiento (cuándo anunciar) | ✅ | `13-11` §6.7 | — |
| 28 | Actualizaciones y parches (numeración, notas) | ✅ | `13-11` §7, §4.3 | — |
| 29 | Parche del día 1 / hotfix | ✅ | `13-11` §6.8 | — |
| **C · Tiendas** | | | | |
| 30 | Steamworks: alta de la app en el panel, cuota | 🔴 | — | No se menciona el proceso de registrar una app nueva en Steamworks ni la cuota (Steam Direct, ~100 USD reembolsable) |
| 31 | Build con `steamcmd`/SteamPipe | 🟡 | `05-02` §3.5 («subir con las herramientas de Steamworks, fuera de GameMaker») | Una línea; sin comando real de `steamcmd`, sin `app_build.vdf` |
| 32 | Depósitos y ramas beta de Steam | 🔴 | — | Cero mención de *depots* ni *beta branches*, pieza central de cualquier flujo real de actualización en Steam |
| 33 | Precios y regiones | ✅ | `13-11` §6.7 | — |
| 34 | Descuentos y su calendario (reglas de Valve) | ✅ | `13-11` §6.7 | — |
| 35 | Sistema de reseñas de Steam (umbrales, cómo se calculan) | 🟡 | `13-11` §6.8 («vigila las reseñas negativas») | No explica el sistema (% positivo, umbrales *Mostly Positive*/*Overwhelmingly Positive*, efecto en el algoritmo de descubrimiento) |
| 36 | Reembolsos (Steam: juego base, DLC, IAP) | ✅ | `13-20` §1.9 | — |
| 37 | La extensión `GMEXT-Steamworks` | ✅ | `05-02` §3.5; `04-20` §1-2, §5 | — |
| 38 | itch.io: páginas, `butler`, *pay-what-you-want* | ✅ | `07-08` §2; `12-06` | — |
| 39 | Google Play: política de contenido y ficha de la tienda | 🔴 | — | No hay nada sobre *Store listing*, la política de contenido de Google Play ni el proceso de alta de la app en Play Console |
| 40 | Google Play: cuestionario de clasificación de contenido / *Data safety* | 🟡 | `13-11` §9.4 cubre IARC en general | IARC está bien explicado como sistema, pero no aparece nunca en el contexto específico de **Play Console** (dónde se rellena, qué es la sección *Data safety* aparte de la clasificación de edad) |
| 41 | Epic Games Store (como canal de distribución) | 🟡 | `12-03` línea 17 solo cataloga `GMEXT-EpicOnlineServices` | Esa extensión es para *servicios* en línea (logros, sesiones), no para publicar en la **tienda** de Epic; no se distingue esa diferencia en ningún sitio |
| 42 | Consolas: proceso de solicitud de acceso de desarrollador | ✅ | `05-02` §1.4, §3.8 | — |
| **D · Monetización** | | | | |
| 43 | Premium vs. F2P (comparativa y encaje) | ✅ | `13-20` §1.2 | — |
| 44 | Precio y psicología (*charm pricing*, anclaje) | 🟡 | `13-11` §6.7 («mirar a los vecinos») | Solo benchmarking por género; nada de psicología de precios (terminaciones en 9, anclaje con precio tachado) |
| 45 | IAP: implementación real en GameMaker | ✅ | `04-20` §4 | — |
| 46 | Anuncios: qué redes funcionan hoy | ✅ | `04-20` §3; `07-03` §3.2 (AdMob, LevelPlay, Opera Ads; ironSource marcado sucesor) | — |
| 47 | Recompensados vs. intersticiales | ✅ | `04-20` §3 | — |
| 48 | Suscripción (modelo de negocio) | ✅ | `13-20` §1.2 | — |
| 49 | DLC y *season pass* | ✅ | `13-20` §1.2, §1.6 (*Pre-Delivered Content*), §2.3 | — |
| 50 | Cosméticos | ✅ | `13-20` §1.3 | — |
| 51 | Cajas de botín y su estado legal por país | ✅ | `13-20` §1.5 | — |
| 52 | Monedas virtuales (economía dual) | ✅ | `13-20` §1.4 | — |
| 53 | Pay-to-win con criterio / patrones oscuros | ✅ | `13-20` §1.3, §1.6 | — |
| 54 | Live ops y retención (KPIs, cuándo NO hacerlo) | ✅ | `13-20` §1.8 | — |
| 55 | Embudo de tienda / KPIs de producto | ✅ | `13-20` §1.9 | — |
| **E · Legal** | | | | |
| 56 | Licencias de assets: CC0, CC-BY y obligaciones | ✅ | `07-09` §1 | — |
| 57 | Fuentes tipográficas y licencia comercial | 🟡 | `13-11` §5 (una frase: «una fuente es software con licencia propia») | Sin desarrollo: SIL OFL, licencia de escritorio vs. *web embedding*, qué falla si se usa una fuente «gratis para uso personal» en un juego comercial |
| 58 | Música con copyright / *samples* | 🟡 | `13-11` §5 (una frase sobre música «de YouTube») | Sin tratar *sample clearance*, bibliotecas de música con licencia por tienda (Epidemic, Artlist) ni el riesgo de *Content ID* en un tráiler de YouTube |
| 59 | Marcas registradas y nombres | 🔴 | — | Cero. Ni una mención de qué implica usar un nombre parecido a una marca registrada existente |
| 60 | Parodia y *fan game* | 🔴 | — | Cero. `buscar.py --todo` y `grep -r` sobre «fan game», «parodia», «homenaje» no devuelven nada en toda la biblioteca |
| 61 | Usar el nombre/imagen de una consola o marca de terceros | 🔴 | — | Relacionado con 59-60: ni una advertencia sobre nombrar «para PlayStation» o usar un logo de consola en material de marketing sin permiso |
| 62 | Licencia de GameMaker y qué permite | ✅ | `05-02` §2; `13-11` §9.1 | — |
| 63 | Código de terceros: MIT vs. GPL y la «contaminación» | 🟡 | `07-09` §1 (tabla: «GPL: ✅ pero contagia») | Una celda de tabla. No explica **qué significa** contagio de copyleft para el código propio (obligación de publicar el tuyo si enlazas GPL), ni cómo distinguirlo de LGPL/MPL |
| 64 | La licencia del propio juego (EULA) | 🔴 | — | No hay plantilla ni explicación de qué debe cubrir un EULA (uso permitido, prohibición de ingeniería inversa, límite de responsabilidad), a diferencia de la política de privacidad que sí tiene plantilla implícita |
| 65 | Política de privacidad obligatoria | ✅ | `13-11` §9.3 | — |
| 66 | GDPR y consentimiento | 🟡 | `13-11` §7 (telemetría con consentimiento); §9.3 (RGPD mencionado de pasada) | Cubre bien el consentimiento de telemetría propia; no cubre bases legales del RGPD, ni el DPA que exige un SDK de terceros (AdMob, Firebase) que procesa datos de jugadores europeos |
| 67 | COPPA y menores (EE. UU.) | 🔴 | — | No aparece en ningún documento. Distinto de PEGI: es una ley de EE. UU. sobre recogida de datos de menores de 13 años, relevante en cuanto el juego tiene anuncios o cuentas |
| 68 | Clasificación por edades: PEGI, ESRB, IARC | ✅ | `13-11` §9.4; `13-20` §1.5 | — |
| 69 | Accesibilidad legal en algunos países | ✅ | `04-27` §6 bis (European Accessibility Act, con la comprobación explícita de que el videojuego **no** está en su ámbito) | — |
| 70 | Impuestos y retenciones en tiendas (W-8BEN, TIN) | ✅ | `13-11` §9.5 | — |
| 71 | Empresa o autónomo | ✅ (fuera de alcance, declarado) | `13-11` §9.5, §12.1 | Deliberadamente no lo resuelve por depender de la jurisdicción — correcto, no es un hueco |
| 72 | Contratos con publisher / *milestones* de financiación | 🔴 | — | `13-11` §12 cubre contratado/colaborador/socio, pero no la figura de un **publisher** que financia por hitos: anticipo recuperable, marketing comprometido, derechos de plataforma |
| 73 | *Work for hire* explícito | 🟡 | `13-11` §12.5 (cesión de derechos, art. 43/51 LPI) | El concepto de cesión está resuelto con rigor legal; el término «work for hire» y su equivalente en otras jurisdicciones (EE. UU.: cesión automática real bajo ciertas condiciones, a diferencia de España) no se nombra |
| 74 | Acuerdos entre socios y reparto (*revenue share*) | ✅ | `13-11` §12.1 | — |
| 75 | Cesión de derechos de encargos (IP assignment) | ✅ | `13-11` §12.5 | — |
| **F · Comunidad y prensa** | | | | |
| 76 | Kit de prensa | ✅ | `13-11` §6.6, §8.4 | — |
| 77 | Contactar con medios y creadores (claves, embargo) | ✅ | `13-11` §6.6 | — |
| 78 | Discord de la comunidad **del propio juego** | 🔴 | — | `07-10` cataloga dónde pedir ayuda **sobre GameMaker**, no cómo montar/estructurar el servidor de Discord de tu propio juego (canales, roles, bots de moderación) |
| 79 | Moderación de una comunidad propia | 🔴 | — | Cero |
| 80 | Recoger opiniones de jugadores (más allá de telemetría) | 🟡 | `13-11` §6.4 (formulario de opinión en Next Fest); `13-11` §7 (telemetría con consentimiento) | Cubre dos casos puntuales; falta metodología general de playtesting externo/beta cerrada con jugadores reales (a diferencia de `13-01` §7.3 que sí cubre cuántos testers internos hacen falta para usabilidad) |
| 81 | Gestionar una crisis (reseña bomb, bug viral, controversia) | 🔴 | — | Cero. Ni una mención de cómo responder a una oleada de reseñas negativas coordinada, un bug viral en redes o una acusación pública |

## Huecos por prioridad

### 🔴 Graves

1. **Marcas registradas, *fan game* y parodia (temas 59-61).** Es el hueco más peligroso porque
   es *invisible* hasta que un usuario pide «un juego inspirado en X» o «un homenaje a la saga Y»:
   sin esta doctrina, un agente no tiene ninguna señal de alarma en la biblioteca y puede generar
   nombres, logos o mecánicas que pisan una marca registrada sin que nadie lo avise.
2. **Firma y publicación real en Google Play y App Store (temas 6, 7, 10, 11, 39, 40).** La
   biblioteca sabe programar la IAP y los anuncios, pero no sabe **subir la app a la tienda**: no
   hay keystore, no hay AAB, no hay ficha de privacidad de Apple ni política de contenido de
   Google. Es el equivalente móvil de lo que `05-02` ya resuelve tan bien para Steam/GX.games.
3. **macOS: notarización (tema 2).** Sin ella, cualquier `.app` que se distribuya fuera de la Mac
   App Store lo bloquea Gatekeeper al primer intento del jugador, y hoy la biblioteca lo resuelve
   con una sola frase.
4. **Steam: alta de la app, depósitos y ramas beta (temas 30, 32).** Todo el resto del ciclo de
   Steam (página, precio, reseñas, reembolsos) está resuelto con detalle; el paso intermedio —
   cómo se sube de verdad una actualización con `steamcmd` y cómo se gestiona una rama de
   pruebas— no está.
5. **EULA del propio juego (tema 64).** La política de privacidad tiene plantilla y checklist; el
   documento hermano que de verdad protege al desarrollador legalmente (límite de responsabilidad,
   prohibición de ingeniería inversa) no existe ni como mención.
6. **COPPA (tema 67).** Un juego con anuncios que llega a jugadores de EE. UU. menores de 13 años
   tiene una obligación legal específica que no aparece en ningún documento, a diferencia de PEGI
   que sí está muy bien cubierto.
7. **Gestión de comunidad y crisis propias (temas 78, 79, 81).** Kit de prensa y contacto con
   medios están resueltos; lo que pasa **después** del lanzamiento con la comunidad del propio
   juego (Discord, moderación, una crisis de reseñas) no tiene ni una línea.
8. **Contratos con publisher (tema 72).** `13-11` §12 resuelve muy bien freelance/colaborador/
   socio, pero la figura del publisher que financia por hitos —habitual en cuanto un estudio
   pequeño busca crecer— es distinta y no está.

### 🟠 Medios

- Epic Games Store como canal de distribución, distinto de la extensión de servicios (tema 41).
- ATT/IDFA como receta completa, no solo entrada de catálogo (tema 12).
- Sistema de reseñas de Steam explicado (tema 35).
- Fuentes tipográficas: licencia comercial en detalle (tema 57).
- MIT vs. GPL: qué significa realmente la «contaminación» (tema 63).
- GDPR: bases legales y DPA con SDKs de terceros (tema 66).
- *Work for hire* como concepto explícito, más allá de la cesión ya cubierta (tema 73).

### 🟡 Menores

- Estructura de un tráiler (tema 23).
- Psicología de precios (tema 44).
- *Samples* y bibliotecas de música con licencia por tienda (tema 58).
- Metodología de playtesting externo/beta con jugadores reales (tema 80).

## Encargo para el redactor

1. **Nuevo documento: `13 - Diseño y producción de videojuegos/26 - Legal de terceros: marcas,
   fan games y parodia.md`** (o ampliar `13-11` §9 con una subsección §9.6 si se prefiere no crear
   archivo — decisión del redactor, pero el contenido no cabe ya en una tabla de esa sección sin
   deslucirla). Contenido: qué es una marca registrada y qué riesgo corre un nombre parecido;
   la doctrina de parodia/*fair use* y por qué varía radicalmente entre EE. UU. y la UE (no
   inventar una regla universal); qué son los *fan games* y por qué algunos titulares los toleran
   y otros los persiguen con *cease & desist* (ejemplos verificables: Nintendo históricamente
   agresiva, otros estudios que autorizan explícitamente); usar el nombre o el logo de una consola
   en marketing sin autorización. Enlazar desde `13-11` §9 y desde `07-09` §1 (tabla de licencias).
   Ningún símbolo de GML implicado: es doctrina legal, como ya hace `05-02` §3.8 bis con las
   consolas.
2. **Ampliar `04 - Recetas por género/28 - Juegos para móvil (táctil).md` §9.3** (o crear una
   subsección nueva) con el trámite real de publicación en cada tienda: en Android, **Play App
   Signing** (clave de subida vs. clave de firma de la app, qué pasa si se pierde la de subida —
   se puede resetear— frente a la de la app —no—) y el **Android App Bundle** (`.aab`, por qué
   sustituyó al APK universal, cómo lo genera GameMaker con `gm-cli package --target android`
   — verificar el nombre exacto del flag de salida `.aab` contra `gm-cli package --help` antes de
   publicarlo, no está confirmado en esta auditoría); en iOS, el proceso de **App Store Connect**
   (subir el build, rellenar la ficha de privacidad *App Privacy* declarando qué recoge cada SDK
   —AdMob, Firebase—, y los motivos de rechazo más comunes de la *App Review Guidelines*: enlaces
   externos de pago sin usar StoreKit, metadatos engañosos, *crashes* en la revisión). Enlazar
   desde `05-02` §3.7, que hoy solo dice «guía oficial: wiki» sin mencionar el trámite de la tienda
   en sí (la wiki de YoYo cubre el *export*, no la publicación en Play Console/App Store Connect).
3. **Ampliar `05 - Referencia/02 - Publicar y exportar.md` §3** con una subsección nueva
   «3.x · macOS: firma y notarización», con el proceso real: certificado **Developer ID
   Application** desde una cuenta de Apple Developer, firma del `.app` (`codesign`), envío a
   notarizar (`notarytool submit`), grapado del ticket (`stapler`), y qué pasa si se distribuye
   sin ello (Gatekeeper bloquea con «no se puede verificar el desarrollador»). Contrastar con la
   documentación oficial de Apple Developer (`developer.apple.com/documentation/security/
   notarizing-macos-software-before-distribution`) antes de escribir, siguiendo el mismo patrón
   de citas fechadas que ya usa el resto de `05-02`.
4. **Ampliar `05 - Referencia/02` §3.5 (Steam)** con el paso que hoy es una sola línea: alta de la
   app en Steamworks (cuota de Steam Direct, verificar la cifra vigente contra
   `partner.steamgames.com` antes de citarla — no verificada en esta auditoría), comandos reales
   de `steamcmd` (`app_build.vdf`, `run_app_build`), y el concepto de **depósitos** y **ramas
   beta** (`SetLive`, canales de prueba antes de publicar en `default`). Enlazar desde `13-11`
   §6.8 (el día 1 ya asume que «subes la build a la tienda» sin decir cómo en Steam).
5. **Nueva plantilla en `13-11` §8 (Plantillas para rellenar): «8.6 · EULA mínimo».** Igual que ya
   existe la de política de privacidad implícita en §9.3, una plantilla corta de EULA: licencia de
   uso (no de propiedad), prohibición de ingeniería inversa y reventa, limitación de
   responsabilidad, terminación por incumplimiento, ley aplicable. Con el mismo aviso que ya usa
   §9 («nada de esto es asesoramiento legal»). Enlazar desde §9.3 (política de privacidad), que ya
   tiene el tono correcto para replicar.
6. **Ampliar `13-11` §9.3 (privacidad) con una subsección §9.3 bis: COPPA.** Qué es (ley de EE. UU.,
   *Children's Online Privacy Protection Act*), cuándo aplica (juego dirigido a menores de 13 años,
   o con base de usuarios significativa de esa edad, verificado contra la propia FTC antes de
   escribir), y su efecto práctico inmediato: anuncios no personalizados obligatorios y
   restricciones de recogida de datos — que además es justo lo que ya cataloga `07-03` con
   `GMEXT-PlayAgeSignals`/`GMEXT-DeclaredAgeRange` sin explicar la ley que las motiva. Enlazar
   ambos documentos entre sí.
7. **Nuevo documento corto: `13 - Diseño y producción de videojuegos/27 - Comunidad propia:
   Discord, moderación y gestión de crisis.md`** (numeración a confirmar contra el índice vigente
   con `_indice/actualizar.py`, que puede haber avanzado desde esta auditoría). Contenido: qué
   canales mínimos tiene el Discord de un juego pequeño (anuncios, general, feedback, bugs); reglas
   de moderación básicas y por qué un solo canal de «bugs» ahorra soporte; plan de tres pasos ante
   una crisis (reseña bomb coordinada, bug viral, acusación pública) — reconocer rápido, no borrar
   comentarios legítimos, comunicar un plan con fecha. Enlazar desde `13-11` §6.6 (press kit) y
   §7 (post-lanzamiento), y desde `07-10` (que resuelve el problema simétrico: dónde pedir ayuda
   sobre GameMaker, no cómo gestionar la comunidad de tu propio juego).
8. **Añadir a `13-11` §12 una subsección «12.7 · Acuerdos con publisher»**, distinguiéndolo de
   colaborador/socio ya cubiertos: anticipo recuperable frente a no recuperable, hitos de
   financiación ligados a entregables (el mismo lenguaje de fases de §2 de ese documento: alfa,
   beta, gold), derechos de plataforma que suele pedir un publisher, y por qué revisar quién es
   dueño del código/marca al terminar el contrato es la cláusula que más se olvida. Enlazar desde
   §12.1 (la tabla contratado/colaborador/socio), añadiendo una cuarta columna o una nota que
   remita a la nueva subsección.
9. **Añadir a `07 - Ecosistema/09 - Asset packs y recursos gráficos.md` §1** dos filas o una nota
   ampliada: fuentes tipográficas (SIL OFL como licencia más común en fuentes gratuitas, y la
   diferencia entre «gratis para uso personal» y comercial — verificar con la licencia real de una
   fuente de ejemplo, p. ej. Google Fonts, antes de generalizar) y qué significa exactamente el
   «contagio» de GPL para el código propio (si enlazas una librería GPL en tu ejecutable, tu propio
   proyecto queda obligado a publicarse también bajo GPL — es la razón por la que ninguna librería
   de la comunidad catalogada en `07-02` es GPL). No crear documento nuevo: esta tabla ya es el
   sitio correcto y solo le faltan dos filas de detalle.
10. **Ampliar `12 - Utilidades e integraciones/03 - Integraciones con servicios.md`** con una nota
    junto a la fila de Epic Games: `GMEXT-EpicOnlineServices` da logros/sesiones/matchmaking vía
    Epic Online Services, **no** publica el juego en la tienda de Epic Games Store — son dos cosas
    distintas y hoy la tabla puede confundirlas. Si se documenta el canal de distribución de Epic
    Games Store en sí, verificar primero si GameMaker tiene algún camino oficial (no confirmado en
    esta auditoría: no se encontró target de build para Epic Games Store en `05-02` §1).

## Lo que comprobé y NO hacía falta

- **Empresa o autónomo, y cómo declarar el ingreso de una tienda.** Parecía un hueco evidente,
  pero `13-11` §9.5 y §12.1 lo dejan fuera **a propósito**, con el mismo criterio que el resto de
  `13-11` aplica a todo lo dependiente de jurisdicción: lo dice explícitamente en vez de inventar
  una respuesta que solo valdría para un país. Correcto tal como está.
- **Cajas de botín y su legalidad.** Antes de leer `13-20` §1.5 esperaba encontrar un hueco grande
  aquí; es, de hecho, la sección mejor investigada de todo el dominio: PEGI 2026, Zagal et al.
  2013, y hasta la distinción entre azar-como-patrón-oscuro y azar-informado. No toques esta
  sección salvo para enlazarla más, nunca para reescribirla.
- **Accesibilidad legal (European Accessibility Act).** Esperaba un vacío; `04-27` §6 bis ya hizo
  el trabajo de leer el texto consolidado de la Directiva y confirmar, artículo por artículo, que
  el videojuego **no** está en su ámbito — con la cita exacta. No hace falta nada más aquí.
- **Reembolsos y tasa de reembolso de Steam.** Cubierto con las tres ventanas exactas (juego base,
  DLC, IAP) y la fuente primaria citada en `13-20` §1.9.
- **La extensión oficial `GMEXT-Steamworks` y el flujo de logros/tablas/nube.** `04-20` ya resuelve
  esto con código GML verificado línea a línea contra la fuente descargada de la extensión — no es
  un hueco, es de lo mejor documentado de toda la biblioteca.
- **itch.io y `butler`.** Pensé que faltaría el CLI; está completo en `07-08` §2.2, con ejemplos de
  canales y buenas prácticas.
- **Steam Deck Verified.** Existe un checklist completo con fuente primaria fechada en `05-02`
  §3.6, incluida la comprobación explícita de que «suspensión/reanudación» **no** aparece en la
  página oficial de Valve pese a citarse a menudo — exactamente el nivel de rigor que pedía este
  encargo.
