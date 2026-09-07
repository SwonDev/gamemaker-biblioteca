# 50 · Juego de lucha

> **Dificultad:** alta · **Antes de esto:** [`04 · 30 — Combate cuerpo a cuerpo`](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md)
> **entero**, no solo hojeado — este documento no repite ni la hitbox, ni la hurtbox, ni el
> controlador único en `End Step`, ni `hit_stop`/`hit_complete`, ni el escalado de daño básico:
> los reutiliza y los extiende. `04 · 30` §1.3 lo dice explícitamente: la arquitectura B (sin
> instancias, §5.11 de ese documento) es la que hace falta «si tu juego es de lucha y necesitas
> frame data exacta con muchas cajas», y no la desarrolla porque un juego de lucha necesita
> «decenas de cajas» y «frame data exacta» — eso es justo lo que empieza aquí.
>
> **Qué NO cubre este documento** (y dónde está): las tres cajas y su porqué, el vocabulario base
> de *frame data* (arranque/activo/recuperación, hitstun/blockstun, cancel, i-frames, poise,
> juggle) — todo eso vive en `04 · 30` y aquí se **usa**, no se repite. El *hit stop*, la sacudida
> de cámara, las partículas y el flash del golpe están en
> [`04 · 15 — Game feel y juice`](./15%20-%20Game%20feel%20y%20juice.md). El movimiento y
> `move_and_collide()` están en [`01 · 08`](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md).
> El multijugador en general —autoridad del servidor, predicción, interpolación, y el propio
> sistema `rollback_*` del runtime— está en
> [`04 · 14 — Multijugador`](./14%20-%20Multijugador.md); aquí sólo se añade lo específico de
> lucha y se **avisa** de una cosa que `04 · 14` no dice con esta fecha exacta (§3.8).

---

## 1 · Los principios

### 1.1 · Qué cambia respecto a `04 · 30`

`04 · 30` construye el sistema de combate — hitbox, hurtbox, cancels, combos, i-frames, parry,
poise — para **cualquier** juego con golpes cuerpo a cuerpo. Un juego de lucha 1 contra 1 es el
caso más exigente de ese mismo sistema, y lo es en cuatro sitios muy concretos:

| En `04 · 30` | En un juego de lucha |
|---|---|
| Una caja por ataque, fija durante todo el activo | **Varias cajas, distintas en cada fotograma** — un tajo que se mueve, un multi-hit con daño distinto por impacto |
| `cancela_a`: una lista de nombres por ataque | Una **tabla de reglas** por grupos (ligero → medio → especial → súper), porque un elenco tiene decenas de movimientos, no cuatro |
| El jugador pulsa un botón | El jugador ejecuta una **secuencia direccional** (cuarto de círculo, carga) que hay que reconocer entre docenas de pulsaciones por segundo, con tolerancia |
| Daño se escala; el resto no | **Daño Y aturdimiento** se escalan — si no, aparecen combos que no terminan nunca (§3.4) |
| Un enemigo, telegrafiado, sin recursos propios | Un **rival humano** con su propia barra, sus propios cancels y su propio *netcode* si juega en línea |

### 1.2 · Vista lateral, no cenital: por qué NO hace falta el eje Z falso

Antes de escribir una línea: un juego de lucha clásico (*Street Fighter*, *Guilty Gear*, *Tekken*
en su plano de combate) es **vista lateral**. Saltar es un movimiento real en `y`, con gravedad y
`vel_y`, exactamente el patrón de [`04 · 01 — Plataformas 2D`](./01%20-%20Plataformas%202D.md):
no hace falta inventar una variable `z` separada como en
[`04 · 46 — Eje Z falso`](./46%20-%20Eje%20Z%20falso%20-%20altura%2C%20sombras%20y%20profundidad%20en%20un%20juego%202D.md),
porque ese documento resuelve un problema distinto — simular altura en una cámara **cenital**,
donde `y` ya está ocupada por la profundidad del suelo. En vista lateral `y` está libre: úsala
para lo que es, un salto de verdad, con `place_meeting`/`move_and_collide` contra el suelo real.
Si tu juego de lucha tiene un plano de esquiva lateral (entrar/salir de la pantalla, al estilo de
algunos *3D fighters*), eso sí es un tercer eje de verdad — y ese caso queda fuera de este
documento (⚠️ no lo cubre ninguno de esta biblioteca todavía).

### 1.3 · Vocabulario nuevo (el de `04 · 30` no se repite)

`04 · 30` §1.2 ya definió arranque/activo/recuperación, hitstun/blockstun, ventaja, cancel, hit
confirm, i-frames, prioridad, poise, juggle, escalado de daño, contragolpe y buffer de entrada,
citando el glosario de Infil y Dustloop. Estos son los que le faltan, de las mismas dos fuentes,
consultadas en vivo el 2026-09-07 (ver Fuentes):

| Término | Qué es |
|---|---|
| **Notación numpad** | Sistema estándar para escribir comandos: el teclado numérico mapea las 8 direcciones + neutro, **siempre asumiendo que el personaje mira a la derecha**. `6` es «hacia delante», `4` es «hacia atrás», `2` es «abajo». `236` es un cuarto de círculo (abajo → abajo-adelante → adelante) — Dustloop, página *Notation* |
| **Motion input** | Un comando que exige una secuencia de direcciones antes del botón (cuarto de círculo, media luna, 360°), distinto de un **command normal** (una sola dirección + botón, como `6P`) |
| **Carga** (*charge*) | Mantener una dirección (normalmente atrás o abajo) durante un tiempo antes de poder ejecutar el especial al invertirla — «tienden a ser relativamente potentes comparados con especiales de otros métodos, como un cuarto de círculo, que se puede ejecutar más rápido y en más situaciones» (Dustloop, *Charge Input*) |
| **Negative edge** | «Usar la SUELTA del botón para ejecutar ataques. […] Algunos movimientos con negative edge también requieren motions especiales» (Dustloop, *Negative Edge*) |
| ***Command throw* / agarre de comando** | «Un agarre que se ejecuta con un comando especial como `214C`. Generalmente tiene propiedades especiales frente a un agarre normal, como más daño o ser intecheable» (Dustloop, *Command Throw*) |
| ***Tech*** | «Recuperarse de una caída o de un estado de hitstun aéreo, normalmente pulsando un botón» (Dustloop, *Tech*) |
| ***Chip damage*** | «Daño sufrido al bloquear un ataque. Normalmente sólo los especiales y los súper hacen chip damage, aunque hay excepciones» (Dustloop, *Chip Damage*) |
| ***Okizeme*** | Del japonés 起き攻め: «atacar a un oponente que está a punto de levantarse tras una caída, normalmente con *meaties* o *mix-ups*» (Dustloop, *Okizeme*) |
| ***Meaty*** | «Golpear a un oponente para cubrir el momento en que pierde la invulnerabilidad. […] Usar intencionadamente un fotograma activo TARDÍO de un ataque, en vez del primero, para golpear con más ventaja» (Dustloop, *Meaty*) |
| ***Cross-up*** | «Atacar al oponente tras cambiar de qué lado horizontal estás, normalmente saltando por encima» (Dustloop, *Cross-up*) |
| ***Reversal*** | «Ejecutar un ataque lo antes posible tras recibir un golpe o salir de hitstun/blockstun», normalmente con invulnerabilidad de arranque (Dustloop, *Reversal*) |
| ***Frame trap*** | «Dejar un pequeño hueco en la ofensiva a propósito, para incitar al defensor a atacar y castigarlo» (Dustloop, *Frame Trap*) |
| **RPS de la levantada** | Atacante y defensor tienen opciones que sólo baten a ciertas respuestas: si el defensor hace *reversal*, el atacante puede bloquear; si el atacante bloquea, el defensor recupera la iniciativa (Dustloop, *RPS*) |

### 1.4 · El mapa de este documento

```
1. Motor de comandos       → el jugador introduce una secuencia, el juego decide qué se ejecuta
2. Frame data en datos     → decenas de cajas, una por fotograma, editables sin recompilar
3. Cancels y gatling       → qué puede cancelar a qué, para un elenco entero, no un ataque suelto
4. Pushback y escalado     → por qué el paso 1-3 solo, sin esto, genera combos que no terminan
5. Agarres y tech          → el tercer vértice del triángulo golpe/agarre/bloqueo
6. Levantada y presión     → qué pasa cuando alguien cae al suelo, y cómo se explota con ventaja
7. Barra de súper          → el recurso que conecta todo lo anterior con el mando del jugador
8. La verdad del netcode   → por qué esto es lo más difícil de poner en red, y qué queda
```

---

## 2 · El método, paso a paso

```
1. Un botón, un golpe, sin motion inputs. Frame data real (04 · 30 ya te lo da).
2. Añade el historial direccional y UN comando de motion (§3.1). Antes de añadir el segundo,
   comprueba que el primero se siente bien: tolerante mesa/pad, sin falsos positivos.
3. Prioridad entre comandos que comparten prefijo (§3.1.4) — imprescindible en cuanto tengas un
   especial Y un súper que empiecen igual.
4. Cajas por fotograma en datos (§3.2), NO en código: mueve el primer ataque de "una caja fija"
   a "un array de cajas por fotograma" y comprueba que el resto del sistema (04 · 30 §5.6) no
   se entera del cambio.
5. Tabla de cancels por grupo (§3.3) en cuanto tengas más de 6-8 movimientos: listar cancela_a
   a mano por movimiento deja de escalar antes de lo que crees.
6. Escalado de hitstun + pushback creciente (§3.4). Sin esto el paso 5 te regala un infinito.
7. Agarre con tech (§3.5). Es el tercer vértice del triángulo — sin él, bloquear es gratis.
8. Levantada, invulnerabilidad de despertar, guardia alta/baja y guard crush (§3.6).
9. Barra de súper (§3.7): llenado, gasto, EX, guard cancel.
10. Sólo entonces, si el juego va a jugarse en línea: §3.8, con los ojos abiertos.
```

Cada paso es jugable antes de pasar al siguiente — el mismo criterio de escalado que usa
`04 · 30` §8.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 · Motor de comandos

#### 3.1.1 · Por qué existe

Un botón se resuelve con `keyboard_check_pressed()` y punto: `04 · 30` §5.8 ya lo hace con
`InputBuffer` (`06 · scr_input_buffer.gml`). Un **motion input** no — necesitas **recordar hacia
dónde apuntaba el stick/cruceta en los últimos N fotogramas**, porque el cuarto de círculo se
completa varios fotogramas antes de que se pulse el botón que lo dispara. `InputBuffer` no
guarda eso: guarda si un botón *concreto* está pendiente, no una secuencia de direcciones. Hace
falta una pieza nueva — no lo sustituye, lo complementa: los botones sueltos (un golpe ligero sin
motion) siguen pasando por `InputBuffer` exactamente igual que en `04 · 30`.

#### 3.1.2 · Notación numpad, relativa al frente

Todo comando se define **como si el personaje mirara siempre a la derecha** (la convención de la
§1.3): `6` es delante, `4` es atrás, `2` es abajo. La traducción de teclas físicas a numpad
refleja el resultado según hacia dónde mira `image_xscale`, con el mismo patrón de signo que usa
`04 · 30` para voltear cajas:

```gml
// ---------------------------------------------------------------------------
// scr_comandos_lucha — parte 1: leer la dirección física como dígito numpad
// Verificado: keyboard_check, gamepad_button_check, gp_padu/d/l/r, sign
// ---------------------------------------------------------------------------

/// @func entrada_direccion_numpad(_dueno)
/// @desc Traduce las teclas de dirección MANTENIDAS ahora a notación numpad
///       (1-9, 5 = neutro), reflejada según hacia dónde mira `_dueno`. `6` es
///       SIEMPRE "hacia delante" — la convención estándar del género (§1.3,
///       Dustloop · Notation).
/// @param {Id.Instance} _dueno
/// @returns {Real} Un dígito 1-9.
function entrada_direccion_numpad(_dueno)
{
    var _arriba = keyboard_check(vk_up)    || gamepad_button_check(0, gp_padu);
    var _abajo  = keyboard_check(vk_down)  || gamepad_button_check(0, gp_padd);
    var _izq    = keyboard_check(vk_left)  || gamepad_button_check(0, gp_padl);
    var _der    = keyboard_check(vk_right) || gamepad_button_check(0, gp_padr);

    var _h_fisico = _der - _izq;    // -1, 0, 1
    var _v_fisico = _arriba - _abajo;

    var _signo = sign(_dueno.image_xscale);
    if (_signo == 0) _signo = 1;

    // La aritmética del numpad: 5 es el centro; +1 horizontal mueve a la
    // columna de al lado (4/5/6), +3 vertical mueve a la fila de arriba
    // (7/8/9) o de abajo (1/2/3). Las cuatro diagonales salen solas.
    return 5 + (_h_fisico * _signo) + (_v_fisico * 3);
}
```

> ⚠️ El mando analógico (`gamepad_axis_value` con `gp_axislh`/`gp_axislv`) se puede sumar al
> D-pad con la misma zona muerta de 0,25 que usa
> [`01 · 12 §…`](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado%2C%20ratón%20y%20gamepad.md)
> para movimiento en 4 direcciones. Un juego de lucha serio casi siempre se juega con cruceta o
> palanca — no inviertas tiempo en el analógico hasta que el D-pad funcione perfecto.

#### 3.1.3 · El historial: sólo cambios, no fotogramas

Guardar una entrada por fotograma desperdicia memoria sin necesidad (a 60 fps, un segundo de
cruceta quieta son 60 entradas idénticas). El truco: **una entrada nueva sólo cuando la
dirección cambia**, con su fotograma de inicio. Comparar comandos contra esto es barato incluso
con docenas de movimientos en la tabla.

```gml
// ---------------------------------------------------------------------------
// scr_comandos_lucha — parte 2: el historial comprimido y la carga
// Verificado: array_push, array_shift, array_length
// ---------------------------------------------------------------------------

#macro COMANDO_HISTORIAL_MAX  16   // entradas (cambios de dirección), no fotogramas

/// @func MotorComandos()
/// @desc Historial direccional comprimido de una entidad. Uno por jugador
///       (a la IA, si ejecuta comandos igual que el humano, también le hace
///       falta — ver 04 · 31 para cómo decide CUÁNDO, no CÓMO se ejecuta).
function MotorComandos() constructor
{
    historial    = [];   // { dir, frame } — sólo cambios de dirección
    frame_actual = 0;
    dir_anterior = 5;

    // Carga (§3.1.6): cuántos fotogramas seguidos lleva la MISMA dirección física.
    carga_direccion = 5;
    carga_frames    = 0;

    /// @desc Una vez por fotograma, con el resultado de entrada_direccion_numpad().
    ///       Llámalo en el Begin Step, ANTES de comprobar ningún botón.
    static tick = function(_dir)
    {
        frame_actual++;

        if (_dir != dir_anterior)
        {
            array_push(historial, { dir : _dir, frame : frame_actual });
            if (array_length(historial) > COMANDO_HISTORIAL_MAX) array_shift(historial);
            dir_anterior = _dir;
        }

        if (_dir == carga_direccion) { carga_frames++; }
        else { carga_direccion = _dir; carga_frames = 1; }
    };

    /// @desc ¿Lleva cargando `_direccion` al menos `_frames_necesarios` fotogramas?
    /// @param {Real} _direccion
    /// @param {Real} _frames_necesarios
    /// @returns {Bool}
    static carga_lista = function(_direccion, _frames_necesarios)
    {
        return (carga_direccion == _direccion) && (carga_frames >= _frames_necesarios);
    };
}
```

#### 3.1.4 · Reconocer una secuencia, con tolerancia — y por qué existe la tolerancia

Un jugador humano casi nunca pasa por los dígitos exactos de un cuarto de círculo: suele
saltarse la diagonal intermedia, o rebasarla un poco. Exigir la secuencia exacta hace el comando
**se sienta roto** aunque el código sea «correcto» — el jugador no puede saber que su ejecución
fue un dígito distinta a la esperada. Por eso cada paso del patrón no es un dígito, es un
**conjunto** de dígitos aceptables:

```gml
// ---------------------------------------------------------------------------
// scr_comandos_lucha — parte 3: conjuntos de dirección reutilizables
// ---------------------------------------------------------------------------
#macro NP_ABAJO       [1, 2, 3]   // cualquier "abajo-ish"
#macro NP_ABAJO_ADEL  [2, 3, 6]   // el paso intermedio del cuarto de círculo — puede saltarse
#macro NP_ADELANTE    [3, 6, 9]   // tolera el overshoot típico al soltar rápido
#macro NP_ATRAS       [1, 4, 7]
#macro NP_ABAJO_ATRAS [1, 2, 4]
#macro NP_ARRIBA      [7, 8, 9]
```

La búsqueda escanea el historial **hacia atrás**, empezando por el ÚLTIMO paso del patrón (el
más cercano al botón que cierra el comando) y retrocediendo. Es la misma idea que usan los
parsers de comando de los motores de lucha reales: comprobar «¿hubo un cuarto de círculo
terminando justo antes de este botón?» en el momento en que el botón se pulsa, en vez de llevar
un autómata de estados por comando que avanza mientras juegas:

```gml
// ---------------------------------------------------------------------------
// scr_comandos_lucha — parte 4: el comparador
// Verificado: array_length, array_contains
// ---------------------------------------------------------------------------

/// @func comando_coincide(_historial, _patron, _frame_hasta, _ventana)
/// @desc ¿Aparece `_patron` como subsecuencia de `_historial`, con el ÚLTIMO
///       paso resuelto en o antes de `_frame_hasta` y el PRIMER paso no más
///       allá de `_ventana` fotogramas atrás? Tolera huecos de neutro entre
///       pasos (un regreso breve a 5 no invalida nada) y direcciones que no
///       pertenecen a ningún paso (se ignoran, no rompen la búsqueda).
/// @param {Array<Struct>} _historial Del MotorComandos: {dir, frame}.
/// @param {Array<Array<Real>>} _patron Un array de PASOS; cada paso es un
///        array de dígitos numpad aceptables para ese paso (§ arriba).
/// @param {Real} _frame_hasta   Normalmente el fotograma del botón que cierra.
/// @param {Real} _ventana       Fotogramas máximos entre el primer paso y `_frame_hasta`.
/// @returns {Struct|Undefined}  { frame_inicio } si coincide; si no, undefined.
function comando_coincide(_historial, _patron, _frame_hasta, _ventana)
{
    var _pasos = array_length(_patron);
    if (_pasos == 0) return undefined;

    var _paso = _pasos - 1;                  // empezamos por el paso MÁS RECIENTE
    var _idx  = array_length(_historial) - 1;

    while (_idx >= 0 && _paso >= 0)
    {
        var _entrada = _historial[_idx];

        if (_frame_hasta - _entrada.frame > _ventana) return undefined;   // fuera de ventana

        if (array_contains(_patron[_paso], _entrada.dir))
        {
            if (_paso == 0) return { frame_inicio : _entrada.frame };     // patrón completo
            _paso--;
        }

        _idx--;
    }

    return undefined;   // se acabó el historial sin completar todos los pasos
}
```

**Por qué existe la tolerancia**, en tres razones concretas (no es un capricho de diseño):

1. **Imprecisión física real.** Un D-pad y un stick físico pasan por estados intermedios que un
   sondeo a 60 Hz puede no capturar en un fotograma exacto — la diagonal se «salta» aunque el
   jugador la haya recorrido de verdad.
2. **La ventana temporal absorbe la velocidad de ejecución.** Un jugador competitivo ejecuta un
   cuarto de círculo en 6-10 fotogramas; alguien aprendiendo, en 20-30. `_ventana` decide cuánta
   de esa diferencia se acepta sin dejar de sentirse «intencional» — demasiado ancha y comandos
   no relacionados se disparan solos; demasiado estrecha y el juego rechaza intentos honestos.
3. **Accesibilidad.** No todo el mundo tiene la misma destreza motriz fina. La tolerancia por
   conjuntos (en vez de por dígito exacto) es la forma más barata de ampliar quién puede jugar
   sin tocar el balance del propio movimiento.

#### 3.1.5 · Prioridad entre comandos que comparten prefijo

Un súper `236236P` y un especial `236P` terminan en el mismo botón. Si el juego comprobara el
especial primero, un jugador que acaba de hacer el doble cuarto de círculo se quedaría con el
especial barato en vez del súper. La solución **no** es un retardo ni una espera: es **el orden
en que se comprueban los patrones**. Se listan de más largo (más específico) a más corto, y gana
el primero que coincida:

```gml
// ---------------------------------------------------------------------------
// scr_comandos_lucha — parte 5: resolver la prioridad entre comandos
// ---------------------------------------------------------------------------

/// @func comando_resolver(_historial, _comandos, _frame_hasta)
/// @desc De una lista de comandos que comparten botón de cierre, devuelve el
///       PRIMERO cuyo patrón coincide. `_comandos` debe venir YA ORDENADO de
///       más largo a más corto — así el súper se prueba antes que el
///       especial, y el especial gana sólo si el súper no encajó.
/// @param {Array<Struct>} _historial
/// @param {Array<Struct>} _comandos  Cada uno: { nombre, patron, ventana }.
/// @param {Real} _frame_hasta
/// @returns {String} El nombre del primer comando que coincide, o "" si ninguno.
function comando_resolver(_historial, _comandos, _frame_hasta)
{
    var _n = array_length(_comandos);
    for (var i = 0; i < _n; i++)
    {
        var _c = _comandos[i];
        if (comando_coincide(_historial, _c.patron, _frame_hasta, _c.ventana) != undefined)
        {
            return _c.nombre;
        }
    }
    return "";
}
```

```gml
// obj_jugador_lucha — Create
// Cuarto de círculo adelante ("236") y su doble ("236236"), en ese orden:
// más largo primero. La ventana del súper es más ancha porque hay que
// completar el doble del recorrido.
global.comandos_jugador = [
    { nombre : "super_bola_energia",
      patron  : [NP_ABAJO, NP_ABAJO_ADEL, NP_ADELANTE, NP_ABAJO, NP_ABAJO_ADEL, NP_ADELANTE],
      ventana : 40 },
    { nombre : "bola_de_energia",
      patron  : [NP_ABAJO, NP_ABAJO_ADEL, NP_ADELANTE],
      ventana : 16 }
];
```

#### 3.1.6 · Carga: una precondición de duración, no una secuencia

Un movimiento de carga (`[4]6`, mantener atrás y soltar hacia delante) no es una subsecuencia de
direcciones: es una **condición de tiempo** («¿llevas cargando atrás lo suficiente?») seguida de
un cambio brusco. Se resuelve aparte, con `carga_lista()` de la §3.1.3:

```gml
// obj_jugador_lucha — Step (comprobación de un especial de carga)
if (comandos.carga_lista(4, 45) && entrada_direccion_numpad(id) == 6 && _p_pulsado)
{
    ataque_empezar("bola_de_energia_carga");
    comandos.carga_frames = 0;    // consumida: hay que recargar para repetirla
}
```

#### 3.1.7 · *Negative edge*: disparar también al soltar el botón

La §1.3 ya lo definió: ejecutar el ataque al **soltar** el botón, no sólo al pulsarlo. Sirve para
encadenar dos especiales sin tener que levantar y volver a apretar el mismo botón entre uno y
otro — mantén pulsado, haz la segunda motion, suelta, y el segundo especial sale igual. Se activa
**sólo** para los comandos de motion, nunca para los botones sueltos (si también disparara un
golpe ligero normal, cada pulsación produciría DOS golpes: uno al bajar el dedo, otro al
subirlo):

```gml
// ---------------------------------------------------------------------------
// obj_jugador_lucha — Begin Step
// Verificado: keyboard_check_pressed, keyboard_check_released,
// gamepad_button_check_pressed, gamepad_button_check_released, gp_face1
// ---------------------------------------------------------------------------
comandos.tick(entrada_direccion_numpad(id));

var _p_pulsado = keyboard_check_pressed(ord("J")) || gamepad_button_check_pressed(0, gp_face1);
var _p_soltado = keyboard_check_released(ord("J")) || gamepad_button_check_released(0, gp_face1);

// La motion se comprueba en el flanco de BAJADA (uso normal) y, si el
// personaje lo permite, también en el de SUBIDA (negative edge).
if (_p_pulsado || (_p_soltado && permite_negative_edge))
{
    var _nombre = comando_resolver(comandos.historial, global.comandos_jugador, comandos.frame_actual);

    if (_nombre != "")       { ataque_empezar(_nombre); }
    else if (_p_pulsado)     { ataque_empezar("golpe_ligero"); }   // sin motion: normal suelto
}
```

---

### 3.2 · Estados por fotograma con *frame data* en datos

#### 3.2.1 · Por qué la arquitectura B, y qué le falta

`04 · 30` §5.11 ya define la arquitectura sin instancias — comprobar el rectángulo del ataque
directamente cada fotograma activo, sin crear `obj_hitbox` — y dice que es «ideal para… un juego
de lucha con frame data exacta y decenas de cajas». Lo que le falta para un elenco real: **una
sola caja por ataque no basta**. Un tajo que se mueve durante sus 4 fotogramas activos, o un
multi-hit donde cada impacto pega distinto, necesita **una caja (o varias) por fotograma**, no
una caja fija repetida. `04 · 30` §8 ya lo insinúa como forma de escalar
(`por_frame : [ undefined, undefined, {caja}, {caja} ]`); esto es esa idea, completa.

#### 3.2.2 · El struct del movimiento

```gml
// ---------------------------------------------------------------------------
// scr_frame_data_lucha — la tabla vive en datos, no en código
// Verificado: variable_struct_exists
//
// CONVENCIÓN DE FOTOGRAMAS: la misma de 04 · 30 §5.1 — `arranque` NO incluye
// el primer activo. `cajas_por_frame` tiene un índice POR CADA fotograma del
// movimiento entero (arranque + activo + recuperación); índice 0 = fotograma 1.
// Cada entrada es `undefined` (sin caja ese fotograma) o un ARRAY de cajas
// (soporta multi-hit: dos cajas activas el mismo fotograma).
// ---------------------------------------------------------------------------
global.ataques_lucha =
{
    golpe_medio_arco : {
        sprite : spr_medio_arco,
        arranque : 8, activo : 4, recuperacion : 12,
        altura : "media",                     // "alta" | "media" | "baja" — §3.6.3
        grupo  : "normal_medio",              // para la tabla de cancels — §3.3
        dano : 9, empuje : 4.0,
        hitstun : 16, blockstun : 8, rompe_aguante : 1, rompe_guardia : 8,
        cancel_ini : 9, cancel_fin : 15, cancela_en_vacio : false,
        sonido : snd_golpe_medio,

        // Un fotograma por índice, arranque(8) + activo(4) + recuperacion(12) = 24.
        // Sólo los 4 activos (índices 8-11) llevan caja; el resto, undefined.
        // La caja se DESPLAZA conforme el arco avanza: esto es lo que la caja
        // única de 04 · 30 no podía representar.
        cajas_por_frame : [
            undefined, undefined, undefined, undefined,      // 1-4  arranque
            undefined, undefined, undefined, undefined,      // 5-8  arranque
            [ { dx : 10, dy : -14, ancho : 16, alto : 14 } ], // 9    activo 1
            [ { dx : 16, dy : -12, ancho : 18, alto : 14 } ], // 10   activo 2
            [ { dx : 22, dy : -10, ancho : 18, alto : 14 } ], // 11   activo 3 — punta del arco
            [ { dx : 26, dy : -8,  ancho : 14, alto : 12 } ], // 12   activo 4
            undefined, undefined, undefined, undefined,      // 13-16 recuperación
            undefined, undefined, undefined, undefined,      // 17-20 recuperación
            undefined, undefined, undefined, undefined       // 21-24 recuperación
        ]
    },

    patada_baja_multi : {
        sprite : spr_patada_multi,
        arranque : 5, activo : 6, recuperacion : 10,
        altura : "baja", grupo : "normal_ligero",
        dano : 3, empuje : 1.0,
        hitstun : 10, blockstun : 5, rompe_aguante : 1, rompe_guardia : 3,
        cancel_ini : 6, cancel_fin : 11, cancela_en_vacio : false,
        sonido : snd_patada,

        // Multi-hit de verdad: dos impactos, el segundo hace más daño Y más
        // empuje que la definición base — cada caja puede SOBRESCRIBIR sus
        // propios campos (§3.2.3), no sólo su posición.
        cajas_por_frame : [
            undefined, undefined, undefined, undefined, undefined,   // 1-5 arranque
            [ { dx : 8,  dy : 4, ancho : 20, alto : 8 } ],            // 6  activo 1
            undefined,                                                // 7  hueco entre impactos
            [ { dx : 8,  dy : 4, ancho : 20, alto : 8 } ],            // 8  activo 2 (repite)
            undefined,
            [ { dx : 10, dy : 4, ancho : 22, alto : 8, dano : 6, empuje : 3.0 } ], // 10 remate
            undefined,
            undefined, undefined, undefined, undefined, undefined,
            undefined, undefined, undefined, undefined, undefined
        ]
    }
};
```

#### 3.2.3 · Leer la caja del fotograma actual

```gml
// ---------------------------------------------------------------------------
// scr_frame_data_lucha — resolver qué hay que dibujar/comprobar este fotograma
// Verificado: array_length, variable_struct_exists
// ---------------------------------------------------------------------------

/// @func cajas_del_frame(_def, _frame_ataque)
/// @desc Las cajas activas en `_frame_ataque` (1-indexado, igual que
///       fase_del_ataque() de 04 · 30 §5.2). [] si ese fotograma no golpea.
/// @param {Struct} _def          Entrada de global.ataques_lucha.
/// @param {Real}   _frame_ataque
/// @returns {Array<Struct>}
function cajas_del_frame(_def, _frame_ataque)
{
    var _idx = floor(_frame_ataque) - 1;
    if (_idx < 0 || _idx >= array_length(_def.cajas_por_frame)) return [];

    var _entrada = _def.cajas_por_frame[_idx];
    return is_undefined(_entrada) ? [] : _entrada;
}

/// @func caja_efecto_resolver(_def, _caja_frame)
/// @desc Combina la caja de un fotograma con el efecto base del movimiento:
///       si la caja NO trae su propio dano/empuje, hereda el de `_def` —
///       el mismo patrón "campo opcional" que golpe_desde_definicion()
///       en 04 · 30 §5.4.
/// @param {Struct} _def
/// @param {Struct} _caja_frame  Una entrada de cajas_por_frame (dx/dy/ancho/alto).
/// @returns {Struct}
function caja_efecto_resolver(_def, _caja_frame)
{
    return {
        off_x  : _caja_frame.dx,  off_y : _caja_frame.dy,
        ancho  : _caja_frame.ancho, alto : _caja_frame.alto,
        dano   : variable_struct_exists(_caja_frame, "dano")   ? _caja_frame.dano   : _def.dano,
        empuje : variable_struct_exists(_caja_frame, "empuje") ? _caja_frame.empuje : _def.empuje,
        hitstun : _def.hitstun, blockstun : _def.blockstun,
        rompe_aguante : _def.rompe_aguante, rompe_guardia : _def.rompe_guardia,
        altura : _def.altura
    };
}
```

En el `Step` del estado «atacando» (el mismo de `04 · 30` §5.8), sustituye la creación de UNA
caja por un bucle sobre `cajas_del_frame()` — arquitectura B, sin instancias, igual que
`04 · 30` §5.11 pero con la posición y el efecto leídos del fotograma exacto:

```gml
// obj_jugador_lucha — Step, dentro del estado "atacando"
// Verificado: array_length, collision_rectangle_list, ds_list_create, ds_list_destroy
var _cajas = cajas_del_frame(ataque_def, ataque_frame);
var _n = array_length(_cajas);

for (var i = 0; i < _n; i++)
{
    var _clave = string(ataque_frame) + "_" + string(i);      // una clave por caja-fotograma
    if (array_contains(ya_golpeados, _clave)) continue;

    var _signo = sign(image_xscale);
    if (_signo == 0) _signo = 1;

    var _ef  = caja_efecto_resolver(ataque_def, _cajas[i]);
    var _cx  = x + _ef.off_x * _signo;
    var _cy  = y + _ef.off_y;
    var _hw  = _ef.ancho * 0.5;
    var _hh  = _ef.alto  * 0.5;

    var _lista = ds_list_create();
    var _num = collision_rectangle_list(_cx - _hw, _cy - _hh, _cx + _hw, _cy + _hh,
                                        obj_enemigo, false, true, _lista, true);

    for (var j = 0; j < _num; j++)
    {
        var _v = _lista[| j];
        array_push(ya_golpeados, _clave);

        var _dir = point_direction(x, y, _v.x, _v.y);
        with (_v) recibir_golpe({ caja : _ef, atacante : other.id, victima : id, direccion : _dir });
    }
    ds_list_destroy(_lista);   // SIEMPRE — 04 · 30 §5.11
}
```

#### 3.2.4 · Editar sin recompilar

`global.ataques_lucha` es un struct plano: `json_stringify()`/`json_parse()` funcionan sin
cambios, exactamente igual que `04 · 30` §8 ya explica para su tabla más simple — no se repite
aquí. Con `cajas_por_frame` como un array explícito por índice, un editor visual (rectángulos
dibujados con el ratón sobre el sprite, uno por fotograma, exportados a este mismo formato) deja
de ser opcional en cuanto la tabla pase de 10-15 movimientos: escribir a mano las coordenadas de
`dx`/`dy`/`ancho`/`alto` para cada fotograma de cada ataque de un elenco completo no escala. La
persistencia de esa tabla en disco está resuelta en
[`01 · 14 — Persistencia y archivos`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md).

---

### 3.3 · Cancels y *gatling*

#### 3.3.1 · Por qué una tabla y no una lista por movimiento

`04 · 30` §4.4 resuelve el cancel con `cancela_a: ["ligero_2"]` — una lista de **nombres**
concretos por ataque. Funciona con 4-6 ataques. Con un elenco de 20-40 movimientos, escribir a
mano qué cancela a qué, ataque por ataque, es un grafo que nadie recuerda ni mantiene sin
errores. La solución del género —el *gatling*, del glosario de Dustloop: «la categoría especial
de cancels que describe cómo cada personaje puede cancelar normales en otros normales»— es
clasificar cada movimiento en un **grupo**, y definir la regla **entre grupos**, una vez:

```gml
// ---------------------------------------------------------------------------
// scr_cancels_lucha — la tabla de reglas, no una lista por movimiento
// Verificado: variable_struct_exists, array_contains
// ---------------------------------------------------------------------------

// Qué grupo puede cancelarse EN qué grupo. Un especial nunca cancela a un
// súper porque no aparece como clave de la derecha en ninguna fila del
// especial ni del súper: el orden del grafo lo impone la propia tabla, sin
// necesidad de un caso especial en el código.
global.tabla_gatling = {
    normal_ligero  : ["normal_medio", "normal_pesado", "especial"],
    normal_medio   : ["normal_pesado", "especial"],
    normal_pesado  : ["especial"],
    especial       : ["especial_ex", "super"],
    especial_ex    : ["super"],
    super          : []                          // nada cancela un súper
};

/// @func grupo_puede_cancelar(_origen, _destino)
/// @desc ¿El grupo `_origen` puede cancelarse en el grupo `_destino`?
/// @param {String} _origen
/// @param {String} _destino
/// @returns {Bool}
function grupo_puede_cancelar(_origen, _destino)
{
    if (!variable_struct_exists(global.tabla_gatling, _origen)) return false;
    return array_contains(global.tabla_gatling[$ _origen], _destino);
}
```

#### 3.3.2 · Comprobación en el estado «atacando»

Extiende `ataque_cancelable()` de `04 · 30` §5.8 con la comprobación de grupo — la ventana de
fotogramas (`cancel_ini`/`cancel_fin`) y el *hit confirm* (`cancela_en_vacio`) siguen siendo
exactamente los mismos:

```gml
// ---------------------------------------------------------------------------
// scr_cancels_lucha — extiende ataque_cancelable() de 04 · 30 §5.8
// ---------------------------------------------------------------------------

/// @func ataque_cancelable_lucha(_def, _frame, _confirmado, _def_destino)
/// @desc Añade la comprobación de GRUPO a la de 04 · 30 §5.8 (ventana +
///       hit confirm). Las tres condiciones deben cumplirse a la vez.
/// @param {Struct} _def          El ataque en curso.
/// @param {Real}   _frame        Fotograma actual del ataque en curso.
/// @param {Bool}   _confirmado   ¿Ha conectado ya?
/// @param {Struct} _def_destino  El ataque candidato a encadenar.
/// @returns {Bool}
function ataque_cancelable_lucha(_def, _frame, _confirmado, _def_destino)
{
    if (_frame < _def.cancel_ini || _frame > _def.cancel_fin) return false;
    if (!_def.cancela_en_vacio && !_confirmado) return false;
    return grupo_puede_cancelar(_def.grupo, _def_destino.grupo);
}
```

#### 3.3.3 · Cadenas fijas (*target combos*)

Algunos movimientos concretos encadenan sólo en un orden muy específico que no encaja en la
tabla general (un golpe que sólo puede seguirse de OTRO golpe concreto, no de cualquiera de su
grupo). Se resuelve con un campo opcional que, si existe, **sustituye** a la tabla para ese
ataque en concreto:

```gml
// En la entrada del ataque, en global.ataques_lucha:
cadena_fija : ["golpe_medio_arco"],   // SÓLO este ataque puede seguir, aunque el
                                       // grupo permitiría cancelar en varios más
```

```gml
// scr_cancels_lucha — la comprobación completa, con la cadena fija primero
function ataque_cancelable_final(_def, _frame, _confirmado, _nombre_destino, _def_destino)
{
    if (_frame < _def.cancel_ini || _frame > _def.cancel_fin) return false;
    if (!_def.cancela_en_vacio && !_confirmado) return false;

    if (variable_struct_exists(_def, "cadena_fija"))
    {
        return array_contains(_def.cadena_fija, _nombre_destino);
    }

    return grupo_puede_cancelar(_def.grupo, _def_destino.grupo);
}
```

---

### 3.4 · *Pushback*, escalado de daño y de *hitstun*

#### 3.4.1 · Por qué los combos infinitos aparecen SOLOS

`04 · 30` §4.8 ya escala el **daño** por golpe de combo. Eso NO evita un combo infinito: sólo
evita que duela infinito. Un combo que se repite para siempre pero hace 1 de daño por golpe
sigue siendo un combo del que la víctima **nunca sale** — un *softlock* de partida, que en la
práctica es peor que el daño desproporcionado, porque ni siquiera termina en una derrota
jugable.

La causa es puramente aritmética. Compara, para un ataque que se repite sobre sí mismo:

```
tiempo hasta que el atacante puede volver a golpear
    = recuperacion (del golpe anterior) + arranque (del siguiente) + 1

tiempo hasta que la víctima recupera el control
    = hitstun (del golpe que la mantiene atrapada)
```

Si `hitstun >= recuperacion + arranque + 1`, el atacante SIEMPRE golpea antes de que la víctima
pueda actuar — y si la desigualdad es estricta (con margen), cada repetición **no pierde
ventaja**, así que el bucle no tiene ninguna razón para acabar. Con los números de ejemplo de
`04 · 30` §5.1 (`ligero_1`: arranque 4, activo 3, recuperación 9, hitstun 14):

```
recuperacion(9) + arranque(4) + 1 = 14  =  hitstun(14)
```

Exactamente igualado: cada repetición conecta justo cuando la víctima sale del hitstun — un
*frame trap* perfecto, no un infinito (todavía). Pero si `hitstun` fuera 16 en vez de 14, la
desigualdad pasa a `16 >= 14` con **2 fotogramas de margen que no se gastan nunca**: el bucle se
repite indefinidamente sin que la víctima recupere el control ni una sola vez. Ese margen es
exactamente lo que el escalado tiene que **cerrar**, combo adentro.

#### 3.4.2 · La corrección: escalar el *hitstun*, no sólo el daño

```gml
// ---------------------------------------------------------------------------
// scr_escalado_lucha — añade esto junto a ESCALADO_COMBO de 04 · 30 §5.0
// Verificado: clamp, floor, array_length
// ---------------------------------------------------------------------------

// Cae más deprisa que el daño: el objetivo NO es "que duela poco", es "que
// el hueco entre golpes se abra" hasta que la víctima recupere el control
// antes del siguiente impacto — rompiendo la desigualdad de la §3.4.1.
#macro ESCALADO_HITSTUN [1.00, 1.00, 0.90, 0.78, 0.66, 0.55, 0.45, 0.36, 0.28, 0.20, 0.15]

/// @func escalado_de_hitstun(_golpes_previos)
/// @param {Real} _golpes_previos
/// @returns {Real} Entre 0.15 y 1.00.
function escalado_de_hitstun(_golpes_previos)
{
    var _t = ESCALADO_HITSTUN;
    var _i = clamp(floor(_golpes_previos), 0, array_length(_t) - 1);
    return _t[_i];
}
```

Aplícalo en el paso 6 de `recibir_golpe()` (`04 · 30` §5.7), donde hoy se lee
`combate.hitstun = max(combate.hitstun, _caja.hitstun + …)`:

```gml
// recibir_golpe() — sustituye SOLO la línea del hitstun, el resto no cambia
var _hitstun_escalado = round(_caja.hitstun * escalado_de_hitstun(combate.combo_golpes));
combate.hitstun = max(combate.hitstun, _hitstun_escalado + (_contra ? 6 : 0));
```

Con esto, tarde o temprano `hitstun_escalado < recuperacion + arranque + 1` — el bucle SE ROMPE
solo, sin ningún límite artificial de «máximo N golpes» que el jugador sienta como una pared
arbitraria.

#### 3.4.3 · *Pushback* creciente: la otra forma de romper el bucle

El empuje también debería crecer con la repetición — por dos motivos distintos según si el golpe
conectó o fue bloqueado:

- **Al golpear**, un empuje creciente aleja al atacante del alcance de su propio golpe repetido,
  rompiendo bucles de golpes muy rápidos y de alcance corto incluso antes de que el escalado de
  hitstun actúe.
- **Al bloquear**, un empuje mayor (normalmente MAYOR que al golpear — el bloqueo debe alejar más
  que el impacto, para que quien bloquea recupere espacio) es lo que impide un *block string*
  point-blank infinito y **fuerza el reseteo al juego neutral** (*footsies*): sin este empuje, el
  atacante puede plantarse pegado al rival y presionar para siempre sin arriesgar nada.

```gml
// ---------------------------------------------------------------------------
// scr_escalado_lucha — pushback creciente
// ---------------------------------------------------------------------------
#macro PUSHBACK_CRECE_GOLPE   0.10   // +10 % de empuje por golpe consecutivo del combo
#macro PUSHBACK_CRECE_BLOQUEO 0.18   // el bloqueo empuja más — fuerza el reseteo neutral

/// @func empuje_escalado(_empuje_base, _repeticiones, _crecimiento)
/// @param {Real} _empuje_base
/// @param {Real} _repeticiones
/// @param {Real} _crecimiento
/// @returns {Real}
function empuje_escalado(_empuje_base, _repeticiones, _crecimiento)
{
    return _empuje_base * (1 + _repeticiones * _crecimiento);
}
```

`combate.combo_golpes` ya existe en `EstadoCombate` (`04 · 30` §6) y cuenta los golpes conectados
seguidos. Para el bloqueo hace falta un contador hermano — **añádelo** al mismo struct sin
reescribirlo entero:

```gml
// Añadido a EstadoCombate (04 · 30 §6), junto a combo_golpes:
// combate.string_bloqueado = 0;   // golpes bloqueados seguidos, sin soltar el bloqueo
```

Y en el paso 2 «Bloqueo» de `recibir_golpe()` (`04 · 30` §5.7), donde hoy se calcula el empuje al
bloquear con un factor fijo (`_caja.empuje * 0.35`), sustituye por:

```gml
combate.string_bloqueado += 1;
var _empuje_bloqueo = empuje_escalado(_caja.empuje * 0.35, combate.string_bloqueado, PUSHBACK_CRECE_BLOQUEO);
vel_x += lengthdir_x(_empuje_bloqueo, _dir);
```

`combate.string_bloqueado` se resetea a 0 exactamente donde `combo_golpes` ya se resetea (al
dejar de bloquear, o tras `COMBO_OLVIDO_FRAMES` sin recibir nada) — mismo mecanismo, mismo sitio,
sin código nuevo.

---

### 3.5 · Agarres y *tech*

#### 3.5.1 · El triángulo, y por qué la arquitectura ya lo resuelve casi gratis

Golpe, agarre y bloqueo forman un triángulo de piedra-papel-tijera (Dustloop, *RPS*): **golpe
bate a agarre** (el agarre tiene arranque, como cualquier ataque, y un golpe que conecte durante
ese arranque lo interrumpe), **agarre bate a bloqueo** (bloquear no protege contra un agarre — es
la razón de ser de la mecánica) y **bloqueo bate a golpe** (ya resuelto en `04 · 30` §4.6). Si el
triángulo se rompe en cualquier vértice —por ejemplo, si bloquear también parase los
agarres— una de las tres opciones deja de tener sentido y el jugador siempre elige la misma.

```
        Golpe
       ╱      ╲
    bate a    bate a
       ╲      ╱
     Bloqueo ← Agarre
      (bate a agarre... NO: agarre bate a bloqueo)
```

Corregido:

```
Golpe  →  bate a  →  Agarre
Agarre →  bate a  →  Bloqueo
Bloqueo → bate a  →  Golpe
```

**El vértice «golpe bate a agarre» sale gratis** de la arquitectura de `04 · 30`: un intento de
agarre es un estado más con su propio `arranque`, y durante el arranque la entidad sigue usando
su hurtbox normal (`04 · 30` §5.5) — no lleva armadura. Si un golpe rival conecta durante esos
fotogramas, `combate.hitstun` se activa y la máquina de estados corta el intento de agarre
exactamente como cortaría cualquier otro ataque (`04 · 30` §6, `combate.tiene_control()`). No
hace falta ningún código nuevo para ese vértice — sólo **no darle armadura al agarre**.

#### 3.5.2 · El agarre en sí: proximidad, no hitbox

A diferencia de un golpe, un agarre **no pasa por el sistema de hitbox/hurtbox** — no lo bloquea
nada de ese sistema, es justo el punto. Se resuelve con una comprobación de proximidad + postura
al llegar al fotograma activo:

```gml
// ---------------------------------------------------------------------------
// scr_agarres_lucha
// Verificado: instance_place, point_distance, keyboard_check_pressed
// ---------------------------------------------------------------------------

#macro AGARRE_ARRANQUE      5
#macro AGARRE_RADIO         18
#macro AGARRE_VENTANA_TECH  10   // fotogramas para escapar tras conectar
#macro AGARRE_DANO          12
#macro AGARRE_HITSTUN       28   // si NO se escapa

// obj_entidad_lucha — Create (variables de agarre, en ambos jugadores)
agarrando_a       = noone;
agarrado_por      = noone;
agarre_tech_frames = 0;

/// @func agarre_intentar(_atacante)
/// @desc Comprueba si hay una víctima válida al alcance, en el fotograma
///       activo del agarre. NO usa hitbox/hurtbox — el agarre NO se bloquea
///       (§3.5.1): sólo comprueba proximidad y que nadie esté ya agarrado.
/// @param {Id.Instance} _atacante
/// @returns {Bool}
function agarre_intentar(_atacante)
{
    with (_atacante)
    {
        var _signo = sign(image_xscale);
        if (_signo == 0) _signo = 1;

        var _obj = instance_place(x + AGARRE_RADIO * _signo, y, obj_enemigo);
        if (_obj == noone) return false;
        if (_obj.agarrado_por != noone || _obj.agarrando_a != noone) return false;
        if (_obj.combate.iframes > 0) return false;   // invulnerable: el agarre falla

        agarrando_a          = _obj;
        _obj.agarrado_por     = id;
        _obj.agarre_tech_frames = AGARRE_VENTANA_TECH;
        return true;
    }
}
```

#### 3.5.3 · La ventana de escape (*tech*)

Mientras dura la ventana, la víctima puede **escapar** pulsando el mismo botón de agarre —
Dustloop, *Tech*: «recuperarse de una caída o de un estado de hitstun aéreo, normalmente
pulsando un botón». Si no lo hace a tiempo, el agarre se resuelve en daño y aturdimiento:

```gml
// obj_entidad_lucha — Step, para CUALQUIERA que esté agarrado
if (agarrado_por != noone)
{
    if (!instance_exists(agarrado_por)) { agarrado_por = noone; }
    else
    {
        // Se pega a una posición fija relativa al agarrador — igual que el
        // agarre de brawler de 04 · 47 §6, pero aquí SÍ hay ventana de escape.
        x = agarrado_por.x + lengthdir_x(14, agarrado_por.image_xscale > 0 ? 0 : 180);
        y = agarrado_por.y;

        if (agarre_tech_frames > 0)
        {
            agarre_tech_frames--;

            if (keyboard_check_pressed(vk_control))   // mismo botón que el agarre
            {
                // TECH: ambos se separan, sin daño. Empuje simétrico y breve
                // aturdimiento MUTUO para que ninguno tenga un turno gratis.
                agarrado_por.agarrando_a = noone;
                agarrado_por.combate.hitstun = max(agarrado_por.combate.hitstun, 8);
                combate.hitstun = max(combate.hitstun, 8);
                vel_x -= lengthdir_x(4, agarrado_por.image_xscale > 0 ? 0 : 180);
                agarrado_por.vel_x += lengthdir_x(4, agarrado_por.image_xscale > 0 ? 0 : 180);
                agarrado_por = noone;
                audio_play_sound(snd_tech, 10, false);
            }
        }
        else if (agarrado_por.agarrando_a == id)
        {
            // Ventana agotada sin tech: se resuelve el agarre.
            combate.vida    -= AGARRE_DANO;
            combate.hitstun  = AGARRE_HITSTUN;
            agarrado_por.agarrando_a = noone;
            agarrado_por = noone;
        }
    }
}
```

> ⚠️ **Diseño, no obligación técnica.** Que un agarre falle contra alguien agachado o en el aire
> (§3.5.4) es una decisión de cada juego, no algo que imponga esta arquitectura. `agarre_intentar()`
> tal y como está aquí agarra a cualquiera al alcance — añade la comprobación de postura si tu
> diseño la necesita.

#### 3.5.4 · Agarre aéreo

La variante para cuando ambos combatientes están en el aire (o, según el diseño, un agarre de
tierra a aire) es la misma función con la comprobación de suelo invertida — y normalmente un
resultado **más punitivo** (caída dura, intecheable) como compensación por el riesgo de
intentarlo en el aire:

```gml
/// @func agarre_aereo_intentar(_atacante)
/// @desc Igual que agarre_intentar(), pero exige que AMBOS estén en el aire.
/// @param {Id.Instance} _atacante
/// @returns {Bool}
function agarre_aereo_intentar(_atacante)
{
    with (_atacante)
    {
        if (en_el_suelo) return false;

        var _signo = sign(image_xscale);
        if (_signo == 0) _signo = 1;

        var _obj = instance_place(x + AGARRE_RADIO * _signo, y, obj_enemigo);
        if (_obj == noone || _obj.en_el_suelo) return false;
        if (_obj.agarrado_por != noone) return false;

        agarrando_a           = _obj;
        _obj.agarrado_por      = id;
        _obj.agarre_tech_frames = AGARRE_VENTANA_TECH - 2;   // ventana más corta: cae mientras decide
        return true;
    }
}
```

---

### 3.6 · Levantada y presión

#### 3.6.1 · Opciones al levantarse

Al caer, la víctima elige (o el diseño decide por ella con un temporizador fijo) **cuándo**
levantarse: cuanto antes, menos tiempo tiene el atacante para preparar una entrada; cuanto más
tarde, más segura pero más tiempo de presión concede.

```gml
// ---------------------------------------------------------------------------
// scr_levantada_lucha
// Verificado: keyboard_check_pressed
// ---------------------------------------------------------------------------
#macro CAIDA_FRAMES_QUICK_RISE_MIN 12   // antes de esto, ni se puede pedir la levantada rápida
#macro CAIDA_FRAMES_TOTAL          40   // levantada "normal": tiempo fijo si no se pide antes
#macro DESPERTAR_IFRAMES           8    // invulnerabilidad AL LEVANTARSE — reutiliza combate.iframes

// Fragmento del struct de estados del jugador (04 · 30 §5.8), un estado más:
levantandose : {
    enter : function()
    {
        caida_frame = 0;
        sprite_index = spr_jugador_caido;
    },
    update : function()
    {
        caida_frame++;

        // Levantada rápida: pedirla adelanta el momento de ponerse en pie.
        if (caida_frame >= CAIDA_FRAMES_QUICK_RISE_MIN
        &&  (keyboard_check_pressed(vk_down) || keyboard_check_pressed(ord("J"))))
        {
            caida_frame = CAIDA_FRAMES_TOTAL;
        }

        if (caida_frame >= CAIDA_FRAMES_TOTAL)
        {
            combate.iframes = DESPERTAR_IFRAMES;   // el mismo campo de 04 · 30 §6 y §5.10
            fsm.set("quieto");
        }
    }
}
```

Reutilizar `combate.iframes` para la invulnerabilidad de despertar no es un atajo: es
exactamente el mismo campo que ya dibuja en amarillo el depurador de cajas de `04 · 30` §5.10, así
que la ventana de despertar se **ve** sin escribir una sola línea de depuración nueva.

#### 3.6.2 · *Okizeme*: el *meaty*, medido en fotogramas

Un *meaty* limpio (Dustloop, *Meaty*: golpear justo cuando la invulnerabilidad de la víctima
termina) es pura aritmética de *frame data* — la misma resta que ya usa `04 · 30` §4.3 para la
ventaja, aplicada al instante del despertar en vez de al instante del golpe:

```gml
/// @func meaty_margen(_frames_hasta_activo, _iframes_restantes_victima)
/// @desc Diferencia en fotogramas entre "cuándo golpea el atacante" y
///       "cuándo deja de ser invulnerable la víctima". Positivo = golpea
///       DESPUÉS de que acabe la invulnerabilidad (limpio). Cero o negativo
///       = el golpe llega mientras la víctima sigue invulnerable: no conecta.
/// @param {Real} _frames_hasta_activo
/// @param {Real} _iframes_restantes_victima
/// @returns {Real}
function meaty_margen(_frames_hasta_activo, _iframes_restantes_victima)
{
    return _frames_hasta_activo - _iframes_restantes_victima;
}
```

Un valor cercano a 0 (positivo, pero pequeño) es el *meaty* «óptimo»: golpea en el primer
instante posible, maximizando la ventaja resultante frente al defensor. Es información útil tanto
para el jugador (aprender el *timing*) como para depurar los propios números de `arranque` de
cada movimiento — si ningún movimiento del elenco puede llegar a `meaty_margen` positivo contra
`DESPERTAR_IFRAMES`, la presión en la levantada no existe en tu juego, sea o no intencional.

#### 3.6.3 · Guardia alta y baja

`04 · 30` §5.7 resuelve la dirección del bloqueo (`bloqueo_valido()`: por delante, no por la
espalda). Le falta la **altura**: un golpe alto (*overhead*) sólo lo para el bloqueo de pie; uno
bajo, sólo el agachado; uno medio, cualquiera de los dos:

```gml
// ---------------------------------------------------------------------------
// scr_guardia_lucha — extiende bloqueo_valido() de 04 · 30 §5.7
// ---------------------------------------------------------------------------

/// @func bloqueo_valido_lucha(_dir, _postura, _altura_ataque)
/// @param {Real}   _dir            Dirección del golpe (igual que 04 · 30 §5.7).
/// @param {String} _postura        "de_pie" o "agachado".
/// @param {String} _altura_ataque  "alta", "baja" o "media" (§3.2.2).
/// @returns {Bool}
function bloqueo_valido_lucha(_dir, _postura, _altura_ataque)
{
    if (!bloqueo_valido(_dir)) return false;   // primero, la dirección (04 · 30)

    if (_altura_ataque == "alta") return (_postura == "de_pie");
    if (_altura_ataque == "baja") return (_postura == "agachado");
    return true;                                // "media": cualquier postura la para
}
```

#### 3.6.4 · *Guard crush*: el bloqueo también se rompe

Bloquear sin límite es tan degenerado como golpear sin límite. La corrección reutiliza
`RecursoCombate` de
[`04 · 36 §3.2`](./36%20-%20Habilidades%2C%20enfriamientos%20y%20recursos%20de%20combate.md#32-recursocombate-el-pool-genérico-y-sus-tres-variantes) —
no hay que escribir un pool de recursos nuevo, es literalmente el mismo struct con el signo de
regeneración a favor de la víctima:

```gml
// obj_jugador_lucha — Create, además de combate = new EstadoCombate(...) (04 · 30 §5.5)
#macro GUARDIA_MAX               60
#macro GUARDIA_REGEN_POR_FRAME   0.35   // se recupera SOLA con el tiempo, no bloqueando
#macro GUARDIA_RETARDO           50     // fotogramas de gracia tras el último bloqueo
#macro GUARD_CRUSH_ATURDIMIENTO  45

combate.guardia = new RecursoCombate(GUARDIA_MAX, GUARDIA_REGEN_POR_FRAME, GUARDIA_RETARDO);
```

Y en el paso 2 «Bloqueo» de `recibir_golpe()` (`04 · 30` §5.7), extendido con la §3.6.3 y la
§3.4.3, con el guard crush como salida:

```gml
// recibir_golpe() — paso 2, versión completa de juego de lucha
if (combate.bloqueando
&&  bloqueo_valido_lucha(_dir, postura, _caja.altura)
&&  !_caja.rompe_bloqueo)
{
    combate.blockstun = max(combate.blockstun, _caja.blockstun);
    combate.vida      -= floor(_caja.dano * 0.15);      // chip damage — Dustloop, Chip Damage

    combate.guardia.gastar(_caja.rompe_guardia);
    combate.string_bloqueado += 1;

    var _empuje = empuje_escalado(_caja.empuje * 0.35, combate.string_bloqueado, PUSHBACK_CRECE_BLOQUEO);
    vel_x += lengthdir_x(_empuje, _dir);

    if (combate.guardia.actual <= 0)
    {
        // GUARD CRUSH: el bloqueo deja de proteger este instante. Aturdimiento
        // completo, igual que si el golpe hubiera conectado limpio.
        combate.blockstun  = 0;
        combate.bloqueando = false;
        combate.hitstun    = GUARD_CRUSH_ATURDIMIENTO;
        audio_play_sound(snd_guard_crush, 10, false);
    }
    else
    {
        audio_play_sound(snd_bloqueo, 10, false);
    }

    return false;
}
```

`combate.guardia.tick()` se llama junto al resto de recursos de la entidad (mismo sitio que
`04 · 36` §3.3 llama a `tick()` de cada `RecursoCombate` desde su gestor por entidad).

#### 3.6.5 · *Cross-up*: una ambigüedad geométrica, no un sistema nuevo

Dustloop, *Cross-up*: «atacar al oponente tras cambiar de qué lado horizontal estás, típicamente
saltando por encima». La detección en sí es geométrica — comparar el lado real del atacante con
el lado que la víctima está bloqueando:

```gml
/// @func ataque_es_crossup(_atacante, _victima)
/// @desc ¿El atacante está, AHORA MISMO, al lado contrario de hacia dónde
///       mira la víctima? Útil para voltear el sprite del salto a media
///       animación y para que una IA sepa cuándo invertir su bloqueo.
/// @param {Id.Instance} _atacante
/// @param {Id.Instance} _victima
/// @returns {Bool}
function ataque_es_crossup(_atacante, _victima)
{
    var _atacante_a_la_derecha = (_atacante.x > _victima.x);
    var _victima_mira_derecha  = (sign(_victima.image_xscale) > 0);
    return (_atacante_a_la_derecha == _victima_mira_derecha);
}
```

> 💡 **La ambigüedad de verdad no es geométrica, es de diseño.** Qué lado cuenta como «el que hay
> que bloquear» durante el propio golpe —¿el de cuando empezó el salto? ¿el de cuando conecta la
> caja?— es una decisión que cada juego toma de forma distinta (algunos «congelan» la orientación
> del defensor al entrar en blockstun, precisamente para que el cruce se resuelva de forma
> consistente en vez de depender del fotograma exacto). `ataque_es_crossup()` te da el dato
> geométrico; la regla de CUÁNDO consultarlo la decides tú.

---

### 3.7 · Barra de súper y recursos

#### 3.7.1 · El pool, reutilizado de `04 · 36`

Igual que la guardia (§3.6.4), la barra de súper es otro `RecursoCombate` — no un sistema nuevo.
Con `_regen_por_frame = 0` es la tercera variante que `04 · 36` §1.6 ya cataloga: «un recurso
puramente "ganado"», que no sube ni baja solo, sólo por lo que el combate le mete o le saca:

```gml
// obj_jugador_lucha — Create
#macro SUPER_MAX                 100
#macro METER_POR_DANO_INFLIGIDO  0.6    // por punto de daño hecho
#macro METER_POR_DANO_RECIBIDO   0.9    // el que va perdiendo llena más rápido: ayuda a remontar
#macro METER_POR_BLOQUEO         0.5    // fijo, por cada golpe bloqueado
#macro COSTE_SUPER                100
#macro COSTE_EX                    25
#macro COSTE_GUARD_CANCEL          50

combate.barra_super = new RecursoCombate(SUPER_MAX, 0, 0);   // no regenera ni decae sola
```

#### 3.7.2 · Cómo se llena

Se engancha en `recibir_golpe()` (`04 · 30` §5.7), en los mismos puntos donde ya se resuelve el
daño y el bloqueo — añade estas líneas, no sustituyas nada:

```gml
// recibir_golpe() — al final del paso 5 "Daño", antes del paso 6:
if (variable_struct_exists(combate, "barra_super"))
{
    combate.barra_super.ganar(_dano * METER_POR_DANO_RECIBIDO);   // la víctima también llena
}
if (instance_exists(_golpe.atacante)
&&  variable_instance_exists(_golpe.atacante, "combate")
&&  variable_struct_exists(_golpe.atacante.combate, "barra_super"))
{
    _golpe.atacante.combate.barra_super.ganar(_dano * METER_POR_DANO_INFLIGIDO);
}
```

```gml
// recibir_golpe() — paso 2 "Bloqueo" (ya extendido en §3.6.4), una línea más:
if (variable_struct_exists(combate, "barra_super")) combate.barra_super.ganar(METER_POR_BLOQUEO);
```

#### 3.7.3 · En qué se gasta

**Súper**, con el propio comando de la §3.1.5:

```gml
// obj_jugador_lucha — al resolver un comando de motion (§3.1.7)
if (_nombre == "super_bola_energia" && !combate.barra_super.hay_suficiente(COSTE_SUPER))
{
    _nombre = "";   // no hay barra: el comando NO se ejecuta (ni siquiera degrada al especial)
}
if (_nombre == "super_bola_energia") combate.barra_super.gastar(COSTE_SUPER);
```

**EX / especial mejorado**: la misma motion, con un botón más fuerte o dos botones a la vez,
apunta a una entrada DISTINTA de `global.ataques_lucha` — normalmente con más daño, más cajas, o
armadura durante el arranque — a coste parcial:

```gml
global.ataques_lucha.bola_de_energia_ex = {
    // misma forma que cualquier entrada (§3.2.2): sprite, arranque, activo,
    // recuperacion, altura, grupo, cajas_por_frame — con mejores números que
    // la versión normal (más daño, más empuje, o un segundo impacto).
    dano : 14, empuje : 5.0, hitstun : 20, blockstun : 10,
    rompe_aguante : 2, rompe_guardia : 10, coste_barra : COSTE_EX
    // ...
};
```

```gml
if (combate.barra_super.hay_suficiente(COSTE_EX) && _dos_botones_a_la_vez)
{
    combate.barra_super.gastar(COSTE_EX);
    ataque_empezar("bola_de_energia_ex");
}
else
{
    ataque_empezar("bola_de_energia");
}
```

**Gasto defensivo (*guard cancel*)**: interrumpe el propio *blockstun*, empuja a los rivales
cercanos y concede una invulnerabilidad breve — rompe la presión al precio de la barra:

```gml
// obj_jugador_lucha — Step, sólo disponible DURANTE el blockstun
if (combate.blockstun > 0
&&  keyboard_check_pressed(vk_alt)
&&  combate.barra_super.hay_suficiente(COSTE_GUARD_CANCEL))
{
    combate.barra_super.gastar(COSTE_GUARD_CANCEL);
    combate.blockstun = 0;
    combate.iframes    = 12;

    with (obj_entidad)
    {
        if (equipo != other.equipo && point_distance(x, y, other.x, other.y) < 40)
        {
            vel_x += lengthdir_x(6, point_direction(other.x, other.y, x, y));
            combate.hitstun = max(combate.hitstun, 10);
        }
    }
}
```

#### 3.7.4 · Barra continua frente a *stocks*

Un diseño alternativo divide el máximo en tramos («niveles» o *stocks*) en vez de un continuo
0-100. Se representa sin cambiar `RecursoCombate`: sólo hace falta un cálculo de lectura,
`floor(actual / por_nivel)`:

```gml
/// @func barra_super_nivel(_recurso, _por_nivel)
/// @param {Struct} _recurso   Un RecursoCombate.
/// @param {Real}   _por_nivel Unidades que forman un tramo completo.
/// @returns {Real} Cuántos tramos completos hay ahora mismo.
function barra_super_nivel(_recurso, _por_nivel)
{
    return floor(_recurso.actual / _por_nivel);
}
```

---

### 3.8 · La verdad sobre el *netcode*

#### 3.8.1 · Por qué el *rollback* de verdad es muy difícil en GML

`04 · 14` §4.6 ya pone tres requisitos estrictos para el *rollback* hecho a mano (determinismo
absoluto, guardar y restaurar el estado completo cada fotograma, y que re-simular N fotogramas
quepa en el presupuesto de uno). Lo que ese documento no detalla —porque no es específico de
lucha— es **por qué el segundo requisito es una trampa concreta en GML**, no sólo trabajo:

1. **Los structs y los arrays son POR REFERENCIA**
   ([`01 · 04 §…`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md):
   «un struct es un contenedor de variables, ligero y por referencia»). Un buffer ingenuo de
   estados anteriores —`historial[i] = combate;`— no copia nada: guarda ocho veces la MISMA
   referencia al struct `EstadoCombate` que sigue mutando. Hace falta `variable_clone(valor,
   [profundidad])` (verificado: existe en el runtime) para una copia profunda de verdad, en
   **cada** struct, array y anidamiento que forme parte del estado simulable — `combate`, la
   tabla `ya_golpeados` de cada caja activa, el `historial` del `MotorComandos` de la §3.1, y
   cualquier cosa que el resultado del siguiente fotograma dependa de leer.
2. **Clonar profundo cuesta CPU**, y hay que pagarlo cada fotograma (no sólo cuando de verdad
   toca rebobinar), porque no sabes de antemano qué fotograma necesitarás restaurar. Con una
   ventana de rebobinado de 6-8 fotogramas, eso es 6-8 clonaciones profundas vivas en todo
   momento — el motivo por el que los motores de rollback serios (fuera de GameMaker) serializan
   a un `buffer` de bytes compacto en vez de clonar structs: más rápido de copiar y de comparar,
   pero mucho más trabajo de implementar (hay que escribir manualmente qué campo va en qué
   posición del buffer, sin la comodidad de `json_stringify`/`variable_clone`).
3. **La arquitectura A de `04 · 30` (instancias efímeras) es un riesgo de determinismo
   adicional** que la arquitectura B no tiene. `04 · 30` §2.1 ya explica que el orden de
   iteración de instancias dentro de un mismo evento **no está garantizado** — es exactamente
   por lo que ese documento mueve todo el combate a un único controlador en `End Step`. Para
   rollback, ese mismo problema aparece un nivel más arriba: si al re-simular un fotograma las
   instancias de `obj_hitbox` no se crean en el mismo orden relativo que la primera vez (por
   ejemplo, por un *pool* que las reutiliza de forma no determinista), cualquier lógica que
   dependa de ese orden puede divergir entre el cliente que predijo el fotograma y el que lo
   recibe confirmado. La arquitectura B de `04 · 30` §5.11 —cajas como datos puros, sin
   instancias— evita el problema de raíz: no hay orden de creación que preservar porque no hay
   instancias que crear. **Es la arquitectura recomendada de base para cualquier juego de lucha
   con aspiraciones online**, no sólo para el *frame data* con muchas cajas.
4. **Determinismo en punto flotante entre plataformas.** ⚠️ Esto no está verificado
   específicamente contra el compilador de GameMaker — es un problema documentado del punto
   flotante IEEE 754 en general, no una afirmación sobre el runtime concreto: operaciones de
   coma flotante pueden producir resultados a nivel de bit ligeramente distintos según la CPU
   (x86 frente a ARM), el nivel de optimización o el orden de evaluación del compilador. Si tu
   juego de lucha sólo se publica para una plataforma y una build, el riesgo es bajo (todos los
   clientes ejecutan literalmente el mismo binario); si cruza plataformas (PC + móvil, por
   ejemplo), es un riesgo real que sólo se descarta probándolo, no asumiéndolo.

#### 3.8.2 · El aviso que toca dar aquí, con la fecha exacta

`04 · 14` §4.6 *bis* ya documenta el sistema de *rollback* nativo del runtime (`rollback_*`, 42
símbolos) y sus tres límites reales: depende de Opera GX/GXC (no es multiplataforma), no tiene ni
un solo ejemplo de uso real en los repositorios descargados, y —el que importa aquí— **fue
retirado del `GmlSpec` en la Beta 2026.100 R2**. La cita exacta, verificada en
[`02 · Novedades 2026/01 — Resumen LTS 2026.0`](../02%20-%20Novedades%202026/01%20-%20Resumen%20LTS%202026.0.md):

> «**Eliminado GmlSpec Rollback** (R2): la funcionalidad de rollback multiplayer desaparece. Si
> tu juego lo usa, **quédate en 2026.0** hasta tener alternativa.»

Para un juego de lucha, la lectura es directa: `rollback_*` es una capacidad de **esta LTS
2026.0 concreta**, ligada además a una sola plataforma (Opera GX). Apostar el *netcode* entero de
un juego de lucha a esa API es apostar a una superficie que el propio fabricante ya ha empezado a
retirar en su rama Beta. Si aun así quieres probarlo sabiendo esto, el flujo mínimo y sus
símbolos verificados están en `04 · 14` §4.6 *bis* — no se repiten aquí.

#### 3.8.3 · Qué alternativas quedan

| Alternativa | Cuándo tiene sentido | Coste |
|---|---|---|
| **Local / *splitscreen*** primero | Siempre, como primer paso — `04 · 14` §8 «Antes de empezar, en serio» ya lo recomienda para CUALQUIER juego online, y en lucha es doblemente cierto: separa la lógica de combate del problema de red antes de mezclar los dos | Ninguno — es trabajo que hay que hacer de todas formas |
| **Autoridad del servidor + *delay* fijo generoso** | Un primer juego de lucha online, sin *rollback* de ningún tipo: se acepta un retraso de entrada constante (4-8 fotogramas) a cambio de simplicidad y de no necesitar re-simulación ni clonado de estado | Bajo — es la misma arquitectura de `04 · 14` §4.1-§4.4, sin el paso extra de predecir al rival |
| ***Lockstep* determinista** | La fila de la propia tabla de `04 · 14` §4.1 ya lo señala para «lucha con rollback» — todos los clientes simulan el mismo estado a partir de los mismos inputs, sin sincronizar posiciones; sigue exigiendo el determinismo absoluto de la §3.8.1, pero NO exige rebobinar ni clonar nada, porque nunca hay una predicción que corregir | Medio — hay que esperar al cliente más lento, y el determinismo sigue siendo un requisito de hierro |
| ***Rollback* DIY** (`04 · 14` §4.6) | Sólo si el juego ya usa la arquitectura B en su totalidad (§3.8.1, punto 3) y el equipo puede dedicarle tiempo real | Alto — es un proyecto dentro del proyecto |
| **`rollback_*` nativo** (`04 · 14` §4.6 *bis*) | Sólo si el juego se compromete con Opera GX/GXC como plataforma y se acepta el riesgo de la §3.8.2 | Bajo en código, alto en riesgo de plataforma |

**La referencia para estudiar esto en GML, ya catalogada en esta biblioteca**: *Gang Garrison 2*
(MPL 2.0, 119 ★) es, según
[`07 · Ecosistema/04`](../07%20-%20Ecosistema/04%20-%20Proyectos%20de%20ejemplo%20para%20estudiar.md),
«el mejor repo de GameMaker para aprender netcode»: implementa *rollback*, predicción del
cliente, sincronización de entidades y compensación de *lag* en GML real, con 9 clases que se
pueden leer enteras. No es un juego de lucha 1v1, pero es *rollback* de verdad, escrito en el
mismo lenguaje que vas a usar — el ejemplo más cercano que existe, y
[`07 · Ecosistema/03`](../07%20-%20Ecosistema/03%20-%20Extensiones%20oficiales%20y%20de%20terceros.md)
ya deja dicho que **GGPO no existe para GameMaker**: no hay atajo de extensión que sustituya a
leer ese código.

---

## 4 · Checklist

- [ ] `04 · 30` entero, leído — este documento no repite cajas, hurtbox, controlador único,
      hit stop ni combos básicos.
- [ ] El motor de comandos (§3.1) tolera huecos y diagonales saltadas — probado con mando Y con
      teclado, no sólo uno de los dos.
- [ ] Los comandos que comparten prefijo (especial/súper) están ordenados de más largo a más
      corto en `global.comandos_jugador` (§3.1.5).
- [ ] La tabla de *frame data* vive en un struct plano (`global.ataques_lucha`), con
      `cajas_por_frame` indexado por fotograma, no una caja fija (§3.2).
- [ ] La tabla de *gatling* (§3.3) clasifica cada movimiento por grupo — no hay una lista
      `cancela_a` escrita a mano por cada uno de los 20+ movimientos del elenco.
- [ ] `ESCALADO_HITSTUN` existe y se aplica, no sólo `ESCALADO_COMBO` — si sólo escalas daño, el
      juego tiene un infinito esperando a que alguien lo descubra (§3.4.1).
- [ ] El *pushback* al bloquear es MAYOR que al golpear, y crece con la repetición (§3.4.3).
- [ ] El agarre NO lleva armadura durante su arranque — «golpe bate a agarre» sale de eso, no de
      código nuevo (§3.5.1).
- [ ] Hay una ventana de *tech* real tras el agarre, no un agarre inescapable (§3.5.3).
- [ ] La invulnerabilidad de despertar existe y tiene un valor que un jugador puede aprender a
      explotar exactamente (`meaty_margen()`, §3.6.2).
- [ ] La guardia distingue alta/baja (§3.6.3) y se puede romper (§3.6.4) — bloquear no es gratis.
- [ ] La barra de súper se llena en más de un sitio (golpear, ser golpeado, bloquear) y se gasta
      en más de uno (súper, EX, defensa) — §3.7.
- [ ] Si el juego va a jugarse en línea: se ha leído la §3.8 entera, no sólo la tabla de
      alternativas — y se sabe con los ojos abiertos a qué se está apostando.

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Reimplementar la hitbox/hurtbox de `04 · 30` «a la medida» del juego de lucha | Divergencia entre este documento y `04 · 30`; el doble de código para el mismo problema | Usa `04 · 30` §5.11 (arquitectura B) tal cual y extiéndela con `cajas_por_frame` (§3.2) |
| Exigir la secuencia numpad EXACTA, sin conjuntos de tolerancia | Los comandos «fallan» constantemente con mando o teclado; se siente roto aunque el código sea correcto | Cada paso del patrón es un CONJUNTO de dígitos aceptables, no uno solo (§3.1.4) |
| Comprobar el especial corto ANTES que el súper largo | El súper nunca sale — el especial se dispara primero y consume el comando | Ordena `global.comandos_jugador` de más largo a más corto (§3.1.5) |
| Negative edge también en los botones sueltos | Un golpe ligero sale DOS veces por cada pulsación (al bajar y al soltar el dedo) | Negative edge sólo en el resolver de comandos de motion, nunca en el buffer de botones simples (§3.1.7) |
| Escalar sólo el daño del combo | El combo no duele mucho, pero no termina NUNCA — un softlock encubierto | Escala también el hitstun (`ESCALADO_HITSTUN`, §3.4.2): tarde o temprano rompe la desigualdad de la §3.4.1 |
| Pushback igual al golpear que al bloquear | El atacante se puede plantar pegado y presionar para siempre sin arriesgar nada | El bloqueo empuja MÁS (`PUSHBACK_CRECE_BLOQUEO > PUSHBACK_CRECE_GOLPE`, §3.4.3) |
| Dar armadura al agarre «para que no lo puedan interrumpir» | El triángulo golpe/agarre/bloqueo se rompe: el agarre pasa a ganarlo todo | El arranque del agarre usa la hurtbox NORMAL — un golpe lo interrumpe igual que a cualquier ataque (§3.5.1) |
| Agarre sin ventana de escape | Bloquear deja de tener sentido: el rival agarra y no hay nada que hacer | `AGARRE_VENTANA_TECH` (§3.5.3) — el mismo botón del agarre lo escapa si se pulsa a tiempo |
| Guardia infinita, sin recurso que la limite | Un jugador puede bloquear literalmente para siempre sin ningún riesgo | `combate.guardia` como `RecursoCombate` de `04 · 36`, con *guard crush* al llegar a cero (§3.6.4) |
| Barra de súper que sólo se llena golpeando | El jugador que va perdiendo nunca tiene recursos para remontar | `METER_POR_DANO_RECIBIDO` mayor que `METER_POR_DANO_INFLIGIDO` (§3.7.2) |
| Diseñar el *netcode* alrededor de `rollback_*` sin leer sus límites | El proyecto queda atado a Opera GX/GXC y a una API que YoYo ya retiró de la Beta | Lee `04 · 14` §4.6 *bis* Y la §3.8.2 de este documento ANTES de comprometerte |
| Asumir que `variable_clone()` es gratis en un bucle de rollback | El juego cae de fps al activar rollback, sólo se nota con varios jugadores online | Perfílalo desde el primer prototipo de rollback — clonar profundo tiene coste real (§3.8.1) |

---

## Ver también

- [04 · 30 — Combate cuerpo a cuerpo](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) —
  **la base entera de este documento**: hitbox/hurtbox/máscara, *frame data*, el controlador
  único en `End Step`, combos con cancels, i-frames, parry, poise, multi-hit.
- [04 · 15 — Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) — *hit stop*, sacudida de
  cámara, empuje base y `hit_complete()`: toda la sensación del golpe vive ahí, no aquí.
- [04 · 14 — Multijugador](./14%20-%20Multijugador.md) §4.1-§4.7 — autoridad del servidor,
  predicción, interpolación, compensación de *lag*; §4.6 y §4.6 *bis* — *rollback* DIY y nativo.
- [04 · 36 — Habilidades, enfriamientos y recursos de combate](./36%20-%20Habilidades%2C%20enfriamientos%20y%20recursos%20de%20combate.md) §3.2 —
  `RecursoCombate`, reutilizado aquí para la guardia (§3.6.4) y la barra de súper (§3.7).
- [04 · 46 — Eje Z falso](./46%20-%20Eje%20Z%20falso%20-%20altura%2C%20sombras%20y%20profundidad%20en%20un%20juego%202D.md) —
  por qué un juego de lucha en vista lateral NO lo necesita (§1.2 de este documento).
- [04 · 47 — Beat 'em up y brawler](./47%20-%20Beat%20em%20up%20y%20brawler.md) §6 — el agarre más
  simple, sin *tech*, del que el de este documento (§3.5) es una versión más exigente.
- [04 · 01 — Plataformas 2D](./01%20-%20Plataformas%202D.md) — gravedad, salto y máquina de
  estados: la base del movimiento vertical que un juego de lucha en vista lateral sí usa.
- [01 · 04 — Structs y constructores (POO en GML)](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) —
  por qué structs y arrays son por referencia, la base técnica de la §3.8.1.
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) —
  guardar la tabla de *frame data* en JSON y editarla sin recompilar (§3.2.4).
- [02 · Novedades 2026/01 — Resumen LTS 2026.0](../02%20-%20Novedades%202026/01%20-%20Resumen%20LTS%202026.0.md) —
  la cita exacta de la retirada de `rollback_*` en la Beta 2026.100 R2 (§3.8.2).
- [07 · Ecosistema/03 — Extensiones oficiales y de terceros](../07%20-%20Ecosistema/03%20-%20Extensiones%20oficiales%20y%20de%20terceros.md) —
  «GGPO no existe para GM» (§3.8.3).
- [07 · Ecosistema/04 — Proyectos de ejemplo para estudiar](../07%20-%20Ecosistema/04%20-%20Proyectos%20de%20ejemplo%20para%20estudiar.md) —
  *Gang Garrison 2*, la mejor referencia de *netcode* real en GML (§3.8.3).
- [06 · `scr_input_buffer.gml`](../06%20-%20Assets%20y%20Scripts/scr_input_buffer.gml) —
  `InputBuffer`, que el motor de comandos de la §3.1 complementa sin sustituir.
- [06 · `scr_state_machine.gml`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) —
  `fsm_bind()`, la misma máquina de estados de `04 · 30` que este documento sigue usando.

---

## Fuentes

**Vocabulario específico de lucha** (`04 · 30` ya cita Infil y Dustloop para el vocabulario base;
estas son las entradas nuevas que le faltaban, consultadas en vivo el **2026-09-07** con
`curl -sL -A "Mozilla/5.0…"` porque `glossary.infil.net` es una SPA que no entrega contenido sin
JavaScript — el propio Dustloop reproduce las definiciones de Infil con su enlace de origen, así
que se cita la página que sí se pudo leer):

- **Dustloop Wiki — Glossary** — *Negative Edge*, *Charge Input*, *Command Throw*, *Tech*, *Chip
  Damage*, *Okizeme*, *Meaty*, *Cross-up*, *Reversal*, *Frame Trap*, *RPS* —
  https://www.dustloop.com/w/Glossary
- **Dustloop Wiki — Notation** — la notación numpad completa (1-9, corchetes para carga,
  `>`/`~` para enlaces y cancels): base de la §3.1.2 y de los comandos de ejemplo de este
  documento — https://www.dustloop.com/w/Notation
- **The Fighting Game Glossary**, Infil — fuente original de las definiciones que Dustloop
  reproduce con enlace directo (`?t=Negative%20Edge`, `?t=Tech`, etc.) —
  https://glossary.infil.net/

**Runtime y biblioteca interna**, verificadas con `python3 "_indice/buscar.py" <símbolo>`:

- `gamepad_button_check`, `gamepad_button_check_pressed`, `gamepad_button_check_released`,
  `gamepad_axis_value`, `gp_padu`/`gp_padd`/`gp_padl`/`gp_padr`, `gp_face1` — Manual oficial,
  `09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Game_Input/GamePad_Input/`.
- `array_push`, `array_shift`, `array_length`, `array_contains`, `variable_clone` — Manual
  oficial, `09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Variable_Functions/`.
- `variable_struct_exists`, `variable_instance_exists`, `is_undefined` — ídem.
- `collision_rectangle_list`, `instance_place`, `point_distance`, `point_direction` —
  ya verificadas y citadas en `04 · 30` §9; reutilizadas aquí sin cambiar de firma.
- **Structs y arrays son por referencia** —
  [`01 · 04 — Structs y constructores`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md)
  §"Structs vs instancias", base técnica de la §3.8.1 de este documento.
- **Eliminación de `rollback_*` en la Beta 2026.100 R2** —
  [`02 - Novedades 2026/01 — Resumen LTS 2026.0`](../02%20-%20Novedades%202026/01%20-%20Resumen%20LTS%202026.0.md),
  cita textual verificada por `grep` directo sobre el documento el 2026-09-07.
- **«GGPO no existe para GM» y *Gang Garrison 2*** —
  [`07 - Ecosistema/03`](../07%20-%20Ecosistema/03%20-%20Extensiones%20oficiales%20y%20de%20terceros.md)
  y [`07 - Ecosistema/04`](../07%20-%20Ecosistema/04%20-%20Proyectos%20de%20ejemplo%20para%20estudiar.md),
  ambas ya investigadas y catalogadas por esta biblioteca.

> ⚠️ **Lo que NO está verificado en este documento.** Todos los símbolos de GML existen en el
> runtime 2026.0.0.23 (comprobados con `buscar.py`), pero el código **no se ha compilado en un
> proyecto real**: los nombres de sprites y sonidos (`spr_medio_arco`, `snd_guard_crush`…) son
> marcadores de posición. Los **números de frame data, ventanas de comando y costes de barra**
> son puntos de partida razonables para el género, **no medidas de ningún juego concreto** —
> cualquier cifra de un juego real citada en este documento lleva su fuente y su fecha al lado;
> donde no la lleva, es un valor de diseño de esta biblioteca, ajustable jugando. El determinismo
> del punto flotante entre plataformas (§3.8.1, punto 4) es conocimiento general del formato
> IEEE 754, no una medición hecha contra el compilador de GameMaker.
