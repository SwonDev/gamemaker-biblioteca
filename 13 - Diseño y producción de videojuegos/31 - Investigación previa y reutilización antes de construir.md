# 31 · Investigación previa y reutilización antes de construir

> **Puerta de investigación antes de una decisión costosa.**
> No sustituye la [especificación](<28 - De hazme un juego a una especificación - el protocolo de elicitación del agente.md>)
> ni los [contratos de desarrollo](<29 - Desarrollo con IA - orquestación, crítica y evidencia.md>):
> los alimenta con evidencia cuando la decisión todavía está abierta.
> Investigación contrastada el **15-10-2026** y ampliada el **07-11-2026** con el caso Relicwild;
> fuentes y límites al final.

Esta ficha existe porque hay una decisión que no es ni requisito ni implementación: **qué
alternativa elegir antes de escribirla**. En el resto del método se le llama **research-first**.
Un motor, una técnica de mallado, un formato de guardado, una librería de entrada o un asset
reutilizable pueden costar semanas si se eligen por intuición. La investigación previa convierte
esa elección en una comparación con evidencia, candidatos descartados y una prueba que distingue.

No es un GDD, un tracker ni un documento de arquitectura. Es una ficha de decisión que vive
junto al encargo y se cierra cuando la decisión queda registrada.

## 1 · Cuándo se abre

| Situación | ¿Investigación previa? |
|---|---|
| El motor, la plataforma o el pipeline ya están fijados por el usuario o por una ADR vigente | No se reabre; se documenta el límite y se construye dentro de él |
| Hay que elegir motor, técnica, formato, librería o asset y la decisión es cara de revertir | Sí |
| El requisito es claro pero no sabemos si existe una solución reutilizable | Sí, acotada a la pregunta |
| Es una corrección pequeña con reproducción y causa conocidas | No; basta el ciclo de 13/29 §3 |
| El usuario pide «investiga» o «compara» | Sí, con el contrato de §2 |

La puerta se abre **antes** de comprometer arquitectura, licencia o producción en volumen. No
se abre para llenar un documento: si la pregunta se responde leyendo una firma o una página
oficial, se responde y se sigue.

## 2 · El contrato de ocho puntos

1. **Incertidumbre y decisión.** Qué no sabemos, qué decisión desbloquea y qué se haría
   distinto según la respuesta. Sin pregunta decisiva no hay investigación: hay exploración.
2. **Criterios de aceptación.** Qué evidencia permitiría elegir y qué resultado obligaría a
   descartar. Se fijan antes de mirar candidatos.
3. **Candidatos.** Repos, motores, técnicas, optimizaciones, referencias y assets. Para cada
   uno: URL, commit o versión, licencia del código y de los pesos/assets, compatibilidad con
   el target, coste de adaptación, mantenimiento y qué se reutiliza (código, idea o asset).
4. **Motores alternativos.** Solo si no hay elección fijada. Experimento mínimo falsable, sin
   migración por moda; se conservan motor elegido, WIP, modelos y permisos.
5. **Prueba discriminante.** El caso más pequeño que separa las opciones; resultado esperado
   antes de ejecutar; qué se mide y con qué instrumento. Se ejecuta solo si está autorizada y
   en un entorno aislado.
6. **Resultado y descarte.** Qué se probó, qué se rechazó y por qué. El intento negativo se
   conserva: evita repetir la misma hipótesis seis meses después.
7. **Cierre con riesgos.** Recomendación, alternativa, dato que falta, condición de revisión y
   qué evidencia invalidaría la elección. Cierre es decisión registrada, no «he investigado».
8. **Límites.** La investigación es de solo lectura **mientras el encargo lo sea**. Un
   experimento futuro puede ejecutarse si está explícitamente autorizado y aislado; nunca
   altera WIP, permisos, modelos ni recursos compartidos. Si falta acceso, se declara y se
   continúa lo independiente.

**Aportación del caso.** El caso Relicwild (2026) añadió tres reglas concretas a esta ficha:
(a) el informe de investigación conserva la lista de intentos ya rechazados para no repetirlos;
(b) la licencia se separa en código, pesos y salidas, y la confirmación del titular se registra;
(c) la prueba discriminante conserva el resultado negativo. El resto del contrato es método
general de la biblioteca y no se atribuye al caso.

La lista canónica de decisiones que abren ficha es **motor, arquitectura, formato, librería,
técnica o asset caro de revertir**; guardado, multijugador y plataforma entran por arquitectura.

## 3 · Ficha de candidato

Una tabla evita comparar recuerdos. Como mínimo:

| Campo | Qué debe decir |
|---|---|
| Candidato | Nombre, URL, commit o versión fijada |
| Qué resuelve | La capacidad concreta, no la categoría |
| Licencia | Código, pesos, assets y avisos transitivos, por separado |
| Compatibilidad | Runtime, target, plataforma, versión y dependencias |
| Coste | Adaptación, mantenimiento, memoria, rendimiento y licencia |
| Reutilización | Código, idea o asset; qué se copia y qué se reescribe |
| Evidencia | Documentación leída, prueba ejecutada o informe consultado |
| Riesgo | Qué puede invalidar la elección y qué falta por verificar |

**Referencia para aprender no es asset para distribuir.** Un decompilado, una captura o un
vídeo sirven para medir reglas y proporciones; no autorizan copiar bytes, modelos ni audio.
La licencia de un archivo puede diferir de la licencia de la raíz, y la de los pesos puede
diferir de la del código. Se archivan las tres cuando el candidato entre en el producto.

## 4 · Qué se compara de verdad

- **Capacidad, no popularidad.** Un repo con más estrellas no resuelve tu caso si no cubre tu
  target o tu versión.
- **Compatibilidad por consumidor.** Que un formato exista no significa que el juego, el
  editor, el exportador y el pipeline lo lean igual.
- **Coste total.** Adaptación, mantenimiento, dependencias transitivas, memoria, tiempo de
  carga y licencia. Una victoria de rendimiento aislada no compensa una semana de integración.
- **Madurez y reversibilidad.** Fecha del último cambio, issues abiertos, versión fijada y
  facilidad para volver atrás.
- **Lo que ya existe en la biblioteca.** `11 - Código descargado/_CATALOGO.md`, los capítulos
  de `04` y `13`, y las librerías de `07` antes de escribir un sistema nuevo.

## 5 · Prueba discriminante y negativos

La prueba discriminante no demuestra que el candidato sea bueno: demuestra que **separa** las
opciones. Debe tener:

1. un caso mínimo que ambas opciones puedan intentar;
2. un resultado esperado escrito antes de ejecutar;
3. un instrumento con unidades y límite;
4. un control que deba fallar si el instrumento no mide;
5. un registro del intento, aunque salga mal.

Si la prueba no se puede ejecutar por permisos, cuota o entorno, se declara **no ejecutada** y
la decisión se toma con evidencia documental, marcando la incertidumbre. No se convierte una
lectura en una ejecución.

## 6 · Decisión, riesgos y cierre

El cierre registra:

- la opción elegida y la razón en una frase;
- la alternativa relevante y por qué se descartó;
- el dato que falta y cómo se obtendría;
- la condición que obligaría a revisar la decisión;
- la evidencia que la invalidaría;
- el coste y el límite aceptados.

Una decisión que cruza módulos, cambia el motor o introduce una dependencia de pago merece una
ADR ligera (13/11 §3.5). La investigación no autoriza a implementar por sí sola: autoriza a
decidir con evidencia.

## 7 · Qué no es investigación previa

- Copiar la primera respuesta de un buscador y llamarla comparación.
- Ejecutar un benchmark sin hipótesis ni control.
- Leer el README de un repo y deducir que cumple la licencia.
- Probar un motor nuevo sin conservar el que ya funciona.
- Convertir la ficha en un documento de arquitectura permanente.
- Declarar «investigado» sin registrar la decisión ni el descarte.

## 8 · Registro mínimo

```text
INVESTIGACIÓN: pregunta/decisión y fecha:
Criterios de aceptación y resultado que descarta:
Candidatos: URL, versión, licencia de código/pesos/assets, compatibilidad, coste, reutilización:
Prueba discriminante: caso, instrumento, resultado esperado y control:
Resultado: observado, negativo conservado, límites:
Decisión: opción, alternativa, riesgo, dato pendiente y condición de revisión:
Evidencia: rutas, huellas, informes y fecha:
```

## Ver también

- [13 · 28 — Elicitación](<28 - De hazme un juego a una especificación - el protocolo de elicitación del agente.md>):
  preguntas de arranque, valores por defecto y cambios de idea.
- [13 · 29 — Desarrollo con IA](<29 - Desarrollo con IA - orquestación, crítica y evidencia.md>):
  contratos, carriles, crítica, evidencia y recursos.
- [13 · 30 — Especificación viva](<30 - Especificación viva y mejora del método.md>):
  requisito versionado, promoción de aprendizaje y evaluación de la skill.
- [13 · 11 — Producción](<11 - Producción, alcance y lanzamiento.md>): alcance, ADR ligera y
  puertas de fase.
- [13 · 06 — Arquitectura](<06 - Arquitectura de un proyecto GameMaker.md>): decisiones que
  cuestan reescribir si se toman tarde.

## Fuentes y límites

Investigación de métodos del 15-10-2026 y del 07-11-2026; el caso Relicwild se cita como
evidencia histórica, no como ejecución repetida aquí. La ficha no instala nada, no cambia
motores ni sustituye la especificación. Los umbrales, modelos y números del caso son suyos:
esta biblioteca conserva el procedimiento, no sus valores.
