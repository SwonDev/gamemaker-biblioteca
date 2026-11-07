# r26 · Integración de aprendizajes de Relicwild en biblioteca y skill

Fecha: **07-11-2026**. La autorización de publicación se registra en el registro privado; este informe público contiene solo hechos técnicos.
hacer command code con deepseek para que tú no gastes tokens, hay que integrarlo todo en la
biblioteca, en la skill y actualizar el repositorio con todo lo nuevo, etc.».
Ámbito: biblioteca `GameMaker_Aprendizaje` y skill `gamemaker-biblioteca`. El proyecto
`Relicwild_World` se usó como fuente de solo lectura; no se modificó, no se ejecutó su juego y
no se copiaron sus datos privados.

## 1 · Fuentes reutilizadas

- Informe final 1/3 (método, cronología y límites), 2/3 sustitutivo (rendimiento, mundo,
  voxel/animación) y 3/3 (audio, Idol, aportaciones y destinos).
- Anexos de prioridades, research-first y fuentes; correcciones de punto 8 y continuidad.
- Bloques técnicos 1–5: optimización, mallado/LOD/culling, mundo/hidrología/determinismo,
  voxel/anatomía/animación y portabilidad GML.
- Antecedentes ya incorporados: `r24-aprendizajes-relicwild.md`, la skill r50 y
  `r25-ensayos.md`. No se duplican; se enlazan cuando el caso solo confirma una regla existente.

## 2 · Qué se integró

| Documento | Contenido incorporado |
|---|---|
| `13/31 - Investigación previa y reutilización...` | Ficha nueva: cuándo se abre, contrato de ocho puntos, candidato, licencia/compatibilidad/coste, prueba discriminante, decisión/riesgos y registro |
| `13/29 §2.3` | Puerta de investigación antes de una decisión costosa; no reabrir motor fijado; no convertir solo lectura en prohibición universal |
| `13/29 §5.1` | Crítica de cierre frente a crítica ciega; evidencia propia del crítico; independencia débil por cuota |
| `13/29 §6.1` | Corrida rota, paquete exportado, omisión `NO_EVALUADO` y modos que deben diferir |
| `13/29 §7.1` | Propiedad y persistencia de procesos por herramienta/sesión; cierre solo en entorno aislado |
| `13/29 §8.1` | Manifiesto de integración: creados, modificados, borrados, enlaces y prueba del consumidor |
| `13/30 §6.1` | Regla + guardarraíl; norma que cita una prueba inexistente; tecnología descartada se marca sustituida |
| `13/30 §8.1` | Candidatos y reutilización; licencia de código/pesos/assets; wrapper que no relicencia |
| `13/10 §6.3.1` | Crédito/deuda con coste real, unidad indivisible, cupo que pierde cobertura, p99,9/1 % low |
| `13/10 §8.6 quinquies` | Corrida rota roja, paquete exportado, autofallo de ventana y omisión |
| `04/29 §9 bis` | Qué transfiere un motor de vóxeles a GML; límites de hilos, instancing, índices, greedy, LOD, oclusores y VAT |
| `01/15 §6` | Presupuesto por unidad, A/A, p99,9/1 % low, medida en exportado/YYC |
| `13/07 §2 bis` | Cauce por columna con puerta precalculada; no sustituye priority-flood en mundo infinito |
| `13/07 §10 bis` | Detectores geométricos con rojo provocado, denominador y defectos restantes; vocación medida |
| `13/07 §14` | Límite del ejemplo retomable: inicialización/copia/finalización fuera del presupuesto |
| `13/04 §8 bis` | Rig de piezas rígidas, andares fisiológicos, fase ligada al desplazamiento y QA |
| `13/09 §6 bis` | YuE2 local, ABC/cot, capas derivadas, derechos código/pesos/salidas, Suno e Idol |
| `13/09 §8 quinquies` | Router de skills de audio y límites reales |
| `05/02 §2 bis` | Licencias transitivas, contenido generado, YuE2/Suno/Idol y enlaces fijados |
| Skill r51 | Referencia `research-first.md`; routing en `SKILL.md`; actualizaciones en `desarrollo-y-evidencia`, `qa-y-entrega`, `contratos-y-aprendizaje`, `contexto-y-recursos` y `assets-y-texto` |
| `AGENTS.md`, `README.md`, `13/_INDICE-DISENO.md` | Routing visible de la nueva ficha y de la puerta de investigación |

## 3 · Límites y contraejemplos conservados

- Las cifras de rendimiento del proyecto de origen son **históricas** de otros carriles; no se
  reejecutaron aquí. El objetivo global sigue sin cumplirse y las cifras concretas pertenecen a
  su informe, no a esta biblioteca.
- No se declara «cero defectos global»: quedan casos de z-fighting y empotrados en el proyecto
  de origen, y esta integración no los arregla.
- La animación por instancia de multitudes (VAT) sigue **pendiente** en el proyecto; la
  microfauna existente es una referencia, no una prueba de multitud.
- El índice GML consultado no muestra familias de hilos, instancing, índice de índices o
  frustum; eso describe ese índice, no una imposibilidad universal. Una extensión nativa o otra
  versión pueden ofrecer otra cosa.
- El origen flotante del caso Godot no se presenta como necesidad de GameMaker: los reales de
  GML son de doble precisión y lo transferible es la regla de marcos, no la técnica.
- YuE2: la licencia permite creadores individuales y puede exigir licencia aparte a empresas;
  no se convierte en prohibición ni en permiso universal. La escucha histórica «nadie la ha
  escuchado» no se presenta como estado actual; la comprobación local se registra en el tracker privado.
- Idol queda como identidad pendiente: Speridlabs es imagen a 3D Gaussian splat, el fork MPS no
  acredita una instalación concreta y `yiyuzhuang/IDOL` es SMPL-X humano.
- No se modificó el juego de origen ni se aplicó integración en él. Durante la investigación no
  hubo commits ni push; la publicación autorizada del 07-11-2026 se registra en §6. Sin
  instalación ni cambio de modelos.

## 4 · Verificación final (07-11-2026)

Comando exacto: `cd $HOME/Documents/GameMaker_Aprendizaje &&
/opt/homebrew/bin/python3.12 _indice/actualizar.py`. Resultado: **exit 0**, «Biblioteca coherente.
Índices al día y sin deuda pendiente». Se usa python3.12 porque el `python3` por defecto (3.14) no
tiene PyYAML y no puede validar el frontmatter de la skill.

| Fecha | Pasada | Rutas | Citas | Resultado |
|---|---|---:|---:|---|
| 07-11 | Local con manual, primera (L6) | 2345 | 2321 | exit 0; histórica |
| 07-11 | Local con manual, tras revisiones (L9) | 2349 | 2322 | exit 0; histórica |
| 07-11 | Local con manual, final H1–H3 | 2349 | 2324 | exit 0; histórica |
| 07-11 | **Clon limpio sin manual (rama publicada)** | **2110** | **2324** | **exit 0; vigente** |

La fila vigente es la última. El manual oficial no se publica en GitHub y se reconstruye aparte;
por eso el clon limpio tiene menos rutas y documentos que la pasada local con manual. Las filas
locales se conservan fechadas como historia y no se presentan como el estado de la rama.
Comprobaciones de la pasada vigente:

- Enlaces: 2110 rutas correctas, 0 rotas; 1640 anclas correctas, 0 rotas; 288 documentos sin
  números de sección repetidos; 2324 citas por número resueltas.
- Ortografía: sin palabras españolas sin tilde.
- GML: 0 funciones del runtime inventadas; 3477 bloques compilables compilan sin errores de
  sintaxis. No se añadió GML nuevo ni se ejecutó un juego.
- Descubrimiento: **las 80 tareas se resuelven**. No se acepta el timeout de 30 s del revisor como
  verde por sí solo; esta pasada completa es la que acredita las 80.
- Skill: `references/indice-documentos.md` regenerado con 279 documentos; `AGENTS.md` regenerado
  desde `SKILL.md`; manifiesto de 15 archivos; todas las rutas citadas existen.
- SkillSpector `--no-llm`: 16/16 componentes, `complete_with_caveats`, score **18 (LOW)**,
  recomendación **SAFE**, 1 hallazgo HIGH `TM2` en `references/asesor-y-activacion.md:137`. La
  evidencia es la frase en prosa «y conserva fallos/omisiones»; revisión semántica: no hay
  llamadas a herramientas, encadenamiento, red, credenciales ni ejecución. **Falso positivo**, no
  se modifica el texto para silenciar el escáner.
- Copias instaladas en otros harnesses siguen en r50 y el repositorio va por r51: **H4, fuera del
  alcance de esta integración**. No se instalaron ni actualizaron; el aviso es esperado.
- El merge en `main` (`SHA retirado`) conserva exactamente el árbol de la rama; la pasada del clon
  limpio sigue siendo la evidencia vigente del contenido publicado.

### Smoke consolidado (H2)

Un solo relato, sin duplicar sesiones:

- **Sesión propia:** `b919c04b-3d6f-42b5-b3f7-8544c090a655`, Command Code con
  `deepseek/deepseek-v4.1-flash`, modo plan, `--no-session`, `--skill` apuntando a la ruta
  absoluta de la skill r51. Leyó `SKILL.md`, `research-first.md`, `13/31`, `13/10 §6.3.1`,
  `01/15 §6`, `13/04 §8 bis`, `13/09 §6 bis`, `05/02 §2 bis` y `consulta-api.md`; no escribió
  archivos ni ejecutó el juego. Para `keyboard_check_pressed` distinguió el índice del runtime del
  proyecto y no afirmó una firma no verificada.
- **Revisor `ctx_303c4113ec85`:** casos A/B/C con `--no-skills --skill <ruta absoluta r51>`.
  Demuestra el paquete actual sin la copia r50, **no** activación automática instalada. No lo
  reejecuté; se cita su veredicto.
- **Límite:** las copias instaladas siguen en r50 y no se actualizan. No se afirma activación
  automática instalada ni se confunde con el paquete r51.

### Revisiones y cierre

- Revisión independiente 1 (7 hallazgos): instancing no universal, frustum/`sphere_is_visible`,
  duplicación 13/29 ↔ 13/10, atribución del caso, lista de disparadores, duplicación de derechos y
  «el caso» sin nombrar. Corregidos.
- Revisión independiente 2 (5 hallazgos): pipeline de ríos, priority-flood/mundo infinito,
  umbrales universales, guardarraíl de juicio y taxonomía de vocaciones. Corregidos.
- Revisor final `ctx_303c4113ec85`: **APTO S1–S6, sin bloqueantes**; H1 contadores fechados,
  H2 smoke consolidado, H3 recuento manual de MAPA eliminado y derivados regenerados, H4 copias
  r50 fuera del repo. No se reabre contenido técnico aprobado.

## 5 · Fuentes públicas fijadas

- YuE2: `MODEL_LICENSE` revisión `1647252d68b7`; licencias de pesos `YuE2-3B` y `YuE2-Vae`.
- Suno: artículos `9601665`, `13876865` y `2425729`.
- Idol: Speridlabs research/idol-sdk, fork MPS `DeanBeanBEER-WARE/idol`, `yiyuzhuang/IDOL`.
- Enlaces completos y fecha en `05/02 §2 bis` y `13/09 §6 bis`.

No se inventaron URLs; las que aparecen son las del anexo contrastado.

## 6 · Publicación

Rama de feature: `docs/relicwild-r51`, creada desde `origin/main` (`SHA retirado`) para no arrastrar
WIP ajeno. Push no forzado al remoto `SwonDev/gamemaker-biblioteca`. Integrada en `main` con
el PR de la rama (`el PR de la rama`), merge commit `SHA retirado`, sin
squash y sin borrar la rama. En el merge `SHA retirado`, el árbol de `main` coincidía con la rama
`SHA retirado`; los commits documentales posteriores (`SHA retirado` y el que contiene esta corrección)
solo cambian este informe, así que el `main` actual ya no es idéntico a la rama.

| Orden | Commit | Unidad |
|---|---|---|
| 1 | `SHA retirado` | método/research-first |
| 2 | `SHA retirado` | técnica: presupuestos, 3D, procgen y animación |
| 3 | `SHA retirado` | audio: YuE2, Suno, Idol y licencias |
| 4 | `SHA retirado` | auditoría r26 |
| 5 | `SHA retirado` | índices y paquete de skill |
| 6 | `SHA retirado` | publicación de la rama |
| 7 | `SHA retirado` | merge de el PR de la rama en `main` |

El push inicial de la rama no activó workflows. El el PR de la rama activó `Instalación portable` en el run
`run retirado` (`event=pull_request`, head `SHA retirado`, `success`); sus seis jobs pasaron. El push
de `main` sobre `SHA retirado` activó el run `run retirado` (`event=push`, `head_branch=main`,
`success`). No se cita `run retirado` como run del PR. Los commits documentales sobre
`_indice/auditorias/**` no disparan CI por el filtro de rutas: N/A. Este párrafo se publica en el
commit documental que contiene esta sección; su SHA se informa en el mensaje final.

**RDD:** el ciclo nativo no está disponible para Command Code (solo Claude Code, Codex, OpenCode
y Pi). No se invocó otro modelo ni se inventó un recibo; se reutilizan las dos revisiones
independientes DeepSeek ya registradas. La aprobación previa del revisor no se reescribe.
