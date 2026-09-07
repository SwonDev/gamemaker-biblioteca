# Trabajo pendiente — tercera ronda (2026-09-06)

> **Estado: auditorías CERRADAS, redacción a medias.** Las diez auditorías de dominio están
> terminadas y sus informes en [`auditorias/`](./auditorias/) (`r3-*.md`): son el encargo ya
> redactado, con evidencia por tema y símbolos verificados. La redacción se detuvo por límite de
> tokens semanal, no por haber terminado.

## Lo que sí quedó hecho

- **Diez auditorías de dominio** (909 temas evaluados con evidencia `archivo §sección`):
  arte y animación (92) · procedural y niveles (83) · simulación y economía (101) ·
  multijugador (78) · rendimiento (105) · datos y persistencia (93) · herramientas (99) ·
  entrada y control (98) · plataformas y legal (81) · narrativa y localización (87).
  Más [`r3-generos-faltantes.md`](./auditorias/r3-generos-faltantes.md), hecha en el hilo principal.
- **Dos documentos nuevos**: `04/46 — Eje Z falso` (595 líneas) y `04/47 — Beat em up` (858).
- **Pendientes 2-6 de la ronda anterior**, cerrados: Xbox Live, colisión isométrica, remisión de
  Box2D, versión de Vinyl, Discord/AR/*serious games*, y 9 páginas más del espejo corregidas.
- **La skill es portable**: `SKILL.md` ya no lleva ruta absoluta, y `instalar.sh` la instala en
  Claude Code, Codex, `~/.agents/skills` (Copilot y Gemini) y opencode.

## Defectos verificados y NO corregidos todavía

Son fallos reales del contenido actual. Por orden de gravedad:

1. 🔴 **Guardar en `working_directory`** — 15 ocurrencias en 10 recetas de `04` (archivos 03, 04,
   05, 06, 07, 09, 10, 11, 12, 15). Esa carpeta es de **solo lectura** en una build exportada: el
   código funciona en el IDE y falla en Windows empaquetado, móvil y macOS con sandbox. La propia
   biblioteca ya lo advierte en `01/14 §1` y en `06/scr_save_load.gml`. **Ojo al corregir:** leer
   de `working_directory` (Included Files) es legítimo; solo la escritura es el defecto.
2. 🔴 **`replay_verificar()` en `13/10 §14.3`** calcula el hash y **nunca lo compara**: da por
   bueno cualquier replay.
3. 🟠 **`08/22` línea 33** — el comentario dice «en bucle» y contradice la firma real de
   `skeleton_animation_set`; produciría animaciones rotas.
4. 🟠 **`04/09 §5.3`** — `ghost_valido` llama a `celda_construible()` y `punto_en_rango()`, que no
   se definen en ninguna parte, y no consulta la rejilla de ocupación: permite construir encima.
5. 🟠 **Citas cruzadas rotas** — `13/01` remite a `01/15` para «el profiler» y allí no está;
   `01/01 §5` promete los Workspaces y no los desarrolla; `04/28` y `13/03` no se enlazan en DPI.

## Cola de redacción (el encargo está escrito en cada informe)

**Géneros que faltan** (`r3-generos-faltantes.md`): `04/48` aventura gráfica · `04/49` deportes y
física de mesa · `04/50` juego de lucha · `04/51` colonia y constructor de bases (el hueco más
grande, lo piden dos auditorías) · ampliar `13/07` con *marching squares* y arena granular ·
ampliar `04/35` con el tablero hexagonal.

**Correcciones que cambian lo que hoy se afirma** (`r3-multijugador-online.md`): existe
`network_config_enable_reliable_udp` nativo y se manda al lector a una librería de terceros ·
HTML5 **no puede alojar servidor** y solo recibe por `network_socket_ws`/`_wss`, y no se dice en
ninguna parte · los 42 símbolos `rollback_*` dependen de Opera GX y **desaparecen en la Beta
2026.100 R2**. Faltan además tokens, *rate limiting* y *lag compensation*.

**Los dos encargos confluentes** están en
[`auditorias/r3-ENCARGOS-CONFLUENTES.md`](./auditorias/r3-ENCARGOS-CONFLUENTES.md): la última milla
de publicación (`steamcmd`, notarización de macOS, Play, App Store) y las herramientas externas de
perfilado.

**Resto por informe**: live-ops y telemetría (`r3-datos-persistencia.md`, 15 encargos) · RTL/CJK ya
resueltos por Scribble y sin documentar (`r3-narrativa-localizacion.md`, 12) · arte generado por IA
con criterio y contornos en pixel art (`r3-arte-animacion.md`, 15) · Voronoi, generación sin
congelar el frame, ciudades (`r3-procedural-niveles.md`, 10) · consola de comandos in-game
(`r3-herramientas-pipeline.md`, 9) · marcas y *fan games* (`r3-plataformas-legal.md`, 10) · IME y
mnemónicos (`r3-input-control.md`, 3) · economía con código y cosecha (`r3-simulacion-sistemas.md`, 14).

## Dos herramientas quedaron a medio hacer

- **`_indice/verificar-espejo.py`** — terminado y **ya integrado como paso 12 de
  `actualizar.py`** (antes paso 11: se desplazó un puesto al añadir la compilación de documentos,
  ver más abajo). Su medición actual: **3119 páginas comparadas · 0 ausentes · 508 incompletas ·
  84 con literales traducidos**. Lo que falta es corregir lo que detecta.

  De esas, **6 páginas ya están corregidas** (no las repitas): `gml_pragma`, `json_encode`,
  `Asynchronous_Functions/HTTP/HTTP`, `http_request`, `Quick_Start_Guide/Drawing` y
  `show_debug_message`. Dos de ellas (`json_encode` y `show_debug_message`) no estaban
  «incompletas»: eran **redacciones antiguas** de una versión anterior del manual, y hubo que
  reescribirlas enteras contra la inglesa vigente. Cuenta con ese caso al planificar el resto.

  Prioriza **los 84 literales traducidos sobre las 508 incompletas**: un literal mal traducido es
  código que falla en silencio (`"oculto"` por `"hidden"`), mientras que una página incompleta
  solo obliga a mirar la inglesa.

## ✅ El pendiente nº 1 de rondas anteriores se cerró en esta sesión

**`_indice/validar-compilacion-docs.py`** ya existía (no como `.sh`: su cabecera explica por qué —
extraer y clasificar ~3200 bloques es análisis de texto con regex, el terreno de
`validar-codigo-gml.py`, no el de un bucle `for` en bash), pero nadie lo había ejecutado de
verdad ni lo tenía enganchado a `actualizar.py`. Esta sesión:

- Lo ejecutó contra los ~3200 bloques ```gml compilables de los documentos y corrigió los errores
  reales de sintaxis que encontró (varios `daño`/`añadir`/`ya_mutó`/`sueño`/`calcular_daño` con
  ñ/tilde, un `const` inexistente en GML —usa `#macro`—, un ternario anidado sin paréntesis
  —confirmado contra el manual: GML no encadena `?:` sin ellos—, `video_draw()` llamado con 4
  argumentos cuando la firma real no lleva ninguno, fragmentos de struct/enum sin envolver, y dos
  bloques de «salida de consola» mal etiquetados como ```gml).
- Encontró y aisló un **bug real del compilador de GameMaker** (`gm-cli`/`GMAssetCompiler.dll`
  2026.0.0.23): un `function Hijo() : Padre() constructor` cuyo `Padre` no está definido en el
  mismo ámbito NO da un error de sintaxis — **crashea el compilador entero**
  (`System.ArgumentNullException` en `GML2VM.AddFuncAndPatch`), reproducido de forma aislada.
  El script ahora detecta y salta ese patrón en vez de arriesgar el crash.
- Mide 17-25 s con el corpus actual (muy por debajo del límite de 3 min), así que se integró como
  **paso 10 de `actualizar.py`** (antes se descartaba por una estimación de tiempo que nunca se
  midió en vivo).
- Última pasada limpia: **3212 de 3213 bloques compilables compilan sin error**; el único bloque
  restante se salta a propósito (el `TestSuite` de `13/10 §4.1`, herencia de un padre no definido
  en ese bloque — ver el motivo arriba).

## Cómo retomarlo

1. Los defectos verificados de arriba van primero: son fallos activos, no ausencias.
2. Cada informe `r3-*.md` trae su «Encargo para el redactor» ya escrito, con símbolos verificados.
3. Tandas de 6-7 agentes como mucho; con 19 en paralelo la sesión se queda sin cuota.
4. Al cerrar cada tanda: `python3 _indice/actualizar.py` y la fila en el índice de la carpeta.
