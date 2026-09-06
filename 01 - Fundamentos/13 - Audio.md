# 13 · Audio

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/audio_play_sound_ext.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Effects/audio_bus_create.htm>
> - `gm-cli manual read "audio_emitter_create"`
> - <https://manual.gamemaker.io/lts/en/Introduction/The_Asset_Browser.htm> (formatos de sonido)
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Debugging/The_Debug_Overlay.htm> (ventana Audio)

---

## 1. Formatos soportados

GameMaker acepta **\*.ogg**, **\*.mp3** y **\*.wav**.

| Formato | Cuándo usarlo | Por qué |
|---|---|---|
| **WAV** | Efectos **cortos** | Se reproducen **al instante**, porque no necesitan decodificación. Archivos más grandes. |
| **MP3 / OGG** | Música y efectos **largos** | Mucho más pequeños, pero tienen **coste de CPU** al decodificar. |

> 💡 Si necesitas procesamiento de audio más complejo, YoYo Games ofrece la **extensión FMOD**: <https://github.com/YoYoGames/GMEXT-FMOD>

---

## 2. Reproducir sonidos

### La forma básica

```gml
audio_play_sound(snd_Explosion, 10, false);
```

Necesitas como mínimo: el **sound asset**, una **prioridad** y si debe **loopear**.

### La forma moderna: `audio_play_sound_ext()`

Idéntica, pero los parámetros se pasan en un **struct**. **Solo la clave `sound` es obligatoria.**

```gml
audio_play_sound_ext({ sound: snd_Explosion });
// prioridad 0, sin loop, todo lo demás por defecto
```

Claves disponibles:

| Clave | Tipo | Por defecto |
|---|---|---|
| `sound` | Sound Asset o Audio Queue ID — **obligatoria** | — |
| `priority` | Real | `0` |
| `loop` | Boolean | `false` |
| `gain` | Real | `1.0` |
| `offset` | Real | el offset del asset |
| `pitch` | Real | `1.0` |
| `listener_mask` | Real | la del emitter / la global |
| `emitter` | Audio Emitter ID | `undefined` |
| `position` | Struct | `undefined` |

El struct `position` acepta:
```gml
{
    x, y, z,
    falloff_ref,
    falloff_max,
    falloff_factor
}
```

**Devuelve:** el **Sound Instance ID** (o `-1` si no se pudo reproducir).

```gml
// Reproducir en un emitter (equivalente a audio_play_sound_on)
var _params =
{
    sound    : snd_disparo,
    priority : 20,
    gain     : 1.2,
    pitch    : 2,
    emitter  : em_entrada_norte
};

audio_play_sound_ext(_params);
```

> 💡 `audio_play_sound_ext()` se comporta como `audio_play_sound()`, `audio_play_sound_at()` o `audio_play_sound_on()` **según las claves que le pases**.

---

## 3. Sonidos vs instancias de sonido («voces»)

Este es el concepto clave del audio en GameMaker.

```gml
var _id = audio_play_sound(snd_Explosion, 10, false);
```

`_id` es una **instancia de sonido** (también llamada «voz»). Puedes usar ese ID para cambiar sus propiedades **solo de esa reproducción concreta**.

Si en cambio pasas el **sound asset** a las funciones, cambias la propiedad a nivel de **asset** (afecta a todas las reproducciones futuras).

```
┌────────────────────────────────────────┐
│  Nivel de ASSET                        │  audio_play_sound(snd_X, ...)
│    ↓                                   │
│  Nivel de EMITTER (si lo hay)          │
│    ↓                                   │
│  Nivel de INSTANCIA (la "voz")         │  audio_sound_gain(_id, ...)
│    ↓                                   │
│  Nivel de BUS (efectos)                │
└────────────────────────────────────────┘
```

Dependiendo de la propiedad, cada nivel actúa como **multiplicador** o **sobrescribe** el valor del nivel anterior.

> 💡 **Los parámetros opcionales de `audio_play_sound*()` fijan el valor a nivel de instancia.**

### El límite de voces

El número máximo de instancias de sonido simultáneas es **128 por defecto**. Se cambia con:

```gml
audio_channel_num(256);
```

> ⚠️ Superar el límite significa que algunos sonidos **no se reproducirán** (la prioridad decide cuáles se descartan).

---

## 4. Propiedades de audio

| Propiedad | Es | Por defecto |
|---|---|---|
| **Gain** | Multiplicador de volumen | En el asset: el valor del deslizador «Volume» del Sound Editor. En los demás niveles: `1` |
| **Pitch** | Multiplicador de tono | `1` en todos los niveles |
| **Offset / Track Position** | Punto del track por donde empieza | `0`. **Sobrescribe** el valor del asset |
| **Listener Mask** | Máscara de bits de qué *listeners* lo oyen | `1` (`0x01`) = el listener por defecto |

```gml
// A nivel de instancia
audio_sound_gain(_id, 0.5, 0);          // (sonido, ganancia, tiempo_en_ms)
audio_sound_pitch(_id, 1.2);
audio_sound_set_track_position(_id, 2.5);
audio_sound_set_listener_mask(_id, 1);

// Leer
audio_sound_get_gain(_id);
audio_sound_get_pitch(_id);
audio_sound_get_track_position(_id);
audio_sound_get_listener_mask(_id);
```

### Conversión lineal ↔ decibelios

```gml
var _db  = lin_to_db(0.5);    // ganancia lineal → dB
var _lin = db_to_lin(-6);     // dB → ganancia lineal
```

> 💡 Los buses de audio trabajan en **dB**. Para un fundido suave y natural, convierte primero.

---

## 5. Loop (bucle)

Un sonido en bucle va desde su **inicio** hasta su **final** por defecto. Puedes cambiar ambos puntos **incluso mientras suena**.

```gml
// Al reproducir
var _motor = audio_play_sound(snd_motor, 100, true);

// O después
audio_sound_loop(_motor, true);

// Puntos de bucle
audio_sound_loop_start(_motor, 1.0);   // segundo 1
audio_sound_loop_end(_motor, 3.5);     // segundo 3.5

// Leer
audio_sound_get_loop(_motor);
audio_sound_get_loop_start(_motor);
audio_sound_get_loop_end(_motor);
```

> ⚠️ **El final del bucle DEBE estar después del inicio.** La única excepción es el valor `0.0`, que marca el final del sonido (equivale a `audio_sound_length()`).

**Caso de uso típico — música con intro que no se repite:**

```gml
var _musica = audio_play_sound(snd_boss, 100, true);
audio_sound_loop_start(_musica, 4.0);   // la intro (0-4s) suena una vez
audio_sound_loop_end(_musica, 0.0);     // 0.0 = hasta el final del track
```

---

## 6. Audio 3D: emitters y listeners

### Emisores (emitters)

Un **emitter** es un punto en el espacio desde el que sale el sonido.

```gml
s_emit = audio_emitter_create();
```

Valores por defecto al crearlo:
- Gain y pitch de `1`
- Listener mask: solo el listener por defecto (`1`)
- Posición `(0, 0, 0)`
- Velocidad `0` (vx = vy = vz = 0)

> ⚠️ **Los emitters son un recurso dinámico**: deben liberarse con `audio_emitter_free()` o tendrás **memory leak**.

```gml
// Create
em_pasos = audio_emitter_create();

// Step: moverlo con el jugador
audio_emitter_position(em_pasos, x, y, 0);

// Clean Up
audio_emitter_free(em_pasos);
```

### Listeners (oyentes)

Definen desde dónde se escucha. Normalmente, la cámara o el jugador.

```gml
audio_listener_position(x, y, 0);
audio_listener_orientation(...);
audio_listener_set_position(...);
audio_listener_set_orientation(...);
```

> 📖 **Con una cámara 3D de verdad** (no solo `z = 0`), `audio_listener_orientation()` se alimenta
> cada frame con la dirección de la cámara (destino − ojo, normalizada) y el vector «arriba»;
> ejemplo completo, con el porqué de cada paso, en
> [04 · 29 §7 bis — Audio en 3D](../04%20-%20Recetas%20por%20género/29%20-%203D%20en%20GameMaker.md).

### Falloff (atenuación por distancia)

```gml
audio_emitter_falloff(em, ref_dist, max_dist, factor);
audio_falloff_set_model(modelo);
```

```gml
// Create del jugador
em_voz = audio_emitter_create();
audio_emitter_falloff(em_voz, 64, 400, 1);
//                             ↑    ↑    ↑
//                     distancia  máx   curva
//                     de ref.
```

### Reproducir en un emitter

```gml
audio_play_sound_on(em_pasos, snd_paso, false, 10);
```

> ⚠️ **Los emitters añaden OTRO nivel** para gain, pitch y listener mask.

---

## 7. Audio buses y efectos

### Buses

Un **bus de audio** es un canal por el que pasan los sonidos, y al que puedes aplicar **efectos**.

```gml
mi_bus = audio_bus_create();
```

> 💡 Un bus creado por el usuario es **recogido por el recolector de basura** cuando no tiene referencias y se destruyen sus emitters vinculados. **No hay función `destroy`**: es deliberado.

```gml
emisor1      = audio_emitter_create();
emisor1_bus  = audio_bus_create();

audio_emitter_bus(emisor1, emisor1_bus);

audio_play_sound_on(emisor1, snd_Ambiente, true, 100);
```

**Orden de procesado:** el sonido pasa primero por los efectos del bus del emitter (`emisor1_bus`) y **después** por los del bus principal (`audio_bus_main`).

```
Emitter → Bus del emitter → audio_bus_main → Salida
```

### Efectos

Los efectos (reverb, eco, delay…) se crean con `audio_effect_create()` y se asignan a uno de los **slots de efectos** de un bus.

El bus al que siempre puedes asignar efectos es el principal: **`audio_bus_main`**.

```gml
// Create del controlador de audio
global.bus_musica = audio_bus_create();
global.bus_efectos = audio_bus_create();

// Crear un efecto de reverb
var _reverb = audio_effect_create(AUDIO_EFFECT_REVERB1);   // nombre ilustrativo
_reverb.decay = 0.8;   // el efecto es un struct; sus parámetros son propiedades (dependen del tipo)

// Asignarlo al slot 0 del bus de música
global.bus_musica.effects[0] = _reverb;   // el bus es un struct; effects es un array fijo de 8
```

> 📖 **Nombres exactos de las constantes y parámetros:** consúltalos en la sección **Audio Effects** del manual, porque dependen del tipo de efecto. Verifica antes de escribir.

### Volúmenes de mezclador (patrón típico)

```gml
// Menú de opciones: el jugador baja la música al 60%
var _ganancia_musica = global.volumen_musica;           // 0..1
global.bus_musica.gain = _ganancia_musica;              // gain es una PROPIEDAD del struct bus

// O en dB, más natural para el oído
global.bus_musica.gain = db_to_lin(-12);
```

---

## 8. Audio groups

Todos los sonidos (salvo los **streamed**) pertenecen a un **audio group**. Los grupos se pueden cargar y descargar en bloque.

```gml
audio_group_load(audiogroup_nivel1);
audio_group_unload(audiogroup_nivel1);
audio_group_is_loaded(audiogroup_nivel1);

audio_group_set_gain(audiogroup_nivel1, 0.8, 0);
audio_group_get_gain(audiogroup_nivel1);
```

> Por defecto todos los sonidos van al grupo **`audiogroup_default`**.

**Por qué importa:** en consolas y móviles con memoria limitada, cargar solo el grupo del nivel actual es la diferencia entre que quepa o no.

---

## 9. Audio en streaming

Para archivos `.ogg` grandes (música larga), cárgalos como **stream** en lugar de en memoria:

```gml
// Create
stream_musica = audio_create_stream("musica/boss_theme.ogg");

// Reproducir
audio_play_sound(stream_musica, 100, true);

// Clean Up
audio_destroy_stream(stream_musica);
```

> 💡 Los sonidos en streaming **no** pertenecen a ningún audio group.

---

## 10. Sincronización: sync groups

Para audio que deba sonar **perfectamente sincronizado a nivel de muestra** (por ejemplo, capas de una misma pista que se activan y desactivan), GameMaker tiene **sync groups**.

```gml
var _grupo = audio_create_sync_group(...);
// ... añadir sonidos al grupo ...
audio_destroy_sync_group(_grupo);
```

> 📖 Ver **Audio Synchronisation** en el manual para la API completa.

---

## 11. Audio en Web (HTML5 / GX.games)

El motor de audio en web requiere **Web Audio**, y el contexto puede **no estar corriendo** o **detenerse** mientras juegas (los navegadores lo pausan sin interacción del usuario).

**Dos formas de detectar el cambio:**

```gml
// A. Función
if (!audio_system_is_available())
{
    // pausar música en bucle, etc.
}
```

```gml
// B. Async System event
var _tipo = async_load[? "event_type"];

if (_tipo == "audio_system_status")
{
    var _estado = async_load[? "status"];   // "available" | "unavailable"

    if (_estado == "available")
    {
        // reanudar música en bucle
    }
    else
    {
        // pausar
    }
}
```

> ⚠️ Este evento se dispara en **todas** las plataformas, pero en todas menos HTML5 **solo una vez** al inicio, cuando se inicializa el motor de audio.

Para comprobar si un sonido se puede reproducir: `audio_sound_is_playable(snd)`.

---

## 12. Manejo de errores

| Situación | Comportamiento |
|---|---|
| Función que recibe un **Sound Asset** o **Audio Sync Group ID** inválido | ⚠️ **Error FATAL (crashea el juego)** |
| Función que recibe un **Sound Instance ID** inválido (el sonido ya no suena) | ✅ Solo imprime un mensaje en el Output Log; **no crashea** |
| Valores inválidos (por ejemplo en `audio_falloff_set_model`) | ⚠️ **Error FATAL** |
| Operación inválida (grabar con un dispositivo ya activo) | ⚠️ **Error FATAL** |

Puedes cambiar los errores fatales por mensajes de log:

```gml
audio_throw_on_error(true);
// El juego continúa en situaciones que antes lo crasheaban
// ⚠️ El efecto del error puede seguir causando bugs
```

> ⚠️ En **HTML5** la mayoría de errores simplemente imprimen un mensaje en el Output Log.

---

## 13. Depuración de audio

```gml
audio_debug(true);   // abre la ventana Audio del Debug Overlay (false la cierra)
```

La ventana **Audio** del Debug Overlay muestra:
- Un **gráfico** con el buffer de salida más reciente del hilo de audio (la señal final que se envía al dispositivo).
- Una **lista** de todas las fuentes de sonido que suenan o podrían sonar, coloreadas por estado:

| Color | Estado |
|---|---|
| **Blanco** | Suena ahora mismo |
| **Rojo** | Ha terminado |
| **Amarillo** | En pausa |
| **Magenta** | Preparándose (transitorio, milisegundos) |
| **Cian** | Deteniéndose (transitorio, milisegundos) |

Columnas: `source`, `buffer`, `syncSource`, `numQueued`, `gain` (como valor de 16 bits, 0-65535), `name`, `pos` (posición en frames, en hex).

> 💡 Es la forma más rápida de diagnosticar «¿por qué se me acumulan 40 sonidos?».

---

## 14. Ejemplo completo: gestor de audio

```gml
// ═══════════ Script: scr_audio (scope global) ═══════════

/// @description Inicializa el sistema de audio del juego.
///              Llamar una sola vez al arrancar.

// Buses
global.bus_master  = audio_bus_main;      // el bus principal, siempre existe
global.bus_musica  = audio_bus_create();
global.bus_efectos = audio_bus_create();

global.volumen_musica  = 0.7;
global.volumen_efectos = 1.0;
```

```gml
// ═══════════ obj_audio (persistente) ═══════════

// ─── Create ───
// Patrón singleton: solo queremos uno
if (instance_number(obj_audio) > 1)
{
    instance_destroy();
    exit;
}
persistent = true;

// Emitter que sigue al jugador
em_jugador = audio_emitter_create();
audio_emitter_falloff(em_jugador, 64, 512, 1);

// Música actual
musica_actual = -1;
musica_asset  = noone;

// ─── Step ───
// El emitter sigue al jugador
if (instance_exists(obj_jugador))
{
    audio_emitter_position(em_jugador, obj_jugador.x, obj_jugador.y, 0);
}

// ─── Clean Up ───
// ⚠️ Los emitters SON recursos dinámicos: hay que liberarlos
audio_emitter_free(em_jugador);
if (musica_actual != -1)
{
    audio_stop_sound(musica_actual);
    musica_actual = -1;
}
```

```gml
// ═══════════ Funciones públicas (Script: scr_audio) ═══════════

/// @function         sfx(sonido, [gain], [pitch])
/// @param {Asset.GMSound} sonido  El sonido a reproducir
/// @param {Real} [gain]           Multiplicador de volumen (1 por defecto)
/// @param {Real} [pitch]          Multiplicador de tono (1 por defecto)
/// @description      Reproduce un efecto de sonido con variación aleatoria
///                   para evitar la monotonía al repetirlo muchas veces.
function sfx(_sonido, _gain = 1, _pitch = 1)
{
    if (!audio_system_is_available()) { return -1; }

    // Pequeña variación de tono: evita el "efecto ametralladora"
    var _pitch_final = _pitch * random_range(0.92, 1.08);

    return audio_play_sound_ext({
        sound  : _sonido,
        gain   : _gain * global.volumen_efectos,
        pitch  : _pitch_final,
        priority : 10
    });
}

/// @function         sfx_posicional(sonido, x, y, [gain])
/// @description      Reproduce un efecto en una posición del mundo (3D).
function sfx_posicional(_sonido, _x, _y, _gain = 1)
{
    if (!audio_system_is_available()) { return -1; }

    return audio_play_sound_ext({
        sound    : _sonido,
        gain     : _gain * global.volumen_efectos,
        pitch    : random_range(0.95, 1.05),
        priority : 5,
        position : { x: _x, y: _y, z: 0,
                     falloff_ref: 64, falloff_max: 512, falloff_factor: 1 }
    });
}

/// @function         musica_poner(sonido)
/// @description      Cambia la música con fundido cruzado.
function musica_poner(_sonido)
{
    if (musica_asset == _sonido) { return; }   // ya suena

    musica_asset = _sonido;

    // Parar la anterior
    if (musica_actual != -1 && audio_is_playing(musica_actual))
    {
        audio_sound_gain(musica_actual, 0, 800);
        var _vieja = musica_actual;
        call_later(0.8, time_source_units_seconds, function()
        {
            audio_stop_sound(_vieja);
        });
    }

    // Empezar la nueva
    musica_actual = audio_play_sound_ext({
        sound  : _sonido,
        loop   : true,
        gain   : 0,
        priority : 100
    });

    // Subir el volumen progresivamente (fundido de entrada)
    audio_sound_gain(musica_actual, global.volumen_musica, 1200);
}

/// @function         audio_aplicar_volumen()
/// @description      Aplica los volúmenes de las opciones del jugador.
function audio_aplicar_volumen()
{
    global.bus_musica.gain  = global.volumen_musica;    // gain es propiedad del struct bus
    global.bus_efectos.gain = global.volumen_efectos;
}
```

```gml
// ═══════════ Uso desde el juego ═══════════

// Disparar
sfx(snd_disparo);

// Explosión en una posición concreta
sfx_posicional(snd_explosion, other.x, other.y, 0.9);

// Cambiar de música al entrar en la zona del jefe
musica_poner(snd_boss_theme);

// El jugador baja la música en el menú de opciones
global.volumen_musica = 0.4;
audio_aplicar_volumen();
```

**Por qué está bien:**
- **Un solo sitio** controla todo el audio.
- La variación aleatoria de pitch evita la monotonía en sonidos repetitivos.
- El **fundido cruzado** hace que los cambios de música no sean bruscos.
- Los volúmenes se aplican en **buses**, no sonido a sonido.
- Se **libera el emitter** en Clean Up (recurso dinámico).
- Se comprueba `audio_system_is_available()` (crítico en web).

---

## Resumen

1. **WAV** para efectos cortos; **MP3/OGG** para música y efectos largos.
2. Distingue **sound asset** (afecta a todas las reproducciones futuras) de **sound instance / voz** (afecta solo a esa).
3. El límite de voces simultáneas es **128** por defecto (`audio_channel_num()`).
4. Propiedades: **gain** (multiplicador), **pitch** (multiplicador), **offset** (sobrescribe), **listener mask** (bitmask).
5. Los **puntos de loop** se pueden cambiar **mientras suena**. `loop_end = 0.0` = hasta el final.
6. **Emitters** = de dónde sale el sonido; **listeners** = desde dónde se oye; **falloff** = cómo se atenúa. ⚠️ Libéralos con `audio_emitter_free()`.
7. **Buses**: el sonido pasa por el bus del emitter y luego por `audio_bus_main`. Los **efectos** van en slots de bus.
8. Los **audio groups** permiten cargar/descargar en bloque (clave en consolas y móvil).
9. ⚠️ En **Web** el contexto de audio puede pausarse: detecta con `audio_system_is_available()` o el Async System event.
10. ⚠️ Un **Sound Asset inválido crashea el juego**; un **Sound Instance ID inválido** solo avisa. `audio_throw_on_error(true)` suaviza los fatales.
