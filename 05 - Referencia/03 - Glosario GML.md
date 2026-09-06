# 03 · Glosario GML (A–Z)

> **Referencia alfabética** de los términos de GameMaker y GML que vas a encontrarte leyendo el
> manual, el foro, los vídeos y el código de la comunidad.
> Generado en **agosto de 2026** · Contexto: **GameMaker LTS 2026.0** (IDE 2026.0.0.16 · GMS2 Runtime 23).
> Cada término lleva **qué es** y **cuándo te lo vas a encontrar**.

---

## Cómo leer este glosario

- Los nombres de funciones, constantes y argumentos se respetan **en inglés** (son la API real).
- Cuando un término tiene un **handle** asociado o un cambio reciente en 2026, está marcado con 🆕.
- Cuando es una trampa o un error común, está marcado con ⚠️.
- Cuando el término está **deprecado** o en desuso, está marcado con ❌.

---

## A

**Alarm (alarma)**
Un temporizador por instancia. Hay 12 ranuras (`alarm[0]`…`alarm[11]`); cuando el contador llega
a 0 se dispara el evento **Alarm** correspondiente. Se cuentan en *steps*, no en segundos.
*Cuándo te lo encontrarás:* en código antiguo y en tutoriales previos a 2023. En 2026, para
temporizadores serios, usa **Time Sources** o `call_later()`, que son independientes del
framerate y cancelables.

**Alpha (alfa)**
El canal de transparencia, de 0 (transparente) a 1 (opaco). Se controla con `draw_set_alpha()` o
`image_alpha`. ⚠️ Olvidar restaurarla a 1 después de dibujar es el bug de renderizado más común
de la historia de GameMaker.

**Application surface**
La superficie (textura) sobre la que GameMaker dibuja **todo** el juego antes de volcarla a la
ventana. Es lo que te permite aplicar shaders o efectos de pantalla completa. Accesible con
`application_surface`.
*Cuándo te la encontrarás:* al hacer transiciones, *post-processing*, o al resolver por qué tu
juego se ve borroso o con el tamaño equivocado.

**Array**
Colección ordenada de valores, indexada desde 0. En GML moderno son objetos de primera clase:
se redimensionan solos, se pasan por referencia y se limpian con el **garbage collector**.
Sustituyen a `ds_list` y `ds_grid` en casi todos los casos.
*Cuándo te lo encontrarás:* constantemente. Ver [05 - Fundamentos/05](../01%20-%20Fundamentos/05%20-%20Arrays%20y%20estructuras%20de%20datos.md).

**Asset**
Cualquier recurso del proyecto: sprite, objeto, room, sonido, fuente, tileset, shader, script,
nota, secuencia, partícula, etc. En 2026 los assets se referencian por **handle**.

**Asset browser**
El panel del IDE donde se ve el árbol de recursos del proyecto. Su organización en carpetas es
**tuya**: GameMaker no impone ninguna.

**Asset bundle**
Paquete de assets distribuible (plantillas, prefabs, kits de inicio). Los oficiales viven en
<https://gamemaker.io/en/bundles> o se instalan desde el **Package Manager**.
*Cuándo te lo encontrarás:* al instalar una plantilla o un pack de arte.

**Audio bus**
🆕 Ruta de mezcla de audio con efectos aplicables. Permite, por ejemplo, bajar el volumen de
toda la música cuando habla un personaje (*ducking*) sin tocar los efectos de sonido.
*Cuándo te lo encontrarás:* al montar el audio de un juego con varias capas. Ver [02 - Novedades/07](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md).

---

## B

**Batch / Batching (lote)**
Agrupación de operaciones de dibujo para enviarlas a la GPU de una vez. Cada cambio de textura,
shader o blend mode **rompe el batch** y cuesta rendimiento.
*Cuándo te lo encontrarás:* optimizando el Draw event. Ver [01 - Fundamentos/11](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md).

**Bed (cama de ambiente)**
Un bucle de ambiente largo y sin nada que destaque, pensado para sonar de fondo sin llamar la
atención; sus **one-shots** (ver esa entrada) le dan vida por encima.
*Cuándo te lo encontrarás:* al montar el ambiente de una zona. Ver [13 · 09 §6](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md).

**Blend mode (modo de mezcla)**
Cómo se combina el color que dibujas con lo que ya hay en pantalla: `bm_normal` (opaco),
`bm_add` (suma, para luces y fuego), `bm_subtract`, `bm_multiply`… Se cambia con
`gpu_set_blendmode()`. ⚠️ Siempre vuelve a `bm_normal` cuando termines.

**bool**
Tipo booleano de GML: `true` / `false`. En GML clásico no existía y se usaba 1/0; en 2026 es un
tipo real.

**Bounding box (BBox)**
El rectángulo alineado a los ejes que delimita una instancia: `bbox_left`, `bbox_right`,
`bbox_top`, `bbox_bottom`. Es la forma más barata de detectar colisiones. 🆕 En 2026 los bboxes
son **precisos e inclusivos**.
*Cuándo te lo encontrarás:* en colisiones, culling y checks de «¿está esto en pantalla?».

**Buffer**
Bloque de memoria binaria sin formato. Se usa para networking, lectura/escritura de ficheros
binarios y paso de datos a extensiones. ⚠️ **No** se limpia solo: hay que llamar a
`buffer_delete()`.

**Built-in time source**
Los dos Time Sources que existen siempre: `time_source_global` (no lo afecta la pausa del juego)
y `time_source_game` (sí la afecta). Todo Time Source que crees hereda de uno de ellos.

---

## C

**Camera (cámara)**
El «ojo»: define **qué parte de la room** se ve. Tiene posición, tamaño, ángulo y velocidad de
seguimiento. Se crea con `camera_create()` y se asigna a un **viewport**.
*Cuándo te la encontrarás:* en el momento en que tu room sea más grande que la pantalla.

**Clean Up event**
Evento que se ejecuta cuando una instancia se destruye **o** cuando la room termina. Es el sitio
correcto para liberar surfaces, buffers, `ds_*` y Time Sources.
*Cuándo te lo encontrarás:* cada vez que tu juego pierda memoria sin motivo aparente.

**Code Editor 2 (CE2)**
🆕 El nuevo editor de código de GameMaker, disponible en la Beta: eventos unificados en un solo
archivo, vistas divididas, mejor Feather. Es **opt-in**.

**Collision space**
El «espacio» lógico en el que viven las instancias a efectos de colisión. Las funciones de
activación/desactivación (`instance_deactivate_object()` y compañía) aceptan un argumento
`collision_space`.
*Cuándo te lo encontrarás:* al hacer *object pooling* con desactivación, o rooms grandes con
chunking.

**Constant (constante)**
Valor con nombre que no cambia. En GML: `enum` (preferido, lo entiende Feather) o `#macro`
(texto sustituido antes de compilar).

**Constructor**
Bloque especial para fabricar **structs** con una forma definida:

```gml
function Enemigo(_vida) constructor {
    vida = _vida;
    static recibir_dano = function(_d) { vida -= _d; };
}
var _e = new Enemigo(10);
```

*Cuándo te lo encontrarás:* cuando quieras datos con comportamiento sin necesidad de instancias.
Ver [01 - Fundamentos/04](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md).

---

## D

**Data structure (`ds_*`)**
❌ En desuso relativo. Las estructuras de datos clásicas: `ds_list`, `ds_map`, `ds_grid`,
`ds_stack`, `ds_queue`, `ds_priority`. ⚠️ **Hay que liberarlas a mano** (`ds_*_destroy()`) y no
se serializan a JSON automáticamente. En 2026 usa arrays y structs salvo necesidad concreta
(por ejemplo `ds_priority` para una cola con prioridad real).

**Debug overlay**
Visualización superpuesta con FPS, conteo de instancias, texturas, memoria y más. Se activa con
`show_debug_overlay(true)`. Es la primera herramienta de diagnóstico que deberías usar.

**delta_time**
Microsegundos transcurridos desde el *frame* anterior. Es la base del movimiento independiente
del framerate: `x += _velocidad * (delta_time / 1000000)`.
*Cuándo te lo encontrarás:* cuando tu juego vaya más rápido en un monitor de 144 Hz.
⚠️ No lo confundas con `room_speed`.

**depth (profundidad)**
Valor que decide el orden de dibujado: menor `depth` se dibuja **antes** (por detrás).
⚠️ En 2026 las **layers** mandan sobre `depth`; úsalo solo para ordenar instancias dentro de una
misma capa. Ver [01 - Fundamentos/10](../01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md).

**Device Input**
Sistema moderno de entrada unificado (teclado, ratón, gamepad, táctil) frente a las funciones
clásicas `keyboard_check()` / `gamepad_button_check()`.
*Cuándo te lo encontrarás:* al dar soporte a varios dispositivos sin duplicar lógica.

**Draw GUI**
Evento de dibujado en **coordenadas de pantalla**, sin transformación de cámara. Era la forma
clásica de hacer HUDs. 🆕 En 2026 compite con las **UI Layers**.

**Ducking**
Bajar automáticamente el volumen de un bus (normalmente la música) mientras suena otro
(normalmente un diálogo o un *stinger*), y devolverlo al terminar. En GameMaker se hace a mano con
`audio_sound_gain()` sobre el bus, más rápido al bajar que al subir para que no se note un
«bombeo». Los buses nativos no traen un compresor de entrada lateral (ver **Sidechain**): el
ducking es la forma en que este motor implementa la misma idea.
*Cuándo te lo encontrarás:* en cualquier juego con diálogo sobre música. Ver [13 · 09 §4.2](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md).

---

## E

**Enum**
Lista de constantes con nombre y autocompletado. Es la forma recomendada de definir constantes
porque **Feather lo entiende** y te valida los tipos.

**Event (evento)**
Momento del ciclo de juego en el que se ejecuta tu código: Create, Destroy, Step, Draw,
Collision, Alarm, Keyboard… 🆕 Code Editor 2 los unifica todos en un mismo archivo.
*Cuándo te lo encontrarás:* siempre. Conocer el **orden** de eventos evita la mayoría de bugs de
principiante. Ver [01 - Fundamentos/06](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md).

**Extension**
Código nativo (o GML empaquetado) que amplía las capacidades del motor. Se distribuye como
`.yymps` y, en 2026, también vía **Package Manager**. Las oficiales de YoYoGames se llaman
`GMEXT-*`. Ver [07 - Ecosistema/03](../07%20-%20Ecosistema/03%20-%20Extensiones%20oficiales%20y%20de%20terceros.md).

---

## F

**Falloff (atenuación por distancia)**
La curva con la que un emisor de audio pierde volumen según se aleja del oyente:
`audio_falloff_set_model()` elige el modelo (lineal, inverso, exponencial…) y
`audio_emitter_falloff()` fija la distancia de referencia, la máxima y el factor. ⚠️ El modelo por
defecto es `audio_falloff_none`: sin llamarlo a mano, la distancia no atenúa nada.
*Cuándo te lo encontrarás:* al montar sonido posicional, en 2D o en 3D. Ver [13 · 09 §5.1](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md) y [04 · 29 §7 bis](../04%20-%20Recetas%20por%20g%C3%A9nero/29%20-%203D%20en%20GameMaker.md) para el caso en 3D.

**Feather**
El analizador estático de código de GameMaker. Detecta variables sin definir, tipos
inconsistentes, argumentos mal usados y código muerto. 🆕 **Activado por defecto en 2026.**
Se alimenta con **JSDoc**: `/// @param {Real} _velocidad`.
*Cuándo te lo encontrarás:* cada vez que compiles. Sus avisos son tu mejor revisor de código.

**Fixture**
Cuerpo físico rígido del sistema de física integrado (Box2D). Se define con `fixture_*` y se
asocia a una instancia. Solo tiene sentido si activas el mundo de física.
*Cuándo te lo encontrarás:* en juegos con físicas reales (no arcade). La mayoría de los juegos
2D **no** lo necesitan.

**Flexpanel**
🆕 Sistema de layout tipo **flexbox** (basado en Yoga) para construir interfaces responsive
dentro de una **UI Layer**. Se accede por código con `layer_get_flexpanel_node()`.
*Cuándo te lo encontrarás:* al montar un HUD, un menú o un inventario.

**Foley**
Efectos de sonido grabados imitando la acción en pantalla (pasos, telas, impactos), en vez de
sacados de una librería. Es la fuente que más identidad da a un juego y, grabada por ti mismo,
también la más barata.
*Cuándo te lo encontrarás:* al decidir de dónde sale cada SFX. Ver [13 · 09 §8](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md).

**Font asset**
Recurso de fuente. Se crea desde un archivo `.ttf`/`.otf` o se genera desde un rango de
caracteres. En 2026 soporta **SDF** y efectos.

**FPS / fps_real**
`fps` es la media de fotogramas por segundo de los últimos frames (suavizada); `fps_real` es la
medición real del frame actual. Si `fps` dice 60 y `fps_real` dice 200, estás midiendo mal.

---

## G

**Garbage collector (GC / recolector de basura)**
Proceso que libera automáticamente la memoria de los **structs** y los **arrays** que ya no se
usan. ⚠️ **No** libera surfaces, buffers, `ds_*`, time sources ni instancias desactivadas.
*Cuándo te lo encontrarás:* al investigar por qué tu juego consume más memoria con el tiempo.

**Game Options**
La configuración por plataforma del proyecto (Windows, Android, HTML5, iOS, Switch…). Se edita
en el IDE y es lo que determina iconos, permisos, orientación y empaquetado.

**GMRT (GameMaker Runtime)**
El runtime nuevo de GameMaker, nombre en clave **Cronus**. Arquitectura abierta: CMake,
LLVM/Clang, Dawn (WebGPU) y SDL2. Está en **Beta 0.21** (agosto de 2026) y se instala desde el
**Package Manager**. 🆕 Todo el desarrollo nuevo va aquí; el GMS2 Runtime está *feature
complete*. ⚠️ Tiene su propia lista de *«Changes to GML»*: **no** es 100 % compatible.
Ver [02 - Novedades/03](../02%20-%20Novedades%202026/03%20-%20GMRT%20-%20El%20nuevo%20runtime.md).

**GMS2 / GMS2 Runtime**
El runtime clásico de GameMaker: Studio 2, el que usa tu proyecto de LTS 2026.0 (versión 23).
Estable, con todos los targets de exportación, pero **feature complete**: no recibe
características nuevas.

**GML (GameMaker Language)**
El lenguaje de scripting de GameMaker. Sintaxis similar a C/JS, de tipado dinámico, con
**structs**, **constructores**, **métodos** y **handles**.

**GMX**
❌ Formato de proyecto de GameMaker: Studio 1.x, basado en XML. Obsoleto; si lo encuentras en
un repo antiguo, tendrás que migrarlo.

**GMZ / YYZ**
`GMZ` es el formato de exportación comprimido de GMS 1.x; **`YYZ`** es el de GMS2 en adelante:
un paquete con todo el proyecto, ideal para **backups**. Ver [Curso 23](../03%20-%20Cursos%20%28YouTube%29/23%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Respaldos%20con%20YYZ.md).

**GUI layer**
Capa conceptual donde dibujas sin transformación de cámara (evento **Draw GUI**). Ver **Draw GUI**.

---

## H

**Handle**
🆕 **El cambio más importante de 2026.** Referencia opaca y con tipo a un asset o a una
estructura de datos. Sustituye a los IDs numéricos.

```gml
// ❌ Ya no
var _sig = sprite_index + 1;
// ✅ Sí
var _spr = spr_enemigo_idle;
if (is_handle(_spr)) { sprite_index = _spr; }
```

⚠️ Los handles **no** son enteros: no puedes sumarles, restarles ni compararlos con `-1`.
*Cuándo te lo encontrarás:* al portar código anterior a 2024 y al usar funciones de assets.
Ver [01 - Fundamentos/03](../01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md).

---

## I

**ID / Instance ID**
Identificador único de una **instancia** en la room. Se obtiene como `id`. ⚠️ No lo confundas con
el ID de un **objeto** (asset). En 2026 los IDs de asset son handles; los de instancia siguen
siendo referencias de instancia.

**IDL (Interface Definition Language)**
Lenguaje para describir la interfaz de una extensión nativa. Lo usa el **Extension Generator**
(`extgen`) de YoYoGames para generar el pegamento entre C++ y GML automáticamente.

**INI**
Formato de fichero de configuración clave=valor. Funciones `ini_open()` / `ini_write_real()` /
`ini_close()`. Útil para opciones; insuficiente para partidas guardadas (usa **JSON**).

**Instance (instancia)**
Una **cosa viva en la room**, creada a partir de un **object**. Tiene variables propias, eventos
y posición. `instance_create_layer()` la crea; `instance_destroy()` la destruye.
*Cuándo te lo encontrarás:* constantemente. El modelo objeto/instancia es el corazón de
GameMaker. Ver [01 - Fundamentos/09](../01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md).

**instance_change()**
❌ **Deprecada en 2026.** Cambiaba el objeto de una instancia conservando su estado.
Sustitúyela por: destruir y crear una nueva pasando un struct con los datos, o por una arquitectura
basada en structs.

**int64**
Entero de 64 bits. GML usa `real` (double) por defecto; `int64` existe para operaciones bitwise
de 64 bits y para IDs grandes.

---

## J–K

**JSON**
Formato de intercambio de texto. En GML: `json_stringify()` convierte structs/arrays a texto y
`json_parse()` lo convierte de vuelta. Es la forma estándar de guardar partidas.
⚠️ No serializa `ds_*` ni el contenido de assets (guarda la referencia por nombre).

**JSDoc**
Comentarios estructurados (`/// @param`, `/// @returns`, `/// @desc`) que **Feather** usa para
inferir tipos y avisarte de errores. En 2026 es parte del estilo recomendado, no un adorno.

---

## L

**Layer (capa)**
Contenedor dentro de una **room** que agrupa elementos: instancias, tilemaps, fondos, rutas de
assets, efectos FX, partículas o UI. Define el orden de dibujado y permite activar/desactivar
grupos enteros. En 2026 es la forma correcta de organizar una room.

**LSP (Language Server Protocol)**
Protocolo estándar que usan los editores externos (como **GMEdit**) para ofrecer
autocompletado y diagnóstico de GML. Es la misma tecnología que alimenta a Feather dentro del IDE.

**LTS (Long Term Support)**
Rama de GameMaker congelada y mantenida durante años, pensada para proyectos serios.
**LTS 2026.0** se publicó el 21 de mayo de 2026 y tendrá soporte hasta al menos el Q1 de 2028.

**LUFS / dBTP**
Las dos unidades con las que se mide el volumen final de una mezcla: **LUFS** (*Loudness Units
Full Scale*, idéntico a LKFS) mide la sonoridad percibida integrada de toda la sesión; **dBTP**
(*decibelios True Peak*) mide el pico real tras reconstruir la señal, que puede superar al pico
que se ve en la forma de onda. Los estándares del oficio piden la mezcla entre −23 y −18 LUFS con
el pico por debajo de −1 dBTP.
*Cuándo te lo encontrarás:* al medir la mezcla antes de publicar. Ver [13 · 09 §4.4](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md).

---

## M

**Mask (máscara)**
La forma que usa GameMaker para las **colisiones** de una instancia. O se genera
automáticamente a partir del sprite, o se asigna explícitamente con `mask_index`.
*Cuándo te lo encontrarás:* cuando tu personaje se atasque en esquinas o colisione con
transparencias.

**method()**
Función que crea un **método**: una función ligada a un ámbito (`self`) concreto.
`var _cb = method(id, mi_funcion);` permite pasar esa función a otra parte sin perder el `self`.

**mp_grid**
Rejilla para planificación de movimiento (pathfinding). `mp_grid_create()` la construye,
`mp_grid_add_instances()` marca obstáculos y `mp_grid_path()` calcula la ruta (A*).
*Cuándo te lo encontrarás:* en tower defense, RTS y juegos de estrategia.

---

## N

**NaN / infinity**
Valores numéricos especiales: *Not a Number* e infinito. Aparecen al dividir por cero o al
hacer raíces de negativos. ⚠️ `NaN` **no** es igual a `NaN`; usa `is_nan()` para detectarlo.

**noone / undefined**
`noone` (-4) significa «ninguna instancia» (lo devuelven `instance_place()` y compañía cuando no
hay colisión). `undefined` significa «sin valor asignado». Son distintos y no intercambiables.

**Note asset**
Recurso de texto dentro del proyecto. Útil para documentación interna, licencias y datos
embebidos.

---

## O

**Object (objeto)**
La **plantilla** de la que se crean las instancias. Define sprite, máscara, eventos y variables
iniciales. No vive en la room: vive en el Asset Browser.
*Cuándo te lo encontrarás:* es la unidad básica de organización de código de GameMaker.

**Object pooling**
Técnica de rendimiento: en vez de crear y destruir instancias continuamente (balas,
partículas, enemigos), las creas todas al principio y las **desactivas/activas** según haga
falta. Ver [`scr_pool.gml`](../06%20-%20Assets%20y%20Scripts/scr_pool.gml).

**One-shot**
Un sonido suelto que se dispara una vez y no está en bucle, por oposición al **bed** (ver esa
entrada): un pájaro, un crujido, un impacto puntual sobre un ambiente que sigue sonando debajo.
*Cuándo te lo encontrarás:* al diseñar un ambiente con vida, o cualquier SFX puntual. Ver [13 · 09 §6](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md).

**other**
Palabra clave que, dentro de un evento de colisión o dentro de un bloque `with()`, hace
referencia a **la otra** instancia implicada. ⚠️ Su significado cambia según el contexto:
en una colisión es el otro objeto; en un `with()` es el objeto que invocó el bloque.

---

## P

**Package Manager**
🆕 El gestor de paquetes del IDE. Instala y versiona assets, extensiones, prefabs e incluso el
propio runtime **GMRT**. Usa la sintaxis `::paquete-version::asset` para referenciar.
Ver [02 - Novedades/08](../02%20-%20Novedades%202026/08%20-%20Package%20Manager%20y%20Prefabs.md).

**Parent object**
Objeto del que otros heredan. Al heredar, el hijo ejecuta el evento del padre si no lo
sobrescribe (o si llama a `event_inherited()`). Úsalo con moderación: una jerarquía profunda
vuelve el código difícil de seguir.

**Particle system (sistema de partículas)**
🆕 En 2026 hay **dos**: el clásico por código (`part_system_create()`, `part_type_*`,
`part_emitter_*`) y el nuevo **asset de Particle System** con editor visual.
Ver [02 - Novedades/05](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20part%C3%ADculas%20nuevo.md).

**Path**
Recurso o estructura que define una ruta por la que una instancia puede moverse
(`path_start()`, `path_add()`). Se usa junto a `mp_grid_path()`.

**Persistence (persistencia)**
Propiedad de una **instancia** que hace que sobreviva al cambio de room (típicamente el
controlador del juego, el inventario o la música). No confundir con **guardar la partida**:
persistir es solo «no destruirte al cambiar de room».

**Pointer**
Referencia a una dirección de memoria, devuelta por algunas extensiones nativas. Tipo
peligroso: úsalo solo si la extensión lo exige.

**Prefab**
🆕 Asset reutilizable e instanciable con variaciones, instalable desde el **Package Manager**.
Las instancias de un prefab se pueden *customizar* o *duplicar*.
*Cuándo te lo encontrarás:* al usar plantillas oficiales o componentes de UI preconstruidos.

---

## R

**Robo de voz (*voice stealing*)**
Cuando se supera el cupo de voces (canales de audio) reservado para un sonido, quitarle el turno a
la instancia más antigua —con un fundido corto para no producir un *click*— en vez de dejar que se
amontonen veinte copias del mismo impacto sonando a la vez.
*Cuándo te lo encontrarás:* al limitar sonidos frecuentes (disparos, impactos). Ver [13 · 09 §3.3](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md).

**Room**
El «nivel» o escena: contiene layers, instancias, tilemaps, cámaras y viewports. Solo una room
está activa a la vez (salvo rooms persistentes superpuestas).

**room_speed**
Cuántos *steps* por segundo ejecuta la room (por defecto 60). ⚠️ **No** es una garantía: es el
objetivo. Para movimiento preciso usa `delta_time`.

**Round robin**
Reproducir una toma distinta cada vez que suena el mismo evento (3-5 variaciones de un disparo,
por ejemplo), en vez del mismo *sample* siempre igual, que a los pocos segundos suena a
«ametralladora robótica». Se combina con una variación aleatoria de tono.
*Cuándo te lo encontrarás:* en cualquier sonido que se repite mucho. Ver [13 · 09 §3.2](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md).

**Runner**
El ejecutable que corre tu juego. Ver **GMS2 Runtime** y **GMRT**.

---

## S

**Sandbox**
El aislamiento de sistema de ficheros que aplica GameMaker por plataforma. Dentro del sandbox
puedes escribir siempre; fuera, depende del target (en consolas y móviles normalmente no).
`game_save_id` es la carpeta correcta para guardar partidas.

**Script**
Recurso que contiene funciones GML. En GML moderno, las funciones definidas en un script son
**globales**. Los scripts también pueden declarar **constructores**.

**Sequence**
Recurso de animación por líneas de tiempo (como las cinemáticas). Se controla con
`sequence_*`. Útil para *cutscenes* y efectos complejos.

**Shader**
Programa que se ejecuta en la GPU, escrito en **GLSL ES** (o HLSL en algunos targets). Se
aplica con `shader_set()` / `shader_reset()` o como **FX** de capa.
*Cuándo te lo encontrarás:* efectos de pantalla completa, disoluciones, luces 2D.

**Sidechain (compresión por clave lateral)**
Técnica de mezcla en la que el nivel de una señal (la música) se reduce automáticamente en función
del nivel de OTRA señal (la voz), usando esta segunda como «clave» del compresor. ⚠️ Los buses de
audio de GameMaker **no** traen un compresor con entrada lateral: el motor implementa la misma
idea a mano, subiendo y bajando la ganancia por código. Ver **Ducking**.
*Cuándo te lo encontrarás:* leyendo sobre mezcla de audio en general; en GameMaker, la palabra que
usarás en la práctica es *ducking*.

**Sprite**
Recurso gráfico: una imagen o una animación de fotogramas. Tiene origen, máscara, puntos de
colisión y velocidad de animación (`image_speed`).

**Static**
Palabra clave para declarar un miembro **de la clase** (del constructor), no de la instancia.
En structs es donde van las funciones, para no duplicarlas en cada instancia:

```gml
function Enemigo() constructor {
    vida = 10;                      // por instancia
    static atacar = function() { };  // compartido
}
```

**Stinger**
Un remate musical corto que suena UNA vez sobre la música de fondo (recoger un objeto clave, matar
al jefe), no una capa en bucle. ⚠️ Debe compartir tono y tempo con la música de base: si desafina,
ningún ajuste de código lo arregla.
*Cuándo te lo encontrarás:* al puntuar momentos clave con música. Ver [04 · 26](../04%20-%20Recetas%20por%20g%C3%A9nero/26%20-%20M%C3%BAsica%20adaptativa%20por%20capas.md) y [13 · 09 §6](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md).

**Struct**
Estructura de datos ligera, tipo objeto JavaScript:

```gml
var _datos = { vida: 10, nombre: "slime" };
_datos.vida -= 1;
```

Se pasa por referencia y la limpia el **garbage collector**. Es la herramienta correcta para
**datos**; el objeto es la herramienta correcta para **comportamiento en el mundo**.

**Surface**
Textura en la que puedes dibujar en vez de en pantalla. Imprescindible para efectos, minimapas
y *post-processing*. ⚠️ **Puede desaparecer** (al cambiar de pantalla completa, al perder el
foco). Comprueba siempre `surface_exists()` antes de usarla, y destrúyela con
`surface_free()`.

---

## T

**Template string**
🆕 Cadena con interpolación: `` `Vida: {vida}` ``. Mucho más legible que concatenar con `+`.

**Texture page**
Imagen grande donde GameMaker empaqueta todos tus sprites para minimizar cambios de textura al
dibujar. Su tamaño y agrupación (texture groups) afectan directamente al rendimiento y al uso
de memoria.

**Tileset**
Recurso que define cómo se corta una imagen de tiles en celdas, con sus brushes y autotiles.

**Tilemap**
Capa de una room hecha de tiles. Es **mucho** más eficiente que miles de instancias para
construir el terreno. Se manipula con `tilemap_get()` / `tilemap_set()`.

**Time source**
🆕 Temporizador moderno y cancelable, con unidades en segundos o frames, repeticiones y
herencia de un time source padre. `time_source_create()` → `time_source_start()` →
`time_source_destroy()`. Sustituye a los **alarms** en casi todo.

**Typeof / is_\*()**
Funciones de comprobación de tipos: `typeof()`, `is_struct()`, `is_handle()`, `is_array()`,
`is_nan()`, `is_undefined()`, `instanceof()`. En 2026 la comprobación de tipos es estricta.

---

## U

**UI Layer**
🆕 Capa especial de room pensada para interfaces, que se dibuja **por encima de todo** y usa
**Flexpanels** para el layout. Sustituye la costumbre de dibujar el HUD en Draw GUI.
Ver [02 - Novedades/04](../02%20-%20Novedades%202026/04%20-%20UI%20Layers%20y%20Flexpanels.md).

**undefined**
Ver **noone / undefined**.

**Viewport**
El «marco»: define **dónde y con qué tamaño** se dibuja lo que ve una **cámara** dentro de la
ventana. Cámara y viewport son cosas distintas y confundirlas causa los clásicos problemas de
imagen borrosa o estirada.

**Vertex buffer**
Bloque de vértices listo para enviar a la GPU. Es la forma eficiente de dibujar geometría
personalizada (polígonos, luces 2D, mallas 3D). Se construye con `vertex_format_*` y
`vertex_*`.

**VM (Virtual Machine)**
Uno de los dos backends de compilación: el juego se compila a bytecode y se interpreta.
Compila rápido, ejecuta más lento. Úsalo durante el desarrollo. El otro es **YYC**.

---

## W–X

**WAD**
Formato de empaquetado de los assets del juego en el ejecutable final (los ficheros `.win`,
`.apk`, etc.). Contiene los datos del juego comprimidos.
*Cuándo te lo encontrarás:* leyendo la estructura de salida de un build o depurando carga de
assets.

**with()**
La construcción más característica de GML: ejecuta un bloque de código **en el ámbito de otra
instancia** (o de todas las de un objeto).

```gml
with (obj_enemigo) { vida -= 10; }   // afecta a todos los enemigos
```

⚠️ Dentro del bloque, `other` es quien invocó el `with()`.

---

## Y–Z

**YY**
Extensión de los ficheros de recursos individuales de un proyecto GMS2 (`*.yy`). Formato JSON
interno. ⚠️ **Nunca los edites a mano**: se corrompen con facilidad. Usa el IDE o
`gm-cli resourcetool`.

**YYP**
El fichero de proyecto de GMS2 en adelante (`*.yyp`). Es un JSON que lista todos los recursos.
⚠️ Tampoco se edita a mano.

**YYZ**
Paquete comprimido de todo el proyecto. Es la forma recomendada de hacer **backups** y de
compartir un proyecto. Se crea desde *File → Export Project → YYZ*.

**YYC (YoYo Compiler)**
El otro backend de compilación: compila GML a **C++** y de ahí a código nativo. Tarda más en
compilar pero ejecuta mucho más rápido. Es lo que debes usar para **release**.
*Cuándo te lo encontrarás:* al exportar la versión final y al perfilar rendimiento real.

---

## Términos que NO existen (no los busques)

| Término | Realidad |
|---|---|
| `Chorus` | ❌ No existe. El sistema de audio de Juju Adams es **Vinyl**. |
| `sprite_is_visible()` | ❌ No existe. Usa `sphere_is_visible()` o tus propios checks de bbox. |
| `handle_type()` | ❌ No existe. Usa `is_handle()` y `typeof()`. |
| `path_create()` | ❌ No existe. Es **`path_add()`**. |
| `ds_*` liberados automáticamente | ❌ Falso. Hay que llamar a `ds_*_destroy()`. |
| `buffer_save()` para guardar partidas | ❌ `buffer_save()` **no es** lo que parece: es `game_save_buffer()`. Para guardar usa **JSON**. |

---

## Verificación

Todos los nombres de funciones, constantes y tipos de este glosario se han comprobado contra el
manual oficial con `gm-cli manual read "<término>"` (manual *monthly*, disponible offline),
salvo los marcados explícitamente.

| Comprobado | Resultado |
|---|---|
| `clamp`, `lerp`, `angle_difference`, `dsin`, `dcos`, `power` | ✅ Nativas — **no** reimplementar |
| `approach`, `wave`, funciones de easing | ❌ **No** existen como nativas |
| `time_source_create/start/stop/destroy`, `time_source_global`, `time_source_game` | ✅ Existen |
| `time_source_units_seconds/frames`, `time_source_expire_nearest/after` | ✅ Existen |
| `call_later(period, unit, callback, [loop])`, `call_cancel` | ✅ Existen |
| `mp_grid_create/add_instances/add_cell/path/destroy` | ✅ Existen |
| `path_add`, `path_delete`, `path_start`, `path_end`, `path_get_length` | ✅ Existen |
| `camera_create/destroy/set_view_pos/set_view_size/set_view_target/apply` | ✅ Existen |
| `json_stringify`, `json_parse`, `struct_exists`, `struct_set`, `struct_get_names` | ✅ Existen |
| `file_text_open_write/read`, `file_text_close`, `file_exists`, `directory_exists`, `directory_create`, `file_delete` | ✅ Existen |
| `move_and_collide`, `place_meeting`, `instance_place` | ✅ Existen |
| `show_debug_overlay`, `get_timer`, `fps_real`, `delta_time`, `room_speed` | ✅ Existen |

---

## Fuentes

- Manual oficial (LTS) — <https://manual.gamemaker.io/lts/en/>
- Manual oficial (Monthly, el que consulta `gm-cli manual read`) — <https://manual.gamemaker.io/monthly/en/>
- Data Types (Handles, int64, literales) — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Data_Types.htm>
- Time Sources — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Time_Sources/Time_Sources.htm>
- Structs — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Variable_Functions.htm>
- Garbage Collection — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Garbage_Collection/Garbage_Collection.htm>

---

*Glosario GML · GameMaker LTS 2026 · Agosto de 2026 · UTF-8*
