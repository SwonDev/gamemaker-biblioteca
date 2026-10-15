# Entrada nativa de Windows; delega al mismo instalador Python.
$ErrorActionPreference = 'Stop'
$script = Join-Path $PSScriptRoot 'instalar.py'
foreach ($candidato in @('py', 'python3', 'python')) {
    $comando = Get-Command $candidato -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $comando) { continue }
    $prefijo = @()
    if ($candidato -eq 'py') { $prefijo = @('-3') }
    & $comando.Source @prefijo -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>$null
    if ($LASTEXITCODE -eq 0) {
        & $comando.Source @prefijo $script @args
        exit $LASTEXITCODE
    }
}
Write-Error 'Falta Python 3.10 o posterior. Instálalo desde https://www.python.org/downloads/.'
exit 1
