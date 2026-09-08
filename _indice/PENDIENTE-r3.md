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

## Lo que quedaba vivo — cerrado el 08-09-2026

Los seis puntos que dejó abiertos esta ronda están resueltos. Ninguno se cerró escribiendo lo
que parecía razonable: los cuatro primeros son código nuevo que compila contra el runtime real,
y los dos últimos son verificaciones en vivo que **contradicen** lo que anunciaban los README.

1. **Ríos** → `13/07 §2 bis`. El método completo, con el paso que casi todo el mundo se salta:
   rellenar depresiones (*priority-flood*, Barnes 2014) antes de trazar nada. Sin él, «ir cuesta
   abajo» se atasca a la tercera celda sobre cualquier mapa de Perlin. De regalo salen los
   lagos, que ya están calculados en ese mismo paso.
2. **Laberintos por backtracker recursivo** → `13/07 §3 quinquies`, con pila explícita (la
   recursión de verdad llega a `ancho × alto` de profundidad), trenzado para quitar callejones y
   la tabla de sesgos: por qué el árbol binario deja siempre un pasillo recto que arruina el
   laberinto.
3. **Roles de sala** → `13/07 §7.4`. Distancia **de grafo**, no de pantalla — el error clásico
   coloca al jefe a dos pasillos de la entrada en un nivel en herradura. Con las tres trampas:
   la llave nunca detrás de su puerta, `-1` no es una distancia grande sino una sala
   inalcanzable, y el jefe más lejano puede ser una sala de 5×5.
4. **La propiedad `Version` por `resourcetool`** → ya estaba resuelta en la Trampa 10 de
   `12/09`, y se ha vuelto a comprobar de forma independiente: se **lee** (`options get`), no se
   **escribe** (*«cannot be set… because it is read-only»*), y no hay ninguna raíz de expresión
   que la alcance porque las opciones no están entre los 17 tipos de `RESOURCE TYPES`.
5. **Puerta de CI por estilo** → `07/13 §11 bis` y `12/01 §2`. El resultado útil es negativo y
   por eso importa: de las cuatro herramientas del ecosistema, **solo GoboCat devuelve un código
   de salida distinto de 0**. `--check` de Gobo original y `lint` de `@turlututu-games/gml-linter`
   terminan siempre en éxito —verificado en el código fuente de sus *releases*, no deducido—, así
   que un job construido sobre ellas pasa siempre en verde con la lista de errores impresa
   encima. Y `cargo install duck` **instala un crate de otro autor**: el nombre está ocupado en
   crates.io desde 2017.
6. **Transpilador TypeScript → GML con LTS 2026** → `12/08`. Sigue sin verificar contra
   `2026.0.0.23` y ahora se sabe por qué no lo va a estar pronto: `0.0.11` de abril de 2026, sin
   un solo *commit* desde entonces. Y un hallazgo nuevo: `pre_project_step.sh` es **idéntico byte
   a byte** al `.bat`, sin *shebang* — la compilación automática está rota en macOS y Linux, falla
   en silencio y la PR que lo diagnostica se cerró sin fusionar.

Además, la auditoría de integración bajó de 4 duplicaciones medias a 3: `logro_desbloquear`
estaba declarada con la misma aridad en `04/20` (envoltorio de Steam) y en `04/54` (sistema
interno del juego), sin que ningún texto avisara del choque de nombre. Se ha renombrado la de
plataforma a `plataforma_logro_desbloquear` y documentado la relación en los dos sentidos. Las
tres que quedan son deliberadas y su propio texto lo dice («reemplaza a la versión de §2»).

Informe de la verificación de herramientas: [`auditorias/r11-linters-ci.md`](./auditorias/r11-linters-ci.md).

## Lo que sigue vivo

**Vigilar lo que caduca**: versiones de librerías de terceros, políticas de tienda y el estado
legal del arte generado por IA. Todo lleva su fecha de consulta en el texto. GoboCat en concreto
avisa de que cambia *«weekly»*, así que la versión fijada en el job de CI (`v0.7.1`) hay que
revisarla de vez en cuando.
