# 23 · Catálogo de patrones en GML

> De los **19 patrones** de Robert Nystrom, *Game Programming Patterns*, esta biblioteca ya
> tiene 12 traducidos a GML — cada uno donde le toca por tema, no aquí (tabla completa en §6).
> Este documento cierra los que faltaban: **Flyweight, Prototype, Subclass Sandbox, Data
> Locality, Dirty Flag, Event Queue**, completa **Bytecode** con un intérprete mínimo, y da un
> **veredicto sobre ECS** en GML — que Nystrom no cubre, pero que todo proyecto grande acaba
> preguntando. No es una introducción a patrones de diseño en general: para eso, el libro
> mismo (enlazado en «Fuentes») lo explica mejor que cualquier resumen.

---

## 1 · Los principios

**Un patrón no es una obligación: es un nombre para un problema que ya se te repitió dos
veces.** Si tu proyecto no tiene ese problema, aplicar el patrón es la deuda técnica, no la
cura. Por eso cada patrón de este documento lleva su sección «cuándo NO usarlo» al mismo nivel
que el código: es la mitad que más se salta al copiar un ejemplo.

Nystrom organiza sus 19 patrones en cinco familias. Las seis piezas que faltaban en esta
biblioteca caen en tres de ellas:

| Familia | Qué resuelve | Patrones de este documento |
|---|---|---|
| *Design Patterns Revisited* | Adaptar los patrones clásicos del GoF a las rarezas de un juego | Flyweight, Prototype |
| *Behavioral* | Definir comportamiento sin que cueste una clase por variante | Subclass Sandbox, Bytecode |
| *Decoupling* | Que un sistema no necesite conocer al que dispara el suceso | Event Queue |
| *Optimization* | Ir más rápido sin cambiar QUÉ calculas, solo CÓMO lo guardas | Data Locality, Dirty Flag |

Dos cosas que GameMaker ya te da gratis, sin que tengas que «implementar el patrón»:

- **Los sprites ya son Flyweight.** `sprite_index` es un *handle* compartido: mil instancias
  con el mismo sprite no duplican ni un píxel de textura, solo guardan el handle y su
  `image_index` particular. §3.1 aplica la misma idea a datos que **no** son un sprite.
- **El evento Step ya es Update Method.** Cada instancia con lógica en su Step está aplicando
  el patrón *Update Method* de Nystrom sin que nadie lo llame así — detalle en
  [01 · 06 §4 y §10](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md#4-el-orden-exacto-de-cada-step).

Y una advertencia que vale para el documento entero: **el runtime de GameMaker está escrito en
C++ y compilado; tu GML no.** Varios de estos patrones (Bytecode, un ECS genérico) meten una
capa de interpretación *encima* de un lenguaje que ya se interpreta o se compila con YYC. Esa
capa cuesta rendimiento real — medido en §3.4 y §3.8, no supuesto.

---

## 2 · El método: qué patrón para qué síntoma

No hay un orden en el que aplicarlos: hay un síntoma que apunta a cada uno.

| Síntoma | Patrón candidato | Sección |
|---|---|---|
| Miles de «cosas» comparten casi todos sus datos (tipo de terreno, definición de enemigo, fuente) y hoy cada una tiene su propia copia | **Flyweight** | §3.1 |
| Necesitas crear variantes de un objeto ya configurado sin escribir un constructor por variante, o tu catálogo JSON (§3.8 de `13/06`) repite los mismos campos en familias enteras | **Prototype** | §3.2 |
| Una familia de subclases (habilidades, hechizos, power-ups) repite el mismo «mover, sonar, invocar partículas» en cada una | **Subclass Sandbox** | §3.3 |
| Un bucle sobre cientos de miles de elementos por Step va lento y no sabes si es el algoritmo o cómo están guardados los datos | **Data Locality** | §3.4 |
| Recalculas algo caro (layout, transformaciones, un total) cada frame aunque nada haya cambiado desde el frame anterior | **Dirty Flag** | §3.5 |
| Un suceso necesita reaccionar sin ejecutarse en el mismo instante que ocurre — para no reentrar, para poder combinar duplicados, para fijar un orden | **Event Queue** | §3.6 |
| El comportamiento tiene que vivir fuera del `.yyp` (reglas editables, mods, contenido de temporada) sin recompilar | **Bytecode** | §3.7 |
| «¿Debería reescribir mi juego sobre un Entity-Component-System?» | veredicto **ECS** | §3.8 |

Si el síntoma es otro, probablemente ya está resuelto en la biblioteca: la tabla de §6 cubre los
otros 12 patrones de Nystrom con su ruta exacta.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 Flyweight

**El problema en GameMaker.** Un mundo de 200×200 celdas de terreno son 40 000 celdas. Si cada
celda guarda su propio struct `{ sprite, coste_movimiento, es_agua }`, estás repitiendo los
mismos 3 valores 40 000 veces cuando en realidad solo hay 5 o 6 **tipos** de terreno distintos.
Lo mismo pasa con 5 000 balas que comparten daño y velocidad, o con cualquier catálogo grande de
`13 · 06 §3.8` cuando dos entradas comparten casi todo. Nystrom separa esto en **estado
intrínseco** (igual para todas: el tipo) y **estado extrínseco** (distinto por instancia: dónde
está). El mundo guarda solo lo extrínseco — un índice — y todas las celdas del mismo tipo
**comparten** el mismo struct intrínseco.

**El código.**

```gml
/// scr_terreno — Flyweight: el TIPO de terreno es compartido (intrínseco); el
/// mundo guarda, por celda, solo un ÍNDICE a ese tipo (extrínseco).

/// @func TipoTerreno(_nombre, _sprite_id, _coste, _es_agua)
/// @desc Estado INTRÍNSECO: igual para cualquier celda que use este tipo.
///       No lleva métodos que lo muten: un Flyweight compartido que cambia
///       cambia a la vez en TODAS las celdas que lo usan.
function TipoTerreno(_nombre, _sprite_id, _coste, _es_agua) constructor {
    nombre    = _nombre;
    sprite_id = _sprite_id;
    coste     = _coste;      // coste de movimiento, para pathfinding
    es_agua   = _es_agua;
}

/// @func terreno_catalogo_crear()
/// @desc Los ÚNICOS structs de terreno que existirán en todo el juego. Cinco
///       tipos, sin importar si el mundo tiene 100 celdas o 10 millones.
function terreno_catalogo_crear() {
    return [
        new TipoTerreno("hierba", spr_terreno_hierba, 1,   false),
        new TipoTerreno("agua",   spr_terreno_agua,   999, true),
        new TipoTerreno("roca",   spr_terreno_roca,   3,   false)
    ];
}

/// @func mundo_crear(_ancho, _alto, _catalogo)
/// @desc El mundo NO guarda TipoTerreno: guarda un array PLANO de índices
///       reales (ver §3.4 — por qué plano y no un array de structs).
function mundo_crear(_ancho, _alto, _catalogo) {
    return {
        ancho:    _ancho,
        alto:     _alto,
        celdas:   array_create(_ancho * _alto, 0),   // 0 = índice al catálogo
        catalogo: _catalogo
    };
}

/// @func mundo_terreno_en(_mundo, _cx, _cy)
/// @desc Resuelve una celda a su TipoTerreno COMPARTIDO. No copia nada.
function mundo_terreno_en(_mundo, _cx, _cy) {
    var _idx = _mundo.celdas[_cy * _mundo.ancho + _cx];
    return _mundo.catalogo[_idx];
}
```

Con esto, un mundo de 40 000 celdas guarda **40 000 reales** (los índices) más **3 structs**
(los tipos), en vez de 40 000 structs completos. La diferencia de memoria escala con el tamaño
del mundo; la de los structs, no.

**Cuándo NO usarlo.** Si tienes una docena de instancias, o si cada una necesita mutar de verdad
su propio estado «intrínseco» (entonces no hay nada compartible: no es un Flyweight, es una
entidad normal). No lo apliques «para escribir menos»: es una optimización de memoria y
coherencia, no de tecleo — de hecho añade una indirección.

**Coste.** Leer un campo cuesta una indirección extra: `mundo_terreno_en(_m, _cx, _cy).coste` en
vez de `_celda.coste` directo. Y si por accidente mutas el `TipoTerreno` compartido
(`_catalogo[0].coste = 5`), **cambia de golpe en cada celda que use ese tipo** — el bug clásico
de Flyweight, y la razón de que sean inmutables por convención.

---

### 3.2 Prototype

**El problema en GameMaker.** El catálogo JSON de
[13 · 06 §3.8](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#38-datos-dirigidos-definir-el-juego-en-json)
resuelve «un enemigo por entrada de datos», pero cuando ocho variantes de goblin comparten el
90 % de sus campos (`resists`, `weaknesses`, `hp`), cada entrada repite esos campos a mano. Y
aparte del dato, a veces lo que quieres clonar es una **instancia ya configurada** — una
plantilla de bala con su sprite, daño y velocidad ya puestos — en vez de escribir un
`obj_bala_fuego`, un `obj_bala_hielo`… con el mismo Create casi idéntico.

**El código — delegación en el catálogo JSON.** Nystrom resuelve la familia de goblins con una
clave `"prototype"` que cada entrada puede declarar: lo que no defina, lo hereda de ahí. Es la
pieza que le falta al catálogo de `13 · 06 §3.8`:

```json
// enemigos.json — con delegación por prototipo. goblin_wizard y goblin_archer
// solo escriben lo que los diferencia; el resto viene de goblin_grunt.
{
  "goblin_grunt":  { "hp": 20, "resists": ["cold", "poison"],
                     "weaknesses": ["fire", "light"], "sprite": "spr_goblin" },
  "goblin_wizard": { "prototipo": "goblin_grunt", "spells": ["fire_ball"] },
  "goblin_archer": { "prototipo": "goblin_grunt", "attacks": ["short_bow"] }
}
```

```gml
/// scr_prototipos — resuelve la clave "prototipo" de un catálogo JSON (que
/// catalogo_leer() de 13 · 06 §3.8 ya carga) ANTES de usarlo.

/// @func catalogo_resolver_prototipos(_catalogo)
/// @desc Para cada entrada con "prototipo", copia los campos que le FALTEN
///       desde la entrada nombrada. Lo que la entrada ya define, gana: el
///       prototipo solo rellena huecos.
/// @param {Struct} _catalogo  Struct { clave: definición }.
/// @returns {Struct}          El mismo catálogo, ya resuelto.
function catalogo_resolver_prototipos(_catalogo) {
    var _claves = struct_get_names(_catalogo);

    for (var _i = 0; _i < array_length(_claves); _i++) {
        var _clave = _claves[_i];
        var _def   = _catalogo[$ _clave];
        if (!variable_struct_exists(_def, "prototipo")) continue;

        var _base_clave = _def.prototipo;
        if (!variable_struct_exists(_catalogo, _base_clave)) {
            show_debug_message($"Prototipo desconocido: «{_base_clave}» (pedido por «{_clave}»)");
            continue;
        }

        // Clon PROFUNDO: si no clonas, dos goblins compartirían el MISMO
        // array "resists", y mutar uno mutaría a los demás — el bug de
        // Flyweight accidental que en §3.1 evitamos a propósito.
        var _base   = variable_clone(_catalogo[$ _base_clave]);
        var _campos = struct_get_names(_base);

        for (var _j = 0; _j < array_length(_campos); _j++) {
            var _campo = _campos[_j];
            if (!variable_struct_exists(_def, _campo)) {
                variable_struct_set(_def, _campo, _base[$ _campo]);
            }
        }
    }
    return _catalogo;
}
```

**El código — clonar una instancia viva.** Para plantillas de comportamiento (una bala, un
proyectil) en vez de solo datos, `instance_copy()` clona una instancia entera:

```gml
/// obj_bala_plantilla · Create — una plantilla YA CONFIGURADA, desactivada,
/// que nunca se ve ni se mueve. Una por variante de bala, no una por bala.
sprite_index = spr_bala_fuego;
dano_base    = 12;   // sin "ñ": los identificadores de GML son solo ASCII (§3.7 lo mide)
velocidad    = 14;
perforante   = false;
instance_deactivate_object(id);   // misma idea que el pool de 06/scr_pool.gml

/// @func bala_disparar(_plantilla, _px, _py, _dir)
/// @desc Clona una plantilla en vez de reescribir un obj_bala por variante.
/// @param {Id.Instance} _plantilla  Una instancia de obj_bala_plantilla.
function bala_disparar(_plantilla, _px, _py, _dir) {
    var _nueva = noone;
    with (_plantilla) {
        // false: NO relanza el Create, que borraría dano_base/velocidad/perforante
        // y los dejaría en los valores por defecto del objeto, no de ESTA plantilla.
        _nueva = instance_copy(false);
    }
    instance_activate_object(_nueva);
    with (_nueva) {
        x = _px; y = _py;
        direction = _dir;
    }
    return _nueva;
}
```

**Cuándo NO usarlo.** Con dos o tres variantes, el catálogo llano de `13 · 06 §3.8` ya basta: la
delegación por prototipo solo paga cuando hay familias grandes con mucho campo compartido. Con
`instance_copy()`, si el Create de la plantilla hace trabajo caro (registrarse en un sistema,
cargar datos), `perf = false` es obligatorio — con `true` repites ese coste en cada clon.

**Coste.** `variable_clone()` con la profundidad por defecto (128) recorre toda la estructura
anidada; para catálogos muy grandes, limita la profundidad (`variable_clone(_base, 2)`) si sabes
que no anidas más de dos niveles.

---

### 3.3 Subclass Sandbox

**El problema en GameMaker.**
[13 · 06 §3.6](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#36-composición-frente-a-herencia)
ya avisa: máximo dos niveles de herencia de objetos, y composición para lo demás. Pero hay un
caso legítimo de herencia de dos niveles que ese documento no nombra: cuando lo que varía de
verdad es **comportamiento**, no datos, y todas las variantes necesitan las mismas operaciones
del mundo — 40 habilidades de un metroidvania que solo necesitan «empujar al jugador, sonar,
invocar partículas». Ponerlas en el padre como **operaciones provistas**, y que cada hija las
combine en un único método, es exactamente *Subclass Sandbox*.

**El código.**

```gml
/// obj_habilidad_base · Create
/// Las "operaciones provistas": lo ÚNICO que una habilidad hija puede tocar
/// del resto del juego. Ninguna hija concreta necesita saber qué es un bus de
/// audio o un sistema de partículas: solo conoce estos tres verbos.
function empujar(_hspeed, _vspeed) {
    with (obj_jugador) { hspeed = _hspeed; vspeed = _vspeed; }
}

function invocar_particulas(_tipo, _cantidad) {
    // Aquí: tu sistema de partículas o VFX del proyecto.
    show_debug_message($"VFX: {_tipo} x{_cantidad}");
}

function reproducir_sonido(_snd) {
    audio_play_sound(_snd, 10, false);
}

/// El "método sandbox": cada hija lo SOBRESCRIBE combinando lo de arriba.
/// En el padre solo existe para dejar claro que hay que sobrescribirlo.
function ejecutar() {
    show_debug_message("obj_habilidad_base.ejecutar() no debería llamarse nunca");
}
```

```gml
/// obj_habilidad_dash (padre: obj_habilidad_base) · Create
event_inherited();   // hereda empujar/invocar_particulas/reproducir_sonido

function ejecutar() {
    empujar(lengthdir_x(20, image_angle), lengthdir_y(20, image_angle));
    invocar_particulas("polvo", 8);
    reproducir_sonido(snd_dash);
}
```

```gml
/// obj_habilidad_gancho (padre: obj_habilidad_base) · Create
event_inherited();

function ejecutar() {
    empujar(0, -16);
    invocar_particulas("chispa_metal", 4);
    reproducir_sonido(snd_gancho);
}
```

Ninguna de las dos hijas sabe que `obj_jugador` existe como objeto, ni cómo suena
`audio_play_sound` por dentro: solo llaman a las tres operaciones que el padre les da.

**Cuándo NO usarlo.** Si las variantes se diferencian por **datos** (stats, sprite, alcance) y
no por lógica distinta, eso es *Type Object* (`13 · 06 §3.8`), no esto. Si la «sandbox» del
padre empieza a acumular decenas de operaciones provistas, es la señal de que el padre se está
hinchando otra vez: reparte esas operaciones en structs de composición
([13 · 06 §3.6](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#36-composición-frente-a-herencia))
que el padre solo reenvía.

**Coste.** El padre queda acoplado a todo lo que sus operaciones provistas tocan — el
*brittle base class problem* que Nystrom nombra explícitamente: cambiar la firma de una
operación provista rompe a la vez a todas las hijas que la usan.

---

### 3.4 Data Locality — medido, no folclore

**El problema en GameMaker.** Cuando actualizas cientos de miles de «cosas» cada Step
(partículas a mano, celdas de un autómata, boids), **cómo guardas los datos** pesa tanto como el
algoritmo. Un struct de GML es un **tipo por referencia**: un array de structs es, en memoria,
un array de *punteros* a bloques dispersos por el heap. Recorrerlo persigue esos punteros y
golpea la caché de la CPU en cada elemento. Un array **plano** de reales es memoria contigua: la
CPU trae varios elementos de golpe en cada línea de caché. `13 · 07 §2.9` ya daba la regla
(«precalcula a un array, no calcules en Draw») sin nombrarla ni medirla; aquí se mide.

**El experimento.** 200 000 «partículas» con posición y velocidad, actualizadas 50 veces
(`x += vx; y += vy`), en dos formas:

- **Array de structs** — `_arr[i] = { x: 0, y: 0, vx: ..., vy: ... }`: cada elemento es una
  referencia a un struct suelto en el heap.
- **Array plano (*struct-of-arrays*)** — cuatro arrays de reales `_px`, `_py`, `_pvx`, `_pvy`:
  cada uno es un bloque contiguo de memoria.

```gml
/// obj_bench · Create — benchmark desechable, compilado y ejecutado de verdad
/// con `gm-cli run --runtime native` para este documento (ver «Fuentes»).

var _n    = 200000;
var _reps = 50;

// --- Preparación: array de STRUCTS (cada elemento es una referencia a heap) --
var _structs = array_create(_n);
for (var _i = 0; _i < _n; _i++) {
    _structs[_i] = { x: 0, y: 0, vx: 1.3, vy: -0.7 };
}

// --- Preparación: array PLANO (struct-of-arrays, solo reales) ---------------
var _px  = array_create(_n, 0);
var _py  = array_create(_n, 0);
var _pvx = array_create(_n, 1.3);
var _pvy = array_create(_n, -0.7);

// --- Medición 1: array de structs -------------------------------------------
var _t0 = get_timer();
for (var _r = 0; _r < _reps; _r++) {
    for (var _i = 0; _i < _n; _i++) {
        var _p = _structs[_i];
        _p.x += _p.vx;
        _p.y += _p.vy;
    }
}
var _t_structs = (get_timer() - _t0) / 1000;   // get_timer() es en microsegundos

// --- Medición 2: array plano -------------------------------------------------
_t0 = get_timer();
for (var _r = 0; _r < _reps; _r++) {
    for (var _i = 0; _i < _n; _i++) {
        _px[_i] += _pvx[_i];
        _py[_i] += _pvy[_i];
    }
}
var _t_plano = (get_timer() - _t0) / 1000;

show_debug_message($"array de structs: {_t_structs / _reps} ms/pasada");
show_debug_message($"array plano:      {_t_plano / _reps} ms/pasada");
show_debug_message($"factor: {_t_structs / _t_plano}x");
```

**Resultado real** (dos pasadas independientes, `gm-cli run --runtime native`, GameMaker runtime
2026.0.0.23, Apple M5 Pro / arm64 — ver «Fuentes» para la metodología):

| Pasada | Array de structs | Array plano | Factor |
|---|---:|---:|---:|
| 1 | 7,58 ms/pasada | 2,79 ms/pasada | **2,72×** |
| 2 | 7,75 ms/pasada | 2,80 ms/pasada | **2,76×** |

El array plano es **~2,7 veces más rápido** que el equivalente en structs, de forma consistente
entre pasadas, para el mismo cálculo exacto. La diferencia no es el algoritmo — es idéntico en
ambas versiones — sino, únicamente, cómo está dispuesta la memoria.

> ⚠️ **Esto se midió compilando a nativo (YYC), no en la VM.** En esta máquina, `gm-cli run`
> sobre el runtime de VM para macOS falló al cargar el juego (un problema del *runner* de
> macOS, no del código): confirmado dos veces, documentado aquí en vez de callado. El **factor**
> entre versiones debería mantenerse en la VM por venir de un efecto de hardware (caché de CPU),
> pero el **número absoluto** de milisegundos no se ha medido ahí — no lo des por bueno sin
> remedir si tu proyecto exporta a VM y el rendimiento es crítico.

**Cuándo NO usarlo.** Si tu bucle recorre decenas o cientos de elementos (la mayoría de
enemigos, proyectiles, NPCs de un juego normal), la diferencia es submilisegundos: no merece la
pérdida de legibilidad de separar `_px`/`_py`/`_pvx`/`_pvy` en vez de un struct con nombre. Este
patrón paga a partir de varios miles de elementos actualizados en un bucle apretado, no antes.

**Coste.** El *struct-of-arrays* es más difícil de leer y de ampliar: añadir un campo nuevo
significa un array nuevo, no una línea en un struct. Y **acopla el índice**: `_px[_i]` y
`_pvx[_i]` tienen que referirse siempre a la misma «partícula» — un `array_delete` en un array y
no en los otros tres desincroniza todo el sistema sin ningún error visible hasta que los datos
ya no cuadran.

---

### 3.5 Dirty Flag

**El problema en GameMaker.** Recalcular algo caro en cada Step o cada Draw aunque nada haya
cambiado desde el frame anterior. `04 · 13 §7` ya lo señala como error suelto — «Recalcular el
layout de Flex Panels cada frame» — sin darle nombre ni una solución reutilizable; aquí se lo
da: guarda un resultado en caché y una bandera; solo recalcula cuando algo lo **ensucia**.

**El código.**

```gml
/// scr_stats_equipo — Dirty Flag: no sumar el inventario en cada frame que se
/// preguntan las stats totales; solo cuando el equipo cambió de verdad.

/// @func StatsEquipo(_base)
/// @param {Struct} _base  Stats sin objetos equipados: { fuerza, defensa }.
function StatsEquipo(_base) constructor {
    base    = _base;
    items   = [];
    sucio   = true;        // arranca sucio: la primera lectura SIEMPRE calcula
    cache   = undefined;

    /// @desc El ÚNICO sitio que ensucia la caché.
    static equipar = function(_item) {
        array_push(items, _item);
        sucio = true;
    };

    static desequipar = function(_item) {
        var _i = array_get_index(items, _item);
        if (_i == -1) return false;
        array_delete(items, _i, 1);
        sucio = true;
        return true;
    };

    /// @desc Lectura pública. Recalcula SOLO si está sucio.
    static total = function() {
        if (sucio) {
            cache = __recalcular();
            sucio = false;
        }
        return cache;
    };

    static __recalcular = function() {
        var _t = variable_clone(base, 0);
        for (var _i = 0; _i < array_length(items); _i++) {
            _t.fuerza  += items[_i].fuerza;
            _t.defensa += items[_i].defensa;
        }
        return _t;
    };
}
```

El mismo truco, con `surface_*`, sirve para no redibujar un minimapa entero cada frame:

```gml
/// obj_minimapa · Create
superficie = surface_create(128, 128);
sucio      = true;               // el mundo aún no se ha dibujado ni una vez

/// obj_minimapa · Step — algo del mundo cambió (un POI nuevo, niebla revelada)
sucio = true;

/// obj_minimapa · Draw GUI
if (sucio) {
    surface_set_target(superficie);
    // ... dibujar el mundo simplificado, UNA vez ...
    surface_reset_target();
    sucio = false;
}
draw_surface(superficie, 16, 16);
```

**Cuándo NO usarlo.** Si el valor cambia casi todos los frames de todas formas (una posición que
se mueve constantemente), el flag nunca ahorra nada y solo añade una rama `if`. Y si el cálculo
es barato, cachearlo no compensa la complejidad de acordarte de ensuciar la caché en cada sitio
que toca el dato de origen — que es, con diferencia, el bug más común de este patrón.

**Coste.** Cada punto que modifica el estado de origen tiene que acordarse de poner
`sucio = true`. Olvidar uno es un bug silencioso: el valor cacheado se queda obsoleto y nada
avisa, porque desde fuera parece que «funciona» hasta que alguien nota el dato viejo.

---

### 3.6 Event Queue

**El problema en GameMaker.**
[04 · 16 — Señales y desacoplamiento](../04%20-%20Recetas%20por%20g%C3%A9nero/16%20-%20Se%C3%B1ales%20y%20desacoplamiento.md)
ya resuelve **quién** se entera de un suceso (Observer). Pero sus oyentes se ejecutan **en el
mismo instante** que la señal, en la misma pila de llamadas del emisor — de forma síncrona. Eso
se rompe cuando: el propio oyente destruye o modifica la instancia que emitió la señal
(reentrada); 30 colisiones del mismo tipo en un frame deberían sonar **una vez** más fuerte, no
30 veces superpuestas; o el orden de varias señales del mismo frame importa y hoy es «el orden
en que se emitieron», no uno elegido a propósito. *Event Queue* no cambia quién escucha —eso
sigue siendo trabajo de las señales—: cambia **cuándo** se procesa.

**El código.**

```gml
/// scr_cola_eventos — Event Queue: desacopla CUÁNDO se procesa un suceso de
/// CUÁNDO ocurrió. Complementa a las señales síncronas de 04 · 16.

function ColaEventos() constructor {
    pendientes = [];

    /// @desc Encola un suceso. Si ya hay uno del mismo tipo esperando y se
    ///       pasa _combinar, los fusiona en vez de duplicarlo — el caso
    ///       clásico de Nystrom: 20 impactos en un frame no deberían sonar
    ///       20 veces.
    /// @param {String}   _tipo
    /// @param {Any}      _datos
    /// @param {Function} [_combinar]  (_pendiente, _nuevo) -> _fusionado
    static encolar = function(_tipo, _datos, _combinar = undefined) {
        if (_combinar != undefined) {
            for (var _i = 0; _i < array_length(pendientes); _i++) {
                if (pendientes[_i].tipo == _tipo) {
                    pendientes[_i].datos = _combinar(pendientes[_i].datos, _datos);
                    return;
                }
            }
        }
        array_push(pendientes, { tipo: _tipo, datos: _datos });
    };

    /// @desc Vacía la cola procesando cada suceso con _manejador(tipo, datos).
    ///       Llámalo UNA vez por Step, desde un sitio fijo (obj_game, End Step).
    static procesar = function(_manejador) {
        var _copia = pendientes;
        pendientes = [];        // vaciar ANTES de procesar: si un manejador
                                 // encola algo nuevo, va a la cola del
                                 // PRÓXIMO frame, no a esta misma pasada
                                 // (evita bucles infinitos dentro de un Step).
        for (var _i = 0; _i < array_length(_copia); _i++) {
            _manejador(_copia[_i].tipo, _copia[_i].datos);
        }
    };
}
```

```gml
/// obj_game · Create
global.cola_sonido = new ColaEventos();

/// obj_enemigo · al recibir un impacto de metal
global.cola_sonido.encolar("impacto_metal", { veces: 1 },
    function(_previo, _nuevo) { return { veces: _previo.veces + _nuevo.veces }; });

/// obj_game · Step (End Step — después de toda la lógica del frame)
global.cola_sonido.procesar(function(_tipo, _datos) {
    switch (_tipo) {
        case "impacto_metal":
            audio_play_sound(snd_impacto_metal, 10, false,
                              min(1 + _datos.veces * 0.15, 2));   // más fuerte, no más veces
            break;
    }
});
```

**Cuándo NO usarlo.** Si solo hay un oyente y necesitas su respuesta **ya** (un valor de
retorno), eso es una llamada directa, no una cola. Si el suceso debe reaccionar en el mismo
frame en que ocurre, una señal síncrona de `04 · 16` basta y es más simple. Y
[13 · 12 §6.6 — Cinemáticas como cola de pasos](12%20-%20Dise%C3%B1o%20narrativo%20y%20di%C3%A1logos.md#66-cinemáticas-como-cola-de-pasos)
**no** es este patrón, aunque lo parezca de nombre: es una cola *secuencial* de un único
productor (un paso detrás de otro); esta es una cola de **muchos** productores concurrentes que
se resuelven en un punto fijo del frame.

**Coste.** `encolar()` con `_combinar` recorre lo pendiente — aceptable para decenas de sucesos
por frame; para miles, indexa por tipo con un `struct` o un `ds_map` en vez de recorrer el
array. Siempre añade un frame de retraso entre que algo ocurre y que se procesa: si tu juego
necesita reaccionar en el mismo frame, este no es el patrón.

---

### 3.7 Bytecode: un intérprete mínimo

**El problema en GameMaker.** Cuando el comportamiento tiene que vivir **fuera** del `.yyp` —
reglas de un hechizo editables sin recompilar, contenido de temporada, un mod de jugador— ni el
catálogo de datos de `13 · 06 §3.8` (datos, sin lógica) ni *Subclass Sandbox* (lógica, pero
compilada dentro del proyecto) sirven. Hace falta ejecutar una secuencia de operaciones que
llega como **dato**. La solución mínima de Nystrom es una máquina de pila: un array de
instrucciones y un bucle que las interpreta, una detrás de otra, sin saltos ni bucles dentro del
propio lenguaje — así un contenido mal escrito no puede colgar el juego.

**El código.**

```gml
/// scr_bytecode — intérprete mínimo de pila para GML.
/// Para algo más ambicioso que aritmética — variables, condicionales,
/// funciones definidas por el propio contenido — no reinventes la rueda:
/// usa catspeak-lang, ya catalogado en
/// [12 · 01 §7](../12%20-%20Utilidades%20e%20integraciones/01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md#7-ejecutar-código-en-tiempo-de-ejecución-scripting-y-modding).

enum OpCode {
    PUSH,          // operando: literal a apilar
    SUMAR,
    MULTIPLICAR,
    LEER_STAT,     // operando: nombre del stat, p.ej. "fuerza"
    DANO           // sin "ñ": los identificadores de GML son solo ASCII
}

/// @func bytecode_ejecutar(_instrucciones, _lanzador, _objetivo)
/// @desc Ejecuta una lista de instrucciones sobre una pila propia. Cada
///       instrucción corre UNA vez, en orden: no hay forma de escribir un
///       bucle infinito en este lenguaje porque el lenguaje no tiene bucles.
/// @param {Array<Struct>} _instrucciones  [{ op: OpCode, operando: Any }, ...]
/// @param {Id.Instance}   _lanzador       Quien lanza (de aquí salen sus stats).
/// @param {Id.Instance}   _objetivo       Quien recibe el efecto.
function bytecode_ejecutar(_instrucciones, _lanzador, _objetivo) {
    var _pila = [];

    for (var _i = 0; _i < array_length(_instrucciones); _i++) {
        var _inst = _instrucciones[_i];

        switch (_inst.op) {
            case OpCode.PUSH:
                array_push(_pila, _inst.operando);
                break;

            case OpCode.SUMAR: {
                var _b = array_pop(_pila);
                var _a = array_pop(_pila);
                array_push(_pila, _a + _b);
                break;
            }

            case OpCode.MULTIPLICAR: {
                var _b = array_pop(_pila);
                var _a = array_pop(_pila);
                array_push(_pila, _a * _b);
                break;
            }

            case OpCode.LEER_STAT:
                array_push(_pila, variable_struct_get(_lanzador.stats, _inst.operando));
                break;

            case OpCode.DANO: {
                var _cantidad = array_pop(_pila);
                _objetivo.stats.vida = max(0, _objetivo.stats.vida - _cantidad);
                break;
            }
        }
    }

    return (array_length(_pila) > 0) ? _pila[array_length(_pila) - 1] : undefined;
}
```

Un hechizo — «el daño es el doble de la fuerza del lanzador» — se define como **dato**, no como
código GML, y puede llegar en un `.json` de contenido:

```json
// hechizo_bola_fuego.json
[
    { "op": "LEER_STAT",   "operando": "fuerza" },
    { "op": "PUSH",        "operando": 2 },
    { "op": "MULTIPLICAR" },
    { "op": "DANO" }
]
```

Cargarlo solo exige traducir el nombre del `op` (una cadena, porque JSON no tiene enums) a su
valor de `OpCode`:

```gml
/// @func bytecode_desde_json(_instrucciones_json)
/// @desc Traduce los "op" en texto (como llegan del JSON) a valores OpCode.
function bytecode_desde_json(_instrucciones_json) {
    static _nombres = ["PUSH", "SUMAR", "MULTIPLICAR", "LEER_STAT", "DANO"];
    var _resultado = array_create(array_length(_instrucciones_json));

    for (var _i = 0; _i < array_length(_instrucciones_json); _i++) {
        var _in = _instrucciones_json[_i];
        _resultado[_i] = {
            op:       array_get_index(_nombres, _in.op),
            operando: _in[$ "operando"] ?? undefined
        };
    }
    return _resultado;
}
```

**Cuándo NO usarlo.** Si el diseñador solo necesita **ajustar números** (daño, alcance,
cooldown), el catálogo JSON llano de `13 · 06 §3.8` basta y es muchísimo más simple de escribir
a mano que una lista de instrucciones. Y si el contenido necesita variables con nombre,
condicionales, bucles o funciones propias —no solo aritmética sobre una pila—, **no escribas tu
propio lenguaje**: mantener un intérprete propio cuesta semanas de trabajo que casi ningún
proyecto se puede permitir, y **catspeak-lang** (enlazado arriba) ya resuelve exactamente eso,
probado y mantenido por otros.

**Coste.** Cada instrucción cuesta un salto de `switch` más un par de operaciones de array
(`array_push`/`array_pop`): decenas de veces más lento que el mismo cálculo escrito directamente
en GML. Acéptalo solo para el comportamiento que de verdad necesita ser dato en tiempo de
ejecución — no para la lógica normal del juego.

---

### 3.8 ECS en GML: el veredicto

Un *Entity-Component-System* separa una entidad en tres piezas: un **id** sin comportamiento,
**componentes** que son datos puros (posición, salud, IA) guardados en arrays contiguos **por
tipo de componente**, y **sistemas** que recorren esos arrays actualizando un aspecto a la vez.
Motores como Unity DOTS o Bevy lo adoptan porque, en un lenguaje de sistemas con control manual
de memoria, ese diseño **es** Data Locality (§3.4) llevado a la arquitectura entera: cada
sistema recorre memoria contigua, sin punteros que perseguir.

**El veredicto, en una frase: en GameMaker, toma prestado el vocabulario de ECS —entidad como
datos, sistema como función que itera— solo para el subsistema puntual que de verdad lo
necesite (aplicando §3.4 ahí), y no reescribas el juego entero sobre una capa de entidades
genérica.**

Tres razones, no una intuición:

1. **GameMaker ya te da la mitad de un ECS, gratis y optimizada en C++.** Una instancia con
   `stats = new Stats(...)` es, en la práctica, un id (`id` de instancia) con un componente
   (`stats`) — es literalmente la composición de
   [13 · 06 §3.6](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#36-composición-frente-a-herencia).
   Lo que un ECS añade encima —colisiones, capas, orden de dibujo, el Room Editor— GameMaker ya
   lo resuelve con `with()`, eventos de colisión e `instance_create_layer`, todo implementado en
   C++. Un ECS genérico o los reimplementa (perdiendo el editor de rooms y el motor de
   colisiones) o los sigue usando por debajo — y entonces, ¿para qué la capa extra?
2. **Es el mismo anti-patrón que `13 · 06 §5` ya nombra como el nº 8**: *reimplementar en GML lo
   que el motor hace en C++* puede ser **hasta 11 veces más lento**, según esa misma tabla
   ([13 · 06 §5](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#5--anti-patrones-los-ocho-de-los-proyectos-que-se-atascan)).
   Una capa de entidad-id → componente construida a mano en GML (con un `ds_map` o un array por
   cada tipo de componente) es exactamente ese envoltorio.
3. **La ventaja real de un ECS es de memoria, y GML no te da las palancas para ganarla del
   todo.** El motor no te deja elegir *layout* de memoria byte a byte ni tiene SIMD accesible
   desde GML: lo máximo que puedes hacer es exactamente §3.4 —arrays planos por campo—, que
   funciona igual de bien **sin** montar el resto del framework (registro de entidades, consultas
   por combinación de componentes, sistemas genéricos).

| | Instancias + structs (`13 · 06 §3.6`) | ECS genérico hecho a mano en GML |
|---|---|---|
| Colisiones, capas, Room Editor | Gratis, del motor | Hay que reimplementarlos, o seguir dependiendo de instancias de todos modos |
| Recorrer 100 entidades heterogéneas | `with(obj_enemigo)`, optimizado en C++ | Una indirección propia, en GML interpretado o YYC |
| Recorrer 100 000 elementos homogéneos sin colisión | Igual de rápido aplicando solo §3.4 | Igual de rápido — **mismo** coste, con más código que mantener |
| Coste de entrada | Cero: es como ya se programa en GML | Alto: construir y mantener el framework entero |

**Cuándo sí se justifica algo parecido a un sistema:** un subsistema aislado con decenas de
miles de elementos totalmente homogéneos que **no** necesitan colisión de motor ni verse en el
Room Editor — un autómata celular grande, un enjambre de partículas a mano, una simulación de
fondo. Ahí, arrays planos por campo (§3.4) **son** la solución — sin entity-ids genéricos, sin
un registro central de componentes: solo la parte de ECS que de verdad paga.

> ⚠️ El corpus de terceros descargado en la biblioteca (nivel 5 de autoridad, no fuente
> primaria) coincide con este veredicto de forma independiente en
> `11 - Código descargado/librerias/extras/painfully-learned-lessons/optimization.md`: describe
> el ECS como algo que «la gente equipara con un botón gratis de rendimiento», señala que
> `ds_grid` es la herramienta de GameMaker que de verdad se acerca al procesado por lotes, y
> — como el propio código no es documentación verificada de esta biblioteca (`AGENTS.md` §1.bis)
> — se cita aquí solo como contraste, no como fuente de la conclusión.

**Coste de montar un ECS «de verdad» en GML.** La indirección entidad-id → componente cuesta una
búsqueda extra (array o `ds_map`) por componente, por entidad y por frame — exactamente el
patrón de acceso disperso que §3.4 mide como más lento. Un ECS mal encajado en GML puede acabar
siendo **más** lento que instancias nativas, no menos: la ventaja de un ECS depende del lenguaje
que lo rodea, y GML no es ese lenguaje.

---

## 4 · Checklist

Antes de aplicar cualquier patrón de este documento:

- [ ] **¿El síntoma es real o es folclore?** Para Data Locality en concreto: mide con
      `get_timer()` en TU proyecto (§3.4) antes de reescribir nada. Un patrón sin medir es una
      superstición con sintaxis de GML.
- [ ] **¿Ya está resuelto en otro sitio de la biblioteca?** Repasa la tabla de §6 antes de
      escribir código nuevo.
- [ ] **Flyweight**: ¿el dato es de verdad inmutable entre instancias? Si necesitas mutarlo por
      instancia, no hay nada que compartir.
- [ ] **Prototype**: ¿`instance_copy()` lleva `perf = false` cuando el Create original hace
      trabajo caro? ¿`variable_clone()` en vez de una copia superficial cuando hay
      arrays/structs anidados que no deben compartirse?
- [ ] **Subclass Sandbox**: ¿de verdad son solo dos niveles? ¿el padre expone *operaciones*, no
      variables sueltas que cualquier hija puede tocar sin control?
- [ ] **Data Locality**: ¿el bucle mueve miles de elementos, no decenas? Si son decenas, no
      compensa la pérdida de legibilidad.
- [ ] **Dirty Flag**: ¿TODOS los puntos que cambian el estado de origen ensucian la caché? Uno
      olvidado es un bug silencioso.
- [ ] **Event Queue**: ¿la cola tiene un tope, o puede crecer sin límite si nadie la vacía?
- [ ] **Bytecode**: ¿de verdad necesitas un lenguaje, o un catálogo JSON llano (`13 · 06 §3.8`)
      resolvía lo mismo con una décima parte del código?
- [ ] **ECS**: ¿el subsistema es homogéneo y sin colisión de motor? Si necesita el Room Editor o
      colisiones, no es candidato — usa instancias.

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Mutar un `TipoTerreno` (u otro Flyweight) compartido pensando que es de una sola celda | Todas las celdas de ese tipo cambian a la vez | Los Flyweight son inmutables; para variar algo, eso es estado extrínseco y va en la celda, no en el tipo |
| `instance_copy(true)` sobre una plantilla ya configurada | El clon vuelve a los valores por defecto: pierde daño/velocidad de la plantilla | `instance_copy(false)` y copiar `x`/`y`/`direction` a mano después |
| Un catálogo JSON con `"prototipo"` sin `catalogo_resolver_prototipos()` | Las entradas hijas no tienen los campos del padre; `undefined` en tiempo de ejecución | Llamarlo justo después de `catalogo_leer()`, antes de usar el catálogo |
| Una jerarquía de `obj_habilidad_*` de tres niveles o más | El «brittle base class problem»: tocar el padre rompe hijas que no tocaste | Máximo dos niveles ([13 · 06 §3.6](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#36-composición-frente-a-herencia)); lo demás, composición |
| Optimizar con array plano un bucle de 30 elementos | Código más difícil de leer, cero ganancia medible | Perfila primero (§3.4); por debajo de unos pocos miles de elementos no compensa |
| Desincronizar `_px[i]` y `_pvx[i]` al borrar solo de uno de los cuatro arrays paralelos | Los datos de una «partícula» dejan de corresponder entre sí, sin ningún error | Borra siempre los cuatro arrays a la vez, o cambia a un índice de reciclado (`06/scr_pool.gml`) en vez de `array_delete` |
| Ensuciar un Dirty Flag en un sitio y olvidarlo en otro | El valor cacheado queda obsoleto sin ningún aviso | Centraliza TODAS las mutaciones en métodos que ensucien (como `equipar`/`desequipar` de §3.5); nunca mutación directa desde fuera |
| Una `ColaEventos` sin tope que nadie vacía | Fuga de memoria lenta: la cola crece sesión tras sesión | Pon un máximo y decide qué hacer al llenarse (descartar el más viejo, o el más nuevo) |
| Escribir un intérprete de Bytecode con bucles o saltos «por si acaso» | El contenido de un mod puede colgar el juego con un bucle infinito | Deliberadamente SIN bucles ni saltos en el lenguaje — si hace falta, usa catspeak-lang, que ya lo resuelve con límites |
| Usar tildes o eñes en un identificador de GML (`función`, `añadir_algo`) | `invalid token ñ`: no compila | Los identificadores de GML son ASCII puro; el texto en español va en comentarios y cadenas, nunca en nombres de función/variable |
| Montar un ECS genérico «porque lo usan los motores grandes» | Más código, misma velocidad (o peor) que instancias + structs | Aplica solo Data Locality (§3.4) al subsistema caliente; no reescribas el juego entero (§3.8) |

---

## 6 · Los 19 patrones de Nystrom → dónde está cada uno en esta biblioteca

| Patrón | Dónde | Estado |
|---|---|---|
| **Command** | [13 · 06 §3.7](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#37-patrón-comando-input-rebinding-y-replays) | Completo |
| **Flyweight** | §3.1 de este documento | Completo |
| **Observer** | [04 · 16 — Señales y desacoplamiento](../04%20-%20Recetas%20por%20g%C3%A9nero/16%20-%20Se%C3%B1ales%20y%20desacoplamiento.md) | Completo |
| **Prototype** | §3.2 de este documento | Completo |
| **Singleton** | [13 · 06 §3.3](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#33-localizador-de-servicios-un-solo-portal-de-globales) (con el argumento en contra) + [01 · 09](../01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md) | Completo |
| **State** | [`06 - Assets y Scripts/scr_state_machine.gml`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) + [07 · 17 — SnowState](../07%20-%20Ecosistema/17%20-%20SnowState%20-%20m%C3%A1quinas%20de%20estado%20%28gu%C3%ADa%20en%20espa%C3%B1ol%29.md) | Completo |
| **Double Buffer** | [13 · 07 §3](07%20-%20Generaci%C3%B3n%20procedural%20avanzada.md#3--autómatas-celulares-cuevas) (`cueva_celular`, comentario «Buffer doble») | Aplicado, sin el nombre hasta este documento |
| **Game Loop** | [01 · 06 §7](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md#7-velocidad-de-juego-delta_time-y-game-loop) + [13 · 06 §3.9](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#39-tiempo-frames-fijos-delta_time-y-paso-fijo-con-acumulador) | Completo |
| **Update Method** | [01 · 06 §4 y §10](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md#4-el-orden-exacto-de-cada-step) | Completo (es el propio evento Step) |
| **Bytecode** | [12 · 01 §7](../12%20-%20Utilidades%20e%20integraciones/01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md#7-ejecutar-código-en-tiempo-de-ejecución-scripting-y-modding) (catálogo de lenguajes) + §3.7 de este documento (intérprete mínimo) | Completo |
| **Subclass Sandbox** | §3.3 de este documento | Completo |
| **Type Object** | [13 · 06 §3.8](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#38-datos-dirigidos-definir-el-juego-en-json) | Completo (catálogo `enemigos.json` → `enemigo_crear()`) |
| **Component** | [13 · 06 §3.6](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#36-composición-frente-a-herencia) | Completo |
| **Event Queue** | §3.6 de este documento + [13 · 12 §6.6](12%20-%20Dise%C3%B1o%20narrativo%20y%20di%C3%A1logos.md#66-cinemáticas-como-cola-de-pasos) (caso particular: cola secuencial de un cinemática) | Completo |
| **Service Locator** | [13 · 06 §3.3](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#33-localizador-de-servicios-un-solo-portal-de-globales) | Completo |
| **Data Locality** | §3.4 de este documento (medido) + [13 · 07 §2.9](07%20-%20Generaci%C3%B3n%20procedural%20avanzada.md#29-rendimiento-precalcula-no-calcules-en-draw) (la regla, sin nombrar ni medir) | Completo |
| **Dirty Flag** | §3.5 de este documento + [04 · 13 §7](../04%20-%20Recetas%20por%20g%C3%A9nero/13%20-%20Estrategia%20y%20gesti%C3%B3n.md#7-errores-clásicos-y-cómo-evitarlos) (caso particular: Flex Panels, sin nombrar) | Completo |
| **Object Pool** | [`06 - Assets y Scripts/scr_pool.gml`](../06%20-%20Assets%20y%20Scripts/scr_pool.gml) + [13 · 06 §1.4](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#14-lo-que-cuesta-cada-patrón) (tabla de coste) | Completo |
| **Spatial Partition** | [13 · 08 §4](08%20-%20F%C3%ADsicas%20a%20mano%20y%20fluidos.md#4--particionado-espacial-colisiones-cuando-hay-cientos-de-cosas) | Completo |
| *(fuera de los 19 de Nystrom)* **ECS** | §3.8 de este documento (veredicto) | Completo |

---

## Ver también

- [13 · 06 — Arquitectura de un proyecto GameMaker](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) — Service Locator, Command, Type Object, Component; el anti-patrón nº 8 que motiva el veredicto de ECS.
- [13 · 07 — Generación procedural avanzada](07%20-%20Generaci%C3%B3n%20procedural%20avanzada.md) — Double Buffer aplicado (`cueva_celular`) y la regla de rendimiento que §3.4 mide.
- [13 · 08 — Físicas a mano y fluidos](08%20-%20F%C3%ADsicas%20a%20mano%20y%20fluidos.md) — Spatial Partition, y por qué tampoco compensa un quadtree la mayoría de las veces (mismo espíritu que el veredicto de ECS).
- [04 · 16 — Señales y desacoplamiento](../04%20-%20Recetas%20por%20g%C3%A9nero/16%20-%20Se%C3%B1ales%20y%20desacoplamiento.md) — Observer; la base síncrona sobre la que Event Queue (§3.6) añade una capa de diferido.
- [12 · 01 §7 — Herramientas del flujo de trabajo](../12%20-%20Utilidades%20e%20integraciones/01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md#7-ejecutar-código-en-tiempo-de-ejecución-scripting-y-modding) — catspeak-lang y el resto de lenguajes embebidos, para cuando el Bytecode de §3.7 se queda corto.
- [`06 - Assets y Scripts/scr_pool.gml`](../06%20-%20Assets%20y%20Scripts/scr_pool.gml) — Object Pool; comparte la idea de «reciclar en vez de crear» con Prototype (§3.2).
- [`06 - Assets y Scripts/scr_state_machine.gml`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) — State; los structs de estado que ahí se recorren son, ellos mismos, un buen candidato a Flyweight si dos instancias comparten un mismo estado sin variables propias.
- [01 · 04 — Structs y constructores (POO en GML)](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) — por qué un struct es un tipo por referencia, la base de por qué Data Locality (§3.4) importa.

---

## Fuentes

Todas consultadas el **6 de septiembre de 2026**.

**Robert Nystrom, *Game Programming Patterns*** — <https://gameprogrammingpatterns.com/contents.html> (índice de los 19 patrones, verificado en vivo con `curl`)

- [Flyweight](https://gameprogrammingpatterns.com/flyweight.html) — estado intrínseco/extrínseco; el ejemplo del terreno por tile que §3.1 traduce directamente.
- [Prototype](https://gameprogrammingpatterns.com/prototype.html) — la delegación por `"prototype"` en JSON (la familia de goblins) que §3.2 lleva al catálogo de `13 · 06 §3.8`.
- [Subclass Sandbox](https://gameprogrammingpatterns.com/subclass-sandbox.html) — operaciones provistas y método sandbox; el ejemplo de superpoderes que §3.3 traduce a habilidades de GameMaker.
- [Data Locality](https://gameprogrammingpatterns.com/data-locality.html) — cachés de CPU, líneas de caché y por qué un array de punteros (structs) es más lento que uno contiguo; §3.4 mide la afirmación en vez de repetirla.
- [Dirty Flag](https://gameprogrammingpatterns.com/dirty-flag.html) — el ejemplo del *scene graph* jerárquico que §3.5 traduce a stats de equipo y a un minimapa en caché.
- [Event Queue](https://gameprogrammingpatterns.com/event-queue.html) — la cola de sonido que coalesce duplicados, base del ejemplo de §3.6.
- [Bytecode](https://gameprogrammingpatterns.com/bytecode.html) — la máquina de pila para hechizos que §3.7 traduce a GML.
- *Component*, *Type Object*, *Service Locator*, *Command*, *State*, *Object Pool*, *Spatial Partition*, *Double Buffer*, *Game Loop*, *Update Method*, *Observer*, *Singleton* — ya citados en su documento correspondiente (tabla de §6); no se repiten aquí.

**Medición propia (§3.4)** — benchmark escrito para este documento, compilado y ejecutado de
verdad con `gm-cli run --runtime native` contra el runtime GameMaker 2026.0.0.23, en un
MacBook Pro con Apple M5 Pro (arm64). Dos pasadas independientes; resultados en la tabla de
§3.4. El *runner* de VM para macOS de este `gm-cli` falló al cargar el proyecto en esta máquina
(confirmado dos veces): se documenta la limitación en vez de callarla, y el número medido se
etiqueta explícitamente como YYC/nativo, no VM.

**Manual oficial de GameMaker LTS 2026** (espejo local en `09 - Manual oficial/`)

- [`get_timer`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Date_And_Time/get_timer.md) — confirma que devuelve microsegundos, la base de la conversión a milisegundos de §3.4.
- [`instance_copy`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Instances/instance_copy.md) — el argumento `perf` y por qué `false` es obligatorio al clonar una plantilla configurada (§3.2).
- [`variable_clone`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Variable_Functions/variable_clone.md) — clonado profundo por defecto (128 niveles) y por qué una copia superficial (`depth = 0`) comparte arrays y structs anidados.

**Corpus descargado (nivel 5 de autoridad, no fuente primaria)** — `11 - Código descargado/librerias/extras/painfully-learned-lessons/optimization.md`, citado en §3.8 solo como contraste independiente al veredicto sobre ECS, nunca como base de la conclusión.
