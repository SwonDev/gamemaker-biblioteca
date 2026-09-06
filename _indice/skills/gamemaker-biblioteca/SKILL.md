---
name: gamemaker-biblioteca
description: Fuente fidedigna para desarrollar con GameMaker LTS 2026 y GML. Úsala antes de escribir o revisar GML, ante cualquier duda de API (¿existe esta función?, firma, obsoleta, manual), y al planificar o construir un juego con GameMaker en cualquiera de sus disciplinas: diseño de juego y GDD, niveles, mundo, pixel art, animación, VFX y shaders, UI/UX y accesibilidad, cámaras, arquitectura y patrones, generación procedural, físicas y fluidos, combate y enemigos, IA, pathfinding, progresión, sonido y voz, testing, producción, negocio, narrativa, matemáticas, móvil y 3D. Dispara con GameMaker, GML, gm-cli, archivos .yyp/.yy/.gml, «hazme un juego», y con «no compila» o «se comporta raro» en un proyecto GameMaker.
---

# GameMaker · biblioteca fidedigna

Una base de conocimiento local, en español, verificada contra el runtime instalado. Existe
para que el GML que escribas **no invente nada** y para que cada decisión de diseño tenga
detrás un documento contrastado.

```sh
BIB="${GM_BIBLIOTECA:-$(cat ~/.config/gamemaker-biblioteca/ruta 2>/dev/null)}"
```

Esa línea abre **cada** comando de esta skill: la biblioteca está donde la instalaron, no en una
ruta fija. La escribe `instalar.sh` al copiar la skill; `$GM_BIBLIOTECA` la pisa si hace falta.

Si `$BIB` sale vacío, la biblioteca no está instalada en esta máquina: dilo, y cae a
`gm-cli manual read "<símbolo>"` para cada duda. **Nunca a la memoria.**

## La regla que gobierna todo

**Cada símbolo de GML se verifica antes de escribirlo.**

```sh
python3 "$BIB/_indice/buscar.py" nombre_de_la_funcion
```

- Aparece → tienes la firma exacta, si está obsoleta, la página del manual (es/en) y dónde se
  usa en código real. Escríbela tal cual.
- No aparece → **no existe en este runtime**. No la escribas. El buscador sugiere parecidas.
- `⚠ ÍNDICE CADUCADO` → el runtime instalado cambió: `python3 "$BIB/_indice/actualizar.py"`
  antes de fiarte de ninguna ficha.
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
python3 "$BIB/_indice/validar-proyecto.py" /ruta/al/proyecto
```

## Comandos

| Necesito | Comando |
|---|---|
| Ficha de una función, constante o variable | `python3 "$BIB/_indice/buscar.py" draw_sprite_ext` |
| Toda una familia | `python3 "$BIB/_indice/buscar.py" --listar audio_` |
| No sé si es símbolo, concepto o ejemplo | `python3 "$BIB/_indice/buscar.py" --todo "coyote time"` |
| Un concepto en la biblioteca | `python3 "$BIB/_indice/buscar.py" --texto "delta_time"` |
| Cómo lo resuelve código real | `python3 "$BIB/_indice/buscar.py" --codigo "state machine"` |
| La página oficial completa | `gm-cli manual read "surface_create"` o el archivo `manual (es)` que da la ficha, bajo `$BIB/09 - Manual oficial/manual-lts-2026-es/` |
| Validar todo el GML de un proyecto | `python3 "$BIB/_indice/validar-proyecto.py" /ruta/al/proyecto` |
| Compilar (desde la carpeta del `.yyp`) | `gm-cli compile` · ejecutar: `gm-cli run` |
| Crear o editar recursos (objetos, sprites, rooms, eventos) | `gm-cli resourcetool eval "<comando>"` o el MCP `gamemaker-resource-tool` del proyecto |
| Proyecto nuevo | `gm-cli init --no-interactive -n <nombre> -t "Space Rocks" --ai --toolchain GMS2@2026.0.0.23` |

Las plantillas con *prefabs* fallan en `gm-cli` 2.3.0 en macOS: usa *Space Rocks* o *Blank
Pixel Game*. El manual `monthly` está discontinuado; la rama vigente es **LTS 2026.0**.

## Qué leer según la tarea

El detalle por disciplina, en orden de lectura, está en
[`references/mapa-disciplinas.md`](references/mapa-disciplinas.md). El índice completo de
documentos, generado del disco, en [`references/indice-documentos.md`](references/indice-documentos.md).

| Te piden… | Empieza por |
|---|---|
| Escribir GML que haga X | `buscar.py` por cada símbolo → `11 - Código descargado/_CATALOGO.md` (¿ya hay librería?) → `05 - Referencia/04 - Convenciones y estilo GML.md` |
| Un juego completo, de principio a fin | `04 - Recetas por género/00 - Anatomía de un juego completo.md` y después la receta del género |
| Un juego de género X | `04 - Recetas por género/` — 46 recetas: los 15 géneros clásicos más combate (cuerpo a cuerpo, a distancia, por turnos), daño y estados, enemigos y director, habilidades, traversal, pathfinding, VFX, tutorial, transiciones y pausa, audio reactivo, modding, bullet heaven/autobattler/deckbuilder, y sigilo/horror/granja/idle |
| Diseñar: mecánicas, niveles, arte, UI, sonido, historia | `13 - Diseño y producción de videojuegos/` (mapa en `references/mapa-disciplinas.md`) |
| Estructurar el proyecto para que crezca | `13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md` |
| Explicar un concepto del motor | `01 - Fundamentos/` → la página del manual en `09 - Manual oficial/manual-lts-2026-es/` |
| «No compila» o «se comporta raro» con código antiguo | `01 - Fundamentos/03 - Handles - el cambio clave de 2026.md` → `02 - Novedades 2026/02 - Cambios en GML 2026.md` → `buscar.py` (¿obsoleta?) → github.com/YoYoGames/GameMaker-Bugs |
| Qué librería, extensión o herramienta usar | `12 - Utilidades e integraciones/_INDICE-UTILIDADES.md` → `11 - Código descargado/_CATALOGO.md` → `07 - Ecosistema/` |
| Assets libres (arte, audio, tiles, fuentes) | `07 - Ecosistema/09 - Asset packs y recursos gráficos.md` |
| Publicar, exportar, tiendas | `05 - Referencia/02 - Publicar y exportar.md` → `13 - …/11 - Producción, alcance y lanzamiento.md` |
| Qué cambió en 2026, qué versión usar | `02 - Novedades 2026/01 - Resumen LTS 2026.0.md` → `README.md` §2 |
| Enseñar a alguien que aprende | `RUTA.md`: sitúa el nivel por lo que sabe hacer y da solo material de su nivel y el siguiente |
| No sé por dónde empezar | `_indice/COMO-BUSCAR.md` |

## Orden de autoridad cuando las fuentes se contradicen

```
1. _indice/simbolos.json   → sale del GmlSpec.xml del runtime instalado
2. 09 - Manual oficial/    → espejo de manual.gamemaker.io, rama LTS, completo en español
3. 02 - Novedades 2026/    → release notes y blog oficial, con fecha
4. 01, 04, 05, 08, 13      → documentación propia, verificada
5. 11 - Código descargado  → código real: muestra la práctica, no la norma
6. 03, 10 - Cursos         → pueden estar desfasados; llevan aviso
```

Un tutorial nunca gana a `simbolos.json`. Lo no verificado lleva ⚠️ en el texto.

## Prohibiciones duras

- `.yy` y `.yyp` no se editan a mano: `gm-cli resourcetool eval` o el MCP. El `.gml` sí.
- Una firma no se supone: se consulta. «Creo que era así» no es una fuente.
- Los IDs de assets son *handles* en 2026: `sprite_index + 1` está muerto.
- Nada de funciones obsoletas (hay 171): la ficha avisa y da la alternativa.
- El código de los juegos comerciales de `11 - Código descargado/juegos_y_motores/` (Pizza
  Tower, Deltarune, AM2R, Hotline Miami, Kirby) se lee, no se copia.
- Los **identificadores de GML son ASCII puro**: `function añadir()` no compila («invalid token ñ»).
  Nombra en español sin tildes ni eñes; `validar-codigo-gml.py` lo detecta.
- El asset **Extensión** es la única excepción a lo anterior: `resourcetool` no puede crearlo
  (`Resource type 'extension' is not creatable`), solo el IDE. Ver `07 - Ecosistema/22 - Crear una extensión nativa (guía en español).md`.
- Nada está «hecho» sin `gm-cli compile` limpio y su salida real reportada.

## Flujo para un desarrollo real

1. **Plano**: `04/00 - Anatomía` + receta del género + `13/01 - Diseño de juego` (core loop) +
   `13/14 - El documento de diseño` (el GDD que un agente puede implementar) + `13/11 - Producción`
   (alcance, vertical slice).
2. **Proyecto**: `gm-cli init` (o el `.yyp` existente; `gm-mcp-setup .` si falta el MCP).
3. **Arquitectura**: `13/06` (gestores, escenas, datos) + convenciones `05/04`.
4. **Sistemas**: antes de escribir uno, `11 - Código descargado/_CATALOGO.md`. Entrada, texto,
   diálogos, audio, guardado y UI ya están resueltos por terceros.
5. **GML**: `buscar.py` por símbolo mientras escribes; `validar-proyecto.py` al terminar.
6. **Compila**: `gm-cli compile`; corrige hasta salida limpia; repórtala.
7. **Antes de publicar**: `13/10 - Testing y QA` → `05/02 - Publicar y exportar`.

## Convenciones del código que generes

`snake_case`; locales con `_` (`var _velocidad`); prefijos `obj_ spr_ snd_ rm_ scr_ fnt_ tset_`;
sin nombres reservados (`x`, `y`, `speed`, `direction`, `id`, `depth`, `score`, `health`,
`lives`) para variables propias; comentarios en español; identificadores de la API en inglés.
Funciones propias sin prefijo de familia del runtime (`draw_`, `audio_`, `ds_`…): confunden
al validador y a Feather.

## Si también está cargada la skill `gamemaker-expert`

Sus patrones de arquitectura sirven. Sus enlaces al manual apuntan al canal `monthly`, que ya
no existe: usa el espejo LTS de `$BIB/09 - Manual oficial/`. Cualquier función que cite se
verifica con `buscar.py` igual que las demás.
