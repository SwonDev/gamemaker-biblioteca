# 19 · Cámaras de juego — encuadre, seguimiento y control

> **La cámara es diseño, no un detalle técnico.** Este documento traduce a GameMaker el marco
> de referencia del oficio —Itay Keren, *Scroll Back: The Theory and Practice of Cameras in
> Side-Scrollers* (GDC 2015)— y añade lo que ese marco exige y la biblioteca aún no tenía:
> zonas de cámara por región, *platform-snapping*, transición pantalla-a-pantalla, cámara
> multijugador con zoom dinámico y cinemáticas encoladas.
>
> **No repite** la API de cámaras y viewports (ya en
> [`01 · 10`](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md)
> §5-§8), el sistema de seguimiento con *deadzone*, *look-ahead*, límites y *shake* (ya escrito
> y compilable en [`06/scr_camera.gml`](../06%20-%20Assets%20y%20Scripts/scr_camera.gml)), el
> *screen shake* por trauma y el zoom suavizado (ya en
> [`04 · 15`](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) §5.1), ni
> la decisión pixel-perfect/subpíxel y el redondeo de cámara (ya en
> [`13 · 03`](./03%20-%20Pixel%20art%20y%20resolución.md) §1.5 y §6.5). Este documento **enlaza**
> esas cuatro piezas y construye encima.

---

## 1 · El marco de Itay Keren: un vocabulario para hablar de cámaras

### 1.1 Por qué hacía falta un vocabulario

En 2015, trabajando en *Mushroom 11*, el diseñador israelí **Itay Keren** se encontró con un
problema que cualquiera que haya programado una cámara 2D reconoce: llevaba treinta años de
historia de diseño resolviéndose una y otra vez, juego a juego, sin que nadie le hubiera puesto
nombre a las soluciones. Dio una charla en el Independent Games Summit de la GDC 2015 —*Scroll
Back*— y la publicó como artículo largo. Es, con diferencia, la referencia más citada del oficio
sobre cámaras en scrollers 2D, y esta biblioteca no la tenía: cero apariciones de «Keren» antes
de este documento (auditoría `_indice/auditorias/colisiones-movimiento-camara.md`, tema C13).

Keren parte de una idea sencilla: la cámara no es una ventana neutral, es una **decisión de
diseño** tan deliberada como el salto o el daño. Y como toda decisión de diseño repetida en
cientos de juegos, tiene patrones con nombre. Sin ese vocabulario, cada equipo reinventa la
misma rueda con nombres distintos («la caja invisible», «el rectángulo muerto», «el margen»),
y es imposible decir «esto es lo mismo que hace *Super Mario World*, pero con dos anclas» sin
describir el código entero.

### 1.2 Atención, interacción y comodidad

Keren organiza el problema en tres ejes que compiten entre sí:

| Eje | Pregunta que responde | Ejemplo de conflicto |
|---|---|---|
| **Interacción** (*Interaction*) | ¿Qué necesita ver el jugador para controlar bien el personaje? | Ver lo que tienes delante para reaccionar a tiempo |
| **Atención** (*Attention*) | ¿Qué quiere el diseñador que el jugador mire? | Un jefe, una pista, un elemento narrativo |
| **Comodidad** (*Comfort*) | ¿Es el movimiento de cámara fisiológicamente agradable? | Nada de saltos bruscos, aceleraciones repentinas o mareo |

Keren respalda el eje de comodidad con fisiología concreta: la **fóvea** da visión central
nítida, mientras que la **parafóvea** y la **perifóvea** —los anillos exteriores de la retina—
están especializadas en detectar *cambios de patrón y de velocidad*, con una vía rápida directa
a la amígdala (respuesta de alerta antes de que la corteza visual termine de «entender» la
imagen). El **sistema vestibular** del oído interno, responsable del equilibrio, espera una
correspondencia entre lo que ves moverse y lo que tu cuerpo siente moverse; cuando esa
correspondencia falta —estás sentado quieto pero la perifovea detecta un scroll rápido—, el
resultado puede ser el mismo malestar que leer en un coche. Por eso una cámara que acelera o
frena de golpe no es solo «fea»: es **incómoda de verdad**, y esa incomodidad tiene una causa
neurológica, no solo estética.

De estos tres ejes salen las familias de técnicas que Keren cataloga a lo largo de treinta años
de scrollers, desde *Rally-X* (1980) hasta *The Swapper* (2013). El resto de esta sección
traduce su glosario completo; la sección 3 lo convierte en código GML.

### 1.3 El glosario de *Scroll Back*, traducido

La tabla conserva el término en inglés (es el que usa el oficio en cualquier idioma) y añade la
traducción, la definición de Keren y dónde vive cada técnica en este documento o en el resto de
la biblioteca.

| Término (Keren) | Traducción | Qué es | Dónde |
|---|---|---|---|
| `position-locking` | Bloqueo de posición | La cámara se ancla exactamente a la posición del objetivo, sin margen | `01 · 10` §7, `06/scr_camera.gml` — §3.1 |
| `camera-window` | Ventana de cámara | Rectángulo de inercia: el objetivo se mueve libre dentro; la cámara solo se mueve cuando lo toca | `06/scr_camera.gml` (`cam_set_deadzone`, simétrica) — §3.2 (asimétrica) |
| `edge-snapping` | Anclaje al borde | Límite duro: la cámara no cruza cierto punto (borde de nivel, de sala) | `06/scr_camera.gml` (`cam_set_bounds`) — §3.3 |
| `speedup-push-zone` / `speedup-pull-zone` | Zona de empuje / zona de arrastre | Acelera la cámara **antes** de que el objetivo choque con el borde de la ventana, para que no dé un salto de velocidad en un solo frame (el truco del punto virtual de *Super Mario Bros.*) | §3.3 |
| `position-snapping` | Reencuadre progresivo | Corrige lentamente la deriva del objetivo dentro de la ventana, sin esperar a que toque el borde (*Shinobi*) | Nota en §3.2 |
| `lerp-smoothing` | Suavizado por interpolación lineal | `lerp()` entre la posición actual de cámara y el destino, cada frame | `01 · 10` §7, `06/scr_camera.gml` — §3.1 |
| `physics-smoothing` | Suavizado por pseudo-física | La cámara acelera y frena como un cuerpo físico en vez de interpolar linealmente (más orgánico, menos reactivo) | Nota en §3.2 |
| `platform-snapping` | Anclaje a plataforma | La cámara vertical **no** sigue el salto: se ancla a la última plataforma pisada y solo se realinea al aterrizar en otra | §3.4 |
| `region-based-anchors` | Anclas por región | Distintas zonas de un nivel —incluso dentro de la misma sala— imponen distintos límites, zoom o comportamiento de cámara | §3.5 |
| `region-focus` | Enfoque de región | La cámara encuadra el rectángulo de una región completa en vez de seguir estrictamente al jugador (*Vessel*, *Geometry Wars*) | §3.5 |
| `cue-focus` | Enfoque por señal | Objetos del mundo (jefes, cofres, checkpoints) atraen la cámara hacia ellos con un peso, no de forma binaria | §3.6 |
| `target-focus` | Enfoque por objetivo de control | La cámara se desplaza hacia donde el jugador **apunta** con el mando o el ratón, no solo hacia donde está | `04 · 02` §5.7 (hacia el ratón) |
| `projected-focus` | Enfoque proyectado | La cámara mira hacia donde el objetivo **estará** dentro de un instante, extrapolando su velocidad | `06/scr_camera.gml` (`cam_set_lookahead`) — §3.7 |
| `static-forward-focus` | Enfoque frontal fijo | Espacio extra reservado en la dirección de progresión principal del juego | Implícito en la ventana asimétrica de §3.2 |
| `dual-forward-focus` | Doble enfoque frontal | Dos anclas, una a cada lado; la cámara cambia de ancla al cruzar un umbral de dirección sostenida (*SMW*, *Cave Story*) | §3.8 |
| `gesture-focus` | Enfoque por gesto | Un gesto o acción del jugador (agacharse, trepar) dispara un cambio de encuadre con nombre propio | Nota en §3.8; relacionado con `04 · 30` (combate) |
| `position-averaging` | Promedio de posiciones | Con varios objetivos, la cámara mira al punto medio de todos ellos | §3.10 |
| `zoom-to-fit` | Zoom de ajuste | La cámara se aleja o se acerca (o hace *dolly*) para que quepan todos los elementos relevantes | `04 · 15` §5.1 (zoom suavizado), `03 · 43` §15-17 — §3.10 |
| `cinematic-paths` | Trayectos cinemáticos | La cámara suspende el control normal para mostrar algo con intención narrativa, y luego lo devuelve | §3.11 |
| `camera-path` | Trayecto predefinido | Recorrido fijo que la cámara sigue con `path_get_x`/`path_get_y`, típico de niveles con progresión lineal marcada (*Klonoa*) | §3.11 |
| `auto-scroll` | Scroll automático | El jugador no controla el scroll en absoluto: avanza sin él | `04 · 03` (shmups; fuera del alcance de este documento) |

### 1.4 Qué cámara pide cada género

Ninguna de las técnicas anteriores es universal. La tabla siguiente cruza los géneros que ya
tiene la biblioteca en [`04 - Recetas por género`](../04%20-%20Recetas%20por%20género/) con la
combinación de técnicas de Keren que mejor les sienta, y dónde está cada pieza.

| Género | Técnica primaria | Técnica secundaria | Dónde |
|---|---|---|---|
| Plataformas clásico | `position-locking` + *camera-window* vertical con `platform-snapping` | `edge-snapping` en los bordes del nivel | `04 · 01`, `04 · 37`, aquí §3.2/§3.4 |
| Plataformas veloz (Sonic-like) | *Camera-window* estrecho y centrado + `platform-snapping` | `projected-focus` por velocidad | `06/scr_camera.gml` (look-ahead), aquí §3.4 |
| Metroidvania | `region-based-anchors` (zonas de cámara) + transición pantalla-a-pantalla | `edge-snapping` en límites de sala | `04 · 06`, aquí §3.5/§3.9 |
| Top-down / *twin-stick* | `position-locking` con *deadzone* pequeña + `target-focus` hacia el disparo | `dual-forward-focus` si el personaje gira 180° | `04 · 02`, aquí §3.8 |
| *Shoot 'em up* | `auto-scroll` | `edge-snapping` a los límites del cañón de scroll | `04 · 03` |
| Carreras / vehículos | `projected-focus` por velocidad/ángulo + `zoom-to-fit` dinámico | `camera-path` en circuitos con curvas cerradas | `04 · 12`, aquí §3.7/§3.11 |
| RPG / Action RPG | `position-locking` con *deadzone* amplia | `cue-focus` en NPCs y `region-focus` en salas de jefe | `04 · 04`, aquí §3.5/§3.6 |
| Puzzle / Match-3 | `region-focus` (la sala de puzzle define el encuadre) | `zoom-to-fit` al tamaño del tablero | `04 · 07`, aquí §3.5 |
| Roguelike | `region-based-anchors` por sala procedural | `cue-focus` en cofres y enemigos únicos | `04 · 05`, aquí §3.5/§3.6 |
| Tower Defense / estrategia | Cámara manual (*pan*/zoom del jugador), sin seguimiento automático | `region-focus` al iniciar una oleada | `04 · 08`, `04 · 13` |
| Survival / crafting (mundo abierto) | `position-locking` con *deadzone* grande | `cue-focus` en eventos del mundo | `04 · 09`, aquí §3.6 |
| Visual novel | Cámara estática, o `cinematic-paths` puros | — | `04 · 10`, aquí §3.11 |
| Multijugador local (co-op / *versus*) | `position-averaging` + `zoom-to-fit` dinámico por caja envolvente | *Tether* si un jugador se aleja | `04 · 14`, aquí §3.10 |
| Combate cuerpo a cuerpo / *brawler* | *Camera-window* horizontal (estilo *Street Fighter*) | `gesture-focus` en golpes fuertes (*hit-stop* + *shake*) | `04 · 30`, `04 · 15` |
| Rítmico | Cámara fija, o `auto-scroll` sincronizado al patrón | `cue-focus` en el *beat* | `04 · 19` |
| 3D (primera/tercera persona, orbital) | Fuera del marco de Keren (es 2D); ver la cámara 3D nativa | — | `04 · 29` |

---

## 2 · El método: elegir y componer

### 2.1 Cinco preguntas antes de escribir código

1. **¿Cuántos focos tiene la cámara?** Uno → sigue directo a §3.1-§3.9. Varios (multijugador,
   piezas de *Mushroom 11*) → §3.10 y `position-averaging`.
2. **¿El jugador controla el scroll?** Si no (shmup de scroll forzado, *rail shooter*), es
   `auto-scroll` y este documento no aplica: ve a `04 · 03`.
3. **¿El nivel tiene carácter por zonas?** Un pasillo estrecho no debe encuadrarse igual que una
   sala de jefe. Si la respuesta es sí, necesitas §3.5 (zonas de cámara) antes que cualquier otra
   cosa: es la pieza que ordena a todas las demás.
4. **¿Hace falta anticipar el movimiento?** Salto (`platform-snapping`, §3.4), velocidad alta
   (`projected-focus`, §3.7) o cambios de dirección frecuentes (`dual-forward-focus`, §3.8).
5. **¿Hay narrativa o eventos que merecen atención propia?** `cue-focus` (§3.6) para atraer sin
   quitar el control; `cinematic-paths` (§3.11) para quitarlo con intención y devolverlo.

### 2.2 Las técnicas se apilan, no se sustituyen

El propio caso de estudio de Keren —el sistema de cámara de *Mushroom 11*— no usa **una**
técnica: usa regiones (`region-based-anchors`) que dictan si el foco es un promedio de posiciones
o el más avanzado en progresión (`position-averaging` frente a un `static-forward-focus` por
región), con `cue-focus` superpuesto para los jefes, y todo suavizado con `projected-focus` +
`physics-smoothing`. Ninguna técnica de esta lista es «la solución»: son capas que se activan o
desactivan según el contexto del nivel.

En GameMaker eso se traduce en una idea de arquitectura muy simple: **una sola cámara, muchas
funciones puras que calculan "a dónde debería ir"**, y el `Step` del controlador decide qué
combinación aplicar según el estado actual (zona, si hay atractores activos, si hay una
cinemática en curso). Es el mismo patrón que ya usa
[`06/scr_camera.gml`](../06%20-%20Assets%20y%20Scripts/scr_camera.gml) —un struct de datos por
cámara, actualizado una vez por *Step*— y el que sigue todo el código de este documento.

### 2.3 Lo que ya tienes en esta biblioteca (sin repetirlo)

| Ya resuelto | Dónde |
|---|---|
| Seguir al jugador con `lerp()`, *deadzone* simétrica, límites de sala | `01 · 10` §7, `06/scr_camera.gml` |
| *Look-ahead* (equivalente a `projected-focus` con clamp) | `06/scr_camera.gml` (`cam_set_lookahead`) |
| *Screen shake* por trauma, zoom suavizado, *punch* direccional | `04 · 15` §5.1 |
| Pixel-perfect frente a subpíxel, redondeo de cámara, decisión de arquitectura | `13 · 03` §1.5, §6.5 |
| Pantalla partida (*split screen*) estática | `01 · 10` §7 |
| Fundido a negro entre rooms (`objTransitionZone` + `objSpawnPoint`) | `04 · 06` §4.1, §5.1 |
| Cámara 3D (primera persona, orbital, tercera persona) | `04 · 29` §1, §7 |

Este documento **extiende** cada fila cuando hace falta (marcado en la sección correspondiente)
y **añade** lo que faltaba: zonas de cámara, *platform-snapping*, ventana asimétrica, atractores,
transición pantalla-a-pantalla, cámara multijugador con zoom dinámico y cinemáticas encoladas.

---

## 3 · Cómo se traduce a GameMaker

Todo el código de esta sección asume un objeto controlador persistente, `obj_camara_director`,
construido sobre los mismos handles y convenciones que `06/scr_camera.gml` (una cámara creada
con `camera_create()`, asignada a `view_camera[0]`). El esqueleto de partida es este; cada
subsección siguiente **añade** variables y bloques de código a él — coméntalo así en tu proyecto
para saber de dónde viene cada pieza:

```gml
/// ---------------------------------------------------------------------------
/// obj_camara_director — Create   (persistente, una única instancia)
/// ---------------------------------------------------------------------------
cam = camera_create();
camera_set_view_size(cam, 480, 270);
view_camera[0] = cam;

// Posición lógica (con decimales; solo se redondea al entregar a la cámara,
// igual que en 13 · 03 §6.5).
cam_x = obj_jugador.x;
cam_y = obj_jugador.y;

estado = "libre";   // "libre" | "transicion_pantalla" | "cinematica" | "multijugador"
```

```gml
/// ---------------------------------------------------------------------------
/// obj_camara_director — Clean Up
/// ---------------------------------------------------------------------------
camera_destroy(cam);   // obligatorio: 01 · 10 §5, si no hay memory leak.
```

### 3.1 Position-locking y el *camera-window* simétrico (ya resueltos)

Es el punto de partida de cualquier cámara: bloqueo de posición puro
(`position-locking`), suavizado con `lerp()`, y una ventana de inercia simétrica
(*camera-window*) para no seguir cada temblor de un píxel. Las tres están **completas y
verificadas** en [`01 · 10`](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md)
§7 («Seguir al jugador manualmente») y en
[`06/scr_camera.gml`](../06%20-%20Assets%20y%20Scripts/scr_camera.gml) (`cam_set_deadzone`,
`cam_set_smooth`, `cam_update`). No hay nada que añadir aquí: si tu juego solo necesita esto,
ya está resuelto. El resto de esta sección son **extensiones** para cuando esto se queda corto.

### 3.2 *Camera-window* asimétrico

La ventana simétrica de `06/scr_camera.gml` (`dz_ancho`/`dz_alto`) reparte el margen por igual
en las cuatro direcciones. Keren documenta que casi ningún juego serio hace eso: *Wonder Boy*
usa una ventana de un solo lado (todo el margen es hacia adelante), y *Rastan Saga* ajusta el
alto de la ventana al tamaño exacto de un salto para no disparar movimiento vertical en cada
brinco. Una ventana **asimétrica** — cuatro márgenes independientes — cubre ambos casos y es el
`camera-window` genérico del que la *deadzone* simétrica es solo un caso particular.

```gml
/// obj_camara_director — Create  (añadido a §3.0)
// Margen en cada dirección, en píxeles de room. Asimétrica a propósito: más
// margen hacia donde avanza el juego (derecha) que hacia atrás.
ventana = {
    izq    : 60,
    der    : 120,
    arriba : 50,
    abajo  : 50
};
```

```gml
/// @func camara_ventana_empujar(_ventana, _cam_x, _cam_y, _obj_x, _obj_y)
/// @desc Empuja el centro de cámara (_cam_x, _cam_y) lo mínimo necesario para
///       que (_obj_x, _obj_y) quede dentro del rectángulo de la ventana.
///       Devuelve un array [nuevo_x, nuevo_y] SIN suavizar: el suavizado se
///       aplica después, sobre el resultado (ver `lerp-smoothing` en §1.3).
/// @param {Struct} _ventana  Struct { izq, der, arriba, abajo } en píxeles.
/// @param {Real}   _cam_x    Centro de cámara actual, X.
/// @param {Real}   _cam_y    Centro de cámara actual, Y.
/// @param {Real}   _obj_x    Posición del objetivo, X.
/// @param {Real}   _obj_y    Posición del objetivo, Y.
/// @returns {Array<Real>}    [nuevo_cam_x, nuevo_cam_y]
function camara_ventana_empujar(_ventana, _cam_x, _cam_y, _obj_x, _obj_y)
{
    var _izq = _cam_x - _ventana.izq;
    var _der = _cam_x + _ventana.der;
    var _arr = _cam_y - _ventana.arriba;
    var _aba = _cam_y + _ventana.abajo;

    if (_obj_x < _izq) { _cam_x -= (_izq - _obj_x); }
    if (_obj_x > _der) { _cam_x += (_obj_x - _der); }
    if (_obj_y < _arr) { _cam_y -= (_arr - _obj_y); }
    if (_obj_y > _aba) { _cam_y += (_obj_y - _aba); }

    return [_cam_x, _cam_y];
}
```

```gml
/// obj_camara_director — Step   (estado == "libre")
var _resultado = camara_ventana_empujar(ventana, cam_x, cam_y, obj_jugador.x, obj_jugador.y);
cam_x = lerp(cam_x, _resultado[0], 0.2);
cam_y = lerp(cam_y, _resultado[1], 0.2);
```

> 💡 **`position-snapping` (Shinobi)**: si tu ventana es muy ancha o muy alta (necesario cuando
> hay saltos grandes, como en *Shinobi*), el objetivo puede quedarse «atascado» en un extremo
> de la ventana con muy poco margen de visión hacia el otro lado. La solución de Keren no es
> encoger la ventana: es alinear la cámara **lentamente** hacia el objetivo incluso dentro de la
> ventana, con un factor de `lerp()` mucho más suave que el del empuje normal (`0.02` frente a
> `0.2`, por ejemplo). Es una segunda pasada de `lerp()` sobre el resultado, no una técnica
> nueva.

> ⚠️ **`physics-smoothing` frente a `lerp-smoothing`**: `lerp()` es *ease-out* puro: se mueve
> rápido al principio y frena según se acerca al destino, pero **arranca instantáneamente**. Un
> suavizado por pseudo-física (llevar una velocidad de cámara que acelera hacia el objetivo y
> frena al llegar, un *ease-in-out*) se siente más orgánico pero reacciona más tarde a cambios
> bruscos — Keren lo cita en *Never Alone*. No hay una función `physics_smooth()` en el runtime:
> se construye con un `vel_cam_x`/`vel_cam_y` propios y `approach()` (ya usado en
> `06/scr_camera.gml`), o revisando `SmoothDamp` de otros motores como referencia de diseño, no
> de API — GameMaker no lo trae.

### 3.3 *Edge-snapping*, y el acelerón antes del borde (*speedup-zones*)

El anclaje a un borde duro (`edge-snapping`) ya está resuelto: es exactamente lo que hace
`cam_set_bounds()` de `06/scr_camera.gml` con el `clamp()` a los límites de la room (cubre C4 y
C12 de la auditoría en su forma simple). Lo que falta es el matiz que documenta Keren en *Super
Mario Bros.*: si la cámara solo empieza a moverse **al tocar** el borde, y Mario cruza ese borde
a velocidad máxima, el fondo pasa de 0 a máxima velocidad en un solo frame — un salto de
velocidad, no de posición, y por eso incómodo (ver el eje de *comfort* en §1.2). La solución de
los diseñadores originales fue un punto virtual, un 25% antes del borde real, donde la cámara ya
empieza a acelerar para llegar «calentada» al momento del cruce.

```gml
/// obj_camara_director — Step  (extiende el empuje de ventana de §3.2)
// Franja de aceleración ANTES del borde derecho de la ventana: en vez de
// esperar al empuje de golpe, la cámara ya se mueve un poco en la dirección
// del jugador mientras se acerca al borde.
var PUSH_ZONE_ANCHO = 32;

var _borde_der = cam_x + ventana.der;
var _dist_al_borde = _borde_der - obj_jugador.x;

if (_dist_al_borde < PUSH_ZONE_ANCHO && obj_jugador.vel_x > 0)
{
    var _empuje = 1 - (_dist_al_borde / PUSH_ZONE_ANCHO);
    cam_x += obj_jugador.vel_x * _empuje * 0.1;
}
```

### 3.4 *Platform-snapping*

El *shake* por trauma y el zoom ya están resueltos (`04 · 15` §5.1), pero ninguno de los dos
resuelve el problema que más se nota en un plataformas «barato»: la cámara vertical siguiendo
cada salto en tiempo real, lo que hace que la pantalla «bote» constantemente. *Super Mario
World* introdujo la solución: la cámara vertical se queda **anclada** a la última plataforma
pisada durante todo el salto, y solo se realinea de golpe al aterrizar en una plataforma de
altura distinta. Es el mismo patrón que usa *Celeste* y casi todo plataformas serio.

```gml
/// obj_camara_director — Create  (añadido)
plataforma_y_referencia = obj_jugador.y;
```

```gml
/// obj_camara_director — Step
// `on_ground` es la misma variable que ya mantiene `objPlayer` en `04 · 01`
// (§5, "Actualizar flag de suelo"). Si tu jugador tiene coyote time, cuenta
// también los frames de coyote como "en el suelo" para este propósito: si
// no, la cámara reencuadraría un instante antes de que el salto sea posible.
var _apoyado = obj_jugador.on_ground || (obj_jugador.coyote_timer > 0);

if (_apoyado)
{
    // Cada aterrizaje mueve la referencia a la Y actual y la fija ahí.
    plataforma_y_referencia = obj_jugador.y;
}

// La cámara vertical IGNORA la Y real del jugador mientras está en el aire:
// solo mira a la última plataforma pisada.
var _vh = camera_get_view_height(cam);
var _cam_y_destino = plataforma_y_referencia - _vh / 2;
cam_y = lerp(cam_y, _cam_y_destino, 0.15);
```

> ⚠️ **Cuándo NO usar esto**: Keren lo remarca — `platform-snapping` solo tiene sentido si el
> juego trata el «estar en el suelo» como un estado bien definido. En un juego con vuelo libre,
> doble salto sin aterrizaje intermedio frecuente o un personaje tipo mochila propulsora (su
> ejemplo es *Awesomenauts*), la cámara debe volver a un `camera-window` vertical normal (§3.1),
> porque «anclarse al suelo» cuando casi nunca lo tocas produce el efecto contrario: una cámara
> que no reacciona.

### 3.5 *Region-based-anchors*: zonas de cámara

Es el hueco más citado por la auditoría (C5, C11 y la mitad de C6): la biblioteca solo tenía el
*clamp* a la room entera. Keren dedica una sección completa a esto porque es lo que separa un
prototipo de un nivel diseñado: un pasillo debe encuadrarse como pasillo, y una sala de jefe debe
verse entera. *Donkey Kong Country* fue de los primeros en dar a los diseñadores control de
cámara por región, incluso dentro del mismo nivel.

```gml
/// ---------------------------------------------------------------------------
/// obj_camara_zona — objeto invisible; se estira en el Room Editor con un
/// sprite de 1x1 (image_xscale/image_yscale) para cubrir el rectángulo de
/// encuadre de una región: un pasillo, una sala de jefe, una plaza abierta.
/// Variables de instancia (definidas en el editor, una por zona colocada):
///   tipo_zona : "seguimiento" (clamp normal, el jugador se mueve libre
///               dentro) | "fija" (la cámara centra el rectángulo completo,
///               ver §3.9 para el uso en transición pantalla-a-pantalla)
///   zoom_zona : 1  (multiplicador de la vista base en esta zona)
/// ---------------------------------------------------------------------------

/// obj_camara_zona — Create
tipo_zona = "seguimiento";
zoom_zona = 1;
```

```gml
/// @func zona_camara_detectar(_x, _y)
/// @desc Devuelve la instancia de `obj_camara_zona` que contiene el punto
///       dado, o `noone` si no hay ninguna. Si dos zonas se solapan, gana la
///       de índice de instancia más alto: coloca las zonas específicas
///       (una sala pequeña) DESPUÉS que las generales (el nivel entero) en
///       el Room Editor.
/// @param {Real} _x
/// @param {Real} _y
/// @returns {Id.Instance}
function zona_camara_detectar(_x, _y)
{
    var _resultado = noone;
    with (obj_camara_zona)
    {
        if (point_in_rectangle(_x, _y, bbox_left, bbox_top, bbox_right, bbox_bottom))
        {
            _resultado = id;
        }
    }
    return _resultado;
}
```

```gml
/// obj_camara_director — Create  (añadido)
zona_actual       = noone;
zona_anterior     = noone;
zona_transicion_t = 1;
```

```gml
/// obj_camara_director — Step  (antes del empuje de ventana de §3.2)
var _zona = zona_camara_detectar(obj_jugador.x, obj_jugador.y);

if (_zona != noone && _zona != zona_actual)
{
    zona_anterior     = zona_actual;
    zona_actual       = _zona;
    zona_transicion_t = 0;
}

if (zona_actual != noone)
{
    var _lim_izq = zona_actual.bbox_left;
    var _lim_der = zona_actual.bbox_right;
    var _lim_arr = zona_actual.bbox_top;
    var _lim_aba = zona_actual.bbox_bottom;

    if (zona_anterior != noone && zona_transicion_t < 1)
    {
        // Mezclamos los límites viejos con los nuevos: el rectángulo de
        // recorte se "abre" o "cierra" con suavidad en vez de saltar de
        // golpe al cruzar el umbral entre un pasillo y una sala grande.
        zona_transicion_t = clamp(zona_transicion_t + 0.04, 0, 1);
        _lim_izq = lerp(zona_anterior.bbox_left,   _lim_izq, zona_transicion_t);
        _lim_der = lerp(zona_anterior.bbox_right,  _lim_der, zona_transicion_t);
        _lim_arr = lerp(zona_anterior.bbox_top,    _lim_arr, zona_transicion_t);
        _lim_aba = lerp(zona_anterior.bbox_bottom, _lim_aba, zona_transicion_t);
    }

    // Reutiliza el clamp ya escrito y verificado en 06/scr_camera.gml: solo
    // le pasamos los límites de la zona en vez de los de la room entera.
    cam_set_bounds(cam, _lim_izq, _lim_arr, _lim_der, _lim_aba);

    // region-focus: si la zona es más pequeña que la vista, cam_update() de
    // scr_camera.gml ya centra en ese eje (el caso "sala más pequeña que la
    // vista" de C4). Aquí solo añadimos el zoom propio de la zona:
    var _vw_base = camera_get_view_width(cam);
    var _zoom_destino = zona_actual.zoom_zona;
    zoom_actual = lerp(is_undefined(zoom_actual) ? 1 : zoom_actual, _zoom_destino, 0.05);
}
```

> 💡 **`region-focus` frente a seguimiento normal**: dentro de una zona pequeña (un puzzle de
> una sola sala, como en *Vessel*), no tiene sentido aplicar la ventana de §3.2: el `clamp()` a
> los límites de la zona ya centra la sala completa en cuanto es más pequeña que la vista. Deja
> el resto del código de seguimiento tal cual — no hace falta una rama especial, `cam_set_bounds`
> ya resuelve ese caso (documentado en C4).

### 3.6 *Cue-focus*: atractores y detractores

*Insanely Twisted Shadow Planet* introdujo un sistema de «doble anillo»: dentro del anillo
interior, el atractor manda del todo sobre el encuadre; entre los dos anillos, se mezcla
proporcionalmente con la posición del jugador. Varios atractores pueden solaparse y sumarse. Un
peso negativo convierte un atractor en **detractor** — aleja la cámara de un punto en vez de
acercarla, útil para ocultar algo hasta que el jugador se acerque physicamente.

```gml
/// @func atractor_crear(_x, _y, _radio_interior, _radio_exterior, _peso)
/// @desc Struct de un atractor (o detractor, con _peso negativo) de cámara.
/// @param {Real} _x
/// @param {Real} _y
/// @param {Real} _radio_interior  Dentro de este radio, el atractor manda del todo.
/// @param {Real} _radio_exterior  Fuera de este radio, no tiene efecto.
/// @param {Real} _peso            1 = atrae con toda su fuerza; -1 = repele; 0.5 = a medias.
/// @returns {Struct}
function atractor_crear(_x, _y, _radio_interior, _radio_exterior, _peso = 1)
{
    return { x: _x, y: _y, r_int: _radio_interior, r_ext: _radio_exterior, peso: _peso };
}

/// @func camara_atraccion_evaluar(_atractores, _obj_x, _obj_y)
/// @desc Aplica todos los atractores activos sobre la posición base del
///       objetivo y devuelve el punto de enfoque final. Varios atractores se
///       acumulan (Keren: "different cues have different rings... can overlap").
/// @param {Array<Struct>} _atractores
/// @param {Real} _obj_x
/// @param {Real} _obj_y
/// @returns {Array<Real>} [foco_x, foco_y]
function camara_atraccion_evaluar(_atractores, _obj_x, _obj_y)
{
    var _foco_x = _obj_x;
    var _foco_y = _obj_y;

    var _n = array_length(_atractores);
    for (var _i = 0; _i < _n; _i++)
    {
        var _a = _atractores[_i];
        var _dist = point_distance(_obj_x, _obj_y, _a.x, _a.y);

        var _factor = 0;
        if (_dist <= _a.r_int)
        {
            _factor = 1;
        }
        else if (_dist < _a.r_ext)
        {
            _factor = 1 - ((_dist - _a.r_int) / (_a.r_ext - _a.r_int));
        }
        _factor = clamp(_factor * _a.peso, -1, 1);

        _foco_x = lerp(_foco_x, _a.x, _factor);
        _foco_y = lerp(_foco_y, _a.y, _factor);
    }

    return [_foco_x, _foco_y];
}
```

```gml
/// obj_camara_director — Step  (sustituye el objetivo de §3.2 cuando hay atractores)
atractores_activos = [];
if (instance_exists(obj_jefe))
{
    array_push(atractores_activos, atractor_crear(obj_jefe.x, obj_jefe.y, 80, 260, 0.6));
}

var _foco = camara_atraccion_evaluar(atractores_activos, obj_jugador.x, obj_jugador.y);
var _resultado = camara_ventana_empujar(ventana, cam_x, cam_y, _foco[0], _foco[1]);
cam_x = lerp(cam_x, _resultado[0], 0.2);
cam_y = lerp(cam_y, _resultado[1], 0.2);
```

### 3.7 *Projected-focus* más allá del *look-ahead*

`cam_set_lookahead()` de `06/scr_camera.gml` **ya es** una implementación de `projected-focus`:
anticipa la cámara según la velocidad del objetivo, con un `clamp()` a `[-1, 1]` para que un
teletransporte no dispare la cámara al otro lado de la sala. Ese *clamp* es correcto para un
personaje con velocidad acotada (un plataformas), pero en un juego donde la velocidad varía
mucho — coches a fondo, balas, un *twin-stick* muy rápido — conviene que la anticipación **escale
con la velocidad real** en vez de saturar en un tope fijo:

```gml
/// @func camara_proyeccion(_x, _y, _vel_x, _vel_y, _tiempo)
/// @desc Punto de enfoque proyectado `_tiempo` segundos hacia adelante según
///       la velocidad actual. Mismo principio que `cam_set_lookahead()`, sin
///       el clamp a [-1, 1]: la anticipación crece con la velocidad real.
/// @param {Real} _x
/// @param {Real} _y
/// @param {Real} _vel_x  Píxeles por segundo (no por frame: multiplica por 1
///                       si tu velocidad ya está en unidades/segundo, o
///                       convierte con delta_time si está en unidades/frame).
/// @param {Real} _vel_y
/// @param {Real} _tiempo Segundos hacia adelante que se proyecta.
/// @returns {Array<Real>} [foco_x, foco_y]
function camara_proyeccion(_x, _y, _vel_x, _vel_y, _tiempo)
{
    return [_x + _vel_x * _tiempo, _y + _vel_y * _tiempo];
}
```

Ya está aplicado con código completo en dos sitios de la biblioteca, y no hace falta repetirlo:
[`04 · 12`](../04%20-%20Recetas%20por%20género/12%20-%20Carreras%20y%20vehículos.md) §5.6 proyecta
según el ángulo del coche (no la velocidad lineal en bruto), y
[`04 · 02`](../04%20-%20Recetas%20por%20género/02%20-%20Top-Down%20_%20Twin-Stick.md) §5.7 proyecta
hacia el ratón en vez de hacia la velocidad — es `target-focus`, no `projected-focus`, pero
resuelve la misma necesidad de anticipación en un top-down.

> ⚠️ En saltos verticales, la proyección por velocidad extrapola mal: justo antes de aterrizar
> la velocidad vertical es máxima (caída libre), y proyectar hacia adelante mueve la cámara hacia
> abajo en el peor momento posible. Por eso `platform-snapping` (§3.4) existe como alternativa
> específica para el eje vertical de un plataformas, y no «más `projected-focus`».

### 3.8 *Dual-forward-focus* con histéresis

*Super Mario World* mantiene dos anclas de cámara, una a cada lado del jugador, y solo cambia de
ancla cuando el jugador se ha desplazado una distancia mínima en la nueva dirección — no en
cuanto invierte el signo de la velocidad. Sin ese umbral, cualquier vacilación cerca de una
pared produciría un tirón de cámara cada frame. *Cave Story* hace lo mismo pero variando la
velocidad de cambio de ancla según la velocidad de andar del personaje.

```gml
/// obj_camara_director — Create  (añadido)
foco_dir_actual = 1;    // 1 = ancla a la derecha, -1 = ancla a la izquierda
foco_dir_dist   = 0;    // distancia acumulada moviéndose en la dirección contraria al ancla
```

```gml
/// obj_camara_director — Step
var UMBRAL_CAMBIO_FOCO = 40;    // píxeles que hay que recorrer para que cambie el ancla
var DISTANCIA_ANCLA    = 90;    // separación del ancla respecto al jugador

var _dir_actual = sign(obj_jugador.vel_x);

if (_dir_actual != 0 && _dir_actual != foco_dir_actual)
{
    foco_dir_dist += abs(obj_jugador.vel_x);
    if (foco_dir_dist > UMBRAL_CAMBIO_FOCO)
    {
        foco_dir_actual = _dir_actual;
        foco_dir_dist = 0;
    }
}
else
{
    foco_dir_dist = 0;   // se resetea en cuanto vuelve a moverse en la dirección del ancla actual
}

var _foco_x = obj_jugador.x + foco_dir_actual * DISTANCIA_ANCLA;
var _resultado = camara_ventana_empujar(ventana, cam_x, cam_y, _foco_x, obj_jugador.y);
cam_x = lerp(cam_x, _resultado[0], 0.2);
```

> 💡 **`gesture-focus`**: un cambio de encuadre disparado por una acción concreta del jugador
> (agacharse para ver más abajo, apuntar hacia arriba) es la misma idea con un *trigger* distinto
> al umbral de distancia: en vez de `foco_dir_actual`, cambias el desplazamiento del ancla al
> entrar en el estado «agachado» de tu máquina de estados de jugador. Ver el patrón de estados
> agachado/de pie ya resuelto en
> [`04 · 37`](../04%20-%20Recetas%20por%20género/37%20-%20Traversal%20en%20plataformas%20-%20pendientes,%20paredes,%20escaleras%20y%20bordes.md).

### 3.9 Transición pantalla-a-pantalla

`04 · 06` ya resuelve la transición entre rooms con fundido a negro (`objTransitionZone` +
`objSpawnPoint`). Lo que falta —y es lo que de verdad se recuerda de *Zelda 1* o del *Metroid*
original— es que la cámara **viaja** de una pantalla a la siguiente mientras el juego se
congela, en vez de cortar a negro. Hay dos formas de conseguirlo en GameMaker, con costes muy
distintos.

**Variante A — una sola room grande dividida en zonas «fijas» (recomendada).** Reutiliza el
sistema de zonas de §3.5: cuando `tipo_zona` de la zona nueva y de la vieja son ambas `"fija"`,
en vez del *clamp* progresivo se dispara un paneo a velocidad constante entre los dos centros.

```gml
/// obj_camara_director — Step  (sustituye la detección de zona de §3.5 cuando
/// AMBAS zonas implicadas son "fija" y no hay ya una transición en curso)
var VELOCIDAD_PANEO_PX_SEG = 220;   // constante: así se siente "viaje", no "easing"

if (_zona != noone && _zona != zona_actual && zona_actual != noone
    && zona_actual.tipo_zona == "fija" && _zona.tipo_zona == "fija"
    && estado == "libre")
{
    estado = "transicion_pantalla";
    obj_jugador.input_bloqueado = true;   // mismo patrón que "transicionando" en 04 · 06 §5.1

    var _origen_x  = (zona_actual.bbox_left + zona_actual.bbox_right) / 2;
    var _origen_y  = (zona_actual.bbox_top  + zona_actual.bbox_bottom) / 2;
    var _destino_x = (_zona.bbox_left + _zona.bbox_right) / 2;
    var _destino_y = (_zona.bbox_top  + _zona.bbox_bottom) / 2;

    var _dist = point_distance(_origen_x, _origen_y, _destino_x, _destino_y);
    var _duracion = _dist / VELOCIDAD_PANEO_PX_SEG;
    var _zona_nueva = _zona;

    // tween_to() es de 06/scr_camera.gml — no: de scr_tween.gml (dependencia
    // nueva de este documento). ease_linear = velocidad constante, no un
    // frenado al llegar: es justo el efecto de "la cámara viaja" de Keren.
    tween_to(id, { cam_x: _destino_x, cam_y: _destino_y }, _duracion, ease_linear,
        function()
        {
            estado = "libre";
            zona_anterior = zona_actual;
            zona_actual   = zona_nueva;
            obj_jugador.input_bloqueado = false;
        });
}
```

```gml
/// obj_camara_director — Step  (en cualquier estado)
tween_update();   // scr_tween.gml: avanza todos los tweens activos, uno por frame
```

**Variante B — rooms independientes por pantalla, con deslizamiento capturado (avanzada).**
Cuando cada pantalla es literalmente una room distinta de GameMaker (no una zona dentro de una
room grande), no hay forma de que la cámara «viaje» de una a otra de forma nativa: la solución
que usan los proyectos que lo consiguen es capturar una instantánea de la pantalla saliente
justo antes de `room_goto()` y deslizarla por encima de la sala entrante mientras esta ya
renderiza detrás.

```gml
/// ---------------------------------------------------------------------------
/// obj_transicion_pantalla — Persistent, una única instancia creada en la
/// primera room del juego (no se destruye entre rooms).
/// ---------------------------------------------------------------------------

/// obj_transicion_pantalla — Create
captura           = -1;      // surface con la instantánea de la pantalla saliente
direccion_salida  = 0;       // grados GML: 0 = derecha, 90 = arriba, 180 = izquierda, 270 = abajo
progreso          = 1;       // 1 = sin transición activa
duracion_segundos = 0.35;

/// @func transicion_pantalla_iniciar(_room_destino, _direccion)
/// @desc Congela la vista actual en una surface, cambia de room y la desliza
///       hacia `_direccion` mientras la nueva sala aparece detrás.
/// @param {Asset.GMRoom} _room_destino
/// @param {Real} _direccion  0/90/180/270.
function transicion_pantalla_iniciar(_room_destino, _direccion)
{
    var _vw = camera_get_view_width(view_camera[0]);
    var _vh = camera_get_view_height(view_camera[0]);

    if (surface_exists(captura)) { surface_free(captura); }
    captura = surface_create(_vw, _vh);
    surface_copy(captura, 0, 0, application_surface);

    direccion_salida = _direccion;
    progreso = 0;

    room_goto(_room_destino);
}

/// obj_transicion_pantalla — Step
if (progreso < 1)
{
    progreso += (delta_time / 1000000) / duracion_segundos;
    if (progreso >= 1)
    {
        progreso = 1;
        if (surface_exists(captura)) { surface_free(captura); captura = -1; }
    }
}

/// obj_transicion_pantalla — Draw GUI   (por encima de la sala nueva)
if (progreso < 1 && surface_exists(captura))
{
    var _gw = display_get_gui_width();
    var _gh = display_get_gui_height();
    var _offset_x = lengthdir_x(_gw, direccion_salida) * progreso;
    var _offset_y = lengthdir_y(_gh, direccion_salida) * progreso;
    draw_surface(captura, _offset_x, _offset_y);
}
```

> ⚠️ **Coste y fragilidad de la Variante B**: una `surface` del tamaño del viewport, viva solo
> durante la transición (por eso se libera en cuanto `progreso` llega a 1: dejar una surface sin
> `surface_free()` es la fuga de memoria más común del motor). Además, la sala entrante debe
> tener ya el estado correcto (posición de spawn, cámara centrada) desde su primer frame, porque
> se ve renderizada detrás de la instantánea saliente desde el instante cero — combínalo con el
> `objSpawnPoint` de `04 · 06` §5.1 para eso. Para casi cualquier metroidvania o Zelda-like, la
> **Variante A es la que hay que elegir por defecto**: es más simple, no depende de surfaces, y
> es exactamente el efecto original (una sola room lógica, dividida en pantallas).

### 3.10 Cámara multijugador con zoom dinámico

Split screen estático (`04 · 14` §8, `01 · 10` §7) resuelve el caso simple. Cuando los
jugadores comparten **una** cámara —*Towerfall*, *Samurai Gunn*, *Super Smash Bros.*— la técnica
de Keren es `position-averaging` (mirar al centro del grupo) combinado con `zoom-to-fit`
dinámico (alejar la cámara cuanto haga falta para que quepan todos).

```gml
/// obj_camara_director — Create  (añadido)
zoom_view_w_base = 480;   // ancho de vista a zoom 1 (el de camera_create)
zoom_view_h_base = 270;
zoom_min         = 0.5;   // más alejada: ve más mundo
zoom_max         = 1.5;   // más cerca: menos mundo, más detalle
zoom_actual      = 1;
zoom_margen      = 96;    // aire alrededor del grupo, en píxeles de room
```

```gml
/// @func camara_grupo_bbox(_obj_jugador)
/// @desc Caja que envuelve a todas las instancias vivas de `_obj_jugador`.
/// @param {Asset.GMObject} _obj_jugador
/// @returns {Struct|Undefined}  { izq, der, arr, aba, cx, cy }, o `undefined`
///          si no queda ninguna instancia con vida.
function camara_grupo_bbox(_obj_jugador)
{
    if (instance_number(_obj_jugador) == 0) { return undefined; }

    var _izq = infinity;
    var _der = -infinity;
    var _arr = infinity;
    var _aba = -infinity;

    with (_obj_jugador)
    {
        _izq = min(_izq, x);
        _der = max(_der, x);
        _arr = min(_arr, y);
        _aba = max(_aba, y);
    }

    return { izq: _izq, der: _der, arr: _arr, aba: _aba,
             cx: (_izq + _der) / 2, cy: (_arr + _aba) / 2 };
}
```

```gml
/// obj_camara_director — Step  (estado == "multijugador")
var _grupo = camara_grupo_bbox(obj_jugador);

if (!is_undefined(_grupo))
{
    cam_x = lerp(cam_x, _grupo.cx, 0.08);
    cam_y = lerp(cam_y, _grupo.cy, 0.08);

    var _ancho_necesario = (_grupo.der - _grupo.izq) + zoom_margen * 2;
    var _alto_necesario  = (_grupo.aba - _grupo.arr) + zoom_margen * 2;

    var _zoom_x = zoom_view_w_base / max(_ancho_necesario, 1);
    var _zoom_y = zoom_view_h_base / max(_alto_necesario, 1);
    var _zoom_deseado = clamp(min(_zoom_x, _zoom_y), zoom_min, zoom_max);

    zoom_actual = lerp(zoom_actual, _zoom_deseado, 0.05);

    // Tether suave: nadie puede alejarse más de lo que zoom_min permite ver.
    // En vez de dejar que el zoom se salga de rango, se empuja al jugador de
    // vuelta hacia el grupo (Keren cita Gauntlet como el fallo de NO tener
    // esto: los jugadores podían bloquearse mutuamente sin poder cruzar el
    // borde de pantalla).
    var _radio_max = (zoom_view_w_base / zoom_min) / 2;
    with (obj_jugador)
    {
        var _dx = x - other.cam_x;
        var _dy = y - other.cam_y;
        var _dist_centro = point_distance(0, 0, _dx, _dy);
        if (_dist_centro > _radio_max)
        {
            var _factor = _radio_max / _dist_centro;
            x = other.cam_x + _dx * _factor;
            y = other.cam_y + _dy * _factor;
        }
    }
}

camera_set_view_size(cam, round(zoom_view_w_base / zoom_actual),
                           round(zoom_view_h_base / zoom_actual));
```

**El choque con el pixel-perfect.** `zoom_actual` no entero significa que
`zoom_view_w_base / zoom_actual` casi nunca da un número entero de píxeles de room — exactamente
la «distorsión de píxel al hacer zoom» que documenta
[`03 · 43`](../03%20-%20Cursos%20%28YouTube%29/43%20-%20PixelatedPope%20-%20Cámaras%20y%20Resolución%202026%20-%20Parte%203%20-%20Avanzado.md)
§17, y la misma decisión pixel-perfect/subpíxel de
[`13 · 03`](./03%20-%20Pixel%20art%20y%20resolución.md) §1.5. Con zoom dinámico no hay forma de
tener las dos cosas a la vez de forma continua: o aceptas subpíxel mientras el zoom cambia, o
cuantizas el zoom a un número fijo de escalones elegidos para que el resultado sea entero:

```gml
/// @func zoom_cuantizar(_zoom_deseado, _zoom_min, _zoom_max, _pasos)
/// @desc Redondea el zoom deseado al escalón más cercano de una escala de
///       `_pasos` niveles fijos entre `_zoom_min` y `_zoom_max`. No garantiza
///       por sí solo que `zoom_view_w_base / zoom` sea entero — para eso,
///       elige `_zoom_min`/`_zoom_max`/`_pasos` de forma que cada escalón
///       resultante SÍ lo sea, y verifícalo una vez con `show_debug_message`
///       antes de confiar en la tabla.
/// @param {Real} _zoom_deseado
/// @param {Real} _zoom_min
/// @param {Real} _zoom_max
/// @param {Real} _pasos
/// @returns {Real}
function zoom_cuantizar(_zoom_deseado, _zoom_min, _zoom_max, _pasos)
{
    var _t = clamp((_zoom_deseado - _zoom_min) / (_zoom_max - _zoom_min), 0, 1);
    var _paso = round(_t * _pasos);
    return lerp(_zoom_min, _zoom_max, _paso / _pasos);
}
```

> ⚠️ La opción más extendida en la práctica —y la más simple de mantener— es aceptar el
> subpíxel **solo** mientras el zoom multijugador está activo (el movimiento entre bloques de
> pixel art ya no es discreto, pero sigue leyéndose bien a la velocidad de una partida de
> arena), y reservar el pixel-perfect estricto para la UI y el HUD, que se dibujan en la capa
> GUI y no dependen del `view_size` de la room (ver `13 · 03` §6.4). Cuantizar el zoom (arriba)
> es la alternativa cuando el estilo visual no tolera ni un frame de subpíxel, a costa de un
> zoom perceptiblemente «a saltos» en vez de continuo.

### 3.11 Cinemáticas: director de cámara, planos, barras y salto

`04 · 00` exige que toda cinemática scriptada sea saltable, y `13 · 04` documenta Sequences a
fondo pero sin pista de cámara. Lo que falta es el sistema en sí: una cola de «planos» (cada uno,
una posición y un zoom con su propia duración y *easing*), reproducida en orden, que **quita** el
control al jugador al empezar y se lo **devuelve** al terminar — o al pulsar saltar.

```gml
/// obj_camara_director — Create  (añadido)
cola_planos   = [];
plano_actual  = -1;
en_cinematica = false;
barra_alto    = 0;    // píxeles de barra negra arriba/abajo, dibujados en Draw GUI
```

```gml
/// @func cinematica_encolar(_x, _y, _duracion, _easing, _zoom)
/// @desc Añade un plano a la cola. No arranca nada por sí sola.
/// @param {Real} _x
/// @param {Real} _y
/// @param {Real} _duracion  Segundos.
/// @param {Function} _easing  De scr_math_util.gml (ease_in_out_sine por defecto).
/// @param {Real} _zoom  1 = zoom base.
function cinematica_encolar(_x, _y, _duracion, _easing = ease_in_out_sine, _zoom = 1)
{
    array_push(cola_planos, { x: _x, y: _y, duracion: _duracion, easing: _easing, zoom: _zoom });
}

/// @func cinematica_reproducir()
/// @desc Arranca la cola ya encolada: quita el control al jugador, saca las
///       barras y empieza el primer plano.
function cinematica_reproducir()
{
    if (array_length(cola_planos) == 0) { return; }

    en_cinematica = true;
    plano_actual  = -1;
    obj_jugador.input_bloqueado = true;

    // Control manual de la cámara: obligatorio antes de moverla por código
    // (ya documentado en 01 · 10 §7 y 03 · 42 §10 — si no, camera_set_view_target
    // pelea con tu tween cada frame).
    camera_set_view_target(cam, noone);

    tween_to(id, { barra_alto: 48 }, 0.4, ease_out_quad);
    cinematica_siguiente_plano();
}

/// @func cinematica_siguiente_plano()
/// @desc Uso interno: avanza al siguiente plano de la cola, o termina si ya
///       no quedan.
function cinematica_siguiente_plano()
{
    plano_actual += 1;
    if (plano_actual >= array_length(cola_planos))
    {
        cinematica_terminar();
        return;
    }

    var _plano = cola_planos[plano_actual];
    tween_to(id, { cam_x: _plano.x, cam_y: _plano.y, zoom_actual: _plano.zoom },
        _plano.duracion, _plano.easing, function() { cinematica_siguiente_plano(); });
}

/// @func cinematica_terminar()
/// @desc Devuelve el control al jugador. Se llama sola al vaciar la cola, o
///       desde el botón de saltar.
function cinematica_terminar()
{
    en_cinematica = false;
    cola_planos = [];
    obj_jugador.input_bloqueado = false;
    camera_set_view_target(cam, obj_jugador);
    tween_to(id, { barra_alto: 0 }, 0.3, ease_in_quad);
}
```

```gml
/// obj_camara_director — Step
if (en_cinematica && keyboard_check_pressed(vk_space))
{
    // Saltable: 04 · 00 lo exige para cualquier cinemática scriptada.
    cinematica_terminar();
}

// Aplica el zoom actual (compartido con §3.10) sea cual sea su origen.
camera_set_view_size(cam, round(zoom_view_w_base / zoom_actual),
                           round(zoom_view_h_base / zoom_actual));
```

```gml
/// obj_camara_director — Draw GUI
if (barra_alto > 0)
{
    draw_set_color(c_black);
    draw_rectangle(0, 0, display_get_gui_width(), barra_alto, false);
    draw_rectangle(0, display_get_gui_height() - barra_alto,
                   display_get_gui_width(), display_get_gui_height(), false);
}
```

**Barridos curvos (`camera-path`, estilo *Klonoa*).** El sistema de planos de arriba mueve la
cámara en línea recta entre dos puntos. Para un recorrido con curvas —una cinemática de
introducción que sobrevuela el nivel— usa un recurso `path` del editor y muéstralo tú mismo con
`path_get_x`/`path_get_y` en vez de dejar que `path_start()` mueva una instancia:

```gml
/// obj_camara_director — Step  (variante de cinemática con path, en vez de tween_to)
var _t = clamp(plano_t, 0, 1);         // 0..1 a lo largo del recorrido, avanzado a mano
cam_x = path_get_x(pth_cinematica_intro, _t);
cam_y = path_get_y(pth_cinematica_intro, _t);
```

---

## 4 · Checklist

- [ ] La cámara se crea con `camera_create()` en el `Create` del director y se destruye con
      `camera_destroy()` en su `Clean Up` (memory leak si falta, ver `01 · 10` §7).
- [ ] Elegiste `position-locking` + *camera-window* como base **antes** de añadir ninguna técnica
      de esta lista — todo lo demás se apila encima, no lo sustituye (§2.2).
- [ ] Si el nivel tiene pasillos y salas distintas, hay zonas de cámara (§3.5) antes que cualquier
      ajuste fino de ventana o *look-ahead*.
- [ ] La cámara vertical de un plataformas usa `platform-snapping` (§3.4), no sigue el salto en
      tiempo real — o, si el juego tiene vuelo/doble salto constante, se decidió explícitamente
      **no** usarlo (ver la advertencia de §3.4).
- [ ] Toda transición entre pantallas/salas está clasificada: fundido (`04 · 06`), paneo en la
      misma room (§3.9 Variante A) o *slide* entre rooms (§3.9 Variante B) — no una mezcla
      accidental de las tres.
- [ ] Si hay zoom dinámico (multijugador, §3.10), se decidió explícitamente si el juego acepta
      subpíxel durante el zoom o si el zoom está cuantizado — no es un olvido.
- [ ] Toda cinemática scriptada es saltable (botón probado, no solo previsto) y devuelve
      `camera_set_view_target()` al jugador al terminar.
- [ ] La posición de cámara se guarda con decimales y solo se redondea al entregarla a
      `camera_set_view_pos()` / `camera_set_view_size()` (13 · 03 §6.5) — comprobado en **cada**
      función nueva de este documento, no solo en el `cam_update()` original.
- [ ] Ninguna `surface` de transición (§3.9 Variante B) queda viva entre transiciones: se libera
      con `surface_free()` en cuanto `progreso` llega a 1.

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Corrección |
|---|---|---|
| La cámara "rebota" en cada salto | Se sigue la Y del jugador en tiempo real en vez de anclarse a la plataforma | `platform-snapping`, §3.4 |
| Un pasillo estrecho se ve con el mismo encuadre que la sala de jefe | No hay zonas de cámara: todo usa el *clamp* de la room entera | Zonas de cámara, §3.5 |
| El cruce entre dos salas da un tirón de cámara | La ventana o los límites cambian de golpe en vez de mezclarse | `zona_transicion_t` interpolando los límites, §3.5 |
| El fondo pasa de quieto a velocidad máxima en un frame al cruzar el borde | No hay franja de aceleración antes del borde (*speedup-zone*) | §3.3 |
| La cámara tiembla al acercarse a una pared, cambiando de ancla constantemente | Falta histéresis en el `dual-forward-focus`: cambia de ancla en cuanto se invierte el signo de la velocidad | Umbral de distancia acumulada, §3.8 |
| El zoom multijugador "rompe" el pixel art de golpe | Se cambia `camera_set_view_size` sin decidir la postura pixel-perfect/subpíxel | §3.10, y la decisión de `13 · 03` §1.5 |
| Un jugador se queda "atrapado" fuera de pantalla en multijugador | No hay *tether*: el zoom-to-fit solo tira de la cámara, nunca del jugador | *Tether* suave, §3.10 |
| La cinemática no se puede saltar y hay que reiniciar el juego para probarla | Se programó el recorrido de cámara sin la comprobación de salto desde el primer commit | `keyboard_check_pressed` en el `Step`, §3.11 — y probarlo de verdad, no solo "está previsto" |
| `camera_set_view_target()` pelea con el `tween_to()` de la cinemática | No se puso `camera_set_view_target(cam, noone)` antes de tomar control manual | §3.11, y la nota ya existente en `03 · 42` §10 |
| Fuga de memoria al hacer transición pantalla-a-pantalla muchas veces seguidas | La `surface` de la Variante B (§3.9) no se libera si la transición se interrumpe a medio camino | Comprobar `surface_exists()` y liberar en cualquier punto de salida, no solo en el camino feliz |

---

## Ver también

- [`01 · 10 — Rooms, capas, cámaras y viewports`](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md) — la API de cámaras, viewports, seguimiento manual y *split screen*
- [`06/scr_camera.gml`](../06%20-%20Assets%20y%20Scripts/scr_camera.gml) — el sistema base: *deadzone*, *look-ahead*, límites, *shake*, redondeo
- [`06/scr_tween.gml`](../06%20-%20Assets%20y%20Scripts/scr_tween.gml) · [`06/scr_state_machine.gml`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) — dependencias de §3.9 y §3.11
- [`04 · 15 — Game feel y juice`](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) §5.1 — *screen shake* por trauma y zoom suavizado
- [`13 · 03 — Pixel art y resolución`](./03%20-%20Pixel%20art%20y%20resolución.md) §1.5, §6.4-6.5 — pixel-perfect frente a subpíxel, redondeo de cámara
- [`04 · 06 — Metroidvania`](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md) §4.1, §5.1-§5.2 — transición con fundido, `objSpawnPoint`, estado de sala persistente
- [`04 · 01 — Plataformas 2D`](../04%20-%20Recetas%20por%20género/01%20-%20Plataformas%202D.md) §5 — `on_ground`, coyote time, el controlador que usa `platform-snapping`
- [`04 · 37 — Traversal en plataformas`](../04%20-%20Recetas%20por%20género/37%20-%20Traversal%20en%20plataformas%20-%20pendientes,%20paredes,%20escaleras%20y%20bordes.md) — estados de agachado/trepar citados en `gesture-focus`
- [`04 · 12 — Carreras y vehículos`](../04%20-%20Recetas%20por%20género/12%20-%20Carreras%20y%20vehículos.md) §5.6 · [`04 · 02 — Top-Down / Twin-Stick`](../04%20-%20Recetas%20por%20género/02%20-%20Top-Down%20_%20Twin-Stick.md) §5.7 — `projected-focus`/`target-focus` ya resueltos con código
- [`04 · 14 — Multijugador`](../04%20-%20Recetas%20por%20género/14%20-%20Multijugador.md) §8 — *split screen* como paso previo al zoom dinámico
- [`04 · 00 — Anatomía de un juego completo`](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md) §4 — por qué toda cinemática scriptada debe ser saltable
- [`13 · 04 — Animación de sprites, Sequences y Animation Curves`](./04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md) — Sequences por código, para animar UI o sprites durante una cinemática
- [`03 · 41-44 — PixelatedPope, Cámaras y Resolución 2026`](../03%20-%20Cursos%20%28YouTube%29/) — los cuatro capítulos completos sobre cámara, resolución y la distorsión de píxel al hacer zoom (§17 del capítulo 3)

---

## Fuentes

Consultada el **6 de septiembre de 2026**.

- **Itay Keren, «Scroll Back: The Theory and Practice of Cameras in Side-Scrollers»**, Game
  Developer (antes Gamasutra), 11-05-2015 — versión escrita de su charla en el Independent
  Games Summit de la GDC 2015. Abierto con `curl -sL -A "Mozilla/5.0"` (WebFetch no estaba
  disponible; WebSearch, excluido de esta tarea):
  <https://www.gamedeveloper.com/design/scroll-back-the-theory-and-practice-of-cameras-in-side-scrollers>.
  Fuente de todo el marco de §1, el glosario completo de §1.3 y los ejemplos citados por nombre
  en §3 (*Wonder Boy*, *Rastan Saga*, *Shinobi*, *Super Mario Bros./World*, *Cave Story*,
  *Insanely Twisted Shadow Planet*, *Donkey Kong Country*, *Klonoa*, *Vessel*, *Geometry Wars*,
  *Gauntlet*, *Never Alone*, *Mushroom 11*).
- **Manual oficial GameMaker LTS 2026** (espejo local en `09 - Manual oficial/`): páginas de
  `camera_create_view`, `camera_set_view_pos`, `camera_set_view_target`, `path_get_x`,
  `path_get_y`, `path_get_length`, `surface_copy`, `application_surface` y
  `display_get_gui_width` — todas verificadas contra el `GmlSpec.xml` del runtime **2026.0.0.23**
  con `python3 "_indice/buscar.py"` antes de usarse en el código de este documento.

**Verificación de la API.** Todos los símbolos del runtime usados en este documento —entre
otros, `camera_create`, `camera_destroy`, `camera_get_view_width`, `camera_get_view_height`,
`camera_set_view_pos`, `camera_set_view_size`, `camera_set_view_target`, `view_camera`,
`point_in_rectangle`, `point_distance`, `lengthdir_x`, `lengthdir_y`, `lerp`, `clamp`, `sign`,
`abs`, `min`, `max`, `infinity`, `instance_number`, `surface_create`, `surface_copy`,
`surface_free`, `surface_exists`, `application_surface`, `draw_surface`, `display_get_gui_width`,
`display_get_gui_height`, `path_get_x`, `path_get_y`, `array_push`, `array_length`,
`keyboard_check_pressed`, `vk_space`, `delta_time`, `room_goto`, `is_undefined`— se comprobaron
uno a uno con `python3 "_indice/buscar.py" <símbolo>` contra el runtime instalado antes de
escribirse. Ninguno está marcado como obsoleto. Las funciones que **no** son del runtime
—`camara_ventana_empujar`, `zona_camara_detectar`, `atractor_crear`,
`camara_atraccion_evaluar`, `camara_proyeccion`, `camara_grupo_bbox`, `zoom_cuantizar`,
`transicion_pantalla_iniciar`, `cinematica_encolar`, `cinematica_reproducir`,
`cinematica_siguiente_plano`, `cinematica_terminar`— son código propio de este documento,
definidas explícitamente en sus propios bloques (no inventan ninguna familia del runtime:
`camara_*` en español no coincide con la familia reservada `camera_*`, y `zona_*`/`atractor_*`/
`cinematica_*`/`zoom_*`/`transicion_*` no son prefijos de ninguna familia nativa). Las
funciones `cam_set_bounds`, `cam_get_data`, `tween_to`, `tween_update`, `ease_linear`,
`ease_in_out_sine`, `ease_out_quad`, `ease_in_quad` ya existen y están verificadas en
`06/scr_camera.gml`, `06/scr_tween.gml` y `06/scr_math_util.gml`: no se repiten aquí, se dan
por dependencia.
