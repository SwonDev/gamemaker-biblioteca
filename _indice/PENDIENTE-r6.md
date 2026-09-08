# Dónde lo dejamos — 8 de septiembre de 2026

> **La biblioteca está coherente y publicada.** `python3 _indice/actualizar.py` sale en verde con
> sus 13 pasos. Todo lo cerrado está subido a
> <https://github.com/SwonDev/gamemaker-biblioteca>. Esto es solo el punto de retomada.

## Lo único a medias

Un agente estaba **documentando los cinco hallazgos de la prueba de regresión**
([`auditorias/r6-regresion.md`](./auditorias/r6-regresion.md)). Su trabajo queda en disco aunque
la sesión se cierre. Al volver, lo primero es **comprobar qué escribió y consolidarlo**:

```sh
cd "/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje"
git status --short                 # ¿qué tocó?
python3 _indice/actualizar.py      # ¿sigue todo coherente?
```

Los cinco hallazgos que tenía que documentar, por si hubiera que rematarlos a mano:

1. **La receta de horneado de fuentes** (`12/09`, trampa 5) necesita fijar también `%Name` —no
   solo `name`— y `parent: null`. Sin eso `resourcetool` falla de **tres formas distintas** para
   la misma causa: repara mal el recurso, crashea con `AccessViolationException`, o da un error de
   *linking* legible. Hay que documentar los tres síntomas juntos, o nadie los reconocerá como
   el mismo problema.
2. **`resourcetool script` (modo por lotes) reporta éxito y NO persiste** un `RESOURCE SET` sobre
   `project.RoomOrderNodes`. Hay que reordenar con `eval`, uno a uno. Matiza dos secciones
   escritas ayer: la que recomienda el modo por lotes por ser 6× más rápido, y la del orden de salas.
3. **`RESOURCE DELETE` de una sala reinicia TODO `RoomOrderNodes`** al orden de creación, no solo
   el hueco. Regla: reordenar **después** de borrar, nunca antes.
4. **`ResourceTool@2026.0.17` tiene un `AccessViolationException` no determinista**: 2 de 5
   llamadas idénticas fallaron sobre un proyecto sano. Mitigación: reintentar.
5. **Un objeto sin sprite es invisible** para `instance_position()` y `place_meeting()`. Es de GML,
   no del CLI. Causa clásica de «mi colisión no funciona y no sé por qué».

**Ojo con esto al retomar:** el agente ya decidió que uno de los hallazgos merece ser trampa
nueva —cambió el título de `12/09 §0` a «las **once** trampas»— pero **la sección de la trampa 11
puede haber quedado sin escribir** (al parar solo llegaba hasta la 10). Comprueba:

```sh
grep -n "^### Trampa 1[01] " "12 - Utilidades e integraciones/09 - Manual del agente de IA - operar GameMaker con gm-cli.md"
```

Si falta, escríbela (será uno de los cinco de arriba, seguramente el nº 1 o el nº 2) y **añádela
también a `SKILL.md`**, que hoy dice diez, ejecutando después
`python3 _indice/sincronizar-skill.py`. El enlace de `AGENTS.md` ya apunta a «once».

## Estado en este momento

- **267 documentos** · **3384 bloques de GML** que compilan contra el runtime real ·
  **2099 rutas** y **1469 anclas** verificadas · espejo del manual a la par del inglés.
- La skill avisa de **diez trampas**, todas verificadas ejecutando, y está enlazada en los siete
  destinos de CLI instalados en esta máquina.
- **Tres pruebas de uso pasadas**: un arcade (`r5-revalidacion.md`), una aventura narrativa con
  tres finales (`r6-prueba-narrativa.md`) y un sokoban de regresión (`r6-regresion.md`).

## Lo que ha demostrado funcionar, para la próxima ronda

**Poner a un agente a construir un juego de verdad encuentra lo que ninguna auditoría documental
ve.** La primera prueba destapó dos bugs graves que cuatro rondas no habían visto; la segunda,
tres huecos; la tercera, cinco detalles finos. La curva baja, que es la señal de que converge.

Y la regla que más ha rendido: **cada hallazgo se convierte en una comprobación automática**, no
en un aviso escrito. Así nacieron la compilación de bloques, la verificación de anclas, la de
integración y la de aridad.
