# 17 · SnowState — máquinas de estado (guía en español)

> **SnowState 3.1.4** (de @sohomsahaun) es la máquina de estados finitos más usada de GameMaker:
> ganó el *Helpful Dev Jam* y fue finalista a *Best Tool* en los GameMaker Awards 2024. Su
> documentación oficial está solo en inglés (wiki de GitHub); esta es una **guía en español**
> con la API verificada contra el código descargado en
> `11 - Código descargado/librerias/maquinas-de-estados/SnowState`.
>
> Traducción y adaptación propia · API extraída del código, no inventada.

---

## ¿Por qué una librería y no la máquina de estados a mano?

Esta biblioteca ya trae una FSM propia en 40 líneas ([`scr_state_machine`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml)),
y para un juego pequeño sobra. **SnowState** aporta lo que cuesta escribir bien: **transiciones
con reglas**, **herencia de estados**, **historial** y **eventos de entrada/salida** limpios.
Cuando el personaje tiene 10+ estados (idle, correr, saltar, caer, atacar, esquivar, herido…),
mantener eso a mano se vuelve frágil; SnowState lo ordena.

---

## 1 · Crear la máquina y sus estados

```gml
/// obj_player · Create — el patrón real de SnowState
fsm = new SnowState("idle");     // el argumento es el estado INICIAL

fsm
    .add("idle", {
        enter: function() { sprite_index = spr_player_idle; },   // al ENTRAR en el estado
        step:  function() {                                      // cada frame en el estado
            if (abs(hsp) > 0) fsm.change("run");
            if (salto)        fsm.change("jump");
        },
        leave: function() { /* al SALIR del estado */ },
    })
    .add("run", {
        enter: function() { sprite_index = spr_player_run; },
        step:  function() {
            if (hsp == 0) fsm.change("idle");
            if (salto)    fsm.change("jump");
        },
    })
    .add("jump", {
        enter: function() { vsp = -salto_fuerza; },
        step:  function() {
            if (vsp > 0) fsm.change("fall");
        },
    });
```

```gml
/// obj_player · Step — una sola línea ejecuta el estado actual
fsm.step();     // llama al `step` del estado en el que estés ahora
```

> 💡 **`enter` / `step` / `leave` son los tres momentos de un estado.** `enter` se ejecuta UNA
> vez al llegar (poner el sprite, dar el impulso de salto); `step` cada frame; `leave` una vez
> al irse (limpiar). Es lo que hace el código legible: cada estado sabe lo suyo.

---

## 2 · Cambiar de estado

```gml
fsm.change("jump");                 // ir a otro estado (dispara leave del actual + enter del nuevo)

fsm.get_current_state();            // en qué estado estás ("jump")
fsm.get_previous_state();           // de dónde venías
fsm.state_is("jump");               // ¿estoy en este estado? (booleano)
fsm.get_time();                     // cuántos frames llevas en el estado actual
```

> 🔺 **`change` NO ejecuta el `step` del nuevo estado en el mismo frame** por defecto: primero
> hace `leave` del viejo y `enter` del nuevo. El `step` nuevo corre en el siguiente `fsm.step()`.

---

## 3 · Transiciones con reglas (lo que ahorra código)

En vez de escribir los `if ... change` a mano en cada `step`, defines **transiciones**: reglas
de «de este estado, a este otro, cuando pase esto».

```gml
/// una transición con nombre: de "idle" a "attack" cuando se dispara el trigger "atacar"
fsm.add_transition("idle", "attack", "atacar");
fsm.add_transition("run",  "attack", "atacar");

/// y en el input, disparas el trigger en vez de llamar a change:
if (input_ataque) fsm.trigger("atacar");   // salta a "attack" desde idle O run
```

- **`add_reflexive_transition`** — una transición de un estado a sí mismo (reiniciar la
  animación de ataque si vuelves a pulsar).
- **`add_wildcard_transition`** — desde **cualquier** estado (un «recibir daño» que interrumpe
  lo que estés haciendo).

```gml
/// desde CUALQUIER estado, al recibir daño, ir a "hurt"
fsm.add_wildcard_transition("hurt", "danio");
// … y al recibir daño:
fsm.trigger("danio");
```

> 💡 **Las transiciones separan el "cuándo" del "qué".** El input dispara triggers; la máquina
> decide a qué estado ir según el estado actual. Añadir un estado nuevo no obliga a tocar los
> demás.

---

## 4 · Herencia de estados (`add_child` / `inherit`)

Estados que comparten comportamiento: `jump` y `fall` se mueven igual en el aire, solo cambia el
sprite. En vez de repetir, uno hereda del otro.

```gml
fsm.add("airborne", {
    step: function() { x += hsp; vsp += gravedad; y += vsp; },   // física común del aire
});
fsm.add_child("airborne", "jump", {
    enter: function() { sprite_index = spr_jump; },
});
fsm.add_child("airborne", "fall", {
    enter: function() { sprite_index = spr_fall; },
});
// "jump" y "fall" ejecutan el step de "airborne" + lo suyo
```

---

## 5 · Historial (`history_*`)

SnowState recuerda por qué estados has pasado —útil para «volver al estado anterior» (salir de
un menú, terminar un ataque y volver a lo que hacías).

```gml
fsm.history_enable();              // activarlo (desactivado por defecto)
fsm.history_set_max_size(8);       // cuántos estados recordar
var _anteriores = fsm.history_get();
```

---

## La API completa (verificada en el código)

| Método | Qué hace |
|---|---|
| `new SnowState(estado_inicial)` | Crea la máquina |
| `.add(nombre, struct)` | Añade un estado con `enter`/`step`/`leave` |
| `.add_child(padre, nombre, struct)` | Estado que hereda de otro |
| `.change(estado)` | Cambia de estado |
| `.step()` | Ejecuta el `step` del estado actual (en el Step del objeto) |
| `.add_transition(de, a, trigger)` | Transición con regla |
| `.add_reflexive_transition` / `.add_wildcard_transition` | A sí mismo / desde cualquiera |
| `.trigger(nombre)` | Dispara un trigger (activa las transiciones que casen) |
| `.get_current_state` / `.get_previous_state` / `.get_states` | Consultar estados |
| `.state_is(estado)` / `.state_exists(estado)` | Comprobaciones |
| `.get_time` / `.set_time` | Frames en el estado actual |
| `.history_enable` / `_disable` / `_get` / `_set_max_size` | Historial |
| `.inherit` / `.on` / `.enter` / `.leave` | Herencia y eventos avanzados |

> 🔺 **Estos métodos NO están en `buscar.py`** (no son del runtime, son de la librería). Para
> verificar una firma, mira el código: `11 - Código descargado/librerias/maquinas-de-estados/SnowState/scripts/SnowState/SnowState.gml`.

---

## Ver también

- [`scr_state_machine`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) — la FSM propia de esta biblioteca, para cuando SnowState es demasiado
- [23 · IA de enemigos y steering](../04%20-%20Recetas%20por%20género/23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) — la FSM como pegamento entre comportamientos
- [02 · Librerías esenciales de la comunidad](./02%20-%20Librerías%20esenciales%20de%20la%20comunidad.md) — el resto del ecosistema
- Wiki oficial (inglés): <https://github.com/sohomsahaun/SnowState/wiki>
