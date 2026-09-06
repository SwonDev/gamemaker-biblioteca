# 16 · Señales y desacoplamiento

> **Por qué existe esta receta:** al cruzar los tutoriales del foro oficial con esta biblioteca
> (01-09-2026) este era **el único sistema sin cubrir**. Y es de los que más ordenan un
> proyecto.
>
> **Fuentes:** [*How to Use Signals in GameMaker*](https://forum.gamemaker.io/index.php?threads/how-to-use-signals-in-gamemaker-and-what-the-hell-signals-even-are.115072/)
> de RefresherTowel (foro oficial) · la librería [Pulse](https://refreshertowel.itch.io/pulse)
> ($15) del mismo autor. **El código de abajo está escrito aquí desde cero** para LTS 2026.

---

## El problema

Tu jugador recibe daño. ¿Quién tiene que enterarse?

- La barra de vida, para bajar.
- La cámara, para temblar.
- El audio, para el sonido de golpe.
- El HUD, para parpadear en rojo.
- El sistema de logros, por si es la primera vez.

La forma ingenua es que el jugador los llame a todos:

```gml
/// obj_player · al recibir daño — ❌ acoplado
hp -= _dano;
obj_hud.parpadear();
obj_camara.temblar(8);
audio_play_sound(snd_dano, 5, false);
if (instance_exists(obj_logros)) obj_logros.comprobar_primer_golpe();
```

Funciona… hasta que:

- **quitas `obj_hud` de una room** → error de instancia inexistente;
- **añades un sexto sistema** → vuelves a tocar el jugador;
- **quieres probar al jugador aislado** → arrastra medio juego detrás;
- **dos sistemas se llaman entre sí** → dependencia circular.

El jugador ha acabado sabiendo de la cámara, del HUD y de los logros. No debería saber de
ninguno.

## La idea

Le das la vuelta: **el jugador anuncia lo que ha pasado y no le importa quién escucha.**

```gml
/// obj_player · al recibir daño — ✅ desacoplado
hp -= _dano;
senal_emitir("jugador_danado", { dano: _dano, hp: hp, x: x, y: y });
```

Y cada sistema se apunta por su cuenta:

```gml
/// obj_camara · Create
senal_escuchar("jugador_danado", function(_datos) {
    temblar(_datos.dano * 2);
});
```

El jugador **no sabe que la cámara existe**. Puedes borrar la cámara y el jugador sigue
funcionando.

---

## Implementación mínima (unas 40 líneas)

Un script global. No hace falta objeto ni librería.

```gml
/// scr_senales — funciones globales de señales

/// @desc Prepara el registro de señales. Llámalo una vez al arrancar el juego.
function senales_init() {
    global.__senales = {};       // { nombre: [ {duena, callback}, ... ] }
}

/// @desc Registra una función que se ejecutará cuando se emita `_nombre`.
/// @param {String} _nombre     Nombre de la señal
/// @param {Function} _callback Función que recibe el struct de datos
/// @param {Id.Instance} [_duena] Instancia propietaria (por defecto, quien llama)
function senal_escuchar(_nombre, _callback, _duena = self) {
    var _lista = global.__senales[$ _nombre];
    if (is_undefined(_lista)) {
        _lista = [];
        global.__senales[$ _nombre] = _lista;
    }
    array_push(_lista, { duena: _duena, callback: method(_duena, _callback) });
}

/// @desc Emite una señal. Todos los oyentes vivos reciben `_datos`.
/// @param {String} _nombre  Nombre de la señal
/// @param {Struct} [_datos] Información asociada
/// @returns {Real} Cuántos oyentes la recibieron
function senal_emitir(_nombre, _datos = {}) {
    var _lista = global.__senales[$ _nombre];
    if (is_undefined(_lista)) return 0;

    var _vivos = [], _n = 0;
    for (var _i = 0; _i < array_length(_lista); _i++) {
        var _o = _lista[_i];
        // descartar oyentes cuya instancia ya no existe
        if (is_struct(_o.duena) || instance_exists(_o.duena)) {
            _o.callback(_datos);
            array_push(_vivos, _o);
            _n++;
        }
    }
    global.__senales[$ _nombre] = _vivos;   // limpieza automática
    return _n;
}

/// @desc Da de baja a una instancia de una señal, o de todas si se omite el nombre.
function senal_olvidar(_duena, _nombre = undefined) {
    var _nombres = is_undefined(_nombre)
                 ? variable_struct_get_names(global.__senales)
                 : [_nombre];
    for (var _i = 0; _i < array_length(_nombres); _i++) {
        var _n = _nombres[_i];
        global.__senales[$ _n] = array_filter(global.__senales[$ _n],
            function(_o) { return _o.duena != _duena; });
    }
}
```

> 🔺 **Dos detalles de LTS 2026 que hacen que esto funcione:**
>
> - **`method(_duena, _callback)`** ata la función a su instancia. Sin esto, dentro del callback
>   `self` sería quien emitió la señal, no quien la escucha, y `temblar()` fallaría.
>   Ver [métodos](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Overview/Method_Variables.md).
> - **`global.__senales[$ _nombre]`** es el **acceso por struct**, que permite claves con
>   nombre dinámico. Ver [structs](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Overview/Structs.md).

### Uso

```gml
/// obj_arranque · Create — una sola vez, en la primera room
senales_init();

/// obj_hud · Create
senal_escuchar("jugador_danado", function(_d) {
    alpha_rojo = 1;
    hp_mostrado = _d.hp;
});

/// obj_camara · Create
senal_escuchar("jugador_danado", function(_d) { temblar(_d.dano * 2); });
senal_escuchar("jefe_derrotado",  function(_d) { temblar(30); });

/// obj_player · Clean Up — ¡importante!
senal_olvidar(id);
```

---

## Las tres trampas

### 1. Oyentes zombis

Una instancia destruida que sigue en la lista provoca un error al emitir. Se cubre por dos
lados: `senal_emitir` **descarta sola** a los que ya no existen, y aun así conviene llamar a
`senal_olvidar(id)` en el **Clean Up**.

> 💡 **Clean Up, no Destroy.** El evento Destroy **no se ejecuta** al cambiar de room ni al
> cerrar el juego; Clean Up sí. Es el sitio correcto para soltar recursos.

### 2. Señales que se emiten a sí mismas

Si el oyente de `"puerta_abierta"` emite `"puerta_abierta"`, tienes un bucle infinito y el juego
se cuelga sin mensaje de error. Si un oyente necesita emitir, **que sea otra señal distinta**.

### 3. Convertirlo todo en señales

Las señales son para **avisar de hechos consumados** a sistemas que no se conocen entre sí. No
son para todo:

| Situación | Herramienta |
|---|---|
| «Ha ocurrido X» y varios sistemas reaccionan | ✅ **Señal** |
| Necesito un valor **ahora** y con respuesta | ❌ Llamada directa a función |
| El objeto padre define comportamiento común | ❌ `event_inherited` |
| Un objeto manda sobre sus propios hijos | ❌ Referencia directa: no están desacoplados |

---

## Señales útiles en un juego de verdad

| Señal | Emite | Escuchan |
|---|---|---|
| `jugador_danado` | jugador | HUD, cámara, audio, logros |
| `jugador_muerto` | jugador | gestor de partida, música, estadísticas |
| `enemigo_muerto` | enemigo | puntuación, sueltas, logros, oleadas |
| `objeto_recogido` | ítem | inventario, HUD, audio |
| `sala_completada` | gestor de sala | puertas, música, guardado |
| `ajustes_cambiados` | menú | audio, pantalla, controles |
| `idioma_cambiado` | menú | **todo** el texto en pantalla |

> 💡 **`ajustes_cambiados` e `idioma_cambiado` son las que más rentan.** Sin señales, cambiar
> el idioma obliga a que el menú conozca cada objeto que dibuja texto. Con señales, cada objeto
> se refresca solo.

---

## Depurar señales

El problema del desacoplamiento es que **cuesta ver quién escucha qué**. Añade esto:

```gml
/// @desc Vuelca al registro de salida el estado del sistema de señales.
function senales_debug() {
    var _nombres = variable_struct_get_names(global.__senales);
    show_debug_message($"=== señales registradas: {array_length(_nombres)} ===");
    for (var _i = 0; _i < array_length(_nombres); _i++) {
        var _n = _nombres[_i];
        show_debug_message($"  {_n}: {array_length(global.__senales[$ _n])} oyentes");
    }
}
```

> 🔺 **`$"texto {variable}"`** son las **plantillas de cadena** de GameMaker moderno: mucho más
> legibles que concatenar con `+` y `string()`. Ver
> [Strings](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Strings/Strings.md).

---

## ¿Merece la pena una librería?

[**Pulse**](https://refreshertowel.itch.io/pulse) ($15, RefresherTowel) hace esto con más
funciones: prioridades, señales de un solo uso, espacios de nombres.

**El criterio honesto:** las 40 líneas de arriba cubren el 90 % de los casos y no añaden
dependencias. Pásate a una librería cuando de verdad necesites prioridades o señales
diferidas, no antes.

---

## Ver también

- [Máquinas de estados](./15%20-%20Game%20feel%20y%20juice.md) y las librerías del tema
  `maquinas-de-estados` en [`11 - Código descargado`](../11%20-%20Código%20descargado/_CATALOGO.md)
- [Qué hacen de verdad los proyectos reales](../07%20-%20Ecosistema/15%20-%20Qué%20hacen%20de%20verdad%20los%20proyectos%20reales.md)
  — por qué `with` y `event_inherited` son tan usados
- Comprueba cualquier función antes de usarla: `python3 "_indice/buscar.py" method`
