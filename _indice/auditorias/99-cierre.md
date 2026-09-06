# Auditoría de cierre · ¿se cerró lo que decían las auditorías, y qué sigue faltando?

> **Qué es esto.** Tercera y última pasada sobre la biblioteca, después de las dos rondas de
> auditoría de `auditorias/` (~490 temas) y de la tanda de redacción que escribió ~30 documentos
> nuevos. Responde a dos preguntas: **(1)** ¿existe y cubre de verdad cada propuesta ALTA y MEDIA
> de los siete informes? **(2)** ¿queda algún punto del desarrollo con GameMaker que **ninguna**
> de las dos rondas haya detectado?
>
> **Instantánea: 2026-09-06, 16:23.** ⚠️ La biblioteca **se estaba escribiendo mientras se
> auditaba**: entre las 16:07 y las 16:23 se cerraron en vivo `04/26`, `04/17`, `04/28`, `07/09`,
> `01/12`, `13/13 §6.8`, apareció `13/22` y se regeneraron a mano `04/_INDICE-RECETAS.md` y
> `13/_INDICE-DISENO.md`. Todo lo que aquí se marca como pendiente hay que **releerlo contra el
> disco** antes de actuar: puede haberse cerrado después de esta hora.
>
> **Método.** `ls` de las carpetas 04, 08 y 13; `grep -c` de los conceptos clave y de los
> identificadores de la API en el archivo concreto de cada propuesta; lectura de las secciones
> dudosas; `python3 _indice/buscar.py --todo` para los huecos candidatos; ejecución de
> `verificar-enlaces.py`, `validar-codigo-gml.py` y `probar-descubrimiento.py`; y un cruce propio
> —recalculado desde el disco, no desde el índice— de las **familias de símbolos** contra los
> documentos que las explican.
>
> Ignorados `Lumbre/` y `GameMaker_Fuentes/`, según el brief de las rondas anteriores.

---

## 0 · Resumen ejecutivo

**El contenido está.** De las **18 propuestas de prioridad ALTA** de los siete informes, **17
están CERRADAS** y una está **PARCIAL** por un detalle de dos líneas. De las **21 propuestas
MEDIA**, **18 están CERRADAS**, 2 **PARCIALES** y 1 cerrada en otro sitio del que proponía el
informe. Los documentos nuevos no son cascarones: `04/39` usa las 12 funciones de partículas que
el informe de VFX echaba en falta, `08/23` trae las diez recetas de shader con su cadena de
ping-pong, `08/24` cubre las cuatro familias de audio del runtime, `13/19` traduce el marco
completo de Itay Keren. Los enlaces internos pasan (**1516 correctos, 0 rotos**) y el validador
de GML no encuentra **ni una función inventada**.

**Y sin embargo la biblioteca hoy no funciona como se promete a sí misma.** El hallazgo más
grave de esta pasada no es un hueco de tema: es que **`python3 _indice/actualizar.py` no se ha
ejecutado desde que se escribieron los documentos nuevos**. Los índices generados
(`MAPA.json`, `documentos.json`, `simbolos.json`, `SKILL.md`, `README.md`, `_INDICE-RECETAS.md`,
`_INDICE-DISENO.md`) son de las **10:37-10:41**; los documentos, de las **14:34-16:18**. El
efecto es medible y comprobado en vivo:

```
$ python3 _indice/buscar.py part_type_death
# part_type_death  (función)
  firma:     part_type_death(ind, death_number, death_type)
  manual (es): …/part_type_death.md
  uso real en código descargado: …
        ← NO aparece «explicada en la biblioteca»
```

…pese a que `04/39` lo explica **14 veces**. Lo mismo con `audio_create_sync_group`, que remite a
`01/13` y no a `08/24 §2`, donde está su sección entera. Un LLM que siga `AGENTS.md` al pie de la
letra —«tu primera parada es `buscar.py`»— **no encontrará el 30 % del material nuevo**. Es
exactamente el fallo que `gamemaker-indices-se-regeneran` describe: *un cruce congelado miente en
silencio*.

Además, en la **TAREA 2** aparecen **seis huecos que ninguna de las dos rondas miró**, y uno de
ellos es grande: **GML Visual (el antiguo Drag & Drop) tiene 313 páginas en el espejo español del
manual —el 10 % de todo el manual— y cero documentos propios que lo expliquen.**

---

## 1 · TAREA 1 — Estado de las propuestas ALTA y MEDIA

Leyenda: **CERRADO** (existe y cubre) · **PARCIAL** (existe, falta algo concreto) ·
**NO HECHO** · **DESPLAZADO** (cerrado, pero en otro documento del que proponía el informe).

### 1.1 · `vfx.md`

| # | Propuesta | Estado | Evidencia |
|---|---|---|---|
| A1 | `04/39 - VFX: diseño y catálogo de efectos` | **CERRADO** | 1027 líneas. §1.1-1.5 anatomía en capas, timing, rampa de color, silueta. §3.2 explosión, §3.3 fuego, §3.4 magia, §3.5 lluvia con salpicadura, §3.6 nieve, §3.7 niebla. La API que faltaba, medida: `part_type_sprite` ×5, `part_type_blend` ×10, `part_type_step` ×7, `part_type_death` ×14, `part_type_colour_mix/_hsv/_rgb` ×13, `part_system_global_space` ×6, `part_particles_count` ×7, `part_system_automatic_update` ×4 (§3.8 congelar partículas en el hit stop) |
| A2 | `08/23 - Recetario de shaders de efecto` | **CERRADO** | 1380 líneas. §2.1 cadena multipasada con ping-pong; §3.1-3.10: hit flash, aberración cromática, CRT/scanlines, glitch, pixelado, shockwave, heat haze, blur gaussiano de dos pasadas, bloom completo, LUT. `surface_rgba16float` ×11 |
| A3 | Catálogo de los 42 FX en `02/06 §4.5` + corregir el espejo español | **CERRADO** | `02/06` §4.5 «Catálogo completo de FX (42 tipos)», 37 identificadores `_filter_*` + los 6 `_effect_*`, con `fx_set_single_layer`/`layer_enable_fx` en §4.5 bis. `_filter_hard_drop_shadow` reclasificado como Filter con nota. **Y el espejo español está arreglado**: `All_Filter_Effect_Types.md` tiene ahora **48 filas igual que la inglesa** y los identificadores en inglés (`_filter_boxes`, `_filter_tintfilter`, `_filter_twirl_distort`…) |
| A4 | Ampliar `04/24` con iluminación avanzada | **CERRADO** | 778 líneas. §3 normal maps (con §3.4 «Separate Texture Page», el requisito que lo rompe), §4 sombras proyectadas (extrusión, §4.3 penumbra, §4.4 presupuesto, Bulb ×12), §5 god rays, §6 ciclo día/noche con `merge_colour` |
| M5 | Trails y estelas | **CERRADO** | `04/39 §3.9 Trails y estelas` (117 líneas). `04/15 §8.1` remite en vez de duplicar |
| M6 | Cerrar el `hit_flash` huérfano | **PARCIAL** ⚠️ | El dibujado **sí** está: `04/15 §5.6 bis · Dibujar el hit_flash (las tres vías)`. **Falta la remisión de una línea en `04/02` y `04/03`**: ambos siguen declarando, decrementando y fijando `hit_flash` sin dibujarlo nunca y sin apuntar a `04/15`. Ninguno de los dos enlaza a `15 - Game feel` (`grep` = 0). Un LLM que lea solo `04/02` sigue produciendo un juego donde nada parpadea |
| M7 | Decals, destrucción y escombros | **CERRADO** | `04/39 §3.10 Decals y marcas persistentes` y `§3.11 Destrucción y escombros` |
| M8 | Zoom punch + transiciones de pantalla | **CERRADO** | `04/15 §8.3 Zoom punch y retroceso de cámara`. Las transiciones (iris ×24, wipe/cortina ×23, disolución ×10) están en `04/41 §3.2`, y `01/10 §9` remite ahí en lugar de duplicarlas |

### 1.2 · `audio.md`

| # | Propuesta | Estado | Evidencia |
|---|---|---|---|
| A-P1 | `08/24 - Audio avanzado` | **CERRADO** | 750 líneas. §2 sync groups (las 11 funciones + el matiz de que `audio_play_in_sync_group` devuelve el **orden**), §3 buffer sounds, §4 play queues con el evento *Audio Playback*, §5 grabación de micrófono (con §«Discrepancia de traducción en el espejo español»), §6 Doppler |
| A-P2 | `04/42 - Audio reactivo al mundo` | **CERRADO** | 668 líneas. §3.1 pasos por material (`tilemap_get_at_pixel`), §3.2 zonas de reverb (`Reverb1`, con el aviso de que solo alcanza a lo que pase por emisores), §3.3 estados de mezcla como structs interpolables, §3.4 sistema de importancia de Overwatch (×29) |
| A-P3 | `06/scr_audio.gml` | **CERRADO** | 531 líneas, con ficha en `06/README.md` §332 y **dentro de `validar-compilacion.sh`** (línea 40), así que cae bajo la garantía de «compila sin errores» |
| M-P4 | `13/24 - Voz, diálogo y localización de audio` | **CERRADO** | 890 líneas. §2 grabación, §3 localización con fallback, §4 subtítulos de efectos con indicador direccional, §5 lip-sync (visemas precalculados), §6 voces procedurales, §7 barks, §8 QA. Y `04/21` ahora tiene §«Localización de audio y voz» que enlaza aquí |
| M-P5 | Transición horizontal en `04/26` | **CERRADO** *(a las 16:11)* | De 120 a 280 líneas: §«Transición horizontal: cambiar de tema sin cortar» (puntos de salida legales, segmento puente), §«La música como máquina de estados», §«Escribir la música para que esto funcione» |
| M-P6 | Audio en `04/17` (HTML5) y `04/28` (móvil) | **CERRADO** *(a las 16:1x)* | `audio_system_is_available`/desbloqueo por gesto ×6 en `04/17`; «latencia» ×5 en `04/28`, junto a la interrupción por llamada que ya estaba (`os_is_paused` + `audio_pause_all`/`audio_resume_all`) |
| M-P7 | Wwise/FMOD/LMMS/ChipTone en `07/09` y `12/05`; versión de Vinyl en `07/21` | **PARCIAL** ⚠️ | `07/09` ya nombra los tres (×5) y `12/05` cubre FMOD; **falta** la versión de Vinyl (6.3.4 estable / 6.4.2-beta) en `07/21`: `grep` = 0 |

### 1.3 · `combate-enemigos.md`

| # | Propuesta | Estado | Evidencia |
|---|---|---|---|
| A-P1 | `04/32 - Sistema de daño y efectos de estado` | **CERRADO** | 1257 líneas. §5.1 tipos y resistencias, §5.2 armadura, §5.3 escudos, §5.4 motor de estados, §5.5 tabla de efectos, §5.10 iconos, §5.11 barra de jefe segmentada, §5.12 serialización, §5.13 registro de daño. Y `04/30` ya no miente sobre las resistencias de `04/04`: su §Ver también remite a `04/32` |
| A-P2 | `04/33 - Diseño de enemigos, encuentros y director` | **CERRADO** | 892 líneas. §1 arquetipos, §2 sinergias y «hueco de escape», §3 gestor de fichas de ataque, §4 tabla de amenaza + versión ligera, §5 director de intensidad, §6 acoplamiento a las oleadas de `04/03` y `04/08` |
| A-P3 | `04/34 - Combate a distancia` | **CERRADO** | 1075 líneas. §5.1 cargador/recarga activa, §5.3 retroceso y dispersión, §5.4 hitscan con **`collision_line_list` ordenado (×19)**, §5.5 asistencia de puntería, §5.6-5.7 cobertura |
| M-P4 | `04/35 - Combate por turnos y táctico` | **CERRADO** | 1713 líneas |
| M-P5 | `13/18 - Diseño de combate y de jefes` | **CERRADO** | 760 líneas, §3 «Las plantillas: ficha de arquetipo, de encuentro y de jefe por fases» |
| M-P6 | `04/36 - Habilidades, enfriamientos y recursos` | **CERRADO** | 1269 líneas |
| M-P7 | §14 de sigilo en `04/31` | **DESPLAZADO** | `04/31` no tiene §14, pero el contenido está —y mejor situado— en `04/45 §2 Sigilo`: §2.3 estados de alerta (`enum EstadoAlerta`), §2.4 medidor de detección con subida/bajada por segundo, distracciones y escondites |

### 1.4 · `colisiones-movimiento-camara.md`

| # | Propuesta | Estado | Evidencia |
|---|---|---|---|
| A-P1 | `04/37 - Traversal en plataformas` | **CERRADO** | 1027 líneas. §3.1 pendientes, §3.2 wall slide/jump, §3.3 wall run, §3.4 corner correction, §3.5 ledge grab, §3.6 agacharse, §3.7 escaleras, §3.8 cuerdas, §3.9 nadar, §3.10 empuje de cajas con deshacer. Extiende el enum y el switch de `04/01 §5.5` en vez de duplicarlos (§2.2) |
| A-P2 | `13/19 - Cámaras de juego` | **CERRADO** | 1047 líneas. §1.3 glosario de *Scroll Back* traducido, §3.2-3.8 las siete técnicas de Keren, §3.4 platform-snapping, §3.5 zonas, §3.9 pantalla-a-pantalla, §3.10 multijugador con zoom, §3.11 cinemáticas |
| A-P3 | «Elegir la forma de la máscara» en `01/08 §4` | **CERRADO** | `01/08` §4 «Elegir la forma de la máscara»: `bboxkind` ×9, `sprite_collision_mask` ×5, `sepmasks`, Diamond, Precise per frame |
| M-P4 | «Bandos y capas de colisión» en `01/08` | **CERRADO** | `01/08 §6 bis`, con §«La variante de máscara de bits», §«Cuándo el `collision_space` NO es la respuesta» y §«Filtrado de colisiones en Box2D» |
| M-P5a | Filtrado de Box2D en `04/22 §5 bis` | **DESPLAZADO** | `04/22` sigue sin `physics_fixture_set_collision_group` (`grep` = 0), pero el tema quedó cubierto en `01/08 §6 bis`. Convendría al menos una línea de remisión desde `04/22 §5` |
| M-P5b | Colisiones isométricas en `13/13 §7.3` | **PARCIAL** ⚠️ | `§7.3 Isométrico (rombo 2:1)` da la proyección y su inversa, y menciona el desempate de `depth`, pero **no** la colisión en rejilla lógica, ni la máscara `Diamond`, ni el offset por altura (`grep` de «Diamond» en el documento = 0) |
| M-P6 | «Zona muerta bien hecha» en `01/12` | **CERRADO** *(a las 16:1x)* | radial/axial/curva de respuesta ×15 |
| M-P7 | «Cuánto cuestan las colisiones» en `01/15` | **CERRADO** | `01/15` §6 «Paso 6: cuánto cuestan las colisiones», con medición en µs contra el presupuesto de 16 666 µs y enlace a `13/08 §4` |

### 1.5 · `feedback-ux.md`

| # | Propuesta | Estado | Evidencia |
|---|---|---|---|
| A-P1 | Ampliar `04/27 - Accesibilidad` | **CERRADO** | De 137 a **824 líneas**. §1.1 shader de daltonismo por matrices (protan/tritan), §2.1 subtítulos con hablante y personalización, §4.1 slider de haptics (×23), §5 mono/estéreo + indicador direccional, §6 recordatorios, §7 modo asistido, **§8 «Lo que GameMaker no puede hacer»** (lector de pantalla, ×9), checklist Basic/Intermediate/Advanced y §«Cómo declararlo en la ficha de Steam» |
| A-P2 | `04/40 - Tutorial, onboarding y prompts` | **CERRADO** | 981 líneas, §3.6 `scr_ui_prompt` que lee dispositivo **y** asignación real del rebinding |
| A-P3 | `04/41 - Transiciones, carga y pausa` | **CERRADO** | 1090 líneas. §3.1 «Pausar de verdad» (`time_source_pause` ×5), §3.2 motor de transiciones, §3.3 pantalla de carga real (`texturegroup_load` + `texturegroup_get_status` ×6), §3.4 menú de pausa con ducking |
| M-P4 | Rebinding de verdad en `04/25 §5` | **CERRADO** | §5.1-5.7, 580 líneas: captura de tecla/botón/eje, §5.3 conflictos (×27), §5.4 perfiles, §5.5 restablecer con confirmación, §5.6 guardado, §5.7 enganche con `icono_boton()` y `prompt_boton()` |
| M-P5 | Trail de cinta, permanence, zoom punch, rumble en `04/15` | **CERRADO** | §8.1 y §8.2 remiten a `04/39` («ya resuelta, no la dupliques»), §8.3 zoom punch, §8.4 vibración del mando con tabla de fuerza/duración por tipo de golpe |
| M-P6 | Mapa y tienda en `13/05 §3.5` | **CERRADO** | `§3.5 j) Pantalla de mapa completo` y `§3.5 k) Tienda`. La barra de jefe fue a `04/32 §5.11`, que es su sitio |
| M-P7 | «La recompensa y el fracaso» | **CERRADO** | `04/15 §8bis`, con §8bis.1 coreografía de la recompensa, §8bis.2 subida de nivel, §8bis.3 pantalla de resultados, §8bis.4 el fracaso sin humillar |

### 1.6 · `diseno-gdd.md`

| # | Propuesta | Estado | Evidencia |
|---|---|---|---|
| A-1 | `13/14 - El documento de diseño` | **CERRADO** | §1.3 pilares, §1.4 elevator pitch, §1.5 wiki viva, §2.20 catálogo de diagramas, §3.1-3.2 guardar el GDD como recurso `Notes` con `resourcetool` (verificado en vivo), §3.4 plantilla completa de 14 secciones |
| A-2 | `13/15 - Teoría del diseño` | **CERRADO** | 1017 líneas: Koster, Salen & Zimmerman, Schell, SDT, Bartle/Quantic, Costikyan, dominancia estratégica, Juul, Fullerton, §12 tabla «qué marco para qué problema», §13 ejemplo aplicado |
| A-3 | `13/16 - Progresión` | **CERRADO** | 1248 líneas |
| A-4 | `13/17 - Diseño de puzzles` | **CERRADO** | 957 líneas |
| M-5 | `13/20 - Modelo de negocio y ética` | **CERRADO** | 912 líneas, con el catálogo de patrones oscuros y la tasa de reembolso de Steam verificada |
| M-6 | `13/21 - Balance por simulación` | **CERRADO** | 987 líneas |
| M-7 | `04/44 - Bullet heaven, autobattler y deckbuilder` | **CERRADO** | 1508 líneas, §0 el esqueleto compartido + un bloque por género |

### 1.7 · `ingenieria.md`

| # | Propuesta | Estado | Evidencia |
|---|---|---|---|
| A-P1 | `13/23 - Catálogo de patrones en GML` | **CERRADO** | §3.1 Flyweight, §3.2 Prototype, §3.3 Subclass Sandbox, **§3.4 Data Locality medido con `get_timer()`**, §3.5 Dirty Flag, §3.6 Event Queue, §3.7 Bytecode, §3.8 veredicto sobre ECS, §6 tabla «los 19 de Nystrom → dónde está cada uno» |
| A-P2 | `04/38 - Pathfinding avanzado` | **CERRADO** | 1196 líneas: §2 flow field, §3 JPS sobre `GridPonderado`, §4 pathfinding en plataformas, §5 suavizado + steering |
| A-P3 | `07/22 - Crear una extensión nativa` | **CERRADO** | 720 líneas: §1 *Copies To*, §2 placeholders y proxies, §3.2/3.3 firma clásica y `RValue`, §6 `GM-ExtensionGenerator`, §7 Android/iOS/HTML5, §8 Configurations |
| A-P4 | `04/43 - Modding y contenido externo` | **CERRADO** | 862 líneas, con §4 «Riesgo: qué puede romper un mod y cómo aislarlo» |
| M-P5 | Lobbies, matchmaking y NAT en `04/14` | **CERRADO** | `§10` completo: §10.1 modelo de datos de una sala, §10.2 matchmaking por cola y MMR, **§10.3 «`steam_lobby_*`: no está en el runtime — es la extensión»**, §10.4 NAT con las tres salidas |
| M-P6 | Seguridad y anti-trampas en `13/10` | **CERRADO** | `§14`: §14.2 detectar lo imposible, §14.3 replay firmado, §14.4 Cheat Engine, §14.5 límites de la ofuscación, §14.6 «la frase honesta» |
| M-P7 | Rebinding en `04/25 §5` | **CERRADO** | Ver feedback M-P4 |
| M-P8 | «Pausar de verdad» en `01/06` | **CERRADO** | `01/06 §8 bis`, que remite a `04/41 §3.1` para la implementación completa |

### 1.8 · Los cuatro defectos con nombre y apellido de `PENDIENTE-auditoria-2.md`

| Defecto | Estado | Evidencia |
|---|---|---|
| 🔴 1 · `hit_flash` huérfano | **PARCIAL** | Dibujado en `04/15 §5.6 bis`; **sin remisión desde `04/02` ni `04/03`** |
| 🔴 2 · El espejo español rompe los FX | **CERRADO** | `All_Filter_Effect_Types.md` español: 48 filas = las mismas que la inglesa, identificadores en inglés |
| 🟠 3 · Cobertura de partículas | **CERRADO** | 12 de 12 funciones citadas ahora presentes en `04/39` |
| 🟠 4 · `04/04` no cubre resistencias | **CERRADO** | Existe `04/32`; `04/30` ya remite ahí |

### 1.9 · Las correcciones de la «tanda 1»

| Corrección | Estado |
|---|---|
| `13/13 §6.8` debe citar `collision_line_list(..., ordered)` | **CERRADO** *(a las 16:1x)* — `collision_line_list` ×4 |
| Bug de traducción: «desde el **inicio** de la línea» | **CERRADO** — la página española lo dice bien |
| `_filter_twirl_distort` (no `_twist_distort`) | **CERRADO** — es el identificador que usa `02/06 §4.5` |
| Ancla rota en `08/06` | **CERRADO** — `verificar-enlaces.py`: 1516 rutas, 0 rotas |
| Identificadores GML en ASCII puro | **CERRADO** — `validar-codigo-gml.py`: 0 funciones inventadas |
| **Excepción real a «nunca edites `.yy` a mano»: el asset Extensión no lo crea `resourcetool`** | **NO HECHO** ⚠️ — no aparece ni en `AGENTS.md §4` ni en `07/13` (`grep` = 0 en ambos) |

---

## 2 · 🔴 El hallazgo transversal: los índices generados están caducados

**Esto bloquea todo lo demás y se arregla con un comando.**

| Artefacto generado | Última regeneración | Documentos más nuevos | ¿Los ve? |
|---|---|---|---|
| `_indice/documentos.json` | 2026-09-06 **10:41** | 2026-09-06 **16:18** | ❌ |
| `_indice/simbolos.json` (cruce símbolo → documento) | **10:41** | **16:18** | ❌ |
| `_indice/MAPA.json` | **10:41** | **16:18** | ❌ (`grep "39 - VFX"` = 0) |
| `README.md` (raíz) | **10:40** | — | ❌ |
| `_indice/skills/gamemaker-biblioteca/SKILL.md` | **10:37** | — | ❌ |
| `04/_INDICE-RECETAS.md` | 2026-09-06 **16:22** | 45 | ✅ *(cerrado a las 16:22, durante esta auditoría; a las 16:18 llegaba solo hasta el 31)* |
| `13/_INDICE-DISENO.md` | **16:22** | 24 | ✅ *(ídem; a las 16:18 llegaba hasta el 13)* |
| `07/_INDICE-ECOSISTEMA.md` | 2026-09-02 **17:30** | — | ❌ no cita `22 - Crear una extensión nativa` |

Consecuencias comprobadas, no supuestas:

1. **`buscar.py <símbolo>` omite el material nuevo.** `part_type_death` no lista ningún documento
   pese a estar explicado 14 veces en `04/39`. `audio_create_sync_group` remite a `01/13` y no a
   `08/24 §2`. Son **exactamente** los símbolos que las auditorías señalaron como huecos: la
   biblioteca los ha cubierto y su propio buscador no se ha enterado.
2. **`MAPA.json` —la vía «legible por máquina» que `AGENTS.md §1.bis` ofrece a los agentes— no
   contiene ninguno de los ~30 documentos nuevos.**
3. **La skill `gamemaker-biblioteca`**, que es como se consume esta biblioteca **desde otros
   proyectos**, sigue anunciando el catálogo de las 10:37.
4. **`probar-descubrimiento.py` pasa las 29 tareas… pero ninguna de las 29 toca el material
   nuevo.** No hay ni una consulta sobre anatomía de un efecto, recetario de shaders, sistema de
   daño, cámara de juego, GDD, puzzles o monetización. El test verde no significa que el material
   nuevo sea descubrible; significa que no se le ha preguntado.

**Arreglo:** `python3 _indice/actualizar.py`, y después añadir a mano las filas que faltan en
`04/_INDICE-RECETAS.md`, `13/_INDICE-DISENO.md` y `07/_INDICE-ECOSISTEMA.md` (el comando descubre
los documentos para `MAPA.json`, pero los índices de carpeta llevan prosa de criterio). Y ampliar
`probar-descubrimiento.py` con 8-10 tareas nuevas que **solo** se resuelvan con los documentos de
esta tanda, para que el test vuelva a demostrar algo.

**Nota adicional:** `_indice/PENDIENTE-auditoria-2.md` sigue listando como pendientes ~30
documentos que **ya existen**. Su propio paso 5 dice «cuando un documento nuevo exista, quítalo de
este archivo». Hoy ese fichero desinforma a quien lo abra.

---

## 3 · TAREA 2 — Huecos que ninguna de las dos rondas detectó

Cada uno verificado con `grep -rli` sobre las once carpetas de contenido y con
`python3 _indice/buscar.py --todo`. Los que resultaron cubiertos están al final, con su ruta.

### 🔴 Prioridad alta

**H1 · GML Visual (Drag & Drop) — el 10 % del manual sin un solo documento propio**

- **Evidencia.** `09 - Manual oficial/manual-lts-2026-es/Drag_And_Drop/` tiene **313 páginas**
  (sobre 3142 del espejo español): `Drag_And_Drop_Overview` más 20 categorías de acciones (Audio,
  Buffers, Cameras, Collisions, Data_Structures, Drawing, Files, Game, Gamepad, Instance, Layers,
  Loops, Movement, Particles, Paths, Random, Rooms, Sequences, Tiles, Time_Sources, Timelines).
  En toda la biblioteca, «GML Visual» / «Drag and Drop» / «DnD» aparece **solo como etiqueta**:
  `05/01` clasifica tutoriales por «sabor», `01/_INDICE-FUNDAMENTOS` dice «es otra forma de lo
  mismo, pero este material es de GML Code», `02/09` menciona el desplegable de lenguaje del Code
  Editor 2. **Ni un documento, ni una sección, ni una tabla de equivalencias.**
- **Por qué importa.** Es el modo de autoría con el que empieza la mayoría de la gente y en el que
  están escritos los tutoriales oficiales *Fire Jump* y *Hero's Trail* que la propia biblioteca
  cita. Un LLM al que le pidan «arréglame este evento» sobre un proyecto DnD, o «pásame esto a
  código», no tiene aquí nada a lo que agarrarse; y `AGENTS.md` prohíbe editar `.yy` a mano, que es
  justo donde vive un evento DnD.
- **Dónde iría.** Documento nuevo `01 - Fundamentos/17 - GML Visual (Drag & Drop) y cómo pasar a
  código.md`: qué es y cuándo tiene sentido; el mapa de las 20 categorías de acciones; la **tabla
  de equivalencias acción → función de GML**; cómo conviven ambos en el mismo proyecto (*Execute
  Code*, y que al cambiar de lenguaje **solo se convierte el evento enfocado**); cómo se guarda un
  evento DnD en el `.yy` y por qué **no** se edita a mano; y la receta de migración incremental de
  un proyecto DnD a GML.

**H2 · Salud del desarrollador: ritmo sostenible, crunch y burnout**

- **Evidencia.** `buscar.py --todo "burnout"` → **cero resultados**. `grep -rliE
  "burnout|crunch|salud mental"` sobre las once carpetas → **0 archivos**. `13/11` planifica el
  alcance («multiplica por tres», la matriz de recorte, un objetivo por semana) pero **nunca desde
  la persona**: no dice qué pasa cuando el alcance se recorta a costa de dormir.
- **Por qué importa.** El motivo nº 1 por el que un proyecto de una persona no se termina no es
  técnico. La biblioteca cubre «qué recortar» y no cubre «cuándo parar».
- **Dónde iría.** Sección nueva `13/11 §12 · El ritmo que se puede sostener`: señales tempranas de
  agotamiento; por qué el *crunch* de fin de proyecto suele ser un fallo de estimación de §1.2 y no
  de esfuerzo; trabajar con un trabajo a jornada completa; el proyecto que hay que abandonar y cómo
  hacerlo sin perderlo todo (postmortem del §8.5 aunque no se lance); y qué se delega primero
  cuando aparece algo de presupuesto (§6.3 ya dice «paga la capsule y el tráiler»).

### 🟠 Prioridad media

**H3 · Trabajar con otras personas: encargos, contratos y licencias del trabajo ajeno**

- **Evidencia.** `grep` sobre las once carpetas: «trabajar en equipo / reparto de roles» → **0**;
  «brief de arte / encargo de arte / hoja de encargo» → **0**; «traductor profesional / agencia de
  traducción / LQA» → **0**; «documentación para el equipo» → **0**. `13/11 §9.2` cubre la licencia
  de un asset **descargado**, y `04/21` la traducción **por IA**, pero nadie cubre **encargar**.
- **Por qué importa.** El paso de «lo hago todo yo» a «pago a alguien por el arte, la música o la
  traducción» es donde un indie firma su primer contrato, y donde se pierde la propiedad de un
  asset por no pactar la cesión. Es lo que separa un juego personal de un producto.
- **Dónde iría.** Sección nueva en `13/11` (§5 bis, junto al pipeline de assets): la hoja de
  encargo (qué entrega, en qué formato, en cuántas revisiones); *work for hire* frente a licencia,
  y por qué hay que pedir la cesión por escrito; tarifas por pieza frente a por hora; **LQA de
  localización** enlazando a `04/21` y `13/24 §3`; y la documentación mínima para que entre otra
  persona al repositorio (que hoy solo existe como el ADR de `13/11 §3.5` y el diario de §3.6).

**H4 · Presupuesto de build: tamaño del paquete y tiempo de arranque**

- **Evidencia.** `buscar.py --todo "tiempo de carga"` → **cero**. «tamaño de la build / del
  ejecutable» → 2 archivos, y ambos de pasada (`02/03` sobre GMRT, `08/19` sobre `forceinline`).
  `05/02 §4.4` tiene un `[ ] Comprobar el tamaño del paquete y los tiempos de carga` en la
  checklist **sin decir cómo ni contra qué cifra**.
- **Por qué importa.** El tamaño de descarga condiciona la conversión en móvil y en web, y el
  tiempo hasta el primer frame es lo primero que juzga cualquiera. La biblioteca tiene todas las
  piezas sueltas —`texturegroup_load` y su estado en `04/41 §3.3`, grupos de texturas en `08/08`,
  compresión GPU en `02/06 §7`, el perfil de memoria en `01/15`— y ningún documento que diga qué
  medir ni qué es aceptable.
- **Dónde iría.** Sección nueva `01/15 §«Presupuesto de build: tamaño y arranque»`: de qué se
  compone el paquete de salida por plataforma; cómo medir el tiempo hasta el primer frame; qué se
  puede diferir con grupos de texturas; audio comprimido frente a sin comprimir y su efecto real;
  qué cifras son razonables en escritorio, móvil y web. Enlaza a `05/02 §4.4`, que hoy solo lo pide.

**H5 · Versionado de assets binarios (Git LFS) en un repositorio de GameMaker**

- **Evidencia.** `buscar.py --todo "Git LFS"` → **cero**. `13/11 §4.1` cubre Git con GameMaker
  (`.gitignore`, ramas, etiquetas) y **no menciona LFS ni una vez**, pese a que un proyecto de
  GameMaker es, en peso, casi todo `.png`, `.ogg` y `.yy`.
- **Por qué importa.** Es el fallo de infraestructura que aparece al año, cuando el repositorio pesa
  gigabytes por el historial de sprites y ya no hay forma barata de arreglarlo.
- **Dónde iría.** Sección corta en `13/11 §4.1`: qué extensiones conviene poner en LFS en un
  proyecto de GameMaker, por qué **los `.yy` no van a LFS** (son texto y deben diferenciarse), qué
  cuesta migrar un repositorio que ya creció, y la alternativa cuando el alojamiento no da LFS.

**H6 · Accesibilidad cognitiva, y el marco legal europeo**

- **Evidencia.** En `04/27`, «Cognitive» aparece 3 veces, siempre **citando** el nivel de una pauta
  de las GAG, nunca como sección propia; `dislexia` y `TDAH` → **0 en toda la biblioteca**.
  «European Accessibility Act» / «Ley Europea de Accesibilidad» → **0**. El documento es honesto y
  dice que su checklist no es la lista entera de GAG, pero la categoría *Cognitive* es una de las
  seis del estándar y es la única sin tratamiento propio.
- **Dónde iría.** `04/27 §6 bis · Carga cognitiva`: tipografías legibles y su interlineado; textos
  sin límite de tiempo y con relectura; reducir la complejidad simultánea como ajuste; el resumen
  de «qué estaba haciendo» al volver de una pausa larga. Y en `13/11 §9`, un párrafo sobre el marco
  legal europeo de accesibilidad y a qué parte de un juego alcanza hoy —marcado como ⚠️ **no
  verificado en vivo**, porque no procede afirmarlo sin fuente.

### 🟢 Prioridad baja

**H7 · Xbox Live / UWP.** `GML_Reference/UWP_And_XBox_Live` tiene **70 páginas** en el espejo, y en
la biblioteca solo hay filas de tabla sobre la extensión `GMEXT-GDK` (`07/01`, `07/03`, `07/22`).
No hay documento que explique logros, perfiles ni guardado de Xbox Live. Es un destino de nicho y
con wiki privada; basta con **una fila honesta en `05/02 §6 «Vacíos de información»`** que diga que
existe, que son 70 páginas y que esta biblioteca no lo cubre.

**H8 · Discord Activities, AR móvil y *serious games*.** `Discord Activit`/`Embedded App SDK` → 0;
`realidad aumentada`/`ARKit`/`ARCore` → 0; `serious game`/`juego educativo`/`gamificación` → 0.
Los tres son legítimamente **fuera de alcance** —GameMaker no tiene soporte de AR, y Discord
Activities exigiría un embebido web específico—, pero decirlo cuesta tres líneas y evita que un
LLM se lo invente. Sitio: `05/02 §6`, que ya es el lugar donde la biblioteca reconoce lo que no
cubre.

### ✅ Verificado como CUBIERTO (candidatos que resultaron no ser huecos)

| Sospecha | Realidad |
|---|---|
| Multijugador local a pantalla partida | `01/10 §7 «Pantalla partida (split screen)»` + cámara multijugador con zoom en `13/19 §3.10` |
| Juego en navegador integrado en una web | `04/17` entero (extensiones `.js`, `gmcallback_`, `localStorage`, CORS) + `05/02 §3.1-3.4` |
| Telemetría con consentimiento | `13/10 §10.4 Telemetría mínima` + `13/11 §9.3 Política de privacidad` + `13/20 §3` |
| Integración continua | `07/13 §11 «Los workflows de GitHub Actions que genera init»` + `13/11 §4.6` |
| GMRT | `02/03` entero, 38 archivos lo citan |
| Feather y análisis estático | `02/09` + `01/15 §2` + `05/04`, 31 archivos |
| Memoria y rendimiento en móvil | `04/28` + `01/15 §4 «La ventana Memory»` |
| Consolas | `05/02 §1.4 «Consolas: wikis privadas»` y `§3.8`, con las URLs de las wikis por plataforma |
| Steam Deck | `05/02 §3.6` + criterios de UI en `13/05` |
| Clasificación por edades (PEGI/ESRB/IARC) | `13/11 §9.4` |
| Impuestos de las tiendas (W-8BEN, retención) | `13/11 §9.5`, verificado contra Steamworks |
| Press kit, demo, claves con embargo | `13/11 §6.6` + plantilla en §8.4 |
| Precio, regiones y descuentos de Steam | `13/11 §6.7`, con las reglas de los 30 días verificadas |
| Modding | `04/43` |
| Versionado y migración del guardado | `01/14` (`VERSION_GUARDADO`) + `06/scr_save_load.gml` (`SAVE_VERSION`) |
| Anti-trampas y replays firmados | `13/10 §14` |
| Game jam | `07/08 - itch.io - jams, assets y juegos` (29 menciones). El `13/26` que proponía la lista BAJA sigue sin existir, pero `07/08` cubre lo operativo |
| Recolector de basura | `01/15 §5`, con referencias débiles |
| Live Wallpapers y Game Strips de GX.games | `05/02 §3.1` + `07/06` (12 plantillas) |
| **Cobertura de la API por familias** | **Ninguna familia de ≥6 símbolos no obsoletos queda sin mención**, y ninguna de ≥8 baja del 60 % — recalculado desde el disco, no desde el índice |

---

## 4 · Veredicto final

**¿Está la biblioteca completa para «desarrollar CUALQUIER videojuego con GameMaker»?**

**Para escribir el juego, sí.** Con las salvedades de abajo, no he encontrado ningún sistema de un
videojuego 2D que un desarrollador vaya a necesitar y que aquí no esté explicado con código
verificado: movimiento, colisiones, cámaras, combate cuerpo a cuerpo y a distancia, daño y estados,
IA, pathfinding, procgen, VFX, shaders, iluminación, audio en todas sus capas, UI, accesibilidad,
guardado, red, plataformas, y encima el oficio de diseñarlo y producirlo. La cobertura de la API es
total a nivel de familia y el código no inventa funciones. **Como cuerpo de conocimiento, está.**

**Lo único que de verdad falta hoy es que la biblioteca se pueda encontrar a sí misma.** Los ~30
documentos nuevos existen en el disco y **no existen en los índices**: `buscar.py` no los asocia a
sus símbolos, `MAPA.json` no los lista, la skill que exporta la biblioteca a otros proyectos no los
conoce, y los índices de carpeta se quedan en el documento 31 y en el 13. Una biblioteca
anti-alucinación cuyo buscador contesta «no consta» sobre material que sí tiene es **peor** que una
incompleta que lo admite, porque el error es silencioso. Se arregla con
**`python3 _indice/actualizar.py`** más tres índices de carpeta escritos a mano y una decena de
tareas nuevas en `probar-descubrimiento.py`. Es media hora de trabajo y es lo primero que hay que
hacer.

Por detrás de eso quedan, en orden:

1. Las dos líneas de remisión del `hit_flash` en `04/02` y `04/03` — el defecto 🔴 nº 1 de la
   segunda ronda sigue medio abierto.
2. La excepción del asset **Extensión** en `AGENTS.md §4` y en `07/13`: es una prohibición dura de
   la biblioteca que tiene una excepción verificada y no documentada.
3. Podar `PENDIENTE-auditoria-2.md`, que hoy anuncia como pendiente lo que ya está escrito.
4. **GML Visual**: 313 páginas de manual y ningún documento propio. Es el único hueco de tema de
   verdadero tamaño que las dos rondas no vieron, y se explica por su punto ciego común —ambas
   auditaron *lo que se programa*, no *cómo se programa*.
5. Los huecos H2-H6: la persona que desarrolla, el trabajo encargado a terceros, el presupuesto de
   build, LFS y la accesibilidad cognitiva.

Ninguno de esos cinco impide hacer un juego. El primero, sí impide encontrar cómo.

---

## 5 · Limitaciones de esta revisión

- **La biblioteca se estaba escribiendo mientras se auditaba.** Entre las 16:07 y las 16:18 se
  cerraron seis propuestas y apareció un documento nuevo. Todo lo marcado como PARCIAL o NO HECHO
  hay que **releerlo contra el disco** antes de actuar: puede haberse cerrado después de las 16:18.
- **Sin acceso a la web en esta pasada.** No he verificado en vivo ninguna URL externa ni ninguna
  afirmación sobre servicios de terceros (Steam, GAG, la ley europea de accesibilidad). Todo lo que
  afirmo sale del disco o de la ejecución de los scripts del propio proyecto.
- **No he compilado nada.** `validar-compilacion.sh` no se ha ejecutado en esta sesión: crea un
  proyecto real con `gm-cli` y consume varios minutos. Me apoyo en `validar-codigo-gml.py`
  (comprueba que los símbolos existen, no que compile) y en que `06/README.md` declara la
  compilación de los once scripts. **El GML de los ~30 documentos nuevos no lo compila nadie**:
  `validar-compilacion.sh` solo cubre `06 - Assets y Scripts/`.
- **Verificación por muestreo, no lectura completa.** Los documentos nuevos suman ~35 000 líneas.
  He comprobado la **estructura** (encabezados) de todos y el **contenido** por `grep` de los
  conceptos e identificadores que cada informe pedía, abriendo entero solo lo dudoso. Un documento
  podría tener la sección correcta con código erróneo dentro sin que yo lo detecte; el único filtro
  que sí es exhaustivo es `validar-codigo-gml.py`.
- **La TAREA 2 tiene el sesgo de mi propia lista.** He probado ~60 temas candidatos, escogidos del
  ciclo de vida de un proyecto real, del árbol del manual y de las pistas del encargo. Un hueco que
  no se me haya ocurrido nombrar no sale en ningún `grep`. El cruce **sí** exhaustivo es el de
  familias de símbolos, y ese sale limpio: el riesgo residual está en lo que **no** es un símbolo
  —oficio, proceso, negocio, personas—, que es justo donde han caído H2 y H3.
- **No he auditado la calidad del espejo del manual más allá de las dos páginas que la segunda
  ronda señaló** (`All_Filter_Effect_Types` y `collision_line_list`). La nota de mantenimiento de
  `vfx.md` —«convendría comprobar si el mismo patrón de traducción de identificadores literales
  afecta a otras páginas»— **sigue sin responder**, y es una comprobación mecánica que merecería su
  propia pasada: cualquier página del espejo que traduzca una cadena literal que se pasa a una
  función es una trampa idéntica a la de los FX.
