# 22 · Animación esqueletal (Spine)

> GameMaker importa animaciones de **Spine** (esotericsoftware.com): personajes con huesos,
> no fotograma a fotograma. Un sprite Spine se anima por **animaciones con nombre** que mezclas,
> encadenas y controlas por código. Son 48 funciones `skeleton_*` que el manual documenta y casi
> ningún tutorial en español toca.
>
> **Hueco detectado** por el detector de cobertura por familias (`actualizar.py` paso 8).

---

## Cuándo usar Spine (y cuándo no)

| | Sprite normal (fotogramas) | Sprite de Spine (huesos) |
|---|---|---|
| Cómo se anima | Dibujas cada frame | Mueves huesos; el motor interpola |
| Peso en disco | Alto (muchas imágenes) | Bajo (un esqueleto + texturas) |
| Transiciones suaves | No (saltan) | Sí (mezcla entre animaciones) |
| Coste | Barato | Más CPU |
| Para qué | Pixel art, animación corta | Personajes grandes, jefes, cinemáticas fluidas |

Se importa un `.json` de Spine como sprite (ver [`sprite_add_ext`](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md)),
y se asigna a un objeto como cualquier sprite. La diferencia es que **lo controlas por código**.

---

## 1 · Reproducir y mezclar animaciones

Las animaciones van en **tracks** (pistas). El track 0 es la animación principal.

```gml
/// reproducir la animación "correr" en bucle: skeleton_animation_set() NO tiene parámetro
/// de track (siempre usa el 0); su segundo argumento es "loop" y por defecto ya es true
skeleton_animation_set("correr");

/// cambiar a "saltar" SIN bucle, en el track 0 — aquí sí hay track: es la versión _ext
skeleton_animation_set_ext("saltar", 0, false);
```

**La clave de Spine es la mezcla (mixing):** en vez de que «idle» salte a «correr», se funden.

```gml
/// Create — definir el tiempo de mezcla entre dos animaciones (en segundos)
skeleton_animation_mix("idle", "correr", 0.2);   // 0,2 s de transición suave
skeleton_animation_mix("correr", "idle", 0.15);
```

> 💡 **La mezcla es lo que hace que Spine se vea profesional.** Sin `skeleton_animation_mix`, los
> cambios de animación son cortes secos. Con 0,1-0,3 s de mezcla, el personaje fluye.

---

## 2 · Encadenar y saber cuándo termina

```gml
/// GameMaker/Spine NO tiene "cola" de animaciones: se encadena a mano
/// comprobando cuándo termina la actual (patrón habitual)
if (skeleton_animation_is_finished(0)) {
    skeleton_animation_set("idle");      // al acabar "saltar", vuelve a "idle" en bucle (loop = true por defecto)
}

/// eventos de Spine: disparar un sonido en el frame del "paso"
/// se reciben en el evento Animation Event del objeto, en la variable event_data
```

> 🔺 **Los eventos de Spine (`skeleton_animation_get_event_frames`) son cómo sincronizas sonido y
> lógica con la animación** — el paso que suena justo cuando el pie toca el suelo, el golpe que
> hace daño en el frame exacto del impacto. Se definen en Spine y se reciben en el evento
> **Animation Event**.

---

## 3 · Manipular huesos y slots por código

```gml
/// apuntar un hueso (la cabeza mira al ratón) — mezclar animación con control manual
var _mapa = ds_map_create();
skeleton_bone_state_get("cabeza", _mapa);
_mapa[? "angle"] = point_direction(x, y, mouse_x, mouse_y);
skeleton_bone_state_set("cabeza", _mapa);
ds_map_destroy(_mapa);

/// teñir un slot (el personaje parpadea en rojo al recibir daño)
skeleton_slot_color_set("cuerpo", c_red, 1);
```

> 💡 **Mover un hueso por código sobre una animación en marcha** es lo que permite que un
> personaje corra Y apunte con la cabeza/arma hacia donde tú quieras a la vez. Es la técnica de
> los shooters con personajes Spine.

---

## 3 bis · Attachments: cambiar armas, sombreros y objetos por código

Un *attachment* es lo que cuelga de un slot del esqueleto: el arma en la mano, el sombrero en la
cabeza. Puedes **cambiarlos en runtime** sin tocar la animación —el arma sigue el movimiento del
brazo aunque la cambies de espada a hacha.

```gml
/// ¿existe el accesorio actual antes de tocarlo?
if (skeleton_attachment_exists("arma")) {
    // reemplazar la espada por un hacha (un sprite del juego)
    skeleton_attachment_replace("arma", spr_hacha, 0, 0, 0, 1, 1, 0);
}

/// crear un accesorio nuevo en un slot que no tenía nada
skeleton_attachment_create("mano_izq", spr_escudo, 0, 0, 0, 1, 1, 0);

/// quitarlo
skeleton_attachment_destroy("mano_izq");
```

> 💡 **Los attachments son cómo montas un sistema de equipamiento sobre un personaje Spine:**
> el inventario cambia el sprite del arma con `skeleton_attachment_replace` y la animación de
> ataque sigue funcionando igual. Un solo esqueleto, infinitas armas.
>
> 🔺 **No existe `skeleton_attachment_queue` ni una función de "cola".** Verifica siempre con
> `python3 _indice/buscar.py --listar skeleton_attachment` los nombres exactos.

---

## 4 · Skins (cambiar el aspecto sin cambiar el esqueleto)

```gml
/// cambiar la "piel" del personaje (armadura, color de equipo) sin tocar la animación
skeleton_skin_set("armadura_dorada");
```

Para skins combinadas en runtime existe `skeleton_skin_create` (verifica su firma con
`python3 _indice/buscar.py skeleton_skin_create`).

---

## 5 · Rendimiento y LOD de esqueletos

Un esqueleto Spine cuesta más CPU que un sprite normal (tabla de §1) porque cada fotograma
recalcula la posición de cada hueso, aplica la mezcla activa si la hay y deforma la malla —
un sprite plano solo cambia qué imagen ya renderizada se dibuja. Cifras de referencia
(cualitativas, no un número mágico, en la misma línea que
[04 · 39 §3.12](../04%20-%20Recetas%20por%20género/39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md#312-presupuesto-medido-y-culling-de-emisores)):
un protagonista y un par de jefes Spine en pantalla no se notan; **decenas de esqueletos
completos animando y mezclando a la vez** (una horda entera hecha de instancias Spine) sí, y
es ahí donde hace falta LOD.

**⚠️ Límite real del motor**: no existe ninguna función `skeleton_*` de velocidad o pausa
(verificado contra la lista completa de las 48 funciones, arriba). No hay equivalente al
`image_speed` de un sprite normal para «bajar los fps de animación» de un esqueleto Spine sin
tocar nada más. Las dos técnicas de abajo trabajan con lo que el motor sí expone.

**Técnica 1 — fuera de cámara: desactivar la instancia entera.** Es la más barata y la más
segura, porque no es específica de Spine: reutiliza la desactivación por región ya verificada
en [01 · 15 §6](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#demasiadas-instancias-activas)
(`instance_deactivate_all` + `instance_activate_region`). Una instancia desactivada no
procesa su Step ni avanza su animación —esquelética o no—, así que un enemigo Spine fuera de
cámara cuesta exactamente lo mismo que uno inactivo de cualquier otro tipo. No hace falta
ningún código específico de esqueletos: si ya aplicas esa técnica al resto del juego, los
esqueletos ya están cubiertos.

**Técnica 2 — dentro de cámara pero de bajo detalle: evita la mezcla, no el esqueleto.** Para
enemigos visibles pero lejanos o pequeños en pantalla, donde desactivarlos del todo se
notaría, el ahorro real está en **no llamar a `skeleton_animation_mix`** para ellos: un corte
directo con `skeleton_animation_set()` (§1) evita el cálculo de mezcla entre dos animaciones
a la vez, quedándose solo con la reproducción de una. La diferencia de coste entre mezclar y
cortar no está cuantificada por una fuente oficial (⚠️ no verificado con una cifra), pero es
consistente con lo que ya dice §1 sobre qué hace la mezcla: calcula una interpolación extra
que un corte seco no necesita.

```gml
/// obj_enemigo_spine · Evento Step — nivel de detalle de animación por distancia a cámara
var _lejos = point_distance(x, y, camera_get_view_x(view_camera[0]) + camera_get_view_width(view_camera[0]) * 0.5,
                                    camera_get_view_y(view_camera[0]) + camera_get_view_height(view_camera[0]) * 0.5) > 400;

if (_lejos)
{
    if (sprite_index != anim_actual) skeleton_animation_set(anim_actual);   // corte seco, sin mezcla
}
else
{
    if (sprite_index != anim_actual) skeleton_animation_mix(anim_anterior, anim_actual, 0.15);   // mezcla completa
}
```

Mide siempre con el **Debug Overlay** (`show_debug_overlay`, [01 · 15 §4](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#4-nivel-3-el-debug-overlay))
cuántos esqueletos simultáneos con mezcla activa soporta tu presupuesto de fotogramas, en
vez de fijar un número a ciegas.

## 6 · DragonBones: por qué no es una alternativa hoy (verificado)

DragonBones es, como Spine, un editor de animación esqueletal 2D — pero **no tiene soporte
nativo en GameMaker**, ni una extensión oficial que lo añada. Verificado el 2026-09-07:

- **Cero funciones `dragonbones_*`** en el runtime: `python3 _indice/buscar.py --listar
  dragonbones` devuelve 0 resultados.
- El **listado oficial de motores soportados por DragonBones**
  (<https://dragonbones.github.io/en/animation.html>) no menciona GameMaker ni GameMaker
  Studio entre sus runtimes.
- En el repositorio oficial de DragonBones hay una petición abierta y sin respuesta desde
  hace **diez años**: el *issue* [`DragonBones/DragonBonesAS#76`](https://github.com/DragonBones/DragonBonesAS/issues/76)
  (abierto el 21 de junio de 2016) pide que DragonBones pueda **exportar en el formato JSON
  de Spine**, precisamente porque «GameMaker Studio ya soporta el formato JSON de Spine» y
  eso permitiría importar animaciones de DragonBones sin que el equipo tenga que construir un
  runtime propio. El issue sigue abierto, sin etiqueta, sin milestone y sin respuesta del
  equipo, a fecha de esta verificación.
- El único intento de la comunidad encontrado es
  [`adenhumbert/gms2d-skeletal-animation`](https://github.com/adenhumbert/gms2d-skeletal-animation)
  («A custom runtime for Gamemaker Studio 2 that allows bone animations from Spine,
  Dragonbones, and (eventually) Spriter»), verificado por la API de búsqueda de repositorios
  de GitHub: **su último commit es del 6 de mayo de 2019** — siete años sin actividad a fecha
  de esta verificación, escrito para GameMaker Studio 2 **antes** del cambio de handles de
  2026 ([01 · 03](../01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md)),
  por lo que no hay garantía de que compile sin reescritura contra el runtime `2026.0.0.23`.
  ⚠️ Búsquedas web devolvieron también los nombres «katsaii/gml-bone-animation» y
  «NuxiiGit/gms2d-skeletal-animation» como posibles variantes o *forks* del mismo proyecto,
  pero ambas URLs devolvieron **404** al abrirlas: no se han podido verificar como
  repositorios distintos y no se citan como fuente.

**Conclusión práctica**: si necesitas animación esqueletal en GameMaker LTS 2026, la vía real
es **Spine**, con soporte nativo y 48 funciones `skeleton_*` verificadas contra el runtime —
todo este documento. DragonBones no es hoy una alternativa viable sin escribir un runtime
propio desde cero.

---

## Las trampas

| Trampa | Consecuencia |
|---|---|
| No definir `skeleton_animation_mix` | Los cambios de animación saltan en seco |
| Olvidar `ds_map_destroy` tras leer un hueso | Fuga de memoria |
| Usar Spine para pixel art | Sobrecoste; usa sprites normales |
| Suponer que el sprite Spine se anima solo | Hay que llamar a `skeleton_animation_set` |
| No comprobar `skeleton_animation_is_finished` | La lógica no se encadena con la animación |

---

## Ver también

- La lista completa: `python3 _indice/buscar.py --listar skeleton_` (48 funciones)
- [03 · Texto y fuentes](./03%20-%20Texto%20y%20fuentes.md) · [01 · Dibujo básico y sprites](./01%20-%20Dibujo%20básico%20y%20sprites.md)
- Documentación de Spine: <https://esotericsoftware.com/>
