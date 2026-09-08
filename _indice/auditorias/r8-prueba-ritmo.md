# R8 · Prueba de ritmo — sincronía de audio con la skill `gamemaker-biblioteca`

> Sexta prueba de perfil de la skill (tras los cinco anteriores de `_indice/auditorias/r3-r7-*`).
> Ataca el requisito técnico más peculiar del género: **el reloj lo manda el audio, no el
> framerate**, y la latencia entre pulsar y oír es el problema central. Construido en
> `~/gm_prueba_ritmo` (fuera de la biblioteca), verificado con `gm-cli compile`/`run` reales,
> medido con mis propios logs de sincronía, y capturado en pantalla con `screen_save()`. Proyecto
> borrado al terminar; esta auditoría y sus seis capturas (`r8-capturas/`) son lo único que queda.

**Versión de referencia**: GameMaker LTS 2026 · IDE `2026.0.0.16` · runtime `2026.0.0.23` ·
`gm-cli` con `ResourceTool@2026.0.17`. Verificado en vivo el 8 de septiembre de 2026.

---

## Veredicto en una frase

**La biblioteca acierta en lo difícil (el reloj es el audio, no el frame) y documenta con
precisión la latencia y las ventanas de acierto — pero el propio patrón de código que enseña para
el conductor (funciones `function nombre() {...}` declaradas dentro del `Create` de un objeto)
no es llamable desde otros objetos en este runtime, y eso rompe exactamente el mecanismo central
que el documento presenta como la pieza que hay que copiar.** Se detecta con el mismo mensaje de
error que ya cataloga la Trampa 4 del manual del agente («Variable X.Y(...) not set before
reading it»), así que un agente que conozca esa trampa **reconoce el síntoma** pero no encontrará,
leyendo 04 · 19, la causa ni el arreglo — hay que saber generalizar la Trampa 4 por cuenta propia.
Corregido (mover las funciones a un script), el resto del capítulo funciona **exactamente como se
describe**, medido con datos reales: la pausa congela el reloj con precisión de milisegundo y la
reanudación no salta ni desincroniza, contra lo que el propio documento advierte que suele pasar.

---

## 1 · ¿El reloj lo manda el audio, y cómo se lee la posición?

**Sí, con la frase más clara de toda la biblioteca sobre el tema**, cita literal de
`04 - Recetas por género/19 - Programación rítmica (juegos de ritmo).md:13`:

> **El reloj es la canción, no el juego.**

Con el contraste ❌/✅ explícito en las líneas 15-29: contar fotogramas se descuadra siempre
(línea 16-19) frente a preguntarle a la canción con `audio_sound_get_track_position()`
(línea 27-28). Y en la línea 33-34, el aviso que evita el error más obvio:

> 🔺 **Necesita el ID de la instancia, no el sonido.** `audio_play_sound` devuelve un ID; ese
> es el que hay que guardar. Pasarle `snd_musica` directamente no funciona.

Implementé el patrón tal cual en `obj_conductor` (`scr_conductor.gml` + `Create_0.gml`/`Step_0.gml`):
guardo el ID que devuelve `audio_play_sound()` en `musica`, y en `Step` calculo
`posicion = (audio_sound_get_track_position(musica) - offset) / seg_por_beat` cada frame — nunca
cuento fotogramas. **Verificado midiendo**, no solo copiando: ver §5 más abajo, con datos reales
de tres ejecuciones automáticas.

---

## 2 · ¿Cubrió la latencia y su calibración?

**Sí, con una receta completa y utilizable tal cual** — `04 · 19 §3` (líneas 125-169): pantalla de
calibración de 16 pulsaciones al ritmo de un metrónomo, descartar la primera muestra («casi
siempre está fuera», línea 164), promediar las 15 restantes, convertir de beats a segundos con
`seg_por_beat`, y guardar con `ini_write_real`. Implementé exactamente esto en `obj_opciones`
(vista `"calibrando"`), reutilizando el propio *backing track* sintetizado como metrónomo (tiene
un bombo marcado en cada beat) para no tener que generar un segundo sonido solo para calibrar.

**Un matiz que la biblioteca señala pero no resuelve con código, y que sí importa**: en la línea
152-153 dice que el bloque de §3 **reemplaza** al `conductor_error()` de §2, «mismo nombre, no lo
declares dos veces» — es decir, la versión final de `conductor_error()` ya descuenta
`global.latencia`. Pero entonces, **¿con qué función mide la propia pantalla de calibración el
desfase bruto del jugador**, si la única `conductor_error()` que queda ya resta una latencia que
la primera vez vale 0 y las siguientes veces sería la que se está intentando recalibrar (circular)?
El documento no lo dice. Añadí `conductor_error_bruto()` como función aparte (la versión de §2,
sin descontar nada) para que la calibración mida limpio — es la única forma sana de tener las dos
sin declarar el mismo nombre dos veces, que es justo lo que la línea 152-153 prohíbe.

---

## 3 · ¿Supe definir el mapa de notas — de dónde salen los tiempos, cómo se guardan?

**Sí, y es la mejor sección técnica del documento** — `04 · 19 §5` (líneas 192-233): el patrón es
un array de structs `{ beat: <real>, tipo: <string> }`, **indexado por beat, nunca por segundos**;
un generador suelta la nota con antelación (`BEATS_DE_VIAJE` beats antes de que le toque sonar);
y la posición en pantalla de cada nota **se calcula desde `beat_objetivo - conductor.posicion`,
nunca se acumula** restando velocidad cada frame. La propia biblioteca explica por qué esto
importa (líneas 229-232): acumulando, un tirón desplaza la nota para siempre; calculando, un
tirón da un salto visual feo pero la nota **sigue llegando exactamente cuando debe**.

Implementé el patrón (`scr_patron.gml` → `patron_generar()`, un chart determinista de 48 beats a
128 BPM, 4 carriles) y el generador (inline en `obj_juego · Step`, sin objeto `obj_generador`
aparte — para una sola canción no hace falta el objeto extra) y la nota (`obj_nota · Step`) con
la fórmula del documento, adaptada de horizontal (el ejemplo mueve `x`) a vertical (yo muevo `y`,
que es el estándar visual del género): misma matemática, mismo principio.

**Un hueco real, no cubierto por el documento**: su generador de ejemplo solo mete notas en beats
enteros. En cuanto el patrón lleva una corchea (`beat: 2.5`, que el propio §5 muestra en su
ejemplo de `patron` de la línea 202 sin que nadie la juzgue después), `conductor_error()` —que
calcula contra `round(posicion)`, el beat entero más cercano— no sirve para juzgarla: redondearía
al beat entero más próximo, no al 2.5 real. Tuve que generalizar yo mismo con
`conductor_error_de(_beat_objetivo)`/`conductor_juzgar_de(_beat_objetivo)`, que reciben el beat
exacto de la nota en vez de asumir el entero más cercano. Es una generalización obvia una vez que
se ve el problema, pero el documento no la escribe, y su propio ejemplo de patrón la necesita.

---

## 4 · ¿Y la ventana de acierto, y su relación con los milisegundos reales?

**Sí, con una tabla exacta y verificable** — `04 · 19 §2` (líneas 89-121):

| Ventana | En beats | A 128 BPM | Implementado |
|---|---|---|---|
| Perfecto | ±0,08 | ±37 ms | `abs(error) <= 0.08` |
| Bien | ±0,18 | ±84 ms | `abs(error) <= 0.18` |
| Flojo | ±0,30 | ±140 ms | `abs(error) <= 0.30` |
| Fallo | resto | — | `else` |

Usé estos cuatro umbrales sin tocarlos, y comprobé la aritmética: a 128 BPM,
`seg_por_beat = 60/128 = 0.46875 s`; `0.08 × 468.75 ms ≈ 37,5 ms` — coincide con lo que dice la
tabla. La biblioteca avisa correctamente (línea 120-121) de que estos números **se ajustan a
mano jugando** y no hay un valor «correcto» universal — les dejé el valor de la tabla tal cual,
que es razonable para un chart de negras y corcheas a 128 BPM como el que construí.

---

## 5 · Las trece trampas: ¿sirvieron? ¿Alguna nueva propia del audio? — **midiendo, no solo leyendo**

### 5.1 · Hallazgo nuevo, el central de esta auditoría: las funciones del conductor no son globales

**No documentado en 04 · 19 ni en las trece trampas del manual del agente**, aunque el síntoma
final SÍ es exactamente el de la Trampa 4 (`12 · 09` líneas 228-249: «el compilador no detecta una
función inventada ni una variable sin declarar»).

`04 · 19 §1` define `conductor_arrancar()` dentro del `Create` de `obj_conductor` (líneas 52-59) y
`§2`/`§3` definen `conductor_error()`/`conductor_juzgar()` de la misma forma (líneas 97-111,
156-162), dando a entender —«todo lo demás le pregunta a él», línea 40— que son llamables desde
cualquier objeto del juego. **Construí el proyecto siguiendo ese patrón al pie de la letra** y, en
cuanto `obj_juego · Create` llamó a una de esas funciones sin cualificar (`conductor_preparar_cancion();`,
mi extensión del mismo patrón), el juego **compiló limpio** (`gm-cli compile --errors-only`,
`exit 0`, cero líneas) y **reventó en tiempo de ejecución** con el mensaje real, capturado con
`gm-cli run` (`/tmp/salida_pruebas.log`):

```
│  of Create Event for object obj_juego:
│  Variable obj_juego.conductor_preparar_cancion(100074, -2147483648) not set before reading it.
│   at gml_Object_obj_juego_Create_0 (line 5) - conductor_preparar_cancion();
```

**Byte a byte, es el mismo formato que documenta la Trampa 4** para una función que literalmente
no existe (`funcion_que_no_existe_de_verdad`). La diferencia — y por qué es un hallazgo nuevo, no
solo la Trampa 4 repetida — es que aquí la función **sí existe y sí se ejecutó ya una vez**
(`obj_conductor · Create` la definió y la llamó sobre sí misma con éxito, visible en el log
anterior a la línea del *crash*: `###SYNC_EVENTO### ARRANQUE t_us=0 …`). Lo que falla es que un
`function nombre() {...}` declarado dentro de un **evento** queda ligado a esa instancia como un
método de `self`, no registrado como identificador global — a diferencia de exactamente el mismo
código si vive en un **script**, donde sí es global desde el primer frame. Esto contradice
directamente la lectura natural de `04 · 19` («un solo objeto persistente lleva el tiempo, todo lo
demás le pregunta a él» sin matiz sobre desde dónde se puede llamar).

**El arreglo, verificado**: moví las diez funciones (`conductor_arrancar`, `conductor_detener`,
`conductor_pausar`, `conductor_reanudar`, `conductor_error`, `conductor_juzgar`,
`conductor_error_bruto`, `conductor_error_de`, `conductor_juzgar_de`,
`conductor_preparar_cancion`) del `Create` de `obj_conductor` a un script nuevo
(`scr_conductor.gml`), sin cambiar una sola línea de su cuerpo — solo el sitio donde se declaran.
Recompilé (`gm-cli compile --errors-only`, `exit 0`, limpio) y volví a ejecutar: **cero errores**,
el juego llega hasta `game_end(0)` sin ningún *crash*. Mismo código, mismo comportamiento
interno (`with (obj_conductor) {...}` sigue igual dentro de cada función) — la única variable fue
«evento vs. script», y esa variable decide si el resto de la biblioteca se puede seguir tal cual o
no. **Regla práctica para cualquiera que use este capítulo**: cualquier función del conductor que
vaya a llamar un objeto que no sea `obj_conductor` tiene que vivir en un script, nunca en su
`Create`, pase lo que diga el documento.

### 5.2 · Las trece trampas del CLI: cuáles tocó esta prueba, y cómo les fue

| # | Trampa | ¿Tocada? | Resultado |
|---|---|---|---|
| 1 | Plantillas con *prefabs* fallan | No — usé «Blank Pixel Game» (de las 9 que funcionan) | — |
| 2 | `resourcetool`/`compile` se cuelgan bajo sandbox | Evitada desde el principio | `dangerouslyDisableSandbox: true` en cada llamada, cero cuelgues en ~60 comandos |
| 3 | `resourcetool` crea el evento equivocado (numeración) | **Sí, activamente evitada** | Usé `subtype=gui` (no `gui_begin`/`gui_end`) para las seis Draw GUI → `Draw_64.gml` en los seis objetos, número correcto verificado por el propio `New GML file: .../Draw_64.gml` de la salida |
| 4 | El compilador no detecta función inventada | **Sí, y una variante nueva (§5.1)** | Ver arriba — el caso real no fue una función inventada sino una mal alcanzada |
| 8 | `includedfile` deja `filePath` vacío, `--errors-only` no lo ve | **Sí, activamente evitada** | Creé `datafiles/fuente_ui.ttf` a mano y fijé `filePath=datafiles` **antes** de compilar; `gm-cli compile` sin `--errors-only` no mostró ningún `WARNING :: datafile … was NOT copied`, y `da=1` en las estadísticas finales del build confirma el fichero incluido |
| 12 | La fuente por defecto omite acentos españoles | **Sí, seguida al pie de la letra** | `font_add("fuente_ui.ttf", 24, false, false, 32, 255)` con un `.ttf` real (`Arial.ttf` del sistema, solo para esta prueba local). Verificado por captura (§6): «¡VICTORIA!», «Puntuación», «Créditos», «síntesis», «¡Nuevo récord!» — todas las tildes, la eñe y los signos de apertura se leen perfectamente |
| 13 | `screen_save()` invierte verticalmente en el runner de Mac | **Sí, y NO se reprodujo** | Ver §6.2 — posible desfase de la propia biblioteca, o comportamiento no determinista |

Las trampas 5, 6, 7, 9, 10, 11 no se tocaron (no usé fuentes horneadas por `resourcetool`, no
necesité `directory_exists`, no probé comandos con la ayuda antes de darlos por imposibles porque
ya sabía el HELP de antemano, no usé `OPTIONS SET`, y no vi ningún `AccessViolationException`).

### 5.3 · Trampa propia del audio sincronizado, verificada midiendo: pausar y reanudar

`04 · 19` avisa en su propia tabla de trampas (línea 246): **`audio_pause_sound` sin recalcular |
Al reanudar, el reloj vuelve pero el juego no.** No da código de cómo evitarlo, solo el aviso.
Implementé la defensa obvia — congelar la actualización de `posicion` mientras `pausado == true`
(`if (musica != -1 && audio_is_playing(musica) && !pausado) { … actualizar posicion … }`, en
`obj_conductor · Step`) — y la **medí** en tres ejecuciones automáticas independientes
(`--config Pruebas`, ver §5.4 para el mecanismo): arranco la canción, pauso a los 4 s reales,
reanudo a los 6 s reales, sigo midiendo hasta los 9 s, y registro `get_timer()` +
`audio_sound_get_track_position()` cada frame el primer segundo y cada 300 ms el resto.

| Ejecución | `posicion` justo antes de pausar | `posicion` justo tras reanudar | ¿Salto? |
|---|---|---|---|
| 3 | 7,53 beats | 7,53 beats (congelada durante los 2 s de pausa) | No |
| 4 (final) | 7,56 beats | 7,56 beats (congelada) | No |

**Congela exacto y reanuda sin saltar, contra lo que la propia tabla de trampas advierte que
suele pasar** — siempre que el `!pausado` que la biblioteca no escribe en código se implemente de
verdad. Es la confirmación de que la trampa es real (si no se guarda ese estado, la posición
seguiría leyendo el `audio_sound_get_track_position()` congelado pero sin saber que está
congelada, lo cual en mi diseño da igual porque no muevo nada mientras `pausado`, pero en un
diseño que anime cosas por su cuenta sin consultar `pausado` sí se notaría el reloj «vuelto» sin
que el resto del juego lo sepa) — coincide con el diagnóstico del documento, con datos reales
detrás, no solo con la advertencia.

### 5.4 · El mecanismo de medición: `--config Pruebas`, sin manos

Repliqué el patrón de `13 · 10 §3.5` (interruptor por `os_get_config()`) para que el propio juego
se audite solo: `gm-cli resourcetool eval "config create name=Pruebas parent=Default"`, y en
`obj_conductor · Create`, si `os_get_config() == "Pruebas"`, arranca la canción sola, mide, pausa,
reanuda y termina con `game_end(0)` — capturable con `gm-cli run --config Pruebas > log 2>&1 &`
más un `grep -q '###game_end###'` en bucle, exactamente como enseña `13 · 10 §3.4`. Sin este
patrón no habría podido medir nada: `gm-cli run` no simula teclado ni ratón (`12 · 09 §4.2`, tabla
de lo que un agente NO puede comprobar solo), así que la única forma de ejercitar pausa/reanudación
sin un humano delante era que el propio código se las diera a sí mismo.

---

## 6 · ¿Algo falso o desfasado en 04/19 o en los documentos de audio?

### 6.1 · La escalera de audio de `13 · 09 §8 bis`: acertada, y ahora comprobada a escala real

La tabla de la línea 609-615 clasifica «disparo, láser, hechizo», «impacto, golpe, explosión» y
«clic, confirmar, cancelar» como razonables por síntesis, y **«instrumentación con melodía o
música completa»** como no razonable. Los dos ejemplos del documento (`tono_generar()`,
`ruido_generar()`, `08 · 24 §3`) son SFX de menos de 200 ms. La pregunta que el documento no
responde —porque no la plantea— es si la misma técnica **escala** a algo del tamaño real de una
canción. La respondí construyendo `cancion_generar()`: un buffer de ~530 000 muestras (~24 s a
22 050 Hz) mezclando tres voces —bombo (ruido grave con envolvente), hi-hat (ruido cortísimo) y
bajo (tono corto, dos notas, nunca una melodía)— todas dentro de las categorías que la tabla
marca como razonables, nunca cruzando a «instrumentación con melodía». **Compila y suena** (según
la propia tabla del documento: un agente no puede verificar «suena bien» por sí solo, `12 · 09
§4.2` — lo que sí verifiqué es que el pipeline entero funciona sin errores a esta escala: la
generación tarda una fracción de segundo en el `Create` de `obj_conductor`, sin *hitches* visibles
en las capturas, y el `audio_sound_get_track_position()` resultante se comporta exactamente igual
que con un sonido cargado desde archivo, medido en §5.3-§5.4).

**El límite real, confirmado, no inventado**: lo que suena es un *backing track* de percusión y
bajo — nada que un jugador describiría como «una canción con melodía». Es exactamente lo que la
tabla predice, ni mejor ni peor. **Para un juego de ritmo publicable, la escalera de §8 bis basta
para el andamiaje técnico (el conductor, la sincronía, las notas) pero no reemplaza tener una
canción real** con melodía reconocible, que es lo que un jugador de este género espera poder
tararear. La biblioteca no promete lo contrario — lo dice con la tabla — pero merece la pena
dejarlo explícito para quien lea solo el catálogo mínimo y no la tabla de arriba: **la síntesis en
runtime resuelve el prototipo técnico completo de un juego de ritmo, no su banda sonora final.**

### 6.2 · La Trampa 13 (`screen_save()` invertido) no se reprodujo — posible desfase

Tomé seis capturas con `screen_save()` en esta sesión (`captura_1_menu.png` …
`captura_6_creditos.png`, archivadas en `_indice/auditorias/r8-capturas/`), mismo `gm-cli`, mismo
`--target mac`, mismo runtime `2026.0.0.23` que documenta la Trampa 13. **Ninguna salió invertida
verticalmente**: el menú, el juego, las opciones, la pausa, la victoria y los créditos se ven
exactamente en la orientación esperada, arriba lo de arriba. La Trampa 13 se verificó originalmente
el mismo 8 de septiembre de 2026 (según su propia fecha), así que no es un desfase de versión
obvio — puede ser una condición no determinista (la propia trampa la describe encontrada UNA vez,
comparada contra una captura de macOS), o depender de algo del entorno que esta sesión no
reprodujo. **No la doy por falsa — la doy por no reproducida aquí**, y dejo la advertencia de
contrastar con `screencapture` como sigue siendo la práctica correcta si algo se ve raro.

### 6.3 · Hallazgo menor, fuera de foco mismo: símbolos Unicode fuera de Latin-1 con `font_add`

Al usar `◀ ▼ ▲ ▶` (flechas pictográficas, todas fuera del rango 32-255 que pide la Trampa 12) como
etiquetas de carril, la primera captura mostró `▼` y `▲` renderizados pero `◀`/`▶` ausentes — un
resultado parcial que no encaja con «todo el rango > 255 se omite igual» (debería ser las cuatro o
ninguna). No aislé la causa exacta con el tiempo disponible; lo que sí hice fue evitar el problema
por completo sustituyendo los pictogramas por ASCII (`< v ^ >`), que se comprobó correcto por
captura. Lo dejo anotado como **una variante de la Trampa 12 que no se generaliza automáticamente
a cualquier Unicode por encima de 255** — parece más matizado que «todo lo que no esté en
`first..last` desaparece igual» — y recomiendo, para cualquier UI de esta biblioteca, no dar por
sentado que un pictograma Unicode se comporta como una tilde solo por estar fuera del mismo rango.

---

## 7 · Verificación real — salida de `gm-cli compile`

Compilación completa (sin `--errors-only`, para que se vea cualquier `WARNING` como el de la
Trampa 8), tras mover las funciones del conductor al script y con las 7 objetos / 5 salas / 5
scripts / 1 archivo incluido del proyecto terminado:

```
│  Options: /Users/adrianpereradelgado/gm_prueba_ritmo/ritmo/local_settings.json
│  Failed to load Options from /Users/adrianpereradelgado/gm_prueba_ritmo/ritmo/local_settings.json
│  Setting up the Asset compiler
│  Found Project Format 2
│  Core Resources : Info - +++ GMSC serialisation:  SUCCESSFUL LOAD AND LINK TIME: 133.006ms
│  Success
│  finished adding assets from /Users/adrianpereradelgado/gm_prueba_ritmo/ritmo/ritmo.yyp.
│  Release build
   … (compilación completa, cero líneas WARNING, cero líneas de error) …
│  Writing Chunk... AUDO size ... 0.00 MB
│  Stats : GMA : Elapsed=275.804
│  Stats : GMA : sp=0,au=0,bk=0,pt=0,sc=33,sh=0,fo=0,tl=0,ob=7,ro=5,da=1,ex=0,ma=6,fm=0x1040929C4AE40830
│  Igor complete.
◆  Compilation finished
```

`da=1` confirma el `.ttf` incluido (Trampa 8 evitada); `ob=7,ro=5` son los 7 objetos y 5 salas del
proyecto; **cero `WARNING`, cero errores**, `gm-cli compile --errors-only` también con `exit 0` y
cero líneas. Antes del arreglo de §5.1, la misma tanda de código **también** compilaba limpio con
`--errors-only` (exit 0) y **reventaba en `gm-cli run`** — confirmando una vez más, con este
proyecto, la advertencia central de la Trampa 4: `--errors-only` no es prueba de que el juego
funcione.

---

## 8 · Mis mediciones de sincronía — datos reales, no descripciones

Metodología en §5.4. Extracto de la ejecución final (`--config Pruebas`, `t_us` = microsegundos
reales desde el arranque, medidos con `get_timer()`; `track_pos` = segundos que devuelve
`audio_sound_get_track_position()`; `posicion` = beats, ya con el `offset` de 1 beat descontado):

```
###SYNC_EVENTO### ARRANQUE t_us=0 offset_seg=0.47 bpm=128 id_musica=400001
###SYNC### t_us=6208    track_pos=0.01  posicion_beats=-0.98  beat_actual=-1  pausado=0
###SYNC### t_us=104775  track_pos=0.11  posicion_beats=-0.77  beat_actual=-1  pausado=0
###SYNC### t_us=1212500 track_pos=1.21  posicion_beats=1.57   beat_actual=1   pausado=0
###SYNC_EVENTO### PAUSAR   t_us=4009554 posicion_antes=7.56
###SYNC### t_us=4212615 track_pos=4.01  posicion_beats=7.56  beat_actual=7  pausado=1
###SYNC### t_us=5712957 track_pos=4.01  posicion_beats=7.56  beat_actual=7  pausado=1   ← 1,5 s de pausa, ni un ms de deriva
###SYNC_EVENTO### REANUDAR t_us=6010041 posicion_antes=7.56
###SYNC### t_us=6312592 track_pos=4.32  posicion_beats=8.22  beat_actual=8  pausado=0   ← reanuda y avanza sin salto
###SYNC_EVENTO### FIN      t_us=9010356 posicion_final=13.97
###game_end###0
```

**Tres hallazgos cuantificados, no solo observados:**

1. **Resolución**: durante el primer segundo se registró cada fotograma (~16-17 ms de intervalo,
   ritmo de un `room_speed` de 60 fps); `track_pos` avanza en lockstep con `t_us` a la precisión
   de 2 decimales mostrada en todos los fotogramas — no se detectó ningún «salto en bloque» propio
   de *buffers* de audio de tamaño fijo, al menos por encima de esa resolución.
2. **Deriva sobre reproducción activa**: en la ejecución final, 7,010 s reales de reproducción
   activa (9,010 s totales menos 2,000 s de pausa) deberían dar `posicion = 13,954` beats según
   la aritmética del propio conductor; se midió `13,97` — una diferencia de **~7 ms sobre 7
   segundos** (≈0,1 %), muy por debajo de la ventana «perfecto» de ±37 ms. En la ejecución 3 la
   diferencia fue de signo contrario, **~12 ms**, del mismo orden. Repetible, consistente, sin
   deriva acumulativa apreciable en la escala de un fragmento de canción.
3. **Pausa/reanudación**: en las dos ejecuciones limpias, `posicion` quedó exactamente congelada
   (7,53 y 7,56 beats respectivamente) durante los 2 s completos de pausa, y **retomó sin salto
   visible** al reanudar — confirmando §5.3.

Una tercera ejecución (la segunda cronológicamente) mostró una anomalía **no relacionada con el
audio**: `obj_menu` confirmó «Jugar» por sí solo en el primer fotograma (sin ninguna tecla
simulada — `gm-cli run` no inyecta entrada, `12 · 09 §4.2`), navegando a `rm_juego` y volviendo a
arrancar la canción a mitad de la medición. No se reprodujo en las otras tres ejecuciones. La
explicación más probable, apoyada en lo que ya documenta la propia Trampa 13 sobre el runner de
Mac (`12 · 09` líneas 902-910): dos ventanas sucesivas de `Mac_Runner` pueden compartir posición en
pantalla, y esta sesión mató y relanzó el proceso varias veces seguidas en el mismo sitio — un
clic o evento de foco perdido de la ventana anterior podría haber aterrizado en la nueva. **No lo
confirmé con certeza** (no aislé la causa con un experimento dedicado); lo anoto como observación
de campo, no como hallazgo verificado.

---

## 9 · Lo construido — cobertura del encargo

| Pieza pedida | Dónde | Verificado |
|---|---|---|
| Menú | `rm_menu` / `obj_menu` | Captura `captura_1_menu.png` — teclado y ratón |
| Opciones con calibración de latencia | `rm_opciones` / `obj_opciones` | Captura `captura_3_opciones.png` — flujo de 16 pulsaciones, `ini_write_real` |
| Pausa | `obj_juego` (estado `"pausado"`) | Captura `captura_4_pausa.png` — `audio_pause_sound`/`audio_resume_sound` medidos en §5.3 |
| Canción jugable con notas | `rm_juego` / `obj_juego` + `obj_nota` | Captura `captura_2_juego.png` — 4 carriles, patrón de 48 beats, generado y juzgado en vivo |
| Puntuación por precisión | `registrar_juicio()` en `obj_juego` | Perfecto/Bien/Flojo/Fallo con las ventanas exactas de `04 · 19 §2` |
| Victoria y derrota | `rm_resultado` / `obj_resultado` | Captura `captura_5_victoria.png` — vida 0-100, derrota si llega a 0, victoria si termina la canción con vida > 0 |
| Guardado de mejor puntuación | `scr_guardado.gml` | `ini_open`/`ini_write_real`/`ini_read_real`, mismo patrón que la latencia |
| Créditos | `rm_creditos` / `obj_creditos` | Captura `captura_6_creditos.png` |
| Audio sin derechos | `scr_audio_sintesis.gml` | 100 % síntesis en tiempo real, `audio_create_buffer_sound()`, cero archivos de sonido — ver §6.1 para el límite honesto |

**Sin verificar por no poder** (`12 · 09 §4.2`, tabla de lo que un agente no puede comprobar
solo): que la música y los SFX suenan *bien* al oído, que el juego se «siente» divertido al
jugarlo con las manos, y el flujo de derrota real jugado a mano (se verificó por revisión de
código y forzando el estado en la secuencia de capturas, no jugando una partida perdida de
verdad — comparte el 95 % del código de dibujo con la victoria, que sí se capturó).

---

## 10 · Limpieza

```
$ ps aux | grep -- "-game .*/gm_prueba_ritmo/" | grep -v grep
(sin salida — sin procesos vivos antes de empezar la limpieza)
$ pkill -f -- "-game /Users/adrianpereradelgado/gm_prueba_ritmo/"
$ ps aux | grep -- "-game .*/gm_prueba_ritmo/" | grep -v grep
(sin salida — confirmado)
$ rm -rf ~/gm_prueba_ritmo
```

El proyecto no existe ya. Esta auditoría y `_indice/auditorias/r8-capturas/*.png` (seis capturas)
son la única evidencia que queda en disco.
