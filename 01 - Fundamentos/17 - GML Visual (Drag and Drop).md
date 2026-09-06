# 17 · GML Visual (Drag and Drop)

> **Fuentes:** espejo local del manual oficial (`manual.gamemaker.io`, descargado 2026-09-01),
> consultado 2026-09-06.
> - <https://manual.gamemaker.io/lts/es/Drag_And_Drop/Drag_And_Drop_Overview/DnD_Overview.htm>
> - <https://manual.gamemaker.io/lts/es/Drag_And_Drop/Drag_And_Drop_Overview/Constructing_Action_Block_Code.htm>
> - <https://manual.gamemaker.io/lts/es/Drag_And_Drop/Drag_And_Drop_Overview/Applying_Actions_To_Other_Instances.htm>
> - <https://manual.gamemaker.io/lts/es/Drag_And_Drop/Drag_And_Drop_Overview/Action_Block_Functions.htm>
> - <https://manual.gamemaker.io/lts/es/Drag_And_Drop/Drag_And_Drop_Overview/Changing_DnD_To_Code.htm>
> - <https://manual.gamemaker.io/lts/es/Drag_And_Drop/Drag_And_Drop_Overview/Right_Mouse_Button_Menu_Options.htm>
> - <https://manual.gamemaker.io/lts/es/Drag_And_Drop/Drag_And_Drop_Reference/DnD_Reference.htm> y las
>   27 páginas de biblioteca de cada familia de acciones que cuelgan de ella (Common, Instance,
>   Instance_Vars, Sequences, Mouse_And_Keyboard, Gamepad, Movement, Collisions, Drawing, Tiles,
>   Audio, Loops, Switch, Data_Structures, Data_Types, Buffers, Files, Random, Cameras, Rooms,
>   Paths, Timelines, Game, Miscellaneous, Particles, Time_Sources, Layers)
> - <https://manual.gamemaker.io/lts/es/IDE_Tools/The_Debugger.htm>
> - `python3 "_indice/buscar.py" <símbolo>` para verificar cada función de la tabla del §4.

---

> Qué es GML Visual, cómo se lee un proyecto hecho en él, y sobre todo **la tabla de
> equivalencias acción → GML** para poder traducir o depurar un proyecto que llega en Drag and
> Drop. No cubre el editor de código de texto (eso es
> [01 · El IDE y el flujo de trabajo](./01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md)) ni
> la sintaxis del lenguaje una vez conviertes (eso es el resto de `01 - Fundamentos/`, empezando
> por [02 · Tipos de datos y variables](./02%20-%20Tipos%20de%20datos%20y%20variables.md)).

---

## 1. Qué es GML Visual y para quién

**GML Visual** (el nombre desde GMS2; el manual y la comunidad todavía lo llaman **Drag and
Drop** o **DnD**, y así aparece en menús antiguos) es una forma de escribir el mismo lenguaje
—GML— arrastrando **bloques de acción** en vez de tecleando texto. No es un lenguaje aparte, no
es más lento en tiempo de ejecución y no es "modo fácil de mentira": es **GML representado como
árbol de nodos**, y detrás de cada bloque hay una función o una sentencia real del lenguaje. El
manual lo dice así en la página de resumen: *"esto no quiere decir que no estés programando
código cuando usas GML Visual, ya que lo haces, sólo que tu código se crea y se presenta de
forma visual"*.

Tres perfiles concretos para los que este documento importa:

- **Quien empieza de cero.** No hay que aprender la sintaxis de GML *y* la lógica de programación
  a la vez. Los dos tutoriales oficiales de GameMaker para principiantes —*Fire Jump* y *Hero's
  Trail*— están escritos en DnD, y el propio IDE ofrece la opción de crear el proyecto entero "en
  GML Visual" desde la pantalla de inicio. Si tu material de aprendizaje es alguno de esos dos
  tutoriales, este documento es el puente hacia el resto de la biblioteca, que está en GML.
- **Quien viene de Scratch, Blueprints (Unreal) o Construct.** La mecánica es la misma: bloques
  que se encadenan visualmente, con "agujeros" para variables y expresiones. La diferencia real
  con Scratch es que en GML Visual los campos de valor **siguen aceptando expresiones y funciones
  de GML escritas como texto** (`random(10)`, `obj_jugador.hp`), así que nunca es 100 % sin
  teclear — es más parecido a Blueprints que a Scratch en ese sentido.
- **Un LLM al que le llega un proyecto ajeno en DnD.** `AGENTS.md` prohíbe editar `.yy` a mano
  porque el formato es frágil — y un evento DnD **vive dentro del `.yy`** del objeto, no en un
  `.gml` de texto. Si te piden "arréglame este evento" o "pásame esto a código" sobre un proyecto
  así, no puedes abrir el archivo y editarlo como texto: necesitas o bien el MCP
  `gamemaker-resource-tool` / `gm-cli resourcetool eval`, o bien saber leer el árbol de acciones
  para razonar sobre él y proponer el GML equivalente. Este documento es la referencia para lo
  segundo; la §4 es la tabla que hace posible lo primero sin alucinar una función.

Por qué el manual lo trata como **lenguaje de primera clase** y no como una curiosidad: la
[Referencia de GML Visual](../09%20-%20Manual%20oficial/manual-lts-2026-es/Drag_And_Drop/Drag_And_Drop_Reference/DnD_Reference.md)
documenta unas **270 acciones** repartidas en 27 familias, con su propia página de argumentos y
ejemplo para cada una — el mismo tratamiento que recibe cualquier función de GML. En el espejo
español de esta biblioteca ocupa **313 páginas**, el 10 % de las 3 142 del manual completo. Antes
de este documento, la biblioteca no tenía ni un párrafo sobre el tema.

> ⚠️ Nada de lo anterior significa que este proyecto o el resto de la biblioteca recomienden
> empezar en DnD. La convención de esta biblioteca —y la de cualquier proyecto de cierto tamaño—
> es GML de texto: ver [§9](#9-cuándo-dar-el-salto-a-gml). Este documento existe para **leer y
> traducir** DnD, no para promover escribir en él desde hoy.

---

## 2. Cómo se lee un bloque de acción: eventos, cadenas y anidado

Un evento (Create, Step, Draw…) de un objeto en modo GML Visual abre una ventana de **código**
con dos paneles: la **Visión general de la acción** a la izquierda (la lista abreviada, en
orden de ejecución, de cada bloque) y el **workspace** a la derecha, donde los bloques aparecen
expandidos con sus argumentos. A la derecha de todo está la **caja de herramientas**, con las 27
bibliotecas de acciones (ver §3) y una barra de búsqueda que filtra por texto (escribir
"dibujar" muestra solo las acciones de dibujo).

### 2.1 · Encadenado: abajo es secuencia, al lado es anidado

Esto es lo único que hay que interiorizar para leer cualquier árbol DnD:

- Una acción **debajo** de otra significa "y luego esto" — secuencia normal, como una línea de
  código detrás de otra.
- Una acción **al lado** (a la derecha) de otra que abre una subcadena —`If Variable`, `If
  Expression`, `For`, `While`, `Repeat`, `Loop`, `Switch`/`Case`, `Apply To...`— significa "esto
  ocurre *dentro* del bloque", como el cuerpo entre `{ }` de un `if` o un bucle en GML de texto.
  Las acciones que abren subcadena se identifican porque el manual describe explícitamente que
  hay que "soltarlas al lado de la acción, no debajo".
- Algunas acciones tienen **dos** puntos de enganche: `If Variable` tiene el flujo normal debajo
  (lo que pasa después del if) y una cadena lateral (lo que pasa si la condición es verdadera).
  En GML de texto: lo lateral es el cuerpo del `if { }`, lo de abajo es el código que sigue al
  cierre de la llave.

```
Si la variable (hp <= 0)          →   if (hp <= 0) {
 └─ Establecer sprite (spr_muerto)  →      sprite_index = spr_muerto;
 └─ Llamada de función (morir)      →      morir();
Ir a la siguiente sala             →   }
                                        room_goto_next();
```

### 2.2 · Variables objetivo y ámbito de la acción

Dos conceptos que el manual llama **variables objetivo** (target) y **ámbito de acción** (scope)
y que no tienen equivalente visual en GML de texto porque en texto son implícitos:

- **Variable objetivo con "Temp" marcado** → crea una `var _nombre` (variable local, solo dentro
  del evento/script). **Sin marcar** → crea o reutiliza una variable de instancia
  (`nombre = valor`). Es la misma distinción de
  [02 · Tipos de datos y variables §"Ámbito de las variables"](./02%20-%20Tipos%20de%20datos%20y%20variables.md),
  solo que aquí es una casilla en vez de la palabra `var`.
- **Ámbito de la acción** (`self` por defecto, `other`, `all`, un objeto concreto, o una
  expresión/ID) es el equivalente visual de anteponer un `with (...)` a la sentencia. Por
  defecto toda acción se ejecuta sobre `self`. Cambiar el ámbito de una acción suelta solo afecta
  a esa acción; para aplicar el cambio a **varias** acciones seguidas se usa la acción especial
  **`Apply To...`**, que abre su propia subcadena y equivale a envolver ese bloque en
  `with (ámbito) { ... }`. Dentro de un bloque `Apply To...`, el ámbito `other` vuelve a apuntar
  a la instancia que llamó al bloque (igual que dentro de un `with`, `other` es quien lo invocó).

### 2.3 · El resto de mecánica del editor

- **Autocompletar**: al escribir en cualquier campo de valor aparecen variables, constantes,
  funciones de GML y nombres de recursos que empiecen igual — funciona exactamente como el
  autocompletado del editor de código de texto.
- **Icono "+"**: amplía una acción para aceptar argumentos opcionales o repetir el bloque con más
  entradas (por ejemplo, `Assign Variable` con el "+" declara varias variables de una vez;
  `Declare a New Function` con el "+" añade más parámetros).
- **Comentarios**: clic derecho → *Comentar* añade una nota junto al bloque; sobrevive a la
  conversión a GML (se convierte en un comentario `//` real).
- **Desactivar/Activar**: pone el bloque en gris y lo salta al compilar, sin borrarlo — es el
  equivalente visual de comentar una línea de GML para probar algo.
- **Alternar punto de interrupción** (`F9` o clic derecho): pone un *breakpoint* real, el mismo
  que usa
  [15 · Depuración y rendimiento §3](./15%20-%20Depuración%20y%20rendimiento.md#3-nivel-2-el-debugger)
  — ver §8.
- **Vista previa en vivo** y **Convertir a GML**: cubiertos enteros en §6.
- **Mostrar ayuda...**: abre el manual en la página de esa acción concreta — el equivalente,
  dentro del IDE, a lo que aquí hace `gm-cli manual read "<acción>"`.

---

## 3. Las familias de acciones: el mapa completo de la caja de herramientas

La caja de herramientas agrupa las acciones en **27 bibliotecas**. Esta tabla es el mapa
completo — para el detalle de cada acción ve directamente a §4, que ya trae el GML.

| Familia | Acciones documentadas | Qué agrupa |
|---|---|---|
| **Common** (Comunes) | 17 | Variables, condicionales (`If`/`Else`), `Execute Code`, llamadas a función, `return`, `Apply To...`, macros, y la declaración de funciones propias. Es la única familia sin la que no se puede hacer nada — el resto son "vocabulario" sobre esta gramática base. |
| **Instance** (Instancia) | 18 | Crear/destruir instancias, alarmas, sprite y transformaciones visuales de la instancia (rotación, escala, alfa, color), eventos de usuario y de padre. |
| **Instance Variables** | 9 | Atajos para `score`, `lives` y `health` — las tres variables integradas de "juego clásico" pensadas para quien empieza. |
| **Movement** (Movimiento) | 13 | Las dos formas de mover algo en GameMaker: por vector (`speed`/`direction`) o por posición directa (`x`/`y`), más gravedad, fricción y rebote de sala. |
| **Collisions** (Colisiones) | 4 | Comprobar solapamiento con un objeto en un punto, una forma (rectángulo/elipse/línea) o "cualquier objeto". |
| **Drawing** (Dibujo) | 23 | Solo funcionan (salvo las `Set_*`) dentro de un evento Draw. Sprites, texto, formas primitivas, barra de salud, y el estado de dibujo (color, alfa, fuente, alineación). |
| **Tiles** (Baldosas) | 12 | Leer y escribir el tilemap de una capa, por celda o por píxel, incluida su transformación (flip/mirror/rotate). |
| **Audio** | 17 | Reproducir, parar, pausar y ajustar volumen/tono de un sonido — el nivel "básico" de audio; lo avanzado (streaming, 3D, buses) no tiene acciones DnD, solo GML. |
| **Loops** (Bucles) | 5 | `Loop` (infinito hasta `Break`), `Repeat` (n veces), `While` (condición), `For` (contador) y `Break`. |
| **Switch** | 3 | `Switch`/`Case`/`Default` — la alternativa a una cadena larga de `If`. |
| **Data Structures** (Estructuras de datos) | 22 | Las **cuatro** estructuras clásicas expuestas en DnD: lista, mapa, rejilla (grid) y pila (stack). Las dos que faltan respecto a GML de texto —cola (queue) y cola de prioridad— no tienen acciones propias. |
| **Data Types** (Tipos de datos) | 3 | Conversión entre decimal/entero y número/string — el mínimo indispensable, sin arrays ni structs (ver §7). |
| **Buffers** | 10 | Crear, copiar, leer y escribir en un buffer de memoria alineado a 1 byte (a diferencia de los buffers de GML de texto, que eligen alineación). |
| **Files** (Archivos) | 10 | Archivos ini (lectura/escritura de secciones y claves) y operaciones genéricas de archivo (renombrar, copiar, borrar, comprobar existencia), más volcar/cargar un buffer a disco. |
| **Random** (Aleatorio) | 3 | Número aleatorio, fijar la semilla, y elegir uno de varios valores. |
| **Cameras** (Cámaras) | 2 | Una sola pareja `Get`/`Set` que cubre **todas** las variables de un viewport (cámara asignada, visibilidad, posición, tamaño, surface) mediante un desplegable — no una acción por variable. |
| **Rooms** (Salas) | 7 | Cambiar de room (por índice, siguiente, anterior, reinicio) y consultar si la room actual es la primera/última. |
| **Paths** (Rutas) | 6 | Seguir un recurso *path* creado en su editor: iniciar, detener, y leer/fijar posición y velocidad a lo largo de la ruta. |
| **Timelines** (Líneas de tiempo) | 4 | Asignar, mover, cambiar de velocidad y arrancar/parar un recurso *timeline* clásico (momentos discretos de juego, distinto de los *Sequences*). |
| **Game** (Juego) | 4 | Reiniciar el juego, salir, y un guardado/carga "de juguete" — ver el ⚠️ de la tabla §4.9. |
| **Miscellaneous** (Varios) | 2 | `Show Debug Message` (la acción de depuración más usada de todas) y `Set Window State` (pantalla completa/ventana). |
| **Particles** (Partículas) | 24 | Sistema → tipo → emisor, las tres piezas de cualquier efecto de partículas. Cubre lo esencial; los efectos "Do Effect" precocinados (explosión, humo, chispas…) no tienen equivalente 1:1 en GML de texto porque son azúcar sintáctico del propio editor. |
| **Sequences** (Secuencias) | 10 | Crear/destruir un elemento de *Sequence* (el sistema moderno de animación por keyframes) en una capa, reproducirlo/pausarlo y leer/fijar su posición y cabezal de reproducción. |
| **Time Sources** (Fuentes de tiempo) | 22 | El temporizador moderno de GameMaker (sustituto recomendado de las alarmas para lógica compleja): crear, encadenar padre/hijo, y consultar su estado — más conversión BPM↔segundos. |
| **Gamepad** | 9 | Ejes, gatillos y botones de mando, con las constantes `gp_*` para las 20 entradas estándar de un mando tipo Xbox/PS. |
| **Mouse and Keyboard** (Ratón y teclado) | 10 | Pulsación de ratón y teclado (`pressed`/`down`/`released`), más el teclado virtual para pantallas táctiles. |
| **Layers** (Capas) | 1 | Solo visibilidad de capa — el resto de manipulación de capas (crear, mover, profundidad) no tiene acciones DnD, solo GML. |

> Nota sobre el manual: su página índice de la Referencia de GML Visual lista "Acciones de la
> instancia" **dos veces** apuntando al mismo enlace de "Acciones comunes" — es un error de la
> propia tabla oficial (verificado leyendo `DnD_Reference.md`), no algo que falte en esta
> biblioteca ni en tu proyecto.

---

## 4. La tabla de equivalencias: acción → GML

Esta es la pieza central del documento. Cada fila es una acción real del manual con su
traducción a GML **verificada símbolo a símbolo** contra `_indice/buscar.py` — nada de esta
tabla es una función inventada. Cuando una acción no tiene una función 1:1 (compone varias
líneas, o no existe función equivalente porque es azúcar del propio editor), se indica.

Convención de la columna GML: `_variable` = variable local (`var`); sin guion bajo = variable de
instancia o global; los nombres de recurso (`obj_x`, `spr_x`, `snd_x`) son ilustrativos.

### 4.1 · Comunes (`Common`)

| Acción (DnD) | Equivalente en GML |
|---|---|
| Assign Variable | `nombre = valor;` — con **Relative** marcado: `nombre += valor;` (o concatena si es string) |
| Declare Temporary Variable | `var _nombre = valor;` |
| Set Global Variable | `global.nombre = valor;` (equivalente por función: `variable_global_set("nombre", valor)`) |
| Get Global Variable | `variable_global_get("nombre")` |
| If Variable | `if (variable == valor) { }` (el operador es un desplegable: `==`, `!=`, `>`, `<`, `>=`, `<=`) |
| If Expression | `if (expresión) { }` |
| If Undefined | `if (is_undefined(variable)) { }` |
| Else | `else { }` (cadena lateral de la acción `If` anterior) |
| Execute Code | GML de texto tal cual, pegado dentro del evento — es el "escape hatch" nativo, ver §5 |
| Execute Script *(legado, no usar en proyectos nuevos)* | `nombre_función(arg0, arg1, ...);` — usar mejor `Function Call` |
| New | `_var = new nombre_función(arg0, arg1);` — la función debe estar marcada **Constructor** |
| Function Call | `_objetivo = nombre_función(arg0, arg1, ...);` — cualquier función de GML o propia |
| Return | `return valor;` |
| Apply To... | `with (objeto_o_id_o_expresión) { }` |
| Macro | `#macro NOMBRE valor` (o `#macro NOMBRE expresión_de_función`, se re-evalúa cada vez) |
| Exit | `exit;` |
| Declare a New Function | `function nombre(_arg0, _arg1 = valor_por_defecto) { }` — con **Constructor** marcado: `function nombre(...) constructor { }`; con **Static**: se comporta como función global de un solo registro; con **Temp**: solo válida dentro del evento actual |

### 4.2 · Instancia (`Instance` + `Instance Variables`)

| Acción (DnD) | Equivalente en GML |
|---|---|
| Create an Object Instance | `_id = instance_create_layer(x, y, "NombreCapa", obj_x);` |
| Destroy Object Instance | `instance_destroy();` (o `instance_destroy(id)` si el ámbito no es `self`) |
| Destroy At Position | `position_destroy(x, y);` |
| Change Object Instance | ⚠️ compila a `instance_change(obj_x, perform_events);`, **marcada obsoleta** en 2026. Prefiere combinar `instance_destroy()` + `instance_create_layer()` (copiando a mano el estado que necesites conservar) |
| Set Alarm | `alarm[n] = pasos;` (con **Relative**: `alarm[n] += pasos;`) |
| Get Alarm | `alarm[n]` |
| Get Instance Count | `instance_number(obj_x)` |
| Call a User Event | `event_user(n);` (n de 0 a 15) |
| Set an Instance Variable | `variable_instance_set(id, "nombre", valor);` |
| Get an Instance Variable | `variable_instance_get(id, "nombre")` |
| Set Sprite | `sprite_index = spr_x; image_index = frame;` |
| Set Instance Rotation | `image_angle = grados;` |
| Set Animation Speed | `image_speed = velocidad;` |
| Set Instance Scale | `image_xscale = x; image_yscale = y;` |
| Set Instance Alpha | `image_alpha = valor;` |
| Set Instance Colour | `image_blend = color;` (constante `c_*` o valor hex `$AARRGGBB`) |
| If Instance Exists | `if (instance_exists(obj_x)) { }` |
| Call Parent Event | `event_inherited();` |
| Set Score | `score = valor;` (variable integrada) |
| Get Score | `score` |
| Set Lives | `lives = valor;` |
| Get Lives | `lives` |
| Set Health | `health = valor;` |
| Get Health | `health` |
| If Score | `if (score == valor) { }` |
| If Lives | `if (lives == valor) { }` |
| If Health | `if (health == valor) { }` |

> `score`, `lives` y `health` son variables integradas "de cortesía" pensadas para prototipos
> rápidos; cualquier proyecto real las sustituye por variables propias (`hp`, `puntos`…) — ver
> [09 · Instancias, objetos y herencia](./09%20-%20Instancias%2C%20objetos%20y%20herencia.md).

### 4.3 · Movimiento (`Movement`)

| Acción (DnD) | Equivalente en GML |
|---|---|
| Set Direction (Fixed) | `direction = grados;` |
| Set Direction (Variable) | `direction = _variable;` |
| Set Point Direction | `direction = point_direction(x1, y1, x2, y2);` |
| Set Direction (Random) | `direction = irandom(359);` (o `choose(...)` entre valores concretos) |
| Set Speed | `speed = valor;` |
| Set Gravity Direction | `gravity_direction = grados;` |
| Set Gravity Force | `gravity = valor;` |
| Reverse (dirección) | `direction += 180;` |
| Reverse (velocidad horizontal/vertical) | `hspeed *= -1;` / `vspeed *= -1;` |
| Reverse (gravedad) | `gravity_direction += 180;` |
| Set Friction | `friction = valor;` |
| Jump to Point | `x = valor_x; y = valor_y;` |
| Jump to Start | `x = xstart; y = ystart;` |
| Snap Position | `x = round(x / horizontal) * horizontal; y = round(y / vertical) * vertical;` — no existe una función `snap_*` única; es la composición de redondeo por celda |
| Wrap Around Room | Sin función 1:1: comprobación manual contra `room_width`/`room_height` con el margen dado, normalmente en el evento *Other → Outside Room* |

### 4.4 · Colisiones (`Collisions`)

| Acción (DnD) | Equivalente en GML |
|---|---|
| If Any Object At Place | `if (place_meeting(x, y, all)) { }` |
| If Object At Place | `if (place_meeting(x, y, obj_x)) { }` — con **Return list** marcado, la lista completa se obtiene con `collision_rectangle(...)`/`collision_point(...)` sobre una máscara puntual, no con `place_meeting` |
| If Collision Shape | `collision_rectangle(x1, y1, x2, y2, obj_x, prec, notme)` / `collision_ellipse(...)` / `collision_line(x1, y1, x2, y2, obj_x, prec, notme)` según la forma elegida |
| If Collision Point | `collision_point(x, y, obj_x, prec, notme)` |

### 4.5 · Dibujo (`Drawing`) — solo válidas en un evento Draw (salvo las `Set_*`)

| Acción (DnD) | Equivalente en GML |
|---|---|
| Draw Self | `draw_self();` |
| Draw Value | `draw_text(x, y, string(valor));` |
| Draw Transformed Value | `draw_text_transformed(x, y, string(valor), xscale, yscale, angle);` |
| Draw Sprite | `draw_sprite(spr_x, subimg, x, y);` |
| Draw Sprite Transformed | `draw_sprite_ext(spr_x, subimg, x, y, xscale, yscale, rot, colour, alpha);` |
| Draw Stacked Sprites | Sin función 1:1: bucle `for` que llama a `draw_sprite_ext()` una vez por elemento apilado |
| Draw Rectangle | `draw_rectangle(x1, y1, x2, y2, outline);` |
| Draw Gradient Rectangle | `draw_rectangle_colour(x1, y1, x2, y2, col1, col2, col3, col4, outline);` |
| Draw Ellipse | `draw_ellipse(x1, y1, x2, y2, outline);` |
| Draw Gradient Ellipse | `draw_ellipse_colour(x1, y1, x2, y2, col1, col2, outline);` |
| Draw Line | `draw_line(x1, y1, x2, y2);` |
| Draw Healthbar | `draw_healthbar(x1, y1, x2, y2, amount, backcol, mincol, maxcol, direction, showback, showborder);` |
| Draw Instance Score / Health / Lives | Sin función 1:1: `draw_text(x, y, string(score));` (o `lives`/`health`) — son azúcar del editor sobre `draw_text` + la variable integrada correspondiente |
| Set Draw Colour | `draw_set_colour(col);` |
| Get Draw Colour | `draw_get_colour()` |
| Set Draw Alpha | `draw_set_alpha(alpha);` |
| Get Draw Alpha | `draw_get_alpha()` |
| Set Font | `draw_set_font(fnt_x);` |
| Get Draw Font | `draw_get_font()` |
| Set Text Alignment | `draw_set_halign(halign); draw_set_valign(valign);` |
| Get Text Alignment | `draw_get_halign()` / `draw_get_valign()` |

### 4.6 · Salas y cámaras (`Rooms` + `Cameras`)

| Acción (DnD) | Equivalente en GML |
|---|---|
| Go To Room | `room_goto(rm_x);` |
| Go To Next Room | `room_goto_next();` |
| Go To Previous Room | `room_goto_previous();` |
| Restart Room | `room_restart();` |
| If Room Is First | `if (room == room_first) { }` |
| If Room Is Last | `if (room == room_last) { }` |
| Get Current Room | `room` |
| Set View Variable | Según el desplegable: `view_set_camera(view, cam)`, `view_set_visible(view, bool)`, `view_set_xport(view, x)`, `view_set_yport(view, y)`, `view_set_wport(view, w)`, `view_set_hport(view, h)` o `view_set_surface_id(view, surf)` |
| Get View Variable | Los mismos siete, en `view_get_*` |

> El desplegable "Variable" de `Set/Get View Variable` es **una acción que cubre siete
> funciones distintas** — es la única familia de DnD donde una sola acción se ramifica así; el
> resto de familias tienen una acción por función.

### 4.7 · Estructuras y tipos de datos (`Data Structures` + `Data Types`)

| Acción (DnD) | Equivalente en GML |
|---|---|
| Create List / Map / Grid / Stack | `_id = ds_list_create();` / `ds_map_create()` / `ds_grid_create(w, h)` / `ds_stack_create()` |
| Clear Data Structure | `ds_list_clear(id)` / `ds_map_clear(id)` / `ds_grid_clear(id, val)` / `ds_stack_clear(id)` (según el tipo) |
| Free Data Structure | `ds_list_destroy(id)` / `ds_map_destroy(id)` / `ds_grid_destroy(id)` / `ds_stack_destroy(id)` |
| Add To List | `ds_list_add(id, valor);` |
| Remove From List | `ds_list_delete(id, ds_list_find_index(id, valor));` |
| Get List Item At | `ds_list_find_value(id, pos)` |
| Get Index of List Item | `ds_list_find_index(id, valor)` |
| Insert Into List | `ds_list_insert(id, pos, valor);` |
| Get List Item Count | `ds_list_size(id)` |
| Set Map Value | `ds_map_add(id, clave, valor);` o `ds_map_replace(id, clave, valor);` si la clave ya existe |
| Get Map Value | `ds_map_find_value(id, clave)` |
| Remove Map Entry | `ds_map_delete(id, clave);` |
| Set Grid Value | `ds_grid_set(id, x, y, valor);` |
| Get Grid Value | `ds_grid_get(id, x, y)` |
| Clear Grid | `ds_grid_clear(id, valor);` |
| Push Onto Stack | `ds_stack_push(id, valor);` |
| Pop Stack | `ds_stack_pop(id)` |
| If Data Structure Exists | `if (ds_exists(id, ds_type_list)) { }` (la constante `ds_type_*` cambia según el tipo elegido) |
| If Data Structure Empty | `ds_list_empty(id)` / `ds_map_empty(id)` / `ds_stack_empty(id)` según el tipo (no existe versión para grid) |
| Decimal to Integer | `floor(valor)` (o `int64(valor)` si necesitas el tipo entero de 64 bits explícito) |
| String to Number | `real(cadena)` |
| Number to String | `string(número)` |

### 4.8 · Archivos y buffers (`Files` + `Buffers`)

| Acción (DnD) | Equivalente en GML |
|---|---|
| Load Buffer | `_buf = buffer_load(nombre_archivo);` |
| Save Buffer | `buffer_save(buf, nombre_archivo);` |
| Rename File | `file_rename(viejo, nuevo);` |
| Copy File | `file_copy(origen, destino);` |
| Delete File | `file_delete(nombre);` |
| Open Ini File | `ini_open(nombre);` |
| Close Ini File | `ini_close();` |
| Write To Ini File | `ini_write_string(sección, clave, valor);` / `ini_write_real(sección, clave, valor);` según el tipo |
| Read Ini File | `ini_read_string(sección, clave, por_defecto)` / `ini_read_real(sección, clave, por_defecto)` |
| If File Exists | `if (file_exists(nombre)) { }` |
| Create a Buffer | `_buf = buffer_create(tamaño, buffer_grow, 1);` (DnD siempre alinea a 1 byte) |
| Copy Buffer | `buffer_copy(origen, offset_origen, tamaño, destino, offset_destino);` |
| Delete Buffer | `buffer_delete(buf);` |
| Read Buffer | `buffer_read(buf, buffer_string);` (el tipo de dato es el desplegable de la acción) |
| Write Buffer | `buffer_write(buf, buffer_string, valor);` |
| Seek Buffer | `buffer_seek(buf, buffer_seek_start, posición);` |
| Get Buffer Size | `buffer_get_size(buf)` |
| Get Buffer Position | `buffer_tell(buf)` |
| If Buffer Exists | `if (buffer_exists(buf)) { }` |
| If End of Buffer | Sin función 1:1: `buffer_tell(buf) >= buffer_get_size(buf)` |

### 4.9 · Audio (`Audio`) y Juego (`Game`)

| Acción (DnD) | Equivalente en GML |
|---|---|
| Play Audio | `_voz = audio_play_sound(snd_x, prioridad, loop);` |
| Stop Audio | `audio_stop_sound(snd_x);` |
| Stop All Audio | `audio_stop_all();` |
| Pause Audio | `audio_pause_sound(snd_x);` |
| Pause All Audio | `audio_pause_all();` |
| Resume Audio | `audio_resume_sound(snd_x);` |
| Resume All Audio | `audio_resume_all();` |
| Set Audio Position | `audio_sound_set_track_position(snd_x, segundos);` |
| Get Audio Length | `audio_sound_length(snd_x)` |
| Set Audio Pitch | `audio_sound_pitch(snd_x, valor);` |
| Get Audio Pitch | `audio_sound_get_pitch(snd_x)` |
| Set Audio Volume | `audio_sound_gain(snd_x, valor, tiempo_ms);` |
| Get Audio Volume | `audio_sound_get_gain(snd_x)` |
| Set Master Volume | `audio_master_gain(valor);` |
| Get Master Volume | Sin función de lectura directa en GML moderno; el propio manual de audio recomienda llevar el valor en una variable propia |
| If Audio Is Playing | `if (audio_is_playing(snd_x)) { }` |
| If Audio Is Paused | `if (audio_is_paused(snd_x)) { }` |
| Restart Game | `game_restart();` |
| End Game | `game_end();` |
| Save Game | ⚠️ compila a `game_save(archivo)`, **marcada obsoleta**. El propio manual recomienda no usarla: no guarda estructuras de datos ni recursos dinámicos y puede dejar de ser compatible entre versiones del runtime. Sistema real en [14 · Persistencia y archivos](./14%20-%20Persistencia%20y%20archivos.md) |
| Load Game | ⚠️ compila a `game_load(archivo)`, la misma obsolescencia que `Save Game` |

Lo avanzado de audio —streaming, posicionamiento 3D, buses y grupos— **no tiene acciones DnD**;
solo existe como función de GML. Detalle en
[13 · Audio](./13%20-%20Audio.md) y
[08/24 · Audio avanzado](../08%20-%20Referencia%20GML%20completa/24%20-%20Audio%20avanzado%20-%20buffers%2C%20colas%2C%20sincron%C3%ADa%20y%20grabaci%C3%B3n.md).

### 4.10 · Input: teclado, ratón y gamepad

| Acción (DnD) | Equivalente en GML |
|---|---|
| If Mouse Pressed | `if (mouse_check_button_pressed(mb_left)) { }` |
| If Mouse Down | `if (mouse_check_button(mb_left)) { }` |
| If Mouse Released | `if (mouse_check_button_released(mb_left)) { }` |
| If Key Pressed | `if (keyboard_check_pressed(vk_space)) { }` |
| If Key Down | `if (keyboard_check(vk_left)) { }` |
| If Key Released | `if (keyboard_check_released(vk_up)) { }` |
| Show Virtual Keyboard | `keyboard_virtual_show(kbv_type_default, kbv_returnkey_default, kbv_autocapitalize_none, false);` |
| Hide Virtual Keyboard | `keyboard_virtual_hide();` |
| Get Virtual Keyboard Height | `keyboard_virtual_height()` |
| If Virtual Keyboard Is Showing | `if (keyboard_virtual_status()) { }` |
| Get Gamepad Axis | `gamepad_axis_value(device, gp_axislh);` (u otro eje `gp_axis*`) |
| Get Gamepad Trigger | `gamepad_button_value(device, gp_shoulderlb);` (el gatillo también se lee como botón analógico) |
| Get Gamepad Count | `gamepad_get_device_count()` |
| Is Gamepad Connected | `gamepad_is_connected(device)` |
| Set Gamepad Axis Deadzone | `gamepad_set_axis_deadzone(device, valor);` |
| Set Gamepad Button Threshold | `gamepad_set_button_threshold(device, valor);` |
| If Gamepad Button Pressed | `if (gamepad_button_check_pressed(device, gp_face1)) { }` |
| If Gamepad Button Down | `if (gamepad_button_check(device, gp_face1)) { }` |
| If Gamepad Button Released | `if (gamepad_button_check_released(device, gp_face1)) { }` |

Detalle completo de zonas muertas, umbrales y mapeo de mandos no estándar en
[12 · Input — teclado, ratón y gamepad](./12%20-%20Input%20-%20teclado%2C%20ratón%20y%20gamepad.md).

### 4.11 · Aleatorio, bucles y control de flujo

| Acción (DnD) | Equivalente en GML |
|---|---|
| Get Random Number | `random(n)` (con **Integer** marcado: `irandom(n)`) |
| Randomise | `randomize();` |
| Choose | `choose(valor1, valor2, ...)` |
| Loop | `while (true) { /* … */ if (condición) { break; } }` — bucle infinito hasta un `Break` interno |
| Repeat | `repeat (n) { }` |
| While | `while (variable comparador valor) { }` |
| For | `for (_i = inicio; condición; _i += incremento) { }` |
| Break | `break;` |
| Switch | `switch (valor) { }` |
| Case | `case constante: { /* … */ } break;` |
| Default *(dentro de un Switch)* | `default: { }` |

### 4.12 · Partículas (`Particles`)

| Acción (DnD) | Equivalente en GML |
|---|---|
| Create Particle System | `_ps = part_system_create();` (o `part_system_create_layer(capa, persistente)` para anclarlo a una capa) |
| Destroy Particle System | `part_system_destroy(ps);` |
| Clear Particle System | `part_system_clear(ps);` |
| Pause Particle System | `part_system_automatic_update(ps, false);` — no hay una función "pause" dedicada; se corta la actualización automática |
| Update Particle System | `part_system_update(ps);` |
| Create Particle Type | `_pt = part_type_create();` |
| Destroy Particle Type | `part_type_destroy(pt);` |
| Set Particle Sprite | `part_type_sprite(pt, spr_x, animate, stretch, random);` |
| Set Particle Size | `part_type_size(pt, size_min, size_max, size_incr, size_wiggle);` |
| Set Particle Colour | `part_type_colour1(pt, color);` (o `part_type_colour2/3` con varias paradas) |
| Set Particle Alpha | `part_type_alpha1(pt, alpha);` (o `part_type_alpha2/3`) |
| Set Particle Life | `part_type_life(pt, life_min, life_max);` |
| Set Particle Speed | `part_type_speed(pt, speed_min, speed_max, speed_incr, speed_wiggle);` |
| Set Particle Direction | `part_type_direction(pt, dir_min, dir_max, dir_incr, dir_wiggle);` |
| Set Particle Orientation | `part_type_orientation(pt, ang_min, ang_max, ang_incr, ang_wiggle, relative);` |
| Set Particle Gravity | `part_type_gravity(pt, cantidad, dirección);` |
| Burst Particles | `part_particles_burst(pt, x, y, ps);` |
| Create Particle Emitter | `_em = part_emitter_create(ps);` |
| Destroy Particle Emitter | `part_emitter_destroy(ps, em);` |
| Emit Particles | `part_emitter_stream(ps, em, pt, número);` (ráfaga puntual: `part_emitter_burst(ps, em, pt, número)`) |
| Set Emitter Region | `part_emitter_region(ps, em, xmin, xmax, ymin, ymax, shape, distribution);` |
| Do Effect | Sin función 1:1: `Do Effect` es azúcar del editor que arma internamente un tipo y un emisor efímeros para un catálogo cerrado de efectos precocinados (explosión, humo, chispas…) — para reproducir uno igual en GML de texto hay que construirlo a mano con `part_type_*`/`part_emitter_*`, no existe un `part_effect_create()` |

Guía completa de partículas (capas, presupuesto, patrones) en
[04/39 · VFX: diseño y catálogo de efectos](../04%20-%20Recetas%20por%20género/39%20-%20VFX%20-%20dise%C3%B1o%20y%20cat%C3%A1logo%20de%20efectos.md).

### 4.13 · Baldosas, capas y secuencias (`Tiles` + `Layers` + `Sequences`)

| Acción (DnD) | Equivalente en GML |
|---|---|
| Set Tile Index at Pixel | `tilemap_set_at_pixel(tilemap, tiledata, x, y);` |
| Get Tile Index at Pixel | `tilemap_get_at_pixel(tilemap, x, y)` |
| Set Tile Index in Cell | `tilemap_set(tilemap, tiledata, cellx, celly);` |
| Get Tile Index in Cell | `tilemap_get(tilemap, cellx, celly)` |
| Set Layer Visibility | `layer_set_visible(layer_id, bool);` |
| Create Sequence Element | `_elem = layer_sequence_create(layer_id, x, y, seq_x);` |
| Destroy Sequence Element | `layer_sequence_destroy(elem);` |
| Play Sequence | `layer_sequence_play(elem);` |
| Pause Sequence | `layer_sequence_pause(elem);` |
| If Sequence Exists | `if (layer_sequence_exists(layer_id, elem)) { }` |
| Get Sequence Length | `layer_sequence_get_length(elem)` |
| Get/Set Sequence Position (x/y del elemento) | `layer_sequence_get_x(elem)` / `layer_sequence_x(elem, x);` (mismo patrón para `_y`) |
| Get/Set Sequence Head (cabezal de reproducción) | `layer_sequence_get_headpos(elem)` / `layer_sequence_headpos(elem, posición);` |

> El `tilemap` de estas acciones se obtiene con `layer_tilemap_get_id(layer_id)` — el propio
> manual de DnD asume que ya tienes el ID a mano (viene precargado como variable de la capa en
> el editor de rooms). El `Get`/`Set Tile Set` de la biblioteca cambia qué *tileset* usa un
> tilemap entero, no una celda.

### 4.14 · Timelines, fuentes de tiempo y paths

| Acción (DnD) | Equivalente en GML |
|---|---|
| Set Instance Timeline | `timeline_index = tml_x;` |
| Set Timeline Moment | `timeline_position = momento;` |
| Set Timeline Speed | `timeline_speed = velocidad;` |
| Set Timeline State | `timeline_running = bool;` (o `timeline_loop = bool;` según la opción elegida) |
| Create Time Source | `_ts = time_source_create(time_source_global, periodo, time_source_units_seconds, callback);` |
| Destroy Time Source | `time_source_destroy(ts);` |
| Start/Stop/Pause/Resume Time Source | `time_source_start(ts);` / `time_source_stop(ts);` / `time_source_pause(ts);` / `time_source_resume(ts);` |
| Reconfigure Time Source | `time_source_reconfigure(ts, periodo, unidades, callback, args, repeticiones, tipo_caducidad);` |
| Get Time Remaining / Get Period | `time_source_get_time_remaining(ts)` / `time_source_get_period(ts)` |
| If Time Source Exists | `if (time_source_exists(ts)) { }` |
| Seconds to BPM / BPM to Seconds | `seconds_to_bpm(segundos)` / `bpm_to_seconds(bpm)` |
| Start Following Path | `path_start(path_x, velocidad, path_action_stop, absolute);` |
| Stop Following Path | `path_end();` |
| Set/Get Position Along Path | `path_position = valor;` / `path_position` |
| Set/Get Path Follow Speed | `path_speed = valor;` / `path_speed` |

Las *fuentes de tiempo* son el reemplazo moderno recomendado de las alarmas para lógica de
temporización compleja (anidamiento padre/hijo, pausa global). Las *timelines* clásicas son un
sistema anterior y más simple, distinto de los recursos *Sequence* del §4.13 — no lo confundas
por el nombre parecido.

---

## 5. Cómo conviven GML Visual y GML Code en el mismo proyecto

GameMaker no obliga a elegir un lenguaje para todo el proyecto. **El lenguaje se fija por
evento**, no por objeto ni por proyecto: un objeto puede tener su evento Create en GML Visual y
su evento Step en GML de texto sin ningún problema, porque ambos compilan al mismo bytecode/VM.
El desplegable de idioma está en la esquina de cada pestaña de evento en el Code Editor 2 (ya
mencionado en
[02 · Novedades 2026 §09](../02%20-%20Novedades%202026/09%20-%20Code%20Editor%202%20y%20Feather.md)).

Dos puentes explícitos entre ambos mundos, ya vistos en la tabla:

- **`Execute Code`** (familia Common): un bloque de GML de texto **dentro** de un evento en modo
  Visual. Es la salida de emergencia natural para cualquier cosa que no tenga acción dedicada
  (arrays, structs, shaders, física, cualquier función sin acción — ver §7).
- **`New`** y **`Declare a New Function`**: los *scripts* de GML Visual son, por dentro, ficheros
  de GML de texto con funciones definidas — cualquier función que declares ahí (marcada
  `Constructor` o no) es llamable exactamente igual desde un evento en GML de texto, y viceversa.
  No hay una "función de DnD" distinta de una función de GML: es la misma función, solo que la
  *definiste* arrastrando bloques.

Esto significa que un proyecto DnD nunca es una caja negra: siempre puedes bajar un nivel con
`Execute Code` para lo que el árbol de acciones no cubre, sin tener que convertir el evento
entero. Detalle de cómo se declaran funciones y su ámbito en
[07 · Funciones, métodos y ámbito](./07%20-%20Funciones%2C%20métodos%20y%20ámbito.md).

---

## 6. Convertir un proyecto de DnD a GML: `Convert to GML`

El camino recomendado por el propio manual, en dos pasos:

1. **Vista previa en vivo** (clic derecho en el workspace → *Vista previa en vivo*). Abre una
   ventana que muestra el GML "de verdad" que hay detrás de las acciones **en tiempo real**, a
   medida que añades/quitas/cambias bloques. Es de solo lectura: puedes copiar fragmentos de ahí
   y pegarlos en un script o en una acción `Execute Code`, pero no puedes editarla directamente.
   Es la forma más segura de comprobar una fila de la tabla del §4 sin comprometerte a nada.
2. **Convertir a código GML** (clic derecho en cualquier evento con acciones → *Convertir a
   código GML*). La primera vez avisa de que es una conversión **de un solo sentido**: pasa las
   acciones a código, pero **no** se puede deshacer acción por acción después. El código
   resultante usa `{}` para delimitar lo que era cada bloque de acción, y crea variables locales
   temporales extra donde antes había un valor de retorno intermedio (el manual pone el ejemplo
   de un `If Instance Exists` seguido de otra acción: el GML generado primero declara `var _val =
   false;`, luego `if (instance_exists(...)) { _val = ...; }`, y por último comprueba `_val`).

### El camino de vuelta (parcial)

Sí existe un "Convertir a GML Visual" desde el menú del editor de código, pero **no** reconstruye
las acciones originales: envuelve **todo** el código de ese evento en una única acción `Execute
Code`. Es útil para poder seguir editando el evento desde el workspace visual (por ejemplo, para
encadenarle acciones DnD después), pero no deshace la conversión — el código dentro de ese
`Execute Code` sigue siendo texto.

### Migración incremental de un proyecto DnD a GML

Para un proyecto real (no solo un evento suelto), conviene ir **objeto por objeto y evento por
evento**, no todo de golpe:

1. Empieza por el objeto con **menos** eventos y acciones — sirve para practicar el patrón antes
   de tocar algo crítico (normalmente el jugador o el controlador de nivel).
2. Antes de convertir, abre **Vista previa en vivo** y lee el GML generado con calma: es la
   oportunidad de detectar nombres de variable poco claros (`_val`, `_val2`…) que conviene
   renombrar a algo con sentido nada más convertir, porque después de convertir ya son texto
   normal y nadie te avisa de que "antes eran el retorno de tal acción".
3. Convierte el evento, aplica las convenciones de
   [05 · Convenciones y estilo GML](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md)
   (`snake_case`, variables locales con `_`) y renombra las variables generadas automáticamente.
4. Compila y prueba **ese objeto solo** antes de seguir con el siguiente — `gm-cli compile` o
   `F5` sobre una room de prueba. La conversión no debería cambiar el comportamiento (es la misma
   VM ejecutando lo mismo), pero un renombrado a mano sí puede introducir un error de tecleo.
5. Repite objeto por objeto. No hace falta terminar el proyecto entero de una sentada — GML
   Visual y GML de texto conviven sin problema mientras dura la migración (§5).

---

## 7. Limitaciones reales de GML Visual

Esto **no** es una opinión: es lo que se deduce de comparar las 27 familias de acciones del §3
contra las funciones de GML Visual del §4 que **no tienen** familia — y de leer los avisos
explícitos del propio manual.

- **No hay categoría de Arrays ni de Structs.** El único gesto DnD hacia los structs modernos es
  `New` + `Declare a New Function` marcada `Constructor` (§4.1) — todo lo demás (crear un array
  literal, `array_push`, recorrer con `array_length`, leer un campo de struct con `.`) no tiene
  acción propia. Es coherente con la fecha: las acciones DnD documentadas en el manual son
  anteriores a los arrays dinámicos y los structs modernos de GML 2.3+ (2020) y nunca se
  ampliaron para cubrirlos — la vía es `Execute Code`. Ver
  [04 · Structs y constructores](./04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md)
  y [05 · Arrays y estructuras de datos §0](./05%20-%20Arrays%20y%20estructuras%20de%20datos.md#0-la-recomendación-oficial-primero)
  — que además recomienda arrays/structs **por encima** de las `ds_*` que sí tiene DnD en el
  §4.7.
- **No hay categoría de Shaders ni de Surfaces.** Cualquier post-procesado, superficie propia o
  shader GLSL/HLSL exige `Execute Code` o convertir el evento entero. Ver
  [08/23 · Recetario de shaders de efecto](../08%20-%20Referencia%20GML%20completa/23%20-%20Recetario%20de%20shaders%20de%20efecto.md).
- **No hay categoría de Physics (Box2D).** Nada de `physics_fixture_*`, `physics_apply_force`,
  juntas ni sensores. Ver
  [08 · Movimiento y colisiones §"Físicas con Box2D"](./08%20-%20Movimiento%20y%20colisiones.md).
- **No hay categoría de red (networking).** `network_*`, sockets y HTTP asíncrono no tienen
  acción — un juego multijugador en DnD puro no es viable más allá de `Execute Code`.
- **No hay categoría de matrices / vertex buffers / 3D.** Todo lo de
  [11 · Dibujo y renderizado](./11%20-%20Dibujo%20y%20renderizado.md) que toca `matrix_*` o
  `vertex_*` queda fuera.
- **Dos estructuras de datos "clásicas" tampoco están**: colas (`ds_queue_*`) y colas de
  prioridad (`ds_priority_*`) no tienen acciones DnD, solo lista/mapa/rejilla/pila (§4.7).
- **El audio avanzado tampoco**: streaming, posicionamiento 3D, buses y grupos de audio son solo
  GML (§4.9).
- **Algunas acciones compilan a funciones obsoletas.** `Change Object Instance` → `instance_
  change()` y `Save/Load Game` → `game_save()`/`game_load()` siguen en la caja de herramientas
  por compatibilidad hacia atrás, pero el propio manual desaconseja las tres — el DnD no te
  protege de usar API obsoleta, solo la esconde detrás de un bloque bonito.
- **El control de versiones es más difícil.** Un evento DnD vive serializado dentro del `.yy`
  del objeto (parecido a JSON pero no pensado para diff humano). Dos personas editando el mismo
  evento en DnD generan conflictos de Git mucho más difíciles de resolver a mano que dos líneas
  de texto — es la razón práctica, más allá de la elegancia, de la regla de `AGENTS.md` de nunca
  tocar un `.yy` a mano: para un evento DnD, literalmente no hay otra forma soportada de
  editarlo que el IDE o el MCP `gamemaker-resource-tool`.
- **Sigues escribiendo expresiones de texto.** Los campos de valor de casi cualquier acción
  aceptan (y muchas veces *necesitan*) una expresión GML tecleada — `random(10)`,
  `obj_jugador.hp`, `string(_var) + "px"`. GML Visual reduce cuánto tecleas, no lo elimina; por
  eso el manual insiste en que "sigues programando, solo que de forma visual" (§1).

---

## 8. Depuración de DnD

Como GML Visual compila a la misma VM que el GML de texto, **el depurador es literalmente el
mismo** — ver
[15 · Depuración y rendimiento §3](./15%20-%20Depuración%20y%20rendimiento.md#3-nivel-2-el-debugger)
para el detalle completo de la herramienta. Lo específico de DnD:

- **Breakpoints sobre un bloque de acción**: clic derecho sobre la acción → *Alternar punto de
  interrupción*, o seleccionarla y pulsar `F9` — exactamente el mismo atajo que sobre una línea
  del editor de código de texto. El bloque se resalta cuando tiene un breakpoint activo, y el
  juego se detiene ahí al ejecutar en modo depuración.
- **`Show Debug Message`** (familia Miscellaneous, §4) es la acción de depuración más usada:
  compila a `show_debug_message(string)` y escribe en la ventana de salida — el equivalente
  visual de un `print` de toda la vida. También genera un punto en la **Vista del gráfico** del
  depurador (junto con `debug_event()`).
- **Desactivar en vez de borrar**: clic derecho → *Desactivar* pone el bloque en gris sin
  eliminarlo — más rápido que comentar/descomentar código de texto para aislar qué acción está
  causando un problema, porque no hay que recordar la sintaxis exacta que había.
- **Vista previa en vivo** (§6) también sirve como herramienta de depuración por sí sola: si el
  comportamiento no es el esperado y sospechas que has entendido mal una acción, mirar el GML
  real que genera aclara la duda antes de tocar nada.
- **Relojes (Watches) y pila de llamadas** funcionan igual que en un proyecto de texto puro: la
  Vista de Recursos del depurador te deja abrir cualquier evento DnD por doble clic para poner
  breakpoints o revisar valores, exactamente como abrirías un script.

---

## 9. Cuándo dar el salto a GML

No hay una regla de "a partir de X líneas". Señales prácticas, de más a menos evidentes:

1. **En cuanto necesites algo del §7** (un array, un struct, un shader, física, red) — en ese
   momento ya estás escribiendo GML dentro de un `Execute Code`, así que la pregunta real es si
   sigue mereciendo la pena mantener el resto del evento en bloques visuales o convertir todo el
   evento de una vez.
2. **En cuanto trabajes en equipo con control de versiones.** El coste de Git de un `.yy` con
   eventos DnD (§7) crece con el número de personas tocando el mismo objeto.
3. **En cuanto el árbol de un evento no quepa en una pantalla sin hacer scroll.** Es la señal
   visual de que la lógica ya pesa más de lo que el formato de bloques comunica bien; en texto,
   la misma lógica se lee de arriba abajo sin depender del zoom del workspace.
4. **En cuanto quieras copiar el mismo patrón de lógica en varios objetos.** En GML de texto eso
   es una función en un script (`07 · Funciones, métodos y ámbito`); en DnD, sin usar `Declare a
   New Function`, tiende a copiarse el árbol de acciones entero de un objeto a otro.
5. **Si ya sabes programar en otro lenguaje** (Python, JavaScript, C#…), probablemente no ganas
   nada empezando en DnD — el coste de aprender la sintaxis de GML es bajo comparado con el de
   aprender la mecánica del editor visual, y el resto de esta biblioteca (04, 05, 08, 13…) está
   escrita en GML de texto directamente.

Ninguna señal exige convertir **todo** de golpe: §5 y §6 ya cubren cómo conviven ambos lenguajes
y cómo migrar evento por evento sin parar el proyecto. Para seguir aprendiendo GML de texto desde
cero, la progresión completa —incluida la prueba de nivel para saber si ya la superaste— está en
[RUTA.md, Nivel 0 → 1 · Aprendiz](../RUTA.md#nivel-0--1--aprendiz), que ya recomienda
[01 · El IDE y el flujo de trabajo](./01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md) y
[02 · Tipos de datos y variables](./02%20-%20Tipos%20de%20datos%20y%20variables.md) como segundo
y cuarto paso del itinerario, justo después de instalar GameMaker.

---

## 10. Checklist

- [ ] Sé distinguir una cadena **debajo** (secuencia) de una cadena **al lado** (cuerpo de un
      `if`/bucle/`switch`/`Apply To...`) con solo mirar el árbol.
- [ ] Sé cuándo una variable objetivo con **Temp** marcado equivale a `var` y cuándo no.
- [ ] Sé traducir las ~20 acciones más comunes (§4.1-4.3) a GML sin mirar la tabla.
- [ ] Sé que `Change Object Instance`, `Save Game` y `Load Game` compilan a funciones obsoletas
      y conozco la alternativa recomendada para cada una.
- [ ] Sé qué seis cosas **no** tiene GML Visual (arrays, structs, shaders, physics, red,
      matrices/3D) y que la vía de escape siempre es `Execute Code`.
- [ ] Sé usar **Vista previa en vivo** antes de **Convertir a código GML**, y sé que la
      conversión es de un solo sentido.
- [ ] Sé poner y quitar un breakpoint sobre un bloque de acción (`F9` o clic derecho).
- [ ] Si me llega un proyecto DnD ajeno para editar, sé que no puedo tocar el `.yy` a mano y uso
      el IDE o `gm-cli resourcetool eval` para lo que no cubra `Execute Code`.

---

## 11. Errores típicos y cómo evitarlos

| Error | Por qué pasa | Cómo evitarlo |
|---|---|---|
| "Añado una acción dentro de un `If` y no hace nada" | La soltaste **debajo** del `If` en vez de **al lado** — quedó en la secuencia principal, no en su cuerpo | Suelta la acción justo a la derecha del bloque `If`/bucle/`Switch`, donde el workspace resalta el hueco válido (§2.1) |
| "Mi variable temporal desaparece en el siguiente evento" | Las variables con **Temp** marcado son locales (`var`): mueren al terminar el evento, igual que en texto | Si necesitas el valor en otro evento, no marques Temp (variable de instancia) o guárdalo en una `global.` |
| "Cambié el ámbito de una acción y las siguientes no se enteraron" | El ámbito de una acción suelta **no se propaga** a las de abajo — solo afecta a esa acción | Usa `Apply To...` cuando necesites que **varias** acciones seguidas compartan ámbito (§2.2) |
| "Convertí el evento a GML y ahora hay variables raras como `_val2`" | Son las variables temporales que el conversor crea automáticamente para valores de retorno intermedios | Renómbralas nada más convertir, mientras aún recuerdas qué acción las generó (§6, paso de migración 2) |
| "Mi save/load no sobrevive a la siguiente actualización del juego" | `Save Game`/`Load Game` compilan a `game_save()`/`game_load()`, obsoletas y sin garantía de compatibilidad entre versiones del runtime | Sistema de guardado propio con archivos/JSON: [14 · Persistencia y archivos](./14%20-%20Persistencia%20y%20archivos.md) |
| "No encuentro la acción para arrays/structs/shaders" | Esas cuatro familias no existen en DnD (§7) | Usa `Execute Code` para ese fragmento; no hace falta convertir el evento entero |
| "Edité el `.yy` para arreglar un evento DnD a mano y ahora el proyecto no abre" | El formato de un evento DnD dentro del `.yy` es interno del IDE y frágil a cambios manuales | Nunca lo edites a mano — usa el IDE, el MCP `gamemaker-resource-tool` o `gm-cli resourcetool eval` |
| "`Change Object Instance` funciona pero Feather avisa" | Compila a `instance_change()`, marcada obsoleta | Sustituye por `instance_destroy()` + `instance_create_layer()` si escribes el evento de nuevo |

---

## Ver también

- [01 · El IDE y el flujo de trabajo](./01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md) —
  el Code Editor 2, el Asset Browser y el resto del entorno donde vive GML Visual.
- [02 · Tipos de datos y variables](./02%20-%20Tipos%20de%20datos%20y%20variables.md) — el ámbito
  de variables que la casilla **Temp** solo esconde detrás de una casilla.
- [04 · Structs y constructores (POO en GML)](./04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md)
  y [05 · Arrays y estructuras de datos](./05%20-%20Arrays%20y%20estructuras%20de%20datos.md) —
  lo que el §7 dice que DnD no cubre.
- [07 · Funciones, métodos y ámbito](./07%20-%20Funciones%2C%20métodos%20y%20ámbito.md) — el
  detalle de `function`/`constructor`/`static` que hay detrás de `Declare a New Function`.
- [14 · Persistencia y archivos](./14%20-%20Persistencia%20y%20archivos.md) — el sistema de
  guardado real que sustituye a `Save Game`/`Load Game`.
- [15 · Depuración y rendimiento](./15%20-%20Depuración%20y%20rendimiento.md) — el depurador
  completo detrás del §8.
- [05 - Referencia/04 · Convenciones y estilo GML](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md)
  — el estilo a aplicar nada más convertir un evento.
- [RUTA.md — Nivel 0 → 1 · Aprendiz](../RUTA.md#nivel-0--1--aprendiz) — dónde encaja este
  documento en la progresión completa de la biblioteca.

## Fuentes

- Manual oficial de GameMaker, espejo español (`09 - Manual oficial/manual-lts-2026-es/`),
  descargado el 1 de septiembre de 2026, consultado el 2026-09-06:
  - [Resumen de GML Visual](../09%20-%20Manual%20oficial/manual-lts-2026-es/Drag_And_Drop/Drag_And_Drop_Overview/DnD_Overview.md)
  - [Construcción de código de bloque de acción](../09%20-%20Manual%20oficial/manual-lts-2026-es/Drag_And_Drop/Drag_And_Drop_Overview/Constructing_Action_Block_Code.md)
  - [Aplicación de acciones a otras instancias](../09%20-%20Manual%20oficial/manual-lts-2026-es/Drag_And_Drop/Drag_And_Drop_Overview/Applying_Actions_To_Other_Instances.md)
  - [Funciones de script del bloque de acción](../09%20-%20Manual%20oficial/manual-lts-2026-es/Drag_And_Drop/Drag_And_Drop_Overview/Action_Block_Functions.md)
  - [Cambiando GML Visual to Code](../09%20-%20Manual%20oficial/manual-lts-2026-es/Drag_And_Drop/Drag_And_Drop_Overview/Changing_DnD_To_Code.md)
  - [Opciones del menú del botón derecho del ratón](../09%20-%20Manual%20oficial/manual-lts-2026-es/Drag_And_Drop/Drag_And_Drop_Overview/Right_Mouse_Button_Menu_Options.md)
  - [Referencia de GML Visual](../09%20-%20Manual%20oficial/manual-lts-2026-es/Drag_And_Drop/Drag_And_Drop_Reference/DnD_Reference.md)
    y las 27 páginas de biblioteca de familia que enlaza (Common, Instance, Instance_Vars,
    Sequences, Mouse_And_Keyboard, Gamepad, Movement, Collisions, Drawing, Tiles, Audio, Loops,
    Switch, Data_Structures, Data_Types, Buffers, Files, Random, Cameras, Rooms, Paths,
    Timelines, Game, Miscellaneous, Particles, Time_Sources, Layers) — leídas íntegras para
    construir §3 y §4
  - Páginas individuales de acción abiertas para verificar argumentos y semántica exacta:
    `Assign_Variable`, `Set_Alarm`, `Create_Object_Instance`, `Destroy_At_Position`,
    `Change_Object_Instance`, `Set_Instance_Colour`, `If_Object_At_Place`,
    `If_Any_Object_At_Place`, `If_Collision_Shape`, `If_Collision_Point`, `Set_View_Variable`,
    `Apply_To...`, `New`, `Macro`, `Declare_A_New_Function`, `Function_Call`, `Execute_Script`,
    `For`, `While`, `Repeat`, `Loop`, `Switch`, `Case`, `Reverse`, `Snap_Position`,
    `Wrap_Around_Room`, `Set_Sprite`, `Set_Window_State`
  - [El depurador](../09%20-%20Manual%20oficial/manual-lts-2026-es/IDE_Tools/The_Debugger.md)
  - `game_save` y `instance_change` (páginas de referencia GML, marcadas DEPRECATED en el
    espejo): confirman la obsolescencia citada en §4 y §7
- `python3 "_indice/buscar.py" <símbolo>`, ejecutado contra el runtime instalado
  2026.0.0.23 para cada función de la tabla del §4 (ver informe de cierre de la tarea).
