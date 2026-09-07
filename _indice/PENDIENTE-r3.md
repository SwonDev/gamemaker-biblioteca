# Tercera ronda — cerrada (2026-09-07)

> **Estado: sin deuda.** `python3 _indice/actualizar.py` termina con
> «Biblioteca coherente. Índices al día y sin deuda pendiente.» y sus **doce pasos en verde**.
> Los informes de las auditorías siguen en [`auditorias/`](./auditorias/) como registro de por
> qué se escribió cada cosa; el veredicto de cierre está en
> [`auditorias/r3-99-cierre.md`](./auditorias/r3-99-cierre.md).

## Qué cambió

**Once encargos de contenido**, salidos de diez auditorías de dominio (909 temas evaluados con
evidencia `archivo §sección`) más una auditoría propia de géneros:

- **`04`** · 46 eje Z falso · 47 beat em up · 48 aventura gráfica · 49 deportes y física de mesa ·
  50 juego de lucha · 51 colonia y constructor de bases · 52 live-ops técnico.
- **`05/05`** entregar el juego: firmar, notarizar y subir a las tiendas.
- **`07/23`** arte generado por IA · **`13/25`** legal de terceros · **`13/26`** comunidad propia.
- Ampliaciones grandes en `13/07` (procedural), `13/22` (ciudades), `01/12` (entrada), `13/05` (UI),
  `13/01` (economía), `04/45` (granja), `04/09` (crafting), `01/14` y `01/15`, `04/14`, `04/21`,
  `07/18`, `13/12`, `08/22`, `13/10`, `12/05`, `12/08`, `04/35` (tablero hexagonal).

## Lo que de verdad cambió la fiabilidad

**Compilar el GML de los documentos** (`validar-compilacion-docs.py`, paso 10 de `actualizar.py`):
extrae 3501 bloques y compila 3216 contra el runtime real en 18 s. Encontró lo que ningún
validador anterior veía — `video_draw()` con cuatro argumentos cuando no acepta ninguno, un
ternario anidado sin paréntesis, `const` (que no existe en GML), pseudocódigo de Python etiquetado
como GML, y decenas de identificadores con eñes que nunca habrían compilado.

**El detector de escrituras en `working_directory` estaba escrito y nunca se llamaba desde
`main()`.** El validador pasaba en verde sin comprobarlo. Ya se ejecuta y afecta al código de salida.

**El espejo del manual está completo por primera vez**: 3119 páginas, 0 ausentes, 0 incompletas,
0 con literales traducidos.

## Trampas del motor descubiertas al compilar

Valen más que cualquier documento, porque no están en el manual:

- **GML no admite notación científica.** `1e10` se trocea en `1` y un identificador `e10`.
- **`function Hijo() : Padre() constructor {}` con el padre no definido crashea el
  `AssetCompiler` entero**, y ese crash se traga los errores de todos los bloques posteriores.
- **El ternario anidado necesita paréntesis**: `a ? x : (b ? y : z)`.
- `const` no existe: es `#macro`. `string_pad`, `path_point_add`, `point_in_polygon`,
  `draw_get_batch_count`, `vk_e`, `keyboard_ime_*` y la familia `locale_*` **no existen**.
- `skeleton_animation_set(animname, [loop])` no tiene argumento de track.
- `skeleton_animation_get_position` devuelve 0-1 normalizado, no segundos.
- `keyboard_unset_map()` no acepta argumentos.

## Lo que queda vivo

Nada bloquea el uso de la biblioteca ni su publicación. Para una ronda futura:

1. Los temas 🟠 y 🟡 de los informes `r3-*.md` que no llegaron a esta tanda: ríos en la generación
   procedural, *backtracking* recursivo de laberintos, roles de sala, CI con `duck` o Gobo (que
   resultó inestable según su propio README), y la propiedad `Version` vía `resourcetool`.
2. La verificación de que el transpilador de TypeScript a GML funciona con LTS 2026.0.0.23:
   su documentación solo declara ≥2024.14.4.
3. Vigilar lo que caduca: versiones de librerías de terceros, políticas de tienda y el estado
   legal del arte generado por IA. Todo lleva su fecha de consulta en el texto.
