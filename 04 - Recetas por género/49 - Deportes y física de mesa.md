# 49 · Deportes y física de mesa

> **Dificultad:** media-alta · Dos géneros que no tenían ni una línea en esta biblioteca
> (verificado: 0 resultados de «deporte», «fútbol», «golf»; «billar» solo aparecía en un
> comentario de [`04 · 22`](./22%20-%20Físicas%20con%20Box2D.md)). Este documento cubre dos
> mitades independientes que pueden leerse por separado.
>
> **(A) Deportes de equipo** — el balón como entidad con estado, pase con anticipación, tiro
> con efecto, IA por roles y formaciones, reglas y árbitro, reloj y marcador.
>
> **(B) Física de mesa** — billar, pinball y minigolf, cada uno resuelto **a mano o con
> Box2D** según cuál compensa para ese juego concreto.
>
> **No repite**: el eje Z falso completo (saltos, sombra, proyectiles con arco), que es
> [`04 · 46`](./46%20-%20Eje%20Z%20falso%20-%20altura%2C%20sombras%20y%20profundidad%20en%20un%20juego%202D.md)
> — aquí se **usa** para el pase alto y el tiro con arco; la configuración del mundo físico,
> las fixtures y los joints de Box2D, que es
> [`04 · 22`](./22%20-%20Físicas%20con%20Box2D.md) — aquí se **usa** para el pinball; la
> colisión y la fricción a mano (Euler semi-implícito, `delta_time`, rebote con restitución
> contra una pared), que es
> [`13 · 08`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/08%20-%20Físicas%20a%20mano%20y%20fluidos.md)
> — aquí se **extiende** con la pieza que faltaba: la colisión elástica **entre dos círculos
> que se mueven los dos**, no un rebote contra una superficie fija. Tampoco repite `GestorFichas`
> ([`04 · 33`](./33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md))
> ni `Arrive`
> ([`04 · 23`](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) §2), que la IA por
> roles usa para moverse a su posición sin pasarse.

---

# Parte A · Deportes de equipo

## A.1 · Visión general y arquitectura

Un deporte de equipo (fútbol, baloncesto, balonmano, hockey) es, en el fondo, un top-down
(`04 · 02`) con una pelota que tiene reglas propias y veintidós entidades que deciden solas
adónde correr. Lo que lo distingue de una arena de combate corriente:

1. **El balón no es un arma, es un recurso que se posee.** Se puede tener, perder, robar y
   pasar — y quien no lo tiene sigue jugando (se desmarca, cubre zona, presiona).
2. **Las reglas son un árbitro externo al jugador**, no una consecuencia física: un balón que
   sale del campo no rebota solo, alguien decide que es saque de banda.
3. **El reloj manda sobre la partida entera**, no solo sobre una animación: el marcador y el
   tiempo son el estado más importante del juego, por encima de la posición de cualquier
   entidad.

```
obj_partido_control      (árbitro + reloj + marcador — uno por partida, §A.6-A.7)
obj_balon                (máquina de estados: libre / poseído / en vuelo — §A.2)
obj_jugador_equipo       (padre de los 22; rol + formación — §A.5)
├── obj_jugador_humano    (uno o dos, con input)
└── obj_jugador_ia        (el resto, con GestorFichas de 04 · 33 para el marcaje — §A.5.4)
obj_porteria             (dos, una por equipo — detecta gol)
obj_campo_zona           (rectángulo invisible: el terreno de juego, para fuera de banda)
```

| Sistema | Qué resuelve aquí | Reutiliza de |
|---|---|---|
| Altura del balón (pase alto, tiro con arco) | — | `04 · 46` §3.9 (`proyectil_arco_lanzar`, adaptado) |
| Movimiento hacia la posición de formación sin pasarse | — | `04 · 23` §2 (`Arrive`) |
| Asignar quién marca a quién sin que se amontonen todos | — | `04 · 33` §3 (`GestorFichas`), con radios de campo abierto |
| Colisión balón-jugador para robar/interceptar | — | `01 · 08` (`place_meeting`/`instance_place`) |
| El resto: estado del balón, pase, tiro, formación, árbitro, reloj | Sistema nuevo — no existía nada parecido en la biblioteca | Este documento |

## A.2 · El balón como entidad con estado

El balón no es un adorno que sigue al jugador: es su propia instancia, con su propia física, y
en todo momento está en uno de tres estados.

```gml
// ---------------------------------------------------------------------------
// scr_deporte_config
// ---------------------------------------------------------------------------
enum BalonEstado { libre, poseido, en_vuelo }

#macro EQUIPO_LOCAL       0
#macro EQUIPO_VISITANTE   1

#macro GRAV_BALON        0.5     // gravedad del arco del balón (04 · 46 §3.9, macro propio:
                                  // el balón no hereda de obj_entidad_saltable)
#macro BALON_FRICCION    0.94    // por paso a 60 fps — decae con power(), no con resta (13 · 08 §1.3)
#macro BALON_RADIO_ROBO  14      // distancia para robar/recoger un balón libre
#macro BALON_COOLDOWN_TOQUE 8    // frames de inmunidad tras un pase: quien lo tocó no lo "recoge" solo

// Valores de ejemplo para el resto de la Parte A — ajústalos jugando; ninguno
// sale de una fórmula, son parámetros de diseño.
#macro VELOCIDAD_MAX                  3.2    // píxeles/paso al correr
#macro RADIO_FRENADO                  40     // 04 · 23 §2 (llegar_a): distancia a la que empieza a frenar
#macro RADIO_ENTRADA                  16     // distancia para intentar robar (§A.2.1)
#macro DISTANCIA_CUBIERTO             50     // a partir de aquí, un rival "cubre" y toca desmarcarse (§A.5.5)
#macro PROB_ROBO_FRENTE               0.35
#macro PROB_ROBO_ESPALDA              0.08
#macro PROB_FALTA_EN_ENTRADA_FALLIDA  0.4
```

```gml
/// obj_balon — Create
estado          = BalonEstado.libre;
poseedor        = noone;
vel_x           = 0;
vel_y           = 0;
z               = 0;        // 04 · 46 — altura sobre el césped
zvel            = 0;
efecto_curva    = 0;        // grados/paso de curvatura lateral mientras está en vuelo (§A.4)
ultimo_toque    = noone;    // quién lo tocó por última vez — para saques de banda/esquina (§A.6)
equipo_ultimo_toque = -1;
cooldown_toque  = 0;

global.balon = id;   // singleton: el resto del documento lo referencia como global.balon
```

```gml
/// obj_balon — Step
if (cooldown_toque > 0) cooldown_toque -= 1;

switch (estado)
{
    case BalonEstado.libre:
        x += vel_x;
        y += vel_y;
        vel_x *= BALON_FRICCION;
        vel_y *= BALON_FRICCION;
        if (point_distance(0, 0, vel_x, vel_y) < 0.05) { vel_x = 0; vel_y = 0; }

        // ¿alguien lo recoge? El más cercano dentro del radio, salvo que sea
        // el que acaba de tocarlo (cooldown_toque evita "robártelo a ti mismo"
        // nada más pasarlo).
        if (cooldown_toque <= 0)
        {
            var _cand = instance_nearest(x, y, obj_jugador_equipo);
            if (_cand != noone && point_distance(x, y, _cand.x, _cand.y) < BALON_RADIO_ROBO)
            {
                balon_asignar_posesion(id, _cand);
            }
        }
        break;

    case BalonEstado.poseido:
        // Sigue al poseedor con un pequeño adelanto en su dirección de carrera:
        // "controlar el balón" no es teletransportarlo al centro del jugador.
        var _dir = point_direction(0, 0, poseedor.vel_x, poseedor.vel_y);
        var _dist = (point_distance(0, 0, poseedor.vel_x, poseedor.vel_y) > 0.1) ? 10 : 6;
        x = poseedor.x + lengthdir_x(_dist, _dir);
        y = poseedor.y + lengthdir_y(_dist, _dir);
        break;

    case BalonEstado.en_vuelo:
        // Curva lateral (efecto): rota el vector de velocidad, no le suma una
        // fuerza aparte — así la rapidez no cambia, solo la dirección (§A.4).
        if (efecto_curva != 0)
        {
            var _rapidez  = point_distance(0, 0, vel_x, vel_y);
            var _dir_vuelo = point_direction(0, 0, vel_x, vel_y) + efecto_curva;
            vel_x = lengthdir_x(_rapidez, _dir_vuelo);
            vel_y = lengthdir_y(_rapidez, _dir_vuelo);
            efecto_curva *= 0.97;   // el efecto se agota: un tiro no curva eternamente
        }

        x += vel_x;
        y += vel_y;
        zvel -= GRAV_BALON;
        z    += zvel;

        if (z <= 0)
        {
            z = 0;
            estado = BalonEstado.libre;   // aterriza: vuelve a rodar libre, con la vel_x/vel_y que traía
        }
        break;
}
```

```gml
/// @func balon_asignar_posesion(_balon, _jugador)
/// @desc El balón pasa a estar poseído por `_jugador`. Común a "recogerlo del
///       suelo" y a "robárselo a otro" (§A.2.1): ambos casos llaman a esto.
function balon_asignar_posesion(_balon, _jugador)
{
    with (_balon)
    {
        estado    = BalonEstado.poseido;
        poseedor  = _jugador;
        vel_x     = 0;
        vel_y     = 0;
        z         = 0;      // controlar el balón lo pega al suelo, venga de donde venga (§A.2)
        zvel      = 0;
        ultimo_toque         = _jugador;
        equipo_ultimo_toque  = _jugador.equipo;
    }
    _jugador.con_balon = true;
}

/// @func balon_liberar(_balon)
/// @desc El balón deja de estar poseído (perderlo, o el primer instante de un
///       pase/tiro antes de fijar su nueva velocidad).
function balon_liberar(_balon)
{
    if (_balon.poseedor != noone && instance_exists(_balon.poseedor))
    {
        _balon.poseedor.con_balon = false;
    }
    _balon.estado    = BalonEstado.libre;
    _balon.poseedor  = noone;
}
```

### A.2.1 · Robar el balón

Robar es, en el fondo, "otro jugador entra en el radio de posesión antes de que el poseedor
reaccione" — no hace falta un sistema de combate (`04 · 30` es para golpes, no para esto):

```gml
/// obj_jugador_equipo — Step, para cualquiera que NO tenga el balón
if (!con_balon && instance_exists(global.balon) && global.balon.estado == BalonEstado.poseido
    && global.balon.poseedor.equipo != equipo
    && point_distance(x, y, global.balon.x, global.balon.y) < RADIO_ENTRADA)
{
    // Probabilidad de robo: más alta si el defensor llega de frente al
    // movimiento del rival (una entrada limpia), más baja si llega de espaldas
    // (habría sido falta en la vida real — aquí, simplemente falla más).
    var _de_frente = dot_product(lengthdir_x(1, point_direction(x, y, global.balon.x, global.balon.y)),
                                  lengthdir_y(1, point_direction(x, y, global.balon.x, global.balon.y)),
                                  lengthdir_x(1, image_angle), lengthdir_y(1, image_angle)) > 0;
    var _prob = _de_frente ? PROB_ROBO_FRENTE : PROB_ROBO_ESPALDA;

    if (random(1) < _prob)
    {
        balon_asignar_posesion(global.balon, id);
    }
    else
    {
        // entrada fallida: falta si el juego decide que sí (§A.6.3) — aquí solo
        // se dispara el gancho, la decisión de pitar es del árbitro
        arbitro_evaluar_entrada(id, global.balon.poseedor);
    }
}
```

> ⚠️ `PROB_ROBO_FRENTE`/`PROB_ROBO_ESPALDA` son parámetros de diseño, no física: ajústalos
> jugando. Un valor típico de partida: 0,35 de frente, 0,08 de espaldas — así una entrada
> desesperada por detrás casi nunca sale bien, que es justo lo que se quiere transmitir.

## A.3 · Pase

### A.3.1 · Pase raso, con anticipación

Pasar "al sitio donde está" el compañero es lo que delata a una IA de fútbol mala: el balón
llega tarde porque el receptor ya se ha movido. La corrección es **liderar al receptor**:
apuntar no a su posición actual, sino a donde estará cuando el balón llegue — que depende de
la propia velocidad del pase, así que hace falta resolverlo con una iteración corta.

```gml
/// @func balon_punto_de_encuentro(_origen_x, _origen_y, _receptor, _velocidad_pase)
/// @desc Dónde debe apuntar el pase para que el balón y el receptor lleguen al
///       mismo punto a la vez, asumiendo que el receptor mantiene su velocidad
///       actual. Tres iteraciones bastan: cada una refina la distancia y por
///       tanto el tiempo de vuelo, y converge rápido porque la corrección es
///       pequeña comparada con la distancia total.
/// @returns {Struct} { x, y }
function balon_punto_de_encuentro(_origen_x, _origen_y, _receptor, _velocidad_pase)
{
    var _px = _receptor.x;
    var _py = _receptor.y;

    repeat (3)
    {
        var _dist    = point_distance(_origen_x, _origen_y, _px, _py);
        var _tiempo  = _dist / max(_velocidad_pase, 0.01);
        _px = _receptor.x + _receptor.vel_x * _tiempo;
        _py = _receptor.y + _receptor.vel_y * _tiempo;
    }
    return { x: _px, y: _py };
}
```

```gml
/// @func balon_pasar(_balon, _origen_x, _origen_y, _receptor, _velocidad_pase)
/// @desc Pase raso (z = 0 todo el trayecto): la variante "alta" es §A.3.2.
function balon_pasar(_balon, _origen_x, _origen_y, _receptor, _velocidad_pase)
{
    var _obj = balon_punto_de_encuentro(_origen_x, _origen_y, _receptor, _velocidad_pase);
    var _dir = point_direction(_origen_x, _origen_y, _obj.x, _obj.y);

    balon_liberar(_balon);
    with (_balon)
    {
        vel_x = lengthdir_x(_velocidad_pase, _dir);
        vel_y = lengthdir_y(_velocidad_pase, _dir);
        z      = 0;      // raso de verdad: sin z, no solo sin arco explícito
        zvel   = 0;
        estado = BalonEstado.libre;
        cooldown_toque = BALON_COOLDOWN_TOQUE;
        ultimo_toque         = other.id;      // other = quien pasa, dentro del with de arriba
        equipo_ultimo_toque  = other.equipo;
    }
}
```

> 💡 **Sin anticipación, el pase directo funciona igual** — `point_direction(_origen_x,
> _origen_y, _receptor.x, _receptor.y)` sin más — y para pases cortos entre jugadores casi
> parados la diferencia no se nota. La anticipación importa en pases largos a un compañero que
> corre, que es exactamente donde una IA sin ella se ve torpe.

### A.3.2 · Pase alto

Un pase alto (por encima de un defensor, un centro al área) es el mismo cálculo de anticipación
para la dirección horizontal, con el arco vertical de `04 · 46` §3.9 por encima — **no se
repite esa física aquí**, solo se llama:

```gml
/// @func balon_pasar_alto(_balon, _origen_x, _origen_y, _receptor, _distancia, _altura_max)
function balon_pasar_alto(_balon, _origen_x, _origen_y, _receptor, _distancia, _altura_max)
{
    var _obj = balon_punto_de_encuentro(_origen_x, _origen_y, _receptor, _distancia / 20);
    var _dir = point_direction(_origen_x, _origen_y, _obj.x, _obj.y);

    balon_liberar(_balon);
    with (_balon)
    {
        // Misma parábola que 04 · 46 §3.9 (proyectil_arco_lanzar), con el
        // macro de gravedad propio de este documento (GRAV_BALON).
        var _v0             = sqrt(2 * GRAV_BALON * _altura_max);
        var _frames_totales  = max(1, round((_v0 / GRAV_BALON) * 2));
        vel_x = lengthdir_x(_distancia / _frames_totales, _dir);
        vel_y = lengthdir_y(_distancia / _frames_totales, _dir);
        z     = 0;
        zvel  = _v0;
        estado = BalonEstado.en_vuelo;
        cooldown_toque = BALON_COOLDOWN_TOQUE;
        ultimo_toque         = other.id;
        equipo_ultimo_toque  = other.equipo;
    }
}
```

La sombra del balón en vuelo, el aterrizaje en `z <= 0`, el dibujado en `y - z`: todo eso ya
está resuelto por `sombra_dibujar()` y el patrón de `04 · 46` §3.5 — solo hay que llamarlos
desde el evento Draw de `obj_balon`, sin reescribir nada:

```gml
/// obj_balon — Draw
sombra_dibujar(x, y, z, 6, 80);   // 04 · 46 §3.5
draw_sprite_ext(sprite_index, image_index, x, y - z, image_xscale, image_yscale,
                 image_angle, image_blend, image_alpha);
```

## A.4 · Tiro: potencia, dirección y efecto

Un tiro es un pase alto sin receptor: la única pieza nueva es el **efecto** (*curve*, la
"vaselina" o el "gol olímpico" de córner), la curvatura lateral que aparece en el `switch` del
§A.2 (`efecto_curva`). Por qué el efecto necesita el arco de `04 · 46` en vez de bastar con una
curva horizontal por sí sola: un balón raso no "lee" como si tuviera efecto, porque no hay
altura que separe visualmente su trayectoria del suelo — el ojo necesita ver que sube, se curva
y baja para leer un lanzamiento con rosca. Por eso el efecto de este documento **se monta
encima** del arco vertical de `04 · 46`, nunca lo sustituye.

```gml
/// @func balon_disparar(_balon, _direccion, _potencia, _altura_max, _efecto)
/// @param {Real} _direccion   Grados, hacia dónde apunta el disparo en el instante del golpeo.
/// @param {Real} _potencia    Rapidez horizontal inicial, en píxeles/paso.
/// @param {Real} _altura_max  Altura máxima del arco (04 · 46 §3.9). 0 = disparo raso, sin arco.
/// @param {Real} _efecto      Grados/paso de curvatura. Positivo = a la derecha de la
///                            dirección de tiro; negativo = a la izquierda. 0 = sin rosca.
function balon_disparar(_balon, _direccion, _potencia, _altura_max, _efecto)
{
    balon_liberar(_balon);
    with (_balon)
    {
        vel_x = lengthdir_x(_potencia, _direccion);
        vel_y = lengthdir_y(_potencia, _direccion);
        efecto_curva = _efecto;

        if (_altura_max > 0)
        {
            zvel   = sqrt(2 * GRAV_BALON * _altura_max);
            estado = BalonEstado.en_vuelo;
        }
        else
        {
            z      = 0;
            zvel   = 0;
            estado = BalonEstado.libre;   // raso: rueda por el suelo con fricción normal (§A.2)
        }
        cooldown_toque = BALON_COOLDOWN_TOQUE;
        ultimo_toque         = other.id;
        equipo_ultimo_toque  = other.equipo;
    }
}
```

```gml
/// obj_jugador_humano — Create
carga_disparo = 0;

/// obj_jugador_humano — Step
// Potencia por tiempo de carga: el mismo principio que la potencia por
// distancia de arrastre de §B.1.4/§B.3.1 (una entrada continua que se
// convierte en potencia), aplicado aquí a mantener pulsado en vez de arrastrar
// el ratón — la mecánica de un balón de fútbol se controla con teclado/mando,
// no arrastrando.
if (con_balon && keyboard_check(vk_control))
{
    carga_disparo = min(carga_disparo + 1, 40);   // tope: no cargar indefinidamente
}

if (con_balon && keyboard_check_released(vk_control))
{
    var _potencia = clamp(carga_disparo * 0.3, 4, 16);
    var _efecto   = (keyboard_check(vk_shift) ? 1 : -1) * clamp(carga_disparo * 0.09, 0, 3.5);
    balon_disparar(global.balon, image_angle, _potencia, 40, _efecto);
    carga_disparo = 0;
}
```

> 🔺 **La rosca se apaga sola (`efecto_curva *= 0.97` cada Step, §A.2).** Sin ese decaimiento un
> tiro con mucho efecto acaba describiendo una espiral en vez de una parábola curvada —
> físicamente absurdo y visualmente confuso. El decaimiento es lo que hace que la curva se
> "cierre" hacia el final del vuelo, que es como se ve un balón real con rosca.

## A.5 · IA por roles y formaciones

### A.5.1 · La formación, como datos

Igual que un `EncuentroDef` (`04 · 33` §2) describe un encuentro sin código, una formación
describe posiciones **relativas al campo** (0 = línea de meta propia, 1 = línea de meta rival;
0 = banda superior, 1 = banda inferior), no coordenadas absolutas — así una misma formación
sirve en cualquier campo, y se puede voltear para el equipo que ataca hacia el otro lado.

```gml
// ---------------------------------------------------------------------------
// scr_formaciones
// ---------------------------------------------------------------------------
global.formacion_442 = [
    { rol: "portero",    x_rel: 0.04, y_rel: 0.50 },
    { rol: "defensa",    x_rel: 0.20, y_rel: 0.14 },
    { rol: "defensa",    x_rel: 0.16, y_rel: 0.38 },
    { rol: "defensa",    x_rel: 0.16, y_rel: 0.62 },
    { rol: "defensa",    x_rel: 0.20, y_rel: 0.86 },
    { rol: "medio",      x_rel: 0.46, y_rel: 0.16 },
    { rol: "medio",      x_rel: 0.42, y_rel: 0.40 },
    { rol: "medio",      x_rel: 0.42, y_rel: 0.60 },
    { rol: "medio",      x_rel: 0.46, y_rel: 0.84 },
    { rol: "delantero",  x_rel: 0.78, y_rel: 0.38 },
    { rol: "delantero",  x_rel: 0.78, y_rel: 0.62 },
];
```

```gml
/// obj_partido_control — Create (además de lo que ya trae §A.7): los límites del
/// terreno, independientes del tamaño de la room — un margen de "banda" alrededor
/// del rectángulo jugable.
global.campo = { x_min: 40, y_min: 40, x_max: room_width - 40, y_max: room_height - 40 };
```

```gml
/// obj_jugador_equipo — Create (el padre común; obj_jugador_humano y
/// obj_jugador_ia solo añaden su propio input o su propia IA por encima)
/// equipo_asignado, slot_asignado y direccion_asignada los pone quien instancia
/// a los 22 jugadores al montar el partido (un bucle sobre global.formacion_442
/// para cada equipo, alternando EQUIPO_LOCAL/EQUIPO_VISITANTE).
equipo                 = equipo_asignado;
mi_slot                = global.formacion_442[slot_asignado];
rol                    = mi_slot.rol;
equipo_direccion_ataque = direccion_asignada;   // 1 o -1 — hacia qué lado ataca ESTE equipo
vel_x                  = 0;
vel_y                  = 0;
con_balon              = false;
```

```gml
/// @func formacion_posicion_objetivo(_slot, _campo, _direccion_ataque, _bola_x, _bola_y)
/// @desc Posición absoluta a la que debe correr un jugador, resultado de dos
///       cosas combinadas: su hueco fijo en la formación, y un DESPLAZAMIENTO
///       DE BLOQUE hacia el balón (defensa de zona: todo el equipo se
///       comprime hacia el lado donde está jugándose el balón, sin
///       deshacer la formación).
/// @param {Struct} _slot    Una entrada de global.formacion_442.
/// @param {Struct} _campo   { x_min, y_min, x_max, y_max } — límites del terreno.
/// @param {Real}   _direccion_ataque  1 = ataca hacia x creciente; -1 = hacia x decreciente.
/// @returns {Struct} { x, y }
function formacion_posicion_objetivo(_slot, _campo, _direccion_ataque, _bola_x, _bola_y)
{
    var _x_rel = (_direccion_ataque > 0) ? _slot.x_rel : (1 - _slot.x_rel);
    var _base_x = lerp(_campo.x_min, _campo.x_max, _x_rel);
    var _base_y = lerp(_campo.y_min, _campo.y_max, _slot.y_rel);

    // Desplazamiento de bloque: cuanto más lejos esté el balón del centro del
    // campo en Y, más se comprime el equipo hacia ese lado — clamp() evita
    // que el desplazamiento saque a nadie de su carril razonable.
    var _centro_y     = lerp(_campo.y_min, _campo.y_max, 0.5);
    var _desplazamiento_y = clamp((_bola_y - _centro_y) * 0.25, -60, 60);

    // Y el bloque sube o baja (eje X) según en qué tercio del campo está el
    // balón: si el balón está en campo rival, el equipo entero adelanta
    // posiciones (presión); si está en campo propio, se repliega.
    var _campo_ancho   = _campo.x_max - _campo.x_min;
    var _bola_x_rel    = (_direccion_ataque > 0)
        ? (_bola_x - _campo.x_min) / _campo_ancho
        : 1 - (_bola_x - _campo.x_min) / _campo_ancho;
    var _desplazamiento_x = clamp((_bola_x_rel - 0.5) * 80, -50, 50) * _direccion_ataque;

    return { x: _base_x + _desplazamiento_x, y: _base_y + _desplazamiento_y };
}
```

### A.5.2 · Moverse a la posición: `Arrive`, no `Seek`

Correr hacia el hueco de formación con `Seek`/`ir_hacia()` (`04 · 23` §1) hace que el jugador
"vibre" sobre el punto exacto, corrigiendo de un lado a otro cada frame. `Arrive`/`llegar_a()`
(`04 · 23` §2) frena al acercarse — es exactamente el comportamiento de un jugador real ocupando
una posición. No se repite aquí, solo se llama tal cual está definida: `llegar_a()` ya mueve
`x`/`y` directamente (lee la posición de quien la llama), así que no hace falta envolverla en
`move_and_collide` a mano:

```gml
/// obj_jugador_ia — Step, cuando NO tiene el balón ni está en fase de ataque directo
var _obj = formacion_posicion_objetivo(mi_slot, global.campo, equipo_direccion_ataque,
                                         global.balon.x, global.balon.y);
llegar_a(_obj.x, _obj.y, VELOCIDAD_MAX, RADIO_FRENADO);   // 04 · 23 §2 — mueve x/y directamente
```

> 💡 **`llegar_a()` no evita que dos jugadores se amontonen entre sí** — solo apunta a un
> punto. Si tu juego necesita que no se solapen físicamente, corre después una pasada de
> `separacion_minima()` (`13 · 08` §3.2) sobre `obj_jugador_equipo`, el mismo patrón que esa
> sección ya usa para cajas que se amontonan — no hace falta reescribirlo para círculos aquí:
> tratar a cada jugador como una caja pequeña centrada en su `x`/`y` es suficiente para este caso.

### A.5.3 · Marcaje al hombre

Cuando el diseño pide marcaje personal en vez de zona, el objetivo de movimiento deja de ser el
hueco de formación y pasa a ser una posición relativa al rival asignado — "al lado de él, del
lado de la portería propia" (goal-side), para que no puedan superarlo con un pase de una sola
vez:

```gml
/// @func posicion_marcaje(_rival, _porteria_propia_x, _porteria_propia_y, _distancia)
/// @desc Un punto entre el rival marcado y la portería propia, a `_distancia`
///       píxeles del rival — "cubrir la espalda" en vez de pegarse encima.
function posicion_marcaje(_rival, _porteria_propia_x, _porteria_propia_y, _distancia)
{
    var _dir = point_direction(_rival.x, _rival.y, _porteria_propia_x, _porteria_propia_y);
    return { x: _rival.x + lengthdir_x(_distancia, _dir),
             y: _rival.y + lengthdir_y(_distancia, _dir) };
}
```

```gml
/// obj_jugador_ia — Create, si el diseño usa marcaje al hombre
rival_marcado = instance_nearest(x, y, obj_jugador_equipo);   // simplificado: el rival más
                                                                // cercano en el saque inicial;
                                                                // un juego real reasigna esto
                                                                // por posición/rol, no solo distancia
```

> 💡 **Zona y marcaje al hombre no son excluyentes.** Muchos equipos reales mezclan: zona en
> campo propio (§A.5.1, más seguro), marcaje al hombre en campo rival sobre el jugador con
> balón (`posicion_marcaje`) y sobre quien recibiría el próximo pase peligroso. La decisión de
> cuál aplicar a cada jugador y cuándo es diseño, no código: aquí están las dos piezas.

### A.5.4 · Cobertura y presión: reutilizando `GestorFichas`

Cuando el balón está cerca de varios rivales a la vez, la regla de "no dejes que todos presionen
al que tiene el balón" es exactamente el problema que `04 · 33` §3 ya resuelve con
`GestorFichas` — aquí se instancia con radios de campo abierto en vez de radios de melé (los de
`04 · 47` §2), y con el balón (no un `obj_jugador`) como objetivo:

```gml
/// obj_partido_control — Create
global.gestor_presion_local = new GestorFichas(
    global.balon,          // el objetivo es el BALÓN, no un jugador — 04 · 33 solo exige x/y
    5,                      // capacidad de rejilla: cuántos pueden acercarse a presionar
    2,                      // capacidad de ataque: cuántos pueden entrar a robar a la vez
    90,                     // radio de aproximación — campo abierto, no melé
    35                      // radio de "ataque" (entrada a robar, §A.2.1)
);
```

El resto —fases `acercandose`/`pidiendo_ataque`/`atacando`, el hueco de escape para que el
poseedor siempre tenga una salida— es literalmente `04 · 33` §3 sin cambiar una línea, con
`solicitar_acercarse`/`solicitar_ataque` sustituyendo a la decisión de "quién presiona ahora" y
`04 · 47` §7 como ejemplo ya escrito de esa misma integración en otro género.

### A.5.5 · Desmarque

Un jugador sin el balón que está "cubierto" (un rival cerca, sin línea de pase clara) debe
generar espacio antes de que se le pueda pasar — el comportamiento inverso a `Arrive`: alejarse
del rival más cercano mientras se mantiene dentro de la zona de formación.

```gml
/// obj_jugador_ia — Step, cuando el compañero con balón está cerca y busca opciones de pase
var _rival_cercano = instance_nearest(x, y, obj_jugador_equipo);
if (_rival_cercano != noone && _rival_cercano.equipo != equipo
    && point_distance(x, y, _rival_cercano.x, _rival_cercano.y) < DISTANCIA_CUBIERTO)
{
    // huir_de() (04 · 23 §1) YA mueve x/y y devuelve el ángulo — aquí se llama
    // con velocidad 0 para quedarse solo con el ángulo (lengthdir_x/y(0, _) no
    // desplaza nada) y poder MEZCLARLO con el tirón hacia el hueco de
    // formación, en vez de aplicar la huida pura.
    var _dir_huida = huir_de(_rival_cercano.x, _rival_cercano.y, 0);

    var _obj = formacion_posicion_objetivo(mi_slot, global.campo, equipo_direccion_ataque,
                                             global.balon.x, global.balon.y);
    var _dir_formacion = point_direction(x, y, _obj.x, _obj.y);

    var _dir_final = point_direction(0, 0,
        lengthdir_x(1, _dir_huida) + lengthdir_x(0.6, _dir_formacion),
        lengthdir_y(1, _dir_huida) + lengthdir_y(0.6, _dir_formacion));

    x += lengthdir_x(VELOCIDAD_MAX, _dir_final);
    y += lengthdir_y(VELOCIDAD_MAX, _dir_final);
}
```

## A.6 · Reglas y árbitro

### A.6.1 · La máquina de estados del partido

```gml
enum EstadoPartido
{
    en_juego,
    parado_saque_banda,
    parado_saque_esquina,
    parado_saque_puerta,
    parado_falta,
    parado_gol,
    descanso,
    finalizado
}
```

```gml
/// obj_partido_control — Step
switch (estado_partido)
{
    case EstadoPartido.en_juego:
        arbitro_comprobar_limites(global.balon);   // §A.6.2
        break;

    // Los estados "parado_*" no avanzan el reloj (§A.7) y esperan a que el
    // jugador (o la IA) ejecute la reanudación — ver §A.6.4.
}
```

### A.6.2 · Fuera de banda y saques

```gml
/// @func arbitro_comprobar_limites(_balon)
/// @desc Comprueba si el balón ha salido del terreno y decide qué saque toca.
///       `global.campo` es el mismo struct { x_min, y_min, x_max, y_max } de §A.5.1.
function arbitro_comprobar_limites(_balon)
{
    var _c = global.campo;
    if (_balon.y < _c.y_min || _balon.y > _c.y_max)
    {
        // Fuera por la banda: saque para el equipo QUE NO tocó el balón en último lugar.
        var _equipo_saca = 1 - _balon.equipo_ultimo_toque;
        partido_parar(EstadoPartido.parado_saque_banda, _equipo_saca,
                       clamp(_balon.x, _c.x_min, _c.x_max),
                       clamp(_balon.y, _c.y_min, _c.y_max));
    }
    else if (_balon.x < _c.x_min || _balon.x > _c.x_max)
    {
        // Fuera por la línea de meta: saque de esquina si lo tocó en último
        // lugar el equipo que DEFIENDE esa portería; saque de puerta si lo
        // tocó el equipo que ATACABA.
        var _lado_local = (_balon.x < _c.x_min);
        var _lo_toco_el_defensor = (_lado_local && _balon.equipo_ultimo_toque == EQUIPO_LOCAL)
                                 || (!_lado_local && _balon.equipo_ultimo_toque == EQUIPO_VISITANTE);

        if (_lo_toco_el_defensor)
        {
            partido_parar(EstadoPartido.parado_saque_esquina, 1 - _balon.equipo_ultimo_toque,
                           _lado_local ? _c.x_min : _c.x_max, _balon.y);
        }
        else
        {
            partido_parar(EstadoPartido.parado_saque_puerta, _balon.equipo_ultimo_toque,
                           _lado_local ? _c.x_min + 20 : _c.x_max - 20,
                           lerp(_c.y_min, _c.y_max, 0.5));
        }
    }
}
```

### A.6.3 · Fuera de juego

El fuera de juego se comprueba **en el instante en que se juega el balón hacia delante**, no de
forma continua — es la trampa más común al implementarlo: comprobarlo cada Step marca fuera de
juego a un delantero que simplemente está de pie ahí, sin que nadie le haya pasado nada.

```gml
/// @func linea_fuera_de_juego(_equipo_defensor, _direccion_ataque)
/// @desc x del segundo defensor más adelantado del equipo que defiende — el
///       portero no cuenta (normalmente es el más retrasado de todos, y
///       contarlo desplazaría la línea sin sentido).
/// @returns {Real}
function linea_fuera_de_juego(_equipo_defensor, _direccion_ataque)
{
    var _xs = [];
    with (obj_jugador_equipo)
    {
        if (equipo == _equipo_defensor && rol != "portero") array_push(_xs, x);
    }
    if (array_length(_xs) < 2) return (_direccion_ataque > 0) ? -99999 : 99999;

    array_sort(_xs, (_direccion_ataque > 0));   // ascendente si ataca hacia x creciente
    var _indice = (_direccion_ataque > 0) ? (array_length(_xs) - 2) : 1;
    return _xs[_indice];
}

/// @func esta_en_fuera_de_juego(_atacante, _direccion_ataque, _linea)
/// @returns {Bool}
function esta_en_fuera_de_juego(_atacante, _direccion_ataque, _linea)
{
    return (_direccion_ataque > 0) ? (_atacante.x > _linea) : (_atacante.x < _linea);
}

/// @func arbitro_pitar_fuera_de_juego(_equipo_favorecido, _x, _y)
/// @desc Se resuelve exactamente igual que una falta (§A.6.4): tiro libre para
///       el equipo favorecido, desde donde estaba el balón.
function arbitro_pitar_fuera_de_juego(_equipo_favorecido, _x, _y)
{
    partido_parar(EstadoPartido.parado_falta, _equipo_favorecido, _x, _y);
}
```

```gml
/// obj_jugador_ia — al ejecutar un pase (dentro de balon_pasar/balon_pasar_alto, ANTES de
/// aplicar la velocidad) — se comprueba solo en el momento del pase, no cada frame.
var _linea = linea_fuera_de_juego(1 - equipo, equipo_direccion_ataque);
if (esta_en_fuera_de_juego(_receptor, equipo_direccion_ataque, _linea))
{
    arbitro_pitar_fuera_de_juego(_receptor.equipo == EQUIPO_LOCAL ? EQUIPO_VISITANTE : EQUIPO_LOCAL,
                                  global.balon.x, global.balon.y);
    exit;   // el pase no se ejecuta: el árbitro ya paró el juego
}
```

> ⚠️ **Simplificación deliberada**: la regla real añade "solo si el atacante interfiere en la
> jugada" y "no fuera de juego si recibe de un saque de banda/esquina/puerta". Este documento
> resuelve la comprobación geométrica (la parte sin la cual no hay fuera de juego posible); las
> excepciones son una lista de condiciones que se añaden al `if` de arriba según cuánto realismo
> quiera el juego.

### A.6.4 · Faltas y reanudaciones

Detectar QUÉ cuenta como falta es una decisión de diseño (una entrada que falla con cierta
probabilidad, como en §A.2.1, o un temporizador de contacto sostenido) — este documento resuelve
el **resultado**: parar el partido, y la reanudación en sí.

```gml
/// @func arbitro_evaluar_entrada(_defensor, _poseedor)
/// @desc Enganche llamado desde §A.2.1 cuando una entrada falla. La probabilidad
///       de que además sea falta (no toda entrada fallida lo es) es otro
///       parámetro de diseño, separado del de robar.
function arbitro_evaluar_entrada(_defensor, _poseedor)
{
    if (random(1) < PROB_FALTA_EN_ENTRADA_FALLIDA)
    {
        partido_parar(EstadoPartido.parado_falta, _poseedor.equipo, _poseedor.x, _poseedor.y);
    }
}

/// @func partido_parar(_estado, _equipo_posesion, _x, _y)
/// @desc Congela el juego en el estado indicado y coloca el balón donde se
///       reanudará. Común a los cuatro tipos de saque y a la falta.
function partido_parar(_estado, _equipo_posesion, _x, _y)
{
    estado_partido = _estado;
    balon_liberar(global.balon);
    global.balon.x = _x;
    global.balon.y = _y;
    global.balon.vel_x = 0;
    global.balon.vel_y = 0;
    global.equipo_reanuda = _equipo_posesion;
}

/// @func partido_reanudar()
/// @desc Llamado cuando el jugador (o la IA) del equipo con posesión decide
///       sacar. Vuelve el partido a estado "en_juego" y entrega el balón al
///       jugador más cercano al punto de saque de ese equipo.
function partido_reanudar()
{
    var _sacador = noone;
    var _mejor_dist = infinity;
    with (obj_jugador_equipo)
    {
        if (equipo == global.equipo_reanuda)
        {
            var _d = point_distance(x, y, global.balon.x, global.balon.y);
            if (_d < _mejor_dist) { _mejor_dist = _d; _sacador = id; }
        }
    }
    if (_sacador != noone) balon_asignar_posesion(global.balon, _sacador);
    estado_partido = EstadoPartido.en_juego;
}
```

> ⚠️ **La distancia mínima del rival al saque** (los 9,15 m/10 yardas reales) no está resuelta
> aquí: es un `move_and_collide` contra una zona circular temporal alrededor del punto de saque,
> el mismo patrón de `obj_zona_altura` de `04 · 46` §3.8 aplicado a "impedir el paso" en vez de
> "cambiar la altura del suelo". Se marca como ⚠️ porque no se ha verificado contra un caso de
> uso real dentro de esta biblioteca — es una extensión razonable, no un patrón ya probado aquí.

## A.7 · Reloj, marcador, tiempo añadido, mitades y prórroga

El reloj de un partido corre en tiempo real, no en frames — a 30 fps y a 144 Hz debe tardar lo
mismo en llegar al descanso. Se apoya en `delta_time` (microsegundos reales desde el frame
anterior), el mismo patrón que `13 · 08` §1.3 usa para el paso fijo de física, aplicado aquí a
un contador de segundos de partido en vez de a una simulación:

```gml
/// obj_partido_control — Create
segundos_partido   = 0;          // tiempo transcurrido en la mitad actual
mitad_actual       = 1;          // 1, 2, o 3/4 si hay prórroga
duracion_mitad     = 180;        // segundos de PARTIDA por mitad — compréselo, no 45 min reales
tiempo_anadido     = 0;          // se calcula al final de cada mitad (§ abajo)
en_tiempo_anadido  = false;
marcador_local     = 0;
marcador_visitante = 0;
paradas_acumuladas = 0;          // segundos que el reloj estuvo "parado_*" esta mitad
requiere_desempate = false;      // true en un torneo de eliminatoria; false en liga (empate vale)
estado_partido     = EstadoPartido.en_juego;
```

```gml
/// obj_partido_control — Step
if (estado_partido != EstadoPartido.descanso && estado_partido != EstadoPartido.finalizado)
{
    var _dt = delta_time / 1000000;   // segundos reales de este frame

    if (estado_partido == EstadoPartido.en_juego)
    {
        segundos_partido += _dt;
    }
    else
    {
        paradas_acumuladas += _dt;    // el tiempo con el juego parado cuenta para el añadido
    }

    var _limite = duracion_mitad + (en_tiempo_anadido ? tiempo_anadido : 0);
    if (segundos_partido >= duracion_mitad && !en_tiempo_anadido)
    {
        // Al llegar al límite regular, se calcula el añadido UNA VEZ con lo
        // acumulado hasta ahora (paradas por faltas, saques, celebraciones de
        // gol) y se entra en tiempo añadido en vez de cortar en seco.
        tiempo_anadido    = round(paradas_acumuladas * 0.5);   // media de las paradas: ajustable
        en_tiempo_anadido = true;
    }
    else if (en_tiempo_anadido && segundos_partido >= _limite)
    {
        partido_fin_de_mitad();
    }
}
```

```gml
/// @func partido_fin_de_mitad()
function partido_fin_de_mitad()
{
    if (mitad_actual < 2)
    {
        mitad_actual += 1;
        estado_partido = EstadoPartido.descanso;
    }
    else if (mitad_actual == 2 && marcador_local == marcador_visitante && requiere_desempate)
    {
        mitad_actual   += 1;          // pasa a prórroga: mitades 3 y 4
        duracion_mitad   = 30;        // prórroga más corta — otro parámetro de diseño
        estado_partido   = EstadoPartido.descanso;
    }
    else
    {
        estado_partido = EstadoPartido.finalizado;
    }

    segundos_partido  = 0;
    paradas_acumuladas = 0;
    en_tiempo_anadido  = false;
}
```

```gml
/// @func partido_tiempo_formatear(_segundos)
/// @desc "MM:SS", con el minuto sin tope (un partido puede pasar de 99:59 en
///       una prórroga larga, así que NO se recorta a dos dígitos el minuto).
/// @returns {String}
function partido_tiempo_formatear(_segundos)
{
    var _min = floor(_segundos / 60);
    var _seg = floor(_segundos mod 60);
    return string(_min) + ":" + ((_seg < 10) ? ("0" + string(_seg)) : string(_seg));
}
```

```gml
/// obj_partido_control — Draw GUI
draw_set_font(fnt_marcador);
draw_set_halign(fa_center);
draw_set_valign(fa_top);
draw_set_color(c_white);

var _texto_reloj = partido_tiempo_formatear(segundos_partido)
                  + (en_tiempo_anadido ? " +" + string(tiempo_anadido) : "");
draw_text(display_get_gui_width() / 2, 8,
          string(marcador_local) + "  -  " + string(marcador_visitante) + "    " + _texto_reloj);
```

Un gol simplemente llama a `partido_parar(EstadoPartido.parado_gol, ...)`, suma al marcador
correspondiente y, tras una pausa breve (celebración — cuenta como parada, así que alimenta el
tiempo añadido de forma natural gracias al cálculo de arriba), reanuda con
`partido_reanudar()` desde el centro del campo.

---

# Parte B · Física de mesa

> Billar, pinball y minigolf comparten familia (una bola, una mesa, el objetivo es meterla en
> algún sitio) pero cada uno tira hacia un lado distinto de la tabla de decisión de
> [`13 · 08` §1.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/08%20-%20Físicas%20a%20mano%20y%20fluidos.md#11-a-mano-o-box2d-la-tabla-de-decisión).
> Este documento no repite esa tabla general: la aplica, caso por caso, a los tres juegos.

| Juego | Vía recomendada | Por qué |
|---|---|---|
| **Billar** | **A mano** (§B.1) | Necesitas la fórmula exacta del choque y control fino sobre restitución/efecto por bola — con Box2D dependes del solver y pierdes ese control |
| **Pinball** | **Box2D** (§B.2) | *Flippers* con bisagra y par de fuerzas son exactamente un `physics_joint_revolute_create` con motor — reescribir eso a mano es reinventar un solver de contactos |
| **Minigolf** | **A mano** (§B.3) | Una sola bola con fricción por terreno es aritmética de tres líneas — un mundo físico entero para un objeto es forzar la herramienta |

Cuando la tabla de un juego concreto se sale de este patrón por defecto (billar con bandas de
formas raras y muchas bolas apiladas que se empujan entre sí; minigolf con obstáculos poligonales
complejos que rebotan a ángulos imprevisibles), la fila de la tabla de `13 · 08` §1.1 vuelve a
aplicar sin cambios: la simulación física entera es Box2D, y tu propio código deja de tener que
resolver la geometría de contacto.

## B.1 · Billar

### B.1.1 · La pieza que faltaba: colisión elástica entre dos círculos

`13 · 08` §7.1 (`rebotar_vector`) resuelve el rebote de UN cuerpo contra una superficie FIJA
— una pared, la banda de la mesa. El billar necesita la otra mitad: **dos bolas que se mueven
las dos**, y el momento se reparte entre ambas según su masa. Es el caso didáctico por
excelencia de conservación del momento en un choque elástico, y no estaba resuelto en ningún
documento de esta biblioteca.

```gml
// ---------------------------------------------------------------------------
// scr_billar_fisica
// ---------------------------------------------------------------------------
#macro BILLAR_FRICCION_MESA  0.985   // por paso a 60 fps — paño con rozamiento bajo
#macro BILLAR_UMBRAL_PARADA  0.03    // por debajo de esto, una bola se considera parada
#macro BILLAR_POTENCIA_MAX   14      // rapidez máxima al salir golpeada, en píxeles/paso
```

```gml
/// @func colisionar_circulos_elastico(_bola_a, _bola_b, _restitucion)
/// @desc Resuelve el choque entre dos bolas circulares: separa el solapamiento
///       y reparte la velocidad a lo largo de la normal de impacto según la
///       masa de cada una. Con masas iguales (billar estándar) el resultado
///       final es INTERCAMBIAR la componente de velocidad normal — aquí se
///       deja la fórmula general (Wikipedia, "Elastic collision", forma 1D
///       aplicada sobre la normal) para poder tener bolas de distinta masa
///       (petanca, canicas) sin tocar el código.
/// @param {Id.Instance} _bola_a
/// @param {Id.Instance} _bola_b
/// @param {Real} _restitucion  1 = elástico perfecto (billar real: 0,92-0,98); 0 = se pegan.
function colisionar_circulos_elastico(_bola_a, _bola_b, _restitucion = 0.95)
{
    var _dx = _bola_b.x - _bola_a.x;
    var _dy = _bola_b.y - _bola_a.y;
    var _dist = point_distance(0, 0, _dx, _dy);
    if (_dist == 0) { _dx = 1; _dy = 0; _dist = 1; }   // centros exactamente iguales: evita 0/0

    var _nx = _dx / _dist;
    var _ny = _dy / _dist;

    // 1. Separar el solapamiento ANTES de tocar la velocidad — si no, el
    //    siguiente Step las vuelve a encontrar solapadas y "vibran" sin fin
    //    (la misma trampa que separacion_minima() evita en 13 · 08 §3.2,
    //    aquí aplicada a círculos en vez de a cajas).
    var _solape = (_bola_a.radio + _bola_b.radio) - _dist;
    if (_solape > 0)
    {
        _bola_a.x -= _nx * _solape * 0.5;
        _bola_a.y -= _ny * _solape * 0.5;
        _bola_b.x += _nx * _solape * 0.5;
        _bola_b.y += _ny * _solape * 0.5;
    }

    // 2. Componente de velocidad de cada bola A LO LARGO de la normal.
    var _van = dot_product(_bola_a.vel_x, _bola_a.vel_y, _nx, _ny);
    var _vbn = dot_product(_bola_b.vel_x, _bola_b.vel_y, _nx, _ny);

    if (_van - _vbn <= 0) return;   // ya se están separando: no choques dos veces (13 · 08 §7.1)

    var _ma = _bola_a.masa;
    var _mb = _bola_b.masa;

    var _van_final = ((_ma - _restitucion * _mb) * _van + (1 + _restitucion) * _mb * _vbn) / (_ma + _mb);
    var _vbn_final = ((_mb - _restitucion * _ma) * _vbn + (1 + _restitucion) * _ma * _van) / (_ma + _mb);

    // 3. Solo se corrige la componente NORMAL. La TANGENCIAL (perpendicular a
    //    la normal) se queda exactamente igual: es lo que hace que dos bolas
    //    que se rozan de refilón sigan casi de largo, en vez de rebotar como
    //    si el golpe hubiera sido frontal.
    var _delta_a = _van_final - _van;
    var _delta_b = _vbn_final - _vbn;

    _bola_a.vel_x += _nx * _delta_a;
    _bola_a.vel_y += _ny * _delta_a;
    _bola_b.vel_x += _nx * _delta_b;
    _bola_b.vel_y += _ny * _delta_b;
}
```

> 💡 **Comprobación con masas iguales** (`_ma == _mb == m`, `_restitucion == 1`): la fórmula da
> `_van_final = _vbn` y `_vbn_final = _van` — las dos bolas literalmente intercambian su
> velocidad a lo largo de la normal. Es el resultado que cualquiera que haya jugado al billar
> reconoce: golpear de lleno una bola parada la deja a ella en movimiento y detiene la tuya.

```gml
/// obj_bola_billar — Create
vel_x = 0;
vel_y = 0;
radio = 8;
masa  = 1;         // todas las bolas de billar pesan lo mismo; se deja como
                    // variable por si el juego mezcla tamaños (petanca)
numero = 0;         // 0 = bola blanca
en_tronera = false;
efecto = 0;         // grados/paso de curvatura por el "toque" del taco (§B.1.4)

// Solo la bola blanca necesita esto — el turno y el arrastre del taco (§B.1.4):
turno_jugador     = (numero == 0);
arrastre_activo   = false;
arrastre_x        = 0;
arrastre_y        = 0;
efecto_pedido     = 0;   // fijado por la UI de "toque" antes de soltar el arrastre
mostrar_apuntado  = false;   // leído en Draw — el arrastre se CALCULA en Step, se DIBUJA en Draw
potencia_actual   = 0;
direccion_actual  = 0;

/// obj_bola_billar — Step
if (!en_tronera)
{
    x += vel_x;
    y += vel_y;

    vel_x *= power(BILLAR_FRICCION_MESA, delta_time / 1000000 * 60);   // 13 · 08 §1.3
    vel_y *= power(BILLAR_FRICCION_MESA, delta_time / 1000000 * 60);
    if (point_distance(0, 0, vel_x, vel_y) < BILLAR_UMBRAL_PARADA) { vel_x = 0; vel_y = 0; }

    // Efecto (backspin/topspin/lateral): decae igual que en el balón de
    // fútbol (§A.4) — mismo mecanismo, distinta escena.
    if (efecto != 0)
    {
        var _rapidez = point_distance(0, 0, vel_x, vel_y);
        if (_rapidez > 0.1)
        {
            var _dir = point_direction(0, 0, vel_x, vel_y) + efecto;
            vel_x = lengthdir_x(_rapidez, _dir);
            vel_y = lengthdir_y(_rapidez, _dir);
        }
        efecto *= 0.94;   // el efecto se agota más rápido que la rosca del balón:
                           // la fricción del paño lo apaga en un par de metros
    }

    // Bandas: rebote contra las cuatro paredes de la mesa con 13 · 08 §7.1
    // (rebotar_vector) — no se repite aquí, solo se llama con la normal de
    // cada banda. Los límites de la mesa son globales: una sola mesa, leída
    // por las N bolas (se fijan en obj_control_billar — Create, §B.1.2).
    if (x - radio < global.mesa_x1) { x = global.mesa_x1 + radio; var _r = rebotar_vector(vel_x, vel_y,  1, 0, 0.8); vel_x = _r[0]; vel_y = _r[1]; }
    if (x + radio > global.mesa_x2) { x = global.mesa_x2 - radio; var _r = rebotar_vector(vel_x, vel_y, -1, 0, 0.8); vel_x = _r[0]; vel_y = _r[1]; }
    if (y - radio < global.mesa_y1) { y = global.mesa_y1 + radio; var _r = rebotar_vector(vel_x, vel_y, 0,  1, 0.8); vel_x = _r[0]; vel_y = _r[1]; }
    if (y + radio > global.mesa_y2) { y = global.mesa_y2 - radio; var _r = rebotar_vector(vel_x, vel_y, 0, -1, 0.8); vel_x = _r[0]; vel_y = _r[1]; }
}
```

### B.1.2 · Detectar y resolver TODAS las colisiones del paño

```gml
/// obj_control_billar — Step, tras mover todas las bolas
var _bolas = [];
with (obj_bola_billar) { if (!en_tronera) array_push(_bolas, id); }

for (var _i = 0; _i < array_length(_bolas); _i++)
{
    for (var _j = _i + 1; _j < array_length(_bolas); _j++)
    {
        var _a = _bolas[_i];
        var _b = _bolas[_j];
        if (solapan_circulos(_a.x, _a.y, _a.radio, _b.x, _b.y, _b.radio))   // 13 · 08 §3.1
        {
            colisionar_circulos_elastico(_a, _b, 0.95);
        }
    }
}
```

> 🔺 **Comparación por parejas es O(n²)** — con 16 bolas son 120 comparaciones por Step, nada
> preocupante. Si tu mesa tiene cientos de bolas (una demo, no billar de verdad), el spatial
> hash de `13 · 08` §4 resuelve exactamente ese caso; no hace falta aquí.

### B.1.3 · Troneras

```gml
/// obj_tronera — Create
radio_boca = 14;

/// obj_control_billar — Step, tras resolver colisiones
with (obj_bola_billar)
{
    if (en_tronera) continue;

    var _t = instance_nearest(x, y, obj_tronera);
    if (_t != noone && point_distance(x, y, _t.x, _t.y) < _t.radio_boca)
    {
        en_tronera = true;
        vel_x = 0;
        vel_y = 0;
        if (numero == 0)
        {
            billar_reposicionar_blanca();   // "falta": la blanca vuelve a la mano
        }
        else
        {
            billar_anotar(numero);
            instance_destroy();
        }
    }
}
```

```gml
/// obj_control_billar — Create
global.bolas_embocadas = [];
// Límites de la mesa, en coordenadas de room — un rectángulo interior al
// tapete (deja fuera el grosor de la banda dibujada).
global.mesa_x1 = 60;  global.mesa_y1 = 60;
global.mesa_x2 = room_width - 60;  global.mesa_y2 = room_height - 60;

/// @func billar_reposicionar_blanca()
/// @desc La bola blanca cayó en una tronera: "falta" clásica de billar — vuelve
///       a estar disponible "en mano", en el punto de salida de la mesa.
function billar_reposicionar_blanca()
{
    with (obj_bola_billar)
    {
        if (numero == 0)
        {
            en_tronera = false;
            x = lerp(global.mesa_x1, global.mesa_x2, 0.25);
            y = lerp(global.mesa_y1, global.mesa_y2, 0.5);
            vel_x = 0;
            vel_y = 0;
        }
    }
}

/// @func billar_anotar(_numero)
/// @desc Registra la bola embocada. A qué grupo pertenece cada jugador (lisas/
///       rayadas) y cuándo se acaba la partida son reglas del juego de billar
///       concreto que implementes — aquí solo se lleva la cuenta.
function billar_anotar(_numero)
{
    array_push(global.bolas_embocadas, _numero);
}
```

### B.1.4 · El golpe: apuntar, cargar potencia y efecto, soltar

```gml
/// obj_bola_billar (la blanca) — Step, solo cuando es el turno del jugador Y
/// no hay ninguna bola en movimiento (billar_hay_bolas_en_movimiento(), abajo).
/// SOLO calcula: dibujar un draw_* aquí no pinta nada — eso es el evento
/// Draw, más abajo (los eventos Step no tienen un contexto de render activo).
mostrar_apuntado = false;

if (turno_jugador && !billar_hay_bolas_en_movimiento())
{
    if (mouse_check_button_pressed(mb_left))
    {
        arrastre_activo = true;
        arrastre_x = mouse_x;
        arrastre_y = mouse_y;
    }

    if (arrastre_activo)
    {
        // El taco tira hacia atrás: la potencia sale del arrastre INVERSO
        // (soltar lejos del punto de partida golpea fuerte).
        var _dx = arrastre_x - mouse_x;
        var _dy = arrastre_y - mouse_y;
        potencia_actual  = clamp(point_distance(0, 0, _dx, _dy) * 0.06, 0, BILLAR_POTENCIA_MAX);
        direccion_actual = point_direction(0, 0, _dx, _dy);
        mostrar_apuntado = true;

        if (mouse_check_button_released(mb_left))
        {
            vel_x  = lengthdir_x(potencia_actual, direccion_actual);
            vel_y  = lengthdir_y(potencia_actual, direccion_actual);
            efecto = efecto_pedido;   // el "toque" lateral elegido antes de tirar (UI aparte)
            arrastre_activo  = false;
            mostrar_apuntado = false;
        }
    }
}
```

```gml
/// obj_bola_billar (la blanca) — Draw
draw_self();
if (mostrar_apuntado)
{
    draw_arrow(x, y, x + lengthdir_x(potencia_actual * 8, direccion_actual),
                      y + lengthdir_y(potencia_actual * 8, direccion_actual), 6);
}
```

```gml
/// @func billar_hay_bolas_en_movimiento()
/// @returns {Bool}
function billar_hay_bolas_en_movimiento()
{
    var _hay = false;
    with (obj_bola_billar)
    {
        if (!en_tronera && point_distance(0, 0, vel_x, vel_y) > 0) { _hay = true; break; }
    }
    return _hay;
}
```

> 💡 **`efecto_pedido`** es el punto donde el jugador pica el taco fuera del centro de la bola
> (una UI aparte: una miniatura de la bola blanca con un punto arrastrable). El modelo de arriba
> es deliberadamente simplificado: el efecto real de billar transfiere momento angular en cada
> choque contra banda o bola, y modelar eso bien —no solo cómo se curva rodando, sino cómo
> "agarra" y cambia el rebote en la banda— es precisamente donde Box2D (con fricción de fixture
> y velocidad angular resueltas por el motor) empieza a compensar frente a la vía a mano.

## B.2 · Pinball

### B.2.1 · El mundo, y por qué aquí SÍ es Box2D

La configuración del mundo físico (gravedad, densidad, restitución, fricción) es exactamente
`04 · 22` §1 — no se repite. Lo único específico de un pinball es la gravedad: apunta "hacia
abajo" en la pantalla (la mesa está inclinada hacia el jugador en la vida real; en 2D esa
inclinación se simula con una gravedad más suave que la de un plataformas):

```gml
/// obj_mesa_pinball — Create
physics_world_gravity(0, 4);   // 04 · 22 §1 — más suave que un plataformas: simula la
                                 // inclinación real de la mesa, no una caída libre completa
global.puntuacion = 0;
global.kicker_x = 60;   // punto de salida del lanzador — ajusta a tu mesa; global porque
global.kicker_y = room_height - 40;   // pinball_activar_multibolas() se llama desde otras instancias
```

### B.2.2 · *Flippers*: bisagra y par de fuerzas

Un *flipper* es un `physics_joint_revolute_create` (la "bisagra") con motor: el **par de
fuerzas** (*torque*) es literalmente lo que ese motor aplica para forzar la rotación contra
cualquier cosa que se le resista — incluida la bola, si le da de lleno.

```gml
#macro LARGO_FLIPPER   48   // píxeles, de punta a punta
#macro GROSOR_FLIPPER  10
```

```gml
/// obj_pivote_flipper_izq — Create (cuerpo ESTÁTICO, densidad 0, invisible;
/// colocado en el Room Editor exactamente en el punto de giro del flipper)
var _fix = physics_fixture_create();
physics_fixture_set_circle_shape(_fix, 2);
physics_fixture_set_density(_fix, 0);
physics_fixture_bind(_fix, id);
physics_fixture_delete(_fix);
```

```gml
/// obj_flipper_izq — Create (cuerpo DINÁMICO: la paleta en sí, alargada)
var _fix = physics_fixture_create();
physics_fixture_set_box_shape(_fix, LARGO_FLIPPER * 0.5, GROSOR_FLIPPER * 0.5);
physics_fixture_set_density(_fix, 3);        // pesada a propósito: que la bola no la mueva sola
physics_fixture_set_friction(_fix, 0.3);
physics_fixture_set_restitution(_fix, 0.1);  // el "pop" lo da la velocidad angular, no el rebote
physics_fixture_bind(_fix, id);
physics_fixture_delete(_fix);

angulo_reposo = 35;    // grados: dónde cae por gravedad, sin pulsar nada
angulo_activo = -35;   // grados: al pulsar, hacia el centro de la mesa

junta = physics_joint_revolute_create(
    obj_pivote_flipper_izq, id,
    obj_pivote_flipper_izq.phy_position_x, obj_pivote_flipper_izq.phy_position_y,
    angulo_activo, angulo_reposo, true,     // límites de ángulo: el flipper no puede pasarse
    900000, 0, true,                        // par motor máximo, velocidad inicial 0, motor activo
    false);                                 // los dos cuerpos no colisionan entre sí
```

```gml
/// obj_flipper_izq — Step
physics_joint_set_value(junta, phy_joint_motor_speed,
    keyboard_check(vk_left) ? -1400 : 500);   // subida rápida, bajada más lenta (mismo signo
                                                // que angulo_activo/angulo_reposo de arriba —
                                                // si tu flipper sube al revés, invierte los dos)
```

> 🔺 **El signo de `motor_speed` depende de cómo coloques la fixture y el ángulo de reposo.**
> `04 · 22` §4 ya avisa de que el orden de argumentos de un joint es el sitio donde más se
> inventa código; aquí además hay que comprobar EN LA PANTALLA que el flipper sube hacia donde
> debería — si sube al revés, cambia el signo de `motor_speed` en vez de tocar los límites de
> ángulo.

`obj_flipper_der` (y su `obj_pivote_flipper_der`) son el mismo patrón en espejo: mismos pasos,
`angulo_reposo`/`angulo_activo` con el signo cambiado, y `vk_right` en vez de `vk_left` en el
Step — no se repite aquí.

### B.2.3 · *Bumpers*

```gml
/// obj_bumper — Create (círculo ESTÁTICO, densidad 0, restitución alta)
var _fix = physics_fixture_create();
physics_fixture_set_circle_shape(_fix, 16);
physics_fixture_set_density(_fix, 0);
physics_fixture_set_restitution(_fix, 0.9);
physics_fixture_bind(_fix, id);
physics_fixture_delete(_fix);

empuje_extra = 12;   // impulso EXTRA, además del rebote físico normal — el "pop" del bumper
puntos       = 100;

/// obj_bumper — Collision con obj_bola_pinball (other = la bola)
var _dir = point_direction(x, y, other.x, other.y);
physics_apply_impulse(other.phy_position_x, other.phy_position_y,
                       lengthdir_x(empuje_extra, _dir), lengthdir_y(empuje_extra, _dir));
global.puntuacion += puntos;   // puntuación de la partida, no del bumper: siempre global
// flash del sprite del bumper, sonido — enganche de VFX (04 · 39), no se repite aquí
```

### B.2.4 · Rampas y carriles

En Box2D 2D no hay una rampa de verdad que suba a otra altura — lo que se llama "rampa" en un
pinball 2D es un **carril guía**: geometría estática que encauza la bola por un camino, y un
**sensor** que detecta que la ha recorrido para dar puntos o activar el multibolas. La forma más
cómoda de dibujar ese carril es un `Path` de GameMaker, trazado a mano en el editor, convertido
en una *chain shape* al arrancar:

```gml
/// obj_carril_guia — Create
/// path_asignado : el Path dibujado en el Room Editor con la forma exacta del carril

var _fix = physics_fixture_create();
physics_fixture_set_chain_shape(_fix, false);   // false: es un carril abierto, no un anillo cerrado

var _n = path_get_number(path_asignado);
for (var _i = 0; _i < _n; _i++)
{
    // physics_fixture_add_point() quiere coordenadas LOCALES a esta instancia;
    // el Path las da en coordenadas de room, así que se restan x/y.
    physics_fixture_add_point(_fix,
        path_get_point_x(path_asignado, _i) - x,
        path_get_point_y(path_asignado, _i) - y);
}

physics_fixture_set_density(_fix, 0);
physics_fixture_set_friction(_fix, 0.05);   // carril resbaladizo: no debe frenar la bola
physics_fixture_bind(_fix, id);
physics_fixture_delete(_fix);
```

```gml
/// obj_sensor_rampa — Create (caja pequeña, densidad 0, SENSOR: detecta sin empujar)
/// rampa_id : 0..NUM_RAMPAS-1 — puesto en el Room Editor, una por instancia,
///            identifica a QUÉ carril de global.rampas_completadas pertenece.
var _fix = physics_fixture_create();
physics_fixture_set_box_shape(_fix, 10, 10);
physics_fixture_set_sensor(_fix, true);
physics_fixture_set_density(_fix, 0);
physics_fixture_bind(_fix, id);
physics_fixture_delete(_fix);

/// obj_sensor_rampa — Collision con obj_bola_pinball
pinball_rampa_completar(rampa_id, other);   // puntúa, activa multibolas si toca, VFX (04 · 39)
```

```gml
#macro NUM_RAMPAS  3   // cuántos carriles/rampas tiene la mesa

/// obj_mesa_pinball — Create
global.rampas_completadas = array_create(NUM_RAMPAS, false);

/// @func pinball_rampa_completar(_rampa_id, _bola)
/// @desc Puntúa el carril y comprueba si ya se completaron todos los que hacen
///       falta para el multibolas. `_bola` no se usa todavía aquí (queda
///       disponible para un futuro combo "misma bola, todas las rampas
///       seguidas" — un gancho de diseño, no una obligación de este documento).
function pinball_rampa_completar(_rampa_id, _bola)
{
    global.puntuacion += 500;
    global.rampas_completadas[_rampa_id] = true;

    var _completo = true;
    for (var _i = 0; _i < array_length(global.rampas_completadas); _i++)
    {
        if (!global.rampas_completadas[_i]) { _completo = false; break; }
    }
    if (_completo) pinball_activar_multibolas(2);
}
```

### B.2.5 · Multibolas

Nada nuevo: instanciar más bolas físicas y lanzarlas con un impulso desde el *kicker* de salida.

```gml
/// @func pinball_activar_multibolas(_cantidad)
function pinball_activar_multibolas(_cantidad)
{
    repeat (_cantidad)
    {
        var _b = instance_create_layer(global.kicker_x, global.kicker_y, "Instancias", obj_bola_pinball);
        with (_b)
        {
            phy_bullet = true;   // §B.2.6 — sale disparada, puede ir muy rápido
            physics_apply_impulse(phy_position_x, phy_position_y, 0, -irandom_range(15, 20));
        }
    }
}
```

### B.2.6 · *Tilt*

```gml
#macro TILT_VENTANA_FRAMES   90     // ~1,5 s a 60 fps: cuánto tarda en "olvidarse" un empujón
#macro TILT_MAX_EMPUJONES    3
#macro TILT_EMPUJE           6

/// obj_mesa_pinball — Create
empujones   = 0;
tilt_activo = false;

/// obj_mesa_pinball — Step
if (keyboard_check_pressed(vk_shift) && !tilt_activo)
{
    empujones += 1;
    alarm[0] = TILT_VENTANA_FRAMES;   // si no se repite antes de que expire, se perdona

    with (obj_bola_pinball)
    {
        physics_apply_impulse(phy_position_x, phy_position_y,
                               irandom_range(-TILT_EMPUJE, TILT_EMPUJE), -TILT_EMPUJE * 0.5);
    }

    if (empujones >= TILT_MAX_EMPUJONES)
    {
        tilt_activo = true;
        with (obj_flipper_izq) { physics_joint_set_value(junta, phy_joint_motor_speed, 0); }
        with (obj_flipper_der) { physics_joint_set_value(junta, phy_joint_motor_speed, 0); }
        // regla clásica: además, esta bola deja de puntuar hasta que se pierde
    }
}

/// obj_mesa_pinball — Alarm 0
empujones = 0;
```

### B.2.7 · Colisión continua frente a discreta: la bola que atraviesa la pared

A alta velocidad (justo después de un buen golpe de *flipper*), una bola puede recorrer más
distancia en un solo paso de física que el grosor de una pared — y como el motor solo comprueba
colisiones en instantes discretos, puede terminar el paso ya al otro lado sin haber "tocado"
nunca la pared en ningún instante comprobado. Es el mismo fenómeno del túnel que `13 · 08` §3.3
resuelve a mano subdividiendo el movimiento; en Box2D la solución es la variable pensada
exactamente para esto:

```gml
/// obj_bola_pinball — Create
phy_bullet = true;   // activa colisión CONTINUA para esta fixture: más cara de calcular,
                      // pero GameMaker la reserva para instancias rápidas por algo (04 · 22
                      // no la usa porque un puzzle físico normal no la necesita)
```

Dos refuerzos adicionales, solo si `phy_bullet` no basta con paredes muy finas:

```gml
/// obj_mesa_pinball — Create
physics_world_update_speed(120);   // el mundo físico se actualiza el DOBLE de veces por
                                     // segundo que la room (60): cada actualización mueve la
                                     // bola la mitad de distancia, así que hay más
                                     // oportunidades de detectar el contacto
```

> 🔺 **La pared en sí también importa.** Una pared de 2 px de grosor es más fácil de atravesar
> que una de 12 px, con o sin `phy_bullet`. La regla práctica: el grosor mínimo de cualquier
> muro debe ser mayor que la distancia que la bola más rápida del juego recorre en un solo paso
> de física — súbelo si ves que la bola "salta" una pared concreta en pruebas.

## B.3 · Minigolf

### B.3.1 · Arrastrar y soltar para apuntar, con previsualización

Mismo patrón de arrastre que el billar (§B.1.4): la potencia sale de la distancia arrastrada, la
dirección de apuntado es la inversa. La diferencia es que aquí SÍ hace falta previsualizar la
trayectoria completa, porque el terreno (pendientes, §B.3.3) puede curvarla de forma que una
simple flecha recta no representa dónde va a acabar la bola.

```gml
#macro MINIGOLF_FRICCION   0.965   // hierba: frena más que el paño de billar
#macro MINIGOLF_UMBRAL_PARADA 0.04
#macro MINIGOLF_PASOS_PREVIEW 90   // cuántos pasos se simulan hacia delante para dibujar la línea
#macro MINIGOLF_POTENCIA_MAX  12   // rapidez máxima del golpe, en píxeles/paso
#macro MINIGOLF_VELOCIDAD_MAX_EMBOCAR 3   // por encima de esto, la bola "salta" el hoyo (§B.3.5)
```

```gml
/// obj_bola_minigolf — Create
vel_x = 0;
vel_y = 0;
golpes = 0;
turno_jugador     = true;
arrastre_activo   = false;
arrastre_x        = 0;
arrastre_y        = 0;
mostrar_apuntado  = false;   // leído en Draw — el arrastre se CALCULA en Step
linea_previsualizada = [];
vx_prueba = 0;
vy_prueba = 0;
```

```gml
/// @func trayectoria_previsualizar(_bola_x, _bola_y, _vel_x, _vel_y)
/// @desc Simula la fricción, la pendiente (§B.3.3) y el viento (§B.3.4) hacia
///       delante SIN mover la bola real — un "fantasma" de la simulación de
///       verdad, con el mismo código que corre en el Step (§B.3.2), para que
///       la previsualización nunca mienta sobre dónde va a acabar el golpe.
/// @returns {Array<Real>} pares [x0,y0, x1,y1, ...] listos para draw_line en cadena
function trayectoria_previsualizar(_bola_x, _bola_y, _vel_x, _vel_y)
{
    var _puntos = array_create((MINIGOLF_PASOS_PREVIEW + 1) * 2);
    var _px = _bola_x, _py = _bola_y;
    var _vx = _vel_x,  _vy = _vel_y;
    _puntos[0] = _px; _puntos[1] = _py;

    var _n = 1;
    for (var _i = 0; _i < MINIGOLF_PASOS_PREVIEW; _i++)
    {
        var _pendiente = terreno_pendiente_en(_px, _py);        // §B.3.3
        _vx = (_vx + _pendiente.x + global.viento_x) * MINIGOLF_FRICCION;
        _vy = (_vy + _pendiente.y + global.viento_y) * MINIGOLF_FRICCION;
        _px += _vx;
        _py += _vy;

        _puntos[_n * 2]     = _px;
        _puntos[_n * 2 + 1] = _py;
        _n += 1;

        if (point_distance(0, 0, _vx, _vy) < MINIGOLF_UMBRAL_PARADA) break;
    }
    return puntos_recortar(_puntos, _n * 2);   // recorta el sobrante si paró antes de los 90 pasos
}

/// @func puntos_recortar(_array, _tam)
/// @desc Copia los primeros `_tam` elementos — GML no recorta arrays in-place
///       más allá de reasignar la longitud, así que se reconstruye.
/// @returns {Array}
function puntos_recortar(_array, _tam)
{
    var _r = array_create(_tam);
    for (var _i = 0; _i < _tam; _i++) _r[_i] = _array[_i];
    return _r;
}
```

```gml
/// obj_bola_minigolf — Step, con la bola parada y en turno del jugador.
/// SOLO calcula; el dibujado de la línea va en el evento Draw, más abajo.
mostrar_apuntado = false;

if (turno_jugador && point_distance(0, 0, vel_x, vel_y) < MINIGOLF_UMBRAL_PARADA)
{
    if (mouse_check_button_pressed(mb_left)) { arrastre_activo = true; arrastre_x = mouse_x; arrastre_y = mouse_y; }

    if (arrastre_activo)
    {
        var _dx = arrastre_x - mouse_x;
        var _dy = arrastre_y - mouse_y;
        var _potencia  = clamp(point_distance(0, 0, _dx, _dy) * 0.05, 0, MINIGOLF_POTENCIA_MAX);
        var _direccion = point_direction(0, 0, _dx, _dy);
        vx_prueba = lengthdir_x(_potencia, _direccion);
        vy_prueba = lengthdir_y(_potencia, _direccion);

        linea_previsualizada = trayectoria_previsualizar(x, y, vx_prueba, vy_prueba);
        mostrar_apuntado = true;

        if (mouse_check_button_released(mb_left))
        {
            vel_x = vx_prueba;
            vel_y = vy_prueba;
            golpes += 1;
            arrastre_activo  = false;
            mostrar_apuntado = false;
        }
    }
}
```

```gml
/// obj_bola_minigolf — Draw
draw_self();
if (mostrar_apuntado)
{
    for (var _i = 0; _i < array_length(linea_previsualizada) - 2; _i += 2)
    {
        draw_line(linea_previsualizada[_i], linea_previsualizada[_i + 1],
                  linea_previsualizada[_i + 2], linea_previsualizada[_i + 3]);
    }
}
```

### B.3.2 · Rodar hasta detenerse

```gml
/// obj_muro_minigolf — variables por instancia, puestas en el Room Editor:
///   normal_x, normal_y : la normal de ESTE tramo de valla, normalizada —
///   cada tramo declara hacia dónde rebota, igual que una banda de billar.

/// obj_bola_minigolf — Step, mientras se mueve
if (point_distance(0, 0, vel_x, vel_y) >= MINIGOLF_UMBRAL_PARADA)
{
    var _pendiente = terreno_pendiente_en(x, y);
    vel_x = (vel_x + _pendiente.x + global.viento_x) * MINIGOLF_FRICCION;
    vel_y = (vel_y + _pendiente.y + global.viento_y) * MINIGOLF_FRICCION;

    // Barrido en sub-pasos para no atravesar un muro fino a un golpe fuerte
    // (13 · 08 §3.3, avanzar_barrido) — no se repite el código, solo se llama.
    // avanzar_barrido() solo dice SI chocó, no con qué normal: se recupera el
    // muro concreto justo donde paró, con un pequeño empujón en la dirección
    // en la que se venía moviendo.
    var _choco = avanzar_barrido(vel_x, vel_y, obj_muro_minigolf, 6);
    if (_choco)
    {
        var _muro = instance_place(x + sign(vel_x), y + sign(vel_y), obj_muro_minigolf);
        if (_muro != noone)
        {
            var _r = rebotar_vector(vel_x, vel_y, _muro.normal_x, _muro.normal_y, 0.5);   // 13 · 08 §7.1
            vel_x = _r[0];
            vel_y = _r[1];
        }
    }
}
else
{
    vel_x = 0;
    vel_y = 0;
}
```

### B.3.3 · Pendientes del terreno

Mismo patrón de zona que `obj_zona_altura` de `04 · 46` §3.8 — un objeto invisible estirado en
el Room Editor sobre el trozo de césped inclinado, con dos variables en vez de una:

```gml
/// obj_zona_pendiente — objeto invisible, estirado en el Room Editor
/// Variables (una por zona, puestas en el editor):
///   pendiente_dir    : 0     — dirección cuesta abajo, en grados
///   pendiente_fuerza : 0.06  — aceleración que aplica, por paso

/// @func terreno_pendiente_en(_x, _y)
/// @desc Suma la aceleración de TODAS las zonas de pendiente que cubren el
///       punto — normalmente solo una, pero permite superponer una pendiente
///       suave general con una rampa más pronunciada en un tramo concreto.
/// @returns {Struct} { x, y } — aceleración a sumar a la velocidad, no una posición
function terreno_pendiente_en(_x, _y)
{
    var _ax = 0, _ay = 0;
    with (obj_zona_pendiente)
    {
        if (point_in_rectangle(_x, _y, bbox_left, bbox_top, bbox_right, bbox_bottom))
        {
            _ax += lengthdir_x(pendiente_fuerza, pendiente_dir);
            _ay += lengthdir_y(pendiente_fuerza, pendiente_dir);
        }
    }
    return { x: _ax, y: _ay };
}
```

### B.3.4 · Viento

Una fuerza constante, global, que se suma exactamente en el mismo punto que la pendiente (§B.3.2
y la previsualización de §B.3.1 ya lo hacen) — así que no hace falta tocar nada más para que el
viento afecte tanto al golpe real como a la línea previsualizada:

```gml
/// obj_control_hoyo — Create (o al empezar cada hoyo, si el viento cambia por hoyo)
global.viento_x = lengthdir_x(0.015, irandom_range(0, 359));
global.viento_y = lengthdir_y(0.015, irandom_range(0, 359));
```

> 💡 **El viento debe ser mucho más débil que la pendiente típica** (aquí 0,015 frente a 0,06):
> si el viento domina, el jugador deja de sentir que apunta el golpe y empieza a sentir que
> "corrige" una fuerza externa constante — es un ajuste de diseño, pero esta proporción de
> partida no se siente injusta.

### B.3.5 · El hoyo

```gml
/// obj_hoyo — Create
radio = 8;

/// obj_control_hoyo — Step
with (obj_bola_minigolf)
{
    var _h = instance_nearest(x, y, obj_hoyo);
    if (_h != noone && point_distance(x, y, _h.x, _h.y) < _h.radio)
    {
        // Regla real del golf/minigolf: demasiado rápida, y la bola "salta"
        // el hoyo en vez de caer — no toda bola que pasa por encima entra.
        if (point_distance(0, 0, vel_x, vel_y) < MINIGOLF_VELOCIDAD_MAX_EMBOCAR)
        {
            minigolf_hoyo_completado(golpes);
            instance_destroy();
        }
    }
}
```

```gml
/// obj_control_hoyo — Create
global.resultados_hoyos = [];
global.hoyo_actual      = 0;

/// @func minigolf_hoyo_completado(_golpes)
/// @desc Registra el resultado del hoyo actual y avanza al siguiente. La
///       transición de escena en sí (cargar el siguiente `Room`, animación de
///       "¡hoyo en uno!") es del juego concreto, no de este documento.
function minigolf_hoyo_completado(_golpes)
{
    array_push(global.resultados_hoyos, _golpes);
    global.hoyo_actual += 1;
}
```

---

## Checklist

- [ ] El balón es una instancia con `estado` (`libre`/`poseido`/`en_vuelo`), nunca una posición
      calculada a partir del jugador — todo lo demás (robo, pase, tiro) depende de eso.
- [ ] El pase con anticipación apunta a `balon_punto_de_encuentro()`, no a la posición actual
      del receptor — si tus pases llegan tarde a un compañero en movimiento, revisa esto primero.
- [ ] El efecto (curva) del disparo, del billar y del pase alto usan el mismo mecanismo: rotar
      el vector de velocidad y dejar que decaiga solo — nunca sumar una fuerza lateral aparte.
- [ ] El fuera de juego se comprueba UNA VEZ, en el instante del pase — nunca cada Step.
- [ ] El desplazamiento de bloque (`formacion_posicion_objetivo`) mueve a TODO el equipo hacia
      el balón, no solo al jugador más cercano — si el equipo se ve descoordinado, revisa que
      todos lean el mismo `global.balon.x`/`y` en el mismo Step.
- [ ] El reloj del partido usa `delta_time`, nunca un contador de frames a secas — si el reloj
      corre distinto a 30 y a 144 fps, es esto.
- [ ] `colisionar_circulos_elastico()` separa el solapamiento ANTES de tocar la velocidad — si
      dos bolas de billar "vibran" pegadas, falta ese paso.
- [ ] Los *flippers* de pinball usan `physics_joint_revolute_create` con límites de ángulo — sin
      `ang_limit = true`, el flipper da la vuelta entera en vez de quedarse en su recorrido.
- [ ] `phy_bullet = true` en toda bola de pinball que pueda salir disparada por un *flipper* —
      sin esto, a velocidad alta puede atravesar una pared fina.
- [ ] La previsualización de minigolf llama a la MISMA función que el movimiento real
      (`trayectoria_previsualizar` reutiliza `terreno_pendiente_en`/fricción/viento) — si tienes
      dos copias del cálculo, un día divergen y la línea empieza a mentir.

---

## Errores clásicos y cómo evitarlos

| Error | Síntoma | Arreglo |
|---|---|---|
| Pase sin anticipación a un receptor en movimiento | El balón llega siempre "detrás" del compañero, se ve torpe | `balon_punto_de_encuentro()` antes de fijar la dirección (§A.3.1) |
| Comprobar el fuera de juego cada Step | Se pita fuera de juego a un delantero parado, sin que nadie le haya pasado nada | Comprobarlo solo en el instante del pase (§A.6.3) |
| El desplazamiento de bloque no usa la posición del balón del mismo frame | El equipo se ve "elástico", con jugadores tirando cada uno hacia un lado | Todos deben leer `global.balon.x`/`y`, no una copia cacheada de otro frame |
| Reloj de partido basado en frames (`segundos += 1/60`) | El partido dura distinto según el framerate real | `delta_time` (§A.7), el mismo patrón que `13 · 08` §1.3 |
| Resolver el choque de billar solo con `rebotar_vector()` (pensado para UNA pared fija) | Las dos bolas rebotan como si una de ellas no se moviera, el momento no se conserva | `colisionar_circulos_elastico()` (§B.1.1): reparte la velocidad entre las DOS |
| No separar el solapamiento antes de resolver la velocidad en el choque de bolas | Dos bolas quedan "pegadas", vibrando, chocando cada frame | El paso 1 de `colisionar_circulos_elastico()` — nunca se puede saltar |
| *Flipper* sin límites de ángulo en el joint | Da la vuelta entera en vez de quedarse en su recorrido de golpeo | `ang_limit = true` con `ang_min_limit`/`ang_max_limit` puestos (§B.2.2) |
| Pinball sin `phy_bullet` en la bola | La bola atraviesa una pared fina tras un golpe fuerte de flipper | `phy_bullet = true` (§B.2.7), y comprobar el grosor real de las paredes |
| Previsualización de minigolf con su propia copia de la física | La línea dibujada no coincide con dónde acaba realmente la bola | Una sola función de simulación, llamada por el preview Y por el Step real (§B.3.1) |
| Viento más fuerte que la pendiente típica | El jugador deja de sentir que controla el golpe | Mantén el viento un orden de magnitud por debajo de la pendiente (§B.3.4) |

---

## Ver también

- [04 · 46 — Eje Z falso](./46%20-%20Eje%20Z%20falso%20-%20altura%2C%20sombras%20y%20profundidad%20en%20un%20juego%202D.md) —
  el arco vertical (`z`/`zvel`, `sombra_dibujar`) que el pase alto y el tiro (§A.3.2, §A.4)
  reutilizan sin repetirlo.
- [04 · 22 — Físicas con Box2D](./22%20-%20Físicas%20con%20Box2D.md) — el mundo físico, las
  fixtures, los joints y las variables `phy_*` que el pinball (§B.2) usa desde la base.
- [13 · 08 — Físicas a mano y fluidos](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/08%20-%20Físicas%20a%20mano%20y%20fluidos.md) —
  Euler semi-implícito, `delta_time`, `solapan_circulos()`, `rebotar_vector()`, el barrido contra
  el túnel: la base sobre la que se construye todo `B.1` y `B.3`.
- [04 · 33 — Diseño de enemigos, encuentros y director de combate](./33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md) —
  `GestorFichas`, reutilizado en §A.5.4 para la presión sin que todo el equipo rival ataque a la
  vez.
- [04 · 23 — IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) —
  `Arrive` (§2) y `Seek`/`Flee` (§1), usados en §A.5.2 y §A.5.5 para el movimiento de formación
  y el desmarque.
- [04 · 47 — Beat 'em up y brawler](./47%20-%20Beat%20em%20up%20y%20brawler.md) — otro ejemplo ya
  escrito de instanciar `GestorFichas` con radios propios del género, el mismo patrón que §A.5.4.
- [04 · 30 — Combate cuerpo a cuerpo](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) —
  por qué robar el balón (§A.2.1) NO usa este sistema: no hay hitboxes, solo una probabilidad
  de entrada.
- [13 · 13 — Matemáticas aplicadas al juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md) §2.7 —
  reflexión de un vector contra una pared, la base matemática que `rebotar_vector()` de `13 · 08`
  implementa y que este documento reutiliza sin repetir la deducción.

---

## Fuentes

- Manual oficial de GameMaker — `physics_joint_revolute_create`, `physics_fixture_set_chain_shape`,
  `physics_fixture_set_sensor`, `physics_fixture_add_point`, `phy_bullet`,
  `physics_world_update_speed`, `path_get_point_x`/`path_get_point_y`, `array_sort`,
  `mouse_check_button_released`, `delta_time` — `09 - Manual oficial/manual-lts-2026-es/`
  (espejo local, consultado 2026-09-07).
- «Elastic collision» (colisión elástica 1D con coeficiente de restitución, descompuesta sobre
  la normal de impacto), Wikipedia — la deducción estándar que `colisionar_circulos_elastico()`
  implementa; contrastada contra el caso límite de masas iguales (intercambio de velocidad
  normal), que es el resultado que cualquier jugador de billar reconoce a simple vista.
- El propio código verificado de esta biblioteca en `04 · 46` (eje Z falso), `04 · 22` (Box2D),
  `13 · 08` (físicas a mano), `04 · 33` (`GestorFichas`) y `04 · 23` (`Arrive`/`Seek`/`Flee`),
  usados aquí como base sin duplicar su contenido — es la fuente primaria más fiable de todas:
  ya compiló antes de escribirse este documento.
