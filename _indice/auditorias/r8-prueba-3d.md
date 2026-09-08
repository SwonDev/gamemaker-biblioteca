# R8 · Prueba de la skill `gamemaker-biblioteca` — juego en 3D

**Fecha:** 8 de septiembre de 2026. **Agente:** Claude (Opus 5, 1M contexto), sesión aislada,
`~/gm_prueba_3d/Templo3D` (creado y borrado en esta misma sesión, nunca dentro de la biblioteca).
**Encargo:** «hazme un juego en 3D con GameMaker» — el perfil que más se aleja de lo habitual de
las siete pruebas anteriores (todas 2D): GameMaker no es un motor 3D, y el documento que lo cubre,
[`04 - Recetas por género/29 - 3D en GameMaker.md`](../../04%20-%20Recetas%20por%20g%C3%A9nero/29%20-%203D%20en%20GameMaker.md),
es el único que se pone a prueba en esta sesión de verdad — el resto de la biblioteca (menús,
pausa, guardado, checklist maestro) ya se validó en R5-R7 y aquí solo se reutiliza.

**Veredicto corto:** **sí, la biblioteca permite hacer un 3D jugable, no solo hablar de 3D.**
Cámara, proyección, vertex buffers, texturas, iluminación fija, billboards, colisión en planta y
mezcla 2D/3D funcionaron **a la primera** siguiendo el código de `04/29` casi literal — cero
errores de render, cero geometría corrupta, cero "pantalla vacía". Los dos únicos *runtime errors*
que golpearon esta sesión fueron **míos**, de encajar mis propias piezas (una llamada a función
sin cualificar, un global leído antes de que nadie lo asignara), no del documento. Sí encontré un
hueco operativo real que ni `04/29` ni el manual del agente cubren (cómo marcar «Página de Textura
Separada» por CLI) y una trampa nueva, propia del 3D, que tampoco está en las trece: el orden de
dibujo *dentro* de `Draw End` entre objetos distintos no lo decide la lógica, lo decide el
`depth`/layer de cada uno, y la receta de `04/29 §6` no lo advierte.

---

## 1 · Qué se construyó

Proyecto `Templo3D` (plantilla *Blank Pixel Game*, `gm-cli init`, la única con la que empecé de
cero sin *prefabs*), **1 060 líneas de GML** en 38 archivos, 0 sprites de la plantilla reutilizados
(todo dibujado con vertex buffers propios salvo tres texturas/billboards generados para esta
prueba).

- **5 salas**: `rm_splash`, `rm_menu`, `rm_opciones`, `rm_creditos`, `rm_juego`.
- **12 objetos**: `obj_juego` (persistente: textos, fuente, formato de vértice global, opciones,
  progreso), `obj_splash`, `obj_menu`, `obj_opciones`, `obj_creditos`, `obj_camara3d` (cámara 3D en
  primera persona), `obj_jugador` (el jugador ES la cámara), `obj_nivel` (construye la arena),
  `obj_pared` (caja de colisión estática), `obj_objetivo` (núcleo coleccionable, billboard),
  `obj_enemigo` (guardián que patrulla/persigue, billboard), `obj_hud`.
- **5 scripts**: `scr_malla3d` (formato de vértice, cubo unitario, suelo, matriz de cartel —
  literal de `04/29 §2`), `scr_colision3d` (AABB en planta + altura de suelo — de `04/29 §8`),
  `scr_menu` (navegación de menús como datos — de `04/18`), `scr_partida` (guardado/carga JSON en
  `game_save_id` — versión reducida de `06/scr_save_load.gml`), `scr_texto` (`txt(clave)`).
- **3 sprites**: `spr_piso` (suelo texturizado, en su propio grupo de textura — ver §3), `spr_objetivo`
  y `spr_enemigo` (billboards con recorte alfa).
- **1 Included File**: `fuente_ui.ttf` (Trampa 12 de `12/09`, ver §5).

**El juego**: *El Templo del Núcleo*. Arena 3D cerrada de 2048×2048 con muros perimetrales y cinco
pilares como cobertura, en primera persona (WASD + ratón, salto con gravedad). El jugador tiene que
recoger 5 núcleos de energía (billboards que flotan) mientras tres guardianes (billboards que
patrullan y persiguen) le quitan vida por contacto. Victoria al recoger los 5; derrota a vida 0.
Splash saltable → menú (Continuar/Jugar/Opciones/Créditos/Salir) → opciones (sensibilidad de
cámara, pantalla completa, borrar partida) → pausa real (Reanudar/Guardar partida/Volver al menú)
→ victoria/derrota con reintentar o volver al menú → créditos. Guardado real: posición, orientación,
vida, núcleos recogidos y mejor tiempo, en JSON dentro de `game_save_id`.

**Recortes explícitos** (regla del checklist maestro de `04/00`: lo que se recorta se dice):
- **Sin audio** — ni música ni SFX. El §7bis de `04/29` (oyente 3D, `audio_listener_position/
  orientation`, falloff en unidades de mundo) **no se ejercitó**: no hay un solo emisor en el
  proyecto. No es un fallo de la biblioteca, es alcance fuera de esta prueba centrada en 3D.
- **Sin raycast contra triángulos** (`04/29 §8`, Möller–Trumbore) — la arena no tiene rampas ni
  techos curvos; la colisión AABB en planta + altura de suelo bastó, tal como el propio documento
  predice («la mayoría de los juegos 3D colisionan en 2D»).
- **Sin *skybox* texturizado** (`04/29 §6`) — cielo resuelto con `draw_clear` + niebla, la
  alternativa que el propio documento llama «el truco más viejo y el que más rinde».
- **Iluminación fija integrada, no shader propio** (`04/29 §5`) — decisión de alcance, no de
  limitación: el documento da las dos vías completas, y la fija bastaba para esta arena.
- **Sensibilidad/pantalla completa no persisten entre sesiones** — solo la partida se guarda en
  disco; las opciones son de la sesión. Recorte deliberado, no un hueco de guardado.

---

## 2 · ¿Te dio la biblioteca lo necesario para la cámara, la proyección y el movimiento?

**Sí, palabra por palabra, y funcionó a la primera.** `obj_camara3d/Create_0.gml` y
`obj_camara3d/Draw_72.gml` en mi proyecto son una copia casi literal de `04/29` líneas 88-121
(montar la cámara, `gpu_set_ztestenable/zwriteenable`, `matrix_build_lookat` +
`matrix_build_projection_perspective_fov` con **los dos signos negativos** que el documento marca
como verificados contra código real en la línea 131 — el aviso explícito de que la ficha de `08/11`
dice lo contrario («FOV negativo con aspecto positivo») y que aquí manda lo verificado, no la
ficha general, se cumplió: con los dos negativos la escena salió derecha a la primera, sin
necesitar probar la otra combinación). `camera_apply()` (línea 119, «sin esto no pasa NADA») estaba
en mi lista de sospechosos antes incluso de escribir código, y no hizo falta usarla como depuración
porque nunca faltó.

El movimiento en primera persona (`obj_jugador/Step_0.gml`) es el bloque de `04/29 §7` líneas
619-638 (`window_mouse_set_locked`, `window_mouse_get_delta_x/_y`, la fórmula de movimiento relativo
a `giro`) trasplantado del objeto `obj_jugador` de doc de ejemplo al mío, más gravedad y salto de
`§8` líneas 894-901. Cero adaptación de fórmulas, solo cablearlo a mis variables.

**Captura real de la escena** (`gm-cli run --target mac`, jugando con teclado real vía `cliclick`,
sin retocar nada tras la captura):

Suelo texturizado en perspectiva correcta, pared con sombreado, esquina con las dos paredes
visibles, niebla fundiendo el techo con el cielo — el resultado de `camera_apply()` +
`matrix_build_lookat` + `matrix_build_projection_perspective_fov` funcionando de verdad, no una
descripción de que debería funcionar.

---

## 3 · ¿Supiste construir la geometría (vertex buffers, formatos de vértice)?

**Sí, y sin necesitar ni un ciclo de depuración.** `scr_malla3d.gml` es `04/29 §2` casi carácter
por carácter: `malla_vertice()`, `malla_cara()` (líneas 214-231), `malla_cubo()` (234-256) y
`malla_suelo()` (262-286). La única decisión propia fue una optimización que el propio documento
sugiere en `§9` línea 933 («un buffer por malla, no por objeto») llevada un paso más allá: en vez
de construir un cubo por cada tamaño de pared/pilar, construí **un único cubo unitario** (semi-lado
1) y lo escalo con `matrix_build(x, y, z, 0, 0, 0, semi_x, semi_y, semi_z)` — el propio parámetro
de escala de `matrix_build` que `§1` línea 182 ya usa para colocar mallas. Con eso, los cuatro
muros perimetrales y los cinco pilares comparten dos vertex buffers (`vb_caja_muro`,
`vb_caja_pilar`), y `obj_nivel/Draw_0.gml` los dibuja con un `with (obj_pared) { ... }` que cambia
solo la matriz de mundo por instancia — el patrón exacto de la línea 944 de `§9`.

El suelo (`malla_suelo`, 16×16 celdas de 128 px) salió texturizado y con la textura repetida
correctamente **a la primera compilación limpia** — sin el bug clásico de UV mal calculadas que
`§2` avisa («el orden en que declaras los atributos es el orden en que hay que escribirlos»): seguí
el orden `posición → normal → texcoord → color` del formato al pie de la letra en
`malla_vertice()`, y no hubo vértices corruptos ni geometría girada.

**El único hueco real que encontré está fuera de `04/29`**: activar «Página de Textura Separada»
—que el propio documento exige en `§3` línea 305-309 para que `gpu_set_texrepeat` no mezcle
sprites vecinos de la misma página— **no tiene ninguna propiedad booleana alcanzable por
`resourcetool`**. Comprobé el esquema completo del recurso sprite con
`resource info expr=spr_piso KEYS` (33 campos listados, incluidos `DynamicTexturePage` y
`textureGroupId`, pero **ningún** `SeparateTexturePage`) y confirmé que el mecanismo real es crear
un **grupo de textura dedicado** y asignarlo:
```
gm-cli resourcetool eval "texturegroup create name=tg_piso"
gm-cli resourcetool eval "texturegroup set group=tg_piso resources=spr_piso"
```
Esto consigue el mismo efecto práctico (el sprite vive en su propia página), pero **ni `04/29` ni
el manual del agente (`12/09`) documentan esta traducción** de «marca la casilla en el editor» a
un comando de CLI. Es un hueco operativo, no una afirmación falsa: el documento dice *qué* hace
falta (`§3`), pero no *cómo* conseguirlo sin el IDE.

---

## 4 · ¿Y las colisiones en 3D, que GameMaker no da hechas?

**Sí, con el criterio correcto y sin sobre-ingeniería.** `04/29 §8` líneas 776-784 lo dice
explícito: «la mayoría de los juegos 3D colisionan en 2D» — planta (x, y) más una altura de suelo,
como hacía *Doom*. Es exactamente lo que este juego necesitaba (paredes verticales de suelo a
techo, terreno plano), así que usé:

- **`cajas_solapan()`** (`§8` líneas 791-795) para el jugador y los guardianes contra las paredes,
  renombrada a `punto_choca_pared()` en mi proyecto porque la reutilicé **para ambos** — el
  jugador y los enemigos comparten la misma función de colisión, sin duplicar código.
- **El patrón de altura de suelo + gravedad + salto** (`§8` líneas 856-901), con
  `altura_del_terreno()` reducida a `return 0` (arena plana) pero dejada como función, no como
  constante, tal como el comentario del propio documento sugiere para poder sustituirla por un
  mapa de alturas real sin tocar el resto del código.

**No usé el rayo contra triángulo (Möller–Trumbore, `§8` líneas 808-846)** porque no hacía falta —
ni rampas, ni techos curvos, ni disparo con puntería de precisión. Lo leí completo y lo entendí
(la explicación de `u`/`v` como coordenadas baricéntricas para interpolar el punto de impacto es
clara), pero es honesto decir que **no lo puse a prueba en código real** en esta sesión: el
juego no lo necesitaba, exactamente como el propio documento predice para este tipo de nivel.

---

## 5 · ¿Te avisó de los límites reales, o te dejó creer que todo es posible?

**Avisó, y de una forma que cambió decisiones reales antes de escribir una línea.** Tres avisos
concretos que seguí al pie de la letra:

1. **El árbol de decisión de `§` inicial** (líneas 25-37) me hizo decidir en 30 segundos que este
   encargo caía en «escenario 3D con jugabilidad 2D» / «2.5D estilo Doom», no en «juego 3D moderno»
   — y la tabla de `§` «Qué es razonable y qué no» (líneas 39-50) confirmó que un mundo cerrado con
   terreno plano y colisión AABB es ✅ razonable, mientras que físicas 3D rígidas o un mundo abierto
   son ❌ nativamente imposibles. No tuve que descubrirlo por las malas.
2. **El aviso de GMRT/GM3D** (`§` líneas 57-71) es el que más valor tuvo de toda la sesión: sin él,
   un agente sin memoria de que GM3D existe pero está incompleto en LTS 2026 podría perder horas
   intentando `GM3D_Scene.loadGltf()` o símbolos parecidos, que **no existen** en el runtime
   `2026.0.0.23` (verificado aquí también con `buscar.py --listar GM3D` → 0 símbolos, igual que el
   documento afirma). Me ahorró ese callejón sin salida antes de entrar en él.
3. **La tabla de librerías de `§8`** (líneas 908-915: ColMesh, DS-3DCollisions, BBMOD, Cardboard,
   Stack3D) me dejó claro que existen alternativas si el AABB casero se quedara corto — no las usé
   porque no hicieron falta, pero saber que están descargadas y dónde es justo el tipo de aviso
   honesto que evita reinventar una rueda a medias.

---

## 6 · ¿Las trece trampas te sirvieron? ¿Alguna nueva propia del 3D?

**Dos de las trece se usaron en vivo, y las dos evitaron exactamente el fallo que prometían.**

- **Trampa 8** (`includedfile` deja `filePath` vacío): reproducida en vivo, letra por letra —
  `resource create type=includedfile name=fuente_ui.ttf` dejó `"filePath":""`; corregido con
  `mkdir datafiles && cp` + `resource set expr=project.IncludedFiles[0].filePath value=datafiles`.
  Compilando **sin** `--errors-only` confirmé cero `WARNING` y `unzip -l ... | grep ttf` mostró
  `assets/fuente_ui.ttf` en el paquete.
- **Trampa 12** (la fuente por defecto no dibuja acentos): evitada por completo *antes* de que
  ocurriera, usando `font_add("fuente_ui.ttf", 24, false, false, 32, 255)` desde el principio en
  vez de `draw_set_font(-1)`. Cada captura de pantalla de esta sesión — menú, opciones, créditos,
  HUD, victoria, derrota — muestra tildes y eñes perfectas: «Núcleo», «Créditos», «¡NÚCLEO
  ESTABILIZADO!», «energía». Sin esta trampa ya conocida, este juego habría salido con los acentos
  comidos en silencio, exactamente como le pasó a R7 antes de que se documentara.

**Trampa nueva, propia de construir 3D con varios objetos, no registrada en las trece ni en el
`§` «Las trampas» final de `04/29`:**

> **El orden de dibujo DENTRO de la fase `Draw End` entre instancias de objetos distintos no lo
> decide la lógica del pase 3D, lo decide `depth`/layer — y `04/29 §6` no lo advierte.**
>
> La receta de `§6` (líneas 516-521) dice: `Draw Begin` monta la cámara, `Draw` dibuja lo opaco,
> `Draw End` dibuja transparencias/carteles **y** apaga el 3D antes de la GUI. Pero si el cierre
> del pase 3D (mi `obj_camara3d · Draw End`, que hace `gpu_set_ztestenable(false)` y
> `draw_set_lighting(false)`) se ejecuta ANTES que los carteles de `obj_objetivo`/`obj_enemigo`
> (que también viven en Draw End), los billboards se dibujarían sin z-test y sin luz — un bug
> silencioso, no un crash. GameMaker decide ese orden por el `depth` de cada instancia (heredado
> del layer en el que se creó), no por qué objeto "lógicamente" debería ir último. En mi proyecto,
> `obj_nivel`/`obj_objetivo`/`obj_enemigo` se crean en el mismo layer que `obj_nivel` (profundidad
> alta, se dibujan primero) y `obj_camara3d` quedó en un layer de profundidad más baja (se dibuja
> después) **por una coincidencia del orden en que `ROOM INSTANCE CREATE` fue creando layers
> nuevos**, no por diseño. Lo hice robusto a propósito fijando `depth = -1000` en
> `obj_camara3d · Create` (ver el comentario en ese archivo), para que el cierre del pase 3D
> **siempre** sea lo último de `Draw End`, pase lo que pase con el orden de creación de la sala.
> Vale la pena añadirlo a `§6` de `04/29` o a la tabla de trampas.

**Un segundo hallazgo, no específico de 3D pero que el diseño de un formato de vértice
*compartido entre objetos* pone en evidencia con más facilidad que en un juego 2D normal:**
leer `global.una_variable` que **nunca** se asignó en ningún sitio no es «`undefined`», es un
error de ejecución («not set before reading it») — incluso dentro de `is_undefined(...)`, porque
el fallo ocurre evaluando el argumento, antes de que la función pueda devolver nada. Lo comprobé
en vivo: `obj_nivel · Create` intentaba un patrón defensivo (`if (is_undefined(global.formato_3d))
{ ...crearlo... }`) para no depender de qué objeto se creara antes en la sala, y **crasheó** la
primera vez que `obj_nivel` se creó antes que `obj_camara3d` (que es quien normalmente lo crea) —
exactamente lo que pretendía evitar. La corrección real no es `is_undefined()` (hace falta
`variable_global_exists()` para comprobarlo sin riesgo), sino **no depender del orden de creación
en absoluto**: moví la creación de `global.formato_3d` a `obj_juego · Create`, el único objeto
persistente que garantizado se crea antes que cualquier cosa de `rm_juego`. Detalle completo en
`objects/obj_juego/Create_0.gml` de la sesión (ya borrado con el proyecto, pero el patrón queda
documentado aquí).

---

## 7 · Compilación y ejecución reales

```
$ python3 "_indice/validar-proyecto.py" ~/gm_prueba_3d/Templo3D --todo
38 archivos .gml · 561 llamadas analizadas · runtime del índice 2026.0.0.23

✓ Ninguna llamada a una función del runtime que no exista.
✓ Ninguna llamada a una función del runtime con un número de argumentos que no cuadre con su firma.

$ gm-cli compile --toolchain GMS2@2026.0.0.23      # SIN --errors-only, la única que muestra
                                                     # el WARNING de la Trampa 8 si algo falla
[…]
│  Compile Objects... finished.... 1 empty events   # obj_creditos·Create, vacío a propósito
│  Final Compile finished.
│  Stats : GMA : sp=3,au=0,bk=0,pt=0,sc=42,sh=0,fo=0,tl=0,ob=12,ro=5,da=1,ex=0,ma=6,…
│  Igor complete.
◆  Compilation finished
```
`grep -i "warning\|error"` sobre la salida completa: **ninguna coincidencia real** (solo el
`Failed to load Options from local_settings.json` benigno de cualquier proyecto sin config local).
`da=1` confirma la fuente empaquetada de verdad (Trampa 8, corregida).

**`gm-cli run --toolchain GMS2@2026.0.0.23 --target mac`**, jugado de verdad —no solo compilado—
en seis lanzamientos distintos de esta sesión, con `cliclick`/`osascript` simulando teclado real
(ver §8 sobre por qué hizo falta cambiar de herramienta a mitad de sesión) y `screencapture` para
las capturas. **Confirmado con capturas de pantalla reales y/o `debug.log`, jugando de verdad**:

- Splash saltable, menú con «Continuar» inactivo/activo según haya partida guardada.
- **La escena 3D real**: suelo texturizado en perspectiva, paredes con sombreado, esquina con dos
  paredes visibles, niebla — la prueba de que la tubería 3D entera funciona, no una descripción.
- Guardián que detecta, persigue y golpea al jugador por contacto (con enfriamiento) → vida a 0 →
  pantalla de derrota (fondo rojo, «DESTRUIDO POR LOS GUARDIANES», tiempo, mejor tiempo, Reintentar
  / Volver al menú).
- Recogida de los 5 núcleos → victoria (fondo verde, «¡NÚCLEO ESTABILIZADO!», mejor tiempo
  actualizado) → el guardado se dispara y el footer del menú principal pasa de «Sin marca todavía»
  a «Mejor tiempo: 1 s · Núcleos x1» al volver.
- Menú de pausa real (Reanudar/Guardar partida/Volver al menú), con la navegación resaltando la
  opción actual.
- **El ciclo completo de guardado y «Continuar»**, verificado por `debug.log` con marcadores
  propios de esta sesión (quitados del código antes de la compilación final citada arriba):
  `R8_PARTIDA_GUARDADA en_curso=1 x=256 y=256 mejor_tiempo=1` al guardar en pausa, seguido de
  `R8_CONTINUAR_RESTAURADO x=256 y=256 z=48 giro=45 salud=100` al elegir «Continuar» desde el
  menú — la posición, altura, orientación y vida guardadas volvieron exactas.
- Pantalla de Opciones («Sensibilidad de cámara: 0.15», «Pantalla completa: No», «Borrar partida
  guardada») y Créditos (texto multilínea con `draw_text_ext`, tildes correctas) legibles y
  navegables.

**No verificado visualmente, solo por comportamiento indirecto y revisión de código**: nunca vi un
guardián o un núcleo dibujado *en pantalla* en una captura (el jugador nunca quedó orientado hacia
uno en el momento exacto de una captura) — pero la lógica que los dibuja (`cartel_matriz` +
`draw_sprite_ext` con recorte alfa, literal de `04/29 §6`) es la misma en los dos objetos, y **el
comportamiento que depende de que existan de verdad en el mundo 3D sí se confirmó**: los guardianes
llegaron hasta el jugador y le hicieron daño (exige que su posición 3D y su movimiento sean reales,
no solo que compile), y recoger los 5 núcleos disparó la victoria (exige que la comprobación de
distancia 3D del núcleo funcione). La iluminación por vértice tampoco se distinguió sin ambigüedad
en las capturas (paredes lisas de un solo color, sin suficientes vértices visibles a la vez para
juzgar el sombreado por Gouraud a simple vista): `draw_set_lighting`/`draw_light_define_*` se
llamaron sin ningún error de compilación ni de ejecución, pero no puedo afirmar con capturas que
el degradado de luz se vea bien, solo que las llamadas no fallan.

---

## 8 · Nota operativa: la interferencia entre sesiones de agente, confirmada en vivo

`12/09 §4.3` avisa: «con más de una sesión de agente activa en el mismo Mac, una captura o un clic
pensados para tu juego pueden aterrizar en la ventana del otro». Esta sesión lo confirmó de forma
directa y repetida: en el momento de las pruebas interactivas había **otras tres** ventanas
`Mac_Runner` corriendo en el mismo Mac (`gm_prueba_ritmo`, `gm_prueba_coop`, `gm_prueba_masivo`,
tres sesiones de agente ajenas), todas con el título literal `Pixel Game` — indistinguibles a
simple vista. Varias capturas y pulsaciones de esta sesión aterrizaron en las ventanas ajenas antes
de aislar el proceso propio por el argumento `-game <ruta>` de `ps -ef`, tal como el documento
recomienda. No se tocó nada destructivo de esos otros proyectos (solo navegación de menú). Un
hallazgo adicional, no cubierto por el documento: `osascript`/System Events resultó **poco fiable**
para mantener el foco de ventana el tiempo suficiente entre una activación y una pulsación con
varias sesiones compitiendo; `cliclick` (clic real + `kp:`/`t:` por eventos `CGEvent`) demostró ser
sustancialmente más fiable en esta máquina concreta y es la herramienta que finalmente permitió
completar la partida de principio a fin con teclado real.

---

## 9 · ¿Hay algo falso o desfasado en `04/29` o en los documentos de dibujo?

**No.** Todo lo que pude contrastar en código real y en pantalla se comportó exactamente como
`04/29` lo describe: el par de signos negativos del FOV/aspecto, `cull_counterclockwise` como cara
frontal correcta, el requisito de `vertex_format_add_normal()` para que la luz haga algo,
`camera_apply()` como interruptor obligatorio, el orden de atributos del formato de vértice, el
patrón de recorte alfa para vegetación/objetos con `gpu_set_alphatestenable`, la exigencia de
Página de Textura Separada para que `gpu_set_texrepeat` no mezcle sprites vecinos, el aviso de que
GM3D no existe todavía en LTS 2026 (confirmado también aquí con `buscar.py`). Lo que encontré no es
información falsa, es **información operativa que falta** — el hueco de §3 (cómo marcar «Página de
Textura Separada» sin el IDE) y la trampa de orden en `Draw End` de §6 — candidatos honestos para
ampliar el documento, no correcciones de algo que dijera mal.

---

## 10 · Veredicto final

**¿Permite la biblioteca hacer un 3D jugable con GameMaker, o solo hablar de 3D?** Permite hacerlo
jugable, de verdad, y lo hizo con menos fricción que las pruebas 2D anteriores en la parte que
más miedo daba (la tubería 3D): cámara, proyección, geometría y colisión funcionaron a la primera
copiando el código de `04/29` casi literal. Los dos bugs de ejecución reales de esta sesión fueron
míos —encajar mis propias piezas entre varios objetos—, no del documento, y los cacé exactamente
con el método que la propia biblioteca prescribe: compilar limpio **no basta**, hay que ejecutar
y leer la salida real (`gm-cli run`, `debug.log`), que es donde aparecieron los dos «not set before
reading it» que `gm-cli compile` había dejado pasar sin un solo aviso.

Donde la biblioteca destaca especialmente en 3D, más que en cualquier perfil 2D probado hasta
ahora, es en **decir que no** con criterio: el árbol de decisión inicial, la tabla de qué es
razonable, y el aviso de GMRT/GM3D evitaron que esta sesión perdiera tiempo en un callejón sin
salida (una API que no existe todavía en el runtime instalado) antes de escribir una sola línea.
Eso es exactamente lo que una base de conocimiento anti-alucinación tiene que hacer, y en 3D — el
terreno donde GameMaker es más débil y donde más fácil es que un agente se invente algo — lo hizo
mejor que en ningún otro perfil probado hasta ahora.

**Lo que queda pendiente de cerrar en `04/29`**: documentar la traducción de «Página de Textura
Separada» a un comando de CLI real (§3), y advertir del orden de `Draw End` entre distintos
objetos como una trampa explícita (§6) — los dos huecos operativos, no factuales, que esta sesión
encontró.

---

## 11 · Limpieza

```
$ ps -ef | grep -- "-game .*/gm_prueba_3d/" | grep -v grep
(sin salida tras el kill — proceso propio aislado y terminado por PID, no pkill -f Mac_Runner)
$ rm -rf ~/gm_prueba_3d
$ ls ~/gm_prueba_3d
ls: /Users/adrianpereradelgado/gm_prueba_3d: No such file or directory
```
