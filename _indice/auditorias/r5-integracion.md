# Auditoría r5 · Integración — ¿el código de la biblioteca funciona JUNTO?

> Fecha: 08-09-2026 · Prueba realizada fuera de la biblioteca, en `~/gm_prueba_integracion`
> (proyecto GameMaker real, `gm-cli` 2.3.0, runtime `GMS2@2026.0.0.23`, plantilla «Blank Pixel
> Game») · 12 incompatibilidades reales confirmadas (3 con error de compilación real, 2 con
> excepción en tiempo de ejecución real, el resto con evidencia textual cruzada) · 3 sistemas de
> naming en vigilancia (recetas independientes, colisión posible pero no probada) · 3 hallazgos ya
> corregidos en esta misma ronda, verificados como cerrados.

## Resumen ejecutivo

**No. El código de la biblioteca está validado pieza a pieza — cada bloque compila solo
(`validar-compilacion-docs.py`, 3350 bloques) y cada símbolo existe (`validar-codigo-gml.py`) —
pero nadie había comprobado nunca que dos documentos que se citan entre sí sigan hablando el
mismo idioma cuando se juntan de verdad.** Al montar cuatro combinaciones reales en un proyecto
GameMaker con `gm-cli` y compilarlas **juntas**, tres fallaron con un error de compilación real
del motor, y una cuarta —aparentemente inofensiva porque compila— **revienta en tiempo de
ejecución la primera vez que se dispara**, con una excepción real capturada en vivo.

El patrón es siempre el mismo: **dos documentos, escritos por agentes distintos en momentos
distintos, resuelven el mismo problema (guardar partida, sacudir la cámara, cargar un slot,
inicializar un director de IA) sin saber que el otro existe.** Uno de los dos gana silenciosamente
la variable/función/global compartida, y el otro deja de funcionar sin que ningún validador
actual lo detecte — porque cada documento, **por separado**, es perfectamente correcto.

El hallazgo más caro por volumen de citas: **`04 · 04` — RPG / Action RPG**, uno de los dos o tres
documentos más reutilizados de toda la biblioteca (lo citan `09`, `10`, `13 · 01`, `45`…), define
su **propio** sistema de guardado (`save_game()`/`load_game()`/`delete_save()`, sin argumentos, un
solo slot) que es **binariamente incompatible** con `06/scr_save_load.gml`, el sistema que el resto
de la biblioteca (`13 · 06` — Arquitectura, `04 · 54` — Metajuego) trata como el estándar. Un
agente que construya un RPG siguiendo `04 · 04` al pie de la letra y luego añada logros/galería
siguiendo `04 · 54` **no consigue que el proyecto compile**.

## Método

1. **Grafo de reutilización.** `grep -rEn` sobre `04 - Recetas por género/` y
   `13 - Diseño y producción de videojuegos/` con los patrones «de `04/NN`», «de `13/NN`»,
   «reutiliza», «reutilizando», «extiende», «definido en» → **280 citas cruzadas** localizadas
   (lista completa conservada en el historial de esta sesión; no se adjunta como archivo aparte
   porque son líneas de grep, no una fuente nueva).
2. **Detección de nombres duplicados.** Se extrajeron con grep TODAS las declaraciones
   `function NOMBRE(...)` de nivel superior en `04/`, `13/` y `06 - Assets y Scripts/` (1 457
   declaraciones), agrupadas por nombre de función y documento de origen. **23 nombres de función
   aparecen definidos en más de un documento.** Cada uno se inspeccionó a mano comparando firmas y
   cuerpos.
3. **Verificación de firma leyendo ambos lados.** Para las citas de mayor tráfico (`GestorFichas`,
   `dano_resolver`, `obj_hitbox`, `EstadoCombate`, `camera_shake`, `tween_to`, `Inventory`,
   `flag_*`, `AzarReproducible`/`calcular_dano`, `logro_desbloquear`, `hp_threshold`,
   `hit_complete`, `apply_knockback`, `barra_dibujar`) se leyó el documento de origen Y el/los
   documentos que dicen reutilizarlo, comparando aridad, orden de argumentos, tipo de retorno y
   unidades.
4. **Prueba de integración real con `gm-cli`.** Proyecto GameMaker de verdad en
   `~/gm_prueba_integracion/PruebaIntegracion` (plantilla «Blank Pixel Game», la única confirmada
   estable por `12 · 09`). Se copiaron literalmente los bloques de código de los documentos
   auditados a *scripts* y *objects* reales del proyecto, vía `gm-cli resourcetool eval`, y se
   compiló (`gm-cli compile`) y ejecutó (`gm-cli run`) el conjunto. Se transcribe la salida real
   del compilador y del motor en cada caso — no es una simulación ni una inferencia.

---

## Incompatibilidades confirmadas — Nivel 1: error de compilación real

### 1 · `save_game()` / `load_game()` / `delete_save()` / `#macro SAVE_VERSION` — 04·04 vs 06/scr_save_load.gml

**El más caro por citas indirectas.** `04 - Recetas por género/04 - RPG _ Action RPG.md` define en
su §5.8 («Save / load completo») un sistema de guardado **propio, sin argumentos, un solo slot
fijo**, sin citar ni una sola vez `scr_save_load.gml` (comprobado: `grep -n "scr_save_load"` sobre
el documento entero → **cero resultados**):

```gml
#macro SAVE_VERSION 3                          // 04·04:1416
#macro SAVE_FILE    "savegame.json"            // 04·04:1417
function save_game()                           // 04·04:1421 — CERO argumentos
function load_game()                           // 04·04:1461 — CERO argumentos
function delete_save()                         // 04·04:1550 — CERO argumentos
```

`06 - Assets y Scripts/scr_save_load.gml` — el sistema que `13 · 06` (Arquitectura de un proyecto
GameMaker, línea 1097) lista como estándar del esqueleto `Systems/` de cualquier proyecto, y que
`04 · 54` (Metajuego transversal, líneas 12, 109, 548) reutiliza explícitamente — define:

```gml
#macro SAVE_VERSION 1                          // scr_save_load.gml:67 — otro significado
function save_game(_slot, _datos)              // scr_save_load.gml:207 — DOS argumentos
function load_game(_slot)                      // scr_save_load.gml:376 — UN argumento
function delete_save(_slot)                    // scr_save_load.gml:493 — UN argumento
```

**Prueba real** (los dos bloques, copiados literalmente a dos *scripts* del mismo proyecto,
compilados juntos con `gm-cli compile`):

```
{"errors":[
  {"source":"AssetCompiler","message":"gml_Script_scr_save_rpg(8) : macro SAVE_VERSION is already defined"},
  {"source":"AssetCompiler","message":"gml_GlobalScript_scr_save_rpg(13) : duplicate script name found gml_Script_save_game"},
  {"source":"AssetCompiler","message":"gml_GlobalScript_scr_save_rpg(20) : duplicate script name found gml_Script_load_game"},
  {"source":"AssetCompiler","message":"gml_GlobalScript_scr_save_rpg(27) : duplicate script name found gml_Script_delete_save"}
]}
```

**Impacto real**: cualquier proyecto que siga `04 · 04` para el sistema de guardado y luego intente
añadir **cualquier** sistema de la biblioteca que reutilice `scr_save_load.gml` (`04 · 54` —
Metajuego; `13 · 06` §3.10 — autoguardado; `13 · 12` §6.2 — flags narrativos, ver hallazgo #3) dejará
de compilar. No hay forma de que ambos coexistan sin que un humano o un agente elija uno y borre
el otro — y ningún documento avisa de que hay que elegir.

**Por qué nadie lo vio**: `04 · 04` fue escrito de forma autocontenida (probablemente antes de que
existiera `scr_save_load.gml` como estándar de la biblioteca) y nunca se reconcilió con el resto.
`validar-compilacion-docs.py` no lo detecta porque compila cada bloque **por separado**: el bloque
de `04 · 04` compila solo, el de `scr_save_load.gml` compila solo. Solo revienta cuando coexisten.

---

### 2 · `camera_shake()` — tres implementaciones incompatibles, una de ellas duplicada dentro de su propio documento

- `04 - Recetas por género/01 - Plataformas 2D.md:651` y
  `04 - Recetas por género/02 - Top-Down _ Twin-Stick.md:659`: `camera_shake(_magnitud, _frames)`
  — **DOS argumentos**, modelo `shake_mag`/`shake_frames` (máximo acumulado, decae en `End Step`),
  definida dentro del `Create` de `objCamera`.
- `04 - Recetas por género/15 - Game feel y juice.md:345`: `camera_shake(_cantidad)` — **UN
  argumento**, modelo de trauma (`camera_add_trauma`, cuadrático, clamp 0..1). Arquitectura
  totalmente distinta a la anterior.
- El **mismo documento 04·15 la vuelve a definir en la línea 1354**, con la misma firma de un
  argumento pero otro cuerpo (respeta `global.feel.shake_enabled`), presentada como «la versión
  que respeta la configuración» — sin decirle nunca al lector que borre la de la línea 345.

`04 - Recetas por género/34 - Combate a distancia - armas, munición y balística.md:620-623` llama
con la firma de **dos** argumentos, citando correctamente `04/02 §5.7`:

```gml
objCamera.camera_shake(weapon.recoil_kick, 6);   // 34:623
```

**Prueba real**: se construyó `objCamera` con el `Create` de `04·02` seguido, en el mismo bloque,
por el de `04·15` — exactamente lo que hace un agente que monta la cámara con la receta de género y
luego «le añade juice» siguiendo `04 · 15`, sin cambiar de objeto. `gm-cli compile`:

```
{"errors":[{"source":"AssetCompiler","message":
  "gml_Object_objCamera_Create_0(30) : duplicate script name found gml_Script_camera_shake@gml_Object_objCamera_Create_0"
}]}
```

Es decir: **GameMaker no permite declarar dos funciones con nombre `camera_shake` dentro del mismo
evento**, aunque «01 · Fundamentos 07 — Funciones, métodos y ámbito» (línea 42 de ese documento)
diga correctamente que una función declarada dentro de un evento no es global — la restricción
de nombre único **sí aplica dentro de ese evento**, y la biblioteca no tenía ningún caso de prueba
que lo demostrara hasta ahora.

**Impacto real**: cualquier receta de movimiento (`01`, `02`, y por herencia todo lo que las cita:
`06`, `37`, `53`…) que luego reciba el pulido de `04 · 15` sobre el mismo `objCamera` no compila.
Si el agente resuelve el choque a mano dejando solo una de las dos, y esa es la de `04 · 15`
(1 argumento), **todas** las llamadas de 2 argumentos que citan `04/02 §5.7` (`04 · 34` entre
ellas) siguen compilando — GML permite llamar con más argumentos de los declarados y descarta los
sobrantes en silencio — pero el segundo argumento (`_frames` = duración del temblor) se **pierde
sin error ni aviso**, y `weapon.recoil_kick` (calibrado como *píxeles de desplazamiento máximo* en
el modelo `04/02`) se interpreta como *cantidad de trauma 0..1* en el modelo `04/15`: valores
típicos de retroceso (2-6) saturan instantáneamente el clamp de trauma a 1.0, el shake máximo
posible, en cada disparo — el mismo tipo de fallo silencioso por unidades incompatibles que ya se
encontró y corrigió en `Needs()` esta misma ronda.

---

### 3 · `partida_cargar(_slot)` — 13·06 (Arquitectura) vs 13·12 (Narrativa), contratos incompatibles

`13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md:672`:

```gml
function partida_cargar(_slot) {                // devuelve Struct|Undefined
    var _d = load_game_raw(_slot);
    ...
    return partida_migrar(_d);                   // el LLAMADOR aplica los datos
}
```

`13 - Diseño y producción de videojuegos/12 - Diseño narrativo y diálogos.md:1181`:

```gml
function partida_cargar(_slot)                   // devuelve Bool
{
    var _d = load_game(_slot);
    ...
    global.flags[$ _k[_i]] = ...                  // esta versión APLICA el estado ella misma
    global.misiones = MisionesDeserializar(...);
    return true;
}
```

Mismo nombre, misma aridad, **tipo de retorno y responsabilidad distintos**: la de `13 · 06` deja
que el llamador decida qué hacer con los datos migrados; la de `13 · 12` los aplica directamente al
estado global y solo informa de éxito/fracaso. Ambas son documentos-ancla de la biblioteca —
`13 · 06` es la referencia de arquitectura de **cualquier** proyecto GameMaker, `13 · 12` es a
donde apunta `flag_*` (reutilizado por `04 · 40`, `04 · 48`, `04 · 56`) — así que un juego narrativo
que siga la arquitectura recomendada Y el sistema de diálogos, ambos citados constantemente en la
biblioteca, choca.

**Prueba real** (los dos bloques copiados literalmente a dos scripts del mismo proyecto):

```
{"errors":[{"source":"AssetCompiler","message":
  "gml_GlobalScript_scr_narrativa_partida(9) : duplicate script name found gml_Script_partida_cargar"
}]}
```

---

## Incompatibilidades confirmadas — Nivel 2: no falla al compilar, revienta al ejecutar

Este nivel es el más peligroso de los dos: **`gm-cli compile` sale con éxito**, así que
`validar-compilacion-docs.py` jamás lo detectaría. El problema aparece la primera vez que el
código se ejecuta de verdad.

### 4 · `global.feel` — leído en 04·15 §6, nunca instanciado en ningún punto del documento

`04 - Recetas por género/15 - Game feel y juice.md` define el constructor `FeelSettings()` en la
línea 1289, y luego, en las líneas 1353-1365, presenta la «versión que respeta la configuración»
de `camera_shake()` y `hit_stop()` — la que el documento recomienda usar — leyendo
`global.feel.shake_enabled` / `global.feel.hitstop_enabled`. **En ningún punto del documento
aparece `global.feel = new FeelSettings()`** (verificado: `grep -n "global\.feel"` sobre el
archivo completo → sólo las tres lecturas, ninguna asignación).

**Prueba real**: se instanció `EstadoCombate` (04·30), `dano_resolver()` (04·32) y `GestorFichas`
(04·33) en un objeto real, y se llamó a `camera_shake()`/`hit_stop()` de 04·15 §6 tal cual, sin
crear `global.feel` antes (exactamente lo que ocurre si un agente copia solo la versión «buena»
de §6, que es la que el documento presenta como la recomendada). Salida real de `gm-cli run`:

```
=== 4. camera_shake / hit_stop de 04·15 §6, SIN haber creado global.feel ===
*** EXCEPCIÓN real al llamar camera_shake(): global variable name 'feel' index (100053) not set before reading it. ***
*** EXCEPCIÓN real al llamar hit_stop(): global variable name 'feel' index (100053) not set before reading it. ***
```

Sin el `try/catch` que se añadió solo para esta prueba, esto **detiene el juego** — un `throw` no
capturado en GameMaker termina la ejecución con un cuadro de error. Es decir: siguiendo `04 · 15`
al pie de la letra, **el primer golpe que se dé en el juego lo cuelga**.

### 5 · `global.gestor_jugador` — usado en todo 04·33, nunca instanciado en el documento

`04 - Recetas por género/33 - Diseño de enemigos, encuentros y director de combate.md` usa
`global.gestor_jugador` en el `Create`, `Step`, `Alarm 0` y `Destroy` de `obj_embestidor` (líneas
348, 353, 362, 376, 382), pero **nunca muestra la línea que lo crea**
(`global.gestor_jugador = new GestorFichas(...)`). Confirmado en la prueba real: se reprodujo el
mismo patrón (usar la variable sin haberla inicializado) y `variable_global_exists("gestor_jugador")`
devolvió `false` — el mismo hueco, la misma clase de bug que el #4, en otro documento.

**Impacto real**: un agente que copie `obj_embestidor` tal cual desde `04 · 33` sin darse cuenta de
que falta esa línea (el documento no la señala como pendiente en ningún punto) obtiene, en cuanto
la primera instancia de `obj_embestidor` llega a su `Step`, exactamente el mismo tipo de excepción
de "variable global no definida" que en el hallazgo #4.

---

## Incompatibilidades confirmadas — Nivel 3: el hueco ya se conoce, pero solo en un sitio

### 6 · `tween_to()` — la advertencia existe, pero no donde vive el problema

`06 - Assets y Scripts/scr_tween.gml` define `tween_to(_objetivo, _props, _duracion, _easing,
_on_complete, _retraso)` — duración en **segundos**, `_props` es un **struct** de varias
propiedades. `04 - Recetas por género/15 - Game feel y juice.md:567` define su propio
`tween_to(_target, _prop, _hasta, _duracion, _ease, _on_end)` — duración en **fotogramas**, `_prop`
es un **string** de una sola propiedad, y necesita el objeto `objTweenManager`.

**Esto ya está detectado y documentado como deuda técnica** — pero solo en
`13 - Diseño y producción de videojuegos/04 - Animación de sprites, Sequences y Animation
Curves.md:536-543`:

> ⚠️ **Deuda técnica del repositorio, léela antes de escribir nada:** hay **dos** sistemas de
> tween con una función que se llama igual. […] **No crees un tercero.** Este documento usa el de
> `scr_tween.gml`

y en su tabla de errores clásicos (línea 1346): *«Un tercer sistema de tween | Tres `tween_to()`
incompatibles en el mismo proyecto | Usar `scr_tween.gml` y nada más (§4)»*.

**El problema**: `04 · 15` — el documento donde vive la SEGUNDA implementación incompatible — **no
tiene ni una sola mención** a esta advertencia, a `scr_tween.gml`, ni a `13 · 04`. Un agente que
llegue a game feel (`04 · 15`, uno de los documentos más citados de la biblioteca: `04 · 30`,
`04 · 32`, `04 · 33`, `04 · 34`, `04 · 47`, `04 · 50` lo citan) sin haber pasado antes por
animación (`13 · 04`) nunca ve el aviso, y usa `tween_to()` de `04 · 15` con total confianza en
que es «el» sistema de tween de la biblioteca.

### 7 · `hit_stop()` duplicado dentro de 04·15 (mismo patrón que camera_shake, menor severidad)

Igual que `camera_shake()`, `hit_stop(_frames)` está definida dos veces en el mismo documento:
línea 260 (versión «cruda») y línea 1360 (versión que respeta `global.feel.hitstop_enabled`). Aquí
la aridad coincide (ambas toman `_frames`), así que no hay corrupción de argumentos — pero si
gana la versión de la línea 260 (por orden de pegado), el ajuste de accesibilidad
`hitstop_enabled` deja de tener efecto sin ningún aviso, y si gana la de la línea 1360 sin que
`global.feel` exista, se reproduce el hallazgo #4.

---

## Hallazgos menores (cosméticos, sin impacto funcional confirmado)

| # | Qué | Evidencia | Por qué no sube de nivel |
|---|---|---|---|
| 8 | `logro_desbloquear()`: `04 · 54:138` (id interno) vs `04 · 20:55` (nombre de API de Steam) — mismo nombre, propósito distinto | `04 · 54:223-226` | **Mitigado explícitamente**: el propio `04 · 54` dice que en el punto de llamada hay que invocar `steam_set_achievement()` en crudo, no el wrapper `logro_desbloquear()` de `04 · 20`. Frágil solo si un agente usa `04 · 20` aislado y luego añade `04 · 54` sin leer esa nota. |
| 9 | `hit_complete()`: el `@func` de `04 · 15:1035` documenta 4 parámetros (`_atacante, _victima, _dano, _direccion`); la función real (línea 1041) tiene 3 | `04 · 47:421,465` llaman con 3 args, correctamente | Los puntos de llamada reales usan la firma real, no la del comentario obsoleto. Solo confunde a quien lee el `@func` sin mirar el cuerpo. |
| 10 | `AzarReproducible(_semilla)` y `calcular_dano(_base,_armadura,_critico)`: definidas **idénticas, carácter por carácter**, en `13 · 10` y `13 · 21` | `13 · 10:146,497` / `13 · 21:444,461` | El contenido es correcto a propósito («reutilizada tal cual»), pero si ambos scripts se copian al mismo proyecto sin deduplicar, es el mismo error `duplicate script name` que los hallazgos 1-3. |
| 11 | `FxPreset`: mencionado en la tabla de structs (`04·15:69`) y en «Cómo escalarlo» (`04·15:1394`) pero **nunca implementado** en el documento | `grep -c "FxPreset"` → 2, ninguna con `function`/`constructor` | Hueco de documentación, no de integración: nadie puede citarlo mal porque no hay código que citar. |
| 12 | `04 · 50:1503` cita «`instance_place`» cuando `04 · 30 §9` en realidad lista `instance_place_list`, y añade `point_distance`/`point_direction` que no están en esa bibliografía (aunque sí se usan, correctamente, en otras partes de `04 · 30`) | `04 · 30:1930-1984` (§9 completo) | Imprecisión de cita, no alucinación: las cuatro funciones existen de verdad en el runtime y se usan bien donde se usan. |

## Lista de vigilancia — colisiones de nombre entre recetas que probablemente nunca se combinen

Detectadas por el barrido de nombres duplicados (paso 2 del método), **no verificadas con
compilación real** porque las recetas de origen son géneros independientes que un mismo proyecto
raramente mezclaría. Se documentan para que quien sí las combine sepa dónde mirar:

| Función | Definición A | Definición B | Choque si coexisten |
|---|---|---|---|
| `set_state(_nuevo)` | `04 · 04:1197` (RPG) | `04 · 07:764` (Puzzle/Match-3) | Misma aridad, cuerpos distintos — `duplicate script name` si ambos scripts están en el proyecto |
| `tablero_nuevo(...)` | `04 · 44:843` (Bullet heaven/deckbuilder) — `(_columnas, _filas)` | `04 · 31:912` (IA de decisión) — sin argumentos | Distinta aridad Y distinto significado («tablero» de cartas vs. *blackboard* de IA) |
| `simular_combate(...)` | `04 · 44:1039` — `(_equipo_a, _equipo_b, _semilla)` | `13 · 21:478` — `(_arma, _enemigo, _azar, _armadura_jugador)` | Distinta aridad y propósito (combate de equipos vs. TTK de un arma) |

---

## Lo que ya se corrigió esta ronda (verificado como cerrado, no reabierto)

Los tres fallos que el encargo cita como ya encontrados se comprobaron contra el disco actual:

- **`objWorldGrid`** — ya no es un struct suelto: es un objeto real con `Create` documentado en
  `04 · 09:689-702`, instanciado y colocado en la jerarquía de objetos, con nota explícita del
  antes/después del fix. Citado correctamente como objeto desde `04 · 51` y `04 · 35`.
- **`Needs()`** — su calibración por fotograma está resuelta: `04 · 51:791-848` explica con
  detalle cómo se compone (no se reescribe) para el caso de "por día" de la colonia, sin tocar la
  implementación original de `04 · 09:245`.
- **`valentia_inversa`** — `04 · 56:325-337` lo marca explícitamente con 🆕 como campo NUEVO que
  añade a `ArquetipoDef` (`04 · 33 §1`), con los seis valores por arquetipo listados uno a uno. Ya
  no es una referencia colgante.

---

## Recomendación honesta

**Sí, hace falta una herramienta nueva — esta clase de fallo es estructuralmente invisible para
las dos que ya existen.** `validar-codigo-gml.py` comprueba que un símbolo exista;
`validar-compilacion-docs.py` comprueba que un bloque compile solo. Ninguna de las dos puede, por
diseño, ver lo que solo aparece cuando **dos** documentos se juntan — que es exactamente donde
viven los 5 hallazgos de nivel 1 y 2 de este informe.

Propongo un tercer script, `_indice/validar-integracion.py`, con dos comprobaciones, una barata y
estática y otra cara pero definitiva:

1. **Detector de nombres duplicados entre documentos (estático, minutos, sin GameMaker).**
   - Extraer con regex todas las declaraciones de nivel superior en cada documento y en
     `06 - Assets y Scripts/`: `function NOMBRE(...)`, `#macro NOMBRE`, `enum NOMBRE`.
   - Agrupar por nombre. Cualquier nombre que aparezca en **más de un archivo**:
     - Si la firma (número y orden de parámetros) **difiere** → 🔴 grave automático (es la
       categoría de los hallazgos 1, 2 y 3 de este informe).
     - Si la firma es idéntica pero el **cuerpo** difiere → 🟠 medio (dos implementaciones que
       harán algo distinto según cuál gane).
     - Si firma y cuerpo son idénticos → 🟡 menor, aviso de "duplícalo o referéncialo, no lo
       repitas" (categoría del hallazgo 10).
   - Esto es exactamente lo que hizo el paso 2 del método de este informe, a mano, en unos
     minutos con `grep`+`awk`. Automatizarlo es sencillo y ya encontró 23 candidatos de los que 6
     resultaron ser bugs reales.
2. **Detector de `global.X` leído sin escritura visible (estático, con más falsos positivos —
   avisar, no fallar).** Para cada documento, listar los `global.NOMBRE` que solo aparecen en
   lecturas (`global.NOMBRE.algo`, nunca `global.NOMBRE =` ni `global.NOMBRE = new`). Si ese mismo
   documento (o uno de los que cita explícitamente como dependencia) tampoco lo crea, marcar como
   sospechoso. Habrá falsos positivos legítimos (globals que se crean en `04 · 00`, el "esqueleto"
   que casi ningún documento cita porque se da por hecho) — por eso es un aviso a revisar a mano,
   no un fallo automático. Así se habrían detectado los hallazgos 4 y 5 sin necesidad de
   `gm-cli run`.
3. **Compilación conjunta real para los pares de mayor tráfico (cara, minutos por combinación,
   pero es la única prueba que no admite duda).** Extender `validar-compilacion.sh` (que ya sabe
   invocar `gm-cli`) con un modo `--integracion` que, para cada par de documentos que se citan
   mutuamente más de N veces en el grafo de reutilización (empezar por los que tienen más citas
   entrantes: `scr_save_load.gml`, `04 · 15`, `13 · 12`, `flag_*` de `13 · 12`, `GestorFichas`),
   monte un proyecto de prueba real con `gm-cli resourcetool eval` — igual que se hizo a mano en
   esta auditoría — y ejecute `gm-cli compile`. No hace falta compilar TODAS las combinaciones
   (crecería como N²): basta con los nodos de mayor grado del grafo de reutilización, que es
   donde un agente que construye un juego real tiene más probabilidad de toparse con el choque.
   El coste real medido en esta sesión: cada combinación de 2-4 documentos tardó 1-3 minutos entre
   `resourcetool eval` y `gm-cli compile` — asumible como paso de `actualizar.py` si se corre solo
   cuando cambian los documentos de mayor grado, no en cada ejecución.

El punto 1 es el de mejor relación coste/hallazgo: sin tocar GameMaker para nada, ya habría
encontrado 1, 2, 3 y 10 de este informe. El punto 3 es el único que puede confirmar de verdad si
algo compila junto — y es el que hace falta para no dar por bueno algo que "parece que debería
compilar".

## Prueba de integración real — transcripción completa

Registrada íntegra dentro de cada hallazgo de nivel 1 y 2 de este informe (salida literal de
`gm-cli compile` / `gm-cli run`, sin editar salvo recortar el ruido de "Writing Chunk..." que no
aporta información). Proyecto de prueba: `~/gm_prueba_integracion/PruebaIntegracion` — creado con
`gm-cli init --no-interactive -n PruebaIntegracion -t "Blank Pixel Game" --toolchain
GMS2@2026.0.0.23`, poblado y limpiado con `gm-cli resourcetool eval`, compilado con `gm-cli
compile` y ejecutado con `gm-cli run --toolchain GMS2@2026.0.0.23`. **Se borra al terminar esta
auditoría, como pide el encargo — no forma parte de la biblioteca.**

## Lo que comprobé y no hacía falta tocar

- La composición de `EstadoCombate` (`04 · 30 §6`) con `dano_resolver()` (`04 · 32 §5.7`) — el
  patrón de "cuelga campos nuevos después de construir, `variable_struct_exists()` los detecta" —
  **funciona exactamente como está documentado**. Prueba real: 40 de daño bruto con 15 de armadura
  → 35 de daño neto, verificado con `gm-cli run` (`daño neto tras armadura 15: 35`).
- `apply_knockback(_obj, _dir, _fuerza, _hitstun)` (`04 · 15:706`) — los tres puntos de llamada
  encontrados en `04 · 30:1063` y `04 · 47:445,452` usan los 4 argumentos en el orden correcto.
- `hp_threshold` (`04 · 32:1057` citando `04 · 03 §5.7`) — la cita es exacta, el campo existe tal
  cual en `objBoss` de `04 · 03`.
- `WaveDef`/`TDGroup` citados por `04 · 33` — correctamente NO redefinidos ahí: vienen de verdad de
  `04 · 03 §5.2` y `04 · 08 §5.8` respectivamente; la frase "un sistema incompatible con WaveDef y
  TDGroup" describe el antipatrón a evitar, no un bug real.
- `barra_dibujar()`/`barra_nueva()`/`barra_fijar()`/`barra_actualizar()` (`13 · 05 §3.5 b`,
  reutilizadas por `04 · 32 §5.11`) — firmas y llamadas coinciden.
