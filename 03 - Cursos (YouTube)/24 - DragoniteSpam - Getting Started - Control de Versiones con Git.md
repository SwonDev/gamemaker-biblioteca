# 24 · DragoniteSpam — Control de versiones con Git

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 12 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=ctOwfkrtZPc> |
| **Duración** | 20 min 2 s |
| **Publicado** | 28 de febrero de 2026 |
| **Nivel** | Principiante |
| **Herramientas** | Git, GitHub Desktop |
| **Código GML** | Ninguno |

El capítulo más importante de toda la serie a efectos prácticos:

> «Si planeas trabajar en tu juego **más de unos quince minutos**, deberías estar haciendo
> esto.»

## Índice de contenido

1. Por qué el YYZ no basta
2. El error clásico: guardar el proyecto en Dropbox o OneDrive
3. Ignora las funciones de control de versiones del IDE
4. Qué es Git (y de dónde viene el nombre)
5. Git frente a GitHub
6. Un apunte sobre Microsoft
7. GitHub Desktop: configuración inicial
8. Crear un repositorio
9. Guardar el proyecto dentro del repositorio
10. Hacer el primer *commit*
11. Cada cuánto hacer *commits*
12. Leer el historial
13. Revertir un *commit*
14. Descartar cambios sin *commit*
15. Recuperar un recurso borrado
16. Control de versiones como seguro

---

## 1. Por qué el YYZ no basta

El sistema de importar/exportar de GameMaker «está bien si tienes prisa o si quieres
mandarle el proyecto a alguien por Google Drive», pero:

> **No es una solución práctica ni viable a largo plazo para las copias de seguridad.**

---

## 2. El error clásico: guardar el proyecto en Dropbox o OneDrive

Mucha gente lo ha intentado a lo largo de los años, y **se rompe por motivos
complicados**:

> Si el sistema intenta **sincronizar** los archivos de la carpeta compartida **al mismo
> tiempo** que GameMaker intenta acceder a ellos, **las cosas se rompen** de formas que
> preferirías evitar.

No guardes tu proyecto dentro de OneDrive, Dropbox ni Google Drive sincronizado.

---

## 3. Ignora las funciones de control de versiones del IDE

En la barra de menús del IDE verás una pestaña **Source Control**.

> **Vamos a ignorarla por completo.**

GameMaker tiene algunas funciones «parecidas al control de versiones», pero:

> «No son muy buenas. **Ojalá no estuvieran ahí.** Creo que causan más confusión de la que
> ayudan.»

Todo el vídeo usa una **herramienta externa**.

---

## 4. Qué es Git (y de dónde viene el nombre)

Existen varios sistemas de control de versiones. **Git es, con diferencia, el más común**
para usar con GameMaker.

> **Dato curioso:** Git **no** es la abreviatura de nada. Es un término anticuado del inglés
> británico para referirse a una persona desagradable. **Su creador, Linus Torvalds, lo
> llamó así por sí mismo.**

Git existe como **herramienta de línea de comandos**, pero en este vídeo **no** se usa
así: se usa un **cliente gráfico**.

---

## 5. Git frente a GitHub

- **Git** es el sistema de control de versiones.
- **GitHub** es **una ubicación centralizada online** donde guardar repositorios Git.

> **No tienes por qué usar GitHub para usar Git.** Hay otras opciones (Bitbucket, por
> ejemplo). A menudo van de la mano, pero no es obligatorio.

---

## 6. Un apunte sobre Microsoft

El autor lo menciona con franqueza:

- La **web** de GitHub es propiedad de Microsoft.
- El **software** GitHub Desktop está desarrollado por Microsoft.
- Microsoft «está en una especie de misión para hacerse enemigo de todo el mundo lo más
  rápido posible».

> Si no quieres tratar con Microsoft, **hay alternativas** tanto a GitHub como a GitHub
> Desktop, con más o menos las mismas funciones.

Él usa GitHub Desktop porque es el más común y el que conoce, y prefiere hablar de algo
familiar «sin sorpresas».

---

## 7. GitHub Desktop: configuración inicial

1. Descarga el instalador desde su página.
2. Al abrirlo, te pedirá **iniciar sesión en github.com**. Puedes **saltarte el paso**.
3. Te pedirá nombre y correo: esa información se adjunta a los **mensajes de commit**.
   (No hace falta poner datos reales.)

---

## 8. Crear un repositorio

GitHub Desktop ofrece tres opciones:

| Opción | Para qué |
|---|---|
| **Clone a repository** | Descargar un proyecto existente de internet |
| **Add an existing repository** | Si ya tienes un repositorio Git en tu disco |
| **Create a new repository on your local drive** | La que normalmente querrás |

Al crearlo puedes añadir:

- Nombre y descripción.
- Un archivo **README**.
- Un **.gitignore**: un archivo de texto que le dice a Git **qué archivos NO mirar**.
- Una **licencia**, importante si vas a compartir el código: dice a la gente qué puede y qué
  no puede hacer legalmente con él.

El autor solo le da nombre y pulsa **Create repository**.

> **Nota:** al abrirlo, GitHub Desktop sale en **modo claro**, que según el autor «se ve
> mal». Se cambia en **Appearance → Dark**.

---

## 9. Guardar el proyecto dentro del repositorio

1. Vuelve a la pantalla de inicio de GameMaker y crea un proyecto nuevo.
2. **En lugar de la ubicación por defecto**, elige la carpeta del repositorio
   (normalmente en `Mis documentos → GitHub → <nombre del repositorio>`).

Al volver a GitHub Desktop verás que **han aparecido cambios**: los archivos recién
añadidos.

---

## 10. Hacer el primer *commit*

> Un **commit** se puede entender como **un punto de guardado** de un juego, o un **punto de
> restauración del sistema**.

Por tradición, el autor hace un commit nada más crear un proyecto, como punto de partida.

1. Escribe una descripción: `initialized project`.
2. Pulsa **Commit X files to main**.
3. La lista de cambios desaparece.
4. En la pestaña **History** ya ves el commit.

---

## 11. Cada cuánto hacer *commits*

> «Cada cuánto deberías hacer un commit es un tema que la humanidad debate probablemente
> desde antes de inventar la rueda.»

| Extremo | Valoración del autor |
|---|---|
| Un commit **por cada línea** cambiada | «Un poco excesivo» |
| Un commit **solo al terminar el día** | «También un poco excesivo» |

Su criterio personal:

> Hago un commit cuando **termino una cosa atómica**: si he añadido el movimiento del
> jugador, o el paso entre rooms, o un NPC aunque no cambie mucho código pero sí añada
> sprites.

La regla de oro:

> Los commits deben ser **lo bastante pequeños** para que puedas encontrar el cambio que
> buscas, pero **lo bastante grandes** para no tener que recorrer un millón de líneas en el
> historial.

---

## 12. Leer el historial

El autor hace una demostración: crea un sprite, un objeto con movimiento básico y lo mete
en la room. GitHub Desktop lista **todos los cambios**:

- La creación del sprite (dos entradas, porque el sistema de sprites de GameMaker es «un
  poco complicado por motivos»).
- El **código del Step** en el archivo `.gml`.
- El código de la **room**, que ahora tiene una instancia.

Hace un commit: `added a player`. Ya hay dos commits en el historial.

---

## 13. Revertir un *commit*

Ahora el autor **invierta los controles** a propósito y hace un commit:
`made the player controls fun`.

Para deshacerlo:

1. Recorre el **historial de commits** y busca el cambio sospechoso.
2. Puedes **deshacerlo a mano** en el código.
3. O puedes **revert changes in this commit**: crea **un commit nuevo que hace exactamente
   lo contrario** del anterior.

### Cómo leer un diff

| Color | Significado |
|---|---|
| **Rojo** | Líneas **eliminadas** |
| **Verde** | Líneas **añadidas** |
| Rojo y verde en la misma línea | La línea **cambió**; se resalta la diferencia |

Después, GameMaker avisa de que **el directorio del proyecto ha sido modificado**, porque
GitHub Desktop ha cambiado archivos en el disco. Pulsa **Reload**.

Al ejecutar, los controles vuelven a funcionar bien.

---

## 14. Descartar cambios sin *commit*

Si has hecho cambios **sin commitear**, Git los reconoce y te los muestra.

Para deshacerlos:

1. Selecciona el cambio (o varios).
2. Pulsa **Discard changes**.

Esto elimina los cambios **antes** de que lleguen a formar parte de un commit.

---

## 15. Recuperar un recurso borrado

Este es el caso más valioso.

> Si borras un asset en GameMaker, te avisa de que es importante y te pregunta si estás
> seguro. Si lo haces igualmente, **el archivo se borra permanentemente y no hay forma de
> recuperarlo**.

De vez en cuando alguien pregunta por qué GameMaker no tiene una **papelera de reciclaje**
integrada. La respuesta del autor:

> «No voy a decir que sea la idea más estúpida del mundo… pero **el fondo de la cuestión es
> que deberías estar usando control de versiones**. El control de versiones resuelve ese
> problema por ti.»

Cómo recuperarlo:

1. Borra el sprite.
2. GitHub Desktop mostrará los archivos cambiados; los **eliminados** llevan un **signo
   menos rojo**.
3. Selecciónalos y pulsa **Discard changes** (o revierte el commit donde ocurrió).
4. GameMaker te preguntará si quieres recargar: pulsa **Reload**.

Y el sprite vuelve.

> Nota: si haces un cambio grande (añadir o borrar archivos) con GameMaker abierto, a veces
> recargará el proyecto entero.

---

## 16. Control de versiones como seguro

> «Una de las muchísimas cosas buenas del control de versiones es que es, básicamente,
> **un seguro**. Es una forma de protegerte de cometer errores así. **Y no tienen por qué ser
> errores tuyos.**»

El autor pone el ejemplo extremo:

> Si **se va la luz** mientras trabajas, pierdes un cambio y tu proyecto se corrompe, con
> control de versiones **hay una forma fácil de recuperar tu trabajo**. Sin él… buena suerte.

Y aclara que no es un escenario hiperbólico:

> «Cada dos o tres semanas alguien aparece en el subreddit o en el Discord contando que le
> ha pasado exactamente eso y preguntando si hay forma de recuperar su trabajo.»

---

## Puntos clave

1. **El YYZ sirve para compartir, no como respaldo a largo plazo.**
2. **Nunca guardes el proyecto en una carpeta sincronizada** (OneDrive, Dropbox): se
   corrompe.
3. **Ignora la pestaña Source Control de GameMaker**: usa una herramienta externa.
4. **Git** es el sistema; **GitHub** es un alojamiento online. Puedes usar Git sin GitHub.
5. **Crea el repositorio y guarda el proyecto DENTRO de su carpeta.**
6. Un **commit** es un punto de guardado al que puedes volver.
7. **Haz commits por «cosas atómicas»** terminadas, ni por línea ni solo al final del día.
8. **Rojo = eliminado, verde = añadido** en los diffs.
9. **Revert** crea un commit que deshace otro; **Discard** elimina cambios sin commitear.
10. **Pulsa Reload en GameMaker** cuando Git cambie archivos en el disco.
11. **Puedes recuperar assets borrados** con control de versiones.
12. **Es un seguro**: te protege de errores tuyos y de desastres del sistema.

---

## Ejercicio propuesto

> **Objetivo:** montar control de versiones en tu proyecto y, sobre todo, **practicar la
> recuperación antes de necesitarla**.

**Parte A — Montaje**

1. Instala **GitHub Desktop** (o el cliente gráfico que prefieras). Puedes saltarte el
   inicio de sesión.
2. Ponlo en **modo oscuro** desde *Appearance*.
3. Crea un repositorio llamado `mi-primer-juego`.
4. Crea un proyecto de GameMaker **guardándolo dentro de la carpeta del repositorio**.
5. Haz el primer commit con el mensaje `initialized project`.

**Parte B — El hábito**

6. Crea un sprite, un objeto con movimiento y colócalo en la room.
7. Haz un commit: `added a player`.
8. Añade una segunda mecánica (por ejemplo disparar). Haz otro commit.
9. Repasa tu historial: ¿podrías localizar en cuál de los commits introdujiste cada cosa?
    Si no, tus commits son demasiado grandes.

**Parte C — Recuperar (lo importante)**

10. **Rompe algo a propósito:** invierte los controles y haz un commit que diga
    `cambio experimental`.
11. Comprueba el fallo en el juego, ve al historial, localiza el commit y **revíertelo**.
12. Pulsa **Reload** en GameMaker cuando te lo pida y verifica que funciona.

**Parte D — Recuperar un borrado**

13. Borra un sprite. Confirma el aviso de GameMaker.
14. Ve a GitHub Desktop, localiza los archivos con el **signo menos rojo** y pulsa
    **Discard changes**.
15. Recarga en GameMaker y comprueba que el sprite ha vuelto.

**Reto extra:** busca en internet un archivo **`.gitignore` para GameMaker** y añádelo a tu
repositorio. Explica qué carpetas o archivos exclusiones y por qué conviene que Git no los
vigile (pista: piensa en las cachés de compilación).
