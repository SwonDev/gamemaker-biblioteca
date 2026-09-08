# 42 · Audio reactivo al mundo — materiales, zonas y estados de mezcla

> Cuatro recetas encadenadas que hacen que el sonido responda a **dónde está** el jugador y **qué
> está pasando**, no solo a qué botón pulsó: pasos que cambian con el suelo, salas que suenan
> distinto entre sí, transiciones de mezcla que no dan un salto audible, y un árbitro que decide
> qué suena de verdad cuando compiten veinte cosas a la vez. Las cuatro se construyen **encima**
> del gestor de audio de
> [13 · 09 §4.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#42-cómo-se-montan-de-verdad-los-buses-en-2026)
> (`global.bus`, `global.em`, `mezcla_aplicar()`), del banco con *round robin* de
> [13 · 09 §3.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#32-variaciones-y-round-robin)
> (`banco_crear()` / `banco_siguiente()`), del cupo de voces de
> [13 · 09 §3.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#33-prioridad-voces-y-el-límite-que-te-falta)
> (`sonar_limitado()`) y del anillo de emisores de
> [13 · 09 §5.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#52-un-anillo-de-emisores-y-dónde-va-el-oyente)
> (`sonar_en()`). **Ninguna de esas funciones se repite aquí**: se enlazan y se usan. Si no las
> tienes ya en tu proyecto, constrúyelas primero — este documento no tiene sentido sin ellas.
>
> **No cubre** mezcla básica de niveles y buses (→ 13 · 09 §4), el sonido posicional en sí mismo
> (→ 13 · 09 §5, aquí solo se usa), *sync groups*, *buffer sounds*, *play queues*, grabación ni
> Doppler (→
> [08 · 24 — Audio avanzado](../08%20-%20Referencia%20GML%20completa/24%20-%20Audio%20avanzado%20-%20buffers%2C%20colas%2C%20sincronía%20y%20grabación.md)),
> voz, subtítulos ni localización (→ 13 · 09 §8, [04 · 27](./27%20-%20Accesibilidad.md)), ni la
> música en capas (→ [04 · 26](./26%20-%20Música%20adaptativa%20por%20capas.md), que resuelve el
> *vertical layering* de la banda sonora — un problema hermano de los «estados de mezcla» de
> este documento, pero no el mismo: aquí se mezclan **buses y efectos**, allí se mezclan **pistas
> de música**).

---

## 1 · Los principios

### 1.1 El mundo no suena homogéneo: el material es información

Un solo `snd_paso` para tierra, piedra, madera y metal es la misma reproducción rígida que
[13 · 09 §3.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#32-variaciones-y-round-robin)
ya resuelve para las *variaciones* de un mismo sonido, aplicada un nivel más arriba: el sonido
correcto depende de un dato del mundo (qué hay bajo los pies) que el código de animación no
conoce y no debería conocer. Separar «qué evento ocurrió» (el broadcast del sprite,
[13 · 04 §3.6](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/04%20-%20Animación%20de%20sprites%2C%20Sequences%20y%20Animation%20Curves.md#36-broadcast-messages-del-sprite))
de «qué sonido corresponde» (una tabla de datos consultada en el momento del evento) es lo que
permite añadir un quinto material sin tocar la animación, el colisionador ni el broadcast.

### 1.2 ⚠️ La regla que gobierna todo este documento: un bus propio solo oye lo que pasa por un emisor

Es la advertencia central de
[13 · 09 §4.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#42-cómo-se-montan-de-verdad-los-buses-en-2026)
y de
[02 · 07 §5.1](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md#51-concepto-todo-pasa-por-un-bus),
y **toda la arquitectura de este documento existe por su culpa**:

> **Los buses personalizados solo se pueden usar con Audio Emitters.** El audio 2D
> (`audio_play_sound()`, `audio_play_sound_ext()` sin la clave `emitter`) y el audio 3D
> (`audio_play_sound_at()`) acaban siempre en el bus principal, tengan o no un bus propio con
> efectos esperándolos. — Manual, *Audio Effects*.

Consecuencia práctica que se repite en las cuatro recetas de abajo: **si quieres que una zona de
reverberación, un estado de mezcla o un sistema de prioridad afecten a un sonido, ese sonido tiene
que sonar desde un emisor** — el anillo de
[13 · 09 §5.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#52-un-anillo-de-emisores-y-dónde-va-el-oyente)
(`sonar_en()`) o un emisor de categoría (`global.em.*`). Un sonido lanzado con
`audio_play_sound()` a secas, o con `sonar_limitado()` tal cual está escrito en
[13 · 09 §3.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#33-prioridad-voces-y-el-límite-que-te-falta)
(que **no** pasa la clave `emitter`), va al bus principal y **ninguna** reverberación de zona ni
ningún estado de mezcla que toque un bus propio lo va a alcanzar, sin que salte ningún error. Esto
tiene consecuencias concretas en §3.1 (los pasos, tal y como los monta `sonar_limitado()`, quedan
**fuera** de la reverberación de zona a propósito) y en §3.2 (la reverberación se cuelga del bus
que sí alimenta el anillo). Si necesitas *buffers*, colas o Doppler para audio generado en
ejecución, esa parte de la API está en
[08 · 24](../08%20-%20Referencia%20GML%20completa/24%20-%20Audio%20avanzado%20-%20buffers%2C%20colas%2C%20sincronía%20y%20grabación.md);
aquí no se repite.

### 1.3 Un «estado de mezcla» es una fotografía completa, no un interruptor

[02 · 07 §5.8 y §5.9](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md#58-ejemplo-completo-bajo-el-agua)
muestran «bajo el agua» y «menú de pausa» como asignaciones instantáneas: un filtro se planta o
se quita en el mismo frame (`audio_bus_main.effects[0] = ef_menu;` / `= undefined;`). Sirve para
enseñar la API, pero en un juego real dos problemas aparecen enseguida: **el salto se oye** (nada
interpola) y **los estados no se declaran en un sitio, se dispersan** por todo el código que
decide cuándo entrar y salir del agua o de la pausa. §3.3 generaliza esos dos ejemplos a una
estructura de datos (`mezcla_estado_crear()`) más una función de transición
(`mezcla_transicionar()`) que interpola gain de buses y parámetros de efectos por igual, con la
misma lógica que ya usa el *ducking* de voz de
[13 · 09 §4.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#42-cómo-se-montan-de-verdad-los-buses-en-2026)
(`duck = lerp(duck, _objetivo, _velocidad);`), pero declarada una vez como dato y reutilizable
para cualquier combinación de bus + efecto.

### 1.4 «Oír siempre lo importante»: el sistema de Overwatch puntúa, no compara volúmenes

[13 · 09 §1.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#13-oír-siempre-lo-importante)
ya cuenta el porqué: Scott Lawlor y Tomas Neumann (Blizzard, GDC 2016) probaron *HDR audio* —el
sonido más fuerte se come a los demás— y lo descartaron por «blanco o negro». Lo sustituyeron por
un sistema donde **cada sonido puntúa** según el daño que hace, la distancia a la cámara y si el
origen es visible, y esa puntuación lo mete en un cubo: alto, normal, bajo o descartado. §3.4
implementa exactamente eso: no es una alternativa a `sonar_limitado()` (que limita **cuántas
copias del mismo sonido** suenan a la vez, §1.2 de
[13 · 09 §3.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#33-prioridad-voces-y-el-límite-que-te-falta)),
sino un árbitro que decide, **entre sonidos distintos** pedidos en el mismo frame, cuáles se
ganan un hueco. Son dos problemas distintos y hacen falta los dos.

---

## 2 · El método, paso a paso

### 2.1 Escribe la tabla material → banco antes de tocar el tileset

Antes de programar nada, decide en una tabla qué materiales existen y cuántas tomas tiene cada
uno (3-5 según [13 · 09 §1.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#2--categorías-y-presupuesto-de-sonido)):

| Material | Tomas | Notas |
|---|---:|---|
| Tierra | 4 | el material «por defecto» si el tile no está en ninguna tabla |
| Piedra | 4 | más brillante en agudos que tierra |
| Madera | 3 | hueca, con algo de resonancia |
| Metal | 4 | la más cara de diferenciar: necesita un timbre claramente distinto |

Después, y solo después, organiza el **tileset del suelo** en bloques contiguos de índices por
material (p. ej. columnas 0-15 tierra, 16-31 piedra…). El código de §3.1 no impone esa
organización: la tabla de rangos es justo lo que traduce «cómo organizaste el tileset» a «qué
banco suena», así que si ya tienes un tileset con otro orden, ajusta los rangos, no el tileset.

### 2.2 Decide las zonas de reverberación como anotaciones del nivel

Una zona de reverberación es un **dato de diseño de nivel**, no una decisión de programación: la
sala es una cueva, un salón enorme o un pasillo estrecho porque el diseñador la dibujó así, y esa
decisión ya se toma con el patrón `obj_zona` de
[13 · 02 §3.6](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/02%20-%20Diseño%20de%20niveles.md#36-triggers-y-zonas-objetos-invisibles).
§3.2 reutiliza exactamente ese patrón (objeto invisible, tamaño por escala en el Room Editor) y
le añade los tres números que definen cómo suena dentro: `size`, `damp` y `mix` de
`AudioEffectType.Reverb1` (rangos y significado en
[13 · 09 §4.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#43-compresor-limitador-y-eq-para-hacer-sitio)).
No coloques dos zonas solapadas si puedes evitarlo: §3.2 resuelve el solape con una prioridad
manual, pero es una salida de emergencia, no el caso normal.

### 2.3 Enumera los estados de mezcla que tu juego necesita de verdad

Una tabla corta, antes de escribir un solo `struct`:

| Estado | Buses que cambian | Efecto que anima | Duración típica |
|---|---|---|---|
| Normal | — (ganancias de referencia) | filtro de agua **abierto** | — (punto de partida) |
| Bajo el agua | música ↓, sfx ↓, ambiente ↑ | LPF2 del bus `sfx`: corte de 18 000 a 300 Hz | 0,5-0,8 s |
| Pausa | (ninguno; solo el efecto) | LPF2 del bus principal: corte de 20 000 a 1 200 Hz | 0,2-0,3 s |

Si tu juego necesita **combinaciones** (pausado *y* bajo el agua), decide ahora si mereces un
tercer estado explícito (`estado_pausa_bajo_agua`) o si aceptas que un estado sustituye al otro:
§3.3 explica por qué esto no se resuelve solo y por qué no conviene fingir que sí.

### 2.4 Decide el presupuesto de importancia antes de que el jugador dispare a nada

Un cupo por cubo (cuántos sonidos «altos», «normales» y «bajos» puede haber sonando en un mismo
frame) es una decisión de diseño de la escena, no un número universal: un jefe con quince
proyectiles necesita cupos distintos a un sigilo de pasillo con dos guardias. Fija un cupo de
partida (§3.4 propone 6 / 3 / 1) y ajústalo escuchando la escena más ruidosa del juego, no la más
tranquila.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 Pasos por material: leer el tile, mapear al banco, disparar desde el broadcast

Lo primero es resolver el `tilemap_element_id` de la capa de suelo **una vez**, no en cada paso.
`layer_tilemap_get_id()` acepta el nombre de la capa como *string*, pero el propio manual avisa
de que hacerlo «tendrá un impacto en el rendimiento» si se llama a menudo — y como
`layer_get_id()` sí admite guardarse en una variable, se resuelve una sola vez:

```gml
// ═══════════ obj_audio · Room Start (NO Create) ═══════════
// obj_audio es persistent (13 · 09 §4.2): su Create solo corre una vez, en la primera room.
// Si el tilemap se busca ahí, cada room nueva seguiría usando el tilemap de la room anterior
// — un `-1` silencioso o, peor, el id de un tilemap que ya no existe. Room Start se ejecuta
// en CADA room, exista o no la capa "Suelo".
global.tilemap_suelo = layer_tilemap_get_id("Suelo");     // -1 si la room no tiene esa capa
```

La tabla de materiales se declara como datos, junto a los bancos que ya sabes construir:

```gml
// ═══════════ scr_materiales — tabla de rangos y bancos por material ═══════════
// Rellena esto según cómo organizaste el tileset del suelo (§2.1). Los índices son los que
// devuelve tile_get_index(): si tu tileset no modifica los tiles (sin voltear/rotar), el índice
// coincide con la posición del tile dentro de la imagen del tile set.
global.material_por_rango =
[
    { desde : 0,  hasta : 15, material : "tierra" },
    { desde : 16, hasta : 31, material : "piedra" },
    { desde : 32, hasta : 47, material : "madera"  },
    { desde : 48, hasta : 63, material : "metal"   },
];

// Un banco de pasos por material, con el mismo banco_crear() de 13 · 09 §3.2 — no se repite.
global.pasos_por_material =
{
    tierra : banco_crear([snd_paso_tierra_1, snd_paso_tierra_2, snd_paso_tierra_3, snd_paso_tierra_4]),
    piedra : banco_crear([snd_paso_piedra_1, snd_paso_piedra_2, snd_paso_piedra_3, snd_paso_piedra_4]),
    madera : banco_crear([snd_paso_madera_1, snd_paso_madera_2, snd_paso_madera_3]),
    metal  : banco_crear([snd_paso_metal_1,  snd_paso_metal_2,  snd_paso_metal_3,  snd_paso_metal_4]),
};

/// scr_materiales · material_bajo(_px, _py)
/// @desc  Material del tile de la capa "Suelo" bajo el punto dado, o `undefined` si no hay
///        tile (un hueco, un puente sin suelo dibujado: ahí no debe sonar nada).
/// @param {Real} _px
/// @param {Real} _py
/// @return {String|Undefined}
function material_bajo(_px, _py)
{
    if (global.tilemap_suelo == -1) { return undefined; }        // room sin capa "Suelo"

    var _dato = tilemap_get_at_pixel(global.tilemap_suelo, _px, _py);
    if (_dato == -1) { return undefined; }                        // punto fuera de la room
    if (tile_get_empty(_dato)) { return undefined; }               // celda vacía: sin sonido

    var _indice = tile_get_index(_dato);
    for (var _i = 0; _i < array_length(global.material_por_rango); _i += 1)
    {
        var _r = global.material_por_rango[_i];
        if (_indice >= _r.desde && _indice <= _r.hasta) { return _r.material; }
    }
    return "tierra";      // índice fuera de toda tabla: mejor un sonido de más que silencio
}
```

Y el disparo va exactamente donde
[13 · 04 §3.6](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/04%20-%20Animación%20de%20sprites%2C%20Sequences%20y%20Animation%20Curves.md#36-broadcast-messages-del-sprite)
ya lo coloca: el evento *Other → Broadcast Message* del jugador, que hoy reproduce un único
`snd_paso` fijo. Sustituye esa línea por:

```gml
/// obj_jugador · Evento Other → Broadcast Message  (reemplaza el snd_paso fijo de 13 · 04 §3.6)
if (event_data[? "event_type"] != "sprite event") { exit; }

switch (event_data[? "message"])
{
    case "paso_izq":
    case "paso_der":
    {
        var _mat = material_bajo(x, bbox_bottom);
        if (!is_undefined(_mat) && struct_exists(global.pasos_por_material, _mat))
        {
            var _banco = struct_get(global.pasos_por_material, _mat);
            // sonar_limitado() ya trae el cupo de voces, la variación de tono y de ganancia
            // (13 · 09 §3.3): aquí solo se le da el banco correcto según el suelo.
            sonar_limitado(banco_siguiente(_banco), 3, db_to_lin(-20), 8);
        }
        break;
    }
    case "golpe_activo": golpe_habilitado = true;  break;
    case "golpe_fin":    golpe_habilitado = false; break;
}
```

> ⚠️ **`sonar_limitado()` no pasa `emitter` por defecto**: por la regla de §1.2, estos pasos suenan
> por el **bus principal**, no por `global.bus.sfx`. Es una elección razonable —los pasos del
> propio jugador casi nunca necesitan reverberación de zona, y añadir un cálculo de emisor a un
> sonido que se dispara varias veces por segundo tiene un coste que no compensa—, pero es una
> elección, no un accidente:
> [`13 · 09` §3.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#33-prioridad-voces-y-el-límite-que-te-falta)
> la deja explícita con un quinto parámetro opcional, `_emisor`. Si quieres que los pasos SÍ lleven
> la reverberación de §3.2 (por ejemplo, unos pasos muy resonantes en una catedral), la forma más
> simple es pasarlo: `sonar_limitado(banco_siguiente(_banco), 3, db_to_lin(-20), 8, global.em.sfx)`
> — mantiene el cupo de voces Y pasa por el bus. La alternativa de sustituir la llamada entera por
> `sonar_en(banco_siguiente(_banco), x, bbox_bottom, db_to_lin(-20), 8)` sigue siendo válida, pero
> ya no es necesaria solo para esto: úsala cuando de verdad quieras el anillo posicional (§5.2) y
> no el cupo de voces (§5 de este documento explica cómo combinarlos si de verdad los necesitas
> juntos).

### 3.2 Zonas de reverberación: `Reverb1` por ambiente con transición interpolada

La reverberación se cuelga del **bus que sí alimenta el anillo de emisores** —
`global.bus.sfx`, inicializado en
[13 · 09 §4.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#42-cómo-se-montan-de-verdad-los-buses-en-2026)
con `emisores_iniciar(24, global.bus.sfx)`— precisamente por la regla de §1.2: es el único bus
propio por el que pasa de verdad algo, porque el anillo entero está enchufado a él.

```gml
// ═══════════ obj_audio · Create (añadido a lo que ya monta 13 · 09 §4.2) ═══════════
// Un solo Reverb1 en el bus del anillo. Se crea ABIERTO (mix 0): sin zona activa no se oye.
global.ef_reverb_mundo = audio_effect_create(AudioEffectType.Reverb1);
global.ef_reverb_mundo.size = 0;
global.ef_reverb_mundo.damp = 0.5;
global.ef_reverb_mundo.mix  = 0;
global.bus.sfx.effects[0] = global.ef_reverb_mundo;

global.reverb_actual   = { size : 0, damp : 0.5, mix : 0 };   // lo que se oye ahora mismo
global.reverb_exterior = { size : 0, damp : 0.5, mix : 0 };   // fuera de cualquier obj_zona_audio
```

`obj_zona_audio` reutiliza el patrón `obj_zona` de
[13 · 02 §3.6](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/02%20-%20Diseño%20de%20niveles.md#36-triggers-y-zonas-objetos-invisibles)
(objeto invisible, tamaño por escala en el Room Editor), con los parámetros de reverberación
como variables de instancia:

```gml
/// obj_zona_audio · Create
// Variable Definitions, por instancia en el Room Editor:
//   reverb_size (Real 0-1) · reverb_damp (Real 0-1) · reverb_mix (Real 0-1)
//   prioridad (Real, más alto gana si dos zonas se solapan) · bed (Asset.GMSound o -1)
reverb_size = 0.6;  reverb_damp = 0.4;  reverb_mix = 0.35;
prioridad   = 0;    bed = -1;
visible = false;
```

Y el gestor central hace el trabajo de encontrar la zona activa y **animar hacia ella**, no de
saltar a sus valores:

```gml
// ═══════════ obj_audio · Step (añadido al de 13 · 09 §5.2, que ya calcula _lx/_ly) ═══════════
// oyente_x/oyente_y: mismo centro de cámara que usa audio_listener_position() en §5.2.
// Se guardan en variables porque el sistema de importancia (§3.4) también las necesita.
var _cam = camera_get_active();
oyente_x = (_cam == -1) ? x : camera_get_view_x(_cam) + camera_get_view_width(_cam)  * 0.5;
oyente_y = (_cam == -1) ? y : camera_get_view_y(_cam) + camera_get_view_height(_cam) * 0.5;

// ¿Qué obj_zona_audio contiene al oyente? Si hay varias solapadas, gana la de mayor prioridad
// — collision_point() con varias instancias superpuestas no garantiza CUÁL de ellas devuelve.
var _zona = noone;  var _mejor_prioridad = -infinity;
with (obj_zona_audio)
{
    if (position_meeting(other.oyente_x, other.oyente_y, id) && prioridad > _mejor_prioridad)
    {
        _mejor_prioridad = prioridad;
        _zona = id;
    }
}

var _objetivo = (_zona != noone)
    ? { size : _zona.reverb_size, damp : _zona.reverb_damp, mix : _zona.reverb_mix }
    : global.reverb_exterior;

// El mismo lerp con factor fijo que ya usa el ducking de voz (13 · 09 §4.2): depende de los
// fps si el juego no los fija — corrige con delta_time si es tu caso.
global.reverb_actual.size = lerp(global.reverb_actual.size, _objetivo.size, 0.05);
global.reverb_actual.damp = lerp(global.reverb_actual.damp, _objetivo.damp, 0.05);
global.reverb_actual.mix  = lerp(global.reverb_actual.mix,  _objetivo.mix,  0.05);

global.ef_reverb_mundo.size = global.reverb_actual.size;
global.ef_reverb_mundo.damp = global.reverb_actual.damp;
global.ef_reverb_mundo.mix  = global.reverb_actual.mix;

// Opcional: si la zona trae un bed propio, cruza también el ambiente — ambiente_poner() ya
// hace el fundido cruzado (13 · 09 §6), no se repite aquí.
if (_zona != noone && _zona.bed != -1) { ambiente_poner(_zona.bed); }
```

> 🔺 **Esto solo mueve lo que suena por el anillo de emisores** (`sonar_en()`). Un impacto
> lanzado con `audio_play_sound_at()` o un sonido de UI con `audio_play_sound()` no lo atraviesa
> nunca, por la regla de §1.2 — y no hay ningún error ni aviso que lo diga: simplemente no suena
> distinto entre la cueva y el campo abierto.
>
> 💡 **No solapes zonas si puedes evitarlo.** La prioridad manual es una salida de emergencia
> para transiciones cortas (el umbral de una puerta), no una forma cómoda de diseñar mazmorras
> enteras: con zonas bien separadas, ni siquiera hace falta el bucle `with`.

### 3.3 Estados de mezcla como *structs* interpolables

Esto generaliza —y sustituye, si los adoptas— los dos ejemplos de asignación instantánea de
[02 · 07 §5.8 y §5.9](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md#58-ejemplo-completo-bajo-el-agua).
Un estado es una fotografía: cuánto debe valer el `gain` de cada bus y qué parámetro de qué
efecto debe valer qué cosa. La función de transición **lee los valores actuales** como punto de
partida —así una transición se puede interrumpir a medio camino sin salto audible—, y los anima
hacia el objetivo:

```gml
// ═══════════ scr_mezcla_estados ═══════════

/// scr_mezcla_estados · mezcla_estado_crear(_ganancias, _efectos)
/// @param {Struct} _ganancias  { musica: 0.4, sfx: 1, ... } — claves de global.bus que se tocan;
///                             las que faltan se quedan como estén.
/// @param {Array}  _efectos    [{ bus: <Struct.AudioBus>, slot: 0, parametro: "cutoff", valor: 1200 }, ...]
/// @return {Struct}
function mezcla_estado_crear(_ganancias = {}, _efectos = [])
{
    return { ganancias : _ganancias, efectos : _efectos };
}

global.mezcla_origen   = undefined;
global.mezcla_objetivo = undefined;
global.mezcla_t        = 1;      // 1 = sin transición en curso
global.mezcla_duracion = 1;

/// scr_mezcla_estados · mezcla_transicionar(_estado, _segundos)
/// @desc  Empieza (o redirige) la transición hacia `_estado`. El punto de partida se LEE de
///        los buses en este instante, no se asume: por eso se puede llamar dos veces seguidas
///        sin que la segunda produzca un salto.
function mezcla_transicionar(_estado, _segundos = 1)
{
    var _origen_ganancias = {};
    var _claves = struct_get_names(_estado.ganancias);
    for (var _i = 0; _i < array_length(_claves); _i += 1)
    {
        var _bus = struct_get(global.bus, _claves[_i]);
        struct_set(_origen_ganancias, _claves[_i], _bus.gain);
    }

    var _origen_efectos = [];
    for (var _i = 0; _i < array_length(_estado.efectos); _i += 1)
    {
        var _e = _estado.efectos[_i];
        array_push(_origen_efectos, struct_get(_e.bus.effects[_e.slot], _e.parametro));
    }

    global.mezcla_origen   = { ganancias : _origen_ganancias, efectos : _origen_efectos };
    global.mezcla_objetivo = _estado;
    global.mezcla_t        = 0;
    global.mezcla_duracion = max(_segundos, 1 / 60);      // evita dividir por 0 con 0 s
}

/// scr_mezcla_estados · mezcla_estados_paso()  — llamar cada Step desde obj_audio
function mezcla_estados_paso()
{
    if (global.mezcla_t >= 1) { return; }
    global.mezcla_t = min(1, global.mezcla_t + (delta_time / 1000000) / global.mezcla_duracion);

    var _claves = struct_get_names(global.mezcla_objetivo.ganancias);
    for (var _i = 0; _i < array_length(_claves); _i += 1)
    {
        var _bus    = struct_get(global.bus, _claves[_i]);
        var _desde  = struct_get(global.mezcla_origen.ganancias,   _claves[_i]);
        var _hasta  = struct_get(global.mezcla_objetivo.ganancias, _claves[_i]);
        _bus.gain   = lerp(_desde, _hasta, global.mezcla_t);
    }

    for (var _i = 0; _i < array_length(global.mezcla_objetivo.efectos); _i += 1)
    {
        var _e     = global.mezcla_objetivo.efectos[_i];
        var _desde = global.mezcla_origen.efectos[_i];
        struct_set(_e.bus.effects[_e.slot], _e.parametro, lerp(_desde, _e.valor, global.mezcla_t));
    }
}
```

Y los tres estados de la tabla de §2.3, declarados una vez como datos:

```gml
// ═══════════ obj_audio · Create (declaración de estados; usa las ganancias de mezcla_aplicar) ═══════════

// El filtro de agua vive en el MISMO bus.sfx que la reverberación de zona (§3.2), en otro slot:
// los dos efectos son independientes y pueden estar activos a la vez sin pisarse.
global.ef_agua = audio_effect_create(AudioEffectType.LPF2);
global.ef_agua.cutoff = 18000;   // abierto de partida — mismo valor "neutro" que usa 13 · 09 §5.3
global.ef_agua.q      = 1;
global.bus.sfx.effects[1] = global.ef_agua;

// El filtro de pausa vive en el bus PRINCIPAL, como en 02 · 07 §5.9 — pero ahora es un valor
// que se anima, no un slot que aparece y desaparece.
global.ef_pausa = audio_effect_create(AudioEffectType.LPF2);
global.ef_pausa.cutoff = 20000;
global.ef_pausa.q      = 1;
audio_bus_main.effects[0] = global.ef_pausa;   // el slot 7 ya lo usa el compresor-techo de 13 · 09 §4.3

global.estado_normal = mezcla_estado_crear(
    { musica : 1, sfx : 1, ambiente : 1 },
    [{ bus : global.bus.sfx,  slot : 1, parametro : "cutoff", valor : 18000 },
     { bus : audio_bus_main,  slot : 0, parametro : "cutoff", valor : 20000 }]
);

global.estado_bajo_agua = mezcla_estado_crear(
    { musica : 0.5, sfx : 0.6, ambiente : 1.3 },
    [{ bus : global.bus.sfx, slot : 1, parametro : "cutoff", valor : 300 }]
);

global.estado_pausa = mezcla_estado_crear(
    {},   // sin cambio de ganancia: la pausa solo amortigua el timbre, no el volumen
    [{ bus : audio_bus_main, slot : 0, parametro : "cutoff", valor : 1200 }]
);

mezcla_transicionar(global.estado_normal, 0);   // fija el punto de partida sin fundido

// ── Uso, en cualquier otro objeto ──
// Al entrar al agua:  mezcla_transicionar(global.estado_bajo_agua, 0.6);
// Al salir del agua:  mezcla_transicionar(global.estado_normal,    0.6);
// Al pausar:          mezcla_transicionar(global.estado_pausa,     0.25);
// Al despausar:       mezcla_transicionar(global.estado_normal,    0.25);
```

> ⚠️ **Solo hay una transición activa a la vez.** Si el jugador pausa el juego estando bajo el
> agua, `mezcla_transicionar(global.estado_pausa, ...)` sustituye el objetivo entero: el filtro
> de agua deja de animarse (se queda congelado en el valor que tuviera) y solo se anima el de
> pausa. Para dos condiciones simultáneas de verdad hacen falta o bien un tercer estado explícito
> (`global.estado_pausa_bajo_agua`, con los dos filtros a la vez) o bien una pila de prioridades
> — que es un sistema más grande y no es lo que resuelve esta receta. Con dos o tres
> combinaciones posibles, declararlas a mano es más barato que construir la pila.

### 3.4 El sistema de importancia de Overwatch: puntuar, agrupar en cubos y resolver por frame

Cada sistema del juego que quiera lanzar un sonido «del mundo» que compite por sitio (impactos,
cargas de ataque, gritos, explosiones lejanas) **pide turno** en vez de llamar directamente a
`sonar_en()`. Al final del frame, después de que todos hayan pedido, se decide qué suena de
verdad — el mismo patrón de «actuar en Step, resolver en End Step» que ya usa la cámara en
[01 · 06 §4](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md#4-el-orden-exacto-de-cada-step)
para seguir al jugador ya movido:

```gml
// ═══════════ scr_importancia — el sistema de Overwatch (13 · 09 §1.3) ═══════════

global.cola_importancia = [];

/// scr_importancia · importancia_calcular(_dano, _dist, _dist_max, _visible)
/// @desc  0-100. Tres factores, con el peso que 13 · 09 §1.3 describe en prosa: el daño pesa
///        más que la distancia, y la distancia más que la visibilidad — ajusta los pesos a tu
///        juego, no son una cifra publicada (⚠️ ver Fuentes).
function importancia_calcular(_dano, _dist, _dist_max, _visible)
{
    var _por_dano  = clamp(_dano / 10, 0, 1)              * 50;   // 0-50
    var _por_cerca = clamp(1 - (_dist / _dist_max), 0, 1) * 30;   // 0-30
    var _por_ver   = _visible ? 20 : 0;                           // 0-20
    return _por_dano + _por_cerca + _por_ver;
}

/// scr_importancia · importancia_bucket(_score)
/// @return {String}  "alto" | "normal" | "bajo" | "descartado"
function importancia_bucket(_score)
{
    if (_score >= 65) { return "alto";       }
    if (_score >= 35) { return "normal";     }
    if (_score >= 12) { return "bajo";       }
    return "descartado";
}

/// scr_importancia · sonido_solicitar(_sonido, _px, _py, _dano, _dist_max, _visible)
/// @desc  Llamar en vez de sonar_en() para cualquier sonido de mundo que compita por sitio.
///        Usa obj_audio.oyente_x/oyente_y, calculados en §3.2.
function sonido_solicitar(_sonido, _px, _py, _dano, _dist_max, _visible)
{
    var _dist  = point_distance(obj_audio.oyente_x, obj_audio.oyente_y, _px, _py);
    var _score = importancia_calcular(_dano, _dist, _dist_max, _visible);
    array_push(global.cola_importancia, { sonido : _sonido, score : _score, px : _px, py : _py });
}

/// scr_importancia · importancia_resolver()  — llamar UNA vez, desde obj_audio · End Step,
///                    después de que TODOS los Step del frame hayan podido pedir turno.
function importancia_resolver()
{
    if (array_length(global.cola_importancia) == 0) { return; }

    // ⚠️ array_sort() con función personalizada trunca a 0 cualquier diferencia de coma
    // flotante MENOR que 1 — lo advierte su propia página del manual. Con un score real
    // (no enteros) hay que envolver la resta en sign(), o el orden queda indefinido.
    array_sort(global.cola_importancia, function(_a, _b) { return sign(_b.score - _a.score); });

    var _cupos  = { alto : 6, normal : 3, bajo : 1 };     // "descartado" nunca suena
    var _usados = { alto : 0, normal : 0, bajo : 0 };

    for (var _i = 0; _i < array_length(global.cola_importancia); _i += 1)
    {
        var _c      = global.cola_importancia[_i];
        var _bucket = importancia_bucket(_c.score);
        if (_bucket == "descartado") { continue; }
        if (struct_get(_usados, _bucket) >= struct_get(_cupos, _bucket)) { continue; }

        struct_set(_usados, _bucket, struct_get(_usados, _bucket) + 1);
        var _refuerzo = (_bucket == "alto") ? db_to_lin(2) : 1;   // lo importante se abre paso
        sonar_en(_c.sonido, _c.px, _c.py, _refuerzo, 10);          // pasa por el anillo (§1.2)
    }

    global.cola_importancia = [];
}
```

La visibilidad se calcula con la **misma técnica** que la oclusión barata de
[13 · 09 §5.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#53-oclusión-barata-una-pared-se-come-los-agudos):
un `collision_line()` entre el oyente y la fuente contra las paredes del nivel.

```gml
/// obj_enemigo · al empezar una carga de ataque (ejemplo de uso)
var _visible = (collision_line(x, y, obj_audio.oyente_x, obj_audio.oyente_y, obj_pared, false, true) == noone);
sonido_solicitar(snd_enemigo_carga, x, y, /*dano*/ 3, /*dist_max*/ 480, _visible);
```

> 💡 **Este sistema arbitra ENTRE sonidos distintos que compiten en el mismo frame**; el cupo de
> voces de `sonar_limitado()` (§1.4) limita cuántas copias del **mismo** sonido suenan a la vez.
> Úsalos juntos: `sonido_solicitar()` para decidir qué de todo lo que pide sonar este frame se
> gana un hueco, `sonar_limitado()` para que ese mismo sonido, si se repite muchas veces
> seguidas, no se amontone.

---

## 4 · Checklist

- [ ] La tabla material → banco de §3.1 está rellena para **todos** los materiales del tileset
      del suelo, con un caso por defecto razonable (§2.1).
- [ ] El tilemap del suelo se resuelve en **Room Start**, no en Create, si `obj_audio` es
      `persistent` (§3.1) — de lo contrario, la segunda room hereda el tilemap de la primera.
- [ ] Cada zona de reverberación (§3.2) tiene su tamaño puesto por **escala**, no por sprites
      distintos, y no se solapa con otra salvo que de verdad lo necesites (§2.2).
- [ ] La reverberación de zona vive en el bus que alimenta el **anillo de emisores**
      (`global.bus.sfx`), nunca en un bus al que nada llega (§1.2, §3.2).
- [ ] Cada estado de mezcla de §3.3 declara **todos** los parámetros de efecto que le importan,
      incluido el estado «normal» — un parámetro que un estado no menciona se queda congelado en
      lo último que valió.
- [ ] `mezcla_transicionar()` se llama con una duración explícita (§3.3): 0 s es válido para el
      arranque, pero nunca para una transición que el jugador debe notar sin sobresalto.
- [ ] Las combinaciones de estados que tu juego permite de verdad (pausa + bajo el agua, por
      ejemplo) están **declaradas como estados propios**, no asumidas por accidente (§3.3 ⚠️).
- [ ] El comparador de `array_sort()` en `importancia_resolver()` usa `sign()` sobre la resta de
      puntuaciones, no la resta a secas (§3.4 ⚠️).
- [ ] Los cupos por cubo de §3.4 se ajustaron escuchando la escena más ruidosa del juego, no la
      pantalla de título.
- [ ] Cualquier sonido que dependa de una zona de reverberación o de un estado de mezcla que
      toque un bus propio se lanza con `sonar_en()` (o con un emisor de categoría), nunca con
      `audio_play_sound()` a secas ni con `sonar_limitado()` tal cual está en 13 · 09 §3.3 (§1.2).

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Qué se oye o qué falla | Arreglo |
|---|---|---|
| **Esperar que la reverberación de zona afecte a `sonar_limitado()` o a `audio_play_sound()`** | El efecto «no funciona» sin ningún error en consola | Solo lo que pasa por un emisor recibe el bus (§1.2); usa `sonar_en()` si necesitas la zona |
| **Buscar el tilemap del suelo en Create con `obj_audio` persistente** | Los pasos suenan al material de la PRIMERA room en todas las demás | Resolverlo en Room Start (§3.1) |
| **Un estado de mezcla que no declara el parámetro que otro estado sí anima** | Al volver al estado «normal», el filtro se queda congelado en el valor del estado anterior | Declara el valor neutro en TODOS los estados que puedan sucederse (§3.3) |
| **Dos estados de mezcla simultáneos sin declarar la combinación** | Pausar bajo el agua quita el filtro de agua sin avisar | Estado explícito para la combinación, o aceptar y documentar que uno gana (§3.3 ⚠️) |
| **`array_sort()` con una resta de floats sin `sign()`** | El orden de importancia es errático cuando dos puntuaciones difieren menos de 1 punto | Envolver la resta en `sign()` — lo advierte la propia página del manual (§3.4) |
| **Zonas de reverberación solapadas sin prioridad** | Qué zona "gana" varía frame a frame sin patrón aparente | Prioridad explícita por zona, o no solapar (§2.2, §3.2) |
| **Cupos de importancia copiados de otro juego sin escuchar la escena propia** | O se descarta lo importante, o se amontona todo igual que sin el sistema | Ajustar cupos contra la escena más ruidosa real del proyecto (§2.4) |
| **Confundir esto con la música en capas** | Se intenta resolver un crossfade de pistas de música con `mezcla_estado_crear()` | Eso es [04 · 26](./26%20-%20Música%20adaptativa%20por%20capas.md); este documento mezcla buses y efectos, no pistas |

---

## Ver también

- [13 · 09 — Diseño de sonido y mezcla](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md) — el gestor completo (§4.2), el banco con *round robin* y el cupo de voces (§3.2, §3.3), el anillo de emisores (§5.2), la oclusión (§5.3) y el sistema de importancia explicado en prosa (§1.3), todos la base de este documento
- [02 · 07 — Audio: buses y efectos](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md) — la API de `AudioEffectType`, y los dos ejemplos (§5.8, §5.9) que §3.3 generaliza
- [13 · 04 — Animación de sprites, Sequences y Animation Curves](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/04%20-%20Animación%20de%20sprites%2C%20Sequences%20y%20Animation%20Curves.md) — los Broadcast Messages del sprite (§3.6) que disparan los pasos de §3.1
- [13 · 02 — Diseño de niveles](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/02%20-%20Diseño%20de%20niveles.md) — el patrón `obj_zona` (§3.6) que §3.2 reutiliza para las zonas de reverberación
- [08 · 24 — Audio avanzado](../08%20-%20Referencia%20GML%20completa/24%20-%20Audio%20avanzado%20-%20buffers%2C%20colas%2C%20sincronía%20y%20grabación.md) — *buffers*, colas, *sync groups* y Doppler: lo que este documento no cubre
- [04 · 26 — Música adaptativa por capas](./26%20-%20Música%20adaptativa%20por%20capas.md) — el problema hermano de los estados de mezcla, resuelto a nivel de pistas de música en vez de buses
- [04 · 27 — Accesibilidad](./27%20-%20Accesibilidad.md) — subtítulos de efectos y avisos direccionales para lo que la reverberación y la importancia comunican solo por oído
- [01 · 06 — Eventos y ciclo del juego](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) — el orden exacto de Step / End Step (§4) en el que se apoya `importancia_resolver()`

---

## Fuentes

Consultadas el **6 de septiembre de 2026**.

**Manual oficial de GameMaker (LTS)** — espejo local en `09 - Manual oficial/manual-lts-2026-es/`,
páginas abiertas directamente en esta sesión:

- `GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_at_pixel.htm` — devuelve `-1` en error; el índice coincide con la posición en el tile set si el tile no está volteado ni rotado
- `.../Tile_Map_Layers/tile_get_index.htm` y `.../tile_get_empty.htm`
- `.../Tile_Map_Layers/layer_tilemap_get_id.htm` — admite nombre de capa como *string*, con el aviso explícito de impacto en rendimiento
- `GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/position_meeting.htm` — acepta un id de instancia, no solo un asset de objeto
- `GameMaker_Language/GML_Reference/Variable_Functions/array_sort.htm` — el aviso sobre truncar a 0 diferencias de coma flotante menores que 1 en el comparador personalizado
- `GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Effects/AudioBus.htm` — `gain` (0-1) y `effects` (array fijo de 8)
- `GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Effects/AudioEffect.htm` — campos exactos de `Reverb1` (`size`, `damp`, `mix`) y `LPF2` (`cutoff`, `q`)

**Símbolos verificados con `python3 _indice/buscar.py`** contra `simbolos.json` (runtime
`2026.0.0.23`): `tilemap_get_at_pixel`, `layer_tilemap_get_id`, `tile_get_index`,
`tile_get_empty`, `layer_get_id`, `audio_bus_create`, `audio_emitter_create`,
`audio_emitter_bus`, `audio_emitter_falloff`, `audio_emitter_position`, `audio_play_sound_ext`,
`audio_effect_create`, `audio_sound_gain`, `audio_falloff_set_model`, `db_to_lin`,
`audio_bus_main`, `event_data`, `array_sort`, `array_delete`, `array_push`, `array_length`,
`array_copy`, `struct_get`, `struct_set`, `struct_exists`, `struct_get_names`, `irandom`,
`irandom_range`, `random_range`, `choose`, `lerp`, `clamp`, `mean`, `sign`, `point_distance`,
`distance_to_point`, `collision_line`, `collision_point`, `collision_point_list`,
`collision_rectangle`, `instance_place`, `position_meeting`, `place_meeting`, `audio_is_playing`,
`audio_stop_sound`, `audio_emitter_free`, `audio_emitter_gain`, `audio_group_set_gain`,
`method`, `max`, `min`, `delta_time`, `gamespeed_fps`, `game_get_speed`, `camera_get_active`,
`camera_get_view_x`, `camera_get_view_y`, `camera_get_view_width`, `camera_get_view_height`,
`is_undefined`, `noone`, `with` (estructura del lenguaje, no función).

**Biblioteca interna ya verificada** — este documento se apoya en trabajo ya sourced ahí y no lo
repite: `13 · 09` (el sistema de importancia de Overwatch — GDC 2016, Lawlor y Neumann — está
citado con su URL original en la sección Fuentes de ese documento, no reabierta esta sesión) y
`02 · 07` (el tutorial oficial *How To Use Audio Effects in GameMaker*, también citado allí).

> ⚠️ **Marcado como no verificado esta sesión**: los pesos exactos de `importancia_calcular()`
> (50/30/20) y los cupos de `importancia_resolver()` (6/3/1) son un punto de partida razonable
> a partir de la descripción en prosa de la charla de Overwatch, no una cifra publicada por
> Blizzard — el propio `13 · 09 §1.3` no da números, solo el criterio. Los rangos de índices del
> tileset en §3.1 son un ejemplo: cada proyecto los redefine según cómo organizó su tileset real.
