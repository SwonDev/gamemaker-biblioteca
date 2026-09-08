# 06 · Arquitectura de un proyecto GameMaker

> **Cómo se estructura un proyecto para que crezca sin romperse.** No es sintaxis GML ni
> mecánicas: es dónde vive cada cosa, quién puede hablar con quién, y qué decisión de hoy te va a
> costar cara dentro de seis meses.
>
> **Lo que NO cubre** (y dónde está): el arco de escenas y el gestor de salas, en
> [04 · 00 Anatomía de un juego completo](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md);
> prefijos y estilo de nombres, en [05 · 04 Convenciones y estilo GML](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md);
> el sistema de señales, en [04 · 16 Señales y desacoplamiento](../04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md);
> structs y constructores, en [01 · 04](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md);
> recolector y perfilado, en [01 · 15](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md).

---

## 1 · Los principios

### 1.1 Qué significa «arquitectura» aquí

Robert Nystrom lo resume en *Game Programming Patterns*: **el buen diseño de software es el que
hace barato el cambio.** No el que es bonito, ni el que usa más patrones. El que hace que mañana,
cuando el diseñador diga «los enemigos ahora tienen escudo», toques dos archivos y no veintitrés.

> **Ante dos formas de hacer algo, gana la que reduce el número de archivos que hay que tocar
> para hacer el cambio siguiente.**

Y su contrapeso: la abstracción también cuesta. Un juego feo terminado vale infinitamente más que
uno perfectamente arquitecturado sin terminar. La arquitectura se paga con velocidad de escritura
hoy a cambio de velocidad de cambio mañana; solo compensa donde el cambio vaya a ocurrir.

### 1.2 Las cuatro fuerzas propias de GameMaker

GameMaker empuja hacia un tipo concreto de desorden. Conocer el empujón es media solución.

| Fuerza del motor | Hacia dónde te empuja | Contrapeso |
|---|---|---|
| El Asset Browser es **plano por tipo** | A no tener ninguna estructura por dominio | Carpetas por dominio **dentro** de cada tipo (§3.1) |
| `global.` funciona sin declarar nada | A que todo sea global y nada tenga dueño | Un único portal de globales (§3.3) |
| Los **eventos** son el único punto de entrada | A mezclar lógica, dibujo y datos en el Step | Capas: Step decide, Draw pinta, los structs guardan (§3.5) |
| Los `.yy`/`.yyp` son ficheros generados | A tener conflictos de Git ilegibles | Disciplina de ramas y de rooms (§3.13) |

### 1.3 Las tres capas

Casi todo problema de arquitectura en GameMaker se reduce a que **una pieza hace el trabajo de
dos capas**:

```
   DATOS          structs y JSON. No saben dibujar ni existir en una room.
     ↑            Serializables, comparables, testables.
   LÓGICA         eventos Step, funciones puras, máquinas de estado.
     ↑            Leen datos, deciden, escriben datos. NO dibujan.
 PRESENTACIÓN     Draw y Draw GUI, sprites, partículas, sonido.
                  Leen datos. NO deciden nada.
```

La flecha va en un solo sentido. Si un struct tiene un campo `color_barra_vida`, ya has mezclado
dos capas.

### 1.4 Lo que cuesta cada patrón

| Patrón | Coste inicial | Empieza a rentar |
|---|---|---|
| Carpetas por dominio | Minutos | Día 1 |
| `obj_game` persistente | ~20 líneas | Con dos rooms |
| Gestores como constructores | ~40 líneas cada uno | Cuando un sistema pasa de 3 variables globales |
| Localizador de servicios | ~30 líneas | Con 4 o más gestores |
| Datos dirigidos (JSON) | 1-2 horas | A partir de ~8 enemigos u objetos |
| Patrón comando | ~30 líneas | Con replays, IA que «juegue» o rebinding |
| Object pool ([ya escrito](../06%20-%20Assets%20y%20Scripts/scr_pool.gml)) | 0 | Al crear/destruir >50 instancias por segundo |
| Paso fijo con acumulador | ~25 líneas | Solo si escribes tu propia física |
| Versionado del guardado | ~15 líneas | Antes del primer parche público |
| Local Packages (`.yymps`) | Minutos | Al empezar el segundo proyecto |

---

## 2 · El método, paso a paso

Orden de montaje de un proyecto nuevo. Cada paso depende del anterior; saltarse uno se paga
rehaciendo.

0. **Ya existe una especificación.** El GDD de una página
   ([13 · 01 §8.1](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#81--gdd-de-una-página--plantilla))
   como mínimo, o el completo de
   [13 · 14](./14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md)
   si el proyecto lo pide — escrito siguiendo el protocolo de elicitación de
   [13 · 28](./28%20-%20De%20hazme%20un%20juego%20a%20una%20especificación%20-%20el%20protocolo%20de%20elicitación%20del%20agente.md)
   si el encargo llegó como una frase suelta. Sin esto no hay paso 1: este método monta el
   proyecto, no lo diseña.
1. **Crear el proyecto con el CLI**, no a mano:
   `gm-cli init --no-interactive -n mi-juego -t "Blank Pixel Game" --ai --toolchain GMS2@2026.0.0.23`
   ([07 · 13](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20línea%20de%20comandos.md)).
2. **`git init` y primer commit vacío**, antes de escribir una línea. Sin esto, el paso 8 no existe.
3. **Las carpetas del Asset Browser** (§3.1). Se crean vacías y se respetan.
4. **`scr_config`**: macros, enums y constantes de balance en un único script (§3.12).
5. **`obj_game` persistente y `rm_init`** (§3.2, §3.4). Aquí el juego ya arranca y va al menú.
6. **El localizador de servicios** y el primer gestor real —audio o ajustes— (§3.3).
7. **El primer sistema completo en vertical**: el jugador se mueve, se dibuja y su estado se
   guarda. Vertical antes que horizontal.
8. **Guardado con versión desde el minuto uno** (§3.10). Añadir `version` después es una
   migración; ponerlo ahora es una línea.
9. **Capa de log y asserts** (§3.14). Antes del primer bug, no después.
10. **Sacar a un módulo** lo que lleve dos semanas estable (§3.15).

> 💡 **Los pasos 1-6 caben en una tarde** y son el 90 % de lo que separa un proyecto que crece de
> uno que se atasca. No son «preparación»: son el proyecto.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 El Asset Browser: por tipo primero, por dominio después

GameMaker **obliga** a la raíz por tipo (Sprites, Objects, Rooms…). No existe una carpeta
`Jugador/` con su sprite, su objeto y su script dentro. La pregunta real es **qué haces dentro de
cada tipo**: subcarpetas por dominio, máximo tres niveles, ya fijado en
[05 · 04 §4](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md#4-organización-de-carpetas-en-el-asset-browser).
No lo repito. Lo que falta es **el criterio de reparto: qué clase de cosa va en cada sitio.**

| Va en… | Lo que es | Ejemplos | Señal de que está mal |
|---|---|---|---|
| **Included Files** (`datafiles/`) | Datos que quieres cambiar **sin recompilar** | `enemigos.json`, `niveles/*.json`, tablas de balance, `.mp4`, CSV de idiomas | Un número de balance escrito dentro de un `.gml` |
| **Scripts** | Lo que no necesita eventos: funciones puras, constructores, gestores, macros, enums | `scr_config`, `scr_servicios`, `scr_gestor_audio` | Un script que guarda estado global sin dueño |
| **Objects** | Lo que necesita eventos, posición o colisión | `obj_jugador`, `obj_enemigo_base`, `obj_game` | Un objeto vacío que solo existe para «llamar a una función» |
| **Rooms** | Escenas y niveles | `rm_init`, `rm_menu`, `rm_zona_01` | Datos de nivel colocados a mano que luego no puedes tocar por código |

La frontera exacta struct/objeto está en
[05 · 04 §6](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md#6-structs-vs-objetos--cuándo-usar-cada-uno).

> 🔺 **Trampa documentada de Included Files:** un fichero incluido no puede llamarse igual que un
> sonido con *streaming*. Con un sonido `main_music` y un fichero `main_music.ogg`, el segundo
> pasa a `undefined` en ejecución. La carpeta real es `datafiles/` y cada fichero tiene su lista
> de plataformas de destino, **configurable por Config** (§3.12).

### 3.2 `obj_game`: el controlador persistente

Un juego necesita **un** objeto que viva desde el arranque hasta `game_end()` y sea dueño de todo
lo que no pertenece a ninguna room. Se marca **Persistent** y se crea una vez, en `rm_init`.

**Sí hace:** crear los gestores en orden, llevar el tiempo global (§3.9), llamar a `limpiar()` de
cada gestor en su **Clean Up**, exponerse por el localizador (§3.3).
**No hace nunca:** lógica de jugador, enemigos, UI o nivel. En cuanto `obj_game` sabe cuánta vida
tiene el jugador, ha dejado de ser un controlador y es un objeto dios (§5).

```gml
/// obj_game · Create   (Persistent = true)
servicios_iniciar();                                   // el registro, vacío

// Los gestores se crean en orden de dependencia: config → audio → partida.
servicio_poner("config",  new GestorConfig());
servicio_poner("audio",   new GestorAudio());
servicio_poner("partida", new GestorPartida());
servicio_poner("juego",   id);   // así nadie escribe `obj_game.` fuera de aquí

acumulador = 0;                  // §3.9
```

```gml
/// obj_game · Clean Up
// Clean Up y NO Destroy: también corre al cerrar el juego y al cambiar de room.
var _nombres = variable_struct_get_names(global.__svc);
for (var _i = 0; _i < array_length(_nombres); _i++) {
    var _s = global.__svc[$ _nombres[_i]];
    if (is_struct(_s) && variable_struct_exists(_s, "limpiar")) _s.limpiar();
}
global.__svc = {};
```

#### Gestor como struct o como objeto

| Hazlo **struct** (`function Gestor() constructor`) si… | Hazlo **objeto** si… |
|---|---|
| No necesita eventos propios | Necesita Step, Draw o alarmas |
| Quieres poder crear dos (uno real y uno de pruebas) | Solo puede haber uno y debe verse en el editor de rooms |
| Quieres serializarlo con `json_stringify` | Tiene que dibujar (cámara, fundido, HUD de depuración) |
| Quieres llamarlo desde tests sin arrancar una room | Necesita colisionar o recibir input directo |

**Por defecto, struct.** No consume una instancia, no ejecuta eventos que no necesitas, lo recoge
el recolector, y **tú decides cuándo se actualiza**. Es la misma razón por la que la FSM de esta
biblioteca ([`scr_state_machine.gml`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml)) es
un struct y no un objeto.

```gml
/// scr_gestor_audio.gml
/// @desc Gestor de audio: sin eventos, serializable, sustituible en tests.
function GestorAudio() constructor {
    volumen_musica  = 1;
    volumen_efectos = 1;
    pista_actual    = undefined;

    /// @param {Real} _v  Volumen entre 0 y 1.
    static poner_volumen_musica = function(_v) {
        volumen_musica = clamp(_v, 0, 1);
        if (!is_undefined(pista_actual)) audio_sound_gain(pista_actual, volumen_musica, 0);
    };

    /// @param {Asset.GMSound} _snd
    static sonar = function(_snd) { return audio_play_sound(_snd, 5, false, volumen_efectos); };

    // ── El trío que hace falta en TODOS los gestores ─────────────────────────
    /// @returns {Struct}  Lo que hay que guardar. Solo datos.
    static serializar = function() {
        return { volumen_musica, volumen_efectos };   // atajo: la clave toma el nombre
    };
    /// @param {Struct} _d  Lo que devolvió `serializar` en una sesión anterior.
    static restaurar = function(_d) {
        volumen_musica  = _d[$ "volumen_musica"]  ?? 1;
        volumen_efectos = _d[$ "volumen_efectos"] ?? 1;
    };
    /// @desc Lo llama obj_game en su Clean Up.
    static limpiar = function() { audio_stop_all(); };
}
```

> 🔺 **`static` en un constructor no duplica el método por instancia**: se comparte. Un gestor con
> veinte métodos `static` ocupa lo mismo que uno con cero
> ([01 · 04 §6](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md#6-static-variables-y-métodos-compartidos)).
>
> 🔺 **`serializar` / `restaurar` / `limpiar` en todos los gestores.** Con esos tres nombres, el
> guardado (§3.10) y la limpieza (§3.11) se escriben una sola vez y valen para todos.

### 3.3 Localizador de servicios: un solo portal de globales

Nystrom dedica un capítulo entero al Singleton para concluir que **hay que evitarlo**: *«si
repasas la lista de problemas que causan las globales, verás que el patrón Singleton no resuelve
ninguno»*; un singleton *«es estado global, solo que encapsulado en una clase»*. Su alternativa
cuando de verdad hay un sistema único (audio, log, guardado) es el **Service Locator**: un
registro que devuelve el servicio por nombre, sin que quien lo pide sepa la implementación.

En GameMaker esto es **un único struct global** y tres funciones. Con esto, `global.` aparece **en
un solo archivo de todo el proyecto**.

```gml
/// scr_servicios.gml — el único sitio del proyecto donde se escribe `global.`

/// @desc Prepara el registro. Una sola vez, en el Create de obj_game.
function servicios_iniciar() { global.__svc = {}; }

/// @desc Registra (o sustituye) un servicio: struct gestor, instancia o función.
/// @param {String} _nombre
/// @param {Any}    _valor
/// @returns {Any}
function servicio_poner(_nombre, _valor) {
    global.__svc[$ _nombre] = _valor;
    return _valor;
}

/// @desc Devuelve el servicio pedido. Si falta, avisa y devuelve el servicio nulo: un
///       servicio ausente debe degradar el juego, no tumbarlo.
/// @param {String} _nombre
/// @returns {Any}
function servicio(_nombre) {
    var _s = global.__svc[$ _nombre];
    if (is_undefined(_s)) {
        registro_error($"Servicio no registrado: «{_nombre}»");
        return servicio_nulo();
    }
    return _s;
}

/// @desc Objeto que acepta las llamadas habituales y no hace nada («null service»).
function servicio_nulo() {
    static _nulo = {
        sonar:      function() { return undefined; },
        serializar: function() { return {}; },
        restaurar:  function() {},
        limpiar:    function() {}
    };
    return _nulo;
}
```

```gml
servicio("audio").sonar(snd_golpe);
servicio("config").poner("dificultad", Dificultad.NORMAL);
```

> 💡 **El servicio nulo es la mitad del valor del patrón.** Un menú que pruebas en su propia room,
> sin `obj_game`, no debe reventar por no haber gestor de audio: debe sonar a nada y seguir.
>
> ⚠️ **La advertencia del propio Nystrom aplica igual:** *«cada vez que haces algo accesible desde
> cualquier parte del programa, te estás buscando problemas»*. Esto es para **sistemas realmente
> únicos** —audio, guardado, log, idioma, input—, no para «el enemigo actual». Si algo se puede
> pasar como argumento, se pasa como argumento.

**Un singleton es aceptable** cuando el recurso es único **por naturaleza física** (el dispositivo
de audio, el sistema de archivos, la ventana) y su ausencia es un fallo de programación, no un
estado posible. Es el problema cuando lo usas para no pensar quién es el dueño de un dato.

Juju Adams —autor de Scribble, Vinyl, SNAP y Chatterbox— llega a lo mismo desde la práctica en
*ThoughtsOnGameMaker*. Su receta: objeto **Persistent**, creado en una sala de inicialización,
reactivado a mano si usas desactivación de instancias, y nunca destruido con un «destruye todas
las instancias» sin recrearlo. Y sus dos límites valen tanto como la receta: **úsalos con
moderación** (música, input, GUI, guardado, red) y **nunca para la instancia del jugador** — el
día que quieras dos jugadores tendrás cableado en todo el proyecto que solo hay uno. Su segunda
idea, la **«evacuación del espacio de nombres global»**, es exactamente lo que hace
`scr_servicios.gml`: no repartir `global.` por el proyecto, sino tener funciones que devuelven el
struct con el estado, para que dos librerías no puedan pisarse un nombre.

### 3.4 El flujo de arranque

`rm_init` → configuración → datos → menú. La room de arranque **no dibuja nada** y **no tiene un
solo frame de juego**: entra, monta y sale. El gestor de escenas con fundido ya está en
[04 · 00 §2](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md#2--el-gestor-de-escenas--el-esqueleto-del-arco);
aquí solo importa **el orden**, que es donde se rompen los proyectos.

```gml
/// obj_arranque · Create   (única instancia de rm_init)
// 1. Configuración del usuario: el idioma y el volumen dependen de ella.
servicio("config").cargar();

// 2. Catálogos de datos: antes que cualquier room de juego.
servicio_poner("catalogo", catalogo_cargar_todo());

// 3. Sistemas que dependen de lo anterior.
senales_init();                                   // 04 · 16
servicio("audio").restaurar(servicio("config").obtener("audio", {}));

// 4. Y solo entonces, a la primera escena de verdad.
room_goto(ROOM_ARRANQUE);                         // macro por Config, §3.12
```

> 🔺 **El orden es una dependencia real, no una preferencia.** El menú usa el idioma; el idioma
> sale de la configuración; la configuración sale del disco. Invertir dos pasos produce un bug que
> solo aparece en la **segunda** ejecución del juego: la primera no tiene fichero de configuración
> y todo cae al valor por defecto, tapando el fallo.

### 3.5 Separación de responsabilidades

**Step decide. Draw pinta. Los structs guardan.** Se incumple de tres formas concretas.

```gml
// ❌ Lógica en Draw: los eventos de dibujado PUEDEN saltarse si el juego pierde frames,
//    y entonces tu jugador deja de moverse.
/// obj_jugador · Draw
x += vel_x;  draw_self();

// ✅ Cada cosa en su capa.
/// obj_jugador · Step   →  x += vel_x;
/// obj_jugador · Draw   →  draw_self();
```

```gml
// ❌ Presentación dentro de los datos: el struct sabe de colores.
stats = { hp: 10, color_barra: c_red };

// ✅ El struct guarda hechos. Quien dibuja decide cómo se ve un hecho.
stats = { hp: 10, hp_max: 10 };
/// obj_hud · Draw GUI
draw_set_colour(stats.hp / stats.hp_max < 0.3 ? c_red : c_lime);
```

El manual oficial lo dice sin rodeos: *«no pongas código que no sea para dibujar cosas en los
eventos Draw»*.

**Objetos «tontos» y sistemas que los recorren.** El tercer incumplimiento es más sutil: cada
instancia hace un trabajo idéntico al de todas. El manual da el ejemplo canónico con `bm_add`:
cien balas que cambian el modo de mezcla rompen el lote de vértices cien veces. La bala solo tiene
datos; un controlador las dibuja todas:

```gml
/// obj_bala · Draw   → vacío (un comentario basta para suprimir el dibujado por defecto)

/// obj_game · Draw — un solo cambio de estado de GPU para todas las balas
gpu_set_blendmode(bm_add);
with (obj_bala) draw_self();
gpu_set_blendmode(bm_normal);
```

Ese es el patrón «entidades tontas + sistema que las recorre», y `with` lo hace natural en GML: en
el corpus analizado en
[07 · 15](../07%20-%20Ecosistema/15%20-%20Qué%20hacen%20de%20verdad%20los%20proyectos%20reales.md)
aparece **8 539 veces**, tercera construcción más frecuente del lenguaje.

**Máquinas de estado.** Una entidad con más de dos comportamientos necesita una FSM, no una cadena
de `if`. Ya resuelto: propia en structs,
[`scr_state_machine.gml`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml)
(`new StateMachine(id, {...}, "idle")` y `fsm.update()` en el Step); de librería, con historial y
jerarquía,
[SnowState](../07%20-%20Ecosistema/17%20-%20SnowState%20-%20máquinas%20de%20estado%20%28guía%20en%20español%29.md).
El dato de arquitectura: **20 de 21 proyectos reales usan una máquina de estados.**

### 3.6 Composición frente a herencia

GameMaker tiene **dos** herencias distintas y conviene no confundirlas:

| | Herencia de objetos (Parent) | Herencia de constructores (`:`) |
|---|---|---|
| Qué comparte | **Eventos** y variables de instancia | Variables y métodos de un struct |
| Llamada al padre | `event_inherited()` en el evento | `: Padre()` en la declaración |
| Para qué sirve de verdad | Colisiones y `with` por familia | Reutilizar datos y comportamiento sin eventos |
| Detalle | [01 · 09 §7](../01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md#7-herencia-de-objetos-parent-objects) | [01 · 04 §4.3](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md#43-herencia-el-operador-) |

**Usa padres de objetos para lo que solo ellos hacen: agrupar para colisiones y para `with`.** Un
`obj_enemigo_base` que existe para que un `collision_line` contra «cualquier enemigo» funcione
está justificado. Un `obj_entidad → obj_criatura → obj_enemigo → obj_enemigo_cuerpo` no: cada
nivel es un archivo más que leer para entender una instancia. **Dos niveles como máximo.**

Para lo demás, composición: el objeto tiene structs y cada struct cubre un dominio. Es el patrón
*Component* de Nystrom —*«los componentes son un menú a la carta: cada cliente elige los platos
que quiere»*— y su problema de partida, el «Bjørn hinchado» que acaba haciendo input, física,
gráficos y sonido, es exactamente el objeto dios de GameMaker.

```gml
/// obj_enemigo · Create
event_inherited();                          // colisión y registro comunes, del padre

// Composición: cada struct cubre UN dominio y se puede reutilizar en otro objeto.
stats      = new Stats(30, 4, 1.2);         // datos puros, serializables
fsm        = new StateMachine(id, estados_patrulla(), "patrullar");
inventario = new Inventario(4);

/// obj_enemigo · Step   →  fsm.update();
```

Ni herencia ni composición resuelven «esto ha pasado y a cinco sistemas les interesa»: eso son
señales, completas en [04 · 16](../04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md).
Reparto entre los cuatro ejes:

```
¿Comportamiento común a una familia de objetos?    → herencia de objetos
¿Capacidad que varias entidades distintas tienen?  → composición (struct)
¿Hecho consumado que a otros les interesa?         → señal
¿Necesito un valor AHORA y con respuesta?          → llamada directa
```

### 3.7 Patrón comando: input, rebinding y replays

El patrón *Command* convierte «pulsar una tecla» en **un dato**. En cuanto la intención del
jugador es un dato y no una llamada directa, salen gratis tres cosas que después cuestan un
refactor: **rebinding**, **que la IA controle al jugador** y **replays y tests deterministas**.

```gml
/// scr_comandos.gml

/// @desc Lee el hardware y devuelve la INTENCIÓN del jugador este frame. No mueve nada.
/// @returns {Struct}
function comando_leer() {
    var _mando = servicio("config").obtener("mando", 0);
    return {
        izq:    keyboard_check(vk_left)  || gamepad_button_check(_mando, gp_padl),
        der:    keyboard_check(vk_right) || gamepad_button_check(_mando, gp_padr),
        saltar: keyboard_check_pressed(vk_space),
        pausa:  keyboard_check_pressed(vk_escape)
    };
}

/// @desc Aplica un comando a una entidad. No lee teclado: solo obedece.
/// @param {Id.Instance} _quien
/// @param {Struct}      _cmd
function comando_aplicar(_quien, _cmd) {
    with (_quien) {
        vel_x = (_cmd.der - _cmd.izq) * velocidad_max;
        if (_cmd.saltar && en_suelo) vel_y = -FUERZA_SALTO;
    }
}
```

```gml
/// obj_jugador · Step — el único sitio donde se decide de dónde sale el comando
var _cmd;
switch (global.modo_entrada) {
    case Entrada.JUGADOR:    _cmd = comando_leer();         break;
    case Entrada.REPETICION: _cmd = repeticion_siguiente(); break;
    case Entrada.IA:         _cmd = ia_decidir(id);         break;
}
if (global.modo_entrada == Entrada.JUGADOR) array_push(global.repeticion.frames, _cmd);
comando_aplicar(id, _cmd);
```

Una repetición es entonces `{ semilla, frames: [] }`: structs y arrays puros, así que se guarda
con `json_stringify` sin conversión y `repeticion_siguiente()` es leer `frames[cursor++]`.

> ⚠️ **Un replay solo funciona si el juego es determinista**, y hacen falta las tres cosas a la
> vez: **semilla fijada** (`random_set_seed`), **paso fijo** en la lógica (§3.9) y **ninguna
> decisión que dependa de `fps_real`**. Con `delta_time` en la lógica, dos ejecuciones de la misma
> grabación divergen. Es literalmente el argumento de Nystrom contra el paso variable: *«la misma
> bala acabará en sitios diferentes en máquinas diferentes»*.

### 3.8 Datos dirigidos: definir el juego en JSON

Ocho enemigos con sus estadísticas escritas en su `Create` son ocho archivos que abrir, recompilar
y volver a probar cada vez que cambia un número. Con datos dirigidos son **un JSON en Included
Files** que puedes editar sin abrir el IDE.

```json
// datafiles/enemigos.json
{
  "goblin":  { "sprite": "spr_goblin",  "hp": 20, "dano": 3, "velocidad": 1.2,
               "objeto": "obj_enemigo_cuerpo",    "sueltas": ["moneda", "pocion"] },
  "arquero": { "sprite": "spr_arquero", "hp": 14, "dano": 5, "velocidad": 0.9,
               "objeto": "obj_enemigo_distancia", "sueltas": ["flecha"] }
}
```

```gml
/// scr_catalogo.gml

/// @desc Lee un fichero de Included Files y lo devuelve como struct.
/// @param {String} _fichero  Nombre tal cual está en datafiles/.
/// @returns {Struct}
function catalogo_leer(_fichero) {
    if (!file_exists(_fichero)) {
        registro_error($"Falta el fichero de datos: {_fichero}");
        return {};
    }
    var _b = buffer_load(_fichero);              // buffer: soporta UTF-8 sin sorpresas
    var _texto = buffer_read(_b, buffer_text);
    buffer_delete(_b);
    return json_parse(_texto);
}

/// @desc Todos los catálogos del juego, en el arranque (§3.4).
function catalogo_cargar_todo() {
    return { enemigos: catalogo_leer("enemigos.json"),
             objetos:  catalogo_leer("objetos.json"),
             niveles:  catalogo_leer("niveles.json") };
}
```

Los nombres de asset del JSON son **cadenas**: hay que traducirlos a handles con
`asset_get_index`.

```gml
/// @desc Crea un enemigo a partir de su clave del catálogo.
/// @param {String} _clave   Por ejemplo "goblin".
/// @param {Real}   _px
/// @param {Real}   _py
/// @returns {Id.Instance}   La instancia creada, o noone si la clave no existe.
function enemigo_crear(_clave, _px, _py) {
    var _cat = servicio("catalogo").enemigos;
    if (!variable_struct_exists(_cat, _clave)) {
        registro_error($"Enemigo desconocido en el catálogo: «{_clave}»");
        return noone;
    }
    var _def = _cat[$ _clave];

    var _obj = asset_get_index(_def.objeto);     // "obj_enemigo_cuerpo" → handle
    if (_obj == -1) {
        registro_error($"El objeto «{_def.objeto}» del catálogo no existe en el proyecto");
        return noone;
    }

    // El struct de instance_create_layer se aplica ANTES del Create.
    return instance_create_layer(_px, _py, "Instances", _obj, {
        clave_catalogo: _clave,
        sprite_index:   asset_get_index(_def.sprite),
        hp:             _def.hp,
        hp_max:         _def.hp,
        dano:           _def.dano,
        velocidad_max:  _def.velocidad,
        sueltas:        _def[$ "sueltas"] ?? []
    });
}
```

> 🔺 **El quinto argumento de `instance_create_layer` es la pieza clave**: el struct se aplica
> **antes** de que corra el Create, así que el Create ya puede leer `hp` y `velocidad_max`. Sin él
> tendrías que crear, escribir variables y reinicializar: la fuente clásica del bug «el enemigo
> nace con la vida del prototipo».
>
> 🔺 **Los IDs de assets son handles en 2026, no enteros.** `asset_get_index` devuelve `-1` si no
> encuentra el nombre; compruébalo. Nada de aritmética con ellos:
> [01 · 03 Handles](../01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md).
>
> 💡 Con el catálogo en JSON, generar contenido con una hoja de cálculo, un script de balance o
> una IA es trivial. El juego no distingue quién escribió el goblin.

### 3.9 Tiempo: frames fijos, `delta_time` y paso fijo con acumulador

La base —`game_set_speed`, `delta_time`, `fps` frente a `fps_real`, Time Sources y `call_later`—
está en [01 · 06 §7 y §8](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md#7-velocidad-de-juego-delta_time-y-game-loop),
y el `time_scale` para pausa y cámara lenta en
[04 · 15 §5.0](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md#50-sistema-de-tiempo-hit-stop-y-time-scale).
Lo que va aquí es **la decisión de arquitectura**: qué modelo de tiempo adopta el proyecto, porque
cambiarlo a mitad es rehacer todo el movimiento.

| Modelo | Cómo se escribe | Cuándo | Riesgo |
|---|---|---|---|
| **Frames fijos** | `game_set_speed(60, gamespeed_fps)` y contar frames | Plataformas, lucha, bullet hell, replays, cualquier salto que deba medir siempre lo mismo | Si no fijas la velocidad, un monitor de 144 Hz acelera el juego |
| **`delta_time`** | Multiplicar el movimiento por `delta_time / 1000000` | Cámaras, UI, animación, efectos | Pierdes determinismo: replays y tests dejan de reproducirse |
| **Paso fijo + acumulador** | Lógica a paso fijo, dibujado libre | Física propia, red, simulación | ~25 líneas más y hay que interpolar el dibujado |

**Lo que hacen los proyectos reales:** solo 11 de 21 usan `delta_time`, y no por descuido. La
combinación recomendada por defecto es **frames fijos para la lógica y `delta_time` para lo
visual**
([07 · 15 §2](../07%20-%20Ecosistema/15%20-%20Qué%20hacen%20de%20verdad%20los%20proyectos%20reales.md#2-delta_time-sigue-siendo-minoritario--y-es-una-decisión-no-un-descuido)).

Si escribes tu propia física necesitas el tercer modelo: el bucle con acumulador de *Game
Programming Patterns*, traducido a los eventos de GameMaker.

```gml
// PASOS_FISICA y MAX_PASOS_POR_FRAME viven en scr_config.gml (§3.12 más abajo, el ÚNICO
// sitio donde se declaran con #macro) — aquí solo se usan, no se redeclaran: GameMaker
// rechaza un macro definido dos veces aunque el valor sea idéntico.

/// obj_game · Create
acumulador = 0;
alfa       = 0;    // 0..1 · cuánto interpolar el dibujado entre dos pasos

/// obj_game · Begin Step
var _dt_paso = 1000000 / PASOS_FISICA;      // microsegundos que dura un paso fijo
acumulador += delta_time;

var _n = 0;
while (acumulador >= _dt_paso && _n < MAX_PASOS_POR_FRAME) {
    with (obj_cuerpo_fisico) simular_paso(1 / PASOS_FISICA);   // dt SIEMPRE constante
    acumulador -= _dt_paso;
    _n++;
}
// Si nos comemos el tope, el frame fue tan lento que no alcanzamos el tiempo real.
// Descartamos el retraso: mejor ir a cámara lenta que colgarse acumulando pasos.
if (_n >= MAX_PASOS_POR_FRAME) acumulador = 0;
alfa = acumulador / _dt_paso;

/// obj_cuerpo_fisico · Draw — interpolar entre el paso anterior y el actual
var _a = obj_game.alfa;
draw_sprite(sprite_index, image_index, lerp(px_anterior, x, _a), lerp(py_anterior, y, _a));
```

> 🔺 **`MAX_PASOS_POR_FRAME` no es opcional.** Sin él, un frame lento obliga a más pasos, que hacen
> el siguiente más lento, que exige más pasos: la *spiral of death*. Con el tope, el juego se
> ralentiza visualmente pero nunca se cuelga.
>
> 🔺 **`room_speed` está deprecada** en 2026 y además ya no fija la velocidad de una room sino la
> de todas. `game_set_speed(FPS_OBJETIVO, gamespeed_fps)` va en el arranque, siempre.

### 3.10 Estado global, guardado y migraciones

Antes de escribir una línea de guardado hay que clasificar, porque las tres clases de estado van a
**ficheros distintos con reglas distintas**:

| Clase | Qué es | Dónde | Cuándo se escribe | Ejemplos |
|---|---|---|---|---|
| **Configuración** | Preferencias del jugador, no del personaje | `config.json`, uno | Al cambiarla en el menú | Volumen, idioma, resolución, rebinding, accesibilidad |
| **Progreso persistente** | Lo que sobrevive a todas las partidas | `perfil.json`, uno | En hitos | Logros, mejores tiempos, desbloqueos, New Game+ |
| **Estado de partida** | La partida en curso | `partida_N.json`, uno por *slot* | En puntos de guardado o autoguardado | Room, posición, inventario, banderas de historia |

Confundirlos produce bugs que el jugador percibe como injustos: borrar la partida y perder el
volumen, o que los logros dependan del *slot*. La implementación robusta —temporal, validación,
reemplazo, slots, metadatos— está en
[`scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml), y el sandbox, los
buffers y las trampas de `json_parse` con handles en
[01 · 14](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md). Lo que añado es **lo
que casi nadie hace y siempre se acaba necesitando: versionar el formato.**

```gml
/// scr_migraciones.gml — VERSION_GUARDADO se declara en scr_config.gml (§3.12, la única
/// fuente de constantes del proyecto); súbelo ahí CADA VEZ que cambie la forma de los
/// datos. Aquí solo se usa, no se redeclara con #macro otra vez.

/// @desc Lleva un guardado de cualquier versión anterior a la actual. Las migraciones son
///       escalones: se aplican en orden y sin saltarse ninguna.
/// @param {Struct} _d  Datos recién leídos del disco.
/// @returns {Struct}
function partida_migrar(_d) {
    var _v = _d[$ "version"] ?? 0;

    if (_v < 1) {   // v0 → v1: el inventario pasó de array de cadenas a array de structs
        var _nuevo = [], _viejo = _d[$ "inventario"] ?? [];
        for (var _i = 0; _i < array_length(_viejo); _i++) {
            array_push(_nuevo, { clave: _viejo[_i], cantidad: 1 });
        }
        _d.inventario = _nuevo;
        _v = 1;
    }
    if (_v < 2) {   // v1 → v2: los ajustes de audio salieron del guardado de partida
        if (variable_struct_exists(_d, "volumen")) variable_struct_remove(_d, "volumen");
        _v = 2;
    }
    if (_v < 3) {   // v2 → v3: campo nuevo; los guardados antiguos toman el valor por defecto
        _d.dificultad ??= Dificultad.NORMAL;
        _v = 3;
    }
    _d.version = VERSION_GUARDADO;
    return _d;
}

/// @desc Carga una partida ya migrada.
/// @param {Real} _slot
/// @returns {Struct|Undefined}
function partida_cargar(_slot) {
    var _d = load_game_raw(_slot);                 // scr_save_load.gml
    if (is_undefined(_d)) return undefined;
    if ((_d[$ "version"] ?? 0) > VERSION_GUARDADO) {
        // El jugador ha vuelto a una versión anterior del juego. No adivines: avisa.
        registro_error("El guardado es de una versión más nueva del juego");
        return undefined;
    }
    return partida_migrar(_d);
}
```

> 🔺 **Las tres reglas del formato de guardado:**
> 1. **El campo `version` existe desde el primer día**, aunque valga 1 y no haya migraciones.
>    Añadirlo después obliga a tratar «sin campo» como caso especial para siempre.
> 2. **Las migraciones son escalones acumulativos** (`if (_v < 1)`, `if (_v < 2)`…), nunca un
>    `switch`: un guardado de la v0 tiene que poder llegar a la v5 pasando por todas.
> 3. **Nunca guardes un handle de asset ni un ID de instancia.** Guarda la **clave del catálogo**
>    (`"goblin"`) y reconstruye con `asset_get_index` (§3.8). Un handle no significa nada en la
>    siguiente ejecución.

#### Autoguardado: cuándo, escritura atómica e indicador

El autoguardado vive en su **propia ranura** (`"auto"`, nunca `"slot1"`): si pisara la partida
manual del jugador, un mal momento para guardar o un bug de tu lado le arruinaría una partida que
él sí guardó a propósito, y además le deja intacta la posibilidad de volver atrás cargando su
último guardado manual. `save_game` (arriba) ya escribe de forma **atómica** — al temporal, se
valida lo escrito y solo entonces se reemplaza con `file_rename` — así que autoguardar es
reutilizar esa función con una ranura fija, no reinventar la escritura segura: un corte de luz a
mitad de un autoguardado deja el `.tmp` a medias y la partida buena intacta.

Lo que sí hace falta decidir es **cuándo dispararlo**:

| Momento | ¿Dispara? | Por qué |
|---|---|---|
| Cambio de sala, ya asentada (tras crear todo lo persistente, no en mitad del `Room Start`) | ✅ | El mundo nuevo ya existe entero; no hay nada a medio construir que perder |
| Hito de progreso (checkpoint, jefe derrotado, capítulo cerrado) | ✅ | Es justo el punto al que el jugador espera volver si algo sale mal |
| A mitad de un fundido, una pantalla de carga o una cutscene | ❌ **nunca** | El estado está a medio montar: cámara a medio mover, room a medio poblar. Cargar eso después reproduce la transición a medias |
| Cada N segundos por temporizador, sin más criterio | ❌ | Es la opción perezosa: puede disparar con el jugador en pleno salto o a mitad de una línea de diálogo |

```gml
/// scr_autoguardado.gml — depende de scr_save_load.gml (save_game). No repite su
/// escritura atómica: la reutiliza con una ranura dedicada al autoguardado.

#macro SLOT_AUTOGUARDADO             "auto"
#macro AUTOGUARDADO_INDICADOR_FRAMES 90        // ~1.5 s a 60 fps

global.autoguardado_bloqueado    = false;      // true durante fundidos, cargas y cutscenes
global.autoguardado_frames_icono = 0;          // cuenta atrás del indicador en Draw GUI

/// @func autoguardado_intentar(_recolectar_datos)
/// @desc Autoguarda si el momento es seguro. Se llama solo en los dos puntos
///       marcados con ✅ en la tabla de arriba, nunca en un Step genérico.
/// @param {Function} _recolectar_datos  Arma el struct con el estado actual.
/// @returns {Bool}
function autoguardado_intentar(_recolectar_datos) {
    if (global.autoguardado_bloqueado) { return false; }

    var _ok = save_game(SLOT_AUTOGUARDADO, _recolectar_datos());
    if (_ok) { global.autoguardado_frames_icono = AUTOGUARDADO_INDICADOR_FRAMES; }
    return _ok;
}
```

```gml
/// Draw GUI de obj_hud — el indicador es la única prueba que tiene el jugador de
/// que el juego SÍ guardó. Sin él, un autoguardado silencioso es indistinguible
/// de uno que falló en silencio.
if (global.autoguardado_frames_icono > 0) {
    global.autoguardado_frames_icono--;
    draw_sprite(spr_icono_guardando, 0, 32, 32);
}
```

`global.autoguardado_bloqueado` la levanta lo que sea que abra un fundido, una carga o una
cutscene, y la baja al terminar: es una bandera propia, no una variable del runtime — GameMaker no
expone ninguna para saber si hay una transición de sala en curso.

### 3.11 Memoria y ciclo de vida

La tabla de «qué hay que destruir» y el funcionamiento del recolector están en
[01 · 15 §5 y §8](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#8-checklist-de-limpieza-de-recursos-dinámicos).
Lo específico de arquitectura son tres decisiones.

**1. Cada recurso tiene un dueño único y explícito.** Si dos objetos pueden liberar la misma
surface, uno la libera y el otro la usa. Regla: **quien lo crea lo destruye**; si eso no es
posible, el dueño es el gestor.

```gml
/// GestorRender · el dueño de las surfaces del juego
function GestorRender() constructor {
    surf_luz = -1;
    static obtener_surface_luz = function() {
        if (!surface_exists(surf_luz)) {          // puede desaparecer al perder el foco
            surf_luz = surface_create(display_get_gui_width(), display_get_gui_height());
        }
        return surf_luz;
    };
    static limpiar = function() {
        if (surface_exists(surf_luz)) { surface_free(surf_luz); surf_luz = -1; }
    };
}
```

**2. `Clean Up`, nunca `Destroy`.** El evento Destroy **no se ejecuta** al cambiar de room ni al
cerrar el juego; Clean Up sí. Un `ds_map` liberado solo en Destroy es una fuga garantizada en
cuanto el jugador cambie de zona.

**3. `weak_ref` para «apuntar sin ser dueño».** Cualquier sistema que guarde una referencia a otra
entidad —el objetivo de un enemigo, el oyente de una señal— corre el riesgo de mantener viva una
referencia a algo muerto:

```gml
/// obj_enemigo · Step
if (!is_undefined(ref_objetivo) && !weak_ref_alive(ref_objetivo)) {
    ref_objetivo = undefined;        // el objetivo ya no existe: a buscar otro
}
```

> ⚠️ **El recolector NO recoge surfaces, buffers, `ds_*`, emisores de audio, cámaras ni time
> sources.** Todo lo que tenga `*_destroy()`, `*_free()` o `*_delete()` lo liberas tú. Ese es el
> motivo real por el que en código nuevo se prefieren **arrays y structs** a `ds_*`: se recogen
> solos y se serializan sin conversión.

### 3.12 Macros, enums y Configs del IDE

**Un solo script `scr_config`** con todas las constantes. Lo recomienda el propio manual: *«te
recomendamos que crees un script asset dedicado y definas todas tus macros ahí»*.

```gml
/// scr_config.gml — la única fuente de constantes del proyecto

// ── Motor ──────────────────────────────────────────────────────────────────
#macro FPS_OBJETIVO        60
#macro PASOS_FISICA       120
#macro MAX_PASOS_POR_FRAME  5

// ── Balance (lo que el diseñador va a tocar) ───────────────────────────────
#macro GRAVEDAD             0.4
#macro FUERZA_SALTO         9
// El coyote time tiene su propio macro y su explicación completa en
// 04 · 01 §5.0 (COYOTE_FRAMES) — no lo repitas aquí con otro valor.

// ── Guardado ───────────────────────────────────────────────────────────────
#macro VERSION_GUARDADO     3
#macro CARPETA_GUARDADO    "guardados/"

// ── Enumeraciones: nunca cadenas sueltas para un conjunto cerrado ──────────
enum Registro   { DEPURACION, INFO, AVISO, ERROR }
enum Entrada    { JUGADOR, REPETICION, IA }
enum Dificultad { FACIL, NORMAL, DIFICIL }
```

> 🔺 **Sintaxis de `#macro`: sin `=` y sin `;` finales.** `#macro TOTAL = 10;` no es una macro
> válida y GameMaker no siempre lo dice con claridad.
>
> 💡 **Enum frente a cadena:** un `enum` es un entero en compilación, Feather te autocompleta los
> valores y una errata se ve al compilar; con cadenas (`estado == "coriendo"`) se descubre jugando.
> La excepción son las **claves de catálogo** (§3.8), que vienen de un JSON y deben ser cadenas.

**Configs del IDE: el mismo código con constantes distintas.** El Editor de Configuraciones (Asset
Browser → Extras) permite varias configuraciones —todas hijas de `Default`— y **cada una puede dar
un valor distinto a la misma macro**, con la sintaxis `#macro <Config>:<NOMBRE> <valor>` y **sin
espacios** alrededor de los dos puntos:

```gml
#macro NIVEL_REGISTRO         Registro.INFO
#macro Debug:NIVEL_REGISTRO   Registro.DEPURACION
#macro Release:NIVEL_REGISTRO Registro.AVISO

#macro DEV                    false
#macro Debug:DEV              true

#macro ROOM_ARRANQUE          rm_splash
#macro Debug:ROOM_ARRANQUE    rm_pruebas      // saltar el menú mientras desarrollas
```

| Config | Para qué | Qué cambia |
|---|---|---|
| `Default` | Día a día | Log en INFO, herramientas de debug activas |
| `Debug` | Cazar un bug concreto | Log al máximo, salto directo a la room de pruebas, `DEV = true` |
| `Release` | La build que se publica | Solo errores, `DEV = false`, sin rooms de prueba |

Las Configs **también controlan** el grupo de texturas de cada sprite, el grupo de audio de cada
sonido y **las plataformas a las que se copia cada Included File**: así las texturas de alta
resolución no entran en la build móvil sin tocar una línea de código.

> ⚠️ **Las Configs no son ramas de Git.** Sirven para variar constantes y qué se empaqueta, no para
> tener dos versiones distintas del juego. Si necesitas eso, es una rama.

### 3.13 Git: qué se ignora y por qué duelen las rooms

Que Git es obligatorio y por qué el `.yyz` no basta está en
[03 · 24](../03%20-%20Cursos%20%28YouTube%29/24%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Control%20de%20Versiones%20con%20Git.md).
Aquí toca **qué pasa con los ficheros del proyecto**.

**GameMaker genera él mismo `.gitignore` y `.gitattributes`** en proyectos nuevos o importados si
está activada *Add skeleton .git defaults to new/imported projects* en Preferencias → **Source
Control (Git)**. El `.gitattributes` hace dos cosas que valen su peso en oro trabajando en equipo:
marca los `.yy` como **`linguist-generated`** (GitHub deja de contarlos como código) y **fuerza
finales de línea LF** en los metadatos, porque Windows, macOS y Linux usan convenciones distintas
y eso solo genera conflictos falsos.

El contenido de la plantilla es público —issue
[YoYoGames/GameMaker-Bugs#2922](https://github.com/YoYoGames/GameMaker-Bugs/issues/2922),
implementado y verificado en IDE `2024.400.0.550`—. El grueso son entradas de sistema operativo
(`Thumbs.db`, `.DS_Store`, `._*`, `$RECYCLE.BIN/`, `*.stackdump`, `*.lnk`…) y **solo dos líneas son
de GameMaker**. Conviene añadirle lo que produce compilar:

```gitignore
# GameMaker temporary files  ← lo que trae la plantilla oficial
*.resource_order
*.old

# Salida de compilación y caché local  ← añadido de esta biblioteca
/Output/
/build/
/tmp/
*.yyz
```

> ⚠️ El segundo bloque **no** es parte de la plantilla oficial: los nombres de las carpetas de
> salida dependen de tus **Preferencias → Runtime/Output**. Y **el repositorio `github/gitignore`
> NO tiene plantilla de GameMaker** (comprobado el 06-09-2026): la autoritativa es la del IDE.
> Desconfía de los `.gitignore` de GameMaker anteriores a 2020 que circulan por internet: ignoran
> carpetas como `Configs/` o `sound/audio/` que **ya no existen** en el formato 2.3+.

**Por qué no se editan los `.yy` ni el `.yyp` a mano.** El manual describe el formato como
*«similar a JSON»* — y ahí está la trampa: **no es JSON válido**. Butterscotch Shenanigans, que
construye herramientas sobre él (Stitch), lo documenta con precisión: los `.yy` llevan **comas
finales** y valores **Int64**, así que un parser JSON genérico o falla o —peor— reescribe el
fichero con otro formato y te llena el diff de ruido que no has cambiado. Y hay una segunda razón:
el `.yy` describe también **los ficheros asociados que le pertenecen** (el PNG del sprite, el
`.gml` del script); editarlo a mano rompe esas referencias y GameMaker responde pidiéndote
desvincular recursos al abrir el proyecto, un proceso que el propio manual advierte que **«no
sustituye a un buen control de versiones»**. La forma correcta de tocar recursos por código es el
`resourcetool` del CLI o su MCP
([07 · 13 §6](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20línea%20de%20comandos.md#6-gm-cli-resourcetool--editar-el-proyecto-sin-ide)):

```sh
gm-cli resourcetool eval "create object obj_enemigo_arquero --parent obj_enemigo_base"
```

> 💡 **Detalle del formato:** las carpetas del árbol del Asset Browser **no existen en disco**. En
> disco cada recurso vive en una carpeta plana por tipo (`objects/`, `sprites/`…) y la jerarquía la
> definen un campo `parent` dentro de cada `.yy` y la lista `Folders` del `.yyp`. Por eso
> reorganizar carpetas toca **muchos** ficheros: hazlo en un commit propio, nunca mezclado con
> cambios de código.

**Ramas y el problema de las rooms.** El `.yy` de una room contiene **la lista completa de
instancias colocadas, cada una con su identificador**, en un solo fichero: es el recurso donde más
gente trabaja a la vez y el que peor se fusiona. El hilo *Conflict problem with git* del foro
oficial (2023) recoge la experiencia de varios equipos, y la conclusión es que **el problema no lo
resuelve una herramienta, lo resuelve el proceso**.

| Situación | Cómo se trabaja |
|---|---|
| Dos personas en **rooms distintas** | Sin problema: reparto normal por ramas |
| Dos personas en **la misma room** | **Una room, un dueño**, acordado por adelantado |
| Conflictos en el **orden de recursos** | Ya resuelto: `*.resource_order` está en el `.gitignore` oficial desde 2024.4 |
| Ramas separadas durante semanas | `git fetch` + `git rebase` **cada vez que el compañero fusiona**, no al final |
| El conflicto ya ocurrió en un `.yy` | Resolverlo línea a línea corrompe la room: quédate con una versión entera (`--ours`/`--theirs`) y rehaz lo otro en el editor |

> 💡 **La forma de evitarlo es de diseño, no de Git:** cuanto más de tu nivel esté en un JSON de
> Included Files (§3.8) y menos colocado a mano en el editor de rooms, menos superficie de
> conflicto. Un fichero de nivel en JSON **sí** se fusiona línea a línea. Y un reparto que funciona
> en equipos pequeños: **una rama de programación y otra de diseño y arte**, fusionadas una vez por
> semana — separa a quien toca `.gml` de quien toca `.yy`.
>
> 🔺 **Antes de cambiar de rama, cierra el proyecto en el IDE.** GameMaker lo mantiene en memoria y
> puede reescribir ficheros al perder el foco.
>
> ⚠️ **No uses el plugin de Git del IDE como control de versiones principal.** Existe y funciona
> (ventana de Conflicts con *Use Theirs* / *Use Mine* / *Merge*), pero la recomendación mayoritaria
> en el foro oficial es Git externo: varios usuarios reportan que un conflicto grande tumba el IDE.

> 🔺 **El conflicto que de verdad pierde trabajo sin avisar: dos ramas añaden recursos
> distintos al `.yyp` raíz.** La regla de arriba —«quédate con una versión entera (`--ours` o
> `--theirs`)»— es correcta cuando el conflicto es sobre **el mismo** recurso. No lo es cuando
> cada rama añadió un recurso **distinto**: el `.yyp` es la lista de todo lo que el proyecto
> reconoce, así que tomar una versión entera **deja huérfano en disco** el recurso que solo
> existía en la otra rama —sus ficheros siguen en `objects/`, `sprites/`… pero el `.yyp` ya no
> los lista—. GameMaker no avisa con un error: el proyecto abre limpio y el recurso, simplemente,
> ya no está en el Asset Browser. Se descubre semanas después, cuando alguien busca ese enemigo o
> ese sprite y no aparece.
>
> La corrección, después de resolver el conflicto con `--ours`/`--theirs`:
> 1. Comprueba en el historial de Git (`git log --diff-filter=A -- "**/*.yy"` sobre la rama
>    perdedora, o simplemente recordando qué añadió cada quien) qué recursos metió la rama que
>    **no** ganó el conflicto.
> 2. Vuelve a darlos de alta con `gm-cli resourcetool eval "create <tipo> <nombre> ..."` —los
>    ficheros del recurso siguen en disco, solo falta la entrada en el `.yyp`— o arrastrando la
>    carpeta del recurso al Asset Browser del IDE, que ofrece re-vincularlo.
> 3. Si el proyecto usa el `gml-parser` de Bscotch (§1 de
>    [`12 · 08`](../12%20-%20Utilidades%20e%20integraciones/08%20-%20Tooling%20externo%20-%20CLI%2C%20parsers%20e%20ingeniería%20inversa.md#1--stitch-bscotch--el-kit-de-pipeline-más-serio)),
>    su método `project.addAssetToYyp('ruta/al/recurso.yy')` hace exactamente este paso 2 desde
>    Node: está pensado, en palabras de su propio README, para «recuperar recursos huérfanos».
>
> Ninguna herramienta detecta el huérfano por ti — ni `gm-cli`, ni el plugin de Git del IDE, ni
> YYP Maker (§3 de [`12 · 01`](../12%20-%20Utilidades%20e%20integraciones/01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md#3-compilar-y-automatizar)):
> la única defensa real es que, tras fusionar una rama que añadió assets, **abras el proyecto y
> mires si todo lo nuevo de esa rama sigue en el Asset Browser** antes de seguir trabajando encima.

### 3.14 Depuración estructurada

**a) Una capa de log con niveles.** `show_debug_message` a pelo produce, a los dos meses, una
consola donde no se lee nada. Con cinco líneas más tienes niveles, filtro por Config y origen:

```gml
/// scr_registro.gml — la capa de log del proyecto

/// @desc Escribe si el nivel supera el umbral de la Config actual.
/// @param {Real}   _nivel   Un valor de la enumeración Registro.
/// @param {String} _texto
function registro_escribir(_nivel, _texto) {
    if (_nivel < NIVEL_REGISTRO) exit;
    static _etiquetas = ["DEBUG", "INFO", "AVISO", "ERROR"];
    var _origen = (object_index != -1) ? object_get_name(object_index) : "global";
    show_debug_message($"[{_etiquetas[_nivel]}] ({_origen}) {_texto}");
}

function registro_depurar(_t) { registro_escribir(Registro.DEPURACION, _t); }
function registro_info(_t)    { registro_escribir(Registro.INFO,       _t); }
function registro_aviso(_t)   { registro_escribir(Registro.AVISO,      _t); }

/// @desc Un error siempre se escribe, y en desarrollo vuelca además la pila de llamadas.
function registro_error(_t) {
    registro_escribir(Registro.ERROR, _t);
    if (DEV) {
        var _pila = debug_get_callstack(8);
        for (var _i = 0; _i < array_length(_pila); _i++) show_debug_message($"        ← {_pila[_i]}");
    }
}
```

> 💡 **`debug_get_callstack()` convierte un log en un diagnóstico.** Saber que se pidió un servicio
> inexistente no sirve; saber desde dónde se pidió, sí. Y como el nivel se controla por Config
> (§3.12), la build de Release no imprime ruido y no hay que ir borrando `show_debug_message`.

**b) Aserciones.** El patrón que falla ruidosamente en desarrollo y calla en release está en
[05 · 04 §7](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md#7-gestión-de-errores-y-aserciones),
y hay una versión lista (`debug_assert`) en
[`scr_debug.gml`](../06%20-%20Assets%20y%20Scripts/scr_debug.gml). La decisión de arquitectura es
**dónde ponerlas**: en las **fronteras** —entrada de las funciones públicas de un gestor, datos
leídos del disco, resultado de `asset_get_index`— y nunca dentro de bucles calientes.

**c) Vistas de depuración por sistema.** El Debug Overlay admite vistas propias con controles en
vivo; la familia completa (`dbg_view`, `dbg_section`, `dbg_slider`, `dbg_watch`, `dbg_button`,
`dbg_checkbox`, `dbg_drop_down`, `dbg_text_input`…) está en
[01 · 15 §4](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#vistas-de-depuración-personalizadas-muy-potente).
Lo que aporta la arquitectura es **una vista por sistema, creada por el propio gestor**, en vez de
una vista gigante en `obj_game`:

```gml
/// GestorAudio · añadido al constructor
static crear_vista_debug = function() {
    if (!DEV) exit;
    dbg_view("Audio", false);                 // pestaña propia, oculta por defecto
    dbg_section("Volúmenes");
    dbg_slider(ref_create(self, "volumen_musica"),  0, 1, "Música");
    dbg_slider(ref_create(self, "volumen_efectos"), 0, 1, "Efectos");
};
```

> ⚠️ **`ref_create` necesita un struct o una instancia**: las variables locales no se pueden
> vigilar, porque la vista se declara una sola vez. Otra razón para que el estado de un sistema
> viva dentro de su gestor y no en variables sueltas.

### 3.15 Escalar: módulos y Local Packages

Un sistema está listo para salir del proyecto cuando cumple tres cosas: **no menciona ningún asset
concreto del juego**, **no lee `global.` salvo por el localizador**, y **lleva dos semanas sin que
lo toques**.

**Módulo dentro del proyecto** = una carpeta por sistema en `Scripts/` con un prefijo común en sus
funciones (`registro_*`, `servicio_*`, `catalogo_*`). El prefijo es lo que evita colisiones al
importarlo en otro proyecto.

**Módulo entre proyectos** = un **Local Package**: *Tools → Create Local Package*, rellenar
*Display Name* y *Package ID*, elegir los assets con *Add* y guardar. Sale un fichero **`.yymps`**
que se importa arrastrándolo sobre el IDE o con *Tools → Import Local Package*. Firmarlo exige un
certificado (Preferencias → Marketplace) y hace que un paquete manipulado no se pueda importar.

> ⚠️ **Discrepancia real en el manual.** La página *Local Asset Packages* **en español** dice que
> el formato es `*.yymp`; la **inglesa** de esa misma página y la de *Formato de proyecto* dicen
> **`.yymps`**, y que `.yymp` es el formato **anterior a 2.3**. En LTS 2026 el IDE crea `.yymps`;
> trata `.yymp` como legado. Es un error de la traducción oficial, no del motor.

Candidatos naturales a `.yymps`: `scr_servicios`, `scr_registro`, la parte de motor de
`scr_config`, la FSM, el pool, el guardado, las señales y la cámara — los scripts de
[06 · Assets y Scripts](../06%20-%20Assets%20y%20Scripts/README.md) están escritos con esa idea.

**La alternativa: un proyecto plantilla.** Es lo que hace Butterscotch Shenanigans —un proyecto
base con sus librerías separadas (shaders, input, audio, localización) del que arrancan todos sus
juegos—, y la extensión **Stitch** para VS Code existe en buena parte para eso: su comando *Import
Assets* copia assets o carpetas enteras de un proyecto a otro y permite **reimportar** para
mantener el código compartido al día. Un `.yymps` es una foto; un proyecto plantilla más una
herramienta de importación es un enlace vivo.

> ⚠️ **Y la advertencia que cierra el documento, en palabras de Juju Adams:** *«no necesitas todo
> esto… es fácil sentir que debes resolver cada problema antes de hacer un juego»*. Minit y Disc
> Room se hicieron con muy poco código compartido. Esto describe el techo, no el suelo: **coge lo
> que tu proyecto necesite hoy y deja el resto para cuando duela.**

---

## 4 · La plantilla y el checklist

### 4.1 El árbol del Asset Browser

```
Sprites/     Player/ · Enemies/ · UI/ · FX/ · Tilesets/
Objects/
  System/      obj_game · obj_camara · obj_fundido · obj_debug
  Player/      obj_jugador
  Enemies/     obj_enemigo_base · obj_enemigo_cuerpo · obj_enemigo_distancia
  UI/          obj_hud · obj_menu · obj_pausa
  Collision/   obj_muro · obj_zona_trigger
Rooms/
  System/      rm_init
  Menus/       rm_splash · rm_menu · rm_opciones · rm_creditos
  Levels/      rm_zona_01 · rm_zona_02
  Test/        rm_pruebas          ← se borra antes del release
Scripts/
  Core/        scr_config · scr_servicios · scr_registro · scr_migraciones
  Managers/    scr_gestor_audio · scr_gestor_config · scr_gestor_partida
  Systems/     scr_state_machine · scr_pool · scr_save_load · scr_senales · scr_camera
  Data/        scr_catalogo · scr_comandos · scr_repeticion
  Utils/       scr_matematicas · scr_dibujo_util
Sounds/      SFX/ · Music/
Fonts/ · Shaders/ · Tilesets/ · Notes/
```

### 4.2 El árbol en disco

```
mi-juego/
  .git/  ·  .gitignore  ·  .gitattributes      ← los dos últimos los genera el IDE
  .mcp.json                                    ← lo genera gm-cli init; el MCP es POR PROYECTO
  mi-juego.yyp                                 ← NO se edita a mano
  mi-juego.resource_order                      ← ignorado por Git
  objects/ · sprites/ · scripts/ · rooms/ · sounds/ · fonts/ · shaders/
  datafiles/          ← Included Files: enemigos.json, niveles.json, idiomas/es.json…
  notes/              ← decisiones de diseño en Markdown, versionadas con el código
  options/            ← ajustes por plataforma
  .github/workflows/  ← compile.yml y package.yml, los genera gm-cli init
```

### 4.3 Checklist de «arquitectura sana»

**Estructura** — [ ] subcarpetas por dominio dentro de cada tipo, **ningún nivel de más de tres**;
[ ] existe una carpeta `Test/` y una tarea pendiente de borrarla; [ ] los números de balance están
en `scr_config` o en un JSON, **nunca dentro de un evento**.

**Globales y dependencias** — [ ] `global.` aparece **solo** en `scr_servicios.gml`; [ ] ningún
objeto escribe `obj_otro.variable` desde fuera; [ ] el jugador no sabe que existe el HUD;
[ ] todo gestor tiene `serializar` / `restaurar` / `limpiar`.

**Capas** — [ ] en Draw **no se modifica** ninguna variable de estado; [ ] ningún struct de datos
contiene sprites, colores ni sonidos; [ ] ninguna función se define dentro de un Step o un Draw.

**Herencia** — [ ] ninguna jerarquía de objetos pasa de **dos niveles**; [ ] cada hijo llama a
`event_inherited()` en los eventos que hereda.

**Tiempo** — [ ] `game_set_speed(FPS_OBJETIVO, gamespeed_fps)` en el arranque; [ ] `room_speed` no
aparece en ninguna parte; [ ] la decisión frames-fijos / `delta_time` está tomada y escrita en
`notes/`.

**Persistencia** — [ ] el guardado tiene campo `version` y existe `partida_migrar`;
[ ] configuración, progreso y partida están en ficheros distintos; [ ] no se guarda ningún handle
de asset ni ID de instancia.

**Memoria** — [ ] todo lo que tiene `*_destroy`/`*_free`/`*_delete` se libera en **Clean Up**;
[ ] cada surface, buffer y `ds_*` tiene un dueño identificable.

**Git y build** — [ ] `.gitignore` y `.gitattributes` están en el repositorio; [ ] nadie ha editado
un `.yy` a mano; [ ] cada room tiene un responsable acordado; [ ] el proyecto **compila**
(`gm-cli compile`) antes de cada commit a la rama principal.

**Depuración** — [ ] hay capa de log con niveles filtrada por Config; [ ] hay aserciones en las
fronteras; [ ] cada sistema con estado tiene su `dbg_view`.

---

## 5 · Anti-patrones: los ocho de los proyectos que se atascan

| # | Anti-patrón | Por qué duele | Arreglo |
|---|---|---|---|
| 1 | **`global.` para todo** (`global.vida`, `global.puerta_abierta_3`) | Ninguna variable tiene dueño, nada se puede probar aislado, y dos sistemas escriben la misma variable en un orden que depende del `depth` | El localizador (§3.3). Migración gradual: busca `global.`, agrupa por sistema, un gestor por grupo |
| 2 | **El objeto dios** (`obj_game` con 900 líneas que sabe de vida, oleadas, música y menú) | Es el «Bjørn hinchado»: todo cambio toca el mismo archivo, dos personas no pueden trabajar a la vez, nada se prueba por separado | Un gestor por dominio (§3.2). El controlador solo crea, coordina y limpia |
| 3 | **Lógica en Draw** (`x += vel_x` en un evento de dibujado) | Los eventos de dibujado **pueden saltarse** al perder frames: el juego se comporta distinto según los FPS. El manual lo prohíbe explícitamente | Step decide, Draw pinta (§3.5) |
| 4 | **Código copiado entre objetos hermanos** | Cada corrección hay que hacerla tres veces, y a la cuarta se te olvida una | Familia → padre + `event_inherited()`. Capacidad suelta → struct compartido. Cálculo → función en `Scripts/` (§3.6) |
| 5 | **Alarmas encadenadas** (`alarm[0]` pone `alarm[1]`, que pone `alarm[2]`…) | La secuencia no se lee en ninguna parte y al pausar o cambiar de room queda a medias en un estado imposible | FSM si es comportamiento; **Time Source** o `call_later` si es solo tiempo ([01 · 06 §8](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md#8-time-sources-la-alternativa-moderna-a-los-alarm)) |
| 6 | **`room_goto` con estado suelto** | Cambiar de room destruye las instancias no persistentes: lo que no esté en un persistente se pierde **en silencio** | Ninguna room se cambia directamente: se pasa por la función de escena, que serializa antes de salir y restaura al entrar (§3.2 y [04 · 00 §2](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md#2--el-gestor-de-escenas--el-esqueleto-del-arco)) |
| 7 | **Definir funciones dentro de Step** | Se crea un método nuevo **cada frame** (60 objetos × 60 fps = 3 600 por segundo que el recolector debe limpiar) y el nombre no existe fuera del evento | Las funciones, en un script; los métodos atados a la instancia, en el **Create** |
| 8 | **Reimplementar en GML lo que el motor hace en C++** (colisiones propias, envoltorios OOP sobre arrays) | El runtime está en C++ y tu GML no: un envoltorio OOP sobre arrays puede ser **hasta 11 veces más lento**, y ahora mantienes dos sistemas | Arquitectura es decidir **quién llama a qué**, no reescribir el motor. Y **perfila antes de optimizar** ([01 · 15 §6](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#6-rendimiento-dónde-está-el-cuello-de-botella)). Única excepción documentada: el sistema de físicas integrado, que casi nadie usa (1 de 21) |

---

## 6 · Onboarding de un compañero nuevo

No es contenido nuevo: es el punto de entrada único que hoy no existe. Cada pieza de esta lista
ya está escrita en algún sitio de esta biblioteca o de un proyecto bien llevado; lo que faltaba
era el orden en que alguien que se incorpora debería leerlas. Dale esta lista —tal cual, o
convertida en un `ONBOARDING.md` del propio proyecto— a quien se una, sea un contratado de
[`13 · 11` §12](11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md#12--trabajar-con-otras-personas)
o un colaborador que se queda.

- [ ] **1. Lee el `CLAUDE.md`/`AGENTS.md` del proyecto** (o el equivalente que tenga) antes de
      tocar nada: son las reglas de ESE repositorio, y priman sobre cualquier convención general.
- [ ] **2. Lee este documento entero** (`13 · 06`), no solo esta sección — es el mapa de cómo
      está organizado el código: Asset Browser por dominio (§3.1), gestores y localizador (§3.2,
      §3.3), dónde va la lógica y dónde el dibujado (§3.5), datos dirigidos (§3.8).
- [ ] **3. Antes de la primera rama, entiende la disciplina de Git de §3.13**: por qué no se
      edita un `.yy`/`.yyp` a mano, qué hace `.gitattributes` con esos ficheros, y sobre todo
      **el reparto de rooms** — pregunta *ahora*, no después de un conflicto, quién es dueño de
      cada room que vayas a tocar.
- [ ] **4. Busca las decisiones ya tomadas antes de proponer una nueva**: la carpeta
      `decisiones/` del proyecto tiene un ADR por cada elección cara de revertir —formato de
      guardado, librería externa, estructura de las salas— ([`13 · 11` §3.5](11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md#35-registro-de-decisiones-adr-ligero)).
      Si tu duda ya tiene un ADR, léelo antes de volver a discutirla.
- [ ] **5. Lee el `DIARIO.md`** de las últimas semanas
      ([`13 · 11` §3.6](11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md#36-el-diario-de-desarrollo))
      si existe: tres líneas por sesión te dan más contexto real que una reunión de media hora.
- [ ] **6. Comprueba que compilas antes de escribir una línea**: `gm-cli compile --errors-only`
      contra el proyecto tal y como está, para descartar que un problema de entorno (toolchain,
      licencia) sea tuyo y no del código ([`13 · 10` §8.1](10%20-%20Testing%20y%20QA.md#81-la-puerta-obligatoria)).
- [ ] **7. Revisa las convenciones de nombres antes del primer commit**: `snake_case`, prefijos
      `obj_ spr_ snd_ rm_ scr_`, nada de nombres reservados —
      [`05 · 04`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md). Un PR que no
      las sigue es la revisión más tediosa de dar y de recibir.
- [ ] **8. Antes de crear algo, busca si ya existe**: `python3 "_indice/buscar.py" --codigo
      "<lo que sea>"` para ver cómo lo resuelve el resto del proyecto, y
      [`11 · Código descargado/_CATALOGO.md`](../11%20-%20Código%20descargado/_CATALOGO.md) para
      no reescribir una librería que el proyecto ya trae.
- [ ] **9. Pregunta quién es dueño de qué** si el equipo reparte por sistemas (audio, UI, IA):
      no está escrito en ningún sitio automáticamente — es la primera pregunta de una
      conversación, no un documento que se lea solo.

**Lo que esta lista no sustituye**: un README técnico propio del proyecto (cómo se instala el
toolchain, a quién preguntar) sigue sin tener plantilla en esta biblioteca — reconocido como hueco
abierto en la auditoría de herramientas y pipeline
(`_indice/auditorias/r3-herramientas-pipeline.md`, tema 87). Esta lista cubre el **orden de
lectura**; un README de instalación sigue siendo trabajo del proyecto concreto.

---

## Ver también

- [04 · 00 Anatomía de un juego completo](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md) — el arco de escenas que este documento presupone
- [04 · 16 Señales y desacoplamiento](../04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md) · [04 · 15 Game feel y juice](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md)
- [05 · 04 Convenciones y estilo GML](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) — prefijos, nombres reservados, JSDoc y aserciones
- [01 · 04 Structs y constructores](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) · [01 · 06 Eventos y ciclo del juego](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) · [01 · 09 Instancias, objetos y herencia](../01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md)
- [01 · 14 Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) · [01 · 15 Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md)
- [06 · Assets y Scripts](../06%20-%20Assets%20y%20Scripts/README.md) — FSM, pool, guardado, cámara y debug ya escritos
- [07 · 13 GM CLI](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20línea%20de%20comandos.md) · [07 · 15 Qué hacen de verdad los proyectos reales](../07%20-%20Ecosistema/15%20-%20Qué%20hacen%20de%20verdad%20los%20proyectos%20reales.md) · [07 · 17 SnowState](../07%20-%20Ecosistema/17%20-%20SnowState%20-%20máquinas%20de%20estado%20%28guía%20en%20español%29.md)
- [03 · 24 Control de versiones con Git](../03%20-%20Cursos%20%28YouTube%29/24%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Control%20de%20Versiones%20con%20Git.md)

---

## Fuentes

Todas consultadas el **6 de septiembre de 2026**.

**Robert Nystrom, *Game Programming Patterns*** — <https://gameprogrammingpatterns.com/contents.html>

- [Singleton](https://gameprogrammingpatterns.com/singleton.html) · el argumento de §3.3 contra la global encapsulada.
- [Service Locator](https://gameprogrammingpatterns.com/service-locator.html) · el registro por nombre, el «null service» y la advertencia sobre el acceso global.
- [Component](https://gameprogrammingpatterns.com/component.html) · el «Bjørn hinchado» y la composición por dominios de §3.6.
- [Game Loop](https://gameprogrammingpatterns.com/game-loop.html) · el acumulador de paso fijo y el determinismo de §3.9.
- *Command*, *State*, *Object Pool* y *Data Locality*, en el mismo dominio.

**Manual oficial de GameMaker LTS 2026** (espejo local en `09 - Manual oficial/`)

- [Buenas prácticas de programación](../09%20-%20Manual%20oficial/manual-lts-2026-es/Additional_Information/Best_Practices_When_Programming.md) — <https://manual.gamemaker.io/lts/es/Additional_Information/Best_Practices_When_Programming.htm> · «no pongas código que no sea para dibujar en los eventos Draw», el controlador que dibuja todas las balas, variables locales y copy-on-write en arrays.
- [Formato de proyecto](../09%20-%20Manual%20oficial/manual-lts-2026-es/Additional_Information/Project_Format.md) — <https://manual.gamemaker.io/lts/en/Additional_Information/Project_Format.htm> · el `.yyp`, los `.yy` «en un formato similar a JSON», el `.resource_order`, y qué hacen el `.gitignore` y el `.gitattributes` del IDE.
- [Configuraciones](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Configurations.md) · [Constantes y macros](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Overview/Variables/Constants.md) — el Editor de Configuración, la jerarquía de configs y la sintaxis `#macro Config:NOMBRE valor`.
- [Archivos incluidos](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Included_Files.md) · la carpeta `datafiles`, las plataformas por fichero y el choque de nombres con sonidos en streaming.
- [Paquetes locales de assets](../09%20-%20Manual%20oficial/manual-lts-2026-es/IDE_Tools/Local_Asset_Packages.md) · crear e importar (⚠️ la traducción española dice `.yymp`; la inglesa y la página de formato dicen `.yymps`).
- [Control de código fuente](../09%20-%20Manual%20oficial/manual-lts-2026-es/IDE_Tools/Source_Control.md) y su ventana de conflictos — <https://manual.gamemaker.io/beta/en/IDE_Tools/Source_Control/Conflicts.htm>.

**Blog oficial** — Gurpreet S. Matharoo, *Nine Simple Coding Tips When Coding With GameMaker*
(21-02-2023) — <https://gamemaker.io/en/blog/best-practices-when-coding-in-gamemaker-studio-2> ·
confirma y amplía la página del manual: estilo consistente y `#region`, variables locales (con
ventaja extra en YYC), `array_create` al tamaño máximo, structs y constructores frente a variables
sueltas, orden de coste de las colisiones y el `with (obj_BULLET) draw_self()` para no romper el
lote.

**Comunidad**

- Juju Adams, *ThoughtsOnGameMaker* — <https://github.com/JujuAdams/ThoughtsOnGameMaker> · `technique-2-singletons.md`, `technique-3-evacuation.md` y `code-reuse.md`, base de §3.3 y §3.15.
- Juju Adams, *painfully-learned-lessons* — <https://github.com/JujuAdams/painfully-learned-lessons> · `optimization.md`: perfila antes de optimizar y **nunca reimplementes sistemas nativos** (anti-patrón 8).
- Butterscotch Shenanigans, *gamemaker-info* — <https://github.com/bscotch/gamemaker-info/blob/develop/notes/gamemaker-projects.md> · el formato `.yyp`/`.yy` «JSON-ish» con comas finales e Int64, y por qué las carpetas del Asset Browser no existen en disco. Su herramienta: <https://github.com/bscotch/stitch>.
- YoYoGames, issue [#2922](https://github.com/YoYoGames/GameMaker-Bugs/issues/2922) · el contenido literal de la plantilla `.gitignore`/`.gitattributes` que hoy genera el IDE.
- Foro oficial, [*Conflict problem with git*](https://forum.gamemaker.io/index.php?threads/conflict-problem-with-git.105936/) (2023) · conflictos reales en `.yy`, Git externo y `fetch`+`rebase` frecuentes.
- Anchorpoint, [*GameMaker with GitHub*](https://www.anchorpoint.app/blog/github-and-gamemaker) (act. 02-2026) · el reparto en rama de programación y rama de diseño/arte.

**En esta biblioteca** — [07 · 15](../07%20-%20Ecosistema/15%20-%20Qué%20hacen%20de%20verdad%20los%20proyectos%20reales.md):
análisis de 21 proyectos y ~1,3 M de líneas de GML (20/21 con máquina de estados, 11/21 con
`delta_time`, 1/21 con el motor de físicas, `with` con 8 539 usos).

**Verificación de la API.** Todos los símbolos de GML de este documento se comprobaron con
`python3 "_indice/buscar.py" <símbolo>` contra el `GmlSpec.xml` del runtime **2026.0.0.23**
instalado. Ninguno está marcado como obsoleto ni como «solo en `fnames`».
