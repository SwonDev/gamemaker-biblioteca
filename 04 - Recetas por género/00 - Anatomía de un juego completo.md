# 00 · Anatomía de un juego completo — de principio a fin

> **Léelo antes de empezar a desarrollar un juego entero.** Las demás recetas de esta carpeta
> resuelven un sistema cada una; este documento es el **plano**: qué escenas tiene un juego
> completo, qué sistemas globales lo sostienen, y en qué orden montarlo. Un juego no es una
> mecánica: es el arco desde que aparece el logo hasta los créditos.
>
> Para cada pieza hay un enlace a la receta que la desarrolla. Este documento no repite ese
> código: te dice **qué necesitas y cuándo**, para que no se te olvide nada.

---

## El arco completo, de un vistazo

```
  Splash / logo         →  pantalla de marca, breve, saltable
  Menú principal        →  Jugar · Continuar · Opciones · Créditos · Salir
  Intro / prólogo       →  historia, texto o VÍDEO, saltable
  ┌─ Bucle de juego ───────────────────────────────┐
  │   Zona 1 → Zona 2 → … (salas de gameplay)        │
  │   ↕ Pausa   ↕ Guardado   ↕ HUD                   │
  │   Muerte → Game Over → reintentar / menú         │
  └─────────────────────────────────────────────────┘
  Final / endgame       →  jefe final, cierre de la historia
  Créditos              →  quién lo hizo, y volver al menú
```

**Un juego "terminado" tiene las siete fases.** Un prototipo puede tener solo el bucle de
juego; un juego que se publica necesita todas. Si un LLM va a desarrollar un juego «de
principio a fin», este es el temario que no puede saltarse.

---

## 1 · Los sistemas globales — se montan PRIMERO

Antes de la primera zona, existen unos pocos objetos **persistentes** que viven toda la
partida. Se crean en una sala de arranque (`rm_init`) y nunca se destruyen.

| Sistema | Qué hace | Receta |
|---|---|---|
| **Gestor de escenas** | Cambiar de sala con transición y sin perder estado | *(§2, aquí abajo)* |
| **Guardado / carga** | Persistir progreso entre sesiones | [`scr_save_load`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml) · [14 · Persistencia](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) |
| **Localización** | Todo el texto por `txt(clave)` | [21 · Localización e idiomas](./21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md) |
| **Audio** | Música por escena, volumen, buses | [13 · Audio](../01%20-%20Fundamentos/13%20-%20Audio.md) |
| **Input** | Teclado + mando + táctil, con rebinding | [12 · Input](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md) |
| **Señales** | Que los sistemas se hablen sin acoplarse | [16 · Señales](./16%20-%20Señales%20y%20desacoplamiento.md) |

```gml
/// rm_init · un objeto obj_arranque, en su Create
// crea los persistentes en orden y salta al menú
iniciar_audio();       // función TUYA: buses y volumen guardado
idioma_cargar(idioma_preferido());
iniciar_input();
partida_cargar_ajustes();
room_goto(rm_menu);
```

> 🔺 **El orden importa:** localización antes que cualquier menú (el menú ya usa `txt()`),
> audio antes que la primera música. Un objeto persistente se marca con **Persistent** en su
> Inspector o vive en una sala que nunca se recarga.
>
> 💡 **No pongas lógica de juego en los globales.** Son fontanería: escena, guardado, idioma,
> audio, input. La lógica del jugador vive en el jugador.

---

## 2 · El gestor de escenas — el esqueleto del arco

Cada fase del arco es una **sala** (`room`). Cambiar de fase es `room_goto`, pero un juego
pulido no salta en seco: se funde a negro.

```gml
/// scr_escenas — cambio de sala con fundido
function ir_a_escena(_sala) {
    global.escena_destino = _sala;
    global.fundido = 0;
    global.fundiendo = true;      // obj_fundido hará el resto
}

/// obj_fundido · Step (persistente, encima de todo)
if (global.fundiendo) {
    global.fundido += 0.05;
    if (global.fundido >= 1) {
        room_goto(global.escena_destino);
        global.fundiendo = false;
    }
}

/// obj_fundido · Draw GUI
if (global.fundido > 0) {
    draw_set_alpha(global.fundido);
    draw_rectangle_color(0, 0, display_get_gui_width(), display_get_gui_height(),
                         c_black, c_black, c_black, c_black, false);
    draw_set_alpha(1);
}
```

> 💡 **GameMaker no tiene una función de transición entre salas** (`transition_define` no
> existe en este runtime). El fundido lo dibujas tú, y por eso lo controlas: velocidad, color,
> forma. Ver [11 · Dibujo y renderizado](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md).

---

## 3 · Splash y menú principal

**Splash:** una o dos salas cortas con tu logo. Regla única: **saltable** con cualquier tecla.
Nadie quiere ver tu logo por 47ª vez. Un `alarm` que salta solo a los 2-3 segundos, o antes si
el jugador pulsa.

**Menú principal:** la receta de menús ya resuelve la navegación.

- Estructura y scroll: [18 · Menús con scroll y navegación](./18%20-%20Menús%20con%20scroll%20y%20navegación.md)
- «Continuar» solo aparece **si hay partida guardada** (`file_exists`): es la opción
  desactivada del menú-como-datos.
- «Opciones» abre la pantalla de ajustes (volumen, idioma, controles, pantalla completa).

```gml
/// las opciones del menú, con «Continuar» condicionada
opciones = [
    { texto: txt("menu_continuar"), accion: continuar, activa: file_exists("guardado.json") },
    { texto: txt("menu_jugar"),     accion: nueva_partida, activa: true },
    { texto: txt("menu_opciones"),  accion: abrir_opciones, activa: true },
    { texto: txt("menu_creditos"),  accion: ver_creditos, activa: true },
    { texto: txt("menu_salir"),     accion: function() { game_end(); }, activa: true },
];
```

---

## 4 · Intro, prólogo y cinemáticas — incluido VÍDEO

La historia se cuenta de tres formas, y un juego suele mezclarlas:

**a) Texto tipo visual novel** — cuadros de diálogo con efecto máquina de escribir.
→ [10 · Visual Novel y narrativa](./10%20-%20Visual%20Novel%20y%20narrativa.md)

**b) Cinemática scriptada** — cámara que se mueve, personajes que entran, con
[Tweens](./15%20-%20Game%20feel%20y%20juice.md) sobre la cámara y las instancias.

**c) Vídeo pregrabado** — GameMaker reproduce archivos de vídeo:

```gml
/// obj_intro · Create — reproducir el vídeo del prólogo
video_open("prologo.mp4");     // en Included Files

/// obj_intro · Draw — dibujar el frame actual a pantalla completa
if (video_get_status() == video_status_playing) {
    var _data = video_draw();      // sin argumentos: devuelve [estado, superficie, ...]
    if (_data[0] == 0) {
        var _w = display_get_gui_width(), _h = display_get_gui_height();
        draw_surface_stretched(_data[1], 0, 0, _w, _h);
    }
}

/// obj_intro · Step — al terminar (o si pulsan saltar), al juego
if (video_get_status() == video_status_closed
 || keyboard_check_pressed(vk_anykey)) {
    video_close();
    ir_a_escena(rm_zona1);
}
```

📘 [`video_open`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Drawing/Videos/video_open.md) ·
[`video_draw`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Drawing/Videos/video_draw.md)

> ⚠️ **Toda intro, prólogo y cinemática DEBE ser saltable.** El jugador que reintenta un jefe
> no quiere ver la cinemática de entrada diez veces. Guarda un flag «ya vi esta escena» para
> saltarla automáticamente la segunda vez.
>
> 🔺 **El vídeo pesa y no se compila dentro del código**: va en Included Files, aumenta el
> tamaño del juego y **no funciona en todas las plataformas** (comprueba el soporte de
> `video_*` en tu target antes de depender de él; en HTML5 el navegador manda).

---

## 5 · El bucle de juego: zonas, HUD, pausa, guardado

Aquí vive el juego de verdad. Su forma concreta depende del género — y para eso está el resto
de esta carpeta:

| Si tu juego es… | Empieza por |
|---|---|
| Plataformas | [01 · Plataformas 2D](./01%20-%20Plataformas%202D.md) |
| Cenital / disparos | [02 · Top-Down](./02%20-%20Top-Down%20_%20Twin-Stick.md) · [03 · Shmup](./03%20-%20Shoot%20em%20up%20%28shmup%29.md) |
| RPG / aventura | [04 · RPG](./04%20-%20RPG%20_%20Action%20RPG.md) · [06 · Metroidvania](./06%20-%20Metroidvania.md) |
| Roguelike | [05 · Roguelike y generación procedural](./05%20-%20Roguelike%20y%20generación%20procedural.md) |
| Puzzle | [07 · Puzzle y Match-3](./07%20-%20Puzzle%20y%20Match-3.md) |
| Estrategia / gestión | [08 · Tower Defense](./08%20-%20Tower%20Defense.md) · [13 · Estrategia](./13%20-%20Estrategia%20y%20gestión.md) |
| Narrativo | [10 · Visual Novel](./10%20-%20Visual%20Novel%20y%20narrativa.md) |

**Lo transversal, valga cual valga el género:**

- **Zonas** = salas conectadas. Al pasar de una a otra, guarda dónde estaba el jugador para
  poder volver (Metroidvania lo detalla).
- **HUD** = vida, monedas, mapa, en el evento **Draw GUI** para que no se mueva con la cámara.
  → [UI Layers y Flexpanels](../02%20-%20Novedades%202026/04%20-%20UI%20Layers%20y%20Flexpanels.md)
- **Pausa** = `instance_deactivate_all(true)` para congelar el mundo mientras dibujas el menú
  de pausa encima. Reactivar con `instance_activate_all()`.
- **Guardado** = qué zona, posición, inventario, progreso de la historia. En puntos de guardado
  o autoguardado al cambiar de zona. → [`scr_save_load`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml)

```gml
/// pausa robusta
function pausar() {
    if (global.pausado) return;
    global.pausado = true;
    instance_deactivate_all(true);   // true = a sí mismo NO (obj_pausa sigue vivo)
    audio_pause_all();
}
function reanudar() {
    global.pausado = false;
    instance_activate_all();
    audio_resume_all();
}
```

> 🔺 **`instance_deactivate_all(true)`**: el `true` deja activa a la instancia que llama, para
> que el propio gestor de pausa siga corriendo y pueda reanudar. Sin él, congelas también al
> que tiene que descongelar.

---

## 6 · Muerte, Game Over y endgame

- **Muerte** → una sala o un estado de Game Over: «Reintentar» (recarga la zona o el último
  guardado) o «Menú». `room_restart()` reinicia la sala actual.
- **Endgame** → el jefe final y el cierre de la historia. Suele ser una zona especial más una
  cinemática de cierre (texto o vídeo, §4).
- **Créditos** → una sala con texto que sube; al acabar, `ir_a_escena(rm_menu)`. Guarda un flag
  `juego_completado` para desbloquear extras o un «New Game+».

```gml
/// créditos que suben y vuelven al menú
/// obj_creditos · Draw GUI
desplaz -= 0.5;
draw_text(display_get_gui_width() / 2, display_get_gui_height() + desplaz, global.texto_creditos);
if (desplaz < -altura_total) ir_a_escena(rm_menu);
```

---

## El checklist de "juego completo"

Un LLM que reciba «hazme un juego de X» y quiera entregarlo **entero** debería poder marcar:

- [ ] Splash saltable
- [ ] Menú principal con Jugar / Continuar (condicionado) / Opciones / Créditos / Salir
- [ ] Pantalla de opciones: volumen, idioma, controles, pantalla completa
- [ ] Intro/prólogo saltable (texto, cinemática o vídeo)
- [ ] Bucle de juego con las zonas del género
- [ ] HUD en Draw GUI
- [ ] Pausa que congela el mundo
- [ ] Guardado y carga (y «Continuar» que los usa)
- [ ] Muerte → Game Over → reintentar / menú
- [ ] Endgame: jefe/cierre final
- [ ] Créditos → vuelta al menú
- [ ] Todo el texto por `txt(clave)`, listo para traducir
- [ ] Sonido y música por escena
- [ ] Funciona con teclado **y** mando

> 💡 **El orden de construcción recomendado:** primero el bucle de juego de una zona (para
> tener algo jugable), luego el gestor de escenas y el menú, luego guardado, luego intro/endgame
> y créditos, y la localización **desde el principio** (meter `txt()` al final es rehacerlo
> todo). La [RUTA](../RUTA.md) de aprendizaje sigue esta misma progresión.

---

## Ver también

- [RUTA.md](../RUTA.md) — el itinerario de cero a experto; este documento es su nivel «juego completo»
- Todas las recetas de género de esta carpeta (01–14)
- [15 · Game feel y juice](./15%20-%20Game%20feel%20y%20juice.md) — lo que separa un juego funcional de uno que se siente bien
