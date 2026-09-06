# Auditoría r3 · Entrada, control y sensación de juego (game feel)

> Fecha 2026-09-06 · 98 temas evaluados · 88 cubiertos · 7 parciales · 3 faltan

## Resumen ejecutivo

El dominio de entrada está, con diferencia, sobre el nivel del resto de la biblioteca: `01 ·
Fundamentos/12` cubre teclado/ratón/gamepad con un rigor poco habitual (zona muerta axial vs.
radial vs. radial escalada, con fórmulas y matices que ni el propio manual explica), `04 · 25`
resuelve un sistema de rebinding completo con detección de conflictos y perfiles, `04 · 15`
documenta el «juice» con arquitectura y código de sobra para cualquier género, y `13 · 05 §2.2-2.3`
resuelve el foco de menú y la detección de dispositivo activo con un nivel de detalle (incluida la
inversión A/B de Nintendo) que no es habitual encontrar en español. El hueco que más duele no es
de código sino de **texto**: no hay ninguna mención a IME ni a introducir caracteres no-ASCII/CJK
(sólo se cubre *mostrarlos*, no *escribirlos*), y el «campo de texto» de UI se resuelve dos veces
de forma parcial y distinta (uno con `keyboard_lastchar`, otro con `clipboard_get_text` suelto en
la referencia) sin una receta única que las una. El segundo hueco real es conceptual: la
biblioteca no conecta nunca vsync/buffering con la latencia de input, un tema clásico de «por qué
un juego se siente responsivo» que el brief pedía explícitamente y que hoy sólo aparece como una
casilla de Game Options sin explicar su coste en frames.

## Tabla tema por tema

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| 1 | `keyboard_check` / `_pressed` / `_released`, diferencia y cuándo usar cada uno | ✅ | `01 · 12 §2` (funciones) | — |
| 2 | `keyboard_check_direct` (física, ignora el mapeo) | ✅ | `01 · 12 §2` (listada en el bloque de funciones) | — |
| 3 | Evento Key/Keyboard del objeto frente a comprobar en Step | ✅ | `01 · 12 §1` («Dos niveles de input») | — |
| 4 | Debug Overlay bloquea eventos pero no funciones; `is_keyboard_used_debug_overlay` | ✅ | `01 · 12 §1` | — |
| 5 | `ord()` solo detecta `0-9`/`A-Z` mayúsculas; constantes `vk_*` para el resto | ✅ | `01 · 12 §2` | — |
| 6 | `keyboard_lastchar` para ñ/acentos y otros caracteres fuera de `ord()` | ✅ | `01 · 12 §2`, `01 · 12 §9` (errores típicos) | — |
| 7 | Remapeo físico del teclado: `keyboard_set_map`/`get_map`/`unset_map` | 🟡 | `01 · 12 §2` (listadas) | Solo aparecen en el bloque de funciones, sin ejemplo ni cuándo usarlas frente al rebinding lógico de `04 · 25` |
| 8 | Simular pulsaciones: `keyboard_key_press`/`_release`, y que NO disparan eventos | ✅ | `01 · 12 §2` | — |
| 9 | `keyboard_string`: capturar texto tecleado | ✅ | `01 · 12 §2`, `08 · 12` (Strings) | — |
| 10 | Campo de texto de UI completo (cursor visible, backspace, límite de longitud) | 🟡 | `04 · 11` (highscore con `keyboard_lastchar`+backspace) | Es un ejemplo A-Z/0-9 de un solo caso de uso; no hay un widget reutilizable con cursor parpadeante ni selección |
| 11 | Pegar del portapapeles (`clipboard_get_text`/`has_text`/`set_text`) en un campo real | 🟡 | `08 · 12 §Portapapeles` (solo referencia) | No está enganchado a ninguna receta de campo de texto; nadie muestra cómo mezclarlo con `keyboard_string` |
| 12 | IME / entrada de caracteres CJK o Unicode fuera de ASCII | 🔴 | — | No hay ninguna mención a composición IME. `21 · Localización` y `13 · 05` cubren **mostrar** CJK (fuentes, atlas), nunca **escribirlo**. Verificado: `--texto "IME"` y `--texto "CJK.*teclado"` no devuelven nada relevante |
| 13 | `mouse_check_button`/`_pressed`/`_released`, constantes `mb_*` | ✅ | `01 · 12 §3` | — |
| 14 | `mouse_x`/`mouse_y` (room) frente a `device_mouse_x_to_gui` (GUI) | ✅ | `01 · 12 §3`, `01 · 12 §9` (error típico) | — |
| 15 | `mouse_wheel_up()`/`_down()`, que son funciones (con paréntesis) y solo en Step | ✅ | `01 · 12 §3`, `04 · 18 §3` | — |
| 16 | Funciones de ventana: `window_mouse_get_x/y`, `window_view_mouse_get_x/y` | ✅ | `01 · 12 §3` | — |
| 17 | Matiz de macOS: `mouse_x`/`mouse_y` no se actualiza en todos los frames | ✅ | `01 · 12 §3` | — |
| 18 | En táctil, botón izquierdo = toque, derecho = doble toque | ✅ | `01 · 12 §3` | — |
| 19 | Detección de gamepad con el evento Async System (`"gamepad discovered"/"lost"`) | ✅ | `01 · 12 §4`, `01 · 12 §8` (ejemplo completo) | — |
| 20 | No asumir slot 0; el slot depende del SO | ✅ | `01 · 12 §4`, `01 · 12 §9` (error típico) | — |
| 21 | El subsistema de gamepad no se inicializa sin usar una función `gamepad_*` antes | ✅ | `01 · 12 §4`, `01 · 12 §9` | — |
| 22 | `gamepad_axis_value`, `gamepad_button_check`/`_value` (analógico, gatillos) | ✅ | `01 · 12 §4` | — |
| 23 | Zona muerta axial (por eje) | ✅ | `01 · 12 §4` («Zona muerta bien hecha», punto 1) | — |
| 24 | Zona muerta radial simple y su «salto» de precisión | ✅ | `01 · 12 §4` (punto 2) | — |
| 25 | Zona muerta radial escalada (reescalado `[dz,1]→[0,1]`) | ✅ | `01 · 12 §4` (punto 3, con función `input_leer_eje_radial`) | — |
| 26 | Curva de respuesta cuadrática/cúbica sobre el eje | ✅ (marcada ⚠️ no verificada contra fuente primaria, correctamente etiquetada) | `01 · 12 §4` (punto 4) | — |
| 27 | Zona muerta exterior (stick que no llega a 1.0) | ✅ (misma etiqueta ⚠️) | `01 · 12 §4` (punto 5) | — |
| 28 | `gamepad_set_axis_deadzone` nativo: por qué no basta para un twin-stick (es axial y global al dispositivo) | ✅ | `01 · 12 §4` («Por qué… no basta») | — |
| 29 | `gamepad_set_vibration` | ✅ | `01 · 12 §4` (listada), `04 · 15 §8.4`, `04 · 27 §4.1` (con decaimiento y ajuste de accesibilidad) | — |
| 30 | Hot-plug: conectar/desconectar mando en marcha | ✅ | `01 · 12 §4`, `01 · 12 §8` | — |
| 31 | Varios mandos a la vez / elegir de qué slot lee la partida | ✅ | `04 · 25 §5.4` (`mando_slot_fijar`) | — |
| 32 | Perfiles independientes **por jugador** en local co-op (dos mandos, dos jugadores) | 🟡 | `04 · 25 §5.4` (nota explícita de límite), `04 · 02 §8` («Local co-op» con `objPlayer2`) | `04 · 25` deja explícito que su modelo es «un jugador, un dispositivo»; `04 · 02` solo tiene una viñeta de una línea sin código. No hay ninguna receta que muestre `global.controles` indexado por jugador |
| 33 | Mapeo de botones por plataforma (mandos no estándar no coinciden con las constantes) | ✅ | `01 · 12 §4` (cita literal del manual + tabla de compatibilidad) | — |
| 34 | SDL GameController DB / `gamecontrollerdb.txt` en Included Files | ✅ | `01 · 12 §4` | — |
| 35 | Iconos de botón correctos según la marca del mando conectado, en caliente | ✅ | `13 · 05 §2.3` (`marca_de_mando()`, `icono_boton()`), con ⚠️ de que es heurística, no API | — |
| 36 | Ejes exclusivos DualSense (acelerómetro/giro/orientación del propio mando) | ✅ | `01 · 12 §4` | — |
| 37 | Pérdida de foco de ventana: mandos DirectInput «se pierden» y un botón mantenido queda pegado | ✅ | `01 · 12 §4` | — |
| 38 | `gamepad_get_mapping`/`test_mapping`/`remove_mapping` (mapeos personalizados) | 🟡 | `01 · 12 §4` (listadas) | Solo enumeradas, sin ejemplo de cuándo un juego necesita escribir su propio mapeo SDL a mano |
| 39 | `gamepad_get_option`/`set_option` | 🟡 | Manual espejado (`09 · GamePad_Input/gamepad_get_option.md`) | No hay ni una línea de prosa propia sobre qué opciones expone en la práctica |
| 40 | Compatibilidad de gamepad por plataforma (Windows/macOS/Ubuntu/HTML5/iOS/Android/consolas) | ✅ | `01 · 12 §4` (tabla completa) | — |
| 41 | Abstracción en verbos (`input_saltar()`) en vez de teclas físicas | ✅ | `01 · 12 §8` (ejemplo completo nativo) | — |
| 42 | Rebinding: capturar tecla, botón de mando y eje, con estado y timeout | ✅ | `04 · 25 §5.2` | — |
| 43 | Detección y resolución de conflictos de rebinding | ✅ | `04 · 25 §5.3` | — |
| 44 | Guardar y cargar el mapeo (persistencia en `ajustes.ini`, no en la partida) | ✅ | `04 · 25 §5.6`, con la regla de por qué va en Configuración y no en el save | — |
| 45 | Restablecer valores de fábrica del rebinding, con confirmación «No» por defecto | ✅ | `04 · 25 §5.5` | — |
| 46 | UI de rebinding: overlay de captura, prompts que leen la asignación real | ✅ | `04 · 25 §5.2` (draw), `04 · 40 §2.4/§3.5/§3.6` | — |
| 47 | Librería **Input** de JujuAdams/Alynne Keith: qué aporta y cuándo usarla | ✅ | `01 · 12 §7`, `07 · 02 §1`, `10 · 10` | — |
| 48 | Ubicación correcta de Input (Codeberg, no GitHub/YoYoGames) y versión (10.4.3, LTS 2026) | ✅ | `01 · 12 §7`, `07 · 02` | — |
| 49 | API de Input: `InputCheck`/`InputPressed`/`InputReleased`/`InputRepeat`/`InputBindingSwap` | ✅ | `10 · 10` | ⚠️ menor: `07 · 02 §1` documenta `InputCheck(verbIndex, [playerIndex])` (índice numérico + `playerIndex` para multijugador) mientras `10 · 10` usa `InputCheck("verbo")` (string). Merece una nota que aclare si son dos formas válidas de la misma API o una imprecisión a corregir |
| 50 | Combos y secuencias direccionales (tipo Konami) sin la librería | ✅ | `10 · 10` (patrón de array+comparación) | — |
| 51 | Doble pulsación (dash con doble toque de dirección) | ✅ | `10 · 08` (`DoblePulsacion` constructor) | — |
| 52 | Device Input / multitáctil (`device_mouse_*`) | ✅ | `01 · 12 §5` | — |
| 53 | Gestos táctiles: tap, doble tap, drag, flick, pinch | ✅ | `01 · 12 §6`/`§8bis` | — |
| 54 | Sensibilidad de gestos (`gesture_drag_distance`, `gesture_flick_speed`, `gesture_double_tap_time`) | ✅ | `01 · 12 §8bis` | — |
| 55 | Joystick virtual completo (con zona muerta y base que «camina») | ✅ | `04 · 28 §5.3` | — |
| 56 | Botones/teclas virtuales (`virtual_key_add/show/hide/delete`) | ✅ | `04 · 28 §5.4` | — |
| 57 | Zona de acierto táctil (9 mm / 48 dp, área tocable > dibujo) | ✅ | `04 · 28 §5.1`, `13 · 05 §2.3` | — |
| 58 | Teclado virtual en móvil (`keyboard_virtual_show`, evento async de altura) | ✅ | `01 · 12 §8bis`, `04 · 28 §5.5` | — |
| 59 | Teclado en pantalla en consola/Steam Deck (Steam Input API) | ✅ | `05 · 02 §3.6` (`steam_show_gamepad_text_input`) | — |
| 60 | Inclinación/acelerómetro (`device_get_tilt_x/y/z`), calibración y zona muerta | ✅ | `04 · 28 §8.1` | — |
| 61 | Giroscopio nativo como sensor separado del acelerómetro | ✅ (aclarado como inexistente) | `04 · 28 §8.1` (implícito: solo hay tilt) | GameMaker no expone un giroscopio en bruto distinto de `device_get_tilt_*`: verificado, `--listar device_get` solo devuelve las tres funciones de tilt. Merece una línea explícita que lo diga, para que nadie busque `device_get_gyro_*` |
| 62 | Vibración en móvil (no nativa; extensión) | ✅ | `04 · 28 §8.2` (GMEXT-MobileUtils, con `--listar vibra`/`haptic` = 0 confirmando que no es nativa) | — |
| 63 | Input buffer con ventana configurable | ✅ | `06 · scr_input_buffer.gml`, `04 · 30 §5.6` (uso en combate) | — |
| 64 | Coyote time | ✅ | `06 · scr_input_buffer.gml`, `01 · 08`, `04 · 01 §4.3` | — |
| 65 | Salto variable por duración de pulsación | ✅ | `06 · scr_input_buffer.gml` (`cortar_salto`), `01 · 08`, `04 · 01 §4.2` | — |
| 66 | Aceleración y fricción (el personaje «pesa») | ✅ | `04 · 01 §4.1` | — |
| 67 | Gravedad asimétrica subida/bajada | ✅ | `04 · 01 §4.2` | — |
| 68 | Input lag: de dónde sale (orden de lectura, buffering) | 🟡 | `04 · 01` (tabla de trampas: «leer input después de mover = 1 frame de latencia») | Solo cubre el error de orden dentro del propio Step; no hay un apartado que explique las fuentes de latencia end-to-end (sondeo de dispositivo, buffering del backbuffer, refresco de pantalla) |
| 69 | Vsync y su coste en latencia de input | 🔴 | `05 · 02 §4.1` (vsync solo como casilla de Game Options), `display_reset(aa, vsync)` verificado en `08 · _API del runtime` | Vsync se documenta como ajuste visual (activado por defecto en 2026.0), nunca como fuente de retraso de input. No hay ninguna mención de `display_reset()` en prosa ni de la disyuntiva «vsync on = menos tearing, más lag» que cualquier jugador competitivo espera poder ajustar |
| 70 | Cola de comandos / encolar acciones (multi-orden con Shift) | ✅ | `04 · 13 §` (RTS: cobrar al encolar, array de órdenes) | — |
| 71 | Repetición de tecla con retardo inicial (key repeat de navegación) | ✅ | `13 · 05 §2.2` (`repeticion_paso`, 0.4 s + 0.1 s, independiente de fps) | — |
| 72 | Mantener pulsado / accesibilidad hold-to-toggle | ✅ | `04 · 27 §4` | — |
| 73 | Navegación de menú con teclado+mando+ratón a la vez | ✅ | `13 · 05 §2.2/§2.3`, `04 · 18 §3` | — |
| 74 | Las cinco leyes del foco (siempre uno, visible, orden explícito, se mueve si se desactiva, se recuerda al volver) | ✅ | `13 · 05 §2.2` | — |
| 75 | Envolvente (wrap): sí en listas cortas, no en sliders ni listas largas | ✅ | `13 · 05 §2.2` (tabla) | — |
| 76 | Sonido de navegación al mover el cursor | ✅ | `04 · 18 §3` | — |
| 77 | Primer elemento seleccionado al abrir una pantalla | ✅ | `13 · 05 §2.2` (ley 1) | — |
| 78 | Atrás/cancelar, con la inversión A/B de Nintendo frente a Xbox/PS | ✅ | `13 · 05 §1.4` | — |
| 79 | Teclas de acceso rápido / mnemonics en menús (saltar directo a una pestaña por letra) | 🔴 | — | No hay ninguna mención. Verificado: `--texto "mnemonic"`, `"letra subrayada"`, `"salto de pestaña"` = 0 resultados en las 11 carpetas de contenido |
| 80 | Navegación por rejilla (grid, inventario) en dos ejes | ✅ | `13 · 05 §2.2` (`foco_rejilla`) | — |
| 81 | Scroll de listas largas: desplazamiento entero + suavizado por separado | ✅ | `04 · 18 §4` | — |
| 82 | Detección del último dispositivo usado (teclado/ratón/mando) y cambio de iconos en caliente | ✅ | `13 · 05 §2.3` | — |
| 83 | Accesibilidad: remapeo completo como requisito | ✅ | `04 · 27 §4` (enlaza a `04 · 25 §5`) | — |
| 84 | Un solo botón (accesibilidad y como género propio) | ✅ | `04 · 27 §4`, `04 · 11` (género completo) | — |
| 85 | Asistencia de puntería como ajuste de accesibilidad | ✅ | `04 · 34 §4.4/§5.5` | — |
| 86 | Sin QTE de ventana imposible, o con alternativa | ✅ | `04 · 27` (checklist Basic) | — |
| 87 | Slider de vibración (no solo on/off) | ✅ | `04 · 27 §4.1` | — |
| 88 | Grabar y reproducir input (`debug_input_record/save/playback`) | ✅ | `13 · 10 §7.1` | — |
| 89 | `keyboard_key_press`/`_release` para automatizar pruebas | ✅ | `01 · 12 §2` | — |
| 90 | Probar sin mando (comprobaciones `gamepad_is_connected` antes de leer) | ✅ | Presente en todos los ejemplos de gamepad de `01 · 12`, `04 · 25`, `13 · 05` | — |
| 91 | Feedback inmediato en capas (7 cosas en 300 ms) | ✅ | `04 · 15 §1` | — |
| 92 | Hit stop / freeze frames, con arquitectura de orden (Begin Step) | ✅ | `04 · 15 §4.2`, `§3` (core loop) | — |
| 93 | Screen shake (con trauma) | ✅ | `04 · 15 §4.1`, `§5.1` | — |
| 94 | Squash & stretch | ✅ | `04 · 15 §4.3`, `§5.3` | — |
| 95 | Knockback | ✅ | `04 · 15 §4.5`, `§5.4` | — |
| 96 | Zoom punch y retroceso de cámara | ✅ | `04 · 15 §8.3` | — |
| 97 | Vibración de mando como capa de feedback (quinta capa) | ✅ | `04 · 15 §8.4` | — |
| 98 | Por qué un juego «se siente bien»: una única fuente de efectos, no repartida | ✅ | `04 · 15 §2` | — |

## Huecos por prioridad

### 🔴 Graves
1. **IME / entrada de texto no-ASCII y CJK.** La biblioteca documenta cómo *mostrar* CJK
   (fuentes, atlas de glifos) pero no una sola línea sobre cómo *se escribe* con un IME activo:
   qué le llega a `keyboard_string`/`keyboard_lastchar` durante la composición, si GameMaker
   soporta la fase de composición de un IME de escritorio, o si hay que apoyarse en el teclado
   virtual también en desktop para estos idiomas. Bloquea a cualquier agente que intente
   localizar un juego a japonés/chino/coreano con entrada de texto (nombre de personaje, chat).
2. **Teclas de acceso rápido / mnemonics en menús.** Cero menciones. No es tan crítico como el
   punto 1, pero es una pauta de usabilidad estándar (Alt+letra, salto directo de pestaña) que
   cualquier menú de opciones con varias pestañas (justo el que ya existe en `04 · 25`) se
   beneficiaría de tener documentada, aunque sea como variante opcional.

### 🟠 Medios
3. **Vsync y su relación con la latencia de input.** `display_reset(aa, vsync)` existe y está
   verificado en el índice de símbolos, pero en toda la biblioteca vsync se trata solo como un
   ajuste visual (tearing) — nunca se conecta con el frame de retraso que añade, un tema de
   «sensación de control» explícitamente pedido en el brief y relevante para cualquier juego de
   acción rápida.
4. **Campo de texto de UI como widget reutilizable.** Existen dos soluciones parciales y
   descosidas: una en `04 · 11` (A-Z/0-9 con `keyboard_lastchar` + backspace, pensada solo para
   iniciales de highscore) y `clipboard_get_text`/`has_text`/`set_text` documentadas en
   `08 · 12` sin ningún consumidor. Ningún documento las une en un campo de texto genérico con
   cursor visible, selección y pegar, que es lo que necesita un chat, un nombre de partida largo
   o un campo de búsqueda.
5. **Perfiles de input por jugador en local co-op.** `04 · 25` resuelve bien el caso «un
   jugador, varios dispositivos posibles» y dice explícitamente que no cubre splitscreen; el
   único puntero real (`04 · 02 §8`) es una viñeta de una línea sin código. Un agente que reciba
   «añade un segundo jugador con su propio mando» no tiene de dónde partir salvo intuir la
   estructura de datos él mismo.

### 🟡 Menores
6. `keyboard_set_map`/`get_map`/`unset_map` están solo listadas, sin ejemplo de cuándo remapear
   a nivel de driver de teclado tiene sentido frente al rebinding lógico de verbos.
7. `gamepad_get_mapping`/`test_mapping`/`remove_mapping` (mapeos SDL manuales) están solo
   listadas, sin receta de cuándo un estudio necesita escribir su propio mapeo.
8. `gamepad_get_option`/`set_option` no tienen ni una línea de prosa propia (solo el manual
   espejado).
9. Discrepancia de firma entre `07 · 02 §1` (`InputCheck(verbIndex, [playerIndex])`) y `10 · 10`
   (`InputCheck("verbo")`) para la librería Input — no es un símbolo de GML nativo así que no
   rompe la regla de «nunca inventar una función», pero merece una nota que lo aclare la próxima
   vez que se revise esa librería externa.
10. No hay una línea explícita que diga «GameMaker no tiene giroscopio nativo separado del
    acelerómetro, solo `device_get_tilt_*`» — se deduce del silencio, pero decirlo evita que un
    LLM futuro busque `device_get_gyro_x` y alucine que existe.
11. `input lag` como concepto de «de dónde sale» solo cubre el error de orden de lectura en el
    Step; falta un cuadro que enumere las demás fuentes (sondeo de dispositivo, USB polling rate,
    buffering de vídeo) aunque GameMaker no dé control directo sobre casi ninguna.

## Encargo para el redactor

1. **Ampliar `01 · Fundamentos/12 - Input - teclado, ratón y gamepad.md`, nueva sub-sección en
   §2 (Teclado) o §8bis**, con IME y texto no-ASCII: qué recibe `keyboard_string` cuando el
   sistema operativo tiene un IME de composición activo (japonés, chino, coreano) en Windows/
   macOS/Linux, si hace falta el teclado virtual también en desktop para esos idiomas, y un
   enlace desde `21 · Localización` (que ya cubre mostrar CJK) para cerrar el círculo
   mostrar↔escribir. Símbolos a verificar antes de escribir: `keyboard_string`,
   `keyboard_lastchar` (ya verificados existentes; falta comprobar en el manual real —
   `gm-cli manual read`— si documentan compatibilidad IME explícitamente antes de afirmar nada).
2. **Nueva sub-sección en `04 · 25 - Menú de opciones y ajustes.md` o en `13 · 05`**: un widget
   `scr_ui_campo_texto` que una `keyboard_string` + `keyboard_lastchar` (para el filtrado de
   caracteres) + `clipboard_get_text`/`clipboard_has_text` (pegar) + un cursor parpadeante
   (`current_time mod 1000 < 500` o similar) + selección con Shift+flechas. Símbolos verificados:
   `keyboard_string`, `keyboard_lastchar`, `clipboard_get_text`, `clipboard_has_text`,
   `clipboard_set_text`, `string_copy`, `string_delete`, `string_insert`, `string_length`.
3. **Ampliar `01 · 12 §4` o `04 · 15`** con un apartado corto «Vsync y latencia de input»: qué es
   `display_reset(aa, vsync)`, la disyuntiva tearing-vs-latencia, y una recomendación de exponer
   el ajuste de vsync como opción de accesibilidad/rendimiento en `04 · 25` (ya tiene la
   infraestructura de sliders/toggles). Símbolo verificado: `display_reset(aa, vsync)`.
4. **Ampliar `04 · 25 §5.4`** (o nueva sección `§5.8`) con un ejemplo mínimo de perfiles de
   input **por jugador** para local co-op: un array `global.controles_jugador[n]` en vez de un
   único `global.controles`, y cómo `input_mover_x(_jugador)` indexa en él. Enlazar desde
   `04 · 02 §8` y `04 · 14`. No requiere símbolos nuevos, es reestructurar la forma de datos ya
   verificada en `04 · 25 §5.1`.
5. **Nota corta en `13 · 05 §2.2`** (leyes del foco) sobre mnemonics/accesos rápidos por letra en
   menús con pestañas — opcional, mencionar como patrón adicional junto a la navegación por
   flechas ya documentada, con el ejemplo de `04 · 25 §5.4` (pestañas Q/E) como base a la que
   añadir el atajo de letra.
6. **Una línea en `01 · 12 §4`** aclarando que no existe un giroscopio nativo distinto de
   `device_get_tilt_x/y/z` — cierra la puerta a que un LLM futuro invente `device_get_gyro_*`.
7. **Menciones opcionales, no urgentes:** un ejemplo de `keyboard_set_map` frente al rebinding
   lógico (§6 de huecos menores), y un ejemplo de `gamepad_test_mapping`/`gamepad_get_mapping`
   para cuando el SDL Gamepad DB integrado no reconoce un mando exótico.

## Lo que comprobé y NO hacía falta

- **Zona muerta de sticks analógicos** — parecía candidata a hueco por lo mucho que se repite el
  error en foros, pero `01 · 12 §4` la resuelve con más rigor (axial/radial/radial escalada/curva
  de respuesta/zona exterior, con fórmulas) que la mayoría de tutoriales publicados.
- **Rebinding con detección de conflictos** — asumía que sería un hueco típico («se puede
  remapear pero sin comprobar choques»); `04 · 25 §5.3` lo resuelve entero, con UI de
  confirmación incluida.
- **Iconos de botón por marca de mando** — pensaba que solo se resolvería «usa la librería
  Input»; en realidad `13 · 05 §2.3` da una heurística nativa completa (`marca_de_mando()`) y
  avisa explícitamente de que es heurística y no una API oficial.
- **Coyote time / input buffer / salto variable** — el trío clásico de "plataformero que se
  siente bien" no solo está explicado, tiene un script reutilizable completo
  (`06 · scr_input_buffer.gml`) con constructores `InputBuffer`, `CoyoteTime` y `JumpHelper`.
- **Convención de Aceptar/Cancelar y la inversión A/B de Nintendo** — di por hecho que sería un
  hueco de matiz de plataforma; `13 · 05 §1.4` lo tiene explícito y correcto.
- **Vibración como ajuste de accesibilidad con decaimiento** — no esperaba encontrar el detalle
  de «nunca sumar fuerza indefinidamente, sustituir el pulso» ya resuelto con código
  (`04 · 27 §4.1`).
- **Testing con grabación de input** — `debug_input_record/save/playback` con sus tres
  constantes de filtro y el evento de finalización están documentados en `13 · 10 §7.1`, listos
  para un flujo de regresión real.
- **Joystick virtual táctil** — esperaba un esbozo simple; `04 · 28 §5.3` incluye el detalle fino
  de que la base «camina» tras el dedo si se sale del radio, que es justo lo que distingue un
  joystick virtual bueno de uno mediocre.
