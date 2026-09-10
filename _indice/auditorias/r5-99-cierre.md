# Cierre de la quinta ronda — auditoría final

> 8 de septiembre de 2026. Auditor de cierre, sin escribir documentación: verifico con evidencia
> lo que la ronda dice haber hecho, contra disco. Criterio de éxito: las palabras del usuario —
> que un agente con esta skill tenga *«conocimiento absoluto y actual… al nivel de un auténtico
> experto de la industria»*, y que al pedirle un juego **no** «se limite a usar assets de baja
> calidad o crear basura» ni se salte especificación, menús o historia.
>
> Nota de proceso: no se ha ejecutado ningún juego ni `gm-cli run` (restricción del usuario). Se
> ha usado `buscar.py`, `gm-cli compile` no hizo falta (la compilación real ya la certifica
> `actualizar.py`, paso 10), y se han ejecutado los validadores. **En curso, no defecto**: durante
> esta auditoría se detectó actividad concurrente sobre `_indice/validar-integracion.py`
> (`git diff` pasó de 0 líneas a +151 entre dos ejecuciones mías de `actualizar.py`, con `ps aux`
> sin mostrar el proceso — corre fuera de esta shell) — es el agente que el encargo anticipaba,
> revisando los avisos de `global.X` sin escribir y clasificándolos en un catálogo
> `EXCEPCIONES_GLOBALS_LECTOR` con motivo documentado por cada uno, además de tocar de refilón
> `04/09` y `13/22`. Cada ejecución de `actualizar.py` de esta auditoría (§5) dio `EXIT_CODE=0`
> pase lo que pasara ese trabajo en paralelo, así que no invalida ninguna de las comprobaciones de
> aquí — se anota, no se evalúa como propio.

---

## 1 · La prueba del agente novato, en seco

Leído `_indice/skills/gamemaker-biblioteca/SKILL.md` de arriba a abajo, sin ningún otro contexto,
como haría un agente que la carga por primera vez.

### 1. «Hazme un juego de plataformas». ¿Qué haces antes de crear el proyecto? ¿Te obliga a algo?

**Sí, con un gate real.** `## Flujo para un desarrollo real`, paso 0 (línea 162-166):

> «0. **Especificación**: si el encargo es «hazme un juego» y no trae ya género, alcance y
> plataforma decididos, pregúntalos en un único turno (nunca un interrogatorio secuencial) y
> completa con los valores por defecto lo que el usuario no conteste — preguntas, criterio de
> parada, defaults y plantilla en `13/28`. Escribe la especificación y **enséñasela al usuario
> antes de crear el proyecto**: no hay paso 2 sin este documento escrito primero.»

El paso 2 («Proyecto: `gm-cli init`…») queda explícitamente bloqueado hasta que exista el
documento. Un agente que lea el flujo entero no puede saltarse esto de forma defendible.

**Matiz real, no cosmético**: esta obligación vive en `## Flujo para un desarrollo real`, no en
`## Prohibiciones duras` (línea 146-158), la lista de reglas absolutas junto a «no editar `.yy` a
mano» o «nada está hecho sin `gm-cli compile` limpio». Un agente que solo repasara esa lista de
prohibiciones (el bloque con más peso retórico del documento, todo en negrita y con «nunca»/
«nada») no encontraría ahí la obligación de especificar antes de crear el proyecto — tendría que
llegar hasta el flujo, dos secciones más abajo, para verla. No es un «no» a la pregunta 1, pero sí
un hueco de posición: el gate más importante de la ronda no está donde están las demás reglas que
no admiten excepción.

### 2. ¿Cómo sabes qué preguntar y qué asumir si el usuario contesta «lo que veas»?

**Sí, y en detalle.** El paso 0 remite a `13/28`, que:
- da las **ocho preguntas mínimas** con su formato (§1-§2),
- fija el **criterio de parada** explícito: «como máximo, una repregunta — y solo sobre dos de las
  ocho» (§2.2, línea 152),
- dedica una sección entera a qué hacer si el usuario dice «lo que veas», «sorpréndeme» o no
  responde (línea 171 en adelante), con un ejemplo trabajado completo («Hazme un juego de
  plataformas, algo cortito, lo que veas.», línea 278-284) que muestra qué se asume y qué se
  pregunta de verdad.

Comprobado con `grep`: 0 apariciones de «lo que veas»/«sorpréndeme» relacionadas con elicitación
en el resto de la biblioteca antes de este documento — la respuesta vive solo aquí, pero vive.

### 3. ¿Sabes que tu juego necesita menú, pausa, opciones y créditos, y dónde está la lista para comprobarlo?

**No — este es el defecto real de la ronda.** `04 - Recetas por género/00 - Anatomía de un juego
completo.md` tiene desde esta ronda un `## El checklist de "juego completo"` (línea 272) que
consolida los cuatro checklists antes sueltos (15 puntos de `04/41`, 26 de `13/05`, el de `13/14`
y el de `05/02 §4.4`), y **tres** de esos cuatro (`04/41 §4`, `13/05 §4`, `13/14 §4`) ya remiten de
vuelta a él con el enlace `#el-checklist-de-juego-completo` — el enlace resuelve, comprobado
contra el `slug` real del encabezado. Es exactamente el trabajo que pedía el encargo #2.

> 📌 **Nota fechada el 2026-09-10.** Las cifras de esta auditoría eran ciertas en r5 y
> han envejecido: `04/41 §4` tiene hoy **16** casillas y `13/02 §5`, **18**. Se dejan como
> estaban porque una auditoría es un registro de un momento, no un documento vivo, y
> reescribirla sería falsear la medida. La lección sí es viva: **un recuento escrito en
> prosa sobre OTRO documento caduca en silencio**. Por eso la skill enlaza las listas y no
> dice cuántas casillas tienen. Lo encontró un agente contándolas en una prueba a ciegas.

Pero **ni `SKILL.md` ni `AGENTS.md`** — los dos ficheros que un agente lee para saber cómo operar
esta biblioteca — mencionan esa lista en ningún punto:

```
$ grep -n "04/00\|checklist" AGENTS.md          →  0 resultados
$ grep -n "04/00\|checklist" SKILL.md           →  1 resultado (línea 167, solo como
                                                     lectura de "Plano", no como gate de cierre)
$ grep -n "menú\|pausa\|créditos\|opciones" SKILL.md
                                                 →  0 resultados (salvo "pausa" una vez,
                                                     como nombre de una de 46 recetas)
```

`SKILL.md` cita `04/00` una vez, en el paso 1 («Plano»), como material de lectura junto a otros
cuatro documentos — nunca como el criterio que decide si el juego está terminado. El paso 6
(«Compila») y el paso 7 («Antes de publicar») no lo mencionan. Un agente que siga el flujo al pie
de la letra puede compilar limpio, pasar por «Antes de publicar» y no saber que existe una lista
de 14+15+26 puntos que comprueba si hay menú, pausa, opciones o créditos. La infraestructura
existe y está bien enlazada **entre los documentos de diseño**; no está enganchada al único sitio
donde un agente que solo carga la skill la vería. Es el mismo patrón que ya diagnosticó
`r5-juego-completo.md` para `AGENTS.md`, y sigue sin cerrar en el fichero que un agente lee de
verdad al arrancar.

### 4. Necesitas un sprite y no tienes ninguno. ¿Qué te dice la skill? ¿Acabarías dibujando un rectángulo?

**No dibujarías un rectángulo — y la skill te lo dice explícitamente, incluso te avisa de que no
lo hagas.** La tabla «Qué leer según la tarea» de `SKILL.md` tenía, antes de esta auditoría, una
referencia rota: la fila «No tengo sprites ni sonidos» apuntaba a `12 - …/09 §7`, que en el
documento real es «Interpretar los errores del compilador» — nada que ver con gráficos. La
sección real que resuelve esto es `12/09 §5.2`, que además dice literalmente: «🔴 La regla que
gobierna las tres alternativas de abajo: en ningún caso se entrega un rectángulo o un cuadrado de
color plano como sprite final», y da tres peldaños con código verificado (silueta biped por
`surface_create`/`draw_circle_color`/`draw_ellipse_color`, assets libres de `07/09`, y
`codex exec` + `gpt-image-2`). **Corregido durante esta auditoría** (línea 128 de `SKILL.md`,
propagado al `AGENTS.md` generado de la skill con `actualizar.py`) — antes de la corrección, un
agente que siguiera la tabla al pie de la letra habría llegado a una sección sobre errores de
compilación y, sin encontrar nada sobre sprites ahí, habría podido concluir razonablemente que no
existe guía y volver al rectángulo por defecto.

### 5. Creas una fuente con `resourcetool`. ¿Te avisa de que no se verá nada?

**Sí, de forma explícita y repetida.** Es la Trampa 5 de las seis que `SKILL.md` obliga a leer
«antes de escribir un solo comando» (línea 73-77): «Una fuente creada con `resourcetool` compila
limpio y no dibuja ni una letra… Hornéalo con Pillow a partir de un `.yy` de referencia, o abre el
IDE una vez». El detalle completo, con el porqué (`"glyphs":{}` vacío, rasterizar es trabajo del
IDE) y las dos soluciones reales, está en `12/09` Trampa 5 — once párrafos, con el comando exacto
para detectarlo (`font glyphlist name=...`) y el aviso de que un `.yy` mal formado en el proceso
no falla limpio, tumba el toolchain entero con un `AccessViolationException`.

### 6. Has compilado con exit 0. ¿La skill te deja decir que está terminado?

**No.** Es una de las ocho `## Prohibiciones duras`: «Nada está «hecho» sin `gm-cli compile`
limpio y su salida real reportada» — y el propio paso 6 del flujo lo repite: «Recuerda que
compilar limpio **no** significa que el código sea correcto (trampa 4)». Las trampas 5 y 6 (fuente
muda, `directory_exists()` mintiendo) están en la misma lista obligatoria de lectura previa, así
que un agente que la haya leído sabe que «exit 0» no basta ni para gráficos ni para guardado. Lo
que el flujo **no** hace es citar, en el paso 6 o 7, el procedimiento concreto que ya existe para
cazar justo esos dos casos (`13/10 §8.6`: capturar la pantalla y mirarla de verdad + matar el
proceso y volver a lanzarlo) — la obligación de desconfiar está, el procedimiento paso a paso para
cumplirla no está enlazado desde el flujo que un agente sigue línea a línea, solo desde el propio
`12/09`.

### Resumen de la prueba

| # | Pregunta | Veredicto |
|---|---|---|
| 1 | Especificación antes de crear el proyecto | ✅ obliga, con matiz de posición (no está en «Prohibiciones duras») |
| 2 | Qué preguntar / qué asumir con «lo que veas» | ✅ completo, vía `13/28` |
| 3 | Sabe que hace falta menú/pausa/opciones/créditos, y dónde comprobarlo | 🔴 **no** — `04/00` tiene la lista maestra, pero ni `SKILL.md` ni `AGENTS.md` la citan como gate |
| 4 | No dibuja un rectángulo sin sprite | ✅ tras la corrección de esta auditoría (cita rota `§7`→`§5.2`) |
| 5 | Avisa de que una fuente de `resourcetool` no se ve | ✅ completo (Trampa 5) |
| 6 | No deja decir «terminado» solo por compilar limpio | 🟡 la prohibición está, el procedimiento de verificación (`13/10 §8.6`) no está enlazado desde el flujo |

Cuatro de seis, sólidas. Una corregida en el momento (cita rota). Una sigue abierta de verdad
(pregunta 3): es el defecto central de esta ronda, explicado con más detalle en la §5.

---

## 2 · Encargo → estado real, con evidencia

| Encargo | Estado | Evidencia |
|---|---|---|
| `13/28` — protocolo de elicitación | ✅ hecho | Documento nuevo, 8 preguntas + criterio de parada (§2.2) + manejo de «lo que veas» (línea 171) + ejemplo trabajado (línea 278). `python3 buscar.py --todo` lo indexa. |
| Paso 0 en los tres puntos de entrada (`SKILL.md`, `AGENTS.md §5`, `13/06 §2`) | ✅ hecho, los tres | `SKILL.md:162-166` (paso 0, imperativo, bloquea el paso 2). `AGENTS.md:192-197` (regla verificable: «es un encargo que incluye diseñar… si no trae ya una especificación»). `13/06` línea 82-88 (paso 0 del método, «Sin esto no hay paso 1», enlaza a `13/28`). |
| `04/00` como lista maestra + tres listas que remiten a ella | ✅ hecho | `04/00:272` `## El checklist de "juego completo"` consolida 4 checklists. `04/41:998`, `13/05:2381`, `13/14:51,213,457,483` enlazan de vuelta con el anchor `#el-checklist-de-juego-completo` (verificado que resuelve). **Pero** ver §1, pregunta 3: `SKILL.md`/`AGENTS.md` no citan esta lista como gate — el encargo literal («04/00 como lista maestra y las tres listas que remiten a ella») está cumplido; el objetivo de fondo (que un agente la use) no del todo. |
| `04/57` — Selección de nivel y capítulo | ✅ hecho, documento sólido | Nuevo, 280 líneas. Regla «desbloqueado se calcula, nunca se guarda» (§1.3/§3.3) con código real (`nivel_desbloqueado()`). Enlaza con `scr_save_load.gml`, `04/18` (scroll), `04/06` (metroidvania), `13/14 §2.20` (grafo de gating). Símbolos verificados: `struct_exists`, `draw_sprite_ext`, `draw_text_color`, `string_repeat` — todos reales. |
| `06/scr_ui_confirmar.gml` | ✅ hecho | Script nuevo, generaliza el patrón de `04/41 §3.4.4` (que la propia receta señalaba «sin generalizar»). `04/41:934-937` ya enlaza de vuelta. `13/05 §3.5` lo documenta como componente m). Símbolos verificados: `gamepad_is_connected`, `gamepad_button_check_pressed`, `is_callable`, `display_get_gui_width/height`, `draw_rectangle_color`, `draw_text_color` — todos reales, firmas correctas. |
| `07/24` — Logotipo, icono, capsule | ✅ hecho, documento sólido | Nuevo, 341 líneas. Tres piezas (logo/icono/capsule) con receta ejecutable, tabla de propiedades por plataforma sacada de `options info` real, bug de Windows documentado con evidencia (`file` confirma `PNG image data` en vez de `.ico`), técnica squircle de macOS verificada. **Pero** ver §3 — sus cifras de propiedad (`icon`, verificadas en vivo) entran en conflicto con lo que citan `13/11`/`05/02` (`option_windows_icon`), que dicen basarse en este mismo documento. |
| Escalera de `12/09 §5.2` | ✅ hecho, resuelve el defecto que `r5-assets.md` encontró en la ronda anterior | Sustituye el `magick -size 64x64 xc:"#ff3366"` (un cuadrado liso) por 3 peldaños con código real y verificado: silueta biped por superficie (`surface_create`/`draw_circle_color`/`draw_ellipse_color`/`sprite_create_from_surface`, firmas verificadas), assets libres (`07/09`), IA (`codex exec`+`gpt-image-2`). Tabla de «calidad mínima exigible» con 5 criterios comprobables. |
| Seis trampas de `12/09` | ✅ presentes y consistentes con el resumen de `SKILL.md` | `12/09:23-292`, seis subsecciones completas, cada una con síntoma, causa, y solución verificada. `SKILL.md:60-83` las resume fielmente (mismas seis, mismo orden, mismos hechos). |
| `13/10 §8.6` | ✅ hecho | «Compilar limpio no es lo mismo que funcionar» — narra los dos bugs reales (fuente muda, `directory_exists()`), dos procedimientos ejecutables (capturar y mirar la pantalla; matar el proceso y verificar tras relanzar), y ambos ítems ya están en el `## 12 · Checklist` del mismo documento (línea 2168-2171). Coherente con `12/09` Trampas 5 y 6, que enlazan hacia aquí. |
| Parche de `scr_save_load.gml` | ✅ hecho, bien documentado | `save_ensure_dir()` (línea 152-170) ya no confía en `directory_exists()`/`directory_create()`: escribe un fichero centinela real y decide por el resultado de la escritura. Comentario de cabecera explica el porqué con referencia cruzada a `r5-prueba-e2e.md §2`, `12/09` Trampa 6 y `01/14 §11`. |
| Unificación de audio `06/scr_audio.gml` ↔ `13/09` | ✅ hecho, con honestidad sobre lo que no se resolvió | `scr_audio.gml` pasa a ser la única implementación (`global.bus.*`/`global.em.*`); comentario explícito de «✅ UNIFICADO» en la cabecera. `13/09 §4.2` ya no repite el bloque de código, remite al script y explica solo la teoría. Headroom (`AUDIO_HEADROOM_MUSICA -10` etc.) idéntico en ambos sitios. `13/09` incluso deja constancia de un matiz sin resolver (ducking dependiente de fps) en vez de ocultarlo. |
| `_indice/validar-integracion.py` | ✅ hecho, funcional | 810 líneas, 3 capas (nombres duplicados con aridad distinta, `global.X` leído sin escribir, compilación conjunta de pares citados). Ejecutado en esta auditoría: exit 0, «Sin duplicaciones graves», 4 avisos MEDIOS informativos, 0 `global.X` sin escribir. Ya integrado como paso 11 de `actualizar.py`. |

---

## 3 · Fallos de siempre — resultado de la caza

| Comprobación | Resultado |
|---|---|
| Números de documento duplicados (todas las carpetas numeradas) | **Limpio** — comprobado con `ls` + `sort \| uniq -d` en las 10 carpetas numeradas |
| Funciones de GML inventadas | **Limpio** — `validar-codigo-gml.py`: 0 posibles funciones del runtime inventadas. Verifiqué a mano 28 símbolos citados en los documentos de esta ronda (`gamepad_*`, `draw_*`, `surface_*`, `audio_*`, `json_*`, `sha1_string_utf8`, `sprite_create_from_surface`…) contra `buscar.py`: firma real en todos los casos |
| Enlaces o anclas rotas | **Limpio** — `actualizar.py` paso 1: 2081 rutas correctas / 0 rotas, 1423 anclas correctas / 0 rotas |
| Identificadores con tilde/eñe en código | **Limpio** — `validar-codigo-gml.py` pasa; `grep -P` propio por `function \w*[áéíóúñ]` en toda la biblioteca (excluido código de terceros) solo encuentra los dos ejemplos deliberados de «esto NO compila» en `AGENTS.md`/`SKILL.md` |
| Documentos prometidos y ausentes | **Limpio** — cubierto por el 0 de rutas rotas del punto de enlaces; `MAPA.json` sincronizado, 267 entradas, todas existen en disco (paso 3 de `actualizar.py`) |
| Contradicciones entre documentos sobre el mismo comando/función | 🔴 **2 encontradas** |

### Contradicción 1 — cita cruzada al número de trampa equivocado (CORREGIDA en esta auditoría)

`13/11:487` remitía a «`12 · 09`… Trampa 1» para explicar el falso «No licensed options» bajo
sandbox. Trampa 1 de `12/09` es la de las plantillas con *prefabs* que fallan — no tiene nada que
ver con el sandbox de red. La trampa correcta es la Trampa 2 (`resourcetool`/`compile` colgándose
bajo el sandbox), que sí describe exactamente ese síntoma. Corregido: `Trampa 1` → `Trampa 2`.

Contexto de por qué apareció esta cita: el propio commit de cierre de la ronda («Y una acusación
desmentida: un agente sugirió que otro había fabricado una verificación. Lo comprobé: el comando
funciona. El fallo era el sandbox…») documenta que hubo una investigación real sobre si
`resourcetool options set/get/info` funcionaba de verdad. La conclusión —sí funciona, el síntoma
lo causa el sandbox de red— quedó bien documentada en tres sitios (`05/02:543-551`,
`13/11:465-489`, `07/24 §2.2`) con evidencia (`Copied … -> …/mac/icons/1024.png`, `Saved
successfully`), y es coherente entre los tres. Solo el número de trampa citado estaba mal.

### Contradicción 2 — el nombre real de la propiedad del icono/versión de Windows, SIN CORREGIR

`07/24 §2.2` es el documento que ejecutó los comandos reales contra `options info platform=windows`
y usa, en todos sus ejemplos verificados (incluido el bug documentado en §2.4, con salida de
`file` real), la propiedad **`icon`**:

```
gm-cli resourcetool eval "options set platform=windows property=icon value=icono_maestro.png"
```

`13/11:463-467` y `05/02:511-513` afirman, citando *ese mismo* `07 · 24 §2.2` como fuente, que el
nombre real de la propiedad es **`option_windows_icon`** (y, para la versión, `option_windows_version`
frente al `option_version` de Main Options), y `13/11:455` incluso da como ejemplo el comando:

```
gm-cli resourcetool eval "options set  platform=windows property=option_windows_version value=1.0.0.42"
```

`grep -n "option_windows" "07 - Ecosistema/24…md"` no encuentra ni una sola aparición: el
documento que se cita como fuente de esos nombres no los usa nunca — usa `icon`, `icon_png`,
`icon_ldpi`, etc., siempre nombres cortos, y los verifica con salida de comandos reales.

No hay forma de saber desde el texto solo si `option_windows_icon` es el nombre del campo dentro
del `.yy` (la fuente que dice haber leído `13/11`: «los ficheros de esquema del propio
toolchain… `Formats/225/BaseProject/options/`») y `icon` es un alias corto que acepta el CLI —en
cuyo caso ambas partes tendrían razón a su nivel, y solo falta decirlo explícitamente— o si uno de
los dos está mal. Lo que sí es seguro es que un agente que copie literalmente el comando de
`13/11:455` (`property=option_windows_version`) en vez del de `07/24` (`property=icon`) puede
estar usando un nombre que el propio documento que se cita como autoridad nunca demuestra que
funcione. **No corregido**: no es una errata de una línea, requiere volver a `options info
platform=windows` en una sesión con red para decidir cuál de los dos nombres (o si ambos, en
capas distintas) es el correcto, y ese trabajo de verificación queda fuera del alcance de una
auditoría de solo lectura.

---

## 4 · Cinco reutilizaciones de código verificadas contra la firma real en origen

| # | Función reutilizada | Origen (firma real) | Dónde se reutiliza | Resultado |
|---|---|---|---|---|
| 1 | `save_game(_slot, _datos, _meta = undefined)` | `06/scr_save_load.gml:257` | `04/54:200,578` (`save_game(_slot, {...})` y `save_game(CRONO_SLOT_PB + _id, {...})`), `13/05:2127` (`return save_game(_slot, _datos, _meta);`) | ✅ coincide — 2-3 argumentos, mismo orden |
| 2 | `save_game()`/`load_game()`/`delete_save()` (mismo estándar) | `06/scr_save_load.gml` | `04/04:1489-1545` (`rpg_guardar()`/`rpg_cargar()`/`rpg_borrar_partida()` — funciones **propias** del RPG que **envuelven** el estándar en vez de redefinirlo, con aviso explícito «No redefinas save_game/load_game/delete_save») | ✅ — este es el hallazgo más caro de `r5-integracion.md` (04/04 tenía su propio sistema sin argumentos, incompatible), y está genuinamente cerrado: `validar-integracion.py` ya no lo reporta |
| 3 | `sprite_create_from_surface(index, x, y, w, h, removeback, smooth, xorig, yorig)` | Función nativa (verificada con `buscar.py`) | `12/09 §5.2`, peldaño 1(a): `sprite_create_from_surface(_surf, 0, 0, _ancho, _alto, false, false, _cx, _alto - 1)` | ✅ orden de argumentos correcto |
| 4 | `draw_text_color(x, y, string, c1, c2, c3, c4, alpha)` | Función nativa | `04/57:188,196-198` (candado e icono de nivel) y `06/scr_ui_confirmar.gml:162-165` (botones Sí/No) | ✅ 8 argumentos en ambos sitios, orden correcto |
| 5 | `captura_tomar()` (sin argumentos) | `13/11:668` | `07/24:249-253` («Compón con arte que el propio juego ya genera. `captura_tomar()`…») | ✅ se cita sin argumentos, coincide con la firma real |

Las cinco reutilizaciones verificadas son correctas. Es la primera ronda de las auditadas en las
que esta comprobación no encuentra ningún fallo — las rondas anteriores citan que «ha fallado en
todas», y aquí el patrón se rompe, con el matiz de que el fallo #2 de la tabla (RPG) era
precisamente uno de los grandes hallazgos de `r5-integracion.md` y se comprueba aquí que sí se
cerró de verdad, no solo de palabra.

---

## 5 · `python3 _indice/actualizar.py` — salida y código de salida

Ejecutado dos veces: una antes de las dos correcciones triviales de esta auditoría, otra después.
Las dos veces, **código de salida 0**.

```
1. Enlaces internos
2081 rutas correctas · 0 rotas
1423 anclas correctas · 0 rotas

2. Índices y MAPA.json
documentos en español : 254
manual (inglés)       : 3119
manual (español)      : 3142
archivos .gml          : 61824
símbolos explicados    : 2387  (cruce símbolo → documento)
símbolos de la API     : 3486  (de ellos 34 solo en fnames)
runtime leído          : 2026.0.0.23
MAPA.json sincronizado con el disco.

3. Coherencia de MAPA.json y del catálogo de código con el disco
267 entradas, todas existen en el disco.

4. Ortografía española
Sin palabras españolas escritas sin tilde.

5. Cobertura de la API
3213 de 3213 símbolos vigentes son localizables (100 %).

6. Nombres de archivo
Todos los nombres de archivo están bien escritos.

7. Prueba de descubrimiento (¿un LLM encuentra lo que necesita?)
Las 49 tareas se resuelven.

8. Cobertura por familias de símbolos
Todas las familias grandes de símbolos tienen algún documento propio.

9. Código GML (¿inventa alguna función del runtime?)
107 funciones propias de ejemplo (informativo) · 0 posibles funciones del runtime INVENTADAS

10. Compilación real del GML de los documentos
3375 bloques se van a compilar; 305 se saltan:
✓ Los 3375 bloques compilables compilan sin errores de sintaxis. Tiempo total: 17.9s

11. Integración entre documentos
✓ Sin duplicaciones graves. 🟠 4 duplicaciones MEDIAS (informativas). ✓ Todo global.X leído se escribe.

12. Skill para agentes: índice generado y rutas citadas
references/indice-documentos.md regenerado: 267 documentos. Todas las rutas citadas existen.
(Gemini CLI / GitHub Copilot CLI / Cursor CLI / Cline: no instalados en esta máquina, no es regresión)

13. Espejo español del manual
3119 páginas comparadas · 0 ausentes · 0 incompletas · 0 con literales traducidos

Biblioteca coherente. Índices al día y sin deuda pendiente.
EXIT_CODE=0
```

Las 4 duplicaciones MEDIAS del paso 11 (`caidas_instalar_manejador`, `conductor_error`,
`logro_desbloquear`, `tween_to`) son avisos informativos preexistentes, no bloqueantes, y
`tween_to` en concreto es una reutilización **intencionada** (`scr_tween.gml` y `04/15` comparten
la misma firma de 6 argumentos a propósito). No forman parte del encargo de esta ronda y no se
han investigado más a fondo aquí.

---

## 6 · Correcciones aplicadas durante esta auditoría (triviales, una línea cada una)

1. `13/11:487` — cita cruzada `Trampa 1` → `Trampa 2` (contradicción 1 de la §3).
2. `_indice/skills/gamemaker-biblioteca/SKILL.md:128` — `12 - …/09 §7` → `12 - …/09 §5.2` (la
   referencia de gráficos sin artista apuntaba a la sección de errores del compilador). Propagado
   al `AGENTS.md` generado de la skill re-ejecutando `actualizar.py`.

Ninguna otra edición. La contradicción 2 (`icon` vs `option_windows_icon`) y el hueco de la
pregunta 3 (`SKILL.md`/`AGENTS.md` sin gate hacia el checklist de `04/00`) quedan sin tocar: ni son
triviales de una línea, ni es mi papel arreglarlos.

---

## 7 · Valoración honesta

**¿Cumple hoy la skill el objetivo del usuario?** Con matices, y más cerca que en cualquier ronda
anterior — pero no del todo.

**Lo que sí se ha resuelto de verdad, no solo en apariencia:**
- La especificación antes de crear el proyecto ya no es una buena intención: es un paso 0
  imperativo en los tres puntos de entrada reales (`SKILL.md`, `AGENTS.md`, `13/06`), con un
  protocolo completo detrás (`13/28`) que responde con precisión a «qué preguntar» y «qué asumir».
  Un agente que siga el flujo escrito **no** puede llegar a `gm-cli init` sin haber escrito y
  enseñado una especificación al usuario primero.
- El rectángulo de color plano como placeholder — la queja textual del usuario, «basura en SVG o
  lo que sea»— está retirado de la biblioteca y sustituido por una escalera real con código
  verificado, con una regla explícita en negrita prohibiendo el propio rectángulo.
- El código de esta ronda encaja consigo mismo de una forma que ninguna ronda anterior logró:
  `validar-integracion.py` es una herramienta nueva y genuinamente útil, ya integrada en el
  comando único de mantenimiento, y las cinco reutilizaciones de código que verifiqué a mano
  —incluida la más grave, el sistema de guardado del RPG— resisten la comprobación.
- Los dos bugs de plataforma que ningún validador anterior detectaba (fuente muda,
  `directory_exists()` mintiendo) están documentados con causa, síntoma y solución, y la solución
  del segundo está aplicada de verdad en `scr_save_load.gml`, no solo descrita.

**Lo que sigue sin cerrar, y es el hueco que de verdad importa:**
- El defecto central de esta ronda —que un agente no sepa que un «juego completo» necesita menú,
  pausa, opciones y créditos, ni dónde comprobarlo— tiene ya toda la infraestructura resuelta
  (`04/00` como lista maestra, tres checklists remitiendo a ella) pero **no está enganchada al
  sitio que un agente realmente lee** (`SKILL.md`, `AGENTS.md`). Es exactamente el patrón que la
  propia ronda identificó y corrigió para la especificación (paso 0) — y que todavía no aplicó al
  cierre. Un agente puede seguir el flujo completo de `SKILL.md`, especificar bien, evitar el
  rectángulo, compilar limpio, y aun así no saber que existe una lista de 14+15+26 puntos que le
  diría que le falta el menú de pausa.
- Una contradicción real y sin resolver sobre el nombre de una propiedad de `resourcetool`
  (`icon` frente a `option_windows_icon`) entre tres documentos que se citan como fuente unos a
  otros — no es grave por sí sola (ambas partes pueden tener razón en capas distintas), pero es
  exactamente el tipo de discrepancia que ya causó, esta misma ronda, una acusación de
  fabricación entre agentes.

**Para cumplir el objetivo del usuario al 100 %, falta:**
1. Una línea en el paso 6 o 7 del flujo de `SKILL.md`/`AGENTS.md` que diga, con el mismo tono
   imperativo del paso 0: «antes de reportar el juego como terminado, compáralo con el checklist
   de `04/00`». Es el mismo movimiento que ya se hizo para la especificación, aplicado al cierre.
2. Resolver la contradicción `icon`/`option_windows_icon` con una sesión que tenga red y pueda
   ejecutar `options info platform=windows` de verdad, y dejar escrito si son dos nombres en capas
   distintas o si uno de los tres documentos está equivocado.

Ninguno de los dos es un rediseño: el primero es una frase, el segundo es una verificación de
quince minutos con las herramientas que la propia biblioteca ya tiene. Con esos dos cierres, la
skill llegaría al «conocimiento absoluto y actual, al nivel de un experto de la industria» que
pide el usuario sin ninguna reserva pendiente de esta ronda.
