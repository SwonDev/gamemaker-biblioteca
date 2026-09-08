# Auditoría r5 · El flujo obligatorio — de «hazme un juego» a una especificación ejecutable

> 8 de septiembre de 2026 · 50 temas evaluados · 21 cubiertos (2 a otra escala) · 9 parciales · 20 faltan
> Referencia: GameMaker LTS 2026.0 (IDE `2026.0.0.16` · runtime `2026.0.0.23`).
> Notación `NN/MM §S` = carpeta `NN - .../MM - ....md`, sección `S`. Todas las citas de línea se
> comprobaron leyendo el archivo entero en esta sesión, no de memoria.

## Resumen ejecutivo

**No, un agente no puede evitar ponerse a picar código a ciegas leyendo solo esta biblioteca —
y no porque falte contenido de diseño, sino porque el contenido que sobra no está enganchado al
único momento en que hace falta: el primer minuto de la conversación, antes de que exista
ningún archivo.**

La pieza que resuelve **cómo se ve una buena especificación** es excelente y no hace falta
tocarla: `13/14 §6` (la «versión para LLM» de la ficha de sistema, con reglas numeradas, rangos,
recorte explícito y criterio de aceptación) y `13/14 §7` (de esa ficha a los recursos concretos
de GameMaker, al orden de construcción y a las tarjetas del tablero) son, literalmente, el
documento que el brief pedía comprobar — y superan la prueba. El ejemplo completo de «Luz de
Ámbar» (`13/14 §6.3`, 83 líneas) es una especificación que un agente puede implementar sin
inventar nada.

**El problema está una capa antes.** Ese ejemplo, y toda la plantilla de `13/01 §8.1`/`13/14
§2`, dan por hecho que alguien **ya rellenó los campos** — pitch, público, plataforma, recorte —
antes de que empiece la sección que el agente lee. Nada en la biblioteca dice **cómo se llega**
de «hazme un juego de plataformas» (una frase) a esos campos rellenos, salvo preguntándole al
usuario. Y sobre esa conversación —qué preguntar, cuántas preguntas, cuándo parar, qué asumir si
el usuario dice «lo que veas»— **no hay ni una palabra en ningún documento de esta biblioteca**.
Verificado con `grep` sobre el árbol completo de documentación propia (carpetas `01` a `13`,
excluidos `09 - Manual oficial` por ser espejo, `11 - Código descargado` por ser código de
terceros, y `Lumbre/`/`GameMaker_Fuentes/` por no formar parte de la biblioteca): cero apariciones
de «preguntar» en un sentido de elicitación agente↔usuario (las que aparecen son diálogo de NPC o
UX de dificultad), cero de «entrevista», «cuestionario» o «AskUserQuestion».

**Y no hay imposición.** Es el punto 3 del encargo, y la respuesta es tajante: `SKILL.md` (línea
151-165, «Flujo para un desarrollo real») dice en su paso 1 «Plano: lee estos cinco documentos» —
un verbo de **lectura**, no de **producción**— y pasa directo al paso 2, «Proyecto: `gm-cli
init`». `AGENTS.md §5` (línea 190-217) es todavía más débil: su paso 1 es condicional («si el
encargo incluye diseñar…») y su paso 3 crea el proyecto sin que haya existido ningún paso 0 de
especificación. Y el documento de arquitectura al que ambos remiten, `13/06 §2` («El método, paso
a paso»), **empieza literalmente en el paso 1 con «Crear el proyecto con el CLI»** — cero mención
a que exista un documento de diseño antes. Ninguno de los tres puntos de entrada por los que un
agente llega al código tiene una puerta que le impida saltarse el diseño. La skill de terceros
`gamemaker-expert` (que `SKILL.md` dice, en su última sección, que «sus patrones de arquitectura sirven») tampoco
la tapa: es referencia pura de API/patrones, cero elicitación, verificado leyendo su `SKILL.md`.

En números: de los 50 temas granulares de este informe, los que **ya existen** son casi todos los
de «cómo se ve una especificación buena» y «cómo se trocea en tareas» (categorías B y C de la
tabla) — la mitad del problema del brief. Los que **faltan casi todos** son los de «cómo se
consigue esa especificación hablando con un humano que solo dijo una frase» (categoría A) y «qué
la obliga a existir» (categoría F) — la otra mitad, y la que da título a esta ronda.

## Tabla tema por tema

Leyenda: ✅ Cubierto y ejecutable por un agente · 🟡 Parcial (documenta pero no permite ejecutar
sin adivinar, o cubre el concepto a otra escala) · 🔴 Falta.

### A · Elicitación: qué preguntar al usuario y cuándo parar (12)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 1 | Lista de 5-8 preguntas mínimas que cambian el diseño, formulada como tal | 🔴 | Ninguna | Ver «Encargo» #1. Los *campos* existen (`13/01 §8.1`, `13/14 §2`) pero como casillas de un documento ya escrito, nunca como guion de preguntas para una conversación |
| 2 | Criterio explícito de cuándo dejar de preguntar | 🔴 | Ninguna | Ni un número máximo de preguntas, ni un criterio de «pregunta solo si la respuesta cambia el sistema 1» |
| 3 | Defaults declarados para «lo que veas» / «sorpréndeme» / silencio del usuario | 🔴 | Ninguna | `grep` de «lo que veas», «sorpréndeme», «tú decides» en la biblioteca: 0 resultados relevantes a elicitación (los 5 que hay son código, no diseño) |
| 4 | Formato de la interrogación (una pregunta cada vez, en bloque, o con una herramienta de opción múltiple) | 🔴 | Ninguna | La biblioteca es agnóstica de CLI a propósito (`$BIB` sirve a Claude Code, Codex, OpenCode…), así que no debe nombrar `AskUserQuestion`, pero **sí** debería decir «en un solo turno, no en un interrogatorio secuencial» — hoy no dice ni eso |
| 5 | Pregunta de género y referencia («X se encuentra con Y») | 🟡 | `13/14 §1.4` da la fórmula del pitch y `13/01 §8.1` pide «Referencias» como casilla | La fórmula está pensada para **redactar** el pitch de un juego ya decidido, no para **preguntarle** al usuario por sus referencias al inicio de la conversación |
| 6 | Pregunta de alcance (¿algo jugable hoy, o un juego completo en semanas?) | 🟡 | `13/11 §1.1` («tu primer juego terminado tiene que ser pequeño») da el criterio correcto | Es una máxima para un humano planificando semanas, no una pregunta que el agente le haga al usuario en el primer turno para calibrar cuánto va a construir hoy |
| 7 | Pregunta de plataforma de destino (cambia el input desde el sistema 1) | 🟡 | `13/14 §2.5`, tabla completa de qué cambia por plataforma (PC/consola/móvil) | La tabla es correcta y citable, pero nada dice que esta sea una de las primeras preguntas — un agente puede leer `13/14` entero (897 líneas) y no llegar a la conclusión de que debe preguntarlo **antes** de crear el proyecto |
| 8 | Pregunta de arte: ¿aporta el usuario sprites/sonidos o los genera el agente? | 🟡 | `04/00` no la tiene; `SKILL.md:119` remite a «`12/09 §7` (gráficos) y `13/09 §8 bis` (sonido)» **cuando ya hace falta el recurso**, no como pregunta previa | Está resuelto el «cómo» (placeholders por código, verificado en `r4-agente-ia-gamemaker.md` #59-60) pero no el «cuándo preguntarlo» |
| 9 | Pregunta de historia/narrativa: ¿sí o no, y cuánta? | 🔴 | Ninguna | `13/14 §2.11` tiene la casilla del GDD completo («Personajes, mundo y narrativa»), pero nunca se plantea como pregunta de arranque |
| 10 | Pregunta de un jugador frente a multijugador (local/online) | 🔴 | Ninguna | Cambia la arquitectura desde el primer sistema (input, cámara, guardado); `04/14` resuelve la implementación de multijugador una vez decidido, no ayuda a decidirlo |
| 11 | Pregunta de para qué es el juego (probar/aprender · subir gratis · vender) como filtro de cuánta producción real hace falta | 🟡 | `13/20 §6.1` («el modelo se elige... antes de programar el primer sistema») da el criterio de que debe decidirse pronto | No está planteado como pregunta al usuario; y calibra directamente si aplican las fases de `13/11 §2` (que son de producción real) o si el agente puede saltárselas por completo |
| 12 | Detectar que la petición inicial ya trae suficiente información y saltar preguntas redundantes | 🔴 | Ninguna | Sin criterio, un agente disciplinado que intente aplicar el punto 1 (si existiera) volvería a preguntar género a alguien que ya escribió «un metroidvania de dos horas, como Hollow Knight pero sin combate» |

### B · De la respuesta a la especificación escrita (10)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 13 | GDD de una página — plantilla | ✅ | `13/01 §8.1` (líneas 836-858): pitch, MDA, referencias, plataforma, verbos, los tres bucles, recorte, riesgo, métrica de éxito | — |
| 14 | Ficha por sistema — plantilla | ✅ | `13/01 §8.2` (líneas 860-884): entradas, salidas, estado, reglas numeradas, tabla de balance con rango, interacciones, feedback, casos borde, telemetría | — |
| 15 | Criterio de cuándo basta el one-pager y cuándo hace falta el GDD completo | ✅ | `13/14 §1.1` (líneas 25-50): 4 señales — equipo >1, publisher/financiación, proyecto >2 semanas, o **un LLM va a implementar veinte sistemas** (la señal 4 es literalmente el caso de uso de esta biblioteca) | — |
| 16 | Plantilla GDD completo, por 19 secciones con «qué va / qué NO va / dónde está ya resuelto» | ✅ | `13/14 §2` (tabla de líneas 191-222) + plantilla lista para copiar en `§3.4` (líneas 410-463) | — |
| 17 | Versión para LLM de la ficha de sistema (reglas numeradas, rango, recorte, símbolos GML probables, fuera de alcance) | ✅ | `13/14 §6.2` (líneas 551-567) | — |
| 18 | Ejemplo real, completo, de principio a fin, verificado símbolo por símbolo | ✅ | `13/14 §6.3` («Luz de Ámbar», líneas 575-659): 3 sistemas fichados, recorte explícito, criterio de aceptación | — |
| 19 | Cómo se deriva el «recorte explícito» de una conversación en la que el usuario no lo mencionó | 🔴 | `13/14` da el campo (`§2` fila «recorte», `§6.1` punto 3) y por qué importa, pero nunca el **proceso** de sacarlo de un usuario que solo pidió «un plataformas» | Sin proceso, el agente tiene que inventarse qué recortar — justo el fallo que la biblioteca entera existe para evitar con símbolos de GML, sin cubrirlo aquí |
| 20 | Trazabilidad: qué decidió el usuario frente a qué asumió el agente por defecto | 🔴 | Ninguna sección de ninguna plantilla la distingue | Sin esto, si el usuario dice después «yo no pedí que hubiera historia», no hay forma de que el agente (o una persona revisando el documento) vea que fue un default, no un acuerdo |
| 21 | Dónde vive el archivo de spec dentro del proyecto de GameMaker | ✅ | `13/14 §3.1-3.2` (líneas 342-388): recurso `Notes`, comando `resource create type=notes` + `NOTE SETFILEPATH`, con el hallazgo verificado de que `SETFILEPATH` no refresca un `Note` ya asignado (hay que borrar y recrear) | — |
| 22 | Verificación de símbolos GML en la fase de spec, antes de comprometerlos a la ficha | ✅ | `13/14 §6.2` («el agente los verifica igualmente con `buscar.py`») + `§6.4` paso 2 | — |

### C · Troceo en tareas y orden de construcción (8)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 23 | Orden entre sistemas de un GDD con varios sistemas fichados | ✅ | `13/14 §7.2` (líneas 728-776): tabla de 8 categorías (núcleo de movimiento → cámara → pilar principal → combate → UI → guardado → audio → pulido) y el método de la tabla de interacción como grafo de dependencia | — |
| 24 | De cada campo de la ficha de sistema al recurso concreto de GameMaker que produce | ✅ | `13/14 §7.1` (tabla de líneas 701-713): entradas→dependencia, salidas→señal o variable, estado→`obj_`/`global`/archivo según sea por-instancia o compartido, reglas→evento o función | — |
| 25 | De cada regla de la ficha a una tarjeta del tablero | ✅ | `13/14 §7.3` (líneas 778-806): ejemplo completo, seis tarjetas de un sistema de 15 líneas | — |
| 26 | Primer hito jugable calibrado a la duración de **una sesión de agente** (no de semanas) | 🔴 | `13/11 §2` da fases (prototipo 10 %, vertical slice 20 %…) pensadas para calendario humano en semanas/meses | Nada dice qué es «lo mínimo jugable» cuando el presupuesto real es una conversación de un rato, no un calendario — ver hallazgo de escala más abajo |
| 27 | Cuántos sistemas/tareas encadena un agente antes de compilar y mostrar algo | 🟡 | `13/14 §6.4` paso 4: «comprobando después de cada sistema con `gm-cli compile`, en vez de esperar a tener los tres niveles enteros» — buen criterio de *cadencia de compilación* | No dice nada sobre la cadencia de **reportar al usuario** (¿tras cada sistema? ¿al terminar el primer sistema jugable?), que es una pregunta distinta de cuándo compilar |
| 28 | Orden de montaje del esqueleto técnico vacío (Git, `scr_config`, `obj_game`, primer sistema vertical) | ✅ | `13/06 §2` (líneas 76-98), 10 pasos, «los pasos 1-6 caben en una tarde» | — |
| 29 | Empalme explícito entre el orden de sistemas de diseño (`13/14 §7.2`) y el orden de montaje técnico (`13/06 §2`) | 🟡 | `13/14 §7.2` cita a `13/06 §2` como lo que pasa «una vez, al principio»; `13/06 §2` no cita nunca de vuelta a `13/14` ni a ningún documento de especificación | El enlace es de ida y no de vuelta (confirmado con `grep`: `13/06` no menciona `13/14` ni «GDD» en ningún sitio) — un agente que llegue a la arquitectura por `13/06` primero no se entera de que debería haber una ficha de sistema antes |
| 30 | Qué hacer si al dibujar la tabla de interacción aparece un ciclo de dependencia | ✅ | `13/14 §7.2` («si al dibujarlo aparece un ciclo… el diseño tiene un problema real») | — |

### D · Cómo se sabe que está terminado (8)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 31 | Checklist de «juego completo» (splash → menú → intro → bucle → muerte → endgame → créditos) | ✅ | `04/00` entero, checklist final (líneas 242-264) | — |
| 32 | Criterio de aceptación por sistema que no dependa de una opinión | ✅ | `13/14 §6.1` punto 4 y `§6.3 §10` (ejemplo: «los 3 niveles compilan, el salto cumple R1-R4, las 3 gemas de cada nivel son recogibles») | — |
| 33 | Estados de un sistema (idea · prototipo · implementado · balanceado) | ✅ | `13/01 §8.2` (cabecera de la ficha) | — |
| 34 | Diferencia entre «compila limpio» y «está terminado» | ✅ | `SKILL.md` trampa 4 (líneas 70-72) + `13/14 §6.4` paso 5 | — |
| 35 | Formato del reporte final que el agente da al usuario al cerrar una sesión | 🔴 | Ninguna | Ni una plantilla de «esto se hizo, esto quedó fuera y por qué, esto es lo siguiente» — el `AGENTS.md` exige reportar la salida real de `gm-cli compile` (regla dura, línea 186) pero no exige ni sugiere un resumen del propio alcance frente a la especificación |
| 36 | Checklist que la propia especificación debe traer, embebido en cada documento generado (pedido explícito del brief) | 🟡 | `13/14 §4` es un checklist real y bueno, pero es un checklist de **calidad del documento** («¿tiene pilares? ¿tiene recorte?»), que vive en `13/14` mismo, no una plantilla de checklist que se **copie dentro** de cada GDD que un agente escriba | Falta que la plantilla de `§3.4` incluya su propia sección `## Checklist de cierre`, generada a partir de las reglas + criterios de aceptación de cada sistema, para que la especificación sea autocontenida y no dependa de que el agente recuerde volver a `13/14 §4` |
| 37 | Qué hace el agente si no puede cumplir un criterio de aceptación (p. ej. una plataforma sin soporte) | 🔴 | Ninguna | Ni una palabra sobre qué reportar cuando un criterio de la propia especificación resulta inalcanzable a mitad de implementación |
| 38 | Vertical slice como puerta binaria «listo para producción» | ✅ (a otra escala) | `13/11 §1.4`, checklist de 10 casillas + 3 preguntas de Donovan (líneas 91-115) | Correcto y bien fundamentado (GDC 2015, Donovan), pero pensado para una porción de 10-20 min con arte y audio finales — desproporcionado como criterio de cierre de una sesión de agente que arranca de cero; ver hallazgo de escala |

### E · Qué se hace cuando el usuario cambia de idea a mitad (6)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 39 | ADR ligero cuando el código y el documento discrepan | ✅ | `13/14 §1.5` (líneas 166-174) + `13/11 §3.5` (líneas 255-278) | — |
| 40 | Feature creep y cómo se frena (lista congelada, cuaderno de ideas, pregunta de la puerta) | ✅ (a otra escala) | `13/11 §1.6` (líneas 133-149): 5 mecanismos concretos | Pensado para un equipo en semanas con hito de *feature complete*; no traducido a «el usuario acaba de pedir algo nuevo en el mismo turno de chat» |
| 41 | La matriz de recorte (coste bajo/alto × toca/no toca el core loop) | ✅ | `13/11 §1.5` (líneas 117-131) | — |
| 42 | Umbral: cuándo un cambio a mitad de sesión es un ajuste menor y cuándo exige reescribir el GDD | 🔴 | Ninguna | Sin este umbral, un agente no tiene forma de distinguir «cambia el color del enemigo» (ajuste) de «ahora quiero que sea un roguelike» (proyecto distinto) más que por criterio propio no verificable |
| 43 | Protocolo cuando el usuario pide algo que contradice el recorte explícito ya escrito | 🟡 | Existe una frase excelente, pero **solo dentro del ejemplo**: `13/14 §6.3` §9 («si el agente considera necesario añadir algo de esta lista, debe señalarlo como pregunta abierta, no implementarlo por iniciativa propia») | Verificado con `grep`: esa frase aparece **una sola vez en toda la biblioteca**, dentro del cuerpo del ejemplo «Luz de Ámbar». No está codificada como regla general en `§1`, `§4` o `§6.1` de `13/14`, así que un agente que lea la plantilla pero no ese ejemplo concreto no la conoce |
| 44 | Qué hacer con sistemas ya construidos que el cambio de idea invalida | 🔴 | Ninguna | Ni siquiera se plantea el caso — el ADR ligero asume que el cambio ya pasó y se documenta después, no que el agente tiene que decidir en vivo si sigue, para o deshace trabajo |

### F · La prueba de imposición: ¿algo obliga a esto antes de escribir GML? (6)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 45 | `SKILL.md` obliga a producir (no solo leer) una especificación antes de crear el proyecto | 🔴 | `SKILL.md:151-165`, paso 1 «Plano»: verbo «lee», no «escribe» ni «pregunta»; paso 2 ya es `gm-cli init` | Sin un verbo de producción y sin un gate, un agente cumple la letra del paso 1 con solo abrir los cinco documentos, sin escribir ni preguntar nada |
| 46 | `AGENTS.md §5` obliga a lo mismo | 🔴 | `AGENTS.md:192-195`, paso 1: condicional («si el encargo incluye diseñar…») y sin mandato de producir un archivo | Un agente que interprete «hazme un juego de plataformas» como un encargo ya diseñado (el género está dicho) puede saltarse el paso 1 entero de forma defendible con la letra actual |
| 47 | `13/06 §2` (a donde remiten ambos) tiene un paso 0 de especificación antes del paso 1 técnico | 🔴 | `13/06 §2` línea 81-83: su propio paso 1 es «Crear el proyecto con el CLI» | Confirmado con `grep`: `13/06` no cita a `13/14` ni a «GDD» en ningún punto del documento |
| 48 | La skill distingue «modo greenfield desde una frase» de «modo tarea puntual sobre un proyecto que ya tiene GDD» | 🔴 | Ninguna | El mismo flujo de 6-7 pasos de `SKILL.md`/`AGENTS.md` se aplica igual a «hazme un juego» que a «añade un enemigo a mi proyecto ya diseñado» — sin bifurcación, el primer caso hereda un flujo pensado para el segundo |
| 49 | Existe un gate equivalente a «no digas terminado sin compilar» pero para «no programes sin especificación» | 🔴 | `AGENTS.md` línea 186 tiene la prohibición dura de no dar nada por terminado sin `gm-cli compile` | No existe la prohibición simétrica del otro extremo del proceso |
| 50 | La skill de terceros `gamemaker-expert` (co-cargable, referenciada en `SKILL.md` líneas 174-178) compensa el hueco | 🔴 | Leído su `SKILL.md` completo (741 líneas, `~/.claude/plugins/cache/gamemaker-skills/gamemaker-expert/`): es una referencia de sintaxis GML, eventos, patrones y rendimiento — cero menciones a preguntar, GDD o especificación | Confirma que el hueco no está tapado por ningún otro componente ya presente en el entorno del usuario |

## Huecos por prioridad

### 🔴 Graves

1. **No existe la lista de preguntas de arranque, ni el criterio de parada, ni los defaults**
   (#1-4, #9-10, #12). Es el hueco que da título al brief: un agente que reciba «hazme un juego
   de plataformas» no tiene ningún documento que le diga qué preguntar, cuánto preguntar, ni qué
   asumir si el usuario contesta «lo que veas». Todo el aparato de plantillas (categoría B) asume
   que esas respuestas ya existen.

2. **Nada obliga a producir una especificación antes de crear el proyecto** (#45-49). Los tres
   puntos de entrada verificados (`SKILL.md` paso 1, `AGENTS.md §5` paso 1, `13/06 §2` paso 1) son
   compatibles con saltarse el diseño por completo y llegar a compilar de principio a fin sin
   haber escrito ni preguntado nada. No es un fallo de contenido: es un fallo de **secuencia
   obligatoria**.

3. **El «señalar como pregunta abierta en vez de implementar por iniciativa propia» —la regla más
   importante contra la invención de alcance— vive en un solo ejemplo y no como regla general**
   (#43). Es exactamente el mismo patrón que ya detectó una ronda anterior con `PENDIENTE-r3.md`:
   un hallazgo correcto que no está en el camino de lectura normal de un agente.

4. **No hay umbral entre «ajuste menor» y «cambio de proyecto» a media sesión** (#39-44). El
   aparato de feature creep (`13/11 §1.6`) y el ADR ligero (`§3.5`) están pensados para un equipo
   que revisa el alcance cada dos semanas, no para un agente que recibe «en realidad, que no
   tenga jefe final» en el mismo turno de chat en el que ya construyó tres salas.

### 🟠 Medios

5. **Toda la maquinaria de producción (`13/11`) está calibrada a semanas/meses de un humano, no a
   la sesión de un agente** (#6, #26, #38, #40). El contenido es correcto y no hay que reescribirlo,
   pero ningún documento traduce «vertical slice» o «feature complete» a la escala de una
   conversación de una tarde — un agente diligente que aplique `13/11 §2` literalmente a «hazme un
   juego» puede terminar planificando fases de semanas para una tarea que el usuario esperaba
   resuelta en la misma sesión.
6. **El enlace entre el orden de sistemas de diseño y el orden de montaje técnico es de ida y no
   de vuelta** (#29): `13/14 §7.2` cita a `13/06 §2`, pero `13/06` no cita nunca a `13/14` ni
   menciona que debería existir una ficha de sistema antes de tocar el CLI.
7. **No hay trazabilidad entre lo que decidió el usuario y lo que asumió el agente por defecto**
   (#20). Sin esto, ninguna especificación generada por un agente es auditable después: no se
   puede saber, leyendo el documento, si «no hay historia» fue una petición o un olvido.
8. **El checklist de cierre de `13/14 §4` no está embebido en la plantilla que se copia** (#36):
   vive en el documento madre, no en cada GDD que un agente escriba, así que depende de que el
   agente recuerde volver a consultarlo.
9. **No hay formato de reporte final al usuario** (#35, #37): la regla dura de reportar la salida
   real de `gm-cli compile` existe; la de reportar el alcance real frente al prometido, no.

### 🟡 Menores

- No hay bifurcación explícita entre «proyecto nuevo desde una frase» y «tarea puntual sobre un
  proyecto con GDD ya existente» (#48) — en la práctica muchos encargos («añade un enemigo»)
  no necesitan este flujo entero, y el documento no lo dice, aunque tampoco genera daño real
  porque un agente razonable no relee todo `13/14` para una tarea de una línea.
- La fórmula del pitch («X se encuentra con Y», `13/14 §1.4`) está escrita para redactar, no para
  preguntar; adaptarla a pregunta es trivial pero no está hecho.
- El criterio de «cuántos sistemas encadena un agente antes de reportar» (#27) se confunde
  fácilmente con «cuántos antes de compilar» (que sí está resuelto) — son preguntas relacionadas
  pero distintas y solo una tiene respuesta.

## Encargo para el redactor

1. **Nuevo documento `13/28 · De «hazme un juego» a una especificación — el protocolo de
   elicitación del agente`** (o una sección nueva `§0` al principio de `13/14`, antes de `§1`, si
   se prefiere no crear documento aparte — decisión del redactor, no de esta auditoría). Debe
   contener, con la misma exigencia de fuente/evidencia que el resto de la carpeta `13`:
   - **Las 5-8 preguntas de arranque**, en un solo bloque, formuladas como preguntas reales (no
     como casillas de plantilla): género y referencia («¿a qué se parece? "X se encuentra con
     Y"»), alcance de esta sesión (¿algo jugable hoy o un proyecto de varias sesiones?),
     plataforma y control de destino, arte (¿aportas assets o los genero yo?), historia sí/no,
     un jugador o multijugador, duración objetivo de partida, para qué es el juego (probar ·
     publicar gratis · vender). Fundamentar cada una citando el campo del GDD al que alimenta
     (`13/01 §8.1`, `13/14 §2`) para no inventar preguntas sin destino.
   - **El criterio de parada**: un solo turno, nunca un interrogatorio secuencial; repreguntar
     solo si la respuesta a alcance o plataforma es ambigua (son las dos que más cambian el
     sistema 1, según `13/14 §2.5` y `13/06 §2` paso 7).
   - **Los defaults por pregunta** cuando el usuario no responde o dice «lo que veas»/«sorpréndeme»,
     cada uno anclado a una regla ya existente de la biblioteca: alcance → el mínimo, nunca el
     máximo (`13/11 §1.1`, «tu primer juego terminado tiene que ser pequeño»); arte → placeholders
     generados por código (`12/09`, receta de PNG/WAV verificada por `r4-agente-ia-gamemaker.md`
     #59-60); historia → no, arcade puro; multijugador → un jugador; duración → sesión corta;
     para qué → para probar/aprender, no para publicar (evita arrastrar toda la maquinaria de
     `13/11` sin que el usuario la haya pedido).
   - **La sección «Premisas asumidas por defecto», distinta de «Decidido por el usuario»**, como
     bloque nuevo obligatorio en la plantilla de `13/14 §3.4` — cada campo del GDD que se rellenó
     con un default lleva una marca (por ejemplo `[DEFAULT]`) trazable hasta esta lista.

2. **Ampliar `13/14 §1` (o `§6.1`) con la regla general que hoy solo vive en el ejemplo**: mover
   (o citar como regla, no repetir) la frase de `§6.3 §9` («si el agente considera necesario
   añadir algo fuera del recorte, debe señalarlo como pregunta abierta, no implementarlo por
   iniciativa propia») a un lugar que un agente lea aunque no llegue al ejemplo completo — el
   candidato natural es como quinta condición de `§6.1` («Qué hace que un GDD sea
   "implementable"»), junto a las cuatro que ya hay.

3. **Nueva subsección en `13/14` (`§7.4` o similar): «Cuando el usuario cambia de idea a mitad de
   la implementación»**, con el umbral que hoy no existe: si el cambio **no** toca el core loop
   (mismo criterio de la matriz de recorte, `13/11 §1.5`), se trata como el ADR ligero ya
   documentado (`§1.5`, una línea, seguir); si **sí** toca el core loop o invalida un sistema ya
   fichado como «implementado», el agente **para** y pregunta explícitamente si reescribir la
   especificación desde el `§2.5` (público/plataforma) hacia abajo, en vez de parchear en
   silencio. Enlazar desde aquí a `13/11 §1.6` (feature creep) y `§3.5` (ADR) sin repetirlos.

4. **Añadir un paso 0 explícito en los tres puntos de entrada verificados**, todos apuntando al
   documento nuevo del encargo #1:
   - `SKILL.md`, antes del actual paso 1 de «Flujo para un desarrollo real» (línea 151): un paso
     0 que diga, en el mismo tono imperativo que el resto de la sección, «si la petición es
     "hazme un juego" y no trae ya género+alcance+plataforma decididos, **haz las preguntas de
     `13/28` antes de leer nada más** y escribe la especificación antes de tocar `gm-cli init`».
   - `AGENTS.md §5` (línea 190), mismo tratamiento, sustituyendo la condicional actual («si el
     encargo incluye diseñar…») por una regla verificable: «si el encargo no trae ya una
     especificación (un GDD, una ficha de sistema, o las respuestas a las preguntas de `13/28`),
     ES que incluye diseñar».
   - `13/06 §2` (línea 76): añadir una línea antes del paso 1 actual («Crear el proyecto con el
     CLI») que diga que este método de montaje asume que ya existe una especificación (`13/14`) y
     enlace hacia atrás — hoy el enlace solo existe en la dirección `13/14 → 13/06`.

5. **Sección nueva en `13/11` (o nota en `§1.4`): «Vertical slice y fases de producción, a escala
   de una sesión de agente»**, aclarando explícitamente que las fases de `§2` (prototipo 10 %,
   vertical slice 20 %…) y el checklist de vertical slice de `§1.4` están calibrados a un
   calendario humano de semanas/meses, y que para una especificación de `13/28` con alcance de
   «una sesión», el criterio de cierre correcto es el de `13/14 §6.1` punto 4 (criterio de
   aceptación por sistema) y el checklist de `04/00`, no las puertas de fase de `13/11 §2`.

6. **Sección `## Checklist de cierre`, embebida en la plantilla de `13/14 §3.4`**, generada a
   partir de las reglas y criterios de aceptación de cada sistema que el propio documento ya
   contiene, para que cada especificación que un agente escriba sea autocontenida (no dependa de
   que el agente recuerde volver a `13/14 §4` para saber si terminó).

7. **Plantilla de reporte final al usuario**, nueva, corta (10-15 líneas): qué se construyó, qué
   quedó en el recorte y por qué, qué preguntas quedaron abiertas (si las hay, por la regla del
   encargo #2), y el resultado real de `gm-cli compile`. Candidato natural: una subsección nueva
   de `13/14 §6.4` («Cómo lo usaría un agente, paso a paso»), como paso 7 después del actual
   paso 6.

### La plantilla concreta de especificación mínima (propuesta para el encargo #1)

Estructura completa, lista para que el redactor la valide y la incorpore. Extiende el one-pager
de `13/01 §8.1` (que no se toca ni se duplica) con los bloques que hoy faltan:

```markdown
# <Título> · Especificación de sesión          versión: 0.1 · fecha: AAAA-MM-DD

## 0 · Preguntas y respuestas
(las 5-8 preguntas de arranque del encargo #1, con la respuesta real del usuario o
 la marca [DEFAULT] si no respondió — trazabilidad exigida por el hallazgo #20)
1. Género y referencia:
2. Alcance de esta sesión:
3. Plataforma y control:
4. Arte (aporta el usuario / lo genera el agente):
5. Historia (sí/no, cuánta):
6. Jugadores (uno / local / online):
7. Duración objetivo de partida:
8. Para qué es (probar · publicar gratis · vender):

## 1 · GDD de una página
(la plantilla completa de 13/01 §8.1, sin repetirla — pitch, MDA, verbos, bucles,
 recorte, riesgo, métrica de éxito; cada campo alimentado por el bloque 0)

## 2 · Sistemas
(una ficha de 13/14 §6.2 por sistema — reglas numeradas, rango, símbolos GML
 probables, fuera de alcance — mínimo el sistema que sostiene el pilar principal)

## 3 · Orden de construcción
(aplicar la tabla de categorías de 13/14 §7.2 a los sistemas fichados en el bloque 2)

## 4 · Checklist de cierre
(generado a partir de "Cómo se prueba" de cada ficha del bloque 2 — encargo #6)

## 5 · Qué hacer si el usuario cambia de idea
(el umbral del encargo #3: ¿toca el core loop? → parar y reescribir desde el
 bloque 0; ¿no lo toca? → ADR de una línea, 13/11 §3.5, y seguir)
```

## Lo que comprobé y NO hacía falta

- **`13/14 §6` (versión para LLM) y `§7` (de la ficha al proyecto), enteros.** Leídos línea a
  línea. Son la mejor pieza de toda la biblioteca en este dominio y ya resuelven exactamente lo
  que prometen: un sistema fichado se implementa sin inventar nada, se ordena entre sí sin
  inventar dependencias, y se trocea en tarjetas de un día sin inventar el proceso. No hace falta
  tocar ni una palabra de estas dos secciones.
- **`13/01 §8` (GDD de una página y ficha por sistema).** Plantillas correctas, ya validadas por
  la auditoría de ronda 2 (`diseno-gdd.md` A2, A4). No reabrir.
- **`04/00` (anatomía + checklist de juego completo).** Correcto para lo que hace: el mapa de
  escenas y el checklist final de qué tiene que existir en un juego que se publica. No es el
  documento que falta (ese es el de elicitación), pero no tiene ningún defecto propio.
- **`13/11` completo, como contenido de producción.** Alcance, estimación ×3, vertical slice
  (con la cita correcta de Donovan, GDC 2015), matriz de recorte, feature creep, tablero de
  cuatro columnas, ADR ligero, ciclos quincenales. Todo verificado y correcto — el único hallazgo
  es de **escala** (no está adaptado a una sesión de agente), no de contenido. No reescribir el
  documento: añadir la nota de escala del encargo #5.
- **Las plantillas de `13/11 §8.1-8.4`** (alcance de una página, vertical slice, plan de hitos,
  press kit). Correctas para su propósito de producción real; no se tocan.
- **`SKILL.md` y `AGENTS.md` como prohibiciones duras de GML** (no inventar símbolos, no editar
  `.yy`/`.yyp` a mano, compilar antes de decir terminado). Ese aparato funciona exactamente como
  debe — el hueco está específicamente en la ausencia de un aparato equivalente para el diseño,
  no en lo que ya existe para el código.
- **`_indice/auditorias/diseno-gdd.md` (A1, A3, A6, A7, A8)**: confirmado que los cinco huecos que
  esa auditoría de ronda 2 señaló sobre el contenido del GDD (documento completo, pilares, pitch,
  diagramas, público/plataforma) están cerrados por `13/14`. No es el mismo hueco que reporta esta
  ronda: aquel era «¿existe la plantilla?» (sí, ya existe y es buena); este es «¿algo hace que un
  agente la rellene con las respuestas correctas y la escriba antes de programar?» (no).
- **`_indice/auditorias/r4-agente-ia-gamemaker.md` y `12/09`**: dominio distinto (mecánica del CLI:
  plantillas rotas, numeración de eventos, cuelgues de `resourcetool`), sin solape real con esta
  ronda. Confirmado leyendo `12/09` entero por si tocaba de refilón la elicitación: no la toca.
- **La skill de terceros `gamemaker-expert`** (`~/.claude/plugins/cache/gamemaker-skills/`), leída
  entera (741 líneas) para comprobar si compensaba el hueco por estar co-cargable. No lo hace: es
  referencia pura de sintaxis/patrones GML.

## Lo que encontré desactualizado

Ninguna afirmación con fecha de caducidad de esta biblioteca resultó falsa en este dominio — el
hallazgo de esta ronda no es «algo que era cierto y dejó de serlo», es «un proceso que nunca
existió». No hay, por tanto, nada que fechar como desactualizado; el único matiz es de **escala**
(§ «Huecos 🟠» #5): `13/11` no está mal ni caducado, está calibrado a un calendario que no es el
de la mayoría de las sesiones en las que un agente recibe «hazme un juego».
