# Auditoría r5 · Assets — cómo consigue un agente assets que no sean basura

> Fecha 2026-09-08 · 63 temas · 32 cubiertos · 24 parciales · 7 faltan

## Resumen ejecutivo

**La pregunta del usuario tiene una respuesta honesta y es incómoda: hoy, para audio, un
agente sin artista produce algo digno; para gráficos, produce basura — y lo hace siguiendo la
propia biblioteca al pie de la letra.**

La buena noticia primero: el problema **ya tiene solución documentada y ejecutable en el
dominio del sonido**. `13 · 09 §8 bis` («Un agente sin archivo de audio: la escalera de
prioridad») es exactamente lo que pide el brief — una escalera con código verificado
(`tono_generar()`/`ruido_generar()` sobre `audio_create_buffer_sound()`, `08 · 24 §3`), una
tabla honesta de qué suena bien sintetizado y qué no, y una salida de emergencia
(`PLACEHOLDERS.md`). Un agente que la sigue entrega un juego con SFX de acción, UI e impacto
que suenan **intencionados**, no rotos. Esto no hay que tocarlo.

La mala noticia es el equivalente gráfico. Existe una sección con el mismo nombre y la misma
ambición — `12 · 09 §5.2` («Gráfico: la misma idea, para sprites»), añadida en esta misma
cuarta ronda respondiendo al encargo #8 de `r4-agente-ia-gamemaker.md` — pero su contenido real,
verificado en esta sesión, es:

```bash
magick -size 64x64 xc:"#ff3366" spr_placeholder.png
```

Un **cuadrado de color plano**. Sin silueta, sin paleta, sin borde, sin punto de origen marcado,
sin ninguna de las tres reglas que la propia biblioteca exige dos capítulos más allá
(`13 · 03 §7.3`: tamaño definitivo, color por categoría, origen y dirección marcados). Es
literalmente la «basura en SVG o lo que sea» que describe el usuario, solo que ahora en PNG y
con el sello de «receta verificada». El encargo de la ronda anterior se cerró en la letra
(«genera un PNG y da el comando que funciona») pero no en el espíritu («que no sea basura») —
y ninguna auditoría posterior (`r4-99-cierre.md` no la incluye en su tabla de encargo→estado)
comprobó la calidad del resultado. Ese es el hueco que esta ronda añade: no es que falte una
política, es que la política que hay **normaliza el rectángulo** en vez de subir el listón.

Encima, esa misma sección le dice al agente **que no use generación por IA** («no hay generador
de arte por IA configurado… nunca depender de una API de terceros sin configurar») y remite,
como alternativa «más elaborada», a la skill hermana `gamedev-self-generated-assets` — que es
íntegramente sobre **Canvas 2D, PixiJS, Phaser y Three.js**, cero aplicable a GML. Un agente de
GameMaker que siga ese enlace no encuentra nada que pueda ejecutar. Y esa prohibición contradice
tanto la política global del propio entorno del usuario (`codex exec` + `gpt-image-2` para
iconos/logos, verificado disponible en esta máquina — ver más abajo) como el propio `07 · 23 §5`
de esta biblioteca, que sí reconoce usos legítimos de IA generativa (referencia, iconos sin
animar con cautela, fondos muy lejanos) siempre que se declare.

**¿Podría un agente ejecutar esto de principio a fin sin acabar con basura?** Depende del tipo
de asset:

- **Audio**: sí, de principio a fin, sin salir de GML. Es el estándar a copiar.
- **Diseño/técnica de arte** (paletas, siluetas, animación, nine-slice, autotiling, shaders de
  efecto, partículas nativas): sí — es la parte mejor cubierta de toda la biblioteca, con
  `13 · 03` como referencia de nivel profesional.
- **El sprite/tile/icono final cuando no hay artista ni asset libre que encaje**: no. El agente
  se queda con dos opciones reales — un rectángulo de color (documentado, pero es basura) o
  parar y pedírselo a un humano. No hay un tercer peldaño verificado entre esos dos extremos.
- **Marca y tienda** (logotipo, icono del ejecutable, capsule de Steam): prácticamente sin
  cubrir. Cero documentos propios; lo poco que hay son tablas de tamaños sin receta de cómo
  llenarlas sin artista.

El hueco no es «falta documentación sobre dónde bajar assets» — esa parte (`07 · 09`) está muy
bien hecha y verificada con enlaces vivos. El hueco es el **último tramo**: qué hace el agente
cuando ya miró en Kenney, ya miró en los Asset Bundles, y sigue sin tener el sprite exacto que
necesita ahora mismo, en este frame, para esta build.

---

## Tabla tema por tema

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| 1 | Sprite idle del jugador | 🟡 | `13/03` completo (técnica); `07/09` (sourcing) | El sprite en sí — ver hueco central #59-60 |
| 2 | Ciclo de andar/correr (4/6/8 frames) | ✅ | `13/03 §4.3 — Ciclos de andar: 4, 6 u 8 frames` | — |
| 3 | Salto y caída del jugador | 🟡 | `13/03 §1.3 Anticipación` (técnica); `13/04 §1.3` (ejemplo de 4 frames) | El sprite final — mismo hueco #59-60 |
| 4 | Daño/muerte, con *frame data* | ✅ | `13/04 §3.7 — Frame data: ligar el daño al fotograma` | — |
| 5 | Ataque(s), *smears* | ✅ | `13/03 §4.5 — Smears: cómo animar movimientos rápidos`; `13/04 §1.4` | — |
| 6 | Retrato/avatar de personaje (diálogo, menú) | 🔴 | Ninguna. `04/10` (Visual Novel) no cubre de dónde sale el busto | Sección nueva — ver encargo #7 |
| 7 | Sprite idle/movimiento de enemigo genérico | 🟡 | `13/03` (técnica general, no específica de enemigos) | El sprite — mismo hueco #59-60 |
| 8 | Sprite de ataque de enemigo | 🟡 | `04/33 — Diseño de enemigos` (diseño, no arte) | Mismo hueco #59-60 |
| 9 | Sprite de daño/muerte de enemigo | 🟡 | `04/33` (diseño) | Mismo hueco #59-60 |
| 10 | Diseño y sprite de jefe (boss, multi-fase) | 🟡 | `04/33 — Diseño de enemigos, encuentros y director de combate` (diseño ✅ completo) | El arte del jefe — mismo hueco #59-60, agravado por ser la pieza más visible del juego |
| 11 | Tileset de plataformas/suelo (arte) | 🟡 | `13/03 §8.2` (checklist técnico); `07/09 §2.2, §2.4` (sourcing Kenney/itch) | Tileset propio sin pack que encaje — mismo hueco #59-60 |
| 12 | Tileset de interiores/paredes (arte) | 🟡 | Igual que #11 | Igual que #11 |
| 13 | Autotiling 16/47 piezas — bitmask de vecinos → índice | ✅ | `13/07 §5 bis — Autotiling clásico`; `13/02 §3.3, L305-318` | — (cerrado desde r3-arte-animacion, tema 20/21/24) |
| 14 | Props/decoración de escena | 🟡 | `13/11 §5` tabla «arte por sistema» los menciona; sin receta de arte | Mismo hueco #59-60 |
| 15 | Partículas de ambiente (polvo, hojas, chispas) | ✅ | `part_type_shape()` verificado con `buscar.py`; `04/39` catálogo completo de formas nativas (`pt_shape_flare`, `pt_shape_spark`…) | — GameMaker trae formas de partícula nativas: cero arte necesario |
| 16 | Moneda/coleccionable | 🟡 | `07/09 §2.2` (Kenney trae monedas CC0) | Diseño propio — mismo hueco #59-60 |
| 17 | Power-up/objeto de inventario | 🟡 | `13/05 §3.5e` (inventario, técnica de UI) | El icono del objeto — mismo hueco #28/#59-60 |
| 18 | Interactivo (llave, puerta, palanca) | 🟡 | Genérico en recetas de género (`04/01`, `04/48`) | Mismo hueco #59-60 |
| 19 | Sprite de proyectil (bala, flecha) | 🟡 | `04/34 — Combate a distancia` (diseño, balística) | Mismo hueco #59-60 |
| 20 | VFX de impacto/explosión (spritesheet) | 🟡 | `04/39` catálogo de diseño completo (72 KB) | El spritesheet en sí si no basta con partículas nativas (#21) |
| 21 | VFX de partículas nativas (chispas, humo, magia, anillo) | ✅ | `part_type_shape()`, `pt_shape_ring/square/star/spark/flare/explosion` — todas verificadas y usadas en `04/39` | — |
| 22 | Shaders de efecto (hit flash, dissolve, glitch, bloom, CRT) | ✅ | `08/23` — recetario de 10 efectos completos, verificados | — |
| 23 | Fondo lejano/parallax | 🟡 | `13/03 §6.8` (técnica, orden de dibujo); `07/09 §2.2` (packs de parallax en Kenney) | Arte propio — mismo hueco #59-60 |
| 24 | Fondo medio | 🟡 | Igual que #23 | Igual que #23 |
| 25 | Cielo/skybox 2D | 🟡 | Igual que #23 | Igual que #23 |
| 26 | Panel/marco nine-slice (técnica) | ✅ | `13/05 §3.4 — Paneles nine-slice: un sprite pequeño para cualquier tamaño` | — (cerrado desde r3-arte-animacion) |
| 27 | Botón, 4 estados (técnica) | ✅ | `13/05 §3.5a` | — |
| 28 | Icono de habilidad/objeto (sourcing) | ✅ | `07/09 §9 — Iconos de UI y habilidades` (Game-icons.net CC-BY, Kenney CC0) | — |
| 29 | Barra de vida/maná/progreso (técnica) | ✅ | `13/05 §3.5b — Barra de vida con retardo` | — |
| 30 | Cursor de ratón personalizado | 🟡 | `window_set_cursor()` verificado; `04/48 §…` y `13/05` lo usan | El sprite del cursor — mismo hueco #59-60 |
| 31 | Fuente tipográfica | ✅ | `07/09 §6` (Google Fonts OFL, Kenney Fonts CC0, con la trampa de licencia de fuente explicada); `13/05 §3.6` | — |
| 32 | Tooltip/caja de diálogo UI | ✅ | `13/05 §3.5d, §3.5f` (mismo patrón nine-slice) | — |
| 33 | Logotipo del juego | 🔴 | Una única mención incidental (`13/03 L448`, «no hagas dithering en un logotipo») | Documento no existe — ver encargo #1 |
| 34 | Icono del ejecutable por plataforma (.ico Windows, iconos iOS, adaptativo Android) | 🔴 | Solo en el manual mirror: `Settings/Game_Options/Windows.md L44`; una fila de checklist en `04/28 L963` sin receta | Ver encargo #2 |
| 35 | Capsule/portada de tienda (Steam header/small/main/vertical, itch cover) | 🔴 | `13/11 §6.2` da **solo tamaños** (920×430, 462×174…), cero receta de cómo llenarlos sin artista | Ver encargo #3 |
| 36 | Capturas de pantalla para tienda | ✅ | `13/11 §4.7` (`captura_tomar()`, `screen_save`/`screen_save_part` verificados); `§6.2` (mínimo 5, 1920×1080) | — |
| 37 | GIF para redes | ✅ | `13/11 §6.2` («los GIFs salen gratis de tus builds quincenales») | — |
| 38 | Tráiler | 🟡 | `13/11 §6.2` lo menciona como el activo que más convierte | Sin receta de producción ni herramienta — fuera del alcance típico de esta biblioteca (es vídeo, no GameMaker), pero merece al menos un enlace a una skill de vídeo del propio entorno |
| 39 | Música de menú | ✅ | `13/09 §2` tabla por género (columna «Música»); `07/09 §2.2, §8` (sourcing) | — |
| 40 | Música de gameplay (loop) | ✅ | Igual que #39; `13/09 §6 — Ambiente y música` | — |
| 41 | Música de victoria | ✅ | `13/09 §2` tabla («jefe, victoria» en Plataformas 2D y RPG) | — |
| 42 | Música de derrota/game over | ✅ | `13/09 §2` tabla RPG («triste») | — |
| 43 | Música adaptativa por capas (combate) | ✅ | `04/26 — Música adaptativa por capas`; `01/13 §5` (sync groups); `08/24 §2` (11 funciones de sincronía verificadas) | — |
| 44 | SFX de acción del jugador (salto, ataque, daño) | ✅ | `13/09 §8 bis` — código verificado (`tono_generar`, `ruido_generar`) | — |
| 45 | SFX de UI (clic, confirmar, cancelar, error) | ✅ | `13/09 §8 bis` (tabla + código: clic con `tono_generar(1600, 0.03)`) | — |
| 46 | SFX de ambiente/loop (viento, agua, ciudad) | 🟡 | `13/09 §8 bis` tabla propia lo marca explícitamente como «no razonable por síntesis» | Correcto que no se pueda sintetizar bien; falta remitir con más fuerza a Freesound/`07/09 §2.5` como única vía real |
| 47 | SFX de impacto/explosión | ✅ | `13/09 §8 bis` (`ruido_generar(0.12)`, verificado) | — |
| 48 | Bancos de audio ya producidos (Incompetech, Pixabay, Sonniss) | ✅ | `07/09 §8`, con licencias y fecha de verificación | — |
| 49 | Voces de diálogo grabadas — proceso completo | ✅ | `13/24` (914 líneas: guion, hoja de grabación generada, importación, localización) | — |
| 50 | Voz sin actor: TTS vs. voces procedurales | 🟡 | `13/24 §6` (procedural, tipo Animal Crossing, ✅ excelente y ejecutable con `tono_generar()`); `13/24 §3.5` marca TTS explícitamente **fuera de alcance**, sin integración verificada | Investigar y documentar una vía de TTS con fuente primaria, o mantener el disclaimer pero enlazarlo desde `12/09` |
| 51 | Ciclo de andar/idle con vida (técnica) | ✅ | `13/03 §4.4 — El idle no es un frame quieto` | — |
| 52 | Sequences y Animation Curves (herramienta nativa) | ✅ | `13/04 §5, §6` — completo, con creación por código | — |
| 53 | Animación esquelética (Spine) | ✅ | `13/04 §7`; `07/21 — Vinyl…` no aplica, es `07 - Ecosistema` catálogo de Spine vía manual | — |
| 54 | Licencias de assets de terceros (CC0/CC-BY/OFL/GPL) | ✅ | `07/09 §1` — tabla completa, con el matiz de fuentes (OFL) y el «contagio» de GPL explicados con fuente y fecha | — |
| 55 | Legal del arte generado por IA (copyright, Steam Content Survey, itch.io) | ✅ | `07/23 §4` — U.S. Copyright Office, Steamworks, itch.io, las tres con fuente primaria y fecha (2026-09-07) | — (cierra temas 90-92 de `r3-arte-animacion.md`; ver «Lo que encontré desactualizado») |
| 56 | Consistencia de estilo en IA generativa (seeds, img2img, ControlNet, LoRA) | 🟡 | `07/23 §3` — las 4 técnicas explicadas con su límite real | Es teoría correcta y honesta, pero cero pasos de «cómo lo invoco desde este agente, en esta sesión» — ver hueco central |
| 57 | Coherencia entre packs de assets mezclados | ✅ | `13/03 §7.1` (remapear paleta, unificar tamaño de tile) | — |
| 58 | **Escalera de prioridad — audio sin artista** | ✅ | `13/09 §8 bis` — completa, código verificado, con tabla de qué sintetizar y qué no | Modelo a imitar para gráficos (ver #59) |
| 59 | **Escalera de prioridad — arte sin artista (agente sin PNG)** | 🟡 GRAVE | `12/09 §5.2` existe (añadido en esta ronda) pero su único peldaño intermedio es un cuadrado de color plano (`magick -size 64x64 xc:"#ff3366"`) | Ver hueco central y encargo #4 |
| 60 | Placeholder «digno» (silueta + paleta + origen) frente a rectángulo/cuadrado liso | 🔴 | `13/03 §7.3` y `13/11 §5` documentan explícitamente el **rectángulo plano** como placeholder válido, sin peldaño superior | Ver encargo #4 — es el hueco central de esta auditoría |
| 61 | Generar un `.wav` como **archivo** importable por CLI (no solo síntesis en runtime) | 🔴 | Confirmado con `grep` cruzado: 0 apariciones de «wave» + «python» en toda la biblioteca | Ver encargo #5 (distinto de #44-47, que es síntesis en tiempo real, ya resuelta) |
| 62 | Herramientas locales de generación disponibles (`magick`, Pillow, `sips`, `ffmpeg`, `codex`) | 🟡 | Verificado con `which`/rutas directas en esta sesión (ver tabla de la sección siguiente) | Están disponibles y funcionan, pero la biblioteca solo las usa para el rectángulo de #60 — falta enseñar a sacarles partido real |
| 63 | Invocación práctica de `gpt-image-2`/`codex exec` para arte 2D de un juego GameMaker | 🔴 | `07/23` es exclusivamente teoría/legal; `12/09 §5.2` **prohíbe** explícitamente esta vía y remite a una skill que no aplica a GML | Ver encargo #6 |

---

## Herramientas disponibles en esta máquina — verificado con rutas absolutas, 2026-09-08

| Herramienta | Disponible | Ruta | Para qué serviría |
|---|---|---|---|
| **ImageMagick** (`magick`) | ✅ | `/opt/homebrew/bin/magick` (7.1.2-29) | Generar PNG por código: formas, degradados, composición, conversión de formatos |
| **Python 3 + Pillow** | ✅ | `python3.12` (alias de `/opt/homebrew/bin/python3.12`), Pillow 12.2.0 | Igual que ImageMagick, con más control programático (dibujo de formas, paleta indexada) |
| **Python 3 + NumPy** | ✅ | NumPy 2.4.6 | Ruido/gradientes procedurales para texturas, reutilizando las fórmulas de `13/07 §2` |
| **`sips`** (macOS nativo) | ✅ | `/usr/bin/sips` | Redimensionar un PNG maestro a todos los tamaños de icono de una vez |
| **`iconutil`** (macOS nativo) | ✅ | `/usr/bin/iconutil` | Empaquetar un `.iconset` en `.icns` (icono de macOS) |
| **`ffmpeg`** | ✅ | `/opt/homebrew/bin/ffmpeg` | Convertir/recortar audio y vídeo (GIFs de marketing, conversión de formatos de audio) |
| **`codex` (CLI)** | ✅ | función de shell que envuelve el binario, operativa | Generación de imágenes con `gpt-image-2` vía `codex exec`, según la política global del propio entorno del usuario |
| **`gm-cli` / `resourcetool`** | ✅ | `/opt/homebrew/bin/gm-cli` (v2.2.0, hay v2.3.0 disponible) | Importar el PNG/WAV generado como asset real del proyecto (`resource create`, `sprite addframe`, `sound setfile`) |
| SVG → raster (`rsvg-convert`, Inkscape, `potrace`) | ❌ | No encontrado | No hay vía verificada para vectorizar/rasterizar SVG fuera de lo que `magick` haga con sus delegados internos — no comprobado en esta sesión |

**Conclusión de esta tabla**: no falta ninguna herramienta. Lo que falta es que la biblioteca
enseñe a usarlas para algo mejor que un cuadrado de un solo color.

---

## Huecos por prioridad

### 🔴 Graves

1. **El único peldaño intermedio del «arte sin artista» es un cuadrado de color plano**
   (temas #59-60). Es la propia biblioteca institucionalizando el problema que describe el
   usuario. No es solo que falte algo: es que lo que hay es contraproducente, porque un agente
   que lo sigue al pie de la letra cree que está cumpliendo la política cuando en realidad está
   produciendo exactamente la basura que se quería evitar.
2. **`12/09 §5.2` prohíbe la generación por IA y remite a una skill que no aplica a GML**
   (tema #63). El agente que necesita algo mejor que el rectángulo y busca la «vía más
   elaborada» que promete el propio documento llega a un callejón sin salida: la skill
   `gamedev-self-generated-assets` es de Canvas/PixiJS/Phaser/Three.js, no de GameMaker.
3. **Marca y tienda sin cubrir**: logotipo (#33), icono del ejecutable por plataforma (#34) y
   capsule de Steam/itch (#35) no tienen ni receta ni puntero a una. Son las tres piezas que ve
   el 100 % de la gente que se cruza con la ficha del juego — la propia `13/11 §5` lo dice del
   tráiler y la capsule («la partida que se olvida siempre, y la única con fecha límite
   externa»), pero no se traduce en contenido.
4. **No hay receta para generar un `.wav` como archivo importable** (tema #61) — distinto de la
   síntesis en tiempo real (ya resuelta): un agente que necesita un asset de sonido persistido
   como archivo (por ejemplo, para un sistema de voz procedural que SÍ debe sobrevivir entre
   sesiones, o para adjuntarlo a un *build* sin recompilar) no tiene receta, solo la síntesis en
   caliente de `13/09 §8 bis`.

### 🟠 Medios

5. **Retrato/avatar de personaje** (#6) — sin ninguna guía, ni siquiera de sourcing, a pesar de
   que `04/10` (Visual Novel) depende de ello constantemente.
6. **La escalera de audio nunca se documentó formalmente en `PLACEHOLDERS.md` (`13/11 §5`)**,
   pese a que `13/09 §8 bis` dice explícitamente «extiéndelo tal cual [a audio]». Grep confirmado:
   `13/11` solo menciona `PLACEHOLDERS.md` para arte (L687), nunca para audio. Es un cabo suelto
   entre dos documentos que se citan mutuamente pero no se sincronizaron del todo.
7. **`gm-cli` desactualizado en esta máquina**: `v2.2.0` instalado, `v2.3.0` disponible
   (`npm install -g @gamemaker/gm-cli` avisa de ello en cada ejecución). No es un hueco de
   contenido, pero cualquier receta que dependa de una versión de `resourcetool` debería anotar
   con qué versión se verificó.

### 🟡 Menores

8. **`13/09 §8 bis` §SFX de ambiente** (#46) podría enlazar más fuerte a Freesound como única
   vía real, en vez de solo excluir la síntesis.
9. **TTS para voz** (#50) sigue honestamente marcado como fuera de alcance — no es un error,
   pero si se investiga alguna vez, ya hay el hueco exacto donde insertarlo (`13/24 §3.5`).
10. **Tráiler** (#38) sin receta de producción — es la única pieza de este audit que sale del
    ámbito de GameMaker (es edición de vídeo), así que basta con un enlace a una herramienta del
    propio entorno del usuario, no un documento nuevo.

---

## Encargo para el redactor

1. **Documento nuevo: `07 - Ecosistema/24 - Logotipo e icono del juego.md`** (o sección dentro de
   `13/11`). Contenido: (a) qué es un logotipo de videojuego frente a un logo corporativo — legible
   a 120×45 px porque así se ve la *small capsule* (`13/11 §6.2`, ya verificado); (b) receta con
   `codex exec` + `gpt-image-2` siguiendo la política global del entorno (varias variantes, el
   usuario elige) — citar `07/23 §5` para el criterio de cuándo es aceptable IA generativa en una
   pieza de marca puntual sin animar; (c) checklist de legibilidad en escala de grises y a tamaño
   mínimo, reutilizando el mismo criterio de `13/03 §8.1`.
2. **Sección nueva en `04/28` (Juegos para móvil) o documento propio: «Iconos del ejecutable, por
   plataforma».** Contenido verificado con `sips`/`iconutil` (ya confirmados disponibles en esta
   sesión): partir de un PNG maestro 1024×1024, generar el `.iconset` con `sips -z $s $s`, empaquetar
   con `iconutil -c icns` (macOS); explicar el equivalente `.ico` de Windows citando
   `Settings/Game_Options/Windows.md L44` del manual mirror (ya localizado); enlazar la fila de
   checklist ya existente en `04/28 L963` (icono adaptativo Android, iconos completos iOS) para
   que deje de ser una casilla sin desarrollar.
3. **Ampliar `13/11 §6.2`** con una subsección «Cómo llenar la capsule sin artista»: orden de
   prioridad — (a) recortar/componer arte ya generado del propio juego (capturas con
   `captura_tomar()`, ya verificado en `13/11 §4.7`) sobre un fondo de color de marca; (b)
   `codex exec` + `gpt-image-2` para una pieza compuesta, declarando su uso según `07/23 §4.2-4.3`;
   (c) encargar a un humano si el juego ya genera ingresos. No repetir la tabla de tamaños, que ya
   está bien.
4. **Reescribir `12/09 §5.2` — el hueco central de esta auditoría.** No basta con ampliar: el
   peldaño 2 actual (`magick -size 64x64 xc:"#ff3366"`) hay que **sustituirlo**, no complementarlo,
   porque normaliza justo lo que se quiere evitar. Escalera propuesta, con símbolos ya verificados
   en esta sesión:
   - Peldaño 1 (ya existe, mantener): `draw_rectangle`/`draw_circle` en el evento Draw, sin
     sprite — sigue siendo el más barato para lógica pura.
   - Peldaño 2 nuevo — **«silueta con paleta y origen», no rectángulo liso**: usar
     `draw_ellipse_color()`/`draw_triangle_color()`/`draw_circle()` (verificadas con `buscar.py`
     en esta sesión) combinadas —por ejemplo, un óvalo con `draw_ellipse_color(x1,y1,x2,y2,
     col_claro,col_oscuro,false)` para un cuerpo con volumen mínimo, más un contorno de 1 px con
     `draw_circle(…,…,true)`— dibujadas sobre una `surface_create()` y convertidas con
     `sprite_create_from_surface()` (verificada, ya usada en `04/39` y `08/23 §3.10`) para que el
     resultado sea un sprite real con máscara de colisión, no solo un dibujo en pantalla. Aplicar
     el mismo criterio de «un color por categoría» que ya fija `13/03 §7.3` (jugador, enemigo,
     objeto, peligro), y marcar el origen con un punto de otro color como hace el ejemplo GML de
     esa misma sección — así el peldaño 2 hereda las tres reglas que hoy solo tiene el peldaño 1.
   - Peldaño 2 alternativo por CLI — cuando el asset SÍ debe ser un archivo (no solo runtime):
     con ImageMagick, generar una forma con relleno y contorno en vez de un rectángulo liso —
     `magick -size 64x64 xc:none -fill "#3a7d44" -stroke "#1c3d22" -strokewidth 2 -draw
     "ellipse 32,32 24,28 0,360"` (o el equivalente con Pillow `ImageDraw.ellipse` con `fill` y
     `outline`) — probarlo en esta sesión antes de publicarlo, igual que se hizo con el rectángulo
     que se está sustituyendo.
   - Peldaño 3 — **`codex exec` + `gpt-image-2`**, citando la política global del entorno del
     usuario y remitiendo a `07/23 §5` para el criterio de declaración y a qué fase del pipeline
     encaja (referencia/concept, no sprite final animado sin retoque). Quitar la frase que prohíbe
     la IA por completo; sustituirla por el criterio real ya escrito en `07/23`.
   - Quitar la remisión a `gamedev-self-generated-assets` (no aplica a GML) y sustituirla, si hace
     falta un puntero externo, por nada — esta biblioteca ya tiene todo lo necesario tras el punto
     anterior.
5. **Sección nueva en `13/09 §8 bis` o `12/09 §5.1`: «Un `.wav` como archivo, no solo en
   runtime».** Receta con el módulo `wave` de la librería estándar de Python (sin dependencias):
   generar una onda senoidal/cuadrada, escribirla con `wave.open(...).writeframes(...)`, e
   importarla con `resourcetool` (`resource create type=sound`, `sound setfile`) — verificarlo en
   vivo en esta máquina antes de publicarlo, igual que se hizo con el PNG.
6. **Una línea en `13/11 §5`** (el párrafo que define `PLACEHOLDERS.md`) que diga explícitamente
   que la lista cubre **arte y audio por igual**, cerrando el cabo suelto con `13/09 §8 bis`
   (hueco medio #6 de esta auditoría).
7. **Sección nueva o subsección en `04/10` (Visual Novel y narrativa) o `13/05`: «Retrato/avatar
   sin artista».** Mínimo: (a) recorte de un sprite de cuerpo entero ya generado por la escalera
   del encargo #4, reencuadrado a busto; (b) sourcing de retratos genéricos en los mismos bancos de
   `07/09` si el pack los trae; (c) IA generativa como referencia/concept si se va a redibujar,
   citando `07/23 §5`.

---

## Lo que comprobé y NO hacía falta

Confirmado con evidencia directa en esta sesión — **no reabrir sin evidencia nueva**:

- **La escalera de audio (`13/09 §8 bis`)** es completa, ejecutable y verificada
  (`audio_create_buffer_sound`, `tono_generar`, `ruido_generar`, `audio_free_buffer_sound`, todas
  confirmadas con `buscar.py`). Es el modelo a copiar, no a rehacer.
- **Bancos y licencias de assets libres (`07/09` completo)**: la tabla de licencias, Kenney,
  OpenGameArt, itch.io, Freesound, fuentes (OFL) y la matriz de qué formato acepta GameMaker están
  bien hechas y con fecha de verificación (31-08-2026 y 07-09-2026 según sección).
- **Legal del arte generado por IA (`07/23 §4`)**: tres fuentes primarias con fecha, verificadas —
  U.S. Copyright Office, Steamworks Content Survey, itch.io quality guidelines. No hace falta
  releerlo; cierra los temas 90-92 de `r3-arte-animacion.md` (ver siguiente sección).
- **Outline selectivo en pixel art (`13/03 §3.9`)** y **autotiling por bitmask (`13/07 §5 bis`,
  `13/02 §3.3`)**: ambos eran huecos de `r3-arte-animacion.md` (temas 9 y 20/21/24) y ahora tienen
  contenido real, no solo un enlace. Confirmado leyendo el contenido completo, no solo el título.
- **Animación (`13/03 §4`, `13/04` completo)**: timing, *frame data*, *Sequences*, *Animation
  Curves*, animación esquelética — nivel de detalle muy por encima del mínimo exigible.
- **Nine-slice, botones, barras de vida, tooltips (`13/05 §3.4-3.5`)**: técnica de implementación
  completa con código; el hueco real ahí es el arte base del panel, no la técnica.
- **Partículas nativas (`part_type_shape`, catálogo en `04/39`)**: GameMaker trae formas de
  partícula que no requieren ningún sprite — verificado, y es una vía real de VFX sin arte que la
  propia biblioteca ya explota bien.
- **Capturas de pantalla para marketing (`13/11 §4.7`)**: mecanismo (`screen_save`,
  `screen_save_part`) verificado y bien pensado (oculta HUD y overlays de depuración antes de
  disparar).
- **Herramientas de la máquina** (`magick`, Pillow, `sips`, `iconutil`, `ffmpeg`, `codex`,
  `gm-cli`): todas verificadas con ruta absoluta en esta sesión (tabla dedicada más arriba). No
  falta instalar nada.

---

## Lo que encontré desactualizado

- **`r3-arte-animacion.md`, huecos 🔴 Graves #1 (temas 90-92, «Arte generado por IA — ausencia
  total»)**: ya **no** es cierto. `07 - Ecosistema/23 - Arte generado por IA (pixel art y assets
  2D).md` existe (`git log --follow` sobre el archivo: commit «Tercera ronda: 11 documentos
  nuevos, compilación real del GML y espejo del manual completo», 2026-09-07), y su propia
  cabecera cita explícitamente que responde a ese hueco («Hueco detectado por la auditoría
  `r3-arte-animacion.md`»). Cubre upscalers (§1), las cuatro técnicas de consistencia de estilo
  con su límite real (§3) y el estado legal con tres fuentes primarias con fecha (§4) — verificado
  leyendo el documento completo, no solo su existencia. **No reabrir esos tres temas.**
- **`r4-agente-ia-gamemaker.md`, encargo #8 («Placeholders sin artista, generados por CLI»)**: el
  encargo se cumplió parcialmente — existe `12 - Utilidades e integraciones/09 - Manual del agente
  de IA - operar GameMaker con gm-cli.md §5.2` con receta de PNG verificada (`magick`, Pillow,
  `resourcetool`). Ambos documentos se commitearon juntos (`25ff725`, «Cuarta ronda: el agente de
  IA como usuario de primera clase»), pero la marca de tiempo en disco muestra el orden real de
  redacción dentro de esa sesión: el informe de auditoría es de las 19:48 del 07-09-2026 y la
  sección de destino se escribió después, a las 20:06 — la respuesta llegó tras el encargo, como
  cabía esperar. Pero **la calidad del resultado no se auditó nunca**: ni `r4-agente-ia-gamemaker.md`
  (que solo pidió «una receta verificada», y la obtuvo) ni `r4-99-cierre.md` (que no incluye este
  encargo en su tabla de encargo→estado) comprobaron si el PNG resultante era digno o basura. Esta
  ronda sí lo hizo: es basura (tema #60 de esta tabla). El encargo #4 de esta auditoría sustituye,
  no complementa, al #8 anterior.
- **`gm-cli` instalado (`v2.2.0`) frente al disponible (`v2.3.0`)**: verificado en esta sesión con
  `gm-cli --help`, que avisa de ello en cada ejecución. No es un hueco de contenido de la
  biblioteca, pero cualquier receta de `resourcetool` que se escriba a partir de ahora debería
  anotar la versión con la que se verificó, por si `v2.3.0` cambia la sintaxis de `eval`.
