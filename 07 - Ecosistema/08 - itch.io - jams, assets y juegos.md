# itch.io — jams, assets y juegos hechos con GameMaker

> Verificado a 31 de agosto de 2026.
> itch.io: <https://itch.io/> · Jams: <https://itch.io/jams> · Documentación de creadores: <https://itch.io/docs/creators/faq>

---

## 1. Por qué itch.io y GameMaker encajan tan bien

- El target **HTML5** de GameMaker genera una carpeta autocontenida que itch.io sirve tal cual.
  Es el camino más corto entre «terminé el juego» y «la gente lo está jugando».
- itch.io no exige revisión, no cobra comisión fija (el reparto por defecto es 0 %, tú eliges)
  y permite juegos de pago, gratis, *name your price* y builds privadas para beta testers.
- Es la plataforma por defecto de casi todas las game jams, incluidas las específicas de
  GameMaker.

---

## 2. Cómo publicar un juego de GameMaker en itch.io

### 2.1 Flujo recomendado (export manual, sin butler)

1. **Compila para HTML5** en GameMaker. El resultado es una carpeta con `index.html`.
2. **Comprímela en `.zip`**. Importante: `index.html` debe quedar en la **raíz del zip**,
   no dentro de una subcarpeta. Es el fallo número uno.
3. En itch.io: **Dashboard → Create new project**.
4. Rellena:
   - **Title & slug** (la URL permanente; piénsatelo, el slug es difícil de cambiar).
   - **Classification**: `Games`, o `Tools` / `Assets` según corresponda.
   - **Kind of project**: HTML5 (o downloadable).
5. **Uploads → Upload files**, sube el `.zip` y marca **«This file will be played in the browser»**.
6. Ajusta el visor: dimensiones, `Embed in page`, orientación, **Enable fullscreen button**,
   y activa *SharedArrayBuffer* solo si tu juego lo necesita.
7. **Pricing**:
   - `$0 or donate` → gratis, con opción de que te paguen lo que quieran.
   - `Paid` → fijas precio. itch.io cobra una comisión reducida y tú marcas el reparto.
8. **Visibility & access**: `Public` o `Draft` mientras terminas.
9. Publica.

### 2.2 Subir con butler (CLI) — recomendable para builds grandes e iterativas

`butler` es la herramienta oficial de itch.io para subir builds por línea de comandos.
Ventajas: subidas **diferenciales** (solo sube lo que cambió), versionado por canal y
posibilidad de automatizarlo.

- Documentación: <https://itch.io/docs/butler/>

```bash
# 1. Autenticarse (una sola vez)
butler login

# 2. Subir la carpeta exportada. <usuario>/<juego> es el slug de la página.
#    El canal separa builds: windows, html5, linux, beta...
butler push ./export/html5 <tu-usuario>/<tu-juego>:html5

# 3. Marcar una build como estable (opcional)
butler push ./export/html5 <tu-usuario>/<tu-juego>:html5 --userversion 1.0.3
```

Buenas prácticas con butler:

- **Un canal por plataforma**: `:html5`, `:windows`, `:mac`, `:linux`.
- Marca en la página del proyecto qué canal es el recomendado.
- Integra el push en tu pipeline de compilación para no subir a mano nunca más.

### 2.3 Checklist antes de publicar

- [ ] ¿Se ve bien el juego a pantalla completa?
- [ ] ¿Funciona con teclado **y** mando, o has documentado que solo teclado?
- [ ] ¿Hay capturas de pantalla y *cover image* decentes? Es lo primero que se ve.
- [ ] ¿Has rellenado los tags (`GameMaker`, género, `Pixel Art`…)? Es como te encuentran.
- [ ] ¿Has escrito una descripción corta y clara arriba del todo?
- [ ] ¿Has indicado licencia de código y de assets?
- [ ] ¿Has probado el build descargado en un navegador limpio?

---

## 3. Game jams relevantes

### 3.1 gm(48) — la jam de GameMaker ★ la más recomendable

<https://gm48.net/>

- **Exclusiva de GameMaker**, trimestral, **48 horas**, remota.
- **Patrocinada oficialmente por GameMaker desde 2016.**
- 6.146 desarrolladores registrados, 436 equipos. 50 ediciones celebradas.
- Organizada por Peter Jørgensen (<https://peterchrjoergensen.dk>).
- Tiene **feedback obligatorio**: para entrar en el ranking hay que escribir críticas a al menos
  10 juegos. Es lo que la hace tan formativa.

**Próximas ediciones (verificadas):**

| Edición | Inicio | Fin | Resultados |
|---|---|---|---|
| **50th gm(48)** | **12 sep 2026, 00:00 UTC** | 14 sep 2026, 00:00 UTC | 28 sep 2026, 20:00 UTC |
| 51st gm(48) | 14 nov 2026, 00:00 UTC | 16 nov 2026, 00:00 UTC | 30 nov 2026, 20:00 UTC |

La votación del tema de la 50ª va del 29 de agosto al 5 de septiembre de 2026.

Enlaces útiles:
- Calendario: <https://gm48.net/game-jam-schedule>
- Cómo empezar: <https://gm48.net/getting-started> · Normas: <https://gm48.net/rules>
- **Juegos open source para estudiar**: <https://gm48.net/open-source-gamemaker-projects>
- Recursos y tutoriales: <https://gm48.net/gamemaker-resources-tutorials-and-assets>
- Discord: <https://gm48.net/discord>

### 3.2 GMTK Game Jam

- Web: <https://gmtkgamejam.com/>
- **Edición 2026** (ya finalizada): <https://itch.io/jam/gmtk-jam-2026> — se celebró del
  **22 al 26 de julio de 2026**. Resultados publicados.
- Formato: 4 días, anual, multitud de motores, escala enorme y showcase en YouTube curado
  por Game Maker's Toolkit.
- Para GameMaker: excelente visibilidad, pero competencia brutal. Úsala para aprender, no
  para ganar.

### 3.3 Ludum Dare

- Web: <https://ludumdare.com/> (el dominio `ldjam.com` **no responde** — usa `ludumdare.com`)
- Trimestral, 48 h, con competiciones separadas para **solo** y para **equipos**.
- GameMaker fue **patrocinador de Ludum Dare 57** (2025).
- ⚠️ **Aviso importante verificado**: se ha anunciado que **Ludum Dare finalizará
  oficialmente en octubre de 2028**. Si la usas, que sea ahora.

### 3.4 GMC Jam — la jam del foro oficial

- <https://forum.gamemaker.io/index.php?forums/gmc-jam.9/> (179 hilos, 20,7K mensajes)
- Subforo *Community Jams*: <https://forum.gamemaker.io/index.php?forums/community-jams.31/>
- Presentación: <https://forum.gamemaker.io/index.php?threads/gmc-jam-welcomes-you.35/>
- Plazos más relajados que gm(48). Ideal si 48 h te resultan imposibles.

### 3.5 Otras

- **Micro Jam**: jam quincenal de juegos pequeños en 48 h, con premios de GameMaker.
  Anunciada en el blog oficial: <https://gamemaker.io/en/blog/micro-jam>
- **Reddit Daily Games Hackathon**: hackathon virtual con premios, impulsada desde el foro:
  <https://forum.gamemaker.io/index.php?threads/join-the-reddit-daily-games-hackathon.122243/>
- **Global Game Jam**: presencial en sedes físicas, multitud de motores.
- Listado general de jams abiertas: <https://itch.io/jams>

### 3.6 Por qué GameMaker es bueno para jams (y cuándo no)

**A favor:**

- El bucle *sprite → objeto → room → run* es rapidísimo. En 20 minutos tienes algo moviéndose.
- Sprites y tilesets se pueden crear en el propio editor.
- El export HTML5 permite tener un build jugable al instante para que otros lo prueben.
- Hay décadas de tutoriales para exactamente los problemas de una jam: colisión de tiles,
  cámaras, transiciones de room, pausa.

**En contra:**

- El arranque en frío del IDE y los tiempos de compilación no son los más rápidos.
- Algunos targets requieren configuración de SDK que en 48 h no te da tiempo.

**Regla para jams**: haz un bucle jugable mínimo en las primeras 4 horas. Todo lo demás
es opcional.

---

## 4. Dónde encontrar assets para prototipar

### 4.1 Asset Bundles oficiales de GameMaker ★

- Descarga: <https://gamemaker.io/en/bundles>
- Guía de uso: <https://gamemaker.io/en/help/articles/how-to-access-and-use-asset-bundles>
- **Licencia**: **Apache 2.0** salvo indicación contraria explícita en el bundle.
  Se pueden usar en juegos comerciales **y en su marketing**.
- Incluyen sprites, sonidos, música, tilesets y a veces proyectos `.yymp` importables.
- Hilo de discusión en el foro:
  <https://forum.gamemaker.io/index.php?threads/asset-bundle-discussion-thread.98642/>

### 4.2 Prefab Library (dentro del IDE)

Desde la versión 2024.13 los bundles se consumen también como **Prefabs**, sin copiar archivos
al proyecto:

- Manual: <https://manual.gamemaker.io/lts/en/IDE_Tools/Prefab_Library.htm>
- Se abre desde el menú **Windows → Prefab Library** → *Package Manager*, con «Package source»
  en **Prefabs**.
- Los assets se referencian desde la colección original al compilar; hay que añadir la
  *Collection Reference* al proyecto.
- El equipo ha anunciado un **Prefab Builder** para crear y compartir colecciones propias
  (<https://gamemaker.io/en/blog/update-spring-2026>).

### 4.3 itch.io assets

- Assets con tag GameMaker: <https://itch.io/game-assets/tag-gamemaker>
- Directorio general de assets: <https://itch.io/game-assets>
- Herramientas para GameMaker: <https://itch.io/tools/tag-gamemaker>
- ⚠️ **Revisa la licencia de cada pack.** En itch.io conviven CC0, CC-BY, licencias
  «solo uso no comercial» y licencias de pago por tramos. No hay una licencia por defecto.

### 4.4 Otros (detalle en `09 - Asset packs y recursos gráficos.md`)

| Recurso | Enlace | Licencia |
|---|---|---|
| Kenney | <https://kenney.nl/assets> | CC0 (dominio público) |
| OpenGameArt | <https://opengameart.org> | Varía por asset — revisar |
| Freesound | <https://freesound.org> | CC0 / CC-BY / Sampling+ — revisar |

---

## 5. Juegos hechos con GameMaker en itch.io que merece la pena estudiar

### 5.1 Proyectos open source (con código descargable)

| Juego / proyecto | Enlace | Por qué estudiarlo | Licencia |
|---|---|---|---|
| **Epsilon Engraving Engine** | <https://yaru.itch.io/epsilon-engraving> | Framework educativo para fangames tipo Undertale/Deltarune. Incluye **capítulo completo de varias horas** con batallas, tiendas, diálogos, rutas pacífica/violenta, y el `.yyz` con el código fuente. Usa las buenas prácticas recomendadas (funciones, introspección, enums). Actualizado en feb 2026. | Consultar en su página |
| **Sugary Spire: Exhibition Night** | <https://en-painter.itch.io/sugary-spire-exhibition-night> | Plataformas de movimiento rápido con pulido altísimo, 4 niveles, música original. Valorado 4,8/5 (72 votos). Hecho con GameMaker + Aseprite. | Código MIT · Assets CC-BY 4.0 |
| **Pollen** | <https://morpho-monarchy.itch.io/pollen> | Biblioteca de partículas **open source y con recarga en vivo**, basada en Vinyl de Juju Adams. Ejemplo de arquitectura de librería moderna para GameMaker (v2024.14.2). Mar 2026. | MIT |
| **Witch's Night** | <https://piktogram.itch.io/witchs-night-full> | Shoot'em up completo de 6 fases con jefes, mejoras y 6 potions. Hecho con GameMaker Studio 2 + Aseprite + Krita + Famitracker. Declaración explícita de «sin contenido generado por IA». | Código MIT · Assets CC-BY-NC 4.0 |
| **Open Shapes and Beats** | <https://github.com/matty147/OSAB> + <https://inkk-ing.itch.io/osab> | Bullet-hell rítmico con editor de niveles. Proyecto escolar de dos años, GameMaker v2024.8.1. | MIT |

### 5.2 Directorios para explorar

- **Todos los juegos hechos con GameMaker**: <https://itch.io/games/made-with-gamemaker>
- **Gratis y open source**: <https://itch.io/games/free/made-with-gamemaker/tag-open-source>
  (39 resultados verificados)
- **Open source de las jams gm(48)** ★ — la mejor fuente para aprender:
  <https://gm48.net/open-source-gamemaker-projects>
  Incluye proyectos `.yyp` completos con código GML, sprites y assets. Juegos hechos en 48 h:
  verás *scoping* agresivo y prototipado eficiente, justo lo que se aprende peor en tutoriales.

### 5.3 Cómo estudiar un proyecto ajeno (método)

1. Descarga el `.yyz` o clona el repo.
2. **Juega 20 minutos** antes de mirar una línea de código. Anota qué te sorprende.
3. Abre el árbol de assets y localiza el objeto jugador. Lee solo sus eventos.
4. Busca el objeto *controller* global (suele haber uno). Ahí está la arquitectura.
5. **No copies y pegues.** Reescribe la idea en tu propio proyecto. Es lo que fija el
   conocimiento.
6. Respeta la licencia: MIT y CC0 son permissivas; CC-BY exige atribución; CC-BY-NC
   **prohíbe uso comercial**.

---

## 6. Resumen de enlaces verificados

| Recurso | Enlace | Estado |
|---|---|---|
| itch.io | <https://itch.io/> | ✅ |
| Jams de itch.io | <https://itch.io/jams> | ✅ |
| butler (docs) | <https://itch.io/docs/butler/> | ✅ |
| gm(48) | <https://gm48.net/> | ✅ |
| gm(48) calendario | <https://gm48.net/game-jam-schedule> | ✅ |
| gm(48) proyectos open source | <https://gm48.net/open-source-gamemaker-projects> | ✅ |
| GMTK Game Jam (oficial) | <https://gmtkgamejam.com/> | 🔴 **no responde** (500 / timeout, comprobado 07-09-2026); usa la edición en itch.io de abajo o <https://gamemakerstoolkit.com/jam/> |
| GMTK Game Jam 2026 (itch.io) | <https://itch.io/jam/gmtk-jam-2026> | ✅ finalizada |
| Ludum Dare | <https://ludumdare.com/> | ✅ (fin anunciado en oct 2028) |
| ~~ldjam.com~~ | ~~<https://ldjam.com>~~ | ❌ **no responde** |
| GMC Jam (foro) | <https://forum.gamemaker.io/index.php?forums/gmc-jam.9/> | ✅ |
| Asset Bundles oficiales | <https://gamemaker.io/en/bundles> | ✅ |
| Prefab Library (manual) | <https://manual.gamemaker.io/lts/en/IDE_Tools/Prefab_Library.htm> | ✅ |
| Juegos made with GameMaker | <https://itch.io/games/made-with-gamemaker> | ✅ |
| Assets tag GameMaker | <https://itch.io/game-assets/tag-gamemaker> | ✅ |
| Herramientas tag GameMaker | <https://itch.io/tools/tag-gamemaker> | ✅ |
| ~~itch.io/jams/tag-gamemaker~~ | ~~<https://itch.io/jams?tag=gamemaker>~~ | ❌ **404** |
