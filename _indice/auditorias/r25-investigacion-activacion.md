# r25 · Activación natural y asesoramiento portátil

Consulta: **15-10-2026**. Alcance: investigación y propuesta para r50; no ensayo con LLM. Se leyeron la skill r49,
desarrollo/evidencia, contratos/aprendizaje, instalación y r24. Esta investigación no instaló agentes, hooks ni ajustes; no
cambió modelos ni consultó juegos. Context7 respondió «Monthly quota exceeded»; se contrastó con documentación oficial
actual y código oficial fijado.

## 1. Resumen de la decisión

La entrada debe reconocer «quiero hacer un juego con GameMaker» sin exigir nombres de skills. El mecanismo real sigue siendo
selección por metadatos: ningún `description` garantiza que todos los modelos la activen siempre. Conviene anunciar pronto
el caso de uso, cargar solo las referencias de esa fase y registrar la lectura observada.

Recomiendo un **contrato portátil de asesoramiento**, invocado con la delegación disponible, un brief acotado y el modelo
actual confirmado. Consulta al iniciar un juego, antes de una decisión costosa de revertir y al estancarse. La consulta
entrega alternativas, riesgos, prueba decisiva y recomendación; el integrador contrasta y decide dentro del encargo.

El advisor nativo de Claude permanece opcional y requiere autorización/configuración previa. No conviene activarlo desde el
instalador. Sin delegación, se informa «autorrevisión» y sus límites; no se inventa un asesor independiente. El crítico
final es otro contexto, sin el consejo inicial ni la explicación del constructor. Las pruebas de r24 no acreditan estas
invocaciones: falta un ensayo nativo con disparador natural, negativo y trazas.

## 2. Base local y garantías comprobadas

| Evidencia | Resultado | Lo que permite afirmar |
|---|---|---|
| `claude --version`, `--help` | Claude Code **2.1.300**, salida 0 | CLI y formatos de salida disponibles; no prueba cuenta ni advisor |
| `codex --version`, `--help` | Codex CLI **0.162.1**, salida 0 | Versión del CLI; no certifica la app de escritorio |
| `codex features list` | Salida 0; `multi_agent stable true`; `multi_agent_v2 stable false` | El flag local de multiagente está activo; no se cambió |
| `codex exec --help` | `--json`, `--cd`, `--output-last-message` | Permite preparar captura nativa de eventos, aún no ejecutada |
| `codex debug prompt-input --help` | Renderizador documentado | Puede probar catálogo visible; no demuestra selección ni consulta |
| r24, control y variante final | Ambos 5/5; carga solicitada explícitamente | Ausencia de regresión en ese escenario, sin ventaja causal ni autoactivación demostrada |

`instalar.sh` ya valida, copia/enlaza y conserva respaldo; `harnesses.py` ya centraliza destinos. Reutilizarlos evita otro
instalador o una segunda configuración de modelos. Los recibos [Pi/OMP](r22-harnesses-pi-omp.md) y
[MiniMax/Hermes/Gentle](r22-harnesses-minimax-hermes-gentle.md) prueban loaders concretos, sin conversación LLM. Esa
evidencia histórica no acredita la nueva ruta de asesoramiento.

## 3. Metadatos, referencias y recarga

**Codex.** La [documentación oficial](https://learn.chatgpt.com/docs/build-skills) describe activación explícita e implícita
por `description`, carga progresiva y acortamiento u omisión de descripciones cuando el catálogo excede su presupuesto. Hay
que poner GameMaker/GML y «hacer un juego» al principio. `agents/openai.yaml` es metadato del harness, no un subagente. El
código de
[SkillMetadata](https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/skills/src/model.rs)
confirma que `policy.allow_implicit_invocation` ausente equivale a `true`; el
[parser](https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/ext/skills/src/loader/metadata.rs)
acepta ese campo. `true` habilita la selección; no impone ejecutar la skill.

**Claude Code.** Su [guía de skills](https://code.claude.com/docs/en/skills) documenta `description` y `when_to_use`; el
segundo añade contexto de activación específico de Claude. `disable-model-invocation: true` impide selección automática.
`user-invocable: false` oculta el comando al usuario, sin impedir selección por Claude. Para portabilidad basta una
descripción clara compartida; no depender de `when_to_use` en otros harnesses. Los archivos en `references/` se enlazan con
condición de lectura; no se cargan todos por existir ni heredan una invocación automática independiente.

**Anidación.** Una skill en un subdirectorio de proyecto depende del descubrimiento del host y del acceso a ese ámbito. No
esconder la única puerta GameMaker en una subcarpeta todavía no descubierta. Mantener una entrada instalada y referencias de
fase a un salto.

**Recarga actual.** Codex detecta cambios de skills; reiniciar si no aparecen. Cambiar `config.toml` sí requiere reinicio
según su guía. Claude vigila `SKILL.md`; si el directorio superior de skills no existía al arrancar, usar `/reload-skills`.
Componentes de plugin distintos de `SKILL.md` pueden requerir `/reload-plugins`. No afirmar «siempre reinicia».

## 4. Delegación y preservación del modelo

La [guía de subagentes Claude](https://code.claude.com/docs/en/sub-agents) establece que `model: inherit` selecciona el
principal. Omitir `model` deja actuar al default ambiental; el parámetro por invocación puede prevalecer. `skills:` precarga
contenido completo, por lo que una biblioteca extensa allí puede duplicar contexto. Un agente ordinario recibe su prompt y
el contexto que se le transmite; no hereda toda la conversación como un fork. La definición de agente puede limitar
herramientas a lectura. Evitar Bash si no hace falta.

La [guía de subagentes Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents) documenta agentes TOML en
`.codex/agents/` o `~/.codex/agents/`, y `agents.enabled` con default `true`. Los defaults `[agents]`, parámetros de spawn y
archivos personalizados pueden afectar al modelo efectivo. Omitir `model` no demuestra por sí solo herencia. Se conservan
proveedor, permisos y MCP del padre; pedir «solo lectura» no crea por sí solo otro sandbox. No introducir flags
experimentales ni reescribir configuración personal.

Por tanto: pedir herencia mediante la API real disponible, comprobar identidad efectiva y registrarla. Si el host no permite
confirmar el modelo, declarar «herencia no verificada»; no sustituirlo por un alias rápido, económico o supuestamente
superior. Si el usuario fijó otro modelo asesor, usar exactamente ese bajo su autorización y comprobar disponibilidad.

Claude vigila agentes en directorios ya existentes; la primera creación del directorio, agentes de `--add-dir` o una sesión
sin comandos pueden exigir reinicio. No se encontró una garantía equivalente de recarga de agentes Codex en la página
consultada: verificar catálogo efectivo o usar sesión fresca; no extrapolar la recarga de skills a agentes.

## 5. Advisor nativo: límites vigentes

La [página oficial de advisor](https://code.claude.com/docs/en/advisor) sigue describiéndolo como experimental: herramienta
ejecutada en servidor Anthropic, disponible también para suscripciones compatibles, no solo facturación por API. Exige
modelos compatibles y acceso; un gateway puede no transportarla. Que el flag no aparezca en `--help` no prueba ausencia.

Claude decide cuándo consultarlo: **no hay ajuste para forzar ni limitar llamadas**. Cada consulta recibe el transcript
completo y lo procesa de nuevo sin caché propia. Los subagentes heredan advisor y aplican su comprobación de compatibilidad.
Una selección rechazada por API puede continuar sin advisor: configuración no equivale a invocación.

`/advisor` guarda `advisorModel`; `--advisor` actúa por sesión. Ninguno debe ejecutarse desde la instalación automática. Si
ya está autorizado/configurado, una consulta se acredita con la entrada nativa `Advising`, su modelo y resultado: reviewed,
declined o unavailable. No sumar automáticamente asesor portátil y advisor nativo para la misma decisión.

## 6. Arquitectura recomendada para r50

1. **Entrada breve.** Descripción frontal: GameMaker, GML, `.yyp`, crear/continuar un juego,
   corregir y verificar. El cuerpo identifica fase y fuente disponible; no enumera todo el
   corpus ni ejecuta automáticamente cada skill de método mencionada.
2. **Ruta de fase.** Nuevo juego → entorno/fuentes + desarrollo/evidencia + asesoramiento;
   cambio de requisito → contratos/aprendizaje; verificación/entrega → QA. API y assets se
   leen cuando esos sistemas entren en alcance. Una duda de firma no necesita un asesor.
3. **Asesor inicial.** Antes de comprometer arquitectura, recibe intención, restricciones,
   runtime/target confirmados, spec disponible o preguntas pendientes, decisiones reversibles
   y costosas, y fuentes mínimas. Puede identificar preguntas; no inventa respuestas del usuario.
4. **Decisión costosa.** Consultar por persistencia/esquema, multiplayer, plataforma, pipeline
   de assets o frontera arquitectónica con efecto de reescritura; no por cada archivo.
5. **Estancamiento.** Consultar cuando una hipótesis se ha repetido sin evidencia nueva o
   pruebas se contradicen. Pasar intentos y resultados; solicitar una hipótesis alternativa
   y una prueba que la distinga. Cambiar modelo no es el remedio automático.
6. **Contrato de salida.** Recomendación, alternativas pertinentes, riesgos, evidencia que
   falta, prueba decisiva y condiciones de revisión. Respuesta acotada; ampliar solo si
   falta un dato necesario para la decisión. El asesor no escribe recursos ni declara aceptación.
7. **Integrador.** Contrasta recomendaciones con spec, fuentes y pruebas, y registra qué
   adopta/rechaza y por qué. Un consejo no sustituye evidencia de GameMaker ni permiso externo.
8. **Sin cascada.** Un asesor activo por decisión; no delega ni se consulta a sí mismo.
   Permitir una aclaración sobre dato nuevo; cerrar esa consulta antes de otra. Reutilizar
   el recibo mientras no cambien sus entradas; no reutilizarlo tras invalidación pertinente.
9. **Degradación explícita.** Si no hay herramienta, permiso o cuota, seguir lo autorizado
   con autorrevisión identificada y prueba directa. Una decisión irreversible aún sin resolver
   permanece pendiente; no certificar independencia que no ocurrió ni intentar otro proveedor.
10. **Crítico final separado.** Contexto fresco, objetivo inmutable y controles válidos;
    no recibe el asesoramiento inicial ni justificaciones del constructor. Su evaluación
    independiente tampoco concede por sí sola aceptación del usuario. Reutilizar `13/29`.

Estos límites de frecuencia y tamaño son **política propuesta**, no capacidades garantizadas por los hosts. La calidad se
conserva dando evidencia pertinente y posibilidad de aclarar; el ahorro se mide después, sin recortar la prueba necesaria
para cumplir el requisito.

## 7. Instalación sencilla y garantías observables

Distribuir un paquete: `SKILL.md`, referencias existentes y la referencia nueva. La entrada debe funcionar con solo
instrucciones. Los adaptadores de agente nativo son opcionales; no exigir otro plugin, MCP, API de pago ni un modelo
distinto para instalar. Si se añaden definiciones nativas, ofrecer destino explícito y respaldo como el instalador actual.
Nunca modificar defaults, activar advisor, conceder confianza o instalar hooks por efecto secundario. Separar instalación de
archivos de una prueba LLM que consume cuota.

Una tabla de soporte debería registrar **copiado → descubierto → cargado → asesor invocado → consejo contrastado**, por
harness y versión. El quinto estado no convierte el consejo en correcto. `AGENTS.md` derivado es la ruta de lectura de hosts
sin skills, no un loader. Para distribución pública, enlazar este límite y el recibo nativo vigente; no anunciar «activación
garantizada» por haber validado YAML o encontrado una ruta en el catálogo.

Un [hook UserPromptSubmit](https://code.claude.com/docs/en/hooks) puede inyectar contexto, y
`InstructionsLoaded`/`SubagentStart` aportar observación. Inyectar una orden no fuerza su cumplimiento; un hook que bloquea
acciones debe tener contrato y pruebas propios. No se propone instalar uno: cambia configuración, portabilidad, latencia y
alcance de permisos.

## 8. Ensayo nativo pendiente y criterio de aceptación

Congelar paquete, hashes, prompts, casos y evaluación antes de correr. Crear fixture accesible sin juegos reales, con
manifiesto/README GameMaker y spec breve; mantener configuración y modelo actual autorizados. No copiar credenciales a
fixtures ni registros. Controles y variante deben compartir reglas externas; declarar las que ya ordenan activar skills,
porque confunden la atribución causal. No llamar «sin guía» a un control que la hereda.

| Caso | Disparador sin nombre de skill | Evidencia esperada |
|---|---|---|
| Positivo natural | «Quiero hacer un juego con GameMaker» | Carga real de entrada/ruta de desarrollo y asesor inicial antes de crear proyecto |
| Positivo cerrado | Spec GameMaker completa con una decisión costosa | Consulta acotada y contraste sobre esa decisión, sin rehacer el GDD |
| Estancamiento | Dos hipótesis fallidas con resultados conservados | Consulta con intentos, prueba diferenciadora y ausencia de cambio de modelo |
| Negativo de dominio | «Corrige las tildes de este párrafo» | No cargar GameMaker ni asesorarlo |
| Negativo de coste | Consulta puntual de una firma GML | Fuente de API; sin asesor innecesario |
| Sin delegación | Mismo caso con herramienta indisponible | Autorrevisión declarada; ninguna invocación inventada |

Comandos propuestos, **no ejecutados**. El primero se ejecuta dentro del fixture; las variables identifican rutas de recibos
y fixture accesibles y verificadas. Se conserva la configuración del CLI; su modelo efectivo puede diferir del seleccionado
en la app.

```sh
claude -p --verbose --output-format stream-json 'Quiero hacer un juego con GameMaker' > "$RECIBO_CLAUDE"
codex exec --json --cd "$FIXTURE" 'Quiero hacer un juego con GameMaker' > "$RECIBO_CODEX"
```

En Claude capturar `--output-format stream-json` y llamadas `Skill`/`Read`/`Agent`, sus resultados y el contexto hijo. En
Codex capturar `codex exec --json`, el rollout o evento nativo de spawn y sus resultados. Los JSONL resumidos pueden omitir
detalles: no inferir ausencia de spawn sin revisar la fuente de eventos efectiva de esa versión. La [salida JSONL
Codex](https://learn.chatgpt.com/docs/non-interactive-mode) acredita comandos/herramientas y uso informado por turno; el
texto final solo es salida del modelo.

Conservar ID real de sesión/turno, modelo efectivo, rutas leídas y SHA, tokens informados, duración, motivo de consulta,
brief, resultado y decisión del integrador. Un hash declarado por el agente debe cotejarse fuera de su respuesta. Un archivo
leído prueba acceso, no comprensión. El asesor debe dejar llamada y respuesta reales; «he consultado» no basta. Repetir en
contextos frescos y registrar fallos, omisiones y tiempos; no recalificar prompts tras ver resultados. Separar
descubrimiento, selección, asesoramiento y calidad del consejo. Un smoke positivo y negativo es mínimo de transporte; no
demuestra fiabilidad universal.

## 9. Procedencia y huellas

Código consultado de `openai/codex`: tag `rust-v0.162.1`, objeto anotado `7a078f6bb4ce0dc2a81408b334ce52979d92c603`, commit
`092d3acd6bec3e3a14bdc7e7a2810ab628ab759d`, resuelto por API pública de GitHub. [Licencia
Apache-2.0](https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/LICENSE). No se adopta ni copia
código externo; se describen interfaces y se enlaza su fuente.

| Archivo/representación realmente leído | SHA-256 |
|---|---|
| r49 `SKILL.md` | `bb3abb386385259e918d0c4768025f8bbe8ea57d677cf6edddc44b1cefc3ebf5` |
| r49 desarrollo/evidencia | `f0816f0ff7d7e8ffbb4e45a3409cb21a15bdea81bb835fe9304033ea51afe1d8` |
| r49 contratos/aprendizaje | `dd085b6404ecfb2d840896af46caac2463711b4b136851082b60d92a1ae73765` |
| Código fijado `skills/src/model.rs` | `26facbe9c82b30dd10bebede46fd6795cb04b713659e45651dad83e6aa07ff10` |
| Código fijado `ext/skills/src/loader/metadata.rs` | `0b203b4696b17ccf695bbcf8eb3a4e471e9c8b47477081126a06f98f35f600eb` |
| [Build skills, Markdown oficial](https://learn.chatgpt.com/docs/build-skills.md) | `ed6e324f747d47adf6f60ee1fca13ba469b3671f55f58c3a78f35947af6919d5` |
| [Subagents Codex, Markdown oficial](https://learn.chatgpt.com/docs/agent-configuration/subagents.md) | `e7469d41c5a18a4ee66ee40ca4a9a2617a697e42554a0198ac4481e1e597357f` |

Las páginas Claude son documentación viva consultada por navegador; su descarga Markdown devolvió HTTP 403, por lo que no se
atribuyen hashes ni commits que no se obtuvieron. Los hashes locales fijan el punto r49 de lectura, aunque el integrador
cambie después r50.
