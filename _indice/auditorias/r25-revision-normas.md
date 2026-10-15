# r25 · Revisión de normas de r50

15-10-2026. Revisión independiente de los diez archivos de instalación indicados,
comparados con el checkout público limpio `519b5be795a86337da309f51a1f5696241edef74`.
Reglas: `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md` y contratos de
`r25-investigacion-instalacion.md`. El WIP ajeno queda fuera.

## Hallazgos

- **P2 — Colisión silenciosa entre bibliotecas.** `instalar.py:189–200` reemplaza el
  único registro global aunque apunte a otra biblioteca. Probe: instalar A para Claude
  y B para Codex devuelve 0/0; Claude conserva su paquete de A, pero su resolución de
  `BIB` pasa a B, sin aviso ni copia del registro anterior. Viola el contrato §4.3
  (`r25-investigacion-instalacion.md:108–109`): dos bibliotecas sin colisiones mudas.
  Detectar el cambio de raíz antes de instalar y exigir una elección explícita, o
  mantener una asociación propia por instalación.
- **P3 — Diagnóstico incorrecto con raíces personalizadas.**
  `_indice/sincronizar-skill.py:323,334,348–355` conserva las rutas fijas de Claude y
  OpenCode aunque `_indice/harnesses.py:63–65` ya resuelva sus overrides. En fixture
  con `CLAUDE_CONFIG_DIR` y copia exacta instalada, informa «✗ Claude Code: falta» en
  la ruta predeterminada. Incumple la regla de reutilizar lo existente y el contrato
  de resolver la raíz efectiva (§2). Derivar también esas entradas de `destinos()`.

## Corregido durante la revisión

**P2 — Destinos recursivos:** el plan inicial permitía instalar Claude dentro del paquete
de `agents`, devolvía 0 y dejaba inválido su manifiesto. El integrador añadió el rechazo
en `instalar.py:121–125`; el probe fresco devuelve 1 antes de crear el home. Cumple ahora
el contrato §4.1.

## Juicios Fowler

Posible **código duplicado**: el catálogo manual de `estado_enlaces()` duplica información
de `harnesses.destinos()`; su divergencia causa el P3 anterior. No se cuenta dos veces.
No señalo otros olores sin consecuencia concreta.

## Evidencia y límites

Python 3.14.7/macOS: instalación **27/27**, bootstrap con transporte simulado **9/9**;
probes propios aislados de solapamiento, dos bibliotecas y override. Sin instalación
real de usuario, juegos, red, credenciales ni modelos. No acredita Windows, Linux,
PowerShell, descarga remota ni selección mediante LLM.

Recuento al corte: **2 abiertos** (1 P2, 1 P3), **1 P2 corregido**, ningún P1.

## Estado de cierre

Revalidación: instalación **32/32**; sincronización **19/19** (Python 3.12.14/PyYAML 6.0.3).
Copias, backup/aviso global, solapamientos y overrides: correctos.

La primera revalidación detectó **un P2 derivado**:
`_indice/skills/gamemaker-biblioteca/references/entorno-y-fuentes.md:38` leía `SKILL_DIR/../`,
atravesando el symlink antes de `..`. Probe A→Claude, B→Qwen(alias): sidecar lógico B,
comando leía A.

Cierre definitivo: Bash usa `dirname`; probe distribuido **3/3** (copia, override, alias),
ejecutado en macOS. **Cero hallazgos abiertos**; PowerShell nativo no ejecutado aquí.
