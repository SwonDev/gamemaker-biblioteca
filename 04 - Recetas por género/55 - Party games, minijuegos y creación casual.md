# 55 · Party games, minijuegos y creación casual

> Dos géneros que no se parecen entre sí más que en el nombre de la carpeta: una **colección de
> minijuegos rotativos** al estilo *WarioWare* (docenas de reglas distintas en sesiones de
> segundos) y un **secuenciador musical de creación**, donde el jugador compone en vez de
> escuchar. Cubre el orquestador que hace rotar los minijuegos y la rejilla de pasos que hace
> componer. **No cubre** un solo juego de un botón continuo — eso es
> [04 · 11](./11%20-%20Arcade%20y%20juegos%20de%20un%20botón.md) — ni **reproducir** un
> patrón rítmico ya compuesto por el diseñador — eso es
> [04 · 19](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md).
> Cierra con dos menciones honestas de una frase: *typing games* y juegos de dibujar.

---

## 1 · Visión general

**Lo que define a un party game de minijuegos:**

- Reglas explicables en **una frase**, distinta cada pocos segundos: "¡ESQUIVA!", "¡CUENTA!",
  "¡NO TOQUES!".
- Un **input que cambia** de minijuego a minijuego (a veces un botón, a veces las flechas, a
  veces el ratón) — al contrario que el arcade de 04 · 11, donde el input es fijo toda la
  partida.
- Una **regla de tiempo compartida**: todas las rondas duran lo mismo (o casi), así el jugador
  interioriza el ritmo de "instrucción → juega → resultado" aunque no sepa qué le va a tocar.
- Sesiones brutalmente cortas. Según la Wikipedia en inglés, en la serie *WarioWare* cada
  microjuego dura entre tres y cinco segundos y el jugador empieza con cuatro vidas; la unidad
  de tiempo interna no son segundos sino **beats**, y el BPM (y con él la dificultad) sube según
  se completan microjuegos (⚠️ fuente secundaria, ver [Fuentes](#fuentes)).

**Por qué esto no es una variación de 04 · 11.** Léelo primero — al menos su
[§1 Visión general y §2 Arquitectura](./11%20-%20Arcade%20y%20juegos%20de%20un%20botón.md#1-visión-general).
Ese documento construye **un** juego continuo: un jugador, un input fijo, una dificultad que
sube sin interrupción. Aquí el problema es distinto: **rotar entre docenas de minijuegos con
reglas, objetos y hasta esquemas de input diferentes**, sin que el código de cada uno sepa nada
de los demás ni del que viene después. Eso exige una pieza que 04 · 11 no tiene ni necesita: un
**orquestador** que carga, ejecuta y desecha minijuegos por turnos según un contrato común. Lo
que SÍ es directamente reutilizable de 04 · 11 es su **contenido**: cualquier minijuego de un
solo botón (saltar, esquivar, un *near miss*) encaja perfecto como uno de los "cartuchos" que
rota el orquestador — de hecho el cartucho de ejemplo de §2.6 es exactamente eso, en miniatura.

---

## 2 · Orquestador de colección de minijuegos (WarioWare-style)

### 2.1 · El contrato mínimo de un minijuego

Cualquier "cartucho" que quieras rotar debe ser un **struct** que implemente exactamente estas
cinco funciones. El orquestador no conoce ni le importa qué hay dentro: solo llama a estas
cinco en el orden fijo de su máquina de fases.

| Función | Cuándo la llama el orquestador | Responsabilidad |
|---|---|---|
| `iniciar()` | Una vez, al empezar la fase de instrucción | Poner el minijuego en su estado inicial: posiciones, contadores, objetivo |
| `step()` | Cada Step, mientras dura la fase de juego | Leer input, mover, comprobar condiciones — nunca dibujar |
| `dibujar()` | Cada Draw GUI, mientras dura la fase de juego y de resultado | Solo dibujar; nunca leer input ni cambiar estado |
| `ha_terminado()` | Cada Step, después de `step()` | Devuelve `true` si el minijuego ya decidió su desenlace ANTES de que se acabe el tiempo |
| `gano_el_jugador()` | Una vez, al cerrar la ronda (por `ha_terminado()` o por tiempo agotado) | Devuelve `true`/`false`. Se pregunta SIEMPRE, gane quien gane el reloj |

> 💡 **`gano_el_jugador()` decide su propio valor por defecto.** Un minijuego de "sobrevive sin
> tocar el pincho" debe empezar asumiendo victoria (`true`) y solo poner `false` cuando el
> jugador falla; un minijuego de "recoge 3 monedas" debe empezar asumiendo derrota (`false`) y
> solo poner `true` cuando se cumple el objetivo. El orquestador no sabe cuál de los dos es tu
> minijuego — por eso la pregunta se hace siempre al final, nunca se asume.

### 2.2 · La regla de tiempo compartida

Todas las rondas se rigen por el mismo reloj de frames, y ese reloj se acorta con cada ronda
superada — así el juego acelera igual que describe la Wikipedia sobre el BPM creciente de
*WarioWare* (⚠️ fuente secundaria), sin que cada minijuego tenga que implementar su propia
curva de dificultad.

```gml
#macro RONDA_SEGUNDOS_BASE     5      // duración de una ronda al empezar la partida
#macro RONDA_SEGUNDOS_MINIMO   2      // el suelo: nunca menos de esto, por rápido que vayas
#macro RONDA_SEGUNDOS_MERMA    0.15   // cuánto se acorta la ronda por cada ronda superada
#macro INSTRUCCION_SEGUNDOS    1.2    // "¡SALTA!" en pantalla antes de que empiece a contar
#macro RESULTADO_SEGUNDOS      0.8    // "¡BIEN!" / "FALLASTE" antes de la siguiente ronda
#macro VIDAS_INICIALES         4      // igual que WarioWare — ver Fuentes
```

El jugador ve y **oye** el mismo reloj en cada ronda: una barra que se vacía (el "fusible" que
describe la Wikipedia sobre *WarioWare*, ⚠️) y un tic por cada segundo que pasa, sea cual sea el
minijuego. Eso es lo que hace que el ritmo se aprenda aunque las reglas cambien constantemente.

### 2.3 · El catálogo como datos

El catálogo de minijuegos es un **array de structs**, no una cadena de `if`/`switch` gigante:
mismo principio de "estructuras como datos" que ya usan
[04 · 36 §3.1](./36%20-%20Habilidades,%20enfriamientos%20y%20recursos%20de%20combate.md#31-el-struct-de-habilidad-dirigido-por-datos)
para las habilidades y
[04 · 44 §1.5.0](./44%20-%20Bullet%20heaven%2C%20autobattler%20y%20deckbuilder.md#150--catálogo-de-armas-y-struct-de-estado)
para las armas — no se repite su código aquí, solo el patrón. La diferencia es que este catálogo
no guarda solo datos planos: guarda además **la función que instancia cada cartucho**, siguiendo
el mismo mecanismo que
[04 · 16](./16%20-%20Señales%20y%20desacoplamiento.md) usa para guardar un callback dentro
de un struct (`callback: method(_duena, _callback)`, invocado después como `_o.callback(...)`):
una función es un valor como cualquier otro, y un campo de struct puede guardarla y llamarla.

```gml
// ---------------------------------------------------------------------------
// scr_catalogo_microjuegos — datos. Añadir un minijuego nuevo es añadir una
// entrada aquí; el orquestador no cambia una sola línea.
// ---------------------------------------------------------------------------

function crear_esquiva()   { return new MicrojuegoEsquiva();   }
function crear_recolecta() { return new MicrojuegoRecolecta(); }

global.catalogo_microjuegos = [
    { instruccion: "¡SALTA!",     crear: crear_esquiva   },
    { instruccion: "¡RECOGE 3!",  crear: crear_recolecta },
];
```

> 🔺 **`crear` guarda la función, no el resultado de llamarla.** `crear_esquiva` sin paréntesis
> es una referencia; `crear_esquiva()` ya sería un `MicrojuegoEsquiva` construido de más. El
> orquestador decide CUÁNDO instanciarlo (justo antes de cada ronda), no el catálogo.

### 2.4 · Máquina de fases del orquestador

```gml
enum FaseRonda
{
    INSTRUCCION,   // muestra la frase, el minijuego ya existe pero no corre step()
    JUGANDO,       // step() y dibujar() cada frame, el reloj compartido cuenta atrás
    RESULTADO      // "¡BIEN!" / "FALLASTE", el minijuego se sigue dibujando de fondo
}
```

```
INSTRUCCION ──(frames_restantes <= 0)──▶ JUGANDO
JUGANDO ──(ha_terminado() o frames_restantes <= 0)──▶ RESULTADO
RESULTADO ──(frames_restantes <= 0, quedan vidas)──▶ INSTRUCCION (nueva ronda)
RESULTADO ──(frames_restantes <= 0, vidas <= 0)────▶ fin de partida
```

### 2.5 · Código base completo

```gml
// ---------------------------------------------------------------------------
// obj_orquestador_microjuegos · Create
// ---------------------------------------------------------------------------

#macro ARENA_X       30
#macro ARENA_Y        30
#macro ARENA_ANCHO   260
#macro ARENA_ALTO    180

fase                  = FaseRonda.INSTRUCCION;
frames_restantes      = 0;
duracion_ronda_frames = 0;
segundo_anterior      = -1;

vidas             = VIDAS_INICIALES;
rondas_superadas  = 0;
puntos_totales    = 0;
gano_la_ronda     = false;

indice_anterior    = -1;
instruccion_actual = "";
microjuego_actual  = undefined;

function preparar_siguiente_ronda()
{
    var _total = array_length(global.catalogo_microjuegos);
    var _indice;
    do
    {
        _indice = irandom(_total - 1);
    }
    until (_indice != indice_anterior || _total == 1);   // no repetir el cartucho anterior
    indice_anterior = _indice;

    var _entrada       = global.catalogo_microjuegos[_indice];
    instruccion_actual = _entrada.instruccion;
    microjuego_actual  = _entrada.crear();
    microjuego_actual.iniciar();

    var _segundos = max(RONDA_SEGUNDOS_MINIMO,
                         RONDA_SEGUNDOS_BASE - (rondas_superadas * RONDA_SEGUNDOS_MERMA));
    duracion_ronda_frames = round(_segundos * game_get_speed(gamespeed_fps));

    fase             = FaseRonda.INSTRUCCION;
    frames_restantes = round(INSTRUCCION_SEGUNDOS * game_get_speed(gamespeed_fps));
    segundo_anterior = -1;
}

preparar_siguiente_ronda();   // arranca la primera ronda nada más crear el objeto
```

```gml
// ---------------------------------------------------------------------------
// obj_orquestador_microjuegos · Step
// ---------------------------------------------------------------------------

frames_restantes--;

switch (fase)
{
    case FaseRonda.INSTRUCCION:
        if (frames_restantes <= 0)
        {
            fase             = FaseRonda.JUGANDO;
            frames_restantes = duracion_ronda_frames;
            segundo_anterior = -1;
        }
    break;

    case FaseRonda.JUGANDO:
        microjuego_actual.step();

        // el reloj compartido: mismo tic para cualquier minijuego (§2.2)
        var _segundo_actual = ceil(frames_restantes / game_get_speed(gamespeed_fps));
        if (_segundo_actual != segundo_anterior)
        {
            segundo_anterior = _segundo_actual;
            audio_play_sound(snd_tic_reloj, 5, false);   // sustituye por tu propio SFX
        }

        if (microjuego_actual.ha_terminado() || frames_restantes <= 0)
        {
            gano_la_ronda = microjuego_actual.gano_el_jugador();

            if (gano_la_ronda)
            {
                rondas_superadas++;
                puntos_totales += 100;
            }
            else
            {
                vidas--;
            }

            fase             = FaseRonda.RESULTADO;
            frames_restantes = round(RESULTADO_SEGUNDOS * game_get_speed(gamespeed_fps));
        }
    break;

    case FaseRonda.RESULTADO:
        if (frames_restantes <= 0)
        {
            if (vidas <= 0)
            {
                // fin de partida — el proyecto decide qué hacer aquí
                // (room_goto(rm_game_over), mostrar puntos_totales, etc.)
            }
            else
            {
                preparar_siguiente_ronda();
            }
        }
    break;
}
```

```gml
// ---------------------------------------------------------------------------
// obj_orquestador_microjuegos · Draw GUI
// ---------------------------------------------------------------------------

draw_set_font(fnt_orquestador);   // sustituye por tu propia fuente
draw_set_halign(fa_center);
draw_set_valign(fa_middle);

switch (fase)
{
    case FaseRonda.INSTRUCCION:
        draw_text(ARENA_X + ARENA_ANCHO / 2, ARENA_Y + ARENA_ALTO / 2, instruccion_actual);
    break;

    case FaseRonda.JUGANDO:
        microjuego_actual.dibujar();

        // la barra de tiempo compartida — el mismo "fusible" en cada minijuego
        var _fraccion = clamp(frames_restantes / duracion_ronda_frames, 0, 1);
        draw_set_color(_fraccion < 0.25 ? c_red : c_lime);
        draw_rectangle(ARENA_X, ARENA_Y - 10, ARENA_X + ARENA_ANCHO * _fraccion, ARENA_Y - 4, false);
        draw_set_color(c_white);
    break;

    case FaseRonda.RESULTADO:
        microjuego_actual.dibujar();
        draw_text(ARENA_X + ARENA_ANCHO / 2, ARENA_Y + ARENA_ALTO / 2,
                   gano_la_ronda ? "¡BIEN!" : "FALLASTE");
    break;
}

draw_set_halign(fa_left);
draw_set_valign(fa_top);
draw_text(8, 8, $"VIDAS {vidas}   RONDA {rondas_superadas}   PUNTOS {puntos_totales}");
```

> ⚠️ **`snd_tic_reloj` y `fnt_orquestador` son assets que tienes que crear tú.** No son símbolos
> del runtime: son nombres de recursos de proyecto, con el mismo criterio de la biblioteca de
> usar `snd_`/`fnt_` como prefijo (05 · 04).

### 2.6 · Cartuchos de ejemplo

Dos minijuegos completos que cumplen el contrato de §2.1. Dibujan con coordenadas relativas al
área definida por `ARENA_X`/`ARENA_Y` en §2.5 y no dependen de instancias de GameMaker: son
structs autocontenidos, así que caben en una sola ronda sin dejar nada que limpiar.

**Cartucho de un botón — reutiliza la idea de 04 · 11.** `MicrojuegoEsquiva` es literalmente el
patrón de
["4.1 · Un botón, muchas acciones"](./11%20-%20Arcade%20y%20juegos%20de%20un%20botón.md#41-un-botón-muchas-acciones)
comprimido en una sola ronda: un salto con gravedad, un obstáculo que se acerca, y una condición
de choque manual (sin `place_meeting` ni sprites: el minijuego es tan pequeño que dos
rectángulos calculados a mano bastan).

```gml
// ---------------------------------------------------------------------------
// scr_microjuego_esquiva
// ---------------------------------------------------------------------------

/// @func MicrojuegoEsquiva()
/// @desc Salta con un botón para esquivar el obstáculo que se acerca por el suelo.
function MicrojuegoEsquiva() constructor
{
    suelo_y         = ARENA_Y + 140;
    jugador_x       = ARENA_X + 40;
    jugador_y       = suelo_y;
    velocidad_y     = 0;
    fuerza_salto    = -6;
    gravedad        = 0.35;
    en_el_suelo     = true;

    obstaculo_x     = ARENA_X + ARENA_ANCHO;
    obstaculo_ancho = 14;
    obstaculo_alto  = 20;
    obstaculo_vel   = 4.5;

    choco           = false;

    iniciar = function()
    {
        jugador_y   = suelo_y;
        velocidad_y = 0;
        en_el_suelo = true;
        obstaculo_x = ARENA_X + ARENA_ANCHO;
        choco       = false;
    }

    step = function()
    {
        if (keyboard_check_pressed(vk_space) && en_el_suelo)
        {
            velocidad_y = fuerza_salto;
            en_el_suelo = false;
        }

        if (!en_el_suelo)
        {
            velocidad_y += gravedad;
            jugador_y    += velocidad_y;
            if (jugador_y >= suelo_y)
            {
                jugador_y   = suelo_y;
                velocidad_y = 0;
                en_el_suelo = true;
            }
        }

        obstaculo_x -= obstaculo_vel;

        // colisión manual: dos rectángulos, sin instancias ni máscaras
        var _choca_x = (obstaculo_x < jugador_x + 8) && (obstaculo_x + obstaculo_ancho > jugador_x - 8);
        var _choca_y = (jugador_y - 16 < suelo_y) && (jugador_y > suelo_y - obstaculo_alto);
        if (_choca_x && _choca_y) choco = true;
    }

    dibujar = function()
    {
        draw_line(ARENA_X, suelo_y, ARENA_X + ARENA_ANCHO, suelo_y);
        draw_rectangle(jugador_x - 8, jugador_y - 16, jugador_x + 8, jugador_y, false);
        draw_rectangle(obstaculo_x, suelo_y - obstaculo_alto, obstaculo_x + obstaculo_ancho, suelo_y, false);
    }

    ha_terminado = function()
    {
        return choco || (obstaculo_x < ARENA_X - obstaculo_ancho);
    }

    gano_el_jugador = function()
    {
        return !choco;   // "sobrevive": gana por defecto, salvo que choque
    }
}
```

**Cartucho de objetivo activo — recoger antes de que se acabe el tiempo.** Al contrario que el
anterior, este empieza asumiendo derrota: solo gana si el jugador cumple el objetivo a tiempo.

```gml
// ---------------------------------------------------------------------------
// scr_microjuego_recolecta
// ---------------------------------------------------------------------------

/// @func MicrojuegoRecolecta()
/// @desc Muévete con las flechas y recoge las 3 monedas antes de que acabe la ronda.
function MicrojuegoRecolecta() constructor
{
    jugador_x = ARENA_X + ARENA_ANCHO / 2;
    jugador_y = ARENA_Y + ARENA_ALTO / 2;
    velocidad = 2.6;

    objetivo   = 3;
    recogidas  = 0;
    monedas    = [];

    iniciar = function()
    {
        jugador_x = ARENA_X + ARENA_ANCHO / 2;
        jugador_y = ARENA_Y + ARENA_ALTO / 2;
        recogidas = 0;
        monedas   = [];

        for (var _i = 0; _i < objetivo; _i++)
        {
            array_push(monedas, {
                px: irandom_range(ARENA_X + 15, ARENA_X + ARENA_ANCHO - 15),
                py: irandom_range(ARENA_Y + 15, ARENA_Y + ARENA_ALTO - 15),
                recogida: false
            });
        }
    }

    step = function()
    {
        if (keyboard_check(vk_left))  jugador_x -= velocidad;
        if (keyboard_check(vk_right)) jugador_x += velocidad;
        if (keyboard_check(vk_up))    jugador_y -= velocidad;
        if (keyboard_check(vk_down))  jugador_y += velocidad;

        for (var _i = 0; _i < array_length(monedas); _i++)
        {
            var _m = monedas[_i];
            if (!_m.recogida && point_distance(jugador_x, jugador_y, _m.px, _m.py) < 12)
            {
                _m.recogida = true;
                recogidas++;
            }
        }
    }

    dibujar = function()
    {
        draw_rectangle(jugador_x - 6, jugador_y - 6, jugador_x + 6, jugador_y + 6, false);
        for (var _i = 0; _i < array_length(monedas); _i++)
        {
            var _m = monedas[_i];
            if (!_m.recogida) draw_circle(_m.px, _m.py, 5, false);
        }
    }

    ha_terminado = function()
    {
        return recogidas >= objetivo;   // termina en cuanto se cumple el objetivo, no espera al reloj
    }

    gano_el_jugador = function()
    {
        return recogidas >= objetivo;   // "cumple el objetivo": pierde por defecto
    }
}
```

Un tercer cartucho, un cuarto, un vigésimo — se añaden igual: un struct nuevo con las mismas
cinco funciones y una entrada nueva en `global.catalogo_microjuegos` (§2.3). El orquestador no
se entera de que existen hasta que le toca sortearlos.

### 2.7 · Errores clásicos y cómo evitarlos

| Error | Qué pasa |
|---|---|
| Un `if (indice == 0) ... else if (indice == 1) ...` en vez del catálogo de §2.3 | Añadir el minijuego 21 obliga a tocar el orquestador. El catálogo existe para que no haga falta |
| Leer input dentro de `dibujar()` | Rompe la separación lógica/render; si algún día divides Step y Draw en hilos o frames distintos, el input se lee tarde o dos veces |
| No resetear estado en `iniciar()`, solo en el constructor | El cartucho se reutiliza (mismo struct, otra ronda) y arrastra el estado de la ronda anterior |
| Que `gano_el_jugador()` dependa de variables que solo existen si `ha_terminado()` fue `true` | Se llama SIEMPRE al cerrar la ronda, también cuando corta el reloj compartido, no el minijuego |
| Reloj de ronda propio por minijuego, en vez del `frames_restantes` del orquestador (§2.2) | El jugador deja de sentir el ritmo compartido — la gracia del género se pierde |
| Repetir el mismo cartucho dos rondas seguidas | `preparar_siguiente_ronda()` en §2.5 evita el `indice_anterior`; sin ese descarte, `irandom` puede repetir |

---

## 3 · Secuenciador musical de creación (*step sequencer*)

### 3.1 · Qué lo diferencia de 04 · 19

[04 · 19](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md) resuelve
**consumir** un patrón que el diseñador ya escribió: su
["5 · Colocar los eventos: el mapa de la canción"](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md#5--colocar-los-eventos-el-mapa-de-la-canción)
lee un array de notas fijas (`patron = [{ beat: 0, tipo: "izquierda" }, ...]`) escrito antes de
compilar. Aquí el patrón **no existe hasta que el jugador lo crea**, celda a celda, en tiempo
real. Es la misma clase de problema (algo tiene que ocurrir en el beat exacto) resuelta al
revés: el dato de "qué suena en qué beat" no viene de un array fijo, sino de una rejilla que el
jugador enciende y apaga con el ratón.

**El reloj se reutiliza tal cual, sin tocarlo.** El
["1 · El conductor"](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md#1--el-conductor)
de 04 · 19 define `obj_conductor`, con `conductor_arrancar(_sonido, _bpm, _offset)` y una señal
`"beat"` que emite `{ n: beat_actual, compas: beat_actual div 4 }` cada vez que se cruza un beat
entero — verificado leyendo el documento, no supuesto. El secuenciador de esta sección se limita
a **escuchar esa misma señal** con el sistema de
[04 · 16](./16%20-%20Señales%20y%20desacoplamiento.md) (`senal_escuchar("beat", ...)`) y a
avanzar una columna por cada beat que llega. Ni una línea de `obj_conductor` se reescribe.

### 3.2 · La rejilla como datos

Filas = sonidos, columnas = tiempo. Un *array de arrays* de booleanos, tan simple como pueda
serlo un patrón de ritmo:

```gml
#macro SECUENCIADOR_FILAS      4      // un sonido por fila
#macro SECUENCIADOR_COLUMNAS   8      // 8 beats — 2 compases de 4, igual que en 04 · 19 §1
#macro CELDA_ANCHO             24
#macro CELDA_ALTO              24
#macro REJILLA_X                60
#macro REJILLA_Y                50
```

`rejilla[_fila][_columna]` vale `true` si esa celda está activa. Se recorre por filas para
dibujar y buscar celdas activas, y se indexa por `_datos.n mod SECUENCIADOR_COLUMNAS` para
saber en qué columna estamos — el mismo `mod` que usa 04 · 19 para el compás (`beat_actual div
4`), aplicado ahora al ancho del patrón en vez de al ancho del compás.

### 3.3 · Código base

```gml
// ---------------------------------------------------------------------------
// obj_secuenciador · Create
// ---------------------------------------------------------------------------

rejilla = array_create(SECUENCIADOR_FILAS);
for (var _f = 0; _f < SECUENCIADOR_FILAS; _f++)
{
    rejilla[_f] = array_create(SECUENCIADOR_COLUMNAS, false);
}

// un sonido corto por fila y su nombre para la etiqueta — sustituye por tus samples
catalogo_sonidos = [snd_bombo, snd_caja, snd_hihat, snd_platillo];
nombres_fila     = ["Bombo", "Caja", "Hi-hat", "Platillo"];

bpm_patron     = 100;
columna_activa = -1;

function avanzar_columna(_datos)
{
    columna_activa = _datos.n mod SECUENCIADOR_COLUMNAS;

    for (var _f = 0; _f < SECUENCIADOR_FILAS; _f++)
    {
        if (rejilla[_f][columna_activa])
        {
            audio_play_sound(catalogo_sonidos[_f], 1, false);
        }
    }
}

// se engancha a la MISMA señal "beat" que emite obj_conductor · Step (04 · 19 §1);
// asume que senales_init() ya corrió una vez al arrancar el juego (04 · 16) —
// no la repitas aquí o borras a cualquier otro oyente ya registrado.
senal_escuchar("beat", avanzar_columna);

// arranca el conductor con el "click" del patrón — mismo mecanismo de 04 · 19, sin tocarlo
with (obj_conductor) { conductor_arrancar(snd_pulso_patron, other.bpm_patron); }
```

```gml
// ---------------------------------------------------------------------------
// obj_secuenciador · Step
// ---------------------------------------------------------------------------

// el "click" del patrón es un audio finito (no-loop, igual que exige conductor_arrancar
// en 04 · 19 §1); cuando termina, se relanza para que la rejilla suene en bucle. Esto NO
// modifica obj_conductor: solo vuelve a llamar a su función pública, tal y como está escrita.
if (!audio_is_playing(obj_conductor.musica))
{
    with (obj_conductor) { conductor_arrancar(snd_pulso_patron, other.bpm_patron); }
}

if (mouse_check_button_pressed(mb_left))
{
    var _col = floor((mouse_x - REJILLA_X) / CELDA_ANCHO);
    var _fil = floor((mouse_y - REJILLA_Y) / CELDA_ALTO);

    if (_col >= 0 && _col < SECUENCIADOR_COLUMNAS && _fil >= 0 && _fil < SECUENCIADOR_FILAS)
    {
        rejilla[_fil][_col] = !rejilla[_fil][_col];
    }
}
```

```gml
// ---------------------------------------------------------------------------
// obj_secuenciador · Draw
// ---------------------------------------------------------------------------

draw_set_valign(fa_middle);

for (var _f = 0; _f < SECUENCIADOR_FILAS; _f++)
{
    draw_text(REJILLA_X - 10, REJILLA_Y + _f * CELDA_ALTO + CELDA_ALTO / 2, nombres_fila[_f]);

    for (var _c = 0; _c < SECUENCIADOR_COLUMNAS; _c++)
    {
        var _x1 = REJILLA_X + _c * CELDA_ANCHO;
        var _y1 = REJILLA_Y + _f * CELDA_ALTO;

        draw_set_color(rejilla[_f][_c] ? c_lime : c_dkgray);
        draw_rectangle(_x1 + 1, _y1 + 1, _x1 + CELDA_ANCHO - 1, _y1 + CELDA_ALTO - 1, false);
    }
}
draw_set_color(c_white);

// resalta la columna que suena ahora — el mismo "que se vea el ritmo" de 04 · 19 §4,
// aplicado a la columna en vez de al sprite del enemigo
if (columna_activa >= 0)
{
    var _x1 = REJILLA_X + columna_activa * CELDA_ANCHO;
    draw_rectangle(_x1, REJILLA_Y, _x1 + CELDA_ANCHO, REJILLA_Y + SECUENCIADOR_FILAS * CELDA_ALTO, true);
}
```

> ⚠️ **`snd_bombo`, `snd_caja`, `snd_hihat`, `snd_platillo` y `snd_pulso_patron` son assets de
> proyecto**, no símbolos del runtime. `snd_pulso_patron` en concreto debe durar exactamente
> `SECUENCIADOR_COLUMNAS` beats al `bpm_patron` elegido (8 beats a 100 BPM ≈ 4,8 s): un metrónomo
> silencioso o con click sirve; lo único que importa es su duración, porque es la que marca
> cuándo se relanza el bucle en el Step de arriba.

### 3.4 · Ampliar la resolución (opcional)

Ocho columnas son ocho negras. Si quieres corcheas (16 pasos en el mismo espacio de 2 compases),
el mecanismo de la señal `"beat"` no basta por sí solo — solo avisa en beats enteros. La salida,
sin crear un segundo reloj, es la misma que usa
[04 · 19 §5](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md#5--colocar-los-eventos-el-mapa-de-la-canción)
para su nota a `beat: 2.5`: leer `frac(obj_conductor.posicion)` directamente en el Step del
secuenciador para detectar también el cruce por 0,5, además de escuchar la señal `"beat"` para
los enteros. No se desarrolla aquí para no duplicar código que ya está resuelto allí.

### 3.5 · Errores clásicos y cómo evitarlos

| Error | Qué pasa |
|---|---|
| Crear un segundo `obj_conductor` propio para el secuenciador | Dos relojes que no coinciden nunca: exactamente el problema que 04 · 19 §1 explica que pasa con dos fuentes de tiempo independientes |
| Tocar el código de `obj_conductor` para hacerlo *loop* | Rompe cualquier otro sistema (rítmico o de este documento) que dependa de su comportamiento documentado. Se relanza desde fuera, como en §3.3, no se modifica por dentro |
| `array_length_1d` en vez de `array_length` para medir la rejilla | Función obsolescente; usa siempre `array_length` |
| Alternar `audio_play_sound` con `loop = true` para las celdas | Cada celda es un golpe puntual, no una pista continua; `loop = false` es lo correcto, igual que en la reproducción de notas de 04 · 19 |
| Volver a llamar a `senales_init()` en el Create del secuenciador | Vacía el registro global de señales — cualquier otro sistema que ya escuchara algo (incluida la cámara del ejemplo de 04 · 16) deja de recibir nada |

---

## 4 · Menciones breves (baja prioridad)

Dos géneros con demanda real pero escasa dentro del ecosistema de GameMaker: no justifican una
receta completa, solo la honestidad de decir qué existe y qué no.

**Typing games (mecanografía).** Baja demanda dentro del ecosistema de GameMaker y sin receta
propia en esta biblioteca; lo técnicamente más cercano, sin desarrollar, son las ventanas de
acierto rítmicas de
[04 · 19 §2 — Juzgar la pulsación del jugador](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md#2--juzgar-la-pulsación-del-jugador),
aplicadas a la letra pulsada en vez de al beat.

**Juegos de dibujar (Gartic Phone-style).** Sin receta propia por la misma baja demanda; la
mitad del problema —convertir lo dibujado en un PNG persistente— ya está resuelta en
[04 · 10 — Visual Novel y narrativa](./10%20-%20Visual%20Novel%20y%20narrativa.md)
(`surface_create` → `sprite_create_from_surface()` → `sprite_save()`), pero la otra mitad
—capturar el trazo continuo del ratón mientras se mueve con el botón pulsado— no está ensamblada
en ningún documento de esta biblioteca, y no se inventa aquí una receta que no existe.

---

## 5 · Checklist

- [ ] El contrato de §2.1 (`iniciar`, `step`, `dibujar`, `ha_terminado`, `gano_el_jugador`) es
      idéntico en todos los cartuchos, sin excepciones ni parámetros añadidos por uno solo
- [ ] El catálogo de minijuegos es un array de structs (§2.3), nunca una cadena de `if`
- [ ] El reloj de ronda es UNO SOLO, compartido por el orquestador (§2.2), no uno por minijuego
- [ ] `gano_el_jugador()` tiene un valor por defecto coherente con el tipo de minijuego
      (sobrevivir = gana por defecto; cumplir un objetivo = pierde por defecto)
- [ ] El secuenciador escucha la señal `"beat"` del `obj_conductor` de 04 · 19; no crea un
      reloj propio (§3.1, §3.5)
- [ ] `snd_pulso_patron` dura exactamente `SECUENCIADOR_COLUMNAS` beats al BPM elegido
- [ ] Cada asset placeholder (`snd_`, `fnt_`) está creado en el proyecto antes de compilar

---

## Ver también

- [04 · 11 — Arcade y juegos de un botón](./11%20-%20Arcade%20y%20juegos%20de%20un%20botón.md) — el contenido de un cartucho de un botón (§2.6)
- [04 · 19 — Programación rítmica (juegos de ritmo)](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md) — el conductor y la señal `"beat"` que reutiliza §3
- [04 · 16 — Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — el mecanismo de callback-en-struct que usan tanto el catálogo (§2.3) como el secuenciador (§3.3)
- [04 · 36 — Habilidades, enfriamientos y recursos de combate](./36%20-%20Habilidades,%20enfriamientos%20y%20recursos%20de%20combate.md) — precedente del patrón "catálogo como datos" (§2.3)
- [04 · 44 — Bullet heaven, autobattler y deckbuilder](./44%20-%20Bullet%20heaven%2C%20autobattler%20y%20deckbuilder.md) — mismo patrón aplicado a armas (§2.3)
- [04 · 10 — Visual Novel y narrativa](./10%20-%20Visual%20Novel%20y%20narrativa.md) — la pieza suelta de captura de surface a sprite que cita §4
- [04 · 15 — Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) — para vestir las transiciones de fase de §2.4 con algo más que un corte seco

---

## Fuentes

- Wikipedia (inglés) — *WarioWare* — <https://en.wikipedia.org/wiki/WarioWare> — consultado
  2026-09-07. Fuente de los datos de §1 y §2.2: duración de 3-5 s por microjuego, 4 vidas
  iniciales, unidad de tiempo en beats y BPM creciente con la dificultad. ⚠️ Fuente secundaria
  (enciclopedia, no la documentación oficial del estudio); se marca explícitamente donde se cita.
- Wikipedia (inglés) — *Music sequencer*, sección «Step sequencer (step recording mode)» —
  <https://en.wikipedia.org/wiki/Music_sequencer> — consultado 2026-09-07. Confirma la
  definición general de un *step sequencer* (pasos de duración fija, activados por fila/columna
  en una caja de ritmos) que fundamenta el diseño de §3.
- Manual oficial de GameMaker LTS 2026, espejo local en `09 - Manual oficial/` — todas las
  funciones citadas en el código llevan su ficha verificada con `_indice/buscar.py`.
