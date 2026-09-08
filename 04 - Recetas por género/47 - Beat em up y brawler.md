# 47 · Beat 'em up y brawler

> **Dificultad:** media-alta · **Construido sobre** [`04 · 46 — Eje Z falso`](./46%20-%20Eje%20Z%20falso%20-%20altura%2C%20sombras%20y%20profundidad%20en%20un%20juego%202D.md).
> *Streets of Rage*, *Final Fight*, *Fight'N Rage*, *River City Girls*, *Castle Crashers*. Este
> documento es el esqueleto que falta entre "sé mover un personaje en top-down" (`04 · 02`) y
> "tengo un brawler jugable": el carril donde se camina, cuándo un golpe conecta de verdad,
> cómo se organiza una horda para que no te maten en dos segundos, agarrar y lanzar, y el
> cooperativo local. **No repite** las cajas de golpe (`04 · 30`), el director de encuentros y
> el gestor de turnos de ataque (`04 · 33`), ni las cámaras (`13 · 19`) — los usa y dice
> exactamente en qué punto engancha con cada uno.

---

## 1 · Visión general

Un beat 'em up es, en el fondo, un top-down (`04 · 02`) con tres restricciones deliberadas que
lo convierten en otra cosa:

1. **El mundo no es libre en 360°.** Caminas por un pasillo, una calle o una arena, con una
   banda estrecha de profundidad — el **carril** (§2) — en vez del plano entero.
2. **El combate no se resuelve solo, se orquesta.** Sin una regla que reparta los turnos de
   ataque, seis enemigos rodeando al jugador le pegan los seis a la vez y el juego es
   injugable. Esa regla ya existe en esta biblioteca (`04 · 33` §3) y aquí se **usa**, no se
   repite.
3. **El espacio vertical existe, aunque el mundo sea 2D.** Saltar, ser lanzado por los aires,
   un agarre que te levanta del suelo: todo eso es el eje Z falso de `04 · 46`, aplicado al
   combate cuerpo a cuerpo.

**Lo que aporta este documento, y de dónde viene cada pieza que NO reinventa:**

| Sistema | Qué resuelve aquí | Reutiliza de |
|---|---|---|
| Carril de profundidad | Restringir el movimiento a una banda creíble, sin tocar el depth-sort | `04 · 02` §4.4 (sin cambios) |
| Alineación en Z | Que un barrido no golpee a quien ha saltado, y un ataque aéreo sí | `04 · 46` (`z`/`zvel`) |
| Hitbox del golpe en sí | — | `04 · 30` completo, sin repetir una línea |
| Oleadas con bloqueo de pantalla | Cuándo se cierra la arena y cuándo se abre | `13 · 19` §3.5 (zonas de cámara) + `06/scr_camera.gml` |
| Quién ataca y cuándo | — | `04 · 33` §3 (`GestorFichas`), reutilizado tal cual con radios de melé |
| Agarres y lanzamientos | Sistema nuevo — no existía en la biblioteca | Este documento |
| Cooperativo local | Input por jugador, cámara compartida | `13 · 19` §3.10 (`camara_grupo_bbox`) |
| Armas y objetos rompibles | Sistema nuevo, engancha en `04 · 30` y `04 · 39` | Este documento |
| Jefes y escenario que hace daño | Fases del jefe y aplicar daño | `04 · 32` §4.8 y §5.7 (`recibir_golpe`) |

**Subgéneros y su presión dominante:**

| Variante | Ejemplo | Qué cambia |
|---|---|---|
| Clásico de calle | *Streets of Rage*, *Final Fight* | Un carril estrecho, oleadas cerradas, combos cortos |
| *Brawler* de arena | *Fight'N Rage*, *Castle Crashers* | Arenas más anchas, combos largos, agarres centrales en el diseño |
| Cooperativo de fiesta | *River City Girls*, *TMNT: Shredder's Revenge* | El carril se ensancha para caber a 4 jugadores; la cámara hace `zoom-to-fit` |

---

## 2 · Arquitectura recomendada

```
obj_entidad_beatemup      (padre: hereda de obj_entidad_saltable de 04 · 46 + combate de 04 · 30)
├── obj_jugador           (uno por jugador; comparten equipo EQUIPO_JUGADOR de 04 · 30)
├── obj_enemigo           (padre de enemigos; usa GestorFichas de 04 · 33 §3)
│   ├── obj_enemigo_base
│   └── obj_jefe
├── obj_agarrado           (estado, no objeto propio — ver §6: la víctima sigue siendo
│                            su misma instancia, solo cambia de máquina de estados)
obj_arena_trigger          (dispara el bloqueo de pantalla y la oleada al entrar, §5)
obj_muro_invisible         (bloquea el avance mientras la arena está activa, §5)
obj_peligro_terreno        (pinchos, fuego, suelo electrificado — §10)
obj_arma_recogible         (§9)
obj_objeto_rompible        (§9)
```

### Configuración

```gml
// ---------------------------------------------------------------------------
// scr_brawler_config
// ---------------------------------------------------------------------------

// El carril de profundidad, en píxeles de room. Se puede sobrescribir por
// arena (§5) si un tramo del nivel necesita una banda distinta.
#macro CARRIL_ANCHO_DEFECTO   64

// Radios del gestor de fichas (04 · 33 §3), pensados para melé cuerpo a cuerpo:
// mucho más pequeños que en una arena abierta de disparos.
#macro BRAWLER_RADIO_ACERCARSE   48
#macro BRAWLER_RADIO_ATAQUE      28
```

---

## 3 · El carril de profundidad

### 3.1 · Qué es y por qué existe

En un top-down libre (`04 · 02`) el jugador puede alejarse en cualquier dirección. En un beat
'em up eso rompe la composición: el fondo del escenario está pintado con una perspectiva fija
(una calle, un pasillo de mazmorra) y un personaje que se aleja "hacia el fondo" más de la
cuenta atraviesa paredes pintadas o se sale del área que la cámara puede encuadrar bien. La
solución no es una pared física por todo el escenario: es una **banda de valores de `y`**
dentro de la cual el personaje puede moverse libremente, y fuera de la cual no se le deja
entrar.

```gml
/// obj_entidad_beatemup — Create (añadido a lo que ya trae obj_entidad_saltable de 04 · 46)
carril_y_min = 300;    // borde "de fondo" del carril, en píxeles de room
carril_y_max = 300 + CARRIL_ANCHO_DEFECTO;   // borde "de frente"
```

```gml
/// obj_entidad_beatemup — Step (después de mover con move_and_collide, igual que en 04 · 02)
y = clamp(y, carril_y_min, carril_y_max);
```

Es literalmente una línea. La razón de que merezca su propia sección no es la dificultad del
código sino la cantidad de sistemas que dependen de que exista: la cámara solo necesita seguir
`x` (la profundidad ya está acotada, así que casi nunca hace falta desplazarse en `y`), las
oleadas pueden colocar enemigos "detrás" del jugador sabiendo que ese detrás cabe en una banda
estrecha, y **el depth-sort no cambia ni una línea**: sigue siendo `depth = -bbox_bottom` de
`04 · 02` §4.4, porque la banda es tan estrecha que la diferencia de profundidad entre "delante"
y "detrás" dentro de ella ya la resuelve por sí sola sin ningún ajuste adicional.

### 3.2 · Carriles distintos por arena

No todo tramo del nivel necesita el mismo ancho de carril — una calle estrecha y una plaza
abierta antes de un jefe no deberían sentirse iguales. La misma zona que bloquea la cámara en
§5 (`obj_arena_trigger`) es quien fija el carril al entrar:

```gml
/// obj_arena_trigger — Create
carril_y_min = 280;
carril_y_max = 420;     // una plaza más ancha que el pasillo por defecto
```

```gml
/// obj_arena_trigger — evento Collision con obj_entidad_beatemup (other = el que entra)
other.carril_y_min = carril_y_min;
other.carril_y_max = carril_y_max;
```

### 3.3 · Escala por profundidad (opcional)

Un toque clásico de los brawlers de 16 bits — *Streets of Rage 2*, *Final Fight* — es escalar
ligeramente el sprite según la posición dentro del carril, para reforzar la sensación de que el
fondo del carril está "más lejos":

```gml
/// obj_entidad_beatemup — Step (tras el clamp del §3.1)
var _t = (y - carril_y_min) / max(1, carril_y_max - carril_y_min);   // 0 = fondo, 1 = frente
var _escala = lerp(0.92, 1.0, _t);
image_xscale = _escala * sign(image_xscale);
image_yscale = _escala;
```

Es puramente cosmético — no toca la máscara de colisión ni el `depth`-sort — y muchos brawlers
modernos lo omiten a propósito porque complica leer los golpes. Trátalo como una decisión de
estilo, no como parte obligatoria del sistema.

---

## 4 · Alineación en Z para que un golpe conecte

### 4.1 · El problema que el carril no resuelve

El carril del §3 decide si dos entidades están lo bastante cerca en profundidad. No dice nada
sobre la **altura**: en un brawler donde se puede saltar (`Streets of Rage 2` en adelante,
`Fight'N Rage`), un barrido bajo no debería golpear a quien está en el aire, y un ataque
"anti-aire" no debería golpear a quien sigue con los pies en el suelo. Esa es exactamente la
variable `z` de `04 · 46`, aplicada como filtro sobre el sistema de hitboxes que ya existe en
`04 · 30` — no lo sustituye, lo complementa con una comprobación previa.

```gml
// ---------------------------------------------------------------------------
// scr_brawler_combate
// ---------------------------------------------------------------------------

/// @func golpe_z_conecta(_victima_z, _def)
/// @desc ¿La altura de la víctima está dentro del rango vertical del ataque?
///       `_def` es la ENTRADA DE DATOS del ataque (una fila de global.ataques,
///       04 · 30 §5.1), a la que este documento le añade DOS campos nuevos en
///       §4.2: z_min y z_max. Un ataque normal cubre 0..999 (golpea a
///       cualquiera, esté saltando o no); uno "bajo" cubre solo 0..12; uno
///       "anti-aire" solo 16..999. La hitbox creada por caja_de_golpe_crear()
///       (04 · 30 §5.4) guarda esa misma entrada en su campo `def`, así que se
///       llama como golpe_z_conecta(victima.z, hitbox.def) — ver §4.2 más abajo.
/// @param {Real}   _victima_z  El `z` (04 · 46) de quien podría recibir el golpe.
/// @param {Struct} _def        La entrada de global.ataques, con z_min/z_max añadidos.
/// @returns {Bool}
function golpe_z_conecta(_victima_z, _def)
{
    var _zmin = variable_struct_exists(_def, "z_min") ? _def.z_min : 0;
    var _zmax = variable_struct_exists(_def, "z_max") ? _def.z_max : 999;
    return (_victima_z >= _zmin) && (_victima_z <= _zmax);
}
```

### 4.2 · Extender la tabla de ataques de `04 · 30`, sin tocar el documento

`04 · 30` §5.1 define `global.ataques` como datos — la tabla se construye una vez, al arrancar
el juego. Aquí no se reescribe esa tabla: se **amplían** las entradas que un brawler necesita,
en el propio archivo de datos del proyecto (`scr_ataques`, ya existente):

```gml
// scr_ataques (extiende las entradas ya definidas en 04 · 30 §5.1, mismo archivo del
// proyecto — no un documento nuevo)
global.ataques[$ "barrido_bajo"] = {
    dano : 6, empuje : 4.0, elevacion : 0, hitstun : 14, blockstun : 8,
    rompe_aguante : false, prioridad : 1,
    caja : { dx : 0.5, dy : 6, ancho : 30, alto : 8 },
    activo : 6, refresco : 20,
    z_min : 0, z_max : 12          // solo golpea a quien tiene los pies (casi) en el suelo
};

global.ataques[$ "golpe_ascendente"] = {
    dano : 9, empuje : 2.0, elevacion : 8, hitstun : 20, blockstun : 10,
    rompe_aguante : true, prioridad : 2,
    caja : { dx : 0.4, dy : -4, ancho : 24, alto : 26 },
    activo : 5, refresco : 26,
    z_min : 0, z_max : 999          // conecta con cualquiera, y ADEMÁS lanza (elevacion)
};
```

`caja_de_golpe_crear()` de `04 · 30` §5.4 no sabe nada de `z_min`/`z_max` — y no hace falta que
lo sepa: la comprobación se añade en la capa de detección, justo antes de llamar a
`recibir_golpe()`:

```gml
/// obj_hitbox — Step (envoltorio sobre el bucle de detección de 04 · 30 §5.6:
/// la MISMA lista de víctimas candidatas, con un filtro extra antes de golpear)
var _lista = ds_list_create();
instance_place_list(caja_x1, caja_y1, obj_entidad_beatemup, _lista, false);

for (var _i = 0; _i < ds_list_size(_lista); _i++)
{
    var _victima = _lista[| _i];
    // self.def es la entrada de global.ataques con la que 04 · 30 §5.4 creó esta
    // hitbox (caja_de_golpe_crear guarda "def : _def" en la instancia). Por eso
    // basta con haberle añadido z_min/z_max a los DATOS del ataque (§4.2): esta
    // línea los lee sin que caja_de_golpe_crear necesite saber que existen.
    if (!golpe_z_conecta(_victima.z, self.def)) continue;   // el filtro de este documento
    // A partir de aquí, exactamente el pipeline de 04 · 30 §5.6: caja contra caja
    // en coordenadas de mundo, comprobar ya_golpeados y, si toca, llamar a
    // recibir_golpe() sobre _victima. No se repite ese código aquí.
}
ds_list_destroy(_lista);
```

> ⚠️ `ds_list_create`/`ds_list_size`/`ds_list_destroy` son las únicas estructuras `ds_*` de todo
> este par de documentos, y solo porque `instance_place_list` las exige por firma — se destruyen
> en la misma línea en la que se agotan, tal y como pide `05 · Referencia`.

### 4.3 · El `elevacion` de `04 · 30`, redirigido a `zvel`

`04 · 30` §5.7 mueve `vel_y` directamente cuando un golpe tiene `elevacion != 0` — una
simplificación razonable para un hack-and-slash sin carril de profundidad, pero que en un
brawler con carril **saca a la víctima de su banda de movimiento** mientras está en el aire. La
corrección, ya anticipada como trampa en `04 · 46` §5 y §7, es una sola línea cambiada en el
punto exacto donde `04 · 30` aplica el lanzamiento:

```gml
// En vez de:  vel_y = _caja.elevacion * power(0.75, combate.juggles);
// en un brawler con eje Z falso:
zvel        = _caja.elevacion * power(0.75, combate.juggles);
en_el_suelo = false;
combate.juggles += 1;
```

`vel_x`/`vel_y` quedan libres para el empuje horizontal (`apply_knockback`, `04 · 15` §5.4) y
`zvel` se encarga de la parte vertical exactamente como en `04 · 46` §3.2 — el aterrizaje ya
sabe volver a enganchar al carril porque `y` nunca se movió del plano de suelo.

---

## 5 · Oleadas con bloqueo de pantalla y avance

### 5.1 · La arena, como zona de cámara reutilizada

El bloqueo de pantalla de un beat 'em up **es** el sistema de zonas de cámara de
[`13 · 19` §3.5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/19%20-%20Cámaras%20de%20juego%20-%20encuadre%2C%20seguimiento%20y%20control.md#35-region-based-anchors-zonas-de-cámara),
con un candado añadido: la cámara no se mueve a la siguiente zona hasta que la oleada actual
está muerta. `obj_camara_zona` y `cam_set_bounds` (`06/scr_camera.gml`) no cambian ni una línea
— lo que añade este documento es la condición de avance.

```gml
/// scr_brawler_encuentros_definir — llamar UNA vez, antes de que la sala cree los
/// obj_arena_trigger (p. ej. desde el Create de un obj_control_nivel con depth muy
/// negativo, o desde el Game Start si el nivel tiene una sola arena). Necesita que
/// `global.arquetipos` ya exista (04 · 33 §1, obj_control · Game Start) — si tu nivel
/// tiene más de una calle, añade aquí una entrada por cada `obj_arena_trigger`.
global.encuentros = {
    calle_01 : new EncuentroDef("calle_01", [
        new GrupoEncuentro(global.arquetipos.enjambre, 3),
        new GrupoEncuentro(global.arquetipos.muro,     1)
    ])
};
```

```gml
/// obj_arena_trigger — Create
encuentro    = global.encuentros.calle_01;   // EncuentroDef de 04 · 33 §2
resuelta     = false;
carril_y_min = 280;
carril_y_max = 420;

// Referencia directa a la instancia de obj_muro_invisible que sella la salida de
// ESTA arena. Se enlaza colocando ambas instancias en el Room Editor y apuntando
// una a la otra con "Creation Code" (muro_salida = <id de la instancia del muro>;)
// — el mismo patrón de enlace manual que ya usa 13 · 19 §3.5 entre zona y cámara.
muro_salida = noone;

/// obj_arena_trigger — evento Collision con obj_jugador (other = el jugador que entra)
if (!resuelta)
{
    resuelta = true;

    // 1. Bloquea la cámara a los límites de esta zona (13 · 19 §3.5 / scr_camera.gml).
    cam_set_bounds(obj_camara_director.cam, bbox_left, bbox_top, bbox_right, bbox_bottom);

    // 2. Sella la salida: el muro invisible enlazado a esta arena se vuelve sólido
    //    para que no se pueda esquivar la oleada saliendo por donde se entró.
    if (instance_exists(muro_salida)) { muro_salida.solid = true; }

    // 3. Puebla el encuentro (adaptador nuevo, hermano de los dos de 04 · 33 §6:
    //    aquí no hay "cuándo" por fotograma, un brawler suelta la oleada entera
    //    de golpe al cerrar la arena).
    encuentro_instanciar_en_arena(encuentro, bbox_left, bbox_right, carril_y_min, carril_y_max);
}
```

```gml
/// @func encuentro_instanciar_en_arena(_encuentro, _x_izq, _x_der, _y_min, _y_max)
/// @desc Tercer adaptador de EncuentroDef (04 · 33 §2), hermano de los dos de
///       04 · 33 §6: aquí el encuentro se puebla ENTERO de golpe, repartido por
///       el carril, en vez de por fotograma (shmup) o por intervalo (TD).
function encuentro_instanciar_en_arena(_encuentro, _x_izq, _x_der, _y_min, _y_max)
{
    for (var _i = 0; _i < array_length(_encuentro.grupos); _i++)
    {
        var _g = _encuentro.grupos[_i];
        for (var _j = 0; _j < _g.cantidad; _j++)
        {
            var _px = irandom_range(_x_izq + 32, _x_der - 32);
            var _py = irandom_range(_y_min, _y_max);
            instance_create_layer(_px, _py, "Instancias", _g.arquetipo.obj);
        }
    }
}
```

### 5.2 · El avance: solo cuando la oleada está muerta

```gml
/// obj_arena_trigger — Step (solo mientras resuelta == true)
if (resuelta && instance_number(obj_enemigo) == 0)
{
    // Libera la cámara: la siguiente zona (o la sala entera) vuelve a marcar límites.
    cam_set_bounds(obj_camara_director.cam, -1, -1, -1, -1);

    if (instance_exists(muro_salida)) { muro_salida.solid = false; }

    instance_destroy();   // esta arena ya cumplió su función
}
```

**Por qué `instance_number(obj_enemigo) == 0` y no una condición más fina**: es deliberado.
Cualquier lógica de "quedan pocos, ya se puede avanzar" (como el director de intensidad de
`04 · 33` §5 hace para el *ritmo* del combate) es una elección de diseño distinta a la de un
beat 'em up clásico, donde la promesa con el jugador es literal: *limpia la pantalla para
seguir*. Si tu juego quiere una versión más permisiva, cambia la condición aquí — no hace falta
tocar nada del director de `04 · 33`, que sigue disponible sin cambios si en algún tramo
prefieres su ritmo en vez del candado estricto.

---

## 6 · Agarres y lanzamientos

Sistema nuevo — no existía nada parecido en el resto de la biblioteca. Un agarre es una
máquina de estados de tres pasos: acercarse lo suficiente, agarrar (la víctima deja de moverse
por su cuenta y seguirse pegada a la posición del agarrador), y soltar — con daño, o con un
lanzamiento que usa el eje Z falso de `04 · 46` para el arco.

```gml
// ---------------------------------------------------------------------------
// scr_brawler_agarres
// ---------------------------------------------------------------------------

#macro BRAWLER_AGARRE_RADIO       20
#macro AGARRE_GOLPES_MAX  3      // cuántos golpes gratis se pueden dar agarrado antes de soltar

/// obj_entidad_beatemup — Create (variables de agarre, en todas las entidades)
agarrando_a  = noone;   // a quién agarro (solo tiene sentido en el agarrador)
agarrado_por = noone;   // quién me agarra (solo tiene sentido en la víctima)
agarre_golpes = 0;
```

```gml
/// obj_jugador — Step, al pulsar el botón de agarre
if (keyboard_check_pressed(vk_control) && agarrando_a == noone && agarrado_por == noone)
{
    var _obj = instance_place(x + lengthdir_x(BRAWLER_AGARRE_RADIO, image_angle),
                               y + lengthdir_y(BRAWLER_AGARRE_RADIO, image_angle),
                               obj_enemigo);

    if (_obj != noone && _obj.agarrado_por == noone && _obj.z <= 4)   // no se agarra en el aire
    {
        agarrando_a       = _obj;
        _obj.agarrado_por = id;
        _obj.combate.hitstun = 999999;   // inmovilizado mientras dure el agarre
    }
}
```

```gml
/// obj_entidad_beatemup — Step, para CUALQUIERA que esté agarrado (jugador o enemigo)
if (agarrado_por != noone)
{
    if (!instance_exists(agarrado_por)) { agarrado_por = noone; }
    else
    {
        // Se pega a una posición fija relativa al agarrador — no se mueve por su cuenta.
        x = agarrado_por.x + lengthdir_x(18, agarrado_por.image_angle);
        y = agarrado_por.y;
        z = agarrado_por.z;
    }
}
```

```gml
/// obj_jugador — Step, con un enemigo ya agarrado (agarrando_a != noone)
if (agarrando_a != noone)
{
    if (!instance_exists(agarrando_a)) { agarrando_a = noone; }
    else if (keyboard_check_pressed(ord("J")) && agarre_golpes < AGARRE_GOLPES_MAX)
    {
        // Golpe gratis mientras dura el agarre: daño directo, sin hitbox (ya está pegado).
        agarrando_a.combate.vida -= 4;
        agarre_golpes += 1;
        hit_complete(agarrando_a, 4, point_direction(x, y, agarrando_a.x, agarrando_a.y));   // 04 · 15 §5.7
    }
    else if (keyboard_check_pressed(ord("K")))
    {
        agarre_lanzar(id, agarrando_a, image_angle);
        agarrando_a = noone;
        agarre_golpes = 0;
    }
}
```

```gml
/// @func agarre_lanzar(_agarrador, _victima, _direccion)
/// @desc Suelta a la víctima con un lanzamiento en arco — el mismo sistema de
///       04 · 46 §3.9 (proyectil_arco_lanzar), aplicado a una entidad viva en
///       vez de a un proyectil nuevo.
function agarre_lanzar(_agarrador, _victima, _direccion)
{
    with (_victima)
    {
        agarrado_por          = noone;
        combate.hitstun       = 45;
        combate.vida         -= 10;

        // Arco de lanzamiento: reutiliza exactamente la parábola de 04 · 46 §3.9.
        var _v0 = sqrt(2 * GRAV_Z * 40);      // 40 px de altura máxima del vuelo
        vel_x   = lengthdir_x(6, _direccion);
        vel_y   = lengthdir_y(6, _direccion);
        zvel    = _v0;
        en_el_suelo = false;

        // Mientras vuela, puede golpear a quien encuentre por el camino: reutiliza
        // el mismo filtro de altura del §4.1, con z_min/z_max amplios (es un
        // "proyectil" grande, golpea a casi cualquiera que toque).
        estado_vuelo = true;
    }
}
```

```gml
/// obj_entidad_beatemup — Collision con obj_entidad_beatemup, solo si estado_vuelo
if (estado_vuelo && place_meeting(x, y, other) && other.equipo != equipo)
{
    other.combate.vida -= 6;         // daño de colisión al golpear a otro enemigo de paso
    hit_complete(other, 6, point_direction(x, y, other.x, other.y));
}
```

La sombra que se encoge bajo el enemigo lanzado, el impacto al aterrizar, el `z <= 0` que pone
fin al vuelo: todo eso ya está resuelto por `04 · 46` §3.2 y §3.5 sin cambiar una línea — el
agarre solo tenía que fijar `vel_x`/`vel_y`/`zvel` con los valores correctos al soltar.

---

## 7 · IA de turnos de ataque: rodean, y solo uno o dos atacan

Esta sección **no repite** `GestorFichas` (`04 · 33` §3) — lo instancia con radios de melé y le
añade el filtro de altura del §4. El «Kung-Fu Circle» y la «Belgian AI» de Michael Dawe que
`04 · 33` ya documenta a fondo son exactamente el comportamiento que un beat 'em up necesita:
los enemigos ocupan posiciones alrededor del jugador (`posicion_ranura`, que ya reparte los
huecos en círculo) y solo a los que tienen ficha de ataque libre se les concede el permiso de
golpear — con el hueco de escape (`04 · 33` §2) incluido de fábrica, así que el jugador nunca ve
un círculo completamente cerrado.

```gml
/// obj_control_nivel — Create (uno por partida; o uno por jugador si el nivel es cooperativo)
global.gestor_jugador = new GestorFichas(
    obj_jugador,                 // el objetivo — 04 · 33 exige una instancia o un struct con x/y
    3,                            // capacidad de rejilla: cuántos pueden acercarse a la vez
    2,                            // capacidad de ataque: cuántos pueden golpear a la vez
    BRAWLER_RADIO_ACERCARSE,      // radio de aproximación — melé, no arena abierta
    BRAWLER_RADIO_ATAQUE
);
```

```gml
/// obj_enemigo — Step (la misma máquina de tres fases de 04 · 33 §3, "Uso", con el
/// filtro de altura de este documento añadido en el momento de golpear)
switch (estado_ficha)
{
    case "acercandose":
        if (ranura == -1)
        {
            ranura = global.gestor_jugador.solicitar_acercarse(id, arquetipo.peso_rejilla,
                                                                 obj_enemigo);
            if (ranura == -1) break;
        }
        var _pos = global.gestor_jugador.posicion_ranura(ranura);
        mp_potential_step(_pos.x, _pos.y, 2, false);   // movimiento: 04 · 23
        y = clamp(y, carril_y_min, carril_y_max);       // el carril del §3 sigue aplicando

        if (point_distance(x, y, obj_jugador.x, obj_jugador.y) <= arquetipo.alcance)
        {
            estado_ficha = "pidiendo_ataque";
        }
        break;

    case "pidiendo_ataque":
        var _ok = global.gestor_jugador.solicitar_ataque(id, arquetipo.peso_ataque,
                                                           arquetipo.nombre, 1400, 900);
        if (_ok)
        {
            estado_ficha = "atacando";
            alarm[0] = arquetipo.telegrafia_fr;
        }
        break;

    case "atacando":
        break;   // el golpe real se lanza en la Alarm 0, igual que en 04 · 33 §3
}

/// obj_enemigo — Alarm 0
global.gestor_jugador.liberar_ataque(arquetipo.peso_ataque);
caja_de_golpe_crear(global.ataques[$ "barrido_bajo"], global.armas.punos);   // 04 · 30 §5.4
estado_ficha = "retirandose";
```

**Con dos jugadores, un gestor por jugador** — tal y como `04 · 33` §3 ya deja anotado
(«normalmente uno por jugador»): cada `GestorFichas` reparte su propia rejilla alrededor de su
objetivo, y cada enemigo elige con `instance_nearest` a qué jugador acosar antes de pedir su
ranura al gestor correspondiente. No hace falta ningún sistema nuevo — solo dos instancias del
mismo constructor.

⚠️ **Nombra el gestor de un solo jugador `global.gestor_p1`, no `global.gestor_jugador`, en
cuanto el nivel sea cooperativo** — y guarda la instancia del primer jugador en
`global.jugador_1`, tal y como la del segundo ya se guarda en `global.jugador_2` (§8.4), para
que ambas existan antes de que el primer enemigo pida su gestor abajo:

```gml
/// obj_jugador_1 — Create (el objeto fijo del primer jugador, ya colocado en la sala)
global.jugador_1 = id;
```

```gml
/// obj_control_nivel — Create, en un nivel cooperativo (sustituye al bloque de un solo
/// jugador de más arriba: mismos argumentos de GestorFichas, otro nombre y otro objetivo)
global.gestor_p1 = new GestorFichas(global.jugador_1, 3, 2,
                                     BRAWLER_RADIO_ACERCARSE, BRAWLER_RADIO_ATAQUE);
```

`global.gestor_p2` ya se crea aparte, al unirse el segundo jugador (§8.4).

```gml
/// obj_enemigo — Create, en un nivel cooperativo
var _blanco = instance_nearest(x, y, obj_jugador);
gestor_asignado = (_blanco == global.jugador_1) ? global.gestor_p1 : global.gestor_p2;
```

---

## 8 · Cooperativo local en el mismo teclado/mando

### 8.1 · Input por jugador, como datos

```gml
/// @func BrawlerInput(_dispositivo_gamepad, _arriba, _abajo, _izq, _der, _ataque, _agarre)
/// @desc -1 en _dispositivo_gamepad significa "usa teclado". Las teclas solo se
///       leen si _dispositivo_gamepad == -1.
function BrawlerInput(_dispositivo_gamepad, _arriba, _abajo, _izq, _der, _ataque, _agarre)
constructor
{
    dispositivo = _dispositivo_gamepad;
    k_arriba = _arriba; k_abajo = _abajo; k_izq = _izq; k_der = _der;
    k_ataque = _ataque; k_agarre = _agarre;

    static leer_x = function()
    {
        if (dispositivo == -1)
        {
            return keyboard_check(k_der) - keyboard_check(k_izq);
        }
        return gamepad_is_connected(dispositivo)
            ? sign(round(gamepad_axis_value(dispositivo, gp_axislh)))
            : 0;
    };

    static leer_y = function()
    {
        if (dispositivo == -1)
        {
            return keyboard_check(k_abajo) - keyboard_check(k_arriba);
        }
        return gamepad_is_connected(dispositivo)
            ? sign(round(gamepad_axis_value(dispositivo, gp_axislv)))
            : 0;
    };

    static ataque_pulsado = function()
    {
        return (dispositivo == -1)
            ? keyboard_check_pressed(k_ataque)
            : (gamepad_is_connected(dispositivo) && gamepad_button_check_pressed(dispositivo, gp_face1));
    };

    static agarre_pulsado = function()
    {
        return (dispositivo == -1)
            ? keyboard_check_pressed(k_agarre)
            : (gamepad_is_connected(dispositivo) && gamepad_button_check_pressed(dispositivo, gp_shoulderr));
    };
}
```

```gml
// scr_brawler_config — dos jugadores en el mismo teclado: WASD contra flechas
global.input_p1 = new BrawlerInput(-1, ord("W"), ord("S"), ord("A"), ord("D"), ord("J"), ord("K"));
global.input_p2 = new BrawlerInput(-1, vk_up, vk_down, vk_left, vk_right, vk_numpad1, vk_numpad2);
// O, con mando: new BrawlerInput(0, ...) para el jugador que use el primer gamepad conectado.
```

```gml
/// obj_jugador — Step
var _ix = entrada.leer_x();
var _iy = entrada.leer_y();
vel_x = _ix * 3;
vel_y = _iy * 3;
move_and_collide(vel_x, vel_y, obj_solido, 4, 0, 0, 8, 8);
if (entrada.ataque_pulsado()) { /* iniciar ataque, 04 · 30 §5.8 */ }
if (entrada.agarre_pulsado()) { /* §6 de este documento */ }
```

### 8.2 · Sin fuego amigo, por diseño de equipos

Ambos jugadores comparten `equipo = EQUIPO_JUGADOR` (la misma constante de `04 · 30` §5.0), así
que el pipeline de golpes de `04 · 30` §5.6 (`if (equipo == _caja.equipo) continue;`) ya evita
que se golpeen entre sí sin ningún código adicional en este documento.

### 8.3 · La cámara: reutiliza el `zoom-to-fit`, no lo repite

Con un solo jugador la cámara sigue una posición. Con dos, la técnica correcta ya está resuelta
en [`13 · 19` §3.10](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/19%20-%20Cámaras%20de%20juego%20-%20encuadre%2C%20seguimiento%20y%20control.md#310-cámara-multijugador-con-zoom-dinámico):
`camara_grupo_bbox(obj_jugador)` da el centro y la caja del grupo, y el zoom se ajusta para que
quepan los dos sin salirse de los límites de la arena activa (§5). No hace falta ni una línea
nueva: la única entrada de este documento es que `obj_jugador` ya existe con ese nombre.

### 8.4 · Unirse a mitad de partida

Un detalle clásico del género (créditos de máquina recreativa): un segundo jugador puede
aparecer sin reiniciar el nivel.

```gml
/// obj_control_nivel — Step, o al pulsar Iniciar en el segundo mando
if (!instance_exists(global.jugador_2) && gamepad_button_check_pressed(1, gp_face1))
{
    global.jugador_2 = instance_create_layer(obj_jugador_1.x - 24, obj_jugador_1.y,
                                              "Instancias", obj_jugador,
                                              { entrada : new BrawlerInput(1, 0,0,0,0, 0,0) });
    global.gestor_p2 = new GestorFichas(global.jugador_2, 3, 2,
                                         BRAWLER_RADIO_ACERCARSE, BRAWLER_RADIO_ATAQUE);
}
```

---

## 9 · Armas recogibles y objetos rompibles

```gml
/// obj_arma_recogible — Create
/// @desc Cambia la entrada activa de global.ataques del jugador que la recoge.
ataque_ligero = "bate_ligero";
ataque_fuerte = "bate_fuerte";

/// obj_arma_recogible — Collision con obj_jugador
other.arma_ligero_actual = ataque_ligero;
other.arma_fuerte_actual = ataque_fuerte;
other.arma_golpes_restantes = 8;   // las armas de un brawler casi siempre se rompen con el uso
instance_destroy();
```

```gml
/// obj_objeto_rompible — Create
hp_objeto     = 3;
drop_prob     = 0.4;      // probabilidad de soltar algo al romperse
drop_obj      = obj_pickup_vida;

/// obj_objeto_rompible — evento personalizado, llamado desde el mismo punto donde
/// 04 · 30 §5.6 resuelve un golpe (una caja NEUTRA — 04 · 30 §5.0 — también puede
/// golpear objetos, no solo entidades vivas)
hp_objeto -= 1;
if (hp_objeto <= 0)
{
    // El estallido en trozos ya está resuelto como VFX genérico: 04 · 39 §3.1
    // (pt_escombro, parte del Create de objFx). No se repite el sistema de partículas
    // aquí — se reutiliza tal cual, como variables de INSTANCIA de objFx (04 · 39 §3.2,
    // fx_explosion_completa()), no como globales.
    part_particles_create(objFx.ps, x, y, objFx.pt_escombro, 10);

    if (random(1) < drop_prob)
    {
        instance_create_layer(x, y, layer, drop_obj);
    }
    instance_destroy();
}
```

Un objeto rompible no necesita una hurtbox de `04 · 30` completa: basta con que su máscara de
colisión sea del tamaño del sprite y con que la caja de golpe (`obj_hitbox` de `04 · 30` §5.3)
lo detecte igual que detecta a una entidad — `instance_place_list` no distingue si el objeto de
destino tiene `combate` o no, así que un `obj_objeto_rompible` con su propio evento de daño
convive sin fricción con el pipeline existente.

---

## 10 · Jefes y escenarios que hacen daño

### 10.1 · El jefe

Un jefe de beat 'em up es un `obj_enemigo` con un `arquetipo` de `04 · 33` §1 y una barra de
vida por fases — que **ya está resuelta** en
[`04 · 32` §4.8](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md#48-barra-de-jefe-segmentada-por-fases)
y no se repite aquí. Lo único específico de un brawler es que la arena del jefe (§5) no libera
la cámara ni desactiva el muro invisible hasta que `combate.vida <= 0`, en vez de hasta que
`instance_number(obj_enemigo) == 0` — un jefe suele convivir con esbirros que él mismo invoca, y
esos esbirros no deben contar para la condición de victoria.

```gml
/// obj_arena_trigger — Step, variante "jefe" (encuentro.es_jefe == true)
if (resuelta && encuentro.es_jefe && !instance_exists(obj_jefe))
{
    // El jefe murió: da igual cuántos esbirros queden vivos todavía.
    cam_set_bounds(obj_camara_director.cam, -1, -1, -1, -1);
    instance_destroy();
}
```

### 10.2 · Escenarios que hacen daño

Pinchos, fuego, suelo electrificado: geometría del nivel que hace daño por contacto, sin ser
un ataque de ninguna entidad. Se resuelve con la misma función `recibir_golpe()` de `04 · 30`
§5.7, con la forma EXACTA que esa función espera — `{ caja, atacante, victima, direccion }`,
no un struct plano — empaquetando el daño como si viniera de una caja de equipo neutro:

```gml
/// obj_peligro_terreno — Create
dano_por_tick    = 3;
intervalo_frames = 30;
timer            = 0;

// La "caja" que exige recibir_golpe() no es una instancia de obj_hitbox real —
// aquí basta un struct con los mismos campos que 04 · 30 §5.4 pone en una hitbox.
caja_peligro = {
    dano : dano_por_tick, empuje : 0, elevacion : 0,
    hitstun : 4, blockstun : 0, rompe_aguante : false,
    prioridad : 0, equipo : EQUIPO_NEUTRO,
    rompe_bloqueo : false, rebote : 0
};

/// obj_peligro_terreno — Step
timer -= 1;
if (timer <= 0 && place_meeting(x, y, obj_entidad_beatemup))
{
    with (obj_entidad_beatemup)
    {
        if (place_meeting(x, y, other) && golpe_z_conecta(z, { z_min: 0, z_max: 6 }))
        {
            recibir_golpe({
                caja      : other.caja_peligro,
                atacante  : other,
                victima   : id,
                direccion : point_direction(other.x, other.y, x, y)
            });
        }
    }
    timer = intervalo_frames;
}
```

`z_max: 6` es lo que permite que **saltar por encima de un charco de fuego lo esquive** — el
mismo filtro de altura del §4.1, aplicado a un peligro estático en vez de a una hitbox de
ataque. Es la prueba de que el eje Z falso de `04 · 46` no es solo para saltos vistosos: es la
regla que decide, en todo el documento, quién puede tocar a quién.

---

## Checklist

- [ ] El carril de profundidad (`carril_y_min`/`carril_y_max`) se aplica con un `clamp()` cada
      Step, y puede variar por arena sin tocar el depth-sort de `04 · 02`.
- [ ] Los ataques que deban fallar contra alguien en el aire (o en el suelo) llevan `z_min`/
      `z_max` en su entrada de `global.ataques`, y `golpe_z_conecta()` se llama ANTES de
      `recibir_golpe()`, nunca después.
- [ ] `elevacion` en un brawler con carril se redirige a `zvel`, no a `vel_y` — si se te olvida,
      la víctima lanzada se sale del carril mientras está en el aire.
- [ ] La cámara se bloquea a la arena (`cam_set_bounds`) al entrar y se libera solo cuando la
      condición de victoria de esa arena se cumple (oleada muerta, o jefe muerto).
- [ ] El `GestorFichas` de cada jugador usa radios de melé (`BRAWLER_RADIO_*`), no los de una
      arena abierta — si los enemigos se quedan a distancia de disparo, revisa esto primero.
- [ ] Un agarre inmoviliza a la víctima (`hitstun` muy alto) y la desengancha de su propio
      movimiento — comprueba que `agarrado_por` se limpia también si el agarrador muere.
- [ ] El lanzamiento de un agarre usa la misma parábola de `04 · 46` §3.9: `zvel` inicial
      calculado con `sqrt(2 * GRAV_Z * altura)`, nunca un número mágico distinto.
- [ ] Los dos jugadores comparten `EQUIPO_JUGADOR`: si se golpean entre sí, revisa que no se
      haya creado un tercer equipo por error.
- [ ] Un objeto rompible se destruye limpiamente y suelta su drop **antes** de destruirse, no
      después (si no, `instance_create_layer` puede fallar por orden de eventos).

---

## Errores clásicos y cómo evitarlos

| Error | Síntoma | Arreglo |
|---|---|---|
| No acotar el carril de profundidad | Los personajes se dispersan por todo el escenario, la cámara no sabe a quién seguir, el fondo pintado se ve mal recortado | `clamp(y, carril_y_min, carril_y_max)` cada Step (§3.1) |
| Dejar `elevacion` moviendo `vel_y` en vez de `zvel` | Un enemigo lanzado "flota" fuera de su carril mientras dura el golpe, y aterriza en una fila de profundidad distinta a la que tenía | Redirigir a `zvel` en el punto exacto donde `04 · 30` §5.7 aplica el lanzamiento (§4.3) |
| Radios del `GestorFichas` copiados tal cual de un ejemplo de arena abierta | Los enemigos rodean al jugador a una distancia absurda para un brawler, o se agolpan todos encima | Usa radios de melé (20-50 px), no los 100+ de un encuentro de disparos (§7) |
| Ignorar el filtro de altura al portar ataques de `04 · 30` | Un barrido bajo golpea a quien acaba de saltar, el salto deja de ser una defensa válida | `golpe_z_conecta()` antes de `recibir_golpe()`, con `z_min`/`z_max` puestos a propósito (§4.1-§4.2) |
| Bloquear la cámara sin sellar también el paso físico | El jugador puede caminar fuera de la arena bloqueada aunque la cámara no le siga, y queda fuera de encuadre | Activa un `obj_muro_invisible` sólido junto con `cam_set_bounds`, no solo la cámara (§5.1) |
| Un objeto rompible sin límite de golpes que puedan alcanzarlo | Los jugadores lo destruyen desde fuera de rango porque comparte la máscara de colisión de una hitbox mucho más grande que el sprite | La máscara de colisión del objeto rompible debe ser la del sprite, no la heredada de un padre genérico |
| Condición de victoria de la arena mal puesta en una sala de jefe | La cámara se libera en cuanto mueren los esbirros, dejando al jefe fuera de cuadro | Para arenas de jefe, la condición es la vida del jefe, no `instance_number(obj_enemigo)` (§10.1) |
| Dos `GestorFichas` compartiendo el mismo objetivo en cooperativo | Los enemigos de los dos jugadores compiten por las mismas ranuras de rejilla y se bloquean entre sí sin motivo | Un gestor por jugador, y cada enemigo elige el suyo con `instance_nearest` antes de pedir ficha (§7) |

---

## Ver también

- [04 · 46 — Eje Z falso](./46%20-%20Eje%20Z%20falso%20-%20altura%2C%20sombras%20y%20profundidad%20en%20un%20juego%202D.md) —
  la base entera de saltos, sombras y lanzamientos que este documento reutiliza sin repetir.
- [04 · 30 — Combate cuerpo a cuerpo](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) —
  las cajas de golpe, `recibir_golpe()`, combos y frame data que este documento **no repite**:
  el §4 solo añade el filtro de altura por encima.
- [04 · 33 — Diseño de enemigos, encuentros y director de combate](./33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md) —
  `GestorFichas`, el hueco de escape y `EncuentroDef`, que este documento **no repite**: el §7
  solo lo instancia con radios de melé.
- [13 · 19 — Cámaras de juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/19%20-%20Cámaras%20de%20juego%20-%20encuadre%2C%20seguimiento%20y%20control.md) —
  zonas de cámara (§3.5) y cámara multijugador con zoom dinámico (§3.10), que este documento
  **no repite**: el §5 y el §8.3 solo los enganchan a la condición de oleada limpiada.
- [04 · 02 — Top-Down / Twin-Stick](./02%20-%20Top-Down%20_%20Twin-Stick.md) —
  el movimiento y el `depth = -bbox_bottom` sobre los que se construye el carril del §3.
- [04 · 32 — Sistema de daño y efectos de estado](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) §4.8 —
  la barra de jefe por fases que usa el §10.1 sin reimplementarla.
- [04 · 39 — VFX: diseño y catálogo de efectos](./39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md) §3.6 —
  los escombros con partículas (`pt_escombro`) que usa el §9 al romper un objeto.
- [04 · 15 — Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) — `apply_knockback()` y
  `hit_complete()`, usados en el §6 y el §10.2 sin repetir su implementación.
- [04 · 23 — IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) —
  `mp_potential_step`, usado en el §7 para el desplazamiento hacia la ranura concedida.
- [01 · 12 — Input: teclado, ratón y gamepad](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado%2C%20ratón%20y%20gamepad.md) —
  el catálogo completo de constantes `gp_*` y `vk_*` usado en `BrawlerInput` (§8.1).
- [10 · 01 — Academia de Hektor Profe](../10%20-%20Cursos%20en%20español/01%20-%20Academia%20de%20Hektor%20Profe.md) —
  curso 7 (Beat'em Up, 5 lecciones): la máquina de estados de animación y la planificación de
  enemigos por escenas, complementarias al código de este documento.

---

## Fuentes

- Michael Dawe, «Beyond the Kung-Fu Circle: The Belgian AI of Kingdoms of Amalur: Reckoning»,
  *Game AI Pro*, vol. 1, cap. 28 — ya citado y usado en `04 · 33` §3; este documento reutiliza
  esa misma cita sin repetirla.
- Manual oficial de GameMaker — `instance_place_list`, `gamepad_axis_value`,
  `gamepad_button_check_pressed`, `keyboard_check_pressed` — `09 - Manual oficial/manual-lts-2026-es/`
  (espejo local, consultado 2026-09-06).
- El propio código verificado de `04 · 30`, `04 · 33`, `04 · 46` y `13 · 19` de esta biblioteca,
  usados como base sin duplicar su contenido — es la fuente primaria más fiable de todas: ya
  compiló antes de escribirse este documento.
