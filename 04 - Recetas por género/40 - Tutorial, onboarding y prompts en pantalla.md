# 40 · Tutorial, onboarding y prompts en pantalla

> El **diseño** de cómo enseñar sin texto —encuadre, camino único, demostración segura,
> repetición con variación, *gating*, el examen de los primeros 60 segundos— ya está resuelto
> en [13 · 01 §5 — Onboarding: enseñar sin texto](<../13 - Diseño y producción de videojuegos/01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md#5--onboarding-enseñar-sin-texto>).
> **Empieza por ahí.** Este documento no repite esa teoría: la traduce en código. Lo que
> faltaba en toda la biblioteca era la fontanería — disparadores por zona que se arman solos,
> «mostrar una sola vez» que sobrevive a cerrar el juego (y a un New Game+), la pista que sube
> de tono cuando el jugador falla la misma cosa varias veces, el *widget* de *prompt* de botón
> que dibuja el icono correcto — el del dispositivo activo **y** de la tecla que el jugador
> **de verdad** tiene asignada, no la de fábrica —, un panel de «¿qué estaba haciendo?»
> accesible en cualquier momento, y el ajuste «saltar tutorial».
>
> **No cubre:** el remapeo de controles en sí — lo hace, cuando exista de verdad,
> [04 · 25 §5 — Reasignar controles](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#5--reasignar-controles-rebinding) —
> ni los componentes genéricos de UI (panel, *toast*, tipografía, el lienzo de la GUI) que ya
> están en [13 · 05 — UI y UX de juego](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md>)
> y a los que este documento se engancha en vez de reinventarlos. Tampoco repite el sistema de
> *flags* narrativo de [13 · 12 §6.2](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md#62-los-flags-un-struct-global-plano-y-guardable>):
> lo **reutiliza**, porque «mostrar una vez» y «contar fallos» son el mismo problema que
> «¿ya se disparó este diálogo?».

---

## 1 · Los principios

### 1.1 El diseño ya está resuelto; lo que falta es el sistema

La auditoría de cobertura de esta biblioteca lo dice sin rodeos: *«Sistema de tutorial en GML:
no existe. 13/12 §3.6 cubre el tono —la voz de personaje que enseña—, no el sistema»*. Hay
teoría excelente en 13/01 §5 y hay un ejemplo de diálogo de tutorial con voz propia en 13/12,
pero ningún documento responde a la pregunta mecánica: **¿qué estructura de datos y qué código
hace que una pista aparezca en el momento justo, una sola vez, y de la forma correcta según lo
que el jugador ha tocado?** Eso es lo único que añade este documento. Si buscas cómo *diseñar*
la progresión de dificultad de un tutorial, vuelve a 13/01 §5; si buscas cómo *implementarla*,
sigue leyendo.

### 1.2 Por qué «una sola vez» vive en el guardado, y no en una variable de sesión

Es tentador resolver «que esto no se repita» con una variable en el controlador persistente:

```gml
// LO QUE NO HAY QUE HACER
if (!tutorial_salto_visto) {
    aviso_lanzar("Pulsa saltar para subir", "info");
    tutorial_salto_visto = true;
}
```

Funciona exactamente hasta que el jugador cierra el juego. `tutorial_salto_visto` vive en una
instancia (o en un `global.` que solo existe mientras el proceso está abierto): al volver a
abrir la partida guardada, la variable nace en `false` otra vez y la pista reaparece como si
fuera la primera vez. La única forma de que «una sola vez» signifique *una sola vez en toda la
vida de esta partida* es que el booleano viaje dentro de los datos que se guardan y se cargan.
No hace falta inventar un sistema nuevo para eso: los *flags* narrativos de
[13 · 12 §6.2](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md#62-los-flags-un-struct-global-plano-y-guardable>)
ya son exactamente «un struct plano, guardable, con una función `flag_una_vez()` que
devuelve `true` la primera vez y `false` siempre después». §3.3 muestra cómo este documento
los reutiliza sin tocar ni una línea de ese archivo.

### 1.3 Por qué un *prompt* no puede llevar la tecla de fábrica cosida al sprite

El error más caro de un HUD de tutorial es escribir, en el sprite o en el texto traducido,
«Pulsa **ESPACIO** para saltar». El día que el menú de opciones permita reasignar controles
—y las Game Accessibility Guidelines lo piden como pauta **Basic**, no opcional: *«Allow
controls to be remapped / reconfigured»* (ver Fuentes)— ese texto miente en cuanto un jugador
reasigna Saltar a otra tecla. El *prompt* tiene que ser un **widget que se recalcula cada
frame** a partir de dos datos, nunca de una cadena fija:

1. **El dispositivo activo ahora mismo** — teclado, ratón o mando, y qué marca de mando — que
   ya resuelve [13 · 05 §2.3](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#23-ratón-táctil-y-mando-a-la-vez-manda-el-último-dispositivo-usado>)
   con `global.ui_dispositivo` y `global.ui_marca_mando`.
2. **La asignación real de esa acción**, después de cualquier rebinding que haya hecho el
   jugador — el dato que hoy [04 · 25 §5](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#5--reasignar-controles-rebinding)
   solo esboza para teclado, y que este documento amplía en §3.5 para que también cubra el
   mando, porque sin eso no hay icono de mando que enseñar.

§3.6 combina ambas cosas en una sola función, `prompt_boton(_accion)`. Ningún otro punto del
código debería volver a escribir «pulsa X» a mano.

### 1.4 Fallar no debería repetir la misma frase: debe subir de volumen

Un jugador que ya ha visto una pista y sigue sin conseguirlo no necesita que se la repitas
igual: necesita **más información de la que tenía antes**. Repetir el mismo texto es lo que
hace que el jugador deje de leer los mensajes del juego a partir del tercero. La escalada de
§2.4/§3.4 propone tres niveles — discreto, claro, demostración — enganchados a un contador de
fallos por pista, reutilizando otra vez `flag_sumar()` de 13/12 §6.2 en vez de inventar un
segundo sistema de contadores.

---

## 2 · El método, paso a paso

### 2.1 El catálogo de pasos de tutorial, como datos

Igual que el resto de la biblioteca resiste la tentación de repartir lógica de diseño en
`if` sueltos, cada pista de tutorial es una fila de una tabla, no una función distinta:

| Campo | Qué es |
|---|---|
| `id` | Clave única y estable — es también la clave del *flag* de «visto» y de «fallos» |
| `requiere` | Nombre de un *flag* narrativo que debe ser verdadero para que la pista tenga sentido (`""` = ninguno) |
| `accion` | La acción del mapa de controles que el *prompt* debe dibujar (§3.5) |
| `texto` | La frase, ya pasada por `txt()` ([04 · 21](./21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md)) — **nunca** lleva el nombre de una tecla dentro |

Que sea una tabla es lo que permite añadir la pista 40 sin tocar el motor que las dispara ni
el que las dibuja: solo se añade una fila.

### 2.2 Tres disparadores, y solo tres

| Disparador | Cuándo se usa | Vive en |
|---|---|---|
| **Zona** | El jugador entra en un área concreta del nivel — el caso típico: el primer hueco que exige saltar | `obj_disparador_tutorial` (§3.2), colocado a mano en el Room Editor |
| **Evento explícito** | Un momento del código que no es geográfico: recoger el arma, abrir el primer cofre, subir de nivel por primera vez | Una llamada directa a `tutorial_mostrar_inicial(_id)` desde ese punto del código |
| **Fallo repetido** | El jugador ya vio la pista inicial (por el disparador que sea) y sigue sin lograrlo | `tutorial_fallo(_id)` (§3.4), llamado desde donde el juego detecta el fallo — un pinchazo, una caída, un enemigo que lo mata |

Los dos primeros muestran la pista **una vez**. El tercero es el único que puede repetirse, y
solo porque escala: nunca repite el mismo mensaje dos veces seguidas (§3.4).

### 2.3 Persistencia, y qué pasa en New Game+

Todo lo que este documento marca como «visto» o «cuántas veces ha fallado» son *flags* con
prefijo `tutorial_visto_` y `fallos_tutorial_`, dentro del mismo `global.flags` plano de
13/12 §6.2. Eso significa que se guardan y se cargan **gratis**: no hay que escribir una sola
línea nueva de persistencia, porque `save_game()` /
[`scr_save_load`](<../06 - Assets y Scripts/scr_save_load.gml>) ya serializa `global.flags`
entero como parte de la partida, junto con el resto de la historia.

La pregunta que sí es una decisión de diseño, y que ningún documento de la biblioteca había
respondido: **¿qué pasa con esos *flags* al empezar un New Game+?** Si `flags_iniciar()` los
resetea todos —lo correcto para la historia, que vuelve a cero—, un jugador que ya sabe saltar
y esquivar vuelve a ver la pista de saltar en la sala 1. La recomendación de este documento,
implementada en §3.3: **el New Game+ conserva el namespace `tutorial_visto_*`** (el jugador ya
demostró que sabe jugar) y **resetea todo lo demás** (la historia, las misiones, el resto de
*flags*). Si tu New Game+ cambia una mecánica de forma sustancial —un juego que en NG+ da un
arma nueva desde el minuto uno—, borra a mano solo los *flags* de esa mecánica concreta antes
de continuar; no hay una regla universal, pero sí una por defecto razonable.

### 2.4 El *widget* de *prompts*: la asignación real, no la de fábrica

El contrato de datos que necesita cualquier *prompt* de botón es mínimo: por cada acción, qué
tecla de teclado y qué botón de mando tiene asignados **ahora mismo**. El esbozo de
[04 · 25 §5](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#5--reasignar-controles-rebinding)
guarda hoy solo la tecla (`global.controles[$ accion] = _tecla`), porque ese documento no
pretendía ser completo — su encargo es otro. §3.5 amplía esa misma estructura (mismo nombre,
`global.controles`) para que cada entrada lleve **también** el botón de mando, porque sin eso
no hay icono de mando que dibujar. El día que `04/25 §5` implemente el rebinding real, solo
tiene que escribir en esta misma estructura con `control_asignar_teclado()` /
`control_asignar_mando()` en vez de tocar el struct a pelo.

Sobre esa base, `prompt_boton(_accion)` (§3.6) combina el dispositivo activo
(`global.ui_dispositivo`) con la asignación real y devuelve qué sprite y qué fotograma dibujar
— o, si esa tecla o botón concretos no tienen icono en la hoja, una **etiqueta de texto de
verdad** en vez de un icono elegido al azar (§3.6, y el error #3 de §5).

**Política de desaparición.** Un *prompt* contextual («pulsa E para abrir») que se queda para
siempre en pantalla dos horas después de que el jugador ya lo domina es ruido visual. §3.6
cuenta los **usos con éxito** de cada acción (no las veces que se ve el *prompt*: las veces que
el jugador **la ejecuta**) con el mismo `flag_sumar()` de 13/12, y deja de mostrarlo a partir
de un umbral.

### 2.5 El recordatorio de objetivo y de controles

Las Game Accessibility Guidelines lo piden en el nivel Cognitive Intermediate: *«Indicate /
allow reminder of controls during gameplay»* y *«Indicate / allow reminder of current
objectives during gameplay»* (ver Fuentes). La resolución práctica es un panel que el jugador
puede abrir en cualquier momento —no solo la primera vez— con una tecla dedicada, que muestra
dos cosas: el objetivo activo en una frase, y la lista de acciones básicas con su *prompt* real
(el mismo widget de §2.4, reutilizado). El objetivo en sí **no se reinventa**: §3.7 lee el
`QuestLog` de [04 · 04 §6](./04%20-%20RPG%20_%20Action%20RPG.md) o el gestor de misiones de
[13 · 12 §6.5](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md#65-un-gestor-de-misiones-mínimo-con-estado-fallada>)
si el proyecto ya tiene uno de los dos, y solo cae a una variable de texto libre si no hay
ninguno.

### 2.6 El ajuste «saltar tutorial»

Es una preferencia de la **persona**, no de la partida: quien ya se sabe el juego de una
versión anterior no quiere volver a verlo en la siguiente. Por eso vive en `ajustes.ini`
—junto al volumen y el idioma, en el mismo array de datos de
[04 · 25](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#los-ajustes-son-datos-otra-vez)—
y no dentro del guardado de partida. La trampa a evitar: si el jugador lo activa a mitad de
partida, las pistas que ya se dispararon **no deben reaparecer** cuando lo desactive más
tarde — por eso, como se ve en §3.2, el *flag* de «visto» se marca **siempre**, esté o no
activado el ajuste; lo único que cambia es si el mensaje llega a dibujarse.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 `scr_tutorial` — el catálogo y el arranque

```gml
// ============================================================================
// scr_tutorial.gml
// El catálogo de pistas de tutorial, como datos, y las constantes de escalada.
// Verificado: struct_exists, is_undefined, show_debug_message
// ============================================================================

#macro TUTORIAL_UMBRAL_PISTA_CLARA   2   // fallos para pasar de "discreto" a "claro"
#macro TUTORIAL_UMBRAL_DEMOSTRACION  4   // fallos para pasar a "demostración"
#macro TUTORIAL_ENFRIAMIENTO_SEG     20  // no repitas la MISMA pista antes de esto

/// @func tutorial_iniciar()
/// @desc Llamar UNA vez, al arrancar el juego (junto a dispositivo_iniciar() y
///       controles_iniciar(), ver el orden en §3.9). El catálogo es constante:
///       no cambia entre partidas, solo el progreso guardado en global.flags.
function tutorial_iniciar() {
    global.tutorial_pasos = {
        primer_salto: {
            requiere: "",
            accion:   "saltar",
            texto:    txt("tut_primer_salto"),
        },
        primer_dash: {
            requiere: "dash",              // el mismo flag de gating de 13/01 §5.3
            accion:   "dash",
            texto:    txt("tut_primer_dash"),
        },
        primer_ataque: {
            requiere: "",
            accion:   "atacar",
            texto:    txt("tut_primer_ataque"),
        },
    };

    // último aviso mostrado por pista, para el enfriamiento del §3.4
    global.tutorial_ultimo_aviso = {};

    global.tutorial_pista_activa = undefined;   // panel de nivel 2 (§3.4)
    global.tutorial_demo_activa  = undefined;   // panel de nivel 3 (§3.4)
}

/// @func tutorial_paso_valido(_id)
/// @desc Comprobación defensiva: un id que no está en el catálogo no debe reventar
///       el juego, solo avisar en consola. Usarla al principio de cualquier función
///       de este documento que reciba un _id desde fuera (un disparador, un evento).
function tutorial_paso_valido(_id) {
    if (struct_exists(global.tutorial_pasos, _id)) return true;
    show_debug_message($"tutorial: el paso '{_id}' no existe en global.tutorial_pasos");
    return false;
}
```

> 💡 **El catálogo es una tabla, el progreso son *flags*.** Nunca guardes el catálogo (los
> textos, a qué acción apunta cada pista): eso vive en código y se actualiza con el juego.
> Lo único que se guarda es "¿ha pasado esto ya?", y eso son los *flags* de §3.3.

### 3.2 `obj_disparador_tutorial` — el disparador de zona

Mismo patrón que `obj_disparador_zona` de
[13 · 12 §6.3](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md#63-disparadores-cuándo-se-lanza-un-nodo>),
adaptado a tutorial: en vez de lanzar un nodo de diálogo, muestra una pista y consume el
*flag* de «visto» **incluso si el ajuste «saltar tutorial» está activo** — ese es el punto
que evita la avalancha retroactiva descrita en §2.6.

```gml
// ---------------------------------------------------------------------------
// obj_disparador_tutorial  (Sprite: una caja invisible. Visible = false)
// Variables de instancia (Room Editor → Variable Definitions):
//    tutorial_id : String  — clave en global.tutorial_pasos
// Verificado: place_meeting, instance_destroy
// ---------------------------------------------------------------------------

/// Step
if (!place_meeting(x, y, obj_jugador)) exit;
if (!tutorial_paso_valido(tutorial_id)) { instance_destroy(); exit; }

var _paso = global.tutorial_pasos[$ tutorial_id];
if (_paso.requiere != "" && !flag_leer(_paso.requiere)) exit;   // aún no toca: sigue armado

// flag_una_vez() marca "visto" YA, se muestre el mensaje o no (§2.6)
if (!flag_una_vez($"tutorial_visto_{tutorial_id}")) { instance_destroy(); exit; }

if (!global.saltar_tutorial) tutorial_mostrar_inicial(tutorial_id);
instance_destroy();
```

```gml
/// @func tutorial_mostrar_inicial(_id)
/// @desc El primer contacto con una mecánica: siempre el nivel más discreto,
///       un toast de 13/05 §3.5i. No pasa por la escalada de fallos: eso
///       empieza a partir de la SEGUNDA vez que el jugador se topa con el problema.
function tutorial_mostrar_inicial(_id) {
    if (!tutorial_paso_valido(_id)) return;
    aviso_lanzar(global.tutorial_pasos[$ _id].texto, "info");
}
```

> ⚠️ **`instance_destroy()` y no un flag de instancia.** El disparador de zona se destruye a sí
> mismo tras el primer paso útil (mostrado o no); si el jugador vuelve a esa sala, el `flag_una_vez`
> ya guardado impide que un disparador nuevo (la sala se recarga entera) vuelva a disparar. Si tu
> proyecto no destruye instancias al salir de la sala (instancias persistentes), esto es
> automático y no hace falta tocar nada.
>
> 🔺 **El disparador de "evento explícito" de §2.2 no necesita objeto propio.** Es literalmente
> `if (!flag_una_vez($"tutorial_visto_{id}")) exit;` seguido de `tutorial_mostrar_inicial(id)`,
> puesto a mano en el punto del código donde ocurre el evento (recoger el arma, abrir el
> cofre). No dupliques `obj_disparador_tutorial` para eso.

### 3.3 La persistencia: reutilizar los *flags* de 13/12, con New Game+

Nada que guardar aparte — el único código nuevo es la función de New Game+ que decide qué
sobrevive:

```gml
/// @func flags_iniciar_new_game_plus()
/// @desc Empieza una partida nueva PERO conserva lo que el jugador ya demostró
///       saber: el namespace tutorial_visto_* no se resetea. Es una decisión de
///       diseño (§2.3), no un detalle técnico: cámbiala si tu NG+ lo necesita.
/// Verificado: variable_global_exists, struct_get_names, array_length,
///             string_pos, struct_set, struct_exists
function flags_iniciar_new_game_plus() {
    var _tutoriales_vistos = {};

    if (variable_global_exists("flags")) {
        var _nombres = struct_get_names(global.flags);
        for (var _i = 0; _i < array_length(_nombres); _i++) {
            var _n = _nombres[_i];
            if (string_pos("tutorial_visto_", _n) == 1) {
                struct_set(_tutoriales_vistos, _n, global.flags[$ _n]);
            }
        }
    }

    flags_iniciar();   // 13 · 12 §6.2 — resetea global.flags a los valores de partida nueva

    var _claves = struct_get_names(_tutoriales_vistos);
    for (var _i = 0; _i < array_length(_claves); _i++) {
        var _c = _claves[_i];
        struct_set(global.flags, _c, _tutoriales_vistos[$ _c]);
    }
}
```

> 💡 **`fallos_tutorial_*` SÍ se resetea en New Game+**, a propósito: es una medida de cuánto
> le costó al jugador la primera vez, no de si ya sabe jugar. Solo `tutorial_visto_*` se
> preserva. Si el New Game+ de tu juego cambia una mecánica en concreto, borra a mano ese
> `tutorial_visto_<mecánica>` de `_tutoriales_vistos` antes de la segunda pasada del bucle.

### 3.4 La escalada de pistas tras N fallos

Aquí es donde entra en juego el contador. `tutorial_fallo(_id)` es la única función que el
resto del proyecto necesita llamar — desde donde sea que el juego detecte que el jugador
falló la cosa que la pista `_id` explica.

```gml
// ============================================================================
// La escalada — tres niveles, el mismo flag_sumar() de 13/12 §6.2
// Verificado: get_timer, struct_exists, variable_global_exists, is_undefined,
//             delta_time, dsin, current_time
// ============================================================================

/// @func tutorial_fallo(_id)
/// @desc Llamar cuando el jugador falla lo que la pista _id enseña (cae en la
///       trampa, muere al enemigo, no consigue el salto). Sube el contador
///       SIEMPRE, aunque el ajuste "saltar tutorial" esté activo — pero solo
///       muestra algo si no lo está.
/// @returns {Real} El número de fallos acumulados (útil para depurar o para telemetría,
///                 ver 13 · 01 §9.5).
function tutorial_fallo(_id) {
    if (!tutorial_paso_valido(_id)) return 0;

    var _fallos = flag_sumar($"fallos_tutorial_{_id}");
    if (!global.saltar_tutorial) {
        var _nivel = tutorial_nivel_pista(_id);
        if (_nivel >= 2) __tutorial_escalar(_id, _nivel);
    }
    return _fallos;
}

/// @func tutorial_nivel_pista(_id)
/// @returns {Real} 1 = discreto (ya mostrado por el disparador inicial) ·
///                 2 = pista clara (panel persistente) · 3 = demostración
function tutorial_nivel_pista(_id) {
    var _fallos = flag_leer($"fallos_tutorial_{_id}", 0);
    if (_fallos >= TUTORIAL_UMBRAL_DEMOSTRACION)  return 3;
    if (_fallos >= TUTORIAL_UMBRAL_PISTA_CLARA)   return 2;
    return 1;
}

/// @func __tutorial_escalar(_id, _nivel)  — uso interno de tutorial_fallo()
/// @desc Aplica el enfriamiento: no repitas la MISMA pista antes de
///       TUTORIAL_ENFRIAMIENTO_SEG, o cada muerte en el mismo sitio dispara un
///       panel encima de otro.
function __tutorial_escalar(_id, _nivel) {
    var _ahora  = get_timer();                                    // microsegundos
    var _ultimo = struct_exists(global.tutorial_ultimo_aviso, _id)
                 ? global.tutorial_ultimo_aviso[$ _id] : 0;

    if (_ahora - _ultimo < TUTORIAL_ENFRIAMIENTO_SEG * 1000000) return;
    global.tutorial_ultimo_aviso[$ _id] = _ahora;

    var _paso = global.tutorial_pasos[$ _id];
    if (_nivel == 2) {
        global.tutorial_pista_activa = { id: _id, paso: _paso, vida: 5.0, alfa: 0 };
    } else {
        global.tutorial_demo_activa = { id: _id, paso: _paso, tiempo: 0 };
    }
}
```

```gml
/// obj_juego · Step (controlador persistente) — actualizar los paneles activos
function tutorial_actualizar() {
    var _dt = delta_time / 1000000;

    if (!is_undefined(global.tutorial_pista_activa)) {
        var _t = global.tutorial_pista_activa;
        _t.vida -= _dt;
        _t.alfa  = (_t.vida > 0.4) ? aproximar(_t.alfa, 1, 0.08) : aproximar(_t.alfa, 0, 0.10);
        if (_t.vida <= 0 && _t.alfa < 0.02) global.tutorial_pista_activa = undefined;
    }

    if (!is_undefined(global.tutorial_demo_activa)) {
        global.tutorial_demo_activa.tiempo += _dt;
        if (global.tutorial_demo_activa.tiempo > 4.0) global.tutorial_demo_activa = undefined;
    }
}

/// obj_juego · Draw GUI — dibujar el nivel que esté activo (nunca los dos a la vez)
function tutorial_dibujar() {
    if (!is_undefined(global.tutorial_pista_activa)) {
        var _t = global.tutorial_pista_activa;
        var _p = ancla(0.5, 0.75);
        draw_set_alpha(_t.alfa);
        panel_dibujar(spr_panel_pista, _p.px - 200, _p.py, 400, 64, c_white, _t.alfa);
        prompt_dibujar(_t.paso.accion, _t.paso.texto, _p.px - 170, _p.py + 20);
        draw_set_alpha(1);
        return;   // los dos niveles nunca coinciden: la demostración solo llega tras la clara
    }

    if (!is_undefined(global.tutorial_demo_activa)) {
        var _d = global.tutorial_demo_activa;
        var _p = ancla(0.5, 0.5);
        var _pulso = global.a11y.reduce_motion ? 1 : (1 + 0.15 * dsin(current_time * 0.3));

        panel_dibujar(spr_panel_demo, _p.px - 260, _p.py - 120, 520, 240);
        draw_set_font(fnt_ui_titulo);
        draw_set_halign(fa_center);
        draw_text(_p.px, _p.py - 90, txt("tut_demostracion_titulo"));
        draw_set_font(fnt_ui);
        draw_text_ext(_p.px - 220, _p.py - 55, _d.paso.texto, -1, 440);

        var _prompt = prompt_boton(_d.paso.accion);
        if (_prompt.icono) {
            draw_sprite_ext(_prompt.sprite, _prompt.frame, _p.px, _p.py + 60,
                            _pulso, _pulso, 0, c_white, 1);
        } else {
            draw_text(_p.px, _p.py + 60, _prompt.etiqueta);
        }
        draw_set_halign(fa_left);
    }
}
```

> 🔺 **El panel de nivel 2 y el de nivel 3 nunca se dibujan a la vez**, y el `return` de
> `tutorial_dibujar()` lo garantiza. No son capas que se suman: son la MISMA idea, cada vez
> con más detalle. Mostrar los dos juntos duplicaría el mensaje y contradiría el §1.4.
>
> 💡 **`dsin(current_time * 0.3)`** da un pulso continuo y barato (sin *alarms*, sin *time
> sources*) para llamar la atención sobre el icono de la demostración — y respeta
> `global.a11y.reduce_motion` de [04 · 27](./27%20-%20Accesibilidad.md) cayendo a una escala
> fija de 1 en vez de pulsar, igual que hace `barra_dibujar()` en 13/05 §3.5b con el temblor.

**Conectar la escalada con el resto del juego** — un ejemplo real, no de una vez desconectada:

```gml
/// obj_pincho · Collision con obj_jugador
jugador_morir();                 // lo que ya haga tu juego al morir
tutorial_fallo("primer_salto");  // avisa a la escalada: esta muerte cuenta para esta pista
```

### 3.5 `scr_controles` — la asignación real de cada acción

```gml
// ============================================================================
// scr_controles.gml
// El mapa de acción → tecla real / botón de mando real. Amplía la forma de
// datos que 04/25 §5 empieza a esbozar (hoy solo guarda la tecla) para que el
// widget de prompts de §3.6 tenga también el botón de mando.
// Verificado: struct_exists
// ============================================================================

/// @func controles_iniciar()
/// @desc Los valores de fábrica. Llamar antes que tutorial_iniciar() (§3.9).
function controles_iniciar() {
    global.controles = {
        saltar:      { teclado: vk_space,   mando: gp_face1 },
        dash:        { teclado: vk_shift,   mando: gp_shoulderr },
        atacar:      { teclado: ord("F"),   mando: gp_face3 },
        interactuar: { teclado: ord("E"),   mando: gp_face2 },
        abrir_ayuda: { teclado: vk_f1,      mando: gp_select },
    };
}

/// @func control_asignar_teclado(_accion, _tecla)
/// @desc Lo que el rebinding de 04/25 §5 debe llamar al capturar una tecla nueva,
///       en vez de escribir `global.controles[$ accion] = _tecla` directamente.
function control_asignar_teclado(_accion, _tecla) {
    if (!struct_exists(global.controles, _accion)) global.controles[$ _accion] = { teclado: vk_nokey, mando: -1 };
    global.controles[$ _accion].teclado = _tecla;
}

/// @func control_asignar_mando(_accion, _boton)
function control_asignar_mando(_accion, _boton) {
    if (!struct_exists(global.controles, _accion)) global.controles[$ _accion] = { teclado: vk_nokey, mando: -1 };
    global.controles[$ _accion].mando = _boton;
}

/// @func control_tecla(_accion)
/// @returns {Real} vk_nokey si la acción no existe: nunca revienta.
function control_tecla(_accion) {
    return struct_exists(global.controles, _accion) ? global.controles[$ _accion].teclado : vk_nokey;
}

/// @func control_boton_mando(_accion)
/// @returns {Real} -1 si la acción no existe.
function control_boton_mando(_accion) {
    return struct_exists(global.controles, _accion) ? global.controles[$ _accion].mando : -1;
}
```

> ⚠️ **Esto NO sustituye a 04/25 §5.** Sigue siendo ese documento el que debe capturar la
> tecla o el botón que pulsa el jugador durante el modo "esperando rebind" (con
> `keyboard_lastkey`, según su propio esbozo) y resolver conflictos entre acciones. Lo único
> que aporta esta sección es la **forma de datos** de destino — teclado y mando en la misma
> entrada — para que el widget de prompts de §3.6 pueda leerla. Guarda `global.controles`
> igual que cualquier otro ajuste ([04 · 25 §4](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#4--guardar-y-cargar-los-ajustes)):
> es una preferencia de la persona, no de la partida.

### 3.6 `scr_ui_prompt` — el widget que lee dispositivo + asignación

```gml
// ============================================================================
// scr_ui_prompt.gml
// El icono de botón correcto: dispositivo activo (13/05 §2.3) + asignación
// real (§3.5). Si la tecla o el botón concretos no tienen icono en la hoja,
// cae a una ETIQUETA DE TEXTO — nunca a un icono elegido al azar (ver error #3
// de §5: no existe keyboard_key_to_string ni nada parecido en el runtime).
// Verificado: is_undefined, struct_exists, string, chr, ord, max,
//             draw_sprite, draw_sprite_ext, draw_text, draw_text_ext,
//             draw_rectangle_color, draw_set_halign, draw_set_valign
// ============================================================================

/// @func __prompt_frame_teclado(_vk)  — uso interno
/// @returns {Real} Fotograma en spr_iconos_teclado, o -1 si no hay icono para esa tecla.
function __prompt_frame_teclado(_vk) {
    static MAPA = undefined;
    if (is_undefined(MAPA)) {
        MAPA = {};
        MAPA[$ string(vk_space)]   = 0;
        MAPA[$ string(vk_shift)]   = 1;
        MAPA[$ string(vk_control)] = 2;
        MAPA[$ string(vk_enter)]   = 3;
        MAPA[$ string(vk_escape)]  = 4;
        MAPA[$ string(vk_tab)]     = 5;
        MAPA[$ string(vk_up)]      = 6;
        MAPA[$ string(vk_down)]    = 7;
        MAPA[$ string(vk_left)]    = 8;
        MAPA[$ string(vk_right)]   = 9;
        MAPA[$ string(vk_f1)]      = 10;
        MAPA[$ string(ord("W"))]   = 11;
        MAPA[$ string(ord("A"))]   = 12;
        MAPA[$ string(ord("S"))]   = 13;
        MAPA[$ string(ord("D"))]   = 14;
        MAPA[$ string(ord("E"))]   = 15;
        MAPA[$ string(ord("F"))]   = 16;
    }
    var _c = string(_vk);
    return struct_exists(MAPA, _c) ? MAPA[$ _c] : -1;
}

/// @func __prompt_frame_mando(_boton)  — uso interno
/// @returns {Real} Fotograma en la hoja de icono_boton(), o -1 si no está mapeado.
function __prompt_frame_mando(_boton) {
    static MAPA = undefined;
    if (is_undefined(MAPA)) {
        MAPA = {};
        MAPA[$ string(gp_face1)]      = 0;
        MAPA[$ string(gp_face2)]      = 1;
        MAPA[$ string(gp_face3)]      = 2;
        MAPA[$ string(gp_face4)]      = 3;
        MAPA[$ string(gp_shoulderl)]  = 4;
        MAPA[$ string(gp_shoulderr)]  = 5;
        MAPA[$ string(gp_shoulderlb)] = 6;
        MAPA[$ string(gp_shoulderrb)] = 7;
        MAPA[$ string(gp_start)]      = 8;
        MAPA[$ string(gp_select)]     = 9;
        MAPA[$ string(gp_padu)]       = 10;
        MAPA[$ string(gp_padd)]       = 11;
        MAPA[$ string(gp_padl)]       = 12;
        MAPA[$ string(gp_padr)]       = 13;
        MAPA[$ string(gp_stickl)]     = 14;
        MAPA[$ string(gp_stickr)]     = 15;
    }
    var _c = string(_boton);
    return struct_exists(MAPA, _c) ? MAPA[$ _c] : -1;
}

/// @func control_nombre_teclado(_vk)
/// @desc Etiqueta de texto de una tecla, para cuando no hay icono (§5, error #3).
///       No existe una función del runtime que haga esto — se comprobó y no está
///       (ver el pie de "anti-alucinación" al final del documento) — así que es
///       una tabla a mano más el rango A-Z / 0-9 vía chr().
function control_nombre_teclado(_vk) {
    static MAPA = undefined;
    if (is_undefined(MAPA)) {
        MAPA = {};
        MAPA[$ string(vk_space)]   = txt("tecla_espacio");
        MAPA[$ string(vk_shift)]   = txt("tecla_mayus");
        MAPA[$ string(vk_control)] = txt("tecla_ctrl");
        MAPA[$ string(vk_alt)]     = txt("tecla_alt");
        MAPA[$ string(vk_enter)]   = txt("tecla_enter");
        MAPA[$ string(vk_escape)]  = txt("tecla_esc");
        MAPA[$ string(vk_tab)]     = txt("tecla_tab");
        MAPA[$ string(vk_up)]      = "↑";
        MAPA[$ string(vk_down)]    = "↓";
        MAPA[$ string(vk_left)]    = "←";
        MAPA[$ string(vk_right)]   = "→";
    }
    var _c = string(_vk);
    if (struct_exists(MAPA, _c)) return MAPA[$ _c];
    if (_vk >= ord("A") && _vk <= ord("Z")) return chr(_vk);   // letras: el propio código vale
    if (_vk >= ord("0") && _vk <= ord("9")) return chr(_vk);   // dígitos
    return "?";                                                 // honesto antes que roto
}

/// @func prompt_boton(_accion)
/// @desc El dato completo que necesita cualquier sitio que dibuje un prompt.
/// @returns {Struct} { sprite, frame, icono (Bool), etiqueta (String, solo si !icono) }
function prompt_boton(_accion) {
    var _mando = (global.ui_dispositivo == "mando");
    var _spr   = icono_boton(_accion);   // 13/05 §2.3 — hoja según dispositivo Y marca

    if (_mando) {
        var _frame = __prompt_frame_mando(control_boton_mando(_accion));
        return { sprite: _spr, frame: max(_frame, 0), icono: (_frame != -1), etiqueta: "" };
    }

    var _frame = __prompt_frame_teclado(control_tecla(_accion));
    return {
        sprite: _spr, frame: max(_frame, 0), icono: (_frame != -1),
        etiqueta: control_nombre_teclado(control_tecla(_accion)),
    };
}

/// @func prompt_dibujar(_accion, _texto, _px, _py)
/// @desc Icono + texto, en coordenadas de GUI. Si la tecla/botón no tiene
///       icono, dibuja una etiqueta de texto en una placa — NUNCA el fotograma
///       0 de la hoja a ciegas, porque sería el icono de OTRA tecla (error #3, §5).
function prompt_dibujar(_accion, _texto, _px, _py) {
    var _p = prompt_boton(_accion);

    draw_set_halign(fa_left);
    draw_set_valign(fa_middle);

    if (_p.icono) {
        draw_sprite(_p.sprite, _p.frame, _px + 16, _py + 16);
    } else {
        draw_rectangle_color(_px, _py, _px + 32, _py + 32, c_dkgray, c_dkgray, c_dkgray, c_dkgray, false);
        draw_set_halign(fa_center);
        draw_text(_px + 16, _py + 16, _p.etiqueta);
        draw_set_halign(fa_left);
    }
    draw_text_ext(_px + 40, _py + 16, _texto, -1, 300);
    draw_set_valign(fa_top);
}

#macro PROMPT_MAX_APARICIONES 5   // tras usarlo con éxito 5 veces, se asume aprendido

/// @func prompt_debe_mostrarse(_accion)
/// @desc Política de desaparición del §2.4: cuenta ÉXITOS, no visualizaciones.
function prompt_debe_mostrarse(_accion) {
    if (global.saltar_tutorial) return false;
    return flag_leer($"usos_prompt_{_accion}", 0) < PROMPT_MAX_APARICIONES;
}

/// @func prompt_marcar_usado(_accion)
/// @desc Llamar cuando el jugador EJECUTA la acción con éxito, no cuando se
///       ve el prompt (si no, nunca sube el contador y nunca desaparece).
function prompt_marcar_usado(_accion) {
    flag_sumar($"usos_prompt_{_accion}");
}
```

Ejemplo de uso completo, un cofre que enseña a interactuar y deja de insistir:

```gml
/// obj_cofre · Draw  (mundo, no GUI: el prompt sigue al objeto en pantalla)
if (place_meeting(x, y, obj_jugador) && prompt_debe_mostrarse("interactuar")) {
    prompt_dibujar("interactuar", txt("prompt_abrir_cofre"), x - 60, y - 50);
}

/// obj_cofre · Collision con obj_jugador, al pulsar interactuar
if (interactuar_pulsado()) {          // tu propia comprobación de input
    abrir_cofre();
    prompt_marcar_usado("interactuar");
}
```

> ⚠️ **`prompt_dibujar()` se ha escrito en el ejemplo del cofre dentro del evento `Draw`, no
> `Draw GUI`.** Es la excepción a la regla de 13/05: un *prompt* que sigue a un objeto del
> mundo (un cofre, un NPC) se dibuja en coordenadas de mundo. El *widget* de §3.7 (el panel de
> ayuda) sí vive en Draw GUI porque es fijo en pantalla. Mismo `prompt_boton()`, sitio distinto.

### 3.7 El panel de objetivo y controles

```gml
// ============================================================================
// scr_panel_ayuda.gml
// «¿Qué estaba haciendo?» — accesible en cualquier momento con abrir_ayuda,
// no solo la primera vez. GAG Cognitive Intermediate: recordatorio de
// controles Y de objetivo, las dos cosas (ver Fuentes).
// Verificado: variable_global_exists, array_length, keyboard_check_pressed,
//             gamepad_button_check_pressed
// ============================================================================

global.panel_ayuda_abierto = false;

/// @func panel_ayuda_alternar()
function panel_ayuda_alternar() {
    global.panel_ayuda_abierto = !global.panel_ayuda_abierto;
}

/// obj_juego · Step
if (keyboard_check_pressed(control_tecla("abrir_ayuda"))
    || gamepad_button_check_pressed(0, control_boton_mando("abrir_ayuda"))) {
    panel_ayuda_alternar();
}

/// @func objetivo_actual_texto()
/// @desc Adaptador: usa el sistema de misiones que YA tenga el proyecto antes
///       de caer al genérico. En orden: QuestLog de 04 · 04 §6, gestor de
///       misiones de 13 · 12 §6.5, variable de texto libre.
function objetivo_actual_texto() {
    if (variable_global_exists("quest_log") && array_length(global.quest_log.activas) > 0) {
        return global.quest_log.activas[0].objetivo;                    // 04 · 04 §6
    }
    if (variable_global_exists("misiones")) {
        var _activas = global.misiones.activas();
        if (array_length(_activas) > 0) return txt($"mision_{_activas[0]}_objetivo");  // 13 · 12 §6.5
    }
    return variable_global_exists("objetivo_actual") ? global.objetivo_actual : txt("sin_objetivo");
}

/// @func objetivo_fijar(_texto)
/// @desc Solo hace falta si el proyecto NO usa ninguno de los dos sistemas de
///       misiones de arriba: una única variable de texto libre.
function objetivo_fijar(_texto) { global.objetivo_actual = _texto; }

/// obj_juego · Draw GUI  — dibujar el panel si está abierto
function panel_ayuda_dibujar() {
    if (!global.panel_ayuda_abierto) return;

    var _p = ancla(0.5, 0.5);
    var _ancho = 560, _alto = 420;
    panel_dibujar(spr_panel_ayuda, _p.px - _ancho * 0.5, _p.py - _alto * 0.5, _ancho, _alto);

    var _ix = _p.px - _ancho * 0.5 + 30;
    var _iy = _p.py - _alto * 0.5 + 24;

    draw_set_font(fnt_ui_titulo);
    draw_text(_ix, _iy, txt("ayuda_objetivo_titulo"));
    draw_set_font(fnt_ui);
    draw_text_ext(_ix, _iy + 30, objetivo_actual_texto(), -1, _ancho - 60);

    draw_set_font(fnt_ui_titulo);
    draw_text(_ix, _iy + 110, txt("ayuda_controles_titulo"));
    draw_set_font(fnt_ui);

    static ACCIONES_BASICAS = ["saltar", "dash", "atacar", "interactuar", "abrir_ayuda"];
    for (var _i = 0; _i < array_length(ACCIONES_BASICAS); _i++) {
        var _accion = ACCIONES_BASICAS[_i];
        prompt_dibujar(_accion, txt($"accion_{_accion}"), _ix, _iy + 140 + _i * 36);
    }
}
```

> 💡 **El panel NO pasa por `global.saltar_tutorial`.** Es un recordatorio bajo demanda, no una
> enseñanza no pedida: un jugador que ha desactivado el tutorial sigue queriendo poder
> comprobar qué tecla es cada cosa. Son ajustes distintos a propósito.
>
> 🔺 **¿Pausar mientras el panel está abierto?** Este documento no lo decide por ti: en un
> juego de un jugador tiene sentido invocar `pausar_de_verdad()` de
> [04 · 41 §3.1](./41%20-%20Transiciones,%20carga%20y%20pausa.md#31-pausar-de-verdad-el-cimiento-que-usan-las-otras-dos-piezas)
> al abrir el panel; en uno con temporizador o multijugador, probablemente no puedas. La
> decisión es del género, no de este widget.

### 3.8 El ajuste «saltar tutorial» en la pantalla de Opciones

Encaja en el array de datos de
[04 · 25 — «Los ajustes son datos»](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#los-ajustes-son-datos-otra-vez)
como una fila más, sin tocar el motor de esa pantalla:

```gml
/// obj_opciones · Create — una fila más en el array `ajustes` de 04/25
array_push(ajustes, {
    tipo: "toggle", clave: "saltar_tutorial",
    etiqueta: txt("op_saltar_tutorial"), val: false,
});
```

```gml
/// dentro de aplicar_ajuste() de 04/25 §2 — un case más en el mismo switch
case "saltar_tutorial":
    global.saltar_tutorial = _w.val;
    break;
```

`guardar_ajustes()` / `cargar_ajustes()` de 04/25 §4 ya recorren el array entero: no hace
falta ni una línea más para que se guarde. El único cuidado es la inicialización, cubierta en
§3.9: `global.saltar_tutorial` debe nacer en `false` en `tutorial_iniciar()`, **antes** de que
`cargar_ajustes()` lo sobreescriba con lo que el jugador eligió la última vez.

> 💡 **Ofrécelo también al empezar partida, no solo en Opciones.** Un jugador que abre el
> juego por primera vez no va a encontrar el menú de Opciones antes de jugar. Muchos juegos
> preguntan «¿Ya conoces los controles?» en la pantalla de Nueva Partida, con las mismas dos
> opciones que este *toggle* — es la misma variable, un segundo sitio desde el que fijarla.

### 3.9 Orden de arranque: quién llama a quién

Todo lo de este documento depende de que otros sistemas ya estén en pie. El orden, para
insertar en el arranque general de
[04 · 00 §Anatomía](./00%20-%20Anatomía%20de%20un%20juego%20completo.md):

```gml
/// obj_juego · Create  (controlador persistente, primera room)
flags_iniciar();          // 13 · 12 §6.2 — el struct global.flags tiene que existir primero
dispositivo_iniciar();    // 13 · 05 §2.3 — global.ui_dispositivo
controles_iniciar();      // §3.5         — global.controles, valores de fábrica
avisos_iniciar();         // 13 · 05 §3.5i — el toast que usa tutorial_mostrar_inicial()
tutorial_iniciar();       // §3.1         — el catálogo, y saltar_tutorial = false por defecto
global.saltar_tutorial = false;

cargar_ajustes();         // 04 · 25 §4 — PUEDE sobreescribir saltar_tutorial con lo guardado
```

```gml
/// obj_juego · Step  (controlador persistente)
dispositivo_actualizar();   // 13 · 05 §2.3
tutorial_actualizar();      // §3.4
avisos_actualizar();        // 13 · 05 §3.5i

/// obj_juego · Draw GUI  (controlador persistente, o un obj_hud dedicado)
avisos_dibujar();            // 13 · 05 §3.5i
tutorial_dibujar();          // §3.4
panel_ayuda_dibujar();       // §3.7
```

---

## 4 · Checklist

**Disparadores**
- [ ] Cada pista tiene una fila en `global.tutorial_pasos`, con `requiere`, `accion` y `texto` — nada de lógica repartida en `if` sueltos
- [ ] El disparador de zona comprueba `requiere` ANTES de `flag_una_vez()`, para no consumir el flag antes de tiempo
- [ ] El disparador de evento explícito reutiliza `tutorial_mostrar_inicial()`, no duplica el objeto de zona

**Persistencia y New Game+**
- [ ] «Visto» y «fallos» viven en `global.flags` (13/12 §6.2): se guardan gratis con `save_game()`
- [ ] El New Game+ pasa por `flags_iniciar_new_game_plus()`, no por `flags_iniciar()` a secas
- [ ] Se ha decidido (y documentado en el propio proyecto) si alguna mecánica nueva de NG+ necesita borrar su `tutorial_visto_*` a mano

**Escalada**
- [ ] `tutorial_fallo(_id)` se llama desde el sitio real donde el jugador falla, no desde un temporizador genérico
- [ ] Los tres niveles muestran MÁS información cada vez, nunca el mismo texto repetido
- [ ] Hay enfriamiento entre repeticiones de la misma pista (`TUTORIAL_ENFRIAMIENTO_SEG`)
- [ ] Los paneles de nivel 2 y 3 nunca se dibujan a la vez

**Prompts**
- [ ] `prompt_boton()` lee `global.ui_dispositivo` (13/05 §2.3) Y `global.controles` (§3.5) — nunca una tecla escrita a mano en el texto
- [ ] Si no hay icono para una tecla/botón concreto, se dibuja una etiqueta de texto, nunca el fotograma 0 por defecto
- [ ] Los *prompts* contextuales cuentan ÉXITOS (`prompt_marcar_usado`), no apariciones, para decidir cuándo desaparecer
- [ ] Ningún texto traducido lleva el nombre de una tecla incrustado (rompe con el rebinding y con la traducción)

**Recordatorio y ajuste**
- [ ] El panel de ayuda es accesible en cualquier momento, no solo en el tutorial inicial
- [ ] `objetivo_actual_texto()` usa el sistema de misiones que el proyecto ya tenga, no uno paralelo
- [ ] «Saltar tutorial» vive en `ajustes.ini` (persona), no en el guardado de partida (progreso)
- [ ] El *flag* de «visto» se marca aunque «saltar tutorial» esté activo, para no inundar de pistas si se desactiva después

---

## 5 · Errores clásicos y cómo evitarlos

1. **Guardar «ya lo vio» en una variable que no viaja en el guardado.** Sobrevive a la sesión,
   no a cerrar el juego: la pista reaparece en la siguiente partida cargada. Usa `global.flags`
   (§1.2, §3.3).
2. **Escribir la tecla dentro del texto traducido** (`"Pulsa ESPACIO para saltar"`, ya en la
   cadena de `txt()`). Se rompe en cuanto el jugador reasigna esa acción, y además obliga a
   retraducir el texto en cada idioma si cambias la tecla de fábrica. El texto describe la
   acción; el icono/etiqueta de la tecla lo pone `prompt_boton()` aparte (§1.3, §3.6).
3. **Asumir que si no hay icono mapeado, el fotograma 0 sirve.** No sirve: es el icono de
   *otra* tecla, y enseña algo falso. `prompt_boton()` devuelve `icono: false` para ese caso
   exacto, y `prompt_dibujar()` cae a una etiqueta de texto (§3.6).
4. **Repetir el mismo mensaje en cada fallo.** Es indistinguible de que el juego no se entera
   de que el jugador ya lo intentó. La escalada de tres niveles (§1.4, §3.4) existe para esto,
   y sin enfriamiento se dispara un panel encima de otro en la misma sesión de intentos.
5. **Un contador de "usos del prompt" que cuenta VISUALIZACIONES en vez de ÉXITOS.** Un
   jugador que ve el *prompt* del cofre 5 veces sin conseguir abrirlo (por ejemplo, porque no
   tiene la llave) no ha aprendido nada, y el *prompt* desaparecería justo cuando más falta
   hace. `prompt_marcar_usado()` se llama al ÉXITO, no al dibujado (§2.4, §3.6).
6. **Que "saltar tutorial" bloquee el disparador entero, sin pasar por `flag_una_vez()`.** Si
   el chequeo de `global.saltar_tutorial` está ANTES de marcar el flag, cada pista se queda
   "sin ver" mientras el ajuste está activo. El día que el jugador lo desactive a mitad de
   partida, todas se disparan de golpe. El orden correcto marca el flag siempre y solo decide
   con el ajuste si se **dibuja** (§2.6, §3.2).
7. **Un panel de recordatorio que reconstruye su propio sistema de misiones.** Si el proyecto
   ya tiene un `QuestLog` (04/04 §6) o un gestor de misiones (13/12 §6.5), el panel debe leer
   de ahí. Mantener un `global.objetivo_actual` en paralelo es la forma más rápida de que se
   desincronicen los dos (§2.5, §3.7).
8. **Guardar «saltar tutorial» en el archivo de partida en vez de en `ajustes.ini`.** Es una
   preferencia de quien juega, no del personaje: debe seguir activa en la partida siguiente,
   incluso en un slot nuevo (§2.6).
9. **Inventar `keyboard_key_to_string()` o algo parecido para poner nombre a una tecla.** No
   existe en el runtime 2026.0.0.23 — comprobado con `buscar.py` — y tampoco existe nada
   equivalente para mando. La única vía es una tabla a mano (`control_nombre_teclado()`, §3.6)
   más el rango A-Z/0-9 con `chr()`.

---

## Ver también

- [00 · Anatomía de un juego completo](./00%20-%20Anatomía%20de%20un%20juego%20completo.md) — dónde encaja el arranque de sistemas globales de §3.9
- [13 · 01 §5 — Onboarding: enseñar sin texto](<../13 - Diseño y producción de videojuegos/01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md#5--onboarding-enseñar-sin-texto>) — el diseño que este documento traduce en código
- [13 · 05 §2.3 — manda el último dispositivo usado](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#23-ratón-táctil-y-mando-a-la-vez-manda-el-último-dispositivo-usado>) — `dispositivo_actualizar()`, `icono_boton()`, `marca_de_mando()`
- [13 · 05 §3.2 — el lienzo de la GUI](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#32-el-lienzo-fija-la-gui-y-no-vuelvas-a-escribir-un-píxel-absoluto>) — `ancla()`, `zona_segura()`
- [13 · 05 §3.4 — paneles nine-slice](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#34-paneles-nine-slice-un-sprite-pequeño-para-cualquier-tamaño>) — `panel_dibujar()`, reutilizado en todos los paneles de este documento
- [13 · 05 §3.5i — notificaciones apiladas](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#i-notificaciones-apiladas-toasts>) — `aviso_lanzar()`, el nivel 1 de la escalada
- [13 · 12 §6.2 — los flags narrativos](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md#62-los-flags-un-struct-global-plano-y-guardable>) — `flag_leer`, `flag_poner`, `flag_sumar`, `flag_una_vez`, reutilizados enteros
- [13 · 12 §6.3 — disparadores narrativos](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md#63-disparadores-cuándo-se-lanza-un-nodo>) — el patrón de `obj_disparador_zona` del que parte `obj_disparador_tutorial`
- [13 · 12 §6.5 — el gestor de misiones](<../13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md#65-un-gestor-de-misiones-mínimo-con-estado-fallada>) — una de las dos fuentes de `objetivo_actual_texto()`
- [04 · 04 §6 — QuestLog](./04%20-%20RPG%20_%20Action%20RPG.md) — la otra fuente de `objetivo_actual_texto()`
- [04 · 21 — Localización](./21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md) — `txt()`, usada en todos los textos de este documento
- [04 · 25 §5 — Reasignar controles](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#5--reasignar-controles-rebinding) — dónde debe escribirse `control_asignar_teclado()` / `control_asignar_mando()`
- [04 · 25 — Los ajustes son datos](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#los-ajustes-son-datos-otra-vez) — dónde encaja el *toggle* «saltar tutorial»
- [04 · 27 — Accesibilidad](./27%20-%20Accesibilidad.md) — `global.a11y.reduce_motion`, respetado en el pulso de la demostración
- [04 · 41 — Transiciones, carga y pausa](./41%20-%20Transiciones,%20carga%20y%20pausa.md) — `pausar_de_verdad()`, opcional al abrir el panel de ayuda
- [06 · scr_save_load.gml](<../06 - Assets y Scripts/scr_save_load.gml>) — cómo se guarda de verdad el struct que contiene `global.flags`

---

## Fuentes

Consultadas el **2026-09-06**.

- Game Accessibility Guidelines, listado completo —
  <https://gameaccessibilityguidelines.com/full-list/> (abierta con `curl -A "Mozilla/5.0" ...`,
  gamemaker.io y este sitio bloquean el user-agent por defecto): cita literal de las pautas
  usadas en este documento — *«Allow controls to be remapped / reconfigured»* (Motor, Basic,
  base de §1.3), *«Include interactive tutorials»* (Cognitive, Basic), *«Indicate / allow
  reminder of controls during gameplay»* y *«Indicate / allow reminder of current objectives
  during gameplay»* (Cognitive, Intermediate, base de §2.5), *«Include contextual in-game
  help / guidance / tips»* (Cognitive, Intermediate). ⚠️ La escalada de pistas en tres niveles
  (§1.4, §3.4) es práctica de diseño extendida en el oficio, no una pauta específica de esta
  lista: no se encontró una guideline textual que la codifique.
- Manual oficial de GameMaker (espejo local, `09 - Manual oficial/manual-lts-2026-en/`),
  [`gamepad_get_description`](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/GamePad_Input/gamepad_get_description.htm)
  (abierta con `curl`) — *«This string is hardware dependant»*: la cita exacta que ya usa
  13/05 §2.3 para justificar por qué `marca_de_mando()` es una heurística, y que este
  documento hereda al construir el icono de mando sobre esa misma función.
- `_indice/simbolos.json` de esta biblioteca (extraído del `GmlSpec.xml` del runtime GMS2
  2026.0.0.23) — fuente de verdad para cada símbolo citado en este documento, consultado con
  `python3 _indice/buscar.py <símbolo>` uno por uno antes de escribirlo.

---

**Anti-alucinación — símbolos que se comprobaron y NO existen** (para que ningún LLM futuro,
incluido el que reescriba este documento, los vuelva a intentar): `keyboard_key_to_string`,
`keyboard_get_name`, `keyboard_key_name`, `vk_to_string` (las cuatro formas obvias de pedirle
al runtime el nombre de una tecla — ninguna existe; de ahí la tabla a mano de
`control_nombre_teclado()`), `gamepad_button_get_name`, `gamepad_get_button_name`,
`gamepad_get_axis_name` (lo mismo para un botón o eje de mando), `layer_get_id_from_name`
(existe `layer_get_id`, que toma el nombre directamente — no hace falta la otra), `flag_get`,
`flags_get_all` (los *flags* de 13/12 §6.2 se leen con `flag_leer`, en singular, y no hay
función para volcarlos todos de golpe: se usa `struct_get_names(global.flags)` si hace falta
iterarlos, como en `flags_iniciar_new_game_plus()`), `struct_get_or_default` (no existe;
el patrón es `struct_exists(...) ? ... : valor_por_defecto`, tal y como ya hace `flag_leer`),
`input_get_binding` (nombre plausible para una API de la librería **Input** de JujuAdams, pero
no es del runtime ni de esta biblioteca: si usas Input, consulta su propia documentación para
el equivalente real en vez de suponer este nombre).
