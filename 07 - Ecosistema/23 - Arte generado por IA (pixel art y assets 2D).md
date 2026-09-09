# 23 · Arte generado por IA (pixel art y assets 2D)

> Este documento trata la IA como **generadora de imágenes**, no como programadora. Para IA
> como agente de código sobre este mismo proyecto (MCP, `gm-cli --ai`, `GMEXT-MLKit`), ver
> [14 · IA y GameMaker](./14%20-%20IA%20y%20GameMaker.md) — son dos preguntas distintas y este
> documento no repite aquella. Tampoco repite el porqué estructural de que un generador de
> imágenes no produce pixel art de verdad (rejilla, paleta, sel-out): eso está resuelto en
> [13 · 03 §7.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/03%20-%20Pixel%20art%20y%20resolución.md#72-ia-referencia-sí-resultado-no)
> y aquí se enlaza, no se repite. Lo que sí cubre este documento: **qué sirve de verdad para
> arte de juego en general (no solo pixel art)**, **por qué la consistencia es el problema real**
> —con las técnicas que existen para paliarla— y **el estado legal**, verificado con fuentes
> primarias con fecha, no por intuición.
>
> **Hueco detectado** por la auditoría `r3-arte-animacion.md`: el único documento con «IA» en el
> título de esta biblioteca trataba la IA exclusivamente como programadora.

---

## 1 · Qué sirve hoy de verdad

La pregunta útil no es «¿es buena la IA generativa?», sino «¿en qué punto del pipeline el
resultado no necesita ser el asset final?». Ahí es donde funciona:

| Uso | Por qué funciona | Ejemplo concreto |
|---|---|---|
| **Hojas de referencia y moodboards** | No hay que ser consistente con nada todavía | «Dame 6 variantes de un mago enano con sombrero cónico» antes de que el artista dibuje el diseño definitivo |
| **Exploración de paleta y composición** | El objetivo es descartar el 90 %, no quedarte con el resultado | Probar 20 combinaciones de color de un escenario antes de pintarlo a mano |
| **Upscalers de imagen sobre arte YA terminado, a resolución alta** | El upscaler interpola detalle sobre una imagen que **ya tiene** intención artística — no inventa forma nueva desde ruido | Ampliar una ilustración de menú, una portada o un retrato de diálogo pintado a mano que necesitas a más resolución de la que se dibujó. Herramientas: Real-ESRGAN, Topaz Gigapixel, waifu2x |
| **Texturas orgánicas sin silueta que leer** | No hay una forma reconocible que deba mantenerse coherente entre usos | Ruido de roca, tierra, tela genérica, como punto de partida para retocar a mano en un material tileable |
| **Retratos puntuales sin animar** | Una sola imagen por personaje, sin necesidad de que cuadre con otras 40 | Un busto de diálogo en una visual novel, si el juego declara su uso (§4) |
| **Fondos muy lejanos, siempre desenfocados** | Nunca se ven a tamaño real ni de cerca — ya cubierto en 13 · 03 §7.2 | La capa de parallax más al fondo de todas |

### 1 bis · Pixel art por IA de verdad: Retro Diffusion y el pipeline de Astropulse

> ❌ **Corrección del 09-09-2026, en el mismo día.** La primera versión de esta sección despachó
> todo esto como «de pago y alojado, por debajo de la escalera de placeholders». **Es falso para
> más de la mitad.** La *generación* se paga por créditos, sí; pero las herramientas de
> **reparación y conversión** —que son las que más falta le hacen a un agente— son **MIT, de
> procesado de imagen puro, sin modelo, sin clave y sin cuenta**. Lo mismo el tramado, los mapas
> normales y el troceado de hojas de sprites.

Todo lo de §1 habla de modelos **generales** (Stable Diffusion, Midjourney) y su conclusión sigue
en pie para ellos. Pero existe una familia entrenada **solo en pixel art** —**Retro Diffusion**,
de Astropulse— y, alrededor, un pipeline abierto que resuelve problemas que esta biblioteca ya
documentaba sin dar solución.

#### Lo que puedes usar HOY sin cuenta ni clave

| Herramienta | Qué resuelve | Requisitos |
|---|---|---|
| **`pixel-art-fixer`** (383 ★, MIT) | Convierte pixel art **falso** —el que sale de un generador o de un upscaler: píxeles fuera de rejilla, bordes emborronados, escala no entera, archivo a 10× de su resolución real— en pixel art **real y alineado**. Su propio README lo dice: *«Image processing only, no model required»* | Ninguno externo |
| **`pixeldetector`** (357 ★, MIT) | **Repara** pixel art dañado por reescalado o por haberse guardado en JPEG, y lo devuelve a su resolución verdadera | Pillow, Numpy, Scipy |
| **`K-Centroid-Aseprite`** (28 ★, MIT) | Reducción de escala por k-medias: conserva los bordes duros donde un remuestreo normal los destroza | — |
| **`hitherdither`** (MIT) | Tramado para paletas arbitrarias, **en PIL** | Pillow |
| **`spritesplitter`** (10 ★, MIT) | Parte una hoja de sprites en imágenes sueltas por relleno por difusión, sin rejilla fija | Pillow |
| **`shadow-projector`** (15 ★, MIT) | Proyecta la sombra de un sprite con fondo transparente | — |
| **`Material-Map-Generator`** (Apache-2.0) | Genera **mapas normales** y de desplazamiento desde una textura | — |
| **`mixamotoopenpose`** (114 ★, MIT) | Convierte animaciones de Mixamo en secuencias OpenPose: poses exactas para guiar la generación con ControlNet | — |

Todas en `11 - Código descargado/herramientas/pixel-art-ia/`.

> 🔑 **`pixel-art-fixer` cierra un agujero que esta biblioteca tenía abierto.** El flujo de assets
> de un agente —generar la imagen con el modelo que sea y meterla en el juego— produce
> justamente eso: algo que *parece* pixel art y no lo es, con la rejilla corrida. `13 · 03 §7`
> avisaba del problema y no daba salida; ahora la hay, y es local. **Pásale por él cualquier
> imagen generada antes de convertirla en sprite.**

> 🔴 **Pero solo a lo generado, y eso hay que MEDIRLO antes.** «Pásale cualquier imagen» aplicado
> literalmente destruye el pixel art dibujado a 1:1: sobre un sprite real de 16×20,
> `pixel-art-fixer` lo declaró una imagen de 6×7 ampliada ×2,5 y `pixeldetector` lo redujo a
> 4×10. La herramienta no falla —busca la rejilla oculta de una imagen ampliada, que es su
> trabajo—; lo que falta es la puerta de delante:
>
> ```bash
> python3 "$BIB/_indice/puerta-pixel-art.py" <carpeta de PNG>
> ```
>
> Sale con 0 si no hay nada que reparar y con 1 diciendo qué PNG lo piden y por qué. Los tres
> criterios y por qué se exigen **a la vez**, en
> [`12 · 09 §5.2` peldaño 2 bis](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md).

> ⚠️ **La CLI de `pixel-art-fixer` está rota.** `python -m pixelfixer.cli entrada.png` —la orden
> que anuncia su propio README— muere con `ModuleNotFoundError: No module named 'detector'`:
> el paquete se renombró y `cli.py` sigue importando el nombre viejo en sus tres sitios.
> **La API sí funciona**: `from pixelfixer import detect` y
> `from pixelfixer.reconstruct import reconstruct`.

#### Lo que sí es de pago: la generación

El modelo de **Retro Diffusion** se llama por API con créditos. Lo que aporta frente a un modelo
general:

- **La rejilla es el espacio de trabajo, no un posprocesado.** Emite píxeles discretos en vez de
  ilustrar y pixelar después, que es de donde salen los bordes sucios y las paletas de 200
  colores.
- **Sabe qué es una hoja de sprites**: genera vistas por dirección y ciclos de animación como
  formato de salida.
- Alrededor hay utilidades del mismo autor que la usan: `tilesetbuilder` (tilesets desde dos
  texturas), `expression-generator` (expresiones de un personaje ya dibujado) y
  `stable-diffusion-aseprite` (dentro de Aseprite).

**Qué NO cambia**, y por eso el resto del documento sigue en pie: la **consistencia entre
generaciones** sigue sin resolverse (§3), y el **estado legal es idéntico** (§4) — que el modelo
sea específico no altera la posición de la U.S. Copyright Office ni la obligación de declararlo
en Steam e itch.io.

##### La alternativa que sí conoce GameMaker: MagicPixel

Medido el **2026-09-09** en el registro de npm y en su propia web, no de oído:

| Qué | Dato |
|---|---|
| CLI | [`@magicpixelart/cli`](https://www.npmjs.com/package/@magicpixelart/cli) v0.5.20 (2026-08-27), **MIT**, ~101 descargas/semana |
| Servicio | <https://magicpixel.art> — generador de pixel art por IA con editor en el navegador |
| Precio | **De pago.** El editor es gratis; generar cuesta créditos: 10 $/mes (200), 20 $/mes (450), 50 $/mes (1200), o 20 $ sueltos por 400. Prueba de **1 día** con 32 créditos |
| Propiedad de lo generado | Sus términos (`magicpixel.art/tos`, §5, leídos el 2026-09-09): «*You retain full ownership of all content you upload, import, create, or generate using the Service, including AI-generated outputs. MagicPixel does not claim ownership*» |
| Debajo | **Google AI** — sus términos dicen que también te obligan los de ese tercero |

**Lo que aporta y nadie más de esta sección tiene**: su CLI **detecta el proyecto por el
`*.yyp`** —GameMaker está en su lista junto a Unity, Godot y proyectos JS— y sincroniza los
assets a disco como PNG aplanados. Y expone un **servidor MCP**, así que el agente puede pedirle
el sprite él mismo en vez de que lo hagas tú a mano.

> ⚠️ **Tres cosas que hay que decir antes de que alguien pague.** (1) Sincronizar PNG a la
> carpeta **no** los convierte en sprites del proyecto: hay que registrarlos con
> `resourcetool`, que es justo lo que hace `_indice/atlas-a-gamemaker.py`. (2) Su repositorio
> del CLI tiene **0 estrellas** — es un canal de distribución de un producto, no un proyecto con
> comunidad detrás; si mañana cierra el servicio, el CLI no sirve de nada. (3) Que ellos no
> reclamen la propiedad **no resuelve el §4** de este documento: la posición de la U.S.
> Copyright Office sobre lo generado por IA y la obligación de declararlo en Steam e itch.io son
> las mismas.

> 🔎 **Hay un servidor MCP oficial** (`retro-diffusion-mcp`, MIT): permite pedir sprites desde
> Claude, Cursor o cualquier cliente MCP, que es exactamente cómo lo usaría un agente. Medido el
> 09-09-2026: es del **02-09-2026 y tiene 3 estrellas**. Existe y es la vía natural; no está
> rodado. Pruébalo antes de depender de él.
>
> 💡 Y hay un **banco de pruebas abierto** —`pixel-bench`, MIT— para medir cuánto se parece una
> reconstrucción al original. Si vas a comparar herramientas en vez de fiarte del ojo, empieza
> ahí.

**El upscaler es el caso que más se malinterpreta.** Un upscaler de imagen general
(Real-ESRGAN, Gigapixel) funciona razonablemente bien sobre **ilustración** —líneas suaves,
degradados, pintura digital— porque su trabajo es «adivinar detalle plausible entre píxeles
vecinos parecidos». Sobre **pixel art**, esa misma operación es destructiva: cada píxel de
pixel art es una decisión deliberada, no una aproximación de algo más detallado, así que
«mejorar el detalle» rompe exactamente lo que hace que sea pixel art. Hay upscalers
específicos entrenados para pixel art (que intentan mantener bordes duros y paleta), pero
incluso esos producen artefactos en formas complejas y **hay que revisar cada resultado a
tamaño real**, no confiar a ciegas. Hoy no sustituyen redibujar a mano.

---

### 1 bis.2 · `sprite-gen`: la tubería que un agente puede conducir entera

[`sprite-gen`](https://github.com/aldegad/sprite-gen) (817 ★, **Apache-2.0**, tocado el
09-09-2026) es a la vez **skill de Codex/Claude y CLI de Python**, y de un solo dibujo base
produce una hoja con alfa real y un `manifest.json` con los **rectángulos absolutos** de cada
fotograma, por estado, con `fps` y `loop`.

Frente a lo de arriba: Retro Diffusion (§1 bis) **genera píxeles**; `sprite-gen` **construye el
asset** — filas por estado, identidad del personaje bloqueada entre fotogramas, croma a alfa de
verdad, rejilla mantenida, y un manifiesto que el motor consume sin adivinar. Se complementan:
puedes generar con lo uno y montar con lo otro.

Lo que **no** trae es la salida a GameMaker —exporta a Aseprite, Phaser y Flame—, y eso lo cierra
`_indice/atlas-a-gamemaker.py`, verificado importando en un proyecto real. Los comandos y la
comprobación completa, en
[`12 · 09 §5.2`, peldaño 2 ter](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md).

### 1 ter · `SpriteBrew`: la tubería más pulida, y por qué aquí sirve solo a medias

[`SpriteBrew`](https://github.com/GAlbanese09/spritebrew) (52 ★, AGPL-3.0, activo a julio de
2026) es hoy el flujo más completo de hoja de sprites del ecosistema: texto → personaje →
animación → troceado → previsualización → **exportación lista para GameMaker**, con 21 estilos y
un modo «anima mi personaje» que parte de tu propio dibujo.

**Y aquí viene la letra pequeña, que es la que importa:**

- **La generación por IA es de pago y hospedada.** Funciona por *tokens* en `spritebrew.com`
  (cuenta gratuita con 5 para empezar; packs desde 4,99 $), no en tu máquina.
- **Por debajo llama a los modelos de Retro Diffusion por API.** Es decir: es un frontal bonito
  sobre lo mismo que [§1 bis](#1-bis--pixel-art-por-ia-de-verdad-retro-diffusion-y-el-pipeline-de-astropulse)
  ya te deja ejecutar **en local y sin cuenta**. Si tienes montado ese pipeline, la generación de
  SpriteBrew no te aporta nada que no tengas.
- **Lo que sí aporta gratis y sin cuenta** son sus herramientas de tubería, que no usan IA:
  trocear una hoja de sprites (con detección por contorno para rejillas irregulares), vista
  previa de la animación, editor de píxeles, redimensionado *pixel-perfect* y **exportación
  multi-motor**. Ese troceado por contorno es justo lo que
  [`spritesplitter`](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md)
  hace en local, por si prefieres no subir nada.
- **AGPL-3.0 cubre el programa, no el arte que produzcas** con él. Aun así, para publicar sigue
  aplicando §4: divulgación en Steam e itch.io.

> ⚠️ **Un agente no puede usarlo desatendido**: es una web con cuenta y tokens. Para el flujo
> automatizado de esta biblioteca, el peldaño sigue siendo el de `12 · 09 §5.2` — dibujo por
> código, assets libres, y generación local.

## 2 · Qué no sirve, y por qué es estructural (no un problema de «calidad del modelo»)

| No sirve para… | Por qué es un límite estructural, no una cuestión de mejorar el modelo |
|---|---|
| **Consistencia de personaje entre fotogramas de una animación** | Un generador de imágenes por difusión no tiene memoria del fotograma anterior: cada generación parte de ruido nuevo. Sin una técnica específica de control (§3), el color del pelo, la forma del arma o el número de dedos cambia entre imágenes que deberían ser el mismo personaje en poses distintas |
| **Animación coherente** | Incluso los modelos de interpolación de vídeo por IA no controlan un esqueleto ni una malla: deforman píxeles de una imagen a otra sin garantía anatómica. El resultado tiembla, deriva y produce artefactos en manos, armas y ropa — lo contrario de lo que exige un ciclo de andar limpio (ver [13 · 04](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md)) |
| **Pixel art de verdad** | Cubierto en [13 · 03 §7.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/03%20-%20Pixel%20art%20y%20resolución.md#72-ia-referencia-sí-resultado-no): sin rejilla, sin paleta cerrada, con antialias donde no debería haberlo |
| **Texturas *tileable* sin retoque** | Un generador genérico no garantiza que el borde derecho continúe el izquierdo y el de abajo el de arriba: eso exige un flujo dedicado (generar con desplazamiento circular + *inpainting* de la costura) que la mayoría de herramientas de consumo no ofrece por defecto |
| **Un asset final que se publica sin revisión humana** | Aparte de lo anterior: es también el punto donde entra el riesgo legal (§4) |

---

## 3 · El problema de la consistencia de estilo: las técnicas reales, y su límite real

Cuando alguien pregunta «¿cómo consigo que mi personaje generado por IA se vea igual en
todas las imágenes?», estas son las técnicas que existen hoy, de la más débil a la más fuerte:

| Técnica | Qué hace | Qué NO resuelve |
|---|---|---|
| **Seed fija** | Fija el ruido inicial de la generación. Con el **mismo prompt** y la misma seed, dos ejecuciones dan resultados parecidos | En cuanto cambias el prompt (nueva pose, nueva acción), el parecido se rompe: la seed no ancla el personaje, ancla el azar |
| **img2img con imagen de partida fija** | En vez de partir de ruido puro, se parte siempre de la misma imagen base (o de una silueta/pose de referencia) y se genera «encima» | Mantiene composición y paleta aproximadas, pero el detalle fino (accesorios, proporciones exactas) sigue derivando cada vez |
| **ControlNet** (u otros condicionadores estructurales: mapa de pose, de profundidad, de bordes) | Fuerza que la generación siga una **pose o silueta exacta** que tú le pasas, mientras el prompt controla el estilo | Controla la estructura, no la identidad: dos generaciones con la misma pose pero prompts ligeramente distintos pueden seguir sin ser «el mismo personaje» en textura y detalle |
| **LoRA** (*Low-Rank Adaptation*) | Un adaptador pequeño, entrenado sobre un conjunto de imágenes **del propio personaje o estilo**, que empuja las generaciones nuevas hacia esa identidad visual | Es la técnica más efectiva de las cuatro para identidad — pero exige tener ya un conjunto de imágenes de referencia consistentes con las que entrenarlo, que es precisamente el problema que se intentaba resolver. Y sigue sin garantizar coincidencia **píxel a píxel**, solo un parecido de alto nivel |

⚠️ **Ni siquiera combinando las cuatro técnicas existe hoy un flujo de IA generativa de imagen
que entregue la consistencia píxel a píxel que exige un sprite recortado y animado** (mismo
número de píxeles de silueta, mismo punto de anclaje del arma, mismo color exacto de rampa
en cada fotograma). Es la razón práctica —más que la estética— de que ningún estudio publique
hoy un set de animación jugable generado así sin una pasada de retoque humano exhaustivo
fotograma a fotograma, que en la práctica equivale a dibujarlo de nuevo.

---

## 4 · El estado legal (verificado el 2026-09-07, con fuente primaria y fecha)

Esto no es una opinión: son tres asuntos distintos —derechos de autor, y las políticas de
**dos** tiendas— que conviene no confundir entre sí.

### 4.1 Derechos de autor: la postura de la U.S. Copyright Office

Fuente primaria: **U.S. Copyright Office**, informe
*«Copyright and Artificial Intelligence, Part 2: Copyrightability»* (29 de enero de 2025),
que sigue a su *«Copyright Registration Guidance: Works Containing AI-Generated Content»*
(Registro Federal, 16 de marzo de 2023) — <https://www.copyright.gov/ai/>.

- **La autoría humana es un requisito de base.** Una obra generada **íntegramente** por IA
  no es registrable como propiedad intelectual en EE. UU.
- **Un prompt, por detallado que sea, no basta.** La Oficina concluyó explícitamente que la
  mera elección de instrucciones de texto —incluso instrucciones elaboradas, fruto de
  esfuerzo humano real— no aporta el control suficiente sobre el resultado como para que el
  usuario sea su autor.
- **La modificación y composición humanas SÍ cuentan.** Si tomas una imagen generada y la
  retocas, recortas, combinas o editas con intervención creativa real, esa parte del trabajo
  —la tuya— sí es registrable; lo que sigue sin serlo es el fragmento puramente generado por
  la máquina.
- **Precedente**: dos solicitudes de registro con contenido generado por IA sin edición
  humana sustancial fueron denegadas — *Théâtre D'Opéra Spatial* (septiembre de 2023) y
  *SURYAST* (diciembre de 2023). Ambos casos confirmaron el mismo criterio.

**Consecuencia práctica para un estudio pequeño**: si el arte de tu portada, tu logo o un
sprite central del juego es sustancialmente generado por IA sin una edición humana real
encima, **esa pieza concreta puede no estar protegida por derechos de autor en EE. UU.** —
en teoría, cualquiera podría reutilizarla sin infringir nada tuyo. Es un riesgo de negocio
distinto de (y añadido a) las políticas de las tiendas de abajo.

### 4.2 Steam: divulgación obligatoria, con exención explícita para herramientas de desarrollo

Fuente primaria: **Steamworks**, documentación oficial del *Content Survey* —
<https://partner.steamgames.com/doc/gettingstarted/contentsurvey> (consultado 2026-09-07).
Valve introdujo la divulgación en enero de 2024 y **reescribió el formulario el 16 de enero
de 2026** para aclarar qué cuenta y qué no.

- **Dos categorías**, ambas exigen describir la implementación «en detalle» en la encuesta:
  - **Pre-Generated** («cualquier contenido que se incluye en tu juego y es consumido por
    jugadores que se crea con la ayuda de herramientas de IA durante el desarrollo»):
    sprites, música, texto, modelos generados en el estudio y que **shippean** con el juego.
  - **Live-Generated** («cualquier contenido creado con la ayuda de herramientas de IA
    mientras el juego se ejecuta»): diálogo o música generados en directo. Exige además
    documentar «qué barandillas» impiden que el sistema genere contenido ilegal u ofensivo.
- **Exención explícita para herramientas de desarrollo**: la propia documentación reconoce
  que «muchos entornos modernos de desarrollo de juegos tienen herramientas de IA
  integradas» y excluye del escrutinio «las ganancias de eficiencia» de usarlas. En la
  práctica: **un asistente de código (Claude Code, Copilot, Cursor) o el andamiaje `--ai` de
  `gm-cli` de esta misma biblioteca NO se declara** — lo que se declara es el contenido
  final que ve o escucha el jugador.
- Esto aparece en la ficha de la tienda como una sección **«AI Generated Content
  Disclosure»**. El procedimiento paso a paso para rellenarlo ya está en
  [13 · 11 §9.4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/11%20-%20Producción,%20alcance%20y%20lanzamiento.md#94-clasificación-por-edades-pegi-esrb-e-iarc);
  no se repite aquí.

### 4.3 itch.io: etiquetado obligatorio, con delisting como sanción en páginas de assets

Fuente primaria: **itch.io**, *«Content creator quality guidelines»* —
<https://itch.io/docs/creators/quality-guidelines> (consultado 2026-09-07). Cita textual:

> *«We ask that you accurately tag your project if it contains materials produced by
> generative AI by utilizing the AI Disclosure section on your project's edit page.»*

- La divulgación se activa para **sistemas que crean contenido nuevo a partir de grandes
  conjuntos de datos** (texto, imagen, música): ChatGPT, DALL·E, Midjourney, Stable
  Diffusion y equivalentes.
- **Exención explícita**: *«Projects using self-contained algorithms without external large
  datasets don't require the use of generative AI tags»* — cubre la IA clásica de
  videojuego (patrones de comportamiento de un NPC, pathfinding), no el arte generativo.
- **Consecuencia de no declarar**: en páginas de **assets** (no solo juegos completos), la
  falta de etiqueta puede dejar la página fuera de las secciones de exploración del sitio
  (*delisting*) — más estricto que en Steam, donde la sanción no llega a ese punto.
- **Nota de mercado, ya recogida en 13 · 03 §7.2**: buena parte de la comunidad de pixel art
  rechaza abiertamente el arte generado (los tutoriales de Pedro Medeiros llevan la etiqueta
  «No generative AI was used»). Declarar correctamente no es solo cumplir la norma: en esa
  comunidad concreta, declarar mal es un coste reputacional real.

⚠️ Ninguna de las tres fuentes anteriores prohíbe usar IA generativa en un juego. Las tres
exigen **transparencia** sobre su uso; la primera (Copyright Office) además introduce un
riesgo de propiedad intelectual sobre el resultado final que no depende de ninguna tienda.

---

## 5 · Dónde encaja en un pipeline real — recomendación práctica

| Fase del pipeline | ¿IA generativa? | Por qué |
|---|---|---|
| Ideación y moodboard iniciales | **Sí** | Nunca se publica; el coste de estar mal es cero |
| Hoja de referencia de un personaje nuevo | **Sí, con cautela** | Solo como guion visual que un artista humano redibuja después — no como fuente del sprite final |
| Concept art de un fondo o splash no jugable | **Sí, si el juego lo declara** (§4.2, §4.3) | Menor exigencia de consistencia entre fotogramas que un personaje animado |
| Sprite final animado y jugable | **No** | Consistencia entre fotogramas y pixel art real no resueltos hoy (§2, §3) |
| Icono o pieza de UI puntual sin animar | **Depende — declarar siempre** | Si es una pieza central de identidad de marca (logo, icono de tienda), pesa el riesgo de propiedad intelectual del §4.1 |
| Textura de material genérico sin silueta (roca, tierra, tela), retocada a mano después | **Sí** | No hay forma reconocible que deba mantenerse coherente entre usos |
| *Upscaling* de un asset comprado que la licencia permite modificar | **Sí, si la licencia lo permite** | Verifica primero la licencia concreta — ver [07 · 09 §1](./09%20-%20Asset%20packs%20y%20recursos%20gráficos.md#1-regla-número-uno-la-licencia) |

La recomendación corta: **usa IA generativa para todo lo que nunca llega al jugador tal
cual, y para nada que sí lo hace sin que un humano lo reelabore.** Es exactamente el mismo
criterio que ya aplica esta biblioteca a sus propias herramientas de imagen —`gpt-image-2`
para hojas de modelado 3D o iconos de marca (ver `img2threejs` y los flujos de diseño del
propio repositorio de herramientas del usuario), nunca como sustituto del sprite final.

---

## 6 · Checklist antes de usar IA generativa en tu arte

- [ ] ¿Sabes en qué fase del pipeline estás usándola (§5), y es una fase donde sí ayuda?
- [ ] Si el resultado va a **shippear tal cual** (no como referencia): ¿lo has descartado?
      (§2, §5)
- [ ] Si va a shippear una pieza retocada por un humano: ¿la edición es sustancial, no un
      simple recorte? (afecta a si esa pieza es tuya de verdad — §4.1)
- [ ] ¿Está declarado en el Content Survey de Steam si publicas ahí? (§4.2, con el
      procedimiento en 13 · 11 §9.4)
- [ ] ¿Está marcada la sección AI Disclosure de itch.io si publicas ahí? (§4.3)
- [ ] ¿Está anotado en tu `CREDITS.md` qué se generó, con qué herramienta y en qué fecha?
      (convención ya definida en [07 · 09 §1](./09%20-%20Asset%20packs%20y%20recursos%20gráficos.md#1-regla-número-uno-la-licencia))
- [ ] Si es pixel art: ¿ha pasado por un artista humano que lo redibuje a rejilla y paleta
      reales? Si no, no es pixel art — ver 13 · 03 §7.2

---

## 7 · Errores clásicos

| Error | Consecuencia | Arreglo |
|---|---|---|
| Confundir «sirve para referencia» con «sirve para publicar» | El sprite final tiene antialias, paleta abierta y ninguna rejilla | §1-§2: usar solo como referencia que un humano redibuja |
| Creer que fijar la seed resuelve la consistencia | El personaje cambia de detalle en cuanto varía el prompt | §3: seed sola es la técnica más débil de las cuatro |
| No declarar en Steam por pensar que «solo fue para ideas» | El Content Survey exige declarar lo que **shippea**, no el proceso interno — pero si algo generado llega al juego, sí cuenta | §4.2: solo se exime el uso puramente interno/herramientas de desarrollo |
| Publicar un asset pack en itch.io sin la etiqueta AI Disclosure | Riesgo de *delisting* de la página del asset | §4.3 |
| Asumir que «lo generé yo, luego es mío» | Sin edición humana sustancial, la pieza puede no ser registrable como propiedad intelectual | §4.1 |
| Usar un upscaler genérico sobre pixel art terminado | Rompe la rejilla y mezcla colores fuera de paleta | §1: los upscalers ayudan sobre ilustración, no sobre pixel art |

---

## Ver también

- [13 · 03 §7.2 — IA: referencia sí, resultado no](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/03%20-%20Pixel%20art%20y%20resolución.md#72-ia-referencia-sí-resultado-no) — el porqué estructural específico de pixel art
- [07 · 14 — IA y GameMaker](./14%20-%20IA%20y%20GameMaker.md) — IA como programadora (MCP, `gm-cli --ai`), no como generadora de arte
- [07 · 09 §1 — Asset packs: la regla de la licencia y `CREDITS.md`](./09%20-%20Asset%20packs%20y%20recursos%20gráficos.md#1-regla-número-uno-la-licencia)
- [13 · 11 §9.4 — Clasificación por edades y Content Survey de Steam](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/11%20-%20Producción,%20alcance%20y%20lanzamiento.md#94-clasificación-por-edades-pegi-esrb-e-iarc) — cómo se rellena el formulario en tu ficha
- [04 · 21 — Localización e idiomas (con traducción por IA)](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md) — el otro uso legítimo de IA generativa ya documentado en esta biblioteca, para texto en vez de imagen

---

## Fuentes

Todas consultadas el **7 de septiembre de 2026**.

- U.S. Copyright Office — *«Copyright and Artificial Intelligence, Part 2: Copyrightability»*
  (29 de enero de 2025) — <https://www.copyright.gov/ai/>
- U.S. Copyright Office — *«Copyright Registration Guidance: Works Containing AI-Generated
  Content»* (Registro Federal, 16 de marzo de 2023), citada desde la misma página anterior
- Steamworks — documentación oficial del *Content Survey*, sección de divulgación de IA
  generativa — <https://partner.steamgames.com/doc/gettingstarted/contentsurvey>
- itch.io — *«Content creator quality guidelines»*, sección de divulgación de IA —
  <https://itch.io/docs/creators/quality-guidelines>

⚠️ **Lo que queda marcado como no verificado directamente**: la fecha exacta de la primera
versión de la política de Steam (enero de 2024) y la cifra de adopción (~20 % de los juegos
del *Content Survey* a julio de 2026, más de 7 300 juegos con IA declarada a marzo de 2026)
proceden de cobertura periodística especializada sobre el cambio del 16 de enero de 2026
(StraySpark Studio, VG Chronicle, GameDeveloper.com), no de un comunicado con esas cifras
firmado por Valve que se haya podido abrir directamente en esta sesión. El texto citado en
§4.2 sobre categorías y exenciones **sí** procede de la página oficial de Steamworks.
