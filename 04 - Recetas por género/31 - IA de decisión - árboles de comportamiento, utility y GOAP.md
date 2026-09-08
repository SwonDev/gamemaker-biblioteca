# 31 · IA de decisión — árboles de comportamiento, utility y GOAP

> Cómo decide un enemigo **qué hacer** cuando una máquina de estados se queda pequeña: árboles
> de comportamiento (BT), IA por utilidad y planificación GOAP, en GML con structs.
>
> **No cubre el movimiento**: seek, flee, arrive, wander, flocking y evasión están en
> [23 · IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md).
> Este documento decide *qué* hacer; aquel resuelve *cómo* moverse. Las FSM están en
> [`scr_state_machine`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) y en
> [07 · 17 — SnowState](../07%20-%20Ecosistema/17%20-%20SnowState%20-%20máquinas%20de%20estado%20%28guía%20en%20español%29.md).
>
> **Hueco detectado:** la biblioteca tenía FSM, steering, A* y utility a nivel estratégico
> ([13 · 5.5](./13%20-%20Estrategia%20y%20gestión.md)), pero **ningún** documento de árboles de
> comportamiento. Este los monta desde cero.

---

## Qué arquitectura, y cuándo

La regla es incómoda pero cierta: **sube de arquitectura solo cuando la de abajo te duela.**

| Arquitectura | Cuándo es la correcta | Cuándo se queda corta | Coste |
|---|---|---|---|
| **FSM** | 2-6 estados con transiciones que sabes enumerar | A ~10 estados las transiciones son N², y añadir uno toca a todos | 40 líneas |
| **HFSM** | Los estados se agrupan: «combate» contiene disparar/recargar/cubrirse | Sigue costando enumerar dentro de cada grupo | SnowState lo da hecho |
| **Árbol de comportamiento** | Decisiones **con prioridad** reevaluadas cada tick, y ramas **reutilizables** entre enemigos | No sabe puntuar: solo dice sí/no. «¿Ataco o curo?» le queda grande | ~120 líneas |
| **Utility** | Varias opciones válidas a la vez y quieres la *mejor* según el contexto | No sabe encadenar pasos: puntúa acciones sueltas, no planes | ~40 líneas de motor; el ajuste es lo caro |
| **GOAP** | El agente debe **encadenar** acciones que no programaste juntas, y replanificar al fallar | Caro de depurar y de CPU; necesita muchas acciones para lucir | Alto — casi nunca compensa en indie |
| **Minimax / alfa-beta** ([§10 bis](#10-bis--búsqueda-adversarial-minimax-y-poda-alfa-beta)) | Juego **por turnos**, de **información perfecta** y **suma cero**: ajedrez, damas, tres en raya, Conecta 4 | Tiempo real, información oculta (manos, niebla de guerra), más de dos bandos, o un árbol que no cabe en el presupuesto del turno | ~80 líneas núcleo + poda; el árbol crece exponencial con la profundidad |

| Enemigo | Arquitectura mínima que basta |
|---|---|
| Goomba, bala, torreta fija | Ni FSM: un `if` en el Step |
| Zombi que persigue | FSM de 2 estados |
| Jefe con fases | HFSM (la fase es el estado padre) |
| Guardia que patrulla, investiga ruidos, persigue y pide refuerzos | **Árbol de comportamiento** |
| Compañero que elige entre curar, cubrir, atacar o retirarse | **Utility**, o BT con un nodo de utilidad |
| Aldeano de simulación (colonia, superviviente, *Sims*) | **Utility** con consideraciones (hambre, sueño, miedo) |
| IA de facción de un RTS | Utility estratégica → ya está en [13 · 5.5](./13%20-%20Estrategia%20y%20gestión.md) |
| Soldado que abre puertas, rompe ventanas y flanquea sin guion | **GOAP** — y prepárate |

> 🔺 **Un juego real mezcla.** Lo normal en producción es un BT para la estructura y la
> prioridad, una hoja que resuelve por utilidad la decisión difícil, y una FSM dentro de la
> acción de combate. No son opciones excluyentes: son capas.

---

## 1 · Los tres estados de retorno (y por qué «Running» lo cambia todo)

Un árbol se **recorre entero cada tick**. Cada nodo devuelve uno de tres valores y el padre
decide qué hacer con él:

| Estado | Significa | Qué hace el padre |
|---|---|---|
| `EXITO` | «terminé, y salió bien» | La secuencia pasa al siguiente hijo; el selector se da por satisfecho |
| `FALLO` | «no puedo, o no se cumple» | La secuencia aborta; el selector prueba el siguiente hijo |
| `EJECUTANDO` | «sigo en ello, vuelve a preguntarme» | Todo el árbol devuelve `EJECUTANDO` y se congela ahí hasta el tick siguiente |

**`EJECUTANDO` es la razón entera de que los BT sirvan en un juego.** Sin él, «camina hasta la
puerta» tendría que resolverse en un frame o no resolverse. Con él, la hoja devuelve
`EJECUTANDO` mientras camina y `EXITO` al llegar; el árbol la retoma en el mismo punto. Chris
Simpson lo resume en el artículo fundacional del tema: un nodo que devuelve *running* «volverá
a procesarse la próxima vez que se ejecute el árbol, momento en el que podrá tener éxito,
fallar o seguir ejecutándose».

```gml
/// scr_arbol_comportamiento — los tres estados posibles de un nodo
enum ArbolEstado { EXITO, FALLO, EJECUTANDO }
```

> 💡 **El árbol no tiene estado; los nodos sí.** Se recorre de cero cada tick — por eso es
> *reactivo* y por eso una amenaza nueva interrumpe lo que estuviera haciendo. La memoria
> («iba por el tercer paso») vive dentro de los nodos y en la pizarra.

---

## 2 · El árbol mínimo en GML: Selector, Secuencia y hojas

Cuatro tipos de nodo cubren el 90 % de los enemigos. La jerga estándar los agrupa en
**composites** (varios hijos), **decoradores** (un hijo) y **hojas** (ninguno).

```gml
/// scr_arbol_comportamiento
/// SELECTOR = «o esto, o esto, o esto» (OR). Prueba los hijos EN ORDEN y se queda
/// con el primero que NO falle: el orden ES la prioridad. Reevalúa desde arriba
/// cada tick, así que una rama de más prioridad puede INTERRUMPIR a otra a medias.
function Selector(_hijos) constructor {
    hijos  = _hijos;
    activo = -1;                        // índice del hijo que quedó EJECUTANDO

    static tick = function(_agente) {
        for (var _i = 0; _i < array_length(hijos); _i++) {
            var _r = hijos[_i].tick(_agente);
            if (_r == ArbolEstado.FALLO) { continue; }          // el siguiente, a ver
            // Cambiamos de rama: la abandonada se reinicia, o retomaría por el paso 3.
            if (activo != -1 && activo != _i) { hijos[activo].reiniciar(); }
            activo = (_r == ArbolEstado.EJECUTANDO) ? _i : -1;
            return _r;
        }
        if (activo != -1) { hijos[activo].reiniciar(); activo = -1; }
        return ArbolEstado.FALLO;                               // ningún hijo pudo
    };

    static reiniciar = function() {
        for (var _i = 0; _i < array_length(hijos); _i++) { hijos[_i].reiniciar(); }
        activo = -1;
    };
}

/// SECUENCIA = «esto, y luego esto» (AND). Falla en cuanto falla un hijo.
/// RECUERDA por dónde iba: una secuencia empezada se termina.
function Secuencia(_hijos) constructor {
    hijos  = _hijos;
    indice = 0;

    static tick = function(_agente) {
        while (indice < array_length(hijos)) {
            var _r = hijos[indice].tick(_agente);
            if (_r == ArbolEstado.EJECUTANDO) { return ArbolEstado.EJECUTANDO; }
            if (_r == ArbolEstado.FALLO)      { reiniciar(); return ArbolEstado.FALLO; }
            indice++;                                           // EXITO: al siguiente
        }
        reiniciar();
        return ArbolEstado.EXITO;
    };

    static reiniciar = function() {
        indice = 0;
        for (var _i = 0; _i < array_length(hijos); _i++) { hijos[_i].reiniciar(); }
    };
}

/// HOJA CONDICION: pregunta algo. Nunca devuelve EJECUTANDO.
/// La función recibe la pizarra y devuelve un booleano.
function Condicion(_fn, _nombre = "condicion") constructor {
    fn = _fn;   nombre = _nombre;
    static tick = function(_agente) {
        return fn(_agente) ? ArbolEstado.EXITO : ArbolEstado.FALLO;
    };
    static reiniciar = function() {};
}

/// HOJA ACCION: hace algo. La función DEBE devolver un ArbolEstado:
/// EJECUTANDO mientras dure, EXITO al acabar, FALLO si no pudo.
function Accion(_fn, _nombre = "accion") constructor {
    fn = _fn;   nombre = _nombre;
    static tick = function(_agente) {
        _agente.nodo_activo = nombre;                           // para depurar (§6)
        return fn(_agente);
    };
    static reiniciar = function() {};
}
```

> 🔺 **Selector y Secuencia se distinguen por una sola letra mental: OR y AND.** El selector
> busca *algo que funcione* y solo falla si fallan todos. La secuencia exige que funcione
> *todo* y falla en cuanto falla uno. Si los confundes, el enemigo hará justo lo contrario de
> lo que esperabas y parecerá un bug del motor.

> ⚠️ **El `reiniciar()` al cambiar de rama es la sutileza que casi ninguna implementación
> pequeña de GML resuelve**, y produce un bug desconcertante: el guardia deja a medias «ir al
> ruido → mirar → volver» para perseguirte, te pierde, y al retomar la investigación **empieza
> por “volver”**. No quites esa línea por parecer código de más.

**Parallel**, el cuarto composite, ejecuta todos sus hijos en el mismo tick y agrega los
resultados con una política. Sirve para «dispara *mientras* te mueves a cubierto».

> ⚠️ **No lo escribas hasta que lo necesites.** En 2D casi todo lo que se resuelve con Parallel
> sale mejor con dos árboles pequeños (uno de movimiento, otro de combate) ticando en el mismo
> Step y compartiendo pizarra: más fácil de depurar, y sin el problema clásico del Parallel
> (qué hacer con los hijos que siguen `EJECUTANDO` cuando el nodo ya ha decidido).

---

## 3 · La pizarra (*blackboard*): la memoria del agente

El árbol es la estructura; lo que cambia de un enemigo a otro es su **pizarra**: un struct con
la instancia dueña y su memoria.

```gml
/// obj_guardia · Create
velocidad = 1.6;   velocidad_paseo = 0.5;   rumbo = random(360);

pizarra = {
    duena     : id,        // la instancia; las acciones actúan sobre ella
    objetivo  : noone,
    ultima_x  : -1,        // dónde vio al jugador por última vez
    ultima_y  : -1,
    alerta    : 0,         // 0 tranquilo · 1 sospecha · 2 combate
    vida      : 100,
    vida_max  : 100,
    vision_cache        : false,
    vision_calculada_en : -1,
    nodo_activo : ""       // solo para depurar
};
arbol = construir_arbol_guardia();     // §5

/// obj_guardia · Step
arbol.tick(pizarra);
```

> 🔺 **Un árbol por enemigo, no uno compartido.** `Secuencia.indice` y `Selector.activo` son
> estado del *recorrido*: si 20 guardias ticaran el mismo objeto `Secuencia` se pisarían el
> índice entre ellos. Dos salidas honestas: **(1)** construir el árbol en el Create de cada
> enemigo — unos cuantos structs por instancia, irrelevante con decenas de enemigos; **(2)**
> guardar el recorrido en la pizarra — más elegante, bastante más código, y solo compensa con
> cientos de agentes. Este documento usa la (1). Lo que sí puedes compartir sin cuidado son las
> **funciones hoja**, que no tienen estado.

Sobre `constructor`, `static` y `method`:
[01 · 04 — Structs y constructores](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md).

---

## 4 · Decoradores: Inversor y Enfriamiento

Un decorador tiene **un solo hijo** y transforma lo que devuelve.

```gml
/// INVERSOR: EXITO ↔ FALLO. EJECUTANDO pasa igual.
/// Sirve para «si NO hay pared delante» reutilizando la condición «hay pared».
function Inversor(_hijo) constructor {
    hijo = _hijo;
    static tick = function(_agente) {
        var _r = hijo.tick(_agente);
        if (_r == ArbolEstado.EXITO) { return ArbolEstado.FALLO; }
        if (_r == ArbolEstado.FALLO) { return ArbolEstado.EXITO; }
        return _r;
    };
    static reiniciar = function() { hijo.reiniciar(); };
}

/// ENFRIAMIENTO (cooldown): tras un EXITO el hijo queda bloqueado N milisegundos
/// y el decorador devuelve FALLO mientras tanto. Es LA pieza que evita el spam.
/// Usa current_time (ms reales) y no un contador de frames: así sigue siendo
/// correcto aunque el árbol tique de forma escalonada (§12).
function Enfriamiento(_hijo, _espera_ms) constructor {
    hijo = _hijo;   espera_ms = _espera_ms;   listo_en = 0;
    static tick = function(_agente) {
        if (current_time < listo_en) { return ArbolEstado.FALLO; }
        var _r = hijo.tick(_agente);
        if (_r == ArbolEstado.EXITO) { listo_en = current_time + espera_ms; }
        return _r;
    };
    static reiniciar = function() { hijo.reiniciar(); };
}

/// REPETIDOR: repite al hijo N veces (o para siempre con _veces = -1).
function Repetidor(_hijo, _veces = -1) constructor {
    hijo = _hijo;   veces = _veces;   hechas = 0;
    static tick = function(_agente) {
        var _r = hijo.tick(_agente);
        if (_r == ArbolEstado.EJECUTANDO) { return ArbolEstado.EJECUTANDO; }
        hechas++;
        if (veces > 0 && hechas >= veces) { reiniciar(); return _r; }
        hijo.reiniciar();
        return ArbolEstado.EJECUTANDO;      // seguimos repitiendo
    };
    static reiniciar = function() { hechas = 0; hijo.reiniciar(); };
}
```

Los otros dos decoradores clásicos son triviales y no necesitan código: el **Succeeder**
(devuelve siempre `EXITO`, para que un fallo no aborte la secuencia) y el **Repeat-until-fail**
(un `Repetidor` que corta con `FALLO` en vez de con `EXITO`).

> 💡 **El enfriamiento va en el árbol, no dentro de la acción.** Si el temporizador vive en
> `ia_atacar()`, no puedes reutilizar esa acción con otra cadencia. Envolviéndola,
> `new Enfriamiento(new Accion(ia_atacar), 900)` y `... 200)` son el mismo ataque a dos ritmos.

---

## 5 · Un enemigo completo

El guardia clásico: **si está malherido huye y se cura; si te ve, persigue y ataca; si no,
patrulla.** El orden de los hijos del selector **es** el orden de prioridad.

```gml
/// scr_ia_guardia — las hojas. Reciben la pizarra.
/// El movimiento (huir_de, lengthdir) NO se reescribe aquí: está en 04 · 23.

function ia_esta_malherido(_p) {
    return (_p.vida < _p.vida_max * 0.25);
}

/// @desc ¿Hay línea de visión libre entre dos puntos?
///       collision_line(x1, y1, x2, y2, obj, prec, notme)
function hay_vision_libre(_x1, _y1, _x2, _y2) {
    return (collision_line(_x1, _y1, _x2, _y2, obj_pared, false, true) == noone);
}

function ia_ve_al_jugador(_p) {
    // Una sola comprobación por tick, aunque el árbol pregunte tres veces.
    if (_p.vision_calculada_en == current_time) { return _p.vision_cache; }
    _p.vision_calculada_en = current_time;
    _p.vision_cache = false;

    if (instance_exists(obj_jugador)) {
        // Distancia primero: descarta la mayoría sin lanzar ningún rayo.
        if (point_distance(_p.duena.x, _p.duena.y, obj_jugador.x, obj_jugador.y) <= 220) {
            _p.vision_cache = hay_vision_libre(_p.duena.x, _p.duena.y,
                                               obj_jugador.x, obj_jugador.y);
        }
    }
    if (_p.vision_cache) {                    // apuntamos dónde estaba, por si lo perdemos
        _p.objetivo = obj_jugador.id;
        _p.ultima_x = obj_jugador.x;
        _p.ultima_y = obj_jugador.y;
        _p.alerta   = 2;
    }
    return _p.vision_cache;
}

function ia_huir(_p) {
    if (!instance_exists(obj_jugador)) { return ArbolEstado.EXITO; }
    var _tx = obj_jugador.x, _ty = obj_jugador.y;
    with (_p.duena) { huir_de(_tx, _ty, velocidad * 1.3); }          // ← 04 · 23
    var _d = point_distance(_p.duena.x, _p.duena.y, _tx, _ty);
    return (_d > 320) ? ArbolEstado.EXITO : ArbolEstado.EJECUTANDO;
}

function ia_curarse(_p) {
    _p.vida = min(_p.vida + 0.5, _p.vida_max);
    return (_p.vida >= _p.vida_max * 0.6) ? ArbolEstado.EXITO : ArbolEstado.EJECUTANDO;
}

function ia_perseguir(_p) {
    if (!instance_exists(_p.objetivo)) { return ArbolEstado.FALLO; }
    // Las coordenadas se sacan ANTES del with: dentro, `x` e `y` ya son las del enemigo.
    var _tx = _p.objetivo.x, _ty = _p.objetivo.y;
    with (_p.duena) { mp_potential_step(_tx, _ty, velocidad, false); }
    return ArbolEstado.EJECUTANDO;      // perseguir no "termina": lo corta la prioridad
}

function ia_atacar(_p) {
    if (!instance_exists(_p.objetivo)) { return ArbolEstado.FALLO; }
    if (point_distance(_p.duena.x, _p.duena.y, _p.objetivo.x, _p.objetivo.y) > 40) {
        return ArbolEstado.FALLO;       // demasiado lejos: que persiga la otra rama
    }
    with (_p.duena) { golpear(); }      // tu función de daño
    return ArbolEstado.EXITO;           // EXITO dispara el enfriamiento del decorador
}

function ia_patrullar(_p) {
    with (_p.duena) {                   // wander, de 04 · 23
        rumbo += random_range(-6, 6);
        x += lengthdir_x(velocidad_paseo, rumbo);
        y += lengthdir_y(velocidad_paseo, rumbo);
    }
    return ArbolEstado.EJECUTANDO;
}
```

```gml
/// scr_ia_guardia — el árbol. Uno por enemigo (§3).
function construir_arbol_guardia() {
    return new Selector([

        // 1 · PRIORIDAD MÁXIMA: si estoy malherido, huyo y me curo.
        new Secuencia([
            new Condicion(ia_esta_malherido, "malherido?"),
            new Accion(ia_huir,    "huir"),
            new Accion(ia_curarse, "curarse")
        ]),

        // 2 · Si te veo: atacar con cadencia, y si no llego, acercarme.
        new Secuencia([
            new Condicion(ia_ve_al_jugador, "te veo?"),
            new Selector([
                new Enfriamiento(new Accion(ia_atacar, "atacar"), 900),
                new Accion(ia_perseguir, "perseguir")
            ])
        ]),

        // 3 · Si no hay nada mejor: patrullar.
        new Accion(ia_patrullar, "patrullar")
    ]);
}
```

> 💡 **Léelo de arriba abajo y ya sabes qué hará el enemigo.** Ese es el único argumento real a
> favor de los BT frente a una FSM: la prioridad está escrita en un sitio, no repartida entre
> veinte `if` de transición. El `Selector` interno del punto 2 es el patrón canónico «ataca si
> puedes, si no acércate»: el enfriamiento devuelve `FALLO` mientras se recarga, así que la
> persecución toma el relevo sola.

> 🔺 **Dentro de un `with`, `x` e `y` son las de la instancia dueña.** Es el error nº 1 al
> escribir hojas. Los `var` locales y los argumentos sí siguen siendo accesibles dentro del
> `with`, así que la costumbre segura es sacar las coordenadas a locales antes de entrar.
> `ia_cubrirse`, `ia_hay_orden`, `ia_ejecutar_orden` y `ia_seguir_al_jugador`, que aparecen más
> abajo, son tuyas y siguen exactamente este molde.

---

## 6 · Depurar el árbol: ver qué nodo manda

Un BT que no puedes ver es una caja negra peor que la FSM que sustituiste.

```gml
/// obj_control · Create — depth muy negativo para ir primero (mismo patrón que
/// objTime, 04 · 15 §5.0): sin esto, el primer obj_guardia revienta con
/// «variable global 'depurar_ia' no definida» en su propio Create de más abajo.
global.depurar_ia = false;   // pon a `true` mientras ajustas el árbol
```

```gml
/// obj_guardia · Draw
draw_self();
if (global.depurar_ia) {
    draw_set_color(c_yellow);
    draw_text(x - 24, y - 40, pizarra.nodo_activo);

    // La línea de visión dibujada: se ve al instante POR QUÉ no te ve.
    if (instance_exists(obj_jugador)) {
        var _libre = hay_vision_libre(x, y, obj_jugador.x, obj_jugador.y);
        draw_set_color(_libre ? c_lime : c_red);
        draw_line(x, y, obj_jugador.x, obj_jugador.y);
    }
    draw_set_color(c_white);
}
```

En el **Debug Overlay** del runtime (F2 en modo depuración) las funciones `dbg_*` **no toman
cadenas sueltas para vigilar**: necesitan una **referencia** creada con `ref_create`.

```gml
/// obj_guardia · Create — al final
if (global.depurar_ia) {
    dbg_view("IA del guardia", true);
    dbg_section("Guardia " + string(id));
    // dbg_watch(dbgref, [label])  ·  ref_create(struct_o_instancia, "nombre")
    dbg_watch(ref_create(pizarra, "nodo_activo"), "Nodo activo");
    dbg_watch(ref_create(pizarra, "alerta"),      "Alerta");
    dbg_watch(ref_create(pizarra, "vida"),        "Vida");
    dbg_watch(ref_create(pizarra, "ultima_x"),    "Último visto X");
}
```

📘 [`dbg_watch`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Debugging/dbg_watch.md)
· [`ref_create`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Variable_Functions/ref_create.md)

> 🔺 **El orden es `dbg_watch(referencia, etiqueta)`, no al revés**, y `dbg_section(nombre,
> [abierta])` toma un booleano, no coordenadas. Compruébalo siempre con
> `python3 "_indice/buscar.py" dbg_watch`: es una familia donde la memoria falla mucho. El
> overlay completo, en [01 · 15 — Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md).

---

## 7 · Árboles como datos: balancear sin recompilar

Con el árbol escrito en GML, cambiar «ataca cada 900 ms» por «cada 700» obliga a recompilar.
Como **datos**, un diseñador lo toca en un `.json` y prueba al vuelo.

```gml
/// datos/arbol_guardia.json (en Included Files)
{ "tipo": "selector", "hijos": [
    { "tipo": "secuencia", "hijos": [
        { "tipo": "condicion", "fn": "ia_esta_malherido" },
        { "tipo": "accion",    "fn": "ia_huir" },
        { "tipo": "accion",    "fn": "ia_curarse" } ]},
    { "tipo": "secuencia", "hijos": [
        { "tipo": "condicion", "fn": "ia_ve_al_jugador" },
        { "tipo": "selector",  "hijos": [
            { "tipo": "enfriamiento", "espera_ms": 900,
              "hijo": { "tipo": "accion", "fn": "ia_atacar" } },
            { "tipo": "accion", "fn": "ia_perseguir" } ]} ]},
    { "tipo": "accion", "fn": "ia_patrullar" } ]}
```

```gml
/// scr_arbol_datos — de struct anidado a árbol de verdad. Recursivo.
function arbol_desde_datos(_def) {
    if (!is_struct(_def) || !struct_exists(_def, "tipo")) {
        show_debug_message("arbol_desde_datos: nodo sin 'tipo'.");
        return new Accion(function(_p) { return ArbolEstado.FALLO; }, "roto");
    }

    switch (_def.tipo) {
        case "selector":
        case "secuencia":
            var _hijos = [];
            var _lista = struct_exists(_def, "hijos") ? _def.hijos : [];
            for (var _i = 0; _i < array_length(_lista); _i++) {
                array_push(_hijos, arbol_desde_datos(_lista[_i]));
            }
            return (_def.tipo == "selector") ? new Selector(_hijos) : new Secuencia(_hijos);

        case "inversor":     return new Inversor(arbol_desde_datos(_def.hijo));
        case "enfriamiento": return new Enfriamiento(arbol_desde_datos(_def.hijo), _def.espera_ms);
        case "repetidor":    return new Repetidor(arbol_desde_datos(_def.hijo),
                                    struct_exists(_def, "veces") ? _def.veces : -1);

        case "condicion":
        case "accion":
            // El nombre se resuelve contra un registro EXPLÍCITO, nunca evaluando cadenas.
            var _fn = global.__ia_hojas[$ _def.fn];
            if (!is_callable(_fn)) {
                show_debug_message("arbol_desde_datos: hoja desconocida '" + string(_def.fn) + "'.");
                _fn = function(_p) { return ArbolEstado.FALLO; };
            }
            return (_def.tipo == "condicion") ? new Condicion(_fn, _def.fn)
                                              : new Accion(_fn, _def.fn);
    }

    show_debug_message("arbol_desde_datos: tipo desconocido '" + string(_def.tipo) + "'.");
    return new Accion(function(_p) { return ArbolEstado.FALLO; }, "desconocido");
}
```

```gml
/// obj_control · Game Start — registrar las hojas y cargar la definición
global.__ia_hojas = {
    ia_esta_malherido, ia_ve_al_jugador, ia_huir, ia_curarse,
    ia_perseguir, ia_atacar, ia_patrullar        // atajo: clave = nombre de la variable
};

var _b   = buffer_load("arbol_guardia.json");
var _txt = buffer_read(_b, buffer_text);
buffer_delete(_b);
global.def_guardia = json_parse(_txt);

/// obj_guardia · Create
arbol = arbol_desde_datos(global.def_guardia);
```

> 🔺 **Registro explícito, no `asset_get_index` ni evaluación de cadenas.** Un mapa
> `nombre → función` escrito a mano es aburrido, pero es lo único que te avisa cuando renombras
> `ia_atacar` y el JSON se queda apuntando al viejo. Además impide que un archivo de datos
> pueda llamar a cualquier cosa.

> ⚠️ **`json_parse` en 2026 convierte cadenas que parecen números**: `"0900"` puede volver como
> `900`. Existe el argumento `inhibit_string_convert` y la opción de *Deprecated Behaviours*;
> el detalle en [01 · 14 — Persistencia y archivos §8](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md).

---

## 8 · Utility AI mínimo: puntuar en vez de ramificar

Un BT solo sabe decir sí o no. Cuando **todas** las opciones son válidas y la pregunta es *cuál
es la mejor ahora*, el árbol se llena de umbrales arbitrarios. Ahí entra la utilidad: **cada
acción se puntúa; gana la más alta.**

La teoría, en dos ideas de David «Rez» Graham (*Game AI Pro*, cap. 9):

1. **Toda puntuación se normaliza a 0-1.** No porque 0-1 sea mágico, sino porque todas deben
   estar en la misma escala para poder combinarse y compararse. «15» no significa nada si no
   sabes si es sobre 25 o sobre 100.
2. **Una decisión es una combinación de consideraciones.** Cada una convierte un dato crudo
   (vida, distancia, munición) en utilidad 0-1 mediante una **curva**.

| Curva | Fórmula | Para qué |
|---|---|---|
| Lineal | `x / m` | Proporción directa: «cuanta más munición, mejor» |
| Cuadrática | `power(x/m, k)`, `k > 1` | Solo importa cerca del máximo: urgencia tardía |
| Cuadrática girada | `power(x/m, k)`, `0 < k < 1` | Importa enseguida y luego se satura |
| Logística (sigmoide) | `1 / (1 + exp(-x))` | Umbral suave: casi nada, salto, casi todo |
| Lineal a trozos | interpolar entre puntos a mano | Cuando ninguna fórmula da la forma que quieres — es lo que usa *The Sims* |

```gml
/// scr_utilidad — curvas. Todas devuelven 0..1.
function curva_lineal(_x, _max) {
    return clamp(_x / max(_max, 0.0001), 0, 1);
}
function curva_potencia(_x, _max, _k) {
    return clamp(power(clamp(_x / max(_max, 0.0001), 0, 1), _k), 0, 1);
}
/// _centro: valor donde vale 0.5 · _pendiente: cuanto mayor, más brusca.
function curva_logistica(_x, _centro, _pendiente) {
    return 1 / (1 + exp(-_pendiente * (_x - _centro)));
}
/// Lineal a trozos: interpola entre puntos ajustados a mano.
/// _puntos = [[x0,y0], [x1,y1], ...] ordenados por x.
function curva_tramos(_x, _puntos) {
    var _n = array_length(_puntos);
    if (_n == 0)                  { return 0; }
    if (_x <= _puntos[0][0])      { return _puntos[0][1]; }
    if (_x >= _puntos[_n - 1][0]) { return _puntos[_n - 1][1]; }
    for (var _i = 1; _i < _n; _i++) {
        if (_x <= _puntos[_i][0]) {
            var _t = (_x - _puntos[_i - 1][0])
                   / max(_puntos[_i][0] - _puntos[_i - 1][0], 0.0001);
            return lerp(_puntos[_i - 1][1], _puntos[_i][1], _t);
        }
    }
    return _puntos[_n - 1][1];
}

/// scr_utilidad — una acción puntuable.
/// _puntuar: function(_pizarra) -> 0..1  ·  _hacer: function(_pizarra) -> ArbolEstado
function OpcionUtil(_nombre, _puntuar, _hacer) constructor {
    nombre = _nombre;   puntuar = _puntuar;   hacer = _hacer;
}

/// Elige entre varias OpcionUtil. Devuelve la elegida, o undefined.
/// _tolerancia 0 = siempre la mejor. 0.1 = azar ponderado entre las que estén
/// dentro del 10 % de la mejor: variedad sin permitir tonterías.
function elegir_por_utilidad(_opciones, _pizarra, _umbral = 0.05, _tolerancia = 0) {
    var _n = array_length(_opciones);
    if (_n == 0) { return undefined; }

    var _puntos = array_create(_n, 0);
    var _mejor  = 0;
    for (var _i = 0; _i < _n; _i++) {
        _puntos[_i] = clamp(_opciones[_i].puntuar(_pizarra), 0, 1);
        _mejor = max(_mejor, _puntos[_i]);
    }

    if (_mejor < _umbral)   { return undefined; }              // nada merece la pena
    if (_tolerancia <= 0)   { return _opciones[array_get_index(_puntos, _mejor)]; }

    var _corte = _mejor * (1 - _tolerancia);
    var _cand = [], _pesos = [], _suma = 0;
    for (var _i = 0; _i < _n; _i++) {
        if (_puntos[_i] >= _corte) {
            array_push(_cand, _opciones[_i]);
            array_push(_pesos, _puntos[_i]);
            _suma += _puntos[_i];
        }
    }
    var _tirada = random(_suma), _acum = 0;
    for (var _i = 0; _i < array_length(_cand); _i++) {
        _acum += _pesos[_i];
        if (_tirada <= _acum) { return _cand[_i]; }
    }
    return _cand[array_length(_cand) - 1];
}
```

Un compañero que decide entre curarse, atacar y cubrirse:

```gml
/// obj_companero · Create
opciones = [
    new OpcionUtil("curarse", function(_p) {
        var _falta = 1 - (_p.vida / _p.vida_max);
        var _tengo = (_p.botiquines > 0) ? 1 : 0;          // consideración de veto
        return curva_logistica(_falta, 0.6, 8) * _tengo;
    }, ia_curarse),

    new OpcionUtil("atacar", function(_p) {
        if (!instance_exists(_p.objetivo)) { return 0; }
        var _d     = point_distance(_p.duena.x, _p.duena.y, _p.objetivo.x, _p.objetivo.y);
        var _cerca = 1 - curva_lineal(_d, 400);            // mejor cuanto más cerca
        var _mun   = curva_potencia(_p.municion, 30, 0.5); // basta con tener algo
        var _sano  = curva_lineal(_p.vida, _p.vida_max);
        return _cerca * _mun * _sano;
    }, ia_atacar),

    new OpcionUtil("cubrirse", function(_p) {
        var _falta   = 1 - (_p.vida / _p.vida_max);
        var _sin_mun = 1 - curva_lineal(_p.municion, 30);
        return max(_falta * 0.8, _sin_mun * 0.6);
    }, ia_cubrirse)
];
decidida = undefined;
inercia  = 0;                  // frames de compromiso con la decisión actual

/// obj_companero · Step
inercia--;
if (is_undefined(decidida) || inercia <= 0) {
    var _nueva = elegir_por_utilidad(opciones, pizarra, 0.05, 0.10);
    if (!is_undefined(_nueva)) {
        if (is_undefined(decidida) || _nueva.nombre != decidida.nombre) { inercia = 30; }
        decidida = _nueva;
    }
}
if (!is_undefined(decidida)) {
    if (decidida.hacer(pizarra) != ArbolEstado.EJECUTANDO) { inercia = 0; }
}
```

> 🔺 **La inercia no es un adorno: sin ella la utilidad oscila.** Es el problema que Graham
> llama exactamente así (*inertia*): si «atacar» y «huir» puntúan 0.51 y 0.50 y decides cada
> frame, el enemigo dispara, huye, dispara, huye. Las tres curas conocidas: comprometerse un
> rato (lo de arriba), dar un bonus a la acción en curso, o no volver a decidir hasta que la
> actual termine.

> 💡 **Multiplicar consideraciones = veto; promediarlas = matiz.** `urgencia * tengo_botiquín`
> pone la puntuación a cero si no hay botiquines: eso es lo que quieres. Promediarlas daría 0.5
> y el compañero intentaría curarse con las manos vacías. Multiplica cuando una consideración
> pueda invalidar la acción; promedia cuando solo la matice.

> ⚠️ **A nivel de facción esto ya está en la biblioteca.**
> [13 · Estrategia y gestión §5.5](./13%20-%20Estrategia%20y%20gestión.md) tiene una IA por
> utilidad completa (recolectar / defender / atacar / expandir) con su umbral y su intervalo de
> decisión. No la repitas: lo de aquí es el mismo principio a nivel de **agente individual**,
> con curvas y con inercia.

---

## 9 · Mezclar los dos: el nodo de utilidad dentro del árbol

Lo que se hace en producción: el BT pone la **estructura y la prioridad**; la utilidad resuelve
**el nodo donde hay varias opciones válidas**. Es la idea de Bill Merrill en *Game AI Pro*
cap. 10, «Building Utility Decisions into Your Existing Behavior Tree».

```gml
/// scr_arbol_comportamiento — composite que elige por puntuación, no por orden.
/// Se enchufa exactamente donde iría un Selector.
function SelectorUtilidad(_opciones, _umbral = 0.05, _tolerancia = 0) constructor {
    opciones = _opciones;   umbral = _umbral;   tolerancia = _tolerancia;
    elegida  = undefined;

    static tick = function(_agente) {
        // Solo reelegimos cuando no hay nada a medias: eso es la inercia.
        if (is_undefined(elegida)) {
            elegida = elegir_por_utilidad(opciones, _agente, umbral, tolerancia);
            if (is_undefined(elegida)) { return ArbolEstado.FALLO; }
        }
        _agente.nodo_activo = elegida.nombre;
        var _r = elegida.hacer(_agente);
        if (_r != ArbolEstado.EJECUTANDO) { elegida = undefined; }
        return _r;
    };
    static reiniciar = function() { elegida = undefined; };
}

/// El árbol del compañero: prioridad arriba, puntuación abajo.
arbol = new Selector([
    new Secuencia([                                   // regla dura: se obedece
        new Condicion(ia_hay_orden, "¿orden?"),
        new Accion(ia_ejecutar_orden, "obedecer")
    ]),
    new SelectorUtilidad(opciones, 0.05, 0.10),       // zona gris: hay una mejor
    new Accion(ia_seguir_al_jugador, "seguir")
]);
```

> 💡 **La regla práctica: BT para lo que es una regla, utilidad para lo que es un juicio.** «Si
> te dan una orden, obedece» es una regla — no la puntúes. «¿Curo, disparo o me cubro?» es un
> juicio — no lo ramifiques con umbrales.

---

## 10 · GOAP en 40 líneas honestas

**GOAP** (*Goal-Oriented Action Planning*) es lo que Jeff Orkin montó para *F.E.A.R.* (2005) y
contó en la GDC 2006. La idea, en una frase suya: una FSM le dice a la IA **exactamente cómo
comportarse en cada situación**; un planificador le dice **cuáles son sus objetivos y sus
acciones, y deja que sea ella quien decida en qué orden encadenarlas**. Las FSM son
*procedimentales*; la planificación es *declarativa*.

- **Estado del mundo**: struct de variables que describen la situación.
- **Objetivo**: un estado del mundo deseado, **parcial** (`{ enemigo_muerto: true }`).
- **Acción**: **precondiciones**, **efectos** y **coste**. En *F.E.A.R.* el coste por acción es
  justo lo que permite usar A* para guiar la búsqueda hacia el plan más barato.
- **Plan**: la cadena de acciones del estado actual al objetivo.

Orkin lo resume con una tabla que vale por media charla: A* sirve para dos cosas distintas y lo
único que cambia son los nodos y las aristas.

| A* | Navegación | Planificación |
|---|---|---|
| Nodos | Polígonos del *navmesh* | Estados del mundo |
| Aristas | Bordes entre polígonos | Acciones |

```gml
/// scr_planificador — GOAP mínimo pero real.
/// Acción: { nombre, coste, precond: {...}, efectos: {...} }
/// Estado: struct de valores simples (bool / número / cadena).

/// Clave estable de un estado. struct_get_names NO garantiza el orden, así que
/// se ordena antes de concatenar; si no, el mismo estado tendría dos claves.
function estado_clave(_estado) {
    var _n = struct_get_names(_estado);
    array_sort(_n, true);
    var _s = "";
    for (var _i = 0; _i < array_length(_n); _i++) {
        _s += _n[_i] + "=" + string(_estado[$ _n[_i]]) + ";";
    }
    return _s;
}

/// ¿El estado cumple TODAS las claves del patrón? (el patrón es parcial)
function estado_cumple(_estado, _patron) {
    var _n = struct_get_names(_patron);
    for (var _i = 0; _i < array_length(_n); _i++) {
        var _k = _n[_i];
        if (!struct_exists(_estado, _k))    { return false; }
        if (_estado[$ _k] != _patron[$ _k]) { return false; }
    }
    return true;
}

/// Aplica los efectos de una acción sobre una COPIA del estado.
function estado_aplicar(_estado, _efectos) {
    var _nuevo = variable_clone(_estado);
    var _n = struct_get_names(_efectos);
    for (var _i = 0; _i < array_length(_n); _i++) { _nuevo[$ _n[_i]] = _efectos[$ _n[_i]]; }
    return _nuevo;
}

/// Plan más barato mediante cola de prioridad por coste acumulado.
/// Es Dijkstra, no A*: en un espacio de estados rara vez tienes una heurística
/// admisible decente, y mentir con una te da planes malos.
/// @returns {Array<Struct>} la secuencia de acciones, o [] si no hay plan.
function planificar(_inicial, _objetivo, _acciones, _max_nodos = 400) {
    if (estado_cumple(_inicial, _objetivo)) { return []; }

    var _cola = ds_priority_create();
    // El coste acumulado va DENTRO del nodo: no hay función que devuelva la
    // prioridad del mínimo sin sacarlo antes de la cola.
    ds_priority_add(_cola, { estado: _inicial, plan: [], coste: 0 }, 0);

    var _vistos = {};
    _vistos[$ estado_clave(_inicial)] = true;
    var _explorados = 0;

    while (!ds_priority_empty(_cola) && _explorados < _max_nodos) {
        var _nodo = ds_priority_delete_min(_cola);
        _explorados++;

        for (var _i = 0; _i < array_length(_acciones); _i++) {
            var _a = _acciones[_i];
            if (!estado_cumple(_nodo.estado, _a.precond)) { continue; }

            var _siguiente = estado_aplicar(_nodo.estado, _a.efectos);
            var _clave = estado_clave(_siguiente);
            if (struct_exists(_vistos, _clave)) { continue; }
            _vistos[$ _clave] = true;

            var _plan = variable_clone(_nodo.plan);
            array_push(_plan, _a);
            var _coste = _nodo.coste + _a.coste;

            if (estado_cumple(_siguiente, _objetivo)) {
                ds_priority_destroy(_cola);
                return _plan;
            }
            ds_priority_add(_cola, { estado: _siguiente, plan: _plan, coste: _coste }, _coste);
        }
    }
    ds_priority_destroy(_cola);
    return [];      // sin plan: el agente cae a un objetivo de menos prioridad
}
```

```gml
/// Uso: eliminar al enemigo, con o sin arma cargada.
var _acciones = [
    { nombre: "recargar",        coste: 2, precond: { tengo_arma: true, cargada: false },
                                           efectos: { cargada: true } },
    { nombre: "coger_arma",      coste: 4, precond: { tengo_arma: false, hay_arma_cerca: true },
                                           efectos: { tengo_arma: true, cargada: false } },
    { nombre: "disparar",        coste: 1, precond: { tengo_arma: true, cargada: true },
                                           efectos: { enemigo_muerto: true } },
    { nombre: "cuerpo_a_cuerpo", coste: 8, precond: { enemigo_cerca: true },
                                           efectos: { enemigo_muerto: true } }
];
var _mundo = { tengo_arma: false, cargada: false, hay_arma_cerca: true,
               enemigo_cerca: false, enemigo_muerto: false };

var _plan = planificar(_mundo, { enemigo_muerto: true }, _acciones);
// _plan → [coger_arma, recargar, disparar]  (coste 7, más barato que el 8 del melé)
```

> ⚠️ **Y ahora la parte honesta: la mayoría de los juegos indie no necesitan esto.** El valor de
> GOAP en *F.E.A.R.* no fue hacer cosas imposibles con una FSM —Orkin lo dice literalmente—,
> sino que **la combinación e interacción de decenas de comportamientos se volvía inmanejable a
> mano**. Con quince acciones por personaje, compensa. Con un enemigo que persigue y ataca,
> GOAP es una forma cara de escribir dos `if`.
>
> Lo que sí merece la pena robarle aunque no lo uses: **replanificar cuando el plan falla**. El
> soldado que intenta abrir la puerta, no puede, y *entonces* decide patearla, y si tampoco
> puede se tira por la ventana — ese comportamiento emergente sale de recalcular el plan con lo
> que se acaba de aprender, no de haberlo guionizado.

> 🔺 **Presupuesta la búsqueda o te comerá el frame.** El `_max_nodos = 400` no es decorativo:
> el espacio de estados crece exponencialmente con el número de variables. Planifica **solo
> cuando cambie el objetivo o falle el plan**, nunca cada frame.

A* de verdad sobre un mapa (que es otra cosa):
[`scr_grid_pathfinding`](../06%20-%20Assets%20y%20Scripts/scr_grid_pathfinding.gml).

---

## 10 bis · Búsqueda adversarial: minimax y poda alfa-beta

**Minimax** (con su optimización real, la **poda alfa-beta**) es el algoritmo clásico para que
una IA elija el mejor movimiento en un juego de **dos bandos, por turnos, de información
perfecta y de suma cero**: ambos ven el tablero entero, se turnan, y lo que gana uno lo pierde
el otro exactamente. Ajedrez, damas, tres en raya, Conecta 4. **No tiene nada que ver con lo que
decide un enemigo en tiempo real**, y por eso va aparte, después de FSM, BT, utility y GOAP — no
dentro de ellos.

> 🔺 **Distinto problema, distinta caja de herramientas.** Todo lo de §1-§10 asume un agente que
> decide solo, tick a tick, contra un mundo que no le devuelve la jugada. Minimax asume lo
> contrario: un rival que **también piensa**, y que en cada uno de sus turnos va a escoger lo
> peor posible para ti. No sustituye a ninguna arquitectura anterior de este documento — responde
> a una pregunta que ninguna de ellas se hace: «si el rival juega perfecto, ¿cuál es mi mejor
> jugada ahora?».

El mismo Orkin de §10 ya reutilizaba A* para dos cosas distintas —navegar y planificar—, con
solo cambiar qué son los nodos y qué son las aristas. Minimax recorre un árbol de estados por
tercera vez, pero con una diferencia que lo cambia todo: en GOAP el agente elige sus propias
acciones sobre un mundo pasivo, que nunca le lleva la contraria. En minimax el árbol se recorre
en dos roles que se alternan un nivel por movimiento: **MAX** (nosotros) elige la rama que más le
conviene; **MIN** (el rival) elige la que **menos** le conviene a MAX. El árbol entero es una
negociación pesimista: MAX asume que MIN siempre va a jugar lo mejor para sí mismo, nunca un
error.

**El tablero, como dato.** Igual que en §7 un árbol de comportamiento se representa como struct
anidado en vez de como control de flujo fijo, aquí el estado del juego es un **array plano**, no
nueve variables `casilla_0_0`…`casilla_2_2`. Así una sola función recorre, copia y puntúa el
tablero sin saber nada de «filas» ni «columnas» — y ese mismo array es lo que viaja, copiado, por
cada rama del árbol.

**Tres en raya es el mínimo honesto.** El encargo original de este documento ya lo deja escrito:
*la complejidad de ajedrez es de contenido, no de técnica*. Cambiar de juego es cambiar
`tablero_movimientos` y `tablero_evaluar` —las dos únicas funciones que conocen las reglas—; el
motor de minimax y la poda de más abajo no cambian ni una línea. Para damas el cambio sería de
tamaño, no de forma: `tablero_movimientos` generaría saltos y capturas sobre un tablero de 32
casillas jugables en vez de 9, y `tablero_evaluar` contaría piezas y coronadas en vez de líneas.

```gml
/// scr_minimax_tres_en_raya
/// Tablero: array de 9 casillas (índice = fila * 3 + columna).
/// 0 = vacía · 1 = ficha de MAX · 2 = ficha de MIN.
function tres_en_raya_tablero_nuevo() {   // nombre específico: no colisiona con
    return array_create(9, 0);                // tablero_nuevo(_columnas,_filas) de 04 · 44 (deckbuilder)
}

/// Las 8 líneas que ganan la partida, precalculadas una sola vez.
global.__lineas_tres_en_raya = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],   // filas
    [0, 3, 6], [1, 4, 7], [2, 5, 8],   // columnas
    [0, 4, 8], [2, 4, 6]               // diagonales
];

/// @returns {Array<Real>} índices (0-8) de las casillas vacías: los movimientos legales.
function tablero_movimientos(_tablero) {
    var _movs = [];
    for (var _i = 0; _i < 9; _i++) {
        if (_tablero[_i] == 0) { array_push(_movs, _i); }
    }
    return _movs;
}

/// Copia el tablero y coloca UNA ficha — nunca muta el original: cada rama del
/// árbol necesita su propia copia, igual que estado_aplicar() en el
/// planificador GOAP de §10.
function tablero_jugar(_tablero, _casilla, _ficha) {
    var _nuevo = array_create(9);
    array_copy(_nuevo, 0, _tablero, 0, 9);
    _nuevo[_casilla] = _ficha;
    return _nuevo;
}

/// +10 si gana MAX, -10 si gana MIN, 0 en cualquier otro caso (incluida la
/// partida en curso). Con solo 9 casillas el árbol se explora HASTA EL FINAL
/// siempre, así que basta con «quién ganó»: una heurística más fina (líneas
/// abiertas, centro ocupado…) solo hace falta cuando el juego no se puede
/// resolver entero —damas, ajedrez— y hay que puntuar posiciones a medio
/// camino donde nadie ha ganado todavía.
function tablero_evaluar(_tablero) {
    var _lineas = global.__lineas_tres_en_raya;
    for (var _i = 0; _i < array_length(_lineas); _i++) {
        var _l = _lineas[_i];
        var _a = _tablero[_l[0]];
        if (_a != 0 && _a == _tablero[_l[1]] && _a == _tablero[_l[2]]) {
            return (_a == 1) ? 10 : -10;
        }
    }
    return 0;
}
```

**Minimax recursivo, con profundidad limitada.** MAX maximiza, MIN minimiza, y se alternan un
nivel del árbol por movimiento. `_profundidad` es el mismo tipo de tope que ya usa este documento
en otros sitios (el `_max_nodos` de §10, los `_veces` de un `Repetidor` en §4): sin un límite, un
juego más grande que el tres en raya no termina nunca de explorar.

```gml
/// @param {Array} _tablero      estado actual
/// @param {Real}  _profundidad  cuántos movimientos más mirar hacia delante
/// @param {Bool}  _maximizando  true si le toca decidir a MAX (nosotros)
/// @returns {Real} la puntuación del mejor resultado alcanzable desde aquí
function minimax(_tablero, _profundidad, _maximizando) {
    var _puntuacion = tablero_evaluar(_tablero);
    if (_puntuacion != 0) { return _puntuacion; }                     // alguien ya ganó

    var _movs = tablero_movimientos(_tablero);
    if (array_length(_movs) == 0 || _profundidad <= 0) { return 0; }  // empate o corte

    if (_maximizando) {
        var _mejor = -infinity;
        for (var _i = 0; _i < array_length(_movs); _i++) {
            var _hijo = tablero_jugar(_tablero, _movs[_i], 1);
            _mejor = max(_mejor, minimax(_hijo, _profundidad - 1, false));
        }
        return _mejor;
    } else {
        var _mejor = infinity;
        for (var _i = 0; _i < array_length(_movs); _i++) {
            var _hijo = tablero_jugar(_tablero, _movs[_i], 2);
            _mejor = min(_mejor, minimax(_hijo, _profundidad - 1, true));
        }
        return _mejor;
    }
}
```

**Poda alfa-beta: el mismo árbol, sin recorrerlo entero.** `minimax()` explora TODAS las ramas
aunque ya sepa que una es peor que otra que encontró antes — trabajo tirado. Alfa-beta lleva dos
números durante el recorrido: `_alfa` (lo mejor que MAX tiene garantizado hasta ahora en algún
sitio del árbol) y `_beta` (lo mejor que MIN tiene garantizado). En cuanto una rama demuestra que
va a ser peor de lo que el rival **ya puede forzar en otro sitio** (`_beta <= _alfa`), se corta:
no hace falta seguir mirando esa rama, porque un rival racional nunca va a dejar que la partida
llegue tan lejos.

**Cuánto reduce, medido de verdad.** Con `minimax()` y `minimax_alfa_beta()` de esta misma
sección, sobre un tablero vacío y explorando hasta el final (`_profundidad = 9`): minimax puro
recorre **549 946 nodos**; con la poda alfa-beta, **18 297** — una reducción del **96,7 %**, sin
cambiar el resultado (los dos concuerdan: la partida es un empate con juego perfecto, `0`).
Medido esta sesión traduciendo literalmente ambas funciones a Python y contando las llamadas
recursivas; el código de la comprobación no forma parte del documento pero el resultado sí es
una medición propia, no una cita de manual.

> ⚠️ La cifra que repite la literatura clásica de IA de juegos (el resultado se atribuye a Knuth
> y Moore, 1975) es que, con el **mejor orden de exploración posible**, alfa-beta reduce el
> factor de ramificación efectivo de `b` a `√b` — del orden de `b^(d/2)` nodos en vez de `b^d`.
> El 96,7 % medido arriba es de un caso concreto (tres en raya, orden de movimientos sin
> optimizar) y no pretende ser esa cota teórica. **No se ha podido verificar la cifra `√b` contra
> ninguna fuente primaria en esta sesión: no hubo acceso a red** (ni `curl` ni WebFetch
> resolvieron ningún host — ver Fuentes). Tómala como orientación de manual, no como medición
> propia.

```gml
/// Misma firma que minimax(), con _alfa y _beta añadidos. La llamada raíz
/// empieza con _alfa = -infinity, _beta = infinity: sin margen que podar todavía.
function minimax_alfa_beta(_tablero, _profundidad, _alfa, _beta, _maximizando) {
    var _puntuacion = tablero_evaluar(_tablero);
    if (_puntuacion != 0) { return _puntuacion; }

    var _movs = tablero_movimientos(_tablero);
    if (array_length(_movs) == 0 || _profundidad <= 0) { return 0; }

    if (_maximizando) {
        var _mejor = -infinity;
        for (var _i = 0; _i < array_length(_movs); _i++) {
            var _hijo = tablero_jugar(_tablero, _movs[_i], 1);
            _mejor = max(_mejor, minimax_alfa_beta(_hijo, _profundidad - 1, _alfa, _beta, false));
            _alfa  = max(_alfa, _mejor);
            if (_beta <= _alfa) { break; }          // MIN no va a dejar llegar aquí: podar
        }
        return _mejor;
    } else {
        var _mejor = infinity;
        for (var _i = 0; _i < array_length(_movs); _i++) {
            var _hijo = tablero_jugar(_tablero, _movs[_i], 2);
            _mejor = min(_mejor, minimax_alfa_beta(_hijo, _profundidad - 1, _alfa, _beta, true));
            _beta  = min(_beta, _mejor);
            if (_beta <= _alfa) { break; }          // MAX no va a dejar llegar aquí: podar
        }
        return _mejor;
    }
}
```

**Presupuesto: ni recorrer de golpe, ni confiar en que «no debería tardar».** Con 9 casillas el
árbol de tres en raya cabe entero en un frame sin que se note —como mucho 9! = 362 880
posiciones, bastantes menos con la poda de arriba—. Con un juego de verdad (damas, un Conecta 4
de 7 columnas) esto deja de ser cierto, y aparecen los dos mismos problemas que este documento ya
resolvió en otro contexto:

- **Tope de nodos explorados**, igual que el `_max_nodos = 400` del planificador GOAP en §10: un
  contador **compartido** entre todas las llamadas recursivas —un struct, porque los structs son
  referencias: todas las llamadas mutan el MISMO contador— que corta la búsqueda al llegar al
  límite y devuelve la evaluación heurística de donde se quedó, no la puntuación exacta.
- **Tope de tiempo real**, con la misma idea que trocea un generador procedural en
  [13 · 07 §14 — Generar sin congelar el frame](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/07%20-%20Generación%20procedural%20avanzada.md#14--generar-sin-congelar-el-frame).
  La diferencia es que un autómata celular se recorre celda a celda —un `for` plano que se puede
  parar y retomar en cualquier índice—, mientras que minimax es una recursión: no hay un punto
  intermedio limpio donde «pausar» sin reescribir el algoritmo entero como una pila explícita
  (viable, pero se sale del alcance «40 líneas honestas» de esta sección). La versión práctica
  que sí cabe aquí es **iterative deepening acotado por reloj**: probar profundidad 1, si sobra
  presupuesto probar profundidad 2, y así sucesivamente, quedándose siempre con el resultado de
  la última profundidad que llegó a TERMINAR. Como cada profundidad añadida multiplica el trabajo
  por el factor de ramificación, comprobar el reloj **solo entre profundidades** —no dentro de la
  recursión— ya evita pasarse mucho del presupuesto en la inmensa mayoría de los casos.

```gml
/// Contador de nodos compartido entre TODAS las llamadas recursivas de una
/// búsqueda: un struct, no una variable suelta, porque los structs son
/// referencias — cada llamada que muta _contador.nodos ve el mismo total.
function contador_nodos_nuevo() {
    return { nodos: 0 };
}

/// minimax_alfa_beta() con tope de nodos: al alcanzarlo, devuelve la
/// evaluación heurística del estado en el que se quedó (no la puntuación
/// exacta) en vez de seguir explorando.
function minimax_con_tope(_tablero, _profundidad, _alfa, _beta, _maximizando, _contador, _tope_nodos) {
    _contador.nodos++;
    if (_contador.nodos >= _tope_nodos) { return tablero_evaluar(_tablero); }

    var _puntuacion = tablero_evaluar(_tablero);
    if (_puntuacion != 0) { return _puntuacion; }

    var _movs = tablero_movimientos(_tablero);
    if (array_length(_movs) == 0 || _profundidad <= 0) { return 0; }

    if (_maximizando) {
        var _mejor = -infinity;
        for (var _i = 0; _i < array_length(_movs); _i++) {
            var _hijo = tablero_jugar(_tablero, _movs[_i], 1);
            _mejor = max(_mejor, minimax_con_tope(_hijo, _profundidad - 1, _alfa, _beta, false, _contador, _tope_nodos));
            _alfa  = max(_alfa, _mejor);
            if (_beta <= _alfa) { break; }
        }
        return _mejor;
    } else {
        var _mejor = infinity;
        for (var _i = 0; _i < array_length(_movs); _i++) {
            var _hijo = tablero_jugar(_tablero, _movs[_i], 2);
            _mejor = min(_mejor, minimax_con_tope(_hijo, _profundidad - 1, _alfa, _beta, true, _contador, _tope_nodos));
            _beta  = min(_beta, _mejor);
            if (_beta <= _alfa) { break; }
        }
        return _mejor;
    }
}

/// Elige el mejor movimiento con iterative deepening acotado por reloj:
/// prueba profundidad 1, 2, 3… y se queda con el resultado de la última que
/// dio tiempo a terminar dentro de _presupuesto_ms.
function mejor_movimiento(_tablero, _ficha, _presupuesto_ms = 50, _tope_nodos = 50000) {
    var _movs = tablero_movimientos(_tablero);
    if (array_length(_movs) == 0) { return -1; }

    var _elegido             = _movs[0];
    var _t0                  = get_timer();
    var _profundidad_maxima  = array_length(_movs);   // no hay más jugadas que casillas vacías
    var _le_toca_a_max_luego = (_ficha == 2);          // tras jugar _ficha, el turno pasa al otro

    for (var _profundidad = 1; _profundidad <= _profundidad_maxima; _profundidad++) {
        var _contador           = contador_nodos_nuevo();
        var _mejor_de_la_pasada = _movs[0];
        var _mejor_puntuacion   = (_ficha == 1) ? -infinity : infinity;

        for (var _i = 0; _i < array_length(_movs); _i++) {
            var _hijo = tablero_jugar(_tablero, _movs[_i], _ficha);
            var _p = minimax_con_tope(_hijo, _profundidad - 1, -infinity, infinity,
                                       _le_toca_a_max_luego, _contador, _tope_nodos);
            var _mejora = (_ficha == 1) ? (_p > _mejor_puntuacion) : (_p < _mejor_puntuacion);
            if (_mejora) { _mejor_puntuacion = _p; _mejor_de_la_pasada = _movs[_i]; }
        }

        if ((get_timer() - _t0) >= _presupuesto_ms * 1000) { break; }   // sin tiempo para ir más hondo
        _elegido = _mejor_de_la_pasada;
    }
    return _elegido;
}
```

```gml
/// Uso: obj_ia_tres_en_raya · el turno de la IA (ficha 2)
tablero = tres_en_raya_tablero_nuevo();
// ... el jugador coloca su ficha con tablero[_casilla] = 1 en algún punto anterior ...
var _casilla_ia = mejor_movimiento(tablero, 2, 50, 50000);   // 50 ms, 50 000 nodos como mucho
tablero[_casilla_ia] = 2;
```

> 💡 **Por qué esto no sustituye a nada de §1-§10.** Un enemigo de acción no tiene turnos: se
> mueve, dispara y decide en tiempo real mientras el jugador hace lo mismo a la vez — no hay
> información perfecta simétrica (el jugador no ve el árbol de decisión del enemigo) ni turnos
> que alternar. Y el deckbuilder de un jugador de
> [`04 · 44 §3`](./44%20-%20Bullet%20heaven%2C%20autobattler%20y%20deckbuilder.md#3--deckbuilder) tampoco es
> candidato: es de **un jugador contra la IA de los enemigos**, no dos agentes racionales
> turnándose sobre el mismo tablero, y encima la mano del jugador es información que el propio
> juego **oculta** — minimax exige que **ambos** bandos vean el estado completo. Un TCG
> competitivo con manos ocultas (Hearthstone, *Magic*) necesita técnicas que quedan fuera de este
> documento —*Perfect Information Monte Carlo*, *Counterfactual Regret Minimization*, o
> simplemente reglas/utility sobre lo que sí es visible—: minimax puro solo vale para información
> perfecta.

---

## 11 · Percepción: ver, oír, recordar y avisar

Una IA solo es tan buena como lo que sabe. Tres sentidos y una memoria bastan.

**Ver.** El **cono de visión** (¿está dentro del ángulo?) ya está resuelto con producto escalar
en [13 · 13 — Matemáticas aplicadas al juego §2.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md);
no lo repito. Lo que le falta es la **línea de visión** (`hay_vision_libre`, §5): el cono dice
dónde *puede* mirar, el rayo dice qué *llega* a ver.

**Oír** es más barato que ver y da mejor juego: no hace falta rayo, solo radio. Y encaja con
las señales de [16 · Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md):
quien hace ruido lo **anuncia**, y quien oye se apunta.

```gml
/// Quien hace ruido no sabe quién escucha.
function hacer_ruido(_x, _y, _radio, _tipo) {
    senal_emitir("ruido", { x: _x, y: _y, radio: _radio, tipo: _tipo });
}

/// obj_guardia · Create — apuntarse a los ruidos y a las alertas del grupo
senal_escuchar("ruido", function(_d) {
    if (point_distance(x, y, _d.x, _d.y) > _d.radio) { return; }
    pizarra.ultima_x = _d.x;
    pizarra.ultima_y = _d.y;
    pizarra.alerta   = max(pizarra.alerta, 1);          // sospecha, no combate
});

senal_escuchar("alerta_grupo", function(_d) {
    if (_d.quien == id)                        { return; }   // yo ya lo sé
    if (point_distance(x, y, _d.x, _d.y) > 500) { return; }  // demasiado lejos
    if (!hay_vision_libre(x, y, _d.x, _d.y))    { return; }  // un muro tapa el grito
    pizarra.ultima_x = _d.x;
    pizarra.ultima_y = _d.y;
    pizarra.alerta   = max(pizarra.alerta, 1);
});

/// Al disparar, al romper una caja, al correr por gravilla:
hacer_ruido(x, y, 260, "disparo");
/// Y al ver al jugador, el guardia lo grita:
senal_emitir("alerta_grupo", { x: obj_jugador.x, y: obj_jugador.y, quien: id });
```

**Recordar** el último sitio donde te vieron es lo que separa a un enemigo tonto de uno
creíble: ya no se planta en seco cuando rompes la línea de visión, va a mirar.

```gml
/// La rama de investigación, colocada ENTRE «te veo» y «patrullar».
new Secuencia([
    new Condicion(function(_p) { return (_p.alerta > 0 && _p.ultima_x >= 0); }, "¿sospecha?"),
    new Accion(function(_p) {
        var _tx = _p.ultima_x, _ty = _p.ultima_y;
        with (_p.duena) { mp_potential_step(_tx, _ty, velocidad * 0.8, false); }

        if (point_distance(_p.duena.x, _p.duena.y, _tx, _ty) < 12) {
            _p.ultima_x = -1;   _p.ultima_y = -1;   _p.alerta = 0;   // aquí no hay nadie
            return ArbolEstado.EXITO;
        }
        return ArbolEstado.EJECUTANDO;
    }, "investigar")
])
```

> 💡 **La alerta de grupo se propaga por la pizarra, no por el árbol.** El árbol no cambia: la
> rama «¿sospecha?» ya existía. Lo único que hace la señal es rellenar `ultima_x`/`ultima_y` de
> otro enemigo. Ese es el pago de tener la memoria fuera del árbol.

> 🔺 **Un radio de 500 px sin filtros no es «gritar», es telepatía.** El filtro de distancia y
> el `hay_vision_libre` del grito son lo que impide que un guardia al otro lado de un muro de
> hormigón se entere.

---

## 12 · Rendimiento: no todos los enemigos, no cada frame

Un árbol de 20 nodos por enemigo y 60 enemigos son 1 200 evaluaciones por frame. Tres medidas,
por orden de rentabilidad.

**1 · Tick escalonado.** Ningún enemigo necesita decidir 60 veces por segundo; diez es de
sobra, y así solo una fracción piensa en cada frame:

```gml
/// obj_enemigo · Create
grupo_ia = irandom(5);          // reparte los enemigos en 6 grupos

/// obj_enemigo · Step
if ((current_time div 100) mod 6 == grupo_ia) { arbol.tick(pizarra); }
mover_segun_decision();         // el movimiento sigue TODOS los frames
```

> 🔺 **Separa decidir de moverse.** Si escalonas el árbol y el movimiento vive dentro de las
> hojas, el enemigo irá a tirones. El patrón correcto: la hoja escribe *la intención* en la
> pizarra (`_p.mover_hacia_x`, `_p.mover_hacia_y`) y el Step la ejecuta cada frame.

**2 · Desactivar lo que no se ve.**

```gml
/// obj_control · Step — margen alrededor de la cámara
var _cx = camera_get_view_x(view_camera[0]),      _cy = camera_get_view_y(view_camera[0]);
var _cw = camera_get_view_width(view_camera[0]),  _ch = camera_get_view_height(view_camera[0]);
var _m  = 320;      // que sigan pensando un poco fuera de pantalla

instance_activate_region(  _cx - _m, _cy - _m, _cw + _m * 2, _ch + _m * 2, true);
instance_deactivate_region(_cx - _m, _cy - _m, _cw + _m * 2, _ch + _m * 2, false, true);
```

> ⚠️ **`instance_deactivate_region(left, top, width, height, inside, notme)` toma ancho y alto,
> no la esquina opuesta.** Es el fallo clásico. Y `inside = false` significa «desactiva lo que
> esté FUERA de la región», que es lo que quieres aquí.
>
> ⚠️ **Una instancia desactivada no existe para casi nada**: no la encuentran
> `instance_nearest`, `collision_line`, `with (obj_x)` ni sus Alarms. Si tu lógica global
> cuenta enemigos vivos, la desactivación te va a mentir. Para enemigos que deben seguir vivos
> pero baratos, es más seguro un tick escalonado muy lento (uno cada 2 segundos).

**3 · Presupuesto de rayos.** `collision_line` es lo más caro que hace una IA típica. La caché
por tick y el filtro de distancia de `ia_ve_al_jugador` (§5) son exactamente eso: **una sola
comprobación por tick, y ninguna si el jugador está lejos.** Mide antes de optimizar:
[01 · 15 — Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md).

---

## 13 · Qué hay ya escrito en GML

Cuatro implementaciones públicas de BT en GML. **Ninguna es grande** (entre 100 y 400 líneas), y
ese es justo el argumento para escribir el tuyo: el motor cabe en un archivo, y depurarlo es
infinitamente más fácil si lo entiendes entero.

*Metadatos consultados por la API de GitHub el 2026-09-06.*

| Repositorio | ⭐ | Licencia | Último cambio | Estado |
|---|---|---|---|---|
| [vitorestevam/GML-Behavior-Tree](https://github.com/vitorestevam/GML-Behavior-Tree) | 37 | ❌ **sin licencia** | 2024-03 | El más completo: `BTreeRoot`, blackboard, Sequence/Selector, decoradores Succeeder e Inverter, herencia `: BTreeLeaf() constructor`. Documenta los nodos en `nodes.md` y cita a Simpson |
| [Gizmo199/BehaviorTree](https://github.com/Gizmo199/BehaviorTree) | 14 | ❌ **sin licencia** | 2023-12 | ~130 líneas, API muy limpia (`bh_tree().selector(bh_sequence(...))`). Clonado en `GameMaker_Fuentes/librerias/Gizmo199__BehaviorTree` |
| [GamemakerCasts/behaviour-trees](https://github.com/GamemakerCasts/behaviour-trees) | 3 | ✅ **MIT** | 2025-06 | Solo `DecisionNode` y `ActionNode`. **No tiene estados de retorno**, así que no hay `EJECUTANDO`: es un árbol de decisión, no un BT |
| [DavidLeBlanc0/Behaviour_Trees_In_GML](https://github.com/DavidLeBlanc0/Behaviour_Trees_In_GML) | 2 | ❌ sin licencia | 2023-01 | Proyecto de demostración, no librería |

> ⚠️ **«Sin licencia» significa que NO puedes usarlo.** Sin licencia explícita el copyright por
> defecto reserva todos los derechos: puedes leerlo y aprender, no incorporarlo a tu juego. De
> las cuatro, solo la de GamemakerCasts (MIT) es utilizable tal cual — y es la más limitada.

> 🔺 **Aviso concreto sobre `Gizmo199/BehaviorTree`.** Leído su código
> (`scripts/__BehaviorTree/__BehaviorTree.gml`), su nodo de acción **siempre devuelve
> `Running`**: `evaluate = function(){ func(); return eBHStatus.Running; }`. Eso significa que
> **una secuencia nunca avanza al paso siguiente por sí sola**: usada como en su README, «ir a
> la puerta → abrirla → entrar» se queda en el primer paso para siempre. Tiene arreglo (que
> `func()` devuelva el estado y propagarlo), pero es el ejemplo perfecto de por qué conviene
> entender el motor antes de adoptarlo.

**Recomendación: escribe el tuyo** con el código de §2-§4. Son unas 120 líneas, no dependes de
nadie, y cuando el enemigo haga algo raro sabrás dónde mirar. Catálogo completo:
[11 · `_CATALOGO.md`](../11%20-%20Código%20descargado/_CATALOGO.md).

---

## Las trampas

| Trampa | Qué se ve en el juego | Arreglo |
|---|---|---|
| **La acción no devuelve `EJECUTANDO`** | El enemigo reinicia el paso cada frame: vibra en el sitio y nunca llega | Toda acción que dure más de un frame devuelve `EJECUTANDO` hasta terminar |
| **El árbol se reconstruye en el Step** | Caída de FPS y toda la memoria de los nodos perdida cada frame | El árbol se construye **una vez**, en el Create |
| **Un árbol compartido con estado dentro** | Con 2 enemigos va; con 20, se pisan el `indice` de las secuencias | Un árbol por enemigo (§3), o el recorrido en la pizarra |
| **La rama abandonada no se reinicia** | El guardia retoma la investigación por la mitad o repite el último paso | `hijos[activo].reiniciar()` al cambiar de rama el selector |
| **Condiciones caras en cada tick** | Un `collision_line` por condición × 3 condiciones × 60 enemigos × 60 fps | Filtro por distancia primero y caché por tick (§5, §12) |
| **Pizarra global compartida** | Todos persiguen la última posición que vio uno solo; alertas telepáticas | Una pizarra por instancia. Lo global son las **señales**, no la memoria |
| **Un árbol gigante para todo el juego** | 80 nodos que nadie entiende, donde un cambio rompe algo lejano | Varios árboles pequeños (combate, patrulla, huida) y un selector arriba |
| **Sin enfriamiento en el ataque** | El enemigo ataca 60 veces por segundo y te mata en un frame | `Enfriamiento` envolviendo la acción, en el árbol y no dentro de ella |
| **Utility sin inercia** | Oscilación: dispara, huye, dispara, huye | Compromiso mínimo, bonus a la acción en curso, o no decidir hasta terminar |
| **Puntuaciones sin normalizar** | Una consideración de 0-100 aplasta a otra de 0-1 y el resto no cuenta | Todo a 0-1, siempre. Es la regla nº 1 del capítulo de Graham |
| **Utility sin umbral mínimo** | Se ejecuta la mejor acción aunque puntúe 0.02: tonterías sin motivo | Umbral de `0.05`-`0.15`; por debajo, no hacer nada |
| **GOAP replanificado cada frame** | Congelaciones periódicas sin causa aparente | Planificar solo al cambiar de objetivo o al fallar el plan, con tope de nodos |
| **Minimax sin poda alfa-beta** | El árbol crece exponencial con la profundidad y un movimiento tarda segundos o congela el frame | Añadir `_alfa`/`_beta` (§10 bis) — mismo resultado, muchísimo menos árbol explorado |
| **Función de evaluación mal escalada** | La IA hace jugadas absurdas: sacrifica la partida por una ventaja que no vale lo que puntúa | Cada término de la heurística pesado a propósito, igual que la normalización 0-1 de utility (§8) |
| **`instance_deactivate_region` con x2/y2** | La mitad de los enemigos desaparecen, o ninguno se desactiva | Son `(left, top, width, height, inside, notme)` |

---

## Ver también

- [23 · IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) — **el movimiento**: seek, flee, arrive, wander, flocking, `mp_potential_step`. Este documento decide; aquel ejecuta
- [`scr_state_machine`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) — la FSM con structs, el escalón anterior al árbol
- [07 · 17 — SnowState](../07%20-%20Ecosistema/17%20-%20SnowState%20-%20máquinas%20de%20estado%20%28guía%20en%20español%29.md) — FSM con herencia de estados e historial
- [13 · Estrategia y gestión §5.5](./13%20-%20Estrategia%20y%20gestión.md) — IA por utilidad a nivel de facción, ya escrita: no la dupliques
- [16 · Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — el bus de eventos que usa §11 para ruidos y alertas
- [08 · Tower Defense](./08%20-%20Tower%20Defense.md) — A* con `mp_grid_path` y targeting de torres
- [`scr_grid_pathfinding`](../06%20-%20Assets%20y%20Scripts/scr_grid_pathfinding.gml) — A* de verdad, el algoritmo del que GOAP toma prestada la idea
- [01 · 04 — Structs y constructores](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) — `constructor`, `static`, `method`: el motor de este documento se apoya ahí
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — `json_parse` y sus trampas de 2026, para los árboles como datos
- [01 · 15 — Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md) — el Debug Overlay completo y cómo medir
- [13 · 13 — Matemáticas aplicadas al juego §2.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md) — el cono de visión, que aquí no se repite
- [02 · Top-Down / Twin-Stick](./02%20-%20Top-Down%20_%20Twin-Stick.md) — el género donde estos enemigos se lucen
- [13 · 07 §14 — Generar sin congelar el frame](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/07%20-%20Generación%20procedural%20avanzada.md#14--generar-sin-congelar-el-frame) — la técnica de trocear trabajo por presupuesto de milisegundos que [§10 bis](#10-bis--búsqueda-adversarial-minimax-y-poda-alfa-beta) adapta a minimax
- [04 · 44 §3 — Deckbuilder](./44%20-%20Bullet%20heaven%2C%20autobattler%20y%20deckbuilder.md#3--deckbuilder) — mano oculta e información imperfecta: por qué NO es candidato a minimax puro, a diferencia del tablero visible de [§10 bis](#10-bis--búsqueda-adversarial-minimax-y-poda-alfa-beta)

---

## Fuentes

Consultadas el **2026-09-06**.

**Abiertas y verificadas:**

- Chris Simpson, **«Behavior trees for AI: How they work»**, *Game Developer*, 18-07-2014 —
  <https://www.gamedeveloper.com/programming/behavior-trees-for-ai-how-they-work>. El artículo
  fundacional del tema fuera de la academia: Success/Failure/Running, nodos
  Composite/Decorator/Leaf, Selector y Sequence como OR y AND, decoradores (Inverter, Succeeder,
  Repeater, Repeat-until-fail), el contexto de datos compartido, y el consejo de guardar los
  nodos activos en vez de recorrer el árbol entero cada frame.
- David «Rez» Graham, **«An Introduction to Utility Theory»**, *Game AI Pro* vol. 1, cap. 9,
  CRC Press, 2013 —
  <http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter09_An_Introduction_to_Utility_Theory.pdf>
  (PDF gratuito, leído entero). De aquí: la normalización obligatoria a 0-1, las curvas (lineal,
  cuadrática, cuadrática girada, logística y lineal a trozos — «exactamente lo que usa *The
  Sims*»), la elección por máximo frente al azar ponderado sobre las N mejores, el *bucketing* /
  dual utility de Kevin Dill, y la sección 9.7 sobre **inercia** y oscilación.
- Jeff Orkin, **«Three States and a Plan: The A.I. of F.E.A.R.»**, *Game Developers Conference*
  2006, Monolith Productions / M.I.T. Media Lab —
  <https://www.gamedevs.org/uploads/three-states-plan-ai-of-fear.pdf> (PDF leído; espejo, ver
  abajo). De aquí: la FSM de tres estados (`Goto`, `Animate`, `UseSmartObject`), STRIPS,
  objetivos y acciones con precondiciones y efectos, el coste por acción que permite usar A*, la
  tabla A*-navegación / A*-planificación, «FSM procedimental vs planificación declarativa», y la
  replanificación como origen del comportamiento emergente (puerta → patada → ventana).
- **Índice de capítulos gratuitos de *Game AI Pro*** — <http://www.gameaipro.com/>.
- **GitHub API** — estrellas, licencia y última actividad de los cuatro repositorios del §13.
- **Manual oficial de GameMaker LTS 2026**, espejo local en `09 - Manual oficial/`:
  [`collision_line`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/collision_line.md),
  [`dbg_text`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Debugging/dbg_text.md),
  [`dbg_watch`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Debugging/dbg_watch.md),
  [`ref_create`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Variable_Functions/ref_create.md).
- **Código de `Gizmo199/BehaviorTree`**, leído en el clon local
  `GameMaker_Fuentes/librerias/Gizmo199__BehaviorTree/scripts/__BehaviorTree/__BehaviorTree.gml`.
- **Manual oficial**, para los símbolos nuevos de §10 bis:
  [`get_timer`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Date_And_Time/get_timer.md),
  [`array_copy`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Variable_Functions/array_copy.md).
- [13 · 07 §14 — Generar sin congelar el frame](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/07%20-%20Generación%20procedural%20avanzada.md#14--generar-sin-congelar-el-frame)
  — leído entero para adaptar la técnica de presupuesto por milisegundos a minimax en §10 bis;
  ya es fuente verificada de la propia biblioteca.

**Citadas pero NO abiertas** (URLs tomadas del índice de gameaipro.com, que sí se abrió):

- ⚠️ Alex Champandard y Philip Dunstan, «The Behavior Tree Starter Kit», *Game AI Pro* vol. 1,
  cap. 6 — <http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter06_The_Behavior_Tree_Starter_Kit.pdf>
- ⚠️ Bill Merrill, «Building Utility Decisions into Your Existing Behavior Tree», *Game AI Pro*
  vol. 1, cap. 10 — <http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter10_Building_Utility_Decisions_into_Your_Existing_Behavior_Tree.pdf>
  (la idea del §9 procede del título y del índice, no del texto completo).
- ⚠️ Anthony Francis, «Overcoming Pitfalls in Behavior Tree Design», *Game AI Pro* vol. 3, cap. 9
  — <http://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter09_Overcoming_Pitfalls_in_Behavior_Tree_Design.pdf>

**Lo que no se pudo verificar:**

- ⚠️ **El foro oficial no tiene ningún hilo de árboles de comportamiento en su sección
  *Tutorials*.** Se descargó el listado de
  <https://forum.gamemaker.io/index.php?forums/tutorials.15/> (HTTP 200, 2026-09-06) y no
  aparece ninguno: hay «Let's Build a Basic State Machine» y «How to Use Signals in GameMaker»,
  pero no hay BT. **La búsqueda del foro (`index.php?search/`) devuelve HTTP 403 sin sesión**,
  así que no puede descartarse que exista un hilo en otra sección. Es justo el hueco que este
  documento cubre.
- ⚠️ **La página personal de Jeff Orkin ya no está donde la citan todos.**
  `alumni.media.mit.edu/~jorkin/goap.html` devuelve **404**, y `jorkin.com` redirige con un
  **301 permanente a `bitpart.ai`**. Por eso el PDF de la GDC 2006 se cita desde el espejo de
  gamedevs.org; la autoría y el evento van impresos en la portada del propio documento, que se
  ha leído.
- ⚠️ **§10 bis (minimax y poda alfa-beta) no tiene fuente externa abierta.** Esta sesión no tuvo
  acceso a red en ningún momento: ni `curl` (los tres intentos con `-A "Mozilla/5.0"` a
  `en.wikipedia.org`, `www.chessprogramming.org` y `www.google.com` devolvieron código de salida
  28, «connection timed out», y hasta `1.1.1.1` sin resolver dominio) ni la herramienta WebFetch
  (`ECONNREFUSED` / `ENOTFOUND` contra los mismos dos primeros hosts) consiguieron abrir nada.
  Minimax se atribuye a Claude Shannon (1950, «Programming a Computer for Playing Chess») y la
  poda alfa-beta a John McCarthy, formalizada por Donald Knuth y Ronald W. Moore en «An Analysis
  of Alpha-Beta Pruning» (*Artificial Intelligence* 6, 1975); el tratamiento de referencia en
  videojuegos es el capítulo de búsqueda adversarial de Stuart Russell y Peter Norvig,
  *Artificial Intelligence: A Modern Approach*. Los tres son atribuciones de conocimiento
  general, **no verificadas contra el texto primario en esta sesión**: no se cita ninguna cifra,
  cita textual ni URL de esos trabajos que no se haya podido comprobar — la única cifra numérica
  que aparece en §10 bis (la reducción a `√b` con orden óptimo) va marcada con su propio ⚠️ en el
  cuerpo del texto, no aquí.
