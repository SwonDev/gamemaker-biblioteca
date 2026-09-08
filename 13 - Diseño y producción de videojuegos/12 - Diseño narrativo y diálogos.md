# 12 · Diseño narrativo y diálogos

> El **oficio de escribir para juegos**: qué historia necesita tu juego, cómo se estructura,
> cómo se cuenta sin cinemáticas, cómo se escribe un diálogo que no sobra, y cómo todo eso se
> convierte en datos que GameMaker puede ejecutar.
>
> **Lo que NO cubre este documento — porque ya está resuelto en otro sitio, y repetirlo sería
> mentir dos veces:** la caja de diálogo, el parser de guion, el *typewriter*, el *backlog* y el
> guardado con miniatura están en
> [`04 · 10 — Visual Novel y narrativa`](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md);
> el dibujado del texto con efectos, en
> [`07 · 18 — Scribble`](../07%20-%20Ecosistema/18%20-%20Scribble%20-%20texto%20rico%20%28guía%20en%20español%29.md);
> y el motor de diálogo ramificado ya hecho, en
> [`07 · 19 — Chatterbox`](../07%20-%20Ecosistema/19%20-%20Chatterbox%20-%20diálogos%20Yarn%20%28guía%20en%20español%29.md).
> Aquí no hay ni una línea de caja de diálogo. Aquí está **qué escribes dentro de ella y por qué**.

---

## 1 · Los principios

### 1.1 Historia, trama y tema no son la misma cosa

Tres palabras que la gente usa como sinónimos y que designan tres trabajos distintos:

| Palabra | Qué es | Quién la controla en un juego |
|---|---|---|
| **Historia** (*story*) | Los hechos, en orden cronológico. «El rey murió y luego murió la reina» | El autor, casi siempre entera |
| **Trama** (*plot*) | Los mismos hechos con su **causa** y en el orden en que se descubren. «…murió la reina **de pena**» | Autor **y jugador**, a medias |
| **Tema** | De qué va de verdad. La pregunta que el juego hace sin enunciarla | El autor, a través de la mecánica |

La distinción entre historia y trama es de E. M. Forster (*Aspects of the Novel*, 1927): «el rey
murió y luego murió la reina» es historia; añadir «de pena» la convierte en trama, porque
introduce la causa. En un juego, **la mitad de la trama la monta el jugador**: elige en qué
orden entra en las salas, a qué NPC habla, qué nota lee y cuál se salta. Escribir para juegos es
escribir sabiendo que el orden no está garantizado.

Consecuencia práctica inmediata: **ninguna pieza de texto puede depender de que el jugador haya
leído otra que no era obligatoria.** Si la nota del sótano explica quién es el antagonista y el
sótano es opcional, el antagonista no está explicado.

El **tema** es lo que más se olvida y lo que más rinde. No es la moraleja; es la pregunta. *Papers,
Please* pregunta «¿a cuánta gente traicionarías por dar de comer a tu familia?», y no lo dice en
ningún diálogo: lo dice el formulario que rellenas. **El tema se afirma con la mecánica; la
historia solo lo ilustra.**

### 1.2 Narrativa embebida frente a narrativa emergente

Henry Jenkins («Game Design as Narrative Architecture») describe cuatro maneras de que un espacio
de juego cuente algo. Las cuatro conviven en un mismo juego:

| Forma | Qué hace | Ejemplo en un juego 2D pequeño |
|---|---|---|
| **Espacio evocador** | El escenario invoca un género que el jugador ya conoce | Un castillo gótico: nadie tiene que explicar que ahí hay vampiros |
| **Narrativa representada** (*enacted*) | El jugador **ejecuta** los sucesos de la historia | La huida del prólogo la corres tú, no la ves |
| **Narrativa embebida** (*embedded*) | El mundo es «un espacio de información, un palacio de la memoria»: el autor reparte la información por el mapa y el jugador la reconstruye | Las tres tumbas con la misma fecha grabada |
| **Narrativa emergente** | No está preprogramada; nace del juego, pero tampoco es caos | Que te quedaras sin balas justo en el pasillo largo |

> 🔺 **La distinción que de verdad importa es la de coste.** La narrativa **embebida** la escribes
> tú, línea a línea: cuesta dinero por palabra y se agota. La **emergente** la produce el sistema:
> cuesta una vez, en forma de reglas, y no se agota nunca. Un equipo de una persona debería
> apoyarse en la emergente todo lo que pueda y gastar la embebida donde de verdad se note.
>
> ⚠️ Jenkins avisa de que la emergente «no está preestructurada ni preprogramada… pero tampoco es
> tan desestructurada, caótica y frustrante como la vida misma». Una historia emergente que el
> jugador no puede contar después **no ha ocurrido**. Hace falta que el sistema deje huellas
> legibles: un registro de muertes, un titular al morir, una lápida con el nombre del anterior.

### 1.3 El jugador como coautor: agencia, no libertad

Janet Murray (*Hamlet on the Holodeck*) llamó **agencia** a «la capacidad satisfactoria de
emprender acciones con sentido y ver los resultados de nuestras decisiones y elecciones».

Las dos palabras que hacen el trabajo son *con sentido* y *resultados*. No dice «muchas
opciones». Un menú con cuarenta ramas que no cambian nada da **cero** agencia. Un juego con una
sola decisión que lo cambia todo da muchísima.

> 💡 **Agencia ≠ libertad.** El jugador no quiere poder hacer cualquier cosa; quiere que **lo que
> hace importe**. Esta es la razón por la que un pasillo con tres decisiones consecuentes se
> recuerda mejor que un mundo abierto con cien misiones intercambiables.

De aquí sale la regla de oro del diseño narrativo interactivo, y la usaremos todo el documento:

> **Es mejor una elección con tres consecuencias que tres elecciones sin ninguna.**

### 1.4 Ludonarrativa y disonancia

**Ludonarrativa** es lo que el juego cuenta **jugando**: sus reglas, su economía, lo que premia y
lo que castiga. **Disonancia ludonarrativa** es lo que ocurre cuando lo que el juego cuenta con
palabras y lo que cuenta con reglas se contradicen. El término lo acuñó **Clint Hocking** el 7 de
octubre de 2007 escribiendo sobre *BioShock*: «*BioShock* parece sufrir una disonancia poderosa
entre de qué va **como juego** y de qué va **como historia**». Y remató con la frase que explica
por qué importa: al enfrentar lo narrativo con lo lúdico, «el juego parece burlarse abiertamente
del jugador por haberse creído su ficción».

Los casos que aparecen en juegos pequeños son casi siempre estos cuatro:

| Disonancia típica | Cómo se ve | Arreglo barato |
|---|---|---|
| El protagonista «no quiere hacer daño» y matas a 300 enemigos | El guion dice pacifismo, la mecánica premia matar | O el guion se rinde y lo asume, o los enemigos dejan de ser personas (robots, plagas) |
| «Corre, no hay tiempo» y luego exploras 40 minutos sin penalización | La urgencia es falsa y el jugador lo nota | Ponle temporizador de verdad, o quita la urgencia del texto |
| El personaje es pobre y llevas 90 000 monedas | La economía contradice la ficción | Ata la ficción a la economía: que el dinero se lo lleve la deuda |
| Un NPC «vital» al que puedes ignorar para siempre | El texto lo pinta imprescindible; el sistema, no | Hazlo un requisito real, o rebaja el texto |

> ⚠️ **Antes de escribir una sola línea, escribe qué premia tu juego.** Si premia matar deprisa,
> tu historia va de matar deprisa, digas lo que digas. Es más fácil cambiar el guion que cambiar
> la economía. → [`13 · 01 — Diseño de juego`](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) §4.

### 1.5 Qué historia necesita cada género

No todos los juegos necesitan la misma cantidad ni el mismo tipo de narrativa. Meter una VN
dentro de un arcade es tan mal diseño como no dar contexto a un RPG.

| Género | Cuánta narrativa | Dónde vive | Qué NO hagas |
|---|---|---|---|
| **Plataformas** | Mínima: una premisa y un final | Carteles del mundo, fondo, jefe final | Cinemática antes de cada nivel |
| **Roguelike** | Marco + emergente | Texto de objeto, diálogo de mercader, epitafios de muertes | Una trama lineal que se ve 40 veces |
| **RPG** | Máxima: es el género de la historia | Diálogo, misiones, libros, NPC con agenda | Muros de *lore* antes de la primera pelea |
| **Puzzle** | Casi ninguna, o toda (dos extremos válidos) | Entre mundos, o en el propio puzle (*Baba Is You*, *The Witness*) | Un narrador que interrumpe cada solución |
| **Survival** | Emergente + embebida, casi sin diálogo | Bases abandonadas, diarios, restos | NPC que te expliquen lo que ves |
| **Visual Novel** | Es el juego entero | Todo el texto | Elecciones decorativas que no ramifican |
| **Shmup / arcade** | Una línea de premisa | Pantalla de título, nombre del jefe | Interrumpir la acción para hablar |
| **Metroidvania** | Media, casi toda ambiental | Arquitectura, cadáveres, grabados | Un tutorial hablado de 10 minutos |

> 💡 **El test de una frase.** Si no puedes decir la premisa de tu juego en una frase que un
> desconocido entienda —«eres un cartero en un mundo que se inunda»—, no tienes historia: tienes
> notas. Escríbela antes que nada; cabe en el
> [GDD de una página](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) §8.

---

## 2 · Estructura

### 2.1 Tres actos, y por qué en un juego el segundo es el problema

La estructura de tres actos (planteamiento / confrontación / resolución) funciona porque describe
un cambio de estado con dos giros. Traducida a juego:

| Acto | Qué pasa en la historia | Qué pasa en la **mecánica** |
|---|---|---|
| **I** — Planteamiento (≈20 %) | Quién eres, qué falta, qué se rompe | Enseñas el verbo principal; el jugador ya sabe jugar al terminar |
| **II** — Confrontación (≈60 %) | Intentos, fracasos, escalada | Se añaden verbos, se combinan, sube la dificultad |
| **III** — Resolución (≈20 %) | El giro final, el clímax, el cierre | Todo lo aprendido se usa a la vez; el jefe es un examen |

**El acto II es donde mueren los juegos de una persona.** Es el 60 % del contenido y el que menos
se puede reciclar narrativamente. Dos salidas honestas:

1. **Estructura episódica**: el acto II se parte en 4-6 unidades de la misma forma
   (llegar a un sitio → resolverlo → volver). Cada unidad se produce igual, y una que caiga no
   rompe el resto.
2. **Estructura de recolección**: el acto II es «consigue las N piezas», en cualquier orden. Es la
   estructura del metroidvania y del 3D collectathon, y es la que mejor tolera que el jugador se
   salte cosas.

> 🔺 **El acto III siempre se sobreescribe.** El final se escribe cuando el juego ya está
> montado, nunca antes: escribirlo primero garantiza que no encaje con el juego que salió de
> verdad.

### 2.2 El viaje del héroe, con cautela

El monomito de Campbell (llamada, umbral, pruebas, abismo, retorno) es útil como **lista de
comprobación de momentos**, y peligroso como plantilla. Dos advertencias serias:

- **Produce el mismo juego una y otra vez.** Huérfano elegido, mentor que muere, mundo salvado.
  Si tu premisa cabe entera en el monomito, tu premisa es una plantilla.
- **Está pensado para un protagonista pasivo al que le pasan cosas.** Un juego va de un
  protagonista que **hace** cosas. La «negativa a la llamada» es literalmente el jugador
  negándose a jugar.

Úsalo así y solo así: como diagnóstico. «¿Hay un momento en que el jugador no puede volver
atrás?» (umbral). «¿Hay un punto en el que todo va mal?» (abismo). «¿El jugador vuelve al inicio
cambiado?» (retorno). Si las tres respuestas son «no», tu historia probablemente sea plana. Si
las tres son «sí» y además hay un mentor que muere, quizá vayas demasiado por el camino trillado.

### 2.3 Kishōtenketsu: estructura sin conflicto

Estructura narrativa de cuatro partes de origen chino (*qǐ chéng zhuǎn hé*), usada en japonés y
coreano, en la que **no hay conflicto ni antagonista**: hay un giro que reencuadra lo anterior.

| Fase | Kanji | Qué hace | En un nivel de juego |
|---|---|---|---|
| **Ki** (起) | Introducción | Presenta el elemento | Se te enseña el bloque que empuja |
| **Shō** (承) | Desarrollo | Lo desarrolla sin sorpresas | Un par de salas usando el bloque |
| **Ten** (転) | **Giro** | Aparece algo que reencuadra lo anterior | El bloque también flota en el agua |
| **Ketsu** (結) | Conclusión | Une las dos ideas y cierra | Una sala que exige empujar **y** flotar |

Es la estructura del diseño de niveles de Nintendo y la que mejor le va a **puzzles, plataformas
y juegos cortos**, porque no exige villano, ni pérdida, ni escalada emocional: exige una idea y un
giro. En esta biblioteca su aplicación al **espacio** —introducir, desarrollar, torcer, concluir—
está desarrollada en [`13 · 02 — Diseño de niveles`](./02%20-%20Diseño%20de%20niveles.md) §1.1. Aquí
interesa lo otro: **también sirve para escribir una escena de diálogo.** Ki: el NPC dice algo
banal. Shō: lo amplía. Ten: revela que sabía algo que tú no. Ketsu: la conversación cambia de
sentido con lo revelado.

### 2.4 Arcos de personaje: deseo, necesidad, herida

El arco de un personaje es la distancia entre lo que **quiere** y lo que **necesita**:

- **Deseo** (*want*): el objetivo consciente, el que persigue. Es lo que mueve la trama.
- **Necesidad** (*need*): lo que le falta de verdad y no sabe. Es lo que mueve el tema.
- **Herida**: el suceso pasado que explica por qué confunde una cosa con la otra.

Un arco es el proceso de cambiar el deseo por la necesidad. El clímax es la escena donde tiene
que elegir entre los dos.

```
Herida ──────► Deseo (equivocado) ──────► Crisis ──────► Necesidad (verdad)
   ↑                                          │
   └──────────── el antagonista la toca ──────┘
```

**El antagonista como espejo.** El mejor antagonista no es el más fuerte: es el que tiene **la
misma herida y eligió la otra salida**. Comparte el deseo del protagonista y le da la razón
llevándolo al extremo. Eso hace que cada escena entre los dos hable del tema sin enunciarlo.

> 💡 **Prueba rápida:** escribe la frase «yo también perdí a alguien, **pero yo**…» en boca de tu
> antagonista. Si la puedes terminar de forma convincente, tienes espejo. Si no, tienes un
> obstáculo con voz.

### 2.5 *Story beats* y ritmo: la narrativa contra el juego

Un **beat** es la unidad mínima de cambio: el momento en que una situación pasa de un estado a
otro. En prosa es un intercambio de diálogo; en un juego es «el jugador descubre X», «el jugador
pierde Y», «aparece la amenaza».

El problema propio del medio: **hay dos ritmos corriendo a la vez y no son el mismo.**

| | Ritmo de juego | Ritmo narrativo |
|---|---|---|
| Lo marca | La dificultad, la tensión, el descanso | La revelación y el cambio |
| Lo controla | El diseñador de niveles | El guionista |
| Su unidad | El encuentro, la sala | El beat |
| Se estropea con | Combates seguidos sin respiro | Dos giros seguidos sin asimilar |

La regla que los reconcilia: **los beats narrativos se colocan en los valles del ritmo de juego,
no en los picos.** El jugador no procesa una revelación mientras esquiva balas. El sitio natural
de una escena de diálogo es justo después de un pico de tensión, cuando la adrenalina baja: por
eso las hogueras, los ascensores lentos y los campamentos existen.

> 🔺 **La curva de tensión de niveles y la de la historia se dibujan en el mismo papel.** El mapa
> de ritmo de [`13 · 02 — Diseño de niveles`](./02%20-%20Diseño%20de%20niveles.md) §1.2 es donde
> van marcados los beats. Si tienes tres revelaciones y las tres caen en el mismo pico, has
> desperdiciado dos.

### 2.6 Las formas de la narrativa interactiva (y su coste)

El catálogo canónico de estructuras de narrativa por elecciones es **«Standard Patterns in
Choice-Based Games», de Sam Kabo Ashwell** (2015). Los nombres son suyos —Emily Short los cita
como referencia obligada cada vez que toca el tema— y describen lo que de verdad se construye:

| Estructura (Ashwell) | Forma | Coste | Cuándo usarla |
|---|---|---|---|
| **Time cave** | Árbol puro, «muchísimos, muchísimos finales»; ninguna rama vuelve | Explosivo (2ⁿ) | Nunca, salvo relatos muy cortos |
| **Gauntlet** (pasillo) | «Largo, no ancho»: un camino ungido con ramitas cortas que mueren o vuelven | Barato | Historia lineal con sabor de elección |
| **Branch and bottleneck** | Ramifica y **vuelve a unirse** con regularidad, «en torno a sucesos comunes a todas las versiones» | Lineal, controlado | **El caballo de batalla.** El 90 % de los juegos con elecciones |
| **Quest** | Ramas distintas que reconvergen en unos pocos finales ganadores | Medio | RPG, metroidvania |
| **Open map** | Geografía estática; el viaje entre nodos es reversible | Medio | Mundo que se recorre en cualquier orden |
| **Sorting hat** | El principio ramifica mucho y reconverge para **asignarte** una rama grande | Medio-alto | Rutas de personaje en una VN |
| **Loop and grow** | Un hilo central que se repite en bucle y va desbloqueando opciones nuevas | Medio | Roguelike narrativo, bucle temporal |
| **Floating modules** | «Sin árbol, sin trama central, sin hilo conductor»: escenas que el sistema saca cuando encajan | Bajo por escena, alto de sistema | *Barks*, diálogo reactivo, sim social |

Sobre ese catálogo, **Emily Short** («Beyond Branching», 2016) añade tres estructuras que ya no
son ramificación en absoluto y que son las que más rinden en un juego pequeño:

| Estructura (Short) | Cómo funciona | Dónde la vas a usar |
|---|---|---|
| **Quality-Based Narrative** (QBN) | *Storylets* —fragmentos de contenido— que se desbloquean por **cualidades** numéricas: inventario, habilidades, progreso | Misiones, encuentros, eventos de roguelike |
| **Salience-Based** | De una **piscina grande** de contenido, el sistema saca en cada momento el fragmento «juzgado más aplicable». Short cita *Left 4 Dead* y *Firewatch* | **Exactamente el sistema de *barks* del §3.5 y del §6.4** |
| **Waypoint** | La conversación avanza por temas: el sistema hace *pathfinding* hacia el siguiente tema disparador | Diálogo de investigación, interrogatorios |

> 💡 **Lo que esto significa para ti:** las estructuras de Ashwell describen **la forma de la
> trama**; las de Short describen **cómo se elige el contenido**. Un juego pequeño y bien montado
> suele ser un *gauntlet* o un *branch and bottleneck* por fuera, con un sistema *salience-based*
> por dentro para todo lo que no es la trama principal. Esa combinación es barata y parece
> enorme.

**El coste de la ramificación pura, en números.** Una elección binaria en cada uno de 10 nodos da
2¹⁰ = 1 024 finales. Si cada rama son 300 palabras, son **más de 300 000 palabras**: cuatro veces
una novela, para un juego de dos horas. Nadie hace eso. Es lo que Short llama «lo contrario de la
narrativa ramificada que explota combinatoriamente, donde como autor **se te castiga por escribir
contenido nuevo**, porque te compromete a escribir todavía más más adelante». La salida es el
*branch and bottleneck*, y su aritmética está en el §4.7.

> 💡 **La regla de producción:** las ramas se pagan **una vez** (la escena), las reacciones se
> pagan **por línea** (una condición dentro de un texto que ya existe). Reaccionar es entre diez y
> cien veces más barato que ramificar, y el jugador lo nota casi igual.

---

## 3 · Contar sin cinemática

Una cinemática es la forma **más cara y menos interactiva** de contar algo. Todo lo que se pueda
contar de otra manera, se cuenta de otra manera. Este apartado es el catálogo de las otras
maneras, ordenadas de más barata a más cara.

### 3.1 Narrativa ambiental (*environmental storytelling*)

La definición operativa viene de la charla de **Harvey Smith y Matthias Worch** en la GDC 2010:

> «Escenificar el espacio del jugador con propiedades del entorno que puedan interpretarse como
> un **todo con sentido**, haciendo avanzar la narrativa del juego.»

La propiedad clave que subrayan es que **depende del jugador para asociar elementos dispersos**.
Lo comparan con la ley de cierre de la Gestalt: el significado ocurre **en los huecos** entre lo
que se enseña. No es «poner cosas bonitas»; es componer un escenario del que se deduce un suceso.

La receta tiene tres piezas obligatorias:

1. **Una situación anómala**: algo que no debería estar así.
2. **Suficientes pistas para deducir la causa**, no todas.
3. **Un hueco que el jugador rellena.** Si lo explicas entero, no es narrativa ambiental: es un
   cartel.

Y una cuarta condición, incómoda, que Smith defiende explícitamente: **tiene que ser posible
pasar de largo.** «Tiene que ser posible perderse algunas cosas para que encontrarlas signifique
algo.» Una escena ambiental que el juego te obliga a mirar deja de ser un descubrimiento.

```
Escena escenificada, en 2D y con cuatro sprites:

    [cama volcada]  [cadena rota en la pared]  [arañazos que van hacia la puerta]
                    [comida a medio comer, aún ahí]

Lo que el jugador deduce solo: aquí había algo atado, se soltó de golpe,
y se fue mientras comía. Nadie ha escrito una sola palabra.
```

**Por qué funciona tan bien y es tan barata.** El jugador que deduce se siente listo; el jugador
al que le explican se siente tutelado. Y en producción, cuatro sprites que ya tenías colocados en
el Room Editor cuestan minutos, no días.

**Cómo se compone bien en 2D**, que es donde nos movemos:

| Herramienta | Uso narrativo |
|---|---|
| **Composición** | Lo importante en el centro de la sala o donde muere la mirada al entrar |
| **Repetición** | Tres veces la misma escena = un patrón, no una casualidad |
| **Contraste** | Un objeto limpio en una sala destrozada llama más que diez rotos |
| **Progresión** | La misma escena, tres salas seguidas, cada vez peor: eso es una secuencia |
| **Silencio** | Una sala vacía después de tres cargadas dice «aquí terminó» |

**El plazo: quince segundos.** Don Carson —diseñador de atracciones de Disney Imagineering antes
que de juegos— fijó en el artículo fundacional del tema (2000) que el jugador debe poder
responder «¿dónde estoy?» en los **primeros quince segundos** de entrar en un entorno, o el
espacio ya ha fallado. Su otra regla útil aquí: incluso en un mundo alienígena hay que dar
**anclajes reconocibles** cada poco, o el jugador se pierde y deja de leer el espacio.

> ⚠️ **El fallo típico:** poner la escena en una esquina que nadie mira. La narrativa ambiental
> depende de la **línea de visión** y del recorrido. Colócala donde el diseño de niveles ya lleva
> los ojos del jugador → [`13 · 02 — Diseño de niveles`](./02%20-%20Diseño%20de%20niveles.md) §1.3
> (legibilidad, *weenies* y líneas de guía).

### 3.2 Objetos y descripciones

El texto de un objeto es la unidad narrativa más eficiente que existe: se lee cuando el jugador
quiere, no interrumpe, cabe en 20 palabras y se reutiliza en cada partida.

Tres tipos, y conviene que estén los tres:

| Tipo | Ejemplo | Qué aporta |
|---|---|---|
| **Funcional** | «Cura 20 de vida» | El jugador lo necesita. Va **siempre primero** |
| **De mundo** | «Ungüento del gremio de barqueros» | Implica que hay un gremio, sin explicarlo |
| **De voz** | «Sabe a río. Nadie sabe por qué» | Da tono, humor o inquietud |

```
❌  "Poción de curación. Un recipiente de vidrio que contiene un líquido
     rojo elaborado por los alquimistas de la torre norte durante el
     reinado de..."          ← 40 palabras y la mecánica no aparece

✅  "Cura 20 PV. Sabe a río. Los barqueros la beben antes de cruzar."
                             ← 12 palabras: mecánica, mundo y voz
```

> 💡 **La descripción de objeto es donde meter el *lore* que no cabe en ningún sitio.** Es
> opcional, es corta y el jugador la lee cuando le apetece. Es el vertedero legítimo del mundo.

### 3.3 Documentos encontrados: el *audiolog* y sus problemas

Notas, diarios, correos, cintas. Es la forma más común de contar el pasado en un juego y también
la más criticada, con razón. Tres problemas reales:

1. **Rompen el ritmo**: parar a leer 300 palabras en mitad de una huida es absurdo.
2. **Los escribe alguien improbable**: nadie redacta su diario íntimo con exposición del mundo
   dentro. Un documento tiene que tener un **motivo verosímil de existir**.
3. **Se acumulan**: si hay 60, el jugador deja de leerlos hacia el número 12.

Las tres reglas que los salvan:

| Regla | Por qué |
|---|---|
| **Máximo 150 palabras**, una pantalla | Si hace falta desplazar, ya es demasiado |
| **Cada documento contiene UN hecho nuevo** | Si contiene tres, dos se pierden |
| **Legible en movimiento o pausando el mundo** | O el jugador lo lee, o lo guarda «para luego» y no vuelve |

> 🔺 **La prueba del emisor.** Antes de escribir un documento, responde: ¿quién lo escribió, para
> quién y por qué lo dejó aquí? Si la respuesta es «el guionista, para el jugador, porque hacía
> falta explicar esto», tíralo y busca otra vía.

### 3.4 «Show, don't tell» traducido a juegos

En prosa, «muestra, no cuentes» significa preferir la escena a la explicación. En un juego hay un
escalón más, y es el bueno:

```
Contar   →  «Los guardias son crueles.»                       (peor)
Mostrar  →  Ves a un guardia pegar a un mendigo.              (mejor)
JUGAR    →  Un guardia te registra a ti y te quita algo tuyo.  (lo propio del medio)
```

La tercera opción usa la mecánica: el jugador **pierde un objeto de verdad**. Esa pérdida la
recordará dentro de un año; la cinemática del mendigo, no.

Traducción operativa: **antes de escribir una línea que caracterice a alguien o a algo, comprueba
si puedes convertirla en una regla del juego.** Si no puedes, muéstrala. Si tampoco, entonces sí,
cuéntala — pero en la menor cantidad de palabras posible.

### 3.5 *Barks*: las frases cortas de los NPC

Un **bark** es una línea corta que un personaje suelta sin conversación: «¡Por allí!», «Otra vez
llueve», «Yo antes era aventurero como tú». Es el mecanismo narrativo con **mejor relación entre
coste y percepción** que existe.

- **Coste**: una línea de 5-10 palabras.
- **Efecto**: el mundo parece vivo, reactivo y consciente de lo que haces.

Elan Ruskin explicó en la GDC el sistema que Valve usa para esto en *Left 4 Dead*: en lugar de
árboles de diálogo, una **base de reglas** donde cada regla exige unos criterios sobre el estado
del mundo, y **gana la regla que cumple más criterios**. Es decir: la respuesta más específica
disponible.

```
Estado del mundo (hechos):     zona = "pantano",  vida_baja = true,
                               llueve = true,     companero = "ana"

Reglas candidatas (ordenadas por nº de criterios, de más a menos):
  3 criterios  zona=pantano  &  vida_baja  &  companero=ana  → "Ana: Aguanta, ya casi salimos del agua."   ✅ gana
  2 criterios  vida_baja     &  llueve                       → "Esto no ayuda…"
  1 criterio   llueve                                        → "Otra vez lloviendo."
  0 criterios  (comodín)                                     → "Sigamos."
```

Lo elegante es que **nunca falta respuesta**: siempre hay una regla de cero criterios. Y añadir
especificidad no requiere tocar código: se añade una regla con más criterios y automáticamente
tiene prioridad. En §6.4 está implementado en GML, en 50 líneas.

Reglas de escritura de *barks*:

| Regla | Motivo |
|---|---|
| **Menos de 10 palabras** | Se leen de un vistazo, sin parar el juego |
| **Nunca información imprescindible** | El jugador puede no oírlo; si es vital, no es un bark |
| **Con enfriamiento** (*cooldown*) | Oír la misma frase dos veces seguidas mata la ilusión |
| **Variantes: 3 mínimo por situación** | Con una sola, a los cinco minutos es un loro |
| **Que reaccionen a flags** | Es la «reactividad barata» del §4.8 |

### 3.6 Diálogo de sistema: el tutorial con voz de personaje

El tutorial y los mensajes de sistema («no tienes suficiente oro», «no puedes equipar esto») son
texto que el jugador lee **seguro**. Es la superficie narrativa más leída del juego y casi nadie
la escribe.

Dos maneras de resolverlo:

| Enfoque | Cómo | Cuándo |
|---|---|---|
| **Voz neutra** | «Necesitas 50 monedas.» | Juegos con UI diegética o sin narrador |
| **Voz de personaje** | «El herrero cruza los brazos: —Cincuenta. Ni una menos.» | Cuando hay un personaje que **plausiblemente** lo diría |

> ⚠️ **La trampa clásica: el personaje que explica lo que no podría saber.** Si un NPC medieval te
> dice «pulsa X para saltar», acabas de romper tu propio mundo. Reglas:
>
> - **El personaje habla de la ficción; la UI habla de los botones.** «Salta la grieta» lo dice el
>   NPC; «[X]» lo dibuja la UI al lado.
> - Si el juego tiene un personaje que **sí** puede saberlo (una IA, un narrador explícito, un
>   fantasma que rompe la cuarta pared), aprovéchalo: es una decisión de diseño, no un accidente.
> - **Lo mejor sigue siendo no escribir el tutorial**: enseñar con el nivel.
>   → [`13 · 01 — Diseño de juego`](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) §5.

---

## 4 · Escribir el diálogo

### 4.1 Voz por personaje: la prueba de tapar el nombre

**La prueba:** tapa los nombres de quien habla en una página de tu guion. Si no puedes decir quién
dice qué, todos tus personajes son la misma persona.

Una voz se construye con cinco palancas, y con dos ya se nota:

| Palanca | Ejemplo A | Ejemplo B |
|---|---|---|
| **Longitud de frase** | «No.» | «Bueno, verás, es que depende un poco de a qué te refieras…» |
| **Vocabulario / registro** | «Optimizar la ruta» | «Ir por lo derecho» |
| **Qué pregunta** | Pregunta por el precio | Pregunta por la gente |
| **Muletillas** | «¿Sí?» al final de todo | Nunca dice el nombre de nadie |
| **Qué evita** | No habla de su familia | No dice «no» directamente |

> 💡 **Lo más rápido que puedes hacer hoy:** dale a cada personaje **una regla de habla** y
> respétala sin excepción. «El herrero nunca usa más de seis palabras.» «La alcaldesa siempre
> responde con otra pregunta.» Es artificial, es barato y funciona.

### 4.2 Subtexto: lo que la frase no dice

Diálogo malo: los personajes dicen lo que sienten. Diálogo bueno: los personajes **hablan de otra
cosa** y lo que sienten se transparenta.

```
❌  —Estoy muy enfadada porque me mentiste sobre lo del dinero.
    —Lo siento, tenía miedo de perderte.

✅  —¿Has cenado?
    —Aún no.
    —Ya. Yo tampoco.
    (silencio)
    —¿Cuánto era?
```

El truco mecánico para conseguirlo: **cada personaje entra en la escena con un objetivo distinto
y ninguno lo enuncia.** Uno quiere una disculpa, el otro quiere irse. La escena es el choque de
los dos objetivos. Por eso la **hoja de escena** del §8 pide *intención* y *obstáculo*
antes que el texto.

> 🔺 **En un juego hay un límite.** Un jugador que no entiende qué tiene que hacer se atasca.
> El subtexto va en el **cómo**, nunca en el **qué**: la información accionable —a dónde ir, qué
> objeto hace falta— se dice clara, y el sentimiento se deja debajo.

### 4.3 Corta el 30 %

Regla de oficio, sin misticismo: **coge tu guion terminado y elimina el 30 % de las palabras sin
quitar información.** Siempre se puede, y siempre queda mejor. Dónde está ese 30 %:

| Lo que sobra | Ejemplo | Queda |
|---|---|---|
| Saludos y despedidas | «Hola, buenos días. ¿Qué tal estás?» | Empieza por la segunda línea |
| Repetir lo que el jugador ya vio | «¡El puente se ha caído!» (lo viste caer) | Fuera |
| Adverbios en las acotaciones | «dijo enfadadamente» | Que lo diga la frase |
| Confirmaciones | «—Ve al molino. —Al molino. Entendido.» | Fuera la segunda |
| Explicar el chiste | «…jajaja, ¿lo pillas? Porque…» | Fuera |
| Recapitulaciones | «Como ya sabes, el rey…» | Si lo sabe, no se lo cuentes |

> 💡 **Empieza tarde, sal pronto.** La regla más rentable de la escritura de escenas: entra en la
> escena lo más tarde que puedas y sal en cuanto tengas lo que venías a buscar. La mayoría de las
> escenas mejoran borrando su primera y su última línea.

### 4.4 Léelo en voz alta

No es una recomendación estética: es un detector de errores. Leer en voz alta te dice, sin
posibilidad de autoengaño:

- Dónde te falta el aire → la frase es demasiado larga para una caja de diálogo.
- Dónde tropiezas → hay una cacofonía o un orden raro de palabras.
- Dónde te aburres al leerlo tú → el jugador se aburrirá el triple.
- Dónde suena a informe → el personaje está haciendo de wikipedia.

> 🔺 **Y hazlo en español, con las tildes puestas.** Un texto que se lee mal en voz alta se
> traduce mal, y la traducción hereda todos los defectos multiplicados
> → [`04 · 21 — Localización`](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md).

### 4.5 Cuánto texto cabe en una caja: la aritmética de la lectura

Una caja de diálogo tiene un tamaño físico y un tiempo de lectura. Los dos se calculan, no se
adivinan.

**La velocidad.** El meta-análisis de Brysbaert (2019), sobre 190 estudios y 18 573 participantes,
sitúa la lectura silenciosa de un adulto en **238 palabras por minuto en no ficción y 260 en
ficción**; la lectura en voz alta, en **183 ppm**. Para diseñar, se usa el peor caso, no la media:

| Perfil | Velocidad de diseño | Uso |
|---|---|---|
| Lector rápido | 300 ppm | No lo consideres: siempre puede pulsar para avanzar |
| **Adulto medio** | **240 ppm = 4 palabras/segundo** | La referencia |
| **Lector lento, niño, no nativo, jugando con ruido** | **160 ppm ≈ 2,7 palabras/s** | **El número con el que diseñas los subtítulos automáticos** |

⚠️ Estas cifras son de estudios en inglés. **La palabra española es más larga** (más sílabas y
más caracteres por palabra), así que en español conviene razonar **por caracteres**, no por
palabras. Regla de trabajo, no medida: **unos 15 caracteres por segundo** para un lector medio y
**10 c/s** para el caso lento. No lo he verificado contra un estudio de lectura en español.

**La cuenta que sale de ahí:**

```
Caja de diálogo de 3 líneas × 45 caracteres  =  135 caracteres
Lector medio  : 135 / 15 c/s  ≈  9 segundos
Lector lento  : 135 / 10 c/s  ≈ 13,5 segundos

Un subtítulo que se quita solo debe durar el caso LENTO.
Un texto que espera a que pulses puede ser más largo — pero no debería.
```

**Los límites prácticos que salen de eso:**

| Límite | Valor | Motivo |
|---|---|---|
| Caracteres por línea | **35-45** | Más ancho y el ojo pierde el renglón al volver |
| Líneas por caja | **2-3** | Cuatro ya parece un muro |
| Caracteres por caja | **≤ 140** | Un tuit viejo: cabe de un vistazo |
| Palabras por bark | **≤ 10** | Se lee sin dejar de jugar |
| Palabras por documento | **≤ 150** | Una pantalla sin desplazar |

> 🔺 **Escribe con el límite puesto desde el primer día.** Un guion escrito en un procesador de
> textos sin límite de caja produce párrafos que luego hay que trocear a mano, y trocear rompe el
> ritmo de las frases. Pon la restricción en la herramienta, no en la revisión.
>
> ⚠️ **Y prueba con el texto al 150 %**, que es lo que hace el ajuste de escala de texto de
> [`04 · 27 — Accesibilidad`](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) §2. Una
> caja que cabe al 100 % y revienta al 150 % es una caja mal diseñada.

### 4.6 Elecciones que importan frente a ilusión de elección

Una elección tiene tres partes, y las tres tienen que estar:

1. **Se entiende antes de elegir.** El jugador sabe *qué* está eligiendo (no necesariamente el
   resultado, pero sí la naturaleza de la apuesta).
2. **Tiene coste.** Si puedes tener las dos cosas, no has elegido.
3. **Se nota después.** Aunque sea una línea de diálogo distinta veinte minutos más tarde.

**Los cuatro tipos de elección**, por orden de coste de producción:

| Tipo | Qué cambia | Coste | Cuándo |
|---|---|---|---|
| **De sabor** | Nada, salvo la línea inmediata | Casi cero | Para dar personalidad al protagonista |
| **De reacción** | Una línea o dos, más tarde | Muy bajo | **El grueso de tu juego** |
| **De estado** | Un flag que abre o cierra contenido existente | Bajo | Puertas, precios, aliados |
| **De rama** | Una escena distinta que hay que escribir | Alto | Dos o tres en todo el juego |

**La ilusión de elección** es cuando el jugador cree haber elegido y no ha cambiado nada. No es
automáticamente una trampa: si la elección **caracteriza al protagonista** o el jugador **nunca
puede saber** que era falsa, funciona. Se vuelve dañina cuando:

- El juego **presume** de que tus decisiones importan y son de sabor.
- El jugador puede rejugar y comprobar que da igual. (Y rejuega, y lo comprueba, y lo cuenta.)
- La elección se presenta como moralmente grave y no tiene consecuencia.

> 💡 **La honestidad barata:** no anuncies reactividad que no tienes. Un juego que nunca promete
> que las decisiones cambien el final y luego cambia una línea de epílogo sorprende para bien. El
> que promete «tus decisiones importan» y no cumple, defrauda aunque tenga más reactividad que el
> primero.

### 4.7 Ramificar cuesta; converger es la solución

Ya está el número en §2.6: ramificar sin converger explota. Los tres patrones que se usan de
verdad:

```
① CUELLO DE BOTELLA (branch and bottleneck) ─ el patrón por defecto

    ┌── rama A ──┐
 ───┼── rama B ──┼───[ NUDO ]───┬── rama D ──┐
    └── rama C ──┘   flags: A|B|C            ├─── final
                                └── rama E ──┘

  · Escribes 3 + 1 + 2 = 6 escenas
  · El jugador percibe 6 recorridos
  · El nudo LEE los flags y cambia una o dos líneas: parece que arrastra todo


② RAMAS QUE CONVERGEN CON MEMORIA ─ lo mismo, más fino

    Elección ── A ──►┐
                     ├─► escena común, con líneas condicionadas por el flag
    Elección ── B ──►┘
                     "Y tú, que dejaste morir al perro, ¿qué opinas?"

  · Coste: una línea condicional. Efecto: el juego se acuerda.


③ ABANICO FINAL ─ solo al final, donde no hay que volver a converger

               ┌── final bueno
    [ NUDO ] ──┼── final neutro
               └── final amargo

  · Se ramifica de verdad SOLO al final, porque ahí no hay que reunir nada.
  · Suma de flags → índice de final. Tres finales cuestan tres escenas cortas.
```

Es también la conclusión de **Josh Sawyer** en su charla de la GDC 2012 sobre la arquitectura de
elecciones de *Fallout: New Vegas*: la estructura del árbol de diálogo de rol apenas ha cambiado
en más de una década, y lo que hace que un mundo se sienta reactivo no es la gran ramificación
divergente de la historia, sino la **reactividad de pequeña escala**, a corto y a largo plazo.
⚠️ Esta síntesis procede del resumen oficial de la charla y de fuentes secundarias que la
comentan; no he podido leer una transcripción literal. De la misma charla se cita a menudo el
«principio del lanzallamas» —que el jugador pueda matar a cualquier personaje y aun así terminar
el juego—, también ⚠️ vía fuente secundaria.

> 🔺 **Regla de presupuesto.** Cuenta las escenas antes de escribirlas. Si tu diagrama tiene más
> escenas que semanas te quedan multiplicadas por tres, el diagrama está mal, no tu velocidad.
> Recorta ramas y sube reacciones: es la conversión que salva proyectos.

### 4.8 Flags, consecuencias diferidas y reactividad barata

Un **flag** es un dato que el mundo recuerda. Es la infraestructura de todo lo anterior.

| Tipo de flag | Ejemplo | Para qué |
|---|---|---|
| **Booleano** | `salvo_al_perro = true` | El 90 % de los casos |
| **Contador** | `veces_mentiste = 3` | Umbrales: «a la tercera, deja de creerte» |
| **Enumerado** | `bando = "gremio"` | Rutas excluyentes |
| **Marca de tiempo** | `visto_en = "acto2"` | Reacciones que caducan |

**Consecuencia diferida** es un flag que se lee **mucho después** de escribirse. Es la técnica que
más impresiona por menos dinero: el jugador olvidó lo que hizo, y el juego no.

```
Acto I   · el jugador deja pasar al ladrón   → flags.dejo_ir_al_ladron = true
Acto III · en la ciudad quemada, un guardia:
             si  dejo_ir_al_ladron  → "Fue él. Tú lo dejaste ir."
             si !dejo_ir_al_ladron  → "Colgamos al culpable hace meses."
```

Una línea de código y dos frases. El jugador cuenta esto en un foro.

**Reactividad barata** es la versión industrializada de lo anterior: los *barks* y las líneas de
NPC leen flags **que ya existen** y cambian de texto. No se escribe contenido nuevo: se
condiciona el que hay.

| Nivel | Qué es | Coste | Efecto percibido |
|---|---|---|---|
| **1 · Saludo por flag** | El tendero saluda distinto si le compraste algo | 1 línea | «me reconoce» |
| **2 · Bark por estado** | Los guardias comentan tu fama | 3 líneas | «el mundo habla de mí» |
| **3 · Escena condicionada** | Una escena existente cambia 2 líneas según flags | 2 líneas | «esto es por mi culpa» |
| **4 · Rama** | Una escena nueva entera | 1 escena | «he cambiado la historia» |

> 💡 **La proporción sana en un juego de una persona:** muchísimo nivel 1 y 2, bastante nivel 3, y
> **dos o tres** cosas de nivel 4 en todo el juego, colocadas donde más se vean. Invertir al revés
> es la forma más común de no terminar un juego narrativo.

---

## 5 · Herramientas de escritura

La decisión no es «cuál es mejor», sino **quién escribe y qué exporta**. Un guion que solo puede
tocar el programador es un guion que no se revisa.

| Herramienta | Qué es | En GameMaker | Coste | Veredicto |
|---|---|---|---|---|
| **Chatterbox** + **Crochet** | Motor de diálogo en GML puro, lenguaje *ChatterScript* «basado libremente en la versión 2 de YarnScript» | **Nativo.** Es la vía normal | Gratis (MIT) | ✅ **La opción por defecto** |
| **Yarn Spinner** | El lenguaje y el conjunto de herramientas original | ❌ **No hay soporte oficial**: sus runtimes son Unity, Godot y Unreal | Gratis | Se usa **indirectamente**, vía Chatterbox |
| **ink** (inkle) | Lenguaje narrativo con *knots*, *diverts* y *weaves*; muy potente para prosa ramificada | Solo vía extensión nativa (§5.2) | Gratis | ⚠️ Con condiciones serias |
| **Twine** | Editor visual de historias por nodos, GPL-3.0, navegador y escritorio | ❌ No exporta a GameMaker | Gratis | ✅ **Para prototipar el árbol**, no para el juego final |
| **articy:draft X** | Base de datos visual de narrativa: nodos, personajes, variables, localización | ❌ Integraciones listas solo para Unity y Unreal | Versión gratuita funcional + versión de pago | Para equipos; en solitario es sobredimensionado |
| **JSON / CSV propios** | Tus propias tablas de nodos y líneas | Nativo, `json_parse` | Gratis | ✅ Para juegos con poco diálogo (§6.1) |

### 5.1 Chatterbox: lo que ya sabes y lo que aquí importa

El bucle de integración (`ChatterboxIsWaiting` → dibujar opciones o líneas → `ChatterboxContinue`
/ `ChatterboxSelect`) está explicado en
[`07 · 19 — Chatterbox`](../07%20-%20Ecosistema/19%20-%20Chatterbox%20-%20diálogos%20Yarn%20%28guía%20en%20español%29.md).
Lo que le falta a ese documento y le hace falta a un **guionista** es esto:

**La forma de un nodo** (verificada en el guion de ejemplo del proyecto de DragoniteSpam que hay
en `11 - Código descargado/plantillas_y_ejemplos/dragonitespam/TutorialChatterboxSetup/datafiles/`):

```
title: Inicio
---
Aquí van las líneas del nodo, una por línea.
Ana: Y con «Nombre:» delante, quien la dice.
===
```

**Las instrucciones que el compilador de Chatterbox reconoce** (extraídas del propio
`__ChatterboxCompile`, no de la documentación):

| Instrucción | Para qué sirve al escribir |
|---|---|
| `<<set $flag = true>>` · `<<declare>>` · `<<constant>>` | Escribir y declarar variables de la historia |
| `<<if>>` · `<<elseif>>` · `<<elif>>` · `<<else>>` · `<<endif>>` | Condicionar líneas y opciones |
| `<<jump nodo>>` · `<<hop nodo>>` | Saltar de nodo (`jump` no vuelve; `hop` apila para volver) |
| `<<jumpback>>` · `<<hopback>>` | Volver por donde viniste |
| `<<stop>>` | Terminar la conversación |
| `<<wait>>` · `<<forcewait>>` · `<<moveahead>>` | Controlar el avance del texto |
| `<<fastforward>>` · `<<fastmark>>` | Saltar tramos ya leídos |
| `<<choose>>` · `<<random option>>` · `<<option split>>` | Variar opciones |

> 💡 **`ChatterboxGetVisited(titulo_nodo, archivo)` es la función más infravalorada de la
> librería.** Te dice si un nodo ya se visitó (firma verificada en su propio `.gml`). Con eso, y sin escribir nada nuevo, un NPC puede saludarte distinto la segunda vez.
> Es reactividad de nivel 1 (§4.8) gratis.

**Localización de los guiones.** Chatterbox trae su propio sistema de IDs de línea:
`ChatterboxLocalizationBuild` etiqueta cada fragmento, `ChatterboxLocalizationExportData` saca una
estructura `[{filename, nodes:[{title, strings:[{hash, content}]}]}]` que se guarda con
`json_stringify`, el traductor la edita, y `ChatterboxLocalizationImportData` la vuelve a cargar.
Encaja con el flujo de traducción por IA de
[`04 · 21 — Localización`](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md).

> 🔺 **Aviso literal del código fuente:** «ESTA FUNCIÓN MODIFICARÁ ARCHIVOS FUENTE EN EL DISCO
> DENTRO DE TU PROYECTO. ASEGÚRATE DE HABER GUARDADO TU TRABAJO EN CONTROL DE VERSIONES.»
> `ChatterboxLocalizationExportData` **reescribe tus `.yarn`** para meterles los IDs. Haz commit
> antes.

**Crochet** es el editor visual de ChatterScript (nodos en un lienzo, como Twine), disponible para
Windows, macOS y Ubuntu y también como editor web. El propio README de Chatterbox lo recomienda
como la mejor manera de empezar. Es lo que le das a alguien que escribe y no programa.

### 5.2 ink en GameMaker: sí existe, pero léete la letra pequeña

**Sí hay runtime.** La biblioteca oficial `inkle/ink-library` lista **GMInk** («Ink integration for
Gamemaker Studio», de GMWolf, publicado en el Marketplace de GameMaker) entre los ports con
soporte, junto a los de Unity, Godot, Unreal, JavaScript, Java y Lua. Y existe un fork mantenido,
**`stalkerhumanoid/gmink-redux`**, que lo actualiza a versiones modernas.

Y aquí está la letra pequeña, que decide por ti:

| Hecho verificado en el repositorio | Consecuencia |
|---|---|
| Es una **extensión nativa de .NET/C#** que exporta `.dll` (Windows) y `.so` (Linux) | **Solo Windows y Linux.** Ni HTML5, ni Android, ni iOS, ni consolas |
| Depende de .NET 9.0.x y de ink 1.2.0 | Otra cadena de herramientas más que mantener |
| Licencia MIT | ✅ Sin problema legal |
| El autor pide mantenedor abiertamente | ⚠️ Riesgo de abandono |

> ⚠️ **Recomendación honesta:** si tu juego va a salir solo en Windows/Linux y ya sabes escribir
> en ink, es viable. En cualquier otro caso —y sobre todo si hay móvil o web en el plan— **usa
> Chatterbox**: es GML puro, corre en todos los targets y no añade una dependencia binaria a tu
> pipeline de compilación.

### 5.3 Twine para prototipar el árbol antes de programar

Twine no exporta a GameMaker y no hace falta que lo haga. Su valor es otro: **te deja ver la forma
de tu historia en media hora**, y descubrir que tienes 40 nodos y ninguna convergencia antes de
haber escrito una línea de GML.

El flujo que funciona:

```
1. Monta el ÁRBOL en Twine (solo etiquetas, sin texto: "elección del puente", "muere el perro")
2. Míralo. Cuenta los nodos. Busca las ramas que no vuelven.
3. Recorta hasta que sea un branch-and-bottleneck (§4.7).
4. AHORA escribe el texto — en Crochet/ChatterScript, o en tu JSON.
5. Tira el Twine. Ya cumplió.
```

Twine es GPL-3.0, funciona en el navegador y como aplicación de escritorio (Electron), y sus
formatos de historia son **Harlowe, SugarCube, Snowman y Paperthin**. Para prototipar da igual
cuál uses: no vas a publicar desde ahí.

> ⚠️ Existen herramientas de línea de comandos de terceros para compilar guiones de Twine
> (`.twee`) fuera del editor. **No las he verificado** contra una fuente primaria, así que no
> construyas un pipeline sobre ellas sin comprobarlo tú.

### 5.4 Tablas propias en JSON/CSV: cuándo son la respuesta correcta

Si tu juego tiene **menos de ~200 líneas de diálogo y ninguna ramificación profunda**, montar
Chatterbox es traer un camión para una caja. Una tabla basta, y encima te sale gratis la
localización, porque ya es el mismo formato que la tabla de cadenas de
[`04 · 21`](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md).

**La regla que lo hace posible: el texto nunca vive en el nodo, vive en la tabla de idiomas.** El
nodo guarda una **clave**.

```json
// datafiles/narrativa/nodos.json — la ESTRUCTURA (nunca se traduce)
{
  "herrero_intro": {
    "quien": "herrero",
    "lineas": ["dlg_herrero_intro_1", "dlg_herrero_intro_2"],
    "opciones": [
      { "clave": "dlg_op_precio",  "destino": "herrero_precio" },
      { "clave": "dlg_op_marchar", "destino": "" }
    ]
  }
}
```

```json
// datafiles/idiomas/es.json — el TEXTO (esto es lo que se traduce)
{
  "dlg_herrero_intro_1": "No compro chatarra.",
  "dlg_herrero_intro_2": "Y eso que traes es chatarra.",
  "dlg_op_precio":       "¿Cuánto por la espada?",
  "dlg_op_marchar":      "Déjalo."
}
```

> 💡 **Separar estructura de texto se paga solo el primer día y se cobra todos los demás.** El
> traductor toca un archivo y no puede romper el grafo; tú tocas el grafo y no rompes ninguna
> traducción; y el diff de git es legible.

---

## 6 · Cómo se traduce a GameMaker

Todo lo anterior se reduce a **cuatro piezas de código** que un juego narrativo necesita y que no
están en ninguna otra receta de esta biblioteca: el **modelo de datos**, los **flags guardables**,
los **disparadores** y el **gestor de misiones**. Más dos cosas que sí existen en otro sitio y aquí
solo se conectan: la **caja de diálogo** (→ [`04 · 10`](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md))
y las **Sequences** (→ [`13 · 04`](./04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md)).

### 6.1 El modelo de datos de la narrativa

Cuatro conceptos, cuatro structs. Es el mínimo que soporta condiciones, efectos y ramas.

```gml
// ---------------------------------------------------------------------------
// scr_narrativa_modelo — el grafo de diálogo como datos
// ---------------------------------------------------------------------------

/// @func Linea(_clave_texto, _quien, [_condicion])
/// @desc Una línea de diálogo. El TEXTO no está aquí: aquí está su clave.
///       El texto vive en la tabla de idiomas y se resuelve con txt().
function Linea(_clave_texto, _quien, _condicion = undefined) constructor
{
    clave     = _clave_texto;   // "dlg_herrero_intro_1"
    quien     = _quien;         // "herrero" — para el retrato y el nombre
    condicion = _condicion;     // método que devuelve bool, o undefined = siempre

    /// @desc ¿Debe verse esta línea con el estado actual del mundo?
    static visible = function()
    {
        if (is_undefined(condicion)) return true;
        return condicion();
    };
}

/// @func Opcion(_clave_texto, _destino, [_condicion], [_efecto])
/// @desc Una elección. `destino` es el id de otro nodo; "" termina la conversación.
function Opcion(_clave_texto, _destino, _condicion = undefined, _efecto = undefined) constructor
{
    clave     = _clave_texto;
    destino   = _destino;
    condicion = _condicion;
    efecto    = _efecto;        // método sin argumentos: cambia flags, da objetos…

    static visible = function()
    {
        if (is_undefined(condicion)) return true;
        return condicion();
    };

    static aplicar = function()
    {
        if (is_method(efecto)) efecto();
    };
}

/// @func Nodo(_id)
/// @desc Un nodo del grafo: unas líneas y, al final, unas opciones (o ninguna).
function Nodo(_id) constructor
{
    identificador = _id;
    lineas        = [];
    opciones      = [];
    al_entrar     = undefined;  // método: efecto que ocurre solo por llegar aquí
    al_salir      = undefined;

    static anadir_linea = function(_linea)  { array_push(lineas, _linea);  return self; };
    static anadir_opcion = function(_opcion) { array_push(opciones, _opcion); return self; };

    /// @desc Las líneas que hoy pasan su condición, ya filtradas.
    static lineas_visibles = function()
    {
        return array_filter(lineas, function(_l) { return _l.visible(); });
    };

    static opciones_visibles = function()
    {
        return array_filter(opciones, function(_o) { return _o.visible(); });
    };
}

/// @func Guion()
/// @desc El grafo completo: id de nodo → Nodo. Vive en global.guion.
function Guion() constructor
{
    nodos = {};

    static anadir = function(_nodo)
    {
        nodos[$ _nodo.identificador] = _nodo;
        return _nodo;
    };

    static obtener = function(_id)
    {
        if (!struct_exists(nodos, _id)) return undefined;
        return nodos[$ _id];
    };

    static existe = function(_id) { return struct_exists(nodos, _id); };
}

/// @func dialogo_empezar(_nodo_id)
/// @desc Arranca la conversación en el nodo indicado. Punto de entrada único desde
///       los disparadores (§6.3) y las cinemáticas (`PasoDialogo`, §6.6).
/// 🔺 Esto arranca el diálogo (pone global.dialogo_activo a true); CERRARLO —
///    ponerlo de vuelta a false cuando el jugador termina de leer— es cosa de tu
///    caja de diálogo (obj_dialogo de 13 · 24, o Chatterbox §5.1): este documento
///    modela el contenido y los disparadores, no dibuja la UI. Sin esa mitad,
///    PasoDialogo.terminado() (más abajo) nunca deja avanzar una cinemática.
function dialogo_empezar(_nodo_id)
{
    if (!global.guion.existe(_nodo_id))
    {
        show_debug_message($"dialogo_empezar: nodo inexistente '{_nodo_id}'");
        return;
    }
    global.nodo_actual    = _nodo_id;
    global.dialogo_activo = true;
    var _nodo = global.guion.obtener(_nodo_id);
    if (is_method(_nodo.al_entrar)) _nodo.al_entrar();
}
```

Montar un nodo con condición y efecto queda así de corto:

```gml
/// obj_narrativa · Create — un nodo escrito a mano
global.guion = new Guion();

// dialogo_empezar() (arriba) y PasoDialogo (§6.6) leen estas antes de que exista
// ninguna conversación — sin inicializarlas aquí, la biblioteca cinemática (y
// obj_jugador · Step de 04 · 48 §3.4.1, que lee las tres) revienta con «variable
// global no definida» en su primer uso.
global.dialogo_activo      = false;   // ninguna conversación en curso
global.nodo_actual         = "";      // "" = sin nodo activo
global.cinematica_en_curso = false;   // Cinematica.empezar()/terminar() (§6.6) la mueven

var _n = global.guion.anadir(new Nodo("herrero_intro"));
_n.anadir_linea(new Linea("dlg_herrero_intro_1", "herrero"));

// esta línea SOLO aparece si ya le compraste algo antes: reactividad de nivel 1
_n.anadir_linea(new Linea("dlg_herrero_reconoce", "herrero",
    function() { return flag_leer("compro_al_herrero"); }));

_n.anadir_opcion(new Opcion("dlg_op_precio", "herrero_precio"));

// esta opción exige una llave Y deja marcado que la enseñaste
_n.anadir_opcion(new Opcion("dlg_op_ensenar_llave", "herrero_llave",
    function() { return flag_leer("tiene_llave"); },
    function() { flag_poner("enseno_la_llave", true); }));
```

> 🔺 **Por qué `condicion` y `efecto` son métodos y no cadenas.** Un `"tiene_llave == true"` que
> hay que interpretar exige escribir un intérprete de expresiones; un método ya es GML y lo
> comprueba Feather. El precio es que **los métodos no se serializan**: nunca guardes un `Nodo` en
> la partida. Guarda solo el **id del nodo actual** y los flags. Es la misma regla que el
> `serialize()` de [`04 · 04 — RPG`](../04%20-%20Recetas%20por%20género/04%20-%20RPG%20_%20Action%20RPG.md) §6.

Si en vez de escribirlos a mano prefieres cargarlos de JSON (§5.4), el bucle de construcción es
directo, y las condiciones se resuelven mirando flags por nombre en lugar de con métodos:

```gml
/// carga el grafo desde datafiles/narrativa/nodos.json
function guion_cargar(_ruta)
{
    if (!file_exists(_ruta)) { show_debug_message($"Falta el guion: {_ruta}"); return new Guion(); }

    var _f = file_text_open_read(_ruta);
    var _crudo = "";
    while (!file_text_eof(_f)) _crudo += file_text_read_string(_f) + file_text_readln(_f);
    file_text_close(_f);

    var _datos  = json_parse(_crudo);
    var _guion  = new Guion();
    var _claves = struct_get_names(_datos);

    for (var _i = 0; _i < array_length(_claves); _i++)
    {
        var _id   = _claves[_i];
        var _def  = _datos[$ _id];
        var _nodo = _guion.anadir(new Nodo(_id));
        var _quien = struct_exists(_def, "quien") ? _def.quien : "";

        for (var _j = 0; _j < array_length(_def.lineas); _j++)
        {
            _nodo.anadir_linea(new Linea(_def.lineas[_j], _quien));
        }

        if (!struct_exists(_def, "opciones")) continue;

        for (var _j = 0; _j < array_length(_def.opciones); _j++)
        {
            var _op = _def.opciones[_j];
            // "requiere" es el NOMBRE de un flag; la condición se fabrica aquí
            var _cond = undefined;
            if (struct_exists(_op, "requiere"))
            {
                var _nombre_flag = _op.requiere;
                _cond = method({ f: _nombre_flag }, function() { return flag_leer(f); });
            }
            _nodo.anadir_opcion(new Opcion(_op.clave, _op.destino, _cond));
        }
    }

    return _guion;
}
```

> ⚠️ **`method({ f: _nombre_flag }, ...)` no es un capricho.** Sin él, todas las condiciones del
> bucle apuntarían a la **misma** variable `_nombre_flag` y todas comprobarían el último flag
> leído. `method()` con un struct propio le da a cada condición su propia copia. Es el error de
> *closure* clásico y en GML se manifiesta igual que en JavaScript.

### 6.1 bis El nodo *hub*: temas que no cierran la conversación

Todo lo anterior modela una conversación que **avanza**: cada `Opcion.destino` lleva a un nodo
distinto. Falta el patrón contrario, común en RPG y novela visual: un menú de temas donde
preguntas lo que quieras, en el orden que quieras, y la conversación **no se cierra sola** —
[Short lo llama *waypoint narrative*, §2.6](#26-las-formas-de-la-narrativa-interactiva-y-su-coste).
No hace falta ningún concepto nuevo: un `Opcion` cuyo `destino` es el **mismo** `Nodo` que la
contiene ya es un *hub*.

```gml
/// obj_narrativa · Create — un hub de temas: la posadera responde lo que le preguntes
var _hub = global.guion.anadir(new Nodo("posadera_hub"));
_hub.anadir_linea(new Linea("dlg_posadera_hub_intro", "posadera"));

// cada tema vuelve al MISMO nodo: la conversación no avanza, solo se repite el menú
_hub.anadir_opcion(new Opcion("dlg_op_preguntar_rumores", "posadera_hub",
    undefined,
    function() {
        // la PRIMERA vez la reacción es especial; a partir de la segunda, la opción
        // sigue ahí pero responde con la línea normal — flag_una_vez() nunca oculta la opción
        if (flag_una_vez("posadera_rumores_contados")) {
            bark_mostrar(txt("dlg_posadera_rumor_sorpresa"));
        } else {
            bark_mostrar(txt("dlg_posadera_rumor_repetido"));
        }
    }));

_hub.anadir_opcion(new Opcion("dlg_op_preguntar_precio", "posadera_hub",
    undefined,
    function() { bark_mostrar(txt("dlg_posadera_precio")); }));

// la salida es una opción MÁS, no un caso especial: destino "" termina la conversación (§6.1)
_hub.anadir_opcion(new Opcion("dlg_op_despedirse", ""));
```

> 🔺 **La diferencia entre un tema y un nodo normal está solo en el `destino`.** Nada en
> `Nodo` ni en `Opcion` sabe que esto es un *hub*: es la misma estructura de datos de §6.1,
> usada de forma distinta. Cero símbolos nuevos del runtime.
>
> 💡 **`flag_una_vez` decide la REACCIÓN, no la disponibilidad.** Al contrario que en una rama
> normal —donde una condición en `Opcion` puede ocultar la opción entera—, aquí la opción
> **siempre** está visible; lo único que cambia con `flag_una_vez` es qué `efecto()` dispara.
> Confundir las dos cosas es el error clásico: si condicionas la opción en vez del efecto, el
> tema desaparece del menú después de la primera vez, y deja de ser un *hub*.

### 6.2 Los flags: un struct global, plano y guardable

Un único struct, sin anidar, con claves de texto. Plano porque así se serializa sin pensar y se
mira de un vistazo en el depurador.

```gml
// ---------------------------------------------------------------------------
// scr_narrativa_flags — el estado de la historia
// ---------------------------------------------------------------------------

/// @func flags_iniciar()
/// @desc Crea el struct de flags. Se llama UNA vez, al empezar partida nueva.
function flags_iniciar()
{
    global.flags = {
        // convención: minúsculas, sin tildes, sin espacios. Son claves de datos.
        acto: 1,
    };
}

/// @func flag_leer(_nombre, [_por_defecto])
/// @desc Lee un flag. Si no existe, devuelve el valor por defecto (false).
///       NUNCA revienta: un guion viejo que pregunta por un flag nuevo sigue funcionando.
function flag_leer(_nombre, _por_defecto = false)
{
    if (!struct_exists(global.flags, _nombre)) return _por_defecto;
    return global.flags[$ _nombre];
}

/// @func flag_poner(_nombre, _valor)
function flag_poner(_nombre, _valor)
{
    global.flags[$ _nombre] = _valor;
    return _valor;
}

/// @func flag_sumar(_nombre, [_cuanto])
/// @desc Contador. Devuelve el valor nuevo. Sirve para "a la tercera mentira…".
function flag_sumar(_nombre, _cuanto = 1)
{
    var _v = flag_leer(_nombre, 0) + _cuanto;
    global.flags[$ _nombre] = _v;
    return _v;
}

/// @func flag_una_vez(_nombre)
/// @desc true la PRIMERA vez que se llama con ese nombre, false siempre después.
///       Es el patrón para "esta escena solo ocurre una vez".
function flag_una_vez(_nombre)
{
    if (flag_leer(_nombre)) return false;
    flag_poner(_nombre, true);
    return true;
}
```

**Guardar y cargar.** El struct es plano: cabe entero en la partida sin conversión, con el
`save_game` / `load_game` de [`scr_save_load`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml).

> ⚠️ **Nombradas `narrativa_*`, no `partida_*`.** `13 · 06` (Arquitectura) ya define
> `partida_cargar(_slot)` como el patrón genérico de CUALQUIER proyecto: carga + migra el
> esquema y **devuelve el struct** para que el llamador decida qué hacer con él. La de aquí es
> distinta a propósito — específica de narrativa, **aplica** el estado ella misma (flags y
> misiones) y devuelve `Bool` — así que lleva un nombre distinto para no declarar dos funciones
> con el mismo nombre y contratos incompatibles en el mismo proyecto. Si usas ambas a la vez,
> encadénalas: `narrativa_cargar()` puede llamar a `partida_migrar()` de `13 · 06` antes de leer
> `_d`, o directamente sustituir su `load_game(_slot)` por `partida_cargar(_slot)` si tu proyecto
> ya sigue esa arquitectura.

```gml
/// guardar: los flags van dentro del struct de la partida, tal cual
function narrativa_guardar(_slot)
{
    return save_game(_slot, {
        flags:      global.flags,                 // struct plano: se serializa solo
        misiones:   global.misiones.serializar(), // §6.5
        nodo_actual: global.nodo_actual,          // el id, no el Nodo
        room_actual: room_get_name(room),
    });
}

/// cargar: y el detalle que evita el 90 % de los crashes al cargar partidas viejas
function narrativa_cargar(_slot)
{
    var _d = load_game(_slot);
    if (!is_struct(_d)) return false;

    flags_iniciar();                              // 1) valores por defecto NUEVOS
    if (struct_exists(_d, "flags"))               // 2) encima, lo que traiga el save
    {
        var _k = struct_get_names(_d.flags);
        for (var _i = 0; _i < array_length(_k); _i++)
        {
            global.flags[$ _k[_i]] = _d.flags[$ _k[_i]];
        }
    }

    global.misiones = MisionesDeserializar(struct_exists(_d, "misiones") ? _d.misiones : {});
    return true;
}
```

> 🔺 **Reinicia primero, superpone después.** Si asignas `global.flags = _d.flags` de golpe,
> una partida guardada antes de que existiera `flags.acto` se carga **sin** `acto`, y el primer
> `global.flags.acto` revienta. Reiniciando y superponiendo, los flags nuevos aparecen con su
> valor por defecto y los viejos se respetan. Detalle general en
> [`01 · 14 — Persistencia y archivos`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) §8.
>
> ⚠️ **Nunca guardes handles de asset ni ids de instancia en los flags.** En 2026 los ids de
> asset son *handles*: al recargar apuntan a otra cosa. Guarda el **nombre** y resuélvelo con
> `asset_get_index` al cargar → [`01 · 03 — Handles`](../01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md).

### 6.3 Disparadores: cuándo se lanza un nodo

Tres formas de que la narrativa ocurra, de menos a más intrusiva.

```gml
// ---------------------------------------------------------------------------
// obj_disparador_zona  (Sprite: una caja invisible. Visible = false)
// Variables de instancia (en el Room Editor, Variable Definitions):
//    nodo_id   : String  — qué nodo lanza
//    una_vez   : Bool    — ¿se agota al dispararse?
//    requiere  : String  — flag necesario ("" = ninguno)
// ---------------------------------------------------------------------------

/// Create
armado = true;

/// Step
if (!armado) exit;
if (!place_meeting(x, y, obj_jugador)) exit;
if (requiere != "" && !flag_leer(requiere)) exit;

if (una_vez)
{
    // el nombre del flag lleva la room dentro: dos disparadores distintos no chocan
    if (!flag_una_vez($"visto_{room_get_name(room)}_{nodo_id}")) { armado = false; exit; }
    armado = false;
}

dialogo_empezar(nodo_id);
```

```gml
// ---------------------------------------------------------------------------
// Disparador al recoger — en el objeto del objeto recogible
// ---------------------------------------------------------------------------

/// obj_reliquia · Collision con obj_jugador
inventario_anadir(item_id);              // función de tu inventario
flag_poner($"tiene_{item_id}", true);

// la primera reliquia dice algo; las demás, no
if (flag_sumar("reliquias_recogidas") == 1) dialogo_empezar("primera_reliquia");

instance_destroy();
```

```gml
// ---------------------------------------------------------------------------
// Disparador al entrar en una room — en el gestor persistente, NO en la room
// ---------------------------------------------------------------------------

/// obj_narrativa · Room Start
var _tabla = {
    rm_cripta:  { nodo: "llegada_cripta",  requiere: "" },
    rm_torre:   { nodo: "llegada_torre",   requiere: "vio_el_mapa" },
};

var _nombre = room_get_name(room);
if (!struct_exists(_tabla, _nombre)) exit;

var _e = _tabla[$ _nombre];
if (_e.requiere != "" && !flag_leer(_e.requiere)) exit;
if (!flag_una_vez($"llegada_{_nombre}")) exit;

dialogo_empezar(_e.nodo);
```

> 💡 **Los tres comparten la misma disciplina:** condición de flag + `flag_una_vez` con una clave
> que incluye la room. Sin eso acabas con la escena de la cripta repitiéndose cada vez que
> vuelves, que es el bug narrativo número uno.
>
> 🔺 **La tabla de rooms va en el gestor persistente, no repartida por las rooms.** Es una sola
> lista que puedes leer entera; ver [`13 · 06 — Arquitectura`](./06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md).

### 6.4 Barks: reglas ordenadas por especificidad

La implementación del sistema de Ruskin (§3.5) y de la narrativa *salience-based* de Short (§2.6).
Cincuenta líneas y es lo que más hace parecer vivo a un juego.

```gml
// ---------------------------------------------------------------------------
// scr_barks — la línea más específica que encaje con el estado del mundo
// ---------------------------------------------------------------------------

/// @func BancoBarks()
function BancoBarks() constructor
{
    reglas = [];   // { criterios, claves, peso, prioridad, ultimo_us }
    prioridad_sonando = -1;   // prioridad del bark que está sonando ahora, -1 = nada sonando

    /// @func anadir(_criterios, _claves_texto, [_prioridad])
    /// @param {Struct} _criterios    hechos que deben cumplirse: { zona: "pantano", vida_baja: true }
    /// @param {Array}  _claves_texto claves de la tabla de idiomas; se elige una al azar
    /// @param {Real}   _prioridad    nivel de urgencia: mayor número corta a uno menor (§6.4)
    static anadir = function(_criterios, _claves_texto, _prioridad = 0)
    {
        array_push(reglas, {
            criterios: _criterios,
            claves:    _claves_texto,
            peso:      array_length(struct_get_names(_criterios)),   // = especificidad
            prioridad: _prioridad,
            ultimo_us: -1,   // el enfriamiento vive EN la regla, no en un índice que se reordena
        });

        // de más específica a más general: la primera que encaje es la mejor
        array_sort(reglas, function(_a, _b) { return _b.peso - _a.peso; });
        return self;
    };

    /// @func elegir(_hechos, [_cooldown_us])
    /// @desc Devuelve una clave de texto, o undefined si no hay nada que decir.
    ///       Si la regla elegida tiene más prioridad que la que suena, corta la que suena.
    static elegir = function(_hechos, _cooldown_us = 8000000)   // 8 s en microsegundos
    {
        var _ahora = get_timer();

        // lo que sonaba ya ha terminado por su cuenta: ya no hay nada que proteger
        if (prioridad_sonando >= 0 && (global.voz_actual == -1 || !audio_is_playing(global.voz_actual)))
        {
            prioridad_sonando = -1;
        }

        for (var _i = 0; _i < array_length(reglas); _i++)
        {
            var _r = reglas[_i];
            if (!encaja(_r.criterios, _hechos)) continue;

            if (_r.ultimo_us >= 0 && (_ahora - _r.ultimo_us < _cooldown_us))
            {
                continue;   // dicha hace nada: pasa a la siguiente, menos específica
            }

            // una regla MÁS urgente que lo que suena corta la línea en curso, no espera turno
            if ((_r.prioridad > prioridad_sonando) && (prioridad_sonando >= 0))
            {
                audio_stop_sound(global.voz_actual);   // global.voz_actual: 13 · 24 §3.2
            }
            else if (_r.prioridad <= prioridad_sonando)
            {
                continue;   // algo igual o más urgente sigue sonando: esta espera su turno
            }

            _r.ultimo_us = _ahora;
            prioridad_sonando = _r.prioridad;
            return _r.claves[irandom(array_length(_r.claves) - 1)];
        }

        return undefined;
    };

    static encaja = function(_criterios, _hechos)
    {
        var _k = struct_get_names(_criterios);
        for (var _i = 0; _i < array_length(_k); _i++)
        {
            if (!struct_exists(_hechos, _k[_i]))          return false;
            if (_hechos[$ _k[_i]] != _criterios[$ _k[_i]]) return false;
        }
        return true;   // un struct de criterios VACÍO encaja siempre: es el comodín
    };
}
```

```gml
/// obj_narrativa · Create — el banco se llena una vez
global.barks = new BancoBarks();

global.barks.anadir({ zona: "pantano", vida_baja: true, companero: "ana" },
                    ["bark_ana_pantano_herido"]);                       // 3 criterios
global.barks.anadir({ vida_baja: true },
                    ["bark_aguanta_1", "bark_aguanta_2", "bark_aguanta_3"]);
global.barks.anadir({ llueve: true },
                    ["bark_lluvia_1", "bark_lluvia_2"]);
global.barks.anadir({}, ["bark_generico_1", "bark_generico_2"]);        // comodín

/// obj_companero · Alarm 0 — cada pocos segundos, di algo si procede
var _hechos = {
    zona:      global.zona_actual,
    vida_baja: (obj_jugador.puntos_vida < obj_jugador.puntos_vida_max * 0.3),
    llueve:    global.clima == "lluvia",
    companero: nombre_personaje,
};

var _clave = global.barks.elegir(_hechos);
if (!is_undefined(_clave)) bark_mostrar(txt(_clave));

alarm[0] = game_get_speed(gamespeed_fps) * 6;
```

> 💡 **Lo bonito del sistema: ampliarlo no toca código.** ¿Quieres que Ana diga algo distinto en
> el pantano y de noche? Añades una regla con cuatro criterios y automáticamente gana a la de
> tres. **Nunca falta respuesta** porque la regla de cero criterios encaja siempre.
>
> 🔺 **Las claves son de la tabla de idiomas** (`txt()`), no texto suelto: un banco de *barks* con
> literales dentro es un banco que no se traduce
> → [`04 · 21`](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md).

**Prioridad, para que lo urgente no se pierda detrás de lo banal.** Un `cooldown` por regla
evita que UNA MISMA línea se repita, pero no protegía nada de que un bark banal siguiera
sonando mientras uno urgente esperaba su turno — el `elegir()` de arriba ya lo resuelve: una
regla con más `prioridad` corta con `audio_stop_sound` la que esté sonando.

```gml
/// obj_narrativa · Create — niveles de prioridad, de menos a más urgente
#macro PRIORIDAD_AMBIENTE 0
#macro PRIORIDAD_REACCION 1
#macro PRIORIDAD_URGENTE  2   // vida crítica
#macro PRIORIDAD_MISION   3   // una línea de guion no se pierde por NADA

global.barks.anadir({ llueve: true },
                    ["bark_lluvia_1", "bark_lluvia_2"], PRIORIDAD_AMBIENTE);
global.barks.anadir({ zona: "pantano", vida_baja: true, companero: "ana" },
                    ["bark_ana_pantano_herido"], PRIORIDAD_REACCION);
global.barks.anadir({ vida_baja: true },
                    ["bark_aguanta_1", "bark_aguanta_2", "bark_aguanta_3"], PRIORIDAD_URGENTE);
global.barks.anadir({ mision_urgente: true },
                    ["bark_mision_ahora_vuelve"], PRIORIDAD_MISION);
```

> ⚠️ **`global.voz_actual`, `audio_stop_sound` y `audio_is_playing`** son de
> [`13 · 24` §3.2](./24%20-%20Voz%2C%20diálogo%20y%20localización%20de%20audio.md#32-resolución-en-runtime-con-fallback-a-subtítulos):
> este `elegir()` da por hecho que quien reproduce la voz del bark guarda su *handle* ahí, tal
> y como ya hace ese documento, y que **está inicializado a `-1`** desde el arranque (antes de
> la primera voz nunca reproducida, no puede valer otra cosa). Si tu proyecto no tiene voz y
> los *barks* son solo texto, inicialízalo igual (`global.voz_actual = -1;`) y el corte de
> audio nunca se disparará solo — la prioridad sigue sirviendo para el orden de aparición del
> texto, sin tocar nada más.

**Diálogo en combate (*banter*).** Los criterios de `elegir()` son un `struct` cualquiera:
`{ en_combate: true, objetivo: "jefe" }` funciona igual que `{ zona: "pantano" }`. Lo único que
cambia en combate es CUÁNDO se le permite disparar un bark:

```gml
/// obj_jefe · Alarm 0 — bark de combate, sin pisar la ventana de impacto
var _hechos = {
    en_combate: true,
    objetivo:   "jefe",
    vida_baja:  (vida < vida_max * 0.3),
};

// nunca dispares un bark durante el hit-stop: es la pausa que vende el golpe
// (time_is_frozen(), 04 · 15 §5.0) y una línea de diálogo encima la rompe
if (!time_is_frozen())
{
    var _clave_combate = global.barks.elegir(_hechos, 3000000);   // cooldown más corto: 3 s
    if (!is_undefined(_clave_combate)) bark_mostrar(txt(_clave_combate));
}

alarm[0] = game_get_speed(gamespeed_fps) * 4;
```

> 🔺 **`time_is_frozen()` es de [`04 · 15` §5.0](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md)**,
> no de este documento: es la comprobación que ya usa el *game feel* para saber si el mundo está
> congelado por *hit-stop* o por una pausa manual. Un bark que aparece a mitad de la ventana de
> impacto rompe la sensación que el *hit-stop* estaba vendiendo — la regla no es «no interrumpas
> animaciones de ataque» en general, es específicamente «no durante la congelación».

### 6.5 Un gestor de misiones mínimo (con estado «fallada»)

⚠️ **Antes de copiar esto, comprueba si no te vale el que ya hay.** Si tu juego es un RPG con
inventario, oro y recompensas, el `QuestLog` de
[`04 · 04 — RPG`](../04%20-%20Recetas%20por%20género/04%20-%20RPG%20_%20Action%20RPG.md) §6 es más
completo que esto y ya está escrito. Lo de aquí es **la versión narrativa**: cuatro estados —
incluido **fallada**, que aquel no tiene— y ninguna dependencia de economía.

```gml
// ---------------------------------------------------------------------------
// scr_misiones — cuatro estados y nada más
// ---------------------------------------------------------------------------

#macro MISION_SIN_EMPEZAR 0
#macro MISION_ACTIVA      1
#macro MISION_COMPLETADA  2
#macro MISION_FALLADA     3

/// @func Misiones()
function Misiones() constructor
{
    estados = {};   // id → { estado, paso }

    static estado_de = function(_id)
    {
        if (!struct_exists(estados, _id)) return MISION_SIN_EMPEZAR;
        return estados[$ _id].estado;
    };

    static paso_de = function(_id)
    {
        if (!struct_exists(estados, _id)) return 0;
        return estados[$ _id].paso;
    };

    /// @desc Solo se activa lo que no se ha tocado. Una misión fallada no revive.
    static activar = function(_id)
    {
        if (estado_de(_id) != MISION_SIN_EMPEZAR) return false;
        estados[$ _id] = { estado: MISION_ACTIVA, paso: 0 };
        senal_emitir("mision_activada", _id);
        return true;
    };

    /// @desc Avanza un paso. Al llegar al total, completa.
    static avanzar = function(_id, _pasos_totales)
    {
        if (estado_de(_id) != MISION_ACTIVA) return false;
        var _e = estados[$ _id];
        _e.paso++;
        if (_e.paso >= _pasos_totales) return completar(_id);
        senal_emitir("mision_avanzada", _id);
        return true;
    };

    static completar = function(_id)
    {
        if (estado_de(_id) != MISION_ACTIVA) return false;
        estados[$ _id].estado = MISION_COMPLETADA;
        flag_poner($"mision_{_id}_completada", true);   // el diálogo lo lee como un flag más
        senal_emitir("mision_completada", _id);
        return true;
    };

    /// @desc Fallar es un final legítimo: el NPC murió, se acabó el plazo, elegiste el otro bando.
    static fallar = function(_id, _motivo = "")
    {
        if (estado_de(_id) != MISION_ACTIVA) return false;
        estados[$ _id].estado = MISION_FALLADA;
        flag_poner($"mision_{_id}_fallada", true);
        senal_emitir("mision_fallada", { id: _id, motivo: _motivo });
        return true;
    };

    static activas = function()
    {
        var _fuera = [];
        var _k = struct_get_names(estados);
        for (var _i = 0; _i < array_length(_k); _i++)
        {
            if (estados[$ _k[_i]].estado == MISION_ACTIVA) array_push(_fuera, _k[_i]);
        }
        return _fuera;
    };

    static serializar = function() { return estados; };   // plano: se guarda tal cual
}

/// @func MisionesDeserializar(_datos)
function MisionesDeserializar(_datos)
{
    var _m = new Misiones();
    if (is_struct(_datos)) _m.estados = _datos;
    return _m;
}
```

```gml
/// uso, y por qué «fallada» merece existir
global.misiones = new Misiones();

global.misiones.activar("salvar_al_boticario");

// el boticario muere en un ataque: la misión NO desaparece, se marca fallada
if (murio_el_boticario) global.misiones.fallar("salvar_al_boticario", "murio");

// y el mundo lo sabe, sin escribir contenido nuevo:
//   en el guion → new Linea("dlg_hija_reproche", "hija",
//                           function() { return flag_leer("mision_salvar_al_boticario_fallada"); })
```

> 💡 **`fallada` no es un estado técnico: es una decisión de diseño.** Un juego donde las misiones
> solo pueden estar pendientes o hechas es un juego donde el jugador no puede perder nada. El
> estado «fallada» es lo que convierte una lista de tareas en una historia.
>
> 🔺 **`senal_emitir` es del sistema de señales de
> [`04 · 16`](../04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md).** Si no lo
> tienes, sustitúyelo por una llamada directa a tu UI. Lo que importa es que el gestor de misiones
> **no dibuja nada**: avisa, y quien quiera pinta.

---

### 6.6 Cinemáticas como cola de pasos

Una cinemática es una **secuencia de pasos que terminan**. Escribirla con `alarm` encadenadas es
lo que la vuelve imposible de saltar y de reordenar. La forma que sí escala: una **cola de pasos**,
donde cada paso es un struct con `empezar()` y `terminado()`.

```gml
// ---------------------------------------------------------------------------
// scr_cinematica — cola de pasos con salto garantizado
// ---------------------------------------------------------------------------

/// @func Cinematica(_nombre)
function Cinematica(_nombre) constructor
{
    nombre    = _nombre;
    pasos     = [];
    indice    = -1;
    en_curso  = false;

    static anadir = function(_paso) { array_push(pasos, _paso); return self; };

    static empezar = function()
    {
        en_curso = true;
        indice   = -1;
        global.cinematica_en_curso = true;
        instance_deactivate_all(true);   // congela el mundo; el gestor sigue vivo
        siguiente();
    };

    static siguiente = function()
    {
        // cerrar el paso anterior si tenía limpieza
        if (indice >= 0 && indice < array_length(pasos))
        {
            var _p = pasos[indice];
            if (struct_exists(_p, "limpiar") && is_method(_p.limpiar)) _p.limpiar();
        }

        indice++;
        if (indice >= array_length(pasos)) { terminar(); return; }
        pasos[indice].empezar();
    };

    /// @desc Se llama desde el Step del gestor.
    static actualizar = function()
    {
        if (!en_curso) return;
        if (indice < 0 || indice >= array_length(pasos)) return;
        if (pasos[indice].terminado()) siguiente();
    };

    /// @desc SALTAR. Recorre los pasos que quedan aplicando solo su EFECTO,
    ///       nunca su presentación: el estado del mundo queda igual que si la
    ///       hubieras visto entera.
    static saltar = function()
    {
        for (var _i = max(indice, 0); _i < array_length(pasos); _i++)
        {
            var _p = pasos[_i];
            if (struct_exists(_p, "efecto") && is_method(_p.efecto)) _p.efecto();
            if (struct_exists(_p, "limpiar") && is_method(_p.limpiar)) _p.limpiar();
        }
        indice = array_length(pasos);
        terminar();
    };

    static terminar = function()
    {
        en_curso = false;
        global.cinematica_en_curso = false;
        instance_activate_all();
        flag_poner($"cinematica_{nombre}_vista", true);
        senal_emitir("cinematica_terminada", nombre);
    };
}
```

Los pasos son structs pequeños. Tres que cubren casi todo:

```gml
/// @func PasoEsperar(_segundos)
function PasoEsperar(_segundos) constructor
{
    duracion = _segundos;    // ← el argumento se COPIA a una variable de instancia
    fin      = 0;

    static empezar   = function() { fin = get_timer() + duracion * 1000000; };
    static terminado = function() { return get_timer() >= fin; };
}

/// @func PasoDialogo(_nodo_id)
function PasoDialogo(_nodo_id) constructor
{
    nodo = _nodo_id;

    static empezar   = function() { dialogo_empezar(nodo); };
    static terminado = function() { return !global.dialogo_activo; };
    static efecto    = function() { };   // al saltar, un diálogo no deja estado: nada que aplicar
}

/// @func PasoFlag(_nombre, _valor)
/// @desc Un paso que SOLO cambia estado. Es el que hace que saltar sea seguro.
function PasoFlag(_nombre, _valor) constructor
{
    clave = _nombre;
    valor = _valor;

    static empezar   = function() { flag_poner(clave, valor); };
    static terminado = function() { return true; };
    static efecto    = function() { flag_poner(clave, valor); };
}
```

> ⚠️ **Un método `static` NO puede leer un argumento del constructor.** Las variables `static` se
> inicializan **una sola vez, en la primera llamada** y **antes del cuerpo** de la función
> ([`01 · 04 — Structs y constructores`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) §6.5):
> el método se crea con los argumentos de **la primera instancia** y se queda con ellos para
> siempre. Todos tus pasos harían lo mismo que el primero. Por eso los tres constructores de
> arriba **copian el argumento a una variable de instancia** (`duracion`, `nodo`, `clave`) y los
> métodos leen esa. Es la misma razón por la que `Cinematica` guarda `nombre = _nombre`.

```gml
/// obj_narrativa · montar y lanzar
if (flag_una_vez("cinematica_puente_lanzada"))
{
    var _c = new Cinematica("puente");
    _c.anadir(new PasoEsperar(0.5))
      .anadir(new PasoDialogo("puente_1"))
      .anadir(new PasoFlag("vio_caer_el_puente", true))
      .anadir(new PasoDialogo("puente_2"));
    _c.empezar();
    global.cinematica = _c;
}

/// obj_narrativa · Step
if (variable_global_exists("cinematica") && global.cinematica.en_curso)
{
    global.cinematica.actualizar();
    if (keyboard_check_pressed(vk_escape)) global.cinematica.saltar();
}
```

> 🔺 **La separación `empezar` / `efecto` es la clave del salto.** `empezar` hace lo bonito;
> `efecto` hace lo que **debe pasar aunque no lo veas**. Si un paso mueve la cámara, su `efecto`
> la coloca en el destino de golpe. Si un paso da un objeto, su `efecto` lo da igual. Sin esta
> separación, saltar una cinemática deja el juego a medias — y ese es un bug que llega a la
> versión final porque nadie prueba el botón de saltar.
>
> 💡 El vídeo pregrabado y la intro con `video_open` están en
> [`04 · 00 — Anatomía de un juego completo`](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md) §4:
> es otro tipo de paso más, con su `terminado()` mirando `video_get_status()`.

### 6.7 Cinemáticas con Sequences

Cuando la cinemática es **movimiento coreografiado** —cámara, personajes que entran, un objeto que
cae— la Sequence gana a la cola de pasos: se monta en el editor, se ve mientras se hace, y no hay
que compilar para ajustar un tiempo. El manejo completo del asset está en
[`13 · 04 — Animación de sprites, Sequences y Animation Curves`](./04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md) §6.
Aquí solo lo que es propio de la narrativa:

| Necesidad narrativa | Cómo se resuelve |
|---|---|
| Lanzar una línea de diálogo en el fotograma exacto | Un **broadcast message** en la pista de la Sequence (§6.4 de aquel documento) |
| Saber cuándo terminó | `layer_sequence_is_finished(elemento)` |
| **Saltarla** | `layer_sequence_headpos(elemento, layer_sequence_get_length(elemento))`, o destruirla y aplicar los efectos a mano |
| Que el personaje real aparezca en la escena | `sequence_instance_override_object` |

```gml
/// PasoSequence — una Sequence como paso de la cola del §6.6
function PasoSequence(_seq, _capa) constructor
{
    secuencia = _seq;     // copiados a instancia: los static no ven los argumentos (§6.6)
    capa      = _capa;
    elemento  = -1;

    static empezar = function()
    {
        elemento = layer_sequence_create(capa, 0, 0, secuencia);
    };

    static terminado = function()
    {
        return (elemento == -1) || layer_sequence_is_finished(elemento);
    };

    static efecto = function()
    {
        // al saltar: llevar el cabezal al final para que sus momentos se apliquen
        if (elemento != -1) layer_sequence_headpos(elemento, layer_sequence_get_length(elemento));
    };

    static limpiar = function()
    {
        if (elemento != -1) { layer_sequence_destroy(elemento); elemento = -1; }
    };
}
```

> ⚠️ **Destruye siempre el elemento de secuencia.** Una Sequence que sobrevive a un cambio de room
> o a un salto de cinemática se queda dibujando encima de la partida. Por eso `limpiar()` existe y
> por eso la cola la llama tanto al avanzar como al saltar.

### 6.8 Saltar la cinemática: siempre, y la segunda vez sola

No es una opción de accesibilidad: es una regla. El jugador que muere ante un jefe **volverá a
entrar en esa sala**, y si tu cinemática de entrada dura veinte segundos, se los va a comer cada
vez. Es la forma más rápida de que alguien cierre tu juego.

Las tres capas, de menos a más:

1. **Se puede saltar con cualquier botón.** Siempre. Sin excepción.
2. **Un aviso visible**: «Mantén [ESC] para saltar». Mantener, no pulsar, evita el salto
   accidental — el mismo criterio que en
   [`04 · 27 — Accesibilidad`](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) §4.
3. **La segunda vez se salta sola**, o al menos se ofrece saltar de entrada.

```gml
/// obj_narrativa · Create
mantener_salto = 0;

/// obj_narrativa · Step — mantener para saltar, y aviso si ya la viste
if (variable_global_exists("cinematica") && global.cinematica.en_curso)
{
    if (flag_leer($"cinematica_{global.cinematica.nombre}_vista"))
    {
        mostrar_aviso_salto("Ya has visto esta escena · [ESC] para saltar");
    }

    if (keyboard_check(vk_escape) || gamepad_button_check(0, gp_face2))
    {
        mantener_salto++;
        if (mantener_salto > game_get_speed(gamespeed_fps) * 0.6) global.cinematica.saltar();
    }
    else mantener_salto = 0;
}
```

> 🔺 **El flag `cinematica_X_vista` lo pone `terminar()` **y** `saltar()`.** Si solo lo pusiera
> `terminar()`, quien salta la cinemática la primera vez la volvería a ver entera la segunda.

### 6.9 Subtítulos, velocidad de texto y voces

**La velocidad de texto es un ajuste, no una constante.** Tres valores y un instantáneo, guardados
con el resto de opciones. El *typewriter* que los consume ya existe: el `typista.in(velocidad)` de
[`07 · 18 — Scribble`](../07%20-%20Ecosistema/18%20-%20Scribble%20-%20texto%20rico%20%28guía%20en%20español%29.md) §3
o el efecto propio de [`04 · 10 — Visual Novel`](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md) §4.2.
Aquí solo va la política:

| Ajuste | Valor | Qué significa |
|---|---|---|
| Lenta | 0,25 car./frame ≈ **15 c/s** | El lector medio del §4.5 |
| Normal | 0,50 car./frame ≈ **30 c/s** | Por defecto |
| Rápida | 1,00 car./frame ≈ **60 c/s** | Quien relee |
| Instantánea | — | Sale entero. **Tiene que existir** |

**Cuánto dura un subtítulo que se quita solo.** Aquí sí hace falta una cuenta, y es la del §4.5
combinada con la duración real del audio si lo hay:

```gml
/// @func subtitulo_duracion(_texto, [_sonido])
/// @desc Segundos que debe permanecer en pantalla un subtítulo que NO espera pulsación.
///       Nunca menos que el audio, nunca menos que el tiempo de lectura del caso lento.
function subtitulo_duracion(_texto, _sonido = undefined)
{
    var _caracteres_por_segundo = 10;                    // caso lento del §4.5
    var _lectura = string_length(_texto) / _caracteres_por_segundo;
    var _minimo  = 1.5;                                   // ni un flash, aunque sean 3 letras

    var _audio = 0;
    if (!is_undefined(_sonido) && audio_exists(_sonido)) _audio = audio_sound_length(_sonido);

    return max(_minimo, _lectura, _audio);
}
```

```gml
/// obj_dialogo · reproducir una línea con voz, si la hay
/// La regla: MANDA EL AUDIO. El texto no desaparece antes de que la frase termine de sonar.
voz = -1;
if (audio_exists(clave_voz_actual)) voz = audio_play_sound(clave_voz_actual, 8, false);

segundos_en_pantalla = subtitulo_duracion(texto_actual, clave_voz_actual);
alarm[0] = game_get_speed(gamespeed_fps) * segundos_en_pantalla;

/// Step — si el jugador avanza a mano, corta también la voz
if (input_confirmar && voz != -1 && audio_is_playing(voz))
{
    audio_stop_sound(voz);
    voz = -1;
}
```

> 🔺 **`audio_sound_length` devuelve segundos** (verificado en el manual oficial LTS 2026) y acepta
> tanto el asset como el id de una instancia sonando. Es la única forma honesta de sincronizar:
> medir, no adivinar. La sincronización fina del *typewriter* con la voz está resuelta en
> [`04 · 10 — Visual Novel`](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md) §5.6:
> aquí solo se decide **cuánto tiempo se queda el texto**.
>
> ⚠️ **Los subtítulos son un ajuste de accesibilidad, no una función de las voces.** Tienen que
> poder activarse aunque no haya voz grabada, y describir también los sonidos importantes
> (`[puerta crujiendo]`) → [`04 · 27 — Accesibilidad`](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) §2.

### 6.10 Validar el grafo antes de jugarlo

`13 · 10` — Testing y QA no tiene ninguna sección narrativa: nada comprueba hoy que un `destino`
apunte a un nodo real, ni que todo nodo sea alcanzable. Un `id` mal escrito en un `destino` (o
un nodo que quedó huérfano al reestructurar una rama) no revienta al compilar — revienta en
mitad de la partida de un jugador, o peor, deja una opción que no lleva a ningún sitio.

Mismo espíritu que `generar_hoja_grabacion.py` (`13 · 24` §2.3): un script en Python que
recorre `datafiles/narrativa/nodos.json` (el mismo archivo que carga `guion_cargar()`, §6.1) y
falla con una lista de problemas en vez de esperar a que un jugador tropiece con ellos.

```python
# validar_grafo_narrativo.py — dos clases de bug que "compila" pero rompe la partida:
# destinos que apuntan a un nodo inexistente, y nodos a los que nunca se puede llegar.
import json, sys

ruta = sys.argv[1] if len(sys.argv) > 1 else "datafiles/narrativa/nodos.json"
nodos = json.load(open(ruta, encoding="utf-8"))

# los nodos que el JUEGO puede lanzar directamente (disparadores en GML, §6.3) no están
# en el JSON: pásalos como argumentos extra. Sin ninguno, se asume el primer nodo del archivo.
entradas = set(sys.argv[2:]) or {next(iter(nodos))}

errores = []
alcanzables = set(entradas)

for id_nodo, nodo in nodos.items():
    for opcion in nodo.get("opciones", []):
        destino = opcion.get("destino", "")
        if destino == "":
            continue   # "" es fin de conversación, válido por definición (§6.1)
        if destino not in nodos:
            errores.append(f"{id_nodo}: la opción '{opcion['clave']}' apunta a "
                            f"'{destino}', que no existe")
        else:
            alcanzables.add(destino)

huerfanos = set(nodos) - alcanzables
for id_nodo in sorted(huerfanos):
    errores.append(f"{id_nodo}: inalcanzable — ninguna opción ni entrada declarada llega aquí")

if errores:
    print(f"{len(errores)} problema(s) en el grafo:")
    for e in errores:
        print(f"  - {e}")
    sys.exit(1)

print(f"{len(nodos)} nodos, todos los destinos resuelven y todos son alcanzables.")
```

```sh
python3 validar_grafo_narrativo.py datafiles/narrativa/nodos.json posadera_hub tienda_intro
#                                                                  ↑ ids de nodo que un disparador
#                                                                    de GML puede lanzar directamente
```

> 🔺 **Las entradas son un argumento, no un descubrimiento automático.** El script solo ve el
> JSON: qué nodo lanza cada `event_create`, `event_user` o zona de interacción vive en GML
> (§6.3), no en `nodos.json`. Sin decirle cuáles son los puntos de entrada reales, el validador
> asume que solo el primer nodo del archivo es alcanzable desde fuera y marca huérfano a
> cualquier otro nodo de entrada legítimo — falso positivo, no bug real.
>
> ⚠️ **Lo que este script NO puede validar: que toda misión activable tenga un camino de código
> hacia `completar()` o `fallar()`.** Esa lógica vive en los `efecto()` de cada `Opcion`
> (funciones GML), y §6.1 ya explica por qué **los métodos no se serializan**: no están en el
> JSON, así que no hay nada que un script en Python pueda recorrer. Comprobarlo de verdad
> exigiría que cada opción declarase en los DATOS a qué misión afecta y cómo (un campo
> `efecto_mision: { id: "...", resultado: "completar" }` en vez de un método), lo que cambia el
> modelo de §6.1 y queda fuera de este documento. Si te hace falta esa garantía, es la primera
> señal de que las misiones deberían tener su propio archivo de datos, no vivir escondidas
> dentro del grafo de diálogo.

---

## 7 · Personajes y mundo

### 7.1 La ficha de personaje: cinco casillas, no cinco páginas

Un personaje de juego no necesita biografía. Necesita **cinco cosas** y las cinco caben en media
pantalla. Todo lo demás es tiempo que no estás dedicando al juego.

| Casilla | Pregunta | Por qué importa |
|---|---|---|
| **Deseo** | ¿Qué quiere ahora mismo? | Es lo que dice en la escena |
| **Necesidad** | ¿Qué le falta de verdad y no sabe? | Es su arco (§2.4) |
| **Herida** | ¿Qué le pasó para confundir las dos? | Es su motivo, y nunca se enuncia |
| **Voz** | Una regla de habla inviolable | Es lo que lo hace reconocible (§4.1) |
| **Función** | ¿Qué hace en el **juego**, no en la historia? | Si no la tiene, sobra |

La quinta casilla es la que se olvida y la que más rinde. **Función en el juego** significa: es
quien vende, quien abre la puerta, quien te da la misión, quien te enseña la mecánica. Un
personaje sin función es decoración cara.

### 7.2 NPC útiles frente a NPC decorativos

| | NPC útil | NPC decorativo |
|---|---|---|
| Qué hace | Vende, abre, guarda, informa, enseña | Está |
| Cuánto texto merece | El necesario, y reactivo | **Un bark, y nada más** |
| Cuántos necesitas | Los que pida el diseño | Muy pocos, y con función ambiental |

**La regla de producción:** cada NPC con nombre propio y árbol de diálogo cuesta entre 200 y 600
palabras, retrato, y mantenimiento cada vez que cambia la historia. Antes de crear el sexto,
pregúntate si no puede ser una línea nueva del segundo.

> 💡 **Un truco que funciona:** los NPC decorativos no hablan contigo, **hablan entre ellos**. Dos
> aldeanos comentando el ataque de anoche cuentan el mundo sin que el jugador tenga que pulsar
> nada, y no exigen árbol ni retrato. Son *barks* de dos voces (§6.4).

### 7.3 *Lore*: solo el que sirve a la mecánica

El error más caro de un juego narrativo pequeño es escribir 30 páginas de mundo antes de tener el
juego. Regla dura:

> **Si un dato del mundo no cambia lo que el jugador hace, ve o siente, no existe.**

Test de tres preguntas para cada pieza de *lore*:

1. ¿**Aparece** en el juego, en algún sitio donde alguien lo vaya a ver?
2. ¿**Explica** algo que el jugador se pregunta de verdad? (No lo que tú te preguntas.)
3. ¿**Justifica** una regla del juego? («Por eso el agua quema.»)

Si las tres respuestas son «no», va a la papelera o a una descripción de objeto (§3.2), que es
donde el *lore* opcional vive sin molestar.

### 7.4 Nombres coherentes

Un mundo se cree o no se cree por sus nombres antes que por su historia. Tres reglas baratas:

| Regla | Ejemplo |
|---|---|
| **Una fonética por cultura** | Los del norte llevan «-vik», «-holm», «-gard»; los del sur, «-ara», «-ita», «-oa» |
| **Nombres funcionales para lugares** | «Paso del Herrero», «Molino Quemado»: cuentan historia y ayudan a orientarse |
| **Longitud consistente** | Si la lengua élfica es de tres sílabas, siempre es de tres sílabas |

Para un juego con **muchos** nombres —un roguelike, un mundo generado—, los nombres se producen
igual que cualquier otro contenido procedural: con una gramática de sílabas y una **semilla**, de
modo que el mismo mundo dé siempre los mismos nombres. El principio de determinismo y el manejo de
semillas están en
[`13 · 07 — Generación procedural avanzada`](./07%20-%20Generación%20procedural%20avanzada.md) §1.1.
⚠️ Ese documento cubre ruido y terreno; **no** trae un generador de nombres hecho. La pieza que
falta es trivial:

```gml
/// @func nombre_generar(_prefijos, _nucleos, _sufijos)
/// @desc Un nombre de una gramática de sílabas. Con random_set_seed antes, es reproducible.
function nombre_generar(_prefijos, _nucleos, _sufijos)
{
    var _n = _prefijos[irandom(array_length(_prefijos) - 1)]
           + _nucleos[irandom(array_length(_nucleos) - 1)]
           + _sufijos[irandom(array_length(_sufijos) - 1)];
    return string_upper(string_char_at(_n, 1)) + string_copy(_n, 2, string_length(_n) - 1);
}

/// las tres listas SON la cultura: cambiarlas cambia el idioma del mundo entero
var _norte = nombre_generar(["bra", "hel", "sig"], ["n", "ld", "rk"], ["vik", "holm", "gard"]);
```

---

## 8 · Plantillas

Cuatro documentos. Ninguno pasa de una página, y esa es la mitad de su valor.

### 8.1 Biblia del mundo, de una página

```markdown
# <Título> · Biblia          versión: 0.1 · fecha: AAAA-MM-DD

## Premisa (UNA frase)
<Eres un cartero en un mundo que se inunda.>

## Tema (la pregunta, no la respuesta)
<¿Qué se salva cuando no cabe todo?>

## Tono
Tres adjetivos: <melancólico, seco, con humor>.
Tres referencias: <película, juego, disco>.
Lo que NUNCA aparece: <gore, romance, villano hablador>.

## El mundo en cinco hechos
1. <hecho que el jugador VE en la primera pantalla>
2. <hecho que justifica la mecánica principal>
3. <hecho que justifica al antagonista>
4. <hecho que el jugador descubre a mitad>
5. <hecho que solo se entiende al final>

## Reglas del mundo (las que afectan al juego)
- <El agua sube una vez por día de juego.>
- <Nadie sabe nadar. Nadie.>

## Reparto (una línea por persona)
| Personaje | Función en el JUEGO | Voz (una regla) |
|---|---|---|
| <nombre> | <vende / abre / enseña> | <nunca dice «no»> |

## Fuera de alcance
<Lo que NO se cuenta en este juego. Escribirlo evita escribirlo.>
```

### 8.2 Ficha de personaje

```markdown
# <Nombre>                    aparece en: <actos / zonas>

Deseo      : <lo que persigue, en una frase>
Necesidad  : <lo que le falta y no sabe>
Herida     : <el suceso pasado; NUNCA se enuncia en el juego>
Voz        : <una regla de habla inviolable>
Función    : <qué hace en la mecánica>

Relación con el protagonista : <aliado / obstáculo / espejo>
Cómo cambia si el jugador... : <flag → qué línea cambia>

Tres frases suyas (para calibrar la voz):
1. <...>
2. <...>
3. <...>

No diría nunca: <...>
```

### 8.3 Hoja de escena / diálogo

La plantilla más útil de todas. Se rellena **antes** de escribir una sola línea de diálogo.

```markdown
# Escena <id>: <nombre corto>          nodo: <id_del_nodo>

Personajes   : <quién está>
Dónde/cuándo : <sala, momento del juego>

## Intención (qué quiere cada uno, y NO lo dice)
- <A>: <quiere una disculpa>
- <B>: <quiere irse>

## Obstáculo
<Qué impide que lo consigan de inmediato.>

## Resultado
<Qué ha cambiado al terminar. Si no cambia nada, la escena sobra.>

## Flags
LEE    : <flag_1, flag_2>          ← cambian el texto
ESCRIBE: <flag_3 = true>           ← lo que esta escena deja marcado
MISIÓN : <activa / avanza / falla: id>

## Salidas
- <opción A> → <nodo destino>   (requiere: <flag>)
- <opción B> → <nodo destino>
- por defecto → <nodo destino>

## Presupuesto
Líneas: <n>   ·   Caracteres por caja: ≤140   ·   ¿Saltable?: sí
```

### 8.4 Mapa de ramas

Un diagrama de texto, en el repositorio, junto al guion. No hace falta más herramienta.

```markdown
# Mapa de ramas · acto II

LEYENDA   [N] nudo obligatorio   (f) escribe flag   <f> lee flag   ✂ rama que se puede cortar

                        ┌── mercado ──(hablo_con_lena)──┐
   [N] llegada_ciudad ──┼── muelle ───(vio_el_barco)────┼── [N] la_reunion <hablo_con_lena>
                        └── ✂ tejados ──────────────────┘         │
                                                                  ├── acepta ──(bando=gremio)─┐
                                                                  └── rechaza ─(bando=libre)──┤
                                                                                              ▼
                                                                                    [N] noche_del_dique

RECUENTO   escenas: 6 (5 si se corta «tejados»)   ·   recorridos percibidos: 3 × 2 = 6
FINALES    3, decididos por: bando + mision_dique_completada + vio_el_barco
```

> 💡 **La columna `✂` no es decorativa.** Marcar de antemano qué rama es prescindible convierte un
> recorte de alcance en una decisión de cinco minutos en vez de una crisis. Es el mismo criterio de
> [`13 · 11 — Producción, alcance y lanzamiento`](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md) §1.

---

## 9 · Checklist

**Antes de escribir una línea**

- [ ] La premisa cabe en una frase y un desconocido la entiende
- [ ] El tema está enunciado, y se afirma con una **mecánica**, no con un diálogo
- [ ] Lo que el juego premia no contradice lo que el juego cuenta (§1.4)
- [ ] Existe el mapa de ramas, y es un *branch and bottleneck*, no un árbol
- [ ] Cada escena del mapa tiene un **resultado** distinto de «pasa el rato»

**Al escribir**

- [ ] Ningún dato imprescindible vive solo en contenido opcional
- [ ] Cada personaje pasa la prueba de tapar el nombre (§4.1)
- [ ] Ninguna caja pasa de ~140 caracteres, ni ningún documento de 150 palabras
- [ ] El guion se ha leído en voz alta y se le ha quitado el 30 %
- [ ] Todo el texto sale de `txt(clave)`; ni un literal en el código
- [ ] Cada elección tiene coste, y el jugador entiende qué está eligiendo
- [ ] Hay al menos tres consecuencias **diferidas** (flag del acto I leído en el acto III)

**Al integrarlo**

- [ ] Los flags están en un struct plano y se guardan con la partida
- [ ] Al cargar se **reinicia y superpone**, nunca se asigna el struct entero (§6.2)
- [ ] Ningún disparador se repite: `flag_una_vez` con la room en la clave
- [ ] Toda cinemática es saltable, con `efecto()` aplicado al saltar
- [ ] La cinemática ya vista se anuncia como saltable la segunda vez
- [ ] La velocidad de texto es un ajuste, e incluye «instantánea»
- [ ] Los subtítulos se activan sin voz, y duran el caso lento (§6.9)
- [ ] La UI cabe con el texto al 150 % y en el idioma más largo
- [ ] Hay *barks* con al menos tres variantes y enfriamiento
- [ ] Un *bark* urgente puede cortar a uno banal que esté sonando, no solo esperar su cooldown (§6.4)
- [ ] El grafo de diálogo se ha validado: cero destinos rotos, cero nodos huérfanos (§6.10)
- [ ] Las misiones pueden **fallar**, y el mundo lo comenta

---

## 10 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Qué hacer |
|---|---|---|
| **Muro de texto** | Cuatro líneas de 60 caracteres en la primera caja | Máximo 140 car./caja. Corta el 30 % (§4.3) |
| ***Lore* por delante del juego** | 20 páginas de mundo y ningún prototipo | El test de tres preguntas del §7.3 |
| **Elecciones sin consecuencia** | El jugador rejuega y ve que da igual | O añade reactividad barata (§4.8), o no la presentes como grave |
| **Cinemática no saltable** | Abandono en el reintento del jefe | §6.8. Y el `efecto()` al saltar, o el mundo queda a medias |
| **Un solo tono para todos** | Tapas el nombre y no sabes quién habla | Una regla de habla por personaje (§4.1) |
| **Tutorial en boca de quien no lo sabría** | Un aldeano medieval te dice «pulsa X» | El personaje habla de la ficción; la UI, de los botones (§3.6) |
| **Disparador que se repite** | La escena de llegada salta cada vez que vuelves | `flag_una_vez` con la room en la clave (§6.3) |
| **Ramificar sin converger** | El acto II tiene 40 escenas y no está escrito | *Branch and bottleneck* (§4.7) |
| **Guardar el struct de nodos** | El save carga y los métodos han desaparecido | Guarda el **id** del nodo y los flags, nunca el `Nodo` (§6.1) |
| **Asignar `global.flags = _d.flags`** | Crash al cargar una partida antigua | Reinicia y superpone (§6.2) |
| **Flags con handles de asset** | Al recargar apuntan a otro sprite | Guarda el nombre, resuelve con `asset_get_index` |
| **Bark sin enfriamiento** | El compañero repite la misma frase en bucle | Cooldown + tres variantes mínimo (§6.4) |
| **Información vital en un bark** | El jugador se pierde la pista y se atasca | Un bark nunca lleva nada imprescindible |
| **Texto literal en el código** | Imposible de traducir; hay que reescribir todo | `txt(clave)` desde el primer día |
| **Documento de 600 palabras** | Nadie lee más allá del número 12 | ≤150 palabras, un hecho nuevo cada uno (§3.3) |
| **Personaje sin función** | Cuesta retrato, texto y mantenimiento, y no hace nada | La quinta casilla de la ficha (§7.1) |
| **Misión que solo puede completarse** | La lista de tareas no es una historia | El estado `MISION_FALLADA` (§6.5) |
| **Sequence que sobrevive al salto** | Dibuja encima de la partida | `limpiar()` con `layer_sequence_destroy` (§6.7) |
| **Bark urgente que no se oye** | Vida crítica avisada tarde, detrás de una línea banal | Prioridad + `audio_stop_sound` en `elegir()` (§6.4) |
| **Bark durante el *hit-stop*** | El golpe pierde fuerza porque encima habla alguien | `time_is_frozen()` antes de disparar el bark (§6.4) |
| **Opción de tema que oculta la opción tras la primera vez** | El *hub* deja de ser *hub*: el menú se vacía | Condiciona el `efecto()`, no la visibilidad de la `Opcion` (§6.1 bis) |
| **`destino` que apunta a un `id` borrado** | Una opción no lleva a ningún sitio en mitad de la partida | `validar_grafo_narrativo.py` antes de cada build (§6.10) |

---

## Ver también

**Lo que implementa lo de aquí**

- [`04 · 10 — Visual Novel y narrativa`](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md) — la caja de diálogo, el parser de guion, el *typewriter*, el *backlog* y el guardado con miniatura
- [`07 · 19 — Chatterbox`](../07%20-%20Ecosistema/19%20-%20Chatterbox%20-%20diálogos%20Yarn%20%28guía%20en%20español%29.md) — el motor de diálogo ramificado ya hecho, y su bucle de integración
- [`07 · 18 — Scribble`](../07%20-%20Ecosistema/18%20-%20Scribble%20-%20texto%20rico%20%28guía%20en%20español%29.md) — dibujar el texto con efectos, colores y máquina de escribir
- [`04 · 04 — RPG / Action RPG`](../04%20-%20Recetas%20por%20género/04%20-%20RPG%20_%20Action%20RPG.md) §6 — el `QuestLog` completo, con recompensas e inventario
- [`04 · 16 — Señales y desacoplamiento`](../04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md) — `senal_emitir` / `senal_escuchar`, usados en §6.5
- [`06 · scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml) — el guardado con escritura segura y versión de esquema

**Lo que lo rodea**

- [`13 · 01 — Diseño de juego`](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) — el core loop y la economía que tu historia no puede contradecir
- [`13 · 02 — Diseño de niveles`](./02%20-%20Diseño%20de%20niveles.md) — el ritmo en el que se incrustan los *beats*, y las líneas de guía que llevan al jugador hasta tu escena ambiental
- [`13 · 04 — Animación de sprites, Sequences y Animation Curves`](./04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md) §6 — las Sequences y sus *broadcast messages*
- [`04 · 15 — Game feel y juice`](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) §5.0 — `time_is_frozen()` y el *hit-stop* que un *bark* de combate no debe pisar (§6.4)
- [`13 · 05 — UI y UX de juego`](./05%20-%20UI%20y%20UX%20de%20juego.md) — dónde vive la caja de diálogo dentro de la interfaz
- [`13 · 07 — Generación procedural avanzada`](./07%20-%20Generación%20procedural%20avanzada.md) — determinismo y semillas, para nombres y contenido reproducibles
- [`13 · 11 — Producción, alcance y lanzamiento`](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md) — recortar ramas es recortar alcance

**Lo que conecta**

- [`04 · 00 — Anatomía de un juego completo`](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md) §4 — intro, prólogo y cinemáticas, incluido vídeo
- [`04 · 21 — Localización e idiomas`](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md) — `txt(clave)`, plurales y traducción asistida
- [`04 · 27 — Accesibilidad`](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) — subtítulos, escala de texto y *hold-to-toggle*
- [`04 · 05 — Roguelike y generación procedural`](../04%20-%20Recetas%20por%20género/05%20-%20Roguelike%20y%20generación%20procedural.md) — el género donde la narrativa emergente lleva el peso
- [`01 · 14 — Persistencia y archivos`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) §8 — JSON, `json_parse` y las trampas del guardado
- [`01 · 03 — Handles`](../01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) — por qué un flag nunca guarda un id de asset
- [`01 · 04 — Structs y constructores`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) — los constructores y `static` de §6
- [`05 · 04 — Convenciones y estilo GML`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) — nombres de flags, nodos y misiones
- [`08 · 12 — Strings`](../08%20-%20Referencia%20GML%20completa/12%20-%20Strings.md) — `string_length`, `string_split`, `string_replace_all`

---

## Fuentes

Consultadas el **6 de septiembre de 2026**.

**Teoría del oficio**

- **Janet H. Murray, *Hamlet on the Holodeck: The Future of Narrative in Cyberspace***, MIT Press,
  1997; edición actualizada 2017 (ISBN 9780262533485). De ahí la definición de **agencia**: «la
  capacidad satisfactoria de emprender acciones con sentido y ver los resultados de nuestras
  decisiones y elecciones». ⚠️ La ficha de MIT Press devolvió **HTTP 403**; la edición vigente y la
  cita se verificaron en <https://en.wikipedia.org/wiki/Hamlet_on_the_Holodeck>, que es **fuente
  secundaria**, no en el libro.
- **Henry Jenkins, «Game Design as Narrative Architecture»**:
  <http://web.mit.edu/~21fms/People/henry3/games&narrative.html> — las cuatro formas (espacio
  evocador, narrativa representada, embebida y emergente), leídas en esa página. ⚠️ La copia del
  MIT no lleva datos de publicación; el ensayo se cita habitualmente como capítulo de *First
  Person: New Media as Story, Performance, and Game* (MIT Press, 2004), dato **no verificado** en
  fuente primaria.
- **E. M. Forster, *Aspects of the Novel*** (1927) — la distinción entre historia y trama.
  ⚠️ Cita clásica ampliamente reproducida; no verificada contra una edición concreta.
- **Clint Hocking, «Ludonarrative Dissonance in Bioshock»**, **7 de octubre de 2007**. La URL
  original de Typepad está **muerta** (redirige a un aparcamiento de dominios). Texto vivo en el
  dominio del autor: <https://clicknothing.com/2007/10/07/ludonarrative-d/>
- **Sam Kabo Ashwell, «Standard Patterns in Choice-Based Games»**, *These Heterogeneous Tasks*,
  **26 de enero de 2015**:
  <https://heterogenoustasks.wordpress.com/2015/01/26/standard-patterns-in-choice-based-games/>
  — **los nombres *time cave*, *gauntlet*, *branch and bottleneck*, *quest*, *open map*, *sorting
  hat*, *loop and grow* y *floating modules* son suyos**, no de Emily Short, que los cita.
- **Emily Short, «Beyond Branching: Quality-Based, Salience-Based, and Waypoint Narrative
  Structures»**, **12 de abril de 2016**:
  <https://emshort.blog/2016/04/12/beyond-branching-quality-based-and-salience-based-narrative-structures/>
  · **«Small-Scale Structures in CYOA»**, **5 de noviembre de 2016**:
  <https://emshort.blog/2016/11/05/small-scale-structures-in-cyoa/>
- **«The significance of plot without conflict»**, blog *still eating oranges*, enero de 2013:
  <https://stilleatingoranges.tumblr.com/post/25153960313/the-significance-of-plot-without-conflict>
  — kishōtenketsu y la estructura sin conflicto. ⚠️ El blog no identifica a su autor con nombre
  propio; no se le atribuye ninguno aquí.
- **Josiah Lebowitz y Chris Klug, *Interactive Storytelling for Video Games***, Focal Press, 2011
  (ISBN 9780240817170); reeditado por Routledge en 2017 (ISBN 9781138427464). ⚠️ No se ha
  encontrado evidencia de una **segunda edición revisada**: todo apunta a una reimpresión del
  texto de 2011.

**Charlas y artículos de la industria**

- **Harvey Smith y Matthias Worch, «What Happened Here? Environmental Storytelling»**, GDC 2010
  (11 de marzo de 2010): <https://gdcvault.com/play/1012647/What-Happened-Here-Environmental> ·
  post del propio ponente <https://www.worch.com/2010/03/11/gdc-2010/> · entrevista posterior con
  citas directas de Smith (Andrea Pitzer, *Nieman Storyboard*, 14 de enero de 2011):
  <https://niemanstoryboard.org/2011/01/14/harvey-smith-on-environmental-storytelling-and-embedding-narrative/>
  ⚠️ El vídeo de GDC Vault está **tras muro de pago**: la definición citada procede de las
  diapositivas públicas y de esa entrevista, no de una transcripción literal de la charla.
- **Don Carson, «Environmental Storytelling: Creating Immersive 3D Worlds Using Lessons Learned
  from the Theme Park Industry»**, Gamasutra / *Game Developer*, **1 de marzo de 2000**:
  <https://www.gamedeveloper.com/design/environmental-storytelling-creating-immersive-3d-worlds-using-lessons-learned-from-the-theme-park-industry>
  ⚠️ Es un **artículo**, no una charla de GDC, aunque se cite muchas veces como tal.
- **Josh Sawyer, «Do (Say) The Right Thing: Choice Architecture, Player Expression, and Narrative
  Design in Fallout: New Vegas»**, GDC 2012 (5 de marzo de 2012):
  <https://www.gdcvault.com/play/1015758/Do-(Say)-The-Right-Thing>
  ⚠️ Verificados título, autor, año y resumen oficial. La preferencia por la **reactividad de
  pequeña escala** frente a la gran ramificación y el «principio del lanzallamas» proceden de
  **resúmenes secundarios**, no de una transcripción. Y una aclaración honesta: **no existe, hasta
  donde se ha podido comprobar, una taxonomía de Sawyer «reactividad inmediata / diferida /
  barata»**. La clasificación en cuatro niveles del §4.8 es de este documento, no suya.
- **Elan Ruskin, «AI-driven Dynamic Dialog through Fuzzy Pattern Matching»**, GDC 2012:
  <https://gdcvault.com/play/1015317/AI-driven-Dynamic-Dialog-through> · diapositivas
  <https://steamcdn-a.akamaihd.net/apps/valve/2012/GDC2012_Ruskin_Elan_DynamicDialog.pdf>
  ⚠️ El PDF no se pudo abrir (excede el límite de la herramienta de descarga) y el vídeo está tras
  muro de pago: el mecanismo de «gana la regla con más criterios» se verificó en un resumen
  técnico de terceros.
- **Mark Brown, «Super Mario 3D World's 4 Step Level Design»**, *Game Maker's Toolkit*, marzo de
  2015: <https://www.youtube.com/watch?v=dBmIkEvEBtA> ⚠️ Divulgación secundaria; el propio vídeo
  atribuye el modelo de cuatro pasos a **Koichi Hayashida**, director del juego.

**Velocidad de lectura**

- **Marc Brysbaert, «How many words do we read per minute? A review and meta-analysis of reading
  rate»**, *Journal of Memory and Language*, vol. 109, art. 104047, 2019. 190 estudios y 18 573
  participantes: **238 ppm** en no ficción, **260 ppm** en ficción, **183 ppm** en voz alta. PDF:
  <https://gwern.net/doc/psychology/linguistics/2019-brysbaert.pdf>
  ⚠️ Los estudios son en **inglés**. La conversión a caracteres por segundo para español del §4.5
  (15 c/s medio, 10 c/s lento) es una **regla de trabajo de este documento**, no un resultado del
  estudio.

**Herramientas (abiertas y verificadas el 6 de septiembre de 2026)**

- **Yarn Spinner**: <https://docs.yarnspinner.dev/> — runtimes oficiales para **Unity, Godot y
  Unreal**. No hay soporte de GameMaker.
- **Chatterbox** (JujuAdams): <https://github.com/JujuAdams/Chatterbox>. El README y el código se
  leyeron en el espejo local `11 - Código descargado/librerias/dialogos-y-narrativa/Chatterbox`.
  Las instrucciones de ChatterScript salen de `__ChatterboxCompile`, y la API de localización
  (`ChatterboxLocalizationBuild` / `ExportData` / `ImportData`, con su aviso de que reescribe los
  archivos fuente) de los propios scripts.
- **Crochet** (FaultyFunctions), editor visual de ChatterScript:
  <https://github.com/FaultyFunctions/Crochet> · editor web <https://faultyfunctions.github.io/Crochet/>
- **Guion Yarn de ejemplo** del que se extrajo la forma `title:` / `---` / `===`:
  `11 - Código descargado/plantillas_y_ejemplos/dragonitespam/TutorialChatterboxSetup/datafiles/DialogueExample.yarn`
- **ink** (inkle): <https://www.inklestudios.com/ink/> · biblioteca oficial de ports
  <https://github.com/inkle/ink-library> — **GMInk** («Ink integration for Gamemaker Studio», de
  GMWolf, publicado en el Marketplace) figura ahí entre los ports con soporte.
- **gmink-redux** (stalkerhumanoid): <https://github.com/stalkerhumanoid/gmink-redux> — extensión
  **.NET/C#** que exporta `.dll` (Windows) y `.so` (Linux); .NET 9.0.x, ink 1.2.0, licencia MIT, y
  el autor pide mantenedor abiertamente. De ahí la limitación de plataformas del §5.2.
- **Twine**: <https://github.com/klembot/twinejs> — GPL-3.0, navegador y escritorio (Electron);
  formatos de historia **Harlowe, SugarCube, Snowman y Paperthin**. ⚠️ `twinery.org` devolvió
  **HTTP 403**; los datos salen del repositorio oficial.
- **articy:draft X**: <https://www.articy.com/en/articydraft/overview/> — integraciones listas para
  **Unity y Unreal**, gestión de localización, y una versión gratuita funcional. No menciona
  GameMaker.

**GameMaker (fuentes primarias)**

- Manual oficial LTS 2026, **`audio_sound_length`**: devuelve la duración **en segundos** y acepta
  tanto el asset de sonido como el id de una instancia en reproducción. Espejo local en
  [`09 · audio_sound_length`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Audio/audio_sound_length.md)
  · <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Audio/audio_sound_length.htm>
- Manual oficial LTS 2026: **`audio_play_sound`**, **`audio_is_playing`**, **`layer_sequence_*`**,
  **`json_parse`**, **`json_stringify`**, **`struct_get_names`** y **`array_filter`** — espejo local
  en `09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/`.

**Verificación**

Todos los símbolos de GML de este documento se comprobaron con
`python3 "_indice/buscar.py" <símbolo>` contra el `GmlSpec.xml` del runtime **2026.0.0.23**.
Las funciones y constructores de los ejemplos que **no** son del runtime —`flag_leer`,
`flag_poner`, `flag_sumar`, `flag_una_vez`, `flags_iniciar`, `guion_cargar`, `nombre_generar`,
`subtitulo_duracion`, `dialogo_empezar`, `bark_mostrar`, `narrativa_guardar`, `narrativa_cargar`,
`mostrar_aviso_salto`, `inventario_anadir`, `txt`, `senal_emitir`, `save_game`, `load_game`,
`MisionesDeserializar`, `time_is_frozen`, y los constructores `Linea`, `Opcion`, `Nodo`, `Guion`,
`BancoBarks`, `Misiones`, `Cinematica`, `PasoEsperar`, `PasoDialogo`, `PasoFlag`,
`PasoSequence`— son código de esta biblioteca, no API de GameMaker. `save_game` y `load_game`
vienen de [`scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml); `txt` de
[`04 · 21`](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md);
`senal_emitir` de [`04 · 16`](../04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md);
`time_is_frozen` de [`04 · 15 — Game feel y juice`](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) §5.0.
`global.voz_actual`, `audio_stop_sound` y `audio_is_playing` en el `BancoBarks` de §6.4 siguen
el patrón ya establecido en [`13 · 24`](./24%20-%20Voz%2C%20diálogo%20y%20localización%20de%20audio.md) §3.2 y §7,
verificados contra el runtime como el resto de funciones de este párrafo.
Las funciones `Chatterbox*` son de la librería de JujuAdams y **no están en `buscar.py`**: se
verificaron leyendo su código fuente en `11 - Código descargado`.
