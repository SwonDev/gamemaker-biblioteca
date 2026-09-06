# Auditoría de cobertura — dominio **AUDIO DE JUEGO COMPLETO**

> Biblioteca auditada: `/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje`
> Fecha: **6 de septiembre de 2026** · Referencia: GameMaker LTS 2026.0 (runtime `2026.0.0.23`)
> Auditor: agente de dominio «audio». Ignorados `Lumbre/` y `GameMaker_Fuentes/`.

---

## 0 · Resumen ejecutivo

El audio es **uno de los dominios mejor cubiertos de la biblioteca**, y por un margen amplio. Hay
seis documentos que lo tratan de frente y otros diez que lo tocan de lado:

| Documento | Líneas | Qué aporta |
|---|---:|---|
| `13 - Diseño y producción de videojuegos/09 - Diseño de sonido y mezcla.md` | 879 | El **oficio**: principios, presupuesto por género, diseño de un SFX, mezcla, buses reales de 2026, loudness con normas leídas, posicional, oclusión, ambiente, formatos, licencias, hoja de sonido y checklist |
| `01 - Fundamentos/13 - Audio.md` | 631 | La **API**: reproducción, voces, propiedades, bucles, emisores/listeners, buses, grupos, streaming, HTML5, errores, depuración, gestor completo |
| `02 - Novedades 2026/07 - Audio - buses y efectos.md` | 446 | Lo **nuevo de 2026**: `audio_play_sound_ext`, loop points, los 12 efectos DSP, reglas del array, bypass, ejemplos, evento *Audio Playback Ended* |
| `04 - Recetas por género/19 - Programación rítmica.md` | 254 | Conductor, ventanas de juicio, **calibración de latencia**, mapa de notas |
| `04 - Recetas por género/26 - Música adaptativa por capas.md` | 120 | *Vertical layering*, crossfade, stingers, transición por compás |
| `07 - Ecosistema/21 - Vinyl.md` | 120 | Mezclador por etiquetas, ducking y *beat tracking* ya resueltos |

**Veredicto.** De los **102 temas canónicos** evaluados: **76 CUBIERTO** (75 %), **15 PARCIAL**
(15 %), **11 FALTA** (11 %).

| Bloque | Temas | Cubierto | Parcial | Falta |
|---|---:|---:|---:|---:|
| A · Diseño de efectos de sonido | 13 | 12 | 1 | 0 |
| B · Implementación nativa en GameMaker | 20 | 15 | 2 | 3 |
| C · Buses, efectos DSP y mezcla | 12 | 10 | 2 | 0 |
| D · Sonido en el espacio | 12 | 7 | 2 | 3 |
| E · Música | 10 | 7 | 3 | 0 |
| F · Ritmo y latencia | 5 | 5 | 0 | 0 |
| G · Voz y diálogo | 10 | 6 | 1 | 3 |
| H · Plataformas: web y móvil | 8 | 6 | 1 | 1 |
| I · Herramientas, middleware y ecosistema | 6 | 4 | 1 | 1 |
| J · Accesibilidad y QA | 6 | 4 | 2 | 0 |

Los huecos no están donde uno esperaría (mezcla, loudness, oclusión, round robin y latencia están
mejor documentados que en la mayoría de libros del oficio). Están en **tres sitios concretos**:

1. **Familias enteras del runtime sin prosa**: *Audio Buffers* (sonido procedural, colas de
   reproducción, grabación de micrófono) y *Audio Synchronisation* (sync groups). Son **21
   funciones** del runtime que solo aparecen en la lista de `08 - .../_API del runtime/API-funciones.md`.
   La carpeta `08 - Referencia GML completa/` —que agrupa la API por familias— **no tiene documento
   de audio**.
2. **La cadena de audio→mundo**: los pasos por material, las zonas de reverberación y los estados
   de mezcla. La propia hoja de sonido de `13 · 09 §9` escribe «banco según superficie» como si
   estuviera resuelto, y **no lo está en ninguna parte**.
3. **La voz como producción**: grabación, localización de voz y lip-sync. La *reproducción* de una
   línea de voz sí está (y bien, en `13 · 12 §6.9`); el proceso de conseguirla, no.

Además, **ninguno de los nueve scripts compilados de `06 - Assets y Scripts/` es de audio**, pese a
que hay un gestor de audio escrito dos veces (en `01 · 13 §14` y en `13 · 09 §4.2`).

---

## 1 · Tabla completa

Leyenda de estado: **CUBIERTO** (documento y sección exactos) · **PARCIAL** (existe pero incompleto)
· **FALTA** (no existe).

### A · Diseño de efectos de sonido

| # | Tema | Estado | Dónde (ruta + encabezado) | Qué falta | Fuente externa que lo exige |
|---|---|---|---|---|---|
| A1 | Anatomía de un SFX: transitorio, cuerpo, cola | **CUBIERTO** | `13 - Diseño.../09 - Diseño de sonido y mezcla.md` → «### 3.1 Transitorio, cuerpo y cola» | — (tabla de capas + duraciones por tipo + la nota de que la cola la puede dar `Reverb1`) | Frank Bry, *Transient Enhancement With Explosions*, Designing Sound (2013) |
| A2 | Construir por capas (*layering*) un sonido complejo | **PARCIAL** | mismo doc, §3.1 | Describe las tres capas conceptualmente, pero no el **montaje**: cómo se apilan 4-6 grabaciones distintas para una explosión, qué aporta cada una, y cómo se hace en Audacity | Stevens & Raybould, *The Game Audio Tutorial*, cap. 2; Bjørn Jacobsen (A Sound Effect, 2018) — «cientos de variaciones por capas» |
| A3 | Variaciones y *round robin* sin repetición | **CUBIERTO** | `13 · 09` → «### 3.2 Variaciones y *round robin*» (`banco_crear` / `banco_siguiente`, con el razonamiento del `ultima` inicial) | — | Jacobsen, *nuisance score*; práctica estándar Wwise/FMOD |
| A4 | Aleatorización de tono en **semitonos** y de ganancia | **CUBIERTO** | `13 · 09 §3.2` (`variacion_tono`, `variacion_ganancia`); también `01 - Fundamentos/13 - Audio.md` §14 (`sfx()`) | — | Idem |
| A5 | Frecuencia ↔ prominencia; fatiga auditiva | **CUBIERTO** | `13 · 09` → «### 1.2 «Todo lo que pasa suena» — y dónde está el límite» (tabla de veces/minuto → dB, duración, tomas) | — | Bjørn Jacobsen, A Sound Effect (2018) |
| A6 | Las cuatro funciones del sonido (feedback, información, emoción, identidad) | **CUBIERTO** | `13 · 09` → «### 1.1 Las cuatro cosas que hace el sonido» | — | Stevens & Raybould; charla de Overwatch |
| A7 | Síntesis: sfxr / jsfxr / Bfxr / ChipTone | **CUBIERTO** | `07 - Ecosistema/09 - Asset packs...md` → «## 5. Herramientas de audio»; paso a paso en `03 - Cursos (YouTube)/09 - ... Parte 9 - Sonidos y Música.md` → «## 11. Efectos de sonido: jsfxr» | ChipTone solo se nombra en la tabla de licencias de `13 · 09 §8`; no está en la tabla de herramientas de `07 · 09 §5` | sfxr (DrPetter), ChipTone (SFBGames) |
| A8 | Grabación propia y **foley** casero | **CUBIERTO** | `03 - Cursos (YouTube)/09 ...` → «## 10. Efectos de sonido: Foley» y «## 4. Haz tu propia música con un ukelele y Audacity» | — | Práctica estándar; *Designing Sound* |
| A9 | Edición y normalización (Audacity, `ffmpeg`) | **CUBIERTO** | `13 · 09` → «## 7 · Formatos y ajustes de importación» (`volumedetect`, `volume`, `loudnorm`, y la regla «SFX por pico, música por loudness»); herramienta en `07 · 09 §5` | — | ffmpeg docs (`ebur128`, `loudnorm`) |
| A10 | Sonidos de UI: categoría, nunca posicional, no dispararlos 60 veces | **CUBIERTO** | `13 · 09` → «## 2 · Categorías y presupuesto de sonido» («La UI nunca es posicional») + §4.2 (emisor `ui`, prioridad 80); patrón anti-spam en `03 · 09` → «## 12. Añadir efectos de sonido sin que se disparen 60 veces» | — | Práctica estándar |
| A11 | Lista mínima de sonidos por género y dimensionado del proyecto | **CUBIERTO** | `13 · 09 §2` (tabla de 10 géneros × 5 categorías, y el ⚠️ honesto de que el dimensionado es experiencia, no fuente publicada) | — | — |
| A12 | Hoja de sonido como documento de trabajo | **CUBIERTO** | `13 · 09` → «## 9 · La hoja de sonido» (plantilla en Markdown + orden de relleno) | — | Práctica de producción (asset list de Wwise/FMOD) |
| A13 | Licencias de audio (CC0 / CC-BY / CC-BY-NC) y hoja de créditos | **CUBIERTO** | `13 · 09` → «## 8 · Herramientas, licencias y accesibilidad»; bancos en `07 · 09` → «### 2.5 Freesound.org (audio)» y «## 8. Bancos de música y SFX ya hechos» | — | Freesound; Creative Commons |

### B · Implementación nativa en GameMaker

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| B1 | `audio_play_sound` / `audio_play_sound_ext` (struct de parámetros) | **CUBIERTO** | `01 · 13` → «### La forma moderna: `audio_play_sound_ext()`»; `02 - Novedades 2026/07` → «## 2» y «## 3» (firma, claves, multiplicación con el asset) | — | Manual, `audio_play_sound_ext.htm` |
| B2 | Asset vs instancia («voz») y la jerarquía asset→emitter→instancia→bus | **CUBIERTO** | `01 · 13` → «## 3. Sonidos vs instancias de sonido («voces»)» (con el diagrama de niveles) | — | Manual, `Audio_Properties.htm` |
| B3 | Límite de 128 voces, `audio_channel_num`, descarte por prioridad | **CUBIERTO** | `01 · 13` → «### El límite de voces»; `13 · 09` → «### 3.3 Prioridad, voces y el límite que te falta» | — | Manual, `audio_channel_num.htm` |
| B4 | **Cupo de voces por sonido** y robo de la más antigua | **CUBIERTO** | `13 · 09 §3.3` (`scr_voces`: `sonar_limitado`, `apagar_con_fundido`, poda de voces muertas) | — | Práctica de mezcla (*voice limiting* de Wwise) |
| B5 | Fundidos sin clic (`audio_sound_gain` con tiempo) | **CUBIERTO** | `13 · 09 §3.3` (`apagar_con_fundido`, 30-60 ms) y `§10.2`; `04 · 26` → «## El crossfade» | — | Manual, `audio_sound_gain.htm` |
| B6 | Puntos de bucle en runtime (intro que no se repite) | **CUBIERTO** | `01 · 13` → «## 5. Loop (bucle)»; `02 · 07` → «## 4. Audio Loop Points» (con el aviso de que **no existe** `audio_sound_loop_points`) | — | Manual, `Audio_Loop_Points.htm` |
| B7 | Bucles con hueco en OGG (*encoder padding*) | **CUBIERTO** | `13 · 09 §7` (⚠️ «Un bucle en OGG puede tener un hueco al repetir») | — | Vorbis/Ogg; práctica común |
| B8 | Grupos de audio: carga/descarga por zona y `audio_group_set_gain` | **CUBIERTO** | `01 · 13` → «## 8. Audio groups»; sliders reales en `04 - Recetas.../25 - Menú de opciones y ajustes.md` (`aplicar_ajuste`) | — | Manual, `Settings/Audio_Groups.htm` |
| B9 | Streaming frente a memoria (`audio_create_stream`) | **CUBIERTO** | `01 · 13` → «## 9. Audio en streaming»; criterio de cuándo, en `13 · 09 §7` (tabla de atributos por tipo de sonido) | — | Manual, `The_Asset_Editors/Sounds.htm` |
| B10 | Formatos y ajustes de importación (WAV/OGG/MP3, sample rate, bitrate, mono vs estéreo) | **CUBIERTO** | `13 · 09 §7` (tabla completa + «3D y mono son lo mismo» citando el manual); `01 · 13` → «## 1. Formatos soportados» | — | Manual, `Sounds.htm` |
| B11 | **Presupuesto de memoria de audio** | **CUBIERTO** | `13 · 09 §7` → «**Presupuesto de memoria.**» (fórmula `frecuencia × bits/8 × canales × segundos`, con los dos ejemplos numéricos) | — | Aritmética PCM |
| B12 | Mezclador de sonido del IDE | **CUBIERTO** | `13 · 09` → «### 4.5 El mezclador de sonido del IDE» | — | Manual, `IDE_Tools/Sound_Mixer.htm` |
| B13 | Evento async **Audio Playback Ended** | **CUBIERTO** | `02 · 07` → «## 6. Evento "Audio Playback Ended"» | — | Manual, `Async_Events/Audio_Playback_Ended.htm` |
| B14 | Errores de audio y `audio_throw_on_error` | **CUBIERTO** | `01 · 13` → «## 12. Manejo de errores» (tabla fatal / no fatal) | — | Manual, `audio_throw_on_error.htm` |
| B15 | Depuración: ventana **Audio** del Debug Overlay | **CUBIERTO** | `01 · 13` → «## 13. Depuración de audio» (colores por estado y columnas); citado como herramienta en `13 · 09 §7` y `§10.1` | — | Manual, `The_Debug_Overlay.htm` |
| B16 | **Sync groups** (sincronía a nivel de muestra) | **PARCIAL** | `01 · 13` → «## 10. Sincronización: sync groups» — **5 líneas** con `audio_create_sync_group(...)` y «Ver el manual» | La firma real es `audio_create_sync_group(loop)`. Faltan las **11 funciones** (`audio_play_in_sync_group`, `audio_start_sync_group`, `audio_sync_group_get_track_pos`, `audio_pause/resume/stop_sync_group`, `audio_sync_group_is_playing/is_paused`, `audio_sync_group_debug`, `audio_destroy_sync_group`) y el caso de uso que las justifica: **capas de música que se activan sin desfase**, que es exactamente lo que `04 · 26` resuelve a mano lanzándolas en el mismo frame | Manual, `Audio_Synchronisation/` (11 páginas espejadas en `09 - Manual oficial/manual-lts-2026-es/.../Audio_Synchronisation/`) |
| B17 | **Audio buffers y colas**: `audio_create_buffer_sound`, `audio_create_play_queue`, `audio_queue_sound` — audio **procedural/sintetizado en runtime** y streaming propio | **FALTA** | Solo el nombre en `08 - Referencia GML completa/_API del runtime/API-funciones.md` | Todo. Es la vía para generar tonos, sintetizar SFX en ejecución, reproducir audio descargado o descodificado por ti, y encadenar buffers sin hueco. Cinco funciones del runtime sin una línea de prosa | Manual, `Audio_Buffers/` (10 páginas espejadas); `08 - .../16 - Buffers.md` existe pero no toca audio |
| B18 | **Grabación de micrófono**: `audio_start_recording`, `audio_get_recorder_count/info`, evento async *Audio Recording* | **FALTA** | Solo el nombre en `API-funciones.md`. El permiso `RECORD_AUDIO` sí está en `04 - Recetas.../28 - Juegos para móvil (táctil).md` | Todo el flujo: elegir dispositivo, copiar el buffer temporal antes de que el evento lo destruya, y convertirlo en sonido con `audio_create_buffer_sound`. Es el único camino a mecánicas de voz/soplido | Manual, `Async_Events/Audio_Recording.htm` (espejada en español) |
| B19 | Audio en **Sequences** (`seqtracktype_audio`, `seqtracktype_audioeffect`) | **PARCIAL** | `13 - Diseño.../04 - Animación de sprites, Sequences y Animation Curves.md` (tabla de tipos de pista y claves `seqaudiokey_oneshot`/`seqaudiokey_loop`); `02 · 07` → «### 5.10 Efectos en Sequences» (3 líneas) | No hay ejemplo de una cinemática con pista de audio ni de **animar un parámetro de efecto** (bajar el cutoff a lo largo de la secuencia), que es lo que hace útil la pista de audio-efecto | Manual, `Sequences/`; blog LTS 2026.0 |
| B20 | Script de audio **compilado y verificado** en `06 - Assets y Scripts/` | **FALTA** | Los nueve scripts son `scr_camera`, `scr_debug`, `scr_grid_pathfinding`, `scr_input_buffer`, `scr_math_util`, `scr_pool`, `scr_save_load`, `scr_state_machine`, `scr_tween` | Ninguno de audio, pese a que hay un gestor completo escrito en `01 · 13 §14` y otro mejor en `13 · 09 §4.2`. El README de `06` presume de «compilación verificada 2026-09-02 · cero errores»: el audio se queda fuera de esa garantía | — (deuda interna de la biblioteca) |

### C · Buses, efectos DSP y mezcla

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| C1 | Concepto de bus y la **limitación clave**: los buses propios solo actúan sobre emisores | **CUBIERTO** | `02 · 07` → «### 5.1 Concepto: todo pasa por un bus» y «### 5.6 Buses personalizados y emitters»; consecuencias arquitectónicas en `13 · 09` → «### 4.2 Cómo se montan de verdad los buses en 2026» (tabla «Quiero… / Herramienta correcta») | — | Manual, `Audio_Effects.htm` |
| C2 | **Lista real de efectos DSP de 2026** | **CUBIERTO** | `02 · 07` → «### 5.2 Efectos disponibles» — 12 tipos: `Bitcrusher`, `Delay`, `Gain`, `HPF2`, `LPF2`, `Reverb1`, `Tremolo`, `EQ`, `PeakEQ`, `HiShelf`, `LoShelf`, `Compressor` | — **Verificado en esta auditoría** contra `09 - Manual oficial/manual-lts-2026-es/.../Audio_Effects/AudioEffectType.md`: la lista coincide exactamente, sin omisiones ni invenciones | Manual, `AudioEffectType.htm`; blog *How To Use Audio Effects in GameMaker* (Matharoo, 2022) — comprobado en vivo, HTTP 200 |
| C3 | Array de 8 efectos: asignar activa, `undefined` quita, orden, bypass | **CUBIERTO** | `02 · 07` → «### 5.4 Reglas del array de efectos» y «### 5.5 Bypass»; «### 5.7 Asignar el mismo efecto a varios sitios» | — | Manual, `AudioBus.htm` |
| C4 | Ajustar parámetros **antes** de asignar (evitar el salto audible) | **CUBIERTO** | `02 · 07 §5.3`; repetido como 💡 en `13 · 09 §4.3` | — | Manual (buena práctica explícita) |
| C5 | Compresor como **limitador** del master (GameMaker no trae limitador) | **CUBIERTO** | `13 · 09` → «### 4.3 Compresor, «limitador» y EQ para hacer sitio» (ratio 20:1, attack 0,001, último hueco del array, con los rangos documentados) | — | Manual, `AudioEffect.htm` (rangos); práctica de mastering |
| C6 | EQ para hacer sitio: mapa de bandas y valle para la voz | **CUBIERTO** | `13 · 09 §4.3` (20-80 / 80-250 / 400-800 / 1,5-3k / 6-12 kHz, con qué hacer en cada una) | — | Alex Riviere, *Demystifying Game Audio Mixing*, A Sound Effect (2023) |
| C7 | **Ducking** música ↔ voz | **CUBIERTO** | `13 · 09 §4.2` (Step con `lerp` asimétrico: baja en ~3 frames, sube en ~25, y el ⚠️ de la dependencia de fps); alternativa hecha en `07 - Ecosistema/21 - Vinyl...md` → «## 3 · Ducking» | — | Riviere (2023); Vinyl `VinylDucker*` |
| C8 | Jerarquía de niveles por categoría (dB relativos) | **CUBIERTO** | `13 · 09` → «### 4.1 La jerarquía de niveles» (tabla con dB, lineal y `db_to_lin`), marcada honestamente como práctica no publicada | — | Riviere (2023); práctica de estudio |
| C9 | **Loudness**: LUFS/LKFS, ASWG-R001, EBU R128, medición con `ffmpeg` | **CUBIERTO** | `13 · 09` → «### 4.4 Loudness: las cifras que sí están publicadas» (−24 LKFS sobremesa, −18 portátil, −1 dBTP; medir 20-30 min de partida real; salida real de `ffmpeg -af ebur128`) | — | ASWG-R001 v1.10 (Sony WWS, 2013); EBU R 128 v5.0 (2023); Spotify |
| C10 | Sliders de volumen **por categoría** conectados a la mezcla | **CUBIERTO** | `04 - Recetas.../25 - Menú de opciones y ajustes.md` (grupos de audio + aplicar en vivo + persistencia); `13 · 09 §4.2` (`mezcla_aplicar` con buses) | — | Guidelines de accesibilidad (Xbox AGDG / AbleGamers) |
| C11 | **Estados / snapshots de mezcla** (combate, pausa, bajo el agua, menú) como sistema | **PARCIAL** | Ejemplos sueltos: `02 · 07` → «### 5.8 Ejemplo completo: "bajo el agua"» y «### 5.9 Ejemplo: transición a menú de pausa» | No hay el **patrón**: un conjunto de estados de mezcla declarados (ganancias por bus + efectos + tiempo de transición) y una función que interpola entre ellos. Cada ejemplo actual toca el bus a pelo y no compone con los demás | Riviere (2023) — «mezcla base frente a *golden path*» y *state mixing*; snapshots de Wwise/FMOD |
| C12 | **Sistema de importancia / HDR audio** | **PARCIAL** | `13 · 09` → «### 1.3 «Oír siempre lo importante»» explica el sistema de Overwatch y por qué rechazaron el HDR audio; `§3.3` implementa el cupo de voces, que es su versión barata | Falta la implementación de la puntuación: cada sonido puntúa por daño, distancia y visibilidad, y esa puntuación decide cubo (alto/normal/bajo/descartado) y ganancia | Lawlor & Neumann, *Overwatch — The Elusive Goal: Play by Sound*, GDC 2016 |

### D · Sonido en el espacio

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| D1 | Emisores, listeners y `audio_emitter_free` (fuga de memoria) | **CUBIERTO** | `01 · 13` → «## 6. Audio 3D: emitters y listeners»; `13 · 09 §4.2` (Clean Up que libera todos los emisores; «los buses NO se liberan: los recoge el GC») | — | Manual, `audio_emitter_create.htm` |
| D2 | **El modelo de falloff por defecto es `none`** — el bug más frecuente | **CUBIERTO** | `13 · 09` → «### 5.1 La atenuación: el ajuste que todo el mundo olvida» (tabla de los 5 modelos + los tres números del emisor) | — | Manual, `audio_falloff_set_model.htm` (fórmulas) |
| D3 | Anillo de emisores reutilizables (posicional **y** por bus propio) | **CUBIERTO** | `13 · 09` → «### 5.2 Un anillo de emisores, y dónde va el oyente» (`scr_emisores`, con el ⚠️ de que reutilizar un emisor mueve los sonidos que sigan sonando) | — | Práctica estándar (*emitter pooling*) |
| D4 | Dónde va el oyente: cámara vs jugador; el problema del zoom | **CUBIERTO** | `13 · 09 §5.2` (oyente en el centro de la cámara + el 🔺 sobre el zoom, que obliga a elegir y escribirlo) | — | Práctica estándar |
| D5 | **Oclusión** barata: raycast + LPF interpolado | **CUBIERTO** | `13 · 09` → «### 5.3 Oclusión barata: una pared se come los agudos» (`obj_fuente_ambiental` completo con bus propio, `LPF2` de 18 kHz a 700 Hz, y `bus.gain` acompañando) | — | Overwatch, GDC 2016 (oclusión gradual por desvío del rayo, 5/30/100 %); tutorial oficial de GameMaker |
| D6 | Dentro / fuera de pantalla: refuerzo del sonido informativo | **CUBIERTO** | `13 · 09` → «### 5.4 Dentro y fuera de pantalla» (`en_pantalla()`, +2 dB si no se ve, no reproducir lo irrelevante) | — | Overwatch, GDC 2016 |
| D7 | Todo lo posicional en **mono** | **CUBIERTO** | `13 · 09 §7` (cita literal del manual: «3D» y «mono» son lo mismo) | — | Manual, `Sounds.htm` |
| D8 | **Pasos según el material / terreno** (detectar tile o superficie y elegir banco) | **FALTA** | La hoja de sonido de `13 · 09 §9` lo da por hecho («banco según superficie») y `§3.2` monta el banco, pero **no existe la detección**. `01 · 13 §6` solo tiene `audio_play_sound_on(em_pasos, snd_paso, ...)` con un único sonido | La receta entera: leer el tile bajo los pies con `tilemap_get_at_pixel` (o una capa de máscara, o un `collision_point` contra objetos de terreno), mapear índice de tile → banco de pasos, y el disparo desde el evento de animación (`13 · 04` ya tiene el broadcast `"paso_der"`, pero reproduce un `snd_paso` fijo) | Stevens & Raybould, *Game Audio Implementation*, cap. sobre *surface types*; *switch containers* de Wwise |
| D9 | **Zonas de reverberación** (cambiar el espacio al entrar en cueva/sala) | **PARCIAL** | `13 · 09 §3.1` lo sugiere («la cola te la puede dar el motor… un `Reverb1` en el bus de la zona»); `02 · 07 §5.8` tiene el caso «bajo el agua» con bypass del master | Falta el patrón de **zona**: un `Reverb1` por ambiente con transición interpolada al cruzar el límite, y la advertencia de que con la limitación de C1 hay que enrutar los SFX del mundo por emisores para que la reverberación los alcance | Stevens & Raybould, cap. *Reverb zones*; práctica estándar |
| D10 | **Múltiples listeners** (cooperativo local / pantalla partida) | **PARCIAL** | `01 · 13` → «## 4. Propiedades de audio» explica la *listener mask* como propiedad; `13 · 09 §2` menciona «(sí en cooperativo)» al hablar de posicional | Falta la receta: `audio_get_listener_count()`, `audio_get_listener_info()`, `audio_listener_set_position(index, …)` y el reparto de máscaras por jugador. Hay pantalla partida documentada en `01 - Fundamentos/10 - Rooms, capas, cámaras y viewports.md`, y el audio no la acompaña | Manual, `Audio_Listeners/` |
| D11 | **Doppler y velocidad** (`audio_emitter_velocity`, `audio_listener_velocity`) | **FALTA** | Solo el nombre en `API-funciones.md` | Sin prosa. Es el efecto canónico de un proyectil, un vehículo o un tren que pasa; y la trampa (hay que actualizar la velocidad cada frame, no solo la posición) no está avisada en ninguna parte | Manual, `Audio_Emitters/audio_emitter_velocity.htm` |
| D12 | **Audio 3D en juegos 3D** (eje Z real, orientación del oyente) | **FALTA** | `04 - Recetas por género/29 - 3D en GameMaker.md` (928 líneas) **no menciona el audio ni una vez**, salvo un «sonido del impacto según el material» de pasada. `01 · 13 §6` lista `audio_listener_orientation(...)` con puntos suspensivos, sin firma ni ejemplo | Firma real (`lookat_x/y/z`, `up_x/y/z`), cómo alimentarla desde la cámara 3D cada frame, `z` en emisores y falloff en unidades de mundo 3D, y por qué un oyente 2D en un juego 3D suena mal (no distingue delante de detrás) | Manual, `audio_listener_orientation.htm`; cualquier guía de audio 3D (Wwise/FMOD) |

### E · Música

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| E1 | **Capas verticales** (*vertical layering*) y crossfade | **CUBIERTO** | `04 - Recetas por género/26 - Música adaptativa por capas.md` → «## La idea» y «## El crossfade» (con el 🔺 de que la sincronía solo sale gratis si arrancan en el mismo frame) | — | Stevens & Raybould, *The Game Audio Tutorial*, cap. 6 |
| E2 | **Transición por compás** (esperar al siguiente compás, no cortar a media frase) | **CUBIERTO** | `04 · 26` → «## Transición por compás (avanzado)» (con `audio_sound_get_track_position` y `seg_por_compas`) | — | Idem |
| E3 | **Stingers** y la regla de tono/tempo | **CUBIERTO** | `04 · 26` → «## Stingers: golpes musicales puntuales»; el matiz de oficio en `13 · 09 §6` («un stinger fuera de tono suena a bug, y ningún GML lo arregla») | — | Idem |
| E4 | `audio_sound_get_track_position` como **reloj maestro** | **CUBIERTO** | `04 - Recetas.../19 - Programación rítmica...md` → «## La regla que decide si tu juego funciona» + «## 1 · El conductor» (con el 🔺 de que necesita el **id de instancia**, no el asset) | — | Manual, `audio_sound_get_track_position.htm` |
| E5 | Tempo, BPM y señal de *beat* desacoplada | **CUBIERTO** | `04 · 19 §1` (`obj_conductor` + `senal_emitir("beat", …)` y el `while` en vez de `if` para no perder beats en un tirón) | — | Práctica estándar (*conductor* de Rhythm Heaven / Crypt of the NecroDancer) |
| E6 | **Música horizontal** (*resequencing*: pista A → puente → pista B) | **PARCIAL** | `04 · 26` cubre solo lo vertical; la transición por compás es el ingrediente pero no la receta | Falta el patrón horizontal: segmentos con puntos de salida legales, un segmento puente opcional, y la cola del segmento anterior sonando sobre la entrada del siguiente. Es la mitad que falta del par «vertical / horizontal» que toda la literatura presenta junta | Stevens & Raybould, *The Game Audio Tutorial*, cap. 6 (*horizontal resequencing*); Darren Korb, *Hades* (GDC 2021) |
| E7 | **Música por estado del juego** como máquina de estados | **PARCIAL** | `04 · 26` engancha `musica_combate()` / `musica_explorar()` a señales (receta 16) | Solo dos estados y dos funciones. Falta la tabla estado → capas activas → tiempo de fundido, y qué pasa con estados que se solapan (combate **y** vida baja) | Idem |
| E8 | **Composición para juegos**: escribir bucles y capas que no cansen | **PARCIAL** | `04 · 26` exige «misma longitud y tempo»; `13 · 09 §6` da la regla del *bed* («cuanto más aburrido, mejor», 30-60 s mínimo) y la del silencio; herramientas en `07 · 09 §5` y `03 · 09 §7` | Falta la parte compositiva: duración de un bucle de gameplay, dónde poner el punto de bucle para que no se note, escribir las capas en la misma tonalidad para que cualquier combinación funcione, y qué instrumentación reservar para cada capa | Stevens & Raybould, cap. 6; Bosca Ceoil (Terry Cavanagh) |
| E9 | Ambiente: *bed* en bucle + *one-shots* a intervalo aleatorio | **CUBIERTO** | `13 · 09` → «## 6 · Ambiente y música» (`obj_ambiente_bosque` con `irandom_range` y posición aleatoria dentro de la vista; `ambiente_poner` con fundido cruzado de 2500 ms) | — | Práctica estándar; error clásico documentado en `§10.2` |
| E10 | **El silencio** como recurso de diseño | **CUBIERTO** | `13 · 09 §6` (cortar 2-4 s antes de la puerta del jefe; 300-500 ms antes del sonido de muerte; dejar la música fuera entre zonas) | — | Práctica de dirección musical |

### F · Ritmo y latencia

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| F1 | Ventanas de juicio (perfecto / bien / flojo) en **beats**, no en ms | **CUBIERTO** | `04 · 19` → «## 2 · Juzgar la pulsación del jugador» (tabla con la equivalencia a 128 BPM y el ⚠️ de que se afinan jugando) | — | Práctica de género (*Guitar Hero*, *Beat Saber*) |
| F2 | **Latencia de entrada y pantalla de calibración** | **CUBIERTO** | `04 · 19` → «## 3 · La latencia, que es el problema de verdad» (16 pulsaciones, media guardada en INI, descarte de la primera muestra, y el descuento en `conductor_error()`) | — | Práctica de género; Bluetooth ≈ 200 ms |
| F3 | Mapa de notas indexado por beat; **calcular** la posición, no acumularla | **CUBIERTO** | `04 · 19` → «## 5 · Colocar los eventos: el mapa de la canción» | — | Práctica de género |
| F4 | Feedback visual sincronizado con el conductor | **CUBIERTO** | `04 · 19` → «## 4 · Que se vea el ritmo» (`power(1 - _fase, 3)` en vez de `sin()`) | — | *12 principles*; game feel |
| F5 | *Beat tracking* con librería (Vinyl compensa la latencia del hilo de audio) | **CUBIERTO** | `07 - Ecosistema/21 - Vinyl...md` → «## 4 · Sincronía con el beat (música rítmica)» (`VinylAttachBeatTracker`, `VinylGetBeatThisStep`, `VinylGetBeatCount`, `VinylGetBeatDistance`) — **verificado en esta auditoría** contra `11 - Código descargado/librerias/audio/Vinyl/scripts/` | — | Vinyl (JujuAdams), MIT |

### G · Voz y diálogo

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| G1 | Reproducir una línea de voz cortando la anterior con fundido | **CUBIERTO** | `13 · 09 §4.2` (`voz_decir()`, prioridad 100, emisor de voz, `apagar_con_fundido(60)`) | — | Práctica estándar |
| G2 | La voz es la **referencia de la mezcla** (0 dB) y agacha la música | **CUBIERTO** | `13 · 09 §4.1` y `§4.2` (ducking a −9 dB) | — | Riviere (2023) |
| G3 | Duración del subtítulo = `max(mínimo, lectura, audio)` | **CUBIERTO** | `13 - Diseño.../12 - Diseño narrativo y diálogos.md` → «### 6.9 Subtítulos, velocidad de texto y voces» (`subtitulo_duracion` con `audio_sound_length`, y «MANDA EL AUDIO») | — | Guidelines de subtitulado (BBC / Game Accessibility Guidelines) |
| G4 | Voz sincronizada con el *typewriter* en novela visual | **CUBIERTO** | `04 - Recetas.../10 - Visual Novel y narrativa.md` → «### 4.6 Voz» (tabla «Audio manda / Texto manda») + `reproducir_voz()` con `asset_get_index("voz_" + _archivo)` | — | Práctica de género |
| G5 | Subtítulos activables, escala de texto y contraste | **CUBIERTO** | `04 - Recetas.../27 - Accesibilidad.md` → «## 2 · Subtítulos y texto legible» | — | Game Accessibility Guidelines |
| G6 | **Subtítulos de efectos con indicador direccional** | **PARCIAL** | Se **pide** en dos sitios (`04 · 27 §2`: «`[puerta crujiendo]`, `[pasos detrás]`»; `13 · 09 §8`: tabla con «Indicador en el borde de pantalla apuntando a la fuente») y no se **implementa** en ninguno | La cola de subtítulos de efectos: registro `sonido → texto`, disparo desde el mismo evento que el audio (`13 · 09 §8` da la regla pero no el código), duración, apilado de varios a la vez, y el indicador de borde con el ángulo hacia el emisor | Game Accessibility Guidelines («captions for meaningful sound», «indicate direction»); *The Last of Us Part II* como referencia |
| G7 | **Grabación de voz como producción** (guion de doblaje, dirección, nomenclatura, edición) | **FALTA** | Nada. `13 · 09 §2` reserva una fila «Voz» en la tabla de categorías y ahí acaba | El proceso: formato del guion con contexto por línea, convención de nombres de fichero (`voz_<personaje>_<escena>_<nnn>`) que además es lo que consume el `asset_get_index` de `04 · 10`, dirección de actores, y edición (recorte de silencios, de-esser, normalización a la referencia de 0 dB) | Stevens & Raybould, *Game Audio Implementation*, cap. de diálogo; práctica de estudio |
| G8 | **Localización de voz** | **FALTA** | `04 - Recetas.../21 - Localización e idiomas (con traducción por IA).md` **no menciona el audio ni una sola vez** (verificado con grep de `audio`, `voz`, `sonido`, `snd_`) | Cómo se localiza la voz: un asset por idioma con sufijo, resolución en runtime con `asset_get_index`, **fallback a solo subtítulos** cuando un idioma no está doblado, el impacto en el tamaño de la build (y por qué la voz va a grupos de audio por idioma o a `datafiles` externos), y el orden: subtitular antes que doblar | Práctica de localización; `04 · 21` es el documento que debería decirlo |
| G9 | **Lip-sync básico** | **FALTA** | Nada en toda la biblioteca (grep de `lip-sync`, `lipsync`: cero resultados) | Lo mínimo útil en 2D: boca abierta/cerrada por amplitud, o 3-4 visemas por energía del buffer; y la alternativa barata sin analizar audio (boca que se mueve mientras `audio_is_playing`, y se para en los silencios del guion) | Práctica de animación 2D; *Rhubarb Lip Sync* como herramienta offline |
| G10 | Chat de voz en multijugador | **CUBIERTO** | `04 - Recetas.../14 - Multijugador.md` (Photon trae canales en vivo, mute por jugador, detección de voz, bitrate y códec; y el aviso de que hacerlo a mano «es otro proyecto aparte») | — | GMEXT-Photon (oficial) |

### H · Plataformas: web y móvil

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| H1 | HTML5: Web Audio, contexto que se pausa, `audio_system_is_available()` y el evento async `"audio_system_status"` | **CUBIERTO** | `01 · 13` → «## 11. Audio en Web (HTML5 / GX.games)» (las dos formas de detectarlo, y el matiz de que fuera de HTML5 el evento salta una sola vez) | — | Manual, `audio_system_is_available.htm` |
| H2 | HTML5: **autoplay bloqueado** hasta el primer gesto del usuario | **PARCIAL** | `04 - Recetas.../17 - Interoperabilidad con la web (HTML5).md` — **una línea de tabla**: «Reproducir audio nada más cargar ❌ Los navegadores lo bloquean hasta la primera interacción» | Falta la receta: pantalla de «pulsa para empezar» que sirve de gesto de desbloqueo, comprobación de `audio_system_is_available()` antes de arrancar la música, y qué hacer con la música de la pantalla de carga (que no puede sonar) | Política de autoplay de Chrome/Safari; Manual, sección HTML5 |
| H3 | HTML5: buses y efectos **limitados** (iOS Safari, contexto no seguro) | **CUBIERTO** | `02 · 07` → «### 5.11 Limitaciones en HTML5» (siguen existiendo sin error de GML pero no suenan; salvo ganancia de bus y ruteo) | — | Manual / blog LTS 2026.0 |
| H4 | HTML5: el *streamed* se trata como no *streamed*; `audio_sound_is_playable()` | **CUBIERTO** | `13 · 09 §7` (⚠️ explícito) y `01 · 13 §11` | — | Manual, `Sounds.htm` |
| H5 | Móvil: el audio **no se reanuda solo** al volver de segundo plano | **CUBIERTO** | `04 - Recetas.../28 - Juegos para móvil (táctil).md` (`os_is_paused` → `audio_pause_all()` / `audio_resume_all()`, con el error clásico «el juego vuelve mudo y parece colgado»); también en `04 · 00` | — | Manual, `os_is_paused.htm` |
| H6 | Móvil: presupuesto de voces y formatos | **CUBIERTO** | `04 · 28` (tabla de rendimiento: «OGG comprimido para la música, WAV para efectos cortos, y pocos sonidos a la vez: el mezclador de un móvil no es el de un PC») | — | Práctica de plataforma |
| H7 | Móvil: **latencia de audio, interrupción por llamada y mezcla con la música del sistema** | **FALTA** | Nada | La latencia de salida en Android es el problema conocido del ecosistema (y no se menciona); tampoco qué pasa si entra una llamada, ni la decisión de si el juego silencia o convive con la música que el jugador ya tenía puesta (que en móvil es lo normal y afecta a la sesión) | Documentación de Android (OpenSL ES / AAudio); guidelines de iOS (`AVAudioSession`) |
| H8 | Móvil: permiso `RECORD_AUDIO` | **CUBIERTO** | `04 · 28` (`os_request_permission`, y la regla de pedirlo justo antes de usarlo) | — | Manual, `os_request_permission.htm` |

### I · Herramientas, middleware y ecosistema

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| I1 | **Vinyl** (guía en español) | **CUBIERTO** | `07 - Ecosistema/21 - Vinyl - audio avanzado (guía en español).md` — reproducción, mezclador por etiquetas, ducking, beat tracking y tabla de API «verificada en el código» | Detalle menor: no dice **qué versión**. Verificado hoy vía API de GitHub: `JujuAdams/Vinyl` ★61, MIT, último cambio **2026-07-08**, estable **6.3.4** y **6.4.2-beta** (junio de 2026). Un documento de librería sin versión envejece en silencio | Repo oficial (MIT) |
| I2 | Catálogo de librerías de audio de la comunidad | **CUBIERTO** | `11 - Código descargado/_CATALOGO.md` → «### Audio y música» (Vinyl, bard-audio, fml, wavload, Phonix, audioExt, LineAudio, Sonus, ExternalAudio, con ★, licencia y fecha real); resumen en `12 - Utilidades.../05 - Pipeline de arte, audio y niveles.md` → «## 5. Audio» | — | API de GitHub (fechas reales) |
| I3 | **FMOD** (extensión oficial `GMEXT-FMOD`) | **PARCIAL** | Se lista en `07 · 09 §5`, `12 · 05 §5` y el catálogo (★74, Apache-2.0, **2026-08-12** — verificado hoy), con la recomendación correcta («salta a FMOD solo si tienes un diseñador que ya trabaja con FMOD Studio») | No hay ni una línea de **cómo se usa**: qué instala la extensión, cómo se cargan los banks, y el criterio real de coste (build, plataformas soportadas, licencia de FMOD por facturación del estudio). Es la única vía a música interactiva de nivel estudio y está a nivel de fila de tabla | `YoYoGames/GMEXT-FMOD` |
| I4 | **Wwise: estado real** | **FALTA** | **Cero menciones en toda la biblioteca** (grep de `Wwise`: sin resultados) | Falta decir explícitamente que **no hay integración mantenida**. Verificado hoy en la API de GitHub: `CaKlassen/gmwwise` ★26, último cambio **2022-10-17**; `Fatdazz/lib-GMWwise` ★2, **2021-01-25**. No hay nada más. Un LLM que no lo lea puede proponer Wwise como si fuera una opción viva; y la pregunta «¿puedo usar Wwise?» es de las primeras que hace quien viene de Unity/Unreal | API de GitHub (consultada el 6-09-2026) |
| I5 | Herramientas de creación (Audacity, Bfxr, jsfxr, Bosca Ceoil, Famitracker, LSDJ, M8) | **CUBIERTO** | `07 · 09` → «## 5. Herramientas de audio»; `03 · 09` → «## 7. Música digital: LSDJ y DirtyWave M8» | Detalle menor: falta **LMMS** (DAW libre, el escalón natural después de Bosca Ceoil) y ChipTone en la tabla | — |
| I6 | Bancos de sonido y música ya hechos | **CUBIERTO** | `07 · 09` → «### 2.5 Freesound.org (audio)» y «## 8. Bancos de música y SFX ya hechos (no generadores)» | — | Freesound, Kenney, OpenGameArt |

### J · Accesibilidad y QA

| # | Tema | Estado | Dónde | Qué falta | Fuente externa |
|---|---|---|---|---|---|
| J1 | Un slider **por categoría**, nunca uno maestro | **CUBIERTO** | `13 · 09 §8` (tabla de accesibilidad) + `§10.2` (error clásico) + `04 · 25` | — | Game Accessibility Guidelines |
| J2 | La regla de implementación: sonido informativo y su representación visual salen del **mismo evento** | **CUBIERTO** | `13 · 09 §8` (última regla, remitiendo a `04 · 16 — Señales`) | — | Game Accessibility Guidelines |
| J3 | La prueba de los 10 minutos con el volumen a cero | **CUBIERTO** | `13 · 09 §8` (🔺 final) | — | Práctica de accesibilidad |
| J4 | Checklist de audio antes de publicar | **CUBIERTO** | `13 · 09` → «### 10.1 Checklist antes de publicar» (9 puntos, todos con la sección donde se resuelven) + «### 10.2 Los errores que se repiten» (11 filas: síntoma → arreglo) | — | — |
| J5 | **QA de audio como pasada de pruebas** | **PARCIAL** | `13 · 09 §10.1` lo pide en dos líneas («escuchado en altavoces de portátil, en auriculares baratos y a volumen bajo; 30 minutos seguidos»); `13 - Diseño.../10 - Testing y QA.md` **excluye explícitamente el audio** de las pruebas automáticas («comprueba que *decides* reproducir el sonido correcto, no que suene») | `13 · 10` dice qué **no** se puede probar y no dice qué hacer en su lugar: matriz de dispositivos, protocolo de escucha, y qué sí es testeable (que la decisión de sonar se toma, que no se supera el cupo de voces, que ningún emisor queda sin liberar) | Práctica de QA de audio |
| J6 | Glosario de términos de audio | **PARCIAL** | `05 - Referencia/03 - Glosario GML.md` → única entrada: «**Audio bus**» | Faltan como entradas: *ducking*, *falloff*, *stinger*, *foley*, *round robin*, LUFS/dBTP, *bed*, *one-shot*, robo de voz, *sidechain*. Todos se usan en `13 · 09` sin estar en el glosario | — (deuda interna) |

---

## 2 · Propuestas priorizadas

### 🔴 ALTA

**P1 · `08 - Referencia GML completa/23 - Audio avanzado - buffers, colas, sincronía y grabación.md`**

Cierra las dos familias del runtime que hoy solo existen como nombres en `API-funciones.md` (B16,
B17, B18, D11) y da a `08` el documento de audio que le falta. Cuatro bloques: **sync groups** con
las 11 funciones reales y el caso que las justifica (capas de música que entran y salen sin desfase,
que es lo que `04 · 26` resuelve a mano); **buffer sounds y play queues** para generar tono y SFX en
ejecución, encadenar buffers sin hueco y reproducir audio que no venga de un asset; **grabación de
micrófono** con el evento async y la copia del buffer temporal antes de que se destruya; y
**Doppler** con `audio_emitter_velocity` / `audio_listener_velocity`. Fuente: el espejo español ya
tiene las 21 páginas (`.../Audio/Audio_Buffers/` y `.../Audio_Synchronisation/`), así que se escribe
sin salir de la biblioteca. Verificar cada firma con `buscar.py` y compilar el ejemplo.

**P2 · `04 - Recetas por género/32 - Audio reactivo al mundo - materiales, zonas y estados de mezcla.md`**

El hueco práctico más caro (D8, D9, C11, C12). Cuatro recetas encadenadas sobre el gestor que ya
existe en `13 · 09 §4.2`: **pasos por material** (leer el tile bajo los pies con
`tilemap_get_at_pixel`, mapear índice → banco de `banco_crear`, y disparar desde el broadcast
`"paso_der"` que `13 · 04` ya define); **zonas de reverberación** con `Reverb1` por ambiente y
transición interpolada, avisando de que solo alcanzan a lo que pase por emisores; **estados de
mezcla** declarados como structs (ganancia por bus + efectos + tiempo) con una función que interpola
entre ellos, sustituyendo los ejemplos sueltos de `02 · 07 §5.8-5.9`; y el **sistema de importancia**
de Overwatch, que `13 · 09 §1.3` explica y nadie implementa. Enlazar desde `13 · 09 §5` y `§9`, donde
la hoja de sonido ya presupone que esto existe.

**P3 · `06 - Assets y Scripts/scr_audio.gml` (+ entrada en su `README.md`)**

Ninguno de los nueve scripts compilados es de audio (B20). Consolidar en un solo script el gestor que
hoy está partido entre `01 · 13 §14` y `13 · 09 §4.2`: buses y emisores por categoría, `mezcla_aplicar`,
banco de tomas con round robin, cupo de voces con fundido, anillo de emisores posicionales, ducking y
crossfade de música. Es el fichero que un LLM copia y pega para tener audio decente en cualquier
proyecto, y el que debe entrar en `bash _indice/validar-compilacion.sh` para que el audio caiga bajo
la misma garantía de «cero errores» que el resto.

### 🟡 MEDIA

**P4 · `13 - Diseño y producción de videojuegos/14 - Voz, diálogo y localización de audio.md`**

Cubre G6, G7, G8 y G9, que hoy están repartidos entre «se pide y no se implementa» y «no existe».
Contenido: proceso de grabación (guion con contexto por línea, convención de nombres que encaje con
el `asset_get_index("voz_" + …)` de `04 · 10`, dirección, edición y normalización a la referencia de
0 dB); **localización de voz** (asset por idioma, resolución en runtime, fallback a solo subtítulos,
impacto en el tamaño de build) — y añadir el enlace desde `04 · 21`, que hoy no menciona el audio;
sistema de **subtítulos de efectos** con indicador direccional, que `04 · 27 §2` y `13 · 09 §8` piden
sin resolver; y **lip-sync básico** en 2D por amplitud. La reproducción y el timing ya están resueltos
en `13 · 12 §6.9`: este documento no los repite, los presupone.

**P5 · Secciones nuevas en `04 - Recetas por género/26 - Música adaptativa por capas.md`**

Le falta la mitad horizontal del par que toda la literatura presenta junto (E6, E7, E8). Añadir:
«## Transición horizontal: cambiar de tema sin cortar» (segmentos con puntos de salida legales,
segmento puente opcional, cola del anterior sobre la entrada del siguiente, apoyado en el
`seg_por_compas` que el documento ya calcula); «## La música como máquina de estados» (tabla estado →
capas activas → tiempo de fundido, y qué hacer cuando dos estados se solapan); y una sección corta de
**escribir la música para que esto funcione** (misma tonalidad en todas las capas, dónde poner el
punto de bucle, instrumentación reservada por capa).

**P6 · Secciones en `04 · 17 (HTML5)` y `04 · 28 (móvil)`**

H2 y H7. En HTML5: la pantalla de «pulsa para empezar» como gesto de desbloqueo del contexto, con
`audio_system_is_available()` antes de arrancar la música y qué hacer con la música de la pantalla de
carga; hoy es una línea de tabla que enuncia el problema y no lo resuelve. En móvil: latencia de
salida por plataforma, interrupción por llamada entrante, y la decisión de si el juego silencia o
convive con la música que el jugador ya tenía puesta.

**P7 · Actualizar `07 - Ecosistema/09 §5` y `12 - Utilidades e integraciones/05 §5`**

I3, I4, I5. Añadir la fila que falta: **Wwise no tiene integración mantenida** —`CaKlassen/gmwwise`
★26 sin tocar desde 2022-10-17, `Fatdazz/lib-GMWwise` desde 2021— con la alternativa (buses nativos +
Vinyl, o FMOD oficial si de verdad hace falta middleware). Añadir un mínimo de **cómo se usa
GMEXT-FMOD** (★74, Apache-2.0, 2026-08-12) y su coste real. Y completar la tabla de herramientas con
**LMMS** y **ChipTone**. Anotar en `07 · 21` la versión de Vinyl (6.3.4 estable / 6.4.2-beta).

### 🟢 BAJA

**P8 · Sección «Audio en 3D» en `04 - Recetas por género/29 - 3D en GameMaker.md`**

D12. El documento tiene 928 líneas y no menciona el audio. Añadir: `audio_listener_orientation` con
su firma real alimentada desde la cámara 3D cada frame (lookat + up), emisores con `z` real, falloff
en unidades de mundo, y por qué un oyente 2D en un juego 3D no distingue delante de detrás. Enlazar
desde `01 · 13 §6`, que hoy escribe la función con puntos suspensivos.

**P9 · Entradas de audio en `05 - Referencia/03 - Glosario GML.md`**

J6. El glosario tiene una sola entrada de audio («Audio bus») mientras `13 · 09` usa a diario
*ducking*, *falloff*, *stinger*, *foley*, *round robin*, LUFS/dBTP, *bed*, *one-shot*, robo de voz y
*sidechain*. Diez entradas cortas, cada una con el enlace a la sección donde se aplica.

**P10 · Sección «El motor del vehículo» en `04 - Recetas por género/12 - Carreras y vehículos.md`**

El documento tiene el derrape con `audio_sound_pitch` variable, pero no el caso canónico de SFX con
parámetro continuo: un bucle de motor cuyo tono sigue las revoluciones, o tres capas
(ralentí / medio / alto) con crossfade por velocidad. Es la receta que se reutiliza en cualquier
maquinaria, ventilador o nave.

**P11 · Sección «Probar el audio» en `13 - Diseño y producción de videojuegos/10 - Testing y QA.md`**

J5. El documento excluye el audio de las pruebas automáticas y no dice qué hacer en su lugar. Añadir:
qué **sí** es testeable (que la decisión de sonar se toma, que no se supera el cupo de voces, que todo
emisor se libera en su Clean Up), la matriz de dispositivos de escucha, y el protocolo de sesión larga
que `13 · 09 §10.1` ya pide en dos líneas.

---

## 3 · Limitaciones de esta auditoría

- **Sin WebSearch.** La sesión había agotado su presupuesto (200/200 llamadas) antes de empezar, así
  que no pude hacer búsquedas web. Lo compensé con: el **espejo local del manual**
  (`09 - Manual oficial/manual-lts-2026-es/`), la **API de GitHub por `curl`** (fechas, estrellas,
  licencias y releases reales de Vinyl, GMEXT-FMOD, gmwwise y lib-GMWwise, consultadas hoy), y una
  **descarga directa con `curl -A "Mozilla/5.0"`** del tutorial oficial `gamemaker.io/en/tutorials/audio-effects`
  (HTTP 200, 121 KB, consistente con lo que cita `13 · 09`).
- **Fuentes bibliográficas no reabiertas.** *The Game Audio Tutorial* (Stevens & Raybould, 2011),
  *Game Audio Implementation* (2016), las charlas de GDC de Overwatch, Celeste y Hades, y los
  artículos de A Sound Effect y Designing Sound los cito **de conocimiento del dominio**, no de una
  lectura hecha en esta sesión. La propia biblioteca ya advierte en `13 · 09` que las fichas de los
  dos libros dieron HTTP 403 en la web del editor. Los temas que atribuyo a esas fuentes son
  canónicos del oficio, pero no he verificado hoy número de capítulo ni cita literal.
- **No abrí `11 - Código descargado/` en profundidad**, salvo para verificar los nombres de la API de
  Vinyl contra `librerias/audio/Vinyl/scripts/`. Hay nueve librerías de audio descargadas
  (bard-audio, Sonus, Phonix, audioExt, LineAudio, ExternalAudio, fml, wavload,
  Simple-Dynamic-Audio-Demo) cuyo contenido no he auditado: es posible que alguna resuelva ya alguno
  de los huecos que propongo escribir, y **conviene mirarlas antes de redactar P2 y P5**.
- **No ejecuté ningún compilado.** Ninguna de mis propuestas incluye código verificado con
  `gm-cli compile`; las firmas que menciono sí las comprobé con `python3 _indice/buscar.py --listar audio_`
  (130 símbolos `audio_*`) y contra el espejo del manual, pero el código de las propuestas está por
  escribir y por compilar.
- **No edité nada de la biblioteca**, según el brief. Este informe es el único artefacto.
