# 20 · Modelo de negocio, monetización y ética del diseño

> Cómo se **diseña** el negocio de un juego, no cómo se programa. Elegir modelo (premium, demo,
> F2P, DLC, suscripción, pase de temporada, early access) y medir su efecto en el resto del
> diseño; decidir qué se vende y qué no; reconocer un patrón oscuro y tener la alternativa
> honesta a mano; entender qué es una caja de botín y qué dice la ley sobre ella; diseñar para
> un jugador que no quiere que el juego le gane la vida; y saber si tu juego pequeño necesita
> live ops (probablemente no) y qué números merece la pena mirar.
>
> **Qué NO cubre, y dónde está:** la API de anuncios, compras integradas, logros, tablas de
> puntuación y nube —
> [04 · 20 — Servicios de plataforma](../04%20-%20Recetas%20por%20género/20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md)
> y su resumen para móvil en
> [04 · 28 §10](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#10--monetización-y-servicios).
> El precio, las regiones, los plazos de Steam y la clasificación por edades —
> [13 · 11 §6.7](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#67-fecha-precio-y-regiones)
> y [§9](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#9--legal-y-administrativo-mínimo).
> Este documento enlaza los tres y no repite ninguno.
>
> **Hueco de diseño detectado:** la biblioteca sabía **llamar a la API** de IAP y anuncios, y
> sabía **fijar el precio**, pero no decía **qué poner dentro de la tienda ni por qué**. La
> plantilla de GDD ya señalaba el hueco explícitamente —
> [13 · 14 §2 fila 2.16](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#2--el-método-paso-a-paso):
> «monetización ⚠️ sin plantilla propia en esta biblioteca». Este documento la escribe.

---

## 1 · Los principios

### 1.1 · Esto es diseño, no la API ni el aviso legal

Tres preguntas que no tienen respuesta en una función de GML ni en una cláusula legal:

1. **¿Qué modelo de negocio hace que el juego que quieres diseñar sea posible de sostener?** Un
   metroidvania narrativo de 8 horas y un juego de cartas con partidas de 3 minutos no deberían
   monetizar igual, aunque los dos usen la misma extensión de IAP.
2. **¿Qué le vendes al jugador sin dejar de ser justo con él?** Esto no lo decide la tienda: lo
   decides tú, antes de abrir el editor de recursos.
3. **¿Qué harías si nadie te vigilara?** Todo patrón oscuro de §1.6 es legal en la mayoría de
   jurisdicciones. Que sea legal no lo hace defendible, y un estudio pequeño vive de la
   reputación mucho más tiempo del que vive de un solo lanzamiento.

El resto de este documento trata de responder a las tres sin recurrir ni a `steam_set_achievement`
ni a un abogado.

> **Lo que este documento NO cubre:** el riesgo legal de construir tu modelo de negocio sobre
> la propiedad intelectual de un tercero — un fan game, un homenaje que se acerca demasiado a una
> marca registrada, merchandising con personajes que no son tuyos. Esa es una pregunta de
> **antes** de diseñar la economía, no de cómo monetizarla, y tiene su propio documento:
> [13 · 25 — Legal de terceros: marcas, fan games y parodia](./25%20-%20Legal%20de%20terceros%20-%20marcas%2C%20fan%20games%20y%20parodia.md).

### 1.2 · El menú de modelos, y su efecto en el resto del diseño

No hay un modelo «mejor»: cada uno **reordena las prioridades de todo lo demás que vas a diseñar**.
Elegirlo tarde es rediseñar por segunda vez.

| Modelo | Qué compra el jugador | Riesgo principal | Efecto en el resto del diseño | Encaja mejor en |
|---|---|---|---|---|
| **Premium** (pago único) | El juego completo, de una vez | El precio es un techo: sin ventas nuevas salvo descuentos | Ningún sistema necesita frenar al jugador para monetizar; dificultad y progresión sirven solo a la experiencia | Juegos de autor, narrativos, con alcance acotado ([13 · 11 §1](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#1--alcance-el-único-problema-que-de-verdad-mata-juegos)) |
| **Demo** | Una porción gratis, y de tiempo ilimitado | Decidir **dónde cortar**: en un gancho, no en el aburrimiento ni en la mejor escena | Obliga a que el primer acto esté más pulido que el resto, y a que el [onboarding de 13 · 01 §5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#5--onboarding-enseñar-sin-texto) no falle nunca | La estrategia jam → itch.io → Steam y [Next Fest](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#64-steam-next-fest) de 13 · 11 §6.4-6.5 |
| **F2P** (free-to-play) | Nada obligatorio; todo lo demás es opcional | La economía tiene que financiar el juego sin frustrar a quien no paga | La progresión, la dificultad y la economía dual (§1.4) quedan **supeditadas a la conversión**: cambia el orden de prioridades del diseño entero | Móvil, multijugador con base de jugadores grande, juego como servicio |
| **DLC / expansión** | Contenido añadido después de comprar el juego base | Percepción de «me vendiste el juego cortado» ([*Pre-Delivered Content*, Zagal et al. §4.2.2](#16--catálogo-de-patrones-oscuros-y-su-alternativa-honesta)) | El juego base **tiene que sentirse completo por sí solo**; el DLC amplía, no completa | RPG, sandbox, estrategia: géneros cuyos sistemas aguantan una segunda vuelta |
| **Suscripción** | Acceso mientras se paga, nunca propiedad | El *churn* (abandono) mata el negocio si el contenido no fluye sin parar | Convierte el diseño en **un compromiso de producción indefinido**: incompatible con «un juego, se termina» | Catálogos de varios juegos o servicios; rara vez encaja en un solo juego indie |
| **Pase de temporada** | Una vía de progresión temporal con recompensas propias | Se convierte en F2P disfrazado en cuanto una recompensa da **poder**, no cosmético | Exige una **cadencia de contenido por temporadas**, que compite de frente con «no hacer live ops» (§1.8) | Juegos multijugador con jugador recurrente; mal encaje en una campaña de un jugador y final cerrado |
| **Early Access** | El juego incompleto, a precio reducido | Las expectativas del comprador: hay que comunicar el roadmap de verdad ([13 · 11 §7](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#7--post-lanzamiento)) | Fuerza transparencia y una cadencia de parches visible desde el primer día | Juegos de sistemas o simulación que se benefician de feedback en vivo; el argumento de vertical slice de [13 · 11 §1.4](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#14-prototipo-mvp-y-vertical-slice-tres-cosas-distintas) aplicado a todo el juego |

> 💡 **Combinar modelos es la norma, no la excepción.** Premium + DLC es el patrón más estable
> para un estudio pequeño: cobras una vez por un juego completo, y si funciona, financias una
> expansión con las ventas del original en vez de apostar el proyecto entero a una economía F2P
> que no has probado nunca.
>
> 🔺 **El modelo se elige en la ficha de una página (§6.1), no a mitad de producción.** Cambiar
> de premium a F2P a los seis meses no es «ajustar el precio»: es rediseñar la curva de
> dificultad, la progresión y la economía desde cero, porque cada una servía a un objetivo
> distinto.

### 1.3 · Qué se vende y qué no: pay-to-win con criterio

«Pay-to-win» se usa como insulto y rara vez como criterio. Hay un espectro, y el punto donde deja
de ser aceptable es más objetivo de lo que parece:

| Qué se vende | Ejemplo | ¿Es pay-to-win? |
|---|---|---|
| **Cosmético puro** | Skins, monturas, colores de arma, tarjetas de perfil | No. No cambia ni una cifra de la simulación |
| **Conveniencia** | Slots de inventario extra, ahorro de tiempo de viaje, un segundo espacio de guardado | Gris. Aceptable **si el ritmo base no se diseñó artificialmente lento para forzar la compra** — eso ya no es conveniencia, es *Pay to Skip* (§1.6) |
| **Poder cosmético-funcional** | Un arma con las mismas estadísticas que la gratuita, distinto aspecto | No, mientras sea verificable: si tiene las mismas cifras, publícalas |
| **Poder real en PvE** | Un objeto que hace al jugador más fuerte contra la IA | Gris. Nadie más pierde por tu ventaja; sigue siendo relevante si crea presión social o mata el reto que el juego prometía |
| **Poder real en PvP o ranking** | Un objeto que hace al jugador más fuerte contra otros jugadores | Sí. Es exactamente lo que Zagal et al. llaman *Monetized Rivalries* (§4.2.3): «una carrera armamentística virtual entre rivales» |
| **Contenido ya incluido en el disco, bloqueado** | Personajes que ya están en el ejecutable pero exigen un pago aparte | Nunca. Es *Pre-Delivered Content* (§4.2.2): el jugador percibe, con razón, que pagó por un juego incompleto a propósito |

**El criterio operativo, en una pregunta:** *¿puede un jugador que solo pagó la entrada ganarle a
otro que solo pagó la entrada, siempre, a base de habilidad?* Si la respuesta deja de ser «sí» en
cuanto añades una compra, esa compra es pay-to-win, la llames como la llames.

> ⚠️ Hay un patrón adicional, más lento y más difícil de señalar con el dedo: el **desgaste por
> *power creep*** — un objeto comprado pierde valor relativo cuando sale contenido nuevo más
> fuerte, y el jugador necesita comprar de nuevo para seguir siendo competitivo. Está descrito en
> la sección monetaria de darkpattern.games («*an item that you purchased in the game may
> depreciate in value because of power-creep… and you may need to make additional purchases to
> remain competitive*»). Diseñar contra esto es simple de enunciar y difícil de mantener: cada
> vez que subas el techo de poder, decide explícitamente si lo comprado antes sigue siendo
> relevante, y dilo en las notas del parche.

### 1.4 · La economía de negocio con el vocabulario de 13 · 01 §4

El vocabulario de *pool*, fuente, sumidero, convertidor e intercambiador de
[13 · 01 §4.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#41--el-vocabulario-correcto)
describe la economía de juego. La economía de **negocio** es la misma economía con una entrada
más: el dinero real.

| Pieza | En la economía de negocio |
|---|---|
| **Pool** | El saldo de moneda dura (comprada) y de moneda blanda (ganada jugando) — dos *pools* distintos, nunca uno |
| **Fuente** | Anuncio recompensado, recompensa de conexión diaria, logro, o **la propia compra con dinero real** |
| **Sumidero** | Gastar en la tienda, apostar en una caja de botín, pagar por saltarse un muro |
| **Convertidor** | El pack que cambia moneda dura por moneda blanda |
| **Intercambiador** | Un mercado entre jugadores, si existe — y entonces necesita su propia fricción contra el lavado de bienes robados con tarjetas de crédito ajenas |

**La regla que ya conoces, aplicada al dinero real.** [13 · 01 §4.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#43--la-regla-que-evita-el-80--de-los-desastres-de-economía)
dice que todo recurso necesita un sumidero o se infla hasta no significar nada. Aplicado a una
moneda premium: si solo la puedes **comprar** y nunca **gastar de forma legible**, el precio deja
de significar algo — que es exactamente el patrón *Premium Currency* de §1.6: un tipo de cambio
difícil de calcular oculta el precio real de cada objeto.

**La regla de un solo sentido, ya escrita en [13 · 16 §2.6](./16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md#26-el-patrón-de-monedas-múltiples-partida-frente-a-meta),
se aplica igual aquí:** dinero real → moneda dura → moneda blanda circula en un solo sentido.
Que **no** se pueda revertir (no hay «cobro» de vuelta a dinero real) es, en la mayoría de
jurisdicciones, el motivo técnico por el que una caja de botín normal no se clasifica como juego
de azar con premio en metálico — aunque sí como algo que hay que declarar por separado (§1.5). El
día que tu juego permita canjear moneda del juego por dinero real o por objetos con valor de
reventa fuera de tu plataforma, has cambiado de categoría legal y esto deja de ser un documento
de diseño para ser un caso de asesoría con un abogado de tu jurisdicción.

### 1.5 · Cajas de botín: mecánica, adicción y estado legal

**La mecánica** es siempre la misma: dinero real (o moneda comprada con dinero real) a cambio de
una recompensa **aleatoria** de valor variable. Cambia el envoltorio —caja, sobre, gacha,
invocación—, no la estructura.

**Por qué engancha.** Es un programa de refuerzo de razón variable, la estructura psicológica
que darkpattern.games resume en su categoría de patrones psicológicos: «*Variable Rewards:
unpredictable or random rewards are more addictive than a predictable schedule*» — verificado en
<https://darkpattern.games/pattern/4/psychological-dark-patterns.html> (06-09-2026). No es una
opinión de diseño: es la misma estructura de refuerzo que las máquinas tragaperras.

**Por qué Zagal et al. NO la llaman, por sí sola, un patrón oscuro.** Su definición de patrón
oscuro exige que el jugador actúe **sin su consentimiento informado** y en contra de su propio
interés. Sobre el azar con dinero, el paper es explícito: *«we do not consider gambling (or
betting) as a dark pattern, because players are complicit in the interaction. Even in cases
where the odds are distinctly against the player, the player has presumably made an informed
decision to participate»* (Zagal, Björk y Lewis, *Dark Patterns in the Design of Games*, FDG
2013, §4.2). **La palabra clave es «informada».** Todo lo que oculta la probabilidad real —el
propio objeto de §1.6 *Artificial Scarcity*, una tasa de cambio confusa, una interfaz que no deja
ver las probabilidades antes de pagar— rompe esa condición y convierte la caja de botín en un
patrón oscuro por la puerta de atrás.

**El estado legal, verificado hoy.** PEGI —el sistema paneuropeo de clasificación por edades, ya
usado en [13 · 11 §9.4](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#94-clasificación-por-edades-pegi-esrb-e-iarc)—
ya tenía un descriptor «*In-Game Purchases*» y otro «*Paid random items*» (verificado en
<https://pegi.info/index.php/page/game-purchases> y en el filtro de búsqueda de
<https://pegi.info/what-do-the-labels-mean>, 06-09-2026). El **12 de marzo de 2026** PEGI anunció
un cambio sustancial, verificado en
<https://pegi.info/index.php/news/pegi-expands-age-rating-criteria-interactive-risk-categories>:
a partir de junio de 2026, esos descriptores **empiezan a determinar la edad mínima por sí
mismos**, no solo a aparecer como aviso:

| Elemento | Efecto en la clasificación (cita textual) |
|---|---|
| **Compras de contenido con tiempo u oferta limitada** | «*games with time-limited or quantity-limited offers will be classified with a PEGI 12*» |
| **NFT o mecánicas de cadena de bloques** | «*games with NFTs or blockchain-related mechanisms will be PEGI 18*» |
| **Objetos aleatorios de pago (*paid random items*)** | «*the default rating will be PEGI 16 if the game contains paid random items (and in some cases they can be a PEGI 18)*» |
| **Jugar por cita** (recompensas por volver) | «*mechanisms that reward returning to the game (e.g. daily quests) will get a PEGI 7. If these mechanisms punish players for not returning… they will become PEGI 12*» |
| **Comunicación totalmente sin restricciones** | «*if games contain entirely unrestricted communication features… they will be PEGI 18*» |

PEGI desarrolló el cambio junto con **USK** (el organismo alemán), que ya lo aplicó en 2023: *«at
least one of the new USK criteria has been applied to approximately 30% of all games… Around 1 in
3 of those games have been given a higher age rating as a result»* — cita de Elisabeth Secker
(USK) en el mismo comunicado. Es la prueba de que esto no es cosmético: mueve clasificaciones de
verdad.

⚠️ **Lo que esta biblioteca NO verificó hoy**, y que debe consultarse antes de decidir nada con
implicaciones legales reales:
- La prohibición de cajas de botín con posibilidad de canje o venta como juego de azar en
  **Bélgica** y la clasificación equivalente en **Países Bajos**, ampliamente citadas desde 2018:
  no se abrió ninguna fuente oficial de esos dos países en esta sesión.
- Los requisitos de **divulgación obligatoria de probabilidades** de las tiendas de aplicaciones
  (Apple y Google los exigen desde hace años para cualquier mecánica de recompensa aleatoria
  comprable): no se abrió la página vigente de ninguna de las dos tiendas hoy.
- La regulación específica de China y Japón (gacha), que es la más antigua y detallada del mundo
  en este tema: no se abrió ninguna fuente china o japonesa hoy.

**El diseño honesto, con lo que sí está verificado:**

1. **Declara las probabilidades exactas**, no un rango. El código de §3.1 obliga a que la tabla
   que le enseñas al jugador sea la misma que usa el sorteo, no una aproximación de marketing.
2. **Usa piedad (*pity*)**, no probabilidad uniforme pura. El mecanismo entero —con las constantes
   verificadas contra *Dota 2*— ya está en
   [13 · 13 §5.7](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md#57--crítico-con-piedad-pity):
   no lo repitas, aplícalo a tu tabla de botín en vez de a un crítico de combate.
3. **Ofrece la compra directa del objeto concreto** como alternativa a la caja, aunque cueste más:
   es la diferencia completa entre vender un objeto y vender una apuesta.
4. **Nunca la vendas a una cuenta declarada como menor de edad** si tu plataforma tiene esa señal
   (ver `GMEXT-PlayAgeSignals` y `GMEXT-DeclaredAgeRange` en
   [04 · 28 §10](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#10--monetización-y-servicios)).

### 1.6 · Catálogo de patrones oscuros (y su alternativa honesta)

Dos fuentes, verificadas hoy, que se citan entre sí: el paper académico que **definió** el
concepto — Zagal, Björk y Lewis, *Dark Patterns in the Design of Games*, FDG 2013 (PDF
descargado y leído de <http://www.fdg2013.org/program/papers/paper06_zagal_etal.pdf>) — y el
catálogo práctico que lo usa como cita en sus cuatro páginas de categoría —
<https://darkpattern.games/> (patterns.php y las cuatro páginas de categoría, 06-09-2026).

**La definición que Zagal et al. acaban fijando**, tras descartar dos versiones más simples:
*«a dark game design pattern is a pattern used intentionally by a game creator to cause negative
experiences for players that are against their best interests and happen without their
consent»*. Las dos palabras que importan son **intencionalidad** y **consentimiento**: un
tutorial que confunde por error no es un patrón oscuro; una mecánica diseñada para que el
jugador no note cuánto está gastando, sí.

#### Temporales — te cuestan tiempo que no ibas a dar

| Patrón | Qué hace | Alternativa honesta |
|---|---|---|
| **Grinding** como coerción | Repetir tareas tediosas es la única vía de progreso, y el jugador nuevo no puede calcular cuánto tiempo hace falta | Publica el tiempo medio hasta cada hito; si el grindeo existe para vender un *Pay to Skip* (fila siguiente), dilo con esas palabras en tu propia cabeza antes de justificarlo con «rejugabilidad» |
| **Jugar por cita** (*Playing by Appointment*) | El juego exige volver a horas fijas, y penaliza con pérdida de valor («*withering*») si no vuelves | Recompensa por volver, nunca castigo por no volver: es exactamente la frontera que PEGI acaba de trazar en §1.5 (PEGI 7 frente a PEGI 12) |
| **Cinta sin fin** (*Infinite Treadmill*) | No hay forma de «terminar» ni de que el progreso se detenga sin perder terreno | Un techo de progresión visible, o una meta que el jugador puede alcanzar y quedarse ahí sin penalización |
| **Esperas artificiales** (*Wait To Play*) | Temporizadores que no cumplen ninguna función de diseño salvo vender la opción de saltarlos | Si el temporizador no aporta nada al ritmo del juego sin monetización, no lo pongas |

#### Monetarios — te cuestan más dinero del que creías gastar

| Patrón | Qué hace | Alternativa honesta |
|---|---|---|
| **Pay to Skip** | El ritmo base se diseña deliberadamente lento para que pagar sea la única salida razonable | Diseña el ritmo para que sea disfrutable sin pagar; vende **adelantar**, no **desatascar** |
| **Moneda premium opaca** | Un tipo de cambio difícil de calcular esconde el precio real de cada objeto, y sobra siempre un resto sin gastar | Precio en la moneda que el jugador entiende (o al menos, muéstralo también en ella) y sin restos imposibles de agotar |
| **Monetized Rivalries** (*Pay to Win*) | «*una carrera armamentística virtual entre rivales*» — pagar para ganar en un ranking o contra otros jugadores | Separar PvP competitivo de cualquier venta de poder; vender solo cosmético en los modos donde otros jugadores pierden por tu compra |
| **Escasez artificial** | «*Limited time offers with unnecessary urgency*» — presión de FOMO sin motivo real de escasez | Si la oferta puede repetirse el mes que viene, no digas que es «única»: la mentira se descubre y cuesta más confianza que la venta que ganaste |
| **Compras accidentales** | Interfaz que facilita pagar sin confirmación ni forma de deshacer | Confirmación explícita siempre, y ruta de reembolso visible — ver §1.5 y la [política de Steam](https://store.steampowered.com/steam_refunds/) |

#### Sociales — usan tus relaciones como palanca

| Patrón | Qué hace | Alternativa honesta |
|---|---|---|
| **Pirámide social** | Invitar amigos da beneficios, y sin un número mínimo de amigos jugando el progreso es casi imposible: el jugador siente que **debe** reclutar | Beneficios por invitar sin que el juego se vuelva injugable sin invitados; el consentimiento de los invitados también importa |
| **Suplantación / Spam de amigos** | El juego publica acciones que el amigo nunca hizo, o envía mensajes en su nombre | Nunca publiques nada en nombre de otra cuenta sin una acción explícita de esa cuenta en ese momento |
| **Miedo a perderse algo** (FOMO) | Contenido nuevo constante hace que dejar de jugar se sienta como quedarse atrás para siempre | Si el contenido perdido vuelve a estar disponible más adelante, dilo. Si de verdad se pierde, esa es una decisión de diseño que hay que poder defender, no ocultar |

#### Psicológicos — usan sesgos cognitivos, no relaciones ni tiempo

| Patrón | Qué hace | Alternativa honesta |
|---|---|---|
| **Recompensas variables** | Las recompensas aleatorias e impredecibles enganchan más que un calendario predecible — la base de §1.5 | Transparencia de probabilidades (§3.1) es la única forma honesta de seguir usando este patrón, que también es divertido cuando no oculta nada |
| **Coleccionarlo todo** | El impulso de completar una colección hace que un jugador compre lo que le falta, aunque no lo quisiera | Que la colección sea opcional de verdad: sin ella no debe faltar contenido jugable, solo un logro cosmético |
| **Progreso invertido** (*Endowed Progress*) | Empezar una barra ya al 20 % hace que abandonarla cueste más que empezarla vacía | Es un truco de motivación legítimo cuando el progreso es real; deja de serlo si el 20 % inicial es falso o cuesta dinero rellenarlo antes de tiempo |

**La pregunta guía de Zagal et al. para lo que no está en esta tabla**, aplicable a cualquier
mecánica nueva que se te ocurra: *¿puede el jugador desarrollar una idea razonable de cuánto le
va a costar —en tiempo o en dinero— antes de comprometerse? ¿Es probable que se arrepienta? ¿Lo
sabría si se lo preguntases en voz alta, delante de otras personas?* Si la respuesta a la última
es que preferirías no preguntarlo, ya tienes la respuesta.

### 1.7 · Juego responsable

**El principio de divulgación**, citado por Zagal et al. desde Berdichevsky y Neuenschwander:
*«el conocimiento de la presencia de mecanismos persuasivos puede sensibilizar a los usuarios y
reducir su eficacia; por eso los creadores de una tecnología persuasiva deberían divulgar sus
motivaciones, métodos y resultados pretendidos»*. Traducido a un checklist de diseño:

- **El jugador puede saber, en todo momento, cuánto tiempo lleva jugando.** Un reloj de sesión
  visible (§3.3) no es una concesión: es la condición mínima para que jugar siga siendo una
  decisión informada.
- **Ningún aviso de sesión penaliza quedarse ni premia especialmente seguir.** El aviso existe
  para informar, no para generar culpa por parar ni FOMO por no continuar (§1.6).
- **Las herramientas de control parental existen y se explican.** PEGI las documenta así:
  *«pueden limitar y monitorizar su gasto en línea, controlar el acceso a la navegación por
  internet y la interacción en línea (chat), y fijar el tiempo que los niños pueden dedicar a
  jugar»* (<https://pegi.info/index.php/page/game-purchases>, 06-09-2026). Si tu juego vende algo
  o tiene chat, comprueba que esas herramientas de la plataforma lo cubren; no dependas solo de
  tu propio interruptor.
- **Las probabilidades de cualquier mecánica de azar están donde se ven antes de pagar**, no en
  un menú de tres niveles de profundidad.

> ⚠️ Los límites legales de tiempo de juego para menores que existen en algunos países (el caso
> más citado es China) no se verificaron con una fuente oficial en esta sesión: si publicas en
> un mercado con ese tipo de regulación, es un requisito de cumplimiento, no una sugerencia de
> diseño, y hay que comprobarlo en la fuente vigente de ese mercado.

### 1.8 · Retención y live ops — y el argumento de no hacerlas

**Retención** es la fracción de jugadores que vuelve N días después de instalar el juego. Las
tres cifras estándar del oficio son **D1, D7 y D30**: qué porcentaje de los que jugaron el día 0
todavía juega al día siguiente, a la semana y al mes. **Live ops** (*live operations*) es la
disciplina de mantener un juego como servicio: temporadas con calendario, eventos limitados,
recompensas por conexión diaria, y un pase de temporada (§1.2) como columna vertebral de todo
ello.

**El ciclo de una temporada**, en su forma mínima: anuncio → ventana de eventos con recompensas
exclusivas → cierre con recompensa final → transición a la siguiente temporada sin que el
jugador sienta que perdió algo que no pudo recuperar (contrasta con *Playing by Appointment*,
§1.6). Cada paso necesita: contenido nuevo listo con antelación, un equipo que lo mantenga
mientras el anterior aún corre, y un plan de qué pasa si la temporada N+1 se retrasa mientras la
N ya cerró.

**El argumento de NO hacerlo, para un estudio pequeño**, con base en lo que ya está escrito en
esta biblioteca:

1. **El alcance es lo que mata proyectos** ([13 · 11 §1.1](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#11-el-principio)),
   y live ops es, por definición, un alcance que nunca termina: cada temporada exige la
   siguiente, indefinidamente, con el mismo equipo que apenas terminó el juego base.
2. **Necesitas infraestructura que esta biblioteca no cubre para un solo desarrollador**:
   backend con autoridad de servidor, monitorización en vivo, moderación y un canal de soporte
   para cuando algo se rompe en producción durante un evento con fecha de caducidad. Nada de eso
   está en el catálogo de [04 · 20](../04%20-%20Recetas%20por%20género/20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md):
   esa receta cubre logros, anuncios, IAP y nube, que son servicios de plataforma, no un backend
   propio de eventos en vivo.
3. **Prometer una temporada que no puedes sostener cuesta más confianza que no prometerla nunca.**
   Es la misma lógica del roadmap público de [13 · 11 §7](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#7--post-lanzamiento):
   «pon menos de lo que crees que vas a hacer», llevada a su extremo razonable: si tienes dudas
   reales de poder sostener una segunda temporada, no anuncies la primera como si hubiera una
   segunda asegurada.
4. **La alternativa que da la mayor parte del beneficio por una fracción del coste**: parches de
   contenido gratuito, sin cadencia prometida ni fecha de caducidad — el patrón de «parches»
   descrito en 13 · 11 §7, que ya recomienda notas de parche aunque sean tres líneas «porque son
   la prueba visible de que el juego está vivo». Eso da la sensación de vida de un live service
   sin la obligación de sostenerlo indefinidamente.

⚠️ Este argumento es un razonamiento de esta biblioteca a partir de lo que ya documenta sobre
alcance y producción, no una estadística de una fuente primaria abierta hoy sobre la tasa de
cierre de juegos como servicio: no lo cites como dato, cítalo como criterio.

**Cuándo SÍ tiene sentido**: el juego es multijugador con una base de jugadores que ya existe
antes de la primera temporada, el equipo tiene un rol dedicado solo a contenido en vivo (no el
mismo que mantiene el motor), y el modelo de negocio (F2P o pase de temporada, §1.2) depende
estructuralmente de la recurrencia. Si alguna de las tres no se cumple, no hagas live ops:
lanza el juego terminado y, si funciona, decide la primera expansión con datos reales en la
mano, no con un roadmap escrito antes del lanzamiento.

> 💡 **No confundas esto con la pieza técnica mínima.** El argumento de arriba es contra un
> **servicio en vivo completo** (temporadas, equipo dedicado, contenido sin fin). Poder apagar un
> evento roto o forzar una actualización crítica sin esperar la revisión de una tienda es otra
> cosa mucho más barata, que sí tiene sentido para cualquier estudio por pequeño que sea: la
> pieza puramente técnica —config remota, feature flags graduales, versión mínima del cliente,
> MOTD, modo mantenimiento— está en
> [`04 · 52 — Live-ops técnico`](../04%20-%20Recetas%20por%20género/52%20-%20Live-ops%20técnico%20%28config%20remota%2C%20versi%C3%B3n%20m%C3%ADnima%2C%20mensajes%20del%20juego%29.md),
> y no exige ni el equipo dedicado ni el compromiso de temporadas que sí exige lo de arriba.

### 1.9 · KPIs de producto y el embudo de tienda

**KPIs de producto** (definiciones, no benchmarks — los umbrales «buenos» varían tanto por
género y plataforma que citar una cifra suelta sería inventar precisión donde no la hay):

| KPI | Fórmula | Para qué sirve |
|---|---|---|
| **Retención D1 / D7 / D30** | jugadores activos el día N ÷ jugadores que instalaron el día 0 | Si D1 es bajo, el problema está en los primeros minutos (onboarding, [13 · 01 §5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#5--onboarding-enseñar-sin-texto)); si D30 es bajo pero D1/D7 son altos, el problema es de contenido a medio plazo |
| **Duración media de sesión** | tiempo jugado ÷ número de sesiones | Compárala con el bucle de sesión que fijaste en tu [GDD de una página](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#81--gdd-de-una-página--plantilla): si difieren mucho, o el bucle está mal medido o el jugador juega distinto de lo previsto |
| **Tasa de conversión** | jugadores que pagan ÷ jugadores totales | Solo tiene sentido con modelo F2P o con IAP opcional; en premium puro no aplica |
| **ARPU / ARPPU** | ingreso total ÷ jugadores totales (ARPU) o ÷ jugadores que pagaron (ARPPU) | ARPPU alto y conversión baja describe una economía que depende de pocos jugadores que gastan mucho: revisa si alguno de los patrones de §1.6 está detrás |
| **LTV** (valor de vida) | ingreso medio esperado por jugador durante toda su relación con el juego | Solo es fiable con datos acumulados de varios meses; con una semana de datos es una extrapolación, no una medida |

**El embudo de tienda**, de fuera hacia dentro: **impresión** (alguien ve tu ficha en una lista) →
**vista de página** → **lista de deseados** → **compra** → **reembolso**. Los tres últimos pasos
ya están medidos en esta biblioteca:

- Las **listas de deseados** como métrica de arrastre, con los tramos de referencia (< 6 000,
  7 000-10 000, 10 000-20 000) y la conversión de deseados a ventas (15 % / 20 % / 25 % según el
  volumen), están en
  [13 · 11 §6.3](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#63-las-wishlists-como-métrica).
  No las repitas aquí: para un primer juego, la métrica útil es **la velocidad** de entrada semanal
  y qué la provocó, tal y como ya dice esa sección.
- El **reembolso** tiene una definición operativa exacta en Steam, verificada en
  <https://store.steampowered.com/steam_refunds/> (06-09-2026): *«Valve will… issue a refund for
  any reason, if the request is made within the required return period, and… the title has been
  played for less than two hours»* — 14 días y menos de 2 horas jugadas para el juego base; 14
  días para el **DLC**, con la misma condición de menos de 2 horas jugadas desde que se compró,
  «*so long as the DLC has not been consumed, modified or transferred*»; y **48 horas** para
  compras dentro del juego («*in-game purchases*»), y solo en juegos donde el propio desarrollador
  activó esa opción. Steamworks calcula tu **tasa de reembolso** como devoluciones ÷ compras en
  un periodo, y avisa de que sube tras cada descuento porque parte de quien compró en oferta
  también pide la devolución — verificado en
  <https://partner.steamgames.com/doc/finance/refunds> (06-09-2026). **Una tasa de reembolso que
  sube después de un parche concreto es la señal de balance más barata que vas a tener**: alguien
  jugó, no le gustó lo que vio, y te lo dijo con la cartera antes de escribir una reseña negativa.

**Cuántos datos hacen falta para que un número signifique algo.** ⚠️ No hay una cifra universal
verificada hoy para esto; la heurística de oficio, coherente con la de
[13 · 01 §7.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#73--cuánta-gente-cada-cuánto)
para playtesting (cinco personas sacan el 85 % de los problemas de usabilidad), es la misma idea
aplicada a KPIs: **una cohorte de menos de unas pocas decenas de jugadores nuevos por día es
ruido**, y un D7 calculado sobre 10 instalaciones no predice nada. Espera a acumular cohortes
antes de decidir que un número «bajó» o «subió».

---

## 2 · El método, paso a paso

### 2.1 · Elegir el modelo antes de diseñar ningún sistema

```
¿El juego es multijugador con base de jugadores propia o planeada desde el diseño?
│
├─ NO → ¿Es un juego corto (< 4 h) o de autor?
│        ├─ SÍ → Premium. Sin DLC salvo que el juego tenga éxito y pidas una expansión después.
│        └─ NO → Premium + DLC planeado para 6-12 meses después del lanzamiento.
│
└─ SÍ → ¿El equipo tiene (o puede tener) un rol dedicado solo a contenido en vivo?
         ├─ NO → F2P o premium con cosméticos, SIN pase de temporada (§1.8: no hagas live ops).
         └─ SÍ → F2P o premium + pase de temporada, con el checklist ético de §2.4 en cada
                  recompensa antes de aprobarla.
```

Este árbol se rellena en la [plantilla de §6.1](#61--modelo-de-negocio-en-una-página) antes de
tocar el editor de recursos, exactamente igual que el GDD de una página se rellena antes de
programar ([13 · 01 §8.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#81--gdd-de-una-página--plantilla)).

### 2.2 · Diseñar el catálogo de la tienda

1. **Clasifica cada objeto vendible** en cosmético, conveniencia o poder (tabla de §1.3) **antes**
   de ponerle precio. El código de §3.2 convierte esta clasificación en una comprobación
   automática.
2. **Fija de 3 a 5 escalones de precio** y no más: un catálogo con veinte precios distintos no se
   recuerda ni se compara, y la comparación es lo que ayuda a decidir.
3. **Cadencia de ofertas**: sigue las reglas ya verificadas de Steam en
   [13 · 11 §6.7](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#67-fecha-precio-y-regiones)
   (no se puede bajar el precio en los primeros 30 días; 30 días de espera tras subirlo antes de
   poder ofrecer descuento). Diseña tu calendario de ofertas alrededor de esas ventanas, no en
   contra de ellas.
4. **Cada oferta pasa por la hoja de §6.2** antes de publicarse: si no puedes rellenar la
   columna «alternativa honesta si esto fuera un patrón de §1.6», no la publiques todavía.

### 2.3 · Diseñar un pase de temporada sin que sea F2P disfrazado

Un pase de temporada tiene dos vías de recompensa, gratis y premium, sobre la misma barra de
progreso. La línea que decide si es honesto:

- **Todo lo que da poder o ventaja jugable va en la vía gratis**, o no va en absoluto. Un arma
  con mejores estadísticas exclusiva del pase premium es *Monetized Rivalries* con un nombre más
  amable.
- **La vía premium vende tiempo y cosmético, no ventaja**: acceso anticipado a recompensas que
  todos obtendrán igual, más cosméticos exclusivos, más una curva de XP algo más generosa —
  nunca estadísticas.
- **El pase caduca con la temporada, pero lo comprado no se pierde nunca.** Si un jugador pagó y
  no llegó a nivel 50, esa compra sigue siendo suya: dale una vía de recuperarlo (XP acelerada
  retroactiva, o que el pase no expire hasta completarse) en vez de que el dinero pagado
  desaparezca sin más — esto es lo que distingue un pase de temporada honesto de un *Pay to Skip*
  con calendario.

El modelo de datos completo está en §3.5.

### 2.4 · El filtro ético: pasar cada elemento monetizable por la pregunta correcta

Antes de dar por bueno cualquier objeto, oferta o mecánica de la tienda, respóndelas en orden. En
cuanto una respuesta sea «no», vuelve a diseñar ese elemento, no lo publiques con un «pero es
solo esta vez»:

1. ¿El jugador puede calcular, antes de pagar, exactamente qué va a recibir y con qué
   probabilidad? (§1.5, §3.1)
2. ¿Puede un jugador que solo pagó la entrada seguir ganando por habilidad? (§1.3)
3. ¿Esta mecánica seguiría existiendo si no diera dinero — o solo existe para vender la forma de
   saltársela? (§1.6, *Pay to Skip*)
4. ¿Se lo explicarías al jugador con las mismas palabras que usaste para diseñarla, en voz alta,
   delante de otras personas de tu equipo? (la pregunta de cierre de §1.6)
5. ¿Un menor de edad identificado como tal en tu plataforma queda excluido de esto? (§1.5)

### 2.5 · Decidir retención/live ops con presupuesto, no con ambición

Antes de aprobar cualquier plan de live ops, escribe el coste en las mismas unidades que usa
[13 · 11 §1.2](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#12-estimar-multiplica-por-tres)
para estimar el resto del proyecto (multiplica por tres tu primera estimación): horas de diseño,
arte y programación **por temporada**, multiplicadas por el número de temporadas que te
comprometes a sostener antes de poder parar sin quedar mal con la comunidad. Si esa cifra es
mayor que el tiempo que tardaste en hacer el juego entero, la respuesta de §1.8 es que no.

---

## 3 · Cómo se traduce a GameMaker

Los cuatro fragmentos siguientes cubren lo que **no** está ya resuelto en otro documento: la
mecánica de sorteo con piedad ya existe en
[13 · 13 §5.5 y §5.7](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md#57--crítico-con-piedad-pity),
la llamada a la tienda ya existe en
[04 · 20](../04%20-%20Recetas%20por%20género/20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md),
y el pipeline de telemetría a JSON ya existe en
[13 · 01 §9.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#95--telemetría-contar-muertes-por-sala-y-volcarlas-a-json).
Aquí solo se añade la capa de **diseño de negocio** sobre esas piezas.

### 3.1 · Tabla de probabilidades declarada

El requisito de §1.5 —que la tabla que ve el jugador sea la misma que usa el sorteo— se cumple
generando las dos del mismo dato, nunca escribiéndolas por separado:

```gml
/// scr_caja_botin — declarar las probabilidades ANTES de escribir el sorteo.
/// Si no puedes generar este texto a partir de tus propios datos de balance,
/// no tienes transparencia real: la tienes en un README que nadie va a leer.

/// @func caja_botin_crear(_nombre, _objetos)
/// @desc Convierte pesos relativos en probabilidades exactas, una sola vez.
/// @param {String} _nombre
/// @param {Array<Struct>} _objetos  cada uno { id, rareza, peso }
/// @return {Struct}  { nombre, objetos: [{ id, rareza, peso, probabilidad }] }
function caja_botin_crear(_nombre, _objetos)
{
    var _peso_total = 0;
    for (var _i = 0; _i < array_length(_objetos); _i++)
    {
        _peso_total += _objetos[_i].peso;
    }

    var _tabla = { nombre: _nombre, objetos: [] };
    for (var _i = 0; _i < array_length(_objetos); _i++)
    {
        var _o = _objetos[_i];
        array_push(_tabla.objetos, {
            id           : _o.id,
            rareza       : _o.rareza,
            peso         : _o.peso,
            probabilidad : _o.peso / _peso_total
        });
    }
    return _tabla;
}

/// @func caja_botin_declarar(_tabla)
/// @desc El texto que va en la ficha de la tienda Y en la propia UI de la caja.
///       Es literalmente la misma fuente: no puede desincronizarse con el sorteo.
/// @param {Struct} _tabla  la que devuelve caja_botin_crear()
/// @return {String}
function caja_botin_declarar(_tabla)
{
    var _texto = $"Probabilidades de «{_tabla.nombre}»:\n";
    for (var _i = 0; _i < array_length(_tabla.objetos); _i++)
    {
        var _o = _tabla.objetos[_i];
        _texto += $"  {_o.id} ({_o.rareza}): {string_format(_o.probabilidad * 100, 1, 2)} %\n";
    }
    return _texto;
}

/// @func caja_botin_abrir(_tabla, _estado_piedad)
/// @desc El sorteo en sí, sobre la MISMA tabla declarada. La piedad (bad-luck
///       protection) se aplica con critico_tirar() de 13 · 13 §5.7 sobre la
///       rareza más alta, no aquí de nuevo: no dupliques ese algoritmo.
/// @param {Struct} _tabla
/// @return {String}  el id del objeto obtenido
function caja_botin_abrir(_tabla)
{
    var _tirada = random(1);
    var _acumulado = 0;
    for (var _i = 0; _i < array_length(_tabla.objetos); _i++)
    {
        _acumulado += _tabla.objetos[_i].probabilidad;
        if (_tirada < _acumulado) return _tabla.objetos[_i].id;
    }
    return _tabla.objetos[array_length(_tabla.objetos) - 1].id;   // margen de error de coma flotante
}
```

```gml
/// Uso, en la definición de contenido (no en el sorteo):
global.caja_temporada_1 = caja_botin_crear("Sobre de Temporada 1", [
    { id: "cosmetico_capa_azul",   rareza: "comun",     peso: 60 },
    { id: "cosmetico_capa_dorada", rareza: "raro",      peso: 30 },
    { id: "cosmetico_capa_mitica", rareza: "legendario", peso: 10 },
]);

// La ficha de la tienda y el botón "ver probabilidades" llaman a la MISMA función:
etiqueta_probabilidades = caja_botin_declarar(global.caja_temporada_1);
```

> 🔺 **Nunca escribas las probabilidades del texto de marketing a mano.** Si la ficha de la
> tienda dice "5 % de probabilidad de legendario" y el peso real en `balance.json` da un 4,2 %,
> tienes una discrepancia que un jugador con calculadora va a encontrar y publicar. Genera el
> texto desde `caja_botin_declarar()`, cópialo, y no lo vuelvas a tocar a mano.

### 3.2 · Detector de pay-to-win: auditar el catálogo

La clasificación de §1.3 y la pregunta 2 del filtro de §2.4, convertidas en una comprobación que
corre sobre tu propio `balance.json` de tienda antes de cada build:

```gml
/// scr_catalogo_tienda — clasificar y auditar lo que se vende.

enum CategoriaVenta { COSMETICO, CONVENIENCIA, PODER }

/// @func objeto_tienda_declarar(_id, _categoria, _afecta_combate)
/// @param {String} _id
/// @param {Real}   _categoria       un valor de CategoriaVenta
/// @param {Bool}   _afecta_combate  true si cambia alguna cifra de daño, vida o velocidad
/// @return {Struct}
function objeto_tienda_declarar(_id, _categoria, _afecta_combate)
{
    return { id: _id, categoria: _categoria, afecta_combate: _afecta_combate };
}

/// @func catalogo_auditar_pay_to_win(_catalogo)
/// @desc Aplica la pregunta 2 de 13 · 20 §2.4 a cada objeto. Un array vacío está
///       bien; cada id que aparece aquí es una decisión que alguien del equipo
///       tiene que poder defender en voz alta, no un bug que arreglar solo.
/// @param {Array<Struct>} _catalogo  objetos creados con objeto_tienda_declarar()
/// @return {Array<String>}  ids en conflicto
function catalogo_auditar_pay_to_win(_catalogo)
{
    var _alertas = [];
    for (var _i = 0; _i < array_length(_catalogo); _i++)
    {
        var _o = _catalogo[_i];
        if (_o.categoria == CategoriaVenta.PODER && _o.afecta_combate)
        {
            array_push(_alertas, _o.id);
        }
    }
    return _alertas;
}
```

```gml
/// obj_debug_tienda · Create — correr la auditoría al arrancar en modo debug
if (DEBUG_MODE)
{
    var _alertas = catalogo_auditar_pay_to_win(global.catalogo_tienda);
    if (array_length(_alertas) > 0)
    {
        show_debug_message($"[AUDITORÍA TIENDA] {array_length(_alertas)} objeto(s) venden poder: "
                          + string(_alertas));
    }
}
```

### 3.3 · Temporizador de sesión responsable

El requisito de §1.7: el jugador puede saber, sin preguntar, cuánto lleva jugando. `get_timer()`
devuelve microsegundos desde el arranque, igual que en el patrón de telemetría de
[13 · 01 §9.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#95--telemetría-contar-muertes-por-sala-y-volcarlas-a-json):

```gml
/// obj_control · Create
sesion_inicio_ms       = get_timer();
sesion_aviso_cada_min  = 60;      // configurable en Opciones; nunca oculto al jugador
sesion_ultimo_aviso    = 0;       // cuántos avisos ya se mostraron

/// obj_control · Step (basta comprobarlo una vez por segundo, no cada frame)
if (current_time mod 1000 < 20)   // aproximación barata a "una vez por segundo"
{
    var _minutos_jugados = floor((get_timer() - sesion_inicio_ms) / 1000000 / 60);
    var _avisos_debidos  = floor(_minutos_jugados / sesion_aviso_cada_min);

    if (_avisos_debidos > sesion_ultimo_aviso)
    {
        sesion_ultimo_aviso = _avisos_debidos;
        mostrar_aviso($"Llevas {_minutos_jugados} min jugando.");   // mostrar_aviso: 04 · 20 §3
    }
}
```

> 🔺 **El aviso se puede cerrar en un toque y no penaliza nada si se ignora.** La versión oscura
> de esto —reducir una recompensa, cerrar una oferta con cuenta atrás, o exigir una confirmación
> incómoda para seguir jugando— es exactamente *Playing by Appointment* al revés (§1.6): no la
> implementes aunque «solo sea para recordar, con un empujoncito».

### 3.4 · Embudo de tienda: telemetría reutilizada

`telemetria_registrar()` de 13 · 01 §9.5 no se toca: el embudo de tienda son eventos más, con su
propio `tipo`. Esto es una lista de llamadas, no una función nueva:

```gml
/// Al abrir la tienda in-game
telemetria_registrar("tienda_abierta", { origen: "menu_pausa" });

/// Al ver una oferta concreta el tiempo suficiente para que cuente como "vista"
telemetria_registrar("oferta_vista", { oferta_id: "pack_inicial" });

/// Al confirmar la compra — ANTES de que la extensión de la tienda la resuelva
/// (el flujo real de compra está en 04 · 20 §4, evento Async - IAP)
telemetria_registrar("oferta_comprada", { oferta_id: "pack_inicial", precio_usd: 4.99 });

/// Si tu juego puede saberlo (algunas tiendas lo notifican): un reembolso
telemetria_registrar("oferta_reembolsada", { oferta_id: "pack_inicial" });
```

Leído con la misma herramienta que 13 · 01 §9.6 ya recomienda:

```sh
jq '{
  tienda_abierta:  [.eventos[] | select(.tipo=="tienda_abierta")]  | length,
  oferta_vista:    [.eventos[] | select(.tipo=="oferta_vista")]    | length,
  oferta_comprada: [.eventos[] | select(.tipo=="oferta_comprada")] | length
} | . + { conversion_vista_a_compra_pct:
          (if .oferta_vista > 0 then (.oferta_comprada / .oferta_vista * 100) else 0 end) }' \
  telemetria.json
```

```json
{ "tienda_abierta": 40, "oferta_vista": 25, "oferta_comprada": 3, "conversion_vista_a_compra_pct": 12 }
```

Con cinco testers esto es ruido (§1.9); con la telemetría de un playtest cerrado de verdad, es la
misma pregunta que la de muertes por sala pero aplicada a la tienda: **¿qué paso del embudo
pierde más gente, y por qué**.

### 3.5 · Modelo de datos de un pase de temporada

Solo el modelo de datos y la entrega de recompensas — el cobro del pase en sí es una compra no
consumible más, ya resuelta en
[04 · 20 §4](../04%20-%20Recetas%20por%20género/20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md#4--compras-integradas-iap):

```gml
/// scr_pase_temporada — el modelo de datos de §2.3, no el cobro.

/// @func pase_temporada_crear(_xp_por_nivel)
/// @param {Array<Real>} _xp_por_nivel  la XP que exige cada nivel, en orden
/// @return {Struct}
function pase_temporada_crear(_xp_por_nivel)
{
    var _pase = { nivel: 0, xp: 0, premium: false, niveles: [] };
    for (var _i = 0; _i < array_length(_xp_por_nivel); _i++)
    {
        array_push(_pase.niveles, {
            xp_necesaria       : _xp_por_nivel[_i],
            recompensa_gratis  : undefined,   // se rellena al diseñar el contenido de la temporada
            recompensa_premium : undefined,   // NUNCA una recompensa que afecte a la §1.3: solo cosmético/tiempo
        });
    }
    return _pase;
}

/// @func pase_temporada_sumar_xp(_pase, _cantidad)
/// @desc Sube de nivel las veces que hagan falta y entrega cada recompensa una sola vez.
function pase_temporada_sumar_xp(_pase, _cantidad)
{
    _pase.xp += _cantidad;
    while (_pase.nivel < array_length(_pase.niveles)
        && _pase.xp >= _pase.niveles[_pase.nivel].xp_necesaria)
    {
        _pase.xp -= _pase.niveles[_pase.nivel].xp_necesaria;
        pase_temporada_entregar(_pase, _pase.nivel);
        _pase.nivel += 1;
    }
}

/// @func pase_temporada_entregar(_pase, _indice_nivel)
/// @desc La vía gratis la recibe TODO jugador; la premium solo quien compró el pase.
function pase_temporada_entregar(_pase, _indice_nivel)
{
    var _nivel = _pase.niveles[_indice_nivel];
    if (_nivel.recompensa_gratis != undefined)
    {
        entregar_recompensa(_nivel.recompensa_gratis);      // entregar_recompensa: función propia del juego
    }
    if (_pase.premium && _nivel.recompensa_premium != undefined)
    {
        entregar_recompensa(_nivel.recompensa_premium);
    }
}
```

```gml
/// Al comprar el pase (evento Async - IAP resuelto, ver 04 · 20 §4):
global.pase_actual.premium = true;

// §2.3: lo comprado no se pierde. Si el jugador ya superó niveles sin haber
// comprado el pase, entrega TODAS las recompensas premium ya alcanzadas de golpe:
for (var _i = 0; _i < global.pase_actual.nivel; _i++)
{
    var _nivel = global.pase_actual.niveles[_i];
    if (_nivel.recompensa_premium != undefined) entregar_recompensa(_nivel.recompensa_premium);
}
```

---

## 4 · Checklist

**Antes de fijar precio a nada**

- [ ] El modelo de negocio está decidido y escrito en la plantilla de §6.1, antes de diseñar
      progresión, dificultad o economía.
- [ ] Cada objeto vendible está clasificado como cosmético, conveniencia o poder (§1.3, §3.2), y
      el auditor de §3.2 no señala ningún objeto de poder que afecte al combate — o si lo hace,
      alguien del equipo puede defenderlo en voz alta.
- [ ] Si hay cajas de botín o cualquier recompensa aleatoria comprable: las probabilidades se
      generan con `caja_botin_declarar()` (§3.1), nunca se escriben a mano en el texto de
      marketing, y hay un sistema de piedad de [13 · 13 §5.7](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md#57--crítico-con-piedad-pity).
- [ ] Cada patrón de la tabla de §1.6 se ha comprobado explícitamente contra el catálogo: no
      «creo que no lo tenemos», sino una lista de qué mecánica se revisó y con qué resultado.
- [ ] Si el juego tiene pase de temporada: ninguna recompensa premium afecta a una estadística de
      combate o progresión competitiva (§2.3).
- [ ] Hay un reloj de sesión visible para el jugador (§3.3), y ningún aviso de sesión penaliza
      parar de jugar.
- [ ] Si se recoge cualquier telemetría de tienda: cumple el marco de consentimiento de
      [13 · 11 §7](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#7--post-lanzamiento)
      (preguntar antes, «no» tan fácil como «sí», funciona igual sin telemetría).
- [ ] Se decidió explícitamente si el juego hace live ops o no (§1.8), con el coste por temporada
      calculado en las mismas unidades que el resto de la estimación de producción (§2.5) — no
      por ambición ni por comparación con juegos de equipos mucho más grandes.
- [ ] La clasificación por edades (PEGI/ESRB/IARC, [13 · 11 §9.4](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#94-clasificación-por-edades-pegi-esrb-e-iarc))
      refleja de verdad las compras integradas y los objetos aleatorios de pago que tiene el
      juego, no una versión optimista del cuestionario.

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Consecuencia | En su lugar |
|---|---|---|
| Elegir el modelo de negocio a mitad de producción | Rediseñar progresión, dificultad y economía por segunda vez | Decidirlo en la plantilla de §6.1 antes de programar el primer sistema |
| Vender poder en PvP «solo un poco» | Se convierte en *Monetized Rivalries* aunque la intención fuera modesta; la comunidad lo nota igual | Cosmético y conveniencia en PvP; poder solo en PvE, y con criterio |
| Diseñar el ritmo base lento a propósito para vender el atajo | Es *Pay to Skip*, y los jugadores lo distinguen del ritmo honesto | Diseña el ritmo para ser disfrutable sin pagar; vende adelantar, no desatascar |
| Escribir las probabilidades de una caja a mano en el texto de marketing | Se desincroniza del sorteo real y alguien lo va a comprobar | Generar el texto con `caja_botin_declarar()` (§3.1) desde el mismo dato que el sorteo |
| Anunciar una «Temporada 1» sin tener presupuesto para la 2 | El roadmap se rompe en público, y cuesta más confianza que no haberlo anunciado | Calcula el coste por temporada (§2.5) antes de anunciar ninguna; si no llega, no hay pase de temporada, hay premium + DLC |
| Penalizar (quitar recompensa, cerrar oferta con cuenta atrás) al jugador que ignora un aviso de sesión | Es *Playing by Appointment* con el nombre de «juego responsable» | El aviso informa; nunca penaliza ni presiona (§1.7, §3.3) |
| Copiar un modelo F2P «porque funciona en móvil» en un juego premium de Steam | El jugador que pagó la entrada no espera fricciones de conversión; genera reseñas negativas centradas en la monetización, no en el juego | El modelo se elige por el juego que quieres, no por el género de moda (§1.2) |
| Confundir «no hacemos trampa con las probabilidades» con «no necesitamos declararlas» | PEGI, y probablemente tu tienda, exigen el descriptor aunque el sorteo sea honesto (§1.5) | Declara siempre que existan objetos aleatorios de pago, sea cual sea la probabilidad real |
| Lanzar DLC el día 1 | Percepción de contenido cortado a propósito (*Pre-Delivered Content*), documentada también por Steamworks: «*customers may perceive that the full game was ready to release but you chose to take away content*» | El juego base se siente completo por sí solo; el DLC llega después, con contenido nuevo de verdad |

---

## 6 · Plantillas para rellenar

### 6.1 · Modelo de negocio en una página

```markdown
# <Título> · Modelo de negocio          versión: 0.1 · fecha: AAAA-MM-DD

**Modelo principal:**  premium · demo · F2P · DLC · suscripción · pase de temporada · early access
**Por qué este y no otro:** (una frase; qué tipo de juego y de equipo lo sostiene)

**Qué se vende:**
  - Cosmético:
  - Conveniencia:
  - Poder (si lo hay, justifícalo con la tabla de 13 · 20 §1.3):

**Qué NUNCA se vende:** (lista explícita — lo que decidiste dejar fuera, y por qué)

**Economía dual (13 · 20 §1.4):**
  Moneda de partida:              Moneda de meta:              Moneda dura (si existe):
  Fuente principal de cada una:
  Sumidero principal de cada una:

**¿Cajas de botín u objetos aleatorios de pago?**  sí · no
  Si sí: tabla de probabilidades declarada (13 · 20 §3.1) — enlace/ruta:
  Sistema de piedad (13 · 13 §5.7) — sí · no · por qué:

**¿Live ops (13 · 20 §1.8)?**  sí · no
  Si sí: coste por temporada (horas) ____  ·  temporadas comprometidas ____
  Si no: plan de parches de contenido post-lanzamiento sin cadencia prometida:

**Checklist ético (13 · 20 §2.4) pasado:**  sí · no · fecha:
**Clasificación por edades prevista:**  PEGI ___ · ESRB ___ (13 · 11 §9.4)
```

### 6.2 · Hoja de una oferta

```markdown
# Oferta: <nombre>                       fecha de publicación: AAAA-MM-DD

**Qué incluye:**
**Precio:**                    **¿Descuento? ¿de cuánto y por qué ahora?:**
**Duración de la oferta:**     **¿Se repetirá más adelante? (si "no", ¿por qué es honesto decirlo?):**

**Categoría (13 · 20 §1.3):**  cosmético · conveniencia · poder
  Si poder: ¿afecta a PvP o ranking?  sí · no  →  si "sí", DETENER, volver a §1.3

**¿Incluye algo aleatorio?**  sí · no
  Si sí: tabla de probabilidades adjunta (13 · 20 §3.1):  sí · no  →  si "no", DETENER

**Filtro ético (13 · 20 §2.4), respuesta a las 5 preguntas:**
  1.
  2.
  3.
  4.
  5.

**¿Un menor identificado como tal queda excluido?**  sí · no · n/a
**Quién la aprobó, y cuándo:**
```

---

## Ver también

- [04 · 20 — Servicios de plataforma](../04%20-%20Recetas%20por%20género/20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md) — la API de logros, anuncios, IAP y nube que este documento no repite
- [04 · 28 §10 — Monetización y servicios (móvil)](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#10--monetización-y-servicios) — extensiones móviles y señales de edad
- [13 · 11 §6-9 — Producción, alcance y lanzamiento](./11%20-%20Producción,%20alcance%20y%20lanzamiento.md#6--lanzamiento) — precio, regiones, wishlists, press kit, post-lanzamiento y legal
- [13 · 01 §4 — Economía y balance](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#4--economía-y-balance) — el vocabulario de pool/fuente/sumidero que este documento extiende al negocio
- [13 · 01 §9.5 — Telemetría](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#95--telemetría-contar-muertes-por-sala-y-volcarlas-a-json) — el pipeline que §3.4 reutiliza para el embudo de tienda
- [13 · 13 §5.5 y §5.7 — Probabilidad justa y piedad](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md#57--crítico-con-piedad-pity) — el mecanismo de bolsa aleatoria y crítico con piedad que §1.5 y §3.1 aplican a las cajas de botín
- [13 · 16 §2.6 — El patrón de monedas múltiples](./16%20-%20Progresión%20-%20árboles%20de%20habilidades,%20desbloqueos%20y%20meta-progresión.md#26-el-patrón-de-monedas-múltiples-partida-frente-a-meta) — moneda de partida frente a moneda de meta, base de la economía dual de §1.4
- [13 · 14 §2 — El documento de diseño](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#2--el-método-paso-a-paso) — dónde encaja la sección 11 (Monetización) de la plantilla larga de GDD
- [13 · 25 — Legal de terceros: marcas, fan games y parodia](./25%20-%20Legal%20de%20terceros%20-%20marcas%2C%20fan%20games%20y%20parodia.md) — el riesgo de construir tu negocio sobre la IP de un tercero, que este documento no cubre (§1.1)

---

## Fuentes

Consultadas y verificadas el **6 de septiembre de 2026** con `curl -sL -A "Mozilla/5.0"` y
`WebFetch` (sin `WebSearch`, agotado en esta sesión):

- **PEGI** — <https://pegi.info/index.php/page/game-purchases> (definición y ejemplos del
  descriptor «In-Game Purchases»); <https://pegi.info/what-do-the-labels-mean> (lista viva de
  descriptores, incluido «Paid random items»); y
  <https://pegi.info/index.php/news/pegi-expands-age-rating-criteria-interactive-risk-categories>
  (comunicado del 12-03-2026, «PEGI expands age rating criteria with interactive risk
  categories» — el cambio de junio de 2026 citado en §1.5, incluida la cita de USK).
- **José P. Zagal, Staffan Björk y Chris Lewis**, *Dark Patterns in the Design of Games*,
  Foundations of Digital Games (FDG) 2013 — PDF descargado y leído completo de
  <http://www.fdg2013.org/program/papers/paper06_zagal_etal.pdf>. Fuente de la definición de
  patrón oscuro, la postura sobre el azar como no-oscuro-por-sí-mismo, el principio de
  divulgación de Berdichevsky y Neuenschwander, y los patrones *Grinding*, *Playing by
  Appointment*, *Pay to Skip*, *Pre-Delivered Content*, *Monetized Rivalries*, *Social Pyramid
  Schemes* e *Impersonation*.
- **darkpattern.games** — <https://darkpattern.games/>, <https://darkpattern.games/patterns.php>
  y las cuatro páginas de categoría (<https://darkpattern.games/pattern/1/temporal-dark-patterns.html>,
  `/pattern/2/monetary-dark-patterns.html`, `/pattern/3/social-dark-patterns.html`,
  `/pattern/4/psychological-dark-patterns.html`). Cita explícitamente a Zagal et al. como fuente
  de su taxonomía; usado aquí para los nombres y descripciones prácticos de §1.6.
- **Steam** — <https://store.steampowered.com/steam_refunds/> (política de reembolsos completa:
  14 días/2 horas para el juego base, 14 días para DLC, 48 horas para compras dentro del juego) y
  <https://partner.steamgames.com/doc/finance/refunds> (cómo se calcula la tasa de reembolso) y
  <https://partner.steamgames.com/doc/store/application/dlc> (buenas prácticas de DLC, citada en
  §5 de la tabla de errores clásicos).
- ⚠️ **gamediscover.co** — se intentó (<https://gamediscover.co/>) con `curl` y con `WebFetch`;
  es una aplicación de una sola página que renderiza su contenido por JavaScript, y ni el HTML
  crudo ni el resumen de `WebFetch` devolvieron artículos, solo la estructura de navegación. No
  se cita ningún dato de esta fuente en el documento.
- ⚠️ **No verificado hoy** (ver aviso completo en §1.5 y §1.7): la prohibición de cajas de botín
  en Bélgica y su clasificación en Países Bajos, los requisitos de divulgación de probabilidades
  de Apple y Google, la regulación de gacha en China y Japón, y los límites legales de tiempo de
  juego para menores en mercados que los tienen.
