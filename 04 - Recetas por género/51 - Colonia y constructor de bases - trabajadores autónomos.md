# 51 · Colonia y constructor de bases — trabajadores autónomos

> *RimWorld*, *Dwarf Fortress*, *Oxygen Not Included*, *Factorio*. Dos auditorías
> independientes de esta biblioteca (`_indice/auditorias/r3-simulacion-sistemas.md`) señalaron
> este género como **el hueco más grande de toda la colección**: no por falta de piezas sueltas
> — pathfinding, Utility AI, *spatial hash* y guardado versionado ya están resueltos y
> verificados en otros documentos — sino porque **nadie las había ensamblado**. Este documento
> es exactamente eso: el pegamento entre seis sistemas que solo sirven de algo **juntos**. No
> repite ninguna pieza que ya existe: la enlaza y dice en qué punto exacto engancha.

---

## 1 · Visión general

### 1.1 · Por qué esto es un género aparte, no un RTS con más pasos

Un *colony sim* se diferencia de la estrategia clásica (`04 · 13`) en una decisión de diseño
concreta: **el jugador no controla directamente a las unidades — les da intención, y ellas
deciden cómo cumplirla.** En un RTS ordenas «esa unidad, a por ese recurso»; en un *colony sim*
marcas «hay que talar ese árbol» y **cualquier** colono libre, con el oficio adecuado, lo hará
cuando le toque. Esa inversión de control es lo que obliga a las seis piezas de abajo a existir
a la vez: sin cola de tareas no hay «cualquier colono»; sin rutinas y necesidades los colonos no
tienen vida propia entre tarea y tarea; sin integridad estructural y redes la base no es más que
una guardería visualmente; y sin simulación fuera de pantalla, cien colonos en un mapa grande
hunden el frame rate en cuanto no caben todos en cámara.

### 1.2 · Las seis piezas, y de dónde viene cada una

| Sistema | Qué resuelve **aquí** | Reutiliza de |
|---|---|---|
| **§2 · Job system** | Cola global de tareas con prioridad, reserva (que dos colonos no vayan al mismo tronco), tareas en varios pasos, cancelación y expiración | `08 · 13 — Estructuras de datos (DS)` (familia `ds_priority_*`, ya en uso en [`04 · 35`](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md) y [`04 · 38`](./38%20-%20Pathfinding%20avanzado%20-%20flow%20fields%2C%20JPS%20y%20plataformas.md) para A*) · utilidad de [`04 · 31` §8](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md) para desempatar candidatas |
| **§3 · Rutinas y horarios** | Jornada por franjas, interrupción por necesidad, ir a dormir/comer cuando toca | El reloj `objTimeOfDay.tiempo` de [`04 · 09` §5.5](./09%20-%20Survival%20y%20crafting.md#55-ciclo-díanoche) y el patrón de calendario de [`04 · 45` §5.2](./45%20-%20Géneros%20sin%20receta%20propia%20-%20sigilo%2C%20horror%2C%20táctica%2C%20granja%20y%20idle.md#52--sistema-crítico-1--calendario-y-estaciones-sobre-el-reloj-que-ya-existe) |
| **§4 · Necesidades de la población** | Decaimiento, umbrales, y cómo una necesidad se convierte en una tarea real | `Needs()` de [`04 · 09` §5.0](./09%20-%20Survival%20y%20crafting.md#50-necesidades) — compuesto, no reescrito |
| **§5 · Construcción con integridad** | Plano frente a construido, materiales por traer, soporte estructural, habitaciones por *flood fill* | `WorldGrid`/`objWorldGrid` y el *ghost preview* de [`04 · 09` §5.3](./09%20-%20Survival%20y%20crafting.md#53-construcción-con-ghost-preview) · el *flood fill* de [`04 · 05` §5.4](./05%20-%20Roguelike%20y%20generación%20procedural.md#54-validación-por-flood-fill) |
| **§6 · Redes de energía y fluidos** | Nodos productor/consumidor, propagación, almacenamiento, déficit, tuberías con caudal | Vocabulario Pool/Fuente/Sumidero/Convertidor de [`13 · 01` §4.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md) · el autómata celular de líquido de [`13 · 08` §10](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/08%20-%20Físicas%20a%20mano%20y%20fluidos.md) |
| **§7 · Simulación fuera de pantalla** | LOD de simulación, actualización por lotes, entidades dormidas, presupuesto real | Tick escalonado de [`04 · 31` §12](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md) · *chunking* de [`04 · 09` §5.4](./09%20-%20Survival%20y%20crafting.md#54-chunking) · presupuesto en µs de [`13 · 08` §14](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/08%20-%20Físicas%20a%20mano%20y%20fluidos.md) |

### 1.3 · Qué NO cubre este documento

- **Precio dinámico y comercio con NPC.** No es el encargo de este documento:
  [`13 · 01` §4.6-§4.7](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#46--precio-dinámico-oferta-y-demanda)
  ya lo resuelve (oferta/demanda con `scr_economia_dinamica`, y la tienda de un NPC con margen y
  stock que se agota y repone).
- **Cosecha y ganado.** Fuera de alcance: son el encargo de
  [`04 · 45`](./45%20-%20Géneros%20sin%20receta%20propia%20-%20sigilo%2C%20horror%2C%20táctica%2C%20granja%20y%20idle.md)
  §5, que ya tiene el calendario y los cultivos por celda sobre los que montarlos.
- **Logística de cintas transportadoras.** El *job system* del §2 mueve materiales **colono a
  colono**; una cinta que mueve ítems sola, sin trabajador de por medio, es una mecánica
  distinta (tema 37 del informe r3) que sigue sin receta en esta biblioteca. Si tu juego es más
  Factorio que RimWorld, el §6 (redes) es tu punto de partida, pero la cinta en sí queda fuera.
- **Facciones, reputación y relaciones NPC↔NPC.** Temas 69-71 del informe: siguen sin cubrir.

### 1.4 · Arquitectura recomendada

Un colono es una **instancia** (`obj_colono`) con tres componentes por composición — no
herencia — cada uno un struct: `necesidades` (§4), `horario` (§3) y `tarea_actual` (§2, un
struct `Tarea`, no una instancia). El resto del mundo — la cola de tareas, la rejilla de
construcción, la red de energía — vive en `global.*`, siguiendo el mismo patrón de
localizador de servicios que
[`13 · 06` §3.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md).

```gml
// scr_config_colonia.gml — asume que el proyecto YA define CELL (04 · 09), CHUNK_PX y
// RADIO_CARGA (04 · 09 §5.4): no se repiten aquí.

#macro COLONO_RADIO_INTERACCION    12      // px — cuándo se considera "ha llegado"
#macro COLONO_CANDIDATOS_A_MIRAR    4      // cuántas tareas de la cola compara antes de elegir
#macro TAREA_PRIORIDAD_MAX        100
#macro TAREA_INTENTOS_MAX           3      // fallos seguidos antes de IMPOSIBLE (§2.7)
#macro TAREA_FRAMES_EXPIRAR       (60 * 60 * 3)   // 3 min sin trabajador disponible (§2.8)
#macro TAREA_EXPIRAR_CADA_FRAMES   60      // cada cuántos frames se revisa la expiración
#macro FRAMES_RECOGER              20      // duración del paso RECOGER de un TRANSPORTAR
#macro DANO_POR_GOLPE               1
#macro FRAMES_POR_GOLPE            30
#macro PRIORIDAD_NECESIDAD_URGENTE 90
#macro PRIORIDAD_CONSTRUCCION      50
#macro UMBRAL_HAMBRE_URGENTE       20
#macro UMBRAL_HAMBRE_RUTINA        60      // más laxo: durante la franja de comer, ver §3.3
#macro UMBRAL_SED_URGENTE          20
#macro UMBRAL_SUENO_URGENTE        15
#macro UMBRAL_HIGIENE_URGENTE      20
#macro UMBRAL_ANIMO_URGENTE        20
#macro SOPORTE_DISTANCIA_MAX        8      // celdas desde un ancla antes de derrumbarse
#macro MATERIAL_RECUPERADO_DERRUMBE 0.5
#macro HABITACIONES_FRAMES_MIN_MS 500      // recalcular habitaciones como mucho 2×/seg
#macro LOD_PASOS_ABSTRACTOS_MAX   600      // tope de "pasos grandes" al despertar (§7.3)
#macro PRESUPUESTO_SIMULACION_US 2000      // µs/frame de este documento, sobre los 16 666 (13 · 08 §14)
#macro COLONOS_DORMIDOS_CADA_FRAMES 90     // cada cuánto avanzan los colonos abstractos (§7.3)
#macro TICK_RED_ENERGIA_CADA_FRAMES 30     // cada cuánto se propaga la red de energía (§6.3)
#macro TILE_AGUA        1      // ajusta a los índices reales de tu tilemap de terreno (§5.2)
#macro TILE_PARED_ROCA  2
```

**Objetos nuevos de este documento:** `obj_colono` (el trabajador), `obj_tablon_trabajos`
(controlador único de la cola global), `obj_planificador_colonia` (coloca planos, §5),
`obj_simulador_colonia` (amortiza el trabajo de fondo, §7). Ninguno sustituye a `objWorldGrid`,
`objStructure`, `objChunkManager`, `objTimeOfDay` ni `objItemDrop` de `04 · 09`: este documento
los usa tal cual están.

**Globales nuevos, todos inicializados en el arranque de la colonia (`obj_game` · Create o
equivalente, junto a lo que ya inicializa `04 · 09`):** `global.almacen` (un `Inventory`, `04 ·
04` §5.2, reutilizado como el almacén central) · `global.almacen_pos` (`{ celda_x, celda_y }`) ·
`global.anclas_soporte` (array de `[x,y]`: suelo natural o cimientos, §5.4) ·
`global.colonia_ancho`/`global.colonia_alto` (tamaño en celdas, para §5.5) ·
`global.jugador_chunk_x`/`global.jugador_chunk_y` (recalculados cada frame desde la posición de
cámara, para el LOD del §7.1) · `global.frame_count` (el mismo contador que ya usa `04 · 09`
§5.4 para su chequeo «cada 30 frames», incrementado una vez por Step en `obj_game`).

```gml
/// obj_game — Create (arranque de la colonia; junto a lo que ya inicializa 04 · 09)
/// Sin este bloque, la primera lectura de cualquiera de estos globals (el job
/// system del §2, el almacén del §2.9, el soporte del §5.4 o el overlay de debug
/// del §7.4) revienta con «variable global no definida» — el párrafo de arriba
/// los da por creados aquí, pero el código nunca se había mostrado.
global.colonia_ancho = room_width  div CELL;   // tamaño jugable en celdas
global.colonia_alto  = room_height div CELL;

global.almacen     = new Inventory(200);       // 04 · 04 §5.2 — ajusta la capacidad a tu economía
global.almacen_pos = { celda_x: global.colonia_ancho div 2, celda_y: global.colonia_alto div 2 };
                                                 // celda real donde coloques tu almacén: ajústala

global.anclas_soporte = [];   // §5.4 — ve empujando aquí el suelo natural o tus cimientos
                               // marcados a mano, según construyes (no de una sola vez)

global.modo_debug  = false;   // pon a `true` para ver el overlay de coste del §7.4
global.frame_count = 0;       // 04 · 09 §5.4 ya lo lee con "mod 30"; se incrementa abajo
```

```gml
/// obj_game — Step
global.frame_count++;

// LOD de colonia (§7.1): recalculado cada frame — mismo cálculo que 04 · 09 §5.4
global.jugador_chunk_x = objPlayer.x div CHUNK_PX;
global.jugador_chunk_y = objPlayer.y div CHUNK_PX;
```

---

## 2 · Job system: cola de tareas y asignación de trabajadores

### 2.1 · El problema: por qué «el más cercano decide» no basta

La tentación es dejar que cada colono, en su Step, mire el mundo y decida por su cuenta qué
hacer. Se rompe en cuanto hay más de dos colonos: dos leñadores libres ven el mismo árbol y los
dos caminan hacia él — uno llega, lo tala, y el otro ha caminado media pantalla para nada. Hace
falta un **tablón único** donde una tarea, en cuanto un colono la coge, deja de estar disponible
para los demás. GameMaker es de un solo hilo lógico: no hace falta ningún *lock* ni sección
crítica para eso — entre «la vi libre» y «la reservo» no hay ningún otro código que pueda
colarse, así que una simple bandera de estado basta.

### 2.2 · Modelo de datos: la tarea como struct, no como instancia

Una `Tarea` **no es una instancia de GameMaker**: vive como struct dentro de la cola global, así
que sobrevive aunque el colono que la estaba haciendo muera, y no gasta un slot de instancia
mientras espera en el tablón.

```gml
// ---------------------------------------------------------------------------
// scr_job_system
// ---------------------------------------------------------------------------

enum TipoTrabajo   { TALAR, MINAR, TRANSPORTAR, CONSTRUIR, LIMPIAR, COCINAR, CURAR,
                      COMER, BEBER, ASEARSE }
enum EstadoTarea   { PENDIENTE, RESERVADA, EN_CURSO, COMPLETADA, CANCELADA, IMPOSIBLE }
enum PasoTarea     { IR, RECOGER, LLEVAR, SOLTAR, TRABAJAR }

/// @func Tarea(_tipo, _celda_x, _celda_y, _prioridad)
/// @desc Una unidad de trabajo. `celda_x`/`celda_y` son coordenadas de REJILLA (no
///       píxeles) y marcan el primer sitio al que hay que ir — el origen de una
///       recogida, o el propio sitio de trabajo si no hace falta transportar nada.
function Tarea(_tipo, _celda_x, _celda_y, _prioridad) constructor
{
    tarea_id      = -1;                 // lo asigna ColaTrabajos.encolar(); -1 = tarea personal (§4.3)
    tipo          = _tipo;
    celda_x       = _celda_x;
    celda_y       = _celda_y;
    prioridad     = _prioridad;         // 0..100 · más alto = sale antes de la cola
    estado        = EstadoTarea.PENDIENTE;
    paso          = PasoTarea.IR;
    reservada_por = noone;              // instancia de obj_colono, o noone

    // Solo los usan algunos tipos — quedan a su valor por defecto cuando no aplican.
    objetivo_inst  = noone;             // instancia real a talar/minar/limpiar/curar
    origen_x = _celda_x; origen_y = _celda_y;
    destino_x = _celda_x; destino_y = _celda_y;
    carga_item     = "";
    carga_cantidad = 0;

    frames_sin_trabajador = 0;          // cuenta hasta expirar (§2.8)
    intentos_fallidos      = 0;         // fallos seguidos antes de IMPOSIBLE (§2.7)
}
```

### 2.3 · La cola global: una `ds_priority` por tipo de trabajo

Una sola `ds_priority` mezclando los diez tipos obligaría a cada colono a recorrerla entera
descartando lo que no sabe hacer. Una **por tipo**, creada bajo demanda, hace que un leñador solo
consulte la suya.

```gml
/// @func ColaTrabajos()
/// @desc El tablón de tareas de toda la colonia. Vive en `global.cola_trabajos`,
///       creado una vez (`obj_tablon_trabajos` · Create).
function ColaTrabajos() constructor
{
    colas  = {};     // string(TipoTrabajo) → Id.DsPriority, una cola por tipo
    tareas = {};      // string(tarea_id) → Tarea — el mapa maestro, existe SIEMPRE,
                       // aunque la tarea esté fuera de su cola mientras está reservada
    siguiente_id = 0;

    cola_de = function(_tipo)
    {
        var _k = string(_tipo);
        if (!variable_struct_exists(colas, _k)) colas[$ _k] = ds_priority_create();
        return colas[$ _k];
    };

    /// @desc Registra la tarea en el mapa maestro y en SU cola de prioridad.
    encolar = function(_tarea)
    {
        var _tid = siguiente_id;
        siguiente_id += 1;
        _tarea.tarea_id = _tid;
        tareas[$ string(_tid)] = _tarea;
        ds_priority_add(cola_de(_tarea.tipo), _tid, _tarea.prioridad);
        return _tid;
    };

    obtener = function(_tarea_id)
    {
        var _k = string(_tarea_id);
        return variable_struct_exists(tareas, _k) ? tareas[$ _k] : undefined;
    };

    /// @desc Saca (pop) la tarea de MAYOR prioridad de un tipo, o `undefined` si no hay
    ///       ninguna. Ya la deja fuera de su `ds_priority`: reservarla después no toca
    ///       la cola para nada — por eso `tarea_reservar()` (§2.4) es tan corta.
    sacar_mejor = function(_tipo)
    {
        var _c = cola_de(_tipo);
        if (ds_priority_empty(_c)) return undefined;
        return obtener(ds_priority_delete_max(_c));
    };

    /// @desc Devuelve una tarea a su cola de prioridad, con SU prioridad. La usan
    ///       `tarea_fallar()` (§2.7) y `colono_buscar_tarea()` (§2.5) al descartar
    ///       candidatas que no eligió.
    reencolar = function(_tarea)
    {
        ds_priority_add(cola_de(_tarea.tipo), _tarea.tarea_id, _tarea.prioridad);
    };

    /// @desc Cambia la prioridad de una tarea PENDIENTE (aún en su cola). Si está
    ///       reservada, la nueva prioridad se aplica sola en cuanto vuelva (`reencolar`).
    reprioritizar = function(_tarea_id, _nueva_prioridad)
    {
        var _t = obtener(_tarea_id);
        if (is_undefined(_t)) return;
        _t.prioridad = _nueva_prioridad;
        if (_t.estado == EstadoTarea.PENDIENTE)
        {
            ds_priority_change_priority(cola_de(_t.tipo), _tarea_id, _nueva_prioridad);
        }
    };

    /// @desc Cancela una tarea. Si sigue pendiente, sale también de su `ds_priority`
    ///       aunque no sea la de mayor prioridad — para eso existe `ds_priority_delete_value`,
    ///       distinta de `delete_max`/`delete_min`.
    cancelar = function(_tarea_id)
    {
        var _t = obtener(_tarea_id);
        if (is_undefined(_t)) return;
        if (_t.estado == EstadoTarea.PENDIENTE)
        {
            ds_priority_delete_value(cola_de(_t.tipo), _tarea_id);
        }
        _t.estado = EstadoTarea.CANCELADA;
        variable_struct_remove(tareas, string(_tarea_id));
    };

    completar = function(_tarea_id)
    {
        var _t = obtener(_tarea_id);
        if (is_undefined(_t)) return;      // tarea personal (tarea_id == -1): no-op seguro
        _t.estado = EstadoTarea.COMPLETADA;
        variable_struct_remove(tareas, string(_tarea_id));
    };

    /// @desc Cuántas tareas PENDIENTES hay de un tipo — para un HUD tipo "3 árboles
    ///       por talar" sin recorrer nada: `ds_priority_size` es O(1).
    pendientes = function(_tipo) { return ds_priority_size(cola_de(_tipo)); };
}

/// obj_tablon_trabajos · Create
global.cola_trabajos = new ColaTrabajos();

/// obj_tablon_trabajos · Step — expiración en lote, no cada frame (§2.8 y §7.2). Mismo
/// criterio de "cada N frames, no cada frame" que 04 · 09 §5.4 (objChunkManager · Step)
/// con su propio global.frame_count.
if (global.frame_count mod TAREA_EXPIRAR_CADA_FRAMES == 0)
{
    cola_trabajos_expirar(global.cola_trabajos);
}
```

> ⚠️ **`ds_priority_add` solo documenta `Real` o `String` como `val`.** Por eso la cola guarda el
> **id numérico** de la tarea, nunca el struct `Tarea` directamente — el mismo criterio que
> siguen `04 · 35` y `04 · 38` guardando índices de rejilla, no structs, dentro de su
> `ds_priority`. El struct de verdad vive en `tareas`, el mapa maestro.

### 2.4 · Reserva: que dos colonos no vayan al mismo tronco

```gml
/// @func tarea_reservar(_tarea, _colono_inst)
/// @desc Ya se sacó de la cola con sacar_mejor(): esto solo marca de quién es.
function tarea_reservar(_tarea, _colono_inst)
{
    _tarea.estado        = EstadoTarea.RESERVADA;
    _tarea.reservada_por = _colono_inst;
    _tarea.paso          = PasoTarea.IR;
}
```

### 2.5 · Asignación: prioridad primero, distancia después

Sacar siempre la de mayor prioridad a ciegas ignora la distancia: un colono podría cruzar medio
mapa por una tarea de prioridad 51 habiendo una de prioridad 50 a su lado. La solución barata:
**sacar varias** de las de mayor prioridad (`ds_priority_delete_max` las entrega en ese orden),
quedarse con la más cercana, y devolver las demás.

```gml
/// @func colono_buscar_tarea(_colono, _tipo)
/// @desc Saca hasta COLONO_CANDIDATOS_A_MIRAR tareas (las de más prioridad, porque
///       delete_max las entrega en ese orden), elige la más cercana, y reencola el
///       resto sin tocar su prioridad. Es el mismo compromiso de 04 · 31 §8: la
///       prioridad decide QUÉ CONJUNTO mirar, la distancia decide cuál de ese conjunto
///       — no hace falta instance_nearest porque una Tarea es un struct, no una
///       instancia de GameMaker (ver §4.3 para el caso en que sí aplica).
function colono_buscar_tarea(_colono, _tipo)
{
    var _vistas  = [];
    var _elegida = undefined;
    var _mejor_d = infinity;

    repeat (COLONO_CANDIDATOS_A_MIRAR)
    {
        var _t = global.cola_trabajos.sacar_mejor(_tipo);
        if (is_undefined(_t)) break;
        array_push(_vistas, _t);

        var _d = point_distance(_colono.x, _colono.y, _t.celda_x * CELL, _t.celda_y * CELL);
        if (_d < _mejor_d) { _mejor_d = _d; _elegida = _t; }
    }

    for (var _i = 0; _i < array_length(_vistas); _i++)
    {
        if (_vistas[_i] != _elegida) global.cola_trabajos.reencolar(_vistas[_i]);
    }

    if (is_undefined(_elegida)) return noone;

    tarea_reservar(_elegida, _colono.id);
    return _elegida;
}

/// @func profesion_tipos_permitidos(_profesion)
/// @desc El orden importa: es el orden en que un colono libre prueba tipos de tarea.
function profesion_tipos_permitidos(_profesion)
{
    switch (_profesion)
    {
        case Profesion.TALADOR:     return [TipoTrabajo.TALAR, TipoTrabajo.TRANSPORTAR];
        case Profesion.MINERO:      return [TipoTrabajo.MINAR, TipoTrabajo.TRANSPORTAR];
        case Profesion.CONSTRUCTOR: return [TipoTrabajo.CONSTRUIR, TipoTrabajo.TRANSPORTAR];
        case Profesion.COCINERO:    return [TipoTrabajo.COCINAR];
        case Profesion.MEDICO:      return [TipoTrabajo.CURAR];
        default:                    return [TipoTrabajo.TALAR, TipoTrabajo.MINAR,
                                             TipoTrabajo.TRANSPORTAR, TipoTrabajo.CONSTRUIR,
                                             TipoTrabajo.LIMPIAR];               // GENERALISTA
    }
}

enum Profesion { GENERALISTA, TALADOR, MINERO, CONSTRUCTOR, COCINERO, MEDICO }
```

### 2.6 · Tareas en varios pasos: ir → recoger → llevar → soltar

No todas las tareas necesitan los cuatro pasos. Talar/minar trabajan donde están (solo
`IR` → `TRABAJAR`); `TRANSPORTAR` es la que de verdad usa los cuatro.

```gml
/// @func paso_siguiente_tras_llegar(_tipo)
function paso_siguiente_tras_llegar(_tipo)
{
    return (_tipo == TipoTrabajo.TRANSPORTAR) ? PasoTarea.RECOGER : PasoTarea.TRABAJAR;
}

/// @func duracion_trabajo(_tipo)
/// @desc Frames de TRABAJAR para los tipos de duración fija. TALAR/MINAR no están
///       aquí: su duración la marca golpear()/romper() de 04 · 09 §5.2 (ver §2.9).
function duracion_trabajo(_tipo)
{
    switch (_tipo)
    {
        case TipoTrabajo.CONSTRUIR: return 180;
        case TipoTrabajo.LIMPIAR:   return 60;
        case TipoTrabajo.COCINAR:   return 150;
        case TipoTrabajo.CURAR:     return 120;
        case TipoTrabajo.COMER:     return 90;
        case TipoTrabajo.BEBER:     return 40;
        case TipoTrabajo.ASEARSE:   return 100;
        default:                    return 60;
    }
}
```

### 2.7 · Cancelar y reencolar

```gml
/// @func tarea_fallar(_tarea)
/// @desc Libera la reserva SIN borrar la tarea (salvo que ya haya fallado demasiadas
///       veces): otro colono, o el mismo más tarde, puede intentarlo. Es el mecanismo
///       genérico de "algo salió mal" — un camino bloqueado, un objetivo destruido, o
///       una interrupción de rutina (§3.3).
function tarea_fallar(_tarea)
{
    if (_tarea.tarea_id == -1)               // tarea personal (§4.3): nunca vivió en la cola
    {
        _tarea.reservada_por = noone;
        return;
    }

    _tarea.intentos_fallidos++;
    _tarea.reservada_por = noone;
    _tarea.paso          = PasoTarea.IR;

    if (_tarea.intentos_fallidos >= TAREA_INTENTOS_MAX)
    {
        _tarea.estado = EstadoTarea.IMPOSIBLE;
        senal_emitir("tarea_imposible", { tarea: _tarea });      // 04 · 16, reutilizado
        variable_struct_remove(global.cola_trabajos.tareas, string(_tarea.tarea_id));
    }
    else
    {
        _tarea.estado = EstadoTarea.PENDIENTE;
        global.cola_trabajos.reencolar(_tarea);
    }
}
```

Cancelar una tarea desde fuera (el jugador borra un plano, un edificio deja de tener sentido) es
directo: `global.cola_trabajos.cancelar(_tarea_id)` — no hace falta pasar por `tarea_fallar()`,
que es específicamente para «se intentó y no se pudo».

### 2.8 · Tareas imposibles y su expiración

Una tarea puede quedarse pendiente para siempre si nadie tiene el oficio adecuado, o si la celda
quedó inaccesible tras un derrumbe (§5.4). `tarea_fallar()` ya cubre el caso de «se reservó y
falló 3 veces»; esto cubre el caso de «nunca llegó a reservarse».

```gml
/// @func cola_trabajos_expirar(_cola)
/// @desc UN barrido cada TAREA_EXPIRAR_CADA_FRAMES frames (mismo criterio de lote que
///       el §7.2), no cada frame: recorrer el mapa maestro entero es O(n), aceptable
///       de tarde en tarde, no 60 veces por segundo.
function cola_trabajos_expirar(_cola)
{
    var _claves = variable_struct_get_names(_cola.tareas);
    for (var _i = 0; _i < array_length(_claves); _i++)
    {
        var _t = _cola.tareas[$ _claves[_i]];
        if (_t.estado != EstadoTarea.PENDIENTE) { _t.frames_sin_trabajador = 0; continue; }

        _t.frames_sin_trabajador += TAREA_EXPIRAR_CADA_FRAMES;
        if (_t.frames_sin_trabajador >= TAREA_FRAMES_EXPIRAR)
        {
            ds_priority_delete_value(_cola.cola_de(_t.tipo), _t.tarea_id);
            _t.estado = EstadoTarea.IMPOSIBLE;
            senal_emitir("tarea_imposible", { tarea: _t });
            variable_struct_remove(_cola.tareas, _claves[_i]);
        }
    }
}
```

> 💡 **`tarea_imposible` es lo que engancha la UI.** Un oyente (`04 · 16`) en el controlador del
> HUD puede pintar un icono de aviso sobre la celda: «esto lleva 3 minutos sin nadie que lo
> haga» es información real para el jugador, no solo un descarte silencioso.

### 2.9 · `obj_colono`: la máquina de estados de trabajo

```gml
enum EstadoColono { OCIOSO, TRABAJANDO, YENDO_A_DORMIR, DURMIENDO, ATENDIENDO_NECESIDAD }

/// obj_colono · Create
profesion       = Profesion.GENERALISTA;
herramienta_equipada = "";                 // "hacha", "pico", "" = a mano — la lee golpear()
velocidad_mov   = 2;
estado_colono   = EstadoColono.OCIOSO;
tarea_actual    = noone;
frames_en_paso  = 0;
cama_x = x;  cama_y = y;                   // el planificador de vivienda las asigna de verdad
necesidades     = new NecesidadesColono();  // §4.1
horario         = horario_colono_defecto(); // §3.1

/// obj_colono · Step — bucle de ejecución de la tarea actual. El despachador de
/// rutina (§3.2) corre ANTES de este bloque en el mismo Step y puede haber cambiado
/// tarea_actual/estado_colono; aquí solo se EJECUTA lo que ya está en marcha.
if ((estado_colono == EstadoColono.TRABAJANDO || estado_colono == EstadoColono.ATENDIENDO_NECESIDAD)
    && tarea_actual != noone)
{
    switch (tarea_actual.paso)
    {
        case PasoTarea.IR:
            var _dx = tarea_actual.celda_x * CELL, _dy = tarea_actual.celda_y * CELL;
            if (point_distance(x, y, _dx, _dy) <= COLONO_RADIO_INTERACCION)
            {
                tarea_actual.paso   = paso_siguiente_tras_llegar(tarea_actual.tipo);
                tarea_actual.estado = EstadoTarea.EN_CURSO;
            }
            else if (!mp_potential_step(_dx, _dy, velocidad_mov, false))
            {
                tarea_fallar(tarea_actual);
                tarea_actual  = noone;
                estado_colono = EstadoColono.OCIOSO;
            }
            break;

        case PasoTarea.RECOGER:                       // solo TRANSPORTAR llega aquí
            if (!global.almacen.has(tarea_actual.carga_item, tarea_actual.carga_cantidad))
            {
                tarea_fallar(tarea_actual);            // otro colono se adelantó
                tarea_actual  = noone;
                estado_colono = EstadoColono.OCIOSO;
                break;
            }
            frames_en_paso++;
            if (frames_en_paso >= FRAMES_RECOGER)
            {
                frames_en_paso = 0;
                global.almacen.remove(tarea_actual.carga_item, tarea_actual.carga_cantidad);   // 04 · 04 §5.2
                tarea_actual.paso = PasoTarea.LLEVAR;
            }
            break;

        case PasoTarea.LLEVAR:
            var _dx = tarea_actual.destino_x * CELL, _dy = tarea_actual.destino_y * CELL;
            if (point_distance(x, y, _dx, _dy) <= COLONO_RADIO_INTERACCION)
            {
                tarea_actual.paso = PasoTarea.SOLTAR;
            }
            else
            {
                mp_potential_step(_dx, _dy, velocidad_mov, false);
            }
            break;

        case PasoTarea.SOLTAR:
            var _k = string(tarea_actual.destino_x) + "," + string(tarea_actual.destino_y);
            if (variable_struct_exists(global.planos, _k))
            {
                var _plan = global.planos[$ _k];                       // §5.3
                _plan.entregar(tarea_actual.carga_item, tarea_actual.carga_cantidad);
                plan_intentar_completar(_plan);
            }
            else
            {
                global.almacen.add(tarea_actual.carga_item, tarea_actual.carga_cantidad);
            }
            global.cola_trabajos.completar(tarea_actual.tarea_id);
            tarea_actual  = noone;
            estado_colono = EstadoColono.OCIOSO;
            break;

        case PasoTarea.TRABAJAR:
            if (tarea_actual.tipo == TipoTrabajo.TALAR || tarea_actual.tipo == TipoTrabajo.MINAR)
            {
                if (!instance_exists(tarea_actual.objetivo_inst))
                {
                    tarea_fallar(tarea_actual);          // alguien más lo taló primero
                    tarea_actual  = noone;
                    estado_colono = EstadoColono.OCIOSO;
                    break;
                }
                frames_en_paso++;
                if (frames_en_paso >= FRAMES_POR_GOLPE)
                {
                    frames_en_paso = 0;
                    // golpear()/romper(): 04 · 09 §5.2, reutilizados TAL CUAL — romper()
                    // ya suelta los objItemDrop en el suelo y destruye el nodo.
                    tarea_actual.objetivo_inst.golpear(DANO_POR_GOLPE, herramienta_equipada);
                    if (!instance_exists(tarea_actual.objetivo_inst))
                    {
                        global.cola_trabajos.completar(tarea_actual.tarea_id);
                        tarea_actual  = noone;
                        estado_colono = EstadoColono.OCIOSO;
                    }
                }
            }
            else
            {
                frames_en_paso++;
                if (frames_en_paso >= duracion_trabajo(tarea_actual.tipo))
                {
                    frames_en_paso = 0;
                    tarea_completar_efecto(tarea_actual);         // §2.6/§5.3/§4.3
                    global.cola_trabajos.completar(tarea_actual.tarea_id);
                    tarea_actual  = noone;
                    estado_colono = EstadoColono.OCIOSO;
                }
            }
            break;
    }
}

/// @func tarea_completar_efecto(_tarea)
/// @desc Solo los tipos de duración fija llegan aquí: TALAR/MINAR terminan solos al
///       destruirse el nodo (arriba) y TRANSPORTAR termina en su propio SOLTAR.
function tarea_completar_efecto(_tarea)
{
    switch (_tarea.tipo)
    {
        case TipoTrabajo.CONSTRUIR:
            construccion_levantar(_tarea.celda_x, _tarea.celda_y);          // §5.3
            break;

        case TipoTrabajo.LIMPIAR:
            if (_tarea.objetivo_inst != noone && instance_exists(_tarea.objetivo_inst))
            {
                instance_destroy(_tarea.objetivo_inst);
            }
            break;

        case TipoTrabajo.COCINAR:
            var _receta = recipe_get("racion");           // amplía global.recipes, ver §4.3
            if (_receta != undefined) _receta.craftear(global.almacen);      // 04 · 09 §5.1
            break;

        case TipoTrabajo.CURAR:
            if (_tarea.objetivo_inst != noone && instance_exists(_tarea.objetivo_inst))
            {
                _tarea.objetivo_inst.hp = _tarea.objetivo_inst.hp_max;
            }
            break;

        case TipoTrabajo.COMER:
            global.almacen.remove("racion", 1);
            _tarea.reservada_por.necesidades.base.consumir({ hambre: 60 });  // 04 · 09 §5.0
            break;

        case TipoTrabajo.BEBER:
            _tarea.reservada_por.necesidades.base.consumir({ sed: 70 });
            break;

        case TipoTrabajo.ASEARSE:
            _tarea.reservada_por.necesidades.higiene = 100;
            break;
    }
}
```

> 🔺 **`tarea_completar_efecto` no sabe nada de colas ni de reservas.** Es deliberado: separa
> «qué significa terminar esta tarea» (aquí) de «cómo se administra el ciclo de vida de una
> tarea» (§2.3-§2.8). La misma separación que `04 · 31` §12 pide entre decidir y moverse.

---

## 3 · Rutinas y horarios de NPC

### 3.1 · El horario como datos, sobre el reloj que ya existe

Ni el reloj (`objTimeOfDay.tiempo`, `04 · 09` §5.5) ni el calendario (`04 · 45` §5.2) se
reescriben aquí: el horario es una tabla de franjas que **consulta** el reloj, exactamente como
el calendario ya consulta el mismo reloj sin crear uno nuevo.

```gml
// ---------------------------------------------------------------------------
// scr_rutina
// ---------------------------------------------------------------------------

enum Actividad { TRABAJAR, OCIO, DORMIR, COMER }

/// @func horario_colono_defecto()
/// @desc Una franja puede cruzar medianoche (hora_inicio > hora_fin): la de dormir,
///       de 22 a 6, es el caso típico.
function horario_colono_defecto()
{
    return [
        { hora_inicio: 6,  hora_fin: 8,  actividad: Actividad.COMER    },
        { hora_inicio: 8,  hora_fin: 18, actividad: Actividad.TRABAJAR },
        { hora_inicio: 18, hora_fin: 20, actividad: Actividad.COMER    },
        { hora_inicio: 20, hora_fin: 22, actividad: Actividad.OCIO     },
        { hora_inicio: 22, hora_fin: 6,  actividad: Actividad.DORMIR   },
    ];
}

/// @func horario_actividad(_horario, _hora)
/// @param {Real} _hora  0..24, normalmente objTimeOfDay.tiempo * 24
function horario_actividad(_horario, _hora)
{
    for (var _i = 0; _i < array_length(_horario); _i++)
    {
        var _f = _horario[_i];
        var _dentro = (_f.hora_inicio <= _f.hora_fin)
            ? (_hora >= _f.hora_inicio && _hora < _f.hora_fin)
            : (_hora >= _f.hora_inicio || _hora < _f.hora_fin);   // cruza medianoche
        if (_dentro) return _f.actividad;
    }
    return Actividad.OCIO;
}
```

> 💡 **Un horario por colono, no uno global.** Nada impide que todos compartan el mismo array
> (turnos idénticos para toda la colonia), pero tenerlo por instancia permite turnos de noche,
> guardias rotativas o un médico que come a otra hora sin ningún sistema nuevo — solo otro array.

### 3.2 · El despachador: qué hace el colono este frame

Este bloque corre **antes** del bucle de ejecución del §2.9, en el mismo Step. Decide; el
bloque del §2.9 ejecuta lo que ya estaba en marcha.

```gml
/// obj_colono · Step — despachador de rutina
var _hora      = objTimeOfDay.tiempo * 24;                  // 04 · 09 §5.5
var _actividad = horario_actividad(horario, _hora);
var _urgente   = necesidades.necesidad_mas_urgente(_actividad);   // §4.3

if (_urgente != noone && estado_colono != EstadoColono.ATENDIENDO_NECESIDAD)
{
    // Una necesidad crítica manda sobre CUALQUIER rutina — incluida TRABAJANDO — pero
    // sin tirar la tarea a la basura: tarea_fallar() (§2.7) la libera para que OTRO
    // colono la recoja mientras este come, bebe o duerme.
    if (tarea_actual != noone) { tarea_fallar(tarea_actual); tarea_actual = noone; }

    if (_urgente == NecesidadTipo.SUENO)
    {
        estado_colono = EstadoColono.YENDO_A_DORMIR;                 // §3.4, no pasa por la cola
    }
    else if (_urgente == NecesidadTipo.ANIMO || _urgente == NecesidadTipo.SOCIAL)
    {
        estado_colono = EstadoColono.OCIOSO;    // que decida el despachador de ocio — fuera de
                                                 // alcance de este documento; steering en 04 · 23
    }
    else
    {
        var _t = necesidad_generar_tarea(_urgente, self);     // §4.3
        if (_t == noone) { estado_colono = EstadoColono.OCIOSO; }
        else { tarea_actual = _t; estado_colono = EstadoColono.ATENDIENDO_NECESIDAD; }
    }
}
else if (_actividad == Actividad.DORMIR
      && estado_colono != EstadoColono.YENDO_A_DORMIR
      && estado_colono != EstadoColono.DURMIENDO
      && estado_colono != EstadoColono.ATENDIENDO_NECESIDAD)
{
    if (tarea_actual != noone) { tarea_fallar(tarea_actual); tarea_actual = noone; }
    estado_colono = EstadoColono.YENDO_A_DORMIR;
}
else if (estado_colono == EstadoColono.OCIOSO && _actividad == Actividad.TRABAJAR)
{
    var _tipos = profesion_tipos_permitidos(profesion);
    for (var _i = 0; _i < array_length(_tipos); _i++)
    {
        tarea_actual = colono_buscar_tarea(self, _tipos[_i]);         // §2.5
        if (tarea_actual != noone) { estado_colono = EstadoColono.TRABAJANDO; break; }
    }
}
```

### 3.3 · Interrupción por necesidad urgente, y comer «cuando toca»

`necesidad_mas_urgente()` (§4.3) recibe la actividad programada precisamente para resolver esto
sin dos caminos de código paralelos: durante la franja de `COMER` del horario, el umbral de
hambre se relaja de `UMBRAL_HAMBRE_URGENTE` (20, zona crítica) a `UMBRAL_HAMBRE_RUTINA` (60,
«ya podría comer»). Así un colono con hambre moderada aprovecha su ventana programada, y fuera
de esa ventana solo interrumpe si de verdad es urgente — un único mecanismo para «rutina» y
«urgencia», no dos.

### 3.4 · Ir a dormir a su cama, y despertar

```gml
/// obj_colono · Step — ir a la cama y dormir (fuera del switch de tareas: no es una
/// Tarea de la cola, es un estado propio del colono)
if (estado_colono == EstadoColono.YENDO_A_DORMIR)
{
    if (point_distance(x, y, cama_x, cama_y) <= COLONO_RADIO_INTERACCION)
    {
        estado_colono = EstadoColono.DURMIENDO;
    }
    else if (!mp_potential_step(cama_x, cama_y, velocidad_mov, false))
    {
        // Cama inalcanzable (bloqueada, o el colono está fuera del área cargada):
        // duerme donde está — mejor que quedarse parado para siempre.
        estado_colono = EstadoColono.DURMIENDO;
    }
}
else if (estado_colono == EstadoColono.DURMIENDO)
{
    necesidades.base.update(0.2, TEMPERATURA_INTERIOR_PROMEDIO, true);   // 04 · 09 §5.0,
                                                                          // actividad baja mientras duerme
    var _hora_ahora = objTimeOfDay.tiempo * 24;
    if (horario_actividad(horario, _hora_ahora) != Actividad.DORMIR)
    {
        estado_colono = EstadoColono.OCIOSO;
    }
}
```

> 🔺 **Dormir no usa `duracion_trabajo()` ni el bucle de tareas.** Es deliberado: la duración de
> dormir la marca el horario (cuándo termina la franja `DORMIR`), no un contador de frames — un
> colono que se acuesta tarde duerme menos, exactamente como se espera de una rutina de verdad.

---

## 4 · Necesidades de la población

### 4.1 · Componer `Needs()`, sin tocarla ni repetirla

`Needs()` de `04 · 09` §5.0 fue escrita para **un** personaje: el jugador. Aquí hace falta
**una instancia por colono**, más tres necesidades que ningún survival de un solo personaje
necesita — higiene, ánimo y vida social. La solución no es reescribir `Needs()`: es
**componerla**, el mismo principio que usa `47 · Beat 'em up` §4.3 para extender el `elevacion`
de `04 · 30` sin tocar ese documento.

```gml
// ---------------------------------------------------------------------------
// scr_necesidades_colono
// ---------------------------------------------------------------------------

enum NecesidadTipo { HAMBRE, SED, SUENO, HIGIENE, ANIMO, SOCIAL }

#macro TEMPERATURA_INTERIOR_PROMEDIO 0.5     // confortable — usado mientras el colono
                                              // está DURMIENDO o dormido/abstracto (§7.3)

/// @func NecesidadesColono()
/// @desc `base` es un Needs() íntegro de 04 · 09 §5.0 — instanciado una vez POR COLONO
///       en vez de una vez para todo el juego. `higiene`/`animo`/`social` son nuevas.
function NecesidadesColono() constructor
{
    base = new Needs();

    higiene = 100;
    animo   = 100;
    social  = 100;

    tasa_higiene = 0.02;
    tasa_animo   = 0.01;

    /// @param {Real} _actividad         1.0 normal, más alto = trabajo físico
    /// @param {Real} _temperatura       0..1, la misma escala que usa Needs.update()
    /// @param {Bool} _hay_companeros_cerca
    update = function(_actividad, _temperatura, _hay_companeros_cerca)
    {
        base.update(_actividad, _temperatura);

        higiene = max(0, higiene - tasa_higiene * _actividad);
        animo   = _hay_companeros_cerca ? min(100, animo + 0.04)  : max(0, animo  - tasa_animo);
        social  = _hay_companeros_cerca ? min(100, social + 0.06) : max(0, social - 0.02);

        // El buen humor depende de lo demás: comer y dormir bien no es un lujo aparte.
        if (base.alguna_critica()) animo = max(0, animo - 0.03);
    };

    /// @desc La necesidad más urgente ahora mismo, o `noone` si todo va bien. Compara
    ///       CADA necesidad contra SU propio umbral (no valores absolutos entre sí:
    ///       hambre y ánimo no están en la misma escala de urgencia real) y se queda
    ///       con la que más se pasa de su umbral.
    /// @param {Real} _actividad_programada  Actividad del horario (§3.1) — relaja el
    ///        umbral de hambre durante la franja de comer (§3.3).
    necesidad_mas_urgente = function(_actividad_programada)
    {
        var _umbral_hambre = (_actividad_programada == Actividad.COMER)
            ? UMBRAL_HAMBRE_RUTINA : UMBRAL_HAMBRE_URGENTE;

        // variable_struct_get() en vez de acceso directo (`base.hambre`): el snippet no
        // depende de cómo esté escrito por dentro el campo de Needs() — solo de su
        // nombre público, que es lo que 04 · 09 §5.0 sí garantiza.
        var _candidatas = [
            { tipo: NecesidadTipo.HAMBRE,  valor: variable_struct_get(base, "hambre"), umbral: _umbral_hambre        },
            { tipo: NecesidadTipo.SED,     valor: variable_struct_get(base, "sed"),    umbral: UMBRAL_SED_URGENTE    },
            { tipo: NecesidadTipo.SUENO,   valor: variable_struct_get(base, "sueno"),  umbral: UMBRAL_SUENO_URGENTE  },
            { tipo: NecesidadTipo.HIGIENE, valor: higiene, umbral: UMBRAL_HIGIENE_URGENTE },
            { tipo: NecesidadTipo.ANIMO,   valor: animo,   umbral: UMBRAL_ANIMO_URGENTE   },
        ];

        var _peor = noone, _peor_margen = 0;
        for (var _i = 0; _i < array_length(_candidatas); _i++)
        {
            var _c = _candidatas[_i];
            var _margen = _c.umbral - _c.valor;     // > 0 → por debajo del umbral
            if (_margen > _peor_margen) { _peor_margen = _margen; _peor = _c.tipo; }
        }
        return _peor;
    };

    serialize = function()
    {
        return { base: base.serialize(), higiene: higiene, animo: animo, social: social };
    };

    static deserialize = function(_d)
    {
        var _n = new NecesidadesColono();
        _n.base    = Needs.deserialize(_d.base);      // 04 · 09 §5.0
        _n.higiene = _d.higiene;
        _n.animo   = _d.animo;
        _n.social  = _d.social;
        return _n;
    };
}
```

### 4.2 · Decaimiento, umbrales y efectos al llegar a cero

Los umbrales viven como macros en `scr_config_colonia.gml` (§1.4): `UMBRAL_HAMBRE_URGENTE`,
`UMBRAL_SED_URGENTE`, `UMBRAL_SUENO_URGENTE`, `UMBRAL_HIGIENE_URGENTE`, `UMBRAL_ANIMO_URGENTE`.
El decaimiento de `hambre`/`sed`/`calor`/`sueño` sigue exactamente la fórmula de `04 · 09` §5.0
(`daño_por_frame()`, `multiplicador_velocidad()`) — **no se repite aquí**: un colono con hambre
crítica ya se mueve más lento y pierde vida por el mismo mecanismo del jugador, gratis, por
composición. Lo único nuevo son los efectos de `higiene`/`animo`/`social` al llegar a cero, y son
deliberadamente suaves en vez de letales — es una colonia, no un roguelike de supervivencia:

| Necesidad a 0 | Efecto |
|---|---|
| Higiene | `animo` decae el doble hasta que se asee (penalización en `update()`, no una nueva variable) |
| Ánimo | El colono deja de aceptar tareas de prioridad baja: extiende `colono_buscar_tarea()` con un filtro `if (_prioridad_minima > 0 && _t.prioridad < _prioridad_minima) continue;` |
| Social | Igual que ánimo, con un umbral más permisivo — se combinan, no se apilan aparte |

### 4.3 · Cómo una necesidad genera una tarea

Esto es lo que el informe r3 pide explícitamente y no existía en ningún sitio: el enganche entre
«algo va mal» y «hay una tarea real en el mundo». A diferencia del §2, esto **no pasa por la
cola compartida** — es personal e inmediato, así que se crea la `Tarea` y se marca reservada por
el colono directamente. Aquí sí encaja `instance_nearest`: no para elegir entre tareas (son
structs, §2.5), sino para encontrar el edificio de servicio más cercano, que **sí** es una
instancia real de GameMaker.

```gml
// ---------------------------------------------------------------------------
// scr_necesidad_tarea
// ---------------------------------------------------------------------------

/// @func necesidad_generar_tarea(_tipo, _colono)
/// @desc Solo HAMBRE/SED/HIGIENE llegan aquí — SUENO/ANIMO/SOCIAL se resuelven
///       cambiando de estado directamente en el despachador (§3.2), sin Tarea.
function necesidad_generar_tarea(_tipo, _colono)
{
    var _t = noone;

    switch (_tipo)
    {
        case NecesidadTipo.HAMBRE:
            var _comedor = instance_nearest(_colono.x, _colono.y, obj_comedor);
            if (_comedor == noone) return noone;
            _t = new Tarea(TipoTrabajo.COMER, _comedor.x div CELL, _comedor.y div CELL,
                            PRIORIDAD_NECESIDAD_URGENTE);
            break;

        case NecesidadTipo.SED:
            var _pozo = instance_nearest(_colono.x, _colono.y, obj_pozo);
            if (_pozo == noone) return noone;
            _t = new Tarea(TipoTrabajo.BEBER, _pozo.x div CELL, _pozo.y div CELL,
                            PRIORIDAD_NECESIDAD_URGENTE);
            break;

        case NecesidadTipo.HIGIENE:
            var _banos = instance_nearest(_colono.x, _colono.y, obj_banos);
            if (_banos == noone) return noone;
            _t = new Tarea(TipoTrabajo.ASEARSE, _banos.x div CELL, _banos.y div CELL,
                            PRIORIDAD_NECESIDAD_URGENTE);
            break;

        default:
            return noone;
    }

    // Nunca pasa por ColaTrabajos.encolar(): tarea_id se queda en -1 a propósito (es
    // la marca que lee tarea_fallar() en §2.7 para no reencolarla en el tablón global).
    _t.reservada_por = _colono;
    _t.estado        = EstadoTarea.RESERVADA;
    return _t;
}
```

Amplía el catálogo de recetas de `04 · 09` §5.1 con la que usa `TipoTrabajo.COCINAR` (mismo
patrón que `global.recipes.hacha_piedra`, no una función nueva):

```gml
// En recipes_init() de tu proyecto, junto a las demás — no reescribas 04 · 09 §5.1
global.recipes.racion = new Recipe(
    "racion", "Ración de comida", "cocina",
    { comida_cruda: 2 },
    { id: "racion", cantidad: 1 }, 0);
```

> ⚠️ **`obj_comedor`, `obj_pozo` y `obj_banos` son objetos nuevos de tu proyecto**, no de esta
> biblioteca ni de `04 · 09`: cualquier objeto estático con posición sirve — no necesitan lógica
> propia, solo existir para que `instance_nearest` los encuentre.

---

## 5 · Construcción con integridad estructural

### 5.1 · Plano frente a construido: dos capas, no una

`WorldGrid`/`objWorldGrid` de `04 · 09` §5.3 sigue siendo, **sin cambios**, la fuente de verdad
de lo que YA está construido: `ocupada()`, `ocupar()`, `liberar()`. Lo que falta es la capa
de **antes**: un plano no ocupa la rejilla de construcción todavía — solo reserva la intención,
y bloquea que otro plano se solape con él mientras espera materiales.

```gml
// ---------------------------------------------------------------------------
// scr_planos
// ---------------------------------------------------------------------------

/// @func PlanConstruccion(_tipo, _celda_x, _celda_y)
/// @desc `materiales_necesarios` es EXACTAMENTE `Recipe.ingredientes` de 04 · 09 §5.1
///       — un struct `{ madera: 8, piedra: 4 }`, no un array. `materiales_entregados`
///       usa las mismas claves.
function PlanConstruccion(_tipo, _celda_x, _celda_y) constructor
{
    tipo    = _tipo;
    celda_x = _celda_x;
    celda_y = _celda_y;
    tarea_construir_id = undefined;

    var _receta = recipe_get(_tipo);                    // 04 · 09 §5.1, reutilizado
    materiales_necesarios = _receta.ingredientes;
    materiales_entregados = {};

    completo = function()
    {
        var _claves = variable_struct_get_names(materiales_necesarios);
        for (var _i = 0; _i < array_length(_claves); _i++)
        {
            var _mat    = _claves[_i];
            var _traido = materiales_entregados[$ _mat] ?? 0;
            if (_traido < materiales_necesarios[$ _mat]) return false;
        }
        return true;
    };

    entregar = function(_item, _cantidad)
    {
        materiales_entregados[$ _item] = (materiales_entregados[$ _item] ?? 0) + _cantidad;
    };
}

global.planos = {};             // "x,y" → PlanConstruccion, separado de objWorldGrid.celdas
```

### 5.2 · Colocar un plano: la MISMA validación de 04 · 09, en modo diferido

`04 · 09` §5.3 ya corrige su propia comprobación de colocación (`objWorldGrid.ocupada()` +
`point_distance()`, ver el aviso `⚠️ Corregido` dentro de ese documento) — este documento la
**reutiliza tal cual**, añadiendo solo que un plano no puede solaparse con otro plano, y que
colocarlo no crafta ni gasta nada al momento: encola tareas `TRANSPORTAR` por cada material que
falte.

```gml
/// obj_planificador_colonia · Step — colocar un plano
if (modo_planificar && mouse_check_button_pressed(mb_left))
{
    var _gx = mouse_x div CELL, _gy = mouse_y div CELL;
    var _k  = string(_gx) + "," + string(_gy);

    var _valido = !objWorldGrid.ocupada(_gx, _gy)              // 04 · 09 §5.3
               && !variable_struct_exists(global.planos, _k)
               && terreno_es_construible(_gx, _gy)
               && point_distance(objPlayer.x, objPlayer.y, _gx * CELL, _gy * CELL) <= RANGO_CONSTRUCCION;  // 04 · 09 §5.3

    if (_valido)
    {
        var _plan = new PlanConstruccion(tipo_seleccionado, _gx, _gy);
        global.planos[$ _k] = _plan;

        var _claves = variable_struct_get_names(_plan.materiales_necesarios);
        for (var _i = 0; _i < array_length(_claves); _i++)
        {
            var _mat = _claves[_i];
            var _t = new Tarea(TipoTrabajo.TRANSPORTAR, global.almacen_pos.celda_x,
                                global.almacen_pos.celda_y, PRIORIDAD_CONSTRUCCION);
            _t.carga_item     = _mat;
            _t.carga_cantidad = _plan.materiales_necesarios[$ _mat];
            _t.destino_x = _gx;  _t.destino_y = _gy;
            global.cola_trabajos.encolar(_t);
        }
    }
}

/// @func terreno_es_construible(_celda_x, _celda_y)
/// @desc Filtro adicional al de ocupación: agua o roca no se pueden pisar. Ajusta la
///       tilemap a la del proyecto — reutiliza `global.tilemap_terreno` de 04 · 09 §5.4.
function terreno_es_construible(_celda_x, _celda_y)
{
    var _tile = tilemap_get(global.tilemap_terreno, _celda_x, _celda_y);
    return _tile != TILE_AGUA && _tile != TILE_PARED_ROCA;
}
```

> ⚠️ **`global.almacen_pos`** (`{ celda_x, celda_y }`) es la celda del almacén central de la
> colonia — se fija cuando se coloca ese edificio, igual que `cama_x`/`cama_y` en `obj_colono`
> (§2.9). El origen de un `TRANSPORTAR` es siempre el almacén en este documento: para acarrear
> directo desde el suelo (talar sin pasar por almacén), añade un origen con `objetivo_inst` como
> hace el paso `TRABAJAR` de TALAR/MINAR (§2.9) — no se repite aquí por espacio.

### 5.3 · Materiales que hay que traer: la construcción como tarea final

```gml
/// @func plan_intentar_completar(_plan)
/// @desc Se llama tras CADA entrega (paso SOLTAR, §2.9). En cuanto el plano tiene
///       todo, encola la única tarea CONSTRUIR — sin duplicarla si ya se encoló.
function plan_intentar_completar(_plan)
{
    if (_plan.tarea_construir_id != undefined) return;
    if (!_plan.completo()) return;

    var _t = new Tarea(TipoTrabajo.CONSTRUIR, _plan.celda_x, _plan.celda_y, PRIORIDAD_CONSTRUCCION);
    _plan.tarea_construir_id = global.cola_trabajos.encolar(_t);
}

/// @func construccion_levantar(_celda_x, _celda_y)
/// @desc El efecto de la tarea CONSTRUIR (§2.9 tarea_completar_efecto): crea la
///       instancia real con el MISMO patrón que 04 · 09 §5.3 (mismo objStructure,
///       mismo objWorldGrid.ocupar()) y borra el plano.
function construccion_levantar(_celda_x, _celda_y)
{
    var _k    = string(_celda_x) + "," + string(_celda_y);
    var _plan = global.planos[$ _k];
    if (_plan == undefined) return;

    var _s = instance_create_depth(_celda_x * CELL + CELL * 0.5, _celda_y * CELL + CELL * 0.5,
                                   -_celda_y * CELL, objStructure);
    _s.tipo_estructura = _plan.tipo;
    _s.grid_x = _celda_x;
    _s.grid_y = _celda_y;
    objWorldGrid.ocupar(_s.grid_x, _s.grid_y, _s);

    variable_struct_remove(global.planos, _k);
    soporte_aplicar_colapso(objWorldGrid, global.anclas_soporte);   // §5.4: puede desbloquear vecinos
    habitaciones_recalcular_si_toca();                              // §5.5
}
```

### 5.4 · Soporte estructural: propagación desde el suelo, y colapso en cascada

El mismo *flood fill* de `04 · 05` §5.4 (`dungeon_flood_fill`, BFS de 4-vecinos) resuelve
«¿hasta dónde llega el soporte?» con un cambio de una palabra: en vez de expandir sobre
**suelo transitable**, expande sobre **celdas ocupadas** de `objWorldGrid`, y en vez de partir
de un único punto de inicio, parte de un conjunto de **anclas** (el suelo natural, o cimientos
marcados a mano) con distancia 0.

```gml
// ---------------------------------------------------------------------------
// scr_soporte_estructural
// ---------------------------------------------------------------------------

/// @func soporte_calcular(_grid, _anclas)
/// @param {Array<Array<Real>>} _anclas  [[x,y], ...] — distancia 0 por definición
/// @returns {Struct} "x,y" → distancia (Real). Ausente = sin soporte.
function soporte_calcular(_grid, _anclas)
{
    var _distancia = {};
    var _cola = [];

    for (var _i = 0; _i < array_length(_anclas); _i++)
    {
        var _k = string(_anclas[_i][0]) + "," + string(_anclas[_i][1]);
        _distancia[$ _k] = 0;
        array_push(_cola, _anclas[_i]);
    }

    while (array_length(_cola) > 0)
    {
        var _celda = array_pop(_cola);
        var _cx = _celda[0], _cy = _celda[1];
        var _d  = _distancia[$ (string(_cx) + "," + string(_cy))];
        if (_d >= SOPORTE_DISTANCIA_MAX) continue;

        var _vecinos = [[_cx+1,_cy], [_cx-1,_cy], [_cx,_cy+1], [_cx,_cy-1]];
        for (var _i = 0; _i < 4; _i++)
        {
            var _nx = _vecinos[_i][0], _ny = _vecinos[_i][1];
            if (!_grid.ocupada(_nx, _ny)) continue;
            var _nk = string(_nx) + "," + string(_ny);
            if (variable_struct_exists(_distancia, _nk)) continue;
            _distancia[$ _nk] = _d + 1;
            array_push(_cola, [_nx, _ny]);
        }
    }
    return _distancia;
}

/// @func estructura_derrumbar(_inst)
/// @desc Destruye y suelta una fracción de los materiales — mismo patrón de
///       objItemDrop que 04 · 09 §5.2 romper(), no una función nueva de "soltar ítem".
function estructura_derrumbar(_inst)
{
    var _receta = recipe_get(_inst.tipo_estructura);
    objWorldGrid.liberar(_inst.grid_x, _inst.grid_y);       // 04 · 09 §5.3

    if (_receta != undefined)
    {
        var _claves = variable_struct_get_names(_receta.ingredientes);
        for (var _i = 0; _i < array_length(_claves); _i++)
        {
            var _mat  = _claves[_i];
            var _cant = floor(_receta.ingredientes[$ _mat] * MATERIAL_RECUPERADO_DERRUMBE);
            for (var _j = 0; _j < _cant; _j++)
            {
                var _item = instance_create_layer(_inst.x + irandom_range(-12, 12),
                                                   _inst.y + irandom_range(-6, 6),
                                                   "Items", objItemDrop);
                _item.item_id = _mat;
            }
        }
    }
    senal_emitir("estructura_derrumbada", { x: _inst.x, y: _inst.y, tipo: _inst.tipo_estructura });
    instance_destroy(_inst);
}

/// @func soporte_aplicar_colapso(_grid, _anclas)
/// @desc Recalcula el soporte y derrumba cualquier celda ocupada sin camino a un
///       ancla en SOPORTE_DISTANCIA_MAX pasos. Se llama tras CADA construcción o
///       demolición — no cada frame: solo puede cambiar justo cuando algo (des)aparece.
function soporte_aplicar_colapso(_grid, _anclas)
{
    var _distancia = soporte_calcular(_grid, _anclas);
    var _claves    = variable_struct_get_names(_grid.celdas);

    for (var _i = 0; _i < array_length(_claves); _i++)
    {
        var _k = _claves[_i];
        if (variable_struct_exists(_distancia, _k)) continue;    // sigue soportada

        var _inst = _grid.celdas[$ _k];
        if (instance_exists(_inst)) estructura_derrumbar(_inst);
    }
}
```

> 🔺 **Llama a `soporte_aplicar_colapso()` también tras una demolición manual**, no solo tras
> construir (§5.3 ya lo hace). Quitar la pared que sostenía un segundo piso es el caso de uso
> real de este sistema — sin la llamada tras demoler, el juego deja estructuras flotando.

### 5.5 · Habitaciones detectadas por *flood fill*

Mismo patrón otra vez, invertido: en vez de expandir sobre celdas **ocupadas** (soporte, arriba),
expande sobre celdas **vacías** delimitadas por ocupadas. Una habitación es una bolsa de vacío
que no toca el borde del mapa — si lo toca, es el exterior, no una habitación.

```gml
/// @func habitaciones_detectar(_grid, _ancho, _alto)
/// @returns {Array<Struct>} cada región: { celdas: [[x,y],...], cerrada: Bool }
function habitaciones_detectar(_grid, _ancho, _alto)
{
    var _visitado = {};
    var _regiones = [];

    for (var _y = 0; _y < _alto; _y++)
    {
        for (var _x = 0; _x < _ancho; _x++)
        {
            var _k0 = string(_x) + "," + string(_y);
            if (_grid.ocupada(_x, _y) || variable_struct_exists(_visitado, _k0)) continue;

            var _celdas  = [];
            var _cola    = [[_x, _y]];
            var _cerrada = true;
            _visitado[$ _k0] = true;

            while (array_length(_cola) > 0)
            {
                var _c  = array_pop(_cola);
                var _cx = _c[0], _cy = _c[1];
                array_push(_celdas, _c);

                if (_cx <= 0 || _cy <= 0 || _cx >= _ancho - 1 || _cy >= _alto - 1) _cerrada = false;

                var _vecinos = [[_cx+1,_cy], [_cx-1,_cy], [_cx,_cy+1], [_cx,_cy-1]];
                for (var _i = 0; _i < 4; _i++)
                {
                    var _nx = _vecinos[_i][0], _ny = _vecinos[_i][1];
                    if (_nx < 0 || _ny < 0 || _nx >= _ancho || _ny >= _alto) continue;
                    if (_grid.ocupada(_nx, _ny)) continue;
                    var _nk = string(_nx) + "," + string(_ny);
                    if (variable_struct_exists(_visitado, _nk)) continue;
                    _visitado[$ _nk] = true;
                    array_push(_cola, [_nx, _ny]);
                }
            }
            array_push(_regiones, { celdas: _celdas, cerrada: _cerrada });
        }
    }
    return _regiones;
}

global.habitaciones = [];
global.habitaciones_ultimo_calculo = 0;

/// @func habitaciones_recalcular_si_toca()
/// @desc Como mucho una vez cada HABITACIONES_FRAMES_MIN_MS: construir 5 paredes
///       seguidas no debe disparar 5 recálculos completos del mapa.
function habitaciones_recalcular_si_toca()
{
    if (current_time - global.habitaciones_ultimo_calculo < HABITACIONES_FRAMES_MIN_MS) return;
    global.habitaciones_ultimo_calculo = current_time;
    global.habitaciones = habitaciones_detectar(objWorldGrid, global.colonia_ancho, global.colonia_alto);
}
```

> 💡 **Una habitación `cerrada` es la entrada de datos, no el sistema entero.** A partir de aquí,
> «cuánto oxígeno tiene» o «qué temperatura mantiene» es sumar/promediar sobre `region.celdas` —
> exactamente el mismo array que ya devuelve esta función, sin tocarla.

---

## 6 · Redes de energía y fluidos

### 6.1 · El vocabulario, reutilizado sin repetirlo

`13 · 01` §4.1 ya da el vocabulario: **Pool** (una reserva con capacidad), **Fuente**
(produce sin consumir), **Sumidero** (consume sin producir), **Convertidor** (una cosa se
convierte en otra). El único «recurso energía» que existía antes en esta biblioteca
(`04 · 13` §5.3, `recursos.energia`) es un **contador global plano**, sin espacio: no hay forma
de que un generador en una esquina del mapa no llegue a un consumidor en la otra. Lo que falta,
y es lo que aporta este apartado, es la versión **espacial** de esos mismos conceptos: un Pool
por cada región conectada de la rejilla, no uno por partida.

### 6.2 · Nodos como grafo sobre la rejilla

```gml
// ---------------------------------------------------------------------------
// scr_red_energia
// ---------------------------------------------------------------------------

enum NodoEnergia { PRODUCTOR, CONSUMIDOR, CONDUCTOR, ALMACEN }

/// @func RedEnergia()
/// @desc Un grafo disperso sobre celdas de rejilla — MISMA forma que objWorldGrid
///       (04 · 09 §5.3: clave "x,y" → dato), pero es una red propia, no la de
///       construcción: un cable y una pared ocupan la MISMA celda sin pisarse.
function RedEnergia() constructor
{
    nodos = {};      // "x,y" → { tipo, capacidad, consumo, prioridad, suministrado,
                      //           almacenado, almacenado_max }

    clave = function(_x, _y) { return string(_x) + "," + string(_y); };

    /// @param {Real} _valor      capacidad (PRODUCTOR/ALMACEN) o consumo (CONSUMIDOR); 0 en CONDUCTOR
    /// @param {Real} _prioridad  solo importa en CONSUMIDOR — más alto se corta el último (§6.3)
    registrar = function(_x, _y, _tipo, _valor, _prioridad = 50)
    {
        nodos[$ clave(_x, _y)] = {
            tipo:      _tipo,
            capacidad: (_tipo == NodoEnergia.PRODUCTOR) ? _valor : 0,
            consumo:   (_tipo == NodoEnergia.CONSUMIDOR) ? _valor : 0,
            prioridad: _prioridad,
            suministrado:   true,
            almacenado:     0,
            almacenado_max: (_tipo == NodoEnergia.ALMACEN) ? _valor : 0
        };
    };

    quitar = function(_x, _y) { variable_struct_remove(nodos, clave(_x, _y)); };

    /// @desc Todas las celdas conectadas a (_x,_y) por 4-vecindad de nodos registrados
    ///       de ESTA red — el MISMO flood fill del §5.4/§5.5 y de 04 · 05 §5.4, esta
    ///       vez sobre "es nodo de la red" en vez de "es soporte" o "está vacío".
    red_conectada = function(_x, _y)
    {
        var _k0 = clave(_x, _y);
        if (!variable_struct_exists(nodos, _k0)) return [];

        var _visitado = {};
        var _cola = [[_x, _y]];
        var _out  = [];
        _visitado[$ _k0] = true;

        while (array_length(_cola) > 0)
        {
            var _c = array_pop(_cola);
            array_push(_out, _c);
            var _vecinos = [[_c[0]+1,_c[1]], [_c[0]-1,_c[1]], [_c[0],_c[1]+1], [_c[0],_c[1]-1]];
            for (var _i = 0; _i < 4; _i++)
            {
                var _nk = clave(_vecinos[_i][0], _vecinos[_i][1]);
                if (!variable_struct_exists(nodos, _nk) || variable_struct_exists(_visitado, _nk)) continue;
                _visitado[$ _nk] = true;
                array_push(_cola, _vecinos[_i]);
            }
        }
        return _out;
    };
}

global.red_energia = new RedEnergia();
```

### 6.3 · Propagación, almacenamiento, déficit y prioridad de reparto

Una pasada **por red conectada**, no por celda: sumar toda la producción y toda la demanda de un
grupo conectado, y repartir. Si sobra, llena los `ALMACEN` hasta el tope. Si falta, primero tira
de los almacenes y, si sigue faltando, corta a los consumidores de **menor** prioridad primero.

```gml
/// @func red_actualizar(_red)
/// @desc Una vez por tick de simulación (§7.2), nunca nodo a nodo ni cada frame.
function red_actualizar(_red)
{
    var _procesados = {};
    var _claves = variable_struct_get_names(_red.nodos);

    for (var _i = 0; _i < array_length(_claves); _i++)
    {
        var _k0 = _claves[_i];
        if (variable_struct_exists(_procesados, _k0)) continue;

        var _partes = string_split(_k0, ",");
        var _grupo  = _red.red_conectada(real(_partes[0]), real(_partes[1]));

        var _produccion = 0, _demanda = 0;
        for (var _j = 0; _j < array_length(_grupo); _j++)
        {
            var _nk = _red.clave(_grupo[_j][0], _grupo[_j][1]);
            _procesados[$ _nk] = true;
            var _n = _red.nodos[$ _nk];

            if (_n.tipo == NodoEnergia.PRODUCTOR)  _produccion += _n.capacidad;
            if (_n.tipo == NodoEnergia.CONSUMIDOR) { _demanda += _n.consumo; _n.suministrado = true; }
        }

        var _balance = _produccion - _demanda;

        if (_balance >= 0)
        {
            var _sobrante = _balance;
            for (var _j = 0; _j < array_length(_grupo) && _sobrante > 0; _j++)
            {
                var _n = _red.nodos[$ _red.clave(_grupo[_j][0], _grupo[_j][1])];
                if (_n.tipo != NodoEnergia.ALMACEN) continue;
                var _mete = min(_n.almacenado_max - _n.almacenado, _sobrante);
                _n.almacenado += _mete;
                _sobrante     -= _mete;
            }
        }
        else
        {
            var _falta = -_balance;

            // 1. Tira de los almacenes de la red antes de cortar a nadie.
            for (var _j = 0; _j < array_length(_grupo) && _falta > 0; _j++)
            {
                var _n = _red.nodos[$ _red.clave(_grupo[_j][0], _grupo[_j][1])];
                if (_n.tipo != NodoEnergia.ALMACEN) continue;
                var _saca = min(_n.almacenado, _falta);
                _n.almacenado -= _saca;
                _falta        -= _saca;
            }

            // 2. Si sigue faltando: corta consumidores de MENOR prioridad primero.
            if (_falta > 0)
            {
                var _consumidores = [];
                for (var _j = 0; _j < array_length(_grupo); _j++)
                {
                    var _n = _red.nodos[$ _red.clave(_grupo[_j][0], _grupo[_j][1])];
                    if (_n.tipo == NodoEnergia.CONSUMIDOR) array_push(_consumidores, _n);
                }
                // Orden DESCENDENTE de prioridad: el final del array es la prioridad más baja.
                array_sort(_consumidores, function(_a, _b) { return _b.prioridad - _a.prioridad; });

                for (var _j = array_length(_consumidores) - 1; _j >= 0 && _falta > 0; _j--)
                {
                    _consumidores[_j].suministrado = false;
                    _falta -= _consumidores[_j].consumo;
                }
            }
        }
    }
}
```

> ⚠️ **`_n.suministrado` es lo que lee un edificio consumidor para saber si tiene energía.** Se
> pone a `true` para TODOS los consumidores al inicio de cada pasada por grupo, y solo se apaga
> en el paso 2 del déficit — sin ese reinicio, un edificio cortado una vez se queda sin energía
> para siempre aunque la red se recupere.

### 6.4 · Tuberías y caudal: red dirigida sobre el líquido de `13 · 08`

`13 · 08` §10 ya resuelve el **líquido en sí** — presión, nivel, flujo entre celdas abiertas con
su autómata celular. Lo que falta, y lo que aporta este apartado, es una **red dirigida** encima:
tuberías que conectan un depósito con una máquina, no un charco abierto. Se modela con la MISMA
`RedEnergia` de arriba, cambiando el vocabulario: `capacidad` → `caudal_max`, `consumo` →
`demanda`. La única regla nueva es el **cuello de botella**: el caudal efectivo de un tramo lo
marca el nodo con menor `caudal_max` de todo el grupo, no la suma.

```gml
/// @func red_caudal_efectivo(_red, _grupo)
/// @desc El cuello de botella del tramo (tema 39 del informe r3: "cuellos de botella
///       sin diagnóstico"). Se aplica como tope extra sobre red_actualizar() antes de
///       repartir: `_produccion = min(_produccion, red_caudal_efectivo(_red, _grupo))`.
function red_caudal_efectivo(_red, _grupo)
{
    var _minimo = infinity;
    for (var _i = 0; _i < array_length(_grupo); _i++)
    {
        var _n = _red.nodos[$ _red.clave(_grupo[_i][0], _grupo[_i][1])];
        if (_n.tipo == NodoEnergia.CONDUCTOR) _minimo = min(_minimo, _n.capacidad);
    }
    return (_minimo == infinity) ? infinity : _minimo;
}
```

> ⚠️ **Esto es una aproximación de tablero, no una simulación de presión real.** Si el juego
> necesita presión/nivel de verdad por tramo (una tubería que se puede reventar, un tanque que
> se puede vaciar por gravedad), la respuesta correcta es aplicar directamente el autómata
> celular de `13 · 08` §10 en vez de esta capa de red — esta capa sirve para decidir SI llega
> caudal a una máquina, no para animar el líquido en sí.

---

## 7 · Simulación fuera de pantalla

### 7.1 · LOD de simulación: activo, lento, abstracto

`04 · 31` §12 ya resuelve el caso binario (activo/desactivado); el informe r3 (tema 78) señala
que ese binario es exactamente lo que **no** sirve aquí: una instancia desactivada no avanza sus
necesidades ni termina sus tareas, así que un colono «apagado» durante media hora vuelve con
hambre negativa sin que nadie lo haya simulado. Hace falta un tercer estado.

```gml
// ---------------------------------------------------------------------------
// scr_lod_colonia
// ---------------------------------------------------------------------------

enum LODSimulacion { ACTIVO, LENTO, ABSTRACTO }

/// @func lod_calcular(_wx, _wy, _pcx, _pcy)
/// @desc Mismo tamaño de chunk que 04 · 09 §5.4 (CHUNK_PX): el propio chunk del
///       jugador es ACTIVO, los cargados-pero-lejos son LENTO, el resto — que
///       04 · 09 §5.4 ya ni siquiera mantiene cargado — es ABSTRACTO.
function lod_calcular(_wx, _wy, _pcx, _pcy)
{
    var _cx = _wx div CHUNK_PX, _cy = _wy div CHUNK_PX;
    var _dist_chunks = max(abs(_cx - _pcx), abs(_cy - _pcy));

    if (_dist_chunks <= 0)          return LODSimulacion.ACTIVO;
    if (_dist_chunks <= RADIO_CARGA) return LODSimulacion.LENTO;
    return LODSimulacion.ABSTRACTO;
}
```

### 7.2 · Actualización por lotes

Un colono en `LENTO` sigue siendo una instancia, pero no necesita pensar 60 veces por segundo:
mismo tick escalonado de `04 · 31` §12, aplicado al despachador de rutina (§3.2) en vez de a un
árbol de comportamiento.

```gml
/// obj_colono · Create
grupo_lod = irandom(9);          // reparte en 10 grupos, igual que 04 · 31 §12

/// obj_colono · Step — el despachador del §3.2 solo corre cada frame en ACTIVO
var _lod = lod_calcular(x, y, global.jugador_chunk_x, global.jugador_chunk_y);

if (_lod == LODSimulacion.ACTIVO || (current_time div 100) mod 10 == grupo_lod)
{
    // ...bloque del §3.2 (despachador de rutina) aquí...
}
// el bucle de EJECUCIÓN de la tarea actual (§2.9) SIGUE corriendo todos los frames,
// igual que 04 · 31 §12 avisa: separar decidir (escalonado) de moverse/actuar (cada frame).
```

### 7.3 · Entidades dormidas: un tercer estado, no encendido/apagado

Cuando un colono sale del radio cargado (`04 · 09` §5.4, `descargar_chunk()`), en vez de
`instance_deactivate_object()` se convierte en un registro de datos barato que **sigue
avanzando**, y se reconstruye al volver a cargar el chunk.

```gml
// ---------------------------------------------------------------------------
// scr_colonos_dormidos
// ---------------------------------------------------------------------------

/// @func ColonoDormido(_colono)
function ColonoDormido(_colono) constructor
{
    perfil_x    = _colono.x;
    perfil_y    = _colono.y;
    profesion   = _colono.profesion;
    necesidades = _colono.necesidades;      // el struct entero, con sus métodos — se
                                             // lleva consigo, no se reconstruye desde cero
}

global.colonos_dormidos = {};    // "cx,cy" → array de ColonoDormido

/// @func colono_dormir(_colono)
/// @desc Se llama desde el mismo punto donde tu copia de 04 · 09 §5.4
///       (descargar_chunk) desactiva enemigos/drops — una línea añadida ahí, sin
///       tocar ese documento.
function colono_dormir(_colono)
{
    var _cx = _colono.x div CHUNK_PX, _cy = _colono.y div CHUNK_PX;
    var _k  = string(_cx) + "," + string(_cy);

    if (!variable_struct_exists(global.colonos_dormidos, _k)) global.colonos_dormidos[$ _k] = [];
    array_push(global.colonos_dormidos[$ _k], new ColonoDormido(_colono));

    if (_colono.tarea_actual != noone) tarea_fallar(_colono.tarea_actual);   // §2.7: libera, no descarta
    instance_destroy(_colono);
}

/// @func colonos_dormidos_avanzar(_k, _pasos)
/// @desc Necesidades a paso grande en vez de mil pasos pequeños — mismo principio que
///       04 · 45 §6.4 progreso_offline_aplicar(), aplicado por colono en vez de al
///       juego entero. Sin instancia no hay quien ejecute el job system: la actividad
///       de fondo es siempre "reposo", nunca "trabajando".
function colonos_dormidos_avanzar(_k, _pasos)
{
    if (!variable_struct_exists(global.colonos_dormidos, _k)) return;
    var _lista = global.colonos_dormidos[$ _k];

    for (var _i = 0; _i < array_length(_lista); _i++)
    {
        var _c = _lista[_i];
        repeat (min(_pasos, LOD_PASOS_ABSTRACTOS_MAX))
        {
            _c.necesidades.update(1.0, TEMPERATURA_INTERIOR_PROMEDIO, false);
        }
    }
}

/// @func colono_despertar_chunk(_cx, _cy)
/// @desc Se llama desde el mismo punto donde 04 · 09 §5.4 (cargar_chunk) activa la
///       región — recrea la instancia de cada colono dormido de ese chunk.
function colono_despertar_chunk(_cx, _cy)
{
    var _k = string(_cx) + "," + string(_cy);
    if (!variable_struct_exists(global.colonos_dormidos, _k)) return;

    var _lista = global.colonos_dormidos[$ _k];
    for (var _i = 0; _i < array_length(_lista); _i++)
    {
        var _c = _lista[_i];
        var _inst = instance_create_depth(_c.perfil_x, _c.perfil_y, -_c.perfil_y, obj_colono);
        _inst.profesion     = _c.profesion;
        _inst.necesidades   = _c.necesidades;
        _inst.estado_colono = EstadoColono.OCIOSO;
    }
    variable_struct_remove(global.colonos_dormidos, _k);
}
```

### 7.4 · El presupuesto de coste real

`13 · 08` §14 fija la referencia: **16 666 µs por frame para TODO**, a 60 fps. Este documento se
lleva un presupuesto propio, medido con `get_timer()` igual que esa sección, y **amortiza** el
trabajo de fondo (expirar tareas, actualizar redes, avanzar colonos dormidos) en vez de hacerlo
todo de golpe: si se agota el presupuesto, el resto espera al frame siguiente — el mismo
principio de `MAX_PASOS_POR_FRAME` de `13 · 06` §3.9, aplicado a una cola de trabajo en vez de a
pasos de física.

```gml
/// obj_simulador_colonia · Create
global.cola_lotes_pendientes = [];       // functions pendientes de ejecutar este frame
coste_simulacion_us = 0;

function tick_red_energia() { red_actualizar(global.red_energia); }    // §6.3

/// obj_simulador_colonia · Step — encola el trabajo periódico (expirar tareas ya
/// corre solo, en obj_tablon_trabajos · Step, §2.3) y luego lo amortiza
if (global.frame_count mod COLONOS_DORMIDOS_CADA_FRAMES == 0)
{
    var _claves = variable_struct_get_names(global.colonos_dormidos);   // §7.3
    for (var _i = 0; _i < array_length(_claves); _i++)
    {
        colonos_dormidos_avanzar(_claves[_i], COLONOS_DORMIDOS_CADA_FRAMES);
    }
}

if (global.frame_count mod TICK_RED_ENERGIA_CADA_FRAMES == 0)
{
    array_push(global.cola_lotes_pendientes, tick_red_energia);
}

var _t0 = get_timer();
while (array_length(global.cola_lotes_pendientes) > 0
    && (get_timer() - _t0) < PRESUPUESTO_SIMULACION_US)
{
    var _trabajo = array_pop(global.cola_lotes_pendientes);
    _trabajo();
}
coste_simulacion_us = get_timer() - _t0;

/// obj_simulador_colonia · Draw GUI — visible igual que el Debug Overlay de 13 · 08 §14
if (global.modo_debug) draw_text(8, 8, $"Simulación colonia: {coste_simulacion_us} µs");
```

> 🔺 **Órdenes de magnitud, no promesas — mide en tu proyecto.** El mismo aviso que hace
> `13 · 08` §14: 2000 µs es un punto de partida razonable (deja 14 666 µs para todo lo demás),
> no una cifra medida en tu hardware.

---

## Checklist

**Job system (§2)**
- [ ] Cada tarea vive como `Tarea` (struct), nunca como instancia — sobrevive a la muerte del
      colono que la tenía reservada.
- [ ] Una `ds_priority` **por tipo** (`ColaTrabajos.colas`), no una mezclando los diez tipos.
- [ ] `sacar_mejor()` es lo único que hace `ds_priority_delete_max`; reservar (§2.4) NO vuelve a
      tocar la `ds_priority`.
- [ ] `colono_buscar_tarea()` reencola las candidatas que no eligió, con su prioridad original.
- [ ] `tarea_fallar()` distingue tareas del tablón (`tarea_id != -1`) de tareas personales
      (`tarea_id == -1`, §4.3): solo las primeras se reencolan.
- [ ] La expiración (§2.8) corre en lote, no cada frame.

**Rutinas y necesidades (§3-§4)**
- [ ] El horario consulta `objTimeOfDay.tiempo`; no crea un reloj propio.
- [ ] `necesidad_mas_urgente()` recibe la actividad programada — el umbral de hambre se relaja
      en la franja de comer, no hay dos caminos de código para «rutina» y «urgencia».
- [ ] Una necesidad urgente **libera** la tarea en curso con `tarea_fallar()`, nunca la descarta
      a lo bruto.
- [ ] `NecesidadesColono` compone `Needs()`, no la reescribe ni la copia.

**Construcción (§5)**
- [ ] Un plano (`global.planos`) y una construcción (`objWorldGrid`) son cosas distintas: nunca
      se ocupa la rejilla de construcción hasta que el plano está completo.
- [ ] `soporte_aplicar_colapso()` se llama tras CADA construcción **y** tras cada demolición.
- [ ] `habitaciones_recalcular_si_toca()` está limitado en frecuencia — no en cada colocación.

**Redes (§6)**
- [ ] `red_actualizar()` reinicia `suministrado = true` para todos los consumidores del grupo
      ANTES de decidir a quién cortar, no solo la primera vez.
- [ ] Los almacenes se vacían antes de cortar a ningún consumidor.

**Simulación fuera de pantalla (§7)**
- [ ] Ningún colono usa `instance_deactivate_object()` al salir del área cargada: se convierte
      en `ColonoDormido` y sigue avanzando.
- [ ] El trabajo de fondo está medido con `get_timer()` y amortizado contra un presupuesto, no
      ejecutado entero de golpe.

---

## Errores clásicos y cómo evitarlos

| Error | Síntoma | Arreglo |
|---|---|---|
| Guardar el struct `Tarea` como `val` de `ds_priority_add` | Comportamiento no documentado — la firma oficial solo cubre `Real` o `String` | Guarda el `tarea_id` (Real) y busca el struct en el mapa maestro `tareas` (§2.3), como ya hacen `04 · 35` y `04 · 38` con índices de rejilla |
| Reservar una tarea y dejarla también en su `ds_priority` | Dos colonos la reservan a la vez, o `ds_priority_size()` cuenta tareas que ya no están libres | `sacar_mejor()` YA la saca de la cola con `delete_max`; reservar (§2.4) no debe volver a tocarla |
| Reencolar una tarea personal (`tarea_id == -1`) al fallar | Entradas fantasma con id `-1` en la cola compartida, que ningún `obtener()` encuentra | `tarea_fallar()` comprueba `tarea_id == -1` primero y libera sin reencolar (§2.7) |
| Un colono desaparece con `instance_deactivate_object()` al salir del chunk | Vuelve con necesidades congeladas en el valor de cuando se fue — o, si el juego SÍ las actualiza en segundo plano por otro camino, con hambre negativa nunca vista por nadie | `colono_dormir()`/`colonos_dormidos_avanzar()` (§7.3): un tercer estado que sigue avanzando, ni activo ni apagado |
| Copiar `WorldGrid`/`objWorldGrid` para añadirle campos de soporte o de plano | Dos fuentes de verdad sobre qué hay en una celda, que pueden desincronizarse | `global.planos` es un mapa APARTE para lo que aún no existe; `soporte_calcular()` LEE `objWorldGrid.celdas`, nunca lo copia (§5.1, §5.4) |
| No reiniciar `suministrado = true` en cada pasada de `red_actualizar()` | Un edificio cortado una vez por falta de energía se queda sin ella para siempre, aunque la red se recupere | Reiniciarlo para todos los `CONSUMIDOR` del grupo antes de calcular el balance (§6.3) |
| Llamar a `golpear()` de `04 · 09` §5.2 con un solo argumento, o inventar un `talar()` que no existe | El símbolo no existe → no compila, o el desgaste del nodo nunca se aplica | `golpear(_dano, _herramienta)` — dos argumentos, y `romper()` la llama sola al llegar a 0 hp; el job system solo llama a `golpear()` en bucle (§2.9) |
| Recalcular `habitaciones_detectar()` en cada `instance_create`/celda ocupada | Construir una pared de 10 bloques dispara 10 barridos completos del mapa | `habitaciones_recalcular_si_toca()` limita por tiempo (§5.5), no por evento |
| Ejecutar `red_actualizar()`, la expiración de tareas y el avance de colonos dormidos sin medir | Un pico de simulación coincide con el peor frame posible (muchos colonos a la vez) | Todo pasa por `obj_simulador_colonia` con `get_timer()` y un presupuesto explícito (§7.4) |

---

## Ver también

- [`04 · 09` — Survival y crafting](./09%20-%20Survival%20y%20crafting.md) — `Needs()` (§5.0),
  `WorldGrid`/`objWorldGrid` y el *ghost preview* corregido (§5.3), `golpear()`/`romper()` de
  `objResourceNode` (§5.2), y el *chunking* (§5.4) sobre los que se construyen los §4, §5 y §7 de
  este documento. **No se toca ni se repite** ninguno de sus structs.
- [`04 · 04` — RPG / Action RPG](./04%20-%20RPG%20_%20Action%20RPG.md) §5.2 — `Inventory` y
  `Equipment`, reutilizados como `global.almacen` en el §5 y el §2.9.
- [`04 · 31` — IA de decisión](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md)
  §8 — `curva_lineal`/`elegir_por_utilidad`, citados en el §2.5; §12 — el tick escalonado del
  que sale el LOD del §7.1-§7.2.
- [`04 · 38` — Pathfinding avanzado](./38%20-%20Pathfinding%20avanzado%20-%20flow%20fields%2C%20JPS%20y%20plataformas.md) —
  precedente de guardar índices, no structs, dentro de una `ds_priority` (§2.3).
- [`04 · 35` — Combate por turnos y táctico en rejilla](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md) —
  mismo precedente de `ds_priority_*` para A*.
- [`04 · 05` — Roguelike y generación procedural](./05%20-%20Roguelike%20y%20generación%20procedural.md#54-validación-por-flood-fill) —
  `dungeon_flood_fill()`, el patrón de BFS que reutilizan tres veces distintas el §5.4, el §5.5
  y el §6.2 de este documento.
- [`04 · 16` — Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) —
  `senal_emitir`/`senal_escuchar`, usados por `tarea_imposible` (§2.7-§2.8) y
  `estructura_derrumbada` (§5.4).
- [`04 · 23` — IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) —
  `mp_potential_step`, el movimiento de `obj_colono` en todo el §2.9 y el §3.4; también el punto
  al que remite el estado `OCIO` del §3.2 cuando no hay tarea que hacer.
- [`04 · 45` — Géneros sin receta propia](./45%20-%20Géneros%20sin%20receta%20propia%20-%20sigilo%2C%20horror%2C%20táctica%2C%20granja%20y%20idle.md) §5.2 —
  el patrón de calendario sobre el reloj de `04 · 09`, que el §3.1 de este documento sigue para
  el horario.
- [`13 · 01` — Diseño de juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md)
  §4.1 — vocabulario Pool/Fuente/Sumidero/Convertidor, que el §6.1 traduce a grafo espacial.
- [`13 · 08` — Físicas a mano y fluidos](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/08%20-%20Físicas%20a%20mano%20y%20fluidos.md) —
  el *spatial hash* (§4), el autómata celular de líquido (§10) que el §6.4 encapsula tras una
  red dirigida, y el presupuesto por frame en µs (§14) que reutiliza el §7.4.
- [`13 · 06` — Arquitectura de un proyecto GameMaker](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md)
  §3.9-§3.10 — el patrón de acumulador con tope (`MAX_PASOS_POR_FRAME`) que inspira el
  presupuesto amortizado del §7.4, y el guardado versionado al que debe sumarse la
  serialización de `NecesidadesColono`/`ColaTrabajos` si el proyecto persiste la colonia entre
  sesiones.
- [`13 · 16` — Progresión](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/16%20-%20Progresión%20-%20árboles%20de%20habilidades%2C%20desbloqueos%20y%20meta-progresión.md) —
  otro ejemplo de grafo por `struct` con validación (Kahn/BFS), si la colonia crece hacia un
  árbol de tecnología propio.
- [`47 · Beat 'em up y brawler`](./47%20-%20Beat%20em%20up%20y%20brawler.md) §4.2-§4.3 —
  el precedente exacto de «ampliar un documento existente por composición, sin tocarlo», que
  siguen el §2.6 y el §4.1 de este documento.

---

## Fuentes

- Manual oficial de GameMaker (espejo local, consultado 2026-09-07) — familia
  `ds_priority_*` (`09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Data_Structures/DS_Priority_Queues/`),
  `instance_nearest`, `instance_activate_region`/`instance_deactivate_region`, `array_sort`,
  `get_timer`, `game_get_speed`.
- El propio código verificado de `04 · 09`, `04 · 04`, `04 · 05`, `04 · 16`, `04 · 31`, `04 · 35`,
  `04 · 38`, `04 · 45`, `13 · 01`, `13 · 06` y `13 · 08` de esta biblioteca, reutilizado sin
  duplicar su contenido — es la fuente primaria más fiable de todas: ya está verificada.
- `_indice/auditorias/r3-simulacion-sistemas.md` (2026-09-06) — el encargo y los 12 temas
  (57, 59, 61, 63, 64, 66, 67, 69, 70, 71, 78, 90) que agrupa este documento.
- Tarn Adams, entrevistas sobre la arquitectura de *Dwarf Fortress* (job system y necesidades
  desacopladas de la simulación de mundo) — referencia de diseño del género, citada de memoria;
  ⚠️ no se abrió una URL concreta en esta sesión, sin fuente primaria verificada.
- Tynan Sylvester, *Designing Games* (2013), cap. sobre sistemas emergentes en *RimWorld* — misma
  referencia de diseño; ⚠️ igual que arriba, sin URL abierta en esta sesión.
