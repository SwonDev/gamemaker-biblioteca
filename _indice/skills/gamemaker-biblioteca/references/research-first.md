# Investigación previa y reutilización

También llamada **research-first**.

Lee esta referencia antes de comprometer motor, arquitectura, formato, librería, técnica o un
asset caro de revertir. No sustituye la especificación ni el ciclo de desarrollo: decide **qué**
alternativa se va a construir y con qué evidencia.

## Cuándo se abre

| Situación | Acción |
|---|---|
| Motor, plataforma o pipeline ya fijados | No reabrir; documentar el límite y construir dentro de él |
| Elección cara de revertir (motor, guardado, multijugador, formato, librería) | Abrir ficha de investigación |
| Existe una librería o técnica reutilizable | Comparar antes de escribir |
| Corrección pequeña con reproducción y causa | No abrir ficha; usar el ciclo de `desarrollo-y-evidencia` |

## Contrato de ocho puntos

1. **Incertidumbre y decisión**: qué no sabemos, qué desbloquea y qué cambiaría según la respuesta.
2. **Criterios**: qué evidencia permite elegir y qué resultado obliga a descartar.
3. **Candidatos**: repos, motores, técnicas, optimizaciones, referencias y assets; URL, commit/versión,
   licencia de código y de pesos/assets, compatibilidad, coste, mantenimiento y qué se reutiliza.
4. **Motores alternativos**: solo si no hay elección fijada; experimento mínimo, sin migrar por moda;
   conservar motor, WIP, modelos y permisos.
5. **Prueba discriminante**: caso mínimo que separa opciones; resultado esperado antes de ejecutar;
   instrumento y control que deba fallar.
6. **Resultado y descarte**: qué se probó, qué se rechazó y por qué; conservar el intento negativo.
7. **Cierre**: recomendación, alternativa, dato pendiente, condición de revisión y evidencia que
   invalidaría la elección.
8. **Límites**: solo lectura mientras el encargo lo sea; un experimento futuro exige autorización
   explícita y entorno aislado, sin alterar WIP, permisos, modelos ni recursos compartidos.

## Ficha de candidato

| Campo | Contenido |
|---|---|
| Candidato | Nombre, URL, commit/versión fijada |
| Capacidad | Qué resuelve, no la categoría |
| Licencia | Código, pesos, assets y avisos transitivos, por separado |
| Compatibilidad | Runtime, target, plataforma, versión y dependencias |
| Coste | Adaptación, mantenimiento, memoria, rendimiento y licencia |
| Reutilización | Código, idea o asset; qué se copia y qué se reescribe |
| Evidencia | Documentación leída, prueba ejecutada o informe consultado |
| Riesgo | Qué puede invalidar la elección y qué falta verificar |

**Referencia para aprender no es asset para distribuir.** Un decompilado, una captura o un
vídeo sirven para medir reglas; no autorizan copiar bytes, modelos ni audio. La licencia de un
archivo puede diferir de la raíz, y la de los pesos de la del código.

## Cierre mínimo

```text
INVESTIGACIÓN: pregunta/decisión y fecha:
Criterios y resultado que descarta:
Candidatos: URL, versión, licencia, compatibilidad, coste, reutilización:
Prueba discriminante: caso, instrumento, esperado y control:
Resultado: observado, negativo conservado, límites:
Decisión: opción, alternativa, riesgo, dato pendiente, condición de revisión:
Evidencia: rutas, huellas, informes y fecha:
```

## Límites

No conviertas la ficha en un GDD ni en un tracker. No inventes APIs, licencias ni ganancias.
No ejecutes ni instales durante una investigación de solo lectura. No cambies un motor ya
fijado sin autorización. No presentes una lectura como ejecución.

## Referencias

- `13 · 31 — Investigación previa y reutilización`
- `13 · 28 — Elicitación`
- `13 · 29 §2.2 — Skills por fase`
- `13 · 30 §8 — Adoptar métodos externos`
