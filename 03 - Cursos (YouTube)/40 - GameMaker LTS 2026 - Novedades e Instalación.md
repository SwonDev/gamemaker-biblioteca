# 40 · GameMaker LTS 2026 ya está aquí

> **Fuente:** DragoniteSpam (vídeo de novedades)
> **Publicado:** 21 de mayo de 2026

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=HWbph_xyP2g> |
| **Duración** | 16 min 33 s |
| **Publicado** | 21 de mayo de 2026 |
| **Nivel** | Todos |
| **Motor** | GameMaker LTS 2026 |

Contexto imprescindible: **GameMaker LTS 2026 se publicó el 21 de mayo de 2026**. Es la
versión estable actual y la que se usa en todo este curso.

## Índice de contenido

1. Qué es una versión LTS
2. LTS 2026 como encrucijada: el final de una era
3. Descargar e instalar
4. La versión de Steam
5. No sobrescribe tus instalaciones anteriores
6. Importar las preferencias
7. El fallo de la importación y cómo solucionarlo a mano
8. Abrir un proyecto y el consejo de oro
9. La situación de las licencias
10. GMRT: expectativas realistas

---

## 1. Qué es una versión LTS

**LTS** puede significar *long-term stable* o *long-term support*, según a quién preguntes.

Es una versión de GameMaker que:

- Debería estar **razonablemente libre de errores**.
- No debería tener **caídas raras ni comportamientos inesperados**.
- **No cambia**, salvo actualizaciones periódicas de especificaciones de consola.

> El precedente fue **LTS 2022**, pensada para proyectos largos o comerciales en los que no
> quieres que aparezcan errores nuevos cada vez que GameMaker se actualiza.

LTS 2026 es lo mismo, **pero con algo más**:

> Ha habido **cambios estructurales internos** en el funcionamiento de GameMaker, que
> deberían permitir que las versiones futuras se construyan sobre esta base **sin grandes
> disrupciones**.

---

## 2. LTS 2026 como encrucijada: el final de una era

Para quien lleve tiempo en esto, GameMaker ya ha vivido varias transiciones:

- GameMaker **7 → 8**.
- GameMaker **8 → HTML5** (que nadie usó; en la práctica, 8 → Studio 1).
- GameMaker **Studio 1 → Studio 2**.

> **Esta es la siguiente de esas transiciones.**

GameMaker LTS 2026 es **la versión final del runtime actual**. Puedes pensarla como:

> **La última actualización de GameMaker Studio 2.**

(El autor bromea con Russell: «ya sé que ya no se llama GameMaker Studio 2. Sonríe y
asiente».)

Después de esta versión, **casi todo el esfuerzo de desarrollo pasará a GMRT**, el *futuro
runtime* de GameMaker, que es básicamente **una reescritura completa desde cero**.

---

## 3. Descargar e instalar

Desde la página de descarga puedes bajar LTS 2026 para **Windows**, **Mac** o **Linux**.

> **La versión de Linux aparece marcada como *beta*.** El autor lo explica sin rodeos: es la
> **misma versión del software**, no te falta ninguna función ni corrección, pero YoYo Games
> no quiere comprometerse a que esté tan libre de errores como las de Windows y Mac.

La instalación:

- Descarga el instalador.
- Acéptalo y sigue los pasos.
- **No sobrescribe** ninguna versión anterior: se instala **como un programa completamente
  aparte**.

---

## 4. La versión de Steam

Si usas GameMaker a través de Steam, **también puedes acceder a LTS 2026**:

1. Propiedades del software en Steam.
2. **Game versions and betas**.
3. En lugar de la versión pública por defecto (2024.14), selecciona **LTS 2026** como versión
   beta.

> No es una página de producto separada. Y por el mismo sistema puedes volver a **LTS 22** o
> a versiones anteriores si lo necesitas.

---

## 5. No sobrescribe tus instalaciones anteriores

Al ser una instalación nueva:

- **Tus proyectos recientes no aparecerán.**
- **No estarás con la sesión iniciada**: tendrás que volver a entrar con tu cuenta de
  GameMaker o de Opera.
- **Todas tus preferencias se habrán borrado.**

---

## 6. Importar las preferencias

Configurar las preferencias una a una es inviable: hay muchísimas.

Solución:

1. Abre los ajustes y baja hasta **Import preferences**.
2. Se abre un buscador de archivos.
3. Selecciona **`local_settings.json`**.
   - Si **has iniciado sesión**, la carpeta que se abre por defecto es la de tu usuario en la
     versión *monthly*.
   - Si **no** has iniciado sesión, irá a la carpeta de usuario desconocido
     (`unknown_user_…`).
4. Confirma la importación.

El autor comprueba que, por ejemplo, **sus rutas de GameMaker** (que tiene en un disco
aparte) se han restaurado correctamente.

En ese archivo también viajan ajustes como:

- GMRT settings.
- Code Editor 2 (CE2).
- Feather.
- Mensajes personalizados.

---

## 7. El fallo de la importación y cómo solucionarlo a mano

> **«Un minuto después de terminar de grabar empecé a ver informes de que NO se importan
> todas las preferencias.»**

Cosas como **la lista de proyectos recientes** y otros ajustes varios **no se importan** con
el botón.

### Solución manual

Copia a mano **todo el contenido de la carpeta de usuario**, no solo el
`local_settings.json`.

En **Windows**:

1. Activa la visualización de archivos ocultos (en Windows 11: pestaña *View → Hidden
   items*).
2. Ve a: `C:\Users\<tu usuario>\AppData\Roaming\GameMakerStudio2\<tu_carpeta_de_usuario>\`
3. Selecciona **todo** y cópialo.
4. Ve a: `C:\Users\<tu usuario>\AppData\Roaming\GameMakerStudio2-LTS2026\`
5. Sustituye el contenido.

> Tarda un rato: hay muchos archivos (layouts de proyectos, etc.). Después reinicia el IDE de
> LTS y recuperarás **no solo los ajustes, sino también los proyectos recientes**.

**Truco:** puedes copiar la ruta directamente desde la barra de direcciones del explorador.

En **Mac y Linux** el autor no sabe la ruta exacta de memoria, pero indica el criterio:

> Es **la carpeta que se abre al pulsar *Import preferences***. Navega hasta ella y copia su
> contenido.

---

## 8. Abrir un proyecto y el consejo de oro

Al abrir un proyecto existente, el autor da un consejo que conecta directamente con el
capítulo 24:

> **Si no has hecho un commit en tu control de versiones, deberías plantearte hacerlo antes
> de actualizar.**

No espera que nada explote al pasar a LTS… salvo que vengas de una versión muy antigua. Pero:

> **Haz un commit para tener un punto fácil al que volver** si algo sale mal.

---

## 9. La situación de las licencias

Punto que ha generado confusión, y el autor lo aclara:

> **Tu licencia actual de GameMaker te sirve para LTS 2026 «hasta el final de los tiempos».**

Salvo que algo cambie mucho, **LTS 2026 será la versión que puedes —y probablemente deberías—
usar durante bastante tiempo**.

### Cuándo cambiará

Cuando salga **GMRT**, el nuevo runtime, **la situación de las licencias cambiará**: tendrás
que **comprar una licencia nueva**.

El autor prevé drama en la comunidad, porque la situación de las licencias de GameMaker ha
sido «bastante caótica en los últimos cinco años». Su consejo: **no te agobies**.

Y recuerda la regla general:

> **Puedes usar GameMaker gratis hasta que intentes ganar dinero con tu juego.** Si haces un
> juego gratuito o una demo gratuita antes de la versión comercial, puedes seguir usándolo
> sin licencia. Solo al vender necesitas una.

---

## 10. GMRT: expectativas realistas

Sobre cuándo llegará GMRT, el autor es escéptico con cariño:

> «YoYo Games dice que GMRT estará listo en cosa de un año, pero sinceramente… ¿cuándo fue
> la última vez que YoYo Games cumplió una fecha? **No cuento con que GMRT sea usable en
> producción hasta dentro de dos o tres años.**»

Y lo justifica:

> LTS 2026 ya se retrasó **como un año**, y muchas otras funciones también se han retrasado
> mucho. «Empezaré a creerme el calendario de vuestra hoja de ruta cuando empecéis a cumplir
> las fechas.»

---

## Puntos clave

1. **LTS 2026 se publicó el 21 de mayo de 2026** y es la versión estable actual.
2. **LTS** = versión estable y sin cambios, pensada para proyectos largos.
3. **LTS 2026 es la última versión del runtime actual**: el final de la era GameMaker Studio 2.
4. El futuro es **GMRT**, una reescritura completa desde cero.
5. Está disponible para **Windows, Mac y Linux** (esta última marcada como beta, pero con las
   mismas funciones).
6. **Se instala como programa aparte**: no sobrescribe versiones anteriores.
7. Al ser instalación nueva: **sin proyectos recientes, sin sesión y sin preferencias**.
8. Usa **Import preferences → `local_settings.json`** para recuperar los ajustes.
9. **El botón no lo importa todo**: para los proyectos recientes hay que copiar a mano la
   carpeta de usuario (`AppData\Roaming\GameMakerStudio2`, con archivos ocultos visibles).
10. **Haz un commit antes de actualizar.**
11. **Tu licencia actual sirve para LTS 2026 indefinidamente.**
12. **GameMaker es gratis hasta que vendas tu juego.**

---

## Ejercicio propuesto

> **Objetivo:** migrar tu entorno a LTS 2026 correctamente y sin perder nada.

1. Comprueba qué versión de GameMaker tienes instalada ahora (IDE y runtime).
2. **Antes de tocar nada:** haz un **commit** de tu proyecto en Git (capítulo 24). Verifica en
   el historial que está ahí.
3. Descarga e instala **LTS 2026**. Comprueba que se instala **como programa separado** y que
   tus versiones anteriores siguen presentes.
4. Abre LTS 2026, inicia sesión y abre los ajustes.
5. Pulsa **Import preferences** y selecciona tu `local_settings.json`.
6. Comprueba que tus ajustes principales (rutas, editor, Feather) se han restaurado.

**Parte de verificación (la importante)**

7. Comprueba si tu **lista de proyectos recientes** se ha importado. Si no es así (es el
   fallo que documenta el autor), cópiala a mano siguiendo los pasos del apartado 7:
   activa los archivos ocultos, ve a `AppData\Roaming\GameMakerStudio2`, copia **todo** tu
   contenido de usuario y pégalo en la carpeta de LTS.
8. Reinicia el IDE y verifica que ahora **sí** aparecen los proyectos recientes.
9. Abre tu proyecto y ejecútalo. Si algo falla, **vuelve al commit** que hiciste en el paso 2.

**Reto extra:** el autor se muestra escéptico con los plazos de GMRT. Investiga en el blog
oficial de GameMaker el estado actual de GMRT y responde por escrito: ¿qué es exactamente, en
qué se diferenciará del runtime actual, y qué implicaría migrar un proyecto? Así tendrás
criterio propio en lugar de depender de lo que se comenta en foros.
