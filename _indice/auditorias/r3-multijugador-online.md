# Auditoría r3 · Multijugador, redes y servicios online

> 6 de septiembre de 2026 · 78 temas evaluados · 37 cubiertos · 23 parciales · 18 faltan
> Referencia: GameMaker LTS 2026.0 (IDE `2026.0.0.16` · runtime `2026.0.0.23`)

## Resumen ejecutivo

El núcleo del netcode en tiempo real está **muy por encima de la media del oficio en español**:
`04 - Recetas por género/14 - Multijugador.md` (1 515 líneas) tiene predicción, reconciliación,
interpolación, salas, matchmaking por MMR y NAT explicados con código completo y verificado, y
`13/10 §14` resuelve anti-trampas y leaderboards con un rigor que no había visto en ningún otro
recurso de la biblioteca. El hueco que más duele no es de profundidad sino de **descubribilidad
y de "el motor ya lo trae"**: hay al menos tres capacidades **nativas** del runtime —UDP fiable
con un solo `network_set_config()`, un sistema de rollback netcode completo (`rollback_*`, 42
símbolos) y el requisito de WebSocket para llegar a un cliente HTML5— que existen, están
verificadas contra `GmlSpec.xml`, y **no aparecen citadas ni una vez** en los documentos que
tratan justo esos problemas. Un agente que siga la receta al pie de la letra construye un
servidor TCP que nunca podrá hablar con un build de HTML5, y va a buscar una librería de
terceros (GMS ENet) para algo que el motor resuelve en una línea. El segundo hueco real es de
**backend genérico**: todo lo online-no-Steam (autenticación con tokens, rate limiting, cuentas
propias, leaderboards sin Steam, async por servidor) está out of scope casi por completo.

## Tabla tema por tema

Leyenda: ✅ Cubierto · 🟡 Parcial · 🔴 Falta

### A · Fundamentos de red (12)

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| A1 | `network_create_socket`/`network_create_server` (cliente y servidor TCP) | ✅ | `04/14` §5.1-§5.3 (código completo, símbolos verificados) | — |
| A2 | `network_send_packet` + buffers como formato de paquete | ✅ | `04/14` §4.2, §5.0 (cabecera de tipo `u8` + payload) | — |
| A3 | TCP vs UDP vs WebSocket: cuándo cada uno | 🟡 | `04/14` §4.1 (tabla comparativa) | Solo comparación conceptual: **WebSocket nunca se implementa** en el código de §5 (que es 100 % TCP). Falta la regla del manual: *HTML5 no puede alojar servidor y solo se le llega por `network_socket_ws`/`_wss`* — ver B/red §D1 |
| A4 | Evento Async Networking (claves de `async_load`, todos los `type`) | ✅ | `04/14` §5.4 (switch completo: `network_type_data/connect/disconnect/non_blocking_connect`) | `network_type_up`/`_down`/`_up_failed` (pérdida de red del SO) no están en ese switch de referencia — solo se nombran en `08/21` como «útiles de verdad» |
| A5 | Fragmentación de paquetes / por qué pasa | ✅ | `04/14` §7 (tabla de errores: «Paquetes de más de ~1400 bytes → fragmentación y pérdidas masivas») | — |
| A6 | Tamaño máximo de paquete recomendado (MTU) | ✅ | `04/14` §4.3 («mantén los snapshots por debajo de ~1200 bytes») | — |
| A7 | Endianness | ✅ | `08/16 - Buffers.md` §"Notas" («little endian en todas las plataformas que soporta GameMaker») | — |
| A8 | Multicast UDP (`network_config_enable_multicast`) | 🔴 | Solo en `08/21` como nombre que «no aparece» en el manual, y en la tabla auto-generada de `08/_API del runtime/API-constantes.md` | 0 explicación de para qué sirve (descubrimiento de servicio por IPv6) ni cuándo usarlo |
| A9 | Descubrimiento de servidor en LAN por *broadcast* (`network_send_broadcast`) | 🔴 | Solo en la tabla auto-generada de funciones | Símbolo real y verificado, cero receta. Es la forma estándar de un "Buscar partida" en LAN sin escribir la IP a mano |
| A10 | Buffers: tipos, alineación, `buffer_seek`, liberación | ✅ | `08/16 - Buffers.md` completo + `04/14` §4.2 | — |
| A11 | Compresión de paquetes (`buffer_compress`/`buffer_decompress`) | 🟡 | `08/16` §"buffer_compress" — pero el único ejemplo es para un **fichero de guardado**, nunca para un snapshot de red | Ejemplo aplicado a comprimir un buffer de snapshot antes de `network_send_packet` |
| A12 | Integridad de paquete (checksum `buffer_crc32`/`buffer_md5`/`buffer_sha1`) | 🟡 | Se usan para replays firmados (`13/10` §14.3) y guardados (`01/14` §12), nunca para validar que un paquete de red no llegó corrupto | Nota de que existe la opción, y cuándo vale la pena frente al coste de CPU |

### B · Arquitecturas (7)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| B1 | Autoridad del servidor + interpolación (recomendada) | ✅ | `04/14` §2.1 (tabla de 3 modelos + recomendación) | — |
| B2 | P2P con autoridad compartida y sus riesgos | ✅ | `04/14` §2.1, §2.2 | — |
| B3 | Lockstep determinista (RTS, turnos) | 🟡 | Una fila de tabla en `04/14` §2.1 («Alta latencia, ideal para RTS/turnos») | Sin desarrollo: no hay ni el patrón de "solo se envían inputs", ni cómo sincronizar el arranque de turno entre todos los clientes |
| B4 | *Listen server* (host-cliente) vs servidor dedicado | 🟡 | El código de `04/14` §5.1-§5.2 **es** un listen server (`mi_id = 0` para el host) | El patrón nunca se nombra ni se compara explícitamente con un dedicado — un lector no sabe que ya está viendo uno de los dos modelos |
| B5 | *Host migration* | 🔴 | 0 menciones en toda la biblioteca | Qué pasa cuando el host de un listen server se desconecta: reelección, reconexión de los demás al nuevo host |
| B6 | Servidor dedicado *headless* en GameMaker | 🟡 | `04/14` §8 punto 7: «GameMaker puede compilar sin ventana… consulta el manual para tu plataforma concreta» | Ninguna cita real ni técnica: falta la opción de exportación concreta (o confirmar que no existe y hay que ocultar la ventana con `window_set_visible(false)` + desactivar el renderizado) |
| B7 | *Relay* (Photon, Steam Datagram Relay) | ✅ | `04/14` §1.2-§1.3, §10.4 (código `steam_net_sockets_*`) | — |

### C · Sincronización (11)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| C1 | Interpolación de entidades remotas | ✅ | `04/14` §4.5, §5.6 (código completo con `lerp` y retraso) | — |
| C2 | Extrapolación / *dead reckoning* | 🔴 | El término no aparece; la técnica tampoco (solo interpolación retrasada, que es lo contrario: mirar al pasado, no proyectar el futuro) | Cuándo usar extrapolación (huecos de red largos) y por qué es más arriesgada que interpolar |
| C3 | Snapshots del estado del mundo | ✅ | `04/14` §5.2 (`servidor_enviar_snapshot`), §5.5 (`recibir_snapshot`) | — |
| C4 | *Delta compression* | 🟡 | `04/14` §8 punto 1 — un párrafo, sin código | Implementación: qué estructura de datos guarda "el último snapshot confirmado por cliente" y cómo se serializa solo el delta |
| C5 | *Tick rate* / cadencia de envío | ✅ | `04/14` §4.3, constantes `NET_TICK_RATE`/`NET_SEND_EVERY` en §5.0 | — |
| C6 | Buffer de entrada (*input delay/buffering*, distinto de la predicción) | 🔴 | No se distingue de la predicción de §4.4 | El patrón de "retrasar N frames el input local para esconder la latencia sin rebobinar" (alternativa/complemento al rollback, la usa GGPO como *fallback*) |
| C7 | *Client-side prediction* | ✅ | `04/14` §4.4, §5.3 (`historial_prediccion`) | — |
| C8 | Reconciliación con umbral de tolerancia | ✅ | `04/14` §4.4, §5.7 (`reconciliar()`, corrección suave vs teletransporte) | — |
| C9 | Rollback netcode DIY (juegos de lucha) | 🟡 | `04/14` §4.6 — requisitos en prosa (determinismo, guardar/restaurar estado, coste de re-simular), **sin una sola línea de código** | Un esqueleto mínimo (guardar N estados en un anillo, comparar input tardío, re-simular) o al menos remitir a GGMR (`12/04` §4, catalogado pero no explicado) |
| C10 | **Rollback netcode NATIVO** (`rollback_*`) | 🔴 | Solo en `08/20 - Lo que el manual no documenta.md` §"Rollback/netcode (19)" como tabla de firmas, **sin ejemplo de uso y sin enlace desde `04/14` §4.6** | Ver hallazgo grave §1 abajo — documento nuevo o sección que explique el flujo completo con sus límites reales |
| C11 | Lockstep y trampas de punto flotante (determinismo entre CPUs, punto fijo) | 🟡 | `13/13 - Matemáticas...md` línea 2605: una fila de tabla («Simulación determinista: sí, crítico, aritmética entera o de punto fijo»); `13/10` §5.3 cubre determinismo de **semilla**, no de **punto flotante entre plataformas** | Por qué un `float` puede divergir entre Windows/Linux/consola (FMA, orden de operaciones) y un patrón de struct de punto fijo en GML (escalar a entero, dividir al leer) |

### D · Latencia (5)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| D1 | *Lag compensation* / *hit registration* (rebobinar hitboxes en servidor) | 🔴 | 0 menciones (el único hit de «lag compensation» en toda la biblioteca es un repo catalogado en `07/04`, no una explicación) | La técnica estándar de shooters en red: el servidor rebobina las posiciones pasadas del objetivo al momento en que el atacante disparó, antes de decidir el impacto |
| D2 | «Favor del atacante» como decisión de diseño consciente | 🔴 | No se nombra | Explicar el trade-off: compensar lag favorece al que dispara (puede matar a alguien que ya está a cubierto en su pantalla) |
| D3 | Ping / RTT: cómo medirlo | ✅ | `04/14` §5.4 (`NetMsg.ping`/`pong`), §5.8 (envío cada 2s) | — |
| D4 | *Jitter* | 🔴 | El término solo aparece en contextos de audio/gráficos, nunca de red | Qué es la variación de latencia y por qué un búfer de interpolación fijo no basta si el jitter es alto |
| D5 | Simulación de latencia en pruebas | ✅ | `12/04` §2 (Colyseus) y §3/§6 (MultiClient); **hallazgo nuevo**: `rollback_define_extra_network_latency()` nativo (`08/20` §"Rollback") | — |

### E · Estado y ancho de banda (5)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| E1 | Qué se replica y autoridad por entidad | ✅ | `04/14` §2.4 (`net_id`), §5.5 (`if (_datos.equipo == _nm.mi_id)`) | — |
| E2 | Área de interés / *relevancia* (interest management) | 🟡 | `04/14` §8 punto 2 — una línea, sin algoritmo | Un patrón concreto (rejilla espacial, radio de interés, o filtrar por `room`) para no enviar entidades lejanas |
| E3 | Presupuesto de ancho de banda | ✅ | `04/14` §4.3 (cifras reales: ~600 B/paquete, 12 KB/s a 20 Hz) | — |
| E4 | Serialización compacta con buffers (tipos pequeños en vez de `real`) | ✅ | `04/14` §5.2 (`buffer_u8`/`s16`/`u16` en vez de floats de 8 bytes) | — |
| E5 | Cuantización (escalado float→entero, *bit-packing*) como técnica nombrada | 🟡 | Se **usa** (`round(vel_x * 100)` a `s16`) pero nunca se nombra ni generaliza | Ejemplo de comprimir un ángulo 0-360° en un solo byte, y la fórmula general de cuantización con rango+precisión |

### F · Multijugador local (3)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| F1 | Pantalla partida (viewports + cámaras múltiples) | ✅ | `01/10 - Rooms, capas, cámaras y viewports.md` §7 "Pantalla partida" (código completo, 2 viewports + 2 `camera_create_view`) | — |
| F2 | Varios mandos, uno por jugador (co-op local 2-4) | 🟡 | `01/12 - Input...md` cubre un único `global.gamepad_slot` global | No hay el patrón "mando N → jugador N" para varios jugadores simultáneos en el mismo teclado/mandos |
| F3 | *Hot-join* local (unirse a mitad de partida en el mismo sofá) | 🔴 | 0 menciones | Cómo crear al jugador 2 al pulsar Start sin reiniciar la partida, y cómo redimensionar los viewports existentes |

### G · Steam (Steamworks) (6)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| G1 | `steam_lobby_*` (crear, filtrar, listar, unirse) | ✅ | `04/14` §10.3, verificado contra `docs/lobbies.js` de la extensión descargada | — |
| G2 | Expulsar de una lobby de Steam | ✅ (con caveat honesto) | `04/14` §10.3 — documenta que **no existe** `steam_lobby_kick` y por qué | — |
| G3 | `steam_net_sockets_*` (P2P por relay de Valve) | ✅ | `04/14` §10.4, verificado contra `docs/networking_sockets.js` | — |
| G4 | Logros y estadísticas de Steam | ✅ | `04/20` §1 | — |
| G5 | Steam Cloud (guardado en la nube) | ✅ | `04/20` §5 | — |
| G6 | Steam Workshop vs `mod.io` | 🟡 | `mod.io` catalogado en `07/01`, `07/03` | No aclara que GameMaker **no tiene** Steam Workshop nativo y que `mod.io` es el reemplazo oficial — un agente puede buscar `steam_ugc_*` sin saber que no aplica aquí |

### H · Alternativas y frameworks (9)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| H1 | Photon (extensión oficial completa) | ✅ | `04/14` §1.2, `12/04` §1 | — |
| H2 | Colyseus (servidor Node autoritativo) | ✅ | `12/04` §2 (código GML + arquitectura + demos) | — |
| H3 | Warp (framework de comunidad) | ✅ (catálogo) | `12/04` §3 | Solo ficha, sin ejemplo de uso — razonable dado que es de terceros y cambia rápido |
| H4 | **Nakama** | 🔴 | 0 menciones en toda la biblioteca | Ni siquiera una fila de catálogo, pese a ser una alternativa habitual a Colyseus |
| H5 | PlayFab | 🟡 | Una fila de tabla en `04/14` §1.3 | Sin detalle de API ni ejemplo — igual que Nakama, sería suficiente una ficha como la de Colyseus |
| H6 | Firebase (Auth, Firestore, Realtime DB) | 🟡 | `12/03` §5 (catalogado como `GMEXT-Firebase`, «Autenticación, Firestore, Realtime DB, Cloud Functions, Analytics») | Cero ejemplo de flujo: registrar usuario, guardar un documento, leerlo |
| H7 | Servidor propio en Node/Go | 🟡 | Colyseus **es** un servidor Node (`12/04` §2), pero un servidor genérico sin framework (socket TCP a pelo en Node) no se muestra | Sería útil un ejemplo mínimo de servidor Node con `net`/`ws` hablando el mismo protocolo de buffers de `04/14` §5.0, para quien no quiera Colyseus/Photon |
| H8 | HTTP REST + JSON (`http_request`/`http_post_string`) | 🟡 | `04/17 - Interoperabilidad con la web.md` §5 «Comunicarte con tu propio servidor» — ejemplo real con `json_stringify`/`json_parse`, aviso de CORS y de no meter claves de API en el cliente | Buen ejemplo pero **enterrado en el documento de HTML5** (no se referencia desde `04/14` ni `12/04`); usa `http_post_string` (sin cabeceras), no `http_request` con `header_map` |
| H9 | Autenticación con tokens (*bearer*/JWT) sobre HTTP | 🔴 | 0 menciones; el ejemplo de `04/17` §5 no manda cabecera `Authorization` | Ver hallazgo grave §4 abajo |

### I · Backend y seguridad (6)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| I1 | Cifrado TLS / HTTPS / WSS | 🔴 | `network_socket_wss` existe como constante (`08/_API del runtime/API-constantes.md`) sin ninguna explicación en prosa; `04/17` §5 usa `https://` en la URL sin decir por qué importa | Una frase que explique que `https://`/`network_socket_wss` cifran el transporte y que sin eso una contraseña o token viaja en claro |
| I2 | Leaderboards genéricos (no-Steam) contra un backend propio | 🟡 | La validación existe (`13/10` §14.2 `puntuacion_es_plausible`), pero no hay un ejemplo de **backend HTTP real** para subir/leer una tabla de clasificación fuera de Steam | Un endpoint de ejemplo (aunque sea pseudo-servidor) con `http_request` + JSON |
| I3 | Cuentas de usuario / autenticación de jugador propia (no Steam/Xbox) | 🟡 | Steam (`04/20` §1) y Xbox/UWP (`04/20` §6.2) tienen su login nativo | Sin guía de "cuenta propia" (email+contraseña u OAuth) contra un backend que no sea de plataforma |
| I4 | Persistencia en servidor (guardado remoto genérico) | 🟡 | Steam Cloud (`04/20` §5) y Firebase (catalogado) existen | Sin ejemplo de guardar/cargar un JSON contra un servidor propio vía `http_request` |
| I5 | Anti-trampas / validación en servidor / nunca confiar en el cliente | ✅ | `13/10` §14 completo (14.1-14.6): plausibilidad de puntuación, replay firmado con `sha1_string_utf8`, cómo funciona Cheat Engine y por qué la ofuscación no lo detiene; más `04/14` §2.2 | — |
| I6 | *Rate limiting* (proteger un backend propio contra abuso) | 🔴 | 0 menciones en toda la biblioteca | Ni un párrafo sobre limitar peticiones por IP/cuenta — relevante para cualquier leaderboard o backend propio |

### J · Matchmaking y lobbies (7)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| J1 | Modelo de datos de una sala (crear/listar/unirse/expulsar) | ✅ | `04/14` §10.1 (`SalaMultijugador : LobbyState() constructor`, código completo) | — |
| J2 | Matchmaking por cola FIFO | ✅ | `04/14` §10.2 (mencionado como caso trivial de `ColaMatchmaking`) | — |
| J3 | Matchmaking por MMR con ventana creciente | ✅ | `04/14` §10.2, código completo (`intentar_emparejar`) | — |
| J4 | ELO/Glicko como sistema de puntuación de habilidad | 🟡 | Se menciona («ajústalos a tu sistema de MMR: Elo, Glicko…») pero no se implementa ninguno de los dos algoritmos | Fórmula de actualización de Elo tras una partida (u honestamente remitir a que es fuera de alcance) |
| J5 | Selección de región | 🟡 | Solo como capacidad de Photon en tabla (`04/14` §1.2) | Sin patrón GML de cómo elegir/mostrar región al jugador |
| J6 | NAT traversal, tipos de NAT, CGNAT | ✅ | `04/14` §10.4 — explicación notablemente precisa y honesta | — |
| J7 | *Port forwarding* / UPnP explícitamente descartados | 🟡 | `04/14` §10.4 dice «abrir puertos en tu router no sirve de nada [con CGNAT]» | No menciona UPnP (0 hits en toda la biblioteca) como intento habitual que tampoco resuelve CGNAT ni funciona en la mayoría de redes domésticas modernas |

### K · Pruebas (3)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| K1 | Probar con varios clientes en local | ✅ | `MultiClient`, catalogado en `12/04` §3 y §6 (paso 3 del flujo recomendado) | — |
| K2 | Simulación de latencia en pruebas | ✅ | Colyseus (`12/04` §2) + hallazgo `rollback_define_extra_network_latency` (`08/20`) | — |
| K3 | Logs y diagnóstico de red | ✅ (cruzado) | `show_debug_message` en todo `04/14` §5; depuración general en `01/15` | — |

### L · Asincrónico (4)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| L1 | Juegos por turnos gestionados por servidor (*play-by-mail*) | 🔴 | 0 menciones | Patrón de "guardar el turno en el servidor, notificar al siguiente jugador, sondear o recibir push" |
| L2 | Notificaciones push (estado real en 2026) | 🔴 | `push_cancel_local_notification`/`push_get_first_local_notification`/`push_get_next_local_notification` marcadas **obsoletas** en `08/_API del runtime/API-funciones.md`; `ev_async_push_notification` solo nombrada en `01/06` §9 | Ninguna alternativa moderna explicada (p.ej. Firebase Cloud Messaging vía `GMEXT-Firebase`, ya catalogado en `12/03` §5 pero sin desarrollar) |
| L3 | Correo del juego / buzón *in-game* | 🔴 | 0 menciones | — |
| L4 | Guilds / gremios (sistema social persistente) | 🔴 | La única mención de «gremio» en la biblioteca es de lore narrativo (`13/12`), no de sistema | — |

## Huecos por prioridad

### 🔴 Graves

1. **UDP fiable nativo sin documentar.** `network_set_config(network_config_enable_reliable_udp, socket)` activa retransmisión con acuse de recibo **en una función del motor** (verificado: manual `Networking/network_set_config.md`, símbolo confirmado con `buscar.py`). `04/14` §8 punto 3 manda al lector a **una librería de terceros** (GMS ENet) para resolver justo esto, sin haber mencionado nunca que el motor ya lo trae. Es el hueco más caro de arreglar mal: cuesta una dependencia externa que no hacía falta.
2. **HTML5 no puede alojar servidor; necesita WebSocket para que le llegue tráfico.** Confirmado en el propio manual (`Networking/Networking.md`, párrafo completo citado arriba): *"si estás creando un proyecto para el objetivo HTML5 (...) no podrás usar las funciones de creación de server (...) tu servidor sólo puede comunicarse con la instancia HTML5 utilizando el protocolo Web Socket"*. Ni `04/14` ni `12/04` lo dicen. Un agente que siga el código de `04/14` §5.2 tal cual para dar soporte a un cliente web no recibirá ni un paquete, sin ningún error visible.
3. **Rollback netcode nativo (`rollback_*`, 42 símbolos) invisible desde la receta de multijugador.** Existe de verdad (`buscar.py --listar rollback_` → 42 símbolos; firmas en `08/20` §"Rollback/netcode"), con su propio evento asíncrono, chat, preferencias de jugador, input simulado para pruebas de sincronía y **`rollback_use_late_join()`** (hot-join nativo). Pero: (a) `04/14` §4.6 trata el rollback como "hazlo tú mismo, es un proyecto serio" sin nombrarlo; (b) nadie explica que depende de **GXC/Opera GX** (confirmado: la página de manual de GXC dice literalmente "para la plataforma de destino Opera GX"; los *release notes* oficiales del `GameMaker-Bugs` etiquetan varios fixes de `rollback_*` como `[OperaGX]`); (c) nadie avisa de que **fue retirado del `GmlSpec` en la Beta 2026.100 Release 2** (`02 - Novedades 2026/01` línea 192: *"Eliminado GmlSpec Rollback (R2): la funcionalidad de rollback multiplayer desaparece"*) — es decir, es una capacidad **de la versión LTS 2026.0 pinneada por esta biblioteca, sin futuro más allá de ella**, y sin un solo ejemplo de uso real en los 608 repos descargados.
4. **Autenticación con tokens sobre HTTP ausente.** `http_request(url, method, header_map, body)` acepta un `ds_map` de cabeceras (incluida `Authorization`) — está en el manual con ejemplo completo — pero **0 documentos propios** lo usan así; el único ejemplo real de la biblioteca (`04/17` §5) usa `http_post_string` sin cabeceras. Cualquier backend propio (leaderboard, cuenta de usuario) necesita esto.
5. ***Rate limiting* ausente.** 0 menciones. Sin él, cualquier receta de leaderboard/backend propio que el redactor construya a partir de esta auditoría queda coja de una defensa básica.
6. ***Lag compensation* / *hit registration* ausente.** Es la técnica estándar de todo shooter en red (Valve, charlas GDC de Overwatch) y esta biblioteca cubre varios géneros de disparo (`04/03` shmup, `04/02` top-down) sin resolver cómo validar un impacto en el servidor cuando el atacante ve al objetivo con retraso.

### 🟠 Medios

- TCP vs UDP vs WebSocket sin código real de WebSocket (A3).
- *Host migration* (B5) y servidor dedicado *headless* sin técnica concreta (B6).
- Lockstep desarrollado, con la trampa de punto flotante entre plataformas y un patrón de punto fijo en GML (B3, C11).
- *Dead reckoning*/extrapolación como técnica nombrada, distinta de la interpolación ya cubierta (C2).
- Buffer de entrada / *input delay* como alternativa al rollback (C6).
- Esqueleto de código para rollback DIY, o remitir con más peso a GGMR (C9).
- Varios mandos por jugador en co-op local + *hot-join* local (F2, F3).
- Nakama (ausente), PlayFab y Firebase solo catalogados sin flujo de uso (H4, H5, H6).
- Cuentas de usuario propias, persistencia genérica en servidor, leaderboard no-Steam (I2, I3, I4).
- Asincrónico: turnos por servidor, correo del juego, gremios, notificaciones push modernas (L1-L4).

### 🟡 Menores

- Multicast UDP y descubrimiento por *broadcast* en LAN (A8, A9).
- `buffer_compress`/checksums aplicados a paquetes de red, no solo a guardados (A11, A12).
- Área de interés con algoritmo concreto (E2); cuantización nombrada como técnica general (E5).
- Selección de región (J5); UPnP descartado explícitamente (J7).
- `network_type_up/down/up_failed` integrados en el switch de referencia (A4).
- Aclarar Steam Workshop vs `mod.io` (G6).
- TLS/WSS explicado con una frase, no solo usado sin comentario (I1).

## Encargo para el redactor

1. **Sección nueva en `04 - Recetas por género/14 - Multijugador.md`, dentro de §8 "Cómo escalarlo", punto 3** ("UDP fiable propio"): antes de mandar a GMS ENet, añadir 10-15 líneas con `network_set_config(network_config_enable_reliable_udp, socket)` y `network_set_config(network_config_disable_reliable_udp, socket)`, citando que hay que activarlo en **ambos extremos** y que añade una cabecera de 12 bytes (fuente: manual `Networking/network_set_config.md`, ya espejado en español). Símbolos verificados: `network_set_config`, `network_config_enable_reliable_udp`, `network_config_disable_reliable_udp`.

2. **Aviso nuevo en `04/14` §4.1** (tabla TCP/UDP/WebSocket) y en `12 - Utilidades e integraciones/04 - Multijugador y red.md` §5: una nota de advertencia citando el manual — un target HTML5 no puede llamar a `network_create_server()` y solo se le llega con `network_socket_ws`/`network_socket_wss`; por tanto un servidor que deba aceptar clientes de escritorio **y** web necesita **dos sockets de escucha**. Símbolos verificados: `network_socket_ws`, `network_socket_wss`, `network_create_server`.

3. **Sección nueva §4.6 bis en `04/14`** (justo después de "Rollback completo"), o documento aparte enlazado desde ahí: explicar el sistema nativo `rollback_*` con sus tres límites reales — (a) requiere **GXC/Opera GX** (cita: manual `GXC/GXC_Functions.md`, "Opera GX y GXC"); (b) **fue retirado del `GmlSpec` en la Beta 2026.100 R2** (cita: `02 - Novedades 2026/01 - Resumen LTS 2026.0.md` línea 192); (c) **cero ejemplos de uso real** encontrados en 608 repos. Aun así listar el flujo mínimo verificado: `rollback_define_player()` → `rollback_define_input()` → `rollback_create_game()`/`rollback_join_game()` → `rollback_sync_on_frame()` en el Step → `rollback_get_input([player_id])`. Mencionar `rollback_use_late_join()` (hot-join nativo) y `rollback_define_extra_network_latency()` (simulación de latencia para pruebas). Marcar todo con ⚠️ de alcance limitado. Símbolos verificados (`buscar.py --listar rollback_`, 42 resultados): los citados más `rollback_display_events`, `rollback_chat`, `rollback_use_player_prefs`, `rollback_define_mock_input`, `rollback_use_random_input`.

4. **Sección nueva "Autenticación con tokens" en `12/04` o en una nueva §6 de `04/17`**, enlazada desde `04/14`: ejemplo con `http_request(url, "POST", header_map, body)` donde `header_map` es un `ds_map` con `"Authorization": "Bearer " + token`. Símbolos verificados: `http_request`, `ds_map_create`, `ds_map_add` (patrón tomado literalmente del ejemplo del manual `Asynchronous_Functions/HTTP/http_request.md`, adaptado a token en vez de Basic Auth). Enlazar el ejemplo ya existente y bueno de `04/17` §5 en vez de duplicarlo.

5. **Párrafo nuevo en `13/10` §14 o nueva §14.7**: *rate limiting* básico — validar en el propio backend un máximo de envíos por IP/cuenta y periodo antes de aceptar una puntuación o guardado, enlazando con la validación ya existente de §14.2. No requiere símbolos de GML nuevos (es lógica de servidor, fuera de GameMaker).

6. **Sección nueva en `04/14`, quizá un §4.7 "Compensación de lag (*lag compensation*)"**: explicar el rebobinado de hitboxes en el servidor al timestamp del disparo del cliente, usando el mismo patrón de `historial_prediccion` de §5.3 pero aplicado al **objetivo** en vez de al propio jugador. Sin símbolos nuevos de GML — es un patrón de datos (histórico de posiciones por entidad + `point_distance`/`collision_*` contra la posición histórica, ya usada en `04/30` para hitboxes).

7. **Ficha nueva en `12/04` §4** (tabla del resto del ecosistema): añadir fila para **Nakama** (servidor open-source, alternativa a Colyseus) siguiendo el mismo formato que la de PlayFab — sin inventar API GML, solo catalogarlo como se hizo con Warp.

8. **Sección corta en `01/12 - Input...md`**: patrón de "mando N → jugador N" para co-op local (usar `gamepad_get_device_count()`/`gamepad_enumerate()` ya documentados en la tabla de §4, asignando cada slot a un jugador en el evento *Async System* "gamepad discovered" ya existente en el propio documento).

9. **Nota en `07 - Ecosistema/03 - Extensiones oficiales y de terceros.md` o en `04/14`**: aclarar explícitamente que GameMaker no tiene Steam Workshop nativo (`steam_ugc_*` no existe; verificar con `buscar.py --listar steam_ugc` antes de escribir la nota) y que `mod.io` (`GMEXT-mod.io`) es el camino oficial.

## Lo que comprobé y NO hacía falta

- **Predicción, reconciliación e interpolación**: pensé que serían un hueco típico de bibliotecas en español y están resueltos con código completo y buen nivel (`04/14` §4.4-§4.5, §5.5-§5.7).
- **Anti-trampas y validación de leaderboard**: existe una sección completa y honesta (`13/10` §14) que ya cubre replay firmado, Cheat Engine, speedhack y por qué la ofuscación de guardado no basta — no hacía falta nada nuevo aquí, solo enlazarla mejor desde el backend genérico del encargo #4-5.
- **Salas, matchmaking por MMR y NAT traversal**: pensé que serían huecos (así lo marcó una auditoría anterior, `ingenieria.md` F7/F8) pero **ya se cerraron** en `04/14` §10 con código completo y una explicación de NAT/CGNAT notablemente precisa. No reabrir.
- **Steam lobbies y P2P sockets**: verificados contra la documentación fuente descargada de la propia extensión (`docs/lobbies.js`, `docs/networking_sockets.js`), no contra suposiciones — están bien y con las advertencias correctas (`steam_lobby_kick` no existe, y se explica por qué).
- **Photon y Colyseus**: catalogados con nivel de detalle suficiente para decidir cuál usar; no necesitan más desarrollo dentro de esta biblioteca porque son productos de terceros con su propia documentación externa completa.
