# 07 · Generación procedural avanzada

> Este documento es la **caja de herramientas de PCG que no cabe en un roguelike**: ruido,
> autómatas celulares, Poisson-disc, Wave Function Collapse, gramáticas, ensamblaje por
> piezas y niveles de plataformas por ritmo. Todo con GML verificado contra el runtime
> 2026.0.0.23.
>
> **Lo que NO cubre porque ya está resuelto:** RNG con semilla, BSP, random walk, validación
> por flood fill y tablas de botín viven en
> [`04 · 05 — Roguelike y generación procedural`](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md).
> Aquí se **reutiliza** ese código (sobre todo el struct `RNG` de su §5.0) y se construye
> encima. Si vas a generar una mazmorra clásica, empieza por ahí y vuelve.

---

## 1 · Los principios

### 1.1 Determinismo: la semilla es el contenido

Un generador procedural **no guarda mapas: guarda números**. Un save ocupa 500 bytes, un bug se
reproduce escribiendo la semilla, y una *daily run* es idéntica para todos sin servidores.

```gml
randomize();                    // UNA vez, al arrancar el juego
var _semilla = random_get_seed();   // guárdala: es tu partida entera

random_set_seed(_semilla, true);    // ⚠️ el segundo argumento importa (ver abajo)
```

**El segundo argumento de `random_set_seed` no es decorativo.** El manual LTS 2026 dice de
`fix_range_bug`: *«uses an alternate function to set the seed that should ensure a higher range
of the random state… the previous behaviour was erroneous and is only kept for legacy
purposes»*. Sin él usas el sembrado antiguo, **defectuoso**. Pasa siempre `true`.

```gml
random_set_seed(12345, true);   // ✅ sembrado correcto
random_set_seed(12345);         // ⚠️ comportamiento heredado, rango de estado reducido
```

Segunda trampa, también del manual: *«results may vary between platforms due to the different
way each target works»*. **La misma semilla puede dar mundos distintos en Windows y en HTML5.**
Si compartes semillas entre plataformas (*daily runs*, códigos de partida), **no puedes usar el
RNG del motor**.

Ese generador ya existe en esta biblioteca: el struct `RNG` de
[`04 · 05 §5.0`](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md).
**Todo el código de este documento lo usa**, nunca el RNG global. Dos razones:

1. **Aislamiento.** Si el combate consume números aleatorios, la generación del siguiente
   nivel cambia según cuántos golpes diste. Un `RNG` por sistema lo impide.
2. **Portabilidad.** Un LCG escrito en GML da la misma secuencia en todos los objetivos.

> 🔎 **Por qué el LCG de `RNG` es exacto en GML.** Los reales son *double* (53 bits de mantisa).
> El paso `state * 1664525 + 1013904223` con `state < 2^32` da como mucho `7,15 · 10¹⁵`, por
> debajo de `9,007 · 10¹⁵`, el mayor entero exacto. Cabe justo: si subes las constantes,
> **pierdes precisión en silencio** y el generador deja de ser reproducible.

### 1.2 Generar → validar → reparar (o rechazar)

Ningún generador interesante produce siempre resultados jugables. El bucle correcto no es
«generar», es:

```
generar(semilla)  →  medir  →  ¿cumple los criterios?
                                 ├─ sí  → publicar
                                 ├─ reparable → reparar y volver a medir
                                 └─ no  → semilla + 1, reintentar (con tope de intentos)
```

**Reintentar con `semilla + 1`**, no con una semilla al azar: la partida sigue descrita por un
número. Y **siempre un tope**: un generador que no converge debe fallar ruidosamente, no colgar
el juego. Las tres reacciones tienen su sitio:

| Reacción | Cuándo | Coste |
|---|---|---|
| **Rechazar y regenerar** | El fallo es raro (<10 %) y la generación es barata | Simple, cero código extra |
| **Reparar** | El fallo es sistemático (islas desconectadas en un autómata celular) | Medio: un paso más de algoritmo |
| **Restringir** | El fallo se puede impedir por construcción (WFC, gramáticas) | Alto: hay que modelar las reglas |

### 1.3 Separar generación de presentación

Se repite aquí porque es **el error más caro**: el generador produce **datos**, y una capa
aparte los convierte en tilemap, instancias y sprites.

```
GENERADOR (puro)          →  array plano de enteros: celdas[fy * ancho + fx]
PRESENTACIÓN (impuro)     →  tilemap_set(...), instance_create_layer(...)
```

Así puedes generar 1 000 mapas en un test sin abrir una ventana, volcarlos a PNG, serializarlos
a un buffer y cambiar el tileset sin tocar el algoritmo.

> ⚡ **Usa un array plano, no un array de arrays.** `celdas[_fy * ancho + _fx]` evita una
> indirección por acceso. En 256×256 son 65 536 accesos por pasada, y un autómata celular hace
> 8 pasadas. La receta del roguelike usa arrays anidados por legibilidad; para mapas grandes,
> aplana.

> 🕳 **La trampa de `array_create`.** `array_create(alto, array_create(ancho, 0))` crea **una
> sola** fila compartida por referencia en todas las posiciones: cambiar una cambia todas. Es
> un bug silencioso. Usa `array_create_ext(alto, function() { return array_create(ancho, 0); })`
> o, mejor, un array plano. Detalle en
> [`08 · 14 — Arrays`](../08%20-%20Referencia%20GML%20completa/14%20-%20Arrays.md).

### 1.4 El *possibility space* y el control de diseño

Un generador no produce «un nivel»: define el **conjunto de todos los niveles que puede
producir**. Ese conjunto es lo que diseñas, y ante cada parámetro la pregunta no es «¿queda
bonito?» sino **«¿qué añade y qué quita del conjunto?»**.

*Procedural Content Generation in Games* (Shaker, Togelius y Nelson) define PCG como *«the
algorithmic creation of game content with limited or **indirect** user input»*: tú no escribes
el nivel, escribes las **restricciones** que dicen qué niveles son admisibles. De ahí la regla
práctica —**el azar puro casi nunca es diseño**— y cuatro formas de acotar el espacio:

| Técnica | Qué controla | Dónde está en este documento |
|---|---|---|
| **Umbrales sobre ruido** | Proporciones globales (cuánta agua, cuánta roca) | §2.7 |
| **Reglas locales** (autómata) | Forma y textura del espacio | §3 |
| **Restricciones de adyacencia** (WFC) | Qué puede tocar a qué | §5 |
| **Gramáticas** | Estructura jerárquica y orden narrativo | §6 |

### 1.5 Mezclar autor y algoritmo

La proceduralidad convincente **casi nunca es 100 % algorítmica**. *Spelunky* y *The Binding of
Isaac* generan la topología por algoritmo y rellenan las salas con **piezas hechas a mano**: el
algoritmo aporta variedad, el autor aporta intención y momentos memorables.

```
Autor      →  20 salas dibujadas a mano, con puertas etiquetadas
Algoritmo  →  elige 8, las orienta y las conecta según las etiquetas
Autor      →  2 salas fijas obligatorias (inicio y jefe)
```

Es la sección §7. Si solo te llevas una idea de este documento, que sea esta.

---

## 2 · Ruido

### 2.0 GameMaker no tiene ninguna función de ruido. Ninguna.

Esto no es una opinión, es un recuento sobre el `GmlSpec.xml` del runtime instalado:

```sh
python3 "_indice/buscar.py" --listar noise     # → 0 símbolos empiezan por «noise»
python3 "_indice/buscar.py" --todo "perlin"    # → 0 símbolos; solo texto y código de terceros
```

De los **3 486 símbolos** del runtime 2026.0.0.23, **cero** contienen `noise`, `perlin`,
`simplex` o `smooth` en su nombre. Tampoco existe `smoothstep`:

```sh
python3 "_indice/buscar.py" smoothstep
# «smoothstep» NO existe en el runtime 2026.0.0.23.
```

**Conclusión operativa: el ruido lo escribes tú, o lo importas.** Lo que sí tienes es todo lo
necesario para escribirlo: `lerp`, `floor`, `frac`, `clamp`, `power`, `sqrt` y arrays rápidos.

### 2.1 Las dos piezas previas: curva de suavizado y `smoothstep` propio

```gml
// ---------------------------------------------------------------------------
// scr_ruido_base
// ---------------------------------------------------------------------------

/// @func curva_quintica(_t)
/// @desc Curva de suavizado de Ken Perlin (2002): 6t⁵ - 15t⁴ + 10t³.
///       Sustituye a la cúbica clásica 3t² - 2t³, cuya SEGUNDA derivada no es
///       cero en los extremos. Eso produce una discontinuidad de segundo orden
///       que se ve como bandas al iluminar una superficie desplazada por ruido
///       (la normal es una derivada: si la derivada salta, la luz salta).
/// @param {Real} _t  Valor en [0, 1]
/// @return {Real}    Valor suavizado en [0, 1]
function curva_quintica(_t)
{
    return _t * _t * _t * (_t * (_t * 6 - 15) + 10);
}

/// @func curva_cubica(_t)
/// @desc La curva antigua. Más barata, suficiente si NO vas a iluminar el
///       resultado ni a derivarlo. Es el `smoothstep` clásico.
function curva_cubica(_t)
{
    return _t * _t * (3 - 2 * _t);
}

/// @func transicion_suave(_borde0, _borde1, _valor)
/// @desc `smoothstep` de toda la vida. GameMaker NO lo trae: aquí lo tienes.
///       Devuelve 0 por debajo de _borde0, 1 por encima de _borde1, y una
///       transición suave en medio.
function transicion_suave(_borde0, _borde1, _valor)
{
    var _t = clamp((_valor - _borde0) / (_borde1 - _borde0), 0, 1);
    return curva_cubica(_t);
}
```

### 2.2 Value noise: el más simple que sirve

*Value noise* asigna un valor aleatorio a cada punto de una retícula entera e interpola entre
ellos. Es rápido y basta para nubes, texturas y mapas de calor. Su defecto: se le notan los
ejes de la retícula (los máximos y mínimos caen siempre en los vértices).

```gml
// ---------------------------------------------------------------------------
// scr_ruido_valor
// ---------------------------------------------------------------------------

/// @func RuidoValor(_semilla)
/// @desc Value noise 2D con tabla de permutación. Determinista y portable:
///       no toca el RNG global. Reutiliza el struct RNG de 04/05 §5.0.
function RuidoValor(_semilla) constructor
{
    // Tabla de permutación de 512 entradas (256 barajadas, duplicadas).
    // Duplicarlas evita un `mod` por acceso en el bucle caliente.
    var _rng  = new RNG(_semilla);
    var _base = array_create(256, 0);
    for (var _i = 0; _i < 256; _i++) _base[_i] = _i;
    _rng.shuffle(_base);

    perm = array_create(512, 0);
    for (var _i = 0; _i < 512; _i++) perm[_i] = _base[_i mod 256];

    /// @desc Valor pseudoaleatorio y determinista del vértice (_cx, _cy) → [0, 1]
    vertice = function(_cx, _cy)
    {
        var _h = perm[(perm[_cx & 255] + (_cy & 255)) & 255];
        return _h / 255;
    };

    /// @desc Muestra el ruido en un punto continuo. Devuelve [0, 1].
    muestra_01 = function(_px, _py)
    {
        var _x0 = floor(_px);
        var _y0 = floor(_py);
        var _fx = _px - _x0;
        var _fy = _py - _y0;

        var _sx = curva_quintica(_fx);
        var _sy = curva_quintica(_fy);

        var _arriba = lerp(vertice(_x0, _y0),     vertice(_x0 + 1, _y0),     _sx);
        var _abajo  = lerp(vertice(_x0, _y0 + 1), vertice(_x0 + 1, _y0 + 1), _sx);

        return lerp(_arriba, _abajo, _sy);
    };

    /// @desc Igual, remapeado a [-1, 1] para poder sumar octavas simétricas.
    muestra = function(_px, _py)
    {
        return muestra_01(_px, _py) * 2 - 1;
    };
}
```

### 2.3 Perlin: ruido por gradientes

La diferencia con *value noise*: en cada vértice de la retícula no se guarda un **valor**, sino
un **vector gradiente**, y el ruido es el producto escalar del gradiente por el vector que va
del vértice al punto. Resultado: los valores en los vértices son siempre 0 y los extremos caen
**entre** vértices. Se ve mucho menos la retícula.

En *Improving Noise* (SIGGRAPH 2002), Perlin corrigió dos defectos de su algoritmo de 1985: la
curva de interpolación (§2.1) y el **conjunto de gradientes**. En vez de gradientes aleatorios
sobre la esfera —que se agrupan en las direcciones de la rejilla— usó los **12 vectores que van
del centro del cubo a sus 12 aristas**: `(1,1,0)`, `(-1,1,0)`, … En 2D el equivalente son las
**4 diagonales**, todas de la misma longitud, normalizadas a 1.

```gml
// ---------------------------------------------------------------------------
// scr_ruido_perlin
// ---------------------------------------------------------------------------

#macro RUIDO_INV_RAIZ2 0.7071067811865476   // 1 / sqrt(2)

/// @func RuidoPerlin(_semilla)
/// @desc Perlin 2D con la curva quíntica y gradientes unitarios.
///       Salida en [-0.7071, 0.7071] aproximadamente (ver nota de rango).
function RuidoPerlin(_semilla) constructor
{
    var _rng  = new RNG(_semilla);
    var _base = array_create(256, 0);
    for (var _i = 0; _i < 256; _i++) _base[_i] = _i;
    _rng.shuffle(_base);

    perm = array_create(512, 0);
    for (var _i = 0; _i < 512; _i++) perm[_i] = _base[_i mod 256];

    /// @desc Producto escalar entre uno de los 4 gradientes diagonales
    ///       (normalizados a longitud 1) y el vector (_dx, _dy).
    gradiente = function(_h, _dx, _dy)
    {
        switch (_h & 3)
        {
            case 0:  return RUIDO_INV_RAIZ2 * ( _dx + _dy);
            case 1:  return RUIDO_INV_RAIZ2 * (-_dx + _dy);
            case 2:  return RUIDO_INV_RAIZ2 * ( _dx - _dy);
            default: return RUIDO_INV_RAIZ2 * (-_dx - _dy);
        }
    };

    /// @desc Muestra el ruido en un punto continuo.
    muestra = function(_px, _py)
    {
        var _x0 = floor(_px);
        var _y0 = floor(_py);
        var _fx = _px - _x0;
        var _fy = _py - _y0;

        var _ix = _x0 & 255;
        var _iy = _y0 & 255;

        // Los índices máximos son 255 + 255 + 1 = 511: caben en perm[512].
        var _aa = perm[perm[_ix]     + _iy];
        var _ba = perm[perm[_ix + 1] + _iy];
        var _ab = perm[perm[_ix]     + _iy + 1];
        var _bb = perm[perm[_ix + 1] + _iy + 1];

        var _u = curva_quintica(_fx);
        var _v = curva_quintica(_fy);

        var _sup = lerp(gradiente(_aa, _fx, _fy),     gradiente(_ba, _fx - 1, _fy),     _u);
        var _inf = lerp(gradiente(_ab, _fx, _fy - 1), gradiente(_bb, _fx - 1, _fy - 1), _u);

        return lerp(_sup, _inf, _v);
    };

    /// @desc Remapeado a [0, 1]. Ver la nota sobre el rango antes de fiarte.
    muestra_01 = function(_px, _py)
    {
        return clamp(muestra(_px, _py) / (2 * RUIDO_INV_RAIZ2) + 0.5, 0, 1);
    };
}
```

> ⚠️ **El rango del ruido de gradientes NO es [-1, 1].** Con gradientes unitarios en 2D el
> límite teórico que se cita habitualmente es ±√2/2 ≈ ±0,707 (⚠️ no verificado contra una
> fuente primaria; la deducción es del autor de este documento). Red Blob Games advierte del
> mismo problema desde el otro lado: distintas librerías devuelven rangos distintos, unas
> `[0,1]` y otras `[-1,1]`, y sumar octavas puede sacarte del rango que esperabas.
> **Mide el mínimo y el máximo reales de tu generador antes de aplicar umbrales.** Un
> generador de biomas con el ruido sin normalizar produce mundos que son 90 % agua o 90 %
> roca sin que sepas por qué.

```gml
/// @func medir_rango_ruido(_ruido, _muestras, _escala)
/// @desc Diagnóstico obligatorio la primera vez que usas un generador de ruido.
///       Imprime el mínimo, el máximo y la media reales.
function medir_rango_ruido(_ruido, _muestras, _escala)
{
    var _minimo = infinity;
    var _maximo = -infinity;
    var _suma   = 0;

    var _rng = new RNG(1);
    repeat (_muestras)
    {
        var _v = _ruido.muestra(_rng.float() * 1000 * _escala,
                                _rng.float() * 1000 * _escala);
        _minimo = min(_minimo, _v);
        _maximo = max(_maximo, _v);
        _suma  += _v;
    }

    show_debug_message($"ruido: min={_minimo} max={_maximo} media={_suma / _muestras}");
    return { minimo: _minimo, maximo: _maximo, media: _suma / _muestras };
}
```

### 2.4 Simplex: por qué está aquí y por qué probablemente no lo necesitas

*Simplex noise* (Perlin, 2001) sustituye la retícula cuadrada por una **simplicial**
(triángulos en 2D). Ventajas reales: coste `O(n²)` en vez de `O(2ⁿ)` con la dimensión,
gradiente continuo y menos artefactos direccionales. **En 2D la diferencia es pequeña**: 3
vértices por muestra en vez de 4.

**Recomendación honesta: en un juego 2D de GameMaker, usa Perlin.** El simplex compensa a
partir de 3-4 dimensiones (ruido animado en el tiempo, volúmenes). Hay implementaciones GML en
la comunidad —el catálogo de
[`12 · 05 — Pipeline de arte, audio y niveles`](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md)
lista varias— pero no lo reimplementes por costumbre. ⚠️ La situación de patentes del simplex
de 3 o más dimensiones ha sido históricamente confusa; si publicas comercialmente, comprueba la
licencia de la implementación concreta que copies.

### 2.5 Octavas y fBm: de una capa de ruido a un terreno

Una sola capa de ruido es una mancha suave. Un terreno tiene detalle a varias escalas: cordi-
lleras, colinas, rocas. Se consigue **sumando la misma función a frecuencias crecientes y
amplitudes decrecientes**. Es lo que se llama fBm (*fractional Brownian motion*).

```gml
// ---------------------------------------------------------------------------
// scr_ruido_fbm
// ---------------------------------------------------------------------------

/// @func ruido_fbm(_ruido, _px, _py, _octavas, _lacunaridad, _ganancia)
/// @desc Suma de octavas normalizada. Divide por la suma de amplitudes para
///       que el resultado conserve el rango de una sola octava (Red Blob Games).
/// @param {Struct} _ruido        RuidoPerlin o RuidoValor
/// @param {Real}   _octavas      4-6 para terreno; 2-3 para humedad
/// @param {Real}   _lacunaridad  Cuánto sube la frecuencia por octava (2 es lo normal)
/// @param {Real}   _ganancia     Cuánto baja la amplitud por octava (0.5 es lo normal)
function ruido_fbm(_ruido, _px, _py, _octavas, _lacunaridad, _ganancia)
{
    var _suma       = 0;
    var _norma      = 0;
    var _amplitud   = 1;
    var _frecuencia = 1;

    repeat (_octavas)
    {
        _suma  += _amplitud * _ruido.muestra(_px * _frecuencia, _py * _frecuencia);
        _norma += _amplitud;

        _amplitud   *= _ganancia;
        _frecuencia *= _lacunaridad;
    }

    return _suma / _norma;
}
```

> **Variante *ridged*.** Cambiando `_ruido.muestra(...)` por `1 - abs(_ruido.muestra(...))` y
> elevando el resultado al cuadrado, las colinas redondas se vuelven cordilleras afiladas. Es
> una línea de diferencia y un generador de terreno distinto.

**Redistribución.** Sumar octavas da una distribución con demasiado terreno medio. Red Blob
Games resuelve esto elevando a una potencia: exponentes altos aplanan las tierras bajas y
afilan los picos.

```gml
/// @func redistribuir(_altura01, _exponente)
/// @desc _exponente > 1 → más llano y menos montaña. < 1 → al revés.
function redistribuir(_altura01, _exponente)
{
    return power(clamp(_altura01, 0, 1), _exponente);
}
```

### 2.6 Dominio deformado (*domain warping*)

El truco más rentable de todo el capítulo: en vez de muestrear el ruido en `(x, y)`, lo
muestreas en `(x + a·f(x,y), y + b·g(x,y))`. Las curvas de nivel dejan de parecer manchas y
empiezan a parecer geología, madera o humo.

```gml
/// @func ruido_deformado(_ruido, _px, _py, _fuerza, _octavas)
/// @desc Domain warping de una pasada. _fuerza entre 0.2 y 2 según el efecto.
function ruido_deformado(_ruido, _px, _py, _fuerza, _octavas)
{
    // Dos campos de ruido decorrelacionados: se consigue desplazando el dominio
    // con offsets que no sean múltiplos enteros de la retícula.
    var _qx = ruido_fbm(_ruido, _px,        _py,        _octavas, 2, 0.5);
    var _qy = ruido_fbm(_ruido, _px + 5.2,  _py + 1.3,  _octavas, 2, 0.5);

    return ruido_fbm(_ruido,
                     _px + _fuerza * _qx,
                     _py + _fuerza * _qy,
                     _octavas, 2, 0.5);
}
```

### 2.7 Ruido 1D para plataformas, ruido 2D para mapas

**1D: el perfil de un terreno lateral.** Se muestrea el ruido a lo largo de una línea. Es la
forma más barata de generar un scroller infinito con colinas creíbles.

```gml
// ---------------------------------------------------------------------------
// scr_terreno_1d
// ---------------------------------------------------------------------------

/// @func perfil_terreno(_ruido, _columnas, _escala, _alto_base, _amplitud)
/// @desc Devuelve un array con la altura (en celdas) de cada columna.
///       Muestrear una línea fija de un ruido 2D (y = 0.5) evita implementar
///       un ruido 1D aparte y da el mismo resultado.
function perfil_terreno(_ruido, _columnas, _escala, _alto_base, _amplitud)
{
    var _perfil = array_create(_columnas, 0);

    for (var _c = 0; _c < _columnas; _c++)
    {
        var _v = ruido_fbm(_ruido, _c * _escala, 0.5, 4, 2, 0.5);   // [-0.7, 0.7]
        var _n = clamp(_v / (2 * RUIDO_INV_RAIZ2) + 0.5, 0, 1);     // [0, 1]
        _perfil[_c] = floor(_alto_base - _n * _amplitud);
    }

    return _perfil;
}
```

**2D: mapa de altura + mapa de humedad → biomas.** Dos campos de ruido **independientes** (dos
semillas distintas) y una tabla de umbrales. Es el esquema de Red Blob Games, tomado a su vez
del diagrama de biomas de Whittaker (temperatura contra precipitación).

```gml
// ---------------------------------------------------------------------------
// scr_mapa_biomas
// ---------------------------------------------------------------------------

enum Bioma { Agua, Playa, Hierba, Bosque, Roca, Nieve }

/// @func bioma_por_umbral(_altura, _humedad)
/// @desc Los umbrales SON el diseño del mundo. Ajústalos con el panel de §11
///       y anota los que te gusten: son tan importantes como la semilla.
function bioma_por_umbral(_altura, _humedad)
{
    if (_altura < 0.34) return Bioma.Agua;
    if (_altura < 0.39) return Bioma.Playa;
    if (_altura > 0.82) return Bioma.Nieve;
    if (_altura > 0.68) return Bioma.Roca;
    return (_humedad > 0.52) ? Bioma.Bosque : Bioma.Hierba;
}

/// @func forma_isla(_nx, _ny)
/// @desc "Square bump" de Red Blob Games: 0 en el centro, 1 en los bordes.
/// @param {Real} _nx  Coordenada normalizada a [-1, 1]
function forma_isla(_nx, _ny)
{
    return 1 - (1 - _nx * _nx) * (1 - _ny * _ny);
}

/// @func generar_mapa_biomas(_ancho, _alto, _semilla, _config)
/// @desc Genera el mapa ENTERO de una vez y lo devuelve como arrays planos.
///       Nada de esto se hace en Draw: se precalcula una vez (ver §2.9).
function generar_mapa_biomas(_ancho, _alto, _semilla, _config)
{
    // Dos semillas distintas → dos campos decorrelacionados.
    var _ruido_altura  = new RuidoPerlin(_semilla);
    var _ruido_humedad = new RuidoPerlin(_semilla + 104729);   // primo grande

    var _escala    = _config.escala;      // 0.02 - 0.08 según el tamaño de mundo
    var _exponente = _config.exponente;   // 1.0 llano, 2.5 muy montañoso
    var _isla      = _config.isla;        // 0 = continente infinito, 1 = isla clara

    var _n       = _ancho * _alto;
    var _biomas  = array_create(_n, Bioma.Agua);
    var _alturas = array_create(_n, 0);

    for (var _fy = 0; _fy < _alto; _fy++)
    {
        for (var _fx = 0; _fx < _ancho; _fx++)
        {
            var _px = _fx * _escala;
            var _py = _fy * _escala;

            // Altura: fBm deformado, normalizado y redistribuido
            var _bruto = ruido_deformado(_ruido_altura, _px, _py, 0.6, 5);
            var _e = clamp(_bruto / (2 * RUIDO_INV_RAIZ2) + 0.5, 0, 1);
            _e = redistribuir(_e, _exponente);

            // Forma de isla: mezcla lineal con el complemento de la distancia
            if (_isla > 0)
            {
                var _nx = (_fx / _ancho) * 2 - 1;
                var _ny = (_fy / _alto)  * 2 - 1;
                var _d  = clamp(forma_isla(_nx, _ny), 0, 1);
                _e = lerp(_e, 1 - _d, _isla);
            }

            // Humedad: menos octavas, se quiere más suave que la altura
            var _hb = ruido_fbm(_ruido_humedad, _px * 0.7, _py * 0.7, 3, 2, 0.5);
            var _m  = clamp(_hb / (2 * RUIDO_INV_RAIZ2) + 0.5, 0, 1);

            var _i = _fy * _ancho + _fx;
            _alturas[_i] = _e;
            _biomas[_i]  = bioma_por_umbral(_e, _m);
        }
    }

    return {
        ancho:   _ancho,
        alto:    _alto,
        semilla: _semilla,
        biomas:  _biomas,
        alturas: _alturas
    };
}
```

### 2.8 Pintar el mapa en un tilemap

Un tilemap estático es **lo más barato que hay** para dibujar un suelo grande: una sola
llamada de dibujo por capa, sin instancias. Se pinta **una vez**, al generar.

```gml
// ---------------------------------------------------------------------------
// objMundo — Create
// ---------------------------------------------------------------------------

mundo = generar_mapa_biomas(192, 128, global.semilla, {
    escala:    0.035,
    exponente: 1.8,
    isla:      0.55
});

var _capa = layer_get_id("Tiles_Mundo");
mapa_tiles = layer_tilemap_get_id(_capa);

// Índice de tile dentro del tileset, uno por bioma. 0 = celda vacía.
INDICE_POR_BIOMA = [ 1, 2, 3, 4, 5, 6 ];   // Agua, Playa, Hierba, Bosque, Roca, Nieve

pintar_mundo(mundo, mapa_tiles);

// ---------------------------------------------------------------------------

/// @func pintar_mundo(_mundo, _mapa_tiles)
/// @desc Vuelca el array de biomas al tilemap. Se llama UNA vez por generación.
function pintar_mundo(_mundo, _mapa_tiles)
{
    var _t0 = get_timer();

    for (var _fy = 0; _fy < _mundo.alto; _fy++)
    {
        for (var _fx = 0; _fx < _mundo.ancho; _fx++)
        {
            var _bioma = _mundo.biomas[_fy * _mundo.ancho + _fx];
            tilemap_set(_mapa_tiles, INDICE_POR_BIOMA[_bioma], _fx, _fy);
        }
    }

    show_debug_message($"pintado en {(get_timer() - _t0) / 1000} ms");
}
```

> El tilemap tiene que ser **al menos tan grande** como el mapa. Si lo creas por código,
> `layer_tilemap_create(_capa, 0, 0, ts_mundo, _ancho, _alto)`; si viene del editor de rooms,
> ajústalo con `tilemap_set_width` y `tilemap_set_height`. Referencia completa de la familia
> en [`08 · 09 — Dibujo de tiles y tilemaps`](../08%20-%20Referencia%20GML%20completa/09%20-%20Dibujo%20de%20tiles%20y%20tilemaps.md)
> y el concepto de *blob* de datos de tile en
> [`01 · 10 §4 — Tile maps y tile sets`](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20c%C3%A1maras%20y%20viewports.md).

### 2.9 Rendimiento: precalcula, no calcules en Draw

Una muestra de Perlin con 5 octavas son 5 llamadas, 20 accesos a `perm`, 20 productos escalares
y 15 `lerp`. **Multiplicado por 60 fps y por cada píxel visible, es inviable.**

| Patrón | Coste en un mapa de 192×128 | Veredicto |
|---|---|---|
| Muestrear el ruido en el evento **Draw** | ~24 500 muestras **por frame** | ❌ nunca |
| Precalcular a un array en **Create** | ~24 500 muestras **una vez** | ✅ siempre |
| Precalcular y pintar a **tilemap** | Lo anterior + 0 coste de dibujo | ✅✅ el objetivo |
| Precalcular a una **surface** y dibujarla | Útil para minimapas | ✅ si no es un tilemap |

Tres reglas más: **un `RuidoPerlin` se construye una vez** (barajar 256 elementos dentro de un
bucle es el error de rendimiento típico); **`array_create` fuera de los bucles**; y en un mundo
grande, **genera por trozos** — el patrón de *chunks* con `diff` ya está resuelto en
[`04 · 09 §4.6 y §5.4 — Survival y crafting`](../04%20-%20Recetas%20por%20g%C3%A9nero/09%20-%20Survival%20y%20crafting.md).

---

## 3 · Autómatas celulares: cuevas

El método canónico de RogueBasin: **rellenas el mapa de ruido binario y dejas que una regla
local lo suavice**. En 4-6 pasadas, un caos de píxeles se convierte en cavernas.

**La regla 4-5**, tal como la enuncia RogueBasin: *«a tile becomes a wall if it was a wall and 4
or more of its eight neighbors were walls, or if it was not a wall and 5 or more neighbors
were»*. Expresado con su notación: `W'(p) = R1(p) >= 5`, donde `R1(p)` cuenta los muros del
entorno de un paso **incluyendo la propia celda**.

> ℹ️ En la notación *Life-like* de autómatas esa misma regla es **B5678/S45678** (nace con 5-8
> vecinos muro, sobrevive con 4-8). ⚠️ Esa equivalencia es una traducción del autor de este
> documento: **RogueBasin no usa la notación B/S**, usa `R1`/`R2`. La incluyo porque es la forma
> en que se busca el algoritmo fuera del mundo roguelike.

La regla sola deja huecos grandes y feos. RogueBasin añade una segunda condición que los
rellena: `W'(p) = R1(p) >= 5 || R2(p) <= 2`, donde `R2` cuenta los muros a **dos** pasos. Sus
parámetros recomendados: relleno inicial del **40 %**, **4 pasadas** con la regla doble y
**3 pasadas** más solo con `R1 >= 5`.

```gml
// ---------------------------------------------------------------------------
// scr_cueva_celular
// ---------------------------------------------------------------------------

/// @func contar_muros(_celdas, _ancho, _alto, _fx, _fy, _radio)
/// @desc Muros en el cuadrado de lado (2·_radio + 1) centrado en (_fx, _fy).
///       Lo que cae fuera del mapa CUENTA COMO MURO: así el borde se sella solo.
function contar_muros(_celdas, _ancho, _alto, _fx, _fy, _radio)
{
    var _n = 0;
    for (var _oy = -_radio; _oy <= _radio; _oy++)
    {
        for (var _ox = -_radio; _ox <= _radio; _ox++)
        {
            var _vx = _fx + _ox;
            var _vy = _fy + _oy;

            if (_vx < 0 || _vy < 0 || _vx >= _ancho || _vy >= _alto) { _n++; continue; }
            if (_celdas[_vy * _ancho + _vx] == 1) _n++;
        }
    }
    return _n;
}

/// @func cueva_celular(_ancho, _alto, _semilla, _relleno, _pasos_dobles, _pasos_simples)
/// @desc Cueva por autómata celular. Devuelve un array plano: 1 = muro, 0 = suelo.
/// @param {Real} _relleno        Fracción inicial de muro (RogueBasin: 0.40)
/// @param {Real} _pasos_dobles   Pasadas con R1>=5 || R2<=2  (RogueBasin: 4)
/// @param {Real} _pasos_simples  Pasadas con R1>=5           (RogueBasin: 3)
function cueva_celular(_ancho, _alto, _semilla, _relleno, _pasos_dobles, _pasos_simples)
{
    var _rng = new RNG(_semilla);
    var _n   = _ancho * _alto;

    // --- Siembra aleatoria; el borde siempre muro -----------------------------
    var _celdas = array_create(_n, 1);
    for (var _fy = 1; _fy < _alto - 1; _fy++)
        for (var _fx = 1; _fx < _ancho - 1; _fx++)
            _celdas[_fy * _ancho + _fx] = _rng.chance(_relleno) ? 1 : 0;

    // --- Pasadas de suavizado -------------------------------------------------
    // Buffer doble: NO se puede leer y escribir el mismo array en una pasada de
    // autómata celular, o cada celda vería a sus vecinas ya actualizadas.
    var _otro = array_create(_n, 1);

    var _total = _pasos_dobles + _pasos_simples;
    for (var _paso = 0; _paso < _total; _paso++)
    {
        var _usar_r2 = (_paso < _pasos_dobles);

        for (var _fy = 0; _fy < _alto; _fy++)
        {
            for (var _fx = 0; _fx < _ancho; _fx++)
            {
                var _r1 = contar_muros(_celdas, _ancho, _alto, _fx, _fy, 1);
                var _es_muro = (_r1 >= 5);

                if (!_es_muro && _usar_r2)
                {
                    var _r2 = contar_muros(_celdas, _ancho, _alto, _fx, _fy, 2);
                    _es_muro = (_r2 <= 2);
                }

                _otro[_fy * _ancho + _fx] = _es_muro ? 1 : 0;
            }
        }

        array_copy(_celdas, 0, _otro, 0, _n);
    }

    return { ancho: _ancho, alto: _alto, celdas: _celdas, semilla: _semilla };
}
```

### 3.1 Conectar las regiones: reparar en vez de rechazar

Un autómata celular produce casi siempre **varias cuevas aisladas**. Rechazar y regenerar es
tirar trabajo: lo correcto es **etiquetar las regiones y quedarse con la mayor**, o cavar
túneles entre ellas.

El flood fill ya está escrito en
[`04 · 05 §5.4`](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md);
aquí va la variante que **etiqueta todas las regiones de una pasada** sobre el array plano.

```gml
/// @func etiquetar_regiones(_cueva)
/// @desc Asigna a cada celda de suelo el número de su región (1, 2, 3…).
///       Devuelve { etiquetas, tamanos } donde tamanos[k] es el área de la región k.
function etiquetar_regiones(_cueva)
{
    var _ancho = _cueva.ancho;
    var _alto  = _cueva.alto;
    var _n     = _ancho * _alto;

    var _etiquetas = array_create(_n, 0);   // 0 = muro o sin visitar
    var _tamanos   = [0];                   // el índice 0 no se usa
    var _actual    = 0;

    for (var _inicio = 0; _inicio < _n; _inicio++)
    {
        if (_cueva.celdas[_inicio] == 1) continue;   // muro
        if (_etiquetas[_inicio] != 0)    continue;   // ya etiquetada

        _actual++;
        var _area = 0;
        var _cola = [_inicio];
        _etiquetas[_inicio] = _actual;

        while (array_length(_cola) > 0)
        {
            var _c  = array_pop(_cola);
            var _cx = _c mod _ancho;
            var _cy = _c div _ancho;
            _area++;

            var _dx = [1, -1, 0, 0];
            var _dy = [0, 0, 1, -1];

            for (var _d = 0; _d < 4; _d++)
            {
                var _vx = _cx + _dx[_d];
                var _vy = _cy + _dy[_d];
                if (_vx < 0 || _vy < 0 || _vx >= _ancho || _vy >= _alto) continue;

                var _vc = _vy * _ancho + _vx;
                if (_cueva.celdas[_vc] == 1)  continue;
                if (_etiquetas[_vc] != 0)     continue;

                _etiquetas[_vc] = _actual;
                array_push(_cola, _vc);
            }
        }

        array_push(_tamanos, _area);
    }

    return { etiquetas: _etiquetas, tamanos: _tamanos, regiones: _actual };
}

/// @func conservar_region_mayor(_cueva)
/// @desc Rellena de muro todas las regiones menos la más grande. Es la
///       reparación más barata que existe y garantiza conectividad total.
/// @return {Real} Fracción del suelo original que se conserva (0..1)
function conservar_region_mayor(_cueva)
{
    var _r = etiquetar_regiones(_cueva);
    if (_r.regiones == 0) return 0;

    var _mejor = 1;
    for (var _k = 2; _k <= _r.regiones; _k++)
        if (_r.tamanos[_k] > _r.tamanos[_mejor]) _mejor = _k;

    var _n = _cueva.ancho * _cueva.alto;
    var _suelo_total = 0;

    for (var _i = 0; _i < _n; _i++)
    {
        if (_cueva.celdas[_i] == 1) continue;
        _suelo_total++;
        if (_r.etiquetas[_i] != _mejor) _cueva.celdas[_i] = 1;   // sellar
    }

    return (_suelo_total > 0) ? (_r.tamanos[_mejor] / _suelo_total) : 0;
}
```

> Si `conservar_region_mayor` devuelve menos de ~0,6, es que el generador está partiendo el
> mapa en trozos: **baja el relleno inicial** o **sube las pasadas de suavizado**. Es una
> métrica de calidad, no solo una reparación (§10).

### 3.2 Variantes de la misma regla

Cambiando dos números tienes generadores completamente distintos. Merece la pena tenerlos
tabulados:

| Efecto | Relleno | Pasadas dobles | Pasadas simples | Nota |
|---|---|---|---|---|
| **Cueva clásica** | 0,40 | 4 | 3 | Los valores de RogueBasin |
| **Cavernas amplias** | 0,45 | 2 | 5 | Menos `R2` → menos relleno de huecos |
| **Laberinto rocoso** | 0,50 | 0 | 2 | Sin suavizar: queda ruidoso a propósito |
| **Islas / archipiélago** | 0,52 | 5 | 4 | Después **no** conserves solo la mayor |
| **Claros de bosque** | 0,38 | 3 | 2 | El «muro» son árboles, no roca |

Para **islas** el remate es multiplicar por una máscara radial: reutiliza `forma_isla` de §2.7
antes de sembrar, de forma que las celdas del borde arranquen con más probabilidad de muro.

---

## 4 · Poisson-disc: distribuir cosas sin que se amontonen

Colocar 200 árboles con `irandom` produce grumos y calvas: el azar uniforme **no** parece
natural. El muestreo de Poisson-disc garantiza que **ningún par de puntos esté a menos de `r`**
y que el resto sea lo más denso posible. Es el algoritmo correcto para árboles, enemigos,
recursos, decoración y puntos de aparición.

El algoritmo es el de Robert Bridson (*Fast Poisson Disk Sampling in Arbitrary Dimensions*,
SIGGRAPH 2007), literalmente en tres pasos:

1. Rejilla de fondo con celda de lado **`r/√n`** (`n` = dimensiones, aquí 2). Con ese tamaño
   **cabe como mucho una muestra por celda**, así que basta un entero por celda.
2. Una muestra inicial al azar; entra en la *active list*.
3. Mientras la lista activa no esté vacía: coge un índice al azar, genera hasta **`k` = 30**
   candidatos en el **anillo entre `r` y `2r`**, acepta el primero válido; si ninguno vale,
   saca ese índice de la lista.

Bridson demuestra que el paso 3 se ejecuta exactamente `2N-1` veces para `N` muestras: el
algoritmo es **O(N)**.

```gml
// ---------------------------------------------------------------------------
// scr_poisson
// ---------------------------------------------------------------------------

/// @func muestreo_poisson(_ancho, _alto, _radio, _semilla, [_k])
/// @desc Bridson 2007. Devuelve un array de structs { px, py } separados al
///       menos _radio píxeles entre sí.
/// @param {Real} _radio  Distancia mínima entre muestras, en píxeles
/// @param {Real} _k      Intentos por muestra activa (30 en el paper)
function muestreo_poisson(_ancho, _alto, _radio, _semilla, _k = 30)
{
    var _rng = new RNG(_semilla);

    // Paso 0 — rejilla de fondo. r/sqrt(2) ⇒ una muestra por celda como máximo.
    var _lado  = _radio / sqrt(2);
    var _cols  = ceil(_ancho / _lado);
    var _filas = ceil(_alto  / _lado);
    var _rejilla = array_create(_cols * _filas, -1);   // -1 = celda vacía

    var _muestras = [];
    var _activos  = [];

    // Paso 1 — primera muestra
    var _p0x = _rng.float() * _ancho;
    var _p0y = _rng.float() * _alto;
    array_push(_muestras, { px: _p0x, py: _p0y });
    _rejilla[floor(_p0y / _lado) * _cols + floor(_p0x / _lado)] = 0;
    array_push(_activos, 0);

    // Paso 2 — bucle principal
    while (array_length(_activos) > 0)
    {
        var _i      = _rng.int(array_length(_activos) - 1);
        var _origen = _muestras[_activos[_i]];
        var _puesto = false;

        repeat (_k)
        {
            // Anillo [r, 2r] UNIFORME POR ÁREA: r·sqrt(1 + 3u).
            // Usar r·(1 + u) es el error habitual: amontona hacia el radio interior.
            var _ang  = _rng.float() * 360;
            var _dist = _radio * sqrt(1 + 3 * _rng.float());

            var _nx = _origen.px + lengthdir_x(_dist, _ang);
            var _ny = _origen.py + lengthdir_y(_dist, _ang);

            if (_nx < 0 || _ny < 0 || _nx >= _ancho || _ny >= _alto) continue;

            var _gx = floor(_nx / _lado);
            var _gy = floor(_ny / _lado);
            var _valido = true;

            // Con celdas de r/sqrt(2), mirar 2 celdas a cada lado es suficiente.
            for (var _oy = -2; _oy <= 2 && _valido; _oy++)
            {
                for (var _ox = -2; _ox <= 2; _ox++)
                {
                    var _vx = _gx + _ox;
                    var _vy = _gy + _oy;
                    if (_vx < 0 || _vy < 0 || _vx >= _cols || _vy >= _filas) continue;

                    var _idx = _rejilla[_vy * _cols + _vx];
                    if (_idx == -1) continue;

                    var _o = _muestras[_idx];
                    if (point_distance(_nx, _ny, _o.px, _o.py) < _radio)
                    {
                        _valido = false;
                        break;
                    }
                }
            }

            if (_valido)
            {
                array_push(_muestras, { px: _nx, py: _ny });
                var _nuevo = array_length(_muestras) - 1;
                _rejilla[_gy * _cols + _gx] = _nuevo;
                array_push(_activos, _nuevo);
                _puesto = true;
                break;
            }
        }

        if (!_puesto) array_delete(_activos, _i, 1);
    }

    return _muestras;
}
```

**Uso típico: poblar el mundo respetando los biomas.**

```gml
// objMundo — Create, después de generar y pintar
var _puntos = muestreo_poisson(room_width, room_height, 56, mundo.semilla + 31337);

for (var _i = 0; _i < array_length(_puntos); _i++)
{
    var _p  = _puntos[_i];
    var _fx = floor(_p.px / TAM_CELDA);
    var _fy = floor(_p.py / TAM_CELDA);
    var _bioma = mundo.biomas[_fy * mundo.ancho + _fx];

    // El muestreo da la POSICIÓN; el bioma decide QUÉ va ahí (o nada).
    switch (_bioma)
    {
        case Bioma.Bosque: instance_create_layer(_p.px, _p.py, "Props", obj_arbol);  break;
        case Bioma.Roca:   instance_create_layer(_p.px, _p.py, "Props", obj_penasco); break;
        case Bioma.Hierba:
            if (_i mod 3 == 0) instance_create_layer(_p.px, _p.py, "Props", obj_arbusto);
            break;
    }
}
```

> **Radio variable.** Bridson asume un `r` constante. Para densidades distintas por bioma, el
> truco barato es generar con el `r` **más pequeño** que necesites y luego **descartar** puntos
> en las zonas que deban ir más despejadas (como arriba con `_i mod 3`). El resultado sigue sin
> solapamientos y no complica el algoritmo.

---

## 5 · Wave Function Collapse

### 5.1 Qué es de verdad

Sin misticismo, en palabras de Boris the Brave: *«WFC is a constraint problem with a twist –
there are thousands of possible solutions»*. **No tiene nada que ver con la física cuántica**:
es un resolutor de restricciones con una heurística (colapsar primero la celda con menos
opciones) y una elección aleatoria ponderada. Lo publicó Maxim Gumin, y su repositorio (MIT)
atribuye el origen a Paul Merrell: *«Merrell derives adjacency constraints between tiles from an
example model… We generalize his approach to work with NxN overlapping patterns»*.

Hay **dos modelos**, y solo uno es razonable en GML:

| Modelo | Entrada | Coste | Veredicto en GameMaker |
|---|---|---|---|
| **Simple tiled** | Tiles + reglas de adyacencia escritas a mano | Bajo | ✅ el de este documento |
| **Overlapping** | Una imagen de ejemplo; extrae patrones N×N | Alto (miles de patrones) | ⚠️ solo si sabes lo que haces |

**La advertencia honesta sobre el atasco.** El repositorio lo admite: *«all the coefficients
for a certain pixel become zero… the algorithm has run into a contradiction and can not
continue»*, y Boris añade que Gumin *«discovered that… it's rarely necessary to backtrack so we
can skip implementing that»*. Es decir: **la implementación canónica no tiene backtracking**;
cuando se contradice, no produce nada. Con reglas laxas pasa poco; con reglas estrictas o mapas
grandes, constantemente. La solución práctica es **reintentar con otra semilla y un tope**
(el bucle de §1.2).

### 5.2 Cuándo NO usar WFC

Antes del código, el filtro que ahorra semanas:

- **¿Solo quieres que los bordes de los tiles encajen?** Eso es **autotiling**, no WFC.
  GameMaker trae *Auto Tiling* en el editor de tile sets y una máscara de bits de vecindad
  (véase [`01 · 10 §4`](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20c%C3%A1maras%20y%20viewports.md)).
  Es O(1) por celda y no se atasca nunca.
- **¿Quieres estructura global (una llave antes que una puerta)?** WFC solo entiende
  restricciones **locales**. Eso son gramáticas (§6) o ensamblaje por piezas (§7).
- **¿Quieres textura visual coherente con muchas combinaciones válidas?** Ahí sí: WFC brilla en
  ciudades, mazmorras decorativas, patrones de tuberías y niveles «que parecen diseñados».

### 5.3 Simple tiled model en GML

Cada tile declara **cuatro etiquetas de borde** (*sockets*): arriba, derecha, abajo, izquierda.
Dos tiles pueden ser vecinos si la etiqueta que se tocan coincide. Con eso, las reglas de
adyacencia se **derivan solas** en vez de escribirse a mano.

```gml
// ---------------------------------------------------------------------------
// scr_colapso_ondas
// ---------------------------------------------------------------------------
// Direcciones: 0 = arriba, 1 = derecha, 2 = abajo, 3 = izquierda.
// La opuesta de _d es (_d + 2) mod 4.

/// @func tiles_de_ejemplo()
/// @desc Un juego mínimo de tiles con sockets: "s" = suelo, "m" = muro.
///       socket = [arriba, derecha, abajo, izquierda]
function tiles_de_ejemplo()
{
    return [
        { indice: 1, peso: 8, socket: ["s", "s", "s", "s"] },   // suelo abierto
        { indice: 2, peso: 4, socket: ["m", "m", "m", "m"] },   // muro macizo
        { indice: 3, peso: 2, socket: ["m", "s", "s", "m"] },   // esquina ↘
        { indice: 4, peso: 2, socket: ["m", "m", "s", "s"] },   // esquina ↙
        { indice: 5, peso: 2, socket: ["s", "s", "m", "m"] },   // esquina ↗
        { indice: 6, peso: 2, socket: ["s", "m", "m", "s"] },   // esquina ↖
        { indice: 7, peso: 3, socket: ["m", "s", "m", "s"] },   // pasillo horizontal
        { indice: 8, peso: 3, socket: ["s", "m", "s", "m"] }    // pasillo vertical
    ];
}

/// @func ColapsoOndas(_ancho, _alto, _tiles, _semilla)
/// @desc WFC "simple tiled". Pensado para rejillas PEQUEÑAS (hasta ~40×40):
///       la propagación es O(celdas · tiles²) y en la VM se nota enseguida.
function ColapsoOndas(_ancho, _alto, _tiles, _semilla) constructor
{
    ancho   = _ancho;
    alto    = _alto;
    tiles   = _tiles;
    n_tiles = array_length(_tiles);
    semilla = _semilla;

    rng           = new RNG(_semilla);
    onda          = [];
    contradiccion = false;

    // --- Tabla de compatibilidad, precalculada una sola vez -------------------
    // compatible[_d][_a][_b] = ¿puede _b estar en la dirección _d de _a?
    compatible = array_create(4, undefined);
    for (var _d = 0; _d < 4; _d++)
    {
        var _tabla = array_create(n_tiles, undefined);
        for (var _a = 0; _a < n_tiles; _a++)
        {
            var _fila = array_create(n_tiles, false);
            for (var _b = 0; _b < n_tiles; _b++)
                _fila[_b] = (tiles[_a].socket[_d] == tiles[_b].socket[(_d + 2) mod 4]);
            _tabla[_a] = _fila;
        }
        compatible[_d] = _tabla;
    }

    /// @desc Devuelve todas las celdas a "todo es posible".
    reiniciar = function(_desplazamiento)
    {
        rng = new RNG(semilla + _desplazamiento * 7919);
        contradiccion = false;

        onda = array_create(ancho * alto, undefined);
        for (var _c = 0; _c < ancho * alto; _c++)
            onda[_c] = array_create(n_tiles, true);   // un array NUEVO por celda
    };

    contar = function(_c)
    {
        var _n = 0;
        var _o = onda[_c];
        for (var _t = 0; _t < n_tiles; _t++) if (_o[_t]) _n++;
        return _n;
    };

    /// @desc Entropía de Shannon con pesos: ln(Σw) − (Σ w·ln w)/Σw.
    ///       Con pesos iguales equivale a "menos opciones = menos entropía".
    entropia = function(_c)
    {
        var _suma = 0;
        var _suma_log = 0;
        var _o = onda[_c];

        for (var _t = 0; _t < n_tiles; _t++)
        {
            if (!_o[_t]) continue;
            var _w = tiles[_t].peso;
            _suma     += _w;
            _suma_log += _w * ln(_w);
        }

        if (_suma <= 0) return -1;
        return ln(_suma) - _suma_log / _suma;
    };

    /// @desc Celda sin colapsar de menor entropía. -1 si ya no queda ninguna.
    siguiente_celda = function()
    {
        var _mejor = -1;
        var _minimo = infinity;

        for (var _c = 0; _c < ancho * alto; _c++)
        {
            if (contar(_c) <= 1) continue;
            // Ruido diminuto para romper empates sin sesgo posicional.
            var _e = entropia(_c) + rng.float() * 0.0001;
            if (_e < _minimo) { _minimo = _e; _mejor = _c; }
        }

        return _mejor;
    };

    /// @desc Elige un tile de la celda con probabilidad proporcional a su peso.
    colapsar = function(_c)
    {
        var _o = onda[_c];
        var _total = 0;
        for (var _t = 0; _t < n_tiles; _t++) if (_o[_t]) _total += tiles[_t].peso;

        var _tirada  = rng.float() * _total;
        var _elegido = -1;

        for (var _t = 0; _t < n_tiles; _t++)
        {
            if (!_o[_t]) continue;
            _tirada -= tiles[_t].peso;
            if (_tirada <= 0) { _elegido = _t; break; }
        }

        // Red de seguridad: el redondeo puede dejar la tirada sin consumir.
        if (_elegido == -1)
            for (var _t = n_tiles - 1; _t >= 0; _t--)
                if (_o[_t]) { _elegido = _t; break; }

        for (var _t = 0; _t < n_tiles; _t++) _o[_t] = (_t == _elegido);
    };

    /// @desc Propaga la restricción hasta que nada cambie (AC-3 simplificado).
    propagar = function(_origen)
    {
        var _pila = [_origen];
        var _dx = [0, 1, 0, -1];
        var _dy = [-1, 0, 1, 0];

        while (array_length(_pila) > 0)
        {
            var _c  = array_pop(_pila);
            var _cx = _c mod ancho;
            var _cy = _c div ancho;

            for (var _d = 0; _d < 4; _d++)
            {
                var _vx = _cx + _dx[_d];
                var _vy = _cy + _dy[_d];
                if (_vx < 0 || _vy < 0 || _vx >= ancho || _vy >= alto) continue;

                var _vc = _vy * ancho + _vx;
                var _cambio = false;

                for (var _b = 0; _b < n_tiles; _b++)
                {
                    if (!onda[_vc][_b]) continue;

                    // ¿Sobrevive algún tile de _c que admita a _b en dirección _d?
                    var _apoyado = false;
                    for (var _a = 0; _a < n_tiles; _a++)
                    {
                        if (!onda[_c][_a]) continue;
                        if (compatible[_d][_a][_b]) { _apoyado = true; break; }
                    }

                    if (!_apoyado) { onda[_vc][_b] = false; _cambio = true; }
                }

                if (_cambio)
                {
                    if (contar(_vc) == 0) { contradiccion = true; return; }
                    array_push(_pila, _vc);
                }
            }
        }
    };

    /// @desc Resuelve la rejilla entera. Sin backtracking: si se contradice,
    ///       reinicia con otra semilla derivada, hasta _max_intentos.
    /// @return {Array|Undefined} Array plano de índices de tile, o undefined.
    resolver = function(_max_intentos)
    {
        for (var _intento = 0; _intento < _max_intentos; _intento++)
        {
            reiniciar(_intento);

            while (true)
            {
                var _c = siguiente_celda();
                if (_c == -1)
                {
                    // Todo colapsado: volcar a índices de tile.
                    var _salida = array_create(ancho * alto, 0);
                    for (var _k = 0; _k < ancho * alto; _k++)
                        for (var _t = 0; _t < n_tiles; _t++)
                            if (onda[_k][_t]) { _salida[_k] = tiles[_t].indice; break; }

                    show_debug_message($"WFC resuelto en el intento {_intento + 1}");
                    return _salida;
                }

                colapsar(_c);
                propagar(_c);
                if (contradiccion) break;
            }
        }

        show_debug_message("WFC: sin solución tras todos los intentos");
        return undefined;
    };
}
```

**Uso:**

```gml
var _wfc = new ColapsoOndas(24, 16, tiles_de_ejemplo(), global.semilla);
var _mapa = _wfc.resolver(20);

if (_mapa != undefined)
{
    var _tm = layer_tilemap_get_id(layer_get_id("Tiles_WFC"));
    for (var _fy = 0; _fy < 16; _fy++)
        for (var _fx = 0; _fx < 24; _fx++)
            tilemap_set(_tm, _mapa[_fy * 24 + _fx], _fx, _fy);
}
else
{
    // Plan B obligatorio: NUNCA dejes al jugador sin nivel.
    generar_nivel_de_respaldo();
}
```

> ⚠️ **Coste real.** La propagación es `O(celdas · tiles²)` en el peor caso y la ejecuta cada
> colapso. Con 8 tiles y 24×16 celdas va sobrada; con 40 tiles y 100×100 celdas **se te va a
> varios segundos en la VM**. Si necesitas mapas grandes: resuelve por regiones solapadas, o
> compila a YYC, o cambia a autotiling. Mide con `get_timer()` antes de asumir nada.

---

## 6 · Gramáticas, L-systems y cadenas de Markov

Ruido y autómatas generan **espacio**. Las gramáticas generan **estructura**: jerarquía, orden,
dependencias. Es lo que hace falta para plantas, ciudades, misiones y nombres.

### 6.1 L-systems: plantas, ríos y calles

Un L-system determinista y libre de contexto (*DOL-system*) es la terna `G = ⟨V, ω, P⟩`:
alfabeto, **axioma** y **producciones**. Prusinkiewicz y Lindenmayer marcan la diferencia clave
con las gramáticas de Chomsky: *«In Chomsky grammars productions are applied sequentially,
whereas in L-systems they are applied in parallel and simultaneously replace all letters in a
given word»*. Ese paralelismo es lo que modela el crecimiento de un organismo.

```gml
// ---------------------------------------------------------------------------
// scr_lsistema
// ---------------------------------------------------------------------------

/// @func expandir_lsistema(_axioma, _reglas, _iteraciones)
/// @desc Reescritura EN PARALELO: cada pasada sustituye todas las letras a la vez.
/// @param {String} _axioma      Cadena inicial, p. ej. "F"
/// @param {Struct} _reglas      Clave = símbolo, valor = sustitución
/// @param {Real}   _iteraciones ⚠️ crece exponencialmente: 5-6 es el techo práctico
function expandir_lsistema(_axioma, _reglas, _iteraciones)
{
    var _actual = _axioma;

    repeat (_iteraciones)
    {
        var _siguiente = "";
        var _n = string_length(_actual);

        for (var _i = 1; _i <= _n; _i++)
        {
            var _c = string_char_at(_actual, _i);
            _siguiente += variable_struct_exists(_reglas, _c) ? _reglas[$ _c] : _c;
        }

        _actual = _siguiente;
        if (string_length(_actual) > 200000) break;   // freno de mano
    }

    return _actual;
}

/// @func dibujar_lsistema(_cadena, _px, _py, _angulo, _paso, _giro)
/// @desc Interpretación "tortuga": F avanza dibujando, + y - giran,
///       [ y ] apilan y restauran el estado (ramas).
function dibujar_lsistema(_cadena, _px, _py, _angulo, _paso, _giro)
{
    var _x_actual = _px;
    var _y_actual = _py;
    var _dir      = _angulo;
    var _pila     = [];

    var _n = string_length(_cadena);
    for (var _i = 1; _i <= _n; _i++)
    {
        switch (string_char_at(_cadena, _i))
        {
            case "F":
                var _nx = _x_actual + lengthdir_x(_paso, _dir);
                var _ny = _y_actual + lengthdir_y(_paso, _dir);
                draw_line(_x_actual, _y_actual, _nx, _ny);
                _x_actual = _nx;
                _y_actual = _ny;
                break;

            case "+": _dir += _giro; break;
            case "-": _dir -= _giro; break;

            case "[":
                array_push(_pila, { px: _x_actual, py: _y_actual, dir: _dir });
                break;

            case "]":
                if (array_length(_pila) > 0)
                {
                    var _e = array_pop(_pila);
                    _x_actual = _e.px;
                    _y_actual = _e.py;
                    _dir      = _e.dir;
                }
                break;
        }
    }
}
```

```gml
// Uso: un arbusto. El axioma "X" no dibuja; solo controla el crecimiento.
var _reglas = {};
_reglas[$ "X"] = "F+[[X]-X]-F[-FX]+X";
_reglas[$ "F"] = "FF";

var _planta = expandir_lsistema("X", _reglas, 5);
// En un evento Draw, o mejor: una sola vez sobre una surface (§11).
dibujar_lsistema(_planta, x, y, 270, 4, 25);
```

| Sistema | Axioma | Reglas | Ángulo | Uso |
|---|---|---|---|---|
| Algas de Lindenmayer | `b` | `a→ab`, `b→a` | — | Ejemplo canónico del libro |
| Curva de Koch | `F` | `F→F+F-F-F+F` | 90° | Costas, grietas |
| Arbusto | `X` | `X→F+[[X]-X]-F[-FX]+X`, `F→FF` | 25° | Vegetación de fondo |
| Árbol binario | `F` | `F→F[+F]F[-F]F` | 25-30° | Ramas, raíces, ríos |

> **De determinista a variado**: hace falta un L-system **estocástico**. Cambia el valor de
> cada regla por un array de alternativas y elige con `_rng.pick(...)`. Con la misma semilla
> sigue siendo reproducible, pero cada planta es distinta.

### 6.2 Gramáticas de misión

La misma idea aplicada a la estructura narrativa: los no terminales se expanden en secuencias
de acciones hasta quedarse en terminales.

```gml
// ---------------------------------------------------------------------------
// scr_gramatica_mision
// ---------------------------------------------------------------------------

/// @func gramatica_misiones()
/// @desc Cada clave es un no terminal; cada valor, sus alternativas.
///       Lo que no es clave es un terminal (una acción concreta del juego).
function gramatica_misiones()
{
    var _g = {};
    _g[$ "MISION"]    = [ ["ENGANCHE", "NUDO", "DESENLACE"] ];
    _g[$ "ENGANCHE"]  = [ ["hablar_pnj"], ["encontrar_cadaver"], ["oir_rumor"] ];
    _g[$ "NUDO"]      = [ ["viajar", "OBSTACULO", "NUDO"],
                          ["OBSTACULO"],
                          ["OBSTACULO", "conseguir_objeto"] ];
    _g[$ "OBSTACULO"] = [ ["derrotar_enemigo"], ["resolver_puzle"], ["sobornar_guardia"] ];
    _g[$ "DESENLACE"] = [ ["entregar_objeto", "cobrar"], ["derrotar_jefe", "cobrar"] ];
    return _g;
}

/// @func expandir_gramatica(_simbolo, _gramatica, _rng, _profundidad)
/// @desc Expansión recursiva con tope de profundidad. Devuelve un array de
///       terminales: la misión ya lista para instanciar.
function expandir_gramatica(_simbolo, _gramatica, _rng, _profundidad)
{
    // Terminal, o demasiado profundo: se devuelve tal cual.
    if (!variable_struct_exists(_gramatica, _simbolo)) return [_simbolo];
    if (_profundidad <= 0) return [];

    var _alternativas = _gramatica[$ _simbolo];
    var _elegida = _alternativas[_rng.int(array_length(_alternativas) - 1)];

    var _salida = [];
    for (var _i = 0; _i < array_length(_elegida); _i++)
    {
        var _sub = expandir_gramatica(_elegida[_i], _gramatica, _rng, _profundidad - 1);
        _salida = array_concat(_salida, _sub);
    }

    return _salida;
}
```

```gml
var _rng = new RNG(global.semilla + 991);
var _mision = expandir_gramatica("MISION", gramatica_misiones(), _rng, 8);
show_debug_message(_mision);
// → ["oir_rumor","viajar","resolver_puzle","derrotar_enemigo","entregar_objeto","cobrar"]
```

> La **recursión con tope** (`NUDO → … NUDO`) es lo que da misiones de longitud variable. Sin
> el tope, la gramática se cuelga: es el error clásico del método.

### 6.3 Nombres con cadenas de Markov sobre sílabas

Una cadena de Markov de orden 1 sobre **sílabas** (en vez de letras) da nombres pronunciables
con un corpus diminuto. Se cuenta qué sílaba sigue a cuál y se muestrea esa distribución.

```gml
// ---------------------------------------------------------------------------
// scr_nombres_markov
// ---------------------------------------------------------------------------

/// @func GeneradorNombres(_corpus, _semilla)
/// @desc Cadena de Markov de orden 1 sobre sílabas.
/// @param {Array<Array<String>>} _corpus Nombres ya separados en sílabas,
///        p. ej. [["ka","re","na"], ["mor","dan"], ["is","el","dur"]]
function GeneradorNombres(_corpus, _semilla) constructor
{
    rng      = new RNG(_semilla);
    inicios  = [];    // sílabas que pueden abrir un nombre
    finales  = [];    // sílabas que pueden cerrarlo
    sigue_a  = {};    // sílaba → array de sílabas que la siguen (con repetición
                      //          = peso: cuanto más frecuente, más veces aparece)

    for (var _i = 0; _i < array_length(_corpus); _i++)
    {
        var _nombre = _corpus[_i];
        var _n = array_length(_nombre);
        if (_n == 0) continue;

        array_push(inicios, _nombre[0]);
        array_push(finales, _nombre[_n - 1]);

        for (var _j = 0; _j < _n - 1; _j++)
        {
            var _a = _nombre[_j];
            if (!variable_struct_exists(sigue_a, _a)) sigue_a[$ _a] = [];
            array_push(sigue_a[$ _a], _nombre[_j + 1]);
        }
    }

    /// @desc Genera un nombre de _min a _max sílabas, capitalizado.
    generar = function(_min, _max)
    {
        var _objetivo = rng.range(_min, _max);
        var _actual   = rng.pick(inicios);
        var _salida   = _actual;

        repeat (_objetivo - 1)
        {
            if (!variable_struct_exists(sigue_a, _actual)) break;

            var _opciones = sigue_a[$ _actual];
            if (array_length(_opciones) == 0) break;

            _actual  = rng.pick(_opciones);
            _salida += _actual;
        }

        return string_upper(string_char_at(_salida, 1)) + string_copy(_salida, 2, string_length(_salida) - 1);
    };
}
```

```gml
var _corpus = [
    ["ka","re","na"], ["mor","dan"],   ["is","el","dur"], ["thal","rik"],
    ["ve","ran","dis"], ["gor","mak"], ["sy","le","na"],  ["dru","ven"]
];
var _nombres = new GeneradorNombres(_corpus, global.semilla);
repeat (5) show_debug_message(_nombres.generar(2, 4));
```

> **Orden 1 basta para nombres.** Órdenes mayores (mirar 2-3 sílabas atrás) reproducen el
> corpus casi literalmente si es pequeño; para usarlos hace falta *backoff* —caer a un orden
> menor cuando no hay datos— y un suavizado tipo *prior* de Dirichlet. Con 20-40 nombres de
> corpus, el orden 1 sobre sílabas da mejor resultado y es una décima parte del código.

---

## 7 · Ensamblaje por piezas

El método de *Spelunky* y *Isaac*: **el algoritmo elige y conecta, el autor dibuja**. Una pieza
es una rejilla pequeña con **puertas etiquetadas** en sus bordes.

### 7.1 Las piezas como datos, no como rooms

**La recomendación firme de este documento: define las piezas como datos (JSON), no como rooms
de GameMaker.** Las funciones de rooms existen —están verificadas— pero tienen trampas que el
manual documenta de forma tajante:

| Función | Existe | Trampa documentada en el manual |
|---|---|---|
| `room_duplicate(index)` | ✅ | Las rooms creadas así **no entran en el orden habitual**: `room_next` y `room_previous` no funcionan sobre ellas |
| `room_instance_add(index, x, y, obj)` | ✅ | *«llamar a esta función en un room asset creado en el navegador Asset **añadirá permanentemente la instancia** a la sala, e incluso llamando a `game_restart()` no devolverá el room a su estado original»* |
| `room_add()` + `room_assign(origen, destino)` | ✅ | La vía correcta si insistes en usar rooms: crea una room nueva y **le copia** el contenido de la plantilla |

Es decir: `room_instance_add` sobre una room del proyecto **corrompe el asset en la sesión en
curso**. El único patrón seguro con rooms es `room_add()` → `room_assign(rm_plantilla, nueva)` →
`room_instance_add(nueva, …)`, y aun así no puedes inspeccionar la pieza como dato, ni validarla,
ni serializarla. Con JSON tienes todo eso gratis, y **GMRoomLoader** (catalogada en
[`12 · 05`](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md))
resuelve el caso híbrido: diseñar en el editor de rooms y cargar por regiones en runtime.

### 7.2 Piezas con puertas etiquetadas

```gml
// ---------------------------------------------------------------------------
// scr_piezas
// ---------------------------------------------------------------------------

/// @func pieza_desde_texto(_nombre, _filas, _puertas, _peso)
/// @desc Una pieza dibujada como texto: '#' muro, '.' suelo, '+' puerta.
///       Se lee de un JSON o se escribe en el propio script.
/// @param {Array<String>} _filas   Dibujo de la pieza, una cadena por fila
/// @param {Array<String>} _puertas Etiqueta por lado: [arriba, derecha, abajo, izquierda]
///                                 "" = ese lado es macizo
function pieza_desde_texto(_nombre, _filas, _puertas, _peso)
{
    var _alto  = array_length(_filas);
    var _ancho = string_length(_filas[0]);
    var _celdas = array_create(_ancho * _alto, 1);

    for (var _fy = 0; _fy < _alto; _fy++)
        for (var _fx = 0; _fx < _ancho; _fx++)
        {
            var _c = string_char_at(_filas[_fy], _fx + 1);
            _celdas[_fy * _ancho + _fx] = (_c == "#") ? 1 : 0;
        }

    return {
        nombre:  _nombre,
        ancho:   _ancho,
        alto:    _alto,
        celdas:  _celdas,
        puertas: _puertas,
        peso:    _peso
    };
}

/// @func catalogo_piezas()
function catalogo_piezas()
{
    return [
        pieza_desde_texto("cruce", [
            "###+###",
            "#.....#",
            "+.....+",
            "#.....#",
            "###+###"
        ], ["ancho", "ancho", "ancho", "ancho"], 5),

        pieza_desde_texto("pasillo_h", [
            "#######",
            "+.....+",
            "#######"
        ], ["", "ancho", "", "ancho"], 8),

        pieza_desde_texto("sala_tesoro", [
            "#######",
            "#..$..#",
            "+.....+",
            "#..$..#",
            "#######"
        ], ["", "ancho", "", "ancho"], 2)
    ];
}
```

### 7.3 Colocar y conectar

```gml
/// @func ensamblar_nivel(_ancho, _alto, _piezas, _semilla, _objetivo)
/// @desc Coloca piezas en una rejilla grande respetando las etiquetas de puerta.
///       Estrategia: crecer desde una pieza semilla, siempre por una puerta libre.
/// @return {Struct} { ancho, alto, celdas, colocadas }
function ensamblar_nivel(_ancho, _alto, _piezas, _semilla, _objetivo)
{
    var _rng = new RNG(_semilla);
    var _mapa = { ancho: _ancho, alto: _alto, celdas: array_create(_ancho * _alto, 1) };

    var _colocadas = [];
    var _frontera  = [];   // puertas libres: { px, py, lado, etiqueta }

    // Semilla: una pieza en el centro.
    var _primera = _rng.pick(_piezas);
    var _cx = floor((_ancho - _primera.ancho) * 0.5);
    var _cy = floor((_alto  - _primera.alto)  * 0.5);
    estampar_pieza(_mapa, _primera, _cx, _cy);
    array_push(_colocadas, { pieza: _primera, px: _cx, py: _cy });
    anotar_puertas(_frontera, _primera, _cx, _cy);

    var _intentos = 0;
    while (array_length(_colocadas) < _objetivo && array_length(_frontera) > 0
           && _intentos < _objetivo * 40)
    {
        _intentos++;

        var _i = _rng.int(array_length(_frontera) - 1);
        var _p = _frontera[_i];
        array_delete(_frontera, _i, 1);

        // Candidatas: piezas con una puerta compatible en el lado OPUESTO.
        var _lado_opuesto = (_p.lado + 2) mod 4;
        var _candidatas = [];
        for (var _k = 0; _k < array_length(_piezas); _k++)
            if (_piezas[_k].puertas[_lado_opuesto] == _p.etiqueta)
                repeat (_piezas[_k].peso) array_push(_candidatas, _piezas[_k]);

        if (array_length(_candidatas) == 0) continue;
        _rng.shuffle(_candidatas);
        var _nueva = _candidatas[0];

        // Posición: pegada a la puerta, por el lado que toca.
        var _nx = _p.px;
        var _ny = _p.py;
        switch (_p.lado)
        {
            case 0: _ny -= _nueva.alto;  _nx -= floor(_nueva.ancho * 0.5); break;  // arriba
            case 1: _nx += 1;            _ny -= floor(_nueva.alto  * 0.5); break;  // derecha
            case 2: _ny += 1;            _nx -= floor(_nueva.ancho * 0.5); break;  // abajo
            case 3: _nx -= _nueva.ancho; _ny -= floor(_nueva.alto  * 0.5); break;  // izquierda
        }

        if (!cabe_pieza(_mapa, _nueva, _nx, _ny)) continue;

        estampar_pieza(_mapa, _nueva, _nx, _ny);
        _mapa.celdas[_p.py * _ancho + _p.px] = 0;   // abrir la puerta que las une
        array_push(_colocadas, { pieza: _nueva, px: _nx, py: _ny });
        anotar_puertas(_frontera, _nueva, _nx, _ny);
    }

    _mapa.colocadas = _colocadas;
    return _mapa;
}

/// @func cabe_pieza(_mapa, _pieza, _px, _py)
/// @desc true si la pieza entra en el mapa y no pisa suelo ya excavado.
function cabe_pieza(_mapa, _pieza, _px, _py)
{
    if (_px < 1 || _py < 1) return false;
    if (_px + _pieza.ancho >= _mapa.ancho) return false;
    if (_py + _pieza.alto  >= _mapa.alto)  return false;

    for (var _fy = 0; _fy < _pieza.alto; _fy++)
        for (var _fx = 0; _fx < _pieza.ancho; _fx++)
            if (_mapa.celdas[(_py + _fy) * _mapa.ancho + (_px + _fx)] == 0) return false;

    return true;
}

/// @func estampar_pieza(_mapa, _pieza, _px, _py)
function estampar_pieza(_mapa, _pieza, _px, _py)
{
    for (var _fy = 0; _fy < _pieza.alto; _fy++)
        for (var _fx = 0; _fx < _pieza.ancho; _fx++)
            _mapa.celdas[(_py + _fy) * _mapa.ancho + (_px + _fx)] =
                _pieza.celdas[_fy * _pieza.ancho + _fx];
}

/// @func anotar_puertas(_frontera, _pieza, _px, _py)
/// @desc Registra las puertas de una pieza recién colocada como puntos de
///       crecimiento. La puerta se sitúa en el centro de cada lado.
function anotar_puertas(_frontera, _pieza, _px, _py)
{
    var _mx = _px + floor(_pieza.ancho * 0.5);
    var _my = _py + floor(_pieza.alto  * 0.5);

    var _puntos_x = [_mx, _px + _pieza.ancho - 1, _mx, _px];
    var _puntos_y = [_py, _my, _py + _pieza.alto - 1, _my];

    for (var _lado = 0; _lado < 4; _lado++)
    {
        var _etiqueta = _pieza.puertas[_lado];
        if (_etiqueta == "") continue;

        array_push(_frontera, {
            px: _puntos_x[_lado],
            py: _puntos_y[_lado],
            lado: _lado,
            etiqueta: _etiqueta
        });
    }
}
```

> Los **Prefabs** de 2026 son la versión oficial de esta idea a nivel de assets: piezas
> reutilizables con sus sprites, objetos y macros. Para piezas de nivel siguen sin sustituir a
> los datos, pero son la forma correcta de distribuir el **contenido** de las piezas entre
> proyectos. Detalle en
> [`02 · 08 — Package Manager y Prefabs`](../02%20-%20Novedades%202026/08%20-%20Package%20Manager%20y%20Prefabs.md).

---

## 8 · Niveles de plataformas por ritmo

Un nivel de plataformas no es un espacio: es una **secuencia temporal de acciones**. Gillian
Smith y sus coautores lo formalizaron en *Rhythm-Based Level Generation for 2D Platformers*
(FDG 2009) con dos ideas que se copian tal cual:

1. **Rhythm group**: una sección pequeña y no solapada del nivel que encapsula una sensación de
   ritmo (tres saltos cortos seguidos; una carrera larga con saltitos entre medias).
2. **Dos capas de gramática**: la primera genera el **ritmo** —verbos `move` y `jump` con
   tiempos de inicio y fin—; la segunda convierte esos verbos en **geometría**. Cita textual:
   *«the first tier is a rhythm generator, and the second tier creates geometry based on that
   rhythm… regardless of geometric representation»*.

Lo que hace jugable la geometría son las **métricas del jugador**: velocidad máxima, velocidad
inicial de salto, altura según cuánto se pulse el botón y tiempo en el aire. **Se miden en tu
propio juego antes de generar nada.**

```gml
// ---------------------------------------------------------------------------
// scr_ritmo_nivel
// ---------------------------------------------------------------------------
// MIDE ESTOS TRES NÚMEROS EN TU JUEGO. No los copies: son los del ejemplo.

#macro JUGADOR_VEL        220    // px/s en carrera
#macro JUGADOR_SALTO_ALTO  96    // px de altura con pulsación larga
#macro JUGADOR_SALTO_LARGO 176   // px de alcance horizontal en un salto pleno
#macro MARGEN_SEGURIDAD   0.82   // nunca pidas el 100 % de lo que el jugador puede

enum Beat { Correr, SaltoCorto, SaltoLargo, SaltoEnemigo, Descanso }

/// @func generar_ritmo(_semilla, _grupos)
/// @desc Capa 1: solo ritmo. Devuelve un array de { tipo, duracion } en segundos.
///       Cada grupo tiene una densidad y un patrón propios: eso es el "rhythm group".
function generar_ritmo(_semilla, _grupos)
{
    var _rng   = new RNG(_semilla);
    var _beats = [];

    repeat (_grupos)
    {
        // La densidad del grupo decide su carácter: tenso, tranquilo o mixto.
        var _densidad = _rng.pick([0.25, 0.5, 0.85]);
        var _n_beats  = _rng.range(3, 6);

        repeat (_n_beats)
        {
            var _tipo = Beat.Correr;

            if (_rng.float() < _densidad)
            {
                _tipo = _rng.pick([Beat.SaltoCorto, Beat.SaltoCorto,
                                   Beat.SaltoLargo, Beat.SaltoEnemigo]);
            }

            array_push(_beats, {
                tipo: _tipo,
                duracion: (_tipo == Beat.Correr) ? _rng.range(6, 12) / 10 : 0.45
            });
        }

        // Respiro entre grupos: es lo que convierte una lista en un ritmo.
        array_push(_beats, { tipo: Beat.Descanso, duracion: _rng.range(8, 14) / 10 });
    }

    return _beats;
}

/// @func ritmo_a_geometria(_beats, _semilla, _y_base)
/// @desc Capa 2: cada beat se convierte en plataformas y enemigos, usando las
///       métricas del jugador para que TODO sea alcanzable por construcción.
/// @return {Array<Struct>} [{ tipo, px, py, ancho }]
function ritmo_a_geometria(_beats, _semilla, _y_base)
{
    var _rng    = new RNG(_semilla + 17);
    var _piezas = [];

    var _px = 0;
    var _py = _y_base;

    var _salto_h = JUGADOR_SALTO_LARGO * MARGEN_SEGURIDAD;
    var _salto_v = JUGADOR_SALTO_ALTO  * MARGEN_SEGURIDAD;

    for (var _i = 0; _i < array_length(_beats); _i++)
    {
        var _b = _beats[_i];

        switch (_b.tipo)
        {
            case Beat.Correr:
            case Beat.Descanso:
                var _largo = round(JUGADOR_VEL * _b.duracion);
                array_push(_piezas, { tipo: "suelo", px: _px, py: _py, ancho: _largo });
                _px += _largo;
                break;

            case Beat.SaltoCorto:
                // Hueco corto y desnivel suave: siempre dentro del alcance.
                var _hueco = round(_salto_h * _rng.range(35, 55) / 100);
                var _sube  = _rng.range(-1, 1) * round(_salto_v * 0.35);
                _px += _hueco;
                _py  = clamp(_py + _sube, _y_base - _salto_v * 2, _y_base + 48);
                array_push(_piezas, { tipo: "suelo", px: _px, py: _py, ancho: 64 });
                _px += 64;
                break;

            case Beat.SaltoLargo:
                var _hueco2 = round(_salto_h * _rng.range(75, 95) / 100);
                _px += _hueco2;
                array_push(_piezas, { tipo: "suelo", px: _px, py: _py, ancho: 96 });
                _px += 96;
                break;

            case Beat.SaltoEnemigo:
                // El obstáculo es el enemigo, no el hueco: el suelo sigue.
                array_push(_piezas, { tipo: "suelo",   px: _px, py: _py, ancho: 128 });
                array_push(_piezas, { tipo: "enemigo", px: _px + 64, py: _py - 16, ancho: 0 });
                _px += 128;
                break;
        }
    }

    return _piezas;
}
```

> **Sobregenerar y filtrar.** El paper produce **1 000 niveles candidatos** y los puntúa con
> *critics* (ajuste a una línea de dificultad del diseñador; chi-cuadrado sobre frecuencias de
> componentes) para quedarse con el mejor. En GameMaker sale casi gratis: el generador es puro,
> llamarlo mil veces son milisegundos.

```gml
/// @func mejor_nivel(_semilla_base, _candidatos, _dificultad_objetivo)
/// @desc Genera N niveles y devuelve el que mejor se ajusta a la curva pedida.
function mejor_nivel(_semilla_base, _candidatos, _dificultad_objetivo)
{
    var _mejor = undefined;
    var _mejor_error = infinity;

    for (var _i = 0; _i < _candidatos; _i++)
    {
        var _beats = generar_ritmo(_semilla_base + _i, 6);

        // Métrica simple: fracción de beats que exigen salto.
        var _saltos = 0;
        for (var _k = 0; _k < array_length(_beats); _k++)
            if (_beats[_k].tipo != Beat.Correr && _beats[_k].tipo != Beat.Descanso) _saltos++;

        var _dificultad = _saltos / array_length(_beats);
        var _error = abs(_dificultad - _dificultad_objetivo);

        if (_error < _mejor_error) { _mejor_error = _error; _mejor = _beats; }
    }

    return _mejor;
}
```

> La curva de dificultad, el ritmo de descanso y el vocabulario de obstáculos son **diseño de
> niveles**, no generación: el generador solo los ejecuta. El documento hermano
> [**13 · 02 — Diseño de niveles**](./02%20-%20Diseño%20de%20niveles.md) de esta misma carpeta cubre esa parte.

---

## 9 · Terreno modificable en runtime y cómo persistirlo

Terreno destructible = **dos representaciones sincronizadas**: la rejilla lógica (colisiones, IA,
guardado) y el tilemap (dibujo). Escribe siempre en la rejilla y **deriva** el tilemap de ella,
nunca al revés.

```gml
// ---------------------------------------------------------------------------
// scr_terreno_modificable
// ---------------------------------------------------------------------------

/// @func Terreno(_ancho, _alto, _tam, _capa, _semilla)
/// @desc Rejilla lógica + tilemap sincronizados. 1 = sólido, 0 = aire.
function Terreno(_ancho, _alto, _tam, _capa, _semilla) constructor
{
    ancho   = _ancho;
    alto    = _alto;
    tam     = _tam;            // píxeles por celda
    semilla = _semilla;
    celdas  = array_create(_ancho * _alto, 1);
    mapa    = layer_tilemap_get_id(layer_get_id(_capa));

    INDICE_SOLIDO = 1;

    solido = function(_fx, _fy)
    {
        if (_fx < 0 || _fy < 0 || _fx >= ancho || _fy >= alto) return true;   // borde sólido
        return (celdas[_fy * ancho + _fx] == 1);
    };

    /// @desc Escribe una celda y actualiza SOLO ese tile. No repinta el mapa.
    escribir = function(_fx, _fy, _valor)
    {
        if (_fx < 0 || _fy < 0 || _fx >= ancho || _fy >= alto) return false;

        var _i = _fy * ancho + _fx;
        if (celdas[_i] == _valor) return false;   // nada que hacer

        celdas[_i] = _valor;
        tilemap_set(mapa, _valor == 1 ? INDICE_SOLIDO : 0, _fx, _fy);
        return true;
    };

    /// @desc Excava un círculo en coordenadas de PÍXEL. Devuelve celdas tocadas.
    excavar = function(_px, _py, _radio_px)
    {
        var _fx0 = floor((_px - _radio_px) / tam);
        var _fy0 = floor((_py - _radio_px) / tam);
        var _fx1 = floor((_px + _radio_px) / tam);
        var _fy1 = floor((_py + _radio_px) / tam);
        var _n = 0;

        for (var _fy = _fy0; _fy <= _fy1; _fy++)
            for (var _fx = _fx0; _fx <= _fx1; _fx++)
            {
                var _cx = _fx * tam + tam * 0.5;
                var _cy = _fy * tam + tam * 0.5;
                if (point_distance(_px, _py, _cx, _cy) <= _radio_px)
                    if (escribir(_fx, _fy, 0)) _n++;
            }

        return _n;
    };
}
```

> `tilemap_set_at_pixel(mapa, tiledata, x, y)` hace lo mismo aceptando **píxeles de la room**
> en vez de celdas — cuidado, porque la tabla de argumentos del manual llama a esos parámetros
> `xcell`/`ycell` aunque el texto y el ejemplo dejan claro que son píxeles. Es cómodo para un
> impacto puntual (`tilemap_set_at_pixel(mapa, 0, bala_x, bala_y)`), pero para un cráter es más
> barato calcular las celdas una vez, como arriba.

**Persistirlo.** Guarda **semilla + diff**, no el mapa entero. Pero cuando el jugador ha
reventado media montaña el diff ya no es pequeño, y un buffer binario gana por goleada a un JSON.

```gml
/// @func guardar_terreno(_terreno, _archivo)
/// @desc Cabecera (ancho, alto, semilla) + un byte por celda, comprimido.
function guardar_terreno(_terreno, _archivo)
{
    var _n   = _terreno.ancho * _terreno.alto;
    var _buf = buffer_create(12 + _n, buffer_fixed, 1);

    buffer_write(_buf, buffer_u32, _terreno.ancho);
    buffer_write(_buf, buffer_u32, _terreno.alto);
    buffer_write(_buf, buffer_u32, _terreno.semilla);
    for (var _i = 0; _i < _n; _i++) buffer_write(_buf, buffer_u8, _terreno.celdas[_i]);

    // Un terreno es casi todo ceros o unos: se comprime muchísimo.
    var _comprimido = buffer_compress(_buf, 0, buffer_get_size(_buf));
    buffer_save(_comprimido, _archivo);

    buffer_delete(_comprimido);
    buffer_delete(_buf);
}

/// @func cargar_terreno(_terreno, _archivo)
/// @desc Devuelve true si cargó. Repinta el tilemap entero al terminar.
function cargar_terreno(_terreno, _archivo)
{
    if (!file_exists(_archivo)) return false;

    var _crudo = buffer_load(_archivo);
    var _buf   = buffer_decompress(_crudo);
    buffer_delete(_crudo);
    if (_buf < 0) return false;   // fichero corrupto o de otra versión

    buffer_seek(_buf, buffer_seek_start, 0);
    var _ancho   = buffer_read(_buf, buffer_u32);
    var _alto    = buffer_read(_buf, buffer_u32);
    var _semilla = buffer_read(_buf, buffer_u32);

    if (_ancho != _terreno.ancho || _alto != _terreno.alto)
    {
        buffer_delete(_buf);
        return false;   // guardado de otra versión del mundo: no lo fuerces
    }

    _terreno.semilla = _semilla;
    for (var _i = 0; _i < _ancho * _alto; _i++)
        _terreno.celdas[_i] = buffer_read(_buf, buffer_u8);
    buffer_delete(_buf);

    for (var _fy = 0; _fy < _alto; _fy++)
        for (var _fx = 0; _fx < _ancho; _fx++)
            tilemap_set(_terreno.mapa,
                        _terreno.celdas[_fy * _ancho + _fx] == 1 ? _terreno.INDICE_SOLIDO : 0,
                        _fx, _fy);

    return true;
}
```

> Comprobar `_ancho`/`_alto` antes de leer el cuerpo **no es paranoia**: un save de una versión
> anterior con otro tamaño de mundo desborda el buffer y revienta. Referencia completa de la
> familia en [`08 · 16 — Buffers`](../08%20-%20Referencia%20GML%20completa/16%20-%20Buffers.md).

---

## 10 · Validación y métricas

Un generador sin métricas es una máquina tragaperras. Estas cuatro cubren el 90 % de los casos.

```gml
// ---------------------------------------------------------------------------
// scr_metricas_nivel
// ---------------------------------------------------------------------------

/// @func distancias_bfs(_mapa, _inicio)
/// @desc BFS desde una celda. Devuelve un array con la distancia en pasos a
///       cada celda (-1 = inalcanzable). Es la base de casi todas las métricas.
function distancias_bfs(_mapa, _inicio)
{
    var _n = _mapa.ancho * _mapa.alto;
    var _dist = array_create(_n, -1);
    if (_mapa.celdas[_inicio] == 1) return _dist;

    var _cola = [_inicio];
    var _cabeza = 0;                  // cola por índice: no reordena el array
    _dist[_inicio] = 0;

    var _dx = [1, -1, 0, 0];
    var _dy = [0, 0, 1, -1];

    while (_cabeza < array_length(_cola))
    {
        var _c = _cola[_cabeza++];
        var _cx = _c mod _mapa.ancho;
        var _cy = _c div _mapa.ancho;

        for (var _d = 0; _d < 4; _d++)
        {
            var _vx = _cx + _dx[_d];
            var _vy = _cy + _dy[_d];
            if (_vx < 0 || _vy < 0 || _vx >= _mapa.ancho || _vy >= _mapa.alto) continue;

            var _vc = _vy * _mapa.ancho + _vx;
            if (_mapa.celdas[_vc] == 1) continue;
            if (_dist[_vc] != -1) continue;

            _dist[_vc] = _dist[_c] + 1;
            array_push(_cola, _vc);
        }
    }

    return _dist;
}

/// @func medir_nivel(_mapa, _inicio, _meta)
/// @desc Las cuatro métricas que deciden si un nivel se publica o se tira.
function medir_nivel(_mapa, _inicio, _meta)
{
    var _n = _mapa.ancho * _mapa.alto;
    var _dist = distancias_bfs(_mapa, _inicio);

    var _suelo = 0;
    var _alcanzable = 0;
    var _mas_lejos = 0;

    for (var _i = 0; _i < _n; _i++)
    {
        if (_mapa.celdas[_i] == 1) continue;
        _suelo++;
        if (_dist[_i] < 0) continue;
        _alcanzable++;
        _mas_lejos = max(_mas_lejos, _dist[_i]);
    }

    return {
        // 1. Conectividad: fracción del suelo alcanzable desde el inicio.
        conectividad: (_suelo > 0) ? _alcanzable / _suelo : 0,
        // 2. Camino crítico: pasos mínimos del inicio a la meta (-1 = imposible).
        camino_critico: (_meta >= 0) ? _dist[_meta] : -1,
        // 3. Densidad: cuánto del mapa es transitable (ni claustrofóbico ni vacío).
        densidad: _suelo / _n,
        // 4. Diámetro: el punto más lejano. Mide si el mapa "da para explorar".
        diametro: _mas_lejos
    };
}

/// @func nivel_aceptable(_m)
/// @desc Los umbrales SON tu diseño. Escríbelos, no los lleves en la cabeza.
function nivel_aceptable(_m)
{
    if (_m.conectividad   < 0.92) return "desconectado";
    if (_m.camino_critico < 0)    return "meta inalcanzable";
    if (_m.camino_critico < 40)   return "demasiado corto";
    if (_m.densidad < 0.25)       return "demasiado estrecho";
    if (_m.densidad > 0.62)       return "demasiado abierto";
    return "";   // cadena vacía = aceptable
}

/// @func generar_hasta_valido(_semilla, _max_intentos)
/// @desc El bucle de §1.2 completo. Rechaza con `semilla + intento`: el mapa
///       resultante sigue estando descrito por dos números (semilla, intento).
function generar_hasta_valido(_semilla, _max_intentos)
{
    for (var _intento = 0; _intento < _max_intentos; _intento++)
    {
        var _mapa = cueva_celular(96, 64, _semilla + _intento, 0.40, 4, 3);
        conservar_region_mayor(_mapa);

        var _inicio = -1;
        var _meta   = -1;
        for (var _i = 0; _i < _mapa.ancho * _mapa.alto; _i++)
            if (_mapa.celdas[_i] == 0) { if (_inicio < 0) _inicio = _i; _meta = _i; }

        if (_inicio < 0) continue;

        var _m = medir_nivel(_mapa, _inicio, _meta);
        var _fallo = nivel_aceptable(_m);

        if (_fallo == "")
        {
            _mapa.metricas = _m;
            _mapa.intento  = _intento;
            return _mapa;
        }

        show_debug_message($"intento {_intento}: rechazado por «{_fallo}»");
    }

    show_debug_message("⚠ ningún mapa válido: revisa los umbrales, no la semilla");
    return undefined;
}
```

**Alcanzabilidad con salto (plataformas).** En un plataformas, «adyacente» no es «pegado»: dos
plataformas están conectadas si el salto llega. La comprobación es la misma que usa el
generador de §8, aplicada al revés.

```gml
/// @func alcanzable_saltando(_desde, _hasta)
/// @desc _desde y _hasta son { px, py } (borde de plataforma). Modelo balístico
///       simplificado: alcance horizontal completo solo si no hay que subir.
function alcanzable_saltando(_desde, _hasta)
{
    var _dx = abs(_hasta.px - _desde.px);
    var _dy = _desde.py - _hasta.py;   // positivo = hay que SUBIR

    if (_dy > JUGADOR_SALTO_ALTO * MARGEN_SEGURIDAD) return false;

    // Subir consume alcance horizontal; bajar lo regala.
    var _fraccion = 1 - clamp(_dy / JUGADOR_SALTO_ALTO, 0, 1) * 0.6;
    var _alcance  = JUGADOR_SALTO_LARGO * MARGEN_SEGURIDAD * _fraccion;
    if (_dy < 0) _alcance *= 1.4;   // caída: llega más lejos

    return (_dx <= _alcance);
}
```

> Para caminos con **coste por celda** (barro, agua, terreno peligroso) no reimplementes A\*:
> ya está escrito y comentado en
> [`06 · scr_grid_pathfinding.gml`](../06%20-%20Assets%20y%20Scripts/scr_grid_pathfinding.gml),
> con dos variantes (`Grid` sobre `mp_grid` y `GridPonderado` en GML puro con costes).

---

## 11 · Herramientas para depurar un generador

**Un generador que no puedes mirar no lo puedes arreglar.** Dos utilidades que cuestan media
hora y ahorran semanas.

```gml
// ---------------------------------------------------------------------------
// scr_depurar_generador
// ---------------------------------------------------------------------------

/// @func volcar_mapa_a_png(_mapa, _archivo, _colores)
/// @desc Dibuja el mapa a una surface a 1 píxel por celda y lo guarda en disco.
///       Mirar 50 PNG seguidos revela sesgos que ningún test detecta.
/// @param {Array<Real>} _colores Color por valor de celda
function volcar_mapa_a_png(_mapa, _archivo, _colores)
{
    var _sup = surface_create(_mapa.ancho, _mapa.alto);

    surface_set_target(_sup);
    draw_clear(c_black);

    for (var _fy = 0; _fy < _mapa.alto; _fy++)
        for (var _fx = 0; _fx < _mapa.ancho; _fx++)
        {
            var _v = _mapa.celdas[_fy * _mapa.ancho + _fx];
            draw_set_color(_colores[_v]);
            draw_point(_fx, _fy);
        }

    surface_reset_target();

    surface_save(_sup, _archivo);      // PNG en game_save_id si das ruta relativa
    surface_free(_sup);
}

/// @func volcar_lote(_semilla_base, _cuantos)
/// @desc Genera N mapas y los vuelca numerados. El diagnóstico más rentable
///       que existe: si 30 mapas se parecen, tu espacio de posibilidades es pobre.
function volcar_lote(_semilla_base, _cuantos)
{
    var _colores = [c_white, make_color_rgb(40, 40, 55)];   // 0 = suelo, 1 = muro

    for (var _i = 0; _i < _cuantos; _i++)
    {
        var _t0 = get_timer();
        var _mapa = cueva_celular(96, 64, _semilla_base + _i, 0.40, 4, 3);
        var _cobertura = conservar_region_mayor(_mapa);
        var _ms = (get_timer() - _t0) / 1000;

        volcar_mapa_a_png(_mapa, $"lote_{_i}.png", _colores);
        show_debug_message($"mapa {_i}: {_ms} ms · región mayor = {_cobertura}");
    }
}
```

**Panel en vivo con el Debug Overlay.** Regenerar con parámetros nuevos sin recompilar es la
diferencia entre ajustar un generador en una tarde o en una semana.

```gml
// ---------------------------------------------------------------------------
// objGeneradorDebug — Create
// ---------------------------------------------------------------------------
// ⚠️ Las variables deben vivir en un struct o una instancia: `ref_create` no
//    puede apuntar a una local. Por eso son variables de instancia.

semilla        = 12345;
relleno_pct    = 40;    // se expone como entero: los sliders enteros son más cómodos
pasos_dobles   = 4;
pasos_simples  = 3;
info           = "sin generar";

regenerar = function()
{
    var _t0 = get_timer();
    mapa = cueva_celular(96, 64, semilla, relleno_pct / 100, pasos_dobles, pasos_simples);
    var _cobertura = conservar_region_mayor(mapa);
    info = $"{(get_timer() - _t0) / 1000} ms · región mayor {_cobertura}";
    // ...y aquí repintas el tilemap.
};

siguiente_semilla = function() { semilla++; regenerar(); };

if (debug_mode)
{
    // ⚠️ `debug_mode` es una VARIABLE de solo lectura, no una función:
    //    `debug_mode()` no compila («unable to use builtin variable as a function call»).
    show_debug_overlay(true);
    dbg_view("Generador procedural", true, 20, 20, 420, 300);

    dbg_section("Parámetros");
    // Firma real (manual LTS 2026): dbg_slider_int(ref, [min], [max], [label], [step])
    dbg_slider_int(ref_create(self, "semilla"),       0, 99999, "Semilla",   1);
    dbg_slider_int(ref_create(self, "relleno_pct"),  30,    60, "Relleno %", 1);
    dbg_slider_int(ref_create(self, "pasos_dobles"),  0,     8, "Pasos R2",  1);
    dbg_slider_int(ref_create(self, "pasos_simples"), 0,     8, "Pasos R1",  1);

    dbg_section("Acciones");
    dbg_button("Regenerar",          ref_create(self, "regenerar"));
    dbg_button("Semilla siguiente",  ref_create(self, "siguiente_semilla"));

    dbg_section("Diagnóstico");
    dbg_watch(ref_create(self, "info"), "Última generación");
}

regenerar();
```

> ⚠️ **Ojo con el orden de los argumentos.** `dbg_button` es `(label, ref)` pero `dbg_watch`,
> `dbg_checkbox` y `dbg_slider_int` son `(ref, …, label)`. Es asimétrico y el compilador no te
> avisa: comprueba cada uno con `gm-cli manual read "dbg_slider_int"`. La familia completa está
> en [`01 · 15 — Depuración y rendimiento`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md).

---

## 12 · Checklist

Antes de dar por bueno un generador:

- [ ] `randomize()` se llama **una vez**, al arrancar, y nunca más.
- [ ] Todas las llamadas a `random_set_seed` pasan `true` como segundo argumento.
- [ ] La generación usa un `RNG` propio, **no** el global, y uno distinto por sistema.
- [ ] Reiniciar la partida con la misma semilla produce **exactamente** el mismo mundo.
- [ ] Existe una función que **mide** el resultado y un umbral escrito para cada métrica.
- [ ] El bucle de reintento tiene **tope** y un plan B si se agota.
- [ ] Nada del generador se ejecuta en un evento **Draw**.
- [ ] El ruido se ha **medido**: sabes su mínimo y su máximo reales, no los supuestos.
- [ ] Los mapas se pueden **volcar a PNG** y los has mirado (50, no 3).
- [ ] Hay un panel de Debug Overlay para regenerar en vivo.
- [ ] El generador devuelve **datos**; ninguna función suya crea instancias ni dibuja.
- [ ] Se ha medido con `get_timer()` en el objetivo real, no solo en el editor.
- [ ] Los guardados almacenan la semilla (y el diff), nunca el mapa entero.

---

## 13 · Errores clásicos

| Error | Síntoma | Solución |
|---|---|---|
| No resembrar al reiniciar | Todas las partidas dan el mismo mundo | `randomize()` al arrancar; guarda `random_get_seed()` |
| `random_set_seed(v)` sin el `true` | Semillas que producen mundos sospechosamente parecidos | Segundo argumento `true`: el sembrado antiguo es defectuoso según el manual |
| Usar el RNG global en la generación | El nivel cambia según cuánto disparaste antes | Un `RNG` propio por sistema (04/05 §5.0) |
| Ruido sin normalizar | El mundo es 90 % agua o 90 % roca y los umbrales «no funcionan» | `medir_rango_ruido` antes de poner un solo umbral |
| Muestrear ruido en el evento Draw | 8 fps con un mapa mediano | Precalcular a un array en Create; pintar a tilemap |
| Construir `RuidoPerlin` dentro del bucle | Barajar 256 elementos por celda | Construirlo una vez y guardarlo |
| `array_create(h, array_create(w, 0))` | Cambiar una fila cambia todas | `array_create_ext`, o mejor un array plano |
| Leer y escribir el mismo array en un autómata | Las cuevas «se derriten» hacia una esquina | Buffer doble y `array_copy` al final de la pasada |
| Autómata sin conectar regiones | Cuevas aisladas donde el jugador no puede llegar | `conservar_region_mayor` o excavar túneles |
| WFC sin backtracking ni reintento | El generador devuelve `undefined` y la room sale vacía | Reintentar con semilla derivada, tope y **plan B** |
| WFC sobre una rejilla grande | Segundos de congelación al generar | Reducir tiles, trocear la rejilla, o autotiling |
| Poisson con anillo `r·(1+u)` | Puntos amontonados a distancia casi exacta `r` | `r·sqrt(1 + 3u)`: uniforme por área (Bridson) |
| Gramática recursiva sin tope | Cuelgue o desbordamiento de pila | Parámetro `_profundidad` que decrece siempre |
| L-system con demasiadas iteraciones | Cadenas de millones de caracteres | Tope de longitud además del de iteraciones |
| `room_instance_add` sobre una room del proyecto | Instancias duplicadas que sobreviven a `game_restart()` | `room_add()` + `room_assign()`, o piezas como datos |
| Arrays 2D anidados en mapas grandes | El generador tarda el triple sin motivo aparente | Array plano `celdas[fy * ancho + fx]` |
| Guardar el mapa entero en el save | Saves enormes que rompen al cambiar de versión | Semilla + diff; y valida la cabecera al cargar |
| Sin métricas | «A veces sale mal» y nadie sabe cuándo | `medir_nivel` + umbrales escritos + volcado a PNG |

---

## Ver también

- [`04 · 05 — Roguelike y generación procedural`](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md) — RNG con semilla, BSP, random walk, flood fill, FOV y tablas de botín. **Empieza por ahí.**
- [`04 · 09 — Survival y crafting`](../04%20-%20Recetas%20por%20g%C3%A9nero/09%20-%20Survival%20y%20crafting.md) — chunking de mundos grandes y el patrón `diff` para persistir solo lo que cambió.
- [`06 · scr_grid_pathfinding.gml`](../06%20-%20Assets%20y%20Scripts/scr_grid_pathfinding.gml) — A\* con y sin costes por celda, para medir caminos críticos de verdad.
- [`01 · 10 — Rooms, capas, cámaras y viewports`](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20c%C3%A1maras%20y%20viewports.md) — §4: tile sets, el *blob* de datos de tile y las máscaras de bits.
- [`08 · 09 — Dibujo de tiles y tilemaps`](../08%20-%20Referencia%20GML%20completa/09%20-%20Dibujo%20de%20tiles%20y%20tilemaps.md) — la familia `tilemap_*` entera, argumento a argumento.
- [`08 · 14 — Arrays`](../08%20-%20Referencia%20GML%20completa/14%20-%20Arrays.md) — `array_create_ext`, semántica de referencia y funciones con callback.
- [`08 · 16 — Buffers`](../08%20-%20Referencia%20GML%20completa/16%20-%20Buffers.md) — tipos, alineación, compresión y guardado en disco.
- [`08 · 10 — Matemáticas`](../08%20-%20Referencia%20GML%20completa/10%20-%20Matem%C3%A1ticas.md) — referencia de `random_*`, `lerp`, `clamp` y compañía.
- [`01 · 15 — Depuración y rendimiento`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md) — Debug Overlay, vistas propias y medición con `get_timer`.
- [`02 · 08 — Package Manager y Prefabs`](../02%20-%20Novedades%202026/08%20-%20Package%20Manager%20y%20Prefabs.md) — distribuir piezas de contenido entre proyectos.
- [`12 · 05 — Pipeline de arte, audio y niveles`](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md) — librerías GML ya escritas de WFC, autómatas celulares y terreno destructible.
- [`13 · 01 — Diseño de juego`](./01%20-%20Dise%C3%B1o%20de%20juego%20-%20core%20loop,%20mec%C3%A1nicas,%20balance%20y%20dificultad.md) — la curva de dificultad que el generador ejecuta.

---

## Fuentes

Todas consultadas el **6 de septiembre de 2026**.

**Manual oficial de GameMaker (espejo local, LTS 2026)**

- `random_set_seed` (incluido el argumento `fix_range_bug`) — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Number_Functions/random_set_seed.htm>
- `tilemap_set_at_pixel` — <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_set_at_pixel.htm>
- `room_duplicate` — <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Rooms/room_duplicate.htm>
- `room_instance_add` — <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Rooms/room_instance_add.htm>
- `dbg_slider_int` — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Debugging/dbg_slider_int.htm>

**Ruido**

- Ken Perlin, *Improving Noise*, SIGGRAPH 2002 — <https://mrl.cs.nyu.edu/~perlin/paper445.pdf> · curva `6t⁵-15t⁴+10t³`, los 12 gradientes de las aristas del cubo y la discontinuidad de segundo orden de la curva antigua.
- Amit Patel (Red Blob Games), *Making maps with noise functions*, 2015 (act. 2022) — <https://www.redblobgames.com/maps/terrain-from-noise/> · elevación + humedad → biomas, amplitudes `[1, 0.5, 0.25]` divididas por su suma, redistribución por exponente, «square bump» para islas y la advertencia sobre rangos.
- Amit Patel, *Hexagonal grids* — <https://www.redblobgames.com/grids/hexagons/> (act. 24-07-2026) · si generas sobre hexágonos en vez de cuadrados.

**Autómatas celulares**

- RogueBasin, *Cellular Automata Method for Generating Random Cave-Like Levels* — <http://www.roguebasin.com/index.php?title=Cellular_Automata_Method_for_Generating_Random_Cave-Like_Levels> · la regla `R1(p) >= 5 || R2(p) <= 2`, relleno inicial del 40 % y la secuencia de 4 + 3 pasadas. ⚠️ La página devuelve **403** al acceso directo; se leyó a través de un proxy de lectura sobre esa misma URL.

**Muestreo**

- Robert Bridson, *Fast Poisson Disk Sampling in Arbitrary Dimensions*, SIGGRAPH 2007 sketch — <https://www.cs.ubc.ca/~rbridson/docs/bridson-siggraph07-poissondisk.pdf> · celda `r/√n`, lista activa, `k = 30`, anillo `[r, 2r]`, `2N-1` iteraciones.

**Wave Function Collapse**

- Boris the Brave, *Wave Function Collapse explained*, 13-04-2020 (act. 28-02-2025) — <https://www.boristhebrave.com/2020/04/13/wave-function-collapse-explained/> · WFC como problema de restricciones, entropía de Shannon con pesos, y por qué la implementación de referencia se salta el backtracking.
- Maxim Gumin, repositorio `mxgmn/WaveFunctionCollapse` (MIT) — <https://github.com/mxgmn/WaveFunctionCollapse> · modelos *overlapping* y *simple tiled*, atribución a la *Model Synthesis* de Paul Merrell (2009) y el comportamiento ante contradicciones.
- Boris the Brave, *Dungeon generation in Unexplored*, 10-04-2021 — <https://www.boristhebrave.com/2021/04/10/dungeon-generation-in-unexplored/> · el caso contrario: reescritura de grafos en vez de restricciones locales.

**Gramáticas y estructura**

- Przemyslaw Prusinkiewicz y Aristid Lindenmayer, *The Algorithmic Beauty of Plants*, Springer 1990 (edición electrónica libre) — <http://algorithmicbotany.org/papers/#abop> · `G = ⟨V, ω, P⟩` y la aplicación **en paralelo** de las producciones frente a las gramáticas de Chomsky.
- Gillian Smith, Mike Treanor, Jim Whitehead y Michael Mateas, *Rhythm-Based Level Generation for 2D Platformers*, FDG/ICFDG 2009 — <https://eis.ucsc.edu/papers/smith-fdg-09.pdf> · *rhythm groups*, gramática de dos capas (ritmo → geometría), métricas del avatar y el filtrado con *critics* sobre 1 000 candidatos.
- Noor Shaker, Julian Togelius y Mark J. Nelson, *Procedural Content Generation in Games*, Springer 2016 (libre en la web de los autores) — <https://www.pcgbook.com/> · la definición *«the algorithmic creation of game content with limited or indirect user input»*, y los capítulos 3 (métodos constructivos), 4 (fractales y ruido) y 5 (gramáticas y L-systems).
