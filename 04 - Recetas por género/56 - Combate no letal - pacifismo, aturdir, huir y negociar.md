# 56 · Combate no letal — pacifismo, aturdir, huir y negociar

> Cómo se resuelve un encuentro **sin matar**: aturdir y noquear, huir de verdad (que el enemigo
> persiga o desista, no un menú), negociar o sobornar, intimidar, y por qué nada de esto vale
> nada si el juego no lo **reconoce** después. No repite el motor de daño (eso es
> [04 · 32](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md)), el diseño de
> encuentros en sí (eso es
> [04 · 33](./33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md)) ni
> el árbol de diálogo en sí (eso es
> [13 · 12](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/12%20-%20Diseño%20narrativo%20y%20diálogos.md)):
> este documento es el **enganche** de los tres hacia una salida que no termina en un cadáver.

---

## 1 · Los principios

### 1.1 Pacifismo como estilo de juego, no como parche de accesibilidad

Es una confusión fácil, porque los dos viven detrás de un interruptor: la asistencia de puntería
de [04 · 34 §4.4](./34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md#44-asistencia-de-puntería-como-ajuste-de-accesibilidad)
es «parte del kit» ([13 · 18 §1.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/18%20-%20Diseño%20de%20combate%20y%20de%20jefes.md#12--el-kit-del-jugador-los-verbos-antes-que-los-enemigos))
porque sin ella un verbo del jugador (disparar con precisión) directamente no existe para quien
tiene dificultad motriz fina. El pacifismo es distinto: **no falta ningún verbo si no está**, es
una restricción que el jugador se impone —o que el juego premia si se impone— por encima de un
combate que funciona igual de bien con o sin ella. Por eso la primera decisión no es de código:
es de **pilar** ([13 · 14 §1.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md#13--pilares-de-diseño-3-5-frases-que-resuelven-discusiones)):
¿puede el jugador **ganar** el juego sin matar a nadie, o el pacifismo es solo una capa de sabor
sobre un combate que igualmente termina en cadáveres? Las dos son respuestas legítimas —
*Dishonored* (Arkane, 2012) y *Undertale* (Toby Fox, 2015) contestan que sí; la inmensa mayoría
de *character action games* contesta que no, y está bien— pero hay que **decidirla antes**,
porque cambia qué partes de este documento hacen falta y cuáles no.

### 1.2 Las cinco vías, y con qué pieza ya construida engancha cada una

Ninguna de las cinco exige un sistema nuevo de cero: todas son una variación o una consecuencia
nueva sobre algo que la biblioteca ya resuelve.

| Vía | Qué le pasa al enemigo | Sistema que reutiliza | Qué es de verdad nuevo |
|---|---|---|---|
| **Aturdir y noquear** | Su vida llega a 0 por un golpe marcado como no letal: sale del combate, no muere | `MotorEfectos` de [04 · 32 §4.4](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md#44-el-motor-de-efectos-de-estado) | Un campo `no_letal` en la caja de golpe (§3.1) y una rama en la máquina de estados de `04 · 30 §5.7` |
| **Huir de verdad** | El enemigo pierde el contacto y **desiste**, en vez de perseguir para siempre | El medidor de detección de [04 · 45 §2.4](./45%20-%20Géneros%20sin%20receta%20propia%20-%20sigilo%2C%20horror%2C%20táctica%2C%20granja%20y%20idle.md#24--sistema-crítico-3--el-medidor-de-detección-y-cómo-cambia-de-estado) y la memoria de [04 · 31 §11](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md#11--percepción-ver-oír-recordar-y-avisar) | La decisión que ese documento deja explícitamente abierta (§3.2): qué hace `COMBATE` al degradarse de verdad |
| **Negociar o sobornar** | Una rama de diálogo cierra el encuentro sin un solo golpe | `Misiones` de [13 · 12 §6.5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/12%20-%20Diseño%20narrativo%20y%20diálogos.md#65-un-gestor-de-misiones-mínimo-con-estado-fallada) | Completar la misión del encuentro por una vía que no es matar a nadie (§3.3) |
| **Intimidar** | El enemigo decide por sí mismo que no le compensa seguir | Utility AI de [04 · 31 §7-8](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md) y la tabla de amenaza de [04 · 33 §4](./33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md#4--a-quién-atacan-la-tabla-de-amenaza-y-su-versión-ligera-de-un-jugador) | Una consideración más de utilidad: «miedo», leída contra la reputación del jugador (§3.4) |
| **Dormir o pacificar a distancia** | Como aturdir, pero sin alertar al resto y sin ruptura de sigilo | El mismo `no_letal` de §3.1, más el cono/oído de [04 · 45 §2.2](./45%20-%20Géneros%20sin%20receta%20propia%20-%20sigilo%2C%20horror%2C%20táctica%2C%20granja%20y%20idle.md#22--sistema-crítico-1--cono-de-visión-y-línea-de-visión-ya-existe) | Que el noqueo silencioso no dispare `hacer_ruido()` (§3.5) |

### 1.3 La consecuencia de diseño es la mitad del sistema

Un juego donde el jugador puede evitar matar pero el juego **no se entera** no tiene pacifismo:
tiene un jugador imponiéndose una regla que nadie más respeta, indistinguible de jugar mal a
propósito. La otra mitad —la que de verdad convierte «no maté a nadie» en una decisión de
diseño en vez de una anécdota del jugador— es que el mundo lo **reconozca**:

- **El sistema de Caos de *Dishonored*** pesa sobre todo las bajas letales frente a las
  neutralizaciones no letales, y ese número cambia «la cantidad de guardias presentes en cada
  zona y su fuerza, la cantidad de ratas, *weepers* y moscas de sangre», y el aprecio de los
  personajes por el protagonista — y decide cuál de los dos finales, uno positivo y uno sombrío,
  recibe el jugador (verificado por `WebSearch`, 2026-09-07; fuente en [§9](#9-fuentes)).
- ***Undertale*** exige la ruta pacifista completa **sin un solo enemigo muerto** (0 EXP/LOVE
  ganado en toda la partida) para desbloquear el final «True Pacifist», y el juego lo recuerda
  entre partidas — matar a uno solo, incluso mucho después, cierra esa puerta para siempre en esa
  misma partida (verificado por `WebSearch`, 2026-09-07; fuente en [§9](#9-fuentes)).

Ninguno de los dos ejemplos necesita una economía nueva: los dos son **un contador que ya
tienes** (`flag_sumar()` de [13 · 12 §6.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/12%20-%20Diseño%20narrativo%20y%20diálogos.md#62-los-flags-un-struct-global-plano-y-guardable))
leído en los sitios correctos: al decidir qué guardias hay en una zona, qué dice un NPC, y qué
final se dispara. El código está en §3.6.

---

## 2 · El método, paso a paso

### 2.1 Decide el alcance antes que el código

Tres niveles, de menor a mayor compromiso, y ninguno es «incompleto» si es el que pide tu juego:

1. **Opción puntual.** Un enemigo concreto, o un tipo de arma (una porra, dardos tranquilizantes)
   que aturde en vez de matar. No hace falta ni el contador de §3.6 ni tocar la ficha de
   encuentro: basta con §3.1.
2. **Sistema paralelo.** El jugador puede resolver la mayoría de encuentros sin matar, y el juego
   lo nota (recompensa, reacción de NPC), pero el juego **no** exige elegir uno de los dos modos
   de cabo a rabo. Aquí ya hace falta §3.6, y conviene marcar la ficha de encuentro (§2.2).
3. **Ruta completa.** Como *Undertale*: el juego reconoce y premia una partida enteramente sin
   bajas, con un final propio. Exige que **todo** encuentro de la campaña tenga salida no letal
   —no solo la mayoría— y que el contador de §3.6 se comprube en el punto de guardado o epílogo.

### 2.2 Marca la ficha de encuentro

La [ficha de encuentro de 13 · 18 §3.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/18%20-%20Diseño%20de%20combate%20y%20de%20jefes.md#32--ficha-de-encuentro)
ya recoge grupos, hueco de escape y arena; este documento le añade una fila (edición aplicada en
ese documento, no se repite aquí): **¿Tiene salida no letal?** sí / no, y si es sí, cuál de las
cinco vías de §1.2 aplica. Un encuentro sin marcar se trata como «no» por defecto: **el silencio
no es una salida no letal accidental**, es el jugador dándose cuenta tarde de que no la había.

### 2.3 Decide qué cuenta como «baja»

Antes de escribir una línea de código, fija la regla — cada proyecto la contesta distinto y las
dos son válidas, pero hay que **elegir**, no dejar que el código la decida por accidente:

- Un enemigo noqueado que después muere por una causa ajena (fuego ambiental, caída, otro
  enemigo que lo remata) ¿cuenta como baja del jugador? *Dishonored* dice que si el jugador causó
  la situación (dejarlo sobre una vía de tren, junto a fuego), sí cuenta.
- Un enemigo noqueado y **nunca revivido** (la partida termina con él inconsciente para siempre)
  ¿es equivalente a muerto para el contador de progreso, aunque no lo sea para el de bajas?

### 2.4 El noqueo no es gratis

Si aturdir cuesta lo mismo que matar (mismo tiempo, mismo riesgo, mismo daño necesario) todo
jugador lo elegirá siempre y «pacifismo» deja de ser una decisión de diseño para ser la única
opción razonable. Dale un coste real y distinto: un arma no letal con menos alcance o más lenta
de recargar (extiende `WeaponDef` de [04 · 34 §5.0](./34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md#50-extensión-de-weapondef-con-munición-y-balística)),
una ventana de golpe más corta, o la exigencia de acercarse por la espalda (sigilo,
[04 · 45 §2](./45%20-%20Géneros%20sin%20receta%20propia%20-%20sigilo%2C%20horror%2C%20táctica%2C%20granja%20y%20idle.md#2--sigilo)).

---

## 3 · Cómo se traduce a GameMaker

### 3.1 Aturdir y noquear: una tercera rama junto a «sigue con vida» y «muere»

`recibir_golpe()` ya calcula `_final` y lo resta de `combate.vida` (`04 · 32 §5.7`); lo único que
falta es que la instancia sepa, en el momento en que la vida llega a 0, si el golpe que la dejó
ahí estaba marcado como no letal. Se resuelve con el mismo patrón que ya usan `tipo` y
`penetracion` (`04 · 32 §2.2`): un **tercer campo opcional** en la caja de golpe.

```gml
// ---------------------------------------------------------------------------
// Extensión de la caja de golpe (global.ataques), sobre 04 · 32 §2.2
// ---------------------------------------------------------------------------
caja : { dx: 22, dy: -12, ancho: 30, alto: 24 },
dano : 18,
tipo : DanoTipo.CONTUNDENTE,
no_letal : true,              // NUEVO. Si falta, se asume false (letal, comportamiento actual)
```

```gml
// ---------------------------------------------------------------------------
// scr_combate_recibir — AÑADIDO al final del paso 5 de 04 · 32 §5.7, justo
// después de restar _final de combate.vida. No sustituye nada de ese paso.
// ---------------------------------------------------------------------------
combate.golpe_no_letal = variable_struct_exists(_caja, "no_letal") ? _caja.no_letal : false;
```

Y en el `Step` de `obj_entidad` (`04 · 30 §5.7`), la línea `if (combate.vida <= 0 &&
!fsm.is("muerto")) fsm.set("muerto");` gana una condición hermana **antes**, no en vez de:

```gml
// ---------------------------------------------------------------------------
// obj_entidad — Step. Sustituye SOLO la línea de "Muerte" de 04 · 30 §5.7,
// el resto del Step (control, i-frames) se queda exactamente igual.
// ---------------------------------------------------------------------------
if (combate.vida <= 0 && !fsm.is("muerto") && !fsm.is("noqueado"))
{
    if (combate.golpe_no_letal) fsm.set("noqueado"); else fsm.set("muerto");
}
```

El estado `noqueado` es una entrada más en `estados_del_jugador()`/`estados_del_enemigo()`
(el mismo struct que ya recibe `fsm_bind()`, `04 · 30 §5.5`): retira a la instancia del combate
(deja de ser objetivo de la tabla de amenaza, `04 · 33 §4`) sin destruirla, sin *loot* de matanza
—o con uno reducido, si el proyecto quiere premiar menos el noqueo que la muerte para no volverlo
estrictamente mejor en todos los sentidos— y anima un sprite «caído» en vez del de muerte:

```gml
// ---------------------------------------------------------------------------
// estados_del_enemigo() — entrada nueva junto a "muerto" (04 · 30 §5.5)
// ---------------------------------------------------------------------------
noqueado : {
    enter : function()
    {
        sprite_index = spr_enemigo_noqueado;
        combate.efectos.limpiar();             // 04 · 32 §5.4: no sigue tiqueando venenos
        loot_soltar(loot_tabla, LOOT_NOQUEO);   // tabla reducida frente a LOOT_MUERTE — 04 · 32
        flag_sumar("total_noqueos");            // §3.6
        senal_emitir("enemigo_noqueado", { enemigo: id });   // 04 · 16, para IA/objetivos que escuchan
    },
    step : function() { /* inmóvil; el resto de la IA ya no se ejecuta desde aquí */ }
}
```

> 💡 **No es lo mismo que el `aturdimiento` de `04 · 32 §4.5`.** Aquel es un efecto de estado
> **temporal** que corta el control unos fotogramas en mitad de un combate que sigue; este
> `noqueado` es una **salida** del combate, tan permanente como `muerto` hasta que algo externo
> lo revierta (una animación de reanimación, si el proyecto la quiere). Comparten motor
> (`MotorEfectos`) pero no comparten propósito — no dupliques uno para hacer el otro.

### 3.2 Huir de verdad: cerrando la decisión que `04 · 45 §2.4` deja abierta

Ese documento mide `pizarra.deteccion` y lo hace **bajar solo** en cuanto el jugador rompe línea
de visión — y dice explícitamente: *«Que `COMBATE` derive a combate real o a un *game over* es
una decisión de diseño, no de este sistema: el medidor solo mide, no castiga»*. Huir de verdad
**es** esa decisión, aplicada al caso en que `COMBATE` ya se disparó de verdad (no sigilo previo,
sino en mitad de la pelea): si `deteccion` cae por debajo del umbral de `DESPREVENIDO` mientras
la instancia sigue marcada como enemiga activa, el encuentro se cierra como **escapado**, un
tercer resultado distinto de «ganado» y de «perdido».

```gml
// ---------------------------------------------------------------------------
// obj_guardia — Step (extensión del tick de detección de 04 · 45 §2.4;
// AÑADIDO al final de ese mismo bloque, no lo sustituye)
// ---------------------------------------------------------------------------
if (pizarra.estado_alerta == EstadoAlerta.DESPREVENIDO && pizarra.en_combate)
{
    pizarra.en_combate = false;
    fsm.set("patrulla");
    senal_emitir("jugador_escapo", { enemigo: id, ultima_pos: [pizarra.ultima_x, pizarra.ultima_y] });
    flag_sumar("total_escapes");   // §3.6
}
```

La diferencia con el «Huir» de menú de [04 · 35 §5.8](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md#58-el-battlemanager-el-bucle-completo)
(`case "huir": if (irandom(1) == 1) room_goto(...)`) es exactamente la que separa un combate por
turnos de uno en tiempo real: allí es **una tirada instantánea** que resuelve el turno entero de
golpe; aquí es **una condición sostenida** —sin contacto visual, más allá del radio de oído
(`hacer_ruido`, `04 · 31 §11`) durante el tiempo que tarda `deteccion` en vaciarse— que se
comprueba fotograma a fotograma. Ni sustituye a la de `04 · 35` en un juego por turnos ni tiene
sentido en uno: son la misma decisión de diseño, resuelta con la gramática de cada género.

> ⚠️ **Sin un enemigo que investigue, «romper la línea de visión» es un truco barato.** La rama
> de investigación de `04 · 31 §11` (el enemigo va a `pizarra.ultima_x/ultima_y` antes de
> rendirse) es lo que evita que el jugador huya solo doblando la primera esquina; sin ella, esta
> sección es indistinguible de «el enemigo tiene memoria de pez». Ya está escrita, sólo hace
> falta no saltársela.

### 3.3 Negociar o sobornar: cerrar el encuentro por diálogo

Si el encuentro ya está modelado como una `Mision` (§1.2, `13 · 12 §6.5`), negociar es
completarla por una vía que **no** es `turno_atacar` — la misma simetría que ya tiene `fallar()`
(«perdiste sin que se acabara el combate») aplicada al sentido contrario: «ganaste sin pelear».
No hace falta un segundo sistema de misiones para esto, con reutilizar el que existe basta:

```gml
// ---------------------------------------------------------------------------
// scr_negociar — se llama desde un nodo de diálogo abierto EN MITAD del
// combate (una tecla de "hablar", o un disparador de 13 · 12 §6.3 que sólo
// existe mientras fsm.is("combate")).
// ---------------------------------------------------------------------------

/// @func negociar_intentar(_encuentro_id, _enemigo)
/// @desc Cierra el encuentro por negociación si las condiciones se cumplen.
/// @returns {Bool} true si el enemigo aceptó y el encuentro se cerró.
function negociar_intentar(_encuentro_id, _enemigo)
{
    // La condición de aceptar es del proyecto: aquí, vida por debajo de un
    // umbral (ya está perdiendo) O un flag narrativo puesto por el guion
    // (un NPC que nunca quiso pelear de verdad).
    var _acepta = (_enemigo.combate.vida < _enemigo.combate.vida_max * 0.3)
               || flag_leer($"{_encuentro_id}_dispuesto_a_negociar", false);

    if (!_acepta) return false;

    global.misiones.completar(_encuentro_id);   // 13 · 12 §6.5 — el encuentro ES la misión
    flag_poner($"encuentro_{_encuentro_id}_resuelto", "negociado");
    flag_sumar("total_negociaciones");           // §3.6

    with (_enemigo) { fsm.set("retirada"); }     // se va, no muere, no queda inconsciente
    senal_emitir("encuentro_negociado", { id: _encuentro_id });
    return true;
}
```

```gml
/// Uso, desde el nodo de diálogo (13 · 12 §6.1): la opción "Negociar" solo
/// aparece si el guion la ofrece — el sistema no la fuerza en todo enemigo.
new Linea("dlg_bandido_negociar", "bandido",
    function() { return negociar_intentar("encuentro_bandidos_camino", obj_bandido_lider); })
```

> 🔺 **`negociar_intentar()` no dibuja el diálogo.** Igual que `Misiones` (`13 · 12 §6.5`), sólo
> decide el estado; la UI de conversación es la de `13 · 12 §2-4`, sin cambios.

### 3.4 Intimidar: la IA que decide rendirse sola

Un enemigo que huye porque el jugador «da miedo» no necesita una rama nueva del árbol de
comportamiento: es una consideración más de utility AI (`04 · 31 §7-8`), comparada contra las que
ya existen (salud propia, distancia al jugador, número de aliados vivos). La entrada nueva es el
**miedo**, y se calcula con lo que la biblioteca ya lleva la cuenta: la tabla de amenaza de
[04 · 33 §4](./33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md#4--a-quién-atacan-la-tabla-de-amenaza-y-su-versión-ligera-de-un-jugador)
(cuánto daño ha hecho el jugador, a cuántos aliados ha derribado ya en este mismo encuentro).

```gml
// ---------------------------------------------------------------------------
// Consideración de utility nueva, añadida al array de considerations de
// 04 · 31 §7 (el resto del enemigo — atacar, cubrirse, perseguir — no cambia)
// ---------------------------------------------------------------------------
function consideracion_miedo(_pizarra)
{
    var _aliados_caidos = _pizarra.aliados_noqueados_o_muertos;   // incrementado por
                                                                   // "enemigo_noqueado"/"muerto" (senal_escuchar)
    var _vida_propia    = _pizarra.duena.combate.vida / _pizarra.duena.combate.vida_max;

    var _miedo = clamp(_aliados_caidos * 0.3 + (1 - _vida_propia) * 0.5, 0, 1);
    return _miedo * _pizarra.duena.arquetipo.valentia_inversa;   // 04 · 33 §1: cada arquetipo
                                                                   // responde distinto al miedo
}
```

```gml
// ---------------------------------------------------------------------------
// Acción "rendirse": gana cuando consideracion_miedo() supera a "atacar"
// ---------------------------------------------------------------------------
new Accion(function(_p) {
    _p.duena.fsm.set("rendido");           // deja de atacar; el jugador puede noquearlo gratis,
    flag_sumar("total_rendiciones");       // negociar (§3.3), o ignorarlo — sigue siendo su elección
    return ArbolEstado.EXITO;
}, "rendirse")
```

> 💡 **Un arquetipo cobarde (`04 · 33 §1`) ya tenía sentido narrativo antes de este documento**
> —huía al primer golpe—; lo único nuevo aquí es que la huida por miedo se **reconoce** como una
> tercera salida del encuentro, con su propio contador, en vez de ser solo una animación.

### 3.5 Dormir o pacificar a distancia: el noqueo silencioso

Un dardo tranquilizante es el mismo `no_letal : true` de §3.1, con dos diferencias: alcance
(hitscan o proyectil de `04 · 34`, no cuerpo a cuerpo) y que **no debe delatar al resto del
grupo**. La alerta de grupo se propaga por `senal_emitir("alerta_grupo", ...)` (`04 · 31 §11`);
basta con no emitirla en esta rama:

```gml
// ---------------------------------------------------------------------------
// Impacto de un dardo — variante de disparar_arma_avanzado() de 04 · 34 §5.3
// que marca el golpe como silencioso además de no letal
// ---------------------------------------------------------------------------
var _golpe_dardo = {
    caja : { dx: 0, dy: 0, ancho: 12, alto: 12 },
    dano : 999,              // fuerza vida a 0 de un golpe: el dardo noquea, no hiere
    tipo : DanoTipo.CONTUNDENTE,
    no_letal : true,
    silencioso : true        // NUEVO: no dispara hacer_ruido() ni alerta_grupo
};
```

```gml
// obj_enemigo — evento Collision con obj_dardo: NO llama a hacer_ruido() ni
// a senal_emitir("alerta_grupo", ...) si el golpe es silencioso — el resto
// del pipeline (recibir_golpe → noqueado, §3.1) se queda exactamente igual.
if (!_golpe.caja.silencioso)
{
    hacer_ruido(x, y, 80, "combate");   // 04 · 31 §11: solo el golpe RUIDOSO alerta
}
```

### 3.6 Las consecuencias reconocibles: el contador, la reacción del mundo, el final

Reutiliza `flag_sumar()`/`flag_leer()` de `13 · 12 §6.2` — no hace falta una estructura de datos
nueva, sólo mirarla en los tres sitios correctos:

```gml
// ---------------------------------------------------------------------------
// 1) El contador ya se rellena solo — cada rama de §3.1-3.4 llama a
//    flag_sumar() en su propio punto de cierre. Aquí sólo se LEE.
// ---------------------------------------------------------------------------

/// @func partida_es_pacifista()
/// @desc true si no hay ni una sola baja registrada en toda la partida.
function partida_es_pacifista()
{
    return flag_leer("total_bajas", 0) == 0;
}
```

```gml
// ---------------------------------------------------------------------------
// 2) Reacción del mundo: cuántos guardias hay en una zona (estilo Caos de
//    Dishonored, §1.3), leído al entrar en la room — no un sistema aparte,
//    una condición más sobre el spawn que ya existe (04 · 33 §6).
// ---------------------------------------------------------------------------
var _bajas = flag_leer("total_bajas", 0);
var _refuerzo = (_bajas > 5) ? 2 : ((_bajas > 0) ? 1 : 0);   // más guardias cuanta más sangre

for (var _i = 0; _i < _refuerzo; _i++)
{
    instance_create_layer(_spawn_x + _i * 32, _spawn_y, "Enemies", obj_guardia_refuerzo);
}
```

```gml
// ---------------------------------------------------------------------------
// 3) El final: se comprueba UNA vez, en el disparador del epílogo — no en
//    cada Step. Reutiliza los disparadores de 13 · 12 §6.3.
// ---------------------------------------------------------------------------
if (partida_es_pacifista())
{
    dialogo_reproducir("final_pacifista");    // 13 · 12 §3-4
}
else if (flag_leer("total_bajas", 0) > flag_leer("total_noqueos", 0) + flag_leer("total_negociaciones", 0))
{
    dialogo_reproducir("final_violento");
}
else
{
    dialogo_reproducir("final_neutral");
}
```

> ⚠️ **Este umbral de tres finales es un ejemplo, no una receta cerrada.** *Dishonored* usa un
> número continuo de Caos con dos finales; *Undertale* exige cero bajas exactas para el mejor de
> los tres. Cuál de los dos modelos encaja depende de la decisión de §2.1 — un «sistema paralelo»
> (nivel 2) suele bastar con un umbral como el de arriba; una «ruta completa» (nivel 3) necesita
> la condición exacta (`== 0`) de `partida_es_pacifista()`.

---

## 4 · Checklist

- [ ] La ficha de encuentro (`13 · 18 §3.2`) declara si tiene salida no letal, y de cuál vía —
      un encuentro sin marcar se trata como «no la tiene».
- [ ] El campo `no_letal` de la caja de golpe es **opcional**: un ataque que no lo declara sigue
      matando exactamente igual que antes de este documento.
- [ ] `noqueado` es un estado de la máquina de estados, no una rama de `if` suelta en el Step —
      se comprueba una vez, junto a la condición de `muerto` (§3.1).
- [ ] `MotorEfectos.limpiar()` se llama al entrar en `noqueado`, igual que al morir — un
      veneno no debe seguir tiqueando sobre un enemigo inconsciente.
- [ ] El *loot* de noqueo es distinto (o menor) que el de muerte — si no lo es, no hay decisión
      real que tomar (§2.4).
- [ ] «Huir de verdad» comprueba `deteccion` sostenida, no un solo frame sin contacto — un parpadeo
      de la línea de visión no debe cerrar el encuentro.
- [ ] El enemigo que pierde de vista al jugador **investiga** (`04 · 31 §11`) antes de rendirse:
      sin eso, huir es trivial y no se siente ganado.
- [ ] `negociar_intentar()` no se ofrece en todo enemigo por defecto: el guion decide dónde
      aparece la opción (§3.3).
- [ ] Un golpe `silencioso` (§3.5) nunca llama a `hacer_ruido()` ni a la señal `alerta_grupo`.
- [ ] `flag_sumar("total_bajas"/"total_noqueos"/...)` se llama **una sola vez** por enemigo, en
      el punto de cierre de su combate — nunca en un Step que se repite.
- [ ] El final (o la reacción del mundo) lee el contador en un disparador puntual, no en cada
      fotograma.

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Confundir `aturdimiento` (`04 · 32 §4.5`) con `noqueado` (§3.1) | El enemigo se levanta solo a los pocos segundos, en mitad de lo que debía ser una salida definitiva del combate | Son dos cosas distintas sobre el mismo motor: usa el estado `noqueado` de la FSM, no el efecto temporal |
| Dar el mismo *loot* por noquear que por matar | El jugador pacifista no pierde nada, y «no matar» deja de ser una decisión | Tabla de *loot* reducida para `LOOT_NOQUEO` (§3.1) |
| Cerrar el encuentro huido con un solo frame sin línea de visión | El jugador «escapa» agachándose un instante detrás de una caja | `deteccion` tiene que **vaciarse** (`04 · 45 §2.4`), no solo dejar de subir por un frame |
| Ofrecer «Negociar» en cualquier enemigo, sin condición | La opción aparece siempre y deja de significar nada | Condición explícita en `negociar_intentar()` — vida baja, o flag narrativo (§3.3) |
| Un dardo tranquilizante que sigue llamando a `hacer_ruido()` | El grupo entero se pone en alerta por un noqueo que debía ser silencioso | Comprobar `_golpe.caja.silencioso` antes de emitir el ruido (§3.5) |
| Leer el contador de bajas en el Step de cada enemigo | Coste de rendimiento innecesario, y riesgo de contar el mismo enemigo varias veces | `flag_sumar()` una vez, en el punto de cierre (muerte/noqueo/negociación); leer sólo en los disparadores (§3.6) |
| Marcar todo encuentro de la campaña como «sin salida no letal» por omisión y no revisarlo nunca | Un jugador que se comprometió al pacifismo llega a un jefe sin ninguna opción y lo vive como un fallo del juego, no una decisión de diseño | Revisar la ficha de encuentro (`13 · 18 §3.2`) de cada jefe **antes** de anunciar el pilar de §1.1 |

---

## Ver también

- [04 · 32 — Sistema de daño y efectos de estado](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) —
  `MotorEfectos`, el pipeline de daño y la caja de golpe que este documento extiende con
  `no_letal` (§3.1).
- [04 · 33 — Diseño de enemigos, encuentros y director de combate](./33%20-%20Diseño%20de%20enemigos%2C%20encuentros%20y%20director%20de%20combate.md) —
  la tabla de amenaza que alimenta la consideración de miedo (§3.4), y `EncuentroDef`, la unidad
  sobre la que se marca la salida no letal en la ficha de `13 · 18 §3.2`.
- [04 · 31 — IA de decisión](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento%2C%20utility%20y%20GOAP.md) —
  la percepción, la memoria y la utility AI que §3.2 y §3.4 reutilizan sin reescribir.
- [04 · 34 — Combate a distancia](./34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md) —
  `WeaponDef`, extendido en §2.4 con el arma no letal como opción de coste distinto.
- [04 · 35 — Combate por turnos y táctico en rejilla](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md) §5.8 —
  el «Huir» de menú con el que §3.2 contrasta la huida en tiempo real.
- [04 · 45 — Géneros sin receta propia](./45%20-%20Géneros%20sin%20receta%20propia%20-%20sigilo%2C%20horror%2C%20táctica%2C%20granja%20y%20idle.md) §2 —
  el cono de visión, la línea de visión y el medidor de detección sobre los que se construye
  toda la §3.2 y §3.5.
- [13 · 12 — Diseño narrativo y diálogos](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/12%20-%20Diseño%20narrativo%20y%20diálogos.md) §6 —
  `Misiones`, los flags y los disparadores que §3.3 y §3.6 reutilizan.
- [13 · 18 — Diseño de combate y de jefes](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/18%20-%20Diseño%20de%20combate%20y%20de%20jefes.md) §3.2 —
  la ficha de encuentro, ampliada con «¿tiene salida no letal?» (§2.2 de este documento).
- [13 · 14 — El documento de diseño](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/14%20-%20El%20documento%20de%20diseño%20-%20del%20one-pager%20al%20GDD%20completo.md) §1.3 —
  pilares de diseño: dónde se decide si el pacifismo es un estilo de juego (§1.1 de este
  documento) o una opción puntual.
- [04 · 27 — Accesibilidad](./27%20-%20Accesibilidad.md) — el otro tipo de interruptor detrás del
  que vive un verbo del jugador, y por qué no es el mismo caso que el pacifismo (§1.1).

---

## Fuentes

Todas consultadas el 2026-09-07.

- Halopedia — *Plasma Rifle* (consultado con `WebFetch`; usada aquí solo como referencia cruzada
  del vocabulario de «arma no letal frente a letal», no citada textualmente en este documento —
  la cita completa está en [04 · 34 §4.6](./34%20-%20Combate%20a%20distancia%20-%20armas%2C%20munición%20y%20balística.md#46-calor-como-recurso-de-disparo)) —
  <https://www.halopedia.org/Plasma_Rifle>
- *Chaos* — Dishonored Wiki (Fandom), consultado por `WebSearch` (el `WebFetch` directo a Fandom
  devolvió 402/403 en esta sesión, así que la cita se apoya en el resumen de búsqueda, no en la
  página completa leída palabra por palabra — marcado ⚠️ para el estándar de verificación del
  brief): confirma que el sistema pesa «sobre todo el número de neutralizaciones letales y no
  letales», cambia «la cantidad de guardias presentes en cada zona y su fuerza, [...] y el
  aprecio de varios personajes por el protagonista», y decide entre el final de caos bajo
  (positivo) y el de caos alto (sombrío) —
  <https://dishonored.fandom.com/wiki/Chaos>
- *True Pacifist Route* — Undertale Wiki, consultado por `WebSearch` (mismo aviso que arriba:
  resumen de búsqueda, no lectura completa — ⚠️): confirma que la ruta exige completar el juego
  «sin matar a un solo monstruo», que el juego «recuerda tus acciones» entre fases de la partida,
  y que matar incluso una sola vez cierra esa ruta para esa partida —
  <https://undertale.wiki/w/True_Pacifist_Route>
- `_indice/auditorias/r4-combate-colisiones-gdd.md` — hueco B7 (combate no letal, 🔴), el
  encargo de este documento.

⚠️ **Lo marcado en este documento.** Las dos fuentes de videojuegos (Dishonored, Undertale) se
verificaron por `WebSearch` tras fallar el acceso directo a Fandom por `WebFetch` (402/403): son
resúmenes de búsqueda que coinciden entre sí y con el conocimiento previo del dominio, no lectura
palabra por palabra de la fuente primaria — el mismo nivel de verificación que ya declaró la
auditoría `r4-combate-colisiones-gdd.md` para estos mismos dos ejemplos. La fuente de Halo (§9,
`04 · 34 §4.6`) sí se leyó completa con `WebFetch` y esa es la única citada textualmente.
