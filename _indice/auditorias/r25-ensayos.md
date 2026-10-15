# r25 · Ensayo nativo de activación y asesoría

15-10-2026. Codex CLI 0.162.1, modelo configurado **gpt-6.1-sol**, esfuerzo **xhigh**, macOS arm64.
El usuario indicó continuar con Codex. Claude 2.1.300 devolvió error OAuth antes de usar tokens;
no se reconfiguró ni se cambió a otro modelo o autenticación. No se atribuye ejecución a Claude.

## Protocolo y observación

Fixture desechable de planificación, sin juego ni recursos; copia de la skill r50 en
`.agents/skills/gamemaker-biblioteca`. Petición literal sin nombre de skill. Sandbox de lectura,
configuración/modelo del CLI conservados; sin crear `.yy`/`.yyp`, compilar ni ejecutar juegos.
Las llamadas nativas y el resultado se cotejaron en el rollout completo de padre e hijo.
Los [datos públicos](r25-ensayos/positivo.json) conservan IDs reales, hashes, comandos
anonimizados y consumo; las reglas personales y el texto cifrado quedan fuera.

| Caso | Carga GameMaker | Asesor invocado | Resultado |
|---|---|---|---|
| Nuevo plataformas 2D, definición antes de crear proyecto | Entrada y referencias de desarrollo/asesor | **1** spawn real, `fork_turns=none`; respuesta recibida y contrastada | Preguntas y validación inicial, sin crear recursos |
| Corrección de tildes ajena a GameMaker | No | **0** | Frase corregida |
| Firma de `keyboard_check_pressed`, runtime explícito | Entrada, entorno y consulta API | **0** | Firma y Bool contrastados con índice/manual |

El padre y el [hijo asesor](r25-ensayos/asesor.json) declaran gpt-6.1-sol en `turn_context`.
El asesor no ejecutó herramientas ni delegó; no se pasó el historial de la conversación.
El anfitrión sí inyectó reglas y catálogo globales en el contexto fresco. La respuesta del
asesor identifica hechos, pendientes, preguntas, propuestas y prueba de definición; el
integrador incorporó su recomendación antes de presentar las preguntas al usuario.

## Coste y límites

| Caso | Entrada acumulada | Entrada en caché | Salida | Tiempo |
|---|---:|---:|---:|---:|
| Positivo, padre | 737.321 | 658.816 | 5.879 | 163,26 s |
| Asesor | 40.006 | 0 | 963 | Incluido en el recorrido anterior |
| Negativo de dominio | 40.388 | 0 | 88 | 9,84 s |
| Firma puntual | 344.503 | 278.144 | 2.186 | 78,47 s |

Son contadores acumulados del host, no tamaño del brief ni coste monetario; no se suman
ciegamente padre e hijo porque el alcance de agregación puede variar. La cuota está
condicionada por el catálogo global y las reglas externas. No se demuestra ahorro causal
ni se promete un número de tokens: la política evita consulta rutinaria, historial completo
y cascadas, y conserva la calidad por evidencia y aclaración acotada.

La llamada de spawn y el brief se almacenan cifrados por el host; se conserva su huella,
no se descifran. La recomendación y la identidad del hijo son observables. El campo
«herencia no verificada» de la respuesta fue contrastado por el integrador contra el
`turn_context` real de ambos. Se verifica transporte y comportamiento de estos casos;
no todas las decisiones costosas, atascos, modelos, agentes o juegos posibles.

## Intentos previos y error del instrumento

Se conservaron dos pasadas exploratorias con `--ephemeral` y un diagnóstico explícito de
transporte. Las pasadas naturales cargaron la entrada, pero el JSONL no mostraba spawn;
esa ausencia **no permite concluir que no hubiera asesor**. La inspección de código
oficial y la repetición sin ephemeral revelaron el backend **multiagente V2**, que no emite
el evento público de spawn. Su wait puede mostrar destinatarios vacíos. El rollout sí
conserva la llamada y la identidad del hijo. Se reforzó el gate de consulta antes de la
segunda pasada; no se atribuye una mejora causal a esa edición.

`--ignore-rules` se usó en la muestra final y controles para limitar reglas externas, pero
no eliminó toda la inyección del anfitrión ni el catálogo global; no es un agente virgen ni
un control sin otras guías. Los prompts y criterios se mantuvieron entre muestras comparables.
Una respuesta que dice «consulté» no habría bastado sin la llamada, el hijo y su resultado.

Fuente del comportamiento de eventos: [spawn V2 del CLI fijado](https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs),
[selección de backend](https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/core/src/config/mod.rs).

La entrada, desarrollo y política asesora del candidato público coinciden byte a byte con el fixture ensayado. Después se corrigió el localizador de biblioteca y se regeneró el índice para el corpus público; esos cambios tienen pruebas propias y no se atribuyen al ensayo asesor anterior.
