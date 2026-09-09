#!/usr/bin/env bash
# Cerrojo de carpeta de trabajo — versión shell de `_indice/cerrojo.py`.
#
# Las herramientas que compilan de verdad construyen su proyecto desechable en una
# ruta FIJA de $HOME. Dos ejecuciones simultáneas se pisan a media compilación y el
# resultado no es un error claro sino un FALSO ROJO: fallos que no existen, o peor,
# un fallo sin ni un error listado. Perseguir ese fantasma cuesta una tarde.
#
# `mkdir` es atómico: o lo creas tú, o ya existía. Con eso basta, sin dependencias.
# Se guarda el PID dentro para distinguir un cerrojo vivo de uno HUÉRFANO (el que
# deja un Ctrl-C o un kill). Sin esa recuperación, el cerrojo sería peor que el
# problema: convertiría un corte en un bloqueo permanente.
#
# Uso:
#   . "$(dirname "$0")/cerrojo.sh"
#   cerrojo_tomar "$PROY" || exit 2      # exit 2 = «no se ha comprobado», nunca 1
#   trap 'cerrojo_soltar "$PROY"' EXIT

cerrojo_tomar() {
    _cl="$1.lock"
    if mkdir "$_cl" 2>/dev/null; then
        echo $$ > "$_cl/pid"
        date "+%Y-%m-%d %H:%M:%S" > "$_cl/desde"
        return 0
    fi
    _pid="$(cat "$_cl/pid" 2>/dev/null || echo "")"
    _desde="$(cat "$_cl/desde" 2>/dev/null || echo "?")"
    if [ -n "$_pid" ] && kill -0 "$_pid" 2>/dev/null; then
        echo "✗ La carpeta de trabajo «$1» ya la está usando otra ejecución"
        echo "  (proceso $_pid, desde $_desde)."
        echo "  NO se ha comprobado nada: dos compilaciones a la vez sobre la misma carpeta"
        echo "  se pisan y producen errores que no existen. Espera a que termine la otra."
        return 1
    fi
    # Huérfano o corrupto: su dueño ya no existe. Se recoge y se reintenta una vez.
    rm -rf "$_cl"
    if mkdir "$_cl" 2>/dev/null; then
        echo $$ > "$_cl/pid"
        date "+%Y-%m-%d %H:%M:%S" > "$_cl/desde"
        return 0
    fi
    echo "✗ No se pudo tomar el cerrojo «$_cl» ni tras recoger uno huérfano."
    return 1
}

cerrojo_soltar() {
    _cl="$1.lock"
    # Solo suelta el suyo: si dentro hay otro PID, es que lo recogió otra ejecución.
    if [ "$(cat "$_cl/pid" 2>/dev/null || echo "")" = "$$" ]; then
        rm -rf "$_cl"
    fi
}
