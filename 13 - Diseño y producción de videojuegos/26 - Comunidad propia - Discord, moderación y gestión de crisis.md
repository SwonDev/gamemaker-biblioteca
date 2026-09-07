# 26 · Comunidad propia: Discord, moderación y gestión de crisis

> Qué pasa **después** de publicar, con la gente que juega tu juego: montar y moderar el Discord
> del propio proyecto, recoger opiniones sin que te ahoguen, y —lo que de verdad separa a un
> estudio pequeño que sobrevive a un mal momento de uno que no— cómo responder a una oleada de
> reseñas negativas, un bug viral o una acusación pública sin empeorarlo.
>
> **Qué NO cubre, y dónde está:** dónde pedir ayuda **sobre GameMaker** (el problema simétrico:
> comunidades para aprender el motor, no para gestionar la tuya) —
> [07 · 10 — Comunidades y dónde preguntar](../07%20-%20Ecosistema/10%20-%20Comunidades%20y%20d%C3%B3nde%20preguntar.md);
> el kit de prensa y el contacto con medios antes del lanzamiento —
> [13 · 11 §6.6](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#66-demo-claves-y-press-kit);
> la telemetría con consentimiento y el postmortem —
> [13 · 11 §7](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#7--post-lanzamiento);
> y el riesgo legal de terceros (marcas, fan games) si la crisis viene de ahí —
> [13 · 25](./25%20-%20Legal%20de%20terceros%20-%20marcas%2C%20fan%20games%20y%20parodia.md).
> Este documento cubre exclusivamente la comunidad **de tu propio juego**, después de que exista
> gente jugándolo.

---

## 1 · Los principios

### 1.1 Una comunidad pequeña se gestiona distinto a una grande

Un Discord de 200 jugadores no necesita el aparato de moderación de uno de 200 000: bots
complejos, equipos de moderadores por turnos o reglas de 40 puntos son sobre-ingeniería que un
estudio de una o pocas personas no puede sostener. **El objetivo con pocos recursos no es
prevenir cualquier incidente posible, es que la estructura mínima aguante sin que tú tengas que
estar mirándola cada hora.**

### 1.2 Un canal mal pensado genera el problema que debería evitar

El error más común no es moderar mal: es **no separar los canales por función**, de forma que el
anuncio importante se pierde entre memes, el bug real se pierde entre charla general, y tú acabas
leyendo cada mensaje de cada canal para no perderte nada. La estructura de §2 existe para que
**la lectura sea opcional en unos canales y obligatoria en otros**, y tú sepas siempre cuáles.

### 1.3 Recoger opinión sin ahogarte es un problema de flujo, no de voluntad

No es que falte compromiso: es que sin un canal dedicado y una forma de convertir «me gustaría
que...» en algo procesable, la opinión de la comunidad se queda en conversación y nunca llega a
una decisión de diseño. El mismo problema, en la escala de un evento concreto, ya lo resuelve
[13 · 11 §6.4](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#64-steam-next-fest)
con el formulario de opinión de Steam Next Fest — aquí se generaliza a la vida entera del
proyecto.

### 1.4 Una crisis no se gestiona en el momento: se gestiona con la preparación de antes

Casi ninguna decisión buena durante una crisis se piensa en caliente. Lo que separa una respuesta
serena de una que empeora las cosas es haber decidido **de antemano** quién puede publicar en
nombre del estudio, qué tono se usa y qué NO se hace nunca (§3.4) — no improvisarlo con la
adrenalina de las primeras horas.

---

## 2 · El método, paso a paso

### 2.1 Los canales mínimos de un Discord de estudio pequeño

Cinco canales cubren la vida entera de un juego pequeño; añade más solo cuando el volumen real lo
justifique, no por adelantado:

| Canal | Para qué sirve | Quién escribe |
|---|---|---|
| **#anuncios** | Parches, novedades, fechas — el único canal que un jugador ocupado necesita seguir | Solo el equipo (canal de solo lectura para el resto) |
| **#general** | Charla libre sobre el juego | Todos |
| **#feedback** | Opiniones y sugerencias de diseño, separadas del ruido de #general | Todos, moderado con criterio (§2.3) |
| **#bugs** | Reportes de fallos, y solo eso — ver por qué en §2.2 | Todos, con una plantilla fija |
| **#reglas-y-bienvenida** | Las normas del servidor y el enlace al press kit/redes | Solo el equipo |

**Añade solo cuando el volumen lo pida**, no antes: un canal de voz cuando la comunidad organice
sus propias partidas; un canal de arte de fans cuando aparezca contenido suficiente para
merecerlo; un canal por idioma cuando la comunidad no anglófona/hispanohablante tenga masa
crítica propia. Un servidor con 30 canales vacíos para 40 miembros no organiza nada: dispersa.

### 2.2 Por qué un solo canal de «bugs» ahorra soporte

Cuando los reportes de fallos se mezclan con la charla general, pasan tres cosas malas a la vez:
**se pierden** entre mensajes no relacionados, **se duplican** porque nadie ve que ya lo reportó
otra persona, y **te obligan a leer todo el canal** para no perderte ninguno. Un canal dedicado,
con una plantilla fija que pides seguir —qué pasó, qué esperabas, versión del juego, capturas o
vídeo—, convierte cada reporte en algo que puedes triar en segundos en vez de reconstruir desde
cero. Es la misma lógica de recogida estructurada que ya usa
[01 · 15 §](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md)
para pedir la carpeta de logs al jugador en vez de un «no me funciona» sin contexto — aplicada
aquí al canal entero, no a un mensaje suelto.

### 2.3 Reglas de moderación básicas

Lo mínimo que un servidor pequeño necesita por escrito, en el canal de bienvenida, antes de tener
un solo problema:

1. **Sé respetuoso.** Cero insultos, acoso o discurso de odio — la única regla que de verdad hace
   falta explicar con ejemplos, porque «respeto» sin ejemplos concretos se interpreta distinto
   según quién lo lea.
2. **Los reportes de bugs van en #bugs**, la charla libre en #general, las sugerencias de diseño
   en #feedback. No es burocracia: es lo que hace que tú puedas seguir cada canal sin agotarte
   (§1.2).
3. **Nada de spoilers sin marcar**, si el juego tiene historia — con la etiqueta de spoiler nativa
   de Discord, no con un aviso de texto que la gente se salta.
4. **Nada de piratería, trampas competitivas o contenido ilegal.** Expulsión directa, sin
   negociación.
5. **El equipo no discute con una crítica dentro del servidor de la misma forma que no lo haría en
   una reseña pública** (§3.4) — una regla que va dirigida a ti tanto como a la comunidad.

### 2.4 Recoger opiniones sin ahogarte

- **Un canal, no un chat privado por persona.** Cada sugerencia repetida por varias personas en
  #feedback es una señal más fuerte que la misma sugerencia recibida diez veces por privado sin
  que nadie más la vea.
- **Reacciona con emoji a lo que ya tienes anotado**, aunque no vayas a implementarlo todavía: la
  comunidad necesita saber que se ha leído, no que se ha aceptado.
- **Convierte el feedback recurrente en un documento**, no en memoria: una nota en tu backlog
  (o en el roadmap si lo llevas público, ver
  [13 · 11 §7](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#7--post-lanzamiento))
  con la fecha y cuántas veces se ha pedido. Sin eso, tres meses después no recuerdas si «pedían
  mucho X» era cierto o una impresión.
- **Beta cerrada con jugadores reales, más allá de la telemetría.** La telemetría de
  [13 · 11 §7](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#7--post-lanzamiento)
  te dice **qué** hace la gente (dónde muere, dónde abandona); una beta cerrada con un grupo
  pequeño de jugadores reales —reclutado en tu propio Discord— te dice **por qué**, con la misma
  lógica de prueba pequeña y pagada (o al menos agradecida con acceso anticipado) que
  [13 · 11 §12.3](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#123-c%C3%B3mo-se-pide-una-prueba)
  ya recomienda para encargos externos.

---

## 3 · Gestionar una crisis: reseña bomb, bug viral o acusación pública

### 3.1 El plan de tres pasos

Sirve igual si la crisis es una oleada coordinada de reseñas negativas, un bug que se ha vuelto
viral en redes, o una acusación pública contra el estudio:

1. **Reconoce rápido**, incluso sin tener la solución todavía. Un mensaje breve en #anuncios y en
   redes —«sabemos que está pasando X, estamos mirándolo, actualizamos en unas horas»— corta la
   sensación de que el estudio ignora el problema, que es lo que más alimenta a una crisis en las
   primeras horas.
2. **No borres comentarios ni reseñas legítimas**, aunque sean injustas o estén mal informadas —
   ver por qué en §3.3.
3. **Comunica un plan con fecha**, no una promesa vaga. «Lo arreglamos en el parche de esta
   semana, jueves» genera confianza; «lo estamos mirando» sin fecha, ninguna. Si la fecha se
   mueve, dilo también — mejor una fecha que se retrasa una vez y se explica que una fecha
   incumplida en silencio.

### 3.2 El caso que muestra por qué funciona: No Man's Sky (2016-2020)

El lanzamiento de *No Man's Sky* en 2016 es el ejemplo más citado de una crisis de reputación
real en videojuegos, y por eso vale la pena entender qué se hizo mal al principio y qué funcionó
después:

- El juego se lanzó sin varias características que el estudio había mostrado o insinuado en el
  marketing previo (batallas espaciales, multijugador real), y la falta de comunicación
  inmediata de Hello Games tras el lanzamiento alimentó la sensación de que el estudio «había
  cobrado y desaparecido». La Autoridad de Estándares de Publicidad del Reino Unido llegó a
  investigar si el material promocional era engañoso.
- La recuperación **no vino de un parche único ni de una disculpa aislada**: Hello Games invirtió
  varios años en actualizaciones de contenido **gratuitas**, sostenidas y consecutivas, que
  fueron cerrando la distancia entre lo prometido y lo entregado. La cobertura posterior lo
  describe consistentemente como una historia de redención construida sobre **constancia**, no
  sobre una sola gran jugada de marketing.

Fuente: ComicBook.com, *10 Years Ago, No Man's Sky Overpromised and Underdelivered, But Its
Revival Is One of Gaming's Greatest Success Stories* —
<https://comicbook.com/gaming/feature/10-years-ago-no-mans-sky-overpromised-and-underdelivered-but-its-revival-is-one-of-gamings-greatest-success-stories/>
(consultado 07-09-2026). ⚠️ Es un caso a escala de un estudio con recursos para sostener años de
desarrollo gratuito — la lección aplicable a un equipo pequeño no es «puedes permitirte lo mismo»,
es el principio de fondo: **la comunicación honesta y sostenida en el tiempo repara más que
cualquier respuesta puntual, por bien escrita que esté**.

### 3.3 Por qué no se borran comentarios ni reseñas legítimas: el efecto Streisand

Borrar una crítica —aunque sea injusta, esté mal informada o duela— casi siempre produce el
efecto contrario al que se busca. Tiene nombre:

> **Efecto Streisand**: el fenómeno por el cual un intento de ocultar, eliminar o censurar
> información produce, como consecuencia no buscada, que esa información se difunda mucho más de
> lo que se habría difundido si no se hubiera intentado esconder. El término lo acuñó Mike
> Masnick, fundador del blog Techdirt, en enero de 2005, a raíz del caso que le da nombre: en
> 2003, la cantante y actriz Barbra Streisand demandó a un fotógrafo por 50 millones de dólares
> por publicar una foto aérea de su casa —una imagen que hasta entonces solo se había descargado
> seis veces—; tras conocerse la demanda, la foto se vio cientos de miles de veces en un mes.

Fuente: Wikipedia, *Streisand effect* — <https://en.wikipedia.org/wiki/Streisand_effect>
(consultado 07-09-2026). El mismo mecanismo se activa en un Discord o en Steam: un comentario
borrado o una reseña ocultada, capturada en pantalla y compartida como prueba de censura, alcanza
mucha más audiencia que el comentario original habría tenido nunca. **Deja la crítica donde está,
aunque duela, y responde ahí mismo si tienes algo que decir** — no la escondas.

### 3.4 El caso que muestra qué NO hacer: Digital Homicide (2016)

El ejemplo contrario, y el más citado como advertencia en la industria indie:

> En marzo de 2016, el estudio Digital Homicide demandó al crítico Jim Sterling por 10 millones
> de dólares por difamación, a raíz de sus críticas negativas a uno de sus juegos. El caso contra
> Sterling se desestimó con perjuicio en febrero de 2017. En septiembre de 2016, el estudio
> además demandó a **100 usuarios anónimos de Steam** por 18 millones de dólares, acusándolos de
> acoso por sus comentarios negativos. Para obtener sus datos, Digital Homicide envió a Valve una
> citación judicial pidiendo la identidad de esos usuarios — y **Valve respondió retirando los 18
> juegos del estudio de Steam** esa misma semana. El propio cofundador del estudio reconoció
> después que esto «destruyó» la compañía.

Fuentes: TechTimes, *Steam Pulls Digital Homicide's Games After It Sued 100 Users Of The
Community For $18 Million* —
<https://www.techtimes.com/articles/178168/20160918/steam-pulls-digital-homicides-games-after-it-sued-100-users-of-the-community-for-18-million-devs-respond.htm>
· Kotaku, *Court Throws Out Digital Homicide's Case Against Critic Jim Sterling* —
<https://kotaku.com/court-throws-out-digital-homicides-case-against-critic-1792599942>
(ambas consultadas 07-09-2026).

**La lección no es «nunca respondas a una crítica»**: es que **discutir con una reseña o una
crítica desde la cuenta oficial del estudio, y mucho más escalarlo a una amenaza legal, casi
siempre cuesta más reputación que la crítica original** — incluso cuando la crítica es injusta,
incluso cuando el estudio «tiene razón» en el fondo del argumento.

### 3.5 Qué NO hacer, resumido

| Nunca | Por qué |
|---|---|
| Discutir públicamente con una reseña o un comentario negativo desde la cuenta del estudio | El caso de Digital Homicide es la versión extrema; en la escala normal, «ganar» una discusión pública con un jugador se percibe casi siempre como el estudio perdiendo (§3.4) |
| Borrar comentarios o reseñas legítimas, aunque sean injustas | Efecto Streisand: multiplica la visibilidad de lo que querías esconder (§3.3) |
| Prometer una fecha que no vas a cumplir para calmar la crisis en el momento | Una fecha incumplida en silencio genera una segunda crisis, peor que la primera |
| Desaparecer sin comunicar nada mientras se investiga el problema | El silencio se interpreta como «el estudio ha huido», el error de comunicación que más alimentó la crisis inicial de No Man's Sky (§3.2) |
| Responder desde una cuenta personal en vez de la oficial del estudio, para «que no cuente» | Se descubre casi siempre, y añade una segunda historia («intentaron ocultar quién hablaba») a la crisis original |

---

## 4 · Checklist

- [ ] El Discord tiene al menos #anuncios, #general, #feedback, #bugs y #reglas-y-bienvenida,
      cada uno con un propósito claro escrito en su descripción.
- [ ] Las reglas de moderación están publicadas y son legibles en menos de un minuto.
- [ ] Hay una plantilla fija para reportar bugs, y se pide seguirla.
- [ ] El feedback recurrente se anota en un documento con fecha, no solo en la memoria del equipo.
- [ ] Decidiste **de antemano** quién puede publicar en nombre del estudio durante una crisis, y
      con qué tono.
- [ ] Tienes claro el plan de tres pasos (§3.1) antes de necesitarlo, no lo estás improvisando
      leyendo esto en mitad de una crisis real.
- [ ] Sabes que no vas a borrar críticas legítimas ni a discutir con una reseña desde la cuenta
      oficial, pase lo que pase.

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Cómo evitarlo |
|---|---|---|
| Un solo canal de «general» donde se mezcla todo | Parece más sencillo al montar el servidor, con pocos miembros | Separa desde el primer día (§2.1): cuesta lo mismo montarlo bien que mal, y reestructurar con comunidad activa es más caro |
| Responder a una crítica injusta con una discusión pública | La sensación de injusticia pide respuesta inmediata | Espera, respira, y si respondes, hazlo con datos y sin discutir el tono de quien critica (§3.4) |
| Borrar una reseña o comentario negativo «para que no se vea» | Parece la solución más rápida | Casi siempre produce el efecto contrario (§3.3): déjalo y responde si tienes algo útil que decir |
| Prometer una fecha de arreglo sin margen real | La presión de calmar la crisis ya | Da una fecha que puedas cumplir, o directamente di «no tengo fecha todavía, la doy en X días» |
| Guardar el feedback solo en la cabeza del equipo | Parece innecesario con pocos usuarios activos | Un documento con fecha desde el primer feedback recurrente; a los tres meses ya no te fías de la memoria (§2.4) |
| Tratar cada mensaje de Discord como si hubiera que responderlo | Sensación de obligación con la comunidad | La estructura de canales (§2.1) hace que solo #bugs y #feedback necesiten lectura activa constante |

---

## Ver también

- [13 · 11 §6.6 — Demo, claves y press kit](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#66-demo-claves-y-press-kit) y
  [§7 — Post-lanzamiento](./11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#7--post-lanzamiento) —
  el kit de prensa antes del lanzamiento y la telemetría con consentimiento después, la otra mitad
  del ciclo de comunidad que este documento no repite
- [13 · 25 — Legal de terceros: marcas, fan games y parodia](./25%20-%20Legal%20de%20terceros%20-%20marcas%2C%20fan%20games%20y%20parodia.md) —
  qué hacer si la crisis viene de una reclamación de propiedad intelectual, no de la comunidad
- [07 · 10 — Comunidades y dónde preguntar](../07%20-%20Ecosistema/10%20-%20Comunidades%20y%20d%C3%B3nde%20preguntar.md) —
  el problema simétrico: dónde pedir ayuda tú sobre GameMaker, no cómo gestionar la comunidad de
  tu propio juego
- [01 · 15 — Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md) —
  cómo pedirle al jugador la carpeta de logs, la misma lógica de recogida estructurada que §2.2
  aplica al canal de bugs entero

---

## Fuentes

Todas consultadas el **7 de septiembre de 2026**.

- ComicBook.com, *10 Years Ago, No Man's Sky Overpromised and Underdelivered, But Its Revival Is
  One of Gaming's Greatest Success Stories* — <https://comicbook.com/gaming/feature/10-years-ago-no-mans-sky-overpromised-and-underdelivered-but-its-revival-is-one-of-gamings-greatest-success-stories/>
- TechTimes, *Steam Pulls Digital Homicide's Games After It Sued 100 Users Of The Community For
  $18 Million, Devs Respond* — <https://www.techtimes.com/articles/178168/20160918/steam-pulls-digital-homicides-games-after-it-sued-100-users-of-the-community-for-18-million-devs-respond.htm>
- Kotaku, *Court Throws Out Digital Homicide's Case Against Critic Jim Sterling* — <https://kotaku.com/court-throws-out-digital-homicides-case-against-critic-1792599942>
- Wikipedia, *Streisand effect* — <https://en.wikipedia.org/wiki/Streisand_effect>
