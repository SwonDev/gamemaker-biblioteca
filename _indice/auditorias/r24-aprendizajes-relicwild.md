# r24 · Aprendizajes de Relicwild para el desarrollo GameMaker con IA

Consulta: **15-10-2026**, exclusivamente de lectura. Relicwild World sigue pausado por
orden expresa del usuario; no se han ejecutado sus herramientas, scripts, juego, builds,
colas ni servicios. Este informe abstrae prácticas y errores de documentación privada:
no incorpora código, assets comerciales, credenciales ni permisos de aquel proyecto.

**Resultado:** la biblioteca ya tiene desarrollo guiado por especificación y un gauntlet
considerable en `13/28` y `13/29`. Conviene reforzar su gobierno y sus oráculos, no crear
otro método paralelo. Relicwild aporta tanto prácticas útiles como contraejemplos: pruebas
numerosas, una crítica válida o una mejora aislada no acreditan fidelidad ni juego acabado.

## 1. Qué se pudo comprobar y qué sigue sin demostrarse

Las fuentes R1–R12 del final identifican los archivos y fragmentos exactos consultados.
«Ejecutado» en esta tabla significa **registrado en recibos históricos leídos**, no una
repetición realizada durante esta investigación.

| Nivel de evidencia | Hecho observado | Límite |
|---|---|---|
| Intención documentada | Ítems verticales, hipótesis, integración, crítico separado, controles y recibos; un auxiliar por defecto y una tarea pesada a la vez [R2] | Prescribirlo no demuestra cumplimiento en cada encargo |
| Ejecución histórica acotada | Botín: persistencia entre dos procesos, controles, simulación y capturas; su recibo conserva fallos generales y conexiones todavía pendientes [R5] | Banco y catálogo no equivalen a integración ni balance final |
| Ejecución histórica acotada | Lote artístico: cuatro candidatos aprobados, dos rechazados y cero instalaciones; se conservan intentos inválidos y versiones [R8] | Aprobación de una regla artística concreta, sin aceptación global del juego |
| Ejecución histórica incompleta | Cierre: batería anterior con 1116 correctas y 12 fallidas; otra batería interrumpida; cargas de 32–57 s y copias experimentales sin promover [R3] | No existe verde global actual; unitarias positivas no cierran el defecto real |
| Decisión posterior vigente | Nuevo mandato de fidelidad literal que exige revalidar las aprobaciones anteriores [R4] | El hito nuevo no está ejecutado ni aprobado por existir su matriz |

La cabecera actual de `ESTADO.md` advierte que sus tablas inferiores son históricas; aun así,
conviven allí texto de preparación y resultados posteriores. Es un riesgo de recuperación
de contexto, no prueba de que todo recibo sea incorrecto. Leer primero pausa y autoridad
vigente permite resolverlo [R1].

## 2. Diferencias que merece la pena integrar

| Aprendizaje | Evidencia y riesgo | Ajuste generalizable a GameMaker |
|---|---|---|
| **Separar fidelidad, preferencia y calidad propia** | El método artístico puntuaba un original como «ancla baja» y afirmaba haberlo superado; el mandato posterior exige equivalencia observable con el original [R4, R6] | Fijar por dominio qué fuente decide: aspecto, manejo, reglas, audio. Una nota de gusto no demuestra equivalencia; una mejora deliberada conserva su diferencia documentada |
| **Una muestra aceptada no redefine todo el producto** | Un modelo concreto pasó a ser canon y criterio relativo para familias diferentes; el propio método detectó después mezcla de dominios al medir una casa con panel de criaturas [R6] | Registrar alcance del ancla: familia, escenario, versión, tamaño aparente y ejes aplicables. No extender automáticamente su aceptación a otros dominios |
| **Una regla vigente inequívoca** | El método conserva un mínimo inicial de diez ciclos, mientras una entrega posterior registra aprobados con tres o cuatro; v2 instalaba la mejor versión tras suspenso y v3 lo prohíbe expresamente [R6, R8] | Cabecera con versión vigente y reglas normativas breves; historial separado o marcado como sustituido. Cada recibo identifica versión de spec, rúbrica y regla de promoción |
| **El presupuesto limita el intento, no rebaja la aceptación** | El usuario corrigió la interpretación de «no iterar eternamente»: no quería instalar resultados deficientes. v3 permite una corrección y exige aprender antes de reconstruir [R6] | Al agotar intentos, conservar rechazo, causa y trabajo; cambiar hipótesis o método y continuar lo independiente. No promover por agotamiento ni renombrar el fallo como deuda aceptada |
| **Aprender de lotes con dueño** | Apéndices por lote registran causa, control y siguiente regla sin sobrescribir el método compartido reservado por otro agente [R7, R8] | El trabajador entrega propuesta de regla y evidencia; un responsable consolida el procedimiento compartido después de revisión. Evitar que todos editen simultáneamente la skill o los validadores |
| **El bloqueo nominal no acredita aislamiento** | `EXCLUSIVO=1` protegía ventanas, pero coincidía una batería headless ajena [R9] | Definir qué recurso protege cada reserva: `.yyp`, `.gmcache`, runner, guardado, CPU/GPU. Registrar contendientes reales del intervalo; repetir rendimiento cuando el protocolo lo exija |
| **La pausa debe alcanzar a todo el trabajo propio** | Tres carriles podían reintentar hasta 72 veces y siguieron tras agotarse la cuota; había lanzadores y monitores huérfanos [R3] | Comprobar cancelación antes del despacho, después de esperas y reintentos; inventariar también procesos desacoplados con identidad atribuible. Cuota agotada y pausa humana son estados distintos |
| **La prueba debe alcanzar el evento, no solo durar** | Dos ventanas no compartían todo el intervalo jugando; viajes solicitados no eran llegadas; una foto «3 s» llegó a 7,356 s [R9, R10] | Registrar hitos de escenario y tiempo real: entró, actuó, llegó, guardó, salió. Un temporizador, una pulsación o un exit 0 no sustituyen el efecto observado |
| **El instrumento puede crear el fallo** | La primera sonda de audio liberaba objetos de un pool; un lanzador devolvía cero pese a error/interrupción; PNG completo no acreditaba escenario completo [R10] | Separar error del instrumento, control negativo y producto; exigir centinela final, código del motor e integridad de todas las salidas. Repetir en ruta nueva conservando el intento inválido |
| **La copia candidata tiene una puerta de promoción** | QA-033 conserva copias con pruebas positivas, pero no se instalaron porque carga, suelo visible y memoria seguían sin acreditar [R3] | Manifiesto de candidato, pruebas acotadas, integración autorizada y regresión de la unión. «Mejor que la base» y «cumple el requisito» son decisiones independientes |

## 3. Automejora sin feedback circular

Hay evidencia de aprendizaje útil: una causa observada se convierte en regla previa, control
y guía para el lote siguiente. También hay límites explícitos: el comprobador artístico
tenía calibración parcial; lint verde no detectaba toda la semántica de forma [R6–R8].

El riesgo más relevante está en ajustar simultáneamente candidato, rúbrica y juez sobre las
mismas muestras. Un lote repitió tres tandas inválidas porque el ancla superaba el techo;
después precisó la rúbrica antes de repetir con las mismas imágenes [R7]. Los recibos
conservan esa secuencia y no recalculan notas antiguas. **Esto no demuestra manipulación**,
pero tampoco demuestra que la rúbrica afinada generalice fuera de ese panel.

Protocolo recomendado para la biblioteca:

1. Congelar antes de la ronda requisito, fuente, rúbrica, imágenes, muestras y regla de decisión.
2. Registrar por separado fallo de acceso/transporte, calibración inválida, rechazo de calidad
   y ausencia de evidencia. Ninguno se convierte en otro por un resumen del agente.
3. No reesculpir ni corregir producto por un juicio inválido; diagnosticar primero el medidor.
4. Una modificación de rúbrica genera versión nueva y motivo prospectivo. No reetiquetar
   resultados previos ni probar la supuesta mejora solo contra los casos que la motivaron.
5. Reservar ejemplos independientes del mismo dominio para validar la regla aprendida.
   Mantener controles de defecto, A/A y un caso válido; un ancla identificable no garantiza ceguera.
6. Someter el aprendizaje propuesto a un revisor que no lo escribió. Automatizar únicamente
   defectos objetivables; conservar juicio sensorial y prueba del comportamiento real.
7. Promover la regla tras demostrar un caso correcto y uno defectuoso, documentando sus
   falsos positivos, cobertura pendiente y condiciones de invalidez.

El original de referencia no debe calificarse obligatoriamente como malo para que una
prueba de **fidelidad** sea válida. Puede servir como comparación de un eje concreto; el
ancla negativa debe representar un defecto conocido de ese eje. Las reglas de gusto del
contenido propio y la equivalencia con la referencia necesitan recibos diferentes [R4, R6].

## 4. Qué existe ya y dónde ampliar

Contraste realizado contra el contenido completo de `13/29` y las secciones de `13/28`.
Las localizaciones siguientes describen la revisión consultada; no son una nueva autoridad
sobre la API ni requieren arrastrar Godot, modelos, umbrales o número de agentes a GameMaker.

| Ya existe en la biblioteca | No duplicar | Mejora concreta |
|---|---|---|
| `13/28` §1.3–1.6, §2 y §3.1 | Preguntas resueltas, procedencia de decisiones, spec escrita y cambios de rumbo | Precisar referencia por versión y por dominio cuando «como X» sea central; distinguir mandato, supuesto delegado y propuesta |
| `13/29` §2.1–2.2 | Spec → tareas verticales → implementar → integrar → revisar; selección Matt/Gentle por fase | Añadir versión/huella de spec y criterio al encargo y al recibo; invalidación explícita por cambio de autoridad |
| `13/29` §3–5 | Hipótesis, estancamiento, crítico fresco, claves separadas, A/A y controles del dominio | Añadir gobierno de cambios de rúbrica, deriva del juez y validación independiente de la regla aprendida |
| `13/29` §6 y §10 | Recibos por revisión, salida incompleta, unidades, denominadores e instrumentación | Incorporar hitos efectivos del escenario y distinguir resultado de lanzador/motor/artefacto; diagnóstico no demuestra efecto en píxeles |
| `13/29` §7 y §13 | FIFO, propietario, pausa, reintentos y procesos atribuibles | Hacer explícito el inventario de descendientes desacoplados y el alcance real de cada exclusión; coste desconocido sigue desconocido |
| `13/29` §11–12 | Procedencia, fronteras, simulación, RNG y separación de banco/runtime | Añadir revisión de integración entre subsistemas y ejemplos de promoción bloqueada aunque existan pruebas locales verdes |
| Skill: desarrollo/evidencia y QA/entrega | Contratos portátiles; no depender de herramientas personales | Llevar solo reglas de decisión breves y enlazar el capítulo detallado. Comprobar recuperación fresca de la regla vigente, no solo enlaces/YAML |

En el encargo de botín, «propiedad exclusiva» coexistía con permiso de migración en archivos
de otro trabajador y la batería osciló durante edición concurrente [R5, R11]. Declarar esa
excepción ayuda, pero **no acredita exclusión**: reservar cada migración o entregarla al
integrador antes de ejecutarla. Las pruebas de componente conservan su valor; la batería
global exige identificar un conjunto estable de entradas y su cobertura real.

## 5. Fuentes primarias privadas y alcance de la trazabilidad

Rutas relativas a la raíz privada de `Relicwild_World`; los números de línea
identifican la lectura del 15-10-2026. Se citan como procedencia local, sin enlazar documentos
privados desde el paquete público ni reproducir sus datos ajenos a este aprendizaje.

| ID | Archivo y fragmento exacto | Qué respalda |
|---|---|---|
| R1 | `RESUME.md:3–24`; `AGENTS.md:3–17`; `ESTADO.md:3–7`; marca `PARAR_ORQUESTADOR` | Pausa vigente, cambio de autoridad, preservación y tablas históricas |
| R2 | `docs/operacion/PROTOCOLO-GAUNTLET.md:7–47`; `docs/operacion/EQUIPO-Y-COSTE.md:16–44` | Intención de ítems, reparto, coste, contexto y exclusión |
| R3 | `docs/qa/CIERRE-ORDENADO-20261014.md:5–17,24–44` | Reintentos, huérfanos, parada, candidatas, fallos y límites del cierre |
| R4 | `docs/plan/MANDATO-FIDELIDAD-LITERAL-20261014.md:7–23,44–54` | Fidelidad por dominio, comparación equivalente, revalidación y trabajo no iniciado |
| R5 | `evidencia/p05/botin_v2/RECIBO.md:54–90,124–161` | Pruebas, concurrencia, integración pendiente y límites de aceptación |
| R6 | `docs/plan/METODO-ESCULTOR-VOXEL.md:46–106,177–243,245–296` | Evolución de criterio, anclas, ruido, v2/v3 y calibración parcial |
| R7 | `docs/plan/METODO-ESCULTOR-VOXEL-B2-MORSA.md:19–36,47–73` | Aislamiento, tandas inválidas, rúbrica prospectiva y aprendizaje con límites |
| R8 | `docs/qa/TURNO-B-morsa_colmillo_helado.md:3–48,61–70` | Aprobados/rechazados, cero instalaciones, controles y cobertura acotada |
| R9 | `docs/qa/TURNO-A1.md:13–44` | Hitos, capturas, crítica, ruido concurrente y evidencia incompleta |
| R10 | `docs/plan/METODO-ESCULTOR-VOXEL-A1.md:7–25` | Errores del medidor, tiempo real, semántica de rúbrica y contadores |
| R11 | `docs/plan/ENCARGO-CODEX-BOTIN-V2.md:12–35,66–98` | Propiedad, excepciones de migración, otros escritores y entrega |
| R12 | `docs/operacion/CRITICO.md:3–44`; `docs/plantillas/REGISTROS.md:7–73,95–100` | Contratos de juicio y trazabilidad; plantillas no son ejecución |

La lectura acredita que esos documentos y recibos contienen lo señalado; no revalida sus
huellas, imágenes, ejecutables ni resultados históricos. El informe no demuestra perfección
de la metodología, ahorro cuantificado, cumplimiento en todas las plataformas ni finalización
de Relicwild. Sus lecciones deben probarse al aplicarlas a un proyecto GameMaker autorizado.
