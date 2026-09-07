# Auditoría r4 · Publicar en consolas — Nintendo, PlayStation y Xbox

> 2026-09-07 · 59 temas evaluados · 6 cubiertos · 13 parciales · 40 faltan

## Resumen ejecutivo

**No, un agente que solo lea esta biblioteca no podría llevar un juego de GameMaker hasta una
consola.** Y eso es correcto hasta cierto punto — nadie puede, sin acceso NDA — pero el problema no
es solo el contenido bajo confidencialidad: es que faltan los **pasos previos, públicos y
100&nbsp;% ejecutables** que sí existen y que hoy no están documentados en ningún sitio de la
biblioteca.

Lo que ya hay es sólido en lo que cubre: `05 · 02 §1.4, §3.8, §3.8 bis` es honesto sobre el NDA, no
inventa nada, y su tabla de «categorías públicas de certificación» (mapeo de botones, guardado
atómico, suspensión/reanudación, avisos legales) es exactamente el patrón correcto para escribir
sobre algo confidencial sin alucinar. **No hay que reescribir esa sección — hay que construir
alrededor de ella.**

Lo que falta es todo lo que un desarrollador real hace **antes** de llegar a esa wiki privada, y
que **no está bajo NDA en absoluto**:

1. **El trámite de acceso en sí, con contactos y URLs reales.** GameMaker publica un artículo de
   ayuda propio con el proceso exacto: a qué web registrarse, a qué email escribir según tu región,
   qué acuerdo firmas y en qué orden. Hoy la biblioteca solo enlaza esa página (§1.4), no dice lo
   que hay dentro. Es la diferencia entre «habla con el fabricante» (lo que hay hoy) y «escribe a
   `developers@nintendo.eu` si estás en Europa, o a `thirdpartypublisher@noa.nintendo.com` si
   estás en EE.&nbsp;UU./resto del mundo, después de registrarte en developer.nintendo.com» (lo que
   un agente necesita para ejecutar el paso).
2. **El vocabulario del oficio, sin el cual ni se puede buscar ayuda.** «Lotcheck», «TRC», «XR»,
   «GDPA», «Gamerscore», «trofeo de platino» no aparecen ni una vez en toda la biblioteca
   (verificado con `buscar.py --todo`). Un agente que no conoce estos términos no puede ni
   formular la pregunta correcta a un humano, ni entender un hilo de GDC o de un foro de porting.
3. **Datos públicos concretos que sí se pueden citar hoy con fuente y fecha**: el precio real de la
   licencia Enterprise (67,99&nbsp;€/mes o 679,99&nbsp;€/12&nbsp;meses, verificado en Steam hoy), la
   convención de botones A/B invertida entre Switch y Xbox (y por qué), las resoluciones de modo
   portátil/dock, los límites de Gamerscore de Xbox, la estructura de trofeos de PlayStation, y que
   los parches ya no cuestan dinero en ninguna de las tres plataformas — todo esto es información
   pública de la industria, no del NDA, y no está en ningún documento.
4. **La alternativa realista, que hoy no existe en absoluto**: cuándo NO compensa ir a consola
   siendo indie, y con qué porting houses o publishers va la gente que sí lo hace. Es el mismo
   patrón que ya resolvió bien la ronda 3 para «publisher que financia por hitos» en general —
   aquí falta la variante específica de consola.

El bloqueo real para un agente hoy no es el NDA — es que, sin este documento, **ni siquiera sabe
por dónde empezar a pedir acceso**, ni reconoce las palabras que va a encontrar en cuanto lo
consiga.

## Tabla tema por tema

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| **A · Antes del devkit — acceso de desarrollador** | | | | |
| 1 | Nintendo: registro en developer.nintendo.com (empresa o individuo) | 🔴 | — | No hay ni la URL de registro ni la aclaración de que vale como individuo sin empresa |
| 2 | Nintendo: NDA y Términos de Servicio antes de acceder a SDK | 🟡 | `05-02` §3.8 («por confidencialidad») | Dice que hay NDA, no el orden del trámite (te registras → aceptas NDA/ToS → accedes a SDKs) |
| 3 | Nintendo: acceso a información de Switch es una solicitud **aparte** del registro general | 🔴 | — | No documentado; es un paso que bloquea a quien solo se registra y espera tener acceso automático |
| 4 | Nintendo: contacto regional para pitch del proyecto (`developers@nintendo.eu` Europa/Australia, `thirdpartypublisher@noa.nintendo.com` EE.UU./resto) | 🔴 | — | Cero. Es el paso GameMaker-específico documentado en el artículo de ayuda oficial de GameMaker, no en el manual |
| 5 | Nintendo: registrar la solicitud en la web de middleware de GameMaker tras la aprobación | 🔴 | — | Paso final de vinculación GameMaker↔Nintendo, ausente |
| 6 | Nintendo: tiempos del proceso completo | 🔴 | — | ⚠️ No hay cifra pública fiable verificada en esta sesión; no inventar un número |
| 7 | PlayStation: registro en partners.playstation.net, entidad legal obligatoria (empresa, o autónomo en Europa) | 🔴 | — | Cero. Ni la URL ni el requisito de ser entidad legal |
| 8 | PlayStation: proyecto/pitch breve como parte de la solicitud («elevator pitch, no un GDD completo») | 🔴 | — | — |
| 9 | PlayStation: revisión y aprobación («unas semanas», Sony) | 🔴 | — | ⚠️ Cifra de fuente secundaria (generalistprogrammer.com, 07-09-2026), no de Sony directamente; marcar como no confirmado con fuente primaria |
| 10 | PlayStation: firma del GDPA (*Global Developer & Publisher Agreement*) tras la aprobación | 🔴 | — | El término «GDPA» no aparece en la biblioteca (`buscar.py --todo`) |
| 11 | PlayStation: acceso a DevNet y vinculación de la cuenta de GameMaker | 🔴 | — | «DevNet» no aparece en la biblioteca |
| 12 | PlayStation: devkit + testkit gratuitos en préstamo (serie DFI-D1000, 2 años, se devuelven) | 🔴 | — | — |
| 13 | Xbox: edad mínima de 18 años para tener relación de desarrollo con Microsoft | 🔴 | — | — |
| 14 | Xbox: cuenta Microsoft **dedicada**, no la personal, para separar credenciales de publicación | 🔴 | — | — |
| 15 | Xbox: registro en ID@Xbox (formulario de contacto + información del estudio) | 🟡 | `04-20` §6.1 menciona ID@Xbox solo como requisito para Xbox Live/UWP, no como el programa de acceso a la consola nativa | El programa ID@Xbox en sí — su web, sus pasos — no está descrito como trámite de acceso a consola |
| 16 | Xbox: NDA mutuo recibido por email (20 min–3 días hábiles) | 🔴 | — | — |
| 17 | Xbox: sin coste de registro; GameMaker vincula la licencia vía su Helpdesk tras confirmar el email de Xbox | 🔴 | — | El paso de vinculación GameMaker↔Xbox (correo asociado a la cuenta de GameMaker) no está |
| 18 | Qué se puede/no se puede decir públicamente estando bajo NDA (anuncios de "estamos en consola X" necesitan visto bueno del fabricante) | 🔴 | — | Ninguna advertencia sobre esto; relevante porque un agente redactando un press kit podría anunciar una plataforma sin permiso del fabricante |
| **B · El NDA y sus consecuencias prácticas** | | | | |
| 19 | Por qué no hay documentación pública (naturaleza contractual del NDA de cada fabricante) | 🟡 | `05-02` §3.8, §3.8 bis (menciona «confidencialidad», «bajo NDA») | Dice que existe, no explica el mecanismo (es un contrato bilateral entre el fabricante y cada desarrollador aprobado, no una política genérica) |
| 20 | Consecuencia explícita para un agente de IA: **no debe inventar** contenido de una wiki privada que no puede leer | 🔴 | — | No hay ninguna instrucción, ni en `05-02` ni en `AGENTS.md`, que diga explícitamente «si el tema es de consola y no está en esta biblioteca, no te lo inventes, dilo» — es justo la regla que pide este encargo |
| 21 | Cómo trabajar con la restricción sin bloquearse: distinguir **categorías públicas** (protocolo de industria, de dominio público) de **detalles exactos** (umbrales, bajo NDA) | 🟡 | `05-02` §3.8 bis es un ejemplo perfecto de esta técnica en la práctica | Funciona como ejemplo, no está enunciada como método reutilizable para el resto de temas de consola (lotcheck, TRC, XR…) |
| **C · GameMaker y las consolas** | | | | |
| 22 | Exportadores actuales: Switch, Switch 2, PS4, PS5, Xbox One/Series | ✅ | `05-02` §3.8 (tabla con las 5 plataformas y su wiki) | — |
| 23 | Licencia Enterprise: qué habilita (consolas + código fuente del runtime) | ✅ | `05-02` §2; `13-11` §9.1 | — |
| 24 | Licencia Enterprise: **precio exacto** | 🟡 | `05-02` §2, `13-11` §9.1 solo dicen «suscripción mensual o anual», sin cifra | Verificado hoy en Steam: **67,99&nbsp;€/mes o 679,99&nbsp;€/12&nbsp;meses** (17&nbsp;% de descuento anual) — <https://store.steampowered.com/app/1847411/GameMaker_Enterprise/> (07-09-2026); corroborado por fuentes agregadas en 79,99&nbsp;USD/mes ≈ 799,99&nbsp;USD/año |
| 25 | Requisito de ser desarrollador **registrado en la plataforma**, aparte de la licencia | ✅ | `05-02` §1.4, §3.8; `13-11` §9.1 | — |
| 26 | El trámite GameMaker-específico de vinculación tras la aprobación del fabricante (a qué email/web de GameMaker avisar, cómo se activa la licencia en tu cuenta) | 🔴 | `05-02` §1.4 solo enlaza `gamemaker.io/en/help/articles/application-process-for-console-access` sin extraer su contenido | El artículo de ayuda oficial de GameMaker (verificado hoy, 07-09-2026) describe el paso a paso completo para las tres plataformas — ver «Encargo» |
| 27 | Switch 2: estado del soporte en GameMaker | 🟡 | `05-02` §3.8 (una cita de las release notes); `README.md` línea 124 (lo nombra como target nuevo) | GameMaker anunció el soporte para Switch 2 el **día uno** de la consola en abril de 2025 (blog oficial, `gamemaker.io/en/blog/gamemaker-nintendo-switch-2`, verificado por búsqueda cruzada 07-09-2026); no hay ficha pública con el detalle de instalación del módulo — verificar si ya se publicó desde entonces |
| 28 | CLI de GameMaker: consolas no soportadas hoy (`switch`, `ps4`, `ps5`, `xboxseriesxs` → «coming soon») | ✅ | `05-02` §1.2 | — |
| 29 | Wikis privadas de runtime por consola (`GMS2-Runner-Switch`, `-Switch2`, `-PS4`, `-PS5`, `-Xbox`) | ✅ | `05-02` §1.4 | — |
| **D · Nintendo Switch y Switch 2** | | | | |
| 30 | **Lotcheck**: qué es y qué comprueba de verdad (terminología/iconos de botón consistentes, no busca «cero bugs») | 🔴 | — | El término «lotcheck» no aparece en toda la biblioteca (`buscar.py --todo`) |
| 31 | Lotcheck: tiempos orientativos (2-4 semanas + 1-2 semanas por ciclo de revisión si hay que corregir algo) | 🔴 | — | Fuente secundaria (generalistprogrammer.com, r-tt.com; el checklist real de Nintendo está bajo NDA) — marcar como orientativo, no oficial |
| 32 | Rendimiento: mantener la tasa de fotogramas objetivo también en la **transición** dock↔portátil | 🟡 | `05-02` §3.8 bis cubre «tiempos de arranque» y «suspensión/reanudación», pero no la transición específica de acoplar/desacoplar | Falta esta transición como categoría propia — es distinta de arrancar o de suspender |
| 33 | Guardado en consola: API del SDK propio, límites de tamaño específicos de la plataforma | 🟡 | `05-02` §3.8 bis cubre el patrón de escritura atómica de forma genérica (aplica a cualquier plataforma) | No dice que en consola el guardado pasa por una **API de sistema propia** (no son los `file_text_*` normales), ni que los límites de tamaño son específicos de cada SDK |
| 34 | Controles: convención **A/B invertida** entre Switch y Xbox, y por qué | 🟡 | `05-02` §3.8 bis cubre «mapeo de botones consistente» y la variante regional de PlayStation, pero no menciona el caso Switch/Xbox — el que pide explícitamente este encargo | Falta el dato concreto: Nintendo heredó del NES (1983) el confirmar a la derecha (A); Sega Genesis/arcade invirtió el orden y Xbox heredó ese layout al dominar el mercado occidental — de ahí que A confirme en Xbox y B cancele en Switch, exactamente al revés |
| 35 | Terminología de botones **exacta y obligatoria** en toda la UI («Press the A Button», con la redacción y capitalización que exige cada fabricante) | 🔴 | — | Es la causa nº1 de fallos de lotcheck/cert citada en varias fuentes cruzadas; no hay ni una línea sobre esto |
| 36 | Resolución objetivo: modo portátil vs. acoplado (Switch: 720p/1080p; Switch 2: 1080p/4K) y legibilidad de texto en ambos | 🔴 | — | Ningún documento menciona cifras de resolución de Switch/Switch 2 (`grep 720p\|1080p\|4K` sin resultados en `05-02` ni en `02 - Novedades 2026/`) |
| 37 | Rechazos típicos de lotcheck | 🟡 | `05-02` §3.8 bis cubre categorías generales sin encuadrarlas como «motivos de rechazo» | Falta la forma «motivo de rechazo → cómo evitarlo», que es el formato que ya usa `05-05` §10 con éxito para macOS/Windows/Steam/Play/App Store — el mismo patrón aplicado a consola |
| 38 | eShop: reparto de ingresos (30&nbsp;% para Nintendo) | 🔴 | — | Cifra pública de fuente secundaria cruzada (generalistprogrammer.com, 07-09-2026); no está en la biblioteca |
| **E · PlayStation y Xbox: certificación, logros/trofeos, guardado, suspensión, reloj** | | | | |
| 39 | **TRC** (*Technical Requirements Checklist*) de PlayStation: qué es y qué cubre | 🔴 | — | El término «TRC» no aparece asociado a PlayStation en ningún documento de la biblioteca (solo coincidencias falsas en código de terceros) |
| 40 | **XR** (*Xbox Requirements*, antes TCR) de Microsoft: qué es, y que el nombre cambió | 🔴 | — | Cero. Verificado hoy contra Microsoft Learn: *«Xbox Requirements (XRs) consist of the policies, technical, and product component-related requirements to which all developers and publishers of Xbox console titles must conform»* — <https://learn.microsoft.com/en-us/gaming/gdk/docs/store/policies/console/certification-requirements> (07-09-2026) |
| 41 | Trofeos de PlayStation: estructura típica (30-50 trofeos bronce/plata/oro + 1 platino), el platino se dispara solo al completar el resto, excepción en F2P | 🔴 | — | «Trophy» solo aparece en código de terceros no relacionado (GameJolt); cero contenido sobre el sistema de trofeos de PlayStation en sí |
| 42 | Logros de Xbox: **Gamerscore** — 1000 obligatorio al lanzamiento, +1000 permitido cada 6 meses, máx. 200 por logro individual | 🔴 | `04-20` §6.2 usa `xboxlive_gamerscore_for_user()` para **leer** el gamerscore de un jugador, no documenta los límites de certificación | La función GML existe y está bien documentada; lo que falta es la regla de negocio de cuánto Gamerscore puede tener un juego nuevo, verificada hoy contra Microsoft Learn, *XR-055 Achievements and Gamerscore* |
| 43 | **Quick Resume** de Xbox Series: qué es, por qué PlayStation no tiene un equivalente directo (arquitectura «a metal» vs. máquina virtual de Xbox) | 🔴 | — | Cero. La guía de implementación de Quick Resume para desarrolladores está tras el programa NDA de Xbox — lo público es el concepto y la diferencia arquitectónica, verificable y citable |
| 44 | Reloj del sistema | 🔴 | — | ⚠️ No se encontró una fuente pública fiable y específica en esta sesión (más allá de la obligación genérica de sincronizar marcas de tiempo online, que no es exclusiva de consola). **No inventar contenido aquí**: dejarlo marcado como pendiente de verificación, no como hueco a rellenar con una suposición |
| 45 | Certificación de PS5: duración orientativa de la revisión inicial (15-20 días hábiles) | 🔴 | — | Fuente secundaria (generalistprogrammer.com, 07-09-2026); el proceso real de Sony está bajo NDA — marcar como orientativo |
| 46 | Devkit de PS5: hardware concreto (serie DFI-D1000 + testkit) | 🔴 | — | — |
| **F · Transversal a las tres consolas** | | | | |
| 47 | Clasificación por edades en consola: **IARC cubre digital** con un solo cuestionario (Nintendo eShop, PlayStation Store, Microsoft/Xbox Store...), pero **físico exige certificado de pago aparte** de ESRB/PEGI | 🟡 | `13-11` §9.4 explica IARC muy bien en general (ya validado como correcto en r3, no reabrir esa valoración) | Falta el matiz específico de consola: el certificado es por combinación juego+plataforma aunque el cuestionario IARC sea uno solo, y la distribución física no acepta IARC |
| 48 | Localización mínima exigida en consola | 🟡 | `04-21` §… menciona el orden EFIGS como prioridad de traducción, en un contexto general, no de certificación | No hay un mínimo fijo universal — cada plataforma exige soportar **todo** lo que el desarrollador declara, y EFIGS+PL es el estándar de facto de la industria, no una regla escrita; falta decir esto con esa precisión |
| 49 | Precio y regiones en las tiendas de consola | 🔴 | `13-11` §6.7 cubre precio/regiones/descuentos solo para **Steam** | Cada tienda de consola define sus propios tramos de precio por región (no un precio libre como en Steam); no verificado en detalle esta sesión — marcar qué falta sin inventar cifras |
| 50 | Parches y su coste: **ya no cuestan dinero** en Nintendo, Sony ni Microsoft (a diferencia del mito histórico de los ~40.000&nbsp;USD por parche de la generación Xbox 360) | 🔴 | — | Verificado hoy por búsqueda cruzada (Shacknews, ResetEra): Sony y Nintendo no cobran por actualizaciones; Microsoft las liberó de coste salvo abuso de reenvíos — dato que desmiente una creencia extendida, con la misma lógica que ya usa `05-05` §3.2 para el mito de la reputación EV de SmartScreen |
| 51 | Coste real de un fallo de certificación (no es solo tiempo: cada resubmission reinicia una cola de 4-8 semanas y suma ~15&nbsp;% al coste total de lanzamiento, según una fuente sectorial) | 🔴 | — | Cero; relevante para que un agente entienda por qué "probar en dispositivo real antes de enviar" (ya sí cubierto para App Store en `05-05` §6.5 y §10) es aún más crítico en consola |
| 52 | Ventanas de publicación / *day-and-date* específicas de consola | 🟡 | `13-11` §6.7 cubre el calendario de lanzamiento de forma genérica (aplicable a cualquier plataforma) | No distingue el caso de lanzar el mismo día en varias consolas a la vez (coordinación de fechas de aprobación entre fabricantes, cada uno con su propia cola de revisión) |
| **G · La alternativa realista: cuándo NO ir a consola, y con quién sí se va** | | | | |
| 53 | Cuándo **NO** compensa ir a consola siendo indie | 🔴 | — | Cero. Ningún documento da criterios (tamaño de equipo, ventas previas en PC/Steam, presupuesto real de porting) para decidir esto |
| 54 | Porting houses conocidas que trabajan con estudios pequeños | 🔴 | — | Cero. Ejemplos verificables hoy: Seaven Studio (Xbox Excellence Award 2025 por *Store Rating*; porteó *Brotato*, *Moonstone Island*, *Streets of Rage 4*), DO Games, Stepico, Game-Ace, Devoted Studios, y el caso concreto de un desarrollador individual registrado como Nintendo Developer especializado en ports a Switch (Konstantin Kopka / Ghostbutter) |
| 55 | Publishers que financian ports de consola específicamente (distinto del publisher genérico de `13-11` §12) | 🔴 | — | Ejemplos verificables hoy: Klabater (financia todo el proceso, se cobra de su parte de royalties desde la primera copia), Noble Robot (fee único o *revenue split*), Crossforge (publisher de récord en consola, el estudio conserva la IP), Axyos Games |
| 56 | Estructura de acuerdos de porting: fee único vs. *revenue share* vs. el riesgo de **cross-collateralización** del *recoupment* entre plataformas | 🔴 | — | Concepto crítico y ausente: un publisher puede agrupar el coste de todos los ports y no pagar regalías de la versión de PC que sí funciona hasta que los ports de consola —que pueden ir peor— también se hayan recuperado |
| 57 | Quién es el «publisher de récord» en la tienda de consola frente a Steam (gestión de la cuenta de plataforma, no solo financiación) | 🔴 | — | Relacionado con 55-56 pero distinto: en consola, a menudo el porting house o publisher **es** la entidad registrada ante el fabricante, no el estudio original — con las implicaciones de control que eso tiene |
| **Verificación cruzada con lo ya auditado** | | | | |
| 58 | Uso del nombre/logo de una consola en material de marketing propio sin autorización | ✅ | `13-25` §4 (uso nominativo, ejemplo del emulador de PlayStation, tabla de riesgo alto/bajo) | — (no reabrir; ya resuelto con rigor por la redacción de la ronda 3) |
| 59 | ¿El target «switch» de Game Options cubre Switch 1 y 2 a la vez, o Switch 2 necesita un nodo nuevo que hoy no aparece en `options list`? | 🔴 | `05-02` §1.1 lista `switch` como único nodo de consola Nintendo en `options list` (sin fecha de esa captura) | **Pregunta bloqueante para un agente**: si Switch 2 comparte nodo con Switch 1, cualquier receta que diga «configura Game Options → switch» vale para ambas; si no, hace falta saber el nombre exacto del nodo nuevo antes de dar instrucciones. ⚠️ Verificación en vivo intentada en esta sesión (ver «Lo que encontré desactualizado») |

## Huecos por prioridad

### 🔴 Graves

1. **El trámite de acceso en sí, con contactos reales, no está** (temas 1, 4, 5, 7, 8, 10, 11, 13-17,
   26). Es el hueco más caro de todos porque bloquea el primer paso: sin esto, un agente no sabe ni
   a qué web ir ni a qué email escribir. Y la información **no está bajo NDA** — la publica el
   propio GameMaker en su centro de ayuda.
2. **El vocabulario del oficio no existe en la biblioteca** (temas 30, 39, 40, 41). «Lotcheck»,
   «TRC», «XR», «trofeo de platino» — sin estos términos, un agente ni siquiera puede formular bien
   una búsqueda de ayuda a un humano o en un foro de porting.
3. **Datos duros verificables que no están, y que no dependen del NDA** (temas 24 con matiz, 34,
   35, 36, 38, 42, 50, 51): precio de Enterprise, convención de botones A/B, resoluciones de
   portátil/dock, límites de Gamerscore, coste real (o su ausencia) de un parche.
4. **La alternativa realista no existe en absoluto** (temas 53-57): cuándo no ir a consola, con qué
   porting houses o publishers va la gente que sí lo hace, y el riesgo de cross-collateralización
   del recoupment. Es el equivalente de consola al «publisher que financia por hitos» que ya pidió
   cerrar la ronda 3 en general — aquí falta la variante específica.
5. **No hay una regla explícita que le diga a un agente de IA que no debe inventarse el contenido
   de una wiki privada** (tema 20). Es justo lo que pide el encargo de esta ronda, y hoy no existe
   ni en `05-02` ni en `AGENTS.md`.

### 🟠 Medios

- Trámite GameMaker-específico de vinculación tras la aprobación del fabricante (tema 26,
  solapado con el grave 1 pero con su propio contenido: el Helpdesk de GameMaker, el correo
  asociado a la cuenta).
- Certificación de PlayStation y Xbox con nombre propio explicado (TRC/XR ya en graves) pero
  también su duración orientativa (temas 9, 31, 45).
- Quick Resume y la diferencia arquitectónica Xbox/PlayStation (tema 43).
- Devkits gratuitos de PlayStation, sus condiciones de préstamo (tema 12, 46).
- La pregunta bloqueante de si Switch 2 comparte nodo de Game Options con Switch 1 (tema 59) —
  resolver **antes** de escribir cualquier receta que mencione el target.

### 🟡 Menores

- Matices sobre temas ya parcialmente cubiertos: transición dock↔portátil (32), guardado por API
  propia de consola (33), rechazos de lotcheck en formato tabla (37), IARC en su ángulo de consola
  (47), localización mínima de facto (48), day-and-date entre varias consolas (52).
- Reloj del sistema (44): dejar marcado como pendiente, no inventar contenido de relleno.

## Encargo para el redactor

1. **Nuevo documento: `05 - Referencia/06 - Publicar en consolas - Nintendo, PlayStation y
   Xbox.md`**, hermano de `05 · 05` (mismo estilo: principios → por plataforma → checklist →
   errores clásicos → fuentes fechadas). Contenido, con las secciones ya verificadas en esta
   auditoría:
   - **§1 · Antes del devkit** (bloque A completo): el trámite de acceso a cada fabricante, con
     URLs y contactos reales — `developer.nintendo.com` (registro) →
     `developers@nintendo.eu` (Europa/Australia) / `thirdpartypublisher@noa.nintendo.com`
     (EE.&nbsp;UU./resto) para el pitch → registro del middleware de GameMaker; `partners.playstation.net`
     (registro de estudio + pitch breve) → GDPA → DevNet → vincular cuenta de GameMaker; ID@Xbox
     (cuenta Microsoft dedicada, 18+ años, formulario + info de estudio) → NDA por email →
     Helpdesk de GameMaker para activar la licencia. Fuente primaria a re-verificar en vivo antes
     de publicar (bloqueada por 403 en esta sesión, reintentar con otro método):
     `gamemaker.io/en/help/articles/application-process-for-console-access`.
   - **§2 · El NDA** (bloque B): por qué no hay documentación pública, con la regla explícita para
     un agente de IA — «si el tema es de consola y no aparece en esta biblioteca ni en el manual
     público, no te lo inventes: dilo, y usa solo categorías de dominio público (charlas GDC,
     artículos de porting houses) citadas como tales, nunca como si vinieran de la wiki privada».
     Enlazar `05-02` §3.8 bis como ejemplo ya resuelto de esta técnica.
   - **§3 · GameMaker y las consolas**: precio de Enterprise verificado (67,99&nbsp;€/mes o
     679,99&nbsp;€/12&nbsp;meses en Steam, con fecha), estado de Switch 2, y la pregunta del tema
     59 resuelta con una verificación en vivo (`gm-cli resourcetool eval "options list"` sobre un
     proyecto con toolchain 2026.0.0.23) antes de publicar nada sobre el target «switch».
   - **§4 · Nintendo Switch y Switch 2**: lotcheck (qué comprueba, tiempos orientativos con la
     fuente marcada como secundaria), terminología de botones obligatoria, la convención A/B
     invertida con su origen histórico (NES 1983 vs. Genesis/Xbox), resoluciones portátil/dock de
     Switch 1 y 2, reparto de ingresos del eShop (30&nbsp;%).
   - **§5 · PlayStation y Xbox**: TRC y XR con sus fuentes oficiales (Microsoft Learn ya
     verificado hoy), estructura de trofeos de PlayStation, límites de Gamerscore de Xbox
     (verificado hoy contra XR-055), Quick Resume, certificación (duración orientativa marcada
     como secundaria), devkits gratuitos con condiciones de préstamo.
   - **§6 · Transversal**: clasificación por edades en su ángulo de consola (IARC digital vs.
     certificado físico), localización de facto (EFIGS+PL), parches gratis hoy en las tres
     plataformas (con el mito histórico de los 40.000&nbsp;USD desmentido y fechado), coste real de
     un fallo de certificación.
   - **§7 · La alternativa realista**: criterios de cuándo NO ir a consola; porting houses citadas
     con ejemplos verificables (Seaven Studio, DO Games, Stepico, Game-Ace, Devoted Studios,
     Ghostbutter/Konstantin Kopka); publishers de porting (Klabater, Noble Robot, Crossforge, Axyos
     Games) con su modelo de acuerdo; el riesgo de cross-collateralización del recoupment.
   - Enlazar desde `05-02` §1.4 y §3.8 (que hoy solo enlazan la web de GameMaker sin extraer su
     contenido), desde `13-11` §9.1 (licencias) y §12 (publisher genérico → variante de consola),
     y desde `13-25` (ya resuelve el tema 58, solo enlazar, no reescribir).
   - Ningún símbolo de GML nuevo que verificar: es trámite y doctrina, como ya hace `05-05` con
     tiendas no-consola.
2. **Añadir a `AGENTS.md` (o al preámbulo del nuevo documento) la regla explícita del tema 20**:
   un agente que reciba un encargo de consola y encuentre que el detalle exacto no está en esta
   biblioteca **debe decirlo y ofrecer las categorías públicas conocidas**, nunca inventar el
   contenido de una wiki `GMS2-Runner-*` que no puede leer.
3. **Verificación pendiente antes de publicar** (no bloquea el resto del documento, pero sí las
   secciones que dependen de ella):
   - Reintentar `gamemaker.io/en/help/articles/application-process-for-console-access` con un
     método distinto a `WebFetch` (bloqueó con 403 en esta sesión) para confirmar el texto exacto
     de los tres flujos de vinculación antes de citarlo como fuente primaria — hoy solo hay
     fragmentos rescatados por búsqueda cruzada, suficientes para el encargo pero no para citar
     como transcripción literal.
   - Resolver el tema 59 (nodo de Game Options de Switch 2): `gm-cli resourcetool eval "OPTIONS
     LIST"` completó sin error en esta sesión pero no imprimió el listado de plataformas —
     investigar el flag correcto (probar `resourcetool eval --help` completo, o preguntar al
     usuario) antes de fiarse de la tabla de `05-02` §1.1 (ver «Lo que encontré desactualizado»).
   - Confirmar con fuente primaria de Sony/Microsoft/Nintendo (no solo secundaria cruzada) las
     cifras de tiempos de certificación (temas 9, 31, 45) antes de darlas como algo más que
     orientativas.

## Lo que comprobé y NO hacía falta

- **`05 · 02` §1.4, §3.8 y §3.8 bis.** Es, con diferencia, el mejor material de consola de toda la
  biblioteca: honesto sobre el NDA, con una tabla de categorías públicas de certificación que no
  inventa ningún umbral concreto y cita explícitamente que son categorías de conocimiento de
  industria, no contenido de la wiki privada. **No reescribir esta sección** — el nuevo documento
  debe enlazarla y construir alrededor, tal como pide el propio patrón que ya usa.
- **`04 · 20` §6 (Xbox Live/UWP).** Cubre con detalle línea a línea (incluidas las funciones
  `⚠️obsoleta` de la familia `uwp_*`) la API de Xbox Live sobre UWP, y distingue explícitamente
  en §6.7 que la exportación **nativa** a consola Xbox es un programa cerrado distinto, bajo NDA,
  sin documentación pública — exactamente la distinción correcta. No es un hueco, es la referencia
  de estilo a seguir para el resto del documento nuevo.
  Distingue GML útil-hoy con SDK ya en la biblioteca de trámite fuera de la biblioteca por NDA.
- **`13 · 25` (legal de terceros: marcas, fan games y parodia), su §4.** Ya resuelve con casos
  reales y fechados el uso del nombre/logo de una consola en marketing propio — tema 58 de esta
  tabla. No tocar, solo enlazar desde el documento nuevo.
- **`13 · 11` §9.1 (licencia de GameMaker) y §9.4 (IARC).** La tabla de licencias está correcta en
  su contenido (solo le falta el precio exacto, tema 24); IARC está muy bien explicado en general
  (r3 ya lo validó ✅) y el matiz que falta es puramente el ángulo de consola (tema 47), no una
  reescritura.
- **`01 · 12` (Input — gamepad).** Documenta bien el mapeo de constantes `gp_face1`-`gp_face4`
  Xbox/PlayStation y el botón home de Switch — es la base técnica correcta sobre la que se apoya
  el tema 34 (convención A/B), pero no es su hueco: ese documento resuelve la lectura del mando en
  GML, no la convención de certificación de cada fabricante.

## Lo que encontré desactualizado

- **El precio de la licencia Enterprise no está en la biblioteca en absoluto** (ni desactualizado
  ni actualizado: simplemente ausente en `05-02` §2 y `13-11` §9.1, que solo dicen «suscripción
  mensual o anual»). Verificado hoy, 07-09-2026, en la página de Steam de GameMaker Enterprise:
  **67,99&nbsp;€/mes o 679,99&nbsp;€ por 12 meses** (17&nbsp;% de descuento anual) —
  <https://store.steampowered.com/app/1847411/GameMaker_Enterprise/>. Cifra corroborada por fuentes
  agregadas en dólares (79,99&nbsp;USD/mes ≈ 799,99&nbsp;USD/año), consistentes entre sí.
- **La captura de `gm-cli resourcetool eval "options list"` que cita `05-02` §1.1 ya no se puede
  reproducir tal cual.** Verificado hoy, 07-09-2026, contra un proyecto de prueba real
  (`~/gm_prueba_agente/test1`, `ResourceTool@2026.0.17`, el mismo runtime que usa esta biblioteca):
  el comando **completa con «ResourceTool Successful» pero no imprime ningún listado de
  plataformas** en `stdout` — ni las 13 de `05-02` §1.1 ni ninguna otra. Ejecutar `eval "options"`
  sin argumento sí devuelve la ayuda del subcomando (`OPTIONS LIST`, `OPTIONS GET`, `OPTIONS INFO`,
  `OPTIONS SET`) y confirma que `LIST` es el verbo correcto — pero su salida real no aparece en
  esta sesión con ninguna de las dos grafías probadas (`"options list"` en minúsculas, `"OPTIONS
  LIST"` en mayúsculas). No se pudo determinar si es un cambio de comportamiento del ResourceTool
  entre la versión que capturó `05-02` §1.1 (sin fecha propia registrada) y la actual, o si hace
  falta un flag adicional no probado en esta sesión (p. ej. una salida a archivo en vez de
  `stdout`). ⚠️ **Consecuencia directa para el tema 59**: no se pudo confirmar si Switch 2 comparte
  el nodo `switch` de Game Options o necesita uno nuevo — sigue bloqueado. Quien escriba el
  documento nuevo debe repetir esta comprobación (probar `--help` de `resourcetool eval` por
  completo, o preguntar directamente al usuario si tiene salida reciente de `options list`) antes
  de dar por buena la tabla de `05-02` §1.1 tal cual está.
- **`gamemaker.io/en/get` y el artículo de ayuda de acceso a consolas devolvieron HTTP 403/429 a
  `WebFetch` en esta sesión** (probable bloqueo de user-agent, no un cambio de contenido): el
  contenido citado en este informe para esas dos páginas viene de fragmentos rescatados por
  `WebSearch` (snippets cruzados, no la página completa), suficientes para orientar el encargo del
  redactor pero **no para citarlos como transcripción literal verificada** — quien escriba el
  documento nuevo debe reintentar el acceso directo (otro user-agent, `curl`, o pedir al usuario
  que pegue el contenido) antes de dar esas citas por definitivas.
- **El mito de los ~40.000&nbsp;USD por parche** que circula en foros de la industria (citado en
  `forums.anandtech.com`, atribuido a Tim Schafer, ~2012-2013) **ya no es cierto** en 2026: Sony y
  Nintendo no cobran por actualizaciones, y Microsoft eliminó la tasa salvo abuso de reenvíos
  excesivos — verificado por búsqueda cruzada (Shacknews, ResetEra, 07-09-2026). Ningún documento
  de la biblioteca repetía este mito, pero vale la pena anticiparlo en el documento nuevo porque es
  una creencia extendida que un agente podría arrastrar de su propio entrenamiento — exactamente el
  mismo patrón que `05-05` §3.2 ya usa con éxito para desmentir el mito de la reputación EV de
  SmartScreen.
