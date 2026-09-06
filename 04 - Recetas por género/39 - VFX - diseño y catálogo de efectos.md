# 39 · VFX — diseño y catálogo de efectos

> El oficio del VFX en GameMaker: **por qué** una explosión se ve bien y no solo **qué función**
> la dibuja. Anatomía en capas, timing, rampas de color, trails/estelas, decals y destrucción —
> con las recetas completas de explosión, fuego, magia, lluvia, nieve y niebla, en las dos vías
> (editor de partículas y `part_type_*` por código). Cierra el hueco de API detectado en la
> auditoría: 13 funciones `part_type_*`/`part_system_*` que existían en el runtime pero no en
> ningún documento de prosa.
>
> **No cubre** (y no hay que confundirlo con esto): el recetario de **shaders** de efecto
> (aberración cromática, CRT, glitch, bloom completo, LUT) — lo que ya existe está en
> [08 · 06 — Shaders](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md); el
> **catálogo completo de los 42 FX de capa** (`fx_create`) — lo que ya existe está en
> [02 · 06 — Gráficos: SVG, SDF, FX y superficies §4](../02%20-%20Novedades%202026/06%20-%20Gráficos%20-%20SVG%2C%20SDF%2C%20FX%20y%20superficies.md);
> ni la **iluminación 2D avanzada** (normal maps, sombras proyectadas, god rays) — lo que ya
> existe está en [04 · 24 — Iluminación 2D](./24%20-%20Iluminación%202D.md). Los tres siguen
> siendo huecos reales de la biblioteca a día de hoy: no hay una promesa de documento futuro,
> solo el techo actual.

---

## 1 · Los principios

### 1.1 Las capas de un efecto: destello → núcleo → escombros → humo → onda

Un efecto de impacto que se ve «genérico» casi siempre tiene **una sola capa**: partículas
saliendo del punto de contacto, todas a la vez, del mismo color. Un efecto que se ve **caro**
tiene varias capas independientes, cada una con su propio material, su propia velocidad y su
propio momento de aparición:

| Capa | Qué es | Vida típica | Blend |
|---|---|---|---|
| **Destello** | 1-3 fotogramas de luz pura en el punto exacto del impacto | 2-4 frames | Aditivo |
| **Núcleo** | La masa de la explosión en sí — lo que da volumen | 8-16 frames | Aditivo |
| **Escombros** | Fragmentos sólidos con gravedad e inercia propia | 20-60 frames | Normal |
| **Humo** | Nace de donde murió el núcleo, no aparece a la vez que el destello | 40-90 frames | Normal, semitransparente |
| **Onda** | Un único anillo que se expande y se apaga — vende la fuerza del golpe | 8-16 frames | Aditivo, sutil |

Ninguna de estas capas es opcional individualmente indispensable — una chispa de impacto normal
solo necesita destello + un par de partículas — pero **una explosión sin las cinco se ve plana**,
por muchas partículas que le eches. Es la diferencia entre `fx_explosion()` (dos emisiones) de
[15 · Game feel y juice §5.5](./15%20-%20Game%20feel%20y%20juice.md#55-partículas-nativas) y
`fx_explosion_completa()` de este documento (§3.2): mismo motor de partículas, cinco capas.

### 1.2 Timing: todo simultáneo se ve plano

Si las cinco capas nacen en el mismo frame, el ojo las lee como una sola masa de ruido. La
separación temporal es gratis y es lo que más vende:

- El **destello** dura literalmente 2-3 frames — es luz, no masa, y la luz no persiste.
- El **núcleo** vive más que el destello, y **al morir** genera el humo (`part_type_death`,
  §3.0). El humo aparece **con retraso natural**, sin que tengas que calcular ningún timer:
  nace exactamente cuando el núcleo termina su vida.
- Los **escombros** salen ya en el primer frame (comparten el impulso inicial de la explosión)
  pero tardan más en desaparecer que cualquier otra capa — son lo último que se ve.
- La **onda** es la más corta de todas después del destello: si dura más de ~15 frames dejas de
  leerla como «expansión» y empiezas a leerla como «un círculo que hay ahí».

Esto es exactamente lo que dice la comunidad de VFX en tiempo real sobre las explosiones: el
efecto **secundario** importa más que el destello inicial. En el hilo *Best resources to learn
about explosion timing?* de realtimevfx.com, la respuesta mejor valorada insiste en que «un buen
efecto debe verse y sentirse durante muchos segundos después» del impacto — escombros que
rebotan, humo que persiste, no solo el flash del primer frame (consultado 2026-09-06,
<https://realtimevfx.com/t/best-resources-to-learn-about-explosion-timing/30835>).

### 1.3 La rampa de color: temperatura, no arcoíris

El color de una explosión o de fuego no es una elección estética libre: sigue la física del
calor. Raymond Schlitter (Slynyrd) lo resume así en su *Pixelblog* al diseñar explosiones de
shmup: «el aire caliente se expande rápido y se ralentiza al enfriarse; el color empieza en
blanco incandescente y se apaga hacia tonos cálidos, y luego a gris según se disipa en humo»
(traducido; consultado 2026-09-06,
<https://www.slynyrd.com/blog/2020/12/14/pixelblog-31-shmup-sprite-design>).

Esa frase es literalmente la rampa que necesitas: **blanco → amarillo → naranja → rojo → gris**.
`part_type_colour3()` te da tres paradas (ind, colour1, colour2, colour3) que se interpolan a
lo largo de la vida de la partícula — es la función exacta para esto, y es una de las que la
biblioteca tenía sin ningún ejemplo (§3.0). El gris del humo **no es una casualidad de diseño**:
es literalmente la misma masa de gas que ya no emite luz propia. Por eso `fx_explosion_completa()`
(§3.2) hace que el humo nazca del núcleo vía `part_type_death` en vez de crearlo por separado:
mismo origen, misma continuidad de color.

### 1.4 Silueta y lectura a distancia: aditivo frente a normal

- **Aditivo** (`part_type_blend(ind, true)`, equivalente a `bm_add`) suma luz: sirve para fuego,
  destellos, magia, chispas — cualquier cosa que **emita** luz. Sobre un fondo oscuro se ve
  espectacular; sobre un fondo ya muy claro, satura a blanco y pierde forma. Y en **HTML5 sin
  WebGL no hay blending aditivo** (ya documentado en
  [02 · 05 §8](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20partículas%20nuevo.md)):
  pruébalo en ese target antes de apostar todo el efecto a él.
- **Normal** es para todo lo que tiene masa y no brilla por sí mismo: humo, escombros, polvo,
  gotas de lluvia, sangre. Mezclar los dos dentro del mismo efecto (núcleo aditivo + humo normal
  + escombros normales) es exactamente lo que da la sensación de material real en vez de ruido
  de partículas.
- **Regla de lectura a distancia**: si un efecto solo se distingue por el color y no por la
  **forma** de la silueta, se pierde de lejos. `pt_shape_ring` para la onda, `pt_shape_square`
  para escombros y `pt_shape_star` para magia comunican qué es el efecto incluso a un tamaño de
  8 px, sin depender del color.

### 1.5 Menos partículas, mejor diseñadas

Es la lección más repetida y la más difícil de aplicar: 200 partículas idénticas casi nunca se
ven mejor que 30 partículas con timing, tamaño y color distintos por capa. Antes de subir el
`number` de una emisión, pregúntate si el problema es de **cantidad** o de **diseño** (falta una
capa, falta timing, falta rampa de color). La charla de referencia del oficio, *Juice it or lose
it* de Martin Jonasson y Petri Purho, hace esta misma observación sobre el «jugo» en general: lo
que vende el impacto no es la cantidad de efectos sino que se acumulen en **capas coordinadas**
sobre el mismo evento (GDC 2012; consultado 2026-09-06,
<https://www.youtube.com/watch?v=Fy0aCDmgnxg>). Este documento aplica esa misma idea
específicamente al VFX, igual que
[15 · Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) la aplica al *game feel* general.

---

## 2 · El método: diseñar antes de codear

### 2.1 Las preguntas, en orden

1. **¿Qué comunica este efecto?** Daño, curación, un secreto, peligro ambiental. El color y la
   forma deben responder a esto antes que a «que quede bonito».
2. **¿Cuánto dura?** Un efecto de un solo uso (impacto, explosión) tiene vida propia y se destruye
   solo. Un efecto continuo (fuego de una antorcha, lluvia) necesita un ciclo de vida gestionado
   (crear/destruir explícitos, §3.3 y §3.5).
3. **¿Aditivo o normal?** Ver §1.4. Decide esto antes de elegir colores: el mismo naranja se ve
   muy distinto en cada modo.
4. **¿Cuántas capas necesita?** Un chispazo de espada no necesita onda expansiva. Una explosión
   de jefe final probablemente sí. No apliques las cinco capas de §1.1 por sistema.
5. **¿Editor o código?** Ver §2.2.

### 2.2 Editor de partículas frente a `part_type_*` por código

[02 · 05 §7](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20partículas%20nuevo.md#7-cuándo-usar-cada-uno)
ya da la regla general («empieza por el editor siempre»). Aplicada a diseño de efectos:

| Situación | Vía |
|---|---|
| Quieres iterar visualmente rápido, ver el resultado en tiempo real | **Editor** (Particle System asset) + *Copy GML to Clipboard* si luego necesitas el código |
| El efecto depende de datos del juego (color del jugador, escala según nivel, el color de un hechizo elegido en runtime) | **Código**, porque necesitas cambiar `part_type_colour1()` u otros parámetros antes de cada emisión (ver `fx_carga_magica`, §3.4) |
| El efecto encadena partículas que generan otras partículas (núcleo → humo, fuego → ascuas) | **Código**: `part_type_death` / `part_type_step` no tienen equivalente visual directo en el editor de forma tan explícita |
| Es un efecto ambiental fijo del nivel (una hoguera ya colocada, niebla de una sala) | **Editor**, colocado en la capa de la room, controlado luego con `layer_particle_*` ([02 · 05 §7 bis](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20partículas%20nuevo.md#7-bis-partículas-colocadas-en-el-editor-de-rooms-layer_particle_)) |

Este documento se centra en la vía de **código**, que es la que tenía el hueco de API. No repite
la interfaz del editor: para eso está
[02 · 05 §2](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20partículas%20nuevo.md#2-el-particle-system-editor).

### 2.3 Presupuesto antes de diseñar, no después

Decide el límite de partículas simultáneas **antes** de escribir la primera emisión, no cuando
el juego ya va a tirones. Un enemigo normal no necesita el mismo presupuesto que un jefe final.
El detalle de medición y culling está en §3.12.

---

## 3 · Cómo se traduce a GameMaker

### 3.0 Cerrando el hueco de API

La auditoría detectó 13 de 34 funciones `part_type_*` y 7 de 19 `part_system_*` documentadas en
prosa. Esta tabla cierra las que hacían falta para las recetas de este documento; cada una se
usa de verdad en §3.1-§3.11, salvo `part_type_colour_mix` y `part_type_colour_rgb`, que llevan
su propio ejemplo suelto porque ninguna receta de más abajo necesitaba las tres variantes de
rampa de color a la vez.

| Función | Qué hace | Dónde se usa en este documento |
|---|---|---|
| `part_type_sprite(ind, sprite, animate, stretch, random)` | La partícula usa TU sprite en vez de una de las 14 formas incluidas | §3.6 (escombros con sprite propio) |
| `part_type_blend(ind, additive)` | `true` = aditivo (`bm_add`), `false` = normal. El interruptor entre «humo» y «fuego/magia» | §3.2, §3.3, §3.4 |
| `part_type_step(ind, step_number, step_type)` | Cada paso, con probabilidad `1/abs(step_number)` si es negativo, engendra `step_type` | §3.3 (el fuego engendra ascuas) |
| `part_type_death(ind, death_number, death_type)` | Al morir, engendra `death_number` partículas de `death_type` | §3.2 (el núcleo engendra humo), §3.5 (la gota engendra salpicadura) |
| `part_type_colour_mix(ind, colour1, colour2)` | Interpola entre dos colores a lo largo de la vida (versión de 2 paradas) | Ejemplo suelto abajo |
| `part_type_colour_hsv(ind, hmin, hmax, smin, smax, vmin, vmax)` | Color aleatorio por rango de matiz/saturación/valor (0-255 cada uno) | §3.4 (magia) |
| `part_type_colour_rgb(ind, rmin, rmax, gmin, gmax, bmin, bmax)` | Color aleatorio por rango de rojo/verde/azul (0-255 cada uno) | Ejemplo suelto abajo |
| `part_system_global_space(ind, enable)` | `true`: las partículas ya emitidas NO siguen al sistema al moverlo — la base de un rastro | §3.9.2 (estela de proyectil) |
| `part_system_automatic_update(ind, automatic)` / `part_system_update(ind)` | Desactiva el avance automático del sistema y lo avanzas tú, un paso a la vez | §3.8 (congelar durante una pausa real) |
| `part_particles_count(ind)` / `part_particles_clear(ind)` | Cuántas partículas vivas hay ahora mismo / vacía el sistema de golpe | §3.12 (presupuesto) |
| `part_type_subimage(ind, subimg)` | Fija una subimagen concreta del sprite de partícula (con `part_type_sprite`, `random` ya la varía solo) | Mencionada en §3.6 |

```gml
// Ejemplo suelto — part_type_colour_mix: interpola entre 2 colores en vez de 3
pt_ejemplo_mix = part_type_create();
part_type_colour_mix(pt_ejemplo_mix, c_yellow, c_red);   // de amarillo a rojo, sin parada intermedia
part_type_life(pt_ejemplo_mix, 20, 20);

// Ejemplo suelto — part_type_colour_rgb: color aleatorio por canal (0-255)
pt_ejemplo_rgb = part_type_create();
part_type_colour_rgb(pt_ejemplo_rgb, 200, 255, 80, 160, 0, 40);  // variaciones de naranja/marrón
```

> ⚠️ **`part_type_death` y `part_type_step` avisan en el propio manual**: nunca uses el mismo
> tipo de partícula como destino (bucle infinito que puede colgar el juego en segundos), y ten
> cuidado con el volumen de partículas que puedes disparar sin darte cuenta (fuente:
> `part_type_death.md` y `part_type_step.md`, manual LTS 2026, ver §Fuentes).

### 3.1 Ampliar `objFx`: los tipos de partícula que faltaban

Esto **amplía** la `Create` de `objFx` que ya existe en
[15 · §5.5](./15%20-%20Game%20feel%20y%20juice.md#55-partículas-nativas): añádelo a continuación
de `pt_dust`, sin tocar lo que ya hay.

```gml
// ---------------------------------------------------------------------------
// objFx — Create (AMPLIACIÓN: añade esto después de pt_dust)
// ---------------------------------------------------------------------------

// --- Tipo: destello aditivo (primer fotograma de cualquier explosión) ---
pt_flash = part_type_create();
part_type_shape(pt_flash, pt_shape_flare);
part_type_size(pt_flash, 1.2, 1.6, 0, 0);
part_type_life(pt_flash, 3, 4);
part_type_colour1(pt_flash, c_white);
part_type_alpha2(pt_flash, 1, 0);
part_type_blend(pt_flash, true);

// --- Tipo: núcleo de la explosión (al apagarse, engendra humo) ---
pt_nucleo = part_type_create();
part_type_shape(pt_nucleo, pt_shape_explosion);
part_type_size(pt_nucleo, 0.8, 1.4, 0.02, 0);
part_type_speed(pt_nucleo, 0.2, 0.6, -0.02, 0);
part_type_direction(pt_nucleo, 0, 359, 0, 0);
part_type_colour3(pt_nucleo, c_white, c_yellow, c_orange);
part_type_alpha3(pt_nucleo, 1, 1, 0);
part_type_blend(pt_nucleo, true);
part_type_life(pt_nucleo, 10, 14);
part_type_death(pt_nucleo, 3, pt_smoke);    // ← el humo NACE del núcleo, con retraso natural

// --- Tipo: escombros con gravedad e inercia propia ---
pt_escombro = part_type_create();
part_type_shape(pt_escombro, pt_shape_square);
part_type_size(pt_escombro, 0.12, 0.28, 0, 0);
part_type_speed(pt_escombro, 2, 7, -0.08, 0);
part_type_direction(pt_escombro, 0, 359, 0, 0);
part_type_gravity(pt_escombro, 0.22, 270);
part_type_orientation(pt_escombro, 0, 359, 8, 6, false);   // gira sobre sí mismo, no con el movimiento
part_type_colour1(pt_escombro, c_dkgray);
part_type_life(pt_escombro, 30, 55);

// --- Tipo: onda expansiva (un único anillo por explosión) ---
pt_onda = part_type_create();
part_type_shape(pt_onda, pt_shape_ring);
part_type_size(pt_onda, 0.3, 0.3, 0.45, 0);      // no varía por partícula: crece con size_incr
part_type_colour1(pt_onda, c_white);
part_type_alpha2(pt_onda, 0.5, 0);
part_type_blend(pt_onda, true);
part_type_life(pt_onda, 12, 12);

// --- Tipo: ascuas del fuego (las engendra pt_fuego, ver más abajo) ---
pt_ascua = part_type_create();
part_type_shape(pt_ascua, pt_shape_spark);
part_type_size(pt_ascua, 0.06, 0.12, 0, 0);
part_type_speed(pt_ascua, 0.3, 0.8, -0.01, 0.1);
part_type_direction(pt_ascua, 70, 110, 0, 6);     // hacia arriba, con temblor
part_type_colour1(pt_ascua, make_color_rgb(255, 160, 40));
part_type_alpha2(pt_ascua, 1, 0);
part_type_blend(pt_ascua, true);
part_type_life(pt_ascua, 10, 18);

// --- Tipo: fuego continuo ---
pt_fuego = part_type_create();
part_type_shape(pt_fuego, pt_shape_flare);
part_type_size(pt_fuego, 0.3, 0.5, 0.02, 0.02);
part_type_speed(pt_fuego, 0.4, 0.9, -0.02, 0.05);
part_type_direction(pt_fuego, 80, 100, 0, 4);
part_type_colour3(pt_fuego, c_white, c_yellow, c_red);    // la misma rampa de temperatura del §1.3
part_type_alpha3(pt_fuego, 1, 1, 0);
part_type_blend(pt_fuego, true);
part_type_life(pt_fuego, 18, 28);
part_type_step(pt_fuego, -6, pt_ascua);    // ~1 de cada 6 pasos engendra una ascua

// --- Tipo: magia / carga de ataque ---
pt_magia = part_type_create();
part_type_shape(pt_magia, pt_shape_star);
part_type_size(pt_magia, 0.15, 0.30, 0, 0);
part_type_speed(pt_magia, 1.5, 2.5, -0.15, 0);    // se frena al acercarse al centro de carga
part_type_life(pt_magia, 14, 20);
part_type_alpha3(pt_magia, 0, 1, 0);              // aparece, brilla, desaparece
part_type_blend(pt_magia, true);
part_type_colour1(pt_magia, c_aqua);              // fx_carga_magica() lo sobreescribe por color

// --- Tipos de clima (lluvia y nieve): ver §3.5 y §3.6, se crean bajo demanda ---
```

```gml
// ---------------------------------------------------------------------------
// objFx — Destroy (AMPLIACIÓN: añade esto junto a los part_type_destroy que ya hay)
// ---------------------------------------------------------------------------
part_type_destroy(pt_flash);
part_type_destroy(pt_nucleo);
part_type_destroy(pt_escombro);
part_type_destroy(pt_onda);
part_type_destroy(pt_ascua);
part_type_destroy(pt_fuego);
part_type_destroy(pt_magia);
```

### 3.2 Explosión completa en capas

```gml
// ---------------------------------------------------------------------------
// scr_fx_vfx — amplía scr_fx de la 15 · §5.5
// ---------------------------------------------------------------------------

/// @func fx_explosion_completa(_x, _y, _escala)
/// @desc Explosión en 5 capas: destello, núcleo (que engendra humo al morir),
///       escombros, chispas y onda expansiva. Sustituye a fx_explosion() de
///       la 15 · §5.5 cuando el impacto merece más que dos emisiones.
function fx_explosion_completa(_x, _y, _escala)
{
    // 1. Destello: el "golpe" del primer fotograma
    part_particles_create(objFx.ps, _x, _y, objFx.pt_flash, 1);

    // 2. Núcleo: el humo nacerá de aquí solo, con retardo natural (part_type_death)
    part_particles_create(objFx.ps, _x, _y, objFx.pt_nucleo, 1 + round(_escala));

    // 3. Escombros en abanico completo, con gravedad propia
    part_particles_create(objFx.ps, _x, _y, objFx.pt_escombro, 10 * _escala);

    // 4. Chispas (ya existentes en la 15 · §5.5), reforzadas
    part_particles_create(objFx.ps, _x, _y, objFx.pt_spark, 24 * _escala);

    // 5. Onda expansiva: una sola partícula que crece y se apaga
    part_particles_create(objFx.ps, _x, _y, objFx.pt_onda, 1);

    camera_shake(0.4 * _escala);
    hit_stop(4);
}
```

> 💡 El humo **no se crea aquí**: nace solo cuando `pt_nucleo` termina su vida
> (`part_type_death(pt_nucleo, 3, pt_smoke)` en §3.1). Es el mecanismo real detrás del
> «escalonado temporal» y la «rampa de color fuego→humo» del §1.2-§1.3: mismo origen, mismo
> punto, retraso automático — sin timers escritos a mano.

### 3.3 Fuego continuo

```gml
/// @func fx_fuego_crear(_x, _y)
/// @desc Fuego persistente (antorcha, hoguera). Devuelve un struct para
///       moverlo o destruirlo luego. El humo reutiliza pt_smoke de la 15 · §5.5.
function fx_fuego_crear(_x, _y)
{
    var _ps = part_system_create_layer("Effects", true);
    part_system_depth(_ps, -50);

    var _em_fuego = part_emitter_create(_ps);
    part_emitter_region(_ps, _em_fuego, _x - 3, _x + 3, _y - 2, _y + 2,
                        ps_shape_rectangle, ps_distr_gaussian);
    part_emitter_stream(_ps, _em_fuego, objFx.pt_fuego, 3);   // 3 partículas de llama por paso

    var _em_humo = part_emitter_create(_ps);
    part_emitter_region(_ps, _em_humo, _x - 2, _x + 2, _y - 4, _y - 2,
                        ps_shape_rectangle, ps_distr_linear);
    part_emitter_stream(_ps, _em_humo, objFx.pt_smoke, 1);

    return { ps: _ps, em_fuego: _em_fuego, em_humo: _em_humo };
}

/// @func fx_fuego_destruir(_fuego)
function fx_fuego_destruir(_fuego)
{
    part_emitter_destroy(_fuego.ps, _fuego.em_fuego);
    part_emitter_destroy(_fuego.ps, _fuego.em_humo);
    part_system_destroy(_fuego.ps);
}
```

```gml
// obj_antorcha — Create / Destroy
fuego = fx_fuego_crear(x, y - 12);
// ...
// obj_antorcha — Destroy
fx_fuego_destruir(fuego);
```

> ⚠️ **El aditivo de `pt_fuego`/`pt_ascua` no existe en HTML5 sin WebGL** (§1.4). Prueba el
> target antes de apostar la hoguera entera al blending aditivo.

### 3.4 Magia y carga de ataque

Las partículas nativas no orbitan un punto por sí solas: `part_type_direction` fija un rango
**igual para todas** las partículas del tipo, no calculado por posición. El truco real (y
verificado en código descargado: `Burrn/BurrnParticleEngine/objects/obj_missile/Step_0.gml`
recalcula `part_type_direction` antes de cada partícula individual) es mutar la dirección del
tipo **justo antes de crear cada partícula suelta**, calculándola con `point_direction()` hacia
el centro:

```gml
/// @func fx_carga_magica(_x, _y, _color, _radio)
/// @desc Partículas que convergen hacia (_x, _y): la "carga" antes de lanzar un hechizo.
///       Llama a esto cada Step mientras dure la carga.
function fx_carga_magica(_x, _y, _color, _radio)
{
    part_type_colour1(objFx.pt_magia, _color);

    repeat (3)
    {
        var _angulo = random(360);
        var _px = _x + lengthdir_x(_radio, _angulo);
        var _py = _y + lengthdir_y(_radio, _angulo);

        // la dirección de ESTA partícula concreta: hacia el centro de carga
        var _dir_centro = point_direction(_px, _py, _x, _y);
        part_type_direction(objFx.pt_magia, _dir_centro - 5, _dir_centro + 5, 0, 0);

        part_particles_create(objFx.ps, _px, _py, objFx.pt_magia, 1);
    }
}
```

```gml
// obj_jefe — Step, durante el estado "cargando_ataque"
fx_carga_magica(x, y, make_color_hsv(200, 200, 255), 48);   // púrpura-azulado, radio 48px
```

Para variar el tono aleatoriamente partícula a partícula en vez de un color fijo, sustituye la
línea de `part_type_colour1` por `part_type_colour_hsv(objFx.pt_magia, 190, 210, 180, 255, 200, 255)`
(rango azul-púrpura, §3.0) antes del `repeat`.

### 3.5 Lluvia con salpicadura

```gml
// ---------------------------------------------------------------------------
// obj_clima — un controlador de clima por room, no dentro de objFx
// ---------------------------------------------------------------------------

// Create
ps_clima = part_system_create_layer("Effects", true);
part_system_depth(ps_clima, -1000);

pt_lluvia = part_type_create();
part_type_shape(pt_lluvia, pt_shape_line);
part_type_size(pt_lluvia, 0.5, 0.9, 0, 0);
part_type_speed(pt_lluvia, 14, 18, 0, 0);
part_type_direction(pt_lluvia, 260, 260, 0, 2);      // casi vertical, con algo de viento
part_type_colour1(pt_lluvia, c_ltgray);
part_type_alpha1(pt_lluvia, 0.5);

pt_splash = part_type_create();
part_type_shape(pt_splash, pt_shape_spark);
part_type_size(pt_splash, 0.15, 0.25, -0.02, 0);
part_type_speed(pt_splash, 0.3, 0.8, 0, 0);
part_type_direction(pt_splash, 30, 150, 0, 0);       // en abanico hacia arriba
part_type_gravity(pt_splash, 0.1, 270);
part_type_colour1(pt_splash, c_ltgray);
part_type_alpha2(pt_splash, 0.6, 0);
part_type_life(pt_splash, 6, 10);

// ⚠️ Las partículas no colisionan (documentado en 02 · 05 §8). La "salpicadura al
// tocar el suelo" es una APROXIMACIÓN: ajustamos la vida de la gota para que expire
// justo cuando su trayectoria alcanzaría el suelo, y ahí muere → engendra el splash.
var _dist_al_suelo = (room_height) - camera_get_view_y(view_camera[0]);
var _vida_gota = round(_dist_al_suelo / 16);          // 16 ≈ velocidad vertical efectiva
part_type_life(pt_lluvia, _vida_gota, _vida_gota);
part_type_death(pt_lluvia, 2, pt_splash);

em_lluvia = part_emitter_create(ps_clima);
part_emitter_relative(ps_clima, em_lluvia, false);
lluvia_activa = false;

// Step — la región sigue siempre a la cámara
var _vx = camera_get_view_x(view_camera[0]);
var _vy = camera_get_view_y(view_camera[0]);
var _vw = camera_get_view_width(view_camera[0]);
part_emitter_region(ps_clima, em_lluvia, _vx, _vx + _vw, _vy - 16, _vy - 16,
                    ps_shape_line, ps_distr_linear);

// Destroy
part_type_destroy(pt_lluvia);
part_type_destroy(pt_splash);
part_emitter_destroy(ps_clima, em_lluvia);
part_system_destroy(ps_clima);
```

```gml
/// @func fx_lluvia_iniciar() / fx_lluvia_detener()
function fx_lluvia_iniciar()
{
    with (obj_clima)
    {
        part_emitter_stream(ps_clima, em_lluvia, pt_lluvia, 6);
        lluvia_activa = true;
    }
}

function fx_lluvia_detener()
{
    with (obj_clima)
    {
        part_emitter_stream(ps_clima, em_lluvia, pt_lluvia, 0);
        lluvia_activa = false;
    }
}
```

> ⚠️ **«Desactivar bajo techo» necesita tu propia información de nivel**: antes de emitir una
> gota en una columna X concreta, comprueba si hay un techo por encima con tu propio sistema de
> colisión o de tiles (por ejemplo `tilemap_get_at_pixel` sobre la capa de techos, o
> `instance_position` contra tus objetos de tejado). No hay una función nativa que lo resuelva
> por ti: esto depende enteramente de cómo está construido tu nivel.

### 3.6 Nieve

**Vía A — partículas nativas** (control total, coste de CPU):

```gml
pt_nieve = part_type_create();
part_type_shape(pt_nieve, pt_shape_snow);
part_type_size(pt_nieve, 0.3, 0.6, 0, 0.02);
part_type_speed(pt_nieve, 0.4, 1.0, 0, 0);
part_type_direction(pt_nieve, 250, 290, 0, 3);    // caída lenta con vaivén lateral
part_type_colour1(pt_nieve, c_white);
part_type_alpha1(pt_nieve, 0.8);
part_type_life(pt_nieve, 200, 260);
```

**Vía B — el FX nativo `_effect_windblown_particles`** (GPU, un leaf sprite por defecto, cero
`part_type_*`): identificador confirmado en el manual oficial en inglés — **no en el espejo
español**, que traduce 25 de los 28 identificadores que sí trae y le faltan 14 tipos enteros
(hallazgo de la auditoría de VFX; cita siempre `manual-lts-2026-en`, nunca `-es`, para nombres de
FX):

```gml
// Create
fx_nieve = fx_create("_effect_windblown_particles");
fx_set_parameter(fx_nieve, "param_num_particles", 300);
fx_set_parameter(fx_nieve, "param_wind_vector_x", -0.3);
fx_set_parameter(fx_nieve, "param_wind_vector_y", 1.2);
fx_set_parameter(fx_nieve, "param_grav_accel", 0.02);
layer_set_fx("Effects", fx_nieve);
```

Es el mismo patrón que ya usa
[02 · 06 §4.3](../02%20-%20Novedades%202026/06%20-%20Gráficos%20-%20SVG%2C%20SDF%2C%20FX%20y%20superficies.md#43-ejemplo-crear-y-modificar-un-fx-en-runtime)
para `_effect_glow`. La diferencia con la vía A: esto vive en una **capa de room**, no en el
sistema de partículas de `objFx`, y su sprite de partícula por defecto es una hoja (no un copo);
cámbialo con el parámetro `param_sprite` si necesitas específicamente nieve.

**Escombros con sprite propio** (cierra `part_type_sprite`/`part_type_subimage`, útil también
para nieve o ceniza estilizada con tu propio arte en vez de las 14 formas incluidas):

```gml
pt_escombro_spr = part_type_create();
part_type_sprite(pt_escombro_spr, spr_escombro_variantes, false, false, true);  // random = true
// part_type_subimage(pt_escombro_spr, 2);   // o fija una subimagen concreta en vez de al azar
part_type_gravity(pt_escombro_spr, 0.2, 270);
part_type_life(pt_escombro_spr, 30, 50);
```

### 3.7 Niebla ambiental 2D

```gml
// obj_niebla — Draw (capa aparte, por delante del suelo y detrás de los personajes)
var _t = current_time / 1000;

gpu_set_blendmode(bm_add);
draw_sprite_tiled_ext(spr_niebla, 0,
                      camera_get_view_x(view_camera[0]) + _t * 6, camera_get_view_y(view_camera[0]),
                      1, 1, c_white, 0.10);
draw_sprite_tiled_ext(spr_niebla, 0,
                      camera_get_view_x(view_camera[0]) - _t * 3, camera_get_view_y(view_camera[0]) + 20,
                      1.4, 1.4, c_white, 0.06);
gpu_set_blendmode(bm_normal);
```

> 💡 **`spr_niebla` necesita ser una textura de ruido/nube suave, con borde difuminado y alfa
> baja** — igual que el `spr_luz` radial que ya pide
> [24 · Iluminación 2D §1](./24%20-%20Iluminación%202D.md#1--el-sistema-de-luces-con-una-superficie).
> Dos capas a distinta velocidad (`_t * 6` frente a `_t * 3`, en direcciones opuestas) es lo que
> vende el parallax: una sola capa moviéndose se lee como "textura desplazándose", no como niebla.

### 3.8 Congelar partículas durante una pausa real

[15 · §5.0](./15%20-%20Game%20feel%20y%20juice.md#50-sistema-de-tiempo-hit-stop-y-time-scale) ya
avisa de que el *hit stop* de combate **debe dejar las partículas sueltas a propósito** — que
las chispas sigan volando mientras el mundo se congela es justo lo que vende el golpe. Eso sigue
siendo así: no uses lo de abajo para el `hit_stop()` de cada golpe.

Donde sí hace falta congelar de verdad las partículas es en una **pausa real** (menú, cinemática,
`global.game_freeze`):

```gml
// objTime — Step (después del Begin Step que ya gestiona hit_stop/time_scale)
if (global.game_freeze)
    part_system_automatic_update(objFx.ps, false);   // el motor deja de avanzarlas solo
else
    part_system_automatic_update(objFx.ps, true);    // vuelve al avance automático
```

Si además quieres que un `time_slow()` (tiempo bala, no pausa) ralentice también las partículas
de forma proporcional —no solo el gameplay—, la vía es la misma pero llamando tú a
`part_system_update(objFx.ps)` manualmente cada N frames según `global.time_scale`, en vez de
alternar todo o nada. Es más trabajo y rara vez merece la pena: en la mayoría de juegos, las
partículas siguiendo a velocidad normal durante el tiempo bala **refuerza** el contraste en vez
de restarle.

### 3.9 Trails y estelas

#### 3.9.1 Trail de espada con `draw_primitive`

```gml
/// @func Trail(_max_puntos, _color, _grosor)
/// @desc Historial de posiciones para dibujar una estela con draw_primitive.
///       Úsalo para armas, dashes o cualquier cosa que necesite una cola sólida
///       (no una nube de partículas).
function Trail(_max_puntos, _color, _grosor) constructor
{
    max_puntos = _max_puntos;
    color      = _color;
    grosor     = _grosor;
    puntos     = [];    // cada elemento: { x, y }

    static registrar = function(_x, _y)
    {
        array_push(puntos, { x: _x, y: _y });
        if (array_length(puntos) > max_puntos) array_delete(puntos, 0, 1);
    };

    static dibujar = function()
    {
        var _n = array_length(puntos);
        if (_n < 2) return;

        draw_primitive_begin(pr_trianglestrip);
        for (var _i = 0; _i < _n; _i++)
        {
            var _t      = _i / (_n - 1);     // 0 en la cola, 1 en la cabeza
            var _grueso = lerp(0, grosor, _t);
            var _p      = puntos[_i];

            var _dir = (_i < _n - 1)
                ? point_direction(_p.x, _p.y, puntos[_i + 1].x, puntos[_i + 1].y)
                : point_direction(puntos[_i - 1].x, puntos[_i - 1].y, _p.x, _p.y);
            var _perp = _dir + 90;

            draw_vertex_colour(_p.x + lengthdir_x(_grueso, _perp), _p.y + lengthdir_y(_grueso, _perp), color, _t);
            draw_vertex_colour(_p.x - lengthdir_x(_grueso, _perp), _p.y - lengthdir_y(_grueso, _perp), color, _t);
        }
        draw_primitive_end();
    };

    static limpiar = function() { puntos = []; };
}
```

```gml
// obj_espada — Create
trail = new Trail(10, c_white, 24);

// obj_espada — Step
if (atacando) trail.registrar(x, y); else trail.limpiar();

// obj_espada — Draw
trail.dibujar();
draw_self();
```

El ancho decrece hacia la cola (`lerp(0, grosor, _t)`) y el alfa de cada vértice usa el mismo
`_t` — cabeza opaca, cola transparente — sin necesitar una textura. Para una estela con
degradado de color en vez de un color plano, sustituye `draw_vertex_colour` por
`draw_primitive_begin_texture(pr_trianglestrip, sprite_get_texture(spr_estela, 0))` +
`draw_vertex_texture(x, y, u, v)`, con `u` avanzando de 0 a 1 a lo largo del historial y un
sprite de degradado horizontal como textura.

#### 3.9.2 Trail de proyectil con `part_system_global_space`

```gml
// obj_proyectil — Create
ps_estela = part_system_create_layer("Effects", true);
part_system_global_space(ps_estela, true);   // las partículas YA emitidas no siguen al sistema

pt_estela = part_type_create();
part_type_shape(pt_estela, pt_shape_disk);
part_type_size(pt_estela, 0.5, 0.7, -0.03, 0);
part_type_colour1(pt_estela, c_aqua);
part_type_blend(pt_estela, true);
part_type_alpha2(pt_estela, 0.6, 0);
part_type_life(pt_estela, 10, 16);

// obj_proyectil — Step
part_system_position(ps_estela, x, y);
part_particles_create(ps_estela, x, y, pt_estela, 2);

// obj_proyectil — Destroy
part_type_destroy(pt_estela);
part_system_destroy(ps_estela);
```

Sin `part_system_global_space(ps_estela, true)`, mover el sistema con `part_system_position()`
arrastraría también las partículas ya creadas — el efecto contrario a una cola.

#### 3.9.3 Motion blur por FX de capa

`_filter_linear_blur` (vector fijo, para movimiento en una dirección) y `_filter_zoom_blur`
(radial desde un punto, para un golpe con impulso hacia la cámara) están en el catálogo completo
de FX (`All_Filter_Effect_Types.md`, manual **en inglés** — el espejo español, de nuevo, no trae
estos dos identificadores entre sus 28 filas):

```gml
fx_blur = fx_create("_filter_linear_blur");
fx_set_parameter(fx_blur, "g_LinearBlurVector", [vel_x * 4, vel_y * 4]);
layer_set_fx("Effects", fx_blur);
```

#### 3.9.4 *Afterimage* (ya existe, no lo dupliques)

Los sprites fantasma de un dash ya están completos en
[06 · Metroidvania §5.4](./06%20-%20Metroidvania.md#54-habilidades-en-el-jugador)
(`objAfterimage`, con su Create y Step). Es la técnica correcta cuando el rastro debe conservar
la **forma completa del sprite** en vez de una cinta o una cola de partículas; las tres técnicas
de esta sección no compiten entre sí, se eligen según qué necesita leerse: silueta completa
(afterimage), un trazo continuo (trail de primitivas) o una estela de luz (partículas).

### 3.10 Decals y marcas persistentes

[01 · Fundamentos 11 §13](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) ya trae
`obj_sangre_decal`, que pinta sobre una surface del tamaño de la room y se autodestruye. Le
faltan cuatro cosas que la auditoría marcó como defectos reales, no como mejoras opcionales:

1. **Aviso de VRAM.** `surface_create(room_width, room_height)` con el formato por defecto
   (`rgba8unorm`, 4 bytes/píxel) en una room de 1920×1080 son **~8,3 MB**; en una room de
   3840×2160, **~33 MB**. Multiplícalo por cada room con decals activos a la vez si no las
   liberas al cambiar de sala.
2. **Estrategia de volatilidad.** Las surfaces se pierden al minimizar o cambiar de resolución
   ([08 · 05 — Superficies](../08%20-%20Referencia%20GML%20completa/05%20-%20Superficies.md)).
   Sin guardar qué se pintó, perder la surface borra todas las manchas de golpe.
3. **Límite y desvanecimiento por antigüedad.** Sin límite, la lista de decals crece sin fin.
4. **Agujeros de bala con rotación**, que el original no cubre.

```gml
// ---------------------------------------------------------------------------
// obj_gestor_decals — sustituye el "pintar y listo" del obj_sangre_decal original
// ---------------------------------------------------------------------------

// Create
surf_decals    = -1;
global.decals  = [];          // { spr, subimg, x, y, angulo, alfa_base, vida }
DECALS_MAXIMO  = 300;
DECAL_VIDA     = 1800;        // 30s a 60fps antes de empezar a desvanecerse
ultimo_segundo = current_time div 1000;

/// @func decal_pintar(_spr, _subimg, _x, _y, _angulo, _alfa)
/// @desc Pinta un decal y lo registra. Ángulo aleatorio para agujeros de bala:
///       decal_pintar(spr_agujero_bala, irandom(2), _x, _y, random(360), 1);
function decal_pintar(_spr, _subimg, _x, _y, _angulo, _alfa)
{
    with (obj_gestor_decals)
    {
        array_push(global.decals, {
            spr: _spr, subimg: _subimg, x: _x, y: _y,
            angulo: _angulo, alfa_base: _alfa, vida: DECAL_VIDA
        });
        if (array_length(global.decals) > DECALS_MAXIMO) array_delete(global.decals, 0, 1);

        if (!surface_exists(surf_decals)) decal_reconstruir();
        else
        {
            surface_set_target(surf_decals);
            draw_sprite_ext(_spr, _subimg, _x, _y, 1, 1, _angulo, c_white, _alfa);
            surface_reset_target();
        }
    }
}

/// @func decal_reconstruir()
/// @desc Recrea la surface y repinta TODOS los decals vivos. Necesario si la
///       surface se perdió, y también sirve para aplicar el desvanecimiento
///       (una surface no permite "borrar" un dibujo suelto: hay que repintar).
function decal_reconstruir()
{
    surf_decals = surface_create(room_width, room_height);
    surface_set_target(surf_decals);
    draw_clear_alpha(c_black, 0);

    for (var _i = array_length(global.decals) - 1; _i >= 0; _i--)
    {
        var _d = global.decals[_i];
        _d.vida--;
        if (_d.vida <= 0) { array_delete(global.decals, _i, 1); continue; }

        var _alfa = _d.alfa_base * clamp(_d.vida / 300, 0, 1);   // se apaga en los últimos 300 frames
        draw_sprite_ext(_d.spr, _d.subimg, _d.x, _d.y, 1, 1, _d.angulo, c_white, _alfa);
    }
    surface_reset_target();
}

// Step — reconstruye una vez por segundo para que el desvanecimiento avance
var _segundo_actual = current_time div 1000;
if (_segundo_actual != ultimo_segundo)
{
    ultimo_segundo = _segundo_actual;
    decal_reconstruir();
}

// Draw (en coordenadas de mundo, antes del HUD)
if (surface_exists(surf_decals)) draw_surface(surf_decals, 0, 0);
```

```gml
// Uso: sangre con rotación aleatoria
decal_pintar(spr_sangre, irandom(sprite_get_number(spr_sangre) - 1), x, y, random(360), 0.8);

// Uso: agujero de bala
decal_pintar(spr_agujero_bala, 0, _x, _y, random(360), 1);
```

> ⚠️ **Repintar cada segundo cuesta CPU** (recrea y rellena toda la surface). Si 300 decals con
> reconstrucción cada segundo no te llega, sube el intervalo o baja `DECALS_MAXIMO`: no hay
> forma nativa de "borrar" un solo dibujo de una surface sin repintar el resto.

### 3.11 Destrucción y escombros

Romper un sprite en trozos sin crear sprites nuevos (barato, sin coste de VRAM extra):
`draw_sprite_part_ext()` **no admite rotación** — solo `draw_sprite_general()` la admite, y esa
función **ignora el origen del sprite**: rota alrededor de la esquina superior izquierda de la
región, no de su centro (confirmado en el manual: "la parte se dibuja con su esquina superior
izquierda en la posición X/Y indicada", y esa posición es también el pivote de `rot`). Sin
corregirlo, cada trozo "orbita" un punto fantasma en vez de girar sobre sí mismo — es el error
más fácil de cometer aquí (ver también §5).

```gml
/// @func romper_en_escombros(_x, _y, _sprite, _subimg, _filas, _columnas, _fuerza)
/// @desc Rompe un sprite en una rejilla de trozos con velocidad e inercia propias.
function romper_en_escombros(_x, _y, _sprite, _subimg, _filas, _columnas, _fuerza)
{
    var _ancho_total = sprite_get_width(_sprite);
    var _alto_total   = sprite_get_height(_sprite);
    var _ancho_trozo  = _ancho_total / _columnas;
    var _alto_trozo   = _alto_total / _filas;

    for (var _fy = 0; _fy < _filas; _fy++)
    {
        for (var _fx = 0; _fx < _columnas; _fx++)
        {
            var _left = _fx * _ancho_trozo;
            var _top  = _fy * _alto_trozo;
            var _cx   = _left + _ancho_trozo * 0.5 - _ancho_total * 0.5;
            var _cy   = _top  + _alto_trozo * 0.5 - _alto_total * 0.5;

            var _inst = instance_create_layer(_x + _cx, _y + _cy, "Effects", obj_escombro);
            _inst.spr_origen    = _sprite;
            _inst.subimg_origen = _subimg;
            _inst.region_left   = _left;
            _inst.region_top    = _top;
            _inst.region_ancho  = _ancho_trozo;
            _inst.region_alto   = _alto_trozo;

            var _dir = point_direction(_x, _y, _inst.x, _inst.y) + random_range(-20, 20);
            _inst.vel_x = lengthdir_x(_fuerza, _dir) + random_range(-1, 1);
            _inst.vel_y = lengthdir_y(_fuerza, _dir) - random_range(1, 3);
            _inst.giro  = random_range(-8, 8);
        }
    }

    fx_dust_land(_x, _y);   // reutiliza el polvo de la 15 · §5.5
}
```

```gml
// obj_escombro — Create
spr_origen = -1; subimg_origen = 0;
region_left = 0; region_top = 0; region_ancho = 1; region_alto = 1;
vel_x = 0; vel_y = 0; giro = 0; grav = 0.35; vida = 90;

// obj_escombro — Step
vel_y += grav;
x += vel_x;
y += vel_y;
image_angle += giro;
vel_x *= 0.98;

vida--;
if (vida <= 0) instance_destroy();

// obj_escombro — Draw
// 🔺 draw_sprite_general() rota alrededor de la esquina superior izquierda de la
// región, NO de su centro. Calculamos a mano dónde debe caer esa esquina para que
// el CENTRO visual quede en (x, y) — si no, el trozo orbita en vez de girar.
var _mitad_ancho = region_ancho * 0.5;
var _mitad_alto  = region_alto  * 0.5;
var _dist_centro = point_distance(0, 0, _mitad_ancho, _mitad_alto);
var _ang_centro  = point_direction(0, 0, _mitad_ancho, _mitad_alto);
var _esquina_x   = x - lengthdir_x(_dist_centro, _ang_centro + image_angle);
var _esquina_y   = y - lengthdir_y(_dist_centro, _ang_centro + image_angle);

var _alfa = clamp(vida / 20, 0, 1);
draw_sprite_general(spr_origen, subimg_origen,
                    region_left, region_top, region_ancho, region_alto,
                    _esquina_x, _esquina_y, 1, 1, image_angle,
                    c_white, c_white, c_white, c_white, _alfa);
```

> 💡 **Alternativa con coste real de VRAM**: `sprite_create_from_surface()` crea un sprite
> independiente por trozo (útil si necesitas guardarlo, serializarlo o tratarlo como asset
> propio), pero cada llamada genera una textura nueva de verdad. Para escombros de un solo uso
> que se destruyen en menos de dos segundos, `draw_sprite_general()` sobre el sprite original —
> sin crear nada nuevo — es la vía barata y la que se recomienda por defecto.

### 3.12 Presupuesto medido y culling de emisores

```gml
// Depuración: cuántas partículas vivas hay ahora mismo en el sistema principal
show_debug_message($"partículas activas: {part_particles_count(objFx.ps)}");

// Límite duro: si te pasas del presupuesto, vacía en vez de acumular sin control
if (part_particles_count(objFx.ps) > 2000) part_particles_clear(objFx.ps);
```

```gml
// obj_hoguera — Step: apaga el emisor de humo si la hoguera está fuera de cámara
var _vx = camera_get_view_x(view_camera[0]);
var _vy = camera_get_view_y(view_camera[0]);
var _visible = rectangle_in_rectangle(
    x - 8, y - 8, x + 8, y + 8,
    _vx, _vy, _vx + camera_get_view_width(view_camera[0]), _vy + camera_get_view_height(view_camera[0])
) != 0;   // 0 = sin contacto; 1 = dentro; 2 = solapa

part_emitter_enable(fuego.ps, fuego.em_fuego, _visible);
part_emitter_enable(fuego.ps, fuego.em_humo, _visible);
```

Cifras de referencia (cualitativas, no un número mágico): la propia
[02 · 05 §8](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20partículas%20nuevo.md#8-limitaciones-y-avisos-importantes)
avisa de no tener 40 000 partículas a la vez y de que el *overdraw* en móvil es la causa
principal de tirones. `part_particles_count()` es la forma de comprobarlo en vivo en vez de
adivinarlo; `part_emitter_enable(false)` en emisores fuera de cámara es la forma más barata de
mantenerte por debajo del límite sin tocar el diseño del efecto.

---

## 4 · Checklist

Antes de dar un efecto por terminado:

- [ ] ¿Tiene más de una capa (§1.1), o es deliberadamente simple (chispa, impacto menor)?
- [ ] ¿Las capas nacen en momentos distintos, o todo aparece en el mismo frame (§1.2)?
- [ ] ¿El color sigue una rampa con sentido (temperatura, elemento), no colores sueltos (§1.3)?
- [ ] ¿Usaste aditivo solo donde algo emite luz de verdad (§1.4)? ¿Lo probaste en HTML5 si es tu
      target?
- [ ] ¿Liberas `part_type_destroy` / `part_system_destroy` / `part_emitter_destroy` de TODO lo
      que crees, incluidos los sistemas de un solo uso (`fx_fuego_crear`/`_destruir`)?
- [ ] ¿El efecto continuo (fuego, lluvia, niebla) tiene un ciclo de vida claro — quién lo crea,
      quién lo destruye, qué pasa al cambiar de room?
- [ ] Si es un trail: ¿elegiste la técnica correcta (afterimage/primitiva/partículas) según qué
      necesita leerse (§3.9.4)?
- [ ] Si pinta decals: ¿tiene límite, desvanecimiento y sobrevive a perder la surface (§3.10)?
- [ ] Si rompe un sprite en trozos: ¿rota sobre su propio centro, no orbita un punto fantasma
      (§3.11)?
- [ ] ¿Mediste `part_particles_count()` con el efecto más exigente del juego activo a la vez?
- [ ] ¿Los emisores continuos fuera de cámara están desactivados (`part_emitter_enable`)?

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Consecuencia | Arreglo |
|---|---|---|
| Todas las capas de una explosión en el mismo frame | Se lee como ruido, no como explosión | Escalona con `part_type_death`/`part_type_step` (§1.2, §3.2) |
| Aditivo en todo, "porque brilla más" | Sobre fondos claros o con mucho aditivo acumulado, todo satura a blanco y pierde forma | Aditivo solo en lo que emite luz; normal en lo que tiene masa (§1.4) |
| Confiar en que `part_type_death`/`step` usan el mismo tipo como destino | Bucle infinito, cuelgue del juego en segundos (avisado en el propio manual) | Usa siempre un tipo DISTINTO como destino |
| `part_system_position()` sin `part_system_global_space(true)` en una estela | La cola entera se mueve con el proyectil en vez de quedarse atrás | Actívalo antes de mover el sistema cada Step (§3.9.2) |
| No liberar `part_type_destroy`/`part_system_destroy` de un efecto de un solo uso | Fuga de memoria progresiva; con cientos de explosiones, degrada el juego | Cada `fx_*_crear()` debe tener su `fx_*_destruir()`, llamado siempre |
| Congelar TODAS las partículas en cada `hit_stop()` de combate | El golpe deja de sentirse — el "freeze mientras las chispas siguen volando" es la clave del impacto (15 · §5.0) | Congela partículas solo en pausa real (`game_freeze`), nunca en el hit stop normal (§3.8) |
| Rotar un trozo de escombro con `draw_sprite_general()` sin corregir el pivote | El trozo orbita un punto fantasma en vez de girar sobre sí mismo | Calcula la esquina compensando el offset al centro (§3.11) |
| Una surface de decals del tamaño de la room sin límite ni desvanecimiento | Crece sin fin y puede consumir decenas de MB de VRAM sin que se note hasta que ya es tarde | Límite de entradas + desvanecimiento por antigüedad + reconstrucción tras perder la surface (§3.10) |
| Citar el espejo español del manual para nombres de FX (`fx_create("...")`) | 25 de 28 identificadores están traducidos y no crean nada: `fx_create()` recibe una cadena literal | Cita siempre `manual-lts-2026-en` para los identificadores de FX (§3.6, §3.9.3) |
| Subir el número de partículas para "arreglar" un efecto que se ve pobre | Cuesta más CPU y casi nunca se ve mejor | El problema casi siempre es de diseño (falta capa, falta timing, falta rampa de color), no de cantidad (§1.5) |

---

## Ver también

- [15 · Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) — `objFx`, `hit_stop`,
  `fx_impact`/`fx_explosion` originales, y el dibujado del `hit_flash` (§5.6 bis)
- [24 · Iluminación 2D](./24%20-%20Iluminación%202D.md) — el sprite de luz radial que también
  necesita la niebla ambiental (§3.7), y el sistema de luces que un buen destello aditivo puede
  llegar a "quemar"
- [06 · Metroidvania §5.4](./06%20-%20Metroidvania.md#54-habilidades-en-el-jugador) —
  `objAfterimage`, la tercera vía de estela (silueta completa)
- [02 · 05 — Sistema de partículas nuevo](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20partículas%20nuevo.md) —
  el editor visual, `layer_particle_*` y cuándo usar cada vía
- [02 · 06 — Gráficos: SVG, SDF, FX y superficies](../02%20-%20Novedades%202026/06%20-%20Gráficos%20-%20SVG%2C%20SDF%2C%20FX%20y%20superficies.md) —
  el patrón `fx_create`/`fx_set_parameter`/`layer_set_fx` que reutilizan §3.6 y §3.9.3
- [08 · 04 — Color y blending](../08%20-%20Referencia%20GML%20completa/04%20-%20Color%20y%20blending.md) —
  los modos de mezcla en detalle, y el búfer de stencil para máscaras de efecto
- [08 · 05 — Superficies](../08%20-%20Referencia%20GML%20completa/05%20-%20Superficies.md) —
  volatilidad, formatos y coste de VRAM, la base técnica de §3.10
- [08 · 06 — Shaders](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md) — anatomía de
  un shader de GameMaker; el shader de `hit_flash` de 15 · §5.6 bis sigue exactamente este patrón
- [01 · Fundamentos 11 — Dibujo y renderizado §13](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) —
  el `obj_sangre_decal` original que amplía §3.10
- [04 · 27 — Accesibilidad](./27%20-%20Accesibilidad.md) — antes de encadenar destellos aditivos
  y ondas expansivas, revisa el límite de fotosensibilidad (<3 flashes/s)

---

## Fuentes

- Manual oficial — familia `part_type_*` (`part_type_sprite`, `part_type_blend`,
  `part_type_step`, `part_type_death`, `part_type_colour_mix`, `part_type_colour_hsv`,
  `part_type_colour_rgb`) —
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Drawing/Particles/Particle_Types/part_type_death.htm>
- Manual oficial — familia `part_system_*` (`part_system_global_space`,
  `part_system_automatic_update`, `part_system_update`, `part_particles_count`,
  `part_particles_clear`) —
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Drawing/Particles/Particle_Systems/part_particles_count.htm>
- Manual oficial — `draw_sprite_general` (rotación + región + color por esquina; nota de que
  ignora el origen del sprite) —
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Sprites_And_Tiles/draw_sprite_general.htm>
- Manual oficial — Primitivas (`draw_primitive_begin`, `draw_vertex_colour`, `pr_trianglestrip`) —
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Drawing/Primitives/draw_primitive_begin.htm>
- Manual oficial (rama **en inglés**, la correcta para los identificadores de FX) — *FX Types &
  Parameters*, catálogo completo de 36 filtros y 6 efectos —
  <https://manual.gamemaker.io/lts/en/The_Asset_Editors/Room_Properties/FX/All_Filter_Effect_Types.htm>
  (consultado 2026-09-06; el espejo español de esta página traduce 25 de sus 28 identificadores
  y le faltan 14 tipos — hallazgo de `_indice/auditorias/vfx.md`)
- Raymond Schlitter (Slynyrd), *Pixelblog 31 — Shmup Sprite Design*: la rampa de color de una
  explosión (blanco → cálido → gris) y el timing de expansión/desaceleración — consultado
  2026-09-06, <https://www.slynyrd.com/blog/2020/12/14/pixelblog-31-shmup-sprite-design>
- *Juice it or lose it*, charla de Martin Jonasson y Petri Purho (GDC 2012) — el principio de
  capas coordinadas sobre un mismo evento, aplicado aquí a VFX igual que
  [15 · Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) lo aplica al *game feel*
  general — consultado 2026-09-06, <https://www.youtube.com/watch?v=Fy0aCDmgnxg>
- Hilo *Best resources to learn about explosion timing?*, realtimevfx.com — los efectos
  secundarios (escombros, humo persistente) importan más que el destello inicial — consultado
  2026-09-06, <https://realtimevfx.com/t/best-resources-to-learn-about-explosion-timing/30835>
- Código real descargado (`11 - Código descargado/librerias/particulas/Burrn/BurrnParticleEngine`)
  — confirma en la práctica el truco de recalcular `part_type_direction()` antes de cada
  partícula individual, usado en `fx_carga_magica()` (§3.4)
