# R7 · Prueba de la skill `gamemaker-biblioteca` — juego para móvil con controles táctiles

**Fecha:** 8 de septiembre de 2026. **Agente:** Claude (Opus 5, 1M contexto), sesión aislada, `~/gm_prueba_movil`
(creado y borrado en esta misma sesión, nunca dentro de la biblioteca). **Encargo:** «hazme un juego para
móvil, con controles táctiles» — perfil no probado antes (los tres anteriores fueron arcade, aventura
narrativa y puzzle con datos externos).

**Veredicto corto:** la skill guía correctamente lo específico de móvil — resolución, densidad, zona
segura, orientación, ciclo de vida, tamaño de botón táctil, joystick virtual — con código citable y
verificado en `buscar.py` en cada paso. El juego resultante es **genuinamente móvil**, no un juego de
escritorio con la resolución cambiada: controles exclusivamente táctiles de dos pulgares, sin una sola
línea de teclado. Pero **la skill no evita que el agente meta la pata al ensamblar sus propias piezas**:
compilé limpio dos veces con bugs visuales reales delante (un botón "desactivado" indistinguible del
activo, un menú que se salía de la pantalla) que solo aparecieron al *mirar* el juego corriendo — exactamente
la advertencia que la propia biblioteca hace y que un agente que solo compile sin ejecutar se saltaría. Y
encontré un fallo no documentado, serio para un proyecto en español: **la fuente por defecto de GameMaker
no tiene glifos de á/é/í/ó/ú/ñ/¿/¡** — se comen en silencio, sin caja de "glifo no encontrado", sin aviso
de ningún tipo.

---

## 1 · Qué se construyó

Proyecto `JuegoMovil` (plantilla *Space Rocks*, `gm-cli init`), sin usar ni un solo sprite de la plantilla:
todo se dibuja por código (`draw_circle_color`, `draw_triangle`, `draw_roundrect_color`) — decisión
deliberada para no depender de un pipeline de arte en esta prueba, documentada en el propio código.

- **5 salas**: `rm_menu`, `rm_opciones`, `rm_creditos`, `rm_juego`, `rm_fin` (960×540, 16:9).
- **8 objetos**: `obj_sistema` (persistente: ciclo de vida, pantalla, config), `obj_menu`, `obj_opciones`,
  `obj_creditos`, `obj_juego` (jugador + gestor de partida + HUD + pausa), `obj_enemigo`, `obj_bala`,
  `obj_fin`.
- **3 scripts**: `scr_pantalla` (escalado, márgenes seguros, mm→GUI), `scr_config` (INI de opciones, JSON
  de partida en buffer, vibración), `scr_ui` (botones y paneles táctiles reutilizables).
- **1 Included File**: `fuente_ui.ttf`, cargada en runtime con `font_add()` — ver §5.
- **Bucle jugable**: nave controlada por joystick virtual (pulgar izquierdo), disparo con botón (pulgar
  derecho, apunta al enemigo más cercano), oleadas con rampa de dificultad, 3 vidas, victoria a 150 puntos.
- **Menú, opciones (volumen música/SFX por slider táctil, vibración, borrar progreso con confirmación),
  pausa que congela el mundo de verdad, guardado de partida en curso + mejor puntuación persistente,
  créditos.** Checklist maestro de `04 · 00` comparado punto por punto en §8.

**Recortes explícitos** (regla del checklist maestro: lo que se recorta se dice, no se omite):
- **Sin teclado ni mando** — el encargo pide controles táctiles «de verdad», no disfrazados; el ítem
  «funciona con teclado y mando» del checklist de `04 · 00` no aplica aquí a propósito.
- **Sin audio** — no se generaron assets de sonido; los sliders de volumen y el enganche de vibración
  existen y persisten, pero no hay ningún `.wav`/`.ogg` que controlar. Fuera de alcance de esta prueba
  (centrada en táctil, no en pipeline de audio).
- **Sin idioma/accesibilidad avanzada** en Opciones — solo volumen y vibración.
- **Vibración real sin activar** — el punto de enganche existe (`feedback_vibrar()` en `scr_config.gml`)
  pero la llamada real a `GMEXT-MobileUtils` está comentada: esa extensión **no se puede crear con
  `resourcetool`** (solo el IDE la instala), y es la única excepción documentada por la propia biblioteca
  a "todo se puede por CLI".

---

## 2 · Evidencia punto por punto

### 2.1 · ¿Guió la skill lo específico de móvil?

**Sí, y con detalle citable en cada punto.** Todo salió de
`04 - Recetas por género/28 - Juegos para móvil (táctil).md`, la receta a la que apunta el propio router
de la skill (`references/mapa-disciplinas.md:144-147`, tabla `## Móvil`):

| Pregunta del encargo | Dónde lo dice la skill | Qué hice con ello |
|---|---|---|
| Resolución y escalado | `04·28 §4.1` — altura fija, anchura según la relación de aspecto real (`display_get_width/height` → `surface_resize` + `camera_set_view_size` + `display_set_gui_size`, "los tres juntos") | `scr_pantalla.gml::ajustar_pantalla()`, código calcado |
| Densidad de pantalla | `04·28 §4.3` — `display_get_dpi_x()` con el aviso de que puede mentir (*bucket* nominal de Android) y "aplica siempre un mínimo absoluto" | `scr_pantalla.gml::milimetros_a_gui()` + `tamano_objetivo_tactil()` con suelo de 48 px |
| Tamaño mínimo de botón táctil | `04·28 §5.1` — 48 dp / 44 pt / 9 mm, tabla con las dos guías oficiales citadas | `tamano_objetivo_tactil()` aplicado a joystick, botón de disparo, botón de pausa y los 5 botones de cada menú |
| Zona segura | `04·28 §4.2` — **"GameMaker no tiene ninguna función de *safe area*", se resuelve con márgenes por porcentaje, es criterio de la biblioteca, no oficial** | `margenes_seguros()`, con la misma advertencia copiada en el comentario del código |
| Orientación | `04·28 §2` — `os_set_orientation_lock()`/`os_lock_orientation()`, con el aviso de que `display_set_orientation` **no existe** y que `os_set_orientation_lock()` apaga las variantes *flipped* | Bloqueo a apaisado en `obj_sistema::Create`, citado; decidí **una sola orientación** por `04·28 §1.2` ("elige una y quédate ahí") |
| Qué pasa al perder el foco / llamada entrante | `04·28 §3` y `§3 bis` — `os_is_paused()` se comporta distinto en móvil (se queda `true`) y en escritorio (pulsa `true` un paso); guardar y parar audio en el flanco de subida, **no** quitar la pausa sola | `obj_sistema::Step`, con la combinación adicional de `window_has_focus()` citada de `01·12 §8` — ver nota abajo |

Las once trampas se leyeron antes del primer comando (§0 de `12·09`), como pide la propia skill. Cuatro
se usaron de verdad en esta sesión; ninguna resultó falsa. Sí aparecieron hallazgos nuevos, fuera de esas
once — ver §2.5.

### 2.2 · ¿Supe implementar el táctil correctamente, o improvisé?

**Implementado, no improvisado — pero con un límite de verificación real, ver §2.4.** El joystick virtual
de `obj_juego` es una copia deliberada, con los nombres de esta biblioteca, del patrón de `04·28 §5.3`
("nace donde tocas", zona muerta reescalada, la base "camina" si el dedo se sale del radio). El botón de
disparo y el de pausa usan el mismo patrón de `04·28 §5.2`: recorrer los 5 posibles dedos
(`device_mouse_check_button(_i, mb_left)`), nunca asumir el índice `0`, y `device_mouse_x_to_gui`/
`device_mouse_y_to_gui` en vez de coordenadas de mundo — la trampa "número uno" que la propia receta señala
(`04·28`, tabla de trampas, penúltima fila).

No usé el sistema de **gestos** de GameMaker (`Gesture - Tap/Drag/Pinch`, `01·12 §6` y `04·28` intro):
para un joystick + botón de disparo, la vía de `device_mouse_*` es la que la propia receta desarrolla en
detalle (§5.3); los gestos habrían encajado mejor para un *pinch-to-zoom* que este juego no necesita.

### 2.3 · ¿Avisó de que ratón y táctil no son lo mismo, con las funciones específicas?

**Sí, en dos sitios que se refuerzan.** `01·12 §3` ("En dispositivos táctiles: el botón izquierdo equivale
a un toque… para multi-touch necesitas `device_mouse_*`, no las del ratón") y `01·12 §5`
("Device Input (multi-touch)… para multi-touch en móvil, las funciones del ratón no bastan"). Apliqué la
regla literalmente: **cero usos de `mouse_x`/`mouse_y`/`mouse_check_button`** en las 27 `.gml` del
proyecto — todo pasa por `device_mouse_*`, confirmado por el propio validador (`validar-proyecto.py`, sin
avisos).

### 2.4 · ¿Pude comprobar algo sin un dispositivo? ¿Me dijo la biblioteca cómo?

**Sí para un dedo, no para dos — y esto último la biblioteca no lo dice.**

`01·12 §8 bis` es explícito: *"Los gestos también funcionan con ratón en escritorio, así que puedes
desarrollar y probar en el PC. Pero prueba en un móvil real antes de publicar."* Apliqué exactamente eso:
lancé el juego compilado con `gm-cli run --target mac`, usé `cliclick` (CLI de automatización de macOS) para
simular el ratón como el dedo `0`, y verifiqué en vivo, con capturas de pantalla reales:

- El menú entero, con sus 5 botones y la navegación por toque.
- El bucle de juego: la nave se movía según el arrastre, el joystick aparecía "donde tocas" y desaparecía
  al soltar, el botón de disparo creaba balas, los enemigos perseguían y colisionaban, la derrota disparaba
  el guardado del progreso y la transición a `rm_fin`, "Reintentar" volvía a jugar.
- La pantalla de Opciones: los dos *sliders* respondían al arrastre, el interruptor de vibración cambiaba
  de estado, "Borrar progreso" abría la confirmación y "No" la cerraba sin borrar nada.

**Lo que NO pude comprobar, y es un hallazgo propio de esta prueba, no algo que la biblioteca advierta**:
un ratón de escritorio es **un solo puntero**. Intenté mantener el joystick pulsado (dedo conceptual 0) y
tocar el botón de disparo a la vez (un segundo `cliclick dd:` en otra coordenada) para simular las dos
manos reales del jugador: el segundo "toque" **no fue un segundo dedo**, fue el mismo cursor del sistema
moviéndose — la base del joystick "caminó" literalmente hasta el botón de disparo en la captura de pantalla
(evidencia visual guardada en la sesión). **El control de dos pulgares que la propia receta recomienda para
"arcade" (`04·28 §1.1`) no se puede ejercitar de verdad con ratón, ni con `cliclick`, ni con AppleScript
— ninguna herramienta de este Mac simula multitáctil real.** `01·12 §8 bis` dice que los gestos "también
funcionan con ratón", que es cierto para un dedo; no dice, en ningún sitio de la biblioteca, que el
multitáctil simultáneo **no se puede probar en absoluto** desde un escritorio sin hardware táctil. Es la
brecha de verificación más seria de esta prueba: un agente puede escribir el código de multitáctil
correcto (verificado contra el manual) y aun así **no tiene ninguna forma de confirmar que funciona como
se espera** hasta que lo prueba alguien con un dispositivo real — que es justo lo que `04·28 §9.1` ya pide
("prueba en un teléfono de verdad"), pero sin decir que ni siquiera el paso intermedio del escritorio sirve
para esto.

### 2.5 · ¿Sirvieron las once trampas, o tropecé con alguna nueva?

**Las once, útiles; cuatro las usé de verdad; y sí, encontré varias que no están en la lista de once.**

Usadas en esta sesión:
- **Trampa 2** (sandbox cuelga `resourcetool`/`compile`): ejecuté todo con `dangerouslyDisableSandbox: true`
  desde el primer comando, tal y como pide el encargo — sin eso, cada llamada se habría colgado.
- **Trampa 5** (fuentes horneadas por `resourcetool` salen con glifos vacíos): la esquivé a propósito
  **no creando ninguna fuente por `resourcetool`** — decidí depender de la fuente por defecto
  (`draw_set_font(-1)`), que es justo la recomendación segura que da `08·03`. Fue precisamente esa decisión
  "segura" la que destapó el hallazgo nuevo del punto 1 de abajo.
- **Trampa 8** (`includedfile` deja `filePath` vacío y no copia el archivo): la reproduje al pie de la letra
  al empaquetar la fuente `.ttf` — `filePath` salió vacío tras `RESOURCE CREATE`, lo corregí con
  `resource set expr=project.IncludedFiles[0].filePath value=datafiles` exactamente como documenta la
  trampa, y confirmé con una compilación **sin** `--errors-only` que el `WARNING` de "datafile … was NOT
  copied" desaparecía y el `.ttf` entraba en el `.zip` (`unzip -l … | grep ttf` → `assets/fuente_ui.ttf`).
- **Trampa 11** (`ResourceTool` revienta sin motivo, ~2 de cada 5 veces): la viví en vivo — varias llamadas
  de `resourcetool eval`/`script` dispararon el diálogo nativo de macOS "ResourceTool se ha cerrado
  inesperadamente" (capturado en pantalla), sin que ninguna operación real fallara (`ResourceTool
  Successful` en la salida). Coincide con lo que documenta la trampa: son crashes del propio binario, no
  del proyecto.

**Hallazgos nuevos, no cubiertos por las once ni por el resto de la biblioteca que consulté:**

1. **La fuente por defecto de GameMaker (`draw_set_font(-1)`) no tiene glifos de á/é/í/ó/ú/ñ/¿/¡.** No
   dibuja una caja de "glifo no encontrado": **omite el carácter en silencio**. "Créditos" se dibujaba
   "Crditos"; "Mejor puntuación" se dibujaba "Mejor puntuacin". Comprobado que **no** es un problema de
   codificación de origen: los bytes UTF-8 de "é" (`c3 a9`) están intactos y correctos tanto en el `.gml`
   fuente como en el `game.ios` ya compilado (`xxd`/hexdump de ambos, idénticos) — el fallo es
   exclusivamente de renderizado, en el juego de glifos que trae la fuente integrada del motor. Esto
   **contradice de facto** la recomendación implícita de `08·03` de usar `draw_set_font(-1)` como opción
   "segura" frente al horneado roto de `resourcetool` (trampa 5): es segura para compilar, no para mostrar
   texto en español. La solución que SÍ funciona por CLI, y que tampoco está conectada en ningún sitio de
   la biblioteca con este problema concreto: `font_add()` (`08·03`, "Gestión de fuentes") cargando un
   `.ttf` real como *Included File*, combinando la propia receta de la trampa 8 con `font_add()`. Verificado
   de punta a punta: compila sin warnings, el `.ttf` entra en el paquete, y el texto en pantalla pasó de
   "Crditos"/"puntuacin" a "Créditos"/"puntuación" — capturas de pantalla de antes y después guardadas en
   la sesión. Para publicar de verdad hace falta una fuente con licencia redistribuible (aquí usé
   `SFNSMono.ttf` del propio sistema, válido solo para esta verificación local, nunca para distribuir).

2. **El suelo de 48 px/9 mm para el objetivo táctil (`04·28 §5.1`) puede no caber si apilas varios
   controles en una pantalla de móvil en apaisado — y la receta no avisa de esta tensión.** Con 5 botones
   del menú a una altura "generosa" (`tamano_objetivo_tactil() * 2`, bien por encima del suelo exigido), el
   bloque entero medía más que los 540 px de alto de diseño: el título se solapaba con "Jugar" y el botón
   de más abajo se salía de la pantalla. Lo mismo, con la misma causa, en la pantalla de Opciones (5
   controles: 2 *sliders* + interruptor + borrar + volver) — "Borrar progreso" quedaba invisible por debajo
   del borde inferior y "Volver" se solapaba con el interruptor de vibración. **Los dos bugs compilaron
   limpio, sin ningún aviso de `validar-proyecto.py` ni de `gm-cli compile`** — solo se ven ejecutando el
   juego y mirando la pantalla, exactamente el punto que la propia biblioteca insiste en repetir
   ("compilar limpio no es funcionar", `13·10 §8.6`). Los corregí encadenando los controles en flujo
   vertical relativo en vez de anclar el último al fondo de la pantalla de forma independiente.

3. **Atenuar un botón "inactivo" bajando el alfa y aclarando el color a la vez puede cancelarse casi por
   completo sobre fondo negro — invisible al ojo hasta que lo compruebas.** Mi primera versión de
   `ui_boton_dibujar()` usaba `c_gray` (más claro) a 0,45 de alfa para "Continuar" desactivado, frente a
   `c_dkgray` (más oscuro) a 0,88 para los botones activos: sobre negro, `128×0,45 ≈ 58` y `64×0,88 ≈ 56` —
   **prácticamente el mismo brillo final**. El botón "Continuar" (correctamente desactivado, sin partida
   guardada) se veía **idéntico** a los activos en la captura de pantalla, aunque el código de toque ya lo
   ignoraba correctamente (no era un bug funcional, era un bug de **affordance**). En una interfaz táctil
   esto es más grave que en una de ratón, porque no hay *hover* que lo delate de otra forma — el propio
   `04·28 §5.6` lo dice en abstracto ("nada de *hover* ni resaltado previo") sin cubrir este caso concreto
   de contraste. Lo corregí manteniendo el mismo color de caja y solo variando el alfa de forma más
   agresiva, y atenuando también el texto.

Ninguno de estos tres es un fallo de la información de la biblioteca — las fórmulas y el suelo de 48 px que
di son correctos y verificados. Son fallos de **cómo un agente compone esas piezas correctas**, que ni
`validar-proyecto.py` ni `gm-cli compile` pueden cazar porque no miran un solo píxel de la pantalla.

---

## 3 · Compilación real

Última compilación, **sin** `--errors-only` (la única que muestra el `WARNING` de un *included file* sin
copiar, per Trampa 8), desde `~/gm_prueba_movil/JuegoMovil`:

```
$ python3 "_indice/validar-proyecto.py" "$(pwd)" --todo
27 archivos .gml · 397 llamadas analizadas · runtime del índice 2026.0.0.23

✓ Ninguna llamada a una función del runtime que no exista.

✓ Ninguna llamada a una función del runtime con un número de argumentos que no cuadre con su firma.

$ gm-cli compile --toolchain GMS2@2026.0.0.23
[…]
│  Compile Constants... finished.
│  Compile Scripts... finished.
│  Compile Rooms... finished..... 0 CC empty
│  Compile Objects... finished.... 0 empty events
│  Compile Timelines...finished.
│  Compile Triggers...finished.
│  Compile UI Layers... finished.
│  Global scripts...finished.
│  -------------------------------------------------------
│  NOTE: 5 Unused Assets found (and will be removed) -
│  GMAudioGroup :: audiogroup_default
│  GMSprite :: spr_bullet, spr_player, spr_rock_big, spr_rock_small
│  -------------------------------------------------------
│  Final Compile finished.
│  Saving IFF file... […]/output/game.zip
│  Stats : GMA : sp=4,au=0,bk=0,pt=0,sc=25,sh=0,fo=0,tl=0,ob=8,ro=5,da=1,ex=0,ma=6,…
│  Igor complete.
◆  Compilation finished
```

**Sin ninguna línea `WARNING`** (la única coincidencia de `grep -i "warning\|error\|fail"` sobre la salida
completa fue el "Failed to load Options from local_settings.json" benigno que aparece en cualquier proyecto
sin config local, no un fallo real). `da=1` confirma el *included file* (la fuente) empaquetado; los 5
"Unused Assets" son los sprites de la plantilla *Space Rocks* que nunca usé, a propósito (todo se dibuja por
código).

`gm-cli run --toolchain GMS2@2026.0.0.23 --target mac` arrancó limpio en cada uno de los cinco lanzamientos
de esta sesión — `debug.log` sin una sola línea de error o excepción, "Entering main loop" cada vez, y
"Igor complete. Game exited" al cerrar sin ningún volcado de pila.

---

## 4 · Lo que la prueba en vivo confirmó y lo que no llegó a ejercitar

**Confirmado con capturas de pantalla reales, jugando con el ratón como dedo `0`:**
menú y sus 5 botones, "Continuar" activo/inactivo correctamente, transición a Opciones y de vuelta,
*sliders* de volumen arrastrables, interruptor de vibración, confirmación de "Borrar progreso" con "No"
como salida segura, joystick virtual (aparece donde tocas, sigue el arrastre), botón de disparo, aparición
y persecución de enemigos, colisión con pérdida de vida, transición a derrota, guardado de la mejor
puntuación, "Reintentar".

**No ejercitado en vivo, solo verificado por revisión de código y por `validar-proyecto.py`:**
la condición de victoria (mismo camino de código que la derrota, solo cambia la condición de entrada — no
jugué hasta 150 puntos); el guardado de emergencia real disparado por `os_is_paused()`/pérdida de foco
**durante una partida en curso** (perdí el foco de la ventana muchas veces por mis propias capturas de
pantalla, sin que el juego se cayera, pero no confirmé explícitamente que `partida.json` se escribiera en
ese instante ni que "Continuar" recuperase esa partida exacta); el comportamiento real en rotación de
dispositivo (bloqueada a propósito, ver `04·28 §1.2`); y, como ya se ha dicho, el multitáctil simultáneo de
verdad.

---

## 5 · ¿Algo en la biblioteca sobre móvil es hoy falso o está desfasado?

**No — no encontré ninguna afirmación de `04·28` ni de `01·12` que resultara falsa al contrastarla en vivo.** Todo lo que verifiqué —el comportamiento de
`os_is_paused()`, el patrón de creación de cámara, la existencia y firma de cada función usada, el
comportamiento de `font_add()` con *Included Files*— se comportó exactamente como está documentado. Lo que
encontré no es información falsa, es **información que falta**: el hueco de la fuente por defecto sin
acentos (§2.5-1), la tensión entre el suelo de 48 px y la altura disponible en apaisado (§2.5-2), y la
imposibilidad de probar multitáctil real desde un escritorio (§2.4). Los tres son candidatos honestos para
una ampliación futura de `04·28`, no correcciones de algo que dijera mal.

---

## 6 · Veredicto final

**¿Entrega hoy un agente con esta skill un juego móvil usable, o uno de escritorio con la resolución
cambiada?** Un juego móvil usable, con una condición: **el agente tiene que ejecutar el juego y mirarlo**,
no basta con compilar limpio. La skill deja clarísimo el "qué" de cada decisión específica de móvil —
resolución, densidad, zona segura, orientación, ciclo de vida, tamaño de botón, joystick virtual— con código
citable y verificado función por función. Lo seguí al pie de la letra y el resultado es un juego que se
controla exclusivamente con el pulgar, pensado para apaisado con dos zonas de contacto, con guardado de
emergencia y pausa reales.

Pero la propia biblioteca ya avisa, en su propia regla de oro, de que "compilar limpio no es funcionar" —
y esta prueba lo confirmó dos veces por cuenta propia: un botón desactivado indistinguible del activo y un
menú que se salía de la pantalla, los dos compilando sin un solo aviso. Y encontró un hueco que **ningún**
documento de la biblioteca cubre: la fuente por defecto de GameMaker no dibuja acentos españoles, lo cual,
para un proyecto cuya regla número uno es "todo el texto en español con tildes", es un fallo que un agente
que confíe ciegamente en "compila limpio, luego funciona" enviaría a producción sin enterarse.

---

## 7 · Limpieza

```
$ pkill -f "gm_prueba_movil" && pkill -f "Mac_Runner -game /Users/adrianpereradelgado/gm_prueba_movil"
$ ps aux | grep -i "gm_prueba_movil\|JuegoMovil" | grep -v grep
(sin salida — limpio)
$ rm -rf ~/gm_prueba_movil
$ ls ~/gm_prueba_movil
ls: /Users/adrianpereradelgado/gm_prueba_movil: No such file or directory
```

**Nota operativa, no un hallazgo sobre la skill**: a mitad de la prueba, dos sesiones de agente distintas en
este mismo Mac tenían cada una su propio `Mac_Runner` corriendo, ambos con el mismo título de ventana
literal `${project_name}` y, por defecto, la misma posición de pantalla — un par de capturas y clics de esta
sesión aterrizaron por error en la ventana del otro proyecto (`gm_prueba_gestion`, ajeno a esta prueba) antes
de que lo detectara por el argumento `-game` de `ps aux` y aislara mi proceso por PID. No se tocó nada
destructivo del otro proyecto (solo clics de navegación en su menú) y no se mató ese proceso.
