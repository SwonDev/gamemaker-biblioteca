# 53 · Souls-like — hoguera y pérdida de recursos al morir

> **Dificultad:** alta · **Antes de esto:** [`04 · 30 — Combate cuerpo a cuerpo`](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md)
> entero, y si tu combate usa habilidades con coste, también
> [`04 · 36 — Habilidades, enfriamientos y recursos de combate`](./36%20-%20Habilidades%2C%20enfriamientos%20y%20recursos%20de%20combate.md).
> Este documento **no repite ni una línea** de i-frames, esquiva, bloqueo, parry ni estamina:
> los reutiliza. Tampoco toca `04 · 06 — Metroidvania`; **extiende** su `WorldState` por
> composición, sin editar su archivo.
>
> **Qué cubre esto, y solo esto**: (a) el checkpoint que reinicia el mundo — la hoguera — y qué
> reinicia frente a qué es progreso permanente; (b) la pérdida y recuperación del recurso
> principal de la run al morir — la marca de muerte. **Qué NO cubre**: el *lock-on* de cámara
> sobre un enemigo objetivo vive en
> [`13 · 19 §3.12 — Lock-on-target`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/19%20-%20Cámaras%20de%20juego%20-%20encuadre%2C%20seguimiento%20y%20control.md#312-lock-on-target-bloquear-la-cámara-sobre-un-enemigo)
> (ver §3.10 de este documento); los i-frames y la esquiva viven en `04 · 30` §4.5; el bloqueo y
> el parry en `04 · 30` §4.6; la estamina como recurso de combate en `04 · 36` §3.2 y §3.6.

---

## 1 · Los principios

### 1.1 · Qué es un *souls-like*, y qué NO es este documento

Un *souls-like* no es un género de combate — es un género de **estructura de riesgo**. La
entrada de Wikipedia sobre el subgénero, consultada en vivo el **2026-09-07** (ver Fuentes), lo
resume así: *"Soulslike games typically have a high level of difficulty where repeated player
character death is expected and incorporated as part of the gameplay, with players often
keeping part of their progress [...] since the last checkpoint. Other losses (such as
experience or currency) are potentially recoverable"*. Traducido: la muerte no es un final, es
una **decisión de diseño repetible** — pierdes algo recuperable, no todo, y el juego te da
exactamente la oportunidad de recuperarlo si te atreves a volver.

La misma fuente describe la pieza central de este documento con una precisión que ahorra
ambigüedad: *"Many Soulslike games use checkpoint systems associated with the bonfires of Dark
Souls. These checkpoints typically serve as respawn or recovery points [...] while resting at
them may reset enemies [...] preserving a risk-and-reward structure around death, recovery, and
exploration"*. Eso es literalmente el §3.1 de este documento: descansar cura, pero **también**
reinicia el nivel — el riesgo-recompensa no es un extra, es el mecanismo.

Este documento construye **dos piezas y enlaza el resto**:

1. **La hoguera** (§3.1-§3.6): un checkpoint que cura al jugador y reinicia enemigos y recursos
   consumibles del nivel, sin tocar el progreso permanente.
2. **La marca de muerte** (§3.7-§3.9): al morir, el recurso principal de la run se deja caer en
   el sitio exacto de la muerte, recuperable — y perdido para siempre si mueres una segunda vez
   sin recogerlo.

No construye el combate (ya está en `04 · 30`/`04 · 36`), ni la cámara de combate (`13 · 19`),
ni jefes, ni narrativa ambiental, ni el *NG+*. Esos son otros documentos, y en algunos casos
huecos todavía sin receta propia en esta biblioteca.

### 1.2 · El triángulo de decisiones

| Decisión | Quién la resuelve | Dónde |
|---|---|---|
| ¿Puedo esquivar/bloquear/parrear este golpe? | `04 · 30` §4.5-§4.6 | *(no se repite aquí)* |
| ¿Con qué recurso pago la esquiva/la habilidad? | `04 · 36` §3.2, §3.6 (`estamina` como `RecursoCombate`) | *(no se repite aquí)* |
| ¿A qué enemigo apunta la cámara? | `13 · 19` §3.12 (*lock-on-target*, §3.10 de este documento) | *(no se repite aquí)* |
| **¿Qué pasa si pierdo, y qué pasa si vuelvo?** | **Este documento** | §3.1-§3.9 |

### 1.3 · Vocabulario nuevo

| Término | Qué es, en esta biblioteca |
|---|---|
| **Hoguera** (*bonfire* / checkpoint) | Punto de descanso: guarda la partida, cura al jugador y reinicia enemigos/recursos del nivel. «*Checkpoints [that] typically serve as respawn or recovery points [...] while resting at them may reset enemies*» (Wikipedia, *Soulslike*, consultado 2026-09-07). |
| **Alma** (recurso principal de la run) | La moneda de progresión que se gana matando/explorando y se gasta en mejoras permanentes — el nombre genérico de este documento para lo que Dark Souls llama *souls* y Bloodborne *blood echoes*: «*a type of currency that can be earned and spent but may be lost or abandoned between deaths if not properly managed*» (misma fuente). |
| **Marca de muerte** (*bloodstain*) | El recogible que aparece en el punto exacto de la muerte con las almas perdidas. Recuperable una vez; si mueres antes de recogerla, desaparece (§3.7). |
| **Reinicio del mundo** | Lo que hace la hoguera al descansar: destruye y repuebla enemigos y recursos consumibles del nivel — nunca las habilidades, mejoras o flags de historia (§3.1). |
| **Coste-beneficio de descansar** | La decisión de diseño central de una hoguera: curas gratis, pero el nivel que acabas de limpiar vuelve a estar lleno. No hay hoguera «solo para guardar» sin ese precio — si lo tuyo es guardar sin consecuencia, es un save point de `04 · 06`, no una hoguera. |

### 1.4 · El mapa de este documento

```
1. Principios          → qué es un souls-like y qué NO construye este documento
2. El método            → orden para implementar hoguera y marca de muerte sin romper 04 · 06
3. GameMaker             3.1  Qué reinicia una hoguera, y qué no (la tabla que lo decide todo)
                          3.2  Extender WorldState por composición
                          3.3  Registrar y reiniciar spawns (función genérica, reutilizada 2 veces)
                          3.4  Los marcadores de spawn
                          3.5  Notificar el propio consumo (enemigo muerto / recurso recogido)
                          3.6  obj_hoguera: descansar de verdad
                          3.7  La marca de muerte: struct y la regla de "una sola marca"
                          3.7b La variante con temporizador (corpse run de EverQuest)
                          3.8  El recogible: obj_marca_muerte
                          3.9  Enganchar la muerte del jugador
                          3.10 Lo que NO se repite aquí, con sus enlaces exactos
4. Checklist
5. Errores clásicos
```

---

## 2 · El método, paso a paso

```
1. Ten 04 · 30 (combate) funcionando: golpear, morir, EstadoCombate.tick(). Sin esto no hay
   "al morir" al que enganchar nada.
2. Extiende WorldState (§3.2) — una función, cero cambios en 04 · 06.
3. Los marcadores de spawn (§3.4) ANTES que la hoguera: sin ellos, hoguera_descansar() no
   tiene de dónde repoblar. Pruébalos solos: entra y sal de una sala, confirma que los
   enemigos vuelven cada vez (comportamiento normal de GameMaker, todavía sin hoguera).
4. obj_hoguera (§3.6): descansar cura y reinicia. Prueba el coste-beneficio con los ojos
   abiertos — mata todo, descansa, confirma que vuelve.
5. La marca de muerte (§3.7-§3.8) es independiente de la hoguera: no la toques hasta que el
   paso 4 funcione, así sabes que un fallo en la marca no es en realidad un fallo del reinicio.
6. Engancha ambas al "morir" del jugador (§3.9) en el orden exacto: crear la marca (necesita
   la posición de la muerte) ANTES de moverlo (player_respawn() cambia esa posición).
```

---

## 3 · Cómo se traduce a GameMaker

### 3.0 · Dónde vive cada cosa

| Pieza | Vive en | Se inicializa en |
|---|---|---|
| `WorldState` (habilidades, flags, punto de guardado) | `04 · 06` §5.0, reutilizado tal cual | El arranque del juego, como ya hace `04 · 06` |
| `spawns_enemigos` / `recursos_consumibles` | Extensión de `WorldState`, §3.2 de este documento | `mundo_extender_hoguera()`, junto al `new WorldState()` |
| `global.almas` | Este documento, un `Real` — no un `RecursoCombate` de `04 · 36`: no tiene enfriamiento ni regeneración, es una cuenta que solo cambia por eventos | Arranque del juego |
| `global.marca_muerte` | Este documento, `undefined` o un struct | Arranque del juego |

```gml
// ---------------------------------------------------------------------------
// obj_controlador_juego — Create (persistente, o el punto de arranque que ya
// use tu proyecto para inicializar global.world, 04 · 06 §5.0)
// ---------------------------------------------------------------------------
global.world = mundo_extender_hoguera(new WorldState());   // §3.2 — 04 · 06 + esta extensión

global.almas        = 0;            // recurso principal de la run (§1.3)
global.marca_muerte = undefined;    // sin marca todavía (§3.7)
```

### 3.1 · Qué reinicia una hoguera, y qué NO

Esta tabla es la decisión de diseño central del documento — todo el código de abajo existe
para hacerla cumplir sin excepciones:

| Se reinicia al descansar | Vive en | NO se reinicia (progreso permanente) | Vive en |
|---|---|---|---|
| Enemigos del nivel (mueren → vuelven) | `spawns_enemigos`, §3.2-§3.3 | Habilidades desbloqueadas | `WorldState.habilidades`, `04 · 06` §5.0 |
| Recursos consumibles del nivel (pociones, plantas, cofres del propio nivel) | `recursos_consumibles`, §3.2-§3.3 | Mejoras compradas / mejoras de arma | Lo que tu proyecto use para inventario permanente — fuera del alcance de este documento |
| — | — | Flags de historia (bosses derrotados, puertas abiertas) | `WorldState.flags`, `04 · 06` §5.0 |
| — | — | Salas visitadas (para el mapa) | `WorldState.salas_visitadas`, `04 · 06` §5.0 |
| — | — | El punto de guardado en sí (se sobrescribe al volver a descansar, pero persiste hasta entonces) | `WorldState.save_room/save_x/save_y`, `04 · 06` §5.0 |

`hoguera_reiniciar_mapa()` (§3.3) solo toca los dos campos nuevos de la izquierda. No llama a
`otorgar()`, no toca `flags`, no toca `salas_visitadas`: literalmente no tiene acceso a esos
campos porque recibe como argumento el mapa concreto sobre el que debe trabajar, no la
`WorldState` entera. Es una restricción de la firma, no una promesa de comentario.

### 3.2 · Extender `WorldState` por composición, sin tocar `04 · 06`

Los structs de GML aceptan campos nuevos en caliente — `variable_struct_exists()` y la
asignación directa (`_struct.campo = valor`) son las mismas dos piezas que
[`01 · 04 — Structs y constructores`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md)
usa para explicar por qué structs y arrays son por referencia. Eso es lo único que hace falta
para "ampliar" `WorldState` sin abrir su archivo: el mismo patrón exacto que
[`04 · 47` §4.2](./47%20-%20Beat%20em%20up%20y%20brawler.md#42--extender-la-tabla-de-ataques-de-04--30-sin-tocar-el-documento)
usa para añadir entradas a `global.ataques` sin tocar `04 · 30`.

```gml
// ---------------------------------------------------------------------------
// scr_hoguera_mundo
// Verificado: variable_struct_exists
// ---------------------------------------------------------------------------

/// @func mundo_extender_hoguera(_world)
/// @desc Añade a una instancia YA CREADA de WorldState (04 · 06 §5.0) los dos
///       campos que este documento necesita. Idempotente y segura sobre saves
///       antiguos: si el campo ya existe (por ejemplo al deserializar un save
///       hecho con esta misma extensión), no lo pisa.
/// @param {Struct.WorldState} _world
/// @returns {Struct.WorldState} la misma instancia, ya extendida
function mundo_extender_hoguera(_world)
{
    if (!variable_struct_exists(_world, "spawns_enemigos"))
    {
        _world.spawns_enemigos = {};        // room_id (String) -> array de PuntoSpawn
    }
    if (!variable_struct_exists(_world, "recursos_consumibles"))
    {
        _world.recursos_consumibles = {};   // room_id (String) -> array de PuntoSpawn
    }
    return _world;
}
```

Cada `PuntoSpawn` es un struct plano `{ tipo, pos_x, pos_y, consumido }` — `tipo` es el
**nombre** del object asset como string (`"obj_esqueleto"`, no el índice), exactamente el
mismo patrón que `04 · 06` §5.0 usa para `save_room` (guarda el string, resuelve con
`asset_get_index()` al usarlo). La razón es la misma: un índice de object asset es un *handle*
en 2026, y guardar el string es lo que sobrevive a un `json_stringify()`/`json_parse()` si algún
día extiendes el guardado a disco (ver el aviso ⚠️ justo debajo).

> ⚠️ **Persistencia a disco de `spawns_enemigos`/`recursos_consumibles`.** Este documento no
> los añade a `WorldState.serialize()`/`deserialize()` (04 · 06 §5.0): son estado de la sesión
> en curso, no progreso que sobreviva a cerrar el juego. Si tu proyecto necesita que el estado
> "qué está muerto" persista entre partidas, el struct ya es JSON-serializable tal cual —
> añadir dos líneas a `serialize()`/`deserialize()` (04 · 06 §5.0) es todo lo que hace falta;
> no se implementa aquí porque no lo pide el encargo, y añadirlo sin que se use sería relleno.

### 3.3 · Registrar y reiniciar spawns: la función genérica

Dos mapas (`spawns_enemigos`, `recursos_consumibles`) con la misma forma necesitan la misma
lógica de registro y reinicio. En vez de escribirla dos veces, una sola función recibe el mapa
por referencia — structs y arrays son por referencia en GML
([`01 · 04`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md)) —
y edita directamente el campo de `WorldState` que le pases, sin que la función sepa cuál de los
dos es.

```gml
// ---------------------------------------------------------------------------
// scr_hoguera_spawns
// Verificado: variable_struct_exists, array_push, array_length,
//             variable_struct_get_names, asset_get_index, instance_create_layer
// ---------------------------------------------------------------------------

/// @func hoguera_registrar_punto(_mapa, _room_id, _tipo, _pos_x, _pos_y)
/// @desc Registra un punto de spawn la PRIMERA vez que se visita su sala. Si
///       ya existe una entrada idéntica (mismo tipo, misma posición — los
///       marcadores del Room Editor no se mueven entre visitas), devuelve su
///       índice sin duplicar. Es lo que llama cada obj_spawn_* en su Create
///       (§3.4): entrar y salir de la sala varias veces NO crea filas nuevas.
/// @param {Struct} _mapa      global.world.spawns_enemigos o .recursos_consumibles
/// @param {String} _room_id   global.room_id (04 · 06 §2)
/// @param {String} _tipo      Nombre del object asset, ej. "obj_esqueleto"
/// @param {Real}   _pos_x
/// @param {Real}   _pos_y
/// @returns {Real} índice del punto dentro de la lista de su sala
function hoguera_registrar_punto(_mapa, _room_id, _tipo, _pos_x, _pos_y)
{
    if (!variable_struct_exists(_mapa, _room_id))
    {
        _mapa[$ _room_id] = [];
    }

    var _lista = _mapa[$ _room_id];
    for (var _i = 0; _i < array_length(_lista); _i++)
    {
        if (_lista[_i].tipo == _tipo
        &&  _lista[_i].pos_x == _pos_x
        &&  _lista[_i].pos_y == _pos_y)
        {
            return _i;
        }
    }

    array_push(_lista, { tipo : _tipo, pos_x : _pos_x, pos_y : _pos_y, consumido : false });
    return array_length(_lista) - 1;
}

/// @func hoguera_marcar_consumido(_mapa, _room_id, _indice)
/// @desc Marca un punto como "ya no está" — un enemigo que acaba de morir o
///       un recurso que se acaba de recoger/agotar. El nombre del campo
///       (consumido) es el mismo para los dos mapas a propósito: para este
///       sistema, un enemigo muerto y una poción recogida son el mismo
///       hecho — "esta entrada no vuelve a poblarse hasta la próxima hoguera".
function hoguera_marcar_consumido(_mapa, _room_id, _indice)
{
    var _lista = _mapa[$ _room_id];
    if (_lista == undefined) return;
    if (_indice < 0 || _indice >= array_length(_lista)) return;

    _lista[_indice].consumido = true;
}

/// @func hoguera_reiniciar_mapa(_mapa, _obj_padre)
/// @desc El cuerpo compartido de "reiniciar enemigos" y "reiniciar recursos"
///       (§3.6): limpia "consumido" en TODAS las salas conocidas del mapa —
///       no solo la actual, porque un souls-like repuebla el mundo entero al
///       descansar, no solo la habitación donde estás — y, para la sala
///       ACTUAL, destruye lo que sigue vivo y lo vuelve a crear desde los
///       datos de spawn. Las demás salas se repueblan solas la próxima vez
///       que el jugador entra en ellas: obj_spawn_* (§3.4) vuelve a leer
///       "consumido" en su propio Create, y ahora está en false.
/// @param {Struct} _mapa               global.world.spawns_enemigos o .recursos_consumibles
/// @param {Asset.GMObject} _obj_padre  obj_enemigo u obj_recurso_nivel (§3.5)
function hoguera_reiniciar_mapa(_mapa, _obj_padre)
{
    var _salas = variable_struct_get_names(_mapa);
    for (var _s = 0; _s < array_length(_salas); _s++)
    {
        var _lista = _mapa[$ _salas[_s]];
        for (var _i = 0; _i < array_length(_lista); _i++)
        {
            _lista[_i].consumido = false;
        }
    }

    with (_obj_padre) { instance_destroy(); }

    var _lista_actual = _mapa[$ global.room_id];
    if (_lista_actual == undefined) exit;

    for (var _i = 0; _i < array_length(_lista_actual); _i++)
    {
        var _pt = _lista_actual[_i];
        instance_create_layer(_pt.pos_x, _pt.pos_y, "Instancias", asset_get_index(_pt.tipo), {
            hoguera_mapa    : _mapa,   // referencia por struct — 01 · 04
            hoguera_room_id : global.room_id,
            hoguera_indice  : _i
        });
    }
}
```

> 🔺 **`with (_obj_padre) { instance_destroy(); }` solo destruye lo que está VIVO en la sala
> actual.** En GameMaker las instancias de otras salas no existen en la lista de instancias
> mientras no estás en ellas — no hace falta (ni se puede) destruir lo que no está cargado. Por
> eso limpiar `consumido` en las demás salas es suficiente: se repueblan solas al entrar.

### 3.4 · Los marcadores de spawn

Un marcador es un objeto ligero, colocado en el Room Editor, que **no es** el enemigo o el
recurso — solo dice dónde y de qué tipo. Es el mismo patrón "marcador + objeto real" que ya usa
[`04 · 47` §5.1](./47%20-%20Beat%20em%20up%20y%20brawler.md#51--la-arena-como-zona-de-cámara-reutilizada)
con `obj_arena_trigger`.

```gml
// ---------------------------------------------------------------------------
// obj_spawn_enemigo — Create
// Variable de instancia "tipo_enemigo" (String) asignada por marcador en el
// Room Editor, ej. "obj_esqueleto" o "obj_arquero"
// ---------------------------------------------------------------------------
var _indice = hoguera_registrar_punto(global.world.spawns_enemigos, global.room_id,
                                       tipo_enemigo, x, y);
var _spawn  = global.world.spawns_enemigos[$ global.room_id][_indice];

if (!_spawn.consumido)
{
    instance_create_layer(x, y, "Instancias", asset_get_index(tipo_enemigo), {
        hoguera_mapa    : global.world.spawns_enemigos,
        hoguera_room_id : global.room_id,
        hoguera_indice  : _indice
    });
}

instance_destroy();   // el marcador ya cumplió su función: no necesita sobrevivir al Step
```

```gml
// ---------------------------------------------------------------------------
// obj_spawn_recurso — Create
// Idéntico a obj_spawn_enemigo, con "recursos_consumibles" en vez de
// "spawns_enemigos" y "tipo_recurso" en vez de "tipo_enemigo" (ej.
// "obj_pocion_curacion", "obj_cofre_nivel")
// ---------------------------------------------------------------------------
var _indice = hoguera_registrar_punto(global.world.recursos_consumibles, global.room_id,
                                       tipo_recurso, x, y);
var _spawn  = global.world.recursos_consumibles[$ global.room_id][_indice];

if (!_spawn.consumido)
{
    instance_create_layer(x, y, "Instancias", asset_get_index(tipo_recurso), {
        hoguera_mapa    : global.world.recursos_consumibles,
        hoguera_room_id : global.room_id,
        hoguera_indice  : _indice
    });
}

instance_destroy();
```

### 3.5 · Notificar el propio consumo

El enemigo real y el recurso real reciben tres variables de instancia (`hoguera_mapa`,
`hoguera_room_id`, `hoguera_indice`) a través del `var_struct` de `instance_create_layer()`
(§3.4) — el mismo mecanismo con el que `04 · 47` §5.1 enlaza `obj_arena_trigger` con su muro.
Solo hace falta comprobar que existen (un enemigo creado a mano, o un jefe sin marcador, no las
tiene) y avisar a la hoguera cuando cada uno desaparece:

```gml
// obj_enemigo — al morir (el mismo hook conceptual que 04 · 33 anota como
// "obj_enemigo · al morir": donde 04 · 30 §6 hace fsm.set("muerto") al llegar
// combate.vida <= 0. Aquí solo se añade la notificación a la hoguera)
if (variable_instance_exists(id, "hoguera_mapa"))
{
    hoguera_marcar_consumido(hoguera_mapa, hoguera_room_id, hoguera_indice);
}
```

```gml
// obj_recurso_nivel — al recogerse o agotarse (el punto exacto depende de tu
// recurso: una poción se recoge al tocarla, un cofre se agota al abrirse)
if (variable_instance_exists(id, "hoguera_mapa"))
{
    hoguera_marcar_consumido(hoguera_mapa, hoguera_room_id, hoguera_indice);
}
```

> 🔺 **`variable_instance_exists(id, "hoguera_mapa")`, no `hoguera_mapa != undefined`.** Si la
> variable de instancia no existe (un enemigo creado sin pasar por `obj_spawn_enemigo`, por
> ejemplo un jefe único), leerla directamente lanza un error de variable inexistente en vez de
> devolver `undefined`. `variable_instance_exists()` es la comprobación segura — el mismo motivo
> por el que `04 · 06` §5.0 usa `variable_struct_exists()` antes de leer un campo que podría no
> estar.

### 3.6 · `obj_hoguera`: descansar de verdad

```gml
// ---------------------------------------------------------------------------
// scr_hoguera_descansar
// Verificado: audio_play_sound
// ---------------------------------------------------------------------------

/// @func hoguera_descansar()
/// @desc Lo que ocurre al descansar: guarda el punto de guardado (04 · 06
///       §5.0, TAL CUAL — no se repite su código), cura al jugador, y
///       reinicia enemigos y recursos consumibles del nivel (§3.1, §3.3). NO
///       toca la marca de muerte (§3.7): descansar no la hace desaparecer ni
///       la recupera — solo una recogida real (§3.8) o una segunda muerte
///       encima de ella la mueven.
function hoguera_descansar()
{
    global.world.guardar_punto(global.room_id, x, y);      // 04 · 06 §5.0, reutilizado
    global.player_stats.hp = global.player_stats.hp_max;   // curar — mismo patrón que objSavePoint, 04 · 06 §5.7

    hoguera_reiniciar_mapa(global.world.spawns_enemigos,      obj_enemigo);       // §3.3
    hoguera_reiniciar_mapa(global.world.recursos_consumibles, obj_recurso_nivel); // §3.3

    audio_play_sound(snd_hoguera_descansar, 10, false);
    fx_floating_text(x, y - 24, "Descansado", c_white);   // 04 · 15 §5.6
    fx_flash(c_white, 0.12, 10);                           // 04 · 15 §5.6
}
```

```gml
// ---------------------------------------------------------------------------
// obj_hoguera — Step
// Descansar es una decisión del jugador, no algo automático al tocar la
// hoguera (a diferencia de objSavePoint en 04 · 06 §5.7, que sí es
// automático): en un souls-like, reiniciar el nivel tiene coste, y un coste
// no debería activarse por caminar cerca sin querer.
// ---------------------------------------------------------------------------
if (place_meeting(x, y, obj_jugador) && keyboard_check_pressed(ord("E")))
{
    hoguera_descansar();
}
```

### 3.7 · La marca de muerte: struct y la regla de "una sola marca"

```gml
// ---------------------------------------------------------------------------
// scr_marca_muerte
// ---------------------------------------------------------------------------

/// @func marca_muerte_crear()
/// @desc Se llama UNA vez, en el instante exacto de morir (§3.9) — ANTES de
///       mover al jugador de vuelta a la hoguera. Guarda dónde y cuánto, y
///       crea el recogible en la sala actual.
///
///       DECISIÓN DE DISEÑO EXPLÍCITA — UNA SOLA MARCA A LA VEZ (como Dark
///       Souls y Elden Ring, no como Hollow Knight, que permite varias): si
///       ya había una marca sin recoger de una muerte anterior, la marca
///       NUEVA la SUSTITUYE. Las almas de la marca vieja se pierden para
///       siempre — no se suman a la nueva, no se acumulan en ningún sitio.
///       Si tu diseño prefiere que varias marcas coexistan, cambia
///       global.marca_muerte (singular) por un array global.marcas_muerte
///       (plural) con array_push() en vez de la asignación de abajo, y
///       adapta obj_marca_muerte (§3.8) para que cada instancia recuerde su
///       propio índice en ese array en vez de un struct único — el resto del
///       sistema (registro por sala, recogida, reinicio) no cambia.
function marca_muerte_crear()
{
    // La marca anterior, si la había y no se llegó a recoger, desaparece
    // aquí. Solo puede haber una instancia viva de obj_marca_muerte a la vez
    // en la sala donde estaba: si esa sala es la actual, se destruye; si era
    // otra sala, no hay instancia viva que destruir (no está cargada), y
    // sobrescribir global.marca_muerte (más abajo) ya la deja sin referencia.
    with (obj_marca_muerte) { instance_destroy(); }

    global.marca_muerte = {
        room_id  : global.room_id,
        pos_x    : x,
        pos_y    : y,
        cantidad : global.almas
    };

    global.almas = 0;   // se pierden AQUÍ; la recogida (§3.8) es lo único que las devuelve

    instance_create_layer(x, y, "Instancias", obj_marca_muerte, {
        cantidad : global.marca_muerte.cantidad
    });
}
```

```gml
// ---------------------------------------------------------------------------
// obj_gestor_marca_muerte — Room Start (una instancia persistente basta: el
// mismo objeto puede vivir en la primera room y sobrevivir a los cambios de
// room, o puedes colocar una instancia normal en cada room — cualquiera de
// las dos formas dispara el evento Room Start al entrar)
// Reconstruye el recogible si la marca pendiente pertenece a ESTA sala —
// necesario porque obj_marca_muerte es una instancia en tiempo de ejecución,
// no algo colocado en el Room Editor: si el jugador sale de la sala sin
// recogerla y vuelve, GameMaker no la recrea solo.
// ---------------------------------------------------------------------------
if (global.marca_muerte != undefined && global.marca_muerte.room_id == global.room_id)
{
    instance_create_layer(global.marca_muerte.pos_x, global.marca_muerte.pos_y, "Instancias",
        obj_marca_muerte, { cantidad : global.marca_muerte.cantidad });
}
```

### 3.7 bis · La variante con temporizador (*corpse run* de EverQuest)

La regla de §3.7 —«una sola marca, la segunda muerte la borra»— es el patrón de Dark
Souls/Elden Ring: **sin presión de tiempo**, solo presión de riesgo (si mueres otra vez antes de
volver, la pierdes). *EverQuest* (1999) resuelve la misma pregunta de diseño —¿qué le pasa a lo
que dejaste caer si tardas en volver?— con un mecanismo distinto: el cadáver **decae solo**,
pasado un tiempo, sin que haga falta una segunda muerte. Los tiempos reales verificados
(`WebSearch`, 2026-09-07; fuente en Fuentes): *"Decay is 30 minutes for level 1, 2 hours for
levels 2-4, and 7 days for level 5 and above [...] the online corpse timer is 3 hours and the
offline corpse timer is 7 days"* — es decir, dos temporizadores independientes (uno mientras
juegas, otro mientras estás desconectado), ninguno de los dos ligado a una segunda muerte.

Sobre la misma `global.marca_muerte` de §3.7, la variante añade un campo y una cuenta atrás:

```gml
// ---------------------------------------------------------------------------
// marca_muerte_crear() — AÑADIDO opcional sobre §3.7: si tu proyecto quiere
// la variante con temporizador en vez de (o además de) "la segunda muerte la
// borra", añade esta línea al struct que ya crea esa función:
// ---------------------------------------------------------------------------
global.marca_muerte = {
    room_id  : global.room_id,
    pos_x    : x,
    pos_y    : y,
    cantidad : global.almas,
    frames_restantes : MARCA_MUERTE_DURACION_FRAMES   // NUEVO — undefined = sin temporizador
};
```

```gml
// ---------------------------------------------------------------------------
// scr_config — nueva constante para esta variante
// ---------------------------------------------------------------------------
#macro MARCA_MUERTE_DURACION_FRAMES (60 * 60 * 5)   // 5 minutos a 60 fps; EverQuest usa horas,
                                                      // pero un checkpoint de nivel corto pide
                                                      // una ventana bastante más corta
```

```gml
// ---------------------------------------------------------------------------
// obj_marca_muerte — Step. AÑADIDO al bloque de §3.8: la cuenta atrás va
// ANTES de la comprobación de recogida, en la misma instancia, sin un
// objeto ni un evento aparte.
// ---------------------------------------------------------------------------
if (!is_undefined(global.marca_muerte.frames_restantes))
{
    global.marca_muerte.frames_restantes--;
    if (global.marca_muerte.frames_restantes <= 0)
    {
        global.marca_muerte = undefined;   // las almas se pierden para siempre: no llegaste a tiempo
        instance_destroy();
        exit;
    }
}
```

> ⚠️ **Elige una de las dos reglas, no las mezcles sin querer.** «La segunda muerte la borra»
> (§3.7) y «el tiempo la borra» (aquí) son respuestas **distintas** a la misma pregunta de
> diseño, y combinarlas sin pensarlo (la marca desaparece por lo que ocurra primero) es válido
> —de hecho es lo que hace EverQuest con sus dos temporizadores— pero debe ser una decisión
> explícita, documentada en la ficha de diseño del proyecto, no un accidente de copiar ambos
> bloques de código.

**La crítica de diseño, con las dos caras verificadas.** No es una mecánica sin controversia:
la discusión de la comunidad sobre *corpse runs* en juegos modernos (Valheim, Enshrouded) los
describe como una mecánica que castiga sobre todo el **tiempo**, no la **cautela** —«*it's just a
loss of time [...] doesn't add difficulty, you just lose time running in a straight line*» (foros
de Steam, resumido por `WebSearch`, 2026-09-07)—, y la industria los ha ido retirando por eso.
Pero el propio Raph Koster (diseñador de *Star Wars Galaxies*, *A Theory of Fun*) matiza en su
blog que el problema no es la mecánica en sí sino cómo se trasladó de los MUD de texto (donde
*"corpse runs were a powerful social force, creating a mutual need and indebtedness that brought
people together"*) a mundos 3D sin los mismos mecanismos compensatorios — el fallo, según él, es
de implementación, no de concepto (`WebFetch`, 2026-09-07; fuente en Fuentes). Documenta esto en
tu propia ficha de diseño antes de elegir esta variante: un temporizador sin ninguna
compensación social o mecánica (un aviso, un mapa que marca el sitio, la posibilidad de pedir
ayuda) es exactamente el caso que la crítica señala como el peor.

### 3.8 · El recogible: `obj_marca_muerte`

```gml
// ---------------------------------------------------------------------------
// obj_marca_muerte — Create
// ---------------------------------------------------------------------------
cantidad = 0;   // el valor real llega por var_struct al crearse (§3.7)
```

```gml
// ---------------------------------------------------------------------------
// obj_marca_muerte — Step
// ---------------------------------------------------------------------------
if (place_meeting(x, y, obj_jugador))
{
    global.almas        += cantidad;
    global.marca_muerte  = undefined;   // ya no hay marca pendiente: la próxima muerte no sustituye nada

    audio_play_sound(snd_recoger_marca, 10, false);
    fx_floating_text(x, y - 20, "+" + string(cantidad) + " almas", c_yellow);   // 04 · 15 §5.6

    instance_destroy();
}
```

### 3.9 · Enganchar la muerte del jugador

El orden importa: la marca necesita la posición de la muerte, y `player_respawn()` la borra al
mover al jugador. Crear la marca **antes** de llamar a `player_respawn()` no es una preferencia
de estilo, es la única forma de que `x`/`y` en `marca_muerte_crear()` (§3.7) sean el sitio
donde el jugador murió y no el sitio donde acaba de reaparecer.

```gml
// obj_jugador — al entrar en el estado "muerto" (el mismo punto que 04 · 30
// §6 dispara con fsm.set("muerto") cuando combate.vida <= 0 — scr_state_machine.gml,
// 06 - Assets y Scripts)
marca_muerte_crear();   // §3.7 — PRIMERO: necesita el x/y de la muerte, no el del respawn
player_respawn();       // 04 · 06 §5.7, TAL CUAL — vuelve al último punto de guardado,
                         // NUNCA a donde murió
```

`player_respawn()` no cambia ni una línea respecto a `04 · 06` §5.7: cura al jugador con
`global.player_stats.hp_max` y hace `room_goto()` a `_w.save_room` (o a `rm_start` si nunca se
descansó). Este documento no lo repite — solo lo llama, en el orden correcto.

### 3.10 · Lo que este documento NO repite, y dónde está de verdad

| Necesitas | Está en | Qué NO hagas aquí |
|---|---|---|
| I-frames y esquiva (invulnerabilidad temporal al esquivar) | [`04 · 30` §4.5](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md#45-i-frames-y-esquiva) | No reimplementes `iframes`/`esquiva_frame` — ya están en `EstadoCombate` |
| Bloqueo y parry | [`04 · 30` §4.6](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md#46-bloqueo-y-parry) | No inventes una segunda ventana de parry: `combate.parry` ya existe |
| Estamina como recurso que paga la esquiva | [`04 · 36` §3.2](./36%20-%20Habilidades%2C%20enfriamientos%20y%20recursos%20de%20combate.md#32-recursocombate-el-pool-genérico-y-sus-tres-variantes) (`RecursoCombate`) y [§3.6](./36%20-%20Habilidades%2C%20enfriamientos%20y%20recursos%20de%20combate.md#36-enganchar-el-coste-de-estamina-a-la-esquiva-que-ya-existe-en-04--30) (el enganche ya hecho) | No crees un segundo pool de estamina — `estamina : new RecursoCombate(100, 0.55, 45)` ya es «regenerativo rápido con techo bajo», el arquetipo correcto para souls-like (`04 · 36` §1.6) |
| Aguante / super armor de un enemigo grande | [`04 · 30` §4.7](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md#47-aguante-poise--super-armor) | Útil para un mini-jefe souls-like; no se repite |
| ***Lock-on-target*: cámara y movimiento enganchados al enemigo objetivo** | [`13 · 19` §3.12](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/19%20-%20Cámaras%20de%20juego%20-%20encuadre%2C%20seguimiento%20y%20control.md#312-lock-on-target-bloquear-la-cámara-sobre-un-enemigo) | Este documento **no** implementa el *lock-on*: es un sistema de cámara y de eje "adelante" del jugador, no de mundo/combate persistente — vive junto al resto de técnicas de encuadre de `13 · 19`, no aquí |

> ✅ **Sobre el enlace a `13 · 19` §3.12.** Cuando se empezó a escribir este documento, el
> *lock-on* estaba siendo añadido a `13 · 19` en paralelo, en un trabajo distinto sobre esta
> misma biblioteca, y todavía no existía una subsección con número propio. Para cuando este
> documento se terminó, `13 · 19` §3.12 — *Lock-on-target: bloquear la cámara sobre un
> enemigo* — ya existía, con el término `lock-on-target` en la tabla de su §1.3, y ese es el
> enlace de arriba: una sección real, no el archivo entero a ciegas. `13 · 19` §3.12 enlaza de
> vuelta a este documento para la parte de riesgo/recursos/muerte del *lock-on* como mecánica de
> combate — la cámara y el movimiento son suyos; los recursos que se pierden al morir son de
> aquí.

---

## 4 · Checklist

- [ ] `04 · 30` (combate) funciona de punta a punta ANTES de tocar este documento: golpear,
      recibir daño, morir, `EstadoCombate.tick()`.
- [ ] `mundo_extender_hoguera()` se llama UNA vez, junto al `new WorldState()` de tu proyecto —
      no en cada room (§3.0, §3.2).
- [ ] `spawns_enemigos`/`recursos_consumibles` son campos de `WorldState`, NO structs nuevos
      sueltos en `global.*` — así viajan con el resto del progreso si algún día los guardas
      (§3.2).
- [ ] Cada `obj_spawn_enemigo`/`obj_spawn_recurso` tiene su `tipo_*` asignado en el Room
      Editor, con el nombre EXACTO del object asset (§3.4).
- [ ] `hoguera_registrar_punto()` no duplica filas al reentrar en una sala — pruébalo antes de
      seguir (§3.3).
- [ ] `with (obj_enemigo) { instance_destroy(); }` en `hoguera_reiniciar_mapa()` usa el objeto
      PADRE de todos los enemigos (`04 · 30` §2.1), no un objeto concreto — si tienes tres tipos
      de enemigo con tres padres distintos, llama a `hoguera_reiniciar_mapa()` una vez por cada
      uno, con el mismo mapa (§3.3, §3.6).
- [ ] `hoguera_descansar()` cura, guarda Y reinicia — las tres cosas, no solo una (§3.6).
- [ ] Descansar es una acción explícita del jugador (botón), no automática al tocar la hoguera
      (§3.6) — el coste-beneficio exige que sea una decisión, no un accidente.
- [ ] Solo existe UNA `global.marca_muerte` a la vez, y una muerte encima de una marca sin
      recoger la sustituye — verificado con las almas viejas realmente perdidas, no sumadas
      (§3.7).
- [ ] `marca_muerte_crear()` se llama ANTES de `player_respawn()`, nunca después (§3.9).
- [ ] Al recoger la marca, `global.marca_muerte` vuelve a `undefined` — si no, la siguiente
      muerte cree que hay una marca que sustituir cuando ya no existe (§3.8).
- [ ] `obj_gestor_marca_muerte` reconstruye el recogible al reentrar en la sala donde quedó
      pendiente — probado saliendo y volviendo sin recogerla (§3.7).
- [ ] Si usas la variante con temporizador (§3.7 bis), la elección de «segunda muerte» / «tiempo»
      / «lo que ocurra primero» está documentada en la ficha de diseño del proyecto, no decidida
      por accidente al copiar código de los dos sitios.
- [ ] El *lock-on* NO está en este documento: si lo necesitas, va en `13 · 19` §3.12 (§3.10).

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Reimplementar i-frames, esquiva, bloqueo o parry «a medida» del souls-like | El doble de código para el mismo problema, y los dos sistemas divergen con el tiempo | Usa `EstadoCombate` de `04 · 30` §6 tal cual — es exactamente lo que un souls-like necesita, no una versión reducida |
| Un segundo pool de estamina propio de este documento | Dos fuentes de verdad sobre cuánta estamina tiene el jugador, que se desincronizan | `estamina : new RecursoCombate(100, 0.55, 45)` de `04 · 36` §3.2 es el único — este documento no toca estamina |
| `spawns_enemigos` como una variable `global.*` suelta, fuera de `WorldState` | Cuando extiendas el guardado a disco, la lista de enemigos muertos no viaja con el save y todo revive al recargar | Que viva DENTRO de `WorldState` (§3.2) desde el principio, aunque hoy no la guardes — el día que la guardes, ya está en el sitio correcto |
| `hoguera_registrar_punto()` sin comprobar duplicados | Cada vez que el jugador entra en una sala, la lista de spawns de esa sala crece sin límite | La comprobación por tipo+posición (§3.3) hace que registrar dos veces la misma sala sea gratis |
| Reiniciar enemigos SOLO en la sala actual al descansar | Enemigos ya muertos en OTRAS salas nunca vuelven, aunque hayas descansado varias veces | `hoguera_reiniciar_mapa()` limpia `consumido` en TODAS las salas conocidas — solo destruye/recrea instancias en la actual porque es la única con instancias vivas (§3.3) |
| Descansar automático al tocar la hoguera, copiado de `objSavePoint` (`04 · 06` §5.7) sin cambiar nada | El jugador reinicia el nivel sin querer, solo por pasar cerca — el coste-beneficio deja de ser una decisión | Exige una pulsación explícita (§3.6) — `objSavePoint` puede ser automático porque NO tiene coste; una hoguera sí |
| Sumar las almas de la marca vieja a la marca nueva al morir dos veces | El jugador nunca pierde nada de verdad: la "pérdida" deja de doler | `marca_muerte_crear()` sobrescribe sin sumar (§3.7) — las almas viejas se pierden, punto |
| Olvidar poner `global.marca_muerte = undefined` al recoger | La siguiente muerte cree que hay que sustituir una marca que ya no existe; si además no se destruyó la instancia vieja, aparecen dos recogibles en el mismo sitio | `obj_marca_muerte` — Step (§3.8) hace las dos cosas en el mismo bloque: cobrar Y limpiar la referencia |
| Llamar a `player_respawn()` antes que `marca_muerte_crear()` | La marca aparece en la hoguera, no donde murió el jugador — rompe toda la tensión de "vuelve a por lo que perdiste" | El orden es fijo: marca primero, respawn después (§3.9) |
| Añadir el temporizador de §3.7 bis sin ningún aviso ni compensación | El jugador pierde el recurso sin enterarse de que había un plazo — la crítica de "castiga el tiempo, no la cautela" en su peor versión | Un icono/contador visible mientras la marca esté pendiente, o combínalo con la regla de §3.7 en vez de sustituirla sin más |
| Construir el *lock-on* dentro de este documento «porque el combate lo necesita» | Duplica el trabajo que ya existe en `13 · 19` §3.12, y mezcla cámara con estado de mundo | El *lock-on* es un sistema de cámara: vive en `13 · 19` §3.12 (§3.10), no aquí, aunque el combate lo dispare |

---

## Ver también

- [`04 · 30` — Combate cuerpo a cuerpo](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) —
  la base entera de combate: `EstadoCombate`, i-frames y esquiva (§4.5), bloqueo y parry (§4.6),
  aguante (§4.7), el hook conceptual de "al morir" (§6). Nada de esto se repite aquí.
- [`04 · 36` — Habilidades, enfriamientos y recursos de combate](./36%20-%20Habilidades%2C%20enfriamientos%20y%20recursos%20de%20combate.md) —
  `RecursoCombate` (§3.2) y el enganche de la estamina a la esquiva (§3.6), reutilizados sin
  cambiar una línea.
- [`04 · 06` — Metroidvania](./06%20-%20Metroidvania.md) §5.0 — `WorldState`, `guardar_punto()`,
  `save_to_disk()`/`load_from_disk()`: la base sobre la que se extiende `spawns_enemigos`/
  `recursos_consumibles` (§3.2). §5.7 — `objSavePoint` y `player_respawn()`, reutilizado tal
  cual en §3.9.
- [`13 · 19` — Cámaras de juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/19%20-%20Cámaras%20de%20juego%20-%20encuadre%2C%20seguimiento%20y%20control.md#312-lock-on-target-bloquear-la-cámara-sobre-un-enemigo)
  §3.12 — *Lock-on-target*: la cámara y el eje "adelante" del jugador enganchados al enemigo
  objetivo (§3.10 de este documento), fuera de alcance aquí a propósito. Ese documento enlaza
  de vuelta a este para la parte de recursos/riesgo/muerte del *lock-on* como mecánica.
- [`04 · 47` — Beat 'em up y brawler](./47%20-%20Beat%20em%20up%20y%20brawler.md) §4.2, §5.1 —
  el precedente exacto de "ampliar un documento existente por composición, sin tocarlo", que
  siguen `mundo_extender_hoguera()` (§3.2) y los marcadores `obj_spawn_*` (§3.4).
- [`04 · 33` — Diseño de enemigos, encuentros y director de combate](./33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md) —
  la anotación "obj_enemigo · al morir" que este documento reutiliza como punto de enganche
  (§3.5).
- [`04 · 15` — Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) §5.6 — `fx_floating_text()`
  y `fx_flash()`, usados en §3.6 y §3.8 sin repetir su código.
- [`01 · 04` — Structs y constructores (POO en GML)](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) —
  por qué structs y arrays son por referencia, la base técnica de §3.2 y §3.3 (`_mapa` se pasa
  y se edita sin necesidad de devolverlo).
- [`01 · 14` — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) —
  si decides guardar `spawns_enemigos`/`recursos_consumibles` a disco (⚠️ de §3.2), el mismo
  patrón `file_text_open_write`/`json_stringify` que ya usa `04 · 06` §5.0.
- [`06` · `scr_state_machine.gml`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) —
  la máquina de estados (`fsm.set("muerto")`) sobre la que engancha §3.9.

---

## Fuentes

**Definición del género y de la mecánica de hoguera/marca de muerte**, Wikipedia (inglés),
consultado en vivo el **2026-09-07** con `curl -sL -A "Mozilla/5.0…"`:

- **"Soulslike"** — <https://en.wikipedia.org/wiki/Soulslike> — citas textuales usadas en §1.1
  y §1.3: *"Soulslike games typically have a high level of difficulty where repeated player
  character death is expected [...] since the last checkpoint. Other losses (such as experience
  or currency) are potentially recoverable"*; *"Soulslike games usually have ways to permanently
  improve the player character's abilities [...] often using a type of currency that can be
  earned and spent but may be lost or abandoned between deaths if not properly managed, similar
  to the souls in the Dark Souls series"*; *"Many Soulslike games use checkpoint systems
  associated with the bonfires of Dark Souls. These checkpoints typically serve as respawn or
  recovery points [...] while resting at them may reset enemies [...] preserving a
  risk-and-reward structure around death, recovery, and exploration"*.

**Runtime y biblioteca interna**, verificadas con `python3 "_indice/buscar.py" <símbolo>` el
**2026-09-07**:

- `instance_create_layer`, `instance_destroy`, `instance_exists`, `place_meeting` — Manual
  oficial, `09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Instances/`
  y `.../Movement_And_Collisions/Collisions/`.
- `variable_struct_exists`, `variable_struct_get_names`, `variable_instance_exists` — Manual
  oficial, `.../GML_Reference/Variable_Functions/`.
- `array_push`, `array_length` — ídem.
- `asset_get_index` — Manual oficial, `.../Asset_Management/Assets_And_Tags/`.
- `audio_play_sound`, `keyboard_check_pressed`, `ord`, `string` — ya verificadas y citadas en
  `04 · 30` y `04 · 06`; reutilizadas aquí sin cambiar de firma.
- **`instance_create_layer` acepta un nombre de capa como string y un `var_struct` opcional
  que se aplica ANTES del evento Create de la nueva instancia** — Manual oficial,
  `.../Asset_Management/Instances/instance_create_layer.md`, verificado leyendo la página
  completa el 2026-09-07 (es la base técnica de §3.4-§3.5: los tres campos `hoguera_*` llegan
  ya asignados cuando el Create del enemigo/recurso se ejecuta).
- **Structs y arrays son por referencia** —
  [`01 · 04 — Structs y constructores`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md),
  base técnica de §3.2-§3.3.
- **El precedente de "ampliar por composición, sin tocar el documento"** —
  [`04 · 47` §4.2](./47%20-%20Beat%20em%20up%20y%20brawler.md#42--extender-la-tabla-de-ataques-de-04--30-sin-tocar-el-documento),
  ya verificado y catalogado por esta biblioteca.

**La variante con temporizador (§3.7 bis)**, añadida por la auditoría
`_indice/auditorias/r4-combate-colisiones-gdd.md` (hueco B6), consultadas el **2026-09-07**:

- Tiempos de decaimiento de cadáver de *EverQuest* — resumidos por `WebSearch` a partir de los
  foros de Project 1999 (comunidad de servidor "classic" de EverQuest): *"Decay is 30 minutes
  for level 1, 2 hours for levels 2-4, and 7 days for level 5 and above [...] the online corpse
  timer is 3 hours and the offline corpse timer is 7 days"* — ⚠️ resumen de búsqueda, no lectura
  completa palabra por palabra de la fuente primaria (los hilos de Project 1999 no se abrieron
  con `WebFetch`).
- Raph Koster — *Why are corpse runs bad?*, blog personal, 17 de noviembre de 2008, leído
  completo con `WebFetch` — <https://www.raphkoster.com/2008/11/17/why-are-corpse-runs-bad/> —
  cita textual: *"corpse runs were a powerful social force, creating a mutual need and
  indebtedness that brought people together"*; su argumento es que el problema no es la mecánica
  sino la falta de mecanismos compensatorios al trasladarla de los MUD de texto a mundos 3D.
- Discusión de la comunidad sobre *corpse runs* en Valheim/Enshrouded (Steam Community),
  resumida por `WebSearch` — ⚠️ resumen de búsqueda, no lectura completa —: *"it's just a loss
  of time [...] doesn't add difficulty, you just lose time running in a straight line"*, citada
  como la cara crítica del debate en §3.7 bis.

> ⚠️ **Lo que NO está verificado en este documento.** Todos los símbolos de GML existen en el
> runtime 2026.0.0.23 (comprobados con `buscar.py`), pero el código **no se ha compilado en un
> proyecto real**: los nombres de objetos, sprites y sonidos (`obj_esqueleto`, `spr_hoguera`,
> `snd_hoguera_descansar`, `snd_recoger_marca`…) son marcadores de posición, igual que en
> `04 · 50` y `04 · 51`. La regla de "una sola marca de muerte, sustituida sin sumar" es una
> **decisión de diseño de esta biblioteca**, no una medición de ningún juego concreto — está
> inspirada en el comportamiento público y ampliamente documentado de Dark Souls/Elden Ring,
> pero no se ha verificado contra el código fuente de esos juegos (no es libre ni está
> disponible). Los tiempos, cantidades de curación y costes de descansar no llevan cifra porque
> este documento no los fija: son decisiones de balance de cada proyecto.
