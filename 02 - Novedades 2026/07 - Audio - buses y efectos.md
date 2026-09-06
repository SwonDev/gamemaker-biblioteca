# Audio: buses, efectos y nuevas funciones (LTS 2026.0)

---

## 1. Novedades de un vistazo

| Novedad | Qué es |
|---|---|
| `audio_play_sound()` con argumentos extra | gain, offset, pitch y listener mask directamente al reproducir |
| `audio_play_sound_ext()` | lo mismo pero pasando un **struct** |
| **Audio Loop Points** en runtime | definir en código qué trozo del sonido se repite |
| **Audio Effects** a través de **Audio Buses** | 12 efectos procesados en buses |
| Efectos como **Parameter Tracks en Sequences** | animar efectos desde una sequence |
| Evento **Audio Playback Ended** | se dispara cuando termina cualquier audio reproducido |

---

## 2. `audio_play_sound()` — nuevos argumentos opcionales

### 2.1 Firma

```gml
audio_play_sound(index, priority, loop, [gain], [offset], [pitch], [listener_mask]);
```

| Argumento | Tipo | Descripción |
|---|---|---|
| `index` | Sound Asset o Audio Queue ID | el sonido a reproducir |
| `priority` | Real | prioridad de canal (más alto = más prioritario) |
| `loop` | Bool | si repite |
| `gain` | Real | **opcional**, por defecto `1` |
| `offset` | Real | **opcional**, segundos desde donde empezar; se clampea a la duración; por defecto el offset del asset |
| `pitch` | Real | **opcional**, multiplicador, positivo; valores ≤ 0 se recortan al mínimo positivo; por defecto `1` |
| `listener_mask` | Real | **opcional**, bitmask; en HTML5 no tiene efecto (no soporta más de un listener) |

Devuelve el **Sound Instance ID** (o `-1` si no se pudo reproducir).

### 2.2 Por qué importa

Antes, si querías gain y pitch tenías que reproducir y **luego** llamar a `audio_sound_gain()` y `audio_sound_pitch()`, y eso podía causar un **retardo no deseado** en el cambio. Ahora las propiedades se aplican **inmediatamente**, en el momento de empezar la reproducción.

### 2.3 Las propiedades se MULTIPLICAN por las del asset

Este es el detalle que más confunde:

> Las propiedades de instancia se multiplican por su valor correspondiente en el **sound asset**.

```gml
audio_sound_gain(snd_explosion, 0.7);              // gain del ASSET = 0.7
audio_sound_set_track_position(snd_explosion, 2);   // offset del ASSET = 2 s

// Instancia 1: gain de instancia 0.5, sin offset
audio_play_sound(snd_explosion, 10, false, 0.5);
// → empieza en 2 s (offset del asset) y se oye con gain 0.5 * 0.7 = 0.35

// Instancia 2: gain de instancia 1, offset 0
audio_play_sound(snd_explosion, 20, false, 1, 0);
// → el offset proporcionado SOBREESCRIBE el del asset; empieza desde el principio
//   y se oye con gain 1 * 0.7 = 0.7
```

### 2.4 Ejemplos

```gml
// Uso básico
if (hp <= 0)
{
    vidas -= 1;
    audio_play_sound(snd_muerte_jugador, 10, false);
}

// Con gain y pitch: sonido de despedida más agudo y algo más alto
if (bbox_left > room_width)
{
    audio_play_sound(snd_adios, 10, false, 1.1, 0, 2);
    //                                     gain offset pitch
}
```

### 2.5 Para cambiar valores DESPUÉS de empezar

| Propiedad | Función |
|---|---|
| gain | `audio_sound_gain()` |
| offset | `audio_sound_set_track_position()` |
| pitch | `audio_sound_pitch()` |
| listener mask | `audio_sound_set_listener_mask()` |

---

## 3. `audio_play_sound_ext()` — parámetros como struct

### 3.1 Firma y claves

```gml
audio_play_sound_ext(params);
// params: Struct
// devuelve: Sound Instance ID (o -1)
```

**La única clave obligatoria es `sound`.** Según las claves que pases, la función se comporta como `audio_play_sound()`, `audio_play_sound_at()` o `audio_play_sound_on()`.

| Clave | Tipo | Por defecto |
|---|---|---|
| `sound` | Sound Asset o Audio Queue ID | **requerido** |
| `priority` | Real | `0` |
| `loop` | Bool | `false` |
| `gain` | Real | `1.0` |
| `offset` | Real | el offset del asset |
| `pitch` | Real | `1.0` |
| `listener_mask` | Real | el del emitter / el global |
| `emitter` | Audio Emitter ID | `undefined` |
| `position` | Struct | `undefined` |
| ├─ `x`, `y`, `z` | Real | — |
| ├─ `falloff_ref` | Real | — |
| ├─ `falloff_max` | Real | — |
| └─ `falloff_factor` | Real | — |

### 3.2 Ejemplos

```gml
// 1) Básico, equivalente a audio_play_sound()
audio_play_sound_ext({ sound: snd_ambiente });
```

```gml
// 2) Sobre un emitter, equivalente a audio_play_sound_on()
var _params =
{
    sound:   snd_disparo,
    priority: 20,
    gain:    1.2,
    pitch:   2,
    emitter: em_entrada_norte
};
audio_play_sound_ext(_params);
```

```gml
// 3) En una posición del espacio 3D, equivalente a audio_play_sound_at()
var _params =
{
    sound: snd_disparo,
    pitch: 1.1,
    position:
    {
        x: 100,
        y: 100,
        z: 20
    }
};
audio_play_sound_ext(_params);
```

### 3.3 Cuándo usar `_ext()`

- Cuando tienes **muchos** parámetros y el orden de argumentos posicionales se vuelve ilegible.
- Cuando **construyes los parámetros dinámicamente** (desde datos, desde un fichero, según el arma, etc.).
- Cuando quieres una **función helper** propia que reciba variaciones.

```gml
/// @function sfx(_sonido, _ganancia, _tono)
function sfx(_sonido, _ganancia = 1, _tono = 1)
{
    return audio_play_sound_ext({
        sound:    _sonido,
        priority: 10,
        gain:     _ganancia * global.volumen_sfx,
        pitch:    _tono * random_range(0.95, 1.05)   // variación para que no suene robótico
    });
}

// Uso
sfx(snd_impacto, 0.8);
sfx(snd_moneda, 1.0, 1.2);
```

---

## 4. Audio Loop Points

Permiten definir **en runtime** qué sección de un sonido se repite, en vez de repetir el fichero entero.

Caso de uso clásico: una pista de música con una intro que solo debe sonar la primera vez.

```gml
// Definir el tramo que se repite
// Intro de 0 a 4 s, luego bucle de 4 a 32 s: son DOS funciones, no una
audio_sound_loop_start(snd_musica_nivel, 4);
audio_sound_loop_end(snd_musica_nivel, 32);
audio_play_sound(snd_musica_nivel, 10, true);
```

```gml
// Volver a repetir el fichero entero: inicio 0, fin 0 (= final del sonido)
audio_sound_loop_start(snd_musica_nivel, 0);
audio_sound_loop_end(snd_musica_nivel, 0);
```

> ✅ Firmas verificadas contra `GmlSpec.xml`: `audio_sound_loop_start(index, time)` y `audio_sound_loop_end(index, time)`. **No existe** `audio_sound_loop_points`: son dos funciones. Detalle en el manual:
> https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Loop_Points/Audio_Loop_Points.htm

---

## 5. Audio Effects y Audio Buses

### 5.1 Concepto: todo pasa por un bus

> **Todos los sonidos en GameMaker se reproducen a través de "buses".** Hay un bus principal, y todos los buses personalizados acaban en él.

- Puedes aplicar efectos al **bus principal** → afectan a **todo el audio**.
- Puedes crear un **bus personalizado** y aplicarle efectos → afectan solo a lo que se rutee a ese bus.
- ⚠️ **Los buses personalizados solo se pueden usar con Audio Emitters.** El audio 2D, el 3D y el de emitter acaban siempre en el bus principal.

### 5.2 Efectos disponibles

Según el blog oficial:

> Bitcrusher, Delay, Gain, High Pass Filter, Low Pass Filter, Parametric EQ, Peak EQ, High Shelf, Low Shelf, Reverb, Tremolo, Compressor

Y según el enum `AudioEffectType` del manual:

| Constante | Efecto | Qué hace |
|---|---|---|
| `AudioEffectType.Bitcrusher` | Bitcrusher | Distorsión en 4 etapas: **Gain → Clipper → reducción de sample rate → reducción de resolución** |
| `AudioEffectType.Delay` | Delay | Retrasa la señal y la mezcla con la original |
| `AudioEffectType.Gain` | Ganancia | Amplifica por un factor |
| `AudioEffectType.HPF2` | Filtro paso alto | Deja pasar frecuencias altas, muta las bajas por debajo del *cutoff* |
| `AudioEffectType.LPF2` | Filtro paso bajo | Deja pasar bajas, muta altas por encima del *cutoff* |
| `AudioEffectType.Reverb1` | Reverb | Mezcla la original con una versión reverberada; permite *dampening* de agudos |
| `AudioEffectType.Tremolo` | Tremolo | Usa un **LFO** para modular parámetros a frecuencia de audio; cambia la amplitud |
| `AudioEffectType.EQ` | Parametric EQ | Ecualizador paramétrico: combina paso alto, paso bajo, **4 peak EQs**, high-shelf y low-shelf |
| `AudioEffectType.PeakEQ` | Peak EQ | Crea un pico o un valle con una ganancia alrededor de una frecuencia central |
| `AudioEffectType.HiShelf` | High Shelf | Pasa todas las frecuencias, pero sube/baja las que están **por encima** de la frecuencia de estantería |
| `AudioEffectType.LoShelf` | Low Shelf | Igual, pero con las que están **por debajo** |
| `AudioEffectType.Compressor` | Compresor | Reduce el rango dinámico (**compresión descendente**: baja el volumen de lo que supera el umbral; lo que está por debajo no se toca). Los canales están **enlazados**, para que no se mueva la imagen estéreo |

### 5.3 Añadir efectos al bus principal

```gml
// Create Event de un objeto de control de audio

// 1) Crear el efecto
var _ef_reverb = audio_effect_create(AudioEffectType.Reverb1);

// 2) Ajustar sus parámetros ANTES de asignarlo
_ef_reverb.size = 0.6;
_ef_reverb.mix  = 0.5;   // cuánto se oye el efecto, 0-1 (similar a lerp)

// 3) Asignarlo a un slot del array de efectos del bus principal
audio_bus_main.effects[0] = _ef_reverb;
```

> **Buena práctica del manual:** asigna el efecto al array **después** de configurar sus parámetros. Así evitas la transición audible de "sin efecto" a "efecto aplicado".

### 5.4 Reglas del array de efectos

- Un bus admite un **máximo de 8 efectos** en su array `effects`.
- Para **quitar** un efecto, pon su slot a `undefined`.
- Asignar un efecto a un slot es lo que lo **activa**.

```gml
// Quitar el efecto del slot 0
audio_bus_main.effects[0] = undefined;
```

### 5.5 Bypass

```gml
// Saltar UN efecto concreto
audio_bus_main.effects[0].bypass = true;

// Saltar TODOS los efectos del bus
audio_bus_main.bypass = true;
```

Con bypass activo, lo que sale del bus/efecto es exactamente lo que entra: la entrada es la salida.

### 5.6 Buses personalizados y emitters

```gml
// Create Event
emitter     = audio_emitter_create();   // emitter
emitter_bus = audio_bus_create();       // bus propio
audio_emitter_bus(emitter, emitter_bus);  // el emitter sale por ese bus

// Ahora los efectos del emitter_bus se aplican a lo que se emita por ahí
audio_play_sound_on(emitter, snd_pasos, false, 10);
```

- Puedes asignar **tantos emitters como quieras** a un mismo bus.
- Todo lo que salga de un bus personalizado **acaba en el bus principal**, así que se le aplican también los efectos de este.
  - Ejemplo: delay en el bus del emitter + reverb en el principal → el audio del emitter se oye con **delay + reverb**; el audio reproducido directo al principal solo con **reverb**.
- Para leer el bus asignado a un emitter: `audio_emitter_get_bus()`.

### 5.7 Asignar el mismo efecto a varios sitios

Un mismo struct de efecto puede asignarse a varios slots (del mismo bus o de buses distintos):

```gml
ef_lpf = audio_effect_create(AudioEffectType.LPF2, {cutoff: 300, q: 1.5});

bus_1.effects[0] = ef_lpf;
bus_1.effects[4] = ef_lpf;
bus_2.effects[0] = ef_lpf;
```

Cada asignación crea una **instancia nueva** del efecto. La analogía del manual: el struct devuelto por `audio_effect_create()` es el "objeto" y cada asignación crea una "instancia". Cada slot tiene la suya.

> Si cambias una variable de `ef_lpf`, el cambio se refleja en **los tres slots**.

### 5.8 Ejemplo completo: "bajo el agua"

```gml
// Create Event — objeto de control de audio

// Crear bus para efectos de entorno
bus_ambiente = audio_bus_create();

// Filtro paso bajo: el agua se come los agudos
ef_lpf = audio_effect_create(AudioEffectType.LPF2);
ef_lpf.cutoff = 800;
ef_lpf.q      = 0.7;

// Reverb para sensación de espacio cerrado
ef_reverb = audio_effect_create(AudioEffectType.Reverb1);
ef_reverb.size = 0.8;
ef_reverb.mix  = 0.4;

// Asignar (después de configurar)
bus_ambiente.effects[0] = ef_lpf;
bus_ambiente.effects[1] = ef_reverb;

// Step Event — según si el jugador está sumergido
audio_bus_main.bypass = !sumergido;
```

### 5.9 Ejemplo: transición a menú de pausa

```gml
// Al pausar: metemos un paso bajo suave para que la música suena "apagada"
ef_menu = audio_effect_create(AudioEffectType.LPF2);
ef_menu.cutoff = 1200;

audio_bus_main.effects[0] = ef_menu;

// Al despausar: lo quitamos
audio_bus_main.effects[0] = undefined;
```

### 5.10 Efectos en Sequences

Los efectos de audio también están disponibles como **Parameter Tracks en Sequences**, así que puedes animarlos (p. ej. bajar el cutoff progresivamente).

### 5.11 Limitaciones en HTML5

Cuando el target es **HTML5**, buses y efectos quedan limitados en estas situaciones:

- El juego corre en **iOS Safari** (por un bug importante de WebKit).
- El juego corre en un **contexto no seguro** (donde no hay audio worklets), p. ej. acceder por móvil a un juego alojado en local dentro de la misma red.

En esos casos, **las funciones, enums y structs siguen existiendo y no dan error de GML**, pero **no tendrán efecto audible**… con dos excepciones:

- la **ganancia del bus**,
- el **ruteo de buses**.

---

## 6. Evento "Audio Playback Ended"

Evento nuevo de la categoría **Async Events** que se ejecuta cuando **termina de reproducirse cualquier audio**.

Se dispara para los sonidos reproducidos con `audio_play_sound()` y `audio_play_sound_ext()`.

Casos de uso:

- encadenar pistas de música sin huecos;
- reproducir un "eco" justo al terminar un disparo;
- liberar recursos o avanzar un estado cuando un diálogo termina de hablar.

```gml
// Evento Audio Playback Ended
show_debug_message("El audio ha terminado");

// Encadenar la siguiente pista
if (pista_actual == 0)
{
    audio_play_sound(snd_musica_b, 10, false);
    pista_actual = 1;
}
```

---

## 7. Otras notas de audio de 2026.0

- **Errores estrictos de audio**: hay una opción en **Deprecated Behaviours** (Game Options) para restaurar el comportamiento antiguo.
- **`audio_group_load_progress()`**: corregido para que devuelva progreso en los targets donde debe funcionar.
- **Sonidos en stream**: corregido un bug que los asignaba a grupos de audio distintos de "default" cuando no tocaba (Beta 2026.100 R1).
- El **Sound Editor** ha recibido una actualización de sus propiedades para reflejar mejor cómo se usan al generar los ficheros de audio finales.
- Si **YYAL** no carga, la IDE avisa en lugar de crashear, pero **no habrá previsualización de audio** en el Sound Editor.

---

## 8. Referencia rápida de funciones

**Buses**

- `audio_bus_create()`
- `audio_bus_main` (struct del bus principal)
- `audio_bus_get_emitters()`
- `audio_bus_clear_emitters()`

**Efectos**

- `audio_effect_create(tipo, [params])`
- `AudioEffectType` (enum)
- `AudioLFOType` (enum)
- `AudioEffect Struct`

**Emitters + buses**

- `audio_emitter_bus(emitter, bus)`
- `audio_emitter_get_bus(emitter)`

**Utilidades**

- `db_to_lin()` / `lin_to_db()` — convertir entre ganancia lineal y decibelios; el manual recomienda usarlas con el efecto Gain

```gml
// -6 dB expresados como ganancia lineal
var _g = db_to_lin(-6);
```

---

## Fuentes

- Manual: Audio Effects — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Effects/Audio_Effects.htm
- Manual: `AudioEffectType` Enum — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Effects/AudioEffectType.htm
- Manual: `audio_play_sound()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/audio_play_sound.htm
- Manual: `audio_play_sound_ext()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/audio_play_sound_ext.htm
- Manual: Audio Loop Points — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Loop_Points/Audio_Loop_Points.htm
- Manual: Audio Playback Ended — https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Async_Events/Audio_Playback_Ended.htm
- Blog LTS 2026.0 — https://gamemaker.io/en/blog/lts-2026-release
- Release notes 2026.0.0 — https://releases.gamemaker.io/release-notes/2026/0
