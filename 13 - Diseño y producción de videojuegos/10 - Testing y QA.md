# 10 · Testing y QA

> Cómo se prueba un juego hecho con GameMaker: qué se puede automatizar y qué no, cómo
> escribir GML que se deje probar, un mini-framework de pruebas completo que ya compila
> y corre con `gm-cli`, los frameworks que existen, y el trabajo humano que ninguna
> máquina hace por ti — QA manual, playtesting y triaje de bugs.
>
> **Lo que NO cubre este documento** (porque ya está cubierto y sería duplicarlo):
> el Debug Overlay, el Debugger del IDE, el recolector de basura y las vistas `dbg_*` están
> en [`01 · 15 — Depuración y rendimiento`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md);
> el catálogo comparado de frameworks de test está en
> [`12 · 01 — Herramientas del flujo de trabajo`](../12%20-%20Utilidades%20e%20integraciones/01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md) §4;
> los requisitos de cada tienda están en
> [`05 · 02 — Publicar y exportar`](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md).

**Todo el código de este documento se ha compilado y ejecutado de verdad** en un proyecto
creado con `gm-cli init` sobre GameMaker LTS 2026.0 (runtime `2026.0.0.23`), el 6 de
septiembre de 2026. Las salidas que verás son copias literales de la terminal.

---

## 1 · Los principios

### 1.1 Un juego no es una aplicación de gestión

La razón por la que el testing automático llegó tarde a los videojuegos no es pereza: es que
**la mayor parte de lo que hace bueno a un juego no es una función pura**. «El salto se siente
flotante», «el jefe es injusto», «no entiendo qué tengo que hacer» son defectos reales y
ningún `assert` los detecta.

Pero debajo de esa capa hay muchísimo código que **sí** es determinista y aburrido, y es
justo donde se esconden los bugs que cuestan dinero: el cálculo de daño, la curva de
experiencia, el guardado, el inventario, la generación de mazmorras, el parser de diálogos,
la conversión de coordenadas de mundo a pantalla.

| Se automatiza bien | Se automatiza mal o nada |
|---|---|
| Funciones puras: matemáticas, balance, parsers | Sensación de control («game feel») |
| Serialización: guardar → cargar → comparar | Dificultad y curva de aprendizaje |
| Máquinas de estado con transiciones definidas | Legibilidad de la interfaz y estética |
| Generación procedural con semilla fija | Que el juego sea divertido |
| Invariantes: «la vida nunca es negativa» | Bugs de driver gráfico y de mando concreto |
| Que el proyecto **compile** y **arranque** en todos los targets | Rendimiento en hardware que no tienes |

> 💡 La regla práctica: **si puedes escribir el resultado esperado como un número, un string o
> un array, hazlo una prueba automática. Si solo puedes describirlo con un adjetivo, es
> playtesting.**

### 1.2 La pirámide, adaptada

La pirámide de test clásica (muchas unitarias, pocas de integración, poquísimas de extremo a
extremo) sirve, pero en GameMaker las capas se llaman de otra manera:

```
                    ┌───────────────────────┐
                    │    5. PLAYTESTING     │   personas reales, sin ayuda
                    │   (días, muy caro)    │   → mide diversión y comprensión
                    ├───────────────────────┤
                    │  4. QA MANUAL         │   plan de pruebas por sistema
                    │  (horas, caro)        │   → mide plataformas y casos raros
                    ├───────────────────────┤
                    │  3. SMOKE TEST        │   ¿arranca y llega al menú?
                    │  (1 min, barato)      │   → mide que el build no está muerto
                    ├───────────────────────┤
                    │  2. INTEGRACIÓN       │   objetos reales en una room de test
                    │  (segundos)           │   → mide que los sistemas encajan
                    ├───────────────────────┤
                    │  1. UNITARIAS         │   funciones y structs sin instancias
                    │  (milisegundos)       │   → mide la lógica pura
                    └───────────────────────┘
```

Cada escalón hacia arriba es **más lento, más caro y más frágil**. La estrategia sensata es la
misma que en cualquier otro oficio: empuja todo lo que puedas hacia abajo.

En un proyecto GameMaker eso se traduce en: scripts `scr_pruebas_*` sobre funciones puras
(capa 1) · una `rm_pruebas` con objetos reales y un objeto árbitro (capa 2) · `gm-cli run`
comprobando que se llega al menú sin excepción (capa 3) · plan de pruebas y matriz de
plataformas (capa 4) · sesiones grabadas con jugadores (capa 5).

### 1.3 El coste de encontrar un fallo

El mismo defecto cuesta órdenes de magnitud más según dónde lo encuentres: **Feather** lo
señala en segundos y te dice la línea; una **prueba unitaria** lo señala en minutos y te dice
la función; **QA manual** cuesta horas porque primero hay que reproducirlo; y **un jugador
tras el lanzamiento** cuesta un parche, una nota y reseñas negativas. Automatizar no es
elegancia: es mover el hallazgo hacia arriba de esa lista.

---

## 2 · Escribir GML que se deje probar

Esto es el 80 % del trabajo. **Un framework de pruebas no arregla código imposible de probar.**

### 2.1 Lógica pura fuera de las instancias

Una función es *pura* si su resultado depende solo de sus argumentos y no toca nada de fuera.
En GML eso significa: no lee `x`, `y`, `image_index`, `global.*` ni `instance_*`, y no dibuja.

```gml
// ❌ Imposible de probar sin montar media room — Step de obj_jugador
if (keyboard_check(vk_right)) { hsp += aceleracion; }
hsp = clamp(hsp, -vel_max, vel_max);
if (!keyboard_check(vk_right) && !keyboard_check(vk_left)) { hsp *= friccion; }
x += hsp;
```

```gml
// ✅ La misma regla, extraída y comprobable en un milisegundo
/// @param {Real}   _velocidad   Velocidad actual.
/// @param {Real}   _direccion   -1 izquierda, 0 nada, 1 derecha.
/// @param {Struct} _ajustes     {aceleracion, friccion, velocidad_maxima}
/// @returns {Real}
function calcular_velocidad_horizontal(_velocidad, _direccion, _ajustes)
{
    if (_direccion != 0)
    {
        _velocidad += _ajustes.aceleracion * sign(_direccion);
        return clamp(_velocidad, -_ajustes.velocidad_maxima, _ajustes.velocidad_maxima);
    }
    _velocidad *= _ajustes.friccion;
    return (abs(_velocidad) < 0.05) ? 0 : _velocidad;
}

// Step de obj_jugador — ahora es una línea de pegamento
var _dir = keyboard_check(vk_right) - keyboard_check(vk_left);
hsp = calcular_velocidad_horizontal(hsp, _dir, ajustes_movimiento);
x += hsp;
```

De regalo, la regla es ahora **reutilizable** (el enemigo usa la misma) y **ajustable desde un
struct de datos**, que es justo lo que quieres para tunear el movimiento sin recompilar.

### 2.2 Inyecta lo que no controlas: azar, reloj y entrada

Las tres fuentes de indeterminismo que rompen una prueba son siempre las mismas.

```gml
// ❌ Distinta cada vez que la llamas:
//    function generar_botin(_nivel) { return (random(1) < 0.1) ? "legendario" : "comun"; }

// ✅ El azar entra por la puerta: le pasas la fuente
/// @desc Fuente de números aleatorios reproducible (congruencial lineal de 32 bits).
///       Sirve tanto para el juego como para las pruebas, con la misma semilla.
/// @param {Real} _semilla
function AzarReproducible(_semilla) constructor
{
    estado = _semilla;

    /// @returns {Real} Real en [0, 1).
    static siguiente = function()
    {
        estado = (estado * 1103515245 + 12345) % 2147483648;
        return estado / 2147483648;
    }

    /// @returns {Real} Entero en [0, _n].
    static entero_hasta = function(_n)
    {
        return floor(siguiente() * (_n + 1));
    }
}

/// @desc Decide el botín. Determinista para una misma fuente y semilla.
/// @param {Real}   _nivel
/// @param {Struct} _azar   Instancia de AzarReproducible.
/// @returns {String}
function generar_botin(_nivel, _azar)
{
    if (_azar.siguiente() < 0.1) { return "legendario"; }
    return (_azar.entero_hasta(10) > 7) ? "raro" : "comun";
}
```

Ahora la prueba es trivial: `generar_botin(3, new AzarReproducible(42))` devuelve **siempre**
lo mismo, en tu máquina y en CI.

> ⚠️ `random_set_seed()` también fija la secuencia global del motor y sirve para el juego, pero
> **no aísla**: cualquier otra llamada a `random()` en el mismo frame desplaza la secuencia y
> la prueba deja de ser reproducible. Para pruebas, una fuente propia inyectada es más segura.

El mismo movimiento vale para el reloj y para la entrada: en vez de leer `current_time` o
`keyboard_check()` dentro de la regla, se pasan como argumento.

```gml
// ❌ function esta_el_buff_activo(_buff)  { return current_time < _buff.fin; }
// ✅
function esta_el_buff_activo(_buff, _ahora) { return _ahora < _buff.fin; }

// ❌ function decidir_accion()  { return keyboard_check(ord("Z")) ? "saltar" : "nada"; }
// ✅ _entrada es un struct que en el juego rellena el lector de input y en la prueba, tú
function decidir_accion(_entrada) { return _entrada.saltar ? "saltar" : "nada"; }
```

### 2.3 Separa calcular de dibujar

Un evento `Draw` que además calcula es intestable por definición: para comprobar el resultado
tendrías que leer píxeles. La regla de siempre — **el Step decide, el Draw pinta** — es, además
de una regla de rendimiento, la que hace posible el testing.

```gml
/// @desc Geometría de una barra de vida. No dibuja nada: por eso se puede probar.
/// @returns {Struct} {ancho_relleno, color}
function calcular_barra_vida(_vida, _vida_maxima, _ancho_total)
{
    var _fraccion = (_vida_maxima <= 0) ? 0 : clamp(_vida / _vida_maxima, 0, 1);
    return {
        ancho_relleno: round(_ancho_total * _fraccion),
        color:         (_fraccion > 0.5) ? c_lime : ((_fraccion > 0.2) ? c_yellow : c_red)
    };
}

// Draw GUI — tonto a propósito
var _b = calcular_barra_vida(vida, vida_maxima, 200);
draw_set_colour(_b.color);
draw_rectangle(20, 20, 20 + _b.ancho_relleno, 32, false);
draw_set_colour(c_white);
```


> El razonamiento largo sobre dónde va cada responsabilidad está en
> [`13 · 06 — Arquitectura de un proyecto GameMaker`](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md). Aquí solo interesa la
> consecuencia: **lo que no calcula el Draw, lo puedes probar.**

### 2.4 La frontera: qué no vas a probar y está bien

No intentes cubrir con unitarias el **dibujado** (un test que llama a `draw_*` fuera de un
evento de dibujo o falla o no mide nada), los **eventos del motor** (`Create`, `Step`,
`Alarm`: eso es integración y va en una room de test), el **audio** (comprueba que *decides*
reproducir el sonido correcto, no que suene) ni la **red contra servidores reales** (prueba el
serializador de paquetes).

### 2.5 · Probar el audio

La frontera de arriba dice qué NO probar; esto es lo que sí, y cómo. «No pruebes que suena» no
significa «no pruebes nada»: hay tres piezas del audio que son código normal, deterministas, y
caben en el mismo `scr_pruebas` de la sección siguiente.

**1. Que la decisión de sonar se toma.** Extrae la decisión a una función pura, con el mismo
movimiento de inyección que §2.2, y prueba ESA función, nunca la llamada real a `audio_play_sound`:

```gml
// ❌ No pruebes esto: llama al motor de audio de verdad
// function reaccionar_a_golpe(_vida) { if (_vida <= 0) { audio_play_sound(snd_muerte, 100, false); } }

// ✅ Separa la decisión de la ejecución
function sonido_por_golpe(_vida_antes, _vida_despues)
{
    if (_vida_despues <= 0)           { return "muerte"; }
    if (_vida_despues < _vida_antes)  { return "dano"; }
    return undefined;
}

// La prueba no toca audio_play_sound en ningún momento
probar("golpe letal decide sonido de muerte", function()
{
    afirmar_igual(sonido_por_golpe(10, 0), "muerte");
});
probar("golpe no letal decide sonido de daño", function()
{
    afirmar_igual(sonido_por_golpe(10, 6), "dano");
});
probar("sin cambio de vida no decide nada", function()
{
    afirmar_igual(sonido_por_golpe(10, 10), undefined);
});
```

**2. Que no se supera el cupo de voces.** Esto ya usa audio de verdad —es una prueba de
integración, en una room de test, no una unitaria pura— pero el resultado que compruebas es un
número, no una percepción: reutiliza `sonar_limitado()` de
[13 · 09 §3.3](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md) y comprueba que el array de voces
vivas nunca crece por encima del cupo:

```gml
probar("el cupo de voces nunca se supera", function()
{
    voces_iniciar();
    for (var _i = 0; _i < 20; _i += 1) { sonar_limitado(snd_prueba_impacto, 4); }
    afirmar_cierto(array_length(struct_get(global.voces, audio_get_name(snd_prueba_impacto))) <= 4,
                   "el cupo de voces se ha saltado");
});
```

**3. Que todo emisor se libera en su Clean Up.** También de integración: crea la instancia en una
room de test, destrúyela, y comprueba con `audio_emitter_exists()` que el emisor ya no existe.
Es la versión automatizada de la comprobación manual que ya pide
[13 · 09 §10.1](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md) con la ventana **Audio** del
Debug Overlay:

```gml
probar("el emisor se libera al destruir la instancia", function()
{
    var _inst = instance_create_layer(0, 0, "Instances", obj_enemigo_con_emisor);
    var _em   = _inst.em_pasos;              // el emisor creado en su Create
    instance_destroy(_inst);                  // dispara su Clean Up de inmediato
    afirmar_cierto(!audio_emitter_exists(_em), "el Clean Up no liberó el emisor");
});
```

### La matriz de dispositivos de escucha

La matriz de plataformas de [§9.2](#92-la-matriz-de-plataformas) prueba dónde corre el juego; esta
es la misma idea aplicada a **cómo se oye**, y es la que de verdad encuentra bugs de mezcla:

| Dispositivo | Qué revela |
|---|---|
| Altavoces de portátil (mono o casi-mono) | Si algo importante solo suena por un canal, aquí desaparece |
| Auriculares baratos con cable | La referencia «normal»: donde jugará la mayoría |
| Auriculares Bluetooth | Latencia añadida (§«Latencia» de [04 · 28 §3 bis](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md) si el juego es móvil) y compresión que se come agudos |
| Altavoz del móvil o de una TV | Rango de graves casi nulo: si el impacto solo vive en los graves, aquí no se oye |
| Volumen del sistema al mínimo | Confirma que **nada crítico** depende solo del audio ([13 · 09 §8](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md), accesibilidad) |
| Sin ningún audio (mudo total) | La prueba de accesibilidad honesta: 10 minutos sin volumen, ver qué se deja de entender |

> 💡 **Un bug de mezcla que solo aparece en un dispositivo de la matriz sigue siendo un bug.**
> «Suena bien en mis auriculares de estudio» no es la vara de medir: la vara es esta matriz.

### El protocolo de sesión larga

[13 · 09 §10.1](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md) ya deja el requisito en dos
líneas de checklist («20-30 min de partida medidos» y «30 minutos seguidos sin que nada moleste»);
esto es cómo ejecutarlo como parte de la sesión larga que ya haces en [§9.4](#94-la-sesión-larga-soak-test):

1. **Arranca la sesión larga habitual de §9.4** (memoria, instancias, surfaces) y súmale el audio:
   deja el juego corriendo 20-30 minutos de partida real, no en el menú.
2. **Abre la ventana Audio del Debug Overlay** (`audio_debug()`) al principio y de nuevo al final.
   Compara el número de voces activas en reposo: si sube con el tiempo, hay emisores o voces que
   no se están liberando — el mismo síntoma que la memoria de §9.4, pero en el hilo de audio.
3. **Mide loudness y pico** de una grabación de esos 20-30 minutos (§4.4 de 13 · 09): integrado
   entre −23 y −18 LUFS, pico por debajo de −1 dBTP.
4. **Escucha, no solo midas:** 30 minutos seguidos con auriculares baratos a volumen bajo. Lo que
   cansa al oído en una sesión larga casi nunca se nota en una prueba de dos minutos —un *one-shot*
   de ambiente demasiado frecuente, un *loop* con un clic al reiniciar— y es exactamente lo que
   este protocolo existe para cazar.

---

## 3 · Un mini-framework de pruebas en un solo script de GML

No necesitas una librería para empezar. Esto es todo lo que hace falta: **un script** de unas
130 líneas contando JSDoc, cero dependencias, y una salida que un servidor de integración
continua sabe leer.

> Ojo, no confundas esto con el `assert()` de
> [`05 · 04 — Convenciones y estilo GML`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) §7:
> aquel es una **guarda de producción** (grita en desarrollo, calla en release); estas
> `afirmar_*` son **aserciones de prueba** que anotan el fallo y dejan continuar la tanda.

### 3.1 El script `scr_pruebas`

```gml
// ═══════════════════════════════════════════════════════════════════════
//  scr_pruebas — mini-framework de pruebas unitarias en GML
//  Un solo script, sin dependencias. Pensado para correr con gm-cli.
// ═══════════════════════════════════════════════════════════════════════

/// @desc Prepara el estado del ejecutor. Llámalo una vez, antes del primer probar().
function pruebas_iniciar()
{
    global.pruebas = {
        total:          0,
        fallidas:       0,
        aserciones:     0,
        fallos_actual:  [],
        arranque:       get_timer()
    };
    show_debug_message("=== PRUEBAS ===");
}

/// @desc Anota un fallo en la prueba en curso. La usan las afirmaciones.
/// @param {String} _texto
function pruebas_anotar_fallo(_texto)
{
    array_push(global.pruebas.fallos_actual, _texto);
}

/// @desc Convierte lo capturado por catch en texto legible.
///       Si el throw fue de un string, catch recibe el string, no un struct.
/// @param {Any} _e
/// @returns {String}
function pruebas_describir_excepcion(_e)
{
    if (is_struct(_e) && struct_exists(_e, "message"))
    {
        return $"{_e.message} (en {_e.script})";
    }
    return string(_e);
}

/// @desc Ejecuta una prueba aislada. Captura la excepción para que un fallo no tumbe la tanda.
/// @param {String}   _nombre  Nombre legible de la prueba.
/// @param {Function} _cuerpo  Función sin argumentos con el cuerpo de la prueba.
function probar(_nombre, _cuerpo)
{
    var _p = global.pruebas;
    _p.total++;
    _p.fallos_actual = [];

    var _inicio = get_timer();
    try
    {
        _cuerpo();
    }
    catch (_e)
    {
        pruebas_anotar_fallo("excepcion no esperada: " + pruebas_describir_excepcion(_e));
    }
    var _ms = (get_timer() - _inicio) / 1000;

    if (array_length(_p.fallos_actual) == 0)
    {
        show_debug_message($"  ok    {_nombre}  ({string_format(_ms, 1, 2)} ms)");
        exit;
    }

    _p.fallidas++;
    show_debug_message($"  FALLO {_nombre}  ({string_format(_ms, 1, 2)} ms)");
    for (var _i = 0; _i < array_length(_p.fallos_actual); _i++)
    {
        show_debug_message($"          {_p.fallos_actual[_i]}");
    }
}

/// @desc Afirma que dos valores son iguales. Los arrays se comparan por contenido.
function afirmar_igual(_obtenido, _esperado, _mensaje = "")
{
    global.pruebas.aserciones++;
    var _ok = (is_array(_obtenido) && is_array(_esperado))
            ? array_equals(_obtenido, _esperado)
            : (_obtenido == _esperado);
    if (!_ok)
    {
        pruebas_anotar_fallo($"esperaba {string(_esperado)}, obtuve {string(_obtenido)}. {_mensaje}");
    }
    return _ok;
}

/// @desc Afirma que una expresión es verdadera.
function afirmar_cierto(_expresion, _mensaje = "")
{
    global.pruebas.aserciones++;
    if (!_expresion)
    {
        pruebas_anotar_fallo($"esperaba true, obtuve {string(_expresion)}. {_mensaje}");
    }
    return _expresion;
}

/// @desc Afirma que la función lanza una excepción. Si no lanza, es un fallo.
function afirmar_lanza(_cuerpo, _mensaje = "")
{
    global.pruebas.aserciones++;
    var _lanzo = false;
    try { _cuerpo(); } catch (_e) { _lanzo = true; }
    if (!_lanzo)
    {
        pruebas_anotar_fallo($"esperaba una excepcion y no se lanzo. {_mensaje}");
    }
    return _lanzo;
}

/// @desc Cierra la tanda, imprime el resumen y termina con código 0 (verde) o 1 (rojo).
function pruebas_terminar()
{
    var _p  = global.pruebas;
    var _ms = (get_timer() - _p.arranque) / 1000;

    show_debug_message("");
    show_debug_message($"{_p.total} pruebas | {_p.aserciones} aserciones | {_p.fallidas} fallidas | {string_format(_ms, 1, 1)} ms");
    show_debug_message(_p.fallidas == 0 ? "RESULTADO: OK" : "RESULTADO: FALLO");

    game_end(_p.fallidas == 0 ? 0 : 1);
}
```

**Tres detalles que no son obvios:**

1. **`game_end([return_code])` sí acepta un código de salida**, opcional y con `0` por defecto.
   La página **en español** del manual todavía muestra la firma vieja `game_end();`; la
   **inglesa** y el `GmlSpec.xml` del runtime `2026.0.0.23` documentan `return_code`. Cuando
   manual traducido y spec no coinciden, **gana el spec** ([`AGENTS.md`](../AGENTS.md) §1 bis).
2. **`catch` no siempre recibe un struct.** Del runtime sí (`message`, `longMessage`, `script`,
   `stacktrace`); de un `throw "texto"` recibe **el string tal cual** y `_e.message` reventaría.
   Por eso existe `pruebas_describir_excepcion()`.
3. `exit` dentro de `probar()` sale **de la función**, no del juego.

### 3.2 Una tanda de pruebas real

```gml
// ═══════════ scr_pruebas_combate ═══════════

/// @desc Daño final tras armadura y crítico. Lógica pura: no lee ni escribe instancias.
/// @param {Real} _base       Daño bruto, >= 0.
/// @param {Real} _armadura   Fracción absorbida, se recorta a 0..0.9.
/// @param {Bool} _critico
/// @returns {Real}
function calcular_dano(_base, _armadura, _critico)
{
    if (!is_numeric(_base) || _base < 0) { throw $"dano base invalido: {_base}"; }
    var _absorcion = clamp(_armadura, 0, 0.9);
    var _dano = _base - (_base * _absorcion);
    if (_critico) { _dano *= 2; }
    return floor(_dano);
}

/// @desc Tanda de pruebas del cálculo de daño.
function pruebas_de_combate()
{
    probar("sin armadura el dano es el base", function() {
        afirmar_igual(calcular_dano(10, 0, false), 10);
    });

    probar("la armadura reduce el dano", function() {
        afirmar_igual(calcular_dano(10, 0.5, false), 5);
    });

    probar("la armadura se recorta al 90 por ciento", function() {
        afirmar_igual(calcular_dano(100, 5, false), 10);
    });

    probar("el critico dobla el dano", function() {
        afirmar_igual(calcular_dano(10, 0, true), 20);
    });

    probar("el dano base negativo lanza", function() {
        afirmar_lanza(function() { calcular_dano(-1, 0, false); });
    });
}
```

Y el objeto que lo lanza, en un `Create`:

```gml
// ─── Create de obj_ejecutor_pruebas ───
pruebas_iniciar();
pruebas_de_combate();
pruebas_terminar();
```

> 🎯 **Esta tanda encontró un bug de verdad mientras se escribía este documento.** La primera
> versión calculaba `_base * (1 - _absorcion)`. Con `_base = 100` y `_absorcion = 0.9`, en
> coma flotante `1 - 0.9` da `0.09999999999999998`, y `floor(9.999999999999998)` es **9**, no
> 10. La prueba dijo `esperaba 10, obtuve 9` y la corrección fue reordenar la expresión a
> `_base - (_base * _absorcion)`. Ese es exactamente el tipo de fallo que ningún playtester
> reporta y que desequilibra un juego en silencio.

### 3.3 Ejecutarlo desde la terminal, de verdad

Los recursos se crean con `gm-cli resourcetool eval "resource create type=script name=…"` y
`"object event findorcreate …"` —**nunca editando el `.yy` a mano**— y el `.gml` con tu editor
de siempre. Después:

```sh
gm-cli compile --errors-only   # puerta 1: ¿compila?
gm-cli run                     # puerta 2: ¿pasan las pruebas?
```

Salida literal de `gm-cli run` con la tanda en verde (6 de septiembre de 2026, macOS,
runtime `2026.0.0.23`):

```
│  === PRUEBAS ===
│    ok    sin armadura el dano es el base  (0.01 ms)
│    ok    la armadura reduce el dano  (0.00 ms)
│    ok    la armadura se recorta al 90 por ciento  (0.00 ms)
│    ok    el critico dobla el dano  (0.00 ms)
│    ok    el dano base negativo lanza  (0.00 ms)
│  5 pruebas | 5 aserciones | 0 fallidas | 0.3 ms
│  RESULTADO: OK
│  ###game_end###0
```

Con un fallo, las líneas cambian a `FALLO …`, `esperaba 21, obtuve 20.`, `RESULTADO: FALLO`
y `###game_end###1`.

### 3.4 ⚠️ `gm-cli run` NO devuelve el código de salida del juego

Esto es lo más importante de toda la sección y no está escrito en ningún sitio:

> **`gm-cli run` sale con `0` aunque el juego llame a `game_end(1)`.** Verificado en `gm-cli`
> 2.3.0 el 6 de septiembre de 2026: con la tanda en rojo, `echo $?` devolvió `0`.

Lo que **sí** puedes usar es que el runner imprime una línea con el código:

```
###game_end###1
```

Así que el envoltorio de CI tiene que leer la salida, no el código de salida. Este script está
probado y devuelve `0` en verde y `1` en rojo:

```sh
#!/usr/bin/env bash
# correr-pruebas.sh — devuelve 0 solo si el juego terminó con game_end(0).
set -uo pipefail

SALIDA="$(mktemp)"
gm-cli run --target mac > "$SALIDA" 2>&1

if grep -q '###game_end###0' "$SALIDA"; then
    grep -E 'ok    |FALLO|pruebas \|' "$SALIDA" | sed 's/^│  //'
    echo "PRUEBAS: OK"
    rm -f "$SALIDA"
    exit 0
fi

echo "PRUEBAS: FALLO"
grep -E 'ok    |FALLO|pruebas \||###game_end###' "$SALIDA" | sed 's/^│  //'
rm -f "$SALIDA"
exit 1
```

Comprobado en las dos direcciones: en verde imprime la tanda y sale con `0`; con una prueba
rota imprime `###game_end###1` y sale con `1`.

Los *flags* reales de `gm-cli run` y `gm-cli compile` (comprobados con `--help` el 6 de
septiembre de 2026) son exactamente estos —`--target`, `--toolchain`, `--runtime {vm|native}`,
`--verbose`, `--errors-only`, `--license`, `--cache-dir`, `--config`, `--toolchain-options`—
y **no hay ninguno para pasarle argumentos al juego**. `gm-cli package` añade `-o / --output`.
No inventes otros: el detalle completo del CLI está en
[`07 · 13 — GM CLI`](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md).

### 3.5 Encender el modo pruebas sin tocar el código

Como no puedes pasarle argumentos al juego desde `gm-cli run`, la vía limpia es una
**configuración del proyecto**. `os_get_config()` devuelve su nombre en tiempo de ejecución:

```sh
gm-cli resourcetool eval "config create name=Pruebas parent=Default"
gm-cli run --config Pruebas
```

```gml
// ─── Create de obj_ejecutor_pruebas ───
if (os_get_config() != "Pruebas") { instance_destroy(); exit; }

pruebas_iniciar();
pruebas_de_combate();
pruebas_terminar();
```

Verificado: con `gm-cli run --config Pruebas` la salida trae `CONFIG ACTIVA = Pruebas` y la
tanda entera; con `gm-cli run` a secas trae `CONFIG ACTIVA = Default` y **ninguna prueba se
ejecuta**. Es el interruptor más limpio que hay, porque no toca el código.

Alternativa si prefieres no crear configuraciones: `environment_get_variable("MI_JUEGO_MODO")`
lee una variable de entorno del proceso.

> ⚠️ Verificado en este Mac: si el proyecto vive bajo `/private/tmp`, el runner de macOS
> arranca, escribe `not in bundle` y **muere con SIGSEGV sin ejecutar nada**, mientras
> `gm-cli run` sigue diciendo `Game exited` y devolviendo `0`. Copiado el mismo proyecto al
> directorio del usuario, funcionó a la primera. Si tus pruebas «pasan» sin imprimir nada,
> sospecha de la ruta antes que del código.

---

## 4 · Los frameworks que ya existen

La tabla comparada de los siete frameworks (estrellas, licencia, fecha, ruta local) está en
[`12 · 01 — Herramientas del flujo de trabajo`](../12%20-%20Utilidades%20e%20integraciones/01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md) §4.
**No la repito.** Aquí va lo que allí no cabe: cómo se usan los dos que importan.

Todos están descargados; las rutas exactas salen de
[`11 · _RUTAS.json`](../11%20-%20C%C3%B3digo%20descargado/_RUTAS.json):

```sh
find "11 - Código descargado" -iname "*TestFramework*"
# → 11 - Código descargado/plantillas_y_ejemplos/GM-TestFramework
```

| Framework | Ruta local |
|---|---|
| GM-TestFramework | `11 - Código descargado/plantillas_y_ejemplos/GM-TestFramework` |
| crispy | `11 - Código descargado/librerias/depuracion/crispy` |
| gm-verrific | `11 - Código descargado/librerias/depuracion/gm-verrific` |
| olympus | `11 - Código descargado/librerias/depuracion/olympus` |
| ganary | `11 - Código descargado/librerias/depuracion/ganary` |
| gms2-test | `11 - Código descargado/librerias/depuracion/gms2-test` |
| GMBenchmark | `11 - Código descargado/librerias/depuracion/GMBenchmark` |

### 4.1 GM-TestFramework — el oficial de YoYo Games

Es **el framework interno del equipo del motor**, publicado para que la comunidad aporte tests
que demuestren bugs. Se ejecuta en cada build de GameMaker y los resultados van a los equipos
de QA y Core Tech. Ficha completa en
[`07 · 01 — GitHub · organización YoYoGames`](../07%20-%20Ecosistema/01%20-%20GitHub%20-%20organizaci%C3%B3n%20YoYoGames.md).

**Cómo está montado** (leído del repositorio clonado):

```
GM-TestFramework/
  launcher.py       orquestador en Python: descarga runtime, lanza Igor, recoge resultados
  tf_compare.py     compara dos tandas de resultados (regresión entre runtimes)
  classes/ utils/   modelo de resultados, servidor de control remoto y utilidades, en Python
  projects/xUnit/   ⬅ EL PROYECTO DE GAMEMAKER (100+ scripts)
      scripts/Assert/ + AssertAPI/   la clase Assert y las funciones globales assert_* (942 líneas)
      scripts/Test/ TestSuite/ TestFrameworkRun/   prueba, conjunto y tanda entera
      scripts/Basic*TestSuite/       las suites reales: Maths, String, Array, Buffer, Json,
                                     Surface, Shader, Handles, WeakRefs, Room, Network…
```

**Escribir una suite** es heredar de `TestSuite` y llamar a `addFact`:

```gml
// Tal cual está escrito en scripts/BasicMathsTestSuite/BasicMathsTestSuite.gml
function BasicMathsTestSuite() : TestSuite() constructor {

    addFact("abs_test #1", function() {
        var numOne = 2;
        var resOne = abs(numOne);
        assert_equals(resOne, 2, "#1 Positive");
    })
}
```

Y registrarla en el `Create` de `objRunner`:

```gml
testFramework.addSuite(BasicMathsTestSuite);
```

Las aserciones son funciones globales que delegan en un singleton (`assert_get_singleton()`):
`assert_equals`, `assert_not_equals`, `assert_greater`, `assert_greater_or_equal`,
`assert_less`, `assert_less_or_equal`… más `addTheory` para pruebas guiadas por datos y
`addTestAsync` para eventos asíncronos. La suite completa se configura con macros propios
(`framework_timeout_millis`, `framework_bail_on_fail`, `framework_filter`…).

**Cómo se ejecuta** (wiki oficial, página *Running The Project*):

```sh
python launcher.py igorRunTests --config-file '<ruta a tu config.json>'
```

El fichero de configuración lleva `access-key`, `user-folder`, `runners` (`"vm,yyc"`),
`targets` (`"windows|Local"`), el `feed` RSS del runtime, `project-path` y `Logger.level`.

> ⚠️ **Su lanzador oficial es solo Windows x64** y pide una *access key* de tu cuenta de
> GameMaker (dice la wiki, página *Running The Project*, consultada el 6 de septiembre de
> 2026). En macOS y Linux puedes abrir `projects/xUnit/xUnit.yyp` y ejecutarlo desde el IDE o
> con `gm-cli run`, pero la automatización en Python está pensada para Windows. Si tu CI no
> es Windows, o usas el mini-framework de §3, o miras a crispy.

**Para qué te sirve de verdad, aunque no lo adoptes:** es la mejor colección pública de casos
límite del motor. Antes de discutir si algo es un bug tuyo o del runtime, busca la función en
`projects/xUnit/scripts/Basic*TestSuite/` y mira qué comportamiento da por bueno YoYo.

### 4.2 crispy — el de la comunidad, xUnit clásico

`crispy` v1.9.0 (MIT) es un framework unitario **escrito íntegramente en GML** para LTS 2022+.
Se instala como paquete local (`.yymps`) desde *Tools → Import Local Package*.

Su jerarquía es la de siempre: `TestRunner` → `TestSuite` → `TestCase`, todos heredando de
`BaseTestClass`. Las aserciones (leídas de `scripts/TestCase/TestCase.gml`) son:

| Aserción | Qué comprueba |
|---|---|
| `assertEqual(a, b, msg)` / `assertNotEqual` | Igualdad |
| `assertTrue(expr, msg)` / `assertFalse` | Verdad |
| `assertIsNoone` / `assertIsNotNoone` | `noone` |
| `assertIsUndefined` / `assertIsNotUndefined` | `undefined` |
| `assertRaises(fn, msg)` | Que la función lance |
| `assertRaiseErrorValue(fn, valor, msg)` | Que lance **ese** error concreto |
| `assertDoesNotThrow(fn, msg)` | Que **no** lance |

Lo que lo hace cómodo es el **descubrimiento automático por prefijo**: escribes funciones
sueltas que empiezan por un patrón y `discover()` las recoge sin que las registres una a una.
Así está montado su proyecto de ejemplo (`objects/obj_test/Create_0.gml`, literal):

```gml
// Create TestRunner
runner = new TestRunner("runner");

hamburger_suite = new TestSuite("hamburger_suite");
// Set up hamburger for tests
hamburger_suite.setUp(function() {
	var _ingredients = [new Ingredient("bun"), new Ingredient("patty"), new Ingredient("bun")];
	hamburger = new Food("hamburger", _ingredients);
});
runner.addTestSuite(hamburger_suite);
// Discovering hamburger tests
runner.discover(hamburger_suite, "test_hamburger_");
```

Y las pruebas son funciones globales con ese prefijo (`scripts/food_tests`, literal):

```gml
function test_food_raise_error_value_when_passing_number_to_name() {
	assertRaiseErrorValue(function() {
		var _ = new Food(12, []);
	}, "Food \"_name\" expected a string, received number.");
}
```

`runner.output` es un método que puedes redefinir: en el ejemplo escribe a la ventana de
Output **y** a una `ds_list` que se dibuja en pantalla. Es el gancho que necesitas para
volcar los resultados a un fichero y que los lea CI.

### 4.3 Cuál elegir

| Situación | Qué usar |
|---|---|
| Empiezas hoy, quieres pruebas esta tarde | El mini-framework de §3. 100 líneas, cero dependencias |
| Quieres `setUp`/`tearDown`, descubrimiento y aserciones ricas | **crispy** |
| Quieres demostrar un bug del motor ante YoYo | **GM-TestFramework** (aporta la suite al repo) |
| Necesitas medir cuánto tarda un trozo de código | **GMBenchmark** (§6) |
| Ya usas el ecosistema Bscotch (Stitch) | **olympus** + **ganary** para regresión |

---

## 5 · Regresión, *golden files* y determinismo

### 5.1 La idea del *golden file*

Hay resultados que son largos y aburridos de escribir a mano: el mapa que genera tu algoritmo,
el árbol de diálogo parseado, la tabla de balance completa. Para esos, la prueba no compara
contra un valor escrito por ti, sino contra **una salida anterior que diste por buena** y que
está guardada en disco. Se llama *golden file* o *snapshot*.

El ciclo es: la primera vez **se acepta y se guarda**; a partir de ahí, cualquier diferencia
es una regresión que tienes que justificar. Si el cambio es intencionado, borras el fichero
dorado y se regenera.

```gml
// ═══════════ scr_pruebas_dorado ═══════════

/// @desc Compara un valor con su copia dorada. Si no existe, la crea y la prueba pasa.
/// @param {String} _nombre  Identificador estable. Será el nombre del fichero.
/// @param {Any}    _valor   Cualquier cosa serializable a JSON.
/// @returns {Bool}
function afirmar_dorado(_nombre, _valor)
{
    var _ruta   = $"dorado_{_nombre}.json";
    var _actual = json_stringify(_valor, true);

    if (!file_exists(_ruta))
    {
        var _f = file_text_open_write(_ruta);
        file_text_write_string(_f, _actual);
        file_text_close(_f);
        show_debug_message($"          [dorado creado] {_ruta} — revísalo y súbelo al repo");
        return true;
    }

    var _g = file_text_open_read(_ruta);
    var _esperado = "";
    while (!file_text_eof(_g)) { _esperado += file_text_readln(_g); }
    file_text_close(_g);

    // readln devuelve la línea sin el salto: normalizamos ambos lados antes de comparar
    if (string_replace_all(_actual, "\n", "") == string_replace_all(_esperado, "\n", ""))
    {
        return afirmar_cierto(true);
    }

    pruebas_anotar_fallo($"el dorado '{_nombre}' ha cambiado. Borra {_ruta} si el cambio es intencionado");
    return afirmar_cierto(false);
}
```

> ⚠️ Los ficheros dorados se escriben en el **directorio de guardado del juego**
> (`game_save_id`), no en la carpeta del proyecto: hay que copiarlos al repositorio a mano la
> primera vez. Y **súbelos a Git**: un dorado que no está versionado no detecta nada.

### 5.2 Guardar y cargar: la prueba de ida y vuelta

El bug de guardado es el peor de todos, porque destruye horas de partida ajena y aparece
semanas después. La prueba es sencilla y hay que tenerla **desde el primer día**:

```gml
/// @desc Ida y vuelta: serializar → deserializar → comparar. Si no coincide, hay pérdida.
function pruebas_de_guardado()
{
    probar("el guardado sobrevive a un ciclo completo", function()
    {
        var _original = {
            version:  3,
            nombre:   "Adrián",
            vida:     87.5,
            posicion: [320, 240],
            mochila:  ["pocion", "llave_oxidada"],
            banderas: { jefe_1: true, tutorial: false }
        };

        var _texto  = json_stringify(_original);
        var _vuelta = json_parse(_texto);

        afirmar_igual(_vuelta.version,  _original.version);
        afirmar_igual(_vuelta.nombre,   _original.nombre);
        afirmar_igual(_vuelta.vida,     _original.vida);
        afirmar_igual(_vuelta.posicion, _original.posicion);   // arrays: por contenido
        afirmar_igual(_vuelta.mochila,  _original.mochila);
        afirmar_cierto(_vuelta.banderas.jefe_1);
        afirmar_cierto(!_vuelta.banderas.tutorial);
    });

    probar("una partida de una version vieja no revienta el cargador", function()
    {
        var _vieja = json_parse(@'{"version":1,"nombre":"antiguo"}');
        afirmar_cierto(is_struct(_vieja));
        afirmar_cierto(!struct_exists(_vieja, "mochila"), "la v1 no tenia mochila");
    });

    probar("un fichero corrupto no tumba el juego", function()
    {
        afirmar_lanza(function() { json_parse("{esto no es json"); });
    });
}

```

Los tres casos son los tres que fallan de verdad: el ciclo completo, **la partida guardada con
una versión anterior de tu juego** y el fichero corrupto. Ejecutados junto a los de §3.2 en el
proyecto de prueba:

```
  ok    el guardado sobrevive a un ciclo completo  (0.12 ms)
  ok    una partida de una version vieja no revienta el cargador  (0.00 ms)
  ok    un fichero corrupto no tumba el juego  (0.09 ms)
8 pruebas | 15 aserciones | 0 fallidas | 0.6 ms
RESULTADO: OK
```
 El detalle del guardado seguro
(escribir a temporal, validar, reemplazar) está en
[`01 · 14 — Persistencia y archivos`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md)
y en [`05 · 04`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) §7.

### 5.3 Determinismo: la generación procedural con semilla

Una mazmorra generada aleatoriamente es intestable… salvo que fijes la semilla. Con la fuente
inyectable de §2.2, una semilla concreta produce **siempre** el mismo nivel, y eso convierte
la generación en algo que puedes afirmar:

```gml
function pruebas_de_generacion()
{
    probar("la misma semilla produce el mismo nivel", function()
    {
        var _a = generar_mazmorra(new AzarReproducible(1234), 40, 30);
        var _b = generar_mazmorra(new AzarReproducible(1234), 40, 30);
        afirmar_igual(json_stringify(_a), json_stringify(_b));
    });

    probar("toda sala generada es alcanzable", function()
    {
        // Invariante: da igual la semilla, esto no puede fallar nunca
        for (var _s = 0; _s < 50; _s++)
        {
            var _m = generar_mazmorra(new AzarReproducible(_s), 40, 30);
            afirmar_cierto(salas_alcanzables(_m) == array_length(_m.salas),
                           $"semilla {_s}: hay salas aisladas");
        }
    });
}
```

La segunda es la más valiosa y se llama **prueba de invariante**: no dice qué mapa esperas,
dice **qué no puede pasar nunca**, y lo comprueba contra cincuenta mapas distintos. Cuando
falla, la propia prueba te da la semilla exacta para reproducirlo.

> Los algoritmos de generación están en
> [`04 · 05 — Roguelike y generación procedural`](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md)
> y el diseño de la generación, en [`13 · 07 — Generación procedural avanzada`](07%20-%20Generaci%C3%B3n%20procedural%20avanzada.md).

---

## 6 · Pruebas de rendimiento

### 6.1 Medir con `get_timer()`

`get_timer()` devuelve microsegundos desde el arranque del juego. Es lo único que necesitas
para un micro-benchmark honesto:

```gml
/// @desc Mide una función repitiéndola. Devuelve microsegundos por iteración.
/// @param {String}   _nombre
/// @param {Function} _cuerpo        Recibe el número de iteraciones.
/// @param {Real}     _iteraciones
/// @returns {Real}
function medir(_nombre, _cuerpo, _iteraciones = 100000)
{
    _cuerpo(1000);                      // calentamiento: descarta el primer coste
    var _t0 = get_timer();
    _cuerpo(_iteraciones);
    var _us = (get_timer() - _t0) / _iteraciones;
    show_debug_message($"  {_nombre}: {string_format(_us, 1, 4)} us/iter  ({_iteraciones} iter)");
    return _us;
}
```

Tres reglas para que el número signifique algo: **calienta antes de medir** (la primera pasada
paga cachés y asignaciones), **repite lo suficiente** (medir una sola llamada mide el ruido del
sistema operativo) y **compara dos alternativas en la misma tanda** — el número absoluto no es
comparable entre máquinas, la relación entre dos versiones sí.

### 6.2 GMBenchmark, cuando quieres comparar en serio

[GMBenchmark](https://github.com/DragoniteSpam/GMBenchmark) (DragoniteSpam, MIT, ★34) hace eso
mismo con interfaz, gráficas y agrupación por temas. Está descargado en
`11 - Código descargado/librerias/depuracion/GMBenchmark`. Su API, leída de su `readme.md`:

```gml
// Un Benchmark agrupa TestCase. Cada TestCase recibe el número de iteraciones.
var _benchmarks = [
    new Benchmark("Variable access", [
        new TestCase("dot operator", function(iterations) {
            var struct = { x: 0 };
            repeat (iterations) { var val = struct.x; }
        }),
        new TestCase("struct accessor", function(iterations) {
            var struct = { x: 0 };
            repeat (iterations) { var val = struct[$ "x"]; }
        })
    ]),
    // …y así con cada alternativa que quieras comparar
];
```

`TestCase` admite además una función `init` opcional, que se ejecuta antes y **no cuenta** en
el tiempo — para preparar el array de un millón de elementos sin contaminar la medida.

### 6.3 El presupuesto por frame

A 60 FPS cada frame dura **16,67 ms**. Ese es el presupuesto total, y lo reparten el Step, el
Draw, el recolector de basura, la entrada y el sistema operativo. Un reparto razonable para
un juego 2D:

| Partida | Presupuesto orientativo |
|---|---|
| Lógica (Step de todas las instancias) | ≤ 4 ms |
| Dibujado (Draw + Draw GUI) | ≤ 8 ms |
| Recolector de basura | ≤ 1 ms (`gc_target_frame_time`) |
| Margen para el sistema | el resto |

Convertirlo en una prueba automática es fácil, y es la que más disgustos evita:

```gml
probar("generar un nivel entero cabe en un frame", function()
{
    var _t0 = get_timer();
    generar_mazmorra(new AzarReproducible(7), 80, 60);
    var _ms = (get_timer() - _t0) / 1000;
    afirmar_cierto(_ms < 16, $"la generacion tardo {string_format(_ms, 1, 2)} ms");
});
```

> ⚠️ Un presupuesto en una prueba es **un aviso, no un dogma**: en CI la máquina puede ir
> cargada. Ponlo generoso (2× o 3× de lo que mides en tu máquina) y trátalo como detector de
> regresiones gordas, no de milisegundos.

### 6.4 Mide en YYC, no en VM

`gm-cli run` y `gm-cli compile` usan **VM por defecto** (`--runtime vm`). El código compilado
nativo (`--runtime native`, el YYC) puede ir **de 2 a 3 veces más rápido en lógica**, y los
cuellos de botella no están en el mismo sitio en los dos.

```sh
gm-cli compile --runtime vm       # desarrollo: compila rápido
gm-cli compile --runtime native   # medición y release: YYC
```

`code_is_compiled()` te dice en tiempo de ejecución en cuál estás. **Toda medición que vayas a
usar para decidir una optimización tiene que hacerse en `native`**, o estarás optimizando un
intérprete que no vas a distribuir. El análisis completo (Debug Overlay, ventana FPS con
*Stacked*, texture swaps, GC) está en
[`01 · 15 — Depuración y rendimiento`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md) §6.

---

## 7 · Depuración reproducible

Un bug que no sabes reproducir no está arreglado: está escondido. Estas cuatro herramientas
convierten «me pasó una vez» en «pasa siempre».

### 7.1 Grabar y reproducir la entrada

El motor graba la entrada del jugador y la reproduce después. Es la forma más directa de
capturar un bug de secuencia:

```gml
// Empezar a grabar (teclado + ratón)
debug_input_record(debug_input_filter_keyboard | debug_input_filter_mouse);

// ...jugar hasta que el bug ocurra...

// Guardar lo grabado
debug_input_save("bug_0042.data");

// En otra sesión: reproducirlo exactamente
debug_input_playback("bug_0042.data");
```

Las tres constantes del filtro son `debug_input_filter_keyboard`, `debug_input_filter_mouse` y
`debug_input_filter_touch`, y se combinan con `|`.

Del manual, tres cosas que conviene saber: durante la reproducción **la entrada real queda
bloqueada por tipo** (si grabaste solo teclado, el ratón sigue respondiendo); al terminar se
dispara el evento **Async System** con `async_load[? "event_type"] == "debug_input_playback_stopped"`,
que es donde comparas el estado final con el esperado; y ⚠️ **son funciones de depuración: no
las dejes en el juego final.**

Un archivo de entrada grabado convierte un bug en una prueba de regresión de verdad: lo
adjuntas al informe, lo metes en el repositorio, y cualquiera lo reproduce en 10 segundos.
El contexto del Debugger del IDE está en
[`01 · 15`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md) §3.

### 7.2 Un log con niveles que sobrevive al cierre

`show_debug_message()` desaparece cuando se cierra el juego. Para un tester que no está a tu
lado, el log tiene que estar en un fichero.

```gml
// ═══════════ scr_registro ═══════════
enum NIVEL { DEPURAR, INFO, AVISO, ERROR }

#macro NIVEL_MINIMO NIVEL.INFO
#macro NIVEL_MINIMO_Release NIVEL.AVISO

/// @desc Escribe una entrada de log a Output y a disco. Barata si el nivel no llega.
/// @param {Real}   _nivel   Constante del enum NIVEL.
/// @param {String} _texto
function registrar(_nivel, _texto)
{
    if (_nivel < NIVEL_MINIMO) { exit; }

    static etiquetas = ["DEPURAR", "INFO", "AVISO", "ERROR"];

    var _d = date_current_datetime();
    var _hora  = $"{date_get_hour(_d)}:{date_get_minute(_d)}:{date_get_second(_d)}";
    var _linea = $"[{_hora}] [{etiquetas[_nivel]}] {_texto}";

    show_debug_message(_linea);

    var _f = file_text_open_append("partida.log");
    file_text_write_string(_f, _linea);
    file_text_writeln(_f);
    file_text_close(_f);
}
```

Dos claves: **`#macro NIVEL_MINIMO_Release`** aprovecha que GameMaker redefine un macro *por
configuración* añadiendo `_NombreDeLaConfig` al nombre —compilando con `--config Release`,
`NIVEL_MINIMO` pasa a `NIVEL.AVISO` sin tocar código—; y ⚠️ **abrir y cerrar el fichero en cada
línea es lento**: vale para avisos y errores, pero si registras cada frame, acumula en un array
y vuelca cada N segundos.

#### A dónde va cada nivel

`registrar()` tiene tres destinos posibles y no todos los niveles llegan a los tres. La Config
activa decide **si** un nivel se procesa (vía `NIVEL_MINIMO`); una vez procesado, el nivel decide
**cuándo** se escribe a disco:

| Nivel | Output del IDE | `partida.log` | Pantalla (consola, §7.5) |
|---|---|---|---|
| `DEPURAR` (traza) | Sí, si pasa `NIVEL_MINIMO` | Sí, en el buffer — se pierde si el juego crashea antes del siguiente volcado | Sí, si la consola está abierta |
| `INFO` | Sí | Sí, en el buffer | Sí |
| `AVISO` | Sí | Sí, **volcado inmediato** | Sí |
| `ERROR` | Sí | Sí, **volcado inmediato** + candidato a `capturar_incidencia()` (§7.3) | Sí, en otro color |

En `Default`/`Debug`, `NIVEL_MINIMO` deja pasar `DEPURAR`; en `Release`,
`NIVEL_MINIMO_Release = NIVEL.AVISO` corta `DEPURAR` e `INFO` en el propio `exit;` de la primera
línea de la función — ni se calcula la fecha ni se toca el disco.

#### Sin castigar el frame: el mismo `registrar()`, con buffer

Abrir y cerrar el fichero en cada llamada es barato si registras un evento suelto (el jugador
guarda, cambia de nivel). Dentro de un bucle caliente —una traza por colisión, por paso de la IA,
por partícula de una simulación a mano (`13 · 08`)— ese `file_text_open_append` de cada línea sí
se nota en el frame. La versión con buffer solo abre el fichero cuando de verdad toca volcar:

```gml
// ═══════════ scr_registro (ampliación: buffer sin coste por frame) ═══════════
global.registro_buffer         = [];
global.registro_ultimo_volcado = current_time;

#macro REGISTRO_INTERVALO_VOLCADO_MS 2000   // cada cuánto se escribe a disco, como mucho

/// @desc Como registrar(), pero acumula en memoria en vez de abrir el fichero en cada
///       llamada. AVISO y ERROR fuerzan un volcado inmediato: un error que no llega a
///       verse en disco si el juego crashea a continuación no sirve de nada.
/// @param {Real}   _nivel   Constante del enum NIVEL.
/// @param {String} _texto
function registrar_bufer(_nivel, _texto)
{
    if (_nivel < NIVEL_MINIMO) { exit; }

    static etiquetas = ["DEPURAR", "INFO", "AVISO", "ERROR"];

    var _d     = date_current_datetime();
    var _hora  = $"{date_get_hour(_d)}:{date_get_minute(_d)}:{date_get_second(_d)}";
    var _linea = $"[{_hora}] [{etiquetas[_nivel]}] {_texto}";

    show_debug_message(_linea);
    array_push(global.registro_buffer, _linea);

    // La consola en pantalla (§7.5) lee de aquí, no del fichero.
    if (variable_global_exists("consola_historial_visible"))
    {
        array_push(global.consola_historial_visible, _linea);
    }

    var _urgente = (_nivel >= NIVEL.AVISO);
    var _lleno   = (array_length(global.registro_buffer) >= 50);
    var _toca    = (current_time - global.registro_ultimo_volcado >= REGISTRO_INTERVALO_VOLCADO_MS);

    if (_urgente || _lleno || _toca) { registro_volcar(); }
}

/// @desc Escribe de una sola vez todo lo acumulado en el buffer. Ábrelo tú también al
///       cerrar el juego (Game End) para no perder la cola sin volcar.
function registro_volcar()
{
    if (array_length(global.registro_buffer) == 0) { exit; }

    var _f = file_text_open_append("partida.log");
    for (var _i = 0; _i < array_length(global.registro_buffer); _i++)
    {
        file_text_write_string(_f, global.registro_buffer[_i]);
        file_text_writeln(_f);
    }
    file_text_close(_f);

    global.registro_buffer         = [];
    global.registro_ultimo_volcado = current_time;
}
```

> ⚠️ **Nunca escribas el log —ni ningún archivo propio— con `working_directory` delante de la
> ruta.** `working_directory` apunta al **file bundle**, la parte del juego empaquetada con el
> ejecutable, y es **de solo lectura en la build exportada**
> ([`01 · 14` §1](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#1-el-sandbox-lo-primero-que-debes-entender)):
> escribir ahí falla en silencio o lanza una excepción según la plataforma. La regla es la misma
> que ya usan `registrar()`/`registro_volcar()` arriba: pásale a `file_text_open_append()` un
> nombre de fichero **relativo, sin ruta delante** (`"partida.log"`), y dejar que GameMaker
> resuelva sola al **save area** (`01 · 14` §1, tabla de resolución de lectura/escritura). Esto
> se aprende bien en el IDE, donde el *Run* del proyecto es más permisivo, y se descubre mal en
> el paquete final —justo el caso que ya avisa `05 · 04` §8 sobre probar el build empaquetado y
> no solo el Run.

Combínalo con `exception_unhandled_handler()` para tener también los cierres inesperados: el
patrón completo, con `debug_get_callstack()`, está en
[`01 · 15`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md) §3 y §9. **No lo repito.**

### 7.3 Capturas automáticas

`screen_save(nombre)` guarda la pantalla en PNG dentro del directorio de guardado. Dispararlo
solo cuando algo va mal te da pruebas gráficas sin llenar el disco:

```gml
/// @desc Guarda una captura con marca de tiempo. Devuelve el nombre del fichero.
function capturar_incidencia(_motivo)
{
    var _d = date_current_datetime();
    var _n = $"incidencia_{_motivo}_{date_get_hour(_d)}{date_get_minute(_d)}{date_get_second(_d)}.png";
    screen_save(_n);
    registrar(NIVEL.AVISO, $"captura guardada: {_n}");
    return _n;
}
```

Buenos momentos para dispararlo: cuando los FPS bajan de un umbral varios segundos seguidos,
cuando el jugador muere en el mismo sitio por tercera vez, cuando una aserción de producción
falla, y —siempre— con la tecla de «reportar bug» del modo QA.

> ⚠️ **En Mac, el PNG que produce `screen_save()` puede salir invertido verticalmente aunque la
> ventana real se vea bien** (Trampa 13 de
> [`12 · 09` §0](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-13--screen_save-invirtió-la-imagen-una-vez--y-hoy-ya-no-no-la-voltees)).
> No afecta a si algo aparece o no, solo a si arriba/abajo en el PNG es arriba/abajo de verdad
> — relevante para §8.6 y el guion de humo de §8.7.

### 7.4 El modo QA: teclas ocultas que no llegan al jugador

Un tester necesita saltarse el nivel 3 para probar el 4. La forma correcta de dárselo es una
puerta cerrada con un macro de configuración:

```gml
// ═══════════ scr_modo_qa ═══════════
#macro MODO_QA          true      // desarrollo
#macro Release:MODO_QA  false     // sintaxis de macro por CONFIGURACIÓN (13 · 06 §3.12):
                                   // "Release" es el nombre de la Config, no un macro nuevo.
                                   // #macro MODO_QA_Release (con guion bajo) NO haría nada:
                                   // sería un macro suelto sin relación con MODO_QA.

/// @desc Atajos de QA. Llámalo desde el Step del controlador. En Release no compila nada.
function modo_qa_paso()
{
    if (!MODO_QA) { exit; }

    // F1 — invulnerabilidad
    if (keyboard_check_pressed(vk_f1) && instance_exists(obj_jugador))
    {
        obj_jugador.invulnerable = !obj_jugador.invulnerable;
        registrar(NIVEL.INFO, $"QA: invulnerable = {obj_jugador.invulnerable}");
    }

    // F2 — teletransporte al cursor
    if (keyboard_check_pressed(vk_f2) && instance_exists(obj_jugador))
    {
        with (obj_jugador) { x = mouse_x; y = mouse_y; }
        registrar(NIVEL.INFO, $"QA: teletransporte a ({mouse_x}, {mouse_y})");
    }

    // F3 — saltar al siguiente nivel
    if (keyboard_check_pressed(vk_f3))
    {
        registrar(NIVEL.INFO, $"QA: salto de nivel desde {room_get_name(room)}");
        room_goto_next();
    }

    // F4 — captura + log marcado, para adjuntar al informe de bug
    if (keyboard_check_pressed(vk_f4)) { capturar_incidencia("tester"); }

    // F5 — reiniciar la room sin perder el estado global
    if (keyboard_check_pressed(vk_f5)) { room_restart(); }
}
```

> 💡 `MODO_QA` como macro y no como variable **no es un detalle de estilo**: un `if (false)`
> con un macro constante lo elimina el compilador, así que en el build de tienda ese código
> ni existe. Con una variable global, seguiría ahí y alguien acabaría encontrándolo.
>
> ⚠️ Comprueba la lista de teclas antes de publicar. Más de un juego ha salido a la venta con
> el «matar a todos los enemigos» todavía en F9.

### 7.5 Una consola de comandos en runtime

El modo QA de §7.4 da atajos de **una tecla**: rápidos, pero fijos y sin parámetros. Una consola
de **texto** resuelve lo que una tecla no puede — `tp 480 260`, `nivel rm_jefe_final`,
`spawn obj_enemigo_arquero 5` — sin recompilar ni añadir una tecla nueva por cada comando futuro.
Es el mismo principio que ya usan casi todos los motores (Source, Quake, Unreal): un intérprete
de línea de comandos mínimo, vivo dentro del propio juego.

#### El contrato: qué guarda cada comando

Un comando es un **struct** con una función y su ayuda, guardado en un registro global por
nombre. Nada de `switch` gigante: dar de alta un comando nuevo es una llamada, no tocar una
función central que crece sin límite.

```gml
// ═══════════ scr_consola ═══════════

/// @desc Registro global de comandos: nombre → { funcion, ayuda }. Llamar una sola vez,
///       antes de registrar el primer comando (el Create de obj_consola, más abajo).
function consola_iniciar()
{
    if (variable_global_exists("consola_comandos")) { exit; }   // ya iniciada
    global.consola_comandos          = {};
    global.consola_historial_visible = [];   // sink en pantalla; lo alimenta registrar_bufer() (§7.2)
}

/// @func consola_registrar(_nombre, _funcion, _ayuda)
/// @desc Da de alta un comando. _funcion recibe un único argumento: un array de strings
///       con los tokens que siguen al nombre del comando (puede estar vacío).
/// @param {String}   _nombre
/// @param {Function} _funcion
/// @param {String}   _ayuda
function consola_registrar(_nombre, _funcion, _ayuda)
{
    variable_struct_set(global.consola_comandos, string_lower(_nombre), {
        funcion: _funcion,
        ayuda:   _ayuda
    });
}
```

#### Parsear la línea: `string_split` + `string_trim`, respetando comillas

`string_split(_texto, " ", true)` trocea por espacios de sobra, pero rompe un argumento como
`decir "hola mundo"` en tres tokens. La solución no es reescribir un parser completo: es trocear
con `string_split` como siempre y **recomponer** los tokens que quedan entre comillas.

```gml
/// @func consola_tokenizar(_texto)
/// @desc Trocea una línea de comandos en tokens, respetando comillas dobles para
///       argumentos con espacios (`decir "hola mundo"` → ["decir", "hola mundo"]).
/// @param {String} _texto
/// @returns {Array<String>}
function consola_tokenizar(_texto)
{
    var _crudo         = string_split(string_trim(_texto), " ", true);
    var _tokens         = [];
    var _dentroComillas = false;
    var _actual          = "";

    for (var _i = 0; _i < array_length(_crudo); _i++)
    {
        var _t = _crudo[_i];

        if (!_dentroComillas && string_char_at(_t, 1) == "\"")
        {
            var _cierraAqui = (string_length(_t) > 1
                && string_char_at(_t, string_length(_t)) == "\"");

            if (_cierraAqui)
            {
                array_push(_tokens, string_copy(_t, 2, string_length(_t) - 2));
            }
            else
            {
                _dentroComillas = true;
                _actual          = string_copy(_t, 2, string_length(_t) - 1);
            }
        }
        else if (_dentroComillas)
        {
            if (string_char_at(_t, string_length(_t)) == "\"")
            {
                _actual         += " " + string_copy(_t, 1, string_length(_t) - 1);
                array_push(_tokens, _actual);
                _dentroComillas = false;
                _actual          = "";
            }
            else
            {
                _actual += " " + _t;
            }
        }
        else
        {
            array_push(_tokens, _t);
        }
    }

    if (_dentroComillas) { array_push(_tokens, _actual); }   // comilla sin cerrar: mejor esto que perder el comando

    return _tokens;
}

/// @func consola_ejecutar(_linea)
/// @desc Parsea una línea completa y ejecuta el comando que corresponda. No hace nada
///       con una línea vacía; avisa por el log (§7.2) si el comando no existe.
/// @param {String} _linea
function consola_ejecutar(_linea)
{
    var _tokens = consola_tokenizar(_linea);
    if (array_length(_tokens) == 0) { exit; }

    var _nombre = string_lower(_tokens[0]);
    array_delete(_tokens, 0, 1);   // lo que queda son los argumentos, ya sin el nombre

    registrar_bufer(NIVEL.INFO, $"> {_linea}");

    if (!variable_struct_exists(global.consola_comandos, _nombre))
    {
        registrar_bufer(NIVEL.AVISO, $"comando desconocido: «{_nombre}». Escribe «ayuda».");
        exit;
    }

    var _comando = variable_struct_get(global.consola_comandos, _nombre);
    _comando.funcion(_tokens);
}
```

`consola_ejecutar()` vuelca cada línea escrita y cada resultado a **la misma capa de log** de
§7.2 (`registrar_bufer()`): la consola no es un sistema aparte, es una entrada de texto sobre el
log que ya existe. Eso también significa que lo que se teclea en la consola queda en
`partida.log`, lo que convierte un informe de bug de un tester en «mira, hice esto en este
orden» en vez de «no sé qué pulsé».

#### El objeto controlador: entrada, historial y autocompletado

```gml
// ═══════════ obj_consola — Create ═══════════
#macro TECLA_CONSOLA vk_f12   // cámbiala si tu plataforma usa F12 para otra cosa

consola_iniciar();

abierta           = false;
historial_comandos = [];      // strings, el más reciente al final
historial_indice   = -1;      // -1 = no se está navegando el historial
sugerencias         = [];

// ── Comandos de ejemplo: el patrón se repite para cada comando nuevo ──
consola_registrar("ayuda", function(_args)
{
    var _nombres = variable_struct_get_names(global.consola_comandos);
    array_sort(_nombres, true);
    for (var _i = 0; _i < array_length(_nombres); _i++)
    {
        var _cmd = variable_struct_get(global.consola_comandos, _nombres[_i]);
        registrar_bufer(NIVEL.INFO, $"  {_nombres[_i]} — {_cmd.ayuda}");
    }
}, "Lista todos los comandos disponibles");

consola_registrar("dios", function(_args)
{
    if (!instance_exists(obj_jugador)) { exit; }
    obj_jugador.invulnerable = !obj_jugador.invulnerable;
    registrar_bufer(NIVEL.INFO, $"invulnerable = {obj_jugador.invulnerable}");
}, "Activa o desactiva la invulnerabilidad del jugador");

consola_registrar("tp", function(_args)
{
    if (array_length(_args) < 2) { registrar_bufer(NIVEL.AVISO, "uso: tp <x> <y>"); exit; }
    if (!instance_exists(obj_jugador)) { exit; }
    obj_jugador.x = real(_args[0]);
    obj_jugador.y = real(_args[1]);
    registrar_bufer(NIVEL.INFO, $"teletransportado a ({_args[0]}, {_args[1]})");
}, "Teletransporta al jugador: tp <x> <y>");

consola_registrar("nivel", function(_args)
{
    if (array_length(_args) < 1) { registrar_bufer(NIVEL.AVISO, "uso: nivel <room>"); exit; }
    if (asset_get_type(_args[0]) != asset_room)
    {
        registrar_bufer(NIVEL.ERROR, $"no existe la room «{_args[0]}»");
        exit;
    }
    room_goto(asset_get_index(_args[0]));
}, "Cambia de room: nivel <nombre_room>");
```

```gml
// ═══════════ obj_consola — Step ═══════════
if (!MODO_QA) { exit; }   // en Release, Release:MODO_QA vale false: el compilador borra todo esto

if (keyboard_check_pressed(TECLA_CONSOLA))
{
    abierta            = !abierta;
    keyboard_string     = "";
    sugerencias          = [];
    historial_indice     = -1;
}

if (!abierta) { exit; }

// Historial: ↑ retrocede, ↓ avanza. historial_indice cuenta desde el final del array.
if (keyboard_check_pressed(vk_up) && historial_indice < array_length(historial_comandos) - 1)
{
    historial_indice++;
    keyboard_string = historial_comandos[array_length(historial_comandos) - 1 - historial_indice];
}
if (keyboard_check_pressed(vk_down))
{
    if (historial_indice > 0)
    {
        historial_indice--;
        keyboard_string = historial_comandos[array_length(historial_comandos) - 1 - historial_indice];
    }
    else if (historial_indice == 0)
    {
        historial_indice = -1;
        keyboard_string   = "";
    }
}

if (keyboard_check_pressed(vk_tab)) { consola_autocompletar(); }

if (keyboard_check_pressed(vk_enter) && string_length(string_trim(keyboard_string)) > 0)
{
    array_push(historial_comandos, keyboard_string);
    consola_ejecutar(keyboard_string);
    keyboard_string    = "";
    sugerencias         = [];
    historial_indice    = -1;
}

if (keyboard_check_pressed(vk_escape)) { abierta = false; }
```

```gml
/// @func consola_autocompletar()
/// @desc Si lo escrito es el principio de un único comando, lo completa. Si hay varias
///       coincidencias, las deja en la variable de instancia `sugerencias` sin tocar
///       keyboard_string. Se llama desde el Step de obj_consola, con self ya puesto.
function consola_autocompletar()
{
    var _prefijo   = string_lower(keyboard_string);
    var _nombres   = variable_struct_get_names(global.consola_comandos);
    var _coinciden = [];

    for (var _i = 0; _i < array_length(_nombres); _i++)
    {
        if (string_pos(_prefijo, string_lower(_nombres[_i])) == 1)
        {
            array_push(_coinciden, _nombres[_i]);
        }
    }

    if (array_length(_coinciden) == 1)
    {
        keyboard_string = _coinciden[0] + " ";
    }
    else if (array_length(_coinciden) > 1)
    {
        array_sort(_coinciden, true);
        sugerencias = _coinciden;
    }
}
```

```gml
// ═══════════ obj_consola — Draw GUI ═══════════
if (!MODO_QA || !abierta) { exit; }

var _ancho      = display_get_gui_width();
var _altoLinea  = 20;
var _lineasLog  = 10;

draw_set_alpha(0.85);
draw_set_colour(c_black);
draw_rectangle(0, 0, _ancho, _altoLinea * (_lineasLog + 2), false);
draw_set_alpha(1);

var _historial = global.consola_historial_visible;
var _primera   = max(0, array_length(_historial) - _lineasLog);
var _y         = 4;

draw_set_colour(c_white);
for (var _i = _primera; _i < array_length(_historial); _i++)
{
    draw_text(6, _y, _historial[_i]);
    _y += _altoLinea;
}

draw_set_colour(c_lime);
draw_text(6, _y, "> " + keyboard_string + (current_time div 500 % 2 == 0 ? "_" : ""));

if (array_length(sugerencias) > 0)
{
    draw_set_colour(c_yellow);
    draw_text(6, _y + _altoLinea, string_join_ext(" · ", sugerencias));
}

draw_set_colour(c_white);
```

`obj_consola` es un único objeto persistente creado una vez desde la room de arranque (§3.4 de
[`13 · 06`](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md)), igual que `obj_game`. No
necesita capturar el ratón ni bloquear el resto del juego: mientras `abierta` es `true`, deja que
el jugador se mueva por debajo — si no quieres eso, comprueba `obj_consola.abierta` en el Step de
`obj_jugador` y sal antes de leer el resto del input, el mismo patrón que ya usa el modo QA.

#### Cómo se desactiva en la build de release, para que no sea un agujero

La consola entera cuelga de `MODO_QA`, el mismo macro de §7.4 — no lo vuelvas a declarar aquí
(un `#macro` repetido no compila): `MODO_QA` y su sobrescritura `Release:MODO_QA` viven en un
único sitio, `scr_modo_qa`.

El primer `if (!MODO_QA) { exit; }` del Step **y** del Draw GUI hace que, compilando con
`--config Release`, el compilador elimine ese código por ser un `if (false)` sobre una constante
—la misma razón por la que §7.4 insiste en macro y no en variable global—. El objeto puede seguir
existiendo en la room de Release: su Step y su Draw GUI no hacen nada. Aun así:

- ⚠️ **No confíes solo en el macro para comandos peligrosos de verdad** (borrar el guardado,
  desbloquear todo el juego): un macro mal puesto en una Config nueva es un error humano. Si un
  comando puede hacer daño real, que además compruebe `DEV` (§3.12 de `13 · 06`) antes de actuar,
  no solo que exista dentro de `MODO_QA`.
- ⚠️ **Revisa la lista de comandos antes de publicar**, igual que la lista de teclas de §7.4 — un
  `dios` o un `nivel` sueltos no son el problema; un comando que dé objetos gratis sí lo es si
  alguien llega a activar `MODO_QA` por error en una build filtrada.
- El `TECLA_CONSOLA` (F12) no colisiona con el modo QA (F1-F5) ni con capturas de sistema
  operativo habituales, pero compruébalo en cada plataforma de destino.

#### Lo que ya existe y esta receta no repite

Tres piezas que un desarrollador suele esperar dentro de «herramientas de depuración en runtime»
**ya están escritas** en otro sitio de esta biblioteca — la consola de esta sección las
complementa, no las sustituye:

| Herramienta | Dónde ya está | Qué hace |
|---|---|---|
| **Inspector de entidades en vivo** | [`01 · 15` §4](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#vistas-de-depuración-personalizadas-muy-potente) | `dbg_slider`, `dbg_watch`, `dbg_checkbox` sobre `ref_create(instancia, "variable")`: ve **y edita** el estado de una instancia concreta mientras juegas, sin tocar código |
| **Gráfica de rendimiento en vivo** | [`01 · 15` §4](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md#la-ventana-fps-cómo-leerla) | La ventana **FPS** del Debug Overlay, en modo *Stacked*, desglosa GC/IO/Update/Draw fotograma a fotograma |
| **Capturas de pantalla e incidencias** | [`13 · 11` §4.7](11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md#47-captura-modo-foto-y-compartir) y §7.3 de este documento | `captura_tomar()`/`captura_tomar_recorte()`, sobre `screen_save()`/`screen_save_part(nombre, x, y, w, h)` — verificada en `buscar.py`, existe en el runtime `2026.0.0.23` |

Un comando de consola como `captura` que llame a `capturar_incidencia()` (§7.3) es la forma
natural de unir las dos piezas: teclear en vez de programar una tecla nueva cada vez.

---

## 8 · Compilar es la primera prueba

### 8.1 La puerta obligatoria

El [`CLAUDE.md`](../AGENTS.md) de esta biblioteca lo dice sin matices: **nada se da por
terminado sin compilar y reportar la salida real.**

```sh
gm-cli compile --errors-only
echo $?        # 0 = compila
```

`--errors-only` silencia todo menos los **errores de sintaxis GML**: si imprime algo por esa
vía, es un problema. Es justo lo que quieres en un *hook* de pre-commit, para iterar rápido
mientras escribes. En el proyecto de prueba de este documento salió con **código 0 y sin una
línea de salida**.

> ⚠️ **Pero `--errors-only` no es la puerta que certifica que un juego está listo — solo que
> compila.** Silencia también los `WARNING`, y al menos uno es un fallo real, no cosmético: un
> *included file* creado por `resourcetool` (un `.json` de datos, por ejemplo) cuyo `filePath`
> quedó vacío no llega al paquete compilado, y el único rastro es
> `WARNING :: datafile ... was NOT copied` — visible **solo** compilando sin el flag,
> reproducido con las dos compilaciones reales en
> [`12 · 09` §0 Trampa 8](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-8--resource-create-typeincludedfile-deja-filepath-fuera-de-datafiles-y---errors-only-no-lo-detecta).
> **La puerta obligatoria real, antes de cerrar cualquier tarea, es compilar dos veces**: una
> con `--errors-only` para el `exit 0` rápido, y **una sin el flag, leyendo la salida completa**
> — es la única que muestra estos avisos.

> ⚠️ Ojo con la asimetría: **`gm-cli compile` sí devuelve un código de salida útil; `gm-cli
> run` no** (§3.4). La puerta de compilación se puede automatizar con `$?`; la de pruebas hay
> que leerla de la salida.

### 8.2 Compilar para más de una plataforma

El error de compilación específico de una plataforma aparece cuando compilas esa plataforma, y
no antes. La matriz mínima para un juego de escritorio:

```sh
gm-cli compile --target windows --errors-only
gm-cli compile --target mac     --errors-only
gm-cli compile --target linux   --errors-only
```

Cada uno necesita su toolchain instalada; `gm-cli` descarga lo que puede. Qué targets soporta
hoy el CLI y cuáles no, en
[`05 · 02 — Publicar y exportar`](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md) §1.2.

### 8.3 HTML5: el que siempre rompe algo

Exportar a web es la prueba más barata de compartir con testers y, a la vez, la que más cosas
rompe, porque HTML5 no tiene todo lo que tiene el escritorio. Lo que se cae, y cómo se detecta:

| Qué falla en HTML5 | Cómo lo pruebas |
|---|---|
| **El Debug Overlay no existe** | Tu HUD de depuración tiene que ser propio |
| **El recolector de basura es el de JavaScript** | `gc_get_stats()` devuelve ceros; no midas ahí |
| `show_message`, `get_string`, `get_integer` | Se ignoran fuera de Windows: revisa que no los uses |
| Ficheros y rutas | Persistencia distinta: prueba guardar y recargar en el navegador |
| `game_end()` | Deja un lienzo en blanco: no lo llames en la versión web |

```sh
gm-cli package --target operagx -o build/juego-web.zip
```

Y ábrelo **en un servidor**, no con `file://`. Las trampas del export web están en
[`01 · 16 — Exportar y publicar`](../01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md).

### 8.4 `gm-cli package`: probar lo que se instala el jugador

```sh
gm-cli package --target mac --runtime native --config Release -o build/juego.zip
```

**El paquete no es el `Run` del IDE.** El runner del IDE perdona cosas que el ejecutable no:
rutas relativas, assets descartados por el compilador, permisos. La regla es sencilla y
figura ya en [`05 · 04`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) §8:
**prueba el build empaquetado antes de cada entrega, no solo el Run.**

### 8.5 Interpretar los errores: lo que el compilador SÍ detecta y lo que NO

Un error de sintaxis normal sale con el formato `gml_Object_<objeto>_<Evento>(<línea>) :
<mensaje>` (verificado rompiendo a propósito un `Create_0.gml` con `var _horizontal = ;`), y
`gm-cli compile` añade al final, además del texto con bordes `│`, un bloque JSON parseable:

```json
{"errors":[{"source":"AssetCompiler","message":"gml_Object_obj_x_Create_0(0) : unexpected symbol \";\" in expression"},{"source":"AssetCompiler","message":".../GMAssetCompiler.dll exited with non-zero status (1)"}]}
```

**🔴 Un `constructor` con padre no definido crashea el `AssetCompiler` entero, sin línea y sin
mensaje útil.** Este hallazgo vivía solo en `_indice/PENDIENTE-r3.md`, un documento de
seguimiento interno que un agente no visita en su flujo normal; queda promovido aquí y en
[`12 · 09` — Manual del agente de IA](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#73--el-crash-silencioso-un-constructor-con-padre-no-definido-tira-abajo-el-assetcompiler-entero),
que trae el detalle completo (reproducción, JSON de ese caso concreto y cómo reconocerlo antes
de sospechar de otra cosa):

```gml
// NO HAGAS ESTO: PadreQueNoExiste no está definido en ningún sitio del proyecto
function Hijo() : PadreQueNoExiste() constructor {
    valor = 1;
}
```

```
Command failed:
/…/runtime-2026.0.0.23/bin/assetcompiler/osx/arm64/GMAssetCompiler.dll exited with non-zero status (1)
```

Verificado en vivo el 7 de septiembre de 2026: el fallo se repite tres veces seguidas, sin
señalar archivo ni línea — es la trampa más difícil de localizar por descarte, porque nada en
el mensaje menciona `constructor` ni herencia.

**Otras trampas del motor**, encontradas por `validar-compilacion-docs.py` al compilar 3 501
bloques de GML de esta biblioteca contra el runtime real, y que también vivían solo en
`PENDIENTE-r3.md`:

| Trampa | Por qué falla |
|---|---|
| **GML no admite notación científica**: `1e10` | Se trocea en el literal `1` seguido del identificador `e10` |
| **El ternario anidado necesita paréntesis** | `a ? x : b ? y : z` falla; escribe `a ? x : (b ? y : z)` |
| **`const` no existe en GML** | Usa `#macro NOMBRE valor` |
| `skeleton_animation_set(animname, [loop])` no tiene argumento de *track* | No busques una firma con más argumentos por analogía con otros motores |
| `skeleton_animation_get_position` devuelve 0-1 normalizado | No son segundos |
| `keyboard_unset_map()` no acepta argumentos | Llamarla con un argumento es un error de sintaxis |

**Por qué esto hace que `validar-proyecto.py` no sea opcional**: GML resuelve los nombres de
función en tiempo de ejecución, así que llamar a una que no existe **no es un error de
compilación**. `funcion_que_no_existe(5, "hola")` compila con `exit 0` limpio y solo revienta al
ejecutar, con un mensaje que ni siquiera nombra el problema real:

```
Variable obj_x.funcion_que_no_existe(100003, -2147483648) not set before reading it.
```

Detalle completo del matiz — `validar-proyecto.py` solo hace fallar el comando (`exit 1`) para
funciones con prefijo de familia del runtime; un nombre de dominio sin prefijo con una errata
solo aparece en la categoría `desconocida`, y **solo con `--todo`** — en
[`12 · 09` §7.5](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#75-por-qué-validar-proyectopy-no-es-opcional--y-un-matiz-importante-sobre-lo-que-detecta-de-verdad).

### 8.6 Compilar limpio no es lo mismo que funcionar: el fallo silencioso de tiempo de ejecución

`gm-cli compile` con `exit 0` certifica **sintaxis**, no comportamiento. §8.5 ya lo dice para
funciones inventadas — pero hay una segunda clase de fallo, más difícil de sospechar porque ni
siquiera necesita una función mal escrita: código que compila limpio, que el propio catálogo de
esta biblioteca da por **verificado**, y que en tiempo de ejecución hace exactamente lo
contrario de lo que promete, sin ningún error visible.
[`_indice/auditorias/r5-prueba-e2e.md`](../_indice/auditorias/r5-prueba-e2e.md) documentó dos
casos reales construyendo un juego completo de punta a punta:

- Una fuente creada con `resourcetool` compila, el objeto que la usa compila, `gm-cli run` no
  imprime ningún error — y el juego entero se queda mudo, sin una sola letra en pantalla
  (Trampa 5 de [`12 · 09`](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-5--las-fuentes-creadas-por-resourcetool-compilan-limpio-y-no-dibujan-ni-una-letra)).
- `directory_exists()`/`directory_create()` devuelven `false` para cualquier ruta bajo `gm-cli
  run --target mac`, incluida la carpeta de guardado que ya existe — y `save_game()` falla en
  silencio, con la única pista una línea de log que hay que estar mirando a propósito
  (Trampa 6 de [`12 · 09`](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-6--directory_existsdirectory_create-devuelven-false-siempre-bajo-gm-cli-run---target-mac)).

Ninguno de los dos apareció en el compilador ni en `validar-proyecto.py`. La checklist de
[`12 · 09` §8](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#8--checklist-final-antes-de-dar-una-tarea-por-terminada),
seguida al pie de la letra, marcaba las siete casillas — incluida «ejecutaste el juego» — y aun
así el juego habría salido mudo y sin guardado. La lección no es «prueba más»: es que **dos
comprobaciones concretas, no genéricas, habrían cazado ambos bugs**, y ningún checklist de esta
biblioteca las pedía hasta ahora (§12 ya las incorpora). Ejecútalas como **procedimiento**, no
como buena intención:

#### Procedimiento 1 · Capturar la pantalla y mirarla de verdad

No basta con que `screen_save()` (§7.3) no lance un error, ni con comprobar que el PNG existe en
disco con `file_exists()` — eso solo demuestra que la función de captura funcionó, no que lo que
hay **dentro** del PNG sea correcto. La fuente muda de la Trampa 5 habría pasado esa
comprobación sin problema: la captura se generaba perfectamente, con la pantalla completa, el
fondo, los botones... y ningún texto.

1. Dispara la captura en el punto exacto que quieres validar — el modo QA de §7.4 ya te da el
   mecanismo (`capturar_incidencia()` o una tecla dedicada) sin tener que jugar a mano.
2. **Abre el PNG y léelo tú, o pídeselo a un agente con capacidad de leer imágenes** (la
   herramienta de lectura de archivos de la mayoría de agentes de IA muestra PNG directamente).
   Comprobar que el archivo pesa más de X bytes no sirve: un PNG de una pantalla con texto vacío
   pesa, a simple vista, lo mismo que uno con texto — la diferencia solo se ve mirando.
3. Confirma explícitamente, por cada pantalla que pruebes, lo que el propio encargo pedía
   verificar: que el texto que el código dice que dibuja aparece de verdad, que los botones
   están donde deberían, que ningún elemento se solapa o queda cortado.
4. No asumas que una fuente o una pantalla nueva funciona por analogía con una ya probada: cada
   fuente creada por `resourcetool` (que no rasteriza glifos — Trampa 5) y cada pantalla nueva
   necesita su propia captura mirada, no una inferencia sobre una captura anterior.

> ✅ **La mitad barata de esto ya no necesita ojos: un glifo que la fuente no tiene mide CERO.**
> Medido dentro del juego contra la fuente por defecto del motor — `a=9`, `á=0`, `ñ=0`, `¿=0` —
> lo que convierte «¿esta fuente dibuja español?» en una condición de arranque:
>
> ```gml
> debug_exigir_fuente_con_acentos(global.fnt_ui);   // 06 · scr_debug.gml
> ```
>
> **Hazlo primero, siempre**: cuesta microsegundos y caza la fuente muda —el fallo más común de
> los dos— antes de gastar una captura. Lo que **no** puede decirte es si el glifo dibujado es el
> correcto: una hoja de glifos con el mapa desordenado mide perfectamente y dibuja letras
> cambiadas. Para eso, los pasos 1-4 de arriba siguen siendo la única vía.

> ✅ **Dos casos concretos del paso 3, verificados construyendo un juego móvil completo**
> ([`_indice/auditorias/r7-prueba-movil.md` §2.5-2 y §2.5-3](../_indice/auditorias/r7-prueba-movil.md#25--sirvieron-las-once-trampas-o-tropecé-con-alguna-nueva)),
> ninguno de ellos una función rota: **cómo un agente compone piezas correctas**, algo que ni el
> compilador ni `validar-proyecto.py` pueden ver porque no es una cuestión de sintaxis.
>
> - Un menú con 5 botones a una altura «generosa» — bien por encima del suelo táctil mínimo de
>   [`04 · 28` §5.1](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#51-el-tamaño-mínimo-de-un-botón) —
>   medía, sumado, más que el alto de diseño de la sala: el título se solapaba con el primer
>   botón y el último quedaba fuera de la pantalla. Las fórmulas de tamaño mínimo eran correctas
>   por separado; nadie sumó la altura total del bloque contra el espacio disponible.
> - Un botón «Continuar» desactivado (correctamente, sin partida guardada — el código de toque
>   ya lo ignoraba) usaba un gris más claro a menor alfa frente al gris más oscuro y mayor alfa
>   de los botones activos: sobre fondo negro, el brillo final resultante era **prácticamente
>   idéntico** — el botón se veía indistinguible de uno activo en la captura, un bug de
>   *affordance*, no de lógica: no hay ningún *hover* que lo delate en una interfaz táctil.
>
> Los dos compilaron limpio, dos veces, sin ningún aviso. Solo se vieron aplicando este mismo
> procedimiento — mirando la captura, no el código.

#### Procedimiento 1 bis · Si no puedes ejecutar: recomponer la pantalla fuera del motor

El Procedimiento 1 empieza con «dispara la captura». **¿Y si no puedes ejecutar el juego?** Pasa
más de lo que parece: un agente al que se le prohíbe `gm-cli run`, un entorno sin pantalla, una
plataforma que no compila aquí. Entre «compila» y «se ve bien» quedaba entonces un vacío, y
`§8.8` —las seis preguntas— no lo llena, porque es una lectura del código.

**La salida es componer la pantalla en Python con los mismos assets**: los mismos PNG, la misma
rejilla, el mismo `image_index` de autotile, el mismo orden de dibujo, la misma fuente de sprite
y el mismo encaje de cámara que hace tu objeto de nivel. Unas 150 líneas con Pillow.

Un agente lo hizo en un juego de puzles y **cazó dos fallos que ni el compilador, ni
`validar-proyecto.py`, ni las seis preguntas vieron**
([`r15` §2.10](../_indice/auditorias/r15-prueba-puzles.md)):

- **El nivel no quedaba centrado.** En la función de encaje de cámara, el término que descuenta
  la franja del HUD **sumaba** donde tenía que restar. Un signo. Leyendo el código pasa
  desapercibido; en la maqueta se ve la banda vacía de 45 px al instante.
- **La pista se salía de la pantalla por los dos lados.** El panel se dibujaba a
  `string_width(texto) + 14` sin acotar contra los 320 px de ancho de la sala.

Ninguno de los dos es un símbolo inventado ni un error de sintaxis, que es justo lo que las seis
preguntas de §8.8 sí cazan. Son errores de **composición**, y solo se ven mirando.

> 🔴 **Y la regla que hace que esto no se convierta en una mentira: di que es una maqueta.**
> Una imagen compuesta en Python **no es una captura del juego** y no comparte una sola línea de
> GML con él: puede coincidir con lo que se verá y puede no coincidir, porque reproduce tu
> lectura del código, no el código. Escríbelo en la cabecera del script y escríbelo al informar.
> Vale para lo que vale —geometría, encaje, solapes, texto que se sale, contraste— y **no** vale
> para dar por verificada la Trampa 5 (una fuente muda se dibuja perfecta en la maqueta, porque
> la maqueta usa la fuente del PNG, no la del `.yy`) ni para el tacto del movimiento.

| Lo que quieres saber | Procedimiento |
|---|---|
| ¿Compila? | `gm-cli compile` sin `--errors-only` |
| ¿Los símbolos existen? | `validar-proyecto.py --todo` |
| ¿Falta alguna pieza del envoltorio? | `auditar-juego-completo.py` |
| ¿Está bien compuesta la pantalla? | **este procedimiento**, si no puedes ejecutar |
| ¿Se ve de verdad lo que el código dice? | Procedimiento 1 — hace falta ejecutar |
| ¿El guardado sobrevive al cierre? | Procedimiento 2 — hace falta ejecutar |
| ¿Se siente bien? | Una persona |

#### Procedimiento 2 · Verificar el guardado tras cerrar y reabrir el proceso

`save_game()` devolviendo `true` en el mismo `run` **no demuestra que el guardado sobreviva**:
demuestra que la función terminó sin error interno, y nada más. La Trampa 6 fallaba exactamente
ahí — el *gate* de `save_ensure_dir()` podía decir que no, mientras la escritura real seguía
funcionando en otros puntos del flujo, así que un chequeo superficial («¿el archivo existe justo
después de guardar?») podía salir en verde por pura coincidencia. La única prueba que no se
puede falsear así es el ciclo completo de proceso:

1. Arranca el juego (`gm-cli run`), juega o fuerza (con el modo QA de §7.4) hasta un estado que
   dispare `save_game()` con datos identificables — una puntuación concreta, no un valor por
   defecto que podría venir de cualquier sitio.
2. Confirma en el log (`registrar()` de §7.2, o `show_debug_message`) que el guardado devolvió
   `true` — necesario, pero no suficiente.
3. **Mata el proceso del runner por completo** ([`12 · 09` §4.3](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#43-gm-cli-run-no-propaga-el-estado-del-juego--y-deja-procesos-huérfanos-si-crashea):
   `pkill -f Mac_Runner` o el nombre del runner de tu plataforma) — no reinicies la room, no
   llames a una función de «recargar»: el objetivo es que no quede nada del proceso anterior en
   memoria.
4. Vuelve a lanzar el juego desde cero (`gm-cli run` otra vez) y comprueba, mirando la pantalla
   o el log, que el dato identificable del paso 1 aparece cargado — el récord, la posición, el
   inventario, lo que hayas guardado.
5. Si el paso 4 no reproduce el dato, el bug está en el guardado a disco (Trampa 6, o cualquier
   otro fallo silencioso de E/S de tu plataforma), no en la lógica de partida — nunca lo
   descartes solo porque el paso 2 salió en verde.

Ninguno de los dos procedimientos exige herramientas fuera de lo que esta biblioteca ya
documenta (`screen_save()` de §7.3, el modo QA de §7.4, `gm-cli run`/`pkill` de `12 · 09` §4.3):
lo que faltaba no era capacidad, era la disciplina de no aceptar «no dio ningún error» como
sinónimo de «funciona». Los dos quedan en el checklist de §12.

### 8.6 bis · Saber qué tiene que salir ANTES de ejecutar

Es el hábito más barato de todos y el que más ha cazado. **Cuatro fallos en un solo día, todos
en el instrumento y no en lo medido, y los cuatro los delató lo mismo**: alguien sabía qué
número tenía que aparecer, y apareció otro.

| Lo que salió | Lo que era |
|---|---|
| Una comprobación que **no imprimía nada**, ni ✓ ni ✗ | la guarda era `is_struct()` sobre un id de instancia: salía por la puerta de atrás |
| **Ceros** a 60°, 75° y 90° | el instrumento fijaba el centro una vez a 0°, y la instancia rotaba alrededor de su esquina: medía donde el objeto ya no estaba |
| **«No toca» en los siete ángulos, también el control** | `place_meeting()` usa la máscara de quien llama, y quien llamaba no tenía sprite |
| Un `✓ todos` que no decía **cuántos** | un ✓ sobre cero se lee igual que un ✓ sobre cuatro |

**La frase que los resume**: *un control que nunca toca no es un control*. Si tu caso de control
—el que TIENE que fallar, o el que TIENE que dar un número concreto— se comporta como el caso
bueno, lo que está roto es el instrumento.

> 🔬 **Cómo se aplica, en dos gestos:**
>
> 1. **Escribe el número esperado antes de ejecutar**, aunque sea en un comentario. «Aquí tienen
>    que salir 4», «a 45° tiene que tocar por fuerza». Una expectativa escrita convierte un
>    resultado raro en una alarma; sin ella, se lee como un dato.
> 2. **Mete siempre un control que tiene que fallar.** Una comprobación que solo mira casos
>    buenos no puede distinguir «todo bien» de «no estoy mirando».
>
> Y un tercero que sale de lo mismo: **una desconfianza sana cuando dos fuentes fiables se
> contradicen.** Una medición dijo que la elipse no servía y la documentación decía que sí. No
> podían ser las dos ciertas — y no lo eran: **estaban hablando de cosas distintas** (la caja
> envolvente y la forma de colisión). Quien midió siguió buscando en vez de creer a la medición,
> y por eso no se deshizo un arreglo correcto. **Cuando la medición y la documentación chocan,
> lo primero que hay que sospechar es que miden variables distintas.**

---

### 8.6 ter · Enumerar desde la AUTORIDAD, no desde una copia

Ésta es la regla madre, y las de abajo son casos suyos. Sale de tres fallos cometidos el mismo
día por dos personas distintas, en tres sitios distintos, que resultaron ser **el mismo fallo**:

| Se enumeraba desde… | La autoridad era… |
|---|---|
| una **lista de objetos escrita a mano** | los objetos que el sistema marca (`nivel_col`) |
| un **manifiesto de assets** | los `.yy` que hay **en el disco** |
| **el campo escrito** en el archivo | **el efecto** en el juego corriendo |

Los tres dan verde. Los tres se lo dan a sí mismos, porque miden la copia que conocen y no lo
que de verdad manda. Dicho así se reconoce el cuarto **antes** de cometerlo: cada vez que
escribas una comprobación, pregúntate **de dónde sale la lista de cosas que va a mirar** — y si
esa fuente puede quedarse desfasada, no es la autoridad.

---

### 8.6 quater · Los TRES peldaños de una verificación, y los dos verdes que no valen

`§8.6` dice que compilar no es funcionar. Hay un peldaño más entre medias, y saltárselo es lo
que produce la mayoría de los verdes falsos:

| Peldaño | Qué prueba | Qué NO prueba |
|---|---|---|
| 1 · **El comando dice que sí** | que la herramienta no devolvió error | nada más — y `Saving...Success` puede ser el guardado del proyecto, no tu comando |
| 2 · **El archivo dice que sí** | que el valor quedó escrito en el `.yy` | que ese valor haga lo que crees |
| 3 · **El juego corriendo dice que sí** | el efecto real | — |

**Los dos primeros son baratos, y por eso se usan; el que importa es el tercero.**

> 📌 **Un caso medido que lo resume.** Un rol cambió nueve velocidades de reproducción y
> verificó leyendo los `.yy` de vuelta: `fallos = 0`. Correcto y honesto — peldaño 2. Pero **en
> esa misma línea de salida iba impreso el `yorigin = 18`** que desplazaba cuatro piezas una
> celda entera, y el ✓ no lo estaba mirando. Lo tuvo delante y no lo vio, porque estaba
> comprobando **la escritura, no el efecto**.

#### El verde por omisión: cuando la comprobación no mira lo que hace falta

Es la otra mitad, y se cuela igual de fácil. Dos formas medidas en la misma sesión:

- **Una lista escrita a mano.** Una comprobación de encaje recorría los cuatro objetos que
  existían el día que se escribió. En cuanto alguien añadiera un quinto, habría dicho `✓` **sin
  haberlo mirado**. Se arregla enumerando por una **marca que el propio sistema pone** —«toda
  instancia que lleve `nivel_col`»— en vez de por una lista que hay que acordarse de ampliar.
- **Una guarda que sale callando.** `if (!is_struct(gestor)) { exit; }` sobre un id de
  instancia salía por la puerta de atrás **sin imprimir ni un ✓ ni un ✗**. La comprobación
  existía, se llamaba, y no comprobaba nada.

> 🔴 **La regla que sale de las dos: una comprobación que no se ejecuta, o que no mira todo lo
> que dice mirar, es PEOR que no tenerla** — porque su silencio se lee como aprobado. Haz que
> cada comprobación diga **cuántas cosas ha mirado**, no solo si le han gustado. Un
> «`PAPELES ✓ 0 piezas`» informa; un `✓` a secas, no.

#### Y cuando una herramienta no puede ver todo el problema, dilo

Una comprobación en ejecución solo ve **objetos que existen y están en la sala**. Si vas a
cambiar diez recursos y solo uno tiene objeto, tu banco validará uno y los otros nueve viajarán
sin mirar.

La salida que funcionó, medida: una **maqueta fuera del motor** que reproduce la aritmética del
constructor y cubre los once recursos sin necesitar objetos. Y lo que la hace fiable no es que
exista, sino que **coincide al píxel con el banco en el único caso que ven las dos**. Acertar
en el caso contrastable es lo único que justifica creerle sobre los otros. Etiquétala como
**maqueta**, no como captura: reproduce tu lectura del código, no el código.

##### Y la versión fuerte: que la maqueta se niegue a funcionar si no está calibrada

Coincidir en el caso contrastable es el mínimo. **La forma robusta es que la propia maqueta lo
compruebe al arrancar y se apague si falla.**

Medido en este proyecto: una herramienta que simula la física del juego para decidir si un nivel
se puede terminar **arranca reproduciendo los cuatro extremos que se midieron en ejecución** —el
abismo de 5 celdas se cruza y el de 6 no; el muro de 5 se sube y el de 6 no—. Si no los
reproduce, **se declara descalibrada y no analiza nada**.

La diferencia es enorme y no es de estilo:

| Maqueta que solo coincide | Maqueta que se calibra sola |
|---|---|
| Es fiable **hoy**, porque alguien lo comprobó | Es fiable **cada vez que se ejecuta** |
| Si el balance cambia, empieza a mentir en silencio | Si el balance cambia, **se calla** |
| Su veredicto hay que contrastarlo | Su veredicto ya viene contrastado |

Una simulación es tan buena como su calibración, y **casi todo el mundo la da por buena porque
la escribió con cuidado**. Escribirla con cuidado no es una calibración: **reproducir una
medición independiente, sí.**

> 🧪 **El complemento, y no es opcional: controles que TIENEN que fallar.** Esa misma
> herramienta lleva dos —un abismo de 9 celdas y un techo de una celda— que deben salir NO APTO.
> Una comprobación que solo prueba casos buenos no puede distinguir «todo bien» de «no estoy
> mirando», que es exactamente el verde por omisión de `§8.6 quater`.

**Y aun así, el veredicto de una maqueta no cierra nada.** Sigue siendo el peldaño 2 con muy
buena pinta: reproduce tu lectura del código, no el código. Lo que decide es el juego corriendo.

---

### 8.7 · El guion de humo: arrancar, capturar sola y verificar el guardado sin manos

§8.6 dice **qué** comprobar. Esta sección es el **cómo**, reproducible por un agente sin manos
ni ojos permanentes sobre la pantalla: cómo arrancar el juego sin quedarse colgado, cómo
conseguir que se capture y se cierre **solo**, dónde cae el archivo y cómo se verifica el
guardado sin que nadie juegue a mano.

> ✅ **Esta sección está verificada en vivo, de punta a punta, no solo compilada.** Sesión del
> 8 de septiembre de 2026, `gm-cli` 2.3.0, runtime `2026.0.0.23`, macOS, proyecto de prueba en
> `~/gm_humo_real` (nunca dentro de esta biblioteca, borrado al terminar). Se montaron los 3
> objetos (`obj_prueba_humo`, `obj_prueba_guardado_humo`, `obj_controlador_humo` — este último,
> ausente del cuerpo del documento en la versión anterior, es el que decide cuál de los otros
> dos instanciar; ver §8.7.2 y §8.7.4), se forzó el evento Draw GUI End real con `resource set`,
> `gm-cli compile --errors-only` y sin el flag salieron `exit 0` sin ningún `WARNING`, y
> `validar-proyecto.py --todo` confirmó cero funciones inventadas sobre los 7 archivos `.gml`
> (35 llamadas analizadas). **Y, a diferencia de la revisión anterior, esta vez `gm-cli run` sí
> se ejecutó** — de hecho fue el encargo explícito de esta sesión: la autocaptura disparó, la
> captura apareció exactamente en la ruta que predecía §8.7.3 (confirmado con `find -newer`, no
> supuesto), se abrió y se miró de verdad, el ciclo de guardado en dos fases sobrevivió a matar
> el proceso entre medias, y no quedó ni un proceso huérfano al terminar. Cada afirmación que
> sigue marcada ✅ tiene esta sesión como fuente directa; lo que sigue marcado ⚠️ es lo que
> ni siquiera esta pasada pudo cubrir (Windows, Linux, HTML5, un paquete firmado y exportado) —
> con la plataforma y el motivo dichos explícitamente, no por omisión.

#### 8.7.1 Arrancar el juego sin bloquear la sesión y sin dejar procesos huérfanos

`gm-cli run --help` (§3.4) no tiene ningún flag de tiempo límite — ni `--timeout` ni nada
parecido. El límite hay que ponerlo tú, envolviendo el proceso:

```bash
#!/usr/bin/env bash
# lanzar-humo.sh — arranca el juego en segundo plano, sin bloquear la sesión, con un
# margen de tiempo, y garantiza que no queda ningún proceso del runner huérfano al salir.
set -uo pipefail

PROYECTO="${1:?ruta al .yyp}"
CONFIG="${2:-Humo}"
TARGET="${3:-mac}"
TOOLCHAIN="GMS2@2026.0.0.23"
NOMBRE_RUNNER="Mac_Runner"        # cambia por plataforma — ver la tabla de abajo
MARGEN_S=20                        # fotogramas de espera del objeto + margen de arranque/cierre

SALIDA="$(mktemp)"
gm-cli run --toolchain "$TOOLCHAIN" --target "$TARGET" --config "$CONFIG" "$PROYECTO" \
    > "$SALIDA" 2>&1 &
PID_RUN=$!

# Espera activa, no un sleep ciego: si el objeto de humo llama a game_end() (caso
# normal), gm-cli run devuelve el control por sí solo y este bucle sale enseguida —
# ✅ verificado en vivo, 8 de septiembre de 2026: una pasada normal de este guion
# completa (compilar + arrancar + esperar 30 fotogramas + capturar + game_end) en
# 2,7-6,1 s según la carga de la máquina, muy por debajo de MARGEN_S — el bucle
# nunca llega a agotar el margen salvo que algo se cuelgue de verdad (ver más abajo).
SEGUNDOS=0
while kill -0 "$PID_RUN" 2>/dev/null && [ "$SEGUNDOS" -lt "$MARGEN_S" ]; do
    sleep 1
    SEGUNDOS=$((SEGUNDOS + 1))
done

# Red de seguridad, SIEMPRE, pase lo que pase arriba — y no es un "por si acaso":
# ✅ verificado en vivo que "kill $PID_RUN" por sí solo NO es fiable para terminar el
# runner real. El proceso Mac_Runner nace con PPID=1 (no es hijo del proceso de
# gm-cli, está huérfano desde el instante en que arranca — "InstallRunnerOnMac" /
# "RunOnMac" en el log lo lanzan por fuera del árbol de procesos de gm-cli), así que
# una señal a $PID_RUN no tiene por qué propagarse. En dos pruebas aisladas de esta
# sesión el resultado fue distinto: una vez el runner seguía vivo un segundo después
# de "kill $PID_RUN"; otra vez ya no estaba tras dos segundos. No lo trates como
# determinista en ningún sentido — `pkill -f "$NOMBRE_RUNNER"` es la única línea que
# se verificó consistente en las tres pruebas de esta sesión (incluida una con un
# objeto que cuelga a propósito, sin llamar nunca a game_end(): el bucle agotó
# MARGEN_S=5 en 5,06 s y `pkill` limpió el proceso, confirmado con `ps` acto
# seguido). Además, y esto tampoco estaba documentado: dos ejecuciones sucesivas sin
# este paso dejaron procesos huérfanos del runner corriendo — verificado en vivo,
# `12 · 09` §4.3 / auditoría r4, hallazgo #50.
kill "$PID_RUN" 2>/dev/null
pkill -f "$NOMBRE_RUNNER" 2>/dev/null

cat "$SALIDA"
echo "__SALIDA_EN__ $SALIDA"   # el llamador decide si borra el temporal o lo inspecciona
```

**El nombre del runner por plataforma**:

| Plataforma | Nombre del proceso | Verificado |
|---|---|---|
| macOS | `Mac_Runner` (ruta completa: `.../runtime-2026.0.0.23/mac/YoYo Runner.app/Contents/MacOS/Mac_Runner`, lanzado con el flag `-runTest`) | ✅ `12 · 09` §4.3, auditoría r4, y re-confirmado de forma independiente el 8 de septiembre de 2026 por esta sesión con el método de comparación de `ps` de abajo — dos fuentes, mismo nombre |
| Windows | ⚠️ no verificado en esta biblioteca — probablemente `Windows_Runner.exe` por el patrón del nombre en macOS | ⚠️ |
| Linux | ⚠️ no verificado — probablemente `Linux_Runner` | ⚠️ |

Si no confías en el nombre (o cambia de versión en versión), no lo asumas: descúbrelo
comparando la lista de procesos antes y después de lanzar, el mismo método que exige el resto
de esta biblioteca para no inventar nada — **este bloque concreto sí se ejecutó en esta
sesión**, con este resultado real:

```bash
ANTES="$(ps -eo comm | sort -u)"
gm-cli run --toolchain GMS2@2026.0.0.23 --target mac "$PROYECTO" > /dev/null 2>&1 &
sleep 3
DESPUES="$(ps -eo comm | sort -u)"
comm -13 <(echo "$ANTES") <(echo "$DESPUES")   # procesos nuevos: ahí está el runner real
kill %1 2>/dev/null
```

```
/Users/…/gm_humo_real/.gmcache/igor/osx/arm64/Igor
hdiutil
```

A los 3 segundos de lanzar, lo que aparece nuevo todavía es **Igor** (el compilador, sigue
trabajando) y `hdiutil` (monta el `.dmg` del runner), no `Mac_Runner` — con caché fría el
compilado tarda más que esos 3 s. `Mac_Runner` aparece un poco después; si tu primera pasada de
este bloque no lo encuentra, sube el `sleep` o repite la comparación un par de veces antes de
concluir nada. Con caché caliente (todas las pruebas siguientes de esta sesión), `Mac_Runner`
ya estaba visible en `ps -ef | grep -i runner` a los 2 s de lanzar.

> ✅ Este bloque de descubrimiento **sí se ejecutó en esta sesión** (8 de septiembre de 2026, la
> salida real está justo arriba). Es el método y, para macOS, ya también un resultado
> reproducido dos veces — pruébalo igualmente en tu plataforma antes de confiar en el nombre si
> no es macOS.

#### 8.7.2 El objeto que se captura solo: por qué Draw GUI, no Alarm ni Step

`screen_save(fname)` (§7.3) **está diseñada para llamarse desde el evento Draw GUI End**; el
propio manual avisa de que en cualquier otro evento «puede no funcionar como se espera, y puede
dar diferentes resultados a través de diferentes objetivos e incluso dispositivos» (fuente en
«Fuentes», al final del documento). Aquí es donde este procedimiento choca con una trampa **ya
documentada por esta biblioteca para otro propósito**, y que nadie había conectado con
`screen_save()` todavía — con una solución real que sí llega a existir, encontrada en paralelo
mientras se escribía esta sección:

> 🔴 **`OBJECT EVENT FINDORCREATE` no puede crear un evento Draw GUI End por nombre.** Es la
> Trampa 3 de [`12 · 09` §0](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-3--resourcetool-crea-el-evento-equivocado-sin-avisar-dos-bugs-de-numeración):
> pedir `subtype=gui_end` no da el evento 75 (el real), da **el mismo archivo que `draw_end`**
> (evento 73) sin ningún aviso — la *whitelist* de `subtype=` es cerrada para ese nombre.

> ✅ **Pero el campo crudo del evento sí se puede forzar con `RESOURCE SET`, y esto se ha
> verificado por código en esta misma sesión, de punta a punta — por dos caminos independientes
> que llegaron al mismo sitio.** `12 · 09` §0 Trampa 9 y su
> [§9 ter](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#9-ter--forzar-un-eventnum-real-cuando-la-whitelist-de-subtype-es-cerrada)
> (añadidos el 8 de septiembre de 2026 por una auditoría de esa sección, en paralelo a esta
> tarea) traen la receta general, con la tabla de números reales verificados y el paso de
> renombrar el `.gml` que esta sección adopta más abajo. La receta que sigue aquí es la
> comprobación específica para este caso concreto —Draw GUI End, no verificado explícitamente en
> `12 · 09`—, hecha sin depender de esa otra fuente:

```bash
gm-cli resourcetool eval "resource create type=object name=obj_prueba_humo"
gm-cli resourcetool eval "object event findorcreate name=obj_prueba_humo type=create"
gm-cli resourcetool eval "object event findorcreate name=obj_prueba_humo type=alarm subtype=0"
gm-cli resourcetool eval "object event findorcreate name=obj_prueba_humo type=draw subtype=gui_end"
gm-cli resourcetool eval "object event findorcreate name=obj_prueba_humo type=step subtype=step_normal"

# El paso anterior creó el evento 73 (draw_end) con otro nombre — la Trampa 3.
# resource info expr=obj_prueba_humo.eventList enseña cuántos eventos hay y en qué
# índice está cada uno; resource info expr=obj_prueba_humo.eventList[N] enseña sus
# campos, incluido el eventNum real. Localiza el índice del evento recién creado
# (eventNum=73 todavía) y fuerza el número correcto:
gm-cli resourcetool eval "resource set expr=obj_prueba_humo.eventList[N].eventNum value=75"

# Confírmalo: debe decir Event_Draw_DrawGUIEnd, no Event_Draw_DrawEnd.
gm-cli resourcetool eval "object event list name=obj_prueba_humo"

# El archivo se quedó con el nombre del número EQUIVOCADO (Draw_73.gml, el de la
# Trampa 3) — renómbralo al número real antes de escribir nada dentro. `12 · 09`
# §9 ter (ver más abajo) es explícito: si no lo haces, el código no vive donde el
# evento real lo busca.
mv objects/obj_prueba_humo/Draw_73.gml objects/obj_prueba_humo/Draw_75.gml
```

**Verificado en esta sesión** (`~/gm_humo_real`, borrado al terminar): tras
`resource set expr=....eventNum value=75`, `object event list` pasó de `Event_Draw_DrawEnd` a
**`Event_Draw_DrawGUIEnd`**, el `.yy` quedó con `"eventNum":75` de verdad, y
`gm-cli compile --errors-only` compiló con `exit 0`. Es el evento real, no una imitación.

> ✅ **El paso de renombrar el `.gml` SÍ se probó de forma aislada en esta sesión, y la
> respuesta es que es obligatorio — no una prudencia, un requisito.** La compilación por sí sola
> no lo delata (compila `exit 0` tanto si el archivo se llama `Draw_73.gml` como
> `Draw_75.gml`), pero el propio log de Igor sí distingue los dos casos con una línea que antes
> nadie había mirado: `Compile Objects...finished.... N empty events`. Con el archivo mal
> nombrado (`Draw_73.gml` y `eventNum:75`) esa línea dice **`1 empty events`**; con el nombre
> correcto (`Draw_75.gml`) dice **`0 empty events`**. Y la consecuencia en tiempo de ejecución es
> exactamente la que predecía [`12 · 09` §9 ter](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#9-ter--forzar-un-eventnum-real-cuando-la-whitelist-de-subtype-es-cerrada):
> con el archivo mal nombrado, el evento Draw GUI End real existe (`eventNum:75` en el `.yy`,
> `object event list` lo confirma) pero está **vacío** — `screen_save()` nunca se llama,
> `debe_capturar` se queda en `true` para siempre, y el juego cuelga sin producir ni el marcador
> `###humo_captura###` ni `game_end()`. Solo lo rescata el `MARGEN_S` de §8.7.1. Con el archivo
> bien renombrado, mismo `.yy`, mismo `eventNum:75`, la única diferencia es el nombre del
> archivo — y el juego captura y termina solo con normalidad. Renombrar el `.gml` no es opcional
> ni una precaución barata: es la diferencia entre un objeto que funciona y uno que cuelga
> siempre, de forma indistinguible por la compilación.

Si por lo que sea `RESOURCE SET` sobre `eventNum` no está disponible en tu versión de
`resourcetool`, o prefieres no depender de un campo interno no documentado por YoYo Games, la
alternativa con garantía total del motor sigue siendo abrir el proyecto en el IDE **una sola
vez** y crear el evento Draw GUI End desde ahí — el mismo patrón que ya resuelve la Trampa 5 de
fuentes mudas (`12 · 09` §0): una vez creado, `resourcetool` y el editor de archivos normal
pueden tocar su `.gml` para siempre sin volver a abrir el IDE.

El objeto completo — **compilado y ejecutado de verdad en esta sesión**, con el evento ya
forzado a Draw GUI End real y el `.gml` ya renombrado (imprescindible, no cosmético — ver el
recuadro de arriba), `gm-cli compile` con y sin `--errors-only`, `exit 0` los dos, sin
`WARNING`, `validar-proyecto.py --todo` en cero funciones inventadas, y en ejecución real
(`gm-cli run`) capturó y terminó solo, de forma repetible, en varias pasadas de esta sesión:

```gml
/// obj_prueba_humo · Create_0.gml
/// Espera N fotogramas, se autocaptura y termina el juego solo.
fotogramas_espera = 30;     // a 60 fps (option_game_speed por defecto), medio segundo:
                              // margen para que fuentes y sprites pinten un frame completo.
                              // Súbelo si tu room tiene una carga o generación procedural
                              // que tarda más de eso en terminar antes de dibujar nada útil.
nombre_captura     = "humo_captura.png";
debe_capturar      = false;
debe_terminar      = false;

alarm_set(0, fotogramas_espera);
```

```gml
/// obj_prueba_humo · Alarm_0.gml
/// Solo levanta la bandera — la captura real ocurre en Draw GUI End (§8.7.2 explica por qué).
debe_capturar = true;
```

> ⚠️ **El objeto tal y como está descrito hasta aquí no dibuja nada** — captura la pantalla,
> pero la pantalla está en blanco (el color de fondo de la room). El paso 5 del guion completo
> (§8.7.6) pide «confirma texto, botones y capas», y con solo `Create`/`Alarm`/Draw GUI End no
> hay nada que confirmar. Añade un evento Draw normal (no GUI, no GUI End: éste se dibuja en
> coordenadas de mundo, antes que el GUI End, y su resultado ya está compuesto en pantalla
> cuando `screen_save()` se ejecuta) con contenido mínimo — verificado en esta sesión:

```gml
/// obj_prueba_humo · Draw_0.gml
/// Contenido visual mínimo para que la autocaptura tenga algo real que demostrar.
draw_set_colour(c_lime);
draw_rectangle(100, 100, 500, 300, false);

draw_set_font(fnt_prueba_humo);
draw_set_colour(c_black);
draw_text(120, 150, "HUMO OK");
```

> 🔴 **El rectángulo se vio en la captura; el texto no — Trampa 5 de `12 · 09` §0 reproducida en
> vivo, dentro de este procedimiento concreto.** `fnt_prueba_humo` se creó con el patrón normal
> (`resource create type=font`, `font setfile` apuntando a un `.ttf` real del sistema,
> `font addrange lower=32 upper=255`, `resource set expr=….size value=24`) y todo respondió
> `Success` — pero `font glyphlist name=fnt_prueba_humo` mostró el diccionario vacío, el `.yy`
> quedó «marked for re-generation» sin regenerarse nunca, y el chunk `FONT` compiló a
> `0.00 MB`. La captura real (§8.7.3) lo confirmó sin ambigüedad: **el rectángulo se ve
> perfectamente; la palabra «HUMO OK» no aparece, ni un solo píxel**. Es la prueba, dentro de
> este mismo guion de humo, de por qué §8.6 insiste en mirar la captura de verdad — un archivo
> PNG que existe y pesa lo normal (5,9 KB aquí) no demuestra que su contenido sea correcto. Si
> tu prueba de humo necesita texto legible, resuelve Trampa 5 primero (abrir el proyecto en el
> IDE una vez y guardar la fuente, o el horneado con Pillow — ambos en `12 · 09` §0) **antes**
> de fiarte de lo que la captura dice sobre el texto. El rectángulo, al no depender de ninguna
> fuente, es la parte de esta prueba que sí es fiable de fábrica.

```gml
/// obj_prueba_humo · Draw_75.gml  (renombrado desde Draw_73.gml tras el "resource set"
/// de arriba — eventNum 75, Draw GUI End real)
if (debe_capturar)
{
    screen_save(nombre_captura);
    debe_capturar = false;
    debe_terminar = true;   // termina en el SIGUIENTE Step, no aquí: deja que el frame
                              // actual — incluida la escritura del PNG a disco — acabe antes.
}
```

```gml
/// obj_prueba_humo · Step_0.gml
/// Marcador de texto plano: el envoltorio de shell no puede fiarse del código de
/// salida de gm-cli run, que no lo propaga (§3.4).
if (debe_terminar)
{
    show_debug_message($"###humo_captura###{nombre_captura}");
    game_end(0);
}
```

Coloca una instancia fija de `obj_controlador_humo` en la primera room que arranca — es un
tercer objeto, no mencionado antes en esta sección y que hacía falta nombrar de verdad: decide
en tiempo de ejecución cuál de los dos objetos de prueba instanciar, bajo la configuración de
pruebas, con el mismo patrón que ya usa §3.5:

```bash
gm-cli resourcetool eval "config create name=Humo parent=Default"
gm-cli resourcetool eval "resource create type=object name=obj_controlador_humo"
gm-cli resourcetool eval "object event findorcreate name=obj_controlador_humo type=create"

# Colócalo de verdad en la room — la versión anterior de esta sección nunca dio este
# comando, solo decía "coloca una instancia". ROOM y OBJECT van sin más nombre de
# argumento; LAYER si no existe se crea. Verificado en esta sesión, "New instance
# 'inst_…'" en la salida y la instancia visible en el .yy de la room después.
gm-cli resourcetool eval "room instance create room=room1 object=obj_controlador_humo layer=Instances x=0 y=0"
```

> 🔴 **Por qué hace falta un controlador y no basta con `instance_create_layer` a pelo, como
> decía la versión anterior de esta sección.** §8.7.4 reutiliza la misma configuración `Humo`
> para el ciclo de guardado (`obj_prueba_guardado_humo`). Si los dos objetos de prueba se
> instancian con el mismo `if (os_get_config() == "Humo")`, los dos quedan activos a la vez: y
> `obj_prueba_guardado_humo` llama a `game_end()` en su propio `Create`, en el fotograma 0 —
> antes de que la alarma de `obj_prueba_humo` (30 fotogramas después) llegue siquiera a
> dispararse. El proceso termina de golpe y ninguna de las dos pruebas corre completa. La
> variable de entorno `HUMO_FASE` que ya usa §8.7.4 para el ciclo de guardado es también la
> señal más barata para separar los dos casos: ausente → prueba de captura; presente → prueba
> de guardado. Verificado en esta sesión: con esta rama, la prueba de captura corre sola cuando
> no hay `HUMO_FASE`, y la de guardado corre sola cuando sí la hay — sin colisión, en ambos
> sentidos.

```gml
/// obj_controlador_humo · Create_0.gml
if (os_get_config() == "Humo")
{
    var _fase = environment_get_variable("HUMO_FASE");
    if (_fase == "")
    {
        instance_create_layer(0, 0, "Instances", obj_prueba_humo);
    }
    else
    {
        instance_create_layer(0, 0, "Instances", obj_prueba_guardado_humo);
    }
}
```

> ✅ Esto también confirma, de paso, algo que el manual de `environment_get_variable()` no dice
> explícitamente: **la función devuelve cadena vacía (`""`), no un valor que rompa la
> comparación ni un error, cuando la variable de entorno no está definida.** Es lo que hace
> posible la rama `_fase == ""` de arriba — verificado en esta sesión, no asumido del manual.

> ⚠️ **No es válido en HTML5.** `screen_save()` no funciona en ese target (nota del propio
> manual) y `game_end()` deja el lienzo en blanco al salir (§8.3, ya documentado). Este
> procedimiento es para los targets de escritorio (`--target mac|windows|linux`).

#### 8.7.3 Dónde queda la captura y cómo la lee el agente

El manual de `screen_save()` dice que el archivo cae en «el directorio de trabajo del juego»,
y da como ejemplo `~/Library/Application Support/[Game Name]/` en Mac — pero esa frase es
engañosa si la comparas con `01 · 14` §1: ese directorio, con ese nombre, **no es el file bundle
de solo lectura que la propia biblioteca llama `working_directory`**, es el **save area**
(`game_save_id`), la única zona con escritura garantizada. `working_directory` se redirige ahí
automáticamente en cuanto el sandbox no permite escribir donde apunta de verdad (`01 · 14`, la
propia página de `working_directory`) — que es el caso por defecto. En la práctica, para un
juego de escritorio sin el sandbox desactivado, **es el mismo sitio**.

La ruta exacta, verificada en vivo dos veces — en la auditoría `r5-prueba-e2e` (08-09-2026) y
de nuevo, de forma independiente, en esta misma sesión (también 08-09-2026, mismo `gm-cli`
2.3.0 y runtime `2026.0.0.23`, con `find -newer` sobre una marca de tiempo real, no supuesta),
con una diferencia importante frente a lo que dice el manual en general:

```
game_save_id = [/Users/.../Library/Application Support/com.yoyogames.macyoyorunner/]
```

**No es `~/Library/Application Support/<Nombre del juego>`** como promete la tabla genérica de
`01 · 14` — es `com.yoyogames.macyoyorunner`, el identificador del *runner* de pruebas sin firma
que lanza `gm-cli run`, igual para cualquier proyecto que compiles con este flujo. Un build
firmado y exportado de verdad (`gm-cli package`, §8.4) previsiblemente usa el identificador real
de tu juego ahí en vez de ese genérico — ⚠️ **eso no está verificado**, ningún documento de esta
biblioteca ha inspeccionado el save area de un paquete exportado todavía.

| Plataforma | Ruta con `gm-cli run` (sin firmar) | Verificado |
|---|---|---|
| macOS | `~/Library/Application Support/com.yoyogames.macyoyorunner/` | ✅ r5-prueba-e2e, 08-09-2026, y re-confirmado de forma independiente el mismo día por esta sesión |
| Windows | ⚠️ previsiblemente `%localappdata%\<algo genérico del runner>`, por el mismo patrón que macOS | ⚠️ no verificado |
| Linux | ⚠️ previsiblemente `~/.config/<algo genérico del runner>` | ⚠️ no verificado |

> 🔴 **Ese directorio se comparte entre proyectos distintos que uses con `gm-cli run` en la
> misma máquina** — no es exclusivo de tu juego. Verificado en esta sesión: junto al
> `humo_captura.png` de esta prueba aparecían, sin relación alguna, capturas y archivos `.json`
> de otro proyecto (`lumbre_captura_….png`, `lumbre_a.json`…) de una sesión anterior. Si dos
> proyectos usan el mismo nombre de archivo de captura o de guardado, uno pisa al otro sin
> avisar. Usa nombres de archivo distintivos (`humo_captura.png`, no `captura.png`) o borra el
> archivo antes de lanzar, como hace `find -newer` de abajo al usar una marca de tiempo en vez
> de confiar en que el archivo no existiera ya.

**Cómo lo encuentra un agente sin memorizar la ruta** — el mismo principio que el resto de esta
biblioteca aplica a todo lo demás: no confíes en una ruta fija, compruébala. **Este bloque
concreto se ejecutó en esta sesión y encontró el archivo real**, en el primer intento:

```bash
MARCA="$(mktemp)"                          # marca de tiempo, antes de lanzar
gm-cli run --toolchain GMS2@2026.0.0.23 --target mac --config Humo "mi-juego.yyp" \
    > /dev/null 2>&1
find ~/Library/Application\ Support -maxdepth 2 -iname "*.png" -newer "$MARCA" 2>/dev/null
```

```
/Users/adrianpereradelgado/Library/Application Support/com.yoyogames.macyoyorunner/humo_captura.png
```

En Windows, cambia la raíz por `%LOCALAPPDATA%`; en Linux, por `~/.config` — ninguna de las dos
se pudo probar en esta sesión (sin esas plataformas a mano), siguen como ⚠️ previsible por
patrón, no verificado.

**Cómo la mira el agente, una vez la tiene**: ábrela con la herramienta de lectura de archivos
que muestre PNG (la mayoría de agentes de IA la tienen) y **mírala de verdad** — §8.6
Procedimiento 1 ya insiste en que un archivo que existe y pesa lo normal no demuestra que su
contenido sea correcto. **Esto se hizo de verdad en esta sesión, y confirmó exactamente esa
advertencia por las malas**: la captura de `obj_prueba_humo` (§8.7.2) mostraba el rectángulo
verde con total nitidez, en la posición exacta del código — pero el texto «HUMO OK» que el
mismo `Draw_0.gml` dibuja **no aparecía en absoluto**, por la Trampa 5 de fuentes vacías
reproducida en vivo (ver el recuadro en §8.7.2). Un agente que solo comprobara «¿existe el PNG
y pesa algo razonable?» (5,9 KB, nada sospechoso) habría dado la prueba por buena sin detectar
que la mitad del contenido esperado faltaba. No hay atajo nuevo aquí: esta sección resuelve
*cómo llegar* al archivo; lo que se hace con él una vez abierto ya está en §8.6 — y esta sesión
es la prueba de que ese paso no es opcional.

> ⚠️ **`screen_save()` se midió invirtiendo la imagen, y HOY YA NO lo hace. No la voltees.**
> Re-comprobado el **2026-09-10** sobre el runtime 2026.0.0.23 en macOS arm64: el PNG sale
> derecho. Un agente se creyó el aviso anterior, volteó su captura para «corregirla» y le
> quedó boca abajo. **Lo que sigue valiendo es el contraste**, porque es barato y cubre los dos
> casos: una vez por sesión, compara una captura de `screen_save()` con una de `screencapture`
> del sistema sobre el mismo fotograma. Si coinciden, ninguna trampa; si difieren solo en el
> eje vertical, el volteo ha vuelto. La medición original (Trampa 13 de
> [`12 · 09` §0](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-13--screen_save-invirtió-la-imagen-una-vez--y-hoy-ya-no-no-la-voltees),
> contrastando el PNG contra una captura de pantalla real (`screencapture`) tomada mientras se
> veía el mismo fotograma en la ventana del runner: la ventana se veía perfectamente, derecha;
> el PNG de `screen_save()` salía boca abajo, con el orden vertical invertido. Si lo que estás
> verificando con este procedimiento incluye POSICIÓN vertical (un elemento arriba/abajo, un
> solapamiento con el borde superior o inferior de la pantalla, «¿el título está por encima del
> primer botón?»), **no confíes en el eje Y de esta captura sin contrastarla al menos una vez
> con `screencapture` en la misma sesión** — la Trampa 5 de fuentes mudas (arriba, §8.7.2/§8.7.3)
> ya demostró que un PNG que existe y pesa lo normal puede mentir sobre su CONTENIDO; esta
> trampa demuestra que también puede mentir sobre su ORIENTACIÓN, mientras el juego real se ve
> bien. Para diagnósticos que no dependen de arriba/abajo (¿aparece el texto?, ¿es el color
> correcto?, ¿existe el sprite?) esta trampa no cambia la conclusión.

#### 8.7.4 El ciclo de guardado sin manos: dos lanzamientos, un objeto

§8.6 Procedimiento 2 ya describe el ciclo manual (jugar, guardar, matar el proceso, reabrir,
comprobar). Aquí está automatizado con el mismo patrón de objeto de prueba — sin que nadie
juegue a mano — para verificar el **mecanismo de E/S** (que un archivo escrito en una ejecución
sobreviva a la muerte del proceso y se lea en la siguiente). Es deliberadamente independiente
del sistema de guardado real de tu juego: valida el mismo circuito que usa `save_game()` /
`load_game()` (`01 · 14` §9-10) sin arrastrar su complejidad. Para el ciclo completo con datos de
partida de verdad, combina esto con el modo QA de §7.4 (F6/F7 fuerza victoria/derrota) tal como
ya recomienda §8.6.

```bash
gm-cli resourcetool eval "resource create type=object name=obj_prueba_guardado_humo"
gm-cli resourcetool eval "object event findorcreate name=obj_prueba_guardado_humo type=create"
```

```gml
/// obj_prueba_guardado_humo · Create_0.gml
/// La fase la decide una variable de entorno, no el código de salida de gm-cli run
/// (§3.4) ni directory_exists()/directory_create() — pueden devolver false SIEMPRE
/// bajo gm-cli run --target mac, incluso sobre una carpeta que ya existe (Trampa 6
/// de 12/09, verificada en vivo en r5-prueba-e2e). Por eso el intento de lectura de
/// verdad decide, nunca una comprobación previa.

var _archivo      = "humo_guardado.sav";
var _valor_prueba = "humo_valor_de_prueba_137";

var _fase = environment_get_variable("HUMO_FASE");
if (_fase == "") { _fase = "escribir"; }

if (_fase == "leer")
{
    if (!file_exists(_archivo))
    {
        show_debug_message("###humo_guardado###FALLO###archivo_no_existe");
        game_end(1);
        exit;
    }

    var _f     = file_text_open_read(_archivo);
    var _leido = file_text_read_string(_f);
    file_text_close(_f);

    var _ok = (_leido == _valor_prueba);
    show_debug_message($"###humo_guardado###{_ok ? "OK" : "FALLO"}###{_leido}");
    file_delete(_archivo);   // deja el terreno limpio para la siguiente tanda

    game_end(_ok ? 0 : 1);
}
else
{
    var _f = file_text_open_write(_archivo);
    file_text_write_string(_f, _valor_prueba);
    file_text_close(_f);

    show_debug_message($"###humo_guardado###ESCRITO###{_valor_prueba}");
    game_end(0);
}
```

El envoltorio de shell lanza el juego **dos veces**, matando el proceso entre medias con el
mismo patrón de §8.7.1 — no basta con dejar que termine solo, hay que asegurarse de que no
sobrevive nada en memoria de la primera ejecución:

```bash
#!/usr/bin/env bash
# verificar-guardado-humo.sh
set -uo pipefail
PROYECTO="${1:?ruta al .yyp}"

echo "── Fase 1: escribir ──"
HUMO_FASE=escribir bash lanzar-humo.sh "$PROYECTO" Humo mac
# (lanzar-humo.sh de §8.7.1 ya mata gm-cli run y pkill -f Mac_Runner al terminar —
#  aquí no hace falta nada más para garantizar que no queda nada vivo)

echo "── Fase 2: releer tras matar el proceso ──"
HUMO_FASE=leer bash lanzar-humo.sh "$PROYECTO" Humo mac
```

Comprueba `###humo_guardado###ESCRITO` en la salida de la fase 1 y `###humo_guardado###OK` en la
de la fase 2 (no `FALLO`, y no la ausencia total del marcador — eso sería un cuelgue o un crash
antes de llegar al `Create`).

> ✅ **El patrón completo se ejecutó de punta a punta en esta sesión, con el mismo objeto de
> prueba, matando el proceso de verdad entre las dos fases** (no solo dejándolo terminar solo:
> `lanzar-humo.sh` hace `kill` del proceso de `gm-cli run` y `pkill -f Mac_Runner` al final de
> cada fase, antes de que arranque la siguiente). Salida real:
>
> ```
> ── Fase 1: escribir ──
> │  ###humo_guardado###ESCRITO###humo_valor_de_prueba_137
> ── Fase 2: releer tras matar el proceso ──
> │  ###humo_guardado###OK###humo_valor_de_prueba_137
> ```
>
> El `OK` de la fase 2 es la parte que importa: demuestra que `humo_guardado.sav`, escrito por
> un proceso de `Mac_Runner` que ya no existe, sigue en disco y se lee igual en un proceso
> nuevo — exactamente la comprobación que habría cazado el bug de `directory_exists()` que
> describe la Trampa 6 de `12 · 09` §0, sin necesidad de que nadie juegue a mano. Las dos fases
> juntas tardaron **6,1 s** en esta sesión (≈3 s cada una, cache caliente); ningún proceso del
> runner quedó vivo al terminar (`ps -ef | grep -i runner` vacío, comprobado justo después).

#### 8.7.5 Qué caza este procedimiento y qué no

**Caza, con confianza razonable**: pantalla en negro o a medias, una fuente que compila pero no
dibuja ni una letra (la Trampa 5 exacta que motivó §8.6, y reproducida dentro de este mismo
guion en §8.7.2/§8.7.3), un elemento de UI fuera de sitio o solapado (no hipotético — un menú
que se salía de la pantalla y un botón desactivado indistinguible del activo, los dos casos
reales del recuadro de §8.6), un guardado que no
sobrevive a cerrar el proceso, un `game_end()` que nunca llega (el objeto se queda colgado sin
terminar — el propio `MARGEN_S` de §8.7.1 lo delata por *timeout*), y una excepción no
controlada que sí aparece en el log (§4.1 de `12 · 09`).

> ✅ **Un caso concreto de «`game_end()` que nunca llega», reproducido a propósito en esta
> sesión**: un evento Draw GUI End cuyo `.gml` se quedó con el nombre equivocado tras el truco
> de `resource set` de §8.7.2 compila limpio, pero el motor lo trata como **vacío** en tiempo de
> ejecución (`Compile Objects...finished.... 1 empty events` en el log de Igor, en vez de
> `0 empty events`) — `screen_save()` nunca se llama, `debe_capturar` se queda en `true` para
> siempre, y el juego no produce ni el marcador ni `game_end()`. `MARGEN_S` lo cazó igual: con
> `MARGEN_S=5` de prueba, el corte llegó a los 5,06 s y `pkill` limpió el proceso. Este
> procedimiento no distingue «el juego tarda en cargar» de «un evento se quedó vacío por un bug
> de `resourcetool`»; ambos se ven igual desde fuera — silencio hasta el *timeout*. Si el
> `fotogramas_espera` de tu objeto es razonable y aun así siempre agota `MARGEN_S`, sospecha
> primero de un evento vacío, no de que tu juego sea lento.

Un dato adicional sobre cómo se ve la salida cuando todo va bien: el propio *runner* de
`gm-cli run`, al lanzarse con el flag `-runTest` (visible en su línea de comando), añade por su
cuenta una línea `###game_end###N` al `debug.log` en cuanto se llama a `game_end(N)` — **no es
algo que el objeto de prueba tenga que escribir**, es el runner el que lo hace, verificado en
esta sesión (ningún `.gml` del proyecto de prueba contenía ese texto y aun así apareció, siempre
justo después del marcador `###humo_captura###` y justo antes de `Game exited`). Es una segunda
señal, gratuita, de que el juego terminó por su cuenta — el mismo patrón que ya usa `13 · 10`
§3.4 para las pruebas unitarias.

**No caza nada de esto** — la lista ya la da `12 · 09` §4.2 con más detalle, no se repite aquí
completa:

- **Jugabilidad, dificultad o sensación** (*game feel*): son juicios humanos, no hay señal en el
  log ni en un PNG que los sustituya.
- **Sonido**: si algo suena mal, si la mezcla satura, si el volumen relativo tiene sentido.
- **Input táctil o de mando físico real**: `gm-cli run` no simula gestos ni un mando conectado.
- **Rendimiento en el hardware objetivo real** (móvil, consola): el runner de escritorio no lo
  reproduce.
- **Certificación de plataforma** (Steam, tiendas, consolas): fuera del alcance de GameMaker.

Y una frontera propia de este procedimiento en concreto, no de `12 · 09`: **una captura tomada
en el fotograma equivocado, o antes de que algo termine de cargar, es indistinguible de una
captura correcta si no la miras** — el `fotogramas_espera` de §8.7.2 es un número que hay que
ajustar a tu juego, no una constante universal. Este guion no sustituye QA manual (§9) ni
playtesting (§10): reduce el coste de la comprobación mecánica de «¿se ve algo razonable y se
guarda de verdad?» para que el tiempo humano se dedique a lo que sí necesita ojos y manos
humanas.

Y una tercera frontera, en Mac: **el paso 5 del guion completo de §8.7.6 (mirar
`humo_captura.png`) no es fiable para juzgar POSICIÓN vertical sin contrastarlo antes con
`screencapture`** — `screen_save()` se midió una vez invirtiendo la imagen verticalmente, y
en el runtime 2026.0.0.23 **ya no lo hace** (re-comprobado el 2026-09-10; Trampa 13 de
`12 · 09` §0, con la historia fechada, y aviso completo en §8.7.3 de esta misma sección). El
contraste se mantiene no porque el volteo siga vivo, sino porque es lo único que distingue
«ha vuelto» de «nunca pasó». El guion detecta igual de bien que «se ve algo» o que «hay texto»; lo que
NO garantiza sin ese contraste es que arriba/abajo en el PNG signifique arriba/abajo de verdad.

#### 8.7.6 El guion de humo completo, antes de decir que un juego está terminado

Secuencia mínima, encadenando todo lo de arriba, para ejecutar antes de dar cualquier tarea de
GameMaker por cerrada — engánchala al checklist de §12. **Verificada de punta a punta el 8 de
septiembre de 2026** (`gm-cli` 2.3.0, runtime `2026.0.0.23`, macOS, proyecto `~/gm_humo_real`),
con los tiempos reales de esa pasada:

```
1. gm-cli compile --errors-only            → exit 0                         (§8.1)          ~1-10 s*
2. gm-cli compile (sin el flag)             → exit 0, sin WARNING            (§8.1, Trampa 8 de 12/09) ~1-2 s
3. python3 _indice/validar-proyecto.py <ruta> --todo
                                             → 0 funciones inventadas        (§8.5, Trampa 4) instantáneo
4. lanzar-humo.sh <proyecto> Humo <target>  → ###humo_captura### en la salida (§8.7.1-2)      ~3-6 s
5. Abre humo_captura.png (§8.7.3) y MÍRALA — confirma texto, botones y capas (§8.6 Procedimiento 1)
6. verificar-guardado-humo.sh <proyecto>    → ESCRITO en fase 1, OK en fase 2 (§8.7.4)         ~6 s (dos lanzamientos)
7. Ningún proceso del runner sigue vivo: ps -ef | grep -i runner → vacío     (§8.7.1)          instantáneo
```

\* El primer `compile` de una sesión paga un coste único de caché (descarga/verificación de
Igor y del runtime si no estaban ya en `~/Library/Caches/GameMakerCLI/`); con caché caliente
baja a ~1-2 s, igual que el paso 2. Ese coste único también se paga en el primer `gm-cli run`
de la sesión («Downloading tools» / «Downloading Igor» / «Fetching license» / «Restoring
prefabs» / «Installing runtime» en su salida) — no vuelve a pagarse en los lanzamientos
siguientes, que es de donde salen los ~3-6 s del paso 4. El total de esta secuencia, de arranque
en frío a limpio, no bajó de la cifra de un solo dígito de segundos por paso salvo el primer
`compile`; en ningún caso llegó a acercarse al `MARGEN_S=20` por defecto.

Si el paso 4 o el 6 no producen su marcador (ni `OK` ni `FALLO`, silencio total), el objeto de
humo no llegó a `game_end()` — trátalo como un fallo, no como «tardó en arrancar»: aquí es
exactamente donde `MARGEN_S` corta la espera y limpia el proceso. Sospecha primero de un evento
vacío por un `.gml` mal renombrado (§8.7.2, §8.7.5) antes que de que el juego sea lento — es la
causa que esta sesión encontró de verdad al reproducir el cuelgue a propósito.

---

### 8.8 Cuando NO puedes ejecutar: las seis preguntas que se responden leyendo

Todo lo anterior —el mini-framework, el guion de humo, §8.6— **se apoya en ejecutar el juego**.
Un agente muchas veces no puede: `run` está prohibido en su entorno, no hay pantalla, o el
encargo es una tarea de fondo. Ahí el flujo se queda cojo por diseño y hace falta la otra red.

Esta lista sale de una revisión de código deliberada, sin poder ejecutar, sobre un juego completo
recién construido ([`r12-prueba-plataformas.md` §1.13](../_indice/auditorias/r12-prueba-plataformas.md)).
**Las seis cazaron algo real en esa única pasada**, y ninguno de los cuatro fallos que
encontraron era un símbolo inventado ni un error de sintaxis: `gm-cli compile` y
`validar-proyecto.py` pasaron por encima de los cuatro sin verlos.

Todos comparten forma: **una guarda mal colocada, o una rama que se olvida de un caso.**

1. **¿Toda global que se lee está inicializada en TODOS los caminos de sala?** No basta con que
   se inicialice: tiene que hacerlo también cuando se entra al nivel desde «continuar partida»,
   desde el selector, o volviendo de la pantalla de opciones.
2. **¿Cada objeto del mundo consulta el interruptor de pausa, y ANTES de cualquier otra cosa de
   su Step?** *(Fallo real encontrado así: un enemigo pisado seguía contando su temporizador de
   KO durante la pausa, porque la guarda estaba **después** del bloque de KO.)*
3. **¿Cada objeto de pantalla corta la entrada mientras hay una transición en curso?** *(Fallo
   real: el gestor del nivel era el único objeto **sin** esa guarda; durante el fundido de salida
   se podía abrir la pantalla de opciones, cuyas funciones eran métodos ligados a una instancia
   que muere al cambiar de sala.)*
4. **¿Cada `if / else if` sobre un estado cubre el caso «ninguna de las dos»?** *(Fallo real:
   `if (hay_plataforma && en_suelo) … else if (!en_suelo) …` deja fuera «no hay plataforma
   debajo Y estoy en el suelo», así que la plataforma móvil seguía arrastrando al jugador de pie
   sobre la roca.)*
5. **¿Alguna global guarda un método ligado a una instancia que puede morir antes de que se
   llame?** Un diálogo abierto, una pantalla de opciones, un callback de confirmación. Compila
   perfecto y revienta —o peor, no revienta y lee basura— cuando la instancia ya no está.
6. **¿Algún contador de vida o temporizador está detrás de una guarda que puede quedarse en
   `false` para siempre?** *(Fallo real: las partículas se congelaban eternamente en la pantalla
   de derrota, porque su guarda era `if (!global.juego_activo) exit;` y su contador de vida
   nunca bajaba. Justo en las dos pantallas que más se miran.)*

> 💡 **Cómo se usa.** No es una lectura general del código: es **seis pasadas dirigidas**, una
> por pregunta, sobre los archivos donde cada una puede aplicar. Buscar una familia concreta de
> fallo encuentra mucho más que releer buscando «errores», que es la forma de no ver ninguno.

> ⚠️ **Esto no sustituye a ejecutar.** Lo que no se puede saber leyendo —si se ve bien, si se
> siente bien, si el audio se solapa, si el rendimiento aguanta— sigue sin saberse, y hay que
> **decirlo explícitamente** al entregar en vez de dar el juego por probado. La lista de qué
> depende de vista, oído o hardware está en
> [`12 · 09 §4.2`](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md).

---

## 9 · QA manual: el trabajo que no se automatiza

### 9.1 El plan de pruebas por sistema

Un plan de pruebas es una tabla. Ni más ni menos. Una por sistema, versionada junto al código:

```markdown
## Plan de pruebas · Sistema de guardado · v0.4.2

| # | Caso | Pasos | Resultado esperado | Plataformas | Estado |
|---|---|---|---|---|---|
| G1 | Guardado normal | Jugar 5 min → menú → Guardar | Aparece la ranura con fecha y nivel | Win/Mac/Linux | ✅ |
| G2 | Carga normal | Guardar → salir → abrir → Cargar | Posición, vida e inventario idénticos | Win/Mac/Linux | ✅ |
| G3 | Sobrescribir | Guardar en ranura 1 dos veces | La segunda sustituye a la primera, sin duplicar | Win | ✅ |
| G4 | Partida de versión vieja | Copiar un `.sav` de la v0.3 y cargar | Migra o avisa; **nunca** cierra el juego | Win | ⚠️ avisa mal |
| G5 | Fichero corrupto | Editar el `.sav` y romper el JSON | Mensaje claro y vuelta al menú | Win | ❌ BUG-118 |
| G6 | Disco lleno | Llenar el volumen y guardar | Avisa y conserva la partida anterior | Win | ⬜ sin probar |
| G7 | Cierre durante el guardado | Matar el proceso mientras guarda | La partida anterior sigue intacta | Win | ⬜ sin probar |
```

Cuatro reglas para que el plan sirva: los **pasos** tienen que ser ejecutables por alguien que
no escribió el código («probar el guardado» no es un caso de prueba); el **resultado esperado**
es una frase falsable («funciona bien» no lo es); cada caso tiene un **identificador estable**
(`G4`) que citan los informes de bug; y los casos en rojo **enlazan al bug**, no lo describen.

### 9.2 La matriz de plataformas

El plan dice *qué* probar; la matriz dice *dónde*. Prueba siempre los **extremos**, no la
media:

| Eje | Extremos que hay que cubrir |
|---|---|
| Sistema | El más viejo que soportas y el más nuevo |
| Resolución | La mínima declarada (¿cabe el HUD?) y 4K (¿se ve el pixel art?) |
| Proporción | 16:9, 16:10, 21:9 y una vertical si vas a móvil |
| Entrada | Teclado, mando Xbox, mando PlayStation, mando genérico barato |
| Idioma | El más largo (alemán) y uno con caracteres no latinos, si localizas |
| Hardware | El portátil integrado más flojo que tengas a mano |
| Ventana | Ventana, pantalla completa, **cambiar entre ambas**, alt-tab, minimizar |

> ⚠️ **Perder y recuperar el foco de la ventana es donde mueren las surfaces.** Está en la
> checklist de [`05 · 04`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) §8
> y es el caso que más se olvida.

### 9.3 *Monkey testing*: romperlo a lo bruto

Consiste en hacer lo que ningún diseñador previó: pulsar todo a la vez, entrar y salir del menú
cincuenta veces seguidas, mantener dos direcciones opuestas, pausar durante una cinemática,
guardar mientras el jefe muere. Es sorprendentemente eficaz porque ataca **las transiciones**,
que es donde vive el estado inconsistente.

Se puede automatizar en parte con un objeto que pulse teclas al azar en una room de prueba —
un mono de verdad— y dejarlo corriendo veinte minutos con `exception_unhandled_handler()`
puesto. Si vuelves y hay un `crash.log`, has ganado el día.

### 9.4 La sesión larga (*soak test*)

Hay fallos que solo aparecen a la hora y media: fugas de memoria, contadores que desbordan,
listas que crecen sin límite, precisión que se degrada. La prueba es dejar el juego corriendo
en un bucle y **mirar la ventana Memory del Debug Overlay** al principio y al final.

| Qué mirar | Síntoma malo |
|---|---|
| **Allocated memory** | Sube y nunca baja tras cambiar de room |
| Número de instancias | Crece sin que aparezcan enemigos nuevos |
| Estructuras de datos | Cada `ds_*_create()` sin su `ds_*_destroy()` |
| Surfaces | Se recrean pero no se liberan |
| FPS | Bajan poco a poco durante la sesión |

La tabla de qué hay que destruir a mano —y por qué va en **Clean Up** y no en Destroy— está en
[`01 · 15`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md) §8. Es la
primera parada cuando la memoria sube.

### 9.5 La checklist de release

La checklist de publicación (nombre de producto, icono, versión, config Release, YYC, texture
groups, tamaño del paquete, portadas 16:9 para GX.games) está completa en
[`05 · 02 — Publicar y exportar`](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md) §4.4
y en [`01 · 16`](../01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md); el calendario y las
puertas del proyecto, en [`13 · 11 — Producción, alcance y lanzamiento`](11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md). **No lo repito.**
Lo que añade QA por encima de aquello es solo esto:

- [ ] Las teclas del **modo QA** están apagadas en la configuración de release.
- [ ] Los **logs de depuración** no escriben a disco en cada frame en release.
- [ ] Los **ficheros dorados** de prueba no se han empaquetado con el juego.
- [ ] El plan de pruebas de cada sistema está **sin casos en rojo ni sin probar**.
- [ ] El **build empaquetado** (no el Run) se ha jugado de principio a fin al menos una vez.

---

## 10 · Playtesting

Aquí se acaba la ingeniería y empieza la observación. El playtesting no busca defectos de
código: busca **defectos de comunicación** entre lo que diseñaste y lo que el jugador entiende.

### 10.1 El protocolo — y dónde está explicado

El protocolo completo —la postura de Valve («los diseños son hipótesis, los playtests son
experimentos»), la regla de **no ayudar ni explicar**, qué preguntar y qué no, el
*think-aloud*, la regla de los cinco usuarios de Nielsen y la tabla de registro por minuto—
está desarrollado en [`13 · 01 — Diseño de juego`](01%20-%20Dise%C3%B1o%20de%20juego%20-%20core%20loop%2C%20mec%C3%A1nicas%2C%20balance%20y%20dificultad.md) §7. **No lo repito.**

Lo que añade este documento son las dos cosas que allí no caben, porque son de QA y no de
diseño:

1. **Grábalo siempre.** La pantalla como mínimo; la cara y las manos si puedes. Un playtest sin
   grabación es un playtest que solo existe en tus notas, y las notas están sesgadas por lo que
   ya creías. Si además dejas puesto `debug_input_record()` (§7.1), tienes la sesión entera
   reproducible dentro del propio motor.
2. **Cuántos, según qué quieras saber.** ⚠️ La regla de los cinco de Nielsen sirve para
   **descubrir problemas de usabilidad**, no para medir opiniones. Games User Research matiza
   los números para videojuegos: **~6 jugadores para descubrir problemas**, **~12 para perfilar
   tipos de jugador** y **~100 si quieres medir opiniones de forma cuantitativa**. Un juego es
   bastante más complejo que la web sobre la que Nielsen hizo el estudio.

### 10.2 Qué medir

Anota **conducta observable**, no impresiones:

| Métrica | Qué revela |
|---|---|
| Tiempo por nivel / por sala | Dónde se atasca |
| Muertes por zona | Picos de dificultad |
| Muertes en el mismo sitio ≥ 3 veces | Un problema de comunicación, no de dificultad |
| Momento del abandono | Dónde se pierde el interés |
| Menús abiertos y cerrados sin usar | Interfaz que no se entiende |
| Mecánicas nunca usadas | O no las descubre, o no le sirven |
| Frases espontáneas («¿y ahora qué?») | Oro puro; transcríbelas literales |
| Dónde mira cuando está perdido | Qué esperaba que fuera la pista |

### 10.3 De la observación a la tarea

El error clásico es aceptar la solución que propone el jugador. **El jugador es un sensor
excelente y un diseñador mediocre.** El proceso correcto tiene tres pasos:

```
OBSERVACIÓN   4 de 5 jugadores dieron vueltas >90 s en la sala 3 antes de encontrar la palanca
      ↓
DIAGNÓSTICO   La palanca no contrasta con el fondo y no hay ninguna pista que dirija la mirada
      ↓
TAREA         [ ] Iluminar la palanca de la sala 3 y añadir un rastro de partículas hacia ella
              Criterio de aceptación: en la próxima tanda, ≥4 de 5 la encuentran en <30 s
```

Lo importante es el **criterio de aceptación**: sin él, la tarea no se puede cerrar y volverá
en la siguiente tanda disfrazada de otra cosa. Y recuerda la regla de conteo de
[`13 · 01`](01%20-%20Dise%C3%B1o%20de%20juego%20-%20core%20loop%2C%20mec%C3%A1nicas%2C%20balance%20y%20dificultad.md) §7.3 — *1 de 5 es ruido, 3 de 5 es el diseño*: no conviertas en tarea
lo que le pasó a una sola persona.

### 10.4 Telemetría mínima

Valve instrumentó el juego para grabar automáticamente «position, health, weapons, time y
cualquier actividad importante: guardar, morir, ser herido, resolver un puzle, luchar contra
un monstruo». Eso lo puedes tener en GML en veinte líneas:

```gml
/// @desc Registra un suceso de telemetría en memoria. Barato: no toca disco.
/// @param {String} _suceso
/// @param {Struct} [_datos]
function telemetria_anotar(_suceso, _datos = {})
{
    if (!variable_global_exists("telemetria")) { global.telemetria = []; }

    array_push(global.telemetria, {
        t:       get_timer() / 1000000,        // segundos desde el arranque
        sala:    room_get_name(room),
        suceso:  _suceso,
        datos:   _datos
    });
}

// Uso
telemetria_anotar("muerte", { x: obj_jugador.x, y: obj_jugador.y, causa: "pinchos" });
telemetria_anotar("nivel_completado", { intentos: intentos });
```

El volcado a JSON al terminar la sesión —y el resto del diseño de qué medir— está en
[`13 · 01 — Diseño de juego`](01%20-%20Dise%C3%B1o%20de%20juego%20-%20core%20loop%2C%20mec%C3%A1nicas%2C%20balance%20y%20dificultad.md); aquí basta con saber que
`json_stringify(global.telemetria, true)` escrito con `file_text_write_string()` te deja un
fichero que abres en una hoja de cálculo.

> ⚠️ Si vas a enviar telemetría por red, eso ya es tratamiento de datos personales: pide
> consentimiento y no guardes nada que identifique a la persona.

---

## 11 · Bugs: informar, clasificar y saber de quién es

### 11.1 La plantilla de un informe reproducible

Un informe sin pasos de reproducción es una queja. La plantilla mínima:

```markdown
## BUG-118 · El juego se cierra al cargar una partida con el JSON roto

**Gravedad:** Alta (pérdida de progreso)   **Frecuencia:** Siempre (5/5)
**Versión:** 0.4.2 (build 214)   **Config:** Default   **Runtime:** vm
**Plataforma:** macOS 26.0, Apple Silicon   **Entrada:** teclado

### Pasos
1. Jugar hasta el nivel 2 y guardar en la ranura 1.
2. Cerrar el juego.
3. Abrir `~/Library/Application Support/mijuego/save_1.json` y borrar la última `}`.
4. Abrir el juego → Continuar.

### Resultado esperado
Mensaje «La partida está dañada» y vuelta al menú principal.

### Resultado real
Ventana de excepción no controlada y cierre. `partida.log` adjunto, línea 412:
`json_parse :: unexpected end of input`.

### Adjuntos
`save_1.json` (el corrupto) · `partida.log` · `incidencia_tester_2317.png` ·
`bug_0118.data` (grabación de entrada para `debug_input_playback`)

### Notas
No pasa con la ranura vacía. Regresión: en 0.4.0 sí avisaba; sospecho del cambio en
`cargar_partida()` del commit a3f1e2.
```

Lo que hace que un informe sea bueno: **la versión y la plataforma exactas**, **pasos
numerados que empiezan desde el arranque del juego**, **la diferencia entre esperado y real
en dos frases**, y **adjuntos** — con la grabación de entrada de §7.1, el bug se reproduce
solo.

### 11.2 Triaje: gravedad × frecuencia

No todos los bugs se arreglan, y desde luego no en el mismo orden. Se cruzan dos ejes:

| | **Siempre** | **A veces** | **Raro** |
|---|---|---|---|
| **Bloqueante** (no se puede seguir jugando, se pierde la partida) | 🔴 P0 · ahora | 🔴 P0 · ahora | 🟠 P1 |
| **Grave** (rompe un sistema, hay rodeo) | 🟠 P1 | 🟠 P1 | 🟡 P2 |
| **Molesto** (feo, confuso, no bloquea) | 🟡 P2 | 🟡 P2 | 🟢 P3 |
| **Cosmético** (un píxel, una tilde) | 🟢 P3 | 🟢 P3 | ⚪ backlog |

Dos matices que la tabla no dice: **la pérdida de progreso siempre sube un escalón** (un bug
de guardado «raro» sigue siendo P0) y **un bug visible en el primer minuto de juego también**,
aunque sea cosmético — es lo primero que verá quien pruebe la demo.

### 11.3 ¿Es mi bug o del runtime?

Antes de pasar tres días peleándote con un comportamiento absurdo, comprueba si ya está
reportado. El canal oficial es **[GameMaker-Bugs](https://github.com/YoYoGames/GameMaker-Bugs)**,
el repositorio público de seguimiento al que envía el *bug reporter* del menú *Help* del IDE.
Ficha en [`07 · 01`](../07%20-%20Ecosistema/01%20-%20GitHub%20-%20organizaci%C3%B3n%20YoYoGames.md).

El protocolo para distinguirlos:

1. **Busca en GameMaker-Bugs** el nombre de la función y el síntoma.
2. **Búscalo en GM-TestFramework**: si YoYo tiene una suite para esa función
   (`projects/xUnit/scripts/Basic*TestSuite/`), lee qué comportamiento da por correcto.
3. **Reduce el caso** a un proyecto nuevo con lo mínimo que lo reproduce. Nueve de cada diez
   veces el bug se evapora aquí, y ahí has aprendido que era tuyo.
4. **Prueba en VM y en YYC** (`--runtime vm` y `--runtime native`). Que se comporte distinto
   en los dos es una señal fuerte de bug del motor.
5. Si sobrevive a todo: **repórtalo con el proyecto reducido adjunto**, y —si te apetece
   ayudar— manda la suite de prueba como *pull request* a GM-TestFramework. Es literalmente
   para lo que existe ese repositorio.

---

## 12 · Checklist

```
CÓDIGO TESTEABLE
[ ] Las reglas están en funciones puras, fuera de los eventos; el Draw solo dibuja.
[ ] El azar y el "ahora" entran por argumento, no por random() ni current_time.

PRUEBAS AUTOMÁTICAS
[ ] Existe una tanda que corre con un solo comando.
[ ] Termina con game_end(0) en verde y game_end(1) en rojo.
[ ] CI lee ###game_end###0 de la salida (gm-cli run NO devuelve el código).
[ ] Hay prueba de ida y vuelta del guardado y de carga de una partida vieja.
[ ] La generación procedural tiene prueba de determinismo por semilla.
[ ] Hay al menos una prueba de invariante ("esto no puede pasar nunca").

COMPILACIÓN
[ ] gm-cli compile --errors-only sale con 0 antes de cada commit (iterar rápido).
[ ] Antes de dar el juego por terminado, se compiló también SIN --errors-only y se
    leyó la salida completa buscando WARNING — el flag anterior los silencia por
    completo, incluido el de un included file que no llegó al paquete (12/09 §0 Trampa 8).
[ ] Se compila para todas las plataformas objetivo, no solo la tuya.
[ ] Se ha probado el paquete (gm-cli package), no solo el Run — y se ha abierto el .zip/
    contenido del build para confirmar que los archivos de datos están dentro de verdad.
[ ] Se ha medido en --runtime native, no en vm.

DEPURACIÓN
[ ] exception_unhandled_handler() volcando a fichero en los builds de tester.
[ ] Log con niveles, y el nivel sube en la configuración Release.
[ ] Modo QA detrás de un #macro por configuración, apagado en release.
[ ] Se sabe grabar y reproducir input para adjuntarlo a los informes.

QA MANUAL Y PLAYTESTING
[ ] Cada sistema tiene su plan de pruebas en una tabla, versionado.
[ ] La matriz cubre los extremos: resolución mínima, 4K, mando barato, alt-tab.
[ ] Sesión larga mirando la ventana Memory al principio y al final.
[ ] Al menos 5 personas que no habían visto el juego, observadas en silencio.
[ ] Cada observación se convirtió en tarea con criterio de aceptación.

«COMPILA LIMPIO» NO ES «FUNCIONA» (§8.6, §8.7 y §8.8)
[ ] Al menos una captura de pantalla por flujo/pantalla nuevo, ABIERTA y mirada de verdad —
    no solo comprobada por que screen_save() no dio error o el PNG existe en disco.
[ ] El guardado se verificó MATANDO el proceso del juego por completo y volviendo a lanzarlo,
    no solo con save_game() == true en el mismo run.
[ ] El guion de humo de §8.7.6 corrió de punta a punta: lanzar, ###humo_captura###, mirar el
    PNG, ###humo_guardado### OK en la segunda fase, y ps -ef | grep -i runner en vacío al final.
[ ] En Mac, si algún juicio depende de POSICIÓN vertical (arriba/abajo, solapamiento con un
    borde), se contrastó al menos una vez una captura de screen_save() contra screencapture
    real — screen_save() puede invertir la imagen mientras la ventana se ve bien (Trampa 13
    de 12/09 §0, §7.3 y §8.7.3 de este documento).
```

---

## 12 bis · Los bugs que solo aparecen cuando dos estados se cruzan

> **De dónde sale esta sección.** De contrastar nuestro checklist contra
> `game-quality-gates`, una skill de gamedev genérica —web y móvil, no GameMaker—
> instalada en la máquina del autor, cuyo material dice estar destilado de setenta y
> tantos bugs reales. Su frase de cabecera merece robarse entera:
>
> > Los bugs no salen de las funciones sueltas, salen de la **interacción entre
> > estados**. Cada mecánica funciona sola; se rompen en combinación.
>
> Eso explica por qué el §12 de arriba, que es un buen checklist de *método de
> prueba*, no las caza: cada casilla mira una cosa a la vez. Lo que sigue es esa idea
> traducida a GameMaker —donde algunas de sus reglas no aplican y otras muerden mucho
> más fuerte—, escrito de cero: la skill de origen **no declara licencia**, así que se
> cita la idea y no se copia el texto.

### 12 bis.1 · Un solo sitio donde se limpia

Un juego se sale de una partida por más puertas de las que parece: morir, terminar el
nivel, volver al menú, cerrar desde la pausa, `room_goto` de un atajo de depuración.
Cada puerta que limpia por su cuenta es una puerta que se olvidará de lo próximo que
añadas.

**Una función, un sitio.** `partida_limpiar()` (o el nombre que uses) que borre en
orden fijo: estructuras de datos → temporizadores → interfaz → proyectiles y
partículas → enemigos. Todas las salidas la llaman. **Mecánica nueva = una línea más
ahí dentro**, nunca una limpieza esparcida por cinco eventos.

En GameMaker el sitio natural es el evento **Clean Up**, que se dispara *tanto* al
destruir la instancia *como* al terminar la sala — las dos puertas por las que se
escapan las fugas.

### 12 bis.2 · Lo que GameMaker **no** recoge solo

Aquí la traducción no es literal: en un motor con recolector de basura, un mapa que
nadie mira desaparece. En GML **no**. Un `ds_map` vive hasta que alguien llama a
`ds_map_destroy`, y si nadie lo hace, cada entrada en la sala deja otro. El juego va
perfecto en la demo de dos minutos y se arrastra a la media hora.

Se crea a mano y se destruye a mano:

| Se crea con | Se destruye con |
|---|---|
| `ds_map_create` · `ds_list_create` · `ds_grid_create` · `ds_stack_create` · `ds_queue_create` · `ds_priority_create` | `ds_*_destroy` |
| `surface_create` | `surface_free` |
| `part_system_create` / `part_system_create_layer` · `part_type_create` · `part_emitter_create` | `part_*_destroy` |
| `buffer_create` | `buffer_delete` |
| `vertex_create_buffer` | `vertex_delete_buffer` |
| `audio_emitter_create` | `audio_emitter_free` |
| `time_source_create` | `time_source_destroy` |
| `sprite_add` · `font_add` | `sprite_delete` · `font_delete` |

**Los structs y los arrays sí se recogen solos** — esa es justamente la razón por la
que conviene preferirlos a las `ds_*` en código nuevo (`08 · 15`). Las `ds_*` siguen
haciendo falta para lo que ellas hacen mejor: rejillas grandes, colas de prioridad.

> 🤖 **Esto ya no es un consejo, es una comprobación.**
> `python3 "$BIB/_indice/auditar-juego-completo.py" <proyecto>` lista cada familia que
> tu proyecto crea y nunca destruye en ninguna parte. Está calibrado para no dar
> falsos positivos: solo habla si el destructor **no aparece ni una vez** en todo el
> proyecto, y a `sprite_add`, `font_add` y `time_source_create` les exige aparecer más
> de una vez antes de decir nada, porque cargar una fuente al arrancar y usarla toda la
> partida es legítimo y no crece. Medido contra los 22 juegos completos de
> `11 - Código descargado/juegos_y_motores` para fijar ese umbral.

### 12 bis.3 · La alarma muere contigo; el *time source*, no

Una alarma pertenece a su instancia: si la instancia se destruye, la alarma se va con
ella. Es cómodo y es la razón por la que casi nadie piensa en esto. Pero
`time_source_create` **no** pertenece a nadie: sigue viva, y su función de vuelta puede
ejecutarse cuando el objeto que la creó ya no existe, tocando variables de una
instancia muerta. Guárdate el identificador y destrúyelo en **Clean Up**.

### 12 bis.4 · Copia los datos ANTES de destruir

El patrón de siempre: la bala muere y quiere dejar chispas de su color en su posición.

```gml
// ✗ leer del difunto
instance_destroy();
efecto_chispas(x, y, color);   // en el evento Destroy aún funciona…
                               // …pero llamado desde FUERA, sobre un id ya muerto, no
// ✓ copiar primero, destruir después
var _x = x, _y = y, _c = color;
instance_destroy();
efecto_chispas(_x, _y, _c);
```

Y su hermano mayor, que ya nos mordió y está documentado en `06 - Assets y Scripts/scr_pool.gml`:
**`instance_exists()` devuelve `false` sobre una instancia desactivada**. Comprobar
existencia antes de reactivar da siempre «no existe», y el objeto se pierde para
siempre sin un solo error. Primero `instance_activate_object()`, después preguntar.

### 12 bis.5 · Modificar un atributo sin mirar los efectos activos

El clásico: el jugador tiene una ralentización activa, entra en una zona de barro que
«asegura» una velocidad mínima, y el `max()` borra la ralentización.

```gml
// ✗ el suelo pisa el efecto de estado
velocidad = max(velocidad, VELOCIDAD_BASE);
// ✓ la referencia es la base YA modificada por los efectos activos
velocidad = max(velocidad, velocidad_base_actual);
```

Cualquier código que toque velocidad, ataque, defensa o tamaño tiene que preguntar
primero qué efectos temporales hay puestos. El sistema de efectos de estado está en
[`04 · 32`](../04%20-%20Recetas%20por%20género/32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md);
esta es la regla que hace que se use de verdad.

### 12 bis.6 · La lista, en una tanda

Antes de dar por terminada una versión, con el juego **en marcha**:

```
[ ] Cada salida de partida (morir, completar, menú, pausa→salir) llama a la MISMA
    función de limpieza.
[ ] Toda ds_*/surface/buffer/partícula/vertex buffer/emisor creada tiene su destructor
    en algún Clean Up  →  lo comprueba auditar-juego-completo.py.
[ ] Todo time_source_create guardado y destruido; ninguna función de vuelta toca una
    instancia que puede haber muerto.
[ ] Los datos se copian a variables locales antes de instance_destroy().
[ ] Nada reactiva instancias sin instance_activate_object() antes de instance_exists().
[ ] Ningún cambio de atributo ignora los efectos de estado activos.
[ ] Entrar y salir de la misma sala veinte veces seguidas: la memoria del depurador
    vuelve al mismo sitio, no sube en escalera.
```

Ese último punto es el que los caza casi todos, y no lo automatiza nadie: se entra y
se sale veinte veces mirando la ventana **Memory** del depurador. Si sube en escalera y
no baja, algo de la tabla de 12 bis.2 se está quedando dentro.

---

## 13 · Errores clásicos y cómo evitarlos

| Error | Por qué duele | Qué hacer |
|---|---|---|
| **Probar solo con el Run del IDE** | El runner perdona rutas, assets descartados y permisos que el ejecutable no | `gm-cli package` y jugar el paquete antes de cada entrega |
| **Tests que dependen de `room_speed`** | `room_speed` está **obsoleta** en 2026 y además ata la prueba a los FPS | Usa `game_get_speed(gamespeed_fps)` en el juego y **pásale los pasos como argumento** a la función que pruebas |
| **Tests que dibujan** | Fuera de un evento Draw no miden nada, y dentro no puedes afirmar sobre píxeles | Prueba la **geometría calculada** (§2.3), no el resultado dibujado |
| **No resetear el estado global entre pruebas** | La prueba 7 pasa sola y falla en la tanda; una hora perdida | Un `setUp` que reinicializa `global.*`, o mejor: que las funciones no lean globales |
| **No probar el guardado** | El bug más caro que existe: destruye partidas ajenas y aparece semanas después | La prueba de ida y vuelta de §5.2, desde el primer día |
| **Fiarse del código de salida de `gm-cli run`** | Devuelve `0` aunque las pruebas fallen: tu CI estará verde siempre | Leer `###game_end###0` de la salida (§3.4) |
| **Usar `random()` en una prueba** | Falla un día de cada veinte y nadie sabe por qué | Fuente de azar inyectada con semilla fija (§2.2) |
| **Comparar reales con `==`** | `100 * (1 - 0.9)` no es `10`. Verificado en este documento | Compara con tolerancia, o reordena la expresión para no restar cerca de cero |
| **Un solo tester: tú** | Ya sabes dónde está la palanca. No puedes perderte | Cinco personas que no han visto el juego |
| **Ayudar durante el playtest** | Destruyes la única medida que te interesa | Silencio. Preguntas al final |
| **Dejar las teclas de QA en el build final** | Un jugador encuentra el modo dios y lo cuenta | `#macro Release:MODO_QA false` |
| **Escribir el log a disco cada frame** | Abre y cierra el fichero 60 veces por segundo | Acumula en un array y vuelca cada N segundos |
| **Informes sin pasos** | «Se cierra a veces» no es un bug, es una sensación | La plantilla de §11.1, con versión, plataforma y adjuntos |

---

## 14 · Seguridad y anti-trampas

Este documento ha hablado de probar que el juego funciona; esta sección habla de probar que
**el jugador no lo está engañando**. Hoy el tema está repartido en tres sitios que no se
citan entre sí: la ofuscación de guardados de
[`01 · 14 — Persistencia y archivos`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) §12,
el «nunca confíes en el cliente» de
[`04 · 14 — Multijugador`](../04%20-%20Recetas%20por%20g%C3%A9nero/14%20-%20Multijugador.md) §2.2,
y nada sobre qué hace de verdad quien te quiere hacer trampa en un ranking. Esta sección los
une y cierra el hueco: leaderboards de un jugador, edición de memoria, y qué defensa es real
y cuál es teatro.

### 14.1 El hecho del que se deriva todo lo demás

**El cliente es territorio enemigo.** [`04 · 14`](../04%20-%20Recetas%20por%20g%C3%A9nero/14%20-%20Multijugador.md) §2.2
lo dice para el multijugador en tiempo real: el cliente envía intenciones, el servidor decide.
El mismo principio se aplica sin cambiar una palabra a un **ranking de un jugador**: no hay
otro jugador al que hacerle trampa, pero sí una tabla de clasificación compartida, y el
cliente que envía su propia puntuación **es exactamente tan poco fiable** como el que envía
"he matado a ese" en un shooter.

La consecuencia práctica: cuánto inviertas en anti-trampas depende de si algo que ve **otra
persona** depende del dato.

| Tu juego tiene… | ¿Vale la pena invertir? |
|---|---|
| Solo progreso local, sin tabla compartida | No. El único perjudicado de hacerse trampa a sí mismo es el propio jugador |
| Logros de plataforma (Steam, Game Center) | Poco: valida lo mínimo, la plataforma ya limita el daño |
| **Tabla de clasificación pública** | Sí: es la única cara visible de tu juego a la que **todo el mundo** cree |
| Multijugador competitivo | Sí, y no es opcional: ya está resuelto en 04/14 §2 |

### 14.2 Antes de aceptar una puntuación: detectar lo imposible

Un backend de leaderboard no necesita entender tu juego para rechazar la mitad de las
trampas: le basta con saber qué es **físicamente imposible** dado el diseño.

```gml
// ═══════════ scr_validar_puntuacion ═══════════

/// @func puntuacion_es_plausible(_puntuacion, _tiempo_segundos, _nivel)
/// @desc Rechaza un envío evidentemente imposible ANTES de tocar el backend de verdad.
///       No demuestra que la partida sea legítima — eso es 14.3 — pero descarta gratis
///       la trampa perezosa: puntuaciones inventadas a mano o pegadas desde otra partida.
/// @param {Real} _puntuacion
/// @param {Real} _tiempo_segundos   Duración real de la partida, medida por el servidor.
/// @param {Real} _nivel             Para comparar contra el máximo teórico de ESE nivel.
/// @returns {Bool}
function puntuacion_es_plausible(_puntuacion, _tiempo_segundos, _nivel)
{
    if (!is_numeric(_puntuacion) || _puntuacion < 0)   return false;
    if (_tiempo_segundos <= 0)                         return false;

    // Límite de diseño: nadie puede sacar más de N puntos por segundo aunque juegue perfecto.
    var _maximo_por_segundo = 12;
    if ((_puntuacion / _tiempo_segundos) > _maximo_por_segundo) return false;

    // Límite absoluto: el nivel tiene un máximo teórico (todos los coleccionables + bonus).
    var _maximo_del_nivel = nivel_puntuacion_maxima(_nivel);   // tu propia tabla de diseño
    if (_puntuacion > _maximo_del_nivel)                       return false;

    return true;
}
```

**Otras señales que cuestan cero calcular** y descartan casi todo el ruido: un
`_tiempo_segundos` menor que el tiempo mínimo humanamente posible para completar el nivel; una
marca de tiempo de envío **anterior** a la de inicio de partida; el mismo identificador de
partida enviado dos veces (reenvío del mismo paquete capturado); y una puntuación que no
cambia nunca de las últimas cifras — señal de que alguien genera valores con una plantilla en
vez de jugar.

> ⚠️ Nada de esta sección **prueba** que la partida sea legítima: solo descarta lo obviamente
> falso. Alguien que se toma la molestia de simular un ritmo de juego "razonable" pasa estos
> filtros sin jugar ni un segundo. Para eso hace falta 14.3.

### 14.3 Replay firmado: la única verificación real para un ranking de un jugador

Sin otro jugador al que compararle el resultado en directo, la única forma de saber si una
puntuación de un jugador es legítima es que el **servidor rejuegue la partida** y compruebe
que le sale lo mismo. Esto no es una idea nueva de esta sección: es exactamente el mismo
determinismo que ya exige la prueba de generación procedural de §5.3 — **mismo estado inicial
+ mismos inputs = mismo resultado** — aplicado a un marcador en vez de a un mapa.

El cliente graba **intenciones**, nunca el resultado — la misma regla de
[`04 · 14`](../04%20-%20Recetas%20por%20g%C3%A9nero/14%20-%20Multijugador.md) §2.2 —, y la
puntuación final que el propio cliente afirma haber sacado va **junto** al replay, no en su
lugar:

```gml
// ═══════════ scr_replay_firmado ═══════════

/// @func replay_iniciar(_semilla)
/// @desc Empieza a grabar una partida verificable. La semilla fija el azar (misma
///       AzarReproducible de §2.2), así que el servidor puede reproducir exactamente
///       la misma partida a partir de los mismos eventos.
function replay_iniciar(_semilla)
{
    global.replay = { semilla: _semilla, eventos: [], frame: 0 };
}

/// @desc Anota una intención del jugador. Llamarlo solo cuando ocurre algo de verdad
///       (una tecla, una decisión), nunca cada frame: el paquete sería enorme.
/// @param {String} _accion
function replay_anotar(_accion)
{
    array_push(global.replay.eventos, { frame: global.replay.frame, accion: _accion });
}

/// @func replay_cerrar(_puntuacion_declarada)
/// @desc Cierra la grabación y la sella con un hash.
///       ⚠️ El hash NO demuestra que la partida sea legítima: solo que el paquete no se
///       corrompió ni se manipuló de camino al servidor. Quien lo demuestra es replay_verificar().
/// @returns {Struct}
function replay_cerrar(_puntuacion_declarada)
{
    var _r = global.replay;
    _r.puntuacion = _puntuacion_declarada;
    _r.hash = sha1_string_utf8(json_stringify(_r.eventos) + string(_r.semilla) + string(_r.puntuacion));
    return _r;
}

/// @func replay_verificar(_replay, _estado_inicial, _simular_frame)
/// @desc Comprueba el sello de integridad, rejuega el replay con la MISMA regla pura del
///       juego (§2.1) y compara el resultado. Esto es lo que de verdad separa una
///       puntuación real de una inventada.
///       ⚠️ Antes esta función re-simulaba y comparaba la puntuación, pero nunca leía
///       `_replay.hash`: el sello que calcula replay_cerrar() quedaba muerto y cualquier
///       paquete corrupto o retocado en tránsito se daba por bueno. Ahora se compara.
/// @param {Struct}   _replay          Lo recibido del cliente (semilla, eventos, puntuación, hash).
/// @param {Function} _estado_inicial  (_azar) → estado de partida en el frame 0.
/// @param {Function} _simular_frame   (_estado, _accion, _azar) → nuevo estado. Función pura,
///                                    la misma que usarías en tus pruebas de §2.1-§2.2.
/// @returns {Bool}
function replay_verificar(_replay, _estado_inicial, _simular_frame)
{
    // 1. Integridad: el hash recibido debe coincidir con el que sale de recalcular la
    //    MISMA fórmula que usó replay_cerrar(). Si no coincide, el paquete se corrompió
    //    o se manipuló de camino al servidor: se rechaza sin gastar CPU en re-simular.
    var _hash_esperado = sha1_string_utf8(json_stringify(_replay.eventos) + string(_replay.semilla) + string(_replay.puntuacion));
    if (_hash_esperado != _replay.hash)
    {
        return false;
    }

    // 2. Autoridad: re-simular con la regla pura del juego y comprobar que la puntuación
    //    declarada es la que de verdad sale de jugar esos eventos desde esa semilla.
    var _azar   = new AzarReproducible(_replay.semilla);
    var _estado = _estado_inicial(_azar);

    for (var _i = 0; _i < array_length(_replay.eventos); _i++)
    {
        _estado = _simular_frame(_estado, _replay.eventos[_i].accion, _azar);
    }

    return (_estado.puntuacion == _replay.puntuacion);
}
```

**Este servidor de verificación no necesita ser GameMaker.** Basta con que reimplemente la
misma regla pura (`_simular_frame`) en el lenguaje que sea — es justo el tipo de función que
§2.1 ya te pide extraer de las instancias, y por eso es portable sin arrastrar el motor entero.
Si tu backend real ya es Colyseus ([`12 · 04`](../12%20-%20Utilidades%20e%20integraciones/04%20-%20Multijugador%20y%20red.md) §2),
la re-simulación vive de forma natural en esa misma sala de Node.js.

> ⚠️ Reejecutar el replay tiene un coste real de CPU en el servidor. Para un juego con miles
> de envíos diarios, verifica solo una muestra aleatoria y los récords que entran en el
> **top N** de la tabla — es donde de verdad importa que no haya trampa.

### 14.4 Editar la memoria en caliente: qué hace de verdad un Cheat Engine

Nada de lo anterior existe porque alguien vaya a **leer tu código GML**. Existe porque
cualquiera puede abrir un editor de memoria y tocar los números en caliente, sin ver una sola
línea de tu proyecto. Cheat Engine, la herramienta de referencia del género, se describe a sí
misma así:

> "Cheat Engine is a tool designed to help you with modifying single player games (…) It
> comes with a memory scanner to quickly scan for variables used within a game and allow you
> to change them, but it also comes with a debugger, disassembler, assembler, **speedhack**…"
> — [cheatengine.org/aboutce.php](https://www.cheatengine.org/aboutce.php)

El procedimiento habitual, y por qué funciona **da igual el lenguaje o motor**:

1. **Primer escaneo**: busca en toda la memoria del proceso el valor exacto que ves en
   pantalla (`vida = 100`).
2. **Cambias algo en el juego** (pierdes vida: ahora `vida = 82`) y pides un **escaneo
   siguiente** filtrando por ese nuevo valor, o simplemente por "ha bajado". Cada ronda reduce
   los candidatos de miles a unos pocos.
3. En dos o tres rondas queda **una dirección de memoria**. A partir de ahí, Cheat Engine
   **escribe directamente en esa dirección** — se salta por completo tu lógica de GML: no hay
   ninguna función que puedas llamar para impedirlo, porque no pasa por tu código.
4. El **speedhack** hace algo distinto y más sutil: intercepta las funciones de reloj del
   sistema operativo para que el juego **crea** que ha pasado más o menos tiempo del real. Un
   cooldown de 10 segundos se vacía en 2; un `_tiempo_segundos` que tu propio servidor mide de
   forma independiente (14.2) es la única defensa que el speedhack no puede tocar, porque el
   reloj falseado es el del cliente, no el tuyo.

**Por qué la ofuscación de guardados no toca este problema en absoluto:** `base64_encode()`
de [`01 · 14`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) §12 ofusca el
**fichero en disco**. Cheat Engine no lee el fichero: lee la **RAM en tiempo de ejecución**, y
ahí tu variable `vida` es un `Real` de GameMaker con su valor en claro, exista o no
codificación en el `.sav`. Son dos superficies de ataque completamente distintas, y proteger
una no protege la otra.

**Lo único que sube algo el coste** (no lo elimina): guardar valores sensibles con una
transformación que cambie cada partida — por ejemplo, sumar un desplazamiento aleatorio de
sesión y restarlo solo al leer, para que el número en RAM no coincida nunca literalmente con
el que se ve en pantalla. Un jugador con Cheat Engine y algo de paciencia lo rompe igual
(basta con seguir el puntero, no el valor), así que trátalo como un obstáculo para el curioso,
no como una defensa — el mismo matiz que la propia ofuscación de guardados.

### 14.5 Por qué la ofuscación de `01/14` §12 solo detiene al curioso

El propio documento ya lo dice sin adornos:

> "⚠️ base64 NO es seguridad. Solo evita la edición casual. Si necesitas proteger el guardado
> de verdad, tendrás que añadir verificación en servidor." —
> [`01 · 14 — Persistencia y archivos`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) §12

Vale la pena decir **por qué** exactamente: decodificar base64 no exige ni Cheat Engine ni
saber programar — cualquier buscador con "decodificar base64" lo resuelve en la misma pestaña
del navegador en la que se buscó. Lo único que impide es que alguien abra el `.sav` en un
editor de texto normal y vea `"vida":100` en claro y lo cambie por accidente o curiosidad. Es
la misma frontera que separa un guardado sin cifrar de uno con `md5_string_utf8()` de checksum
(01/14 §12): detecta la edición casual, no a quien la busca a propósito.

Es, de hecho, el mismo principio que 04/14 §2.2 aplicado a un fichero en vez de a un paquete
de red: **cualquier dato que viva en la máquina del jugador —en disco o en RAM— está bajo su
control total**, y ninguna cantidad de ofuscación cambia esa propiedad. Solo cambia cuánto
esfuerzo hace falta para saltársela.

### 14.6 La frase honesta

En un juego **de un jugador**, el anti-trampas no es rentable: el único perjudicado de un
guardado editado a mano es quien lo editó, y cada hora dedicada a ofuscarlo es una hora que no
se dedicó al juego. En un juego **con ranking o multijugador**, la única defensa real es
**el servidor**: validar lo imposible (14.2), re-simular lo dudoso (14.3), y decidir el
resultado sin preguntarle nunca al cliente qué cree que pasó. Todo lo demás —ofuscación,
variables desplazadas, anti-debug casero— no detiene a nadie decidido: solo sube el precio de
entrada para quien no pensaba currárselo de todas formas.

### 14.7 · *Rate limiting*: limitar cuántas veces se puede llamar al backend

Todo lo anterior (14.2-14.6) asume que la petición **llega** al backend. Sin límite de
frecuencia, alguien puede automatizar el envío — probar combinaciones hasta que una pase
`puntuacion_es_plausible()` (14.2), o simplemente saturar el servidor a peticiones por segundo,
una forma barata de *denial of service*. Es lógica de **servidor**, no de GameMaker — no hay
una función `network_*` o `http_*` que la resuelva desde el cliente —, pero se enlaza aquí
porque protege el mismo backend que valida 14.2 y re-simula 14.3, y porque
[`04 · 17`](../04%20-%20Recetas%20por%20g%C3%A9nero/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md) §6
la señala como la primera defensa que necesita un endpoint de login.

**El patrón estándar, en cualquier lenguaje de servidor:** un contador con ventana de tiempo
por identificador — IP, cuenta de usuario, o el token de sesión de
[`04 · 17`](../04%20-%20Recetas%20por%20g%C3%A9nero/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md) §6 —
que rechaza la petición cuando se supera un máximo dentro de la ventana:

```
si peticiones[identificador] en los últimos N segundos > máximo:
    responder 429 "Too Many Requests" y descartar
si no:
    incrementar el contador y procesar la petición normalmente
```

- **Por IP** es la primera barrera (barata, frena la automatización simple), pero una IP
  compartida (NAT de instituto, CGNAT — ver
  [`04 · 14`](../04%20-%20Recetas%20por%20g%C3%A9nero/14%20-%20Multijugador.md) §10.4) puede
  penalizar a jugadores legítimos que no tienen la culpa de compartir salida a internet. **Por
  cuenta de usuario/token** es más justo en cuanto ya hay autenticación (04/17 §6): cada
  jugador tiene su propio presupuesto, sin castigar a su vecino de red.
- **Valores de partida razonables para un envío de puntuación o guardado** (ajústalos a tu
  juego; no son una cifra medida contra un sistema real): unas pocas peticiones por minuto por
  cuenta —una partida no puede terminar más rápido que su duración mínima, que 14.2 ya usa para
  descartar tiempos imposibles— y un límite algo más laxo por IP, para no bloquear a quien
  comparte red con otros jugadores legítimos. Para un endpoint de **login**, el límite debe ser
  mucho más estricto (unos pocos intentos por minuto): ahí lo que se protege no es un
  leaderboard, es una contraseña frente a fuerza bruta.
- **Código HTTP estándar para la respuesta:** `429 Too Many Requests`, con una cabecera
  `Retry-After` si tu framework de servidor la soporta — así un cliente bien hecho sabe cuánto
  esperar en vez de reintentar en bucle y empeorar el problema.
- Si tu backend ya es **Colyseus**
  ([`12 · 04`](../12%20-%20Utilidades%20e%20integraciones/04%20-%20Multijugador%20y%20red.md) §2),
  el contador vive de forma natural en la misma sala de Node.js que ya re-simula 14.3; si usas
  un servicio gestionado —**Firebase**
  ([`12 · 03`](../12%20-%20Utilidades%20e%20integraciones/03%20-%20Integraciones%20con%20servicios.md) §5)
  o **PlayFab**
  ([`04 · 14`](../04%20-%20Recetas%20por%20g%C3%A9nero/14%20-%20Multijugador.md) §1.3)—, casi
  todos traen *rate limiting* de serie y solo hace falta activarlo, no escribirlo.

> ⚠️ El *rate limiting* del lado del **cliente** (por ejemplo, deshabilitar un botón unos
> segundos tras pulsarlo) es una mejora de UX, **no una defensa**: cualquiera que hable
> directamente con tu backend —sin pasar por tu juego compilado, con `curl` o Postman— lo
> ignora por completo. La cuenta atrás real vive siempre en el servidor, igual que la
> validación de 14.2 y la re-simulación de 14.3.

---

## Ver también

**En esta biblioteca**

- [`01 · 15 — Depuración y rendimiento`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md) — Feather, Debugger, Debug Overlay, vistas `dbg_*`, GC, limpieza de recursos. **La base de todo esto.**
- [`01 · 14 — Persistencia y archivos`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — guardado, JSON, buffers.
- [`01 · 16 — Exportar y publicar`](../01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md) — HTML5 y sus trampas.
- [`04 · 05 — Roguelike y generación procedural`](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md) — los algoritmos que hay que probar con semilla.
- [`04 · 14 — Multijugador`](../04%20-%20Recetas%20por%20g%C3%A9nero/14%20-%20Multijugador.md) §2.2 — «nunca confíes en el cliente», la base de §14 de este documento.
- [`04 · 17 — Interoperabilidad con la web`](../04%20-%20Recetas%20por%20g%C3%A9nero/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md) §6 — autenticación con tokens sobre HTTP, el primer endpoint que necesita el §14.7 de este documento.
- [`05 · 02 — Publicar y exportar`](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md) §4.4 — checklist de release y CI.
- [`05 · 04 — Convenciones y estilo GML`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) §7 y §8 — aserciones de producción y checklist antes de compilar.
- [`07 · 01 — GitHub · organización YoYoGames`](../07%20-%20Ecosistema/01%20-%20GitHub%20-%20organizaci%C3%B3n%20YoYoGames.md) — GM-TestFramework y GameMaker-Bugs.
- [`07 · 13 — GM CLI`](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md) — el CLI al completo.
- [`12 · 01 — Herramientas del flujo de trabajo`](../12%20-%20Utilidades%20e%20integraciones/01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md) §4 y §5 — tabla comparada de frameworks y de herramientas de depuración en runtime.
- [`12 · 09 — Manual del agente de IA`](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md) — las nueve trampas que hacen fracasar a un agente; la Trampa 3 (numeración de eventos Draw/Other) es la que explica por qué `subtype=gui_end` no da el evento real, la Trampa 9 y su [§9 ter](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#9-ter--forzar-un-eventnum-real-cuando-la-whitelist-de-subtype-es-cerrada) traen la receta que §8.7.2 usa para forzarlo de verdad con `RESOURCE SET`, y las Trampas 5 y 6 están detrás de §8.6.
- [`11 · _CATALOGO.md`](../11%20-%20C%C3%B3digo%20descargado/_CATALOGO.md) y [`_RUTAS.json`](../11%20-%20C%C3%B3digo%20descargado/_RUTAS.json) — dónde está cada repositorio clonado.
- [`AGENTS.md`](../AGENTS.md) §4 y §5 — las prohibiciones duras y el flujo de desarrollo.
- [`_indice/auditorias/r5-prueba-e2e.md`](../_indice/auditorias/r5-prueba-e2e.md) — la prueba end-to-end que motiva §8.6: los dos bugs que ningún checklist anterior habría cazado, y la ruta real de `game_save_id` que cita §8.7.3.

**En esta misma carpeta**

- [`13 · 01 — Diseño de juego`](01%20-%20Dise%C3%B1o%20de%20juego%20-%20core%20loop%2C%20mec%C3%A1nicas%2C%20balance%20y%20dificultad.md) — telemetría, métricas y volcado a JSON.
- [`13 · 05 — UI y UX de juego`](05%20-%20UI%20y%20UX%20de%20juego.md) §3.1 — por qué el HUD y los menús normalmente viven en el evento Draw GUI, la base de §8.7.2.
- [`13 · 06 — Arquitectura de un proyecto GameMaker`](06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) — separación cálculo/dibujo, módulos y fronteras.
- [`13 · 07 — Generación procedural avanzada`](07%20-%20Generaci%C3%B3n%20procedural%20avanzada.md) — semillas y algoritmos deterministas.
- [`13 · 11 — Producción, alcance y lanzamiento`](11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md) — dónde encaja QA en el calendario del proyecto.

---

## Fuentes

Todas consultadas o ejecutadas el **6 de septiembre de 2026**, salvo §8.7 (añadida el **8 de
septiembre de 2026**, ver el bloque de fuentes propio al final de esta sección).

**Primarias del motor**

- Manual oficial LTS 2026, `game_end` (versión inglesa, que documenta `return_code`; la
  española aún muestra la firma sin argumentos):
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/General_Game_Control/game_end.htm>
- Manual oficial LTS 2026, `try` / `catch` / `finally`:
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Overview/Language_Features/try_catch_finally.htm>
- Manual oficial LTS 2026, `throw`:
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Overview/Language_Features/throw.htm>
- Manual oficial LTS 2026, `debug_input_record` / `debug_input_playback` /
  `exception_unhandled_handler`:
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Debugging/debug_input_record.htm>
- `gm-cli` 2.3.0 — `--help` de `run`, `compile`, `package`, `init` y
  `resourcetool eval "help config"`, ejecutados en esta máquina; y la ejecución real de un
  proyecto creado con `gm-cli init` (plantilla *Blank Pixel Game*, toolchain
  `GMS2@2026.0.0.23`): `compile --errors-only` → 0, `run` en verde y en rojo,
  `run --config Pruebas`.

**Añadido — §8.7 (8 de septiembre de 2026, primera redacción)**

> En la sesión que escribió esta sección por primera vez, `gm-cli run` estuvo prohibido por
> restricción explícita del usuario — no de la biblioteca. Todo lo de abajo, de esta primera
> tanda de fuentes, es verificación por **compilación**, no por ejecución. Una sesión posterior,
> el mismo día, sí ejecutó `gm-cli run` de verdad: ver el bloque «Añadido — §8.7, verificación en
> tiempo de ejecución» más abajo, y el aviso ✅ al inicio de §8.7.

- Manual oficial LTS 2026, `screen_save` y `screen_save_part` (la exigencia de llamarlas desde
  Draw GUI End, y la ruta de guardado en Windows/Mac):
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Cameras_And_Display/screen_save.htm> ·
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Cameras_And_Display/screen_save_part.htm>
- Manual oficial LTS 2026, `working_directory` (la redirección automática al save area cuando el
  sandbox no permite escribir en el directorio de trabajo):
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/File_Handling/File_Directories/working_directory.htm>
- `gm-cli run --help` (8 de septiembre de 2026, esta sesión): confirma que no existe ningún flag
  de tiempo límite (`--target`, `--toolchain`, `--runtime`, `--verbose/--no-verbose`,
  `--errors-only`, `--license`, `--cache-dir`, `--config`, `--toolchain-options`, nada más).
- `gm-cli resourcetool eval` y `gm-cli compile`, ejecutados de verdad en esta sesión, en tres
  proyectos de prueba sucesivos (nunca dentro de esta biblioteca, todos borrados al terminar,
  plantilla *Blank Pixel Game*, toolchain `GMS2@2026.0.0.23`): un primer proyecto que confirmó
  la Trampa 3 tal como ya la documentaba `12 · 09` (`gui_end` → `Event_Draw_DrawEnd`, evento 73)
  y compiló el objeto de humo con el evento `Draw GUI` normal como primera aproximación; un
  segundo proyecto (`~/gm_prueba_humo_qa2`) que descubrió y confirmó por separado que `resource
  set expr=<obj>.eventList[N].eventNum value=75` fuerza el evento real —`object event list` pasó
  de `Event_Draw_DrawEnd` a `Event_Draw_DrawGUIEnd`, y `compile --errors-only` siguió en
  `exit 0`—; y un tercer proyecto final (`~/gm_prueba_humo_final`) con los tres objetos completos
  de §8.7 ya usando el evento forzado, `object event list` confirmando `Event_Draw_DrawGUIEnd`,
  `config create name=Humo`, `compile --errors-only` y sin el flag (`exit 0` los dos, sin
  `WARNING`), y `validar-proyecto.py --todo` sobre los 6
  archivos `.gml` nuevos (0 funciones inventadas).
- [`_indice/auditorias/r5-prueba-e2e.md`](../_indice/auditorias/r5-prueba-e2e.md) (08-09-2026,
  sesión distinta a esta): la ruta real de `game_save_id` bajo `gm-cli run --target mac`
  (`com.yoyogames.macyoyorunner`, no el nombre del juego) y la técnica de teclas sintéticas por
  `osascript` que este documento descarta a favor de la autocaptura.
- [`12 · 09` §0 Trampa 3](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-3--resourcetool-crea-el-evento-equivocado-sin-avisar-dos-bugs-de-numeraci%C3%B3n)
  y §4.3 (sesiones anteriores): la colisión `gui_end`→`draw_end` y el patrón de matar el proceso
  del runner por nombre, ambos reutilizados tal cual en §8.7.

**Añadido — §8.7, verificación en tiempo de ejecución (8 de septiembre de 2026, sesión
posterior a la redacción original)**

Todo lo de abajo es ejecución real con `gm-cli run`, no solo compilación — `gm-cli` 2.3.0,
runtime `2026.0.0.23`, macOS, proyecto de prueba `~/gm_humo_real` (nunca dentro de esta
biblioteca, borrado al terminar). Ningún proceso del runner quedó vivo al cerrar la sesión
(`ps -ef | grep -i runner` vacío, comprobado al final).

- Los 3 objetos de §8.7 montados con `resourcetool` (`obj_prueba_humo`, `obj_prueba_guardado_humo`,
  `obj_controlador_humo` — este último, sin código publicado hasta ahora, resuelto en esta
  sesión: ver §8.7.2), la fuente `fnt_prueba_humo` para probar el texto, y la instancia de
  `obj_controlador_humo` colocada con `resourcetool eval "room instance create room=room1
  object=obj_controlador_humo layer=Instances x=0 y=0"`.
- `gm-cli compile --errors-only` y sin el flag, ambos `exit 0`, sin `WARNING`;
  `validar-proyecto.py --todo` en 0 funciones inventadas sobre 7 archivos `.gml` (35 llamadas
  analizadas).
- El truco de `resource set expr=<obj>.eventList[N].eventNum value=75` de §8.7.2, reproducido de
  nuevo (índice 4 de 5 en el `eventList`, `eventNum` 73→75, `object event list` confirmó
  `Event_Draw_DrawGUIEnd`) — y, a diferencia de la sesión anterior, esta vez **ejecutado**: con
  el `.gml` mal renombrado, `Compile Objects...finished.... 1 empty events` en el log de Igor y
  el juego cuelga sin capturar; con el nombre correcto, `0 empty events` y captura+cierre
  normales. Cerraba el único ⚠️ que quedaba abierto en esa sección.
- `lanzar-humo.sh` y `verificar-guardado-humo.sh`, escritos tal cual los da §8.7.1 y §8.7.4 y
  ejecutados varias veces cada uno: marcador `###humo_captura###` y PNG real en
  `~/Library/Application Support/com.yoyogames.macyoyorunner/humo_captura.png` (confirmado con
  `find -newer`, no supuesto); ciclo de guardado en dos fases con `HUMO_FASE=escribir` y
  `HUMO_FASE=leer`, matando el proceso entre medias, con salida `###humo_guardado###ESCRITO` y
  luego `###humo_guardado###OK`.
- La captura real, abierta y mirada: el rectángulo de `Draw_0.gml` se veía con nitidez; el texto
  no apareció, por la Trampa 5 de `12 · 09` reproducida en vivo dentro de este procedimiento
  (`font glyphlist` vacío, chunk `FONT` a `0.00 MB` tras compilar) — ver §8.7.2 y §8.7.3.
- El escenario de cuelgue, reproducido a propósito (mismo objeto, `game_end()` comentado): con
  `MARGEN_S=5` de prueba, el corte llegó a los 5,06 s y `pkill -f Mac_Runner` limpió el proceso
  (confirmado con `ps` inmediatamente después) — el mecanismo que describe §8.7.1 como red de
  seguridad funciona de verdad, no solo en teoría.
- El nombre del proceso `Mac_Runner` en macOS, re-confirmado por el método de comparación de
  `ps` de §8.7.1 (independiente de la fuente anterior, `12 · 09` §4.3), y la ruta completa del
  binario (`.../runtime-2026.0.0.23/mac/YoYo Runner.app/Contents/MacOS/Mac_Runner`, con el flag
  `-runTest`) leída directamente de su línea de comando en `ps -ef`.
- El marcador `###game_end###N` visto en el `debug.log` sin que ningún `.gml` del proyecto lo
  escribiera — lo emite el propio runner al llamarse a `game_end(N)` bajo `-runTest`, la misma
  convención que ya usa `13 · 10` §3.4 para las pruebas unitarias.

**Frameworks**

- GM-TestFramework (YoYo Games): <https://github.com/YoYoGames/GM-TestFramework> · wiki
  (*Home*, *Running The Project*, *Creating Suites And Tests*):
  <https://github.com/YoYoGames/GM-TestFramework/wiki> · y el repositorio clonado en
  `11 - Código descargado/plantillas_y_ejemplos/GM-TestFramework`.
- crispy v1.9.0 (bfrymire, MIT): <https://github.com/bfrymire/crispy> · documentación:
  <https://bfrymire.github.io/crispy> · código leído en
  `11 - Código descargado/librerias/depuracion/crispy` (`scripts/TestCase`, `scripts/TestSuite`,
  `scripts/TestRunner`, `objects/obj_test`, `scripts/food_tests`).
- GMBenchmark (DragoniteSpam, MIT): <https://github.com/DragoniteSpam/GMBenchmark> ·
  `readme.md` del repositorio clonado.
- GameMaker-Bugs (canal oficial de reporte): <https://github.com/YoYoGames/GameMaker-Bugs>

**Playtesting y QA**

- Ken Birdwell, *The Cabal: Valve's Design Process for Creating Half-Life* (Game Developer,
  1999): <https://www.gamedeveloper.com/design/the-cabal-valve-s-design-process-for-creating-i-half-life-i->
- Jakob Nielsen, *Why You Only Need to Test with 5 Users* (Nielsen Norman Group):
  <https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/>
- Games User Research, *How many players do I need for a playtest?*:
  <https://gamesuserresearch.com/how-many-players-do-i-need-for-a-playtest/>

**Seguridad y anti-trampas (§14)**

- Cheat Engine, *About Cheat Engine* (descripción oficial del escáner de memoria y el
  *speedhack*, abierta con `curl` el 6 de septiembre de 2026):
  <https://www.cheatengine.org/aboutce.php>
- Manual oficial LTS 2026 — `sha1_string_utf8`, `md5_string_utf8`, `base64_encode` /
  `base64_decode` (funciones de hash y codificación usadas en el replay firmado de §14.3):
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/File_Handling/Encoding_And_Hashing/sha1_string_utf8.htm>
- [`01 · 14 — Persistencia y archivos`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) §12
  y [`04 · 14 — Multijugador`](../04%20-%20Recetas%20por%20g%C3%A9nero/14%20-%20Multijugador.md) §2.2 —
  las dos secciones de esta biblioteca que §14 conecta.
