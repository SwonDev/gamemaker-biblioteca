# 19 · Programación rítmica (juegos de ritmo)

> *Crypt of the NecroDancer*, *Rhythm Doctor*, *Thumper*, o simplemente enemigos que atacan
> al compás. Todo lo que tenga que ocurrir **en el beat**.
>
> **Hueco detectado** al cruzar el [catálogo de tutoriales del foro](../07%20-%20Ecosistema/16%20-%20Cat%C3%A1logo%20de%20la%20secci%C3%B3n%20Tutorials%20del%20foro.md)
> con esta biblioteca. Mecanismo verificado contra el manual LTS 2026.
>
> **Corrección del 8 de septiembre de 2026**: las funciones del conductor
> (`conductor_arrancar`, `conductor_error`, `conductor_juzgar`) vivían declaradas dentro del
> `Create` de `obj_conductor`. Eso compilaba limpio y reventaba en tiempo de ejecución en cuanto
> **otro** objeto las llamaba — mismo mensaje que la Trampa 4 de
> [`12 · 09`](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-4--el-compilador-no-detecta-una-función-inventada-ni-una-variable-sin-declarar)
> (`Variable X.Y(...) not set before reading it`), pero por una causa distinta: la función sí
> existe, solo que no donde el compilador la busca. Movidas a un script (`scr_conductor.gml`);
> el porqué está en §1. Encontrado y verificado en vivo — compilar, ejecutar y volver a
> compilar tras el arreglo — en
> [`_indice/auditorias/r8-prueba-ritmo.md` §5.1](../_indice/auditorias/r8-prueba-ritmo.md#51--hallazgo-nuevo-el-central-de-esta-auditoría-las-funciones-del-conductor-no-son-globales).
> La misma sesión midió también la deriva real de `audio_sound_get_track_position()` en pausa y
> reproducción activa: números corregidos en la tabla de trampas, al final de este documento.

---

## La regla que decide si tu juego funciona

**El reloj es la canción, no el juego.**

```gml
/// ❌ contar fotogramas — se desincroniza SIEMPRE
contador++;
if (contador >= 30) { beat(); contador = 0; }
```

Esto se descuadra pasados dos minutos, y no por un bug tuyo: el reloj de la tarjeta de sonido
y el bucle del juego **corren a velocidades ligeramente distintas**. Un fotograma perdido, un
cambio de sala, un alt-tab, y ya vas medio beat por detrás. El jugador lo nota antes que tú.

```gml
/// ✅ preguntarle a la canción dónde está
var _seg   = audio_sound_get_track_position(musica);
var _beats = _seg * (bpm / 60);
```

📘 [`audio_sound_get_track_position`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Audio/audio_sound_get_track_position.md)

> 🔺 **Necesita el ID de la instancia, no el sonido.** `audio_play_sound` devuelve un ID; ese
> es el que hay que guardar. Pasarle `snd_musica` directamente no funciona.

---

## 1 · El conductor

Un solo objeto persistente lleva el tiempo. Todo lo demás le pregunta a él.

```gml
/// obj_conductor · Create — solo variables, ninguna función (ver el aviso de abajo)
bpm          = 128;
seg_por_beat = 60 / bpm;
offset       = 0;      // desfase del primer beat dentro del archivo (segundos)

musica       = -1;
beat_actual  = -1;     // último beat entero que ya se ha anunciado
posicion     = 0;      // en beats, con decimales
pausado      = false;  // ver conductor_pausar()/conductor_reanudar(), más abajo
```

> ⚠️ **Las funciones del conductor van en un script, no en este `Create`.** Un
> `function nombre() {...}` declarado dentro de un evento no registra un identificador global:
> queda ligado a `self` como una **variable más de esa instancia** (el mismo mecanismo que hace
> que [`method()`](../08%20-%20Referencia%20GML%20completa/15%20-%20Structs%20-%20funciones.md)
> diga «crea una función ligada a un ámbito concreto, de modo que dentro de ella `self` apunta a
> ese ámbito»). Por eso `obj_conductor` puede llamarse a sí mismo sin problema —`self` ya es
> él—, pero **cualquier otro objeto** que la llame sin cualificar revienta en tiempo de
> ejecución con `Variable obj_x.conductor_arrancar(...) not set before reading it`: compila
> limpio (la Trampa 4 de `12 · 09` no distingue «no existe» de «no es tuya»), y solo se ve
> jugando. Declarar una función dentro de un evento **es legítimo** cuando solo la va a usar esa
> misma instancia — el patrón *controller singleton* de uso interno—; en cuanto otro objeto
> necesite llamarla, como es el caso aquí («todo lo demás le pregunta a él»), tiene que vivir en
> un script, donde sí queda registrada como global desde el primer fotograma.

```gml
/// scr_conductor.gml — llamables desde cualquier objeto del juego
function conductor_arrancar(_sonido, _bpm, _offset = 0) {
    with (obj_conductor) {
        bpm          = _bpm;
        seg_por_beat = 60 / _bpm;
        offset       = _offset;
        beat_actual  = -1;
        pausado      = false;
        musica       = audio_play_sound(_sonido, 10, false);
        return musica;
    }
}

function conductor_pausar() {
    with (obj_conductor) {
        if (musica != -1) {
            audio_pause_sound(musica);
            pausado = true;
        }
    }
}

function conductor_reanudar() {
    with (obj_conductor) {
        if (musica != -1) {
            audio_resume_sound(musica);
            pausado = false;
        }
    }
}
```

> 💡 **El `with (obj_conductor)` no es opcional dentro de un script.** Al mover el cuerpo de un
> evento a un script, `self` dentro de la función pasa a ser quien la llame, no ya
> `obj_conductor` — sin el `with`, `conductor_arrancar()` llamada desde `obj_juego` escribiría
> `bpm`, `musica`… en `obj_juego`, no en el conductor. Es el mismo patrón que ya usan
> `conductor_error()`/`conductor_juzgar()` en el §2 de abajo, aplicado también aquí.

```gml
/// obj_conductor · Step
if (musica == -1 || !audio_is_playing(musica) || pausado) exit;

var _seg  = audio_sound_get_track_position(musica) - offset;
posicion  = _seg / seg_por_beat;              // 3.25 = un cuarto después del beat 3

// ¿hemos cruzado a un beat nuevo desde el fotograma anterior?
var _entero = floor(posicion);
if (_entero > beat_actual) {
    // si el juego se atascó, puede que hayamos saltado varios: los anunciamos todos
    while (beat_actual < _entero) {
        beat_actual++;
        senal_emitir("beat", { n: beat_actual, compas: beat_actual div 4 });
    }
}
```

> 💡 **El `while` en vez de un `if` no es paranoia.** Un tirón de 200 ms a 128 BPM se come
> medio beat; una carga de sala se come cinco. Con un `if`, los enemigos que debían moverse en
> esos beats simplemente no se mueven, y la partida se rompe en silencio.
>
> 💡 La emisión usa el sistema de [16 · Señales](./16%20-%20Señales%20y%20desacoplamiento.md).
> Sin él, el conductor acabaría con una lista de `with (obj_enemigo)` que crece sin parar.

---

## 2 · Juzgar la pulsación del jugador

El jugador nunca acierta exactamente. Lo que mides es **cuánto se ha desviado**, y decides con
qué tolerancia lo perdonas.

**Estas dos funciones también van en `scr_conductor.gml`** (continuación del script de §1), no
en ningún evento — por la misma razón: las va a llamar `obj_nota`, la UI de puntuación, quien
sea, nunca solo `obj_conductor`.

```gml
/// scr_conductor.gml (continuación) — devuelve el error respecto al beat más cercano, en beats
/// 0 = clavado · -0.1 = un pelín pronto · +0.1 = un pelín tarde
function conductor_error() {
    with (obj_conductor) {
        return posicion - round(posicion);
    }
}

/// clasifica esa desviación
function conductor_juzgar() {
    var _e = abs(conductor_error());

    if (_e <= 0.08) return "perfecto";
    if (_e <= 0.18) return "bien";
    if (_e <= 0.30) return "flojo";
    return "fallo";
}
```

| Ventana | En beats | A 128 BPM | Sensación |
|---|---|---|---|
| Perfecto | ±0,08 | ±37 ms | Exigente pero justo |
| Bien | ±0,18 | ±84 ms | Cómodo |
| Flojo | ±0,30 | ±140 ms | Muy permisivo |

> ⚠️ **Estas ventanas se ajustan a mano, jugando.** No hay número correcto: depende del BPM,
> del género y de si tu público juega con mando o con teclado. Empieza permisivo y aprieta.

---

## 3 · La latencia, que es el problema de verdad

Entre que el jugador pulsa y que **oye** el sonido pasan milisegundos: el sistema operativo, el
buffer de la tarjeta, la pantalla, los cascos Bluetooth. En Bluetooth pueden ser **200 ms** —
más de un cuarto de beat.

**No puedes eliminarla. Puedes dejar que el jugador la calibre.**

```gml
/// pantalla de calibración: el jugador pulsa 16 veces al ritmo de un metrónomo
/// y nos quedamos con su desviación media
if (tecla_pulsada) {
    array_push(muestras, conductor_error());

    if (array_length(muestras) >= 16) {
        var _suma = 0;
        for (var _i = 0; _i < 16; _i++) _suma += muestras[_i];

        // guardamos la media como offset personal del jugador
        global.latencia = (_suma / 16) * obj_conductor.seg_por_beat;
        ini_open("ajustes.ini");
        ini_write_real("audio", "latencia", global.latencia);
        ini_close();
    }
}
```

Y a partir de ahí, todo juicio la descuenta — **este bloque REEMPLAZA al `conductor_error()` de
§2 dentro de `scr_conductor.gml`**, mismo nombre, no lo declares dos veces en el mismo script:

```gml
/// scr_conductor.gml — sustituye a la versión de §2
function conductor_error() {
    with (obj_conductor) {
        var _p = posicion - (global.latencia / seg_por_beat);
        return _p - round(_p);
    }
}
```

> 💡 **Descarta la primera pulsación de la calibración.** Casi siempre está fuera: el jugador
> aún está pillando el ritmo, y una muestra mala entre 16 desplaza la media lo suficiente para
> que la calibración empeore las cosas.
>
> ⚠️ **Todo juego de ritmo serio tiene pantalla de calibración.** Si el tuyo no la tiene, para
> media de tus jugadores el juego estará roto y creerán que es culpa suya.

---

## 4 · Que se vea el ritmo

Lo visual no debe consultar el reloj por su cuenta: usa la misma `posicion` del conductor.

```gml
/// obj_enemigo · Draw — rebote sincronizado, sin variables propias
var _fase  = frac(obj_conductor.posicion);        // 0 → 1 dentro del beat
var _salto = 1 + 0.25 * power(1 - _fase, 3);      // golpe seco y caída suave

draw_sprite_ext(sprite_index, image_index, x, y, 1, _salto, 0, c_white, 1);
```

> 💡 **`power(1 - _fase, 3)` en vez de `sin()`.** El seno sube y baja igual de suave, y eso se
> ve blando. La potencia da el golpe instantáneo en el beat y la caída progresiva, que es lo
> que el ojo lee como «al ritmo». Ver
> [15 · Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md).

---

## 5 · Colocar los eventos: el mapa de la canción

El patrón de notas son datos, y se indexan **por beat**, nunca por segundos.

```gml
/// un compás de 4 beats, cuatro veces
patron = [
    { beat: 0,   tipo: "izquierda" },
    { beat: 1,   tipo: "derecha"   },
    { beat: 2,   tipo: "izquierda" },
    { beat: 2.5, tipo: "derecha"   },   // corchea
    { beat: 3,   tipo: "salto"     },
];
```

```gml
/// obj_generador · Step — soltar la nota con antelación para que llegue a tiempo
#macro BEATS_DE_VIAJE 4        // cuántos beats tarda la nota en cruzar la pantalla

var _p = obj_conductor.posicion;

while (siguiente < array_length(patron)
    && patron[siguiente].beat <= _p + BEATS_DE_VIAJE) {

    var _nota = instance_create_layer(x, y, "Notas", obj_nota);
    _nota.beat_objetivo = patron[siguiente].beat;
    _nota.tipo          = patron[siguiente].tipo;
    siguiente++;
}
```

```gml
/// obj_nota · Step — la posición se calcula, no se acumula
var _restan = beat_objetivo - obj_conductor.posicion;
x = x_meta + _restan * (ancho_pantalla / BEATS_DE_VIAJE);
```

> 💡 **Calcular la posición en vez de acumular `x -= velocidad` es la diferencia entre un
> juego de ritmo que funciona y uno que no.** Acumulando, cada fotograma perdido desplaza la
> nota para siempre. Calculando desde `beat_objetivo`, un tirón produce un salto visual feo
> pero la nota **sigue llegando exactamente cuando debe**. La sincronía se conserva.

---

## Las trampas

| Trampa | Qué pasa |
|---|---|
| Contar fotogramas o usar `alarm` | Se descuadra a los pocos minutos, siempre |
| Pasar `snd_musica` en vez del ID de instancia | La función devuelve basura |
| `if` en vez de `while` al detectar el beat | Un tirón se salta beats en silencio |
| Acumular `x -= vel` en las notas | Cada fotograma perdido desincroniza permanentemente |
| No tener calibración de latencia | Roto para todo el que juegue con Bluetooth |
| Olvidar el `offset` del archivo | Casi ningún MP3 empieza en el beat 0 |
| `function` del conductor declarada en un evento, llamada desde otro objeto | Compila limpio; revienta en `gm-cli run` (`Variable X.Y(...) not set before reading it`) — muévela a `scr_conductor.gml`, ver §1 |
| Pausar sin guardar el estado `pausado` | Ver el matiz medido justo debajo — no es tan grave como suena, pero hay que escribir el guardia |

> 📏 **`audio_pause_sound` sin recalcular, medido, no solo advertido**: `audio_is_playing()`
> sigue devolviendo `true` con el sonido en pausa —lo dice el propio manual—, así que sin el
> flag `pausado` de §1 el conductor seguiría intentando actualizar `posicion` cada fotograma.
> Con el guardia puesto (`if (... || pausado) exit;`), medido en tres ejecuciones automáticas
> reales ([`_indice/auditorias/r8-prueba-ritmo.md` §5.3](../_indice/auditorias/r8-prueba-ritmo.md#53--trampa-propia-del-audio-sincronizado-verificada-midiendo-pausar-y-reanudar)
> y [§8](../_indice/auditorias/r8-prueba-ritmo.md#8--mis-mediciones-de-sincronía--datos-reales-no-descripciones)):
> la pausa congela `posicion` **exacta**, sin ni un milisegundo de deriva durante los 2 s que
> duró la pausa, y al reanudar **no hay salto** — la próxima lectura continúa justo donde se
> quedó. Sobre reproducción activa (sin pausar), la deriva acumulada de
> `audio_sound_get_track_position()` frente al cálculo teórico fue de **7-12 ms en 7 s** de
> canción (≈0,1 %), y la resolución observada fue de un fotograma (~16-17 ms a 60 fps) — ambas
> muy por debajo de la ventana «perfecto» (±37 ms a 128 BPM). **El aviso original de esta tabla
> era más alarmista que la realidad**: el reloj no se desincroniza al pausar; lo que hace falta,
> y que este documento no escribía en código hasta esta corrección, es guardar el estado
> `pausado` (§1) y comprobarlo antes de tocar `posicion` — sin ese guardia explícito, nada
> garantiza que una futura versión del runtime siga sin recalcular nada durante la pausa.

---

## Ver también

- [13 · Audio](../01%20-%20Fundamentos/13%20-%20Audio.md) — reproducción, grupos y streaming
- [16 · Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — el mecanismo que usa el conductor
- [11 · Arcade y juegos de un botón](./11%20-%20Arcade%20y%20juegos%20de%20un%20botón.md) — parientes cercanos en estructura
- [15 · Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md)
