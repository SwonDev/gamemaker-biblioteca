# r14 · Barrido exhaustivo del ecosistema: qué falta y qué no

> Ejecutado el **09-09-2026** contra la API de GitHub. El objetivo no era añadir repositorios,
> sino **saber cuáles faltan y por qué no están** — un catálogo grande no vale de nada si nadie
> sabe qué deja fuera.

## Qué se consultó

Cuatro búsquedas, unificadas por nombre completo:

| Consulta | Para qué |
|---|---|
| `language:"Game Maker Language" stars:>=25` | Lo popular escrito en GML |
| `language:"Game Maker Language" stars:10..24` | La cola media |
| `topic:gamemaker stars:>=10` · `topic:gamemaker-studio-2 stars:>=5` | Lo que se etiqueta como GameMaker aunque no sea GML |
| `gamemaker in:name,description stars:>=20` | Herramientas *sobre* GameMaker escritas en otros lenguajes |

**501 repositorios únicos.** Contrastados contra las 616 claves de `_RUTAS.json`.

## El resultado, y por qué el número bruto engaña

De los 501, **221 no estaban catalogados** tras filtrar fangames y decompilaciones. Pero
revisándolos uno a uno, la inmensa mayoría **no debe estar**:

| Categoría | Ejemplos | Por qué se queda fuera |
|---|---|---|
| **Motores y runners alternativos** | GDevelop (26 355 ★), OpenGMK, `cinnamon`, Luna, `fabricator`, xtreme3d | No son GameMaker LTS 2026: son otros motores o reimplementaciones del runtime. Interesan como contexto, no como corpus de GML |
| **Herramientas de GM 8.x / Studio 1.4** | `gm8x_fix`, `gmsched`, `GayMaker`, `Super-Mega-Engine` | Otra generación del motor. Su GML no compila hoy |
| **Portado y modding de juegos ajenos** | `gmloader-next`, `GMloader-ports`, `G3M`, `GameMaker-Anywhere` | Ejecutar juegos de otros en otras plataformas: no es desarrollar |
| **Temas del IDE y traducciones** | `dracula/gamemaker-studio`, `gms2translation`, bundle de Sublime | Ya cubierto por `07 · 01` |
| **Mal clasificados por GitHub** | Un cargador USB-C de LiPo, una placa para C64, scripts de R de análisis de redes | GitHub etiqueta como GML cualquier `.gml` suelto |
| **Fangames y decompilaciones** | Undertale, Deltarune, Pizza Tower, Mario, Sonic, Kirby | Riesgo legal y valor técnico bajo. La biblioteca ya tiene cinco como referencia de lectura y lo dice |

## Lo que SÍ faltaba, y se ha integrado

| Repositorio | Por qué importa | Estado |
|---|---|---|
| `GMShaders-Radiance-Cascades` (171 ★, Unlicense) | **Iluminación global 2D**: cobertura cero en la biblioteca | ✅ integrado + `04 · 24 §5 bis` |
| `Volumetric-HRC` (121 ★, Unlicense, 07-2026) | Volumétricos en tiempo constante | ✅ integrado |
| `2D-QuickRayTracing-GLSL` (82 ★, LGPL-2.1) | La base de los dos anteriores | ✅ integrado |
| `RadianceCascades` · `Global-Irradiance` · `PathTraced-Volumetrics` | La familia completa del autor | ✅ integrados |
| `prettylight` (86 ★, MIT) | El extremo mínimo de iluminación | ✅ integrado |
| `ColorMod` (27 ★, MIT, 2024) | Sustituye a `Chameleon`, parada desde 2022 | ✅ integrado + `13 · 03` corregido |

**El hueco de fondo no era un repositorio: era un autor.** Yaazarai —el del boletín *GM Shaders*—
no se mencionaba ni una vez en 268 documentos, y con él faltaba toda la línea de investigación de
iluminación global 2D en GameMaker.

## Lo que se decidió NO integrar, y por qué

- **`h3rb/gml-pro`** (147 ★): colección grande de shaders y utilidades, **sin licencia declarada**.
  Sin licencia explícita el código es «todos los derechos reservados». No entra al corpus.
- **`GML-Behavior-Tree`** (37 ★, sin licencia): los árboles de comportamiento ya están cubiertos
  en `04 · 31` con código propio verificado.
- **`input_legacy`** (37 ★): lo sustituyó `Input`, que sí está catalogado.
- **`3DCollisions`**: ya estaba, bajo el nombre `DS-3DCollisions`.
- **`FMODGMS`** (62 ★): FMOD ya se cubre en cuatro documentos de `07`.
- **`SpriteBrew`** y los servicios web de generación: de pago y por créditos. Anotados en
  `07 · 23 §1 bis` como contexto, no integrados.

## Un hallazgo colateral, en la organización de YoYo

`YoYoGames/GameMaker-Manual-ES` existe y se actualizó el 28-07-2026. Se comprobó si la biblioteca
llevaba meses duplicando trabajo oficial: **no** — ya estaba catalogado, medido y explicado en
`10 · 04`. Muestreo directo del repositorio oficial que confirma por qué el espejo existe:
`draw_text` está en español allí, `move_and_collide` sigue en inglés.

Lo que sí apareció fue un error de medición propio: `10 · 04` titulaba «dato medido sobre el
espejo» una tabla que describía el manual **oficial** (86 % traducido). El espejo de esta
biblioteca está al 100 %. Corregido, con las dos tablas separadas.

## Conclusión

El catálogo pasa de 608 a **616 repositorios**. La cifra importa menos que esto: de 501
repositorios revisados, **se sabe por qué está fuera cada uno de los que no entró**, y eso es lo
que convierte el catálogo en una decisión y no en una acumulación.
