# r11 · Linters y formateadores de GML para CI/pre-commit — verificación en vivo

> Verificado en vivo el **8 de septiembre de 2026** contra GitHub API (sin token, límite de
> 60 req/h, nunca agotado — quedaban 25/60 al terminar), el registro de npm vía `pnpm view` y
> descarga directa de tarballs (sin ejecutar `postinstall`, sin `cargo install`). Referencia:
> GameMaker LTS 2026.0 (IDE `2026.0.0.16` · runtime `2026.0.0.23`).
>
> Objetivo del encargo: decidir qué herramienta(s) pueden sostener un job de CI y un hook de
> pre-commit reales — es decir, que **fallen con código de salida ≠ 0** cuando hay violaciones.
> Este informe es solo de investigación: no contiene el YAML del job ni el script del hook.

---

## 1 · duck (analizador estático de GML)

### Veredicto: **VIVA pero dormida** — repo sin archivar, cero commits desde hace 15 meses, nunca llegó a publicarse

- Repo: **[`imlazyeye/duck`](https://github.com/imlazyeye/duck)** — confirmado por GitHub API,
  no hay otro candidato razonable (es el único con ese nombre que analiza GML; el autor firma
  como Gabriel Weiner).
- Lenguaje: **Rust** (468 573 líneas Rust + 6 131 Python de tooling interno, según
  `GET /repos/imlazyeye/duck/languages`).
- Estrellas: 14 · *forks*: 1 · *issues* abiertas: 0 · licencia: **dual MIT/Apache-2.0** (el
  repo declara `Apache-2.0` como licencia "principal" en la API, pero contiene `LICENSE-MIT` y
  `LICENSE-APACHE`; el `Cargo.toml` dice `license = "MIT OR Apache-2.0"` — el badge del README
  dice solo "MIT", así que hay tres fuentes con matices distintos, la más autoritativa es
  `Cargo.toml`).
- **Último commit: `86db8a1` — 2025-06-05T14:20:20Z** ("fix #2 and impl unused_local_variable").
  Sin ningún commit desde entonces — **más de 15 meses** a fecha de esta verificación.
- **Sin releases y sin tags**: `GET /repos/imlazyeye/duck/releases` y `.../tags` devuelven `[]`
  (array vacío), ambos confirmados con dos llamadas independientes. El README linka a una
  página de [Releases](https://github.com/imlazyeye/duck/releases) que **no tiene nada
  publicado**.
- **Único fork existente** (`NPC-Studio/duck`) es un simple espejo — su único *push* es del
  mismo día que el último commit upstream, 3 horas después. No hay ningún fork más activo que
  el original, a diferencia de lo que ocurre con Gobo/GoboCat (§2).
- **Cita textual del README** (`https://raw.githubusercontent.com/imlazyeye/duck/main/README.md`):

  > ⚠️ **duck is not yet released and is unstable! An announcement will be made when 0.1.0 is
  > released**

  El badge de compatibilidad declarado en el propio README:
  `![gm_version](https://img.shields.io/badge/GM%20Runtime-2022.3.0.497-blue)` — **GameMaker
  2022.3.0.497**, cuatro años y muchas versiones mayores antes de LTS 2026.0.0.23. No hay
  ninguna mención a 2024.x, 2025.x ni 2026.x en el README.

### Instalación — el propio README está roto

El README dice: *"The latest release can be found [here](.../releases). Rust users can also
install with `cargo install duck`."* Las dos vías fallan hoy:

1. **La página de Releases está vacía** (verificado arriba) — no hay binario que descargar.
2. **`cargo install duck` instala el paquete equivocado.** Verificado contra la API de
   crates.io (`GET https://crates.io/api/v1/crates/duck`): el nombre `duck` en crates.io
   pertenece a un crate sin relación, `duck 0.2.0` de `lfairy`
   (*"Like `Iterator::peekable`, but can be stacked an arbitrary number of times"*, repo
   `github.com/lfairy/duck`, subido en 2017). El `Cargo.toml` real del proyecto de GML
   (`imlazyeye/duck`) declara `version = "0.0.0"` y **nunca se ha publicado a crates.io** —
   confirmado también porque `cargo install duck` no tiene forma de saber a qué repo apuntar
   sin publicación, y no existe un segundo crate con nombre parecido (`duck-gml`, `duck_gml`)
   en la búsqueda de crates.io.
   - **La única instalación real hoy es compilar desde el código fuente** (`git clone` +
     `cargo build --release`, no ejecutado en esta verificación por la regla de "no instalar
     nada que compile/ejecute código sin avisar" del encargo) — no está documentado como tal en
     ningún sitio del propio repo.

### Comando de ejecución y código de salida — verificado leyendo el código fuente real

No hay binario que probar, así que esto se verificó leyendo `cli/main.rs` y `cli/input.rs`
directamente del repo (commit `86db8a1`, rama `main`), no ejecutando el programa:

```
duck run [--path <dir>] [--allow-warnings] [--allow-errors] [--allow-duck-errors]
          [--color] [--brief] [--ignored-file-paths <rutas...>]
duck new-config [default|full]      # crea .duck.toml en el directorio actual
duck explain <lint_name>            # explica un lint por nombre; hay 40 lints (LINTS.md)
duck emit <output_path> [--path] [--format json|yaml]   # experimental, aviso propio de inestabilidad
```

**Fichero de configuración:** `.duck.toml` (TOML), en el directorio desde el que se ejecuta.
Se crea con `duck new-config`.

**Código de salida de `duck run`** (leído directamente de `cli/main.rs`, función `run`):

```rust
i32::from(
    (!allow_warnings && run_summary.warning_count() != 0)
        || (!allow_denials && run_summary.denial_count() != 0)
        || (!allow_errors && (!run_summary.io_errors().is_empty())),
)
```

Es decir: **`1` si hay warnings, denials (errores de lint) o errores de E/S** (con las tres
excepciones desactivables por flag), **`0` en cualquier otro caso**. Esto es exactamente el
comportamiento que hace falta para un gate de CI — **si el binario existiera para instalar**.

> Este es el único de los cuatro casos de este informe en el que se verificó el código de
> salida **leyendo el código fuente**, no ejecutando el binario — porque no hay binario que
> ejecutar sin compilar desde cero.

---

## 2 · Gobo / GoboCat (formateador de GML)

### Veredicto conjunto: **Gobo VIVA pero de mantenimiento lento — GoboCat VIVA y activa** (fork recomendado para uso real)

### 2.1 · Gobo ([`Pizzaandy/Gobo`](https://github.com/Pizzaandy/Gobo))

- Lenguaje: **C#** (266 346 líneas) + JS/HTML/CSS del *playground* web.
- Estrellas: 33 · *forks*: 8 · *issues* abiertas: 5 · licencia: **MIT**.
- **Último commit: `65310a6` — 2025-11-21T17:50:37Z** ("migrate to slnx + fix website deploy").
- **Última release: `v0.4.0` — 2024-10-14T03:37:32Z** — casi dos años antes de esta
  verificación, y más de un año antes del último commit: hay actividad en el repo (parches,
  refactors, la web del *playground*) que **no se ha vuelto a empaquetar en una release
  descargable** desde entonces.
- Assets de `v0.4.0` (los que se descargarían hoy): `gobo-macos.zip`, `gobo-ubuntu.zip`,
  `gobo-windows.zip` — **binario autocontenido compilado con Native AOT/.NET 8**, confirmado
  también en el propio README ("*Gobo is written in C# and compiles to a self-contained binary
  using Native AOT in .NET 8*").
- **El README (`raw.githubusercontent.com/Pizzaandy/Gobo/main/README.md`) sigue sin documentar
  la CLI**: no hay una sola línea de ejemplo de invocación, ni de `--check`, ni del fichero de
  configuración. Solo enlaza el [formateador web](https://pizzaandy.github.io/Gobo/) para
  probar pegando código. Esto **confirma** lo que ya tenía anotado la biblioteca (`12/01`):
  sigue siendo así hoy.

**Comando, config y código de salida — verificado leyendo `Gobo.Cli/Program.cs` directamente**
(porque el README no lo documenta), contrastado en la rama `main` **y en la etiqueta `v0.4.0`**
(el binario que de verdad se descarga hoy) — el código es idéntico en ambos puntos:

```
gobo [opciones] <archivo-o-directorio>
  -h --help       Ayuda
  -v --version    Versión
  --check         Verifica formato SIN escribir cambios
  --fast          Salta la validación del árbol de sintaxis tras formatear
  --write-stdout  Escribe el resultado por stdout
  --skip-write    No escribe cambios (para pruebas)
```

Fichero de configuración: **`.goborc.json`** (JSON), buscado subiendo por los directorios
padre desde el archivo/carpeta objetivo. Opciones soportadas en v0.4.0, leídas de
`Gobo/FormatOptions.cs`: `UseTabs` (bool, por defecto `true`), `TabWidth` (int, 4), `Width`
(int, 90), `FlatExpressions` (bool, `false`).

> 🔴 **Hallazgo crítico, verificado leyendo el código fuente en la etiqueta `v0.4.0` (el
> binario real descargable hoy):** la función `Run` de `Gobo.Cli/Program.cs` **siempre
> retorna `0` al final**, sin condición sobre si `--check` encontró archivos sin formatear.
> `CheckFile` solo imprime `[Warn] {ruta}` por consola cuando un archivo no está formateado —
> no marca ningún fallo que suba hasta el código de salida del proceso. La única forma de que
> `gobo --check` devuelva algo distinto de `0` es una ruta inválida, un archivo que no es
> `.gml`, o un directorio sin archivos `.gml`. **`gobo --check` en la versión v0.4.0 NO sirve
> como puerta de CI basada en código de salida** — haría falta parsear el `stdout` buscando
> líneas `[Warn]` y fallar el job manualmente si aparece alguna.

### 2.2 · GoboCat ([`EttyKitty/GoboCat`](https://github.com/EttyKitty/GoboCat))

- Es un **fork** de `Pizzaandy/Gobo` (confirmado por el campo `parent` de la API de GitHub) —
  la biblioteca tenía anotada la URL antigua `EttyKitty/Gobo` en `11/_CATALOGO.md:158`, que hoy
  **redirige (HTTP 301)** al nombre correcto `EttyKitty/GoboCat` (HTTP 200): el repo se
  renombró en algún momento; conviene corregir esa entrada del catálogo.
- Lenguaje: **C#**. Estrellas: 0 · *forks*: 2 · *issues* abiertas: 1 · licencia: **MIT**.
- **Último commit: `6154630` — 2026-07-22T20:04:28Z** ("test: Add multiline chain test case")
  — hace algo menos de 7 semanas, mucho más reciente que el Gobo original.
- **Última release: `v0.7.1` — 2026-06-28T10:11:01Z** — con binarios para
  `linux-x64`, `macos-arm64`, `macos-x64` y `windows-x64` (Gobo original solo cubría
  macos/ubuntu/windows genéricos, sin distinguir arquitectura de Mac).
- **Su README SÍ documenta la CLI y el `--check` con exit code**, cita textual:

  > **Check if files are formatted (CI/CD):** Use this in GitHub Actions or build scripts. It
  > will return a non-zero exit code if any files need formatting without actually changing
  > them.
  > ```bash
  > gobo --check ./src
  > ```

  Y también trae la advertencia de madurez, cita textual:

  > [!WARNING]
  > GoboCat is in active development. Options and behaviors change weekly. For stability, use
  > older versions or the original Gobo.

- **Verificado que la promesa del README es cierta leyendo el código**, tanto en `main` como
  **en la etiqueta `v0.7.1`** (idéntico en ambas): `Gobo.Cli/Program.cs` termina con
  `return (isCheckMode && failureCount > 0) ? 1 : 0;` — **sí propaga el fallo al código de
  salida**. Esto es justo lo que le falta a Gobo original y es la pieza que hace falta para
  un hook de pre-commit o un job de CI reales.
- Config: mismo fichero **`.goborc.json`**, mismo mecanismo de búsqueda hacia arriba, pero con
  **muchas más opciones** que Gobo original — 12 claves documentadas en el README (`useTabs`,
  `tabWidth`, `flatExpressions`, `multilineStructs`, `multilineArrays`, `multilineTernary`,
  `multilineArguments`, `multilineConstructors`, `multilineChainedMethods`,
  `blankLineAfterBlocks`, `explicitUndefined`) frente a las 4 de Gobo. Ignora automáticamente
  `node_modules`, `extensions`, `.git`, `.svn`, `prefabs`, `bin`, `obj` (confirmado en
  `Program.cs`, no solo en el README).
- Ninguno de los dos formateadores (Gobo ni GoboCat) declara una versión mínima de GameMaker
  compatible — son formateadores de texto GML puro, no dependen de la instalación del IDE ni
  del runtime. No hay verificación específica contra LTS 2026.0.0.23 más allá de que ninguno de
  los dos documenta haber roto con sintaxis reciente.

---

## 3 · `@turlututu-games/gml-linter` (npm)

### Veredicto: **VIVA** (paquete real, descargable, publicado hace 2 meses) — **pero su modo `lint` no falla nunca por código de salida**

- **Confirmado con `pnpm view @turlututu-games/gml-linter`** (comando real, ejecutado hoy):

  ```
  @turlututu-games/gml-linter@0.0.6 | deps: 4 | versions: 6
  Linting tool for GameMaker Language
  bin: gml-linter
  .tarball: https://registry.npmjs.org/@turlututu-games/gml-linter/-/gml-linter-0.0.6.tgz
  published 2 months ago by leomaradan <npm@leomaradan.com>
  ```

  `pnpm view @turlututu-games/gml-linter time --json` confirma la fecha exacta:
  **`0.0.6` publicada el 2026-06-25T09:18:16Z** — coincide con lo que ya tenía anotado la
  biblioteca. Sin publicaciones nuevas desde entonces (6 versiones en total: 0.0.1 → 0.0.6,
  todas entre 2026-01-14 y 2026-06-25).
- `pnpm view ... engines --json` → **`"node": ">=22.17.1 <23.0.0"`** — rango de Node
  estrictamente acotado a Node 22, dato que no estaba en la auditoría previa y es
  imprescindible para el `node-version` de cualquier job de CI que lo use.
- `pnpm view ... repository` y `... homepage` → **ambos vacíos**. Verificado también
  descargando el `.tgz` real (`curl` directo a la URL de `dist.tarball` de arriba, sin ejecutar
  ningún script del paquete) y leyendo su `package.json`: no declara `repository` ni
  `homepage`, y tampoco declara `license` en el campo del manifiesto (aunque el `.tgz` sí
  incluye un fichero `LICENSE` de texto — MIT, "Copyright (c) 2026 Turlututu Games" — que no
  está enlazado desde `package.json`).
- **Confirmado de forma independiente que no existe repositorio público**: la organización
  `Turlututu-Games` existe en GitHub (`GET /orgs/Turlututu-Games` responde con el login), pero
  solo tiene **dos repos públicos** — `dont-get-caught` y `AudioEngineGML` — ninguno es
  `gml-linter`. Una búsqueda amplia en GitHub (`GET /search/repositories?q=gml-linter`) devuelve
  3 resultados, todos de otros autores y sin relación (`beccapana/GML_linter`,
  `codename-B/gml-lint`, `ThomasHickman/linter-gml`, éste último sin cambios desde 2016). Esto
  reconfirma, hoy, lo que ya tenía anotado la biblioteca: el paquete de npm es la única fuente
  disponible, no hay código fuente público que auditar más allá del propio `.tgz`.

### Comando de ejecución — verificado descomprimiendo el `.tgz` real y leyendo el JS compilado

`bin/gml-linter` es un *wrapper* de una línea (`require('../dist/cli.js')`). El comando por
defecto (registrado en `yargs` como `"$0 [files..]"`, es decir, el comando implícito cuando no
se nombra ningún subcomando) es:

```
gml-linter [archivos...] [--watch|-w] [--fix|-f] [--config|-c <ruta>]
gml-linter extract <archivo-o-carpeta> [--output|-o <ruta>]   # exporta la estructura a JSON
```

Sin argumentos, opera sobre el directorio actual. **Fichero de configuración: `.gml-linter.json`**,
buscado subiendo por los directorios padre desde el archivo objetivo hasta encontrar el config o
un `.yyp` (raíz del proyecto), validado contra un *schema* generado con
`typescript-json-schema` (confirmado en `package.json`, script `"schema"`). 17 reglas activas
por defecto — lista completa ya estaba en la auditoría previa y se confirma sin cambios en
`0.0.6`: `functionName`, `functionParamName`, `noGlobal`, `noTabAsSpace`, `noTrailingSpace`,
`noMultiEmptyLines`, `missingEnumValue`, `missingEventDescription` y seis reglas de formato de
JSDoc.

> 🔴 **Hallazgo nuevo, verificado leyendo el código JS compilado (`dist/cli.js`) de la
> versión 0.0.6 real, extraída del `.tgz` descargado del registro de npm:** en todo el
> fichero solo hay **dos** llamadas a `process.exit()`, ambas `process.exit(1)`, y ambas
> ocurren únicamente cuando la configuración resuelta **no tiene ninguna regla activa**
> ("No rules to apply. Exiting.") — un caso de configuración rota, no de violaciones
> encontradas. La función que imprime el resumen final (`Problems detected in N files.
> warnings X errors Y`) **solo hace `console.log`**, nunca toca `process.exitCode` ni llama a
> `process.exit`. **`gml-linter` (0.0.6) siempre termina con código `0` aunque encuentre e
> imprima errores y warnings de lint** — no sirve, tal cual está hoy, como puerta de CI basada
> en código de salida. Un hook que lo use tendría que capturar y parsear el `stdout` (buscar
> la línea `Problems detected in`) para decidir si falla el commit, igual que con Gobo
> original.

---

## 4 · Transpilador TypeScript → GML: `@odemian/gamemaker-typescript` (`gmts`)

### Veredicto: **VIVA pero estancada** — sin commits desde hace casi 5 meses, con un bug de macOS/Linux **confirmado y sin corregir**

- **Confirmado con `pnpm view @odemian/gamemaker-typescript`** (ejecutado hoy):

  ```
  @odemian/gamemaker-typescript@0.0.11 | MIT | deps: 5 | versions: 12
  bin: gmts, gamemaker-typescript
  published 4 months ago by GitHub Actions <npm-oidc-no-reply@github.com>
  ```

  `pnpm view ... time --json` confirma: **`0.0.11` publicada el 2026-04-17T20:42:58Z** —
  coincide con la auditoría previa. **Sin publicaciones nuevas desde entonces** (12 versiones,
  0.0.0 → 0.0.11, todas entre 2026-03-22 y 2026-04-17: desarrollo muy intenso durante 4 semanas
  y luego silencio de publicación).
  Nota curiosa: la publica una GitHub Action con OIDC (`npm-oidc-no-reply@github.com`), no un
  usuario a mano — sugiere un pipeline de release automatizado, aunque no se ha vuelto a
  disparar.
- `pnpm view ... engines --json` → `{"node": ">=22"}`.
- Repo confirmado en `package.json`:
  **[`OleksandrDemian/gamemaker-typescript`](https://github.com/OleksandrDemian/gamemaker-typescript)**.
  Estrellas: 10 · *forks*: 2 · *issues* abiertas: **0** · licencia: MIT.
- **Último commit: `61cb60b` — 2026-04-18T07:53:33Z** ("fix BoolNumberType") — coincide con el
  release de npm del día anterior. **Sin ningún commit desde entonces**, casi 5 meses.
- Últimas 10 releases de GitHub coinciden exactamente con las 10 últimas versiones de npm
  (`v0.0.2` … `v0.0.11`), sin ninguna posterior.

### El README literal sobre versiones soportadas

Cita textual (`raw.githubusercontent.com/OleksandrDemian/gamemaker-typescript/master/README.md`):

> ⚠️ This project is in very early stage of development and **requires GameMaker v2024.14.4
> (March 2026)**
>
> [...]
>
> Starting from version `2024.14.4` (**April 2026**) GameMaker added `pre_project_step`
> extension hook which allows to compile file before assets collection. So if you use that
> version or newer, after running `gmts setup` GameMaker will automatically compile `.ts`
> files before running the game.

(El propio README se contradice en el mes exacto —"March 2026" en la línea 7, "April 2026" en
la línea 136— para la misma versión `2024.14.4`; no es un error mío de transcripción, son dos
frases distintas del mismo documento con fechas distintas.)

**No hay ninguna mención a `2025.x` ni `2026.0`/`2026.0.0.23` en todo el README** — confirmado
con una búsqueda de texto sobre el documento completo. La compatibilidad con LTS 2026.0.0.23
**sigue sin verificar por parte del propio proyecto**: no hay ninguna señal (ni positiva ni
negativa) de que se haya probado contra esa versión.

### Hallazgo nuevo y verificado en esta ronda: `gmts setup` está roto en macOS y Linux

Se localizaron dos *pull requests* cerradas relacionadas con compilación automática:

- PR #5, *"Fix pre_project_step.sh being a Windows batch script (breaks gmts setup on
  Mac/Linux)"* — **cerrada sin fusionar** (`merged: false`).
- PR/issue #6, *"Fix/pre project step sh"* — también **cerrada sin fusionar**.

El diagnóstico de la PR #5, citado textualmente de su descripción:

> `gamemaker-config/extensions/files/pre_project_step.sh` was byte-identical to
> `pre_project_step.bat` — Windows batch syntax (`@echo off`, `where`, `call`) with no
> shebang. On macOS/Linux, GameMaker's Igor build tool execs this file directly. With no
> `#!/bin/bash` line, the kernel tries to run it as a native binary and fails with `Exec
> format error`, breaking `gmts setup` for every Mac/Linux user.

**Verificado de forma independiente, byte a byte, sobre la rama `master` actual (no sobre la
PR):** se descargaron `pre_project_step.sh` y `pre_project_step.bat` directamente del repo con
`curl` y se compararon con `diff` — **son idénticos byte a byte** (`diff` no reporta ninguna
diferencia). El primer byte del `.sh` es `40 65 63 68...` = `"@echo off"` — **no hay
`#!/bin/bash` ni ningún shebang**. Esto confirma exactamente el diagnóstico de la PR rechazada:
el fichero que `gmts setup` copia como hook de compilación automática para macOS/Linux es, tal
cual, un script de Windows.

> 🔴 **Para esta biblioteca (macOS, GameMaker LTS 2026.0.0.23 en Steam) esto es más grave que
> la duda de compatibilidad de versión**: aunque el proyecto de prueba usara una versión de
> GameMaker ≥2024.14.4, el hook de compilación automática (`gmts setup` → `pre_project_step`)
> **no puede funcionar en macOS tal como está publicado hoy en npm (0.0.11) ni en el código
> fuente actual del repo (`master`, commit `61cb60b`)** — el arreglo existe como propuesta
> (PR #5) pero fue rechazado/cerrado sin fusionar, con lo que el bug sigue vivo. No se ha
> ejecutado `gmts setup` en un proyecto real para confirmar el mensaje de error exacto (habría
> exigido instalar el paquete globalmente, fuera del alcance "no instalar nada" de este
> encargo) — lo verificado es la causa raíz a nivel de fichero, que es suficiente para
> descartar el hook automático sin necesidad de reproducir el fallo en vivo.
>
> La vía manual (`gmts compile`, ejecutado a mano o desde un script propio) no depende de
> `pre_project_step.sh` y no debería verse afectada por este bug — es la única vía fiable en
> macOS hoy, siempre con la reserva de que tampoco se ha ejecutado en esta verificación.

### Limitaciones — cita textual del README, confirmada sin cambios respecto a la auditoría previa

> - The package is currently in the Proof of Concept (PoC) stage.
> - Types are incomplete, and not all object types are supported yet.
> - Enums are not supported
> - Constructor function are not supported

---

## Qué se puede escribir en la biblioteca con esto

**Queda respaldado, con fuente verificada hoy:**

- Los cuatro nombres de paquete/repo son correctos y **están vivos** en el sentido de "existen
  y son descargables/consultables hoy" — ninguno es NO EXISTE.
- **Ninguna de las cuatro herramientas sirve, tal cual, como puerta de CI/pre-commit basada en
  código de salida** sin trabajo adicional:
  - `duck`: el código fuente SÍ implementa el exit code correcto, pero **no hay binario
    instalable** sin compilar desde cero (Releases vacío, `cargo install duck` instala un
    crate ajeno).
  - `Gobo` (original, v0.4.0, el binario real descargable): `--check` **siempre devuelve 0**,
    incluso con archivos mal formateados — bug confirmado en el código fuente de la propia
    etiqueta de la release.
  - `GoboCat` (fork, v0.7.1): **es la única de las cuatro que sí propaga el fallo al código de
    salida**, verificado tanto en el README como en el código fuente de su release más
    reciente. Es la opción recomendable para un hook real, con la reserva explícita de su
    propio README ("changes weekly, for stability use older versions or the original Gobo").
  - `@turlututu-games/gml-linter` (0.0.6): **siempre devuelve 0** salvo con una configuración
    sin reglas activas — confirmado leyendo el JS compilado del paquete real.
  - `gamemaker-typescript`/`gmts` (0.0.11): no es un linter/formateador de estilo sino un
    transpilador; su "modo comprobación" natural sería `gmts compile` fallando si hay errores
    de tipos, pero **eso no se ha verificado en esta ronda** (no se ejecutó el binario).
- **Compatibilidad con LTS 2026.0.0.23**: ninguna de las cuatro herramientas la menciona en su
  documentación, ni a favor ni en contra. Gobo/GoboCat, al ser formateadores de texto GML puro,
  son los que menos dependen de la versión del runtime. `duck` declara compatibilidad con una
  versión de 2022, cuatro años obsoleta. `gmts` declara depender de una característica del
  runtime (`pre_project_step`, GameMaker ≥2024.14.4) cuya disponibilidad en 2026.0.0.23 no está
  confirmada ni desmentida por la fuente — y, además, tiene un bug de plataforma que la
  inutiliza en macOS independientemente de esa duda.
- **`EttyKitty/Gobo` está mal como URL en `11 - Código descargado/_CATALOGO.md:158`** — hoy
  redirige (301) a `EttyKitty/GoboCat`, que es la URL correcta y ya está bien puesta en
  `12 - Utilidades e integraciones/01 - Herramientas del flujo de trabajo.md:54`. Vale la pena
  corregir esa línea del catálogo en la próxima pasada de `_indice/actualizar.py`.

**Queda sin respaldo — no escribir sin decirlo:**

- Que cualquiera de las cuatro herramientas "sirve para CI" sin matices: **es falso para tres
  de las cuatro** (Gobo original, gml-linter, y duck por falta de binario) tal como están
  publicadas hoy. Solo GoboCat cumple la promesa de exit code, y con la reserva de estabilidad
  de su propio README.
- Cualquier afirmación sobre el comportamiento de `gmts setup`/`gmts compile` en ejecución real
  sobre un proyecto de GameMaker LTS 2026.0.0.23 — no se ha ejecutado el binario en esta
  verificación (regla explícita del encargo de no instalar/ejecutar código sin avisar). Lo
  verificado es la causa raíz del bug de macOS a nivel de fichero fuente, no el mensaje de
  error real en pantalla.
- El comportamiento de `duck run` en ejecución real — se verificó leyendo `cli/main.rs`, nunca
  ejecutando el binario (no existe binario que ejecutar sin compilar desde cero).
- Cualquier fecha de "0.1.0" o de una futura release de `duck`: el README solo dice "an
  announcement will be made", sin plazo, y no hay ninguna señal de que vaya a ocurrir pronto
  dado el silencio de 15 meses.
