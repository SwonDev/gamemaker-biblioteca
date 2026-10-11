# 12 · HTTP asíncrono: estados, propiedad y respuestas tardías

> Contrato transversal para clientes HTTP en GML. Complementa las recetas de
> [configuración remota](<../04 - Recetas por género/52 - Live-ops técnico (config remota, versión mínima, mensajes del juego).md>)
> y [telemetría](<../13 - Diseño y producción de videojuegos/01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md>).
> No sustituye una librería HTTP existente ni implementa un backend.
> Fuentes LTS consultadas el **11-10-2026**; la ejecución se registra por runtime y target,
> sin extender una prueba de macOS a HTML5, móvil, YYC o GMRT.

## 1 · Separar transporte, HTTP y aceptación del producto

Un callback tiene tres preguntas distintas: ¿terminó la descarga?, ¿qué respondió HTTP?,
¿aceptó el servicio la operación? En `async_load`, `status` pertenece al motor;
`http_status` pertenece a HTTP. Un `status == 0` con `http_status == 500` no es éxito.
Una respuesta 2xx tampoco demuestra por sí sola que un pago, una partida o un lote
de eventos haya quedado persistido: manda el contrato del endpoint y su confirmación.

| Situación | Acción del cliente |
|---|---|
| ID ajeno | Ignorar; puede pertenecer a otro sistema |
| `status == 1` | Conservar el ID en vuelo; es progreso |
| `status < 0` | Cerrar el intento como fallo de transporte |
| `status == 0`, código HTTP ausente | Cerrar el intento sin acreditar éxito |
| `status == 0`, código HTTP fuera de 2xx | Resolver según el endpoint; conservar datos pendientes |
| 2xx | Validar el cuerpo y la confirmación que el endpoint exija |

Un 204 no trae cuerpo que analizar. Un 304 requiere una caché válida y una solicitud
condicional previa; no significa «aplica un JSON vacío». Redirecciones, autenticación,
429 y 5xx necesitan una política explícita. No reintentes todos los 4xx indefinidamente.

### 1.1 Clasificador compartido

Este helper propio recibe un DS map válido del evento y el ID esperado. No conserva
el map, no lo destruye y no interpreta JSON. Los campos de diagnóstico son escalares.
La receta que lo usa debe incluir este bloque en un script del proyecto.

```gml
function clasificar_respuesta_http(_mapa, _id_esperado)
{
    var _r = { coincide: false, terminal: false, exito_http: false,
               clase: "invalida", codigo: -1 };
    if (!ds_map_exists(_mapa, "id") || !ds_map_exists(_mapa, "status")) return _r;
    if (_id_esperado == -1 || _mapa[? "id"] != _id_esperado)
    {
        _r.clase = "ajena";
        return _r;
    }
    _r.coincide = true;
    var _estado = _mapa[? "status"];
    if (!is_real(_estado)) return _r;
    if (_estado == 1) { _r.clase = "progreso"; return _r; }
    if (_estado < 0) { _r.terminal = true; _r.clase = "transporte"; return _r; }
    if (_estado != 0) return _r;

    _r.terminal = true;
    _r.clase = "sin_codigo";
    if (!ds_map_exists(_mapa, "http_status")) return _r;
    var _codigo = _mapa[? "http_status"];
    if (!is_real(_codigo) || _codigo != floor(_codigo)
        || _codigo < 100 || _codigo > 599) return _r;
    _r.codigo = _codigo;
    _r.clase = "http";
    _r.exito_http = _codigo >= 200 && _codigo < 300;
    return _r;
}
```

`exito_http` describe únicamente la categoría HTTP. En un GET de configuración,
exige además un cuerpo string, JSON válido, esquema y versión compatibles; en un POST,
la confirmación definida por el servicio. El clasificador trata una respuesta sin código
como indeterminada, aunque el transporte terminase. Eso evita borrar una cola sin evidencia.

## 2 · Propiedad y vida útil

Los eventos asíncronos se difunden a las instancias que tengan ese evento. El emisor
y el receptor pueden ser distintos. Usa un receptor de vida estable y separa el
ID de transporte del destinatario lógico: pantalla, partida, perfil o sesión.

`async_load` solo es válido durante el evento: GameMaker crea y elimina su DS map.
No lo guardes en una cola para el Step ni lo destruyas. Copia los strings y números
necesarios a datos propios. `response_headers` puede faltar: comprueba su existencia
y la validez del DS map antes de leerlo, y copia los valores que quieras conservar.
Un buffer o recurso recibido sigue teniendo una política de propiedad específica;
copiar su handle no duplica el recurso. No extrapoles el ciclo de vida del map a ese buffer.

El map de cabeceras que **tú** creas para `http_request` se puede destruir tras la
llamada, como muestra el ejemplo oficial. Si usas un buffer como cuerpo o destino,
consulta su contrato de posición, tamaño usado y liberación en el runtime aplicable;
esta receta usa cuerpos string y no acredita esa variante.

## 3 · Tiempo, sustitución y cancelación lógica

Registra por intento: ID, instante de inicio, plazo, destinatario y generación de su
contexto. El plazo es tiempo transcurrido, no número de frames. Una pérdida de foco
o una suspensión puede retrasar la entrega al bucle principal.

1. Si la llamada devuelve `-1`, no queda un intento esperando callback. Registra el
   fallo de inicio y aplica la cadencia de reintento; evita relanzarla cada frame.
2. El progreso conserva el ID. Solo un resultado terminal o el plazo local cierra el intento.
3. Al caducar o sustituir el intento, invalida su ID lógico y suscribe el nuevo con
   otro ID y generación. Descarta los callbacks antiguos antes de aplicar efectos.
4. Antes de entregar el resultado, verifica que el destinatario y su generación
   siguen vigentes. Una pantalla recreada no debe recibir la respuesta de la anterior.
5. Una cancelación **lógica** evita aplicar el resultado; no demuestra que el transporte
   se haya detenido ni que el servidor haya deshecho un POST. No inventes una función
   de cancelación: comprueba la API de la librería o extensión elegida.

Limita intentos concurrentes, tamaño de respuesta y presupuesto de reintentos. Para
descargas grandes, selecciona archivo o buffer y su presupuesto antes de solicitarlas.
El progreso no está disponible en todos los targets: una UI debe poder mostrar espera
indeterminada sin depender de que llegue `status == 1`. HTML5 añade CORS y restricciones
del navegador; una prueba de localhost nativa no comprueba esas condiciones.

## 4 · Persistencia e idempotencia

Una cola no se borra por «ha terminado HTTP». Conserva exactamente el lote enviado
hasta recibir su confirmación. Si el fichero cambió mientras volaba, no borres su
versión nueva al confirmar la anterior. La comparación con el cuerpo enviado protege
esa escritura nueva; una cola con varios lotes necesita IDs estables y confirmaciones
por lote, sin reescribir los pendientes de otra sesión al iniciar.

Si el servidor aceptó un POST y la respuesta se perdió, repetir puede duplicar su efecto.
Define una clave estable por operación/lote que el **servidor** deduplique y confirme.
Generar una clave nueva en cada reintento rompe esa protección. Un timeout o un checksum
local no prueban ejecución «exactamente una vez». Tampoco una URL pública es un secreto;
las credenciales sí deben vivir fuera del código y nunca aparecer en logs o recibos.

## 5 · Pruebas que distinguen los fallos

| Caso | Debe observarse |
|---|---|
| Progreso seguido de final | El ID sigue vigente y el final se procesa |
| ID ajeno, repetido o respuesta de una generación anterior | Ningún efecto duplicado o sobre el contexto nuevo |
| Transporte fallido; 400, 429 y 500; código ausente | Datos pendientes conservados y política de reintento explícita |
| 200 con JSON roto; 204; 304 | Validación y caché conforme al endpoint, sin asumir cuerpo |
| Un segundo volcado durante un POST | Confirmar el primero no borra datos nuevos |
| Plazo local y respuesta tardía | Cierre del intento; callback tardío descartado |
| Cerrar y reabrir el proceso | Recuperación real de pendientes, según el esquema de cola |

Prueba el clasificador con maps sintéticos para forzar progreso y códigos ausentes;
prueba también eventos reales contra un servidor local controlado. El servidor registra
peticiones y códigos, el runner registra IDs y efectos, y el recibo fija las huellas de
los bloques ejecutados. No conviertas un control sintético en evidencia de CORS, TLS,
backend remoto, deduplicación del servidor o persistencia tras un cierre.

## Fuentes

- [Eventos asíncronos y vida útil de async_load](https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Async_Events.htm).
- [Evento HTTP: estados, campos y targets con progreso](https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Async_Events/HTTP.htm).
- [http_request: firma, retorno y cuerpos](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asynchronous_Functions/HTTP/http_request.htm).
- [GMRT 0.22: corrección específica de liberación del buffer HTTP](https://releases.gamemaker.io/release-notes/2026/GMRT_MS_22).
