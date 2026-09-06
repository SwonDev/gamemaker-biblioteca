# 05 · Scripts y utilidades GML

> Verificado el **31 de agosto de 2026** con `gm-cli manual read` (manual oficial, versión LTS 2026).
> Para cada script se indica explícitamente **qué ya trae GameMaker de serie** y por qué merece la pena la versión propia.
> Todo el código está comentado en español y usa GML moderno (constructores, structs, `static`, `method`).

---

## 0. Auditoría previa: qué **no** hace falta reimplementar

Antes de escribir una sola línea he consultado el manual oficial. Esto **ya existe de serie** y NO debes reescribirlo:

| Función | Estado | Conclusión |
|---|---|---|
| `lerp(a, b, amt)` | ✅ **Nativo** | No reimplementes interpolación lineal. |
| `animcurve_*` (Animation Curves) | ✅ **Nativo** | Existe un sistema de curvas completo: `animcurve_get`, `animcurve_get_channel`, `animcurve_channel_evaluate`, `animcurve_create`, `animcurve_channel_new`, `animcurve_point_new`, `animcurve_destroy`. |
| `ds_grid_*` | ✅ **Nativo** | Rejillas 2D completas: `ds_grid_create`, `ds_grid_set`, `ds_grid_get`, `ds_grid_destroy`. |
| `mp_grid_path()` | ✅ **Nativo** | Pathfinding A* sobre una rejilla MP. |
| `tilemap_get()` / `tilemap_set()` / `tilemap_get_width()` / `tilemap_get_height()` | ✅ **Nativo** | Lectura y escritura de *tiles*. |
| `camera_create()` / `camera_destroy()` / `camera_set_*` | ✅ **Nativo** | Cámaras. |
| `instance_create_layer()` | ✅ **Nativo** | Creación de instancias. |
| `json_stringify()` / `json_parse()` | ✅ **Nativo** | Serialización de structs y arrays. |
| `struct_get_names()` | ✅ **Nativo** | Nombres de las variables de un struct (también existe `variable_struct_get_names`, su nombre antiguo). |
| `instance_deactivate_layer()` / `instance_activate_layer()` | ✅ **Nativo** | Activar/desactivar instancias por capa. |
| `ds_priority_*` | ✅ **Nativo** | Cola de prioridad, base del A*. |

Y esto **no existe**, así que sí hay que escribirlo:

| Necesidad | Estado |
|---|---|
| Funciones de **easing** (`ease_in_cubic`, `ease_out_elastic`…) | ❌ **No existe.** Lo más parecido son las Animation Curves, pero exigen crear un **asset** en el IDE. |
| **Tweening** con líneas de tiempo encadenables | ❌ No existe. |
| **Shake** de cámara | ❌ No existe (`camera_set_*` no trae sacudida). |
| **Object pooling** | ❌ No existe. Crear y destruir instancias es lo único nativo. |
| **Máquina de estados** | ❌ No existe. |
| **Guardado** robusto con *schema* y migración | ❌ Existen `json_stringify`/`json_parse`, pero no la lógica de migración. |
| **Input buffering** | ❌ No existe. |
| Sistema de **diálogo** | ❌ No existe (para eso está Chatterbox, ver archivo 02). |
| **Ruido / Perlin** | ❌ **Confirmado: `gm-cli manual read "noise"` devuelve «No results found».** No hay nada nativo. |

---

## 1. Funciones de easing

**¿Nativo?** No. `animcurve_*` existe pero requiere assets. Estas funciones son puro cálculo, sin dependencias.

```gml
// scripts/ScrEasing/ScrEasing.gml
// Colección de funciones de easing «clásicas» (Robert Penner).
// Todas reciben t en [0, 1] y devuelven un valor (normalmente en [0, 1],
// aunque los «back» y «elastic» pueden salirse un poco del rango).

function ease_linear(_t)
{
    return _t;
}

function ease_in_quad(_t)
{
    return _t * _t;
}

function ease_out_quad(_t)
{
    return _t * (2 - _t);
}

function ease_in_out_quad(_t)
{
    return (_t < 0.5)? 2*_t*_t : -1 + (4 - 2*_t)*_t;
}

function ease_in_cubic(_t)
{
    return _t * _t * _t;
}

function ease_out_cubic(_t)
{
    var _invertido = _t - 1;
    return _invertido * _invertido * _invertido + 1;
}

function ease_in_out_cubic(_t)
{
    return (_t < 0.5)? 4*_t*_t*_t : 1 - power(-2*_t + 2, 3)/2;
}

function ease_out_back(_t)
{
    var _rebote = 1.70158;              // constante que controla el «rebote»
    var _invertido = _t - 1;
    return 1 + (_rebote + 1)*power(_invertido, 3) + _rebote*power(_invertido, 2);
}

function ease_out_elastic(_t)
{
    var _periodo = 0.3;
    var _amplitud = 1;
    if (_t == 0) return 0;
    if (_t == 1) return 1;
    var _s = _periodo / (2*pi) * arcsin(1/_amplitud);
    return _amplitud * power(2, -10*_t) * sin((_t - _s)*(2*pi)/_periodo) + 1;
}

function ease_out_bounce(_t)
{
    // Rebote por tramos, como una pelota que cae
    var _n1 = 7.5625;
    var _d1 = 2.75;

    if (_t < 1/_d1)
    {
        return _n1 * _t * _t;
    }
    else if (_t < 2/_d1)
    {
        var _t2 = _t - 1.5/_d1;
        return _n1 * _t2 * _t2 + 0.75;
    }
    else if (_t < 2.5/_d1)
    {
        var _t3 = _t - 2.25/_d1;
        return _n1 * _t3 * _t3 + 0.9375;
    }
    else
    {
        var _t4 = _t - 2.625/_d1;
        return _n1 * _t4 * _t4 + 0.984375;
    }
}

/// Aplica una función de easing para interpolar de _origen a _destino.
/// Usa lerp(), que SÍ es nativo de GameMaker.
/// @param {Real} _origen
/// @param {Real} _destino
/// @param {Real} _progreso   Valor entre 0 y 1
/// @param {Function} _easing  Una de las funciones de arriba
function ease_lerp(_origen, _destino, _progreso, _easing)
{
    return lerp(_origen, _destino, _easing(clamp(_progreso, 0, 1)));
}
```

```gml
// Uso
var _x_suavizado = ease_lerp(x_inicial, x_final, 0.25, ease_out_cubic);
```

---

## 2. Sistema de tweens

**¿Nativo?** No. GameMaker trae *Time Sources* (`time_source_create`, `call_later`…), pero no un *tween* con easing encadenable.

```gml
// scripts/Tween/Tween.gml
// Tween mínimo pero completo: anima un valor con easing y devuelve el progreso.

function Tween(_duracion, _easing) constructor
{
    duracion  = _duracion;                         // en frames
    easing    = _easing ?? ease_linear;            // ?? = operador de coalescencia nula
    tiempo    = 0;
    activo    = false;
    bucle     = false;
    alFinal   = undefined;                         // callback opcional

    /// Inicia (o reinicia) el tween desde cero
    static Empezar = function()
    {
        tiempo = 0;
        activo = true;
        return self;
    }

    /// Avanza un frame y devuelve el valor interpolado (0..1 ya con easing)
    static Actualizar = function()
    {
        if (!activo) return 1;

        tiempo += 1;
        var _crudo = tiempo / duracion;

        if (_crudo >= 1)
        {
            if (bucle)
            {
                tiempo = 0;
                _crudo = 0;
            }
            else
            {
                activo = false;
                _crudo = 1;
                if (is_method(alFinal)) alFinal();
            }
        }

        return easing(clamp(_crudo, 0, 1));
    }

    /// Devuelve el progreso interpolado entre dos valores
    static Valor = function(_origen, _destino)
    {
        return lerp(_origen, _destino, Actualizar());
    }
}
```

```gml
// obj_logo · Create
tween_aparicion = new Tween(45, ease_out_back);   // 45 frames (0,75 s a 60 fps)
tween_aparicion.Empezar();

// obj_logo · Step
escala = tween_aparicion.Valor(0, 1);

// obj_logo · Draw
draw_sprite_ext(spr_logo, 0, x, y, escala, escala, 0, c_white, 1);
```

---

## 3. Rejilla (grid) con structs

**¿Nativo?** Sí, `ds_grid_*`. **Por qué la versión propia:** los `ds_grid` exigen gestionar la memoria a mano (`ds_grid_destroy`) y son índices opacos que no se serializan con `json_stringify`. Esta versión usa un array 2D dentro de un struct, se guarda sola y no tiene fugas.

```gml
// scripts/Rejilla/Rejilla.gml

function Rejilla(_ancho, _alto, _valorInicial = 0) constructor
{
    ancho = _ancho;
    alto  = _alto;
    celdas = array_create(_ancho*_alto, _valorInicial);

    /// Índice interno (una sola dimensión) a partir de columna y fila
    static __Indice = function(_cx, _cy)
    {
        return _cy * ancho + _cx;
    }

    static Obtener = function(_cx, _cy)
    {
        if ((_cx < 0) || (_cy < 0) || (_cx >= ancho) || (_cy >= alto)) return undefined;
        return celdas[__Indice(_cx, _cy)];
    }

    static Colocar = function(_cx, _cy, _valor)
    {
        if ((_cx < 0) || (_cy < 0) || (_cx >= ancho) || (_cy >= alto)) return false;
        celdas[@ __Indice(_cx, _cy)] = _valor;   // [@...] modifica el array «in situ»
        return true;
    }

    /// Ejecuta una función por cada celda: funcion(valor, cx, cy)
    static PorCada = function(_funcion)
    {
        for (var _cy = 0; _cy < alto; _cy++)
        {
            for (var _cx = 0; _cx < ancho; _cx++)
            {
                _funcion(Obtener(_cx, _cy), _cx, _cy);
            }
        }
    }

    /// Vecinos en las 4 direcciones cardinales (sin diagonales)
    static Vecinos4 = function(_cx, _cy)
    {
        var _resultado = [];
        var _dir = [[1,0],[-1,0],[0,1],[0,-1]];
        for (var _i = 0; _i < 4; _i++)
        {
            var _nx = _cx + _dir[_i][0];
            var _ny = _cy + _dir[_i][1];
            if ((_nx >= 0) && (_ny >= 0) && (_nx < ancho) && (_ny < alto))
            {
                array_push(_resultado, [_nx, _ny]);
            }
        }
        return _resultado;
    }

    /// Vecinos en las 8 direcciones (con diagonales)
    static Vecinos8 = function(_cx, _cy)
    {
        var _resultado = [];
        for (var _dy = -1; _dy <= 1; _dy++)
        {
            for (var _dx = -1; _dx <= 1; _dx++)
            {
                if ((_dx == 0) && (_dy == 0)) continue;
                var _nx = _cx + _dx;
                var _ny = _cy + _dy;
                if ((_nx >= 0) && (_ny >= 0) && (_nx < ancho) && (_ny < alto))
                {
                    array_push(_resultado, [_nx, _ny]);
                }
            }
        }
        return _resultado;
    }

    /// Rellena toda la rejilla con un valor
    static Rellenar = function(_valor)
    {
        array_resize(celdas, 0);
        array_resize(celdas, ancho*alto);
        var _i = 0;
        repeat(ancho*alto)
        {
            celdas[@ _i] = _valor;
            _i++;
        }
    }
}
```

```gml
// Uso
rejilla = new Rejilla(64, 48, 0);
rejilla.Colocar(10, 10, 1);
show_debug_message(rejilla.Obtener(10, 10));   // -> 1
show_debug_message(array_length(rejilla.Vecinos8(10, 10)));  // -> 8
```

---

## 4. Pathfinding A*

**¿Nativo?** Sí, `mp_grid_path()`. **Por qué la versión propia:** `mp_grid_path` te obliga a crear un **asset de tipo path** y no te deja elegir la heurística ni aplicar costes por celda (barro, carretera…). Esta versión devuelve un array de puntos directamente.

```gml
// scripts/AEstrella/AEstrella.gml
// A* sobre una rejilla. Usa ds_priority_create() (nativo) como cola abierta.
// _esTransitable(cx, cy) -> true/false
// _coste(cx, cy)         -> coste de entrar en la celda (por defecto 1)

function AEstrella(_rejilla, _inicio, _destino, _esTransitable, _coste = undefined)
{
    var _ancho = _rejilla.ancho;
    var _alto  = _rejilla.alto;

    // Si no se pasa función de coste, todas las celdas valen 1
    var _fnCoste = is_method(_coste)? _coste : function(_cx, _cy) { return 1; };

    var _total = _ancho * _alto;

    // Mapas de trabajo. Se indexan con cy*ancho+cx
    var _gCoste = array_create(_total, infinity);
    var _padre  = array_create(_total, -1);
    var _cerrado = array_create(_total, false);

    var _indice = function(_cx, _cy) { return _cy * _ancho + _cx; };

    var _iInicio  = _indice(_inicio[0],  _inicio[1]);
    var _iDestino = _indice(_destino[0], _destino[1]);

    _gCoste[_iInicio] = 0;

    // Cola de prioridad: prioridad MÁS BAJA primero (por eso insertamos la f negativa)
    var _abierta = ds_priority_create();
    ds_priority_add(_abierta, _iInicio, 0);

    // Heurística: distancia de Manhattan (4 direcciones). Para 8 direcciones usa la octil.
    var _heuristica = function(_cx, _cy)
    {
        return abs(_cx - _destino[0]) + abs(_cy - _destino[1]);
    };

    while (!ds_priority_empty(_abierta))
    {
        var _actual = ds_priority_delete_min(_abierta);

        if (_actual == _iDestino)
        {
            // Reconstruimos el camino tirando de padres
            var _camino = [];
            var _nodo = _actual;
            while (_nodo != -1)
            {
                array_push(_camino, [_nodo mod _ancho, _nodo div _ancho]);
                _nodo = _padre[_nodo];
            }
            array_reverse(_camino);      // invertir: del inicio al destino
            ds_priority_destroy(_abierta);
            return _camino;
        }

        if (_cerrado[_actual]) continue;
        _cerrado[@ _actual] = true;

        var _cx = _actual mod _ancho;
        var _cy = _actual div _ancho;

        var _vecinos = _rejilla.Vecinos4(_cx, _cy);
        for (var _i = 0; _i < array_length(_vecinos); _i++)
        {
            var _nx = _vecinos[_i][0];
            var _ny = _vecinos[_i][1];

            if (!_esTransitable(_nx, _ny)) continue;

            var _iVecino = _indice(_nx, _ny);
            if (_cerrado[_iVecino]) continue;

            var _gTentativo = _gCoste[_actual] + _fnCoste(_nx, _ny);

            if (_gTentativo < _gCoste[_iVecino])
            {
                _padre[@  _iVecino] = _actual;
                _gCoste[@ _iVecino] = _gTentativo;

                var _f = _gTentativo + _heuristica(_nx, _ny);
                ds_priority_add(_abierta, _iVecino, _f);
            }
        }
    }

    // No hay camino posible
    ds_priority_destroy(_abierta);
    return [];
}
```

```gml
// Uso
var _esSuelo = function(_cx, _cy) { return rejilla.Obtener(_cx, _cy) != 1; };
var _coste   = function(_cx, _cy) { return (rejilla.Obtener(_cx, _cy) == 2)? 5 : 1; }; // barro = 5

var _ruta = AEstrella(rejilla, [0, 0], [30, 20], _esSuelo, _coste);

if (array_length(_ruta) > 0)
{
    var _primerPaso = _ruta[1];          // _ruta[0] es la propia casilla de inicio
    objetivo_x = _primerPaso[0] * 32;
    objetivo_y = _primerPaso[1] * 32;
}
```

> ⚠️ **No olvides `ds_priority_destroy()`**. Las estructuras de datos de GameMaker no se liberan solas y una fuga aquí se nota enseguida.

---

## 5. Máquina de estados con structs

**¿Nativo?** No. Es el patrón más útil de GameMaker y no viene de serie.

```gml
// scripts/MaquinaEstados/MaquinaEstados.gml

function MaquinaEstados(_propietario) constructor
{
    dueno         = _propietario;      // la instancia a la que pertenece
    estadoActual  = undefined;
    estados       = {};                // struct: nombre -> struct con .Entrar/.Actualizar/.Salir

    /// Registra un estado. _ciclo es un struct con Entrar, Actualizar y Salir (opcionales)
    static Anadir = function(_nombre, _ciclo)
    {
        estados[$ _nombre] = _ciclo;
        return self;
    }

    /// Cambia de estado ejecutando Salir del viejo y Entrar del nuevo
    static Cambiar = function(_nombre)
    {
        if (estadoActual == _nombre) return false;
        if (!variable_struct_exists(estados, _nombre))
        {
            show_debug_message("Estado inexistente: " + _nombre);
            return false;
        }

        var _viejo = (estadoActual == undefined)? undefined : estados[$ estadoActual];
        if (is_struct(_viejo) && is_method(_viejo[$ "Salir"])) _viejo.Salir(dueno);

        estadoActual = _nombre;
        var _nuevo = estados[$ _nombre];
        if (is_method(_nuevo[$ "Entrar"])) _nuevo.Entrar(dueno);

        return true;
    }

    /// Llama a esto en el Step de la instancia
    static Actualizar = function()
    {
        if (estadoActual == undefined) return;
        var _estado = estados[$ estadoActual];
        if (is_method(_estado[$ "Actualizar"])) _estado.Actualizar(dueno);
    }
}
```

```gml
// obj_enemigo · Create
fsm = new MaquinaEstados(id);

fsm.Anadir("patrullar", {
    Entrar: function(_yo) { _yo.velocidad = 1; },
    Actualizar: function(_yo)
    {
        x += _yo.velocidad;
        if (distance_to_object(obj_jugador) < 120) _yo.fsm.Cambiar("perseguir");
    },
    Salir: function(_yo) { show_debug_message("Dejo de patrullar"); }
});

fsm.Anadir("perseguir", {
    Entrar: function(_yo) { _yo.velocidad = 3; },
    Actualizar: function(_yo)
    {
        move_towards_point(obj_jugador.x, obj_jugador.y, _yo.velocidad);
        if (distance_to_object(obj_jugador) > 250) _yo.fsm.Cambiar("patrullar");
    }
});

fsm.Cambiar("patrullar");
```

```gml
// obj_enemigo · Step
fsm.Actualizar();
```

---

## 6. Object pooling

**¿Nativo?** No. `instance_create_layer()` crea y `instance_destroy()` destruye, con el coste de ejecutar el evento Create cada vez.

```gml
// scripts/Pool/Pool.gml
// Pool de instancias reutilizables. En vez de destruir, se desactivan.

function Pool(_objeto, _capa, _tamanoInicial = 16) constructor
{
    objeto  = _objeto;
    capa    = _capa;
    libres  = [];
    activos = [];

    // Precalienta el pool
    repeat(_tamanoInicial)
    {
        var _instancia = instance_create_layer(0, 0, capa, objeto);
        _instancia.visible = false;
        instance_deactivate_object(_instancia);
        array_push(libres, _instancia);
    }

    /// Saca una instancia del pool (o la crea si no quedan libres)
    static Obtener = function(_x, _y)
    {
        var _instancia;

        if (array_length(libres) > 0)
        {
            _instancia = array_pop(libres);
            instance_activate_object(_instancia);
        }
        else
        {
            // El pool se ha quedado corto: crecer es mejor que fallar
            _instancia = instance_create_layer(_x, _y, capa, objeto);
        }

        _instancia.x = _x;
        _instancia.y = _y;
        _instancia.visible = true;

        // Si la instancia define OnReutilizar(), la llamamos para resetear su estado
        if (is_method(_instancia[$ "OnReutilizar"])) _instancia.OnReutilizar();

        array_push(activos, _instancia);
        return _instancia;
    }

    /// Devuelve una instancia al pool
    static Devolver = function(_instancia)
    {
        if (_instancia == undefined) return false;

        var _pos = array_get_index(activos, _instancia);
        if (_pos == -1) return false;

        array_delete(activos, _pos, 1);

        _instancia.visible = false;
        instance_deactivate_object(_instancia);
        array_push(libres, _instancia);

        return true;
    }

    /// Devuelve todas las instancias activas
    static DevolverTodas = function()
    {
        while (array_length(activos) > 0)
        {
            Devolver(array_pop(activos));
        }
    }

    /// Limpieza: destruye de verdad. Llamar al salir de la room.
    static Destruir = function()
    {
        DevolverTodas();
        var _i = 0;
        repeat(array_length(libres))
        {
            var _instancia = libres[_i];
            instance_activate_object(_instancia);
            instance_destroy(_instancia);
            _i++;
        }
        array_resize(libres, 0);
    }
}
```

```gml
// obj_controlador · Create
pool_balas = new Pool(obj_bala, "Instances", 64);

// obj_jugador · Step (disparar)
var _bala = obj_controlador.pool_balas.Obtener(x, y);
_bala.direccion = point_direction(x, y, mouse_x, mouse_y);

// obj_bala · cuando debe desaparecer
obj_controlador.pool_balas.Devolver(id);

// obj_controlador · Room End / Clean Up
pool_balas.Destruir();
```

> ⚠️ **Obligatorio implementar `OnReutilizar()`** en el objeto pooled para resetear vida, velocidad, temporizadores… Si no, te reutiliza una bala «muerta».

---

## 7. Cámara con shake

**¿Nativo?** Las cámaras sí (`camera_create`, `camera_set_view_pos`…); el **shake**, no.

```gml
// scripts/CamaraShake/CamaraShake.gml

function CamaraShake() constructor
{
    magnitud     = 0;      // intensidad actual del temblor en píxeles
    decaimiento  = 0.9;    // cuánto se reduce cada frame (0..1)
    semillaX     = 0;
    semillaY     = 0;
    desplazX     = 0;
    desplazY     = 0;

    /// Dispara un temblor. Si ya había uno, se queda el mayor.
    static Sacudir = function(_magnitud, _decaimiento = 0.9)
    {
        magnitud    = max(magnitud, _magnitud);
        decaimiento = _decaimiento;
        semillaX    = random(1000);
        semillaY    = random(1000);
    }

    /// Llamar en el Step ANTES de posicionar la cámara.
    /// Devuelve el desplazamiento a aplicar como array [x, y].
    static Actualizar = function()
    {
        if (magnitud <= 0.1)
        {
            magnitud = 0;
            desplazX = 0;
            desplazY = 0;
            return [0, 0];
        }

        // Ruido aleatorio suave: avanzamos la semilla para que no salte frame a frame
        semillaX += 0.5;
        semillaY += 0.5;

        desplazX = (random(2) - 1) * magnitud;
        desplazY = (random(2) - 1) * magnitud;

        magnitud *= decaimiento;

        return [desplazX, desplazY];
    }
}
```

```gml
// obj_camara · Create
camara = camera_create_view(0, 0, 640, 360, 0, obj_jugador, -1, -1, 320, 180);
view_set_camera(0, camara);
shake = new CamaraShake();

// obj_camara · Step (o Step End, para que el jugador ya se haya movido)
var _desplaz = shake.Actualizar();

camera_set_view_pos(camara,
                    obj_jugador.x - camera_get_view_width(camara)/2  + _desplaz[0],
                    obj_jugador.y - camera_get_view_height(camara)/2 + _desplaz[1]);

// En cualquier sitio: sacudir al recibir un golpe
obj_camara.shake.Sacudir(8, 0.85);
```

> 💡 **Variante con ruido Perlin** en vez de `random()`: sustituye el cálculo por la función `ruido_perlin()` de la sección 11 para un temblor más «orgánico» y menos nervioso.

---

## 8. Guardado y carga con structs

**¿Nativo?** `json_stringify()` y `json_parse()` sí; la lógica de **versionado y migración**, no.

```gml
// scripts/Guardado/Guardado.gml
// Guardado robusto: versión del esquema + migración + escritura atómica.

#macro VERSION_GUARDADO 2
#macro RUTA_GUARDADO   "guardado.json"

/// Estructura por defecto de una partida nueva
function GuardadoPorDefecto()
{
    return {
        version: VERSION_GUARDADO,
        nombre:  "Jugador",
        nivel:   1,
        vida:    100,
        inventario: [],
        opciones: {
            musica: 1,
            efectos: 1
        }
    };
}

/// Migra los datos de una versión antigua del esquema a la actual
function GuardadoMigrar(_datos)
{
    var _version = _datos[$ "version"] ?? 1;

    // v1 -> v2: se añadió el bloque "opciones"
    if (_version < 2)
    {
        if (!variable_struct_exists(_datos, "opciones"))
        {
            _datos.opciones = { musica: 1, efectos: 1 };
        }
        _datos.version = 2;
    }

    // Futuras migraciones van aquí: if (_version < 3) { ... }

    return _datos;
}

/// Guarda la partida. Devuelve true si ha ido bien.
function GuardadoGuardar()
{
    var _datos = GuardadoPorDefecto();

    // Rellenamos con el estado real del juego
    _datos.nombre = global.nombre_jugador;
    _datos.nivel  = global.nivel_actual;
    _datos.vida   = obj_jugador.vida;
    _datos.opciones.musica = global.volumen_musica;

    var _json = json_stringify(_datos);

    // Escritura atómica: escribimos en un fichero temporal y luego renombramos.
    // Así, si el juego se cierra a media escritura, no corruptemos el guardado bueno.
    var _temporal = RUTA_GUARDADO + ".tmp";

    var _buffer = buffer_create(string_byte_length(_json) + 1, buffer_fixed, 1);
    buffer_write(_buffer, buffer_string, _json);
    buffer_save(_buffer, _temporal);
    buffer_delete(_buffer);

    // Si existía un guardado anterior, lo borramos y movemos el temporal
    if (file_exists(RUTA_GUARDADO)) file_delete(RUTA_GUARDADO);
    file_rename(_temporal, RUTA_GUARDADO);

    return true;
}

/// Carga la partida. Devuelve un struct, o los datos por defecto si no hay fichero.
function GuardadoCargar()
{
    if (!file_exists(RUTA_GUARDADO)) return GuardadoPorDefecto();

    var _buffer = buffer_load(RUTA_GUARDADO);
    var _json   = buffer_read(_buffer, buffer_string);
    buffer_delete(_buffer);

    var _datos = json_parse(_json);

    // Si el JSON era basura, json_parse devuelve undefined
    if (!is_struct(_datos))
    {
        show_debug_message("Guardado corrupto, se empieza de cero");
        return GuardadoPorDefecto();
    }

    return GuardadoMigrar(_datos);
}

/// Borra la partida guardada
function GuardadoBorrar()
{
    if (file_exists(RUTA_GUARDADO)) file_delete(RUTA_GUARDADO);
    if (file_exists(RUTA_GUARDADO + ".tmp")) file_delete(RUTA_GUARDADO + ".tmp");
}
```

```gml
// Uso
var _partida = GuardadoCargar();
global.nivel_actual = _partida.nivel;      // lee el nivel
// ...
GuardadoGuardar();                          // escribe
```

> ⚠️ **Nunca guardes referencias a assets** (sprites, rooms, sonidos) con `json_stringify`: se guarda como índice numérico que cambia entre ejecuciones. Guarda el **nombre** con `room_get_name()` y recupéralo con `asset_get_index()`.

---

## 9. Input buffering

**¿Nativo?** No. Es la técnica que hace que el jugador sienta que el juego «le hace caso»: si pulsa *saltar* 3 frames antes de tocar el suelo, el salto se ejecuta igual.

```gml
// scripts/InputBuffer/InputBuffer.gml
// Buffer de entrada: recuerda CUÁNDO se pulsó una tecla para poder
// consumirla dentro de una ventana de tiempo.

function InputBuffer() constructor
{
    buffer       = {};     // nombre de la acción -> frame en que se pulsó
    ventana      = 8;      // frames de gracia
    frameActual  = 0;

    /// Llamar en el Step, ANTES de leer nada
    static Actualizar = function()
    {
        frameActual += 1;
    }

    /// Registra una pulsación
    static Pulsar = function(_accion)
    {
        buffer[$ _accion] = frameActual;
    }

    /// ¿Se pulsó la acción dentro de la ventana de gracia? (no consume)
    static Disponible = function(_accion, _ventana = undefined)
    {
        var _v = (_ventana == undefined)? ventana : _ventana;
        var _frame = buffer[$ _accion];
        if (_frame == undefined) return false;
        return ((frameActual - _frame) <= _v);
    }

    /// Consume la acción: devuelve true una sola vez y la borra
    static Consumir = function(_accion, _ventana = undefined)
    {
        if (!Disponible(_accion, _ventana)) return false;
        variable_struct_remove(buffer, _accion);
        return true;
    }

    /// Limpia todo el buffer (útil al pausar o cambiar de room)
    static Limpiar = function()
    {
        var _claves = struct_get_names(buffer);
        var _i = 0;
        repeat(array_length(_claves))
        {
            variable_struct_remove(buffer, _claves[_i]);
            _i++;
        }
    }
}
```

```gml
// obj_jugador · Create
entrada = new InputBuffer();
entrada.ventana = 6;      // 6 frames = 100 ms a 60fps

// obj_jugador · Step (Begin Step, para registrar la pulsación lo antes posible)
entrada.Actualizar();

if (keyboard_check_pressed(vk_space)) entrada.Pulsar("saltar");
if (mouse_check_button_pressed(mb_left)) entrada.Pulsar("atacar");

// obj_jugador · Step (lógica de movimiento)
var _en_suelo = place_meeting(x, y + 1, obj_suelo);

// Aunque el jugador pulsase ANTES de aterrizar, el salto sale
if (entrada.Consumir("saltar") && _en_suelo)
{
    velocidad_vertical = -12;
}
```

---

## 10. Sistema de diálogo simple

**¿Nativo?** No. Para algo serio usa **Chatterbox** (ver archivo 02). Esta versión es para cuando necesitas 20 líneas y nada más.

```gml
// scripts/Dialogo/Dialogo.gml
// Diálogo lineal con efecto de máquina de escribir.

function Dialogo() constructor
{
    lineas      = [];       // array de structs {texto, orador}
    indice      = 0;        // línea actual
    caracteres  = 0;        // cuántos caracteres se muestran
    velocidad   = 0.6;      // caracteres por frame
    activo      = false;

    /// Carga un array de líneas: [{texto:"...", orador:"..."}, ...]
    static Cargar = function(_lineas)
    {
        lineas     = _lineas;
        indice     = 0;
        caracteres = 0;
        activo     = true;
    }

    /// Avanza. Si la línea se está escribiendo, la completa de golpe.
    static Avanzar = function()
    {
        if (!activo) return false;

        var _linea = lineas[indice];
        if (caracteres < string_length(_linea.texto))
        {
            caracteres = string_length(_linea.texto);   // mostrar todo de golpe
            return false;
        }

        indice += 1;
        caracteres = 0;

        if (indice >= array_length(lineas))
        {
            Cerrar();
        }
        return true;
    }

    static Cerrar = function()
    {
        activo     = false;
        indice     = 0;
        caracteres = 0;
    }

    /// Llamar cada frame
    static Actualizar = function()
    {
        if (!activo) return;
        var _total = string_length(lineas[indice].texto);
        if (caracteres < _total) caracteres += velocidad;
    }

    /// Devuelve el texto visible ahora mismo (recortado)
    static TextoVisible = function()
    {
        if (!activo) return "";
        return string_copy(lineas[indice].texto, 1, floor(caracteres));
    }

    /// Devuelve el orador de la línea actual (o "" si no tiene)
    static Orador = function()
    {
        if (!activo) return "";
        return lineas[indice][$ "orador"] ?? "";
    }

    /// ¿Se ha terminado de escribir la línea? (para mostrar el icono «continuar»)
    static HaTerminado = function()
    {
        if (!activo) return true;
        return (caracteres >= string_length(lineas[indice].texto));
    }
}
```

```gml
// obj_npc · Create
dialogo = new Dialogo();
dialogo.Cargar([
    { orador: "Aldeano", texto: "¡Eh, tú! Ten cuidado con el bosque." },
    { orador: "Aldeano", texto: "Dicen que algo acecha entre los árboles." },
    { orador: "Aldeano", texto: "Yo no iría de noche." }
]);

// obj_npc · Step
if (keyboard_check_pressed(vk_space)) dialogo.Avanzar();

// obj_npc · Draw GUI
if (dialogo.activo)
{
    draw_set_font(fnt_dialogo);
    draw_rectangle(32, 320, 608, 430, false);
    draw_set_color(c_white);
    draw_text(48, 336, dialogo.Orador());
    draw_text_ext(48, 366, dialogo.TextoVisible(), 16, 520);

    if (dialogo.HaTerminado())
    {
        draw_text(520, 410, "▼");   // indicador de «pulsa para continuar»
    }
}
```

---

## 11. Ruido Perlin

**¿Nativo? NO.** Verificado con `gm-cli manual read "noise"` → *«No results found»*. GameMaker no trae ninguna función de ruido.

```gml
// scripts/Ruido/Ruido.gml
// Ruido Perlin 1D y 2D con semilla, sin dependencias.
// Implementación clásica: rejilla de gradientes + interpolación suave.

/// Inicializa la tabla de permutaciones con una semilla.
/// Llamar una sola vez al arrancar el juego.
function RuidoInicializar(_semilla = 1337)
{
    random_set_seed(_semilla);

    global.ruido_p = array_create(512);
    var _permutacion = array_create(256);

    var _i = 0;
    repeat(256)
    {
        _permutacion[@ _i] = _i;
        _i++;
    }

    // Barajado de Fisher-Yates
    for (var _j = 255; _j > 0; _j--)
    {
        var _k = irandom(_j);
        var _tmp = _permutacion[_j];
        _permutacion[@ _j] = _permutacion[_k];
        _permutacion[@ _k] = _tmp;
    }

    // Duplicamos la tabla para no tener que hacer módulo todo el rato
    _i = 0;
    repeat(512)
    {
        global.ruido_p[@ _i] = _permutacion[_i mod 256];
        _i++;
    }
}

/// Curva de suavizado (fade) de Perlin: 6t⁵ - 15t⁴ + 10t³
function __ruido_fade(_t)
{
    return _t * _t * _t * (_t * (_t * 6 - 15) + 10);
}

/// Producto escalar del gradiente 2D
function __ruido_gradiente(_hash, _x, _y)
{
    switch (_hash mod 4)
    {
        case 0: return  _x + _y;   // gradiente (1, 1)
        case 1: return -_x + _y;   // gradiente (-1, 1)
        case 2: return  _x - _y;   // gradiente (1, -1)
        default: return -_x - _y;  // gradiente (-1, -1)
    }
}

/// Ruido Perlin 2D. Devuelve un valor aproximadamente en [-1, 1].
function ruido_perlin(_x, _y)
{
    var _xi = floor(_x) & 255;
    var _yi = floor(_y) & 255;

    var _xf = _x - floor(_x);
    var _yf = _y - floor(_y);

    var _u = __ruido_fade(_xf);
    var _v = __ruido_fade(_yf);

    var _p = global.ruido_p;

    var _aa = _p[_p[_xi]     + _yi];
    var _ab = _p[_p[_xi]     + _yi + 1];
    var _ba = _p[_p[_xi + 1] + _yi];
    var _bb = _p[_p[_xi + 1] + _yi + 1];

    var _x1 = lerp(__ruido_gradiente(_aa, _xf,     _yf),
                   __ruido_gradiente(_ba, _xf - 1, _yf), _u);

    var _x2 = lerp(__ruido_gradiente(_ab, _xf,     _yf - 1),
                   __ruido_gradiente(_bb, _xf - 1, _yf - 1), _u);

    return lerp(_x1, _x2, _v);
}

/// Ruido fractal (fBm): suma varias «octavas» de Perlin.
/// _octavas      cuántas capas se acumulan
/// _persistencia cuánto baja la amplitud en cada capa (típicamente 0.5)
/// _lacunaridad  cuánto sube la frecuencia en cada capa (típicamente 2.0)
function ruido_fractal(_x, _y, _octavas = 4, _persistencia = 0.5, _lacunaridad = 2.0)
{
    var _total      = 0;
    var _frecuencia = 1;
    var _amplitud   = 1;
    var _maximo     = 0;

    var _i = 0;
    repeat(_octavas)
    {
        _total      += ruido_perlin(_x*_frecuencia, _y*_frecuencia) * _amplitud;
        _maximo     += _amplitud;
        _amplitud   *= _persistencia;
        _frecuencia *= _lacunaridad;
        _i++;
    }

    return _total / _maximo;   // normalizado a [-1, 1]
}
```

```gml
// obj_generador · Create
RuidoInicializar(1234);
var _ancho = 128;
var _alto  = 128;

for (var _cy = 0; _cy < _alto; _cy++)
{
    for (var _cx = 0; _cx < _ancho; _cx++)
    {
        // Ruido a escala y lo convertimos a 0..1
        var _n = (ruido_fractal(_cx * 0.05, _cy * 0.05) + 1) / 2;

        if (_n < 0.35)      rejilla.Colocar(_cx, _cy, 0);   // agua
        else if (_n < 0.45) rejilla.Colocar(_cx, _cy, 1);   // arena
        else if (_n < 0.75) rejilla.Colocar(_cx, _cy, 2);   // hierba
        else                rejilla.Colocar(_cx, _cy, 3);   // montaña
    }
}
```

---

## 12. Utilidades de tilemap

**¿Nativo?** `tilemap_get()` y `tilemap_set()` existen, pero devuelven/manipulan **datos en crudo** (índice de tile + flags de rotación y volteo). Estas envolturas hacen el código legible.

```gml
// scripts/TilemapUtil/TilemapUtil.gml

/// Devuelve el ID del tilemap de una capa, o undefined si no existe.
function capa_tilemap(_nombreCapa)
{
    var _capa = layer_get_id(_nombreCapa);
    if (_capa == -1) return undefined;

    var _tilemap = layer_tilemap_get_id(_capa);
    if (_tilemap < 0) return undefined;

    return _tilemap;
}

/// Índice de tile «limpio» (sin flags de volteo ni rotación) en una celda.
function tile_indice(_tilemap, _cx, _cy)
{
    if (_tilemap == undefined) return 0;
    var _dato = tilemap_get(_tilemap, _cx, _cy);
    return _dato & tile_index_mask;      // tile_index_mask es constante nativa
}

/// Coloca un tile sin flags, en una celda.
function tile_colocar(_tilemap, _indice, _cx, _cy)
{
    if (_tilemap == undefined) return false;

    var _ancho = tilemap_get_width(_tilemap);
    var _alto  = tilemap_get_height(_tilemap);
    if ((_cx < 0) || (_cy < 0) || (_cx >= _ancho) || (_cy >= _alto)) return false;

    tilemap_set(_tilemap, _indice, _cx, _cy);
    return true;
}

/// ¿Es este tile sólido? _solidos es un array de índices considerados sólidos.
function tile_es_solido(_tilemap, _cx, _cy, _solidos)
{
    var _indice = tile_indice(_tilemap, _cx, _cy);
    return (array_get_index(_solidos, _indice) != -1);
}

/// Conversión de píxeles de la room a celda del tilemap
function pixeles_a_celda(_tilemap, _px, _py)
{
    var _tam = tilemap_get_tile_width(_tilemap);   // asume tiles cuadrados
    return [floor(_px / _tam), floor(_py / _tam)];
}

/// Conversión de celda a píxeles (esquina superior izquierda)
function celda_a_pixeles(_tilemap, _cx, _cy)
{
    var _tam = tilemap_get_tile_width(_tilemap);
    return [_cx * _tam, _cy * _tam];
}

/// Rellena un rectángulo de celdas con un tile
function tile_rellenar_rectangulo(_tilemap, _indice, _x1, _y1, _x2, _y2)
{
    for (var _cy = _y1; _cy <= _y2; _cy++)
    {
        for (var _cx = _x1; _cx <= _x2; _cx++)
        {
            tile_colocar(_tilemap, _indice, _cx, _cy);
        }
    }
}
```

```gml
// obj_nivel · Create
tilemap_suelo = capa_tilemap("Tiles_Suelo");
var _solidos = [1, 2, 3, 4];

// obj_jugador · Step — colisión simple contra el tilemap
var _celda = pixeles_a_celda(obj_nivel.tilemap_suelo, x, y + 16);
if (tile_es_solido(obj_nivel.tilemap_suelo, _celda[0], _celda[1], _solidos))
{
    en_suelo = true;
}
```

---

## 13. Checklist: antes de copiar cualquier script

1. **¿Ya existe nativamente?** Consulta `gm-cli manual read "<función>"`. Es rapidísimo y evita duplicar lógica.
2. **¿Libera memoria?** Todo `ds_*`, `buffer_*`, `surface_*` y `camera_create` necesita su `*_destroy` / `*_free` / `*_delete`.
3. **¿Usa nombres reservados?** Evita `speed`, `direction`, `id`, `depth`, `score`, `health`, `gravity`. Prefija los locales con `_`.
4. **¿Convenciones GML?** `snake_case` para todo, `obj_`/`spr_`/`scr_`/`rm_` como prefijos de recurso.
5. **¿Funciona en GMRT?** Si estás probando el runtime nuevo, recuerda que está en beta y el depurador es limitado.
