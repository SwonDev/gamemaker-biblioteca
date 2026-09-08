#!/usr/bin/env bash
# Reconstruye las dos partes que el repositorio publica SIN contenido porque no son
# propias (ver PUBLICAR.md): el espejo del manual oficial (09) y el código de
# terceros descargado (11). Sin esto, `buscar.py` funciona pero dos de sus cuatro
# fuentes están vacías.
#
#   ./reconstruir.sh            explica las opciones y cuánto ocupa cada una
#   ./reconstruir.sh manual     descarga el manual oficial de manual.gamemaker.io
#   ./reconstruir.sh codigo     clona los repositorios de terceros catalogados
#
# Cualquier argumento extra se pasa tal cual al script de Python correspondiente
# (por ejemplo `./reconstruir.sh codigo --limite 3 --destino /ruta/de/prueba`, que es
# como se prueba esto sin descargar el corpus entero).
#
# Ninguna de las dos operaciones toca nada que ya exista en el disco: ambas son
# reanudables (si algo ya está descargado, se salta) y piden confirmación antes de
# empezar porque hablan con servidores de terceros y pueden tardar bastante.
set -euo pipefail

# El instalador oficial de python.org para Windows registra `python.exe`, NO
# `python3.exe` (ese alias es convención de macOS/Linux; solo la app de Microsoft
# Store trae ambos) — mismo criterio que usa instalar.sh.
elegir_python() {
  if command -v python3 >/dev/null 2>&1; then
    echo python3
    return 0
  fi
  if command -v python >/dev/null 2>&1 \
      && python -c 'import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)' 2>/dev/null; then
    echo python
    return 0
  fi
  return 1
}

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IND="$RAIZ/_indice/reconstruccion"
MODO="${1:-}"
[ $# -gt 0 ] && shift

confirmar() {
  # Pide una confirmación explícita por stdin. En un script o pipe no interactivo,
  # `read` devuelve vacío al instante y esto cancela — hay que pasar la respuesta
  # por stdin a propósito (p. ej. `echo s | ./reconstruir.sh codigo`), nunca se
  # asume un «sí» por defecto.
  read -r -p "$1 [s/N] " respuesta || true
  case "$respuesta" in
    [sS] | [sS][iI]) return 0 ;;
    *)
      echo "Cancelado."
      exit 1
      ;;
  esac
}

ayuda() {
  cat <<'FIN'
Reconstruye lo que el .gitignore deja fuera de este repositorio porque no es trabajo
propio (el detalle está en PUBLICAR.md):

  ./reconstruir.sh manual
      Descarga el manual oficial de GameMaker (manual.gamemaker.io, rama LTS) y lo
      convierte a Markdown en «09 - Manual oficial/», con la misma estructura de
      carpetas que ya espera buscar.py. Reanudable: si una página ya existe en disco,
      no se vuelve a descargar, así que se puede cortar e ir retomando.

      Tamaño y tiempo: ≈6 150 páginas entre los dos idiomas (inglés + español). Con el
      límite de cortesía del servidor (4 peticiones a la vez, con reintento si
      responde 429) puede llevar bien más de una hora la primera vez. El conversor
      HTML→Markdown es una reimplementación (el original que generó el espejo ya
      publicado no está en este repositorio, se perdió) — sigue el mismo criterio
      documentado en «09 - Manual oficial/README.md» y se ha probado contra páginas
      reales, pero no reproduce el espejo carácter a carácter. Detalle y limitaciones
      exactas en la cabecera de `_indice/reconstruccion/descargar_manual.py`.

      Si además quieres el mismo nivel de traducción al español que ya tiene esta
      biblioteca (401 páginas que YoYo Games no había traducido), ejecuta después:
        python3 "_indice/traduccion/tm.py" aplicar ""
      Reutiliza la memoria de traducción ya publicada (`_indice/traduccion/tm_es.json`
      y compañía): no hace falta traducir nada de nuevo.

  ./reconstruir.sh codigo
      Clona con `git clone --depth 1` los repositorios de terceros catalogados en
      «11 - Código descargado/_RUTAS.json» (608 en total). Reanudable igual que arriba
      — si una carpeta ya tiene contenido, se salta; si un clon falla, se informa y se
      sigue con los demás, sin abortar el resto.

      Tamaño: ≈3,8 GB en disco, varios cientos de peticiones a GitHub.

      SIEMPRE quedan fuera, sin flag para activarlos: Pizza Tower, Deltarune, AM2R,
      Hotline Miami, Kirby, y cualquier otro repositorio de la categoría «juegos y
      motores» que no tenga una licencia libre reconocida (MIT, GPL, BSD, Apache…) en
      el catálogo — son 13 de los 608. Para ver la lista exacta y por qué, sin clonar
      nada en absoluto:
        python3 "_indice/reconstruccion/clonar_codigo.py" --listar-excluidos

      Cada uno de los 595 restantes conserva su propia licencia (está en su carpeta):
      esto es material de consulta y aprendizaje, no una autorización para reutilizar
      el código de otro en un proyecto tuyo — léela antes de copiar nada entero.

Prueba rápida sin descargar todo (a cualquiera de los dos se le puede pasar --limite
y --destino, que van derechos al script de Python):
  ./reconstruir.sh codigo --limite 3 --destino /tmp/prueba
FIN
}

case "$MODO" in
  "")
    ayuda
    ;;
  -h | --help | help)
    ayuda
    ;;
  manual | codigo)
    PY="$(elegir_python || true)"
    if [ -z "$PY" ]; then
      echo "✗ Hace falta python3 para reconstruir esto (en Windows, si «python3» no se"
      echo "  encuentra, prueba con el instalador de python.org o la app de Microsoft Store,"
      echo "  que sí registra python3). Instálalo y vuelve a intentarlo."
      exit 1
    fi

    if [ "$MODO" = manual ]; then
      echo "Vas a descargar el manual oficial de GameMaker desde manual.gamemaker.io."
      echo "≈6 150 páginas (inglés + español) · calcula bien más de una hora la primera vez."
      echo "Reanudable: lo que ya esté descargado (aquí, o de un intento anterior) se salta."
      confirmar "¿Continuar?"
      exec "$PY" "$IND/descargar_manual.py" "$@"
    else
      echo "Vas a clonar con git los repositorios de terceros catalogados en _RUTAS.json."
      echo "≈3,8 GB en disco · 608 repositorios, 13 excluidos siempre (juegos comerciales"
      echo "o sin licencia libre en la categoría «juegos y motores» — ver PUBLICAR.md)."
      echo "Reanudable: lo que ya esté clonado se salta; un fallo puntual no aborta el resto."
      confirmar "¿Continuar?"
      exec "$PY" "$IND/clonar_codigo.py" "$@"
    fi
    ;;
  *)
    echo "✗ Opción desconocida: $MODO"
    echo
    ayuda
    exit 2
    ;;
esac
