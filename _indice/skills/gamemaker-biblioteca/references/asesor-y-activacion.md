# Activación y asesoramiento

Lee esta referencia al iniciar un juego, antes de una decisión costosa de revertir o cuando
el trabajo se estanque. El integrador consulta; el asesor recibe un encargo de lectura,
devuelve su recomendación y termina esa consulta. Este protocolo no le encarga otro asesor.

## Activar por intención y cargar por fase

«Quiero hacer un juego con GameMaker», «Game Maker», GML, `.yyp`, `gm-cli`, «hazme un juego»
y «no compila» deben llevar a la entrada de esta skill sin pedir al usuario su nombre.
La descripción permite que el harness la seleccione; no garantiza la decisión de cualquier
modelo. Copiar el paquete, verlo en catálogo, cargarlo y seguirlo son estados distintos.

El usuario puede pedir solo requisitos o una explicación: usa el procedimiento pertinente
sin sondear GameMaker ni recorrer toda la biblioteca. Antes de citar una firma, recomendar
API u operar el motor sí se aplica entorno/fuentes y la referencia de esa operación.
Una firma GML puntual necesita verificación de API; no una consulta arquitectónica.

Esta entrada enruta las fases. Los nombres Matt, Gentle y otras metodologías en las
referencias identifican procedimientos compatibles; no ordenan instalar paquetes ni lanzar
todos sus agentes. Reutiliza el método disponible y los contratos portátiles de esta skill.

## Cuándo consultar automáticamente

| Situación | Pregunta que debe resolver el asesor |
|---|---|
| Nuevo juego, antes de comprometer arquitectura o crear recursos | ¿Qué requisito, riesgo o decisión inicial puede obligar a rehacer el juego? |
| Decisión costosa de revertir: guardado/esquema, multiplayer, plataforma, pipeline o fronteras compartidas | ¿Qué alternativa encaja mejor con las restricciones y qué prueba distingue las opciones? |
| Hipótesis repetida sin progreso, fallos recurrentes o evidencia contradictoria | ¿Qué explicación alternativa falta y cuál es la siguiente prueba que la puede refutar? |

Si ya existe asesoramiento vigente para la misma decisión, úsalo. Reabre la consulta
cuando cambien sus requisitos, entradas o evidencia relevante. Una continuación rutinaria,
un cambio pequeño con reproducción clara o una consulta de documentación no la disparan.
Una incertidumbre que afecta a varias escenas, persistencia o aceptación sí puede hacerlo.

## Elegir el mecanismo disponible

1. **Ejecuta la consulta**, también si el resultado inicial será un conjunto de preguntas:
   el asesor identifica riesgos y requisitos omitidos antes de dar por cerrado ese conjunto.
   No basta con leer esta referencia ni anunciar que se consultará más adelante.
   Este procedimiento pide explícitamente delegar un subagente de solo lectura.
   Reutiliza el rol asesor/arquitecto o mecanismo de delegación ya disponible y autorizado
   para esta tarea. Encárgale solo lectura, con fronteras y salida concretas; no crees otro
   rol equivalente ni instales un harness para resolver la consulta.
2. Si existe delegación genérica, puede ejecutar el mismo contrato. Pasa un contexto fresco
   con el brief y fuentes pertinentes. Evita heredar el historial completo cuando el host
   permita pasar un encargo autónomo y ese historial no sea necesario.
3. El advisor nativo de Claude es una opción si ya está configurado/autorizado y disponible.
   Usa una sola vía de asesoramiento por decisión. Activar o reconfigurar `/advisor`,
   `advisorModel`, flags, modelos o proveedores mantiene su autorización específica.
4. Sin delegación, permiso o cuota, registra **autorrevisión, sin asesor independiente**,
   aplica el checklist con fuentes/prueba directa y continúa lo autorizado. Una decisión
   bloqueada por información o permiso reales conserva ese estado; no inventes una consulta.

La lectura solicitada al asesor no es un sandbox. Usa restricciones de herramientas
disponibles; si no hay aislamiento real, decláralo y conserva los permisos del encargo.
El asesor no escribe `.yy`/`.yyp`, no compila concurrentemente ni toca recursos compartidos.

## Modelos y roles del usuario

Conserva modelos, proveedores, esfuerzo y roles elegidos por el usuario para principal,
implementador, asesor y crítico. Un asesor configurado con otro modelo por decisión del
usuario sigue esa elección. No lo conviertas a «inherit» ni a un alias distinto para ahorrar.
Si no existe elección específica, solicita heredar el modelo actual mediante la API real.

**Omitir `model` no demuestra herencia.** Claude Code puede aplicar un default ambiental;
`model: inherit` en una definición solicita el principal, y un parámetro de invocación puede
prevalecer. Codex puede resolver defaults `[agents]`, valores de spawn y archivos de agente.
Comprueba la identidad efectiva que exponga el host y registra el resultado. Si no puedes
verificarla, informa **herencia no verificada**; conserva configuración y no sustituyas modelos.
Fuentes: [Claude](https://code.claude.com/docs/en/sub-agents),
[Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents).

El [advisor nativo Claude](https://code.claude.com/docs/en/advisor) es experimental y recibe
el transcript completo; cada consulta lo procesa de nuevo sin caché propia. Su momento de
invocación depende del modelo y no tiene un límite configurable de llamadas. Los subagentes
pueden heredarlo: la instrucción de no consultar otro asesor reduce cascadas, no impone un
límite técnico. No atribuyas consulta efectiva a su mera configuración.

## Brief y resultado verificable

Envía una pregunta decisiva y el paquete mínimo suficiente. Empieza por un resumen corto;
enlaza los archivos concretos y fragmentos necesarios. Amplía solo cuando una omisión impida
decidir con calidad. Una biblioteca entera o un transcript completo no son el paquete por defecto.

```text
ASESORÍA: decisión/ID y revisión; motivo: inicio, decisión costosa o atasco.
Objetivo y restricciones del usuario; decisiones fijadas y preguntas pendientes:
Motor/runtime/target conocidos; marca lo que todavía no se ha confirmado:
Spec/contratos y fuentes pertinentes, con rutas/revisión:
Opciones consideradas; intentos, resultados y evidencia que contradice la hipótesis:
Permisos, frontera de solo lectura y presupuesto autorizado:
Pregunta decisiva:
Salida: recomendación razonada, alternativa relevante, riesgo, dato pendiente,
prueba discriminante y condición para revisar el consejo. No delegar de nuevo.
```

Pide una recomendación breve con evidencia suficiente; una aclaración sobre dato nuevo
puede completar la consulta. El asesor distingue hechos, inferencias y propuestas, y cita
qué consultó realmente. No responde por el usuario a requisitos todavía abiertos.
No encadenes asesores hasta conseguir acuerdo ni reinicies sin novedad una consulta agotada.
Si hace falta investigar más, concreta otra pregunta y su prueba dentro del alcance autorizado.

El integrador contrasta el consejo con spec, fuentes y pruebas. Adopta, adapta o rechaza
cada punto relevante con una razón verificable. Un resultado favorable no concede aceptación,
no cambia requisitos y no sustituye compilación, runtime, crítica válida ni experiencia humana.

Registra en el tracker o recibo existente, sin otra memoria paralela:

```text
ASESORÍA ID/revisión y motivo; entradas/rutas/huellas:
Mecanismo y agente/sesión reales; modelo efectivo o límite de verificación:
Llamada y respuesta observadas; estado: recibido, rechazado, indisponible o autorrevisión:
Consejo y fuente; decisión del integrador y evidencia que la sostiene:
Pendiente/prueba siguiente; tokens y duración si el host los informa:
```

Una llamada nativa con respuesta acredita consulta; «he consultado» en texto no basta.
En Claude, `Advising` distingue reviewed, declined y unavailable; en delegación, conserva
llamada, ID real y resultado. En Codex usa sus eventos/rollout de herramientas, según versión.
Un archivo leído o una huella cotejada acredita acceso, no comprensión ni consejo correcto.

## Asesor inicial y crítico final

El asesor ayuda a escoger un enfoque y puede conocer las alternativas del constructor.
La crítica ciega final evalúa un objetivo inmutable en **otro contexto fresco**, con
controles negativos e idénticos válidos. Conserva fuera de ese paquete el consejo inicial,
las justificaciones del constructor y las claves. No reutilices el asesor contaminado como
juez ciego. La crítica sigue desarrollo/evidencia y QA/entrega; no requiere otra skill instalada.

## Comprobar la activación

La prueba natural usa la petición GameMaker sin nombrar esta skill y conserva llamadas de
carga, referencias y asesoramiento. Incluye una consulta ajena y una firma GML puntual como
controles de sobreactivación. Compara configuración, versión y modelo efectivos, y conserva
fallos/omisiones. Un catálogo correcto o una respuesta textual no prueba la ruta completa.
Tras actualizar, comprueba visibilidad en el harness; su recarga depende de la versión y
del componente. No reinicies procesos ni cambies configuración del usuario para ocultar un fallo.
