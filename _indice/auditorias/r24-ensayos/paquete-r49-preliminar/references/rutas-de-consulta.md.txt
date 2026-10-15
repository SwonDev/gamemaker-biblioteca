# Rutas de consulta

Lee para elegir género, disciplina, material de aprendizaje o documento de la biblioteca.

## Qué leer según la tarea

El detalle por disciplina, en orden de lectura, está en
[mapa-disciplinas.md](mapa-disciplinas.md). El índice completo de
documentos, generado del disco, en [indice-documentos.md](indice-documentos.md).

| Te piden… | Empieza por |
|---|---|
| Escribir GML que haga X | `buscar.py` por cada símbolo → `11 - Código descargado/_CATALOGO.md` (¿ya hay librería?) → `05 - Referencia/04 - Convenciones y estilo GML.md` |
| Un juego completo, de principio a fin | `04 - Recetas por género/00 - Anatomía de un juego completo.md` y después la receta del género |
| Un juego de género X | `04 - Recetas por género/` — **59 recetas**: los géneros clásicos (plataformas, RPG, roguelike, metroidvania, tower defense, puzle, shoot'em up, carreras, gestión, ritmo, sigilo, horror, granja, idle) más beat'em up, aventura gráfica, deportes, lucha, souls-like, colonia, party games y bullet heaven/autobattler/deckbuilder; y los sistemas transversales: **el nivel como mapa de texto** (la única vía de montar un nivel sin abrir el editor de salas), **puertas, llaves y placas de presión** (el puzle de sala), combate (cuerpo a cuerpo, a distancia, por turnos, no letal), daño y estados, enemigos y director, habilidades, traversal, pathfinding, VFX, tutorial, transiciones y pausa, audio reactivo, modding, eje Z falso, selección de nivel, metajuego y live-ops |
| Diseñar: mecánicas, niveles, arte, UI, sonido, historia | `13 - Diseño y producción de videojuegos/` (mapa en `mapa-disciplinas.md`) |
| Desarrollo largo con IA, varios harnesses, gauntlet, crítica A/B, colas o retomar una pausa | `13 - Diseño y producción de videojuegos/29 - Desarrollo con IA - orquestación, crítica y evidencia.md` antes de despachar trabajo; después `12/09` y `13/10` para las puertas técnicas |
| Búsqueda, clasificación o deduplicación de código, información y recursos; contexto/tokens | `12 - Utilidades e integraciones/11 - Búsqueda multimodal con EmbeddingGemma 2 - contexto y recursos para agentes.md`: literal frente a significado, MCP real, fuentes verificadas, índices acotados y fallback |
| Búsqueda semántica o RAG como función de producto | `13/29 §11.1` y `12/11`: consumidor real, servicio/modelo conservado, reserva fuera del corpus, fidelidad y recuperación separadas |
| Estructurar el proyecto para que crezca | `13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md` |
| HTTP, callbacks asíncronos, respuestas tardías, timeout o reintentos | `12 - Utilidades e integraciones/12 - HTTP asíncrono - estados, propiedad y respuestas tardías.md`: ID, progreso frente a terminal, HTTP frente a aceptación, propiedad y persistencia |
| Explicar un concepto del motor | `01 - Fundamentos/` → la página del manual en `09 - Manual oficial/manual-lts-2026-es/` |
| «No compila» o «se comporta raro» con código antiguo | `01 - Fundamentos/03 - Handles - el cambio clave de 2026.md` → `02 - Novedades 2026/02 - Cambios en GML 2026.md` → `buscar.py` (¿obsoleta?) → github.com/YoYoGames/GameMaker-Bugs |
| Qué librería, extensión o herramienta usar | `12 - Utilidades e integraciones/_INDICE-UTILIDADES.md` → `11 - Código descargado/_CATALOGO.md` → `07 - Ecosistema/` |
| Fijar resolución, escala de ventana, tamaño de la GUI o pantalla completa | `13 - …/03 - Pixel art y resolución.md` §1.6 — **antes** de escribir el primer `window_set_size()`; a ojo sale una escala no entera y el pixel art «hierve» |
| Assets libres (arte, audio, tiles, fuentes) | `07 - Ecosistema/09 - Asset packs y recursos gráficos.md` |
| **Operar GameMaker siendo un agente** (crear recursos, eventos, compilar, depurar sin ver la pantalla) | `12 - Utilidades e integraciones/09 - Manual del agente de IA - operar GameMaker con gm-cli.md` |
| Publicar, exportar, tiendas | `05 - Referencia/02 - Publicar y exportar.md` → `05 - Referencia/05 - Entregar el juego…` (firmar, notarizar, `steamcmd`, Play, App Store) → `13 - …/11 - Producción, alcance y lanzamiento.md` |
| Publicar en **consola** (Nintendo, PlayStation, Xbox) | `05 - Referencia/06 - Publicar en consolas…` — trámite, licencia, *lotcheck*, TRC/XR, y dónde empieza el NDA |
| Marcas, *fan games*, EULA, menores | `13 - …/25 - Legal de terceros…` y `13 - …/20 - Modelo de negocio…` |
| No tengo sprites ni sonidos | `12 - …/09 §5.2` (gráficos) y `13 - …/09 §8 bis` (sonido sintetizado por código) |
| Qué cambió en 2026, qué versión usar | `02 - Novedades 2026/01 - Resumen LTS 2026.0.md` → [runtime objetivo](entorno-y-fuentes.md#fijar-el-runtime-objetivo-antes-de-confiar-en-el-índice); contrasta las release notes aplicables |
| Enseñar a alguien que aprende | `RUTA.md`: sitúa el nivel por lo que sabe hacer y da solo material de su nivel y el siguiente |
| No sé por dónde empezar | `_indice/COMO-BUSCAR.md` |

> 🎮 **Y si lo que quieres es ver un juego ENTERO montado**, no una pieza suelta:
> `14 - Juego de referencia/` trae «Enjambre» completo —especificación previa, arte y
> sonido generados por código, portada, menú, opciones, pausa, derrota, guardado con
> versión y checksum, dos idiomas y mando—, con la fuente entera y los generadores
> para reconstruirlo. Compila y se ejecuta. Su README dice qué mirar para cada cosa.
