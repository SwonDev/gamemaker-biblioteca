# Desarrollo con IA — orquestación, crítica y evidencia

> **Metodología para cualquier proyecto GameMaker asistido por IA, nuevo o existente.**
> Cómo mantener contratos, datos, assets, pruebas y decisiones coherentes cuando trabajan
> varias personas o agentes. Método generalizado de un desarrollo prolongado con IA, contrastado
> con sus reglas, historial, encargos, herramientas y recibos hasta el 11-10-2026.
> La trazabilidad y los límites están en [las pruebas de la biblioteca](../_indice/auditorias/r21-publicacion.md).
> El proyecto fuente seguía pausado: esta lectura no certifica su revisión actual.

No sustituye la [especificación inicial](<28 - De hazme un juego a una especificación - el protocolo de elicitación del agente.md>),
la [arquitectura](<06 - Arquitectura de un proyecto GameMaker.md>) ni el
[manual operativo del CLI](<../12 - Utilidades e integraciones/09 - Manual del agente de IA - operar GameMaker con gm-cli.md>).
Los conecta: aquí vive el contrato de trabajo; allí, las API y los procedimientos técnicos.
Los umbrales visuales, el hardware y los modelos del caso son decisiones de aquel proyecto,
no requisitos universales para GameMaker.

## 1 · Antes de actuar: recuperar el encargo real

En un proyecto existente, lee primero reglas, especificación, glosario, dirección visual,
matriz de requisitos, estado y punto de pausa. Comprueba checkout, revisión y cambios locales.
El orden de precedencia debe estar declarado: una entrega de agente o un log nunca revoca
una orden del usuario. Una pausa explícita sigue vigente aunque el supervisor tenga trabajo.

Haz un inventario de lo que existe antes de crear otra implementación: sistemas, herramientas,
assets, pruebas y documentación. Incluye los cambios locales y los archivos ajenos al encargo.
Para cada pieza distingue **planificada, construida, integrada, accesible, probada y aceptada**.
Un catálogo de mil entradas no acredita mil personajes jugables: comprueba archivo, carga,
selección y presencia en la escena. Tampoco una herramienta verde acredita el producto.

La inspección de un proyecto pausado autoriza leer; arrancar runners, pruebas, colas o agentes
necesita que el usuario haya autorizado retomar esa actividad. Una actualización de la
biblioteca no reanuda por sí sola el juego del que aprendió.

## 2 · Contratos permanentes y una orden corta

Una orden de bucle debe señalar los contratos, no intentar contener todo el proyecto.
Usa documentos con responsabilidades distintas:

| Documento | Pregunta que resuelve | Quién puede cambiar el criterio |
|---|---|---|
| Especificación y matriz de requisitos | ¿Qué debe poder hacer el jugador? | El usuario para cambios de alcance |
| Glosario | ¿Qué significa cada concepto del juego? | Responsable de dominio, dejando la decisión |
| Dirección visual | ¿Qué identidad, referencia y resolución se conservan? | Responsable autorizado; no un generador por defecto |
| Reglas operativas | ¿Cómo se escribe, prueba e integra aquí? | Responsable del proceso dentro del encargo |
| Estado y diario | ¿Qué está integrado, bloqueado, pendiente y probado? | Integrador, con recibos |
| Encargo de una pieza | ¿Quién posee qué archivos y qué debe demostrar? | Integrador y constructor |
| Decisión técnica | ¿Por qué se eligió esta solución y qué se descartó? | Responsable de esa decisión |

Cada requisito debe tener ID estable, criterio observable, prueba, artefacto y estado.
Distingue obligatorio, aceptado con limitación y pendiente. Cambiar un porcentaje o eliminar
una prueba para conseguir verde cambia el contrato y necesita autorización.

Una orden útil contiene objetivo, rutas de contratos, revisión de partida, límites de
actuación, siguiente puerta y criterio de parada. Al terminar una ronda, el agente debe
escribir en la conversación el delta comprobado y el siguiente bloqueo: algunos evaluadores
solo reciben esa conversación. Un enlace a un log sin su resultado puede dejarles sin señal.
Los límites y comandos de cada harness se consultan en su versión real; no se convierten
los límites históricos de un harness en una API permanente.

### 2.1 Desarrollo guiado por especificación: del encargo al requisito probado

El método se adapta al género, plataforma y tamaño. Un juego nuevo empieza con
`13/28`; una continuación reutiliza especificación y decisiones vigentes. Una corrección
pequeña necesita un contrato acotado, no rehacer un GDD. No se impone el arte, el formato 3D,
la cantidad de agentes o el hardware del caso estudiado a otro juego.

| Fase | Trabajo y artefacto | Puerta para avanzar |
|---|---|---|
| Recuperar/explorar | Reglas, inventario, glosario, diseño, estado, revisión y permisos | Distinguir lo existente, duplicado, pendiente y pausado |
| Aclarar | Preguntas agrupadas solo sobre decisiones que faltan; contexto de dominio | Encargo observable, supuestos visibles y alcance autorizado |
| Especificar | Problema, solución, historias/casos, contratos, restricciones, fuera de alcance y decisiones de prueba | Documento escrito y mostrado; requisitos con ID y criterio medible |
| Partir en tareas | Piezas de extremo a extremo con dependencias, dueño y aceptación | Cada pieza demostrable; fronteras compartidas e integrador identificados |
| Prototipar si hay incertidumbre | Experimento acotado que contesta una pregunta de lógica o aspecto | Resultado y decisión; el prototipo no se convierte por omisión en producto |
| Implementar | Frontera existente preferida; API verificada; prueba significativa antes de corrección cuando corresponda | Rojo real por el defecto, verde por el comportamiento requerido |
| Integrar | Contratos entre sistemas, recursos compartidos, datos/derivados y migraciones | Unión accesible y comprobada; no heredar el verde de una rama |
| Revisar y aceptar | Diff contra spec/normas, controles, runtime, crítica y presupuesto aplicables | Recibo vigente por requisito; sentidos o plataformas pendientes declarados |
| Evolucionar | Estado, matriz y ADR cuando cambia una decisión | Criterio anterior conservado; cambio de alcance autorizado |

Las tareas verticales entregan comportamiento completo, por ejemplo seleccionar, confirmar,
persistir y volver a cargar una opción, con su error y prueba. No dejes «toda la UI» y «todo
el guardado» como ramas que no pueden demostrar nada solas. Un cambio mecánico con alcance
muy amplio puede requerir expandir → migrar consumidores → retirar el contrato antiguo;
no fuerces piezas independientes si solo la unión puede quedar verde.

La especificación describe decisiones y comportamiento; el encargo de implementación concreta
rutas actuales, propiedad y controles. Así se evita que una spec estable dependa de números de
línea caducados. Cada requisito conecta tarea, implementación, prueba, evidencia y estado.
Un fallo nuevo vuelve a la hipótesis y al requisito afectado, no se esconde cambiando su texto.

Si cambia una decisión, registra motivo, alternativas, consecuencia, fuente y qué evidencia
invalida. Mantén la documentación junto al cambio autorizado; no declares aceptación antes
de que el juego satisfaga la spec vigente. La envoltura del juego completo se comprueba con
`04/00`: menú, opciones, pausa, persistencia, fin, créditos, entrada, sonido y distribución
según el alcance. El género no justifica olvidarla.

### 2.2 Skills por intención y fase, con un procedimiento portátil

El agente selecciona y carga las skills pertinentes; el usuario no necesita invocarlas.
Comprueba catálogo y versión del harness, lee su `SKILL.md` antes de aplicar el procedimiento
y registra qué decisión o comprobación aportó. Los nombres de la tabla identifican el perfil
estudiado: en otro harness pueden tener namespace o equivalentes. Esta biblioteca no instala
esos paquetes externos ni depende de rutas personales; los contratos de este capítulo siguen
siendo consultables si falta una skill. Informa la capacidad ausente sin simular su ejecución.

| Intención/fase | Skills del método | Resultado esperado |
|---|---|---|
| Idea o requisitos ambiguos | `grill-with-docs`, `domain-modeling`; `ask-matt` para elegir flujo | Contexto/glosario y decisiones que faltaban, sin repetir preguntas resueltas |
| Especificación y tareas | `to-spec` → `to-tickets` | Spec y dependencias por comportamiento; tracker local si no se autoriza publicar |
| Construcción | `implement` + `tdd`; `gamemaker-biblioteca` y `gamemaker-expert` para el motor | Fronteras claras, símbolos verificados y pruebas del contrato |
| Fallo o lentitud | `diagnosing-bugs`; `research` para fuentes | Reproducción, causa, hipótesis y corrección comprobada |
| Arquitectura o incertidumbre lógica | `codebase-design`, `mp-prototype` | Contratos de módulo o experimento descartable antes de expandir |
| Visual, HUD, menús y arte | `antislop` + `antislop-ui` primero; `ui-ux-pro-max`, `design-md` | Identidad/tokens en DESIGN, estados y criterios visuales explícitos |
| Movimiento y pulido | `emil-animate`, `review-animations`, `emil-design-eng`; `impeccable` cuando corresponda | Interrupción, ritmo, jerarquía y feedback probados en juego |
| Modelo/asset 3D real | `imagegen` + `img2threejs`; `vgpu` para escenas/exportación | Referencia autoritativa, regiones inferidas, pasadas y validación multiángulo |
| Localizar/clasificar contenido | `embeddinggemma` y búsqueda literal | Fuentes relevantes con procedencia y contexto acotado; véase 12/11 |
| Aislamiento o trabajo independiente autorizado | `using-git-worktrees`, `dispatching-parallel-agents` | Propiedad y recursos separados; WIP y modelos conservados |
| Revisión normal y prueba de entrega | `mp-code-review`, `verification-before-completion` | Scope y normas contra spec, comandos reales y límites |
| Riesgo que requiere doble juicio | `judgment-day` cuando el encargo lo requiera | Crítica independiente y controles; no añade permisos |
| Conocimiento y continuidad | `writing-for-agents`, `writing-skills`; `handoff` solo si se pide | Reglas consultables, consulta fresca y checkpoint recuperable |

Los nombres `mp-code-review` y `mp-prototype` corresponden a Codex; otros harnesses pueden
llamarlos `code-review` y `prototype`. Carga también especialidad y comprobaciones del target
real. `shadcn` corresponde a frontend compatible, no a un HUD GML. No arrastres herramientas
web, Apple o 3D a un proyecto que no las necesita. Las puertas visuales del perfil —anti-slop,
StyleSeed o equivalentes— se ejecutan sobre píxeles reales con el criterio del proyecto;
ausencia de herramienta se declara, no se convierte en aprobación inventada.

Las reglas del proyecto y las instrucciones del usuario conservan precedencia sobre una
skill: modelos, autorizaciones, pausa, alcance, WIP y credenciales. Un paso de skill que dice
«commit», «publicar tickets» o «limpiar» no autoriza esa operación por sí mismo. Reutiliza
requisitos ya acordados y continúa lo autorizado; pide solo la decisión o permiso que falta.
No hagas una ceremonia de aprobación para cada paso rutinario ni reduzcas pruebas para seguir.

## 3 · El ciclo: una hipótesis y una diferencia observable

1. Localiza el bloqueo que impide el siguiente requisito, con evidencia vigente.
2. Formula una hipótesis falsable y una modificación acotada.
3. Reserva archivos y recursos; conserva un estado de referencia recuperable.
4. Construye la pieza. Para GML, verifica símbolos y valida antes de compilar.
5. Prueba primero el contrato de la herramienta y después el comportamiento en el juego.
6. Compara contra la referencia y solicita crítica independiente cuando corresponda.
7. Integra solo bajo la autorización y las puertas del proyecto. Revalida lo que la
   integración pudo cambiar; las pruebas de una rama no acreditan automáticamente la unión.
8. Registra resultado, revisión, límites y bloqueo siguiente; repite con una hipótesis nueva.

Si varias rondas no mejoran una medida válida, cambia de enfoque: inspecciona la frontera,
reduce a un caso reproducible o mide otra hipótesis. No repitas la misma generación esperando
que el azar dé una aprobación. El número de rondas sin progreso se fija en el encargo; las
cuatro rondas del caso estudiado son una elección, no una ley del motor.

Un fallo de control, una prueba incompleta y un resultado negativo son tres estados distintos.
Conserva todos. Nunca selecciones solo las pasadas favorables ni retires una prueba fallida
sin corregir su causa o documentar que el criterio cambió con autorización.

## 4 · Constructor, integrador y crítico

El constructor recibe propósito, referencia, archivos que posee, entradas/salidas, presupuesto,
puertas y formato de entrega. No revierte WIP ajeno. No toca recursos compartidos ni fusiona
porque «su prueba pasa» si esa atribución corresponde al integrador.

El integrador coordina las fronteras, registra los recursos y evalúa la combinación. En
GameMaker, hay **un solo escritor del `.yyp`** y exclusión para compilar/ejecutar/empaquetar
contra la misma `.gmcache`: el mecanismo y las carreras demostradas están en las trampas
19–20 del manual del CLI. Un worktree separa archivos, no separa el guardado ni una GPU.
No des por independientes dos agentes que comparten cualquiera de esas cosas.

Una operación de ResourceTool puede reescribir recursos ajenos al objetivo. Inventaría y
coteja toda su frontera de mutación, con instantánea de bytes previa y escritor único;
comparar solo el recurso pedido o restaurar por diferencias de Git no protege WIP concurrente.
Comprueba también identidad lógica: carpeta y nombre pueden identificar un archivo incluido,
aunque un subcomando lo busque solo por nombre. Rechaza ambigüedad antes de borrar.

El crítico evalúa el entregable con contexto fresco. Antes del veredicto recibe el criterio,
la referencia y evidencias comparables. No recibe la explicación persuasiva del constructor,
su código, sus conclusiones ni la clave que identifica la versión nueva. Después del juicio
puede recibir contexto para diagnosticar. Comprueba también la identidad del modelo/juez elegido:
un endpoint sano no demuestra pesos, revisión ni configuración correctos. Si vio la clave o discutió la solución antes de
juzgar, marca la ronda contaminada y repite con otro paquete y contexto fresco.

En un trabajo pequeño una persona puede construir e integrar; la independencia del juicio
sigue teniendo valor. No inventes agentes ni cambies los modelos elegidos para cumplir una
plantilla. Cantidad, modelos y permisos de los agentes los fija el encargo vigente.

## 5 · Crítica visual: aislar también los archivos

Prepara pares A/B con nombres neutros, orden aleatorio, misma cámara, resolución, iluminación,
pose y recorte. Guarda la clave **fuera del directorio accesible al crítico**, con acceso
separado cuando sea posible. Ocultarla en las instrucciones mientras el archivo está a su
alcance no es aislamiento. Los metadatos, el nombre del archivo y los bordes también pueden
revelar qué versión está mirando. Sella el recibo del juicio antes de desvelar la clave;
conserva sus notas originales y registra por separado cualquier explicación posterior.

Incluye controles: un defecto conocido que deba detectar, una pareja idéntica que deba
empatar y, cuando corresponda, una referencia independiente. El control no debe reutilizar
los mismos bytes identificables del par evaluado: reconocer una imagen de control puede
revelar la clave. Registra el orden y las huellas del paquete antes de abrirlo.

Un control fallido invalida la medición de esa ronda. Un crítico que elige bien un par no
queda calibrado para toda clase de imagen: los controles deben representar el defecto que
se quiere medir. Ajustar umbrales con una tanda y evaluarlos sobre esa misma tanda no
acredita generalización: reserva casos independientes por familia. Guarda observaciones por
región, severidad y requisito, no solo una nota.

Hay dos decisiones distintas:

| Puerta | Comparación | Consecuencia |
|---|---|---|
| Integración de mejora | Último producto válido, mismos requisitos | Puede integrar una mejora autorizada sin degradar otras piezas |
| Aceptación final | Referencia y umbral del usuario para el hito | Permite declarar ese hito aceptado |

Mejorar respecto a ayer no demuestra aceptación final. Si un retrato antiguo era atractivo
pero representaba otra criatura, corrige la identidad y compara la nueva versión contra la
fuente correcta; la preferencia del crítico no autoriza conservar un error factual.
Una imagen convincente tampoco prueba entrada, sonido, legibilidad en movimiento o sensación
al jugar. Esas puertas necesitan evidencia del juego y, para juicio sensorial, del usuario.

## 6 · Evidencia que pertenece a una revisión

Cada recibo debe identificar qué se ejecutó y qué observó, incluyendo WIP. Una revisión de
Git sin las huellas de los cambios locales no identifica el código realmente probado.

| Campo | Contenido mínimo |
|---|---|
| Identidad | Commit, estado del árbol y manifiesto SHA-256 de entradas usadas |
| Entorno | CLI, runtime, target, VM/YYC, configuración y hardware relevante |
| Construcción | Comando, código de salida, log completo y huella del binario/paquete |
| Caso | Escenario, semilla, población, cámara, resolución, intervalo y entradas |
| Resultado | Aserciones, fallos, duración, salida incompleta y motivo |
| Evidencia | Rutas y huellas de capturas, datos, controles y recibos |
| Alcance | Producto normal o copia instrumentada; requisito que se está probando |
| Vigencia | Qué cambios invalidan esta prueba y qué sigue sin comprobar |

Minimiza los metadatos de evidencia antes de exportar o indexar: versiones y campos necesarios,
no el entorno completo heredado del proceso. Revisa argumentos, logs y trazas para excluir
credenciales y datos ajenos al encargo; restringe el acceso al bruto que deba conservarse.
Una huella permite atribución sin publicar el contenido sensible. No copies secretos a
recibos, paquetes de juez, agentes ni documentación para explicar un fallo histórico.

Declara qué significa el código de salida de cada instrumento. Algunos salen con 0 al
calibrar aunque las filas del producto no cumplan objetivo. Conserva por separado cobertura,
calibración y requisito aprobado, con aserciones nombradas y señal final inequívoca. Un CSV
sin los eventos esperados no demuestra ausencia de errores: puede no haber ejercido el caso.
Un pipeline de shell conserva el fallo de cada etapa; el último filtro o mensaje no convierte
un proceso fallido en éxito ni su invocación en pieza terminada.

El informe distingue **aserción, medición informativa y caso omitido**, con sus contadores
y el modo de ejecución. En el harness del caso, ciertos umbrales temporales solo decidían fallos
en modo de rendimiento; en modo normal una medida fuera del umbral podía aumentar el total
sin aumentar fallos. Por eso `total=N, fallos=0` no certifica por sí solo todos los presupuestos.
Conserva flags, recursos reservados, universo previsto y excepciones junto al resultado.

Cuando cambian una entrada, el runtime, una configuración, un asset derivado o el escenario,
la evidencia afectada pasa a **histórica**. Conserva el resultado anterior y ejecuta la puerta
necesaria cuando esté autorizado. Una compilación nueva no refresca la batería antigua.
Un porcentaje sin denominador, una captura sin origen y una salida cortada no son aprobación.

Una medida por máscara declara población por clase, área y confianza de alineación. Una clase
vacía no queda aprobada por autoigualdad; ausencia de observación no es cero del fenómeno.
Lee todas las celdas exigidas: una conclusión narrativa favorable no vence un eje perdido.
Si el instrumento usó una imagen reducida o el criterio equivocado, corrige el oráculo y
conserva la huella del candidato; no regeneres para acomodarlo a una medición inválida.

Un resultado histórico favorable no refresca una batería posterior incompleta. Ese cuidado forma parte del método: no escribir «todo verde» en la
revisión actual. Las tres capas de QA —herramientas, juego instrumentado y juicio del producto—
están desarrolladas en [Testing y QA](<10 - Testing y QA.md>).

## 7 · Máquina compartida y colas con propietario

Haz un inventario de recursos escasos: CPU, RAM, GPU, runner, Blender, disco, `.yyp`, `.gmcache`
y directorios de guardado. Decide qué trabajos pueden coexistir a partir de sus consumos,
no del número de agentes. La lectura o una simulación CPU puede avanzar mientras espera
su turno un render; dos jobs «distintos» pueden competir por la misma memoria.

Para trabajos pesados, define exclusión y cola FIFO, token de propietario y orden de adquisición
consistente. Por ejemplo, GPU → juego → Blender; otro sistema puede necesitar otro orden, pero
no órdenes opuestos entre participantes. Evita adquirir dos veces el mismo bloqueo heredado.
El tiempo de espera de la herramienta que transporta la orden debe cubrir la reserva: declarar
cuatro horas de cola sirve de poco si el transporte mata el comando antes. Prueba el límite
más corto de CLI, cliente, lote y transporte; verificar un parámetro aislado no acredita la espera.

Al migrar una cola, prueba todos sus consumidores: adquisición, herencia, transferencia,
cancelación y cierre, también con mezcla de Bash/Python si ambos participan. Una mejora del
proveedor no actualiza un cierre antiguo. Distingue reservas heredadas de propias, valida su
propietario y prueba error tras adquisición parcial; libera solo lo adquirido por esa operación.

Para admisión por RAM, registra presión actual y memoria disponible/recuperable con unidades.
El swap acumulado no demuestra por sí solo presión vigente. Un fallo al consultar el sistema
necesita estado explícito; un tope que termina procesos tampoco acredita recuperación del guardado.

Registra propietario, proceso y fecha de inicio. Un PID solo puede reutilizarse: coteja su
identidad antes de actuar. Una reserva vieja no justifica expulsar trabajo vivo. Expiración,
propietario muerto y proceso lento requieren políticas distintas. Si no puedes atribuir un
proceso al encargo, informa del bloqueo; no uses una limpieza por nombre global.

Si un trabajo autorizado consume créditos, fija presupuesto y registro antes de despacharlo.
Reserva el coste previsto de forma atómica bajo exclusión, contando también trabajos en vuelo;
comprobar saldo y escribir después permite que dos jobs excedan juntos el límite. Conserva
fallos/reintentos como consumo cuando el proveedor los cobre y separa estimación, reserva y
cargo confirmado. Si falta el registro requerido, bloquea despacho; no interpretas ausencia
como presupuesto ilimitado. La reserva no autoriza pagos, credenciales o modelos nuevos.

Al pausar: deja de despachar, permite que la operación autorizada alcance un punto seguro,
registra lo pendiente y confirma procesos/colas propios. No reinicies al perder una sesión ni
conviertas un marcador de parada en una tarea pendiente que el supervisor deba «arreglar».

## 8 · Disco: un worktree no es una copia de la máquina

Antes de generar ramas y copias, calcula qué incluye cada una. Excluye cachés regenerables de
las copias de prueba cuando la herramienta lo permita, sin modificar ni borrar el original.
No multipliques modelos, resultados intermedios y evidencia pesada en cada agente. Un conjunto
de entradas inmutable puede compartirse por lectura; las salidas deben tener propietario.

Mantén un manifiesto de origen, huellas, enlaces y metadatos necesarios. Preserva código,
WIP, assets, modelos, licencias, datos mutables, backups y evidencia antes de retirar copias.
Una restauración no está comprobada porque se creó el directorio: coteja contenido y enlaces.
Si no puedes conservar atributos requeridos, la copia no sustituye todavía al original.

En sistemas con clones o compresión, el tamaño lógico de carpetas no mide el espacio físico
recuperado. Comprueba el sistema de archivos antes/después. Ni un backup autorizado permite
borrar otra ruta, ni haber desarrollado en local autoriza acceso remoto o publicación.

## 9 · Pruebas que respetan el guardado y los procesos

Resuelve el guardado que usa el **ejecutable real**. En el caso macOS VM y YYC podían tener
rutas distintas; cambiar el directorio de trabajo o una variable de entorno no acredita
cambiar el guardado del motor. Consulta `game_save_id` y los archivos que crea la ejecución.

Antes de una prueba con escritura:

1. Identifica el directorio efectivo, todos sus archivos y los posibles escritores.
2. Evita escritores simultáneos y guarda una instantánea con huellas de todo el estado.
3. Ejecuta el caso acotado, registrando la identidad del runner y del lanzador.
4. Cierra solo los procesos atribuidos a esta prueba y verifica que dejaron de escribir.
5. Restaura y coteja la instantánea completa; conserva un recibo de la restauración.

Si fallan cierre o restauración, deja un marcador de recuperación pendiente y bloquea la
siguiente prueba que podría convertir el guardado contaminado en su «backup bueno».
No se sustituye el guardado del usuario con un fixture. La comprobación de persistencia incluye
cerrar y reabrir el proceso; inspeccionar una variable en memoria no demuestra persistencia.

El runner macOS puede quedar fuera del árbol del CLI. Por eso cerrar el lanzador no basta,
y matar por el nombre genérico puede cerrar el juego de otro encargo. Diseña adquisición y
cierre con identidad verificable y recuperación desde el momento del lanzamiento. Si falta
esa atribución, la limpieza queda pendiente y el test no se declara completo.

## 10 · Rendimiento: comparar experimentos equivalentes

Primero calibra A/A: misma versión contra sí misma para estimar el ruido de la máquina y el
protocolo. Después alterna A/B con repeticiones, mismas entradas y sin contendientes pesados.
Conserva cada pasada, incluida la desfavorable. El número de repeticiones se fija antes,
no se amplía hasta lograr un verde.

Para un presupuesto de 60 Hz, 1000/60 = 16,667 ms por frame. Una media de 60 FPS no acredita
que cada frame cumpla el presupuesto. Define qué percentil y qué máximos acepta el requisito.
No sumes percentiles independientes como si fueran muestras del mismo frame; tampoco sumes
CPU y GPU si se solapan. El instrumento, la unidad y la ventana deben estar declarados.
Un intervalo de respuesta de GPU no equivale automáticamente a tiempo activo del dispositivo;
la captura y la escritura posterior de su archivo tampoco son el mismo intervalo.

Declara el algoritmo de percentil y conserva muestras brutas antes de filtrar. Comprueba la
integridad del perfil completo, sus unidades y metadatos; una fila favorable no sanea el resto.
El «mejor de tres» estima un coste favorable y no el peor observado ni un p99. En A/A, una media
de diferencias con signo puede cancelar variaciones: conserva magnitudes y dispersión además
de su dirección. En mediciones GPU asíncronas, publica muestras recibidas y pendientes y cómo
cierras la ventana; no presentes como completo un intervalo que aún tiene resultados sin leer.

Verifica que la población y la carga permanecen durante **todo el intervalo**, no solo en una
captura inicial. Un detector que elige únicamente el tramo favorable deja de probar el
escenario solicitado. Separa carga, calentamiento y tramo medido conforme al contrato.
Guarda las marcas de tiempo y duración real, y falla si no alcanza la cobertura requerida.

La instrumentación puede cambiar el coste; úsala para diagnóstico y vuelve al producto normal
para aceptación. VM y YYC son builds distintas. Mejorar una simulación Python tampoco acredita
el paso de GML: compara casos de frontera contra el runtime. El montaje, la captura, la entrada
y el cierre son parte del medidor; deben tener sus propias pruebas y controles fallidos.

Los percentiles de respuesta necesitan denominadores. Informa solicitudes totales, respuestas,
órdenes reemplazadas, casos sin desplazamiento y timeouts, con su política de clasificación.
En el caso estudiado, un clic pendiente sin movimiento se descartaba tras un plazo fijo; si
solo se miden respuestas, los casos lentos o inalcanzables desaparecen del p99. Ese plazo es
una decisión del instrumento, no un umbral universal. Conserva el intervalo completo y los
casos descartados antes de juzgar latencia. La inspección de ese código descubre el sesgo
posible; no acredita cuánto afectó a una medición histórica.

## 11 · Datos, assets derivados y fronteras de formato

Una fuente canónica de datos alimenta catálogo, selección, modelo, retrato, animaciones,
localización y guardado. Los IDs se mantienen estables y los cambios de esquema tienen
migración. Cuenta por separado definido, generado, exportado, cargable y alcanzable.
Las comprobaciones de consistencia deben encontrar tanto una entrada sin asset como un
archivo que ya no corresponde a su dato. El tamaño del catálogo no mide esa coherencia. Separa claves de asset e IDs de los rótulos
visibles; corregir un nombre no debe consumir la secuencia aleatoria histórica ni cambiar
identidades persistidas salvo migración autorizada.

Para cada asset derivado conserva huellas de fuente, generador, parámetros y salida. Cambiar
el modelo o la paleta invalida su retrato y su atlas aunque esos archivos sigan existiendo.
Una caché «presente» no es una caché «vigente». Comprueba trazabilidad antes de reutilizarla.

Una generación de varios archivos conserva una identidad común para imagen, recibo y
manifiesto. Publica un conjunto completo y recuperable: salida provisional, validación de
todas las piezas y promoción declarada. Si se interrumpe, los lectores distinguen generación
incompleta del último conjunto válido. La caché identifica también la receta completa y sus
versiones; existencia del archivo o parámetros redondeados no acreditan equivalencia de entradas.

En 3D, el contrato de exportación incluye versión, bytes, coordenadas, normales, pivote,
materiales, jerarquía, animación y límites. Prueba ida/vuelta, archivos truncados y versiones
incompatibles; valida la lectura en el juego. El formato interno del caso no es una
API incorporada de GameMaker. Reutiliza el principio, no sus nombres ni sus bytes sin contrato.

Comprueba compatibilidad por consumidor, no solo por formato: juego, preview, render externo,
retrato y auditor pueden admitir versiones distintas. Valida finitud y dominios de todos los
campos numéricos; NaN puede escapar a una comparación de tolerancia. Genera en una salida
provisional, valida y promueve después: «escrito» no significa «apto», aunque se agotaran las
iteraciones. El contrato técnico está en [3D en GameMaker](<../04 - Recetas por género/29 - 3D en GameMaker.md>) §11.

El pipeline completo es fuente → vistas → geometría → materiales → jerarquía → animación →
exportación → integración → retratos → escena real → rendimiento. Comprueba en cada frontera
escala, transparencia, orientación e identidad. Generar una imagen con aspecto 3D no entrega
un modelo, ni un render externo demuestra la integración. Mantén las referencias originales;
las vistas inferidas deben declararse como tales. Verifica licencias y permisos de cada fuente
antes de distribuir. No cambies el modelo de IA elegido para acelerar o abaratar el pipeline.

Para encontrar y clasificar fuentes sin cargar todo el proyecto en el contexto, usa el
procedimiento portátil de [Búsqueda multimodal con EmbeddingGemma 2](<../12 - Utilidades e integraciones/11 - Búsqueda multimodal con EmbeddingGemma 2 - contexto y recursos para agentes.md>).
Distingue ese uso por el agente de una función semántica distribuida dentro del producto.

### 11.1 Integración semántica: medir cada frontera

Si el proyecto ya usa un servicio de embeddings, conserva su modelo, revisión, precisión y
contrato. Comprueba identidad y rechaza vectores nulos, no finitos o con dimensiones distintas.
Reutiliza el servicio autorizado; un cliente del proyecto no debe descargar otros pesos,
levantar otro demonio ni registrar otro MCP para poder hacer una consulta. Verifica la frontera
HTTP con servidor de prueba y después la conexión real cuando esté autorizada. La consulta no
instala paquetes; el entorno se prepara explícitamente con su lockfile.

Cuando cambia la arquitectura de integración, revisa que la suite ejerza la frontera vigente.
Un test escrito para un demonio interno no certifica el cliente HTTP que lo sustituyó, aunque
se conserve su nombre o un recibo antiguo. Distingue cobertura desalineada detectada por lectura
de un fallo reproducido; registra cuál falta ejecutar bajo autorización. Aísla también salidas,
logs y temporales de los tests con dobles: un modo «fake» no garantiza ausencia de escritura
sobre el proyecto real.

Separa búsqueda léxica CPU, semántica y combinación híbrida. Cada resultado necesita ruta,
ubicación, extracto y procedencia verificables. Un fallback debe ser explícito: que responda
algo no demuestra que utilizó el modelo solicitado. Tampoco la fidelidad de vectores acredita
la utilidad de los resultados ni que el harness esté usando su integración.

Antes de ajustar pesos o filtros, fija consultas, relevancia, baseline y métrica. Reserva
preguntas independientes **fuera del corpus y de sus derivados**, sin usarlas para elegir
parámetros. Si están indexadas, la prueba histórica sirve de diagnóstico de ese corpus; no
acredita generalización. Guarda las variantes rechazadas y repite solo si cambió la hipótesis
o el criterio autorizado. Un MRR por debajo del baseline no se convierte en aprobado porque
las pruebas unitarias del cliente pasen.

Mide por separado codificación, consulta completa, arranque en frío e indexación incremental.
Una tanda de embeddings calientes no mide las otras tres. Conserva corpus, fragmentación,
modelo y parámetros en el manifiesto de entradas. Prueba también interrupción al actualizar,
archivo borrado/renombrado, índice obsoleto y recuperación: una ruta devuelta debe seguir
resolviendo al contenido que la evidencia identifica.

La huella identifica el fragmento completo, no solo su extracto visible. Declara si el ranking
puntúa archivos o fragmentos y evita votos duplicados; una puntuación de fusión de rangos no
es similitud coseno. Publica cada actualización tras cotejar la fuente y conserva la versión
anterior si falla. Una raíz inaccesible no es un corpus vacío que se pueda purgar.

Distingue lectura de fuentes y escritura de caché: una consulta puede crear esquemas, índices
o vectores. Enumera y prueba esos efectos con permisos y aislamiento explícitos. La instalación
autorizada tampoco debe quedar dependiente de un worktree temporal. Un vídeo sintético de
imágenes fijas permite controles concretos; no acredita diversidad temporal de partidas reales.

## 12 · Simulación, azar y nombres que engañan

Las pruebas de progresión necesitan entradas deterministas y estados de frontera: inventario
lleno, derrota, recompensa repetida, retorno, cambio de versión y recuperación tras cierre.
Una simulación externa sirve para explorar y calibrar; los mismos vectores deben pasar en
GML antes de afirmar paridad. Una prueba estadística finita no demuestra equivalencia exacta.

Aísla el estado aleatorio por consumidor cuando el contrato requiera reproducción. Una semilla
global no evita que otra llamada adelante la secuencia. Compara también probabilidades muy
pequeñas y extremos del rango; el redondeo puede introducir un sesgo que no sale en una tanda
corta. Usa controles con sesgo conocido para comprobar que el detector puede fallar.

Si un estado global tiene el mismo nombre que una función, la comprobación
`variable_global_exists` puede ver el símbolo sin garantizar que el estado booleano esté inicializado. Evita compartir nombres entre funciones y flags globales.
`validar-proyecto.py` detecta escrituras directas de `global.nombre` que pueden ocultar una
función de script declarada en el nivel superior, y las reporta como **COLISIÓN GLOBAL**, también en `--json`.
Es un análisis léxico: excluye funciones anidadas y eventos, no resuelve accesos dinámicos ni
toda la semántica de ámbitos, y requiere contraste en runtime.
No interpreta una llamada a `global.nombre` como una escritura ni rechaza asignar
una referencia a la misma función. No reemplaza una prueba del arranque y de la rama afectada.

Distingue también solicitud de audio, reproducción aceptada y audibilidad, y preparación por
debug frente a entrada real del autopiloto; los casos cruzados están en `13/10 §15`.

## 13 · Continuidad entre harnesses y pausa recuperable

Cuando cambia el harness, conserva identidad del proyecto, checkout, revisión, WIP,
contratos, autorizaciones, modelo elegido y estado de pruebas. Un límite de cuota explica
una interrupción; no cambia la especificación ni autoriza sustituir un modelo.
El agente entrante consulta la evidencia, no solo las conclusiones del anterior.

Un supervisor clasifica fallo con código de salida y segmento nuevo del registro. Prueba
citas de errores, mensajes antiguos y fallo real: buscar una frase en toda la transcripción
puede redisparar por historia. Comprueba cancelación antes de cada despacho/reintento y al
salir de una espera; la pausa no se valida solo al crear el supervisor.

Un punto de pausa útil deja: orden exacta del usuario, checkout y revisión, cambios locales,
procesos/reservas propios, último resultado completo con revisión, resultados incompletos,
bloqueos, próximos pasos y operaciones que requieren nueva autorización. No borra las ramas
pendientes ni reconstruye el proyecto desde una versión «limpia».

Al retomar, comprueba que el usuario autorizó esa fase y que siguen existiendo sus entradas.
Desbloquea solo los marcadores cuyo motivo haya resuelto esa autorización. Mantén separado
lo desarrollado, integrado, instalado, publicado y aceptado: ninguno implica los siguientes.
Una integración autorizada en un proyecto no autoriza commits, push ni instalación en otro.

## 14 · Plantillas mínimas y puerta de entrega

### 14.1 Encargo de pieza

```text
ID y requisito:
Checkout/revisión de partida y WIP que preservar:
Archivos propios / fronteras compartidas / integrador:
Entradas autoritativas y huellas:
Salida observable y contratos de formato:
Recursos, orden de bloqueo y presupuesto:
Pruebas propias y controles negativos:
Comparación de integración / criterio final:
Entrega: diff, comandos, recibos, límites y próximo bloqueo.
Permisos vigentes y operaciones reservadas al usuario:
```

### 14.2 Recibo de ronda

```text
Hipótesis / requisito / referencia:
Revisión y huellas de entradas / binario:
Entorno / escenario / intervalo / población:
Comandos y resultados completos:
Controles y crítica aislada:
Decisión de integrar / estado de aceptación final:
Cambios que invalidan evidencia previa:
Guardado y procesos: estado anterior, cierre, restauración cotejada:
Bloqueo siguiente / acción autorizada siguiente:
```

### 14.3 Comprobar antes de declarar el hito

- [ ] Requisitos cotejados con el juego completo; recortes y sentidos pendientes declarados.
- [ ] Pruebas de herramientas separadas de las del juego y de aceptación del usuario.
- [ ] Resultados completos ligados a entradas actuales; históricos identificados.
- [ ] Crítica con clave separada, controles válidos y contexto sin contaminar.
- [ ] Datos y assets derivados coherentes; migraciones y runtime realmente probados.
- [ ] Rendimiento comparable con intervalo y población completos, sin seleccionar verdes.
- [ ] Recursos, procesos y guardado propios recuperados y cotejados.
- [ ] WIP y evidencia conservados; pausa, modelos y permisos respetados.
- [ ] Skill: rutas existentes, YAML válido, paquete completo y prueba de consulta fresca.

## Fuentes y límites

La evidencia primaria del caso se conserva en privado. El [recibo público](../_indice/auditorias/r21-publicacion.md)
registra únicamente las pruebas de la biblioteca. Estas prácticas se abstraen del caso;
las recomendaciones de este documento no afirman haber sido ejecutadas aquí sobre cada
plataforma o cada juego. La comprobación estática, la compilación de documentación y una
prueba de consulta no certifican perfección universal, calidad final ni ausencia de bugs.

Documentación oficial contrastada el 11-10-2026:
[gm-cli](https://github.com/YoYoGames/gm-cli/blob/main/README.md),
[skills de OpenAI](https://developers.openai.com/plugins/concepts/skills) y
[evaluación de skills](https://developers.openai.com/blog/eval-skills).
El manual y el índice del runtime siguen mandando para las API de GML.
