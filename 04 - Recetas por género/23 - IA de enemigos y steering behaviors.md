# 23 · IA de enemigos y steering behaviors

> Enemigos que persiguen, huyen, rodean, patrullan, deambulan o se agrupan. Los *steering
> behaviors* son el vocabulario del movimiento con intención: piezas pequeñas que se combinan.
>
> **Cobertura parcial detectada:** había FSM (plataformas, shmup), A* con `mp_grid` (Tower
> Defense) y homing, pero no una receta dedicada de seek/flee/arrive/wander/flocking. Aquí está.

---

## El patrón común: dirección deseada → movimiento

Todo steering behavior calcula **hacia dónde quiere ir** el enemigo, y el movimiento sale de
ahí. La herramienta base es `point_direction` + `lengthdir`:

```gml
/// perseguir (seek): ir hacia el objetivo
var _dir = point_direction(x, y, objetivo.x, objetivo.y);
x += lengthdir_x(velocidad, _dir);
y += lengthdir_y(velocidad, _dir);
```

> 💡 **`lengthdir_x/y(longitud, dirección)`** convierte «avanzar N en el ángulo D» en un
> desplazamiento x/y. Es la función más útil de todo el movimiento 2D en GameMaker. En grados,
> con 0 = derecha y **subiendo en sentido antihorario** (0=der, 90=arriba, 180=izq, 270=abajo).

---

## 1 · Seek y Flee — perseguir y huir

```gml
/// scr_ia
function ir_hacia(_tx, _ty, _vel) {
    var _dir = point_direction(x, y, _tx, _ty);
    x += lengthdir_x(_vel, _dir);
    y += lengthdir_y(_vel, _dir);
    return _dir;   // devuelve el ángulo, útil para orientar el sprite
}

function huir_de(_tx, _ty, _vel) {
    var _dir = point_direction(_tx, _ty, x, y);   // ¡al revés!
    x += lengthdir_x(_vel, _dir);
    y += lengthdir_y(_vel, _dir);
    return _dir;
}
```

```gml
/// enemigo que persigue si te ve, huye si tiene poca vida
if (hp < hp_max * 0.2) {
    huir_de(obj_jugador.x, obj_jugador.y, velocidad * 1.2);   // acorralado, más rápido
} else if (point_distance(x, y, obj_jugador.x, obj_jugador.y) < rango_vision) {
    image_angle = ir_hacia(obj_jugador.x, obj_jugador.y, velocidad);
}
```

---

## 2 · Arrive — frenar al llegar (no orbitar el objetivo)

El *seek* puro pasa de largo y vuelve, orbitando. **Arrive** frena al acercarse:

```gml
function llegar_a(_tx, _ty, _vel, _radio_freno) {
    var _dist = point_distance(x, y, _tx, _ty);
    var _dir = point_direction(x, y, _tx, _ty);
    // dentro del radio de frenado, la velocidad baja proporcionalmente
    var _v = (_dist < _radio_freno) ? _vel * (_dist / _radio_freno) : _vel;
    x += lengthdir_x(_v, _dir);
    y += lengthdir_y(_v, _dir);
}
```

> 🔺 **Sin Arrive, los enemigos "vibran" sobre el objetivo.** Es el defecto que delata a un
> enemigo mal programado: llega, se pasa, vuelve, se pasa. El radio de frenado lo elimina.

---

## 3 · Wander — deambular con naturalidad

Un enemigo inactivo no debe quedarse quieto ni moverse en línea recta. **Wander** es un rumbo
que cambia poco a poco:

```gml
/// Create
rumbo = random(360);

/// Step — el rumbo deriva suavemente; nada de saltos bruscos
rumbo += random_range(-8, 8);
x += lengthdir_x(velocidad_paseo, rumbo);
y += lengthdir_y(velocidad_paseo, rumbo);

// rebotar en los bordes de la zona en vez de salirse
if (x < 32 || x > room_width - 32)  rumbo = 180 - rumbo;
if (y < 32 || y > room_height - 32) rumbo = -rumbo;
```

> 💡 **La clave del wander es `+= random_range(-8, 8)`, no `= random(360)`.** Cambiar el rumbo
> entero cada frame da un temblor epiléptico; derivarlo poco a poco da un vagar creíble.

---

## 4 · Evasión de obstáculos — `mp_potential_step`

Seek en línea recta se clava en las paredes. `mp_potential_step` va hacia el objetivo
**rodeando** los objetos que le indiques:

```gml
/// avanzar hacia el jugador esquivando obj_pared
mp_potential_step(obj_jugador.x, obj_jugador.y, velocidad, obj_pared);
```

📘 [`mp_potential_step`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Movement_And_Collisions/Motion_Planning/mp_potential_step.md)

> 💡 **Para un mapa con paredes, `mp_potential_step` es el atajo.** No es tan bueno como A*
> (`mp_grid_path`, ver [08 · Tower Defense](./08%20-%20Tower%20Defense.md)) para laberintos
> complejos, pero para «acércate esquivando» es una línea y funciona.

---

## 5 · Patrullas con Paths

Para rutas fijas (un guardia que da una ronda), el recurso **Path** es lo natural:

```gml
/// Create — asignar una ronda predefinida (dibujada en el editor de Paths)
path_start(pth_ronda, 2, path_action_reverse, true);  // recorre y vuelve
```

O construida por código:

```gml
mi_ruta = path_add();
path_add_point(mi_ruta, 100, 100, 100);
path_add_point(mi_ruta, 400, 100, 100);
path_add_point(mi_ruta, 400, 300, 100);
path_start(mi_ruta, 3, path_action_restart, true);
```

> 🔺 **`path_start` toma el control del movimiento del objeto.** Combínalo con estados: en
> estado «patrulla» usa el path; al ver al jugador, `path_end()` y pasa a «perseguir» con seek.
> El pegamento es la máquina de estados de [`scr_state_machine`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml).

---

## 6 · Flocking — bandadas y enjambres (básico)

Movimiento de grupo (murciélagos, peces, un enjambre): tres reglas sobre los vecinos cercanos.

```gml
/// Step — separación (no amontonarse) + cohesión (no dispersarse) + persecución
var _sep_x = 0, _sep_y = 0, _n = 0, _cx = 0, _cy = 0;
with (obj_enemigo) {
    if (id == other.id) continue;
    var _d = point_distance(x, y, other.x, other.y);
    if (_d < 48 && _d > 0) {
        _sep_x += (other.x - x) / _d;   // alejarse de los muy cercanos
        _sep_y += (other.y - y) / _d;
        _cx += x; _cy += y; _n++;        // centro del grupo, para cohesión
    }
}
// aplicar: separación (empuja fuera) + un poco hacia el centro del grupo + hacia el jugador
if (_n > 0) {
    x -= _sep_x * 0.6;  y -= _sep_y * 0.6;
    var _dir = point_direction(x, y, (_cx/_n)*0.3 + obj_jugador.x*0.7,
                                     (_cy/_n)*0.3 + obj_jugador.y*0.7);
    x += lengthdir_x(velocidad, _dir);
    y += lengthdir_y(velocidad, _dir);
}
```

> ⚠️ **Flocking es O(n²): cada enemigo mira a todos.** Con 20 va sobrado; con 300 se arrastra.
> Para enjambres grandes, limita el vecindario con una rejilla espacial o revisa solo una
> muestra. Ver [15 · Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md).

---

## Qué comportamiento para qué enemigo

| Enemigo | Comportamiento |
|---|---|
| Zombi lento | Seek directo |
| Guardia | Path (patrulla) → Seek al detectar |
| Enemigo a distancia | Arrive a rango medio + huir si te acercas |
| Fantasma que atraviesa paredes | Seek directo (sin evasión, a propósito) |
| Enemigo por mazmorra con paredes | `mp_potential_step` o A* |
| Murciélagos / enjambre | Flocking |
| Animal inofensivo | Wander |

---

## Ver también

- [08 · Tower Defense](./08%20-%20Tower%20Defense.md) — A* con `mp_grid_path` para caminos óptimos
- [`scr_state_machine`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) — el pegamento entre comportamientos (patrulla ↔ persigue ↔ huye)
- [02 · Top-Down / Twin-Stick](./02%20-%20Top-Down%20_%20Twin-Stick.md) — donde estos enemigos viven
