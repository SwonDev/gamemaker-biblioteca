# 25 · Legal de terceros: marcas, fan games y parodia

> ⚠️ **Esto es información legal orientativa, no asesoramiento jurídico.** Resume doctrina y
> casos públicos verificados para que sepas cuándo hay riesgo y qué preguntar — no sustituye a
> un abogado de propiedad intelectual, y la respuesta correcta para tu caso concreto depende de
> tu jurisdicción, de tu jurisdicción de distribución (una tienda global te pone bajo el foco de
> varias a la vez) y de hechos que solo un profesional puede valorar con el contrato o el juego
> delante. Si te llega una reclamación real, §6 de este documento es el punto de partida, no el
> final.
>
> **El riesgo que cubre este documento es invisible hasta que aparece**: pedirle a un agente de
> IA «un homenaje a Zelda» o «un juego como Hollow Knight pero con...» no dispara ninguna alarma
> por sí solo, y sin embargo puede terminar generando un nombre, un logo o un diseño de personaje
> que pisa una marca registrada o un derecho de autor de un tercero. Este documento es esa
> alarma.
>
> **Qué NO cubre, y dónde está:** las licencias de assets de terceros (CC0, CC-BY, fuentes
> tipográficas, contagio de GPL) —
> [07 · 09 §1](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gr%C3%A1ficos.md);
> la licencia del propio juego frente al jugador (EULA) y la privacidad de menores (COPPA/RGPD) —
> [13 · 11 §8.6 y §9.3](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#9--legal-y-administrativo-m%C3%ADnimo);
> la cesión de derechos al encargar arte o música a otra persona —
> [13 · 11 §12.5](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#125-cesi%C3%B3n-de-derechos-por-qu%C3%A9-lo-pagu%C3%A9-no-es-es-m%C3%ADo);
> las cajas de botín y su estado legal por país —
> [13 · 20 §1.5](./20%20-%20Modelo%20de%20negocio%2C%20monetizaci%C3%B3n%20y%20%C3%A9tica%20del%20dise%C3%B1o.md#15--cajas-de-bot%C3%ADn-mec%C3%A1nica-adicci%C3%B3n-y-estado-legal);
> y el trámite de firma, notarización y subida a cada tienda —
> [05 · 05](<../05 - Referencia/05 - Entregar el juego - firmar, notarizar y subir a las tiendas.md>).
> Este documento cubre exclusivamente el riesgo de usar **la propiedad intelectual de un tercero**
> —su nombre, sus personajes, su marca— sin permiso.

---

## 1 · Los principios

### 1.1 Marca registrada y derecho de autor protegen cosas distintas

Es el error de base que hace que todo lo demás se entienda mal: **«propiedad intelectual» no es
una sola cosa**. Para un videojuego importan sobre todo dos regímenes, y protegen aspectos
distintos del mismo producto:

| | **Derecho de autor** (*copyright*) | **Marca registrada** (*trademark*) |
|---|---|---|
| Qué protege | La **expresión concreta**: el código, el arte, la música, el guion, el diseño visual de un personaje | Un **signo distintivo** que identifica el origen comercial de un producto: un nombre, un logo, a veces un sonido o un color |
| Cómo se obtiene | **Automático** desde el momento en que se crea la obra, sin registro (Convenio de Berna) | Normalmente hace falta **registrarla** ante una oficina (USPTO en EE. UU., EUIPO en la UE, OEPM en España) y usarla en el comercio |
| Cuánto dura | Un plazo fijo (vida del autor + décadas, según el país) | **Indefinida**, mientras se siga usando y renovando |
| Qué NO protege | Ideas, sistemas, métodos o reglas de juego (§1.3) | Nada que no sea el signo en sí: no protege una mecánica ni una idea |

Fuente: definiciones oficiales verificadas en U.S. Patent and Trademark Office, *Protecting Your
Trademark* — <https://www.uspto.gov/sites/default/files/BasicFacts_0.pdf>, y EUIPO, *Tipos de
marcas* — <https://www.euipo.europa.eu/es/trade-marks/before-applying/types-of-trade-marks>
(ambas consultadas 07-09-2026). La EUIPO lo resume así: una marca registrada da a su titular «el
derecho exclusivo a utilizarla en operaciones económicas y a evitar que otros utilicen signos
distintivos idénticos o similares aplicados a productos o servicios idénticos o similares».

**Por qué importa la distinción para un desarrollador**: casi siempre se infringen **las dos a la
vez** cuando se copia un personaje conocido —su nombre está protegido como marca, su diseño
visual como derecho de autor—, pero hay casos donde solo aplica una. Usar el nombre «Mario» en tu
ficha de tienda para decir «como Mario, pero...» es un problema de marca aunque no dibujes a
Mario; copiar el diseño exacto de un enemigo sin usar su nombre es un problema de derecho de
autor aunque no menciones la marca.

### 1.2 Lo peligroso es el nombre y el aspecto de un personaje, no la mecánica

**Las reglas de un juego no se registran ni se protegen por derecho de autor.** Es la llamada
*dicotomía idea/expresión*, y para videojuegos hay un caso que la fijó con precisión:

> **Tetris Holding, LLC v. Xio Interactive, Inc.** (Distrito de Nueva Jersey, sentencia del 30 de
> mayo de 2012). Xio admitió haber copiado deliberadamente Tetris al diseñar su clon «Mino», y
> basó su defensa en que las reglas, la mecánica y la función del juego no están protegidas por
> derecho de autor —lo cual es **cierto**—. El tribunal falló igualmente a favor de Tetris,
> porque Xio no se había limitado a copiar la mecánica: había copiado también la **expresión
> visual concreta** —proporciones del tablero, forma y color exactos de las piezas, el «aspecto y
> sensación» (*look and feel*)— que sí está protegida.

Fuentes cruzadas: Loeb & Loeb, *Tetris Holding, LLC v. Xio Interactive, Inc.* —
<https://www.loeb.com/en/insights/publications/2012/06/tetris-holding-llc-v-xio-interactive-inc>
· Wikipedia, *Tetris Holding, LLC v. Xio Interactive, Inc.* —
<https://en.wikipedia.org/wiki/Tetris_Holding,_LLC_v._Xio_Interactive,_Inc.> (ambas consultadas
07-09-2026).

**Lo que se sigue de este caso, en la práctica**:

- Un *deckbuilder roguelike*, un *metroidvania*, un *souls-like*: **el género y la mecánica son
  libres de copiar**, y así se ha hecho toda la historia del medio. Nadie es dueño de «subir de
  nivel», «vida regenerable en hogueras» o «combinar cartas para formar un mazo».
- **Lo que sí es peligroso es la expresión concreta que va encima de esa mecánica**: el nombre
  exacto de un personaje, su diseño visual reconocible, su música, su logo, el texto literal de
  sus diálogos, el diseño exacto de un nivel icónico píxel a píxel.
- «Un homenaje a X» es, en la práctica, la frase que separa lo legal (inspirarte en su mecánica y
  su tono) de lo arriesgado (usar su nombre, sus personajes o su arte).

### 1.3 Fan games: una zona gris permanente, no una excepción legal

**No existe una excepción legal universal llamada «fan game».** Hacer un juego gratuito «por
amor al original» no cambia que sigas usando el nombre, los personajes o el arte de otra persona
sin su permiso. Lo que existe en la práctica son tres situaciones muy distintas, y confundirlas es
el error más caro:

1. **Tolerancia informal**: el titular sabe que existen fan games de su franquicia y, de momento,
   no actúa. **No es un permiso**: puede cambiar de política cualquier día, sin aviso, incluso
   contra un proyecto que llevaba años activo (§3).
2. **Política de contenido de fans por escrito**: el titular publica reglas explícitas de qué se
   puede y qué no. Existe, pero es menos habitual de lo que parece, y **casi siempre excluye
   videojuegos** aunque permita arte, vídeos o merchandising (§3.4).
3. **Autorización explícita del proyecto concreto**: el titular contacta directamente y da luz
   verde a ese fan game en particular. Es el único caso con seguridad jurídica real, y es raro.

**El apoyo público de un creador no es un contrato.** Que el propio autor de un juego diga en
redes que le encantan los fan games de su obra (§3.4) genera buena voluntad, no un documento legal
que te proteja si la empresa que sea dueña de los derechos —que puede no ser la misma persona—
decide actuar.

### 1.4 Parodia: qué protege y qué no, y por qué varía tanto entre países

La parodia **sí** es una excepción legal reconocida en varios sistemas, pero **su alcance real
cambia radicalmente según la jurisdicción** — no hay una regla universal, y afirmar lo contrario
es la forma más rápida de dar un consejo legal falso.

**Estados Unidos — *fair use*, artículo 17 U.S.C. § 107.** No hay una excepción de «parodia»
como tal en el texto de la ley: la parodia se defiende dentro del test de cuatro factores del
*fair use* (propósito y carácter del uso, naturaleza de la obra, cantidad usada, efecto sobre el
mercado de la obra original). El caso de referencia:

> **Campbell v. Acuff-Rose Music, Inc.**, 510 U.S. 569 (1994). El grupo 2 Live Crew grabó una
> versión paródica de «Oh, Pretty Woman» de Roy Orbison. El Tribunal Supremo revocó el fallo del
> Sexto Circuito y estableció que **una parodia con fines comerciales puede ser *fair use***: el
> carácter comercial es solo uno de los factores a valorar, no un veto automático.

Fuente: resumen oficial de la Oficina de Copyright de EE. UU. —
<https://www.copyright.gov/fair-use/summaries/campbell-acuff-1994.pdf> (consultado 07-09-2026).
**Matiz importante**: este test es caso por caso y exige que la parodia realmente **comente o se
burle del original** — usar su fama solo para vender algo distinto («sátira» pura sin comentar la
obra en sí) tiene mucha menos protección que la parodia genuina.

**Unión Europea — excepción opcional, artículo 5.3.k de la Directiva 2001/29/CE.** Cada Estado
miembro decide si la incorpora. El caso que fija su alcance:

> **Deckmyn v. Vandersteen** (TJUE, C-201/13, sentencia del 3 de septiembre de 2014). Un político
> belga distribuyó un calendario con una portada que imitaba un cómic («Suske en Wiske») cambiando
> al protagonista por el alcalde de Gante lanzando monedas a gente de otras etnias, con un mensaje
> discriminatorio. El TJUE fijó que «parodia» es un **concepto autónomo del derecho de la UE**,
> con dos características esenciales: **(1) evocar una obra existente siendo perceptiblemente
> distinta de ella, y (2) constituir una expresión de humor o burla** — y que hay que
> **equilibrar** ese derecho con los del autor original (no vale si el mensaje discrimina o daña
> gravemente su reputación).

Fuentes: EUR-Lex, texto de la sentencia — <https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX%3A62013CJ0201>
· Lexology, resumen — <https://www.lexology.com/library/detail.aspx?g=bf1068a2-2a88-467f-b103-ffce3b55b729>
(ambas consultadas 07-09-2026).

**España — artículo 39 del Texto Refundido de la Ley de Propiedad Intelectual** (Real Decreto
Legislativo 1/1996). La parodia de una obra divulgada **no necesita el consentimiento del autor**
siempre que **no implique riesgo de confusión con la obra original** ni **infiera un daño a la
obra o a su autor**. Fuente: texto consolidado, BOE — <https://www.boe.es/buscar/act.php?id=BOE-A-1996-8930>
(consultado 07-09-2026), artículo 39.

**Lo que NO cambia entre jurisdicciones, y es la trampa habitual**: **ninguna de estas tres
excepciones cubre automáticamente la marca registrada**, solo el derecho de autor. Una parodia
puede estar perfectamente protegida como obra derivada y, al mismo tiempo, seguir infringiendo la
marca si genera confusión sobre el origen comercial del producto o si el uso del nombre/logo va
más allá de lo necesario para la broma. Ver §4 para la parte de marca.

---

## 2 · El método: evaluar el riesgo antes de escribir una línea

### 2.1 Las cuatro preguntas

1. **¿Usas el nombre, el logo o el diseño reconocible de un personaje concreto de otra obra?**
   Si sí, hay riesgo real de marca y/o derecho de autor (§1.1-§1.2), con independencia de si
   cobras por el juego.
2. **¿Te apoyas solo en el género o la mecánica de otro juego, con nombres y arte propios?**
   Bajo riesgo: las mecánicas no están protegidas (§1.2). Este es el terreno de la inmensa
   mayoría de juegos «inspirados en» que sí se publican sin problema.
3. **Lo que haces, ¿comenta o se burla de verdad del original, o solo usa su fama para vender
   algo distinto?** Determina si puedes apoyarte en la excepción de parodia de tu jurisdicción
   (§1.4) — y recuerda que esa excepción, aunque aplique, no cubre la marca.
4. **¿El titular tiene una política de fan content explícita, o un historial documentado de
   tolerancia o de persecución con esa franquicia concreta?** Investiga caso por caso: la tabla
   de §3.5 da el patrón de cinco titulares reales, no una regla general — cada empresa (e incluso
   cada franquicia dentro de la misma empresa) se comporta distinto.

### 2.2 Señales de alarma concretas

Cualquiera de estas, sola, ya sube el riesgo de una reclamación real:

- El **nombre de tu juego** en la propia tienda incluye el nombre de la franquicia original
  («... like», «fan game de...», «tributo a...»).
- Usas **assets extraídos literalmente** del juego original (sprites, modelos o texturas
  «rippeados» de la ROM o del propio juego, no recreados).
- Usas el **logo o la tipografía oficial** de la franquicia.
- **Vendes** el fan game, aunque sea a un precio simbólico: rompe casi cualquier tolerancia
  informal que existiera para la versión gratuita (ver el caso de Take-Two en §3.2, cuya
  excepción explícita es «no comercial»).
- No hay **ningún aviso** de que el proyecto no está afiliado ni respaldado por el titular
  original — es la mínima señal de buena fe que casi todas las políticas de fan content exigen
  (§3.4).

### 2.3 La escalera de riesgo

| Nivel | Qué es | Riesgo | Ejemplo del patrón |
|---|---|---|---|
| **Mínimo** | Género/mecánica inspirados, nombres y arte 100 % propios | Muy bajo — las mecánicas no se protegen (§1.2) | Cualquier *roguelike* con mazo de cartas propio |
| **Bajo** | Parodia genuina que comenta el original, con nombres/arte transformados, sin usar el logo oficial | Depende de la jurisdicción (§1.4) y de que no genere confusión de marca | Un chiste visual claramente distinto, no una copia con el nombre cambiado una letra |
| **Medio-alto** | Fan game gratuito con nombres/personajes originales reconocibles, código y arte propios, sin assets extraídos | Zona gris pura: depende por completo de la tolerancia histórica de ese titular concreto (§3) | Los ejemplos de §3.1-§3.4 |
| **Alto** | Fan game (gratis o de pago) con assets extraídos del original, o que vende contenido | Muy alto en casi cualquier caso documentado | La inmensa mayoría de los proyectos bloqueados en §3 |

---

## 3 · Casos verificados: lo que ha pasado de verdad, con fecha

No hay una «regla de la industria»: hay historiales por empresa, y a veces por franquicia dentro
de la misma empresa. Estos cinco casos, verificados con fuente y fecha, muestran el espectro real.

### 3.1 Nintendo: un historial consistentemente agresivo

Dos casos ocurridos **el mismo mes**, agosto-septiembre de 2016, ilustran el patrón:

- **AM2R** (*Another Metroid 2 Remake*). Se lanzó gratis el **6 de agosto de 2016**, coincidiendo
  con el 30.º aniversario de la serie Metroid, tras cerca de 10 años de desarrollo. Nintendo
  empezó a retirar los enlaces de descarga al día siguiente (**7 de agosto**). El **2 de
  septiembre de 2016**, el desarrollador, Milton "DoctorM64" Guasti, recibió una notificación de
  retirada DMCA directa de Nintendo of America y anunció el fin del proyecto: *«Nintendo of
  America, Inc. has filed a takedown request under the Digital Millennium Copyright Act (DMCA).
  I received the request on my personal email, so I'm complying with their requests»*. Fuentes:
  Nintendo Life, 02-09-2016 —
  <https://www.nintendolife.com/news/2016/09/nintendo_of_america_issues_takedown_request_on_am2r_ending_the_project>
  · Wikipedia, *AM2R* — <https://en.wikipedia.org/wiki/AM2R> (ambas consultadas 07-09-2026).
- **Pokémon Uranium**. Lanzado también el **6 de agosto de 2016** tras más de nueve años de
  desarrollo, alcanzó **1,5 millones de descargas** en su primera semana. Los desarrolladores
  recibieron múltiples notificaciones de retirada de abogados en representación de Nintendo of
  America y dejaron de ofrecer enlaces oficiales de descarga desde su propia web. Fuente: Slashdot,
  *Nintendo Shuts Down 'Pokemon Uranium' Fan Game After 1.5 Million Downloads*, 18-08-2016 —
  <https://games.slashdot.org/story/16/08/18/0047205/nintendo-shuts-down-pokemon-uranium-fan-game-after-15-million-downloads>
  (consultado 07-09-2026). ⚠️ Alguna fuente secundaria matiza que los propios desarrolladores
  actuaron de forma preventiva antes de recibir una carta formal individual; en cualquier caso, el
  resultado —notificaciones de retirada y fin de la distribución oficial— es el mismo.

**El patrón**: ambos proyectos eran gratuitos, llevaban años en desarrollo con conocimiento
tácito del público, y ninguno sobrevivió al éxito que atrajo atención mediática. Con Nintendo, la
popularidad del fan game no es un escudo: es lo que dispara la reclamación.

### 3.2 Take-Two/Rockstar: OpenIV y el giro de política (2017)

- **5 de junio de 2017**: el desarrollador principal de OpenIV, una herramienta de modding para
  GTA V muy usada, recibió una **carta de cese y desista** de Take-Two Interactive, alegando que
  la herramienta permitía a terceros *«defeat security features of its software and modify that
  software in violation [of] Take-Two's rights»*.
- **14 de junio de 2017**: el equipo de OpenIV anunció el cierre de la distribución de la
  herramienta tras casi 10 años activa.
- **Reacción de la comunidad**: una oleada de reseñas negativas masivas contra los juegos de
  Take-Two en Steam y una petición en Change.org con más de 77 000 firmas.
- **~23 de junio de 2017**: Take-Two/Rockstar dieron marcha atrás y publicaron una política
  explícita: **no** emprenderán acciones legales contra proyectos de terceros sobre sus juegos de
  PC que sean **de un solo jugador, no comerciales, y respeten los derechos de propiedad
  intelectual de terceros** — quedando **excluidos** expresamente el multijugador/*online*, las
  herramientas que puedan afectarlo, y el uso de **otra propiedad intelectual** (incluida otra IP
  del propio Rockstar) dentro del proyecto.

Fuentes: PC Gamer —
<https://www.pcgamer.com/gta-modding-tool-openiv-shuts-down-claiming-cease-and-desist-from-take-two/>
· bit-tech, 15-06-2017 — <https://www.bit-tech.net/news/gaming/2017/06/15/gta-tool-openiv-downed/>
· PC Gamer, sobre la política revisada —
<https://www.pcgamer.com/rockstar-says-you-wont-be-banned-for-using-gta-5-single-player-mods/>
(todas consultadas 07-09-2026).

**Por qué importa para un fan game, no solo para un mod**: la política de Take-Two es una de las
más generosas de la industria por escrito, y aun así **no cubre un fan game independiente** —
solo mods del propio juego de Take-Two, de un jugador, sin mezclar IP ajena. Un juego nuevo que
use personajes de GTA sigue fuera de esa excepción.

### 3.3 Sega: Streets of Rage Remake (2011)

Un proyecto de fans llevado con más cuidado que la media y, aun así, bloqueado:

- El proyecto («Bombergames», liderado por el desarrollador español conocido como «Bomber Link»)
  empezó el **17 de marzo de 2003** y llegó a implicar a más de 20 personas durante ocho años.
  Los propios creadores habían **informado a Sega por carta durante el desarrollo**.
- Se lanzó completo y gratuito en **abril de 2011**: más de 100 fases nuevas o remasterizadas, 19
  personajes jugables, 64 enemigos de toda la saga, 83 canciones remezcladas y 8 finales.
- **11 de abril de 2011**: Sega contactó al foro que alojaba el juego pidiendo su retirada, citando
  la necesidad de «proteger nuestros derechos de propiedad intelectual». Un moderador del foro lo
  confirmó públicamente ese mismo día. Fuente: Kotaku, 11-04-2011 —
  <https://kotaku.com/fan-made-streets-of-rage-remake-pulled-after-request-fr-5791059> (consultado
  07-09-2026).
- El equipo siguió publicando pequeñas actualizaciones de forma discreta después de la retirada
  del alojamiento oficial.

**Un dato que pone el caso en perspectiva, sin implicar continuidad del equipo**: casi una década
después, Sega **sí** encargó una secuela oficial de la saga —*Streets of Rage 4* (2020, Dotemu /
Lizardcube / Guard Crush Games, estudios distintos al equipo de Bombergames—, mostrando que la
demanda que el fan game había detectado años antes acabó sirviéndose por la vía oficial, no por la
del proyecto bloqueado.

### 3.4 El otro extremo: tolerancia pública y políticas escritas

No todos los titulares se comportan igual. Dos ejemplos documentados de mayor apertura, con sus
límites reales:

- **Toby Fox (Undertale)**: tolerancia pública informal y explícita. El propio creador ha
  nombrado y elogiado fan games concretos —*Glitchtale*, *Underswap*, *Underverse*, *Inktale*,
  *Underfell*— y, a propósito de la polémica sobre los derechos musicales de *Undertale Yellow*,
  declaró: *«If well-meaning fans have made a mistake, it should be our job to figure out how to
  help them make it right»* y *«More than anything, we should be supporting the love and passion
  of our fans at every opportunity»*. Fuente: GamesRadar+ —
  <https://www.gamesradar.com/undertales-toby-fox-says-fans-should-be-supported-at-every-opportunity-amid-debate-over-music-rights-in-fanmade-prequel/>
  (consultado 07-09-2026). ⚠️ Sigue siendo **tolerancia informal**, no una licencia por escrito:
  no protege legalmente a nadie si mañana cambia de postura o si los derechos pasan a otra
  entidad.
- **Wizards of the Coast** (Dungeons & Dragons): tiene una **política de contenido de fans por
  escrito**, poco habitual en la industria — <https://company.wizards.com/en/legal/fancontentpolicy>
  (consultado 07-09-2026). Permite arte, vídeos, pódcast y contenido similar de forma gratuita
  (incluso con ingresos de plataformas como YouTube o Patreon), pero **prohíbe explícitamente**
  usar su propiedad intelectual «en otros juegos, sean tuyos o de otra persona» —cita literal:
  *«Don't use Wizards' IP in other games. This includes your own or other people's games»»—,
  vender el contenido, o usar sus logos y marcas sin permiso. Es la política de fan content más
  generosa que apareció en esta investigación, y **aun así traza la línea justo en los
  videojuegos**.

### 3.5 Tabla resumen

| Titular | Postura documentada | Caso y fecha |
|---|---|---|
| **Nintendo** | Agresiva y consistente, incluso años después de que el proyecto lleve activo con conocimiento público | AM2R y Pokémon Uranium, ago-sep 2016 |
| **Take-Two / Rockstar** | Bloqueo inicial → política escrita de tolerancia parcial (solo mods de un jugador, sin otra IP) | OpenIV, jun 2017 |
| **Sega** | Bloqueo sin política de tolerancia general publicada | Streets of Rage Remake, abr 2011 |
| **Toby Fox / Undertale** | Tolerancia pública informal, no vinculante | Declaraciones públicas, ~2022-2026 |
| **Wizards of the Coast** | Política escrita, pero excluye explícitamente los videojuegos | Fan Content Policy vigente (07-09-2026) |

**La lectura correcta de esta tabla no es «Nintendo mala, Toby Fox bueno»**: es que **no hay
forma de predecir la postura de un titular sin investigar esa franquicia en concreto**, y que
incluso la política escrita más generosa localizada en esta investigación excluye justo la
categoría —videojuegos— que más le importa a quien lee este documento.

---

## 4 · Usar el nombre, el logo o la imagen de una consola, un motor o una marca de terceros

Distinto de crear un fan game: esto es sobre **mencionar** una marca ajena real —una consola, un
motor, un mando— en tu propia ficha de tienda o marketing, cuando lo que vendes es tu juego
original.

> 🎮 **Si la consola es una de las que estás desarrollando de verdad**, esta sección cubre el
> riesgo de marca en general; el matiz específico de consola —estar aprobado como desarrollador
> **no** te da permiso para anunciar la plataforma hasta que el fabricante lo autorice, es
> información sujeta a NDA— está en
> [05 · 06 §2.4](../05%20-%20Referencia/06%20-%20Publicar%20en%20consolas%20-%20Nintendo%2C%20PlayStation%20y%20Xbox.md#24-qué-pasa-si-te-dicen-que-no-y-qué-no-puedes-anunciar-aunque-te-digan-que-sí).

### 4.1 El uso nominativo: la salida legal para referirte a algo real

Existe una doctrina reconocida —sobre todo en EE. UU., con equivalentes prácticos en otras
jurisdicciones— que permite nombrar la marca de otro **para describir un hecho real**, sin que
eso sea infracción:

> **New Kids on the Block v. News America Publishing, Inc.**, 971 F.2d 302 (9.º Circuito, 1992).
> El tribunal fijó un test de tres partes para el **uso nominativo** (*nominative fair use*): **(1)**
> el producto o servicio no se puede identificar fácilmente sin usar la marca; **(2)** se usa solo
> lo necesario de la marca, ni un elemento más; **(3)** el uso no sugiere patrocinio o aprobación
> del titular de la marca.

Fuente: Quimbee, resumen del caso —
<https://www.quimbee.com/cases/new-kids-on-the-block-v-news-america-publishing-inc> (consultado
07-09-2026).

Un caso más específico de videojuegos, sobre usar capturas reales de un sistema ajeno con fines
comparativos:

> **Sony Computer Entertainment America v. Bleem, LLC**, 214 F.3d 1022 (9.º Circuito, 2000). Bleem
> vendía un emulador de PlayStation para PC y usaba capturas de pantalla reales de juegos de Sony
> en su publicidad comparativa, mostrando la diferencia de resolución. El tribunal falló que ese
> uso era *fair use* — con el matiz de que las capturas tenían que ser **imágenes reales** tomadas
> de la pantalla, no aproximaciones simuladas.

Fuente: Studicata, resumen del caso —
<https://www.studicata.com/case-briefs/case/sony-computer-entertainment-america-v-bleem>
(consultado 07-09-2026). ⚠️ Es un caso concreto sobre capturas de pantalla en publicidad
comparativa de un producto competidor (un emulador), no una licencia general para usar material
de una consola en cualquier contexto — no lo generalices más allá de lo que dice.

### 4.2 Qué sí y qué no en tu ficha de tienda

| Práctica | Riesgo | Por qué |
|---|---|---|
| «Compatible con mando de Xbox / PlayStation / Switch Pro» (texto) | Bajo — uso nominativo descriptivo | Describe un hecho real, sin usar el logo oficial, sin sugerir patrocinio (§4.1) |
| «Hecho con GameMaker» en tu ficha o créditos | Bajo — describe la herramienta real que usaste | Uso nominativo típico; no encontramos en esta sesión una guía pública de marca de YoYo Games que lo restrinja — ⚠️ no verificado: si vas a usar el **logo** oficial de GameMaker (no solo el texto), confírmalo contra los términos vigentes de `gamemaker.io` antes de publicarlo |
| El **logo oficial** de una consola en tu *capsule*, icono o tráiler, sin ser un producto licenciado | Alto | El logo de una marca registrada usado como si fueras un producto oficial es exactamente lo que el test de uso nominativo prohíbe (parte 2 y 3 de §4.1) |
| «Producto oficial de Nintendo/Sony/Microsoft», o cualquier redacción que insinúe patrocinio o licencia que no tienes | Muy alto | Va contra la tercera condición del uso nominativo en cualquier jurisdicción, con independencia de si es cierto lo demás |
| Capturas de pantalla reales de otro juego, con fines de comparación genuina | Depende del contexto (§4.1, caso Bleem) | Válido cuando compara de verdad y no simula ni degrada la imagen |

### 4.3 Emuladores, motores y compatibilidad: el matiz que separa a Bleem de un fan game

Bleem vendía software **propio** (un emulador) y usaba imágenes ajenas solo para **compararlo**
con el original — no vendía un producto que se hiciera pasar por PlayStation ni usaba personajes
de Sony. Es la misma lógica que aplica a mencionar «GameMaker» o «compatible con mando Xbox»: se
permite **describir una relación real y verificable** con la marca de otro, no **apropiarse** de
su identidad, sus personajes o su fama. La línea entre «lo menciono porque es cierto» y «lo uso
para que parezca oficial» es, en la práctica, la misma línea que separa el uso nominativo legal de
la infracción.

---

## 5 · Música y sonidos con derechos

[13 · 11 §5](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#5--assets-y-pipeline)
ya advierte de lo esencial: una fuente tipográfica es software con licencia propia distinta del
pack donde venía, y la música «para vídeos de YouTube» no es una licencia de videojuego. Dos
piezas que faltaban ahí y sí importan en producción:

- **No existe una «regla de los X segundos» que permita samplear sin permiso.** Es uno de los
  mitos más repetidos del sector musical y se aplica igual a un videojuego que incluya una
  muestra real de una grabación ajena en su banda sonora. El caso de referencia lo dice sin
  matices:

  > **Bridgeport Music, Inc. v. Dimension Films**, 410 F.3d 792 (6.º Circuito, sentencia del 3 de
  > junio de 2005). Una película había usado dos segundos de un solo de guitarra de una grabación
  > ajena, con el tono bajado y en bucle. El tribunal falló que **usar cualquier fragmento de una
  > grabación sonora, sin importar la duración, infringe el copyright salvo que el titular dé
  > permiso**, con la frase que quedó como cita habitual del caso: *«Get a license or do not
  > sample. We do not see this as stifling creativity in any significant way»*.

  Fuente: Wikipedia, *Bridgeport Music, Inc. v. Dimension Films* —
  <https://en.wikipedia.org/wiki/Bridgeport_Music,_Inc._v._Dimension_Films> (consultado
  07-09-2026). ⚠️ Es doctrina de un circuito concreto de EE. UU. (no de todo el país ni de otras
  jurisdicciones), pero el principio práctico —samplear sin licencia es un riesgo real, no una
  zona gris de segundos— se aplica igual en la mayoría de sistemas de derecho de autor.
- **El Content ID de YouTube es un problema distinto de la licencia del juego en sí.** Aunque
  tengas la licencia correcta para usar una pista **dentro** de tu juego, un tráiler o un vídeo
  de gameplay que la incluya puede recibir una reclamación automática de Content ID si la
  plataforma de distribución de música del autor original no reconoce esa licencia concreta —
  típicamente porque la licencia cubre «uso en el juego» pero no «vídeos de marketing en
  YouTube» como modalidad de explotación separada (el mismo problema de modalidades explícitas
  que ya explica
  [13 · 11 §12.5](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#125-cesi%C3%B3n-de-derechos-por-qu%C3%A9-lo-pagu%C3%A9-no-es-es-m%C3%ADo)
  para encargos de arte). Antes de encargar o comprar música, confirma por escrito que la licencia
  cubre explícitamente **tráileres y vídeos de marketing en plataformas de terceros**, no solo «el
  juego».

---

## 6 · Qué hacer si te llega una reclamación

### 6.1 Primero: lee exactamente qué te reclaman

No todas las reclamaciones son iguales, y reaccionar antes de entender cuál es cuál cuesta caro:

- **¿Es una notificación de retirada (DMCA u otra) contra tu tienda/alojamiento**, o una **carta
  de cese y desista** dirigida a ti directamente? La primera la resuelve la plataforma según su
  proceso; la segunda te la envían a ti y espera una respuesta tuya.
- **¿Reclaman derecho de autor, marca, o ambos?** Cambia qué defensa tiene sentido (§1.1): una
  reclamación de marca por el nombre de tu juego no se resuelve retirando una imagen, y viceversa.
- **¿Qué piden exactamente?** Retirar el juego entero, cambiar solo el nombre, quitar un asset
  concreto — a veces la reclamación es mucho más limitada de lo que parece a primera lectura, y
  responder ofreciendo el cambio mínimo razonable puede resolverlo sin más.

### 6.2 Estados Unidos: notificación DMCA y contranotificación

Si tu juego se retiró de una plataforma (Steam, itch.io, GitHub, YouTube) por una notificación
DMCA, la propia ley (17 U.S.C. § 512) prevé un mecanismo de respuesta:

- Puedes presentar una **contranotificación** (*counter-notice*), bajo pena de perjurio,
  declarando tu **buena fe** de que el contenido se retiró por error o identificación equivocada.
- Si el reclamante original **no presenta una demanda judicial**, la plataforma debe **restaurar
  el contenido en no menos de 10 ni más de 14 días hábiles** tras recibir tu contranotificación —
  verificado en el texto de la ley, 17 U.S.C. § 512(g)(2)(C) —
  <https://www.law.cornell.edu/uscode/text/17/512> (consultado 07-09-2026).
- **Presentar una contranotificación falsa expone a las mismas penas por perjurio** que una
  notificación de retirada falsa: no la uses como táctica dilatoria si sabes que la reclamación
  es legítima.

⚠️ Presentar una contranotificación es, en la práctica, decirle al reclamante «si sigues
adelante, te veo en un tribunal de EE. UU.» — es una decisión con consecuencias reales, no un
trámite administrativo. No la presentes sin haber valorado con criterio (o con un abogado, si el
caso lo justifica) si tu uso está de verdad protegido.

### 6.3 Fuera de EE. UU.: notificación y retirada, y la vía civil

Fuera del marco DMCA, la mayoría de plataformas aplican de todas formas un proceso de
**notificación y retirada** (*notice-and-takedown*) similar por contrato, aunque no exista la
misma ley detrás. ⚠️ El detalle exacto —qué exige, qué plazos hay, si existe un equivalente
formal a la contranotificación— depende de la plataforma y de tu jurisdicción; no lo generalices
sin comprobarlo en los términos de servicio concretos de dónde publiques. En la Unión Europea, el
marco general de responsabilidad de plataformas por contenido de terceros está hoy regulado por
el Reglamento de Servicios Digitales (*Digital Services Act*) — ⚠️ no verificado en detalle en
esta sesión su aplicación específica a reclamaciones de propiedad intelectual en tiendas de
videojuegos: confírmalo con una fuente legal si te enfrentas a un caso real en la UE.

### 6.4 Cuándo hablar con un abogado de verdad

Este documento te da el mapa, no el veredicto. Habla con un profesional de propiedad intelectual
en cuanto se cumpla cualquiera de estas condiciones:

- Recibiste una **carta de cese y desista** dirigida a ti (no solo una notificación automática a
  una plataforma).
- El titular menciona **daños económicos** o amenaza con una demanda, no solo con retirar el
  contenido.
- Tu proyecto ya genera ingresos reales y una retirada te supondría una pérdida significativa.
- No tienes claro si tu caso entra en la excepción de parodia de tu jurisdicción (§1.4) y el
  riesgo de seguir adelante sin saberlo es alto.

---

## 7 · Checklist

- [ ] Antes de nombrar el juego, comprueba que el nombre no incluye —ni se parece demasiado— al
      de una franquicia existente.
- [ ] Todo personaje, logo y pieza de música es **creación propia** o tiene licencia verificada;
      nada «rippeado» de un juego real.
- [ ] Si el juego se inspira abiertamente en otra obra, la inspiración es de **mecánica y tono**,
      no de nombres ni de diseño visual reconocible (§1.2).
- [ ] Si hay parodia genuina, revisaste qué exige tu jurisdicción concreta (§1.4) — y recordaste
      que la excepción de parodia no cubre la marca (§1.1).
- [ ] Si mencionas una consola, un mando o un motor en tu ficha, es **texto descriptivo real**, no
      el logo oficial ni una frase que sugiera patrocinio (§4.2).
- [ ] Investigaste el historial concreto de ese titular con fan games —no asumas que «como Toby
      Fox lo permite, cualquiera lo permite» (§3.5).
- [ ] Si el proyecto se apoya en la tolerancia informal de un titular, sabes que **puede
      cambiar cualquier día** y tienes un plan si pasa.
- [ ] La música de tráileres y marketing tiene licencia explícita para **esa modalidad concreta**,
      no solo para «el juego» (§5).
- [ ] Sabes qué es una contranotificación DMCA y cuándo tendría sentido presentarla, si alguna
      vez te retiran contenido por error (§6.2).

---

## 8 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Cómo evitarlo |
|---|---|---|
| «Es gratis, así que no puede pasar nada» | Confundir «no lucrativo» con «legal» | AM2R y Pokémon Uranium eran gratuitos y fueron retirados igualmente (§3.1) — lo gratuito reduce el daño reclamable, no elimina la infracción |
| «Llevo años publicado sin que digan nada» | Confundir tolerancia con permiso | La tolerancia es revocable en cualquier momento, y a menudo se activa justo cuando el proyecto se vuelve visible (§1.3, §3.1) |
| «Solo copio la mecánica, no hay problema» — cuando en realidad también copia nombres y arte | Aplicar mal la distinción de §1.2: la mecánica es libre, la expresión no | Verifica por separado cada elemento: nombre, diseño visual, música, texto — no solo la mecánica de base |
| «Es una parodia, así que estoy protegido» sin comprobar la jurisdicción | Tratar la parodia como un escudo universal | Comprueba el test de tu jurisdicción (§1.4) y recuerda que ninguna excepción de parodia cubre la marca (§1.1) |
| Usar el logo oficial de una consola en el icono o la *capsule* «porque el juego funciona con ese mando» | Confundir compatibilidad real con licencia de marca | El uso nominativo permite el texto descriptivo, no el logo oficial sin licencia (§4.2) |
| Descargar música «libre de copyright» de un canal de YouTube y usarla también en el tráiler sin comprobar la licencia | Asumir que una licencia de «uso en vídeos» cubre cualquier plataforma o formato | Verifica que la licencia cubra explícitamente la modalidad exacta que vas a usar (§5) |

---

## Ver también

- [13 · 11 §8 — Plantillas para rellenar](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#8--plantillas-para-rellenar) y
  [§9 — Legal y administrativo mínimo](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#9--legal-y-administrativo-m%C3%ADnimo) —
  la plantilla de EULA (§8.6), la política de privacidad, COPPA/RGPD, la clasificación por edades
  y las licencias de GameMaker y de los assets
- [13 · 20 — Modelo de negocio, monetización y ética del diseño](./20%20-%20Modelo%20de%20negocio%2C%20monetizaci%C3%B3n%20y%20%C3%A9tica%20del%20dise%C3%B1o.md) —
  qué se vende y qué no, y las cajas de botín y su estado legal por país (§1.5), el otro frente
  legal de un juego pequeño
  · [26 · Comunidad propia](./26%20-%20Comunidad%20propia%20-%20Discord%2C%20moderaci%C3%B3n%20y%20gesti%C3%B3n%20de%20crisis.md) —
  qué hacer si la reclamación de un tercero se convierte en una crisis pública de comunidad
- [07 · 09 — Asset packs y recursos gráficos §1](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gr%C3%A1ficos.md) —
  la tabla de licencias de assets (CC0, CC-BY, fuentes tipográficas, contagio de GPL), el permiso
  que sí necesitas pedir antes de usar el trabajo de otra persona
- [05 · 05 — Entregar el juego: firmar, notarizar y subir a las tiendas](<../05 - Referencia/05 - Entregar el juego - firmar, notarizar y subir a las tiendas.md>) —
  el trámite técnico de publicación; este documento cubre el riesgo de contenido, no el de firma
- [13 · 14 — El documento de diseño](./14%20-%20El%20documento%20de%20dise%C3%B1o%20-%20del%20one-pager%20al%20GDD%20completo.md) —
  dónde declarar en el propio GDD si el juego se inspira en otra obra, y hasta qué punto

---

## Fuentes

Todas consultadas el **7 de septiembre de 2026**.

**Marca vs. derecho de autor**
- USPTO, *Protecting Your Trademark* — <https://www.uspto.gov/sites/default/files/BasicFacts_0.pdf>
- EUIPO, *Tipos de marcas* — <https://www.euipo.europa.eu/es/trade-marks/before-applying/types-of-trade-marks>

**Mecánicas de juego y derecho de autor**
- Loeb & Loeb, *Tetris Holding, LLC v. Xio Interactive, Inc.* — <https://www.loeb.com/en/insights/publications/2012/06/tetris-holding-llc-v-xio-interactive-inc>
- Wikipedia, *Tetris Holding, LLC v. Xio Interactive, Inc.* — <https://en.wikipedia.org/wiki/Tetris_Holding,_LLC_v._Xio_Interactive,_Inc.>

**Parodia por jurisdicción**
- Oficina de Copyright de EE. UU., resumen de *Campbell v. Acuff-Rose Music, Inc.* (1994) — <https://www.copyright.gov/fair-use/summaries/campbell-acuff-1994.pdf>
- EUR-Lex, sentencia *Deckmyn v. Vandersteen* (TJUE, C-201/13, 2014) — <https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX%3A62013CJ0201>
- Lexology, resumen de *Deckmyn v. Vandersteen* — <https://www.lexology.com/library/detail.aspx?g=bf1068a2-2a88-467f-b103-ffce3b55b729>
- BOE, Real Decreto Legislativo 1/1996 (Ley de Propiedad Intelectual), artículo 39 — <https://www.boe.es/buscar/act.php?id=BOE-A-1996-8930>

**Casos de fan games (§3)**
- Nintendo Life, *Nintendo of America Issues Takedown Request on AM2R, Ending the Project*, 02-09-2016 — <https://www.nintendolife.com/news/2016/09/nintendo_of_america_issues_takedown_request_on_am2r_ending_the_project>
- Wikipedia, *AM2R* — <https://en.wikipedia.org/wiki/AM2R>
- Slashdot, *Nintendo Shuts Down 'Pokemon Uranium' Fan Game After 1.5 Million Downloads*, 18-08-2016 — <https://games.slashdot.org/story/16/08/18/0047205/nintendo-shuts-down-pokemon-uranium-fan-game-after-15-million-downloads>
- PC Gamer, *GTA modding tool OpenIV shuts down due to cease and desist from Take-Two* — <https://www.pcgamer.com/gta-modding-tool-openiv-shuts-down-claiming-cease-and-desist-from-take-two/>
- bit-tech, *GTA modding tool OpenIV downed by cease and desist notification*, 15-06-2017 — <https://www.bit-tech.net/news/gaming/2017/06/15/gta-tool-openiv-downed/>
- PC Gamer, *Rockstar says you won't be banned for using GTA 5 single-player mods* — <https://www.pcgamer.com/rockstar-says-you-wont-be-banned-for-using-gta-5-single-player-mods/>
- Kotaku, *Fan-Made Streets Of Rage Remake Pulled After Request From Sega*, 11-04-2011 — <https://kotaku.com/fan-made-streets-of-rage-remake-pulled-after-request-fr-5791059>
- GamesRadar+, *Undertale's Toby Fox says fans should be "supported at every opportunity"...* — <https://www.gamesradar.com/undertales-toby-fox-says-fans-should-be-supported-at-every-opportunity-amid-debate-over-music-rights-in-fanmade-prequel/>
- Wizards of the Coast, *Fan Content Policy* — <https://company.wizards.com/en/legal/fancontentpolicy>

**Uso de marcas de terceros (§4)**
- Quimbee, resumen de *New Kids on the Block v. News America Publishing, Inc.* (1992) — <https://www.quimbee.com/cases/new-kids-on-the-block-v-news-america-publishing-inc>
- Studicata, resumen de *Sony Computer Entertainment America v. Bleem, LLC* (2000) — <https://www.studicata.com/case-briefs/case/sony-computer-entertainment-america-v-bleem>

**Música y samples (§5)**
- Wikipedia, *Bridgeport Music, Inc. v. Dimension Films* — <https://en.wikipedia.org/wiki/Bridgeport_Music,_Inc._v._Dimension_Films>

**DMCA: notificación y contranotificación (§6)**
- Cornell Law School, Legal Information Institute, 17 U.S. Code § 512 — <https://www.law.cornell.edu/uscode/text/17/512>
- Odin Law and Media, *The DMCA Process Explained for Game Developers* — <https://odinlaw.com/blog-dmca-process-for-game-developers/>
