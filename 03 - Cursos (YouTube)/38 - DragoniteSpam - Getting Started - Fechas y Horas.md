# 38 · DragoniteSpam — Fechas y horas

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 26 de 26 de la playlist oficial · **FIN DE LA SERIE**

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=VD2EnEOUCCo> |
| **Duración** | 30 min 27 s |
| **Publicado** | 22 de agosto de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `current_*`, `current_time`, `get_timer()`, `date_create_datetime()`, `date_current_datetime()`, `date_get_*()`, `date_inc_*()`, `date_*_span()`, `date_datetime_string()`, `date_compare_datetime()`, `date_is_today()`, `date_leap_year()` |

Capítulo final de la serie. Un tema que «no es vital para hacer juegos», pero que conviene
conocer, sobre todo en juegos con **elementos en tiempo real**.

## Índice de contenido

1. Las variables `current_*`
2. Índices: el mes empieza en 1, el día de la semana en 0
3. `current_time`: milisegundos desde el arranque
4. `date_create_datetime()`
5. `date_current_datetime()`
6. `date_get_*()`: extraer datos
7. `date_inc_*()`: avanzar el tiempo
8. `date_*_span()`: cuánto tiempo ha pasado
9. Comparar fechas
10. Formatear para el jugador (localización)
11. `date_valid_datetime()`
12. Zonas horarias
13. `get_timer()` y para qué sirve de verdad
14. Funciones curiosas: `date_is_today()` y `date_leap_year()`
15. Atajo de teclado útil

---

## 1. Las variables `current_*`

GameMaker trae un conjunto de variables integradas **globales** con la hora actual del
sistema del usuario:

| Variable | Contenido |
|---|---|
| `current_second` | Segundo actual |
| `current_minute` | Minuto actual |
| `current_hour` | Hora actual, en formato **24 horas** |
| `current_day` | Día del mes |
| `current_month` | Mes |
| `current_year` | Año |
| `current_weekday` | Día de la semana |

```gml
draw_text(32, 32,  current_second);
draw_text(32, 64,  current_minute);
draw_text(32, 96,  current_hour);
draw_text(32, 128, current_day);
draw_text(32, 160, current_month);
draw_text(32, 192, current_year);
draw_text(32, 224, current_weekday);
```

> **Son de solo lectura**: no puedes «fijar» el mes ni nada parecido.

Son útiles, por ejemplo, para **guardar la fecha y hora del último guardado** del jugador.

---

## 2. Índices: el mes empieza en 1, el día de la semana en 0

Dos convenciones distintas que conviene recordar:

| Valor | Empieza en | Ejemplo |
|---|---|---|
| **`current_weekday`** | **0** | Domingo = 0, lunes = 1, martes = 2, miércoles = 3… |
| **`current_month`** | **1** | Enero = 1, agosto = 8… |

> El autor reconoce que no le suelen gustar los índices basados en 1 frente a los basados
> en 0, **pero en el mes le parece bien**: cuando escribes una fecha, no cuentas los meses
> desde cero.

---

## 3. `current_time`: milisegundos desde el arranque

> **No** tiene que ver con la hora del reloj: representa **los milisegundos transcurridos
> desde que el juego empezó**.

Si el juego lleva 5 minutos: 300 segundos = **300.000 milisegundos**.

---

## 4. `date_create_datetime()`

```gml
date_create_datetime(year, month, day, hour, minute, second);
```

Devuelve una **marca de tiempo única** a partir de los datos que le des.

```gml
var _timestamp = date_create_datetime(2026, 8, 5, 15, 9, 30);
```

### Qué contiene realmente

> Es un número que representa **los días transcurridos desde (parece ser) el 1 de enero de
> 1899** como parte entera, y **la fracción del día transcurrida** como parte decimal.

El autor lo encuentra «un formato de fecha algo raro» y cree que es el que usan **los
programas de hojas de cálculo**, que a veces necesitan fechas anteriores al 1 de enero de
1970.

### Verlo en pantalla

Si lo dibujas tal cual, verás algo como `46240,63`. Para ver cómo avanza en tiempo real,
rellénalo con las variables `current_*`:

```gml
var _timestamp = date_create_datetime(current_year, current_month, current_day,
                                      current_hour, current_minute, current_second);
```

> **⚠️ Truco importante:** al convertir un número a cadena, GameMaker lo **trunca a dos
> decimales**. Para ver más precisión usa **`string_format()`**:
>
> ```gml
> draw_text(32, 32, string_format(_timestamp, 1, 6));
> ```

---

## 5. `date_current_datetime()`

Es la función hermana: hace lo mismo pero **con la fecha y hora actuales**, sin que le
pases nada.

```gml
var _now = date_current_datetime();
```

---

## 6. `date_get_*()`: extraer datos

Para sacar información de una marca de tiempo:

```gml
date_get_year(timestamp);
date_get_month(timestamp);
date_get_day(timestamp);
date_get_hour(timestamp);
date_get_minute(timestamp);
date_get_second(timestamp);
```

> El autor avisa: **no** llames a tu variable `current_hour`, porque es un nombre reservado.
> Usa algo como `now_hour`.

Puedes ir en los dos sentidos: crear marcas de tiempo a partir de datos, y extraer datos de
una marca de tiempo.

---

## 7. `date_inc_*()`: avanzar el tiempo

```gml
date_inc_day(timestamp, cantidad);
date_inc_month(timestamp, cantidad);
date_inc_year(timestamp, cantidad);
date_inc_week(timestamp, cantidad);
date_inc_minute(timestamp, cantidad);
date_inc_hour(timestamp, cantidad);
date_inc_second(timestamp, cantidad);
```

> **No modifican la marca original**: **devuelven una nueva**.

```gml
var _original = date_create_datetime(2020, 1, 23, 12, 0, 0);
var _avanzada = date_inc_day(_original, 5);   // 5 días después
```

Con 15 días sobre el 23 de enero de 2020 llegas al **7 de febrero**.

---

## 8. `date_*_span()`: cuánto tiempo ha pasado

```gml
date_year_span(t1, t2);
date_month_span(t1, t2);
date_week_span(t1, t2);
date_day_span(t1, t2);
date_hour_span(t1, t2);
date_minute_span(t1, t2);
date_second_span(t1, t2);
```

> **Queja del autor:** todas las demás funciones siguen el patrón `date_operacion_unidad`
> (`date_inc_day`, `date_get_hour`…), pero estas **lo invierten**: `date_day_span` en vez de
> `date_span_day`. A él le gustaría que fuera al revés. Lo tiene apuntado para sugerirlo.

Ejemplo: entre principios de 2020 y mediados de 2026 hay **2.386 días** y más de tres
millones y medio de minutos.

---

## 9. Comparar fechas

```gml
date_compare_datetime(t1, t2);
date_compare_date(t1, t2);
date_compare_time(t1, t2);
```

Devuelven:

| Resultado | Significado |
|---|---|
| **−1** | La primera fecha es **anterior** |
| **0** | Son **iguales** |
| **+1** | La primera fecha es **posterior** |

Útil, por ejemplo, para comparar **dos partidas guardadas** y saber cuál es la más antigua.

> El autor se equivoca al predecir el signo en directo y lo corrige: es un buen recordatorio
> de que **hay que leer la documentación** en vez de suponer.

---

## 10. Formatear para el jugador (localización)

```gml
date_datetime_string(timestamp);
```

Convierte una marca de tiempo en algo legible:

```
8/5/2026 at 3:25:59.60 PM
```

> **Lo mejor: localiza la hora.** Si tu región usa **día/mes/año** en lugar de
> **mes/día/año**, se reflejará automáticamente.

La función básicamente le pregunta al sistema operativo por su función de localización de
hora.

> Es ideal para mostrar al jugador **la fecha y hora de su última partida guardada** sin
> tener que preocuparte del formato local.

También existen:

- **`date_date_string()`** — solo la fecha.
- **`date_time_string()`** — solo la hora.

> El autor desearía que el formato **año-mes-día** se estandarizara, porque así los nombres
> de archivo se ordenarían alfabéticamente. «Eso es un problema mío.»

---

## 11. `date_valid_datetime()`

Comprueba si una fecha es válida:

```gml
date_valid_datetime(2026, 8, 5, 12, 12, 12);   // Válida
```

Dos peculiaridades que divierten al autor:

- **Rechaza fechas anteriores al inicio de la época Unix (1970)**, aunque el formato de
  GameMaker **no** sea un timestamp Unix y debería ser válido hasta 1900.
- **Rechaza poner 30 días en febrero.**

> «Nunca se me habría ocurrido que esto fuera algo a lo que prestar atención… salvo que por
> lo visto a alguien le pareció suficiente problema como para añadirlo a GameMaker.»

Y señala que **el manual no lo documenta explícitamente**: asume que ya lo sabes.

---

## 12. Zonas horarias

```gml
date_set_timezone(timezone_local);
date_set_timezone(timezone_utc);
```

Permite trabajar con la **hora local** del sistema o con **UTC**.

> **⚠️ El ajuste persiste entre fotogramas**: si lo cambias para una comprobación,
> **vuelve a dejarlo como estaba** antes de dibujar la hora local.

El autor confiesa no haber tenido que usarla nunca, pero está ahí si la necesitas.

(Curiosamente, su instalación de Windows le da una diferencia de 7 horas en vez de 4: sospecha
que Windows no sabe en qué zona horaria está, no que GameMaker esté fallando.)

---

## 13. `get_timer()` y para qué sirve de verdad

```gml
get_timer();
```

Es igual que `current_time` pero **en microsegundos** en vez de milisegundos:

| Función | Unidad |
|---|---|
| `current_time` | **Milisegundos** (1/1000 de segundo) |
| `get_timer()` | **Microsegundos** (1/1.000.000 de segundo) |

> Si le quitas los últimos tres dígitos a `get_timer()`, obtienes exactamente
> `current_time`.

Usos reales que le da el autor:

- **Medir cuánto tarda una tarea** concreta del juego.
- **Hacer benchmarking** de código cuando usar el perfilador no resulta práctico. «Lo uso
  constantemente para esto.»
- Podrías usarla para fijar la semilla del generador aleatorio… aunque en la práctica es
  mejor llamar directamente a `randomise()`.

> En conjunto, el autor considera que ambas son **más útiles para diagnóstico que para
> jugabilidad**.

---

## 14. Funciones curiosas: `date_is_today()` y `date_leap_year()`

| Función | Para qué |
|---|---|
| **`date_is_today(timestamp)`** | Saber si una fecha es hoy, sin tener que comparar día, mes y año por separado |
| **`date_leap_year(timestamp)`** | Saber si un año es **bisiesto** |

### La regla de los años bisiestos

> El manual sugiere usar `date_leap_year()` para **huevos de Pascua** en tus juegos.

El autor aprovecha para explicar la regla completa:

- Los años **divisibles por 4** son bisiestos. (Todo el mundo sabe esta parte.)
- Pero los **divisibles por 100 NO** lo son…
- **…salvo** si son **divisibles por 400**.

Por tanto:

| Año | ¿Bisiesto? | Motivo |
|---|---|---|
| 2000 | **Sí** | Divisible por 400 |
| 1900 | No | Divisible por 100 pero no por 400 |
| 2100 | No | Divisible por 100 pero no por 400 |

> «Probablemente no sea algo que afecte a nadie vivo hoy… aunque, siendo 2026, puede que
> alguno siga por aquí en 2100.»

(El autor bromea con que **no confirmará ni desmentirá** si su juego tiene huevos de Pascua
para jugar un 29 de febrero.)

---

## 15. Atajo de teclado útil

> **`Ctrl + D`** (o `Cmd + D` en Mac) **duplica la línea actual**.

Muy útil para escribir varias líneas parecidas. **También funciona en el navegador de
recursos** para duplicar un asset.

> El autor cree que mucha gente lo descubre **por accidente**, queriendo pulsar `Ctrl + S`
> y fallando.

---

## Puntos clave

1. **`current_second/minute/hour/day/month/year/weekday`** dan la hora real del sistema; son
   de **solo lectura**.
2. **`current_weekday`** empieza en **0** (domingo); **`current_month`** empieza en **1**
   (enero).
3. **`current_time`** = milisegundos desde que arrancó el juego.
4. **`date_create_datetime(a, m, d, h, min, s)`** crea una marca de tiempo; el formato son
   **días desde 1899** con la fracción del día como decimales.
5. **`date_current_datetime()`** hace lo mismo con la hora actual.
6. Usa **`string_format()`** si GameMaker te trunca los decimales al mostrar un número.
7. **`date_get_*()`** extrae datos; **`date_inc_*()`** avanza el tiempo **devolviendo una
   marca nueva** (no modifica la original).
8. **`date_*_span()`** mide tiempo transcurrido (ojo: el orden del nombre está invertido
   respecto al resto).
9. **`date_compare_datetime()`** devuelve −1 / 0 / +1.
10. **`date_datetime_string()`** formatea **y localiza** automáticamente.
11. **`get_timer()`** devuelve **microsegundos**: ideal para medir rendimiento.
12. **`Ctrl + D`** duplica la línea actual (y también assets).

---

## Ejercicio propuesto

> **Objetivo:** montar un pequeño panel de reloj y usar las fechas para algo útil: un
> sistema de guardado con fecha.

**Parte A — El reloj**

1. Crea un objeto vacío y, en su Draw, muestra las siete variables `current_*` en líneas
   separadas (espaciadas 32 píxeles).
2. Comprueba que `current_hour` usa formato **24 horas**.
3. Averigúa qué día de la semana es hoy y verifica que `current_weekday` cuadra con
   **domingo = 0**.
4. Añade `current_time` y observa cómo sube.

**Parte B — Marcas de tiempo**

5. Crea una marca de tiempo fija con `date_create_datetime()` y muéstrala. Comprueba qué
   aspecto tiene (un número grande con decimales).
6. Muestra la misma marca con **`string_format()`** y 6 decimales, y observa cómo avanza.
7. Sustitúyela por `date_current_datetime()`.
8. Extrae la hora y el año con `date_get_hour()` y `date_get_year()`. **No** llames a la
   variable `current_hour`.

**Parte C — Aritmética de fechas**

9. Crea una fecha fija y avánzala 5 días con `date_inc_day()`. Comprueba que la original
   **no se modifica**.
10. Avánzala 15 días y verifica el día resultante.
11. Mide cuántos días han pasado entre esa fecha y hoy con `date_day_span()`.
12. Compara las dos fechas con `date_compare_datetime()` y comprueba el signo devuelto.

**Parte D — Para el jugador**

13. Muestra la fecha con `date_datetime_string()` y comprueba que **se localiza** a tu
    región.
14. Comprueba `date_valid_datetime()` con: una fecha válida, una anterior a 1970, y un
    30 de febrero. Anota los tres resultados.
15. Prueba `date_is_today()` con una marca de hoy y con una de otro día.
16. Comprueba `date_leap_year()` con 2000, 1900 y 2100, y verifica la regla de los
    bisiestos.

**Reto extra (el caso útil):** implementa un sistema de guardado que almacene
`date_current_datetime()` al guardar, y al cargar muestre al jugador **«Última partida:
<fecha>»** usando `date_datetime_string()`. Añade también cuántos días han pasado con
`date_day_span()`. Es el uso más práctico de todo este apartado.
