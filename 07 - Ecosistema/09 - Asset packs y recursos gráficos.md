# Asset packs y recursos gráficos, de audio y de niveles

> Verificado a 31 de agosto de 2026. Todos los enlaces comprobados con HTTP 200 salvo indicación.
> **Aviso**: las licencias de los bancos de assets de terceros cambian. Revisa siempre la
> licencia concreta de cada asset antes de meterlo en un proyecto comercial.

---

## 1. Regla número uno: la licencia

| Licencia | ¿Uso comercial? | ¿Atribución? | Dónde se ve |
|---|---|---|---|
| **CC0 / Dominio público** | ✅ Sí | No requerida | Kenney, gran parte de OpenGameArt |
| **Apache 2.0** | ✅ Sí | Aviso de licencia | **Asset Bundles oficiales de GameMaker** |
| **MIT** | ✅ Sí | Aviso de licencia | Muchos proyectos open source de itch.io |
| **CC-BY 4.0** | ✅ Sí | **Sí, obligatoria** | OpenGameArt, itch.io |
| **CC-BY-NC / CC-BY-SA** | ❌ No comercial (NC) | Sí | Cuidado con los jams y con Steam |
| **GPL** | ✅ pero contagia | Sí | Evítalo salvo que tu juego sea GPL |

**Práctica recomendada**: mantén un archivo `CREDITS.md` dentro del proyecto con, para cada
asset externo: nombre, autor, origen (URL) y licencia. Te ahorrará un disgusto en el momento
de publicar.

**Fuentes tipográficas: la licencia del pack no es la licencia de la fuente.** Es el matiz que
más se pasa por alto —también citado de pasada en
[13 · 11 §5](<../13 - Diseño y producción de videojuegos/11 - Producción, alcance y lanzamiento.md#5--assets-y-pipeline>)—:
una fuente incluida en un asset pack CC0 no hereda automáticamente esa licencia, porque **una
fuente es software con su propio archivo de licencia**, casi siempre distinto del resto del pack.
La licencia libre más común en fuentes gratuitas es la **SIL Open Font License (OFL)**: permite
uso comercial, modificación e incrustación (*embedding*) sin coste, con dos condiciones reales —
**no se puede vender la fuente por sí sola** (sí empaquetada dentro de tu juego) y, si la
modificas y redistribuyes, la fuente modificada **también** tiene que quedar bajo OFL (es
*copyleft*, igual que GPL, pero solo para el archivo de fuente, no para el resto de tu proyecto).
Verificado en TLDRLegal, *SIL Open Font License v1.1 (OFL-1.1) Explained in Plain English* —
<https://www.tldrlegal.com/license/open-font-license-ofl-explained> (consultado 07-09-2026). Es
también la licencia mayoritaria en Google Fonts, junto a una minoría en Apache 2.0 (Roboto y
variantes) — verificado en Hacker News, hilo con cita directa a la documentación de Google Fonts
(07-09-2026). **Lo que NO cubre OFL ni ninguna fuente «gratis para uso personal»**: si una fuente
dice explícitamente «*personal use only*» o «*free for non-commercial use*», usarla en un juego
que se vende —o que lleva anuncios— es exactamente el mismo problema que CC-BY-NC de la tabla de
arriba, solo que aplicado a tipografía en vez de a arte.

**Qué significa de verdad el «contagio» de GPL.** La tabla de arriba lo resume en una celda; en
la práctica: si tu proyecto **enlaza** una librería bajo GPL —la incluyes compilada dentro de tu
ejecutable, no solo la usas como herramienta externa—, la GPL exige que **tu propio código
también se publique bajo GPL** al distribuir el juego. Es la razón de fondo por la que ninguna
librería catalogada en
[07 · 02 — Librerías esenciales de la comunidad](./02%20-%20Librer%C3%ADas%20esenciales%20de%20la%20comunidad.md)
es GPL: una dependencia GPL obligaría a abrir el código fuente completo de tu juego, algo que casi
ningún estudio comercial quiere. **MIT, Apache 2.0 y LGPL no contagian** de esta forma: MIT y
Apache permiten enlazar en un proyecto cerrado sin condición añadida (solo aviso de licencia);
LGPL permite enlazar dinámicamente sin contagiar el proyecto que la usa, aunque sí exige que la
propia librería LGPL —si la modificas— publique esos cambios. Si dudas de la licencia exacta de
una dependencia antes de enlazarla, trátala como GPL hasta comprobarlo: el coste de equivocarte al
revés es mucho mayor.

---

## 2. Bancos de assets

### 2.1 Asset Bundles oficiales de GameMaker ★ empieza por aquí

- **Descarga**: <https://gamemaker.io/en/bundles>
- **Guía de uso**: <https://gamemaker.io/en/help/articles/how-to-access-and-use-asset-bundles>
- **Licencia**: **Apache 2.0**, salvo indicación contraria en el bundle.
  Uso permitido en los juegos **y en su marketing**.
- **Hilo oficial**: <https://forum.gamemaker.io/index.php?threads/asset-bundle-discussion-thread.98642/>
- Contienen sprites, tilesets, sonidos, música y en ocasiones proyectos `.yymp` importables.
- **Ventaja decisiva**: están hechos para GameMaker, con las dimensiones y formatos adecuados,
  y gratis sin trampa.

**Prefab Library** (consumirlos sin copiar archivos):
<https://manual.gamemaker.io/lts/en/IDE_Tools/Prefab_Library.htm>
Menú **Windows → Prefab Library** → *Package Manager* → «Package source: Prefabs».

### 2.2 Kenney.nl ★ la mejor relación calidad/molestia

- **Assets**: <https://kenney.nl/assets> · por categoría: <https://kenney.nl/assets/category:2D>
- **Licencia**: **CC0** (dominio público). Sin atribución, uso comercial total, incluido
  en packs de jam.
- Estilo: vectorial plano, limpio, coherente entre packs. Ideal para prototipar.
- Incluye: plataformas, top-down, UI, efectos de partículas, sonidos, música, fuentes,
  personajes, vehículos, isométrico, y *kits* completos por género.
- Encaja con casi cualquier juego 2D y, sobre todo, **encaja consigo mismo**: todos los packs
  comparten paleta y proporción, así que puedes mezclarlos sin que se note.

### 2.3 OpenGameArt.org

- <https://opengameart.org/>
- ⚠️ **Licencia variable por asset**. Hay CC0, CC-BY, GPL y licencias propias. El filtro
  por licencia es obligatorio antes de descargar nada.
- Calidad muy desigual: hay joyas y hay *asset flips* de 2007. Filtra por valoración y fecha.
- Fuerte en: tilesets, sprites, música, efectos de sonido y modelos 3D.

### 2.4 itch.io (assets)

- Assets con tag GameMaker: <https://itch.io/game-assets/tag-gamemaker>
- Directorio general: <https://itch.io/game-assets>
- Herramientas: <https://itch.io/tools/tag-gamemaker>
- Muchos packs son de pago con tramos («paga lo que quieras», «$5+», «licencia comercial
  aparte»). **Lee la licencia antes de comprar.**
- Es donde vive el material más actual y con mejor gusto artístico en 2026.

### 2.5 Freesound.org (audio)

- <https://freesound.org/> · FAQ: <https://freesound.org/help/faq/>
- Banco de efectos de sonido colaborativo, enorme.
- Licencias: **CC0**, **CC-BY** y **Sampling+**. Cada sonido indica la suya. Filtra por licencia.
- La calidad depende del contribuidor; suele requerir edición (normalizar, recortar, quitar ruido).

### 2.6 Sección de assets del foro oficial

<https://forum.gamemaker.io/index.php?forums/gamemaker-assets.16/> (1,3K hilos)
Assets y extensiones publicados por la comunidad, con discusión. Ejemplo verificado activo
en ago 2026: *Crystal - 2D Lighting Engine* de kburkhart84.

---

## 3. Herramientas de pixel art

| Herramienta | Enlace | Precio | Notas |
|---|---|---|---|
| **Aseprite** | <https://www.aseprite.org/> · Docs: <https://www.aseprite.org/docs/> | De pago (~$20), o compila el código: <https://github.com/aseprite/aseprite> | **El estándar de facto.** Animación por *tags*, tilesets, paletas, CLI. Licencia propia: el código es de fuente abierta pero el binario oficial es de pago. |
| **LibreSprite** | <https://libresprite.github.io/> · <https://github.com/LibreSprite/LibreSprite> | **Gratis**, GPL-2.0 | *Fork* de Aseprite anterior al cambio de licencia. Interfaz casi idéntica. Excelente si no quieres pagar. |
| **Piskel** | <https://www.piskelapp.com/> | **Gratis**, en el navegador | Sin instalación, exporta spritesheets y GIF. Perfecto para empezar o para un jam. |
| **Pixelorama** | <https://pixelorama.org/> | **Gratis**, MIT | Hecho en Godot, multiplataforma, con animación y soporte de tilesets. Alternativa moderna y creciente. |

Otras menciones: **Krita** (gratis, para ilustración y fondos; se usa en proyectos reales de
GameMaker, p. ej. Witch's Night) y **GraphicsGale** (clásico gratuito en su versión legacy).

**Consejo de flujo para GameMaker**: trabaja a una resolución nativa baja (p. ej. 32×32 por
tile), exporta spritesheets con **espaciado 0** y nombres de frame coherentes, y deja el
origen de los sprites siempre en el mismo sitio (centro-abajo para personajes, centro para
objetos).

---

## 4. Tilemaps: Tiled y cómo exportar a GameMaker

### 4.1 Tiled

- **Web**: <https://www.mapeditor.org/> · Docs: <https://docs.mapeditor.org/en/stable/manual/export-yy/>
- **Código**: <https://github.com/mapeditor/tiled> · **Comprar/descargar**: <https://thorbjorn.itch.io/tiled>
- **Foro**: <https://discourse.mapeditor.org/>
- Gratis y de código abierto (GPL-2.0); en itch.io puedes pagar lo que quieras por builds.

Tiled incluye un **plugin nativo de exportación a GameMaker** (formato `.yy`), desarrollado
con colaboración de YoYo Games.

### 4.2 Cómo exportar de Tiled a GameMaker (flujo que funciona)

1. **Crea primero la room vacía en GameMaker.** Es el paso que casi todo el mundo salta y
   por eso falla. No se puede añadir una room al proyecto seleccionando un `.yy`.
2. Crea también en GameMaker, **con los mismos nombres**, los tilesets y sprites que usará
   el mapa.
3. En Tiled: **File → Export As** → formato **GameMaker** (`*.yy`).
4. Navega a la carpeta `rooms/<tu_room>/` del proyecto y **sobrescribe el archivo `.yy`**
   de esa room.
5. **Cierra y vuelve a abrir GameMaker.** Verificado en el foro de Tiled (abr 2026): tras
   sobrescribir hay que reiniciar el IDE; el recargado en caliente no siempre aplica.
6. ⚠️ **Haz copia de seguridad del proyecto antes de sobrescribir.**

### 4.3 Correspondencia de capas

| Capa en Tiled | Resultado en GameMaker |
|---|---|
| Tile layer (ortogonal, tile size = grid size, un tileset) | Tile layer |
| Tile layer con **varios tilesets** | Grupo con una tile layer por tileset (GM solo admite un tileset por capa) |
| Tile layer isométrica/hexagonal o con tile size distinto | Asset layer (sin rotación) |
| Tile layer con *collection of images* | Asset layer con sprite graphics |
| Image layer | Background layer |
| Object layer con Class | Instancias |
| Object layer sin Class (tile object) | Tile graphic o sprite graphic |

### 4.4 Gotchas conocidos

- **El nombre del tileset en Tiled debe coincidir exactamente** con el del asset en GameMaker.
- **La rotación libre no se soporta en asset layers.** Si necesitas rotar, usa tiles en capas
  de tiles con alineación a rejilla (múltiplos de 90°) o un *collection of images* tileset.
- En 2024 GameMaker cambió el formato de archivo (campos `%Name`, `type tag`, orden alfabético
  de claves). **Tiled 1.11.2 o superior** ya incorpora el plugin actualizado. Con versiones
  anteriores verás errores tipo *«A type tag field is required at the start of the JSON record»*.
- **Paralaje**: el exportador estándar no lo cubre bien. Solución comunitaria verificada:
  **gmParallax** de TobySushi — <https://github.com/TobySushi/gmParallax> — añade una opción
  de exportación extendida (*Gamemaker Extended Export*) que genera el objeto de control de
  paralaje automáticamente.

### 4.5 Alternativa sin salir de GameMaker

GameMaker tiene editor de tilesets y tile layers propio. Para proyectos pequeños o si estás
empezando, aprender el editor nativo antes que Tiled evita una capa entera de fricción.

---

## 5. Herramientas de audio

| Herramienta | Enlace | Precio | Para qué |
|---|---|---|---|
| **Audacity** | <https://www.audacityteam.org/> | **Gratis**, GPL | Editor de audio completo: grabar, recortar, normalizar, quitar ruido, convertir formatos. Imprescindible para limpiar lo que descargues de Freesound. |
| **Bfxr** | <https://www.bfxr.net/> | **Gratis**, en el navegador | Generador de SFX tipo 8-bit/chiptune. El clásico para efectos de salto, disparo, golpe, moneda. |
| **jsfxr** | <https://sfxr.me/> | **Gratis**, en el navegador | Variante moderna de sfxr con más control y presets. |
| **Bosca Ceoil** | <https://boscaceoil.net/> | **Gratis**, de código abierto | Componer música por bucles. De Terry Cavanagh (VVVVVV, Super Hexagon). Curva de aprendizaje mínima; sale música usable en minutos. |
| **Famitracker** | (búsqueda web) | Gratis | Tracker estilo NES. Se usa en proyectos reales de GameMaker. |
| **LMMS** | <https://lmms.io/> | **Gratis**, GPL | DAW completo (secuenciador, sintetizadores, mezclador) cuando Bosca Ceoil se queda corto y no quieres pagar por un DAW comercial. |
| **ChipTone** | <https://sfbgames.itch.io/chiptone> | **Gratis**, en el navegador | Generador de SFX chiptune de SFB Games; alternativa a Bfxr/jsfxr con más control sobre la envolvente. |

**Formatos para GameMaker**: `.wav` para efectos cortos (sin comprimir, carga rápida) y
`.ogg` para música (comprimido, ocupa poco). Evita `.mp3` por problemas de licencia históricos
y por el *gap* al hacer bucle.

> ⚠️ **Wwise no tiene integración mantenida para GameMaker.** Las dos únicas envolturas
> encontradas están abandonadas: `CaKlassen/gmwwise` (★26, sin *commits* desde 2022-10) y
> `Fatdazz/lib-GMWwise` (★2, sin *commits* desde 2021) — verificado con la API de GitHub el
> 6 de septiembre de 2026. Si necesitas mezcla/*ducking*/variaciones sin escribirlas a mano, usa
> los buses nativos del motor + **Vinyl**, o el **GMEXT-FMOD** oficial si de verdad hace falta
> middleware de terceros: ver [12 · 05 §5](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte,%20audio%20y%20niveles.md).

---

## 6. Fuentes y tipografía

Las fuentes se importan en GameMaker como cualquier asset, pero **revisa la licencia**:

- **Google Fonts** — casi todas con licencia **SIL Open Font License** (uso comercial libre).
  Es la opción segura por defecto para juegos en 2026.
- **Kenney Fonts** — CC0, incluidas en su web.
- ⚠️ Ojo con las fuentes «gratuitas» de bancos de dudosa procedencia: hay fuentes
  *shareware* y con licencia solo personal circulando como si fueran libres.

### 6.1 Tipografías de PÍXEL — que no son las de Google Fonts

Google Fonts es la opción segura… para texto vectorial. En un juego de pixel art una fuente
vectorial escalada **hierve**: el rasterizador la suaviza y los bordes bailan al mover la cámara.
Lo que hace falta es una tipografía **diseñada a tamaño de píxel**, que se usa a su tamaño nativo
o a múltiplos enteros de él.

Comprobadas el 09-09-2026, con la licencia leída en la propia página:

| Tipografía | Autor | Licencia | Nota |
|---|---|---|---|
| [monogram](https://datagoblin.itch.io/monogram) | datagoblin | **CC0** (*Creative Commons Zero v1.0 Universal*, dicho en la ficha) | Monoespaciada, 5×7, con acentos y símbolos. La opción por defecto si no quieres pensar |
| [m5x7](https://managore.itch.io/m5x7) · [m6x11](https://managore.itch.io/m6x11) | Daniel Linssen | **CC0** («free to use») | Dos tamaños de la misma familia; m6x11 lee mejor a tamaño pequeño |
| [Pixel Operator](https://www.dafont.com/pixel-operator.font) | Jayvee Enaguas | ⚠️ **compruébala** | Su página de DaFont muestra a la vez «100% Free», «Donationware» y «Free for personal»: DaFont agrupa varias fuentes por página y esas etiquetas no siempre son de la que buscas. Abre el `readme` del `.zip` antes de publicar |
| [Kenney Fonts](https://kenney.nl/assets/kenney-fonts) | Kenney | **CC0** | Ya citadas arriba; incluyen varias de píxel |

> 🔴 **La trampa que las hace inútiles si no la conoces**: importar una fuente de píxel y dejar
> que GameMaker la interpole la deja igual de borrosa que una vectorial. Va con
> `gpu_set_texfilter(false)` y a tamaño nativo o múltiplo entero — la explicación completa, con
> la escala de ventana, en
> [`13 · 03 §1.6`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/03%20-%20Pixel%20art%20y%20resolución.md).
>
> Y si además la quieres **con tildes y eñes garantizadas**, la vía que no depende de ninguna
> licencia ajena es hornear tu propia hoja de glifos: receta completa en
> [`12 · 09`, Trampa 12](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md),
> con el generador ya escrito.

Para texto con caracteres CJK (chino, japonés, coreano) en GameMaker, consulta el tutorial
específico del foro:
<https://forum.gamemaker.io/index.php?threads/handling-cjk-text-in-gms-2.100032/>

---

## 7. Tabla resumen verificada

| Recurso | Enlace | Licencia | Estado |
|---|---|---|---|
| Asset Bundles oficiales | <https://gamemaker.io/en/bundles> | Apache 2.0 | ✅ |
| Guía de Asset Bundles | <https://gamemaker.io/en/help/articles/how-to-access-and-use-asset-bundles> | — | ✅ |
| Prefab Library (manual) | <https://manual.gamemaker.io/lts/en/IDE_Tools/Prefab_Library.htm> | — | ✅ |
| Kenney | <https://kenney.nl/assets> | CC0 | ✅ |
| Kenney por categoría | <https://kenney.nl/assets/category:2D> | CC0 | ✅ |
| OpenGameArt | <https://opengameart.org/> | Variable | ✅ |
| Freesound | <https://freesound.org/> | CC0/CC-BY/Sampling+ | ✅ |
| itch.io assets | <https://itch.io/game-assets> | Variable | ✅ |
| Assets tag GameMaker | <https://itch.io/game-assets/tag-gamemaker> | Variable | ✅ |
| Aseprite | <https://www.aseprite.org/> | De pago / compilar | ✅ |
| Aseprite (código) | <https://github.com/aseprite/aseprite> | Fuente abierta | ✅ |
| LibreSprite | <https://libresprite.github.io/> | GPL-2.0 | ✅ |
| Piskel | <https://www.piskelapp.com/> | Gratis | ✅ |
| Pixelorama | <https://pixelorama.org/> | MIT | ✅ |
| Tiled | <https://www.mapeditor.org/> | GPL-2.0 | ✅ |
| Tiled → GameMaker (docs) | <https://docs.mapeditor.org/en/stable/manual/export-yy/> | — | ✅ |
| Tiled (itch.io) | <https://thorbjorn.itch.io/tiled> | Paga lo que quieras | ✅ |
| Tiled (foro) | <https://discourse.mapeditor.org/> | — | ✅ |
| gmParallax | <https://github.com/TobySushi/gmParallax> | — | ✅ |
| Audacity | <https://www.audacityteam.org/> | GPL | ✅ |
| Bfxr | <https://www.bfxr.net/> | Gratis | ✅ |
| jsfxr | <https://sfxr.me/> | Gratis | ✅ |
| Bosca Ceoil | <https://boscaceoil.net/> | Código abierto | ✅ |
| Foro — GameMaker Assets | <https://forum.gamemaker.io/index.php?forums/gamemaker-assets.16/> | Variable | ✅ |
| ~~Pixelorama GitHub (ruta antigua)~~ | ~~github.com/pixelorama/Pixelorama~~ | — | ❌ 404 |
| ~~OpenGameArt términos~~ | ~~opengameart.org/content/terms-of-use~~ | — | ❌ 404 |
| ~~Kenney tutorials~~ | ~~kenney.nl/tutorials~~ | — | ❌ 404 |

---

## 7 bis. Modelos 3D libres — el hueco que dejaba `04 · 29`

Esta biblioteca tiene receta de [3D en GameMaker](../04%20-%20Recetas%20por%20género/29%20-%203D%20en%20GameMaker.md)
—cámara, z-buffer, *culling*, niebla, matrices y carga de `.obj`— y hasta hoy **ninguna fuente de
modelos**. Un agente al que le pidan un juego 3D se quedaba igual que con los sprites: sin nada
que poner.

Las cuatro que sirven, comprobadas el 09-09-2026 (código 200 y licencia leída en el propio sitio):

| Fuente | Qué tiene | Formatos | Licencia |
|---|---|---|---|
| [Kenney 3D](https://kenney.nl/assets/category:3D) | Kits completos y coherentes entre sí: ciudad, mazmorra, naves, prototipado | OBJ · FBX · glTF | **CC0** |
| [Quaternius](https://quaternius.com/) | Packs temáticos con estilo propio: personajes animados, naturaleza, vehículos | OBJ · FBX · glTF · Blend | **CC0** (declarado en su portada) |
| [Kay Lousberg](https://kaylousberg.itch.io/) | Kits *low-poly* muy pulidos, con personajes riggeados | glTF · FBX · OBJ | **CC0** |
| [ambientCG](https://ambientcg.com/) | **Texturas PBR**, no modelos: suelos, paredes, metal, tela | PNG/JPG por canal | **CC0** («Public Domain», dicho en su portada) |
| [Poly Pizza](https://poly.pizza/) | Buscador con miles de modelos sueltos, heredero de Google Poly | glTF/GLB | **Mezclada: CC0 y CC-BY** — mira la ficha de CADA modelo |

> 🔴 **Poly Pizza es la excepción y por eso va la última.** Las otras cuatro son CC0 de arriba
> abajo; ahí la licencia es **por modelo**, y hay CC-BY entre medias. Bajar sin mirar la ficha es
> cómo se acaba publicando con una atribución que faltaba. La regla de §1 vale aquí doble.

**Cómo llegan a GameMaker**, que es la parte que no cuenta ninguna de esas webs:

- `.obj` va directo con el cargador de
  [`04 · 29 §2`](../04%20-%20Recetas%20por%20género/29%20-%203D%20en%20GameMaker.md) — es texto plano
  y se convierte a *vertex buffer* en la carga.
- glTF/FBX **no** los lee GameMaker: pasan por [`BBMOD`](https://github.com/blueburncz/BBMOD)
  (catalogado en `11 - Código descargado`), que los convierte a su propio formato binario.
- Las texturas PBR de ambientCG son más de las que GameMaker 2D-con-3D suele necesitar: coge el
  *color* y, como mucho, el mapa normal para `04 · 24`.

> ⚠️ **Antes de bajar un kit entero, mira el presupuesto de triángulos de
> [`04 · 29`](../04%20-%20Recetas%20por%20género/29%20-%203D%20en%20GameMaker.md)**: GameMaker
> dibuja 3D, pero no es un motor 3D, y un modelo de 40 000 triángulos pensado para Unity se come
> el framerate sin avisar.

---

## 8. Bancos de música y SFX ya hechos (no generadores)

La sección 5 lista **herramientas para crear** audio; esto es dónde bajar **audio ya producido**.

| Recurso | Enlace | Licencia | Nota |
|---|---|---|---|
| **Incompetech** (Kevin MacLeod) | <https://incompetech.com/music/royalty-free/> | **CC-BY 4.0** ⚠️ | Música de fondo por géneros. Gratis **dando crédito** ("*Título* – Kevin MacLeod, incompetech.com, CC BY 4.0"), o licencia de pago para omitirlo |
| **Pixabay Music / SFX** | <https://pixabay.com/music/> · <https://pixabay.com/sound-effects/> | **Pixabay License** | Comercial **sin atribución**; no revender el audio tal cual. Sin registro |
| **Sonniss — GDC Game Audio Bundle** | <https://sonniss.com/gameaudiogdc> | **Royalty-free, comercial ilimitado, sin atribución** (prohíbe entrenar IA) | Gigabytes de SFX profesional en WAV. El bundle más reciente es **2024** |

> ⚠️ **CC-BY-NC = no comercial** (aparece en Freesound y OGA): no vale para un juego que vendas o
> monetices (los anuncios cuentan). **CC-BY** obliga a acreditar. Guarda el crédito en `CREDITS.md`
> desde el minuto uno. Nota histórica: **FreePD.com cerró en 2025**; ignora recomendaciones que la citen.

---

## 9. Iconos de UI y habilidades

| Recurso | Enlace | Licencia | Nota |
|---|---|---|---|
| **Game-icons.net** | <https://game-icons.net/> | **CC-BY 3.0** ⚠️ | 4.180 iconos vectoriales (SVG/PNG) de habilidades, ítems y HUD. Comercial **con atribución** ("Lorc, Delapouite & contributors"). Exporta PNG al tamaño de tu UI |
| **Kenney — UI packs** | <https://kenney.nl/assets/category:2D> | **CC0** | Botones, paneles y cursores sin atribución |

---

## 10. Paletas de color

Elegir una paleta coherente **antes** de pintar ahorra rehacer sprites.

| Recurso | Enlace | Licencia | Nota |
|---|---|---|---|
| **Lospec — Palette List** | <https://lospec.com/palette-list> | **Libre** (los colores no son copyrightables) | +4.400 paletas pixel-art; exporta a HEX/PNG/GPL/PAL para GIMP, Aseprite o Paint.NET |
| **Coolors** | <https://coolors.co/> | **Libre** | Generador de esquemas para UI y arte; bloquea colores y genera armonías |

---

## 11. Qué formato importa GameMaker (bájalo ya correcto)

Datos del **manual oficial LTS 2026** (Sprites / Sounds / Videos):

| Tipo | Formatos que acepta | Qué bajar |
|---|---|---|
| **Imágenes** | `PNG`, `JPG`, `GIF`, vectorial `SVG`/`SWF`, esqueletal `Spine` | **PNG** con transparencia. Varias imágenes = *frames* del mismo sprite |
| **Audio** | `WAV`, `MP3`, `OGG` | **WAV** para SFX cortos, **OGG** para música (evita `.mp3` por licencia y *gap* al hacer bucle) |
| **Vídeo** | contenedores `.mp4`/`.avi`/`.mkv` (GameMaker usa los códecs del sistema, no trae ninguno) | **`.mp4` (H.264)**. ⚠️ Algunos códecs cobran licencia según ingresos/plataforma |
| **Fuentes** | `TTF`, `OTF` | Para pixel art, tamaño nativo y sin antialias |
