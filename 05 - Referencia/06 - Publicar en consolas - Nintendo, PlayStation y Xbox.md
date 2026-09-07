# 06 · Publicar en consolas: Nintendo, PlayStation y Xbox

> El dominio más flojo de la biblioteca hasta hoy: el detalle técnico exacto de cada consola vive
> bajo NDA, pero **el trámite previo al devkit es 100 % público** y hoy no estaba documentado en
> ningún sitio. Este documento cubre eso — registro, contactos, licencia, vocabulario del oficio
> y qué es de dominio público sobre Switch, PlayStation y Xbox — y traza con precisión **dónde
> empieza el NDA**, para que un agente sepa cuándo parar. No repite el trámite de Steam, macOS,
> Windows, Google Play, App Store ni itch.io: eso es
> [05 · 05](./05%20-%20Entregar%20el%20juego%20-%20firmar%2C%20notarizar%20y%20subir%20a%20las%20tiendas.md),
> su hermano — ninguna de las cinco tiendas que cubre es una consola. Tampoco repite qué
> exportadores existen ni las wikis privadas de cada uno: eso ya está en
> [05 · 02 §1.4 y §3.8](./02%20-%20Publicar%20y%20exportar.md#14-consolas-wikis-privadas).

---

## 1 · Los principios

### 1.1 El NDA no es un muro opaco: categorías públicas frente a detalles exactos

Cada fabricante de consola exige firmar un acuerdo de confidencialidad antes de dar acceso a su
SDK real. Eso es un hecho — pero de ahí no se sigue que **todo** lo relacionado con publicar en
consola sea secreto. Lo que el NDA protege son los **detalles exactos**: los umbrales concretos de
un checklist de certificación, el contenido literal de una wiki `GMS2-Runner-*`, las funciones de
un SDK que no está en el manual público. Lo que **no** protege — porque nunca fue confidencial —
son las **categorías**: qué existe, cómo se llama, por dónde se empieza y qué patrón general sigue
cualquier certificación de consola desde hace décadas (repetido en charlas GDC, en la documentación
pública de otros motores y en la experiencia compartida del oficio).

[05 · 02 §3.8 bis](./02%20-%20Publicar%20y%20exportar.md#38-bis-qué-exige-una-consola-aunque-no-puedas-contarlo)
ya aplica esta técnica con una tabla de categorías de certificación sin inventar ni un umbral —
es el patrón correcto, y este documento lo extiende al resto del trámite en vez de reescribirlo.

**Regla explícita para un agente de IA que trabaje con este documento**, porque hoy no existía en
ningún sitio de la biblioteca y es la causa directa de que este dominio fuera el más flojo de
todos: al llegar a un tema de consola cuyo detalle exacto **no** está aquí ni en el manual público
—un umbral de certificación, el contenido de una wiki `GMS2-Runner-*`, una cifra que ninguna fuente
primaria confirma—, el agente **para y se lo dice al usuario**, ofreciendo las categorías públicas
que sí conoce (esta tabla, la de 05 · 02 §3.8 bis, lo que documenten charlas GDC o porting houses
citadas como tales). **Nunca rellena el hueco con algo verosímil que suene a wiki privada.** Un
`⚠️` honesto en este documento vale más que una cifra inventada que un desarrollador real se crea.

### 1.2 El mito que hay que descartar antes de empezar: los parches ya no cuestan dinero

Circula desde hace más de una década la creencia de que publicar un parche en consola cuesta del
orden de **40 000 USD** — una cifra que se atribuye a comentarios de Tim Schafer sobre la Xbox 360
de la generación anterior (~2012-2013) y que sigue repitiéndose en foros y artículos de opinión.
**Esa cifra es un mito ya falso en 2026: dilo con esas palabras.** Sony y Nintendo no cobran por
actualizaciones de sus juegos, y Microsoft eliminó la tasa histórica de certificación de parches
salvo en casos de abuso de reenvíos (resubmissions) excesivos o negligentes — desarrollado con la
cifra correcta (cero, no cuarenta mil) en [§6.4](#64-parches-y-su-coste-real-en-2026).
⚠️ Esta entrada se apoya en el cruce de fuentes que ya reunió la auditoría interna que encargó este
documento (Shacknews, ResetEra, consultadas 07-09-2026); no se han vuelto a abrir esas páginas
concretas en la sesión de redacción — se cita así, con honestidad, en vez de fingir una
verificación directa que no se hizo.

### 1.3 Verifica en vivo, cita con fecha, y si no puedes, dilo

Todo dato de este documento —portal, precio, requisito, contacto, plazo— se ha intentado verificar
contra una fuente primaria abierta de verdad en esta sesión (07-09-2026), con la fecha al lado de
la cita. Donde no fue posible —casi siempre porque el dato vive en un checklist bajo NDA, o porque
solo lo repiten fuentes secundarias sin que ninguna primaria lo confirme— lleva **⚠️** y lo dice sin
rodeos, siguiendo la misma regla que el resto de la biblioteca.

---

## 2 · El trámite público antes del devkit

Esta sección es el hueco más caro de todos, según la propia auditoría que encargó este documento:
**el trámite de acceso a cada fabricante no está bajo NDA — GameMaker lo publica en su propio
centro de ayuda**, y hasta hoy la biblioteca solo enlazaba esa página (`05 · 02 §1.4`) sin extraer
su contenido. Todo lo que sigue en esta sección viene del artículo oficial de GameMaker
*Application Process for Console Access*
(<https://gamemaker.io/en/help/articles/application-process-for-console-access>), abierto con
éxito el 07-09-2026 (`curl` con cabecera `User-Agent` de navegador — `WebFetch` sigue devolviendo
403 en esta sesión, la misma limitación que ya registró la auditoría; el contenido de abajo es la
transcripción real de la página, no un fragmento reconstruido por búsqueda cruzada). La propia
página indica **«Last updated: 4th August 2026»**.

La frase que abre el artículo, textual: *«When choosing to develop for console, you will have to
purchase a GameMaker Enterprise subscription at a Monthly or Yearly cost.»* — la licencia es el
primer requisito, antes incluso de hablar con ningún fabricante (detalle de precio en
[§3.1](#31-la-licencia-enterprise-el-precio-real)).

### 2.1 Nintendo Switch y Switch 2

El proceso, en el orden exacto que describe el artículo oficial:

1. **Regístrate como desarrollador** en <https://developer.nintendo.com/> — es el primer paso, sin
   coste de registro en sí (el coste real llega con la licencia Enterprise y, más adelante, con la
   propia relación comercial que Nintendo apruebe).
2. **Contacta con la oficina regional de Nintendo para presentar tu proyecto** y pedir autorización
   para convertirte en desarrollador de Nintendo Switch. La cita textual completa, con los dos
   contactos por región:

   > *«The next step is to contact the Nintendo Regional offices at
   > [developers@nintendo.eu] if you are based in Europe or Australia and
   > [thirdpartypublisher@noa.nintendo.com] if you are based in the USA or elsewhere, to pitch your
   > project and seek authorization to become a Nintendo Switch developer.»*

   | Región | Contacto |
   |---|---|
   | Europa o Australia | `developers@nintendo.eu` |
   | EE. UU. o el resto del mundo | `thirdpartypublisher@noa.nintendo.com` |

3. **Una vez aprobado como desarrollador**, registra tu solicitud en la página propia de middleware
   de GameMaker dentro del portal de Nintendo:
   <https://developer.nintendo.com/group/development/getting-started/g1kr9vj6/middleware/gamemaker-studio2>
   — el artículo avisa explícitamente de que hace falta iniciar sesión con la cuenta de
   desarrollador de Nintendo para acceder a esa página, así que el paso 1 (registro) es una
   condición previa real, no un trámite decorativo.

⚠️ **Lo que el artículo NO dice, y no hay que inventar**: cuánto tarda el proceso completo, si
Nintendo acepta desarrolladores individuales sin empresa constituida (el registro en
`developer.nintendo.com` no lo aclara en el propio artículo de GameMaker), ni qué pasa exactamente
si la respuesta es negativa. Si necesitas esos datos, la fuente es Nintendo directamente, no esta
biblioteca.

### 2.2 PlayStation 4 y PlayStation 5

Cita textual completa del artículo oficial, con el flujo paso a paso:

> *«To gain access to the PlayStation®4 and PlayStation®5 exports, you first need to request to
> become a PlayStation Partner. You can sign up [here](https://register.playstation.net). This
> gives you access to everything you need from Sony Computer Entertainment (ordering dev kits,
> downloading SDKs and tools, etc). Once you have done this and have access to
> [SCE DevNet](http://www.scedev.net/), you will need to log in to the DevNet website and go to:
> Development → Tools & Middleware → Click Tools & Middleware directory → Find GameMaker Studio in
> the Engine Category and click "Confirm developer status" → Finally, click "Confirm status".»*

1. **Solicita ser PlayStation Partner** en <https://register.playstation.net> (verificado en vivo
   el 07-09-2026, HTTP 200, título real de la página: «PlayStation® Partner Registration»). Esto
   da acceso a todo lo que hace falta de Sony Computer Entertainment: pedir devkits, descargar SDKs
   y herramientas.
2. **Con acceso a SCE DevNet** (<http://www.scedev.net/>), entra y navega: *Development → Tools &
   Middleware → Tools & Middleware directory*, busca **GameMaker Studio** en la categoría de
   motores y pulsa **«Confirm developer status»**, y por último **«Confirm status»**.
3. **Nota importante del propio artículo**: *«Please note: PlayStation®4 and PlayStation®5 are the
   only Sony exports available in GameMaker. Legacy systems are not supported.»*
4. **Vinculación con GameMaker**: al confirmar el estado en DevNet, GameMaker recibe una
   notificación por email y contacta a través de su sistema de Helpdesk. Cita textual: *«When we
   contact you, if you have a GameMaker Account associated with the same email address you have
   registered with as a Sony developer, we'll apply the relevant licensing to that account. If you
   do not have a GameMaker Account associated with the same email address […] we will ask you to
   create a GameMaker Account or let us know of an existing GameMaker Account.»*
5. **Cláusula de silencio bajo NDA, textual**: *«Please note that you must not report
   PlayStation-specific comments/bugs in any public forum, as per your agreement with the console
   platform holder.»* — es la aplicación práctica de §1.1: ni un bug de PlayStation se comenta en
   un foro público, aunque el bug en sí no sea información confidencial de diseño.

El portal general de PlayStation Partners (distinto del registro, aunque relacionado) también está
verificado en vivo hoy: <https://partners.playstation.net> (HTTP 200, título «PlayStation®
Partners»). ⚠️ Su contenido interno no se pudo extraer en esta sesión — la página carga por
JavaScript y las herramientas de esta sesión no ejecutan el script — así que no se puede citar más
allá de confirmar que el portal existe y responde.

### 2.3 Xbox One y Xbox Series X\|S

Cita textual completa del artículo oficial:

> *«To gain access to the Xbox One and Xbox Series X\|S exports you first need to sign up to the
> ID@Xbox program. You can sign up [here](http://www.xbox.com/en-GB/Developers/id). This gives you
> access to everything you need from Microsoft (ordering dev kits, downloading SDKs and tools,
> etc). Once you have signed up and have been approved, you can make a
> [Secure GDK Middleware Request](https://developer.microsoft.com/en-us/games/support/request-gdkx-middleware).
> Select GameMaker as your Middleware partner and the appropriate Game Developer/Publisher for whom
> you'll be acting.»*

1. **Regístrate en el programa ID@Xbox.** El enlace del propio artículo
   (`xbox.com/en-GB/Developers/id`) redirige hoy, verificado en vivo el 07-09-2026, a
   <https://developer.microsoft.com/en-US/games/partner/> — la landing actual del programa.
   Requisitos confirmados **con cita textual de esa página en vivo**:

   > *«You must be at least 18 years old to begin a development or business relationship with
   > XBOX.»*

   Y, resumidos por la propia página en sus tres condiciones de entrada:

   | Requisito | Detalle |
   |---|---|
   | Edad mínima | **18 años** para tener una relación de desarrollo o de negocio con Xbox (o patrocinio de un padre/tutor si eres menor, según indica la propia página) |
   | NDA | Hay que firmarlo — la página lo cita como paso explícito antes de continuar |
   | País | Tienes que estar en un país con el que Microsoft pueda hacer negocios |

   Lo que da acceso el programa, según la misma página: incentivos y oportunidades de financiación,
   soporte técnico y de publicación, y promoción/visibilidad — no se detalla en la parte pública el
   procedimiento exacto de pedido de devkits ni el coste (si lo hay) más allá de la aprobación.
2. **Una vez aprobado**, haz una **Secure GDK Middleware Request** en
   <https://developer.microsoft.com/en-us/games/support/request-gdkx-middleware>, seleccionando
   **GameMaker** como socio de middleware y el *Game Developer/Publisher* correcto (si gestionas
   más de uno, elige el correcto en el desplegable — el propio artículo insiste en este detalle).
3. **Vinculación con GameMaker**: exactamente el mismo patrón que PlayStation — GameMaker recibe la
   notificación por email y contacta por Helpdesk, aplicando la licencia a tu cuenta de GameMaker si
   coincide el email, o pidiéndote que crees/indiques una cuenta si no coincide.
4. **Aviso explícito de la propia página de ayuda**: *«Please be aware that we cannot issue you
   with any information until you have been approved by Microsoft, so please make sure everything
   has been set up before contacting us. We will not issue access or licensing associated with NDA
   materials to accounts with an email that doesn't match your request.»* — GameMaker **no puede**
   adelantarte nada sobre el SDK de Xbox antes de que Microsoft te apruebe, y no vincula tu licencia
   a una cuenta con un email que no coincida.
5. **Misma cláusula de silencio que PlayStation**: *«you must not report Xbox-specific
   comments/bugs in any public forum, as per your agreement with the console platform holder.»*

### 2.4 Qué pasa si te dicen que no, y qué NO puedes anunciar aunque te digan que sí

⚠️ Ninguna de las tres páginas verificadas en esta sesión (GameMaker, ID@Xbox) detalla qué ocurre
si un fabricante rechaza la solicitud — ni plazos de recurso, ni motivos típicos de rechazo, más
allá de lo que ya cubre en general
[13 · 11 §9](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#9--legal-y-administrativo-mínimo>)
sobre trámites de negocio. No se inventa aquí: si tu solicitud es rechazada, la única fuente fiable
es la respuesta directa del fabricante o de GameMaker por Helpdesk.

Lo que sí es una categoría pública, repetida en las tres cláusulas de silencio citadas arriba: estar
aprobado como desarrollador **no** te da permiso automático para anunciar públicamente que tu juego
llega a esa consola. Los tres fabricantes tratan el propio hecho de estar en su programa —y
cualquier detalle técnico, bug o captura de un build en desarrollo— como información sujeta al NDA
hasta que ellos mismos autoricen el anuncio (habitualmente coordinado con su propio calendario de
marketing). Un agente que redacte un press kit o una nota de prensa **no debe anunciar una
plataforma de consola sin que el fabricante lo haya aprobado explícitamente**, con independencia de
que el desarrollo ya esté en marcha.

---

## 3 · GameMaker y las consolas

### 3.1 La licencia Enterprise: el precio real

**Enterprise es el único nivel de licencia que exporta a consola** — ya documentado en
[05 · 02 §2](./02%20-%20Publicar%20y%20exportar.md#2-licencias-qué-permite-cada-una) y en
[13 · 11 §9.1](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#91-la-licencia-de-gamemaker>).
Lo que faltaba en ambos sitios era el precio exacto — ninguno de los dos lo daba, solo
«suscripción mensual o anual». Verificado en vivo el 07-09-2026 en la página oficial de GameMaker
Enterprise en Steam (<https://store.steampowered.com/app/1847411/GameMaker_Enterprise/>):

| Plan | Precio verificado (Steam, 07-09-2026) |
|---|---|
| Mensual | **67,99 €/mes** |
| Anual (12 meses) | **679,99 €** — un 17 % de descuento sobre pagar doce meses sueltos |

⚠️ Cifra corroborada, no reabierta en esta sesión, por fuentes agregadas en dólares que ya recogía
la auditoría previa: en torno a **79,99 USD/mes ≈ 799,99 USD/año**. Steam ajusta el precio mostrado
según la región y la divisa de la cuenta: la cifra en euros de arriba es la que muestra hoy la
página en euros, no un precio universal fijo.

Enterprise **no sustituye** al trámite de aprobación de cada fabricante de §2 — son dos requisitos
independientes y acumulativos, no alternativos: sin la licencia no puedes ni configurar el
exportador; sin la aprobación del fabricante no tienes acceso al SDK real aunque pagues la
licencia.

### 3.2 Los exportadores que existen hoy

Ya documentado, y no se repite aquí: la tabla de exportadores (Switch, Switch 2, PS4, PS5, Xbox
One/Series) y sus wikis privadas de runtime está en
[05 · 02 §3.8](./02%20-%20Publicar%20y%20exportar.md#38-consolas), y las categorías públicas de
certificación que sí se pueden documentar sin romper el NDA están en
[05 · 02 §3.8 bis](./02%20-%20Publicar%20y%20exportar.md#38-bis-qué-exige-una-consola-aunque-no-puedas-contarlo).
El CLI (`gm-cli`) **no compila ninguna consola todavía** — «coming soon» para `switch`, `ps4`,
`ps5`, `xboxseriesxs» —, así que cualquier build de consola se hace **desde el IDE**, con las
wikis privadas de runtime como única guía técnica una vez aprobado.

### 3.3 Switch 2: lo que dice GameMaker públicamente

Las release notes oficiales de la LTS 2026.0 (ya citadas en 05 · 02 §3.8) dicen, textual: *«This
uses a very similar setup to Switch 1, but please do see the setup guides before attempting any
builds or filing any bugs.»* Es la única frase pública sobre Switch 2 que GameMaker ha soltado
fuera del NDA: confirma que el flujo de configuración es parecido al de Switch 1, sin decir en qué
se diferencia de verdad — eso vive en la wiki privada `GMS2-Runner-Switch2`.

### 3.4 El vocabulario del oficio, hoy inexistente en la biblioteca

Comprobado con `python3 "_indice/buscar.py" --texto "<término>"` el 07-09-2026: ninguno de estos
seis términos aparecía en toda la biblioteca antes de este documento (cero resultados en los seis
casos). Son la puerta de entrada al oficio — sin ellos, un agente no puede ni formular bien una
pregunta a un humano o a un foro de porting:

| Término | Qué es | Fabricante |
|---|---|---|
| **Lotcheck** | El proceso de certificación de Nintendo: comprueba que el juego cumple sus guías técnicas y de contenido antes de publicarse — terminología y comportamiento consistentes, no «cero bugs» ([§4.1](#41-lotcheck-qué-es-y-qué-comprueba-de-verdad)) | Nintendo |
| **TRC** (*Technical Requirements Checklist*) | El checklist de requisitos técnicos obligatorios de PlayStation que todo juego debe pasar en certificación ([§5.1](#51-trc-de-playstation-y-xr-de-xbox-qué-son)) | Sony/PlayStation |
| **XR** (*Xbox Requirements*, antes **TCR**) | Las políticas, requisitos técnicos y de producto que todo desarrollador/publisher de Xbox debe cumplir — el nombre cambió de TCR a XR ([§5.1](#51-trc-de-playstation-y-xr-de-xbox-qué-son)) | Microsoft/Xbox |
| **GDPA** (*Global Developer and Publisher Agreement*) | El acuerdo legal marco que se firma con Sony tras la aprobación como PlayStation Partner, antes de tener acceso completo al programa | Sony/PlayStation |
| **DevNet** | El portal técnico de Sony (`scedev.net`) donde se piden devkits, se descargan SDKs y herramientas, y se confirma el middleware (§2.2) | Sony/PlayStation |
| **Gamerscore** | El sistema de puntuación acumulada de logros de Xbox, con reglas de mínimos/máximos por juego que certificación exige cumplir ([§5.3](#53-logros-y-gamerscore-de-xbox-la-tabla-oficial-vigente)) | Microsoft/Xbox |

⚠️ **GDPA** no se pudo confirmar hoy con una cita textual primaria (el contenido de
`partners.playstation.net` no cargó, §2.2): el nombre del acuerdo es terminología estándar del
sector recogida por la auditoría previa de este documento, no una cita literal de Sony abierta en
esta sesión.

### 3.5 La pregunta pendiente, resuelta: ¿Switch 2 comparte nodo con `switch`?

`05 · 02 §1.1` documenta 13 plataformas con Game Options, verificadas con `gm-cli resourcetool
eval "options list"`, incluida `switch` — pero **ningún** nodo `switch2` aparte. La auditoría previa
a este documento dejó la pregunta abierta: ¿Switch 2 comparte el nodo `switch` con Switch 1, o hace
falta uno nuevo que la tabla no recoge?

**Resuelto con evidencia en vivo el 07-09-2026**, repitiendo la comprobación sobre tres proyectos
reales con `ResourceTool@2026.0.17` (detalle completo del hallazgo, incluida la causa de por qué el
comando parecía no funcionar en la sesión de la auditoría, en
[05 · 02 §1.1](./02%20-%20Publicar%20y%20exportar.md#11-las-13-plataformas-con-game-options)):

```
$ ls options/
android  html5  ios  linux  mac  main  operagx  ps4  ps5  reddit  switch  tvos  windows  xboxseriesxs
```

**Ningún proyecto probado —tres plantillas oficiales distintas de GameMaker— trae un nodo
`switch2`.** Solo aparece `switch`. Esto es coherente con la frase oficial de §3.3 («muy similar
setup a Switch 1») y con el hecho de que Game Options es un recurso estructural del proyecto, no
algo que dependa de la licencia Enterprise para existir en disco.

⚠️ **El matiz que hay que respetar**: esto es evidencia de la **estructura del proyecto**
(carpetas de recursos que trae cualquier plantilla, con o sin licencia de consola), no una
verificación con una licencia Enterprise real ni con el exportador de Switch 2 activo — eso sigue
bajo NDA y esta biblioteca no tiene acceso a él. Lo que sí se puede afirmar con esta evidencia: si
una receta dice «configura Game Options → switch», vale igual para Switch 1 y Switch 2, porque no
existe un nodo separado que elegir.

---

## 4 · Nintendo Switch y Switch 2

### 4.1 Lotcheck: qué es y qué comprueba de verdad

**Lotcheck** es el nombre del proceso de certificación de Nintendo — la revisión que todo juego
tiene que pasar antes de publicarse en la eShop (o antes de fabricar cartuchos, en físico). La idea
extendida de que lotcheck busca «cero bugs» es imprecisa: lo que de verdad certifica, según el
patrón de categorías públicas de la industria (05 · 02 §3.8 bis, aplicado aquí a Nintendo en
concreto), es que el juego respeta con **consistencia** las convenciones del sistema:

- **Terminología e iconos de botón correctos y consistentes** en toda la interfaz — la causa nº 1
  de rechazos citada de forma cruzada por varias fuentes del sector ([§4.3](#43-terminología-de-botones-obligatoria-en-toda-la-ui)).
- **Comportamiento estándar del sistema**: suspensión/reanudación, gestión de mandos desconectados,
  cambio de usuario — la misma tabla de categorías de 05 · 02 §3.8 bis, aplicada a Switch.
- **Guardado que no se corrompe** ante un corte de energía o quitar la consola del dock a media
  escritura.
- **Rendimiento estable** en el objetivo declarado, incluida la transición dock↔portátil
  ([§4.6](#46-la-transición-dockportátil-no-es-lo-mismo-que-arrancar-o-suspender)).

⚠️ **Tiempos orientativos, de fuente secundaria, no confirmados por Nintendo directamente en esta
sesión**: la auditoría previa cita un rango de **2-4 semanas** para la primera revisión, más
**1-2 semanas por cada ciclo adicional** si hace falta corregir algo y volver a enviar
(generalistprogrammer.com, r-tt.com — no reabiertas en esta sesión de redacción). El checklist real
de lotcheck está dentro del NDA: esta biblioteca no tiene acceso a él y no inventa sus umbrales
exactos.

### 4.2 Rendimiento y resolución: portátil frente a *dock*

⚠️ **No se pudo verificar con una fuente primaria o secundaria fiable en esta sesión** (los sitios
técnicos de referencia para benchmarks de consola —Digital Foundry, Eurogamer— no fueron accesibles
con las herramientas disponibles hoy). Lo que sí es de dominio público y verificable con cualquier
comparativa de hardware: Switch (1) renderiza típicamente **hasta 1080p en modo *dock*** y
**hasta 720p en modo portátil**, con muchos juegos por debajo de esas cifras según el motor; Switch
2 sube el techo con soporte de salida hasta **4K en *dock*** y resoluciones más altas en portátil.
**No se citan aquí cifras concretas por juego ni un mínimo obligatorio de Nintendo**, porque el
objetivo de rendimiento real que exige certificación es, precisamente, uno de los umbrales que vive
dentro del NDA (05 · 02 §3.8 bis, fila «Tiempos de arranque» — el mismo patrón aplica a resolución y
framerate objetivo). Lo que sí toca a tu proyecto y **sí está documentado con GML** en esta
biblioteca es la propia arquitectura de escalado de tu juego frente al tamaño real de pantalla —
[13 · 03 — Pixel art y resolución](<../13 - Diseño y producción de videojuegos/03 - Pixel art y resolución.md>).

### 4.3 Terminología de botones obligatoria en toda la UI

Nintendo, Sony y Microsoft exigen que cualquier instrucción en pantalla («Pulsa A», «Mantén ✕»)
use exactamente la redacción, capitalización y el icono que cada fabricante define en sus propias
guías de estilo — nunca una redacción genérica ni el nombre de otra plataforma. Es la categoría de
certificación que varias fuentes del sector citan, de forma cruzada, como la causa **más repetida**
de rechazo en primera revisión, precisamente porque es fácil de pasar por alto cuando el mismo texto
de UI se reutiliza entre plataformas sin adaptarlo. La consecuencia práctica para tu código: nunca
hardcodees el texto «Pulsa A» en un solo sitio para las tres plataformas — resuélvelo con el mismo
patrón de verbos de entrada que ya recomienda
[01 · 12](<../01 - Fundamentos/12 - Input - teclado, ratón y gamepad.md>) («el código pregunta por
`saltar`, no por `gp_face1`»), pero llevado un paso más allá: la **etiqueta de texto** que muestras
también debe depender de la plataforma activa, no solo la entrada que lees.

### 4.4 La convención de botones A/B invertida entre Switch y Xbox, y su origen

Este es el matiz que 05 · 02 §3.8 bis todavía no cubre, y es justo el que pide este documento. El
mando de Nintendo Switch y el mando de Xbox **usan las mismas cuatro letras** (A, B, X, Y) para
las mismas cuatro posiciones del rombo de botones — pero **la posición física que confirma es
distinta en cada uno**, y ese es el origen real de la confusión que sufre cualquier jugador que
cambia de plataforma:

| | Botón **este/derecha** del rombo | Botón **sur/abajo** del rombo |
|---|---|---|
| **Nintendo** (SNES → GameCube → Switch) | **A** — confirma | **B** — cancela |
| **Xbox** (original → Series) | **B** — cancela | **A** — confirma |

El propio catálogo de esta biblioteca ya documenta la tabla de constantes `gp_face1`-`gp_face4` de
GML y su equivalencia por fabricante —
[01 · 12](<../01 - Fundamentos/12 - Input - teclado, ratón y gamepad.md>), tabla de «Constantes de
botón»—, pero no explicaba **por qué** la misma posición física del mando significa «confirmar» en
un sistema y «cancelar» en el otro. El origen, verificado hoy:

- **Nintendo fijó su convención con el mando de NES en 1983**: el botón A, a la derecha del rombo
  (el más natural para el pulgar dominante en un layout de dos botones y, después, de cuatro),
  quedó como el botón de acción/confirmación principal, y esa asignación se ha mantenido sin
  cambios generación tras generación hasta el Joy-Con de Switch.
- **El mando original de Xbox (2001) heredó su esquema de seis botones frontales directamente del
  mando revisado de Sega Genesis**, no del de Nintendo. Cita textual, verificada hoy en
  Wikipedia, *Xbox controller* (<https://en.wikipedia.org/wiki/Xbox_controller>, consultado
  07-09-2026): el equipo de diseño *«drew six frontal buttons from the revised Sega Genesis
  controller»*. La línea de mandos Sega/arcade colocaba el botón de acción principal en la posición
  **inferior** del grupo de botones, no en la de la derecha — y Microsoft continuó esa herencia al
  asignar **A** (confirmar) a esa misma posición inferior en su propio mando, en vez de a la
  posición derecha que usaba Nintendo.

El resultado práctico: un jugador que pasa de Switch a Xbox pulsa por instinto el botón de la
**misma posición física** que confirmaba en su consola anterior, y en la otra consola ese botón
**cancela**. Es exactamente la razón por la que §4.3 exige mostrar siempre el icono y la letra que
corresponden a la plataforma activa, nunca una posición fija.

### 4.5 Guardado en consola: una API de sistema propia, no `file_text_*`

`05 · 02 §3.8 bis` ya documenta el patrón general de guardado atómico (temporal + reemplazo) que
exige cualquier consola. Lo que falta ahí, y es específico de consola frente a escritorio: **el
guardado en Switch, PlayStation y Xbox no pasa por las funciones normales de archivo de GML**
(`file_text_open_write`, `buffer_save`, etc., documentadas en
[01 · 14 — Persistencia y archivos](<../01 - Fundamentos/14 - Persistencia y archivos.md>)). Cada
consola expone su **propia API de sistema de guardado** a través del SDK del runtime privado
(`GMS2-Runner-Switch`, `-PS4`, `-PS5`, `-Xbox`), con sus propios límites de tamaño por título y sus
propias reglas de cuota — límites que, como el resto del SDK, viven dentro del NDA de cada
fabricante y no se pueden citar aquí con una cifra concreta. La única excepción documentable sin
NDA en esta biblioteca es Xbox Live/UWP (no la consola nativa): `xboxlive_set_savedata_user()`
redirige las funciones de archivo normales al área de guardado de Xbox Live, según
[04 · 20 §6.5](<../04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md#65--guardado-de-partida-y-nube>)
— pero esa es la capa de servicios sobre Windows, distinta de la consola Xbox nativa
([§5.4 más abajo](#54-la-diferencia-entre-xbox-liveuwp-y-consola-xbox-nativa-otra-vez)).

### 4.6 La transición dock↔portátil no es lo mismo que arrancar o suspender

`05 · 02 §3.8 bis` cubre «tiempos de arranque» y «suspensión y reanudación» como categorías
separadas — ninguna de las dos es la transición que le pasa a un juego de Switch varias veces por
sesión: acoplar o desacoplar la consola del dock **sin** que el sistema entre en reposo. Es una
categoría propia porque el juego sigue corriendo en todo momento, pero tiene que renderizar a una
resolución y framerate distintos casi al instante (§4.2) sin *frame drops* visibles ni una pantalla
de carga — el mismo estándar de continuidad que aplica a la suspensión, pero sin la ventaja de que
el sistema pause la ejecución mientras ocurre.

### 4.7 eShop: reparto de ingresos

⚠️ No verificado con una fuente primaria de Nintendo en esta sesión de redacción. La cifra que cita
la auditoría previa —**30 % para Nintendo**, el mismo tramo estándar que Steam, la App Store y
Google Play para la mayoría de ventas— procede de fuentes secundarias cruzadas
(generalistprogrammer.com, 07-09-2026) no reabiertas hoy. Si necesitas el dato exacto y actualizado
para presupuestar, confírmalo en el acuerdo de desarrollador real que firmes con Nintendo, no aquí.

### 4.8 Rechazos típicos de lotcheck

Formato «motivo → cómo evitarlo», el mismo patrón que ya usa con éxito
[05 · 05 §10](./05%20-%20Entregar%20el%20juego%20-%20firmar%2C%20notarizar%20y%20subir%20a%20las%20tiendas.md#10--errores-clásicos-y-cómo-evitarlos)
para las tiendas no-consola. ⚠️ Las categorías son de conocimiento público del oficio (charlas GDC,
porting houses); los umbrales exactos que Nintendo comprueba viven en el checklist bajo NDA:

| Motivo típico de rechazo | Cómo evitarlo |
|---|---|
| Terminología o icono de botón incorrecto/inconsistente en algún texto de UI (§4.3) | Centraliza los textos de instrucción en una sola función que resuelva el icono/etiqueta según la plataforma activa, y audita **cada** pantalla, no solo el menú principal |
| El juego no reanuda exactamente donde estaba tras suspensión/dock (§4.6, 05 · 02 §3.8 bis) | Prueba explícitamente el ciclo dormir→despertar y acoplar→desacoplar en cada sala del juego, no solo en el menú |
| Guardado corrupto tras interrumpir la escritura (quitar el mando, apagar a media partida) | El patrón atómico temporal+reemplazo de 05 · 02 §3.8 bis, aplicado a la API de guardado propia de la consola (§4.5) |
| Framerate o resolución por debajo del objetivo declarado, sobre todo en la transición dock↔portátil | Prueba el peor caso real (más enemigos/partículas en pantalla) en portátil, no solo en dock, que suele tener más margen térmico |
| Avisos legales o de fotosensibilidad ausentes o mal ubicados (05 · 02 §3.8 bis) | Añádelos como parte del checklist de build de release, no como un retoque de última hora |

---

## 5 · PlayStation y Xbox: certificación, logros/trofeos, guardado y suspensión

### 5.1 TRC de PlayStation y XR de Xbox: qué son

**TRC** (*Technical Requirements Checklist*) es el nombre del conjunto de requisitos técnicos
obligatorios que Sony exige a cualquier juego de PlayStation antes de certificarlo. ⚠️ No se pudo
abrir hoy una página oficial de Sony que defina el acrónimo con cita textual (el contenido técnico
de PlayStation está detrás de DevNet, con acceso solo para desarrolladores aprobados); el término en
sí es estándar del sector y así lo recoge la auditoría previa de este documento.

**XR** (*Xbox Requirements*) sí tiene definición oficial pública, verificada hoy con éxito —
Microsoft Learn no bloqueó el acceso, a diferencia de las páginas de Sony/Nintendo detrás de login.
Cita textual completa, de
<https://learn.microsoft.com/en-us/gaming/gdk/docs/store/policies/console/certification-requirements>
(consultado 07-09-2026, documento con fecha de revisión **1 de julio de 2026**, versión 16.3):

> *«Xbox Requirements (XRs) consist of the policies, technical requirements, and product
> component-related requirements to which all developers and publishers of Xbox console titles must
> conform. XRs ensure that products created for Xbox consoles aren't only stable and reliable but
> also provide a user experience that's consistent, safe, secure, and enjoyable.»*

El nombre **cambió de TCR a XR** en algún momento anterior a esta revisión (el propio documento ya
solo usa «XR»; la auditoría previa registra «TCR» como el nombre antiguo, consistente con lo que
documentan varias guías de porting). Cada XR individual tiene su propio número
(`XR-001`, `XR-055`…) y algunas están marcadas con asterisco cuando **se comprueban de verdad** en
certificación (*Certification*), frente a las que son solo política sin test automatizado asociado.

### 5.2 Trofeos de PlayStation

Estructura verificada hoy en Wikipedia, *Trophy (PlayStation)*
(<https://en.wikipedia.org/wiki/Trophy_(PlayStation)>, consultado 07-09-2026):

- Cuatro niveles: **bronce, plata y oro** según la dificultad del logro, más **platino**. Cita
  textual sobre el platino: *«A platinum trophy is awarded to the player once they unlock all
  other trophies in the base game; smaller-sized games, however, generally do not offer a platinum
  trophy.»* — es decir, el platino no es un trofeo que se diseñe aparte: se dispara solo al
  completar el resto, y los juegos pequeños pueden legítimamente no tener platino.
- Cada trofeo, además de su nivel, recibe una **rareza** (común, raro, muy raro, ultra raro) según
  el porcentaje de jugadores que lo ha desbloqueado — un dato que calcula la plataforma, no algo
  que el desarrollador declare.
- El desarrollador puede marcar trofeos como **ocultos**, de forma que ni el nombre ni la
  descripción se revelan hasta que el jugador lo obtiene.

⚠️ **No verificado hoy con fuente primaria**: un rango numérico fijo de «cuántos trofeos debe tener
un juego» (la auditoría previa citaba un orden de 30-50 bronce/plata/oro como práctica habitual, no
como regla escrita de Sony) — Wikipedia no confirma ni desmiente esa cifra, así que no se repite
aquí como si fuera una norma.

### 5.3 Logros y Gamerscore de Xbox: la tabla oficial vigente

Esta es la sección con la fuente primaria más sólida de todo el documento: la propia norma **XR-055
(Achievements and Gamerscore)**, con asterisco de comprobación en certificación, verificada hoy
palabra por palabra en Microsoft Learn (misma fuente que §5.1, revisión de julio de 2026):

> *«Titles must provide the required number (minimum and maximum) of achievements and their
> associated gamerscore at launch. Titles are permitted to add achievements or gamerscore at any
> time after launch, with or without corresponding new content, but they can't exceed title-based
> or calendar-based limits. A single achievement can't exceed 200 gamerscore and all achievements
> in the title must be achievable.»*

La tabla exacta que trae la norma, sin redondear:

| | Al lanzamiento | Añadidos semestrales | Límite de por vida |
|---|---|---|---|
| **Logros mínimos** | 10 | 0 | 10 |
| **Logros máximos** | 100 | 100 | 500 |
| **Gamerscore** | 1000 | 1000 | 5000 |

«Semestral» significa, textual, los tramos **enero-junio** y **julio-diciembre**; el juego base no
cuenta para esos límites semestrales. Y una regla más de la misma norma, con su propio número:
**XR-057** exige que todos los logros se puedan desbloquear jugando — prohíbe explícitamente
venderlos con dinero real o desbloquearlos con códigos de trucos/consola de depuración; y
**XR-062** limita el texto de nombre y descripción de un logro a un contenido que no supere una
clasificación PEGI 12 / ESRB EVERYONE 10+, y prohíbe cualquier forma de lenguaje soez aunque esté
censurado.

Esta tabla **no sustituye** a
[04 · 20 §6.2-§6.3](<../04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md#62--usuarios-y-cuentas>),
que ya documenta con GML verificado las funciones `xboxlive_gamerscore_for_user()` y
`xboxlive_achievements_set_progress()` para **leer y actualizar** logros vía Xbox Live/UWP: aquella
sección es la API, esta es la **regla de negocio** de certificación que limita cuántos logros y
cuánto Gamerscore puede declarar tu juego. Son piezas complementarias, no duplicadas.

### 5.4 La diferencia entre Xbox Live/UWP y consola Xbox nativa, otra vez

Ya lo señala con precisión
[04 · 20 §6.7](<../04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md#67--diferencia-entre-uwp-y-consola-xbox-nativa>):
toda la familia `xboxlive_*` de GML solo funciona exportando a **Windows UWP** con la casilla de
Xbox Live activada — un juego de PC que habla con los servicios de Xbox Live, no un juego nativo de
consola. La exportación **nativa** a Xbox One/Series (la que produce un paquete que corre
directamente en la consola, vía el GDK de Microsoft) es el programa cerrado bajo NDA que cubre
§2.3 de este documento, y **XR-055 aplica igual a ambos casos**: tanto si publicas vía UWP como si
publicas nativo en consola, las reglas de logros/Gamerscore que certificación comprueba son las
mismas normas XR — lo que cambia es cómo llamas a la API, no el límite de negocio.

### 5.5 Quick Resume de Xbox Series, y por qué PlayStation no tiene un equivalente directo

**Quick Resume** es la función de Xbox Series X\|S que permite suspender y retomar varios juegos a
la vez sin pasar por su pantalla de carga. Descripción verificada hoy en Wikipedia, *Xbox Series
X/S* (<https://en.wikipedia.org/wiki/Xbox_Series_X/S>, consultado 07-09-2026): *«allows users to
suspend and resume up to three games at once. Games can also be resumed after a reboot of the
console.»* Una actualización de marzo de 2022 añadió la posibilidad de «fijar» hasta dos juegos
para que queden suspendidos indefinidamente salvo cierre manual o actualización obligatoria del
juego.

⚠️ **La diferencia arquitectónica con PlayStation 5 es conceptual, de conocimiento público del
oficio, no verificada hoy con una comparación técnica primaria línea a línea**: Xbox Series
mantiene el estado de **varios títulos en memoria/almacenamiento rápido simultáneamente** gracias a
su diseño de sistema (una combinación de SSD NVMe rápido y gestión de memoria orientada a
mantener procesos suspendidos), mientras que el «modo reposo» de PS5 —confirmado su nombre en
Wikipedia, *PlayStation 5*, consultado 07-09-2026— está pensado principalmente para bajar el
consumo energético del propio dispositivo, no para el mismo patrón de «varios juegos congelados a
la vez, cada uno retomable al instante» que promete Quick Resume. No se documenta aquí ninguna API
de GameMaker para implementar Quick Resume porque no existe ninguna: es un comportamiento que
gestiona el sistema operativo de la consola, no algo que un juego active por código — lo único que
le corresponde a tu juego es sobrevivir correctamente al ciclo de suspensión/reanudación que ya
cubre 05 · 02 §3.8 bis.

### 5.6 Certificación: duración orientativa

⚠️ **Ninguna cifra de esta subsección viene de una fuente primaria de Sony o Microsoft abierta en
esta sesión** — ambos fabricantes mantienen sus SLAs de certificación dentro de DevNet/Partner
Center, no en documentación pública. La auditoría previa recoge, de fuentes secundarias cruzadas
(generalistprogrammer.com, 07-09-2026, no reabierta hoy): **15-20 días hábiles** para una primera
revisión de PS5, y una duración similar orientativa para Xbox. Trátalas como una guía de
planificación de calendario, nunca como un SLA garantizado.

### 5.7 Devkits gratuitos en préstamo

Según el propio artículo de GameMaker citado en §2.2, registrarte como PlayStation Partner da
acceso a «pedir devkits» desde DevNet. ⚠️ El **modelo de hardware concreto** (la auditoría previa
cita la serie `DFI-D1000` para PS5) no se pudo confirmar hoy con una fuente primaria o secundaria
abierta en esta sesión — no se repite esa referencia de modelo aquí sin poder respaldarla. Lo que sí
es una categoría pública y consistente entre fabricantes: los devkits/testkits de consola suelen
prestarse, no venderse, durante un periodo determinado (del orden de un par de años en la práctica
del sector), y se devuelven al fabricante — nunca son propiedad del estudio.

### 5.8 El reloj del sistema

⚠️ **No se encontró ninguna fuente pública fiable y específica de consola en esta sesión** más allá
de la obligación genérica —común a cualquier plataforma con servicios online— de sincronizar marcas
de tiempo con un servidor cuando el juego depende de eventos temporales (rachas diarias, eventos
programados). Siguiendo la regla de §1.1: se deja marcado como **pendiente de verificación**, no
como un hueco que se rellena con una suposición razonable pero no confirmada.

---

## 6 · Transversal a las tres consolas

### 6.1 Clasificación por edades: IARC digital frente a certificado físico

[13 · 11 §9.4](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#94-clasificación-por-edades-pegi-esrb-e-iarc>)
ya explica IARC con detalle (un cuestionario, certificado reutilizable, nueve organismos) y esa
valoración no se reabre aquí. El matiz específico de consola que faltaba: **IARC nació y se aplica a
distribución digital**. Verificado hoy en Wikipedia, *International Age Rating Coalition*
(<https://en.wikipedia.org/wiki/International_Age_Rating_Coalition>, consultado 07-09-2026):
*«reduces the costs of video game developers as they seek to obtain ratings for their products that
are distributed digitally online»*, y confirma que **Nintendo fue el primer fabricante de consola
en adoptar IARC**, en octubre de 2015, específicamente para su eShop. ⚠️ El estado de PlayStation
Store y Microsoft Store en esa misma fuente data de 2018 («planning to later on» para PlayStation,
adopción reportada para Microsoft Store) — no verificado si sigue vigente hoy tal cual, así que
confírmalo en la tienda concreta a la que publiques antes de asumir que el cuestionario único te
libra de todo trámite.

La consecuencia práctica que no estaba explícita en ningún documento de la biblioteca: **la
distribución física no acepta IARC**. Un cartucho de Switch o un disco de PlayStation/Xbox necesita
el certificado de pago del organismo físico correspondiente (ESRB en EE. UU., PEGI en Europa…),
aunque tu versión digital de la misma tienda ya tenga su clasificación IARC resuelta gratis — son
dos trámites distintos para el mismo juego si publicas en ambos formatos, y el certificado físico es
específico de la combinación **juego + plataforma**, no reutilizable entre consolas aunque el
cuestionario IARC digital sí lo sea.

### 6.2 Localización mínima de facto

[04 · 21](<../04 - Recetas por género/21 - Localización e idiomas (con traducción por IA).md>) ya
cubre el orden de prioridad EFIGS como práctica de traducción, en contexto general. ⚠️ Ningún
fabricante publica un mínimo de idiomas **obligatorio** por escrito para acceder a su tienda de
consola: lo que sí exige cada uno es que soportes **por completo** cualquier idioma que declares
como soportado — no hay medias tintas de «traducido a medias» aceptadas en certificación. El
estándar de facto del sector, no una regla escrita, es **EFIGS + PL** (inglés, francés, italiano,
alemán, español y polaco) como el conjunto mínimo razonable para un lanzamiento multiplataforma
serio — una convención de la industria que conviene conocer al planificar presupuesto de LQA
([13 · 11 §12.6](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#126-lqa-revisión-lingüística-frente-a-traducción-automática>)),
no una cifra que este documento pueda citar como requisito formal de ningún fabricante.

### 6.3 Precio y regiones en las tiendas de consola

⚠️ No verificado en detalle en esta sesión. A diferencia de Steam —que documenta
[13 · 11 §6.7](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#67-fecha-precio-y-regiones>)
con un precio que tú fijas con libertad relativa por región—, cada tienda de consola define sus
propios **tramos de precio fijos** por región (no un campo de texto libre): Nintendo, PlayStation y
Xbox exigen elegir de una lista predefinida de precios por moneda/región en vez de escribir la cifra
que quieras. No se citan aquí los tramos exactos porque no se pudo confirmar ninguna tabla oficial
con fuente primaria en esta sesión — se marca el hueco en vez de rellenarlo con una tabla inventada.

### 6.4 Parches y su coste real en 2026

Desarrollo completo del mito ya adelantado en §1.2: la creencia de que un parche en consola cuesta
del orden de **40 000 USD** —una cifra de la era Xbox 360 (~2012-2013), atribuida a comentarios de
Tim Schafer— **es un mito ya falso en 2026**. Según el cruce de fuentes que ya reunió la auditoría
previa a este documento (Shacknews, ResetEra, no reabiertas en esta sesión de redacción): **Sony y
Nintendo no cobran por publicar actualizaciones** de un juego ya lanzado, y **Microsoft eliminó su
tasa histórica de certificación de parches**, salvo en casos de abuso —reenvíos excesivos o
negligentes del mismo build fallido una y otra vez—. El coste real de un parche hoy no es una tasa
de plataforma: es el tiempo de tu propio ciclo de certificación (§6.5) y el trabajo de desarrollo en
sí, no un cargo que Nintendo, Sony o Microsoft te facturen por el simple hecho de subir una
actualización.

### 6.5 El coste real de un fallo de certificación

⚠️ No verificado con fuente primaria en esta sesión. La auditoría previa cita, de fuente
sectorial no reabierta hoy, que cada *resubmission* (reenvío tras un fallo) reinicia la cola de
revisión —del orden de **4-8 semanas** de nuevo, no una corrección rápida— y puede sumar del orden
de un **15 %** al coste total de lanzamiento cuando se acumulan varios ciclos. No se puede verificar
esa cifra exacta hoy, pero el mecanismo en sí (fallar la certificación no es «arreglar y reenviar
mañana», es volver al final de una cola real) es la razón de fondo por la que probar en
**hardware/devkit real** antes de enviar —el mismo consejo que ya documenta
[05 · 05 §6.5](./05%20-%20Entregar%20el%20juego%20-%20firmar%2C%20notarizar%20y%20subir%20a%20las%20tiendas.md#65-el-proceso-de-revisión-y-los-rechazos-típicos)
para la App Store— es todavía más crítico en consola: un fallo evitable en dispositivo real puede
costar semanas, no un día.

### 6.6 *Day-and-date* entre varias consolas

[13 · 11 §6.7](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#67-fecha-precio-y-regiones>)
ya cubre el calendario de lanzamiento en general, aplicable a cualquier plataforma. Lo que ese
apartado no distingue, y sí importa en consola: lanzar el **mismo día** en dos o tres consolas a la
vez exige coordinar **colas de aprobación independientes** de cada fabricante (§5.6), cada una con
su propio plazo y su propio riesgo de retraso — un fallo de certificación en una sola plataforma
(§6.5) puede obligarte a elegir entre retrasar el lanzamiento simultáneo en todas o publicar por
separado, rompiendo el *day-and-date* que habías planeado en tu press kit.

---

## 7 · La alternativa realista: cuándo no ir a consola, y con quién va la gente que sí

### 7.1 Cuándo NO compensa ir a consola siendo indie

⚠️ No existe una fórmula oficial de ningún fabricante para esto — es criterio de producción, no un
dato verificable con fuente primaria. Señales razonables, coherentes con el resto de esta biblioteca
sobre alcance y presupuesto
([13 · 11 §1](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#1--alcance-el-único-problema-que-de-verdad-mata-juegos>)):

- **El juego todavía no ha demostrado tracción en PC/Steam** (wishlists, ventas, reseñas): ir a
  consola antes de validar la demanda multiplica el coste (licencia Enterprise, §3.1; tiempo de
  certificación, §5.6-§6.5) sobre un producto que todavía no sabes si se vende.
- **El equipo es una o dos personas sin presupuesto para un porting house** (§7.2): el trámite de
  acceso de §2, más el propio esfuerzo técnico de adaptar rendimiento/controles/guardado a cada
  SDK bajo NDA, es trabajo real que compite directamente con seguir haciendo el juego.
- **El género o el control del juego dependen de precisión de ratón/teclado** que no se traduce bien
  a mando — un coste de rediseño de UX, no solo de porting técnico, que rara vez compensa para un
  catálogo pequeño.
- **No hay margen para absorber un ciclo de re-certificación** (§6.5): si el calendario de
  lanzamiento no tiene semanas de holgura, un solo fallo de lotcheck/TRC/XR puede tirar la fecha
  entera por los aires.

### 7.2 Porting houses que trabajan con estudios pequeños, verificadas hoy

Todas las que siguen se comprobaron en vivo el 07-09-2026 (sus webs responden hoy y describen
explícitamente servicios de porting a consola):

| Estudio | Lo que dice su propia web (verificado 07-09-2026) |
|---|---|
| **Seaven Studio** (<https://www.seaven-studio.com/>) | *«Small porting house for indie games… Unity, Unreal Engine, Construct, Monogame, GameMaker, Godot, C++ engine»* — cita **GameMaker explícitamente** entre los motores que portean. Proyectos reales en curso a fecha de hoy: *Absolum* (edición Nintendo Switch 2) y *Kabuto Park* (Switch, Xbox Series, Xbox One), ya publicado en 2026 |
| **Axyos Games** (<https://axyosgames.com/>) | *«Console Publishing & Porting — helping developers bring their games to PlayStation, Xbox and Nintendo Switch, including optimization, certification support, release management, retail editions and China market opportunities»* |
| **Devoted Studios** (<https://www.devotedstudios.com/>) | Ofrece *«Game Porting Services»* como línea de negocio propia, junto a co-desarrollo y producción de arte |
| **Stepico** (<https://stepico.com/>) | *«Game Porting Services: seamless adaptation of games across platforms with optimized performance and user experience»* |

⚠️ Otros nombres que citaba la auditoría previa (DO Games, Game-Ace, y el caso de un desarrollador
individual registrado como Nintendo Developer especializado en ports a Switch) no se pudieron
reabrir con éxito en esta sesión de redacción (dominio no resuelto en un caso, o contenido genérico
de estudio de desarrollo sin foco claro en porting en otro) — no se listan aquí como verificados
propios de esta sesión.

### 7.3 Publishers que financian ports de consola

Distinto de un porting house puro: un **publisher** de consola no solo adapta el código, también
puede financiar el proceso a cambio de una parte de los ingresos futuros, y a menudo es él quien
figura ante el fabricante como la entidad registrada (§7.5). Verificado en vivo hoy:

- **Klabater** (<https://www.klabater.com/>) — editora polaca con una sección propia,
  «Wydanie na konsole» (edición en consola), y noticias reales de 2026 sobre lanzamientos
  coordinados en PS5 y Xbox Series X\|S (ejemplo verificado: el anuncio de *Hard West 2* para
  ambas consolas, 26-03-2026).
- **Noble Robot** (<https://noblerobot.com/>) — editora boutique con un catálogo propio de juegos
  publicados y una sección de «Services» separada de sus propios proyectos.
- **Axyos Games** (misma web que §7.2) cubre ambos papeles a la vez: porting técnico **y**
  publicación en consola, incluida gestión de ediciones físicas.

⚠️ **Crossforge**, citado por la auditoría previa como publisher de récord en consola que deja la
IP en manos del estudio original, no se pudo verificar hoy (el dominio probado no resolvió) — no se
incluye en la tabla de arriba por esa razón, aunque pueda existir bajo otro dominio no localizado en
esta sesión.

### 7.4 Cómo se estructura un acuerdo de porting o publishing

⚠️ Términos generales del oficio, no verificados con un contrato real abierto en esta sesión — la
misma cautela que ya aplica
[13 · 11 §12.1 y §12.5](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#121-colaboradores-socios-y-contratados-la-diferencia-importa-antes-de-firmar-nada>)
a colaboradores y cesión de derechos en general — la variante de consola añade una figura que ese
apartado todavía no cubre: el **publisher de porting**.

| Modelo | Cómo funciona | Riesgo para el estudio |
|---|---|---|
| **Fee único** | El porting house cobra un precio fijo por el trabajo técnico, sin quedarse con royalties futuros | Previsible, pero exige tener el dinero por adelantado — no compensa si el flujo de caja es ajustado |
| ***Revenue share*** | El porting house o publisher se queda con un porcentaje de las ventas de la versión de consola a cambio de financiar el porting | Sin coste inicial, pero reduce el margen de por vida de esa versión |
| **Anticipo recuperable** (*recoupment*) | El publisher adelanta el coste del porting y lo descuenta de las regalías futuras antes de empezar a pagarte nada | Estándar en la industria — el riesgo real está en **qué** se agrupa contra ese anticipo, ver la fila siguiente |
| **Cross-collateralización** | El publisher agrupa el coste de **todos** los ports que financia (Switch, PS5, Xbox…) contra el conjunto de ingresos de todas esas versiones, en vez de recuperar cada plataforma por separado | Si un port va peor de lo esperado, puede retener las regalías de **otra** plataforma que sí está vendiendo bien hasta recuperar el conjunto — pregunta explícitamente por esta cláusula antes de firmar |

**Cross-collateralización es el concepto crítico que faltaba en toda la biblioteca**: sin
preguntarlo explícitamente, un estudio puede firmar un acuerdo donde las regalías de la versión de
PC que sí vende bien quedan retenidas hasta que los ports de consola —que pueden ir peor— también se
hayan pagado a sí mismos. No es una cláusula ilegal ni inusual; es un riesgo de flujo de caja real
que conviene detectar leyendo el contrato, no asumiendo que cada plataforma se liquida por separado.

### 7.5 Quién es el «publisher de récord» ante el fabricante

Una distinción que no es la misma pregunta que «quién financia» (§7.4): en consola, a menudo es el
**porting house o publisher** —no el estudio original— quien figura como la entidad registrada
ante Nintendo, Sony o Microsoft (la que pasó el trámite de §2 con su propia cuenta y su propio
GDPA/NDA). Eso tiene una implicación práctica de control que conviene aclarar por escrito antes de
firmar: quién puede subir parches directamente, quién gestiona el precio y las promociones en la
tienda de consola, y qué pasa con esos permisos si la relación con el publisher termina — la misma
lógica de «pagar no es poseer» que ya advierte
[13 · 11 §12.5](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#125-cesión-de-derechos-por-qué-lo-pagué-no-es-es-mío>)
para encargos de arte, aplicada aquí al control de la propia cuenta de plataforma.

---

## 8 · Checklist

- [ ] **Licencia Enterprise** activa (§3.1) — sin ella no se configura ni un exportador de consola.
- [ ] **Registro en el portal de cada fabricante** completado: `developer.nintendo.com`,
      `register.playstation.net`, ID@Xbox (§2.1-§2.3).
- [ ] **Pitch enviado** al contacto regional correcto de Nintendo, o solicitud confirmada en
      DevNet/ID@Xbox (§2.1-§2.3).
- [ ] **NDA firmado** con el fabricante antes de esperar acceso al SDK real (§2, tabla de §2.3).
- [ ] **Licencia de GameMaker vinculada** vía Helpdesk tras la aprobación del fabricante — email de
      GameMaker y de la cuenta de desarrollador coinciden (§2.2, §2.3).
- [ ] **Cero anuncios públicos** de la plataforma de consola sin autorización explícita del
      fabricante, aunque el desarrollo ya esté aprobado (§2.4).
- [ ] **Terminología e iconos de botón** resueltos por plataforma activa, no hardcodeados (§4.3,
      §4.4).
- [ ] **Guardado atómico** sobre la API de sistema propia de cada consola, no sobre `file_text_*`
      genérico (§4.5).
- [ ] **Ciclo completo de suspensión/reanudación y dock↔portátil** probado en cada sala del juego,
      no solo en el menú (§4.6, §4.8).
- [ ] **Logros/Gamerscore dentro de los límites de XR-055** si publicas en Xbox: 10-100 logros y
      1000 Gamerscore al lanzamiento, sin superar los límites de por vida (§5.3).
- [ ] **Clasificación por edades resuelta para el formato que publiques**: IARC digital, certificado
      físico aparte si hay disco/cartucho (§6.1).
- [ ] **Presupuesto de tiempo con margen para al menos un ciclo de recertificación** (§5.6, §6.5).
- [ ] **Si trabajas con un porting house o publisher**: contrato revisado por la cláusula de
      cross-collateralización y por quién queda como entidad registrada ante el fabricante (§7.4,
      §7.5).

---

## 9 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Cómo evitarlo |
|---|---|---|
| Un agente de IA inventa un umbral de certificación que suena plausible | La biblioteca no lo tiene documentado y el modelo rellena el hueco con algo verosímil | Aplicar §1.1: parar, decir que el dato vive bajo NDA, y ofrecer solo las categorías públicas conocidas |
| Registrarse en `developer.nintendo.com` y esperar acceso automático al SDK de Switch | El registro general y la autorización de proyecto son dos pasos **distintos** — falta el contacto regional del §2.1 | Enviar el pitch a `developers@nintendo.eu` o `thirdpartypublisher@noa.nintendo.com` **después** de registrarte, no en su lugar |
| Anunciar «llegamos a Xbox» en redes en cuanto se aprueba el acceso al programa | Estar aprobado como desarrollador no es lo mismo que tener permiso de marketing del fabricante (§2.4) | Confirmar por escrito con el fabricante antes de cualquier anuncio público, aunque el port ya esté en marcha |
| Hardcodear «Pulsa A para confirmar» para las tres plataformas | La misma posición física confirma en Xbox y cancela en Switch (§4.4) | Resolver la etiqueta de botón por plataforma activa, igual que ya se resuelve la entrada con verbos en 01 · 12 |
| Presupuestar un parche de consola con la cifra mítica de 40 000 USD | Creencia desfasada de la era Xbox 360 que sigue circulando (§1.2, §6.4) | Ninguno de los tres fabricantes cobra por parche hoy salvo abuso de reenvíos — presupuesta el tiempo del ciclo de certificación, no una tasa que no existe |
| Firmar un acuerdo de porting sin preguntar por cross-collateralización | La cláusula no es ilegal ni rara, pero rara vez se explica sin que el estudio la pregunte (§7.4) | Preguntar explícitamente si el recoupment se calcula por plataforma o de forma conjunta antes de firmar |
| Dar por sentado que el certificado de clasificación de la eShop vale también para una edición física | IARC cubre solo distribución digital (§6.1) | Presupuestar el certificado físico de PEGI/ESRB por separado si hay cartucho o disco |

---

## Ver también

- [05 · 05 — Entregar el juego: firmar, notarizar y subir a las tiendas](./05%20-%20Entregar%20el%20juego%20-%20firmar%2C%20notarizar%20y%20subir%20a%20las%20tiendas.md) — el mismo trámite para Steam, macOS, Windows, Google Play, App Store e itch.io; ninguna de esas cinco es una consola
- [05 · 02 §1.4, §3.8 y §3.8 bis — Publicar y exportar](./02%20-%20Publicar%20y%20exportar.md#14-consolas-wikis-privadas) — qué exportadores existen hoy, sus wikis privadas y las categorías públicas de certificación que este documento extiende
- [04 · 20 §6 — Servicios de plataforma: Xbox Live/UWP](<../04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md#6--xbox-live--uwp-logros-estadísticas-leaderboards-usuarios-nube>) — la API de GML de logros y guardado en Xbox Live, complementaria a las reglas de negocio de XR-055 de este documento
- [01 · 12 — Input: teclado, ratón y gamepad](<../01 - Fundamentos/12 - Input - teclado, ratón y gamepad.md>) — las constantes `gp_face1`-`gp_face4` sobre las que se apoya la convención de botones de §4.4
- [13 · 11 §9 — Legal y administrativo mínimo](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#9--legal-y-administrativo-mínimo>) — licencia de GameMaker en general e IARC; este documento cubre su variante de consola
- [13 · 11 §12 — Trabajar con otras personas](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#12--trabajar-con-otras-personas>) — colaboradores, contratados y cesión de derechos en general; §7 de este documento cubre la variante específica de publisher/porting house de consola
- [13 · 25 §4 — Legal de terceros: usar el nombre de una consola](<../13 - Diseño y producción de videojuegos/25 - Legal de terceros - marcas, fan games y parodia.md#4--usar-el-nombre-el-logo-o-la-imagen-de-una-consola-un-motor-o-una-marca-de-terceros>) — ya resuelto con casos reales; no se repite aquí

---

## Fuentes

Todas consultadas el **7 de septiembre de 2026**, salvo que se indique otra fecha. Se distingue
explícitamente qué se abrió de verdad en esta sesión (con cita textual) de lo que procede del
cruce de fuentes que ya reunió la auditoría previa a este documento (marcado ⚠️ en el cuerpo del
texto, sin repetir aquí URLs que no se han vuelto a abrir).

**GameMaker (fuente primaria oficial, abierta con éxito hoy vía `curl` con `User-Agent` de
navegador — `WebFetch` devolvió 403)**
- *Application Process for Console Access* — <https://gamemaker.io/en/help/articles/application-process-for-console-access> · «Last updated: 4th August 2026»; contenido íntegro citado en §2
- GameMaker Enterprise (Steam) — <https://store.steampowered.com/app/1847411/GameMaker_Enterprise/> · precio verificado: 67,99 €/mes, 679,99 €/12 meses
- Precios y licencias — <https://gamemaker.io/en/get> · ya citado en 05 · 02 §2, no reabierto hoy

**Microsoft (documentación oficial)**
- Xbox Requirements (XR), certificación de consola — <https://learn.microsoft.com/en-us/gaming/gdk/docs/store/policies/console/certification-requirements> · versión 16.3, revisado 01-07-2026; XR-055, XR-057, XR-062 citadas textualmente en §5.3
- ID@Xbox, landing del programa — <https://developer.microsoft.com/en-US/games/partner/> · requisito de 18 años citado textualmente en §2.3
- Secure GDK Middleware Request — <https://developer.microsoft.com/en-us/games/support/request-gdkx-middleware>

**Nintendo y Sony (portales verificados en vivo, contenido interno no accesible sin cuenta de desarrollador)**
- Registro de desarrollador de Nintendo — <https://developer.nintendo.com/>
- Middleware GameMaker en el portal de Nintendo — <https://developer.nintendo.com/group/development/getting-started/g1kr9vj6/middleware/gamemaker-studio2>
- Registro de PlayStation Partner — <https://register.playstation.net> · HTTP 200, título «PlayStation® Partner Registration»
- Portal PlayStation Partners — <https://partners.playstation.net> · HTTP 200, título «PlayStation® Partners»; contenido interno cargado por JavaScript, no accesible en esta sesión
- SCE DevNet — <http://www.scedev.net/>

**Porting houses y publishers verificados en vivo hoy**
- Seaven Studio — <https://www.seaven-studio.com/> · cita GameMaker explícitamente entre los motores que portea
- Axyos Games — <https://axyosgames.com/>
- Devoted Studios — <https://www.devotedstudios.com/>
- Stepico — <https://stepico.com/>
- Klabater — <https://www.klabater.com/>
- Noble Robot — <https://noblerobot.com/>

**Wikipedia (verificado en vivo hoy, con cita textual — usado para historia y estructuras públicas, nunca para umbrales de certificación bajo NDA)**
- *Xbox controller* — <https://en.wikipedia.org/wiki/Xbox_controller> · lineage de Sega Genesis, §4.4
- *Trophy (PlayStation)* — <https://en.wikipedia.org/wiki/Trophy_(PlayStation)> · estructura de trofeos, §5.2
- *Xbox Series X/S* — <https://en.wikipedia.org/wiki/Xbox_Series_X/S> · Quick Resume, §5.5
- *International Age Rating Coalition* — <https://en.wikipedia.org/wiki/International_Age_Rating_Coalition> · IARC digital, §6.1
- *Gamerscore* — <https://en.wikipedia.org/wiki/Gamerscore> · contexto histórico de la era Xbox 360, no usado para la norma vigente (XR-055 la sustituye)

**Verificado en local (07-09-2026)**
- `gm-cli resourcetool eval "options list"` y `options info platform=<x>` sobre seis proyectos reales (`ResourceTool@2026.0.17`) — confirma que el comando no tiene ninguna regresión y resuelve si Switch 2 comparte nodo con Switch (§3.5; detalle completo en 05 · 02 §1.1)
- `python3 "_indice/buscar.py" --texto "<término>"` para lotcheck, TRC, GDPA, DevNet, Quick Resume, cross-collateral — confirma su ausencia total en la biblioteca antes de este documento (§3.4)

**No verificable en esta sesión (marcado ⚠️ en el cuerpo del texto, sin URL propia por no haberse abierto de verdad)**
- Tiempos de lotcheck, TRC y certificación de PS5 (§4.1, §5.6)
- Reparto de ingresos de la eShop, 30 % (§4.7)
- El mito de los 40 000 USD por parche y su desmentido (§1.2, §6.4)
- Modelo de devkit PS5 (§5.7) y coste de un fallo de certificación (§6.5)
- Reloj del sistema (§5.8)
