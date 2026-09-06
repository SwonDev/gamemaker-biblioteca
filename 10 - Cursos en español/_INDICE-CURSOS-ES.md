# 10 · Cursos y materiales de GameMaker en español

> **Investigación realizada el 1 de septiembre de 2026.** Todos los enlaces de vídeo se han
> verificado uno a uno con `yt-dlp`; las webs, con petición HTTP directa. Nada está inventado.
> Cuando un dato no se ha podido confirmar, se dice.

---

## El resumen honesto, antes de nada

**No existe hoy un curso completo de GameMaker en español actualizado a 2026.** Ni de pago ni
gratuito. Esto no es pereza de la búsqueda: es el estado real del ecosistema.

Lo que sí existe se reparte en tres bloques, y ninguno cubre lo que el otro deja:

| Bloque | Estado | Qué aporta | Qué le falta |
|---|---|---|---|
| **Academia de Hektor Profe** | 📚 Completa pero **de GameMaker: Studio 1.4** (motor descatalogado) | **100 lecciones** en 7 cursos, la mejor pedagogía en castellano que existe | El motor cambió de arriba abajo: sin structs, sin métodos, sin handles, sin layers |
| **Altair_AML** | 🎯 **Lo más moderno en español** (2023-2024) | Introducción completa al GML actual, eventos, structs, interfaz, y un tutorial de Mega Man X | Son piezas sueltas, no un curso cerrado; no llega a LTS 2026 |
| **Vídeos sueltos y blogs** | 🧩 Dispersos, 2013-2025 | Resuelven dudas concretas: salto, colisiones, barras de vida, disparo | Sin hilo conductor, la mayoría de la era GMS 1.x / 2.x |

> 💡 **Consecuencia:** el material en español más actualizado sobre GameMaker LTS 2026 **es
> esta misma biblioteca**. Los cursos de esta carpeta sirven para *complementarla* —para oír
> los conceptos explicados en voz alta en tu idioma—, no para sustituirla. Si algo de un
> vídeo contradice a [`09 - Manual oficial`](../09%20-%20Manual%20oficial/) o a
> [`02 - Novedades 2026`](../02%20-%20Novedades%202026/), **manda el manual**.

> 🆕 **Los mejores vídeos en español ya no hace falta verlos para consultarlos.** Los
> documentos **06 a 11** recogen su contenido en forma de **apuntes técnicos**: reordenados por
> temas, con el código escrito y verificado para LTS 2026 (los subtítulos no recogen el código)
> y con anotaciones 🔺 de todo lo que ha cambiado. Se pueden leer, buscar con `grep` y consultar
> por un agente. **No son transcripciones literales**: para seguir la clase tal cual, ve al
> vídeo, que está siempre enlazado en la cabecera de cada documento.
>
> Entre los cuatro nuevos hay **un plataformas completo** (08), **la ruta de principiante más
> reciente que existe en español** (09, con vídeos de hasta octubre de 2025), **dos librerías
> imprescindibles con sus enlaces corregidos a 2026** (10) y **el mapa del IDE** (11).

---

## Los documentos de esta carpeta

| # | Documento | Qué cubre |
|---|---|---|
| 01 | [Academia de Hektor Profe](./01%20-%20Academia%20de%20Hektor%20Profe.md) | Los 7 cursos y 100 lecciones de Escuela de Videojuegos, lección a lección, con qué sigue valiendo y qué está muerto |
| 02 | [Altair_AML — GameMaker 2024 en español](./02%20-%20Altair%20AML%20-%20GameMaker%202024.md) | La serie más moderna en castellano, con enlaces y duración verificados |
| 03 | [Otros canales y series en español](./03%20-%20Otros%20canales%20y%20series.md) | Todo lo demás que se ha encontrado y verificado, con veredicto por canal |
| 04 | [Recursos escritos en español](./04%20-%20Recursos%20escritos%20en%20espa%C3%B1ol.md) | Blogs, webs, foro hispano, cursos de pago y traducciones |
| 05 | [Ruta de aprendizaje en español](./05%20-%20Ruta%20de%20aprendizaje%20en%20espa%C3%B1ol.md) | Cómo combinar todo lo anterior con esta biblioteca para aprender de verdad |
| 06 | ⭐ [**Curso de GML en vídeo — transcripción estructurada**](./06%20-%20Curso%20de%20GML%20en%20v%C3%ADdeo%20-%20transcripci%C3%B3n%20estructurada.md) | Los 52 minutos de Altair_AML **transcritos, reordenados en 14 capítulos y con el código escrito**, más 8 anotaciones de lo que ha cambiado en 2026 |
| 07 | ⭐ [**Los eventos, transcripción estructurada**](./07%20-%20Curso%20de%20eventos%20en%20v%C3%ADdeo%20-%20transcripci%C3%B3n%20estructurada.md) | Los 16 minutos sobre eventos, con el orden completo de un frame y las tres trampas del evento Draw |
| 08 | ⭐ [**Plataformas estilo Megaman X**](./08%20-%20Plataformas%20estilo%20Megaman%20X%20-%20apuntes%20de%20la%20serie%20de%20Altair.md) | **Un plataformas completo**: colisión por ejes, rampas, plataformas atravesables, wall jump, escaleras, dash, disparo cargado, daño y HUD. La serie de 6 vídeos de Altair condensada y corregida |
| 09 | 🆕 [**Plataformas para principiantes (Alas de reptil, 2025)**](./09%20-%20Plataformas%20para%20principiantes%20-%20apuntes%20de%20Alas%20de%20reptil%202025.md) | **El material más reciente en español** (hasta oct-2025): desde crear el sprite hasta colisión con muros y techos. Con los límites del enfoque explicados |
| 12 | 🆕 [**Primer contacto — decisiones al empezar (2025-2026)**](./12%20-%20Primer%20contacto%20-%20decisiones%20al%20empezar%20%282025-2026%29.md) | Apuntes del *Getting Started 2025/2026* de DragoniteSpam (subtítulos ES): qué versión, qué plantilla, GML vs visual, login. Datos al día |
| 10 | 🔧 [**Herramientas: Input y Scribble**](./10%20-%20Herramientas%20de%20la%20comunidad%20-%20Input%20y%20Scribble.md) | Las dos librerías más útiles de la comunidad. ⚠️ **Input se mudó a Codeberg**: los enlaces del vídeo dan 404 |
| 11 | 🗺️ [**El IDE en español — recorrido guiado**](./11%20-%20El%20IDE%20de%20GameMaker%20en%20espa%C3%B1ol%20-%20recorrido%20guiado.md) | Dónde está cada cosa en el IDE, con cada zona enlazada a **su página del manual en español** |

---

## Tabla rápida: ¿qué veo según lo que necesite?

| Necesito… | Mira… | Ojo con… |
|---|---|---|
| Entender qué es un videojuego y cómo se piensa | Hektor Profe · *Tu Primer Videojuego* (19 lecciones) | El IDE que sale es de 2015. Los conceptos valen, los clics no |
| Aprender a programar desde cero, en español | Hektor Profe · *El Lenguaje GML* (17 lecciones) | GML ha cambiado: hoy hay `struct`, `method`, `static`, `constructor` |
| El GML **de hoy**, explicado en español | Altair_AML · *Introducción Completa al Lenguaje* (52 min, 2024) | Es de 2024: le falta lo de LTS 2026 (handles, UI Layers, partículas nuevas) |
| Practicar mecánicas de 9 minijuegos | Hektor Profe · *Serie de Minijuegos* | Reescribe el código con GML moderno mientras lo sigues |
| Un juego completo grande, paso a paso | Hektor Profe · *Shooter TDS* (25 lecciones) y *Action RPG* (13) | Son los dos mejores del catálogo en castellano |
| Sistemas concretos (salto, colisiones, vida) | [03 · Otros canales](./03%20-%20Otros%20canales%20y%20series.md) | Verifica cada función con `buscar.py` antes de copiarla |
| **Hacer un plataformas de verdad** | [08 · Megaman X](./08%20-%20Plataformas%20estilo%20Megaman%20X%20-%20apuntes%20de%20la%20serie%20de%20Altair.md) | Es el patrón bueno: colisión por ejes. Empieza por aquí si ya sabes programar |
| **Empezar de cero, sin saber nada** | [09 · Alas de reptil](./09%20-%20Plataformas%20para%20principiantes%20-%20apuntes%20de%20Alas%20de%20reptil%202025.md) | Usa `gravity`/`vspeed`: fácil de entender, pero se rompe con velocidades altas |
| Soporte de mando o diálogos con estilo | [10 · Input y Scribble](./10%20-%20Herramientas%20de%20la%20comunidad%20-%20Input%20y%20Scribble.md) | **Input ya no está en itch.io ni en GitHub**: está en Codeberg |
| Saber dónde se cambia algo en el IDE | [11 · Recorrido por el IDE](./11%20-%20El%20IDE%20de%20GameMaker%20en%20espa%C3%B1ol%20-%20recorrido%20guiado.md) | No confundas *Preferences* (tu IDE) con *Game Options* (tu juego) |
| **Qué versión/plantilla elijo al empezar** | [12 · Primer contacto — decisiones](./12%20-%20Primer%20contacto%20-%20decisiones%20al%20empezar%20%282025-2026%29.md) | LTS 2026 + plantilla de **pixel art** + GML; el login casi nunca hace falta |
| Lo de 2026: handles, GMRT, UI Layers, Flexpanels | **No hay vídeo en español.** Ve a [`02 - Novedades 2026`](../02%20-%20Novedades%202026/) | — |

---

## Método de verificación

1. **Búsqueda amplia** en YouTube con `yt-dlp` (`ytsearch25:`) sobre seis consultas distintas
   en castellano, más búsqueda web en español.
2. **Resolución de canal** de cada vídeo candidato (`channel_id`, fecha de subida, duración)
   para descartar contenido en portugués, que aparece mezclado constantemente en los
   resultados de «Game Maker curso».
3. **Volcado de playlists** completo con `--flat-playlist` para contar los vídeos reales de
   cada serie en vez de fiarse del título.
4. **Verificación HTTP** de cada web citada, y lectura de su `sitemap.xml` cuando existía,
   para datar la última actualización real del sitio.

Lo descartado y por qué está en [03 · Otros canales](./03%20-%20Otros%20canales%20y%20series.md).
