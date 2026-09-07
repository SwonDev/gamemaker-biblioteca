# 18 · Diseño de combate y de jefes

> Qué hace legible un golpe antes de que duela, qué verbo del jugador responde a qué amenaza,
> cuántos fotogramas de aviso exige un cuerpo humano antes de pedirle una respuesta, cuándo un
> jefe enseña y cuándo solo alarga el reloj, y cuánto cuesta —en segundos, no en frustración—
> volver a intentarlo. Es el documento que se rellena **antes** de tocar el MCP de recursos.
>
> **Es de oficio, no de código.** La frontera es explícita: aquí se **decide**; en
> [04 · 30 — Combate cuerpo a cuerpo](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md),
> [04 · 32 — Sistema de daño y efectos de estado](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md),
> [04 · 33 — Diseño de enemigos, encuentros y director de combate](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md)
> y
> [04 · 34 — Combate a distancia](../04%20-%20Recetas%20por%20género/34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md)
> ya está **implementado**: hitboxes, hurtboxes y *frame data*; tipos de daño, armadura,
> escudos y el motor de efectos de estado; arquetipos, sinergias, el gestor de fichas de
> ataque, la tabla de amenaza y el director de intensidad; munición, retroceso, hitscan y
> cobertura. Este documento no repite ni una línea de ese GML: da el **criterio** con el que
> rellenar los `struct` que ya existen —`ArquetipoDef`, `EncuentroDef`, el array `phases` de un
> jefe— antes de escribir el primero de ellos.
>
> **No cubre**: la fórmula de daño ni el motor de estados (documento 32), el movimiento o la
> decisión individual de un enemigo
> ([04 · 23](../04%20-%20Recetas%20por%20género/23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md),
> [04 · 31](../04%20-%20Recetas%20por%20género/31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md)),
> ni el ritmo a escala de nivel completo ([13 · 02](./02%20-%20Diseño%20de%20niveles.md) §1.2,
> con su gráfico de intensidad de *minutos*). Este documento baja ese mismo criterio a la
> escala del **encuentro** y del **jefe** —segundos, no minutos— y decide algo que ningún
> documento de la biblioteca decidía todavía: cuánto debe durar un aviso para ser justo, y
> cuánto debe costar fallar.

---

## 1 · Los principios

### 1.1 · La cadena de legibilidad: señal → lectura → decisión → ejecución → consecuencia

Todo golpe que el jugador recibe y que se siente injusto rompe uno de estos cinco eslabones, y
casi siempre el mismo:

```
  SEÑAL          LECTURA         DECISIÓN         EJECUCIÓN         CONSECUENCIA
  (el tell)  →  (¿la vi?)   →  (¿sé qué hacer?) → (¿pude hacerlo?) → (¿entiendo por qué?)
```

- **Señal.** El ataque anuncia su llegada de forma que compite con todo lo demás en pantalla
  (partículas, HUD, otros enemigos) y gana. Si no gana, no hay señal: hay ruido.
- **Lectura.** La señal tarda lo suficiente en llegar a una decisión como para que un cuerpo
  humano pueda procesarla. Esto tiene un piso medible, no una sensación — es todo el §1.3.
- **Decisión.** El jugador sabe **qué verbo** de su kit responde a esta señal, porque ya lo ha
  aprendido con una señal parecida antes (§1.2 y §1.4).
- **Ejecución.** El *input* llega a tiempo y el juego lo respeta —sin *input lag* que devore el
  margen que la lectura ya dejaba ajustado.
- **Consecuencia.** El resultado —vivir, recibir daño reducido, quedar expuesto— se explica por
  sí solo. Esto es §2.7: el jugador debe poder reconstruir por qué murió.

[13 · 02 §1.3](./02%20-%20Diseño%20de%20niveles.md) ya exige esta misma cadena para la
**navegación** de un nivel (*landmarks*, *weenies*, la prueba de los cinco segundos): un
enemigo o un jefe es, para efectos de legibilidad, **una pieza más del nivel que hay que leer
igual de rápido**. El vocabulario mecánico que sostiene la señal —hitbox, hurtbox, *frame
data*— ya está resuelto en
[04 · 30 §1.1-1.2](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md);
lo que este documento añade es el criterio de **cuánto** debe durar cada eslabón para que la
cadena no se rompa.

> 🔺 **Cuando algo «se siente injusto», busca el eslabón roto antes de tocar números.** Subir
> la vida del jugador no arregla un tell que dura menos que el tiempo de reacción; solo alarga
> el combate hasta que el jugador memoriza el patrón a base de morir, que es la forma más cara
> de enseñar algo.

### 1.2 · El kit del jugador: los verbos antes que los enemigos

Un enemigo no es una amenaza hasta que existe un verbo del jugador que responde a ella. Y un
verbo del jugador es decoración hasta que existe una amenaza que lo exige. Diseñar combate es
diseñar **esa correspondencia**, no una lista de monstruos.

| Verbo del jugador | Qué amenaza responde | Coste / riesgo | Dónde está implementado |
|---|---|---|---|
| **Golpear** | La ventana de castigo tras el *arranque* y la *recuperación* de un ataque enemigo | Ninguno si el timing es bueno; expone si se falla | [04 · 30 §5.2, §5.6](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) |
| **Esquivar** (*dodge*) | Un golpe de área o uno que no se puede bloquear | Arranque vulnerable de 2 fotogramas antes de los i-frames | [04 · 30 §4.5](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) |
| **Bloquear** | Daño constante, previsible, de bajo riesgo para el enemigo | Pierdes el turno; el bloqueo debe ser direccional | [04 · 30 §4.6](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) |
| **Parry** | Un golpe único, fuerte, que castiga la pasividad | Ventana de 4-8 fotogramas; fallar deja indefenso | [04 · 30 §4.6, §5.9](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) |
| **Romper aguante** (armas/combos pesados) | Un enemigo con *poise* que ignora el *hitstun* normal | Exige comprometerse a un ataque más lento | [04 · 30 §4.7](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) |
| **Romper línea de visión / cubrirse** | Un tirador, francotirador o arma hitscan | Cede terreno; a veces cede el turno de otro enemigo | [04 · 34 §4.5](../04%20-%20Recetas%20por%20género/34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md) |
| **Priorizar objetivo** | Un enemigo de apoyo (cura) o un francotirador oculto | Ignorar al resto del grupo mientras tanto | [04 · 33 §4](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md) |
| **Usar un estado propio** (invulnerabilidad temporal, curación) | Presión sostenida que agota un recurso más rápido de lo previsto | Consume un recurso limitado | [04 · 32 §4.7](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) |

Dos reglas se leen directamente de esta tabla:

1. **No añadas un ataque enemigo nuevo hasta que sepas qué fila de esta tabla lo contesta.** Si
   la respuesta es «ninguna», el ataque no es difícil: es aleatorio.
2. **No añadas un verbo nuevo al jugador hasta que exista (o esté planeada) una amenaza que lo
   exija.** Un botón de esquiva que nunca hace falta es ruido en el HUD, no una decisión.

> 💡 **La asistencia de puntería de [04 · 34 §4.4](../04%20-%20Recetas%20por%20género/34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md)
> es parte del kit, no un extra.** Vive detrás de un interruptor explícito en `global.a11y`
> ([04 · 27](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md)): para quien tiene
> dificultad motriz fina, es la diferencia entre tener el verbo «disparar con precisión» o no
> tenerlo en absoluto. Diseñar el kit incluye decidir qué verbos llevan un ajuste de
> accesibilidad y cuáles no lo necesitan.

### 1.3 · El vocabulario del *tell*: duración mínima en fotogramas

Un **tell** no es lo mismo que la anticipación de la animación clásica. [13 · 04 §1.1-1.3](./04%20-%20Animación%20de%20sprites%2C%20Sequences%20y%20Animation%20Curves.md)
ya trata la anticipación como principio de peso y lectura visual —«siete fotogramas de
anticipación son 117 ms: bastante para verlo, poco para sentirlo pesado»— y eso basta para que
un salto se **sienta** bien. Un tell de combate tiene una exigencia añadida: no solo debe
**verse**, tiene que dejar tiempo **de sobra** para que el jugador perciba la señal, decida
entre las respuestas válidas de §1.2 y **ejecute** esa respuesta antes de que el golpe llegue.
Esa es la diferencia entre anticipación-para-el-peso y anticipación-para-la-justicia, y la
segunda tiene un piso medible.

**El piso, con números.** La mentalometría (*mental chronometry*) sitúa el tiempo de reacción
visual simple de un adulto joven en torno a **190-200 ms** en condiciones de laboratorio —una
sola señal, una sola respuesta posible—, y marca cualquier respuesta por debajo de **100-200
ms** como «anticipatoria»: el sujeto ya tenía el movimiento programado antes de que apareciera
la señal, no reaccionó a ella. El tiempo de reacción auditivo simple es algo más corto, en torno
a **160 ms**. Eso es el suelo absoluto — y es el suelo para una sola respuesta posible, no para
elegir entre varias.

Cuando hay que **elegir** entre dos o más respuestas válidas —¿esquivo a la izquierda o a la
derecha?, ¿bloqueo o esquivo?—, la **ley de Hick** (Hick, 1952; refinada por Hyman —
«ley de Hick-Hyman») describe cómo crece el tiempo de decisión con el número de opciones:

```
  T = b · log₂(n + 1)
```

El tiempo de reacción por elección crece **logarítmicamente** con el número de respuestas
válidas `n`: duplicar las opciones no duplica el tiempo, pero sí lo aumenta de forma
consistente y medible. La consecuencia directa para un tell: **cuantas más respuestas válidas
le des al jugador, más margen necesita el aviso** — no es una intuición de diseño, es la misma
ley que rige un panel de mando o un menú.

**La tabla de trabajo** — ⚠️ es una regla de oficio construida sumando el piso de reacción, un
margen de decisión creciente por la ley de Hick y un margen de ejecución motriz e *input lag*
(~80-100 ms); no es una cifra publicada por ningún estudio de videojuegos, ajústala con
playtesting real (§2.10):

| Qué debe decidir el jugador | Respuestas válidas (`n`) | Margen mínimo | A 60 fps |
|---|---|---|---|
| Esquivar o no esquivar (amenaza única, respuesta binaria) | 1-2 | ~300-350 ms | 18-21 fotogramas |
| Elegir dirección de esquiva, o esquivar/bloquear | 2-3 | ~400-500 ms | 24-30 fotogramas |
| Elegir entre bloquear, esquivar o parry (alto riesgo si falla) | 4+ | ~500-650 ms | 30-39 fotogramas |
| *Parry* puro, deliberadamente por DEBAJO del piso de reacción | — | 4-8 fotogramas | 4-8 fotogramas |

La última fila no es una excepción a la regla: es la que la confirma. La ventana de *parry* de
[04 · 30 §4.6](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md)
(4-8 fotogramas) es **más corta** que el piso de reacción simple a propósito: un *parry* que se
pudiera reaccionar en tiempo real dejaría de premiar la memoria del patrón y se convertiría en
otro bloqueo con más recompensa. Por eso el *parry* se aprende **de memoria** —el jugador
anticipa, no reacciona—, mientras que el bloqueo y la esquiva sí caben dentro del piso de
reacción real.

**Verificación cruzada, sin buscarla a propósito.** La biblioteca ya tenía dos ejemplos de
código escritos por dos manos distintas, en dos documentos distintos, sin coordinarse entre
sí, y ambos caen dentro de esta misma banda:

- [04 · 30 §5.12](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md)
  define el arranque del `enemigo_zarpazo` en `arranque: 26` fotogramas (~433 ms a 60 fps), con
  el comentario literal «~0,43 s de aviso: el jugador puede reaccionar».
- [04 · 15 §5.8](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) define
  `ANTICIPATE_FRAMES = 30` (500 ms) para el ataque de un jefe, con el comentario «medio segundo
  de aviso: esquivable».

Ambos caen en la fila «esquivar o no esquivar / elegir dirección» de la tabla de arriba, sin que
nadie los calculara con esta fórmula. Eso no demuestra que la fórmula sea la única correcta,
pero sí que el instinto de dos redactores distintos coincide con el piso medido — úsalo como
verificación, no como excusa para no medir el tuyo con playtesting real.

**Dos reglas más, sobre el propio tell, no sobre su duración:**

- 🔺 **Un tell necesita al menos dos canales — visual y sonoro — nunca solo uno.** Un jugador
  con la cámara ocupada en otro enemigo, o con pérdida auditiva, tiene que poder leer el aviso
  por el canal que le queda. Es la misma regla que
  [04 · 27 §1](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) exige para el
  color: nunca comuniques con un solo canal lo que puede decidir una muerte.
- 🔺 **Una silueta de tell = una respuesta correcta, siempre.** Si dos ataques comparten el
  mismo aviso visual pero exigen contadores distintos (uno se esquiva, el otro se bloquea), el
  jugador no está leyendo el combate: está tirando una moneda. Esto es diseño, no arte: pide al
  animador un tell **distinto** para cada respuesta distinta antes de pedirle que quede bonito.

**Convertir segundos a fotogramas sin asumir 60 fps** es una línea, ya resuelta en
[13 · 13 §12.1](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md) —
`segundos_a_frames(_segundos)`, que llama a `game_get_speed(gamespeed_fps)` en vez de escribir
un número a mano—: §4.2 la reutiliza para convertir esta tabla en datos.

### 1.4 · El enemigo como pregunta, no como obstáculo con vida

[04 · 33 §1](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md)
ya fija el vocabulario que este documento adopta como principio: cada arquetipo se define
respondiendo a **cuatro preguntas** —qué presión aplica, a qué obliga, cómo se contrarresta, qué
pasa si se ignora— y no a un número de vida. La tabla de seis arquetipos (embestidor, tirador,
muro, enjambre, francotirador, apoyo) con su presión, su contrapartida y su telegrafía en
fotogramas está allí completa; este documento no la repite.

Lo que este documento **añade** es el criterio previo: antes de decidir la vida o el daño de un
enemigo, decide **qué pregunta le hace al jugador** y verifica en la tabla de §1.2 que existe un
verbo que la contesta. Un enemigo sin pregunta es un saco de vida; un saco de vida solo alarga
el combate, nunca lo hace interesante.

Un encuentro es una **combinación** de preguntas, no una suma de vidas. La regla de
[04 · 33 §2](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md)
—combinar un arquetipo que empuja con uno que ancla, y la prueba «si lo quito, ¿cambia algo?»—
es la aplicación directa de este principio a más de un enemigo a la vez, y §2.6 la extiende a
los *adds* de un jefe.

### 1.5 · El jefe no es un enemigo grande: es una pieza de nivel

El error más caro de diseño de jefes es tratarlo como «el mismo enemigo, con más vida y más
daño». Un jefe bien diseñado es, en la práctica, **un nivel corto disfrazado de personaje**:
tiene arena (el espacio), pacing (tensión y respiro, [13 · 02 §1.2](./02%20-%20Diseño%20de%20niveles.md)),
*landmarks* (el propio jefe es el *weenie* de toda la sala,
[13 · 02 §1.3](./02%20-%20Diseño%20de%20niveles.md)), y una estructura de enseñanza —cada fase
introduce una idea, igual que [13 · 01 §5.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md)
exige «una idea nueva cada vez» al enseñar una mecánica normal.

Tres consecuencias prácticas de esta idea, que se desarrollan en §2:

1. **La arena se diseña antes que el jefe** (§2.3), igual que una sala se diseña antes que sus
   enemigos ([13 · 02 §2](./02%20-%20Diseño%20de%20niveles.md)).
2. **Cada fase enseña una cosa** (§2.4), la misma disciplina de onboarding de
   [13 · 01 §5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md)
   aplicada a segundos en vez de a minutos.
3. **El jefe queda fuera del director de intensidad** de
   [04 · 33 §5-6](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md):
   un nivel diseñado a mano no deja que un sistema automático decida su ritmo a mitad de la
   pelea, y un jefe tampoco.

---

## 2 · El método, paso a paso

### 2.1 · Diseña el kit antes que ningún enemigo

Antes de escribir la primera ficha de arquetipo (§3.1), completa la tabla de §1.2 para tu
proyecto: lista los verbos del jugador, lista qué amenaza contesta cada uno, y **deja en blanco
lo que todavía no existe**. Un hueco en esa tabla es información: o falta un verbo, o vas a
diseñar un enemigo que no necesita ninguno nuevo (reutiliza uno que ya tienes).

### 2.2 · Diseña el tell antes que la animación final

El orden que evita rehacer trabajo de arte: decide la duración mínima en fotogramas con la
tabla de §1.3 **antes** de pedir la animación, entrégasela al animador como una restricción dura
—«el arranque no puede bajar de 24 fotogramas», no «que se vea rápido»— y dale la sensación de
peso y lectura de
[13 · 04 §1.1-1.4](./04%20-%20Animación%20de%20sprites%2C%20Sequences%20y%20Animation%20Curves.md)
**dentro** de ese presupuesto, no en contra de él. Si el arte final necesita menos fotogramas
para verse bien, sobra tiempo: repártelo en la recuperación (la ventana de castigo), nunca lo
quites del arranque.

### 2.3 · La arena, antes que el jefe

Aplica el mismo método de [13 · 02 §2.1](./02%20-%20Diseño%20de%20niveles.md) —las métricas del
jugador como unidad de medida— al espacio del jefe:

- **Tamaño mínimo**: el jugador debe poder ejecutar su esquiva más larga sin chocar con el borde
  de la arena a mitad de la maniobra.
- **Hazards fijos**: ¿hay lava, un borde, una zona que se derrumba? Decide si son parte del
  reto del jugador o del enemigo (una zona que daña a ambos por igual es más justa que una que
  solo perjudica al jugador).
- **Coberturas**, si el jefe ataca a distancia: usa el sistema de
  [04 · 34 §4.5](../04%20-%20Recetas%20por%20género/34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md)
  tal cual — no lo reinventes para el jefe.
- **¿Cambia la arena entre fases?** Un suelo que se inunda, columnas que caen: es una forma
  barata de que una fase «enseñe algo nuevo» sin escribir un ataque nuevo — es el mismo espíritu
  del *gating* de [13 · 02 §1.4](./02%20-%20Diseño%20de%20niveles.md) aplicado al propio combate.

### 2.4 · Estructura de fases: qué cambia y qué se conserva

El array `phases` de
[04 · 03 §5.7](../04%20-%20Recetas%20por%20género/03%20-%20Shoot%20em%20up%20%28shmup%29.md)
—cada fase con su `hp_threshold`, `on_enter` y `on_update`— ya es la forma de código correcta;
la decisión de diseño es **qué entra en cada fase**:

| Qué SÍ cambia entre fases | Qué NUNCA cambia entre fases |
|---|---|
| Un ataque nuevo, con su propio tell (§1.3) | Los verbos del kit del jugador que ya funcionaban |
| Un *hazard* de la arena que se activa (§2.3) | La legibilidad del HUD y de la barra de vida |
| El ritmo de *adds* (§2.6) | La cámara y el encuadre básico del combate |
| El tempo de los patrones ya conocidos (más rápido, no distinto) | El significado de un tell ya aprendido (§1.3, regla de la silueta) |

🔺 **Cada fase enseña exactamente UNA cosa nueva.** Es la regla del «3+1» de
[13 · 01 §3.2](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md)
bajada a la escala de un combate: si la fase 2 introduce un ataque nuevo Y cambia la arena Y
mete *adds* a la vez, el jugador no puede saber cuál de los tres lo mató, y eso rompe
directamente §2.7.

**La transición entre fases es una puntuación, no un vacío.** El código ya existente de
[04 · 03 §5.7](../04%20-%20Recetas%20por%20género/03%20-%20Shoot%20em%20up%20%28shmup%29.md)
marca al jefe `invulnerable = true`, sacude la cámara, limpia las balas en pantalla y da 40
fotogramas antes de volver a atacar — no es relleno, es la señal de «esto ha cambiado, presta
atención» que separa una fase de la siguiente. Diséñala con esa intención, no la trates como un
efecto que sobra.

### 2.5 · El checkpoint entre fases y el coste del reintento, en segundos

[13 · 02 §1.6](./02%20-%20Diseño%20de%20niveles.md) ya fija el principio para un nivel completo:
**la distancia entre puntos de control es la dificultad**, más que los propios enemigos, y «el
jugador nunca debería repetir un trozo que ya demostró saber hacer». Un jefe con fases es el
mismo problema a escala de segundos: si un jugador domina las fases 1 y 2 el 90 % de las veces
y muere sistemáticamente a un tell nuevo de la fase 3, obligarlo a repetir 60-90 segundos ya
dominados en cada intento no mide su habilidad contra la fase 3 — mide su paciencia.

Esto **no tiene una respuesta correcta única**: es una decisión de diseño que hay que tomar a
propósito, con su coste expresado en segundos, no dejarla «como haya salido»:

| Diseño de reintento | Qué se reinicia | Coste típico (13 · 01 §4.4) | Qué mide de verdad | Cuándo elegirlo |
|---|---|---|---|---|
| **Reinicio completo** | Todas las fases, vida al 100 % | 40-150 s — el TTK completo del jefe | Resistencia y dominio de la secuencia ENTERA | El jefe es la prueba final de un tramo largo; repetir fases dominadas es parte del reto a propósito |
| **Checkpoint por fase** | Solo la fase en la que murió; vida del jefe fijada al umbral de esa fase | El TTK de una sola fase (10-50 s) | Solo la habilidad nueva de esa fase, aislada | El jefe enseña una mecánica por fase y quieres medir esa mecánica, no la resistencia |
| **Práctica tras N muertes** | Como el checkpoint por fase, pero solo se activa tras varios intentos fallidos seguidos | Igual que el anterior, decreciente con el tiempo | Igual, con menos frustración acumulada | Juegos donde avanzar la historia importa más que la maestría del combate |
| **Sin reintento de jefe (una vida)** | Vuelve al último punto de control DEL NIVEL, no del jefe | Minutos: todo el tramo hasta el jefe | El nivel entero, no solo el jefe | *Roguelike*/muerte permanente: el jefe es una prueba del *run* completo, a propósito |

🔺 **Decide esta fila ANTES de programar el jefe, y anótala en la ficha de §3.3.** Es la
diferencia entre un jefe difícil a propósito y un jefe que se siente injusto por accidente
porque nadie decidió cuánto debía costar fallar.

> ⚠️ Esta tabla extiende el principio de checkpoints de
> [13 · 02 §1.6](./02%20-%20Diseño%20de%20niveles.md) a la escala de un jefe por fases; no es
> una cita de una fuente externa nueva. Nombrar convenciones de género (el reinicio completo de
> los *soulslike*, el checkpoint por fase de muchos juegos de acción con narrativa) describe una
> práctica ampliamente observada, no verificada con una fuente primaria por título en esta
> sesión — ver **Fuentes**.

La traducción a código de esta decisión —cómo guardar «en qué fase murió» sin reescribir el
jefe— está en §4.3.

### 2.6 · *Adds*: cuándo suman tensión y cuándo son ruido

Aplica la misma prueba de
[04 · 33 §2](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md)
a los refuerzos de un jefe: **¿qué decisión distinta obliga a tomar este *add* mientras dura la
fase?** Un esbirro que solo suma vida que golpear no complica el combate, lo alarga — sube el
TTK sin subir la decisión, que es justo el error que el §1 de este documento previene.

Un *add* que sí aporta:

- Obliga a **repartir el objetivo** entre el jefe y él (la tabla de amenaza o `ConfianzaGrupo`
  de [04 · 33 §4](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md)
  aplican igual dentro de una pelea de jefe).
- Obliga a **moverse** de una posición segura frente al jefe (rompe la estrategia de «quedarse
  quieto y esquivar el patrón conocido»).
- Aparece **coordinado con el patrón del jefe**, no al azar — el jugador debe poder anticipar
  cuándo van a llegar, no solo que van a llegar.

🔺 **Los *adds* de un jefe se programan por fase (`on_enter`/`on_update`), nunca por el director
de intensidad.** [04 · 33 §5](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md)
ya excluye explícitamente a los jefes del ritmo adaptativo de Michael Booth («los encuentros con
jefe NO se ven afectados por el ritmo adaptativo»): si el director decidiera cuándo entran los
*adds* de un jefe, una pelea podría volverse errática o desaparecer a media pelea, y el jugador
lo notaría como un fallo, no como dificultad.

### 2.7 · El jugador debe poder reconstruir por qué murió

Es la prueba de control de todo el documento, y la más barata de aplicar en playtest: al
morir, ¿puede el tester decir, sin que se lo expliques, qué tell no leyó o qué verbo no usó a
tiempo? Si la respuesta habitual es «no sé qué ha pasado», el fallo no es del jugador — es de la
cadena de §1.1, y casi siempre está en la señal (tapada por HUD o efectos) o en la lectura
(tell demasiado corto).

Dos herramientas ya existentes en la biblioteca sirven exactamente para esto, **para ti, no
para el jugador**:

- El **registro de daño** de
  [04 · 30 §5.13](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md)
  y [04 · 32 §5.13](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md)
  te dice si la muerte fue **un golpe grande y claro** (legible: el problema es el tell) o
  **el desgaste de varios efectos apilados** (ilegible: el problema es la comunicación de
  estados de [04 · 32 §4.6, §5.10](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md)).
- La trampa que ya advierte
  [13 · 05](./05%20-%20UI%20y%20UX%20de%20juego.md) en su propia tabla de errores: **«la HUD
  tapa el juego» — «el jefe está detrás de la barra de vida» porque «la HUD se diseñó sobre una
  captura vacía»**. Diseña el HUD de combate sobre una captura del momento más cargado de la
  pelea, no sobre la pantalla en reposo.

### 2.8 · Balance de combate: DPS junto al TTK

[13 · 01 §4.4](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md)
ya da el TTK (*time to kill*) —`golpes = ceil(vida / daño)`, `TTK = (golpes − 1) × cadencia/fps`—
con su tabla de referencia (Baba 0,2 s, Bruto 2,2 s, Jefe 40-150 s en 2-4 fases) y la heurística
de «golpe estándar». Ese documento no nombra el **DPS** (*damage per second*) porque, con un
arma y una cadencia fijas, el TTK ya lo contiene implícito. En combate, con varios enemigos de
cadencias distintas y con daño repartido en el tiempo (los efectos de estado de
[04 · 32](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md)),
el DPS es la métrica que permite comparar cosas que el TTK por sí solo confunde:

```
  dps = daño_por_golpe × (fps / cadencia_en_frames)
```

Para un enemigo o un jefe con **daño sostenido** —veneno, quemadura, un chorro continuo—, el DPS
de diseño es la suma del componente instantáneo y el componente por tiempo del motor de
efectos de [04 · 32 §4.4-4.5](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md):
un ataque que hace poco daño directo pero aplica un veneno largo puede tener el mismo DPS que un
golpe seco mucho más aparatoso, y **eso hay que decidirlo a propósito**, no descubrirlo en
producción.

**La regla de oro del balance de un jefe con fases**: el DPS de diseño debería **subir** de
fase en fase (más daño, más cadencia, o ambos), no solo el número de ataques — es lo que hace
que la fase final se sienta como el clímax y no como «lo mismo, más largo». La plantilla de
§3.3 incluye una columna de DPS de diseño por fase, precisamente para forzar esta comparación
antes de programar nada.

**Verificar el DPS de diseño contra el DPS real** ya tiene herramienta hecha:
`dano_dps_medido()` de
[04 · 32 §5.13](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md)
mide, sobre la telemetría de
[13 · 01 §9.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md),
cuánto daño hizo de verdad cada fuente en una ventana de tiempo. Compararlo con el número de la
hoja de balance (§4.4) en **cada** sesión de playtest de combate —no solo al final del
proyecto— es la diferencia entre «el jefe se siente raro» y saber si el problema es el tell, el
DPS o la vida.

### 2.9 · Dificultad: qué se puede tocar y qué no

[13 · 01 §3.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md)
ya distingue **DDA oculta** de **asistencia explícita**, y
[04 · 33 §5](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md)
ya aplica esa frontera al director de intensidad: «el algoritmo ajusta el ritmo, no la
dificultad». Para combate y jefes, esa frontera se traduce en una lista concreta:

| Se puede tocar (en caliente o dinámicamente) | No se toca nunca en silencio |
|---|---|
| Población y ritmo de *adds* fuera de un jefe (04 · 33 §5-6) | La duración del tell ya aprendido (§1.3) |
| Vida o daño del enemigo — SOLO detrás de un ajuste EXPLÍCITO que el jugador activa (04 · 27) | Vida o daño del enemigo en silencio (DDA oculta) — rompe la confianza que 13 · 01 §3.3 ya advierte |
| El coste del reintento (§2.5), como una elección declarada, no un parche | El *hitbox*/*hurtbox* y la ventana de i-frames (04 · 30 §4.5) |
| La cadencia de un arma **del jugador**, si sube por progresión (eso es una recompensa, no DDA) | El ritmo del director de intensidad dentro de un jefe (excluido a propósito, 04 · 33 §5) |

🔺 **Tocar el *frame data* que el jugador ya memorizó, aunque sea para «ayudarlo», se lee como
trampa del juego, no como ayuda.** Un jugador que aprendió a esquivar un ataque con un ritmo
concreto y de repente ese ritmo cambia sin avisar pierde la confianza en que el juego juega
limpio — mucho más que si el enemigo simplemente tuviera menos vida.

### 2.10 · Playtesting de combate

El protocolo general ya está en
[13 · 01 §7](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md)
—*think-aloud*, no ayudar ni explicar, «¿qué intentabas hacer en ese momento?» en vez de
«¿fue muy difícil?», cinco personas por ronda— y no se repite aquí. Lo que añade el combate:

- **Mira el momento justo después de morir**, no solo la muerte. Un asentimiento («sí, ya sé lo
  que hice mal») confirma la cadena de §1.1 y §2.7. Una cara de confusión, aunque el tester no lo
  diga en voz alta, es la señal más fiable de que un tell no se está leyendo.
- **Cuenta cuántas veces recibe daño de un tell que «ya conocía»**, no solo de uno nuevo. Un
  tell que sigue sorprendiendo al quinto intento no es difícil: está por debajo del piso de
  §1.3, o dos ataques comparten silueta (§1.3, regla de la silueta).
- **Extiende la telemetría de
  [13 · 01 §9.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md)
  con el campo `fase`** en el evento de muerte del jefe: cuántas muertes por fase es a un jefe
  lo que «qué sala mata más» es a un nivel — la misma pregunta, ya resuelta con `jq` en
  [13 · 01 §9.6](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md).
- **Compara el DPS medido con el de diseño** (§2.8) en la misma sesión, no después: si el
  jugador tarda el doble de lo previsto, mira primero si el DPS real coincide con el de la hoja
  antes de tocar la vida del jefe a ciegas.
- La métrica «qué medir» de
  [13 · 10 §10.2](./10%20-%20Testing%20y%20QA.md) —observación frente a interpretación,
  separadas y con marca de tiempo— aplica sin cambios al combate: anota lo que el tester **hizo**
  en el momento, interpreta después.

---

## 3 · Las plantillas: ficha de arquetipo, de encuentro y de jefe por fases

Se rellenan **antes** de crear ningún recurso con el MCP, igual que la hoja de nivel de
[13 · 02 §4](./02%20-%20Diseño%20de%20niveles.md) se rellena antes de abrir el Room Editor. Cada
campo alimenta directamente un `struct` que ya existe en la biblioteca — el mapeo exacto está
en §4.1.

### 3.1 · Ficha de arquetipo de enemigo

```markdown
# Arquetipo: <nombre>              familia: embestidor · tirador · muro · enjambre · francotirador · apoyo · <nuevo>

**¿Qué presión aplica?** (el problema concreto que le plantea al jugador — 04 · 33 §1)
**¿A qué obliga?** (la acción que el jugador DEBE tomar para no sufrirla)
**¿Cómo se contrarresta?** (el verbo del kit del jugador que lo neutraliza — §1.2)
**¿Qué pasa si se ignora?** (por qué no basta con no hacerle caso)

**Vida en golpes estándar:** ____        **TTK objetivo:** ____ s     (13 · 01 §4.4)
**Alcance:** ____ px                     **DPS de diseño:** ____      (§2.8)
**Telegrafía:** ____ fotogramas — según la tabla de §1.3, con ____ respuestas válidas

**Peso de rejilla / peso de ataque** (04 · 33 §3, `GestorFichas`): ____ / ____

**Se combina bien con** (uno que empuja + uno que ancla — 04 · 33 §2): ____
**Nunca combinar con, y por qué:** ____

**Feedback al jugador:** color/silueta del tell, sonido propio, qué NO comparte con otro arquetipo
**Verificado en playtest** (§2.10): fecha ____ — ¿algún tester recibió daño «sin verlo venir»? ____
```

### 3.2 · Ficha de encuentro

```markdown
# Encuentro: <nombre>                     zona: <sala/arena>     momento del arco: <n> de <total>

**Grupos** (04 · 33 §2, `EncuentroDef`):
| Arquetipo | Cantidad | Qué decisión distinta añade (si la respuesta es "ninguna", sobra) |
|---|---|---|
|  |  |  |

**¿Hay hueco de escape garantizado?** (04 · 33 §2) sí / no
**Capacidad de rejilla / de ataque del gestor de fichas** (04 · 33 §3): ____ / ____
**¿A quién ataca el grupo si hay varios objetivos?** tabla de amenaza / `ConfianzaGrupo` / un solo objetivo (04 · 33 §4)

**Intensidad prevista** (0-5, el gráfico de 13 · 02 §1.2 a escala de encuentro): entrada ____ → pico ____ → salida ____
**¿Lo dispara el director de intensidad (04 · 33 §5) o está guionizado a mano?** ____

**Arena:** hazards ____ · coberturas (04 · 34 §4.5) ____ · tamaño frente a la esquiva más larga del jugador ____

**¿Tiene salida no letal?** sí / no — si sí, ¿cuál vía?: aturdir/noquear · huir de verdad ·
negociar/sobornar · intimidar · dormir a distancia (04 · 56 §1.2). Un encuentro sin marcar se
trata como "no la tiene" — el silencio no es una salida accidental.

**Verificado en playtest** (§2.10): ¿algún tester describió el encuentro como "ruido" en vez de "difícil"? ____
```

### 3.3 · Ficha de jefe por fases

```markdown
# Jefe: <nombre>                     vida total: ____     TTK objetivo: ____ s (13 · 01 §4.4)

**La arena** (§2.3, diséñala ANTES que el jefe):
- Tamaño / hazards / coberturas: ____
- ¿Cambia entre fases, y en cuál? ____

| Fase | Umbral de vida | Qué enseña ESTA fase (una sola cosa — §2.4) | Ataque(s) nuevo(s): tell, fotogramas, nº de respuestas válidas | DPS de diseño | *Adds*: ¿qué decisión distinta obligan? (§2.6) |
|---|---|---|---|---|---|
| 1 |  |  |  |  |  |
| 2 |  |  |  |  |  |
| 3 |  |  |  |  |  |

**Transición entre fases** (04 · 03 §5.7): invulnerabilidad ____ fotogramas · limpia pantalla sí/no · feedback de cámara ____

**Reintento** (§2.5): reinicio completo / checkpoint por fase / práctica tras N muertes / sin reintento de jefe
**Coste del reintento, en segundos:** ____
**¿Por qué esta decisión y no otra?** ____

**Barra de vida:** segmentada (04 · 32 §4.8, §5.11), nombre visible, fase actual visible

**La pregunta de control de §2.7** — "¿qué tell no leyó, o qué verbo del kit no usó a tiempo?": ____

**Verificado en playtest** (§2.10): DPS medido (04 · 32 §5.13) frente a DPS de diseño, por fase: ____
```

---

## 4 · Cómo se traduce a GameMaker

### 4.1 · De la ficha al *struct*: qué campo va a cada tabla ya existente

| Campo de la ficha (§3) | Dónde vive ya en la biblioteca |
|---|---|
| Presión / obliga a / contraparte / vida en golpes / alcance / telegrafía / peso | `ArquetipoDef` — [04 · 33 §1](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md) |
| Grupos de un encuentro | `EncuentroDef` / `GrupoEncuentro` — [04 · 33 §2](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md) |
| Capacidad de rejilla/ataque | `GestorFichas` — [04 · 33 §3](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md) |
| Umbral de vida, `on_enter`/`on_update` por fase | el array `phases` — [04 · 03 §5.7](../04%20-%20Recetas%20por%20género/03%20-%20Shoot%20em%20up%20%28shmup%29.md) |
| Fotogramas de telegrafía | el campo `arranque` de la tabla de ataques — [04 · 30 §5.1](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) |
| Barra de vida segmentada | `barra_jefe_nueva/fijar/actualizar/dibujar` — [04 · 32 §5.11](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) |
| DPS de diseño frente a DPS medido | `tiempo_para_matar()` (13 · 01 §9.4) frente a `dano_dps_medido()` (04 · 32 §5.13) |

### 4.2 · El colchón de reacción, como función

Convierte la tabla de §1.3 en un dato en vez de repetir el número a mano en cada ataque nuevo.
Reutiliza `segundos_a_frames()`, ya definida en
[13 · 13 §12.1](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md) — no se redefine aquí:

```gml
/// scr_lectura_combate
/// @func tell_frames_minimos(_num_respuestas)
/// @desc El piso de fotogramas de un tell, según cuántas respuestas válidas debe
///       distinguir el jugador (§1.3). Es la tabla de §1.3 hecha datos, NO una medida
///       científica: ajústala con playtesting real (§2.10). Usa segundos_a_frames()
///       de 13 · 13 §12.1: nunca asumas 60 fps.
/// @param {Real} _num_respuestas  1-2 = esquivar o no · 3 = elegir dirección o
///                                bloquear/esquivar · 4+ = bloquear/esquivar/parry.
/// @returns {Real}  Fotogramas mínimos de arranque, a la velocidad real del juego.
function tell_frames_minimos(_num_respuestas)
{
    var _segundos = 0.30;                          // piso: percepción + un solo gesto
    if (_num_respuestas >= 3) { _segundos = 0.45; } // + decisión entre 2-3 opciones
    if (_num_respuestas >= 4) { _segundos = 0.60; } // + decisión entre 4 o más

    return segundos_a_frames(_segundos);            // 13 · 13 §12.1
}
```

```gml
// Al definir un ataque nuevo en la tabla de 04 · 30 §5.1:
global.ataques.jefe_embestida.arranque = max(
    global.ataques.jefe_embestida.arranque,   // lo que decidió el arte
    tell_frames_minimos(2)                    // el piso que exige §1.3
);
```

`max()` deja que el arte pida **más** tiempo del piso si el ataque lo necesita para verse bien,
pero nunca menos: el piso de reacción no se negocia por estética.

### 4.3 · El checkpoint entre fases, extendiendo el patrón de 13 · 02 §3.8

La decisión de §2.5 se traduce como **un dato que sobrevive a la muerte del jugador**, con el
mismo patrón que `global.control` de
[13 · 02 §3.8](./02%20-%20Diseño%20de%20niveles.md) usa para el punto de control del nivel —no
lo sustituye, vive junto a él:

```gml
/// obj_jefe · Create — extiende el array `phases` de 04 · 03 §5.7 con el reintento de §2.5.
/// La decisión (reinicio completo / checkpoint por fase) es UN booleano, no una
/// reescritura del jefe.
event_inherited();

var _hay_checkpoint = variable_global_exists("control_jefe") && global.control_jefe > 0;

if (JEFE_CHECKPOINT_POR_FASE && _hay_checkpoint)
{
    phase_index = global.control_jefe;
    hp          = hp_max * phases[phase_index].hp_threshold;   // vida al umbral de ESA fase
}
else
{
    phase_index = 0;
    hp          = hp_max;
}

phases[phase_index].on_enter(self);
```

```gml
// obj_jefe · dentro del bloque de cambio de fase, ya existente en 04 · 03 §5.7
global.control_jefe = phase_index;   // se lee en el Create tras la próxima muerte del jugador

// obj_jefe · Destroy (victoria) — el jefe cae: se limpia el progreso de reintento
global.control_jefe = 0;
```

`JEFE_CHECKPOINT_POR_FASE` es la macro que hace visible, en `scr_combate_config`
([04 · 30 §5.0](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md)),
la decisión que la ficha de §3.3 ya declaró en texto: cambiarla no exige tocar el jefe, solo
la constante.

### 4.4 · La hoja de balance como datos: jefes en `balance.json`

Extiende el `balance.json` de
[13 · 01 §9.3](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md)
con una sección `jefes` que lleva el DPS de diseño de la ficha de §3.3 ya calculado, para
compararlo directamente con `dano_dps_medido()` (§2.8) sin recalcular nada a mano:

```json
{
  "jefes": {
    "el_guardian": {
      "vida_total": 3000,
      "fases": [
        { "hp_umbral": 1.00, "dano_medio": 18, "cadencia_frames": 50, "dps_diseno": 21.6 },
        { "hp_umbral": 0.66, "dano_medio": 24, "cadencia_frames": 40, "dps_diseno": 36.0 },
        { "hp_umbral": 0.33, "dano_medio": 30, "cadencia_frames": 30, "dps_diseno": 60.0 }
      ],
      "ttk_objetivo_s": 90,
      "coste_reintento": "checkpoint_por_fase"
    }
  }
}
```

El `dps_diseno` de cada fase sube (21,6 → 36,0 → 60,0): es la comprobación numérica de la regla
de §2.8 —cada fase debe presionar más que la anterior— hecha visible en la propia hoja, antes de
que un solo jugador la juegue.

---

## 5 · Checklist

- [ ] ¿Cada verbo del kit del jugador responde a una amenaza real, y cada amenaza tiene un
      verbo que la contesta (§1.2)?
- [ ] ¿Cada tell dura, como mínimo, lo que exige la tabla de §1.3 según el número de respuestas
      válidas que le pide al jugador?
- [ ] ¿Todo tell tiene canal visual **y** sonoro, y una silueta que no comparte con ningún otro
      ataque de respuesta distinta (§1.3)?
- [ ] ¿Cada arquetipo responde a las cuatro preguntas de
      [04 · 33 §1](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md),
      no solo a un número de vida (§1.4)?
- [ ] ¿Se diseñó la arena antes que el jefe, con su tamaño verificado contra la esquiva más
      larga del jugador (§2.3)?
- [ ] ¿Cada fase del jefe enseña exactamente una cosa nueva, y la transición entre fases se
      siente como puntuación, no como vacío (§2.4)?
- [ ] ¿Se decidió explícitamente el coste del reintento, en segundos, ANTES de programar el
      jefe, y quedó anotado en la ficha (§2.5, §3.3)?
- [ ] ¿Cada *add* de una fase obliga a una decisión distinta — repartir objetivo, moverse,
      romper línea de visión — y no solo alarga el TTK (§2.6)?
- [ ] ¿Los *adds* del jefe están fuera del director de intensidad de
      [04 · 33 §5](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md)?
- [ ] ¿Puede un tester reconstruir, sin que se lo expliques, por qué murió (§2.7)?
- [ ] ¿El DPS de diseño sube de fase en fase, y se comparó con el DPS medido en playtest
      (§2.8)?
- [ ] ¿Ninguna dificultad se ajustó tocando el *frame data* o los i-frames en silencio (§2.9)?
- [ ] ¿El playtest de combate midió confusión-tras-la-muerte y muertes por fase, no solo «qué
      tan difícil fue» (§2.10)?

---

## 6 · Errores clásicos y cómo evitarlos

| Error | Qué se ve en el juego | Arreglo |
|---|---|---|
| El tell dura menos que el piso de reacción de §1.3 | El jugador jura que era imposible esquivar — y tiene razón | Usa la tabla de §1.3 según el número de respuestas válidas, nunca un número a ojo |
| El tell solo tiene canal visual | Un jugador con la cámara ocupada en otra cosa, o con dificultad auditiva o visual, recibe daño «de la nada» | Todo tell lleva sonido propio además del color (§1.3, 04 · 27) |
| Dos ataques comparten silueta de tell con contrapartidas distintas | El jugador acierta el contador la mitad de las veces: parece azar, no habilidad | Una silueta = una respuesta correcta, siempre (§1.3) |
| Se sube la dificultad tocando el *frame data* o la ventana de i-frames en silencio | El jugador que dominaba el patrón deja de leerlo y lo vive como trampa del juego | Ajusta población y ritmo (04 · 33 §5-6, 13 · 01 §3.3), nunca el *frame data* ya aprendido (§2.9) |
| Se añaden *adds* a un jefe sin decidir qué obligan a hacer de distinto | El combate se alarga, no se complica: sube el TTK sin subir la decisión | Aplica la prueba de 04 · 33 §2: si quitar el *add* no cambia nada, sobra (§2.6) |
| El reintento completo de un jefe de 90 s no se decidió, «es lo que salió» | El playtest reporta frustración creciente en el tercer y cuarto intento, no en el jefe en sí | Decide el coste del reintento en segundos ANTES de programar el jefe, como un campo más de la ficha (§2.5, §3.3) |
| Una fase introduce un ataque nuevo, un *hazard* nuevo y *adds* nuevos a la vez | El jugador no puede saber cuál de los tres lo mató; §2.7 se rompe | Una fase, una idea nueva (§2.4) |
| Nadie compara el DPS medido con el de diseño hasta el lanzamiento | El jefe «se siente mal» pero nadie sabe si es el tell, el DPS o la vida | `dano_dps_medido()` (04 · 32 §5.13) contra la hoja de balance en CADA sesión de playtest de combate (§2.8, §2.10) |
| La HUD tapa el tell en el momento en que más importa | Ya lo advierte 13 · 05: «la HUD se diseñó sobre una captura vacía» | Diseña el HUD sobre el momento más cargado del combate (§2.7, 13 · 05) |
| Preguntar «¿fue muy difícil el jefe?» en el playtest | Respuestas de cortesía que no dicen nada accionable | Protocolo de 13 · 01 §7.2: «¿qué intentabas hacer en ese momento?» (§2.10) |

---

## Ver también

- [04 · 30 — Combate cuerpo a cuerpo](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) —
  la hitbox/hurtbox real, el *frame data*, los i-frames, el aguante y la telegrafía del
  «enemigo mínimo» (§5.12) que este documento convierte en regla general de diseño.
- [04 · 32 — Sistema de daño y efectos de estado](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) —
  la barra de jefe segmentada (§4.8, §5.11) y el registro de daño con DPS medido (§5.13) que
  §2.7-2.8 usan para verificar tanto la legibilidad como el balance.
- [04 · 33 — Diseño de enemigos, encuentros y director de combate](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md) —
  arquetipos, sinergias, el gestor de fichas de ataque, la tabla de amenaza y el director de
  intensidad: la implementación de las «preguntas» de §1.4 y de los campos de las plantillas
  de §3.1-3.2.
- [04 · 34 — Combate a distancia](../04%20-%20Recetas%20por%20género/34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md) —
  cobertura y asistencia de puntería, para arenas de jefe con ataques a distancia (§1.5, §2.3).
- [04 · 56 — Combate no letal](../04%20-%20Recetas%20por%20género/56%20-%20Combate%20no%20letal%20-%20pacifismo%2C%20aturdir%2C%20huir%20y%20negociar.md) —
  la salida no letal de la ficha de encuentro de §3.2: aturdir/noquear, huir de verdad,
  negociar, intimidar y las consecuencias que la reconocen.
- [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) —
  anticipación y recuperación (§4.8) y el `BossAttackState` con `ANTICIPATE_FRAMES` (§5.8) que
  §1.3 usa como verificación cruzada del piso de reacción.
- [04 · 27 — Accesibilidad](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) —
  por qué un tell necesita dos canales, y la asistencia de puntería como interruptor explícito
  del kit (§1.2, §1.3).
- [13 · 01 — Diseño de juego](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md) —
  §3.1 Flow, §3.2 las cuatro curvas y la regla del 3+1, §3.3 dificultad dinámica, §4.4 TTK,
  §5.1 onboarding, §7 playtesting, §9.3-9.5 balance y telemetría: el marco que este documento
  extiende a combate y jefes.
- [13 · 02 — Diseño de niveles](./02%20-%20Diseño%20de%20niveles.md) — §1.2 *pacing*, §1.3
  legibilidad (*landmarks*, *weenies*), §1.6 checkpoints y distancia entre retos, §3.8 puntos
  de control con guardado: el jefe como pieza de nivel de §1.5.
- [13 · 04 — Animación de sprites, Sequences y Animation Curves](./04%20-%20Animación%20de%20sprites%2C%20Sequences%20y%20Animation%20Curves.md) —
  anticipación traducida a un sprite (§1.1-1.4): la base visual del tell, con la que §1.3 marca
  la diferencia entre «se ve bien» y «da tiempo a reaccionar».
- [13 · 05 — UI y UX de juego](./05%20-%20UI%20y%20UX%20de%20juego.md) — la barra de vida
  «fantasma» (§3.5 b), y la trampa «la HUD tapa el juego» que §2.7 y §6 citan.
- [13 · 10 — Testing y QA](./10%20-%20Testing%20y%20QA.md) — §10.2 qué medir en un playtest:
  la extensión a métricas de combate de §2.10.
- [13 · 13 — Matemáticas aplicadas al juego](./13%20-%20Matemáticas%20aplicadas%20al%20juego.md) —
  §12.1 `segundos_a_frames()`, la conversión que usa §4.2 para no asumir 60 fps nunca.

---

## Fuentes

Consultadas el **2026-09-06**.

**Tiempo de reacción y ley de Hick** (abiertas y leídas con WebFetch esta sesión):

- **Wikipedia, «Mental chronometry»** — <https://en.wikipedia.org/wiki/Mental_chronometry> —
  el tiempo de reacción visual simple en adultos jóvenes (~190-200 ms), el auditivo (~160 ms),
  y el umbral de 100-200 ms por debajo del cual una respuesta se considera «anticipatoria»
  (motora, programada antes del estímulo) y no una reacción real. Es la base numérica del piso
  de §1.3.
- **Wikipedia, «Hick's law»** — <https://en.wikipedia.org/wiki/Hick%27s_law> — la fórmula
  `T = b · log₂(n + 1)`, el crecimiento logarítmico (no lineal) del tiempo de decisión con el
  número de opciones, y su origen (William Edmund Hick, 1951-1952; refinada por Ray Hyman —
  «ley de Hick-Hyman»). Es la base del margen de decisión que crece con el número de respuestas
  válidas de la tabla de §1.3.

**Reutilizadas de la propia biblioteca**, ya citadas y verificadas en el documento de origen —
no se abrió una URL nueva para ellas en esta sesión:

- **Tynan Sylvester, *Designing Games: A Guide to Engineering Experiences*** (O'Reilly, 2013) —
  ya citado en [13 · 01](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md).
  Se reutiliza aquí como marco general de tensión y coste del fracaso detrás de §2.5.
- **Jesse Schell, *The Art of Game Design: A Book of Lenses*** — ya citado en
  [13 · 01 §3.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md)
  para la lente del Flow; ⚠️ verificado allí solo sobre la 1.ª edición. Se reutiliza como marco
  general en §2.9, sin cita textual nueva.
- **Michael Booth (Valve), «The AI Systems of Left 4 Dead»**, GDC 2009 — ya verificado en
  [04 · 33](../04%20-%20Recetas%20por%20género/33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md)
  sobre el PDF oficial de Valve, leído entero allí. Se reutiliza aquí solo para la regla «los
  jefes no responden al ritmo adaptativo» (§2.6), ya citada literalmente en el documento de
  origen — no se reabrió el PDF en esta sesión.
- **Level Design Book** (Robert Yang y colaboradores) — ya citado en
  [13 · 02](./02%20-%20Diseño%20de%20niveles.md). Se reutiliza el principio de distancia entre
  puntos de control (§1.6 de ese documento) para el checkpoint por fase de §2.5.

**La propia biblioteca como verificación cruzada** (no como fuente externa): el `arranque: 26`
de [04 · 30 §5.12](../04%20-%20Recetas%20por%20género/30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md)
y el `ANTICIPATE_FRAMES = 30` de
[04 · 15 §5.8](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) son
código ya escrito en documentos distintos, por criterios distintos, y ambos caen dentro de la
banda de §1.3 sin haberse calculado con esta fórmula — se citan como coincidencia que respalda
la tabla, no como su origen.

**Marcado con ⚠️ en el texto.** La tabla de fotogramas mínimos de §1.3 es una regla de oficio
construida sumando el piso de reacción de Wikipedia, el crecimiento por la ley de Hick y un
margen de ejecución/*input lag* estimado (~80-100 ms): no es una cifra publicada por ningún
estudio de videojuegos. Las convenciones de género nombradas en §2.5 (reinicio completo frente
a checkpoint por fase) describen una práctica ampliamente observada en el medio, sin una fuente
primaria por título verificada en esta sesión — **WebSearch no se usó en esta sesión** (agotado
para el hilo de auditoría que originó este encargo); solo se abrieron las dos URLs de Wikipedia
de arriba con WebFetch.

**Verificación de símbolos.** Todos los símbolos de GML usados en los §4.2-4.4 —
`game_get_speed`, `gamespeed_fps`, `ceil`, `round`, `variable_global_exists`,
`event_inherited`— se comprobaron con `python3 "_indice/buscar.py" <símbolo>` contra el
`GmlSpec.xml` del runtime **2026.0.0.23**. `segundos_a_frames()`, `tiempo_para_matar()`,
`dano_dps_medido()`, `ArquetipoDef`, `EncuentroDef`, `GestorFichas` y `barra_jefe_*` **no** son
símbolos del runtime: son funciones propias ya definidas en los documentos que se enlazan junto
a cada una, y este documento las reutiliza sin redefinirlas. Ningún símbolo que se quiso usar
resultó inexistente.
