# 48 · Aventura gráfica y point and click

> **Dificultad:** media · *Monkey Island*, *Day of the Tentacle*, *Machinarium*, *Thimbleweed
> Park*. El género de señalar y hacer clic: hotspots, verbos, caminar hasta el sitio correcto,
> combinar objetos y no dejar nunca al jugador atascado sin salida. Cobertura previa: **cero** —
> verificado con `buscar.py --texto "point and click"` y `--texto "aventura gráfica"` antes de
> escribir este documento.
> **No cubre**: los diálogos ramificados y sus flags (eso es
> [`13 · 12`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/12%20-%20Diseño%20narrativo%20y%20diálogos.md),
> que este documento reutiliza sin repetir), el diseño de los propios puzzles — qué objeto hace
> falta para qué candado — (eso es
> [`13 · 17`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/17%20-%20Diseño%20de%20puzzles.md)),
> la mecánica general de guardado (eso es
> [`13 · 06`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md)
> §3.10), ni el pathfinding sobre rejilla —
> [`04 · 38`](./38%20-%20Pathfinding%20avanzado%20-%20flow%20fields%2C%20JPS%20y%20plataformas.md)
> va sobre `mp_grid`, celdas y unidades que se evitan entre sí; una aventura gráfica no tiene
> rejilla, tiene un **polígono de suelo continuo**, y ese algoritmo sí es de este documento.

---

## 1 · Los principios

### 1.1 · Qué hace distinto a este género

Un point and click no tiene un "personaje que se controla": tiene un **mundo que se señala**. La
diferencia no es cosmética, cambia qué sistemas hacen falta:

| En un juego de acción | En una aventura gráfica |
|---|---|
| El jugador mueve al personaje con teclado/mando, fotograma a fotograma | El jugador señala un punto o un objeto; el personaje decide cómo llegar |
| La interacción es "tocar = pasa algo" (colisión) | La interacción es "señalar + elegir qué hacer" (verbo) |
| El estado del mundo es casi todo numérico (HP, munición) | El estado del mundo es casi todo **booleano y narrativo** (¿está abierta la puerta?, ¿ya hablé con el guardia?) |
| Perder es habitual y se espera que perder | Perder de verdad (sin poder continuar) es, en el diseño moderno del género, **un fallo de diseño** — ver §1.4 |

Esto convierte a la aventura gráfica en el género donde la **interfaz de entrada** (§2) y la
**gestión de estado** (§3.8) pesan tanto como el propio movimiento, y donde el fallo más caro no
es un enemigo difícil sino un jugador que, sin saberlo, ya no puede ganar (§3.11).

### 1.2 · Los ocho sistemas de este documento, y qué reutiliza cada uno

| Sistema | Qué resuelve aquí | Reutiliza de |
|---|---|---|
| Hotspots y cursor contextual | Qué hay bajo el ratón y qué verbo le corresponde | Sistema nuevo — §3.1-§3.3 |
| Interfaz de verbos | Cómo el jugador dice "quiero hacer X con Y" | Sistema nuevo — §3.4 |
| *Walk-to* poligonal | Llevar al personaje al punto pulsado sin rejilla | Sistema nuevo — §3.5. Contraste explícito con `04 · 38` (rejilla) |
| Escalado por profundidad | El personaje encoge al fondo de la sala | Variante de `04 · 47` §3.3 (banda de brawler), adaptada a una sala completa |
| Inventario combinatorio | Usar A con B, examinar, arrastrar | Sistema nuevo — §3.7 |
| Estado del mundo | Banderas de historia frente a estado de un objeto concreto | `13 · 12` §6.2 (`flag_*`) reutilizado tal cual + registro nuevo por objeto — §3.8 |
| Guardado | Qué entra en el fichero de esta partida | `13 · 06` §3.10 (arquitectura), `01 · 14` (sandbox), reutilizados sin repetir — §3.9 |
| Escenas y guion | Cinemáticas cortas con el control quitado y devuelto | `13 · 12` §6.6 (`Cinematica`), extendido con dos pasos nuevos — §3.10 |

### 1.3 · Tres interfaces de verbos, y cuál se implementa aquí

La pregunta "¿cómo le dice el jugador al motor qué quiere hacer?" tiene tres respuestas
históricas, con presupuestos de producción muy distintos:

| Interfaz | Ejemplos | Verbos típicos | A favor | En contra |
|---|---|---|---|---|
| **Nueve verbos (SCUMM clásico)** | *Maniac Mansion*, *Monkey Island 1-2*, *Day of the Tentacle* | Coger, Abrir, Cerrar, Empujar, Tirar de, Dar, Usar, Mirar, Hablar con | Máxima expresividad — probar el verbo "equivocado" es a menudo un chiste escrito a propósito. Nunca hay ambigüedad sobre qué se pidió | Una barra entera de pantalla; la mayoría de combinaciones verbo-objeto no hacen nada y eso frustra sin querer; hay que escribir una respuesta para cada verbo en cada objeto o se nota el hueco |
| **Dos botones (izquierdo usar, derecho mirar)** | *Full Throttle*, *The Dig*, *Blade Runner*, gran parte de las aventuras de LucasArts de mediados de los 90 | *Usar* (contextual: coger/hablar/abrir/tirar según el objeto) + *Mirar* | Rápido de aprender, cabe en cualquier pantalla, se traduce sin fricción a un mando (dos botones) o a una pantalla táctil (tocar/mantener) | El motor tiene que decidir un único verbo "correcto" por objeto; si dos acciones son igual de válidas, una gana y la otra desaparece |
| **Un botón + rueda contextual** | *Machinarium* (sin verbos, un único cursor icónico), *Thimbleweed Park* (además de los 9 clásicos, un modo simplificado) | Un clic simple hace la acción evidente; mantener pulsado despliega solo los verbos que ESE objeto admite | El más limpio en móvil; cero verbos muertos, porque la rueda nunca ofrece uno que no aplique | Cada objeto debe declarar su propia lista de verbos válidos; una rueda mal calibrada puede esconder una acción que el jugador ni sabe buscar |

**Recomendación de este documento, y por qué**: **dos botones**, implementado completo en §3.4.
Nueve verbos multiplican por nueve el trabajo de escritura de respuestas sin multiplicar la
diversión en la misma proporción para un equipo pequeño o en solitario. La rueda de un botón es
la mejor opción en móvil, pero exige que cada hotspot declare su lista de verbos válidos desde el
primer día — una disciplina de datos que rara vez compensa en un proyecto que quiere shippear
pronto. Dos botones da toda la expresividad que casi cualquier juego necesita, con una
responsabilidad clara: izquierdo actúa, derecho informa.

### 1.4 · La regla de oro, adelantada

Se desarrolla entera en §3.11, pero condiciona TODO lo demás, así que va aquí primero: **una
aventura gráfica bien diseñada se puede terminar de principio a fin sin morir ni tener que
cargar una partida**, y sin que el jugador pueda quedarse sin poder ganar por haber tomado una
decisión razonable. Es la primera de las reglas que Ron Gilbert escribió en 1989 mientras
diseñaba el primer *Monkey Island* — «*Live and learn*» — y sigue siendo, casi cuarenta años
después, el consenso de diseño del género: un *softlock* no es una trampa ingeniosa, es un
defecto de guion que el jugador nunca debería tener que descubrir por las malas.

---

## 2 · El método, paso a paso

```
1. Hotspots: define QUÉ es interactivo en cada sala y con qué prioridad (§3.1).
2. Cursor: un cursor contextual + etiqueta de nombre bajo el ratón (§3.2-§3.3).
3. Verbos: dos botones — usar (contextual) y mirar (§3.4).
4. Walkboxes: el polígono de suelo de la sala, con sus conexiones a las salas vecinas (§3.5).
5. Walk-to: BFS sobre el grafo de walkboxes + waypoints por el borde compartido (§3.5.3-3.5.4).
6. Encolar la acción: "ve allí Y ENTONCES actúa" — una variable, no una cinemática (§3.5.5).
7. Escalado por profundidad, si la sala tiene perspectiva (§3.6).
8. Inventario: catálogo de objetos, combinaciones, arrastrar y examinar (§3.7).
9. Estado del mundo: banderas globales + registro por objeto (§3.8), y qué va al guardado (§3.9).
10. Escenas: cinemáticas cortas reutilizando el motor de cola de 13 · 12 (§3.10).
11. Antes de dar el nivel por cerrado: pasa la sala por la regla de oro (§3.11).
```

Cada paso depende del anterior — no hay atajos razonables: un cursor contextual sin hotspots no
tiene nada que leer, y un inventario combinatorio sin estado del mundo no puede recordar qué ya
se combinó.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 · Hotspots: tres formas de marcar una zona interactiva

Un *hotspot* es "un sitio donde el clic significa algo". Hay tres formas de definirlo, y la
elección depende de si el objeto tiene sprite propio o es solo una zona pintada en el fondo:

| Técnica | Cuándo usarla | Coste |
|---|---|---|
| **Por objeto (bounding box)** | El objeto tiene sprite propio y su forma es más o menos rectangular (una caja, un cartel) | El más barato: `instance_position` contra el objeto de sobra |
| **Por máscara (precisa)** | El objeto tiene sprite propio, pero su silueta no es rectangular (una estatua, un árbol) y clicar el aire de la esquina no debería contar | Un cambio en el Sprite Editor (`bboxkind_precise`, `01 · 08`) — el propio motor calcula el contorno |
| **Por polígono (invisible)** | No hay sprite: el hotspot es "la ventana pintada en el fondo" o "ese tramo de la barandilla" | Un polígono a mano, con el mismo test que el *walkbox* del §3.5 — se reutiliza la misma función |

```gml
/// obj_hotspot — objeto PADRE de cualquier cosa interactiva de la sala: una
/// puerta, un NPC, un objeto del suelo, una zona sin sprite. Las variables
/// se ponen en el Creation Code de cada instancia, en el Room Editor.

/// obj_hotspot — Create
nombre_mostrado   = "el objeto";   // lo que lee la etiqueta (§3.3) y la línea de frase (§3.4.4)
prioridad         = 0;             // más alto gana si dos hotspots se solapan (§3.2.3)
punto_de_pie_x    = x;             // dónde se PARA el jugador para poder usar este hotspot
punto_de_pie_y    = y + 12;        // (por defecto, justo debajo del propio hotspot)
verbo_por_defecto = "mirar";       // qué cursor mostrar cuando el ratón pasa por encima (§3.2.2)
usa_poligono      = false;         // true si es un hotspot SIN sprite (§3.1, fila 3)
vertices_poligono  = [];           // solo si usa_poligono == true

/// Cada hotspot concreto sobrescribe estos dos métodos DESPUÉS de llamar a
/// event_inherited() en su propio Create. El valor devuelto es el texto de
/// la línea de frase (§3.4.4), o `undefined` si el verbo ya "habló por sí
/// mismo" (p.ej. cambiar de sala, §3.5.6).
verbo_usar  = function() { return respuesta_por_defecto("usar",  nombre_mostrado); };
verbo_mirar = function() { return respuesta_por_defecto("mirar", nombre_mostrado); };
```

```gml
/// @func poligono_caja(_vertices)
/// @desc Caja delimitadora (izq/arriba/der/abajo) de un polígono. La usan
///       tanto el resaltado de hotspots (§3.3) como el desempate por área en
///       el solapado de prioridad (§3.2.3) — un solo cálculo, dos usos.
/// @param {Array} _vertices  Array de [x,y].
/// @returns {Struct}
function poligono_caja(_vertices)
{
    var _izq = infinity, _der = -infinity, _arr = infinity, _aba = -infinity;
    for (var _i = 0; _i < array_length(_vertices); _i++)
    {
        var _vx = _vertices[_i][0];
        var _vy = _vertices[_i][1];
        _izq = min(_izq, _vx);  _der = max(_der, _vx);
        _arr = min(_arr, _vy);  _aba = max(_aba, _vy);
    }
    return { izq: _izq, arriba: _arr, der: _der, abajo: _aba };
}
```

### 3.2 · Cursor contextual, etiqueta y prioridad

#### 3.2.1 · Qué hotspot hay bajo el cursor

```gml
// ---------------------------------------------------------------------------
// scr_aventura_hotspots
// ---------------------------------------------------------------------------

/// @func punto_en_poligono(_px, _py, _vertices)
/// @desc Ray casting par-impar (el algoritmo estándar de "point in polygon",
///       PNPOLY de W. Randolph Franklin): cuenta cuántas veces un rayo
///       horizontal hacia la derecha desde (_px,_py) cruza los bordes del
///       polígono. Un número impar de cruces significa que el punto está
///       dentro. Sirve para CUALQUIER polígono simple, convexo o no —
///       GameMaker no trae ninguna función equivalente (verificado:
///       `point_in_polygon` y `collision_polygon` no existen en el runtime).
/// @param {Real}  _px
/// @param {Real}  _py
/// @param {Array} _vertices  Array de [x,y] en el orden en que se recorre el borde.
/// @returns {Bool}
function punto_en_poligono(_px, _py, _vertices)
{
    var _n = array_length(_vertices);
    var _dentro = false;
    var _j = _n - 1;

    for (var _i = 0; _i < _n; _i++)
    {
        var _xi = _vertices[_i][0], _yi = _vertices[_i][1];
        var _xj = _vertices[_j][0], _yj = _vertices[_j][1];

        if (((_yi > _py) != (_yj > _py)) &&
            (_px < (_xj - _xi) * (_py - _yi) / (_yj - _yi) + _xi))
        {
            _dentro = !_dentro;
        }
        _j = _i;
    }
    return _dentro;
}

/// @func hotspot_bajo_cursor()
/// @desc El hotspot que debe responder al clic ahora mismo. Reúne TODOS los
///       candidatos (por máscara y por polígono) y desempata por prioridad
///       explícita y, si empatan, por área — el más pequeño gana, porque es
///       el más específico (una llave encima de una mesa: gana la llave).
/// @returns {Id.Instance}  o `noone` si no hay nada bajo el cursor.
function hotspot_bajo_cursor()
{
    var _mejor       = noone;
    var _mejor_prio   = -infinity;
    var _mejor_area   = infinity;

    // Candidatos CON sprite (por objeto o por máscara — instance_position ya
    // respeta bboxkind_precise si el hotspot lo tiene activado, 01 · 08).
    with (obj_hotspot)
    {
        if (usa_poligono) continue;   // esos se prueban aparte, más abajo
        if (!instance_position(mouse_x, mouse_y, id)) continue;

        var _area = (bbox_right - bbox_left) * (bbox_bottom - bbox_top);
        if (prioridad > _mejor_prio || (prioridad == _mejor_prio && _area < _mejor_area))
        {
            _mejor = id; _mejor_prio = prioridad; _mejor_area = _area;
        }
    }

    // Candidatos SIN sprite (polígono a mano, §3.1 fila 3) — misma regla de
    // desempate, reutilizando poligono_caja() para el área.
    with (obj_hotspot)
    {
        if (!usa_poligono) continue;
        if (!punto_en_poligono(mouse_x, mouse_y, vertices_poligono)) continue;

        var _caja = poligono_caja(vertices_poligono);
        var _area = (_caja.der - _caja.izq) * (_caja.abajo - _caja.arriba);
        if (prioridad > _mejor_prio || (prioridad == _mejor_prio && _area < _mejor_area))
        {
            _mejor = id; _mejor_prio = prioridad; _mejor_area = _area;
        }
    }

    return _mejor;
}
```

> 🔺 **La regla de desempate en una frase**: gana la prioridad explícita si alguien la puso; si
> no, gana el hotspot más pequeño. Es la razón de que una llave diminuta encima de una mesa
> grande siga siendo clicable: si ganara el más grande, la mesa taparía cualquier objeto
> pequeño posado sobre ella para siempre.

#### 3.2.2 · Cursor contextual

```gml
/// obj_controlador_aventura — Create
window_set_cursor(cr_none);   // apaga el cursor del sistema operativo: se dibuja el propio (pixel art)

global.cursores_por_verbo = {
    mirar:   spr_cursor_mirar,
    usar:    spr_cursor_mano,
    coger:   spr_cursor_coger,
    hablar:  spr_cursor_hablar,
    caminar: spr_cursor_flecha,   // sobre suelo vacío, sin hotspot debajo
};

/// obj_controlador_aventura — Draw GUI (se dibuja SIEMPRE, encima de todo)
var _gui_x = device_mouse_x_to_gui(0);
var _gui_y = device_mouse_y_to_gui(0);
var _hs    = hotspot_bajo_cursor();
var _verbo = (_hs != noone) ? _hs.verbo_por_defecto : "caminar";

draw_sprite(global.cursores_por_verbo[$ _verbo], 0, _gui_x, _gui_y);

if (_hs != noone)
{
    draw_set_halign(fa_center);
    draw_set_valign(fa_bottom);
    draw_text_colour(_gui_x, _gui_y - 18, _hs.nombre_mostrado,
                      c_white, c_white, c_white, c_white, 1);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);
}
```

> 💡 Si tu juego no usa pixel art marcado y no te importa el cursor del sistema, la alternativa
> de una línea es la variable global `cursor_sprite` (verificada: existe, ámbito global) en vez
> de dibujar a mano en el Draw GUI — GameMaker la sustituye por el cursor del SO automáticamente.
> El dibujado manual de arriba da más control (rotación, parpadeo, verbos con icono compuesto) y
> es lo que usan la mayoría de aventuras gráficas pixel art comerciales.

### 3.3 · Resaltar todos los hotspots: la tecla que ya es estándar

Desde que las reediciones modernas de LucasArts y juegos como *Thimbleweed Park* la
popularizaron, mantener pulsada una tecla (habitualmente `Tab`) para que **todos** los hotspots
de la sala se marquen a la vez es una expectativa del jugador actual, no un lujo — sin ella,
buscar el único píxel interactivo de un fondo pintado a mano es frustración pura. ⚠️ La tecla
exacta varía de un juego a otro; `Tab` es la convención más citada y la que se usa aquí por
defecto, pero conviene dejarla reasignable en el menú de opciones (`04 · 25`).

```gml
#macro RESALTAR_HOTSPOTS_TECLA vk_tab

/// obj_hotspot — Draw (después de dibujarse a sí mismo, si el hotspot tiene sprite propio)
if (keyboard_check(RESALTAR_HOTSPOTS_TECLA))
{
    var _pulso = 0.5 + 0.5 * sin(current_time / 200);   // parpadeo suave, no una luz fija

    var _caja = usa_poligono ? poligono_caja(vertices_poligono)
                              : { izq: bbox_left, arriba: bbox_top, der: bbox_right, abajo: bbox_bottom };

    draw_set_alpha(0.35 + 0.35 * _pulso);
    draw_set_color(c_white);
    draw_rectangle(_caja.izq - 2, _caja.arriba - 2, _caja.der + 2, _caja.abajo + 2, true);
    draw_set_alpha(1);

    draw_set_halign(fa_center);
    draw_text(x, _caja.arriba - 14, nombre_mostrado);
    draw_set_halign(fa_left);
}
```

> 💡 **Alternativa con más producción**: el filtro `_filter_outline` de las FX de 2026
> (`02 - Novedades 2026/06` §4.5) da un contorno real en vez de un rectángulo — se aplica a una
> capa "Hotspots" dedicada (con `fx_set_single_layer`, para no arrastrar todo lo de abajo) que
> solo se hace visible mientras la tecla está pulsada. El rectángulo de arriba es la opción de
> coste cero; el FX es el pulido, no un sustituto necesario.

### 3.4 · Interfaz de verbos: dos botones, implementados

#### 3.4.1 · La resolución de verbo

El clic izquierdo siempre pide **usar** (contextual: cada hotspot decide qué significa "usar" —
coger, hablar, abrir); el derecho siempre pide **mirar**. Mirar nunca exige caminar hasta el
objeto — se puede examinar algo desde el otro lado de la sala, como en el género de siempre.
Usar sí exige estar en el punto de pie del hotspot, así que primero camina y luego actúa: el
mismo patrón de "ve allí Y ENTONCES…" del enunciado de este documento, resuelto en §3.5.5.

```gml
/// obj_jugador — Step (bloqueado durante una cinemática o un diálogo — 13 · 12 §6.6 y §6.9)
if (!global.cinematica_en_curso && !global.dialogo_activo)
{
    if (mouse_check_button_pressed(mb_left) || mouse_check_button_pressed(mb_right))
    {
        var _es_usar = mouse_check_button_pressed(mb_left);
        var _hs      = hotspot_bajo_cursor();

        if (_hs != noone)
        {
            if (_es_usar)
            {
                // "Usar" exige caminar hasta el punto de pie del hotspot ANTES
                // de ejecutar su verbo — se encola, no se ejecuta ya (§3.5.5).
                jugador_ir_y_actuar(id, _hs.punto_de_pie_x, _hs.punto_de_pie_y,
                                    method(_hs, _hs.verbo_usar));
            }
            else
            {
                // "Mirar" no exige caminar: responde al instante.
                var _texto = _hs.verbo_mirar();
                if (!is_undefined(_texto)) { linea_frase_mostrar(_texto); }
            }
        }
        else if (_es_usar)
        {
            // Clic en suelo vacío: solo caminar, sin acción encolada.
            jugador_ir_y_actuar(id, mouse_x, mouse_y, undefined);
        }
    }
}
```

> ⚠️ `id` como primer argumento de `jugador_ir_y_actuar` es **la variable integrada** de la
> propia instancia que llama (el jugador), no un nombre inventado — se pasa así porque §3.5
> define la función como de propósito general, útil para mover a cualquier instancia, no solo al
> jugador.

#### 3.4.2 · Respuestas por defecto que no repiten "eso no funciona"

```gml
/// @func respuesta_por_defecto(_verbo, _objeto_nombre)
/// @desc El texto de reserva cuando un hotspot NO ha sobrescrito verbo_usar/
///       verbo_mirar con algo específico. Usa siempre el nombre del objeto:
///       una frase genérica que menciona el objeto suena escrita a
///       propósito; una frase seca sin nombre suena a error del motor.
function respuesta_por_defecto(_verbo, _objeto_nombre)
{
    switch (_verbo)
    {
        case "usar":   return $"No parece que {_objeto_nombre} sirva para nada aquí.";
        case "mirar":  return $"No hay nada especial que decir sobre {_objeto_nombre}.";
        case "coger":  return $"No necesito llevarme eso.";
        case "hablar": return $"Aquí no hay nadie con quien hablar.";
        default:       return $"Eso no funciona.";
    }
}
```

Cada hotspot importante debería sobrescribir estas dos respuestas con algo propio — es donde
vive la mitad del humor de una aventura gráfica clásica. La función de arriba no es "la"
respuesta del juego: es la red de seguridad para el 80 % de los objetos de attrezzo que no
necesitan una línea escrita a mano.

#### 3.4.3 · La línea de frase

```gml
// ---------------------------------------------------------------------------
// scr_aventura_ui
// ---------------------------------------------------------------------------
#macro FRASE_DURACION_FRAMES 150   // ~2.5 s a 60 fps — tiempo de lectura, no un parpadeo

global.frase_texto  = "";
global.frase_frames = 0;

/// @func linea_frase_mostrar(_texto)
/// @desc La frase estilo SCUMM ("Mirar la puerta del taller") que confirma
///       al jugador qué acaba de pedir. Se llama desde §3.4.1 y desde
///       cualquier verbo_usar/verbo_mirar que devuelva texto.
function linea_frase_mostrar(_texto)
{
    global.frase_texto  = _texto;
    global.frase_frames = FRASE_DURACION_FRAMES;
}
```

```gml
/// obj_controlador_aventura — Step
if (global.frase_frames > 0) { global.frase_frames--; }

/// obj_controlador_aventura — Draw GUI (después del cursor, §3.2.2)
if (global.frase_frames > 0)
{
    draw_set_halign(fa_center);
    draw_set_valign(fa_top);
    draw_text_colour(display_get_gui_width() / 2, 8, global.frase_texto,
                      c_white, c_white, c_white, c_white, 1);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);
}
```

### 3.5 · *Walk-to*: llevar al personaje al punto pulsado, dentro de un polígono de suelo

Esta es la pieza central del documento, y la que **no** duplica `04 · 38`: ese documento resuelve
"muchas unidades sobre una rejilla de celdas" (campo de flujo, JPS, `mp_grid`). Aquí no hay
rejilla — hay una sala pintada a mano con un suelo de forma irregular, y el camino más natural es
una línea recta dentro de cada tramo de suelo, no una escalera de celdas.

#### 3.5.1 · El *walkbox*: un polígono de suelo, con vecinos enlazados a mano

```gml
/// obj_walkbox — objeto invisible. Cada instancia es UN tramo convexo del
/// suelo caminable de la sala. Variables puestas en el Creation Code de cada
/// instancia, en el Room Editor:

/// obj_walkbox — Create
indice     = 0;    // único DENTRO de esta room, empieza en 0 (0, 1, 2…)
vertices   = [];   // polígono del tramo de suelo, en coordenadas de room: [[x0,y0],[x1,y1],…]
conexiones = [];   // qué otras cajas tocan esta, y por QUÉ borde exacto — ver abajo

// Perspectiva opcional de esta caja (§3.6) — desactivada si escala_activa es false.
escala_activa  = false;
escala_y_lejos = 0;
escala_y_cerca = 0;
escala_min     = 0.6;
escala_max     = 1.0;
```

```gml
// Ejemplo real: dos cajas contiguas de una habitación en forma de "L" — la
// caja 0 es el tramo ancho, la caja 1 el pasillo estrecho hacia la puerta.
// Comparten el borde vertical en x=200. "caja" es el índice de la vecina;
// "p1"/"p2" son los DOS puntos que dibujan el borde COMPARTIDO — el mismo
// patrón de enlace manual que 04 · 47 §5.1 usa entre obj_arena_trigger y su
// muro_salida: nada de detección automática, el diseñador lo dice una vez.
indice     = 0;
vertices   = [[40,280], [200,280], [200,420], [40,420]];
conexiones = [ { caja: 1, p1: [200,300], p2: [200,400] } ];
```

```gml
indice     = 1;
vertices   = [[200,300], [280,300], [280,400], [200,400]];
conexiones = [ { caja: 0, p1: [200,300], p2: [200,400] } ];   // el mismo borde, del otro lado
```

> 🔺 **Por qué el borde se declara a mano y no se detecta**: dos polígonos que se tocan solo en
> parte (un pasillo estrecho que entra en una sala grande) son difíciles de resolver de forma
> genérica sin falsos positivos. Declarar el segmento compartido a mano cuesta una línea por
> conexión y es imposible de acertar mal por accidente.

Al entrar en la sala, un controlador indexa las cajas una vez, para poder ir de "índice" a
"instancia" en O(1) durante el resto de la escena:

```gml
/// @func walkboxes_indexar()
/// @desc Se llama en el Room Start de la sala, ANTES de que el jugador pueda
///       hacer clic. Construye el array indice → instancia que usa todo lo
///       demás de esta sección.
function walkboxes_indexar()
{
    var _maximo = 0;
    with (obj_walkbox) { _maximo = max(_maximo, indice); }

    global.mapa_cajas = array_create(_maximo + 1, noone);
    with (obj_walkbox) { global.mapa_cajas[indice] = id; }
}
```

#### 3.5.2 · Qué caja contiene un punto (y qué hacer si el clic cae fuera de todas)

```gml
/// @func walkbox_en_punto(_x, _y)
/// @desc La instancia de obj_walkbox que contiene el punto, o `noone` si no
///       hay ninguna — reutiliza punto_en_poligono() del §3.2.1: el mismo
///       test sirve para hotspots sin sprite y para el suelo caminable.
function walkbox_en_punto(_x, _y)
{
    var _resultado = noone;
    with (obj_walkbox)
    {
        if (_resultado == noone && punto_en_poligono(_x, _y, vertices))
        {
            _resultado = id;
        }
    }
    return _resultado;
}

/// @func punto_mas_cercano_en_segmento(_px, _py, _x1, _y1, _x2, _y2)
/// @desc Proyección vectorial estándar de un punto sobre un segmento,
///       recortada al propio segmento (parámetro t en [0, 1]). Se usa dos
///       veces en este documento: aquí, para "el jugador clicó fuera del
///       suelo, ¿cuál es el punto caminable más cercano?", y en §3.5.4, para
///       calcular por dónde cruzar de una caja a la siguiente.
function punto_mas_cercano_en_segmento(_px, _py, _x1, _y1, _x2, _y2)
{
    var _dx = _x2 - _x1;
    var _dy = _y2 - _y1;
    var _largo2 = _dx * _dx + _dy * _dy;

    if (_largo2 <= 0) { return { x: _x1, y: _y1 }; }   // segmento degenerado

    var _t = clamp(((_px - _x1) * _dx + (_py - _y1) * _dy) / _largo2, 0, 1);
    return { x: _x1 + _t * _dx, y: _y1 + _t * _dy };
}

/// @func caminable_punto_mas_cercano(_x, _y)
/// @desc Si (_x,_y) ya está en un walkbox, se devuelve tal cual. Si no (el
///       jugador clicó sobre una mesa pintada, o fuera del suelo), se
///       recorta al punto caminable más próximo — recorriendo el borde de
///       CADA caja con la misma función de proyección. Evita que un clic
///       "casi correcto" no haga nada, que es la forma más barata de que
///       un point and click se sienta roto.
function caminable_punto_mas_cercano(_x, _y)
{
    if (walkbox_en_punto(_x, _y) != noone) { return { x: _x, y: _y }; }

    var _mejor      = { x: _x, y: _y };
    var _mejor_dist = infinity;

    with (obj_walkbox)
    {
        var _n = array_length(vertices);
        for (var _i = 0; _i < _n; _i++)
        {
            var _a = vertices[_i];
            var _b = vertices[(_i + 1) mod _n];
            var _p = punto_mas_cercano_en_segmento(_x, _y, _a[0], _a[1], _b[0], _b[1]);
            var _d = point_distance(_x, _y, _p.x, _p.y);

            if (_d < _mejor_dist) { _mejor_dist = _d; _mejor = _p; }
        }
    }
    return _mejor;
}
```

#### 3.5.3 · El grafo de cajas: BFS, no A\*

El número de walkboxes de una sala de aventura gráfica se cuenta con los dedos de las dos manos
—no son las miles de celdas de una rejilla de `04 · 38`—, así que un BFS simple sobre un array
plano ya da el camino más corto en número de cajas, sin la complejidad de una cola de prioridad.
Mismo idioma de cola FIFO por índice que usa `13 · 17` §3.3 para su propio BFS, adaptado aquí
porque los nodos son enteros pequeños (el índice de la caja) y no hace falta ni un `ds_map`.

```gml
/// @func walkbox_camino_cajas(_caja_inicio, _caja_fin)
/// @desc BFS sobre el grafo de conexiones. Devuelve un array de índices de
///       caja, de inicio a fin (ambos incluidos), o `undefined` si las dos
///       zonas de suelo no están conectadas.
function walkbox_camino_cajas(_caja_inicio, _caja_fin)
{
    if (_caja_inicio == _caja_fin) { return [_caja_inicio]; }

    var _n        = array_length(global.mapa_cajas);
    var _visitado = array_create(_n, false);
    var _origen   = array_create(_n, -1);
    var _cola     = [_caja_inicio];
    var _cabeza   = 0;

    _visitado[_caja_inicio] = true;

    while (_cabeza < array_length(_cola))
    {
        var _actual = _cola[_cabeza++];
        var _inst   = global.mapa_cajas[_actual];

        for (var _i = 0; _i < array_length(_inst.conexiones); _i++)
        {
            var _vecino = _inst.conexiones[_i].caja;
            if (_visitado[_vecino]) { continue; }

            _visitado[_vecino] = true;
            _origen[_vecino]   = _actual;

            if (_vecino == _caja_fin)
            {
                var _camino = [_caja_fin];
                var _c = _actual;
                while (_c != -1) { array_push(_camino, _c); _c = _origen[_c]; }
                return array_reverse(_camino);
            }
            array_push(_cola, _vecino);
        }
    }
    return undefined;   // no hay camino a pie entre las dos zonas
}
```

#### 3.5.4 · De la secuencia de cajas a una ruta de puntos

Cada vez que la ruta cruza de una caja a la siguiente, el punto de cruce es la proyección del
**destino final** sobre el borde compartido — es la aproximación clásica de este tipo de
pathfinding (la técnica de "cajas de suelo" que usaban los motores SCUMM de LucasArts,
confirmada como término del género en el propio artículo de Wikipedia sobre SCUMM; el algoritmo
exacto de aquellos motores no se ha podido contrastar contra su código fuente esta sesión, así
que lo de abajo es la versión propia de esta biblioteca del mismo concepto, no una réplica
byte a byte). El efecto práctico es que el personaje "corta" cada esquina de forma natural en
vez de pasar siempre por el centro geométrico del borde.

```gml
/// @func walkbox_ruta_calcular(_x_desde, _y_desde, _x_hasta, _y_hasta)
/// @desc La API pública de todo el §3.5: dado un origen y un destino
///       (todavía SIN recortar a suelo caminable — eso lo hace el llamador
///       con caminable_punto_mas_cercano si hace falta), devuelve un array
///       de waypoints [{x,y}, …] a seguir en orden, o `undefined` si no hay
///       camino a pie entre los dos puntos.
function walkbox_ruta_calcular(_x_desde, _y_desde, _x_hasta, _y_hasta)
{
    var _caja_desde = walkbox_en_punto(_x_desde, _y_desde);
    var _caja_hasta = walkbox_en_punto(_x_hasta, _y_hasta);
    if (_caja_desde == noone || _caja_hasta == noone) { return undefined; }

    var _camino_cajas = walkbox_camino_cajas(_caja_desde.indice, _caja_hasta.indice);
    if (is_undefined(_camino_cajas)) { return undefined; }

    var _ruta = [];
    for (var _i = 0; _i < array_length(_camino_cajas) - 1; _i++)
    {
        var _actual  = global.mapa_cajas[_camino_cajas[_i]];
        var _sig_ind = _camino_cajas[_i + 1];

        for (var _c = 0; _c < array_length(_actual.conexiones); _c++)
        {
            var _con = _actual.conexiones[_c];
            if (_con.caja != _sig_ind) { continue; }

            var _p = punto_mas_cercano_en_segmento(_x_hasta, _y_hasta,
                                                    _con.p1[0], _con.p1[1],
                                                    _con.p2[0], _con.p2[1]);
            array_push(_ruta, _p);
            break;
        }
    }
    array_push(_ruta, { x: _x_hasta, y: _y_hasta });
    return _ruta;
}
```

> ⚠️ Esta técnica asume walkboxes **convexos** — si un tramo de suelo tiene forma de "L" o de
> herradura, la proyección sobre un borde puede dar un waypoint que cae fuera del propio
> polígono. La solución del género (y de este documento) no es una matemática más complicada:
> es **partir la sala en más cajas convexas**, tantas como haga falta. Un pasillo en "L" son dos
> cajas rectangulares, no una.

#### 3.5.5 · Seguir la ruta, y encolar la acción para cuando se llegue

```gml
/// obj_jugador — Create (o cualquier instancia que deba caminar por walkboxes)
ruta              = [];
ruta_indice       = 0;
caminando         = false;
accion_al_llegar  = undefined;   // method(), o undefined si solo hay que caminar
velocidad_base    = 2.2;

/// @func jugador_ir_y_actuar(_instancia, _x_destino, _y_destino, _accion)
/// @desc Calcula la ruta y la deja lista para que el Step de _instancia la
///       recorra. Si ya había una ruta en marcha, la SUSTITUYE — un clic
///       nuevo cancela el anterior sin que haga falta ningún botón de
///       "cancelar" aparte (§3.5.6 lo explica).
/// @param {Id.Instance} _instancia
/// @param {Real}        _x_destino
/// @param {Real}        _y_destino
/// @param {Function}    _accion     method() a ejecutar al llegar, o undefined.
function jugador_ir_y_actuar(_instancia, _x_destino, _y_destino, _accion)
{
    var _destino = caminable_punto_mas_cercano(_x_destino, _y_destino);
    var _ruta    = walkbox_ruta_calcular(_instancia.x, _instancia.y, _destino.x, _destino.y);

    if (is_undefined(_ruta))
    {
        // Los dos puntos no están conectados a pie (dos salas sin puerta
        // entre ellas, por ejemplo). Decisión de diseño, no de motor: aquí
        // simplemente no se hace nada.
        return;
    }

    with (_instancia)
    {
        ruta             = _ruta;
        ruta_indice      = 0;
        caminando        = true;
        accion_al_llegar = _accion;
    }
}
```

> 🔺 **`global.jugador` es la referencia global a ESTA instancia, no del walk-to genérico de
> arriba.** Las cinemáticas del §3.10 (`PasoCaminar`) y el guardado del §3.9 corren fuera del
> Step de `obj_jugador` y no tienen su `id` a mano — sin esta línea, revientan con «variable
> global 'jugador' no definida». No la muevas al bloque de Create genérico de arriba: una
> instancia NPC que lo reutilice para caminar por walkboxes pisaría `global.jugador`.

```gml
/// obj_jugador — Create (además del bloque genérico de arriba; solo en el objeto
/// real del jugador, nunca en un NPC que reutilice el walk-to)
global.jugador = id;
```

```gml
/// obj_jugador — Step (después de leer el input del §3.4.1)
if (caminando)
{
    var _obj = ruta[ruta_indice];

    if (point_distance(x, y, _obj.x, _obj.y) <= velocidad_base)
    {
        x = _obj.x; y = _obj.y;
        ruta_indice++;

        if (ruta_indice >= array_length(ruta))
        {
            caminando = false;
            if (!is_undefined(accion_al_llegar))
            {
                var _texto = accion_al_llegar();
                if (!is_undefined(_texto)) { linea_frase_mostrar(_texto); }
                accion_al_llegar = undefined;
            }
        }
    }
    else
    {
        var _dir = point_direction(x, y, _obj.x, _obj.y);
        x += lengthdir_x(velocidad_base, _dir);
        y += lengthdir_y(velocidad_base, _dir);
        image_xscale = (lengthdir_x(1, _dir) < 0) ? -abs(image_xscale) : abs(image_xscale);
    }
}

depth = -bbox_bottom;   // el mismo depth-sort de 04 · 02 §4.4 — no cambia por caminar en walkboxes
```

> 🔺 **Cancelar es gratis, no un sistema aparte.** `jugador_ir_y_actuar()` siempre sobrescribe
> `ruta`, `ruta_indice` y `accion_al_llegar` con los del clic más reciente. Si el jugador pulsa
> dos veces seguidas en sitios distintos, el segundo clic gana sin que haga falta ningún código
> de "detener la ruta anterior primero" — ya no existe en el momento en que se sustituye.

#### 3.5.6 · Caminar entre habitaciones

Salir de una sala es, desde el punto de vista de este sistema, un hotspot como cualquier otro
—normalmente una puerta— cuyo `verbo_usar` no responde con texto: cambia de *room* y coloca al
jugador en el punto de aparición de la sala nueva.

```gml
// ---------------------------------------------------------------------------
// scr_aventura_habitaciones
// ---------------------------------------------------------------------------
global.siguiente_spawn_x = 0;
global.siguiente_spawn_y = 0;

/// @func cambiar_de_habitacion(_room_destino, _spawn_x, _spawn_y)
/// @desc Guarda dónde debe aparecer el jugador en la sala nueva y cambia de
///       room. No hace fundido por sí sola — engancha aquí el sistema de
///       transiciones de 04 · 41 si quieres un fundido a negro entre salas.
function cambiar_de_habitacion(_room_destino, _spawn_x, _spawn_y)
{
    global.siguiente_spawn_x = _spawn_x;
    global.siguiente_spawn_y = _spawn_y;
    room_goto(_room_destino);
}
```

```gml
/// obj_salida_taller — hereda de obj_hotspot
/// obj_salida_taller — Create
event_inherited();
nombre_mostrado   = "la puerta del taller";
verbo_por_defecto = "usar";
punto_de_pie_x    = x;
punto_de_pie_y    = y + 14;

verbo_usar = function()
{
    cambiar_de_habitacion(rm_calle, 40, 260);
    return undefined;   // la sala cambia entera: no hace falta línea de frase
};
```

```gml
/// obj_controlador_aventura — Room Start (antes de que el jugador pueda hacer clic)
walkboxes_indexar();   // §3.5.1 — las cajas son nuevas, hay que re-indexarlas cada sala

/// obj_jugador — Room Start (obj_jugador debe sobrevivir al cambio de sala: o
/// es persistente — 13 · 06 §3.11 — o cada room lo vuelve a crear en su
/// Creation Code; cualquiera de los dos vale, lo único que importa es leer
/// el spawn ANTES del primer Step)
x = global.siguiente_spawn_x;
y = global.siguiente_spawn_y;
caminando        = false;
ruta             = [];
accion_al_llegar = undefined;
```

### 3.6 · Escalado por profundidad

La misma idea que `04 · 47` §3.3 usa para la banda estrecha de un beat 'em up, pero aplicada a
una sala entera con perspectiva: el personaje se hace pequeño cerca del fondo pintado y grande
cerca de la "cámara". A diferencia de `04 · 47` (una banda fija en todo el nivel), aquí cada
walkbox declara su propia zona de escala porque una sala de aventura gráfica rara vez tiene una
sola perspectiva de principio a fin.

```gml
/// obj_jugador — Step (después de mover x/y en el §3.5.5)
var _caja = walkbox_en_punto(x, y);

if (_caja != noone && _caja.escala_activa)
{
    var _t = clamp((y - _caja.escala_y_lejos) / max(1, _caja.escala_y_cerca - _caja.escala_y_lejos), 0, 1);
    var _escala = lerp(_caja.escala_min, _caja.escala_max, _t);

    image_yscale = _escala;
    image_xscale = _escala * sign(image_xscale);   // conserva la orientación (izq/der) del §3.5.5

    velocidad_actual = velocidad_base * _escala;   // al fondo, además de pequeño, más lento
    audio_sound_gain(snd_pasos, _escala, 0);        // y los pasos suenan más lejanos
}
else
{
    image_yscale = 1; image_xscale = sign(image_xscale);
    velocidad_actual = velocidad_base;
}
```

El orden de dibujado **no cambia de criterio**: sigue siendo `depth = -bbox_bottom` (§3.5.5,
igual que `04 · 02` §4.4 y que `04 · 46` §3.6 ya advierten para cualquier técnica de altura o
escala falsa) — la escala afecta a cómo se ve el personaje, nunca a quién tapa a quién.

### 3.7 · Inventario combinatorio

#### 3.7.1 · El catálogo y el inventario como datos

```gml
// ---------------------------------------------------------------------------
// scr_aventura_inventario
// ---------------------------------------------------------------------------

/// El catálogo: TODO objeto que puede existir en el inventario, indexado por
/// una clave de texto — nunca por un sprite_index (01 · 03, los assets son
/// handles en 2026 y no se pueden guardar como si fueran números fijos).
global.catalogo_objetos = {
    llave_oxidada: { nombre: "una llave oxidada", sprite: spr_inv_llave,
                      descripcion: "Está cubierta de óxido. Aun así, parece que gira." },
    aceite:        { nombre: "una lata de aceite", sprite: spr_inv_aceite,
                      descripcion: "Media lata de aceite para máquinas." },
};

global.inventario = [];   // array de claves de catálogo — plano, se guarda tal cual (§3.9)

/// @func inventario_anadir(_clave)
function inventario_anadir(_clave)
{
    if (!array_contains(global.inventario, _clave)) { array_push(global.inventario, _clave); }
}

/// @func inventario_quitar(_clave)
function inventario_quitar(_clave)
{
    var _i = array_get_index(global.inventario, _clave);
    if (_i >= 0) { array_delete(global.inventario, _i, 1); }
}
```

#### 3.7.2 · La matriz de combinaciones

```gml
/// @func combinacion_clave(_item_a, _item_b)
/// @desc Normaliza el orden alfabético: "usar A con B" y "usar B con A"
///       tienen que dar la MISMA combinación sin definirla dos veces.
function combinacion_clave(_item_a, _item_b)
{
    return (_item_a < _item_b) ? (_item_a + "+" + _item_b) : (_item_b + "+" + _item_a);
}

global.combinaciones = {};

/// @func combinacion_definir(_item_a, _item_b, _resultado_fn)
/// @desc _resultado_fn es un method() sin argumentos que aplica el efecto
///       (dar un objeto nuevo, poner un flag — 13 · 12 §6.2 — cambiar el
///       estado del mundo, §3.8) y devuelve el texto de la línea de frase.
function combinacion_definir(_item_a, _item_b, _resultado_fn)
{
    global.combinaciones[$ combinacion_clave(_item_a, _item_b)] = _resultado_fn;
}

/// @func combinacion_usar(_item_a, _item_b)
/// @returns {String|Undefined}  El texto a mostrar, o `undefined` si NO hay
///          combinación definida (el llamador cae entonces a la respuesta
///          por defecto, §3.4.2 adaptada a "combinar" — ver más abajo).
function combinacion_usar(_item_a, _item_b)
{
    var _clave = combinacion_clave(_item_a, _item_b);
    if (!struct_exists(global.combinaciones, _clave)) { return undefined; }
    return global.combinaciones[$ _clave]();
}
```

```gml
// Ejemplo: la llave oxidada + el aceite dan una llave que ya funciona.
combinacion_definir("llave_oxidada", "aceite", function()
{
    inventario_quitar("llave_oxidada");
    inventario_quitar("aceite");
    inventario_anadir("llave_engrasada");
    flag_poner("engraso_la_llave", true);   // 13 · 12 §6.2 — reutilizado sin repetir
    return "La llave gira mucho mejor ahora que no chirría.";
});
```

#### 3.7.3 · Arrastrar y soltar

```gml
/// obj_controlador_aventura — Create
arrastrando = "";   // clave de catálogo, o "" si no se está arrastrando nada

/// obj_controlador_aventura — Step (los slots de inventario son otro tipo de
/// hotspot — obj_slot_inventario, hereda de obj_hotspot con nombre_mostrado
/// = catálogo[clave].nombre)
if (mouse_check_button_pressed(mb_left))
{
    var _hs = hotspot_bajo_cursor();
    if (_hs != noone && object_get_name(_hs.object_index) == "obj_slot_inventario" && _hs.clave != "")
    {
        arrastrando = _hs.clave;
    }
}

if (arrastrando != "" && mouse_check_button_released(mb_left))
{
    var _hs = hotspot_bajo_cursor();

    if (_hs != noone && object_get_name(_hs.object_index) == "obj_slot_inventario" && _hs.clave != "")
    {
        // Soltado sobre OTRO objeto del inventario: combinar.
        var _texto = combinacion_usar(arrastrando, _hs.clave);
        linea_frase_mostrar(_texto ?? respuesta_por_defecto("usar",
                             global.catalogo_objetos[$ arrastrando].nombre));
    }
    else if (_hs != noone)
    {
        // Soltado sobre un hotspot del mundo: usar el objeto arrastrado SOBRE él.
        // Cada hotspot que acepte objetos concretos define su propio verbo_usar_con()
        // (mismo patrón de sobrescritura que verbo_usar/verbo_mirar, §3.1); si no lo
        // define, cae a la respuesta genérica.
        var _texto = variable_instance_exists(_hs, "verbo_usar_con")
            ? _hs.verbo_usar_con(arrastrando)
            : respuesta_por_defecto("usar", _hs.nombre_mostrado);
        linea_frase_mostrar(_texto);
    }
    // Soltado en el vacío: no pasa nada — el objeto simplemente vuelve a su sitio,
    // porque el inventario se DIBUJA desde global.inventario, no desde una posición
    // arrastrada de verdad.

    arrastrando = "";
}

/// obj_controlador_aventura — Draw GUI, mientras arrastrando != ""
if (arrastrando != "")
{
    draw_sprite(global.catalogo_objetos[$ arrastrando].sprite, 0,
                device_mouse_x_to_gui(0), device_mouse_y_to_gui(0));
}
```

> ⚠️ `variable_instance_exists` comprueba si una instancia concreta tiene esa variable definida
> — necesario aquí porque no todos los hotspots del mundo aceptan objetos del inventario, solo
> los que declaran `verbo_usar_con`.

#### 3.7.4 · Examinar

"Examinar" un objeto del inventario reutiliza el mismo verbo **mirar** que ya tienen los
hotspots del mundo (§3.4): un slot de inventario es un `obj_hotspot` más, así que el clic derecho
sobre él ya funciona sin código adicional — solo hace falta que su `verbo_mirar` lea la
descripción del catálogo en vez de la genérica:

```gml
/// obj_slot_inventario — Create (tras event_inherited())
verbo_mirar = function()
{
    return (clave != "") ? global.catalogo_objetos[$ clave].descripcion
                          : "No llevo nada ahí.";
};
```

### 3.8 · Estado del mundo: banderas globales frente a estado por objeto

Dos clases de memoria del mundo, con alcance distinto — la misma disciplina de clasificar antes
de guardar que ya pide `13 · 06` §3.10, aplicada al vocabulario propio de este género:

| Clase | Qué es | Ejemplo | Dónde vive |
|---|---|---|---|
| **Bandera global (flag)** | Un hecho de la HISTORIA, sin dueño físico | "ya hablé con el guardia", "el acto es el 2" | `global.flags` — `13 · 12` §6.2, reutilizado tal cual |
| **Estado por objeto** | Algo que le pasa a ESTE objeto de ESTA sala en concreto | "esta puerta está abierta", "esta caja ya se rompió" | Registro nuevo de este documento, abajo |

Confundirlas es el mismo bug que `13 · 06` ya avisa para progreso/partida: si "la puerta está
abierta" viviera en un flag global con el nombre de la puerta, dos puertas con el mismo nombre en
salas distintas compartirían estado sin querer.

```gml
// ---------------------------------------------------------------------------
// scr_aventura_estado_mundo
// ---------------------------------------------------------------------------

/// { "rm_taller.puerta_norte": { abierta: true }, "rm_taller.jarron": { recogido: true } }
global.estado_mundo = {};

/// @func mundo_clave(_nombre_objeto)
/// @desc Sala actual + nombre propio del objeto: dos objetos con el mismo
///       nombre en salas distintas nunca comparten registro por accidente.
function mundo_clave(_nombre_objeto)
{
    return room_get_name(room) + "." + _nombre_objeto;
}

/// @func mundo_leer(_nombre_objeto, _campo, _por_defecto)
function mundo_leer(_nombre_objeto, _campo, _por_defecto)
{
    var _clave = mundo_clave(_nombre_objeto);
    if (!struct_exists(global.estado_mundo, _clave)) { return _por_defecto; }

    var _registro = global.estado_mundo[$ _clave];
    return struct_exists(_registro, _campo) ? _registro[$ _campo] : _por_defecto;
}

/// @func mundo_escribir(_nombre_objeto, _campo, _valor)
function mundo_escribir(_nombre_objeto, _campo, _valor)
{
    var _clave = mundo_clave(_nombre_objeto);
    if (!struct_exists(global.estado_mundo, _clave)) { global.estado_mundo[$ _clave] = {}; }
    global.estado_mundo[$ _clave][$ _campo] = _valor;
}
```

**Puertas que se quedan abiertas al volver a la sala:**

```gml
/// obj_puerta_taller — hereda de obj_hotspot
/// obj_puerta_taller — Create (tras event_inherited())
nombre_propio = "puerta_norte";                        // identificador único DENTRO de esta room
abierta       = mundo_leer(nombre_propio, "abierta", false);
image_index   = abierta ? 1 : 0;

verbo_usar = function()
{
    if (abierta) { return "Ya está abierta."; }

    abierta = true;
    mundo_escribir(nombre_propio, "abierta", true);
    image_index = 1;
    return "La puerta se abre con un chirrido.";
};
```

**Objetos que desaparecen para siempre al cogerlos:**

```gml
/// obj_jarron_recogible — hereda de obj_hotspot
/// obj_jarron_recogible — Create (tras event_inherited())
nombre_propio = "jarron";
verbo_por_defecto = "coger";

if (mundo_leer(nombre_propio, "recogido", false))
{
    instance_destroy();   // ya se cogió en una visita anterior: no vuelve a aparecer
    exit;
}

verbo_usar = function()
{
    inventario_anadir("jarron_roto");
    mundo_escribir(nombre_propio, "recogido", true);
    instance_destroy();
    return "Un jarrón viejo. Podría servir para algo.";
};
```

**Condiciones para que un diálogo aparezca**: eso ya está resuelto — `13 · 12` §6.3
(disparadores) decide CUÁNDO se lanza un nodo de diálogo, y §6.4 (*barks*) decide qué línea suena
según el estado actual. Ninguno de los dos se repite aquí: un NPC de esta receta es, para efectos
de diálogo, exactamente lo que `13 · 12` ya describe — este documento solo aporta que su
`verbo_usar` (o un verbo `hablar` si tu interfaz de verbos lo separa) es el punto donde se llama
a `dialogo_empezar()`.

### 3.9 · Cómo se guarda todo esto

La arquitectura de guardado —ranuras, escritura atómica, migraciones de versión— está resuelta
entera en `13 · 06` §3.10, y el sandbox de archivos en `01 · 14` §1: **ninguno de los dos se
repite aquí.** Lo único propio de este género es **qué entra en el struct** que ese sistema
guarda — la función `_recolectar_datos` que `13 · 06` ya pide como argumento de
`autoguardado_intentar()` / `save_game()`:

```gml
#macro VERSION_GUARDADO_AVENTURA 1   // 13 · 06 §3.10: el campo existe desde el primer día

/// @func partida_recolectar_datos()
/// @desc Arma el struct de esta aventura. No repite save_game ni la
///       escritura atómica (13 · 06 §3.10 ya los resuelve) — solo dice QUÉ
///       hace falta recordar en este género.
function partida_recolectar_datos()
{
    return {
        version:      VERSION_GUARDADO_AVENTURA,
        flags:        global.flags,          // 13 · 12 §6.2
        estado_mundo: global.estado_mundo,   // §3.8 de este documento
        inventario:   global.inventario,     // §3.7.1
        room_actual:  room_get_name(room),
        jugador_x:    global.jugador.x,
        jugador_y:    global.jugador.y,
    };
}
```

> ⚠️ Igual que advierte `13 · 06` §3.10: nunca guardes un `sprite_index` ni un `object_index`
> dentro de `catalogo_objetos` — ese struct vive en código, no en el fichero de guardado; el
> guardado solo lleva las **claves de texto** (`"llave_oxidada"`), y al cargar se reconstruyen
> las referencias mirando `global.catalogo_objetos[$ clave]`.

### 3.10 · Escenas y guion: cinemáticas cortas con el motor que ya existe

Una cinemática de aventura gráfica ("el guardia se da la vuelta, el jugador cruza corriendo, la
puerta se cierra") es, en su forma, exactamente la cola de pasos de `13 · 12` §6.6
(`Cinematica`, con `empezar()`/`actualizar()`/`saltar()` y la separación `empezar`/`efecto` que
hace segura la función de saltar) — **no se repite el motor aquí**. Lo único que aporta este
documento son dos tipos de paso nuevos, pensados para este género, que se enchufan en esa misma
cola:

```gml
/// @func PasoCaminar(_x, _y)
/// @desc Un paso de Cinematica (13 · 12 §6.6) que mueve al jugador con el
///       walk-to del §3.5 y no se da por terminado hasta que llega.
function PasoCaminar(_x, _y) constructor
{
    destino_x = _x;
    destino_y = _y;

    static empezar = function()
    {
        jugador_ir_y_actuar(global.jugador, destino_x, destino_y, undefined);
    };
    static terminado = function()
    {
        return !global.jugador.caminando;
    };
    static efecto = function()
    {
        // Al SALTAR la cinemática: coloca al jugador de golpe en el
        // destino, sin recorrer el camino — la misma separación
        // empezar/efecto que ya explica 13 · 12 §6.6.
        global.jugador.x = destino_x;
        global.jugador.y = destino_y;
        global.jugador.caminando = false;
    };
}

/// @func PasoInteraccion(_hotspot_verbo_fn)
/// @desc Un paso instantáneo que ejecuta un verbo (§3.1) sin esperar nada —
///       para escenas donde el guion "aprieta el botón" en vez del jugador.
function PasoInteraccion(_hotspot_verbo_fn) constructor
{
    verbo_fn = _hotspot_verbo_fn;

    static empezar   = function() { verbo_fn(); };
    static terminado = function() { return true; };   // instantáneo: un fotograma
    static efecto    = function() { verbo_fn(); };     // igual al saltar: el efecto es el mismo
}
```

**Quitar el control y devolverlo**: `Cinematica.empezar()` (código de `13 · 12`, sin tocar) llama
a `instance_deactivate_all(true)`, que congela **todo salvo la instancia que llamó** — en una
cinemática genérica eso es justo lo que se quiere, pero aquí el propio jugador tiene que poder
moverse por guion (`PasoCaminar` necesita que su Step siga corriendo). La adaptación es una sola
línea, con una función ya existente del catálogo:

```gml
/// obj_narrativa — al lanzar una cinemática que incluye PasoCaminar
var _c = new Cinematica("guardia_distraido");
_c.anadir(new PasoCaminar(jugador_punto_escondite_x, jugador_punto_escondite_y))
  .anadir(new PasoDialogo("guardia_distraido_1"));   // 13 · 12 §6.6

_c.empezar();
instance_activate_object(obj_jugador);   // la única línea que añade este género: el jugador
                                          // vuelve a recibir Step (puede seguir su ruta), pero
                                          // sigue sin poder iniciar una acción nueva — eso lo
                                          // bloquea global.cinematica_en_curso en el §3.4.1.
global.cinematica = _c;
```

### 3.11 · La regla de oro del género: no crear callejones sin salida

#### 3.11.1 · Las reglas, de la fuente

Ron Gilbert escribió esto en 1989 mientras diseñaba el primer *Monkey Island*, en un artículo
titulado *«Why Adventure Games Suck (And What We Can Do About It)»*, republicado por él mismo en
2004 (Grumpy Gamer, consultado en vivo el 2026-09-07). Dos de sus reglas son, literalmente, la
definición operativa de "callejón sin salida":

> **«Live and learn»**: *«…un juego de aventuras debería poder jugarse de principio a fin sin
> "morir" ni tener que cargar la partida, si el jugador es cuidadoso y observador. Es mal diseño
> meter puzzles y situaciones que obligan a morir para aprender qué NO hacer la próxima vez.»*
>
> **«I forgot to pick it up»**: *«Nunca exijas al jugador coger un objeto que se usa más tarde si
> luego no puede volver a por él cuando lo necesita. […] Si el frasco de agua hace falta en la
> nave y solo se puede conseguir en el planeta, crea un uso para él EN EL PLANETA que garantice
> que se coge.»*

Traducidas a mecánica: un *dead end* de aventura gráfica no es "un puzzle difícil", es una de
estas dos cosas exactas — **(a)** el jugador destruyó, gastó o dejó fuera de alcance un objeto que
el guion da por hecho que sigue disponible más adelante, o **(b)** una acción cerró el paso hacia
atrás (zarpar, volar un puente, un ascensor de un solo uso) sin comprobar antes que ya se tenía
todo lo necesario. Es también la razón de que las aventuras gráficas comerciales modernas hayan
dejado de permitir esto salvo como decisión de diseño explícita y anunciada: un jugador que
descubre media hora después de la causa que su partida ya no tiene salida no vuelve a confiar en
que "explorar" sea seguro, y eso mata la curiosidad que sostiene al género entero.

#### 3.11.2 · Cómo se detecta por diseño, no jugando a ciegas

**Técnica 1 — el ejercicio de Gilbert, en una tabla.** Antes de dar una sala por cerrada, escribe
la secuencia completa de acciones que la resuelve como si fuera un guion, columna a columna:
"acción → qué exige tener ya (flags/objetos) → qué deja disponible". Cualquier fila cuya columna
"exige" pida algo que ninguna fila anterior dejó disponible es un agujero de guion — el mismo
método que Gilbert describe como "cuéntaselo a alguien como si fuera una historia normal, y mira
dónde el protagonista sabe algo que no pudo haber aprendido".

**Técnica 2 — un guardián de punto de no retorno**, en código:

```gml
/// @func punto_de_no_retorno_verificar(_flags_requeridos)
/// @desc Llamar ANTES de cualquier transición que cierre el paso hacia
///       atrás (zarpar, dinamitar el puente). Si falta algo que el diseño
///       exige haber conseguido antes, BLOQUEA la transición — la
///       aplicación directa de "Live and learn": el jugador nunca debe
///       enterarse de que dejó algo atrás DESPUÉS de que ya no haya vuelta.
/// @param {Array<String>} _flags_requeridos
/// @returns {Bool}
function punto_de_no_retorno_verificar(_flags_requeridos)
{
    for (var _i = 0; _i < array_length(_flags_requeridos); _i++)
    {
        if (!flag_leer(_flags_requeridos[_i])) { return false; }   // 13 · 12 §6.2, reutilizado
    }
    return true;
}
```

```gml
/// obj_barca — verbo_usar (zarpar hacia el segundo acto)
verbo_usar = function()
{
    if (!punto_de_no_retorno_verificar(["tiene_el_mapa", "tiene_la_brujula"]))
    {
        // Nunca "No puedes hacer eso": di POR QUÉ, para que el jugador sepa
        // qué le falta sin tener que adivinarlo — la otra mitad de la regla
        // de Gilbert es que el jugador SIEMPRE puede saber qué necesita.
        return "Antes de zarpar debería llevar un mapa y algo con lo que orientarme.";
    }

    cambiar_de_habitacion(rm_segundo_acto, 60, 300);
    return undefined;
};
```

**Técnica 3 — nunca un objeto único e irrecuperable para un puzzle posterior.** Si un objeto se
consume (§3.7.2, una combinación que lo destruye) y hace falta OTRA VEZ más adelante, o (a) el
juego debe permitir recuperarlo (una tienda que lo vende de nuevo, un NPC que da otro), o (b) el
puzzle posterior debe aceptar una alternativa. Diseñarlo así desde el principio es mucho más
barato que parchear un *dead end* descubierto en *playtesting* — y es precisamente la clase de
comprobación que corresponde a
[`13 · 17`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/17%20-%20Diseño%20de%20puzzles.md)
§2.3-§2.4 (medir dificultad, pistas graduadas) una vez que el puzzle en sí ya no tiene el agujero.

---

## 4 · Checklist

- [ ] Cada hotspot importante (§3.1) tiene `verbo_usar`/`verbo_mirar` propios — los que se
      quedan con la respuesta genérica (§3.4.2) son attrezzo, no puzzles.
- [ ] `hotspot_bajo_cursor()` desempata por prioridad y luego por área — un objeto pequeño sobre
      uno grande sigue siendo clicable (§3.2.1).
- [ ] La tecla de resaltar hotspots (§3.3) existe y es reasignable en el menú de opciones.
- [ ] El clic izquierdo siempre pide "usar" contextual; el derecho siempre "mirar", y "mirar"
      NUNCA exige caminar hasta el objeto (§3.4.1).
- [ ] Cada `obj_walkbox` tiene su `indice` único por sala y sus `conexiones` con el borde
      compartido puesto a mano — nunca detectado automáticamente (§3.5.1).
- [ ] Un clic fuera de todo walkbox se recorta al punto caminable más cercano, no se ignora
      (§3.5.2, `caminable_punto_mas_cercano`).
- [ ] Un walkbox no convexo está partido en varias cajas convexas (§3.5.4, la advertencia final).
- [ ] `jugador_ir_y_actuar()` se llama de nuevo en cada clic — nunca hace falta un botón de
      cancelar aparte (§3.5.5).
- [ ] La escala por profundidad, si la sala la usa, va ligada a la velocidad y al volumen de
      pasos, no solo al tamaño del sprite (§3.6).
- [ ] Las combinaciones se definen una sola vez por par —`combinacion_clave()` normaliza el
      orden— y ninguna cae en "eso no funciona" a secas (§3.7.2, §3.4.2).
- [ ] El estado por objeto (§3.8) usa `mundo_clave()` (sala + nombre propio), nunca un flag
      global con el nombre del objeto — dos puertas iguales en salas distintas no deben
      compartir estado.
- [ ] `partida_recolectar_datos()` guarda `flags`, `estado_mundo` e `inventario` como structs
      planos — nunca un `sprite_index` ni un `object_index` dentro (§3.9).
- [ ] Toda cinemática que mueva al jugador por guion reactiva `obj_jugador` justo después de
      `Cinematica.empezar()` (§3.10) — si no, el `PasoCaminar` se queda esperando un Step que
      nunca llega.
- [ ] Cada transición que cierra el paso hacia atrás pasa por
      `punto_de_no_retorno_verificar()` ANTES de ejecutarse, nunca después (§3.11.2).
- [ ] Ningún objeto de un solo uso es indispensable para un puzzle posterior sin una vía de
      recuperación — comprobado con el ejercicio de la tabla de Gilbert (§3.11.2).

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Arreglo |
|---|---|---|
| Hotspots con solo bounding box en sprites no rectangulares | Clicar "el aire" junto a una estatua activa el verbo, y clicar la propia estatua a veces no | Máscara precisa (`bboxkind_precise`, `01 · 08`) para siluetas no rectangulares (§3.1) |
| Un solo hotspot gigante detrás de varios pequeños | Un objeto diminuto sobre una mesa nunca se puede clicar: la mesa siempre gana | Desempate por área en `hotspot_bajo_cursor()` — el más pequeño gana si no hay prioridad explícita (§3.2.1) |
| Walkbox cóncavo tratado como si fuera convexo | El personaje "atraviesa" una esquina del escenario al cruzar de una zona a otra | Partir la sala en más cajas convexas — nunca un polígono con muescas (§3.5.4) |
| Conexión entre cajas sin el segmento compartido, solo el índice de la vecina | El camino calculado por BFS existe, pero el waypoint de cruce cae fuera del suelo real | `conexiones` siempre lleva `p1`/`p2`, el borde EXACTO, no solo "caja: N" (§3.5.1) |
| `elevacion`/velocidad de escala copiada de `04 · 47` sin adaptar los rangos | El personaje se hace diminuto o gigantesco de golpe al moverse un píxel | `escala_y_lejos`/`escala_y_cerca` puestos a la altura real de la sala, no valores de ejemplo copiados (§3.6) |
| Combinación definida solo en un sentido (`"A+B"` pero no `"B+A"`) | Arrastrar A sobre B funciona, arrastrar B sobre A no — y parece un bug aleatorio | `combinacion_clave()` normaliza el orden SIEMPRE: nunca construyas la clave a mano en otro sitio (§3.7.2) |
| Estado de "puerta abierta" guardado como flag global con el nombre de la puerta | Dos salas con una "puerta_norte" cada una comparten el mismo booleano sin querer | `mundo_clave()` — sala actual + nombre propio — nunca un flag pelado (§3.8) |
| Cinemática con `PasoCaminar` sin reactivar al jugador | El paso de caminar nunca termina: el juego parece colgado en mitad de la escena | `instance_activate_object(obj_jugador)` justo después de `Cinematica.empezar()` (§3.10) |
| Transición que cierra el paso sin comprobar requisitos | El jugador zarpa sin el mapa y descubre 40 minutos después que ya no puede volver a por él | `punto_de_no_retorno_verificar()` antes de la transición, con un mensaje que diga QUÉ falta (§3.11.2) |
| Un objeto de un solo uso, indispensable más tarde, sin forma de recuperarlo | *Softlock* silencioso: el jugador no se entera hasta que ya es tarde | Vía de recuperación (otro NPC, otra tienda) o puzzle alternativo — nunca un objeto único crítico (§3.11.2, técnica 3) |

---

## Ver también

- [13 · 12 — Diseño narrativo y diálogos](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/12%20-%20Diseño%20narrativo%20y%20diálogos.md) —
  las banderas (`flag_*`, §6.2), los disparadores de diálogo (§6.3), las elecciones que importan
  (§4.6-§4.8) y el motor de cinemáticas en cola (§6.6) que este documento reutiliza en §3.8, §3.9
  y §3.10 sin repetir ni una línea.
- [13 · 17 — Diseño de puzzles](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/17%20-%20Diseño%20de%20puzzles.md) —
  qué hace bueno o malo a un puzzle de objeto, medir su dificultad y dar pistas graduadas: la
  parte de DISEÑO de un puzzle de aventura gráfica, que este documento no repite (solo aporta la
  mecánica de inventario y estado que lo hace posible, §3.7-§3.8).
- [13 · 06 — Arquitectura de un proyecto GameMaker](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) §3.10 —
  la arquitectura completa de guardado (ranuras, migraciones, autoguardado atómico) que §3.9
  reutiliza sin repetir; y §3.7, el patrón comando del que el motor de cinemáticas de `13 · 12`
  hereda su filosofía de separar intención y aplicación.
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) §1 —
  el sandbox de archivos: nunca se guarda escribiendo en `working_directory` (solo lectura en una
  build exportada), siempre en el *save area* que ya usa `save_game` de `13 · 06`.
- [04 · 38 — Pathfinding avanzado](./38%20-%20Pathfinding%20avanzado%20-%20flow%20fields%2C%20JPS%20y%20plataformas.md) —
  el contraste explícito de §3.5: ese documento resuelve rejillas y muchas unidades; este
  documento resuelve un polígono de suelo continuo con un único personaje, y por eso es un
  algoritmo distinto, no una variación del mismo.
- [04 · 47 — Beat 'em up y brawler](./47%20-%20Beat%20em%20up%20y%20brawler.md) §3.3 —
  el precedente directo del escalado por profundidad del §3.6 de este documento, aplicado allí a
  una banda estrecha de combate en vez de a una sala completa con perspectiva.
- [04 · 46 — Eje Z falso](./46%20-%20Eje%20Z%20falso%20-%20altura%2C%20sombras%20y%20profundidad%20en%20un%20juego%202D.md) §3.6 —
  la regla de que el `depth`-sort usa SIEMPRE la posición de suelo, nunca la de dibujo ni la de
  escala, que el §3.6 de este documento hereda sin excepción.
- [04 · 02 — Top-Down / Twin-Stick](./02%20-%20Top-Down%20_%20Twin-Stick.md) §4.4 —
  `depth = -bbox_bottom`, la base del orden de dibujado que este documento no cambia en ningún
  momento, ni al caminar por walkboxes ni al escalar por profundidad.
- [04 · 41 — Transiciones, carga y pausa](./41%20-%20Transiciones%2C%20carga%20y%20pausa.md) —
  el fundido a negro entre salas que `cambiar_de_habitacion()` (§3.5.6) puede enganchar para un
  cambio de sala pulido, sin que este documento repita ese sistema.
- [04 · 25 — Menú de opciones y ajustes](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md) —
  dónde vive el rebinding de la tecla de resaltar hotspots (§3.3).
- [02 - Novedades 2026/06 — Gráficos: SVG, SDF, FX y superficies](../02%20-%20Novedades%202026/06%20-%20Gráficos%20-%20SVG%2C%20SDF%2C%20FX%20y%20superficies.md) §4.5 —
  el filtro `_filter_outline` que el §3.3 de este documento menciona como alternativa de más
  producción al rectángulo de resaltado dibujado a mano.
- [01 · 08 — Movimiento y colisiones](./../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) —
  `bboxkind_precise`, la máscara de colisión que hace posible un hotspot "por máscara" (§3.1).

---

## Fuentes

- Ron Gilbert, *«Why Adventure Games Suck (And What We Can Do About It)»*, escrito en 1989
  durante el desarrollo de *The Secret of Monkey Island*, republicado en Grumpy Gamer el 12 de
  mayo de 2004 — <https://grumpygamer.com/why_adventure_games_suck> (consultado en vivo,
  2026-09-07): las reglas «Live and learn» e «I forgot to pick it up» citadas en §1.4 y §3.11.1.
- Wikipedia, artículo «SCUMM» — <https://en.wikipedia.org/wiki/SCUMM> (consultado en vivo,
  2026-09-07): confirma «walkboxes» como término establecido del motor de las aventuras clásicas
  de LucasArts (herramienta ScummC), usado en §3.5.4. El algoritmo exacto de esos motores no se
  ha podido contrastar contra su código fuente esta sesión (el código de SCUMM no es de acceso
  trivial ni libre) — la implementación del §3.5 es la versión propia de esta biblioteca del
  mismo concepto de género, marcada como tal en el propio texto.
- W. Randolph Franklin, *PNPOLY — Point Inclusion in Polygon Test*: el algoritmo de *ray casting*
  par-impar usado en `punto_en_poligono()` (§3.2.1) es la formulación estándar de este test,
  ampliamente documentada en computación gráfica; ⚠️ no se ha podido abrir la página original del
  autor (`wrf.ecse.rpi.edu`) en vivo esta sesión para citar la URL exacta.
- Manual oficial de GameMaker — `instance_position`, `point_in_rectangle`, `point_in_triangle`,
  `mouse_check_button_pressed`, `fx_create`, `layer_set_fx` — `09 - Manual oficial/manual-lts-2026-es/`
  (espejo local, consultado 2026-09-07).
- El propio código verificado de esta biblioteca en `13 · 12` (flags, cinemáticas), `13 · 06`
  (arquitectura de guardado), `13 · 17` (BFS con cola FIFO por índice) y `04 · 46`/`04 · 47`
  (eje Z falso, escalado por profundidad), usados como base sin duplicar su contenido — es la
  fuente primaria más fiable de todas: ya compiló antes de escribirse este documento.
