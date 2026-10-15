# r25 · Instalación portable y descubrimiento de la skill

Fecha de consulta y ensayos: **15-10-2026**. Auditoría sobre HEAD
`19d53b645373c4950a4ba0d267657d2c147dee0b`, con WIP r49 presente. Solo se escribe
este informe; las instalaciones reales, configuraciones, modelos y juegos pausados
permanecen fuera de las mutaciones. Los ensayos usan directorios temporales propios.

## 1 · Decisión recomendada

Convertir `instalar.sh` en envoltorio fino de **un `instalar.py` con biblioteca estándar**,
y ofrecer la misma entrada desde PowerShell, sin Bash obligatorio. Reutilizar
`_indice/harnesses.py`, no crear otro catálogo ni depender de otro gestor de skills.
La operación local debe ser una orden después de disponer del checkout y Python 3.10+:
`python instalar.py`, `--harness nombre` o `--destino carpeta`. Son interfaces propuestas,
no comandos que ya existan. En Windows se admite `py -3 instalar.py`.

La validación estricta YAML sigue en mantenimiento con PyYAML. El sincronizador genera
un manifiesto SHA-256 del paquete publicable; el consumidor comprueba bytes, versión,
lista exacta, rutas relativas y referencias usando solo Python. No sustituir YAML por
un parser parcial ni instalar dependencias globales. Pillow es para comprobaciones de
imágenes, no una dependencia necesaria para copiar instrucciones verificadas.

## 2 · Huecos del instalador actual

| Prioridad | Evidencia actual | Requisito verificable |
|---|---|---|
| Bloqueante | `instalar.sh:1,43–59`: exige Bash, Python y sincronizador con PyYAML; la guía necesita seis órdenes | Entrada Python nativa y paquete generado con manifiesto; venv/PyYAML/Pillow quedan en mantenimiento |
| Bloqueante | `harnesses.py:58` elige solo `$CODEX_HOME/skills` para `--harness codex`; `.agents` se instala únicamente en modo general | Elegir la ruta canónica `.agents/skills` documentada por OpenAI; compatibilidad heredada explícita, sin asumir que la ruta antigua basta |
| Bloqueante | `instalar.sh:117–130`: selección individual no registra biblioteca; exige export manual | Registro local del instalador accesible desde la copia o destino elegido, sin tocar perfiles de shell ni configuración del harness |
| Alta | Detección solo por nombres en PATH; `agent` puede ser cualquier programa; apps/extensiones sin CLI no aparecen | Mostrar plan y motivo de detección; usar señales de directorios existentes y selección explícita; tratar detección como indicio |
| Alta | Claude siempre `~/.claude`; OpenCode siempre `~/.config/opencode` | Contrastar overrides de sus raíces y declarar los no resueltos; nunca adivinar ni editar proveedores para que descubran la skill |
| Alta | Reinstalar sobre enlace a copia compartida mueve el enlace al backup y lo reemplaza por otra copia | Preservar topología y actualizar una única copia representativa cuando su destino esté dentro del plan autorizado |
| Alta | Se conserva backup por destino y se restaura si falla `mv`; no hay rollback del conjunto ni comando de restauración | Recibo por destino con backup/huellas, error y estado parcial claro; restauración explícita y limitada a archivos propios |
| Media | `--comprobar` ejecuta sincronizador que regenera dos derivados antes de salir | Comprobación real sin escrituras; generación separada de instalación |
| Media | Reinstalaciones idénticas crean backups nuevos; fallo de promoción deja temporal | Comparación previa, no-op idéntico, limpieza en `finally`; conservar backup y diagnóstico si la restauración falla |
| Media | Actualización documentada como `git pull --ff-only`; no existe bootstrap fijado | No descargar/ejecutar `main` móvil; instalar revisión o release concreta y comprobar integridad antes de promover |

El override de OpenCode requiere comprobar su raíz efectiva: sus docs admiten
`OPENCODE_CONFIG_DIR` y fuentes adicionales; la tabla de skills describe el default.
El resolver actual no consulta ese override ni `XDG_CONFIG_HOME`. Este último exige
contraste con la versión instalada, no una regla inferida de las convenciones XDG.
[Configuración OpenCode](https://opencode.ai/docs/config/),
[ubicaciones de skills](https://opencode.ai/docs/skills/).
Claude documenta `CLAUDE_CONFIG_DIR` para trasladar sus archivos de usuario; el
instalador actual lo ignora. La correspondencia exacta con skills debe acreditarse
con el loader de la versión objetivo, además de la documentación.
[Configuración Claude](https://code.claude.com/docs/en/settings).

## 3 · Qué significa «todos»

«Todos» debe significar los **15 harnesses identificados por el catálogo** y el destino
compartido `agents`, con límites por versión y plataforma. No significa cualquier agente
existente, agentes remotos, cloud o sesiones de otras máquinas. Esta matriz describe
rutas candidatas; una copia correcta no prueba descubrimiento ni selección automática.

| Selector | Destino de usuario actual o recomendado | Límite de descubrimiento |
|---|---|---|
| `agents` | `~/.agents/skills` | Ruta compartida, sin promesa universal |
| `claude` | `~/.claude/skills`, contrastar override | Skills personales locales; permisos, visibilidad y contexto pueden impedir activación |
| `codex` | **`~/.agents/skills` canónica** | Conservar legacy solo cuando proceda; nombres duplicados pueden aparecer en selectores |
| `opencode` | `~/.config/opencode/skills`, raíz personalizada por verificar | También descubre `.claude` y `.agents`; permisos pueden ocultar o impedir carga |
| `qwen` | `~/.qwen/skills` | Manda `skills.directories`; copia allí no demuestra que se lea |
| `kimi` | `~/.kimi-code/skills` | Preservar alias existentes y validar YAML estricto |
| `gemini` | `~/.gemini/skills` o `.agents` | Alias `.agents` prevalece en el mismo nivel; puede estar deshabilitada |
| `copilot` | `~/.copilot/skills` o `.agents` | Recarga y `/skills info`; no confundir CLI con otras superficies Copilot |
| `cursor` | `~/.cursor/skills` o `.agents` | Skills locales no llegan automáticamente a Cloud Agents/SSH/workers |
| `cline` | `~/.cline/skills` | Presencia de extensión no implica comando `cline` en PATH |
| `pi` | `~/.pi/agent/skills` / `PI_CODING_AGENT_DIR` | Alias `.agents`; confianza y configuración de proyecto importan |
| `omp` | `~/.omp/agent/skills` / perfil y override comprobados | Providers, exclusiones y herramienta lectora condicionan catálogo |
| `minimax` | `~/.minimax/skills` / `MINIMAX_DATA_DIR` | Puede desactivar fuentes; perfiles o flags requieren destino explícito |
| `dsh` | `~/.dsh/skills` / `DSH_HOME` | Requiere provider filesystem y consumidor activos |
| `hermes` | `~/.hermes/skills`; Windows LOCALAPPDATA | Respeta home/sufijo; confianza en skills de proyecto |
| `gentle-shell` | `~/.gentle-shell/agent/skills` / override | Resolver efectivo depende de la selección de home del wrapper |

Fuentes primarias reconsultadas: [Claude Skills](https://code.claude.com/docs/en/skills),
[OpenAI Skills](https://learn.chatgpt.com/docs/build-skills),
[OpenCode Skills](https://opencode.ai/docs/skills/),
[Gemini Skills](https://geminicli.com/docs/cli/skills/),
[Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills),
[Cursor Skills](https://cursor.com/docs/skills).
Las restantes filas conservan los límites documentados y probados en r22/r23;
esta consulta no vuelve a certificar sus versiones actuales.

Pi: [docs fijadas a `abe508e1b89912adde45528136c3221eb69acdd7`](https://github.com/earendil-works/pi/blob/abe508e1b89912adde45528136c3221eb69acdd7/packages/coding-agent/docs/skills.md),
tag 1.1.0, commit 07-10-2026. OMP:
[docs fijadas a `d49c7b570ef25673b55e05d9bcf8dea5eea6ee05`](https://github.com/can1357/oh-my-pi/blob/d49c7b570ef25673b55e05d9bcf8dea5eea6ee05/docs/skills.md),
commit del archivo 10-10-2026. Las páginas web anteriores son móviles, consultadas en la
fecha de cabecera. [Agent Skills](https://agentskills.io/specification) define estructura,
metadatos y referencias; no impone rutas del host ni garantiza autoactivación.

Para otros agentes, conservar el fallback `AGENTS.md` generado y sus referencias,
integrándolo sin sobrescribir reglas existentes. Debe ser una adaptación elegida por
el consumidor, no una escritura silenciosa de instrucciones en todos sus proyectos.

## 4 · Contratos concretos del reemplazo

1. **Plan antes de mutar:** resolver destinos, aliases y origen real; deduplicar por
   identidad de ruta. Rechazar destino dentro del paquete y solapamientos recursivos.
   Identificar alias OpenCode/Qwen/Kimi a la copia de Claude, instalar esa copia una vez
   y conservar los enlaces. Un enlace colgante, bucle o destino fuera del plan no concede
   permiso para modificar otro árbol: diagnosticarlo y permitir selección explícita.
2. **Promoción por destino:** preparar dentro de su mismo volumen, cotejar lista exacta
   y SHA-256, conservar anterior y promover. Si falla, restaurar anterior; si también
   falla restaurar, mantener backup/temporal y describir las rutas recuperables.
   No borrar backups automáticamente ni esconder una instalación parcial entre destinos.
3. **Sin configuración ajena:** escribir solo paquete, recibo/registro propio y backups.
   La ruta privada de biblioteca no debe formar parte del manifiesto público ni filtrarse
   a Git. Registrar cómo se localiza desde una copia y desde un enlace; verificar traslado
   de la biblioteca, selección individual y dos bibliotecas distintas sin colisiones mudas.
4. **Dependencias y alcance:** GameMaker, runtime, corpus, Git, LLM y embeddings no son
   requisitos para instalar instrucciones desde un checkout. Índices opcionales fallan
   antes de reemplazar instalaciones y conservan selección explícita de runtime.
5. **Actualización reproducible:** bootstrap pequeño fijado a commit y digest, descarga
   temporal, extracción sin escapes ni enlaces fuera de destino y cotejo antes de ejecutar.
   Diferenciar integridad de autenticidad: un digest servido junto al contenido no añade
   confianza independiente. Mantener modo local/offline; sin autoactualizador residente.
6. **Privacidad/corpus:** el bootstrap obtiene solo distribución pública; manual y código
   de terceros siguen opt-in con licencia/espacio. No empaquetar conversaciones, rutas
   personales, runtime ni los recibos locales de instalación. No migrar modelos o claves.

## 5 · Ensayos frescos y huellas

Host: macOS **27.0.1 arm64**, Python de ensayo **3.12.14**, PyYAML **6.0.3**, Pillow
**12.2.0**. `python3` por defecto es **3.14.7**; no se sustituyó ningún intérprete.
Se ejecutaron **19/19** pruebas de instalador y **16/16** de sincronización: exit 0.
Sus fixtures sustituyen el sincronizador del instalador; las 19 pruebas no prueban por
sí solas el flujo completo sin dependencias ni la instalación nativa en otros sistemas.

Probe adicional `--harness codex`: exit 0, archivo legacy presente, ruta canónica
`.agents` ausente y registro de biblioteca ausente. Inyección de fallo de promoción
`mv`: exit 1, contenido anterior restaurado, **un temporal `.gm-skill.*` restante**.
No se ejecutó el instalador contra los homes reales.

Se repitió el programa publicado de loaders r22 sobre la skill r49 de **13 archivos**:
**OMP instalado 18.10.4**, Bun **1.4.3**, **79 aserciones correctas**, exit 0,
fetch bloqueado y cero conversaciones/modelos. Cubre providers nativo/agents, aliases,
metadatos y copia exacta; no selección automática de un modelo. r23 acredita r48/12
archivos y OMP 18.8.7/Pi 1.1.0: es evidencia histórica para lo no repetido.

| Entrada inspeccionada o ejecutada | SHA-256 |
|---|---|
| `instalar.sh` | `0b8cb8a8783fd957a7743f7b70be84e2fe95f88240e6d295a24933883b2dcf96` |
| `_indice/harnesses.py` | `60c23928e09e876a08b456dcefab87a997a2a993edcb81edac5ff60e47e5e80e` |
| `_indice/sincronizar-skill.py` | `640a8e7bf55ecc94aaf71854c5587f5b292d3fb29e9a7dfe318a4613245f13fb` |
| Skill r49 `SKILL.md` | `bb3abb386385259e918d0c4768025f8bbe8ea57d677cf6edddc44b1cefc3ebf5` |
| OMP `src/discovery/helpers.ts` | `3176e3569cb5878f1ff3e5f928b9179821a5b302de2d1bb2525cf382792d8acb` |
| OMP utils `src/dirs.ts` | `a9f431bf757eb5a90e5dcbc3c2d91f1633192facdb3b174cdf5057cbd7bc8047` |

Linux/Windows: sin ensayo nativo ni PowerShell disponible en este host. Modelar rutas
con `PureWindowsPath`, mocks o CI acredita esas pruebas, no ejecución en hardware ajeno.
Antes de anunciar soporte probado, ejecutar instalación/segunda instalación, Unicode y
espacios, HOME/USERPROFILE, ausencia de Bash/dependencias/motor, permisos, copia/enlace,
fallos y restauración en runners Windows/Linux. Publicar matriz de resultados separada
de descubrimiento mediante loaders y de autoactivación observada con un agente.
