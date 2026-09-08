# R8 · Prueba de perfil: cooperativo local a dos jugadores, mismo teclado, pantalla compartida

> **Fecha:** 2026-09-08 · **Proyecto de prueba:** `~/gm_prueba_coop/gm_prueba_coop` (creado y
> destruido en esta sesión, fuera de la biblioteca) · **Plantilla:** `Blank Pixel Game` (una de
> las 9 que funcionan según la Trampa 1 de `12 · 09`) · **Toolchain:** `GMS2@2026.0.0.23`.
>
> **Encargo:** construir «un juego para dos jugadores en el mismo teclado, con pantalla
> compartida», pequeño pero completo (menú, opciones, pausa, bucle jugable con victoria y
> derrota, guardado, créditos), usando **solo** la skill `gamemaker-biblioteca` como fuente, y
> reportar con evidencia — cita exacta o «no me lo dijo».
>
> Sexta prueba de perfil de esta serie (arcade, aventura narrativa, puzzle con datos, móvil
> táctil, gestión con economía → **esta**: dos jugadores a la vez). Ataca lo que ningún perfil
> anterior probó: repartir la entrada entre dos personas reales en el mismo dispositivo.

---

## 0 · Veredicto honesto, por delante

**La biblioteca resuelve de sobra la mitad "dura" del problema — input repartido y cámara
compartida — con código de producción, verificado y cruzado entre cuatro documentos.** La otra
mitad — HUD duplicado, quién pausa, qué pasa cuando un jugador muere — está **en blanco**: cero
resultados de búsqueda, cero documento que lo mencione. Y la sesión encontró **un fallo que
habría llegado a producción sin avisar**: sin la Trampa 12, el juego entero —escrito en español
con tildes y eñes porque así lo exige el propio `CLAUDE.md` de este repositorio— habría
compilado limpio, pasado `validar-proyecto.py` limpio, y mostrado el texto **roto** en pantalla
("código" → "cdigo"). Ese es el hallazgo más importante de esta prueba, no una nota al margen.

También se encontraron dos hechos falsos/desfasados en documentos **fuera** del área de
cooperativo (detallados en §6), y dos trampas nuevas de herramienta (`resourcetool` rechaza el
evento Async System sin alternativa, y una escritura cruda por índice en `RoomOrderNodes` puede
tumbar el compilador entero sin ningún aviso al escribirla).

**Compila limpio, corre limpio, y las tres transiciones de estado (derribado, derrota, victoria
con guardado real) se verificaron EN VIVO, no solo por inspección de código.** El detalle de
cada comprobación está en §7.

---

## 1 · El juego construido

**"Dos al rescate"** — arena top-down única (1366×768), dos jugadores simultáneos:

- **Jugador 1**: `W A S D` mover · `F` acción/reanimar · `Q` pausa · azul.
- **Jugador 2**: flechas mover · `Enter` acción/reanimar · `Ctrl` pausa · naranja.
- Mando opcional y añadible en marcha para cualquiera de los dos (el teclado nunca deja de
  funcionar; si hay mando conectado en su ranura, manda en cuanto se mueve).
- 5 gemas que cualquiera recoge para un contador compartido, 4 enemigos que persiguen al jugador
  vivo más cercano, una meta que solo se abre con los dos jugadores encima a la vez.
- Si un jugador llega a 0 de vida, queda **derribado** (no muere: pierde el control, se dibuja
  más pequeño y atenuado) — el compañero lo reanima quedándose cerca 1,5 s. Si los dos están
  derribados a la vez, **derrota**. Recoger las 5 gemas y pisar la meta los dos a la vez,
  **victoria** — guarda el progreso.
- Menú principal, Opciones (volumen + panel de controles de solo lectura), Créditos, Pausa
  (cualquiera de los dos jugadores la abre y la navega), guardado con `06/scr_save_load.gml`
  reutilizado literal.

**Objetos** (13): `obj_juego`, `obj_input_manager`, `obj_menu_principal`, `obj_opciones`,
`obj_creditos`, `obj_jugador`, `obj_enemigo`, `obj_gema`, `obj_meta`, `obj_camara_director`,
`obj_hud`, `obj_pausa`, `obj_control_nivel`.
**Rooms** (4): `rm_menu` (arranque), `rm_opciones`, `rm_creditos`, `rm_juego`.
**Scripts propios** (4): `scr_input.gml`, `scr_camara.gml`, `scr_utilidades.gml`, y
`scr_guardado.gml` — este último es **una copia literal** de
`06 - Assets y Scripts/scr_save_load.gml` de la biblioteca, sin cambiar una línea de su lógica.

Rutas reales del proyecto (destruido al terminar esta auditoría, quedan aquí como referencia):
`~/gm_prueba_coop/gm_prueba_coop/objects/`, `~/gm_prueba_coop/gm_prueba_coop/scripts/`,
`~/gm_prueba_coop/gm_prueba_coop/rooms/`.

---

## 2 · ¿Te guió la skill para repartir la entrada entre dos jugadores, y para añadir mandos?

**Sí, de sobra, y con código que se pudo copiar casi literal.** Cuatro documentos, todos
enlazados entre sí:

1. **`04 - Recetas por género/47 - Beat em up y brawler.md` §8.1 "Input por jugador, como
   datos" (línea 587)** — da el constructor `BrawlerInput(_dispositivo_gamepad, _arriba, _abajo,
   _izq, _der, _ataque, _agarre)` y, literal:
   > `global.input_p1 = new BrawlerInput(-1, ord("W"), ord("S"), ord("A"), ord("D"), ord("J"),
   > ord("K")); global.input_p2 = new BrawlerInput(-1, vk_up, vk_down, vk_left, vk_right,
   > vk_numpad1, vk_numpad2);`

   Es exactamente WASD contra flechas — el reparto que pedía el encargo, ya resuelto.

2. **`01 - Fundamentos/12 - Input - teclado, ratón y gamepad.md`, "Varios mandos, uno por
   jugador (co-op local)" (línea 603)** — el patrón `mandos_por_jugador[]` +
   `mando_asignar()`/`mando_liberar()`, con la razón exacta de por qué dejar el hueco en `-1` en
   vez de encoger el array al desconectar un mando (para que el otro jugador no cambie de
   número a mitad de partida).

3. **`04 - Recetas por género/25 - Menú de opciones y ajustes.md` §5.8 "Perfiles de input por
   jugador: local co-op" (línea 735)** — avisa **explícitamente** de que la pestaña "Mando
   1/Mando 2" de §5.4 **no es** splitscreen de verdad (sigue escribiendo en el mismo
   `global.controles`), y da la forma correcta: un `global.controles_jugador[n]`, un struct
   completo por jugador, para que remapear el Jugador 2 no toque al 1.

4. **`04 - Recetas por género/02 - Top-Down _ Twin-Stick.md` §8, punto 8 "Local co-op" (línea
   880)** — enlaza hacia el punto 3 como "el punto de partida" para dar a cada jugador sus
   propias teclas.

**Lo que construí** (`scripts/scr_input/scr_input.gml`): un `InputJugador` que adapta
`BrawlerInput` — con una diferencia deliberada frente al original: en vez de "o teclado o mando"
(`dispositivo == -1` excluyente), el teclado de cada jugador está **siempre** activo (porque el
encargo es "mismo teclado") y el mando, si `obj_input_manager.mandos_por_jugador[n]` tiene una
ranura válida, se **combina** por encima en cuanto se mueve — así un mando se puede enchufar a
mitad de partida sin que deje de funcionar el teclado. Verificado con
`python3 _indice/buscar.py` que los símbolos usados (`gamepad_is_connected`,
`gamepad_axis_value`, `gamepad_button_check_pressed`, `gp_axislh`, `gp_axislv`, `gp_face1`,
`gp_padu/d/l/r`, `gp_start`) existen todos de verdad.

---

## 3 · ¿Te dijo cómo resolver la cámara, y lo pudiste implementar?

**Sí, con una técnica completa y con nombre — y también la alternativa que no usé.**

**`13 - Diseño y producción de videojuegos/19 - Cámaras de juego...md` §3.10 "Cámara
multijugador con zoom dinámico" (línea 746)** da la técnica de Itay Keren —
*position-averaging* (mirar al centro del grupo) + *zoom-to-fit* dinámico (alejar lo justo para
que quepan los dos) — con **código completo**: la función `camara_grupo_bbox(_obj_jugador)`, el
cálculo del zoom deseado a partir del `bbox` del grupo, y un **tether** que empuja de vuelta al
jugador que se aleja demasiado (citando *Gauntlet* como el ejemplo histórico de lo que pasa sin
él: los jugadores pueden bloquearse mutuamente sin poder cruzar el borde de pantalla).

Copié esa función **casi literal** a `scripts/scr_camara/scr_camara.gml`, y el bloque de Step
completo (lerp de centro, cálculo de zoom, tether) a `obj_camara_director` (End Step, tal y como
recomienda `01 · 10 §7`: "así la cámara reacciona a la posición YA actualizada del jugador").

**La alternativa documentada, que no usé pero también está resuelta**: pantalla partida estática
— `01 - Fundamentos/10 - Rooms, capas, cámaras y viewports.md`, "Pantalla partida (split
screen)" (línea 454) — dos viewports, dos cámaras, código completo con
`view_set_xport`/`view_set_wport`/`camera_create_view`. Elegí la cámara compartida porque es la
que la biblioteca desarrolla con más profundidad propia (tether, zoom cuantizado, la discusión de
pixel-perfect frente a subpíxel), no porque la de pantalla partida esté peor resuelta.

**Verificado en vivo, no solo leído**: la cámara corrió en tiempo real durante los tres escenarios
de prueba (§7) sin errores, con los dos jugadores moviéndose (por la IA de los enemigos
empujándolos) y el `with (obj_jugador)` del tether ejecutándose cada End Step.

**Hallazgo — cita cruzada rota en el propio §3.10 (línea 748)**:

> "Split screen estático (`04 · 14` §8, `01 · 10` §7) resuelve el caso simple."

`01 · 10 §7` es correcta (tiene el código de pantalla partida). **`04 · 14` §8 no** —
`04 - Recetas por género/14 - Multijugador.md` §8 se llama "Cómo escalarlo" y es sobre
*networking* online: *delta compression*, UDP fiable, rollback, lobbies persistentes, servidor
dedicado, *replays*. Leí la sección entera: no menciona pantalla partida ni una vez. Es una
referencia cruzada equivocada dentro de un documento que, por lo demás, es el más completo de
toda la biblioteca en el tema de esta prueba.

---

## 4 · ¿Y la interfaz duplicada, y quién controla la pausa y los menús?

### Interfaz duplicada: guía **indirecta**, no un documento propio

Búsquedas `--texto "HUD por jugador"` e `--texto "interfaz duplicada"`: **sin resultados**. No
hay ningún documento de la biblioteca dedicado a "cómo duplicar el HUD para dos jugadores". Lo
que sí hay, y sirvió, es una nota de pasada dentro de `13 · 19 §3.10` (la misma sección de la
cámara): recomienda dibujar el HUD en la capa GUI, "que no depende del `view_size` de la room" —
la razón de que el zoom-to-fit dinámico no deforme la interfaz. Construí el HUD (`obj_hud`) yo
mismo siguiendo esa idea: dos paneles simétricos con `display_get_gui_width()`/
`display_get_gui_height()`, uno por jugador, cada uno en su esquina y con el color de su equipo,
sin superponerse nunca porque las coordenadas GUI no cambian con el zoom del mundo. Funciona, y
funciona **por lo que dice `13 · 19`**, pero no hay un documento que enseñe el patrón "un panel
por jugador" en sí.

### Quién pausa: **no me lo dijo**, con un matiz importante

`04 - Recetas por género/41 - Transiciones, carga y pausa.md` §3.4.6 "Cuándo NO se puede (o no se
debe) pausar" (línea 978) dice, literal:

> "⚠️ Esta biblioteca no cubre pausa en red — la salida honesta es que «pausa» abra solo un menú
> local que no toque el estado compartido, o que el género lo prohíba explícitamente mientras
> haya otros jugadores conectados."

Eso es sobre multijugador **en red** (desincronización entre clientes), no sobre coop local en
el mismo sofá — ahí congelar el mundo entero (`pausar_de_verdad()`, que `41` sí resuelve para un
jugador) es correcto porque los dos ven la misma pantalla congelada. Pero la biblioteca **no
dice** quién de los dos jugadores puede pausar, ni cómo se navega un menú de pausa compartido.
Búsquedas `--texto "quién puede pausar"` y `--texto "pausa cooperativo"`: **sin resultados**.

**Decisión propia, documentada en el código** (`obj_pausa`, comentario de cabecera): cualquiera
de los dos jugadores puede pausar y despausar con su tecla, o con Escape universal; mientras está
en pausa, **los dos** mueven el mismo cursor del menú compartido. No es lo que dice la
biblioteca — es lo que decidí yo porque la biblioteca no lo dice.

---

## 5 · ¿Cubrió los casos incómodos: uno muere, desconexión, reaparición, separación?

Muy desigual — dos casos resueltos de sobra, dos en blanco:

| Caso | Cobertura | Evidencia |
|---|---|---|
| **El juego los separa demasiado** | ✅ Resuelto con nombre y código | Tether de `13 · 19 §3.10` (cita *Gauntlet*), implementado y activo en `obj_camara_director` |
| **Mando se desconecta** | ✅ Resuelto con nombre y código | `mando_liberar()` de `01 · 12`, deja el hueco en `-1` para no renumerar al otro jugador |
| **Uno muere y el otro sigue / reaparición** | ❌ No me lo dijo | `--texto "un jugador muere"` y `--texto "reaparición"` — sin resultados relevantes (el único hit de "reaparición" es una función de respawn de un solo jugador en `13 · 02`, sin relación con reanimar a un compañero) |

Para el caso sin cubrir construí una mecánica propia: **derribado en vez de muerte** (el jugador
pierde el control, no desaparece), reanimado por cercanía del compañero durante 1,5 s
(`revivir_frames_necesarios = 90`), con decaimiento del progreso si el compañero se aleja antes
de completarlo. Derrota solo si los **dos** están derribados a la vez. Verificado en vivo (§7):
provoqué las dos caídas dejando que los enemigos golpearan sin defensa, y `obj_control_nivel`
detectó la derrota correctamente en el primer Step en que ambas condiciones fueron ciertas.

---

## 6 · ¿Encontraste algo falso o desfasado?

Dos hallazgos, ninguno dentro del núcleo de cooperativo local, los dos verificados contra una
fuente independiente antes de darlos por buenos:

### 6.1 · Cita cruzada rota: `13 · 19` línea 748 → `04 · 14 §8`

Ya detallado en §3. `04 - Recetas por género/14 - Multijugador.md` §8 ("Cómo escalarlo") es sobre
compensar ancho de banda en redes online, no sobre pantalla partida. Leída la sección completa
(línea 1291-1338) para confirmar que no hay ninguna mención de split screen antes de reportarlo.

### 6.2 · Afirmación falsa sobre el operador `??`

`04 - Recetas por género/10 - Visual Novel y narrativa.md`, línea 1060:

> `// GML no tiene operador "??": inicializa el campo al crear el struct.`

**Es falso.** El manual oficial, espejado en este mismo repositorio
(`09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Overview/
Expressions_And_Operators.md`, líneas 33-56), documenta `??` y `??=` como operadores reales de
coalescencia de nulos, con su sintaxis exacta (`entrada ?? valor_si_null`) y un ejemplo
(`username = data.username ?? "INVALID USERNAME";`). Y la propia biblioteca los usa: el ejemplo
de migraciones de `13 · 06 §3.10` tiene `_d.dificultad ??= Dificultad.NORMAL;`, y el script que
reutilicé literal, `06/scr_save_load.gml`, usa el patrón `_valor[$ "clave"] ?? _por_defecto` con
normalidad. Usé `??` en mi propio código (`obj_juego`, cargando config/perfil) sin ningún
problema — otra confirmación de que el operador existe y funciona en el runtime
`2026.0.0.23`.

---

## 7 · Verificación en vivo — no solo inspección de código

### 7.1 · `validar-proyecto.py` (antes y después del arreglo de fuente)

```
37 archivos .gml · 715 llamadas analizadas · runtime del índice 2026.0.0.23

✓ Ninguna llamada a una función del runtime que no exista.
✓ Ninguna llamada a una función del runtime con un número de argumentos que no cuadre con su firma.
```

### 7.2 · `gm-cli compile` — salida real, sin recortar el resultado clave

```
Compile Rooms...
finished..... 0 CC empty
finished..... 0 CC empty
Compile Objects...
finished.... 0 empty events
...
Stats : GMA : sp=0,au=0,bk=0,pt=0,sc=57,sh=0,fo=0,tl=0,ob=13,ro=4,da=0,ex=0,ma=6,fm=0x929C69E62434
Igor complete.
◆  Compilation finished
EXIT CODE: 0
```

Cero `WARNING` (comprobado con `grep -i warning`, sin salida) — incluida la comprobación
específica de la Trampa 8 sobre el *included file* de la fuente, que sí habría avisado si el
`.ttf` se hubiera quedado fuera de `datafiles/`.

### 7.3 · Ejecución real con `gm-cli run`, tres escenarios forzados

No basta con `exit 0` (Trampa 4: el compilador no detecta una función inventada ni un fallo de
render). Se forzaron tres escenarios con `alarm[]` temporales (borrados antes de entregar) para
ejercitar el código que un jugador humano tardaría minutos en alcanzar:

1. **Derrota real**: dejé correr `rm_juego` sin ningún input (los enemigos persiguen solos).
   Log real:
   ```
   obj_juego listo — victorias previas: 0, mejor cosecha de gemas: 0
   [PRUEBA] Jugador 1 derribado
   [PRUEBA] Jugador 2 derribado
   [PRUEBA] DERROTA — los dos jugadores derribados a la vez
   ```
   Proceso vivo y estable durante todo el ciclo (comprobado con `ps aux`, ~55 % CPU sostenido,
   sin excepción en el log).

2. **Victoria real + guardado real**: forcé `gemas_recogidas = 5` y teleporté a los dos jugadores
   a la meta. Log real: `[PRUEBA] VICTORIA — save_game(perfil) devolvió 1`. El archivo apareció
   de verdad en disco:
   ```
   $ cat ".../com.yoyogames.macyoyorunner/save_perfil.json"
   {"checksum":"dca6b076de5f470fadb1801042de4da5945051f9","version":1.0,
    "fecha":"Tue Sep  8 17:41:39 2026","datos":"{\"victorias\":1.0,\"mejor_gemas\":5.0}"}
   ```

3. **Recarga del guardado**: relancé el juego sin forzar nada. Log real:
   `obj_juego listo — victorias previas: 1, mejor cosecha de gemas: 5` — confirma que
   `load_game("perfil")` leyó de verdad lo que `save_game()` había escrito en la ejecución
   anterior. Ciclo completo guardar→cerrar→cargar verificado, no asumido.

### 7.4 · La fuente española, verificada con una captura real (no una suposición)

Antes de escribir el informe comprobé si el texto en español se veía bien de verdad, con
`screen_save()` (no con una captura de escritorio: en esta máquina hay varias sesiones de
GameMaker corriendo a la vez y una captura de pantalla normal puede coger la ventana de otro
proyecto por error, como me pasó dos veces en esta misma sesión antes de darme cuenta). El PNG
real, después de aplicar la Trampa 12 (ver §8), muestra "código", "Cámara", "acción", "Diseño"
con sus tildes y su eñe intactas — guardado durante la sesión, borrado con el resto del proyecto
al terminar.

---

## 8 · ¿Las trece trampas sirvieron? ¿Alguna nueva propia?

**Sirvieron, y una de ellas evitó un fallo que habría llegado a "terminado" sin que nadie lo
notara.**

| Trampa | Aplicada | Resultado |
|---|---|---|
| 1 · plantillas rotas | Sí | Usé `Blank Pixel Game` (de las 9 que funcionan); creación del proyecto sin fallos |
| 2 · sandbox cuelga `resourcetool`/`compile` | Sí | `dangerouslyDisableSandbox: true` en las ~140 llamadas de `resourcetool`/`compile`/`run`; cero cuelgues |
| 3 · numeración de eventos | Sí | Usé `subtype=gui` (no `gui_begin`), `step_normal`/`step_end` — los `.gml` resultantes fueron exactamente `Draw_64.gml`/`Step_0.gml`/`Step_2.gml`, como promete la trampa |
| 4 · el compilador no detecta funciones inventadas | Sí, decisiva | Motivó correr `validar-proyecto.py` Y `gm-cli run` de verdad en vez de fiarme del `exit 0` — ver §7.3 |
| 7 · probar `resource info expr=project` antes de rendirse | Sí | Encontré `RoomOrderNodes` así, y lo usé con éxito (y luego con un fallo propio, ver 8.2 abajo) |
| 8 · `includedfile` deja `filePath` vacío | Sí, aplicada al pie de la letra | `mkdir datafiles && cp`, luego `resource set expr=project.IncludedFiles[0].filePath value=datafiles` — cero `WARNING`, `.ttf` confirmado dentro del `.zip` compilado |
| 9 · un subtype rechazado no significa que la propiedad cruda sea inalcanzable | Sí, confirmada en los dos sentidos | El `async_system` SÍ está fuera de alcance (§8.1); `RoomOrderNodes[0].roomId` SÍ se pudo tocar crudo (y ahí generé mi propio fallo, §8.2) |
| 12 · la fuente por defecto no dibuja acentos españoles | **Sí, la más importante de esta sesión** | Ver §8.3 |
| 13 · `screen_save()` invertido en Mac | Parcial — no reproducida | La captura de `screen_save()` salió del derecho, no invertida. Un solo dato, no contradice la trampa (pudo depender de esta build/ventana concreta), pero lo anoto porque no coincidió |

Las trampas 5, 6, 10 y 11 no aplican a este proyecto (no usé fuentes horneadas por
`resourcetool`, ni `directory_exists`/`create`, ni `OPTIONS SET`, y ningún `ResourceTool` se
comportó de forma no determinista en ~140 invocaciones).

### 8.1 · Trampa nueva: `resourcetool` rechaza el evento Async System sin alternativa

El patrón de `01 · 12` para detectar mandos que se conectan o desconectan en marcha depende del
evento **Async System**. Intenté crearlo exactamente como pide `resourcetool`:

```
$ gm-cli resourcetool eval "object event findorcreate name=obj_input_manager type=other subtype=async_system"
Invalid subtype 'async_system' for event type 'other'. Expected outside | boundary |
outside_view0 | boundary_view0 | game_start | game_end | room_start | room_end |
animation_end | animation_update | animation_event | end_of_path | user0 | broadcast_message
```

No está en la lista, y `object event types` tampoco lo lista en ninguna categoría (revisé las
177 líneas completas de esa tabla). Un agente que solo pueda usar `resourcetool` —como manda el
`CLAUDE.md` de este repositorio— **no puede crear ese evento por ningún nombre**. Lo resolví
sondeando `gamepad_get_device_count()`/`gamepad_is_connected()` cada Step en vez de reaccionar al
evento asíncrono — funcionalmente equivalente (el jugador no nota un frame de diferencia), pero
es un hueco real de la herramienta que no estaba documentado en las 13 trampas.

### 8.2 · Trampa nueva: `RESOURCE SET` sobre `RoomOrderNodes` acepta duplicados y tumba el compilador

Para probar `rm_juego` en caliente sin depender de que un humano navegara el menú, reordené
temporalmente `RoomOrderNodes` con `resource set expr=project.RoomOrderNodes[0].roomId
value=rm_juego` (la técnica cruda que recomienda la Trampa 9). El comando se aceptó sin ningún
aviso — pero dejó `rm_juego` **duplicado** en la lista (aparecía en el índice 0 y también en el
3, donde ya estaba `rm_menu` antes del cambio). El siguiente `gm-cli run` no dio un error de
GameMaker: tumbó el compilador entero con una excepción de .NET sin manejar:

```
Unhandled exception.
System.Reflection.TargetInvocationException: Exception has been thrown by the target of an invocation.
 ---> System.ArgumentOutOfRangeException: Index was out of range. Must be non-negative and less than the size of the collection. (Parameter 'index')
   at System.Collections.Generic.List`1.get_Item(Int32 index)
   at GMAssetCompiler.GMProjectSymbols.GatherResources()
   ...
◆  Game exited
```

precedido por 16 líneas de `Already added instance`. Lo reparé devolviendo el índice 0 a
`rm_menu` (mismo comando, valor correcto) y recompilé limpio. Es un fallo autoinfligido — nadie
me obligó a duplicar la entrada — pero demuestra que la vía cruda de la Trampa 9 **no tiene
ninguna validación de integridad referencial**: acepta con gusto un estado que el propio motor
no sabe procesar, y el error que sale al pisarlo es un *stack trace* de .NET en bruto, no un
mensaje de GameMaker que oriente a un agente sobre qué se rompió.

### 8.3 · La Trampa 12, en directo: el fallo que casi se me escapa

Escribí las ~30 cadenas de texto del juego con tildes y eñes completas, porque así lo exige el
`CLAUDE.md` raíz de este repositorio y el de este propio proyecto. Ni una sola herramienta de
verificación que usé —ni `gm-cli compile`, ni `validar-proyecto.py`, ni el propio `grep` sobre mi
código— habría detectado que, sin una fuente cargada con `font_add()`, el motor iba a
**omitir en silencio** cada `á é í ó ú ñ Ñ ¿ ¡` de la pantalla. Lo supe porque recordé la Trampa
12 al planificar el HUD, no porque ningún paso automático de este flujo me avisara.

Apliqué la solución exacta que da la propia trampa — conectar `font_add()` con la receta de
*Included Files* de la Trampa 8, en vez de depender de la fuente por defecto:

```gml
/// obj_juego — Create
global.fnt_ui = font_add("fuente_ui.ttf", 24, false, false, 32, 255);
```

con `datafiles/fuente_ui.ttf` copiado a mano y `project.IncludedFiles[0].filePath` fijado a
`datafiles` (§8, Trampa 8). Añadí `draw_set_font(global.fnt_ui)` al principio de cada evento
Draw GUI y dentro de mi función compartida `texto_centrado()`, con guardado/restauración de la
fuente anterior igual que ya hacía con la alineación y el color.

**Verificado, no asumido**: antes del arreglo, el razonamiento decía que el texto saldría roto;
después del arreglo, la captura real de `screen_save()` (§7.4) muestra "código", "Cámara",
"acción" y "Diseño" con sus tildes y su eñe intactas, y `gm-cli compile` sin recortar no mostró
ningún `WARNING` de *included file* — la comprobación exacta que exige la propia Trampa 8 antes
de dar la tarea por terminada.

**Por qué es el hallazgo más importante de esta sesión**: no es un caso límite exótico de
cooperativo. Es la combinación de dos reglas que *ya* estaban en la orden de esta tarea —
"escribe todo el texto en español con tildes y eñes" y "verifica antes de decir que está
hecho"— chocando contra un fallo que ninguna de las herramientas de verificación de esta misma
biblioteca detecta por sí sola. Sin la Trampa 12 explícita en el documento, este informe habría
dado el juego por "compila limpio, corre limpio" siendo mentira a nivel de píxel.

---

## 9 · Lo que quedó fuera de alcance, dicho sin adornos

- **Remapeo de teclas completo.** `04 · 25 §5` lo resuelve entero (captura, conflictos,
  perfiles); en Opciones solo hay un panel de solo lectura con el esquema fijo de cada jugador.
  No es una limitación de la biblioteca — es una limitación de tiempo de esta prueba, ya
  anotada como tal en el propio código (`obj_opciones/Create_0.gml`).
- **Mando real, con hardware.** Esta máquina no tenía ningún mando físico conectado durante la
  sesión (`gamepad_get_device_count()` devolvió 0 en todos los arranques). El código sigue el
  patrón verificado de `01 · 12` y compila/corre sin error, pero **nunca recibió una pulsación
  real de un mando** — solo el camino de teclado se ejercitó de verdad.
- **Colisión precisa.** Ningún objeto tiene sprite ni máscara de colisión (el juego no genera
  arte propio): el contacto jugador-enemigo, la recogida de gemas y la activación de la meta se
  resuelven por distancia (`point_distance`), no por `place_meeting()`/`instance_place()`. Es
  una simplificación deliberada para no mezclar "¿funciona el cooperativo?" con "¿funciona el
  arte?" — pero es una simplificación real, no una equivalencia perfecta a un juego con sprites.
- **Sin audio.** Hay un sistema de volumen completo (música/SFX, persistido en `config`) pero
  ningún sonido real: el proyecto no trae ningún asset de audio. El volumen se aplicaría a un
  grupo de audio existente si lo hubiera.
- **Guardado sin "estado de partida".** Clasificado según `13 · 06 §3.10`: hay Configuración
  (`config`) y Progreso persistente (`perfil`), pero no Estado de partida — el nivel es una sola
  arena corta, así que no hace falta guardar "a medias". En un juego más largo haría falta la
  tercera ranura (`partida_N.json`) que también describe esa misma sección.

---

## 10 · Veredicto

**La biblioteca cumple, con matices que importan.**

Para las dos piezas que de verdad distinguen a un cooperativo local de un juego de un jugador
—repartir la entrada entre dos personas en el mismo dispositivo, y sostener una cámara que no
deje a ninguna fuera de cuadro— la biblioteca dio código de producción, cruzado entre cuatro
documentos que se citan entre sí de forma coherente (con una excepción, §6.1), listo para
adaptar sin inventar una sola función: las 715 llamadas de este proyecto pasaron
`validar-proyecto.py` sin ni un solo hueco.

Para las piezas "blandas" del género —HUD duplicado, quién pausa entre dos jugadores locales,
qué pasa cuando uno cae— la biblioteca calla, con una honestidad que hay que reconocerle: no
inventa una respuesta a medias ni ofrece un patrón que no ha probado. Simplemente no está. Un
agente que no supiera buscar con `--texto` antes de escribir código habría podido inventarse una
respuesta ahí sin que nada se lo impidiera — la biblioteca no cubre el hueco, pero tampoco
miente sobre no cubrirlo.

Y el hallazgo que más pesa no es de cooperativo en absoluto: es que el propio flujo de
verificación que esta biblioteca enseña a seguir — compilar, `validar-proyecto.py`, mirar el
`exit code` — **no basta** para un proyecto escrito en español, y la única razón por la que este
informe no está firmando un juego con el texto roto es que la Trampa 12 existe, se leyó, y se
aplicó. Esa trampa debería estar más arriba en la lista de las trece, no en el puesto 12: es la
única que puede hacer que una tarea entera en español salga "terminada" y esté mal a la vista de
cualquiera que la abra.

---

## 11 · Limpieza

- Procesos `Mac_Runner`/`Igor` con `-game .../gm_prueba_coop/...` verificados y terminados con
  `pkill -f` filtrado por esa ruta exacta (nunca por nombre de proceso a secas: esta máquina
  tenía sesiones de GameMaker de otros proyectos corriendo en paralelo — `gm_prueba_3d/Templo3D`
  entre ellas — y `ps aux` se usó antes y después de cada `pkill` para confirmar que no se tocó
  ningún proceso ajeno).
- Ficheros de guardado propios (`save_perfil.json`, `save_perfil.bak1.json`,
  `captura_fuente.png`) generados durante las pruebas en la carpeta compartida
  `~/Library/Application Support/com.yoyogames.macyoyorunner/` — carpeta que usan a la vez
  varios proyectos de prueba distintos de otras sesiones (`lumbre_*`, `ritmo_*`, `partida.json`,
  `progreso.json` no son míos y no se tocaron) — borrados solo los tres ficheros identificables
  como propios de esta sesión.
- `~/gm_prueba_coop` completo, borrado al terminar esta auditoría.
