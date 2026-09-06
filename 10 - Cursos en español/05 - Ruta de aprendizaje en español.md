# 05 · Ruta de aprendizaje 100 % en español

> Cómo combinar lo que existe en castellano —que está incompleto y desfasado— con esta
> biblioteca —que sí está al día— para aprender GameMaker LTS 2026 **sin pasar por el inglés**.

---

## El problema, dicho claro

| Lo que hay en español | Lo que le falta |
|---|---|
| La mejor pedagogía (Hektor Profe, 100 lecciones) | Está hecha con un motor **descatalogado** (GMS 1.4) |
| La mejor explicación del lenguaje (Altair_AML, 52 min) | Se queda en **2024** |
| El manual oficial traducido (2 602 páginas) | Le faltan **431 páginas**, justo las de 2026, y el texto es de 2021-2022 |
| Recetas concretas (RyVack, Adderly, blogs) | Código de la era **GMS 1.x/2.0** |

**La solución** es leer *esta* biblioteca como columna vertebral y usar los vídeos como
refuerzo hablado. Todo el material propio está escrito para **LTS 2026** y verificado contra
el `GmlSpec.xml` del runtime instalado.

---

## Fase 0 · Prepara la herramienta (medio día)

| # | Haz esto | Material |
|---|---|---|
| 1 | Instala GameMaker LTS 2026 y ponlo **en español** desde las preferencias del IDE | [`01 - Fundamentos/01 · El IDE y el flujo de trabajo`](../01%20-%20Fundamentos/01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md) |
| 2 | Mira el recorrido del IDE en español | [Altair_AML · Interfaz General](https://youtu.be/KRJhX4YgcHo) (17 min) |
| 3 | Aprende a comprobar si una función existe **antes** de escribirla | `python3 "_indice/buscar.py" draw_sprite` |

> 💡 El paso 3 es el que más disgustos ahorra. Todos los tutoriales en español que vas a ver
> son de versiones antiguas, y usan funciones que hoy están obsoletas o retiradas. El buscador
> te lo dice al instante.

---

## Fase 1 · El modelo mental (1 semana)

**Objetivo:** entender qué es una room, un sprite, un objeto, una instancia y un evento.

| # | Material | Formato | Notas |
|---|---|---|---|
| 1 | [Hektor Profe · *Tu Primer Videojuego*](./01%20-%20Academia%20de%20Hektor%20Profe.md), lecciones **01, 02, 04, 05** | 🎥 vídeo | Salta la 03 (instalación de un motor que ya no existe) |
| 2 | [`01 - Fundamentos/06 · Eventos y ciclo del juego`](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) | 📖 lectura | **El documento más importante de toda la biblioteca** |
| 3 | [Altair_AML · Introducción a los EVENTOS](https://youtu.be/tPUNtpHVFSw) | 🎥 16 min | Lo mismo, escuchado en voz alta |
| 4 | [`01 - Fundamentos/09 · Instancias, objetos y herencia`](../01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md) | 📖 lectura | `with()` no tiene equivalente en otros motores |
| 5 | Hektor Profe · *Tu Primer Videojuego*, lecciones **13, 15, 16, 18** | 🎥 vídeo | Step, variables, fin de partida, alarmas |

**Al terminar sabrás:** por qué tu código se ejecuta cuando se ejecuta.

---

## Fase 2 · El lenguaje GML de verdad (2 semanas)

**Objetivo:** escribir GML de 2026, no de 2015.

| # | Material | Formato |
|---|---|---|
| 1 | [Altair_AML · **Introducción Completa al Lenguaje**](https://youtu.be/UneMzjBKODs) | 🎥 **52 min** — véelo entero |
| 2 | [`01 - Fundamentos/02 · Tipos de datos y variables`](../01%20-%20Fundamentos/02%20-%20Tipos%20de%20datos%20y%20variables.md) | 📖 |
| 3 | Hektor Profe · *El Lenguaje GML*, lecciones **01-06** (variables, macros, operadores, expresiones, condicionales, bucles) | 🎥 |
| 4 | [`01 - Fundamentos/07 · Funciones, métodos y ámbito`](../01%20-%20Fundamentos/07%20-%20Funciones%2C%20m%C3%A9todos%20y%20%C3%A1mbito.md) | 📖 ⚠️ **Sustituye a la lección 07 de Hektor Profe**, que está obsoleta |
| 5 | [`01 - Fundamentos/04 · Structs y constructores (POO en GML)`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) | 📖 ⚠️ **No existe en ningún curso en español** |
| 6 | [Altair_AML · ¿Qué son los Structs?](https://youtu.be/gzRbXITRS9Q) | 🎥 4 min — introducción rápida |
| 7 | [`01 - Fundamentos/05 · Arrays y estructuras de datos`](../01%20-%20Fundamentos/05%20-%20Arrays%20y%20estructuras%20de%20datos.md) | 📖 Por qué ya casi nunca usas `ds_*` |
| 8 | [`05 - Referencia/04 · Convenciones y estilo GML`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md) | 📖 Antes de coger vicios |

**Al terminar sabrás:** escribir funciones, métodos, structs y constructores con la sintaxis
actual.

---

## Fase 3 · Tu primer juego completo (3 semanas)

Elige **una** de estas dos vías. No las mezcles.

### Vía A — Guiada en vídeo (recomendada si te cuesta arrancar)

**Hektor Profe · *Juego Arcade PONG*** — 12 lecciones. Es corto, se acaba, y cubre menú,
dificultad y distribución.

Mientras lo sigues, ten abiertos:

- [`04 - Recetas por género/11 · Arcade y juegos de un botón`](../04%20-%20Recetas%20por%20g%C3%A9nero/11%20-%20Arcade%20y%20juegos%20de%20un%20bot%C3%B3n.md)
- [`04 - Recetas por género/15 · Game feel y juice`](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md) — **desde el primer día**

**Traduce el código sobre la marcha.** Cada vez que el vídeo use una función, compruébala:

```sh
python3 "_indice/buscar.py" <función>
```

### Vía B — Con plantilla oficial (recomendada si ya programas)

```sh
gm-cli init --no-interactive -n mi-juego -t "Space Rocks" --ai --toolchain GMS2@2026.0.0.23
```

Y sigue [`04 - Recetas por género`](../04%20-%20Recetas%20por%20g%C3%A9nero/) del género que
elijas. Copia los scripts base de [`06 - Assets y Scripts`](../06%20-%20Assets%20y%20Scripts/README.md).

---

## Fase 4 · Un juego con sistemas de verdad (4-6 semanas)

**Hektor Profe · *Juego Shooter TDS*** (25 lecciones) o ***Juego Action RPG*** (13 lecciones).
Son los dos mejores cursos en español que existen.

Cada bloque de lecciones tiene su equivalente moderno aquí:

| Lecciones del curso | Léelo también en |
|---|---|
| 06-09 · Máquina de estados e IA | `06 - Assets y Scripts/scr_state_machine.gml` · [`04 - Recetas/02 · Top-Down`](../04%20-%20Recetas%20por%20g%C3%A9nero/02%20-%20Top-Down%20_%20Twin-Stick.md) |
| 03 · Fondo, vista y cámara | [`01 - Fundamentos/10 · Rooms, capas, cámaras`](../01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md) · `06 - Assets y Scripts/scr_camera.gml` |
| 12-13, 23 · HUD y barras de vida | [`02 - Novedades 2026/04 · UI Layers y Flexpanels`](../02%20-%20Novedades%202026/04%20-%20UI%20Layers%20y%20Flexpanels.md) ⚠️ hoy hay un sistema mejor |
| 20 · Partículas | [`02 - Novedades 2026/05 · Sistema de partículas nuevo`](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20part%C3%ADculas%20nuevo.md) ⚠️ cambió por completo |
| 21, 24 · Superficies (oscuridad, pausa) | [`08 - Referencia GML/05 · Superficies`](../08%20-%20Referencia%20GML%20completa/05%20-%20Superficies.md) |
| 17 · Música y sonidos | [`02 - Novedades 2026/07 · Audio: buses y efectos`](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md) ⚠️ cambió |
| RPG 13 · Guardado en INI | [`01 - Fundamentos/14 · Persistencia y archivos`](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md) · `06 - Assets y Scripts/scr_save_load.gml` |

---

## Fase 5 · Dejar de escribirlo todo tú (1 semana)

Aquí es donde el español se acaba y hay que tirar de la biblioteca. Las dos librerías que más
tiempo te van a ahorrar tienen explicación en castellano:

| Librería | Vídeo en español | Código descargado |
|---|---|---|
| **Input** (entrada, gamepads, remapeo) | [Altair_AML · Mejora tu proyecto con INPUT](https://youtu.be/mcJ86swsjNE) (11 min) | `11 - Código descargado/librerias/entrada/Input/` |
| **Scribble** (texto y diálogos) | [Altair_AML · Diálogos con Scribble](https://youtu.be/rxsPzpbBv74) (7 min) | `11 - Código descargado/librerias/texto-y-tipografia/Scribble/` |

Para el resto, el catálogo está en español aunque el código esté en inglés:
[`11 - Código descargado/_CATALOGO.md`](../11%20-%20C%C3%B3digo%20descargado/_CATALOGO.md).

---

## Fase 6 · Ponerse al día con 2026 (2-3 días)

**No hay ni un solo vídeo en español que cubra esto.** Es lectura obligatoria:

1. [`02 - Novedades 2026/01 · Resumen LTS 2026.0`](../02%20-%20Novedades%202026/01%20-%20Resumen%20LTS%202026.0.md)
2. [`01 - Fundamentos/03 · Handles — el cambio clave de 2026`](../01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) 🔴
3. [`02 - Novedades 2026/02 · Cambios en GML 2026`](../02%20-%20Novedades%202026/02%20-%20Cambios%20en%20GML%202026.md) 🔴
4. [`02 - Novedades 2026/04 · UI Layers y Flexpanels`](../02%20-%20Novedades%202026/04%20-%20UI%20Layers%20y%20Flexpanels.md)
5. [`02 - Novedades 2026/03 · GMRT — El nuevo runtime`](../02%20-%20Novedades%202026/03%20-%20GMRT%20-%20El%20nuevo%20runtime.md)

---

## Resumen visual de la ruta

```
Fase 0  Herramienta ......  Altair (interfaz) + buscar.py
Fase 1  Modelo mental ....  Hektor 01/02/04/05/13/15/16/18  +  Fundamentos 06 y 09
Fase 2  El lenguaje ......  Altair 52 min  +  Fundamentos 02/04/05/07  +  Hektor GML 01-06
Fase 3  Primer juego .....  Hektor PONG  ó  gm-cli init + Recetas
Fase 4  Juego con sistemas  Hektor TDS (25) ó ARPG (13)  +  Recetas + Novedades
Fase 5  Librerías ........  Altair (Input, Scribble)  +  11 - Código descargado
Fase 6  Ponerse al día ...  02 - Novedades 2026  (solo existe aquí, en español)
```

**Tiempo total estimado: 10-12 semanas** a ritmo de aficionado.

> ⚠️ **La regla que no debes saltarte en toda la ruta:** cada vez que un vídeo escriba una
> función, compruébala con `python3 "_indice/buscar.py" <función>` antes de copiarla. Todos
> los cursos en español son de versiones anteriores del motor.
