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
/// reproducir la animación "correr" en bucle, en el track 0
skeleton_animation_set("correr", 0);

/// cambiar a "saltar" SIN bucle
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
    skeleton_animation_set("idle", 0);      // al acabar "saltar", vuelve a "idle"
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
