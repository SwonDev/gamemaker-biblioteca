# 09 · Diseño de sonido y mezcla

> El **oficio** del audio, no su API: qué sonidos necesita tu juego, cómo se construye cada uno, a
> qué nivel relativo va cada cosa, cómo se coloca en el espacio y cómo se comprueba antes de
> publicar. No se repite ninguna firma del **runtime** — reproducción, emisores, buses, efectos y
> grupos están en [01 · 13 — Audio](../01%20-%20Fundamentos/13%20-%20Audio.md) y
> [02 · 07 — Audio: buses y efectos](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md).
> La música por capas, en [04 · 26](../04%20-%20Recetas%20por%20género/26%20-%20Música%20adaptativa%20por%20capas.md);
> la librería Vinyl, en [07 · 21](../07%20-%20Ecosistema/21%20-%20Vinyl%20-%20audio%20avanzado%20%28guía%20en%20español%29.md).
>
> ✅ **Unificado con
> [`06 - Assets y Scripts/scr_audio.gml`](<../06 - Assets y Scripts/scr_audio.gml>).** Hasta la
> ronda anterior este documento y `scr_audio.gml` definían, por separado, dos sistemas de audio
> completos e incompatibles con ~10 nombres de función coincidentes (`mezcla_aplicar`, `sonar_en`,
> `sonar_limitado`, `voz_decir`, `voces_paso`, `apagar_con_fundido`, `banco_crear`,
> `banco_siguiente`, `ambiente_poner`, `variacion_tono`, `variacion_ganancia`) y globals distintos.
> Ya no: **el código vive únicamente en `scr_audio.gml`**, con los nombres de global que ya usaban
> este documento y las recetas construidas encima (`global.bus.*`, `global.em.*`,
> `global.volumen_*`) — son los que citan de verdad `04 · 26`, `04 · 42`, `04 · 45`, `13 · 10` y
> `13 · 24`. `scr_audio.gml` absorbió además lo que aquí faltaba: `sfx()`, `sfx_ui()` y
> `musica_poner()` como funciones reales (antes solo descritas), y las cifras de *headroom* y
> *ducking* de abajo son las mismas que usan sus macros (`AUDIO_HEADROOM_*`, `AUDIO_DUCK_*`).
> **Este documento ya NO redefine esas funciones**: explica la teoría (por qué esas cifras, por
> qué esa curva, el mapa de bandas de EQ, LUFS…) y remite al script para el código. La única
> diferencia de comportamiento real que sobrevivió a la unificación —`sonar_limitado()` sin
> `emitter` por defecto— está señalada en §3.3, con el porqué.
> Aquí se decide **qué** suena, **cuándo**, **a qué nivel** y **por qué**.

---

## 1 · Los principios

### 1.1 Las cuatro cosas que hace el sonido

Si un sonido no hace ninguna de estas cuatro, sobra.

| Función | Qué resuelve | Ejemplo | Si falta |
|---|---|---|---|
| **Feedback** | Confirma que **ya ha pasado** algo que el jugador provocó | click del salto, impacto | El juego se siente muerto y el mando «llega tarde», aunque el input sea perfecto |
| **Información** | Avisa de algo que el jugador **no ve** y **va a pasar** | pasos a la espalda, carga de un ataque, vida baja | El juego parece injusto: mueres sin poder reaccionar |
| **Emoción** | Da temperatura a la escena sin decir nada | música, reverberación de cueva, silencio antes del jefe | Todo tiene el mismo tono |
| **Identidad** | Hace tu juego reconocible en dos segundos | el salto de Mario, el ping de una carta | El juego suena a plantilla |

Lo que más se falla es confundir feedback con información. El feedback confirma el pasado y puede
ser corto y seco; la información anuncia el futuro y necesita **tiempo de reacción**: si el aviso
de un ataque dura 120 ms y el ataque llega en 150 ms, no sirve de nada. **Un sonido informativo se
diseña desde el tiempo de reacción hacia atrás.**

### 1.2 «Todo lo que pasa suena» — y dónde está el límite

Regla de producción: **todo cambio de estado perceptible tiene que sonar**; si algo se ve y no
suena, el cerebro lo registra como un fallo. El límite es la **fatiga**: Bjørn Jacobsen la formalizó
como *nuisance score*, la suma de molestias mínimas —una repetición, una frecuencia que pincha, un
sonido más alto de la cuenta— que el jugador no sabe identificar pero que a los veinte minutos le
hacen bajar el volumen.

> 🔺 **La regla que ordena todo lo demás: cuanto más se repite un sonido, más bajo, más corto y
> más variado tiene que ser.** Frecuencia y prominencia son inversamente proporcionales.

| Veces por minuto | Tratamiento |
|---|---|
| **> 60** (pasos, motor, teclas) | −18 a −24 dB · < 150 ms · 5-8 tomas · variación de tono obligatoria |
| **10 – 60** (disparo, salto, golpe) | −6 a −12 dB · < 400 ms · 3-5 tomas |
| **1 – 10** (puerta, objeto, subir nivel) | −3 a −8 dB · hasta 1 s · 2-3 tomas |
| **< 1** (jefe, muerte, logro) | 0 a −3 dB · sin límite · una toma memorable |

### 1.3 «Oír siempre lo importante»

En la charla de GDC 2016 sobre *Overwatch*, Scott Lawlor y Tomas Neumann cuentan que probaron *HDR
audio* (el sonido más fuerte gana y aplasta a los demás) y lo descartaron por «blanco o negro». Lo
sustituyeron por un **sistema de importancia**: cada sonido puntúa según el daño que hace, la
distancia y si se ve al enemigo, y esa puntuación lo mete en un cubo (alto, normal, bajo,
descartado). Su lema, de Walter Murch, es *«Dense Clarity, Clear Density»*: puedes tener muchísimo
sonido, mientras lo importante siga oyéndose.

**La jerarquía de tu mezcla es una decisión de diseño que escribes en una tabla antes de tocar un
slider.** Si no la escribes, la decide el último sonido que importaste.

---

## 2 · Categorías y presupuesto de sonido

De este reparto salen los buses, los sliders de opciones y las prioridades.

| Categoría | Qué entra | Posicional | Prioridad | Tomas |
|---|---|---|---|---|
| **SFX de jugador** | salto, ataque, daño, pasos, habilidades | No (sí en cooperativo) | 20-40 | 3-5 |
| **SFX de mundo y enemigos** | disparos, impactos, puertas, trampas, destrucción | **Sí** | 10-20 | 3-5 |
| **UI** | mover, confirmar, cancelar, error, notificación | Nunca | 60-80 | 1-2 |
| **Ambiente** | *beds* en bucle + *one-shots* esporádicos | Bed no · one-shots sí | 5-90 | bed 1 · one-shots 4-8 |
| **Música** | temas, capas, *stingers* | No | 100 | — |
| **Voz** | diálogo, narrador, esfuerzos | Según el juego | 100 | 3-5 los esfuerzos |

> 💡 **La UI nunca es posicional.** Un botón no está en el mundo: si suena atenuado o paneado a un
> lado, es un bug.

**Lista mínima por género**, los sonidos sin los cuales el género no se lee. Cada celda cuenta
sonidos distintos, no tomas: multiplica por la columna «Tomas» para saber cuántos ficheros son.

| Género | SFX jugador | SFX mundo/enemigos | UI | Ambiente | Música |
|---|---|---|---|---|---|
| **Plataformas 2D** | salto, aterrizaje, pasos, daño, muerte, dash | moneda, checkpoint, enemigo pisado, plataforma, pincho, puerta | menú ×4, pausa | bed por bioma (3) + one-shots | menú, 2-3 niveles, jefe, victoria |
| **Top-down / twin-stick** | disparo, recarga, daño, muerte, dash | impacto en pared, impacto en carne, muerte ×3 tipos, casquillo, explosión | menú ×4, subir nivel | bed por zona + one-shots | exploración, combate, jefe |
| **Shoot'em up** | disparo ×3 armas, bomba, escudo, muerte | impacto, explosión pequeña/grande, power-up, aviso de jefe | menú ×4, récord | drone de motor continuo | menú, fase ×2, jefe |
| **RPG / Action RPG** | ataque ×3 armas, bloqueo, daño, curación, pasos ×4 superficies | crítico, muerte ×4 enemigos, cofre, puerta, trampa | menú ×6, inventario, equipar, comprar, error | pueblo, mazmorra, bosque, cueva | pueblo, mapa, combate, jefe, victoria, triste |
| **Roguelike** | ataque, daño, muerte, objeto, habilidad ×3 | enemigos ×5, puerta de sala, cofre, altar | menú ×4, elección de objeto | bed por piso (4) | menú, piso ×4, jefe |
| **Puzzle / Match-3** | seleccionar, mover, combo ×3 niveles, deshacer | caída de pieza, explosión de combo, tiempo agotándose | menú ×4, estrella, nivel superado | bed suave único | menú, juego, tenso |
| **Tower Defense** | colocar, mejorar, vender, colocación inválida | disparo por torre (×N), muerte de enemigo, fuga de vida, oleada | menú ×4, oleada, victoria/derrota | bed del mapa | menú, oleada, jefe |
| **Novela visual** | avanzar texto, elegir, auto-play | — | menú ×6, guardar, cargar, historial | bed por escenario (5-8) | tema por personaje (3-5), tensión, romántico |
| **Carreras** | motor (bucle con tono variable), derrape, freno, cambio, choque | rebufo, chispa, público, cuenta atrás | menú ×4, vuelta, meta | bed de circuito | menú, carrera, victoria |
| **Arcade / un botón** | acción única, muerte, punto | obstáculo pasado, récord batido | menú ×3 | bed único | menú, juego (1-2), récord |

> 🔺 **La UI es lo que más se olvida y lo que más se oye.** Cuatro sonidos de menú se pulsan cientos
> de veces: si uno chirría, el juego chirría. Interfaz en
> [13 · 05 — UI y UX de juego](./05%20-%20UI%20y%20UX%20de%20juego.md).

⚠️ Dimensionado orientativo, de experiencia de producción y **no de fuente publicada**: prototipo
12-20 sonidos (15-25 ficheros) · *vertical slice* 40-60 (90-150) · juego publicado 120-250 (300-600).

---

## 3 · Diseñar un efecto de sonido

### 3.1 Transitorio, cuerpo y cola

| Capa | Cuándo | Qué aporta | De dónde sale | Si falta |
|---|---|---|---|---|
| **Transitorio** | 0-20 ms | el golpe, la posición temporal exacta, la fuerza | un click, un chasquido, un *snare* recortado | llega tarde y no «pega» |
| **Cuerpo** | 20-200 ms | el material y el tamaño: metal, carne, piedra | la grabación principal, un tono grave, ruido filtrado | suena a click de ratón, sin peso |
| **Cola** | 200 ms-2 s | el espacio: sala pequeña, cañón, exterior | reverberación, escombros, resonancia | suena pegado a la cara, sin mundo |

Frank Bry lo explica desde la compresión: en una explosión real la cola puede estar **40 dB por
debajo** del ataque en los primeros 500 ms, y por eso la grabación en crudo «suena floja» hasta que
un compresor con el *release* bien puesto levanta cuerpo y cola sin tocar el transitorio.

> 💡 **En GameMaker la cola te la puede dar el motor.** Un fichero con transitorio + cuerpo, y la
> cola es un `AudioEffectType.Reverb1` en el bus de la zona: el mismo disparo suena en la cueva y
> en campo abierto sin duplicar assets.

**Cuánto debe durar:** click de UI 40-80 ms · paso 80-150 ms · disparo ligero 120-250 ms · impacto
200-500 ms · explosión 1-2,5 s · muerte 1-2 s · *stinger* 2-4 s. **Si dura más que la animación que
acompaña, sobra cola; si dura menos, falta cuerpo.**

### 3.2 Variaciones y *round robin*

Un solo fichero repetido cincuenta veces es el error más audible del audio de juegos. La solución
tiene dos mitades y hay que aplicar las dos: **varias tomas del mismo sonido** y **aleatorización de
tono y ganancia**. Solo con lo segundo, el oído reconoce el mismo fichero acelerado; solo con lo
primero, tres tomas en bucle son un patrón detectable al minuto. El tono se piensa en **semitonos**,
no en porcentajes: `±1,5 semitonos` es un multiplicador entre 0,91 y 1,09 —el «±10 %» de toda la
vida— y no desafina nada.

> El código real —`variacion_tono()`, `variacion_ganancia()`, `banco_crear()` y
> `banco_siguiente()`— vive en
> [`06 - Assets y Scripts/scr_audio.gml`](<../06 - Assets y Scripts/scr_audio.gml>): mismas firmas
> y mismos valores por defecto que los de aquí abajo. No los redeclares en tu proyecto; impórtalo.

```gml
// ── Uso ──
// Create:  banco_pasos = banco_crear([snd_paso_1, snd_paso_2, snd_paso_3, snd_paso_4]);
// Al pisar:
audio_play_sound_ext({
    sound : banco_siguiente(banco_pasos), priority : 8,
    gain  : db_to_lin(-20) * variacion_ganancia(2),      // los pasos van MUY bajos
    pitch : variacion_tono(2)
});
```

### 3.3 Prioridad, voces y el límite que te falta

GameMaker admite **128 voces simultáneas por defecto**, y cuando se llenan decide la prioridad. Eso
protege el motor, no tu mezcla: veinte impactos idénticos en un frame caben de sobra en 128 voces y
suenan como un cañonazo de ruido con el volumen sumado. **El límite que necesitas es por sonido, y
lo escribes tú.**

> El código real —`voces_iniciar()`, `apagar_con_fundido()`, `voces_paso()` y `sonar_limitado()`—
> vive en
> [`06 - Assets y Scripts/scr_audio.gml`](<../06 - Assets y Scripts/scr_audio.gml>). `voces_iniciar()`
> una vez (en `rm_init`, o dentro de `audio_init()` si ya usas el sistema completo) · `voces_paso()`
> cada frame (ya la llama `audio_step()`). Roba la voz MÁS ANTIGUA al llenarse el cupo: un cupo de
> 3-5 voces por sonido arregla el 90 % de las mezclas sucias de un juego indie, y es más barato y
> más eficaz que un compresor.
>
> ⚠️ **`sonar_limitado()` no pasa `emitter` por defecto**: el sonido sale por el bus principal, sin
> el coste de calcular un emisor y sin que le afecten el volumen de "Efectos" ni ningún efecto
> colgado de un bus propio. No es un descuido: es la opción correcta para un sonido que se dispara
> muchas veces por segundo (los pasos de `04 · 42` §1.2/§3.1, que documenta el porqué con detalle).
> Si el sonido SÍ necesita pasar por un bus, pásalo explícitamente con el quinto parámetro:
> `sonar_limitado(snd_impacto_metal, 4, db_to_lin(-8), 15, global.em.sfx)`.

```gml
// Uso: como mucho 4 impactos idénticos a la vez, por el bus principal (barato)
sonar_limitado(snd_impacto_metal, 4, db_to_lin(-8), 15);

// Uso: igual, pero que respete el volumen de "Efectos" y la reverberación de zona (§3.2, §5.2)
sonar_limitado(snd_impacto_metal, 4, db_to_lin(-8), 15, global.em.sfx);
```

---

## 4 · La mezcla

### 4.1 La jerarquía de niveles

⚠️ Punto de partida de práctica común, no norma publicada: lo que importa no son las cifras sino
**el orden y la separación** —dos categorías a menos de 3 dB competirán—.

| Categoría | Nivel relativo | Lineal | En código |
|---|---|---|---|
| **Voz / diálogo** | 0 dB (la referencia) | 1,00 | — |
| **SFX críticos del jugador** (daño, muerte) | −2 a −4 dB | 0,79 – 0,63 | `db_to_lin(-3)` |
| **SFX frecuentes del jugador** (ataque, salto) | −6 dB | 0,50 | `db_to_lin(-6)` |
| **SFX de enemigos y mundo** | −8 dB | 0,40 | `db_to_lin(-8)` |
| **UI** | −8 a −10 dB | 0,40 – 0,32 | `db_to_lin(-9)` |
| **Música** | −8 a −12 dB | 0,40 – 0,25 | `db_to_lin(-10)` |
| **Ambiente (bed)** | −18 a −24 dB | 0,13 – 0,06 | `db_to_lin(-20)` |

> 💡 **La música siempre por debajo de los SFX; la voz siempre por encima de todo.** Si tu música
> necesita estar por encima de los efectos para apreciarse, el problema es que los efectos ocupan
> sus frecuencias: eso se arregla con EQ (§4.3), no subiendo la música.

### 4.2 Cómo se montan de verdad los buses en 2026

Hay una limitación documentada que cambia toda la arquitectura y que no se descubre hasta tener el
mezclador escrito:

> **Los buses propios solo se pueden usar con emisores de audio.** El audio 2D
> (`audio_play_sound`), el 3D (`audio_play_sound_at`) y el de emisor acaban enrutados al bus
> principal; solo lo que pasa **por un emisor asignado a un bus** recibe sus efectos y ganancia.
> — Manual, *Audio Effects*.

| Quiero… | Herramienta correcta |
|---|---|
| Sliders de volumen por categoría en Opciones | **Grupos de audio** (`audio_group_set_gain`), como en [04 · 25](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md). Funcionan con cualquier reproducción |
| Compresor o limitador sobre TODO | El **bus principal**: siempre lo recibe todo |
| EQ solo en la música, o *ducking* con efectos | **Bus propio + emisor de categoría**, reproduciendo con la clave `emitter` |
| SFX posicional que además pase por el bus de efectos | **Emisores colocados en el mundo**, no `audio_play_sound_at` |

> El código real de todo lo anterior —el `obj_audio` Create/Step/Clean Up con sus cinco buses y
> cinco emisores de categoría, `mezcla_aplicar()`, `voz_decir()` y el ducking de música mientras
> hay diálogo— vive en
> [`06 - Assets y Scripts/scr_audio.gml`](<../06 - Assets y Scripts/scr_audio.gml>), detrás de tres
> únicas llamadas: `audio_init()` en el Create de tu controlador persistente, `audio_step()` en su
> Step, `audio_destruir()` en su Clean Up. No repitas este bloque en tu proyecto.

| Slider (0..1) | Bus | *Headroom* | En código |
|---|---|---|---|
| `global.volumen_musica` | `global.bus.musica` | −10 dB | `AUDIO_HEADROOM_MUSICA` |
| `global.volumen_sfx` | `global.bus.sfx` | −6 dB | `AUDIO_HEADROOM_SFX` |
| `global.volumen_ui` | `global.bus.ui` | −9 dB | `AUDIO_HEADROOM_UI` |
| `global.volumen_voz` | `global.bus.voz` | 0 dB (la referencia) | — |
| `global.volumen_ambiente` | `global.bus.ambiente` | −20 dB | `AUDIO_HEADROOM_AMBIENTE` |

> ⚠️ El ducking de `audio_step()` usa `lerp` con factor fijo: depende de la tasa de frames, a 30 fps
> el fundido tarda el doble. Si no fijas los fps, corrige el factor con `delta_time`
> ([04 · 15](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md)) — pendiente de
> aplicar en `scr_audio.gml` si tu proyecto no fija los fps.

### 4.3 Compresor, «limitador» y EQ para hacer sitio

**GameMaker no trae limitador.** El sustituto es un `Compressor` con ratio muy alto y ataque mínimo
en el **último hueco** del bus principal: hace de techo blando y evita que el recorte digital
ensucie el sonido cuando explotan diez cosas a la vez.

```gml
// obj_audio · Create (continuación) — red de seguridad del master
var _techo = audio_effect_create(AudioEffectType.Compressor);
_techo.ingain    = 1.0;
_techo.threshold = db_to_lin(-3);   // ≈ 0.708 · rango documentado 0.001 - 1
_techo.ratio     = 20;              // 20:1 es prácticamente un limitador
_techo.attack    = 0.001;           // el mínimo documentado (0.001 - 0.1 s)
_techo.release   = 0.15;            // rango documentado 0.01 - 1 s
_techo.outgain   = 1.0;

// ⚠️ El manual dice que los efectos se pueden REORDENAR manipulando el array, de lo que se
// deduce que el índice es el orden de procesado, pero no lo afirma con esas palabras. Por si
// acaso, el techo va en el último hueco, donde nada puede esquivarlo.
audio_bus_main.effects[7] = _techo;

// Hacer sitio a la voz: un valle de −4 dB centrado en 2 kHz, permanente, en la música
var _hueco = audio_effect_create(AudioEffectType.PeakEQ);
_hueco.freq = 2000;   _hueco.q = 1.5;      // rangos documentados: 10-20000 Hz y 1-100
_hueco.gain = db_to_lin(-4);               // ganancia LINEAL: menor que 1 es recorte
global.bus.musica.effects[0] = _hueco;
```

**El mapa de bandas**, para saber a quién quitarle sitio: **20-80 Hz** son explosiones y sub del
bombo (paso alto con `HPF2` a 40-60 Hz en todo lo demás); **80-250 Hz** es el cuerpo de casi todo
(recórtalo en pasos y UI, que no necesitan graves); **400-800 Hz** es el «barro» que se acumula sin
aportar (suele mejorar con −2 dB en el bus de ambiente); **1,5-3 kHz** es la inteligibilidad de la
voz y los transitorios, reservado a voz y SFX críticos; y **6-12 kHz** es el aire y el siseo, lo
primero que fatiga: sospecha ahí si algo pincha.

> 💡 **Ajusta los parámetros del efecto ANTES de asignarlo al array.** Asignarlo es lo que lo
> activa, y con los valores por defecto se oye el salto.

### 4.4 Loudness: las cifras que sí están publicadas

| Norma | Ámbito | Nivel objetivo | True Peak máx. |
|---|---|---|---|
| **ASWG-R001 v1.10** (Sony WWS, ago. 2013) | juegos en consola de sobremesa | **−24 (±2) LKFS** | **−1 dBTP** |
| **ASWG-R001 v1.10** | juegos en consola portátil | **−18 (±2) LKFS** | **−1 dBTP** |
| **EBU R 128 v5.0** (nov. 2023) | radiodifusión (referencia habitual en PC) | **−23,0 LUFS ±1,0 LU** | **−1 dBTP** (±0,3 dB) |
| **Spotify** | música en streaming | **−14 LUFS** | **−1 dBTP** (−2 si va más alto) |

Lo que casi nadie aplica del ASWG-R001, y es su parte útil: se mide con un medidor conforme a
**ITU-R BS.1770-3** (`LKFS` y `LUFS` son **la misma unidad**); se mide **la mezcla entera**, no solo
el diálogo ni solo la música; se mide durante **30 minutos como mínimo** sobre un recorte
representativo de todo el juego; y el margen de −1 dBTP tiene una razón concreta: el remuestreo y el
filtrado en tiempo real **suben** los picos, igual que la mezcla de envolvente a estéreo. GameMaker
no mide loudness; `ffmpeg` sí, con el medidor EBU R 128 integrado:

```sh
ffmpeg -i captura_partida.wav -af ebur128=peak=true -f null -
#   Integrated loudness:  I:  -21.8 LUFS      True peak:  Peak: -21.1 dBFS
#   Loudness range:       LRA: 20.0 LU
```

> 🔺 **Graba 20-30 minutos de partida real** —menú, exploración, combate, jefe, pausa— y mide eso:
> un SFX medido a solas no dice nada del loudness del juego.
>
> ⚠️ En PC no hay norma obligatoria. Referencia práctica **extrapolada** de las dos anteriores:
> entre **−23 y −18 LUFS integrados con el pico por debajo de −1 dBTP**. Por encima de −16 LUFS tu
> juego será más alto que casi todo lo demás, el jugador bajará el volumen del sistema y perderás
> la dinámica que tanto trabajaste.

### 4.5 El mezclador de sonido del IDE

Existe y casi nadie lo usa: **Herramientas → Mezclador de sonido**. Arrastras varios sound assets
—o un grupo de audio entero— a columnas, los reproduces juntos y ajustas sus volúmenes
**relativos** escuchándolos a la vez; las columnas se pueden enlazar para moverlas juntas.

> 💡 **Es la forma correcta de fijar el volumen por defecto de cada asset** (el deslizador «Volume»
> del Editor de sonido). Ese valor se **multiplica** por la ganancia de instancia
> ([02 · 07 §2.3](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md)), así que
> dejarlo todo a 1 significa hacer la mezcla entera desde el código, sonido a sonido. Fija ahí los
> relativos una vez y el código solo moverá categorías.

---

## 5 · Sonido posicional en 2D

### 5.1 La atenuación: el ajuste que todo el mundo olvida

> ⚠️ **El modelo por defecto es `audio_falloff_none`**, y con él la ganancia vale siempre 1. Si no
> lo cambias, tus emisores y tu `audio_play_sound_at()` suenan igual de fuerte a dos píxeles que a
> dos pantallas. Es, con diferencia, el bug de audio más frecuente.

```gml
// obj_audio · Create — se elige UNA vez; es global para todo el juego
audio_falloff_set_model(audio_falloff_inverse_distance_clamped);
```

| Modelo | Curva | Cuándo |
|---|---|---|
| `audio_falloff_none` | plana | El defecto. Solo si no quieres atenuación en ninguna parte |
| `audio_falloff_linear_distance_clamped` | recta | Predecible y fácil de razonar; bueno con vista fija |
| `audio_falloff_inverse_distance_clamped` | 1/d | El más «natural»: cae rápido cerca, despacio lejos |
| `audio_falloff_exponent_distance_clamped` | potencia | Control fino de la curva con el factor |
| Variantes `_scaled` | — | Garantizan silencio total a la distancia máxima |

Los tres números de cada emisor: **referencia** (donde empieza a bajar; media pantalla es buen punto
de partida), **máxima** (donde deja de bajar; pantalla y media) y **factor** (`1` neutro; `0` la
desactiva en todos los modelos salvo los `_scaled`).

### 5.2 Un anillo de emisores, y dónde va el oyente

Si quieres sonido posicional **y** que pase por tu bus de efectos, `audio_play_sound_at()` no
sirve: el audio 3D va directo al bus principal. La solución es un anillo de emisores reutilizables.

> El código real —`emisores_iniciar(_cantidad, _bus)`, `emisores_liberar()`, `sonar_en()` y el
> posicionado del oyente en la cámara cada frame— vive en
> [`06 - Assets y Scripts/scr_audio.gml`](<../06 - Assets y Scripts/scr_audio.gml>), ya integrado en
> `audio_init()` / `audio_step()` / `audio_destruir()`. Las referencias de atenuación del anillo
> (240 · 720 · 1) están en sus macros `AUDIO_ANILLO_FALLOFF_REF` / `AUDIO_ANILLO_FALLOFF_MAX`.
>
> ⚠️ **Reutilizar un emisor MUEVE los sonidos que sigan sonando en él.** Con SFX cortos (< 500 ms) y
> 16-32 emisores no se nota; para bucles largos (un fuego, una cascada) usa un emisor dedicado
> (§5.3 hace exactamente eso).

> 🔺 **En un juego con zoom, el oyente en la cámara falla**: al alejarse todo enmudece a la vez. O
> escalas la distancia de referencia con el zoom, o dejas el oyente en el jugador y aceptas la
> desincronización visual. Elige y escríbelo: los dos caminos tienen coste.

### 5.3 Oclusión barata: una pared se come los agudos

Un rayo, un filtro paso bajo y una interpolación. Es lo que hace el tutorial oficial de GameMaker
con el diálogo «al otro lado de la pared».

```gml
// ═══════════ obj_fuente_ambiental — un bucle largo (fuego, máquina, cascada) ═══════════

// ─── Create ───  emisor propio y dedicado, con su bus y su filtro
em = audio_emitter_create();  bus = audio_bus_create();  audio_emitter_bus(em, bus);
audio_emitter_falloff(em, 180, 640, 1);  audio_emitter_position(em, x, y, 0);
ef_oclusion = audio_effect_create(AudioEffectType.LPF2);
ef_oclusion.cutoff = 18000;   // abierto: no filtra nada audible · q va de 1 a 100
ef_oclusion.q      = 1;
bus.effects[0] = ef_oclusion;
oclusion = 0;                 // 0 = despejado · 1 = totalmente tapado
voz = audio_play_sound_ext({ sound : snd_fuego, loop : true, priority : 5, emitter : em });

// ─── Step ───  el oyente está en el centro de la cámara, igual que en §5.2
var _cam = camera_get_active();
var _lx = (_cam == -1) ? x : camera_get_view_x(_cam) + camera_get_view_width(_cam)  * 0.5;
var _ly = (_cam == -1) ? y : camera_get_view_y(_cam) + camera_get_view_height(_cam) * 0.5;
var _tapado = (collision_line(x, y, _lx, _ly, obj_pared, false, true) != noone);

oclusion = lerp(oclusion, _tapado ? 1 : 0, 0.12);     // sin interpolar se oye un "zip" artificial
ef_oclusion.cutoff = lerp(18000, 700, oclusion);      // los agudos se van primero
bus.gain           = lerp(1, db_to_lin(-8), oclusion);

// ─── Clean Up ───  apagar_con_fundido(voz, 120); audio_emitter_free(em);
//                  el bus no se libera: lo recoge el recolector de basura solo
```

> 💡 **La oclusión gradual es información, no realismo.** En *Overwatch* midieron cuánto tiene que
> desviarse el sonido para llegar (5 %, 30 %, 100 %) precisamente para que el jugador distinguiera
> «pared fina» de «dos salas más allá». Un `bool` no comunica eso.

### 5.4 Dentro y fuera de pantalla

Lo que ves ya te informa; lo que no ves tiene que informarte **solo** con el sonido.

```gml
function en_pantalla(_px, _py, _margen = 64)
{
    var _cam = camera_get_active();
    if (_cam == -1) { return true; }
    var _x1 = camera_get_view_x(_cam) - _margen, _y1 = camera_get_view_y(_cam) - _margen;
    return (_px >= _x1 && _px <= _x1 + camera_get_view_width(_cam)  + _margen * 2
         && _py >= _y1 && _py <= _y1 + camera_get_view_height(_cam) + _margen * 2);
}

// El enemigo que carga un ataque: margen generoso para avisar antes de aparecer
if (en_pantalla(x, y, 260))
{
    var _refuerzo = en_pantalla(x, y, 0) ? 1 : db_to_lin(2);      // +2 dB si NO se ve
    sonar_en(snd_enemigo_carga, x, y, _refuerzo, 30);
}
```

Fuente **visible** → nivel normal, la imagen ya lleva la información. Fuente **fuera de pantalla y
relevante** → +2 a +3 dB y prioridad alta, es el único aviso que tiene el jugador. Fuente **fuera
de pantalla e irrelevante** → no reproducir: gasta una voz y suma al *nuisance score*.

---

## 6 · Ambiente y música

Un ambiente tiene dos piezas, y confundirlas es lo que hace que un bosque suene a bucle. El **bed**
es un bucle largo, continuo y sin nada que destaque —**cuanto más aburrido, mejor**: un rasgo
reconocible vuelve audible el bucle; 30-60 s como mínimo—. Los **one-shots** son sonidos sueltos que
le dan vida, disparados **a intervalos aleatorios**, nunca fijos, y desde posiciones distintas.

```gml
// obj_ambiente_bosque · Create
banco_aves = banco_crear([snd_ave_1, snd_ave_2, snd_ave_3, snd_ave_4]);
siguiente  = 0;

// obj_ambiente_bosque · Step
siguiente -= 1;
if (siguiente <= 0)
{
    var _fps  = game_get_speed(gamespeed_fps);
    siguiente = irandom_range(4 * _fps, 14 * _fps);       // entre 4 y 14 s: nunca fijo

    var _cam = camera_get_active();
    if (_cam != -1)      // en un punto cualquiera de la vista: el pájaro está "por ahí"
    {
        sonar_en(banco_siguiente(banco_aves),
                 camera_get_view_x(_cam) + irandom(camera_get_view_width(_cam)),
                 camera_get_view_y(_cam) + irandom(camera_get_view_height(_cam)), db_to_lin(-14), 4);
    }
}

```

Cambia el bed con `ambiente_poner(_sonido, [_ms])` — 2000-4000 ms hacen que el cambio de zona no
se note como un corte, los dos beds suenan a la vez durante el cruce, uno bajando y otro subiendo.
La música se cambia igual, con `musica_poner(_sonido, [_ms])` (mismo crossfade, mismo patrón, otro
bus). El código real de ambas —comparten la misma implementación genérica por dentro— vive en
[`06 - Assets y Scripts/scr_audio.gml`](<../06 - Assets y Scripts/scr_audio.gml>); no las
redeclares.

Los *stingers* están cubiertos en
[04 · 26](../04%20-%20Recetas%20por%20género/26%20-%20Música%20adaptativa%20por%20capas.md); lo de
oficio que toca aquí es que **un stinger fuera del tono y el tempo de la música de fondo suena a
bug**, y ningún GML lo arregla. Y **el silencio es el recurso más barato y el menos usado**: cortar
la música 2-4 s antes de que se abra la puerta del jefe hace la entrada; 300-500 ms de silencio
total antes del sonido de muerte marcan el corte; y dejar la música fuera un par de minutos entre
zonas, tras media hora de juego, reinicia el oído. Sincronizar acciones con el compás está en
[04 · 19 — Programación rítmica](../04%20-%20Recetas%20por%20género/19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md).

---

## 7 · Formatos y ajustes de importación

Los ajustes viven en el **Editor de sonido**, sección *Atributos*.

| Tipo de sonido | Origen | Atributo | Grupo de audio |
|---|---|---|---|
| SFX corto (< 2 s): pasos, UI, disparos | **WAV** | **Sin comprimir** | Sí |
| SFX medio (2-8 s): explosión con cola | WAV u OGG | **Comprimido** o **Descomprimir al cargar** | Sí |
| Ambiente en bucle (30-60 s) | **OGG** | **Descomprimir al cargar**, o **Comprimido - Streamed** si es el de la zona inicial | Solo si no es *streamed* |
| Música (2-5 min) | **OGG** | **Comprimido - Streamed** | ❌ Los *streamed* no van a grupos |
| Voz / diálogo largo | **OGG** | **Comprimido - Streamed** | ❌ |

> ⚠️ **Un SFX de 50 ms en OGG es un error**: la descompresión añade latencia justo donde importa y
> el ahorro es de kilobytes. WAV sin comprimir, siempre.
>
> ⚠️ **Un bucle en OGG puede tener un hueco al repetir** (el *encoder* añade silencio de relleno).
> Si tu bucle «respira» al dar la vuelta, prueba sin comprimir o define los puntos de bucle en
> código ([02 · 07 §4](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md)).
>
> ⚠️ **En HTML5 el audio *streamed* se trata como no *streamed*** por una limitación de los
> navegadores, y puede no estar listo cuando el juego ya ha cargado: comprueba con
> `audio_sound_is_playable()` antes de reproducirlo.

**Opciones de destino.** Los valores por defecto documentados son **16 bits, 44 100 Hz y 128 kbps**,
adecuados en general. Merece la pena apartarse en tres casos: **22 050 Hz** para SFX sin contenido
agudo (golpes sordos, pasos en tierra: mitad de memoria, inaudible); **96 kbps** para beds largos de
fondo; y **192 kbps** solo para música que sea argumento de venta.

> **Todo lo que reproduzcas posicionalmente tiene que ser mono (o «3D»).** «3D» y «mono» son
> exactamente lo mismo: «3D» es solo una etiqueta del IDE para que nadie elija estéreo por error, y
> se exporta como mono. — Manual, *El editor de sonido*.

Música y ambiente en bucle van en **estéreo**: la anchura es la mitad de su efecto. La UI da igual.

**Presupuesto de memoria.** `WAV sin comprimir = frecuencia × (bits / 8) × canales × segundos`: un
disparo mono de 300 ms a 44 100 Hz y 16 bits ocupa ~26 KB, pero 3 minutos de música estéreo sin
comprimir son **~31 MB**; por eso la música va comprimida y en *streaming*. Para medirlo en
ejecución, la ventana **Audio** del Debug Overlay lista las fuentes que suenan o podrían sonar, con
estado y ganancia ([01 · 15](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md)): es
lo que responde a «¿por qué se me han acumulado cuarenta voces?». Los **grupos de audio** cargan y
descargan bloques por zona, y su identificador **es el nombre que le diste en la ventana de Grupos
de audio**: es un asset del proyecto, no un símbolo del runtime, así que no sale en `buscar.py`.

**Normalizar antes de importar.** Importar cada sonido a un volumen distinto convierte la mezcla en
una partida de topos. Deja todos los SFX con el pico verdadero en el mismo sitio y ajusta los
relativos en el Mezclador de sonido del IDE (§4.5).

```sh
ffmpeg -i disparo.wav -af volumedetect -f null -                            # → max_volume: -21.1 dB
ffmpeg -i disparo.wav -af "volume=18.1dB" -ar 44100 -ac 1 disparo_norm.wav  # deja el pico en −3 dB
ffmpeg -i bed.wav -af "loudnorm=I=-20:TP=-1.5:LRA=11" -ar 44100 -ac 2 bed_norm.wav
```

> 💡 **Los SFX se normalizan por pico; la música y el ambiente, por loudness.** Un SFX normalizado
> por loudness pierde el transitorio, que es justo lo que le da el golpe.

---

## 8 · Herramientas, licencias y accesibilidad

Las tablas de generadores, editores y bancos ya están en la biblioteca y **no se repiten**:
[07 · 09 §5 y §8](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md) (Audacity,
Bfxr, jsfxr, Bosca Ceoil, Freesound) y
[03 · 09](../03%20-%20Cursos%20%28YouTube%29/09%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%209%20-%20Sonidos%20y%20Música.md)
(foley casero, jsfxr paso a paso, copyright). Lo que sí es decisión de producción:

| Origen | Regla |
|---|---|
| Generado (jsfxr, Bfxr, ChipTone) | Es tuyo. Ideal para prototipar en una tarde |
| Freesound **CC0** | Sin riesgo; anota igualmente autor y URL |
| Freesound **CC-BY** | Atribución obligatoria: olvidarla es incumplir la licencia |
| Freesound **CC-BY-NC** | ⛔ **No sirve para un juego que vendas**, ni con «paga lo que quieras» |
| Grabado por ti (foley) | Lo que más identidad da y lo más barato |
| Sacado de otro juego o película | ⛔ Nunca. Ni «solo para el prototipo»: se queda |

> 🔺 **Lleva la hoja de créditos desde el primer sonido** (fichero, autor, URL, licencia).
> Reconstruirla con 300 ficheros dentro es una tarde perdida y un riesgo legal real.

### 8 bis · Un agente sin archivo de audio: la escalera de prioridad

La pregunta que responde esta sección no es «¿de dónde saco sonido?» (eso es la tabla de arriba
y [07 · 09](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md)): es
**«necesito un efecto AHORA MISMO, y no tengo ningún archivo — ¿qué hago sin salir de la
biblioteca?»** Es el caso real de un agente de IA construyendo un juego sin artista de sonido, y
la respuesta ya estaba escrita en
[08 · 24 §3](../08%20-%20Referencia%20GML%20completa/24%20-%20Audio%20avanzado%20-%20buffers%2C%20colas%2C%20sincronía%20y%20grabación.md#3--buffer-sounds-síntesis-y-audio-procedural-en-tiempo-real),
sin que nada apuntara a ella desde aquí.

**El orden, de lo que un agente puede hacer siempre a lo que depende de herramientas externas:**

1. **Sintetizar con `audio_create_buffer_sound()`** — cero dependencias, cero archivos, cero
   conexión a internet: solo GML. `tono_generar()` y `ruido_generar()` de 08 · 24 §3 ya están
   escritas y probadas; lo único que falta es saber que **cubren el catálogo básico de un juego
   entero**, no solo el ejemplo de una explosión con el que se presentaron.
2. **Generador externo (jsfxr, Bfxr, ChipTone)** si el agente tiene acceso a shell o navegador —
   tabla completa en [07 · 09 §8](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md)
   y paso a paso en
   [03 · 09](../03%20-%20Cursos%20%28YouTube%29/09%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%209%20-%20Sonidos%20y%20Música.md).
   Da más control tímbrico que la síntesis en runtime, a cambio de un paso fuera de GameMaker.
3. **`PLACEHOLDERS.md` extendido a audio** si ninguna de las dos anteriores es aceptable ahora
   mismo (por ejemplo, un sonido que de verdad necesita grabación real, como una voz). El patrón
   de placeholder de
   [13 · 11 §5](./11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md#5--assets-y-pipeline)
   («nombre definitivo desde el principio, se lista en `PLACEHOLDERS.md`, se vacía en beta») hoy
   solo se aplica a arte — extiéndelo tal cual: un sonido silencioso o sintetizado con el nombre
   de asset definitivo (`snd_jugador_muerte` con un `ruido_generar()` de 08 · 24 §3 en vez de
   una grabación), listado en la misma tabla.

**Qué se puede sintetizar razonablemente, y qué no.** `audio_create_buffer_sound()` genera **PCM
puro** — sin instrumentos, sin voz, sin timbre grabado — así que lo que suena bien es lo que ya
suena a «señal», no a «objeto del mundo real»:

| Se sintetiza razonablemente bien | No razonable por síntesis — busca un archivo de verdad |
|---|---|
| Disparo, láser, hechizo (tono corto y agudo) | Voz humana o diálogo — usa [13 · 24](./24%20-%20Voz%2C%20diálogo%20y%20localización%20de%20audio.md) |
| Salto, rebote (tono corto con pitch alto) | Foley realista: pasos sobre grava, tela, agua |
| Recogible, moneda, «ding» de acierto | Instrumentación con melodía o música completa |
| Impacto, golpe, explosión pequeña (ruido con caída) | Ambientes con textura orgánica (bosque, ciudad, multitud) |
| Clic, confirmar, cancelar, error de UI | Cualquier sonido que el jugador deba reconocer como «grabado de la realidad» |

**El catálogo mínimo**, con `tono_generar(_frecuencia_hz, _duracion_seg)` y
`ruido_generar(_duracion_seg)` de 08 · 24 §3 tal cual, sin modificarlas:

```gml
// Disparo / láser: agudo y muy corto — la brevedad vende "energía", no el timbre
var _disparo = tono_generar(1200, 0.08);
audio_play_sound(_disparo.sonido, 60, false);

// Salto: un tono corto con el pitch subido en la reproducción, no en la síntesis
var _salto     = tono_generar(440, 0.10);
var _id_salto  = audio_play_sound(_salto.sonido, 50, false);
audio_sound_pitch(_id_salto, 1.3);

// Moneda / recogible: dos tonos en rápida sucesión — el "ding-ding" clásico
var _moneda_a = tono_generar(988,  0.05);   // Si5
var _moneda_b = tono_generar(1319, 0.08);   // Mi6, una quinta por encima
audio_play_sound(_moneda_a.sonido, 40, false);
alarm_set(0, 3);                             // el segundo tono, 3 frames después (01 · 06)

// Impacto / golpe: ruido_generar() ya está pensado exactamente para esto
var _impacto = ruido_generar(0.12);
audio_play_sound(_impacto.sonido, 70, false);

// Interfaz (clic, confirmar, cancelar): muy corto, casi sin cuerpo
var _clic = tono_generar(1600, 0.03);
audio_play_sound(_clic.sonido, 30, false);
```

> ⚠️ No olvides `audio_free_buffer_sound()` + `buffer_delete()` cuando el sonido termine (08 · 24
> §3, tabla de errores clásicos) — cada llamada de la lista de arriba crea un buffer nuevo, y
> sin liberarlo se acumula igual que cualquier otra fuga de memoria.

**Accesibilidad.** Todo lo que el sonido comunica **en exclusiva** es información que no recibe quien
es sordo o juega sin volumen —y jugar sin volumen es mucho más común que la sordera.

| Necesidad | Qué implementar | Dónde |
|---|---|---|
| Diálogo comprensible | **Subtítulos activables** con nombre del hablante | [04 · 27 §2](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) |
| Efectos importantes | **Subtítulos de efectos**: `[puerta crujiendo]`, `[pasos detrás]` | [04 · 27 §2](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) |
| Avisos direccionales | Indicador en el borde de pantalla apuntando a la fuente | §5.4 · [13 · 05](./05%20-%20UI%20y%20UX%20de%20juego.md) |
| Control del jugador | **Un slider por categoría**, no uno maestro | [04 · 25](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md) |
| Fatiga y sobrecarga | Opción de reducir sonidos repetitivos o bajar el ambiente aparte | §1.2 |

> 🔺 **La prueba honesta: juega tu juego con el volumen a cero durante diez minutos.** Todo lo que
> dejes de entender es una barrera que estabas ignorando.

Regla de implementación: **cualquier evento que dispare un sonido informativo debe disparar también,
en el mismo sitio del código, su representación visual.** Si están en sitios distintos, uno se
desincronizará; la forma limpia es emitir una señal única que escuchen audio e interfaz
([04 · 16](../04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md)).

### 8 quater · Generar audio con IA — y por qué aquí la licencia va PRIMERO

El arte tiene su peldaño de IA escrito y probado (`12 · 09 §5.2` peldaño 3, `07 · 23`). El audio
no lo tenía, y la asimetría se notaba: un agente sin compositor se quedaba en la síntesis del
§8 bis, que cubre los efectos pero **no la música**, que es donde de verdad no puede improvisar.

**Pero en audio el orden se invierte respecto al arte: la licencia se mira antes que la calidad**,
porque la herramienta abierta más conocida no se puede usar en un juego que vendas. Verificado
leyendo cada licencia el 09-09-2026, no de memoria:

**Todo lo de esta tabla está comprobado el 09-09-2026 leyendo el repositorio y su licencia**,
con la fecha del último cambio a la vista — porque en esto lo que valía hace un año ya no vale:

| Herramienta | Estado | Código | **Pesos del modelo** | ¿Sirve para un juego comercial? |
|---|---|---|---|---|
| [`audio.cpp`](https://github.com/0xShug0/audio.cpp) — 2 380 ★ | 🟢 **vivo**, último cambio **hoy** (creado en junio de 2026) | **Apache-2.0** | Uno por familia — 62 familias, música incluida (MiniMax Music 3, ACE-Step 1.5 XL) | **Es la vía práctica hoy.** Motor en C++ puro sobre `ggml`: **sin Python, sin Conda**, GGUF cuantizado, y corre en CPU, CUDA, Metal y ROCm. Justo lo que un agente puede invocar desde una terminal |
| [`stable-audio-tools`](https://github.com/Stability-AI/stable-audio-tools) — 3,9 k ★ | 🟢 vivo, último cambio hoy | MIT | *Stability AI Community License*; el modelo está **gated** en HuggingFace | **Depende de tu facturación**: esa licencia pone un umbral de ingresos. Léela entera y guárdate la fecha antes de publicar |
| [`audiocraft`](https://github.com/facebookresearch/audiocraft) — MusicGen/AudioGen, 23,6 k ★ | 🟡 **quieto desde marzo de 2026** | MIT | 🔴 **CC-BY-NC 4.0** | **NO, y por eso está en esta tabla.** Es la que más gente encuentra primero por sus 23 mil estrellas, y su propio README lo dice: *«The models weights in this repository are released under the CC-BY-NC 4.0 license»* |
| Servicios hospedados (ElevenLabs, Suno, Magnific…) | — | — | — | **Lo que diga TU plan**, no lo que diga la portada: los derechos de uso comercial van atados al nivel de suscripción |

> 🔴 **Y la regla que generaliza el caso de MusicGen: la licencia del programa NO es la licencia
> del modelo.** `audio.cpp` es Apache-2.0 y eso no dice nada sobre los pesos que le cargues:
> cada familia de modelos trae los suyos. Mira **las dos** antes de publicar, siempre, y anota la
> fecha en la que las leíste.

> 🔴 **El error caro es de los que no dan ningún síntoma.** Un `.ogg` generado con MusicGen suena
> igual de bien que uno con licencia limpia, entra en el proyecto igual, compila igual y se
> publica igual. El problema aparece cuando el juego ya está a la venta. Es exactamente la misma
> familia que la fuente muda o el *included file* que no se copia: **compila, corre y miente**,
> solo que aquí la factura no la paga el jugador.

**Dónde encaja en la escalera del §8 bis**: entre el peldaño 2 y el 3, **no por encima de la
síntesis**. Y la razón no es ideológica:

- Para **efectos**, la síntesis del §8 bis y jsfxr siguen ganando: son gratis, deterministas,
  offline, sin licencia que leer, y un láser de arcade sintetizado suena mejor que uno generado.
- Para **música**, es al revés: un bucle de dos minutos no se sintetiza con `tono_generar()`, y
  ahí es donde la generación aporta lo que ninguna otra vía da.

**Y se declara igual que el arte.** Las reglas de divulgación de Steam e itch.io de
[`07 · 23 §4`](../07%20-%20Ecosistema/23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md#4--el-estado-legal-verificado-el-2026-09-07-con-fuente-primaria-y-fecha)
están escritas hablando de imágenes, pero **no distinguen el medio**: el formulario de Steam
pregunta por contenido generado por IA, no por arte generado por IA.

> ✅ **Qué caza el compilador y qué no — medido, no supuesto (09-09-2026).** Antes de
> recomendar una guarda conviene saber si hace falta, así que se probó:
>
> | Situación | `gm-cli compile` |
> |---|---|
> | `resource create type=sound` sin archivo, y **nadie lo referencia** en GML | ✅ **exit 0, limpio** — el compilador lo descarta por no usado |
> | El mismo sonido, **referenciado** desde el código | 🔴 **exit 1**: `Failed to convert audio file 'snd_x' - source file does not exist` |
>
> Es decir: **el asset sin archivo lo caza el compilador**, y bien —en cuanto lo uses—. Lo que
> NO caza es lo otro: un archivo que **sí existe y no suena** (silencio grabado, una conversión
> que salió vacía, un `.ogg` de 0 s). Ahí la duración sí es la medida:
>
> ```gml
> // En el arranque, con los sonidos que de verdad tienen que sonar:
> debug_exigir_sonidos([snd_musica_menu, snd_golpe, snd_moneda]);   // 06 · scr_debug.gml
> ```
>
> `audio_sound_length()` devuelve la duración en segundos, y está **medida en ejecución**:
> `bash _indice/validar-ejecucion.sh` comprueba en cada pasada que un `.wav` de medio segundo
> mide `0.50`. Igual que con la fuente: duración 0 prueba que no hay audio y es concluyente;
> duración > 0 prueba que hay algo, **no** que sea el sonido correcto ni que se oiga bien. Eso
> sigue siendo trabajo de una persona (§4).
>
> ⚠️ **Y la consecuencia práctica del cuadro de arriba**: que `gm-cli compile` salga limpio **no
> significa que todos tus assets de sonido tengan audio detrás** — solo que los que usas hoy lo
> tienen. Un agente que crea los assets en una fase y escribe el código en otra no se entera
> hasta la segunda.

### 8 ter · Un `.wav` como archivo, no solo en runtime

§8 bis resuelve la síntesis **en caliente**, dentro del juego en marcha — perfecta para un SFX
que se genera y se reproduce en el mismo frame. Pero hay un caso distinto: un asset de sonido
que necesita **persistir como archivo** — para importarlo con `resourcetool` antes de compilar,
para adjuntarlo a una build sin recompilar, o como salida de un sistema de voz procedural que
debe sobrevivir entre sesiones (`13 · 24 §6`). Para eso hace falta escribir un `.wav` de verdad
en disco, y la biblioteca no tenía receta — la síntesis de §8 bis vive solo en memoria de
GameMaker, nunca toca el disco.

La solución usa el módulo `wave` de la librería estándar de Python — **sin dependencias**, y con
el mismo criterio de envolvente que `tono_generar()`/`ruido_generar()` de
[`08 · 24` §3](../08%20-%20Referencia%20GML%20completa/24%20-%20Audio%20avanzado%20-%20buffers%2C%20colas%2C%20sincronía%20y%20grabación.md#3--buffer-sounds-síntesis-y-audio-procedural-en-tiempo-real),
para que el resultado suene igual de intencionado. **Verificado en esta sesión**: genera un
`.wav` real, confirmado con `file` (`RIFF ... WAVE audio, Microsoft PCM, 16 bit, mono 22050 Hz`)
y con `ffprobe`/`afinfo`, e importado sin errores en un proyecto de prueba:

```python
import wave, struct, random

def tono_generar_wav(ruta, frecuencia_hz, duracion_seg, amplitud=0.6, tasa=22050):
    """Onda cuadrada mono de 16 bits con ataque/caida cortos — mismo criterio que
    tono_generar() de 08 · 24 §3, pero escrita a un .wav real en disco."""
    n_muestras = round(tasa * duracion_seg)
    n_ataque = round(tasa * 0.005)
    n_caida = round(tasa * 0.05)
    muestras_x_ciclo = tasa / frecuencia_hz
    mitad_ciclo = muestras_x_ciclo / 2

    datos = bytearray()
    for i in range(n_muestras):
        env = 1.0
        if i < n_ataque:
            env = i / n_ataque
        elif i > n_muestras - n_caida:
            env = (n_muestras - i) / n_caida
        onda = 1.0 if (i % muestras_x_ciclo) < mitad_ciclo else -1.0
        valor = max(-32768, min(32767, int(onda * env * amplitud * 32767)))
        datos += struct.pack("<h", valor)

    with wave.open(ruta, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)       # 16 bits
        f.setframerate(tasa)
        f.writeframes(bytes(datos))

def ruido_generar_wav(ruta, duracion_seg, amplitud=0.8, tasa=22050, semilla=None):
    """Ruido blanco mono de 16 bits con caida de potencia — equivalente a ruido_generar()
    de 08 · 24 §3, como archivo .wav."""
    if semilla is not None:
        random.seed(semilla)
    n_muestras = round(tasa * duracion_seg)
    datos = bytearray()
    for i in range(n_muestras):
        t = i / n_muestras
        env = (1 - t) ** 3
        valor = max(-32768, min(32767, int(random.uniform(-1, 1) * env * amplitud * 32767)))
        datos += struct.pack("<h", valor)

    with wave.open(ruta, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(tasa)
        f.writeframes(bytes(datos))

tono_generar_wav("snd_moneda.wav", 988, 0.15)
ruido_generar_wav("snd_impacto.wav", 0.12)
```

Impórtalo como cualquier otro asset de sonido — verificado con `gm-cli resourcetool` en esta
sesión, compilación limpia (`exit 0`) incluida:

```bash
gm-cli resourcetool eval "resource create type=sound name=snd_moneda"
gm-cli resourcetool eval "sound setfile name=snd_moneda path=snd_moneda.wav"
```

> ⚠️ Sigue siendo **PCM de 8 bits sin instrumentos ni timbre grabado** (la misma tabla de §8 bis
> de qué se sintetiza razonablemente bien y qué no aplica aquí tal cual): esta receta cambia
> *dónde vive* el sonido, no *qué tipo* de sonido es capaz de producir la síntesis. Para foley,
> voz o música real, sigue haciendo falta un archivo grabado — `07 · 09 §5` y §8.

---

## 9 · La hoja de sonido

Una tabla por sistema, rellenada **antes** de pedir o generar un solo fichero: convierte «hay que
ponerle sonidos» en una lista de trabajo cerrada que un LLM puede completar desde el diseño e
implementar sin volver a preguntar.

```markdown
## Hoja de sonido — <sistema>

| Evento (dónde salta) | Sonido | Tomas | Categoría | Prioridad | Posicional | Cupo | Nivel | Notas |
|---|---|---|---|---|---|---|---|---|
| `obj_jugador` Step · salta | `snd_salto` | 3 | SFX jugador | 30 | No | 2 | −6 dB | tono ±1,5 st |
| `obj_jugador` Step · pisa | `snd_paso_N` | 5 | SFX jugador | 8 | No | 3 | −20 dB | banco según superficie |
| `obj_bala` Collision · pared | `snd_impacto_pared` | 4 | SFX mundo | 15 | **Sí** | 4 | −8 dB | mono obligatorio |
| `obj_enemigo` · empieza carga | `snd_carga` | 1 | SFX mundo | 40 | **Sí** | 1 | −5 dB | informativo: +2 dB fuera de pantalla |
| `rm_cueva` Room Start | `snd_bed_cueva` | 1 | Ambiente | 90 | No | 1 | −20 dB | bucle ≥ 40 s, cruce 3000 ms |
| `obj_npc` · línea de diálogo | `voz_npc_NN` | 1 | Voz | 100 | No | 1 | 0 dB | ducking −9 dB + subtítulo |
```

Se rellena en este orden: **evento** (objeto y evento exactos; si no sabes dónde va la llamada, el
sonido no está diseñado) → **tomas** (§1.2, según veces por minuto) → **categoría** (§2, de ahí
salen bus y emisor) → **prioridad** (UI y voz altas, ambiente baja) → **cupo de voces** (§3.3) →
**nivel** (§4.1) → **notas** (mono/estéreo, duración, si es informativo, si lleva subtítulo).

---

## 10 · Checklist y errores clásicos

### 10.1 Checklist antes de publicar

- [ ] La hoja de sonido está rellena para **todos** los sistemas, no solo el combate.
- [ ] Ficheros normalizados a un pico común, relativos fijados en el Mezclador del IDE (§4.5, §7),
      todo lo posicional en **mono** y `audio_falloff_set_model()` llamado a mano (§5.1).
- [ ] Cada categoría tiene bus y emisor, Opciones mueve los cinco, la voz es la referencia, la
      música va 8-12 dB por debajo de los SFX del jugador y el ducking baja rápido (≈3 frames) y
      sube despacio (≈25) (§4.1, §4.2).
- [ ] Compresor-techo en el último hueco del bus principal (§4.3), y ningún sonido se para sin
      fundido: no hay clicks (§3.3).
- [ ] Cada sonido frecuente tiene 3-5 tomas, variación de tono y cupo de voces (§3.2, §3.3).
- [ ] 20-30 min de partida medidos: loudness entre −23 y −18 LUFS, pico **bajo −1 dBTP** (§4.4).
- [ ] Escuchado en altavoces de portátil, en auriculares baratos y a volumen bajo; 30 minutos
      seguidos sin que nada moleste (§1.2); y 10 minutos con el volumen a cero (§8).
- [ ] Ventana **Audio** del Debug Overlay sin voces acumuladas, y `audio_emitter_free()` llamado
      para **todos** los emisores en sus Clean Up (§4.2, §7).
- [ ] Probado en HTML5 si exportas ahí: *streaming*, buses limitados y el contexto que se pausa
      ([01 · 13 §11](../01%20-%20Fundamentos/13%20-%20Audio.md)).

### 10.2 Los errores que se repiten

| Error | Qué se oye | Arreglo |
|---|---|---|
| **Música al mismo nivel que los SFX** | Suena bien en el menú y tapa todo en combate | Música 8-12 dB por debajo (§4.1). Si no se aprecia, es EQ (§4.3), no volumen |
| **Cortar un sonido sin fundido** | *Click* seco al parar la música o cambiar de zona | `apagar_con_fundido()` con 30-60 ms (§3.3) |
| **Un solo sample de disparo** | Ametralladora robótica a los diez segundos | 3-5 tomas + `variacion_tono()` (§3.2) |
| **Posicional sin modelo de atenuación** | Todo suena igual de fuerte esté donde esté | `audio_falloff_set_model()`; el defecto es `audio_falloff_none` (§5.1) |
| **Oyente en el jugador con cámara adelantada** | Oyes lo que no ves | Oyente en el centro de la cámara (§5.2) |
| **OGG para un SFX de 50 ms** | Latencia perceptible al pulsar | WAV sin comprimir (§7) |
| **Esperar que un bus propio afecte a `audio_play_sound()`** | El efecto «no funciona» y no hay error | Los buses propios solo actúan sobre emisores (§4.2) |
| **One-shots de ambiente a intervalo fijo** | El pájaro canta cada 6,0 s exactos | `irandom_range` con rango ancho (§6) |
| **Volumen maestro único en Opciones** | Quien solo quiere quitar la música lo apaga todo | Un slider por categoría (§8) |
| **Master por encima de −1 dBTP** | Distorsión al comprimir o al mezclar a estéreo en consola | Compresor-techo (§4.3) y medir (§4.4) |
| **Stinger fuera de tono** | Parece un bug de audio | Mismo tono y tempo que la base ([04 · 26](../04%20-%20Recetas%20por%20género/26%20-%20Música%20adaptativa%20por%20capas.md)) |

---

## Ver también

- [`06 - Assets y Scripts/scr_audio.gml`](<../06 - Assets y Scripts/scr_audio.gml>) — el código real de todo lo que este documento explica: `audio_init`, `audio_step`, `audio_destruir`, `mezcla_aplicar`, `voces_iniciar`, `emisores_iniciar`, `emisores_liberar`, `variacion_tono`, `variacion_ganancia`, `banco_crear`, `banco_siguiente`, `apagar_con_fundido`, `voces_paso`, `sonar_limitado`, `sonar_en`, `sfx`, `sfx_ui`, `voz_decir`, `musica_poner`, `ambiente_poner`
- [01 · 13 — Audio](../01%20-%20Fundamentos/13%20-%20Audio.md) — la API completa: reproducción, voces, emisores, grupos, streaming, errores
- [02 · 07 — Audio: buses y efectos](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md) — `AudioEffectType`, parámetros de cada efecto, `audio_play_sound_ext`, puntos de bucle
- [04 · 26 — Música adaptativa por capas](../04%20-%20Recetas%20por%20género/26%20-%20Música%20adaptativa%20por%20capas.md) · [04 · 19 — Programación rítmica](../04%20-%20Recetas%20por%20género/19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md) — *vertical layering*, crossfade sincronizado, stingers y sincronía con el compás
- [04 · 25 — Menú de opciones](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md) · [04 · 27 — Accesibilidad](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) — sliders de volumen, subtítulos y avisos visuales
- [04 · 16 — Señales](../04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md) · [04 · 15 — Game feel](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) — disparar sonido e interfaz desde el mismo evento
- [04 · 00 — Anatomía de un juego completo](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md) — dónde encaja `obj_audio` entre los sistemas globales
- [07 · 21 — Vinyl](../07%20-%20Ecosistema/21%20-%20Vinyl%20-%20audio%20avanzado%20%28guía%20en%20español%29.md) — mezclador por etiquetas, ducking y beat tracking ya hechos
- [07 · 09 — Asset packs y recursos](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md) · [03 · 09 — Crear tus sonidos](../03%20-%20Cursos%20%28YouTube%29/09%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%209%20-%20Sonidos%20y%20Música.md) — herramientas, bancos, foley y copyright
- [01 · 15 — Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md) — la ventana Audio del Debug Overlay
- [13 · 05 — UI y UX de juego](./05%20-%20UI%20y%20UX%20de%20juego.md) · [05 · 04 — Convenciones y estilo GML](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) — sonidos de interfaz, y nombres, prefijos y reservados

---

## Fuentes

Todas consultadas el **6 de septiembre de 2026**.

**Manual oficial de GameMaker (LTS)** — espejo en `09 - Manual oficial/manual-lts-2026-es/`. Base
`https://manual.gamemaker.io/lts/en/`, y a continuación la ruta de cada página citada:

- `The_Asset_Editors/Sounds.htm` (atributos de importación, conversión OGG, opciones de destino, mono/estéreo/3D) · `IDE_Tools/Sound_Mixer.htm` (el mezclador del IDE) · `Settings/Audio_Groups.htm` (el ID del grupo es el nombre que le das en el IDE)
- `GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Effects/` → `Audio_Effects.htm` («los buses propios solo se pueden usar con emisores»), `AudioEffect.htm` (rangos exactos de Compressor, PeakEQ, LPF2, Reverb1, Delay), `AudioBus.htm` (`gain` 0-1, `effects` de tamaño fijo 8), `AudioEffectType.htm`
- `GameMaker_Language/GML_Reference/Asset_Management/Audio/` → `audio_falloff_set_model.htm` (fórmulas de cada modelo; el defecto es `audio_falloff_none`), `audio_channel_num.htm` (128 canales por defecto)

**Blog y tutoriales oficiales**

- Gurpreet S. Matharoo, *How To Use Audio Effects in GameMaker*, 30 de noviembre de 2022 — reverb en el bus principal; delay y paso bajo por bus propio + emisor; bitcrusher; y la nota de que los buses los recoge el GC pero los emisores hay que liberarlos: <https://gamemaker.io/en/tutorials/audio-effects>

**Normas de loudness (PDF originales, leídos)**

- Sony Worldwide Studios Audio Standards Working Group, **ASWG-R001 v1.10**, *Average Loudness and Peak Levels of Audio Content on Sony Computer Entertainment Platforms*, agosto de 2013 — −24 (±2) LKFS en sobremesa, −18 (±2) LKFS en portátil, True Peak ≤ −1 dBTP, medición ITU-R BS.1770-3, mínimo 30 minutos representativos, LKFS ≡ LUFS: <http://gameaudiopodcast.com/ASWG-R001.pdf>
- EBU, **R 128 v5.0**, *Loudness normalisation and permitted maximum level of audio signals*, noviembre de 2023 — −23,0 LUFS ±1,0 LU y True Peak máximo −1 dBTP (tolerancia ±0,3 dB): <https://tech.ebu.ch/publications/r128> · PDF <https://tech.ebu.ch/docs/r/r128.pdf>
- Spotify for Artists, *Loudness normalization* — −14 dB LUFS y True Peak por debajo de −1 dBTP: <https://support.spotify.com/us/artists/article/loudness-normalization/>

**Charlas y artículos del oficio**

- Scott Lawlor y Tomas Neumann (Blizzard), *Overwatch — The Elusive Goal: Play by Sound*, GDC 2016 — el sistema de importancia, el rechazo del HDR audio, «Dense Clarity, Clear Density» de Walter Murch, oclusión gradual por desvío del rayo: <https://www.youtube.com/watch?v=60P0hzTTJ4Q> · ficha <https://gdcvault.com/play/1023317/Overwatch-The-Elusive-Goal-Play> · diapositivas transcritas <https://archive.org/details/GDC2016Lawlor>
- Bjørn Jacobsen, *How to maintain immersion (+ reduce repetition & listening fatigue) in game audio*, A Sound Effect, 16 de mayo de 2018 — el *nuisance score*, construir cientos de variaciones por capas, y por qué pasos y puertas son los peores reincidentes: <https://www.asoundeffect.com/game-audio-immersion/>
- Alex Riviere, *Demystifying Game Audio Mixing*, A Sound Effect, 17 de julio de 2023 — mezcla base frente a *golden path*, reglas por tipo de sonido (paneo, loudness, espectro, dinámica) y priorización con side-chaining, ducking, HDR y *state mixing*: <https://www.asoundeffect.com/game-audio-mixing-demystified/>
- Frank Bry, *Transient Enhancement With Explosions*, Designing Sound, 21 de enero de 2013 — ataque, cuerpo y cola de una explosión, y cómo el *release* del compresor levanta la cola sin tocar el transitorio: <https://designingsound.org/2013/01/21/transient-enhancement-with-explosions/>


**Libros de referencia.** ⚠️ Datos tomados de las fichas de Routledge, O'Reilly y AbeBooks: la
página del editor devolvió HTTP 403 y no pude abrirla directamente.

- Richard Stevens y Dave Raybould, *The Game Audio Tutorial: A Practical Guide to Sound and Music for Interactive Games*, Focal Press, 2011, ISBN 978-0-240-81726-2 — <https://www.routledge.com/p/book/9780240817262>
- Richard Stevens y Dave Raybould, *Game Audio Implementation*, Focal Press, 2016, ISBN 978-1-138-77724-8

**Herramienta de medición.** `ffmpeg`, filtros `ebur128` (medidor EBU R 128 con pico verdadero),
`volumedetect` y `loudnorm`. Verificados ejecutándolos en esta máquina: la salida citada en §4.4 es
real. <https://ffmpeg.org/ffmpeg-filters.html#ebur128>

---

> ⚠️ **Marcado como no verificado:** los niveles relativos por categoría de §4.1 y los recuentos de
> sonidos de §2 son práctica común de producción, no cifras de una fuente publicada; el rango de
> −23 a −18 LUFS recomendado para PC en §4.4 es una **extrapolación** de las dos normas citadas, no
> una norma en sí; y las fichas de los dos libros no se pudieron abrir en la web del editor. Todo
> lo demás está contrastado contra el manual oficial, contra los PDF originales de las normas, o
> ejecutado en esta máquina.
