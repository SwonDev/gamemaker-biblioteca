# Herramienta de traducción del manual

Este directorio contiene las herramientas con las que se ha **completado en español el manual
oficial de GameMaker**. Hoy no queda ni una página en inglés dentro de
`09 - Manual oficial/manual-lts-2026-es/`.

Funciona como una **memoria de traducción** (el mismo método que usan las herramientas TAO
profesionales): segmenta cada página en unidades traducibles —párrafos, celdas de tabla,
encabezados, elementos de lista—, busca cada unidad en la memoria y reconstruye la página en
español. **El código, los enlaces y los nombres de función no se tocan nunca.**

La regla dura: **una página solo se escribe cuando *todas* sus unidades están traducidas.**
Por eso nunca aparece una página a medias.

## Los tres huecos que había, y las tres herramientas

| Hueco | Alcance | Herramienta |
|---|---:|---|
| Páginas enteras en inglés | 401 páginas | `tm.py` + `tm_es.json` |
| Tablas de argumentos en inglés dentro de páginas «traducidas» por YoYo | 3 181 celdas en 1 468 páginas | `celdas.py` + `celdas_es.json` |
| Etiquetas de enlace y cabeceras de tabla en inglés | 167 apariciones en 113 páginas | `etiquetas.py` |

## Uso

```sh
cd "_indice/traduccion"

# --- 1. Páginas enteras -------------------------------------------------
python3 cola_traduccion.py estado           # ¿cuántas páginas quedan?
python3 tm.py faltan "Debugging" 100        # ¿qué unidades faltan?
python3 anadir_tm.py <<'JSON'               # añadir a la memoria
{ "This function returns the width.": "Esta función devuelve el ancho." }
JSON
python3 tm.py aplicar ""                    # escribir las páginas completas

# --- 2. Celdas de tablas de argumentos ----------------------------------
python3 celdas.py estado                    # ¿cuántas celdas quedan?
python3 celdas.py extraer                   # → celdas_faltan.json
python3 anadir_celdas.py <<'JSON'
{ "The index of the grid.": "El índice de la rejilla." }
JSON
python3 celdas.py aplicar                   # sustituirlas en el espejo

# --- 3. Etiquetas de enlace y cabeceras ---------------------------------
python3 etiquetas.py estado
python3 etiquetas.py aplicar
```

## Estado

| Dato | Valor |
|---|---:|
| Páginas que YoYo Games dejó sin traducir | 431 |
| Traducidas por esta biblioteca | **401** |
| **Pendientes** | **0** ✅ |
| Unidades de prosa en `tm_es.json` | **4 503** |
| Celdas de tabla en `celdas_es.json` | **2 009** |
| Etiquetas y cabeceras en `etiquetas.py` | 55 + 9 |

Las páginas traducidas llevan la marca `<!-- traducido-por-la-biblioteca -->` en la primera
línea y una nota al pie. La versión inglesa completa sigue disponible en
`manual-lts-2026-en/` para contrastar.

> En los mensajes de Feather los títulos de regla se dejan **bilingües** a propósito
> (`GM1000 - No enclosing loop from which to break. (No hay ningún bucle del que salir)`),
> porque el IDE los muestra en inglés y hay que poder buscarlos tal cual.

## Si YoYo Games publica páginas nuevas

El flujo es reanudable: se vuelve a espejar el manual, se lanza `cola_traduccion.py estado` y
solo hay que traducir las unidades que aún no estén en la memoria. Todo lo demás se
reconstruye solo.

## Archivos

| Archivo | Qué es |
|---|---|
| `tm.py` | Motor de prosa: segmentación, memoria, reconstrucción |
| `tm_es.json` | Memoria de traducción de prosa (inglés → español) |
| `cola_traduccion.py` · `cola_traduccion.json` | Gestión de qué páginas quedan |
| `anadir_tm.py` | Añade pares a `tm_es.json` |
| `celdas.py` | Traduce solo las celdas de tabla en inglés, sin tocar la prosa oficial |
| `celdas_es.json` · `celdas_faltan.json` | Memoria y cola de celdas |
| `anadir_celdas.py` | Añade pares a `celdas_es.json` |
| `etiquetas.py` | Etiquetas de enlace y cabeceras de tabla (memoria incrustada) |
