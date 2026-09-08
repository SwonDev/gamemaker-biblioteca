# Auditoría r5 · Qué hace que un juego esté terminado, y no sea un prototipo

> Fecha: 08-09-2026 · Metodología: `_indice/auditorias/BRIEF-auditor-r4.md` (el método de la
> ronda 4 sigue vigente). 64 temas granulares en 7 bloques (envoltura, ciclo, primeros cinco
> minutos, narrativa, presentación, respeto al jugador, cierre) · **44 ✅ cubiertos** ·
> **13 🟡 parciales** · **4 🟠 medios** · **3 🔴 graves** — y, por encima de la tabla, **un
> defecto sistémico que no es ninguna fila concreta**: la prueba de imposición.
>
> Verificado contra disco con `buscar.py --todo`, `grep` en las carpetas citadas por el brief, y
> **un proyecto de prueba creado y compilado en vivo** (`gm-cli init` con la plantilla *Space
> Rocks*, `gm-cli resourcetool eval "options ..."`) para cerrar un ⚠️ que la propia biblioteca ya
> dejaba abierto en `13/11`.

## Resumen ejecutivo

**La pregunta del brief no es «¿existe el contenido?». Es «¿hay algo que obligue a usarlo?». Y
la respuesta, para el envoltorio completo de un juego, es no.**

El contenido existe y es bueno — mejor de lo que esperaba antes de auditar. `04/00 - Anatomía de
un juego completo` da el plano entero (splash → menú → intro → bucle → pausa → guardado →
endgame → créditos) con un checklist de 14 puntos al final. `04/41 - Transiciones, carga y
pausa` es, línea a línea, el documento más riguroso que he leído en esta biblioteca: pausa que
congela de verdad seis subsistemas distintos, barra de carga que no miente, confirmación de
salida con «No» por defecto — y trae su **propio** checklist de 15 puntos. `13/05 - UI y UX de
juego` tiene un checklist de **26** puntos. `04/25` y `04/27` resuelven opciones y accesibilidad
con un detalle que no tiene nada de prototipo. Si la pregunta fuera solo «¿está documentado
cómo se hace un menú de pausa que funcione de verdad», la respuesta sería un sí rotundo.

Pero un agente no lee 900 documentos por iniciativa propia: sigue el camino que la biblioteca le
marca. Y ese camino, comprobado documento por documento, **no pasa por ninguno de esos cuatro
checklists a menos que el agente ya sepa que existen**:

1. **`AGENTS.md`** — el archivo que `CLAUDE.md` ordena leer «entero antes de escribir una sola
   línea de GML» — **no menciona ni una vez** `04/00`, «menú», «pausa», «créditos», «opciones»
   ni ningún checklist de «juego completo» (verificado con `grep -n` sobre las 297 líneas del
   archivo: cero resultados). Su único gate de «terminado» es compilar limpio.
2. **`13/14 - El documento de diseño`**, el propio documento que la biblioteca describe como «el
   caso de uso propio de esta biblioteca» para que un LLM implemente sin inventar (§1.1, punto
   4), **jamás cita `04/00`** en sus 897 líneas (verificado con `grep`). Su plantilla de 19
   secciones tiene una fila «UI y UX» (2.14) que remite a `13/05`, pero nada obliga a que el
   wrapper —título, pausa, opciones, créditos— forme parte del alcance salvo que quien redacta
   el GDD ya lo sepa y lo escriba. El propio documento dice, sobre el recorte: «está escrito, no
   asumido» (§6.1) — lo cual traslada la responsabilidad exactamente a donde el brief dice que
   falla: a la memoria de quien redacta, no a un valor por defecto.
3. **`SKILL.md`** —el punto de entrada real, el que carga un agente en OTRO proyecto cuando el
   usuario pide «hazme un juego con GameMaker»— sí cita `04/00`, una vez, como primer ítem de
   «1. Plano» dentro de «Flujo para un desarrollo real» (línea 153). Es la única vía de éxito
   real que encontré. Pero es una **recomendación de lectura dentro de una lista de siete
   pasos**, no un gate: nada comprueba que el agente la haya seguido, y el paso 7 («Antes de
   publicar») no vuelve a mencionarla. Las «Prohibiciones duras» de `SKILL.md` y de `AGENTS.md`
   —la única sección de ambos documentos con forma de regla dura, no de sugerencia— tienen
   exactamente **una** condición de «terminado»: `gm-cli compile` limpio. Ninguna sobre el
   envoltorio.
4. Hay, contadas, **cuatro checklists distintos y no unificados** que cubren fragmentos
   solapados de «qué hace falta»: el de `04/00` (qué pantallas existen), el de `04/41 §4`
   (transiciones/pausa/carga correctas), el de `13/05 §4` (UI antes de publicar, 26 puntos) y el
   de `13/14 §4` (el GDD está completo). Ninguno enlaza a los otros tres como conjunto. Un
   agente que abra uno no se entera de que existen los demás.

**Conclusión de la prueba de agente** (desarrollada en detalle en la sección dedicada): un
agente que reciba «hazme un juego de plataformas» y siga la skill de forma literal **sí puede
llegar al envoltorio completo**, porque el paso 1 de `SKILL.md` lo pone delante. Pero nada lo
obliga a comprobar, antes de decir «terminado», que lo hizo — y el patrón más probable con un
agente real (que trabaja iterando sobre el bucle de juego hasta que "se siente bien" y entonces
declara la tarea cumplida) es exactamente el que describe el usuario: bucle de juego perfecto,
cero menús. Esto coincide, punto por punto, con el hallazgo ya cerrado por la propia biblioteca
en `13/14 §1.1.4`: «la ambigüedad que un humano rellenaría preguntando, el agente la rellena
inventando» — aquí la ambigüedad no es sobre una regla de diseño, es sobre si el wrapper cuenta
como parte del encargo, y hoy nada la cierra por defecto.

Además, en el bloque de **cierre** (icono del ejecutable, nombre y versión del build, metadatos
de la build) encontré un hallazgo nuevo y verificado en vivo: el subsistema `OPTIONS` de
`gm-cli resourcetool` —la única vía documentada, sin IDE, para fijar el icono/nombre/versión de
un build— devuelve `No licensed options for platform 'X'` para **todas** las plataformas
probadas en esta máquina (`main`, `windows`, `mac`, `html5`), y `options list` no imprime la
tabla de 13 plataformas que `07/13` documenta. La propia biblioteca ya había marcado esto con un
⚠️ honesto en `13/11 §4.3 bis`; esta auditoría lo confirma, lo amplía a todas las plataformas y
**cierra el nombre exacto de las propiedades** leyendo los ficheros de esquema del propio
toolchain instalado (ver hallazgo dedicado más abajo).

---

## Tabla tema por tema

Leyenda: ✅ cubierto y con receta ejecutable · 🟡 parcial (regla o mención sin receta completa) ·
🟠 documentado pero sin nada que obligue a implementarlo, o con un hueco de mecanismo real ·
🔴 falta por completo, o el mecanismo documentado no funciona tal y como está descrito.

### A · Envoltura

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| A1 | Pantalla de título/splash, saltable | ✅ | `04/00 §3` («Splash: una o dos salas cortas... Regla única: saltable») | — |
| A2 | Marca de agua/splash obligatorios del motor | ✅ (confirmado que NO aplica) | `05/02 §2` — cita literal de YoYo: «GameMaker does not force a watermark or splash screen on your games», verificado 07-09-2026 | — |
| A3 | Menú principal: Jugar/Continuar/Opciones/Créditos/Salir | ✅ | `04/00 §3` (código con `activa: file_exists(...)`) · `13/05 §2.1` (mapa de pantallas completo) | — |
| A4 | Menú de pausa completo (estructura, congelar, reanudar) | ✅✅ | `04/41 §3.4` (777-991): estructura, apertura/cierre, fondo congelado real, confirmación, foco que vuelve, cuándo NO pausar | — |
| A5 | Opciones: volumen por bus (música/SFX/voz) | ✅ | `04/25 §1-2` (`audio_group_set_gain`, aviso contra `audio_master_gain`) | — |
| A6 | Opciones: vídeo (pantalla completa, resolución, vsync) | ✅ | `04/25:75` (`window_set_fullscreen`) | — |
| A7 | Opciones: controles (rebinding teclado + mando) | ✅ | `04/25 §5` (700+ líneas: conflictos, perfiles, ejes, timeout) | — |
| A8 | Opciones: idioma | ✅ | `04/21 §3` (detectar y cambiar en caliente) | — |
| A9 | Opciones: accesibilidad (subtítulos, daltonismo, texto, reduce motion) | ✅ | `04/27` completo (888 líneas) | — |
| A10 | Pantalla de créditos, con vuelta al menú | ✅ | `04/00 §6` (código de créditos con scroll y flag `juego_completado`) | — |
| A11 | Confirmaciones de acción destructiva (salir/sobrescribir/restablecer) | 🟡 | Regla en `13/05 §2.1` regla 3 y en su checklist §4; código real solo para «salir» en `04/41 §3.4.4` (con «No» por defecto, sin `show_question()`) | No hay un **widget de confirmación modal reutilizable**; el caso «sobrescribir partida guardada» no tiene receta (ver B4b) |
| A12 | Salir del juego limpio (`game_end`, sin colgarse) | ✅ | `13/10 §8.3` (tabla: «`game_end()` deja un lienzo en blanco en HTML5: no lo llames ahí») | — |

### B · Ciclo

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| B1 | Nueva partida | ✅ | `04/00 §3` | — |
| B2 | Continuar (condicionado a partida existente) | ✅ | `04/00 §3` (`file_exists("guardado.json")`) | — |
| B3 | Selección de nivel/capítulo (bloqueado/desbloqueado, progreso) | 🔴 | `grep` en toda `04/` y `13/`: cero recetas. `04/18` da la navegación genérica (scroll de listas) y `04/04` menciona `rm_worldmap` de pasada; ninguno resuelve el **dato** (qué niveles están desbloqueados, cómo se marca completado/con estrellas) ni la UI de selección | Una receta: estructura de datos de niveles (`array` de structs con `desbloqueado`/`completado`/`mejor_puntuacion`), pantalla de selección con miniaturas, y su conexión con el guardado |
| B4 | Guardado con ranuras múltiples | ✅ (con inconsistencia) | `06 - Assets y Scripts/scr_save_load.gml` sí soporta `slot` con nombre, copias de seguridad rotativas y checksum | El sistema «recomendado» de `01/14 §9` usa `#macro ARCHIVO_GUARDADO "save01.json"` — **un único archivo hardcodeado, sin concepto de ranura**. `04/00 §1` cita los dos como si fueran la misma cosa; un agente que copie el de `01/14` (más corto, más visible) se queda sin ranuras |
| B4b | UX de ranura: metadatos (hora, zona, tiempo jugado, miniatura), indicador «guardando…», confirmación de sobrescritura | 🔴 | `grep -n "miniatura\|thumbnail\|tiempo jugado"` sobre `scr_save_load.gml`, `13/05` y `04/25`: cero resultados. **Ya lo marcó la ronda 2** (`feedback-ux.md`, hallazgo K3) como ❌; reconfirmado hoy, sigue sin existir | La ficha de ranura (hora, zona, tiempo jugado, miniatura vía `screen_save_part` o `application_surface`), el indicador que no miente, y la confirmación de sobrescritura reutilizando el widget que falta en A11 |
| B5 | Autoguardado | ✅ | `04/00 §5` («en puntos de guardado o autoguardado al cambiar de zona») | — |
| B6 | Muerte → Game Over → reintentar/menú | ✅ | `04/00 §6` | — |
| B7 | Victoria / pantalla de resultados | ✅ | `04/15 §8bis.3` — animación de tally («una pantalla de resultados que aparece ya rellena no se lee, se ignora») | — |
| B8 | Reinicio de partida/nivel | ✅ | `04/00 §6` (`room_restart()`) | — |
| B9 | Volver al menú desde cualquier pantalla | ✅ | `13/05 §2.1` regla 2 («toda pantalla tiene una salida visible») | — |
| B10 | Borrado de partida guardada | ✅ | `scr_save_load.gml` (`delete_save`) | — |

### C · Primeros cinco minutos

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| C1 | Pantalla de carga real (barra honesta, sin parpadeo) | ✅✅ | `04/41 §3.3` (`texturegroup_get_status()`, duración mínima, «algo que leer») | — |
| C2 | Logos/atribuciones legales de apertura | ✅ | Motor: no aplica (`05/02 §2`) · Assets con licencia CC: `13/25 §5` | — |
| C3 | Tutorial integrado / enseñanza por diseño | ✅✅ | `04/40` completo (943 líneas: catálogo de pasos, tres disparadores, escalada de pistas) | — |
| C4 | Primer objetivo claro | ✅ | `13/01 §5 Onboarding: enseñar sin texto` | — |
| C5 | Prompts en pantalla contextuales | ✅ | `04/40 §3.6 scr_ui_prompt` (lee dispositivo + asignación real) | — |
| C6 | Curva de dificultad de la primera zona | ✅ | `13/01 §3` y §5 (misma estructura que onboarding) | — |

### D · Narrativa cuando aplica

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| D1 | Intro/prólogo saltable (texto, cinemática, vídeo) | ✅ | `04/00 §4` (las tres formas, con `video_open`/`video_draw` verificados) | — |
| D2 | Cierre narrativo/epílogo | ✅ | `04/00 §6` (endgame) + `13/12 §2.1` (estructura de tres actos) | — |
| D3 | Diálogos con nombre de personaje | ✅ | `13/12 §6` (modelo de datos, flags, barks) | — |
| D4 | Textos de objeto/examinar | ✅ | `13/12 §3.2 Objetos y descripciones` | — |
| D5 | Tono coherente / voz por personaje | ✅ | `13/12 §4.1` («la prueba de tapar el nombre») | — |
| D6 | Todo el texto pasa por `txt()`, listo para traducir | ✅ (regla) / 🟡 (verificación) | `04/21` («ni un texto suelto en el código») | No existe un linter equivalente a `validar-proyecto.py` que detecte **literales de texto en español fuera de `txt()`** en un proyecto real; la regla depende de la disciplina del agente, sin red de seguridad automatizada |
| D7 | Créditos: roles narrativos y técnicos | ✅ (trivial) | `04/00 §6` (créditos genéricos, suficiente) | — |

### E · Presentación

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| E1 | Fuente legible (tamaño mínimo por distancia) | ✅ | `13/05 §1.2` (26 px @1080p consola, 18 px escritorio, cita XAG 101) | — |
| E2 | Paleta de color coherente | ✅ | `13/03` (pixel art y resolución) · `13/14 §2.12` (sección del GDD) | — |
| E3 | Iconografía consistente | ✅ | `13/05 §1.6 Affordance`, §3.7 | — |
| E4 | Transiciones entre pantallas/salas | ✅✅ | `04/41 §3.2` (fundido, wipe, cortinas, iris, disolución con shader) | — |
| E5 | Sonido de interfaz (foco/aceptar/cancelar/error) | ✅ | `13/05 §4` checklist («existen los cuatro sonidos») | — |
| E6 | Música por escena/estado | ✅ | `04/00 §1` · `04/26` (música adaptativa por capas) | — |
| E7 | Ajuste de ventana (pantalla completa/resolución) | ✅ | `04/25:75` | — |
| E8 | Cursor de ratón personalizado/oculto según plataforma | ✅ | `04/48` (aventura gráfica) · `13/05 §2.3` (`window_set_cursor`, verificado con `buscar.py`) | — |
| E9 | Título de la ventana (`window_set_caption`) | 🟡 | Símbolo real, verificado con `buscar.py` (existe, firma `window_set_caption(caption)`) | `grep -l` sobre toda `04/` y `13/`: **ninguna receta lo usa**. No forma parte de ningún checklist de cierre pese a ser una línea |

### F · Respeto al jugador

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| F1 | Recordar ajustes entre sesiones | ✅ | `04/25 §4` (INI) | — |
| F2 | No perder progreso (guardado robusto) | ✅✅ | `01/14 §12bis/12ter` (checksum, copia rotativa, qué pasa si se apaga a mitad) · `scr_save_load.gml` | — |
| F3 | Pausa real (congela timers, física, IA — no solo el dibujo) | ✅✅ | `04/41 §3.1` — seis subsistemas por separado: instancias, Time Sources, alarmas, partículas, Sequences, audio | — |
| F4 | Salir sin miedo (salida visible desde cualquier pantalla) | ✅ | `13/05 §2.1` regla 2 | — |
| F5 | No bloquearse (soft-lock de diseño) | ✅ | `13/14 §2.20` (diagrama de estados del jugador: «un estado sin ninguna flecha de salida... es un cuelgue de diseño») | — |
| F6 | Manejo de fallos de guardado/carga (corrupción, disco) | ✅ | `01/14 §9` (`try/catch` sobre `json_parse`) · `scr_save_load.gml` (`load_game_recover`) | — |
| F7 | Tiempos de espera razonables, sin loading mudo | ✅ | `04/41 §1.2` («una barra decorativa es peor que nada») | — |
| F8 | Opciones de comodidad (reduce motion, tope de flashes) | ✅ | `04/27 §3` (umbral WCAG de 3 destellos/s) | — |

### G · Cierre / publicación

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| G1 | Build probado empaquetado, no solo Run del IDE | ✅ | `13/10 §8.4` («el runner del IDE perdona cosas que el ejecutable no») | — |
| G1b | Build probado en una máquina sin dependencias de desarrollo | 🟡 | `13/10 §8.4` prueba el paquete, pero no en una máquina que **nunca tuvo GameMaker** (DLLs/redistribuibles que faltan es el fallo clásico de indies en Windows) | Una línea en el checklist de `05/02 §4.4`: probar el instalador en una VM/máquina limpia |
| G2 | Icono del ejecutable (ventana, taskbar, dock) | 🟠 → parcialmente 🔴 el mecanismo | `05/02 §4.4` lo pide («Icono y splash propios por plataforma») sin decir cómo. **Verificado en vivo hoy** (ver hallazgo dedicado abajo): la propiedad real es `option_windows_icon` (ruta a `.ico`), pero el comando documentado para fijarla (`resourcetool options set`) devuelve `No licensed options` en esta máquina | Documentar la propiedad real (cerrada por esta auditoría) y el fallback si `resourcetool` no está disponible (el IDE, igual que ya se documenta para el asset Extensión) |
| G3 | Nombre del producto y versión visibles en el build | 🟠 | `13/11 §4.4` (sello de versión **dentro** del juego, con `GM_version`/`GM_build_type`, ✅ ese sí funciona) — pero fijar el **nombre de producto/versión de Game Options** tiene el mismo hallazgo que G2 y G6 | — |
| G4 | Sin depuración visible (overlay, cheats) en el build final | ✅ | `01/15 §12` (`debug_mode` se apaga solo) · `13/10 §7.4-7.5` (`MODO_QA_Release false`, consola de comandos que se desactiva en release) | — |
| G5 | Sin `show_debug_message()` sobrante en producción | 🟠 | Existe un patrón de logging con niveles (`13/10 §7.2`, `NIVEL_MINIMO_Release NIVEL.AVISO`) que resuelve el problema de raíz | No está enlazado desde el checklist de release (`05/02 §4.4`); las **254** apariciones de `show_debug_message` en el resto de la biblioteca (código de ejemplo en casi cualquier receta) no llevan ningún aviso de silenciarlo/retirarlo antes de publicar |
| G6 | Metadatos de build (nombre de paquete, versión, autor) vía Game Options | 🔴 | Ver hallazgo dedicado: el subsistema `OPTIONS` de `resourcetool` no es utilizable en esta máquina para ninguna plataforma probada, y el nombre exacto de las propiedades no estaba verificado (`13/11:447` ya lo marcaba con ⚠️) | Esta auditoría cierra el nombre de las propiedades (ver abajo); falta documentar la vía alternativa (IDE) cuando `resourcetool` da «No licensed options» |
| G7 | Firma y notarización (macOS) / firma de código (Windows) | ✅✅ | `05/05` completo (`codesign`, `notarytool`, `stapler`, `signtool`) | — |
| G8 | Checklist QA/smoke test antes de publicar | ✅ | `13/10` completo | — |
| G9 | Página de tienda lista (capturas, descripción, requisitos) | ✅ | `13/11 §6` | — |
| G10 | Manejo de crashes: no silencioso, informa al jugador | ✅ | `13/11 §4.5` («el manejador amable: mensaje al jugador, autoguardado de emergencia y dónde está el log») | — |

**Recuento**: 64 temas · **44 ✅** (incluye A2, C2, D7 verificados como «no aplica») · **13 🟡**
(A11, B4, D6, E9, G1b, y las notas «qué falta» de varios ✅ marcados con matiz) · **4 🟠** (G2,
G3, G5, y el matiz de G6) · **3 🔴** (B3, B4b, G6 como mecanismo).

---

## Prueba de agente

Reproduciendo el escenario exacto del brief: «un usuario le dice a una IA "hazme un juego con
GameMaker". La IA carga la skill `gamemaker-biblioteca`».

**1. ¿El agente sabría que existe un plano completo del juego (`04/00`) antes de escribir GML?**
**Sí, si sigue `SKILL.md` al pie de la letra.** El primer paso de «Flujo para un desarrollo
real» (línea 153) lo cita explícitamente. **No, si trabaja directamente en este repo vía
`AGENTS.md`** (el archivo que `CLAUDE.md` manda leer «entero»): cero menciones, verificado.

**2. Una vez que sabe que existe, ¿algo le exige volver a comprobarlo antes de decir
"terminado"?** **No.** Ni `SKILL.md` ni `AGENTS.md` tienen un paso «7 bis: compara el resultado
contra el checklist de `04/00`». El único gate universal de ambos documentos es compilar limpio.
Un agente que interprete «terminado» como «compila y el bucle funciona» —la lectura más natural
del único gate duro que existe— cumple la letra de la skill sin menú, sin pausa, sin opciones.

**3. Si el agente escribe primero un GDD siguiendo `13/14` (la vía que la propia biblioteca
recomienda para no inventar), ¿el GDD le recuerda el wrapper?** **No por defecto.** La plantilla
de 19 secciones no tiene una fila dedicada a «pantalla de título, pausa, opciones, créditos»; la
más cercana (2.14, UI y UX) remite a `13/05`, que trata la **mecánica** de la UI (botones,
inventario, tooltips), no la lista de qué pantallas debe tener un juego completo. Y `13/14` no
cita `04/00` ni una vez en 897 líneas.

**4. ¿Sabría el agente que el sistema de guardado "recomendado" (`01/14 §9`) no tiene
ranuras, y que el que sí las tiene vive en otro archivo (`scr_save_load.gml`)?** **No de forma
clara.** `04/00 §1` cita los dos en la misma celda de tabla, como si fueran intercambiables. Un
agente que copie el primero (más corto, con nombre de función más memorable —
`guardar_partida()`/`cargar_partida()` frente a `save_game("slot1", ...)`) construye un juego
sin ranuras sin saber que eligió la opción incompleta.

**5. ¿Sabría el agente fijar el icono del ejecutable y el nombre del build sin el IDE?** **No,
verificado en vivo hoy.** El único camino documentado (`gm-cli resourcetool eval "options
..."`) devuelve `No licensed options for platform 'X'` para las cuatro plataformas probadas
(`main`, `windows`, `mac`, `html5`) en esta máquina con licencia Professional activa. La
biblioteca ya lo sabía a medias (`13/11:447`, un ⚠️ honesto) pero no ofrecía alternativa. Esta
auditoría añade el nombre real de las propiedades (leído del propio toolchain instalado, ver
abajo) pero **la vía de ejecución sigue rota** y no hay fallback documentado.

**Conclusión de la prueba**: el camino de éxito existe (`SKILL.md` → `04/00` → el resto de
recetas) y, si un agente lo sigue letra por letra desde el principio, construye un juego con
envoltorio completo. Pero no hay ningún punto de control que lo obligue a comprobar, al final,
que lo hizo — y el punto de partida más probable de un agente real (escribir primero un GDD
siguiendo la propia guía «para LLM» de la biblioteca) no lo recuerda por sí solo. Esto es
exactamente la descripción del problema que dio origen a esta ronda.

---

## Hallazgo dedicado: `OPTIONS` de `resourcetool` — verificado en vivo, 08-09-2026

**Contexto.** `13/11 §4.3 bis` ya advertía, con honestidad: «No verificado en esta sesión: el
nombre exacto de la propiedad `Version` en `OPTIONS SET`. El CLI de este equipo respondió `No
licensed options for platform 'windows'`». Esta auditoría reproduce el problema, lo generaliza y
cierra la parte que sí se puede cerrar sin licencia de exportación.

**Reproducción** (`gm-cli` 2.3.0 · `ResourceTool@2026.0.17` · runtime `2026.0.0.23` · licencia
Professional activa vía `GAMEMAKER_CLI_LICENSE`, proyecto nuevo con la plantilla *Space Rocks*):

```
$ gm-cli resourcetool eval "options list"
ResourceTool Successful                    # sin ninguna tabla — 07/13 documenta una tabla de 13 filas

$ gm-cli resourcetool eval "options info platform=windows"
No licensed options for platform 'windows'. Available:
ResourceTool Failed

$ gm-cli resourcetool eval "options info platform=mac"
No licensed options for platform 'mac'. Available:
ResourceTool Failed

$ gm-cli resourcetool eval "options info platform=html5"
No licensed options for platform 'html5'. Available:
ResourceTool Failed

$ gm-cli resourcetool eval "options get platform=main property=option_author"
No licensed options for platform 'main'. Available:
ResourceTool Failed
```

Cuatro plataformas probadas, las cuatro con el mismo error — incluida `main`, que no debería
depender de ningún módulo de exportación. La sintaxis (`platform=X property=Y value=Z`) es
correcta (el error es de licencia/entitlement, no de argumento: se comprobó con `resource types`
como control, que sí devuelve datos reales). **No verificado**: si esto es un límite de la
licencia Professional o un bug de `ResourceTool@2026.0.17`; no hay forma de distinguirlo sin
acceso a una cuenta Enterprise o a un cambio de versión, y no se debe afirmar cuál es sin esa
prueba.

**Lo que sí se pudo cerrar**: los nombres reales de las propiedades, leídos directamente de los
ficheros de esquema que trae el propio toolchain instalado (`ResourceTool`), no de terceros ni
de una suposición — la misma clase de fuente primaria que ya usa `_indice/simbolos.json` con
`GmlSpec.xml`:

```
.gmcache/project-tool/.../Formats/225/BaseProject/options/main/options_main.yy
    option_version : 100          ← ENTERO plano, NO "X.Y.Z.B" (contradice 05/02 §4.4)
    option_author, option_gameid, option_gameguid, option_steam_app_id ...

.gmcache/project-tool/.../Formats/225/BaseProject/options/windows/options_windows.yy
    option_windows_icon           : "${base_options_dir}\windows\icons\icon.ico"
    option_windows_display_name   : "Made in GameMaker Studio 2"
    option_windows_product_info   : "Made in GameMaker Studio 2"
    option_windows_company_info   : "YoYo Games Ltd"
    option_windows_executable_name: "${project_name}"
    option_windows_version        : { major, minor, revision, build }   ← estructurado, SÍ es X.Y.Z.B
    option_windows_start_fullscreen, option_windows_display_cursor, option_windows_splash_screen ...
```

**Contradicción encontrada**: `05/02 §4.4` pide «Versión en formato `X.Y.Z.B`» como un único
ítem de checklist, pero hay **dos** campos de versión distintos en el propio esquema —
`option_version` (entero plano, en Main Options, probablemente heredado) y
`option_windows_version` (objeto `{major,minor,revision,build}`, por plataforma). El checklist
no distingue cuál rellenar, y ninguno de los dos se llama `Version` a secas (la propiedad que
`13/11` intentaba adivinar).

---

## Huecos por prioridad

### 🔴 Graves

1. **No existe ningún gate que obligue a comparar el resultado contra un checklist de «juego
   completo» antes de decir «terminado».** No es una fila de la tabla: es la causa raíz detrás
   de la mitad de los 🟠/🟡. La única «Prohibición dura» de cierre en `AGENTS.md` y `SKILL.md` es
   compilar limpio. `04/00`, `04/41 §4` y `13/05 §4` tienen checklists excelentes que nadie está
   obligado a abrir.
2. **`13/14` (el GDD pensado para que un LLM implemente sin inventar) no cita `04/00` ni una
   vez.** Es la combinación más peligrosa: el documento que la biblioteca señala como su propio
   caso de uso para agentes no menciona el único documento con el checklist del envoltorio. Un
   GDD perfectamente redactado según su propia plantilla puede omitir el wrapper entero sin que
   nada lo señale.
3. **B3 — selección de nivel/capítulo**: cero recetas en toda la biblioteca. Es un elemento
   estándar de cualquier juego con niveles discretos (plataformas, puzzle, arcade) y no tiene ni
   la estructura de datos ni la pantalla.
4. **B4b — UX de ranura de guardado** (metadatos, indicador, confirmación de sobrescritura):
   confirmado hoy que sigue exactamente igual que cuando la ronda 2 lo marcó ❌.
5. **G6 — metadatos de build vía `OPTIONS`**: el mecanismo documentado (`resourcetool options
   set`) no funciona en la máquina de referencia de este proyecto, verificado en vivo, y no hay
   alternativa documentada (a diferencia del asset Extensión, que sí tiene su excepción «usa el
   IDE» explícita en `AGENTS.md §4`).

### 🟠 Medios

6. **G2/G3 — icono y nombre del build**: mismo mecanismo roto que G6; esta auditoría cierra el
   nombre de las propiedades pero no la vía de ejecución.
7. **G5 — `show_debug_message()` sin gating de producción**: el patrón correcto existe
   (`13/10 §7.2`) pero no está enlazado desde el checklist de release, y 254 usos de ejemplo en
   el resto de la biblioteca no llevan aviso.
8. **A11/B4b — falta un widget de confirmación modal reutilizable**: la regla («toda acción
   destructiva confirma, con "No" por defecto») está en tres sitios distintos pero el código
   solo existe para el caso «salir», no como componente genérico.
9. **B4 — dos sistemas de guardado documentados con distinta capacidad** (uno sin ranuras, otro
   con ranuras) citados en la misma celda de tabla de `04/00 §1`, sin distinguir cuál usar.

### 🟡 Menores

10. **D6** — sin linter que detecte texto sin `txt()` en un proyecto real (la regla existe, la
    red de seguridad automatizada no).
11. **E9** — `window_set_caption()` documentado pero usado en cero recetas.
12. **G1b** — ningún checklist pide probar el build en una máquina sin GameMaker instalado.
13. Cuatro checklists de cierre (`04/00`, `04/41 §4`, `13/05 §4`, `13/14 §4`) sin referencia
    cruzada entre ellos.

---

## Encargo para el redactor

1. **`AGENTS.md` §4 (Prohibiciones duras)** — añadir una prohibición dura nueva, al mismo nivel
   que «No des una tarea por terminada sin compilar»: *«No declares un juego "terminado" sin
   comparar el resultado, punto por punto, contra el checklist de
   `04 - Recetas por género/00 - Anatomía de un juego completo.md` (sección final) y el de
   `13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md §4`. Si algo falta, dilo
   explícitamente en vez de omitirlo.»* Sin símbolos de GML que verificar (es una regla de
   proceso, no de API).
2. **`SKILL.md`** — dos cambios:
   a. Añadir el mismo texto del punto 1 a «Prohibiciones duras» (hoy solo tiene la regla de
      compilar).
   b. En «Flujo para un desarrollo real», añadir un paso 8 explícito: *«8. **Antes de decir
      "terminado"**: compara contra `04/00` (checklist final) y `13/05 §4`; si el encargo
      recortó algo del wrapper a propósito, dilo (mismo criterio que `13/14 §1.5`: "no aplica:
      <razón>", nunca silencio).»*
3. **`13/14 - El documento de diseño`, §2 (tabla de secciones) y §3.4 (plantilla)** — añadir una
   fila nueva, **2.14 bis · Envoltorio de pantallas**, entre «UI y UX» (2.14) y «Técnica»
   (2.15): qué va (splash/menú/pausa/opciones/créditos, marcados presentes o "no aplica: <razón>"
   siguiendo el mismo criterio que ya usa `§1.5` para secciones vacías) — remite a
   `04/00` (checklist) sin repetirlo. Añadir la cita a `04/00` en el propio §1.1 punto 4 (el
   párrafo que ya explica por qué un agente necesita reglas explícitas) para que el documento
   más citado por un agente-GDD no sea ciego al wrapper.
4. **`04/00 §1` (tabla de sistemas globales)** — separar la fila «Guardado / carga» en dos, o
   añadir una nota: `01/14 §9` es el sistema mínimo (una sola partida, sin ranura) y
   `06 - Assets y Scripts/scr_save_load.gml` es el que soporta ranuras múltiples, backups y
   checksum — decir explícitamente cuál usar si el juego necesita más de una partida guardada.
5. **`04 - Recetas por género/` — nueva receta o ampliación de `04/18`**: selección de
   nivel/capítulo. Estructura de datos (array de structs con `desbloqueado`/`completado`/mejor
   resultado), pantalla con miniaturas reutilizando el patrón de scroll de `04/18`, conexión con
   `scr_save_load.gml`. Símbolos a verificar con `buscar.py` antes de escribir: ninguno nuevo
   más allá de los ya usados en `04/18` y `scr_save_load.gml`.
6. **`06 - Assets y Scripts/scr_save_load.gml` o `13/05` — UX de ranura de guardado**: ficha por
   ranura (fecha/hora con `date_datetime_string`, zona/room con `room_get_name`, tiempo jugado si
   se guarda un contador, miniatura opcional con `screen_save_part` verificado con `buscar.py`
   antes de usarlo), indicador «guardando…» no bloqueante, y el widget de confirmación genérico
   que falta en A11 (reutilizable para «sobrescribir», «salir», «restablecer ajustes», «borrar
   partida») — sin depender de `show_question()` (ya descartada en `01/15`).
7. **`05/02 §4.4` (checklist de release)** — corregir el ítem «Versión en formato X.Y.Z.B»
   distinguiendo `option_version` (Main, entero, legado) de `option_windows_version`
   (`{major,minor,revision,build}`, estructurado, el que sí encaja con X.Y.Z.B); añadir el
   nombre real de `option_windows_icon`/`option_windows_display_name`/`option_windows_product_info`
   citados en esta auditoría; añadir un ítem «silenciar o retirar `show_debug_message()` de
   depuración» con enlace a `13/10 §7.2`; añadir un ítem «probar el instalador en una máquina sin
   GameMaker instalado». Marcar con ⚠️ que `resourcetool options set/get/info` devolvió «No
   licensed options» en la máquina de referencia de este proyecto (fecha de esta auditoría) y
   documentar el fallback por IDE, con el mismo formato que la excepción ya documentada del
   asset Extensión (`AGENTS.md §4`).
8. **`13/11 §4.3 bis`** — sustituir el ⚠️ actual («no verificado el nombre exacto de la
   propiedad `Version`») por los nombres reales encontrados en esta auditoría, y ampliar el
   aviso de licencia de «windows» a las cuatro plataformas probadas.

---

## Lo que comprobé y NO hacía falta

- El contenido de `04/25` (opciones), `04/27` (accesibilidad), `13/05` (UI/UX), `13/12`
  (narrativa) y `04/40` (tutorial) — todos ya extensamente auditados y ampliados en rondas
  anteriores (ronda 2 `feedback-ux.md`, ronda 3/4). Los leí para verificar el ángulo de
  **imposición**, no el de contenido; el contenido está a la altura de lo que esas rondas ya
  documentaron. No reabro ninguno de sus veredictos ✅.
- `05/05` (firmar y notarizar) y `05/06` (consolas) — ya auditados a fondo en `r4-consolas.md`
  y `r3-plataformas-legal.md`; los usé como evidencia de que G7 está resuelto, sin volver a
  auditar su contenido.
- El manejador de crashes «amable» de `13/11 §4.5` — ya lo pedía la ronda 2 (K6, 🟡) y está
  resuelto; confirmado, no reabro.
- La regla `option_windows_version` frente a `option_version` **no estaba documentada en ningún
  sitio de la biblioteca antes de esta auditoría** (verificado con `grep` global de
  `option_windows_version` y `option_version`: cero resultados fuera de esta auditoría) — no es
  que estuviera mal, es que no existía.

## Lo que encontré desactualizado

- **`07 - Ecosistema/13 §7`** dice que `gm-cli resourcetool eval "options list"` «devuelve 13
  plataformas: main, android, html5, ios, linux, mac, operagx, ps4, ps5, switch, tvos, windows,
  xboxseriesxs». **Verificado en vivo el 08-09-2026** (`gm-cli` 2.3.0, `ResourceTool@2026.0.17`,
  runtime `2026.0.0.23`, proyecto nuevo con plantilla *Space Rocks*, licencia Professional
  activa): el comando devuelve únicamente `ResourceTool Successful`, sin ninguna tabla. No se
  puede afirmar si es un cambio de versión del CLI/ResourceTool frente a cuando se escribió
  `07/13`, o si depende de la licencia — pero la salida documentada y la salida real no
  coinciden hoy, con esa combinación de versiones exacta.
- **`05/02 §4.4`** («Versión en formato `X.Y.Z.B`») es ambiguo/parcialmente inexacto frente al
  esquema real de Game Options descubierto hoy: existen dos campos de versión con forma
  distinta (`option_version` entero en Main, `option_windows_version` estructurado por
  plataforma), y el checklist no dice cuál.
