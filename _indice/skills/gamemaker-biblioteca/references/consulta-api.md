# Consulta y escritura de GML

Lee antes de escribir o recomendar símbolos, incluso en una respuesta sin código.

Contenido: [firmas y validador](#la-regla-que-gobierna-todo) ·
[consultas](#comandos-de-consulta) · [autoridad](#orden-de-autoridad-cuando-las-fuentes-se-contradicen) ·
[convenciones](#convenciones-del-código-que-generes).

## La regla que gobierna todo

**Cada símbolo de GML se verifica antes de escribirlo — la firma ENTERA, no solo que exista**:
confirmar el nombre y adivinar los argumentos «porque suenan razonables» es el fallo que cuela
código roto (caso real en `_indice/auditorias/r5-revalidacion.md`).

> 🔴 **Y esto vale también cuando NO estás escribiendo código.** Nombrar una función en una frase
> —«desactívalo con `sprite_set_interpolation`»— cuenta como escribirla: el usuario la va a
> copiar igual. **Antes de enviar cualquier respuesta que recomiende una función de GML, verifica
> todas las que hayas nombrado con el índice compatible o el manual oficial aplicable**, aunque estés seguro y aunque sea una sola línea de
> conversación.
>
> No es una precaución teórica. El 09-09-2026, un CLI con esta skill cargada respondió a «mi
> sprite se ve emborronado» recomendando `sprite_set_interpolation()`. **No existía en el runtime consultado.**
> Había consultado la biblioteca para el resto de la respuesta y aun así añadió ese nombre de
> memoria, que es exactamente el fallo que esta skill existe para impedir. Este nombre se cita como contraejemplo histórico, nunca como API utilizable. Si te descubres
> recomendando un nombre sin verificarlo en este turno, detente y consúltalo.

```sh
python3 "$BIB/_indice/buscar.py" nombre_de_la_funcion
```

- Aparece → cuenta los argumentos de la línea `firma:` — cada `[nombre]` entre corchetes es
  opcional, el resto obligatorio, siempre en ese orden (p. ej. `audio_play_sound(index, priority,
  loop, [gain], [offset], [pitch], [listener_mask])` exige 3 como mínimo y admite hasta 7) — más si
  está obsoleta, la página del manual (es/en) y dónde se usa en código real. Escríbela tal cual.
- No aparece → no está en la cobertura del índice de **esa versión**. Antes de negar que exista,
  comprueba que coincide con el proyecto y revisa `fnames`, manual, structs/enumeraciones,
  API de plataforma, extensiones y funciones propias. El buscador sugiere nombres parecidos.
- `⚠ ÍNDICE CADUCADO` → compara el runtime del proyecto y `meta.runtime`; consulta la fuente
  correcta o regenera con el selector explícito dentro del mantenimiento autorizado.
- `⚠️ SOLO EN fnames` → existe pero Feather no la autocompleta; pruébala antes de apoyarte en ella.
- «obsoleta» → usa la alternativa que indica la ficha.
- **Structs y enumeraciones incorporados** (`AudioBus`, `AudioEffectType`, `AnimCurveChannel`…)
  no son símbolos de `GmlSpec.xml`: la ficha lo dice y da su página del manual. Sus propiedades
  y valores (`AudioBus.gain`, `AudioEffectType.LPF2`) se leen ahí o con `--manual "AudioBus"`.

Antes de compilar, pasa el validador sobre el proyecto entero: lista por nombre cada llamada a
una función del runtime que no existe, dónde está y cuál parecida sí existe. Funciona también
sobre una carpeta suelta de `.gml` sin `.yyp`; en ese caso dilo en el reporte, porque no habrá
compilación que lo confirme.

```sh
python3 "$BIB/_indice/validar-proyecto.py" /ruta/al/proyecto --todo
```

**Usa `--todo` para ver el detalle de nombres desconocidos.** El validador actual hace fallar
las llamadas a nombres que no define el proyecto, no declara el runtime y no reciben ninguna
asignación, también sin `--todo`. Los desconocidos plausibles como métodos o extensiones
requieren revisión: ni la lista ni un exit 0 demuestran resolución dinámica en runtime.
Consulta el `--help` de la versión disponible; no reutilices semántica de flags de una copia vieja.

## Comandos de consulta

| Necesito | Comando |
|---|---|
| Ficha de una función, constante o variable | `python3 "$BIB/_indice/buscar.py" draw_sprite_ext` |
| Toda una familia | `python3 "$BIB/_indice/buscar.py" --listar audio_` |
| No sé si es símbolo, concepto o ejemplo | `python3 "$BIB/_indice/buscar.py" --todo "coyote time"` |
| Un concepto en la biblioteca | `python3 "$BIB/_indice/buscar.py" --texto "delta_time"` |
| Cómo lo resuelve código real | `python3 "$BIB/_indice/buscar.py" --codigo "state machine"` |
| La página oficial completa | `gm-cli manual read "surface_create"` o el archivo `manual (es)` que da la ficha, bajo `$BIB/09 - Manual oficial/manual-lts-2026-es/` |
| **`place_meeting()` y compañía** | Usan **la máscara de QUIEN LLAMA**, no la del objeto que les pasas — la firma `place_meeting(x, y, obj)` invita a leerlo al revés. Medido: llamarla desde un objeto **sin sprite** devuelve `false` SIEMPRE, contra todo y en todos los ángulos. Para comprobar la colisión de otra instancia, `with (esa) { … }`. `01/08` |
| **Un sprite que GIRA y mata** | Con máscara `Rectangle`, girar el sprite **agranda la hitbox**: el manual dice que es *«an axis-aligned bounding box around the (rotated and scaled) instance»*, así que envuelve al sprite ya girado y crece **√2 a 45°** — 18 px pasan a **25,46**. Un engranaje mata 3,7 px más lejos en unos ángulos que en otros y el dibujo no cambia: **la víctima no puede aprenderlo**. Salidas: `Rectangle With Rotation` (la más barata, configura con el IDE o una vía de recursos verificada), `Ellipse` (invariante, mejor para lo redondo), o dejar `image_angle = 0` y girar solo en el `draw_sprite_ext`. Criterio en `01/08` |
| **`other` dentro de un `with`** | **No ve las `var` locales** de la función de fuera: `other._local` revienta con «not set before reading it» — y al ser error de ejecución, **cuelga la sesión** (trampa 22). Usa una variable de instancia, o un struct, que sí viaja por referencia. `12/09` trampa 23 |
| **Un estado que se pierde y no sabes por qué** | Si usas `image_index` para elegir un ESTADO (encendido/apagado, abierto/cerrado) y el sprite tiene `playbackSpeed` distinto de 0, **la animación lo reescribe cada paso**: medido, un estado perdido **30 veces por segundo**. Es de los peores de diagnosticar porque **no está en el código ni en el sprite por separado**, solo en la combinación. Salida: `image_speed = 0` en el objeto, o `playbackSpeed = 0` en el sprite cuando sus fotogramas son variantes y no un ciclo. `auditar-juego-completo.py` lo caza y hace fallar; criterio en `08/01` |

## Orden de autoridad cuando las fuentes se contradicen

```
1. _indice/simbolos.json   → GmlSpec.xml + fnames; solo si meta.runtime coincide con el proyecto
2. 09 - Manual oficial/    → manual oficial de la rama/versión del proyecto; espejo o web verificado
3. 02 - Novedades 2026/    → release notes y blog oficial, con fecha
4. 01, 04, 05, 08, 13      → documentación propia, verificada
5. 11 - Código descargado  → código real: muestra la práctica, no la norma
6. 03, 10 - Cursos         → pueden estar desfasados; llevan aviso
```

Un tutorial nunca gana a `simbolos.json`. Lo no verificado lleva ⚠️ en el texto.

La autoridad depende de versión y cobertura: un índice de escritorio o de otra versión no
invalida APIs de plataforma, extensiones ni una página oficial aplicable a otro runtime.

- Una firma no se supone: se consulta. «Creo que era así» no es una fuente.

- Los IDs de assets son *handles* en 2026: `sprite_index + 1` está muerto.

- Nada de funciones obsoletas (171 en el índice histórico; comprueba el actual): la ficha avisa y da la alternativa.

- Los **identificadores de GML son ASCII puro**: `function añadir()` no compila («invalid token ñ»).
  Nombra en español sin tildes ni eñes; `validar-codigo-gml.py` lo detecta.

## Convenciones del código que generes

`snake_case`; locales con `_` (`var _velocidad`); prefijos `obj_ spr_ snd_ rm_ scr_ fnt_ tset_`;
sin nombres reservados (`x`, `y`, `speed`, `direction`, `id`, `depth`, `score`, `health`,
`lives`) para variables propias; comentarios en español; identificadores de la API en inglés.
Funciones propias sin prefijo de familia del runtime (`draw_`, `audio_`, `ds_`…): confunden
al validador y a Feather.

## Si también está cargada la skill `gamemaker-expert`

Sus patrones de arquitectura sirven. Sus enlaces históricos al canal `monthly` requieren
comprobación: usa el manual oficial de la rama del proyecto, con espejo compatible o web.
Cualquier función que cite se verifica con el índice compatible o la fuente oficial aplicable.
