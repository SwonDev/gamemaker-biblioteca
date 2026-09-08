# 57 · Selección de nivel y capítulo

> La pantalla donde el jugador elige **qué nivel jugar**, con lo que ya completó y lo que
> todavía no ha desbloqueado. La auditoría `_indice/auditorias/r5-juego-completo.md` (hallazgo
> B3) confirmó que esta biblioteca no tenía receta: `04 · 04` menciona `rm_worldmap` al pasar y
> `04 · 06` resuelve el mundo interconectado de un metroidvania, pero ninguno de los dos cierra
> el caso más común — plataformas, puzzle o arcade con niveles **discretos y numerados**.
>
> **Lo que NO cubre, porque ya está resuelto en otro sitio:** el scroll y la navegación de una
> lista larga (mismo mecanismo, otro contenido) →
> [04 · 18](./18%20-%20Menús%20con%20scroll%20y%20navegación.md); el mundo persistente e
> interconectado de un metroidvania (sin niveles discretos que elegir, se explora) →
> [04 · 06](./06%20-%20Metroidvania.md); dónde y cómo se guarda el progreso →
> [`scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml) y
> [13 · 05, componente n) Ranura de guardado](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#n-ranura-de-guardado-metadatos-miniatura-y-guardando);
> el lugar de esta pantalla en el arco completo del juego →
> [04 · 00 §3](./00%20-%20Anatomía%20de%20un%20juego%20completo.md#3--splash-y-menú-principal).

---

## 1 · Los principios

### 1.1 Tres formas de organizar el avance, y cuál necesitas

| Forma | Cómo se elige el siguiente nivel | Ejemplo | Receta |
|---|---|---|---|
| **Lineal estricta** | No se elige: el juego encadena niveles solo, sin pantalla de selección | Un arcade corto de una sesión | No hace falta esta receta: `room_goto(siguiente_nivel)` basta |
| **Capítulos / niveles discretos** | El jugador ve una lista o rejilla y elige entre los desbloqueados | *Angry Birds*, *Super Mario Bros*, la mayoría de los puzzle | **Esta receta** |
| **Mundo interconectado** | No hay pantalla de selección: se explora y el propio mapa es la navegación | Metroidvania, mundo abierto | [04 · 06](./06%20-%20Metroidvania.md) — no repitas esta receta ahí |

Si tu juego es lineal estricto o un mundo interconectado, esta pantalla **no aplica** — dilo
explícitamente en el checklist de `04 · 00` («no aplica: juego lineal de una sola sesión»),
igual que pide `13 · 14 §1.5` para cualquier sección que no corresponda. No es un hueco: es una
decisión de diseño.

### 1.2 Un nivel, como dato

La pantalla de selección no es más que la vista de una tabla. Cada nivel necesita, como mínimo:

- **Un identificador estable** (`"nivel_01"`), no un índice de array. Si algún día reordenas o
  insertas un nivel en medio, un índice desincroniza cualquier partida guardada; un id no.
- **Un requisito de desbloqueo** — normalmente «completa el anterior», a veces un grafo más
  complejo (ver el **grafo de gating** de
  [13 · 14 §2.20](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#220--el-catálogo-de-diagramas-de-diseño)
  si el desbloqueo no es una cadena simple).
- **Un resultado**, si el género lo tiene: completado sí/no, mejor puntuación, estrellas.

### 1.3 El progreso vive en la partida guardada, no en variables sueltas

Este es el error más caro de la sección (ver §5): guardar «desbloqueado» como una bandera
independiente del resultado. Se desincroniza en cuanto alguien edita a mano un guardado, prueba
en el IDE saltándose niveles, o migra el esquema. La regla única: **«desbloqueado» se calcula
siempre a partir de «completado»**, nunca se guarda por separado.

---

## 2 · El método, paso a paso

1. **Define el catálogo de niveles como datos** — un array de structs en el objeto que gestiona
   la selección, o un `.json` si el catálogo es largo (mismo criterio que
   [13 · 02 §4](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/02%20-%20Diseño%20de%20niveles.md#4--la-hoja-de-nivel-la-plantilla-que-se-rellena-antes-de-construir)
   para la hoja de nivel).
2. **Decide la condición de desbloqueo**: cadena lineal (cada nivel requiere el anterior) es el
   90 % de los casos; si el tuyo se ramifica, dibuja el grafo de gating antes de programar
   nada.
3. **El progreso se guarda dentro de la misma ranura que el resto de la partida**
   (`scr_save_load.gml`, §3.2 de esta receta) — no en un archivo aparte. Una partida y su
   progreso de niveles son el mismo dato; separarlos es la forma más rápida de que se
   desincronicen entre sí.
4. **Diseña la pantalla**: rejilla o lista con miniatura, nombre, estado (bloqueado /
   desbloqueado / completado) y resultado. Si hay más niveles de los que caben en pantalla,
   reutiliza el scroll de [04 · 18](./18%20-%20Menús%20con%20scroll%20y%20navegación.md) — el
   mecanismo de cursor, ventana y flechas ▲▼ es exactamente el mismo, solo cambia lo que se
   dibuja en cada fila.
5. **Conecta con «Continuar» del menú principal** (`04 · 00 §3`): «Continuar» salta directo al
   último nivel jugado sin pasar por esta pantalla; «Selección de nivel» (o «Mapa», o
   «Capítulos», el rótulo que uses) es la que deja elegir cualquiera de los desbloqueados.

---

## 3 · Cómo se traduce a GameMaker

### 3.1 El catálogo de niveles

```gml
/// obj_seleccion_nivel · Create
/// Verificado: room, array de structs (01 · 04)

niveles = [
    { id: "nivel_01", nombre: txt("nivel_01_nombre"), room_destino: rm_zona1,
      miniatura: spr_niv01_mini, requiere: [] },
    { id: "nivel_02", nombre: txt("nivel_02_nombre"), room_destino: rm_zona2,
      miniatura: spr_niv02_mini, requiere: ["nivel_01"] },
    { id: "nivel_03", nombre: txt("nivel_03_nombre"), room_destino: rm_zona3,
      miniatura: spr_niv03_mini, requiere: ["nivel_02"] },
];

// Carga el progreso desde la misma ranura que usa menu_continuar() (§3.5) — sin esto,
// la Draw GUI de §3.4 lee global.progreso_niveles antes de que exista y revienta en
// el primer frame. Sin partida guardada (primera vez que se juega), un struct vacío
// deja todos los niveles sin requisitos desbloqueados (nivel_desbloqueado(), §3.3).
var _datos_partida = load_game("slot1");
global.progreso_niveles = (is_struct(_datos_partida) && struct_exists(_datos_partida, "progreso_niveles"))
    ? _datos_partida.progreso_niveles
    : {};
```

> 💡 **`miniatura` es un sprite propio del nivel, no una captura dinámica.** A diferencia de la
> ficha de una ranura de guardado (que muestra una captura real de la partida — ver
> [13 · 05, componente n)](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#n-ranura-de-guardado-metadatos-miniatura-y-guardando)),
> la miniatura de un nivel es arte estático que preparas de antemano: es contenido, no un
> registro de partida.

### 3.2 El progreso, dentro de los datos que ya guardas

```gml
/// Fragmento de los _datos que le pasas a save_game() — no un archivo aparte
var _datos = {
    // … el resto de tu partida (posición, inventario, vida…) …
    ultimo_nivel_jugado: "nivel_02",
    progreso_niveles: {
        nivel_01: { completado: true,  mejor_puntuacion: 1200, estrellas: 3 },
        nivel_02: { completado: false, mejor_puntuacion: 0,    estrellas: 0 },
        nivel_03: { completado: false, mejor_puntuacion: 0,    estrellas: 0 },
    },
};
save_game("slot1", _datos);
```

> ⚠️ **Este struct viaja dentro de `_datos`, el mismo argumento que ya usa `save_game()`
> ([06 · scr_save_load.gml](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml)).** No inventes
> un segundo archivo de progreso: `load_game_recover()` ya trae la red de seguridad de backups
> y checksum, y un archivo aparte no la tendría.

### 3.3 Desbloqueado se CALCULA, nunca se guarda

```gml
/// @func nivel_desbloqueado(_nivel, _progreso)
/// @desc true si todos los niveles que _nivel.requiere están completados en _progreso.
///       Un nivel sin requisitos (array vacío) siempre está desbloqueado.
/// @param {Struct} _nivel     Una entrada del array `niveles` (§3.1).
/// @param {Struct} _progreso  El struct `progreso_niveles` cargado de la partida (§3.2).
/// @returns {Bool}
function nivel_desbloqueado(_nivel, _progreso) {
    var _n = array_length(_nivel.requiere);
    for (var _i = 0; _i < _n; _i++) {
        var _id_requisito = _nivel.requiere[_i];
        if (!struct_exists(_progreso, _id_requisito))          return false;
        if (!_progreso[$ _id_requisito].completado)            return false;
    }
    return true;
}
```

> 🔺 **Esta función es la que evita la desincronización de §1.3.** No existe ningún
> `nivel.desbloqueado = true` guardado en disco: el estado se deriva cada vez que se dibuja la
> pantalla, a partir de lo único que sí se guarda (`completado`). Si cambias la cadena de
> requisitos en una actualización del juego, las partidas viejas se recalculan solas — no hace
> falta migrar nada.

### 3.4 La pantalla: rejilla con tres estados visuales

```gml
/// obj_seleccion_nivel · Draw GUI
/// Verificado: draw_sprite_ext, draw_text_color, draw_text, array_length, string_repeat

var _cols = 3;
var _celda = 180;
var _x0 = 100, _y0 = 100;
var _n = array_length(niveles);

for (var _i = 0; _i < _n; _i++) {
    var _nv  = niveles[_i];
    var _fil = _i div _cols;
    var _col = _i mod _cols;
    var _cx  = _x0 + _col * _celda;
    var _cy  = _y0 + _fil * _celda;

    var _desbloqueado = nivel_desbloqueado(_nv, global.progreso_niveles);
    var _resultado     = struct_exists(global.progreso_niveles, _nv.id)
                          ? global.progreso_niveles[$ _nv.id] : undefined;
    var _completado     = _desbloqueado && is_struct(_resultado) && _resultado.completado;

    if (!_desbloqueado) {
        // bloqueado: miniatura oscurecida + candado. NUNCA se dibuja igual que un nivel jugable
        // — ver 13/05 §1.6 (affordance: un elemento inactivo debe PARECER inactivo).
        draw_sprite_ext(_nv.miniatura, 0, _cx, _cy, 1, 1, 0, c_gray, 0.5);
        draw_text_color(_cx + 70, _cy + 70, "🔒", c_white, c_white, c_white, c_white, 1);
        continue;
    }

    draw_sprite_ext(_nv.miniatura, 0, _cx, _cy, 1, 1, 0, c_white, 1);
    draw_text(_cx, _cy + 140, _nv.nombre);

    if (_completado) {
        var _estrellas = string_repeat("★", _resultado.estrellas)
                        + string_repeat("☆", 3 - _resultado.estrellas);
        draw_text(_cx, _cy + 160, _estrellas);
    }

    if (_i == seleccion) draw_text(_cx - 20, _cy + 70, ">");
}
```

> 💡 **Tres estados, no dos.** «Bloqueado» y «desbloqueado sin completar» son visualmente
> distintos del mismo modo que «desbloqueado sin completar» y «completado» lo son: un jugador
> que ve la misma miniatura para «no lo he probado» y «lo bloquea otro nivel» no entiende por
> qué no puede entrar.

### 3.5 «Continuar» frente a «Selección de nivel»

```gml
/// scr_menu — dos entradas del menú principal (04 · 00 §3) que leen el mismo progreso

/// @func menu_continuar()
/// @desc Salta directo al último nivel jugado, sin pasar por la pantalla de selección.
function menu_continuar() {
    var _datos = load_game("slot1");
    if (!is_struct(_datos)) { return; }   // "Continuar" ya está desactivada si esto pasara (04/00 §3)
    room_goto(nivel_buscar_room(_datos.ultimo_nivel_jugado));
}

/// @func nivel_buscar_room(_id)
/// @returns {Asset.GMRoom}
function nivel_buscar_room(_id) {
    var _n = array_length(niveles);
    for (var _i = 0; _i < _n; _i++) {
        if (niveles[_i].id == _id) { return niveles[_i].room_destino; }
    }
    return niveles[0].room_destino;   // fallback: el primer nivel, nunca un room inexistente
}
```

---

## 4 · Checklist

- [ ] Cada nivel tiene un **id estable** (string), nunca un índice de array
- [ ] «Desbloqueado» se **calcula** desde `completado` (§3.3); no existe ningún campo
      `desbloqueado` guardado por separado
- [ ] El progreso de niveles vive **dentro** de la misma ranura que el resto de la partida
      (`scr_save_load.gml`), no en un archivo propio
- [ ] Un nivel bloqueado se ve claramente distinto de uno desbloqueado sin completar (§3.4)
- [ ] Hay foco/cursor navegable con teclado y mando, con el mismo criterio de
      [13 · 05 §2.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#22-navegación-con-mando-y-teclado-foco-orden-envolvente-y-repetición)
      que cualquier otro menú
- [ ] Si hay más niveles de los que caben en pantalla, usa el scroll de
      [04 · 18](./18%20-%20Menús%20con%20scroll%20y%20navegación.md) en vez de encoger la
      rejilla hasta ilegible
- [ ] «Continuar» del menú principal no pasa por esta pantalla; «Selección de nivel» sí
- [ ] Si tu juego es lineal estricto o un mundo interconectado sin niveles discretos, esta
      pantalla está marcada **«no aplica: <razón>»** en el checklist de
      [04 · 00](./00%20-%20Anatomía%20de%20un%20juego%20completo.md#el-checklist-de-juego-completo),
      no omitida en silencio

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Qué se ve | La causa real | La corrección |
|---|---|---|---|
| **Guardar «desbloqueado» como campo aparte** | Un nivel queda bloqueado para siempre aunque el anterior esté completado (o al revés) | Dos fuentes de verdad para el mismo hecho, que se desincronizan | Derívalo siempre de `completado` (§3.3); nunca lo guardes |
| **Usar el índice del array como id** | Insertar un nivel nuevo en medio de la lista desordena el progreso de partidas ya guardadas | El índice cambia de significado al reordenar; el id no | Un `id` de string estable por nivel, nunca `niveles[i]` como clave |
| **Un nivel bloqueado se dibuja igual que uno jugable** | El jugador pincha y no pasa nada, sin saber por qué | Falta el estado visual «bloqueado» (§3.4) | Oscurecer + icono de candado, siempre — no solo desactivar el clic |
| **Progreso de niveles en un archivo separado del guardado principal** | Un jugador recupera el guardado de un backup y el progreso de niveles no coincide | Dos archivos que deberían ser uno solo se desincronizan al primer fallo | Todo dentro de `_datos` de `save_game()` (§3.2) |
| **Un catálogo de niveles fijo, sin `requiere`** | Añadir una rama alternativa de niveles obliga a reescribir toda la lógica de desbloqueo | Se codificó «nivel N+1 requiere nivel N» a fuego en vez de como dato | `requiere: []` es un array — vacío es «siempre desbloqueado», con varios ids es un grafo |

---

## Ver también

- [04 · 00 — Anatomía de un juego completo §3](./00%20-%20Anatomía%20de%20un%20juego%20completo.md#3--splash-y-menú-principal) — dónde encaja esta pantalla en el arco completo, y el checklist maestro
- [04 · 18 — Menús con scroll y navegación](./18%20-%20Menús%20con%20scroll%20y%20navegación.md) — el mecanismo de cursor/ventana/scroll que reutiliza §3.4 si hay muchos niveles
- [04 · 06 — Metroidvania](./06%20-%20Metroidvania.md) — la alternativa cuando NO hay niveles discretos que elegir, sino un mundo interconectado
- [06 · scr_save_load.gml](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml) — dónde vive de verdad el progreso de niveles (§3.2)
- [13 · 02 §4 — La hoja de nivel](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/02%20-%20Diseño%20de%20niveles.md#4--la-hoja-de-nivel-la-plantilla-que-se-rellena-antes-de-construir) — el diseño de contenido de cada nivel, antes de que exista como fila de esta pantalla
- [13 · 14 §2.20 — El grafo de gating](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#220--el-catálogo-de-diagramas-de-diseño) — cuando el desbloqueo no es una cadena lineal simple
- [13 · 05 §1.6 — Affordance](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md) y [componente n) Ranura de guardado](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#n-ranura-de-guardado-metadatos-miniatura-y-guardando) — el estado visual inactivo, y la diferencia entre la miniatura de un nivel (arte fijo) y la de una ranura de guardado (captura real)
- [01 · 04 — Structs y constructores](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md#34-con-el-accessor--) — el accessor `[$ ]` usado en §3.3 y §3.4
