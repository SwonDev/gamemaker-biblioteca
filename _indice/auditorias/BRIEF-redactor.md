# Brief común para redactar un documento nuevo de la biblioteca GameMaker (v2)

## Qué es la biblioteca

`/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje` es una **base de conocimiento en
español sobre GameMaker LTS 2026.0** (IDE 2026.0.0.16 · runtime 2026.0.0.23) construida para
que un LLM desarrolle cualquier videojuego con el motor **sin inventarse nada**. No es un
proyecto de GameMaker. Léete `AGENTS.md` de la raíz antes de escribir (5 minutos).

La carpeta `Lumbre/` es el juego personal del usuario: **no la toques ni la cites.**

## Tu entregable

Un único archivo Markdown nuevo en la ruta que te indica tu encargo. Nada más: no edites
otros documentos, no ejecutes `_indice/actualizar.py` ni `_indice/construir-indices.py`
(los ejecuta el orquestador al final), no toques `MAPA.json`.

## Reglas inviolables

1. **Todo símbolo de GML que escribas debe existir.** Verifícalo con
   `python3 "_indice/buscar.py" <símbolo>` (desde la raíz de la biblioteca) ANTES de usarlo.
   Si no aparece, no existe: no lo escribas. Familias enteras: `--listar audio_`.
   Los avisos `⚠ SOLO EN fnames` y «obsoleta» significan lo que dicen: evita las obsoletas.
   Para leer la página del manual: `gm-cli manual read "<símbolo>"` o abre el espejo en
   `09 - Manual oficial/manual-lts-2026-es/`.
2. **Las funciones propias que definas en ejemplos NO llevan prefijo de familia del runtime.**
   Prohibido nombrarlas `draw_*`, `audio_*`, `gpu_*`, `ds_*`, `camera_*`, `instance_*`,
   `sprite_*`, `room_*`, `layer_*`, `surface_*`, `shader_*`, `buffer_*`, `string_*`, `file_*`,
   `ini_*`, `json_*`, `physics_*`, `part_*`, `path_*`, `mp_*`, `tile_*`, `tilemap_*`,
   `window_*`, `display_*`, `os_*`, `game_*`, `font_*`, `texture_*`, `vertex_*`, `matrix_*`,
   `math_*`, `keyboard_*`, `mouse_*`, `gamepad_*`, `view_*`, `event_*`, `object_*`, `asset_*`,
   `struct_*`, `array_*`, `variable_*`, `script_*`, `time_*`, `date_*`, `point_*`,
   `lengthdir_*`, `collision_*`, `place_*`, `move_*`, `distance_*`, `angle_*`. Usa nombres de
   dominio en español (`calcular_salto`, `generar_ruido`, `nivel_cargar`). Un validador
   automático marca en rojo cualquier `familia_*(` que no exista en el runtime.
3. **Nombres reservados**: nunca uses como variable propia `x`, `y`, `speed`, `direction`,
   `id`, `depth`, `score`, `health`, `lives`, `image_index`... salvo que quieras la variable
   integrada. Convenciones en `05 - Referencia/04 - Convenciones y estilo GML.md`:
   `snake_case`, locales con `_` (`var _velocidad`), prefijos `obj_ spr_ snd_ rm_ scr_`.
4. **Los IDs de assets son handles en 2026**: nada de `sprite_index + 1`.
5. **Español con ortografía completa** (tildes, eñes, ¿ ¡). Los identificadores de la API en
   inglés. Los comentarios de código en español.
6. **Lo que no hayas verificado contra una fuente primaria se marca con ⚠️.** Es mejor una
   marca honesta que una afirmación bonita.
7. Si al investigar descubres que algo de tu encargo YA está bien cubierto en otro documento
   de la biblioteca, **no lo repitas**: enlázalo y dedica el espacio a lo que falta.

## Formato del documento

Cabecera y estructura (adáptala al tema, pero conserva el espíritu):

```markdown
# NN · Título

> Dos o cuatro líneas: para qué sirve este documento, a quién le hace falta y qué NO cubre
> (con enlace a lo que lo cubre).

---

## 1 · Los principios (la teoría, compacta, con el «por qué»)
## 2 · El método, paso a paso
## 3 · Cómo se traduce a GameMaker (código GML verificado, assets, editor, ajustes del IDE)
## 4 · Checklist
## 5 · Errores clásicos y cómo evitarlos
## Ver también
## Fuentes
```

- Longitud orientativa: **500-1 200 líneas**. Denso, útil, sin relleno; el código completo cuenta
  y se prefiere a la prosa. Si te pasas, recorta prosa, no código pedido. Tablas cuando ordenan.
- Bloques de código con ` ```gml `. Código completo y copiable, no pseudocódigo con `...`.
- «Ver también»: enlaces **relativos y con espacios codificados como `%20`**, como hace el
  resto de la biblioteca. Ejemplo desde una carpeta hermana:
  `[04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md)`.
  Todo enlace que escribas debe apuntar a un archivo que exista (compruébalo con `ls`).
- «Fuentes»: URLs primarias reales que hayas abierto (WebFetch/WebSearch), con la fecha de
  consulta (2026-09-06). Blog y manual oficial de GameMaker, charlas GDC, libros y artículos
  reconocidos del oficio. Un tutorial de YouTube nunca gana al manual.

## Antes de escribir

1. Lee `AGENTS.md` y `04 - Recetas por género/00 - Anatomía de un juego completo.md` para
   coger el tono.
2. Lee los documentos existentes que te lista tu encargo: son lo que NO debes duplicar y lo
   que debes enlazar.
3. Investiga las fuentes primarias del tema. **WebSearch está agotado en esta sesión: no lo
   uses.** Abre URLs concretas con WebFetch o con `curl -sL -A "Mozilla/5.0" <url>` desde Bash
   (gamemaker.io responde a curl con User-Agent; GDC Vault no se puede rastrear). El espejo local
   del manual (`09 - Manual oficial/manual-lts-2026-es/` y `-en/`) y el código de
   `11 - Código descargado/` son fuentes primarias que siempre tienes. Cita solo lo que hayas
   abierto de verdad; lo demás va con ⚠️ y sin URL.
4. Verifica cada símbolo de GML con `buscar.py` y guarda la lista de los verificados.

## Antes de entregar

- `python3 _indice/validar-codigo-gml.py` (desde la raíz; tarda ~10 s) → debe decir 0 inventadas.
- `python3 _indice/verificar-enlaces.py "<carpeta de tu documento>"` → 0 rotas.
- Si tu encargo incluye editar secciones de OTROS documentos, edita solo los que te asigna el
  encargo (otro agente puede estar editando el resto): inserta secciones nuevas o líneas nuevas,
  no reescribas lo existente, y respeta su formato.

## Al terminar, informa de

- Ruta del archivo y número de líneas.
- Lista de símbolos de GML usados (todos verificados) y cualquier símbolo que quisiste usar y
  NO existe (esto es oro: evita alucinaciones futuras).
- Fuentes consultadas.
- Qué quedó marcado con ⚠️ y por qué.
- Qué documentos existentes enlazaste.
