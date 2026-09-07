# 02 · Librerías esenciales de la comunidad

> Verificado el **31 de agosto de 2026** contra la API de GitHub, la API de Codeberg y los READMEs de cada repo.
> Todas las URLs, versiones y licencias de esta página se han comprobado una a una.
> Compatibilidad declarada: **GameMaker LTS 2026.0** (IDE 2026.0.0.16 · runtime 2026.0.0.23).

---

## ⚠️ Avisos importantes antes de empezar

| Qué | Estado |
|---|---|
| **Input** se mudó de GitHub a **Codeberg** | El repo de GitHub está **archivado**. La versión actual (10.4.3) solo está en Codeberg. |
| **Chorus** | **No existe.** No hay ningún repositorio público con ese nombre de Juju Adams ni de nadie en la órbita de GameMaker. El sistema de audio de Juju Adams es **Vinyl**. |
| **GMLinear** | El repo original (`dicksonlaw583/gmlinear`) está **archivado** (2019, GameMaker Studio 1.x). El sucesor es **`gmlinear2`** (último push 2025-07-29). |
| **YYToolkit** | **No es una librería GML**. Es una herramienta externa de *modding* de juegos ya compilados. No te sirve para desarrollar tu juego. |
| **Ugg** (3D primitives) | Prácticamente **estancado**: 3 ★, último push 2025-11-13. |

---

## 1. Input — sistema de entrada multiplataforma

- **Autores:** Juju Adams, Alynne Keith y colaboradores.
- **⭐ Nueva ubicación oficial:** **<https://codeberg.org/offalynne/Input>**
  - Repo antiguo de GitHub: <https://github.com/offalynne/Input> — **312 ★, ARCHIVADO**, descripción literal: *«Moved to Codeberg 🏔️🚚»*. Último push 2026-01-30.
- **Versión actual:** **10.4.3** (release del 2026-08-19 en Codeberg). 2.878 commits, 98 tags.
- **Documentación:** <https://offalynne.grebedoc.dev/Input/>
- **Descarga (.yymps):** <https://codeberg.org/offalynne/input/releases/>
- **Licencia:** **MIT** (verificado leyendo el fichero `LICENSE` de Codeberg: «MIT License, Copyright (c) 2023 Julian Adams»). **Apta para uso comercial.**
- **Compatibilidad:** el README lo declara explícitamente: *«Input 10.4.3 — Comprehensive cross-platform input for GameMaker LTS 2026»*.
- **Qué problema resuelve:** remapeo de controles, multi-jugador local, detección de gamepad con base de datos propia, soporte de táctil, iconos de botón por dispositivo, *hotswap*, y una capa de abstracción («verbos») que desacopla *la acción* («saltar») del *dispositivo* (teclado, mando, pantalla).
- **Versiones antiguas:** Input Legacy para LTS 2022 → <https://github.com/offalynne/Input-Legacy> (release 8.1.4).

### Ejemplo mínimo

```gml
// scripts/ScrConfigurarInput/ScrConfigurarInput.gml
// Input exige definir los verbos DENTRO de __InputConfigVerbs().
// Esta función la llama la propia librería al arrancar el juego.

function __InputConfigVerbs()
{
    // InputDefineVerb(indice, nombreExport, bindingTecladoRaton, bindingGamepad, [metadata])
    // Los índices suelen declararse como macros para leerlos cómodo.
    InputDefineVerb(0, "mover_horizontal", ["A", "D", vk_left, vk_right], [gp_padl, gp_padr]);
    InputDefineVerb(1, "saltar",           ["W", vk_space, vk_up],        [gp_face1]);
    InputDefineVerb(2, "atacar",           [mb_left, "J"],                [gp_face3]);
}
```

```gml
// obj_jugador · Step
var _mover = InputCheck(1) - InputCheck(0); // Derecha - Izquierda
var _velocidad_horizontal = _mover * 4;

// InputPressed() es verdadero SOLO en el frame en que se pulsa
if (InputPressed(1) && place_meeting(x, y + 1, obj_suelo))
{
    velocidad_vertical = -12;
}
```

Funciones clave verificadas en el código fuente:

| Función | Firma | Uso |
|---|---|---|
| `InputCheck` | `(verbIndex, [playerIndex=0])` | ¿Está pulsado ahora? |
| `InputPressed` | `(verb, [playerIndex=0])` | ¿Se acaba de pulsar? |
| `InputValue` | `(verb, [playerIndex=0])` | Valor analógico (para sticks) |
| `InputDeviceIsConnected` | — | Detectar gamepads |
| `InputBindingsExport` / `InputBindingsImport` | — | Guardar/cargar remapeos del jugador |

> **Atajo:** si no quieres toda la librería, el README enlaza alternativas más ligeras: [Firehammer Input](https://firehammergames.itch.io/firehammer-input) e [Input Dog](https://github.com/messhof/Input-Dog).

---

## 2. Scribble Deluxe — texto enriquecido

- **Autor:** Juju Adams.
- **Enlace:** <https://github.com/JujuAdams/Scribble>
- **Versión:** **9.7.3** (release 2026-01-28). Último push 2026-08-10 · **415 ★**.
- **Licencia:** **MIT** → uso comercial sin problema.
- **Documentación:** <http://jujuadams.github.io/Scribble>
- **Qué problema resuelve:** el texto nativo de GameMaker no permite efectos por carácter, ni saltos de página, ni tipógrafos (*typewriter*), ni internacionalización seria. Scribble renderiza con **vertex buffers** y soporta: escritura árabe, hebrea, tailandesa y devanagari (BiDi incluido), macros, *sprites* en línea, fuentes externas, animaciones por carácter y paginación.
- **Alternativa ligera:** [ScribbleJunior](https://github.com/JujuAdams/ScribbleJunior) (25 ★, MIT, push 2026-07-16) — «*Lightweight text renderer*» si Scribble te sobra.

### Ejemplo mínimo

```gml
// Create: cachea el elemento. IMPORTANTE: no llames a scribble() en Draw.
texto = scribble("[wave][c_blue]¡Hola, [/c]mundo![/wave]");

// Draw
texto.draw(x, y);
```

```gml
// Efectos de animación disponibles (verificados en el repo):
scribble_anim_wave();    // ondulación vertical
scribble_anim_shake();   // temblor
scribble_anim_rainbow(); // arcoíris
scribble_anim_pulse();   // pulso de escala
scribble_anim_blink();   // parpadeo
scribble_anim_reset();   // quita todas las animaciones

// Dibujo con tipógrafo estilo RPG:
var _elemento = scribble("Texto que aparece poco a poco");
_elemento.draw(32, 32);
```

> ⚠️ **No** envuelvas elementos en `scribble()` dos veces: la propia librería lanza un error si le pasas un elemento ya creado. Llama al método `.draw()` directamente.

---

## 3. Chatterbox — diálogo y narrativa ramificada

- **Autor:** Juju Adams.
- **Enlace:** <https://github.com/JujuAdams/Chatterbox>
- **Versión:** **4.0.0** (release 2026-05-30). Push 2026-08-13 · **175 ★**.
- **Licencia:** **MIT**.
- **Compatibilidad:** el README lo dice literalmente: *«Narrative engine for GameMaker LTS 2026»*.
- **Documentación:** <http://jujuadams.github.io/Chatterbox>
- **Editor visual (muy recomendable):** [Crochet](https://github.com/FaultyFunctions/Crochet) — Windows, macOS, Ubuntu y versión web en <https://faultyfunctions.github.io/Crochet/>.
- **Qué problema resuelve:** escribir diálogo ramificado. Usa **ChatterScript**, un lenguaje basado en YarnScript v2 (el de *Night in the Woods*).

### Ejemplo mínimo

```gml
// Create
chatterbox = ChatterboxCreate("dialogos/npc.chatter", true, id);

// Step — avanzar con la tecla Espacio
if (keyboard_check_pressed(vk_space))
{
    chatterbox.Continue();          // pasa a la siguiente línea
}
```

```gml
// Draw — imprimir las líneas activas
var _total = chatterbox.GetContentCount();
for (var _i = 0; _i < _total; _i++)
{
    draw_text(32, 32 + 24*_i, chatterbox.GetContent(_i));
}

// Mostrar las opciones de respuesta
var _opciones = chatterbox.GetOptionCount();
for (var _j = 0; _j < _opciones; _j++)
{
    draw_text(48, 200 + 24*_j, string(_j) + ") " + chatterbox.GetOption(_j));
}

// Elegir la opción 0
// chatterbox.Select(0);
```

Métodos verificados en el código fuente: `.Jump(título)`, `.Select(índice)`, `.Continue([nombre])`, `.Stop()`, `.IsStopped()`, `.GetContent(i)`, `.GetContentCount()`, `.GetOption(i)`, `.GetOptionCount()`, `.GetCurrentNodeTitle()`, `.FindNode(título)`.

---

## 4. Audio

### Vinyl (Juju Adams) — **la recomendada**

- **Enlace:** <https://github.com/JujuAdams/Vinyl>
- **Versión:** **6.4.2-beta** (release 2026-06-03). Push 2026-07-08 · **61 ★**.
- **Licencia:** **MIT**.
- **Compatibilidad:** *«Audio tooling for GameMaker LTS 2026»*.
- **Documentación:** <http://jujuadams.github.io/Vinyl>
- **Qué problema resuelve:** el audio de GameMaker se queda corto en cuanto quieres capas, *ducking*, sincronía con el BPM, *shuffle* o *cross-fade*. Vinyl añade «patrones» (shuffle, blend, head-loop-tail), *beat tracking*, *duckers* y control por voces.

```gml
// Firma verificada: VinylPlay(patron, [loop], [gain=1], [pitch=1], [ducker], [duckPrio])
var _voz = VinylPlay("musica_nivel", true, 0.8, 1.0);

VinylMasterSetGain(0.7);        // volumen maestro
VinylStop(_voz);                // parar esa voz concreta
```

Alternativas citadas por el propio autor: [Bard Audio](https://github.com/gl326/bard-audio), [LineAudio](https://github.com/WangleLine/LineAudio), [Sonus](https://github.com/tabularelf/Sonus).

> **Sobre Chorus:** se menciona a veces como «la nueva librería de audio de Juju Adams», pero **no existe públicamente**. Búsqueda en GitHub y en el manual: cero resultados. Usa **Vinyl**.

### Otras

- **FMOD** (oficial de YoYoGames): <https://github.com/YoYoGames/GMEXT-FMOD> · Apache-2.0 · escritorio, móvil y consolas.
- **flingos-MIDI** (de nicho): <https://github.com/flingoXD/flingos-MIDI> · **3 ★** · MIT · push 2026-08-18 (verificado 2026-09-07). Extensión de reproducción **MIDI** para GameMaker — cierra un hueco real (no había ninguna opción libre de MIDI en el catálogo), pero con tracción mínima. Revísala antes de recomendarla como primera opción para un proyecto serio.

---

## 5. Iluminación, 3D y colisiones

### Bulb — luces y sombras 2D

- **Enlace:** <https://github.com/JujuAdams/Bulb> · **107 ★** · MIT · push 2026-07-08.
- **Última release:** 22.0.7 (**2024-09-25**). ⚠️ El código se actualiza (push 2026-07) pero **no publica releases desde 2024**: descarga desde la release, no desde `main`.
- **Qué problema resuelve:** luces y sombras 2D dinámicas.

### Bonk — colisiones 3D

- **Enlace:** <https://github.com/JujuAdams/Bonk> · **15 ★** · MIT · push **2026-08-27** (el más activo del lote).
- **Versión:** **4.0.0** — *«3D collisions for GameMaker LTS 2026»*.
- **Qué problema resuelve:** tests booleanos de «¿está dentro?» y tests de «empuje» (*push out*) entre formas 3D, *raycasting* y un sistema de rejilla para reducir comprobaciones.
- **Formas soportadas** (matriz verificada en el README): AABB, cápsula, cilindro, quad, caja rotada, esfera, triángulo, línea/rayo, punto.
- **Limitaciones declaradas:** cilindros y cápsulas están alineados en Z y **no se pueden rotar**; las cajas rotadas solo giran en el eje Z.

```gml
// Nomenclatura verificada en el repo:
//   Bonk<TipoA>Collide<TipoB>()  -> devuelve vector que separa las formas ("push out")
//   Bonk<TipoA>Touch<TipoB>()    -> booleano: ¿se tocan?
var _empuje = BonkAABCollideSphere(caja_x, caja_y, caja_z, caja_w, caja_h, caja_d,
                                   esfera_x, esfera_y, esfera_z, esfera_r);
if (is_struct(_empuje))
{
    x += _empuje.x;
    y += _empuje.y;
    z += _empuje.z;
}
```

> Consulta el README antes de usarla: la firma exacta de cada función varía según las formas implicadas.

### ColMesh — colisiones 3D contra malla (la clásica)

- **Enlace:** <https://github.com/TheSnidr/ColMesh> · MIT · de TheSnidr. **Descargada en la biblioteca**: `11 - Código descargado/librerias/3d/ColMesh` (255 archivos `.gml`).
- **Qué problema resuelve:** colisión de un cuerpo (esfera, cápsula) contra **mallas 3D arbitrarias** —el suelo de un nivel entero, no solo formas primitivas—. Es lo que usas para «caminar por un mundo 3D con rampas y escaleras».
- **Frente a Bonk:** Bonk es primitiva contra primitiva (rápido, para físicas simples); **ColMesh es cuerpo contra malla** (para terreno y niveles). Se complementan: Bonk para objetos, ColMesh para el mundo.
- **Formas de colisión:** esferas y cápsulas contra triángulos de malla, con un sistema espacial para no comprobar toda la malla en cada paso.

> 🔺 **ColMesh es de la era GMS 2.3**, anterior a LTS 2026. El núcleo (matemática de colisión)
> es GML puro y sigue funcionando, pero revisa las llamadas al importarla a 2026. Es la
> referencia histórica del 3D en GameMaker: mucho código de mundos 3D parte de ella.

### BBMOD — motor 3D

- **Enlace:** <https://github.com/blueburncz/BBMOD> · **119 ★** · MIT · push 2026-08-04.
- **Web / documentación:** <https://blueburn.cz/bbmod/docs/3>
- **Qué problema resuelve:** hace viable el 3D en GameMaker: modelos, materiales, animaciones, *particles*, sombras.
- **Compañero imprescindible:** el addon de Blender <https://github.com/blueburncz/BBMOD-Blender> para exportar assets.
- **Demos oficiales:** Sponza, Vehicle Demo, Zombie Demo (enlazados desde el README).

> 🕰️ **Xtreme3D** (<https://github.com/xtreme3d/xtreme3d>, 50★, `NOASSERTION`, push
> 2026-08-17, verificado 2026-09-07): motor 3D nativo (DLL) de la era **GM8/Studio 1.x**, con
> actividad residual. **BBMOD sigue siendo la recomendación moderna** para LTS 2026; Xtreme3D
> solo interesa para proyectos heredados que ya lo usan.

### Otras de Juju Adams (3D)

| Librería | Enlace | ★ | Lic. | Push | Para qué |
|---|---|---:|---|---|---|
| Cardboard | [JujuAdams/Cardboard](https://github.com/JujuAdams/Cardboard) | 3 | MIT | 2026-07-08 | Render 3D isométrico / *Z-tilt* |
| GMD3D11 | [JujuAdams/GMD3D11](https://github.com/JujuAdams/GMD3D11) | 0 | CC0-1.0 | 2026-07-14 | Funciones D3D11 |
| basic-quaternions | [JujuAdams/basic-quaternions](https://github.com/JujuAdams/basic-quaternions) | 16 | MIT | 2026-07-08 | Cuaterniones |
| Ugg | [JujuAdams/Ugg](https://github.com/JujuAdams/Ugg) | 3 | MIT | **2025-11-13** | Primitivas 3D — ⚠️ **estancada** |

> 💸 **GMPhysX** (bytecauldron, itch.io) — *bridge* real a **NVIDIA PhysX** para físicas de
> cuerpo rígido más allá de Box2D nativo y Bonk. De pago, en **alfa** y **solo Windows**
> (verificado 2026-09-07 vía itch.io e issues de `bytecauldron/gmphysx-bugs`, push
> 2026-08-16). No sustituye a Box2D nativo (`04/22`, con partículas de fluido) ni a Bonk: es
> una opción de nicho para quien necesite físicas AAA y pueda asumir el coste y la limitación
> de plataforma.

---

## 6. Interfaces de usuario (UI)

| Librería | Autor | Enlace | ★ | Lic. | Push | Nota |
|---|---|---|---:|---|---|---|
| **Bento** | Juju Adams | [JujuAdams/Bento](https://github.com/JujuAdams/Bento) | 53 | MIT | 2026-08-17 | *«Cross-platform UI framework»*. v2.3.4-alpha. **Sin releases publicadas**: hay que generar el `.yymps` desde el repo. |
| **YUI** | shdwcat | [shdwcat/YUI](https://github.com/shdwcat/YUI) | 66 | MIT | 2026-08-24 | v0.6.7. **La más completa**: ficheros de texto declarativos, *live reload*, *data binding*, plantillas, temas, animaciones, drag & drop. Extensión de VS Code. |
| **LimeUI** | Limekys | [Limekys/LimeUI](https://github.com/Limekys/LimeUI) | 36 | MIT | 2026-08-29 | Framework con **flexpanels**. Muy activa. |
| **GMUI** | erkan612 | [erkan612/GMUI](https://github.com/erkan612/GMUI) | 30 | MIT | 2026-08-10 | UI **en modo inmediato** (estilo Dear ImGui). |
| **Emu** | DragoniteSpam | [DragoniteSpam/Emu](https://github.com/DragoniteSpam/Emu) | 43 | MIT (desde 2020) | 2026-02-18 | Pensada para **herramientas y aplicaciones**, no para juegos. Documentación en la wiki de DragoniteSpam. |
| **pfb-UserInterface** | YoYoGames | [pfb-UserInterface](https://github.com/YoYoGames/pfb-UserInterface) | 3 | MIT | 2026-07-02 | Prefabs oficiales: Button, Checkbox, Dropdown, Infobox, ProgressBar, ScrollBar, Slider, Spinner, Textbox, Toggle, Slot. |

Alternativas que cita el propio Juju Adams: [PXLUI](https://github.com/1pxlchibs/PXLUI), [SimpleUI](https://github.com/evolutionleo/SimpleUI).

> **MajorGUI_GML** (erkan612, mismo autor que GMUI): <https://github.com/erkan612/MajorGUI_GML>
> · **9 ★** · MIT · push 2026-04-15 (verificado 2026-09-07). UI en **modo retenido** (frente al
> modo inmediato de GMUI). Mención breve como alternativa, no sustituye a Bento/YUI/LimeUI/GMUI
> como recomendación principal — tracción mucho menor.

---

## 7. Guardado, datos y depuración

| Librería | Autor | Enlace | ★ | Lic. | Push | Para qué |
|---|---|---|---:|---|---|---|
| **db** | Juju Adams | [JujuAdams/db](https://github.com/JujuAdams/db) | 22 | MIT | 2026-08-26 | v3.0.0. Base de datos de partida guardada sobre JSON, con **acceso «perezoso»**: si falta una clave intermedia, no crashea. |
| **Elephant** | Juju Adams | [JujuAdams/Elephant](https://github.com/JujuAdams/Elephant) | 24 | MIT | 2026-07-02 | v1.5.1. Serialización avanzada de structs/arrays: **referencias circulares**, constructores, esquemas por constructor. |
| **Snitch** | Juju Adams | [JujuAdams/Snitch](https://github.com/JujuAdams/Snitch) | 39 | MIT | 2026-07-29 | v5.0.1. *Logging* y manejo de cierres inesperados. Integra **Sentry**. |
| **iota** | Juju Adams | [JujuAdams/iota](https://github.com/JujuAdams/iota) | 48 | MIT | 2026-07-08 | v4.0.1. Delta time y dilatación temporal. |
| **DoLater** | Juju Adams | [JujuAdams/DoLater](https://github.com/JujuAdams/DoLater) | 45 | MIT | 2026-06-07 | v5.0.0. Mejora `call_later()` nativo: permite pasar argumentos. |
| **Figgy** | GlebTsereteli | [GlebTsereteli/Figgy](https://github.com/GlebTsereteli/Figgy) | 27 | MIT | 2026-08-10 | Configs **en vivo** y persistentes para afinar balance sin recompilar. |
| **Lookout** | GlebTsereteli | [GlebTsereteli/Lookout](https://github.com/GlebTsereteli/Lookout) | 21 | MIT | 2026-08-08 | *Overlays* de depuración. |
| **GMBenchmark** | DragoniteSpam | [DragoniteSpam/GMBenchmark](https://github.com/DragoniteSpam/GMBenchmark) | 34 | — | 2026-08-18 | Medir rendimiento de trozos de GML. |

### Ejemplos mínimos

```gml
// ── db: acceso seguro a datos de guardado ────────────────────────────────
// Firma verificada: db_create([datosIniciales], [datosPorDefecto])
var _datos = { settings: { audio: { musica: 1, sfx: 1 } } };
global.partida = db_create(_datos);

// Firma verificada: db_read(baseDeDatos, [clave], ...)
var _volumen = db_read(global.partida, "settings", "audio", "musica");
// Si falta cualquier nivel intermedio, devuelve undefined en vez de crashear.

// db_write(baseDeDatos, valor, [clave], ...)  → escribe
// db_default(...)                             → define la plantilla por defecto
```

```gml
// ── Snitch: logging con salida a consola, fichero y red ──────────────────
// Firma verificada: Snitch(valor, [valor], ...)
Snitch("Jugador ha entrado en la sala ", room_get_name(room), " con ", vidas, " vidas");

SnitchLogSet(true);        // activa el volcado a fichero de log
SnitchSentryBreadcrumb("checkpoint:boss");   // miga de pan para Sentry
```

```gml
// ── iota: control del tiempo ─────────────────────────────────────────────
// Firma verificada: IotaClock([identificador])
// Métodos públicos: .Update(), .AddTickMethod(método), .AddBeginTickMethod(método)
reloj = new IotaClock("principal");

// Step
reloj.Update();
```

```gml
// ── DoLater: ejecutar algo dentro de N frames, con argumentos ────────────
// Firma verificada: DoLater(frames, funcion, argumento, ...)
DoLater(30, function(_mensaje) {
    show_debug_message(_mensaje);
}, "Han pasado 30 frames");
```

---

## 8. Niveles, texturas y localización

| Librería | Autor | Enlace | ★ | Lic. | Push | Para qué |
|---|---|---|---:|---|---|---|
| **GMRoomLoader** | GlebTsereteli | [GlebTsereteli/GMRoomLoader](https://github.com/GlebTsereteli/GMRoomLoader) | 128 | MIT | 2026-08-17 | v3.1.1. Carga el contenido de **otras rooms dentro de la room actual** en tiempo de ejecución. Ideal para generación procedural, *chunking* y *stamp pools*. **Ganadora de un GameMaker Award.** |
| **Collage** | tabularelf | [tabularelf/Collage](https://github.com/tabularelf/Collage) | 29 | MIT | 2026-07-26 | v0.5.0. Constructor de *texture pages* en tiempo de ejecución. |
| **lexicon** | tabularelf | [tabularelf/lexicon](https://github.com/tabularelf/lexicon) | 52 | MIT | 2026-07-11 | v4.1.4. Localización: CSV/JSON, *fallback* de idioma, reemplazo de subcadenas, fuentes por idioma, formato fecha/número/moneda vía la librería [Unic](https://github.com/TabularElf/Unic). |
| **STANNcam** | stann-co | [stann-co/STANNcam](https://github.com/stann-co/STANNcam) | 43 | MIT | 2026-08-21 | v2.4.0. Cámara *pixel-perfect* con hasta 8 cámaras, zonas, zoom, **shake**, resoluciones de juego y GUI independientes. |
| **GML-OOP** | Mtax | [Mtax-Development/GML-OOP](https://github.com/Mtax-Development/GML-OOP) | 34 | **NOASSERTION** ⚠️ | 2026-08-29 | Constructores que envuelven las funcionalidades nativas de GameMaker. Revisa la licencia antes de usarlo en comercial. |

> 💸 **REZOL** (FoxyOfJungle, itch.io) — cámara *pixel-perfect* + escalado GUI + *split-screen*
> + HDR, más completa que STANNcam pero **de pago** (sin repo GitHub público que comparar,
> verificado 2026-09-07). Mismo tratamiento que otras herramientas de pago de FoxyOfJungle
> citadas en `12/05`: mención como alternativa, no sustituye a STANNcam como recomendación
> gratuita por defecto.

```gml
// ── GMRoomLoader: cargar una room dentro de la actual ────────────────────
// Ejemplos del README oficial:
RoomLoader.Load(rm_nivel, mouse_x, mouse_y);          // cargar en la posición del ratón

// Cargar un fragmento de mazmorra aleatorio, centrado y con espejo aleatorio
var _fragmento = tag_get_asset_ids("FragmentoMazmorra", asset_room);
carga = RoomLoader.MiddleCenter().Mirror(choose(true, false))
                  .Load(_fragmento[irandom(array_length(_fragmento)-1)], x, y);

// Capturar una room en un sprite para el menú de selección de nivel
vista_jefe = RoomLoader.Tilemaps().Sprites().ScreenshotSprite(rm_jefe);
```

```gml
// ── lexicon: localización ────────────────────────────────────────────────
// Documentación: https://tabularelf.com/lexicon/
// Soporta reemplazo de {0}…{9999} y de {nombre_variable} mediante structs,
// con fallback de idioma y carga CSV/JSON.

// Ejemplo de uso típico (consulta la doc para la API exacta de tu versión):
// Lexicon_SetLocale("es");
// draw_text(x, y, Lexicon_Get("menu.jugar"));
```

---

## 9. Herramientas de desarrollo

### GMEdit — editor de código externo

- **Autor:** YellowAfterlife.
- **Enlace:** <https://github.com/YellowAfterlife/GMEdit> · **369 ★** · **MIT** · push 2026-07-22.
- **Binarios estables:** <https://yellowafterlife.itch.io/gmedit> (**no hay releases en GitHub** — verificado: la API devuelve 404).
- **Versión online (para probar sin instalar):** <https://yellowafterlife.github.io/GMEdit/>
- **Qué problema resuelve:** el editor del IDE de GameMaker se queda corto en cuanto el proyecto crece. GMEdit usa **Ace** (el editor de la web de Cloud9), tiene editores combinados para objetos, *timelines* y extensiones, guardado incremental, temas, plugins y extensiones de sintaxis.
- **Soporta:** GameMaker: Studio, GMS2 (formatos pre-2.3 y 2.3) y soporte limitado para proyectos legacy (≤ 8.1).
- **Ojo:** se ejecuta **junto al IDE**, no lo sustituye. Hay formas de lanzar el juego desde el propio GMEdit (documentado en su wiki).

### renderdoc-gms2-kit — depurar el pipeline gráfico con RenderDoc (de nicho)

- **Enlace:** <https://github.com/odditica/renderdoc-gms2-kit> · **25 ★** · **MIT** · push **2022-08-18** ⚠️ (parado hace más de 3 años, verificado 2026-09-07).
- **Qué problema resuelve:** genera la configuración necesaria para depurar el *pipeline* gráfico de un proyecto GMS2 con **RenderDoc** (captura de *draw calls*, inspección de shaders y texturas frame a frame). Es un generador de ajustes, no código GML — hueco real: 0 menciones de RenderDoc en el resto de la biblioteca.
- **Estado honesto:** sin actividad desde 2022 y no verificado contra LTS 2026. Al limitarse a generar configuración (no depender de la API interna del runtime), probablemente sigue funcionando, pero pruébalo antes de apoyarte en él para un proyecto real.

### Otras utilidades de Juju Adams (activas en 2026)

| Librería | ★ | Lic. | Push | Para qué |
|---|---:|---|---|---|
| [SNAP](https://github.com/JujuAdams/SNAP) | 100 | MIT | 2026-07-08 | Conversores de formatos de datos (declara LTS 2022) |
| [Dynamo](https://github.com/JujuAdams/Dynamo) | 36 | MIT | 2026-07-08 | Carga dinámica de datos (declara LTS 2022) |
| [Hotglue](https://github.com/JujuAdams/Hotglue) | 8 | **sin licencia** ⚠️ | 2026-07-13 | **Fusionar proyectos** de GameMaker LTS 2026 |
| [PictureFrame](https://github.com/JujuAdams/PictureFrame) | 10 | MIT | 2026-08-16 | Calculadora de *render pipeline* |
| [Splat](https://github.com/JujuAdams/Splat) | 5 | MIT | 2026-07-28 | Caché de sprites con *vertex buffers* (LTS 2026) |
| [PRNG-Functions](https://github.com/JujuAdams/PRNG-Functions) | 5 | MIT | 2026-08-20 | Generadores pseudoaleatorios |
| [AsciiTransliterate](https://github.com/JujuAdams/AsciiTransliterate) | 1 | MIT | 2026-07-28 | Convertir Unicode a romanización ASCII |
| [Podium](https://github.com/JujuAdams/Podium) | 0 | MIT | 2026-08-28 | API unificada de leaderboards nativos |
| [Sus](https://github.com/JujuAdams/Sus) | 0 | MIT | 2026-08-28 | «*Single User System*» para juegos de un jugador |
| [Moniker](https://github.com/JujuAdams/Moniker) | 0 | MIT | 2026-08-16 | Nombres de jugador internacionalizados |
| [Allchievements](https://github.com/JujuAdams/Allchievements) | 2 | MIT | 2026-07-03 | *Wrapper* de logros multiplataforma |
| [PNGEncoder](https://github.com/JujuAdams/PNGEncoder) | 4 | **sin licencia** ⚠️ | 2026-07-28 | Codificar PNG sin pasar por disco |

---

## 10. Colecciones de scripts

| Recurso | Enlace | ★ | Licencia | Push |
|---|---|---:|---|---|
| **gmlscripts.com** | [gmlscripts/scripts](https://github.com/gmlscripts/scripts) | 85 | **NOASSERTION** ⚠️ | 2026-07-24 |
| **HelpfulGMLScripts** (PixelatedPope) | [PixelatedPope/HelpfulGMLScripts](https://github.com/PixelatedPope/HelpfulGMLScripts) | 37 | **sin licencia** ⚠️ | 2026-07-24 |
| **GMLinear 2** (dicksonlaw583) | [dicksonlaw583/gmlinear2](https://github.com/dicksonlaw583/gmlinear2) | 17 | MIT | 2025-07-29 |

- **gmlscripts.com** es la referencia histórica de la comunidad (el equivalente a «la biblioteca de snippets»). Su licencia es `NOASSERTION`: **revisa los términos en la web antes de usarlos en un producto comercial**.
- **GMLinear 2**: operaciones de matrices y vectores en GML puro, con funciones optimizadas *hard-codeadas* para vectores 2D/3D/4D y matrices 2×2, 3×3 y 4×4.
  - Requisito declarado: **GameMaker 2024.11 / 2022.0.3 LTS o superior** → compatible con LTS 2026.
  - Versiones por rama: v2.3.0 para GMS 2.3.0–2.3.7 · v2.0.0 para GMS ≤ 2.2 · [GMLinear Legacy](https://github.com/dicksonlaw583/gmlinear-legacy) para GMS 1.4.
  - ⚠️ El repo antiguo <https://github.com/dicksonlaw583/gmlinear> está **archivado** (2019).
- **BigInt** (MedicV2, de nicho): <https://github.com/MedicV2/BigInt> · **2 ★** · `NOASSERTION` ⚠️ · push 2026-08-05 (verificado 2026-09-07). Enteros de **precisión arbitraria** — GML no tiene *bigint* nativo y no hay ninguna otra librería equivalente ya catalogada, pero con 2 ★ y sin licencia SPDX clara conviene leer el código antes de confiar en él para algo serio. Apunta explícitamente a GameMaker LTS 2026.

---

## 10 bis. Descargadas en la biblioteca (barrido GitHub por estrellas, 02-09-2026)

Barrido sistemático de los repos de GameMaker mejor valorados de GitHub cruzado con lo ya
descargado. Estas cinco, de alto valor y ausentes, se **descargaron** a
`11 - Código descargado/` (búscalas con `python3 _indice/buscar.py --codigo <nombre>`):

| Recurso | Enlace | ★ | Qué aporta |
|---|---|---:|---|
| **TurboGML** (FoxyOfJungle) | [FoxyOfJungle/TurboGML](https://github.com/FoxyOfJungle/TurboGML) | 282 | Colección grande de utilidades GML: matemáticas, arrays, strings, color, dibujo. Una de las más completas |
| **gdash** (gm-core) | [gm-core/gdash](https://github.com/gm-core/gdash) | 98 | Utilidades tipo *lodash*: manipulación de arrays, structs, strings con estilo funcional. 259 scripts |
| **Kawase** (JujuAdams) | [JujuAdams/Kawase](https://github.com/JujuAdams/Kawase) | 71 | **Blur de Kawase**: desenfoque gaussiano de alta calidad y barato por shader. Mejor que el blur ingenuo |
| **AdvancedParticleSystem** (Limekys) | [Limekys/AdvancedParticleSystem](https://github.com/Limekys/AdvancedParticleSystem) | 37 | Sistema de partículas por encima del nativo: más control, efectos preconfigurados |
| **painfully-learned-lessons** (JujuAdams) | [JujuAdams/painfully-learned-lessons](https://github.com/JujuAdams/painfully-learned-lessons) | 63 | **No es código: son LECCIONES.** Problemas reales del runtime (Spine, optimización) y sus soluciones, de un desarrollador veterano |

> 💡 **`painfully-learned-lessons` merece una lectura aparte:** recoge trampas del runtime que no
> están en el manual (problemas de Spine, cuellos de botella de rendimiento) con las soluciones
> que costó encontrar. Es justo el tipo de conocimiento «no obvio» que un LLM no tiene. Está descargado en `11 - Código descargado/librerias/extras/painfully-learned-lessons`.

---

## 11. Falsos amigos: qué **no** es lo que parece

| Nombre | Realidad verificada |
|---|---|
| **Chorus** | **No existe públicamente.** Ni en GitHub ni como release. Usa **Vinyl**. |
| **YYToolkit** | Es [AurieFramework/YYToolkit](https://github.com/AurieFramework/YYToolkit): *«The definitive internal modding tool for GameMaker games»*. Inyecta código en juegos GameMaker **ya compilados**. No es una librería que importes en tu proyecto. Último push 2026-03-03. |
| **Input (GitHub)** | Archivado. La versión viva está en **Codeberg**. |
| **GMLinear (sin el 2)** | Archivado, para GameMaker Studio 1.x. |
| **Bulb** | Push reciente, pero **última release de septiembre de 2024**. |
| **Bento** | Sin releases publicadas; hay que generar el paquete a mano. |
| **Ugg** | Estancada desde noviembre de 2025. |

---

## 12. Recomendación por perfil (2026)

**Si empiezas un juego 2D hoy**, este es el conjunto más sólido y con licencias limpias (todo MIT):

1. **Input** (Codeberg) — entrada y remapeo.
2. **Scribble** — texto con efectos.
3. **Vinyl** — audio.
4. **GMRoomLoader** — niveles modulares / procedurales.
5. **Snitch** — logs y crashes.
6. **db** — partidas guardadas robustas.
7. **iota** — delta time.
8. **STANNcam** — cámara.
9. **GMEdit** — editor (si el IDE se te queda corto).

**Si haces 3D:** BBMOD + Bonk (+ GMD3D11 si necesitas D3D11 directo).

**Si haces narrativa:** Chatterbox + Crochet (editor visual) + Scribble.

**Si dudas de una licencia:** el orden de seguridad es MIT > Apache-2.0 > NOASSERTION > sin licencia. Todo lo marcado con ⚠️ **revísalo antes de publicar comercialmente**.
