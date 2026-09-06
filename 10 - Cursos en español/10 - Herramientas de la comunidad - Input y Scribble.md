# 10 · Herramientas de la comunidad: Input y Scribble

> **Fuente de partida:** dos vídeos de [Altair_AML](https://www.youtube.com/@Altair_AML) (2023):
> [*Mejora tu proyecto con Input*](https://youtu.be/mcJ86swsjNE) (11:00) y
> [*Cómo crear diálogos fácilmente con Scribble*](https://youtu.be/rxsPzpbBv74) (7:23).
>
> ⚠️ **Los enlaces de descarga de los vídeos ya no son válidos.** Este documento recoge la
> técnica que enseñan pero con las **rutas y versiones verificadas el 1 de septiembre de 2026**.

---

## ⚠️ Lo primero: dónde están hoy, de verdad

Los vídeos son de 2023 y mandan a itch.io. Comprobado hoy:

| Librería | Lo que dice el vídeo | **Dónde está en 2026** | Estado verificado |
|---|---|---|---|
| **Input** | `jujuadams.itch.io/input` | **[codeberg.org/offalynne/Input](https://codeberg.org/offalynne/Input)** | ✅ v**10.4.3** (19-08-2026) · MIT |
| **Scribble** | `jujuadams.itch.io/scribble` | **[github.com/JujuAdams/Scribble](https://github.com/JujuAdams/Scribble)** | ✅ v**9.7.3** (28-01-2026) · MIT · 415 ★ |

**Input cambió de casa y de responsable.** El repositorio de GitHub (`JujuAdams/Input` →
`offalynne/Input`) está **archivado** con el aviso *«Moved to Codeberg»*, y la página de itch.io
devuelve **404**. El proyecto lo mantiene ahora [**offalynne**](https://codeberg.org/offalynne)
y sigue muy vivo: el último cambio es de **hoy mismo**.

- 📘 Documentación de Input: <https://offalynne.grebedoc.dev/Input/>
- 📘 Documentación de Scribble: <https://github.com/JujuAdams/Scribble/wiki>

> 🔺 Scribble tiene además una **9.8.0-alpha** (agosto 2026). Para producción, quédate en la
> **9.7.3** estable.

---

## Cómo se instala cualquiera de las dos

Las dos se distribuyen como **paquete local `.yymps`**, que es la vía de instalación estándar
de GameMaker para librerías de solo código:

1. Descarga el `.yymps` de la sección de *releases* del repositorio.
2. En GameMaker: **Tools → Import Local Package**.
3. Selecciona el archivo, pulsa **Add All** e **Import**.

> 🔺 **2026:** ojo, hay repos que ofrecen **dos** descargas: el `.yymps` (los recursos, para
> importar a *tu* proyecto) y un `.yyz`/proyecto completo (una demo, que abre un proyecto
> aparte). Para añadirlo a tu juego quieres **siempre el `.yymps`**.

---

# Input — mando, teclado y ratón unificados

## Qué problema resuelve

En GameMaker puro, dar soporte a mando es trabajo real: `gamepad_button_check`,
`gamepad_axis_value`, zonas muertas, detectar conexiones y desconexiones, y mantener a la vez
un camino paralelo para teclado. Input lo colapsa en **una sola llamada**.

La idea central es el **verbo**: no preguntas «¿está pulsada la flecha derecha?» sino
«¿está activo el verbo *derecha*?». Qué tecla o botón corresponde a ese verbo es
configuración, no código.

```gml
// GameMaker puro: teclado y mando por separado
if (keyboard_check(vk_right) || gamepad_button_check(0, gp_padr)) { ... }

// Con Input: un verbo, todos los dispositivos
if (InputCheck("right")) { ... }
```

## Configuración

Todo se define en dos scripts que vienen con la librería:

- **`__input_config_verbs`** — asocia cada verbo con sus teclas y botones. Hay dos bloques
  separados: uno para **teclado y ratón** y otro para **gamepad**. Un mismo verbo puede tener
  varias entradas (flecha derecha *y* tecla D).
- **`__input_config_icons`** — asocia cada entrada con un icono, para poder dibujar en pantalla
  «pulsa [A]» y que el icono cambie solo según el mando conectado.

Ambos vienen ya rellenos con valores razonables: es más fácil copiar el patrón que empezar
de cero.

## Las funciones básicas

| Función | Equivale a | Nota |
|---|---|---|
| `InputCheck("verbo")` | `keyboard_check` | mientras se mantiene |
| `InputPressed("verbo")` | `keyboard_check_pressed` | solo el frame de la pulsación |
| `InputReleased("verbo")` | `keyboard_check_released` | solo el frame de la soltada |

## Las tres que justifican la librería

**`InputRepeat("verbo")`** — se activa cada cierto intervalo mientras mantienes pulsado.
Es el disparo automático de los arcade y la repetición al navegar un menú, gratis.

> 🔺 **La API de Input es PascalCase**, no snake_case: `InputCheck`, `InputPressed`,
> `InputReleased`, `InputRepeat`, `InputBindingSwap`… (verificado contra el repo descargado en
> `11 - Código descargado/librerias/entrada/Input`, 200 funciones, todas `Input…`).

**Doble pulsación** — Input **no** trae una función dedicada; se monta a mano con un
escribir un temporizador (compara con
[el constructor `DoblePulsacion`](./08%20-%20Plataformas%20estilo%20Megaman%20X%20-%20apuntes%20de%20la%20serie%20de%20Altair.md#detectar-doble-pulsación-con-un-constructor)
que hay que montar a mano sin la librería).

**Combos** — secuencias tipo Konami o entradas de lucha. **Input no incluye un sistema de
combos** en la versión descargada: se montan a mano guardando las últimas pulsaciones en una
cola y comparándola con el patrón.

```gml
/// Create
secuencia = [];
patron = ["up", "up", "down", "down", "left", "right"];

/// Step — apila la pulsación y comprueba si el final coincide con el patrón
var _verbos = ["up", "down", "left", "right"];
for (var _i = 0; _i < array_length(_verbos); _i++) {
    if (InputPressed(_verbos[_i])) {
        array_push(secuencia, _verbos[_i]);
        if (array_length(secuencia) > array_length(patron)) array_delete(secuencia, 0, 1);
    }
}
// ¿los últimos N coinciden con el patrón?
if (array_equals(secuencia, patron)) desbloquear_extras();
```

## Remapeo de teclas

Input trae `InputBindingSwap()`, la pieza que permite montar una pantalla de «configurar
controles» de verdad. El patrón:

1. Dibujas la lista de verbos con su icono actual.
2. El jugador elige uno.
3. Escuchas la siguiente entrada y la intercambias con `InputBindingSwap()`.

> 💡 **Comprueba siempre que el mando siga conectado** antes de pedirle iconos o estados. Un
> mando se desconecta en mitad de la partida y, si no lo compruebas, pides el icono de un
> dispositivo que ya no existe. Es el fallo más común al montar estos menús.

## Veredicto

**Si tu juego va a soportar mando, úsala.** Está probada en juegos comerciales publicados
(*Shovel Knight Pocket Dungeon*, entre otros) y el coste de adoptarla es una tarde. Hacer esto
a mano y hacerlo bien es de las cosas que más tiempo consumen sin que se note en pantalla.

---

# Scribble — texto con formato y efectos

## Qué problema resuelve

Las funciones de texto de GameMaker (`draw_text` y compañía) dibujan una cadena en un color y
poco más. No hay forma nativa de:

- pintar **una palabra suelta** de otro color dentro de la misma frase,
- **incrustar un sprite** en mitad del texto (un icono de botón, un emoji),
- efectos de movimiento (temblor, ondulación, arcoíris),
- ni la **máquina de escribir** carácter a carácter que quiere todo sistema de diálogo.

Scribble hace las cuatro cosas.

## Uso básico

```gml
/// Draw
var _texto = scribble("Hola [c_red]mundo[/c] con [wave]efecto[/wave] y [spr_icono]");
_texto.wrap(300, 200);          // caja de 300×200: el texto se ajusta solo
_texto.draw(x, y);
```

**El formato va entre corchetes**, dentro de la propia cadena. Sin corchetes, el texto se
dibuja en una sola línea infinita; `.wrap()` es lo que le pone caja y salto de línea
automático.

Comandos habituales:

| Comando | Efecto |
|---|---|
| `[c_red]` … `[/c]` | color (cualquier constante de color de GameMaker) |
| `[wave]` … `[/wave]` | ondulación vertical |
| `[shake]` … `[/shake]` | temblor |
| `[rainbow]` … `[/rainbow]` | degradado animado |
| `[spr_nombre]` | incrusta un sprite en línea |
| `[page]` | corta ahí y empieza página nueva |

La lista completa está en la [wiki oficial](https://github.com/JujuAdams/Scribble/wiki).

## Efecto máquina de escribir

Es lo que casi todo el mundo busca. Se hace con un **typist**, un objeto aparte que controla el
ritmo de aparición:

```gml
/// Create
typist = scribble_typist();
typist.in(0.5, 0);              // velocidad de escritura

texto = scribble("Primera página.[page]Segunda página.");

/// Draw
texto.wrap(300, 200);
texto.draw(x, y, typist);       // ← el typist se pasa al draw

/// Step — avanzar de página
if (keyboard_check_pressed(vk_space)) {
    if (typist.get_state() == 1) typist.page_next();   // ya terminó: pasar página
    else                         typist.skip();        // aún escribiendo: mostrar todo ya
}
```

> 💡 **`[page]` es el separador de páginas** y el typist se encarga del resto. El detalle que
> más se agradece en un diálogo: si el jugador pulsa mientras el texto se escribe, **muéstralo
> entero** (`skip()`) en vez de ignorarlo o pasar de página. Es la diferencia entre un diálogo
> que se siente bien y uno que exaspera.

## Cuándo NO usarla

El propio autor del vídeo lo dice y tiene razón: **si tu juego apenas tiene texto, no la
metas.** Para dos carteles y un menú, `draw_text` sobra y te ahorras una dependencia.

Scribble compensa cuando hay **RPG, novela visual o cualquier diálogo con personalidad**: texto
con colores, retratos, iconos de botón en línea, o mucho texto que además hay que traducir.

---

## Resumen para decidir

| Necesito… | Librería | ¿Merece la pena? |
|---|---|---|
| Soporte de mando decente | **Input** | ✅ Casi siempre |
| Remapeo de controles | **Input** | ✅ Hacerlo a mano es carísimo |
| Combos y doble pulsación | **Input** | ➖ Se puede a mano, pero regalado |
| Solo teclado, un plataformas | — | ❌ `keyboard_check` basta |
| Diálogos con color y efectos | **Scribble** | ✅ |
| Máquina de escribir | **Scribble** | ✅ Muy engorroso a mano |
| Juego traducido a varios idiomas | **Scribble** | ✅ Está pensado para eso |
| Dos carteles y un menú | — | ❌ `draw_text` |

---

## Cómo comprobar esto tú mismo dentro de un año

Los enlaces de las librerías caducan, como ha pasado con Input. Antes de fiarte de este
documento:

```sh
# ¿sigue vivo el repo y cuál es la última versión?
curl -s https://api.github.com/repos/JujuAdams/Scribble/releases/latest | grep tag_name
curl -s https://codeberg.org/api/v1/repos/offalynne/Input/releases | head -20
```

Y comprueba cualquier función antes de usarla:

```sh
python3 "_indice/buscar.py" scribble
```

Más librerías catalogadas en
[12 - Utilidades e integraciones](../12%20-%20Utilidades%20e%20integraciones/) y
[07 - Ecosistema](../07%20-%20Ecosistema/).
