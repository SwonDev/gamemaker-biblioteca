# 26 · Música adaptativa por capas

> Música que reacciona al juego: sube de intensidad en combate, se calma al explorar, mete
> tambores al acercarse el jefe. La técnica es el **vertical layering**: varias pistas que suenan
> a la vez y sincronizadas, y subes o bajas el volumen de cada una según lo que pasa.
>
> **Cobertura parcial detectada:** había buses/efectos (Novedades 07) y la idea de «capas que
> entran y salen», pero no la receta concreta de crossfade sincronizado.

---

## La idea: todas suenan, controlas el volumen

Divides tu música en capas exportadas **a la misma longitud y tempo**: `mus_base` (bajo +
batería), `mus_melodia`, `mus_combate` (cuerdas tensas), `mus_jefe`. Las lanzas **todas a la
vez**, en bucle, y solo cambias su ganancia.

```
mus_base      ████████████████  (siempre al 100 %)
mus_melodia   ████░░░░████████  (sube al explorar)
mus_combate   ░░░░████████░░░░  (sube en combate)
```

Como arrancan juntas y son igual de largas, **nunca se desincronizan**.

```gml
/// obj_musica · Create — lanzar todas las capas a la vez, en bucle, empezando en silencio
capas = {
    base:    audio_play_sound(mus_base,    100, true),
    melodia: audio_play_sound(mus_melodia, 100, true),
    combate: audio_play_sound(mus_combate, 100, true),
};
audio_sound_gain(capas.base,    1, 0);   // la base siempre suena
audio_sound_gain(capas.melodia, 0, 0);   // las demás, en silencio de momento
audio_sound_gain(capas.combate, 0, 0);
```

> 🔺 **La sincronía sale gratis SOLO si arrancan en el mismo frame.** Lanza las capas juntas en
> el mismo evento. Si lanzas una tarde, va desfasada y ya no hay forma de cuadrarlas a mano.

---

## El crossfade: subir y bajar capas

`audio_sound_gain(instancia, volumen, milisegundos)` **hace el fundido por ti**: el tercer
argumento es el tiempo del cambio.

```gml
/// entrar en combate: sube la capa de combate, baja la melodía, en 1,5 s
function musica_combate() {
    audio_sound_gain(capas.melodia, 0,   1500);
    audio_sound_gain(capas.combate, 1,   1500);
}

/// volver a explorar
function musica_explorar() {
    audio_sound_gain(capas.combate, 0,   2000);
    audio_sound_gain(capas.melodia, 0.8, 2000);
}
```

```gml
/// disparado por el estado del juego, con señales (receta 16)
senal_escuchar("combate_empieza", musica_combate);
senal_escuchar("combate_acaba",   musica_explorar);
```

> 💡 **El tiempo del fundido es el 90 % del efecto.** Un corte instantáneo (0 ms) suena a
> videojuego de 1990. 1000–2000 ms hacen que la transición sea invisible y la música parezca
> «entender» lo que pasa.

---

## Stingers: golpes musicales puntuales

Un *stinger* es un remate corto que suena UNA vez sobre la música (recoger un objeto clave,
matar al jefe). No es una capa en bucle: se dispara suelto.

```gml
audio_play_sound(mus_stinger_victoria, 200, false);   // prioridad alta, sin bucle
```

> ⚠️ **El stinger debe estar en el mismo tono/tempo que la música de fondo** o suena a error.
> Es cosa de tu compositor, no del código: si desafina, no hay GML que lo salve.

---

## Transición por compás (avanzado)

Para que un cambio de tema entre justo en el siguiente compás (no a mitad), usa la posición de
la pista, igual que en [19 · Programación rítmica](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md):

```gml
/// esperar al siguiente compás para el cambio, en vez de cortar a media frase
var _seg = audio_sound_get_track_position(capas.base);
var _seg_por_compas = (60 / bpm) * 4;
var _hasta_compas = _seg_por_compas - (_seg mod _seg_por_compas);
alarm[0] = (_hasta_compas * game_get_speed(gamespeed_fps));   // cambiar cuando llegue
```

---

## Transición horizontal: cambiar de tema sin cortar

El *vertical layering* de arriba resuelve la intensidad **dentro** de un mismo tema (sube o baja
una capa). La otra mitad de la técnica —la que hace falta para pasar de la música de **explorar**
a la de **jefe**, que no comparten ni el tema ni el tempo— es el ***horizontal re-sequencing***:
en vez de mezclar capas, saltas de un segmento de música a otro, y el truco entero está en
**cuándo** saltas.

### Segmentos con puntos de salida legales

Divide cada tema en segmentos de longitud fija —normalmente un número entero de compases— y
**solo cambias de tema al final de un segmento**, nunca a mitad de frase. El cálculo ya lo tienes
arriba: `_seg_por_compas` marca cada punto de salida legal.

```gml
/// scr_musica_horizontal — cambiar de TEMA (no de capa) en el siguiente compás legal
// Cada tema se exporta en dos piezas: "_entrada" (un compás suelto, con el pickup que engancha
// con el bucle) y "_bucle" (el grueso, en bucle). Ver "Escribir la música…" más abajo.

tema_actual    = "explorar";
tema_pendiente = undefined;
tema_voz       = audio_play_sound(asset_get_index(tema_actual + "_bucle"), 100, true);

/// pedir el cambio: solo agenda el punto de salida, no corta nada todavía
function musica_pedir_tema(_tema_nuevo)
{
    if (tema_actual == _tema_nuevo || tema_pendiente == _tema_nuevo) { return; }
    tema_pendiente = _tema_nuevo;

    var _seg            = audio_sound_get_track_position(tema_voz);
    var _seg_por_compas = (60 / bpm) * 4;
    var _hasta_compas   = _seg_por_compas - (_seg mod _seg_por_compas);
    alarm[0] = (_hasta_compas * game_get_speed(gamespeed_fps));   // el punto de salida legal
}

/// Alarm 0 — el ÚNICO sitio donde de verdad se cambia de tema
function musica_cambiar_tema_evento()
{
    if (is_undefined(tema_pendiente)) { return; }

    var _viejo = tema_voz;
    tema_voz   = audio_play_sound(asset_get_index(tema_pendiente + "_entrada"), 100, false);
    // El evento Audio Playback Ended (02 · 07 §6) encadena el "_bucle" del tema nuevo cuando
    // la "_entrada" termine: ahí mismo, no en esta función.

    // La cola del tema viejo se apaga DESPACIO, solapada con el ataque del nuevo: 400-800 ms
    // de solape, nunca un corte seco. Sin este solape hay un hueco de silencio audible.
    audio_sound_gain(_viejo, 0, 600);

    tema_actual    = tema_pendiente;
    tema_pendiente = undefined;
}
```

> 💡 **El «puente» (opcional):** si los dos temas están en tonalidades distintas —el salto de
> «explorar» a «jefe» suele subir de modo—, un salto directo suena a corte aunque caiga en el
> compás correcto. La solución no es de código: es un **segmento puente** de 1-4 compases,
> compuesto para modular de un tema al otro, que se dispara en vez de la «_entrada» directa
> cuando los dos temas lo necesitan. Resérvalo para transiciones que de verdad lo piden (el
> salto a jefe, el final del juego); usarlo en cada cambio de zona es más trabajo de composición
> del que la mayoría de proyectos puede permitirse.

> ⚠️ **La cola solapada solo funciona si el tema viejo tiene algo que solapar.** Si su bucle
> corta en seco al final del compás (sin *release*, sin reverberación), los 600 ms de
> `audio_sound_gain` no tienen nada que desvanecer y el efecto es el mismo corte de siempre. Es
> una decisión de mezcla del propio tema (ver «Escribir la música…» más abajo), no algo que
> arregle el código.

---

## La música como máquina de estados

Con capas y temas ya resueltos, el problema que queda es **quién decide qué suena**. Si cada
sistema del juego llama a `audio_sound_gain()` por su cuenta —el de combate cuando aparece un
enemigo, el del jefe cuando entras en su sala, el de exploración cuando te alejas—, dos de esos
sistemas activos a la vez **se pisan las peticiones de fundido** y la música empieza a
«tartamudear» entre dos objetivos de ganancia distintos cada pocos frames.

La solución es tratar la música como una **máquina de estados con prioridad**: una tabla de datos
en vez de `if` repartidos por el código, y un único punto que de verdad toca las ganancias.

| Estado | Prioridad | Capas activas | Fundido | Nota |
|---|---:|---|---|---|
| Explorar | 0 | base 1 · melodía 0,8 · combate 0 | 2000 ms | estado de reposo, siempre hay uno activo |
| Combate | 1 | base 1 · melodía 0 · combate 1 | 1500 ms | se activa con el primer enemigo alertado |
| Jefe | 2 | base 1 · melodía 0 · combate 0 · **tema «jefe»** | 800 ms + cambio de tema | no es una capa más: cambia de TEMA (sección anterior) |

```gml
/// scr_musica_estados — una tabla de datos en vez de "if" repartidos por el código
global.musica_estados = {
    explorar : { prioridad : 0, capas : { base : 1, melodia : 0.8, combate : 0 }, fundido : 2000 },
    combate  : { prioridad : 1, capas : { base : 1, melodia : 0,   combate : 1 }, fundido : 1500 },
    jefe     : { prioridad : 2, capas : { base : 1, melodia : 0,   combate : 0 }, fundido : 800,
                 tema : "jefe" },   // además pide el cambio de tema de la sección anterior
};

global.musica_estados_activos = [];   // los estados que están "pidiendo" sonar ahora mismo

/// Llamar cuando un sistema entra o sale de un estado que afecta a la música
/// (p.ej. "combate" al primer enemigo alertado, "jefe" al entrar en su sala)
function musica_estado_pedir(_nombre, _activo)
{
    var _i = array_get_index(global.musica_estados_activos, _nombre);
    if (_activo  && _i == -1) { array_push(global.musica_estados_activos, _nombre); }
    if (!_activo && _i != -1) { array_delete(global.musica_estados_activos, _i, 1); }
    musica_estado_aplicar();
}

/// El único punto que de verdad toca ganancias: gana el estado de MAYOR prioridad activo.
/// Si "combate" y "jefe" están activos a la vez (el jefe invoca esbirros), gana "jefe": nunca
/// se mezclan las ganancias de dos estados en el mismo frame.
function musica_estado_aplicar()
{
    var _ganador  = "explorar";
    var _prio_max = -1;
    for (var _i = 0; _i < array_length(global.musica_estados_activos); _i += 1)
    {
        var _e    = global.musica_estados_activos[_i];
        var _prio = global.musica_estados[_e].prioridad;
        if (_prio > _prio_max) { _prio_max = _prio; _ganador = _e; }
    }

    var _def = global.musica_estados[_ganador];
    audio_sound_gain(capas.base,    _def.capas.base,    _def.fundido);
    audio_sound_gain(capas.melodia, _def.capas.melodia, _def.fundido);
    audio_sound_gain(capas.combate, _def.capas.combate, _def.fundido);
    if (struct_exists(_def, "tema")) { musica_pedir_tema(_def.tema); }
}
```

> ⚠️ **Cuando dos estados se solapan, no promedies sus ganancias.** Mezclar «combate al 60 %» y
> «jefe al 40 %» no suena a transición: suena a que el mezclador está roto. Elige siempre **un**
> estado ganador por prioridad, como arriba.

---

## Escribir la música para que esto funcione

Nada de lo anterior arregla una composición que no está pensada para esto. Tres reglas para el
compositor, no para el código:

- **Misma tonalidad en todas las capas de un mismo tema** (ya se pedía para el *vertical
  layering*: misma longitud y tempo; añade tonalidad a la lista). Si «combate» modulase a otro
  tono, la capa «base» y la capa «combate» chocarían en cuanto sonasen juntas.
- **El punto de bucle va en un compás limpio**, sin nota a medio sonar ni respiración cortada. Si
  el tema tiene una intro que solo debe sonar la primera vez, no la repitas a mano dentro del
  fichero: usa `audio_sound_loop_start()` / `audio_sound_loop_end()`
  ([02 · Novedades — Audio: buses y efectos §4](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md))
  para marcar en runtime dónde empieza el tramo que se repite.
- **Instrumentación reservada por capa.** Si el bajo suena tanto en «base» como en «combate»,
  apagar «combate» deja un hueco de bajo audible en vez de una simple bajada de intensidad. Cada
  capa debe aportar instrumentos que nadie más toca: percusión y metales en «combate», cuerdas y
  arpegios en «melodía», batería y bajo (siempre presentes) en «base».

---

## Las trampas

| Trampa | Consecuencia |
|---|---|
| Lanzar las capas en frames distintos | Se desincronizan sin remedio |
| Capas de distinta longitud/tempo | Se van separando en cada bucle |
| Crossfade instantáneo (0 ms) | Suena a corte brusco de los 90 |
| Stinger desafinado con la base | Parece un bug de audio |
| Comprimir capas con bucles muy cortos | Penalización de rendimiento; usa sin comprimir |
| Cambiar de tema sin esperar al compás | Corta la frase a mitad; suena a error, no a transición |
| Capas de un mismo tema en tonalidades distintas | Chocan en cuanto suenan juntas |
| Promediar las ganancias de dos estados solapados | La música «tartamudea» entre dos objetivos de fundido |

---

## Ver también

- [02 · Novedades — Audio: buses y efectos](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md) — para procesar las capas con efectos
- [19 · Programación rítmica](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md) — sincronía al compás
- [16 · Señales](./16%20-%20Señales%20y%20desacoplamiento.md) — disparar los cambios desde el estado del juego
- [13 · Audio](../01%20-%20Fundamentos/13%20-%20Audio.md) — lo básico de reproducción
- [13 · 09 — Diseño de sonido y mezcla](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md) — el stinger en el contexto de la mezcla completa, y el checklist de publicación
