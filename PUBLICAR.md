# Publicar esta biblioteca

## Qué se publica y qué no

| Parte | ¿Va al repositorio? | Por qué |
|---|---|---|
| Documentación propia (`01`-`08`, `10`, `12`, `13`) | ✅ Sí | Trabajo propio · CC BY-SA 4.0 |
| Herramientas (`_indice/`, `instalar.sh`) | ✅ Sí | Trabajo propio · MIT |
| La skill (`_indice/skills/`) | ✅ Sí | Es el entregable |
| `09 - Manual oficial/` (30 MB) | ❌ No | Copyright de YoYo Games |
| `11 - Código descargado/` (3,8 GB) | ❌ No | 608 licencias ajenas + juegos comerciales |
| `Lumbre/`, `GameMaker_Fuentes/` | ❌ No | Personal y almacén crudo |

Total publicable: **363 archivos · 14 MB**. Está todo en el `.gitignore`.

## Lo que le pasa a quien clone el repositorio

Al ejecutar `./instalar.sh`, `actualizar.py` deriva `simbolos.json` del `GmlSpec.xml` **del
runtime que esa persona tenga instalado**. Eso no es un apaño: es lo que garantiza que la
biblioteca no le mienta sobre una versión que no es la suya.

Lo que **no** tendrá, y hay que decírselo en el README con todas las letras:

- **El espejo del manual.** `buscar.py` sigue dando la firma exacta de cada símbolo (sale del
  runtime, no del manual), pero la ficha remitirá a `manual.gamemaker.io` en vez de a un archivo
  local. `gm-cli manual read "<tema>"` cubre el hueco sin conexión.
- **El corpus de código real.** Las búsquedas `--codigo` no devolverán nada.

## Pendiente antes de publicar

1. **Script de reconstrucción** que descargue el manual y clone los repositorios en la máquina de
   quien clona. No está escrito. Las piezas para el manual están en `_indice/traduccion/`; las
   URLs de los 608 repositorios, en `11 - Código descargado/_RUTAS.json` (que **sí** conviene
   publicar aunque el código no: son solo nombres y rutas). Comprobar antes si `_RUTAS.json`
   guarda la URL de origen o solo la ruta local; si es lo segundo, hay que recuperarla del
   `_CATALOGO.md`.
2. **README de portada.** El `README.md` actual es el índice interno de la biblioteca y presupone
   que ya la tienes. Para GitHub hace falta una portada que empiece por qué problema resuelve
   (que un agente de IA no invente funciones de GML), cómo se instala en una línea, y qué NO
   incluye.
3. **Decidir el nombre del repositorio** y si es público desde el primer commit.
4. **Confirmación del autor** antes de `git remote add` y `git push`. No se ha creado nada en
   GitHub todavía.
