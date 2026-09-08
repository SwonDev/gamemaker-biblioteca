# 33 · Diseño de enemigos, encuentros y director de combate

> Qué presión aplica cada arquetipo de enemigo, cómo se combinan varios en un encuentro sin
> volverse ruido, quién reparte los turnos de ataque para que no te golpeen seis a la vez, a
> quién atacan cuando hay más de un objetivo posible, y quién sube y baja la tensión de la
> partida sin que se note. Es el documento del **grupo**.
>
> **No cubre**: cómo se mueve un enemigo individual —*seek*, *flee*, patrulla, *flocking*— está
> en [23 · IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md).
> Cómo decide un enemigo individual qué hacer —árbol de comportamiento, utility, GOAP,
> percepción y alerta de grupo— está en
> [31 · IA de decisión](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento,%20utility%20y%20GOAP.md),
> que este documento **no repite**. Cuánto duele cada golpe y los efectos de estado (veneno,
> aturdimiento, escudos, resistencias) están en
> [32 · Sistema de daño y efectos de estado](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md)
> — documento hermano de esta misma auditoría, escrito en paralelo a este: si el enlace no
> resuelve todavía es que se está terminando.
>
> **Hueco detectado:** la biblioteca ya tenía movimiento (23), decisión individual (31) y
> combate cuerpo a cuerpo (30), pero ningún documento trataba el enemigo como pieza de un
> **grupo diseñado a propósito**: qué rol cumple cada uno, cómo se reparten los turnos de
> ataque, a quién apunta el grupo cuando hay varios objetivos, y quién decide cuándo aprieta
> la partida y cuándo la suelta. Este documento lo cierra.

---

## 1 · El vocabulario: arquetipos, o qué presión aplica cada enemigo

Marty Stratton, director del *Doom* de 2016, describe el combate del juego como un tablero:
**«cada nivel es un tablero de juego, el jugador y los monstruos son las piezas»**. Hugo
Martin, su director creativo, lo contrasta con el *Doom 3* anterior: **«el Terminator no
está flanqueando enemigos desde una puerta; el Terminator está corriendo y masacrando
gente»**. A esa filosofía la llamaron internamente *push-forward combat* — «combate que
empuja hacia delante»: el juego castiga la pasividad y recompensa la agresión (el *Glory
Kill* y la motosierra devuelven vida, munición y armadura al rematar).

Lo que interesa aquí no es imitar *Doom*, sino robarle el método: **un enemigo no es un
objetivo con vida, es una pieza que aplica un tipo de presión concreto.** Kurt Loudy, diseñador
de IA del estudio, resume la progresión de dificultad de los demonios con una imagen de artes
marciales: los zombis son **«cinturones blancos en una película de Bruce Lee»** — sirven para
que el jugador «se sienta genial matándolos» antes de que aparezca el «cinturón negro».

> 💡 **Esto es la misma idea que ya usa 13 · 01 §1.6 — Diseño elegante: pocas reglas, muchas
> situaciones.** Un arquetipo bien definido es una regla; combinar dos o tres arquetipos
> genera la situación. No hace falta inventar un enemigo nuevo para cada encuentro: hace falta
> combinar mejor los seis de abajo.

Cada arquetipo se define respondiendo a **cuatro preguntas**, no a un número de vida:

1. **¿Qué presión aplica?** — el problema que le plantea al jugador.
2. **¿A qué obliga?** — la acción concreta que el jugador debe tomar para no sufrirla.
3. **¿Cómo se contrarresta?** — la herramienta o decisión que lo neutraliza.
4. **¿Qué pasa si se ignora?** — por qué no puedes simplemente no hacerle caso.

| Arquetipo | Presión que aplica | Obliga al jugador a | Se contrarresta con | Vida en golpes* | TTK objetivo* | Alcance | Telegrafía |
|---|---|---|---|---|---|---|---|
| **Embestidor** (*rusher*) | Cierra distancia rápido; castiga la quietud | Moverse, no plantarse | Golpe de área o esquiva con i-frames ([30 §4.5](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md)) | 2 (tier *Baba*) | 0,2 – 0,4 s | Cuerpo a cuerpo | 8-14 fotogramas |
| **Tirador** (*ranged*) | Daño constante a media distancia | Buscar cobertura o cerrar distancia | Cerrar distancia o interponer un muro | 3 (tier *Arquero*) | 0,4 – 0,8 s | Media (150-300 px) | Retículo o parpadeo antes de disparar |
| **Muro** (*tank*) | Bloquea el paso, absorbe el foco del grupo | Rodearlo, repartir el daño, o priorizar a otro | Rodearlo (§2) o daño perforante | 12 (tier *Bruto*) | 2 – 3 s | Cuerpo a cuerpo | Arranque largo, claramente leído |
| **Enjambre** (*swarm*) | Presión numérica; ninguno es peligroso solo | Usar ataques de área, no enfocar a uno | Área de efecto y empuje (*knockback*) | 1-2 cada uno | < 0,2 s cada uno | Cuerpo a cuerpo | Casi nula: la amenaza es el número |
| **Francotirador** (*sniper*) | Amenaza a larga distancia mientras estás distraído | Romper línea de visión, priorizarlo | Cobertura + amenaza prioritaria (§4) | 2-3 (frágil) | 0,2 – 0,4 s si llegas | Larga (> 300 px) | Puntero o parpadeo, con retardo largo |
| **Apoyo** (*support*) | Cura o potencia a otros; casi no ataca | Decidir si matarlo ya o ignorarlo | Foco de objetivo prioritario (§4) | 2-4 | variable | Media | Aura o gesto de invocación visible |

\* *«Golpes» y TTK reutilizan el vocabulario de*
[`13 · 01 — Diseño de juego`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md)
*§4.4 (Baba = 2 golpes, Arquero = 3, Bruto = 12, Jefe = 200, con la pistola de referencia de
esa sección). No se repite la fórmula del TTK aquí: sólo se asigna cada arquetipo a un nivel de
esa tabla. Enjambre y Francotirador son matices nuevos — la fragilidad alta y la presión no
proporcional al daño que hacen.*

```gml
/// scr_arquetipos
/// @func ArquetipoDef(_nombre, _obj, _presion, _obliga_a, _contraparte, _vida_golpes,
///                     _alcance, _telegrafia_fr, _peso_rejilla, _peso_ataque)
/// @desc La ficha de diseño de un arquetipo, hecha datos. `_peso_rejilla` y `_peso_ataque`
///       son el coste que le cuesta al gestor de fichas de ataque (§3); no son arbitrarios,
///       están puestos para que un muro cueste más que un enjambre.
function ArquetipoDef(_nombre, _obj, _presion, _obliga_a, _contraparte, _vida_golpes,
                       _alcance, _telegrafia_fr, _peso_rejilla, _peso_ataque) constructor {
    nombre        = _nombre;
    obj           = _obj;             // el objeto de GameMaker que instancia este arquetipo
    presion       = _presion;         // texto: para el editor de encuentros o la wiki interna
    obliga_a      = _obliga_a;
    contraparte   = _contraparte;
    vida_golpes   = _vida_golpes;     // en "golpes estándar" — 13 · 01 §4.4
    alcance       = _alcance;
    telegrafia_fr = _telegrafia_fr;   // fotogramas de anticipación antes de golpear
    peso_rejilla  = _peso_rejilla;    // §3 · GestorFichas
    peso_ataque   = _peso_ataque;     // §3 · GestorFichas
}

/// obj_control · Game Start — la tabla de arquetipos se construye UNA vez
global.arquetipos = {
    embestidor: new ArquetipoDef("embestidor", obj_embestidor,
        "cierra distancia rápido y castiga la quietud", "moverte, no plantarte",
        "golpe de área o esquiva con i-frames (30 §4.5)", 2, 32, 10, 4, 5),

    tirador: new ArquetipoDef("tirador", obj_tirador,
        "daño constante a distancia media", "buscar cobertura o cerrar distancia",
        "cerrar distancia o interponer un muro", 3, 260, 20, 3, 3),

    muro: new ArquetipoDef("muro", obj_muro,
        "bloquea el paso y absorbe el foco del grupo", "rodearlo o repartir el daño",
        "rodearlo (§2) o daño perforante", 12, 40, 26, 8, 6),

    enjambre: new ArquetipoDef("enjambre", obj_enjambre,
        "presión numérica: ninguno es peligroso solo", "usar área, no enfocar a uno",
        "ataques de área y empuje (knockback)", 1, 24, 4, 1, 1),

    francotirador: new ArquetipoDef("francotirador", obj_francotirador,
        "amenaza a larga distancia mientras estás distraído", "romper línea de visión",
        "cobertura y prioridad de amenaza alta (§4)", 2, 420, 40, 2, 2),

    apoyo: new ArquetipoDef("apoyo", obj_apoyo,
        "cura o potencia a otros; casi no ataca", "elegir entre matarlo ya o ignorarlo",
        "foco de objetivo prioritario (§4)", 3, 220, 30, 2, 2)
};
```

> ⚠️ **Los `obj_*` de arriba son objetos de TU proyecto, no símbolos del runtime.** Como
> `objEnemyGrunt` en [04 · 03](./03%20-%20Shoot%20em%20up%20%28shmup%29.md) o `obj_guardia` en
> [31](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento,%20utility%20y%20GOAP.md),
> son marcadores de posición: los creas tú con el MCP `gamemaker-resource-tool`, no con código.

---

## 2 · Sinergias: cómo se combinan en un encuentro (y el hueco que nunca se cierra)

Un solo arquetipo repetido cien veces sigue siendo aburrido. La regla mínima que genera una
**decisión real** es combinar **un enemigo que empuja** (te obliga a moverte) **con uno que
ancla** (te castiga por moverte, o por quedarte quieto):

| Combinación | Por qué funciona | Ejemplo |
|---|---|---|
| Enjambre + Tirador | El enjambre te obliga a moverte; el tirador te castiga si paras a apuntar | Zombis + arquero a distancia |
| Muro + Francotirador | El muro te obliga a rodear, exponiéndote al disparo lejano | Escudero + torreta al fondo de la sala |
| Embestidor + Apoyo | Si no matas rápido al embestidor, el apoyo lo cura: fuerza el foco de objetivo | Perro rabioso + chamán |
| Muro + Enjambre | El muro absorbe tu ataque de área mientras el enjambre te rodea por los lados | Bruto al frente, ratas por detrás |
| Francotirador + Enjambre | El enjambre te impide quedarte quieto para eliminar al francotirador | Murciélagos + arquero en altura |

> 🔺 **Tres arquetipos sin relación no son un encuentro difícil: son ruido.** Si al quitar uno
> de los tres el combate sigue exactamente igual, ese enemigo no aportaba presión, aportaba
> vida que absorber. La prueba: pregúntate qué **decisión distinta** obliga a tomar cada
> arquetipo que añades. Si la respuesta es «ninguna», sobra.

### El hueco de escape

Tobias Karlsson (Sony Bend), describiendo la coordinación de escuadras de *Days Gone*, señala
un detalle de diseño deliberado: cuando la IA flanquea al jugador por ambos lados, **«los que
flanquean siempre dejan una abertura en la retaguardia para que el enemigo tenga la
oportunidad de retirarse, lo que permite un combate más dinámico»**. Rodear del todo no es
más difícil, es injusto — el jugador no puede leer una salida que no existe.

```gml
/// scr_encuentros
/// @desc ¿Queda al menos un arco de `_grados` libre de enemigos alrededor de (`_px`,`_py`)?
///       NO es el "Frontline" completo de Days Gone (eso exige recalcular la posición de
///       todo el escuadrón cada frame): es la regla mínima que evita rodear del todo.
function hay_hueco_de_escape(_px, _py, _obj_enemigo, _grados = 70) {
    var _n = instance_number(_obj_enemigo);
    if (_n == 0) { return true; }

    var _angulos = array_create(_n);
    var _i = 0;
    with (_obj_enemigo) {
        _angulos[_i] = point_direction(_px, _py, x, y);
        _i++;
    }
    array_sort(_angulos, true);       // ascendente, todos en [0, 360)

    for (var _j = 0; _j < _n; _j++) {
        var _actual = _angulos[_j];
        // el hueco tras el último ángulo da la vuelta completa hasta el primero
        var _sig = (_j < _n - 1) ? _angulos[_j + 1] : (_angulos[0] + 360);
        if ((_sig - _actual) >= _grados) { return true; }
    }
    return false;
}
```

Se usa como condición antes de conceder la **última** posición disponible en el gestor de
fichas del §3 — no antes de cada una, sólo de la que cerraría el círculo.

### La receta de un encuentro, como dato

```gml
/// scr_encuentros
/// @func GrupoEncuentro(_arquetipo, _cantidad)
function GrupoEncuentro(_arquetipo, _cantidad) constructor {
    arquetipo = _arquetipo;
    cantidad  = _cantidad;
}

/// @func EncuentroDef(_nombre, _grupos)
/// @desc Una "receta" de encuentro: QUÉ arquetipos combinar y cuántos de cada uno.
///       NO decide CUÁNDO aparecen — eso ya está resuelto en 04 · 03 §5.2 (WaveDef) y
///       04 · 08 §5.8 (TDWave): esta struct sólo los alimenta, no los sustituye (§6-7).
function EncuentroDef(_nombre, _grupos) constructor {
    nombre = _nombre;
    grupos = _grupos;      // array de GrupoEncuentro
}

/// La emboscada de pasillo de la tabla de arriba: "el muro obliga a rodear, el enjambre
/// te acosa mientras rodeas".
var _emboscada = new EncuentroDef("emboscada_pasillo", [
    new GrupoEncuentro(global.arquetipos.muro,     1),
    new GrupoEncuentro(global.arquetipos.enjambre, 5)
]);
```

Los dos adaptadores que convierten esta receta en algo que los sistemas de oleadas YA
existentes saben consumir están en el §6, junto al director de intensidad — no antes, porque
sin el director no hay quién decida CUÁNDO usar cada receta.

---

## 3 · El gestor de fichas de ataque: por qué no deberían pegarte seis a la vez

Exigir que los enemigos ataquen de uno en uno es una técnica tan vieja que tiene nombre propio:
el **«Kung-Fu Circle»**, llamado así por las escenas de artes marciales donde decenas de
rivales esperan su turno para atacar al protagonista. Michael Dawe lo describe así para
*Kingdoms of Amalur: Reckoning*: es fácil de programar, pero **«esta restricción puede ser
demasiado estricta para un juego de combate ágil»**. La alternativa que usó el equipo de
Amalur — apodada internamente **«Belgian AI»** — permite que ataquen varios a la vez, pero con
un límite dirigido por datos, no por una regla fija de «máximo dos».

**La idea, en una frase de Dawe**: cada personaje objetivo (normalmente el jugador) lleva una
rejilla invisible a su alrededor con dos variables — **capacidad de rejilla** (cuántos
enemigos pueden *acercarse* a la vez) y **capacidad de ataque** (cuántos pueden *golpear* a la
vez). Cada enemigo tiene un **peso de rejilla** y cada ataque un **peso de ataque**; mientras
la suma de pesos no supere la capacidad, se concede permiso. Una IA central — el **gestor de
escena** (*stage manager*) — es quien reparte los permisos; ningún enemigo decide por sí solo
si puede atacar.

```gml
/// scr_gestor_fichas
/// @func GestorFichas(_objetivo, _capacidad_rejilla, _capacidad_ataque,
///                     _radio_aproximacion, _radio_ataque, _ranuras)
/// @desc Adaptación de la "Belgian AI" de Kingdoms of Amalur: Reckoning (Michael Dawe,
///       "Beyond the Kung-Fu Circle", Game AI Pro vol. 1, cap. 28). Un gestor por objetivo
///       (normalmente uno por jugador). La rejilla viaja CON el objetivo: `objetivo.x/y` se
///       lee en cada consulta, nunca se congela.
function GestorFichas(_objetivo, _capacidad_rejilla, _capacidad_ataque,
                       _radio_aproximacion, _radio_ataque, _ranuras = 8) constructor {
    objetivo                 = _objetivo;
    capacidad_rejilla        = _capacidad_rejilla;
    capacidad_ataque         = _capacidad_ataque;
    disponible_rejilla       = _capacidad_rejilla;
    disponible_ataque        = _capacidad_ataque;
    radio_aproximacion       = _radio_aproximacion;    // "approach circle" de Dawe
    radio_ataque             = _radio_ataque;          // "attack circle" de Dawe
    num_ranuras              = _ranuras;
    ranura_ocupante          = array_create(_ranuras, noone);
    cooldown_global_listo_en = 0;
    cooldown_por_arquetipo   = {};    // especie → current_time del próximo permitido
    cooldown_por_instancia   = {};    // instancia → current_time del próximo permitido

    /// @desc Posición mundial de una ranura de la rejilla (índice 0..num_ranuras-1).
    static posicion_ranura = function(_ranura) {
        var _ang = (360 / num_ranuras) * _ranura;
        return { x: objetivo.x + lengthdir_x(radio_aproximacion, _ang),
                 y: objetivo.y + lengthdir_y(radio_aproximacion, _ang) };
    };

    /// @desc La ranura libre más cercana a un punto, o -1 si todas están ocupadas.
    static ranura_mas_cercana = function(_x, _y) {
        var _mejor = -1, _mejor_d = infinity;
        for (var _i = 0; _i < num_ranuras; _i++) {
            if (ranura_ocupante[_i] != noone && instance_exists(ranura_ocupante[_i])) { continue; }
            var _pos = posicion_ranura(_i);
            var _d   = point_distance(_x, _y, _pos.x, _pos.y);
            if (_d < _mejor_d) { _mejor_d = _d; _mejor = _i; }
        }
        return _mejor;
    };

    /// @desc Permiso para ACERCARSE (no para atacar). Devuelve el índice de ranura, o -1.
    ///       `_obj_enemigo_grupo`, si se pasa, exige el hueco de escape del §2 justo antes
    ///       de conceder la ÚLTIMA ranura disponible — nunca antes de eso, sería demasiado
    ///       conservador.
    static solicitar_acercarse = function(_atacante, _peso, _obj_enemigo_grupo = noone) {
        if (_peso > disponible_rejilla) { return -1; }

        if (_obj_enemigo_grupo != noone && (disponible_rejilla - _peso) <= 0) {
            if (!hay_hueco_de_escape(objetivo.x, objetivo.y, _obj_enemigo_grupo)) { return -1; }
        }

        var _ranura = ranura_mas_cercana(_atacante.x, _atacante.y);
        if (_ranura == -1) { return -1; }

        ranura_ocupante[_ranura] = _atacante;
        disponible_rejilla -= _peso;
        return _ranura;
    };

    /// @desc Se libera al retirarse, al morir, o justo después de atacar (ver más abajo).
    static liberar_acercarse = function(_atacante, _ranura, _peso) {
        if (_ranura >= 0 && _ranura < num_ranuras && ranura_ocupante[_ranura] == _atacante) {
            ranura_ocupante[_ranura] = noone;
        }
        disponible_rejilla = min(capacidad_rejilla, disponible_rejilla + _peso);
    };

    /// @desc Con la ranura ya concedida, pide permiso para LANZAR el ataque. Respeta TRES
    ///       enfriamientos a la vez — el propio, el de su especie y el global — tal y como
    ///       Dawe describe en §28.6.2: "cooldowns on individual, creature-wide, and global
    ///       bases to prevent creatures from launching too many of the same attacks".
    static solicitar_ataque = function(_atacante, _peso, _nombre_arquetipo,
                                        _cooldown_individual_ms, _cooldown_especie_ms) {
        if (_peso > disponible_ataque)               { return false; }
        if (current_time < cooldown_global_listo_en) { return false; }

        var _listo_especie = cooldown_por_arquetipo[$ _nombre_arquetipo];
        if (!is_undefined(_listo_especie) && current_time < _listo_especie) { return false; }

        var _clave_individual = string(_atacante);
        var _listo_individual = cooldown_por_instancia[$ _clave_individual];
        if (!is_undefined(_listo_individual) && current_time < _listo_individual) { return false; }

        disponible_ataque -= _peso;
        cooldown_por_arquetipo[$ _nombre_arquetipo]  = current_time + _cooldown_especie_ms;
        cooldown_por_instancia[$ _clave_individual]  = current_time + _cooldown_individual_ms;
        cooldown_global_listo_en                      = current_time + (_cooldown_especie_ms * 0.15);
        return true;
    };

    /// @desc Dawe es explícito: "creatures would relinquish control of their grid slot back
    ///       to the stage manager immediately after launching an attack" — se libera EN
    ///       CUANTO se lanza el golpe, no cuando termina la animación de recuperación.
    static liberar_ataque = function(_peso) {
        disponible_ataque = min(capacidad_ataque, disponible_ataque + _peso);
    };
}
```

### Uso: un enemigo completo pasando por las tres fases

Antes de que un solo `obj_embestidor` llegue a su Step necesitas el gestor **instanciado**: es
un struct por objetivo (uno por jugador), no una función global suelta.

```gml
/// obj_jugador · Create (o donde inicialices la partida — UNA vez, no por enemigo)
global.gestor_jugador = new GestorFichas(id, /*capacidad_rejilla*/ 4, /*capacidad_ataque*/ 2,
                                          /*radio_aproximacion*/ 64, /*radio_ataque*/ 48);
```

> 🔺 Sin esta línea, `global.gestor_jugador.solicitar_acercarse(...)` en el Step de abajo lanza
> "variable global name 'gestor_jugador' index (…) not set before reading it" en cuanto el
> primer `obj_embestidor` llega a su Step — confirmado en ejecución real. El mismo patrón que
> `global.feel` en [`04 · 15` §5.0](./15%20-%20Game%20feel%20y%20juice.md#50-sistema-de-tiempo-hit-stop-y-time-scale).

```gml
/// obj_embestidor · Create
arquetipo    = global.arquetipos.embestidor;
estado_ficha = "acercandose";
ranura       = -1;

/// obj_embestidor · Step
switch (estado_ficha) {
    case "acercandose":
        if (ranura == -1) {
            ranura = global.gestor_jugador.solicitar_acercarse(id, arquetipo.peso_rejilla,
                                                                 obj_embestidor);
            if (ranura == -1) { break; }      // sin sitio: espera fuera, sigue en este estado
        }

        var _pos = global.gestor_jugador.posicion_ranura(ranura);
        mp_potential_step(_pos.x, _pos.y, 2, false);      // movimiento: ver 04 · 23

        if (point_distance(x, y, obj_jugador.x, obj_jugador.y) <= arquetipo.alcance) {
            estado_ficha = "pidiendo_ataque";
        }
        break;

    case "pidiendo_ataque":
        var _ok = global.gestor_jugador.solicitar_ataque(id, arquetipo.peso_ataque,
                                                           arquetipo.nombre, 1400, 900);
        if (_ok) {
            estado_ficha = "atacando";
            alarm[0] = arquetipo.telegrafia_fr;           // el arranque, ver 30 §5.2
        }
        break;

    case "atacando":
        // Nada que hacer aquí: el golpe real se lanza en la Alarm 0.
        break;
}

/// obj_embestidor · Alarm 0 — el ataque se lanza AHORA
global.gestor_jugador.liberar_ataque(arquetipo.peso_ataque);
// crear_hitbox(...) — la hitbox real es 04 · 30 §5.3-5.4, no se repite aquí.
estado_ficha = "retirandose";

/// obj_embestidor · Destroy — nunca dejes una ranura fantasma ocupada
if (ranura != -1) {
    global.gestor_jugador.liberar_acercarse(id, ranura, arquetipo.peso_rejilla);
}
```

> 🔺 **La difícultad se ajusta con la capacidad, no con el peso de cada enemigo.** Dawe: al
> subir la dificultad en *Reckoning* «escalamos la capacidad de rejilla y de ataque en
> consecuencia», nunca el peso individual de cada criatura — así la relación entre enemigos se
> mantiene y sólo cambia cuántos entran a la vez. Es el mismo espíritu que
> [13 · 01 §3.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md):
> ajusta lo que el jugador no está midiendo directamente.

---

## 4 · A quién atacan: la tabla de amenaza, y su versión ligera de un jugador

Cuando hay **más de un objetivo posible** — cooperativo, compañeros de IA, torretas, un
invocado — algo tiene que decidir a quién ataca cada enemigo. La convención extendida de
MMO/ARPG es la **tabla de amenaza** (*aggro*/*threat table*): cada enemigo acumula un valor de
amenaza por objetivo, y ataca al que más tiene.

> ⚠️ Esto es vocabulario de oficio ampliamente extendido (WoW, buscadores de grupo de
> incontables ARPG), no una técnica con una única fuente primaria como los §3 y §5: no hay una
> cita que abrir aquí, y se marca como tal en vez de inventar una.

```gml
/// scr_amenaza
/// @func EntradaAmenaza(_objetivo, _valor)
function EntradaAmenaza(_objetivo, _valor) constructor {
    objetivo = _objetivo;
    valor    = _valor;
}

/// @func TablaAmenaza()
/// @desc Una tabla por enemigo (o una compartida por grupo, si prefieres que ataquen todos
///       al mismo objetivo). Acumula, decae, y admite provocar (taunt).
function TablaAmenaza() constructor {
    entradas      = [];       // array de EntradaAmenaza
    forzado       = noone;
    forzado_hasta = 0;

    static sumar = function(_objetivo, _cantidad) {
        for (var _i = 0; _i < array_length(entradas); _i++) {
            if (entradas[_i].objetivo == _objetivo) {
                entradas[_i].valor += _cantidad;
                return;
            }
        }
        array_push(entradas, new EntradaAmenaza(_objetivo, _cantidad));
    };

    /// @desc Curar también genera amenaza: quien te mantiene vivo es tan peligroso como
    ///       quien pega. `_multiplicador` suele ser menor que el de daño directo.
    static sumar_por_curacion = function(_objetivo, _cantidad_curada, _multiplicador = 0.5) {
        sumar(_objetivo, _cantidad_curada * _multiplicador);
    };

    /// @desc Llamar una vez por Step (o cada pocos frames). Sin decaimiento, el primer
    ///       golpe fija el objetivo para siempre aunque deje de hacer nada.
    static decaer = function(_tasa_por_segundo) {
        var _dt = delta_time / 1000000;
        for (var _i = array_length(entradas) - 1; _i >= 0; _i--) {
            entradas[_i].valor -= _tasa_por_segundo * _dt;
            if (entradas[_i].valor <= 0 || !instance_exists(entradas[_i].objetivo)) {
                array_delete(entradas, _i, 1);
            }
        }
    };

    static objetivo_prioritario = function() {
        var _mejor = noone, _mejor_valor = -1;
        for (var _i = 0; _i < array_length(entradas); _i++) {
            if (instance_exists(entradas[_i].objetivo) && entradas[_i].valor > _mejor_valor) {
                _mejor_valor = entradas[_i].valor;
                _mejor       = entradas[_i].objetivo;
            }
        }
        return _mejor;
    };

    /// @desc Taunt: fuerza el objetivo durante `_duracion_ms`, por encima de la tabla real.
    static provocar = function(_objetivo, _duracion_ms) {
        forzado       = _objetivo;
        forzado_hasta = current_time + _duracion_ms;
    };

    /// @desc El que de verdad debe atacar el enemigo AHORA MISMO.
    static objetivo_actual = function() {
        if (forzado != noone && current_time < forzado_hasta && instance_exists(forzado)) {
            return forzado;
        }
        return objetivo_prioritario();
    };
}
```

### La versión ligera: un solo jugador, sin tabla

Si sólo hay un objetivo humano de verdad y como mucho un par de invocados, una tabla de
amenaza completa es sobre-ingeniería. Tobias Karlsson (Sony Bend) describe, para *Days Gone*,
un sistema mucho más simple que decide **la actitud del grupo**, no a quién ataca cada uno: la
**Confianza** (*Confidence*). Es, en su definición, **«cuán confiada está una IA de que su
bando va a ganar el enfrentamiento actual»**, calculada a partir de la fuerza relativa de
aliados y enemigos, con cinco niveles: pánico, preocupado, neutral, confiado y heroico.

```gml
/// scr_confianza_grupo — adaptado de Tobias Karlsson, "Squad Coordination in Days Gone"
/// (Game AI Pro, Online Edition 2021, cap. 12). Aquí NO se implementa el "Frontline"
/// completo de Days Gone —exige recalcular la posición de todo el escuadrón cada frame—:
/// sólo la parte que decide la ACTITUD del grupo, que es la que hace falta en un juego de
/// un jugador sin varios objetivos que repartir.
enum ConfianzaNivel { PANICO, PREOCUPADO, NEUTRAL, CONFIADO, HEROICO }

function ConfianzaGrupo() constructor {
    valor = 1.0;     // fuerza_aliada / fuerza_enemiga · 1.0 = empate

    /// @desc `_fuerza_aliada` y `_fuerza_enemiga` ya deben incluir armadura, arma y heridas
    ///       si tu juego los modela (Karlsson §3.1); si no, basta con la vida sumada.
    static actualizar = function(_fuerza_aliada, _fuerza_enemiga) {
        valor = _fuerza_aliada / max(_fuerza_enemiga, 0.0001);
    };

    static nivel = function() {
        if (valor < 0.4) { return ConfianzaNivel.PANICO; }
        if (valor < 0.8) { return ConfianzaNivel.PREOCUPADO; }
        if (valor < 1.3) { return ConfianzaNivel.NEUTRAL; }
        if (valor < 2.0) { return ConfianzaNivel.CONFIADO; }
        return ConfianzaNivel.HEROICO;
    };

    /// @desc La actitud táctica que dispara cada nivel (Karlsson §6): retirarse, sostener
    ///       posiciones, o presionar y flanquear — respetando siempre el hueco de escape (§2).
    static actitud = function() {
        switch (nivel()) {
            case ConfianzaNivel.PANICO:
            case ConfianzaNivel.PREOCUPADO: return "retirarse";
            case ConfianzaNivel.CONFIADO:
            case ConfianzaNivel.HEROICO:    return "presionar";
            default:                        return "sostener";
        }
    };
}
```

> 💡 **Son ortogonales, no alternativas.** `TablaAmenaza` responde **a quién** atacar cuando
> hay varios objetivos de verdad. `ConfianzaGrupo` responde **cuánto empuja** el grupo mientras
> decide eso. Un juego con un compañero de IA usa las dos: la tabla elige el objetivo, la
> confianza decide si el grupo presiona o se repliega.

---

## 5 · El director de intensidad: acumular, sostener el pico, apagarlo, calmar

Michael Booth (Valve), en la charla de GDC 2009 sobre la IA de *Left 4 Dead*, parte de una
observación sobre *Counter-Strike*: **«el ritmo natural de CS es "de picos", con periodos de
tensión tranquila puntuados por momentos impredecibles de combate intenso»**, y de dos hechos
incómodos: **«el combate constante y sin cambios es agotador»** y **«los periodos largos de
inactividad son aburridos»**. La solución de *Left 4 Dead* es el **AI Director**, y su pieza de
ritmo se llama **Adaptive Dramatic Pacing**.

**El algoritmo, en las palabras de Booth:**

1. Estimar la **«intensidad emocional»** de cada superviviente.
2. Rastrear la intensidad máxima de todo el grupo.
3. Si la intensidad es demasiado alta, retirar las amenazas importantes un tiempo.
4. Si no, crear una población interesante de amenazas.

La intensidad **sube** al recibir daño (proporcional al daño), al quedar incapacitado, al ser
empujado/arrastrado por un infectado, y **al morir un enemigo cerca — inversamente
proporcional a la distancia**. **Decae hacia cero con el tiempo**, salvo que haya un infectado
enganchado activamente al jugador: mientras dura el combate, la intensidad no baja sola.

Con ese valor, el director recorre **cuatro estados**:

| Estado | Población de amenazas | Condición de salida |
|---|---|---|
| **Acumular** (*Build Up*) | Completa: errantes, hordas, infectados especiales | La intensidad cruza el umbral de pico |
| **Sostener pico** (*Sustain Peak*) | Completa | 3-5 s desde que se cruzó el umbral — duración mínima, para que el combate actual no se corte a medias |
| **Apagar pico** (*Peak Fade*) | Mínima | La intensidad baja del umbral **y** hay un respiro natural en la acción (no se deja pasar a Calma en mitad de un combate) |
| **Calma** (*Relax*) | Mínima: nada de errantes, hordas ni especiales | 30-45 s, o hasta recorrer distancia suficiente — entonces vuelve a Acumular |

Dos reglas explícitas de Booth que importan más que el propio algoritmo:

- **«Los encuentros con jefe NO se ven afectados por el ritmo adaptativo»** — cambian el ritmo
  por sí mismos, y quitarlos rompería demasiado la estructura del nivel.
- **«El algoritmo ajusta el ritmo, no la dificultad. La amplitud (dificultad) no cambia, la
  frecuencia (ritmo) sí.»** Esto es exactamente la misma frontera que ya traza
  [13 · 01 §3.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md):
  lo que **no** se ajusta en silencio es la vida y el daño del enemigo — lo que sí, es cuántos
  aparecen y cuándo.

```gml
/// scr_director_combate — traducción de la Adaptive Dramatic Pacing de Michael Booth
/// (Valve), "The AI Systems of Left 4 Dead", GDC 2009.
enum DirectorEstado { CALMA, ACUMULAR, SOSTENER_PICO, APAGAR_PICO }

/// @func DirectorCombate(_umbral_pico, _pico_minimo_seg, _calma_seg)
function DirectorCombate(_umbral_pico = 100, _pico_minimo_seg = 4, _calma_seg = 35) constructor {
    intensidad      = 0;
    umbral_pico     = _umbral_pico;
    pico_minimo_seg = _pico_minimo_seg;    // "Sustain Peak": 3-5 s en la charla original
    calma_seg       = _calma_seg;          // "Relax": 30-45 s en la charla original
    estado          = DirectorEstado.ACUMULAR;
    reloj           = 0;                   // segundos transcurridos en el estado actual
    hubo_respiro    = false;               // "Peak Fade" exige un respiro real antes de Calma

    // --- Los cuatro eventos que suman intensidad, según Booth §"Estimating emotional intensity"
    static sumar_dano          = function(_dano) { intensidad += _dano * 0.6; };
    static sumar_incapacitado  = function()      { intensidad += 40; };
    static sumar_empuje        = function()      { intensidad += 8; };
    static sumar_muerte_cercana = function(_dist, _radio = 300) {
        intensidad += 12 * clamp(1 - (_dist / _radio), 0, 1);
    };

    /// @desc Un tick por Step. `_hay_enemigo_enganchado`: si hay un enemigo activamente
    ///       atacando o persiguiendo de cerca — mientras sea así, la intensidad NO decae.
    static step = function(_hay_enemigo_enganchado) {
        var _dt = delta_time / 1000000;
        reloj += _dt;

        if (!_hay_enemigo_enganchado) {
            intensidad = max(0, intensidad - 6 * _dt);
        }

        switch (estado) {
            case DirectorEstado.ACUMULAR:
                if (intensidad >= umbral_pico) { estado = DirectorEstado.SOSTENER_PICO; reloj = 0; }
                break;

            case DirectorEstado.SOSTENER_PICO:
                if (reloj >= pico_minimo_seg) {
                    estado = DirectorEstado.APAGAR_PICO;
                    hubo_respiro = false;
                }
                break;

            case DirectorEstado.APAGAR_PICO:
                if (!_hay_enemigo_enganchado) { hubo_respiro = true; }
                if (hubo_respiro && intensidad < umbral_pico * 0.5) {
                    estado = DirectorEstado.CALMA;
                    reloj  = 0;
                }
                break;

            case DirectorEstado.CALMA:
                if (reloj >= calma_seg) { estado = DirectorEstado.ACUMULAR; reloj = 0; }
                break;
        }
    };

    /// @desc Población completa (Acumular/Sostener/Apagar) o mínima (Calma). Los jefes NO
    ///       consultan esto: quedan fuera del ritmo adaptativo a propósito (Booth).
    static poblacion_completa = function() {
        return (estado != DirectorEstado.CALMA);
    };
}
```

```gml
/// obj_control · Create — un director por partida (o uno por jugador, si es cooperativo)
director = new DirectorCombate();

/// obj_control · Step — "enganchado" = hay un enemigo vivo cerca, atacando o persiguiendo
var _mas_cercano  = instance_nearest(obj_jugador.x, obj_jugador.y, objEnemyBase);
var _enganchado   = instance_exists(_mas_cercano)
                  && point_distance(obj_jugador.x, obj_jugador.y, _mas_cercano.x, _mas_cercano.y) < 200;
director.step(_enganchado);

/// obj_jugador · al recibir daño (o vía la señal "jugador_danado" de 04 · 16, si ya la usas)
director.sumar_dano(_dano);

/// obj_enemigo · al morir
director.sumar_muerte_cercana(point_distance(x, y, obj_jugador.x, obj_jugador.y));
```

---

## 6 · Acoplar el director a las oleadas que ya existen

El director del §5 no sustituye a los sistemas de oleadas de la biblioteca: **decide cuándo
usarlos y con cuánta población**, sin tocar sus datos de dificultad. Los dos adaptadores del
§2 son el puente entre `EncuentroDef` y lo que `objWaveDirector` (04 · 03) y `objWaveManager`
(04 · 08) ya saben ejecutar.

```gml
/// scr_encuentros
/// @desc Traduce un EncuentroDef a las SpawnEntry de 04 · 03 §5.2 (shmup: por fotograma).
///       No repite WaveDef/SpawnEntry: los alimenta.
function encuentro_a_spawn_entries(_encuentro, _frame_inicio, _formation, _x, _y, _espaciado) {
    var _entries = [];
    var _frame   = _frame_inicio;
    for (var _i = 0; _i < array_length(_encuentro.grupos); _i++) {
        var _g = _encuentro.grupos[_i];
        array_push(_entries, new SpawnEntry(_frame, _g.arquetipo.obj, _x, _y,
                                             _formation, _g.cantidad, _espaciado));
        _frame += 40;      // separa cada grupo del encuentro para que no aparezcan encimados
    }
    return _entries;
}

/// @desc Traduce un EncuentroDef a los TDGroup de 04 · 08 §5.8 (Tower Defense: por intervalo).
function encuentro_a_td_grupos(_encuentro, _retardo, _intervalo) {
    var _grupos = [];
    for (var _i = 0; _i < array_length(_encuentro.grupos); _i++) {
        var _g = _encuentro.grupos[_i];
        array_push(_grupos, new TDGroup(_g.arquetipo.nombre, _g.cantidad, _retardo, _intervalo));
        _retardo += 20;
    }
    return _grupos;
}
```

```gml
// Un encuentro concreto, listo para los dos géneros a la vez.
var _emboscada = new EncuentroDef("emboscada_pasillo", [
    new GrupoEncuentro(global.arquetipos.muro,     1),
    new GrupoEncuentro(global.arquetipos.enjambre, 5)
]);

// Para un shmup (04 · 03): SpawnEntry listas para meter en un WaveDef.
var _entries = encuentro_a_spawn_entries(_emboscada, 60, global.Formation.line_h, 160, -40, 28);
var _oleada  = new WaveDef(_entries);

// Para un Tower Defense (04 · 08): TDGroup listos para un TDWave.
var _grupos_td = encuentro_a_td_grupos(_emboscada, 30, 40);
var _oleada_td = new TDWave(_grupos_td, 60);   // 60 de recompensa al completarla
```

### El acoplamiento con el director: sólo población y ritmo, nunca dificultad

```gml
// objWaveDirector (04 · 03) · Step, dentro de case "running" — SIN tocar WaveDef/SpawnEntry.
wave.update();

// Si la oleada de guion ya se agotó, el jefe aún no ha llegado, y el director está en
// ACUMULAR, refuerza con un grupo de relleno en vez de dejar un vacío. Nunca se toca vida
// ni daño: sólo cuántos entran.
if (wave.finished && director.estado == DirectorEstado.ACUMULAR
    && instance_number(objEnemyBase) < 4) {
    spawn_formation(new SpawnEntry(0, obj_enjambre, x, y - 40, global.Formation.line_h, 3, 28));
}
```

```gml
// scr_waves_td (04 · 08), dentro de TDWave.update(), justo antes del "if (_toca)" original.
// Añade un campo opcional `es_relleno` (por defecto false) a los TDGroup que quieras que el
// director pueda pausar — los de refuerzo, NUNCA los que definen el reto real de la oleada.
if (_toca && _g.es_relleno && !director.poblacion_completa()) {
    continue;      // se pospone, no se descarta: el timer no se reinicia, sólo se retrasa
}
```

> ⚠️ **Los jefes quedan fuera de las dos comprobaciones de arriba, a propósito** (Booth,
> §5): ni `objBoss` de 04 · 03 ni un `TDGroup` de tipo jefe deberían consultar nunca
> `director.estado`. Si el jefe desaparece o se ralentiza a media pelea porque el director
> entró en Calma, el jugador lo va a notar y se va a sentir engañado.

---

## 7 · Qué patrón de oleada usar cuándo, y el pacing bajado del nivel al encuentro

La biblioteca ya tiene **dos** sistemas de oleadas dirigidos por datos, y no hace falta un
tercero — sólo saber cuál usar:

| | `WaveDef` / `SpawnEntry` (04 · 03 §5.2) | `TDWave` / `TDGroup` (04 · 08 §5.8) |
|---|---|---|
| Granularidad | Fotograma absoluto dentro de la oleada | Retardo + intervalo relativo |
| Pensado para | Coreografía leída de un guion (shmup, jefe) | Goteo continuo de un mismo tipo (TD, horda) |
| Formación | Sí — línea, arco, uve (`_formation`) | No: aparecen en el punto de *spawn* del mapa |
| Recompensa al completar | No la define el propio sistema | `TDWave.recompensa`, en oro |
| Lo gobierna | `objWaveDirector` (04 · 03 §5.3) | `objWaveManager` (04 · 08 §5.8) |
| Se alimenta de `EncuentroDef` (§2) vía | `encuentro_a_spawn_entries()` | `encuentro_a_td_grupos()` |

**La recomendación**: usa `WaveDef` cuando el ritmo lo dicta el diseñador fotograma a
fotograma — bullet hell, la antesala de un jefe. Usa `TDGroup` cuando el ritmo lo dicta un
parámetro — una horda continua, un TD, un *survival*. Ambos se acoplan al **mismo**
`DirectorCombate` del §5-6: es un solo director con dos consumidores distintos, no dos
directores que puedan desincronizarse.

### El pacing, bajado de escala

[`13 · 02 — Diseño de niveles`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/02%20-%20Diseño%20de%20niveles.md)
§1.2 dibuja el **gráfico de intensidad** a escala de *nivel* — varios encuentros, minutos u
horas. El `intensidad` de `DirectorCombate` (§5) **es ese mismo gráfico, pero a escala de
encuentro** — segundos, no minutos. No hace falta un segundo sistema de medición: hace falta
exponer la variable que ya existe con el mismo mecanismo de depuración de
[31 · 6](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento,%20utility%20y%20GOAP.md):

```gml
/// obj_control · Create — depurar el director en vivo (mismo patrón que 04 · 31 §6)
if (global.depurar_ia) {
    dbg_view("Director de combate", true);
    dbg_watch(ref_create(director, "intensidad"), "Intensidad");
    dbg_watch(ref_create(director, "estado"),     "Estado");
}
```

> 💡 Un pico del director que dura de más, o una calma que nunca se dispara, se ve en este
> panel al instante — no hace falta jugar diez minutos a ciegas para notarlo.

---

## Checklist

- [ ] ¿Cada arquetipo responde a las cuatro preguntas del §1 (presión / obliga a / se
      contrarresta / qué pasa si se ignora), no sólo a un número de vida?
- [ ] ¿Todo encuentro combina al menos un arquetipo que empuja y uno que ancla (§2)?
- [ ] ¿Ningún encuentro puede rodear al jugador sin dejar el hueco de escape (§2)?
- [ ] ¿El gestor de fichas limita cuántos **atacan** a la vez, no sólo cuántos hay en pantalla
      (§3)?
- [ ] ¿Los enfriamientos existen a los tres niveles de Dawe — individual, especie, global —
      y no sólo en la instancia (§3)?
- [ ] ¿La tabla de amenaza decae y admite provocar (*taunt*), no sólo acumula (§4)?
- [ ] ¿Se usó `ConfianzaGrupo`, no una tabla de amenaza completa, si no hay varios objetivos
      de verdad (§4)?
- [ ] ¿El director de intensidad ajusta **población y ritmo**, nunca vida ni daño del
      enemigo (§5, y [13 · 01 §3.3](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md))?
- [ ] ¿Los encuentros de jefe quedan explícitamente fuera del director (§5, §6)?
- [ ] ¿El director se acopla a `WaveDef`/`TDGroup` ya existentes, sin reescribirlos (§6)?

---

## Las trampas

| Trampa | Qué se ve en el juego | Arreglo |
|---|---|---|
| Todos los enemigos atacan a la vez | El jugador recibe daño de seis sitios en un solo fotograma; se siente injusto | Gestor de fichas (§3): capacidad de **ataque**, no sólo de rejilla |
| El enfriamiento vive dentro de cada instancia | Cinco enemigos del mismo tipo atacan cada uno cada 900 ms — pero los cinco a la vez | Enfriamiento **por especie** en el gestor, no sólo en la instancia (§3) |
| La rejilla nunca se libera | A los 30 s ya no quedan ranuras libres aunque los ocupantes originales murieron | `liberar_acercarse()` en el Destroy, siempre (§3) |
| Rodear del todo al jugador | Se siente una emboscada sin salida, no un reto | `hay_hueco_de_escape()` antes de conceder la última ranura (§2, §3) |
| Tres arquetipos sin relación entre sí | El encuentro se siente largo, no difícil | Combina uno que empuja + uno que ancla (§2); si quitar uno no cambia nada, sobra |
| El director sube la vida o el daño del enemigo | El jugador nota el ajuste: «mi victoria no es mía» | El director sólo cambia **población y ritmo** (§5), nunca vida ni daño |
| El director también afecta al jefe | El jefe se comporta de forma errática o desaparece a medio combate | Excluir explícitamente los encuentros de jefe (§5, §6) |
| La tabla de amenaza nunca decae | El primer golpe fija el objetivo para siempre, aunque deje de hacer nada | `decaer()` cada Step, con una tasa por segundo (§4) |
| Calcular una tabla de amenaza completa para un solo jugador | Complejidad sin beneficio: sólo hay un objetivo real | Usa `ConfianzaGrupo` (§4) si no hay compañeros/invocados de verdad |
| Reinventar un tercer formato de oleada | Un sistema incompatible con `WaveDef` y `TDGroup` que nadie más reutiliza | `EncuentroDef` + los dos adaptadores del §6, nunca una tercera estructura |

---

## Ver también

- [23 · IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) — el **movimiento** de cada enemigo: *seek*, *flee*, patrulla, *flocking*. Este documento decide el grupo; aquel resuelve cómo se desplaza cada uno
- [31 · IA de decisión](./31%20-%20IA%20de%20decisión%20-%20árboles%20de%20comportamiento,%20utility%20y%20GOAP.md) — qué hace **un** enemigo: árbol de comportamiento, utility, GOAP, percepción y la señal `alerta_grupo` que este documento no repite
- [32 · Sistema de daño y efectos de estado](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md) — cuánto duele cada golpe, resistencias, escudos y efectos de estado (documento hermano, en paralelo a este)
- [30 · Combate cuerpo a cuerpo — hitboxes, hurtboxes y combos](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes%2C%20hurtboxes%20y%20combos.md) — la hitbox real del ataque y su telegrafía, que el §3 sólo referencia
- [16 · Señales y desacoplamiento](./16%20-%20Señales%20y%20desacoplamiento.md) — el bus de eventos (`senal_emitir`/`senal_escuchar`) que puede disparar `director.sumar_dano()` sin acoplar al jugador con el director
- [03 · Shoot 'em up (shmup)](./03%20-%20Shoot%20em%20up%20%28shmup%29.md) — `WaveDef`, `SpawnEntry` y `objWaveDirector`, que el §6 acopla sin reescribir
- [08 · Tower Defense](./08%20-%20Tower%20Defense.md) — `TDWave`, `TDGroup` y `objWaveManager`, igual de intactos tras el acoplamiento del §6
- [`13 · 01 — Diseño de juego`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md) §4.4 — el TTK y los «golpes estándar» que el §1 reutiliza sin repetir la fórmula; §3.3 — qué NO se ajusta en silencio, la regla que gobierna todo el §5
- [`13 · 02 — Diseño de niveles`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/02%20-%20Diseño%20de%20niveles.md) §1.2 — el gráfico de intensidad a escala de nivel, del que el §7 es la versión a escala de encuentro

---

## Fuentes

Consultadas el **2026-09-06**.

**Abiertas y verificadas** (leídas en PDF completo o en el artículo, con las citas literales
que aparecen en el texto):

- Michael Booth (Valve), **«The AI Systems of Left 4 Dead»**, *Game Developers Conference*
  2009 —
  <https://media.steampowered.com/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf>
  (PDF oficial de Valve, leído entero). De aquí sale el §5 completo: la observación sobre el
  ritmo «de picos» de *Counter-Strike*, el algoritmo de *Adaptive Dramatic Pacing*, los cuatro
  eventos que suman «Survivor Intensity» y su decaimiento condicionado, los cuatro estados
  (*Build Up* → *Sustain Peak* → *Peak Fade* → *Relax*) con sus duraciones (3-5 s / 30-45 s), la
  exclusión explícita de los jefes, y la frase «el algoritmo ajusta el ritmo, no la
  dificultad».
- Michael Dawe, **«Beyond the Kung-Fu Circle: A Flexible System for Managing NPC Attacks»**,
  *Game AI Pro* vol. 1, cap. 28, CRC Press, 2013 —
  <http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter28_Beyond_the_Kung-Fu_Circle_A_Flexible_System_for_Managing_NPC_Attacks.pdf>
  (PDF gratuito, leído entero). De aquí sale el §3 completo: el problema del «Kung-Fu Circle»,
  el sistema «Belgian AI» de *Kingdoms of Amalur: Reckoning*, la rejilla con capacidad y peso,
  el gestor de escena (*stage manager*), los círculos de aproximación y de ataque, la
  liberación inmediata del permiso tras atacar, los tres niveles de enfriamiento (individual,
  especie, global), y el escalado de dificultad por capacidad en vez de por peso.
- Tobias Karlsson (Sony Bend), **«Squad Coordination in Days Gone»**, *Game AI Pro*, Online
  Edition 2021, cap. 12 —
  <http://www.gameaipro.com/GameAIProOnlineEdition2021/GameAIProOnlineEdition2021_Chapter12_Squad_Coordination_in_Days_Gone.pdf>
  (PDF gratuito, leído: introducción, el sistema de Confianza completo con su fórmula, y el
  uso táctico del *Frontline* en las cuatro fases — formar, combate normal, retirada,
  presionar y flanquear). De aquí sale la cita literal sobre dejar una abertura en la
  retaguardia (§2) y el sistema `ConfianzaGrupo` (§4).
- David Craddock, **«Stairway to Badass: The Making and Remaking of Doom: Keywords»**,
  *Shacknews*, 2016 —
  <https://www.shacknews.com/article/99662/stairway-to-badass-the-making-and-remaking-of-doom?page=3>.
  De aquí salen las citas de Marty Stratton («be aggressive, be fast…», el tablero de
  ajedrez), Hugo Martin (el contraste con *Doom 3*) y Kurt Loudy (los «cinturones blancos») que
  abren el §1.
- **Índice de capítulos gratuitos de *Game AI Pro*** — <http://www.gameaipro.com/> — usado
  para localizar los dos capítulos de arriba por título exacto y autor.
- **Wikipedia, «Doom (2016 video game)»** —
  <https://en.wikipedia.org/wiki/Doom_(2016_video_game)> — usada como puente para confirmar el
  término «push-forward combat» y su referencia cruzada al artículo de Shacknews; no se cita
  como fuente última, sólo como confirmación de que la cita de Craddock está bien atribuida.
- **Manual oficial de GameMaker LTS 2026**, espejo local en `09 - Manual oficial/`:
  [`delta_time`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Date_And_Time/delta_time.md)
  (la conversión `delta_time / 1000000` a segundos usada en `TablaAmenaza.decaer()` y
  `DirectorCombate.step()` es literalmente el ejemplo de esa página del manual),
  [`array_sort`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Variable_Functions/array_sort.md),
  [`dbg_watch`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Debugging/dbg_watch.md).

**Lo que no se pudo verificar:**

- ⚠️ No existe una única fuente primaria abierta para la «tabla de amenaza» de MMO/ARPG del
  §4(a): es vocabulario de oficio extendido (WoW y similares), sin un artículo o charla técnica
  concreta que citar. Se ha marcado explícitamente en el texto en vez de inventar una cita.
- ⚠️ No se intentó abrir GDC Vault: como ya advirtió la auditoría que originó este documento,
  su buscador es JavaScript y no responde a `curl`; ninguna cita de este documento depende de
  GDC Vault — las tres charlas/capítulos usados están en PDF descargable directo (Valve y
  gameaipro.com) o en un artículo web (Shacknews).
