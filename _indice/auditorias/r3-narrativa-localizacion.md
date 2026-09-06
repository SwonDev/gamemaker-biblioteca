# Auditoría r3 · Narrativa, escritura, diálogo, localización y voz

> Fecha 2026-09-06 · 87 temas evaluados · 69 cubiertos · 9 parciales · 9 faltan

## Resumen ejecutivo

El dominio narrativo es, con diferencia, el mejor cubierto de toda la biblioteca: `13 · 12`
(2208 líneas) y `13 · 24` (967 líneas) son tratados casi de nivel de libro de texto —teoría de
Murray/Jenkins/Ashwell/Short con fuentes citadas y verificadas en vivo, modelo de datos completo
en GML, Chatterbox y Scribble con guías dedicadas en español— y la escritura de diálogo, la
estructura narrativa y la producción de voz están todos bien resueltos con símbolos verificados.
El hueco que más duele no es de teoría sino de **documentación de una capacidad que ya existe**:
Scribble trae *shaping* contextual árabe, reordenamiento BiDi y separación de palabras CJK sin
espacios **de fábrica**, verificado en su propio código fuente, y la biblioteca no lo menciona en
ningún sitio — un agente que reciba «localiza esto a árabe» concluirá que GameMaker no puede, y
sí puede. El segundo hueco real es de patrones de diálogo que faltan del todo (menú de temas
repetibles, prioridad/interrupción entre líneas) y de producción de localización que nunca se
escribió (género gramatical, formato de números/fechas, texto en imágenes, coste real y qué
idiomas priorizar, testing narrativo de estados sin salida).

## Tabla tema por tema

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| 1 | Premisa en una frase | ✅ | `13·12` §1.5 | — |
| 2 | Historia, trama y tema (Forster) | ✅ | `13·12` §1.1 | — |
| 3 | Agencia del jugador (Murray) | ✅ | `13·12` §1.3 | — |
| 4 | Disonancia ludonarrativa (Hocking) | ✅ | `13·12` §1.4 | — |
| 5 | Narrativa embebida vs. emergente (Jenkins, 4 formas) | ✅ | `13·12` §1.2 | — |
| 6 | Qué historia necesita cada género | ✅ | `13·12` §1.5 (tabla) | — |
| 7 | Narrativa ambiental (Smith/Worch/Carson) | ✅ | `13·12` §3.1 | — |
| 8 | *Show, don't tell* traducido a mecánica | ✅ | `13·12` §3.4 | — |
| 9 | Ritmo narrativo entre picos de juego (beats en los valles) | ✅ | `13·12` §2.5 | — |
| 10 | Tono y voz de cada personaje (prueba de tapar el nombre) | ✅ | `13·12` §4.1, §7.1 | — |
| 11 | Escribir poco y bien (cortar el 30 %, leer en voz alta) | ✅ | `13·12` §4.3-4.4 | — |
| 12 | Diálogo de sistema/tutorial con voz de personaje | ✅ | `13·12` §3.6 | — |
| 13 | Documentos encontrados (*audiologs*) y sus 3 problemas | ✅ | `13·12` §3.3 | — |
| 14 | Objetos y descripciones (funcional/mundo/voz) | ✅ | `13·12` §3.2 | — |
| 15 | Subtexto | ✅ | `13·12` §4.2 | — |
| 16 | Nombres coherentes y su generación procedural | ✅ | `13·12` §7.4 (`nombre_generar`) | — |
| 17 | *Lore*: solo el que sirve a la mecánica | ✅ | `13·12` §7.3 | — |
| 18 | NPC útiles vs. decorativos | ✅ | `13·12` §7.2 | — |
| 19 | Tres actos y el problema del acto II | ✅ | `13·12` §2.1 | — |
| 20 | Viaje del héroe (como diagnóstico, no plantilla) | ✅ | `13·12` §2.2 | — |
| 21 | Kishōtenketsu (estructura sin conflicto) | ✅ | `13·12` §2.3 | — |
| 22 | Arcos de personaje (deseo/necesidad/herida, antagonista espejo) | ✅ | `13·12` §2.4 | — |
| 23 | Catálogo de Ashwell (*gauntlet*, *branch-and-bottleneck*, *quest*, *open map*, *sorting hat*, *loop-and-grow*, *floating modules*, *time cave*) | ✅ | `13·12` §2.6 | — |
| 24 | Catálogo de Short (QBN, *salience-based*, *waypoint*) | ✅ | `13·12` §2.6 | — |
| 25 | Estructura «collar de perlas» (*string of pearls*) | 🟡 | `13·12` §2.1 (episódico), §2.6 (*gauntlet*) | El nombre y el patrón concreto (tramo lineal + *hub* explorable entre beats) no aparecen con esa etiqueta; hoy hay que deducirlo cruzando dos secciones |
| 26 | Mundo abierto y narrativa emergente | ✅ | `13·12` §1.2, §2.6 (*open map*) | — |
| 27 | Finales múltiples sin multiplicar el trabajo ×10 | ✅ | `13·12` §4.7 (abanico final) | — |
| 28 | Consecuencias diferidas | ✅ | `13·12` §4.8 | — |
| 29 | Banderas y estado del mundo persistente | ✅ | `13·12` §6.2 (`flag_leer`/`flag_poner`/`flag_sumar`/`flag_una_vez`) | — |
| 30 | Gestión de la combinatoria (coste 2ⁿ de ramificar) | ✅ | `13·12` §2.6, §4.7 | — |
| 31 | Modelo de datos: nodos, líneas, opciones, condiciones | ✅ | `13·12` §6.1 (`Linea`, `Opcion`, `Nodo`, `Guion`) | — |
| 32 | Opciones repetibles frente a únicas (menú de temas / *hub* conversacional) | 🔴 | — | No existe el patrón «nodo que se repregunta a sí mismo»: una opción de tema que, tras responderse, vuelve al mismo nodo con las demás opciones intactas y una salida explícita. Hoy toda `Opcion.destino` avanza; no hay ejemplo de un *hub* |
| 33 | Diálogo por temas (*waypoint narrative*, Short) en GML | 🟡 | `13·12` §2.6 (citado en teoría) | La estructura *waypoint* se nombra pero no se traduce a código, a diferencia de QBN/*salience-based* que sí tienen implementación (`BancoBarks`) |
| 34 | *Barks*: reglas por especificidad y antirrepetición | ✅ | `13·12` §3.5, §6.4 (`BancoBarks`) | — |
| 35 | Interrupciones y prioridad entre líneas de diálogo/*barks* | 🔴 | — | `BancoBarks.elegir()` nunca corta una línea en curso; no hay campo de prioridad ni regla de «esto calla lo anterior». Un bark urgente (vida crítica) puede perderse detrás de uno banal con `cooldown` aún activo |
| 36 | Diálogo en combate (*banter*) como sistema propio | 🟡 | `13·12` §6.4 (aplicable vía criterios `en_combate`) | El sistema de *barks* lo soporta en teoría, pero no hay un ejemplo trabajado ni la advertencia de no interrumpir animaciones de ataque con una línea |
| 37 | Personalidad por variación de línea / voces por personaje | ✅ | `13·24` §7, `13·09` §3.2 (*round robin*) | — |
| 38 | Texto con formato: color, velocidad, pausas, temblor | ✅ | `07·18` (Scribble, comandos `[c_]`, `[shake]`, `[wave]`…) | — |
| 39 | Retratos y emociones | ✅ | `04·10` §4.3, `13·24` §5.4 (capa de boca separada) | — |
| 40 | Avanzar y saltar el texto (*typewriter* + *skip*) | ✅ | `04·10` §4.2, `07·18` §3 (`typista.skip()`) | — |
| 41 | Elecciones que importan vs. ilusión de elección | ✅ | `13·12` §4.6 | — |
| 42 | Cuánto texto cabe en una caja (aritmética de lectura) | ✅ | `13·12` §4.5 (Brysbaert 2019, c/s en español) | — |
| 43 | Ramificar cuesta; converger es la solución (patrones de cuello de botella) | ✅ | `13·12` §4.7 | — |
| 44 | Ink de Inkle: integración real en GameMaker y sus límites | ✅ | `13·12` §5.2 (GMInk, `gmink-redux`: solo Windows/Linux, .NET) | — |
| 45 | Yarn Spinner: sin *runtime* oficial de GameMaker | ✅ | `13·12` §5 (tabla) | — |
| 46 | Twine: prototipar el árbol antes de programar | ✅ | `13·12` §5.3 | — |
| 47 | articy:draft: sin integración lista para GameMaker | ✅ | `13·12` §5 (tabla) | — |
| 48 | Chatterbox (JujuAdams): el motor de diálogo Yarn nativo | ✅ | `07·19` (guía completa, API verificada en código) | — |
| 49 | Scribble: texto rico, la pareja de Chatterbox | ✅ | `07·18` | — |
| 50 | Tablas JSON/CSV propias: cuándo bastan | ✅ | `13·12` §5.4 | — |
| 51 | Renderizado de texto rico (comandos, efectos animados) | ✅ | `07·18` §1-2 | — |
| 52 | Saltos de línea automáticos y ancho de caja | ✅ | `13·12` §4.5, `07·18` §4 (`.wrap()`) | — |
| 53 | Fuentes y sus glifos (rangos, `*_CHARSET`) | ✅ | `04·21` §4, `08·20` (19 `*_CHARSET`) | — |
| 54 | Tamaño legible y escala de texto (accesibilidad) | ✅ | `04·27` §2 | — |
| 55 | Velocidad de escritura / máquina de escribir y su coste | ✅ | `04·10` §4.2, `13·12` §6.9 | — |
| 56 | Subtítulos con reglas de accesibilidad (GAG, Steam) | ✅ | `04·27` §2, §2.1 (nombre del hablante, caja personalizable, «antes del primer sonido») | — |
| 57 | Arquitectura desde el día uno: nunca texto en el código | ✅ | `04·21` (regla de oro) | — |
| 58 | Claves frente a texto fuente | ✅ | `04·21` §1-2 (`txt()`) | — |
| 59 | Archivos de idioma (JSON por idioma) | ✅ | `04·21` §1 | — |
| 60 | Plurales (más allá de «+s») | 🟡 | `04·21` §2 (`txt_n`) | Solo cubre singular/plural binario con código funcionando; para ruso (3 formas) o árabe (6) da la indicación de «amplía `txt_n`» pero no las reglas de qué claves ni sus condiciones — no se puede implementar leyendo solo esto |
| 61 | Género gramatical en las traducciones | 🔴 | — | Nada. Un texto como «Estás listo» no tiene forma de resolver «lista» sin construir la clave a mano; no hay patrón de sufijo de género (`_m`/`_f`) equivalente al de plural |
| 62 | Orden de palabras: por qué concatenar frases es un error | 🟡 | `04·21` §2 (uso de `{variables}` ya evita el problema de facto) | El patrón correcto existe pero el antipatrón nunca se nombra ni se ejemplifica: nadie que llegue con el hábito de `"Has encontrado " + item + "."` sabe por qué está mal fuera de España |
| 63 | Formato de números y fechas por región | 🔴 | — | Ningún símbolo `locale_*` existe en el runtime (verificado: `--listar locale` → 0 resultados) y `date_date_string`/`string_format` no aceptan configuración regional; la biblioteca no avisa de que hay que construirlo a mano (separador decimal, orden día/mes/año) |
| 64 | Texto incrustado en imágenes | 🔴 | — | Ningún documento de la biblioteca avisa de que un botón/logo con texto quemado en el sprite necesita una variante por idioma o hay que rehacerlo como texto real sobre gráfico neutro |
| 65 | Expansión del texto (alemán +30 %, chino más corto) | ✅ | `04·21` §5, `04·27` §2 (prueba al 150 %) | — |
| 66 | RTL: árabe y hebreo (BiDi + *shaping* contextual) | 🔴 | Código verificado en `11 - Código descargado/librerias/texto-y-tipografia/Scribble/scripts/{StringArabicParse,StringHebrewParse,GlyphArrayBiDiReorder}.gml` y `__scribble_gen_5_finalize_bidi.gml`; probado en `obj_test_arabic` con `scribble(texto_arabe).draw(x,y)` **sin** llamar a ninguna función manual | **Scribble ya lo resuelve de fábrica y ningún documento lo dice.** `07·18` no menciona BiDi ni árabe/hebreo; `04·21` da a entender que el alfabeto es solo cuestión de glifos de fuente, no de dirección de escritura ni de formas contextuales |
| 67 | CJK: fuentes enormes y su cacheado | ✅ | `04·21` §4 (`font_cache_glyph`, Noto Sans CJK) | — |
| 68 | Saltos de línea sin espacios (CJK) | 🔴 | Código verificado: `__scribble_gen_4_build_words.gml` trata cada carácter CJK como palabra aislada (`ISOLATED_CJK`) rompible de forma independiente | Scribble ya resuelve el ajuste de línea en chino/japonés sin espacios; no está documentado en `07·18` ni en `04·21`, que solo hablan de fuentes CJK, no de cómo se parte la línea |
| 69 | Entrada de texto por IME | 🟡 | `01 · 12` §8bis (`keyboard_virtual_show` en móvil) | El teclado virtual de móvil delega en el IME del sistema operativo (cubierto), pero no hay ninguna mención de si `keyboard_string` compone IME en escritorio (japonés/chino con teclado físico); nicho, pero sin verificar |
| 70 | Elegir idioma y detección automática | ✅ | `04·21` §3 (`os_get_language`), `04·25` (dropdown de idioma) | — |
| 71 | Traducción por IA con revisión humana | ✅ | `04·21` §5 (`traducir_idioma.py`, memoria de traducción) | — |
| 72 | Coste real de localizar y qué idiomas priorizar por retorno | 🔴 | — | Ningún documento habla de presupuesto de localización ni de criterio de priorización de idiomas (EFIGS+ZH-CN+JA+KO+PT-BR+RU es el orden habitual del sector, pero no está ni mencionado ni hay una fuente primaria citada en esta sesión) |
| 73 | Catálogo de librerías de localización de terceros | 🟡 | `12·05` §8 (lexicon, polyglot, Localize, gm-i18n, GMLocalize2, `small_pp_localization_tool`, Cultured, Unic, AsciiTransliterate — todas verificadas en `11 - Código descargado/librerias/localizacion/`) | Existe pero **`04·21` no lo enlaza**: quien llega a la receta de localización nunca sabe que `small_pp_localization_tool` exporta a hoja de cálculo para traductores, ni que `Unic` resuelve `string_upper("ñ")` — justo el fallo de mayúsculas que ya está documentado como problema conocido de esta biblioteca en español |
| 74 | Grabar o no (texto siempre, voz cuando compensa) | ✅ | `13·24` §1.2 | — |
| 75 | Dirección de actores y guion de grabación | ✅ | `13·24` §2.1, §2.4 | — |
| 76 | Formato, compresión e importación (mono, *streaming*) | ✅ | `13·24` §2.6 | — |
| 77 | Sincronía con el subtítulo (manda el audio) | ✅ | `13·12` §6.9, `04·10` §4.6 | — |
| 78 | Sincronía labial simple (*lip-sync*) | ✅ | `13·24` §5 (boca binaria + visemas Rhubarb) | — |
| 79 | Latencia de carga (*audio groups* asíncronos) | ✅ | `13·24` §3.3 (evento Async - Save/Load) | — |
| 80 | Tamaño en disco (por idioma, por SKU) | ✅ | `13·24` §3.4 (Configuraciones por SKU regional) | — |
| 81 | Voz por IA: estado legal y ético | ✅ | `13·24` §3.5 (marcado explícitamente fuera de alcance, con honestidad) | — |
| 82 | Localizar la voz (convención de nombres, *fallback*) | ✅ | `13·24` §2.2, §3.1-3.2 (`voz_<clave>_<idioma>`) | — |
| 83 | Biblia del juego | ✅ | `13·12` §8.1 | — |
| 84 | Hoja de cálculo de líneas con id y estado | 🟡 | `13·24` §2.3 (`generar_hoja_grabacion.py`, generada, con clave+texto) | Falta la columna **estado** (borrador/traducido/revisado/grabado/obsoleto) que pide el encargo; y no se enlaza con `small_pp_localization_tool` (#73), que ya exporta exactamente esa hoja para traductores |
| 85 | Control de versiones del texto | ✅ | `13·12` §5.4 («el diff de git es legible»), `13·11` §4.1 (git con GameMaker) | — |
| 86 | Revisión y corrección (relectura, consistencia de *lore*) | 🟡 | `13·12` §4.4 (leer en voz alta, individual por línea) | No hay un paso de producción para una relectura completa que cace contradicciones de continuidad (edad, cronología, nombres) a través de todo el guion, distinto de la revisión línea a línea |
| 87 | Testing narrativo: ¿se puede llegar a un estado sin salida? | 🔴 | — | `13·10` (Testing y QA) no tiene ninguna sección narrativa; no existe un validador que recorra `nodos.json` comprobando que todo `destino` resuelve a un nodo real, que ningún nodo queda huérfano, o que una misión `ACTIVA` tiene siempre un camino a `COMPLETADA` o `FALLADA` |

## Huecos por prioridad

### 🔴 Graves

1. **RTL (árabe/hebreo) y CJK sin espacios ya resueltos por Scribble, sin documentar** (#66, #68).
   Es el hueco que más duele: la biblioteca da a entender —por omisión— que GameMaker no puede
   con árabe/hebreo, cuando la librería estándar que la propia biblioteca recomienda ya lo hace
   con cero código adicional.
2. **Menú de temas / *hub* conversacional con opciones repetibles** (#32). Patrón de diálogo
   común (RPG, VN) sin ejemplo ni mención.
3. **Interrupción y prioridad entre líneas de diálogo/*barks*** (#35). El sistema existente no
   puede garantizar que una línea urgente no se pierda detrás de una banal.
4. **Género gramatical en localización** (#61). Sin patrón, cada traductor lo resuelve distinto y
   rompe la consistencia de las claves.
5. **Formato de números y fechas por región** (#63). GameMaker no ofrece nada nativo y no se avisa.
6. **Texto incrustado en imágenes** (#64). Riesgo de producción silencioso: assets gráficos que
   nadie recuerda traducir.
7. **Coste real de localizar y prioridad de idiomas** (#72). Falta toda guía de producción/negocio.
8. **Testing narrativo de estados sin salida** (#87). Ningún validador de grafo de diálogo/misión.

### 🟠 Medios

- Diálogo por temas (*waypoint*) sin traducir a código (#33).
- Diálogo en combate (*banter*) sin ejemplo dedicado (#36).
- Hoja de líneas sin columna de estado, y sin enlazar con `small_pp_localization_tool` (#84).
- Catálogo de librerías de localización de terceros sin enlazar desde la receta principal (#73).
- Revisión y corrección de continuidad narrativa como paso de producción (#86).

### 🟡 Menores

- Nombre «collar de perlas» no usado, aunque el patrón exista repartido en dos secciones (#25).
- Antipatrón de concatenar frases nunca nombrado explícitamente (#62).
- Entrada IME en escritorio sin verificar (#69).
- Plurales complejos (ruso/árabe) solo avisados, sin tabla de reglas (#60).

## Encargo para el redactor

1. **Documentar BiDi/RTL y CJK de Scribble** — archivo `07 - Ecosistema/18 - Scribble - texto
   rico (guía en español).md`, nueva sección «6 · Escritura de derecha a izquierda y CJK».
   Contenido: `scribble(texto_arabe).draw(x,y)` ya aplica *shaping* contextual árabe y
   reordenamiento BiDi automáticamente (mostrar el ejemplo real de `obj_test_arabic`: fuente con
   `scribble_font_set_default("fnt_noto_arabic")` y una fuente Noto Arabic con el rango Unicode
   0x0600-0x06FF); mencionar que existen además `StringArabicParse()` y `StringHebrewParse()`
   como utilidades sueltas para cuando se usa `draw_text` nativo en vez de Scribble (verificado
   en `StringArabicParse.gml`/`StringHebrewParse.gml`); y que el ajuste de línea en CJK ya trata
   cada carácter como palabra rompible sin necesitar espacios (verificado en
   `__scribble_gen_4_build_words.gml`, constante `ISOLATED_CJK`). Símbolos de la librería
   (no del runtime, verificar firma en el propio código si se cita literal):
   `scribble_font_set_default`, `StringArabicParse`, `StringHebrewParse`, `GlyphArrayBiDiReorder`.
   Enlazar esta sección nueva desde `04 - Recetas por género/21 - Localización e idiomas (con
   traducción por IA).md` §4, sustituyendo la impresión actual de que RTL/CJK es «solo fuentes».

2. **Nodo *hub* con opciones repetibles** — archivo `13 - Diseño y producción de videojuegos/12
   - Diseño narrativo y diálogos.md`, nueva subsección «6.1 bis · El nodo *hub*: temas que no
   cierran la conversación». Contenido: un `Opcion` cuyo `destino` es el mismo `Nodo` que la
   contiene; cada tema usa `flag_una_vez` para no repetir la primera reacción especial (pero la
   opción sigue disponible); una opción de salida explícita (`destino: ""`). Reutiliza los
   constructores ya existentes (`Nodo`, `Opcion`, `flag_una_vez`) — cero símbolos nuevos del
   runtime.

3. **Prioridad e interrupción de *barks*** — mismo archivo, ampliar `BancoBarks` en §6.4: añadir
   un campo `prioridad` a cada regla y, en `elegir()`, permitir que una regla de prioridad mayor
   interrumpa (`audio_stop_sound` sobre `global.voz_actual`, verificado en `13·24`) el bark que
   esté sonando. Tabla de niveles sugerida: ambiente < reacción < urgente (vida crítica) < línea
   de misión.

4. **Ejemplo de diálogo en combate** — mismo archivo, añadir a §6.4 un ejemplo con criterios
   `{ en_combate: true, objetivo: "jefe" }` y una nota de no disparar un bark durante los frames
   de *hitstop*/ventana de ataque (enlazar con `04 · 18 — Diseño de combate y de jefes` si ese
   documento ya define esas ventanas; comprobar antes de citar sección exacta).

5. **Género gramatical** — archivo `04 - Recetas por género/21 - Localización e idiomas (con
   traducción por IA).md`, nueva subsección «2 bis · Género gramatical», paralela a los plurales:
   `txt_g(_base, _genero)` que añade el sufijo `_m`/`_f`/`_n` a la clave, con la misma idea de
   `txt_n`. Cero símbolos nuevos del runtime (usa `struct_exists`, ya verificado en el propio
   documento).

6. **Antipatrón de concatenar frases** — mismo archivo, añadir justo tras el aviso de plurales un
   bloque ❌/✅ explícito: `"Has encontrado " + item.nombre + "."` (roto en alemán/japonés por
   orden de palabras) frente a `txt("obtuviste_objeto", { objeto: item.nombre })`.

7. **Formato de números y fechas** — mismo archivo, nueva subsección «2 ter · Números y fechas
   por región»: advertir que no existe ningún símbolo `locale_*` en el runtime (verificado,
   `--listar locale` → 0), que `string_format` siempre usa punto decimal y que `date_date_string`
   no acepta orden regional; proponer una tabla `{ idioma: { separador_miles, separador_decimal,
   orden_fecha } }` como estructura de datos propia. Símbolos verificados a citar:
   `string_format`, `date_date_string`, `date_get_day`, `date_get_month`, `date_get_year`.

8. **Texto en imágenes** — archivo `12 - Utilidades e integraciones/05 - Pipeline de arte, audio
   y niveles.md` §8 (Localización), añadir un aviso: cualquier sprite con texto quemado necesita
   una variante `spr_boton_jugar_<idioma>` o debe rehacerse como texto real sobre gráfico neutro;
   patrón de resolución con `asset_get_index("spr_" + nombre + "_" + global.idioma)` (mismo
   patrón ya verificado en `13·24` §3.2 para voz).

9. **Coste y prioridad de idiomas** — mismo archivo que #5-7 (`04·21`), sección breve al final,
   marcada explícitamente con ⚠️ por ser criterio de negocio sin fuente primaria verificada en
   esta sesión: mencionar que el orden habitual del sector para un juego indie es
   inglés → EFIGS → chino simplificado → japonés/coreano → portugués de Brasil → ruso, y que la
   decisión real debe apoyarse en los datos de wishlist por región de la propia página de Steam
   del juego, no en esta tabla.

10. **Enlazar el catálogo de terceros** — mismo archivo (`04·21`), añadir a «Ver también»:
    `12 · 05 §8 — Localización (catálogo de librerías)`, destacando `Unic` (mayúsculas/orden
    correcto con ñ — cierra un problema ya conocido del propio proyecto en español) y
    `small_pp_localization_tool` (exportación a hoja de cálculo para traductores, cierra el hueco
    #84 sin reimplementarlo).

11. **Columna de estado en la hoja de líneas** — archivo `13 - Diseño y producción de
    videojuegos/24 - Voz, diálogo y localización de audio.md` §2.3, ampliar
    `generar_hoja_grabacion.py` con una columna `estado` (`borrador` / `traducido` /
    `revisado` / `grabado`) y mencionar `small_pp_localization_tool` como alternativa ya hecha
    para quien no quiera mantener el script propio.

12. **Validador del grafo narrativo** — archivo `13 - Diseño y producción de videojuegos/12 -
    Diseño narrativo y diálogos.md`, nueva subsección «6.10 · Validar el grafo antes de jugarlo»:
    un script (Python, mismo espíritu que `generar_hoja_grabacion.py`) que recorre
    `datafiles/narrativa/nodos.json` y comprueba (a) que todo `destino` de toda `Opcion` resuelve
    a un `id` de nodo existente, (b) que ningún nodo queda sin ninguna referencia entrante (ni
    disparador ni opción) y por tanto es inalcanzable, (c) opcionalmente, para el gestor de
    misiones (`13·12` §6.5), que toda misión `activar()`-ble tiene al menos un camino de código
    hacia `completar()` o `fallar()`. No requiere símbolos nuevos del runtime: es análisis del
    JSON con `json_parse`/`struct_get_names` del lado Python, no GML.

## Lo que comprobé y NO hacía falta

- **Chatterbox y su localización de guiones**: ya resuelto con `ChatterboxLocalizationBuild` /
  `ExportData` / `ImportData`, citado y con el aviso literal del propio código sobre que
  reescribe archivos fuente (`13·12` §5.1). No hace falta nada más.
- **ink en GameMaker**: parecía sospechoso que «no hubiera soporte», pero sí lo hay (GMInk,
  `gmink-redux`) y la biblioteca ya documenta sus límites reales de plataforma (.NET, solo
  Windows/Linux) con honestidad. Cubierto.
- **Sincronía de voz con el *typewriter***: pensé que faltaba la regla de qué manda (¿el audio o
  el texto?); ya está resuelta y con la decisión correcta tomada («manda el audio») en `04·10`
  §4.6 y `13·12` §6.9.
- **Lip-sync**: pensé que sería un hueco por ser una limitación conocida de GameMaker (no hay
  `audio_sound_get_amplitude`); en realidad `13·24` §5 ya lo documenta con las dos alternativas
  reales (boca binaria y visemas precalculados con Rhubarb Lip Sync) y la ausencia está señalada
  con ⚠️ explícito, exactamente como pide el método.
- **Biblia del mundo**: no aparecía al buscar «biblia del juego» literal porque el documento la
  llama «Biblia del mundo» (`13·12` §8.1); está cubierta, solo cambia el nombre.
- **Doblaje parcial y *fallback* a subtítulos**: `voz_localizada_obtener()` devolviendo `-1` sin
  romper el subtítulo ya está resuelto y probado en la checklist de QA de voz (`13·24` §8).
- **Tamaño de build por idioma**: pensé que sería un hueco de producción; `13·24` §3.4 ya explica
  la diferencia entre RAM (audio groups) y peso del paquete (Configuraciones por SKU), citando el
  manual oficial.
