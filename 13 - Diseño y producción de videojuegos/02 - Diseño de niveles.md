# 02 · Diseño de niveles

> **El diseño de niveles es un oficio, no una decoración.** Aquí está cómo se piensa un nivel antes de construirlo,
> cómo se construye sin rehacerlo tres veces, y cómo se traduce a las herramientas reales de GameMaker: Room Editor,
> tile sets, capas, triggers y datos externos.
>
> **No cubre** las mecánicas de cada género ([`04 - Recetas por género`](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md)), ni la API de rooms,
> capas y cámaras ([`01 · 10`](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md)), ni el
> flujo LDtk/Tiled → GameMaker, ya resuelto en [`12 · 05`](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md) §2.

---

## 1 · Los principios

### 1.1 El nivel enseña: introducir → desarrollar → torcer → concluir

La estructura de nivel más influyente del oficio no viene del diseño de juegos: viene de la poesía china de cuatro
versos y del manga de cuatro viñetas. Se llama **kishōtenketsu** (起承転結) y Nintendo la usa como andamio de cada
escenario desde *Super Mario Galaxy 2*.

Koichi Hayashida lo explicó así: primero *«tienes que aprender a usar esa mecánica»*; después *«el escenario te ofrece
un escenario algo más complicado en el que tienes que usarla»*; luego *«pasa algo raro que te hace pensar en ella de
una forma que no esperabas»*; y al final *«puedes demostrar qué dominio has alcanzado»*. Miyamoto —que dibujaba cómics
de joven— trajo la idea.

| Fase | Japonés | Qué hace el nivel | Coste de fallar |
|---|---|---|---|
| **Introducir** | *ki* (起) | Presenta la idea en un espacio seguro | Nulo: se puede fallar sin consecuencia |
| **Desarrollar** | *shō* (承) | La misma idea, más exigente | Pequeño: retroceder unos metros |
| **Torcer** | *ten* (転) | La idea combinada con otra, o del revés | Medio |
| **Concluir** | *ketsu* (結) | El examen: todo lo aprendido, junto | Alto: aquí sí duele |

**La regla operativa: una idea por nivel.** Si tu nivel enseña tres mecánicas nuevas, no es un nivel: son tres niveles
mal cortados. Y cuando una idea se ha introducido, desarrollado, torcido y concluido, **se tira**: ya cumplió. Es lo
que permite meter cuarenta ideas sin cansar.

> 💡 Es inmediatamente accionable para un LLM: cuando te pidan «hazme el nivel 3», la primera pregunta no es «¿cuántos
> enemigos?», sino «¿qué idea enseña y cuáles son sus cuatro momentos?».

### 1.2 Ritmo (*pacing*): tensión y descanso

*Level Design Book* define el ritmo como *«el orden general y el ritmo de actividades y eventos en un nivel»*, y su
consejo central es corto y difícil de aplicar: **alterna picos y valles**. *«Los jugadores se acostumbran a periodos
prolongados de alta intensidad»* — la tensión sostenida deja de ser tensión. Y al revés: *«después de un combate de
jefe de alta intensidad, las cinemáticas y las zonas de baja intensidad se sienten como una recompensa»*.

La herramienta práctica es el **gráfico de intensidad**: X el tiempo, Y la intensidad de 0 a 5. Se dibuja *antes* de
construir y se corrige *después* de cada playtest. La intensidad no es solo dificultad: una escena sin input puede
tener intensidad emocional máxima.

```
 5 |                    ╭─╮            ╭───╮        entrada · reto · respiro
 3 |    ╭────╮     ╭───╯   ╲──╮   ╭───╯     ╲       combate · puzle · JEFE
 1 |╭──╯      ╲───╯           ╲──╯           ╲───   salida
 0 +──────────────────────────────────────────────→ tiempo
```

Un **beat** es *«un trozo pequeño y autocontenido de nivel»*. La técnica del *pile of beats* (usada en *Portal*)
consiste en construir muchos beats aislados, quedarse con los que funcionan y **ordenarlos después**: más barato que
diseñar la secuencia entera y descubrir que sobra el tercio central.

> ⚠️ El propio *Level Design Book* avisa: *«no puedes hacer playtest de un documento; los documentos de diseño nunca
> sobreviven a la realidad»*. El gráfico es una hipótesis.

### 1.3 Legibilidad: puntos de referencia, *weenies* y líneas de guía

El jugador tiene que saber **dónde está** y **hacia dónde va** sin leer nada. La teoría viene de la arquitectura:
Kevin Lynch describió el mapa mental de una ciudad como *caminos* («las vías que se usan para moverse»), *puntos de
referencia* («entidades fácilmente identificables que se usan como referencia») y *nodos* («puntos fuertes de
intersección»).

- **Landmark.** Algo alto, único e irrepetible visible desde lejos. Si tu nivel tiene dos torres iguales, no tiene
  puntos de referencia: tiene confusión.
- **Weenie.** Término de los Imagineers de Disney: un objeto grande y visible al fondo que *tira* del visitante sin
  obligarlo (el castillo al fondo de Main Street). En 2D, una silueta enorme al fondo del parallax que se ve desde la
  entrada y a la que se llega al final.
- **Líneas de guía.** La composición dirige la mirada: una fila de monedas, una hilera de farolas, una diagonal de
  plataformas. *Level Design Book* las llama *«líneas de objetos coleccionables o potenciadores»* — migas de pan.
- **Contraste de color y luz.** *«Contrastes de color (por ejemplo, una puerta azul brillante en un paisaje naranja
  oscuro)»*. Traducción barata a 2D: **lo interactivo tiene un color que no aparece en el fondo**. Nunca uses el color
  del suelo para una plataforma móvil.
- **Silueta.** Si en escala de grises no distingues plataforma de decorado, el jugador tampoco.

> 🔺 **La prueba de los cinco segundos.** Enseña una captura durante cinco segundos y pregunta hacia dónde iría. Si
> duda, el problema no es del jugador.

### 1.4 *Gating*: llaves, cerraduras y puertas blandas

| Tipo | Cómo se abre | Ejemplo | Riesgo |
|---|---|---|---|
| **Duro (llave)** | Un objeto o habilidad concretos | Puerta roja / llave roja; doble salto | Sin pista, el jugador se pierde |
| **Blando** | Habilidad del jugador, no del personaje | Un salto difícil que puede intentar siempre | Frustración si parece imposible |
| **De conocimiento** | El jugador entiende algo | Un interruptor oculto que ya vio funcionar | Se rompe si el jugador olvida |

**Regla de oro del gate duro: la cerradura se enseña antes que la llave.** El jugador ve la puerta que no puede abrir,
se queda con la imagen, y al encontrar la habilidad piensa «ya sé dónde usar esto». Es el motor del metroidvania, y su
implementación vive en [`04 · 06 — Metroidvania`](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md) §4.3 y
§5.5, que no repetimos.

**Regla de oro de la comunicación: el gate dice que falta algo, no qué falta.** Una puerta que se sacude comunica
«aquí hay algo»; un cartel que dice «necesitas el doble salto» mata el descubrimiento.

### 1.5 Riesgo, recompensa, secretos y atajos

Dan Taylor lo formuló como principio 7: *«un buen diseño de niveles permite al jugador controlar la dificultad»*. En
vez de preguntar «¿fácil, normal o difícil?» al empezar, el nivel ofrece una **ruta principal segura y rutas
opcionales caras**:

- **Camino alto = más riesgo, más premio**, y la elección es informada: se ve el premio *antes* de aceptar el riesgo.
  Un secreto que no se intuye no es un secreto, es un accidente.
- **Secretos en tres capas:** los que ves y aún no puedes coger (gate), los que ves si miras (una pared con textura
  distinta) y los que solo aparecen si experimentas. Los tres deben existir.
- **Atajos.** Uno que se abre desde el lado lejano —la escalera que bajas desde arriba y conecta con el principio—
  convierte el mapa en un anillo y hace *sentir* al jugador que domina el espacio. Es el recurso más barato para dar
  sensación de maestría.

### 1.6 Puntos de control, respawn y distancia entre retos

La distancia entre puntos de control **es** la dificultad, más que los enemigos.

| Modelo | Separación | Coste de morir | Ejemplo |
|---|---|---|---|
| **Pantalla única** | Una pantalla | ~1 s | *Celeste*: cientos de salas cortas, morir es casi gratis, la dificultad puede ser brutal |
| **Tramo largo** | Varios minutos | 30-90 s | *Souls*: morir duele, la tensión viene del riesgo acumulado |

Lo que **no** funciona es mezclarlos sin querer: un tramo largo con dificultad de pantalla única es el patrón de
abandono más común que existe.

> 💡 **El jugador nunca debería repetir un trozo que ya demostró saber hacer.** Si repite, el checkpoint está mal
> puesto.

### 1.7 Los diez principios de Dan Taylor

Un buen diseño de niveles… **(1)** *es divertido de recorrer* — la navegación es gameplay: verticalidad, atajos,
flujo. **(2)** *No depende de palabras* — el entorno cuenta: restos, desgaste, marcas de una pelea. **(3)** *Dice qué
hacer, no cómo*: *«los objetivos deben ser visualmente distintos»*, pero el método lo elige el jugador. **(4)**
*Enseña algo nuevo constantemente* — idea nueva, o recontextualización de una vieja. **(5)** *Es sorprendente* — un
cambio de escala, de ritmo o de regla; prototípalo antes de construirlo. **(6)** *Empodera al jugador*: sus acciones
dejan huella en el mundo. **(7)** *Le deja controlar la dificultad* con rutas opcionales de riesgo/recompensa. **(8)**
*Es eficiente*: piezas modulares, espacios bidireccionales, coleccionables que reaprovechan el mapa. **(9)** *Crea
emoción* — se empieza por la emoción y se eligen mecánica y métrica hacia atrás. **(10)** *Lo dirigen las mecánicas*:
el nivel es *«un sistema de entrega de gameplay»*.

---

## 2 · El método, paso a paso

### 2.1 Las métricas del jugador son la unidad de medida

**Nada se mide en píxeles: se mide en saltos.**

| Métrica | Se expresa en | Para qué la usas |
|---|---|---|
| Alto de salto | píxeles y **celdas** | Alto máximo de un obstáculo franqueable |
| Alcance de salto | píxeles y celdas | Anchura máxima de un abismo |
| Velocidad de carrera | px/frame | Longitud de un pasillo antes de aburrir |
| Alto del personaje | celdas | Alto mínimo de un túnel |
| Alcance del ataque | celdas | Distancia mínima de seguridad de un enemigo |
| Ancho de la cámara | celdas visibles | Cuánto puede anticipar el jugador |

*Level Design Book* insiste en dos cosas que ahorran meses: las métricas del jugador son **hechos medidos por el
motor**, mientras que las de construcción (ancho de pasillo, alto de muro) son **decisiones del diseñador**; y *«las
métricas son una herramienta útil para tomar decisiones, pero las métricas no son magia»* — al final decide el
playtest.

### 2.2 La hoja de métricas y la sala de pruebas

La **hoja de métricas** es una tabla de una página con esos números y su equivalente en celdas. La **sala de pruebas**
es esa tabla construida en el motor: una `rm_metricas` con

- una **escalera de muros** de 1, 2, 3… 10 celdas de alto,
- una **serie de abismos** de 1, 2, 3… 12 celdas de ancho,
- un **peine de techos** a 1, 2 y 3 celdas para probar túneles,
- un pasillo largo con marcas cada 10 celdas para cronometrar la velocidad.

Se juega después de **cada** cambio de física. Si el salto cambia, la hoja cambia y todos los niveles construidos con
la hoja vieja están mal. Por eso la hoja se versiona con el proyecto.

### 2.3 Boceto → caja gris → prueba → arte

```
 1. BOCETO      papel o cuadrícula. Planta, ruta crítica, beats. 10 min.
      ↓         ¿La idea del nivel cabe en una frase?
 2. CAJA GRIS   tiles de colores planos, sin arte. Todo jugable. 1-3 h.
      ↓         ¿Se puede terminar? ¿Los saltos entran? ¿Se ve hacia dónde ir?
 3. PRUEBA      alguien que no eres tú lo juega. Se anota, no se explica.
      ↓         ← se vuelve a 1 o a 2 tantas veces como haga falta
 4. ARTE        tiles definitivos, autotiles, parallax, luz, props, audio.
```

El argumento para no saltarse el paso 2: *«es "barato" borrar o reconstruir geometría rugosa de blockout, pero tirar
trabajo de arte ya terminado es "caro" y un desperdicio»*. Y un consejo que en 2D se traduce igual: durante el
playtest hay que *«caminar por el espacio, dentro del motor, con gravedad, colisión y velocidad completas del
jugador»* — nada de juzgar el nivel mirando el Room Editor con el zoom alejado.

**La caja gris en GameMaker es literal:** un tile set de 3-4 tiles de colores planos (suelo · pared · peligro ·
decorado) con el mismo tamaño de celda que el definitivo. El día del arte solo hay que cambiar el tile set de la capa
y repasar los autotiles.

### 2.4 Playtesting: qué se mira y qué no se pregunta

- **No expliques nada.** Cada vez que abres la boca estás parcheando el nivel con tu voz.
- **Apunta el reloj, no la opinión.** Dónde se paró, cuántas veces murió, en qué punto miró al suelo buscando la
  salida, dónde se rió. «Me pareció un poco largo» es un dato débil; treinta segundos de silencio delante de una
  puerta es un dato duro.
- **Tres jugadores bastan** para encontrar los fallos de legibilidad; para el equilibrio, más.
- **Instrumenta el nivel:** cuenta muertes por zona y vuélcalas con `show_debug_message()`.

### 2.5 Versionado de niveles

Un nivel es código: se versiona. Tres capas de defensa en GameMaker:

1. **Git sobre el proyecto.** Los `.yy` de las rooms son JSON: hacen *diff* razonablemente y se revierten. ⚠️ No los
   edites a mano —se corrompen—; usa el IDE o `gm-cli resourcetool eval`. Guía en [`03 · 24 — Control de versiones con Git`](../03%20-%20Cursos%20%28YouTube%29/24%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Control%20de%20Versiones%20con%20Git.md).
2. **Salas hijas como variantes** (§3.2): `rm_bosque_01` y su hija `rm_bosque_01_dificil` comparten todo salvo lo que
   desactives.
3. **Niveles como datos** (§3.9): si el nivel es un `.json`, el *diff* lo lee una persona **y un LLM**, y se edita sin
   abrir el IDE.

> 💡 Nombra las rooms por zona y número (`rm_bosque_01`), no por orden de creación. Y **no uses `room_get_name()` como
> identificador de guardado**: si renombras la room, rompes todas las partidas (ver Metroidvania §2).

### 2.6 Tipos de estructura

| Estructura | Forma | Cuándo | Coste | Receta |
|---|---|---|---|---|
| **Lineal** | Sarta de niveles | Plataformas, arcade, narrativo | Bajo | [`04 · 01`](../04%20-%20Recetas%20por%20género/01%20-%20Plataformas%202D.md) |
| **Hub** | Centro + radios | Progresión no lineal ligera | Medio | [`04 · 00`](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md) §5 |
| **Mundo abierto por zonas** | Zonas cosidas por bordes | Aventura, survival | Alto | [`04 · 09`](../04%20-%20Recetas%20por%20género/09%20-%20Survival%20y%20crafting.md) |
| **Metroidvania** | Grafo con gates | Exploración con habilidades | Alto | [`04 · 06`](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md) |
| **Procedural** | Generado por semilla | Rejugabilidad | Medio, se paga en validación | [`04 · 05`](../04%20-%20Recetas%20por%20género/05%20-%20Roguelike%20y%20generación%20procedural.md) · [`13 · 07`](./07%20-%20Generación%20procedural%20avanzada.md) |

**Híbrido, casi siempre.** Lo que mejor funciona es procedural *con piezas hechas a mano*: el generador ordena
habitaciones que un humano diseñó. En GameMaker eso tiene implementación directa con
[**GMRoomLoader**](https://github.com/GlebTsereteli/GMRoomLoader), que carga rooms como *prefabs* en tiempo de
ejecución y en cualquier posición ([`12 · 05`](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md) §2).

---

## 3 · Cómo se traduce a GameMaker

### 3.1 El Room Editor: lo que de verdad importa al diseñar

| Herramienta | Dónde | Por qué importa |
|---|---|---|
| **Rejilla del lienzo** | Barra superior, tecla `G` | Ponla al tamaño de celda de tu tile set, no a los 32 px por defecto. `Shift+G` alterna el ajuste |
| **Guías** | Arrastrando desde las reglas | Marca con guías el alto de salto y el alcance máximo: dejas de medir a ojo |
| **Bloqueo de capa** | Candado del editor de capas | Bloquea la de colisión mientras decoras. Ahorra horas |
| **Seleccionar de cualquier capa** | Tecla `P` mantenida | Tocar un prop sin cambiar de capa |
| **Orden de creación de instancias** | Menú Room | Si un controlador debe existir antes que el jugador, se arrastra arriba |
| **Código de creación de la room** | Propiedades de la room | Se ejecuta al entrar, *después* del Create de todas las instancias y *antes* de su Room Start. El sitio correcto para los parámetros del nivel |
| **Persistente** | Propiedades de la room | ⚠️ Con la room persistente, el código de creación **solo corre la primera vez** |

**Capas mínimas de un nivel serio**, de atrás hacia delante: `Fondo_Lejano` y `Fondo_Cercano` (Background, parallax
lento y medio) · `Tiles_Decorado` (sin colisión) · **`Tiles_Colision`** (el suelo real: esta es la que manda) ·
`Instancias` (jugador, enemigos, triggers, spawners) · `Tiles_Frente` (hojas y columnas que tapan al jugador) ·
`Efectos` (filtros de zona).

> ⚠️ En el Room Editor **solo cabe un tile map por capa de tiles**; en código sí puedes tener varios en la misma capa.
> Y la profundidad de capa va de **-16000 a 16000**: fuera de ese rango no se dibuja nada, aunque los eventos sigan
> corriendo.

### 3.2 Herencia de rooms: la plantilla de nivel

Es la función del Room Editor que más tiempo ahorra y la que menos gente usa. Una room hija es *«esencialmente un clon
del padre»* y **todo en ella está vinculado al padre**: si mueves un tile en el padre, se mueve en la hija. La
herencia se desactiva **selectivamente** por capa, por instancia, por elemento o por propiedad.

```
rm_base_vista → solo cámara, viewport y tamaño de celda
  └─ rm_base_juego → hereda la vista + controladores persistentes y HUD
       ├─ rm_bosque_01 → hereda todo; solo pinta tiles y coloca enemigos
       └─ rm_bosque_02, rm_bosque_03…
```

Cuando decidas que la cámara debe ser 20 px más ancha, lo cambias **una vez**. Para una variante difícil de un nivel:
clic derecho sobre la room → **Create Child Room**, y en la hija desactivas la herencia solo de la capa de instancias.
El orden y la herencia se reorganizan desde el **Room Manager**, no arrastrando en el Asset Browser.

> 🔺 **Trampa documentada:** *«si edita cualquier propiedad heredada, se desactivará automáticamente la herencia en la
> sección a la que pertenece»*. Tocas un tile de la hija «para probar» y esa capa deja de heredar para siempre. Revisa
> los botones de herencia antes de dar un nivel por bueno.

### 3.3 Tiles: tile set, autotiles y pinceles

El flujo paso a paso está en [`03 · 16`](../03%20-%20Cursos%20%28YouTube%29/16%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Editor%20de%20Rooms,%20Tiles%20y%20Tile%20Sets.md)
y [`03 · 17`](../03%20-%20Cursos%20%28YouTube%29/17%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Autotiles.md);
la API, en [`08 · 09`](../08%20-%20Referencia%20GML%20completa/09%20-%20Dibujo%20de%20tiles%20y%20tilemaps.md). Lo que
aporta este documento es **cuál usar y cuándo**:

| Herramienta | Qué resuelve | Cuándo |
|---|---|---|
| **Autotile de 16** | Dos terrenos que se tocan (hierba/tierra, tierra/vacío) | Siempre: el 90 % de los casos y el más barato de rellenar |
| **Autotile de 47** | Formas estrechas y muchas combinaciones | Solo si el de 16 deja esquinas feas. Exige muchos más tiles dibujados |
| **Brush Builder** | Grupos de tiles que se repiten (ventana, arco, valla) | Para no repintar la misma composición veinte veces: *«básicamente estás creando tiles usando tiles»* |
| **Baldosas animadas** | Agua, lava, antorchas | Los fotogramas van **dentro del tile set**, no como subimágenes |
| **Convertir imagen en mapa Tile** | Tienes el nivel pintado como imagen | Menú **Room**: importa un PNG/GIF/BMP, extrae los tiles únicos y crea el tile set y la capa |

⚠️ **La casilla vacía es siempre la de arriba a la izquierda** del tile set: reserva ese hueco. Y el consejo oficial
para colisiones: *«si usas un tile set así para colisiones, asigna el tile de arriba a la izquierda a la última
casilla gris de la plantilla, porque permite una detección de colisión más fácil (ya que el ID del tile devolvería 0,
el equivalente de false)»*.

> ⚠️ Los autotiles **no son accesibles desde código**: no hay función para «pinta aquí con el autotile X». Si generas
> niveles proceduralmente, el cálculo de bordes lo haces tú (bitmask de 4 u 8 vecinos) y lo escribes con
> `tilemap_set()`. Lo cubre [`13 · 07 — Generación procedural avanzada`](./07%20-%20Generación%20procedural%20avanzada.md).

### 3.4 Colisión de tiles: las dos vías

**Vía A — máscara del tile set.** El tile set tiene un sprite con máscara de colisión válida y **«Disable Source
Sprite Export» desactivado**; entonces el tile map se comporta como un sólido más y basta con pasar su handle
(`layer_tilemap_get_id("Tiles_Colision")`, cacheado en el Create) a `move_and_collide()` o a `place_meeting()`. El
detalle está en [`01 · 10`](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md) §4.

**Vía B — lectura de celdas.** Más control, y obligatoria si solo algunos tiles colisionan. El patrón oficial lee las
cuatro esquinas de la caja de colisión; debajo, cómo se leen los **tiles con propiedad** (lava, hielo, ruido):

```gml
/// @func comprobar_solido(_mapa, _dx, _dy)   ¿Hay tile sólido si me muevo (_dx, _dy)?
function comprobar_solido(_mapa, _dx, _dy)
{
    var _izq = bbox_left + _dx,  _der = bbox_right  + _dx;
    var _arr = bbox_top  + _dy,  _aba = bbox_bottom + _dy;
    return tilemap_get_at_pixel(_mapa, _izq, _arr) || tilemap_get_at_pixel(_mapa, _der, _arr)
        || tilemap_get_at_pixel(_mapa, _izq, _aba) || tilemap_get_at_pixel(_mapa, _der, _aba);
}

// (a) tile con propiedad, por índice — sencillo, se rompe si reordenas el tile set
if (tile_get_index(tilemap_get_at_pixel(mapa_solido, x, y + 1)) == IDX_LAVA) { recibir_dano(1); }

// (b) por los bits libres del blob de 32 bits (19-27: 9 bits tuyos por celda).
//     Sobrevive al reordenado, pero exige fijar tilemap_set_mask() para que no se
//     lean como índice. Detalle del blob y de la máscara en 01 · 10 §4.
#macro BIT_DANINO (1 << 19)
if (tilemap_get_at_pixel(mapa_solido, x, y + 1) & BIT_DANINO) { recibir_dano(1); }
```

> ⚠️ Si un tile es **más pequeño que la caja de colisión**, el personaje puede colarse entre las cuatro esquinas.
> Solución oficial: añadir comprobaciones en el punto medio de cada lado.

### 3.5 Parallax: decisiones de diseño

El código (`layer_x()` / `layer_y()` contra `camera_get_view_x()` en **End Step**) ya está en [`01 · 10`](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md) §3; aquí solo lo que decide el
diseñador. El parallax no es decoración: es **información de distancia** y hace legible la escala del nivel.

- **Tres capas bastan**: factores ~0.20 (lejos), ~0.55 (medio), 1.0 (el juego).
- **El factor de la capa más lejana casi nunca debe bajar de 0.1**: por debajo, el fondo parece pintado en el cristal
  y marea.
- **El *weenie* del §1.3 vive en la capa lejana**: es la silueta que se ve desde la entrada y a la que se llega al
  final. Si tu parallax no contiene ningún hito, es papel pintado.

### 3.6 Triggers y zonas: objetos invisibles

Un *trigger* es un objeto sin sprite visible que emite una señal al entrar el jugador. Es la pieza que convierte un
nivel bonito en un nivel **dirigido**: aquí empieza la música, aquí la cámara se aleja, aquí aparece el jefe.

```gml
/// obj_zona — Create
// Variable Definitions, por instancia en el Room Editor:
//   aviso (String) → señal a emitir · una_vez (Bool) → ¿solo la primera vez?
aviso = "musica_jefe";  una_vez = true;  disparada = false;
visible = false;            // invisible en juego, visible en el editor

/// obj_zona — Step
if (disparada && una_vez) { exit; }

if (place_meeting(x, y, obj_jugador))
{
    if (!disparada) { disparada = true; senal_emitir(aviso, { zona: id, px: x, py: y }); }
}
else if (!una_vez) { disparada = false; }   // rearmar al salir
```

`senal_emitir()` es la función de [`04 · 16 — Señales y desacoplamiento`](../04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md). Usarla en vez de
tocar variables ajenas permite que el mismo `obj_zona` sirva para la música, la cámara y el diálogo sin que el nivel
dependa de quién escucha.

> 💡 **Da tamaño al trigger con la escala en el Room Editor**, no creando veinte objetos: un sprite de 16×16 escalado a
> 8×3 es una zona de 128×48 en una sola instancia. Ponle un sprite de color chillón semitransparente: en juego está
> `visible = false`, en el editor lo ves.

### 3.7 Spawners: enemigos que aparecen cuando toca

```gml
/// obj_spawner — Create
// Variable Definitions: que_crear (Asset) · cuantos (0 = infinito) · cadencia (frames)
//                       dispersion (px) · distancia (px, radio de activación)
que_crear = obj_enemigo;  cuantos = 3;  cadencia = 45;
dispersion = 24;  distancia = 240;  creados = 0;  activo = false;  visible = false;

/// obj_spawner — Step
if (!instance_exists(obj_jugador)) { exit; }
var _lejos = point_distance(x, y, obj_jugador.x, obj_jugador.y) > distancia;

if (!activo && !_lejos)     { activo = true;  alarm[0] = 1; }   // primera, inmediata
else if (activo && _lejos)  { activo = false; alarm[0] = -1; }  // se apaga al alejarse

/// obj_spawner — Alarm 0
if (cuantos > 0 && creados >= cuantos) { exit; }
var _px = x + irandom_range(-dispersion, dispersion);
var _py = y + irandom_range(-dispersion, dispersion);
instance_create_layer(_px, _py, "Instancias", que_crear, { origen_spawner: id });
creados++;
alarm[0] = cadencia;
```

El quinto argumento de `instance_create_layer()` es un **struct de variables iniciales** que se aplican *antes* del
evento Create de la instancia nueva. Es la forma limpia de parametrizar enemigos desde el nivel sin crear un objeto
por variante.

### 3.8 Puntos de control con guardado

```gml
/// obj_arranque — Create  (una vez por partida)
global.control = { sala: rm_bosque_01, px: 64, py: 64, orden: -1 };

/// obj_checkpoint — Create      // Variable Definitions: orden (0, 1, 2… creciente)
orden = 0;

/// obj_checkpoint — Collision con obj_jugador
if (global.control.sala == room && global.control.orden >= orden) { exit; }

global.control = { sala: room, px: x, py: y - 8, orden: orden };
audio_play_sound(snd_checkpoint, 10, false);
partida_guardar();            // ← scr_save_load

/// obj_jugador — función de reaparición
function reaparecer()
{
    // si el checkpoint está en otra sala, el Room Start colocará al jugador allí
    if (room != global.control.sala) { room_goto(global.control.sala); exit; }
    x = global.control.px;  y = global.control.py;
    vel_x = 0;              vel_y = 0;
}
```

> ⚠️ La comprobación `global.control.orden >= orden` evita el bug clásico: volver atrás y **retroceder** el punto de control. El
> `orden` es un número creciente dentro del nivel, no la distancia.

El guardado en disco está resuelto en [`scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml) y en
[`01 · 14`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md).

### 3.9 Room como nivel · nivel como datos

| | **Room = nivel** | **Nivel = datos** |
|---|---|---|
| Dónde vive | En el `.yy` de la room | En un `.json` de *Included Files*, o generado |
| Se edita con | El Room Editor (autotiles, pinceles, guías) | LDtk, Tiled, un editor propio o código |
| Diff en Git | JSON del IDE, legible a duras penas | Legible por una persona **y por un LLM** |
| Modding · procedural | No · solo con GMRoomLoader | Sí, gratis · natural |
| Coste de arranque | Cero | Un cargador que escribir y depurar |

**Recomendación honesta:** empieza con *room = nivel*. Pasa a datos solo con una razón concreta (más de ~40 niveles,
modding, procedural, o un diseñador que no quiere abrir GameMaker). El flujo LDtk/Tiled → GameMaker, con sus trampas
reales, está en [`12 · 05`](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md) §2 y [`07 · 09`](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md) §4.

**Formato mínimo** si te lo montas tú:

```json
{ "version": 1, "nombre": "bosque_01", "celda": 16, "ancho": 60, "alto": 34,
  "capas": { "Tiles_Colision": [0, 0, 1, 1, 1, 0] },
  "entidades": [
    { "objeto": "obj_enemigo", "px": 320, "py": 208, "props": { "vida": 3 } },
    { "objeto": "obj_zona", "px": 640, "py": 160,
      "props": { "aviso": "musica_jefe", "una_vez": true } } ] }
```

Y el cargador completo:

```gml
/// scr_niveles — carga de niveles desde datos externos.
/// Se invoca desde el CÓDIGO DE CREACIÓN de la room:
///     var _n = nivel_leer(working_directory + "niveles/bosque_01.json");
///     if (!is_undefined(_n)) { nivel_pintar(_n, "Tiles_Colision"); nivel_poblar(_n, "Instancias"); }

/// @func   nivel_leer(_ruta)
/// @return struct con los datos, o undefined si no existe o está roto
function nivel_leer(_ruta)
{
    if (!file_exists(_ruta)) { show_debug_message($"[nivel] No existe: {_ruta}"); return undefined; }
    var _buf   = buffer_load(_ruta);
    var _texto = buffer_read(_buf, buffer_text);   // lee el buffer entero como string
    buffer_delete(_buf);

    var _datos = json_parse(_texto);
    if (!is_struct(_datos) || !variable_struct_exists(_datos, "version"))
    {
        show_debug_message($"[nivel] Formato inválido: {_ruta}");
        return undefined;
    }
    return _datos;
}

/// @func nivel_pintar(_datos, _nombre_capa)
/// @desc Vuelca un array de índices de tile en el tile map de una capa.
function nivel_pintar(_datos, _nombre_capa)
{
    var _mapa = layer_tilemap_get_id(_nombre_capa);
    if (_mapa == -1) { return false; }
    var _celdas = struct_get(_datos.capas, _nombre_capa);
    if (!is_array(_celdas)) { return false; }

    var _ancho = _datos.ancho, _alto = _datos.alto;
    tilemap_set_width(_mapa, _ancho);
    tilemap_set_height(_mapa, _alto);
    for (var _fila = 0; _fila < _alto; _fila++)
    {
        for (var _col = 0; _col < _ancho; _col++)
        {
            tilemap_set(_mapa, _celdas[_fila * _ancho + _col], _col, _fila);
        }
    }
    return true;
}

/// @func   nivel_poblar(_datos, _nombre_capa)
/// @return cuántas entidades se crearon
function nivel_poblar(_datos, _nombre_capa)
{
    if (!variable_struct_exists(_datos, "entidades")) { return 0; }
    var _lista = _datos.entidades, _hechas = 0;

    for (var _k = 0; _k < array_length(_lista); _k++)
    {
        var _ent = _lista[_k];
        var _obj = asset_get_index(_ent.objeto);
        if (_obj == -1)
        {   // el nivel se carga igual: cojo, pero jugable
            show_debug_message($"[nivel] Objeto desconocido: {_ent.objeto}");
            continue;
        }
        var _props = variable_struct_exists(_ent, "props") ? _ent.props : {};
        instance_create_layer(_ent.px, _ent.py, _nombre_capa, _obj, _props);
        _hechas++;
    }
    return _hechas;
}
```

> 💡 **El camino intermedio que casi nadie conoce:** `room_get_info()` devuelve una room como struct —tamaño, capas,
> elementos y hasta los datos del tile map— sin salir de GameMaker. Sirve para *exportar* a datos niveles hechos en el
> Room Editor: `var _info = room_get_info(rm_bosque_01, false, true, true, true, true, false);`

### 3.10 Un editor de niveles dentro del juego

Treinta líneas y tienes la iteración más rápida posible: pintar mientras juegas. Convierte «compilar para probar un
cambio de tile» en «pintar y ver».

```gml
/// obj_editor — Create
mapa = layer_tilemap_get_id("Tiles_Colision");
pincel = 1;  encendido = false;  ruta = working_directory + "nivel_editado.json";

/// obj_editor — Step
if (keyboard_check_pressed(vk_f2)) { encendido = !encendido; }
if (!encendido) { exit; }
if (mouse_wheel_up())   { pincel++; }
if (mouse_wheel_down()) { pincel = max(0, pincel - 1); }

// mouse_x / mouse_y están en coordenadas de la ROOM: justo lo que pide *_at_pixel
if (mouse_check_button(mb_left))  { tilemap_set_at_pixel(mapa, pincel, mouse_x, mouse_y); }
if (mouse_check_button(mb_right)) { tilemap_set_at_pixel(mapa, 0,      mouse_x, mouse_y); }

if (keyboard_check_pressed(vk_f5)) { editor_guardar(ruta); }
if (keyboard_check_pressed(vk_f9))
{
    var _d = nivel_leer(ruta);
    if (!is_undefined(_d)) { nivel_pintar(_d, "Tiles_Colision"); }
}

/// obj_editor — Draw GUI
if (encendido) { draw_text(8, 8, $"EDITOR · pincel {pincel} · F5 guardar · F9 cargar · F2 salir"); }
```

Añade en el evento **Draw** una retícula sobre la celda apuntada —`tilemap_get_cell_x_at_pixel()` y
`tilemap_get_cell_y_at_pixel()` por `tilemap_get_tile_width()` / `tilemap_get_tile_height()`, y un
`draw_rectangle()` sin relleno— y sabrás siempre dónde vas a pintar. Y `editor_guardar()` es el bucle inverso de
`nivel_pintar()`: recorre las celdas con `tilemap_get()`, se queda con `tile_get_index()` de cada una —que descarta
los bits de flip/mirror/rotate—, arma el struct del §3.9 y lo escribe con `json_stringify()` +
`file_text_open_write()` / `file_text_write_string()` / `file_text_close()`.

> ⚠️ `working_directory` **no es la carpeta del proyecto**: es el sandbox de la aplicación. El `.json` que guardes ahí
> no aparece en tu repositorio; hay que copiarlo a mano. Es una herramienta de iteración, no un pipeline de
> producción.

### 3.11 Medir las métricas de salto en código

Las fórmulas analíticas dan el orden de magnitud; la simulación da el número con el que se construye. Con la
integración por frames que usa GameMaker (`vel_y += grav;  y += vel_y;`), `t_subida ≈ v0 / g_sube` frames y
`altura ≈ v0² / (2·g_sube) + v0/2` píxeles. Con las constantes de
[`04 · 01 Plataformas 2D`](../04%20-%20Recetas%20por%20género/01%20-%20Plataformas%202D.md) (`JUMP_SPEED = 11`,
`GRAV_RISE = 0.45`, `GRAV_FALL = 0.62`) la fórmula da **139,9 px**… y la simulación real, **129,0 px**. Ocho por
ciento: **casi una celda entera de 16 px**. Por eso las métricas se miden, no se calculan.

```gml
/// scr_metricas — mide el salto reproduciendo la MISMA integración que el jugador
#macro TAM_CELDA 16

/// @func   medir_salto(_v0, _grav_sube, _grav_baja, _vel_terminal, _vel_horizontal)
/// @desc   Simula un salto completo hasta volver a la altura de partida.
/// @return struct { alto_px, alto_celdas, frames_aire, alcance_px, alcance_celdas }
function medir_salto(_v0, _grav_sube, _grav_baja, _vel_terminal, _vel_horizontal)
{
    var _vy = -_v0;                             // negativo = hacia arriba
    var _altura = 0, _cima = 0, _frames = 0;

    do
    {
        _vy += (_vy < 0) ? _grav_sube : _grav_baja;
        _vy  = min(_vy, _vel_terminal);
        _altura -= _vy;                         // Y crece hacia abajo en pantalla
        _cima    = max(_cima, _altura);
        _frames++;
    }
    until (_altura <= 0 || _frames > 600);      // el 600 evita colgarse si la gravedad es 0

    var _alcance = _vel_horizontal * _frames;
    return { alto_px: _cima,   alto_celdas: _cima / TAM_CELDA,   frames_aire: _frames,
             alcance_px: _alcance, alcance_celdas: _alcance / TAM_CELDA };
}
```

Y la hoja de métricas dibujada sobre el propio juego, para no tener que creerse los números:

```gml
/// obj_metricas — Create   (en rm_metricas y en cualquier nivel mientras diseñas)
largo = medir_salto(11.0, 0.45, 0.62, 14.0, 4.0);   // botón mantenido
corto = medir_salto(11.0, 0.90, 0.62, 14.0, 4.0);   // botón soltado enseguida

/// obj_metricas — Draw   (la banda jugable, dibujada en el mundo sobre el jugador)
if (!instance_exists(obj_jugador)) { exit; }
draw_set_alpha(0.35);
draw_set_colour(c_lime);   // techo alcanzable
draw_line(obj_jugador.x - 64, obj_jugador.y - largo.alto_px,
          obj_jugador.x + 64, obj_jugador.y - largo.alto_px);
draw_set_colour(c_red);    // abismo máximo
draw_line(obj_jugador.x, obj_jugador.y, obj_jugador.x + largo.alcance_px, obj_jugador.y);
draw_set_alpha(1);  draw_set_colour(c_white);

/// obj_metricas — Draw GUI
// ⚠️ Los template strings de GML NO admiten formato dentro de las llaves: `{v:0.00}` es un
//    error de sintaxis. Los decimales se fijan con string_format().
draw_text(8, 8, $"LARGO {string_format(largo.alto_celdas, 1, 2)} alto ·"
              + $" {string_format(largo.alcance_celdas, 1, 2)} alcance (celdas)\n"
              + $"CORTO {string_format(corto.alto_celdas, 1, 2)} alto ·"
              + $" {string_format(corto.alcance_celdas, 1, 2)} alcance (celdas)");
```

Con esos dos números —**8,06 celdas de alto y 11,25 de alcance** en el ejemplo— ya se pueden escribir las reglas de
construcción del juego:

| Regla | Valor | Por qué |
|---|---|---|
| Obstáculo franqueable | ≤ 6 celdas | 8 es el máximo teórico; 2 de margen o el salto se siente injusto |
| Obstáculo infranqueable | ≥ 10 celdas | Que se vea claramente imposible, no «casi» |
| Abismo normal | ≤ 8 celdas | El máximo es 11; a 11 solo entra el salto perfecto |
| Abismo de examen | 10-11 celdas | Solo en la fase *ketsu*, y con checkpoint cerca |
| Techo de túnel | alto del jugador + 1 | Para que no se enganche al saltar sin querer |

---

## 4 · La hoja de nivel: la plantilla que se rellena ANTES de construir

Este es el entregable que un LLM debe producir **antes** de tocar el Room Editor. Cabe en una pantalla y evita el 80 %
de los niveles que hay que tirar.

```markdown
# Nivel: <id> — <nombre>
**Zona:** <bosque | torre | cripta>   **Posición en el arco:** <n> de <total>
**Duración objetivo:** <minutos>      **Dificultad objetivo:** <1-5>
## 1. La idea (una frase)
Este nivel enseña: ____________________________________________
## 2. Los cuatro momentos
| Fase | Qué pasa | Dónde (coordenada o beat) | Intensidad 0-5 |
|---|---|---|---|
| Introducir | | | |
| Desarrollar | | | |
| Torcer | | | |
| Concluir | | | |
## 3. Métricas usadas   (hoja versión ____)
- Alto de salto ____ celdas · Alcance ____ celdas
- Obstáculo máximo aquí ____ celdas · Abismo máximo aquí ____ celdas
## 4. Ruta y espacio
- Ruta crítica, de entrada a salida, en una línea: ___________________
- Punto de referencia visible desde la entrada: ______________________
- Rutas opcionales: ____ (riesgo / recompensa) · Secretos: ____ (¿se intuyen?)
- Atajo de vuelta: sí / no · ¿desde dónde se abre? ___________________
## 5. Elementos
| Tipo | Cuántos | Notas |
|---|---|---|
| Enemigos | | ¿alguno nuevo? |
| Gates | | tipo y llave |
| Checkpoints | | separación en segundos |
| Triggers · coleccionables | | qué señal emite cada trigger |
## 6. Reutilización y riesgos
- Tiles, pinceles o prefabs que ya existen y voy a reusar: ____________
- Room base de la que hereda: ________________________________________
- Lo que puede salir mal, y cómo lo compruebo en el playtest: _________
```

---

## 5 · Checklist de revisión

**Antes de pasarlo a arte:**

- [ ] Se puede terminar, alguien que no eres tú lo ha terminado, y **sin explicaciones**.
- [ ] La idea del nivel cabe en una frase y tiene sus cuatro momentos.
- [ ] Ningún salto excede la métrica declarada para este nivel.
- [ ] No hay callejones sin salida silenciosos: todo camino lleva a algo, o se ve que no.
- [ ] Desde la entrada se ve un punto de referencia hacia el que ir.
- [ ] Lo interactivo se distingue del decorado en escala de grises.
- [ ] La cámara ve el peligro **antes** de que pueda matarte: no hay caídas ciegas.
- [ ] Los checkpoints están donde el jugador se atasca, no cada X metros.
- [ ] Se puede volver atrás desde cualquier punto, o está claro que no se puede.
- [ ] La intensidad sube y baja: no es todo pico ni todo valle.

**Antes de darlo por terminado:**

- [ ] Funciona con teclado **y** con mando.
- [ ] Nada depende de un `instance_exists()` que no compruebas.
- [ ] Los triggers de una sola vez no se re-disparan al volver.
- [ ] Se ve bien a la resolución mínima soportada: nada crítico fuera de la vista.
- [ ] Las capas de colisión no tienen tiles decorativos, ni al revés.
- [ ] La room hereda de la base correcta y no se le rompió la herencia sin querer.
- [ ] Los tiles de frente no tapan nada que el jugador necesite ver.
- [ ] `gm-cli compile` sale limpio y el nivel se ha jugado entero tras compilar.

---

## 6 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| **Diseñar antes de tener métricas** | Al ajustar el salto se rompen todos los niveles | Hoja de métricas y `rm_metricas` **primero** |
| **Arte antes de aprobar la caja gris** | No te atreves a mover una plataforma porque «ya está bonita» | Caja gris con 4 tiles planos; el arte al final |
| **Un nivel que enseña tres cosas** | El jugador no recuerda ninguna | Una idea por nivel, y se tira al acabar |
| **Métrica al límite** | El salto solo entra si es perfecto: se percibe injusto | Deja 2 celdas de margen salvo en la fase de examen |
| **Muerte por caída ciega** | El jugador salta y muere sin haber podido saberlo | Sube la cámara o pon una plataforma de aviso |
| **Simetría perfecta** | El jugador se desorienta: todo se parece | Rompe la simetría; un punto de referencia único por zona |
| **Explicar el gate con texto** | Se pierde el descubrimiento | El gate se sacude o suena; no dice qué falta |
| **Checkpoints cada X metros** | Repetir tramos ya dominados | Ponlos donde el playtest muestra que la gente muere |
| **Editar `.yy` de rooms a mano** | Proyecto corrupto, room que no abre | IDE, MCP `gamemaker-resource-tool` o `gm-cli resourcetool eval` |
| **Romper la herencia sin darse cuenta** | Un cambio en la room base no llega a las hijas | Repasa los botones de herencia antes de cerrar el nivel |
| **Tile decorativo en la capa de colisión** | Suelo invisible, muros fantasma | Capa de colisión con solo tiles sólidos; bloquéala mientras decoras |
| **Comparar un ID de tile map con `false`** | Colisiones que fallan cuando el tile map tiene ID 0 | Compara contra `noone`; usa `tile_get_index()` para leer índices |
| **`room_get_name()` como ID de guardado** | Renombras una room y rompes todas las partidas | Un identificador propio que no cambia nunca |
| **Esperar autotiles desde código** | «¿Por qué no puedo pintar autotiles por GML?» | No se puede: calcula el bitmask de vecinos y usa `tilemap_set()` |

---

## Ver también

- [`01 · 10 — Rooms, capas, cámaras y viewports`](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md) — la API completa de rooms, capas, tile maps, parallax y cámaras
- [`04 · 00 — Anatomía de un juego completo`](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md) — dónde encajan los niveles en el arco del juego
- [`04 · 01 — Plataformas 2D`](../04%20-%20Recetas%20por%20género/01%20-%20Plataformas%202D.md) — de dónde salen las constantes de salto y la cámara con *deadzone*
- [`04 · 05 — Roguelike y generación procedural`](../04%20-%20Recetas%20por%20género/05%20-%20Roguelike%20y%20generación%20procedural.md) · [`13 · 07 — Generación procedural avanzada`](./07%20-%20Generación%20procedural%20avanzada.md) — cuando el nivel lo construye el algoritmo
- [`04 · 06 — Metroidvania`](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md) — gates, llaves, estado del mundo, transiciones entre rooms
- [`04 · 15 — Game feel y juice`](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) · [`04 · 16 — Señales y desacoplamiento`](../04%20-%20Recetas%20por%20género/16%20-%20Señales%20y%20desacoplamiento.md) — el tacto, y `senal_emitir()` para los triggers
- [`07 · 09 — Asset packs y recursos gráficos`](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md) §4 · [`12 · 05 — Pipeline de arte, audio y niveles`](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md) — Tiled, LDtk, GMRoomLoader, Hotglue
- [`08 · 09 — Dibujo de tiles y tilemaps`](../08%20-%20Referencia%20GML%20completa/09%20-%20Dibujo%20de%20tiles%20y%20tilemaps.md) — referencia de la familia `tilemap_*`
- [`03 · 16 — Editor de Rooms, Tiles y Tile Sets`](../03%20-%20Cursos%20%28YouTube%29/16%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Editor%20de%20Rooms,%20Tiles%20y%20Tile%20Sets.md) · [`03 · 17 — Autotiles`](../03%20-%20Cursos%20%28YouTube%29/17%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Autotiles.md)
- [`05 · 04 — Convenciones y estilo GML`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) — nombres de rooms, capas y objetos

---

## Fuentes

Consultadas el **6 de septiembre de 2026**.

**Diseño de niveles**

- **Level Design Book** (Robert Yang y colaboradores), el manual abierto de referencia:
  [proceso](https://book.leveldesignbook.com/process) · [caja gris](https://book.leveldesignbook.com/process/blockout)
  · [métricas](https://book.leveldesignbook.com/process/blockout/metrics) · [*wayfinding* y Kevin Lynch](https://book.leveldesignbook.com/process/blockout/wayfinding) · [ritmo y beats](https://book.leveldesignbook.com/process/preproduction/pacing)
- **Dan Taylor, «Ten Principles of Good Level Design»** (GDC 2013), en dos partes en Game Developer, 29-09-2013 y
  06-10-2013: [parte 1](https://www.gamedeveloper.com/design/ten-principles-of-good-level-design-part-1-) · [parte 2](https://www.gamedeveloper.com/design/ten-principles-of-good-level-design-part-2-) ·
  [charla](https://www.gdcvault.com/play/1017803/Ten-Principles-for-Good-Level)
- **Kishōtenketsu / Nintendo**: «The secret to Mario level design», Game Developer, entrevista a **Koichi Hayashida**
  (director de *Super Mario 3D Land* y *Super Mario Galaxy 2*):
  <https://www.gamedeveloper.com/design/the-secret-to-i-mario-i-level-design>. ⚠️ Divulgación secundaria útil como
  resumen: *Game Maker's Toolkit*, «Super Mario 3D World's 4 Step Level Design» (Mark Brown, 2015).
- **Maddy Thorson, «Level Design Workshop: Designing Celeste»** (GDC 2017): el modelo de sala única con muerte casi
  gratuita: <https://www.youtube.com/watch?v=4RlpMhBKNr0>
- **Christopher W. Totten, *An Architectural Approach to Level Design*, 2.ª ed.**, CRC Press / A K Peters, 2019 (ISBN
  978-0815361367): *prospect and refuge*, espacios de recompensa, comunicación visual. ⚠️ La ficha del editor devolvió
  HTTP 403 el día de consulta; edición, ISBN y contenidos (cap. 5, «Prospect and Refuge Spatial Design») proceden de
  catálogos secundarios (Google Books, VitalSource, AbeBooks), **no** de la página del editor.

**GameMaker (fuentes primarias)**

- Manual oficial LTS 2026: [**El editor de Room**](https://manual.gamemaker.io/lts/es/The_Asset_Editors/Rooms.htm)
  (capas, rejilla, guías, orden de creación, «Convertir imagen en mapa Tile») · [**Herencia de rooms**](https://manual.gamemaker.io/lts/es/The_Asset_Editors/Room_Properties/Room_Inheritance.htm) · [**Propiedades de la room**](https://manual.gamemaker.io/lts/es/The_Asset_Editors/Room_Properties/Room_Properties.htm)
  (persistencia, código de creación, borrar el búfer de pantalla), y las páginas de `room_get_info`,
  `tilemap_set_at_pixel`, `layer_tilemap_get_id` y `buffer_read`. Espejos locales:
  [`Rooms.md`](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Rooms.md) ·
  [`Room_Inheritance.md`](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Room_Properties/Room_Inheritance.md)
- **Blog oficial, «A Practical Guide To Using Tiles in GameMaker»** (Gurpreet S. Matharoo, 13-05-2021): Tile Set
  Editor, autotiles de 16 y 47, Brush Builder, baldosas animadas y `tilemap_get_at_pixel()` en las cuatro esquinas de
  la caja de colisión: <https://gamemaker.io/en/blog/practical-guide-tiles>
- **Blog oficial, «Expanding Worlds: Building Games With Interconnected Levels»** (Gurpreet S. Matharoo, 12-08-2021):
  objetos de entrada/salida, gestor de rooms persistente, guardado del estado de la room y transición con fundido:
  <https://gamemaker.io/en/blog/multiple-levels-tutorial>

**Verificación** · Todos los símbolos de GML de este documento se comprobaron con `python3 "_indice/buscar.py"
<símbolo>` contra el `GmlSpec.xml` del runtime **2026.0.0.23**. Las funciones de los ejemplos que **no** son del
runtime —`medir_salto`, `nivel_leer`, `nivel_pintar`, `nivel_poblar`, `editor_guardar`, `comprobar_solido`,
`reaparecer`, `recibir_dano`, `partida_guardar`, `senal_emitir`— son código de esta biblioteca. Los números del §3.11
salen de ejecutar la simulación de `medir_salto()` con las constantes de la receta 01, no de una estimación.
