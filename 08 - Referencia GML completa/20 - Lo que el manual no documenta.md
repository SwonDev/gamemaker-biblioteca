# 20 · Lo que existe en el runtime y el manual no documenta

> **Investigación propia**, hecha el **2 de septiembre de 2026** cruzando los **3 453 símbolos
> del `GmlSpec.xml`** del runtime instalado (`2026.0.0.23`) contra las **3 119 páginas** del
> manual oficial en inglés.
>
> Resultado: **133 funciones existen en el runtime y no aparecen en ninguna página del
> manual.** De esas, **26 no están marcadas como obsoletas**: son funciones vivas, usables y
> sin documentación.

---

> ## ✅ Estado actualizado
>
> Este documento **cuenta** los huecos. Desde que se escribió, se han **cerrado**:
>
> | | Entonces | Ahora |
> |---|---|---|
> | Páginas del manual en español | 3 033 | **3 142 — ya no falta ninguna** |
> | Páginas que solo existían en inglés | 109 | **0** (traducidas por esta biblioteca) |
> | Símbolos vigentes que no aparecían en ningún sitio | 87 | **0** |
>
> Las cifras de abajo **siguen siendo correctas**: se refieren al manual **en inglés**, que no
> ha cambiado — esas 133 funciones siguen sin tener página oficial. Lo que ha cambiado es que
> **ya no son invisibles para quien use esta biblioteca**:
>
> - Las páginas que existían solo en inglés están traducidas y marcadas con
>   `<!-- traducido-por-la-biblioteca -->`.
> - Las 47 constantes que el manual solo escribía como rango (`ev_outside_view0...7`,
>   «hasta `argument15`») están una a una en
>   [21 · Constantes que el manual abrevia](./21%20-%20Constantes%20que%20el%20manual%20abrevia.md),
>   incluida **`pi`**, que no aparecía escrita en ninguna página del manual.
>
> `python3 _indice/actualizar.py` recalcula esta cobertura en cada ejecución, así que si un
> runtime nuevo añade símbolos, saldrán aquí como pendientes por su nombre.

### Cómo sé que no es un fallo de mi espejo

Antes de afirmar que algo «no está documentado» hay que descartar que **el espejo esté
incompleto**. Comprobado el 2 de septiembre de 2026:

| Prueba | Resultado | Qué demuestra |
|---|---|---|
| Páginas del espejo en inglés | **3 119** | — |
| URLs del `sitemap.xml` oficial | **3 119** | **El espejo está completo**: no falta ni una página publicada |
| `sitemap.xml` filtrado por «rollback» | **0 coincidencias** | Esas páginas no están publicadas |
| `clamp.htm` (página conocida) | HTTP **200** | El servidor no me está bloqueando |
| Ruta inventada `pagina_inventada_xyz.htm` | HTTP **403** | En este servidor **403 significa «no existe»**, no «prohibido» |
| `rollback_get_input.htm` | HTTP **403** | La página **no existe** |

> 🔍 **El hallazgo más llamativo:** el `GmlSpec.xml` del runtime **enlaza a páginas de manual
> que YoYo Games nunca publicó**. Por ejemplo, declara para `rollback_get_input` la URL
> `…/Rollback/Rollback_Functions/rollback_get_input.htm`, que devuelve 403. No es un enlace
> roto por una mudanza: esa sección del manual **no llegó a existir**.

---

## Por qué este documento importa

Es el punto ciego clásico de un LLM:

- Si le preguntas por `rollback_get_input`, **no la encuentra en el manual** y puede decirte
  que no existe. Existe.
- Si le preguntas por `gpu_get_tex_repeat`, puede **inventarse la firma** porque no hay página
  que consultar. Aquí está la real.
- Si encuentra `win8_appbar_enable` en código viejo, puede intentar arreglarlo. **Está muerta**:
  hay que borrarla.

> ✅ **La regla del proyecto sigue igual**: verifica siempre con
> `python3 "_indice/buscar.py" <función>`. Ese buscador lee el `GmlSpec.xml`, **no** el manual,
> así que sí conoce estas 133. Este documento explica **por qué** no tienen página.

---

## Las 26 vivas y sin documentar

### Rollback / netcode (19) — la familia más afectada

El sistema de **rollback netcode** de GameMaker está prácticamente sin páginas de manual. Es la
tecnología de multijugador con predicción y corrección que usan los juegos de lucha.

| Firma | Devuelve | Qué hace |
|---|---|---|
| `rollback_create_game(num_players, [sync_test], [region])` | — | Conecta con GXC y crea una partida del tamaño indicado. El usuario debe estar identificado en GXC |
| `rollback_join_game([dry_run])` | Bool | Comprueba si el juego se abrió desde una invitación de GXC y, si es así, se une |
| `rollback_start_game()` | — | Inicia la partida actual |
| `rollback_leave_game()` | — | Abandona la partida actual |
| `rollback_use_manual_start()` | — | Exige arranque manual: no empieza sola al conectarse todos |
| `rollback_define_player(player_object, [layer_name])` | — | Define qué objeto representa a los jugadores |
| `rollback_define_input(input_struct)` | — | Define el input que usará el sistema de rollback |
| `rollback_get_input([player_id])` | Struct | Devuelve un struct con `w,a,s,d,z,x,c,space,up,left,down,right` y sus campos `last_?` del fotograma anterior |
| `rollback_define_input_frame_delay(delay)` | — | Fija un retardo local de input en fotogramas |
| `rollback_sync_on_frame()` | Bool | Sincroniza en el fotograma actual: no avanza hasta confirmar todos los inputs |
| `rollback_get_info([player_id])` | Struct | Devuelve `player_name` y `avatar_url` del jugador |
| `rollback_chat(message, [to])` | — | Envía un mensaje de chat |
| `rollback_display_events(enabled)` | — | Activa o desactiva la visualización por defecto de los eventos de rollback (por defecto, activada) |
| `rollback_use_player_prefs([default])` | — | Activa las preferencias de jugador. **Hay que llamarla antes** de crear o unirse a una partida |
| `rollback_set_player_prefs(default)` | — | Actualiza las preferencias locales. Solo tras unirse o crear, y **antes** de empezar |
| `rollback_get_player_prefs([player_id])` | Any | Lee las preferencias de un jugador; `undefined` si no hay |
| `rollback_define_mock_input(player_id, input_struct)` | — | Input simulado para las pruebas de sincronización |
| `rollback_use_random_input(enabled)` | — | Input aleatorio para los demás jugadores en pruebas de sincronización |
| `rollback_define_extra_network_latency(latency)` | — | Añade latencia artificial para **probar en condiciones de red malas** |

> ⚠️ **La API declara una URL de manual para todas ellas** (`…/Rollback/Rollback_Functions/…`)
> **y ninguna existe.** Si un agente sigue ese enlace, se encontrará un 403 y puede concluir
> erróneamente que la función no existe. Existe: está en el `GmlSpec.xml` del runtime instalado.
>
> 💡 **Las tres últimas son de diagnóstico y valen oro.** `sync_test` más
> `rollback_define_extra_network_latency` te permiten reproducir los fallos de red **sin salir
> de tu máquina**, que es donde se pierden semanas depurando multijugador.

Contexto general del tema en [14 · Multijugador](../04%20-%20Recetas%20por%20género/14%20-%20Multijugador.md).

### Getters de GPU (3) — sus setters sí están documentados

| Firma | Devuelve | Qué hace |
|---|---|---|
| `gpu_get_tex_repeat()` | Bool | Si la repetición de texturas está activada |
| `gpu_get_tex_repeat_ext(sampler_id)` | Bool | Lo mismo para un muestreador concreto de shader |
| `gpu_get_blendequation_sepalpha()` | Array de constantes | Ecuaciones de mezcla de color y de alfa en uso |

> 🔺 Sus equivalentes `gpu_set_*` **sí tienen página**. Es una omisión del manual, no una API a
> medias: los getters funcionan.

### Flex Panels (2) — funciones de 2026 sin documentar

| Firma | Devuelve | Qué hace |
|---|---|---|
| `flexpanel_get_rounding_scale()` | Real | Factor de escala al redondear valores de disposición |
| `flexpanel_set_rounding_scale(scaleFactor)` | — | Fija ese factor. **`0` desactiva el redondeo** |

> 💡 **Útil de verdad en pixel art.** Si tu interfaz con Flex Panels queda a medio píxel y se ve
> borrosa, este es el ajuste que buscas. No está en la
> [documentación de Flex Panels](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Flex_Panels/Flex_Panels.md).

### Sueltas (2)

| Firma | Devuelve | Qué hace |
|---|---|---|
| `draw_get_circle_precision()` | Real | Precisión con la que se dibujan los círculos |
| `window_minimize()` | — | Minimiza la ventana del juego. Se restaura con `window_restore()` |

---

## Las 107 obsoletas — bórralas si las ves

El runtime las conserva por compatibilidad, pero **están marcadas como obsoletas en el propio
`GmlSpec.xml`** y no tienen página de manual. Si aparecen en código que copies, la respuesta no
es arreglarlas: es **quitarlas**.

| Familia | Nº | Qué era | Qué hacer hoy |
|---|---:|---|---|
| `win8_*` | 35 | Windows 8 / Metro | Plataforma muerta. Borrar |
| `uwp_*` | 21 | Universal Windows Platform | Ver [UWP y Xbox Live](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/UWP_And_XBox_Live/) para lo que sí sigue |
| `winphone_*` | 18 | Windows Phone | Plataforma muerta. Borrar |
| `achievement_*` | 17 | Logros y marcadores antiguos | Usar el SDK de la tienda correspondiente |
| `ads_*` | 8 | Publicidad integrada | Usar una extensión de anuncios actual |
| `push_*` | 6 | Notificaciones push antiguas | Extensiones específicas de plataforma |
| `room_set_background_color(ur)` | 2 | Fondo de room por código | Usar **capas de fondo** en el editor de rooms |

> ⚠️ **`room_set_background_colour` es la trampa más probable.** Aparece en montones de
> tutoriales de la era GMS 1.x. Hoy el fondo se define con una **capa de fondo**. Ver
> [10 · Rooms, capas, cámaras y viewports](../01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md).

---

## Variables y constantes: el mismo cruce

Aplicando el método a las **210 variables** y **886 constantes** del runtime, el resultado bruto
engaña. Hay que separar tres cosas muy distintas:

| Categoría | Nº | ¿Es un problema? |
|---|---:|---|
| **Alias de grafía** (`color`/`colour`, `gray`/`grey`, `center`/`centre`) | 13 | ❌ No. El gemelo **sí** está documentado |
| **Miembros numerados de una familia** (`argument4`…`argument14`) | 11 | ❌ No. Se documentan como familia |
| **Realmente ausentes del manual** | **67** | ✅ Sí |

### 1 · Alias de grafía — funcionan, pero no aparecen

GameMaker acepta **las dos grafías**, británica y estadounidense, pero el manual solo documenta
una. Estas 13 existen y funcionan aunque no las encuentres:

| Existe y funciona | Documentado como |
|---|---|
| `bm_dest_color` | `bm_dest_colour` |
| `bm_inv_dest_color` | `bm_inv_dest_colour` |
| `bm_inv_src_color` | `bm_inv_src_colour` |
| `bm_src_color` | `bm_src_colour` |
| `c_dkgrey` | `c_dkgray` |
| `c_grey` | `c_gray` |
| `c_ltgrey` | `c_ltgray` |
| `nineslice_center` | `nineslice_centre` |
| `phy_particle_data_flag_color` | `phy_particle_data_flag_colour` |
| `phy_particle_flag_colormixing` | `phy_particle_flag_colourmixing` |
| `seqtracktype_color` | `seqtracktype_colour` |
| `vertex_type_color` | `vertex_type_colour` |
| `vertex_usage_color` | `vertex_usage_colour` |

> 💡 **Regla práctica:** si buscas una constante con `color`, `gray` o `center` y no aparece,
> prueba con `colour`, `grey` o `centre`. Y al revés. **Las dos compilan.**

### 2 · Miembros numerados

`argument4` … `argument14` no tienen entrada propia: se documentan en la página de la familia
`argument`. Lo mismo ocurre con varios `ev_*` numerados. No es un hueco.

### 3 · Las 67 realmente ausentes

#### Rollback / netcode (22) — coherente con las funciones

Además de las 19 funciones, **toda la capa de eventos y estado del rollback está sin
documentar**. Son las constantes de evento y las variables globales que necesitas para saber
qué está pasando en la partida:

| Constante / variable | Qué señala |
|---|---|
| `rollback_api_server` | This global variable contains the gx games API url |
| `rollback_chat_message` | Fired when you receive a chat message, including those sent by the local player (in rollback_event_param) |
| `rollback_confirmed_frame` | This global variable contains the frame number for which we have confirmed input for all players |
| `rollback_connect_error` | Fired when you fail to connect to the backend |
| `rollback_connect_info` | Fired when you get info of where players should connect (in rollback_event_param) share_url |
| `rollback_connected_to_peer` | Fired when the (in rollback_event_param) player_id is connected |
| `rollback_connection_rejected` | Fired when connection attempt was rejected. The error can be caused by invalid token, mismatch in client  |
| `rollback_current_frame` | This global variable contains the network tick and can be used in rollback networking instead of wall clo |
| `rollback_disconnected_from_peer` | Fired when the (in rollback_event_param) player_id is disconnected |
| `rollback_end_game` | Fired when server wants clients to stop the game. Usually this event means that clients are in inconsiste |
| `rollback_event_id` | This global variable contains the last event id that was fired |
| `rollback_event_param` | This global variable contains a struct with parameters for the last event that was fired |
| `rollback_game_full` | Fired when the game you're trying to join is already full |
| `rollback_game_info` | Fired when you receive back info about the game (in rollback_event_param) player_id and num_players |
| `rollback_game_interrupted` | Fired when the game is interrupted by a (in rollback_event_param) player_id |
| `rollback_game_resumed` | Fired when the game resumes after being interrupted by (in rollback_event_param) player_id |
| `rollback_game_running` | This global variable contains the flag if the game is currently running |
| `rollback_high_latency` | Fired when the latency to the server is too high and it's impossible to run the game. Multiplayer session |
| `rollback_player_prefs` | Fired when you receive new preferences set by any of the players in the game, including those set by the  |
| `rollback_protocol_rejected` | Fired when connection attempt was rejected. The error means that client uses obsolete version of the prot |
| `rollback_synchronized_with_peer` | Fired when the (in rollback_event_param) player_id is done synchonizing |
| `rollback_synchronizing_with_peer` | Fired when the (in rollback_event_param) player_id is synchonizing |

> 💡 **Cómo se usan:** el evento llega en `rollback_event_id` y sus datos en
> `rollback_event_param`. `rollback_current_frame` es el reloj de red, y hay que usarlo **en
> lugar del reloj de pared** para que la simulación sea determinista.

#### Compras integradas (19) — API antigua

| Constante | Qué señala |
|---|---|
| `iap_available` | — |
| `iap_canceled` | — |
| `iap_ev_consume` | — |
| `iap_ev_product` | — |
| `iap_ev_purchase` | — |
| `iap_ev_restore` | — |
| `iap_ev_storeload` | — |
| `iap_failed` | — |
| `iap_purchased` | — |
| `iap_refunded` | — |
| `iap_status_available` | — |
| `iap_status_loading` | — |
| `iap_status_processing` | — |
| `iap_status_restoring` | — |
| `iap_status_unavailable` | — |
| `iap_status_uninitialised` | — |
| `iap_storeload_failed` | — |
| `iap_storeload_ok` | — |
| `iap_unavailable` | — |

> ⚠️ **Ojo con esta familia.** Son de la API de compras **antigua**. Para monetizar hoy, mira
> las extensiones de tienda actuales en
> [12 · Integraciones con servicios](../12%20-%20Utilidades%20e%20integraciones/03%20-%20Integraciones%20con%20servicios.md).

#### Eventos de vista (14)

`ev_outside_view1`…`7` y `ev_boundary_view1`…`7`: los eventos que se disparan cuando una
instancia sale de una vista concreta o toca su borde. La página de eventos documenta los de la
vista 0; los de las vistas 1 a 7 existen igual.

#### Ratón (6)

| Constante | Qué es |
|---|---|
| `m_axisx` | Mouse x-axis position in room coordinates |
| `m_axisx_gui` | Mouse x-axis position in GUI coordinates |
| `m_axisy` | Mouse y-axis position in room coordinates |
| `m_axisy_gui` | Mouse y-axis position in GUI coordinates |
| `m_scroll_down` | Mouse scroll direction down |
| `m_scroll_up` | Mouse scroll direction up |

> 💡 Útiles con las funciones de **dispositivo de entrada** para leer los ejes del ratón y la
> rueda como si fueran un mando.

#### Sueltas

| Símbolo | Qué es |
|---|---|
| `$$implicit_argument$$` | — |
| `in_collision_tree` | — |
| `layerelementtype_text` | The element is a text element. |
| `network_config_websocket_protocol` | Set the protocol to use on websocket upgrade message, protocol is a string as 3rd parameter |
| `os_operagx` | Opera GX |
| `vertex_usage_psize` | — |

> 💡 **`os_operagx`** es la constante de plataforma de **Opera GX**, el destino de GX.games.
> Que no esté documentada explica por qué tanta gente comprueba la plataforma con el valor
> numérico en vez de con la constante.

---

## Y al revés: 757 constantes documentadas sin página propia

De las 886 constantes del runtime, **874 no tienen página propia**, pero **757 sí aparecen
documentadas dentro de la página de su función**. Eso es normal y correcto: `bm_add` se explica
en la página de `gpu_set_blendmode`, no en una página aparte.

**Solo 117 constantes no aparecen en ningún sitio**, y casi todas pertenecen a las familias
obsoletas de arriba.

> 💡 **Consecuencia práctica:** si buscas una constante y no encuentras su página, **búscala
> dentro de la función que la usa**:
> `python3 "_indice/buscar.py" --manual "<constante>"`.

---

## Un tercer punto ciego: `fnames`, la otra lista del runtime

Toda la referencia de esta biblioteca se construyó a partir de **`GmlSpec.xml`**. Analizando
la instalación local se encontró un **segundo archivo de definición** que nadie menciona:

```
~/Library/Caches/GameMakerCLI/runtimes-gms2/runtime-2026.0.0.23/fnames
```

Es texto plano, 14 «capítulos», **3 322 símbolos únicos**, y usa sufijos como marcador de tipo:

| Forma | Significa | Ejemplo |
|---|---|---|
| `nombre(args)` | función | `nameof(name)` |
| `nombre#` | constante | `self#` |
| `nombre@` | variable integrada | `x@` |
| `nombre&` | variable de instancia | `argument_relative&` |

### El cruce

| | Símbolos |
|---|---:|
| `GmlSpec.xml` | 3 453 |
| `fnames` | 3 322 |
| En ambos | 3 288 |
| **Solo en `fnames`** | **34** |

De esos 34, **7 sí están en el manual** (así que existen y se usan, pero `GmlSpec.xml` no los
declara) y **27 no aparecen ni en `GmlSpec.xml` ni en el manual**.

> 🔍 **Eran invisibles para cualquier herramienta basada en la documentación.** Ya no: los 34
> símbolos **están integrados en el índice** de esta biblioteca y `buscar.py` los encuentra,
> marcados con un aviso de que Feather no los reconoce:
>
> ```console
> $ python3 "_indice/buscar.py" SHIFTJIS_CHARSET
> # SHIFTJIS_CHARSET  (variable)
>   ⚠️  SOLO EN `fnames`, no en GmlSpec.xml
>       Feather no la reconoce: sin autocompletado. Verifícala en tu proyecto.
> ```
>
> La fusión la hace `_indice/construir-indices.py` en cada regeneración, leyendo el runtime más
> reciente. **`GmlSpec.xml` siempre manda**: un símbolo de `fnames` nunca pisa uno suyo.

### Los 19 `*_CHARSET` — los más útiles de todos

Constantes de **juego de caracteres** para usar con `font_add`. Son las que permiten cargar una
fuente con alfabetos que no son el latino básico:

`ANSI_CHARSET` · `DEFAULT_CHARSET` · `SYMBOL_CHARSET` · `MAC_CHARSET` · `OEM_CHARSET` ·
`EASTEUROPE_CHARSET` · `BALTIC_CHARSET` · `RUSSIAN_CHARSET` · `GREEK_CHARSET` ·
`TURKISH_CHARSET` · `HEBREW_CHARSET` · `ARABIC_CHARSET` · `THAI_CHARSET` ·
`VIETNAMESE_CHARSET` · `SHIFTJIS_CHARSET` (japonés) · `HANGEUL_CHARSET` · `JOHAB_CHARSET`
(coreano) · `GB2312_CHARSET` · `CHINESEBIG5_CHARSET` (chino)

> 💡 **Por qué importan:** si tu juego tiene que mostrar cirílico, griego, árabe, japonés o
> chino, el juego de caracteres es justo lo que hay que indicar al añadir la fuente. Que no
> estén documentadas explica por qué la localización a idiomas no latinos se percibe como
> «imposible» en GameMaker. Existen desde siempre y siguen en el runtime 2026.
>
> ⚠️ **Verifícalas en tu proyecto antes de confiar en ellas.** Están en el runtime, pero al no
> estar en `GmlSpec.xml` **Feather las marcará como desconocidas** y no tendrás autocompletado.

### Dos funciones reales que no están en ninguna documentación

| Función | Familia | Contexto |
|---|---|---|
| `flexpanel_node_set_data` | Flex Panels | Complementa a `flexpanel_node_get_data`, que **sí** está documentada. Permite **escribir** el struct de datos de un nodo, no solo leerlo |
| `rollback_use_late_join` | Rollback | Incorporación tardía a una partida ya empezada. Encaja con las otras 19 funciones de rollback sin documentar |

> 💡 **`flexpanel_node_set_data` es el hallazgo más práctico.** El manual documenta el *getter* y
> dice que el struct devuelto es una referencia que se puede modificar. Que exista también un
> *setter* no aparece en ninguna parte.

### Y cinco sueltas

| Símbolo | Qué parece ser |
|---|---|
| `ev_pre_create` | La constante del evento **Pre-Create**, que el manual sí menciona como «código de precreación» al hablar de variables de objeto, pero sin dar la constante |
| `gamemaker_version` | Versión de GameMaker en tiempo de ejecución |
| `bm_complex` | Un modo de mezcla adicional |
| `button_type` · `input_type` · `text_type` | Relacionadas con los diálogos del sistema |

---

## Estructura del runtime instalado

Documentado de paso, porque no está en ningún sitio y sirve para saber **qué compila tu máquina**:

```
runtime-2026.0.0.23/          580 MB
├── GmlSpec.xml               definición de la API (la que usa buscar.py)
├── fnames                    la otra lista de símbolos (3 322)
├── BaseProject/              plantilla base de todo proyecto nuevo
├── bin/          355 MB      compiladores y herramientas
├── yyc/          162 MB      compilador nativo YYC
├── mac/           38 MB      target macOS
├── operagx/       15 MB      target GX.games (+ su propio GmlSpec.xml)
├── interpreted/  4,4 MB      máquina virtual (VM)
└── receipt.json              módulos instalados
```

**Módulos declarados en `receipt.json`:** `base`, `base-module-osx-arm64`, `mac`, `macYYC`,
`operagx`, `operagxYYC`.

> 💡 **Eso dice exactamente para qué puedes compilar en esta máquina**: macOS (VM y YYC) y
> GX.games (VM y YYC). Para Windows, Android o iOS habría que instalar sus módulos.
> El `operagx/GmlSpec.xml` es una **segunda definición de API**, específica de GX.games: por eso
> el catálogo de la biblioteca la incluye aparte.

### Cómo repetir este análisis

```sh
R=~/Library/Caches/GameMakerCLI/runtimes-gms2/runtime-<versión>

# módulos instalados = para qué puedes compilar
python3 -c "import json;print(list(json.load(open('$R/receipt.json'))))"

# símbolos de fnames, por tipo
grep -v '^//' $R/fnames | grep -c '('     # funciones
grep -v '^//' $R/fnames | grep -c '#$'    # constantes
```

---

## Cómo se ha hecho, y cómo repetirlo

```sh
# 1 · símbolos que el runtime declara
python3 -c "import json; d=json.load(open('08 - Referencia GML completa/_API del runtime/gml-api.json')); print(len(d['functions']), 'funciones')"

# 2 · ¿tiene página propia en el manual?
ls "09 - Manual oficial/manual-lts-2026-en" -R | grep -i "^rollback_get_input"

# 3 · ¿aparece mencionada en alguna parte?
python3 "_indice/buscar.py" --manual "rollback_get_input"

# 4 · la ficha real, que sale del GmlSpec.xml y no del manual
python3 "_indice/buscar.py" rollback_get_input
```

**Repite este cruce cuando actualices el runtime.** Cada versión añade funciones antes de que
el manual las documente: ese desfase es precisamente el hueco que cubre este documento.

---

## Resumen

| Dato | Valor |
|---|---:|
| Símbolos del runtime analizados | **3 453** |
| Páginas del manual (inglés) | 3 119 · **= las URLs del sitemap: el espejo está completo** |
| **Funciones** sin página propia | 243 |
| …documentadas dentro de otra página | 110 |
| …**ausentes del manual entero** | **133** |
| …de ellas, **vivas** (no obsoletas) | **26** |
| **Variables** ausentes del manual entero | 22 · **18 vivas** |
| **Constantes** ausentes del manual entero | 117 · **73 vivas** |
| …de esas, alias de grafía (el gemelo sí está) | 13 |
| …de esas, miembros numerados de una familia | 11 |
| …**realmente sin documentar (var. + const.)** | **67** |
| **Total de símbolos vivos sin documentación** | **93** |
| 🆕 Símbolos en `fnames` pero **no** en `GmlSpec.xml` | 34 · **27 tampoco en el manual** |
| **TOTAL invisible a la documentación** | **120** |

### Las tres familias que concentran el problema

| Familia | Símbolos vivos sin documentar | Estado |
|---|---:|---|
| **Rollback / netcode** | 19 funciones + 22 constantes y variables = **41** | La API entera existe **sin una sola página de manual** |
| **Compras integradas (`iap_*`)** | 19 constantes | API antigua: usa las extensiones de tienda actuales |
| **Eventos de vista (`ev_*_view1..7`)** | 14 constantes | Existen igual que los de la vista 0 |

> 🔍 **Conclusión para un agente:** ante un símbolo `rollback_*`, `iap_*` o
> `ev_outside_view3`, **no digas que no existe** porque el manual no lo recoja. Verifícalo
> siempre contra el runtime:
>
> ```sh
> python3 "_indice/buscar.py" <símbolo>
> ```
