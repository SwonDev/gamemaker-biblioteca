# 29 · 3D en GameMaker

> GameMaker es un motor 2D con una **tubería 3D de bajo nivel** debajo: matrices, vertex
> buffers, z-buffer, culling y shaders. No hay editor de escena 3D, ni importador de modelos,
> ni sistema de colisiones 3D. Todo eso lo pones tú o lo trae una librería.
>
> Este documento es el **flujo completo**: decidir si el 3D te conviene, plantar una cámara,
> construir geometría, texturizarla, iluminarla, mezclarla con 2D, moverla y chocar con ella.
> **No repite las fichas de funciones**: la referencia de vertex buffers está en
> [08 · 07](../08%20-%20Referencia%20GML%20completa/07%20-%20Vertex%20buffers%20y%20formatos.md) y la de
> matrices en [08 · 11](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores,%20matrices%20y%20ángulos.md).

---

## La decisión que va antes del código

**Las funciones `d3d_*` ya no existen.** Se retiraron con el paso a GMS2 y en el runtime
`2026.0.0.23` no queda ninguna: `python3 "_indice/buscar.py" --listar d3d_` devuelve **0
símbolos**. Lo que hay hoy son cinco piezas sueltas —`matrix_*`, `vertex_*`, `camera_set_*_mat`,
`gpu_set_*` y los shaders— que **tú** tienes que coser. No hay «modo 3D» que activar.

Eso cambia la pregunta: no es «¿puedo hacer 3D?» —sí puedes—, sino «¿cuánto trabajo estoy
dispuesto a poner en la parte que en Godot o Unity viene hecha?».

```
¿Qué papel tiene el 3D en tu juego?
├─ TRUCO VISUAL sobre un juego 2D (sprite stacking, parallax, sombras falsas, isométrico)
│  → NO uses la tubería 3D. Sigue en 2D: es más barato y se ve igual.
├─ ESCENARIO 3D con jugabilidad 2D (mazmorra por rejilla, Paper Mario, Mario Kart)
│  → 3D razonable. Geometría sencilla, colisión en un mapa 2D. Este documento.
├─ JUEGO 3D low-poly estilo PS1, o un minijuego 3D dentro de un juego 2D
│  → Se puede, y hay quien lo ha hecho, pero vas a escribir tu propio motor.
│     Presupuesta semanas, no tardes. Mira BBMOD antes de empezar de cero.
└─ JUEGO 3D MODERNO (PBR, sombras dinámicas, animación esquelética, físicas)
   → GameMaker no es la herramienta. Godot o Unity te dan eso el primer día.
      Decirlo no es traición: es respetar tu tiempo.
```

### Qué es razonable y qué no

| Ambición | ¿Razonable en GameMaker LTS 2026? | Por qué |
|---|---|---|
| Sprite stacking / *fake 3D* con sprites escalados | ✅ Sí, y ni siquiera necesita la tubería 3D | Todo son `draw_sprite_ext` en 2D. Ver [`Stack3D`](https://github.com/dev-dwarf/Stack3D) |
| Mazmorra por rejilla (*Eye of the Beholder*, *Etrian Odyssey*) | ✅ Sí | Geometría trivial: cubos y quads. Ver [`Bronze-Box`](https://github.com/cicadian/Bronze-Box) |
| 2.5D estilo *Doom*: nivel 3D + enemigos como carteles | ✅ Sí | Es el caso al que mejor se adapta el motor |
| Nivel low-poly estilo PS1 con textura | ✅ Sí, con trabajo | Necesitas un cargador de modelos y colisión propia |
| Terreno con mapa de alturas y personaje que anda por él | ✅ Sí | §8 de este documento |
| Animación esquelética (*skinning*), sombras proyectadas, PBR | 🟡 Solo con librería o shaders propios | BBMOD trae skinning y PBR; del *shadow mapping* hay 3 tutoriales de DragoniteSpam (48, 49, 82) |
| Físicas 3D rígidas (cajas que se apilan, ragdolls) | ❌ No hay nada nativo | Box2D es **2D**. Ver [22 · Físicas con Box2D](./22%20-%20Físicas%20con%20Box2D.md) |
| Un mundo abierto 3D | ❌ | No hay *streaming*, ni LOD, ni octrees, ni cull jerárquico |

> 💡 **La alternativa honesta:** si tu juego es 3D de verdad, Godot 4 y Unity 6 te dan editor de
> escena, importador glTF, NavMesh y luces con sombras sin escribir una línea. GameMaker gana
> cuando el 3D es **una capa sobre un juego 2D** y ya sabes GML: ahí cambiar de motor cuesta más
> que aprender vertex buffers.

### El estado en GMRT ⚠️

GMRT —el runtime nuevo— trae una API 3D propia, **GM3D**: matemática 3D con cuaterniones, carga
de modelos **glTF** con skinning y animación, y un grafo de escena con cámaras, luces y
volúmenes de entorno. Es la dirección oficial del 3D en GameMaker. Pero hoy, **con LTS 2026.0 no
la tienes**: ninguno de sus símbolos existe en el `GmlSpec.xml` del runtime `2026.0.0.23`
(`buscar.py --listar GM3D` → **0 símbolos**). El propio documento de GMRT la describe como
«funciones GM3D **(incompletas, pidiendo feedback)**», avisa de que **no hay ayuda de sintaxis
en la IDE**, y lista `vertex_buffer_exists()` y `vertex_format_exists()` como incompatibles en
0.21.0 —dos funciones que este documento usa—.

⚠️ **Conclusión práctica:** todo lo que sigue está escrito para la tubería clásica de LTS 2026,
que funciona hoy y en producción. GM3D es lo que vendrá; síguelo, no lo uses aún para nada con
fecha de entrega. Detalle en
[02 · 03 — GMRT, el nuevo runtime](../02%20-%20Novedades%202026/03%20-%20GMRT%20-%20El%20nuevo%20runtime.md).

---

> 🎨 **¿Y los modelos?** Hasta hoy esta receta explicaba cómo cargar un `.obj` y no decía de
> dónde sacarlo. Cuatro fuentes **CC0** —Kenney 3D, Quaternius, Kay Lousberg y ambientCG para
> texturas— más un buscador con licencia mezclada, en
> [`07 · 09 §7 bis`](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md).
> Ahí está también qué formato entra directo (`.obj`) y cuál necesita pasar por `BBMOD`
> (glTF y FBX).

## 1 · Los ejes, la cámara y el interruptor de profundidad

### El sistema de coordenadas: Z arriba, Y al sur

GameMaker no impone un sistema 3D —las matrices se lo tragan todo—, pero **la comunidad
convergió en uno** y conviene no pelearse con él: **X al este, Y al sur** (como en 2D, donde
`y` crece hacia abajo) y **Z arriba**, con `z = 0` en el suelo. De ahí salen las dos cosas que
verás en todo el código: el vector «arriba» de la cámara es `(0, 0, 1)`, y la trigonometría del
plano **resta** en Y: un punto a distancia `_dist` y ángulo `_giro` alrededor de `(_cx, _cy)`
está en `_cx + _dist * dcos(_giro)`, `_cy - _dist * dsin(_giro)`.

### La cámara 3D, completa

```gml
/// obj_camara3d · Create — montar la cámara y encender la profundidad
#macro FOV_VERTICAL   60      // grados. 60-75 en primera persona, 40-55 en tercera
#macro PLANO_CERCANO   1
#macro PLANO_LEJANO 32000
gpu_set_ztestenable(true);    // descarta lo que queda detrás de otra cosa (viene APAGADO)
gpu_set_zwriteenable(true);   // escribe la profundidad de cada píxel dibujado
camara = camera_create();
view_enabled = true;
view_visible[0] = true;
view_camera[0] = camara;
giro = 0;         // yaw, en grados
elevacion = 20;   // pitch, en grados
distancia = 320;
```
```gml
/// obj_camara3d · Draw Begin — plantar la proyección ANTES de dibujar nada
draw_clear(c_black);
var _mira_x = obj_jugador.x;
var _mira_y = obj_jugador.y;
var _mira_z = obj_jugador.z + 48;      // mira al pecho, no a los pies
var _ojo_x = _mira_x + distancia * dcos(giro) * dcos(elevacion);
var _ojo_y = _mira_y - distancia * dsin(giro) * dcos(elevacion);
var _ojo_z = _mira_z - distancia * dsin(elevacion);
// VISTA: dónde está la cámara y a dónde mira. Arriba = (0,0,1)
var _vista = matrix_build_lookat(_ojo_x, _ojo_y, _ojo_z, _mira_x, _mira_y, _mira_z, 0, 0, 1);
// PROYECCIÓN: FOV en GRADOS, y negativo junto con el aspecto (ver el aviso de abajo)
var _proyeccion = matrix_build_projection_perspective_fov(
    -FOV_VERTICAL, -window_get_width() / window_get_height(), PLANO_CERCANO, PLANO_LEJANO);
camera_set_view_mat(camara, _vista);
camera_set_proj_mat(camara, _proyeccion);
camera_apply(camara);                   // ← sin esto no pasa NADA
/// obj_camara3d · Clean Up  →  camera_destroy(camara);
```

> 🔺 **El FOV y el aspecto van los DOS en negativo.** Ese par de signos corrige el eje Y de
> GameMaker, que apunta hacia abajo. Negar solo el FOV invierte también la X y la escena sale
> girada 180°; no negar nada la deja **reflejada verticalmente**. Es lo que hace el script
> oficial de compatibilidad `@d3d_set_projection_ext` —`(-fov, -aspect, znear, zfar)`— y lo que
> usan los 90 tutoriales de la serie 3D de DragoniteSpam (el nº 13 se llama literalmente *Fixing
> The Up Direction*), `DDDEditorGMS2` y `Macaw`.
>
> ⚠️ La ficha de [08 · 11](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores,%20matrices%20y%20ángulos.md)
> dice «FOV negativo con aspecto **positivo**»; con el convenio Z-arriba de aquí, lo verificado
> contra el código real es **los dos negativos**. Si sale espejada en horizontal, prueba la otra
> combinación: depende del vector «arriba» que hayas elegido.

> 💡 **`camera_apply()` es el interruptor.** Puedes rellenar las matrices perfectamente y no ver
> nada porque nunca las aplicaste, y hay que llamarlo **antes** de dibujar, en el mismo evento.

### El z-buffer, en dos funciones

`gpu_set_ztestenable(true)` **comprueba** la profundidad —no dibuja un píxel si ya hay algo más
cerca— y va encendido todo el pase 3D; **viene apagado por defecto**, y sin él las caras traseras
de un cubo se dibujan encima de las delanteras si les toca ir después. `gpu_set_zwriteenable`
**escribe** la profundidad de lo que dibuja: encendido para lo opaco, **apagado** para lo
transparente y para el cielo (§6). `gpu_set_zfunc(cmpfunc_lessequal)` cambia el criterio de
comparación y casi nunca hace falta: sirve para trucos (rayos X, contornos).

### Culling: no dibujar lo que no se ve

`gpu_set_cullmode()` toma `cull_noculling` (las dos caras, por defecto), `cull_clockwise`
(descarta los triángulos en sentido horario) o `cull_counterclockwise` (descarta los
antihorarios). El manual define la cara **frontal** como aquella cuyos vértices se ven **en sentido
antihorario**, pero con la Y invertida de la proyección el sentido aparente se da la vuelta: el
código real (el demo de `DS-3DCollisions`) usa `cull_counterclockwise`.

> 💡 **La regla de depuración:** empieza con `cull_noculling`; cuando la escena se vea bien,
> prueba una de las dos constantes y si desaparece lo que debía verse, es la otra. En geometría
> cerrada el culling ahorra aproximadamente la mitad del tiempo de dibujo.

### Niebla: profundidad barata y truco para el plano lejano

```gml
gpu_set_fog(true, c_black, 600, 2400);   // enable, color, distancia de inicio, de fin
// ...dibujar la escena...
gpu_set_fog(false, c_black, 0, 1);
```

La niebla difumina lo lejano y **esconde el corte del plano lejano**: si acaba antes de
`PLANO_LEJANO`, nadie ve aparecer la geometría de golpe. El truco más viejo del 3D y el que más
rinde. 🔺 **Con un shader propio no se aplica sola**: hay que leer los uniforms `gm_FogStart`,
`gm_RcpFogRange`, `gm_FogColour` y `gm_PS_FogEnabled`, documentados en
[08 · 06 — Shaders](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md).

### La matriz de mundo: colocar una malla en la escena

Un vertex buffer guarda la geometría **en coordenadas locales**, centrada en su propio origen;
para ponerla en el mundo se cambia `matrix_world` antes de enviarla:

```gml
// Colocar, girar y escalar una malla
matrix_set(matrix_world, matrix_build(x, y, z,          // posición
                                      0, 0, giro,       // rotación X, Y, Z (grados)
                                      1, 1, 1));        // escala
vertex_submit(vb_cofre, pr_trianglelist, sprite_get_texture(spr_madera, 0));
matrix_set(matrix_world, matrix_build_identity());      // ← RESETEAR SIEMPRE
```

> 🔺 **Si no reseteas la matriz de mundo, todo lo que dibujes después hereda esa
> transformación** —incluidos los sprites del HUD, que saldrán girados y a 3.000 píxeles—.
> `matrix_build_identity()` después de cada malla, sin excepción. El orden de rotación de
> `matrix_build` es **YXZ**, detallado en
> [08 · 11](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores,%20matrices%20y%20ángulos.md).

---

## 2 · Geometría: del formato de vértice al cubo

### El formato y dos ayudantes para no repetirte

```gml
/// obj_camara3d · Create (antes de construir nada)
vertex_format_begin();
vertex_format_add_position_3d();   // x, y, z      → in_Position
vertex_format_add_normal();        // nx, ny, nz   → in_Normal (necesario para iluminar)
vertex_format_add_texcoord();      // u, v         → in_TextureCoord
vertex_format_add_colour();        // color+alfa   → in_Colour
formato = vertex_format_end();
```

> 🔺 **El orden en que declaras los atributos es el orden en que hay que escribirlos**, vértice
> a vértice, sin saltarse ninguno: es la fuente número uno de «no se ve nada» y de vértices
> corruptos. Ficha de cada función en
> [08 · 07](../08%20-%20Referencia%20GML%20completa/07%20-%20Vertex%20buffers%20y%20formatos.md).

```gml
/// scr_malla — escribe un vértice completo con el formato de arriba
function malla_vertice(_vb, _px, _py, _pz, _nx, _ny, _nz, _u, _v, _color, _alfa) {
    vertex_position_3d(_vb, _px, _py, _pz);
    vertex_normal(_vb, _nx, _ny, _nz);
    vertex_texcoord(_vb, _u, _v);
    vertex_colour(_vb, _color, _alfa);
}
/// Escribe un cuadrilátero como DOS triángulos (1-2-3 y 1-3-4)
function malla_cara(_vb, _x1,_y1,_z1, _x2,_y2,_z2, _x3,_y3,_z3, _x4,_y4,_z4,
                    _nx,_ny,_nz, _color) {
    malla_vertice(_vb, _x1,_y1,_z1, _nx,_ny,_nz, 0, 0, _color, 1);
    malla_vertice(_vb, _x2,_y2,_z2, _nx,_ny,_nz, 1, 0, _color, 1);
    malla_vertice(_vb, _x3,_y3,_z3, _nx,_ny,_nz, 1, 1, _color, 1);
    malla_vertice(_vb, _x1,_y1,_z1, _nx,_ny,_nz, 0, 0, _color, 1);
    malla_vertice(_vb, _x3,_y3,_z3, _nx,_ny,_nz, 1, 1, _color, 1);
    malla_vertice(_vb, _x4,_y4,_z4, _nx,_ny,_nz, 0, 1, _color, 1);
}
```

### Un cubo entero

```gml
/// Construye un cubo centrado en el origen, de lado 2*_s. Devuelve el vertex buffer.
function malla_cubo(_formato, _s = 32, _color = c_white) {
    var _vb = vertex_create_buffer();
    vertex_begin(_vb, _formato);
    // Cara superior (+Z)
    malla_cara(_vb, -_s,-_s, _s,  _s,-_s, _s,  _s, _s, _s, -_s, _s, _s,   0, 0, 1, _color);
    // Cara inferior (-Z)
    malla_cara(_vb, -_s, _s,-_s,  _s, _s,-_s,  _s,-_s,-_s, -_s,-_s,-_s,   0, 0,-1, _color);
    // Cara norte (-Y)
    malla_cara(_vb, -_s,-_s,-_s,  _s,-_s,-_s,  _s,-_s, _s, -_s,-_s, _s,   0,-1, 0, _color);
    // Cara sur (+Y)
    malla_cara(_vb,  _s, _s,-_s, -_s, _s,-_s, -_s, _s, _s,  _s, _s, _s,   0, 1, 0, _color);
    // Cara este (+X)
    malla_cara(_vb,  _s,-_s,-_s,  _s, _s,-_s,  _s, _s, _s,  _s,-_s, _s,   1, 0, 0, _color);
    // Cara oeste (-X)
    malla_cara(_vb, -_s, _s,-_s, -_s,-_s,-_s, -_s,-_s, _s, -_s, _s, _s,  -1, 0, 0, _color);
    vertex_end(_vb);
    vertex_freeze(_vb);      // geometría estática: congélala, se dibuja mucho más rápido
    return _vb;
}
```

Son **36 vértices**: 6 caras × 2 triángulos × 3. `pr_trianglelist` no comparte vértices entre
triángulos, y aquí es lo correcto: cada cara tiene su propia normal.

### Un suelo texturizado, con la textura repetida

```gml
/// Un plano de _celdas × _celdas en el suelo (z = 0). Las UV van de 0 a _celdas,
/// no de 0 a 1: eso es lo que repite la textura (necesita gpu_set_texrepeat, §3)
function malla_suelo(_formato, _celdas = 32, _tam = 128) {
    var _vb = vertex_create_buffer();
    vertex_begin(_vb, _formato);
    for (var _i = 0; _i < _celdas; _i++) {
        for (var _j = 0; _j < _celdas; _j++) {
            var _x1 = _i * _tam, _x2 = _x1 + _tam;
            var _y1 = _j * _tam, _y2 = _y1 + _tam;
            malla_vertice(_vb, _x1,_y1,0, 0,0,1, _i,   _j,   c_white, 1);
            malla_vertice(_vb, _x2,_y1,0, 0,0,1, _i+1, _j,   c_white, 1);
            malla_vertice(_vb, _x2,_y2,0, 0,0,1, _i+1, _j+1, c_white, 1);
            malla_vertice(_vb, _x1,_y1,0, 0,0,1, _i,   _j,   c_white, 1);
            malla_vertice(_vb, _x2,_y2,0, 0,0,1, _i+1, _j+1, c_white, 1);
            malla_vertice(_vb, _x1,_y2,0, 0,0,1, _i,   _j+1, c_white, 1);
        }
    }
    vertex_end(_vb);
    vertex_freeze(_vb);
    return _vb;
}
```

> 🔺 **No hay `pr_trianglefan` fiable.** El manual dice que los abanicos «no se permiten, ya que
> la mayoría del hardware móvil no acepta ese tipo de primitiva»: la constante existe, pero donde
> no se soporta se convierte a `pr_trianglelist` por dentro. Usa lista o tira, y olvídalo.

---

## 3 · Texturas: UV, repetición y mipmaps

La textura de un vertex buffer se pasa en `vertex_submit` y sale de un sprite:

```gml
vertex_submit(vb_cubo, pr_trianglelist, -1);    // -1 = sin textura, solo el color del vértice
gpu_set_texrepeat(true);                        // UV mayores que 1 repiten la textura
vertex_submit(vb_suelo, pr_trianglelist, sprite_get_texture(spr_hierba, 0));
gpu_set_texrepeat(false);
```

> 🔺 **La repetición exige que el sprite esté en su propia página de textura.** El manual lo dice
> sin rodeos: «tendrá que estar marcado como **Separate Texture Page** en el Editor de Sprites».
> Si no lo marcas, al repetir verás trozos de los sprites vecinos: es el bug del «suelo con la
> cara de un enemigo repetida por todas partes». Y ojo: **dibujar un sprite normal resetea
> `texrepeat` a `false`**, así que si intercalas HUD y geometría, reactívalo.
>
> **Por CLI/MCP no hay ninguna casilla `SeparateTexturePage` que marcar.** `resource info
> expr=<sprite> KEYS` no lista ese campo (solo `DynamicTexturePage`, que es otra cosa —ver
> [12 · 09](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md),
> y `textureGroupId`): un agente que busque esa propiedad concreta no la va a encontrar. La vía
> real, con el mismo efecto práctico, es meter el sprite en un **grupo de textura dedicado**, que
> se empaqueta en sus propias páginas y no comparte página con nada del grupo `Default`:
> ```bash
> gm-cli resourcetool eval "texturegroup create name=tg_piso"
> gm-cli resourcetool eval "texturegroup set group=tg_piso resources=spr_piso"
> ```
> Verificado en vivo el 8 de septiembre de 2026: `texturegroup create`/`texturegroup set` existen
> de verdad (`resourcetool eval "help texturegroup"` los lista), compilan limpio y el sprite deja
> de compartir página con sus vecinos.

### Filtrado y mipmaps

```gml
gpu_set_tex_filter(true);              // interpolación lineal: suaviza al acercarse
gpu_set_tex_mip_enable(mip_on);        // mip_off | mip_on | mip_markedonly (por defecto)
gpu_set_tex_mip_filter(tf_anisotropic);
gpu_set_tex_max_aniso(4);
```

Los **mipmaps** son versiones reducidas de la textura que la GPU usa cuando la superficie está
lejos. Sin ellos un suelo en perspectiva **hierve**: los píxeles del horizonte parpadean al mover
la cámara, y es el defecto más visible de una escena 3D casera. `mip_markedonly` (el valor por
defecto) los activa solo en los grupos marcados en el **Texture Group Manager** del IDE, que es
lo recomendable; `tf_anisotropic` con `gpu_set_tex_max_aniso(4)` o `(8)` arregla el emborronado
del suelo en ángulo rasante por muy poco coste.

> 🔺 **Las fuentes no admiten mipmapping:** con `mip_on` global y fuentes en un grupo de textura,
> los glifos salen corruptos. Ponlas en su propio grupo sin mipmaps. Detalle en
> [08 · 08 — Texturas y grupos de texturas](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md).

---

## 4 · Cargar un modelo `.obj`

El Wavefront `.obj` es texto plano y lo exporta cualquier herramienta (Blender, MagicaVoxel,
Asset Forge). Un parser mínimo cabe en 60 líneas de GML:

```gml
/// scr_modelo_obj
/// Carga un .obj TRIANGULADO en un vertex buffer.
/// @param {String} _ruta      Ruta del fichero (normalmente working_directory + "algo.obj")
/// @param {Any}    _formato   El formato de vértice de §2
/// @param {Bool}   _blender   true = intercambiar Y y Z (exportación por defecto de Blender)
function modelo_cargar_obj(_ruta, _formato, _blender = true, _color = c_white) {
    if (!file_exists(_ruta)) {
        show_debug_message($"OBJ no encontrado: {_ruta}");
        return -1;
    }

    var _pos = [];    // posiciones "v"
    var _uv  = [];    // coordenadas de textura "vt"
    var _nor = [];    // normales "vn"

    var _vb = vertex_create_buffer();
    vertex_begin(_vb, _formato);

    var _fichero = file_text_open_read(_ruta);
    while (!file_text_eof(_fichero)) {
        var _linea = string_trim(file_text_readln(_fichero));
        if (_linea == "" || string_char_at(_linea, 1) == "#") continue;

        var _campos = string_split(_linea, " ", true);   // true = descartar vacíos
        switch (_campos[0]) {
            case "v":
                array_push(_pos, [real(_campos[1]), real(_campos[2]), real(_campos[3])]);
                break;

            case "vt":
                // OBJ tiene el origen UV abajo-izquierda; GameMaker, arriba-izquierda
                array_push(_uv, [real(_campos[1]), 1 - real(_campos[2])]);
                break;

            case "vn":
                array_push(_nor, [real(_campos[1]), real(_campos[2]), real(_campos[3])]);
                break;

            case "f":
                // "f v/vt/vn v/vt/vn v/vt/vn" — los índices empiezan en 1, no en 0
                for (var _k = 1; _k <= 3; _k++) {
                    var _trozos = string_split(_campos[_k], "/", false);

                    var _p = _pos[real(_trozos[0]) - 1];
                    var _px = _p[0], _py = _p[1], _pz = _p[2];

                    var _u = 0, _v = 0;
                    if (array_length(_trozos) > 1 && _trozos[1] != "") {
                        var _t = _uv[real(_trozos[1]) - 1];
                        _u = _t[0]; _v = _t[1];
                    }

                    var _nx = 0, _ny = 0, _nz = 1;
                    if (array_length(_trozos) > 2 && _trozos[2] != "") {
                        var _n = _nor[real(_trozos[2]) - 1];
                        _nx = _n[0]; _ny = _n[1]; _nz = _n[2];
                    }

                    if (_blender) {                  // Blender exporta con Y arriba
                        var _tmp = _py; _py = _pz; _pz = _tmp;
                        _tmp = _ny;    _ny = _nz;   _nz = _tmp;
                    }

                    malla_vertice(_vb, _px, _py, _pz, _nx, _ny, _nz, _u, _v, _color, 1);
                }
                break;
        }
    }

    file_text_close(_fichero);
    vertex_end(_vb);
    vertex_freeze(_vb);
    return _vb;
}
```

> 🔺 **Tres trampas del `.obj`:** los índices **empiezan en 1** (de ahí el `- 1`); las caras
> pueden tener más de 3 vértices y este parser solo lee los tres primeros (exporta
> **triangulado**); y la **V de las UV va del revés** (por eso `1 - real(...)` en `"vt"`: si la
> textura sale invertida verticalmente, es esto).
>
> 💡 **Parsear un `.obj` grande tarda.** Hazlo en el arranque, no al abrir una puerta. Si el
> modelo no cambia, guarda el vertex buffer ya montado con `buffer_save` y recárgalo con
> `buffer_load` + `vertex_create_buffer_from_buffer`: es órdenes de magnitud más rápido. Para
> `.mtl` y modelos complejos usa [`dotobj`](https://github.com/JujuAdams/dotobj) (MIT, 47 ★).

---

## 5 · Luz: la tubería fija frente al shader

### La iluminación integrada (existe, y es limitada)

```gml
/// Create
draw_set_lighting(true);                                     // encender la iluminación
draw_light_define_ambient(make_color_rgb(60, 60, 80));       // luz de relleno azulada
// Luz direccional (el sol). El vector es unitario: cada componente entre -1 y 1
draw_light_define_direction(0, -0.4, -0.5, -0.75, c_white);
draw_light_enable(0, true);
// Luz puntual (una antorcha): índice, posición, alcance, color
draw_light_define_point(1, 512, 512, 96, 400, c_orange);
draw_light_enable(1, true);
```

Límites reales: el formato de vértice **tiene que incluir** `vertex_format_add_normal()` (sin
normales, todo sale plano); solo hay **8 luces de hardware activas a la vez** (definir, puedes
más); se calcula **por vértice, no por píxel**, así que en un cubo de 8 vértices la luz se ve a
bandas; y **con un shader propio se ignora**, salvo que leas tú los uniforms
`gm_LightingEnabled`, `gm_Lights_Direction[]`, `gm_Lights_PosRange[]`, `gm_Lights_Colour[]` y
`gm_AmbientColour`. Sirve para un prototipo, una mazmorra por rejilla o cuando no quieres tocar
GLSL; para cualquier cosa con ambición, shader.

### Iluminación difusa por shader (lo que vas a usar)

```glsl
// ══════ shd_luz_difusa.vsh — lleva la normal al espacio de mundo ══════
attribute vec3 in_Position;
attribute vec3 in_Normal;
attribute vec4 in_Colour;
attribute vec2 in_TextureCoord;
varying vec2 v_vTexcoord;
varying vec4 v_vColour;
varying vec3 v_vNormalMundo;
void main() {
    vec4 object_space_pos = vec4(in_Position.x, in_Position.y, in_Position.z, 1.0);
    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * object_space_pos;
    // La normal se transforma con w = 0: rota, pero no se traslada
    v_vNormalMundo = normalize((gm_Matrices[MATRIX_WORLD] * vec4(in_Normal, 0.0)).xyz);
    v_vColour   = in_Colour;
    v_vTexcoord = in_TextureCoord;
}
```
```glsl
// ══════ shd_luz_difusa.fsh — Lambert por píxel ══════
varying vec2 v_vTexcoord;
varying vec4 v_vColour;
varying vec3 v_vNormalMundo;
uniform vec3 u_vHaciaLaLuz;    // vector unitario que apunta HACIA la luz
uniform vec3 u_vColorLuz;
uniform vec3 u_vColorAmbiente;
void main() {
    vec4 base = v_vColour * texture2D(gm_BaseTexture, v_vTexcoord);
    float difusa = max(dot(normalize(v_vNormalMundo), normalize(u_vHaciaLaLuz)), 0.0);
    vec3 luz = min(u_vColorAmbiente + u_vColorLuz * difusa, vec3(1.0));
    gl_FragColor = vec4(base.rgb * luz, base.a);
}
```

**Cómo se alimenta desde GML**, cacheando los *handles* (buscarlos cada frame cuesta):

```gml
/// obj_camara3d · Create
u_hacia_luz = shader_get_uniform(shd_luz_difusa, "u_vHaciaLaLuz");
u_color_luz = shader_get_uniform(shd_luz_difusa, "u_vColorLuz");
u_ambiente  = shader_get_uniform(shd_luz_difusa, "u_vColorAmbiente");
/// obj_camara3d · Draw — dentro del pase 3D
shader_set(shd_luz_difusa);
shader_set_uniform_f(u_hacia_luz, 0.40, 0.35, 0.85);   // el sol, arriba y al noreste
shader_set_uniform_f(u_color_luz, 1.0, 0.95, 0.85);    // luz cálida
shader_set_uniform_f(u_ambiente,  0.25, 0.27, 0.35);   // relleno frío en la sombra
vertex_submit(vb_suelo, pr_trianglelist, sprite_get_texture(spr_hierba, 0));
vertex_submit(vb_cubo,  pr_trianglelist, -1);
shader_reset();
```

> 💡 **Luz cálida + ambiente frío** es el truco de dirección de arte que separa una escena
> «apagada» de una que se ve bien, y no cuesta nada. Anatomía completa de un shader, uniforms
> integrados e índices de matriz en
> [08 · 06 — Shaders](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md).

---

## 6 · Mezclar 2D y 3D

Aquí es donde GameMaker gana: **el mismo motor dibuja una escena 3D y un HUD 2D sin cambiar de
contexto**. La clave es el orden y el estado activo en cada momento.

```
Draw Begin  →  limpiar, montar la cámara 3D (camera_apply)
Draw        →  geometría OPACA (ztest ON, zwrite ON)
Draw End    →  geometría TRANSPARENTE y carteles (ztest ON, zwrite OFF), y apagar el 3D
Draw GUI    →  HUD, menús, texto (ya en 2D, sin z-buffer)
```

### Carteles (*billboards*): un sprite que siempre mira a la cámara

```gml
/// scr_cartel — matriz de mundo de un sprite que siempre encara a la cámara.
/// _giro sale de la CÁMARA, no del cartel: así todos son coplanares y no se atraviesan.
function cartel_matriz(_px, _py, _pz, _giro) {
    // 90° en X pone el sprite «de pie»; el giro en Z lo encara a la cámara
    return matrix_build(_px, _py, _pz, 90, 0, _giro, 1, 1, 1);
}
```
```gml
/// obj_camara3d · Draw Begin — calcular el giro una vez por frame
giro_cartel = point_direction(_ojo_x, _ojo_y, _mira_x, _mira_y) - 90;
```
```gml
/// obj_enemigo · Draw End — el enemigo es un sprite en un mundo 3D
gpu_set_zwriteenable(false);          // transparencias: comparar profundidad, no escribirla
matrix_set(matrix_world, cartel_matriz(x, y, z, obj_camara3d.giro_cartel));
draw_sprite_ext(spr_enemigo, image_index, 0, 0, 1, 1, 0, c_white, 1);
matrix_set(matrix_world, matrix_build_identity());
gpu_set_zwriteenable(true);
```

> 💡 **El origen del sprite va abajo-centro:** así `z` es la altura del suelo bajo sus pies y no
> hay que compensar media altura en cada cuenta.

### El problema de la transparencia

Un píxel semitransparente que **escribe** en el z-buffer tapa lo que hay detrás aunque se vea a
través de él: la hierba con alfa sale como recortes negros y el cristal borra lo que hay al otro
lado. Hay dos soluciones, y se eligen por el tipo de transparencia:

| Tipo | Solución | Código |
|---|---|---|
| **Recorte** (hierba, vallas, hojas: o se ve o no se ve) | Alpha test: descarta el píxel antes del z-buffer | `gpu_set_alphatestenable(true); gpu_set_alphatestref(128);` |
| **Semitransparente real** (cristal, humo, fuego) | Dibujarlo el último, de lejos a cerca, sin escribir profundidad | `gpu_set_zwriteenable(false);` |

```gml
/// Vegetación con recorte: puede dibujarse en cualquier orden, sin bordes negros
gpu_set_alphatestenable(true);
gpu_set_alphatestref(128);              // alfa < 0.5 → el píxel no existe
vertex_submit(vb_hierba, pr_trianglelist, sprite_get_texture(spr_hierba_alfa, 0));
gpu_set_alphatestenable(false);
```

> 🔺 **El alpha test penaliza el rendimiento en iOS y Android** (lo avisa el manual): rompe
> optimizaciones del hardware móvil. En escritorio no se nota; en móvil, mídelo.

### El cielo (*skybox*)

```gml
/// PRIMERO de todo, centrado en la cámara y sin escribir profundidad:
/// así todo lo demás lo tapa, esté a la distancia que esté
gpu_set_zwriteenable(false);
matrix_set(matrix_world, matrix_build(_ojo_x, _ojo_y, _ojo_z, 0, 0, 0, 1, 1, 1));
vertex_submit(vb_cielo, pr_trianglelist, sprite_get_texture(spr_cielo, 0));
matrix_set(matrix_world, matrix_build_identity());
gpu_set_zwriteenable(true);
```

### El HUD y el fin del pase 3D

```gml
/// obj_camara3d · Draw End — cerrar el 3D antes de que llegue la GUI
shader_reset();
gpu_set_ztestenable(false);
gpu_set_zwriteenable(false);
gpu_set_cullmode(cull_noculling);
gpu_set_fog(false, c_black, 0, 1);
matrix_set(matrix_world, matrix_build_identity());
```

A partir de ahí, **Draw GUI** es 2D puro y sin sorpresas.

> 🔺 **Si no apagas el z-test antes de la GUI, el HUD puede desaparecer** o parpadear: el depth
> buffer todavía tiene la geometría del frame y algunos píxeles del HUD no pasan la prueba.
> Apagar los cuatro interruptores al cerrar el pase 3D es lo correcto, y lo que hace el demo de
> `DS-3DCollisions`.

> 🔺 **Entre objetos DISTINTOS, quién dibuja antes dentro de `Draw End` lo decide `depth`, no el
> orden "lógico" del código.** El bloque de arriba que cierra el pase 3D y los carteles de otros
> objetos (§ «Carteles») compiten por el mismo evento `Draw End`, y GameMaker no los ejecuta en
> el orden en que "deberían" ir — los ejecuta por `depth` (heredado del layer en el que se creó
> cada instancia), de mayor a menor, exactamente igual que en 2D. Si la instancia que cierra el
> pase 3D tiene un `depth` más alto que la de un cartel, el cierre se ejecuta **antes** que el
> cartel: el cartel se dibuja sin z-test y sin iluminación, sin ningún error — un bug silencioso
> de dibujado, no un *crash*. Y el `depth` que hereda cada instancia depende de en qué layer la
> creó el editor de rooms o `ROOM INSTANCE CREATE`, un detalle fácil de dejar al azar en un
> proyecto con varios objetos 3D. **La corrección es fijar `depth` explícitamente, no confiar en
> el orden de creación de la sala**: pon el objeto que cierra el pase 3D (la cámara, normalmente)
> al `depth` más bajo posible (`depth = -1000` en su `Create`, por ejemplo) para que su
> `Draw End` sea **siempre** lo último, sea cual sea el orden en que se crearon el resto de
> instancias.

### 2.5D: cuando el 3D es solo el escenario

- **Doom / Wolfenstein**: nivel 3D real (paredes y suelo en vertex buffers) + enemigos y objetos
  como carteles, con la colisión **en 2D** sobre la planta del nivel.
- **Paper Mario**: escenario 3D + personajes como quads planos con animación de sprite; el giro
  del cartel se congela para que se vean «de papel».
- **Mario Kart / F-Zero**: pista en 3D, karts como carteles o mallas simples. Ver
  [12 · Carreras y vehículos](./12%20-%20Carreras%20y%20vehículos.md).
- **Sprite stacking**: **sin tubería 3D**, capas de sprite apiladas con `draw_sprite_ext` y un
  desplazamiento. Ver [`Stack3D`](https://github.com/dev-dwarf/Stack3D).

---

## 7 · Control de cámara

### Primera persona con el ratón bloqueado

```gml
/// obj_jugador · Create
z = 48;  giro = 0;  elevacion = 0;   // z = altura de los ojos
window_mouse_set_locked(true);       // oculta y fija el cursor: el ratón pasa a ser un mando
```
```gml
/// obj_jugador · Step
if (window_mouse_get_locked()) {
    var _sensibilidad = 0.15;
    giro      -= window_mouse_get_delta_x() * _sensibilidad;
    elevacion -= window_mouse_get_delta_y() * _sensibilidad;
    elevacion  = clamp(elevacion, -85, 85);      // no dejar que el cuello se rompa
}
// Movimiento relativo a hacia dónde miras
var _velocidad = 4;
var _avance = keyboard_check(ord("W")) - keyboard_check(ord("S"));
var _lado   = keyboard_check(ord("D")) - keyboard_check(ord("A"));
x += (_avance * dcos(giro) + _lado * dcos(giro - 90)) * _velocidad;
y -= (_avance * dsin(giro) + _lado * dsin(giro - 90)) * _velocidad;
if (keyboard_check_pressed(vk_escape)) window_mouse_set_locked(false);
```

> 🔺 **`window_mouse_set_locked` solo existe en escritorio (Windows, Ubuntu, macOS) y navegador
> (HTML5 y GX.games).** En HTML5 **no puede llamarse en el evento Create** —el navegador exige
> un clic previo sobre el lienzo— y no funciona en Ubuntu con Wayland. Ten siempre alternativa
> con teclado o mando. `window_mouse_get_delta_x()` / `_y()` devuelven el desplazamiento entre
> el paso anterior y el actual, **esté el ratón bloqueado o no**; es la forma correcta, porque
> el viejo truco de recentrar el cursor con `window_mouse_set` cada frame arrastra tirones.

### Cámara orbital (editor, visor de modelos)

```gml
/// obj_camara3d · Step — orbitar arrastrando con el botón derecho, zoom con la rueda
if (mouse_check_button(mb_right)) {
    giro      -= window_mouse_get_delta_x() * 0.3;
    elevacion  = clamp(elevacion + window_mouse_get_delta_y() * 0.3, -89, 89);
}
if (mouse_wheel_up())   distancia = max(64,   distancia * 0.9);
if (mouse_wheel_down()) distancia = min(4096, distancia / 0.9);
```

### Tercera persona con seguimiento suave

```gml
/// obj_camara3d · End Step — el jugador YA se ha movido este frame
// El objetivo de la cámara persigue al jugador con retraso: se siente vivo, no rígido
mira_x = lerp(mira_x, obj_jugador.x, 0.15);
mira_y = lerp(mira_y, obj_jugador.y, 0.15);
mira_z = lerp(mira_z, obj_jugador.z + 48, 0.10);   // más lento en vertical: menos mareo
// El giro sigue al del jugador, pero con más retraso todavía
var _diferencia = angle_difference(obj_jugador.giro, giro);
giro += _diferencia * 0.08;
```

> 💡 **Suavizar la Z menos que la X/Y** quita el mareo al saltar: si la cámara sigue la altura a
> la misma velocidad, el salto se siente como un ascensor. Más en
> [15 · Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md).

---

## 7 bis · Audio en 3D

El sonido posicional en 2D está resuelto en
[13 · 09 §5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md);
esta sección es solo lo que cambia al añadir la tercera dimensión: el oyente ya no está fijo
mirando «hacia abajo», sino que **hereda la orientación de la cámara**, y esa orientación hay que
dársela a mano, cada frame.

### El oyente sigue a la cámara, no al jugador

`audio_listener_position()` y `audio_listener_orientation()` **no se actualizan solas**: si no
las llamas en el mismo sitio donde construyes la cámara (§1), el oyente se queda callado en el
origen, mirando hacia donde estuviera la última vez.

```gml
/// obj_camara3d · Draw Begin — justo después de calcular _ojo_* y _mira_* de §1
audio_listener_position(_ojo_x, _ojo_y, _ojo_z);

// audio_listener_orientation() quiere una DIRECCIÓN (hacia dónde mira), no el punto al que
// mira: hay que restar y normalizar. Arriba = (0,0,1), el mismo convenio Z-arriba de §1.
var _dir_x = _mira_x - _ojo_x;
var _dir_y = _mira_y - _ojo_y;
var _dir_z = _mira_z - _ojo_z;
var _dir_len = sqrt(_dir_x * _dir_x + _dir_y * _dir_y + _dir_z * _dir_z);
if (_dir_len > 0)
{
    audio_listener_orientation(_dir_x / _dir_len, _dir_y / _dir_len, _dir_z / _dir_len, 0, 0, 1);
}
```

> 🔺 **Confundir el punto de mira con la dirección de mira es el error más común aquí.**
> `_mira_x/_y/_z` es DÓNDE está el pecho del jugador (un punto en el espacio, puede valer miles
> de unidades); `audio_listener_orientation` quiere hacia DÓNDE apunta la cámara (un vector,
> normalizado a longitud 1). Pasarle el punto sin restar `_ojo_*` primero orienta el oyente hacia
> un vector gigantesco que el motor de audio no interpreta como cabría esperar.

### Emisores con z real

En 2D el emisor siempre lleva `z = 0` porque no hay altura que representar. En 3D, la `z` real es
la mitad del efecto: un enemigo en la pasarela de arriba debe sonar **por encima**, no al lado.

```gml
// obj_enemigo_volador · Create
em_vuelo = audio_emitter_create();
audio_emitter_falloff(em_vuelo, 200, 4000, 1);   // en unidades de MUNDO — ver el apartado siguiente

// obj_enemigo_volador · Step
audio_emitter_position(em_vuelo, x, y, z);        // la z real del enemigo, no 0

// obj_enemigo_volador · Clean Up
audio_emitter_free(em_vuelo);
```

### Falloff en unidades de mundo, no de píxel

`audio_emitter_falloff(emitter, ref_dist, max_dist, factor)` recibe las mismas unidades que tu
escena, y en 3D esas unidades suelen ser mucho más grandes que en un juego 2D: con el
`PLANO_LEJANO 32000` de §1, copiar un `max_dist` de 400 (razonable en píxeles 2D) apaga el sonido
a un paso de la cámara.

| Escena | `ref_dist` orientativa | `max_dist` orientativa |
|---|---:|---:|
| Interior pequeño (una habitación) | 100-300 | 1500-3000 |
| Exterior abierto | 500-1000 | 8000-16000 |

> ⚠️ El modelo por defecto sigue siendo `audio_falloff_none` (ganancia siempre 1) — la misma
> trampa que en 2D. Sin `audio_falloff_set_model()` llamado a mano
> ([13 · 09 §5.1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/09%20-%20Diseño%20de%20sonido%20y%20mezcla.md)),
> la distancia en 3D tampoco hace nada.

### Por qué un oyente sin orientación no distingue delante de detrás

Si te quedas solo con `audio_listener_position()` y dejas la orientación fija —o la fijas una vez
y no la actualizas cuando gira la cámara—, el oyente **oye la distancia bien pero no la
dirección**: un enemigo detrás de ti y uno delante, a la misma distancia, producen el mismo
paneo. Es el llamado *cono de confusión* de la psicoacústica: el manual no documenta el algoritmo
interno de paneo de GameMaker, pero por cómo se comporta —resuelve izquierda/derecha a partir del
ángulo entre la mirada del oyente y el emisor— es un paneo estéreo convencional, no un motor con
HRTF (audio binaural real) ⚠️ **inferido del comportamiento, no confirmado por el manual**.
Delante y detrás caen en el mismo ángulo relativo si la orientación no gira de verdad con la
cámara. Actualizar `audio_listener_orientation()` cada frame (bloque de arriba) es la condición
**necesaria** para que el jugador distinga «me atacan por detrás»; no es la condición suficiente:
incluso con la orientación correcta, dos sonidos exactamente delante y exactamente detrás pueden
seguir confundiéndose, porque es una limitación del panning estéreo, no un bug del proyecto. Si el
desambiguado delante/detrás es crítico para la jugabilidad (sigilo, terror), añade una señal
**visual** (indicador direccional en pantalla) en vez de depender solo del oído.

> 💡 **Objetos rápidos (naves, coches en 3D):** si además de la posición quieres el Doppler
> —el motor de la nave que sube de tono al acercarse—, es `audio_emitter_velocity()` /
> `audio_listener_velocity()`, ya cubiertos con ejemplo completo en
> [08 · 24 §6](../08%20-%20Referencia%20GML%20completa/24%20-%20Audio%20avanzado%20-%20buffers,%20colas,%20sincronía%20y%20grabación.md).
> No se repite aquí.

---

## 8 · Colisiones en 3D

### La decisión: la mayoría de los «juegos 3D» colisionan en 2D

¿El jugador anda por un suelo con paredes verticales? → **colisión 2D en planta** (`x`, `y`) más
una altura de suelo; es lo que hacía *Doom*. ¿Plataformas a distintas alturas que se solapan en
planta? → al menos una caja 3D. ¿Rampas, techos curvos, geometría arbitraria? → raycast contra
triángulos, o una librería. **La colisión 2D nativa sigue funcionando en un juego 3D**:
`place_meeting`, `instance_place` y los tilemaps operan sobre `x` e `y`, que no dejan de existir
porque hayas añadido una `z`. Es gratis, rápida y probada. Ver
[01 · 08 — Movimiento y colisiones](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md).

### Caja contra caja y esfera contra plano

```gml
/// scr_colision3d
/// ¿Se solapan dos cajas alineadas a los ejes? Se dan por centro + tamaño total.
function cajas_solapan(_ax,_ay,_az, _aw,_ah,_ad, _bx,_by,_bz, _bw,_bh,_bd) {
    return (abs(_ax - _bx) * 2 < (_aw + _bw))
        && (abs(_ay - _by) * 2 < (_ah + _bh))
        && (abs(_az - _bz) * 2 < (_ad + _bd));
}
/// Cuánto hay que empujar la esfera a lo largo de la normal, o 0 si no toca el plano.
/// La normal (_nx,_ny,_nz) tiene que ser UNITARIA.
function esfera_contra_plano(_ex,_ey,_ez, _radio, _px,_py,_pz, _nx,_ny,_nz) {
    var _dist = dot_product_3d(_ex - _px, _ey - _py, _ez - _pz, _nx, _ny, _nz);
    if (_dist >= _radio) return 0;
    return _radio - _dist;
}
```

Si `esfera_contra_plano` devuelve algo mayor que 0, mueve la esfera esa cantidad **a lo largo de
la normal** (`x += _nx * _empuje`…) y quedará apoyada: es la base de «andar por una rampa».

### Rayo contra triángulo: Möller–Trumbore en GML

**El** algoritmo de raycast (Möller y Trumbore, 1997), sin precalcular nada ni almacenar el plano
del triángulo. Sirve para disparos, para el ratón sobre la escena, para saber qué hay bajo los
pies y para la línea de visión de un enemigo.

```gml
/// scr_raycast
#macro RAYO_EPSILON 0.000001

/// Devuelve la distancia t a lo largo del rayo hasta el triángulo, o -1 si no lo cruza.
/// El punto de impacto es (_ox + _dx*t, _oy + _dy*t, _oz + _dz*t).
/// La dirección (_dx,_dy,_dz) debe ser unitaria para que t esté en píxeles.
function rayo_contra_triangulo(_ox, _oy, _oz, _dx, _dy, _dz,
                               _ax, _ay, _az, _bx, _by, _bz, _cx, _cy, _cz) {
    // Las dos aristas que salen del vértice A
    var _e1x = _bx - _ax, _e1y = _by - _ay, _e1z = _bz - _az;
    var _e2x = _cx - _ax, _e2y = _cy - _ay, _e2z = _cz - _az;
    // h = dirección × arista2
    var _hx = _dy * _e2z - _dz * _e2y;
    var _hy = _dz * _e2x - _dx * _e2z;
    var _hz = _dx * _e2y - _dy * _e2x;
    var _det = dot_product_3d(_e1x, _e1y, _e1z, _hx, _hy, _hz);
    if (abs(_det) < RAYO_EPSILON) return -1;   // el rayo es paralelo al triángulo
    var _inv = 1 / _det;
    // s = origen del rayo - A
    var _sx = _ox - _ax, _sy = _oy - _ay, _sz = _oz - _az;
    var _u = _inv * dot_product_3d(_sx, _sy, _sz, _hx, _hy, _hz);
    if (_u < 0 || _u > 1) return -1;           // fuera del triángulo
    // q = s × arista1
    var _qx = _sy * _e1z - _sz * _e1y;
    var _qy = _sz * _e1x - _sx * _e1z;
    var _qz = _sx * _e1y - _sy * _e1x;
    var _v = _inv * dot_product_3d(_dx, _dy, _dz, _qx, _qy, _qz);
    if (_v < 0 || _u + _v > 1) return -1;      // fuera del triángulo
    var _t = _inv * dot_product_3d(_e2x, _e2y, _e2z, _qx, _qy, _qz);
    return (_t > RAYO_EPSILON) ? _t : -1;      // t <= 0 → el triángulo está detrás
}
```

> 💡 **`u` y `v` son las coordenadas baricéntricas del impacto**: si los devuelves en vez de
> descartarlos, puedes interpolar la normal y la UV del punto exacto de choque (para elegir el
> sonido del impacto según el material, por ejemplo).
>
> 🔺 **No lo lances contra todos los triángulos del nivel.** 20.000 triángulos son 20.000
> llamadas por rayo. Divide el mundo en una rejilla (*spatial hash*) y prueba solo las celdas
> que el rayo atraviesa; `DS-3DCollisions` trae una hecha (`Col_Spatial_Hash`).

### Suelo por mapa de alturas

Para terreno la colisión no necesita triángulos: basta con la altura del suelo en un punto,
interpolada entre las cuatro esquinas de su celda.

```gml
/// scr_terreno
#macro TERRENO_CELDA 128
/// Altura del terreno en (_px, _py), interpolada bilinealmente.
/// global.mapa_altura es un array 2D: global.mapa_altura[columna][fila]
function altura_del_terreno(_px, _py) {
    var _gx = _px / TERRENO_CELDA;
    var _gy = _py / TERRENO_CELDA;
    var _i  = floor(_gx);
    var _j  = floor(_gy);
    var _fx = _gx - _i;                 // posición dentro de la celda, 0..1
    var _fy = _gy - _j;
    var _cols  = array_length(global.mapa_altura);
    var _filas = array_length(global.mapa_altura[0]);
    if (_i < 0 || _j < 0 || _i >= _cols - 1 || _j >= _filas - 1) return 0;
    var _h00 = global.mapa_altura[_i][_j];
    var _h10 = global.mapa_altura[_i + 1][_j];
    var _h01 = global.mapa_altura[_i][_j + 1];
    var _h11 = global.mapa_altura[_i + 1][_j + 1];
    return lerp(lerp(_h00, _h10, _fx), lerp(_h01, _h11, _fx), _fy);
}
```

```gml
/// obj_control · Create — terreno de ejemplo (llano, 64×64 celdas a altura 0).
/// Sustitúyelo por tu import de heightmap o por ruido procedural (04 · 05) — sin
/// esta línea, altura_del_terreno() lee un global.mapa_altura que nunca se creó.
global.mapa_altura = array_create(64);
for (var _i = 0; _i < 64; _i++)
{
    global.mapa_altura[_i] = array_create(64, 0);
}
```
```gml
/// obj_jugador · Step — caminar sobre el terreno con gravedad
z_velocidad -= 0.6;                       // gravedad: con Z arriba, se resta
z += z_velocidad;
var _suelo = altura_del_terreno(x, y);
en_el_suelo = (z <= _suelo);
if (en_el_suelo) { z = _suelo; z_velocidad = 0; }
if (en_el_suelo && keyboard_check_pressed(vk_space)) z_velocidad = 10;
```

### Librerías que ya lo resuelven

Todas están **descargadas** en la biblioteca; míralas antes de escribir tu sistema de colisión.

| Librería | Qué resuelve | Dónde está |
|---|---|---|
| **ColMesh** (TheSnidr) | Esferas y cápsulas contra **mallas arbitrarias**, con partición espacial. La referencia histórica del 3D en GameMaker | `11 - Código descargado/librerias/3d/ColMesh` |
| **DS-3DCollisions** (DragoniteSpam) | Colisión 3D **nativa** sin extensiones: AABB, OBB, esfera, cápsula, plano, triángulo, malla, rayo, *spatial hash*, frustum | `11 - Código descargado/librerias/3d/DS-3DCollisions` |
| **Bonk** (Juju Adams) | Primitiva contra primitiva, 2D y 3D, fuera del sistema de máscaras | `11 - Código descargado/librerias/fisica/Bonk` |
| **BBMOD** (blueburncz) | Motor 3D completo: modelos, PBR, animación esquelética, terreno, sombras, niebla | `11 - Código descargado/librerias/3d/BBMOD` |
| **Cardboard** (Juju Adams) | Geometría 3D sencilla montada sobre la tubería 2D. De ahí sale la matriz de cartel de §6 | `11 - Código descargado/librerias/3d/Cardboard` |
| **Stack3D** (dev-dwarf) | Sprite stacking rápido (falso 3D sin tubería 3D) | `11 - Código descargado/librerias/3d/Stack3D` |

Fichas completas de ColMesh y BBMOD en
[07 · 02 — Librerías esenciales de la comunidad](../07%20-%20Ecosistema/02%20-%20Librerías%20esenciales%20de%20la%20comunidad.md).

> ⚠️ **ColMesh es de la era GMS 2.3** y GitHub **no reporta licencia detectada** en el repo
> (consultado el 2026-09-06). El núcleo matemático es GML puro y sigue valiendo: revisa las
> llamadas al portarlo a LTS 2026 y confirma la licencia con el autor antes de publicar.

---

## 9 · Rendimiento

El 3D se hunde por motivos distintos que el 2D. Por orden de impacto:

| Técnica | Qué gana | Cómo |
|---|---|---|
| **`vertex_freeze`** | Lo más grande, con diferencia | Toda geometría que no cambie: nivel, props, terreno. Congelada vive en la GPU |
| **Un buffer por malla, no por objeto** | Menos *draw calls* | 200 cajas = **1** buffer de cubo dibujado 200 veces con distinta `matrix_world` |
| **Fundir la geometría estática** | Menos *draw calls* todavía | Todo el nivel en un buffer congelado: 1 llamada para el escenario entero |
| **Culling por distancia y de caras** | Menos triángulos, ~mitad del dibujo | `sphere_is_visible(x, y, z, radio)` descarta lo que sale del frustum; `gpu_set_cullmode` quita las caras traseras |
| **Niebla + plano lejano corto** | Menos geometría lejana | `gpu_set_fog` esconde el corte; `PLANO_LEJANO` bajo recorta más |
| **Una sola página de textura** | Menos cambios de textura | Todo el nivel en un atlas: el 3D no aprovecha el *batching* automático |
| **Nada de primitivas inmediatas** | Enorme | `draw_primitive_begin` + `draw_vertex_*` reconstruye el buffer **cada frame** |
| **YYC** | 2-5× en la lógica GML | El coste de matemática de colisión en GML baja mucho compilando a C++ |

```gml
/// El patrón correcto para dibujar muchas copias de la misma malla
var _tex = sprite_get_texture(spr_caja, 0);
with (obj_caja) {
    // No dibujar lo que no cabe en la cámara
    if (!sphere_is_visible(x, y, z, 48)) continue;
    matrix_set(matrix_world, matrix_build(x, y, z, 0, 0, giro, 1, 1, 1));
    vertex_submit(obj_camara3d.vb_caja, pr_trianglelist, _tex);
}
matrix_set(matrix_world, matrix_build_identity());
```

> 🔺 **`draw_primitive_begin_texture` + `draw_vertex_texture_colour` es la trampa del
> principiante:** funciona, se lee fácil, y reenvía toda la geometría a la GPU cada frame. Vale
> para depurar (una línea, un eje) y para nada más. Vertex buffers congelados, siempre.
>
> 💡 **Mide antes de optimizar.** `GMBenchmark` (DragoniteSpam, MIT) y el tutorial
> `HowManyTriangles` de la misma serie dicen cuántos triángulos aguanta tu máquina de verdad.

---

## 10 · Lo que ya tienes descargado para estudiar

No empieces de cero: los proyectos de referencia ya están clonados en
`11 - Código descargado/plantillas_y_ejemplos/`. **La serie 3D de DragoniteSpam** (90 proyectos
MIT, `3DTutorial1` → `3DTutorial94`, en `dragonitespam/`) es el curso de 3D en GameMaker: cámara,
vertex buffers, texturas, OBJ, primera y tercera persona, *billboarding*, *split screen*, niebla,
*toon shading*, *normal mapping*, *shadow mapping* y *deferred rendering*. **3D-2D**, el viejo
ejemplo oficial de mezclar 3D y 2D, está **abandonado** y su propio repo remite a GM3D-Samples.

**Qué hay dentro de GM3D-Samples** (YoYo Games, MIT, 13 ★) (leído el 2026-09-06): cuatro escenas —`objSample_0_Static`
(un `.glb` estático con luz direccional y cámara orbital), `objSample_1_Animated` (animación
esquelética), `objSample_2_Scene` (grafo de escena completo) y `objSample_3_Forest` (el mismo
modelo instanciado muchas veces)—, cuatro shaders, modelos `.glb` de Kenney, y
`notes/GM3D_API.md`: un índice de 953 líneas con toda la API (`GM3D_Scene.loadGltf()`,
`GM3D_CameraComponent`, `GM3D_LightComponent`, `GM3D_Quaternion`, `GM3D_Matrix4`, `GM3D_Vec3`…).

> ⚠️ **GM3D-Samples no compila con el runtime LTS `2026.0.0.23`:** ninguno de sus símbolos
> `GM3D_*` existe en el `GmlSpec.xml` instalado, y su propio fichero de notas avisa de que «todo
> aquí es experimental y puede cambiar». Léelo para saber hacia dónde va el motor, no como API
> de hoy. Ficha del repo en
> [07 · 01 — GitHub, organización YoYoGames](../07%20-%20Ecosistema/01%20-%20GitHub%20-%20organización%20YoYoGames.md).

---

## Las trampas

| Trampa | Consecuencia |
|---|---|
| No llamar a `camera_apply()` | Pantalla vacía con las matrices perfectamente montadas |
| Dejar el z-test apagado (`gpu_set_ztestenable`) | Las caras traseras se dibujan encima de las delanteras |
| No apagar el z-test antes de la GUI | El HUD desaparece o parpadea |
| Escribir en el z-buffer al dibujar transparencias | Recortes negros alrededor de la hierba; el cristal borra lo de detrás |
| No resetear `matrix_world` con `matrix_build_identity()` | Todo lo que dibujes después sale girado y desplazado |
| FOV negativo con aspecto positivo (o los dos positivos) | Escena espejada o girada 180°: la Y de GameMaker va hacia abajo |
| Pasar el FOV en radianes | El campo de visión se va a 3.400°: se ve todo minúsculo. **Va en grados** |
| Textura repetida sin **Separate Texture Page** | El suelo repite trozos de otros sprites de la misma página |
| Formato de vértice sin `vertex_format_add_normal()` | La iluminación no hace nada: todo plano |
| Escribir los atributos en distinto orden que el formato | Geometría corrupta o error en tiempo de ejecución |
| Usar `pr_trianglefan` | No está soportado en móvil; se convierte por dentro o falla |
| No congelar (`vertex_freeze`) la geometría estática | Rendimiento muchísimo peor sin ganar nada |
| Reconstruir con `draw_primitive_*` cada frame | La forma más rápida de bajar de 60 fps |
| Índices del `.obj` sin restar 1 | El modelo sale como una explosión de triángulos |
| No destruir la cámara en Clean Up | Fuga de recursos al cambiar de sala |

---

## Ver también

- [08 · 07 — Vertex buffers y formatos](../08%20-%20Referencia%20GML%20completa/07%20-%20Vertex%20buffers%20y%20formatos.md) — la ficha de cada función `vertex_*` y un terreno procedural completo
- [08 · 11 — Vectores, matrices y ángulos](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores,%20matrices%20y%20ángulos.md) — `matrix_build*`, la pila de matrices, producto escalar 3D
- [08 · 06 — Shaders](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md) — anatomía de un shader, uniforms integrados, índices de matriz, niebla
- [08 · 08 — Texturas y grupos de texturas](../08%20-%20Referencia%20GML%20completa/08%20-%20Texturas%20y%20grupos%20de%20texturas.md) — páginas de textura, VRAM, grupos dinámicos
- [01 · 10 — Rooms, capas, cámaras y viewports §7](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md) y [01 · 11 — Dibujo y renderizado](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) — crear y destruir cámaras, orden de los eventos de dibujo, *batching*, Draw GUI
- [02 · 03 — GMRT, el nuevo runtime](../02%20-%20Novedades%202026/03%20-%20GMRT%20-%20El%20nuevo%20runtime.md) — el estado de GM3D y cuándo (no) usarlo
- [13 · 13 — Matemáticas aplicadas al juego](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md) — vectores, producto escalar y vectorial, interpolación
- [07 · 02 — Librerías esenciales de la comunidad](../07%20-%20Ecosistema/02%20-%20Librerías%20esenciales%20de%20la%20comunidad.md) — fichas de ColMesh, BBMOD y Bonk
- [07 · 04 — Proyectos de ejemplo para estudiar §4 bis](../07%20-%20Ecosistema/04%20-%20Proyectos%20de%20ejemplo%20para%20estudiar.md) — el desglose de la serie 3D de DragoniteSpam
- [24 · Iluminación 2D](./24%20-%20Iluminación%202D.md) — cuando lo que quieres es luz, no 3D
- [12 · Carreras y vehículos](./12%20-%20Carreras%20y%20vehículos.md) — el caso 2.5D más común

---

## Fuentes

Consultadas el **2026-09-06**.

- **Manual oficial de GameMaker LTS 2026** (espejo local en `09 - Manual oficial/manual-lts-2026-es/`): la [guía de primitivas y construcción de vértices](https://manual.gamemaker.io/lts/es/Additional_Information/Guide_To_Primitives_And_Vertex_Building.htm) (formatos, mapeo a atributos del shader, la prohibición de `pr_trianglefan`); [`matrix_build_lookat`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Matrix_Functions/matrix_build_lookat.htm) y [`matrix_build_projection_perspective_fov`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Matrix_Functions/matrix_build_projection_perspective_fov.htm) (el FOV va **en grados**); GPU Control ([`gpu_set_ztestenable`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_ztestenable.htm), [`gpu_set_cullmode`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_cullmode.htm), `gpu_set_fog`, `gpu_set_alphatestenable` con su aviso de rendimiento en iOS/Android, [`gpu_set_texrepeat`](https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_texrepeat.htm) y su exigencia de *Separate Texture Page*, `gpu_set_tex_mip_enable`); Lighting (`draw_set_lighting`, `draw_light_define_direction`/`_point`/`_ambient`, límite de **8 luces de hardware**); y The Game Window (`window_mouse_set_locked`, `window_mouse_get_delta_x`/`_y`, con sus límites en HTML5 y Wayland).
- **[github.com/YoYoGames/GM3D-Samples](https://github.com/YoYoGames/GM3D-Samples)** — MIT, 13 ★, creado el 2026-05-29, último *push* el 2026-09-05 (API de GitHub). Proyecto clonado en la biblioteca; contenido descrito en §10.
- **[github.com/blueburncz/BBMOD](https://github.com/blueburncz/BBMOD)** — «Make 3D games in GameMaker!», MIT, 119 ★, rama `bbmod3`, último *push* 2026-08-04. Documentación: <https://blueburn.cz/bbmod/>.
- **[github.com/TheSnidr/ColMesh](https://github.com/TheSnidr/ColMesh)** — «A 3D collision system for GameMaker Studio 2.3», 19 ★, creado 2021-01-17, último *push* 2025-08-12. ⚠️ GitHub no reporta licencia detectada.
- **[github.com/JujuAdams/dotobj](https://github.com/JujuAdams/dotobj)** — cargador `.obj`/`.mtl` en GML nativo, MIT, 47 ★, último *push* 2025-10-12.
- **[github.com/DragoniteSpam](https://github.com/DragoniteSpam)** y la organización [DragoniteSpam-GameMaker-Tutorials](https://github.com/DragoniteSpam-GameMaker-Tutorials) — 193 proyectos MIT, de los que 90 son la serie 3D. El convenio de ejes, el par de signos de la proyección y el patrón de `matrix_world` de este documento salen de leer su código, clonado en la biblioteca.
- **Tomas Möller y Ben Trumbore, «Fast, Minimum Storage Ray/Triangle Intersection», *Journal of Graphics Tools*, vol. 2, 1997, pp. 21–28** — el algoritmo de §8, vía <https://en.wikipedia.org/wiki/Möller–Trumbore_intersection_algorithm>.
