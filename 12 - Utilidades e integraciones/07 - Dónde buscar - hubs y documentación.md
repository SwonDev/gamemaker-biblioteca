# 07 · Dónde buscar: hubs, foros y documentación

> El mapa de **dónde vive la información** de GameMaker. Ordenado por fiabilidad: primero las
> fuentes primarias, luego los agregadores, luego las comunidades.
>
> Verificado el 1 de septiembre de 2026.

---

## Nivel 0 · Lo que ya tienes en local (empieza aquí)

Antes de abrir el navegador:

| Necesito | Comando |
|---|---|
| ¿Existe esta función? ¿Cómo se llama? | `python3 "_indice/buscar.py" <símbolo>` |
| Todas las funciones de una familia | `python3 "_indice/buscar.py" --listar audio_` |
| La página oficial del manual | `python3 "_indice/buscar.py" --manual "surface"` |
| Cómo lo resuelve gente real | `python3 "_indice/buscar.py" --codigo "coyote"` |
| Explicación en español | `python3 "_indice/buscar.py" --texto "máquina de estados"` |
| El manual desde el CLI oficial | `gm-cli manual read "<tema>"` |

**Tienes offline:** 3 119 páginas del manual en inglés, 3 033 en español, la API completa del
runtime (2 357 funciones), 141 documentos propios en español y **41 602 archivos `.gml`** de
314 repositorios reales.

---

## Nivel 1 · Fuentes primarias oficiales

| Fuente | URL | Frecuencia | Para qué |
|---|---|---|---|
| **Notas de versión** | <https://releases.gamemaker.io/> | Cada release | **La verdad sobre qué cambió.** Al detalle, IDE y runtime |
| **Manual (LTS)** | <https://manual.gamemaker.io/lts/en/> · [es](https://manual.gamemaker.io/lts/es/) | Continuo | Referencia de la rama estable |
| **Blog oficial** | <https://gamemaker.io/en/blog> | Mensual | El **porqué** detrás de cada versión, y los anuncios grandes |
| **Roadmap** | <https://roadmap.gamemaker.io> | Trimestral | Qué viene. ⚠️ Es un GitHub Project: no se lee sin JavaScript |
| **Rastreador de bugs** | <https://github.com/YoYoGames/GameMaker-Bugs> | Diario | **Búscalo aquí antes de perder una tarde.** También la [wiki de SDK requeridos](https://github.com/YoYoGames/GameMaker-Bugs/wiki#required-sdks) |
| **Tutoriales oficiales** | <https://gamemaker.io/en/tutorials> | — | 106 tutoriales. ⚠️ **Solo en inglés** |
| **GitHub de YoYo Games** | <https://github.com/YoYoGames> | Diario | Extensiones, ejemplos, CLI, GMRT, manuales |
| **GMRT Beta** | <https://github.com/YoYoGames/GMRT-Beta> | Mensual | El runtime nuevo |
| **Centro de ayuda** | <https://help.gamemaker.io/> | — | Licencias, cuentas, facturación |
| **Marketplace** | <https://marketplace.gamemaker.io/> | — | Tienda oficial de assets |

📖 Catalogado en [`07 - Ecosistema/01 · GitHub — organización YoYoGames`](../07%20-%20Ecosistema/01%20-%20GitHub%20-%20organizaci%C3%B3n%20YoYoGames.md)
y [`05 - Referencia/01 · Tutoriales oficiales`](../05%20-%20Referencia/01%20-%20Tutoriales%20oficiales.md).

### Versiones vigentes el 1 de septiembre de 2026

| Canal | Versión | Fecha |
|---|---|---|
| **LTS** (recomendado) | **2026.0.0** · IDE 16 / runtime GMS2 23 | 21-05-2026 (actualización menor 27-05-2026) |
| **Beta** | **2026.100.0** · IDE 1139 / runtime 1090 (Release 5) | 27-08-2026 |
| **GMRT** | **0.21** | julio 2026 |
| Monthly | ❌ **Discontinuado.** Sustituido por LTS 2026; el último fue 2024.14.4 | — |

---

## Nivel 2 · Agregadores de la comunidad ★

### awesome-gamemaker — <https://github.com/bytecauldron/awesome-gamemaker>

★501 · actualizado 2026-08-23. **La mejor lista curada que existe.** 208 enlaces organizados
en 30 secciones: Data Manipulation, Native Extensions, Timing, Async, Utilities, Tools,
Debugging, Input Handling, User Interface, Localization, Physics, Sprites, Audio, Levels,
Particles, Lighting, Shaders, 3D, Sprite Stacking, Networking, Integrations, Camera,
Sequences, State Machines, Pathing, Useful Extras, Blogs, YouTube, Community.

> ✅ **Los 167 repositorios de esta lista que no teníamos están descargados** y organizados
> por tema en [`11 - Código descargado/librerias/`](../11%20-%20C%C3%B3digo%20descargado/_CATALOGO.md).

### GameMaker Kitchen — <https://www.gamemakerkitchen.com/>

Hub independiente con secciones de **Libraries, Plugins, Tools, Tutorials, Assets, Snippets y
Cookbooks**, cada entrada etiquetada y con autor. Organiza *Cookbook Jams* (la nº 5 se anunció
el 8 de septiembre de 2025). Tiene Discord propio.

Es donde aparecen cosas que **no están en GitHub**: `Cultured` (localización), `Shady`
(preprocesador GLSL), `AseSync GUI`, `GM Code Exporter`, `Texer`, `GX Types`, `Emobble`
(emojis para Scribble), los *plugins* de Input de offalynne.

### GMLScripts.com — <https://www.gmlscripts.com/script/index>

Archivo histórico de cientos de funciones de matemáticas, geometría, colisiones y dibujo, cada
una con su demo, organizadas como la documentación oficial. Mucho es de la era GMS 1.x, pero
**los algoritmos no caducan**.
📁 Descargado en `11 - Código descargado/librerias/utilidades/scripts/`.

### GameMakerLibraries — <https://github.com/JujuAdams/GameMakerLibraries>

★123. Índice de librerías mantenido por Juju Adams. ⚠️ Sin cambios desde 2022; úsalo como
complemento de awesome-gamemaker, no en su lugar.

### GameMaker Discord Community — <https://github.com/GameMakerDiscord>

Organización de GitHub donde la comunidad del Discord oficial publica sus herramientas:
`Rubber`, `Xpanda`, `GMTwitch`, `GOG.gml`, `Map.gml`, `random-level-gen-gms2`.

---

## Nivel 3 · Foros y comunidades

| Comunidad | URL | Idioma | Estado |
|---|---|---|---|
| **Foro oficial** | <https://forum.gamemaker.io/> | Inglés | ✅ Activo. Es el sucesor directo del histórico GMC; los enlaces de `forum.yoyogames.com` redirigen aquí |
| **Discord oficial** | <https://discord.gg/gamemaker> | Inglés | ✅ ~28 000 miembros. Lo más rápido para una duda |
| **r/gamemaker** | <https://www.reddit.com/r/gamemaker/> | Inglés | ✅ Activo. Alimenta gm(48) |
| **gm(48) Discord** | <https://gm48.net/discord> | Inglés | ✅ Muy activo durante las jams |
| **GameMaker Kitchen Discord** | desde <https://www.gamemakerkitchen.com/> | Inglés | ✅ Activo |
| **Comunidad GameMaker** 🇪🇸 | <https://www.comunidadgm.org/foro/> | **Español** | 🟡 Mantenido, pero con hilos de 2019-2022. Vale como archivo |
| **GMCLAN** | <https://gmclan.org/> | Polaco | ✅ Activo (⚠️ no es español, pese al nombre) |
| **Meetups locales** | <https://gamemaker.io/en/community> | Varios | ✅ Con anfitriones en España, México, Argentina, Costa Rica, Perú, Uruguay y Chile |

📖 Detalle completo, incluidos los contactos hispanos, en
[`07 - Ecosistema/10 · Comunidades y dónde preguntar`](../07%20-%20Ecosistema/10%20-%20Comunidades%20y%20d%C3%B3nde%20preguntar.md).

> ⚠️ **Regla:** Discord para lo urgente, foro para lo importante. Discord se pierde en el
> scroll; el foro es indexable y te sirve dentro de tres años.

---

## Nivel 4 · Artículos y lectura de fondo

| Recurso | Autor | Por qué |
|---|---|---|
| [2.3 Syntax in Detail](https://yal.cc/gamemaker-2-3-syntax-in-details/) | YellowAfterlife | La guía definitiva de la sintaxis moderna de GML |
| [ThoughtsOnGameMaker](https://github.com/JujuAdams/ThoughtsOnGameMaker) ★53 | Juju Adams | Reflexiones sobre el motor de quien mantiene media docena de las librerías clave. 📁 `librerias/extras/ThoughtsOnGameMaker/` |
| [GameMaker Garbage Collection](https://gist.github.com/DatZach/96a30d6ae4225f8ec152719e57aed26b) | DatZach | Cómo funciona de verdad el recolector de basura |
| [Source Control with Git & GameMaker](https://www.youtube.com/watch?v=UZG-P68xWio&list=PLSFMekK0JFgzmyDxVxj5Cctafu5UX_vUC) | FriendlyCosmonaut | Git aplicado a proyectos de GameMaker |
| [Game Resolution & Aspect Ratio Management](https://www.youtube.com/watch?v=_g1LQ6aIJFk&list=PLXkVsacazW2qvdnKNzgBLkUwlgi3FU-VO) | PixelatedPope | Resolución y escalado. 📖 Transcrito al español en [Cursos 41-44](../03%20-%20Cursos%20%28YouTube%29/_INDICE-CURSOS.md) |
| [GitHub Yacc to GML Fix](https://www.reddit.com/r/gamemaker/comments/n5m35l/a_simple_fix_for_github_incorrectly_detecting/) | r/gamemaker | Para que GitHub detecte tu repo como GML y no como Yacc |

---

## Nivel 5 · En español

| Recurso | Qué es | Estado |
|---|---|---|
| **Esta biblioteca** | 141 documentos + manual espejado + API + 314 repos | ✅ Al día (LTS 2026) |
| [Manual oficial en español](https://manual.gamemaker.io/lts/es/) | 3 033 páginas | 🟡 86 % traducido, texto de 2021-2022 |
| [Escuela de Videojuegos](https://hektorprofe.github.io/escueladevideojuegos/) | 100 lecciones, CC BY 4.0 | 🔴 GameMaker 1.4 |
| [Aprende Game Maker](https://www.aprendegamemaker.com/) | +100 artículos | 🟡 Última entrada: julio de 2023 |
| [Comunidad GameMaker](https://www.comunidadgm.org/foro/) | Foro hispano | 🟡 Archivo (2019-2022) |
| [Altair_AML](https://www.youtube.com/channel/UCMP5XWWzhJ_A6DPNKNfQVOw) | Vídeo, GML moderno | 🟡 2024 |

📖 Todo el detalle en [`10 - Cursos en español`](../10%20-%20Cursos%20en%20espa%C3%B1ol/_INDICE-CURSOS-ES.md).

---

## Rutina de 15 minutos a la semana

```
1. releases.gamemaker.io  → ¿qué hay nuevo desde tu versión?
2. gamemaker.io/en/blog   → ¿algún anuncio grande? (Photon y Colyseus salieron así)
3. Si algo te afecta      → python3 "_indice/buscar.py" <función>  y  gm-cli manual read
4. Si huele a bug         → busca en GameMaker-Bugs ANTES de investigar tú
5. Una vez al mes         → git -C awesome-gamemaker pull, a ver qué librería nueva hay
```

---

## Fuentes

Todas las URL de esta página se han comprobado por petición HTTP el 1 de septiembre de 2026.
Las versiones de GameMaker proceden de <https://releases.gamemaker.io/> y de las notas de
versión de [LTS 2026.0](https://releases.gamemaker.io/release-notes/2026/0) y
[2026.100.0](https://releases.gamemaker.io/release-notes/2026/100).
