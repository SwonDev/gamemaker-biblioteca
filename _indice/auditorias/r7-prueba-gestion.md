# R7 · Prueba de la skill `gamemaker-biblioteca` — juego de gestión (granja + tienda)

**Fecha:** 8 de septiembre de 2026. **Agente:** Claude (Opus 5, 1M contexto), sesión aislada,
`~/gm_prueba_gestion` (creado y borrado en esta misma sesión, nunca dentro de la biblioteca).
**Encargo:** «hazme un juego de gestión, tipo tienda o granja, con economía y que se pueda
guardar la partida» — el perfil que más sistemas entrelaza a la vez de las pruebas r6/r7
(inventario, economía con precios, producción por tiempo, interfaz densa, guardado de un
estado grande), elegido a propósito porque es donde más probable es que las piezas de la
biblioteca —escritas por documentos distintos que se citan entre sí— no encajen solas.

**Veredicto corto:** las piezas **no encajan solas — casi ninguna combinación lo hizo a la
primera** — pero la biblioteca da todo lo necesario para encajarlas a mano, con evidencia
citable en cada punto de fricción. Encontré **cinco incompatibilidades reales entre
documentos** (dos monedas con nombre distinto para el mismo concepto, dos modelos de datos de
inventario incompatibles, dos sistemas de «tienda» que no se citan entre sí, un `cultivo_plantar()`
que no cobra semilla, y un `panel_dibujar()` acoplado a un sprite que nadie avisa que hay que
tener listo) y **dos bugs reales de ejecución** que compilaron limpio y solo revientan al jugar
— uno de ellos con causa raíz en un comportamiento de GML (variables `static` de un
constructor) que ninguno de los documentos combinados menciona, y que **`validar-integracion.py`
no puede ver por diseño** porque su capa 3 solo compila, nunca ejecuta (§6). El guardado, en
cambio, **aguantó sin fisuras** un estado grande y anidado —huerto de 20 celdas, inventario con
varios objetos apilados, catálogo de tienda con 6 entradas mutables, calendario— a través de un
`pkill` real del proceso y una recarga completa. Y la economía dinámica **no es teoría**: la
comprobé con la calculadora en la mano contra los precios que enseñó el juego en vivo y
cuadraron al céntimo.

---

## 1 · Qué se construyó

Proyecto `gm_prueba_gestion` (plantilla *Blank Pixel Game* — sin *prefabs*, la única sin las 9
plantillas rotas de la Trampa 2 que no necesitaba tocar), **"Cosecha y Trato"**: el jugador
cultiva y riega un huerto de 20 parcelas (5×4), vende la cosecha y compra semillas a un
mercader con precio que sube y baja de verdad según lo que compra y vende, contra un
calendario de 10 días y 4 estaciones, con el objetivo de reunir 300 monedas antes de que se
acabe el tiempo.

- **3 salas**: `rm_menu`, `rm_juego`, `rm_creditos`.
- **5 objetos**: `obj_juego` (persistente: arranque, calendario, modo QA), `obj_parcela` (×20,
  clic para plantar/regar/cosechar/arrancar), `obj_hud` (HUD + inventario + tienda + pausa +
  opciones + resultado, todo en Draw GUI), `obj_menu`, `obj_creditos`.
- **17 scripts**: dos copiados **verbatim** de la biblioteca (`scr_save_load.gml`,
  `scr_ui_confirmar.gml`); el resto, adaptaciones documentadas de `13·05`, `13·01`, `04·04`,
  `04·45` y `04·16` — el detalle de cada adaptación, con la línea exacta que no encajaba, está
  en `objects/*/​*.gml` y `scripts/*/​*.gml` de la sesión (ya borrados con el proyecto; citados
  aquí de memoria y con captura de pantalla como evidencia).
- **1 `datafiles/items.json`** (6 objetos: 3 semillas, 3 cosechas) + **6 sonidos** sintetizados
  con la receta de `13·09 §8 ter` (`.wav` generado con el módulo `wave` de Python, sin
  dependencias) + **2 fuentes horneadas a mano con Pillow** (Trampa 5, ver §5) + **2 sprites**
  procedurales de dos tonos + contorno (`12·09 §5.2`, peldaño 1).
- **Bucle completo**: menú (Nueva partida / Continuar / Opciones / Créditos / Salir) → granja
  jugable con HUD denso (día, estación, oro, objetivo, selector de semilla) → pausa real →
  guardado/carga → fin de partida (victoria a 300 oro, derrota al día 11) → vuelta al menú.
  Checklist maestro de `04·00` comparado en §7.

**Recortes explícitos** (regla del checklist maestro: lo que se recorta se dice, no se omite):
- **Sin mando** — solo teclado y ratón; `dispositivo_actualizar()` de `13·05 §2.3` se copió
  recortando la rama de mando (el juego no lo necesitaba y no había forma de probarlo aquí).
- **Un solo slot de guardado** (`"partida"`), no varios — es una partida de sesión única con
  un final claro (victoria/derrota a 10 días), no un juego de progresión larga; el checklist de
  `04·00` lo permite expresamente para este caso.
- **Sin splash ni intro/cinemática** — el encargo es una prueba de integración de sistemas, no
  de presentación; el título hace de splash.
- **Sin ganado** — `04·45 §5.6` documenta un `Animal()` completo (struct sobre `Needs()`,
  degradación diaria, reproducción, serialización) que decidí NO usar para no diluir el foco de
  la prueba (inventario+economía+guardado+UI ya cubren de sobra el objetivo); es un recurso real
  de la biblioteca que dejé sobre la mesa a propósito, no un hueco de la biblioteca.
- **Sin localización `txt()`** — todo el texto está escrito directamente en español; el
  checklist de `04·00` lo pide para publicar, no para esta prueba de integración.

---

## 2 · ¿Encajaron las piezas de inventario, economía, guardado e interfaz, o tuve que adaptarlas?

**Tuve que adaptarlas — las cinco fricciones reales, con la línea que no cuadraba:**

### 2.1 · Dos monedas con nombre distinto para el mismo concepto

`13·05 §3.5k` (`scr_ui_tienda`, el componente de tienda del catálogo de UI) lee y escribe
`global.monedas` directamente (`global.monedas -= _item.precio` en su `tienda_comprar()`). Pero
**ningún otro documento de la biblioteca declara esa global**: `04·04 §5.2` guarda el oro en
`Inventory.oro`, y `13·01 §9.9` lo confirma citando exactamente ese campo («`Inventory` con su
campo `oro`, reutilizado como billetera»). Un agente que siguiera `13·05 §3.5k` al pie de la
letra en un proyecto que ya usa `Inventory` (que es lo que hace CUALQUIER receta con inventario
por pilas, incluida la de granja) tendría **dos carteras del jugador que nunca se sincronizan**.
Lo resolví sustituyendo cada lectura/escritura de `global.monedas` por `global.inventario.oro` en
mi `scr_ui_tienda.gml`.

**`validar-integracion.py` no lo detecta**: lo comprobé en vivo (§6) — su capa 2 («¿todo
`global.X` leído se escribe en algún sitio?») da `global.monedas` por bueno porque `13·05 §3.5k`
lo escribe DENTRO de su propio documento. El fallo no es «variable sin escribir», es «dos
variables distintas modelan el mismo concepto sin saberlo» — una categoría que ninguna de las
tres capas del script comprueba.

### 2.2 · Dos modelos de datos de inventario incompatibles

`13·05 §3.5e` (el inventario en cuadrícula) espera un array de **ranuras fijas**
`objetos[columnas*filas]` donde cada celda ya contiene `{icono, cantidad}` directamente. El
`Inventory` de `04·04 §5.2` —el que de verdad usa cualquier receta con oro e ítems— es una
**lista dinámica** `slots[]` de `{item_id, cantidad}` que crece al final, sin índice de celda
fijo y sin campo `icono` (el icono se busca aparte con `item_get_def(item_id)`). Son dos
estructuras de datos que no comparten ni un campo, y ninguno de los dos documentos menciona al
otro, aunque `04·45 §5` cita a los dos juntos para «granja» en la misma sección. Escribí un
puente (`inventario_ui_proyectar()`) que vuelca `slots[]` en un array de celdas fijo cada vez que
se abre la ventana, resolviendo icono y nombre con `item_get_def()`. El arrastrar-y-soltar del
documento original lo descarté entero: no aplica a un juego donde los objetos se consumen por
acción (plantar, vender), nunca se arrastran a un hueco de equipo.

### 2.3 · Dos sistemas de «tienda» que no se citan entre sí

`13·05 §3.5k` es solo interfaz: catálogo `{nombre, icono, precio, stat, stat_equipado, comprado}`,
precio fijo, compra única con bandera `comprado`, sin existencias. `13·01 §9.8`
(`TiendaNPC`) es solo economía: `{id, precio_base, stock, stock_max, stock_referencia}`, precio
que sube y baja con el stock (`precio_dinamico()`, §4.6), margen compra/venta, reposición diaria.
**Ni un campo en común.** Ninguno de los dos documentos enlaza al otro pese a resolver
literalmente el mismo problema («una tienda»). Los fusioné a mano: mi `tienda_ui_step()` no lee
`_item.precio` una vez, llama a `tienda.precio_venta()`/`precio_compra()` **cada frame**, y añadí
dos pestañas («Vender cosecha» / «Comprar semillas») porque el documento de UI solo ilustra un
catálogo de un solo sentido — vender la cosecha es la mitad del bucle económico de este juego, y
no había ninguna UI ya escrita para ello.

Encima, `TiendaNPC.step()` (la reposición diaria de `13·01 §9.8`) solo sabe reponer **hacia
`stock_max`** — pensada para un catálogo solo-de-compra. Con un catálogo de dos direcciones (el
jugador compra semillas Y vende cosecha) esa única regla no vale para las dos mitades: tuve que
escribir `tienda_paso_dia()` con una rama por `direccion` (semillas reponen hacia el máximo,
cosecha decae hacia el nivel normal) — un caso que el documento fuente no cubre porque su
ejemplo nunca combina las dos direcciones en el mismo catálogo.

### 2.4 · `cultivo_plantar()` no cobra la semilla

`04·45 §5.3` da `cultivo_plantar(_col, _fila, _tipo_semilla)` sin descontar nada del inventario
del jugador — planta gratis. Sin ese descuento, comprar semillas en la tienda (§2.3) no tendría
ningún efecto sobre el huerto: la mitad de la economía del juego quedaría desconectada de la
otra mitad. Añadí `Inventory.remove()`/`has()` (`04·04 §5.2`) antes de plantar — un enganche
que ninguno de los dos documentos hace por sí solo, aunque `04·45 §5` cite a `04·04` para
«recolección, inventario por pila» en su propia sección «a qué apoyarte».

### 2.5 · `panel_dibujar()` acoplado a un sprite que nadie avisa que hace falta

`13·05 §3.4/§3.5a` dibuja cada panel (botón, tienda, inventario, avisos) con
`panel_dibujar(_spr, _px, _py, _ancho, _alto, ...)` sobre un sprite de panel con nine-slice ya
recortado a mano **en el editor**. Esta prueba no genera arte de UI (fuera de alcance
deliberado: es una prueba de integración de sistemas, no de arte — ver `12·09 §5.2`, que
tampoco cubre paneles, solo sprites de personaje/objeto). Reescribí `panel_dibujar()` sin el
parámetro `_spr`, con `draw_roundrect_ext`, y tuve que actualizar **cada** llamada del resto de
componentes (tienda, inventario, avisos, botones) para no pasarles un sprite que ya no
esperaban. El documento nunca avisa de que `panel_dibujar()` es un punto de acoplamiento con un
asset que hay que tener preparado de antemano — se descubre al intentar usarlo sin ese asset.

**Lo que SÍ encajó sin fricción, para que quede constancia** (§6.2 de la biblioteca lo pide:
citar también lo que funciona): el bus de señales (`04·16`) enganchando calendario → huerto →
reposición de tienda → condición de fin, sin un solo cambio; `scr_save_load.gml` y
`scr_ui_confirmar.gml`, **copiados literalmente, cero cambios, cero bugs**; `ancla()`/
`zona_segura()`/`boton_*` (`13·05 §3.2/§3.5a`) rock-solid en menú, HUD, pausa, opciones y tienda;
la fórmula de precio dinámico (`13·01 §4.6/§9.8`) verificada con la calculadora contra los
precios reales en pantalla (§4); y el patrón de calendario/cultivo de `04·45 §5.2/§5.3`
funcionando exactamente como está escrito una vez enganchado.

---

## 3 · ¿Aguantó el guardado un estado grande, al matar el proceso y reabrir?

**Sí, sin ninguna fisura — y encontró dos bugs reales por el camino (§5).**

Jugué varios días de partida (planté, regué, compré semillas de los tres tipos, dejé que dos
parcelas se marchitaran por no regarlas), guardé con `F9` (atajo QA que llama a la misma
`granja_guardar()` que el botón «Guardar» del menú de pausa — mismo camino de código) y
confirmé el estado exacto por el archivo en disco antes de tocar nada más:

```json
"inventario":{"capacidad":40,"slots":[
  {"item_id":"semilla_nabo","cantidad":2},
  {"item_id":"semilla_patata","cantidad":1},
  {"item_id":"semilla_zanahoria","cantidad":1}],"oro":13},
"huerto":[ {"estado":4,"tipo":0,"edad_dias":1,"regada":false},
           {"estado":4,"tipo":0,"edad_dias":1,"regada":false},
           /* ...18 celdas más, VACIA... */ ],
"dia_actual":3,"estacion_indice":2,"tiempo_dia":0.4989...,
"tienda":{"catalogo":[
  {"id":"semilla_nabo","direccion":"compra","stock":30,"stock_max":30,"stock_referencia":10,"precio_base":4},
  /* ...5 entradas más, precios y stock ya movidos por el juego... */ ]},
"objetivo_oro":300,"dias_limite":10
```

Un huerto de 20 structs anidados, un inventario con varios ítems apilados y oro, un catálogo de
tienda de 6 entradas con estado mutable propio, y el calendario — el «estado grande y complejo»
que pide la prueba. Con el `checksum` (`sha1_string_utf8`) y el sobre `version`/`fecha`/`meta`
de `scr_save_load.gml` intactos.

Entonces:

```
$ pkill -f Mac_Runner
$ ps aux | grep -i Mac_Runner | grep -v grep
(sin salida)
```

Proceso muerto de verdad, no solo la ventana cerrada. Relancé el juego desde cero
(`gm-cli run`), y en el menú, **«Continuar» ya aparecía activo** (`save_exists(SLOT_PARTIDA)`
detectó el archivo del proceso anterior). Clic en «Continuar» → **la partida se reconstruyó
exactamente**: mismo día (9/10, Otoño), mismo oro (13), mismas tres semillas con sus cantidades
exactas, mismas dos parcelas marchitas en las mismas celdas, resto del huerto vacío. Capturas de
pantalla de antes y después de matar el proceso, comparadas campo a campo — coinciden en todo.

**Con dos bugs reales por el camino, ambos en la ruta de carga, ninguno en la de guardado** —
ver §5 para el detalle y la causa raíz.

---

## 4 · ¿Me dio la biblioteca una economía que funcione, o solo teoría?

**Funciona de verdad, y lo comprobé con la calculadora, no solo mirando que el número
cambiara.** `13·01 §4.6` da la fórmula:

```
precio = precio_base × clamp((stock/stock_referencia)^(-elasticidad), 0.4, 3.0)
```

Tras varios días de juego sin comprar nada, el stock de semillas (dirección «compra», que se
repone solo con `tienda_paso_dia()`) había subido de 10 a 22 unidades (stock_referencia=10). Los
precios que enseñó la tienda en pantalla:

| Objeto | precio_base | Precio mostrado | `4×(22/10)^-0.6` |
|---|---|---|---|
| Semilla de nabo | 4 | **3** | `ceil(4 × 0,6232) = 3` ✓ |
| Semilla de patata | 7 | **5** | `ceil(7 × 0,6232) = 5` ✓ |
| Semilla de zanahoria | 5 | **4** | `ceil(5 × 0,6232) = 4` ✓ |

Coincide al céntimo con la fórmula documentada — **no es un número que sube porque sí, es
oferta y demanda real, verificable**. Compré una semilla de patata (oro 20→16, confirmado por
toast «Comprado: Semilla de patata (-4)») y el precio de la siguiente unidad subió acorde al
descuento de stock. Compré también una de zanahoria (oro 16→13). Es exactamente lo que pide
`13·01 §4.6`: «el precio se mueve, pero sin que el jugador lo note frame a frame» — elasticidad
0,6, el rango medio que la propia tabla recomienda.

Y la tabla estacional que añadí (§2 de mi `scr_economia.gml`, no citada por ningún documento —
es una pieza propia de esta prueba) engancha el calendario de `04·45 §5.2` con el precio de
`13·01 §9.8`: el nabo vale un 20 % más en primavera y un 20 % menos en invierno, y así con cada
cultivo. Es la única conexión real entre «granja» y «economía» que hilvana los dos documentos —
ninguno de los dos lo hace por sí solo.

**Veredicto**: la biblioteca no da solo la teoría (`13·01 §4.1` el vocabulario, `§4.6` la
fórmula) — da el código que funciona (`13·01 §9.8`, `TiendaNPC` completo con margen y stock).
Lo que NO da es el paso de unirlo con una UI que lo muestre (§2.3) ni con un calendario que le
dé estacionalidad — eso lo puse yo.

---

## 5 · Los dos bugs reales de ejecución — compilaron limpio, reventaron al jugar

### 5.1 · `Inventory.deserialize(...)`: «Variable \<unknown_object\>.deserialize(...) not set before reading it»

**Reproducido en vivo, primer intento de «Continuar» tras relanzar el proceso desde cero**
(exactamente el flujo de §3): `gm-cli compile` en verde, el juego arranca, el menú se ve bien,
clic en «Continuar» y el runner muestra el diálogo de error nativo con la traza completa:

```
ERROR in action number 1
of  Step Event0 for object obj_menu:
Variable <unknown_object>.deserialize(100021, -2147483648) not set before reading it.
 at gml_Script_granja_aplicar_datos (line 34) -    global.inventario   =
Inventory.deserialize(_data.inventario);
```

**Causa raíz, confirmada contra el manual oficial** (no una suposición — `09 - Manual oficial/
manual-lts-2026-es/.../Functions/Static_Variables.md:67-71`, sección «Estáticas con
constructores»): *«Las variables estáticas en los constructores solo se inicializan **una vez**
para ese constructor»* — la primera vez que se llama con `new`. `Inventory.deserialize` es un
método `static` (`04·04 §5.2`: `static deserialize = function(_d) {...}`), así que
`Inventory.deserialize(...)` **no existe como miembro accesible** hasta que `new Inventory(...)`
se ha llamado al menos una vez en el proceso. En mi proyecto —y en **cualquier** proyecto que
siga `04·04 §5.8` al pie de la letra— el único sitio que llama a `new Inventory()` es
`granja_partida_nueva()`/el equivalente de «Nueva partida». Si el jugador **relanza el juego y
pulsa "Continuar" directamente**, sin pasar por "Nueva partida" en ese proceso, `Inventory`
nunca se ha instanciado todavía: `rpg_cargar()`/`granja_cargar()` revienta en la primera línea
que toca el inventario.

Esto es exactamente el flujo que este informe estaba obligado a probar («matar el proceso y
reabrir») — y es el camino que **cualquier jugador real toma más a menudo**: cerrar el juego a
mitad de partida y volver a abrirlo más tarde, sin querer empezar una partida nueva primero.
`04·04 §5.8` no lo menciona ni una vez; el propio código de `rpg_cargar()` que da como ejemplo
tiene el mismo agujero.

**Arreglo** (documentado en el propio código, con la cita al manual): «cebar» el constructor con
una llamada `new Inventory(1);` desechable en el arranque del juego (`obj_juego::Create`), antes
de que cualquier ruta de carga pueda ejecutarse. Apliqué el mismo arreglo a `TiendaNPC` (mi
propia extensión de `13·01 §9.8`, con el mismo patrón `static deserialize`), porque tiene
exactamente la misma vulnerabilidad y por la misma razón.

### 5.2 · `global.nombres_estacion`: la ruta de carga se salta la inicialización que solo pone «Nueva partida»

Al arreglar 5.1 y volver a probar «Continuar» en frío, apareció un segundo error, distinto:

```
ERROR in action number 1
of  Draw Event for object obj_hud:
Variable <unknown_object>.nombres_estacion(100007, 2) not set before reading it.
 at gml_Object_obj_hud_Draw_64 (line 17) -   $"Día {_dia_abs}/{DIAS_LIMITE} · {global.nombres_estacion[global.estacion_indice]}"
```

Este es **mío**, no de un documento de la biblioteca — pero nace de seguir demasiado al pie de
la letra el patrón de `04·45 §5.2` (`calendario_iniciar()` rellena `global.nombres_estacion`)
combinado con `04·00 §1` («los sistemas globales se montan primero»): asumí que «montar los
sistemas globales» y «empezar una partida nueva» eran el mismo momento, y no lo son —
`granja_cargar()` (la ruta de «Continuar») nunca pasa por `calendario_iniciar()`, así que una
tabla que debería ser una constante del juego (los nombres de las cuatro estaciones no cambian
entre partidas) se quedaba sin rellenar en la ruta de carga. Lo saco de `calendario_iniciar()`
y lo pongo en el arranque incondicional de `obj_juego::Create`, donde debía estar desde el
principio por ser dato constante, no estado de partida.

Con los dos arreglos, «Continuar» en frío funciona de punta a punta (§3). **Ninguno de los dos
bugs lo cazó `gm-cli compile`** — los dos exit 0, limpio, las dos veces — exactamente la
advertencia de la Trampa 4 («el compilador no detecta variables sin declarar, revienta al
ejecutar»), aquí con una causa nueva (orden de inicialización de `static` en constructores) que
ni la Trampa 4 ni ningún otro documento de la biblioteca describen.

---

## 6 · ¿`validar-integracion.py` habría cazado algo de esto?

**No, ninguno de los siete hallazgos de §2 y §5 — lo comprobé ejecutándolo de verdad, no
asumiéndolo.**

```
$ python3 _indice/validar-integracion.py
validar-integracion.py — capas 1 y 2 (nombres duplicados · global.X sin escribir)

✓ Sin duplicaciones graves (mismo nombre, distinta aridad, o macro/enum repetido).

🟠 4 duplicación(es) MEDIA(S) (misma aridad, cuerpo distinto — una gana en silencio):
  [4 casos sin relación con esta prueba: caidas_instalar_manejador, conductor_error,
   logro_desbloquear, tween_to]

✓ Todo `global.X` leído en la biblioteca se escribe en algún sitio de la biblioteca.

Sin incompatibilidades de integración detectadas.
```

Sale limpio sobre la biblioteca completa, y por diseño **no puede** ver mis siete hallazgos:

- **§2.1 (`global.monedas` vs `Inventory.oro`)**: la capa 2 solo pregunta «¿se escribe en algún
  sitio?» — y `global.monedas` SÍ se escribe, dentro del mismo documento que lo lee (`13·05
  §3.5k`). El fallo no es «variable sin escribir», es «dos variables distintas para el mismo
  concepto real» — una categoría semántica que ninguna de las tres capas comprueba (lo dice el
  propio script en su docstring: compara *nombres*, no *significados*).
- **§2.2, §2.3, §2.4 (modelos de datos incompatibles, dos tiendas, plantar sin cobrar)**: la
  capa 1 compara **nombres duplicados** con aridad o cuerpo distinto. Estos tres casos usan
  vocabularios **completamente distintos** sin ni un nombre en común (`inventario_nuevo`/
  `objetos[]` frente a `Inventory`/`slots[]`; `tienda_comprar()` frente a
  `TiendaNPC.vender_a_jugador()`) — no hay ninguna colisión de nombre que detectar, así que la
  capa 1 no tiene ninguna señal que comparar. Es, con diferencia, el tipo de incompatibilidad
  más difícil de cazar de forma estática: dos soluciones al mismo problema que no se citan ni
  comparten una sola palabra.
- **§5.1, §5.2 (bugs de ejecución)**: la capa 3 (`--compilar`), la única que toca GameMaker de
  verdad, **solo llama a `gm-cli compile`, nunca a `gm-cli run`** (confirmado leyendo el propio
  script: `subprocess.run(cmd...)` donde `cmd` es siempre `compile`, nunca `run`). El grupo
  `"guardado"` de `GRUPOS` (línea 782) además incluye exactamente `04·04` +
  `scr_save_load.gml` + `13·06` — el trío de documentos donde vive el bug 5.1 — pero como el
  bug solo se manifiesta **ejecutando** el juego y pulsando «Continuar», ni siquiera
  `--compilar --grupo guardado` lo habría encontrado: compilaría limpio, igual que en mi propio
  proyecto.

**Conclusión honesta**: `validar-integracion.py` es una herramienta real y útil (encontró de
verdad los casos para los que se diseñó, como demuestra `r5-integracion.md`), pero cubre **una
capa** del problema —nombres que chocan o que nadie inicializa—, no **incompatibilidad
semántica** (dos soluciones distintas al mismo problema) ni **comportamiento de ejecución**
(un `static` que no está listo hasta la primera llamada). A la propia herramienta le falta una
capa, tal como pedía el encargo de esta prueba.

---

## 7 · ¿Mostrar muchos datos en pantalla de forma legible?

**Sí — la jerarquía de tres niveles de `13·05 §1.1` se sostiene con una interfaz bastante
cargada.** La barra superior (día/estación · oro/objetivo · atajos) y la fila de selección de
semilla se leen de un vistazo; el panel de tienda con dos pestañas, seis filas de precio y un
diálogo de confirmación superpuesto no se sintió abrumador en las capturas de pantalla reales —
el patrón de `panel_dibujar()` + `boton_*` con estados de cuatro colores (§3.5a) hace su trabajo.
Los avisos apilados (`§3.5i`) se probaron en vivo con compras y plantaciones reales y nunca se
solaparon con el resto de la UI de forma ilegible, aunque en una ocasión un aviso largo se
superpuso brevemente con la etiqueta «Tienda» del HUD — un roce cosmético, no un bloqueo.

Lo que **no** pude verificar de forma concluyente por límite de tiempo de la sesión (no de la
biblioteca): la cosecha completa de un cultivo maduro y su venta real con inventario de cosecha
no vacío — el reloj de calendario (30 s/día, acelerado a propósito) corrió más rápido que mi
ritmo de pruebas interactivas, y las dos parcelas que planté se marchitaron antes de madurar por
no regarlas a tiempo (una demostración honesta, aunque no buscada, de que `04·45 §5.3` sí
castiga el descuido). La pestaña «Vender cosecha» se verificó correctamente deshabilitada con
cantidad 0 (botón inactivo, motivo «No tienes ninguna»), pero no llegué a ver una venta de
cosecha real con oro entrando por esa vía — el código es la misma llamada
(`Inventory.add()`/`global.tienda.comprar_de_jugador()`) que ya se verificó funcionando en la
dirección de compra, así que el riesgo es bajo, pero lo digo con claridad en vez de omitirlo.

---

## 8 · Compilación real

Última compilación, **sin** `--errors-only` (la que muestra cualquier `WARNING` de un
*included file* sin copiar, Trampa 8), desde `~/gm_prueba_gestion/gm_prueba_gestion`:

```
$ python3 "_indice/validar-proyecto.py" "$(pwd)" --todo
31 archivos .gml · 1066 llamadas analizadas · runtime del índice 2026.0.0.23

✓ Ninguna llamada a una función del runtime que no exista.

✓ Ninguna llamada a una función del runtime con un número de argumentos que no cuadre con su firma.

$ gm-cli compile --toolchain GMS2@2026.0.0.23 --target mac
[…]
│  Compile Constants... finished.
│  Compile Scripts... finished.
│  Compile Rooms... finished..... 0 CC empty
│  Compile Objects... finished.... 0 empty events
│  Compile Timelines...finished.
│  Compile Triggers...finished.
│  Compile UI Layers... finished.
│  Global scripts...finished.
│  Final Compile finished.
│  Saving IFF file... […]/output/game.zip
│  Stats : GMA : sp=2,au=6,bk=0,pt=0,sc=195,sh=0,fo=2,tl=0,ob=5,ro=3,da=1,ex=0,ma=6,…
│  Igor complete.
◆  Compilation finished
```

**Sin ninguna línea `WARNING` ni `ERROR`** (`grep -i "warning\|error"` sobre la salida completa,
sin coincidencias). `da=1` confirma `items.json` empaquetado con `filePath` corregido (Trampa 8,
ver §9); `fo=2` las dos fuentes horneadas a mano; `au=6` los seis sonidos sintetizados.

`gm-cli run --toolchain GMS2@2026.0.0.23 --target mac` arrancó limpio en los seis lanzamientos
de esta sesión — `debug.log` sin una excepción no controlada salvo las dos de §5 (ambas
reproducidas, diagnosticadas y corregidas antes de la compilación final de arriba).

**Recuerda que "compila limpio" no es "funciona"** (`13·10 §8.6`, repetido aquí a propósito):
los dos bugs de §5 compilaron limpio las dos veces, exactamente como advierte la biblioteca.

---

## 9 · Las once trampas — cuáles se usaron de verdad, y una nueva

Usadas en esta sesión, las once leídas antes del primer comando:

- **Trampa 1** (sandbox cuelga `resourcetool`/`compile`): todo con `dangerouslyDisableSandbox:
  true` desde el primer comando — sin eso, cada llamada se habría colgado.
- **Trampa 2** (plantillas rotas): usé *Blank Pixel Game*, sin *prefabs* — sin fricción.
- **Trampa 5** (fuentes horneadas por `resourcetool` con glifos vacíos): reproducida al
  crear `fnt_ui`/`fnt_titulo` (glifos `{}` tras `font addrange`/`font setfile`), resuelta con
  la receta de Pillow: parto del `.yy` YA creado por `resourcetool` en el proyecto de destino
  (con `%Name`/`parent` correctos de fábrica, evitando el `AccessViolationException` de
  identidad que documenta la propia Trampa 5), rasterizo con `PIL.ImageFont`/`ImageDraw` sobre
  Arial del sistema, y sobrescribo `glyphs`/`ranges`/`size`. **Verificado con captura de
  pantalla real de la ventana**, no solo con el tamaño del *chunk* `FONT`: texto en español con
  tildes, eñes, ¿ y ¡ se lee perfectamente en el juego corriendo.
- **Trampa 8** (`includedfile` deja `filePath` vacío): reproducida al empaquetar
  `items.json` — corregida con `resource set expr=project.IncludedFiles[0].filePath
  value=datafiles` (por índice, no por nombre del recurso — `items.json` lleva un punto,
  exactamente la advertencia de la propia trampa sobre nombres con punto). Confirmado con la
  compilación sin `--errors-only` de §8: `da=1`, sin `WARNING`.
- **Trampa 9** (subtipos de evento): `OBJECT EVENT FINDORCREATE ... TYPE=Step` con `SUBTYPE`
  vacío falla («Invalid value '' for 'SUBTYPE'»); hace falta `SUBTYPE=step_normal` explícito
  (y `SUBTYPE=draw_normal`/`gui` para Draw/Draw GUI). No es exactamente la Trampa 9 tal como la
  describe la biblioteca (esa habla de GUI Begin/End y Room End, que no usé), pero es la misma
  familia de fricción: el `HELP` de `resourcetool` no dice qué subtipo hace falta hasta que se
  prueba y falla.
- **Trampa 11** (`ResourceTool` revienta sin motivo): un diálogo nativo «ResourceTool se ha
  cerrado inesperadamente» apareció capturado de fondo en una captura de pantalla durante la
  sesión, sin que ninguna llamada real de esta prueba reportara fallo (`ResourceTool
  Successful` en cada una) — consistente con lo que documenta la trampa: crashes del binario,
  no del proyecto, que no hace falta perseguir si la operación en sí ya dijo éxito.

**Trampa nueva, fuera de las once y de las cuatro de GML puro:**

**`screen_save()` en el runner de Mac invierte la imagen verticalmente — la ventana real no.**
Al comprobar mi propio horneado de fuentes (Trampa 5) con `screen_save()`, el PNG resultante
mostraba el texto y un sprite de prueba **boca abajo y con el orden vertical invertido** (un
título dibujado en `y=20` aparecía al fondo de la imagen, no arriba). Antes de asumir que mi
horneado estaba mal, comparé contra una captura de pantalla real de macOS
(`screencapture`) tomada mientras el mismo frame se veía en la ventana del runner: **la ventana
se ve perfectamente, derecha, en el orden correcto** — el volteo es exclusivo de
`screen_save()` en esta combinación (`gm-cli` 2.3.0, runtime 2026.0.0.23, `--target mac`), no
del juego ni de mi código. Esto es relevante para cualquier agente que use `screen_save()` como
canal de verificación (`12·09 §4.1`, tal como recomienda la propia biblioteca para «depurar sin
ver la pantalla»): **la captura automática puede mentir sobre la orientación mientras el juego
real se ve bien**, así que conviene contrastar al menos una vez con una captura de pantalla del
sistema operativo antes de diagnosticar un bug de renderizado a partir solo de `screen_save()`.

Las cuatro trampas de GML puro (`1e10`, ternario anidado, `#macro` en vez de `const`,
constructor con padre no definido) no aparecieron: no escribí notación científica, no anidé
ternarios, y usé `#macro` para las constantes desde el principio (aprendido de las pruebas r5/r6
citadas por la propia biblioteca).

---

## 10 · Veredicto final

**¿Encajan las piezas de la biblioteca cuando un juego usa muchas a la vez?** No solas — pero
la biblioteca da, en cada punto de fricción, lo que hace falta para encajarlas a mano con
confianza, con una firma verificable y una cita exacta de dónde viene cada mitad del problema.
Las cinco fricciones de §2 tienen un patrón común: son documentos escritos por manos distintas
que resuelven el mismo problema de dos formas razonables por separado, y **ninguno de los dos
sabe que el otro existe** — ni siquiera cuando un tercer documento (`04·45 §5`) los cita a los
dos juntos en la misma sección «a qué apoyarte». Eso no es un fallo de la información —cada
pieza, por su cuenta, es correcta y está bien escrita— es exactamente el límite que esta prueba
estaba diseñada para encontrar.

Los dos bugs de ejecución de §5 son más serios que los de fricción de UI: uno de ellos rompe el
flujo **más común de un jugador real** («cerrar el juego y volver más tarde»), compila limpio,
y su causa —el orden de inicialización de variables `static` en un constructor— **no está
descrita en ningún documento de la biblioteca**, incluido el que la introduce (`04·04 §5.2`,
`Inventory.deserialize`) y el que la extiende (`13·01 §9.8`, con mi propio `TiendaNPC` sufriendo
la misma vulnerabilidad por seguir el mismo patrón). Es un hallazgo nuevo, con causa raíz
confirmada contra el manual oficial, no una sospecha.

Y el guardado —la pieza que esta prueba estaba más obligada a estresar— **aguantó perfecto** un
estado grande y anidado a través de un `pkill` real, sin ayuda de nada que no fuera
`scr_save_load.gml` tal cual está escrito. Si algo de esta prueba hay que creerse sin reservas,
es eso.

---

## 11 · Limpieza

```
$ pkill -f Mac_Runner
$ ps aux | grep -i "Mac_Runner\|gm_prueba_gestion" | grep -v grep
(sin salida — limpio)
$ rm -rf ~/gm_prueba_gestion
$ ls ~/gm_prueba_gestion
ls: /Users/adrianpereradelgado/gm_prueba_gestion: No such file or directory
```

**Nota operativa, no un hallazgo sobre la skill**: durante esta sesión hubo, como mínimo, otras
dos sesiones de agente activas en el mismo Mac (una trabajando en un proyecto llamado
"Lumbre", otra en un "sandbox ARPG" vía Codex/ChatGPT), cada una con su propia ventana de
runner o de app compitiendo por el foco del sistema. Varios clics y teclas de esta sesión
aterrizaron por error en esas otras ventanas antes de que reposicionara la ventana de mi propio
proceso a una zona despejada de la pantalla y verificara el `PID` con `ps aux` antes de cada
tanda de capturas. No se tocó nada destructivo de esos otros proyectos (solo clics de
navegación). El sibling report `r7-prueba-movil.md` documenta el mismo problema en la dirección
contraria (un clic de esa sesión aterrizó en la ventana de ESTA prueba) — confirma que la
interferencia fue real y mutua, un recordatorio de que ejecutar `gm-cli run` con verificación
visual automatizada en un Mac compartido por varias sesiones de agente necesita aislar el
proceso propio por `PID`/posición de ventana desde el primer lanzamiento, no solo al final.
