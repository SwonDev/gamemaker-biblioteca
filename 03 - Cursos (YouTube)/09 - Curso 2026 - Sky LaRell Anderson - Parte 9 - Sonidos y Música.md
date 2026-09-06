# 09 · Crear tus propios sonidos y música

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 9 de 12

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=hAHOQuPwtYY> |
| **Duración** | 40 min 5 s |
| **Publicado** | 29 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `audio_play_sound`, `audio_stop_sound`, `audio_stop_all` |

Capítulo distinto: casi no hay código, pero es **el más importante a nivel legal** de
toda la serie. Trata de **derechos de autor**, de cómo hacer tu propia música aunque
no seas músico, y de cómo meter audio en GameMaker sin que suene 60 veces por segundo.

## Índice de contenido

1. La parte más difícil: la música y el copyright
2. La regla de oro del copyright
3. Las licencias que sí tienes que guardar
4. Haz tu propia música con un ukelele y Audacity
5. Editar y exportar el bucle en Audacity
6. Respaldar los archivos en la nube
7. Música digital: LSDJ y DirtyWave M8
8. Añadir la música a GameMaker
9. Parar y cambiar la música
10. Efectos de sonido: Foley
11. Efectos de sonido: jsfxr
12. Añadir efectos de sonido sin que se disparen 60 veces

---

## 1. La parte más difícil: la música y el copyright

Se puede encontrar música «libre de derechos» en sitios como **Pixabay**
(buscando *copyright free music* en Google). El autor lo demuestra buscando y
escuchando una pista.

Pero hay trampas graves:

- Que algo aparezca en un buscador **no significa** que sea libre de derechos.
- Aunque ponga **«free to use»**, al subirlo a YouTube **te llega un *copyright
  strike***.
- Las políticas suelen prohibir usos «inmorales o ilegales»… y **¿qué es inmoral?**
  Si el contenido de tu juego es arte para ti pero alguien lo considera inmoral, estás
  expuesto.

---

## 2. La regla de oro del copyright

> **Si no hiciste algo tú, no eres el propietario de su copyright.** Aunque el creador
> diga que puedes hacer lo que quieras, **seguirá siendo el titular**.

Es una simplificación, pero es la forma más directa de pensarlo.

Y la consecuencia práctica:

> Si solo estás aprendiendo, usa música descargada sin problema. **Pero en el momento
> en que publiques tu juego —aunque sea gratis— estarás infringiendo la ley**, salvo
> que seas titular del copyright o puedas demostrar que tienes permiso.

---

## 3. Las licencias que sí tienes que guardar

El autor muestra su carpeta de licencias para su juego *Technolonare*. Actualmente
usa **tres**:

| Recurso | Licencia |
|---|---|
| Tipografía Pixel Emulator | Licencia del tipo de letra localizada y archivada |
| Librería **Input** para GameMaker (sistema mejorado de teclado y mando) | Licencia **MIT** (indica titular y permiso) |
| Un filtro visual comprado en **itch.io** | Licencia de uso adquirida |

> Te puedes ahorrar todo esto **si haces tu propia música**, por simple que sea.
>
> «No nos importa que sea simple. **Solo es de aficionado si no encaja con la visión de
> tu juego.**»

---

## 4. Haz tu propia música con un ukelele y Audacity

Material mínimo:

- Un **ukelele barato** (el suyo costó unos 100 €; los hay más baratos) o un **piano
  de juguete**.
- El **smartphone**, con su app de notas de voz.
- **Audacity**: software libre, de código abierto y gratuito.

Proceso:

1. Abre Audacity y configura el **dispositivo de grabación** (tu micrófono) y el de
   **reproducción** (tus auriculares).
2. Acerca el micro al ukelele y **toca**.
3. Busca acordes sencillos en internet.

> **Consejo de diseño:** si tu juego es de acción, evita acordes mayores (suena
> «alegre»). Usa **menores**. Tres menores muy fáciles en ukelele: **Re menor**,
> **La mayor 7** y **Sol menor**.

También puedes grabar directamente con el móvil, enviarte el archivo por correo y
arrastrarlo a Audacity. O usar el micrófono del ordenador.

> El autor recuerda los primeros discos de **The Mountain Goats**, grabados en
> grabadoras de cassette. Incluso tiene una **grabadora de cassette** para dar
> «carácter» al sonido. La baja fidelidad no es un problema: es una elección estética.

---

## 5. Editar y exportar el bucle en Audacity

1. **Recorta** el silencio inicial: deja la pista empezando justo donde arranca la
   música.
2. **Reducción de ruido:** Efectos → *Noise Reduction*. Primero *Get Noise Profile*
   sobre un tramo de silencio, luego aplica el efecto.
3. Averigua **cuánto silencio necesitas al final** para que el bucle encaje. El autor
   lo hace **de oído**: si necesita unos 9/10 de segundo, usa
   **Generar → Silencio** y lo inserta.
4. Selecciona todo: **Tracks → Mix → Render** para aplanar la pista.
5. Pega una copia a continuación y comprueba que el empalme suena bien. Ajusta hasta
   que te convenza.
6. **Efectos:** añade un poco de *reverb* u otros a gusto.
7. **Archivo → Exportar audio** → **MP3** en el escritorio.

> Para aprender Audacity, el autor tiene en su canal *el tutorial de Audacity más
> rápido del mundo*.

---

## 6. Respaldar los archivos en la nube

Igual que con los YYZ:

> **Mueve tus pistas a la nube en cuanto las tengas.** El autor paga un par de euros al
> mes por almacenamiento extra en Google Drive y crea una carpeta específica para cada
> proyecto. Así, si el ordenador se rompe, **no pierdes nada**.

Además, nómbralas **igual que las vas a llamar en GameMaker** (`snd_music`, etc.).

---

## 7. Música digital: LSDJ y DirtyWave M8

### LSDJ (Little Sound DJ)

Es el programa con el que el autor compuso **toda** la música de *Snapshot Spirit
Live!*: un **tracker para Game Boy**. Funciona sobre una Game Boy real o un
emulador.

> Los *chiptunes* suenan bien porque Nintendo no habría lanzado un producto que
> sonara mal. Es un sonido auténtico y con mucha personalidad.

Se controla literalmente con los botones de la Game Boy. Aprenderlo es más sencillo de
lo que parece: hay tutoriales en YouTube.

### DirtyWave M8

Es la evolución: un **instrumento hardware** que expande la idea de LSDJ, con muchos
sonidos ya cargados y pantalla propia. Se puede llevar al parque y componer al lado de
un lago.

El autor lo describe como **hacer música por hoja de cálculo**:

- Una flecha recorre las líneas y reproduce lo que hay en cada una.
- Asignas los sonidos **mediante números**.
- Apilas pistas (melodía, bombo, hi-hat…) y vas añadiendo efectos.

Estructura jerárquica: **Canción → Chain (cadena) → Phrase (frase)**, y dentro de
cada frase eliges instrumento y notas.

> Su música de menú para el proyecto nuevo le llevó **unos 8 minutos**: muy pocas
> notas, un poco de reverb, y algo muy tranquilo. No hace falta más.

---

## 8. Añadir la música a GameMaker

1. Crea el grupo **`Sounds`**.
2. Nomenclatura: como `s` ya es de *sprites*, el autor usa **`snd_`** para sonidos.
3. Crea el recurso **Sound** `snd_music` y carga el archivo.
4. Lanza la música en el **Creation Code de la pantalla de título**:

```gml
audio_play_sound(snd_music, 1, true);
```

| Argumento | Valor | Significado |
|---|---|---|
| sonido | `snd_music` | El recurso de sonido |
| prioridad | `1` | Prioridad si hay demasiados sonidos a la vez |
| bucle | `true` | Que se repita indefinidamente |

> **Sobre la prioridad:** GameMaker no puede reproducir un número ilimitado de sonidos
> simultáneos. Para los juegos que vas a hacer, **pon 1 y no te preocupes**. Solo
> importa en proyectos grandes con muchas pistas a la vez.

---

## 9. Parar y cambiar la música

| Función | Efecto |
|---|---|
| `audio_stop_all()` | Detiene **todos** los sonidos en reproducción |
| `audio_stop_sound(snd_music)` | Detiene **ese** sonido en concreto |

Para cambiar de canción: paras la actual y reproduces la nueva.

> Para descubrir todas las funciones de audio, haz **clic central sobre
> `audio_play_sound`**: el manual te mostrará el resto (pausa, reanudación, etc.).

---

## 10. Efectos de sonido: Foley

**Foley** es crear sonidos en la vida real y capturarlos.

- Abre la app de notas de voz del móvil y **graba**.
- Un disparo puede ser simplemente tu voz haciendo «tss» o «pum».
- ¿Pasos? Ponte el micro junto a los pies y camina. El autor lo hizo así para su juego.
- ¿Puertas? Graba puertas reales.

> En *Snapshot Spirit Live!* (un juego de fotografía), **todos** los sonidos de cámara
> se hicieron poniendo su **cámara analógica de carrete** junto a un micrófono y
> accionándola de distintas formas.

Puedes grabar objetos de tu casa, golpecitos, lo que sea. **Puedes hacerlo tú.**

---

## 11. Efectos de sonido: jsfxr

Para juegos de resolución pequeña hay una herramienta fantástica: **jsfxr**
(búscalo como *8bit sound effects maker*).

Funcionamiento: pulsas cualquiera de los botones generadores y obtienes un efecto
distinto cada vez. Muchos suenan fuerte, así que el autor baja el volumen del
escritorio antes de probarlos.

Cuando encuentres uno que te guste:

1. Ajusta el volumen en la propia herramienta (o luego en Audacity).
2. Descárgalo.
3. **Nómbralo igual que en GameMaker**: `snd_bullet`, `snd_button_hover`,
   `snd_enemy_die`…

> **Nota de formato:** jsfxr exporta **WAV**, que es sin pérdida pero **muy pesado**.
> Lo ideal es abrirlo en Audacity y exportarlo como **MP3**, mucho más ligero.

---

## 12. Añadir efectos de sonido sin que se disparen 60 veces

> **⚠️ El error clásico:** si pones `audio_play_sound()` en un **Step**, se dispara
> **60 veces por segundo**. Da igual que pongas `loop = false`: la función **inicia**
> la reproducción, y la estás llamando en cada fotograma. Suena horrible.

### Disparo de la bala

Ponlo en el **Create** de `oBullet`, porque la bala se crea una sola vez:

```gml
// Create event de oBullet
audio_play_sound(snd_bullet, 1, false);
```

> «Esta es una forma de asegurarte de que solo se dispara una vez: añadirlo al Create
> de algo que estás creando.»

### Sonido al pasar el ratón por un botón

Aquí hace falta un truco, porque el Step sí se ejecuta constantemente. Usa el propio
estado para que solo suene en la **transición**:

```gml
if (!hover)                                   // Si ANTES no estábamos encima…
{
    audio_play_sound(snd_button_hover, 1, false);
    hover = true;                             // …y ahora sí lo estamos
}
```

Como dentro del bloque se pone `hover = true`, en los fotogramas siguientes la
condición `!hover` ya es falsa y **no vuelve a sonar**.

(Podrías escribir `if (hover == false)`, pero `!hover` es más corto y rápido.)

### Sonido al hacer clic

Aquí es seguro, porque **`mouse_check_button_pressed()` solo es verdadero durante un
fotograma**:

```gml
if (mouse_check_button_pressed(mb_any))
{
    audio_play_sound(snd_button_click, 1, false);
    // …
}
```

### Sonido al morir el enemigo

También es seguro, porque **justo después se destruye el objeto**:

```gml
if (hp <= 0)
{
    audio_play_sound(snd_enemy_die, 1, false);
    instance_destroy();   // El código ya no existirá para volver a ejecutarse
}
```

---

## Puntos clave

1. **Si no lo hiciste tú, no eres el dueño del copyright.** Publicar —aunque sea gratis—
   con música ajena es ilegal sin permiso.
2. **«Free to use» no protege de un *copyright strike*** en YouTube.
3. **Guarda las licencias** de todo lo que no hayas creado (fuentes, librerías,
   filtros comprados…).
4. **Haz tu propia música.** Un ukelele de 100 €, el móvil y Audacity bastan.
5. **Acordes menores para acción**, mayores para alegría.
6. **Respaldar el audio en la nube**, igual que los YYZ.
7. **LSDJ (Game Boy) y DirtyWave M8** son instrumentos *tracker* accesibles y muy
   personales.
8. **`audio_play_sound(sonido, prioridad, bucle)`**; prioridad `1` basta para empezar.
9. **`audio_stop_all()`** y **`audio_stop_sound()`** para detener.
10. **Nunca pongas `audio_play_sound()` en un Step** sin control: suena 60 veces por
    segundo.
11. **Soluciones seguras:** Create de un objeto recién creado, transición de estado
    (`if (!hover)`), funciones `_pressed` (un solo fotograma) o código seguido de
    `instance_destroy()`.
12. **WAV pesa mucho**: convierte a MP3 con Audacity.

---

## Ejercicio propuesto

> **Objetivo:** dotar al juego de música y efectos propios, respetando las licencias y
> sin disparos repetidos de audio.

**Parte A — Legal**

1. Haz una lista de **todos** los recursos de tu proyecto que no has creado tú
   (fuentes, librerías, música, arte).
2. Para cada uno, localiza su **licencia** y guárdala en una carpeta `licencias/` dentro
   de tu carpeta de proyecto en la nube.
3. Escribe un archivo `CREDITOS.md` con el nombre del recurso, su autor, la licencia y
   de dónde lo sacaste. Es un hábito profesional y te evitará problemas.

**Parte B — Música propia**

4. Graba 30-60 segundos de algo: ukelele, piano de juguete, palmadas, silbidos, o
   simplemente golpes sobre la mesa con ritmo.
5. Ábrelo en Audacity: recorta el inicio, aplica reducción de ruido y añade el silencio
   final necesario para que **encaje en bucle**.
6. Aplana con **Tracks → Mix → Render**, pega una copia detrás y comprueba el empalme.
7. Añade un efecto (reverb) y **exporta a MP3** como `snd_music`.
8. Súbelo a tu carpeta de Google Drive.

**Parte C — Integrar la música**

9. Crea el grupo `Sounds` y el recurso `snd_music`.
10. Lanza la música desde el Creation Code de `rTitle` con
    `audio_play_sound(snd_music, 1, true);`.
11. Añade temporalmente `audio_stop_sound(snd_music);` al clic de un botón para
    comprobar que funciona, y quítalo después.

**Parte D — Efectos de sonido**

12. Genera 4 efectos en **jsfxr**: `snd_bullet`, `snd_button_hover`,
    `snd_button_click` y `snd_enemy_die`. Nómbralos así en tu disco.
13. Añade `snd_bullet` al **Create** de `oBullet`.
14. Implementa el sonido de *hover* con el truco `if (!hover)` en el botón.
15. Añade el sonido de clic dentro del `mouse_check_button_pressed()`.
16. Añade el sonido de muerte del enemigo justo antes de `instance_destroy()`.

**Reto extra (el más instructivo):** mueve a propósito la línea
`audio_play_sound(snd_bullet, 1, false);` al **Step** de `oBullet` y dispara una vez.
Escucha el resultado y explica por qué ocurre, aunque `loop` sea `false`. Después
devuélvela al Create.
