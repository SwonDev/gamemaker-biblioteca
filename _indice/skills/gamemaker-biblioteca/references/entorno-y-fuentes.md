# Entorno, runtime y fuentes

Lee esta referencia una vez por sesión, antes de consultar API u operar GameMaker.
Los sondeos siguientes solo comprueban rutas y comandos: no arrancan el IDE, el juego,
un modelo ni un servicio. Elige el bloque de tu shell; Bash no es requisito en Windows.

Contenido: [capacidades y sondeos](#localizar-biblioteca-y-capacidades) ·
[runtime objetivo](#fijar-el-runtime-objetivo-antes-de-confiar-en-el-índice) ·
[fallback oficial](#fallback-sin-índice-sin-biblioteca-o-sin-gm-cli).

## Localizar biblioteca y capacidades

Una skill instalada es una copia, puede estar incompleta o desfasada aunque responda con
seguridad. La etiqueta `SKILL-VERSION` identifica la revisión; `sincronizar-skill.py` compara
versión y bytes de SKILL, AGENTS y todas las referencias. Si difieren de la fuente canónica,
informa y reinstala con `python3 instalar.py` dentro del alcance autorizado; no cambies a escondidas
la configuración del harness. El paquete de skill puede existir sin la biblioteca completa.

Resuelve la biblioteca en este orden: `GM_BIBLIOTECA` explícita → archivo oculto
`.gamemaker-biblioteca-ruta` junto a la **carpeta de skill instalada** → raíz canónica si
estás leyendo su propio árbol `_indice/skills/` → `~/.config/gamemaker-biblioteca/ruta`.
Comprueba siempre `_indice/buscar.py` en la raíz candidata. El registro por destino permite
usar dos bibliotecas sin que una copia pase silenciosamente a consultar la otra.

El agente obtiene `SKILL_DIR`/`$SkillDir` de la ruta real de `SKILL.md` que acaba de leer;
no pide al usuario que configure esa variable. Conserva la ruta lógica al comprobar el
archivo adyacente, antes de resolver un symlink. `BIB` significa la biblioteca completa,
no la carpeta de esta skill. Un paquete aislado no implica una biblioteca instalada.
La instalación normal, `--harness` y `--destino` escriben su ruta adyacente; el registro
global es fallback y `--destino` solo lo cambia con `--registrar`. No necesitas exportar
variables. La instalación solo requiere Python 3.10+; PyYAML/Pillow son de mantenimiento.

### Bash / zsh

```sh
BIB="${GM_BIBLIOTECA:-}"
if [ -z "$BIB" ] && [ -n "${SKILL_DIR:-}" ]; then
  BIB="$(cat "$(dirname "$SKILL_DIR")/.gamemaker-biblioteca-ruta" 2>/dev/null)"
fi
if [ -z "$BIB" ]; then
  BIB="$(cat ~/.config/gamemaker-biblioteca/ruta 2>/dev/null)"
fi
if [ -z "$BIB" ] || [ ! -f "$BIB/_indice/buscar.py" ]; then
  echo "SIN biblioteca completa: siguen disponibles las referencias del paquete de skill."
elif [ ! -f "$BIB/_indice/simbolos.json" ]; then
  echo "Biblioteca disponible, SIN índice: documentos sí; verificación de símbolos pendiente."
else
  echo "Biblioteca e índice presentes; falta comparar el runtime objetivo con meta.runtime."
fi
command -v gm-cli || true
command -v python3 || true
```

### PowerShell

```powershell
$BIB = $env:GM_BIBLIOTECA
if ([string]::IsNullOrWhiteSpace($BIB) -and (Get-Variable SkillDir -ErrorAction SilentlyContinue)) {
    $rutaDestino = Join-Path (Split-Path $SkillDir -Parent) '.gamemaker-biblioteca-ruta'
    if (Test-Path -LiteralPath $rutaDestino -PathType Leaf) {
        $BIB = (Get-Content -LiteralPath $rutaDestino -Raw -Encoding UTF8).Trim()
    }
}
$rutaGuardada = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.config/gamemaker-biblioteca/ruta'
if ([string]::IsNullOrWhiteSpace($BIB) -and (Test-Path -LiteralPath $rutaGuardada -PathType Leaf)) {
    $BIB = (Get-Content -LiteralPath $rutaGuardada -Raw -Encoding UTF8).Trim()
}
if ([string]::IsNullOrWhiteSpace($BIB)) {
    Write-Output 'SIN ruta de biblioteca: siguen disponibles las referencias del paquete.'
} elseif (-not (Test-Path -LiteralPath (Join-Path $BIB '_indice/buscar.py') -PathType Leaf)) {
    Write-Output 'SIN biblioteca completa: sigue el fallback oficial.'
} elseif (-not (Test-Path -LiteralPath (Join-Path $BIB '_indice/simbolos.json') -PathType Leaf)) {
    Write-Output 'Biblioteca disponible, SIN índice: documentos sí; firmas pendientes.'
} else {
    $metaIndice = (Get-Content -LiteralPath (Join-Path $BIB '_indice/simbolos.json') -Raw -Encoding UTF8 | ConvertFrom-Json).meta
    Write-Output "Índice presente, runtime $($metaIndice.runtime); compáralo con el proyecto."
}
Get-Command gm-cli, python3, python, py -ErrorAction SilentlyContinue | Select-Object Name, Source
```

Los comandos Python del resto del paquete están escritos como `python3`; en PowerShell usa
el intérprete realmente encontrado: `python3`, `python` o `py -3`. Si no hay Python, no declares
que ejecutaste buscadores o validadores. Para leer archivos usa `Get-Content -LiteralPath`;
`Select-String` reemplaza búsquedas textuales simples. Los scripts `.sh` requieren Bash/WSL:
no los presentes como comandos nativos de PowerShell ni instales herramientas sin alcance.
El buscador puede depender de `grep` para búsquedas textuales; una ficha exacta disponible
no demuestra que también funcionen `--texto`, `--manual`, `--codigo` o `--todo`.

Una ruta vacía o caducada no es una avería de Python: evita llamar a `/_indice/buscar.py`.
Un clon puede contener documentos y herramientas sin tener `simbolos.json`; cada validador
puede necesitar su propio índice o dependencia. Presencia de archivos no certifica ejecución.

## Fijar el runtime objetivo antes de confiar en el índice

1. Recupera engine/toolchain, **runtime de compilación**, target y configuración del proyecto
   desde sus opciones, comandos o CI fijados y recibos de compilación vigentes. Distingue
   GMS2 de GMRT. La versión del IDE en un `.yyp` no basta para identificar el runtime.
2. Lee `meta.runtime` y `meta.fuentes` de `simbolos.json`. El runtime más reciente cacheado
   en la máquina puede pertenecer a otro proyecto: **manda el runtime del proyecto**.
   El r47 de esta biblioteca admite `GM_BIBLIOTECA_RUNTIME`: versión, `runtime-<versión>`
   o directorio de runtime que contenga el spec. Es un selector de la fuente del índice,
   no una orden de actualizar el proyecto. No cambia el toolchain de GameMaker.
3. Si usas el selector, fija exactamente el runtime del proyecto, con `$env:GM_BIBLIOTECA_RUNTIME`
   en PowerShell o `export GM_BIBLIOTECA_RUNTIME=...` en Bash, solo en la sesión necesaria.
   Un valor explícito inválido debe producir **exit 2**, sin escoger otro runtime en silencio.
4. Una ficha solo acredita la versión y cobertura declaradas. Si `meta.runtime` difiere del
   proyecto, no uses el índice para negar o certificar su API. Regenera desde el spec correcto
   con `python3 "$BIB/_indice/actualizar.py"` si está instalado y el mantenimiento está autorizado,
   o contrasta con el manual oficial de la versión objetivo. No actualices GameMaker para
   hacer coincidir el índice. Si falta el dato del proyecto, decláralo pendiente.

`⚠ ÍNDICE CADUCADO` requiere investigar qué runtime comparó el buscador: no basta con que
el runtime de máquina coincida con el índice si ambos difieren del proyecto. La referencia
histórica de la biblioteca es LTS 2026.0, IDE 2026.0.0.16 y GMS2 2026.0.0.23; no obliga a migrar
un proyecto con otra versión. Conserva engine, runtime y target elegidos por el usuario.

## Fallback sin índice, sin biblioteca o sin gm-cli

- **Con biblioteca e índice compatibles:** consulta `buscar.py`; confirma firma completa,
  obsolescencia y notas del manual antes de recomendar un símbolo.
- **Con documentos pero sin índice:** los documentos siguen disponibles. Si existe `gm-cli`,
  usa `gm-cli manual read "<símbolo>"` y comprueba qué rama/versionado entrega. No conviertas
  un fallo del buscador en «la función no existe».
- **Sin gm-cli o sin biblioteca completa:** usa el **manual oficial en la web**, desde
  [GameMaker Manual LTS en español](https://manual.gamemaker.io/lts/es/index.htm) o
  [GameMaker Manual LTS en inglés](https://manual.gamemaker.io/lts/en/index.htm).
  Selecciona la rama que corresponda al runtime objetivo; para cambios o diferencias de versión,
  contrasta las notas oficiales de esa versión. Si el manual no fija la revisión exacta,
  declara ese límite y no presentes una firma de otra rama como certificada para el proyecto.
- **Sin acceso a una fuente primaria aplicable:** explica qué falta y conserva el estado
  «no verificado». Nunca completes una firma de memoria. Puedes avanzar en diseño o lectura
  sin prometer haber comprobado todas las funciones.

En el reporte de API conserva símbolo, firma, rama/versión, URL o ruta de la fuente y fecha
de consulta. La falta de índice no prueba ausencia de un símbolo. Un resultado negativo de
un índice disponible solo describe **esa versión y esa cobertura**: revisa `fnames`, structs,
enumeraciones, APIs de plataforma y extensiones o funciones propias antes de negar su existencia.
El aviso histórico de r46 sobre el canal `monthly` se refiere al entorno documentado; comprueba
la rama oficial aplicable al proyecto en vez de reutilizar un enlace antiguo sin abrirlo.
