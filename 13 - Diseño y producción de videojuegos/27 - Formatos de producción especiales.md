# 27 · Formatos de producción especiales

> Cinco encargos que no son «un género de videojuego», sino un **formato de producción**: el
> mismo motor, las mismas mecánicas que ya sabes construir, pero con una restricción externa que
> cambia el diseño — no hay teclado, el cliente pone el temario, la sesión dura tres minutos, el
> jugador es menor de edad, o la partida la ve más gente de la que la juega. Ninguno de los
> cinco tiene receta propia en `04 - Recetas por género/` porque no son géneros: son **contextos
> de entrega** que se le pueden superponer a cualquier género ya cubierto.
>
> **Qué NO cubre este documento, y dónde está.** El diseño de mecánicas, niveles, economía y
> dificultad de un juego «normal» — todo `13` de arriba abajo, empezando por
> [13 · 01](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md).
> El marco legal general (privacidad, edades, impuestos) —
> [13 · 11 §9](./11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md#9--legal-y-administrativo-mínimo).
> La accesibilidad transversal (daltonismo, subtítulos, motriz) —
> [04 · 27](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md). Como en
> [04 · 45](../04%20-%20Recetas%20por%20género/45%20-%20Géneros%20sin%20receta%20propia%20-%20sigilo%2C%20horror%2C%20táctica%2C%20granja%20y%20idle.md),
> donde el material ya existe en otro documento **se enlaza y no se repite**; el código que
> aparece aquí es el que faltaba por escribir en algún sitio de la biblioteca.

---

## 1 · Qué cubre este documento

| Formato | La convención que trae el jugador | Qué construye este documento | A qué te apoyas (ya existe) |
|---|---|---|---|
| **Kiosco / exposición / museo** | Un único control, cero curva de aprendizaje, la partida de otro no es la mía | Temporizador de inactividad → *attract mode*, reinicio automático sin «continuar» | [04 · 25](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md) (menú de ajustes, no aplica aquí: no hay ajustes que tocar) |
| **Educativo / *serious game*** | El temario no lo elige el estudio, hay que medir si aprendió | Pregunta con opciones + registro de aciertos/fallos como dato | [13 · 01 §9.5-9.7](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#95--telemetría-contar-muertes-por-sala-y-volcarlas-a-json) (telemetría a JSON, reutilizada tal cual) |
| **Publicitario (*advergame*)** | Menos de 3 minutos, sin instalar nada, la marca vive dentro del juego | Temporizador de sesión con cierre y llamada a la acción | [04 · 17 §3 bis-4](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md) (audio, memoria y detección en HTML5) |
| **Para niños** | Sin leer, sin morir de verdad, sin comprar sin que lo sepa un adulto | Puerta parental (aritmética o mantener pulsado), sin *fail state* duro | [13 · 11 §9.3](./11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md#93-política-de-privacidad) (COPPA/RGPD, ya completo), [13 · 01 §5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#5--onboarding-enseñar-sin-texto) (enseñar sin texto), [04 · 28 §5.1](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#51-el-tamaño-mínimo-de-un-botón) (hitbox mínima) |
| **Para *streamers*** | Se lee a 720p con el chat encima, hay huecos para hablar, sin *strikes* de copyright | HUD spectator-friendly, ritmo con respiro, lo que existe de verdad para Twitch | [13 · 05 §1.2 y §3.3](./05%20-%20UI%20y%20UX%20de%20juego.md#12-legibilidad-el-tamaño-mínimo-de-texto-no-es-una-opinión) (legibilidad, zonas seguras), [13 · 02 §1.2](./02%20-%20Diseño%20de%20niveles.md#12-ritmo-pacing-tensión-y-descanso) (ritmo), [13 · 09 §8](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#8--herramientas-licencias-y-accesibilidad) (licencias de música) |

Los cinco se pueden combinar: un *advergame* para niños, un *serious game* que además se enseña
en un kiosco de feria. Cuando se combinan, aplica las dos secciones — ninguna pisa a la otra
porque todas trabajan sobre el mismo patrón: un controlador persistente que vigila una condición
(inactividad, tiempo de sesión, edad de quien pulsa) y actúa sobre `room_goto`, no sobre la
lógica de juego en sí.

---

## 2 · Kiosco, exposición y museo

### 2.1 · La convención: un control, cero memoria de quién jugó antes

El jugador de un stand de feria o de un museo no leyó el manual, no sabe que existe un manual, y
en la mayoría de los casos **nunca ha tocado un teclado de PC para jugar**. Tres promesas
distintas a las de un juego normal:

1. **Un único control físico**, o una pantalla táctil con pocos botones grandes. Si hacen falta
   dos manos y cuatro teclas, la mitad del público ya se ha ido antes de entender el primer
   nivel.
2. **Nadie continúa la partida de otro.** No hay pantalla de «cargar partida» ni de «continuar»:
   cada persona que se acerca empieza de cero, y la sesión anterior no debe dejar rastro visible
   (puntuación, progreso o inventario) que la persona siguiente no se haya ganado.
3. **El kiosco se vende solo cuando nadie lo está usando.** Un stand con la pantalla congelada
   en un menú no atrae a nadie; un *attract mode* — una demostración en bucle o una pantalla de
   título animada — es lo que hace que alguien se pare a mirar.

### 2.2 · Temporizador de inactividad y *attract mode*

El patrón: un contador que se resetea en **cualquier** input real (teclado, ratón, uno o dos
dedos en pantalla táctil) y que, al llegar a un umbral, saca al juego del control del jugador
actual y lo manda a la demostración.

```gml
/// obj_reloj_kiosco — objeto persistente, Create
inactividad_actual = 0;                  // segundos sin ningún input, se resetea con cualquiera
inactividad_limite = 60;                 // ajusta al tráfico real del stand (feria concurrida: menos)
modo_demostracion  = (room == rm_demostracion);

/// obj_reloj_kiosco — Step
var _hubo_input = keyboard_check(vk_anykey)
    || mouse_check_button_pressed(mb_any)
    || device_mouse_check_button_pressed(0, mb_any)
    || device_mouse_check_button_pressed(1, mb_any);   // segundo dedo, pantallas grandes

if (_hubo_input) {
    inactividad_actual = 0;

    if (modo_demostracion) {
        // el primer toque SOLO saca de la demo; no arranca la partida por sí mismo,
        // para que quien llega vea el menú y decida, no se encuentre ya jugando
        modo_demostracion = false;
        room_goto(rm_menu);
    }
} else {
    inactividad_actual += delta_time / 1000000;   // delta_time es en microsegundos

    if (!modo_demostracion && inactividad_actual >= inactividad_limite) {
        modo_demostracion = true;
        room_goto(rm_demostracion);
    }
}
```

`rm_demostracion` puede ser una repetición grabada (inputs pregrabados que se reproducen sobre
la lógica real del juego, lo más barato de mantener sincronizado con cambios de balance) o un
vídeo/*flythrough* del arte. Lo único que importa para este documento es el mecanismo del
temporizador; el contenido de la sala de demostración es una decisión de arte, no de código.

> 🔺 **El umbral depende del contexto, no es un número universal.** 60 segundos es razonable
> para un juego de partida corta en una feria con cola; un museo sin cola y con una pieza que
> invita a leer puede aguantar 3-5 minutos sin sentirse abandonado. Mide con gente real antes de
> fijarlo.

### 2.3 · Reinicio automático: nunca «continuar»

Cuando la partida termina (victoria, derrota o tiempo agotado), no hay pantalla de guardado ni
de continuar: se muestra el resultado un rato fijo y se vuelve solo al menú, sin esperar ninguna
acción de quien jugó.

```gml
/// obj_pantalla_resultado — Create (se llega aquí al ganar, perder o agotar el tiempo)
alarm[0] = game_get_speed(gamespeed_fps) * 8;   // 8 s mostrando el resultado y fuera

/// obj_pantalla_resultado — Alarm 0
room_goto(rm_menu);   // siempre partida nueva: jamás "continuar" la de quien se acaba de ir
```

Si el juego guarda algo (una puntuación alta local, por ejemplo), esa persistencia vive en el
propio disco del kiosco entre sesiones — el sistema de partida guardada de
[01 · 14](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) sirve sin cambios —,
pero **nunca se ofrece un "continuar" al jugador**: la tabla de puntuaciones se puede mostrar en
el *attract mode*, no como opción de menú.

### 2.4 · Accesibilidad física del kiosco

Dos cosas que sí dependen del mueble físico, no del código, y que conviene decidir antes de
imprimir la carcasa:

- **Altura y alcance.** Una pantalla pensada para adultos de pie deja fuera a niños y a
  personas en silla de ruedas si el botón físico o la zona táctil activa quedan por encima de
  su alcance cómodo. ⚠️ No se verificó en esta sesión una cifra normativa concreta (el estándar
  de referencia en EE. UU. es la ADA/Access Board, pero su texto vigente no se pudo consultar
  con garantías desde aquí): trátalo como una decisión de mueble a validar con el fabricante del
  kiosco o con la normativa local del país donde se expone, no como un número que esta
  biblioteca te dé por bueno.
- **Contraste con la luz ambiente.** Un stand de feria suele tener luz cenital dura o luz de
  escaparate; el mismo contraste que en casa se lee perfecto puede desaparecer bajo un foco.
  Prueba el build en las condiciones de luz reales del sitio, no en el monitor del estudio —
  la misma lógica que ya aplica [04 · 28 §6.5](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#65-medir-en-el-dispositivo-no-en-el-pc)
  a un móvil real en vez del PC de desarrollo.

---

## 3 · Juegos educativos y *serious games*

### 3.1 · La convención: el encargo trae las restricciones puestas

Un *serious game* no es un juego normal con menos violencia: es un encargo con condiciones que
no negocia el estudio.

- **El currículo lo fija el cliente.** Qué preguntas, qué contenidos y en qué orden no son una
  decisión de diseño de juego: son un dato de entrada, normalmente un documento aparte que llega
  antes que el GDD.
- **Hay que medir si el jugador aprendió, no solo si se divirtió.** Eso exige un dato concreto
  por interacción — qué se le preguntó, qué respondió, si acertó —, no un LMS completo ni un
  sistema de perfiles: la unidad mínima de medida es el intento.
- **El público es cautivo.** Un jugador de Steam eligió estar ahí; un alumno en una sesión de
  aula no. Eso sube el listón de accesibilidad — nadie debería quedarse fuera del contenido
  obligatorio por un control que no puede usar — y baja el de violencia: sin ella, o con
  exactamente la que el currículo o el cliente autoricen por escrito.

### 3.2 · Pregunta con opciones y registro de aciertos/fallos

El dato que hace falta no es «puntuación final»: es **cada intento**, con su acierto o su fallo,
para poder responder después «¿qué pregunta falla todo el mundo?» — la misma lógica que
[13 · 01 §9.6](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#96--leer-el-volcado)
aplica a «¿qué sala mata más?».

```gml
/// scr_cuestionario — la pregunta con opciones, como dato

/// @func pregunta_crear(_identificador, _enunciado, _opciones, _indice_correcta)
/// @desc  _opciones es un array de strings; _indice_correcta es su posición (0-based).
function pregunta_crear(_identificador, _enunciado, _opciones, _indice_correcta) {
    return {
        identificador   : _identificador,
        enunciado       : _enunciado,
        opciones        : _opciones,
        indice_correcta : _indice_correcta
    };
}

/// @func pregunta_responder(_pregunta, _indice_elegida)
/// @desc  Registra el intento como dato — no solo el resultado final — reutilizando
///        telemetria_registrar() de 13 · 01 §9.5, y devuelve si acertó.
function pregunta_responder(_pregunta, _indice_elegida) {
    var _acierto = (_indice_elegida == _pregunta.indice_correcta);

    telemetria_registrar("respuesta", {
        pregunta        : _pregunta.identificador,
        elegida         : _indice_elegida,
        indice_correcta : _pregunta.indice_correcta,
        acierto         : _acierto
    });

    return _acierto;
}
```

El controlador que las muestra es deliberadamente simple: nada de arrastrar, nada de temporizador
de respuesta salvo que el currículo lo pida — la exigencia es entender la pregunta y elegir, no
ser rápido.

```gml
/// obj_controlador_cuestionario — Create
preguntas = [
    pregunta_crear("suma_01", "¿Cuánto es 3 + 4?", ["6", "7", "8"], 1),
    pregunta_crear("capital_01", "¿Cuál es la capital de Francia?", ["Madrid", "París", "Roma"], 1)
];
indice_actual = 0;
altura_opcion = 64;         // hitbox grande: el público es cautivo, no viene entrenado

/// obj_controlador_cuestionario — Step
if (indice_actual < array_length(preguntas)) {
    var _p = preguntas[indice_actual];

    if (mouse_check_button_pressed(mb_left)) {
        for (var _i = 0; _i < array_length(_p.opciones); _i++) {
            var _y1 = 100 + _i * (altura_opcion + 12);
            var _y2 = _y1 + altura_opcion;

            if (point_in_rectangle(mouse_x, mouse_y, 40, _y1, 400, _y2)) {
                pregunta_responder(_p, _i);
                indice_actual += 1;
                break;
            }
        }
    }
}

/// obj_controlador_cuestionario — Draw GUI
if (indice_actual < array_length(preguntas)) {
    var _p = preguntas[indice_actual];
    draw_set_halign(fa_left);
    draw_text(40, 40, _p.enunciado);

    for (var _i = 0; _i < array_length(_p.opciones); _i++) {
        var _y1 = 100 + _i * (altura_opcion + 12);
        var _y2 = _y1 + altura_opcion;
        draw_rectangle(40, _y1, 400, _y2, false);
        draw_text(56, _y1 + 20, _p.opciones[_i]);
    }
}
```

`telemetria_registrar()` ya vuelca a JSON en cada cambio de sala y al terminar el juego
([13 · 01 §9.5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#95--telemetría-contar-muertes-por-sala-y-volcarlas-a-json));
para un centro educativo que necesite el resultado en su propio sistema, en vez de leerlo con
`jq` a mano como en §9.6, el mismo `http_request` con cola y reintento de
[13 · 01 §9.7](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#97--de-volcado-local-a-backend-real-httprequest-con-cola-y-reintento)
lo manda a un backend propio: no hace falta escribir un sistema de exportación nuevo, el patrón
ya existe y no distingue entre «evento de muerte» y «evento de respuesta».

### 3.3 · Accesibilidad reforzada y sin violencia

Como el público no eligió estar ahí, ningún contenido obligatorio puede depender de un sentido o
de una habilidad motriz concretos: subtítulos y lector de pantalla no son un extra, son
condición de que el propio contenido llegue a todo el mundo. La checklist completa —
daltonismo, subtítulos, motricidad, dificultad ajustable — ya está en
[04 · 27](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) y no se repite aquí; lo
único específico de este formato es que en un *serious game* no son «Basic/Intermediate/Advanced»
opcionales, sino el nivel «Basic» **obligatorio** para todo el contenido curricular.

Sobre la violencia: sin ella salvo que el propio currículo la contemple explícitamente (educación
vial con un choque simulado, por ejemplo) — y en ese caso, la restricción la documenta el
cliente por escrito antes de diseñar una sola escena, no el estudio por su cuenta.

---

## 4 · Juegos publicitarios (*advergames*)

### 4.1 · La convención: sesión corta, marca dentro del mundo

Un *advergame* se juega una vez, dura menos de tres minutos y su objetivo no es retener: es que
la marca se recuerde. Tres reglas que se rompen constantemente y que valen la pena repetir:

1. **La marca vive DENTRO del juego, no encima.** El logo en la lata que recoges, el producto
   como power-up, el color de marca como paleta del nivel — nunca un banner superpuesto que
   tapa la pantalla mientras se juega. Un *advergame* que se siente como un anuncio con un
   minijuego pegado falla en lo único que tenía que hacer bien.
2. **Sesión corta de verdad.** No «se puede terminar en 3 minutos si vas perfecto»: el diseño
   fuerza el corte, con un temporizador que cierra la sesión y no un nivel que el jugador
   competente extiende a diez minutos y el casual abandona a los noventa segundos frustrado.
3. **Cero fricción de descarga.** WebGL/HTML5, cargando directamente desde el enlace del
   anuncio o de la campaña — nadie instala nada para probar un *advergame*.

### 4.2 · Temporizador de sesión con cierre y llamada a la acción

```gml
/// obj_sesion_publicitaria — Create
tiempo_transcurrido        = 0;
duracion_maxima            = 150;   // 2 min 30 s de juego real, margen bajo el tope de 3 minutos
llamada_accion_mostrada    = false;

/// obj_sesion_publicitaria — Step
tiempo_transcurrido += delta_time / 1000000;

if (!llamada_accion_mostrada && tiempo_transcurrido >= duracion_maxima) {
    llamada_accion_mostrada = true;
    room_goto(rm_cierre_campana);   // pantalla de resultado + CTA de la marca, no un pop-up
}
```

`rm_cierre_campana` es donde vive la llamada a la acción — «visita la web», «prueba el producto»
— y es el único momento en el que sí conviene salir del navegador:

```gml
/// obj_boton_visitar_marca — cualquier evento de click en la sala de cierre
if (os_browser != browser_not_a_browser) {
    url_open("https://www.marca-ejemplo.com/promo");   // se abre en pestaña nueva del navegador
}
```

El margen de 30 segundos entre `duracion_maxima` y el tope real de 3 minutos absorbe la carga
inicial y la pantalla de cierre en sí; súbelo si el nivel se completa siempre antes de tiempo, y
bájalo si el 90 % de las sesiones expiran a mitad del contenido — con datos de verdad, usando el
mismo patrón de telemetría de §3.2, no a ojo.

### 4.3 · Sin fricción de descarga: apóyate en HTML5, no lo repitas

Todo lo técnico de publicar un *advergame* como WebGL/HTML5 ya está resuelto en
[04 · 17](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md)
y no se repite aquí:

- **Desbloquear el audio.** Un *advergame* casi siempre arranca con un clic desde un anuncio, no
  con una interacción explícita del jugador dentro del propio juego — la pantalla «pulsa para
  empezar» de [04 · 17 §3 bis](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md)
  es exactamente el mecanismo que hace falta antes de que suene nada, jingle de marca incluido.
- **El techo de memoria real.** Con una sesión de menos de tres minutos el riesgo de agotar
  memoria es bajo, pero si el *advergame* se sirve embebido dentro de un anuncio en un móvil de
  gama baja (el peor caso, no el PC del cliente en la reunión), el techo de
  [04 · 17 §3 ter](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md)
  sigue aplicando igual.
- **Detectar dónde se ejecuta.** Si el mismo *advergame* se sirve como anuncio embebido y como
  demo independiente en la web de la marca, `os_browser` de
  [04 · 17 §4](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md)
  es lo que decide si el botón de §4.2 puede abrir pestaña nueva o si el contenedor del anuncio
  lo bloquea (algunos formatos de anuncio interceptan la navegación: pruébalo en el formato real
  de la campaña, no solo en local).

---

## 5 · Juegos para niños

### 5.1 · Lo legal ya está — se enlaza, no se repite

El marco legal de recoger datos de un menor, COPPA en EE. UU. y el umbral de edad variable del
RGPD en la UE (España lo fija en 14 años), **ya está completo** en
[13 · 11 §9.3 — «Datos de menores»](./11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md#93-política-de-privacidad),
con sus fuentes primarias verificadas (FTC, BOE). No se repite ni una frase de eso aquí: lo que
falta, y lo que cierra esta sección, es la mitad de **diseño** que ese documento no cubre —
cómo se comunica el juego con alguien que no sabe leer bien todavía, y qué pasa antes de que
cualquier enlace externo o compra se dispare.

### 5.2 · Iconos sin depender de la lectura

Enseñar sin texto ya tiene su teoría completa en
[13 · 01 §5](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#5--onboarding-enseñar-sin-texto)
— la regla de una idea nueva cada vez, gating, el examen de los primeros 60 segundos — y aplica
sin cambios. Lo específico de un juego infantil es que ahí **no es una técnica de onboarding
para los primeros minutos**: es la única forma de comunicación durante todo el juego, porque
gran parte del público todavía no lee con fluidez o no lee en absoluto.

En la práctica: cualquier acción que en un juego para adultos se resolvería con una frase de
texto (un tutorial, un mensaje de error, una condición de victoria) se resuelve aquí con un
icono, un color y una demostración animada — la misma caja de herramientas de
[13 · 01 §5.2](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md#5--onboarding-enseñar-sin-texto),
aplicada de forma permanente en vez de solo al principio.

### 5.3 · Sin *fail state* duro: recompensar el intento

Una pantalla de «GAME OVER» con una `X` roja no enseña a un niño pequeño a intentarlo de nuevo:
enseña que se equivocó y punto. El patrón que sí funciona:

- **No hay derrota permanente.** Si el jugador «falla» un reto, el juego lo redirige a un
  segundo intento inmediato, casi siempre con una pista extra, en vez de mandarlo a un menú.
- **El feedback de fallo es neutro o alentador, nunca punitivo.** Un color cálido y un personaje
  que anima a repetir, no un sonido de derrota ni una racha de vidas que se acaba.
- **No hay contador de vidas visible que pueda llegar a cero.** Si el diseño necesita un límite
  interno por razones de ritmo, no se le muestra al jugador como una cuenta atrás hacia el
  fracaso.

Técnicamente esto no pide ningún sistema nuevo: es la misma máquina de estados de cualquier
receta de género —
[13 · 18 — Diseño de combate y de jefes](./18%20-%20Diseño%20de%20combate%20y%20de%20jefes.md)
para el combate, o la del propio género base del juego — a la que simplemente **no se le conecta
una transición a un estado de derrota**: la transición de «fallo» va siempre de vuelta al mismo
reto, no a una pantalla distinta.

### 5.4 · Puerta parental antes de cualquier enlace o compra

No es autenticación real — nada de contraseñas ni de cuentas —, es una comprobación rápida de
que hay un adulto delante de la pantalla en ese momento. Dos variantes válidas; la biblioteca no
impone cuál usar, pero ambas comparten el mismo principio: algo que un adulto resuelve en
segundos y que un niño pequeño, a la velocidad a la que hace falta, normalmente no.

**Variante 1 — problema aritmético con opciones**, reutilizando el mismo patrón de detección de
clic que §3.2:

```gml
/// obj_puerta_parental — Create
factor_a            = irandom_range(3, 9);
factor_b            = irandom_range(2, 7);
respuesta_correcta  = factor_a * factor_b;
opciones            = [respuesta_correcta, respuesta_correcta + irandom_range(1, 5),
                        respuesta_correcta - irandom_range(1, 4)];
opciones            = array_shuffle(opciones);   // la correcta no cae siempre en el mismo sitio
destino_tras_pasar  = rm_ajustes_padres;         // enlace externo, compra o lo que active la puerta

/// obj_puerta_parental — Step
if (mouse_check_button_pressed(mb_left)) {
    for (var _i = 0; _i < array_length(opciones); _i++) {
        var _y1 = 120 + _i * 76;
        var _y2 = _y1 + 64;

        if (point_in_rectangle(mouse_x, mouse_y, 60, _y1, 360, _y2)) {
            if (opciones[_i] == respuesta_correcta) {
                room_goto(destino_tras_pasar);
            } else {
                // fallo: nueva cuenta, no un castigo — puede ser el propio niño probando
                factor_a           = irandom_range(3, 9);
                factor_b           = irandom_range(2, 7);
                respuesta_correcta = factor_a * factor_b;
                opciones           = array_shuffle([respuesta_correcta,
                    respuesta_correcta + irandom_range(1, 5), respuesta_correcta - irandom_range(1, 4)]);
            }
        }
    }
}

/// obj_puerta_parental — Draw GUI
draw_text(60, 60, $"Para continuar, un adulto: ¿cuánto es {factor_a} x {factor_b}?");
for (var _i = 0; _i < array_length(opciones); _i++) {
    var _y1 = 120 + _i * 76;
    draw_rectangle(60, _y1, 360, _y1 + 64, false);
    draw_text(76, _y1 + 20, string(opciones[_i]));
}
```

**Variante 2 — mantener pulsado 3 segundos**, más simple y sin depender de una cuenta que un
niño mayor sí podría resolver:

```gml
/// obj_puerta_parental_mantener — Create
tiempo_mantenido    = 0;
tiempo_necesario    = 3;                  // segundos que hay que mantener pulsado
boton_x1 = 60; boton_y1 = 120; boton_x2 = 360; boton_y2 = 184;
destino_tras_pasar  = rm_ajustes_padres;

/// obj_puerta_parental_mantener — Step
var _dentro  = point_in_rectangle(mouse_x, mouse_y, boton_x1, boton_y1, boton_x2, boton_y2);
var _pulsado = mouse_check_button(mb_left) || device_mouse_check_button(0, mb_any);

if (_dentro && _pulsado) {
    tiempo_mantenido += delta_time / 1000000;
    if (tiempo_mantenido >= tiempo_necesario) {
        room_goto(destino_tras_pasar);
    }
} else {
    tiempo_mantenido = 0;   // soltar antes de tiempo cancela: no se guarda progreso parcial
}

/// obj_puerta_parental_mantener — Draw GUI
draw_rectangle(boton_x1, boton_y1, boton_x2, boton_y2, false);
draw_text(boton_x1 + 16, boton_y1 + 20, "Mantén pulsado 3 segundos (para un adulto)");
draw_set_color(c_white);
draw_rectangle(boton_x1, boton_y1, boton_x1 + (boton_x2 - boton_x1) * (tiempo_mantenido / tiempo_necesario), boton_y2, false);
draw_set_color(c_black);
```

> 🔺 **`mouse_check_button` es continuo; `mouse_check_button_pressed` solo dispara una vez.** Es
> el error más fácil de cometer aquí: usar la versión `_pressed` en la Variante 2 hace que
> `tiempo_mantenido` nunca avance más allá del primer paso, porque solo es verdadera en el frame
> exacto en que se pulsa. Lo mismo aplica a `device_mouse_check_button` frente a
> `device_mouse_check_button_pressed` para pantalla táctil.

### 5.5 · Controles simplificados y tolerantes

El suelo de 48 px de zona táctil de
[04 · 28 §5.1](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#51-el-tamaño-mínimo-de-un-botón)
está pensado para un adulto con buena motricidad fina; una mano infantil, con menos precisión y
menos control del gesto, necesita un suelo más alto todavía — súbelo en vez de tratar 48 px como
un mínimo universal. Además:

- **Nada de combos ni de ventanas de tiempo ajustadas.** Un input, una acción; si hace falta
  encadenar dos gestos, dales el margen de tiempo más generoso que el diseño tolere.
- **La hitbox del personaje/objetivo, no solo la del botón, también se agranda.** Tocar «casi»
  encima de un objetivo pequeño y que no cuente frustra más a un niño que a un adulto, porque no
  tiene el vocabulario para entender por qué falló.
- **Un control físico por acción, nunca un gesto compuesto** (arrastrar-y-soltar con precisión,
  pellizcar para hacer zoom) como única vía: la motricidad fina para esos gestos madura tarde.

---

## 6 · Juegos para *streamers* — diseño *spectator-friendly*

### 6.1 · La convención: el juego se juega Y se retransmite a la vez

Quien diseña para *streamers* diseña para dos audiencias con necesidades distintas al mismo
tiempo: quien tiene el mando, que ve el juego a resolución completa y sin nada encima, y quien
lo ve por Twitch, que lo ve comprimido, a menudo a 720p, con el chat, la cámara y las alertas
tapando parte de la pantalla, y sin poder tocar nada.

### 6.2 · HUD legible a 720p, y en las esquinas que tapa el *streamer*

[13 · 05 §1.2](./05%20-%20UI%20y%20UX%20de%20juego.md#12-legibilidad-el-tamaño-mínimo-de-texto-no-es-una-opinión)
ya da la cifra oficial de legibilidad (Xbox Accessibility Guidelines: 26 px a 1080p para
distancia de sofá) y la técnica robusta de escribirla como **fracción de la altura del GUI**, no
en píxeles absolutos. ⚠️ No existe una cifra equivalente publicada específicamente para
retransmisión en directo — no se encontró ninguna guía oficial de Twitch sobre tamaño de HUD en
esta sesión —, pero el problema de fondo es el mismo por dos razones distintas y acumulativas:
la compresión de vídeo del *streaming* desenfoca los bordes finos igual que la distancia al
televisor, y el vídeo de Twitch se ve con frecuencia en una ventana pequeña del navegador o en
el móvil, no a pantalla completa. Con ese razonamiento, y no con una fuente nueva, la
recomendación es usar el mismo suelo de consola (**2,4 % de la altura del GUI**, la cifra que
en 1080p da los 26 px de §1.2) como mínimo para retransmisión, en vez del suelo de escritorio.

Lo que sí es nuevo aquí es la esquina: la zona segura de
[13 · 05 §3.3](./05%20-%20UI%20y%20UX%20de%20juego.md#33-zonas-seguras-el-notch-del-móvil-y-el-overscan-de-la-tele)
protege del *notch* y del *overscan*, pero un *streamer* añade su propia obstrucción — la
cámara facial, casi siempre en una esquina inferior — que el juego no puede detectar ni conocer
de antemano. La única defensa que no depende de adivinar dónde está la cámara es **no poner
información crítica en una sola esquina**: la vida, la puntuación o el objetivo activo van en
una franja (arriba o abajo, centrada o a lo ancho), nunca como el único dato metido en un
rincón que cualquier overlay puede tapar sin que el diseño se entere.

### 6.3 · Ritmo con huecos para hablar

El ritmo general — picos y valles de intensidad, el gráfico de
[13 · 02 §1.2](./02%20-%20Diseño%20de%20niveles.md#12-ritmo-pacing-tensión-y-descanso) — ya
está resuelto y no se repite. Lo específico de un juego pensado para retransmitirse es que
**los valles no son solo descanso del jugador: son el hueco donde el streamer comenta, lee el
chat y reacciona**, y ese hueco tiene una duración mínima distinta a la de un valle pensado
solo para bajar la tensión de quien juega en solitario.

- **Los valles necesitan más margen del que pide un jugador solo.** Un valle de cinco segundos
  basta para que un jugador respire; un streamer necesita más para leer una pregunta del chat y
  responderla en voz alta sin perderse la siguiente sección. Diez a veinte segundos de tramo sin
  presión activa —no vacío de contenido, solo sin urgencia— es lo que deja hablar sin que el
  juego avance solo mientras tanto.
- **Evita los eventos por tiempo fijo dentro de un valle.** Si algo puede dispararse a los 8
  segundos exactos de haber llegado a una zona de calma, el streamer que se ha puesto a hablar
  lo pierde. Los eventos del valle mejor disparados por una acción del jugador (entrar en una
  sala, recoger un objeto), nunca por un reloj que no espera a que termine la frase.
- **Los objetivos secundarios opcionales son huecos gratis.** Un cofre, una zona explorable sin
  urgencia, un NPC con el que hablar sin límite de tiempo: dan al streamer una excusa para
  quedarse quieto y comentar sin que la cámara del stream se sienta vacía de contenido.

### 6.4 · Sin música con copyright

Las licencias seguras para retransmisión en directo — qué origen de audio sirve, cuál exige
atribución y cuál está directamente prohibido para un juego que se vende — ya están completas en
[13 · 09 §8](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#8--herramientas-licencias-y-accesibilidad),
con la misma tabla que aplica a cualquier juego. Lo único que añade el contexto de *streaming* es
que el filtro se aplica con más rigor todavía: una pista con copyright que en el propio juego
pasa desapercibida puede disparar un *Content ID* automático de Twitch o YouTube en cuanto
alguien la retransmite, silenciando el vídeo en directo o el VOD entero, aunque el resto del
audio (voz del streamer, efectos) esté limpio. La regla práctica no cambia — CC0, CC-BY con
atribución o grabación propia — pero conviene comprobar explícitamente que cada pista de música
del juego está en esa lista **antes** de que un streamer la use en directo, no después de la
primera queja.

### 6.5 · Integración con el chat de Twitch — lo que existe de verdad

GameMaker **no trae ninguna función nativa de Twitch en el runtime**: no hay ningún símbolo
`twitch_*` en `GmlSpec.xml` ni en `fnames`, y `buscar.py` no encuentra nada — se comprobó en
esta sesión. Lo que sí existe, y con lo que hay que trabajar, es una **extensión oficial de
YoYo Games**, `GMEXT-Twitch`, publicada en
[github.com/YoYoGames/GMEXT-Twitch](https://github.com/YoYoGames/GMEXT-Twitch) (Apache-2.0, 21
estrellas, último cambio 2025-12-29), ya clonada en esta biblioteca en
`11 - Código descargado/extensiones_oficiales/GMEXT-Twitch/` y cita catalogada en
[12 · 03 §2](../12%20-%20Utilidades%20e%20integraciones/03%20-%20Integraciones%20con%20servicios.md#2-comunidad-y-redes).
Instalación y alternativas de comunidad completas en ese documento — no se repiten aquí.

Lo que sí aporta este documento, porque lo verificó leyendo el código real de la extensión, no
el catálogo: sus funciones **no están indexadas por `buscar.py`** (son de la extensión, no del
runtime) y hay una trampa concreta para un juego pensado para *streaming* en navegador:

| Función real de la extensión (verificada en su código fuente) | Qué hace |
|---|---|
| `twitch_chat_send_chat_message(...)` | Envía un mensaje al chat vía la API REST de Twitch (Helix) — funciona en cualquier plataforma, incluido HTML5, porque usa `http_request` por debajo |
| `twitch_chat_live_connect(_channel_id, _nickname, _callback)` | Se conecta al chat **en directo** para leer lo que escribe la gente |
| `twitch_chat_live_send(_texto)` / `twitch_chat_live_disconnect()` | Enviar al chat en directo y cortar la conexión |

⚠️ **La conexión de chat en directo, tal y como está escrita en la versión de la extensión
clonada en esta biblioteca, usa un socket TCP crudo** (`network_create_socket(network_socket_tcp)`
contra `irc.chat.twitch.tv:6667`, el protocolo IRC clásico de Twitch) **y eso no funciona en un
export HTML5**: el propio manual oficial de `network_create_socket`
(`09 - Manual oficial/manual-lts-2026-es/…/network_create_socket.md`) trae un ejemplo que hace
exactamente esta distinción — TCP crudo cuando `os_browser == browser_not_a_browser` (fuera del
navegador), `network_socket_ws`/`network_socket_wss` cuando no. Twitch expone su chat también
por WebSocket seguro en `wss://irc-ws.chat.twitch.tv:443` con el mismo protocolo IRC por
encima, así que un chat en directo dentro de un juego HTML5 es técnicamente posible, pero **no
con la función `twitch_chat_live_connect` de la extensión tal cual viene**: hace falta
reescribir esa conexión con `network_create_socket(network_socket_wss)` +
`network_connect_raw_async(...)` en vez del socket TCP que trae la extensión. El propio catálogo
de [12 · 03 §2](../12%20-%20Utilidades%20e%20integraciones/03%20-%20Integraciones%20con%20servicios.md#2-comunidad-y-redes)
ya señala una alternativa de comunidad («MM's Twitch IRC») marcada explícitamente como que
«funciona incluso en HTML5» — la pista de que esta limitación es conocida en la comunidad, no
una suposición de este documento. El patrón general de conectar un socket asíncrono y leerlo en
el evento **Async - Networking**, con `network_socket_ws`/`wss` en vez de TCP para web, ya está
completo en
[04 · 14 §4.1 y §5.4](../04%20-%20Recetas%20por%20género/14%20-%20Multijugador.md#41-tcp-vs-udp-vs-websocket)
y no se repite aquí: es el mismo mecanismo, aplicado al *host* de Twitch en vez de al servidor
propio del juego.

---

## Ver también

- [04 · 45 — Géneros sin receta propia](../04%20-%20Recetas%20por%20género/45%20-%20Géneros%20sin%20receta%20propia%20-%20sigilo%2C%20horror%2C%20táctica%2C%20granja%20y%20idle.md) — el documento hermano de este: contextos de género sin receta propia, con el mismo patrón de «enlaza, no repitas».
- [13 · 01 §5 y §9.5-9.7](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md) — onboarding sin texto (§5) y telemetría a JSON (§9.5-9.7), la base de §3.2 y §5.2.
- [13 · 05 §1.2 y §3.3](./05%20-%20UI%20y%20UX%20de%20juego.md) — legibilidad y zonas seguras, la base de §6.2.
- [13 · 02 §1.2](./02%20-%20Diseño%20de%20niveles.md) — el gráfico de ritmo del que parte §6.3.
- [13 · 09 §8](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md) — licencias de audio, la base de §6.4.
- [13 · 11 §9.3 y §9.4](./11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md) — COPPA/RGPD (§9.3) y clasificación por edades PEGI/ESRB/IARC (§9.4), el marco legal completo de §5.1.
- [04 · 17 §3 bis-4](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md) — audio, memoria y detección de entorno en HTML5, la base de §4.3.
- [04 · 27 §4](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) — accesibilidad motriz, la base de §3.3 y §5.5.
- [04 · 28 §5.1 y §6.5](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md) — tamaño mínimo de botón táctil, la base de §5.5, y medir en el dispositivo real, la base de §2.4.
- [04 · 14 §4.1 y §5.4](../04%20-%20Recetas%20por%20género/14%20-%20Multijugador.md) — WebSocket frente a TCP y el evento asíncrono de red, la base técnica de §6.5.
- [12 · 03 §2](../12%20-%20Utilidades%20e%20integraciones/03%20-%20Integraciones%20con%20servicios.md) — el catálogo completo de integraciones con Twitch, Discord y otras redes, la base de §6.5.
- [01 · 14 — Persistencia y archivos](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) — el sistema de guardado que §2.3 menciona para una tabla de puntuaciones local.

## Fuentes

**Manual oficial y runtime** — todos los símbolos de GML de este documento comprobados con
`python3 _indice/buscar.py` contra el runtime `2026.0.0.23` (espejo local en
`09 - Manual oficial/`): `keyboard_check`, `vk_anykey`, `mouse_check_button_pressed`,
`mouse_check_button`, `mb_any`, `mb_left`, `device_mouse_check_button_pressed`,
`device_mouse_check_button`, `delta_time`, `room_goto`, `alarm`, `game_get_speed`,
`gamespeed_fps`, `url_open`, `os_browser`, `browser_not_a_browser`, `irandom_range`, `irandom`,
`array_shuffle`, `array_length`, `array_push` (mencionado, no reescrito), `point_in_rectangle`,
`mouse_x`, `mouse_y`, `draw_text`, `draw_rectangle`, `draw_set_halign`, `fa_left`,
`draw_set_color`, `c_white`, `c_black`, `string`, `network_create_socket`, `network_socket_tcp`,
`network_socket_ws`, `network_socket_wss`, `network_connect_raw_async`. La página del manual de
`network_create_socket` (`09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Networking/network_create_socket.md`)
es la fuente directa de la distinción TCP/WebSocket citada en §6.5.
`telemetria_registrar()`/`telemetria_iniciar()`/`telemetria_volcar()` (§9.5 de
[13 · 01](./01%20-%20Diseño%20de%20juego%20-%20core%20loop%2C%20mecánicas%2C%20balance%20y%20dificultad.md))
son funciones **propias de la biblioteca**, no del runtime: se enlazan a su definición en vez de
reescribirlas.

**Código real descargado, consultado en esta sesión (2026-09-07):**

- `11 - Código descargado/extensiones_oficiales/GMEXT-Twitch/source/twitch_gml/scripts/twitch_functions/twitch_functions.gml`
  — código fuente completo de la extensión oficial de Twitch, leído directamente para verificar
  `twitch_chat_live_connect`, `twitch_chat_send_chat_message` y el uso de `network_socket_tcp`
  contra `irc.chat.twitch.tv:6667` citados en §6.5. Repositorio:
  <https://github.com/YoYoGames/GMEXT-Twitch> (Apache-2.0, 21 ★, último commit 2025-12-29 según
  el catálogo de esta biblioteca).
- `11 - Código descargado/extensiones_oficiales/GMEXT-Twitch/README.md` — confirma que la
  extensión funciona «across all available platform since it relies on using Twitch REST API»
  para la parte REST, sin mencionar el chat en directo, consistente con la limitación de socket
  TCP encontrada en el código.

**Diseño y accesibilidad, consultadas el 2026-09-07:**

[^1]: Federal Trade Commission, *Complying with COPPA: Frequently Asked Questions* —
    <https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions>
    — ya citada con su cita textual completa en
    [13 · 11 §9.3](./11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md#93-política-de-privacidad);
    no se repite la cita aquí.
[^2]: Google, *Touch target size — Android Accessibility Help* —
    <https://support.google.com/accessibility/android/answer/7101858?hl=en> — el suelo de 48 px
    que [04 · 28 §5.1](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#51-el-tamaño-mínimo-de-un-botón)
    ya cita y que §5.5 de este documento extiende al público infantil.

⚠️ **Lo que quedó sin verificar y por qué:** la normativa concreta de altura/alcance físico de un
kiosco accesible (§2.4) — se intentó consultar la página de estándares del US Access Board
(`access-board.gov/ict/`) por `curl`, pero el contenido normativo se sirve por JavaScript y no
llegó en el HTML crudo, así que no hay cifra que citar con garantías; una guía específica de
Twitch sobre tamaño de HUD para retransmisión (§6.2) — no se encontró ninguna publicada por
Twitch, y la recomendación de esa sección es una extrapolación razonada de la cifra de
[13 · 05 §1.2](./05%20-%20UI%20y%20UX%20de%20juego.md#12-legibilidad-el-tamaño-mínimo-de-texto-no-es-una-opinión),
marcada como tal en el propio texto.
