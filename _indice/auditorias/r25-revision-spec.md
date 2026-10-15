# r25 · Revisión de especificación de r50

15-10-2026. Revisión fresca del candidato de la raíz sobre el alcance r25 y la base pública
`519b5be795a86337da309f51a1f5696241edef74`; el WIP histórico de la raíz no se considera alcance.

## Hallazgos

1. **[P2] Una instalación enlazada no puede actualizarse mediante el bootstrap.**
   R5 exige «Actualizar sin perder trabajo ni configuración» (`r25-plan-y-criterios.md:14`);
   `INSTALACION.md:151–164` ofrece repetir el bootstrap y admite `--enlace`.
   `instalar-remoto.py:103–106` valida desde una biblioteca temporal antes de promoverla.
   En una instalación previa con `--enlace --harness codex`, el enlace apunta al paquete
   de la biblioteca estable, distinto del origen temporal. `instalar.py:125–131` lo rechaza
   como referente fuera del plan cuando cambia la revisión. Fixture con dos paquetes
   válidos: primera instalación exit 0; actualización exit 1; sigue presente la versión
   anterior. Reconocer de forma acotada los enlaces a la biblioteca que el propio bootstrap
   va a actualizar permitiría conservarlos sin autorizar referentes ajenos.

2. **[P2] Dos destinos anidados producen una copia instalada inválida con salida 0.**
   R4 exige «copias verificadas» (`r25-plan-y-criterios.md:13`); la investigación exige
   «Rechazar […] solapamientos recursivos» (`r25-investigacion-instalacion.md:97–101`).
   `instalar.py:108–132` compara cada destino con el origen, pero no los destinos entre sí.
   Ejemplo alcanzable: `CLAUDE_CONFIG_DIR=<home>/datos` y
   `OPENCODE_CONFIG_DIR=<home>/datos/skills/gamemaker-biblioteca/nested`, instalación general.
   Fixture: exit 0; OpenCode se instala dentro de Claude; `validar_paquete()` sobre Claude
   falla por archivos adicionales. La planificación debe rechazar el solapamiento antes
   de crear o mover nada.

## Cobertura y límites

Pruebas ejecutadas con Python aislado y biblioteca estándar: instalación **27/27**,
bootstrap **9/9**, más ambos casos anteriores. Se revisaron skill/referencias, instaladores,
guías, workflow y ensayo de distribución. No se ejecutaron LLM, juegos, descargas ni cambios
de configuración global. No apareció comportamiento extra no autorizado en este alcance.

R1/R2 requieren trazas nativas: ensayos textuales o catálogo no certifican activación ni
asesoría real. Publicación, matriz nativa y sus recibos siguen en curso y no se convierten
en hallazgos por estar pendientes. El asesor portátil conserva modelos y permisos; no
presupone habilitar globalmente el advisor experimental de Claude.

## Revalidación de las correcciones

15-10-2026: ambos hallazgos originales corregidos. Repetición independiente: actualización
con `SKILL.md` distinto, exit 0/0, enlace conservado y contenido nuevo; solapamiento, exit 1
sin crear destinos. Suites: instalación **32/32**; bootstrap **11/11**, incluido rollback del plan.

Límite derivado: `instalar-remoto.py:105–109` con `--comprobar` verifica únicamente paquete,
no plan. El mismo solapamiento da exit 0 sin escrituras; la instalación efectiva sí lo rechaza.
