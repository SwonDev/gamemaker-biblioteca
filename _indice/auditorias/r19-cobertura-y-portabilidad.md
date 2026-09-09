# r19 · «¿Qué le falta?» deja de ser una opinión — y Windows deja de ser un hueco en blanco

> **Encargo**: comprobar que no faltan géneros, recursos, herramientas de IA ni repositorios, y
> cerrar lo que quedaba sin verificar. **Fecha**: 2026-09-09.
>
> El problema con las cinco revisiones anteriores de «qué le falta» es que fueron **miradas**,
> no mediciones: nadie puede repetirlas, y la sesión siguiente vuelve a empezar de cero sin
> saber qué se comprobó ya. Aquí se convierten en una herramienta.

---

## 1 · La cobertura, medida

Nuevo `_indice/auditar-cobertura.py`. Cada fila de sus tres listas es **una cosa que un juego
real necesita**; para cada una se busca evidencia en los documentos de contenido —las
auditorías quedan fuera a propósito: un género mencionado solo en un informe de trabajo no está
cubierto para quien viene a hacer un juego—. La lista se escribe a mano, porque es un juicio
sobre qué debería cubrir la biblioteca; la comprobación es automática y el resultado,
reproducible.

| Bloque | Puntos | Resultado |
|---|---:|---|
| Géneros | 36 | ✓ los 36 con respaldo |
| Recursos | 13 | ✓ los 13 |
| Herramientas de IA | 11 | ✓ las 11 |
| **Total** | **60** | **exit 0** |

Repositorios: **635** catalogados en `_RUTAS.json`; que cuadren con el disco lo comprueba
`actualizar.py` paso 3, y se imprime aquí para tener la cifra en el mismo sitio.

**Lo que este número NO dice.** Es una comprobación de **presencia**, no de calidad: que
«sigilo» aparezca en dos documentos demuestra que está tratado, no que esté bien tratado. Por
eso cada ✗ se presenta como una pregunta —«o falta de verdad, o está cubierto con otras
palabras, y entonces lo que toca es añadir el sinónimo a la lista, no un documento nuevo»—.
Siete casos de autoprueba, entre ellos el que impide el peor fallo posible: un árbol vacío que
contesta «sin huecos».

---

## 2 · Windows: dos fallos reales encontrados **sin** tener Windows

«Sin verificar en Windows» llevaba meses escrito como una casilla en blanco. No hay máquina
Windows aquí, así que no se puede ejecutar — pero sí se puede **auditar el código por sus
rutas específicas de esa plataforma**, y ahí salieron dos fallos, uno de ellos grave y
recién introducido en esta misma sesión.

### 2.1 · 🔴 `os.kill(pid, 0)` no pregunta en Windows: MATA

El cerrojo de las carpetas de trabajo (`_indice/cerrojo.py`, escrito hoy) decidía si un cerrojo
estaba huérfano preguntando «¿sigue vivo su dueño?» con la forma canónica de POSIX:

```python
os.kill(pid, 0)      # en Linux y Mac: no envía nada, solo pregunta
```

La documentación de Python es explícita: **en Windows, `os.kill(pid, sig)` con cualquier señal
que no sea `CTRL_C_EVENT` o `CTRL_BREAK_EVENT` llama a `TerminateProcess`**. Es decir, la línea
que pregunta si un proceso vive lo **termina**.

En este sitio concreto eso es lo peor posible: la función existe para decidir si puede quedarse
con una carpeta de trabajo. En Windows habría **matado la compilación de otra persona** y luego
se habría quedado con su carpeta.

Corregido con `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)`, que solo consulta. Y con dos
casos de autoprueba que se ejecutan **desde cualquier sistema**, espiando `os.kill`:

```
✓ la rama de Windows NUNCA llama a os.kill (allí MATA)
✓ y la de POSIX sí lo usa, con la señal 0
```

### 2.2 · Sin `grep`, `buscar.py` decía «no existe» en vez de «no he mirado»

`grep` viene de serie en macOS y Linux; en Windows, no. `buscar.py` ya avisaba de ello por
pantalla —bien— pero devolvía **exit 1**, que en el contrato de esta biblioteca significa «se ha
buscado y no está». Es el **falso «no existe»**, el peor fallo posible aquí, entrando por la
puerta de Windows: el aviso se lee, el código de salida es lo que consume un script.

Las cuatro búsquedas de texto salen ahora con **2** («no se ha podido buscar»), y `--todo` lo
dice con todas las letras: de sus cuatro fuentes, tres se recorren con `grep`, así que sin él
solo se ha mirado una. Cuatro casos de autoprueba, fingiendo que `grep` no está.

> **Lo que esto cambia en el estado de verificación**: Windows sigue **sin ejecutarse** — no hay
> máquina, y así seguirá escrito. Pero ya no es una casilla en blanco: sus rutas de código
> específicas están auditadas, y las dos que estaban mal, corregidas y con prueba.

---

## 3 · Kimi y Qwen: qué se puede afirmar y qué no

Tampoco se pueden ejecutar aquí (límites y autenticación ajenos). Lo que sí se comprueba, y se
comprobó, es **qué reciben exactamente**:

| Destino | Versión | Frontmatter | Contenido | Tildes |
|---|---|---|---|---|
| Claude Code | r18 | ✓ | idéntico al canónico | ✓ |
| Codex (pool) | r18 | ✓ | idéntico | ✓ |
| Genérico `~/.agents` | r18 | ✓ | idéntico | ✓ |
| opencode | r18 | ✓ | idéntico | ✓ |
| **Qwen Code** | r18 | ✓ | idéntico | ✓ |
| **Kimi Code CLI** | r18 | ✓ | idéntico | ✓ |

Los seis reciben el mismo archivo, byte a byte, con `name` y `description` presentes y las
tildes intactas. **Eso no demuestra que Kimi o Qwen la activen bien**: demuestra que el
problema, si lo hay, no está en lo que se les entrega. Es tan lejos como se puede llegar sin
sus credenciales, y se dice así.

---

## 4 · Estado, sin adornos

- **Verificado ejecutando**: macOS arm64 — 14 herramientas · 157 casos de autoprueba ·
  el juego de [`r18`](./r18-prueba-visual.md) construido, ejecutado y fotografiado.
- **Verificado por auditoría de código, no ejecutando**: las rutas de Windows de `cerrojo.py`
  y `buscar.py`, con prueba automática que corre en cualquier sistema.
- **Sin verificar, y así seguirá hasta que haya máquina o cuenta**: Windows ejecutándose de
  verdad · el peldaño de *computer use* (razonado, nunca medido) · Kimi y Qwen activando la
  skill.
