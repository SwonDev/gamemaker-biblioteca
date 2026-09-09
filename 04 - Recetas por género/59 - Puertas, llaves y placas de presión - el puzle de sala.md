# 59 · Puertas, llaves y placas de presión — el puzle de sala

> **Dificultad:** media · **Se apoya en** [`13 · 17`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/17%20-%20Diseño%20de%20puzzles.md)
> (diseño de puzles y el Sokoban completo) y [`04 · 58`](./58%20-%20El%20nivel%20como%20mapa%20de%20texto%20-%20construir%20sin%20abrir%20el%20editor%20de%20salas.md)
> (el nivel en texto).

> **El hueco que cierra este documento.** `13 · 17 §3` da el Sokoban entero —estado inmutable,
> empuje, bloqueos de esquina, solver BFS, deshacer— y `04 · 37 §3.10` una versión más ligera.
> Lo que no estaba en ninguna parte es **la otra mitad de cualquier puzle de sala**: la placa de
> presión, la puerta que abre un circuito de placas, la llave y la cerradura, y el «reiniciar el
> nivel». Lo detectó un agente que construyó un juego de puzles completo con esta biblioteca y
> tuvo que decidirlo todo por su cuenta:
>
> ```console
> $ python3 "$BIB/_indice/buscar.py" --todo "placa de presion"
> Sin resultados para «placa de presion» en ninguna de las cuatro fuentes.
> ```
>
> ([`r15-prueba-puzles.md` §2.9](../_indice/auditorias/r15-prueba-puzles.md))

---

## 1 · El error que hay que no cometer: conectar la placa a la puerta

Lo primero que sale es esto:

```gml
// obj_placa · Step        ❌ NO
if (place_meeting(x, y, obj_caja)) obj_puerta.abierta = true;
```

Y funciona… hasta el segundo puzle. Se rompe en cuanto hay **dos** puertas (`obj_puerta` como
nombre de objeto apunta a *una* instancia arbitraria), en cuanto hay **dos placas para una
puerta** (la primera que se suelte la cierra), y en cuanto quieres que una placa haga otra cosa
—un puente, una plataforma, apagar unos pinchos—.

La estructura que sí escala tiene tres piezas y es siempre la misma:

```
EMISOR  ──publica su estado en──▶  CANAL  ──lo lee──▶  RECEPTOR
placa                              "puerta_norte"      puerta
palanca                            "puente_1"          puente
cerradura                          "sala_final"        pinchos
```

**El emisor no sabe qué abre. El receptor no sabe quién lo abre.** Los une una cadena de texto.
Es el mismo desacoplamiento que [`04 · 16`](./16%20-%20Señales%20y%20desacoplamiento.md) aplica
a los eventos del juego, en pequeño: aquí el «canal» es lo que allí es una señal.

---

## 2 · El canal: un struct global, y por qué no un booleano

```gml
/// @func circuitos_reiniciar()
/// @desc Llámalo al construir el nivel, ANTES de crear las instancias. Si no, el
///       canal conserva el estado del intento anterior y la puerta empieza abierta.
function circuitos_reiniciar()
{
    global.circuitos = {};
}

/// @func circuito_fijar(_canal, _emisor, _activo)
/// @desc Un emisor publica su estado. La clave es el emisor, no un contador: si
///       fuera un contador, un emisor que publique dos veces «pulsada» lo dejaría
///       en 2 y la puerta no se cerraría nunca.
/// @param {String} _canal
/// @param {Id.Instance} _emisor
/// @param {Bool} _activo
function circuito_fijar(_canal, _emisor, _activo)
{
    if (!struct_exists(global.circuitos, _canal))
    {
        struct_set(global.circuitos, _canal, {});
    }
    struct_set(global.circuitos[$ _canal], string(_emisor), _activo);
}

/// @func circuito_cuenta(_canal)
/// @desc Devuelve [activos, totales] de ese canal.
/// @return {Array<Real>}
function circuito_cuenta(_canal)
{
    if (!struct_exists(global.circuitos, _canal)) return [0, 0];

    var _c = global.circuitos[$ _canal];
    var _claves = struct_get_names(_c);
    var _activos = 0;
    for (var _i = 0; _i < array_length(_claves); _i++)
    {
        if (struct_get(_c, _claves[_i])) _activos++;
    }
    return [_activos, array_length(_claves)];
}

/// @func circuito_abierto(_canal, _modo, _cuantos)
/// @desc ¿Se cumple la condición del canal?
/// @param {String} _canal
/// @param {String} _modo   "todos" · "alguno" · "exactamente"
/// @param {Real}   _cuantos  solo para "exactamente"
/// @return {Bool}
function circuito_abierto(_canal, _modo = "todos", _cuantos = 1)
{
    var _n = circuito_cuenta(_canal);
    var _activos = _n[0];
    var _totales = _n[1];

    // Un canal sin un solo emisor NO está abierto. Si devolviera true, una puerta
    // con el nombre de canal mal escrito se abriría sola y parecería un acierto.
    if (_totales == 0) return false;

    switch (_modo)
    {
        case "alguno":      return (_activos > 0);
        case "exactamente": return (_activos == _cuantos);
        default:            return (_activos == _totales);   // "todos"
    }
}
```

> 🔴 **El canal sin emisores devuelve `false`, y esto no es un detalle.** Escribir
> `canal = "puerta_norte"` en la placa y `canal = "puerta_nore"` en la puerta es el error de
> dedo más probable de todo el sistema. Si un canal vacío contara como «condición cumplida», la
> puerta se abriría sola desde el primer frame y **parecería que el puzle funciona**. Con
> `false`, la puerta no abre nunca y lo notas en el primer intento.
>
> Mejor todavía: valida los canales al construir el nivel — §6.

---

## 3 · La placa de presión

```gml
// obj_placa · Create
canal   = "puerta_norte";
pulsada = false;
fija    = false;             // true = una vez pulsada, se queda pulsada
circuito_fijar(canal, id, false);
```

```gml
// obj_placa · Step
if (fija && pulsada) exit;   // ya cumplió su papel

// Lo que pesa: una caja O el jugador. Que acepte las dos cosas es lo que hace
// interesante el puzle — si solo aceptara cajas, sería contar cajas.
var _peso  = (instance_place(x, y, obj_caja) != noone)
          || (instance_place(x, y, obj_jugador) != noone);

if (_peso != pulsada)
{
    pulsada = _peso;
    circuito_fijar(canal, id, pulsada);
    audio_play_sound(pulsada ? snd_placa_baja : snd_placa_sube, 1, false);
    image_index = pulsada;   // sub-imagen 0 suelta, 1 pulsada
}
```

> ⚠️ **Se evalúa en el Step, no en el evento Collision.** Con el evento de colisión tienes el
> «pulsar» pero no el «soltar»: nadie te avisa cuando la caja deja de estar encima. La versión
> que sale primero —`Collision with obj_caja: pulsada = true`— deja la placa pulsada para
> siempre y el puzle se resuelve empujando la caja **por encima** de la placa sin dejarla ahí.
>
> Y si la caja se **destruye** encima de la placa (cae a un pozo, la quema algo), el Step se
> entera solo. El evento de colisión, no.

**Tres variantes que salen gratis desde aquí:**

| Quieres | Cómo |
|---|---|
| Placa que se queda pulsada | `fija = true` |
| Placa que solo acepta cajas | quita el `instance_place(..., obj_jugador)` |
| Placa con temporizador (se suelta a los 3 s) | un `Cooldown` de [`06 · scr_tiempo.gml`](../06%20-%20Assets%20y%20Scripts/scr_tiempo.gml), y publica `false` al vencer |

---

## 4 · La puerta: abrir es dejar de estorbar, no dejar de dibujarse

```gml
// obj_puerta · Create
canal   = "puerta_norte";
modo    = "todos";
cuantos = 1;
abierta = false;
```

```gml
// obj_puerta · Step
var _ahora = circuito_abierto(canal, modo, cuantos);
if (_ahora == abierta) exit;

abierta = _ahora;
image_index = abierta;
audio_play_sound(abierta ? snd_puerta_abre : snd_puerta_cierra, 1, false);
```

Y la colisión, que es donde se cuela el fallo:

```gml
// obj_jugador · el movimiento consulta la puerta, no la destruye
function celda_bloqueada(_gx, _gy)
{
    var _inst = instance_position(_gx * CELDA + CELDA / 2,
                                  _gy * CELDA + CELDA / 2, obj_puerta);
    if (_inst != noone && !_inst.abierta) return true;
    return place_meeting(_gx * CELDA, _gy * CELDA, obj_muro);
}
```

> 🔴 **No destruyas la puerta al abrirla.** Es lo cómodo —`instance_destroy()` y ya no
> colisiona— y cierra tres caminos a la vez: no se puede **volver a cerrar** cuando la caja
> salga de la placa, no se puede **deshacer** el movimiento que la abrió
> ([`13 · 17 §3.6`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/17%20-%20Diseño%20de%20puzzles.md)),
> y no se puede **reiniciar el nivel** sin reconstruirlo entero. Una puerta abierta es una
> puerta con `abierta = true`, nada más.
>
> Si el sprite abierto tiene que dejar pasar visualmente, eso es `image_index`, no
> `instance_destroy`.

---

## 5 · Llave y cerradura: se guardan por clave estable, no por índice

Una llave es un emisor que publica **una sola vez** y no vuelve a cambiar. La tentación es
guardar «llaves recogidas: 3» y comparar números; eso convierte dos llaves distintas en la
misma, y una partida guardada abre la puerta equivocada.

```gml
// obj_llave · Create — la clave viene del mapa (04 · 58 §5), no del orden de creación
// nivel_clave la pone `nivel_mapa_construir()` de 06 · scr_nivel_mapa.gml
if (llave_tienes(nivel_clave)) instance_destroy();
```

```gml
/// @func llaves_reiniciar()
function llaves_reiniciar()
{
    global.llaves = {};
}

/// @func llave_coger(_clave)
/// @param {String} _clave  la clave estable de la casilla: "n1_x34_y12"
function llave_coger(_clave)
{
    struct_set(global.llaves, _clave, true);
}

/// @func llave_tienes(_clave)
/// @return {Bool}
function llave_tienes(_clave)
{
    return struct_exists(global.llaves, _clave);
}

/// @func llave_cuantas()
/// @return {Real}
function llave_cuantas()
{
    return array_length(struct_get_names(global.llaves));
}
```

Y la cerradura consume una llave cualquiera o una concreta, según el diseño:

```gml
// obj_cerradura · el jugador la toca
if (llave_cuantas() > 0)
{
    // Cualquiera vale: se gasta la primera. Para una llave CONCRETA, guarda en la
    // cerradura la clave que exige y usa llave_tienes(esa_clave).
    var _nombres = struct_get_names(global.llaves);
    struct_remove(global.llaves, _nombres[0]);
    circuito_fijar(canal, id, true);
}
```

> 💡 **Por qué la clave estable y no un índice de recorrido**: insertar una llave en mitad del
> mapa desplaza el índice de todas las siguientes, y una partida guardada creerá que recogió
> otras. Está contado en [`04 · 58 §5`](./58%20-%20El%20nivel%20como%20mapa%20de%20texto%20-%20construir%20sin%20abrir%20el%20editor%20de%20salas.md).

---

## 6 · Validar los canales al construir, no al jugar

Un canal mal escrito no da error: da una puerta que no abre nunca, y te lo cuenta un jugador.
Se comprueba en cuanto el nivel está montado, con la misma disciplina que
[`04 · 58 §3`](./58%20-%20El%20nivel%20como%20mapa%20de%20texto%20-%20construir%20sin%20abrir%20el%20editor%20de%20salas.md):

```gml
/// @func circuitos_validar()
/// @desc Un receptor cuyo canal no tiene emisores, o un emisor cuyo canal no
///       escucha nadie, son los dos síntomas de un nombre mal escrito.
/// @return {Array<String>}  vacío si está todo bien
function circuitos_validar()
{
    var _problemas = [];

    with (obj_puerta)
    {
        if (!struct_exists(global.circuitos, canal))
        {
            array_push(_problemas, "la puerta en " + string(x) + "," + string(y)
                + " escucha el canal «" + canal + "», que no tiene ni un emisor");
        }
    }

    var _canales = struct_get_names(global.circuitos);
    for (var _i = 0; _i < array_length(_canales); _i++)
    {
        var _c = _canales[_i];
        var _escuchas = 0;
        with (obj_puerta) { if (canal == _c) _escuchas++; }
        if (_escuchas == 0)
        {
            array_push(_problemas, "el canal «" + _c + "» tiene emisores y no lo escucha nadie");
        }
    }

    return _problemas;
}
```

Y en el Create del gestor de nivel, después de construir:

```gml
var _p = circuitos_validar();
for (var _i = 0; _i < array_length(_p); _i++) show_debug_message("CIRCUITO: " + _p[_i]);
```

---

## 7 · Reiniciar el nivel

Es la acción que más se pulsa en un juego de puzles y la que más veces está mal escrita.

```gml
/// @func nivel_reiniciar()
/// @desc Reconstruye el nivel desde su mapa de texto. NO usa room_restart().
function nivel_reiniciar()
{
    // 1 · Fuera todo lo que el nivel creó. El gestor NO se destruye a sí mismo.
    with (obj_caja)      instance_destroy();
    with (obj_placa)     instance_destroy();
    with (obj_puerta)    instance_destroy();
    with (obj_llave)     instance_destroy();
    with (obj_jugador)   instance_destroy();

    // 2 · Y todo el estado que vivía fuera de las instancias. Sin esto, el nivel
    //     se reconstruye con las puertas ya abiertas del intento anterior.
    circuitos_reiniciar();
    llaves_reiniciar();
    global.pasos = 0;
    global.deshacer = [];

    // 3 · Reconstruir.
    var _r = nivel_mapa_construir(mi_mapa(global.nivel_actual), mi_leyenda(),
                                  { nombre: "n" + string(global.nivel_actual) });
    instance_create_layer(_r.aparicion_x, _r.aparicion_y, "Instances", obj_jugador);
}
```

> 🔴 **`room_restart()` parece la respuesta y trae dos problemas.** Reinicia la sala entera
> —incluido el gestor, el HUD y cualquier cosa persistente que hubieras colocado— y **no toca
> nada de lo que vive en `global`**: los circuitos y las llaves sobreviven al reinicio, así que
> el nivel vuelve a empezar con las puertas abiertas. El paso 2 de arriba es el que de verdad
> reinicia; el 1 y el 3 solo mueven instancias.

> 🔴 **Y si el botón de reiniciar está en el menú de pausa, cuidado con la guarda.** Durante la
> pausa, `instance_deactivate_all()` ya ha corrido y **`instance_exists()` devuelve `false`
> sobre todo lo desactivado**: un `if (instance_exists(global.gestor)) nivel_reiniciar();` no
> hace absolutamente nada, sin error. Reactiva primero, comprueba después —
> [`04 · 41 §3.1.1`](./41%20-%20Transiciones,%20carga%20y%20pausa.md).

---

## 8 · Checklist

- [ ] Ninguna placa nombra a `obj_puerta` directamente: publica en un canal
- [ ] Las placas se evalúan en el **Step**, no en el evento Collision (si no, no hay «soltar»)
- [ ] Un canal sin emisores devuelve `false`, y hay una validación que lo dice al construir
- [ ] Abrir una puerta es `abierta = true`, nunca `instance_destroy()`
- [ ] Las llaves se guardan por **clave estable** de la casilla, no por índice ni por contador
- [ ] `circuitos_reiniciar()` y `llaves_reiniciar()` se llaman **antes** de construir el nivel
- [ ] Reiniciar el nivel limpia también el estado de `global`, no solo las instancias
- [ ] El «reiniciar» del menú de pausa no empieza con una guarda `instance_exists`
- [ ] Cada puzle tiene solución comprobada por una búsqueda, no por intuición ([`13 · 17 §3.3`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/17%20-%20Diseño%20de%20puzzles.md))

---

## Ver también

- [13 · 17 — Diseño de puzles](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/17%20-%20Diseño%20de%20puzzles.md) — el Sokoban completo, el deshacer y el solver que demuestra que hay solución
- [58 · El nivel como mapa de texto](./58%20-%20El%20nivel%20como%20mapa%20de%20texto%20-%20construir%20sin%20abrir%20el%20editor%20de%20salas.md) — dónde salen `nivel_clave` y la construcción del nivel
- [41 · Transiciones, carga y pausa](./41%20-%20Transiciones,%20carga%20y%20pausa.md) — la trampa de `instance_exists` durante la pausa
- [16 · Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — el mismo desacoplamiento, a escala de juego
- [07 · Puzzle y Match-3](./07%20-%20Puzzle%20y%20Match-3.md) — el otro puzle, el de rejilla y combinaciones
