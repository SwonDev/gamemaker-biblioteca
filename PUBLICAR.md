# Publicar esta biblioteca

Publicada en <https://github.com/SwonDev/gamemaker-biblioteca>.

## Qué se publica y qué no

| Parte | ¿Va al repositorio? | Por qué |
|---|---|---|
| Documentación propia (`01`-`08`, `10`, `12`, `13`) | ✅ Sí | Trabajo propio · CC BY-SA 4.0 |
| Herramientas (`_indice/`, `instalar.sh`, `reconstruir.sh`) | ✅ Sí | Trabajo propio · MIT |
| La skill (`_indice/skills/`) | ✅ Sí | Es el entregable |
| `11 - Código descargado/_RUTAS.json` y `_CATALOGO.md` (127 KB) | ✅ Sí | Solo nombres, rutas y enlaces a GitHub — ni una línea de código ajeno. Los usa `reconstruir.sh codigo` para saber qué clonar |
| `09 - Manual oficial/` (30 MB) | ❌ No | Copyright de YoYo Games |
| `11 - Código descargado/` — el resto (3,8 GB) | ❌ No | 608 licencias ajenas + juegos comerciales |
| `Lumbre/`, `GameMaker_Fuentes/` | ❌ No | Personal y almacén crudo |

Total publicable: **363 archivos · 14 MB** más los dos ficheros de catálogo de arriba. Está
todo en el `.gitignore` (con la excepción de esos dos, sacados a propósito con un patrón `!`).

## Lo que le pasa a quien clone el repositorio

Al ejecutar `./instalar.sh`, `actualizar.py` deriva `simbolos.json` del `GmlSpec.xml` **del
runtime que esa persona tenga instalado**. Eso no es un apaño: es lo que garantiza que la
biblioteca no le mienta sobre una versión que no es la suya.

`./instalar.sh` también detecta e instala la skill en cada CLI de IA que la persona tenga: Claude
Code, Codex, opencode, Qwen Code, Kimi Code CLI, `~/.agents/skills` (estándar abierto que además
leen Copilot CLI, Gemini CLI y Cursor CLI) y Cline. Investigado en vivo contra documentación
oficial el 07-09-2026 — detalle y fuentes en el README, sección
[«Qué CLI de IA están soportados»](README.md#qué-cli-de-ia-están-soportados). El único archivo que
genera fuera de esas carpetas de skills es
`_indice/skills/gamemaker-biblioteca/AGENTS.md` (derivado de `SKILL.md` por
`_indice/sincronizar-skill.py`, para quien use un CLI que solo lea `AGENTS.md`) — ya incluido en
«La skill» de la tabla de arriba, no hace falta una fila propia.

Lo que **no** tendrá hasta que ejecute `./reconstruir.sh`, y hay que decírselo en el README con
todas las letras:

- **El espejo del manual.** `buscar.py` sigue dando la firma exacta de cada símbolo (sale del
  runtime, no del manual), pero la ficha remitirá a `manual.gamemaker.io` en vez de a un archivo
  local. `gm-cli manual read "<tema>"` cubre el hueco sin conexión; `./reconstruir.sh manual` lo
  reconstruye del todo (ver limitación más abajo).
- **El corpus de código real.** Las búsquedas `--codigo` no devolverán nada hasta
  `./reconstruir.sh codigo`.

## Pendiente antes de publicar

1. ~~**Script de reconstrucción** que descargue el manual y clone los repositorios en la máquina
   de quien clona.~~ ✅ Hecho: `./reconstruir.sh` (`manual` | `codigo`), con los dos scripts que
   llama en `_indice/reconstruccion/`. Detalle:

   - **`./reconstruir.sh codigo`** clona con `git clone --depth 1` los 595 repositorios libres de
     los 608 en `_RUTAS.json`, resolviendo cada URL contra `_CATALOGO.md` (más una regla para los
     193 tutoriales de DragoniteSpam, que el catálogo no lista uno a uno, y 7 excepciones
     verificadas a mano contra GitHub el 2026-09-07 para nombres que no aparecen igual en ambos
     ficheros). Reanudable: si una carpeta ya tiene contenido, se salta; si un `git clone` falla,
     se informa y se sigue con los demás. **Excluye siempre** — sin flag para desactivarlo — los
     13 repositorios de la categoría `juegos_y_motores/` que son un juego comercial conocido
     (Pizza Tower, Deltarune, AM2R, Hotline Miami, Kirby, por nombre) o que no declaran una
     licencia libre reconocida en el catálogo (`--listar-excluidos` da la lista exacta sin clonar
     nada). Probado de verdad: clona repos reales, reanuda sin volver a descargarlos, y falla sin
     abortar el resto ante una URL rota — ver el hilo de la sesión que lo escribió.
   - **`./reconstruir.sh manual`** descarga el sitemap de `manual.gamemaker.io` (rama LTS, en/es)
     y convierte cada página de HTML (RoboHelp) a Markdown con un conversor propio, en la misma
     estructura de carpetas que ya espera `buscar.py`. Reanudable (salta lo que ya exista en
     disco) y limitado a 4 peticiones simultáneas con reintento ante un 429, igual que documenta
     `09 - Manual oficial/README.md`.
     **Limitación asumida y documentada**: el conversor HTML→Markdown *original* que generó el
     espejo ya publicado se perdió — no está en este repositorio ni se encontró copia. Lo que hay
     es una reimplementación, escrita y verificada contra páginas reales del manual en vivo
     (probado contra 34 páginas en inglés: coincide byte a byte en varias tras descontar un
     artefacto que ya traía el propio corpus original — un comentario HTML que se filtraba como
     texto en algunas páginas —, y en el resto la única diferencia real es contenido que YoYo
     Games ha actualizado desde el 1 de septiembre de 2026, o alguna inconsistencia menor que ya
     tenía el original). No reproduce el espejo carácter a carácter y no descarga imágenes (igual
     que el original, documentado en `09 - Manual oficial/README.md`). Es honesto a propósito:
     mejor esto, verificado, que fingir que se recuperó el script perdido.
     Para llegar al mismo nivel de traducción al español que ya tiene esta biblioteca (401
     páginas que YoYo Games no traducía), tras reconstruir el espejo hace falta además
     `python3 _indice/traduccion/tm.py aplicar ""`, que reutiliza la memoria de traducción ya
     publicada — no hay que traducir nada de nuevo.
2. ~~**README de portada.**~~ ✅ Hecho — es lo primero que hay en `README.md`.
3. ~~**Decidir el nombre del repositorio** y si es público desde el primer commit.~~ ✅ Hecho:
   `gamemaker-biblioteca`, público.
4. ~~**Confirmación del autor** antes de `git remote add` y `git push`.~~ ✅ Hecho — el remoto ya
   está configurado y el primer commit, publicado.
