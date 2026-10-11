# r23 · HTTP e input: ejecución del GML documental

Fecha: **11-10-2026**. **49 comprobaciones correctas, 0 fallidas** en la pasada positiva;
cuatro controles negativos detectan sus fallos. Python **3.10.21**, CLI **2.4.0**,
GMS2 **2026.0.0.23**, target **mac**, VM, macOS arm64. Las cinco compilaciones sin
`--errors-only` terminan con salida 0 y sin líneas `WARNING`.

## 1 · Repetición y vinculación con fuentes

```sh
python3 _indice/pruebas/probar-http-r48.py
python3 _indice/pruebas/probar-http-r48.py --solo-extraer
python3 _indice/pruebas/probar-http-r48.py --mutacion progreso
python3 _indice/pruebas/probar-http-r48.py --mutacion http
python3 _indice/pruebas/probar-http-r48.py --mutacion cola
python3 _indice/pruebas/probar-http-r48.py --mutacion input
```

La pasada positiva debe salir con 0; cada mutación, con **1**, no con error de entorno 2.
El runner comprueba **49 aserciones**, ocho peticiones del servidor y ocho callbacks
terminales. Un resultado ausente, duplicado, incompleto o una fuente cambiada no da verde.
Los [recibos públicos](./r23-http-recibos.json) contienen las huellas por documento/bloque,
banco y orquestador, códigos de salida, solicitudes y diagnósticos escalares del callback.
No contienen rutas personales, cuerpos de usuario, credenciales ni endpoints remotos.

Se extraen de sus documentos el clasificador, el bloque de lectura/envío de telemetría
y los dos eventos HTTP. Los callbacks se escriben íntegros en eventos reales; el código
declarado no tiene una implementación alternativa en Python. El fragmento vectorial
de Input se extrae desde la lectura de ejes hasta antes de la colisión y se envuelve
en una función que devuelve el vector. Se inyectan ejes en esa frontera; no hardware.

Para liveops, el fixture sustituye **solo** la aplicación del dominio por un receptor
JSON mínimo que cuenta efectos. Acredita el filtro del callback, no el esquema de
configuración, sus valores de balance ni su caché completa. Los macros del banco
fijan nombres de fichero de prueba; los pedidos los lanza el propio banco al servidor
local. No se acredita la función de envío con un endpoint de producción.

Recursos y eventos se crean por ResourceTool, con `eventNum=62` por `RESOURCE SET`
y el nombre correcto de `.gml`; no se editan `.yy`/`.yyp`. Proyecto y servidor son propios,
temporales. El servidor escucha exclusivamente en loopback y se cierra en `finally`.
Cada comando tiene un tope; el ejecutor POSIX reutilizado de r47 termina solo su grupo.

## 2 · Casos y denominadores

- **20 contratos sintéticos:** progreso, error, código ausente, 13 códigos/tipos HTTP,
  ID ajeno, intento invalidado, estado desconocido y map sin campos.
- **4 vectores:** cero, `(0.4, 0)`, diagonal `(1, 1)` y `(0.3, 0.4)`.
  Tolerancia declarada **0.0001**. Una aserción `< 0.000001` fallaba incluso con cero
  diferencia porque el epsilon de comparación predeterminado es 0.00001; se corrigió
  el instrumento sin cambiar el epsilon global del juego.
  [Contrato oficial de comparaciones](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Number_Functions/math_set_epsilon.htm).
- **25 comprobaciones de integración:** ocho solicitudes iniciadas, ocho cierres de intento,
  ocho efectos de config/persistencia y conservación del contenido nuevo. GET 200 válido,
  500, 204 y JSON roto; POST 500, 200, 204 y confirmación de un volcado anterior.

## 3 · Controles negativos sobre el fixture

| Mutación | Correctas / fallidas | Salida | Fallo observado |
|---|---|---|---|
| Progreso considerado terminal | 48 / 1 | 1 | Se pierde la guarda que conserva el intento |
| Cualquier HTTP ≥ 200 aceptado | 43 / 6 | 1 | Se admiten redirecciones y respuestas de error |
| Borrado sin comparar el volcado enviado | 47 / 2 | 1 | Desaparece el fichero nuevo y su contenido |
| Normalización de todo vector no nulo | 47 / 2 | 1 | Inclinaciones 0.4 y 0.5 se convierten en velocidad máxima |

La mutación debe localizar exactamente un punto de aplicación. Los documentos nunca
se mutan: cada fixture conserva la huella de su fuente y registra la variante introducida.

## 4 · Límites

El progreso y el código ausente se fuerzan con maps sintéticos; no se declara descarga
progresiva real. Los intentos invalidados prueban el descarte por ID, no un sistema completo
de generaciones ni cancelación del transporte. No se ejecutaron TLS, CORS, backend remoto,
persistencia multisesión, idempotencia del servidor, HTML5, Android, Windows, YYC o GMRT.
El input no acredita hotplug, mandos físicos ni colisiones. La prueba de 49 casos no
certifica ausencia de errores en todos los clientes HTTP ni en todos los juegos.
