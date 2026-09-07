# 24 · Audio avanzado — buffers, colas, sincronía y grabación

> Referencia exhaustiva de **GameMaker LTS 2026** (IDE 2026.0.0.16 · Runtime 2026.0.0.23) de las
> dos familias de la API de audio que el resto de la biblioteca solo nombraba en
> `_API del runtime/API-funciones.md`: **Audio Buffers** (síntesis en tiempo real, streaming
> propio y grabación de micrófono) y **Audio Synchronisation** (sync groups), más el Doppler
> (`audio_emitter_velocity` / `audio_listener_velocity`). **No** cubre reproducción básica,
> voces, audio groups ni streaming de asset (→
> [01 · 13 — Audio](../01%20-%20Fundamentos/13%20-%20Audio.md)), buses ni los 12 efectos DSP (→
> [02 · 07 — Audio: buses y efectos](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md)),
> ni el oficio de mezcla, prioridad y atenuación (→
> [13 · 09 — Diseño de sonido y mezcla](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md)).
> Todas las firmas están verificadas con `python3 _indice/buscar.py` contra el manual oficial LTS.

---

## 1 · Los principios

Cuatro familias resuelven cuatro problemas que **no** se resuelven con `audio_play_sound()`:

| Problema | Familia | Restricción principal |
|---|---|---|
| «Quiero que 4 pistas suenen sin el más mínimo desfase» | **Sync groups** (§2) | Solo audio **comprimido** (`.ogg`/`.mp3`); no en HTML5 |
| «Quiero generar el sonido yo, sin un archivo de por medio» | **Buffer sounds** (§3) | Solo PCM: `buffer_u8` o `buffer_s16`; 1000-48000 Hz |
| «Quiero transmitir audio que no viene de un asset» (red, disco propio, decodificado a mano) | **Play queues** (§4) | No hay duración ni posición de pista; hay que reponer a mano |
| «Quiero capturar el micrófono» | **Grabación** (§5) | No en HTML5; formato/frecuencia los decide la plataforma, no tú |
| «Quiero que algo en movimiento suene con Doppler» | **Doppler** (§6) | Hay que actualizar la velocidad **cada frame**, igual que la posición |

Las cuatro comparten una regla de la casa (ver
[08 · 16 — Buffers](./16%20-%20Buffers.md)): **todo lo que se crea a mano se destruye a mano**.
Un sonido de buffer, una cola o un grupo de sincronía no los recoge el recolector de basura.

> ⚠️ El manual oficial escribe la constante de audio 3D como `audio_3D` (con «D» mayúscula) en
> la prosa de `audio_create_buffer_sound` y `audio_create_play_queue`. El símbolo real del
> runtime es **`audio_3d`**, en minúsculas — verificado con `buscar.py`. Es exactamente el tipo
> de errata que esta biblioteca existe para cazar.

---

## 2 · Sync groups: sincronía a nivel de muestra

Un **sync group** arranca varias pistas **exactamente en el mismo instante** y las mantiene
sincronizadas a nivel de muestra durante toda la reproducción — no solo al empezar, como el
patrón manual de [04 · 26 — Música adaptativa por capas](../04%20-%20Recetas%20por%20género/26%20-%20Música%20adaptativa%20por%20capas.md)
(que depende de lanzar los `audio_play_sound_ext` en el mismo frame y confiar en que no haya
jitter). Con un sync group la sincronía la garantiza el motor, no el timing del `Step`.

**Restricciones que hay que tener claras antes de usarlo:**

1. Las pistas deben ser audio **comprimido**: `.ogg` o `.mp3`. Un `.wav` sin comprimir no vale.
2. **No disponible en HTML5** — todas las páginas del manual lo repiten en cada función.
3. Si `loop = true`, **todas las pistas añadidas después deben tener la misma longitud**;
   si no, el bucle se rompe.
4. Un sync group hay que destruirlo (`audio_destroy_sync_group`) cuando ya no se usa, igual
   que un buffer o un emisor: no lo libera el recolector de basura.

### Las 11 funciones

| Función | Devuelve | Qué hace |
|---|---|---|
| `audio_create_sync_group(loop)` | `Id.AudioSyncGroup` | Crea el grupo. `loop` es `true`/`false`. |
| `audio_play_in_sync_group(group_index, sound_index)` | `Real` | Añade un sonido comprimido al grupo. No lo reproduce todavía. |
| `audio_start_sync_group(group_index)` | — | Arranca todas las pistas del grupo a la vez. |
| `audio_stop_sync_group(group_index)` | — | Detiene el grupo. |
| `audio_pause_sync_group(group_index)` | — | Pausa sin perder la posición. |
| `audio_resume_sync_group(group_index)` | — | Reanuda desde donde se pausó. |
| `audio_sync_group_get_track_pos(group_index)` | `Real` | Posición de reproducción, en **segundos**. |
| `audio_sync_group_is_playing(group_index)` | `Bool` | Si el grupo está sonando. |
| `audio_sync_group_is_paused(group_index)` | `Bool` | Si el grupo está en pausa. |
| `audio_sync_group_debug(group_index)` | — | Superposición de depuración (`-1` la desactiva). |
| `audio_destroy_sync_group(group_index)` | — | Libera el grupo y sus recursos. |

### `audio_play_in_sync_group` devuelve el **orden**, no un id de instancia

El manual es explícito: el valor de retorno es `>= 0` si tiene éxito (el orden del sonido
dentro del grupo: 0 el primero añadido, 1 el segundo…) y `-1` si falla. **No** es el id de
instancia que devuelve `audio_play_sound()`.

> ⚠️ `buscar.py` (que deriva el tipo del `GmlSpec.xml` del runtime) marca el retorno de
> `audio_play_in_sync_group` como `Id.Buffer`. El manual, en cambio, lo describe como un
> `Real` de orden (`0, 1, 2…` o `-1`) — y así es como se usa en la práctica y en el propio
> ejemplo oficial. Documento el comportamiento funcional del manual; el `GmlSpec.xml` parece
> llevar aquí una anotación de tipo heredada e imprecisa.

Para controlar el volumen de una pista concreta del grupo (por ejemplo, para un crossfade),
`audio_sound_gain()` acepta directamente **el asset de sonido** que pasaste a
`audio_play_in_sync_group` — no hace falta guardar ningún id aparte. Eso sí:
`audio_sound_gain(asset, …)` afecta a **todas** las instancias de ese asset que estén sonando
en la room, así que no reutilices el mismo asset como dos capas simultáneas si necesitas
volúmenes independientes.

### Ejemplo práctico: capas de música con sincronía garantizada

Sustituye el patrón «lánzalas todas en el mismo `Step`» de `04 · 26` por esta versión, que no
depende de que el frame no tenga jitter:

```gml
/// @function musica_capas_iniciar(_capas)
/// @description Arranca un array de sonidos COMPRIMIDOS (.ogg/.mp3, misma duración si se van
///              a repetir en bucle) sincronizados a nivel de muestra. Devuelve el id del grupo.
function musica_capas_iniciar(_capas)
{
    var _grupo = audio_create_sync_group(true);

    for (var i = 0; i < array_length(_capas); i++)
    {
        var _orden = audio_play_in_sync_group(_grupo, _capas[i]);
        if (_orden == -1)
        {
            show_debug_message("musica_capas_iniciar: la capa " + string(i) +
                                " no se pudo añadir (¿no está comprimida?)");
        }
    }

    audio_start_sync_group(_grupo);
    return _grupo;
}

/// @function musica_capa_activar(_asset_capa, _activa)
/// @description Sube o baja al instante el volumen de UNA capa del grupo, en 300 ms.
function musica_capa_activar(_asset_capa, _activa)
{
    audio_sound_gain(_asset_capa, _activa ? 1 : 0, 300);
}
```

```gml
// Uso: obj_musica — Create
capas = [snd_musica_base, snd_musica_bateria, snd_musica_lead];
grupo_musica = musica_capas_iniciar(capas);
musica_capa_activar(snd_musica_bateria, false);   // arranca en silencio hasta que haga falta
musica_capa_activar(snd_musica_lead, false);

// obj_musica — cuando empieza el combate
musica_capa_activar(snd_musica_bateria, true);

// obj_musica — Room End / Clean Up
audio_destroy_sync_group(grupo_musica);
```

Para pausar con el menú de pausa (en vez de tocar los buses, como hace
`02 · 07 §5.9`), usa `audio_pause_sync_group(grupo_musica)` /
`audio_resume_sync_group(grupo_musica)`: mantiene la sincronía entre capas al reanudar, cosa
que un `audio_pause_sound` por capa no garantiza igual de bien.

Para un HUD de depuración de audio (además del **Debug Overlay** que ya cubre
`01 · 13 §13`):

```gml
if (global.debug_audio) audio_sync_group_debug(grupo_musica);
else                    audio_sync_group_debug(-1);
```

### Errores clásicos con sync groups

| Síntoma | Causa | Arreglo |
|---|---|---|
| El grupo no suena en el navegador | Sync groups no existen en HTML5 | Usa capas normales con `audio_play_sound_ext` + el patrón de `04 · 26` como *fallback* |
| Al hacer bucle, las capas se desincronizan tras la primera vuelta | Las pistas no tienen **exactamente** la misma duración | Recorta/rellena las pistas en la edición a la muestra exacta |
| `audio_play_in_sync_group` devuelve `-1` | El sonido es `.wav` (no comprimido) | Reexporta a `.ogg` o `.mp3` |
| Fuga de memoria de audio al cambiar de room | No se llamó a `audio_destroy_sync_group` | Destrúyelo en **Room End** o **Clean Up**, igual que un emisor (`01 · 13 §6`) |

---

## 3 · Buffer sounds: síntesis y audio procedural en tiempo real

> 💡 **¿Un agente sin ningún archivo de audio?** Esta sección es la respuesta — la escalera completa de prioridad (síntesis primero, generador externo después, placeholder al final) está en [13 · 09 §8 bis](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#8-bis--un-agente-sin-archivo-de-audio-la-escalera-de-prioridad).

Un **buffer sound** convierte datos que tú mismo escribes en un buffer (ver
[08 · 16 — Buffers](./16%20-%20Buffers.md) para la base) en un sonido reproducible con la API
normal (`audio_play_sound`, `audio_sound_gain`, `audio_sound_pitch`…). No crea un sonido nuevo
en memoria: **apunta** a la posición del buffer donde están los datos, así que:

- El buffer **solo admite PCM sin comprimir**: `buffer_u8` (8 bits, sin signo, silencio = 128)
  o `buffer_s16` (16 bits, con signo, silencio = 0). Nada de `.ogg`/`.mp3` ni `buffer_f32`.
- La frecuencia de muestreo debe estar entre **1000 Hz y 48000 Hz**.
- Los canales se indican con `audio_mono`, `audio_stereo` o `audio_3d` (⚠️ minúscula, ver §1).
- **No modifiques el buffer** después de crear un sonido a partir de él: resultados
  impredecibles. Y no puedes borrar el buffer mientras el sonido siga vivo.

### Las 2 funciones

#### `audio_create_buffer_sound(bufferId, bufferFormat, bufferRate, bufferOffset, bufferLength, bufferChannels)`

Crea el sonido. `bufferOffset` y `bufferLength` están en **bytes** (usa `buffer_sizeof()`,
documentada en `08 · 16`, para no calcular a mano el tamaño por muestra).

**Devuelve:** `Asset.GMSound` — un *handle* de asset, no un índice numérico (ver
`01 - Fundamentos/03 - Handles`: nada de aritmética sobre este valor).

#### `audio_free_buffer_sound(index)`

Libera el sonido creado a partir de un buffer. **Hay que llamarla** antes de borrar el buffer
de origen (`buffer_delete`) y antes de que la variable se pierda, o hay fuga de memoria.

### Ejemplo práctico: sintetizar un tono con envolvente

Una onda cuadrada con ataque y caída cortos (evita el clic de cortar la onda a mitad de ciclo)
sirve para un «pickup» o un «láser» sin depender de ningún archivo:

```gml
/// @function tono_generar(_frecuencia_hz, _duracion_seg, [_amplitud])
/// @description Sintetiza una onda cuadrada mono de 8 bits con envolvente de ataque/caída y
///              la envuelve en un sonido reproducible. Devuelve { sonido, buffer }: hay que
///              liberar los dos con audio_free_buffer_sound() y buffer_delete() cuando acabe.
function tono_generar(_frecuencia_hz, _duracion_seg, _amplitud = 0.6)
{
    var _tasa             = 22050;                       // de sobra para un SFX de 8 bits
    var _muestras         = round(_tasa * _duracion_seg);
    var _muestras_ataque  = round(_tasa * 0.005);        // 5 ms
    var _muestras_caida   = round(_tasa * 0.05);         // 50 ms
    var _muestras_x_ciclo = _tasa / _frecuencia_hz;
    var _mitad_ciclo      = _muestras_x_ciclo / 2;

    var _buffer = buffer_create(_muestras, buffer_fast, 1);   // buffer_fast exige buffer_u8

    for (var i = 0; i < _muestras; i++)
    {
        var _envolvente = 1;
        if (i < _muestras_ataque)                  _envolvente = i / _muestras_ataque;
        else if (i > _muestras - _muestras_caida)  _envolvente = (_muestras - i) / _muestras_caida;

        var _onda  = ((i mod _muestras_x_ciclo) < _mitad_ciclo) ? 1 : -1;   // cuadrada [-1, 1]
        var _valor = 128 + round(_onda * _envolvente * _amplitud * 127);

        buffer_write(_buffer, buffer_u8, clamp(_valor, 0, 255));
    }

    var _sonido = audio_create_buffer_sound(_buffer, buffer_u8, _tasa, 0, _muestras, audio_mono);
    return { sonido: _sonido, buffer: _buffer };
}
```

```gml
// Uso, por ejemplo al recoger una moneda:
var _t = tono_generar(880, 0.15);
audio_play_sound(_t.sonido, 80, false);

// Cuando ya no suena (por ejemplo, en el evento Audio Playback Ended de 02 · 07):
audio_free_buffer_sound(_t.sonido);
buffer_delete(_t.buffer);
```

### Ejemplo práctico: ruido con caída para una explosión sintetizada

Ruido blanco con una envolvente de potencia (el mismo tipo de curva que ya usa el *game feel*
de la biblioteca para que algo se sienta con peso, en vez de un `sin()` — ver
`04 · 15 — Game feel y juice`):

```gml
/// @function ruido_generar(_duracion_seg, [_amplitud])
/// @description Ruido blanco mono de 8 bits con caída exponencial (curva de potencia).
///              Devuelve { sonido, buffer }, a liberar igual que en tono_generar().
function ruido_generar(_duracion_seg, _amplitud = 0.8)
{
    var _tasa     = 22050;
    var _muestras = round(_tasa * _duracion_seg);
    var _buffer   = buffer_create(_muestras, buffer_fast, 1);

    for (var i = 0; i < _muestras; i++)
    {
        var _t          = i / _muestras;
        var _envolvente = power(1 - _t, 3);                       // decae rápido
        var _valor      = 128 + round(irandom_range(-127, 127) * _envolvente * _amplitud);

        buffer_write(_buffer, buffer_u8, clamp(_valor, 0, 255));
    }

    var _sonido = audio_create_buffer_sound(_buffer, buffer_u8, _tasa, 0, _muestras, audio_mono);
    return { sonido: _sonido, buffer: _buffer };
}
```

Cambiar `_duracion_seg` y sembrar `random_set_seed()` antes de llamar da variaciones gratis sin
necesitar un banco de tomas grabadas (comparar con el *round robin* de `13 · 09 §3.2`, que es
la vía recomendada cuando el sonido no es sintético).

### Errores clásicos con buffer sounds

| Síntoma | Causa | Arreglo |
|---|---|---|
| `audio_create_buffer_sound` no da error pero suena a ruido basura | Se usó `buffer_f32` o `buffer_s32` | Solo `buffer_u8` o `buffer_s16` están soportados |
| El sonido se corrompe tras un rato de partida | Se escribió en el buffer después de crear el sonido | No lo toques una vez creado el sonido; genera un buffer nuevo si necesitas otro sonido |
| Fuga de memoria de audio | No se llamó a `audio_free_buffer_sound` antes de perder la variable | Libera el sonido primero, **luego** `buffer_delete` el buffer |
| Clic audible al final del SFX sintetizado | La onda no vuelve a 128/0 antes de cortar | Añade una caída (ver `_muestras_caida` arriba) en vez de cortar en seco |

---

## 4 · Play queues: streaming propio sin huecos

Un **audio queue** reproduce datos de un buffer (o de varios, encadenados) como si fuera un
sonido en streaming, sin pasar por el navegador de assets. Es la vía para reproducir audio que
llega por red, que decodificas tú mismo, o que generas más rápido de lo que cabría en un solo
buffer sound. La cola se controla como cualquier sonido (`audio_play_sound`, `audio_sound_gain`,
pausa…), con una única limitación: **no** se puede leer ni fijar la posición de pista
(`audio_sound_get_track_position` / `audio_sound_set_track_position` no aplican).

### Las 3 funciones

| Función | Devuelve | Qué hace |
|---|---|---|
| `audio_create_play_queue(queueformat, queuerate, queuechannels)` | `Real` (id de cola) | Prepara la cola. Mismos formatos/frecuencias/canales que un buffer sound. |
| `audio_queue_sound(queueindex, bufferid, bufferoffset, bufferlength)` | — | Añade datos de un buffer a la cola. El buffer no se puede borrar hasta liberar la cola. |
| `audio_free_play_queue(queueindex)` | — | Libera la cola. Detiene cualquier sonido que estuviera reproduciéndose desde ella. |

### El evento **Audio Playback** (de las colas — no confundir con *Audio Playback Ended*)

Cuando un audio queue termina de reproducir uno de sus buffers, dispara el evento asíncrono
**Audio Playback**, distinto del evento **Audio Playback Ended** que ya documenta
`02 · 07 §… (Evento "Audio Playback Ended")` para sonidos normales. El `ds_map` de
`async_load` trae:

- `"queue_id"` — la cola que ha terminado de reproducir ese buffer.
- `"buffer_id"` — el buffer que ya no se está reproduciendo (puedes borrarlo o reponerlo).
- `"queue_shutdown"` — `0` en reproducción normal; `1` cuando el evento llega porque se llamó
  a `audio_free_play_queue()`. Con `1`, no encoles nada más.

Como una cola puede formarse de varios buffers, este evento puede dispararse **varias veces**
para la misma cola: una por cada buffer que se agota.

### Ejemplo práctico: encadenar fragmentos sin dejar un hueco de silencio

```gml
// obj_reproductor_streaming — Create
formato_cola      = buffer_s16;
frecuencia_cola   = 44100;
canales_cola      = audio_stereo;
cola              = audio_create_play_queue(formato_cola, frecuencia_cola, canales_cola);
total_fragmentos  = 4;
siguiente_indice  = 0;
buffers_en_cola   = ds_list_create();   // para poder borrarlos cuando el evento avise

/// @function fragmento_encolar(_indice)
/// @description Carga el fragmento PCM crudo _indice desde disco y lo añade a la cola.
function fragmento_encolar(_indice)
{
    var _ruta = "fragmentos/musica_" + string(_indice) + ".raw";   // PCM sin cabecera
    if (!file_exists(_ruta))
    {
        show_debug_message("fragmento_encolar: no existe " + _ruta);
        return;
    }

    var _b = buffer_load(_ruta);
    audio_queue_sound(cola, _b, 0, buffer_get_size(_b));
    ds_list_add(buffers_en_cola, _b);
}

// encola los dos primeros fragmentos por adelantado: si esperas a que el primero
// termine para pedir el segundo, se oye un hueco
fragmento_encolar(0);
fragmento_encolar(1);
siguiente_indice = 2;

sonido_cola = audio_play_sound(cola, 100, false);
```

```gml
// obj_reproductor_streaming — Evento Asíncrono: Audio Playback
if (async_load[? "queue_id"] == cola)
{
    var _buffer_terminado = async_load[? "buffer_id"];
    var _pos = ds_list_find_index(buffers_en_cola, _buffer_terminado);
    if (_pos != -1)
    {
        buffer_delete(_buffer_terminado);
        ds_list_delete(buffers_en_cola, _pos);
    }

    if (async_load[? "queue_shutdown"]) exit;   // ya se llamó a audio_free_play_queue()

    if (siguiente_indice < total_fragmentos)
    {
        fragmento_encolar(siguiente_indice);   // repón lo que se acaba de consumir
        siguiente_indice++;
    }
}
```

```gml
// obj_reproductor_streaming — Clean Up / Room End
audio_free_play_queue(cola);
for (var i = 0; i < ds_list_size(buffers_en_cola); i++)
{
    buffer_delete(buffers_en_cola[| i]);
}
ds_list_destroy(buffers_en_cola);
```

> 💡 Este mismo patrón —encolar por adelantado y reponer al recibir el evento— es el que hace
> falta para reproducir audio que llega **por red** en trozos: en vez de `buffer_load()` desde
> disco, el buffer viene de un `buffer_async_group` o de un socket, y se encola en cuanto llega
> en vez de esperar a tenerlo todo.

### Errores clásicos con play queues

| Síntoma | Causa | Arreglo |
|---|---|---|
| Hueco de silencio entre fragmentos | Se encoló el siguiente fragmento **después** de que el anterior terminara | Encola con antelación (al menos un fragmento por delante, como arriba) |
| `buffer_delete` falla o corrompe el audio | Se borró un buffer que seguía enganchado a la cola | Espera al evento **Audio Playback** con ese `buffer_id` antes de borrarlo |
| El audio se corta al final sin avisar | No se comprobó `"queue_shutdown"` | Trátalo como señal de «no queda nada que reponer», no como un error |
| Se intenta leer `audio_sound_get_track_position(cola)` | Los queues no soportan posición de pista | Lleva tu propia cuenta de fragmentos reproducidos si necesitas un progreso |

---

## 5 · Grabación de micrófono

La grabación de audio funciona en casi todas las plataformas **excepto HTML5**, pero eso no
garantiza que el dispositivo tenga un micrófono disponible: hay que comprobarlo siempre con
`audio_get_recorder_count()` antes de usar el resto de funciones.

> **NOTA del manual:** en el target Opera GX, `audio_get_recorder_count()` **siempre devuelve
> 1**, esté o no haya un micrófono real disponible.

Para el permiso de Android (`RECORD_AUDIO`), no lo repitas aquí: está resuelto en
[04 · 28 — Juegos para móvil (táctil)](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md)
con `os_request_permission("android.permission.RECORD_AUDIO")`. Pide el permiso justo antes de
llamar a `audio_start_recording()`, no al arrancar el juego.

### Las 4 funciones

| Función | Devuelve | Qué hace |
|---|---|---|
| `audio_get_recorder_count()` | `Real` | Nº de fuentes de grabación disponibles (micrófonos, etc.). |
| `audio_get_recorder_info(recorder_index)` | `Id.DsMap` | Nombre, formato, frecuencia y canales de una fuente. **Tú destruyes el mapa.** |
| `audio_start_recording(recorder_index)` | `Real` | Empieza a grabar. El valor devuelto es el **índice de canal** que identifica esta grabación en el evento asíncrono. |
| `audio_stop_recording(channel_index)` | — | Detiene el canal de grabación dado. |

### ⚠️ Discrepancia de traducción en el espejo español

`09 - Manual oficial/manual-lts-2026-es/.../audio_get_recorder_info.md` traduce las **claves**
del `ds_map` que devuelve la función: escribe que el mapa trae `"nombre"`, `"índice"` y
`"canales"`. Esas claves son *literales de GML que el runtime usa tal cual*, no texto de
interfaz — **no se traducen**. Comprobado contra el espejo en inglés
(`manual-lts-2026-en/.../audio_get_recorder_info.md`), las claves reales son:

- `"name"` (no `"nombre"`)
- `"index"` (no `"índice"`)
- `"data_format"` — esta sí coincide en los dos idiomas
- `"sample_rate"` — esta también coincide
- `"channels"` (no `"canales"`)

Quien copie `_info[? "nombre"]` del manual en español obtendrá `undefined` en tiempo real. El
código de este documento usa siempre las claves en inglés, que son las que funcionan. Este
documento **no** edita el espejo (fuera del alcance del encargo); queda constancia aquí para
que nadie repita el error.

> 🔍 Aparte, tanto la página en español como en inglés de `audio_get_recorder_info` comparten
> un ejemplo de código **copiado por error** de la página de `audio_queue_sound` (no tiene
> nada que ver con `audio_get_recorder_info`). Es un fallo del manual oficial en los dos
> idiomas, no de la traducción de esta biblioteca — por eso el ejemplo de abajo es propio.

### El evento asíncrono **Audio Recording**

Se dispara **en cada paso** en que llega audio grabado, mientras `audio_start_recording()`
esté activo. El `ds_map` de `async_load` trae:

- `"buffer_id"` — el buffer **temporal** con los datos de audio de este paso.
- `"channel_index"` — el índice de canal devuelto por `audio_start_recording()`.
- `"data_len"` — cuántos bytes llegaron en este paso.

> 🔺 **El buffer temporal se destruye en cuanto termina el evento.** Si no copias su contenido
> a un buffer propio dentro del propio evento, esos datos se pierden para siempre.

### Ejemplo práctico completo: grabar, reproducir y exportar a WAV

```gml
// obj_grabadora — Create
grabando               = false;
grabacion_buffer       = -1;
grabacion_canal        = -1;
grabacion_formato      = buffer_s16;
grabacion_frecuencia   = 16000;
grabacion_canales      = audio_mono;
grabacion_bytes_usados = 0;
grabacion_bytes_max    = 0;
grabacion_duracion_max = 5;   // segundos

/// @function grabacion_iniciar()
/// @description Arranca la grabación desde la primera fuente disponible. Lee el formato real
///              de la plataforma en vez de asumirlo (hoy es siempre buffer_s16 / 16000 Hz /
///              mono, pero el propio manual avisa de que puede cambiar).
function grabacion_iniciar()
{
    if (audio_get_recorder_count() <= 0)
    {
        show_debug_message("grabacion_iniciar: no hay ningún micrófono disponible.");
        return false;
    }

    var _info = audio_get_recorder_info(0);
    grabacion_formato    = _info[? "data_format"];
    grabacion_frecuencia = _info[? "sample_rate"];
    grabacion_canales    = _info[? "channels"];
    ds_map_destroy(_info);   // el manual avisa: este mapa NO se destruye solo

    grabacion_bytes_max    = grabacion_frecuencia * buffer_sizeof(grabacion_formato) * grabacion_duracion_max;
    grabacion_buffer       = buffer_create(grabacion_bytes_max, buffer_grow, 1);
    grabacion_bytes_usados = 0;
    grabacion_canal        = audio_start_recording(0);
    grabando               = true;
    return true;
}

/// @function grabacion_detener()
function grabacion_detener()
{
    if (!grabando) return;
    audio_stop_recording(grabacion_canal);
    grabando = false;
}
```

```gml
// obj_grabadora — Evento Asíncrono: Audio Recording
if (grabando && async_load[? "channel_index"] == grabacion_canal)
{
    var _len = async_load[? "data_len"];

    // el buffer temporal desaparece al acabar este evento: cópialo YA
    buffer_copy(async_load[? "buffer_id"], 0, _len, grabacion_buffer, grabacion_bytes_usados);
    grabacion_bytes_usados += _len;

    if (grabacion_bytes_usados >= grabacion_bytes_max)
    {
        grabacion_detener();   // se llenó el buffer: para antes de desbordar
    }
}
```

Con el audio ya capturado en `grabacion_buffer`, dos salidas:

```gml
/// @function grabacion_reproducir()
/// @description Convierte lo grabado en un sonido reproducible directamente, sin pasar por
///              disco. Devuelve el asset de sonido: libéralo con audio_free_buffer_sound()
///              cuando termine (por ejemplo, en el evento Audio Playback Ended de 02 · 07).
function grabacion_reproducir()
{
    var _sonido = audio_create_buffer_sound(grabacion_buffer, grabacion_formato,
                                             grabacion_frecuencia, 0, grabacion_bytes_usados,
                                             grabacion_canales);
    audio_play_sound(_sonido, 80, false);
    return _sonido;
}
```

```gml
/// @function wav_construir(_pcm, _pcm_offset, _pcm_bytes, _canales, _muestras_por_seg, _bits)
/// @description Envuelve datos PCM crudos (como los que llegan de audio_get_recorder_info /
///              el evento Audio Recording) en un buffer con cabecera WAV canónica de 44 bytes,
///              listo para buffer_save() o para audio_create_buffer_sound(). Layout verificado
///              contra la especificación RIFF/WAVE (ver «Fuentes»).
function wav_construir(_pcm, _pcm_offset, _pcm_bytes, _canales, _muestras_por_seg, _bits)
{
    var _bloque       = _canales * (_bits div 8);
    var _bytes_x_seg  = _muestras_por_seg * _bloque;
    var _wav          = buffer_create(44 + _pcm_bytes, buffer_grow, 1);

    buffer_write(_wav, buffer_text, "RIFF");
    buffer_write(_wav, buffer_u32,  36 + _pcm_bytes);        // ChunkSize = tamaño total - 8
    buffer_write(_wav, buffer_text, "WAVE");
    buffer_write(_wav, buffer_text, "fmt ");                 // OJO: el espacio final es parte del ID
    buffer_write(_wav, buffer_u32,  16);                     // Subchunk1Size: 16 para PCM
    buffer_write(_wav, buffer_u16,  1);                      // AudioFormat: 1 = PCM sin comprimir
    buffer_write(_wav, buffer_u16,  _canales);
    buffer_write(_wav, buffer_u32,  _muestras_por_seg);
    buffer_write(_wav, buffer_u32,  _bytes_x_seg);           // ByteRate
    buffer_write(_wav, buffer_u16,  _bloque);                // BlockAlign
    buffer_write(_wav, buffer_u16,  _bits);
    buffer_write(_wav, buffer_text, "data");
    buffer_write(_wav, buffer_u32,  _pcm_bytes);             // Subchunk2Size

    buffer_copy(_pcm, _pcm_offset, _pcm_bytes, _wav, 44);
    return _wav;
}

/// @function grabacion_guardar_wav(_ruta)
function grabacion_guardar_wav(_ruta)
{
    var _num_canales = (grabacion_canales == audio_stereo) ? 2 : 1;
    var _bits         = (grabacion_formato == buffer_s16) ? 16 : 8;

    var _wav = wav_construir(grabacion_buffer, 0, grabacion_bytes_usados, _num_canales,
                              grabacion_frecuencia, _bits);
    buffer_save(_wav, _ruta);
    buffer_delete(_wav);
}
```

```gml
// obj_grabadora — Clean Up
if (grabando) audio_stop_recording(grabacion_canal);
if (grabacion_buffer != -1)
{
    buffer_delete(grabacion_buffer);
    grabacion_buffer = -1;
}
```

`buffer_text` (documentada en `08 · 16`) escribe la cadena **sin** carácter nulo final — justo
lo que necesita un identificador RIFF de 4 bytes exactos como `"RIFF"` o `"fmt "`. Usar
`buffer_string` ahí metería un byte de más y desalinearía toda la cabecera.

### Errores clásicos con grabación

| Síntoma | Causa | Arreglo |
|---|---|---|
| El audio grabado llega vacío o cortado | Se leyó `async_load[? "buffer_id"]` fuera del evento, o se guardó la referencia para usarla después | Copia con `buffer_copy` **dentro** del propio evento Audio Recording |
| Funciona en PC y no en el navegador | Grabación no disponible en HTML5 | Comprueba la plataforma y ofrece una alternativa (o desactiva la función) |
| `audio_get_recorder_count()` da `0` aun con micrófono conectado | El permiso del SO no se concedió, o el dispositivo lo bloquea | Pide el permiso primero (`04 · 28`) y vuelve a comprobar tras concederlo |
| El WAV exportado no reproduce en un reproductor externo | Falta el espacio en `"fmt "`, o se calculó mal `ByteRate`/`BlockAlign` | Usa `wav_construir()` tal cual: los tres campos dependen unos de otros |
| `_info[? "nombre"]` devuelve `undefined` | Se copiaron las claves del manual en **español** | Usa las claves en inglés: `"name"`, `"index"`, `"channels"` (ver aviso de traducción arriba) |

---

## 6 · Doppler: velocidad de emisores y del oyente

El Doppler en GameMaker **no** se calcula solo a partir de la posición: hace falta decirle al
motor la **velocidad** por separado, con su propio vector. Actualizar solo
`audio_emitter_position()` cada `Step` (como ya hace `13 · 09 §5.2` para el anillo de emisores
posicionales) mueve el sonido en el espacio, pero **no** produce Doppler — para eso hace falta
`audio_emitter_velocity()` en el mismo `Step`.

### Las 4 funciones

| Función | Qué hace |
|---|---|
| `audio_emitter_velocity(emitter, vx, vy, vz)` | Velocidad de un emisor, en las mismas unidades que uses para su posición (normalmente píxeles/paso). |
| `audio_listener_velocity(vx, vy, vz)` | Velocidad del oyente **0** (el que usan la mayoría de proyectos con un solo oyente). |
| `audio_listener_set_velocity(index, x, y, z)` | Velocidad de un oyente concreto por índice — imprescindible si hay más de uno. |
| `audio_listener_get_data(index)` | `Id.DsMap` con posición, velocidad y orientación del oyente: claves `"x"/"y"/"z"`, `"vx"/"vy"/"vz"`, `"lookat_x…"`, `"up_x…"`. Tú destruyes el mapa. |

### Ejemplo práctico: un proyectil con Doppler

```gml
// obj_proyectil — Create
emisor        = audio_emitter_create();
sonido_vuelo  = -1;

// obj_proyectil — Step
audio_emitter_position(emisor, x, y, 0);
audio_emitter_velocity(emisor, hspeed, vspeed, 0);   // 🔺 sin esto no hay Doppler

if (sonido_vuelo == -1)
{
    sonido_vuelo = audio_play_sound_on(emisor, snd_proyectil_vuelo, true, 60);
}

// obj_proyectil — Clean Up
audio_emitter_free(emisor);   // libera también el sonido que sonaba en él (01 · 13 §6)
```

```gml
// obj_jugador (o la cámara, si el oyente vive ahí) — Step
audio_listener_position(x, y, 0);
audio_listener_velocity(hspeed, vspeed, 0);
```

> 💡 Si el oyente está quieto o se mueve a velocidad constante durante toda la partida (cámara
> fija, *side-scroller* a velocidad constante), no hace falta llamar a
> `audio_listener_velocity()` en absoluto: el valor por defecto ya es `(0, 0, 0)`.

### Varios oyentes (cooperativo local / pantalla partida)

`audio_listener_velocity()` sin índice siempre apunta al oyente **0**. Con más de un oyente,
usa `audio_get_listener_count()` + `audio_get_listener_info()` (documentadas junto al resto de
la familia *Audio Listeners* en `01 · 13 §6`) para recorrer los índices reales de la
plataforma, y `audio_listener_set_velocity(indice, vx, vy, vz)` para cada uno por separado:

```gml
var _num = audio_get_listener_count();
for (var i = 0; i < _num; i++)
{
    var _info = audio_get_listener_info(i);
    audio_listener_set_velocity(_info[? "index"], jugador[i].hspeed, jugador[i].vspeed, 0);
    ds_map_destroy(_info);
}
```

### Errores clásicos con Doppler

| Síntoma | Causa | Arreglo |
|---|---|---|
| El sonido se mueve en el espacio pero no cambia de tono al pasar | Solo se actualizó la posición | Añade `audio_emitter_velocity()` / `audio_listener_velocity()` en el mismo `Step` |
| El Doppler es exagerado o casi imperceptible | Las unidades de velocidad no coinciden con las de posición | Usa las mismas unidades que ya usas para `x`/`y` (normalmente píxeles/paso); no hace falta convertir a m/s |
| Con dos jugadores, solo uno tiene Doppler correcto | Se usó `audio_listener_velocity()` (oyente 0) para los dos | Usa `audio_listener_set_velocity(indice, …)` con el índice de cada oyente |

---

## 7 · Checklist antes de dar por hecho el audio en buffers

- [ ] Cada sync group creado tiene su `audio_destroy_sync_group()` en **Room End**/**Clean Up**.
- [ ] Todas las pistas de un sync group con `loop = true` miden exactamente lo mismo.
- [ ] Cada buffer sound creado (`audio_create_buffer_sound`) se libera con
      `audio_free_buffer_sound()` **antes** de `buffer_delete()` el buffer de origen.
- [ ] Ningún buffer de un buffer sound se modifica después de crear el sonido.
- [ ] Cada audio queue tiene su `audio_free_play_queue()`, y no se borra un buffer encolado
      hasta que el evento **Audio Playback** confirma que ya no se usa.
- [ ] Antes de grabar, se comprueba `audio_get_recorder_count() > 0`.
- [ ] El buffer temporal del evento **Audio Recording** se copia **dentro** del propio evento.
- [ ] Los emisores y el oyente reciben velocidad (`_velocity`), no solo posición, si necesitan
      Doppler.
- [ ] Ninguna de estas cuatro familias se usa en un *target* HTML5 sin comprobar antes que
      están disponibles (sync groups y grabación no lo están; buffer sounds y play queues sí).

---

## 8 · Errores clásicos y cómo evitarlos

| Familia | Síntoma | Arreglo |
|---|---|---|
| Sync groups | No suena en HTML5 | No están soportados ahí: usa el patrón manual de `04 · 26` como *fallback* |
| Buffer sounds | Ruido basura o silencio | Solo `buffer_u8`/`buffer_s16`; nunca `buffer_f32` |
| Play queues | Hueco de silencio entre fragmentos | Encola con antelación, no al terminar el anterior |
| Grabación | Datos vacíos | Copia el buffer temporal **dentro** del evento Audio Recording |
| Grabación | `_info[? "nombre"]` da `undefined` | Usa las claves en **inglés** (ver la discrepancia de traducción en §5) |
| Doppler | No hay efecto | Actualiza `_velocity`, no solo posición, cada `Step` |
| Las cuatro | Fuga de memoria de audio | Cada `create`/`start` tiene su `destroy`/`free`/`delete` — sin excepción |

---

## Ver también

- [01 · 13 — Audio](../01%20-%20Fundamentos/13%20-%20Audio.md) — reproducción básica, voces,
  emisores/listeners posicionales, audio groups, streaming de assets, HTML5 y depuración.
- [02 · 07 — Audio: buses y efectos](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md) —
  buses, los 12 efectos DSP, y el evento *Audio Playback Ended* (el de los sonidos normales;
  distinto del evento *Audio Playback* de los play queues que cubre el §4 de este documento).
- [04 · 26 — Música adaptativa por capas](../04%20-%20Recetas%20por%20género/26%20-%20Música%20adaptativa%20por%20capas.md) —
  el patrón manual de capas verticales; el §2 de aquí es la versión con sincronía garantizada.
- [13 · 09 — Diseño de sonido y mezcla](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md) —
  el oficio: presupuesto de sonido, prioridad de voces, atenuación, oclusión.
- [04 · 28 — Juegos para móvil (táctil)](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md) —
  permiso `RECORD_AUDIO` en Android.
- [08 · 16 — Buffers](./16%20-%20Buffers.md) — la base de todo este documento: tipos de dato,
  alineación, `buffer_text` vs `buffer_string`, `buffer_poke`, buenas prácticas.
- [05 · 03 — Glosario GML](../05%20-%20Referencia/03%20-%20Glosario%20GML.md) — términos de
  audio usados en toda la biblioteca.
- La lista completa de la familia: `python3 _indice/buscar.py --listar audio_` (130 símbolos).

---

## Fuentes

- [Audio Buffers (manual LTS, ES)](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Buffers/Audio_Buffers.htm)
- [Audio Synchronisation (manual LTS, ES)](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Synchronisation/Audio_Synchronisation.htm)
- [audio_emitter_velocity (manual LTS, ES)](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Emitters/audio_emitter_velocity.htm)
- [audio_listener_velocity (manual LTS, ES)](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Listeners/audio_listener_velocity.htm)
- [audio_listener_get_data (manual LTS, ES)](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Listeners/audio_listener_get_data.htm)
- [Evento asíncrono: Grabación de audio (manual LTS, ES)](https://manual.gamemaker.io/lts/es/The_Asset_Editors/Object_Properties/Async_Events/Audio_Recording.htm)
- [Evento asíncrono: Reproducción de audio (manual LTS, ES)](https://manual.gamemaker.io/lts/es/The_Asset_Editors/Object_Properties/Async_Events/Audio_Playback.htm)
- [audio_get_recorder_info (manual LTS, EN)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Buffers/audio_get_recorder_info.htm) —
  contrastada frase a frase contra el espejo en español para localizar la discrepancia de
  traducción de §5.
- [WAV PCM soundfile format — cabecera RIFF/WAVE canónica](https://en.wikipedia.org/wiki/WAV) —
  consultada el 2026-09-06 (vía WebFetch) para verificar offsets, tamaños y las fórmulas de
  `ChunkSize`/`ByteRate`/`BlockAlign` usadas en `wav_construir()`.
- Verificación de cada firma con `python3 _indice/buscar.py` contra `GmlSpec.xml` del runtime
  `2026.0.0.23`, consultado el 2026-09-06.
