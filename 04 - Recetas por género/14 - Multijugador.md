# 14 — Multijugador

> **Dificultad:** avanzada · **Lee esto antes de empezar un proyecto online**
> GameMaker **no tiene** multijugador integrado de alto nivel. Tiene sockets de
> bajo nivel y una estrategia oficial basada en extensiones de terceros. Este
> documento explica exactamente qué hay, qué no, y cómo montarlo tú.

---

## 1. Visión general: el estado real en 2026

### 1.1 Lo que dice YoYo Games oficialmente

Del blog **GameMaker Update Spring 2026** (Russell Kay, 30 de abril de 2026),
sección *Multiplayer*:

> "We tried a few avenues for online multiplayer with GameMaker and ultimately
> decided to focus our work with several multiplayer system providers to bring
> industry standard services into GameMaker as extensions. Giving you as a
> developer some choice on what you use when developing a multiplayer game.
> We'll also continue our official support of the Steamwork multiplayer. Some
> of the partners we're working with already have extensions released with more
> coming: **Namazu Elements, Colyseus, Steamworks, Photon (Coming soon)**."

Traducción operativa: **no esperes un `multiplayer_start()` nativo.** Lo que
hay es:

| Capa | Qué existe |
|---|---|
| **Red de bajo nivel** | Sockets TCP, UDP y WebSocket nativos + buffers. Completo y funcional |
| **Red de alto nivel** | Nada integrado. Lo aportan las extensiones |
| **Oficial de YoYo Games** | Photon (desde julio 2026), Steamworks |
| **Terceros con comunidad** | Colyseus, Namazu Elements, GMS ENet, PlayFab |

### 1.2 Photon: la apuesta oficial (julio de 2026)

Publicado el 14 de julio de 2026 por Patrick Roche (YoYo Games). Es la
extensión oficial más reciente y la primera "solución completa".

**Lo que trae:**

- **Multijugador en tiempo real**: rooms, lobbies, *matchmaking*.
- **Estado de juego sincronizado**: *compare-and-swap* para garantizar que
  todos ven lo mismo; soporta *payloads* binarios propios además de strings.
- **Chat de texto en el juego**: lista de amigos, mensajes privados, presencia,
  múltiples canales.
- **Chat de voz**: canales en vivo, mute por jugador, control de volumen,
  detección de voz, y acceso a bitrate y códec.
- **Diagnóstico de red integrado**: ping, RTT, estadísticas de tráfico,
  selección de región, pérdida de paquetes.

**Importante sobre GMRT:** el propio anuncio indica que **Fusion Core 3**
(Photon) llegará **al nuevo runtime GMRT como característica central**, no al
GMS2 Runtime. Si trabajas en GMS2 (como toda esta biblioteca), usa la
extensión, no esperes integración nativa.

Repositorio: `https://github.com/YoYoGames/GMEXT-Photon`

### 1.3 Otras extensiones

| Extensión | Tipo | Notas |
|---|---|---|
| **GMEXT-Photon** | Oficial YoYo Games | Cloud, rooms, voz, chat. La más completa en 2026 |
| **GMEXT-Steamworks** | Oficial YoYo Games | P2P con Steam Networking, lobbies, *matchmaking*. Requiere tener acceso a la API de Steam de tu juego |
| **Colyseus** | Tercero, citado por YoYo | Servidor Node.js con sincronización de estado. Muy usado en juegos web |
| **Namazu Elements** | Tercero, citado por YoYo | Backend como servicio |
| **GMS ENet** | Comunidad (jul 2026) | UDP fiable con capa propia de secuenciación. Buena opción si quieres control total |
| **PlayFab Party / Multiplayer** | Tercero | Multijugador a escala con servicios de Azure |

### 1.4 Lo que SÍ trae GameMaker de serie

Del manual oficial, sección *Networking*:

- Sockets TCP (orientado a conexión), UDP (sin conexión) y **WebSocket**.
- IPv4 e IPv6 en todas las plataformas **excepto** Nintendo Switch,
  PlayStation 4 y PlayStation 5.
- Envío y recepción mediante **buffers**.
- Un **evento asíncrono de red** que entrega un DS map con los datos.

Esto basta para montar tu propio netcode. No es cómodo, pero es suficiente y
es lo que haremos en esta receta.

---

## 2. Arquitectura recomendada

### 2.1 Elige el modelo de red antes de escribir una línea

Esta decisión es **casi imposible de cambiar después**. Tres opciones:

| Modelo | Cómo funciona | Latencia sentida | Ideal para |
|---|---|---|---|
| **Lockstep determinista** | Todos los clientes simulan lo mismo; solo se envían inputs | Alta (hay que esperar al más lento) | RTS, juegos por turnos, lucha con rollback |
| **Autoridad del servidor + interpolación** | El servidor manda el estado; los clientes interpolan entre snapshots | Media (100-150 ms) | Shooters, top-down, carreras |
| **P2P con autoridad compartida** | Cada cliente manda sus entidades | Baja pero insegura | Cooperativo de pocos jugadores, sin competitivo |

**Recomendación general:** autoridad del servidor + interpolación. Es el más
fácil de hacer bien y el más tolerante a la latencia. **Evita el P2P con
autoridad compartida en cualquier juego competitivo**: permite trampear.

### 2.2 Nunca confíes en el cliente

Si el cliente puede decir "he matado a ese", el cliente puede mentir. En un
modelo con servidor:

- El cliente envía **intenciones** ("me muevo a la derecha", "disparo").
- El servidor valida y decide el resultado.
- El cliente recibe el estado y lo muestra.

El cliente puede predecir localmente para que se sienta inmediato (ver 4.4),
pero **el servidor siempre tiene la última palabra**.

**Esta regla no es solo para partidas en tiempo real.** Si tu juego tiene cualquier backend
propio —leaderboard, cuenta de usuario, guardado remoto—, "nunca confíes en el cliente" se
traduce en tres piezas concretas que esta biblioteca ya cubre, aunque no vivan en este
documento: **autenticar** cada petición con un token en vez de confiar en quién dice ser el
cliente ([`04 · 17`](17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md) §6),
**limitar cuántas veces** se puede llamar a ese backend antes de aceptar más peticiones
([`13 · 10`](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/10%20-%20Testing%20y%20QA.md) §14.7),
y **validar en servidor** lo que el cliente afirma (puntuaciones, replays, resultado de una
partida — ya resuelto en
[`13 · 10`](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/10%20-%20Testing%20y%20QA.md) §14
completo).

### 2.3 Jerarquía de objetos

```
objNetManager        (persistente: sockets, buffers, cola de mensajes)
├── rol: "servidor" | "cliente" | "ninguno"
├── objNetEntity     (padre: entidades sincronizadas)
│   ├── net_id       → ID estable en la red (¡NO el id de instancia!)
│   └── propietario  → qué cliente la controla
└── objLobby         (UI: conectar, listar partidas)
```

### 2.4 La regla del `net_id`

**Nunca envíes `id` de instancia por la red.** Los IDs son locales a cada
máquina y no coinciden. Cada entidad sincronizada necesita un **ID de red
propio y estable**, asignado por el servidor.

```gml
net_id = -1;    // lo asigna el servidor al crear la entidad
```

---

## 3. El bucle central (core loop)

```
┌─ Red: evento Async Networking ───────────────────────────┐
│ A. Recibir paquetes → parsear por tipo de mensaje        │
│    - snapshot de estado → guardarlo en el buffer de      │
│      interpolación                                       │
│    - evento (muerte, disparo) → aplicarlo                │
│    - conexión / desconexión de un cliente                │
└──────────────────────────────────────────────────────────┘
┌─ Step ───────────────────────────────────────────────────┐
│ B. Cliente: leer input → enviar intención (cada frame o  │
│    cada N frames)                                        │
│ C. Cliente: predecir su propio movimiento localmente     │
│ D. Cliente: interpolar el resto de entidades entre los   │
│    dos últimos snapshots recibidos                       │
│ E. Servidor: recoger intenciones de todos → simular      │
│ F. Servidor: cada N frames, enviar snapshot a todos      │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 TCP vs UDP vs WebSocket

| Protocolo | Garantías | Latencia | Úsalo para |
|---|---|---|---|
| **TCP** | Entrega ordenada y fiable | Variable; se bloquea si se pierde un paquete | Lobby, chat, guardado en la nube, juegos por turnos |
| **UDP** | Sin garantías; llega o no | Baja y constante | Juegos de acción en tiempo real |
| **WebSocket** | Como TCP, sobre HTTP | Variable | Juegos web (HTML5), integración con servidores Node |

**Regla práctica:** acción en tiempo real → UDP. Todo lo demás → TCP. No
intentes hacer un shooter sobre TCP: cuando se pierda un paquete, todo lo demás
se bloquea esperándolo.

> ⚠️ **HTML5 no puede alojar un servidor, y solo se le llega por WebSocket.** El manual oficial
> lo dice sin rodeos: *"si estás creando un proyecto para el objetivo HTML5 (...) no podrás
> usar las funciones de creación de server debido a las restricciones del navegador"* —
> `network_create_server()` simplemente no funciona en un build HTML5. Y si tu servidor de
> escritorio/móvil necesita aceptar también clientes web, el propio manual añade la segunda
> mitad del problema: *"su server sólo puede comunicarse con la instancia HTML5 utilizando el
> protocolo Web Socket"*, con `network_socket_ws` (sin cifrar) o `network_socket_wss` (cifrado,
> equivalente a HTTPS) — ver [`network_create_server()`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Networking/network_create_server.md).
> En la práctica esto significa **dos sockets de escucha en el servidor**, uno
> `network_socket_tcp`/`network_socket_udp` para Windows/Android/etc. y otro
> `network_socket_ws`/`network_socket_wss` para el navegador — el código 100 % TCP de la §5 de
> esta receta, tal cual, **no recibirá ni un paquete de un cliente HTML5, sin ningún error
> visible**. Símbolos verificados: `network_create_server`, `network_socket_ws`,
> `network_socket_wss`.

### 4.2 Buffers: el formato de los paquetes

Todo lo que envías va en un buffer. Firmas verificadas:

```gml
buffer_create(size, type, alignment);     // type: buffer_fixed | buffer_grow | buffer_wrap
buffer_seek(buffer, base, offset);        // base: buffer_seek_start | _relative | _end
buffer_write(buffer, type, value);        // escribe en la posición de búsqueda actual
buffer_read(buffer, type);                // lee desde la posición actual
buffer_tell(buffer);                      // posición actual
buffer_delete(buffer);                    // liberar SIEMPRE
network_send_packet(socket, bufferid, size);
```

Tipos de datos: `buffer_u8`, `buffer_s8`, `buffer_u16`, `buffer_s16`,
`buffer_u32`, `buffer_s32`, `buffer_f16`, `buffer_f32`, `buffer_f64`,
`buffer_bool`, `buffer_string`, `buffer_text`.

**Diseño del paquete: empieza siempre por un byte de tipo.** Es la convención
más simple y la que mejor escala.

```
[0]      → tipo de mensaje (u8)
[1..]    → payload según el tipo
```

### 4.3 Cadencia de envío y ancho de banda

| Qué | Cuándo enviar |
|---|---|
| Input del cliente | Cada frame, o cada 2-3 frames si vas justo |
| Snapshot del servidor | Cada 3-6 frames (10-20 Hz es suficiente para la mayoría) |
| Eventos (muerte, disparo) | Inmediato, con fiabilidad propia |
| Chat | Al pulsar Enter |

**Tamaño de paquete:** mantén los snapshots por debajo de ~1200 bytes (el MTU
típico de Ethernet es 1500). Si se te va de ahí, divide en varios paquetes o
comprime.

**Optimización clave: solo envía lo que cambió.** Un snapshot completo de 50
entidades son ~600 bytes por paquete y por cliente. A 20 Hz son 12 KB/s por
cliente. Un delta (solo las entidades que se movieron) reduce eso a una
fracción.

### 4.4 Predicción del cliente y reconciliación

Sin predicción, el jugador pulsa "adelante" y tarda un RTT entero en ver el
movimiento. Con 100 ms de RTT, el juego se siente pastoso.

**Cómo funciona:**

1. El cliente aplica su input **inmediatamente** y guarda el resultado en un
   historial con un número de secuencia.
2. El servidor responde con el estado real y el último número de secuencia que
   procesó.
3. El cliente compara: si coincide, todo bien. Si no, **rebobina** al estado
   del servidor y **re-simula** los inputs posteriores.

Ese "rebobinar y re-simular" es el **rollback**.

```gml
// Historial del cliente
historial[secuencia] = { x, y, vel_x, vel_y };
```

**Reconciliación suave:** si la discrepancia es pequeña, corrígela con `lerp`
en lugar de teletransportar. Los saltos de posición se notan muchísimo.

### 4.5 Interpolación de entidades remotas

El servidor manda snapshots a 20 Hz; tú dibujas a 60 Hz. Hay huecos de 3
frames. Sin interpolación, las entidades remotas se mueven a trompicones.

**Solución:** guarda los últimos dos snapshots y dibuja en un punto
intermedio, retrasado un intervalo de snapshot:

```gml
// Dibujar en (ahora - intervalo_entre_snapshots)
var _t = (tiempo_actual - tiempo_retraso) / intervalo_snapshot;
x = lerp(snapshot_anterior.x, snapshot_reciente.x, _t);
```

Ese retraso de ~50 ms es invisible y elimina los trompicones por completo.

### 4.6 Rollback completo (para juegos de lucha)

En un juego de lucha no basta con predecir tu movimiento: hay que predecir el
del rival, y cuando llega el input real, **rebobinar el mundo entero** y
re-simular.

Requisitos estrictos:

1. **El juego debe ser determinista.** Mismo estado + mismos inputs = mismo
   resultado. Nada de `random()` sin semilla, nada de `current_time`.
2. **Debes poder guardar y restaurar el estado completo** cada frame.
3. **El coste de re-simular N frames cabe en un frame.** Con N = 8 y un juego
   sencillo, sí cabe.

Es factible en GameMaker, pero es un proyecto serio. Para tu primer juego
online, usa autoridad del servidor con interpolación.

### 4.6 bis · Rollback netcode NATIVO (`rollback_*`) — con límites reales

Todo el §4.6 anterior describe un rollback **hecho a mano**. Lo que no se ha dicho hasta aquí
es que el runtime trae su **propio** sistema de rollback: 42 símbolos `rollback_*`, confirmados
contra el `GmlSpec.xml` instalado:

```sh
python3 "_indice/buscar.py" --listar rollback_
# → 42 símbolos empiezan por «rollback_»
```

⚠️ **Antes de emocionarte, sus tres límites reales:**

1. **Depende de GXC/Opera GX.** No es multiplataforma como el resto de esta receta.
   `rollback_create_game()` "conecta con GXC y crea una partida — el usuario debe estar
   identificado en GXC", y el propio manual dedica su sección **GXC** en exclusiva a
   "la plataforma de destino Opera GX" —
   [`GXC/GXC_Functions`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/GXC/GXC_Functions.md).
   Si tu juego no se publica (también) para Opera GX, este sistema no es una opción para ti.
2. **Fue retirado del `GmlSpec` en la Beta 2026.100 R2.** Los *release notes* de esta misma
   biblioteca lo dicen sin ambigüedad: *"Eliminado GmlSpec Rollback (R2): la funcionalidad de
   rollback multiplayer desaparece. Si tu juego lo usa, quédate en 2026.0 hasta tener
   alternativa"* —
   [`02 - Novedades 2026/01 · Resumen LTS 2026.0`](../02%20-%20Novedades%202026/01%20-%20Resumen%20LTS%202026.0.md).
   Es decir: es una capacidad de **esta versión LTS 2026.0** (la que fija esta biblioteca), sin
   garantía de futuro más allá de ella.
3. **Cero ejemplos de uso real.** En los más de 600 repositorios descargados en
   `11 - Código descargado/`, las únicas apariciones de `rollback_*` son catálogos de símbolos y
   herramientas que listan la API completa del runtime (extractores de `GmlSpec.xml`,
   generadores de tipos) — ninguna es un juego usándolo de verdad. No hay precedente al que
   mirar si algo falla.

**Ninguna de las tres páginas de manual que declara el propio `GmlSpec.xml` existe** —
`…/Rollback/Rollback_Functions/rollback_get_input.htm` devuelve 403, no 200. El catálogo
completo de firmas, sin ejemplo de uso, está en
[`08 · 20 — Lo que el manual no documenta`](../08%20-%20Referencia%20GML%20completa/20%20-%20Lo%20que%20el%20manual%20no%20documenta.md)
§"Rollback / netcode". Aun con todo eso, el flujo mínimo verificado es este:

```gml
// ═══════════ scr_rollback_nativo — ⚠️ requiere Opera GX/GXC, ver límites arriba ═══════════

// --- Antes de crear o unirse a una partida --------------------------------------------
rollback_define_player(objJugador);              // qué objeto representa a cada jugador
rollback_define_input(input_frame_vacio());       // forma del struct de input que sincroniza

// --- Anfitrión: crea la partida ------------------------------------------------------
rollback_create_game(2);          // 2 jugadores; sync_test y region son opcionales

// --- El otro jugador: se une -----------------------------------------------------------
// rollback_join_game();

// --- En el Step, CADA frame -------------------------------------------------------------
if (rollback_sync_on_frame())     // true solo cuando ya llegó el input de TODOS los jugadores
{
    var _mi_input    = rollback_get_input();          // el propio
    var _input_rival = rollback_get_input(id_rival);  // el del otro jugador
    // ...simular el frame con ambos inputs — el propio sistema hace el rebobinado y
    // re-simulado por debajo cuando un input tardío obliga a corregir el pasado.
}
```

Dos funciones de diagnóstico que valen oro para probar sin salir de tu máquina:

```gml
rollback_define_extra_network_latency(120);   // simula 120 ms de latencia añadida, para probar
// ⚠️ rollback_use_late_join() SOLO EN `fnames`: existe en el runtime pero GmlSpec.xml no la
// declara y Feather no la reconoce (sin autocompletado). Verifícala en tu proyecto antes de
// apoyarte en ella para el hot-join nativo.
rollback_use_late_join();
```

Símbolos verificados con `buscar.py`: `rollback_define_player`, `rollback_define_input`,
`rollback_create_game`, `rollback_join_game`, `rollback_sync_on_frame`, `rollback_get_input`,
`rollback_define_extra_network_latency`, `rollback_use_late_join` (⚠️ solo en `fnames`),
además de `rollback_start_game`, `rollback_leave_game`, `rollback_use_manual_start`,
`rollback_display_events`, `rollback_chat`, `rollback_use_player_prefs`,
`rollback_set_player_prefs`, `rollback_get_player_prefs`, `rollback_define_mock_input` y
`rollback_use_random_input` (estas dos últimas, para simular a los rivales en pruebas de
sincronía sin tener a nadie más conectado).

> 💡 **La recomendación de esta receta no cambia**: para tu primer juego de lucha o de mucho
> *timing*, el rollback DIY del §4.6 (multiplataforma, sin fecha de caducidad conocida) sigue
> siendo la apuesta más segura. Usa `rollback_*` nativo solo si ya estás comprometido con
> Opera GX/GXC como plataforma y aceptas el riesgo de que desaparezca en un runtime posterior.

### 4.7 · Compensación de lag (*lag compensation*) y *hit registration*

Ningún género de disparo en red escapa a este problema, y esta receta no lo había resuelto
todavía: el atacante **siempre** ve al objetivo con retraso — por la interpolación retrasada
del §4.5 en su propia pantalla, y por el viaje de ida y vuelta del paquete de disparo. Si el
servidor valida el impacto contra la posición **actual** del objetivo, el atacante falla
sistemáticamente tiros que en su pantalla eran limpios, y cuanto más ping tenga, peor.

**La técnica estándar** (la usan Source/Counter-Strike y la explican las charlas GDC de
*Overwatch*): el servidor guarda un historial de posiciones de cada entidad con marca de
tiempo, y cuando llega un disparo con el instante en que el cliente **vio** al objetivo,
rebobina — no el mundo entero como en el rollback de §4.6, solo el hitbox del objetivo — a la
posición que tenía en ese instante, y valida el impacto contra **esa** posición.

```gml
// ═══════════ objNetEntity — Create (añade esto al Create de §5.6) ═══════════
historial_hitbox = [];      // solo lo necesita rellenar el servidor
```

```gml
// ═══════════ objNetEntity — Step del SERVIDOR (añade esto al Step de §5.6) ═══════════
if (objNetManager.rol == "servidor")
{
    array_push(historial_hitbox, { t: current_time, x: x, y: y });

    // Solo hace falta cubrir el margen de latencia que vayas a compensar (aquí, 300 ms).
    // A 60 fps son ~18 registros por entidad: recorta el resto para no acumular memoria.
    while (array_length(historial_hitbox) > 0
        && current_time - historial_hitbox[0].t > 300)
    {
        array_delete(historial_hitbox, 0, 1);
    }
}
```

```gml
// ═══════════ scr_lag_compensation ═══════════

/// @func hitbox_en_instante(_historial, _instante)
/// @desc Busca la posición del historial más cercana a _instante, interpolando entre las dos
///       muestras que lo rodean — el mismo principio que ya usa §5.6 con los snapshots de red.
/// @returns {Struct} { x, y } o undefined si el historial está vacío.
function hitbox_en_instante(_historial, _instante)
{
    var _n = array_length(_historial);
    if (_n == 0) return undefined;
    if (_instante <= _historial[0].t) return { x: _historial[0].x, y: _historial[0].y };

    for (var _i = 1; _i < _n; _i++)
    {
        if (_historial[_i].t >= _instante)
        {
            var _a = _historial[_i - 1];
            var _b = _historial[_i];
            var _t = (_instante - _a.t) / max(1, _b.t - _a.t);
            return { x: lerp(_a.x, _b.x, _t), y: lerp(_a.y, _b.y, _t) };
        }
    }

    var _ultimo = _historial[_n - 1];
    return { x: _ultimo.x, y: _ultimo.y };
}

/// @func servidor_validar_disparo(_x_disparo, _y_disparo, _objetivo, _instante_cliente, _radio)
/// @desc Comprueba el impacto contra la posición que tenía _objetivo cuando el ATACANTE lo
///       vio, no contra su posición actual. _instante_cliente viaja en el paquete de disparo,
///       con el mismo current_time que ya usa el ping de §5.4/§5.8.
/// @returns {Bool}
function servidor_validar_disparo(_x_disparo, _y_disparo, _objetivo, _instante_cliente, _radio)
{
    // Nunca confíes en el timestamp del cliente sin límite (14.2 de 13/10): acótalo al margen
    // de historial que de verdad guardas arriba.
    var _maximo_rebobinado = 300;    // ms
    var _instante = clamp(_instante_cliente, current_time - _maximo_rebobinado, current_time);

    var _pos = hitbox_en_instante(_objetivo.historial_hitbox, _instante);
    if (_pos == undefined) return false;

    // Geometría pura contra la posición HISTÓRICA. A propósito NO se usa collision_circle() ni
    // place_meeting(): esas funciones comprueban la posición ACTUAL de la instancia en la
    // room, no una coordenada arbitraria que tú elijas — no hay forma de pedirles "como si
    // estuviera aquí". point_in_circle() sí compara un punto contra un círculo cualquiera.
    return point_in_circle(_x_disparo, _y_disparo, _pos.x, _pos.y, _radio);
}
```

Símbolos verificados: `point_in_circle(px, py, x1, y1, rad)`, `current_time`, `clamp`, `lerp`,
`array_push`, `array_delete`.

**"Favor del atacante" no es un bug: es una decisión de diseño.** Compensar el lag siempre
favorece a quien dispara — puede matar a alguien que, en SU pantalla, ya estaba a cubierto,
porque el servidor está validando contra el pasado del objetivo. La alternativa (validar contra
el presente) favorece al defensor pero hace que el atacante con ping alto no pueda acertar
nunca un tiro limpio. La mayoría de shooters competitivos eligen favorecer al atacante porque
"me mataron después de esconderme" se siente menos injusto para el conjunto de la partida que
"disparé bien y no le di nunca". Decide esto **antes** de programarlo, no lo dejes caer por
accidente en cómo implementes el rebobinado.

> ⚠️ **El techo práctico en GML: no hay rebobinado gratis contra el sprite mask.** Las
> funciones de colisión del motor (`collision_circle`, `collision_line`, `place_meeting`…)
> siempre comprueban la posición **real y actual** de la instancia en la room — no existe un
> "como si `_objetivo` estuviera en (x, y)" que reutilice su máscara de sprite. La única forma
> de comprobar un impacto contra una posición pasada sin mover la instancia (y sin arriesgarte
> a disparar sus propios eventos de colisión) es con geometría pura —`point_in_circle`,
> `point_in_rectangle`, `rectangle_in_rectangle`— contra una forma simple que tú mismo guardes
> en el historial, como el círculo de arriba. Es exactamente lo que hacen los shooters grandes
> (los hitboxes de *Overwatch* son cápsulas, no la malla del personaje), así que no es una
> limitación que se note en la práctica — pero si tu combate depende de un hitbox con la
> silueta exacta del sprite, esa precisión no sobrevive al rebobinado. Guarda también el
> **tamaño** de la forma en el historial si tu entidad cambia de hitbox con la animación
> (agacharse, cargar un golpe): un círculo o rectángulo fijo por entidad no basta en ese caso.
>
> El otro límite es de memoria/CPU, no del lenguaje: el coste escala con *jugadores × entidades
> relevantes × fotogramas de la ventana de compensación*. Para un puñado de jugadores en una
> arena es insignificante; si tu juego tiene cientos de entidades, combina esto con el área de
> interés del §8 punto 2 antes de guardar historial de todo lo que existe en la room.

Ver también: [`04 · 30 — Combate cuerpo a cuerpo`](30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md)
para el diseño de hitboxes/hurtboxes en sí; esta sección solo añade el rebobinado temporal por
encima de las formas que ya definas allí.

---

## 5. Código base

### 5.0 Constantes de protocolo

```gml
// ---------------------------------------------------------------------------
// scr_net_config
// ---------------------------------------------------------------------------

// --- Tipos de mensaje (u8) -------------------------------------------------------
enum NetMsg {
    ping          = 1,
    pong          = 2,
    client_input  = 10,   // cliente → servidor: intención de movimiento
    server_snapshot = 20, // servidor → cliente: estado del mundo
    spawn_entity  = 30,
    kill_entity   = 31,
    chat          = 40,
    client_hello  = 50,
    server_welcome = 51
}

#macro NET_PORT      6510
#macro NET_TICK_RATE 20         // snapshots por segundo
#macro NET_SEND_EVERY 3         // 60 fps / 20 Hz = 3 frames por snapshot
#macro NET_MAX_CLIENTS 4
```

### 5.1 `objNetManager`

```gml
// ---------------------------------------------------------------------------
// objNetManager — Create (persistente)
// ---------------------------------------------------------------------------
rol        = "ninguno";      // "servidor" | "cliente" | "ninguno"
socket     = -1;
conectado  = false;

// --- Identidad ---
mi_id      = -1;             // ID que me asigna el servidor

// --- Entidades sincronizadas ---
// clave: net_id (string) → instancia
entidades  = {};
siguiente_net_id = 1;

// --- Cliente: buffer de interpolación --------------------------------------------
// Guardamos los dos últimos snapshots para interpolar entre ellos.
snapshot_anterior = noone;
snapshot_reciente = noone;
tiempo_ultimo_snapshot = 0;

// --- Cliente: predicción -----------------------------------------------------------
secuencia_input    = 0;
historial_prediccion = [];      // [{ sec, x, y, vel_x, vel_y }]
ultima_sec_confirmada = 0;

// --- Servidor: clientes conectados ---------------------------------------------------
clientes = {};                  // socket → { id, ip, ultimo_input }

// --- Ping --------------------------------------------------------------------------
ping_enviado_en = 0;
ping_ms = 0;

// --- Chat (§5.9) ---------------------------------------------------------------------
// chat_mensaje_recibido() (más abajo) hace array_push(global.chat_log, …) — si esta
// global no existe antes del primer mensaje, revienta con "variable global no
// definida". Se crea aquí porque objNetManager es persistente y va primero: un
// mensaje puede llegar en cualquier momento de la partida.
global.chat_log = [];
```

> ⚠️ **Estos dos helpers van en un script, no en `objNetManager`.** No tocan ninguna
> variable de instancia — solo construyen y mandan un buffer con los parámetros que
> reciben — y se llaman desde varios sitios que no son `objNetManager` (más abajo, en
> distintos puntos del documento). Una `function nombre() {...}` declarada dentro de un
> evento solo la puede llamar sin cualificar la instancia donde se declaró; dejarlos aquí
> revienta en cuanto los llame otro objeto, el mismo mecanismo que
> [`04 · 19` §1](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md#1--el-conductor).

```gml
// ---------------------------------------------------------------------------
// scr_net_buffer.gml
// ---------------------------------------------------------------------------

/// @func net_buffer_nuevo(_tipo_mensaje)
/// @desc Crea un buffer de escritura con la cabecera de tipo ya puesta.
function net_buffer_nuevo(_tipo_mensaje)
{
    var _b = buffer_create(256, buffer_grow, 1);
    buffer_write(_b, buffer_u8, _tipo_mensaje);
    return _b;
}

/// @func net_enviar(_socket, _buffer)
/// @desc Envía el buffer y lo libera. Nunca dejes buffers sin liberar.
function net_enviar(_socket, _buffer)
{
    if (_socket < 0) { buffer_delete(_buffer); return false; }

    var _size = buffer_tell(_buffer);
    var _resultado = network_send_packet(_socket, _buffer, _size);

    buffer_delete(_buffer);
    return (_resultado >= 0);
}
```

### 5.2 Servidor

```gml
// ---------------------------------------------------------------------------
// scr_net_server
// ---------------------------------------------------------------------------

/// @func net_host()
/// @desc Arranca un servidor TCP en NET_PORT.
function net_host()
{
    var _nm = objNetManager;

    _nm.socket = network_create_server(network_socket_tcp, NET_PORT,
                                       NET_MAX_CLIENTS);

    if (_nm.socket < 0)
    {
        show_debug_message("ERROR: no se pudo crear el servidor");
        return false;
    }

    _nm.rol = "servidor";
    _nm.conectado = true;
    _nm.mi_id = 0;             // el servidor es el cliente 0

    show_debug_message("Servidor escuchando en el puerto " + string(NET_PORT));
    return true;
}

/// @func servidor_enviar_snapshot()
/// @desc Manda el estado completo a todos los clientes.
function servidor_enviar_snapshot()
{
    var _nm = objNetManager;
    if (_nm.rol != "servidor") return;

    var _b = net_buffer_nuevo(NetMsg.server_snapshot);

    // Timestamp del servidor (para la interpolación del cliente)
    buffer_write(_b, buffer_u32, global.frame_count);

    // --- Cuántas entidades -----------------------------------------------------------
    var _ids = variable_struct_get_names(_nm.entidades);
    buffer_write(_b, buffer_u16, array_length(_ids));

    // --- Cada entidad ------------------------------------------------------------------
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        var _clave = _ids[_i];
        var _ent = _nm.entidades[$ _clave];

        if (!instance_exists(_ent))
        {
            // Entidad muerta: lo notificamos aparte y la limpiamos
            variable_struct_remove(_nm.entidades, _clave);
            continue;
        }

        buffer_write(_b, buffer_u32, real(_clave));     // net_id
        buffer_write(_b, buffer_u8,  _ent.tipo_entidad); // tipo (para spawnear)
        buffer_write(_b, buffer_s16, round(_ent.x));
        buffer_write(_b, buffer_s16, round(_ent.y));
        buffer_write(_b, buffer_s16, round(_ent.vel_x * 100));
        buffer_write(_b, buffer_s16, round(_ent.vel_y * 100));
        buffer_write(_b, buffer_u8,  _ent.hp);
        buffer_write(_b, buffer_u8,  _ent.equipo);
    }

    // --- Enviar a todos los clientes -----------------------------------------------------
    var _sockets = variable_struct_get_names(_nm.clientes);
    for (var _i = 0; _i < array_length(_sockets); _i++)
    {
        // network_send_packet NO consume el buffer, así que podemos reenviarlo.
        // Solo hay que borrarlo una vez, al final.
        var _sock = real(_sockets[_i]);
        network_send_packet(_sock, _b, buffer_tell(_b));
    }

    buffer_delete(_b);
}
```

### 5.3 Cliente

```gml
// ---------------------------------------------------------------------------
// scr_net_client
// ---------------------------------------------------------------------------

/// @func net_join(_ip)
/// @desc Conecta a un servidor.
function net_join(_ip)
{
    var _nm = objNetManager;

    _nm.socket = network_create_socket(network_socket_tcp);

    if (_nm.socket < 0)
    {
        show_debug_message("ERROR: no se pudo crear el socket");
        return false;
    }

    var _resultado = network_connect(_nm.socket, _ip, NET_PORT);

    if (_resultado < 0)
    {
        show_debug_message("ERROR: no se pudo conectar a " + _ip);
        return false;
    }

    _nm.rol = "cliente";
    _nm.conectado = true;

    show_debug_message("Conectando a " + _ip + ":" + string(NET_PORT));
    return true;
}

/// @func cliente_enviar_input()
/// @desc Manda la intención de movimiento. Solo intenciones, nunca posición.
function cliente_enviar_input()
{
    var _nm = objNetManager;
    if (_nm.rol != "cliente" || !_nm.conectado) return;

    var _b = net_buffer_nuevo(NetMsg.client_input);

    // Número de secuencia: imprescindible para la predicción
    _nm.secuencia_input++;
    buffer_write(_b, buffer_u32, _nm.secuencia_input);

    // Intención: qué teclas pulsa. NO mandamos la posición.
    var _ix = keyboard_check(vk_right) - keyboard_check(vk_left);
    var _iy = keyboard_check(vk_down)  - keyboard_check(vk_up);

    buffer_write(_b, buffer_s8, _ix);
    buffer_write(_b, buffer_s8, _iy);
    buffer_write(_b, buffer_bool, keyboard_check(vk_space));   // disparar

    net_enviar(_nm.socket, _b);

    // --- Guardar en el historial para la reconciliación ---------------------------------
    if (instance_exists(objPlayerLocal))
    {
        array_push(_nm.historial_prediccion, {
            sec:   _nm.secuencia_input,
            x:     objPlayerLocal.x,
            y:     objPlayerLocal.y,
            vel_x: objPlayerLocal.vel_x,
            vel_y: objPlayerLocal.vel_y
        });

        // Limitar el historial
        if (array_length(_nm.historial_prediccion) > 120)
        {
            array_delete(_nm.historial_prediccion, 0, 1);
        }
    }
}
```

### 5.4 Evento asíncrono de red

El evento **Async → Networking** entrega un DS map en `async_load`. Las claves
relevantes son `type`, `id`, `ip`, `port`, `buffer`, `size`.

```gml
// ---------------------------------------------------------------------------
// objNetManager — Async: Networking
// ---------------------------------------------------------------------------
var _tipo = async_load[? "type"];

switch (_tipo)
{
    // --- Datos recibidos ---------------------------------------------------------------
    case network_type_data:
        var _buffer = async_load[? "buffer"];
        var _size   = async_load[? "size"];
        var _ip     = async_load[? "ip"];
        var _port   = async_load[? "port"];

        if (_buffer == undefined || !buffer_exists(_buffer)) break;

        // Leer el buffer COMPLETO
        buffer_seek(_buffer, buffer_seek_start, 0);

        while (buffer_tell(_buffer) < _size)
        {
            var _msg = buffer_read(_buffer, buffer_u8);

            switch (_msg)
            {
                case NetMsg.server_snapshot:
                    recibir_snapshot(_buffer);
                    break;

                case NetMsg.spawn_entity:
                    recibir_spawn(_buffer);
                    break;

                case NetMsg.kill_entity:
                    recibir_kill(_buffer);
                    break;

                case NetMsg.ping:
                    // Contestamos con un pong
                    var _b = net_buffer_nuevo(NetMsg.pong);
                    buffer_write(_b, buffer_u32, buffer_read(_buffer, buffer_u32));
                    net_enviar(socket, _b);
                    break;

                case NetMsg.pong:
                    var _enviado_en = buffer_read(_buffer, buffer_u32);
                    ping_ms = (current_time - _enviado_en);
                    break;

                case NetMsg.server_welcome:
                    mi_id = buffer_read(_buffer, buffer_u32);
                    show_debug_message("El servidor me asignó el id " +
                                       string(mi_id));
                    break;

                case NetMsg.chat:
                    var _quien = buffer_read(_buffer, buffer_u32);
                    var _texto = buffer_read(_buffer, buffer_string);
                    chat_mensaje_recibido(_quien, _texto);
                    break;

                default:
                    // Tipo desconocido: no podemos seguir leyendo porque no
                    // sabemos cuánto ocupa su payload. Salimos del bucle.
                    show_debug_message("Mensaje desconocido: " + string(_msg));
                    buffer_seek(_buffer, buffer_seek_end, 0);
            }
        }
        break;

    // --- Nuevo cliente conectado (solo servidor) --------------------------------------
    case network_type_connect:
        var _sock = async_load[? "socket"];
        var _ip   = async_load[? "ip"];

        show_debug_message("Cliente conectado: " + string(_ip));

        // Registrar
        var _nuevo_id = struct_names_count(clientes) + 1;
        clientes[$ string(_sock)] = {
            id: _nuevo_id,
            ip: _ip,
            ultimo_input_sec: 0
        };

        // Darle la bienvenida con su ID
        var _b = net_buffer_nuevo(NetMsg.server_welcome);
        buffer_write(_b, buffer_u32, _nuevo_id);
        net_enviar(_sock, _b);
        break;

    // --- Cliente desconectado (solo servidor) ------------------------------------------
    case network_type_disconnect:
        var _sock = async_load[? "socket"];

        show_debug_message("Cliente desconectado: " + string(_sock));

        if (variable_struct_exists(clientes, string(_sock)))
        {
            variable_struct_remove(clientes, string(_sock));
        }
        break;

    // --- Modo no bloqueante: la conexión terminó -----------------------------------------
    case network_type_non_blocking_connect:
        show_debug_message("Conexión establecida");
        conectado = true;
        break;
}
```

### 5.5 Recibir el snapshot e interpolar

```gml
// ---------------------------------------------------------------------------
// objNetManager — recibir_snapshot(_buffer)
// ---------------------------------------------------------------------------
function recibir_snapshot(_buffer)
{
    var _nm = objNetManager;

    var _tick = buffer_read(_buffer, buffer_u32);
    var _count = buffer_read(_buffer, buffer_u16);

    // --- Nuevo snapshot -----------------------------------------------------------------
    var _snap = { tick: _tick, entidades: {} };

    for (var _i = 0; _i < _count; _i++)
    {
        var _net_id  = buffer_read(_buffer, buffer_u32);
        var _tipo    = buffer_read(_buffer, buffer_u8);
        var _x       = buffer_read(_buffer, buffer_s16);
        var _y       = buffer_read(_buffer, buffer_s16);
        var _vel_x   = buffer_read(_buffer, buffer_s16) / 100;
        var _vel_y   = buffer_read(_buffer, buffer_s16) / 100;
        var _hp      = buffer_read(_buffer, buffer_u8);
        var _equipo  = buffer_read(_buffer, buffer_u8);

        _snap.entidades[$ string(_net_id)] = {
            tipo: _tipo, x: _x, y: _y,
            vel_x: _vel_x, vel_y: _vel_y,
            hp: _hp, equipo: _equipo
        };
    }

    // --- Rotar los snapshots para la interpolación ------------------------------------
    _nm.snapshot_anterior = _nm.snapshot_reciente;
    _nm.snapshot_reciente = _snap;
    _nm.tiempo_ultimo_snapshot = current_time;

    // Si es el primer snapshot, inicializar el anterior con él
    if (_nm.snapshot_anterior == noone) _nm.snapshot_anterior = _snap;

    // --- Aplicar a las entidades (creándolas si no existen) ----------------------------
    var _ids = variable_struct_get_names(_snap.entidades);

    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        var _clave = _ids[_i];
        var _datos = _snap.entidades[$ _clave];
        var _net_id = real(_clave);

        var _inst = variable_struct_exists(_nm.entidades, _clave)
            ? _nm.entidades[$ _clave] : noone;

        // ¿No existe todavía? Crearla.
        if (_inst == noone || !instance_exists(_inst))
        {
            _inst = instance_create_depth(_datos.x, _datos.y, -_datos.y,
                                          objNetEntity);
            _inst.net_id = _net_id;
            _inst.tipo_entidad = _datos.tipo;
            _nm.entidades[$ _clave] = _inst;
        }

        // --- ¿Es MÍA? Entonces NO la interpolo: la predicción local manda. --------------
        //    Guardo la posición del servidor para la reconciliación.
        if (_datos.equipo == _nm.mi_id)
        {
            _inst.x_servidor = _datos.x;
            _inst.y_servidor = _datos.y;
            reconciliar(_inst);
        }
        else
        {
            // --- Entidad remota: guardar destino para interpolar --------------------------
            _inst.x_anterior = _inst.x;
            _inst.y_anterior = _inst.y;
            _inst.x_objetivo = _datos.x;
            _inst.y_objetivo = _datos.y;
        }

        _inst.hp     = _datos.hp;
        _inst.equipo = _datos.equipo;
        _inst.vel_x  = _datos.vel_x;
        _inst.vel_y  = _datos.vel_y;
    }
}
```

### 5.6 Interpolación de entidades remotas

```gml
// ---------------------------------------------------------------------------
// objNetEntity — Create
// ---------------------------------------------------------------------------
net_id       = -1;
tipo_entidad = 0;
equipo       = -1;

// Interpolación
x_anterior   = x;
y_anterior   = y;
x_objetivo   = x;
y_objetivo   = y;

// Reconciliación (solo para la entidad propia)
x_servidor   = x;
y_servidor   = y;

vel_x = 0;
vel_y = 0;
hp    = 100;
```

```gml
// ---------------------------------------------------------------------------
// objNetEntity — Step
// ---------------------------------------------------------------------------
// --- Interpolar hacia el objetivo (entidades remotas) ------------------------------
if (equipo != objNetManager.mi_id)
{
    // El intervalo entre snapshots: 1000 ms / tick rate
    var _intervalo = 1000 / NET_TICK_RATE;

    // Cuánto tiempo ha pasado desde el último snapshot
    var _transcurrido = current_time - objNetManager.tiempo_ultimo_snapshot;

    // Factor de interpolación 0..1
    var _t = clamp(_transcurrido / _intervalo, 0, 1);

    x = lerp(x_anterior, x_objetivo, _t);
    y = lerp(y_anterior, y_objetivo, _t);

    // Actualizar el origen cuando llega un snapshot nuevo
    // (se hace en recibir_snapshot, aquí solo interpolamos)
}
else
{
    // --- Entidad propia: la mueve el input local (predicción) -------------------------
    //    objPlayerLocal ya la ha movido. Aquí no tocamos x/y.
}

depth = -y;
```

### 5.7 Reconciliación (corregir la predicción)

```gml
// ---------------------------------------------------------------------------
// scr_net_reconcile
// ---------------------------------------------------------------------------

/// @func reconciliar(_inst)
/// @desc Compara lo que predijo el cliente con lo que dice el servidor.
///       Si la diferencia es pequeña, la ignora. Si es grande, corrige.
function reconciliar(_inst)
{
    var _nm = objNetManager;

    var _dx = _inst.x_servidor - _inst.x;
    var _dy = _inst.y_servidor - _inst.y;
    var _distancia = point_distance(0, 0, _dx, _dy);

    // --- Umbral de tolerancia -----------------------------------------------------------
    // Sin esto, el cliente "tiembla" constantemente por errores de redondeo.
    if (_distancia < 2)
    {
        return;                      // todo bien, no hacemos nada
    }

    if (_distancia < 24)
    {
        // --- Discrepancia pequeña: corrección SUAVE -------------------------------------
        //    Teletransportar se nota muchísimo. Un lerp gradual es invisible.
        _inst.x = lerp(_inst.x, _inst.x_servidor, 0.25);
        _inst.y = lerp(_inst.y, _inst.y_servidor, 0.25);
    }
    else
    {
        // --- Discrepancia grande: teletransportar ------------------------------------------
        //    Aquí ha pasado algo gordo (colisión no predicha, empujón del
        //    servidor). Mejor un salto que un estado incoherente.
        _inst.x = _inst.x_servidor;
        _inst.y = _inst.y_servidor;

        show_debug_message("Corrección brusca: " + string(round(_distancia)) + "px");
    }
}
```

### 5.8 Bucle del servidor

```gml
// ---------------------------------------------------------------------------
// objNetManager — Step
// ---------------------------------------------------------------------------
switch (rol)
{
    case "servidor":
        // --- Enviar snapshots a la cadencia configurada --------------------------------
        if (global.frame_count mod NET_SEND_EVERY == 0)
        {
            servidor_enviar_snapshot();
        }
        break;

    case "cliente":
        if (!conectado) break;

        // --- Enviar input cada frame (o cada 2 si quieres ahorrar ancho de banda) ------
        cliente_enviar_input();

        // --- Ping cada 2 segundos ----------------------------------------------------------
        if (global.frame_count mod 120 == 0)
        {
            var _b = net_buffer_nuevo(NetMsg.ping);
            buffer_write(_b, buffer_u32, current_time);
            net_enviar(socket, _b);
        }
        break;
}
```

### 5.9 Chat

```gml
// ---------------------------------------------------------------------------
// scr_net_chat
// ---------------------------------------------------------------------------

/// @func chat_enviar(_texto)
function chat_enviar(_texto)
{
    if (_texto == "") return;

    var _b = net_buffer_nuevo(NetMsg.chat);
    buffer_write(_b, buffer_u32, objNetManager.mi_id);
    buffer_write(_b, buffer_string, _texto);
    net_enviar(objNetManager.socket, _b);
}

/// @func chat_mensaje_recibido(_quien, _texto)
function chat_mensaje_recibido(_quien, _texto)
{
    array_push(global.chat_log, {
        quien: _quien,
        texto: _texto,
        tiempo: current_time
    });

    if (array_length(global.chat_log) > 100)
    {
        array_delete(global.chat_log, 0, 1);
    }

    audio_play_sound(sndChat, 6, false);
}
```

### 5.10 Desconexión limpia

```gml
// ---------------------------------------------------------------------------
// objNetManager — Destroy / Cleanup
// ---------------------------------------------------------------------------

/// @func net_shutdown()
function net_shutdown()
{
    if (socket >= 0)
    {
        // Avisar al otro extremo si somos cliente
        if (rol == "cliente")
        {
            // (opcional) enviar un mensaje de "me voy"
        }

        network_destroy(socket);
        socket = -1;
    }

    rol = "ninguno";
    conectado = false;

    // Limpiar entidades de red
    var _ids = variable_struct_get_names(entidades);
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        var _e = entidades[$ _ids[_i]];
        if (instance_exists(_e)) instance_destroy(_e);
    }
    entidades = {};

    array_resize(historial_prediccion, 0);
    snapshot_anterior = noone;
    snapshot_reciente = noone;
}
```

---

## 6. Gestión del estado del jugador en red

```gml
// ---------------------------------------------------------------------------
// scr_net_state
// ---------------------------------------------------------------------------

/// @func NetPlayerState(_id_red)
/// @desc Estado de un jugador en la red. El servidor ES la autoridad.
function NetPlayerState(_id_red) constructor
{
    id_red     = _id_red;
    nombre     = "Jugador" + string(_id_red);
    equipo     = _id_red;
    hp         = 100;
    muertes    = 0;
    bajas      = 0;
    ping_ms    = 0;
    listo      = false;          // para el lobby

    /// @desc Reiniciar entre partidas sin desconectar.
    reset = function()
    {
        hp      = 100;
        muertes = 0;
        bajas   = 0;
    };
}

/// @func LobbyState()
/// @desc Sala de espera antes de empezar la partida.
function LobbyState() constructor
{
    jugadores = {};             // id_red → NetPlayerState
    max_jugadores = 4;
    partida_empezada = false;

    anadir = function(_id_red, _nombre)
    {
        if (struct_names_count(jugadores) >= max_jugadores) return false;

        var _p = new NetPlayerState(_id_red);
        if (_nombre != undefined) _p.nombre = _nombre;
        jugadores[$ string(_id_red)] = _p;
        return true;
    };

    quitar = function(_id_red)
    {
        var _k = string(_id_red);
        if (variable_struct_exists(jugadores, _k))
        {
            variable_struct_remove(jugadores, _k);
        }
    };

    todos_listos = function()
    {
        if (struct_names_count(jugadores) < 2) return false;

        var _ids = variable_struct_get_names(jugadores);
        for (var _i = 0; _i < array_length(_ids); _i++)
        {
            if (!jugadores[$ _ids[_i]].listo) return false;
        }
        return true;
    };

    set_listo = function(_id_red, _listo)
    {
        var _k = string(_id_red);
        if (variable_struct_exists(jugadores, _k))
        {
            jugadores[$ _k].listo = _listo;
        }
    };
}
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Enviar `id` de instancia por la red | Los IDs no coinciden entre máquinas | `net_id` asignado por el servidor |
| No liberar los buffers | Fuga de memoria brutal (cada paquete es un buffer) | `buffer_delete()` siempre, incluso en los caminos de error |
| Paquetes de más de ~1400 bytes | Fragmentación y pérdidas masivas | Divide o comprime; mantén < 1200 bytes |
| Leer el buffer sin `buffer_seek` al inicio | Lees desde donde se quedó la última escritura | `buffer_seek(_b, buffer_seek_start, 0)` antes de leer |
| Acción en tiempo real sobre TCP | Bloqueos cuando se pierde un paquete | UDP para acción; TCP para lobby y chat |
| Snapshots completos a 60 Hz | Ancho de banda disparado | 10-20 Hz es suficiente; usa deltas |
| Sin predicción del cliente | El juego se siente a cámara lenta con latencia | Predicción + reconciliación suave |
| Reconciliación sin umbral de tolerancia | El personaje tiembla constantemente | Ignora discrepancias < 2 px |
| Teletransportar en cada corrección | Saltos visibles en el movimiento | `lerp` si la discrepancia es pequeña |
| Confiar en el cliente para el daño | Trampas triviales | El servidor valida y decide |
| No manejar `network_type_disconnect` | El servidor acumula clientes fantasma | Limpia el registro en el evento async |
| Enviar floats sin escalar | 4-8 bytes por valor; paquetes enormes | Escala a enteros: `round(vel * 100)` como `s16` |
| tipo de mensaje desconocido sin salir del bucle | Desincronización total del stream | Sal del bucle de lectura si no reconoces el tipo |
| Asumir IPv6 en consolas | No funciona en Switch / PS4 / PS5 | IPv4 en consolas |

---

## 8. Cómo escalarlo

1. **Delta compression** — envía solo las entidades que cambiaron respecto al
   último snapshot confirmado por ese cliente. Requiere acuse de recibo por
   cliente.
2. **Áreas de interés** — no envíes entidades lejanas. En un mundo grande es
   la optimización que más rinde.
3. **UDP fiable NATIVO, antes de salir a por una librería de terceros** — el motor ya trae
   esto en una línea por extremo. `network_set_config()` acepta las constantes
   `network_config_enable_reliable_udp` / `network_config_disable_reliable_udp`, que activan o
   desactivan una capa de acuse de recibo y reenvío de paquetes perdidos **sobre un socket UDP
   ya creado** (verificado contra el manual oficial,
   [`Networking/network_set_config`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Networking/network_set_config.md)):

   ```gml
   // En AMBOS extremos de la conexión, antes de enviar nada por ese socket:
   network_set_config(network_config_enable_reliable_udp, socket);
   // network_set_config(network_config_disable_reliable_udp, socket);   // para desactivarlo
   ```

   Tres cosas que dice el manual y que hay que respetar:

   - **Actívalo en los DOS lados** antes de mandar datos por ese socket; lo que se envía o
     recibe antes de activarlo no se ve afectado.
   - Añade una **cabecera de 12 bytes** a cada paquete UDP (la información que GameMaker usa
     para comprobar errores y reenviar lo que falte) — cuenta con eso en el presupuesto de
     ancho de banda de §4.3.
   - **No garantiza el orden de llegada**, solo que llegue: "fiable" aquí significa
     retransmisión, no secuenciación. El snapshot de §5.2 ya resuelve el orden con su propio
     número de tick; si tu protocolo necesita orden en otro tipo de mensaje, sigue siendo cosa
     tuya. Puedes activarlo y desactivarlo varias veces sobre el mismo socket, e incluso tener
     dos sockets UDP simultáneos con configuraciones distintas.
   - No funciona en el objetivo **HTML5** (el propio manual lo dice sin rodeos, la misma
     restricción de servidor de la §4.1: no puedes crear ni configurar sockets de servidor ahí).

   Símbolos verificados: `network_set_config`, `network_config_enable_reliable_udp`,
   `network_config_disable_reliable_udp`.

   **Cuándo SÍ conviene GMS ENet (u otra librería de terceros) en su lugar:** cuando necesitas
   algo que la opción nativa no da — varios **canales** independientes por conexión (unos
   fiables y otros no, sin que un paquete perdido en uno bloquee a los demás), control de
   congestión más fino, o **interoperabilidad** con un servidor que no sea GameMaker y ya hable
   el protocolo ENet (muy común si tu backend está en C/C++, o si reusas infraestructura de
   otro motor). Para un juego GameMaker↔GameMaker sin esas necesidades,
   `network_config_enable_reliable_udp` resuelve el caso común sin sumar una dependencia
   externa que no hacía falta.
4. **Rollback completo** — solo si haces un juego de lucha o peleas 1v1 con
   mucho *timing*. Exige determinismo absoluto.
5. **Voz** — Photon ya la trae. Si lo haces tú, es otro proyecto aparte.
6. **Lobbies persistentes y *matchmaking*** — lo dan las extensiones. No lo
   escribas a mano salvo que necesites algo muy concreto.
7. **Servidor dedicado headless** — GameMaker puede compilar sin ventana
   (targets de escritorio con opciones de servidor). Consulta el manual para
   tu plataforma concreta.
8. **Replays** — graba el stream de snapshots; reprodúcelo sin red.

### Antes de empezar, en serio

El multijugador multiplica por 5 la complejidad de un proyecto. Si es tu
primer juego online:

1. Haz primero la versión **local** del juego y que funcione bien.
2. Añade **split-screen local** (dos viewports). Te obliga a separar input de
   lógica sin sufrir la red — incluido dar a cada jugador su propio esquema de teclas/botones,
   no solo su propio mando: ver
   [25 · Menú de opciones §5.8](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#58-perfiles-de-input-por-jugador-local-co-op).
3. Después añade red con autoridad del servidor.
4. Solo entonces piensa en rollback.

---

## 9. Fuentes

- **GameMaker Update Spring 2026: LTS Roadmap, GMRT, and the Future**
  (Russell Kay, 30 abr 2026) — sección *Multiplayer*, declaración oficial de la
  estrategia de extensiones —
  https://gamemaker.io/en/blog/update-spring-2026
- **Photon GameMaker Extension Release** (Patrick Roche, 14 jul 2026) —
  características, Fusion Core 3 para GMRT —
  https://gamemaker.io/en/blog/photon-extention-release
- **GMEXT-Photon** (repositorio oficial de YoYo Games) —
  https://github.com/YoYoGames/GMEXT-Photon
- **GMEXT-Steamworks** (repositorio oficial; documentación en su wiki) —
  https://github.com/YoYoGames/GMEXT-Steamworks
- Manual oficial — **Networking** (sockets TCP/UDP/WebSocket, limitaciones de
  plataforma) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Networking/Networking.htm
- Manual oficial — `network_create_server`, `network_create_socket`,
  `network_connect`, `network_send_packet`, `network_destroy` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Networking/Networking.htm
- Manual oficial — **Buffers** (`buffer_create`, `buffer_seek`,
  `buffer_write`, `buffer_read`, `buffer_tell`, `buffer_delete`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Buffers/Buffers.htm
- Manual oficial — **Async Networking event** (claves de `async_load`) —
  https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Async_Events.htm
- Comunidad: **GMS ENet** (UDP fiable, julio 2026) —
  https://forum.gamemaker.io/index.php?threads/gms-enet-enet-reliable-udp-networking-library-for-gamemaker.124136/
- Receta propia: **15 — Game feel y juice** (la predicción se nota más si el
  feedback es bueno)

---

## 10 · Salas, matchmaking y por qué tu servidor no es alcanzable

El §1.2 y [`12 · 04 — Multijugador y red`](../12%20-%20Utilidades%20e%20integraciones/04%20-%20Multijugador%20y%20red.md) §2
delegan lobbies y *matchmaking* en Photon o Colyseus y no vuelven sobre el tema. Es la
decisión correcta para producción, pero deja tres preguntas sin responder: **qué datos tiene
una sala por dentro**, **cómo emparejar jugadores antes de meterlos en una**, y **por qué
"levanto mi propio servidor en casa" no funciona aunque el código de la §5 esté perfecto**.
Esta sección responde a las tres sin depender de ninguna extensión, y cierra con las tres
salidas reales cuando decidas que sí quieres una.

### 10.1 El modelo de datos de una sala: crear, listar, unirse, expulsar

Una **sala** (*room* o *lobby*) es distinta de la partida en sí: es la sala de espera donde
los jugadores se agrupan, ven quién más hay y confirman que están listos, **antes** de que
empiece la simulación de la §3. El §6 ya define una `LobbyState` para *una* sala activa
(`jugadores`, `anadir`, `quitar`, `todos_listos`). Lo que falta para un **directorio con
varias salas simultáneas** es: un identificador listable, quién manda en la sala, si es
pública o privada, y una forma de echar a alguien que no sea "yo me borro a mí mismo".

`SalaMultijugador` **hereda** de `LobbyState` (sintaxis verificada: la misma que usa
`BasicMathsTestSuite() : TestSuite() constructor` en
[`13 · 10 — Testing y QA`](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/10%20-%20Testing%20y%20QA.md) §4.1)
para no repetir `jugadores`, `anadir`, `quitar` ni `todos_listos`:

```gml
// ═══════════ scr_salas ═══════════

/// @func SalaMultijugador(_id_sala, _nombre, _anfitrion_id, _max_jugadores)
/// @desc Una sala listable y expulsable. Amplía LobbyState (§6) con lo que hace
///       falta para un DIRECTORIO de salas, no solo la sala activa.
function SalaMultijugador(_id_sala, _nombre, _anfitrion_id, _max_jugadores) : LobbyState() constructor
{
    id_sala       = _id_sala;          // identificador estable, asignado por el servidor
    nombre        = _nombre;
    anfitrion_id  = _anfitrion_id;     // id_red del jugador con permiso de expulsar
    max_jugadores = _max_jugadores;    // sobrescribe el valor por defecto de LobbyState
    publica       = true;              // false = solo se une quien tenga el id_sala
    estado        = "esperando";       // "esperando" | "jugando"
    datos         = {};                // metadatos libres: modo, región, mmr_medio…

    /// @desc Solo el anfitrión puede expulsar, y no puede expulsarse a sí mismo.
    /// @param {Real} _quien_expulsa  id_red de quien pide la expulsión.
    /// @param {Real} _id_red_objetivo
    /// @returns {Bool}
    expulsar = function(_quien_expulsa, _id_red_objetivo)
    {
        if (_quien_expulsa != anfitrion_id)      return false;
        if (_id_red_objetivo == anfitrion_id)    return false;
        if (!variable_struct_exists(jugadores, string(_id_red_objetivo))) return false;

        quitar(_id_red_objetivo);      // heredado de LobbyState (§6)
        return true;
    };
}
```

El **directorio** vive en el proceso que hace de punto de encuentro (puede ser el mismo
`objNetManager` de §5.1 si tu juego es pequeño, o un proceso de *matchmaking* aparte si
separas "encontrar partida" de "jugar la partida"):

```gml
// ═══════════ scr_salas_directorio (en el proceso que hace de directorio) ═══════════
global.salas            = {};      // id_sala (string) → SalaMultijugador
global.siguiente_id_sala = 1;

/// @func sala_crear(_anfitrion_id, _nombre, _max_jugadores)
/// @returns {Struct} La sala recién creada, con el anfitrión ya dentro.
function sala_crear(_anfitrion_id, _nombre, _max_jugadores)
{
    var _id   = string(global.siguiente_id_sala++);
    var _sala = new SalaMultijugador(_id, _nombre, _anfitrion_id, _max_jugadores);

    _sala.anadir(_anfitrion_id, "Anfitrión");     // heredado de LobbyState
    global.salas[$ _id] = _sala;
    return _sala;
}

/// @func sala_listar()
/// @desc Salas públicas, esperando y con hueco. Lo que pintarías en un menú "Buscar partida".
/// @returns {Array<Struct>}
function sala_listar()
{
    var _resultado = [];
    var _ids = variable_struct_get_names(global.salas);

    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        var _s = global.salas[$ _ids[_i]];
        if (_s.estado != "esperando")                            continue;
        if (!_s.publica)                                         continue;
        if (struct_names_count(_s.jugadores) >= _s.max_jugadores) continue;

        array_push(_resultado, _s);
    }
    return _resultado;
}

/// @func sala_unirse(_id_sala, _id_red, _nombre)
/// @returns {Bool} false si no existe, ya empezó o está llena.
function sala_unirse(_id_sala, _id_red, _nombre)
{
    if (!variable_struct_exists(global.salas, _id_sala)) return false;

    var _s = global.salas[$ _id_sala];
    if (_s.estado != "esperando") return false;

    return _s.anadir(_id_red, _nombre);   // false si ya está llena (LobbyState.anadir, §6)
}

/// @func sala_expulsar(_id_sala, _quien_expulsa, _id_red_objetivo)
/// @returns {Bool}
function sala_expulsar(_id_sala, _quien_expulsa, _id_red_objetivo)
{
    if (!variable_struct_exists(global.salas, _id_sala)) return false;
    return global.salas[$ _id_sala].expulsar(_quien_expulsa, _id_red_objetivo);
}
```

**Por la red**, las cuatro operaciones son cuatro mensajes más en el mismo protocolo de la
§5.0. GameMaker no permite declarar `enum NetMsg` dos veces — **no es una segunda declaración,
es la primera de la §5.0 con estos seis valores añadidos**: sustituye tu `enum NetMsg` entero
por este bloque (los números de mensaje comparten un solo espacio):

```gml
// enum NetMsg completo — REEMPLAZA al de la §5.0, no lo declares dos veces.
enum NetMsg
{
    // --- de la §5.0 ---------------------------------------------------------
    ping            = 1,
    pong            = 2,
    client_input    = 10,   // cliente → servidor: intención de movimiento
    server_snapshot = 20,   // servidor → cliente: estado del mundo
    spawn_entity    = 30,
    kill_entity     = 31,
    chat            = 40,
    client_hello    = 50,
    server_welcome  = 51,
    // --- nuevo aquí: gestión de salas ---------------------------------------
    room_create        = 60,
    room_list_request  = 61,
    room_list          = 62,   // servidor → cliente: resultado de room_list_request
    room_join          = 63,
    room_join_denied   = 64,   // sala llena, ya empezada, o no existe
    room_kicked        = 65    // servidor → cliente expulsado
}
```

Solo hace falta escribir el codificador del mensaje que no es trivial — el listado, porque
va con un número variable de salas — el resto son un `net_buffer_nuevo(NetMsg.room_join)` con
un único `buffer_write(_b, buffer_u32, real(_id_sala))`, exactamente como `client_hello` en
§5.4:

```gml
/// @func sala_codificar_lista(_buffer, _salas)
/// @desc Escribe el listado de salas disponibles en un buffer ya abierto con net_buffer_nuevo().
function sala_codificar_lista(_buffer, _salas)
{
    buffer_write(_buffer, buffer_u16, array_length(_salas));

    for (var _i = 0; _i < array_length(_salas); _i++)
    {
        var _s = _salas[_i];
        buffer_write(_buffer, buffer_u32,    real(_s.id_sala));
        buffer_write(_buffer, buffer_string, _s.nombre);
        buffer_write(_buffer, buffer_u8,     struct_names_count(_s.jugadores));
        buffer_write(_buffer, buffer_u8,     _s.max_jugadores);
    }
}
```

En el cliente, `NetMsg.room_list` se lee con el mismo patrón de bucle que `server_snapshot`
en §5.4: leer el `u16` de recuento y luego esa cantidad de entradas, para rellenar la lista de
partidas del menú.

### 10.2 Matchmaking básico: por cola y por MMR

*Matchmaking* es decidir **quién entra en la misma sala** antes de que el jugador la vea. Dos
estrategias, de más simple a más justa:

| Estrategia | Cómo funciona | Cuándo usarla |
|---|---|---|
| **Por cola (FIFO)** | Los primeros N que piden partida forman una | Cooperativo, casual, pocos jugadores concurrentes |
| **Por MMR con ventana creciente** | Empareja a los más parecidos en habilidad; si nadie encaja, ensancha el margen cuanto más tiempo llevan esperando | Competitivo, cuando la diferencia de nivel arruina la partida |

La cola por MMR es un contenedor de espera + una función que intenta formar un grupo cada
vez que se llama (desde el `Step` del servidor, por ejemplo cada segundo):

```gml
// ═══════════ scr_matchmaking ═══════════

/// @func ColaMatchmaking()
/// @desc Cola de espera para emparejar por MMR. La ventana de búsqueda se ensancha con
///       el tiempo de espera del más antiguo del grupo candidato, para que nadie espere
///       eternamente por una pareja perfecta.
function ColaMatchmaking() constructor
{
    esperando = [];      // [{ id_red, mmr, desde }]

    /// @desc Mete a un jugador en la cola. Llamar una vez al pedir partida.
    entrar = function(_id_red, _mmr)
    {
        array_push(esperando, { id_red: _id_red, mmr: _mmr, desde: current_time });
    };

    /// @desc Sácalo si cancela la búsqueda.
    salir = function(_id_red)
    {
        for (var _i = array_length(esperando) - 1; _i >= 0; _i--)
        {
            if (esperando[_i].id_red == _id_red) { array_delete(esperando, _i, 1); return; }
        }
    };

    /// @func intentar_emparejar(_tamano, _ventana_base, _ventana_por_segundo)
    /// @desc Busca un grupo de _tamano jugadores cuyo rango de MMR quepa en la ventana
    ///       vigente. Si lo encuentra, lo saca de la cola y lo devuelve.
    /// @returns {Array<Struct>} El grupo emparejado, o [] si todavía no hay ninguno posible.
    intentar_emparejar = function(_tamano, _ventana_base = 100, _ventana_por_segundo = 20)
    {
        if (array_length(esperando) < _tamano) return [];

        // Ordenar por MMR: sobre una cola ordenada, el hueco más estrecho está siempre
        // entre vecinos consecutivos, así que basta una pasada.
        array_sort(esperando, function(_a, _b) { return _a.mmr - _b.mmr; });

        for (var _i = 0; _i <= array_length(esperando) - _tamano; _i++)
        {
            var _primero = esperando[_i];
            var _ultimo  = esperando[_i + _tamano - 1];

            // Cuanto más lleva esperando el más antiguo del grupo, más se ensancha el margen
            // aceptable de diferencia de MMR — así nunca se queda nadie esperando para siempre.
            var _espera_s = (current_time - _primero.desde) / 1000;
            var _ventana  = _ventana_base + _ventana_por_segundo * _espera_s;

            if ((_ultimo.mmr - _primero.mmr) <= _ventana)
            {
                var _grupo = [];
                for (var _j = _i; _j < _i + _tamano; _j++) { array_push(_grupo, esperando[_j]); }
                array_delete(esperando, _i, _tamano);
                return _grupo;
            }
        }
        return [];
    };
}
```

Con el grupo devuelto, el servidor llama a `sala_crear()` (10.1) con el primero como
anfitrión (o sin anfitrión, si tu servidor es autoritativo y no necesita uno) y a
`sala_unirse()` con el resto. La cola simple por FIFO es este mismo constructor sin el
`array_sort` ni la ventana: `intentar_emparejar` se limita a devolver los primeros `_tamano`
elementos de `esperando` en cuanto los hay.

> ⚠️ Los valores `100` y `20` de la ventana son un punto de partida razonable, no una cifra
> medida contra un juego real: ajústalos a la escala de tu propio sistema de MMR (Elo, Glicko
> o el que uses) y a cuántos jugadores concurrentes esperas tener en cola.

### 10.3 `steam_lobby_*`: no está en el runtime — es la extensión

```sh
python3 "_indice/buscar.py" --listar steam_lobby
# → 0 símbolos empiezan por «steam_lobby»
```

**No es un fallo del buscador.** Desde que las funciones de Steam salieron del corredor base
del motor, `steam_lobby_*` (y todo `steam_*`) vive **exclusivamente** en la extensión oficial
**GMEXT-Steamworks**, no en `GmlSpec.xml`. Lo confirma el propio manual espejado:

> "Todas las funciones de Steam en GameMaker han sido trasladadas fuera del corredor base y
> ahora forman parte de un extension." — [`Steam` (manual oficial)](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Steam/Steam.md)

Así que antes de escribir `steam_lobby_create(...)`, **instala GMEXT-Steamworks** — ficha en
[`07 · 03 — Extensiones oficiales y de terceros`](../07%20-%20Ecosistema/03%20-%20Extensiones%20oficiales%20y%20de%20terceros.md)
y guía de uso en
[`12 · 04 — Multijugador y red`](../12%20-%20Utilidades%20e%20integraciones/04%20-%20Multijugador%20y%20red.md) —
y da por hecho que **`buscar.py` nunca la va a encontrar**: es API de terceros, aunque la
publique YoYo Games.

Las firmas siguientes están verificadas contra la **documentación fuente de la propia
extensión**, clonada en
[`11 - Código descargado/extensiones_oficiales/GMEXT-Steamworks/docs/lobbies.js`](../11%20-%20C%C3%B3digo%20descargado/extensiones_oficiales/GMEXT-Steamworks/docs/lobbies.js),
no contra `buscar.py`:

```gml
// --- Crear y anunciar una sala pública de hasta 4 jugadores -----------------------------
steam_lobby_create(steam_lobby_type_public, 4);

// En el evento Async → Steam (NO Async → Networking: es un evento aparte):
var _tipo = async_load[? "event_type"];

switch (_tipo)
{
    case "lobby_created":
        if (async_load[? "success"])
        {
            var _id = async_load[? "lobby_id"];
            steam_lobby_set_data("modo",       "1v1");
            steam_lobby_set_data("mmr_medio",  string(mi_mmr));   // para filtrar al listar
        }
        break;

    case "lobby_joined":
        show_debug_message("Entré en la sala " + string(async_load[? "lobby_id"]));
        break;

    // Se dispara al entrar, salir, ser expulsado (8) o expulsado+baneado (16) un miembro
    case "lobby_chat_update":
        var _flags = async_load[? "change_flags"];
        if (_flags & 8) { show_debug_message("Un jugador fue expulsado de la sala"); }
        break;
}

// --- Buscar salas con un MMR parecido y unirse a la primera -----------------------------
steam_lobby_list_add_string_filter("modo", "1v1", steam_lobby_list_filter_eq);
steam_lobby_list_add_numerical_filter("mmr_medio", mi_mmr - 200, steam_lobby_list_filter_gt);
steam_lobby_list_request();

// En el Async → Steam, cuando event_type == "lobby_list":
var _n = steam_lobby_list_get_count();
if (_n > 0) { steam_lobby_list_join(0); }
```

> ⚠️ **La extensión no expone una función para expulsar directamente a un miembro** (no existe
> un `steam_lobby_kick`; se buscó en `docs/lobbies.js` completo). `change_flags & 8` en
> `lobby_chat_update` **informa** de que alguien fue expulsado, pero quien decide expulsar lo
> hace **fuera** de la API de lobbies — normalmente cerrando la conexión de ese jugador a nivel
> de tu propio transporte (§5), o pidiéndole por el chat de la sala (`steam_lobby_set_data`)
> que llame a `steam_lobby_leave()` él mismo. Si necesitas expulsión dura de verdad, usa el
> modelo de la 10.1: el servidor de tu partida es quien tiene la última palabra, la sala de
> Steam es solo el punto de encuentro.

### 10.4 NAT: por qué "monto mi propio servidor en casa" no funciona

Todo el código de la §5 asume que un cliente puede llegar a `network_create_server()` en la
otra máquina. Detrás de un router doméstico, eso casi nunca es verdad, y no es un bug de
GameMaker: es cómo funciona internet desde los años 90.

**El problema, en corto:** tu router hace **NAT** (*Network Address Translation*) — traduce
tu IP privada (`192.168.x.x`) a la única IP pública que el ISP le asignó al router. Cuando
sale una conexión (tu juego conectándose a algo), el router recuerda el camino de vuelta y
deja pasar la respuesta. Pero una conexión **entrante que nadie pidió** —como la de un amigo
intentando llegar a tu `network_create_server()`— no tiene ningún camino de vuelta que seguir,
y el router la descarta por defecto.

**"Pues abro el puerto en el router" — y a veces ni eso basta:**

- **CGNAT (*Carrier-Grade NAT*):** muchos ISPs (fibra móvil, algunos residenciales) ya no dan
  una IP pública real por hogar; meten a varios clientes detrás de la **misma** IP pública, en
  un NAT que **el proveedor** controla. Abrir puertos en tu router no sirve de nada: el NAT
  que bloquea está un salto más allá, y tú no tienes acceso a él.
- Aunque tengas IP pública propia, pedirle a cada jugador que entre al panel de su router y
  abra un puerto es, en la práctica, pedirle que no juegue.
- El **tipo de NAT** (cono completo, restringido, simétrico) determina si el *NAT traversal*
  peer-to-peer (STUN/hole punching) funciona siquiera entre dos jugadores sin servidor: con
  NAT simétrico en cualquiera de los dos lados, ni eso funciona de forma fiable.

**Las tres salidas reales**, ya presentes en esta biblioteca pero sin esta explicación:

| Solución | Cómo evita el NAT | Dónde está documentada |
|---|---|---|
| **Relay tipo Photon** | Ambos jugadores **salen** hacia la nube de Photon (una conexión saliente siempre está permitida); Photon reenvía los paquetes entre ellos. Ninguno necesita abrir un puerto | §1.2-§1.3 de este documento · [`12 · 04`](../12%20-%20Utilidades%20e%20integraciones/04%20-%20Multijugador%20y%20red.md) §1 |
| **Servidor dedicado en la nube (Colyseus u otro)** | El servidor no vive detrás de tu router: vive en un VPS con una **IP pública real**, sin NAT doméstico ni CGNAT de por medio | [`12 · 04`](../12%20-%20Utilidades%20e%20integraciones/04%20-%20Multijugador%20y%20red.md) §2 |
| **Steam Datagram Relay (`steam_net_sockets_*`)** | Los clientes se conectan por **SteamID**, no por IP:puerto; el tráfico se reenvía por la red de relés de Valve. También oculta la IP real de tus jugadores | Esta sección |

La tercera no estaba cubierta: es la propia **red de sockets** de la extensión de Steam
(distinta de `steam_lobby_*`), verificada en `docs/networking_sockets.js` del mismo
repositorio:

```gml
// --- Anfitrión: escucha conexiones P2P relayadas por la red de Valve --------------------
socket_escucha = steam_net_sockets_create_listen_socket_p2p(0);   // puerto virtual 0

// Async → Steam, event_type == "steam_net_message_on_state_change":
if (async_load[? "state"] == steam_net_connection_state_connecting)
{
    steam_net_sockets_accept_connection(async_load[? "connection"]);
}

// --- Cliente: conecta al anfitrión por su SteamID, NO por IP ----------------------------
conexion = steam_net_sockets_connect_p2p(steam_id_anfitrion, 0);

// Enviar: mismo buffer que ya usas en §5, otra API de transporte por debajo
var _b = net_buffer_nuevo(NetMsg.client_input);
steam_net_sockets_send_message(conexion, _b, buffer_tell(_b), steam_net_send_flag_reliable);
buffer_delete(_b);
```

> ⚠️ `steam_net_sockets_*` tampoco aparece en `buscar.py` por el mismo motivo que
> `steam_lobby_*` (10.3): es API de la extensión GMEXT-Steamworks, no del runtime base. Exige
> que el jugador tenga Steam abierto y una copia legítima del juego en esa cuenta — no sirve
> para un juego fuera de la plataforma Steam.

**La recomendación por defecto de esta biblioteca sigue siendo la del §1.2 y el
[`12 · 04`](../12%20-%20Utilidades%20e%20integraciones/04%20-%20Multijugador%20y%20red.md):**
usa Photon o Colyseus salvo que ya estés comprometido con Steam como única plataforma. Ninguna
de las tres exige que tu jugador entienda qué es un NAT — que es exactamente el problema que
resuelven.

### Fuentes de esta sección

Consultadas el 6 de septiembre de 2026.

- Manual oficial LTS 2026 — **Steam** (confirma el traslado de las funciones de Steam fuera
  del runtime base, hacia la extensión):
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Steam/Steam.htm>
- GMEXT-Steamworks (repositorio oficial clonado) — `docs/lobbies.js` y
  `docs/networking_sockets.js` (documentación fuente de la wiki, con firmas y ejemplos reales
  de `steam_lobby_*` y `steam_net_sockets_*`):
  `11 - Código descargado/extensiones_oficiales/GMEXT-Steamworks/docs/` ·
  <https://github.com/YoYoGames/GMEXT-Steamworks>
- Steamworks SDK — `ISteamNetworkingSockets::ConnectP2P` (Steam Datagram Relay):
  <https://partner.steamgames.com/doc/api/ISteamNetworkingSockets#ConnectP2P>
- `array_sort` (función personalizada de ordenación, patrón de la resta usado en 10.2) —
  manual oficial LTS 2026:
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Variable_Functions/array_sort.htm>
