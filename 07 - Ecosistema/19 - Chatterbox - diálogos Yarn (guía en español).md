# 19 · Chatterbox — diálogos ramificados con Yarn (guía en español)

> **Chatterbox** (de @jujuadams) reproduce guiones escritos en **Yarn** —el lenguaje de diálogo
> de *Night in the Woods* o *A Short Hike*— dentro de GameMaker. Separas el **guion** (un archivo
> `.yarn`/`.chatter` que escribe el guionista) de la **presentación** (tu código, que lo dibuja
> con [Scribble](./18%20-%20Scribble%20-%20texto%20rico%20%28guía%20en%20español%29.md)). Guía en
> español con la API verificada contra el código en
> `11 - Código descargado/librerias/dialogos-y-narrativa/Chatterbox`.

---

## La idea: guion aparte, código que lo lee

El guionista escribe nodos de diálogo en Yarn (con ramas, opciones, variables). Tu código no
sabe qué dice cada personaje; solo **avanza** por el guion y **dibuja** lo que Chatterbox le da.
Añadir una conversación no toca el código.

```
guion.yarn  →  Chatterbox lo interpreta  →  tu código pide "¿qué toca decir?" y lo dibuja
```

---

## 1 · Cargar el guion y crear la conversación

```gml
/// Create — cargar el archivo de guion UNA vez (al arrancar el juego)
ChatterboxLoadFromFile("guion.yarn");     // en Included Files

/// empezar una conversación desde un nodo
box = ChatterboxCreate("guion.yarn");     // la fuente
ChatterboxJump(box, "Inicio");            // saltar al nodo "Inicio"
```

Otras formas de cargar: `ChatterboxLoadFromString` (guion en una cadena),
`ChatterboxLoadFromBuffer` (desde un búfer).

---

## 2 · El bucle de diálogo (el corazón)

Chatterbox está en uno de dos estados: **mostrando texto** o **esperando que elijas una opción**.

```gml
/// Draw — dibujar lo que toca ahora
if (ChatterboxIsWaiting(box)) {
    // hay OPCIONES: dibujar cada una para que el jugador elija
    var _n = ChatterboxGetOptionCount(box);
    for (var _i = 0; _i < _n; _i++) {
        var _texto = ChatterboxGetOption(box, _i);
        scribble(_texto).draw(50, 100 + _i * 30);   // dibujado con Scribble
    }
} else {
    // hay LÍNEAS de diálogo: dibujar el contenido actual
    var _n = ChatterboxGetContentCount(box);
    for (var _i = 0; _i < _n; _i++) {
        var _speaker = ChatterboxGetContentSpeaker(box, _i);   // quién habla
        var _speech  = ChatterboxGetContent(box, _i);          // qué dice
        scribble(_speaker + ": " + _speech).draw(50, 50);
    }
}
```

```gml
/// Step — avanzar
if (input_confirmar && !ChatterboxIsWaiting(box)) {
    ChatterboxContinue(box);              // pasar a la siguiente línea
}

/// elegir una opción cuando está esperando
if (ChatterboxIsWaiting(box) && input_confirmar) {
    ChatterboxSelect(box, opcion_marcada); // el índice de la opción elegida
}
```

> 🔺 **`ChatterboxIsWaiting` es lo que gobierna el bucle:** si está esperando, dibujas opciones y
> usas `ChatterboxSelect`; si no, dibujas texto y usas `ChatterboxContinue`. Confundir los dos es
> el error nº 1 al integrar Chatterbox.
>
> 💡 **Chatterbox no dibuja nada**: te da cadenas. Tú las dibujas —lo natural es con
> [Scribble](./18%20-%20Scribble%20-%20texto%20rico%20%28guía%20en%20español%29.md), para tener typewriter y colores.

---

## 3 · Variables (el estado de la historia)

Yarn tiene variables (`$oro`, `$ha_visto_al_rey`) que el guion lee y escribe. Tu código las
comparte con el juego:

```gml
/// leer una variable del guion (para dar oro de verdad al jugador)
var _recompensa = ChatterboxVariableGet(box, "recompensa");
global.oro += _recompensa;

/// escribir una variable que el guion consultará (ramas según el estado del juego)
ChatterboxVariableSet(box, "tiene_llave", global.inventario_llave);
```

- `ChatterboxVariablesImport` / export — guardar y cargar el estado de la historia con la partida.

> 💡 **Las variables son cómo el diálogo reacciona al juego y viceversa.** El guion puede
> ramificar según `$tiene_llave`, y tú lees `$recompensa` para darla. El guionista y el
> programador se comunican por variables, sin pisarse.

---

## 4 · Funciones y metadatos (avanzado)

```gml
/// exponer una función del juego al guion (que el diálogo pueda "hacer cosas")
ChatterboxAddFunction("dar_objeto", function(_id) { inventario_add(_id); });
// en el guion Yarn:  <<dar_objeto("espada")>>

/// metadatos de una línea (etiquetas para animación de retrato, emoción…)
var _meta = ChatterboxGetContentMetadata(box, 0);   // p.ej. "#enfadado"
```

---

## La API esencial (verificada en el código)

| Función | Qué hace |
|---|---|
| `ChatterboxLoadFromFile(archivo)` | Carga el guion Yarn |
| `ChatterboxCreate(fuente)` | Crea una conversación |
| `ChatterboxJump(box, nodo)` | Salta a un nodo del guion |
| `ChatterboxContinue(box)` | Avanza a la siguiente línea |
| `ChatterboxIsWaiting(box)` | ¿Esperando que elijas una opción? |
| `ChatterboxGetContentCount` / `GetContent` / `GetContentSpeaker` | Leer las líneas actuales |
| `ChatterboxGetOptionCount` / `GetOption` | Leer las opciones |
| `ChatterboxSelect(box, índice)` | Elegir una opción |
| `ChatterboxVariableGet` / `VariableSet` | Compartir estado con el juego |
| `ChatterboxAddFunction(nombre, método)` | Que el guion llame a tu código |
| `ChatterboxIsStopped(box)` | ¿Terminó la conversación? |

> 🔺 **No están en `buscar.py`** (son de librería). Verifica firmas en
> `11 - Código descargado/librerias/dialogos-y-narrativa/Chatterbox/scripts/`.

---

## Ver también

- [18 · Scribble](./18%20-%20Scribble%20-%20texto%20rico%20%28guía%20en%20español%29.md) — para dibujar lo que Chatterbox decide, con estilo
- [10 · Visual Novel y narrativa](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md) — montar la escena de diálogo completa
- [21 · Localización](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md) — traducir los guiones Yarn
- Repo oficial: <https://github.com/JujuAdams/Chatterbox> · Yarn: <https://yarnspinner.dev/>
