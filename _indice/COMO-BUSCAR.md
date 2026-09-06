# Cómo buscar en esta biblioteca

> **Árbol de decisión para agentes.** Si eres un LLM y no sabes dónde mirar, empieza aquí.
> La versión legible por máquina de todo esto es [`MAPA.json`](./MAPA.json).

---

## Paso 0 · La regla que va antes que todo

```sh
python3 "_indice/buscar.py" <símbolo>
```

> 💡 **¿No sabes si lo que buscas es un símbolo, un concepto o un ejemplo?** Usa
> `python3 _indice/buscar.py --todo "<lo que sea>"`: barre símbolos, biblioteca,
> manual y código real a la vez, y ordena la respuesta por autoridad.

**Antes de escribir cualquier función de GML.** Si no aparece, no existe en este runtime
(`2026.0.0.23`). El buscador te da la firma exacta, si está obsoleta, la página del manual en
español y en inglés, los documentos que lo explican y los repositorios reales donde se usa.

Tres avisos que puede darte, y qué significan:

| Aviso | Qué hacer |
|---|---|
| `⚠ ÍNDICE CADUCADO` | Hay un runtime instalado distinto del que generó el índice. **No te fíes de la ficha**: ejecuta `python3 _indice/actualizar.py` |
| `⚠ SOLO LECTURA` | Puedes leer la variable, pero **asignarle un valor no hace nada** (`fps`, `view_hspeed`…) |
| `No es una función, constante ni variable del runtime, pero SÍ aparece documentado` | Es un prefijo o una directiva (`gmcallback_`, `#macro`), no un símbolo. Sigue las rutas que te da |

> 💡 **Si `buscar.py` dice que algo no existe, no existe.** El buscador se re-deriva del
> `GmlSpec.xml` del runtime instalado en cada regeneración, y comprueba también el manual
> antes de dar ese veredicto.

### Si el manual no lo explica

Todos los símbolos vigentes del runtime son localizables, pero no todos por la misma vía:

- **[08 · 20 — Lo que el manual no documenta](../08%20-%20Referencia%20GML%20completa/20%20-%20Lo%20que%20el%20manual%20no%20documenta.md)** — las 133 funciones que existen en el runtime y no tienen página oficial, y cómo se comprobó que no es un fallo del espejo.
- **[08 · 21 — Constantes que el manual abrevia](../08%20-%20Referencia%20GML%20completa/21%20-%20Constantes%20que%20el%20manual%20abrevia.md)** — las 47 que el manual solo escribe como rango (`ev_outside_view0...7`, «hasta `argument15`»), incluida **`pi`**. Si buscas una y el manual no la encuentra, está aquí.
- Las páginas marcadas con `<!-- traducido-por-la-biblioteca -->` son traducción propia: YoYo no publicó versión española de ellas.

---

## Paso 1 · ¿Qué te están pidiendo?

### A · «Escribe código GML que haga X»

```
1. python3 "_indice/buscar.py" <cada función que vayas a usar>
2. ¿Existe ya una librería?  →  11 - Código descargado/_CATALOGO.md
3. ¿Cómo lo resuelve la gente?  →  python3 "_indice/buscar.py" --codigo "<concepto>"
4. Convenciones de nombres  →  05 - Referencia/04 - Convenciones y estilo GML.md
5. Valida el proyecto entero: python3 "_indice/validar-proyecto.py" <ruta-del-proyecto>
6. Compila: gm-cli compile
```

### B bis · «Hazme un juego COMPLETO de principio a fin»

Empieza **siempre** por [`04 - Recetas por género/00 - Anatomía de un juego completo.md`](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md).
Es el plano: qué escenas necesita un juego entero (splash, menú, prólogo/vídeo, zonas, pausa,
guardado, endgame, créditos), qué sistemas globales lo sostienen y en qué orden montarlo. Trae
un checklist de «juego completo» y enlaza a la receta de cada pieza. Léelo antes de escribir
nada; luego baja al género concreto en «B».

### B · «Haz un juego de género X»

```
1. 04 - Recetas por género/          ← qué sistemas y en qué orden
2. 11 - Código descargado/_CATALOGO.md  ← qué está ya resuelto por terceros
3. 04 - Recetas por género/15 - Game feel y juice.md  ← desde el día 1, no al final
4. gm-cli init --no-interactive -n <nombre> -t "Space Rocks" --ai --toolchain GMS2@2026.0.0.23
```

⚠️ Las plantillas con *prefabs* fallan en `gm-cli` 2.3.0 en macOS. Usa *Space Rocks* o
*Blank Pixel Game*. Detalle en `07 - Ecosistema/13 - GM CLI - la línea de comandos.md`.

### C · «Explícame cómo funciona X en GameMaker»

```
1. 01 - Fundamentos/            ← el concepto, en español, con el «por qué»
2. 09 - Manual oficial/manual-lts-2026-es/  ← la página oficial completa
3. 10 - Cursos en español/06 y 07  ← si prefieres la explicación de un curso
```

### D · «Mi código antiguo no compila / se comporta raro»

```
1. 01 - Fundamentos/03 - Handles - el cambio clave de 2026.md   ← 🔴 la causa nº1
2. 02 - Novedades 2026/02 - Cambios en GML 2026.md
3. python3 "_indice/buscar.py" <la función sospechosa>   ← ¿está obsoleta?
4. https://github.com/YoYoGames/GameMaker-Bugs  ← ¿es un bug conocido?
```

### E · «¿Qué herramienta / librería / extensión uso para X?»

```
1. 12 - Utilidades e integraciones/_INDICE-UTILIDADES.md
2. 11 - Código descargado/_CATALOGO.md   ← 314 repos descritos en español
3. 07 - Ecosistema/                       ← el contexto y qué está abandonado
```

### F · «¿Qué hay de nuevo? ¿Qué versión uso?»

```
1. 02 - Novedades 2026/01 - Resumen LTS 2026.0.md
2. README.md §2  ← estado del ecosistema con fechas
3. https://releases.gamemaker.io/  ← la fuente viva
```

### H · «Diseña / planifica X» (mecánicas, niveles, arte, UI, sonido, historia, producción)

```
1. 13 - Diseño y producción de videojuegos/_INDICE-DISENO.md  ← la disciplina, del principio al código
2. 04 - Recetas por género/00 - Anatomía de un juego completo.md  ← el plano del juego entero
3. La receta del género en 04 y las librerías de 11 - Código descargado/_CATALOGO.md
```

El orden de lectura por disciplina (diseño de juego, niveles, pixel art, animación, UI,
arquitectura, procgen, físicas y fluidos, matemáticas, IA, sonido, gráficos, narrativa,
input, guardado, red, móvil, rendimiento, testing, producción) está en
`_indice/skills/gamemaker-biblioteca/references/mapa-disciplinas.md`: es el mismo mapa que
usan Claude Code y Codex desde otros proyectos.

### G · «Quiero aprender / enséñame»

```
0. RUTA.md  ← ⭐ la progresión completa de cero a profesional (6 niveles con prueba)
1. README.md §4  ← cuatro rutas según de dónde vengas
2. 10 - Cursos en español/05 - Ruta de aprendizaje en español.md  ← si quieres solo español
3. 03 - Cursos (YouTube)/_INDICE-CURSOS.md  ← 44 capítulos transcritos
```

---

## Paso 2 · Tabla de decisión rápida

| Lo que necesitas | Dónde |
|---|---|
| Firma exacta de una función | `buscar.py <símbolo>` |
| Todas las funciones de una familia | `buscar.py --listar audio_` |
| La página oficial completa | `09 - Manual oficial/manual-lts-2026-es/` (o `-en/`) |
| Un concepto explicado en español | `01 - Fundamentos/` |
| Qué cambió en 2026 | `02 - Novedades 2026/` |
| Qué sistemas lleva un género | `04 - Recetas por género/` |
| Cómo se llama algo | `05 - Referencia/03 - Glosario GML.md` |
| Cómo nombrar mis variables | `05 - Referencia/04 - Convenciones y estilo GML.md` |
| Cómo publicar | `05 - Referencia/02 - Publicar y exportar.md` |
| Código base ya escrito | `06 - Assets y Scripts/` |
| Una librería de terceros | `11 - Código descargado/_CATALOGO.md` |
| Cómo lo hace un juego real | `buscar.py --codigo "<concepto>"` |
| Una herramienta externa | `12 - Utilidades e integraciones/` |
| Diseñar (mecánicas, niveles, pixel art, animación, UI, arquitectura, procgen, físicas, sonido, testing, producción, narrativa, matemáticas) | `13 - Diseño y producción de videojuegos/` |
| Validar todo el GML de un proyecto real | `python3 "_indice/validar-proyecto.py" <proyecto>` |
| Usar la biblioteca desde otro proyecto (Claude Code / Codex) | la skill `gamemaker-biblioteca` (`_indice/skills/gamemaker-biblioteca/SKILL.md`) |
| Multijugador | `12 - Utilidades e integraciones/04 - Multijugador y red.md` |
| Assets gráficos y de audio | `12 - .../06 - itch.io...` y `07 - Ecosistema/09` |
| Dónde preguntar | `07 - Ecosistema/10 - Comunidades y dónde preguntar.md` |
| Aprender en español | `10 - Cursos en español/` |
| La API completa en JSON | `08 - .../＿API del runtime/gml-api.json` |

---

## Paso 3 · Prohibiciones que nunca se saltan

| ❌ Nunca | ✅ En su lugar |
|---|---|
| Editar `.yy` o `.yyp` a mano | `gm-cli resourcetool eval` o el MCP `gamemaker-resource-tool` |
| Suponer una firma de función | `buscar.py <símbolo>` |
| Usar una función obsoleta (hay 171) | El buscador te avisa y sugiere alternativa |
| Aritmética con IDs de assets (`sprite_index + 1`) | Son **handles**: `01 - Fundamentos/03` |
| Copiar código de Pizza Tower, Deltarune, AM2R, Hotline Miami o Kirby | Están para **leer**, no son libres |
| Decir «hecho» sin compilar | `gm-cli compile` y reportar la salida real |
| Usar `npm` | `pnpm` |

---

## Paso 4 · Cuando las fuentes se contradicen

Este es el orden de autoridad, de mayor a menor:

```
1. _indice/simbolos.json  (sale del GmlSpec.xml del runtime instalado)
2. 09 - Manual oficial/   (espejo de manual.gamemaker.io, rama LTS)
3. 02 - Novedades 2026/   (release notes y blog oficial, con fecha)
4. 01, 04, 05, 08, 13     (documentación propia, verificada)
5. 11 - Código descargado (código real: muestra la práctica, no la norma)
6. 03, 10 - Cursos        (pueden estar desfasados; llevan aviso)
```

**Un tutorial de YouTube nunca gana a `simbolos.json`.**

---

## Notas de estado que cambian la respuesta

- **El manual está completo en español.** La traducción oficial llegaba al 86 %; las 401
  páginas que faltaban las tradujo esta biblioteca (llevan `<!-- traducido-por-la-biblioteca -->`),
  además de 3 181 celdas de tablas de argumentos que YoYo había dejado en inglés. **Puedes citar
  `manual-lts-2026-es/` sin comprobar el idioma.** El inglés sigue en `manual-lts-2026-en/`.
- **No existe ningún curso completo de GameMaker en español actualizado a 2026.** Lo más
  cercano son las transcripciones de `10 - Cursos en español/06` y `/07`.
- **El canal Monthly está discontinuado.** Solo hay LTS, Beta y GMRT.
- **El multijugador ya no es el punto débil**: Photon (julio 2026) y Colyseus (agosto 2026)
  tienen API de GML completa.
