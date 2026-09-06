# Trabajo pendiente — segunda auditoría (2026-09-06)

> **Qué es esto.** Siete auditores revisaron la biblioteca dominio por dominio contra listas
> canónicas del oficio (~490 temas). Los informes completos, con la tabla tema por tema, la
> evidencia de cada veredicto y la propuesta concreta, están en
> [`auditorias/`](./auditorias/). Este archivo es solo el **plan de ejecución**: qué falta,
> en qué orden y con qué frontera para no duplicar.
>
> **Estado: cerrado el 2026-09-06.** Los ~30 documentos propuestos se escribieron y verificaron;
> `actualizar.py` sale con «Biblioteca coherente». Lo que queda es la lista corta del final.

## Estado por dominio

| Dominio | Temas | Cubierto | Parcial | Falta | Informe |
|---|---:|---:|---:|---:|---|
| Audio | 102 | 76 | 15 | 11 | [`auditorias/audio.md`](./auditorias/audio.md) |
| Ingeniería y sistemas | 83 | 63 | 12 | 8 | [`auditorias/ingenieria.md`](./auditorias/ingenieria.md) |
| VFX y gráficos | 82 | 44 | 18 | 20 | [`auditorias/vfx.md`](./auditorias/vfx.md) |
| Colisiones, movimiento y cámara | 62 | 42 | 11 | 9 | [`auditorias/colisiones-movimiento-camara.md`](./auditorias/colisiones-movimiento-camara.md) |
| Feedback, UI/UX y onboarding | 55 | 34 | 12 | 9 | [`auditorias/feedback-ux.md`](./auditorias/feedback-ux.md) |
| Diseño de juego y GDD | 55 | — | — | 3 bloques | [`auditorias/diseno-gdd.md`](./auditorias/diseno-gdd.md) |
| Combate, enemigos y jefes | 50 | 23 | 14 | 13 | [`auditorias/combate-enemigos.md`](./auditorias/combate-enemigos.md) |

**Ningún dominio está vacío.** Lo que falta es, casi siempre, la capa intermedia: la API está
documentada y el «cómo se siente» también, pero falta el **sistema de datos** que hay en medio.

## Defectos con nombre y apellido (arreglar antes que escribir nada nuevo)

1. 🔴 **`hit_flash` está huérfano.** Se declara y decrementa en `04/02`, `04/03` y `04/15` §5.7,
   y **no se dibuja en ninguna parte**. Un LLM que siga esas recetas hace un juego donde nada
   parpadea al recibir un golpe. Arreglo: dibujarlo en `04/15` §5.6 con las tres vías
   (`image_blend` + `gpu_set_fog`, shader de uniform, sprite blanco encima) y una línea de
   remisión en las otras dos.
2. 🔴 **El espejo español rompe los FX.** `manual-lts-2026-es/…/All_Filter_Effect_Types.md`
   tiene **28 filas frente a las 42 de la inglesa** y **traduce 25 identificadores internos**
   que son cadenas literales de `fx_create()` (`"_cajas_de_filtro"` por `"_filter_boxes"`).
   Mientras no se corrija, **esa página no se puede citar**: usar la inglesa. Y conviene
   revisar si el mismo patrón afecta a otras páginas (`"g_*"`, otros catálogos de cadenas).
3. 🟠 **Cobertura de partículas medible:** solo **13 de 34** funciones `part_type_*` y **7 de
   19** `part_system_*` aparecen en algún documento de prosa. Faltan justo las que separan un
   efecto genérico de uno bueno (`part_type_sprite`, `part_type_blend`, `part_type_step`/`_death`)
   y `part_system_automatic_update`, que es lo que haría que las partículas respeten el hit stop.
4. 🟠 **`04/04` no cubre resistencias** pese a que `04/30` lo afirmaba (ya corregido en `04/30`).
   No existe sistema de tipos de daño en ninguna parte de la biblioteca.

## Qué se hizo (2026-09-06)

**32 documentos nuevos** y ~20 ampliaciones, todos con símbolos verificados y validadores en verde:

- **`04 - Recetas por género/`**: 32 daño y estados · 33 enemigos y director · 34 combate a distancia ·
  35 por turnos y táctico · 36 habilidades y enfriamientos · 37 traversal · 38 pathfinding avanzado ·
  39 VFX · 40 tutorial y onboarding · 41 transiciones, carga y pausa · 42 audio reactivo · 43 modding ·
  44 bullet heaven/autobattler/deckbuilder · 45 géneros sin receta.
- **`13 - Diseño y producción/`**: 14 el documento de diseño · 15 teoría · 16 progresión · 17 puzzles ·
  18 combate y jefes · 19 cámaras · 20 negocio y ética · 21 balance por simulación · 22 mundo y
  exploración · 23 patrones en GML · 24 voz y localización.
- **Otros**: `01/17` GML Visual · `08/23` recetario de shaders · `08/24` audio avanzado ·
  `07/22` extensión nativa · `06/scr_audio.gml` y `06/scr_tiempo.gml` (compilados).
- **Ampliaciones**: `04/15` (juice avanzado, recompensa y fracaso), `04/24` (luz avanzada),
  `04/25` (rebinding real), `04/26` (transición horizontal), `04/27` (accesibilidad completa +
  cognitiva), `04/14` (lobbies y NAT), `13/05` (mapa y tienda), `13/10` (anti-trampas, probar audio),
  `13/11` (equipo, salud, Git LFS), `05/02` (consolas, Steam Deck, presupuesto de build),
  `01/06`, `01/08`, `01/12`, `01/15`, `13/13`, `12/01`, `07/09`, `12/05`, `05/03`, `04/12`,
  `04/17`, `04/28`, `04/29`, `AGENTS.md`.

### Defectos corregidos

1. **`hit_flash` huérfano**: dibujado añadido en `04/15` §5.6 bis; `04/02` y `04/03` remiten a él.
2. **Espejo español del manual**: 24 páginas corregidas — el catálogo de FX (28→42 filas, 25
   identificadores literales restaurados), `collision_line_list` («centro»→«inicio»), claves de
   `ds_map` en audio, Sequences (`image_speed`), red, Xbox Live, teclado virtual. 57 candidatas
   descartadas por ser UI legítimamente traducida.
3. **Identificadores no ASCII**: 20 casos corregidos en 5 documentos (uno no habría compilado
   nunca) y comprobación añadida a `validar-codigo-gml.py`.
4. **`directory_get_working()`** citada en `01/14` y no existe; formato de `texturegroup_add` en
   `08/08` estaba como array y es struct; `13/13` §6.8 desconocía `collision_line_list(..., ordered)`.
5. **Herramientas**: `validar-proyecto.py` nuevo, `sincronizar-skill.py` nuevo (paso 10),
   `probar-descubrimiento.py` pasó de 29 a 49 casos, y `Lumbre`/`GameMaker_Fuentes`/`auditorias`
   quedaron excluidos de los recorridos.

## Lo que queda (lista corta)

Ninguno bloquea el uso de la biblioteca. Por orden de valor:

1. **Compilar el GML de los documentos nuevos.** `validar-compilacion.sh` solo cubre `06/`. Varios
   redactores compilaron su código a mano (07, 08, 10, 11, 13, 17, 21, 23 y los dos scripts), pero
   no hay una pasada automática sobre las ~35 000 líneas nuevas.

### Cerrados el 2026-09-06 (ampliaciones pequeñas)

2. ✅ **Xbox Live / UWP**: sección nueva en `04/20` §6 — familia `xboxlive_*` (usuarios, estadísticas
   y logros, leaderboards, nube, matchmaking), con la advertencia de que **no está en `GmlSpec.xml`**
   (las firmas vienen del manual, no de `buscar.py`), qué exige (UWP + Xbox Live habilitado, cuenta
   ID@Xbox, certificación) y la distinción frente a la exportación nativa a consola (cerrada, bajo NDA).
3. ✅ **Discord Activities, AR móvil y *serious games***: fila honesta en `05/02` §6 — ninguno de los
   tres tiene soporte hoy (Discord: solo un «Discord Social SDK» en el roadmap, que no es Activities;
   AR: cero funciones de cámara/tracking y ninguna extensión ARKit/ARCore en el catálogo; *serious
   games* es una etiqueta de propósito sin exigencia técnica, pero sin SCORM/xAPI documentado).
4. ✅ **Colisión isométrica** en `13/13` §7.3: colisión en rejilla lógica (7.3.1), máscara `Diamond`
   (7.3.2), desempate de `depth` por capa+`y` (7.3.3) y offset por altura (7.3.4). Remisión al
   filtrado de Box2D añadida en `04/22` §5 hacia `01/08` §6 bis (sin duplicar).
5. ✅ **Versión de Vinyl** en `07/21`: comprobada contra la API de GitHub el 2026-09-06 — estable
   `6.3.4` (2026-01-28), más reciente `6.4.2-beta` (2026-06-03, con *beat tracker*).
6. ✅ **Patrón de literales traducidos, revisado más allá de las familias ya barridas.** Encontrados
   y corregidos **9 páginas más** con el mismo defecto (una clave o un valor literal de `async_load`
   traducido al español, que rompe la comparación en GML si el lector confía en el texto):
   - `keyboard_status` devuelto como `"oculto"/"oculto"/"mostrando"/"visible"` en vez de
     `"hiding"/"hidden"/"showing"/"visible"` — duplicado en **7 páginas**: `Async_Events/System.md`,
     `Virtual_Keys_And_Keyboards.md`, `keyboard_virtual_show.md`, `keyboard_virtual_hide.md`,
     `Drag_And_Drop/.../Mouse_And_Keyboard_Actions.md`, `Hide_Virtual_Keyboard.md`,
     `Show_Virtual_Keyboard.md`.
   - Las claves de `async_load` de HTTP (`http_get.md`, `http_get_file.md`, `http_post_string.md`)
     traducidas como `estado`/`resultado` en vez de `status`/`result`.
   - `cloud_synchronise.md` con la clave `"descripción"` en vez de `"description"`.
   - Prosa que citaba entre comillas la clave ya traducida (`Async_Events/Cloud.md`,
     `Async_Events/HTTP.md`, `get_string_async.md`, `get_integer_async.md`).
   - **Hallazgo colateral, sin corregir**: `Async_Events/System.md` en español tiene 66 líneas
     frente a las 109 del inglés — le faltan secciones enteras (`DeviceMotion`,
     `DisplayLayoutInfo`/insets seguros, `permission_request_result`, `receipt_validation`,
     `onResume`). No es el mismo defecto (es un hueco de contenido, no una traducción rota), pero
     conviene una pasada de traducción completa en una sesión futura.

## Cómo retomarlo

1. El informe del dominio en [`auditorias/`](./auditorias/) trae el encargo ya redactado.
2. [`auditorias/BRIEF-redactor.md`](./auditorias/BRIEF-redactor.md) es el brief del redactor.
3. Tandas de 6-7 agentes; cada redactor consume ~300 000 tokens.
4. Al cerrar cada tanda: `python3 _indice/actualizar.py` y añadir la fila al índice de la carpeta.
