# 18 · Fecha y hora en GML

> Referencia exhaustiva de **GameMaker LTS 2026** (IDE 2026.0.0.16 · Runtime 2026.0.0.23).

> Todas las firmas han sido verificadas contra el manual oficial LTS.

---

## Cómo funciona el tipo *datetime*

Un **datetime** es un único número real que codifica **a la vez** la fecha y la hora.
GameMaker ofrece funciones para construirlo, compararlo, descomponerlo en partes y
calcular distancias entre dos de ellos.

```gml
var _ahora = date_current_datetime();
show_debug_message(date_datetime_string(_ahora));
```

Por defecto todas las funciones trabajan en la **hora local** del sistema. Para que el
comportamiento sea idéntico en todos los dispositivos, fija la zona horaria a UTC:

```gml
date_set_timezone(timezone_utc);
```

| Constante | Significado |
| --- | --- |
| `timezone_local` | La hora local del sistema (valor por defecto). |
| `timezone_utc` | Tiempo universal coordinado. |

### El día de la semana

Tanto `date_get_weekday` como `current_weekday` devuelven un número de **0 a 6**:

| Valor | Día |
| --- | --- |
| 0 | domingo |
| 1 | lunes |
| 2 | martes |
| 3 | miércoles |
| 4 | jueves |
| 5 | viernes |
| 6 | sábado |

---

## Fecha y hora del sistema frente a temporización interna

Es importante no confundir las dos familias:

| Familia | Unidad | Para qué sirve |
| --- | --- | --- |
| `date_*` / `current_*` | Fecha y hora del **reloj del sistema** | Mostrar la hora, guardar cuándo se jugó, calcular recompensas diarias |
| `get_timer()` / `delta_time` | **Microsegundos** desde el arranque | Medir rendimiento y mover objetos con independencia del framerate |

```gml
// Movimiento independiente del framerate (delta_time está en microsegundos)
x += velocidad_por_segundo * (delta_time / 1000000);
```

---

## Crear y validar fechas


### `date_current_datetime()`

- **Devuelve:** Datetime
- **Qué hace:** Devuelve la fecha y hora **actual** como un valor *datetime*, en la zona horaria configurada.
- **Ejemplo:**

```gml
myhour = date_get_hour(date_current_datetime());
myday = date_get_day(date_current_datetime());
```

### `date_create_datetime(year, month, day, hour, minute, second)`

- **Devuelve:** Datetime
- **Qué hace:** Crea un valor *datetime* a partir de año, mes, día, hora, minuto y segundo.
- **Ejemplo:**

```gml
mydatetime = date_create_datetime(2011, 9, 15, 9, 43, 30);
```

### `date_valid_datetime(year, month, day, hour, minute, second)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la combinación de año, mes, día, hora, minuto y segundo forma una fecha y hora **válidas**.
- **Ejemplo:**

```gml
if (date_valid_datetime(2011, 9, 15, 10, 3, 30))
{
    mydatetime = date_create_datetime(2011, 9, 15, 10, 3, 30);
}
```

---

## Comparar fechas


### `date_compare_datetime(date1, date2)`

- **Devuelve:** Real
- **Qué hace:** Compara dos valores *datetime*. Devuelve `-1` si `date1` es anterior, `0` si son iguales y `1` si es posterior.
- **Ejemplo:**

```gml
d = date_compare_datetime(date_create_datetime(2011, 9, 15, 11, 4, 0), date_current_datetime());
```

- **Notas:** Devuelve `-1`, `0` o `1`: ideal para ordenar fechas directamente con `array_sort`.

### `date_compare_date( date1, date2 )`

- **Devuelve:** Real
- **Qué hace:** Compara solo la **fecha** de dos valores *datetime*, ignorando la hora. Devuelve `-1`, `0` o `1`.
- **Ejemplo:**

```gml
d = date_compare_date(date_create_datetime(2011, 9, 15, 11, 4, 0), date_current_datetime());
```

- **Notas:** Ignora la hora: solo compara año, mes y día.

### `date_compare_time(datetime1, datetime2)`

- **Devuelve:** Real
- **Qué hace:** Compara solo la **hora** de dos valores *datetime*, ignorando la fecha. Devuelve `-1`, `0` o `1`.
- **Ejemplo:**

```gml
d = date_compare_time(date_create_datetime( 2011, 9, 15, 11, 4, 0 ), date_current_datetime());
```

- **Notas:** Ignora la fecha: solo compara hora, minuto y segundo.

### `date_date_of(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve solo la parte de **fecha** de un datetime (la hora se descarta).
- **Ejemplo:**

```gml
today = date_date_of(date_current_datetime());
```

### `date_time_of(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve solo la parte de **hora** de un datetime (la fecha se descarta).
- **Ejemplo:**

```gml
time = date_time_of(date_current_datetime());
```

### `date_is_today(date)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el datetime corresponde al **día de hoy**.
- **Ejemplo:**

```gml
if (date_is_today(global.Halloween))
{
    global.Max_Levels = 200;
}
```

### `date_leap_year(date)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el año del datetime es **bisiesto**.
- **Ejemplo:**

```gml
if (date_leap_year(date_current_datetime()))
{
    if (!global.ExtraContent)
    {
        global.ExtraContent = true;
    }
}
```

---

## Extraer componentes


### `date_get_year(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **año** del datetime.
- **Ejemplo:**

```gml
myyear = date_get_year(date_current_datetime());
```

### `date_get_month(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **mes** del datetime (1 a 12).
- **Ejemplo:**

```gml
mymonth = date_get_month(date_current_datetime());
```

### `date_get_week(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el número de **semana** del año correspondiente al datetime.
- **Ejemplo:**

```gml
myweek = date_get_week(date_current_datetime());
```

### `date_get_weekday(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **día de la semana** del datetime: 0 = domingo, 1 = lunes, …, 6 = sábado.
- **Ejemplo:**

```gml
myweekday = date_get_weekday(date_current_datetime());
```

- **Notas:** 0 = domingo, 1 = lunes, 2 = martes, 3 = miércoles, 4 = jueves, 5 = viernes, 6 = sábado.

### `date_get_day(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **día del mes** del datetime (1 a 31).
- **Ejemplo:**

```gml
myday = date_get_day( date_current_datetime() );
```

### `date_get_hour(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la **hora** del datetime (0 a 23).
- **Ejemplo:**

```gml
myhour = date_get_hour(date_current_datetime());
```

### `date_get_minute(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve los **minutos** del datetime (0 a 59).
- **Ejemplo:**

```gml
myminute = date_get_minute(date_current_datetime());
```

### `date_get_second(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve los **segundos** del datetime (0 a 59).
- **Ejemplo:**

```gml
mysecond = date_get_second(date_current_datetime());
```

### `date_get_day_of_year( date )`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **día del año** del datetime (1 a 365, o 366 si es bisiesto).
- **Ejemplo:**

```gml
mydayyear = date_get_day_of_year(date_current_datetime());
```

### `date_get_hour_of_year(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántas **horas** han pasado desde el principio del año.
- **Ejemplo:**

```gml
myhouryear = date_get_hour_of_year(date_current_datetime());
```

### `date_get_minute_of_year(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántos **minutos** han pasado desde el principio del año.
- **Ejemplo:**

```gml
myminuteyear = date_get_minute_of_year(date_current_datetime());
```

### `date_get_second_of_year( date )`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántos **segundos** han pasado desde el principio del año.
- **Ejemplo:**

```gml
mysecondyear = date_get_second_of_year(date_current_datetime());
```

---

## Incrementar fechas


### `date_inc_year(date, amount)`

- **Devuelve:** Real
- **Qué hace:** Devuelve un datetime con `amount` **años** añadidos (o restados, si es negativo).
- **Ejemplo:**

```gml
mynewdatetime = date_inc_year(date_current_datetime(), 1000);
```

### `date_inc_month( date, amount )`

- **Devuelve:** Real
- **Qué hace:** Devuelve un datetime con `amount` **meses** añadidos.
- **Ejemplo:**

```gml
mynewdatetime = date_inc_month(date_current_datetime(), 12);
```

- **Notas:** GameMaker ajusta el día si el mes destino tiene menos días (por ejemplo, 31 de enero + 1 mes da 28/29 de febrero o 3 de marzo, según el año).

### `date_inc_week(date, amount)`

- **Devuelve:** Real
- **Qué hace:** Devuelve un datetime con `amount` **semanas** añadidas.
- **Ejemplo:**

```gml
mynewdatetime = date_inc_week(date_current_datetime(), 52);
```

### `date_inc_day(date, amount)`

- **Devuelve:** Real
- **Qué hace:** Devuelve un datetime con `amount` **días** añadidos.
- **Ejemplo:**

```gml
mynewdatetime = date_inc_day(date_current_datetime(), 365);
```

### `date_inc_hour(date, amount)`

- **Devuelve:** Real
- **Qué hace:** Devuelve un datetime con `amount` **horas** añadidas.
- **Ejemplo:**

```gml
mynewdatetime = date_inc_hour(date_current_datetime(), 24);
```

### `date_inc_minute( date, amount )`

- **Devuelve:** Real
- **Qué hace:** Devuelve un datetime con `amount` **minutos** añadidos.
- **Ejemplo:**

```gml
mynewdatetime = date_inc_minute(date_current_datetime(), 60);
```

### `date_inc_second(date, amount)`

- **Devuelve:** Real
- **Qué hace:** Devuelve un datetime con `amount` **segundos** añadidos.
- **Ejemplo:**

```gml
mynewdatetime = date_inc_second(date_current_datetime(), 60);
```

---

## Calcular distancias entre fechas


### `date_second_span(date1, date2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántos **segundos** hay entre dos datetimes.
- **Ejemplo:**

```gml
diff = date_second_span(date_create_datetime(2011, 9, 15, 11, 4, 0 ), date_current_datetime());
```

### `date_minute_span(date1, date2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántos **minutos** hay entre dos datetimes.
- **Ejemplo:**

```gml
diff = date_minute_span(date_create_datetime(2011, 9, 15, 11, 4, 0 ), date_current_datetime());
```

### `date_hour_span(date1, date2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántas **horas** hay entre dos datetimes.
- **Ejemplo:**

```gml
diff = date_hour_span(date_create_datetime( 2011, 9, 15, 11, 4, 0 ), date_current_datetime());
```

### `date_day_span(date1, date2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántos **días** hay entre dos datetimes.
- **Ejemplo:**

```gml
diff = date_day_span(date_create_datetime(2011, 9, 15, 11, 4, 0), date_current_datetime());
```

### `date_week_span(date1, date2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántas **semanas** hay entre dos datetimes.
- **Ejemplo:**

```gml
diff = date_week_span( date_create_datetime( 2011, 9, 15, 11, 4, 0 ), date_current_datetime() );
```

### `date_month_span(date1, date2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántos **meses** hay entre dos datetimes.
- **Ejemplo:**

```gml
diff = date_month_span(date_create_datetime(2011, 9, 15, 11, 4, 0 ), date_current_datetime());
```

### `date_year_span(date1, date2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántos **años** hay entre dos datetimes.
- **Ejemplo:**

```gml
diff = date_year_span(date_create_datetime(2011, 9, 15, 11, 4, 0), date_current_datetime());
```

### `date_days_in_month(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántos **días** tiene el mes del datetime indicado.
- **Ejemplo:**

```gml
days = date_days_in_month(date_current_datetime());
```

### `date_days_in_year(date)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántos **días** tiene el año del datetime indicado.
- **Ejemplo:**

```gml
days = date_days_in_year(date_current_datetime());
```

- **Notas:** Devuelve 365 o 366 según si el año es bisiesto.

---

## Convertir a string


### `date_date_string(date)`

- **Devuelve:** String
- **Qué hace:** Devuelve la **fecha** del datetime como string, con el formato por defecto del sistema.
- **Ejemplo:**

```gml
str = date_date_string(date_current_datetime());
 draw_text(32, 32, str);
```

- **Notas:** El formato depende de la configuración regional del sistema.

### `date_time_string(date)`

- **Devuelve:** String
- **Qué hace:** Devuelve la **hora** del datetime como string, con el formato por defecto del sistema.
- **Ejemplo:**

```gml
str = date_time_string(date_current_datetime());
```

- **Notas:** El formato depende de la configuración regional del sistema.

### `date_datetime_string(date)`

- **Devuelve:** String
- **Qué hace:** Devuelve la **fecha y la hora** completas como string, con el formato por defecto del sistema.
- **Ejemplo:**

```gml
str = date_datetime_string(date_current_datetime());
```

- **Notas:** El formato depende de la configuración regional del sistema.

---

## Zona horaria


### `date_set_timezone(timezone)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Fija la zona horaria que usarán las funciones de fecha: `timezone_local` (la del sistema) o `timezone_utc`.
- **Ejemplo:**

```gml
if (date_get_timezone() != timezone_utc)
{
    date_set_timezone(timezone_utc);
}
```

- **Notas:** Por defecto GameMaker usa la hora **local** del sistema. Llama a `date_set_timezone(timezone_utc)` si quieres consistencia entre dispositivos.

### `date_get_timezone()`

- **Devuelve:** Time Zone Constant
- **Qué hace:** Devuelve la zona horaria actualmente configurada.
- **Ejemplo:**

```gml
if (date_get_timezone() != timezone_utc)
{
    date_set_timezone(timezone_utc);
}
```

- **Notas:** Devuelve `timezone_local` o `timezone_utc`.

---

## Fecha y hora actuales (variables)


### `current_time`

- **Devuelve:** Real
- **Qué hace:** Número de **milisegundos** transcurridos desde la medianoche del 1 de enero de 1970 (época Unix), en hora local.
- **Ejemplo:**

```gml
if (current_time > 600000)
{
    msg = show_question_async("Would you like to rate?");
}
```

- **Notas:** En milisegundos desde la época Unix. Cuidado: en plataformas de 32 bits puede desbordar.

### `current_year`

- **Devuelve:** Real
- **Qué hace:** El **año** actual.
- **Ejemplo:**

```gml
draw_text(32, 32, "Today is " + string(current_day) + "/" + string(current_month) + "/" + string(current_year) + ".");
```

### `current_month`

- **Devuelve:** Real
- **Qué hace:** El **mes** actual (1 a 12).
- **Ejemplo:**

```gml
draw_text(32, 32, "Today is " + string(current_day) + "/" + string(current_month) + "/" + string(current_year) + ".");
```

### `current_day`

- **Devuelve:** Real
- **Qué hace:** El **día del mes** actual (1 a 31).
- **Ejemplo:**

```gml
draw_text(32, 32, "Today is " + string(current_day) + "/" + string (current_month) + "/" + string(current_year) +".");
```

### `current_weekday`

- **Devuelve:** Real
- **Qué hace:** El **día de la semana** actual: 0 = domingo, 1 = lunes, …, 6 = sábado.
- **Ejemplo:**

```gml
var day;
switch(current_weekday)
{
    case 0: day = "Sunday"; break;
    case 1: day = "Monday"; break;
    case 2: day = "Tuesday"; break;
    case 3: day = "Wednesday"; break;
    case 4: day = "Thursday"; break;
    case 5: day = "Friday"; break;
    case 6: day = "Saturday"; break;
}
draw_text(32, 32, "Today is " + day +".");
```

- **Notas:** 0 = domingo, 1 = lunes, …, 6 = sábado.

### `current_hour`

- **Devuelve:** Real
- **Qué hace:** La **hora** actual (0 a 23).
- **Ejemplo:**

```gml
draw_text(32, 32, "The time is " + string(current_hour) + ":" + string(current_minute) + "." + string(current_second));
```

### `current_minute`

- **Devuelve:** Real
- **Qué hace:** Los **minutos** actuales (0 a 59).
- **Ejemplo:**

```gml
draw_text(32, 32, "The time is " + string(current_hour) + ":" + string(current_minute) + "." + string(current_second));
```

### `current_second`

- **Devuelve:** Real
- **Qué hace:** Los **segundos** actuales (0 a 59).
- **Ejemplo:**

```gml
draw_text(32, 32, "The time is " + string(current_hour) + ":" + string(current_minute) + "." + string(current_second));
```

---

## Temporización de alta precisión


### `get_timer()`

- **Devuelve:** Real
- **Qué hace:** Devuelve los **microsegundos** transcurridos desde que se arrancó el juego. Es la herramienta de mayor precisión para medir tiempos internos; no tiene relación con la fecha del sistema.
- **Ejemplo:**

```gml
time = get_timer();
```

- **Notas:** Se reinicia al arrancar el juego. Úsalo para medir, no para saber la hora.

### `delta_time`

- **Devuelve:** Real (integer)
- **Qué hace:** Los **microsegundos** que tardó el fotograma anterior en procesarse. Es la medida real del tiempo entre fotogramas y la base de cualquier movimiento independiente del framerate.
- **Ejemplo:**

*Ejemplo 1: velocidad base en píxeles por paso*


```gml
var _dt = delta_time / game_get_speed(gamespeed_microseconds);
speed = spd * _dt;
```

*Ejemplo 2: velocidad base en píxeles por segundo*


```gml
var _dt = delta_time / 1000000;
speed = spd * _dt;
```

- **Notas:** Se mide en **microsegundos**. Para pasar a segundos: `delta_time / 1000000`.

---

## Receta: recompensa diaria

El patrón típico de «vuelve mañana para recoger tu premio»:

```gml
function puede_reclamar_diario()
{
    var _ahora = date_current_datetime();
    var _ultimo = variable_global_get("ultima_recompensa");

    if (is_undefined(_ultimo)) return true;

    return date_day_span(_ultimo, _ahora) >= 1;
}

function reclamar_diario()
{
    global.ultima_recompensa = date_current_datetime();
    global.monedas += 100;
}
```

## Receta: formatear un cronómetro

```gml
function formatear_crono(_milisegundos)
{
    var _total_seg = floor(_milisegundos / 1000);
    var _min = floor(_total_seg / 60);
    var _seg = _total_seg mod 60;
    var _cen = floor((_milisegundos mod 1000) / 10);

    return string_format(_min, 2, 0) + ":" +
           string_format(_seg, 2, 0) + "." +
           string_format(_cen, 2, 0);
}
```

## Receta: saber cuánto tiempo lleva el jugador sin entrar

```gml
var _ahora   = date_current_datetime();
var _ultima  = json_parse(cargar_json()).ultima_vez;
var _dias    = date_day_span(_ultima, _ahora);
var _horas   = date_hour_span(_ultima, _ahora) mod 24;

show_debug_message($"Ausente {_dias} días y {_horas} horas");
```

---

## Funciones de fecha que NO existen en GML

| Nombre | Alternativa real |
| --- | --- |
| `date_is_timezone()` | `date_get_timezone()` |
| `set_timer()` | No existe: usa *time sources* (`time_source_create`) |
| `date_get_timestamp()` | `current_time` / `date_current_datetime()` |

> Para cualquier temporizador dentro del juego, usa los **time sources**
> (`time_source_create`, `time_source_start`, …), no las alarmas ni las funciones de fecha.

---

## Fuentes

- [GML Code Reference — GameMaker LTS 2026](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/GML_Reference.htm)
- [Date And Time (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Date_And_Time/Date_And_Time.htm)
- [Time Sources (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Time_Sources/Time_Sources.htm)
- Verificación de cada firma con `gm-cli manual read "<función>"` y contra el manual LTS (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
