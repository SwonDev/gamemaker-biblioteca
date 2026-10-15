# r24 · Métodos para especificar, experimentar y mejorar la skill

Consulta: **15-10-2026**. Investigación de fuentes primarias y lectura de archivos fijados
a revisiones de Git. El objetivo es mejorar el método GameMaker existente mediante aportes
concretos. No se han instalado paquetes, hooks, agentes ni memorias de terceros; tampoco se
ha ejecutado su contenido ni se han modificado los juegos de los que aprende la biblioteca.

## 1. Qué existe ya y qué merece ampliación

Se leyeron `13/28` y `13/29`, y se contrastaron las partes pertinentes de `13/01`, `13/10`,
`13/14` y la skill. La biblioteca **ya tiene desarrollo guiado por especificación**:
elicitación, contrato observable, tareas verticales, hipótesis falsable, dueño, integrador,
crítica independiente, controles y recibos ligados a una revisión. También tiene MDA,
prototipado y playtesting. Reescribir esos procedimientos con otra marca aumentaría las
contradicciones y el coste de consulta.

| Fuente local | Ya cubierto | Ampliación útil |
|---|---|---|
| `13/28` y `13/14` | Encargo → especificación, supuestos, recorte, parámetros y aceptación | Cambio pequeño sobre la spec vigente, con efecto explícito en tareas y evidencia |
| `13/29` §2.1–4 | Flujo Matt adaptado, tareas verticales, agentes con contrato y recursos compartidos | Comprobar coherencia entre contratos antes de despachar y después de integrar |
| `13/01` §1, §6–8; `13/10` §10 | Experiencia objetivo, prototipo y conducta observada frente a interpretación | Vincular cada experimento de diseño al requisito afectado y a la decisión posterior |
| `13/29` §5–6 y §14 | Crítica aislada y vigencia de pruebas | Separar aceptación del juego de evaluación de la propia biblioteca/skill |
| `13/29` §11 y §14.3 | Casos independientes para búsqueda y consulta fresca de la skill | Promoción de aprendizajes con baseline, contraprueba, muestra reservada y reversión |

Estas ampliaciones son una **operacionalización de cobertura existente**, no el
descubrimiento de que faltaba una metodología completa. El complemento debe remitir a esos
capítulos y aportar solo las plantillas y decisiones nuevas.

## 2. Procedencia comprobada de los repositorios

La API de GitHub resolvió nombre canónico, rama, SHA, fecha del commit y licencia de raíz.
Después se leyeron archivos desde `raw.githubusercontent.com` usando esos SHA. Las fechas
son de los commits de rama consultados, **no fechas de release ni versiones instaladas**.

| Repositorio canónico | Revisión leída | Fecha UTC del commit | Licencia de raíz |
|---|---|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336) | `49dd158d1076134a641b33efb035946536778336` | 09-10-2026 10:56:49 | MIT |
| [Gentleman-Programming/gentle-ai](https://github.com/Gentleman-Programming/gentle-ai/tree/89f1523876fc27874cabdb60c6587f078a61e9cf) | `89f1523876fc27874cabdb60c6587f078a61e9cf` | 15-10-2026 13:59:35 | MIT |
| [affaan-m/ECC](https://github.com/affaan-m/ECC/tree/b92f181b3b748d1abbc2afd94af6aa7d8c8fca29) | `b92f181b3b748d1abbc2afd94af6aa7d8c8fca29` | 12-10-2026 02:02:10 | MIT |
| [github/spec-kit](https://github.com/github/spec-kit/tree/6e7348de375f62922349e3bb20640edfda2383ad) | `6e7348de375f62922349e3bb20640edfda2383ad` | 15-10-2026 15:03:01 | MIT |
| [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec/tree/f80d860fc510ba4f51180c8ddde35b91b32de657) | `f80d860fc510ba4f51180c8ddde35b91b32de657` | 15-10-2026 00:04:13 | MIT |
| [YoYoGames/gm-cli](https://github.com/YoYoGames/gm-cli/tree/e67838d4c087ad88d6de18b04e09abb40e44303e) | `e67838d4c087ad88d6de18b04e09abb40e44303e` | 06-10-2026 08:27:50 | Apache-2.0 |

La URL que aportó el usuario, `https://github.com/affaan-m/ECC`, es válida y la API la
devuelve como canónica; no fue necesario sustituirla por otro proyecto. La licencia de raíz
no reemplaza declaraciones por archivo: `judgment-day`, `work-unit-commits` y
`rdd-defect-workflow` de Gentle declaran **Apache-2.0** en su frontmatter. Esta investigación
resume ideas y enlaza fuentes; una futura redistribución de sus archivos deberá conservar
su procedencia y condiciones concretas.

## 3. Matriz de adopción y rechazo

| Fuente y archivo realmente consultado | Aporte comprobado en el texto | Decisión para GameMaker |
|---|---|---|
| Matt: [to-spec](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/to-spec/SKILL.md), [to-tickets](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/to-tickets/SKILL.md) | Síntesis de acuerdos, fronteras de prueba, tareas verticales y dependencias; excepción expandir → migrar → retirar para refactors amplios | **Conservar** el método ya adaptado en `13/29`. No crear otro planificador ni publicar tickets por defecto |
| Matt: [tdd](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/tdd/SKILL.md) y [code-review](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/code-review/SKILL.md) | Comportamiento por interfaz, esperado independiente y revisión por dos ejes: normas/spec | **Adaptar a GML** mediante pruebas de sistemas, runtime, entradas y datos. Una prueba de función no acredita experiencia de juego |
| Matt: [retro](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/retro/SKILL.md) | Buscar primero controles existentes; un fallo mecánico pide un control determinista; reservar reglas para juicio y mejorar navegación | **Adoptar** como criterio para promover aprendizajes: nueva regla solo si produce una decisión o una comprobación útil |
| Gentle: [guía de skills](https://github.com/Gentleman-Programming/gentle-ai/blob/89f1523876fc27874cabdb60c6587f078a61e9cf/docs/skill-style-guide.md) | Activación, reglas, bifurcaciones, pasos y salida; detalle en referencias; registro de rutas | **Adaptar** la estructura y comprobar descubrimiento. Sus presupuestos de tokens son política de ese repo, no límites universales de la biblioteca |
| Gentle: [judgment-day](https://github.com/Gentleman-Programming/gentle-ai/blob/89f1523876fc27874cabdb60c6587f078a61e9cf/internal/assets/skills/judgment-day/SKILL.md) | Dos jueces ciegos, mismo objetivo inmutable, rondas acotadas; juicio sin autoridad de entrega | **Conservar opcional** cuando se pida ese juicio. No convertir toda tarea en doble revisión ni equiparar acuerdo con verdad |
| Gentle: [pruebas deterministas de agentes](https://github.com/Gentleman-Programming/gentle-ai/blob/89f1523876fc27874cabdb60c6587f078a61e9cf/docs/testing-agents-deterministically.md) | Runtime real con razonamiento guionizado para probar transporte/orden/efectos; distingue lo que el prompt vivo no queda probado | **Adoptar la separación**: fixtures verifican herramientas; ensayos con agentes reales verifican uso de la skill. No atribuir al segundo lo que solo prueba el primero |
| ECC: [eval-harness](https://github.com/affaan-m/ECC/blob/b92f181b3b748d1abbc2afd94af6aa7d8c8fca29/skills/eval-harness/SKILL.md) | Evaluaciones de capacidad/regresión, distintos jueces y repetición; advierte sobre sobreajuste, coste y latencia | **Adaptar** a un banco de encargos GameMaker, con fallos, controles y todos los intentos. No adoptar porcentajes genéricos como puerta universal |
| ECC: [continuous-learning-v2](https://github.com/affaan-m/ECC/blob/b92f181b3b748d1abbc2afd94af6aa7d8c8fca29/skills/continuous-learning-v2/SKILL.md) | Observaciones atómicas, alcance por proyecto y promoción a otro alcance | **Adoptar la ficha y el alcance**. Rechazar captura nueva por hooks y promoción automática por frecuencia o puntuación; dos proyectos no prueban universalidad |
| ECC: [team-agent-orchestration](https://github.com/affaan-m/ECC/blob/b92f181b3b748d1abbc2afd94af6aa7d8c8fca29/skills/team-agent-orchestration/SKILL.md), [iterative-retrieval](https://github.com/affaan-m/ECC/blob/b92f181b3b748d1abbc2afd94af6aa7d8c8fca29/skills/iterative-retrieval/SKILL.md) | Dueño/alcance/evidencia/puerta; contexto refinado según lo que falta | **Ya cubierto en gran parte**. Añadir consulta progresiva, sin copiar el número de agentes, umbrales de relevancia ni rondas como ley |
| Spec Kit: [analyze](https://github.com/github/spec-kit/blob/6e7348de375f62922349e3bb20640edfda2383ad/templates/commands/analyze.md), [converge](https://github.com/github/spec-kit/blob/6e7348de375f62922349e3bb20640edfda2383ad/templates/commands/converge.md) | Coherencia spec/plan/tareas; detección de obligaciones sin cubrir y trabajo no solicitado; convergencia sin reescribir intención | **Adaptar una comprobación portátil** antes/después del trabajo. Convergencia genera tareas, no prueba runtime ni aceptación |
| OpenSpec: [esquema spec-driven](https://github.com/Fission-AI/OpenSpec/blob/f80d860fc510ba4f51180c8ddde35b91b32de657/schemas/spec-driven/schema.yaml), [verificación](https://github.com/Fission-AI/OpenSpec/blob/f80d860fc510ba4f51180c8ddde35b91b32de657/src/core/templates/workflows/verify-change.ts) | Contrato por capacidad y deltas añadido/modificado/retirado/renombrado; completitud, corrección y coherencia; ausencia de evidencia distinta de no aplicable | **Adaptar la semántica de cambio**, con ID estable y escenarios. No exigir su CLI, sintaxis Markdown exacta ni jerarquía de carpetas |

### 3.1 Límites que impiden importar el paquete entero

ECC no es un motor GameMaker ni una certificación de calidad de sus juegos. Su
[verification-loop](https://github.com/affaan-m/ECC/blob/b92f181b3b748d1abbc2afd94af6aa7d8c8fca29/skills/verification-loop/SKILL.md)
contiene ejemplos TypeScript/Python, un objetivo genérico de cobertura y búsquedas textuales
de secretos. Son recetas que necesitan otra frontera en GameMaker; no sustituyen el índice,
el manual, los validadores ni las pruebas del producto.

Más decisivo: el propio
[eval-harness](https://github.com/affaan-m/ECC/blob/b92f181b3b748d1abbc2afd94af6aa7d8c8fca29/skills/eval-harness/SKILL.md)
declara **deshabilitada la ejecución de candidatos en todos los sistemas operativos** por no
tener un backend de aislamiento verificado. Las utilidades de cápsulas/recibos o la lectura
estática no acreditan ejecución, aislamiento ni promoción de un candidato. No se ha probado
aquí esa implementación y no se recomienda integrarla para obtener una supuesta puerta ya
resuelta.

Las plantillas de Spec Kit incluyen tratamiento de hooks; algunos ejemplos de Matt y ECC
prescriben publicar, hacer commit o automatizar integración. Este estudio **no los ejecutó**.
Esas órdenes no deben trasladarse como permisos implícitos a la skill GameMaker. Tampoco
debe introducirse una memoria paralela ni cambiar modelos/personas para imitar el repositorio.

## 4. El aporte específico de videojuegos

El artículo original [MDA, de Hunicke, LeBlanc y Zubek](https://www.cs.northwestern.edu/~hunicke/MDA.pdf)
distingue mecánicas, dinámicas y experiencia del jugador. Cambiar una regla puede alterar la
conducta emergente y la emoción que provoca. De ahí se deriva una aplicación local: separar
la prueba determinista de la regla de la hipótesis de experiencia; pasar la primera no prueba
la segunda. MDA ya está en `13/01`; se amplía su enlace con requisito y evidencia, no su teoría.

La [presentación de Mike Ambinder, Valve, GDC 2009](https://cdn.akamai.steamstatic.com/apps/valve/2009/GDC2009_ValvesApproachToPlaytesting.pdf)
contrasta observación, relato verbal, preguntas y experimentos. El pensar en voz alta se
plantea sin guiar ni corregir, y también puede distraer o alterar la experiencia; las
estadísticas permiten comparar, pero promediar pierde contexto y puede sugerir patrones
ilusorios. El recibo debería registrar método y limitación, además del resultado. No se
deduce una cantidad universal de testers ni una regla de descartar todo caso minoritario.

El material de [prototipado de MIT, CMS.611J](https://ocw.mit.edu/courses/cms-611j-creating-video-games-fall-2014/348ee58d265e61e4760d196bd97b1ad1_MITCMS_611JF14_Paper_Prot.pdf)
propone pregunta falsable → diseño rápido → jugar → revisar → repetir. Refuerza el experimento
que contesta una incertidumbre, no añadir producción antes de tener respuesta. Para la
biblioteca, su valor adicional es guardar la pregunta, el resultado y la decisión que modifica
la spec, junto a una referencia al protocolo ya existente.

El [artículo publicado por GameMaker sobre automatización de builds](https://gamemaker.io/en/blog/bs-tech-automate-builds)
describe el caso de Butterscotch Shenanigans: ejecutar pruebas dentro del juego y devolver un
resultado que el flujo pueda evaluar; usa Olympus y rutas distintas por target. Eso respalda
la frontera GML/runtime. No convierte Olympus en requisito oficial ni demuestra que haya un
comando nativo universal `gm-cli test`. El procedimiento de compilación y ejecución vigente
sigue en la biblioteca y [r23](r23-investigacion-versiones.md).

## 5. Propuesta concreta, ordenada por valor

1. **Delta de spec y coherencia.** Para cada cambio, identificar requisito, versión anterior,
   decisión autorizada, escenarios que cambian, tareas afectadas y evidencia que deja de
   servir. Una retirada debe demostrar ausencia del comportamiento; renombrar no obliga a
   reescribir símbolos de código si la conducta se conserva. Es adaptación de OpenSpec y
   Spec Kit a los recibos que ya tiene `13/29`.
2. **Dos resultados por sistema.** Comportamiento de la regla probado y experiencia objetivo
   observada, cada uno con método/estado. El experimento vincula hipótesis → observación →
   interpretación → decisión → cambio. No inventar un porcentaje de diversión.
3. **Promoción gobernada de aprendizajes.** Incidente y fuente → alcance → regla candidata →
   contraprueba → ensayo independiente → aceptar/rechazar/revisar. Versionar la regla y
   señalar qué evidencia podría refutarla. Una preferencia privada no se publica como ley
   del motor; un workaround se liga a componente, versión y condición de retirada.
4. **Evaluar la skill, además de validarla.** Comparar baseline y cambio sobre los mismos
   encargos, con harness/modelo/versión fijos y contexto fresco; reservar casos no usados
   para ajustar instrucciones. Cubrir descubrimiento, consulta correcta, símbolo real,
   preservación de WIP/pausa y resultado observable. No imponer una aplicación sintética
   enorme para cada ajuste editorial.
5. **Mantener pequeña la puerta de entrada.** Activación y ruta a la decisión; plantillas y
   ejemplos en referencias. Ensayar qué referencia carga un agente ante cada intención y
   comprobar que no salta a contenido irrelevante. Conservar el orden local Matt → motor →
   verificación; Gentle y ECC aportan piezas, no sustituyen ese contrato.

El informe recomienda empezar con **plantillas portátiles y controles existentes**. Un nuevo
validador solo se justifica cuando haya un error mecánico repetible que el mantenimiento
actual no detecte. Podría verificar IDs únicos, referencias y evidencia vencida declarada;
no podría resolver con fiabilidad contradicciones semánticas ni certificar que un juego es
bueno. No conviene crear un segundo orquestador o gestor de estado para este complemento.

Al usar repetición, distinguir «hubo al menos un éxito en k intentos» de «todos los k
intentos salieron bien». Registrar el denominador, fallos, reintentos y coste. Tres éxitos
observados son un resultado de esa muestra, no una estimación de fiabilidad perfecta. Esta
es una cautela de evaluación de la propuesta local, no una puerta estadística validada aquí.

## 6. Lectura, adaptación y prueba: alcance del recibo

**Lectura real:** los archivos enlazados de Matt, Gentle, ECC, Spec Kit y OpenSpec; materiales
primarios de MDA, Valve, MIT y GameMaker. También se consultaron los árboles de esos repos y
sus metadatos. Los árboles servían para encontrar archivos, no para acreditar cobertura de
todas sus capacidades. No se inspeccionó exhaustivamente su implementación completa.

**Adaptación local constatada:** las skills instaladas `implement` y `to-spec` no son
idénticas en bytes a la revisión de Matt consultada: incluyen activación automática y
precedencia local para permisos/trackers. `judgment-day` sí coincide en bytes con el archivo
fijado de Gentle, versión declarada `1.7`. Esa coincidencia no acredita paridad del paquete,
de sus referencias, del harness ni de su ejecución. La biblioteca debe documentar su método
portátil y la procedencia, sin llamarlo una copia exacta de upstream.

**No ejecutado:** CLI ni hooks de estos métodos, juicios de Gentle, evaluaciones ECC,
Spec Kit/OpenSpec, compilación de juegos o pruebas de otros targets. No se han validado
rendimiento, superioridad ni fiabilidad universal de ninguno. Las recomendaciones son una
síntesis razonada para completar el método existente; los ensayos posteriores deben conservar
su propio recibo, revisión, resultados y límites.

## 7. Contraste especializado: pruebas y automatización GameMaker

Se revisaron primero el catálogo `11/_CATALOGO.md`, `13/10` §3–5 y el manual operativo
`12/09`. Ya están GM-TestFramework, crispy, Olympus, ganary y su árbol de elección. No falta
otro catálogo: interesa precisar **qué método añade cada herramienta** y cuánto de él se
ha demostrado para el proyecto de destino.

| Fuente fijada y licencia comprobada | Método útil y cobertura local | Elección y límite |
|---|---|---|
| [YoYoGames/GM-TestFramework](https://github.com/YoYoGames/GM-TestFramework/tree/1eb0853f2bd8b490ecc1633e4d8f6424a15c899a), `develop`, commit del 02-10-2026 16:48:19 UTC; [LICENSE Apache-2.0](https://github.com/YoYoGames/GM-TestFramework/blob/1eb0853f2bd8b490ecc1633e4d8f6424a15c899a/LICENSE) | Casos reproducibles del motor y comparación de resultados por runtime/compilador; ya explicado en `13/10` §4.1 | Consultar sus casos al aislar un bug del motor. Su [orquestador](https://github.com/YoYoGames/GM-TestFramework/blob/1eb0853f2bd8b490ecc1633e4d8f6424a15c899a/classes/commands/IgorRunTestsCommand.py) fija Igor Windows x64; no adoptarlo como CI portátil |
| [bscotch/olympus](https://github.com/bscotch/olympus/tree/2e8a34f065facabc6133225005c3591755652f04), `develop`, commit del 13-05-2024 19:18:16 UTC; [MIT](https://github.com/bscotch/olympus/blob/2e8a34f065facabc6133225005c3591755652f04/LICENSE.md) | Registro JSON, eventos asíncronos, reinicio tras crash y feedback humano; aparece en el catálogo y en la elección de `13/10` §4.3 | Evaluarlo si el banco del juego necesita esas capacidades. El [README](https://github.com/bscotch/olympus/blob/2e8a34f065facabc6133225005c3591755652f04/README.md) declara GameMaker 2024.4+ y API cambiante; esa declaración no es una prueba en LTS 2026, GMRT ni todos los targets |

Hay un matiz de host importante: GM-TestFramework incluye un
[wrapper de arranque Bash](https://github.com/YoYoGames/GM-TestFramework/blob/1eb0853f2bd8b490ecc1633e4d8f6424a15c899a/launcher2.sh)
con ramas de preparación para macOS/Linux, pero el orquestador leído usa `igor.exe` de
Windows x64 y el [workflow LTS2026](https://github.com/YoYoGames/GM-TestFramework/blob/1eb0853f2bd8b490ecc1633e4d8f6424a15c899a/.github/workflows/LTS2026.yml)
corre en Windows. El wrapper no acredita automatización completa desde esos otros hosts.
Tampoco ejecutar la suite con una versión de runtime valida automáticamente otra versión,
compilador o target. Se leyó también `tf_compare.py`; no se ejecutó ni se asumió que fuera
un comparador local sin efectos externos.

El aporte incremental de la [documentación de Olympus](https://github.com/bscotch/olympus/blob/2e8a34f065facabc6133225005c3591755652f04/src/datafiles/Olympus/Olympus_README.md)
es hacer explícitos `passed`, `failed`, `skipped` y `crashed`: recuperar una suite después
de caer identifica el caso y permite continuar, **no convierte el crash en aprobado**.
También separa la aserción programática del juicio humano sobre imagen/sonido. Esos estados
son transferibles al recibo de la biblioteca sin importar el framework. Su registro vive
en el área de guardado y su manejo de excepciones debe coordinarse con el del juego.

Para elegir, empezar por la frontera que falta: lógica pequeña → banco existente de `13/10`
§3; descubrimiento y fixtures → crispy ya documentado; reproducción de un bug del motor →
GM-TestFramework; async, continuidad tras crash o confirmación humana estructurada → evaluar
Olympus. Stitch es una vía de importación de este último, no una obligación metodológica.
Ninguno demuestra diversión, accesibilidad sensorial o compatibilidad de todos los targets.
No se recomienda instalar otro paquete si el banco actual puede representar la misma prueba.

**Resultado de esta ampliación:** dos repositorios especializados contrastados en fuentes,
sin demos, compilación, integración ni comparación A/B ejecutadas. Aportan precisión al método
de prueba y elección; no justifican reemplazar el flujo Matt ni añadir otro orquestador.
