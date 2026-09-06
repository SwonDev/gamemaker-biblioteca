# 04 · Animación de sprites, Sequences y Animation Curves

> Cómo se anima un juego 2D en GameMaker: los principios del oficio traducidos a sprites de pocos
> fotogramas, la animación por `image_index`, la animación procedural, el asset **Animation Curve**
> y el asset **Sequence**.
> **No repite** el catálogo de `draw_sprite*` ni la tabla de variables `image_*` —eso está en
> [08 · 01](../08%20-%20Referencia%20GML%20completa/01%20-%20Dibujo%20b%C3%A1sico%20y%20sprites.md)—
> ni el catálogo de curvas de easing ni el screen shake, que viven en
> [04 · 15](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md).
> La animación esquelética tiene documento propio:
> [08 · 22](../08%20-%20Referencia%20GML%20completa/22%20-%20Animaci%C3%B3n%20esqueletal%20%28Spine%29.md).

```
                            ¿QUÉ ESTOY ANIMANDO?
        ┌────────────────────────────┼────────────────────────────┐
  Dibujo distinto            Misma imagen que se           Composición de
  en cada fotograma          mueve / escala / tiñe         varias piezas
        │                            │                            │
  FOTOGRAMAS  (§3)           CÓDIGO PROCEDURAL (§4)         SEQUENCE (§6)
  image_index                 lerp · dsin · tween        layer_sequence_*
  image_speed                        │                            │
  Animation End                      └─ forma de la ───────┐      │
  Broadcast Messages                    interpolación      ▼      ▼
        │                                        ANIMATION CURVE (asset, §5)
        └─ ¿muchas partes articuladas? → Spine   animcurve_channel_evaluate
```

---

## 1 · Los principios, traducidos a un sprite de juego

Los **doce principios de la animación** son de Frank Thomas y Ollie Johnston (*The Illusion of
Life: Disney Animation*, 1981). Se escribieron para dibujo animado a 24 fps con presupuesto de
estudio. Un sprite de juego tiene cuatro fotogramas y medio y, además, una obligación que una
película no tiene: **el jugador debe poder leer el estado del personaje y reaccionar**. Eso
reordena las prioridades.

### 1.1 Cuáles importan de verdad, y en qué orden

| Principio | Prioridad | Por qué |
|---|---|---|
| **Timing** (cuántos fotogramas dura) | crítica | Es el principio que se *siente* con el mando. Un ataque de 8 fotogramas de arranque y otro de 3 son dos juegos distintos. |
| **Anticipación** | crítica | Es el **telegrafiado**: sin ella el jugador no puede esquivar y el juego se percibe injusto. Es diseño, no adorno. |
| **Exageración** | crítica | A 32×32 px un movimiento «realista» no se lee. Si dudas, exagera. |
| **Puesta en escena** (*staging*) | alta | En 2D es **silueta**: la pose de ataque no puede confundirse con la de reposo ni en negro sobre blanco. |
| **Squash & stretch** | alta | Da peso e impacto y se hace **sin dibujar un fotograma**, escalando. Cubierto en [04 · 15 §4.3 y §5.3](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md). |
| **Slow in / slow out** | alta | Es literalmente el *easing*: se resuelve con una curva, no con fotogramas. |
| **Follow-through y overlapping** | media | Capa, pelo y arma siguen moviéndose cuando el cuerpo para. Se hace con retardo en código (§4.4). |
| **Arcos** | media | Un salto que sube recto parece un ascensor. Se arregla en la física, no en el sprite. |
| **Acción secundaria** | media | Parpadeo, respiración, punta de la capa: lo que impide que un personaje parado parezca muerto. |
| **Atractivo** (*appeal*) | media | Legibilidad más personalidad. Se decide al diseñar el personaje. |
| **Dibujo sólido** | baja | Pensado para volumen dibujado a mano; en pixel art se traduce en coherencia de perspectiva y paleta. |
| **Straight ahead / pose a pose** | baja | Es un **método de trabajo**, no una propiedad del resultado. En sprites cortos trabajas pose a pose. |

> ⚠️ El orden de prioridad es criterio propio de esta biblioteca. Los doce nombres y sus
> definiciones sí son de Thomas & Johnston.

### 1.2 Timing no es spacing

Richard Williams (*The Animator's Survival Kit*, 2001) los separa con un ejemplo que se entiende
en diez segundos: mueve una moneda por la mesa en 24 fotogramas con espaciado regular; muévela
otra vez **en los mismos 24 fotogramas**, pero saliendo despacio de la posición 1 y entrando
despacio en la 25. Mismo timing, spacing distinto, sensación completamente distinta.

> «Podrías decir que la animación es el arte del *timing*. […] Para un animador, es sólo la mitad
> de la batalla. Necesitamos también el *spacing*.»

De ahí la regla operativa de este documento: **el timing se pone con fotogramas o con duraciones;
el spacing se pone con una Animation Curve o con una función de easing.** Confundirlos es el
error más común.

### 1.3 Un salto de 4 fotogramas con 2 de anticipación

Seis subimágenes en `spr_jugador_salto`:

| Sub. | Pose | Duración a 60 fps | Principio |
|---|---|---|---|
| 0 | Flexión ligera de rodillas | 3 frames | Anticipación |
| 1 | Flexión máxima, hombros bajos | 4 frames | Anticipación (el fotograma que se «lee») |
| 2 | Despegue, cuerpo estirado | 2 frames | Exageración + stretch |
| 3 | Subida, brazos arriba | mientras `vsp < -1` | Timing dinámico |
| 4 | Ápice, cuerpo recogido | mientras `abs(vsp) <= 1` | La pose que menos se ve y más importa |
| 5 | Caída, piernas adelantadas | mientras `vsp > 1` | Anticipa el aterrizaje |

Las subimágenes 0-2 se **reproducen** una vez a velocidad fija; las 3-5 no se reproducen: se
**seleccionan** según la velocidad vertical (la «cascada de prioridades» de
[03 · 11 §9](../03%20-%20Cursos%20%28YouTube%29/11%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%2011%20-%20Animaciones%20y%20Tile%20Sets.md)).
Siete fotogramas de anticipación son 117 ms: bastante para verlo, poco para sentirlo pesado.

### 1.4 Un ataque con *smear*

Un *smear frame* es un fotograma deformado que representa el recorrido entero del arma. Es
exageración pura y sólo funciona si se ve **un único fotograma de juego**:

```
sub 0  anticipación (arma atrás)        4 frames  ← se lee
sub 1  smear (borrón del arco)          1 frame   ← no se lee, se siente
sub 2  impacto (arma abajo, extendida)  3 frames  ← el hitbox está aquí
sub 3  recuperación                     6 frames
```

Con dos fotogramas ya se percibe como un dibujo feo; con uno, el cerebro lo integra como
velocidad. Es el mismo truco del *motion blur* de Pedro Medeiros (Saint11).

---

## 2 · Las cuatro herramientas, y cuál usar

| Herramienta | Anima… | Úsala para… | Evítala para… |
|---|---|---|---|
| **Fotogramas** (`image_index`, `image_speed`) | subimágenes dibujadas | todo lo que el jugador controla: correr, saltar, atacar | mover suavemente algo que no cambia de dibujo |
| **Código procedural** (`lerp`, `dsin`, tween) | posición, escala, ángulo, color, alpha | *juice*, reacciones, UI, oscilaciones, follow-through | personajes con dibujos distintos |
| **Animation Curve** (asset, `animcurve_*`) | uno o varios valores 0→1 | dar **forma** a una interpolación que un diseñador debe poder retocar | easing genérico de código (§5.6) |
| **Sequence** (asset, `layer_sequence_*`) | una línea de tiempo con pistas de sprite, instancia, audio, texto, partículas y curvas | cinemáticas, ataques compuestos, intros, UI animada | **cualquier cosa que dependa del input** (§6.7) |

> 💡 Regla rápida: **si el jugador puede interrumpirlo, no es una Sequence.**

---

## 3 · Animación por fotogramas

### 3.1 Las variables

`sprite_index` (qué sprite) · `image_index` (qué subimagen, base 0) · `image_number` (cuántas hay,
**solo lectura**) · `image_speed` (**multiplicador**, no fps). La tabla completa de las trece
variables `image_*` está en
[08 · 01](../08%20-%20Referencia%20GML%20completa/01%20-%20Dibujo%20b%C3%A1sico%20y%20sprites.md).

Lo único que hay que grabarse: **`image_speed = 1` no significa «un fotograma por paso»**,
significa «la velocidad que le puse al sprite en el IDE».

### 3.2 «Frames per second» frente a «Frames per game frame»

El desplegable **Frame Speed** del editor de sprites tiene dos modos, y la diferencia es enorme:

| Modo | Constante | `sprite_get_speed()` devuelve | Con valor 10, a 60 fps |
|---|---|---|---|
| **Frames per second** | `spritespeed_framespersecond` | subimágenes por **segundo** | 10 subimágenes/s → una cada 6 pasos |
| **Frames per game frame** | `spritespeed_framespergameframe` | subimágenes por **paso de juego** | 10 subimágenes por paso: se salta la animación entera |

El manual es explícito: en modo *per game frame* los valores «se suelen fijar en 1 o menos (por
ejemplo, una velocidad de 0,5 mostrará un nuevo cuadro cada dos pasos de juego)».

**Modo recomendado: *Frames per second*.** Es el único que sobrevive a un cambio de velocidad del
juego y el único en el que el número significa lo que un animador espera.

```gml
/// scr_animacion · velocidad_real_animacion(_spr, _mult)
/// @desc Subimágenes por segundo reales de un sprite con un multiplicador dado.
/// @param {Asset.GMSprite} _spr   Sprite a medir.
/// @param {Real} _mult            El image_speed aplicado (1 = sin cambio).
/// @return {Real}
function velocidad_real_animacion(_spr, _mult = 1)
{
    var _base = sprite_get_speed(_spr) * _mult;

    // En modo «por paso de juego» la cifra hay que pasarla a segundos.
    if (sprite_get_speed_type(_spr) == spritespeed_framespergameframe)
    {
        return _base * game_get_speed(gamespeed_fps);
    }

    return _base;
}

/// scr_animacion · duracion_animacion(_spr, _mult)
/// @desc Segundos que tarda el sprite en recorrer todas sus subimágenes una vez.
/// @return {Real}  Duración en segundos, o infinity si está parado.
function duracion_animacion(_spr, _mult = 1)
{
    var _fps = velocidad_real_animacion(_spr, _mult);
    return (_fps <= 0) ? infinity : sprite_get_number(_spr) / _fps;
}
```

> ⚠️ `sprite_set_speed(index, speed, type)` cambia la velocidad **del recurso**: afecta a todas
> las instancias presentes y futuras. Para una sola instancia, `image_speed`.

### 3.3 Detectar el final de la animación

**a) El evento *Other → Animation End***, que se dispara «justo al final de la animación, cuando el
índice de la sub-imagen muestra que se ha alcanzado el último fotograma». Es la vía limpia:

```gml
/// obj_explosion · Evento Other → Animation End
instance_destroy();
```

**b) La comprobación manual**, la del propio manual, cuando el objeto usa varias animaciones y
sólo te importa el final de una:

```gml
/// obj_jugador · Evento Step (fragmento)
if (image_speed > 0 && image_index >= image_number - 1)
{
    fsm.set("quieto");
}
```

> 🔺 **`image_index` es un número real, no entero.** Con `image_speed` fraccionario vale 3.7 antes
> de valer 4. Por eso se compara con `>=` y **nunca** con `==`, que se salta el final la mitad de
> las veces.

### 3.4 Reproducir una vez y congelar

```gml
/// obj_puerta_abriendose · Evento Other → Animation End
image_speed = 0;                  // Detiene el ciclo.
image_index = image_number - 1;   // Fija el último fotograma exacto.
```

Detener sin fijar el índice deja `image_index` en un valor fraccionario que se dibuja bien pero
envenena cualquier comparación posterior. Para congelar en el primero, `image_speed = 0;
image_index = 0;` en el Create.

### 3.5 Cambiar de sprite sin reiniciar el fotograma

Asignar `sprite_index` **no reinicia `image_index`**. Eso es justo lo que quieres al cambiar entre
sprites que comparten cadencia (correr normal ↔ correr con arma): la fase se conserva y no hay
salto visual. Y es justo lo que no quieres al entrar en una animación de un solo uso. El error
clásico es resolverlo así:

```gml
// ❌ MAL: reinicia 60 veces por segundo, así que nunca pasa del fotograma 0.
sprite_index = spr_jugador_correr;
image_index  = 0;
```

El patrón correcto compara antes de asignar:

```gml
/// scr_animacion · cambiar_sprite(_spr, _reiniciar, _velocidad)
/// @desc Cambia el sprite de la instancia actual sólo si es distinto del que ya tiene.
/// @param {Asset.GMSprite} _spr   Sprite destino.
/// @param {Bool} _reiniciar       true = empezar en la subimagen 0.
/// @param {Real} _velocidad       Multiplicador (image_speed).
/// @return {Bool}                 true si hubo cambio.
function cambiar_sprite(_spr, _reiniciar = false, _velocidad = 1)
{
    image_speed = _velocidad;
    if (sprite_index == _spr) return false;   // Ya estaba: no se toca image_index.

    sprite_index = _spr;
    // Conserva la fase, pero sin salirse del rango del sprite nuevo.
    image_index = _reiniciar ? 0 : (image_index mod sprite_get_number(_spr));

    return true;
}
```

> ⚠️ El `mod` es defensivo: el manual documenta que el fotograma visible se conserva al cambiar de
> sprite, pero **no** especifica qué ocurre si el sprite nuevo tiene menos subimágenes que el
> `image_index` actual. Recortarlo cuesta una operación y elimina la duda.

### 3.6 Broadcast Messages del sprite

El editor de sprites tiene un botón **Broadcast Messages** que planta un *string* en un fotograma
concreto. Al llegar la reproducción a ese fotograma, el mensaje se emite a **todas** las
instancias que tengan el evento *Other → Broadcast Message*.

La recepción va por `event_data`, un DS Map global que **sólo tiene datos dentro del evento que lo
disparó** (fuera vale `-1`):

| Clave | Tipo | Contenido |
|---|---|---|
| `"event_type"` | String | `"sprite event"` o `"sequence event"` |
| `"message"` | String | El texto escrito en el editor |
| `"element_id"` | Layer Element ID | El elemento emisor (útil con `layer_get_element_type()`) |

```gml
/// obj_jugador · Evento Other → Broadcast Message
if (event_data[? "event_type"] != "sprite event") exit;

switch (event_data[? "message"])
{
    case "paso_izq":
    case "paso_der":     audio_play_sound(snd_paso, 5, false);  break;
    case "golpe_activo": golpe_habilitado = true;               break;
    case "golpe_fin":    golpe_habilitado = false;              break;
}
```

> 🔺 **La trampa gorda:** el manual advierte de que «si se establece el `image_index` de una
> instancia directamente en un fotograma, **no** se activará ningún mensaje de difusión que pueda
> estar presente en ese fotograma». Si tu animación avanza a mano (`image_index = 3`) en vez de
> con `image_speed`, los broadcasts **no suenan**. Y si en el mismo paso llegan varios mensajes,
> el evento se ejecuta **una vez por cada uno**.

### 3.7 *Frame data*: ligar el daño al fotograma

El vocabulario viene de los juegos de lucha y está estandarizado en la wiki Dustloop. Se mide en
**fotogramas**, no en segundos:

| Término | Definición (Dustloop) | En GameMaker |
|---|---|---|
| **Startup** | Desde que se inicia el golpe hasta el primer fotograma que golpea, **incluido** | Los fotogramas de anticipación |
| **Active** | Los fotogramas durante los cuales el golpe puede impactar | Cuando existe el *hitbox* |
| **Recovery** | Todos los posteriores a los activos, hasta poder volver a actuar | La recuperación |

A 60 fps un fotograma son 16,67 ms. «Startup 10F» significa que el ataque **no hace nada durante 9
fotogramas y golpea en el décimo**.

Los broadcast messages (§3.6) son la opción del artista, pero se rompen si tocas `image_index` a
mano. La opción robusta es una **tabla de datos** al lado del sprite: es *greppable*, se testea sin
abrir el IDE y no depende de que nadie recuerde mover una marca al reexportar.

```gml
/// scr_ataques · tabla de frame data (crear una vez, p. ej. desde un objeto controlador)
global.frame_data =
{
    ataque_ligero : { sprite : spr_jugador_ataque_1, activo_ini : 2, activo_fin : 3, dano : 1 },
    ataque_fuerte : { sprite : spr_jugador_ataque_2, activo_ini : 5, activo_fin : 7, dano : 3 },
};

/// scr_ataques · ventana_de_golpe(_nombre, _indice)
/// @desc ¿Cae la subimagen actual dentro de la ventana activa del ataque?
/// @param {String} _nombre   Clave dentro de global.frame_data.
/// @param {Real}   _indice   La subimagen actual (image_index).
/// @return {Bool}
function ventana_de_golpe(_nombre, _indice)
{
    if (!variable_struct_exists(global.frame_data, _nombre)) return false;

    var _d = global.frame_data[$ _nombre];
    var _f = floor(_indice);   // image_index es real: lo bajamos a fotograma entero.

    return (_f >= _d.activo_ini && _f <= _d.activo_fin);
}
```

```gml
/// obj_jugador · Evento Step (dentro del estado "atacando")
if (ventana_de_golpe(ataque_actual, image_index))
{
    var _d = global.frame_data[$ ataque_actual];
    var _v = collision_rectangle(bbox_left, bbox_top, bbox_right, bbox_bottom,
                                 obj_enemigo, false, true);

    // Un golpe por ventana activa, no uno por paso: ya_golpeados se vacía al ENTRAR al estado.
    if (_v != noone && !array_contains(ya_golpeados, _v))
    {
        array_push(ya_golpeados, _v);
        with (_v) recibir_dano(_d.dano);
    }
}
```

### 3.8 Del estado al sprite

La máquina de estados decide qué pasa; la capa de animación decide qué se ve. Mantenlas separadas:
no metas `sprite_index = ...` dentro de la lógica de movimiento. Usa la FSM de
[06 · `scr_state_machine.gml`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml)
(`fsm_bind()` y luego `.set()`, `.update()`, `.get()`, `.get_time()`) y una **tabla estado →
animación** al lado:

```gml
/// obj_jugador · Evento Create (fragmento)
animaciones =
{
    quieto   : { sprite : spr_jugador_quieto,   vel : 1,   bucle : true  },
    correr   : { sprite : spr_jugador_correr,   vel : 1,   bucle : true  },
    salto    : { sprite : spr_jugador_salto,    vel : 1,   bucle : false },
    atacando : { sprite : spr_jugador_ataque_1, vel : 1.2, bucle : false },
};
```

```gml
/// scr_animacion · aplicar_animacion()
/// @desc Sincroniza el sprite visible con el estado actual de la FSM. Llamar al final del Step.
/// @return {Undefined}
function aplicar_animacion()
{
    var _nombre = fsm.get();
    if (!variable_struct_exists(animaciones, _nombre)) return;

    var _a = animaciones[$ _nombre];

    // Reinicia sólo si el estado acaba de empezar: así los bucles conservan su fase.
    cambiar_sprite(_a.sprite, fsm.get_time() <= 1, _a.vel);

    if (!_a.bucle && image_index >= image_number - 1)
    {
        image_speed = 0;
        image_index = image_number - 1;
    }

    if (hsp != 0) image_xscale = sign(hsp);   // Voltea hacia donde se mueve.
}
```

Añadir una animación pasa a ser añadir una fila a `animaciones`, no tocar la lógica. La
alternativa —la cascada de `if`/`else if` en orden de prioridad— está explicada con su bug del
parpadeo en el ápice del salto en
[03 · 11 §9 y §10](../03%20-%20Cursos%20%28YouTube%29/11%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%2011%20-%20Animaciones%20y%20Tile%20Sets.md);
es más rápida de escribir y peor de mantener a partir de seis estados.

### 3.9 Origen y máscara de colisión

El **origen** es el punto del sprite que se coloca en la `x`/`y` de la instancia. Si el fotograma
de correr tiene el origen en los pies y el de saltar en el centro, **el personaje da un salto de
píxeles al cambiar de sprite** aunque no se haya movido. Es el error que más cuesta diagnosticar
porque parece un bug de física.

1. **Todos los sprites de un personaje comparten origen.** En plataformas, *Bottom Centre*: el
   suelo es lo que no puede temblar.
2. Si un fotograma necesita más espacio (un *smear* que sobresale), **no lo recortes**: amplía el
   lienzo de todos y deja el origen donde estaba. El manual permite orígenes fuera del sprite, con
   valores negativos o mayores que el ancho.
3. Comprueba el origen fotograma a fotograma antes de dar el sprite por bueno.

Sobre resolución y rejilla de píxeles, ver
[13 · 03 — Pixel art y resolución](./03%20-%20Pixel%20art%20y%20resoluci%C3%B3n.md).

**Máscara.** Por defecto es «Same as Sprite»: cambia con cada sprite y con cada fotograma. Para un
personaje eso casi siempre es un error, porque la caja crece y mengua sola y las colisiones se
perciben injustas. `mask_index = spr_jugador_mascara;` en el Create y listo.

| Situación | Máscara |
|---|---|
| Jugador, enemigo, plataforma | **Fija** (`mask_index` a un sprite dedicado) |
| Proyectil que rota | Fija, y a menudo más pequeña que el dibujo |
| *Hitbox* de ataque | Objeto aparte que se crea y destruye, o `collision_rectangle` (§3.7) |
| Ítem con sprite irregular que sí debe variar | Por fotograma (dejar «Same as Sprite») |

> 🔺 `image_xscale` e `image_yscale` **escalan también la máscara**: un squash & stretch sobre el
> jugador altera sus colisiones. Por eso el squash se aplica en el Draw con `draw_sprite_ext()`,
> que es lo que hace [04 · 15 §5.3](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md).

---

## 4 · Animación procedural en código

> ⚠️ **Deuda técnica del repositorio, léela antes de escribir nada:** hay **dos** sistemas de tween
> con una función que se llama igual. [`06 · scr_tween.gml`](../06%20-%20Assets%20y%20Scripts/scr_tween.gml)
> define `tween_to(_objetivo, _props, _duracion, _easing, _on_complete, _retraso)` con duración en
> **segundos** y un struct de propiedades, y necesita `tween_update()` una vez por paso.
> [04 · 15 §5.2](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md) define
> otro `tween_to(_target, _prop, _hasta, _duracion, _ease, _on_end)` con duración en **fotogramas**
> y el objeto `objTweenManager`. **No crees un tercero.** Este documento usa el de `scr_tween.gml`,
> que es el sistema de `06 - Assets y Scripts`.

### 4.1 Qué easing pide cada principio

El catálogo de curvas por sensación está en
[04 · 15 §4.4](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md) y las
implementaciones en `scr_math_util.gml`. Aquí va el mapeo que falta: de principio de animación a
curva.

| Principio | Curva | Por qué |
|---|---|---|
| **Slow out** (salir despacio) | `ease_in_quad` | El movimiento arranca lento: es la definición literal. |
| **Slow in** (entrar despacio) | `ease_out_quad` | Frena al llegar. La curva por defecto de casi toda la UI. |
| **Anticipación** | `ease_in_cubic` sobre un desplazamiento **contrario** | Se echa atrás despacio y sale de golpe. |
| **Follow-through / overshoot** | `ease_out_back` | Se pasa del destino y vuelve: el rebote de una capa. |
| **Elasticidad / impacto** | `ease_out_elastic` | Oscila varias veces. Con cuentagotas: cansa. |
| **Peso / caída** | `ease_in_quad` y luego `ease_out_bounce` | Acelera al caer, rebota al tocar. |
| **Movimiento mecánico** | `ease_linear` | Un mecanismo **no** debe tener easing: delata que es una máquina. |

### 4.2 `lerp` con `delta_time`, sin depender de los fps

El seguimiento suave más escrito del mundo está mal:

```gml
// ❌ MAL: a 30 fps se mueve la mitad de rápido que a 60. No es determinista.
x = lerp(x, objetivo_x, 0.1);
```

`lerp(a, b, amt)` no sabe nada del tiempo. La corrección es expresar el suavizado como **qué
fracción de la distancia queda tras un segundo**, y elevarla al tiempo transcurrido:

```gml
/// scr_animacion · suavizar(_actual, _objetivo, _restante_por_segundo)
/// @desc Interpolación exponencial independiente de la tasa de fotogramas.
/// @param {Real} _actual                Valor actual.
/// @param {Real} _objetivo              Valor destino.
/// @param {Real} _restante_por_segundo  Fracción que queda tras 1 s (0.001 rápido, 0.5 lento).
/// @return {Real}
function suavizar(_actual, _objetivo, _restante_por_segundo = 0.001)
{
    var _dt = delta_time / 1000000;                    // delta_time viene en microsegundos.
    var _k  = 1 - power(_restante_por_segundo, _dt);

    return lerp(_actual, _objetivo, clamp(_k, 0, 1));
}
```

```gml
/// obj_camara · Evento Step
x = suavizar(x, obj_jugador.x, 0.002);
y = suavizar(y, obj_jugador.y, 0.002);
```

El resultado es idéntico a 30, 60 o 144 fps.

> 🔺 `delta_time` mide **tiempo real**: no se detiene con un *hit stop*. Si usas el sistema de
> escala de tiempo de [04 · 15 §5.0](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md),
> multiplica `_dt` por `time_delta()` —su API pública, que vale 0 mientras el juego está
> congelado— o el mundo se quedará quieto mientras la cámara sigue moviéndose.

### 4.3 Oscilación, *bob* y temblor

Dos piezas que dan vida sin dibujar un fotograma. Ambas comparten un principio: **acumular una
fase propia**, nunca leer `current_time`, que ni se pausa ni respeta la escala de tiempo.

```gml
/// obj_moneda · Evento Create
fase = random(360);   // Desfase inicial: sin él todas las monedas suben a la vez.
altura_bob = 4;       // Píxeles de recorrido.
ciclos_bob = 1.2;     // Ciclos completos por segundo.
y_base = y;
```

```gml
/// obj_moneda · Evento Step
fase = (fase + ciclos_bob * 360 * (delta_time / 1000000) * time_delta()) mod 360;
y = y_base + dsin(fase) * altura_bob;
```

`dsin()` trabaja en grados: la fase se lee directamente como «vuelta completa = 360» y no hay que
mezclar `pi` en el código de gameplay.

**Temblor de un elemento suelto**, distinto del screen shake de
[04 · 15 §5.1](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md), que mueve
la cámara entera:

```gml
/// obj_cofre · Evento Create
temblor_fuerza = 0;  temblor_tiempo = 0;  temblor_total = 1;
temblor_x = 0;       temblor_y = 0;

/// Arranca un temblor local. _intensidad en píxeles, _duracion en segundos.
temblor = function(_intensidad, _duracion)
{
    temblor_fuerza = max(temblor_fuerza, _intensidad);  // Un golpe flojo no apaga uno fuerte.
    temblor_tiempo = max(temblor_tiempo, _duracion);
    temblor_total  = temblor_tiempo;
};
```

```gml
/// obj_cofre · Evento Step
if (temblor_tiempo > 0)
{
    // A propósito SIN time_delta(): 04 · 15 §5.0 recomienda que el temblor y las partículas
    // sigan vivos durante el hit stop. Es lo que hace que la congelación se lea como impacto.
    temblor_tiempo -= delta_time / 1000000;

    // La fuerza decae: un temblor que no decae parece un error gráfico.
    var _f = temblor_fuerza * clamp(temblor_tiempo / temblor_total, 0, 1);
    temblor_x = random_range(-_f, _f);
    temblor_y = random_range(-_f, _f);
}
else
{
    temblor_fuerza = 0;  temblor_x = 0;  temblor_y = 0;
}
```

```gml
/// obj_cofre · Evento Draw
draw_sprite_ext(sprite_index, image_index, x + temblor_x, y + temblor_y,
                image_xscale, image_yscale, image_angle, image_blend, image_alpha);
```

Dibujar el desplazamiento en el Draw en vez de mover `x`/`y` mantiene la posición lógica intacta:
el cofre tiembla pero sus colisiones no se mueven.

### 4.4 Follow-through: una cadena que sigue al cuerpo

Pelo, capa, cola, cadena de una maza: *overlapping action* resuelto con matemáticas en lugar de
con dibujos. Cada eslabón persigue al anterior con retardo y una distancia máxima.

```gml
/// obj_capa · Evento Create
eslabones = 6;  separacion = 3;  tension = 0.35;   // 0 = flácida, 1 = rígida.
puntos = array_create(eslabones);
for (var i = 0; i < eslabones; i++) puntos[i] = { px : x, py : y };
```

```gml
/// obj_capa · Evento Step
var _dt = (delta_time / 1000000) * time_delta();
var _k  = 1 - power(1 - tension, _dt * 60);   // Independiente de los fps (§4.2).

puntos[0].px = obj_jugador.x;                 // El eslabón 0 va pegado al hombro.
puntos[0].py = obj_jugador.y - 10;

for (var i = 1; i < eslabones; i++)
{
    var _ant = puntos[i - 1], _act = puntos[i];

    _act.px = lerp(_act.px, _ant.px, _k);
    _act.py = lerp(_act.py, _ant.py + separacion, _k);   // +separacion = gravedad barata.

    // Restricción de distancia: sin ella la cadena se estira sin límite.
    if (point_distance(_ant.px, _ant.py, _act.px, _act.py) > separacion)
    {
        var _dir = point_direction(_ant.px, _ant.py, _act.px, _act.py);
        _act.px = _ant.px + lengthdir_x(separacion, _dir);
        _act.py = _ant.py + lengthdir_y(separacion, _dir);
    }
}
```

En el Draw, un `draw_sprite(spr_capa_eslabon, i, puntos[i].px, puntos[i].py)` por eslabón. Bajar
`tension` da terciopelo pesado; subirla, una cinta ligera. Para la versión con física real
—Verlet, restricciones iterativas, fluidos— ver
[13 · 08 — Físicas a mano y fluidos](./08%20-%20F%C3%ADsicas%20a%20mano%20y%20fluidos.md).

---

## 5 · Animation Curves (asset)

### 5.1 Qué son

Una **Animation Curve** es un asset que guarda **una o varias curvas** que describen cómo cambia un
valor a lo largo del tiempo. Dos propiedades que hay que interiorizar:

- **El eje horizontal está siempre normalizado de 0 a 1.** No son segundos ni fotogramas: es
  «porcentaje del recorrido». La duración la pones tú multiplicando.
- **El eje vertical es libre.** El editor lo muestra de −1 a 1 por defecto, pero el manual dice
  que ese rango es **puramente visual** y «no sujeta los valores del canal».

Se editan arrastrando puntos en el
[Animation Curve Editor](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Animation_Curves.md)
del IDE. Ese es su valor real: **un diseñador puede afinar la sensación sin abrir el código**.

### 5.2 Canales y tipos de interpolación

Una curva se compone de **canales**. Cada canal es una curva independiente con su nombre, su color
y sus puntos, así que una sola curva describe una posición (canales `x`, `y`) o un degradado de
color (canales `a`, `r`, `g`, `b`).

Los tres tipos de interpolación existen y se llaman así (verificados contra el runtime):

| Constante | Nombre en el IDE | Qué hace |
|---|---|---|
| `animcurvetype_linear` | **Linear** | Recta entre puntos. |
| `animcurvetype_catmullrom` | **Smooth** | Interpolación **catmull-rom**: pasa por todos los puntos suavizando. |
| `animcurvetype_bezier` | **Bezier** | Bézier con tiradores por punto. **La única con la que funcionan los presets.** |

En el canal, `iterations` (16 por defecto) es cuántos puntos internos se generan por segmento en
modo catmull-rom; en modo lineal la variable existe pero no hace nada.

La **Animation Curve Library** trae presets con nombre (Cubic, Quart, Expo, Elastic…), tres modos
de suavizado y dos **modos de aplicación**: *Overwrite* (borra los puntos intermedios) y *Between*
(aplica el preset entre cada par de puntos y añade los que hagan falta). Un canal plano no cambia
al aplicarle un preset: necesita pendiente.

> ⚠️ **Contradicción entre dos fuentes oficiales.** El manual (página *Animation Curve Library*)
> dice: «*Ease In: la curva empieza con una aceleración más rápida y luego decelera*». El blog
> oficial, del mismo redactor técnico (Matharoo, 8-4-2021), dice lo contrario: «*Ease In empieza
> con una curva lenta que acelera cerca del final; Ease Out es lo opuesto*». La segunda es la
> convención estándar del oficio (CSS, Penner). **Compruébalo visualmente en el IDE** aplicando
> *Expo* a un canal con pendiente: se ve en un vistazo.

### 5.3 Evaluarlas desde código

```gml
animcurve_get(curve_id)                                     // → Struct.AnimCurve
animcurve_get_channel(curve_struct_or_id, nombre_o_indice)  // → Struct.AnimCurveChannel
animcurve_get_channel_index(curve_struct_or_id, nombre)     // → Real
animcurve_channel_evaluate(channel_struct, posx)            // → Real (posx de 0 a 1)
```

**La regla: cachea el struct del canal en el Create, no lo pidas cada paso.**

```gml
/// obj_boton · Evento Create
canal_escala = animcurve_get_channel(ac_boton_pulsado, "escala");
t = 0;              // Posición normalizada 0 → 1.
duracion = 0.35;    // Segundos que dura la animación completa.
animando = false;
escala_actual = 1;
```

```gml
/// obj_boton · Evento Step
if (!animando) exit;

t += (delta_time / 1000000) / duracion;
if (t >= 1) { t = 1; animando = false; }

// animcurve_channel_evaluate exige posx entre 0 y 1: el clamp no es opcional.
escala_actual = animcurve_channel_evaluate(canal_escala, clamp(t, 0, 1));
```

```gml
/// obj_boton · Evento Draw
draw_sprite_ext(sprite_index, image_index, x, y,
                escala_actual, escala_actual, 0, c_white, image_alpha);
```

> 🔺 El ejemplo del propio manual usa
> `animcurve_channel_evaluate(_channel, sin(current_time/1000))`. `sin()` devuelve valores
> **negativos** y el manual exige `posx` entre 0 y 1: ese ejemplo enseña la sintaxis, no el uso
> correcto. **No lo copies sin un `clamp`.**

### 5.4 Cuatro casos que rinden

| Caso | Canales | Cómo |
|---|---|---|
| **Curva de salto** | 1 (`altura`) | `t` = fracción del salto, multiplicada por la altura máxima. Permite un ápice colgado sin tocar la gravedad. |
| **Curva de fade** | 1 (`alpha`) | `image_alpha = animcurve_channel_evaluate(canal, t)`. Un fade con curva no se siente igual que uno lineal. |
| **Curva de daño** | 1 (`multiplicador`) | Eje X = fracción de la ventana activa; eje Y = multiplicador. Golpes con «punto dulce» sin números mágicos. |
| **Easing propio dibujado en el IDE** | 1 | Cuando ninguna curva estándar da la sensación buscada: el diseñador la dibuja, el programador no toca nada. |

La curva de daño es la que menos se ve por ahí y más rinde:

```gml
/// scr_ataques · dano_por_fotograma(_nombre, _indice)
/// @desc Daño del ataque en la subimagen actual, modulado por su curva.
/// @return {Real}  Daño ya multiplicado, 0 fuera de la ventana activa.
function dano_por_fotograma(_nombre, _indice)
{
    if (!ventana_de_golpe(_nombre, _indice)) return 0;

    var _d = global.frame_data[$ _nombre];
    var _ancho = _d.activo_fin - _d.activo_ini;
    var _t = (_ancho <= 0) ? 0 : (floor(_indice) - _d.activo_ini) / _ancho;

    // Aquí se busca por claridad; en un bucle caliente cachea el canal una vez (§5.3).
    var _canal = animcurve_get_channel(ac_curva_dano, "multiplicador");

    return _d.dano * animcurve_channel_evaluate(_canal, clamp(_t, 0, 1));
}
```

### 5.5 Crear curvas por código

`animcurve_create()` devuelve un struct vacío al que se le asigna un array de canales
(`animcurve_channel_new()`), y a cada canal un array de puntos (`animcurve_point_new()`, con `posx`
de 0 a 1 y `value`). Útil para curvas generadas —dificultad procedural, curvas leídas de un archivo
de configuración—, no para las de siempre.

```gml
/// scr_animacion · curva_rebote_nueva(_altura, _rebotes)
/// @desc Construye una AnimCurve en memoria con forma de rebote decreciente.
/// @return {Struct.AnimCurve}  Hay que destruirla con animcurve_destroy().
function curva_rebote_nueva(_altura = 1, _rebotes = 3)
{
    _rebotes = max(1, _rebotes);

    var _curva = animcurve_create();
    _curva.name = "rebote_generado";

    var _canal = animcurve_channel_new();
    _canal.name = "altura";
    _canal.type = animcurvetype_catmullrom;
    _canal.iterations = 8;

    var _total = 1 + _rebotes * 2;            // Un punto inicial + pico y suelo por rebote.
    var _puntos = array_create(_total);

    _puntos[0] = animcurve_point_new();
    _puntos[0].posx = 0;  _puntos[0].value = 0;

    for (var i = 0; i < _rebotes; i++)
    {
        var _pico = animcurve_point_new();
        _pico.posx  = (i * 2 + 1) / _total;
        _pico.value = _altura * power(0.5, i);   // Cada rebote llega a la mitad.
        _puntos[i * 2 + 1] = _pico;

        var _suelo = animcurve_point_new();
        _suelo.posx = (i * 2 + 2) / _total;  _suelo.value = 0;
        _puntos[i * 2 + 2] = _suelo;
    }

    _canal.points = _puntos;
    _curva.channels = [_canal];

    return _curva;
}
```

```gml
/// obj_controlador · Evento Clean Up
if (animcurve_exists(curva_rebote)) animcurve_destroy(curva_rebote);
```

> 🔺 **Las curvas creadas con `animcurve_create()` hay que destruirlas.** El manual avisa de que si
> no, «ocuparán espacio en la memoria, lo que puede provocar una fuga». Los canales y los puntos sí
> los recoge el recolector al destruir la curva; la curva no. Las curvas que son **asset** (creadas
> en el IDE) no se destruyen: no las has creado tú.

### 5.6 Cuándo NO usarlas

Para easing genérico de código, **no**. Esta biblioteca ya tomó esa decisión y está documentada en
`06 · scr_math_util.gml` y en el [README de `06`](../06%20-%20Assets%20y%20Scripts/README.md): una
curva exige crear un asset, mantenerlo sincronizado y buscar su canal en runtime; una función pura
de easing es una línea, se testea sola y no gasta memoria.

Las Animation Curves ganan en un caso exacto: **cuando la forma de la curva es una decisión de
diseño que alguien que no programa tiene que poder cambiar**, o cuando la curva se usa dentro de
una Sequence, que es su hábitat natural
([manual](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sequence_Properties/Using_Animation_Curves.md)).
Al asignar una curva a una pista de parámetro el número de canales debe cuadrar: Posición 2 (X, Y),
Rotación 1, Multiplicación de color 4 (A, R, G, B, y **el rango debe ser 0-255**), Escala 2,
Volumen 1 (entre 0 y 1), Tono 1 (mínimo 0).

---

## 6 · Sequences (asset)

### 6.1 El vocabulario, que es la mitad del problema

| Término | Qué es | Cómo se toca |
|---|---|---|
| **Sequence object** | El asset, el plano | `sequence_get(seq_x)` · `sequence_create()` |
| **Sequence instance** | La copia viva de ese plano | `layer_sequence_get_instance(elemento)` · variable `sequence_instance` |
| **Sequence element** | El elemento de capa que la contiene en una room | Lo que devuelve `layer_sequence_create()`; todas las `layer_sequence_*` |
| **Sequence data** | El struct con pistas, keyframes, longitud y modo de reproducción | Campos del sequence object: `.length`, `.loopmode`, `.playbackSpeed`… |

> 🔺 **Editar un sequence *object* en runtime es permanente.** El manual lo dice literalmente: los
> cambios «**no** se restablecerán al reiniciar el juego o el room usando `room_restart()` o
> `game_restart()`». Si modificas el asset, guarda el valor original y restáuralo.

### 6.2 Qué puede llevar una pista

Constantes `seqtracktype_*` verificadas contra el runtime:

| Constante | Pista de… |
|---|---|
| `seqtracktype_graphic` · `seqtracktype_spriteframes` | un sprite dibujado; los fotogramas concretos de ese sprite |
| `seqtracktype_instance` | una instancia de objeto real, con sus eventos |
| `seqtracktype_audio` · `seqtracktype_audioeffect` | sonido y efectos de bus de audio |
| `seqtracktype_text` · `seqtracktype_string` | texto en pantalla |
| `seqtracktype_particlesystem` | un asset de Particle System |
| `seqtracktype_sequence` | otra Sequence anidada |
| `seqtracktype_real` · `seqtracktype_bool` · `seqtracktype_color` (`seqtracktype_colour`) | pistas de parámetro: posición, escala, alpha, tinte… |
| `seqtracktype_clipmask` · `_clipmask_mask` · `_clipmask_subject` | máscaras de recorte |
| `seqtracktype_moment` · `seqtracktype_message` | momentos (código) y broadcast messages |
| `seqtracktype_group` · `seqtracktype_empty` | agrupación y pistas vacías |

Modos de reproducción: `seqplay_oneshot`, `seqplay_loop`, `seqplay_pingpong`. Dirección del
cabezal: `seqdir_left` / `seqdir_right`. Las claves de audio admiten `seqaudiokey_oneshot` y
`seqaudiokey_loop`, y las de parámetro `seqinterpolation_assign` (salto seco) o
`seqinterpolation_lerp` (interpolado).

> La pista de partículas tiene una limitación documentada: se añade **una sola pista para todo el
> sistema** y los emisores no se animan por separado. Ver
> [02 · 05 §3.2](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20part%C3%ADculas%20nuevo.md).

### 6.3 Reproducir una Sequence por código

El patrón del tutorial oficial, con una capa creada al vuelo para que la Sequence se dibuje a la
profundidad del personaje:

```gml
/// scr_animacion · lanzar_secuencia(_seq)
/// @desc Crea una capa a la profundidad de la instancia y reproduce en ella una Sequence.
/// @param {Asset.GMSequence} _seq  La Sequence a reproducir.
/// @return {Id.SequenceElement}
function lanzar_secuencia(_seq)
{
    capa_secuencia     = layer_create(depth);
    elemento_secuencia = layer_sequence_create(capa_secuencia, x, y, _seq);
    layer_sequence_xscale(elemento_secuencia, image_xscale);  // Hereda el volteo.

    return elemento_secuencia;
}

/// scr_animacion · secuencia_activa()
/// @desc Limpia la Sequence en curso si ha terminado. Llamar cada paso.
/// @return {Bool}  true si sigue reproduciéndose.
function secuencia_activa()
{
    if (elemento_secuencia == -1) return false;

    if (layer_sequence_is_finished(elemento_secuencia))
    {
        layer_sequence_destroy(elemento_secuencia);
        layer_destroy(capa_secuencia);
        elemento_secuencia = -1;
        capa_secuencia     = -1;
        return false;
    }

    return true;
}
```

```gml
/// obj_jugador · Evento Create (fragmento)
capa_secuencia = -1;  elemento_secuencia = -1;
```

```gml
/// obj_jugador · Evento Step (fragmento)
if (secuencia_activa()) exit;   // Mientras la Sequence manda, el jugador no se controla.

if (keyboard_check_pressed(vk_space))
{
    lanzar_secuencia(seq_ataque_pesado);
    alarm[0] = 1;   // Ver la nota de abajo: ocultar en el mismo paso deja un frame vacío.
}
```

```gml
/// obj_jugador · Evento Alarm 0
visible = false;    // La Sequence ya dibuja al personaje.
```

> 🔺 **Hay un fotograma de desfase** entre crear el elemento y que la Sequence aparezca. Si ocultas
> la instancia en el mismo paso se ve un fotograma vacío; el tutorial oficial lo resuelve con una
> alarma de 1 paso. Es un detalle pequeño que se nota mucho.

Control de la reproducción, todo verificado:

```gml
layer_sequence_pause(elemento);                 // layer_sequence_play() reanuda.
layer_sequence_is_paused(elemento);             // → Bool
layer_sequence_headpos(elemento, 30);           // Salta al fotograma 30 (scrub).
layer_sequence_get_headpos(elemento);           // → posición actual del cabezal
layer_sequence_get_length(elemento);            // → longitud en fotogramas
layer_sequence_headdir(elemento, seqdir_left);  // Reproduce hacia atrás.
layer_sequence_speedscale(elemento, 0.25);      // Cámara lenta al 25 %.
layer_sequence_x(elemento, x);                  // También _y, _angle, _xscale, _alpha, _blend.
```

`layer_sequence_speedscale()` es la vía para que un *hit stop* alcance también a las Sequences en
curso: escala 0 durante la congelación, 1 después.

### 6.4 Momentos, broadcast messages y eventos

Son **tres** cosas distintas y se confunden constantemente:

- **Momento** — una llamada a una función en un fotograma concreto. Se añade con el botón
  *Add Moment* del editor (basta dar el nombre de la función) o por código, montando una pista
  `seqtracktype_moment` cuyos *keyframe data* llevan `.event = method(...)`. Es preciso y acoplado.
- **Broadcast message** — un *string* emitido en un fotograma, recibido igual que el de un sprite
  (§3.6), sólo que `event_data[? "event_type"]` vale `"sequence event"`. Se define en
  `messageEventKeyframes` con pistas `seqtracktype_message`. Es desacoplado: cámara, audio y UI
  pueden reaccionar al mismo fotograma sin conocerse.
- **Eventos de la Sequence** — propiedades del struct a las que se asigna un `method()`:
  `event_create`, `event_destroy`, `event_clean_up`, `event_step`, `event_step_begin`,
  `event_step_end`, `event_async_system`, `event_broadcast_message`. Dentro de esas funciones
  `self` es la instancia de Sequence y **no admiten argumentos**.

```gml
/// obj_camara · Evento Other → Broadcast Message
if (event_data[? "event_type"] != "sequence event") exit;

switch (event_data[? "message"])
{
    case "impacto":
        temblor(6, 0.25);
        audio_play_sound(snd_impacto, 10, false);
    break;

    case "fin_cinematica":
        // element_id identifica al emisor: sirve para consultarlo o destruirlo.
        if (layer_get_element_type(event_data[? "element_id"]) == layerelementtype_sequence)
        {
            global.cinematica_en_curso = false;
        }
    break;
}
```

Para un juego que ya usa señales
([04 · 16](../04%20-%20Recetas%20por%20g%C3%A9nero/16%20-%20Se%C3%B1ales%20y%20desacoplamiento.md)),
el broadcast encaja mejor que el momento.

> 🔺 Si la Sequence está **en pausa**, sus eventos Step **no se disparan**, y no vuelven a hacerlo
> hasta el paso siguiente a reanudarla. Es la causa habitual de «mi código de Sequence dejó de
> ejecutarse sin motivo». El orden de los eventos no cambia aunque se reproduzca hacia atrás.

### 6.5 Sustituir objetos e ignorar el control del jugador

`sequence_instance_override_object(instancia, objeto_original, objeto_o_instancia_nuevos)` sustituye
todas las apariciones de un objeto dentro de una instancia de Sequence: sirve para reutilizar una
cinemática con personajes distintos, o para meter **al jugador real** en ella.

```gml
/// obj_disparador_cinematica · Evento Create
var _el  = layer_sequence_create("Cinematicas", x, y, seq_encuentro);
var _ins = layer_sequence_get_instance(_el);

sequence_instance_override_object(_ins, obj_maniqui_jugador, obj_jugador.id);
```

> 🔺 **Sólo funciona antes de que la Sequence empiece a reproducirse.** Si ya arrancó, la llamada
> no hace nada y no avisa.

En el objeto controlado hay que apagar su lógica, para lo que existen dos variables integradas de
solo lectura:

```gml
/// obj_jugador · Evento Step (primera línea)
if (in_sequence) exit;   // Una Sequence me está moviendo: no toco x/y.
```

`in_sequence` vale `true` mientras una Sequence controla la instancia y vuelve a `false` al
terminar, aunque el elemento siga existiendo. `drawn_by_sequence` dice si la dibuja la Sequence
—ordenada junto al resto de sus elementos— en vez de dibujarse ella misma; a diferencia de
`in_sequence`, **sí se puede escribir**.

> El manual insiste: las instancias dentro de una Sequence **no deben tocar** sus variables `x`,
> `y`, `image_xscale`, `image_yscale` ni `image_angle`, porque la Sequence las sobrescribe cada paso.

### 6.6 Rendimiento y cambios de room

- Las instancias de las pistas de objeto **se crean en cuanto se crea el elemento**, no cuando
  empieza su *asset key*: el controlador sólo cambia su `visible`. Sus eventos Create se ejecutan
  al principio, aunque el personaje aparezca en el segundo 4.
- Una Sequence viva es una capa más, con su coste. Destrúyela al terminar (§6.3).
- Los assets de Sequence y las Animation Curves **requieren el recolector de basura pero aun así
  hay que llamar a su función de destrucción**; está señalado en
  [01 · 15](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md).
- Al cambiar de room, los elementos de la room vieja desaparecen con ella, pero las **referencias**
  guardadas en variables globales quedan colgando: ponlas a `-1` en el Room End.

### 6.7 Cuándo NO usar una Sequence

**Cualquier cosa que dependa del input.** Una Sequence es una línea de tiempo grabada: no sabe que
el jugador soltó el botón, no se interrumpe a mitad sin cortar en seco y no se ramifica.

| Sí, Sequence | No, Sequence |
|---|---|
| Intro, cinemática, pantalla de título | Correr, saltar, atacar |
| Ataque de jefe scriptado y no cancelable | Combo del jugador con cancelaciones |
| Transición de menú, UI animada compleja | HUD que refleja valores cambiantes |
| Fondo animado, decorado | Cualquier cosa con hitbox que el jugador controla |
| Efecto compuesto (sprite + sonido + partículas + texto) | Un efecto que hay que instanciar 200 veces |

---

## 7 · Animación esqueletal, en dos líneas

Si el personaje tiene muchas partes articuladas y muchas animaciones, dibujar cada fotograma sale
carísimo. **Spine** resuelve eso: el esqueleto se anima fuera de GameMaker y el runtime lo
reproduce con las 48 funciones `skeleton_*`, con mezcla entre animaciones (`skeleton_animation_mix`),
manipulación de huesos y sistemas de equipamiento vía *attachments*. Está entero en
[08 · 22](../08%20-%20Referencia%20GML%20completa/22%20-%20Animaci%C3%B3n%20esqueletal%20%28Spine%29.md).

Dos cosas de aquí aplican allí: **`image_index` sigue funcionando** sobre un sprite de Spine, y los
eventos *Animation Update* y *Animation Event* **son exclusivos de Spine** — no tienen nada que ver
con *Animation End* (§3.3), aunque estén uno al lado del otro en la lista de eventos *Other*.

---

## 8 · Timing: 60 fps y «animar en dobles»

Richard Williams cuenta que Ken Harris, el animador de Warner Bros. que llegó a su estudio,
planificaba en **dobles**: «doce dibujos por segundo, exponiendo cada dibujo dos veces, en lugar de
trabajar en *unos*, una exposición por dibujo, que son veinticuatro dibujos por segundo — el doble
de trabajo». Y añade la regla: «como la mayoría de las acciones normales funcionan bien en dobles,
los animadores de Warner intentaban evitar poner acciones en unos», y pasaban a unos sólo para las
acciones rápidas.

Un juego moderno corre a 60 fps, no a 24, así que la traducción es esta:

| Cadencia | Subimágenes/s | Pasos de juego por subimagen a 60 fps | Sensación |
|---|---|---|---|
| «Unos» de cine | 24 | 2,5 | Muy fluido; caro de dibujar |
| **Estándar de pixel art (dobles)** | **12** | **5** | El punto dulce: legible y asumible |
| «Treses» | 8 | 7,5 | Estilizado, entrecortado a propósito |
| Idle lento | 4-6 | 10-15 | Respiración, parpadeo, agua |
| Efecto rápido (*smear*, chispa) | 30-60 | 1-2 | Se siente, no se lee |

**En el IDE:** modo *Frames per second* y el valor de la columna «Subimágenes/s». Nada de dividir a
mano. **En el código:** `image_speed` como multiplicador — un enemigo herido al 60 % es
`image_speed = 0.6`, no un sprite nuevo.

**Pausar la animación con la escala de tiempo.** `image_speed` no conoce el *hit stop*: hay que
multiplicarlo tú.

```gml
/// obj_jugador · Evento Step (al aplicar la animación)
image_speed = velocidad_animacion_base * time_delta();
```

`time_delta()` (de [04 · 15 §5.0](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md))
devuelve 0 mientras el juego está congelado, así que el sprite se queda clavado en el fotograma del
impacto: exactamente lo que hace que un golpe se sienta. Para las Sequences, lo mismo con
`layer_sequence_speedscale()`.

---

## 9 · Checklist de calidad

- [ ] **Silueta.** Rellena el sprite de negro: ¿se distingue la pose de las demás del personaje?
- [ ] **Origen.** Todos los fotogramas comparten origen, y es *Bottom Centre* si camina por el suelo.
- [ ] **Máscara.** `mask_index` apunta a un sprite fijo y no cambia con la animación.
- [ ] **Anticipación.** Toda acción que el jugador deba poder responder tiene al menos 6 fotogramas
      de telegrafiado a 60 fps (100 ms).
- [ ] **Bucle.** El último fotograma enlaza con el primero sin salto. Míralo veinte veces seguidas.
- [ ] **Timing medido.** Sabes en fotogramas el *startup*, los activos y la recuperación, y están en
      una tabla, no dispersos por el código.
- [ ] **Cadencia.** Modo *Frames per second*, con un valor de la tabla del §8.
- [ ] **Fin gestionado.** Las animaciones de un solo uso congelan explícitamente
      (`image_speed = 0; image_index = image_number - 1;`).
- [ ] **Interrumpible.** Se cancela en el fotograma que el diseño dice y el estado queda limpio
      (`ya_golpeados` vaciado, hitbox destruido).
- [ ] **Escala de tiempo.** La animación se congela con el *hit stop* y respeta la pausa.
- [ ] **Sin fugas.** Cada `animcurve_create()` tiene su `animcurve_destroy()`; cada
      `layer_sequence_create()` su `layer_sequence_destroy()`.
- [ ] **A 30 y a 144 fps.** Nada que use `delta_time` cambia de comportamiento.

---

## 10 · Errores clásicos y cómo evitarlos

| Error | Qué se ve | Arreglo |
|---|---|---|
| `image_index = 0` cada paso | La animación no pasa del primer fotograma | Comparar `sprite_index` antes de asignar (§3.5) |
| `image_index == image_number - 1` | El final se detecta a veces sí y a veces no | Usar `>=`: `image_index` es real, no entero (§3.3) |
| Confundir `image_speed` con fps | La animación va al doble o a la mitad | Es un **multiplicador** de la velocidad del editor (§3.1) |
| Modo *Frames per game frame* con valor 10 | La animación entera pasa en un paso | Cambiar a *Frames per second* (§3.2) |
| Orígenes distintos entre fotogramas | El personaje da un saltito al cambiar de animación | Un solo origen para todos los sprites (§3.9) |
| Máscara «Same as Sprite» en el jugador | Colisiones que aparecen y desaparecen solas | `mask_index` a un sprite dedicado (§3.9) |
| Squash & stretch con `image_xscale` | Las colisiones se deforman con el efecto | Deformar en el Draw con `draw_sprite_ext()` (§3.9) |
| Broadcast messages que no suenan | Pasos y golpes sin audio | El sprite avanza con `image_index` a mano: sólo saltan con `image_speed` (§3.6) |
| `lerp(x, objetivo, 0.1)` | El juego se siente distinto a 30 y a 144 fps | Interpolación exponencial con `delta_time` (§4.2) |
| `current_time` para un *bob* | La oscilación no se pausa ni respeta el *hit stop* | Acumular una fase propia con `delta_time * time_delta()` (§4.3) |
| Todas las monedas suben a la vez | El nivel «respira» de forma antinatural | Desfase aleatorio por instancia (`fase = random(360)`) |
| `posx` fuera de 0-1 en `animcurve_channel_evaluate` | Valores raros o 0 | `clamp(t, 0, 1)`: el manual exige el rango (§5.3) |
| Buscar el canal de la curva cada paso | Coste innecesario en el bucle principal | Cachear el struct del canal en el Create (§5.3) |
| `animcurve_create()` sin `animcurve_destroy()` | Fuga de memoria que crece con el tiempo | Destruir en el Clean Up (§5.5) |
| Sequence para el ataque del jugador | No se puede cancelar y se siente rígido | Fotogramas + FSM; Sequence sólo para lo no interrumpible (§6.7) |
| `sequence_instance_override_object` tarde | No hace nada y no avisa | Llamarla justo tras `layer_sequence_create()` (§6.5) |
| La instancia se mueve dentro de la Sequence | Tirones y posiciones imposibles | `if (in_sequence) exit;` al principio del Step (§6.5) |
| Editar un sequence object en runtime | El cambio persiste tras `room_restart()` | Guardar el valor original y restaurarlo (§6.1) |
| Ocultar la instancia el mismo paso que lanzas la Sequence | Un fotograma en blanco | Alarma de 1 paso (§6.3) |
| Un tercer sistema de tween | Tres `tween_to()` incompatibles en el mismo proyecto | Usar `scr_tween.gml` y nada más (§4) |

---

## Ver también

- [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md) — easing (§4.4), screen shake (§5.1), tween (§5.2), squash & stretch (§5.3), escala de tiempo (§5.0), anticipación (§4.8 y §5.8).
- [06 · `scr_tween.gml`](../06%20-%20Assets%20y%20Scripts/scr_tween.gml) — `tween_to`, `tween_update`, `tween_stop`, `tween_stop_all`, `tween_delay`. El sistema de tween de esta biblioteca.
- [06 · `scr_state_machine.gml`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) — `fsm_bind()` y el struct `StateMachine` que dirige qué animación toca.
- [08 · 01 — Dibujo básico y sprites](../08%20-%20Referencia%20GML%20completa/01%20-%20Dibujo%20b%C3%A1sico%20y%20sprites.md) — la tabla completa de variables `image_*` y toda la familia `draw_sprite*`.
- [08 · 22 — Animación esqueletal (Spine)](../08%20-%20Referencia%20GML%20completa/22%20-%20Animaci%C3%B3n%20esqueletal%20%28Spine%29.md) · [08 · 15 — Structs y funciones](../08%20-%20Referencia%20GML%20completa/15%20-%20Structs%20-%20funciones.md) — cómo funcionan los structs que devuelven `animcurve_*` y `sequence_*`.
- [01 · 11 — Dibujo y renderizado](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) · [01 · 06 — Eventos y ciclo del juego](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) — dónde encaja el Draw en el frame y el orden exacto de los eventos.
- [03 · 11 — Animaciones y Tile Sets](../03%20-%20Cursos%20%28YouTube%29/11%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%2011%20-%20Animaciones%20y%20Tile%20Sets.md) — la cascada de prioridades paso a paso, con su bug del ápice.
- [02 · 05 — Sistema de partículas nuevo](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20part%C3%ADculas%20nuevo.md) §3.2 — la pista de partículas dentro de una Sequence.
- [13 · 03 — Pixel art y resolución](./03%20-%20Pixel%20art%20y%20resoluci%C3%B3n.md) · [13 · 08 — Físicas a mano y fluidos](./08%20-%20F%C3%ADsicas%20a%20mano%20y%20fluidos.md).
- [05 · 04 — Convenciones y estilo GML](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) — nombres reservados y prefijos.
- Manual espejado: [El editor de Sequence](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sequences.md) · [El editor de curvas de animación](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Animation_Curves.md) · [Mensajes de difusión](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sequence_Properties/Broadcast_Messages.md) · [Eventos, momentos y mensajes de difusión](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Sequences/Sequence_Events_Moments_Broadcast.md) · [Funciones de curvas de animación](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Animation_Curves/Animation_Curves.md)

---

## Fuentes

Consultadas el **6 de septiembre de 2026**.

1. Frank Thomas y Ollie Johnston, *The Illusion of Life: Disney Animation*, Hyperion, 1981 — origen de los doce principios; nombres y definiciones verificados en <https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation>.
2. Richard Williams, *The Animator's Survival Kit*, Faber & Faber, 2001 — capítulos «It's all in the timing and the spacing» (la moneda; timing frente a spacing) y «The Great Ones and Twos Battle» (Ken Harris; doce dibujos por segundo en dobles). Texto completo consultado en <https://archive.org/stream/TheAnimatorsSurvivalKitRichardWilliams/The%20Animator's%20Survival%20Kit%20-%20Richard%20Williams_djvu.txt>.
3. Pedro Medeiros (Saint11), *Pixel Art Tutorials* — 61 tutoriales, entre ellos *Motion Blur*, *Character Idle*, *Walk Cycle* y *Fabric / Flags* (2017). Índice en <https://lospec.com/pixel-art-tutorials/author/pedro-medeiros>; original en <https://saint11.art/blog/pixel-art-tutorials/>.
4. Dustloop Wiki, *Using Frame Data* — definiciones de *startup*, *active*, *recovery*, *blockstun*, *hitstun* y la convención «first active frame». <https://www.dustloop.com/wiki/index.php/Using_Frame_Data>.
5. Manual oficial de GameMaker, rama LTS, espejo local en `09 - Manual oficial/manual-lts-2026-es/` (descargado el 1-9-2026 de <https://manual.gamemaker.io/lts/es/>). Páginas usadas: *El editor de Sequence*, *El editor de curvas de animación*, *La biblioteca de curvas de animación*, *Uso de las curvas de animación*, *Mensajes de difusión*, *Eventos, momentos y mensajes de difusión*, *Otros eventos* (Animation End / Animation Update / Animation Event), *El editor de sprites* (Frame Speed, Broadcast Messages, Sprite Origin), y las fichas de `image_index`, `image_speed`, `sprite_set_speed`, `sprite_get_speed_type`, `layer_sequence_create`, `sequence_instance_override_object`, `in_sequence`, `drawn_by_sequence`, `animcurve_create`, `animcurve_channel_new`, `animcurve_point_new` y `animcurve_channel_evaluate`.
6. Gurpreet S. Matharoo, *Easy Tweening with Animation Curve Library*, blog oficial de GameMaker, 8-4-2021 — presets de la Curve Library, modos de suavizado y uso de `animcurve_get_channel()` / `animcurve_channel_evaluate()` desde GML. <https://gamemaker.io/en/blog/easy-tweening-with-animation-curve-library>.
7. Gurpreet S. Matharoo, *Busting Moves! Bring Your Characters to Life with Sequences*, blog oficial, 10-6-2021 — patrón `layer_create` + `layer_sequence_create` + `layer_sequence_is_finished` + destrucción, y el desfase de un fotograma al ocultar la instancia. <https://gamemaker.io/en/blog/busting-moves-sequences>.
8. Gurpreet S. Matharoo y Sam Spade, *How to Animate Objects in GameMaker*, tutorial oficial, 13-10-2022 — flujo del editor de Sequences (Stretch Asset Key, Curve Mode, Convert to Curve, Curve Library) y el patrón `if (!in_sequence)` para sustituir instancias por su Sequence. <https://gamemaker.io/en/tutorials/animate-objects-gamemaker>.
9. `GmlSpec.xml` del runtime GMS2 `2026.0.0.23` instalado — todos los símbolos de este documento verificados con `python3 "_indice/buscar.py"`.
