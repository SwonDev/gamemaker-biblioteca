# 01 · El espacio de trabajo

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 1 de 12

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=iETcg9lcOXs> |
| **Duración** | 20 min 12 s |
| **Publicado** | 21 de enero de 2026 |
| **Nivel** | Principiante absoluto |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | Ninguno (capítulo de orientación) |

## Índice de contenido

1. Antes de empezar: el ratón de tres botones
2. Crear el proyecto y la convención de nombres
3. Anatomía del espacio de trabajo
4. La biblioteca de recursos y los grupos
5. La barra de herramientas superior
6. Ejecutar, depurar y crear el ejecutable
7. Opciones de juego: el ajuste que arregla el pixel art
8. Navegación: rueda del ratón y clic central
9. Copias de seguridad con archivos YYZ
10. Restaurar un proyecto desde un YYZ

---

## 1. Antes de empezar: el ratón de tres botones

El autor es el Dr. Skyler Lel Anderson, profesor de artes mediáticas digitales y
diseño de juegos en la Universidad de St. Thomas, en St. Paul (Minesota). La serie
enseña los **fundamentos** de GameMaker: desde unas pocas formas que se mueven hasta
exportar y publicar el juego. La idea no es que al terminar seas experto, sino que
tengas la base suficiente para seguir aprendiendo por tu cuenta y hacer el juego que
tú quieras.

La primera recomendación, antes de tocar el motor, es de **hardware**:

> Consigue un ratón de tres botones. Es barato y vas a usarlo constantemente.

Un ratón de tres botones significa:

- **Clic izquierdo** y **clic derecho**.
- **Rueda de scroll** que además **se puede pulsar** como si fuera un tercer botón.

Casi cualquier ratón con rueda de scroll sirve, porque la rueda suele ser
pulsable. El autor insiste en que sea **con cable en vez de inalámbrico**: el
inalámbrico altera la aceleración y la sensibilidad del puntero, y eso se nota
mucho cuando haces pixel art y necesitas mover el cursor con precisión milimétrica.
Además, los ratones con cable son más baratos.

### Si usas un portátil con trackpad

Puedes seguir el curso igual, pero hay un detalle importante: al abrir GameMaker en
un portátil verás, cerca de la parte superior, una pequeña opción destacada llamada
**Laptop Mode** (modo portátil). **Debes desactivarla**, porque interfiere con los
atajos de ratón que se usan en el curso.

En un trackpad tendrás que averiguar por tu cuenta cómo emitir clic izquierdo, clic
derecho y clic de rueda (normalmente combinando `Opción` o `Control` con el clic).
Funciona, pero no es cómodo. De verdad: usa un ratón.

---

## 2. Crear el proyecto y la convención de nombres

Descarga e instala la versión más reciente de GameMaker. Al abrirlo, cierra
cualquier asistente o tutorial emergente que aparezca y pulsa:

```
New Project → Game → Blank Game
```

Ahora viene una de las enseñanzas más prácticas del capítulo: **la convención de
nombres del proyecto**.

El autor la exige a sus alumnos y la recomienda encarecidamente a todo el mundo:

```
<NombreCorto> <AAMMDD> <Vn>
```

Por ejemplo:

```
GM Tutorial 260114 V1
```

Desglosado:

| Parte | Significado | Ejemplo |
|---|---|---|
| `GM Tutorial` | Nombre corto del proyecto | `GM Tutorial` |
| `26` | Año (dos dígitos) | 2026 |
| `01` | Mes | enero |
| `14` | Día | 14 |
| `V1` | Número de versión de ese día | `V1`, `V2`, `V3`… |

### ¿Por qué este formato?

Porque cuando tengas una carpeta llena de copias de seguridad de un mes entero de
trabajo, **se ordenarán automáticamente de más antigua a más reciente** de forma
alfabética. Como vas de año → mes → día, basta con desplazarte al final de la lista
para encontrar siempre la versión más reciente. Y funciona incluso si el proyecto
dura más de un año.

El sufijo `V1` cubre el caso de que hagas **varias copias el mismo día**: si guardas
otra versión por la tarde, la llamas `V2`, y así sucesivamente.

Después de nombrarlo, pulsa **Let's Go**.

---

## 3. Anatomía del espacio de trabajo

Al entrar verás cuatro zonas principales:

```
┌──────────────┬──────────────────────────┬───────────────┐
│  Biblioteca  │                          │               │
│  de recursos │      ESPACIO DE          │   Inspector   │
│  (assets)    │      TRABAJO             │ (propiedades) │
│              │                          │               │
├──────────────┴──────────────────────────┴───────────────┤
│  Salida / mensajes / errores                            │
└─────────────────────────────────────────────────────────┘
```

- **Espacio de trabajo (centro):** donde programas y trabajas en el juego.
- **Inspector (derecha):** muestra las propiedades de lo que tengas seleccionado.
- **Biblioteca de recursos (izquierda):** donde gestionas todo lo que creas.
- **Salida (abajo):** mensajes, errores y avisos de GameMaker.

### Paneles redimensionables y plegables

Todos los paneles se pueden:

- **Redimensionar** arrastrando sus bordes.
- **Minimizar** con una pequeña barra cliqueable que aparece al arrastrarlos al
  extremo.

El autor recomienda usar un **monitor grande** si tienes acceso a uno, porque es
muy útil tener abiertos a la vez la biblioteca de recursos, el inspector y el
espacio de trabajo.

### F11 y F12

- **`F11` / `F12`:** minimizan todos los paneles de golpe.
- Volver a pulsar **`F12`** los restaura.

> Si alguna vez pulsas `F12` por accidente y desaparece todo, no has perdido
> nada. Vuelve a pulsar `F12` o abre los paneles manualmente.

### Pestañas de espacio de trabajo

El espacio de trabajo funciona **como un navegador web**, con pestañas. Puedes
tener una pestaña para una parte del juego y otra para otra. Para renombrarlas:

- **Clic derecho → Rename**, o
- selecciona la pestaña y pulsa **`F2`**.

El autor, en la práctica, prefiere trabajar con una sola pestaña.

---

## 4. La biblioteca de recursos y los grupos

Al empezar solo tienes un recurso creado automáticamente: **`Room1`**.

En GameMaker, una **room** (habitación) es un espacio o nivel del juego. Es el
nombre que usa el motor para lo que en otros sitios llamarías escena o nivel.

### La regla de oro de la organización

> Todo recurso debe pertenecer a un **grupo**. Nada suelto.

Un grupo es básicamente una carpeta. Se crea con **clic derecho en la biblioteca →
Create Group**. Por ejemplo, creas un grupo `Rooms` y arrastras `Room1` dentro. Así
puedes abrirlo cuando lo necesites y ocultarlo cuando no.

Los grupos:

- Aceptan **cualquier tipo de recurso**: sonidos, arte, scripts, fuentes…
- Pueden contener **subgrupos** (carpetas dentro de carpetas).
- Debes crear un grupo **por cada tipo de recurso** que uses.

Un ejemplo de jerarquía:

```
Rooms/
├── Menus/          ← pantallas de menú, pausa, inicio
│   ├── rm_start
│   └── rm_pause
└── Levels/         ← niveles jugables
    └── rm_level1
```

Adquiere el hábito desde el principio: gestionar bien los recursos te ahorrará
muchísimo tiempo cuando el proyecto crezca.

### Otras herramientas de la biblioteca

- **Barra de búsqueda:** imprescindible cuando tengas muchos recursos.
- **Borrar:** clic derecho → Delete, o simplemente selecciona y pulsa la tecla
  `Supr`.
- **Renombrar:** clic derecho → Rename, o `F2`.
- **Quick Access:** el autor lo minimiza porque no lo usa; es un panel de accesos
  rápidos.

### El inspector

Al seleccionar `Room1`, el inspector muestra sus propiedades. El inspector cambia
según lo que tengas seleccionado: es el panel donde ajustarás casi todo en
GameMaker.

---

## 5. La barra de herramientas superior

De izquierda a derecha, los controles importantes:

### Zoom

Tres iconos de lupa: **alejar**, **acercar** y **restablecer zoom**.

> Acostúmbrate al botón de **restablecer zoom**. Cuando te pierdas o la vista se
> vuelva confusa, púlsalo y todo volverá a su sitio.

### Colapsar paneles

El botón equivalente a `F12`, para plegar o desplegar los paneles acoplados.

### Help (ayuda)

La documentación de GameMaker es **extraordinariamente buena** y deberías
acostumbrarte a usarla. Al pulsarla se abre en tu navegador (la primera vez te
pedirá descargarla; acepta).

El truco más útil: **cualquier texto de color dentro de GameMaker se puede pulsar
con el botón central del ratón** para abrir directamente la ayuda de esa función.
Es la forma más rápida de consultar el manual.

### Clean

Limpia la caché de compilación. No te preocupes por él de momento.

### Run y Stop

- **Run:** compila y ejecuta el juego para probarlo.
- **Stop:** lo detiene.

Si ejecutas ahora con solo `Room1`, verás una ventana en negro: es tu juego, vacío.

### Debug

Si pulsas **Debug** por error, se abre una versión del juego con el depurador y un
montón de información de rendimiento. No pasa nada: ciérralo con **Stop**.

### Create Executable / Create Executable and Launch

Sirven para generar una **aplicación** de tu juego, la que subirías a itch.io o a
Steam. Durante el desarrollo usarás casi siempre **Run**.

### Selector de plataforma

Junto a los botones anteriores verás la plataforma de destino (**Windows**, **Mac**
…). Si no has iniciado sesión aparecerá como `Test`. Al crear una cuenta de
GameMaker tendrás acceso a más plataformas; por ejemplo, el autor usa **HTML5**
para hacer juegos de navegador.

### Guardar, abrir, nuevo, inicio

- **Save Project (`Ctrl + S`):** acostúmbrate a guardar. Además, GameMaker guarda
  automáticamente cada vez que ejecutas el juego.
- **Open Project:** abre otros proyectos.
- **New Project:** crea uno nuevo.
- **Home:** cierra el proyecto y vuelve a la pantalla de inicio, donde verás tus
  **proyectos recientes** para reabrirlos con un clic.

Todo esto también está en el menú **File**.

---

## 6. Opciones de juego: el ajuste que arregla el pixel art

**Game Options** afecta al comportamiento real del juego. Aquí está el ajuste que el
autor menciona como fuente habitual de problemas:

```
Game Options → Windows → Graphics → ☐ Interpolate colors between pixels
```

Esta opción **difumina los colores entre píxeles**. Es útil en juegos de alta
resolución, pero **estropea el pixel art**, porque hace que los sprites se vean
borrosos.

> Siempre que algo se vea borroso, ve a
> **Game Options → Windows → Graphics** y **desmarca** «Interpolate colors between
> pixels». Pulsa **Apply** y **OK**.

Desde este mismo sitio puedes configurar el título de la ventana, los gráficos y
las analíticas para la exportación a HTML5.

---

## 7. Navegación: rueda del ratón y clic central

- **Rueda del ratón:** desplaza el espacio de trabajo hacia arriba y abajo.
- **Clic central (pulsar la rueda) y arrastrar:** mueve libremente la vista,
  estés donde estés.

Este gesto de **clic central + arrastre** funciona también en otras ventanas de
GameMaker, y es la forma cómoda de moverte cuando tienes mucho contenido en pantalla.

---

## 8. Copias de seguridad con archivos YYZ

Esta es la parte más importante del capítulo.

> El autor ha visto a innumerables alumnos con un proyecto roto y sin forma de
> recuperarlo. Cuando les pregunta por la última copia de seguridad, resulta que
> fue hace varios días, tras trabajar cinco horas diarias desde entonces.

### El hábito

> Cada vez que te levantes del ordenador —vayas a comer o termines el día— haz una
> copia de seguridad.

### Guardar no es lo mismo que respaldar

Guardar el proyecto (`Ctrl + S`) crea una carpeta con todos los recursos: muchos
archivos y subcarpetas en tu disco. Es válido para trabajar en local, pero no sirve
como copia de seguridad portable.

Para respaldar:

```
File → Export Project → YYZ
```

Un archivo **YYZ** es un único fichero comprimido con **todo** el proyecto: arte,
sonidos, código, todo.

### Diferencia entre YYP y YYZ

| Extensión | Qué es | Para qué sirve |
|---|---|---|
| **.yyp** | Archivo de proyecto sin exportar | Trabajar en tu máquina |
| **.yyz** | Proyecto exportado y comprimido | **Respaldar y transportar** |

### Dónde guardarlo

**No** lo guardes en la carpeta de proyectos. Guárdalo en:

- El escritorio, y de ahí arrástralo a la nube, o
- directamente en **Google Drive, OneDrive, iCloud o Dropbox**.

Los YYZ **no ocupan apenas nada** (no son como los vídeos). Desde cualquier
ordenador con GameMaker instalado puedes descargar el archivo de la nube y seguir
trabajando.

### Beneficio extra: limpiar el proyecto

Exportar a YYZ y volver a importarlo **limpia la memoria y la caché** del
proyecto. Si un sprite se ve con fallos gráficos o algo funciona mal sin motivo,
exporta y reimporta: es una forma infalible de limpiar la compilación. (También
puedes hacerlo desde el menú **Build**, pero el YYZ es más fiable.)

---

## 9. Restaurar un proyecto desde un YYZ

El proceso completo de recuperación:

1. Descarga el `.yyz` de tu servicio en la nube.
2. **Haz doble clic** en el archivo: se abre GameMaker y lo importa.
3. Te pedirá dónde guardar la versión local del proyecto.
   - Si el día es el mismo, **cambia el número de versión** (por ejemplo `V2`),
     porque si repites `V1` intentará guardar en la carpeta que ya existe.
4. Pulsa **Save**.

El proyecto se importa con **toda** su configuración intacta: los grupos que
creaste, y ajustes como el de interpolación de píxeles, que seguirá desmarcado.

---

## Puntos clave

1. **Usa un ratón de tres botones con cable.** El clic central se usa
   constantemente, y el cable mejora la precisión del puntero.
2. **En un portátil, desactiva Laptop Mode** o los atajos no funcionarán.
3. **Nombra los proyectos como `Nombre AAMMDD Vn`.** Se ordenan solos de antiguo a
   reciente y funcionan más allá de un año.
4. **Cada recurso vive dentro de un grupo.** Crea un grupo por tipo y usa
   subgrupos; es el hábito que sostiene proyectos grandes.
5. **`F12`** pliega y despliega los paneles; **`F2`** renombra lo seleccionado.
6. **Restablece el zoom** cuando te pierdas.
7. **Clic central sobre cualquier texto de color** abre la ayuda de esa función. La
   documentación de GameMaker es de primera categoría: úsala.
8. **Desmarca «Interpolate colors between pixels»** si haces pixel art y lo ves
   borroso.
9. **Clic central + arrastrar** para desplazarte por cualquier ventana.
10. **Respaldar con `File → Export Project → YYZ` al terminar cada sesión** es el
    hábito más importante de todo el curso. Guárdalo en la nube, no en la carpeta
    de proyectos.

---

## Ejercicio propuesto

> **Objetivo:** interiorizar la convención de nombres y el ciclo de respaldo antes
> de escribir una sola línea de código.

1. Crea un proyecto en blanco llamado `Practica Espacio <AAMMDD de hoy> V1`.
2. Crea esta estructura de grupos en la biblioteca de recursos:

   ```
   Sprites/
   Objects/
   Rooms/
   Sounds/
   Fonts/
   Scripts/
   ```

   Dentro de `Rooms`, crea dos subgrupos: `Menus` y `Niveles`. Mueve `Room1` a
   `Niveles` y renómbralo a `rm_nivel1` con `F2`.

3. Entra en **Game Options → Windows → Graphics** y desmarca *Interpolate colors
   between pixels*. Aplica los cambios.
4. Pulsa **Run** y comprueba que se abre una ventana vacía. Ciérrala con **Stop**.
5. Practica la navegación: usa la rueda para desplazarte y **clic central +
   arrastre** para mover la vista. Prueba `F12` para plegar los paneles y volver a
   restaurarlos.
6. Practica la ayuda: pulsa con el **botón central** sobre cualquier función o
   texto de color que veas en el inspector y observa cómo se abre el manual en el
   navegador.
7. **Exporta el proyecto a YYZ** en tu carpeta de Google Drive (o el servicio que
   uses), con el mismo nombre que el proyecto.
8. Cierra GameMaker, borra el proyecto de la lista de recientes, y **vuelve a
   importarlo haciendo doble clic en el YYZ**, guardándolo como `V2`.

Comprueba al final que el grupo `Niveles` sigue existiendo, que la room se llama
`rm_nivel1` y que la opción de interpolación sigue desmarcada. Si es así, ya
dominas el único hábito que te salvará de perder semanas de trabajo.
