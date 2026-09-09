# 58 · El nivel como mapa de texto — construir sin abrir el editor de salas

> **El hueco que cierra este documento.** Toda esta biblioteca está escrita para un agente que
> no abre el IDE, y sin embargo la técnica que hace posible **diseñar un nivel sin él** no
> estaba en ninguna parte: `04 · 01 §2` habla de rooms y capas dando por hecho el editor de
> salas, y [`13 · 02`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/02%20-%20Diseño%20de%20niveles.md)
> habla de diseño, no de cómo materializarlo. Lo detectó un agente que construyó un juego
> completo con esta biblioteca y tuvo que inventarse el patrón sobre la marcha —«la decisión
> estructural más grande del juego, y la tomé sin apoyo»
> ([`r12-prueba-plataformas.md` §1.8](../_indice/auditorias/r12-prueba-plataformas.md)).

> ✅ **Esto ya está escrito, compilado y EJECUTADO: no lo reimplementes.**
> [`06 · scr_nivel_mapa.gml`](../06%20-%20Assets%20y%20Scripts/scr_nivel_mapa.gml) es todo lo de
> aquí abajo generalizado —la leyenda decide qué es sólido, los papeles son un campo y no dos
> caracteres fijos, y `nivel_mapa_construir()` valida antes de crear nada—. Pasa un banco de 46
> comprobaciones dentro de un juego real (`bash _indice/validar-ejecucion.sh`).
> **Lee esta receta para entender las decisiones; usa el script para no repetirlas.**
>
> Los nombres son distintos a propósito —el script usa `nivel_mapa_…` y esta receta `nivel_…`—
> para que puedas tener las dos cosas delante sin que una pise a la otra. Si usas el script,
> **no copies además el código de abajo**: harías dos versiones de lo mismo, y la que no está
> probada ganaría la mitad de las veces.

---

## 1 · Por qué no se colocan las instancias en la sala

Hay tres formas de llenar un nivel, y para un agente solo una es viable.

| Vía | Coste | Problema |
|---|---|---|
| Editor de salas del IDE | — | **No existe** para un agente |
| `ROOM INSTANCE CREATE`, una por bloque | Una llamada de `resourcetool` por instancia | Un nivel modesto son **1 400 instancias**: minutos por iteración, y cada retoque del diseño las repite todas |
| **Mapa de texto + constructor en el Create** | Un archivo de texto | Ninguno. Es esta receta |

Y hay una razón más para no dejar el nivel *dentro* de la sala: **borrar o recrear una sala se
lleva su contenido** ([`12 · 09 §9.2`](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md)),
así que iterar sobre el diseño —que es lo que se hace todo el rato— resulta caro y arriesgado.
Con el nivel en datos, la sala se queda vacía para siempre y el diseño se cambia editando texto.

> 💡 **La otra mitad de la misma idea**: si el nivel es de baldosas y no de instancias,
> `ROOM LAYER TILES SET … FILE=<csv>` importa un tilemap entero desde un CSV en una sola llamada
> — es la vía natural para traer un mapa hecho en Tiled. Está en
> [`12 · 09 §3 bis.3`](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#3-bis3-tilesets-y-tilemaps--incluido-importar-un-csv).
> Las dos técnicas conviven: baldosas para el terreno, instancias para lo que tiene lógica.

---

## 2 · La leyenda: un carácter, una cosa

```gml
// scr_niveles.gml

#macro MAPA_CELDA 16          // píxeles por casilla

/// @func nivel_leyenda()
/// @desc Un carácter -> qué se crea. Punto y espacio son aire.
///       Devuelve un struct para poder preguntarlo con `[$ _c]` sin ifs anidados.
function nivel_leyenda()
{
    return {
        "#" : { objeto: obj_solido,        solido: true  },
        "=" : { objeto: obj_plataforma,    solido: false },  // de un sentido
        "^" : { objeto: obj_pincho,        solido: false },
        "o" : { objeto: obj_moneda,        solido: false },
        "c" : { objeto: obj_cangrejo,      solido: false },
        "@" : { objeto: obj_aparicion,     solido: false },  // dónde empieza el jugador
        "!" : { objeto: obj_salida,        solido: false }
    };
}
```

> ⚠️ **No uses la comilla doble como carácter del mapa.** Parece un símbolo cómodo para una
> plataforma larga y obliga a escaparla dentro del literal; si el generador que escribe el
> `.gml` se olvida de escaparla, **el literal se cierra antes de tiempo** y a partir de ahí el
> archivo entero se lee mal — el compilador falla, y los analizadores dan una lista de errores
> desconcertante. Caso real en
> [`r12-prueba-plataformas.md` §1.1](../_indice/auditorias/r12-prueba-plataformas.md).
> `validar-proyecto.py` ya avisa de un literal sin cerrar, pero es más fácil no crearlo:
> elige `>`, `-` o `~`.

---

## 3 · Validar el mapa ANTES de construirlo

Un mapa mal formado no da un error: da un nivel roto de una forma difícil de ver —una fila
desplazada, un enemigo que aparece dentro de la roca, ninguna salida—. Se valida en el Create,
una vez, y se falla ruidosamente.

```gml
/// @func nivel_validar(_filas, _leyenda)
/// @desc Comprueba lo que rompe un nivel en silencio. Devuelve [] si está bien,
///       o un array de problemas legibles.
/// @param {Array<String>} _filas
/// @param {Struct} _leyenda
/// @return {Array<String>}
function nivel_validar(_filas, _leyenda)
{
    var _problemas = [];
    var _alto = array_length(_filas);

    if (_alto == 0) { array_push(_problemas, "el mapa no tiene ni una fila"); return _problemas; }

    var _ancho = string_length(_filas[0]);
    var _apariciones = 0;
    var _salidas     = 0;

    for (var _y = 0; _y < _alto; _y++)
    {
        // Todas las filas miden lo mismo. Una fila corta desplaza TODO lo que
        // hay debajo y es el error más común al editar el mapa a mano.
        if (string_length(_filas[_y]) != _ancho)
        {
            array_push(_problemas, "la fila " + string(_y) + " mide "
                + string(string_length(_filas[_y])) + " y la primera mide " + string(_ancho));
        }

        for (var _x = 1; _x <= string_length(_filas[_y]); _x++)
        {
            var _c = string_char_at(_filas[_y], _x);
            if (_c == "." || _c == " ") continue;

            // Un carácter que no está en la leyenda se ignoraría en silencio.
            if (!struct_exists(_leyenda, _c))
            {
                array_push(_problemas, "carácter «" + _c + "» sin leyenda, en "
                    + string(_x - 1) + "," + string(_y));
                continue;
            }
            if (_c == "@") _apariciones++;
            if (_c == "!") _salidas++;
        }
    }

    if (_apariciones != 1) array_push(_problemas, "hay " + string(_apariciones)
        + " puntos de aparición y debe haber exactamente 1");
    if (_salidas == 0)     array_push(_problemas, "el nivel no tiene salida");

    return _problemas;
}
```

Y en el Create del gestor de nivel, **antes** de construir nada:

```gml
var _leyenda   = nivel_leyenda();
var _filas     = nivel_filas(global.nivel_actual);
var _problemas = nivel_validar(_filas, _leyenda);

if (array_length(_problemas) > 0)
{
    for (var _i = 0; _i < array_length(_problemas); _i++)
        show_debug_message("MAPA MAL FORMADO: " + _problemas[_i]);
    // Falla ruidosamente: un nivel roto que arranca es peor que uno que no arranca.
    show_error("El mapa del nivel " + string(global.nivel_actual) + " está mal formado."
             + " Mira el log.", true);
}
```

> ⚠️ **No te apoyes en que `show_error()` pare el juego.** El manual de LTS 2026 dice de su
> segundo argumento: *«only exists for backwards compatibility … and will have no effect»*, y de
> la función entera: *«for debug use only»*. Es decir, el `true` de ahí arriba no promete nada.
> Lo que sí garantiza que no arranque un nivel a medias es **no construir**: por eso
> `nivel_mapa_construir()` de [`06 · scr_nivel_mapa.gml`](../06%20-%20Assets%20y%20Scripts/scr_nivel_mapa.gml)
> valida primero y, si hay un problema, **vuelve sin crear una sola instancia** — pase lo que
> pase con el diálogo. Y acepta un `al_fallar` para llevar el aviso a tu propia pantalla de
> error, que además es lo único que hace el fallo *comprobable*: con un diálogo modal delante,
> una prueba automática se queda colgada.

---

## 4 · Construir, saltándose lo que nadie va a ver

El constructor es un doble bucle. Lo único que no es obvio es la optimización, y **no es
opcional en un nivel grande**: una casilla de roca rodeada de roca por los ocho lados no se ve
nunca y no colisiona con nada, así que crear su instancia es gasto puro.

```gml
/// @func nivel_construir(_filas, _leyenda, _capa)
/// @desc Instancia el mapa. Devuelve { aparicion_x, aparicion_y, creadas, saltadas }.
function nivel_construir(_filas, _leyenda, _capa)
{
    var _alto = array_length(_filas);
    var _res  = { aparicion_x: 0, aparicion_y: 0, creadas: 0, saltadas: 0 };

    for (var _y = 0; _y < _alto; _y++)
    {
        var _fila = _filas[_y];
        for (var _x = 0; _x < string_length(_fila); _x++)
        {
            var _c = string_char_at(_fila, _x + 1);
            if (_c == "." || _c == " ") continue;
            if (!struct_exists(_leyenda, _c)) continue;   // ya avisó nivel_validar()

            var _px = _x * MAPA_CELDA;
            var _py = _y * MAPA_CELDA;

            if (_c == "@")
            {
                _res.aparicion_x = _px;
                _res.aparicion_y = _py;
                continue;
            }

            // Roca enterrada: ocho vecinos sólidos = invisible e intocable.
            if (_c == "#" && nivel_enterrada(_filas, _x, _y))
            {
                _res.saltadas++;
                continue;
            }

            instance_create_layer(_px, _py, _capa, _leyenda[$ _c].objeto);
            _res.creadas++;
        }
    }

    return _res;
}

/// @func nivel_enterrada(_filas, _x, _y)
/// @desc true si las ocho casillas vecinas son sólidas (o el borde del mapa).
///       Fuera del mapa cuenta como sólido: si no, todo el borde quedaría "visible".
function nivel_enterrada(_filas, _x, _y)
{
    var _alto = array_length(_filas);
    for (var _oy = -1; _oy <= 1; _oy++)
    {
        for (var _ox = -1; _ox <= 1; _ox++)
        {
            if (_ox == 0 && _oy == 0) continue;

            var _vx = _x + _ox;
            var _vy = _y + _oy;
            if (_vy < 0 || _vy >= _alto) continue;                       // borde: sólido
            var _fila = _filas[_vy];
            if (_vx < 0 || _vx >= string_length(_fila)) continue;        // borde: sólido

            if (string_char_at(_fila, _vx + 1) != "#") return false;
        }
    }
    return true;
}
```

> 🔴 **Si el objeto deduce su posición de su casilla, las variables van en el QUINTO argumento.**
> `instance_create_layer()` ejecuta el `Create` de la instancia **antes de devolver**, así que
> esto llega tarde:
>
> ```gml
> var _inst = instance_create_layer(_px, _py, _capa, obj_bloque);
> _inst.gx = _x;  _inst.gy = _y;      // ❌ el Create ya corrió con gx = 0
> ```
>
> El bloque se coloca en 0,0 y ahí se queda, encima del muro, sin un solo error. Le costó media
> hora a un agente ([`r15` §2.5](../_indice/auditorias/r15-prueba-puzles.md)). La vía buena es el
> quinto argumento, `[var_struct]`, que se aplica **antes** del `Create`:
>
> ```gml
> var _inst = instance_create_layer(_px, _py, _capa, obj_bloque, { gx: _x, gy: _y });
> ```
>
> **Y ojo con la segunda mitad de la trampa**: si el propio `Create` escribe `gx = 0` como valor
> por defecto, lo pisa igual. Por eso `nivel_mapa_construir()` hace las dos cosas —lo pasa en el
> struct *y* lo vuelve a poner después— y ofrece un gancho `al_crear(_inst, _c, _col, _fila)`
> para el objeto que necesite recolocarse a sí mismo con el dato ya en la mano. Que el quinto
> argumento llega antes del `Create` está **medido** en `validar-ejecucion.sh`, no supuesto.

**Cuánto ahorra**, medido en los tres niveles de un juego real construido con esta receta:

| Nivel | Bloques en el mapa | Instancias creadas | Ahorro |
|---|---|---|---|
| 1 | 758 | 272 | **64 %** |
| 2 | 1 793 | 716 | 60 % |
| 3 | 646 | 436 | 33 % |

El ahorro depende de lo maciza que sea la roca: un nivel de cuevas gana mucho más que uno de
plataformas flotantes. En los tres casos, sin coste visual alguno.

> ⚠️ **Solo se saltan las casillas SÓLIDAS y solo si el vecindario completo lo es.** Un
> coleccionable enterrado sigue teniendo que existir (el guardado lo cuenta), y un bloque con
> ocho vecinos sólidos pero que el jugador puede destruir tampoco se salta. Si tu juego permite
> excavar, esta optimización no aplica: la roca de dentro se vuelve visible en cuanto se rompe
> la de fuera.

---

## 5 · Índices estables: de lo que depende el guardado

Los coleccionables no se guardan por posición: se guardan por **índice**, y ese índice tiene
que salir igual en cada arranque. El recorrido de arriba (fila a fila, izquierda a derecha) ya
lo garantiza — **siempre que no cambies el mapa**.

```gml
/// Al crear cada coleccionable, dale su índice:
var _inst = instance_create_layer(_px, _py, _capa, obj_moneda);
_inst.indice = _res.creadas_coleccionables++;

/// Y al construir, no crees los ya recogidos:
if (_c == "o" && global.recogidos[_indice_previsto]) continue;
```

> 🔴 **Editar el mapa invalida los guardados.** Añadir una moneda en mitad del nivel desplaza el
> índice de todas las siguientes, y una partida guardada creerá que recogió otras. Hay dos
> salidas: **congelar el mapa** cuando publiques, o guardar por **clave estable**
> (`"n1_x34_y12"` a partir de la posición en el mapa, que no se desplaza al insertar). La
> segunda cuesta una línea más y es la que aguanta parches posteriores.

---

## 6 · Autotile de 4 bits: que la roca no parezca un tablero de ajedrez

Con el mapa en texto, elegir el sprite correcto para cada bloque es una máscara de bits de sus
cuatro vecinos. El bitmask completo de 8 vecinos (47 baldosas) y la variante de 16 están en
[`13 · 07 §5 bis`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/07%20-%20Generación%20procedural%20avanzada.md#5-bis--autotiling-clásico-bitmask-de-vecinos--índice-de-tile);
esto es la versión mínima que basta para un plataformas.

```gml
/// @func nivel_bitmask(_filas, _x, _y)
/// @desc 1 arriba · 2 derecha · 4 abajo · 8 izquierda. Fuera del mapa cuenta
///       como sólido, para que el borde no se dibuje con contorno.
/// @return {Real} 0..15, listo para usar como image_index
function nivel_bitmask(_filas, _x, _y)
{
    var _dx = [ 0,  1,  0, -1];
    var _dy = [-1,  0,  1,  0];
    var _m  = 0;

    for (var _k = 0; _k < 4; _k++)
    {
        var _vx = _x + _dx[_k];
        var _vy = _y + _dy[_k];
        var _es_solido = true;                       // fuera del mapa: sólido

        if (_vy >= 0 && _vy < array_length(_filas))
        {
            var _fila = _filas[_vy];
            if (_vx >= 0 && _vx < string_length(_fila))
                _es_solido = (string_char_at(_fila, _vx + 1) == "#");
        }

        if (_es_solido) _m |= (1 << _k);
    }

    return _m;
}
```

Ordena las 16 sub-imágenes del sprite en ese mismo orden y asigna `image_index = _m` al crear
el bloque. No hace falta nada más.

> 🔀 **Aquí fuera del mapa cuenta como SÓLIDO; en [`13 · 07 §5 bis`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/07%20-%20Generación%20procedural%20avanzada.md#5-bis--autotiling-clásico-bitmask-de-vecinos--índice-de-tile)
> cuenta como VACÍO.** No es una contradicción: son dos preguntas distintas y las dos respuestas
> son correctas en su sitio.
>
> | Fuera del mapa… | Qué pasa en el borde | Cuándo lo quieres |
> |---|---|---|
> | **sólido** (esta receta) | la roca del borde **no** se remata con contorno | el nivel continúa fuera de cámara: rematarlo delataría dónde se acaba |
> | **vacío** (`13 · 07`) | el borde **sí** se remata | el mapa se ve entero, como una isla o un tablero |
>
> Elegir mal no da error: da un contorno de más o de menos que nadie sabe de dónde sale. En
> `scr_nivel_mapa.gml` es la opción `fuera_es_solido`, y hay una prueba de las dos direcciones —
> la misma esquina da bitmask **15** con una y **6** con la otra.

---

## 7 · Dónde vive el mapa

| Sitio | Cuándo | Cuidado |
|---|---|---|
| Un `.gml` con el array de cadenas | Por defecto. Cero E/S, cero fallos de ruta | El archivo crece; no se puede tocar sin recompilar |
| Un *included file* de texto | Si quieres que se pueda editar sin recompilar (mods) | Los *included files* se pasan a **minúsculas** en el paquete y hay que fijar su `filePath` a mano — [`12 · 09` Trampa 8](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md) |
| Un CSV importado al tilemap por CLI | Si el terreno es de baldosas | `ROOM LAYER TILES SET FILE=` — §1 |

Si generas el `.gml` desde un script (Python, por ejemplo), **valida la salida**: es donde se
cuela la comilla sin escapar del §2. `python3 "$BIB/_indice/validar-proyecto.py" <proyecto>`
avisa de un literal sin cerrar con archivo y línea.

---

## 8 · Checklist

- [ ] La leyenda **no usa la comilla doble** como carácter
- [ ] `nivel_validar()` se llama en el Create, antes de construir, y falla ruidosamente
- [ ] Todas las filas miden lo mismo (lo comprueba la validación)
- [ ] Hay exactamente un punto de aparición y al menos una salida
- [ ] Los caracteres sin leyenda se detectan, no se ignoran
- [ ] La roca enterrada no se instancia — y se comprueba que el ahorro es real
- [ ] Los coleccionables se guardan por clave estable, no por índice de recorrido
- [ ] El bitmask trata el fuera-de-mapa como sólido (o el borde sale con contorno)
- [ ] Si el `.gml` lo genera un script, la salida pasa `validar-proyecto.py`

---

## Ver también

- [00 · Anatomía de un juego completo](./00%20-%20Anatomía%20de%20un%20juego%20completo.md) — dónde encaja el nivel dentro del arco
- [01 · Plataformas 2D](./01%20-%20Plataformas%202D.md) — el movimiento que recorre este nivel
- [13 · 02 — Diseño de niveles](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/02%20-%20Diseño%20de%20niveles.md) — qué poner en el mapa; esto es cómo materializarlo
- [13 · 07 §5 bis — Autotiling clásico](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/07%20-%20Generación%20procedural%20avanzada.md#5-bis--autotiling-clásico-bitmask-de-vecinos--índice-de-tile) — el bitmask completo de 8 vecinos
- [12 · 09 §3 bis — Construir el juego entero por CLI](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#3-bis--construir-el-juego-entero-por-cli-qué-se-escribe-de-verdad) — salas, capas y tilemaps por línea de comandos
