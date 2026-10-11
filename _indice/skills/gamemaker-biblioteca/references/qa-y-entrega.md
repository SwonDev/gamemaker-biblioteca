# QA y entrega

Lee al medir, probar, revisar o declarar verde, aceptación, terminado o publicación.

Contenido: instrumentos y alcance · cierre de un juego · límites de portabilidad.

## Instrumentos y alcance

| Necesito | Comando o contrato |
|---|---|
| Validar todo el GML de un proyecto | `python3 "$BIB/_indice/validar-proyecto.py" /ruta/al/proyecto --todo` — **sale con 1** ante llamadas que su análisis no encuentra definidas, declaradas ni asignadas, también sin `--todo`. Este flag muestra el detalle de desconocidos: revísalos. La ausencia de asignaciones permite distinguir una función inexistente de un posible método de struct; es análisis léxico, no resolución dinámica. Las de plataforma (`steam_*`, `ps5_*`…) van aparte y no hacen fallar: comprueba su extensión y target. Consulta el `--help` disponible |
| **¿Es un juego o solo un bucle de juego?** | `python3 "$BIB/_indice/auditar-juego-completo.py" /ruta/al/proyecto` |
| **Escribir una maqueta o simulación** | Una simulación es tan buena como su calibración, y **escribirla con cuidado NO es calibrarla**. La forma robusta: que **reproduzca al arrancar unas mediciones independientes** y, si no lo consigue, **se declare descalibrada y no analice nada**. Así deja de ser fiable «hoy porque alguien lo comprobó» y pasa a serlo cada vez que se ejecuta — si el balance cambia, se calla en vez de dar un APTO falso. Con controles que TIENEN que fallar. Y aun así su veredicto es el peldaño 2: decide el juego corriendo. `13/10 §8.6 quater` |
| **Cuando el resultado sale raro** | Sospecha del **instrumento** antes que de lo medido: cuatro veces en un día el fallo estaba en la herramienta. Los cuatro los cazó el mismo hábito — **saber qué número tiene que salir ANTES de ejecutar** — y la frase que los resume es *«un control que nunca toca no es un control»*. Mete siempre un caso que TIENE que fallar: una comprobación que solo mira casos buenos no distingue «todo bien» de «no estoy mirando». Y si una medición contradice a la documentación, **sospecha primero que miden variables distintas**. `13/10 §8.6 bis` |
| **Cómo se verifica de verdad** | **Tres peldaños, y los dos primeros son los baratos**: el comando dice que sí → el archivo dice que sí → **el juego corriendo dice que sí**. Medido: alguien verificó nueve valores leyendo los `.yy` (`fallos = 0`, honesto) y en esa misma línea iba impreso el origen que desplazaba cuatro piezas una celda — comprobó la escritura, no el efecto. Y cuidado con el **verde por omisión**: una lista de objetos escrita a mano da ✓ sin mirar los nuevos, y una guarda mal elegida (`is_struct` sobre un id de instancia) sale callando. **Una comprobación que no dice cuántas cosas ha mirado no vale.** `13/10 §8.6 quater` |
| ¿Las trampas del CLI siguen siendo ciertas hoy? | `bash "$BIB/_indice/verificar-trampas.sh"` — las reproduce contra el CLI instalado. Si alguna ya no se cumple, este documento está desfasado |
| ¿El código reutilizable de la biblioteca hace lo que dice? | `bash "$BIB/_indice/validar-ejecucion.sh"` — monta un juego real y lo **ejecuta**: **205 comprobaciones en la batería histórica documentada** sobre los 13 scripts de `06`. Compilar no es ejecutar: sacó cuatro fallos que compilaban limpios. **Valida el banco antes de arrancarlo**, porque un nombre inventado ahí dentro compila con exit 0 y CUELGA la ejecución sin decir nada |

- Nada está «hecho» sin `gm-cli compile` limpio y su salida real reportada. `--errors-only`
  sirve para iterar rápido, pero **antes de dar un juego por terminado, compílalo al menos una
  vez sin ese flag y lee los avisos**: es el único modo que muestra el `WARNING` de un
  *included file* sin copiar (trampa 8). Y **compilar limpio no es funcionar**: la fuente muda y
  el guardado roto de las trampas 5 y 6 compilan sin una queja (`13/10 §8.6` da las dos
  comprobaciones que sí los cazan).

- No declares un juego «terminado» sin compararlo punto por punto con el checklist maestro de
  `04/00`. Si algo falta o no aplica, dilo; el silencio no vale.

## Cierre de un desarrollo

7. **Antes de decir «terminado»**, en este orden:
   a. `python3 "$BIB/_indice/auditar-juego-completo.py" <proyecto>` — mira el `.yyp`, los `.yy`
      y todo el `.gml`, y te dice qué piezas del envoltorio **no encuentra**: menú, opciones,
      pausa, guardado, créditos, fin de partida, sonido, mando, si el jugador entra por una
      portada o directo al nivel, y qué objetos sin sprite están pintando rectángulos. Sale con
      código 1 mientras falte algo, para que no se pueda pasar por alto. También avisa de
      **objetos contra los que colisiona tu código y que no tienen máscara** —sin sprite ni
      `maskSpriteId`, `place_meeting()` no los encuentra nunca: son invisibles Y atravesables,
      sin un solo error. Y de **sprites de personaje que son un color plano**, que son el
      rectángulo prohibido guardado como PNG en vez de dibujado — el detector de rectángulos no
      los ve porque el objeto sí tiene sprite. Y de tres cosas más del checklist de `04/00` que
      una máquina sí puede mirar: si **alguien dibuja en Draw GUI** (donde viven el HUD y los
      menús), si hay **texto escrito a pelo en un `draw_text`** —que no se puede traducir— y si
      el **splash o la intro se pueden saltar**.
      **Y te lista los recursos que creas y no destruyes nunca**: `ds_*`, superficies,
      buffers, partículas, *vertex buffers*, emisores de audio y *time sources*. GameMaker
      no los recoge solo —los structs y los arrays sí, estos no—, así que cada entrada en
      la sala deja otro y el juego que va fino en dos minutos se arrastra a la media hora.
      Es la clase de fallo que no sale probando cada mecánica por separado, solo cuando dos
      estados se cruzan: la lista entera, con la tanda para cazarlos, está en `13/10 §12 bis`.
      **También te dice qué sistemas has escrito que ya existían hechos** —entrada, texto,
      diálogo, serialización, guardado, tweens, pathfinding, idiomas—: tres agentes seguidos
      escribieron su propio sistema de entrada teniendo `Input` en el catálogo, así que el paso
      «mira `11 · _CATALOGO.md` antes de escribir un sistema» dejó de ser una frase y pasó a
      ser una comprobación.
   b. Cada ✗ es **una pregunta, no una acusación**: puede ser un falso positivo (un menú que vive
      dentro de otra sala) o puede faltar de verdad. Compruébalo tú.
   c. Compara además, pantalla por pantalla, contra el checklist maestro de
      `04/00 - Anatomía de un juego completo` **y contra las tres listas que enlaza**:
      `04/41 §4` (transiciones, carga y pausa), `13/05 §4` (UI antes de publicar) y
      `05/02 §4.4` (build de release). **No son opcionales**: la tabla de `04/00` las presenta
      como «detalle», y una casilla marcada sin abrir la lista que enlaza no está marcada — es
      un fallo real y medido, no una hipótesis (`_indice/auditorias/r12-prueba-plataformas.md`
      §1.12). El script cubre lo que una máquina puede ver; el resto —si el menú se entiende, si
      la historia se sostiene— no lo cubre nadie más que tú.
   d. **Si no puedes ejecutar el juego** (sin `run`, sin pantalla, tarea de fondo), quedan dos
      redes, y conviene tender las dos:
      · **Recompón la pantalla fuera del motor** —los mismos PNG, la misma rejilla, el mismo
        orden de dibujo, unas 150 líneas con Pillow— y **mírala**: `13/10 §8.6`, procedimiento
        1 bis. Es lo que más ha cazado: un signo invertido en el encaje de cámara y un panel que
        se salía de pantalla, dos cosas que ni el compilador ni las preguntas de abajo ven.
        **Y di que es una maqueta**, no una captura: reproduce tu lectura del código, no el
        código, y no vale para dar por buena la trampa 5.
      · Las **seis preguntas de `13/10 §8.8`**, que se responden leyendo y cazan la otra clase
        de fallo — guardas de pausa mal colocadas, ramas que olvidan un caso, métodos ligados a
        instancias que mueren.
      Y di explícitamente qué quedó sin comprobar por no poder ejecutar.
   e. **Lo que recortes, se dice**; no se omite en silencio.
8. **Antes de publicar**: `13/10 - Testing y QA` → `05/02 - Publicar y exportar` →
   `05/05 - Entregar el juego` (firmar y subir) → `05/06` si va a consola.

## Límites de portabilidad registrados

> 🖥️ **Y lo que NO está verificado, dicho por delante para que no lo descubras tú.**
> El desarrollo de juegos de esta skill se ha ejecutado entero en **macOS arm64**. Las
> **14 herramientas de `_indice/` identificadas en la auditoría r19 se ejecutaron en Windows**
> (Python 3.12.7 de Windows sobre Wine): 12 pasan y las otras 2 dicen «falta Pillow, no he mirado nada», que es
> la respuesta correcta. Por el camino salieron cuatro fallos —`os.kill` en Windows no
> pregunta, **mata**; un proceso muerto parece vivo si solo miras `OpenProcess`; sin `grep`
> las búsquedas decían «no existe» en vez de «no he mirado»; y seis herramientas reventaban
> al imprimir un `✓`—, todos corregidos.
> **En Windows también se ha ejecutado el JUEGO**: compilado con `--target windows` desde
> el Mac y corrido bajo Wine — DirectX11 por hardware, menús navegados y partida guardada
> con su checksum correcto. Lo que sigue sin probarse ahí es el **IDE** y el empaquetado
> final (`package --target windows` necesita Windows de verdad, Trampa 19). El peldaño de *computer use* está **razonado, nunca medido**. Y de **Kimi y Qwen**
> solo está comprobado que reciben la skill íntegra, no que la activen — Qwen, además,
> declara `~/.claude/skills` y no `~/.qwen/skills` en su `settings.json`.
> Detalle en `_indice/auditorias/r19-cobertura-y-portabilidad.md`.
>
> Ese resultado es histórico y no acredita herramientas añadidas o cambiadas después.
> Consulta el recibo de cada revisión: la ejecución de contratos r47 y HTTP r48 se limita
> a macOS VM; una autoprueba Python o una revisión de PowerShell tampoco demuestra
> ejecución del runner ni empaquetado en Windows nativo.
