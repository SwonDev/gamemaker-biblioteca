# 12 · Primer contacto: las decisiones al empezar (apuntes 2025-2026)

> Apuntes propios del vídeo **«Getting Started with GameMaker (2025/2026)»** de **DragoniteSpam**
> (30 de octubre de 2025, 22:35), con la transcripción en español. No es el recorrido de menús
> —eso está en [11 · El IDE, recorrido guiado](./11%20-%20El%20IDE%20de%20GameMaker%20en%20español%20-%20recorrido%20guiado.md)—
> sino las **decisiones** que un principiante toma nada más abrir GameMaker, con datos al día.
>
> Fuente: <https://www.youtube.com/watch?v=bX3uF7oDDA4>

---

## 1 · ¿Qué versión instalo? (esto es lo que más confunde)

El vídeo lo cuenta desde el momento exacto del cambio de ciclo, y sigue vigente:

- **La versión "actual" (no-LTS)** cuando se grabó era **GameMaker 2024.14** — sí, la
  numeración es rara, «es una larga historia».
- **LTS 2026 salió en enero de 2026.** Es la versión **estable que no cambia durante años y con
  pocos fallos**. Es la que usa esta biblioteca como referencia: **IDE 2026.0.0.16 · runtime
  2026.0.0.23**.

**Regla práctica del vídeo, ajustada a hoy:** si empiezas ahora, usa **LTS 2026**. Cuando se
grabó, la LTS vigente tenía ~3 años y le faltaban funciones, y por eso él no la recomendaba
*entonces*; pero LTS 2026 ya está fuera y **es la opción estable recomendada**.

- GameMaker es **gratis de usar**. Solo pagas a YoYo Games si **vendes** tu juego.
- Está en la web (gamemaker.io → descargas) y en Steam (mismo producto).
- Corre en Windows, macOS y Linux (Linux oficialmente solo Ubuntu; otras distros «a veces
  funciona, a veces explota»).

> 💡 **Requisitos reales:** GameMaker es ligero (no es Unity ni Unreal; se parece a Godot o RPG
> Maker en consumo). Cualquier CPU de doble núcleo, sin tarjeta gráfica dedicada, con gráficos
> integrados. Un SSD solo acelera el arranque.

---

## 2 · La plantilla que evita el error nº 1 del principiante

Al crear proyecto nuevo → tipo **juego** (no «fondo de pantalla animado» ni «tira de juego»,
que son cosas de Opera). Hay dos plantillas de juego en blanco, y **la elección importa**:

| Plantilla | Cuándo |
|---|---|
| Juego en blanco (normal) | Arte de alta resolución, no pixel art |
| **Juego de pixel art en blanco** | **El 90 % de los casos** — pixel art nítido |

> 🔺 **El error más común, en palabras del propio vídeo:** la gente aparece en el subreddit, el
> Discord y el foro «quejándose de que su pixel art se ve horrible y no saben por qué». La causa
> es una configuración de **escalado de gráficos** que estropea el pixel art, y que la plantilla
> normal deja mal por defecto. **Usa la plantilla de pixel art** y te ahorras el dolor de cabeza.
> Se puede cambiar dentro del proyecto en cualquier momento, pero es mejor empezar bien.

---

## 3 · ¿GML o «visual»? — GML, sin miedo

Al crear el proyecto eliges lenguaje. La recomendación es clara:

- **GML (código).** El scripting visual de GameMaker «no es muy bueno» y no se recomienda para
  el día a día.
- **GML se parece a JavaScript.** Si no lo conoces, no pasa nada.
- «Animo a la gente a no tener miedo al código; no es terriblemente difícil.»

> 💡 Esta biblioteca refuerza lo mismo: todo el material, las recetas y los scripts están en
> **GML**. El visual (Drag & Drop) solo aparece para traducir a código, no como destino.

---

## 4 · ¿Hace falta iniciar sesión? — Casi nunca

Puedes iniciar sesión con una cuenta de **Opera** (la empresa dueña de GameMaker) o una cuenta
antigua de GameMaker. Pero:

- **Usas ~95 % del motor sin iniciar sesión.**
- El login **solo importa al distribuir** tu juego (exportar a otras plataformas, móvil,
  consolas con cuenta de desarrollador).
- Toda la serie del vídeo se hace **sin login**.

**Plataformas de destino** (botón de destino): por defecto siempre hay **`gx.games`** (juego
web, «como los antiguos flash») y **`test`** (la plataforma del sistema en el que estás:
Windows, macOS o Linux). Iniciar sesión desbloquea las demás.

---

## 5 · Lo primero que creas: sprite → objeto → room

El vídeo monta el mínimo, y el orden mental es el que conviene recordar:

1. **Sprite** = el recurso gráfico. Se dibuja en el editor (o se importa con «Import»). Puede
   tener **varias subimágenes** (para animación).
2. **Objeto** = la entidad que *hace cosas y a la que le pasan cosas* (el jugador, por ejemplo).
   Se le **asigna un sprite** arrastrándolo al cuadro de sprite del editor de objetos.
3. **Room** = el nivel; el espacio físico/visual donde todo existe mientras el juego corre. Un
   proyecto nuevo trae solo `rm_room1`.

**Los tres recursos que importan al empezar son esos: rooms, objetos y sprites.** Fuentes,
scripts y shaders llegan después.

> 🔺 **Convención de nombres** (no obligatoria, pero universal): `obj_player`, `spr_player`,
> `rm_nivel1`. Prefijo de tipo + nombre. Hay variantes (mayúsculas en vez de `_`, prefijo de una
> letra), pero la de tres letras con guion bajo es la más común. Coincide con la que usa esta
> biblioteca y el [CLAUDE.md del proyecto](../CLAUDE.md).
>
> 💡 **Organiza con grupos** (carpetas del navegador de recursos) en cuanto tengas varios
> recursos: clic derecho → crear grupo, y arrastras dentro.

---

## 6 · Atajo que vas a usar mil veces

- **F5 = ejecutar el juego.** «Se convertirá en tu mejor amigo»; te cansarás de mover el ratón
  al botón de play. Los cuatro botones de esa zona: depurar, ejecutar, detener, y limpiar la
  caché del compilador.
- La **pestaña de salida (Output)** es donde aparecen los mensajes al ejecutar; los **errores de
  compilación** tienen su propia pestaña.
- La **pegatina de versión** (arriba a la derecha) te dice qué IDE y qué runtime usas — útil para
  saber si tu versión coincide con la de un tutorial.

---

## Ver también

- [11 · El IDE, recorrido guiado](./11%20-%20El%20IDE%20de%20GameMaker%20en%20español%20-%20recorrido%20guiado.md) — el recorrido detallado de menús y editores
- [01 · El IDE y el flujo de trabajo](../01%20-%20Fundamentos/01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md) — los fundamentos del entorno
- [00 · Anatomía de un juego completo](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md) — el siguiente paso: montar un juego entero
- [Resumen LTS 2026.0](../02%20-%20Novedades%202026/01%20-%20Resumen%20LTS%202026.0.md) — qué trae la versión que instalas
