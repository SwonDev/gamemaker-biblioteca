# 10 — Visual Novel y narrativa

> **Dificultad:** media
> El género más barato de producir y el más difícil de escribir bien. Técnica-
> mente es el más sencillo de esta biblioteca; el esfuerzo está en el sistema
> de datos, no en el motor.

---

## 1. Visión general

Una *visual novel* es un libro interactivo: texto, retratos, fondos, música, y
decisiones que cambian qué texto lees después.

**Lo que define al género:**

- El jugador **lee**, no juega. El ritmo lo marca la lectura, no los reflejos.
- Las decisiones tienen consecuencias **narrativas**, no mecánicas.
- La presentación es el 80 % del valor: tipografía, retratos, transiciones,
  música.
- Los **sistemas de conveniencia** no son opcionales: saltar texto ya leído,
  *backlog*, auto-avance. Si no los tienes, el jugador que relee se rebela.

**Referencias hechas en GameMaker:** *Doki Doki Literature Club* (hecho en
Ren'Py, pero el diseño es el canon), *VA-11 HALL-A*, *Long Live The Queen*
(hecha en GameMaker), *One Night Stand* (GameMaker), *Butterfly Soup*
(GameMaker). GameMaker es una opción habitual para VN con minijuegos
integrados, porque ahí Ren'Py se queda corto.

**Subgéneros:**

| Subgénero | Rasgo |
|---|---|
| *Kinetic novel* | Sin decisiones; lectura lineal |
| Ramificada | Decisiones → rutas distintas |
| *Dating sim* | Estadísticas de afinidad por personaje |
| Híbrida con minijuegos | VN + puzles o combate (Persona-like) |
| *Sound novel* | Pantalla negra, texto, efectos de sonido (Higurashi) |

---

## 2. Arquitectura recomendada

### El guion como datos

```
┌─ GUION (texto plano o JSON) ─────────────────────────────┐
│ archivo de texto con marcadores:                         │
│   *label inicio                                          │
│   [fondo: aula_dia]                                      │
│   [musica: tema_calmado]                                 │
│   Ana: [feliz] Buenos días.                              │
│   Ana: ¿Has dormido bien?                                │
│   ? Sí, muy bien -> ruta_descansado                      │
│   ? No, fatal    -> ruta_cansado                         │
└──────────────────────────────────────────────────────────┘
                          ↓ parser
┌─ MODELO (structs en memoria) ────────────────────────────┐
│ nodos: { label: [ {tipo, speaker, texto, comandos} ] }   │
└──────────────────────────────────────────────────────────┘
                          ↓ runner
┌─ VISTA (objDialogue) ────────────────────────────────────┐
│ caja de texto, retrato, typewriter, opciones             │
└──────────────────────────────────────────────────────────┘
```

**Por qué un formato de texto propio en vez de structs a mano:** porque lo
escribes tú (o un guionista) cientos de veces. `Ana: Hola.` es infinitamente
más rápido de escribir que `array_push(nodos, {speaker:"Ana", text:"Hola"})`.

### Jerarquía de objetos

```
objVNRunner       (controller: parsea el guion y avanza por los nodos)
objVNTextbox      (dibuja la caja, el texto con typewriter, el nombre)
objVNPortrait     (retratos con transiciones de entrada/salida)
objVNChoice       (botones de elección)
objVNBacklog      (historial de texto ya leído)
objSaveLoad       (guardado con capturas de pantalla)
objConfig         (velocidad de texto, auto, skip)
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `VNNode` | Una línea: tipo, personaje, texto, comandos |
| `VNChoice` | Una opción: texto, label destino, condición |
| `VNState` | Variables de la historia, flags, afinidades |
| `VNSave` | Guardado: label actual + índice + estado + captura |

---

## 3. El bucle central (core loop)

```
┌─ Step de objVNRunner ────────────────────────────────────┐
│ 1. ¿Hay un nodo activo?                                  │
│ 2. Si es texto: avanzar el typewriter                    │
│    - si está escribiendo y se pulsa → completar          │
│    - si ya terminó y se pulsa → siguiente nodo           │
│ 3. Si es comando ([fondo:], [musica:]) → ejecutar y      │
│    pasar AUTOMÁTICAMENTE al siguiente                    │
│ 4. Si es salto (-> label) → cambiar de label             │
│ 5. Si es elección (?) → mostrar botones, esperar         │
│ 6. ¿Auto-avance activo? → temporizador                   │
│ 7. ¿Skip activo? → saltar hasta decisión o texto nuevo   │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 El formato del guion

Usa un convenio simple y consistente. Este es el que recomiendo:

| Sintaxis | Significado |
|---|---|
| `*etiqueta` | Define un punto de salto |
| `Personaje: texto` | Línea de diálogo |
| `Personaje: [emocion] texto` | Diálogo con emoji/expresión |
| `texto` (sin dos puntos) | Narración |
| `? Texto -> etiqueta` | Opción de elección |
| `[fondo: nombre]` | Comando: cambiar fondo |
| `[musica: nombre]` | Comando: música |
| `[sfx: nombre]` | Comando: efecto de sonido |
| `[set: variable, valor]` | Comando: asignar variable |
| `[if variable -> etiqueta]` | Comando: salto condicional |
| `-> etiqueta` | Salto incondicional |
| `[voz: archivo]` | Línea de voz |

### 4.2 Typewriter effect

El texto aparece carácter a carácter. Tres detalles que separan uno mediocre
de uno bueno:

1. **Velocidad configurable y guardada.** Cada jugador lee a un ritmo distinto.
2. **Pausas en puntuación.** Un punto debe parar más que una letra. Eso hace
   que suene a voz humana.
3. **Saltar al instante.** Si pulsas mientras escribe, se muestra todo de golpe.

```gml
// Pausas según el último carácter escrito
switch (_ultimo_char)
{
    case ".": case "!": case "?": _delay += 12; break;
    case ",": case ";": case ":": _delay += 6;  break;
    case " ":                     _delay += 0;  break;
    default:                      _delay += 1;
}
```

### 4.3 Retratos

El retrato muestra quién habla y su emoción. Implementación:

- Un sprite por personaje con una subimagen por emoción, o sprites separados.
- El personaje que habla se resalta; los demás se atenúan (alfa baja, escala
  ligeramente menor, o tono gris).
- Transición de entrada/salida con un tween corto (8-12 frames).

### 4.3 bis Retrato sin artista: de dónde sale el busto

§4.3 y §5.5 cubren cómo se **muestra** y se **cambia** un retrato; lo que falta es de dónde sale
la imagen en sí cuando no hay artista. Tres vías, en orden de coste:

1. **Recorta un sprite de cuerpo entero que ya generaste con la escalera de
   [12 · 09 §5.2](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#52-gráfico-la-escalera-de-prioridad-sin-el-rectángulo-plano)**,
   reencuadrado a busto (cabeza + hombros) y escalado al tamaño del panel de diálogo. Es gratis
   si el personaje ya existe como sprite jugable o de enemigo, y mantiene la coherencia de paleta
   con el resto del juego.
2. **Busca un retrato genérico en los mismos bancos de
   [07 · 09](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md)** —
   varios packs de personajes de itch.io y OpenGameArt incluyen bustos de diálogo pensados para
   novela visual, con la licencia ya comprobada en ese documento.
3. **IA generativa, y aquí sí como candidata seria, no solo de referencia**: el propio
   [`07 · 23` §1](../07%20-%20Ecosistema/23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md#1--qué-sirve-hoy-de-verdad)
   señala «retratos puntuales sin animar» como uno de los usos que sí funcionan hoy — una sola
   imagen por personaje, sin la exigencia de consistencia entre 40 fotogramas que rompe la IA en
   un ciclo de animación. Comando verificado en esta sesión, el mismo patrón que
   [`07 · 24` §1.2](../07%20-%20Ecosistema/24%20-%20Logotipo%2C%20icono%20del%20ejecutable%20y%20capsule%20de%20tienda.md#12-receta-codex-exec--gpt-image-2):

   ```bash
   codex exec -C <dir_proyecto> --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check \
     -o <scratch>/codex_last.txt \
     "Usa tu herramienta de generación de imágenes (gpt-image-2) para crear el retrato de busto
      de '<personaje>': <descripción física, ropa, expresión>, estilo coherente con <estilo del
      juego>, fondo transparente o neutro, sin texto. Genera 2-3 expresiones distintas (neutral,
      feliz, enfadado). Guarda los PNG en <ruta>. Al terminar lista las rutas."
   ```

   Si el retrato va a redibujarse a mano después, es referencia (`07 · 23` §5, fila «Hoja de
   referencia»); si va a shippear tal cual, **decláralo** igual que cualquier otra pieza de IA
   generativa (`07 · 23` §4.2-§4.3) y pasa el checklist de `07 · 23` §6 antes de darlo por bueno.

### 4.4 Elecciones ramificadas

Una elección tiene: texto, destino y **condición opcional**. Las condiciones
permiten opciones que solo aparecen si has hecho algo antes. Es la herramienta
más potente del guionista.

```gml
opcion = {
    texto: "Confesar lo que sientes",
    destino: "ruta_confesion",
    condicion: function() { return global.vn_state.afinidad_ana >= 3; },
    efecto: function() { global.vn_state.afinidad_ana += 2; }
};
```

### 4.5 Guardado, y el truco de la captura

Guardar una VN es trivial (label + índice + variables). Lo que la hace buena
es la **miniatura**: una captura de la pantalla en el momento de guardar.

```gml
// Capturar el application surface y guardarlo como PNG
var _surf = surface_create(display_get_gui_width(), display_get_gui_height());
surface_copy(_surf, 0, 0, application_surface);
// Reducir de tamaño a ~200px de ancho
// sprite_save() o buffer_save() para persistirlo
```

Sin miniatura, el jugador no sabe qué partida es cuál y acaba guardando todo
en un solo slot.

### 4.6 Voz

Si tienes voces grabadas, el typewriter debe **sincronizarse con el audio**, no
al revés. Dos enfoques:

| Enfoque | Cómo |
|---|---|
| **Audio manda** | Duración del texto = duración del audio |
| **Texto manda** | El audio se corta si el jugador avanza |

El primero es mejor: el jugador oye la frase completa.

### 4.7 Backlog

Un historial de las últimas N líneas, accesible con la rueda del ratón o una
tecla. Es **imprescindible** en una VN: el jugador se despista, vuelve atrás,
y sin backlog se pierde.

---

## 5. Código base

### 5.1 Parser del guion

```gml
// ---------------------------------------------------------------------------
// scr_vn_parser
// ---------------------------------------------------------------------------

/// @func vn_parse(_ruta_archivo)
/// @desc Lee un archivo de guion y construye { labels: { nombre: [nodos] } }
function vn_parse(_ruta_archivo)
{
    if (!file_exists(_ruta_archivo))
    {
        show_debug_message("ERROR: no existe el guion " + _ruta_archivo);
        return { labels: {} };
    }

    var _f = file_text_open_read(_ruta_archivo);
    var _lineas = [];

    while (!file_text_eof(_f))
    {
        array_push(_lineas, file_text_read_string(_f));
        file_text_readln(_f);
    }
    file_text_close(_f);

    var _labels = {};
    var _label_actual = "inicio";
    _labels[$ _label_actual] = [];

    for (var _i = 0; _i < array_length(_lineas); _i++)
    {
        var _linea = string_trim(_lineas[_i]);

        // Ignorar vacías y comentarios
        if (_linea == "") continue;
        if (string_starts_with(_linea, "//")) continue;

        // --- Etiqueta: *nombre -------------------------------------------------
        if (string_starts_with(_linea, "*"))
        {
            _label_actual = string_trim(string_delete(_linea, 1, 1));
            if (!variable_struct_exists(_labels, _label_actual))
            {
                _labels[$ _label_actual] = [];
            }
            continue;
        }

        // --- Comando: [algo] -----------------------------------------------------
        if (string_starts_with(_linea, "["))
        {
            var _cmd = vn_parse_comando(_linea);
            array_push(_labels[$ _label_actual], _cmd);
            continue;
        }

        // --- Opción: ? texto -> destino -------------------------------------------
        if (string_starts_with(_linea, "?"))
        {
            var _op = vn_parse_opcion(_linea);
            array_push(_labels[$ _label_actual], {
                tipo: "opcion",
                texto: _op.texto,
                destino: _op.destino
            });
            continue;
        }

        // --- Salto incondicional: -> destino ----------------------------------------
        if (string_starts_with(_linea, "->"))
        {
            array_push(_labels[$ _label_actual], {
                tipo: "salto",
                destino: string_trim(string_delete(_linea, 1, 2))
            });
            continue;
        }

        // --- Diálogo o narración -----------------------------------------------------
        var _dos_puntos = string_pos(":", _linea);

        if (_dos_puntos > 0)
        {
            var _speaker = string_trim(string_copy(_linea, 1, _dos_puntos - 1));
            var _texto   = string_trim(string_delete(_linea, 1, _dos_puntos));

            // ¿Lleva emoción entre corchetes?  Ana: [feliz] Hola
            var _emocion = "";
            if (string_starts_with(_texto, "["))
            {
                var _cierre = string_pos("]", _texto);
                if (_cierre > 0)
                {
                    _emocion = string_copy(_texto, 2, _cierre - 2);
                    _texto   = string_trim(string_delete(_texto, 1, _cierre));
                }
            }

            array_push(_labels[$ _label_actual], {
                tipo: "texto",
                speaker: _speaker,
                emocion: _emocion,
                texto: _texto
            });
        }
        else
        {
            // Narración
            array_push(_labels[$ _label_actual], {
                tipo: "texto",
                speaker: "",
                emocion: "",
                texto: _linea
            });
        }
    }

    return { labels: _labels };
}

/// @func vn_parse_comando(_linea)
function vn_parse_comando(_linea)
{
    // Quitar los corchetes
    var _c = string_copy(_linea, 2, string_length(_linea) - 2);

    // Formato "clave: valor"  o  "clave: arg1, arg2"
    var _sep = string_pos(":", _c);

    if (_sep == 0) return { tipo: "cmd", clave: string_trim(_c), valor: "" };

    var _clave = string_trim(string_copy(_c, 1, _sep - 1));
    var _valor = string_trim(string_delete(_c, 1, _sep));

    // Salto condicional: [if variable -> etiqueta]
    if (_clave == "if")
    {
        var _flecha = string_pos("->", _valor);
        if (_flecha > 0)
        {
            return {
                tipo: "condicional",
                variable: string_trim(string_copy(_valor, 1, _flecha - 1)),
                destino:  string_trim(string_delete(_valor, 1, _flecha + 1))
            };
        }
    }

    return { tipo: "cmd", clave: _clave, valor: _valor };
}

/// @func vn_parse_opcion(_linea)
function vn_parse_opcion(_linea)
{
    // Formato: ? texto -> destino
    var _sin = string_trim(string_delete(_linea, 1, 1));
    var _flecha = string_pos("->", _sin);

    if (_flecha == 0) return { texto: _sin, destino: "" };

    return {
        texto:   string_trim(string_copy(_sin, 1, _flecha - 1)),
        destino: string_trim(string_delete(_sin, 1, _flecha + 1))
    };
}

// NOTA IMPORTANTE: string_trim() y string_starts_with() son funciones NATIVAS
// de GameMaker. No las redefinas: duplicar una función integrada es un error
// de compilación.
//
//   string_trim(str, [substr])          → quita espacios (o substr) al inicio y final
//   string_starts_with(str, substr)     → true si str empieza por substr
//
// El parser de más abajo las usa directamente.
//
// Otras funciones nativas útiles para un parser que NO debes reimplementar:
//   string_ends_with(str, substr)
//   string_split(string, delimiter, [remove_empty], [max_splits])
//   string_contains(str, substr)
//   array_contains(array, value, [offset], [length])
```

### 5.2 Estado de la historia

```gml
// ---------------------------------------------------------------------------
// scr_vn_state
// ---------------------------------------------------------------------------

/// @func VNState()
/// @desc Variables de la historia. Se guardan y se cargan.
function VNState() constructor
{
    variables = {};      // { conocio_a_ana: true, llaves: 2 }
    afinidad  = {};      // { ana: 3, luis: 1 }

    /// @desc Lee una variable (los nombres desconocidos valen 0/false).
    get = function(_nombre)
    {
        if (!variable_struct_exists(variables, _nombre)) return 0;
        return variables[$ _nombre];
    };

    set = function(_nombre, _valor)
    {
        variables[$ _nombre] = _valor;
    };

    sumar = function(_nombre, _cantidad)
    {
        set(_nombre, get(_nombre) + ((_cantidad == undefined) ? 1 : _cantidad));
    };

    /// @desc Afinidad con un personaje.
    afinidad_get = function(_personaje)
    {
        if (!variable_struct_exists(afinidad, _personaje)) return 0;
        return afinidad[$ _personaje];
    };

    afinidad_sumar = function(_personaje, _cantidad)
    {
        var _actual = afinidad_get(_personaje);
        afinidad[$ _personaje] = _actual + _cantidad;

        // Feedback: cuando la afinidad cambia, que el jugador lo note
        if (_cantidad > 0)
        {
            fx_floating_text(objPlayer.x, objPlayer.y - 20,
                             "+ afinidad con " + _personaje, c_pink);
        }
    };

    serialize = function()
    {
        return { variables: variables, afinidad: afinidad };
    };

    static deserialize = function(_d)
    {
        var _s = new VNState();
        _s.variables = _d.variables;
        _s.afinidad  = _d.afinidad;
        return _s;
    };
}
```

### 5.3 El runner

```gml
// ---------------------------------------------------------------------------
// objVNRunner — Create
// ---------------------------------------------------------------------------
guion = vn_parse("guion_cap1.txt");

label_actual = "inicio";
indice       = 0;

nodo         = undefined;      // nodo activo
texto_mostrado = "";
char_index   = 0;
char_delay   = 0;

// Opciones activas (si el nodo es de tipo "opcion", hay varias seguidas)
opciones     = [];

// Ajustes
vel_texto    = 1.0;      // multiplicador
auto_avance  = false;
auto_timer   = 0;
skip_activo  = false;

// Backlog: últimas 100 líneas
backlog      = [];

global.vn_state = new VNState();

// Empezar
cargar_label("inicio");
```

```gml
// ---------------------------------------------------------------------------
// objVNRunner — Step
// ---------------------------------------------------------------------------
if (skip_activo)
{
    saltar_hasta_decision();
    exit;
}

// --- Auto-avance ---------------------------------------------------------------
if (auto_avance && nodo != undefined && nodo.tipo == "texto")
{
    if (char_index >= string_length(nodo.texto))
    {
        auto_timer++;
        if (auto_timer > 90)      // ~1,5 s para leer
        {
            auto_timer = 0;
            avanzar();
        }
    }
}

// --- Typewriter -----------------------------------------------------------------
if (nodo != undefined && nodo.tipo == "texto" &&
    char_index < string_length(nodo.texto))
{
    char_delay -= vel_texto;

    while (char_delay <= 0 && char_index < string_length(nodo.texto))
    {
        char_index++;
        var _c = string_char_at(nodo.texto, char_index);

        // Pausas por puntuación: esto es lo que hace que "suene" a humano
        switch (_c)
        {
            case ".": case "!": case "?": char_delay += 14; break;
            case ",": case ";": case ":": char_delay += 7;  break;
            case "…":                     char_delay += 18; break;
            default:                      char_delay += 1.6;
        }

        // Sonido de voz cada pocos caracteres
        if (char_index mod 3 == 0 && variable_struct_exists(nodo, "voz"))
        {
            // (ver sección 5.6)
        }
    }

    texto_mostrado = string_copy(nodo.texto, 1, floor(char_index));
}
else
{
    texto_mostrado = (nodo != undefined) ? nodo.texto : "";
}

// --- Input -----------------------------------------------------------------------
var _confirmar = keyboard_check_pressed(vk_space)
              || keyboard_check_pressed(ord("Z"))
              || mouse_check_button_pressed(mb_left);

if (_confirmar && array_length(opciones) == 0)
{
    if (nodo != undefined && nodo.tipo == "texto" &&
        char_index < string_length(nodo.texto))
    {
        // Completar el texto de golpe
        char_index = string_length(nodo.texto);
    }
    else
    {
        avanzar();
    }
}

// --- Backlog con la rueda del ratón ------------------------------------------------
if (mouse_wheel_up() && !objVNBacklog.abierto)
{
    objVNBacklog.abrir();
}

// --- Saltar con Ctrl ---------------------------------------------------------------
skip_activo = keyboard_check(vk_control);
```

```gml
// ---------------------------------------------------------------------------
// objVNRunner — avanzar y ejecutar nodos
// ---------------------------------------------------------------------------

/// @func avanzar()
/// @desc Ejecuta el nodo actual y pasa al siguiente.
///       Los comandos se ejecutan y encadenan automáticamente.
function avanzar()
{
    var _ejecutados = 0;

    while (true)
    {
        indice++;
        _ejecutados++;

        // Salvaguarda anti-bucle infinito
        if (_ejecutados > 200)
        {
            show_debug_message("ERROR: bucle infinito en el guion");
            break;
        }

        var _lista = guion.labels[$ label_actual];

        if (indice >= array_length(_lista))
        {
            // Fin del guion
            nodo = undefined;
            show_debug_message("FIN del guion en label: " + label_actual);
            return;
        }

        var _n = _lista[indice];

        // --- Comando: ejecutar y seguir -------------------------------------------
        if (_n.tipo == "cmd")
        {
            ejecutar_comando(_n);
            continue;
        }

        // --- Condicional ------------------------------------------------------------
        if (_n.tipo == "condicional")
        {
            if (global.vn_state.get(_n.variable))
            {
                cargar_label(_n.destino);
                return;
            }
            continue;
        }

        // --- Salto ---------------------------------------------------------------------
        if (_n.tipo == "salto")
        {
            cargar_label(_n.destino);
            return;
        }

        // --- Opción: recoger TODAS las opciones seguidas y esperar -------------------
        if (_n.tipo == "opcion")
        {
            opciones = [];
            var _lista2 = guion.labels[$ label_actual];
            var _j = indice;

            while (_j < array_length(_lista2) && _lista2[_j].tipo == "opcion")
            {
                array_push(opciones, _lista2[_j]);
                _j++;
            }

            nodo = undefined;
            return;
        }

        // --- Texto: mostrar y parar ---------------------------------------------------
        if (_n.tipo == "texto")
        {
            nodo = _n;
            char_index = 0;
            char_delay = 0;
            texto_mostrado = "";

            // Añadir al backlog
            array_push(backlog, {
                speaker: _n.speaker,
                texto: _n.texto
            });
            if (array_length(backlog) > 100) array_delete(backlog, 0, 1);

            // Actualizar retrato y voz
            if (_n.speaker != "") actualizar_retrato(_n.speaker, _n.emocion);
            if (variable_struct_exists(_n, "voz")) reproducir_voz(_n.voz);

            return;
        }
    }
}

/// @func cargar_label(_nombre)
function cargar_label(_nombre)
{
    if (!variable_struct_exists(guion.labels, _nombre))
    {
        show_debug_message("ERROR: label inexistente: " + _nombre);
        return false;
    }

    label_actual = _nombre;
    indice       = -1;      // avanzar() lo pondrá a 0
    opciones     = [];
    nodo         = undefined;

    avanzar();
    return true;
}

/// @func ejecutar_comando(_cmd)
function ejecutar_comando(_cmd)
{
    switch (_cmd.clave)
    {
        case "fondo":
            objVNTextbox.cambiar_fondo(asset_get_index("bg_" + _cmd.valor));
            break;

        case "musica":
            var _snd = asset_get_index("mus_" + _cmd.valor);
            if (_snd != -1)
            {
                if (audio_is_playing(global.musica_actual))
                {
                    audio_stop_sound(global.musica_actual);
                }
                global.musica_actual = audio_play_sound(_snd, 1, true);
            }
            break;

        case "sfx":
            var _snd = asset_get_index("sfx_" + _cmd.valor);
            if (_snd != -1) audio_play_sound(_snd, 5, false);
            break;

        case "set":
            // Formato: [set: nombre, valor]
            var _partes = string_split(_cmd.valor, ",");
            if (array_length(_partes) >= 2)
            {
                var _nombre = string_trim(_partes[0]);
                var _valor_s = string_trim(_partes[1]);

                // ¿Es número?
                var _valor = (string_digits(_valor_s) == _valor_s && _valor_s != "")
                    ? real(_valor_s)
                    : ((_valor_s == "true") ? true :
                       ((_valor_s == "false") ? false : _valor_s));

                global.vn_state.set(_nombre, _valor);
            }
            break;

        case "afinidad":
            // Formato: [afinidad: ana, +2]
            var _partes = string_split(_cmd.valor, ",");
            if (array_length(_partes) >= 2)
            {
                var _personaje = string_trim(_partes[0]);
                var _cantidad = real(string_trim(_partes[1]));
                global.vn_state.afinidad_sumar(_personaje, _cantidad);
            }
            break;

        case "voz":
            // Se asocia a la SIGUIENTE línea de texto
            // (se procesa cuando se alcanza ese nodo)
            break;

        default:
            show_debug_message("Comando desconocido: " + _cmd.clave);
    }
}

/// @func seleccionar_opcion(_indice)
function seleccionar_opcion(_indice)
{
    if (_indice < 0 || _indice >= array_length(opciones)) return;

    var _op = opciones[_indice];

    // Registrar la decisión (útil para finales y desbloqueos)
    global.vn_state.set("decision_" + label_actual + "_" + string(indice), true);

    opciones = [];
    cargar_label(_op.destino);
}

/// @func saltar_hasta_decision()
/// @desc Modo skip: avanza rápido hasta encontrar una opción o texto no leído.
function saltar_hasta_decision()
{
    // Los nodos ya leídos se marcan en un set
    var _clave = label_actual + "_" + string(indice);

    if (!variable_struct_exists(global.vn_leido, _clave))
    {
        // Texto nuevo: parar el skip
        skip_activo = false;
        return;
    }

    avanzar();
}
```

### 5.4 La caja de texto

```gml
// ---------------------------------------------------------------------------
// objVNTextbox — Create
// ---------------------------------------------------------------------------
fondo_actual = bg_aula_dia;
fondo_alpha  = 1;
fondo_nuevo  = noone;

// Transición de fondo
transicion_t = 0;

// ---------------------------------------------------------------------------
// objVNTextbox — Step
// ---------------------------------------------------------------------------
if (fondo_nuevo != noone)
{
    transicion_t++;
    if (transicion_t >= 20)
    {
        fondo_actual = fondo_nuevo;
        fondo_nuevo  = noone;
        transicion_t = 0;
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objVNTextbox — Draw GUI
// ---------------------------------------------------------------------------
var _gw = display_get_gui_width();
var _gh = display_get_gui_height();

// --- Fondo ---------------------------------------------------------------------
// Crossfade entre el fondo actual y el nuevo
draw_sprite(fondo_actual, 0, 0, 0);
if (fondo_nuevo != noone)
{
    draw_set_alpha(transicion_t / 20);
    draw_sprite(fondo_nuevo, 0, 0, 0);
    draw_set_alpha(1);
}

// --- Retratos --------------------------------------------------------------------
objVNPortrait.dibujar();

// --- Caja de texto -----------------------------------------------------------------
var _box_h = 150;
var _box_y = _gh - _box_h - 20;

draw_set_alpha(0.88);
draw_set_color(c_black);
draw_roundrect_ext(30, _box_y, _gw - 30, _box_y + _box_h, 12, 12, false);

draw_set_alpha(1);
draw_set_color(c_white);
draw_roundrect_ext(30, _box_y, _gw - 30, _box_y + _box_h, 12, 12, true);

// --- Nombre del personaje -----------------------------------------------------------
var _runner = objVNRunner;

if (_runner.nodo != undefined && _runner.nodo.speaker != "")
{
    draw_set_font(fntVNName);
    draw_set_color(c_yellow);
    draw_text(52, _box_y + 12, _runner.nodo.speaker);
}

// --- Texto con typewriter -------------------------------------------------------------
draw_set_font(fntVNText);
draw_set_color(c_white);
draw_text_ext(52, _box_y + 48, _runner.texto_mostrado, 26, _gw - 104);

// --- Indicador de "continuar" -----------------------------------------------------------
if (_runner.char_index >= string_length(_runner.nodo.texto))
{
    var _bob = sin(current_time * 0.005) * 3;
    draw_sprite(sprContinueArrow, 0, _gw - 60, _box_y + _box_h - 30 + _bob);
}

// --- Opciones -------------------------------------------------------------------------------
if (array_length(_runner.opciones) > 0)
{
    dibujar_opciones(_gw, _gh);
}
```

```gml
// ---------------------------------------------------------------------------
// objVNTextbox — dibujar_opciones
// ---------------------------------------------------------------------------
function dibujar_opciones(_gw, _gh)
{
    var _ops = objVNRunner.opciones;
    var _alto_op = 46;
    var _total_h = array_length(_ops) * _alto_op;
    var _y0 = (_gh * 0.5) - (_total_h * 0.5);

    // Oscurecer el fondo para que las opciones destaquen
    draw_set_alpha(0.5);
    draw_set_color(c_black);
    draw_rectangle(0, 0, _gw, _gh, false);
    draw_set_alpha(1);

    for (var _i = 0; _i < array_length(_ops); _i++)
    {
        var _y = _y0 + (_i * _alto_op);
        var _mouse_encima = point_in_rectangle(
            mouse_x, mouse_y, _gw * 0.25, _y, _gw * 0.75, _y + _alto_op - 8);

        // Fondo de la opción
        draw_set_alpha(_mouse_encima ? 0.92 : 0.75);
        draw_set_color(c_black);
        draw_roundrect_ext(_gw * 0.25, _y, _gw * 0.75, _y + _alto_op - 8,
                           8, 8, false);

        draw_set_alpha(1);
        draw_set_color(_mouse_encima ? c_yellow : c_white);
        draw_roundrect_ext(_gw * 0.25, _y, _gw * 0.75, _y + _alto_op - 8,
                           8, 8, true);

        // Texto
        draw_set_font(fntVNText);
        draw_set_color(_mouse_encima ? c_yellow : c_white);
        draw_set_halign(fa_center);
        draw_set_valign(fa_middle);
        draw_text(_gw * 0.5, _y + (_alto_op - 8) * 0.5, _ops[_i].texto);
        draw_set_halign(fa_left);
        draw_set_valign(fa_top);

        // Clic
        if (_mouse_encima && mouse_check_button_pressed(mb_left))
        {
            objVNRunner.seleccionar_opcion(_i);
            audio_play_sound(sndSelect, 10, false);
            break;      // solo una por frame
        }
    }
}
```

> `draw_roundrect_ext(x1, y1, x2, y2, xrad, yrad, outline)` es la función
> correcta en GameMaker moderno. La antigua `draw_roundrect()` sin `_ext` está
> obsoleta.

### 5.5 Retratos

```gml
// ---------------------------------------------------------------------------
// objVNPortrait — Create
// ---------------------------------------------------------------------------
// Retratos activos en escena: array de { sprite, emocion, x, alpha_actual,
//                                        alpha_objetivo, escala }
retratos = [];

/// @func establecer(_personaje, _emocion, _x)
function establecer(_personaje, _emocion, _x)
{
    // ¿Ya está en escena?
    for (var _i = 0; _i < array_length(retratos); _i++)
    {
        if (retratos[_i].personaje == _personaje)
        {
            retratos[_i].emocion = _emocion;
            return;
        }
    }

    var _spr = asset_get_index("spr_" + string_lower(_personaje) + "_" + _emocion);
    if (_spr == -1) _spr = asset_get_index("spr_" + string_lower(_personaje));

    array_push(retratos, {
        personaje: _personaje,
        sprite: _spr,
        emocion: _emocion,
        x: _x,
        alpha_actual: 0,
        alpha_objetivo: 1,
        escala: 1,
        escala_objetivo: 1
    });
}

/// @func resaltar(_personaje)
/// @desc El que habla se ilumina; el resto se atenúa.
function resaltar(_personaje)
{
    for (var _i = 0; _i < array_length(retratos); _i++)
    {
        var _r = retratos[_i];
        var _habla = (_r.personaje == _personaje);

        _r.alpha_objetivo  = _habla ? 1.0 : 0.45;
        _r.escala_objetivo = _habla ? 1.0 : 0.94;
    }
}

/// @func quitar(_personaje)
function quitar(_personaje)
{
    for (var _i = 0; _i < array_length(retratos); _i++)
    {
        if (retratos[_i].personaje == _personaje)
        {
            retratos[_i].alpha_objetivo = 0;
        }
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objVNPortrait — Step
// ---------------------------------------------------------------------------
for (var _i = array_length(retratos) - 1; _i >= 0; _i--)
{
    var _r = retratos[_i];

    _r.alpha_actual = lerp(_r.alpha_actual, _r.alpha_objetivo, 0.15);
    _r.escala       = lerp(_r.escala, _r.escala_objetivo, 0.15);

    // Eliminar los que ya son invisibles del todo
    if (_r.alpha_objetivo == 0 && _r.alpha_actual < 0.02)
    {
        array_delete(retratos, _i, 1);
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objVNPortrait — dibujar()
// ---------------------------------------------------------------------------
function dibujar()
{
    var _gh = display_get_gui_height();

    for (var _i = 0; _i < array_length(retratos); _i++)
    {
        var _r = retratos[_i];
        if (_r.sprite == -1) continue;

        draw_sprite_ext(_r.sprite, 0, _r.x, _gh - 40,
                        _r.escala, _r.escala, 0, c_white, _r.alpha_actual);
    }
}
```

### 5.6 Voces sincronizadas con el typewriter

```gml
// ---------------------------------------------------------------------------
// scr_vn_voice
// ---------------------------------------------------------------------------

/// @func reproducir_voz(_archivo)
/// @desc Reproduce la voz asociada a una línea.
///       Guardamos la referencia para poder cortarla si el jugador avanza.
function reproducir_voz(_archivo)
{
    var _snd = asset_get_index("voz_" + _archivo);
    if (_snd == -1) return;

    // Cortar la voz anterior si sigue sonando
    if (global.voz_actual != noone && audio_is_playing(global.voz_actual))
    {
        audio_stop_sound(global.voz_actual);
    }

    global.voz_actual = audio_play_sound(_snd, 10, false);

    // --- Sincronización: ajustar la velocidad del texto a la duración ----------
    // audio_sound_length() devuelve la duración en segundos.
    var _duracion_frames = audio_sound_length(_snd) * game_get_speed(gamespeed_fps);
    var _caracteres = string_length(objVNRunner.nodo.texto);

    if (_caracteres > 0 && _duracion_frames > 0)
    {
        // Caracteres por frame necesarios para terminar con el audio
        objVNRunner.vel_texto = (_caracteres / _duracion_frames) * 1.6;
    }
}
```

> `audio_sound_length(sound)` devuelve segundos. `game_get_speed(gamespeed_fps)`
> da los fps reales del juego. Con ambos conviertes a frames sin hardcodear 60.

### 5.7 Backlog

```gml
// ---------------------------------------------------------------------------
// objVNBacklog — Create
// ---------------------------------------------------------------------------
abierto  = false;
scroll   = 0;
depth    = -10000;
```

```gml
// ---------------------------------------------------------------------------
// objVNBacklog — Step
// ---------------------------------------------------------------------------
if (!abierto) exit;

// Cerrar
if (mouse_check_button_pressed(mb_right) || keyboard_check_pressed(vk_escape))
{
    abierto = false;
    exit;
}

// Scroll con la rueda
if (mouse_wheel_up())   scroll = max(0, scroll - 1);
if (mouse_wheel_down()) scroll = min(40, scroll + 1);
```

```gml
// ---------------------------------------------------------------------------
// objVNBacklog — Draw GUI
// ---------------------------------------------------------------------------
if (!abierto) exit;

var _gw = display_get_gui_width();
var _gh = display_get_gui_height();

draw_set_alpha(0.92);
draw_set_color(c_black);
draw_rectangle(0, 0, _gw, _gh, false);
draw_set_alpha(1);

draw_set_font(fntVNText);
draw_set_color(c_white);
draw_text(30, 20, "HISTORIAL  (clic derecho para cerrar)");

var _y = 70;
var _backlog = objVNRunner.backlog;
var _inicio = max(0, array_length(_backlog) - 25 - scroll);

for (var _i = _inicio; _i < array_length(_backlog) - scroll; _i++)
{
    var _entrada = _backlog[_i];

    if (_entrada.speaker != "")
    {
        draw_set_color(c_yellow);
        draw_text(40, _y, _entrada.speaker + ":");
        draw_set_color(c_white);
        draw_text_ext(40 + string_width(_entrada.speaker + ": ") + 8, _y,
                      _entrada.texto, 22, _gw - 100);
    }
    else
    {
        draw_set_color(c_ltgray);
        draw_text_ext(40, _y, _entrada.texto, 22, _gw - 100);
    }

    _y += 34;
    if (_y > _gh - 30) break;
}
```

### 5.8 Guardado con miniatura

```gml
// ---------------------------------------------------------------------------
// scr_vn_save
// ---------------------------------------------------------------------------

/// @func vn_save(_slot)
/// @desc Guarda la partida con una miniatura de la pantalla.
function vn_save(_slot)
{
    var _r = objVNRunner;

    var _data = {
        version:  1,
        label:    _r.label_actual,
        indice:   _r.indice,
        estado:   global.vn_state.serialize(),
        fecha:    date_datetime_string(date_current_datetime()),
        texto:    (_r.nodo != undefined) ? _r.nodo.texto : ""
    };

    // --- Miniatura -----------------------------------------------------------------
    // Capturar el application_surface, reducirlo y guardarlo como PNG
    var _gw = display_get_gui_width();
    var _gh = display_get_gui_height();

    var _surf = surface_create(_gw, _gh);
    surface_copy(_surf, 0, 0, application_surface);

    var _thumb_w = 200;
    var _thumb_h = round(_gh * (_thumb_w / _gw));
    var _thumb = surface_create(_thumb_w, _thumb_h);
    surface_set_target(_thumb);
    draw_surface_stretched(_surf, 0, 0, _thumb_w, _thumb_h);
    surface_reset_target();

    // Guardar el sprite (GameMaker solo guarda PNG a través de un sprite)
    var _spr = sprite_create_from_surface(_thumb, 0, 0, _thumb_w, _thumb_h,
                                          false, false, 0, 0);
    // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
    // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
    // 14 - Persistencia y archivos.md §1.
    sprite_save(_spr, 0, game_save_id + "vn_slot" + string(_slot) + ".png");
    sprite_delete(_spr);

    surface_free(_thumb);
    surface_free(_surf);

    // --- Datos -----------------------------------------------------------------------
    var _f = file_text_open_write(game_save_id + "vn_slot" + string(_slot) + ".json");
    file_text_write_string(_f, json_stringify(_data));
    file_text_close(_f);

    return true;
}

/// @func vn_load(_slot)
function vn_load(_slot)
{
    var _path = game_save_id + "vn_slot" + string(_slot) + ".json";
    if (!file_exists(_path)) return false;

    var _f = file_text_open_read(_path);
    var _d = json_parse(file_text_read_string(_f));
    file_text_close(_f);

    global.vn_state = VNState.deserialize(_d.estado);

    // Restaurar posición exacta en el guion
    var _r = objVNRunner;
    _r.label_actual = _d.label;
    _r.indice       = _d.indice - 1;    // avanzar() lo dejará en su sitio
    _r.opciones     = [];
    _r.nodo         = undefined;

    // Reconstruir el backlog mínimo para que no quede vacío
    _r.backlog = [];

    _r.avanzar();

    return true;
}
```

---

## 6. Gestión del estado del jugador

```gml
// ---------------------------------------------------------------------------
// objVNConfig — Create (persistente)
// ---------------------------------------------------------------------------
if (variable_global_exists("vn_config_listo")) exit;
global.vn_config_listo = true;

// Texto ya leído (para el skip): clave "label_indice"
global.vn_leido = {};

// Ajustes del jugador
global.vn_config = {
    vel_texto:       1.0,     // multiplicador
    auto_avance:     false,
    volumen_musica:  0.7,
    volumen_voz:     1.0,
    volumen_sfx:     0.8,
    saltar_leido:    true
};

/// @func vn_aplicar_config()
function vn_aplicar_config()
{
    objVNRunner.vel_texto = global.vn_config.vel_texto;
    objVNRunner.auto_avance = global.vn_config.auto_avance;

    audio_group_set_gain(audiogroup_music, global.vn_config.volumen_musica, 0);
    audio_group_set_gain(audiogroup_voice, global.vn_config.volumen_voz, 0);
    audio_group_set_gain(audiogroup_sfx,   global.vn_config.volumen_sfx, 0);
}

/// @func vn_guardar_config()
function vn_guardar_config()
{
    // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
    // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
    // 14 - Persistencia y archivos.md §1.
    var _f = file_text_open_write(game_save_id + "vn_config.json");
    file_text_write_string(_f, json_stringify(global.vn_config));
    file_text_close(_f);
}

/// @func vn_cargar_config()
function vn_cargar_config()
{
    var _path = game_save_id + "vn_config.json";
    if (!file_exists(_path)) return;

    var _f = file_text_open_read(_path);
    var _d = json_parse(file_text_read_string(_f));
    file_text_close(_f);

    global.vn_config.vel_texto      = _d.vel_texto;
    global.vn_config.auto_avance    = _d.auto_avance;
    global.vn_config.volumen_musica = _d.volumen_musica;
    global.vn_config.volumen_voz    = _d.volumen_voz;
    global.vn_config.volumen_sfx    = _d.volumen_sfx;
    global.vn_config.saltar_leido   = _d.saltar_leido;

    vn_aplicar_config();
}
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Guion escrito en structs a mano | 500 líneas = 500 structs; el guionista se rinde | Formato de texto plano + parser |
| Parser sin salvaguarda anti-bucle | Un `->` mal puesto cuelga el juego | Contador de nodos ejecutados con tope |
| Typewriter sin pausas de puntuación | Suena a máquina, no a persona | Pausas de 14 frames para `.!?`, 7 para `,;:` |
| Velocidad de texto fija | Mitad de los jugadores la quieren más rápida | Configuración persistente |
| No poder saltar el texto | Segunda lectura insoportable | Pulsar = completar; Ctrl = skip |
| Voz que se solapa con la anterior | Se oyen dos frases a la vez | `audio_stop_sound()` antes de reproducir |
| Guardado sin miniatura | Nadie sabe qué partida es cuál | Captura del `application_surface` |
| No liberar las surfaces de la miniatura | Fuga de memoria en cada guardado | `surface_free()` siempre |
| `sprite_save()` sin `sprite_delete()` | Sprites dinámicos acumulados en memoria | `sprite_delete()` tras guardar |
| Backlog sin límite | Crece hasta agotar la memoria | Tope de 100 entradas con `array_delete` |
| `draw_roundrect()` sin `_ext` | Función obsoleta | `draw_roundrect_ext()` |
| Elección que se dispara dos veces | Dos clics en el mismo frame procesan dos opciones | `break` tras seleccionar |
| Retratos sin atenuar a los que no hablan | No se sabe quién está hablando | Alfa 0.45 y escala 0.94 en los secundarios |

---

## 8. Cómo escalarlo

1. **Menús de configuración completos** — velocidad, auto, volúmenes, skip,
   pantalla completa. Es lo primero que busca el jugador.
2. **Galería de CG y música** — desbloquea imágenes al verlas. Da una razón
   para rejugar.
3. **Diagrama de flujo** — un grafo visual de las decisiones tomadas (estilo
   *Zero Escape*). Muy valorado y no tan difícil: ya tienes `label` + `indice`.
4. **Minijuegos** — la ventaja de GameMaker frente a Ren'Py. Un puzle, una
   conversación por chat, una investigación de escena.
5. **Sistema de calendario** — días que avanzan, eventos por fecha (Persona).
   Reutiliza el ciclo día/noche de la receta 09.
6. **Traducción** — el parser ya lee archivos: ten `guion_es.txt` y
   `guion_en.txt`.
7. **Efectos de texto** — temblor para gritos, color para énfasis, velocidad
   variable por línea.
8. **Transiciones de escena** — fundidos, cortinillas, *pan* de cámara sobre
   el fondo.

**Cuándo pasar a otra receta:** el parser de guion que has construido sirve
para cualquier juego con datos externos. Es la técnica que usan los diálogos
del RPG (receta 04) en versión seria.

---

## 9. Fuentes

- Manual oficial — `file_text_open_read`, `file_text_read_string`,
  `file_text_eof` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/File_Handling/File_Handling.htm
- Manual oficial — Strings (`string_pos`, `string_copy`, `string_delete`,
  `string_char_at`, `string_length`, `string_digits`, `string_lower`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/Strings.htm
- Manual oficial — `string_split` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/string_split.htm
- Manual oficial — Audio (`audio_play_sound`, `audio_stop_sound`,
  `audio_sound_length`, `audio_sound_pitch`, `audio_group_set_gain`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio.htm
- Manual oficial — Surfaces y sprites dinámicos (`surface_create`,
  `surface_copy`, `sprite_create_from_surface`, `sprite_save`,
  `sprite_delete`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Surfaces.htm
- Manual oficial — `draw_roundrect_ext`, `draw_text_ext`, `draw_set_font` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms.htm
- Manual oficial — `game_get_speed(gamespeed_fps)` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/General_Game_Control.htm
- Receta propia: **04 — RPG** (grafo de diálogo con structs)
