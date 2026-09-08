# 05 · UI y UX de juego

> La interfaz es el único trozo de tu juego que el jugador mira **todo el rato**. Este
> documento explica cómo se diseña —jerarquía, legibilidad, feedback, taxonomía diegética— y
> cómo se implementa en GameMaker LTS 2026: el lienzo de la GUI, las anclas, las zonas
> seguras, los paneles nine-slice y los componentes clásicos (botón, barra de vida, tooltip,
> inventario, minimapa, notificaciones).
>
> **Lo que NO cubre, porque ya está resuelto en otro sitio:**
> la navegación de listas largas y el scroll → [04 · 18](../04%20-%20Recetas%20por%20género/18%20-%20Menús%20con%20scroll%20y%20navegación.md) ·
> los widgets de opciones y su persistencia → [04 · 25](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md) ·
> la accesibilidad general → [04 · 27](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) ·
> el efecto máquina de escribir → [04 · 10](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md) ·
> qué es el evento Draw GUI → [03 · 35](../03%20-%20Cursos%20%28YouTube%29/35%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Evento%20Draw%20GUI.md).

---

## 1 · Los principios

### 1.1 Jerarquía visual: tres niveles, no diez

Una HUD no es una lista de datos: es una **respuesta ordenada a tres preguntas**. Si tu
interfaz no las contesta en menos de un segundo, sobra información o falta jerarquía.

| Pregunta del jugador | Nivel | Dónde vive | Ejemplo |
|---|---|---|---|
| **¿Cómo estoy?** | Crítico, permanente | Cerca de la acción o en una esquina fija | vida, munición, tiempo |
| **¿Qué tengo?** | Contextual, aparece y se va | Junto al objeto o al borde | arma equipada, objeto recogido, buff activo |
| **¿Qué hago ahora?** | Diferido, bajo demanda | Pantalla aparte | mapa, inventario, diario, árbol de habilidades |

El ojo ordena por, en este orden: **tamaño → contraste → posición → color**. El color es el
último criterio, no el primero, y es el único que un 8 % de los hombres no puede usar
([04 · 27](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md)).

> 💡 **La prueba del entrecerrar los ojos.** Haz una captura del juego, redúcela al 25 % y
> míralas borrosa. Lo que sigue siendo distinguible es tu jerarquía real. Si a ese tamaño la
> vida y la munición pesan lo mismo, no tienes jerarquía: tienes una lista.

### 1.2 Legibilidad: el tamaño mínimo de texto no es una opinión

La distancia de visionado cambia el problema por completo. El mismo texto que en un monitor a
60 cm es cómodo, en un televisor a 3 metros no existe.

Hay una cifra oficial y conviene usarla en vez de inventarse una. Las **Xbox Accessibility
Guidelines**, en su apartado **XAG 101 «Text Display»**, lo dicen literalmente:

> *«Font size should equal or exceed: **26 px at 1080p / 52 px at 4K**»* — para consola.
> Para PC y VR bajan a **18 px a 1080p / 36 px a 4K**.

Y la medida es la **altura del cuerpo** de la letra (ascendente + altura de x + descendente),
no el «tamaño de fuente» del editor, que incluye espaciado. Además exigen que el texto pueda
escalarse **hasta el 200 %** de ese mínimo.

| Contexto | Distancia | Mínimo a 1080p | Fuente |
|---|---|---|---|
| Consola / TV («10-foot UI») | ≈ 3 m | **26 px** | Xbox Accessibility Guidelines 101 |
| Escritorio / VR | 50-70 cm | **18 px** | Xbox Accessibility Guidelines 101 |
| TV: texto principal / secundario | ≈ 3 m | **30 px / 24 px** | «Designing for TV», Microsoft (15 y 12 epx sobre 960×540) |
| TV: elemento tocable | ≈ 3 m | **64 px** de alto | Ídem (32 epx) |

La forma **robusta** de escribirlo en tu código no es en píxeles absolutos, sino como
**fracción de la altura de la GUI**, porque así sobrevive a cualquier resolución:

```
2,4 % de la altura de la GUI  →  26 px a 1080p  →  mínimo de consola
1,7 % de la altura de la GUI  →  18 px a 1080p  →  mínimo de escritorio
```

> ⚠️ **El «tamaño» que pones en el editor de fuentes no es la altura de mayúscula.** Un
> `font_add("Inter.ttf", 26, …)` no garantiza 26 px de cuerpo visible. Mide con
> `string_height("Ag")` sobre la fuente ya cargada y ajusta hasta llegar al mínimo real.

> ⚠️ **Diseña siempre para el peor caso, no para tu monitor.** Si tu juego sale en Switch o
> en Steam Deck, tu texto de 12 px «que se lee perfectamente» es ilegible. La prueba real es
> mirar la pantalla desde el sofá, o alejarte tres metros del monitor.

### 1.3 Contraste: nunca texto directamente sobre el juego

El fondo de un juego **cambia solo**. Un texto blanco perfecto sobre una cueva oscura
desaparece en la nieve del nivel siguiente. La solución no es elegir mejor el color: es
**garantizar el fondo**.

Tres capas, de peor a mejor:

1. ❌ `draw_text()` a pelo sobre el mundo.
2. 🟡 Texto con contorno o sombra proyectada (mejora, no resuelve; ver
   `font_enable_effects` en [08 · 03](../08%20-%20Referencia%20GML%20completa/03%20-%20Texto%20y%20fuentes.md)).
3. ✅ Texto sobre un **panel semitransparente oscuro** (un *scrim*). Con alfa 0,6-0,75 sobre
   negro, el contraste deja de depender de lo que haya debajo.

Como suelo de referencia sirve el criterio de la web (WCAG 2.2): **4,5:1** para texto normal
y **3:1** para texto grande. Un juego no está obligado a cumplirlo, pero un texto por debajo
de 3:1 es directamente ilegible para mucha gente.

### 1.4 Consistencia: el jugador aprende una vez

- **El mismo botón hace lo mismo en todas las pantallas.** Aceptar es siempre el mismo botón;
  cancelar/volver, siempre el mismo. Si en el menú se acepta con A y en la tienda con X, has
  roto el contrato.
- **La posición no baila.** Si «Volver» está abajo a la izquierda, está abajo a la izquierda
  en las nueve pantallas.
- **El vocabulario no baila.** «Objetos», «Inventario» y «Mochila» son tres palabras para lo
  mismo: elige una y repítela hasta en los tutoriales.

> 🔺 **Ojo con la convención de plataforma.** En GameMaker `gp_face1` es siempre el botón
> **inferior** del rombo, `gp_face2` el derecho. En Xbox y PlayStation eso es «aceptar» y
> «cancelar»; en Nintendo la disposición física de las letras está invertida respecto a Xbox,
> así que si dibujas la letra en pantalla debes decidirla por plataforma, no por constante
> (§2.3). Ver [01 · 12](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md).

### 1.5 Feedback inmediato: un control tiene cuatro estados, no dos

Este es el fallo más repetido en juegos de un solo desarrollador: el botón solo tiene
«normal» y «pulsado».

| Estado | Cuándo | Qué debe comunicar | Sonido |
|---|---|---|---|
| **Normal** | En reposo | «esto se puede tocar» | — |
| **Foco / hover** | El cursor encima **o** el foco de mando encima | «si aceptas ahora, es esto» | sonido corto, solo al **entrar** |
| **Pulsado** | Mientras se mantiene | «te he oído» | sonido de confirmación |
| **Inactivo** | No se puede usar ahora | «existe, pero no ahora» — y **por qué** | sonido de error si insisten |

Dos reglas que no son negociables:

- **Un botón inactivo se dibuja, no se esconde.** Si desaparece, el jugador cree que se le ha
  roto el juego; si está gris, entiende que hay una condición. Y si lo pulsa, dale un motivo
  («Necesitas 3 llaves»), no un silencio.
- **El sonido de foco se dispara en el cambio de estado, no cada frame.** Si lo pones en el
  `if (encima)` sin comparar con el estado anterior, obtienes una metralleta.

La latencia también es feedback: por debajo de **100 ms** una respuesta se percibe como
instantánea. Un botón que se anima 300 ms antes de reaccionar se siente roto aunque sea
precioso.

### 1.5 bis El mismo principio, en el mundo: acción rechazada

§1.5 lo resuelve para un botón de menú. La misma regla — **toda entrada rechazada responde en
≤1 frame, con un motivo, nunca con silencio** — se aplica igual FUERA de los menús, y hoy solo
existe como ejemplos sueltos que nadie ha juntado:

- La puerta cerrada que se sacude sin decir el motivo, en
  [04 · 06 — Metroidvania](../04%20-%20Recetas%20por%20género/06%20-%20Metroidvania.md) («Feedback:
  la puerta se sacude»).
- El icono de habilidad que baja a alfa 0,6 durante el enfriamiento, en
  [04 · 36 §3.3-3.4](../04%20-%20Recetas%20por%20género/36%20-%20Habilidades%2C%20enfriamientos%20y%20recursos%20de%20combate.md).
- El botón inactivo de §1.5, con sus cuatro estados y su motivo visible.

Los tres resuelven el MISMO problema en tres sitios distintos, sin una pieza compartida. Aquí
está esa pieza — el equivalente de «botón inactivo» para el mundo, no el menú:

```gml
/// @func accion_rechazada(_x, _y, _motivo)
/// @desc Dispara en el punto donde el jugador intentó algo que no pudo: reutiliza
///       fx_floating_text (04 · 15 §5.6) para el motivo y un sonido corto de "denegado".
///       _motivo puede ser "" cuando el propio choque físico ya lo dice todo.
function accion_rechazada(_x, _y, _motivo)
{
    if (_motivo != "") fx_floating_text(_x, _y, _motivo, c_ltgray);
    audio_play_sound(snd_denegado, 5, false);
}
```

```gml
// obj_jugador — al intentar lanzar una habilidad que sigue en enfriamiento (04 · 36 §3.3:
// mismos campos que ya usa slot_habilidad_dibujar() para el alfa 0,6 del icono)
var _clave = "bola_fuego";
var _listo = (habilidades.enfriamiento[$ _clave] <= 0) && (habilidades.cargas[$ _clave] > 0);
if (!_listo)
{
    accion_rechazada(x, y - 20, txt("en_enfriamiento"));
    exit;
}
```

```gml
// obj_jugador — al chocar con un muro invisible que sella una zona (obj_muro_invisible
// de 04 · 47 §5, o el límite de un traversal de 04 · 37)
if (place_meeting(x + hspeed, y, obj_muro_invisible))
{
    accion_rechazada(x, y, "");   // sin texto: el choque ya dice "por aquí no"
    camera_shake(0.05);           // sacudida sutil — no la del golpe de combate de 04 · 15 §5.1
}
```

> 💡 **No es una receta nueva por sistema — es una función de una línea que faltaba juntar.**
> Cada acción bloqueada del juego (habilidad en enfriamiento, puerta sin llave, muro invisible,
> objeto que no se puede coger) gana el mismo tratamiento con la misma llamada, en vez de que
> cada sistema invente su propio silencio o su propio parche.

### 1.6 Affordance: la forma dice el uso

Un elemento tiene *affordance* cuando su aspecto sugiere lo que se puede hacer con él. En un
juego eso significa:

- Lo pulsable tiene **relieve, borde o fondo**; lo que no lo tiene, no se toca.
- Lo arrastrable tiene **agarre visual** (una textura de rejilla, una sombra que lo despega
  del fondo).
- Un icono solo se entiende sin etiqueta si es **convención universal** (⏸ pausa, ⚙ ajustes,
  🔊 sonido). Todo lo demás lleva texto, o lo lleva al menos la primera vez.
- **El foco de mando necesita su propia affordance**: no basta con cambiar el color del texto.
  Un recuadro, una flecha o un panel que crece se ven desde el sofá; un blanco un poco más
  blanco, no.

### 1.7 Carga cognitiva: cuenta los elementos, no los píxeles

Cada elemento simultáneo compite por la atención. El coste no está en el espacio que ocupa,
sino en **cuántas decisiones obliga a tomar a la vez**.

- **Revelación progresiva.** El primer nivel no enseña el árbol de habilidades. Un elemento
  de HUD aparece cuando aparece la mecánica que lo usa, no antes. Celia Hodent, que fue
  directora de UX en Epic, lo resume en una cifra en su charla *The Gamer's Brain* (GDC): la
  memoria de trabajo aguanta **unos 3 elementos** a la vez, así que un tutorial que introduce
  más de tres cosas seguidas no está enseñando, está borrando.
- **Oculta lo que está lleno.** Una barra de resistencia al 100 % no informa de nada: puede
  desvanecerse y volver en cuanto baje. Ganas pantalla y ganas dramatismo.
- **Agrupa por proximidad.** Todo lo del jugador junto; todo lo del enemigo, junto y lejos.
  Dos grupos separados se leen más rápido que ocho elementos repartidos.
- **Un número o una barra, no los dos.** «87/120» y una barra dicen lo mismo. Elige según lo
  que el jugador necesita: la barra para *sensación*, el número para *cálculo*.

### 1.8 La HUD es game feel

La HUD no es un visor pasivo: es **donde se siente el daño**. Los mismos principios de
[04 · 15](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) aplican a la
interfaz:

- Una barra de vida que baja de golpe informa. Una que baja de golpe **y deja detrás un
  rastro rojo que se retrasa** (§3.5b) duele.
- Un contador que salta de 100 a 350 informa. Uno que **cuenta hacia arriba y tiembla** en el
  último dígito celebra.
- El icono del arma que **se sacude** al recargar hace que la recarga se sienta física.

Regla de reparto: **el mundo dice qué pasa, la HUD dice cuánto importa.** Si el efecto lo ves
en el mundo (el enemigo parpadea, sale sangre), la HUD no necesita repetirlo entero: le basta
con acusar el golpe.

### 1.9 La taxonomía diegética: dos preguntas, seis categorías

La clasificación que usa el oficio viene de la tesis de máster **«Beyond the HUD — User
Interfaces for Increased Player Immersion in FPS Games»** (Erik Fagerholt y Magnus Lorentzon,
Chalmers University of Technology, 2009, en colaboración con EA DICE). Su aportación es que
un elemento de interfaz se sitúa respondiendo a **dos preguntas independientes**:

1. **Ficción (*diegesis*)**: ¿el elemento existe dentro del relato? ¿El personaje sabe que
   está ahí?
2. **Espacio (*spatiality*)**: literalmente, *«does the UI element exist within the 3D game
   space or not?»* — ¿está en la geometría del mundo o pegado a la cámara?

> ⚠️ **La versión de «cuatro cuadrantes» que circula por internet es una simplificación
> posterior, no lo que dice la tesis.** El texto original llega a **seis categorías**, porque
> los autores encontraron zonas grises (la sangre en la pantalla de *Killzone 2*, la «Runner
> Vision» de *Mirror's Edge*) que no caben en cuatro casillas. Si citas la tesis, cita las
> seis; si usas las cuatro, di que es una simplificación.

| Categoría original | Ficción | Espacio | Qué es | Ejemplos de la tesis |
|---|---|---|---|---|
| **Non-diegetic** (HUD) | ❌ | ❌ | La HUD clásica: barra de vida, munición, minimapa | Casi cualquier FPS |
| **Meta-perception** | ✅ | ❌ | Lo que el personaje *percibe*, dibujado sobre la pantalla | La sangre en pantalla como salud (*Killzone 2*) |
| **Meta-representation** | ✅ | ❌ | Un objeto de la ficción representado como *overlay* | El móvil del avatar (*GTA IV*) |
| **Geometric** | ❌ | ✅ | En el espacio del juego, pero el personaje no lo ve | Siluetas a través de paredes (*Left 4 Dead*), Runner Vision (*Mirror's Edge*), briefings proyectados (*Splinter Cell: Conviction*) |
| **Diegetic** | ✅ | ✅ | Parte del mundo y del relato | *Dead Space*, *Far Cry 2*, *Metroid Prime 3* |
| **Signifiers** | ✅ | ✅ | Subcategoría diegética: pistas del propio mundo, sin widget | Humo de las armas dañadas (*Call of Juarez*), rastros de sangre direccionales (*Dead Space*) |

La **simplificación popular** mapea así: *no diegética* = Non-diegetic · *meta* = las dos
categorías meta · *espacial* = Geometric · *diegética* = Diegetic + Signifiers.

Para qué sirve saberlo:

- **Diegética**: máxima inmersión, mínima legibilidad, y cara de producir. Para lo que se
  **consulta**, no para lo que se **vigila**.
- **Geométrica / espacial**: la más infravalorada. Un contorno sobre el objetivo elimina un
  marcador de la esquina.
- **Meta**: la más barata en juice. Un efecto de pantalla comunica estado sin añadir un widget.
- **No diegética**: la que se lee más rápido. No es «peor»: es la correcta para lo crítico.
- **Signifiers**: gratis y casi nadie la usa. Que el mundo cuente el estado (un arma que humea,
  un motor que chirría) ahorra un icono entero.

> 💡 **En 2D la taxonomía funciona igual.** «Dentro del espacio» es el evento **Draw** (se
> mueve con la cámara); «fuera del espacio» es el evento **Draw GUI**. La decisión de en qué
> evento dibujas un elemento **es** la decisión de en qué categoría lo pones.

### 1.10 Cuándo ocultar la HUD

Ocultar no es esconder información: es **quitarla cuando ya no informa**.

| Situación | Qué hacer |
|---|---|
| Cinemática, transición, pantalla de carga | HUD fuera, entera y con un fundido corto |
| Un recurso está al máximo y estable | Desvanecer ese elemento; volver al instante en que cambie |
| Modo foto / modo exploración sin amenazas | HUD fuera con una tecla, y decirlo la primera vez |
| El jugador lleva 20 h y ya se sabe los controles | Recordatorios de botones fuera; el resto se queda |
| **Combate, salto de precisión, decisión con coste** | **Nunca.** Aquí no se oculta nada |

Dos avisos:

- **Un elemento que aparece y desaparece llama más la atención que uno fijo.** Si la barra de
  vida solo aparece al recibir daño, su aparición es en sí un aviso — eso puede ser
  deliberado y bueno, o un susto constante si tu juego hace daño cada dos segundos.
- **Si ocultas la HUD, el jugador tiene que poder recuperarla.** Un ajuste en Opciones
  («HUD: completa / mínima / oculta») y no un secreto.

---

## 2 · El método: del mapa de pantallas al layout

### 2.1 El mapa de pantallas se dibuja antes de programar nada

```
                       ┌──────────┐
                       │  SPLASH  │   saltable con cualquier tecla, 2-3 s máximo
                       └────┬─────┘
                            ▼
   ┌────────────┐     ┌─────────────────┐     ┌──────────────┐
   │ CONTROLES  │◀───▶│    OPCIONES     │◀───▶│ MENÚ PRINCIP.│
   │ (rebinding)│     │ (UNA sola, para │     │              │
   └────────────┘     │  menú y pausa)  │     └──────┬───────┘
                      └────────▲────────┘            │ Jugar
                               │                     ▼
                               │        ┌──────────────────────────────┐
                               │        │            JUEGO             │
                               │        │ HUD · diálogos · avisos      │
                               │        └───┬──────────────────────┬───┘
                               │            │ Pausa                │ Fin de partida
                               │            ▼                      ▼
                               │     ┌───────────────┐      ┌──────────────┐
                               └─────┤     PAUSA     │      │  RESULTADOS  │
                                     │ · Reanudar ───┼──▶ JUEGO            │
                                     │ · Opciones    │      └──────┬───────┘
                                     │ · Salir (con  │             │
                                     │   confirmar) ─┼──▶ MENÚ ◀───┘
                                     └───────────────┘
```

Cuatro reglas que se ven en el dibujo y no en el código:

1. **Opciones es una sola pantalla**, abierta desde dos sitios. Si la duplicas, la segunda se
   queda desactualizada. Guarda de dónde vienes y vuelve ahí.
2. **Toda pantalla tiene una salida visible** y siempre el mismo botón. Una pantalla sin
   salida clara es un cuelgue percibido.
3. **Toda acción destructiva pide confirmación** (salir sin guardar, borrar partida,
   restablecer controles) y el botón por defecto de esa confirmación es **«No»**.
4. **Pausa congela el mundo**, no lo dibuja aparte. La receta está en
   [04 · 00 §5](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md)
   (`instance_deactivate_all(true)`).

### 2.2 Navegación con mando y teclado: foco, orden, envolvente y repetición

La navegación de una **lista** con scroll ya está resuelta en
[04 · 18](../04%20-%20Recetas%20por%20género/18%20-%20Menús%20con%20scroll%20y%20navegación.md). Aquí
va lo que aquella receta no cubre y lo que más se rompe: **el foco como concepto**, la
**cuadrícula** y la **repetición de input**.

**Las cinco leyes del foco**

1. **Siempre hay exactamente uno.** Al abrir una pantalla, algo tiene el foco antes del primer
   frame. Nunca se entra en una pantalla «sin nada seleccionado».
2. **El foco se ve sin ratón.** Un recuadro, una flecha, un panel que crece. No un color un
   poco distinto.
3. **El orden lo defines tú.** Nunca lo derives del orden de creación de instancias ni del
   orden de un `ds_map`: escribe el array.
4. **Si el elemento con foco se desactiva, el foco se mueve.** Si no, el jugador pulsa
   aceptar y no pasa nada.
5. **Al volver de una subpantalla, el foco vuelve donde estaba.** Guarda el índice al salir.

**Envolvente (*wrap*): sí en listas, no en valores**

| Elemento | ¿Envuelve? | Por qué |
|---|---|---|
| Lista vertical corta (≤ 8) | ✅ Sí | Llegar a «Salir» desde arriba es un solo golpe |
| Lista larga con scroll | ❌ No | Envolver 60 filas desorienta; el tope avisa de que es el final |
| Slider (volumen, brillo) | ❌ **Nunca** | Pasar de 100 % a 0 % de un toque es un desastre |
| Cuadrícula (inventario) | ⚠️ Solo en el eje horizontal, y solo si las filas están completas | Envolver en vertical salta de la primera a la última fila |

**Repetición de input: dos números y ya**

Si el jugador mantiene abajo, la selección debe repetir — pero no a 60 pasos por segundo.
Todo el mundo usa la misma pareja de valores: **retardo inicial ≈ 0,4 s**, **repetición ≈
0,1 s**.

```gml
// scr_ui_navegacion  —  repetición de input independiente de los fps
// Verificado: delta_time, keyboard_check, gamepad_button_check, gamepad_axis_value

/// @func repeticion_nueva()
/// @desc Estado de una dirección que se puede mantener pulsada.
/// @returns {Struct}
function repeticion_nueva() {
    return { activa: false, espera: 0 };
}

/// @func repeticion_paso(_estado, _pulsando)
/// @desc Devuelve true en el frame en que hay que dar UN paso de navegación.
///       Dispara al pulsar, espera 0,4 s y luego repite cada 0,1 s.
/// @param  {Struct} _estado    Un struct de repeticion_nueva()
/// @param  {Bool}   _pulsando  Si la dirección está mantenida AHORA
/// @returns {Bool}
function repeticion_paso(_estado, _pulsando) {
    static RETARDO    = 0.40;   // segundos hasta la primera repetición
    static INTERVALO  = 0.10;   // segundos entre repeticiones

    if (!_pulsando) {
        _estado.activa = false;
        _estado.espera = 0;
        return false;
    }

    if (!_estado.activa) {              // primer frame: paso inmediato
        _estado.activa = true;
        _estado.espera = RETARDO;
        return true;
    }

    _estado.espera -= delta_time / 1000000;   // delta_time viene en microsegundos
    if (_estado.espera <= 0) {
        _estado.espera += INTERVALO;
        return true;
    }
    return false;
}
```

```gml
/// obj_ui · Create — un estado por dirección
rep_arriba = repeticion_nueva();
rep_abajo  = repeticion_nueva();

/// obj_ui · Step
var _zm = 0.5;   // zona muerta del stick, más alta que la de moverse por el mundo
var _arr = keyboard_check(vk_up)   || gamepad_button_check(0, gp_padu)
        || gamepad_axis_value(0, gp_axislv) < -_zm;
var _aba = keyboard_check(vk_down) || gamepad_button_check(0, gp_padd)
        || gamepad_axis_value(0, gp_axislv) >  _zm;

// menu_mover() salta las opciones desactivadas y está en 04 · 18; no lo repetimos aquí
if (repeticion_paso(rep_arriba, _arr)) foco = menu_mover(elementos, foco, -1);
if (repeticion_paso(rep_abajo,  _aba)) foco = menu_mover(elementos, foco,  1);
```

> 🔺 **El stick analógico tiene que pasar por la zona muerta.** Sin `_zm`, un mando con
> desgaste navega solo por el menú. `gamepad_set_axis_deadzone(0, 0.25)` fija una zona muerta
> global, pero para navegación conviene un umbral **más alto** (0,5) que para moverse por el
> mundo: te da un gesto deliberado en lugar de un roce.

**Cuadrícula: mover en dos ejes sin salirse**

```gml
/// @func foco_rejilla(_indice, _dx, _dy, _columnas, _total, _envolver_x)
/// @desc Mueve un índice lineal por una rejilla de _columnas columnas.
/// @returns {Real} El índice nuevo (nunca fuera de rango)
function foco_rejilla(_indice, _dx, _dy, _columnas, _total, _envolver_x = true) {
    var _filas = ceil(_total / _columnas);
    var _col   = _indice mod _columnas;
    var _fila  = _indice div _columnas;

    _col += _dx;
    if (_envolver_x) _col = (_col + _columnas) mod _columnas;
    else             _col = clamp(_col, 0, _columnas - 1);

    _fila = clamp(_fila + _dy, 0, _filas - 1);     // vertical NUNCA envuelve

    var _nuevo = _fila * _columnas + _col;
    if (_nuevo >= _total) _nuevo = _total - 1;     // última fila incompleta
    return _nuevo;
}
```

> 💡 **`div` es la división entera de GML**, y `mod` el resto. `_indice div _columnas` da la
> fila; `_indice mod _columnas`, la columna. Es la conversión índice ↔ celda que vas a repetir
> en el inventario (§3.5e) y en el mapa.

> 💡 **Teclas de acceso rápido (mnemonics) en menús con pestañas.** Además de la navegación por
> flechas de arriba, un menú con varias pestañas —el propio ejemplo de
> [04 · 25 §5.4](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md#54-perfiles-teclado--mando-1--mando-2),
> que ya cambia de pestaña con Q/E y hombro izquierdo/derecho— puede añadir un **salto directo**
> por letra: pulsar la inicial subrayada de una pestaña o de una opción del menú principal la
> selecciona sin recorrer las intermedias. No es una segunda forma de navegar, es un atajo
> **encima** de la que ya existe:
>
> ```gml
> // obj_opciones · Step — atajo directo, además de Q/E; NO sustituye la navegación por flechas
> if (keyboard_check_pressed(ord("C"))) perfil_activo = "controles";   // pestaña "Controles"
> if (keyboard_check_pressed(ord("V"))) perfil_activo = "video";       // pestaña "Vídeo"
> if (keyboard_check_pressed(ord("A"))) perfil_activo = "audio";       // pestaña "Audio"
> ```
>
> Dibuja la letra subrayada (o en otro color) dentro de la etiqueta de la pestaña, para que el
> atajo sea descubrible sin tener que probarlo a ciegas. Dos límites reales: no hay forma de
> pedirle esto a un **mando** (los mnemonics son un patrón de teclado, el mando ya tiene su
> propio atajo de hombros) y dos pestañas que empiecen por la misma letra no pueden compartir
> tecla — resuélvelo con la inicial de una palabra distinta del rótulo si hace falta.

### 2.3 Ratón, táctil y mando a la vez: manda el último dispositivo usado

Un juego de PC moderno se maneja con las tres cosas, a veces en la misma partida. La regla
que usan todos los juegos que lo hacen bien:

> **El último dispositivo que el jugador tocó decide qué iconos se dibujan y si hay cursor.**
> No hay un ajuste de «modo mando»: el juego se da cuenta solo.

```gml
// scr_ui_dispositivo  —  detección del último dispositivo usado
// Verificado: keyboard_check_pressed, mouse_check_button_pressed, window_mouse_get_x,
//             gamepad_is_connected, gamepad_button_check_pressed, gamepad_axis_value,
//             gamepad_get_description, string_pos, string_lower, window_set_cursor

/// @func dispositivo_iniciar()
/// @desc Llamar UNA vez, en el Create del controlador persistente.
function dispositivo_iniciar() {
    global.ui_dispositivo = "teclado";   // "teclado" | "raton" | "mando"
    global.ui_marca_mando = "generico";  // "xbox" | "playstation" | "nintendo" | "generico"
    global.__ui_raton_ant = [window_mouse_get_x(), window_mouse_get_y()];
}

/// @func dispositivo_actualizar()
/// @desc Llamar cada Step. Cambia global.ui_dispositivo cuando el jugador cambia de mando.
function dispositivo_actualizar() {
    // --- ratón: solo cuenta si se MUEVE de verdad o se hace clic ---
    var _mx = window_mouse_get_x();
    var _my = window_mouse_get_y();
    var _movido = point_distance(_mx, _my,
                                 global.__ui_raton_ant[0], global.__ui_raton_ant[1]) > 4;
    global.__ui_raton_ant = [_mx, _my];

    if (_movido || mouse_check_button_pressed(mb_any)) {
        global.ui_dispositivo = "raton";
    }
    else if (keyboard_check_pressed(vk_anykey)) {
        global.ui_dispositivo = "teclado";
    }
    else if (gamepad_is_connected(0) && __ui_mando_activo(0)) {
        global.ui_dispositivo = "mando";
        global.ui_marca_mando = marca_de_mando(0);
    }

    // el cursor del sistema solo existe cuando el ratón manda
    window_set_cursor(global.ui_dispositivo == "raton" ? cr_default : cr_none);
}

/// @func __ui_mando_activo(_slot)  — ¿ha tocado el mando este frame? Uso interno.
function __ui_mando_activo(_slot) {
    static BOTONES = [gp_face1, gp_face2, gp_face3, gp_face4, gp_padu, gp_padd, gp_padl,
                      gp_padr, gp_shoulderl, gp_shoulderr, gp_shoulderlb, gp_shoulderrb,
                      gp_start, gp_select, gp_stickl, gp_stickr];

    for (var _i = 0; _i < array_length(BOTONES); _i++) {
        if (gamepad_button_check_pressed(_slot, BOTONES[_i])) return true;
    }
    return abs(gamepad_axis_value(_slot, gp_axislh)) > 0.5      // los sticks también cuentan
        || abs(gamepad_axis_value(_slot, gp_axislv)) > 0.5;
}

/// @func marca_de_mando(_slot)
/// @desc Familia del mando a partir de su nombre, para dibujar la letra correcta.
/// @returns {String} "xbox" | "playstation" | "nintendo" | "generico"
function marca_de_mando(_slot) {
    static FAMILIAS = [
        ["xbox",        ["xbox", "xinput"]],
        ["playstation", ["dualsense", "dualshock", "playstation", "wireless controller"]],
        ["nintendo",    ["nintendo", "switch", "joy-con", "pro controller"]],
    ];
    var _nombre = string_lower(gamepad_get_description(_slot));

    for (var _f = 0; _f < array_length(FAMILIAS); _f++) {
        var _claves = FAMILIAS[_f][1];
        for (var _c = 0; _c < array_length(_claves); _c++) {
            if (string_pos(_claves[_c], _nombre) > 0) return FAMILIAS[_f][0];
        }
    }
    return "generico";
}

/// @func icono_boton(_accion)  — sprite del icono según el dispositivo actual.
function icono_boton(_accion) {
    if (global.ui_dispositivo != "mando") return spr_iconos_teclado;
    switch (global.ui_marca_mando) {
        case "playstation": return spr_iconos_playstation;
        case "nintendo":    return spr_iconos_nintendo;
        default:            return spr_iconos_xbox;
    }
}
```

> ⚠️ **`marca_de_mando()` es una heurística, no una API.** GameMaker no expone la familia del
> mando: `gamepad_get_description()` devuelve la cadena que reporta el driver, y esa cadena
> varía entre Windows, Linux y macOS para el mismo mando físico. Comprueba los nombres reales
> con `show_debug_message(gamepad_get_description(0))` en cada plataforma antes de fiarte, y
> deja siempre un fallback genérico. Si necesitas esto en serio, la librería **Input** de
> JujuAdams ya mantiene esa base de datos por ti:
> [10 · 10](../10%20-%20Cursos%20en%20español/10%20-%20Herramientas%20de%20la%20comunidad%20-%20Input%20y%20Scribble.md)
> y [01 · 12 §7](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md).

**Táctil**: en móvil no existe hover, así que un botón solo tiene tres estados útiles
(normal, pulsado, inactivo) y **el área tocable tiene que ser mayor que el dibujo**. La regla
de oro es ≈ 9 mm de lado, que a 1080p en un móvil típico son unos 90-100 px de GUI. Ver los
gestos en [01 · 12 §8bis](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md).

---

## 3 · Cómo se traduce a GameMaker

### 3.1 Draw GUI a mano o UI Layers: la decisión

GameMaker LTS 2026 tiene dos caminos para la interfaz. No son equivalentes y **la elección se
toma una vez, al principio del proyecto**.

| | **Draw GUI a mano** | **UI Layers + Flexpanels** |
|---|---|---|
| Dónde se define | En código, en el evento Draw GUI | En el **Room Editor**, visualmente |
| Layout | Lo calculas tú (anclas, §3.2) | Flexbox (librería Yoga): `flex`, `gap`, `padding`, `justify` |
| Responsive | Tan bueno como tus anclas | Automático por diseño |
| Iteración visual | Compilar para ver un cambio | Se ve en el editor al momento |
| Alcance | Cualquier cosa que sepas dibujar | Sprites, objetos, secuencias y texto colocados en paneles |
| Coordenadas del ratón | `device_mouse_x_to_gui(0)` | La instancia ya vive en espacio GUI: `mouse_x`/`bbox_*` valen |
| Efectos raros (shaders, surfaces, primitivas) | ✅ Todo | ⚠️ Solo lo que quepa en un asset |
| Depurar por qué algo está donde está | Lees tu código | Depende del cálculo de Yoga |
| Rooms | Lo dibujas donde quieras | Las UI layers son **globales a todo el proyecto** |
| Madurez | Existe desde siempre, no va a cambiar | Sistema nuevo de 2026, todavía moviéndose |

**Cómo decidir, sin ambigüedad:**

- **HUD sencillo, juego de píxel, resolución fija, un desarrollador** → **Draw GUI a mano**.
  Menos partes móviles, control total, y todo lo de este documento aplica directamente.
- **Menús y pantallas con muchos elementos, varias resoluciones, alguien que no programa
  tocando el diseño** → **UI Layers**. El editor visual se paga solo.
- **Mezcla los dos sin miedo.** Nada impide tener los menús en UI Layers y el HUD de combate
  en Draw GUI. De hecho es lo más habitual: la parte que cambia cada frame (barras, números,
  daño flotante) es más fácil en Draw GUI, y la que es estructura fija (paneles, pestañas,
  márgenes) es más fácil en Flexpanels.

Todo el detalle de UI Layers —cómo se crean, el orden de dibujado, `layer_get_flexpanel_node()`,
qué cambia para las instancias que viven dentro— está en
[02 · 04](../02%20-%20Novedades%202026/04%20-%20UI%20Layers%20y%20Flexpanels.md). No lo repito aquí.

> ⚠️ **El manual no dice que las UI Layers sean «la forma recomendada» de hacer UI.** Las
> describe como la herramienta para HUDs y menús, pero no deprecia el evento Draw GUI ni lo
> desaconseja. Cualquier afirmación de que Draw GUI «está obsoleto» es falsa.
>
> 🔺 Las funciones `flexpanel_*` **solo calculan el layout**: te dan posiciones y tamaños de
> un árbol de rectángulos. El dibujado sigue siendo tuyo. Eso las hace utilizables también
> sin el editor, para maquetar una pantalla propia.

### 3.2 El lienzo: fija la GUI y no vuelvas a escribir un píxel absoluto

Lo primero que hace un juego serio es **fijar la resolución lógica de la GUI**. A partir de
ahí, todas tus coordenadas son estables y GameMaker se encarga de escalarlas.

```gml
/// obj_juego · Create  (controlador persistente, primera room)
// Resolución LÓGICA de la interfaz. No es la de la ventana: es en la que diseñas.
//   · Juego de píxel: la misma que la application surface (p. ej. 480 x 270)
//   · Juego HD:       1920 x 1080 y a escalar
display_set_gui_size(1920, 1080);

// Márgenes de seguridad como FRACCIÓN, no en píxeles (§3.3)
global.ui_margen_x = 0;
global.ui_margen_y = 0;

dispositivo_iniciar();
```

**Las tres funciones del lienzo, con lo que de verdad hacen** (manual LTS 2026):

| Función | Qué hace |
|---|---|
| `display_get_gui_width()` / `display_get_gui_height()` | Devuelven el tamaño **actual** de la GUI en píxeles lógicos. Si has llamado a `display_set_gui_size(1920, 1080)`, devuelven 1920 y 1080 pase lo que pase con la ventana |
| `display_set_gui_size(w, h)` | Fija ese tamaño lógico. La GUI se **estira** para llenar la application surface. Con `-1, -1` se restablece a 1:1 con la application surface |
| `display_set_gui_maximise([xscale], [yscale], [xoffset], [yoffset])` | Cambia el **origen y la referencia**: la GUI pasa a medirse contra la ventana o la pantalla en vez de contra la application surface. Es lo que necesitas para dibujar **sobre las barras negras** del *letterbox* |

> 🔺 **Corrección importante.** Verás por ahí (incluido en
> [03 · 35 §9](../03%20-%20Cursos%20%28YouTube%29/35%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Evento%20Draw%20GUI.md))
> que llamar a `display_set_gui_maximise()` **sin argumentos** «restablece la escala a 1». El
> manual dice otra cosa: sin argumentos **maximiza** la GUI a la pantalla o ventana, con
> origen en su (0,0). **El restablecimiento es `display_set_gui_maximise(-1, -1)`.** Es una
> confusión frecuente y merece la pena tenerla clara: si tu HUD «se descoloca al pulsar
> pantalla completa», mira aquí primero.
>
> 💡 `display_set_gui_maximize` (con *z*, ortografía americana) **también existe** en el
> runtime, con la misma firma. Son alias. Usa la que quieras, pero usa siempre la misma.

**La función `ancla()`: el único sitio del proyecto donde se escriben coordenadas**

```gml
// scr_ui_layout
// Verificado: display_get_gui_width, display_get_gui_height, lerp, clamp, floor

/// @func zona_segura()
/// @desc Rectángulo útil de la GUI, ya descontados los márgenes de seguridad (§3.3).
/// @returns {Struct} { izq, arr, der, aba, ancho, alto, centro_x, centro_y }
function zona_segura() {
    var _w = display_get_gui_width();
    var _h = display_get_gui_height();
    var _mx = _w * global.ui_margen_x;
    var _my = _h * global.ui_margen_y;

    return {
        izq: _mx,           arr: _my,
        der: _w - _mx,      aba: _h - _my,
        ancho: _w - _mx * 2, alto: _h - _my * 2,
        centro_x: _w * 0.5,  centro_y: _h * 0.5,
    };
}

/// @func ancla(_fx, _fy, _margen_x, _margen_y)
/// @desc Punto de la GUI expresado como fracción de la zona segura más un margen
///       EN PÍXELES HACIA DENTRO. Sobrevive a cualquier resolución y a cualquier
///       cambio de tamaño de ventana.
///         ancla(0, 0, 32, 32)      → esquina superior izquierda, 32 px hacia dentro
///         ancla(0.5, 0)            → centro arriba
///         ancla(1, 1, 24, 24)      → esquina inferior derecha, 24 px hacia dentro
/// @param  {Real} _fx        Fracción horizontal, 0 = izquierda, 1 = derecha
/// @param  {Real} _fy        Fracción vertical, 0 = arriba, 1 = abajo
/// @param  {Real} _margen_x  Píxeles de GUI hacia el interior (opcional)
/// @param  {Real} _margen_y  Píxeles de GUI hacia el interior (opcional)
/// @returns {Struct} { px, py }
function ancla(_fx, _fy, _margen_x = 0, _margen_y = 0) {
    var _s = zona_segura();

    // El margen apunta siempre hacia dentro: si anclas a la derecha, resta.
    var _sx = (_fx > 0.5) ? -1 : 1;
    var _sy = (_fy > 0.5) ? -1 : 1;

    return {
        px: floor(lerp(_s.izq, _s.der, _fx) + _margen_x * _sx),
        py: floor(lerp(_s.arr, _s.aba, _fy) + _margen_y * _sy),
    };
}

/// @func escala_ui()  — multiplicador de tamaño elegido por el jugador (1.0 … 1.5, ver 04 · 27)
function escala_ui() { return global.a11y.escala_texto; }
```

```gml
/// obj_hud · Draw GUI  —  así se usa: cero números mágicos de pantalla
draw_set_font(fnt_ui);
draw_set_valign(fa_top);

var _p = ancla(0, 0, 32, 32);                     // arriba a la izquierda
draw_set_halign(fa_left);
draw_text(_p.px, _p.py, $"Vida: {obj_jugador.vida}");

var _q = ancla(1, 0, 32, 32);                     // arriba a la derecha
draw_set_halign(fa_right);
draw_text(_q.px, _q.py, $"{global.monedas} ◆");

draw_set_halign(fa_left);   // deja el estado como lo encontraste
```

> ⚠️ **`draw_set_halign`, `draw_set_valign`, `draw_set_color`, `draw_set_alpha` y
> `draw_set_font` son estado GLOBAL del renderizador.** Lo que dejes puesto lo hereda la
> siguiente instancia que dibuje. Cada bloque de UI debe restablecer lo que toque, o tendrás
> el bug clásico de «el texto del mundo se ha vuelto amarillo y centrado».

### 3.3 Zonas seguras: el notch del móvil y el overscan de la tele

> ⚠️ **GameMaker no tiene ninguna función de *safe area*.** Comprobado sobre el manual LTS
> 2026 completo y sobre el catálogo de símbolos del runtime: no existe `display_get_safe_area`,
> ni nada equivalente para el notch. `display_get_dpi_x()` / `display_get_dpi_y()` existen,
> pero informan de densidad de píxel, no de recortes de pantalla. **El margen lo calculas tú.**

Los dos problemas son distintos:

- **Televisor (*overscan*).** Muchas teles siguen recortando los bordes de la imagen. Las
  cifras vigentes coinciden entre fabricantes: la guía **«Designing for TV» de Microsoft** y
  la de **Android TV / Google TV** dan el mismo margen —**5 %**, es decir 48 dp/epx a los
  lados y 27 arriba y abajo sobre un lienzo de referencia de 960×540—, y la recomendación
  **EBU R95** sitúa el *graphics safe* en el **5 %** y el *action safe* en el **3,5 %**. La
  **HIG de Apple para tvOS** manda retranquear el contenido principal **60 puntos arriba y
  abajo y 80 a los lados**, que sobre 1920×1080 puntos son un 5,6 % y un 4,2 %.
  **Conclusión operativa: un 5 % de margen por lado y no te compliques.**

  > ⚠️ La regla antigua de «*title safe* 80 % / *action safe* 90 %» viene de las
  > recomendaciones SMPTE de los años sesenta y **ya no es la vigente**: los estándares
  > modernos la han estrechado al 5 %. Si te encuentras el 10 % en un tutorial, está
  > desactualizado — aunque en 4:3 antiguo era correcto.
- **Móvil (*notch*, isla dinámica, esquinas redondeadas, barra de gestos).** El recorte no es
  simétrico y depende del modelo y de la orientación. No lo puedes consultar: solo puedes
  reservar un margen generoso en el lado corto y, si el juego es horizontal, en **ambos**
  laterales (el notch cambia de lado al girar el móvil).

```gml
/// scr_ui_layout  (continuación)  —  fijar los márgenes al arrancar
/// Verificado: os_type, os_ios, os_android, os_switch, os_ps5, os_xboxseriesxs, os_tvos

/// @func margenes_por_plataforma(_extra)
/// @desc Fija global.ui_margen_x / _y (FRACCIÓN de la pantalla) según dónde corremos.
/// @param {Real} _extra  Corrección del jugador, 0 … 0.05 (el calibrador de abajo)
function margenes_por_plataforma(_extra = 0) {
    switch (os_type) {
        case os_switch:
        case os_ps5:
        case os_xboxseriesxs:
        case os_tvos:
            global.ui_margen_x = 0.05;      // TV: 5 % por lado (Microsoft, Google TV, EBU R95)
            global.ui_margen_y = 0.05;
            break;

        case os_ios:
        case os_android:
            // Notch + barra de gestos: asimétrico de verdad, pero a ciegas solo
            // se puede reservar un margen simétrico y generoso.
            global.ui_margen_x = 0.045;
            global.ui_margen_y = 0.030;
            break;

        default:                            // escritorio y navegador
            global.ui_margen_x = 0;
            global.ui_margen_y = 0;
            break;
    }

    global.ui_margen_x += _extra;           // corrección del jugador
    global.ui_margen_y += _extra;
}
```

> 💡 **El truco que usan las consolas: deja que lo ajuste el jugador.** Una pantalla de
> calibración con un recuadro y las flechas para encogerlo («ajusta hasta ver el marco
> completo») resuelve el overscan y el notch de una vez, en todos los modelos, sin API. Es un
> ajuste más de [04 · 25](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md):
> un slider de 0 a 0,05 sumado a `global.ui_margen_*`.
>
> 🔺 **La zona segura afecta a la UI, no al juego.** El mundo puede y debe llenar la pantalla
> entera: lo que se retranquea es la HUD.

### 3.4 Paneles nine-slice: un sprite pequeño para cualquier tamaño

El *nine slice* corta un sprite con cuatro guías en nueve trozos: las esquinas nunca se
escalan, los bordes se estiran o se repiten en un solo eje, y el centro rellena. Es la forma
correcta de tener paneles, botones y bocadillos de cualquier tamaño con **una sola imagen de
48×48 px**.

**En el editor**: se activa en el editor de sprites, pestaña **Nine Slice**, arrastrando las
cuatro guías. Una vez activo, el sprite se dibuja así **en todas partes**, sin tocar código.

**Por código** (para cambiarlo en runtime o para generar paneles temáticos):

```gml
/// obj_juego · Create  —  configurar el panel de la interfaz
/// Verificado: sprite_nineslice_create, sprite_set_nineslice, sprite_get_nineslice,
///             nineslice_left/top/right/bottom/centre,
///             nineslice_stretch/repeat/mirror/blank/hide

var _ns = sprite_nineslice_create();   // struct nuevo, con valores por defecto

_ns.enabled = true;
_ns.left    = 12;   // desplazamiento de la guía izquierda desde el borde izquierdo
_ns.right   = 12;   // ídem desde el borde derecho
_ns.top     = 12;
_ns.bottom  = 12;

// tilemode es un ARRAY indexado por las constantes de corte
_ns.tilemode[nineslice_centre] = nineslice_stretch;  // el centro se estira
_ns.tilemode[nineslice_top]    = nineslice_repeat;   // el borde superior se repite
_ns.tilemode[nineslice_bottom] = nineslice_repeat;
_ns.tilemode[nineslice_left]   = nineslice_stretch;
_ns.tilemode[nineslice_right]  = nineslice_stretch;

sprite_set_nineslice(spr_panel, _ns);
```

**Los campos del struct Nine Slice**, tal cual los define el manual:

| Campo | Tipo | Qué es |
|---|---|---|
| `enabled` | Bool | Nine slicing activo para ese sprite |
| `left`, `right`, `top`, `bottom` | Real | Desplazamiento de cada guía desde su borde |
| `tilemode` | Array | Modo de cada corte, indexado por `nineslice_left`, `nineslice_top`, `nineslice_right`, `nineslice_bottom`, `nineslice_centre` |

Modos: `nineslice_stretch` (estira) · `nineslice_repeat` (repite) · `nineslice_mirror`
(repite en espejo) · `nineslice_blank` (ni estira ni repite: deja hueco) · `nineslice_hide`
(no dibuja ese corte).

```gml
/// @func panel_dibujar(_spr, _px, _py, _ancho, _alto, _color, _alfa)
/// @desc Dibuja un panel nine-slice. El sprite debe tener nine slice activo.
function panel_dibujar(_spr, _px, _py, _ancho, _alto, _color = c_white, _alfa = 1) {
    draw_sprite_stretched_ext(_spr, 0, _px, _py, _ancho, _alto, _color, _alfa);
}
```

> 🔺 **Cuatro trampas del nine slice, todas reales:**
> 1. **No funciona con `draw_sprite_part()` ni con `draw_sprite_pos()`.** Lo dice el manual:
>    esas funciones dibujan un trozo o deforman, y el nine slice se desactiva. Usa
>    `draw_sprite_stretched()`, `draw_sprite_stretched_ext()` o `draw_sprite_ext()`.
> 2. **`sprite_set_nineslice()` cambia el ASSET, no una instancia.** Afecta a todo lo que use
>    ese sprite en todo el juego, y a lo que se cree después.
> 3. **`sprite_get_nineslice()` devuelve el struct vivo del sprite.** Si lo modificas, estás
>    modificando el sprite. Para hacer pruebas parte de `sprite_nineslice_create()`.
> 4. **La constante del centro es `nineslice_centre`**, con *-re*. (`nineslice_center` también
>    existe en el runtime como alias, pero el manual documenta la británica: usa esa.)
>
> 💡 **Sin nine slice también se puede**, dibujando los nueve trozos a mano con
> `draw_sprite_part_ext()`. Es más código y más *draw calls*: solo merece la pena si necesitas
> que cada trozo tenga color o alfa distintos.

### 3.5 Los componentes clásicos

Todos comparten el mismo patrón: **un struct con el estado, una función que lo actualiza en
el Step y otra que lo dibuja en el Draw GUI.** Nunca lógica en el Draw.

#### a) Botón, con sus cuatro estados

```gml
// scr_ui_boton
// Verificado: point_in_rectangle, device_mouse_x_to_gui, device_mouse_y_to_gui,
//             device_mouse_check_button, device_mouse_check_button_released,
//             keyboard_check_pressed, gamepad_button_check_pressed, audio_play_sound,
//             draw_sprite_stretched_ext, draw_text_transformed, string_width, is_callable

/// @func boton_nuevo(_etiqueta, _fx, _fy, _mx, _my, _ancho, _alto, _accion)
/// @desc El botón guarda su ANCLA, no su posición: así sobrevive a cambiar de resolución.
function boton_nuevo(_etiqueta, _fx, _fy, _mx, _my, _ancho, _alto, _accion) {
    return {
        etiqueta: _etiqueta,
        fx: _fx, fy: _fy, mx: _mx, my: _my,     // ancla
        ancho: _ancho, alto: _alto,
        px: 0, py: 0,                            // se recalcula cada frame
        activo: true,                            // false → estado "inactivo"
        motivo: "",                              // por qué está inactivo (se enseña)
        estado: "normal", previo: "normal",
        pulso: 1,                                // escala, para el juice
        accion: _accion,
    };
}

/// @func boton_actualizar(_b, _con_foco)
/// @desc Step. Devuelve true en el frame en que se activa.
function boton_actualizar(_b, _con_foco) {
    var _p = ancla(_b.fx, _b.fy, _b.mx, _b.my);
    _b.px = _p.px - _b.ancho * 0.5;              // el ancla marca el CENTRO
    _b.py = _p.py - _b.alto  * 0.5;

    _b.previo = _b.estado;
    _b.pulso  = aproximar(_b.pulso, 1, 0.06);    // vuelve a su tamaño (`aproximar()` en §3.5b)

    var _raton = (global.ui_dispositivo == "raton")
              && point_in_rectangle(device_mouse_x_to_gui(0), device_mouse_y_to_gui(0),
                                    _b.px, _b.py, _b.px + _b.ancho, _b.py + _b.alto);

    if (!_b.activo) {
        _b.estado = "inactivo";
        // insistir en un botón inactivo merece una respuesta, no silencio
        if (_raton && device_mouse_check_button_released(0, mb_left)) {
            audio_play_sound(snd_ui_error, 10, false);
            aviso_lanzar(_b.motivo, "error");
        }
        return false;
    }

    var _mantiene = _raton && device_mouse_check_button(0, mb_left);
    var _suelta   = _raton && device_mouse_check_button_released(0, mb_left);
    var _confirma = _con_foco && (keyboard_check_pressed(vk_enter)
                              ||  gamepad_button_check_pressed(0, gp_face1));

    if      (_mantiene)           _b.estado = "pulsado";
    else if (_raton || _con_foco) _b.estado = "foco";
    else                          _b.estado = "normal";

    // el sonido va en el CAMBIO de estado, no cada frame
    if (_b.estado == "foco" && _b.previo == "normal") {
        audio_play_sound(snd_ui_foco, 10, false);
    }

    if (_suelta || _confirma) {
        audio_play_sound(snd_ui_aceptar, 10, false);
        _b.pulso = 0.90;
        if (is_callable(_b.accion)) _b.accion();
        return true;
    }
    return false;
}

/// @func boton_dibujar(_b)
/// @desc Draw GUI. Solo dibuja: ni una decisión de lógica aquí.
function boton_dibujar(_b) {
    static COLORES = {
        normal:   { fondo: c_white,  tinta: c_white, desp: 0 },
        foco:     { fondo: c_yellow, tinta: c_white, desp: 0 },
        pulsado:  { fondo: c_yellow, tinta: c_white, desp: 2 },   // se hunde 2 px
        inactivo: { fondo: c_gray,   tinta: c_gray,  desp: 0 },
    };
    var _c = COLORES[$ _b.estado];

    var _w = _b.ancho * _b.pulso;
    var _h = _b.alto  * _b.pulso;
    var _x = _b.px + (_b.ancho - _w) * 0.5;
    var _y = _b.py + (_b.alto  - _h) * 0.5 + _c.desp;

    panel_dibujar(spr_panel_boton, _x, _y, _w, _h, _c.fondo, _b.activo ? 1 : 0.55);

    var _e = escala_ui();
    draw_set_font(fnt_ui);
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    draw_set_color(_c.tinta);
    draw_set_alpha(_b.activo ? 1 : 0.55);
    draw_text_transformed(_x + _w * 0.5, _y + _h * 0.5, _b.etiqueta, _e, _e, 0);

    draw_set_alpha(1);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);
}
```

> 💡 **`COLORES[$ _b.estado]` es acceso a struct por nombre en tiempo de ejecución.** El
> acesor `[$ ]` te ahorra el `switch` de cuatro ramas y hace que añadir un estado sea añadir
> una línea.

#### b) Barra de vida con retardo (la barra «fantasma»)

Dos valores para el mismo dato: el real, que salta al instante, y el **fantasma**, que lo
persigue con retardo. El hueco entre ambos es el daño recibido — y es lo que se ve.

```gml
// scr_ui_barra
// Verificado: lerp, power, clamp, min, max, delta_time, random_range,
//             draw_rectangle_color  (y draw_healthbar, citada más abajo)

/// @func aproximar(_actual, _objetivo, _mitad_vida)
/// @desc Suavizado exponencial INDEPENDIENTE de los fps: en _mitad_vida segundos
///       recorre la mitad de lo que le falta, dé el juego 30 o 240 fps.
/// @param {Real} _mitad_vida  Segundos. 0.05 = muy rápido, 0.4 = perezoso.
function aproximar(_actual, _objetivo, _mitad_vida) {
    var _dt = delta_time / 1000000;                  // microsegundos → segundos
    return lerp(_objetivo, _actual, power(0.5, _dt / _mitad_vida));
}

/// @func barra_nueva(_maximo)
function barra_nueva(_maximo) {
    return { valor: _maximo, fantasma: _maximo, maximo: _maximo,
             espera: 0, sacudida: 0 };
}

/// @func barra_fijar(_b, _valor)
/// @desc Cambia el valor real. El fantasma se quedará atrás a propósito.
function barra_fijar(_b, _valor) {
    var _antes = _b.valor;
    _b.valor = clamp(_valor, 0, _b.maximo);
    if (_b.valor < _antes) {
        _b.espera   = 0.35;                 // el fantasma no se mueve durante 0,35 s
        _b.sacudida = 6;                     // y la barra tiembla
    } else {
        _b.fantasma = min(_b.fantasma, _b.valor);   // al curar, el fantasma no estorba
    }
}

/// @func barra_actualizar(_b)
function barra_actualizar(_b) {
    var _dt = delta_time / 1000000;
    _b.espera   = max(0, _b.espera - _dt);
    _b.sacudida = aproximar(_b.sacudida, 0, 0.08);
    if (_b.espera <= 0) _b.fantasma = aproximar(_b.fantasma, _b.valor, 0.18);
}

/// @func barra_dibujar(_b, _px, _py, _ancho, _alto)
function barra_dibujar(_b, _px, _py, _ancho, _alto) {
    // el temblor respeta el ajuste de accesibilidad (04 · 27)
    var _s = global.a11y.reduce_motion ? 0 : _b.sacudida;
    var _x = _px + random_range(-_s, _s);

    // 1. fondo
    draw_rectangle_color(_x, _py, _x + _ancho, _py + _alto,
                         c_black, c_black, c_black, c_black, false);
    // 2. fantasma (el daño que "todavía duele")
    var _wf = _ancho * (_b.fantasma / _b.maximo);
    draw_rectangle_color(_x, _py, _x + _wf, _py + _alto,
                         c_red, c_red, c_red, c_red, false);
    // 3. vida real, encima
    var _wv = _ancho * (_b.valor / _b.maximo);
    var _col = (_b.valor / _b.maximo < 0.25) ? c_orange : c_lime;
    draw_rectangle_color(_x, _py, _x + _wv, _py + _alto,
                         _col, _col, _col, _col, false);
    // 4. borde
    draw_rectangle_color(_x, _py, _x + _ancho, _py + _alto,
                         c_white, c_white, c_white, c_white, true);
}
```

> 💡 **`draw_healthbar(x1, y1, x2, y2, amount, backcol, mincol, maxcol, direction, showback,
> showborder)` existe y sirve para prototipar en un minuto.** Ojo con dos detalles: `amount`
> va de **0 a 100**, no de 0 a 1; y `direction` es `0` izquierda, `1` derecha, `2` arriba,
> `3` abajo. Para la versión con fantasma no vale, porque solo dibuja una barra.

#### c) Texto flotante de daño: el que vive en el mundo pero se lee en la GUI

El texto flotante completo (aparición, subida, desvanecido, *pop* de entrada) está en
[04 · 15 §5.6](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md). Lo que
falta ahí y hace falta aquí es **el problema de UI**: si lo dibujas en el evento Draw, la
cámara lo escala, y con zoom 3× tus números de daño son gigantes y borrosos.

La solución es dibujarlo en **Draw GUI**, convirtiendo la posición del mundo a coordenadas de
GUI. Así el número siempre tiene el mismo tamaño y la misma nitidez, esté el zoom donde esté.

```gml
// scr_ui_layout (continuación)
// Verificado: view_camera, camera_get_view_x/_y/_width/_height,
//             display_get_gui_width, display_get_gui_height

/// @func mundo_a_gui(_wx, _wy)
/// @desc Convierte un punto del mundo (room) a coordenadas de la capa GUI.
///       Úsalo para dibujar en Draw GUI algo que está anclado a una posición del mundo:
///       números de daño, nombres sobre la cabeza, marcadores de objetivo.
/// @returns {Struct} { px, py }
function mundo_a_gui(_wx, _wy) {
    var _cam = view_camera[0];                      // cámara del viewport 0
    var _vx = camera_get_view_x(_cam);
    var _vy = camera_get_view_y(_cam);
    var _vw = camera_get_view_width(_cam);
    var _vh = camera_get_view_height(_cam);

    return {
        px: (_wx - _vx) / _vw * display_get_gui_width(),
        py: (_wy - _vy) / _vh * display_get_gui_height(),
    };
}
```

```gml
/// obj_texto_flotante · Draw GUI  (dejando el evento Draw vacío)
var _p = mundo_a_gui(x, y);
var _e = escala_ui() * pulso;

draw_set_font(fnt_dano);
draw_set_halign(fa_center);
draw_set_valign(fa_middle);
draw_set_alpha(alfa);

draw_set_color(c_black);                                    // contorno barato
draw_text_transformed(_p.px + 2, _p.py + 2, texto, _e, _e, 0);
draw_set_color(color);
draw_text_transformed(_p.px, _p.py, texto, _e, _e, 0);

draw_set_alpha(1);
draw_set_halign(fa_left);
draw_set_valign(fa_top);
```

> 🔺 **`mundo_a_gui()` en Draw GUI usa `view_camera[0]` a propósito.** En el evento Draw GUI
> no hay «cámara activa» del viewport que se esté dibujando, porque la GUI se dibuja una sola
> vez y no por viewport. Si tienes pantalla partida, dibuja esos elementos en el evento
> **Draw End** de cada viewport, no en Draw GUI.

#### d) Tooltip: el que siempre se sale de la pantalla

Dos requisitos y un bug clásico. Requisitos: **aparece tras una pausa** (si aparece al
instante, parpadea al pasar el ratón) y **se mide antes de dibujarse**. El bug: se sale por
la derecha o por abajo.

```gml
// scr_ui_pista
// Verificado: string_width_ext, string_height_ext, draw_text_ext, clamp, delta_time

/// @func pista_dibujar(_texto, _px, _py, _ancho_max)
/// @desc Bocadillo de ayuda que NUNCA se sale de la pantalla.
function pista_dibujar(_texto, _px, _py, _ancho_max = 320) {
    if (_texto == "") return;

    draw_set_font(fnt_ui_pequena);
    var _sep = -1;                                   // separación de línea por defecto
    var _tw  = min(_ancho_max, string_width_ext(_texto, _sep, _ancho_max));
    var _th  = string_height_ext(_texto, _sep, _ancho_max);

    var _pad = 10;
    var _w = _tw + _pad * 2;
    var _h = _th + _pad * 2;

    // el bocadillo sale arriba a la derecha del cursor…
    var _x = _px + 18;
    var _y = _py - _h - 8;

    // …salvo que no quepa: entonces se voltea al otro lado
    var _s = zona_segura();
    if (_x + _w > _s.der) _x = _px - _w - 18;
    if (_y      < _s.arr) _y = _py + 22;

    // y en cualquier caso se le mete dentro a la fuerza
    _x = clamp(_x, _s.izq, _s.der - _w);
    _y = clamp(_y, _s.arr, _s.aba - _h);

    panel_dibujar(spr_panel_pista, _x, _y, _w, _h, c_white, 0.95);

    draw_set_color(c_white);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);
    draw_text_ext(_x + _pad, _y + _pad, _texto, _sep, _ancho_max);
}
```

```gml
/// obj_ui · Step — la pausa antes de mostrarla
if (elemento_bajo_cursor == elemento_anterior) {
    espera_pista = max(0, espera_pista - delta_time / 1000000);
} else {
    espera_pista = 0.45;                    // 0,45 s de reposo antes de aparecer
    elemento_anterior = elemento_bajo_cursor;
}
mostrar_pista = (espera_pista <= 0);
```

> 💡 **`string_width_ext(cadena, sep, ancho)` y `string_height_ext(...)` miden el texto ya
> con los saltos automáticos aplicados**, exactamente como lo dibujará `draw_text_ext()` con
> los mismos argumentos. Medir con `string_width()` a secas y luego dibujar con `_ext` es la
> receta para que el panel no coincida con el texto.
>
> 🔺 **Mide siempre después de `draw_set_font()`.** Las funciones de medida usan la fuente
> **actual**: si mides antes de fijar la fuente, mides con otra.

#### e) Inventario en cuadrícula con arrastrar y soltar

Un inventario es un array plano dibujado como rejilla: `_i div _columnas` da la fila y
`_i mod _columnas` la columna (§2.2). El arrastre es una máquina de tres estados: *nada* →
*cogido* → *soltado*.

```gml
// scr_ui_inventario
// Verificado: array_create, array_length, floor, is_undefined, device_mouse_x_to_gui,
//             device_mouse_y_to_gui, device_mouse_check_button_pressed,
//             device_mouse_check_button_released, draw_sprite_ext, draw_sprite_stretched_ext

/// @func inventario_nuevo(_columnas, _filas, _lado, _hueco)
function inventario_nuevo(_columnas, _filas, _lado = 64, _hueco = 6) {
    return {
        objetos: array_create(_columnas * _filas, undefined),
        columnas: _columnas, filas: _filas, lado: _lado, hueco: _hueco,
        px: 0, py: 0,               // esquina; se recalcula cada frame
        foco: 0,                    // celda marcada (mando / teclado)
        cogido: undefined,          // objeto en la mano
        origen: -1,                 // celda de la que salió
    };
}

/// @func inventario_celda_en(_inv, _mx, _my)
/// @desc Índice de la celda bajo un punto de la GUI, o -1 si no hay ninguna.
function inventario_celda_en(_inv, _mx, _my) {
    var _paso = _inv.lado + _inv.hueco;
    var _cx = floor((_mx - _inv.px) / _paso);
    var _cy = floor((_my - _inv.py) / _paso);

    if (_cx < 0 || _cx >= _inv.columnas || _cy < 0 || _cy >= _inv.filas) return -1;
    // caer en el hueco entre celdas no cuenta como celda
    if ((_mx - _inv.px) mod _paso > _inv.lado) return -1;
    if ((_my - _inv.py) mod _paso > _inv.lado) return -1;

    return _cy * _inv.columnas + _cx;
}

/// @func inventario_coger(_inv, _celda)
function inventario_coger(_inv, _celda) {
    if (_celda < 0 || is_undefined(_inv.objetos[_celda])) return;
    _inv.cogido = _inv.objetos[_celda];
    _inv.origen = _celda;
    _inv.objetos[_celda] = undefined;
    audio_play_sound(snd_ui_coger, 10, false);
}

/// @func inventario_soltar(_inv, _celda)
/// @desc Deja lo que hay en la mano. Destino inválido → vuelve a su sitio, nunca se pierde.
function inventario_soltar(_inv, _celda) {
    if (_celda < 0) {
        _inv.objetos[_inv.origen] = _inv.cogido;
        audio_play_sound(snd_ui_error, 10, false);
    } else {
        var _ocupante = _inv.objetos[_celda];           // intercambio, no sobrescritura
        _inv.objetos[_celda]      = _inv.cogido;
        _inv.objetos[_inv.origen] = _ocupante;
        audio_play_sound(snd_ui_soltar, 10, false);
    }
    _inv.cogido = undefined;
    _inv.origen = -1;
}

/// @func inventario_actualizar(_inv)  — Step
function inventario_actualizar(_inv) {
    var _p = ancla(0.5, 0.5);
    var _paso = _inv.lado + _inv.hueco;
    _inv.px = _p.px - (_inv.columnas * _paso - _inv.hueco) * 0.5;
    _inv.py = _p.py - (_inv.filas    * _paso - _inv.hueco) * 0.5;

    if (global.ui_dispositivo == "raton") {
        var _celda = inventario_celda_en(_inv, device_mouse_x_to_gui(0),
                                               device_mouse_y_to_gui(0));
        if (_celda >= 0) _inv.foco = _celda;            // el ratón MUEVE el foco, no lo sustituye

        if (device_mouse_check_button_pressed(0, mb_left))  inventario_coger(_inv, _celda);
        if (device_mouse_check_button_released(0, mb_left)
        && !is_undefined(_inv.cogido))                       inventario_soltar(_inv, _celda);
    }
    // mando y teclado: el mismo botón coge y deja
    else if (gamepad_button_check_pressed(0, gp_face1) || keyboard_check_pressed(vk_enter)) {
        if (is_undefined(_inv.cogido)) inventario_coger(_inv, _inv.foco);
        else                           inventario_soltar(_inv, _inv.foco);
    }
}

/// @func inventario_dibujar(_inv)  — Draw GUI
function inventario_dibujar(_inv) {
    var _paso = _inv.lado + _inv.hueco;

    for (var _i = 0; _i < array_length(_inv.objetos); _i++) {
        var _cx = _inv.px + (_i mod _inv.columnas) * _paso;
        var _cy = _inv.py + (_i div _inv.columnas) * _paso;

        panel_dibujar(spr_panel_celda, _cx, _cy, _inv.lado, _inv.lado);

        var _obj = _inv.objetos[_i];
        if (!is_undefined(_obj)) {
            draw_sprite_ext(_obj.icono, 0, _cx + _inv.lado * 0.5, _cy + _inv.lado * 0.5,
                            1, 1, 0, c_white, 1);
            if (_obj.cantidad > 1) {
                draw_set_halign(fa_right);
                draw_text(_cx + _inv.lado - 4, _cy + _inv.lado - 20, string(_obj.cantidad));
                draw_set_halign(fa_left);
            }
        }
        // el foco se ve SIEMPRE, haya ratón o no
        if (_i == _inv.foco) {
            draw_sprite_stretched_ext(spr_celda_foco, 0, _cx - 3, _cy - 3,
                                      _inv.lado + 6, _inv.lado + 6, c_yellow, 1);
        }
    }

    // lo que llevas en la mano va AL FINAL, pegado al cursor o a la celda con foco
    if (!is_undefined(_inv.cogido)) {
        var _usa_raton = (global.ui_dispositivo == "raton");
        var _hx = _usa_raton ? device_mouse_x_to_gui(0)
                             : _inv.px + (_inv.foco mod _inv.columnas) * _paso + _inv.lado * 0.5;
        var _hy = _usa_raton ? device_mouse_y_to_gui(0)
                             : _inv.py + (_inv.foco div _inv.columnas) * _paso + _inv.lado * 0.5;
        draw_sprite_ext(_inv.cogido.icono, 0, _hx, _hy, 1.1, 1.1, 0, c_white, 0.9);
    }
}
```

> 🔺 **Nunca destruyas el objeto al cogerlo.** El patrón «lo saco de la celda y lo guardo en
> `cogido`» garantiza que un soltar inválido lo devuelve. Si lo borras y lo recreas al soltar,
> cualquier fallo (un cambio de room, un alt-tab, una excepción) borra el objeto del jugador.
> Es el bug de inventario más caro que existe.

#### f) Diálogo: la caja, no el texto

El parser del guion, el efecto máquina de escribir, los retratos y el backlog están completos
en [04 · 10](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md), y si
quieres texto con formato en línea, colores, temblor y saltos por palabra, la herramienta es
**Scribble** ([07 · 18](../07%20-%20Ecosistema/18%20-%20Scribble%20-%20texto%20rico%20%28guía%20en%20español%29.md)).
Aquí solo la parte de interfaz, que es la que se olvida:

- **La caja se dimensiona con el texto medido, no al revés.** `string_height_ext(texto, -1,
  ancho_util)` te da el alto exacto; súmale el *padding* y dibuja el panel nine-slice con ese
  alto. Así una frase corta no deja un cajón vacío y una larga no se desborda.
- **El ancho útil es el ancho de la caja menos el padding menos el retrato.** Ese es el valor
  que va tanto en la medida como en `draw_text_ext()`. Un solo sitio donde se calcula.
- **El indicador de «continuar»** (el triangulito que parpadea) solo aparece cuando el texto
  ha terminado de escribirse. Si aparece antes, el jugador pulsa y se salta media línea.
- **El primer toque completa, el segundo avanza.** Nunca al revés, y nunca «un solo toque que
  a veces completa y a veces avanza».
- **La caja de diálogo es lo único que puede tapar al personaje**, así que va abajo si la
  acción está arriba y arriba si está abajo. En un juego con la cámara centrada, abajo.

#### g) Minimapa con surface: dibujar una vez, mostrar mil

El error es repintar el mapa entero cada frame. Lo correcto es pintarlo **una vez** en una
surface y luego mostrar el trozo que toca con `draw_surface_part_ext()`.

```gml
// obj_minimapa
// Verificado: surface_create, surface_exists, surface_set_target, surface_reset_target,
//             surface_free, draw_clear_alpha, draw_surface_part_ext, layer_tilemap_get_id,
//             tilemap_get_width, tilemap_get_height, tilemap_get

/// Create
mapa_ancho = 512;   mapa_alto = 512;      // resolución de la surface (potencia de 2)
superficie = -1;
sucio      = true;                        // "hay que repintar el mapa"

/// Step  — la surface se pierde sola (minimizar, cambiar resolución, Android en segundo
///         plano). Comprobarlo cada frame no es paranoia: es obligatorio.
if (!surface_exists(superficie)) {
    superficie = surface_create(mapa_ancho, mapa_alto);
    sucio = true;
}

/// Draw GUI Begin  — repintar SOLO cuando algo ha cambiado
if (sucio) {
    surface_set_target(superficie);
    draw_clear_alpha(c_black, 0);

    var _tm = layer_tilemap_get_id(layer_get_id("Colisiones"));
    var _cols = tilemap_get_width(_tm), _filas = tilemap_get_height(_tm);
    var _ex = mapa_ancho / _cols, _ey = mapa_alto / _filas;

    for (var _j = 0; _j < _filas; _j++) {
        for (var _i = 0; _i < _cols; _i++) {
            if (tilemap_get(_tm, _i, _j) != 0) {
                draw_rectangle_color(_i * _ex, _j * _ey, (_i + 1) * _ex, (_j + 1) * _ey,
                                     c_dkgray, c_dkgray, c_dkgray, c_dkgray, false);
            }
        }
    }
    surface_reset_target();
    sucio = false;
}

/// Draw GUI  — mostrar el trozo centrado en el jugador
var _p = ancla(1, 0, 24, 24);
var _lado = 180, _zoom = 3;                   // píxeles de mapa por píxel de pantalla
var _cx = (obj_jugador.x / room_width)  * mapa_ancho;
var _cy = (obj_jugador.y / room_height) * mapa_alto;
var _vw = _lado / _zoom, _vh = _lado / _zoom;

panel_dibujar(spr_panel_mapa, _p.px - _lado, _p.py, _lado, _lado);
draw_surface_part_ext(superficie,
                      clamp(_cx - _vw * 0.5, 0, mapa_ancho - _vw),
                      clamp(_cy - _vh * 0.5, 0, mapa_alto  - _vh),
                      _vw, _vh, _p.px - _lado, _p.py, _zoom, _zoom, c_white, 1);
draw_sprite(spr_punto_jugador, 0, _p.px - _lado * 0.5, _p.py + _lado * 0.5);

/// Clean Up
if (surface_exists(superficie)) surface_free(superficie);
```

> 🔺 **Las seis reglas de las surfaces aplican enteras** —volatilidad, `surface_free()` en el
> Clean Up, nada de crearlas en el Draw sin comprobar—: están en
> [01 · 11 §8](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) y en
> [08 · 05](../08%20-%20Referencia%20GML%20completa/05%20-%20Superficies.md). El fallo típico del
> minimapa es justo ese: funciona hasta que alguien minimiza la ventana.
>
> 💡 **`sucio` es el patrón entero.** Ponlo a `true` cuando el jugador descubra una zona o se
> destruya un muro. El resto del tiempo el minimapa cuesta **una** llamada de dibujo.

#### h) Marcador y temporizador

```gml
// scr_ui_marcador
// Verificado: floor, frac, max, abs, string, string_format, string_replace_all,
//             random_range, draw_text_transformed, draw_set_halign
//             (aproximar() y escala_ui() son de este mismo documento)

/// @func tiempo_texto(_segundos, _con_centesimas)
/// @desc Formatea segundos como m:ss o m:ss.cc, con relleno de ceros.
function tiempo_texto(_segundos, _con_centesimas = false) {
    _segundos = max(0, _segundos);
    var _m  = floor(_segundos / 60);
    var _s  = floor(_segundos) mod 60;
    var _cc = floor(frac(_segundos) * 100);

    var _txt = string(_m) + ":" + string_format(_s, 2, 0);
    _txt = string_replace_all(_txt, " ", "0");            // string_format rellena con espacios
    if (_con_centesimas) {
        _txt += "." + string_replace_all(string_format(_cc, 2, 0), " ", "0");
    }
    return _txt;
}

/// @func marcador_nuevo()
function marcador_nuevo() {
    return { real: 0, mostrado: 0, temblor: 0 };
}

/// @func marcador_sumar(_m, _cuanto)
function marcador_sumar(_m, _cuanto) {
    _m.real += _cuanto;
    _m.temblor = 5;                       // el número acusa el golpe (§3.8)
}

/// @func marcador_actualizar(_m)
function marcador_actualizar(_m) {
    _m.mostrado = aproximar(_m.mostrado, _m.real, 0.12);
    if (abs(_m.real - _m.mostrado) < 1) _m.mostrado = _m.real;   // engancha al final
    _m.temblor = aproximar(_m.temblor, 0, 0.07);
}

/// @func marcador_dibujar(_m, _px, _py)
function marcador_dibujar(_m, _px, _py) {
    var _t = global.a11y.reduce_motion ? 0 : _m.temblor;    // 04 · 27
    var _e = escala_ui() * (1 + _t * 0.02);
    draw_set_font(fnt_numeros);
    draw_set_halign(fa_right);
    draw_text_transformed(_px + random_range(-_t, _t), _py,
                          string(floor(_m.mostrado)), _e, _e, 0);
    draw_set_halign(fa_left);
}
```

> ⚠️ **El baile de los dígitos.** Con una fuente proporcional, un contador que pasa de `199`
> a `200` se mueve, porque el `1` es más estrecho que el `2`. Se arregla de dos formas:
> **fuente monoespaciada para los números** (una fuente de sprite creada con
> `font_add_sprite_ext()` es perfecta para esto), o **alineando a la derecha** con
> `draw_set_halign(fa_right)`, que al menos deja fijo el borde derecho. Para un cronómetro,
> la monoespaciada es obligatoria.

#### i) Notificaciones apiladas (*toasts*)

Un array de avisos que se apilan, se desplazan hacia su sitio y se van solos. La sutileza
está en que **la posición objetivo se recalcula cada frame** a partir del índice: así, cuando
uno caduca, los de abajo suben deslizándose en vez de saltar.

```gml
// scr_ui_avisos
// Verificado: array_length, array_push, array_delete, delta_time, min,
//             audio_play_sound, draw_text_ext, draw_set_alpha, draw_set_valign

/// @func avisos_iniciar()
function avisos_iniciar() { global.ui_avisos = []; }

/// @func aviso_lanzar(_texto, _tipo)
/// @param {String} _tipo  "info" | "logro" | "error"
function aviso_lanzar(_texto, _tipo = "info") {
    static MAXIMO = 4;

    // si ya hay demasiados, el más viejo empieza a irse ya
    if (array_length(global.ui_avisos) >= MAXIMO) {
        global.ui_avisos[0].vida = min(global.ui_avisos[0].vida, 0.25);
    }

    array_push(global.ui_avisos, {
        texto: _texto, tipo: _tipo,
        vida: 3.5,                 // segundos en pantalla
        alfa: 0,                   // entra apareciendo
        desplaz: 40,               // entra deslizándose desde la derecha
        py: 0, py_objetivo: 0,     // py lo fija avisos_actualizar() a partir del índice
    });
    audio_play_sound(_tipo == "error" ? snd_ui_error : snd_ui_aviso, 10, false);
}

/// @func avisos_actualizar()
function avisos_actualizar() {
    var _dt = delta_time / 1000000;
    var _s  = zona_segura();
    var _alto = 56, _hueco = 8;

    for (var _i = array_length(global.ui_avisos) - 1; _i >= 0; _i--) {
        var _a = global.ui_avisos[_i];

        _a.vida -= _dt;
        _a.py_objetivo = _s.arr + 24 + _i * (_alto + _hueco);
        _a.py          = aproximar(_a.py, _a.py_objetivo, 0.10);

        if (_a.vida > 0.4) {                       // entrando / estable
            _a.alfa    = aproximar(_a.alfa, 1, 0.08);
            _a.desplaz = aproximar(_a.desplaz, 0, 0.10);
        } else {                                    // saliendo
            _a.alfa    = aproximar(_a.alfa, 0, 0.10);
            _a.desplaz = aproximar(_a.desplaz, 40, 0.12);
        }

        if (_a.vida <= 0 && _a.alfa < 0.02) array_delete(global.ui_avisos, _i, 1);
    }
}

/// @func avisos_dibujar()
function avisos_dibujar() {
    static COLOR = { info: c_white, logro: c_yellow, error: c_red };
    var _s = zona_segura();
    var _ancho = 340, _alto = 56;

    draw_set_font(fnt_ui);
    draw_set_valign(fa_middle);
    draw_set_halign(fa_left);

    for (var _i = 0; _i < array_length(global.ui_avisos); _i++) {
        var _a = global.ui_avisos[_i];
        var _x = _s.der - _ancho - 24 + _a.desplaz;

        panel_dibujar(spr_panel_aviso, _x, _a.py, _ancho, _alto,
                      COLOR[$ _a.tipo], _a.alfa * 0.95);

        draw_set_alpha(_a.alfa);
        draw_set_color(c_white);
        draw_text_ext(_x + 16, _a.py + _alto * 0.5, _a.texto, -1, _ancho - 32);
        draw_set_alpha(1);
    }
    draw_set_valign(fa_top);
}
```

> 🔺 **El bucle de borrado va hacia atrás.** `for (_i = n-1; _i >= 0; _i--)` con
> `array_delete()` dentro. Hacia delante, borrar un elemento desplaza los siguientes y te
> saltas uno. Es el mismo motivo por el que se recorren al revés los arrays de partículas.

#### j) Pantalla de mapa completo: desplazamiento y zoom, salas y viaje rápido

El minimapa (§3.5g) muestra el entorno inmediato y se dibuja solo. La pantalla de **mapa
completo** es otra cosa: una pantalla propia que congela el juego, se navega con calma y
resuelve una pregunta que el minimapa no puede: *"¿qué me queda por ver, y adónde puedo
saltar ya?"*. Comparte con el minimapa la misma surface pre-renderizada — las seis reglas de
volatilidad de las surfaces de §3.5g aplican enteras aquí también, no se repiten.

```gml
// scr_ui_mapa
// Verificado: array_length, array_push, mouse_wheel_up, mouse_wheel_down, gamepad_axis_value,
//             gamepad_button_check_pressed, keyboard_check, keyboard_check_pressed, clamp,
//             lerp, point_distance, infinity, draw_surface_part_ext, draw_sprite_ext,
//             draw_sprite_stretched_ext, draw_sprite
// (ancla(), zona_segura(), panel_dibujar() y aviso_lanzar() son de este mismo documento)

enum SalaEstado { OCULTA, VISITADA, DESCUBIERTA }

/// @func mapa_nuevo(_ancho_mundo, _alto_mundo)
/// @desc El mapa vive en las MISMAS coordenadas que las rooms del mundo, a escala reducida.
function mapa_nuevo(_ancho_mundo, _alto_mundo) {
    return {
        ancho_mundo: _ancho_mundo, alto_mundo: _alto_mundo,
        zoom: 1, zoom_obj: 1,
        cam_x: _ancho_mundo * 0.5, cam_y: _alto_mundo * 0.5,
        salas: [],       // { id_sala, x, y, icono, estado }
        foco: 0,
    };
}

/// @func mapa_sala_registrar(_mapa, _id_sala, _x, _y, _icono)
/// @desc Una vez por sala jugable, al construir el mapa (no hace falta que el jugador la
///       haya visto: empieza en SalaEstado.OCULTA y no se dibuja hasta que se marque).
function mapa_sala_registrar(_mapa, _id_sala, _x, _y, _icono) {
    array_push(_mapa.salas, { id_sala: _id_sala, x: _x, y: _y, icono: _icono,
                               estado: SalaEstado.OCULTA });
}

/// @func mapa_sala_marcar(_mapa, _id_sala, _estado)
/// @desc "Visitada" al entrar la primera vez: revela el CONTORNO, no el icono — "sé que
///       existe, no sé qué hay". "Descubierta" al completarla: icono a color y viaje rápido
///       habilitado. Nunca degrada un estado ya alcanzado (por eso el `max`).
function mapa_sala_marcar(_mapa, _id_sala, _estado) {
    for (var _i = 0; _i < array_length(_mapa.salas); _i++) {
        if (_mapa.salas[_i].id_sala == _id_sala) {
            _mapa.salas[_i].estado = max(_mapa.salas[_i].estado, _estado);
            return;
        }
    }
}

/// @func mapa_actualizar(_mapa)  — Step, SOLO mientras la pantalla de mapa está abierta
function mapa_actualizar(_mapa) {
    if (mouse_wheel_up())   _mapa.zoom_obj = clamp(_mapa.zoom_obj + 0.2, 0.5, 3);
    if (mouse_wheel_down()) _mapa.zoom_obj = clamp(_mapa.zoom_obj - 0.2, 0.5, 3);
    _mapa.zoom = lerp(_mapa.zoom, _mapa.zoom_obj, 0.2);

    var _vel = 8 / _mapa.zoom;      // más despacio al acercar: el mismo gesto recorre menos mundo
    var _dx = gamepad_axis_value(0, gp_axislh) * _vel
            + (keyboard_check(vk_right) - keyboard_check(vk_left)) * _vel;
    var _dy = gamepad_axis_value(0, gp_axislv) * _vel
            + (keyboard_check(vk_down) - keyboard_check(vk_up)) * _vel;
    _mapa.cam_x = clamp(_mapa.cam_x + _dx, 0, _mapa.ancho_mundo);
    _mapa.cam_y = clamp(_mapa.cam_y + _dy, 0, _mapa.alto_mundo);

    // El foco salta a la sala revelada más cercana a la cámara: no hace falta un cursor
    // aparte ni una rejilla — un mapa de sala no es una cuadrícula regular (§2.2).
    var _mejor = -1, _mejor_dist = infinity;
    for (var _i = 0; _i < array_length(_mapa.salas); _i++) {
        var _s = _mapa.salas[_i];
        if (_s.estado == SalaEstado.OCULTA) continue;
        var _d = point_distance(_mapa.cam_x, _mapa.cam_y, _s.x, _s.y);
        if (_d < _mejor_dist) { _mejor_dist = _d; _mejor = _i; }
    }
    _mapa.foco = _mejor;

    if (_mapa.foco >= 0
    && (keyboard_check_pressed(vk_enter) || gamepad_button_check_pressed(0, gp_face1))) {
        var _s = _mapa.salas[_mapa.foco];
        if (_s.estado == SalaEstado.DESCUBIERTA) {
            ir_a_escena(_s.id_sala);        // 04 · 00 §2 — el fundido a negro hace el resto
        } else {
            audio_play_sound(snd_ui_error, 10, false);
            aviso_lanzar("Aún no has llegado ahí", "error");
        }
    }
}

/// @func mapa_dibujar(_mapa, _surf_fondo)  — Draw GUI
/// @desc _surf_fondo es la surface con el mapa ya pintado (mismo patrón "sucio" que el
///       minimapa de §3.5g: se repinta solo cuando se descubre una sala nueva, no cada frame).
function mapa_dibujar(_mapa, _surf_fondo) {
    var _s = zona_segura();
    panel_dibujar(spr_panel_mapa_completo, _s.izq, _s.arr, _s.ancho, _s.alto);

    var _vw = _s.ancho / _mapa.zoom;
    var _vh = _s.alto  / _mapa.zoom;
    var _mx = clamp(_mapa.cam_x - _vw * 0.5, 0, max(0, _mapa.ancho_mundo - _vw));
    var _my = clamp(_mapa.cam_y - _vh * 0.5, 0, max(0, _mapa.alto_mundo  - _vh));

    draw_surface_part_ext(_surf_fondo, _mx, _my, _vw, _vh,
                          _s.izq, _s.arr, _mapa.zoom, _mapa.zoom, c_white, 1);

    for (var _i = 0; _i < array_length(_mapa.salas); _i++) {
        var _sala = _mapa.salas[_i];
        if (_sala.estado == SalaEstado.OCULTA) continue;

        var _px = _s.izq + (_sala.x - _mx) * _mapa.zoom;
        var _py = _s.arr + (_sala.y - _my) * _mapa.zoom;
        if (_px < _s.izq || _px > _s.der || _py < _s.arr || _py > _s.aba) continue;

        var _es_descubierta = (_sala.estado == SalaEstado.DESCUBIERTA);
        draw_sprite_ext(_sala.icono, 0, _px, _py, 1, 1, 0,
                        _es_descubierta ? c_white : c_gray, _es_descubierta ? 1 : 0.5);

        if (_i == _mapa.foco) {
            draw_sprite_stretched_ext(spr_celda_foco, 0, _px - 20, _py - 20, 40, 40, c_yellow, 1);
        }
    }

    // El jugador se ve siempre, esté la cámara del mapa donde esté
    draw_sprite(spr_punto_jugador, 0,
               _s.izq + (obj_jugador.x - _mx) * _mapa.zoom,
               _s.arr + (obj_jugador.y - _my) * _mapa.zoom);
}
```

> 🔺 **Visitada y descubierta no son el mismo bit.** Confundirlas es el error típico: una sala
> "visitada" que ya enseña el icono completo delata el contenido antes de que el jugador lo
> vea (un cofre, un jefe, una salida secundaria). El viaje rápido depende del estado
> **descubierta**, nunca del visitada — llegar de pie a una sala no basta para tele-transportarte
> a ella luego si no la has terminado de explorar.
>
> 💡 **El zoom es el mismo patrón que el zoom punch de la cámara de juego**
> ([04 · 15 §8.3](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md#83-zoom-punch-y-retroceso-de-cámara)):
> un valor objetivo (`zoom_obj`) y un `lerp` hacia él cada frame. Es la técnica que evita que
> el mapa dé un salto brusco al girar la rueda del ratón.

#### k) Tienda: precio, «no te lo puedes permitir», confirmación y venta

Reutiliza el **inventario en cuadrícula** (§3.5e) para el catálogo y el **botón de cuatro
estados** (§3.5a) para comprar: la tienda no inventa un quinto estado de botón para "no te
lo puedes permitir", usa el `inactivo` que ya existe, con su `motivo`.

```gml
// scr_ui_tienda
// Verificado: array_length, array_push, string, keyboard_check_pressed, gamepad_button_check_pressed,
//             audio_play_sound, method, method_get_self
// Reutiliza boton_nuevo/boton_actualizar/boton_dibujar (§3.5a), panel_dibujar (§3.4),
// aviso_lanzar (§3.5i) y global.monedas (§3.2)

/// @func tienda_nuevo(_catalogo)
/// @desc _catalogo: array de { nombre, icono, precio, stat, stat_equipado, comprado }.
///       `stat` y `stat_equipado` son el número que se compara contra lo que el jugador
///       lleva puesto (p. ej. daño de un arma); déjalos en 0 si el artículo no compara.
function tienda_nuevo(_catalogo) {
    var _botones = [];
    for (var _i = 0; _i < array_length(_catalogo); _i++) {
        // el índice va atado al botón con method(): cada uno pide confirmar SU artículo
        array_push(_botones, boton_nuevo(_catalogo[_i].nombre, 0.5, 0, 0, 140 + _i * 72,
                   420, 64, method({ tienda: undefined, indice: _i },
                   function() { tienda.confirmando = indice; })));
    }
    var _t = {
        catalogo: _catalogo, botones: _botones, confirmando: -1, foco: 0,
        rep_arriba: repeticion_nueva(), rep_abajo: repeticion_nueva(),   // navegación, §2.2
    };
    // method_get_self() recupera el struct de contexto del método para completarlo con la
    // tienda ya construida: no se puede pasar `_t` antes de que exista.
    for (var _i = 0; _i < array_length(_botones); _i++) {
        method_get_self(_botones[_i].accion).tienda = _t;
    }
    return _t;
}

/// @func tienda_actualizar(_t)  — Step
function tienda_actualizar(_t) {
    // El precio decide activo/motivo CADA FRAME: si el jugador gana monedas mirando la
    // tienda, el botón se activa solo, sin tener que cerrar y reabrir la pantalla (§1.5).
    for (var _i = 0; _i < array_length(_t.catalogo); _i++) {
        var _item = _t.catalogo[_i];
        var _asequible = global.monedas >= _item.precio;
        _t.botones[_i].activo = _asequible && !_item.comprado;
        _t.botones[_i].motivo = _item.comprado
            ? "Ya lo tienes"
            : (_asequible ? "" : $"Te faltan {_item.precio - global.monedas} monedas");
    }

    if (_t.confirmando >= 0) {
        // Confirmación con «No» por defecto (§2.1 punto 3): aceptar exige una pulsación
        // aparte, cancelar es el camino corto (Escape / B).
        if (keyboard_check_pressed(vk_enter) || gamepad_button_check_pressed(0, gp_face1)) {
            tienda_comprar(_t, _t.confirmando);
            _t.confirmando = -1;
        } else if (keyboard_check_pressed(vk_escape) || gamepad_button_check_pressed(0, gp_face2)) {
            _t.confirmando = -1;    // cancelar nunca necesita su propia confirmación
        }
        return;
    }

    // Foco vertical con la misma repetición de §2.2 (retardo 0,4 s, luego cada 0,1 s)
    var _arr = keyboard_check(vk_up)   || gamepad_button_check(0, gp_padu);
    var _aba = keyboard_check(vk_down) || gamepad_button_check(0, gp_padd);
    if (repeticion_paso(_t.rep_arriba, _arr)) _t.foco = max(0, _t.foco - 1);
    if (repeticion_paso(_t.rep_abajo,  _aba)) _t.foco = min(array_length(_t.botones) - 1, _t.foco + 1);

    for (var _i = 0; _i < array_length(_t.botones); _i++) {
        boton_actualizar(_t.botones[_i], _i == _t.foco);
    }
}

/// @func tienda_comprar(_t, _indice)
function tienda_comprar(_t, _indice) {
    var _item = _t.catalogo[_indice];
    global.monedas -= _item.precio;
    _item.comprado = true;
    audio_play_sound(snd_ui_aceptar, 10, false);
    aviso_lanzar($"Comprado: {_item.nombre}", "info");
}

/// @func tienda_vender(_t, _item, _precio_venta)
/// @desc La venta usa SU PROPIO precio, normalmente una fracción del de compra (mitad es lo
///       habitual): vender por el precio de compra íntegro invita a comprar y vender en bucle
///       para "duplicar" moneda.
function tienda_vender(_t, _item, _precio_venta) {
    global.monedas += _precio_venta;
    _item.comprado = false;
    audio_play_sound(snd_ui_aceptar, 10, false);
    aviso_lanzar($"Vendido: {_item.nombre} (+{_precio_venta})", "info");
}

/// @func tienda_dibujar(_t)  — Draw GUI
function tienda_dibujar(_t) {
    var _s = zona_segura();
    panel_dibujar(spr_panel_tienda, _s.izq, _s.arr, _s.ancho, _s.alto);

    var _p = ancla(1, 0, 32, 32);
    draw_set_halign(fa_right);
    draw_text(_p.px, _p.py, $"{global.monedas} ◆");
    draw_set_halign(fa_left);

    for (var _i = 0; _i < array_length(_t.botones); _i++) {
        boton_dibujar(_t.botones[_i]);

        // precio junto al botón, y la comparación con lo equipado si el artículo tiene stat
        var _item = _t.catalogo[_i];
        var _b = _t.botones[_i];
        draw_text(_b.px + _b.ancho + 12, _b.py + 20, $"{_item.precio} ◆");

        if (_item.stat != 0) {
            var _dif = _item.stat - _item.stat_equipado;
            draw_set_color(_dif > 0 ? c_lime : (_dif < 0 ? c_red : c_white));
            draw_text(_b.px + _b.ancho + 12, _b.py + 40,
                      (_dif > 0 ? "+" : "") + string(_dif) + " frente a lo equipado");
            draw_set_color(c_white);
        }
    }

    if (_t.confirmando >= 0) {
        var _item = _t.catalogo[_t.confirmando];
        panel_dibujar(spr_panel_dialogo, _s.centro_x - 200, _s.centro_y - 60, 400, 120);
        draw_set_halign(fa_center);
        draw_text(_s.centro_x, _s.centro_y - 20, $"¿Comprar {_item.nombre} por {_item.precio}?");
        draw_text(_s.centro_x, _s.centro_y + 20, "Aceptar: confirmar   ·   Cancelar: No");
        draw_set_halign(fa_left);
    }
}
```

> 💡 **`boton_nuevo` no necesitaba cambios.** El estado `inactivo` con `motivo` ya resolvía
> "no te lo puedes permitir" desde que se escribió en §3.5a — la tienda solo decide **cuándo**
> ponerlo a `false` y **qué motivo** enseñar. Es la señal de que el catálogo de componentes
> está bien diseñado: los casos nuevos se resuelven combinando piezas, no añadiendo estados.
>
> ⚠️ **La comparación con lo equipado necesita que `stat`/`stat_equipado` signifiquen lo
> mismo.** Si un artículo compara daño y otro defensa, no los metas en el mismo campo `stat`:
> usa `+N` en verde/rojo solo cuando de verdad son comparables, o el color mentirá.

#### l) Campo de texto: el widget que faltaba

> **Cobertura parcial detectada, unida aquí.** Hasta ahora la biblioteca resolvía esto dos
> veces y a medias: `04 · 11` teclea altas de highscore con `keyboard_lastchar` + backspace (sin
> cursor ni selección, pensado solo para 3-8 caracteres A-Z/0-9), y `08 · 12` documenta
> `clipboard_get_text()`/`clipboard_has_text()` como referencia suelta, sin ningún consumidor.
> Este widget une las dos piezas en un campo genérico — nombre de partida, chat, buscador — con
> cursor visible, selección y pegar. **No repite ninguna de las dos**: las reutiliza.

```gml
// scr_ui_campo_texto
// Verificado: keyboard_string, keyboard_lastchar, clipboard_get_text, clipboard_has_text,
//             clipboard_set_text, string_copy, string_delete, string_insert, string_length,
//             string_char_at, string_width, string_height, ord, is_callable, current_time,
//             keyboard_check, keyboard_check_pressed, draw_line_width, draw_rectangle_color,
//             draw_get_color, draw_set_alpha, min, max

/// @func campo_texto_nuevo(_max_longitud, _texto_inicial, _filtro)
/// @desc _filtro es OPCIONAL: una función que recibe un carácter (string de longitud 1) y
///       devuelve true/false. Sin filtro, se acepta cualquier carácter salvo los de control
///       (ord() < 32) — lo bastante permisivo para admitir CJK si el campo llega desde un IME
///       (01 · 12, sección «IME y entrada de texto no ASCII»).
function campo_texto_nuevo(_max_longitud, _texto_inicial = "", _filtro = undefined) {
    return {
        texto: _texto_inicial,
        cursor: string_length(_texto_inicial) + 1,   // posiciones de string: empiezan en 1
        seleccion: -1,             // posición del otro extremo de la selección, o -1 si no hay
        max_longitud: _max_longitud,
        filtro: _filtro,
        activo: false,
        aviso: false,              // true un frame: el último carácter tecleado se rechazó
        parpadeo_base: 0,
    };
}

/// @func campo_texto_activar(_campo)
/// @desc Llamar al entrar en el campo (clic, Tab, foco de mando). Limpia el buffer de
///       teclado para que texto tecleado ANTES de entrar no aparezca de golpe.
function campo_texto_activar(_campo) {
    keyboard_string     = "";
    _campo.activo       = true;
    _campo.parpadeo_base = current_time;   // el cursor arranca siempre visible, no a mitad de ciclo
}

/// @func campo_texto_desactivar(_campo)
function campo_texto_desactivar(_campo) {
    _campo.activo = false;
    _campo.seleccion = -1;
}

/// __campo_texto_caracter_valido(_campo, _c) — uso interno
function __campo_texto_caracter_valido(_campo, _c) {
    if (is_callable(_campo.filtro)) return _campo.filtro(_c);
    return (ord(_c) >= 32);   // por defecto: cualquier cosa menos caracteres de control
}

/// __campo_texto_borrar_seleccion(_campo) — uso interno
function __campo_texto_borrar_seleccion(_campo) {
    var _ini = min(_campo.cursor, _campo.seleccion);
    var _fin = max(_campo.cursor, _campo.seleccion);
    _campo.texto     = string_delete(_campo.texto, _ini, _fin - _ini);
    _campo.cursor    = _ini;
    _campo.seleccion = -1;
}

/// @func campo_texto_actualizar(_campo)  — Step. No hace nada si el campo no está activo.
function campo_texto_actualizar(_campo) {
    if (!_campo.activo) return;
    _campo.aviso = false;

    // 1 · Texto tecleado ESTE frame (teclado físico, teclado virtual o IME — ver 01 · 12).
    //     Se vacía `keyboard_string` tras leerlo para quedarnos solo con el delta del frame:
    //     así se puede insertar en la posición del CURSOR en vez de siempre al final, que es
    //     lo que haría fiarse del buffer acumulado del propio sistema.
    var _nuevo = keyboard_string;
    keyboard_string = "";

    if (_nuevo != "") {
        var _n = string_length(_nuevo);
        for (var _i = 1; _i <= _n; _i++) {
            var _c = string_char_at(_nuevo, _i);
            if (!__campo_texto_caracter_valido(_campo, _c)) { _campo.aviso = true; continue; }
            if (string_length(_campo.texto) >= _campo.max_longitud) { _campo.aviso = true; continue; }

            if (_campo.seleccion != -1) __campo_texto_borrar_seleccion(_campo);
            _campo.texto  = string_insert(_c, _campo.texto, _campo.cursor);
            _campo.cursor += 1;
        }
        // keyboard_lastchar es el último carácter FÍSICO tecleado — no filtra por sí solo
        // (es independiente de keyboard_string, según el propio manual), pero consumirlo aquí
        // evita que un backspace/atajo posterior lo vea como "sin procesar".
        keyboard_lastchar = "";
    }

    // 2 · Backspace / Delete — NUNCA el backspace interno de keyboard_string: al vaciarlo cada
    //     frame en el punto 1, ese backspace del sistema ya no tiene nada sobre lo que actuar.
    if (keyboard_check_pressed(vk_backspace)) {
        if (_campo.seleccion != -1) __campo_texto_borrar_seleccion(_campo);
        else if (_campo.cursor > 1) {
            _campo.texto  = string_delete(_campo.texto, _campo.cursor - 1, 1);
            _campo.cursor -= 1;
        }
    }
    if (keyboard_check_pressed(vk_delete)) {
        if (_campo.seleccion != -1) __campo_texto_borrar_seleccion(_campo);
        else if (_campo.cursor <= string_length(_campo.texto)) {
            _campo.texto = string_delete(_campo.texto, _campo.cursor, 1);
        }
    }

    // 3 · Cursor y selección — Shift+flecha extiende o crea la selección; flecha sola la cierra
    var _shift = keyboard_check(vk_shift);
    if (keyboard_check_pressed(vk_left) && _campo.cursor > 1) {
        if (_shift) { if (_campo.seleccion == -1) _campo.seleccion = _campo.cursor; }
        else _campo.seleccion = -1;
        _campo.cursor -= 1;
    }
    if (keyboard_check_pressed(vk_right) && _campo.cursor <= string_length(_campo.texto)) {
        if (_shift) { if (_campo.seleccion == -1) _campo.seleccion = _campo.cursor; }
        else _campo.seleccion = -1;
        _campo.cursor += 1;
    }

    // 4 · Pegar y copiar — el portapapeles de 08 · 12, enganchado por fin a un consumidor real
    var _ctrl = keyboard_check(vk_control) || keyboard_check(vk_lcontrol);
    if (_ctrl && keyboard_check_pressed(ord("V")) && clipboard_has_text()) {
        if (_campo.seleccion != -1) __campo_texto_borrar_seleccion(_campo);
        var _pegado  = clipboard_get_text();
        var _espacio = _campo.max_longitud - string_length(_campo.texto);
        if (string_length(_pegado) > _espacio) _pegado = string_copy(_pegado, 1, max(_espacio, 0));
        _campo.texto   = string_insert(_pegado, _campo.texto, _campo.cursor);
        _campo.cursor += string_length(_pegado);
    }
    if (_ctrl && keyboard_check_pressed(ord("C")) && _campo.seleccion != -1) {
        var _ini = min(_campo.cursor, _campo.seleccion);
        var _fin = max(_campo.cursor, _campo.seleccion);
        clipboard_set_text(string_copy(_campo.texto, _ini, _fin - _ini));
    }
}

/// @func campo_texto_dibujar(_campo, _px, _py)  — Draw GUI
function campo_texto_dibujar(_campo, _px, _py) {
    var _col_previo = draw_get_color();
    var _alto       = string_height(_campo.texto == "" ? "Ag" : _campo.texto);

    draw_text(_px, _py, _campo.texto);

    if (_campo.activo) {
        if (_campo.seleccion != -1) {
            var _ini = min(_campo.cursor, _campo.seleccion);
            var _fin = max(_campo.cursor, _campo.seleccion);
            var _x1  = _px + string_width(string_copy(_campo.texto, 1, _ini - 1));
            var _x2  = _px + string_width(string_copy(_campo.texto, 1, _fin - 1));
            draw_set_alpha(0.35);
            draw_rectangle_color(_x1, _py, _x2, _py + _alto, c_aqua, c_aqua, c_aqua, c_aqua, false);
            draw_set_alpha(1);
        }

        // Cursor parpadeante: medio segundo visible, medio invisible, desde que se activó
        // el campo — nunca `current_time mod 1000` a secas, o arranca a mitad de parpadeo
        // según lleve encendido el juego, en vez de siempre visible al entrar en el campo.
        if ((current_time - _campo.parpadeo_base) mod 1000 < 500) {
            var _x_cursor = _px + string_width(string_copy(_campo.texto, 1, _campo.cursor - 1));
            draw_line_width(_x_cursor, _py, _x_cursor, _py + _alto, 2);
        }
    }

    draw_set_color(_col_previo);
}
```

> ⚠️ **`keyboard_lastchar` no filtra `keyboard_string` por sí solo.** El manual las documenta
> como variables **independientes**: limpiar `keyboard_lastchar` no borra ni retiene nada de
> `keyboard_string`. Por eso el filtrado real ocurre carácter a carácter sobre el *delta* de
> `keyboard_string` (punto 1 de `campo_texto_actualizar`); `keyboard_lastchar` solo se usa para
> no dejarlo "sin consumir" de cara a otro código que lo esté mirando.
>
> 🔺 **Vaciar `keyboard_string` cada frame es la clave de todo el widget.** Es lo que permite
> insertar el texto tecleado en la posición del **cursor** en vez de siempre al final, y es lo
> que hace que el backspace/delete propios (punto 2) sean necesarios: el borrado automático que
> el manual describe para `keyboard_string` actúa sobre el buffer del sistema, que aquí se
> vacía cada frame antes de que ese borrado tenga nada que morder.
>
> 💡 **CJK/IME**: activa `keyboard_virtual_show()` al llamar a `campo_texto_activar()` si el
> campo debe admitir japonés/chino/coreano — ver
> [01 · 12, «IME y entrada de texto no ASCII (CJK)»](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md).
> El widget no necesita ningún cambio: `keyboard_string` es la misma variable en los dos casos.

#### m) Confirmación (Sí/No, con «No» por defecto)

> **Hueco cerrado.** `04 · 41 §3.4.4` ya resolvía la confirmación de «¿Seguro que quieres
> salir?» y señalaba explícitamente que la biblioteca «todavía no tiene un widget de
> confirmación reutilizable de propósito general». Este componente lo es —
> [`scr_ui_confirmar.gml`](../06%20-%20Assets%20y%20Scripts/scr_ui_confirmar.gml), verificado
> con `buscar.py`— y sirve para salir, sobrescribir una ranura de guardado (componente n,
> justo debajo), borrar una partida o restablecer los ajustes de `04 · 25`. La regla que aplica
> siempre es la misma: **toda acción destructiva confirma, y «No» empieza con el foco**
> ([§2.1, regla 3](#21-el-mapa-de-pantallas-se-dibuja-antes-de-programar-nada)).

```gml
/// obj_pausa (o cualquier objeto persistente que gestione la UI) · Create
confirmar_configurar_textos(txt("comun_si"), txt("comun_no"));   // una vez, con la localización ya cargada

/// Step — antes que cualquier otro input de la pantalla lea la tecla de aceptar/cancelar
confirmar_step();

/// Draw GUI — por encima de todo lo demás
confirmar_dibujar();

/// En cualquier sitio donde haga falta confirmar algo:
confirmar_abrir(txt("pausa_confirmar_salir"),
    function() { reanudar_de_verdad(); ir_a_escena(rm_menu_principal); },   // "Sí"
    undefined);                                                            // "No": solo cierra
```

> ⚠️ **No usa `show_question()`**: bloquea el juego en un bucle cerrado y se ignora fuera de
> Windows salvo en modo debug (`01 · 15 §12`). Es un estado más de tu propia máquina, como el
> resto de esta biblioteca.

#### n) Ranura de guardado (metadatos, miniatura y «guardando…»)

> **Hueco cerrado.** La ronda 2 de auditoría (`feedback-ux.md`, hallazgo K3) ya señalaba que
> faltaba una ficha de ranura con metadatos; `_indice/auditorias/r5-juego-completo.md`
> (hallazgo B4b) confirmó que seguía sin existir. `06 · scr_save_load.gml` ya soporta un
> tercer argumento `_meta` en `save_game()` y las funciones `save_thumbnail_*` — este
> componente es la pantalla que los usa.

**El catálogo de metadatos que le pasas a `save_game()`.** `_meta` es un struct libre — pon lo
que tu juego necesite mostrar (zona/room, tiempo jugado, porcentaje completado…):

```gml
/// En el punto donde ya guardas la partida (checkpoint, autoguardado, guardado manual)
/// Verificado: room_get_name, date_second_span, date_current_datetime

var _meta = {
    zona          : room_get_name(room),
    tiempo_jugado : global.tiempo_jugado_segundos,   // el propio juego lleva la cuenta (abajo)
    porcentaje    : calcular_porcentaje_completado(),   // función TUYA, específica del juego
};
guardado_con_indicador("slot1", _datos_de_la_partida, _meta);
```

```gml
/// obj_arranque (o donde ya lleves el reloj de partida) · Create
global.tiempo_jugado_segundos = 0;
global.tiempo_jugado_desde    = date_current_datetime();

/// Step — solo suma mientras NO está pausado (usa el mismo global.pausado de 04 · 00 §5)
if (!global.pausado) {
    global.tiempo_jugado_segundos += date_second_span(global.tiempo_jugado_desde, date_current_datetime());
    global.tiempo_jugado_desde = date_current_datetime();
}
```

**El indicador «guardando…», sin parpadear en un guardado casi instantáneo.** Mismo principio
que la duración mínima de la pantalla de carga
([04 · 41 §1.2](../04%20-%20Recetas%20por%20género/41%20-%20Transiciones%2C%20carga%20y%20pausa.md#12-una-barra-de-carga-honesta-mide-lo-que-carga-una-barra-decorativa-es-peor-que-nada)):

```gml
/// Verificado: current_time

#macro GUARDANDO_INDICADOR_MIN_MS 500

/// @func guardado_con_indicador(_slot, _datos, _meta)
/// @desc Guarda y deja el indicador visible un mínimo de tiempo (abajo), para que un guardado
///       de un JSON pequeño (unos pocos ms) no se vea como un parpadeo de un solo frame.
function guardado_con_indicador(_slot, _datos, _meta) {
    global.guardando_activo = true;
    global.guardando_desde  = current_time;
    return save_game(_slot, _datos, _meta);
}

/// Draw GUI, en cualquier pantalla donde pueda dispararse un guardado
if (global.guardando_activo) {
    if (current_time - global.guardando_desde < GUARDANDO_INDICADOR_MIN_MS) {
        draw_text(display_get_gui_width() - 140, display_get_gui_height() - 30, txt("comun_guardando"));
    } else {
        global.guardando_activo = false;
    }
}
```

**La ficha de ranura, con miniaturas cargadas UNA vez, no cada frame.** Cargar un sprite desde
disco en cada Draw sería el mismo error que ya marca `13/05 §4` para las surfaces: trabajo
repetido que sobra. Se carga en `Create` de la pantalla de selección y se libera en `Clean Up`:

```gml
/// obj_seleccion_partida · Create
/// Verificado: save_list, save_thumbnail_load, array_create, array_length

ranuras    = save_list(["slot1", "slot2", "slot3"]);
miniaturas = array_create(array_length(ranuras), undefined);

for (var _i = 0; _i < array_length(ranuras); _i++) {
    if (ranuras[_i].existe) { miniaturas[_i] = save_thumbnail_load(ranuras[_i].slot); }
}

/// obj_seleccion_partida · Clean Up
/// Verificado: sprite_exists, sprite_delete
for (var _i = 0; _i < array_length(miniaturas); _i++) {
    if (miniaturas[_i] != undefined && sprite_exists(miniaturas[_i])) { sprite_delete(miniaturas[_i]); }
}
```

```gml
/// obj_seleccion_partida · Draw GUI — una fila por ranura
/// Verificado: draw_sprite_ext, draw_text, string, is_struct, struct_exists

for (var _i = 0; _i < array_length(ranuras); _i++) {
    var _r  = ranuras[_i];
    var _fy = _y0 + _i * 100;

    if (!_r.existe) { draw_text(_x0, _fy, txt("ranura_vacia")); continue; }

    if (miniaturas[_i] != undefined) { draw_sprite_ext(miniaturas[_i], 0, _x0, _fy, 0.25, 0.25, 0, c_white, 1); }

    draw_text(_x0 + 90, _fy, _r.fecha);

    if (is_struct(_r.meta)) {
        if (struct_exists(_r.meta, "zona"))          { draw_text(_x0 + 90, _fy + 18, _r.meta.zona); }
        if (struct_exists(_r.meta, "tiempo_jugado"))  { draw_text(_x0 + 90, _fy + 36, tiempo_jugado_formatear(_r.meta.tiempo_jugado)); }
        if (struct_exists(_r.meta, "porcentaje"))     { draw_text(_x0 + 90, _fy + 54, string(_r.meta.porcentaje) + "%"); }
    }
}
```

```gml
// Verificado: floor, string, string_format, string_replace_all

/// @func tiempo_jugado_formatear(_segundos)
/// @desc Como tiempo_texto() (§3.5h), pero con HORAS: ese formatea el cronómetro de una
///       sesión o partida (segundos), este el tiempo ACUMULADO de toda la partida guardada
///       (que sí puede pasar de una hora). No lo sustituye: le añade el rango que falta.
/// @returns {String}  "H:MM:SS" si dura una hora o más, "MM:SS" si no.
function tiempo_jugado_formatear(_segundos) {
    var _h = floor(_segundos / 3600);
    var _m = floor(_segundos / 60) mod 60;
    var _s = floor(_segundos) mod 60;
    var _txt = (_h > 0)
        ? string(_h) + ":" + string_format(_m, 2, 0) + ":" + string_format(_s, 2, 0)
        : string_format(_m, 2, 0) + ":" + string_format(_s, 2, 0);
    return string_replace_all(_txt, " ", "0");   // string_format rellena con espacios, no ceros (§3.5h)
}
```

**Sobrescribir y borrar, con el widget de confirmación de arriba — nunca en silencio:**

```gml
/// Verificado: save_exists (06 · scr_save_load.gml)

/// @func ranura_pedir_sobrescribir(_slot, _datos, _meta)
/// @desc Si la ranura está vacía, guarda directo. Si ya tiene partida, confirma primero.
function ranura_pedir_sobrescribir(_slot, _datos, _meta) {
    if (!save_exists(_slot)) { guardado_con_indicador(_slot, _datos, _meta); return; }
    confirmar_abrir(txt("ranura_sobrescribir_pregunta"),
        function() { guardado_con_indicador(_slot, _datos, _meta); },
        undefined);
}

/// @func ranura_pedir_borrado(_slot, _al_borrar)
/// @desc _al_borrar es TUYA: normalmente, recargar la lista de ranuras de §Create de arriba.
function ranura_pedir_borrado(_slot, _al_borrar) {
    confirmar_abrir(txt("ranura_borrar_pregunta"),
        function() { delete_save(_slot); _al_borrar(); },
        undefined);
}
```

> 🔺 **`delete_save()` ya borra la miniatura sola** (`06 · scr_save_load.gml`, actualizado):
> no hace falta llamar a `save_thumbnail_delete()` aparte al borrar una partida entera.

### 3.6 Tipografía: bitmap, TTF y SDF

| | **Fuente de sprite (bitmap)** | **TTF/OTF del IDE** | **SDF** |
|---|---|---|---|
| Cómo se hace | `font_add_sprite_ext()` o el editor de fuentes | Se importa el `.ttf` en el IDE | Se activa en el editor, o `font_enable_sdf()` sobre una fuente cargada con `font_add()` |
| Escalado | ❌ Se rompe fuera de múltiplos enteros | 🟡 Se emborrona | ✅ Nítida a cualquier escala |
| Rotación | ❌ Fea | 🟡 Regular | ✅ Limpia |
| Contorno / brillo / sombra | Hay que dibujarlo tú | Hay que dibujarlo tú | ✅ `font_enable_effects()` |
| Coste de textura | Bajo | Medio | Medio-alto (crece con `font_sdf_spread`) |
| Estética píxel | ✅ Perfecta | ❌ | ❌ (suaviza los bordes) |
| Idiomas con muchos glifos | ❌ Inviable a mano | ✅ | ✅ |

Reglas de decisión:

- **Juego de píxel a resolución fija** → fuente de sprite. Es la única que respeta la rejilla.
- **Juego HD, UI que escala, títulos grandes, texto que se anima** → **SDF**.
- **Texto muy pequeño y muy denso** (una tabla de estadísticas) → TTF normal: el SDF con
  spread alto pierde precisión en tamaños diminutos.

```gml
/// Cargar una fuente de archivo y activarle SDF en runtime
/// Verificado: font_add, font_enable_sdf, font_sdf_spread, font_enable_effects
global.fnt_titulo = font_add("Inter-Bold.ttf", 48, false, false, 32, 255);
font_enable_sdf(global.fnt_titulo, true);
font_sdf_spread(global.fnt_titulo, 12);          // rango 2-32, por defecto 8
```

> 🔺 **`font_enable_sdf()` solo funciona con fuentes añadidas con `font_add()` desde archivo.**
> No sirve con fuentes de sprite ni con las importadas en el IDE por código, y **no funciona
> en HTML5** (ahí el SDF se activa desde el editor de fuentes). Detalle completo en
> [08 · 03](../08%20-%20Referencia%20GML%20completa/03%20-%20Texto%20y%20fuentes.md).

**Tamaño y espaciado**

- El *kerning* y el interletraje se ajustan en el **editor de fuentes** del IDE (rango de
  caracteres, separación, márgenes del glifo). GameMaker no expone un `font_set_kerning`.
- El interlineado sí lo controlas al dibujar: es el argumento `sep` de `draw_text_ext()`.
  `-1` usa el alto de la «M» de la fuente. Para texto de UI, `sep` un 20-30 % mayor que el
  alto de línea mejora mucho la legibilidad.
- **Deja crecer el texto un 30 %.** El alemán y el ruso son bastante más largos que el
  español; el turco y el finés, más aún. Si tu botón mide exactamente lo que mide
  «Continuar», reventará en la primera traducción.

**Alfabetos no latinos**

Ruso, griego, japonés, chino y coreano no caben en el rango 32-255 por defecto. Hay que
añadir el rango de glifos que uses, y para CJK eso significa **miles**. La estrategia y las
trampas están en
[04 · 21 §4](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md).

> ⚠️ Las constantes `*_CHARSET` (`RUSSIAN_CHARSET`, `SHIFTJIS_CHARSET`, `HANGEUL_CHARSET`,
> `GREEK_CHARSET`…) **existen en el runtime pero no están en `GmlSpec.xml` ni documentadas en
> el manual**: Feather no las autocompleta y no hay página oficial que describa su
> comportamiento con `font_add()`. Existen, no son una invención, pero **pruébalas en tu
> proyecto antes de apoyar la localización en ellas**. Contexto en
> [08 · 20](../08%20-%20Referencia%20GML%20completa/20%20-%20Lo%20que%20el%20manual%20no%20documenta.md).

### 3.7 Accesibilidad: solo lo que es específico de la UI

El sistema completo (daltonismo, subtítulos, *reduce motion*, accesibilidad motriz, el struct
`global.a11y`) está en
[04 · 27](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) y no lo repito. Lo que
sí es responsabilidad **del layout**:

1. **Si hay escala de texto configurable, el layout tiene que medirse, no fijarse.** Un panel
   cuyo alto sale de `string_height_ext()` × `escala_ui()` aguanta el 150 %. Uno con
   `alto = 48` no. Esta es la razón real por la que las funciones de medida están en este
   documento.
2. **Prueba tu UI al 150 % antes de darla por hecha.** Es el mismo *stress test* que la
   traducción al alemán, y descubre los mismos bugs.
3. **El foco tiene que verse sin color.** Un recuadro o una flecha, no solo un tono distinto:
   el foco es el elemento más importante de la pantalla para quien juega con mando y para
   quien no distingue tu amarillo de tu blanco.
4. **Los iconos de estado llevan forma además de color.** Veneno no es «verde»: es «verde con
   forma de gota». Igual que en el mundo ([04 · 27 §1](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md)),
   pero en la HUD se olvida más porque los iconos son pequeños.
5. **Si el jugador puede reasignar controles, los iconos de la UI reflejan la asignación real**
   ([04 · 25 §5](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md)).
   Un tutorial que dice «pulsa E» cuando el jugador ha puesto F es peor que no decir nada.

### 3.8 Juice de UI: tres cosas y ni una más

La teoría del juice, el easing, el screen shake y el *hit stop* están en
[04 · 15](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md), y el sistema de
tweens listo para copiar es
[`scr_tween.gml`](../06%20-%20Assets%20y%20Scripts/scr_tween.gml). Aplicado a la interfaz se
reduce a tres cosas:

**1. Los paneles entran y salen, no aparecen.**

```gml
/// Abrir una pantalla: el panel sube con rebote mientras aparece
/// Requiere scr_tween.gml y scr_math_util.gml (funciones de easing)
panel_desplaz = 120;
panel_alfa    = 0;
tween_to(self, { panel_desplaz: 0 }, 0.28, ease_out_back);
tween_to(self, { panel_alfa: 1    }, 0.18, ease_out_quad);

/// Cerrarla: más rápido que abrirla, siempre
tween_to(self, { panel_desplaz: 90, panel_alfa: 0 }, 0.16, ease_in_quad, function() {
    instance_destroy();
});
```

> 💡 **Salir siempre más rápido que entrar.** Entrada 250-300 ms, salida 150-180 ms. Una
> transición de cierre lenta se percibe como lentitud del juego; una de apertura lenta, como
> elegancia. Y **nada de UI por encima de 350 ms**: por ahí empieza a molestar.

**2. Cuatro sonidos, y solo cuatro.**

| Sonido | Cuándo |
|---|---|
| `snd_ui_foco` | El foco entra en un elemento nuevo (nunca cada frame) |
| `snd_ui_aceptar` | Confirmación |
| `snd_ui_cancelar` | Volver atrás. Distinto del de aceptar, y más grave |
| `snd_ui_error` | Acción no disponible |

Un menú con esos cuatro suena profesional. Uno con doce suena a caos.

**3. Los números tiemblan cuando cambian.** Ya está en `marcador_dibujar()` (§3.5h): una
sacudida de 4-6 px que decae en 0,15 s. Es la diferencia entre un contador y una recompensa.

> ⚠️ **Todo esto pasa por `global.a11y.reduce_motion`.** Con esa opción activa: sin temblor,
> sin sacudida, transiciones a la mitad de duración o instantáneas. Ver
> [04 · 27 §3](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md).

### 3.9 Cuándo no lo montes a mano

Si tu juego necesita **muchas** pantallas con estructura (pestañas, listas anidadas, tablas,
ventanas movibles), montarlo con las funciones de este documento se convierte en un trabajo
a tiempo completo. Hay librerías maduras y con licencia MIT en el
[catálogo de código descargado](../11%20-%20Código%20descargado/_CATALOGO.md), sección
*Interfaz de usuario (UI/HUD)*:

| Librería | Enfoque | Para qué encaja |
|---|---|---|
| **YUI** | Declarativa, con lenguaje de marcado propio inspirado en HTML/CSS | Pantallas complejas que cambian mucho durante el desarrollo |
| **Bento** (JujuAdams) | Layout declarativo, framework completo | HUD y menús de un juego comercial |
| **gooey** | Basada en sprites: botones, paneles, listas, ventanas | Interfaz con arte propio, sin pelearse con el layout |
| **Emu** (DragoniteSpam) | Tipo *Windows Forms* | **Herramientas y editores internos**, no la UI del jugador |
| **Scribble** | Texto rico, formato en línea, efectos | Cualquier juego con diálogo o texto con estilo |

> 💡 **La decisión honesta**: más de tres pantallas con listas y pestañas → una librería sale
> rentable. Un HUD de cinco elementos y dos menús → a mano, con lo de este documento, es más
> rápido y sin dependencias.

---

## 4 · Checklist de UI antes de publicar

> Esta es la lista de la UI en concreto: layout, interacción, feedback, accesibilidad. No
> repite el checklist de «juego completo» —
> [04 · 00](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md#el-checklist-de-juego-completo)
> es el índice maestro (splash, menú, guardado, cierre…) y remite aquí para el detalle de UI
> que sigue. Compara contra los dos antes de decir que un juego está terminado.

**Legibilidad y layout**

- [ ] Ningún texto por debajo de **26 px equivalentes a 1080p** si el juego sale en consola
      (18 px en escritorio).
- [ ] Ningún texto se dibuja directamente sobre el mundo: todo lleva panel, contorno o sombra.
- [ ] Toda la UI está dentro de la zona segura del 5 % en consola.
- [ ] La UI se ha probado en **16:9, 16:10, 21:9 y 4:3**, y en vertical si el juego es móvil.
- [ ] La UI se ha probado con la **escala de texto al 150 %**.
- [ ] La UI se ha probado con la **traducción más larga** (alemán o ruso).
- [ ] Ninguna coordenada de UI está escrita a pelo: todo pasa por `ancla()` o por Flexpanels.

**Interacción**

- [ ] **Todo el juego se puede terminar solo con mando**, sin tocar el ratón ni una vez.
- [ ] **Todo el juego se puede terminar solo con teclado.**
- [ ] Al abrir cualquier pantalla hay un elemento con el foco, y ese foco **se ve**.
- [ ] Los iconos de botón cambian solos al cambiar de dispositivo (§2.3).
- [ ] Los iconos reflejan el **rebinding** del jugador, no la asignación por defecto.
- [ ] Cada pantalla tiene una salida visible, y siempre con el mismo botón.
- [ ] Toda acción destructiva pide confirmación, con «No» por defecto (componente m,
      `scr_ui_confirmar.gml` — no un diálogo distinto cada vez).
- [ ] La repetición al mantener una dirección funciona (0,4 s + 0,1 s) y no se dispara sola
      con un stick desgastado.

**Feedback**

- [ ] Todos los controles tienen los **cuatro** estados: normal, foco, pulsado, inactivo.
- [ ] Ningún botón inactivo desaparece: se ve gris y **dice por qué**.
- [ ] Los sonidos de UI van en el **cambio** de estado, no cada frame.
- [ ] Existen los cuatro sonidos: foco, aceptar, cancelar, error.
- [ ] Todo cambio de valor importante tiene una respuesta visual (barra fantasma, temblor).
- [ ] Nada de la UI tarda más de **350 ms** en responder ni en animarse.

**Accesibilidad y robustez**

- [ ] Nada se comunica **solo** con color (§3.7 y [04 · 27](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md)).
- [ ] `reduce_motion` apaga temblores, sacudidas y flashes de la UI.
- [ ] Las surfaces de la UI (minimapa, retratos, previsualizaciones) se comprueban con
      `surface_exists()` cada frame y se liberan en el Clean Up.
- [ ] El estado de dibujo (`halign`, `valign`, `color`, `alpha`, `font`) se restablece al
      salir de cada bloque de UI.
- [ ] El juego se ha visto **desde tres metros** en una tele de verdad, no solo en el monitor.

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Qué se ve | La causa real | La corrección |
|---|---|---|---|
| **El texto se sale del panel** | La última palabra desaparece por el borde | El panel tiene tamaño fijo y el texto no | Dimensiona el panel con `string_width_ext()` / `string_height_ext()` usando **los mismos** `sep` y `w` que luego pasas a `draw_text_ext()` |
| **La UI escalada sale borrosa** | Bordes sucios, texto emborronado | Escala no entera con filtrado lineal, o texto bitmap escalado a 1,37× | Escala a **múltiplos enteros** en juegos de píxel, o pasa el texto a **SDF** (§3.6). `gpu_set_tex_filter(false)` para el arte de píxel |
| **Botón sin estado inactivo** | El jugador pulsa y no pasa nada | Solo se codificaron dos estados | Los cuatro estados de §1.5, y un `motivo` que se enseñe al insistir |
| **El menú no se puede usar con mando** | Hay que soltar el mando para tocar una opción | La UI se escribió pensando solo en el ratón, con `point_in_rectangle` como única entrada | Un índice de foco desde el primer día. El ratón **también** mueve el foco; no es un camino aparte |
| **La HUD tapa el juego** | El jefe está detrás de la barra de vida | La HUD se diseñó sobre una captura vacía | Diseña sobre una captura del **momento más cargado** del juego, y aplica §1.10 |
| **El HUD se descoloca en pantalla completa** | Todo salta al pulsar F11 | Coordenadas basadas en `window_get_width()`, o `display_set_gui_maximise()` mal entendida | `display_get_gui_width()` siempre, y recuerda que el reset es `display_set_gui_maximise(-1, -1)`, no la llamada sin argumentos |
| **El texto del mundo sale amarillo y centrado** | Colores que se «contagian» entre objetos | `draw_set_color` / `draw_set_halign` son estado global y alguien no los restableció | Restablece al final de cada bloque de dibujo |
| **El ratón no coincide con los botones** | Hay que pinchar «al lado» del botón | Se comparó `mouse_x` (coordenadas de room) con coordenadas de GUI | `device_mouse_x_to_gui(0)` / `device_mouse_y_to_gui(0)` en Draw GUI |
| **El minimapa desaparece al minimizar** | Un hueco negro tras un alt-tab | La surface se volatilizó y nadie lo comprobó | `if (!surface_exists(...)) recrear` **cada** Step |
| **El sonido de menú es una metralleta** | *bip-bip-bip-bip* al pasar el ratón | El sonido está en `if (encima)`, sin comparar con el estado anterior | Dispara en el cambio: `if (estado == "foco" && previo == "normal")` |
| **El objeto del inventario se pierde** | Un objeto desaparece al arrastrarlo mal | Se destruye al coger y se recrea al soltar | Sácalo de la celda y guárdalo en `cogido`; un soltar inválido lo devuelve |
| **Los números bailan** | El contador se mueve de lado al cambiar de dígito | Fuente proporcional | Fuente de sprite monoespaciada para números, o `fa_right` |
| **La barra de vida no se siente** | El jugador no sabe que le han dado | La barra baja de golpe y sin más | Barra fantasma + temblor (§3.5b) |
| **Todo se dibuja aunque no se vea** | 200 fps se convierten en 60 | Se dibuja la lista completa, o el minimapa se repinta cada frame | `continue` fuera de la ventana ([04 · 18](../04%20-%20Recetas%20por%20género/18%20-%20Menús%20con%20scroll%20y%20navegación.md)) y el patrón `sucio` (§3.5g) |

---

## Ver también

**Dentro de la biblioteca**

- [02 · 04 — UI Layers y Flexpanels](../02%20-%20Novedades%202026/04%20-%20UI%20Layers%20y%20Flexpanels.md) — el sistema visual de 2026, con el orden de dibujado y las funciones de runtime
- [04 · 18 — Menús con scroll y navegación](../04%20-%20Recetas%20por%20género/18%20-%20Menús%20con%20scroll%20y%20navegación.md) — listas largas, scroll suavizado y barra de desplazamiento
- [04 · 25 — Menú de opciones y ajustes](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md) — sliders, toggles, dropdowns, persistencia y rebinding
- [04 · 27 — Accesibilidad](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) — daltonismo, subtítulos, escala de texto, reduce motion
- [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md) — el texto flotante completo, easing y el resto del juice
- [04 · 10 — Visual Novel y narrativa](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md) — la caja de diálogo, el typewriter y el backlog
- [04 · 21 — Localización e idiomas](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md) — alfabetos no latinos y el crecimiento del texto
- [04 · 00 — Anatomía de un juego completo](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md) — el arco de pantallas, la pausa y el fundido entre salas
- [01 · 11 — Dibujo y renderizado](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md) — Draw GUI frente a Draw, surfaces, batching
- [01 · 12 — Input: teclado, ratón y gamepad](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md) — constantes, zonas muertas, gestos y la librería Input
- [01 · 10 — Rooms, capas, cámaras y viewports](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md) — de dónde salen las coordenadas que convierte `mundo_a_gui()`
- [03 · 35 — DragoniteSpam: el evento Draw GUI](../03%20-%20Cursos%20%28YouTube%29/35%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Evento%20Draw%20GUI.md) — la introducción, si esto te queda grande
- [07 · 18 — Scribble, texto rico](../07%20-%20Ecosistema/18%20-%20Scribble%20-%20texto%20rico%20%28guía%20en%20español%29.md) · [10 · 10 — Input y Scribble](../10%20-%20Cursos%20en%20español/10%20-%20Herramientas%20de%20la%20comunidad%20-%20Input%20y%20Scribble.md)
- [08 · 03 — Texto y fuentes](../08%20-%20Referencia%20GML%20completa/03%20-%20Texto%20y%20fuentes.md) · [08 · 05 — Superficies](../08%20-%20Referencia%20GML%20completa/05%20-%20Superficies.md) · [08 · 20 — Lo que el manual no documenta](../08%20-%20Referencia%20GML%20completa/20%20-%20Lo%20que%20el%20manual%20no%20documenta.md)
- [08 · 12 — Strings](../08%20-%20Referencia%20GML%20completa/12%20-%20Strings.md#portapapeles) — `clipboard_get_text`/`has_text`/`set_text` y las funciones de manipulación que usa `campo_texto_actualizar()` (§3.5l)
- [04 · 11 — Arcade y juegos de un botón](../04%20-%20Recetas%20por%20género/11%20-%20Arcade%20y%20juegos%20de%20un%20botón.md) — la alta de highscore con `keyboard_lastchar`, el caso simple que §3.5l generaliza sin repetirlo
- [`scr_tween.gml`](../06%20-%20Assets%20y%20Scripts/scr_tween.gml) · [`scr_math_util.gml`](../06%20-%20Assets%20y%20Scripts/scr_math_util.gml) — tweens y easing listos para copiar
- [`scr_ui_confirmar.gml`](../06%20-%20Assets%20y%20Scripts/scr_ui_confirmar.gml) — el widget de confirmación del componente m)
- [`scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml) — `save_game()`, `save_list()` y `save_thumbnail_*` que usa el componente n)
- [04 · 57 — Selección de nivel y capítulo](../04%20-%20Recetas%20por%20género/57%20-%20Selección%20de%20nivel%20y%20capítulo.md) — otra pantalla de «elegir entre varias opciones con estado», con el mismo criterio de estados visuales del componente n)
- [11 · Catálogo de código descargado](../11%20-%20Código%20descargado/_CATALOGO.md) — las librerías de UI de la comunidad
- [05 · 04 — Convenciones y estilo GML](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md)

**Bancos de referencia visual** (para mirar antes de diseñar, no para copiar)

- **Game UI Database** — 1 911 juegos y 76 674 capturas catalogadas por tipo de pantalla y por
  elemento. Es la herramienta que usa el oficio.
- **Interface In Game** — 399 juegos y 16 147 capturas y clips, con la clasificación por
  elemento (menú, HUD, inventario, ajustes…).

---

## Fuentes

Consultadas y abiertas el **2026-09-06**.

**Diseño y teoría**

- Erik Fagerholt y Magnus Lorentzon, *Beyond the HUD — User Interfaces for Increased Player
  Immersion in FPS Games*, tesis de máster, Chalmers University of Technology, 2009 (en
  colaboración con EA DICE). PDF completo, 124 páginas:
  <https://publications.lib.chalmers.se/records/fulltext/111921.pdf> ·
  ficha: <https://odr.chalmers.se/items/d5fe6889-4cc6-49c2-ba56-0d759e2f37eb>
- Dino Ignacio (Visceral Games / EA), *Crafting Destruction: The Evolution of the Dead Space
  User Interface*, **GDC 2013**. <https://gdcvault.com/play/1017723/Crafting-Destruction-The-Evolution-of>
  · vídeo: <https://www.youtube.com/watch?v=pXGWJRV1Zoc>
- Celia Hodent, *The Gamer's Brain: How Neuroscience and UX Can Impact Design*, **GDC 2015**
  (<https://gdcvault.com/play/1022310>); *Part 2: UX of Onboarding and Player Engagement*, GDC
  2016 (<https://gdcvault.com/play/1023231>); *Part 3: The UX of Engagement and Immersion*, GDC
  2017 (<https://gdcvault.com/play/1024055>).
- David Candland (Bungie), *Tenacious Design and The Interface of Destiny*, GDC 2016 ·
  Christian Savoie (Massive/Ubisoft), *Lessons Learned Creating UI for The Division*, GDC 2017 ·
  Vidhi Shah (Blackbird), *Cutting Apart The Diegetic Interface of Hardspace: Shipbreaker*,
  GDC 2021.
- **Game UI Database** (Edd Coates) — <https://www.gameuidatabase.com/>
- **Interface In Game** — <https://interfaceingame.com/>

**Legibilidad, zonas seguras y accesibilidad**

- Microsoft, *Xbox Accessibility Guidelines — 101: Text Display*:
  <https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/101>
  («Font size should equal or exceed: 26 px at 1080p / 52 px at 4K»).
- Microsoft, *Designing for Xbox and TV* (10-foot experience, márgenes del 5 %, 48/27 epx
  sobre 960×540): <https://learn.microsoft.com/en-us/windows/apps/design/devices/designing-for-tv>
- Google, *Android TV — Layouts* (mismos 48 dp / 27 dp de margen):
  <https://developer.android.com/design/ui/tv/guides/styles/layouts>
- EBU, *Recommendation R 95 — Safe Areas for 16:9 Television Production*, v1.1, junio de 2017
  (*graphics safe* 5 %, *action safe* 3,5 %): <https://tech.ebu.ch/docs/r/r095.pdf>
- Apple, *Human Interface Guidelines — Layout* (safe areas; tvOS: 60 puntos arriba y abajo,
  80 a los lados): <https://developer.apple.com/design/human-interface-guidelines/layout>
- W3C, *Web Content Accessibility Guidelines (WCAG) 2.2* — contraste 4,5:1 / 3:1 y el umbral
  de tres destellos por segundo: <https://www.w3.org/TR/WCAG22/>

**GameMaker (manual oficial LTS 2026, espejo local en `09 - Manual oficial/manual-lts-2026-es/`)**

- *Draw Events* (Draw GUI Begin / Draw GUI / Draw GUI End, espacio de coordenadas):
  <https://manual.gamemaker.io/lts/es/The_Asset_Editors/Object_Properties/Draw_Events.htm>
- `display_set_gui_size`:
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Cameras_And_Display/display_set_gui_size.htm>
- `display_set_gui_maximise`:
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Cameras_And_Display/display_set_gui_maximise.htm>
- *Nine Slices* (editor de sprites):
  <https://manual.gamemaker.io/lts/es/The_Asset_Editors/Sprite_Properties/Nine_Slices.htm>
- *Nine Slice Struct* (campos y constantes de `tilemode`):
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Nine_Slice_Struct.htm>
- `sprite_nineslice_create`:
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Manipulation/sprite_nineslice_create.htm>
- `device_mouse_x_to_gui`:
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Game_Input/Device_Input/device_mouse_x_to_gui.htm>
- `draw_healthbar`:
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Drawing/Basic_Forms/draw_healthbar.htm>
- *UI Layers* y *UI Layers At Runtime*:
  <https://manual.gamemaker.io/lts/en/The_Asset_Editors/Room_Properties/UI_Layers.htm> ·
  <https://manual.gamemaker.io/lts/en/The_Asset_Editors/Room_Properties/UI_Layers_At_Runtime.htm>
- *Flex Panels* (basado en Yoga; solo calculan layout, no dibujan):
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Flex_Panels/Flex_Panels.htm>
- *Expressions And Operators* (`div`, `mod`):
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Overview/Expressions_And_Operators.htm>
- `mouse_wheel_up` / `mouse_wheel_down` (zoom del mapa completo, §3.5j):
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Game_Input/Mouse_Input/mouse_wheel_up.htm>
- `point_distance` (foco del mapa completo por cercanía, §3.5j):
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Angles_And_Distance/point_distance.htm>
- `method_get_self` (recuperar el contexto de un botón de la tienda, §3.5k):
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Variable_Functions/method_get_self.htm>
- `keyboard_string` / `keyboard_lastchar` (campo de texto, §3.5l):
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Game_Input/Keyboard_Input/keyboard_string.htm> ·
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Game_Input/Keyboard_Input/keyboard_lastchar.htm>
- `clipboard_get_text` / `clipboard_has_text` / `clipboard_set_text` (pegar y copiar, §3.5l):
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/clipboard_get_text.htm>
- `string_insert` / `string_delete` / `string_copy` (edición del texto, §3.5l):
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Strings/string_insert.htm>

**Correcciones que salieron de verificar y conviene no perder**

- ⚠️ **No existe ninguna función de *safe area* ni de notch en GameMaker.** Comprobado sobre
  el manual completo y sobre el catálogo de símbolos del runtime 2026.0.0.23. `display_get_dpi_x()`
  y `display_get_dpi_y()` sí existen, pero informan de densidad de píxel.
- ⚠️ **La taxonomía de Fagerholt y Lorentzon tiene seis categorías, no cuatro.** La versión de
  cuatro cuadrantes que circula es una simplificación posterior.
- ⚠️ **«The Cost of Ignoring UX» no existe** como charla de GDC ni de ningún evento del sector,
  pese a citarse a menudo. Lo más cercano por tema es *Dark Patterns: How Good UX Can Be Bad
  UX* (GDC 2017), que es otra charla.
- ⚠️ **La regla de *title safe* al 80 % está desactualizada**: viene de las recomendaciones
  SMPTE de los años sesenta para 4:3. En 16:9 el estándar vigente es el 5 % de margen.
- ⚠️ **`display_set_gui_maximise()` sin argumentos NO restablece la GUI**: la maximiza. El
  reset es `display_set_gui_maximise(-1, -1)`.
- ⚠️ Las constantes `*_CHARSET` existen en el runtime pero **no están en `GmlSpec.xml` ni en el
  manual**: Feather no las reconoce. Existen, pero pruébalas antes de depender de ellas.
