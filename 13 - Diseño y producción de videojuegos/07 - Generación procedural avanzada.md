# 07 · Generación procedural avanzada

> Este documento es la **caja de herramientas de PCG que no cabe en un roguelike**: ruido,
> autómatas celulares, ríos sobre el mapa de alturas, laberintos, Poisson-disc, Wave
> Function Collapse, gramáticas, ensamblaje por piezas con reparto de roles y niveles
> de plataformas por ritmo. Todo con GML verificado contra el runtime
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
randomize();                        // UNA vez, al arrancar el juego (p. ej. en el Create del
                                     // primer objeto persistente — 13 · 06 §3.2)
global.semilla = random_get_seed(); // guárdala: es tu partida entera. Todo generador de este
                                     // documento la lee (§2.8 en adelante) — sin ella revienta
                                     // el primero que se ejecute.

random_set_seed(global.semilla, true);   // ⚠️ el segundo argumento importa (ver abajo)
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

pintar_mundo(mundo, mapa_tiles);
```

> ⚠️ **`pintar_mundo()` va en un script, no en este `Create` — y `INDICE_POR_BIOMA` no es
> una variable de instancia, es una tabla constante.** El documento la llama más abajo
> desde `objGeneradorAsincrono` y `objControladorCarga` (§2.9), ninguno de los dos
> `objMundo`. `#macro` es la forma correcta de declarar una constante en GML —
> `const` no existe (`AGENTS.md`) — y así `INDICE_POR_BIOMA` queda accesible desde
> cualquier sitio sin que `pintar_mundo()` dependa de ningún `self` en absoluto. Dejar
> `pintar_mundo()` en el `Create` revienta con `Variable X.pintar_mundo(...) not set
> before reading it` en cuanto la llama otro objeto — el mismo mecanismo de
> [`04 · 19` §1](../04%20-%20Recetas%20por%20g%C3%A9nero/19%20-%20Programaci%C3%B3n%20r%C3%ADtmica%20%28juegos%20de%20ritmo%29.md#1--el-conductor).

```gml
// scr_pintar_mundo.gml

// Índice de tile dentro del tileset, uno por bioma. 0 = celda vacía.
#macro INDICE_POR_BIOMA [ 1, 2, 3, 4, 5, 6 ]   // Agua, Playa, Hierba, Bosque, Roca, Nieve

/// @func pintar_mundo(_mundo, _mapa_tiles)
/// @desc Vuelca el array de biomas al tilemap. Se llama UNA vez por generación.
function pintar_mundo(_mundo, _mapa_tiles)
{
    var _t0 = get_timer();
    var _tabla = INDICE_POR_BIOMA;

    for (var _fy = 0; _fy < _mundo.alto; _fy++)
    {
        for (var _fx = 0; _fx < _mundo.ancho; _fx++)
        {
            var _bioma = _mundo.biomas[_fy * _mundo.ancho + _fx];
            tilemap_set(_mapa_tiles, _tabla[_bioma], _fx, _fy);
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

## 2 bis · Ríos: del mapa de alturas al cauce

Un río dibujado a mano sobre un mapa generado **siempre se nota**. Cruza una montaña, nace en
mitad de una llanura o desemboca hacia arriba. La razón es que un río no es una forma: es la
**consecuencia** de un mapa de alturas. Si el terreno lo genera el ruido de §2, el cauce tiene
que salir del mismo terreno o el jugador percibe la costura aunque no sepa nombrarla.

El método completo son tres pasos, y **el primero es el que casi todo el mundo se salta**.

### 2 bis .1 Por qué «ir cuesta abajo» no funciona

El impulso natural es: pon un manantial en un pico, mira los ocho vecinos, muévete al más bajo,
repite. Sobre ruido fBm eso **se atasca en la tercera o cuarta celda**. Un mapa de Perlin está
lleno de mínimos locales: hoyos de una sola celda rodeados de celdas más altas. El río llega
ahí y no tiene a dónde ir.

Los parches habituales empeoran el resultado:

| Parche | Qué produce |
|---|---|
| Si te atascas, salta a un vecino al azar | El río sube cuestas. Se ve inmediatamente |
| Si te atascas, para | Ríos de seis celdas que no llegan al mar |
| Suavizar mucho el terreno antes | Un mundo sin relieve, y los hoyos siguen ahí |
| Bajar el mínimo local a la fuerza | Zanjas de una celda en mitad de la nada |

La solución de verdad viene de la hidrología, no del *gamedev*: **rellenar las depresiones
antes de trazar nada**. Sobre una superficie sin depresiones, «ir cuesta abajo» no puede
atascarse — por construcción, toda celda tiene un camino no ascendente hasta el borde del mapa.

### 2 bis .2 Paso 1 — Rellenar depresiones (*priority-flood*)

El algoritmo es de Barnes, Lehman y Mulla (2014) y es sorprendentemente corto: mete todo el
borde del mapa en una cola de prioridad ordenada por altura, y ve sacando siempre la celda más
baja. Cada vecino que salga se queda con **la mayor de dos alturas**: la suya y la de la celda
por la que se ha llegado. Un hoyo se llena hasta el nivel de su punto de escape, exactamente
como se llenaría de agua.

```gml
/// @func rellenar_depresiones(_alt, _ancho, _alto)
/// @desc Devuelve una copia de _alt sin mínimos locales (Priority-Flood, Barnes 2014).
///       Toda celda del resultado tiene un camino NO ascendente hasta el borde.
/// @param {Array<Real>} _alt   Mapa de alturas original (no se modifica)
/// @param {Real} _ancho
/// @param {Real} _alto
/// @return {Array<Real>} Superficie rellenada
function rellenar_depresiones(_alt, _ancho, _alto)
{
    var _n       = _ancho * _alto;
    var _relleno = array_create(_n, 0);
    var _visto   = array_create(_n, false);
    var _cola    = ds_priority_create();

    // El borde entero es la condición de contorno: desde ahí el agua ya escapa.
    for (var _y = 0; _y < _alto; _y++)
    {
        for (var _x = 0; _x < _ancho; _x++)
        {
            if (_x > 0 && _x < _ancho - 1 && _y > 0 && _y < _alto - 1) continue;

            var _i = _y * _ancho + _x;
            _relleno[_i] = _alt[_i];
            _visto[_i]   = true;
            ds_priority_add(_cola, _i, _alt[_i]);
        }
    }

    var _dx = [ 1, 1, 0, -1, -1, -1,  0,  1];
    var _dy = [ 0, 1, 1,  1,  0, -1, -1, -1];

    while (ds_priority_size(_cola) > 0)
    {
        var _c  = ds_priority_delete_min(_cola);
        var _cx = _c mod _ancho;
        var _cy = _c div _ancho;

        for (var _k = 0; _k < 8; _k++)
        {
            var _nx = _cx + _dx[_k];
            var _ny = _cy + _dy[_k];
            if (_nx < 0 || _ny < 0 || _nx >= _ancho || _ny >= _alto) continue;

            var _ni = _ny * _ancho + _nx;
            if (_visto[_ni]) continue;

            // Aquí está todo el algoritmo: nunca por debajo de la celda de llegada.
            _relleno[_ni] = max(_alt[_ni], _relleno[_c]);
            _visto[_ni]   = true;
            ds_priority_add(_cola, _ni, _relleno[_ni]);
        }
    }

    ds_priority_destroy(_cola);
    return _relleno;
}
```

> ⚠️ **`ds_priority_delete_min` devuelve el valor, no la prioridad.** Es el error de uso más
> común de esta estructura: quien espera la altura recibe el índice de celda y el algoritmo
> produce basura sin fallar. Si necesitas también la prioridad, guárdala tú en `_relleno`
> como hace el código de arriba.

**Las mesetas.** Rellenar deja zonas perfectamente planas — el interior de cada hoyo relleno.
Sobre una meseta exacta, «el vecino más bajo» es un empate y el trazado se queda dando vueltas.
La corrección estándar es inclinar la meseta un épsilon en el sentido en que se rellenó:

```gml
// Tras rellenar: si la celda no cambió de altura, no estaba en un hoyo.
// Si cambió, súbela un pelo más que su vecina de llegada para romper el empate.
#macro RIO_EPSILON 0.000001
```

Ese épsilon es **invisible en el terreno** (una millonésima de la escala de altura) y suficiente
para que la comparación de reales dé un ganador. No uses un valor mucho menor: los reales de GML
son *double* y a partir de cierto punto el épsilon se pierde al sumarse a una altura cercana a 1.

### 2 bis .3 Paso 2 — Dirección y acumulación de flujo (D8)

Con la superficie rellenada, cada celda tiene un destino único: su vecino más bajo. Es el modelo
**D8** — ocho direcciones, una sola salida por celda. Y una vez sabes a dónde va cada celda,
sabes **cuánta agua pasa por cada una**: la suya más la de todas las que desembocan en ella.

Eso es lo que decide qué es un río y qué es un arroyo. No hace falta elegir manantiales: los
manantiales salen solos, allí donde la acumulación cruza un umbral.

```gml
/// @func calcular_flujo(_relleno, _ancho, _alto)
/// @desc D8: a dónde va cada celda y cuánta agua acumula.
/// @return {Struct} { destino, acumulacion }  — ambos arrays de _ancho * _alto.
///                  destino[i] == -1 significa que el agua sale del mapa por ahí.
function calcular_flujo(_relleno, _ancho, _alto)
{
    var _n       = _ancho * _alto;
    var _destino = array_create(_n, -1);
    var _acum    = array_create(_n, 1);   // cada celda aporta su propia lluvia

    var _dx = [ 1, 1, 0, -1, -1, -1,  0,  1];
    var _dy = [ 0, 1, 1,  1,  0, -1, -1, -1];
    // La diagonal recorre más terreno: se compara pendiente, no desnivel bruto.
    var _dist = [1, 1.4142135623730951, 1, 1.4142135623730951,
                 1, 1.4142135623730951, 1, 1.4142135623730951];

    for (var _y = 0; _y < _alto; _y++)
    {
        for (var _x = 0; _x < _ancho; _x++)
        {
            var _i = _y * _ancho + _x;

            // El borde es sumidero: el agua abandona el mapa.
            if (_x == 0 || _y == 0 || _x == _ancho - 1 || _y == _alto - 1) continue;

            var _mejor      = -1;
            var _mejor_pend = 0;

            for (var _k = 0; _k < 8; _k++)
            {
                var _ni = (_y + _dy[_k]) * _ancho + (_x + _dx[_k]);
                var _p  = (_relleno[_i] - _relleno[_ni]) / _dist[_k];
                if (_p > _mejor_pend)
                {
                    _mejor_pend = _p;
                    _mejor      = _ni;
                }
            }

            _destino[_i] = _mejor;
        }
    }

    // Acumular de arriba abajo: si procesas las celdas de mayor a menor altura,
    // cuando llegas a una ya has sumado todo lo que le llega desde arriba.
    var _orden = array_create(_n, 0);
    for (var _i = 0; _i < _n; _i++) _orden[_i] = _i;

    array_sort(_orden, function(_a, _b)
    {
        // Descendente por altura. El array de alturas viaja por `global` porque
        // el comparador de array_sort no admite argumentos extra.
        var _h = global.__rio_relleno;
        if (_h[_a] < _h[_b]) return  1;
        if (_h[_a] > _h[_b]) return -1;
        return 0;
    });

    for (var _j = 0; _j < _n; _j++)
    {
        var _i = _orden[_j];
        var _d = _destino[_i];
        if (_d >= 0) _acum[_d] += _acum[_i];
    }

    return { destino: _destino, acumulacion: _acum };
}
```

> ⚠️ **El comparador de `array_sort` recibe exactamente dos argumentos.** No hay forma de
> pasarle el mapa de alturas como parámetro, y una función anónima declarada dentro de otra
> **no captura** las variables locales de la que la contiene: `_relleno` no existe dentro del
> comparador. Por eso el código lo publica en `global.__rio_relleno` justo antes de ordenar.
> Es feo y es deliberado; la alternativa (ordenar a mano con un `ds_priority`) cuesta el doble
> de líneas para el mismo resultado. Asigna la global **antes** de la llamada:
>
> ```gml
> global.__rio_relleno = _relleno;
> var _flujo = calcular_flujo(_relleno, _ancho, _alto);
> ```

**Qué umbral.** La acumulación de una celda es «cuántas celdas drenan por aquí». En un mapa de
192×128 (24 576 celdas), un umbral de 60-120 da una red de ríos con dos o tres cauces
principales; 500 deja un único río; 20 llena el mapa de regatos. Escálalo con el mapa: lo que
importa es la fracción, no el número.

**El ancho no es lineal.** Un río con el cuádruple de cuenca no es cuatro veces más ancho. La
relación empírica en hidrología es aproximadamente la raíz cuadrada del caudal, y visualmente
funciona muy bien:

```gml
/// @func ancho_de_rio(_acumulacion, _umbral, _ancho_max)
/// @desc Ancho en celdas, creciendo como la raíz de la cuenca drenada.
function ancho_de_rio(_acumulacion, _umbral, _ancho_max)
{
    if (_acumulacion < _umbral) return 0;
    return min(_ancho_max, sqrt(_acumulacion / _umbral));
}
```

### 2 bis .4 Paso 3 — Excavar el cauce

Marcar celdas como «agua» en el tilemap da un río plano pegado encima del terreno. Un río de
verdad **ha excavado un valle**: hunde el cauce en el mapa de alturas *original* (no en el
rellenado) y deja que el degradado alcance a las celdas vecinas.

```gml
/// @func excavar_cauces(_alt, _flujo, _ancho, _alto, _umbral, _profundidad)
/// @desc Hunde el terreno donde pasa el río, con caída suave hacia las orillas.
///       Modifica _alt IN PLACE y devuelve el array de anchos por celda.
function excavar_cauces(_alt, _flujo, _ancho, _alto, _umbral, _profundidad)
{
    var _acum   = _flujo.acumulacion;
    var _anchos = array_create(_ancho * _alto, 0);

    for (var _y = 1; _y < _alto - 1; _y++)
    {
        for (var _x = 1; _x < _ancho - 1; _x++)
        {
            var _i = _y * _ancho + _x;
            var _w = ancho_de_rio(_acum[_i], _umbral, 4);
            if (_w <= 0) continue;

            _anchos[_i] = _w;

            var _radio = ceil(_w);
            for (var _oy = -_radio; _oy <= _radio; _oy++)
            {
                for (var _ox = -_radio; _ox <= _radio; _ox++)
                {
                    var _vx = _x + _ox;
                    var _vy = _y + _oy;
                    if (_vx < 0 || _vy < 0 || _vx >= _ancho || _vy >= _alto) continue;

                    var _d = point_distance(0, 0, _ox, _oy);
                    if (_d > _radio) continue;

                    // 1 en el eje del cauce, 0 en la orilla.
                    var _caida = 1 - (_d / (_radio + 1));
                    var _vi    = _vy * _ancho + _vx;
                    _alt[_vi] -= _profundidad * _caida * _caida;
                }
            }
        }
    }

    return _anchos;
}
```

Con `_profundidad` entre 0,02 y 0,06 sobre alturas normalizadas a 0-1, el valle se lee sin que
el mapa parezca acuchillado. Por encima de 0,1 se convierte en un cañón — que puede ser
justo lo que quieres para un bioma concreto, pero decídelo, no lo heredes.

### 2 bis .5 El montaje completo

```gml
/// @func generar_mundo_con_rios(_ancho, _alto, _semilla)
/// @desc Ruido → depresiones rellenas → flujo → cauces excavados.
/// @return {Struct} { alturas, anchos_rio, acumulacion }
function generar_mundo_con_rios(_ancho, _alto, _semilla)
{
    // 1. Terreno base con el Perlin de §2.3 y el fBm de §2.5.
    var _alt   = array_create(_ancho * _alto, 0);
    var _ruido = new RuidoPerlin(_semilla);

    for (var _y = 0; _y < _alto; _y++)
        for (var _x = 0; _x < _ancho; _x++)
            _alt[_y * _ancho + _x] =
                clamp(ruido_fbm(_ruido, _x * 0.02, _y * 0.02, 5, 2, 0.5)
                      / (2 * RUIDO_INV_RAIZ2) + 0.5, 0, 1);

    // 2. Superficie hidrológica: sin ella el paso 3 se atasca.
    var _relleno = rellenar_depresiones(_alt, _ancho, _alto);

    // 3. Flujo. La global es requisito del comparador, ver §2 bis .3.
    global.__rio_relleno = _relleno;
    var _flujo = calcular_flujo(_relleno, _ancho, _alto);

    // 4. Excavar sobre el terreno ORIGINAL, no sobre el rellenado:
    //    los hoyos rellenos son lagos, y un lago no se excava.
    var _umbral = (_ancho * _alto) * 0.004;
    var _anchos = excavar_cauces(_alt, _flujo, _ancho, _alto, _umbral, 0.04);

    return { alturas: _alt, anchos_rio: _anchos, acumulacion: _flujo.acumulacion };
}
```

**Los lagos salen gratis.** Una celda cuyo relleno quedó por encima de su altura original estaba
en un hoyo: `_relleno[i] > _alt[i] + RIO_EPSILON` es exactamente la definición de «bajo el agua
de un lago», y la diferencia entre ambos valores es la profundidad. No hace falta un algoritmo
aparte para lagos; ya lo has calculado en el paso 1.

```gml
/// @func es_lago(_alt, _relleno, _i)
function es_lago(_alt, _relleno, _i)
{
    return (_relleno[_i] - _alt[_i]) > RIO_EPSILON;
}
```

### 2 bis .6 Coste y cuándo no hacerlo

En un mapa de 192×128 sobre el runtime 2026.0.0.23, el reparto es aproximadamente: el ruido fBm
domina, el *priority-flood* añade un `ds_priority` de 24 576 entradas, y la ordenación para la
acumulación es el otro término. **Todo esto se hace una vez por mundo**, en el Create o —mejor—
troceado con el patrón retomable de §14. Nada de esto va en un evento Step.

Tres casos en los que **no** merece la pena:

- **Mapa por trozos infinito.** El *priority-flood* necesita el mapa entero para saber dónde
  escapa el agua; no se puede calcular por *chunks* sin costuras. Para mundos infinitos, los
  ríos se trazan como curvas autoritarias (L-system de §6.1) y el terreno se adapta a ellas,
  no al revés.
- **Vista lateral.** Un río en un plataformas es una decoración con colisión, no una red de
  drenaje.
- **Mapas menores de ~64×64.** La red no tiene espacio para ramificarse y sale un único
  chorretón. Dibuja el río a mano y ahórrate las tres pasadas.

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

## 3 bis · Poda de callejones sin salida

Un autómata celular ya conectado (§3.1) sigue lleno de **puntas ciegas**: celdas de suelo con un
único vecino transitable. Algunas son intencionadas (un cofre al fondo de un ramal), pero la
mayoría son ruido que alarga el recorrido sin añadir nada. Dos usos opuestos para la misma
detección: **rellenarlas** (mazmorra más directa) o **marcarlas** como candidatas a sala secreta
en vez de tocarlas — la tercera capa de secretos de
[13 · 02 §1.5](./02%20-%20Diseño%20de%20niveles.md#15-riesgo-recompensa-secretos-y-atajos).

```gml
// ---------------------------------------------------------------------------
// scr_callejones
// Verificado: array_create, array_length, array_push
// ---------------------------------------------------------------------------

/// @func contar_vecinos_suelo(_celdas, _ancho, _alto, _fx, _fy)
/// @desc Vecinos de SUELO en las 4 direcciones ortogonales (sin diagonales):
///       un callejón sin salida es una cuestión de conectividad de paso, no
///       de vecindad de muro como `contar_muros` (§3).
function contar_vecinos_suelo(_celdas, _ancho, _alto, _fx, _fy)
{
    var _n  = 0;
    var _dx = [1, -1, 0, 0];
    var _dy = [0, 0, 1, -1];

    for (var _d = 0; _d < 4; _d++)
    {
        var _vx = _fx + _dx[_d];
        var _vy = _fy + _dy[_d];
        if (_vx < 0 || _vy < 0 || _vx >= _ancho || _vy >= _alto) continue;
        if (_celdas[_vy * _ancho + _vx] == 0) _n++;
    }

    return _n;
}

/// @func encontrar_callejones(_cueva)
/// @desc Celdas de suelo con EXACTAMENTE 1 vecino de suelo: por definición,
///       la punta de un callejón sin salida (o de una cámara de acceso único).
/// @return {Array<Real>} Índices dentro de _cueva.celdas
function encontrar_callejones(_cueva)
{
    var _ancho = _cueva.ancho;
    var _alto  = _cueva.alto;
    var _lista = [];

    for (var _fy = 0; _fy < _alto; _fy++)
        for (var _fx = 0; _fx < _ancho; _fx++)
        {
            var _i = _fy * _ancho + _fx;
            if (_cueva.celdas[_i] == 1) continue;
            if (contar_vecinos_suelo(_cueva.celdas, _ancho, _alto, _fx, _fy) == 1)
                array_push(_lista, _i);
        }

    return _lista;
}

/// @func podar_callejones(_cueva, _max_pasadas)
/// @desc Rellena de muro los callejones, PASADA A PASADA: al sellar la punta,
///       su vecino puede convertirse en la nueva punta (erosión desde el
///       final del ramal hacia la sala de la que cuelga). Se detiene cuando
///       no aparecen más o se agota el tope — un ramal corto desaparece
///       entero; uno que lleva a una sala grande se acorta hasta la puerta.
/// @return {Real} Cuántas celdas se sellaron en total.
function podar_callejones(_cueva, _max_pasadas)
{
    var _selladas = 0;

    for (var _pasada = 0; _pasada < _max_pasadas; _pasada++)
    {
        var _callejones = encontrar_callejones(_cueva);
        if (array_length(_callejones) == 0) break;

        for (var _i = 0; _i < array_length(_callejones); _i++)
            _cueva.celdas[_callejones[_i]] = 1;

        _selladas += array_length(_callejones);
    }

    return _selladas;
}
```

> ⚠️ **Poda sin criterio se come ramales enteros que sí importan.** Si el mapa tiene una entrada
> y una salida marcadas (§10), exclúyelas de `encontrar_callejones` (o limita `_max_pasadas`):
> de lo contrario un pasillo recto hacia la meta, que solo tiene puertas en sus dos extremos, se
> rellena igual que cualquier ramal muerto.

Para la variante de **secretos**, no rellenes nada: usa `encontrar_callejones()` directamente y
reserva esas celdas para una sala pequeña con un ítem, un tesoro o un atajo — la técnica de
señalización y recompensa ya está en
[13 · 02 §1.5](./02%20-%20Diseño%20de%20niveles.md#15-riesgo-recompensa-secretos-y-atajos).

---

## 3 ter · Marching squares: contornos suaves

`cueva_celular()` (§3) devuelve un campo **binario**: 1 muro, 0 suelo. Pintado a tilemap
celda a celda, cada esquina es un ángulo recto — funciona, pero se nota la rejilla. *Marching
squares* extrae el **contorno** de ese campo como una polilínea que corta las celdas por donde
corresponde, no por sus bordes: el mismo dato, una silueta mucho más orgánica encima.

**La idea, en una frase de Jamie Wong** (*Metaballs and Marching Squares*, 2014): cada celda de
la rejilla se examina esquina a esquina, y las cuatro esquinas —dentro o fuera del contorno—
generan *"2⁴ posibles configuraciones"*, numeradas 0-15 al leerlas como un número binario. Con
esa tabla, y con interpolación lineal en el borde donde el campo cruza el umbral, la línea deja
de tener solo ángulos de 90° y 45° y pasa por el punto exacto donde el valor cambia.

### La tabla de 16 casos

Esquinas numeradas en sentido horario desde arriba-izquierda: `SI` (bit 1), `SD` (bit 2), `ID`
(bit 4), `II` (bit 8). El caso es la suma de los bits de las esquinas que están **dentro**
(≥ umbral). Los bordes de la celda son N (arriba), E (derecha), S (abajo), O (izquierda).

| Caso | Esquinas dentro | Segmento(s) | Caso | Esquinas dentro | Segmento(s) |
|---|---|---|---|---|---|
| 0 | ninguna | — (celda vacía) | 8 | II | S–O |
| 1 | SI | O–N | 9 | SI, II | N–S |
| 2 | SD | N–E | 10 | SD, II | *silla* |
| 3 | SI, SD | O–E | 11 | SI, SD, II | E–S |
| 4 | ID | E–S | 12 | ID, II | O–E |
| 5 | SI, ID | *silla* | 13 | SI, ID, II | N–E |
| 6 | SD, ID | N–S | 14 | SD, ID, II | O–N |
| 7 | SI, SD, ID | O–S | 15 | todas | — (celda llena) |

Los casos **5** y **10** son la *silla de montar*: dos esquinas opuestas dentro y las otras dos
fuera admite dos lecturas distintas (¿están las dos esquinas "dentro" conectadas por el centro, o
separadas?). El desempate estándar mira el promedio de las 4 esquinas contra el umbral.

### Del binario al continuo: por qué hace falta suavizar el campo primero

Con un campo estrictamente 0/1, el cruce de cada borde cae **siempre en su punto medio**: mejor
que los escalones de un tile, pero sigue siendo una rejilla de segmentos de igual longitud, no
una curva. Para un contorno de verdad, cada **vértice** de la rejilla necesita un valor continuo.
El truco barato: la fracción de las hasta 4 celdas que tocan ese vértice que son muro — reutiliza
exactamente el conteo de `contar_muros` (§3), a otra escala.

```gml
// ---------------------------------------------------------------------------
// scr_marching_squares
// Verificado: draw_primitive_begin, draw_primitive_end, draw_vertex, pr_linelist
// ---------------------------------------------------------------------------

/// @func valor_vertice_cueva(_cueva, _vx, _vy)
/// @desc Valor continuo [0, 1] en el VÉRTICE (_vx, _vy) de la rejilla: fracción
///       de las hasta 4 celdas que lo tocan que son muro. Fuera del mapa
///       cuenta como muro (mismo criterio de borde sellado que `contar_muros`).
function valor_vertice_cueva(_cueva, _vx, _vy)
{
    var _ancho = _cueva.ancho;
    var _alto  = _cueva.alto;
    var _suma  = 0;

    var _ox = [-1, 0, -1, 0];
    var _oy = [-1, -1, 0, 0];

    for (var _k = 0; _k < 4; _k++)
    {
        var _cx = _vx + _ox[_k];
        var _cy = _vy + _oy[_k];

        if (_cx < 0 || _cy < 0 || _cx >= _ancho || _cy >= _alto) { _suma += 1; continue; }
        _suma += _cueva.celdas[_cy * _ancho + _cx];
    }

    return _suma / 4;
}

/// @func campo_vertices_cueva(_cueva)
/// @desc Precalcula el campo continuo en TODOS los vértices de golpe: una
///       rejilla de (ancho+1)×(alto+1) valores. Se hace una vez (§2.9);
///       `marching_squares_lista` la recorre muchas veces si hace falta.
function campo_vertices_cueva(_cueva)
{
    var _vancho = _cueva.ancho + 1;
    var _valto  = _cueva.alto + 1;
    var _campo  = array_create(_vancho * _valto, 0);

    for (var _vy = 0; _vy < _valto; _vy++)
        for (var _vx = 0; _vx < _vancho; _vx++)
            _campo[_vy * _vancho + _vx] = valor_vertice_cueva(_cueva, _vx, _vy);

    return { ancho: _vancho, alto: _valto, valores: _campo };
}

/// @func borde_interpolado(_a, _b, _umbral)
/// @desc Fracción [0, 1] a lo largo de un borde donde el campo cruza el
///       umbral, por interpolación lineal entre sus dos esquinas. Es esto lo
///       que evita que el cruce caiga siempre en el punto medio.
function borde_interpolado(_a, _b, _umbral)
{
    if (abs(_a - _b) < 0.00001) return 0.5;
    return clamp((_umbral - _a) / (_b - _a), 0, 1);
}

/// @func marching_squares_lista(_campo, _tam_celda, _umbral)
/// @desc Recorre el campo de vértices (`campo_vertices_cueva` u otro campo
///       escalar del mismo formato) y devuelve la lista de segmentos del
///       contorno, en coordenadas de PÍXEL.
/// @return {Array<Struct>} [{ x1, y1, x2, y2 }, ...]
function marching_squares_lista(_campo, _tam_celda, _umbral)
{
    var _ancho = _campo.ancho;   // vértices: hay una celda menos en cada eje
    var _alto  = _campo.alto;
    var _v     = _campo.valores;
    var _segmentos = [];

    for (var _fy = 0; _fy < _alto - 1; _fy++)
    {
        for (var _fx = 0; _fx < _ancho - 1; _fx++)
        {
            var _si = _v[_fy       * _ancho + _fx];       // superior-izquierda
            var _sd = _v[_fy       * _ancho + _fx + 1];   // superior-derecha
            var _id = _v[(_fy + 1) * _ancho + _fx + 1];   // inferior-derecha
            var _ii = _v[(_fy + 1) * _ancho + _fx];       // inferior-izquierda

            var _caso = (_si >= _umbral ? 1 : 0) | (_sd >= _umbral ? 2 : 0)
                      | (_id >= _umbral ? 4 : 0) | (_ii >= _umbral ? 8 : 0);

            if (_caso == 0 || _caso == 15) continue;   // celda toda fuera o toda dentro

            var _px = _fx * _tam_celda;
            var _py = _fy * _tam_celda;

            var _n_x = _px + borde_interpolado(_si, _sd, _umbral) * _tam_celda;
            var _n_y = _py;
            var _s_x = _px + borde_interpolado(_ii, _id, _umbral) * _tam_celda;
            var _s_y = _py + _tam_celda;
            var _o_x = _px;
            var _o_y = _py + borde_interpolado(_si, _ii, _umbral) * _tam_celda;
            var _e_x = _px + _tam_celda;
            var _e_y = _py + borde_interpolado(_sd, _id, _umbral) * _tam_celda;

            switch (_caso)
            {
                case 1:  array_push(_segmentos, { x1: _o_x, y1: _o_y, x2: _n_x, y2: _n_y }); break;
                case 2:  array_push(_segmentos, { x1: _n_x, y1: _n_y, x2: _e_x, y2: _e_y }); break;
                case 3:  array_push(_segmentos, { x1: _o_x, y1: _o_y, x2: _e_x, y2: _e_y }); break;
                case 4:  array_push(_segmentos, { x1: _e_x, y1: _e_y, x2: _s_x, y2: _s_y }); break;
                case 6:  array_push(_segmentos, { x1: _n_x, y1: _n_y, x2: _s_x, y2: _s_y }); break;
                case 7:  array_push(_segmentos, { x1: _o_x, y1: _o_y, x2: _s_x, y2: _s_y }); break;
                case 8:  array_push(_segmentos, { x1: _s_x, y1: _s_y, x2: _o_x, y2: _o_y }); break;
                case 9:  array_push(_segmentos, { x1: _n_x, y1: _n_y, x2: _s_x, y2: _s_y }); break;
                case 11: array_push(_segmentos, { x1: _e_x, y1: _e_y, x2: _s_x, y2: _s_y }); break;
                case 12: array_push(_segmentos, { x1: _o_x, y1: _o_y, x2: _e_x, y2: _e_y }); break;
                case 13: array_push(_segmentos, { x1: _n_x, y1: _n_y, x2: _e_x, y2: _e_y }); break;
                case 14: array_push(_segmentos, { x1: _o_x, y1: _o_y, x2: _n_x, y2: _n_y }); break;

                case 5:   // silla SI+ID: el promedio de las 4 esquinas desempata
                    var _centro5 = (_si + _sd + _id + _ii) / 4;
                    if (_centro5 < _umbral)
                    {
                        array_push(_segmentos, { x1: _o_x, y1: _o_y, x2: _n_x, y2: _n_y });
                        array_push(_segmentos, { x1: _e_x, y1: _e_y, x2: _s_x, y2: _s_y });
                    }
                    else
                    {
                        array_push(_segmentos, { x1: _n_x, y1: _n_y, x2: _e_x, y2: _e_y });
                        array_push(_segmentos, { x1: _s_x, y1: _s_y, x2: _o_x, y2: _o_y });
                    }
                    break;

                case 10:   // silla SD+II: mismo criterio, complementario
                    var _centro10 = (_si + _sd + _id + _ii) / 4;
                    if (_centro10 < _umbral)
                    {
                        array_push(_segmentos, { x1: _n_x, y1: _n_y, x2: _e_x, y2: _e_y });
                        array_push(_segmentos, { x1: _s_x, y1: _s_y, x2: _o_x, y2: _o_y });
                    }
                    else
                    {
                        array_push(_segmentos, { x1: _o_x, y1: _o_y, x2: _n_x, y2: _n_y });
                        array_push(_segmentos, { x1: _e_x, y1: _e_y, x2: _s_x, y2: _s_y });
                    }
                    break;
            }
        }
    }

    return _segmentos;
}

/// @func dibujar_contorno(_segmentos, _color)
/// @desc Dibuja la lista de segmentos como polilínea. La lista se calcula UNA
///       vez fuera de Draw (§2.9); dibujarla cada frame es barato.
function dibujar_contorno(_segmentos, _color)
{
    draw_set_color(_color);
    draw_primitive_begin(pr_linelist);

    for (var _i = 0; _i < array_length(_segmentos); _i++)
    {
        var _s = _segmentos[_i];
        draw_vertex(_s.x1, _s.y1);
        draw_vertex(_s.x2, _s.y2);
    }

    draw_primitive_end();
}
```

**Uso**, sobre una cueva ya generada y podada:

```gml
// objMundo — Create, tras cueva_celular() + conservar_region_mayor() + podar_callejones()
var _campo = campo_vertices_cueva(cueva);
contorno = marching_squares_lista(_campo, TAM_CELDA, 0.5);

// objMundo — Draw
dibujar_contorno(contorno, c_white);
```

> 🔎 **Sobre el propio tilemap, o encima.** El tilemap sigue siendo lo más barato para el relleno
> (§2.8): marching squares no lo sustituye, se **superpone** como un contorno vectorial —el borde
> de la roca, una veta de mineral, la silueta que separa cueva de fondo. Para terreno
> **destructible** (§9), recalcula el contorno solo tras `excavar()`, nunca en Draw ni en cada
> Step; si el mapa es grande, repártelo con el patrón de §14.
>
> 🔗 **La misma técnica sirve para los *metaballs* de
> [13 · 08 §12](./08%20-%20Físicas%20a%20mano%20y%20fluidos.md#12--metaballs-agua-y-limo-estilizados).**
> Aquella sección funde gotas con `gpu_set_alphatestref` (recorte de alfa, borde con escalones a
> propósito, aspecto de dibujo animado). Si en vez de eso corres `marching_squares_lista()` sobre
> el campo de alfa acumulado de las gotas —sustituyendo `valor_vertice_cueva` por un muestreo del
> alfa en cada vértice— el borde sale suave y vectorial, más caro de calcular pero sin dentado.
> No dupliques el dibujo de las gotas: la función `blobs_dibujar()` de aquella sección sigue
> siendo quien las acumula.

---

## 3 quater · Otras familias: difusión limitada por agregación y multi-agente

Autómatas celulares (§3) aplican **una regla local por igual a todo el mapa**. Estas dos familias
cambian el enfoque: en vez de una regla sobre una rejilla completa, **un agente que se mueve y
decide** va escribiendo el mapa a su paso. Son nicho frente al resto del documento, pero cubren
dos texturas que ni el ruido ni el autómata dan: ramificación orgánica y composición por rasgos.

### Difusión limitada por agregación (DLA)

DLA simula un fenómeno físico real —partículas en movimiento browniano que se pegan al chocar con
un agregado ya formado— para generar estructuras **ramificadas**: vetas de mineral, rayos, raíces,
y cuevas con muchos túneles estrechos y pocos bucles. RogueBasin lo resume en una frase: crea una
semilla, suelta un caminante que se mueve al azar, y **"move the walker around until it collides
with a floor tile; then carve out another floor tile where that walker was"** — se excava la
posición del caminante, no la celda con la que chocó. Repetido miles de veces, el resultado es
siempre **una única región conectada** (cada celda nueva toca, por construcción, algo que ya
estaba conectado a la semilla): a diferencia del autómata celular de §3, **no hace falta**
`conservar_region_mayor()`.

```gml
// ---------------------------------------------------------------------------
// scr_dla
// Verificado: array_create, array_length (ya usados en este documento)
// ---------------------------------------------------------------------------

/// @func dla_cueva(_ancho, _alto, _semilla, _particulas, _pasos_max)
/// @desc Difusión limitada por agregación sobre rejilla (Witten y Sander,
///       1981; la adaptación a mazmorras es de RogueBasin). Cada caminante
///       nace en un punto al azar del mapa y avanza en las 4 direcciones
///       hasta TOCAR una celda de suelo; entonces se excava SU posición y se
///       descarta. Si agota `_pasos_max` sin tocar nada, se descarta sin
///       excavar nada (ver la nota de rendimiento más abajo).
/// @param {Real} _particulas  Cuantas más, más densa y menos ramificada sale
/// @param {Real} _pasos_max   Tope de pasos por caminante
/// @return {Struct} { ancho, alto, celdas, semilla, adheridas }
function dla_cueva(_ancho, _alto, _semilla, _particulas, _pasos_max)
{
    var _rng    = new RNG(_semilla);
    var _celdas = array_create(_ancho * _alto, 1);   // todo muro

    var _cx0 = _ancho div 2;
    var _cy0 = _alto div 2;
    _celdas[_cy0 * _ancho + _cx0] = 0;   // la semilla: un único punto de suelo

    var _dx = [1, -1, 0, 0];
    var _dy = [0, 0, 1, -1];
    var _adheridas = 0;

    for (var _p = 0; _p < _particulas; _p++)
    {
        var _wx = _rng.range(1, _ancho - 2);
        var _wy = _rng.range(1, _alto - 2);

        repeat (_pasos_max)
        {
            var _toca = false;
            for (var _d = 0; _d < 4; _d++)
            {
                var _vx = _wx + _dx[_d];
                var _vy = _wy + _dy[_d];
                if (_vx < 0 || _vy < 0 || _vx >= _ancho || _vy >= _alto) continue;
                if (_celdas[_vy * _ancho + _vx] == 0) { _toca = true; break; }
            }

            if (_toca)
            {
                _celdas[_wy * _ancho + _wx] = 0;
                _adheridas++;
                break;
            }

            var _d2 = _rng.int(3);
            _wx = clamp(_wx + _dx[_d2], 1, _ancho - 2);
            _wy = clamp(_wy + _dy[_d2], 1, _alto - 2);
        }
    }

    return { ancho: _ancho, alto: _alto, celdas: _celdas, semilla: _semilla, adheridas: _adheridas };
}
```

> ⚡ **Rendimiento.** Con la semilla en el centro y caminantes naciendo en cualquier punto del
> mapa, la mayoría de los pasos se gastan vagando por celdas vacías antes de acercarse siquiera al
> agregado — es la trampa clásica de DLA. Dos salidas, sin complicar el código de arriba: reduce
> el mapa, o compara `adheridas` contra `_particulas` pedidas (si son muy distintas, sube
> `_pasos_max`). Para mapas grandes, `dla_cueva()` es de manual el candidato ideal para repartir
> partícula a partícula entre varios `Step` con el patrón de §14.
>
> RogueBasin también señala el defecto del resultado: *"loops are quite infrequent... dead ends
> are common"* — si quieres más bucles, combina el resultado con `podar_callejones()` (§3 bis)
> **en sentido inverso** (no rellenar, sino cavar un túnel adicional entre dos ramas cercanas), o
> simplemente acéptalo: para una veta de mineral o una raíz, los callejones sin salida no son un
> defecto, son el aspecto correcto.

### Generación multi-agente

La idea, llevada a su extremo, es la de Doran y Parberry (*Controlled Procedural Terrain
Generation Using Software Agents*, 2010, resumida en el capítulo 4 de Shaker, Togelius y Nelson):
en vez de una única regla, se lanzan **varios tipos de agente especializados** —de costa, de
suavizado, de playa, de montaña, de río— que recorren el mapa y lo modifican cada uno a su manera,
compartiendo la misma rejilla. Cada agente tiene su propio **presupuesto de pasos** ("tokens" en
el paper) y su propio comportamiento; el mapa final es la suma de sus rasgos, no una regla
uniforme aplicada a todo. Adaptado a una mazmorra 2D en vez de un terreno 3D, la versión mínima es
un `Cavador`: un agente que camina y excava un pincel de un tamaño dado a su paso.

```gml
// ---------------------------------------------------------------------------
// scr_multiagente
// ---------------------------------------------------------------------------

/// @func Cavador(_px, _py, _pasos, _ancho_pincel)
/// @desc Un agente digger con presupuesto de pasos y pincel propios. Varios
///       cavadores con parámetros distintos, lanzados desde puntos distintos
///       y escribiendo en LA MISMA rejilla, son la generación multi-agente:
///       cada uno aporta un rasgo (una sala amplia, un pasillo largo y
///       estrecho) en vez de aplicar una única regla por igual a todo el mapa.
function Cavador(_px, _py, _pasos, _ancho_pincel) constructor
{
    px = _px;
    py = _py;
    pasos_restantes = _pasos;
    pincel = _ancho_pincel;

    /// @desc Un paso: excava el pincel centrado en (px, py) y se mueve.
    ///       `_rng` la pone quien orquesta: todos los cavadores comparten UN
    ///       único generador para que el mapa entero dependa de una semilla.
    /// @return {Bool} true si dio el paso, false si ya no le quedaban
    paso = function(_celdas, _ancho, _alto, _rng)
    {
        if (pasos_restantes <= 0) return false;

        var _radio = (pincel - 1) div 2;
        for (var _oy = -_radio; _oy <= _radio; _oy++)
            for (var _ox = -_radio; _ox <= _radio; _ox++)
            {
                var _cx = clamp(px + _ox, 1, _ancho - 2);
                var _cy = clamp(py + _oy, 1, _alto - 2);
                _celdas[_cy * _ancho + _cx] = 0;
            }

        var _dx = [1, -1, 0, 0];
        var _dy = [0, 0, 1, -1];
        var _d  = _rng.int(3);
        px = clamp(px + _dx[_d], 1, _ancho - 2);
        py = clamp(py + _dy[_d], 1, _alto - 2);

        pasos_restantes--;
        return true;
    };
}

/// @func cueva_multiagente(_ancho, _alto, _semilla, _cavadores_cfg)
/// @desc Varios Cavador() trabajando a la vez, TURNÁNDOSE un paso cada uno
///       (no uno entero de golpe) para que ninguno termine mucho antes que
///       el resto — el mismo motivo por el que §14 reparte el trabajo en
///       trozos pequeños en vez de de una tacada.
/// @param {Array<Struct>} _cavadores_cfg [{ px, py, pasos, pincel }, ...]
function cueva_multiagente(_ancho, _alto, _semilla, _cavadores_cfg)
{
    var _rng    = new RNG(_semilla);
    var _celdas = array_create(_ancho * _alto, 1);

    var _cavadores = [];
    for (var _i = 0; _i < array_length(_cavadores_cfg); _i++)
    {
        var _c = _cavadores_cfg[_i];
        array_push(_cavadores, new Cavador(_c.px, _c.py, _c.pasos, _c.pincel));
    }

    var _quedan = array_length(_cavadores);
    while (_quedan > 0)
    {
        _quedan = 0;
        for (var _i = 0; _i < array_length(_cavadores); _i++)
            if (_cavadores[_i].paso(_celdas, _ancho, _alto, _rng)) _quedan++;
    }

    return { ancho: _ancho, alto: _alto, celdas: _celdas, semilla: _semilla };
}
```

```gml
// Uso: cuatro agentes con roles distintos, la misma semilla de siempre.
var _cueva = cueva_multiagente(96, 64, global.semilla, [
    { px: 48, py: 32, pasos: 400, pincel: 5 },   // una sala grande en el centro
    { px: 10, py: 10, pasos: 250, pincel: 1 },   // un pasillo estrecho y largo
    { px: 85, py: 55, pasos: 250, pincel: 1 },
    { px: 20, py: 50, pasos: 150, pincel: 3 }
]);
conservar_region_mayor(_cueva);   // §3.1: aquí SÍ hace falta, a diferencia de DLA
```

> ⚠️ A diferencia de DLA, **los agentes no garantizan conectividad**: cada uno pasea por su
> cuenta y puede que dos cavadores nunca lleguen a tocarse. Siempre `conservar_region_mayor()` (o
> cavar un túnel de emergencia entre las regiones más grandes) después de correrlos.

| Técnica | Conectividad | Textura | Coste típico |
|---|---|---|---|
| Autómata celular (§3) | No garantizada — hace falta §3.1 | Cavernas redondeadas, uniformes | Bajo, `O(celdas · pasadas)` |
| DLA | Garantizada por construcción | Ramificada, muchos callejones | Medio-alto, depende de cuántos pasos se agotan |
| Multi-agente | No garantizada — hace falta §3.1 | Compuesta: cada agente aporta un rasgo distinto | Medio, controlable agente a agente |

---

## 3 quinquies · Laberintos perfectos: el backtracker recursivo

Un autómata celular da cuevas; un laberinto es lo contrario. Un **laberinto perfecto** es una
rejilla en la que existe **exactamente un camino** entre cualquier par de celdas: sin bucles y
sin zonas aisladas. En términos de grafos es un **árbol de expansión** sobre la rejilla, y esa
definición es la que conviene tener en la cabeza, porque explica de un golpe todas sus
propiedades: `celdas - 1` pasillos, ningún ciclo, siempre conexo, y la solución es única.

Sirve para mazmorras clásicas, para el interior de un edificio, para catacumbas y —sobre todo—
como **esqueleto** al que luego se le abren salas, se le añaden bucles y se le pega decoración.
Un laberinto crudo es aburrido; un laberinto crudo bien generado es un excelente punto de
partida.

### 3 quinquies .1 Representar el laberinto por paredes, no por baldosas

La tentación es trabajar directamente sobre una rejilla de baldosas donde una celda es «pared»
o «suelo». Funciona, pero complica todo: hay que razonar con celdas de índice par e impar y
cualquier despiste produce paredes de grosor inconsistente.

Es mucho más limpio guardar, **por celda, qué paredes siguen en pie** como una máscara de bits:

```gml
#macro LAB_NORTE 1
#macro LAB_ESTE  2
#macro LAB_SUR   4
#macro LAB_OESTE 8
```

Una celda arranca con `15` (las cuatro paredes) y abrir un pasillo es quitar un bit **a las dos
celdas implicadas**. La conversión a baldosas se hace al final, una sola vez, y ahí sí se usa el
truco clásico: un laberinto de `A × B` celdas se dibuja en una rejilla de `(2A+1) × (2B+1)`
baldosas, donde las celdas caen en las posiciones impares y las paredes en las pares.

### 3 quinquies .2 El algoritmo, con pila explícita

El *recursive backtracker* es una búsqueda en profundidad que va abriendo pasillos hacia celdas
no visitadas y retrocede cuando se queda sin salida. Se llama «recursivo» por cómo se explica,
no por cómo debe escribirse:

> ⚠️ **No lo escribas con recursión de verdad.** La profundidad de la pila llega a ser del orden
> de `ancho × alto` — miles de llamadas anidadas en un laberinto mediano. GameMaker no documenta
> un límite de recursión, y cuando se rebasa el runner se cierra sin un mensaje que sirva de
> nada. La versión iterativa es **el mismo algoritmo**, ocupa las mismas líneas y no plantea la
> pregunta. Es un array usado como pila, nada más.

```gml
/// @func generar_laberinto(_ancho, _alto, _semilla)
/// @desc Laberinto perfecto por backtracker recursivo (versión iterativa).
///       Todas las celdas quedan conectadas y no hay ningún bucle.
/// @param {Real} _ancho   Celdas de ancho (no baldosas)
/// @param {Real} _alto    Celdas de alto
/// @param {Real} _semilla
/// @return {Struct} { ancho, alto, paredes }  paredes[i] = máscara LAB_*
function generar_laberinto(_ancho, _alto, _semilla)
{
    var _rng     = new RNG(_semilla);
    var _n       = _ancho * _alto;
    var _paredes = array_create(_n, LAB_NORTE | LAB_ESTE | LAB_SUR | LAB_OESTE);
    var _visto   = array_create(_n, false);

    // Índice de dirección: 0 norte, 1 este, 2 sur, 3 oeste.
    var _dx  = [ 0,  1,  0, -1];
    var _dy  = [-1,  0,  1,  0];
    var _bit = [LAB_NORTE, LAB_ESTE, LAB_SUR, LAB_OESTE];
    // La pared que se quita en la celda vecina es siempre la opuesta.
    var _opu = [LAB_SUR, LAB_OESTE, LAB_NORTE, LAB_ESTE];

    var _inicio = _rng.int(_n - 1);
    _visto[_inicio] = true;

    var _pila = [_inicio];

    while (array_length(_pila) > 0)
    {
        var _c  = _pila[array_length(_pila) - 1];
        var _cx = _c mod _ancho;
        var _cy = _c div _ancho;

        // Vecinos sin visitar, en orden aleatorio.
        var _libres = [];
        for (var _d = 0; _d < 4; _d++)
        {
            var _nx = _cx + _dx[_d];
            var _ny = _cy + _dy[_d];
            if (_nx < 0 || _ny < 0 || _nx >= _ancho || _ny >= _alto) continue;
            if (_visto[_ny * _ancho + _nx]) continue;
            array_push(_libres, _d);
        }

        if (array_length(_libres) == 0)
        {
            // Callejón: retrocede. Esto es el «backtrack» del nombre.
            array_delete(_pila, array_length(_pila) - 1, 1);
            continue;
        }

        var _d  = _rng.pick(_libres);
        var _ni = (_cy + _dy[_d]) * _ancho + (_cx + _dx[_d]);

        // Abrir el pasillo: hay que quitar el bit EN LAS DOS celdas.
        _paredes[_c]  = _paredes[_c]  & ~_bit[_d];
        _paredes[_ni] = _paredes[_ni] & ~_opu[_d];

        _visto[_ni] = true;
        array_push(_pila, _ni);
    }

    return { ancho: _ancho, alto: _alto, paredes: _paredes };
}
```

> ⚠️ **Quitar la pared en una sola de las dos celdas** es el fallo clásico de esta receta. El
> laberinto se recorre perfectamente si tu jugador consulta la celda de origen, y se convierte
> en un muro invisible si consulta la de destino. Es un bug que no rompe la generación, solo el
> movimiento — y por eso cuesta tanto encontrarlo. `_bit[_d]` y `_opu[_d]`, siempre los dos.

### 3 quinquies .3 Pasar de máscaras a baldosas

```gml
/// @func laberinto_a_rejilla(_lab)
/// @desc Expande el laberinto a una rejilla de (2A+1) x (2B+1):
///       1 = pared, 0 = suelo. Es la forma en que se pinta al tilemap (§2.8).
/// @return {Struct} { ancho, alto, celdas }
function laberinto_a_rejilla(_lab)
{
    var _rw = _lab.ancho * 2 + 1;
    var _rh = _lab.alto  * 2 + 1;
    var _r  = array_create(_rw * _rh, 1);

    for (var _cy = 0; _cy < _lab.alto; _cy++)
    {
        for (var _cx = 0; _cx < _lab.ancho; _cx++)
        {
            var _m  = _lab.paredes[_cy * _lab.ancho + _cx];
            var _rx = _cx * 2 + 1;
            var _ry = _cy * 2 + 1;

            _r[_ry * _rw + _rx] = 0;                                  // la celda
            if ((_m & LAB_NORTE) == 0) _r[(_ry - 1) * _rw + _rx] = 0; // pasillos
            if ((_m & LAB_ESTE)  == 0) _r[_ry * _rw + (_rx + 1)] = 0;
            if ((_m & LAB_SUR)   == 0) _r[(_ry + 1) * _rw + _rx] = 0;
            if ((_m & LAB_OESTE) == 0) _r[_ry * _rw + (_rx - 1)] = 0;
        }
    }

    return { ancho: _rw, alto: _rh, celdas: _r };
}
```

### 3 quinquies .4 Trenzado: quitarle los callejones

Un laberinto perfecto es, para jugar, **agotador**: cada callejón obliga a desandar el camino
entero. El remedio es el **trenzado** (*braiding*): abrir una pared más en cada callejón sin
salida, lo que introduce bucles y deja de ser perfecto — que es exactamente lo que quieres.

```gml
/// @func trenzar_laberinto(_lab, _semilla, _proporcion)
/// @desc Elimina callejones abriendo una pared extra. _proporcion 0 = ninguno,
///       1 = todos. Con 1 el laberinto deja de tener callejones por completo.
function trenzar_laberinto(_lab, _semilla, _proporcion)
{
    var _rng = new RNG(_semilla + 7919);
    var _dx  = [ 0,  1,  0, -1];
    var _dy  = [-1,  0,  1,  0];
    var _bit = [LAB_NORTE, LAB_ESTE, LAB_SUR, LAB_OESTE];
    var _opu = [LAB_SUR, LAB_OESTE, LAB_NORTE, LAB_ESTE];

    for (var _cy = 0; _cy < _lab.alto; _cy++)
    {
        for (var _cx = 0; _cx < _lab.ancho; _cx++)
        {
            var _i = _cy * _lab.ancho + _cx;

            // Un callejón tiene tres paredes en pie: exactamente un bit a 0.
            var _abiertas = 0;
            for (var _d = 0; _d < 4; _d++)
                if ((_lab.paredes[_i] & _bit[_d]) == 0) _abiertas++;

            if (_abiertas != 1) continue;
            if (!_rng.chance(_proporcion)) continue;

            // Candidatas: paredes en pie que dan a una celda dentro del mapa.
            var _cand = [];
            for (var _d = 0; _d < 4; _d++)
            {
                if ((_lab.paredes[_i] & _bit[_d]) == 0) continue;
                var _nx = _cx + _dx[_d];
                var _ny = _cy + _dy[_d];
                if (_nx < 0 || _ny < 0 || _nx >= _lab.ancho || _ny >= _lab.alto) continue;
                array_push(_cand, _d);
            }
            if (array_length(_cand) == 0) continue;

            var _d  = _rng.pick(_cand);
            var _ni = (_cy + _dy[_d]) * _lab.ancho + (_cx + _dx[_d]);
            _lab.paredes[_i]  = _lab.paredes[_i]  & ~_bit[_d];
            _lab.paredes[_ni] = _lab.paredes[_ni] & ~_opu[_d];
        }
    }

    return _lab;
}
```

Con `_proporcion` a 0,5 el laberinto conserva la sensación de laberinto y pierde la mitad de la
frustración. A 1 se convierte en una red de pasillos con bucles, muy adecuada para una mazmorra
de acción donde el jugador huye de enemigos.

> La **poda** de [§3 bis](#3-bis--poda-de-callejones-sin-salida) es la operación inversa y
> resuelve otro problema: allí se **rellenan** los callejones de una cueva porque sobran; aquí
> se **conectan** los de un laberinto porque estorban. No las confundas: podar un laberinto
> perfecto lo deja casi vacío, porque casi todo él es callejón.

### 3 quinquies .5 Qué algoritmo elegir, y por qué el sesgo importa

Todos estos algoritmos producen laberintos perfectos válidos. La diferencia es la **textura**:
qué se siente al recorrerlos. La terminología («*river*», el grado de serpenteo) es de Jamis
Buck, que sigue siendo la mejor referencia divulgativa sobre el tema.

| Algoritmo | Textura | Memoria | Cuándo |
|---|---|---|---|
| **Backtracker recursivo** | Pasillos largos y serpenteantes, pocos callejones pero muy profundos | Pila O(celdas) | Por defecto. Da sensación de estar perdido |
| **Prim aleatorio** | Muy ramificado, callejones cortos por todas partes | Frontera O(celdas) | Cuando quieres que se vea todo el mapa pronto |
| **Kruskal aleatorio** | Uniforme, sin sesgo perceptible | Conjuntos disjuntos | Cuando el laberinto debe parecer «neutro» |
| **Árbol binario** | Sesgo diagonal evidente: dos bordes son un pasillo recto | O(1) | Casi nunca. Sirve para explicar el sesgo |
| **Eller** | Como Kruskal, generado por filas | O(ancho) | Laberintos infinitos o gigantes por trozos |

**El sesgo no es un detalle académico.** El árbol binario deja siempre un pasillo recto completo
en dos de los cuatro bordes: un jugador que lo descubra una vez lo usará siempre y tu laberinto
deja de existir. El backtracker recursivo tiene su propio sesgo —recorridos largos, pocas
bifurcaciones cerca del inicio— pero es un sesgo que **juega a favor**: se siente como una
cueva explorada, no como una rejilla.

Si vas a insertar salas rectangulares dentro del laberinto, hazlo **antes** de generarlo:
marca esas celdas como ya visitadas y con sus paredes internas quitadas, y arranca el
backtracker desde el borde de una de ellas. El algoritmo tejerá los pasillos alrededor sin
tocar las salas, y todas quedarán conectadas por construcción — es la misma idea que el
ensamblaje por piezas de [§7](#7--ensamblaje-por-piezas), pero con el laberinto haciendo de
argamasa.

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

## 4 bis · Voronoi: regiones y formas orgánicas

Un diagrama de Voronoi reparte el plano en tantas regiones como semillas: cada punto pertenece a
la región de la semilla **más cercana**. Amit Patel lo resume bien en *Polygonal Map Generation
for Games* (2010, actualizado 2025): en vez de generar un mapa celda a celda, genera **unos
cientos de regiones** —cada una reconocible, con nombre, con vecinos bien definidos— en vez de
decenas de miles de celdas sueltas. Es la herramienta que faltaba para tres huecos del documento:
**biomas por territorio** (fronteras nítidas, no el degradado de un umbral de ruido, §2.7), **for-
mas de sala orgánicas** para una mazmorra, y **varios continentes** en el mismo mapa.

### Por fuerza bruta, no por el algoritmo de Fortune

El algoritmo de referencia (Fortune, `O(n log n)`, con una cola de eventos y un árbol de playa)
es complejo de implementar bien y no hace falta en GameMaker: para las rejillas de este documento
(unos cientos de celdas por lado, unas pocas decenas o centenas de semillas) basta **fuerza
bruta**: por cada celda de la rejilla, recorrer todas las semillas con `point_distance()` y
quedarse con la más cercana. Coste `O(celdas · semillas)` — con 200×200 celdas y 80 semillas son
3,2 millones de comparaciones, unos pocos milisegundos en la VM (mídelo con `get_timer()`, §2.9).
Si subes de escala, repártelo con el mismo patrón de generación por pasos de §14.

```gml
// ---------------------------------------------------------------------------
// scr_voronoi
// Verificado: point_distance, array_create, array_length (ya usados en el documento)
// Depende de muestreo_poisson() (§4) — NO se redefine aquí.
// ---------------------------------------------------------------------------

/// @func diagrama_voronoi(_ancho, _alto, _radio_semillas, _semilla)
/// @param {Real} _radio_semillas  Separación mínima entre semillas (Poisson-
///        disc, §4): sin esto, dos semillas casi pegadas producen una región
///        minúscula, casi un punto — el mismo motivo por el que §4 usa
///        Poisson-disc en vez de `irandom` a secas.
/// @return {Struct} { ancho, alto, semillas, regiones } — `regiones[i]` es el
///         ÍNDICE de la semilla más cercana a la celda `i`, no un color.
function diagrama_voronoi(_ancho, _alto, _radio_semillas, _semilla)
{
    var _semillas   = muestreo_poisson(_ancho, _alto, _radio_semillas, _semilla);
    var _n_semillas = array_length(_semillas);
    var _regiones   = array_create(_ancho * _alto, 0);

    for (var _fy = 0; _fy < _alto; _fy++)
    {
        for (var _fx = 0; _fx < _ancho; _fx++)
        {
            var _mejor      = 0;
            var _mejor_dist = infinity;

            for (var _s = 0; _s < _n_semillas; _s++)
            {
                var _d = point_distance(_fx, _fy, _semillas[_s].px, _semillas[_s].py);
                if (_d < _mejor_dist) { _mejor_dist = _d; _mejor = _s; }
            }

            _regiones[_fy * _ancho + _fx] = _mejor;
        }
    }

    return { ancho: _ancho, alto: _alto, semillas: _semillas, regiones: _regiones };
}
```

### Relajación de Lloyd: regiones más uniformes

Poisson-disc ya evita amontonamientos, pero las regiones resultantes siguen siendo desiguales en
forma. La relajación de Lloyd las regulariza: mueve cada semilla al **centroide** de su propia
región y recalcula el diagrama entero. Patel: *"running it twice gives good results"* — más
iteraciones dan regiones más uniformes pero más redondas y menos orgánicas; para formas de sala
1-2 pasadas bastan.

```gml
/// @func voronoi_relajar_lloyd(_diagrama, _iteraciones)
/// @desc Mueve cada semilla al centroide de su región y recalcula, tantas
///       veces como _iteraciones. Modifica _diagrama.semillas y
///       _diagrama.regiones en el sitio; también los devuelve.
function voronoi_relajar_lloyd(_diagrama, _iteraciones)
{
    var _ancho    = _diagrama.ancho;
    var _alto     = _diagrama.alto;
    var _semillas = _diagrama.semillas;
    var _n        = array_length(_semillas);

    repeat (_iteraciones)
    {
        var _suma_x = array_create(_n, 0);
        var _suma_y = array_create(_n, 0);
        var _cuenta = array_create(_n, 0);

        for (var _fy = 0; _fy < _alto; _fy++)
            for (var _fx = 0; _fx < _ancho; _fx++)
            {
                var _r = _diagrama.regiones[_fy * _ancho + _fx];
                _suma_x[_r] += _fx;
                _suma_y[_r] += _fy;
                _cuenta[_r]++;
            }

        for (var _s = 0; _s < _n; _s++)
        {
            if (_cuenta[_s] == 0) continue;   // región vaciada por el redondeo: se deja donde está
            _semillas[_s].px = _suma_x[_s] / _cuenta[_s];
            _semillas[_s].py = _suma_y[_s] / _cuenta[_s];
        }

        for (var _fy = 0; _fy < _alto; _fy++)
            for (var _fx = 0; _fx < _ancho; _fx++)
            {
                var _mejor      = 0;
                var _mejor_dist = infinity;
                for (var _s = 0; _s < _n; _s++)
                {
                    var _d = point_distance(_fx, _fy, _semillas[_s].px, _semillas[_s].py);
                    if (_d < _mejor_dist) { _mejor_dist = _d; _mejor = _s; }
                }
                _diagrama.regiones[_fy * _ancho + _fx] = _mejor;
            }
    }

    return _diagrama;
}
```

### Tres aplicaciones

**1 · Biomas por territorio.** Cada **semilla** (no cada celda) tira un bioma; la celda hereda el
de su región. Frente al umbral de ruido de §2.7, esto da fronteras **nítidas** entre territorios
— el aspecto de un mapa político o de provincias, no de un gradiente climático.

```gml
/// @func biomas_por_territorio(_diagrama, _semilla)
/// @desc Bioma: el enum de §2.7. Reutilízalo, no lo redefinas.
function biomas_por_territorio(_diagrama, _semilla)
{
    var _rng = new RNG(_semilla);
    var _n   = array_length(_diagrama.semillas);
    var _bioma_por_semilla = array_create(_n, Bioma.Hierba);

    for (var _s = 0; _s < _n; _s++)
        _bioma_por_semilla[_s] = _rng.pick([Bioma.Hierba, Bioma.Bosque, Bioma.Roca, Bioma.Nieve]);

    var _biomas = array_create(array_length(_diagrama.regiones), Bioma.Hierba);
    for (var _i = 0; _i < array_length(_diagrama.regiones); _i++)
        _biomas[_i] = _bioma_por_semilla[_diagrama.regiones[_i]];

    return _biomas;
}
```

**2 · Formas de sala orgánicas.** Deja como suelo el interior de cada región y como muro la franja
de frontera entre regiones vecinas — el resultado son salas de polígono irregular, en las antípo-
das de las rectangulares de BSP (`04 · 05 §5.2`).

```gml
/// @func voronoi_a_cueva(_diagrama, _grosor_muro)
/// @desc SUELO en el interior de cada región; MURO en la franja de
///       _grosor_muro celdas alrededor de cada frontera entre regiones.
function voronoi_a_cueva(_diagrama, _grosor_muro)
{
    var _ancho  = _diagrama.ancho;
    var _alto   = _diagrama.alto;
    var _celdas = array_create(_ancho * _alto, 1);

    for (var _fy = 0; _fy < _alto; _fy++)
        for (var _fx = 0; _fx < _ancho; _fx++)
        {
            var _r = _diagrama.regiones[_fy * _ancho + _fx];
            var _es_frontera = false;

            for (var _oy = -_grosor_muro; _oy <= _grosor_muro && !_es_frontera; _oy++)
                for (var _ox = -_grosor_muro; _ox <= _grosor_muro; _ox++)
                {
                    var _vx = clamp(_fx + _ox, 0, _ancho - 1);
                    var _vy = clamp(_fy + _oy, 0, _alto - 1);
                    if (_diagrama.regiones[_vy * _ancho + _vx] != _r) { _es_frontera = true; break; }
                }

            if (!_es_frontera) _celdas[_fy * _ancho + _fx] = 0;
        }

    return { ancho: _ancho, alto: _alto, celdas: _celdas };
}
```

Pasa el resultado por `marching_squares_lista()` (§3 ter) para redondear las esquinas de las
salas, o excava corredores entre regiones vecinas con el mismo patrón en L de `04 · 05 §5.2`.

**3 · Continentes múltiples.** En vez de un bioma, asigna a cada semilla "tierra" o "agua" según
una muestra de ruido de **baja frecuencia** (§2.5, 1-2 octavas) en la posición de la semilla. Cada
grupo de territorios de tierra separado de otro por territorios de agua es, de hecho, un
continente distinto: varias masas de tierra en el mismo mapa, no la isla única o el "continente
infinito" que son los dos únicos casos que cubre `_isla` en §2.7.

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

    /// @desc UN colapso + su propagación. Pensada para intercalar entre otros
    ///       muchos Step sin bloquear el frame (§14) en vez de resolver la
    ///       rejilla entera de golpe con `resolver()`. Antes de la primera
    ///       llamada, invoca `reiniciar(0)` una vez.
    /// @return {Bool} true si YA no queda nada que avanzar (resuelto o
    ///         contradicho); en ese caso comprueba `contradiccion` para saber
    ///         cuál de los dos pasó.
    resolver_un_paso = function()
    {
        if (contradiccion) return true;

        var _c = siguiente_celda();
        if (_c == -1) return true;   // todo colapsado: no queda trabajo

        colapsar(_c);
        propagar(_c);
        return contradiccion;
    };

    /// @desc Vuelca la onda YA resuelta (sin contradicción) a un array plano
    ///       de índices de tile. Solo tiene sentido tras `resolver_un_paso()`
    ///       haber devuelto true con `contradiccion == false`.
    volcar_a_indices = function()
    {
        var _salida = array_create(ancho * alto, 0);
        for (var _k = 0; _k < ancho * alto; _k++)
            for (var _t = 0; _t < n_tiles; _t++)
                if (onda[_k][_t]) { _salida[_k] = tiles[_t].indice; break; }
        return _salida;
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

## 5 bis · Autotiling clásico: bitmask de vecinos → índice de tile

WFC (§5) resuelve el caso general —cualquier número de terrenos, reglas de adyacencia
arbitrarias— a costa de propagación y de un «Plan B» obligatorio si falla. Para el caso más
frecuente con diferencia —**dos terrenos que se tocan** (hierba/tierra, suelo/vacío)— hay una
técnica mucho más barata y **100 % determinista**: el autotiling clásico por *bitmask* de
vecinos, la misma idea que usa el editor de tile sets de GameMaker
([13 · 02 §3.3](./02%20-%20Diseño%20de%20niveles.md#33-tiles-tile-set-autotiles-y-pinceles))
pero **calculada a mano**, porque —ya lo dice ese mismo apartado— **los autotiles del editor
no son accesibles desde código**: si generas el nivel proceduralmente, el cálculo de bordes lo
haces tú.

La idea es siempre la misma: por cada celda del terreno, mira qué vecinos son **del mismo
terreno** y **cuáles no**; codifica esa información en un número (el *bitmask*); usa ese
número para elegir qué pieza del tile set dibujar ahí. Dos variantes, según cuántos vecinos
miras:

| Esquema | Vecinos que mira | Piezas necesarias | Cuándo |
|---|---|---|---|
| **16 baldosas** («edge autotiling») | Los 4 ortogonales (N, E, S, O) | 16 | Casi siempre: transiciones simples entre dos terrenos |
| **47 baldosas** («blob autotiling») | Los 8 vecinos (+ diagonales NE, SE, SO, NO) | 47 | Solo si necesitas distinguir una esquina interior de una exterior — ver §3.3 |

### El bitmask de 4 vecinos (16 baldosas)

Convención estándar: cada lado con el mismo terreno suma una potencia de 2 —
**N = 1, E = 2, S = 4, O = 8**—, así que el resultado es un número de **0 a 15** que codifica
exactamente los 16 casos posibles (aislada, cuatro remates de un solo lado, cuatro esquinas,
cuatro bordes rectos de dos lados opuestos... hasta la pieza rodeada por los cuatro lados).

```gml
/// @func vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy, _dx, _dy, _terreno)
/// @desc  true si la celda vecina existe (dentro de la grid) y es del mismo terreno.
///        Fuera del mapa se trata como "distinto terreno" — el borde del nivel siempre
///        se dibuja como límite, nunca como si continuara fuera.
function vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy, _dx, _dy, _terreno)
{
    var _nx = _cx + _dx, _ny = _cy + _dy;
    if (_nx < 0 || _nx >= _ancho || _ny < 0 || _ny >= _alto) return false;
    return _grid[_ny * _ancho + _nx] == _terreno;
}

/// @func bitmask_4_vecinos(_grid, _ancho, _alto, _cx, _cy, _terreno)
/// @desc  Bitmask de 4 bits (N=1, E=2, S=4, O=8) para autotiling de 16 piezas. Devuelve 0-15.
function bitmask_4_vecinos(_grid, _ancho, _alto, _cx, _cy, _terreno)
{
    var _n = vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy,  0, -1, _terreno);
    var _e = vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy,  1,  0, _terreno);
    var _s = vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy,  0,  1, _terreno);
    var _o = vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy, -1,  0, _terreno);

    return (_n * 1) + (_e * 2) + (_s * 4) + (_o * 8);
}
```

**El truco que evita cualquier tabla de traducción**: numera tus 16 baldosas en el tile set
**en ese mismo orden** —índice 0 = pieza aislada (sin ningún vecino), índice 15 = pieza
rodeada por los cuatro lados, y los 14 casos intermedios siguiendo la misma suma de bits—, y
el *bitmask* pasa a ser directamente el índice de tile. Sin tabla, sin `switch`:

```gml
/// obj_generador · pintar terreno con autotiling de 16 piezas, sin tabla de traducción
var _tm = layer_tilemap_get_id(layer_get_id("Tiles_Terreno"));

for (var _cy = 0; _cy < alto; _cy++)
{
    for (var _cx = 0; _cx < ancho; _cx++)
    {
        if (grid[_cy * ancho + _cx] != TERRENO_SUELO) continue;

        var _mascara = bitmask_4_vecinos(grid, ancho, alto, _cx, _cy, TERRENO_SUELO);
        tilemap_set(_tm, tile_set_index(0, _mascara), _cx, _cy);
    }
}
```

### El bitmask de 8 vecinos (47 baldosas)

Con 8 vecinos habría, en teoría, 256 combinaciones — pero la mayoría son geométricamente
imposibles de dibujar como una única pieza de borde: una esquina en diagonal (por ejemplo,
NE) solo tiene sentido visual si **sus dos lados ortogonales también son del mismo
terreno** (N **y** E). Si N está pero E no, esa «esquina» no se puede dibujar como transición
limpia. Aplicando esa regla a las 256 combinaciones crudas quedan exactamente **47**
distintas — el origen del nombre.

```gml
/// @func bitmask_8_vecinos_blob(_grid, _ancho, _alto, _cx, _cy, _terreno)
/// @desc  Bitmask de 8 bits con la regla de validez de esquina del "blob tileset": una
///        diagonal solo cuenta si sus dos lados ortogonales también son del mismo terreno.
function bitmask_8_vecinos_blob(_grid, _ancho, _alto, _cx, _cy, _terreno)
{
    var _n  = vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy,  0, -1, _terreno);
    var _e  = vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy,  1,  0, _terreno);
    var _s  = vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy,  0,  1, _terreno);
    var _o  = vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy, -1,  0, _terreno);
    var _ne = _n && _e && vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy,  1, -1, _terreno);
    var _se = _s && _e && vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy,  1,  1, _terreno);
    var _so = _s && _o && vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy, -1,  1, _terreno);
    var _no = _n && _o && vecino_mismo_terreno(_grid, _ancho, _alto, _cx, _cy, -1, -1, _terreno);

    return (_n*1) + (_e*2) + (_s*4) + (_o*8) + (_ne*16) + (_se*32) + (_so*64) + (_no*128);
}
```

A diferencia del caso de 16, aquí **sí hace falta una tabla**: el resultado de la función de
arriba es uno de 47 valores válidos, pero repartidos sin orden dentro del rango 0-255 —no hay
forma de que el número sea directamente el índice. En vez de escribir esa tabla a mano (y
arriesgarte a transcribirla mal), constrúyela **una vez, por enumeración**, que es
autoverificable: recorre los 16 casos ortogonales y, para cada uno, todas las combinaciones
de las esquinas que sí son geométricamente posibles en ese caso.

```gml
/// @func construir_tabla_blob_47()
/// @desc  Genera, una sola vez, la tabla que traduce cada máscara cruda válida (0-255) a un
///        índice compacto 0-46. El orden es determinista pero es UNA convención entre varias
///        posibles: coloca tus 47 baldosas del tile set en ese mismo orden, o vuelca la tabla
///        con show_debug_message() y adapta tu tile set a lo que veas.
/// @return {Id.DsMap} máscara cruda (0-255) → índice compacto (0-46)
function construir_tabla_blob_47()
{
    var _tabla = ds_map_create();
    var _siguiente = 0;

    for (var _orto = 0; _orto < 16; _orto++)
    {
        var _n = (_orto & 1) != 0, _e = (_orto & 2) != 0;
        var _s = (_orto & 4) != 0, _o = (_orto & 8) != 0;

        // Qué esquinas son geométricamente posibles con este juego de lados.
        var _puede_ne = _n && _e, _puede_se = _s && _e;
        var _puede_so = _s && _o, _puede_no = _n && _o;
        var _num_esquinas = _puede_ne + _puede_se + _puede_so + _puede_no;

        for (var _c = 0; _c < power(2, _num_esquinas); _c++)
        {
            // Reparte los bits de _c entre las esquinas posibles, en orden NE, SE, SO, NO.
            var _bit = 0, _ne = 0, _se = 0, _so = 0, _no = 0;
            if (_puede_ne) { _ne = (_c >> _bit) & 1; _bit++; }
            if (_puede_se) { _se = (_c >> _bit) & 1; _bit++; }
            if (_puede_so) { _so = (_c >> _bit) & 1; _bit++; }
            if (_puede_no) { _no = (_c >> _bit) & 1; _bit++; }

            var _mascara = _orto + (_ne*16) + (_se*32) + (_so*64) + (_no*128);
            _tabla[? _mascara] = _siguiente;
            _siguiente++;
        }
    }

    show_debug_message($"tabla blob: {_siguiente} piezas generadas (debe ser 47)");
    return _tabla;
}
```

```gml
/// obj_generador · Create — construir la tabla una sola vez
tabla_blob = construir_tabla_blob_47();
```

```gml
/// obj_generador · pintar terreno con autotiling de 47 piezas
var _mascara = bitmask_8_vecinos_blob(grid, ancho, alto, _cx, _cy, TERRENO_SUELO);
var _indice  = tabla_blob[? _mascara];
tilemap_set(_tm, tile_set_index(0, _indice), _cx, _cy);
```

> ⚠️ Ni GameMaker ni ninguna fuente oficial documentan una **numeración estándar universal**
> para las 47 piezas: cada tile set las dibuja en el orden que le resulta cómodo a su autor.
> Lo único garantizado —y lo que sí hace este algoritmo— es que hay **exactamente 47** casos
> válidos y que la asignación es **determinista y estable** entre ejecuciones: genera la tabla
> una vez, vuélcala con `show_debug_message()` para ver el orden, y dibuja tu tile set (o
> reordénalo) para que coincida.

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

### 7.4 Roles de sala: quién es el jefe y dónde va el tesoro

Ensamblar el nivel deja un montón de salas iguales. Lo que convierte ese montón en una mazmorra
es **repartir papeles**: entrada, jefe, tesoro, tienda, atajo. Y ese reparto tiene una única
regla que hay que respetar por encima de todo:

> ⚠️ **La distancia que importa es la del grafo, no la de la pantalla.** Elegir «la sala más
> lejana» midiendo píxeles entre centros es el error clásico: en un nivel con forma de herradura,
> la sala del jefe acaba a dos pasillos de la entrada aunque en el mapa esté en la otra punta. La
> distancia buena es **cuántas salas hay que atravesar**, y eso se calcula con un recorrido en
> anchura sobre las celdas transitables.

### 7.4.1 Etiquetar cada celda con su sala

`ensamblar_nivel` (§7.3) devuelve `colocadas`, la lista de piezas con su posición. Lo primero es
poder preguntar, dada una celda, a qué sala pertenece:

```gml
/// @func mapa_de_salas(_mapa)
/// @desc Estampa el índice de sala sobre cada celda de su huella.
///       -1 en las celdas que no pertenecen a ninguna pieza.
/// @return {Array<Real>} idsala[i]
function mapa_de_salas(_mapa)
{
    var _id = array_create(_mapa.ancho * _mapa.alto, -1);

    for (var _s = 0; _s < array_length(_mapa.colocadas); _s++)
    {
        var _c = _mapa.colocadas[_s];
        for (var _fy = 0; _fy < _c.pieza.alto; _fy++)
        {
            for (var _fx = 0; _fx < _c.pieza.ancho; _fx++)
            {
                var _x = _c.px + _fx;
                var _y = _c.py + _fy;
                if (_x < 0 || _y < 0 || _x >= _mapa.ancho || _y >= _mapa.alto) continue;
                _id[_y * _mapa.ancho + _x] = _s;
            }
        }
    }

    return _id;
}
```

### 7.4.2 Distancia real desde la entrada

```gml
/// @func distancias_desde(_mapa, _ix, _iy)
/// @desc Recorrido en anchura sobre celdas transitables (celdas == 0).
///       Devuelve la distancia en celdas; -1 en lo inalcanzable.
/// @return {Array<Real>}
function distancias_desde(_mapa, _ix, _iy)
{
    var _n    = _mapa.ancho * _mapa.alto;
    var _dist = array_create(_n, -1);
    var _cola = ds_queue_create();

    var _ini = _iy * _mapa.ancho + _ix;
    _dist[_ini] = 0;
    ds_queue_enqueue(_cola, _ini);

    var _dx = [1, 0, -1, 0];
    var _dy = [0, 1, 0, -1];

    while (!ds_queue_empty(_cola))
    {
        var _c  = ds_queue_dequeue(_cola);
        var _cx = _c mod _mapa.ancho;
        var _cy = _c div _mapa.ancho;

        for (var _k = 0; _k < 4; _k++)
        {
            var _nx = _cx + _dx[_k];
            var _ny = _cy + _dy[_k];
            if (_nx < 0 || _ny < 0 || _nx >= _mapa.ancho || _ny >= _mapa.alto) continue;

            var _ni = _ny * _mapa.ancho + _nx;
            if (_dist[_ni] != -1) continue;          // ya visitada
            if (_mapa.celdas[_ni] != 0) continue;    // pared

            _dist[_ni] = _dist[_c] + 1;
            ds_queue_enqueue(_cola, _ni);
        }
    }

    ds_queue_destroy(_cola);
    return _dist;
}
```

> ⚠️ **La cola en anchura da la distancia mínima solo si marcas al encolar, no al desencolar.**
> Si compruebas `_dist[_ni] != -1` en el momento de sacar de la cola, la misma celda entra varias
> veces y el recorrido degenera. El `_dist[_ni] = ...` de arriba está **antes** del
> `ds_queue_enqueue` a propósito.

### 7.4.3 El reparto

```gml
/// @func asignar_roles(_mapa, _ix, _iy)
/// @desc Reparte papeles usando distancia de grafo y grado de conexión.
/// @return {Struct} { entrada, jefe, tienda, tesoros, distancias_sala }
function asignar_roles(_mapa, _ix, _iy)
{
    var _idsala = mapa_de_salas(_mapa);
    var _dist   = distancias_desde(_mapa, _ix, _iy);
    var _nsalas = array_length(_mapa.colocadas);

    // Distancia de cada sala = la de su celda más cercana a la entrada.
    var _dsala  = array_create(_nsalas, -1);
    // Grado = a cuántas salas distintas toca. Una hoja tiene grado 1.
    var _vecinas = array_create(_nsalas, undefined);
    for (var _s = 0; _s < _nsalas; _s++) _vecinas[_s] = {};

    var _dx = [1, 0, -1, 0];
    var _dy = [0, 1, 0, -1];

    for (var _y = 0; _y < _mapa.alto; _y++)
    {
        for (var _x = 0; _x < _mapa.ancho; _x++)
        {
            var _i = _y * _mapa.ancho + _x;
            var _s = _idsala[_i];
            if (_s < 0 || _dist[_i] < 0) continue;

            if (_dsala[_s] < 0 || _dist[_i] < _dsala[_s]) _dsala[_s] = _dist[_i];

            for (var _k = 0; _k < 4; _k++)
            {
                var _nx = _x + _dx[_k];
                var _ny = _y + _dy[_k];
                if (_nx < 0 || _ny < 0 || _nx >= _mapa.ancho || _ny >= _mapa.alto) continue;

                var _o = _idsala[_ny * _mapa.ancho + _nx];
                if (_o >= 0 && _o != _s) variable_struct_set(_vecinas[_s], string(_o), true);
            }
        }
    }

    // Entrada: la sala que contiene el punto de partida.
    var _entrada = _idsala[_iy * _mapa.ancho + _ix];

    // Jefe: la sala alcanzable más lejana EN EL GRAFO.
    var _jefe = _entrada;
    for (var _s = 0; _s < _nsalas; _s++)
        if (_dsala[_s] > _dsala[_jefe]) _jefe = _s;

    // Tesoros: hojas (grado 1) que no son ni la entrada ni el jefe.
    // Una hoja es un desvío: el jugador que la encuentra ha elegido explorar.
    var _tesoros = [];
    for (var _s = 0; _s < _nsalas; _s++)
    {
        if (_s == _entrada || _s == _jefe) continue;
        if (array_length(variable_struct_get_names(_vecinas[_s])) == 1)
            array_push(_tesoros, _s);
    }

    // Tienda: en el camino principal, a un 60 % del recorrido. Ni al empezar
    // (no hay dinero) ni pegada al jefe (no da tiempo a usar lo comprado).
    var _objetivo = _dsala[_jefe] * 0.6;
    var _tienda   = -1;
    var _mejor    = infinity;
    for (var _s = 0; _s < _nsalas; _s++)
    {
        if (_s == _entrada || _s == _jefe) continue;
        if (array_length(variable_struct_get_names(_vecinas[_s])) < 2) continue;  // no hoja
        var _e = abs(_dsala[_s] - _objetivo);
        if (_e < _mejor) { _mejor = _e; _tienda = _s; }
    }

    return {
        entrada: _entrada,
        jefe: _jefe,
        tienda: _tienda,
        tesoros: _tesoros,
        distancias_sala: _dsala
    };
}
```

### 7.4.4 Las tres trampas del reparto

**Una llave nunca detrás de su propia puerta.** En cuanto cierras una sala con una llave, todo el
reparto se vuelve un problema de orden. La regla mínima: la llave se coloca en una sala cuya
distancia sea **estrictamente menor** que la de la puerta que abre, midiendo sobre el grafo *con
la puerta cerrada*. Si generas varias llaves, calcula las distancias de nuevo tras colocar cada
puerta; reutilizar el `_dist` inicial es exactamente cómo se producen las mazmorras imposibles.

**Un `-1` no es una distancia grande, es una sala inalcanzable.** El código de arriba las excluye
porque compara con `_dsala[_jefe]` partiendo de la entrada, pero si ordenas salas por distancia
en otro sitio, un `-1` se cuela como la más cercana. Una sala inalcanzable es siempre un bug del
ensamblaje: detéctalo y **rechaza el nivel** (§1.2), no lo parchees repartiendo papeles en una
zona a la que nadie puede llegar.

**El jefe más lejano puede ser una sala minúscula.** El algoritmo elige por distancia, no por
tamaño, y una arena de jefe de 5×5 celdas no funciona. Filtra: entre las salas del último cuartil
de distancia, quédate con la más grande. Es una línea más y evita el clásico jefe encajonado:

```gml
// Jefe: la sala más GRANDE dentro del cuartil más lejano.
var _corte = _dsala[_jefe] * 0.75;
var _mejor_area = -1;
for (var _s = 0; _s < _nsalas; _s++)
{
    if (_dsala[_s] < _corte) continue;
    var _p = _mapa.colocadas[_s].pieza;
    var _area = _p.ancho * _p.alto;
    if (_area > _mejor_area) { _mejor_area = _area; _jefe = _s; }
}
```

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
| WFC sobre una rejilla grande | Segundos de congelación al generar | Reducir tiles, autotiling, o repartir la resolución en pasos (§14) |
| Generación completa en un solo Step | El juego se congela un instante al generar, o al cargar una room | Reescribir el generador como retomable y repartirlo con un presupuesto de ms por frame (§14) |
| Poisson con anillo `r·(1+u)` | Puntos amontonados a distancia casi exacta `r` | `r·sqrt(1 + 3u)`: uniforme por área (Bridson) |
| Gramática recursiva sin tope | Cuelgue o desbordamiento de pila | Parámetro `_profundidad` que decrece siempre |
| L-system con demasiadas iteraciones | Cadenas de millones de caracteres | Tope de longitud además del de iteraciones |
| `room_instance_add` sobre una room del proyecto | Instancias duplicadas que sobreviven a `game_restart()` | `room_add()` + `room_assign()`, o piezas como datos |
| Arrays 2D anidados en mapas grandes | El generador tarda el triple sin motivo aparente | Array plano `celdas[fy * ancho + fx]` |
| Guardar el mapa entero en el save | Saves enormes que rompen al cambiar de versión | Semilla + diff; y valida la cabecera al cargar |
| Sin métricas | «A veces sale mal» y nadie sabe cuándo | `medir_nivel` + umbrales escritos + volcado a PNG |
| Campo binario sin suavizar en marching squares | El contorno pasa siempre por el punto medio de cada borde: mejor que un tile, pero no es curvo | `valor_vertice_cueva()` (§3 ter): un valor continuo por vértice, no el array 0/1 directo |
| DLA con caminantes naciendo lejos del agregado | Miles de pasos gastados en celdas vacías; `adheridas` muy por debajo de `_particulas` | Mapa más pequeño, más `_pasos_max`, o repartir partícula a partícula con §14 |

---

## 14 · Generar sin congelar el frame

Todo el código de este documento asume, hasta aquí, que la generación entera cabe en una sola
llamada: un `Step`, un `Create`. Con mapas pequeños (los de los ejemplos) eso no se nota. Con un
autómata celular sobre 500×500 celdas, un WFC de 40 tiles sobre 100×100, o unos cuantos miles de
partículas de DLA (§3 quater), la generación se va a decenas o cientos de milisegundos — y a 60
fps, un solo frame son 16,6 ms. El síntoma no es solo un frame perdido: es un tirón visible, o la
room que tarda en aparecer con la pantalla congelada.

**La solución no es hacerlo más rápido: es partirlo.** Ejecutar una fracción del trabajo por
frame, con un presupuesto de milisegundos, y ceder el resto al siguiente. Para eso el generador
tiene que dejar de ser una función que hace todo de una vez y pasar a ser un **objeto que recuerda
en qué punto se quedó** entre una llamada y la siguiente.

### 14.1 Reescribir un generador como retomable

El cambio de forma es siempre el mismo: en vez de un `for` que recorre `_ancho * _alto` celdas de
una tacada, guarda el índice de la celda en curso como campo del struct, y una función `avanzar()`
que retoma desde ahí. Aquí, sobre `cueva_celular()` (§3):

```gml
// ---------------------------------------------------------------------------
// scr_generador_por_pasos
// Verificado: get_timer, array_create, array_copy (ya usados en el documento);
//             time_source_create, time_source_start, time_source_destroy,
//             time_source_units_frames, time_source_game, call_later
// ---------------------------------------------------------------------------

/// @func GeneradorPorPasos(_ancho, _alto, _semilla, _relleno, _pasos_dobles, _pasos_simples)
/// @desc Reescritura RETOMABLE de cueva_celular() (§3): en vez de hacer las
///       `_pasos_dobles + _pasos_simples` pasadas de golpe, guarda en qué
///       pasada y en qué celda se quedó. `avanzar()` puede llamarse muchas
///       veces; cada vez procesa solo lo que quepa en el presupuesto.
function GeneradorPorPasos(_ancho, _alto, _semilla, _relleno, _pasos_dobles, _pasos_simples) constructor
{
    ancho = _ancho;
    alto  = _alto;
    n     = _ancho * _alto;

    rng = new RNG(_semilla);

    celdas = array_create(n, 1);
    for (var _fy = 1; _fy < alto - 1; _fy++)
        for (var _fx = 1; _fx < ancho - 1; _fx++)
            celdas[_fy * ancho + _fx] = rng.chance(_relleno) ? 1 : 0;

    otro = array_create(n, 1);

    total_pasadas = _pasos_dobles + _pasos_simples;
    pasos_dobles  = _pasos_dobles;
    pasada_actual = 0;
    celda_actual  = 0;    // índice DENTRO de la pasada en curso
    terminado     = false;

    /// @desc Procesa hasta _presupuesto_ms de trabajo REAL, medido con
    ///       get_timer() (que da microsegundos: de ahí el ×1000). Puede
    ///       quedarse a mitad de una pasada — por eso se guarda celda_actual,
    ///       no solo la pasada.
    /// @return {Bool} true si terminó en esta llamada; false si queda trabajo
    avanzar = function(_presupuesto_ms)
    {
        if (terminado) return true;

        var _t0 = get_timer();

        while ((get_timer() - _t0) < _presupuesto_ms * 1000)
        {
            var _usar_r2 = (pasada_actual < pasos_dobles);
            var _fx = celda_actual mod ancho;
            var _fy = celda_actual div ancho;

            var _r1 = contar_muros(celdas, ancho, alto, _fx, _fy, 1);
            var _es_muro = (_r1 >= 5);

            if (!_es_muro && _usar_r2)
            {
                var _r2 = contar_muros(celdas, ancho, alto, _fx, _fy, 2);
                _es_muro = (_r2 <= 2);
            }

            otro[celda_actual] = _es_muro ? 1 : 0;
            celda_actual++;

            if (celda_actual >= n)
            {
                // Pasada completa: intercambiar buffers y pasar a la siguiente.
                array_copy(celdas, 0, otro, 0, n);
                celda_actual = 0;
                pasada_actual++;

                if (pasada_actual >= total_pasadas)
                {
                    terminado = true;
                    return true;
                }
            }
        }

        return false;   // se acabó el presupuesto de este frame; queda trabajo
    };

    /// @desc Progreso [0, 1] para una barra de carga.
    progreso = function()
    {
        return (pasada_actual + celda_actual / n) / total_pasadas;
    };
}
```

### 14.2 Impulsarlo desde el Step de una instancia

El patrón más simple: una instancia de "pantalla de carga" con su propio `Step`, que llama a
`avanzar()` con un presupuesto fijo cada frame y pinta una barra con `progreso()`.

```gml
// ---------------------------------------------------------------------------
// objGeneradorAsincrono — Create
// ---------------------------------------------------------------------------
generador       = new GeneradorPorPasos(192, 128, global.semilla, 0.40, 4, 3);
PRESUPUESTO_MS  = 3;   // ms por frame dedicados a generar; el resto es tuyo

// ---------------------------------------------------------------------------
// objGeneradorAsincrono — Step
// ---------------------------------------------------------------------------
if (!generador.terminado)
{
    if (_boton_cancelar_pulsado())   // lo que sea que detecte tu UI de pausa
    {
        // Nada que destruir: hasta que avanzar() devuelve true no se ha
        // instanciado ni pintado nada (§1.3, separar generación de
        // presentación) — cancelar es simplemente dejar de llamar a avanzar().
        generador = undefined;
        room_goto(rm_menu);
        exit;
    }

    var _listo = generador.avanzar(PRESUPUESTO_MS);

    if (_listo)
    {
        conservar_region_mayor(generador);    // §3.1, ya con el mapa completo
        pintar_mundo(generador, mapa_tiles);  // §2.8
        room_goto(rm_juego);
    }
}

// ---------------------------------------------------------------------------
// objGeneradorAsincrono — Draw GUI
// ---------------------------------------------------------------------------
if (!generador.terminado)
{
    draw_set_color(c_dkgray);
    draw_rectangle(100, 550, 700, 580, false);
    draw_set_color(c_lime);
    draw_rectangle(100, 550, 100 + 600 * generador.progreso(), 580, false);
}
```

### 14.3 Alternativa: un Time Source en vez de un Step propio

Si quien lanza la generación no tiene por qué tener un `Step` que viva hasta el final —por
ejemplo, un controlador persistente al que un botón de menú solo le da la orden— un **Time Source**
que se repite cada frame (`time_source_units_frames`, periodo 1, repeticiones -1) hace lo mismo sin
depender de ningún evento, y se autodestruye al terminar:

```gml
// objControladorCarga — al pulsar "Nueva partida"
generador = new GeneradorPorPasos(192, 128, global.semilla, 0.40, 4, 3);

ts_generacion = time_source_create(
    time_source_game,
    1,
    time_source_units_frames,
    function()
    {
        if (generador.avanzar(3))   // 3 ms de presupuesto por frame
        {
            time_source_destroy(ts_generacion);
            conservar_region_mayor(generador);
            pintar_mundo(generador, mapa_tiles);
            room_goto(rm_juego);
        }
    },
    [], -1
);
time_source_start(ts_generacion);
```

> ⚠️ **Destrúyelo si cancelas o cambias de room a mano.** Igual que con cualquier Time Source
> (`01 · 06 §8`), si el jugador sale antes de que termine, comprueba `time_source_exists(...)` y
> destrúyelo tú: si no, sigue disparándose sobre un generador que ya nadie lee.

### 14.4 El mismo patrón sobre WFC

`ColapsoOndas` (§5.3) ya tiene el método `resolver_un_paso()`: UN colapso y su propagación, en vez
de la rejilla entera. Se conduce igual que `GeneradorPorPasos`, con la salvedad de que una
contradicción a mitad de camino obliga a reiniciar con otra semilla derivada — el mismo criterio
de reintento de §5.3, solo que ahora repartido en el tiempo:

```gml
// objWFCAsincrono — Step
if (!wfc_listo)
{
    var _t0 = get_timer();
    while ((get_timer() - _t0) < PRESUPUESTO_MS * 1000)
    {
        if (_wfc.resolver_un_paso())
        {
            if (_wfc.contradiccion)
            {
                intento++;
                if (intento >= MAX_INTENTOS) { wfc_listo = true; generar_nivel_de_respaldo(); break; }
                _wfc.reiniciar(intento);      // otra semilla derivada (§5.3)
            }
            else
            {
                mapa_wfc = _wfc.volcar_a_indices();
                wfc_listo = true;
            }
            break;
        }
    }
}
```

### 14.5 Cuándo NO hace falta

Repartir la generación tiene un coste de complejidad — un objeto con estado en vez de una función
pura, una pantalla de carga que dibujar. Si `get_timer()` (§2.9) mide que tu generador entero tarda
menos de 1-2 ms, no lo repartas: es una solución para un problema que todavía no tienes. El
umbral operativo: si el presupuesto por frame razonable (2-4 ms, dejando el resto a juego y
render) no le basta a `avanzar()` para completar la generación en un solo `Step`, es cuando toca
partirlo.

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
- [`13 · 02 — Diseño de niveles`](./02%20-%20Dise%C3%B1o%20de%20niveles.md#15-riesgo-recompensa-secretos-y-atajos) — §1.5: las tres capas de secretos que reutiliza la poda de callejones (§3 bis).
- [`13 · 08 — Físicas a mano y fluidos`](./08%20-%20F%C3%ADsicas%20a%20mano%20y%20fluidos.md#12--metaballs-agua-y-limo-estilizados) — §12: metaballs por recorte de alfa; marching squares (§3 ter) es la alternativa vectorial.
- [`13 · 22 — Diseño de mundo y exploración`](./22%20-%20Dise%C3%B1o%20de%20mundo%20y%20exploraci%C3%B3n.md#33-bis--ciudades-y-redes-de-calles) — §3.3 bis: trazado de calles apoyado en el `NodoManzana` derivado del BSP de este documento.
- [`01 · 06 — Eventos y ciclo del juego`](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md#8-time-sources-la-alternativa-moderna-a-los-alarm) — §8: Time Sources y `call_later`, la base de §14.
- [`01 · 07 — Funciones, métodos y ámbito`](../01%20-%20Fundamentos/07%20-%20Funciones%2C%20m%C3%A9todos%20y%20%C3%A1mbito.md#7-closures-clausuras) — §7: closures, lo que hace posible capturar `generador` dentro del callback de un Time Source en §14.

---

## Fuentes

Todas consultadas el **6 de septiembre de 2026**.

**Manual oficial de GameMaker (espejo local, LTS 2026)**

- `random_set_seed` (incluido el argumento `fix_range_bug`) — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Number_Functions/random_set_seed.htm>
- `tilemap_set_at_pixel` — <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_set_at_pixel.htm>
- `room_duplicate` — <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Rooms/room_duplicate.htm>
- `room_instance_add` — <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Rooms/room_instance_add.htm>
- `dbg_slider_int` — <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Debugging/dbg_slider_int.htm>
- `time_source_create` — <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Time_Sources/time_source_create.htm>
- `call_later` — <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Time_Sources/call_later.htm>

**Ruido**

- Ken Perlin, *Improving Noise*, SIGGRAPH 2002 — <https://mrl.cs.nyu.edu/~perlin/paper445.pdf> · curva `6t⁵-15t⁴+10t³`, los 12 gradientes de las aristas del cubo y la discontinuidad de segundo orden de la curva antigua.
- Amit Patel (Red Blob Games), *Making maps with noise functions*, 2015 (act. 2022) — <https://www.redblobgames.com/maps/terrain-from-noise/> · elevación + humedad → biomas, amplitudes `[1, 0.5, 0.25]` divididas por su suma, redistribución por exponente, «square bump» para islas y la advertencia sobre rangos.
- Amit Patel, *Hexagonal grids* — <https://www.redblobgames.com/grids/hexagons/> (act. 24-07-2026) · si generas sobre hexágonos en vez de cuadrados.

**Autómatas celulares**

- RogueBasin, *Cellular Automata Method for Generating Random Cave-Like Levels* — <http://www.roguebasin.com/index.php?title=Cellular_Automata_Method_for_Generating_Random_Cave-Like_Levels> · la regla `R1(p) >= 5 || R2(p) <= 2`, relleno inicial del 40 % y la secuencia de 4 + 3 pasadas. ⚠️ La página devuelve **403** al acceso directo; se leyó a través de un proxy de lectura sobre esa misma URL.

**Marching squares**

- Jamie Wong, *Metaballs and Marching Squares*, 19-08-2014 — <https://jamie-wong.com/2014/08/19/metaballs-and-marching-squares/> · las `2⁴` configuraciones de un campo binario, la interpolación lineal en el borde para evitar ángulos de 90°/45°, y la relación directa con la suma de campos de un metaball.
- Paul Bourke, *Polygonising a Scalar Field*, 05-1994 (tablas de Cory Bloyd y Geoffrey Heller) — <https://paulbourke.net/geometry/polygonise/> · la versión 3D (marching cubes) del mismo principio, y la fórmula de interpolación `P = P1 + (isovalue - V1)(P2 - P1)/(V2 - V1)` que aquí se traduce a `borde_interpolado()`.

**Difusión limitada por agregación y multi-agente**

- RogueBasin, *Diffusion-limited aggregation* — <https://www.roguebasin.com/index.php/Diffusion-limited_aggregation> · el caminante que se excava a sí mismo al tocar la estructura, la garantía de conectividad, y por qué los bucles son infrecuentes. ⚠️ La página devuelve **403** al acceso directo; se leyó a través de un proxy de lectura sobre esa misma URL.
- J. Doran e I. Parberry, *Controlled Procedural Terrain Generation Using Software Agents*, IEEE Transactions on Computational Intelligence and AI in Games 2(2), 2010, resumido en Noor Shaker, Julian Togelius y Mark J. Nelson, *Procedural Content Generation in Games*, cap. 4 (*Fractals, noise and agents with applications to landscapes*), Springer 2016 — <https://www.pcgbook.com/chapter04.pdf> · agentes especializados (costa, suavizado, playa, montaña, río) con presupuesto de "tokens" propio, escribiendo todos sobre el mismo mapa — el origen de `Cavador` y `cueva_multiagente`.

**Muestreo**

- Robert Bridson, *Fast Poisson Disk Sampling in Arbitrary Dimensions*, SIGGRAPH 2007 sketch — <https://www.cs.ubc.ca/~rbridson/docs/bridson-siggraph07-poissondisk.pdf> · celda `r/√n`, lista activa, `k = 30`, anillo `[r, 2r]`, `2N-1` iteraciones.

**Voronoi**

- Amit Patel, *Polygonal Map Generation for Games*, 09-2010 (act. 01-2025) — <http://www-cs-students.stanford.edu/~amitp/game-programming/polygon-map-generation/> · Voronoi por semillas para mapas de "unos cientos de polígonos", la relajación de Lloyd (mover cada semilla al centroide, dos pasadas bastan), y su aplicación a biomas y ríos.

**Wave Function Collapse**

- Boris the Brave, *Wave Function Collapse explained*, 13-04-2020 (act. 28-02-2025) — <https://www.boristhebrave.com/2020/04/13/wave-function-collapse-explained/> · WFC como problema de restricciones, entropía de Shannon con pesos, y por qué la implementación de referencia se salta el backtracking.
- Maxim Gumin, repositorio `mxgmn/WaveFunctionCollapse` (MIT) — <https://github.com/mxgmn/WaveFunctionCollapse> · modelos *overlapping* y *simple tiled*, atribución a la *Model Synthesis* de Paul Merrell (2009) y el comportamiento ante contradicciones.
- Boris the Brave, *Dungeon generation in Unexplored*, 10-04-2021 — <https://www.boristhebrave.com/2021/04/10/dungeon-generation-in-unexplored/> · el caso contrario: reescritura de grafos en vez de restricciones locales.

**Gramáticas y estructura**

- Przemyslaw Prusinkiewicz y Aristid Lindenmayer, *The Algorithmic Beauty of Plants*, Springer 1990 (edición electrónica libre) — <http://algorithmicbotany.org/papers/#abop> · `G = ⟨V, ω, P⟩` y la aplicación **en paralelo** de las producciones frente a las gramáticas de Chomsky.
- Gillian Smith, Mike Treanor, Jim Whitehead y Michael Mateas, *Rhythm-Based Level Generation for 2D Platformers*, FDG/ICFDG 2009 — <https://eis.ucsc.edu/papers/smith-fdg-09.pdf> · *rhythm groups*, gramática de dos capas (ritmo → geometría), métricas del avatar y el filtrado con *critics* sobre 1 000 candidatos.
- Noor Shaker, Julian Togelius y Mark J. Nelson, *Procedural Content Generation in Games*, Springer 2016 (libre en la web de los autores) — <https://www.pcgbook.com/> · la definición *«the algorithmic creation of game content with limited or indirect user input»*, y los capítulos 3 (métodos constructivos), 4 (fractales y ruido) y 5 (gramáticas y L-systems).
