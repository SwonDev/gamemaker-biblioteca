# r22 · Contratos, contradicciones y límites de la biblioteca

Fecha: **11-10-2026**. Auditoría dirigida sobre el paquete público posterior a r46.
Se revisan las fuentes de autoridad, consumidores del índice y secciones de red,
guardado cloud, replay, localización, accesibilidad y publicación. No es una lectura
semántica de todos los documentos ni una certificación de ausencia de errores.

Se reutilizan los capítulos existentes. Los recibos anteriores siguen siendo históricos:
[r19](./r19-cobertura-y-portabilidad.md) mide presencia temática y describe sus límites;
[r21](./r21-publicacion.md) acredita los casos ejecutados en aquella revisión. Ninguno
demuestra por sí solo la corrección de todos los contratos de una receta.

## 1 · Hallazgos y destino

Las ubicaciones citan secciones estables, porque las líneas cambian durante la integración.
«Corregido» describe el cambio de fuente; los niveles de comprobación están en §3.

| Evidencia inicial | Diferencia que faltaba | Destino existente y estado |
|---|---|---|
| Selección lexicográfica del último directorio de runtime en los consumidores del índice | `2026.9.0.0` ordena después de `2026.10.0.0`; además, tener una caché más reciente no demuestra qué runtime usa un proyecto | `_indice/buscar.py`, `construir-indices.py`, `validar-proyecto.py`: comunicado a la revisión de herramientas; resolución común en `runtime_biblioteca.py` |
| El extractor ignoraba un XML malformado y podía devolver una API parcial o vacía | Una extracción incompleta no puede publicar un índice que parezca completo ni justificar un resultado negativo | `_indice/construir-indices.py`: reproducción aislada y hallazgo trasladado a la revisión del extractor |
| `08 · 04` negaba la existencia de `gpu_get_blendequation_sepalpha`, declarado en el índice y tratado en `08 · 20` | La prosa debe conservar la firma y el retorno real; una limitación histórica no equivale a inexistencia actual | [08 · 04 — Color y blending](<../../08 - Referencia GML completa/04 - Color y blending.md>), «Ecuaciones de mezcla»: corregido por la revisión de autoridad |
| Raíz y QA describían inversión vertical de `screen_save`, mientras la medición posterior citada decía lo contrario | Conservar runtime, plataforma y fecha de cada medición; comparar ventana y captura antes de transformar píxeles | `AGENTS.md` y [13 · 10 — QA](<../../13 - Diseño y producción de videojuegos/10 - Testing y QA.md>) §7.3: conciliados por la revisión de QA; no se repite una prueba visual aquí |
| El mapa y las reglas citaban revisiones distintas de Beta bajo una misma referencia | Separar versión de referencia, instantánea fechada y última versión disponible | `_indice/MAPA.json` y reglas de autoridad: revisión coordinada; fuentes fechadas en §4 |
| La skill atribuía a `--todo` un cambio de código de salida que el validador ya aplicaba sin esa opción | Diferenciar ampliar el informe de cambiar la condición de fallo | Skill y `_indice/validar-proyecto.py`: contradicción comunicada a la revisión de la skill |
| El evento de conexión no comprobaba `succeeded`; el texto pedía borrar también el buffer entrante | Una solicitud de conexión puede terminar con fallo; el buffer de Async Networking pertenece al motor hasta terminar el evento | [04 · 14 — Multijugador](<../../04 - Recetas por género/14 - Multijugador.md>) §§4.2 y 5.4: corregido |
| Snapshot contaba IDs que después no escribía; faltaban consumidor de intenciones y confirmación por destinatario | Longitud declarada, entidades vivas y bytes escritos deben coincidir; el ACK confirma entrada aplicada por ese cliente | `04 · 14` §§5.3–5.8: filtrado previo, lectura acotada, secuencias y ACK individual; el callback de gameplay y la re-simulación completa siguen siendo fronteras explícitas |
| La arquitectura distinguía propietario y equipo, pero la aplicación del snapshot e interpolación usaban el equipo como identidad; el reloj global no se inicializaba en el código base | Compartir equipo no concede predicción local; el host no debe interpolar encima de su simulación; el reloj debe tener dueño e inicialización | `04 · 14` §§5.0–5.8 bis: propietario `u32` independiente, registro de 19 bytes, límite común, interpolación solo del cliente y tick de sesión inicializado |
| TCP raw se presentaba sin contrato de reconstrucción | Una lectura TCP puede contener una fracción de mensaje o varios; cada peer necesita estado, longitud máxima y gestión de envíos parciales | `04 · 14` §4.2 bis: contrato y negativos documentados; no se presenta un parser raw como implementado |
| La carga cloud prefería automáticamente la copia Steam cuando existía | Una copia cloud puede ser anterior al progreso offline; diferencia de contenido no prueba cuál es válida o más nueva | [04 · 20 — Servicios de plataforma](<../../04 - Recetas por género/20 - Servicios de plataforma (logros, anuncios, compras).md>) §5: lectura de candidatos sin sobrescritura, conflicto, revisión base, validación y recuperación |
| Activación por app y éxito de escritura local en la API se confundían con sincronización remota completada | Cuenta y app tienen controles separados; la API puede trabajar con caché local y una escritura no acredita recepción del servidor | `04 · 20` §5: ambos controles, resultado limitado, cuotas, raíces por plataforma y cambios durante suspensión |
| SHA-1 sin clave se llamaba firma; el verificador omitía frames sin acción y podía comparar JSON reserializado | El checksum prueba consistencia del sobre, no autenticidad; hay que conservar bytes y avanzar todos los ticks con contexto confiable | [13 · 10 — QA](<../../13 - Diseño y producción de videojuegos/10 - Testing y QA.md>) §14.3: sobre con JSON exacto, límites, seed/versión confiables, agrupación por frame y simulación de ticks vacíos |
| Dos formas de plural servían también para los idiomas de más categorías; el fallback conservaba el código solicitado | Las reglas y claves corresponden al idioma realmente cargado; enteros, decimales y ordinales tienen contratos distintos | [04 · 21 — Localización](<../../04 - Recetas por género/21 - Localización e idiomas (con traducción por IA).md>) §§1 y 2: subconjunto cardinal entero CLDR 48 explícito, categorías por idioma y marcador para entradas no soportadas |
| Cobertura de RTL y fuentes no distinguía caracteres de grafemas | Recortar, borrar y revelar texto exige límites de grafema; segmentación, normalización y bidi son problemas distintos | `04 · 21` §4.1: contrato Unicode y casos de composición, selección, escritura mixta y glifos; no se inventa una función GML de segmentación |
| Se daban porcentajes universales de traducción automática y expansión del alemán | Medir cadenas, contexto y locales del producto; una categoría de idioma no da una tasa de corrección o anchura universal | `04 · 21` §§4 bis y 5, «Las trampas»: afirmaciones retiradas; revisión lingüística y dimensiones verificables |
| `reduce_motion` mantenía un flash con alfa menor; el límite de flashes se trataba por emisor | La opción debe suprimir el efecto previsto; para WCAG el recuento corresponde a la composición visible, en cualquier segundo | [04 · 27 — Accesibilidad](<../../04 - Recetas por género/27 - Accesibilidad.md>) §3: retorno antes del flash, criterio compuesto y distinción entre flashes y patrones |

## 2 · Lagunas útiles que permanecen

Estas son propuestas de extensión o pruebas pendientes, no declaraciones de ausencia de
capítulos. Publicación, privacidad, RTL, accesibilidad, QA y producción ya tienen material.

| Base existente | Extensión o evidencia que falta | Criterio verificable |
|---|---|---|
| `13 · 10` §§8.2–8.4, 9.2 y 9.5; `05 · 02`; `05 · 05`; `13 · 11` §§4.6 y 10 | Vincular en una matriz común compilación, paquete instalado y descarga de tienda, con runtime, configuración, revisión y huella del artefacto | Por destino declarado: primera instalación y actualización, usuario sin cachés del desarrollador, permisos/rutas reales, arranque offline y recuperación; cada casilla conserva resultado y entorno, sin extrapolar Wine a Windows nativo |
| `04 · 14` §§5.7–5.8 bis | Ejecutar la fixture loopback y completar netcode para un juego concreto | Dos peers y servidor, conexión fallida, entrada inválida/duplicada, entidad eliminada, snapshot truncado, ACK por cliente y pérdida del host; definir timeout, acciones, cola o intención mantenida y reconciliación antes de declarar producto |
| `04 · 14` §4.2 bis | Implementar y probar el parser si un proyecto necesita TCP raw | Fragmentar cabecera y payload, agrupar mensajes, exceder límite, cerrar a mitad y simular envío parcial; no basta que compile una llamada a `network_send_raw` |
| `04 · 20` §5 y `01 · 14` | Probar los conflictos en una app Steam configurada y con cuentas/entornos de prueba autorizados | Dos ramas desde la misma revisión, progreso offline, cuota/error, cloud desactivado, datos corruptos, OS distintos y suspensión; conservar ambas copias y registrar decisión sin afirmar una subida no observada |
| `04 · 21` §§1, 4 y 5; `13 · 11` §12.6 | Extender el plural al repertorio real del producto y probar el renderer/editor elegido | Decimales visibles, ordinales o idiomas fuera del subconjunto requieren reglas verificadas; grafemas, bidi y ajuste de caja requieren pruebas del flujo real, además de que estén los glifos |
| `04 · 27` §3 y `13 · 10` | Evaluar la composición audiovisual exportada con opciones persistidas | Medir el caso más intenso con todos los emisores, revisar patrones y cambios de escena; WCAG y XAG orientan criterios, pero este cambio de código no certifica ausencia de riesgo |
| `13 · 10` §14.3 | Ejecutar replay con estado inicial, reloj, acciones y azar del juego y con el servidor receptor | Frames vacíos y simultáneos, límites, seed/versión discordantes, acción inválida y checksum recalculado; la verificación no acredita por sí sola autor humano ni ausencia de automatización |

## 3 · Comprobación observada en esta auditoría

- **Lectura primaria y contraste de código:** manual LTS de Networking, fuentes de extensión
  Steamworks fijadas a revisión, release notes, CLDR y estándares Unicode, RFC 2104, WCAG
  2.2 y XAG 118. Context7 no pudo consultarse por cuota del proveedor; no se sustituyó esa
  limitación por una supuesta consulta realizada.
- **Reproducciones aisladas de herramientas, sin publicar índices:** extracción de las funciones
  antiguas mediante AST; listado simulado `2026.9.0.0`/`2026.10.0.0` reprodujo la selección
  lexicográfica; carpeta temporal vacía devolvió `{}`; fixture válida junto a XML malformado
  devolvió solo la parte válida. Son recibos del defecto anterior, no del helper nuevo.
- **Consultas reales a `buscar.py`:** firmas de los símbolos GML introducidos contrastadas
  contra el índice del runtime. Una firma disponible prueba nombre y aridad; no prueba
  ownership de buffers, autoridad de datos ni comportamiento de red.
- **`python3 -B _indice/validar-codigo-gml.py`:** código de salida **0**, sin funciones inventadas
  del runtime ni aridades incorrectas. Conservó dos avisos de nombres no resolubles sin el
  corpus opcional: `camera_set_view_pos_subpixel` y `display_write_all_specs`.
- **`git diff --check`:** código de salida **0** después de editar los capítulos.
- **Verificación de enlaces con Python 3.12:** código de salida **0**; 2036 rutas y 1638
  anclas válidas, sin rotas; 280 documentos sin secciones repetidas y 2307 citas numéricas
  resueltas. Se excluyen explícitamente 239 enlaces al manual/corpus opcionales ausentes.
  La primera llamada con el `python3` del sistema (3.9) falló al compilar una expresión
  regular con grupo atómico; se repitió con el intérprete compatible, sin modificarlo.

En esta auditoría no se ejecutaron GameMaker, red loopback, Steam Cloud ni mediciones de
píxeles. Los escenarios nuevos son planes reproducibles, no pruebas funcionales realizadas.
La compilación de bloques y cualquier fixture ejecutada durante la integración deben quedar
en su recibo correspondiente, con el artefacto y entorno utilizados.

## 4 · Fuentes primarias y fecha

Consultadas el **11-10-2026**. Las citas de manual son LTS; las release notes se usan para
distinguir fechas y canales, no para actualizar automáticamente el runtime de un proyecto.

- [Release notes LTS 2026.0](https://releases.gamemaker.io/release-notes/2026/0.html):
  IDE `2026.0.0.16` y runtime `2026.0.0.23`, referencia mantenida.
- [Release notes Beta 2026.100](https://releases.gamemaker.io/release-notes/2026/100.html):
  release 5, IDE 1139/runtime 1090, 27-08-2026; release 6, IDE 1142/runtime 1093,
  02-09-2026; release 9 disponible al consultar, IDE 1171/runtime 1116, 07-10-2026.
  Una instantánea del 07-09 no se transforma retroactivamente en la última disponible.
- [Async Networking LTS](https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Async_Events/Networking.htm):
  `succeeded`, ID del peer, buffer temporal y límites del aviso de desconexión al cliente.
- [Networking LTS](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Networking/Networking.htm)
  y [network_send_raw](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Networking/network_send_raw.htm):
  familias normal/raw, cabeceras, fronteras del flujo TCP y resultado del envío.
- [Steam Cloud](https://partner.steamgames.com/doc/features/cloud?l=english) y
  [documentación de GMEXT-Steamworks fijada a `b49d4c3`](https://github.com/YoYoGames/GMEXT-Steamworks/blob/b49d4c3af7b9850ab7fd4a54d2eee04d666e4808/docs/cloud.js):
  controles de app/cuenta, caché, resultado de escritura y configuración por plataforma.
- [CLDR 48 — reglas de plural](https://www.unicode.org/cldr/charts/48/supplemental/language_plural_rules.html)
  y [especificación de plurales](https://cldr.unicode.org/index/cldr-spec/plural-rules):
  categorías y operandos; el helper documenta su subconjunto, no implementa todo CLDR.
- [UAX 29 — segmentación](https://www.unicode.org/reports/tr29/) y
  [UAX 9 — bidi](https://www.unicode.org/reports/tr9/): límites de grafema y orden bidireccional.
- [RFC 2104 — HMAC](https://www.rfc-editor.org/rfc/rfc2104): autenticación mediante clave;
  no convierte un checksum público en firma.
- [WCAG 2.2 — tres flashes o bajo el umbral](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html)
  y [XAG 118 — fotosensibilidad](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/118):
  composición visible, transiciones, umbrales y patrones que requieren revisión adicional.

El resultado útil es un conjunto de contratos corregidos, pruebas que pueden repetirse y
límites expresos. Una biblioteca extensa necesita seguir contrastándose con la versión y
el producto de cada consumidor; esta revisión finita no autoriza llamarla infalible.
