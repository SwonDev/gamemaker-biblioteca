# 41 · Transiciones, carga y pausa

> Cómo se sale de una sala, cómo se espera a que la siguiente esté lista, y qué significa de
> verdad «pausar». Tres problemas que parecen triviales y que son, juntos, la causa más común de
> bugs silenciosos: un jefe que sigue perdiendo vida con el menú de pausa abierto, una barra de
> carga que miente, un fundido que tapa el HUD a medias. Este documento no repite el fundido
> simple de [01 · 10 §9](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md#9-transiciones-entre-rooms)
> ni el `pausar()`/`reanudar()` básico de [00 · Anatomía §5](./00%20-%20Anatomía%20de%20un%20juego%20completo.md#5--el-bucle-de-juego-zonas-hud-pausa-guardado):
> los **extiende** hasta el punto en que de verdad se sostienen en un juego completo. No cubre
> el remapeo de controles ([25 · Opciones §5](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#5--reasignar-controles-rebinding))
> ni el diseño visual de los botones y el mapa de pantallas
> ([13/05 §2.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#21-el-mapa-de-pantallas-se-dibuja-antes-de-programar-nada)),
> que ya están resueltos y a los que este documento se engancha.

---

## 1 · Los principios

### 1.1 Una transición es una máquina de estados, no un `room_goto` con maquillaje

`room_goto()` cambia de sala en el mismo frame. Todo lo demás —el fundido, el wipe, el
iris— es **decoración alrededor de ese instante**, y por eso siempre tiene la misma forma,
sea cual sea el efecto visual:

```
   IDLE ──(pide ir a X)──▶ SALIENDO ──(cubierto al 100%)──▶ room_goto(X) ──▶ ENTRANDO ──▶ IDLE
```

Tres estados, dos disparadores. El error habitual es programar el efecto visual y el cambio de
sala como si fueran la misma cosa (`alpha += 0.05; if (alpha >= 1) room_goto(...)`), lo que
funciona para un fundido y se rompe en cuanto quieres un segundo tipo de transición, porque hay
que reescribir el `if`. Separar **estado** (dónde está la transición) de **forma** (qué tipo de
efecto dibuja) permite añadir un wipe o un iris sin tocar la máquina de estados: solo el `switch`
de dibujado. Ver §3.2.

### 1.2 Una barra de carga honesta mide lo que carga; una barra decorativa es peor que nada

GameMaker no da un porcentaje de bytes cargados: `texturegroup_get_status()` devuelve un
**estado discreto de 4 valores** (sin cargar → cargando → en RAM → en VRAM, ver
[08 · 08](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md#estados-de-un-grupo-de-textura)),
no una fracción continua. Frente a eso hay dos formas de mentir:

- **La barra que sube sola con un temporizador**, sin mirar si algo terminó de cargar de verdad.
  Si el disco es lento, llega al 100 % y el juego se congela igual un segundo más: el jugador
  deja de confiar en la barra la primera vez que se lo encuentra.
- **La barra que salta de 0 a 100 en dos frames** porque el SSD es rápido y la carga real dura
  40 ms. Técnicamente honesta, pero parece un parpadeo, no una carga, y en un juego con
  fotosensibilidad declarada es justo el tipo de destello que el checklist de accesibilidad
  prohíbe (ver [04 · 27 §…](./27%20-%20Accesibilidad.md), «nunca más de 3 destellos por segundo»).

La solución no es fingir progreso: es **medir el progreso real** (§3.3.2) y separar, con una
variable distinta, la **duración mínima** que debe estar visible la pantalla para que se lea como
una carga y no como un parpadeo (§3.3.3). Ninguna de las dos sustituye a la otra.

### 1.3 «Pausado» no es una variable: son media docena de sistemas que hay que parar por separado

`global.pausado = true;` no pausa nada por sí sola: es una etiqueta que tú lees en tu propio
código. Lo que de verdad congela el juego son las funciones que actúan sobre cada sistema, y
GameMaker tiene **cuatro familias de sistemas con reglas de pausa completamente distintas**:

| Familia | ¿Vive dentro de una instancia? | ¿La para `instance_deactivate_all`? |
|---|---|---|
| Step, Alarm, Collision, Draw, animación de sprite (`image_index`) | Sí | ✅ Sí — la instancia «deja de existir» mientras dure |
| Time Sources | No, son globales | ❌ No |
| Sistemas de partículas | No, son objetos del motor aparte | ❌ No |
| Sequences en una capa | No, viven en la capa | ❌ No |
| Física (Box2D) | El cuerpo cuelga de la instancia, pero el mundo físico es aparte | ❌ No — **lo dice el propio manual** (§3.1.7) |
| Audio | No, es un mezclador aparte | ❌ No, pero `audio_pause_all()` ya lo resuelve |

Esto significa que el `instance_deactivate_all(true)` de
[00 · Anatomía §5](./00%20-%20Anatomía%20de%20un%20juego%20completo.md#5--el-bucle-de-juego-zonas-hud-pausa-guardado)
—que **sí** es correcto y **sí** para Step, Alarm, Collision, Draw y la animación de sprite de
un plumazo— **no toca ni las Time Sources, ni las partículas, ni las Sequences, ni la física**.
Son sistemas que existen fuera del ciclo de instancias y que hay que pausar tú, uno por uno.
Ese es el tema del §3.1, y es la razón de que este documento exista: sin esa lista, cada
proyecto descubre uno de estos agujeros por accidente, normalmente en un directo o en una demo.

---

## 2 · El método, paso a paso

### 2.1 Elige el repertorio de transiciones — no metas las cinco

Un fundido a negro cubre el 90 % de los casos y no necesita justificación. Los demás tipos
comunican algo:

| Tipo | Qué transmite | Cuándo |
|---|---|---|
| **Fundido** | Neutro, no distrae | Entre salas normales, muerte → reintento |
| **Wipe** (cortina lateral) | Direccional, dinámico | Cambiar de zona en un mapa, avanzar en un nivel lineal |
| **Cortinas** (arriba/abajo) | Teatral, marca un final | Fin de capítulo, cinemática → gameplay |
| **Iris** | Focaliza la atención en un punto | Zoom a una puerta, a un jefe, clásico de cierre de escena |
| **Disolución con ruido** | Orgánico, texturizado | Estética retro/pixel art, cambios de realidad (sueño, flashback) |

Decide **una por defecto** (normalmente el fundido) y usa las demás como acento en momentos
concretos. Un juego que cambia de tipo de transición en cada sala no comunica nada: solo es
ruido visual.

### 2.2 Diseña la pantalla de carga: cuándo aparece y qué mide

Antes de escribir código, responde a tres preguntas:

1. **¿Qué grupos de textura pesan lo bastante como para justificar una pantalla de carga?**
   Si tu juego cabe entero en el grupo de texturas por defecto, no necesitas nada de esto: un
   fundido de la transición ya basta. La pantalla de carga real (§3.3) es para juegos que
   dividen sus assets en `texturegroup`s por zona.
2. **¿Cuál es la duración mínima aceptable?** Ni tan corta que parezca un parpadeo (1.3), ni
   tan larga que el jugador piense que se ha colgado (con un SSD moderno, 0.8-1.5 s suele
   bastar para que se lea como intencional).
3. **¿Qué hay que decir mientras se espera?** Un consejo rotativo cuesta una tabla de textos y
   evita la pantalla en blanco. No es obligatorio, pero es la diferencia entre «esto está
   cargando» y «esto se ha quedado pillado».

### 2.3 Diseña el menú de pausa: mapa de pantallas y qué se congela

El mapa de pantallas ya está resuelto en
[13/05 §2.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#21-el-mapa-de-pantallas-se-dibuja-antes-de-programar-nada):
Reanudar / Opciones (la misma pantalla que desde el menú principal) / Salir (con confirmación).
Lo que falta decidir es la mecánica:

1. **¿Qué congela la pausa?** Normalmente, todo: es una pausa real, el jugador puede tardar
   minutos en volver. Usa el congelado duro de §3.1.8.
2. **¿Qué se ve detrás del menú?** El mundo congelado y oscurecido de verdad (no un rectángulo
   negro liso) da más contexto: el jugador recuerda dónde estaba. Requiere capturar el último
   frame antes de congelar (§3.1.8) porque, si no, `instance_deactivate_all` también apaga el
   dibujado y el fondo desaparece.
3. **¿Qué pasa con el audio?** Como mínimo, `audio_pause_all()`. Como mejora, un *ducking* o un
   filtro de paso bajo (§3.4.3) que dice «esto sigue sonando, pero estás fuera del juego».
4. **¿Dónde NO se puede pausar?** Decídelo ahora, no lo descubras en QA (§3.4.6).

---

## 3 · Cómo se traduce a GameMaker

### 3.1 Pausar de verdad: el cimiento que usan las otras dos piezas

Tanto el motor de transiciones (§3.2, que congela el mundo mientras dura el efecto) como el
menú de pausa (§3.4) se apoyan en las mismas dos funciones: `pausar_de_verdad()` y
`reanudar_de_verdad()`. Se construyen aquí, en un fichero aparte (`scr_pausa.gml`), para no
duplicarlas.

#### 3.1.1 Instancias: lo que ya resuelve `instance_deactivate_all`

```gml
instance_deactivate_all(true);   // true = a quien llama NO se desactiva a sí mismo
```

Según el propio manual, una instancia desactivada **«deja de ser procesada de cualquier
manera»**: no corre Step, no corre Alarm, no se comprueban sus colisiones y **tampoco se
dibuja** — es, a efectos prácticos, como si no existiera hasta que se reactive. Eso incluye la
animación automática de sprite (`image_index` avanzando según `image_speed`), así que **no
hace falta tocarla a mano** si usas este camino. Es la comprobación que hace
[01 · 11 §11](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) al usar
`instance_deactivate_all` para *culling*: si las instancias desactivadas siguieran
dibujándose, esa técnica de rendimiento no ahorraría ninguna llamada de dibujado.

> 🔺 **Justo por eso desaparece el mundo detrás de un menú de pausa que solo hace
> `instance_deactivate_all`.** No es un bug de GameMaker: es que le has pedido exactamente eso.
> La solución está en §3.1.8 (capturar el frame antes de desactivar).

> 🔴 **Y esto es lo que muerde de verdad: `instance_exists()` devuelve `false` sobre una
> instancia desactivada.** También `instance_number()` deja de contarla. Así que **cualquier
> acción del menú de pausa que empiece con una guarda `instance_exists` es un no-op
> silencioso**: se pulsa el botón, suena, el menú se cierra y no pasa nada. Sin error, sin
> aviso. Lo sufrió un agente con un «Reiniciar nivel» que parecía obviamente correcto
> ([`r15` §2.4](../_indice/auditorias/r15-prueba-puzles.md)), y la superficie es mayor de lo que
> parece: cualquier función tuya de rejilla, de búsqueda o de colisión que use `instance_exists`
> por dentro devolverá un mundo vacío si se la llama desde la pausa.
>
> ```gml
> // MAL — durante la pausa esto no hace nada:
> if (instance_exists(global.nivel)) reiniciar_nivel(global.nivel);
> pausa_cerrar();
>
> // BIEN — reactivar primero, comprobar después:
> pausa_cerrar();                                    // hace el instance_activate_all()
> if (instance_exists(global.nivel)) reiniciar_nivel(global.nivel);
> ```
>
> **Ojo con lo que dice el manual, porque contesta a otra pregunta.**
> `instance_deactivate_object` avisa de que «la desactivación no es instantánea: la instancia no
> se considera inactiva hasta el final del evento». Es cierto —*sigue procesando eventos* ese
> frame— pero **no vale para `instance_exists()`**, que responde `false` ya en el mismo evento
> en que se desactiva. Medido, no deducido: `bash _indice/validar-ejecucion.sh` lo comprueba en
> un juego real en cada ejecución.
>
> Esto mismo se llevó por delante dos funciones de [`06 · scr_pool.gml`](../06%20-%20Assets%20y%20Scripts/scr_pool.gml),
> que guarda sus instancias libres desactivadas: recorrerlas filtrando por `instance_exists()`
> **vaciaba la lista entera**. Se arregla activando antes de preguntar.

#### 3.1.2 Lo que NO toca: Time Sources, partículas, Sequences y física

Ninguno de estos cuatro sistemas es una instancia, así que `instance_deactivate_all` los deja
exactamente como estaban:

- **Time Sources.** Corren en su propia fase del step (ver la tabla de
  [01 · 06 §4](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md#4-el-orden-exacto-de-cada-step)),
  **antes** incluso que las Alarmas. Nada de lo que hagas con instancias las toca.
- **Sistemas de partículas.** `part_system_create()` devuelve un identificador de motor, no una
  instancia; se actualizan solos cada step salvo que se lo desactives explícitamente con
  `part_system_automatic_update()`.
- **Sequences en una capa.** `layer_sequence_create()` cuelga de una **capa**, no de la
  instancia que la creó. Sigue reproduciéndose aunque esa instancia se desactive.
- **La física de Box2D.** Es la que tiene el aviso más explícito, y viene del propio manual de
  `physics_pause_enable`:

  > **NOTA**: Esto es especialmente útil si desea desactivar todas las instancias en un room, ya
  > que **incluso cuando se desactiva un cuerpo físico seguirá siendo calculado y simulado en el
  > mundo de la física**.

  Es decir: puedes desactivar la instancia de una caja con física, y la caja **seguirá
  cayendo** dentro del mundo de Box2D como si nada, invisible pero simulándose, hasta que
  aparece de golpe en una posición rara al reactivarla. Si tu juego usa Box2D, `physics_pause_enable(true)`
  no es opcional.

#### 3.1.3 El registro de sistemas pausables

Como no existe un `part_system_pause_all()` ni un `layer_sequence_pause_all()` (se han
comprobado y no están en el runtime), la única forma de pausarlos todos es **llevar tú la
cuenta** de cuáles existen. Un array global por familia basta:

```gml
// ─── Globales de inicio, junto a los del §1 de 00 · Anatomía ───
global.pausado                 = false;
global.registro_particulas     = [];   // Id.ParticleSystem que deben congelarse con el mundo
global.registro_secuencias     = [];   // structs { capa, elemento } — ídem para Sequences
global.surf_fondo_pausa        = -1;   // instantánea del último frame, ver §3.1.8
```

```gml
/// @func particulas_registrar_pausable(_sistema)
/// @desc Llama a esto justo después de cada part_system_create() que deba congelarse
///       cuando el juego se pause (los efectos de la propia UI de pausa, NO).
function particulas_registrar_pausable(_sistema) {
    array_push(global.registro_particulas, _sistema);
    return _sistema;
}

/// @func secuencia_registrar_pausable(_capa, _elemento)
/// @desc Igual, para cada layer_sequence_create() que deba pararse con el mundo.
function secuencia_registrar_pausable(_capa, _elemento) {
    array_push(global.registro_secuencias, { capa: _capa, elemento: _elemento });
    return _elemento;
}
```

> 💡 No registres **todo**: la lluvia de fondo del propio menú de opciones, o una partícula
> puramente cosmética del logo, probablemente no debe congelarse cuando el jugador pausa. El
> registro es una decisión de diseño por sistema, no una obligación automática.

#### 3.1.4 Time Sources: la jerarquía padre-hijo hace el trabajo por ti

`time_source_create()` acepta como primer argumento (`padre`) otra Time Source, no solo
`time_source_game` o `time_source_global`. Y el manual de `time_source_resume()` dice, en su
primera línea:

> Esta función reanuda la Fuente de Time Source dada **y sus hijos**.

Eso convierte el problema de «pausar N Time Sources sueltas» en «pausar una sola, la raíz»,
si desde el principio cuelgas todas las tuyas de ella en vez de colgarlas directamente de
`time_source_game`:

```gml
// ─── una vez, al arrancar el juego (rm_init, junto al resto de §1 de 00 · Anatomía) ───
global.ts_raiz_pausable = time_source_create(
    time_source_game, 1, time_source_units_frames,
    function() {},           // no hace nada: solo existe para agrupar a sus hijos
    [], -1, time_source_expire_after
);
time_source_start(global.ts_raiz_pausable);

/// @func time_source_pausable(_periodo, _unidades, _callback, _args, _repeticiones, _tipo)
/// @desc Igual que time_source_create(), pero cuelga de la raíz pausable en vez de
///       de time_source_game directamente. Úsala para CUALQUIER temporizador de
///       gameplay que deba respetar la pausa.
function time_source_pausable(_periodo, _unidades, _callback, _args = [],
                               _repeticiones = 1, _tipo = time_source_expire_after) {
    return time_source_create(global.ts_raiz_pausable, _periodo, _unidades,
                               _callback, _args, _repeticiones, _tipo);
}
```

Con esto, pausar TODAS las Time Sources del juego es una sola línea:
`time_source_pause(global.ts_raiz_pausable)`.

> ⚠️ El manual solo documenta el arrastre a los hijos para `time_source_resume()`, no para
> `time_source_pause()` en su propia página. No sería coherente que resumir arrastrase a los
> hijos y pausar no lo hiciera (¿qué sentido tendría reanudar algo que nunca se paró?), pero al
> no estar escrito igual de explícito en ambas páginas, **compruébalo con un caso de prueba en
> tu proyecto** antes de depender de ello a ciegas en producción.

#### 3.1.5 Alarmas: el contraataque en Begin Step (solo hace falta si NO desactivas instancias)

Si usas `instance_deactivate_all` (§3.1.1), las alarmas ya se paran solas: no hagas nada más.
Este apartado es para el otro patrón de pausa — el de **time scale 0** de
[04 · 15 §5.0](./15%20-%20Game%20feel%20y%20juice.md#50-sistema-de-tiempo-hit-stop-y-time-scale)—,
donde las instancias **siguen activas** a propósito (para que sigan dibujándose y
animándose) y solo el movimiento se congela consultando `time_delta()`.

El problema: las alarmas **no consultan tu código**. Según la tabla de eventos de
[01 · 06 §4](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md#4-el-orden-exacto-de-cada-step),
la fase `ALARMS` del motor decrementa cada alarma activa **antes** de que corra tu evento Step,
y lo hace sí o sí con tal de que el evento Alarm tenga algo dentro (aunque sea un comentario,
según ese mismo documento). Un `if (time_delta() == 0) exit;` al principio de Step no llega a
tiempo: la alarma ya ha bajado, y si llega a 0 ya ha disparado su código.

La única forma de neutralizarla sin desactivar la instancia es **contrarrestar el
decremento automático**, y hay que hacerlo en **Begin Step** — la única fase garantizada que
corre ANTES que `ALARMS`:

```gml
/// obj_jugador (o cualquier objeto con alarmas que deba respetar el time scale)
/// Begin Step
if (time_is_frozen()) {          // de scr_time, 04/15 §5.0
    for (var _i = 0; _i < 12; _i++) {
        if (alarm[_i] > -1) alarm[_i] += 1;   // cancela el -1 que le va a aplicar ALARMS
    }
}
```

> 💡 En la práctica, mezclar los dos patrones suele ser la solución más simple: usar
> `instance_deactivate_all` para todo lo que tenga alarmas, y reservar el time scale 0 para
> unas pocas instancias «con permiso para seguir vivas» durante la pausa (partículas de
> ambiente, un cursor animado del propio menú) que normalmente no usan Alarm en absoluto.

#### 3.1.6 Partículas: parar la actualización automática

`part_system_create()` deja el sistema en `automatic_update = true` por defecto: se actualiza
solo cada step, sin que ninguna instancia tenga que llamarlo. Pararlo y arrancarlo es simétrico:

```gml
/// @func particulas_pausar()
function particulas_pausar() {
    for (var _i = 0; _i < array_length(global.registro_particulas); _i++) {
        var _ps = global.registro_particulas[_i];
        if (part_system_exists(_ps)) part_system_automatic_update(_ps, false);
    }
}

/// @func particulas_reanudar()
function particulas_reanudar() {
    for (var _i = 0; _i < array_length(global.registro_particulas); _i++) {
        var _ps = global.registro_particulas[_i];
        if (part_system_exists(_ps)) part_system_automatic_update(_ps, true);
    }
}
```

> ⚠️ Esto congela el sistema (deja de emitir y de mover partículas existentes), pero **no las
> oculta**. Si además usas `automatic_draw = false` en algún sistema, acuérdate de que dibujarlo
> tú a mano seguirá pintando el último estado — que es exactamente lo que quieres en una pausa
> (una explosión a medias se queda a medias, no desaparece).

#### 3.1.7 Sequences: `layer_sequence_pause` / `layer_sequence_play`

El par correcto **no** es `pause`/`resume` — esa función no existe para Sequences (se ha
comprobado; sí existe para audio y para Time Sources, pero aquí el verbo es distinto). Es
`layer_sequence_pause()` para pausar y **`layer_sequence_play()`** para reanudar, tal y como ya
lo documenta
[13/04](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md):

```gml
/// @func secuencias_pausar()
function secuencias_pausar() {
    for (var _i = 0; _i < array_length(global.registro_secuencias); _i++) {
        var _r = global.registro_secuencias[_i];
        if (layer_sequence_exists(_r.capa, _r.elemento)) layer_sequence_pause(_r.elemento);
    }
}

/// @func secuencias_reanudar()
function secuencias_reanudar() {
    for (var _i = 0; _i < array_length(global.registro_secuencias); _i++) {
        var _r = global.registro_secuencias[_i];
        if (layer_sequence_exists(_r.capa, _r.elemento)) layer_sequence_play(_r.elemento);
    }
}
```

#### 3.1.8 La función completa: `pausar_de_verdad()` / `reanudar_de_verdad()`

Ahora sí, la versión que usan tanto el menú de pausa (§3.4) como el motor de transiciones
(§3.2) — una ampliación directa del `pausar()`/`reanudar()` de
[00 · Anatomía §5](./00%20-%20Anatomía%20de%20un%20juego%20completo.md#5--el-bucle-de-juego-zonas-hud-pausa-guardado),
que ya resolvía las instancias y el audio y aquí se completa con lo que le faltaba:

```gml
/// @func pausar_de_verdad()
/// @desc Congelado real: instancias, física, Time Sources, partículas, Sequences y audio.
function pausar_de_verdad() {
    if (global.pausado) return;
    global.pausado = true;

    // 1) Capturamos el último frame ANTES de apagar el dibujado: si no, el fondo
    //    desaparece en cuanto instance_deactivate_all haga efecto (§3.1.1).
    global.surf_fondo_pausa = surface_create(surface_get_width(application_surface),
                                              surface_get_height(application_surface));
    surface_copy(global.surf_fondo_pausa, 0, 0, application_surface);

    // 2) Instancias: Step, Alarm, Collision, Draw y animación de sprite, todo de golpe.
    instance_deactivate_all(true);

    // 3) Lo que instance_deactivate_all NO toca (§3.1.2):
    physics_pause_enable(true);
    time_source_pause(global.ts_raiz_pausable);
    particulas_pausar();
    secuencias_pausar();

    // 4) Audio.
    audio_pause_all();
}

/// @func reanudar_de_verdad()
function reanudar_de_verdad() {
    if (!global.pausado) return;
    global.pausado = false;

    if (surface_exists(global.surf_fondo_pausa)) surface_free(global.surf_fondo_pausa);

    instance_activate_all();
    physics_pause_enable(false);
    time_source_resume(global.ts_raiz_pausable);
    particulas_reanudar();
    secuencias_reanudar();
    audio_resume_all();
}
```

#### 3.1.9 Tabla de decisión: time scale 0 frente a `instance_deactivate_all`

Las dos formas de «pausar» que usa esta biblioteca no son intercambiables: resuelven problemas
distintos.

| | `global.time_scale = 0` ([04/15 §5.0](./15%20-%20Game%20feel%20y%20juice.md#50-sistema-de-tiempo-hit-stop-y-time-scale)) | `instance_deactivate_all(true)` ([00 §5](./00%20-%20Anatomía%20de%20un%20juego%20completo.md#5--el-bucle-de-juego-zonas-hud-pausa-guardado) + §3.1.8) |
|---|---|---|
| Movimiento en tu propio código (`x += vel_x * time_delta()`) | Se para, **si todo tu código lo consulta** — un solo sistema que se olvide sigue moviéndose | Se para solo: Step no corre |
| Alarmas | Siguen contando y disparándose salvo el contraataque de §3.1.5 | Se paran solas |
| Animación de sprite (`image_index`) | Sigue avanzando sola salvo que pongas `image_speed = 0` a mano | Se para sola |
| Colisiones | Se siguen comprobando | Se paran |
| Dibujado / visibilidad | El mundo se sigue viendo y animando — es la gracia de este método | Deja de dibujarse: necesitas la instantánea de §3.1.8 |
| Time Sources, partículas, Sequences, física | Siguen su curso salvo que las pauses tú (§3.1.3-3.1.7) | **Igual**: tampoco las toca (§3.1.2) |
| Reversibilidad | Instantánea, sin coste: es una variable | Con coste de una llamada (barata) por sistema |
| Úsalo para… | Pausas breves y «vivas»: un tiempo bala, un cuadro de diálogo rápido, un inventario que no detiene el mundo | Pausa real: el jugador se va al menú de opciones y puede tardar minutos |

La fila que sorprende a casi todo el mundo es la penúltima: **ninguno de los dos métodos**
resuelve Time Sources, partículas, Sequences o física por sí solo. Son sistemas ortogonales al
mecanismo de pausa que elijas, y siempre hay que pausarlos aparte — el §3.1 entero existe por
esa fila.

---

### 3.2 El motor de transiciones

Generaliza el fundido único de
[01 · 10 §9](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md#9-transiciones-entre-rooms)
a los cinco tipos de §2.1, manteniendo la misma máquina de tres estados y apoyándose en el
congelado de §3.1.8: el mundo no debe cambiar mientras dura el efecto.

#### 3.2.1 Los enums y el estado compartido

```gml
enum TransicionTipo   { Fundido, Wipe, Cortinas, Iris, Disolucion }
enum TransicionEstado { Idle, Saliendo, Entrando }
enum WipeDireccion    { Izquierda, Derecha, Arriba, Abajo }
```

```gml
/// obj_transicion (persistente, ÚNICO — crear en rm_init) · Create
if (instance_number(obj_transicion) > 1) { instance_destroy(); exit; }

estado           = TransicionEstado.Idle;
tipo             = TransicionTipo.Fundido;
direccion_wipe   = WipeDireccion.Izquierda;
progreso_cubrir  = 0;      // 0 = pantalla despejada · 1 = pantalla totalmente cubierta
duracion_fase    = 0.4;    // segundos por fase (salida Y entrada duran lo mismo)
room_destino     = noone;
callback_llegada = undefined;

// shader de disolución, ver §3.2.6 — se prepara aquí para no repetir shader_get_uniform cada frame
u_progreso_dis    = shader_get_uniform(sh_disolver, "u_progreso");
u_color_borde_dis = shader_get_uniform(sh_disolver, "u_color_borde");
u_ancho_borde_dis = shader_get_uniform(sh_disolver, "u_ancho_borde");
s_ruido_dis       = shader_get_sampler_index(sh_disolver, "s_ruido");

// shader de iris, ver §3.2.5
u_centro_iris     = shader_get_uniform(sh_iris, "u_centro");
u_radio_iris      = shader_get_uniform(sh_iris, "u_radio");
u_aspecto_iris    = shader_get_uniform(sh_iris, "u_aspecto");
u_borde_iris      = shader_get_uniform(sh_iris, "u_ancho_borde");
```

```gml
/// @func ir_a_escena(_room, _tipo, _callback)
/// @desc Punto de entrada único para cambiar de sala con transición.
///       Devuelve false si ya hay una transición en curso (evita el doble room_goto
///       de pulsar "Jugar" dos veces antes de que cargue la primera).
function ir_a_escena(_room, _tipo = TransicionTipo.Fundido, _callback = undefined) {
    if (estado != TransicionEstado.Idle) return false;

    tipo             = _tipo;
    room_destino     = _room;
    callback_llegada = _callback;
    progreso_cubrir  = 0;
    estado           = TransicionEstado.Saliendo;
    pausar_de_verdad();     // el mundo no debe cambiar mientras el efecto está en pantalla
    return true;
}
```

```gml
/// obj_transicion · Step
if (estado == TransicionEstado.Idle) exit;

var _velocidad = 1 / (duracion_fase * game_get_speed(gamespeed_fps));

switch (estado) {
    case TransicionEstado.Saliendo:
        progreso_cubrir = min(progreso_cubrir + _velocidad, 1);
        if (progreso_cubrir >= 1) {
            room_goto(room_destino);
            estado = TransicionEstado.Entrando;
            if (is_callable(callback_llegada)) callback_llegada();
        }
        break;

    case TransicionEstado.Entrando:
        progreso_cubrir = max(progreso_cubrir - _velocidad, 0);
        if (progreso_cubrir <= 0) {
            estado = TransicionEstado.Idle;
            reanudar_de_verdad();
        }
        break;
}
```

> 🔺 **`obj_transicion` debe seguir corriendo Step aunque el resto del mundo esté congelado.**
> Es la instancia que llama a `pausar_de_verdad()`, así que `instance_deactivate_all(true)` la
> deja activa a propósito (el `true` es justo eso, ver §3.1.1). Si además tienes tu propio
> `obj_pausa`, ambos deben quedar fuera de la desactivación.

> 💡 Si prefieres desacoplar «ya hemos llegado a la sala nueva» de quien pidió la transición
> (por ejemplo, para que el HUD se entere sin que `ir_a_escena` conozca al HUD), emite una señal
> en vez de usar `callback_llegada` — ver
> [04 · 16 — Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md).

#### 3.2.2 Dibujado: despachar por tipo

```gml
/// obj_transicion · Draw GUI (depth muy negativo: por encima de todo, incluido el HUD)
if (estado == TransicionEstado.Idle) exit;

var _gw = display_get_gui_width();
var _gh = display_get_gui_height();

switch (tipo) {
    case TransicionTipo.Fundido:    dibujar_transicion_fundido(_gw, _gh);   break;
    case TransicionTipo.Wipe:       dibujar_transicion_wipe(_gw, _gh);      break;
    case TransicionTipo.Cortinas:   dibujar_transicion_cortinas(_gw, _gh);  break;
    case TransicionTipo.Iris:       dibujar_transicion_iris(_gw, _gh);      break;
    case TransicionTipo.Disolucion: dibujar_transicion_disolucion(_gw, _gh); break;
}
```

#### 3.2.3 Fundido

```gml
/// @func dibujar_transicion_fundido(_gw, _gh)
function dibujar_transicion_fundido(_gw, _gh) {
    draw_set_alpha(progreso_cubrir);
    draw_set_colour(c_black);
    draw_rectangle(0, 0, _gw, _gh, false);
    draw_set_alpha(1);
    draw_set_colour(c_white);
}
```

#### 3.2.4 Wipe

```gml
/// @func dibujar_transicion_wipe(_gw, _gh)
function dibujar_transicion_wipe(_gw, _gh) {
    draw_set_colour(c_black);
    switch (direccion_wipe) {
        case WipeDireccion.Izquierda:
            draw_rectangle(0, 0, _gw * progreso_cubrir, _gh, false);
            break;
        case WipeDireccion.Derecha:
            draw_rectangle(_gw * (1 - progreso_cubrir), 0, _gw, _gh, false);
            break;
        case WipeDireccion.Arriba:
            draw_rectangle(0, 0, _gw, _gh * progreso_cubrir, false);
            break;
        case WipeDireccion.Abajo:
            draw_rectangle(0, _gh * (1 - progreso_cubrir), _gw, _gh, false);
            break;
    }
    draw_set_colour(c_white);
}
```

#### 3.2.5 Cortinas

```gml
/// @func dibujar_transicion_cortinas(_gw, _gh)
function dibujar_transicion_cortinas(_gw, _gh) {
    var _alto = (_gh / 2) * progreso_cubrir;
    draw_set_colour(c_black);
    draw_rectangle(0, 0, _gw, _alto, false);              // cortina superior
    draw_rectangle(0, _gh - _alto, _gw, _gh, false);       // cortina inferior
    draw_set_colour(c_white);
}
```

#### 3.2.6 Iris

Un iris circular necesita saber la distancia de cada píxel al centro, corregida por la
proporción de pantalla (si no, el círculo sale ovalado). No hay ninguna función de dibujo que
haga esto directamente: es un shader de dos líneas, escrito con el mismo patrón —y las mismas
funciones verificadas— que el resto de [08 · 06](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md).

**Vertex shader** (`sh_iris.vsh`) — idéntico al de `sh_disolver` (08/06 §6.3): cópialo tal cual.

**Fragment shader** (`sh_iris.fsh`):
```glsl
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform vec2  u_centro;       // centro del iris, en coordenadas de textura 0-1
uniform float u_radio;        // radio actual, en fracción de la ALTURA de pantalla
uniform float u_aspecto;      // ancho / alto, para que el círculo no salga ovalado
uniform float u_ancho_borde;  // suavizado del borde

void main()
{
    vec2 delta = v_vTexcoord - u_centro;
    delta.x *= u_aspecto;                 // corrige la distorsión horizontal
    float distancia = length(delta);

    // Dentro del radio: transparente (se ve el juego). Fuera: el color puesto por draw_set_colour.
    float mascara = smoothstep(u_radio, u_radio + u_ancho_borde, distancia);
    if (mascara <= 0.0) discard;

    gl_FragColor = vec4(v_vColour.rgb, v_vColour.a * mascara);
}
```

```gml
/// @func dibujar_transicion_iris(_gw, _gh)
function dibujar_transicion_iris(_gw, _gh) {
    var _aspecto      = _gw / _gh;
    var _radio_maximo = point_distance(0, 0, 0.5 * _aspecto, 0.5);  // del centro a la esquina
    var _radio        = _radio_maximo * (1 - progreso_cubrir);

    shader_set(sh_iris);
    shader_set_uniform_f(u_centro_iris, 0.5, 0.5);
    shader_set_uniform_f(u_radio_iris, _radio);
    shader_set_uniform_f(u_aspecto_iris, _aspecto);
    shader_set_uniform_f(u_borde_iris, 0.02);
    draw_set_colour(c_black);
    draw_rectangle(0, 0, _gw, _gh, false);
    draw_set_colour(c_white);
    shader_reset();
}
```

#### 3.2.7 Disolución con ruido — reutilizando el shader de 08/06 §6.3 sin tocar una línea

El shader `sh_disolver` de
[08 · 06 §6.3](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md#63-disolución-dissolve)
está pensado para desintegrar un sprite: compara una textura de ruido contra `u_progreso` y
descarta ("`discard`") los píxeles donde el ruido es menor. El shader **no sabe qué está
dibujando** — le da igual si lo que recibe es un sprite o un rectángulo liso —, así que
reutilizarlo para una transición de pantalla completa es simplemente dibujar un rectángulo
negro a pantalla completa **con ese shader puesto**, en vez de un `draw_self()`:

```gml
/// @func dibujar_transicion_disolucion(_gw, _gh)
function dibujar_transicion_disolucion(_gw, _gh) {
    shader_set(sh_disolver);
    texture_set_stage(s_ruido_dis, sprite_get_texture(spr_ruido_transicion, 0));

    // El shader original hace que lo dibujado DESAPAREZCA según SUBE u_progreso
    // (progreso 0 = intacto, 1 = disuelto). Aquí queremos lo contrario: que el
    // rectángulo negro APAREZCA según sube progreso_cubrir. Por eso el complementario.
    shader_set_uniform_f(u_progreso_dis, 1 - progreso_cubrir);
    shader_set_uniform_f(u_color_borde_dis, 1, 0.7, 0.3);   // reborde cálido, opcional
    shader_set_uniform_f(u_ancho_borde_dis, 0.08);

    draw_set_colour(c_black);
    draw_rectangle(0, 0, _gw, _gh, false);
    draw_set_colour(c_white);
    shader_reset();
}
```

`spr_ruido_transicion` es la misma clase de textura de ruido en escala de grises que pide
`sh_disolver` en 08/06 (`spr_ruido_disolver`): si tu proyecto ya la tiene, reutilízala tal cual.

> ⚠️ El código GML de este apartado (`shader_set`, `shader_get_uniform`,
> `shader_set_uniform_f`, `texture_set_stage`, `sprite_get_texture`, `draw_rectangle`) está
> verificado contra `simbolos.json`. El GLSL de `sh_iris.fsh` es original para este documento
> (no procede de 08/06, que solo aporta el patrón y el shader de disolución); usa únicamente
> funciones estándar de GLSL ES (`length`, `smoothstep`) ya empleadas sin marcar en el propio
> `sh_disolver`.

---

### 3.3 La pantalla de carga real

#### 3.3.1 Qué mide y qué no

`texturegroup_get_status()` no da un porcentaje: da un estado de 4 pasos por grupo
(§08/08). Con varios grupos pedidos a la vez, el progreso real es **el promedio del estado de
cada grupo**, normalizado a 0-1. Es más basto que un porcentaje de bytes, pero es **cierto** —
y es preferible a fingir continuidad que el motor no ofrece.

#### 3.3.2 El objeto completo

```gml
/// obj_pantalla_carga · Create
/// (se crea al llegar a una room "puente" dedicada a cargar, o justo antes de room_goto)
grupos_a_cargar  = ["tg_Nivel2", "tg_MusicaNivel2"];   // los que pide la room destino
room_destino     = rm_nivel2;
tiempo_inicio    = get_timer();          // microsegundos: independiente del framerate
duracion_minima  = 1_200_000;            // 1.2 s — que no parpadee en discos rápidos
intervalo_consejo = 4_000_000;           // cambia de consejo cada 4 s
progreso_real    = 0;

for (var _i = 0; _i < array_length(grupos_a_cargar); _i++) {
    texturegroup_load(grupos_a_cargar[_i], true);   // true = enviar a VRAM cuando esté lista
}
```

```gml
/// obj_pantalla_carga · Step
var _acumulado = 0;
for (var _i = 0; _i < array_length(grupos_a_cargar); _i++) {
    var _estado = texturegroup_get_status(grupos_a_cargar[_i]);
    _acumulado += _estado / texturegroup_status_fetched;   // 0 · 0.33 · 0.66 · 1 por grupo
}
progreso_real = _acumulado / array_length(grupos_a_cargar);

var _tiempo_pasado = get_timer() - tiempo_inicio;
if (progreso_real >= 1 && _tiempo_pasado >= duracion_minima) {
    room_goto(room_destino);
}
```

> 🔺 **La condición de salida exige LAS DOS cosas: carga terminada Y tiempo mínimo cumplido.**
> Nunca al revés — no adelantes `room_goto` solo porque ha pasado el tiempo mínimo si la carga
> real todavía no ha terminado (dejarías el asset a medio enviar a VRAM en la sala nueva).

```gml
/// obj_pantalla_carga · Draw GUI
var _gw = display_get_gui_width();
var _gh = display_get_gui_height();

draw_set_colour(c_black);
draw_rectangle(0, 0, _gw, _gh, false);

var _bw = _gw * 0.5;
var _bh = 24;
var _bx = (_gw - _bw) / 2;
var _by = _gh * 0.75;

draw_set_colour(c_gray);
draw_rectangle(_bx, _by, _bx + _bw, _by + _bh, false);
draw_set_colour(c_white);
draw_rectangle(_bx, _by, _bx + _bw * progreso_real, _by + _bh, false);

draw_set_halign(fa_center);
draw_set_valign(fa_middle);
draw_text(_gw / 2, _by - 24, string(floor(progreso_real * 100)) + "%");

// consejo rotativo — cambia solo, sin variable de estado propia: se deriva del reloj
var _indice_consejo = floor((get_timer() - tiempo_inicio) / intervalo_consejo)
                       mod array_length(global.consejos_carga);
draw_text(_gw / 2, _by + _bh + 40, global.consejos_carga[_indice_consejo]);

draw_set_halign(fa_left);
draw_set_valign(fa_top);
```

```gml
// global.consejos_carga, definido una vez al arrancar (junto a la localización, §1 de 00 · Anatomía)
global.consejos_carga = [
    txt("consejo_carga_1"),
    txt("consejo_carga_2"),
    txt("consejo_carga_3"),
];
```

#### 3.3.3 Errores que esta receta evita a propósito

- **No usa un temporizador como fuente de verdad.** `progreso_real` sale siempre de
  `texturegroup_get_status()`; `duracion_minima` solo retrasa el `room_goto`, nunca infla la
  barra.
- **No cambia de sala antes de que la VRAM esté lista** (`texturegroup_status_fetched`, no
  `_loaded`): pedir `true` en `texturegroup_load()` ya apunta a ese estado final.
- **Es reentrante**: si por lo que sea `grupos_a_cargar` incluye un grupo que ya estaba
  cargado de antes, su estado ya será `fetched` desde el primer step y no bloquea a los demás.

---

### 3.4 El menú de pausa completo

#### 3.4.1 Estructura

Tres opciones, en el orden que ya fija
[13/05 §2.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#21-el-mapa-de-pantallas-se-dibuja-antes-de-programar-nada):
**Reanudar · Opciones · Salir**. La navegación entre ellas (foco, envolvente, repetición de
tecla mantenida) no se repite aquí: usa
[13/05 §2.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#22-navegación-con-mando-y-teclado-foco-orden-envolvente-y-repetición)
o el patrón de lista de
[04 · 18](./18%20-%20Menús%20con%20scroll%20y%20navegación.md), y el botón de cuatro estados de
[13/05 §3.5a](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#a-botón-con-sus-cuatro-estados)
para el aspecto visual. Lo que sigue es lo que le falta a esa base para ser un menú de pausa de
verdad: el freeze, el fondo, el audio y la confirmación.

```gml
enum PausaEstado { Cerrado, Menu, Confirmando }
```

```gml
/// obj_pausa (persistente, ÚNICO) · Create
if (instance_number(obj_pausa) > 1) { instance_destroy(); exit; }

estado          = PausaEstado.Cerrado;
foco            = 0;
foco_guardado   = 0;         // ley 5 de 13/05 §2.2: el foco vuelve donde estaba
opciones_pausa  = [txt("pausa_reanudar"), txt("pausa_opciones"), txt("pausa_salir")];
```

#### 3.4.2 Abrir y cerrar: congelar de verdad, no solo mostrar un panel

```gml
/// obj_pausa · Step
if (estado == PausaEstado.Cerrado) {
    var _abrir = keyboard_check_pressed(vk_escape)
              || (gamepad_is_connected(0) && gamepad_button_check_pressed(0, gp_start));
    if (_abrir) {
        estado = PausaEstado.Menu;
        foco   = 0;
        pausar_de_verdad();                        // §3.1.8: instancias, física, TS, partículas,
                                                     // Sequences, audio — todo de un tirón
        audio_sound_gain(mus_actual, 0.25, 500);    // ducking: baja la música en 500 ms
    }
    exit;
}

if (estado == PausaEstado.Menu) {
    // navegación con la técnica de 13/05 §2.2 / 04/18 — omitida aquí, ya está resuelta
    if (input_confirmar_pulsado()) {
        switch (foco) {
            case 0: cerrar_pausa();               break;   // Reanudar
            case 1: abrir_opciones_desde_pausa();  break;   // Opciones
            case 2: estado = PausaEstado.Confirmando; break; // Salir → confirmar primero
        }
    }
}
```

```gml
/// @func cerrar_pausa()
function cerrar_pausa() {
    audio_sound_gain(mus_actual, 1.0, 500);   // deshace el ducking
    reanudar_de_verdad();
    estado = PausaEstado.Cerrado;
}
```

> 💡 **Ducking simple** con `audio_sound_gain(index, volumen, tiempo)` basta para «esto sigue
> sonando, pero más flojo». Si quieres un efecto más caracterizado (la música «amortiguada»
> detrás del menú, no solo más baja), aplica un filtro de paso bajo al bus principal — ya está
> resuelto en
> [02 · Novedades 2026 — Audio §5.9](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md#59-ejemplo-transición-a-menú-de-pausa),
> con el propio ejemplo titulado «transición a menú de pausa».

#### 3.4.3 Dibujar el fondo congelado, oscurecido de verdad

```gml
/// obj_pausa · Draw GUI
if (estado == PausaEstado.Cerrado) exit;

var _gw = display_get_gui_width();
var _gh = display_get_gui_height();

// El mundo "congelado" que se ve detrás es la instantánea de pausar_de_verdad() (§3.1.8),
// no el mundo en vivo: instance_deactivate_all ya apagó su dibujado.
if (surface_exists(global.surf_fondo_pausa)) {
    draw_surface_stretched(global.surf_fondo_pausa, 0, 0, _gw, _gh);
}

draw_set_alpha(0.6);
draw_set_colour(c_black);
draw_rectangle(0, 0, _gw, _gh, false);
draw_set_alpha(1);
draw_set_colour(c_white);

// ... dibujar aquí el panel y los tres botones con el widget de 13/05 §3.5a ...

if (estado == PausaEstado.Confirmando) dibujar_confirmacion_salir(_gw, _gh);
```

#### 3.4.4 «¿Seguro que quieres salir?» — con «No» por defecto, sin `show_question()`

La regla ya está fijada en
[13/05 §2.1, punto 3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#21-el-mapa-de-pantallas-se-dibuja-antes-de-programar-nada):
toda acción destructiva confirma, y el botón por defecto es «No». Lo que falta es el mecanismo,
porque la tentación de usar `show_question()` es real y **está descartada**:
[01 · 15](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md) advierte que
`show_question()` **bloquea el juego en un bucle cerrado y se ignora al compilar para
cualquier plataforma que no sea Windows** (salvo en modo debug). Un diálogo de confirmación de
verdad es, como todo lo demás en este documento, un estado más:

```gml
/// obj_pausa · Confirmando — Step (llamado desde el switch de §3.4.2)
foco_confirmacion = foco_confirmacion ?? 0;    // 0 = "No", 1 = "Sí" — "No" empieza con el foco

if (input_izquierda_pulsada() || input_derecha_pulsada()) {
    foco_confirmacion = 1 - foco_confirmacion;
}
if (input_confirmar_pulsado()) {
    if (foco_confirmacion == 1) {
        reanudar_de_verdad();                  // no dejes el mundo congelado al salir
        ir_a_escena(rm_menu_principal);
    } else {
        estado = PausaEstado.Menu;              // vuelve al menú de pausa, no al juego
    }
    foco_confirmacion = 0;                      // se resetea a "No" para la próxima vez
}
if (input_cancelar_pulsado()) {                 // Esc/B también cancela, no solo "No"
    estado = PausaEstado.Menu;
    foco_confirmacion = 0;
}
```

```gml
/// @func dibujar_confirmacion_salir(_gw, _gh)
function dibujar_confirmacion_salir(_gw, _gh) {
    var _pw = 420, _ph = 160;
    var _px = (_gw - _pw) / 2, _py = (_gh - _ph) / 2;

    draw_set_colour(c_black);
    draw_rectangle(_px, _py, _px + _pw, _py + _ph, false);

    draw_set_halign(fa_center);
    draw_text(_gw / 2, _py + 32, txt("pausa_confirmar_salir"));

    draw_text_color(_gw / 2 - 80, _py + _ph - 40, txt("comun_no"),
                     foco_confirmacion == 0 ? c_white : c_gray,
                     foco_confirmacion == 0 ? c_white : c_gray,
                     foco_confirmacion == 0 ? c_white : c_gray,
                     foco_confirmacion == 0 ? c_white : c_gray, 1);
    draw_text_color(_gw / 2 + 80, _py + _ph - 40, txt("comun_si"),
                     foco_confirmacion == 1 ? c_white : c_gray,
                     foco_confirmacion == 1 ? c_white : c_gray,
                     foco_confirmacion == 1 ? c_white : c_gray,
                     foco_confirmacion == 1 ? c_white : c_gray, 1);
    draw_set_halign(fa_left);
}
```

> 🔺 Este es el diálogo mínimo de esta receta, escrito solo para «salir». **Actualización:** el
> patrón ya está generalizado en
> [`scr_ui_confirmar.gml`](../06%20-%20Assets%20y%20Scripts/scr_ui_confirmar.gml) — un widget de
> confirmación reutilizable para CUALQUIER acción destructiva (salir, sobrescribir una ranura de
> guardado, borrar partida, restablecer controles…), documentado como componente m) en
> [13/05 §3.5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#m-confirmación-síno-con-no-por-defecto).
> El componente «Diálogo» de
> [13/05 §3.5f](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#f-diálogo-la-caja-no-el-texto)
> sigue siendo para texto narrativo, no para confirmar/cancelar — son componentes distintos.

#### 3.4.5 El foco que vuelve donde estaba

Al entrar en Opciones desde la pausa (la misma pantalla que desde el menú principal, regla 1 de
13/05 §2.1) y volver, el foco debe reaparecer en «Opciones», no saltar a «Reanudar» — es la
**ley 5** de
[13/05 §2.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#22-navegación-con-mando-y-teclado-foco-orden-envolvente-y-repetición):
«al volver de una subpantalla, el foco vuelve donde estaba».

```gml
/// @func abrir_opciones_desde_pausa()
function abrir_opciones_desde_pausa() {
    global.opciones_origen = "pausa";   // la pantalla de Opciones ya lee esta variable
    foco_guardado          = foco;      // se guarda el índice, no la pantalla entera
    room_goto(rm_opciones);
}
```

```gml
/// obj_pausa · Create de rm_opciones (o donde corresponda al volver) — solo el fragmento relevante
if (global.opciones_origen == "pausa") {
    room_goto(rm_ultima_sala_de_juego);
    with (obj_pausa) {
        estado = PausaEstado.Menu;
        foco   = foco_guardado;        // el foco vuelve donde estaba, no a 0
    }
}
```

#### 3.4.6 Cuándo NO se puede (o no se debe) pausar

- **Mientras una transición ya está en curso.** `ir_a_escena()` ya se protege a sí misma
  (§3.2.1: `if (estado != Idle) return false;`), pero el propio `obj_pausa` debería ignorar la
  tecla de pausa si `obj_transicion.estado != TransicionEstado.Idle` — pausar a mitad de un
  fundido dejaría el mundo en un estado a medio congelar dos veces.
- **En multijugador en tiempo real.** Congelar solo tu cliente con `pausar_de_verdad()` no
  para a los demás jugadores: te desincronizas. ⚠️ Esta biblioteca no cubre pausa en red — la
  salida honesta es que «pausa» abra solo un menú local que no toque el estado compartido, o
  que el género lo prohíba explícitamente mientras haya otros jugadores conectados (ver
  [04 · 14 — Multijugador](./14%20-%20Multijugador.md) para la arquitectura general).
- **Durante el propio Game Over o la pantalla de resultados**, si ya tienen su propia máquina
  de estados: decide una jerarquía clara (normalmente, Game Over gana y la pausa se desactiva
  hasta volver al menú).
- **Cuando el sistema operativo ya te ha pausado.** En móvil, `os_is_paused()` **ya** dispara
  su propia rutina de guardado + `audio_pause_all()` en
  [04 · 28 §…](<./28 - Juegos para móvil (táctil).md>) — no dupliques esa lógica
  llamando también a `pausar_de_verdad()` ahí: el sistema operativo va a congelar el proceso
  entero un instante después de todas formas.

---

## 4 · Checklist

> Esta lista es el detalle de transiciones/carga/pausa. El índice maestro de «juego completo»
> —el que compara TODO el envoltorio, no solo esta pieza— es
> [04 · 00](./00%20-%20Anatomía%20de%20un%20juego%20completo.md#el-checklist-de-juego-completo).

**Transiciones**
- [ ] Hay un tipo por defecto (normalmente Fundido) y los demás se usan con intención, no al azar
- [ ] `ir_a_escena()` se protege contra una segunda llamada mientras ya hay una en curso
- [ ] La transición congela el mundo mientras dura (llama a `pausar_de_verdad()`)
- [ ] Ningún efecto destella más de 3 veces por segundo (ver 04/27)
- [ ] El fundido/wipe/iris se dibuja en Draw GUI, para tapar también el HUD

**Pantalla de carga**
- [ ] El progreso de la barra sale de `texturegroup_get_status()`, nunca de un temporizador a solas
- [ ] Hay una duración mínima que evita el parpadeo, independiente del progreso real
- [ ] El cambio de sala exige progreso real completo Y tiempo mínimo cumplido, las dos cosas
- [ ] Hay algo que leer mientras se espera (consejo, lore, nada de pantalla en blanco)

**Pausa**
- [ ] `pausar_de_verdad()` cubre instancias, física, Time Sources, partículas, Sequences y audio
- [ ] El fondo detrás del menú es una instantánea capturada ANTES de desactivar instancias
- [ ] «Salir» confirma con «No» por defecto, sin usar `show_question()`
- [ ] El foco vuelve donde estaba al salir de Opciones (ley 5 de 13/05 §2.2)
- [ ] Está decidido dónde NO se puede pausar (transición en curso, multijugador, Game Over)
- [ ] **Ninguna acción del menú de pausa empieza con una guarda `instance_exists`** — durante la pausa devuelve `false` sobre todo lo desactivado y la acción se convierte en un no-op silencioso (§3.1.1)
- [ ] Todas las Time Sources de gameplay cuelgan de `global.ts_raiz_pausable`, no de `time_source_game` directamente

---

## 5 · Errores clásicos y cómo evitarlos

1. **Pensar que `instance_deactivate_all` ya lo pausa todo.** Para instancias sí; deja
   corriendo Time Sources, partículas, Sequences y física (§3.1.2). Es el error más caro de
   este documento porque no se nota hasta que hay un sistema de partículas o un cuerpo físico
   en juego, y para entonces suele estar ya en producción.
2. **Congelar el mundo con `instance_deactivate_all` y sorprenderse de que desaparece detrás
   del menú de pausa.** No es un bug: las instancias desactivadas no se dibujan. Captura el
   frame ANTES de desactivar (§3.1.8).
3. **Poner una alarma a 0 esperando que corra ese mismo step.** No corre: se pone a -1
   inmediatamente y el código se salta (ya lo advierte
   [01 · 06 §6](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md#alarm)).
   Si quieres que se dispare en el siguiente step, ponla a 1.
4. **Usar `show_question()` para confirmar "Salir".** Bloquea el juego y se ignora fuera de
   Windows salvo en debug (§3.4.4). Sustitúyelo siempre por un estado más de tu propia máquina.
5. **Confirmar destructivo con "Sí" como opción por defecto.** Un clic de pánico (o una
   repetición de tecla mal calculada) borra progreso. "No" siempre empieza con el foco.
6. **Olvidar `physics_pause_enable(true)` en un juego con Box2D.** Los cuerpos siguen
   simulándose bajo el menú de pausa aunque sus instancias estén desactivadas — lo confirma el
   propio manual de `physics_pause_enable` (§3.1.2).
7. **Colgar cada Time Source directamente de `time_source_game`.** Funciona hasta que hay diez
   de ellas y hay que pausarlas todas a mano. Cuélgalas de `global.ts_raiz_pausable` desde el
   primer día (§3.1.4): pausar una jerarquía es gratis, deshacer la decisión más tarde no.
8. **Una barra de carga que sube con un temporizador en vez de con el estado real.** Se ve
   bien en el ordenador de quien lo programa (SSD rápido) y miente en el disco duro mecánico
   de otra persona, donde llega al 100 % y el juego se queda congelado igual (§1.2).
9. **No tener duración mínima en la carga.** En hardware rápido la pantalla dura dos frames:
   parece un parpadeo, no una carga — y en un juego con modo de accesibilidad para
   fotosensibilidad, ese parpadeo es justo lo que hay que evitar (04/27).

---

## Ver también

- [00 · Anatomía de un juego completo §2 y §5](./00%20-%20Anatomía%20de%20un%20juego%20completo.md) — el fundido simple y el `pausar()` básico que este documento extiende
- [01 · 06 — Eventos y ciclo del juego §4 y §8](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) — el orden exacto del step (de dónde sale la posición de Alarmas y Time Sources) y la base de Time Sources
- [01 · 10 — Rooms, capas, cámaras y viewports §9](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md) — la versión mínima de transición que aquí se generaliza
- [01 · 11 — Dibujo y renderizado](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) — `application_surface`, de dónde sale la instantánea del fondo de pausa
- [01 · 12 — Input](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md) — pérdida de foco de ventana como disparador de pausa
- [01 · 15 — Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md) — por qué `show_question()` está descartado
- [04 · 14 — Multijugador](./14%20-%20Multijugador.md) — por qué la pausa no se puede tratar igual en red
- [04 · 15 — Game feel y juice §5.0](./15%20-%20Game%20feel%20y%20juice.md) — `time_scale`, `hit_stop` y el otro patrón de pausa
- [04 · 16 — Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — alternativa al callback de `ir_a_escena()`
- [04 · 18 — Menús con scroll y navegación](./18%20-%20Menús%20con%20scroll%20y%20navegación.md) — navegación completa de una lista de opciones
- [04 · 25 — Menú de opciones y ajustes](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md) — la pantalla de Opciones que reutiliza tanto el menú principal como la pausa
- [04 · 27 — Accesibilidad](./27%20-%20Accesibilidad.md) — el límite de destellos por segundo
- [04 · 28 — Juegos para móvil (táctil)](<./28 - Juegos para móvil (táctil).md>) — `os_is_paused()` y el ciclo de vida en segundo plano
- [08 · 06 — Shaders §6.3](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md) — el shader de disolución que se reutiliza en §3.2.7
- [08 · 08 — Texturas y grupos de texturas](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md) — la API completa de `texturegroup_*`
- [02 · Novedades 2026 — Audio, buses y efectos §5.9](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md) — el filtro de paso bajo para el menú de pausa
- [13 · 05 — UI y UX de juego §2.1, §2.2 y §3.5a](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md) — el mapa de pantallas, las cinco leyes del foco y el botón de cuatro estados

---

## Fuentes

- Manual oficial de GameMaker (espejo local, `09 - Manual oficial/manual-lts-2026-es/`), consultado 2026-09-06:
  - [`instance_deactivate_all`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Instances/Deactivating_Instances/instance_deactivate_all.htm) y [Desactivación de instancias](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Instances/Deactivating_Instances/Deactivating_Instances.htm) — «no son procesadas de ninguna manera»
  - [`physics_pause_enable`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Physics/The_Physics_World/physics_pause_enable.htm) — el aviso explícito de que un cuerpo físico se sigue simulando bajo una instancia desactivada
  - [`time_source_resume`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Time_Sources/time_source_resume.htm) y [`time_source_pause`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Time_Sources/time_source_pause.htm) — el arrastre a los hijos
  - [`texturegroup_get_status`](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_get_status.htm) y [`texturegroup_load`](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Textures/texturegroup_load.htm) — el estado discreto de 4 valores
  - [`get_timer`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Date_And_Time/get_timer.htm) — microsegundos desde el arranque, base de la duración mínima
  - [`application_surface`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Drawing/Surfaces/application_surface.htm) — el patrón de post-procesado ya documentado en 01/11
- `_indice/simbolos.json` de esta biblioteca (extraído del `GmlSpec.xml` del runtime GMS2 2026.0.0.23) — fuente de verdad para cada símbolo citado en este documento

---

**Anti-alucinación — símbolos que se comprobaron y NO existen** (por si algún día parecen
plausibles): `texturegroup_get_all`, `texturegroup_get_texture` (existe `texturegroup_get_textures`,
en plural), `texturegroup_get_name` (existe `texturegroup_get_names`, en plural),
`texture_group_load`, `texturegroup_load_status`, `layer_sequence_resume` (el verbo correcto es
`layer_sequence_play`), `time_source_pause_all`, `part_system_pause_all`,
`layer_sequence_pause_all`, `part_system_get_all`, `audio_bus_get_gain` y `audio_bus_set_gain`
(el bus de audio es un **struct** con miembro `.gain`, no funciones — ver `audio_bus_main.gain`),
`application_surface_get_texture`.
