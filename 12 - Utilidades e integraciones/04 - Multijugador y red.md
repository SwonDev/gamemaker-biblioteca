# 04 · Multijugador y red

> **2026 es el año en que el multijugador dejó de ser el punto débil de GameMaker.**
> En julio y agosto llegaron **dos frameworks profesionales completos** —Photon y Colyseus—
> con API de GML nativa. Antes de eso solo había sockets a pelo y librerías de la comunidad.
>
> Verificado el 1 de septiembre de 2026 contra el blog oficial y la API de GitHub.

---

## Resumen: qué elegir

| Si quieres… | Usa | Coste | Estado |
|---|---|---|---|
| Lo más rápido y probado, con chat y voz incluidos | **Photon** (extensión oficial) | Modelo de precios de Photon | ✅ Publicada 14-07-2026 |
| Servidor autoritativo propio, código abierto, sin dependencia de nadie | **Colyseus** | Gratis autoalojado · Colyseus Cloud opcional | 🟡 Beta desde 06-08-2026 |
| Un framework de la comunidad, todo en GameMaker + Node | **Warp** | Gratis (MIT) | ✅ Activo (2026-07-31) |
| Combate competitivo con *rollback* | **GGMR** | 💸 itch.io | ⚠️ No verificado |
| Aprender cómo funciona por debajo | Funciones nativas `network_*` + ejemplos de gmclan | Gratis | ✅ |

---

## 1. Photon — la extensión oficial ★ 🆕

**[GMEXT-Photon](https://github.com/YoYoGames/GMEXT-Photon)** ★8 · actualizada 2026-08-25
Anuncio: [*Photon GameMaker Extension Release*](https://gamemaker.io/en/blog/photon-extention-release), **14 de julio de 2026**

Photon es la plataforma de red en tiempo real que usan juegos como *Phasmophobia*, *PEAK* y
*Rogue Trader*. La extensión la trae a GameMaker de forma oficial.

**Lo que trae de serie:**

| Capacidad | Detalle |
|---|---|
| **Tiempo real** | Salas (*rooms*), *lobbies* y emparejamiento |
| **Estado sincronizado** | *Compare-and-swap* para que todos vean el mismo estado; admite cadenas o binario propio |
| **Chat de texto** | Lista de amigos, mensajes privados, presencia y múltiples canales |
| **Chat de voz** | Canales de voz en directo, silenciar por jugador, volumen, detección de habla, y control de *bitrate* y códec |
| **Diagnóstico de red** | Ping, RTT, estadísticas de tráfico, selección de región y pérdida de paquetes |

📁 Descargada en `11 - Código descargado/extensiones_oficiales/GMEXT-Photon/`
📖 Documentación completa en la wiki del propio repositorio.

> 🔮 **Dato de futuro confirmado por YoYo Games:** *Fusion Core 3* de Photon llegará a **GMRT
> como característica del núcleo**, no como extensión. Es la primera integración de red que se
> anuncia como parte del runtime nuevo. Ver
> [`02 - Novedades 2026/03 · GMRT`](../02%20-%20Novedades%202026/03%20-%20GMRT%20-%20El%20nuevo%20runtime.md).

---

## 2. Colyseus — servidor autoritativo de código abierto 🆕

Anuncio: [*Bringing Real-Time Multiplayer to GameMaker with Colyseus*](https://gamemaker.io/en/blog/colyseus-multiplayer), **6 de agosto de 2026**

Framework de código abierto construido alrededor de **salas**, con **servidor autoritativo**.
El servidor es una aplicación **Node.js + TypeScript** aparte de tu proyecto de GameMaker.

### Cómo se usa desde GML

```gml
// Create
cliente = colyseus_client_create("ws://localhost:2567");
colyseus_client_join_or_create(cliente, "mi_sala", { modo: "1v1", region: "eu" });

colyseus_on_state_change(function(_estado) { /* el estado cambió en el servidor */ });
colyseus_on_message(function(_tipo, _datos) { /* mensaje del servidor */ });

// Step
colyseus_process();   // despacha todos los eventos pendientes
```

> ⚠️ Los nombres de función anteriores están tomados **literalmente del artículo oficial**.
> Como la extensión es de terceros, **no aparecen en `GmlSpec.xml`** y por tanto
> `buscar.py` no los conoce: no es un error del buscador. Verifícalos contra el repositorio
> de Colyseus antes de escribir código.

**Encaja bien en:** cualquier juego **por sesiones** — arena, shooters, carreras, cartas,
mesa, estrategia por turnos. Un mundo persistente enorme no encaja bien; el truco habitual es
partirlo en regiones y tratar cada región como una sala.

**Plataformas:** ✅ Windows, macOS, Linux (bibliotecas nativas en C) · ✅ HTML5 y GX.games
(compilación WebAssembly del mismo núcleo) · ⏳ iOS y Android **sin probar todavía**.

**Ventajas clave sobre hacerlo a mano:**

- **Antitrampas por diseño**: el cliente envía *intenciones* («quiero moverme»), no hechos
  («estoy aquí»). El servidor decide.
- **Información oculta**: el servidor posee la baraja y solo te cuenta tu mano. Con un modelo
  cliente-anfitrión eso es muy difícil.
- **Sincronización automática**: el servidor envía **parches binarios compactos** solo de lo
  que cambió; en GML llegan como *callbacks* (`on_add`, cambio de valor, `on_remove`).
- **Reconexión automática** con cola de mensajes salientes mientras la conexión está caída.
- **Simulación de latencia** integrada para desarrollo local. Úsala: un juego que va perfecto
  en `localhost` puede sentirse muy distinto con 100 ms.

**Lo que sigue siendo tuyo:** la presentación. Interpolar o suavizar entre las actualizaciones
que llegan, y en los juegos más exigentes, predicción.

**Alojamiento:** el servidor es una aplicación Node.js normal. En desarrollo, `npm start` y
apuntas a `localhost`. En producción, cualquier VPS, Docker o nube. Autoalojarlo es
**gratuito y sin ataduras**; existe *Colyseus Cloud* como opción gestionada.

**Demos oficiales con código fuente completo:** un juego de cartas por turnos y un juego de
tanques en tiempo real. Incluyen reglas autoritativas, información oculta, bots que rellenan
huecos y jugadores caídos que vuelven sin reiniciar la partida.

> ⚠️ **Estado beta.** Colyseus está pre-1.0, así que la API puede cambiar entre versiones.
> Espera algún bug y algún cambio incompatible documentado.

---

## 3. Warp — el framework de la comunidad ★149

**[evolutionleo/Warp](https://github.com/evolutionleo/Warp)** · MIT · 2026-07-31

Framework completo de multijugador escrito en **GameMaker y Node.js**. Es la opción de la
comunidad más completa y sigue muy activa. Incluye cliente GML y servidor.

📁 `11 - Código descargado/librerias/red-y-multijugador/Warp/` (293 archivos)

---

## 4. El resto del ecosistema de red

| Librería | ★ | Qué es | Ruta local |
|---|---:|---|---|
| [**http.gml**](https://github.com/Sidorakh/http.gml) | 19 | Envoltorio HTTP: recibir peticiones GET y subir ficheros desde GML | `librerias/red-y-multijugador/http.gml` |
| [**MultiClient**](https://github.com/tabularelf/MultiClient) | 31 | **Lanza varias instancias del juego a la vez** para probar red sin dos ordenadores | `librerias/red-y-multijugador/MultiClient` |
| [**patchwire-gm**](https://github.com/gm-core/patchwire-gm) | 36 | Librería de red de gm-core, aislada | `librerias/red-y-multijugador/patchwire-gm` |
| [**GMNest**](https://github.com/TimVN/GMNest) | 2 | Extensión de **Socket.IO** para HTML5 | `librerias/red-y-multijugador/GMNest` |
| [**gm_networking**](https://github.com/gmclan-org/gm_networking) | 2 | Demostración mínima de red. Bueno para **entender** el mecanismo | `librerias/red-y-multijugador/gm_networking` |
| [**gm_boomers_networking**](https://github.com/gmclan-org/gm_boomers_networking) | 2 | Imita la API del clásico **39dll** con funciones nativas | `librerias/red-y-multijugador/gm_boomers_networking` |
| [**Nakama**](https://github.com/heroiclabs/nakama) | — | Servidor de backend **open-source y autoalojable** (Apache-2.0): autenticación, storage, chat, multijugador en tiempo real y por turnos, leaderboards, torneos. Sin cliente oficial para GameMaker (⚠️ verificado en el propio repositorio el 2026-09-07: lista clientes para Unity, Godot, Unreal, Defold, .NET, JS, Java, iOS — GML no aparece) | No descargado. Se habla con él por HTTP/WebSocket con las funciones nativas de §5, igual que con cualquier servidor propio sin cliente GML dedicado |

**De pago en itch.io / Marketplace (no descargados):**

| Producto | Autor | Precio | Qué es |
|---|---|---:|---|
| [Good GameMaker Rollback (GGMR)](https://springrollgames.itch.io/ggmr) | Spring Roll Games | 💸 | *Rollback netcode* para juegos competitivos |
| [Rocket Networking Engine](https://marketplace.gamemaker.io/assets/11424/rocket-networking-engine) | Marketplace | 💸 | Motor de multijugador de bajo código |
| [MMO Engine 2](https://bukmand.itch.io/mmo-engine-2-gamemaker) | Bukmand | $8,07 | Código fuente de un motor MMO |
| [Online Voice Chat](https://bukmand.itch.io/online-voice-chat-gamemaker) | Bukmand | $2,97 | Chat de voz |
| [EZ Networking](https://jasontomlee.itch.io/easy-gms-networking-platformer-build) | Jason Tomlee | 💸 | Anfitrión/cliente con chat |

---

## 5. Las funciones nativas siguen ahí

Antes de meter un framework, mira lo que trae el motor:

```sh
python3 "_indice/buscar.py" --listar network_
python3 "_indice/buscar.py" --listar http_
python3 "_indice/buscar.py" --listar buffer_
```

GameMaker trae sockets TCP/UDP (`network_create_socket`, `network_send_packet`…), servidor
(`network_create_server`), HTTP asíncrono y **buffers** para serializar. Para un juego de dos
jugadores en LAN eso basta y sobra.

Lee [`08 - Referencia GML completa/16 · Buffers`](../08%20-%20Referencia%20GML%20completa/16%20-%20Buffers.md)
antes de diseñar tu protocolo: si no empaquetas bien, el ancho de banda se dispara.

> ⚠️ **Un detalle que rompe un build en silencio: HTML5 no puede alojar servidor.**
> `network_create_server()` no funciona en el objetivo HTML5 (restricción del navegador, no un
> bug de GameMaker) y solo se le llega por **WebSocket** (`network_socket_ws` sin cifrar,
> `network_socket_wss` cifrado). Si tu servidor de escritorio también debe aceptar clientes
> web, necesitas **dos sockets de escucha** — uno TCP/UDP normal y otro WebSocket. Explicación
> completa, con la cita textual del manual:
> [`04 · 14 — Multijugador`](../04%20-%20Recetas%20por%20g%C3%A9nero/14%20-%20Multijugador.md) §4.1.
>
> 💡 **UDP fiable sin sumar una dependencia:** `network_set_config(network_config_enable_reliable_udp,
> socket)` activa acuse de recibo y reenvío sobre un socket UDP ya creado — actívalo en los dos
> extremos, añade 12 bytes de cabecera por paquete. Antes de meter GMS ENet solo para esto, lee
> [`04 · 14`](../04%20-%20Recetas%20por%20g%C3%A9nero/14%20-%20Multijugador.md) §8 punto 3.

---

## 6. Cómo abordarlo (orden recomendado)

1. **Lee la receta**: [`04 - Recetas por género/14 · Multijugador`](../04%20-%20Recetas%20por%20g%C3%A9nero/14%20-%20Multijugador.md).
2. **Decide la autoridad** antes de escribir nada: ¿cliente-anfitrión o servidor autoritativo?
   Cambiar de idea a mitad cuesta una reescritura.
3. **Prototipa en local** con `MultiClient` (dos ventanas) y la simulación de latencia.
4. **Elige framework**: Photon si quieres lo probado con chat y voz; Colyseus si quieres
   servidor autoritativo abierto y no depender de nadie; Warp si prefieres algo de la
   comunidad y sin coste.
5. **Prueba con latencia real desde el primer día.** Es el error nº 1: todo va bien en
   `localhost` y se rompe con 100 ms.

---

## Fuentes

- *Photon GameMaker Extension Release* (14-07-2026): <https://gamemaker.io/en/blog/photon-extention-release>
- *Bringing Real-Time Multiplayer to GameMaker with Colyseus* (06-08-2026): <https://gamemaker.io/en/blog/colyseus-multiplayer>
- GMEXT-Photon: <https://github.com/YoYoGames/GMEXT-Photon>
- awesome-gamemaker · Networking: <https://github.com/bytecauldron/awesome-gamemaker>
- Metadatos de repositorios: API de GitHub, 1 de septiembre de 2026
- Nakama (heroiclabs), README del repositorio (open-source, autoalojable, lista de clientes
  oficiales, sin GameMaker entre ellos), consultado el 7 de septiembre de 2026:
  <https://github.com/heroiclabs/nakama>
- Manual oficial LTS 2026 — `network_set_config` (UDP fiable nativo, cabecera de 12 bytes,
  activación en ambos extremos), consultado el 7 de septiembre de 2026:
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Networking/network_set_config.htm>
