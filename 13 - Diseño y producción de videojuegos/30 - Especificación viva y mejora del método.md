# 30 · Especificación viva y mejora del método

> **Del requisito a la evidencia, y del fallo a una mejora reutilizable.**
> Complemento operativo de [28 · Elicitación](<28 - De hazme un juego a una especificación - el protocolo de elicitación del agente.md>)
> y [29 · Desarrollo con IA](<29 - Desarrollo con IA - orquestación, crítica y evidencia.md>).
> Investigación contrastada el **15-10-2026**; fuentes, revisiones y límites en
> [r24 · Investigación de métodos](../_indice/auditorias/r24-investigacion-metodos.md).

La biblioteca ya enseña especificación, tareas verticales, hipótesis y playtesting.
Aquí se concreta cómo mantenerlos conectados cuando cambian el juego, las pruebas o la
propia skill. El objetivo es detectar errores y aprender con evidencia. Ningún proceso
garantiza que cualquier juego resulte perfecto.

## 1 · El mínimo que necesita cada encargo

Reutiliza los documentos y herramientas existentes. Una corrección pequeña puede vivir
en una tarjeta con criterio, reproducción, cambio y prueba; un sistema nuevo necesita
además contratos y dependencias; un juego completo usa el GDD y sus fichas. No impongas
un directorio, un tracker, un enjambre de agentes o una instalación de SDD para cada caso.

| Pieza | Contenido que permite decidir |
|---|---|
| Requisito versionado | ID estable, comportamiento o hipótesis, criterio y autoridad |
| Tarea vertical | Requisitos, entradas, dependencias, dueño y demostración completa |
| Caso | Condiciones iniciales, acción, resultado esperado y cómo observarlo |
| Recibo | Caso y revisión probados, entradas, resultado completo y límites |
| Cambio | Antes/después, motivo, autorización aplicable y evidencias afectadas |
| Aprendizaje | Observación, reproducción, alcance y comprobación de la mejora |

Son responsabilidades, no seis archivos obligatorios. La fuente normativa vigente se
identifica al principio; las versiones anteriores se conservan como historia. Dos órdenes
incompatibles dispersas por un documento no forman una especificación ejecutable: resuelve
qué instrucción autorizada manda y señala la sección sustituida antes de seguir.

## 2 · Qué se acepta y con qué prueba

Clasifica el criterio antes de construir; un requisito puede necesitar varios tipos.

| Tipo | Ejemplo de criterio | Evidencia pertinente |
|---|---|---|
| Comportamiento | La opción confirmada reaparece tras cerrar y abrir | Recorrido real y lectura posterior del estado persistido |
| Experiencia | El jugador entiende cuándo puede esquivar | Conducta observada y contexto de playtest; hipótesis según 13/01 §7 |
| Presentación/fidelidad | El enemigo conserva la silueta de la referencia | Comparación controlada con la fuente y crítica por regiones |
| Restricción | El escenario mantiene el presupuesto temporal acordado | Muestras, población, percentil y entorno según 13/29 §10 |

Un bot puede comprobar acciones y estados; no sustituye a personas para afirmar diversión
o comprensión. Un juez visual puede describir legibilidad; una puntuación favorable no
demuestra por sí sola fidelidad, sonido, control o experiencia sostenida. Registra cada eje
por separado. El protocolo de observación ya está en [Diseño de juego](<01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md>)
y [Testing y QA](<10 - Testing y QA.md>); aquí se enlaza su resultado al requisito.

La cadena mínima es:

```text
R-OP-01@2 → T-OP-02 → C-OP-01/C-OP-02 → E-OP-07 → decisión por R-OP-01@2
```

La revisión del requisito y la del producto son identidades distintas. El recibo identifica
ambas, junto a WIP, entradas y entorno. La matriz apunta a los casos requeridos y a cada
resultado vigente; cuenta previstos, ejecutados, fallidos, omitidos e inválidos. Un único
caso favorable no cierra una fila cuyo otro caso obligatorio falta.

Usa estados con significado observable: pendiente, construido, integrado, probado y aceptado.
Anota además si la evidencia es vigente, histórica, incompleta o inválida. Un bloqueo o
un fallo no desaparece porque se reescriba la conclusión. La aceptación del responsable
autorizado se registra separada del veredicto técnico; un agente no se concede autoridad
adicional cambiando esa etiqueta. Los estados y recibos siguen el contrato de `13/29`.

## 3 · Cambiar la especificación sin heredar un verde incorrecto

1. Identifica requisito y versión vigentes, motivo, nueva condición y autoridad aplicable.
   Distingue implementación dentro del encargo de un cambio de alcance que necesita decisión.
2. Recorre dependencias: consumidores, escenas, datos, assets derivados, guardado, controles,
   casos y requisitos vecinos. Conserva la versión previa y su evidencia.
3. Marca las evidencias afectadas como históricas y sus casos como pendientes de revalidar.
   Una prueba del criterio antiguo no prueba el nuevo. Las evidencias no afectadas pueden
   conservar vigencia si se justifica la independencia de sus entradas y contratos.
4. Actualiza los casos y tareas afectados antes de implementar; fija el resultado esperado
   que distinguiría fallo de éxito. El integrador reserva las fronteras compartidas.
5. Ejecuta la pieza y las regresiones necesarias; actualiza la matriz con los recibos nuevos.
   Un cambio posterior a la medición vuelve a abrir esta comprobación.

Este análisis también se aplica si cambia el **oráculo**: referencia visual, significado de
una medida, rúbrica o configuración del juez. Una herramienta descalibrada invalida su juicio;
si el candidato no cambió, conserva sus bytes y corrige primero la medición. Evita generar
otra versión solo para acomodarse a una nota. Mantén independientes la fidelidad a la fuente
y la preferencia de estilo: forzar que la referencia obtenga una nota baja puede contradecir
el encargo de parecerse a ella.

## 4 · Ejemplo completo: opciones persistentes en GameMaker

Ejemplo didáctico, **no ejecución de un juego en esta ronda**. Los nombres de recursos
son orientativos; se reutilizan los del proyecto. `R-OP-01@1` exigía cambiar el volumen en
la sesión. La versión `@2`, autorizada por el encargo, añade confirmación y persistencia.

| Elemento | Contrato concreto |
|---|---|
| Requisito `R-OP-01@2` | Al confirmar, guardar y recuperar el valor tras cerrar y abrir; cancelar conserva el anterior |
| Entrada existente | Acciones unificadas, pantalla de opciones, mezcla de audio, serialización y ruta de guardado real |
| Tarea `T-OP-01` | Recorrer portada → opciones → ajustar → cancelar → regresar; copia editable separada del valor aplicado |
| Tarea `T-OP-02` | Tras la frontera de T-OP-01, confirmar → persistir → cerrar → abrir → mostrar y aplicar el valor |
| Frontera compartida | Esquema de opciones, arranque, audio y recursos de pantalla; un integrador y un escritor de recursos |
| Caso `C-OP-01` | Ajustar y cancelar: el valor previo permanece al volver y al reabrir |
| Caso `C-OP-02` | Confirmar un valor distinguible, cerrar el proceso y reabrir: UI y audio usan el valor guardado |
| Casos cruzados | C-OP-03 a C-OP-08 de la matriz siguiente, obligatorios en este ejemplo |
| Control negativo | Una versión de prueba que omite la escritura debe fallar C-OP-02 |
| Evidencia anterior | La prueba de cambio en memoria de @1 queda histórica respecto a persistencia @2 |
| Aceptación | C-OP-01 a C-OP-08 ejecutados y aprobados sobre la unión @2; sin omisiones ni controles inválidos; el resultado de @1 no rellena los omitidos |

**Política fijada para este ejemplo:** valor previo 0,8, ajuste 0,3 y rango válido 0–1.
Sin archivo se usa 0,8. Si el archivo está corrupto, se recupera la copia válida anterior 0,6;
si no existe, se usa 0,8 con aviso. Se conserva el archivo defectuoso hasta una confirmación
explícita. Son decisiones de esta ficha didáctica, no valores ni políticas universales.

Los estados de pantalla son **cerrada → editando → confirmando → cerrada**; cancelar vuelve
de editando a cerrada sin aplicar ni escribir. Un error de escritura deja la pantalla en
editando con aviso y valor previo aplicado; el recibo de éxito no se emite. Perder foco no
equivale a confirmar. El estado de pausa del mundo es independiente del de la pantalla.

| Caso obligatorio | Inicio y acción | Resultado esperado que decide la prueba |
|---|---|---|
| C-OP-01 | Guardado válido 0,8; editar 0,3 y cancelar | UI al volver y mezcla siguen en 0,8; no cambia el archivo |
| C-OP-02 | Editar 0,3, confirmar con escritura correcta, cerrar proceso y abrir | Pantalla y mezcla cargan 0,3 desde el archivo; se alcanza el arranque normal |
| C-OP-03 | Perfil de prueba sin archivo; arrancar | UI y mezcla usan 0,8; menú accesible y sin error de script |
| C-OP-04 | Archivo corrupto; arrancar con copia previa 0,6 y repetir sin copia | Primer recorrido recupera 0,6; segundo usa default 0,8 y muestra aviso; ambos conservan el archivo defectuoso hasta confirmar |
| C-OP-05 | Editando 0,3, perder foco mientras una acción está pulsada y recuperar | Sigue editando; no aplica ni guarda; requiere una pulsación nueva para confirmar |
| C-OP-06 | Ejecutar C-OP-01/02 con acciones de mando y desconectar/reconectar al editar | Mismos valores y transiciones; no hay confirmación espontánea ni doble escritura |
| C-OP-07 | Mundo en pausa; abrir opciones, editar/cancelar y repetir confirmando | Se vuelve a pausa, sin avanzar el mundo durante el modal; cada rama conserva el resultado de C-OP-01/02 |
| C-OP-08 | Valor aplicado 0,8; editar 0,3 y provocar fallo de escritura al confirmar | Aviso, pantalla editable y aplicado 0,8; sin recibo de éxito |

Los fixtures de ausencia, corrupción y fallo
de escritura usan un perfil de prueba recuperable; no se fabrican dañando la partida real.
La revisión de `R-OP-01@2` incluye esta política y matriz, antes de implementar o medir.

Antes de crear guardado, entrada o UI nuevos, comprueba los sistemas actuales y el catálogo
de librerías. Las tareas entregan recorridos completos, en vez de separar «todo el menú» y
«todo el guardado» sin probar su unión. Si la frontera aún no existe, acuerda su contrato
antes de despachar consumidores dependientes.

Los `.gml` de propiedad independiente pueden trabajarse en paralelo. Recursos `.yy`/`.yyp`
se modifican por ResourceTool/MCP o IDE, por un solo escritor; compile/run/package comparten
estado y requieren exclusión. Revisa la huella de la integración y ejecuta el recorrido en
esa unión. La prueba protege y restaura el guardado completo según `13/29 §9`; cambiar la
carpeta de trabajo no demuestra aislamiento. La fuente de UI, la entrada y la localización
siguen las decisiones tempranas de la referencia de desarrollo de la skill.

Si también existe `R-UX-01` («la confirmación se entiende»), los casos anteriores prueban
funcionamiento. La observación con jugadores aporta otra evidencia; hasta tenerla, esa
hipótesis sigue pendiente. El éxito técnico de R-OP-01 no la aprueba por arrastre.

## 5 · Gauntlet con decisiones y presupuesto

El bucle de `13/29 §3` ya define hipótesis → cambio → prueba → crítica → integración.
Antes de la primera ronda, concreta criterio vigente, referencia, regresiones, presupuesto
autorizado y número de rondas sin progreso que dispara diagnóstico. Conserva el resultado
de cada ronda, incluso fallos, empates, cancelaciones y controles inválidos.

| Resultado | Acción siguiente |
|---|---|
| Control fallido o juicio contaminado | Invalidar la medición; reparar instrumento o preparar otro contexto y paquete |
| Mejora real sin alcanzar el umbral | Integrar solo si lo permite la puerta del proyecto; aceptación final pendiente |
| Regresión en un requisito obligatorio | Conservar candidato como experimento; corregir antes de promover |
| Desacuerdo entre críticos | Registrar ejes y evidencia del desacuerdo; no seleccionar solo el voto favorable |
| Sin progreso válido | Diagnosticar otra hipótesis, frontera o referencia; mantener el criterio del usuario |
| Cuota agotada, permiso ausente o pausa | Bloquear nuevos despachos y reintentos afectados, incluidos descendientes |

Agotar rondas o presupuesto no convierte al mejor candidato disponible en aceptado. Cambiar
de hipótesis dentro del alcance permite continuar trabajo útil; un límite externo que impide
actuar se comunica con su causa. No se sustituye el modelo elegido ni se reduce el umbral.
Una orden de parada llega al supervisor, a sus colas, a las esperas y al relanzamiento;
comprueba identidad de los procesos propios antes de cerrar o declarar la pausa efectiva.

La doble revisión de código ayuda a contrastar normas y spec. La crítica ciega de producto
evalúa otro objeto y recibe otro contexto. Ni dos agentes con la misma explicación previa
forman dos observaciones independientes, ni el acuerdo entre ellos sustituye el criterio
del usuario o un playtest. El aislamiento y los controles están desarrollados en `13/29 §4–5`.

## 6 · Automejora: promover un aprendizaje, no una anécdota

| Paso | Qué debe quedar antes de avanzar |
|---|---|
| Observar | Síntoma, contexto, resultado esperado/real, versión y evidencia; distinguir hecho de interpretación |
| Reproducir | Caso mínimo y control que detecta el defecto; si no se reproduce, conservar como hipótesis |
| Corregir | Causa y frontera afectada; revisar primero validador y ejemplo existentes |
| Elegir destino | Fallo mecánico → comprobación automatizable; error de juicio → regla breve y ejemplo que la cumpla |
| Acotar | Motor/versión/target/género aplicables, contraejemplo y circunstancias donde la regla no corresponde |
| Evaluar | Casos previos y nuevos independientes, resultados desfavorables y comportamiento con/sin guía |
| Promover | Revisión del cambio, rutas descubribles, versión y mantenimiento; retirar o sustituir consejos contradictorios |

Corrige primero la fuente que los usuarios copian. Añadir una advertencia mientras el
ejemplo vecino sigue enseñando el fallo perpetúa el problema. La revisión comprueba también
si otro capítulo, plantilla o referencia portátil queda contradictorio.

Ejemplo de alcance: «En esta versión del CLI, HELP escribió el proyecto» exige protección
de escritura y una reproducción verificable. No autoriza concluir «todos los comandos de
ayuda de todos los motores escriben». Una decisión de estilo de un ARPG tampoco determina
el arte de un puzzle. La observación conserva procedencia y confianza; una conclusión de
otro agente se contrasta cuando decide una integración.

La promoción modifica documentación o comprobaciones dentro del encargo. Instalar hooks,
cambiar modelos, escribir memorias globales, ejecutar código ajeno o publicar mantiene sus
permisos propios. El aprendizaje no necesita esas acciones para ser útil y revisable.

## 7 · Evaluar la skill además de validar sus archivos

Enlaces, YAML, índices y compilación prueban propiedades necesarias del paquete y del
corpus. Para saber si una instrucción cambia decisiones hacen falta ensayos del consumidor.

1. Fija escenario, fallo tentador, criterios de puntuación y repeticiones antes de probar.
   Incluye tiempo/coste hundido/autoridad aparente cuando se mida disciplina.
2. Ejecuta un control sin la guía y una variante con la skill y sus referencias realmente
   disponibles, en contextos frescos. Mantén escenario, modelo, herramientas y condiciones
   comparables; declara cualquier diferencia. Conserva prompt y respuesta íntegros.
3. Lee manualmente cada respuesta: recitar la regla o repetir una frase del escenario
   no equivale a elegir la acción correcta. Informa aprobados y fallos por criterio y variante,
   con denominadores; separa pruebas de capacidad nueva de regresiones ya conocidas.
4. Si ajustas la instrucción con esos casos, úsalos como desarrollo y evalúa también otros
   independientes, sin filtrar la clave al agente. Conserva variantes rechazadas.
5. Comprueba consulta con biblioteca completa y paquete solo; distingue una herramienta
   ausente de un consejo incorrecto. Prueba el loader del harness objetivo cuando corresponda.

Si el control ya responde correctamente, no hay evidencia de una mejora causal de esa
instrucción. Puede seguir aportando una referencia consultable, pero una muestra sin fallos
no demuestra universalidad. Unas pocas repeticiones describen ese ensayo; no establecen
significancia estadística ni fiabilidad de todos los modelos, géneros o plataformas.

La prueba de descubrimiento de esta biblioteca verifica que el buscador devuelve rutas;
no ejecuta un LLM. Mantén separados ambos resultados. Tampoco una respuesta de planificación
demuestra que el agente habría compilado o preservado datos al actuar: esa frontera requiere
una prueba de ejecución aislada y autorizada.

## 8 · Adoptar métodos externos sin importar sus supuestos

Para cada repositorio conserva URL/revisión, archivo, licencia aplicable, capacidad, evidencia
leída/ejecutada, diferencia con la biblioteca y decisión de adopción. La licencia de un archivo
puede diferir de la raíz. Los nombres de comandos y hooks de otro harness no son API de GameMaker.

De Matt se reutilizan requisitos, tareas verticales, pruebas y revisión; de Gentle, contratos
y revisiones pertinentes; de ECC, ideas de evaluación y aprendizaje que superen el contraste.
Spec Kit y OpenSpec permiten estudiar organización y cambios de especificación. El método
portátil mantiene las reglas del proyecto: no instala esos sistemas ni sustituye el flujo
elegido. La matriz de investigación identifica lo incorporado, adaptado o descartado.

Si se integra **código** de un upstream, rigen revisión fijada, licencia, demos y matriz de
capacidades con pruebas de paridad. Estudiar documentos y adaptar una práctica no acredita
esa integración. Prioriza una diferencia demostrable frente a añadir otra colección de
agentes, comandos o dependencias. Las API de GML siguen verificándose por runtime y manual.

## 9 · Dos registros para reutilizar

Completa solo los campos pertinentes; se pueden añadir al tracker o documento que ya existe.

```text
CAMBIO DE REQUISITO
ID/versión anterior → nueva; motivo y autoridad:
Criterio vigente; caso que diferencia fallo/éxito:
Consumidores y dependencias afectados; propietario/integrador:
Evidencias históricas y casos pendientes; independencia de lo conservado:
Tarea vertical y regresiones; resultado/recibo por caso:
Estado técnico; decisión de aceptación; límites:
```

```text
APRENDIZAJE CANDIDATO
Hecho observado y evidencia; hipótesis causal:
Reproducción y control; motor/versión/target:
Corrección y destino (ejemplo, prueba o regla):
Ámbito, contraejemplo y consejo sustituido:
Ensayo con/sin guía; casos independientes y resultados completos:
Decisión de promover, revisar o conservar como hipótesis; revisión:
```

## Fuentes y límites

La [investigación de métodos](../_indice/auditorias/r24-investigacion-metodos.md) conserva
fuentes primarias fijadas y decisiones. Los [aprendizajes de Relicwild](../_indice/auditorias/r24-aprendizajes-relicwild.md)
se abstraen de una lectura de contratos y recibos de un proyecto en pausa. Sus resultados
son los que registran esos archivos; no se reejecutaron ni certifican el juego actual.
Los [ensayos de la skill](../_indice/auditorias/r24-ensayos-skill.md) y el
[recibo de validación](../_indice/auditorias/r24-validacion.md) informan qué se probó aquí.
Este capítulo no instala ni afirma haber ejecutado los frameworks externos estudiados.
