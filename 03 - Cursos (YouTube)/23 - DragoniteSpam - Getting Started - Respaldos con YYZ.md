# 23 · DragoniteSpam — Copias de seguridad con archivos YYZ

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 11 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=u1pvyG-OSQE> |
| **Duración** | 7 min 3 s |
| **Publicado** | 28 de febrero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | Ninguno |

Capítulo corto pero con una idea de fondo valiosa:

> «Hay otras formas de respaldar un proyecto de GameMaker, y hay formas que
> **probablemente deberías** estar usando. Pero a veces, *keep it simple, stupid* gana a
> todo lo demás. Y soy de los que creen que, aunque no vayas a usar algo, **saber que
> existe, cómo funciona y por qué funciona** sigue siendo conocimiento importante en tu
> arsenal.»

## Índice de contenido

1. Exportar como YYZ
2. Cómo se guarda un proyecto en tu disco
3. Un consejo de configuración de Windows
4. No puedes enviar el `.yyp` suelto
5. Restaurar: doble clic en el YYZ
6. Restaurar: botón Import
7. El YYZ es un ZIP disfrazado
8. El formato ZIP está por todas partes
9. Respaldar a mano también vale
10. Pero la respuesta correcta es el control de versiones

---

## 1. Exportar como YYZ

```
Menú → Export Project → Export as YYZ
```

(La otra opción es *Export as template*, que el autor confiesa no saber para qué sirve en
16 años usando GameMaker.)

Guardas el archivo (`tutorial project random numbers.yyz`) en una carpeta. **Ese es tu
archivo de respaldo.**

---

## 2. Cómo se guarda un proyecto en tu disco

Hasta ahora en la serie se han abierto los proyectos desde el lanzador del IDE. Pero puedes
ver dónde viven:

```
Help → Open Project in Explorer
```

La estructura típica de la carpeta de un proyecto:

| Elemento | Contenido |
|---|---|
| `tutorial project random numbers.yyp` | El archivo principal del proyecto |
| Un archivo de **resource order** | Orden de recursos |
| Carpeta `objects` | Los objetos: código en archivos `.gml` y metadatos en `.yy` |
| Carpeta `sprites` | Lo mismo para los sprites |
| Carpeta `rooms` | Lo mismo para las rooms |

> **Un proyecto de GameMaker está compuesto por muchos archivos.**

---

## 3. Un consejo de configuración de Windows

> Asegúrate de que **«Hide extensions for known file types»** (ocultar extensiones) esté
> **desactivado**.

En Windows 11: Opciones → Ver.

> «Eso hace la vida mucho más fácil en muchísimos aspectos.»

---

## 4. No puedes enviar el `.yyp` suelto

> **No** puedes coger el archivo `.yyp`, mandarlo por correo y esperar que alguien pueda
> abrir tu proyecto.

Para compartir o respaldar el proyecto completo, **exporta a YYZ**.

---

## 5. Restaurar: doble clic en el YYZ

El autor hace la demostración completa:

1. Cierra el proyecto (guardando cambios).
2. **Borra la carpeta del proyecto.**
3. Comprueba que, al cerrar y reabrir GameMaker, el proyecto **ya no está** en la lista de
   recientes.

Para recuperarlo:

> Al instalar GameMaker, **Windows debería asociar la extensión `.yyz`** con el programa.
> Así que basta con hacer **doble clic** en el archivo.

Se abre una ventana nueva de GameMaker con un diálogo de **guardar como**, que extrae el
contenido del proyecto. Y listo: ahí están otra vez el Create y el Step del jugador, y la
carpeta ha reaparecido en el explorador.

---

## 6. Restaurar: botón Import

La otra vía es el botón **Import** de la pantalla de inicio de GameMaker, que te permite
seleccionar el `.yyz` que quieras abrir. Hace exactamente lo mismo: extrae los archivos y
**recrea la estructura del proyecto en el disco**.

---

## 7. El YYZ es un ZIP disfrazado

> **Dato curioso de informática:** el formato YYZ es, en realidad, **un archivo ZIP
> disfrazado**.

Si le cambias la extensión a `.zip` y lo abres, verás el contenido de tu proyecto
comprimido.

No es especialmente importante, pero es cómodo saberlo: es lo que permite asociarlo
directamente con GameMaker.

---

## 8. El formato ZIP está por todas partes

El autor aprovecha para explicar algo más general:

> Es bastante común que **los formatos de archivo de programas concretos sean ZIP
> disfrazados**. Incluso formatos que usas a diario.

Ejemplos que cita:

- `.docx` (Word)
- `.xlsx` (Excel)
- `.pptx` (PowerPoint)

Si sabes lo que haces, puedes extraer un documento de Word como ZIP y ver su contenido:
el texto, las imágenes incrustadas…

---

## 9. Respaldar a mano también vale

> «Y también puedes, perfectamente, hacer clic derecho → Nuevo → Carpeta comprimida,
> llamarla «copia de seguridad del proyecto» y meter el proyecto entero ahí.»

Puedes respaldar un proyecto metiéndolo en un **ZIP**, un **7z** o el formato que prefieras,
y luego extraerlo tú mismo.

(El autor se encuentra con que Windows se queja porque la carpeta `datafiles` está vacía:
no le gusta añadir carpetas vacías a un ZIP.)

---

## 10. Pero la respuesta correcta es el control de versiones

> «Con todo esto dicho, hay otras formas de respaldar tus proyectos de GameMaker —y formas
> que **cabe argumentar que deberías** estar usando—. Y con eso me refiero al **control de
> versiones**.»

Que es el tema del siguiente vídeo de la serie (Git).

---

## Puntos clave

1. **Export Project → Export as YYZ** crea el archivo de respaldo.
2. **Un proyecto es una carpeta con muchos archivos** (`.yyp`, `.yy`, `.gml`…), no un
   archivo único.
3. **No puedes compartir solo el `.yyp`**: hay que exportar a YYZ.
4. Para restaurar: **doble clic en el YYZ** o el botón **Import**.
5. **El YYZ es un ZIP con otra extensión.**
6. Muchos formatos cotidianos (`.docx`, `.xlsx`) también son ZIP disfrazados.
7. Un ZIP a mano también sirve como respaldo.
8. **Desactiva «ocultar extensiones»** en Windows.
9. **El método recomendado a largo plazo es el control de versiones (Git).**

---

## Ejercicio propuesto

> **Objetivo:** comprobar de verdad que tu respaldo funciona. Un respaldo que no has
> restaurado nunca es solo una esperanza.

1. Abre uno de tus proyectos de la serie.
2. Ve a **Help → Open Project in Explorer** y navega por la carpeta. Localiza el `.yyp`, la
   carpeta `objects` y un archivo `.gml`. Ábrelo con un editor de texto: es tu código.
3. Exporta el proyecto con **Export Project → Export as YYZ** a una carpeta de respaldo en
   tu nube.
4. Cierra el proyecto desde GameMaker.
5. **Borra la carpeta del proyecto de tu disco.**
6. Cierra y reabre GameMaker: comprueba que el proyecto ha desaparecido de la lista de
   recientes.
7. **Restaura con doble clic** en el YYZ. Comprueba que se abre el diálogo de extracción y
   que recuperas el proyecto.
8. Abre el Step de tu objeto principal y verifica que **el código está intacto**.

**Parte de experimentación**

9. Borra de nuevo la carpeta del proyecto y esta vez restaura usando el botón **Import**
   de la pantalla de inicio.
10. **Comprueba el dato curioso:** copia el YYZ, cámbiale la extensión a `.zip` y ábrelo.
    Navega por su interior y localiza un archivo `.gml`. Confirma que contiene tu código.
11. Haz lo mismo con un `.docx` de Word que tengas por ahí (cópialo, cámbiale la extensión a
    `.zip` y ábrelo). Busca la carpeta `media` y comprueba que ahí están las imágenes
    incrustadas.

**Reto extra:** crea un respaldo **manual** comprimiendo la carpeta del proyecto con el
explorador de archivos. Después extráelo en otro sitio y abre el proyecto desde ahí con
GameMaker. Compara los dos métodos (YYZ frente a ZIP manual) y anota en cuál confiarías más
para un proyecto de seis meses.
