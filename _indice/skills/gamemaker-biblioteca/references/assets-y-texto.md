# Assets, fuentes y texto

Lee al producir, integrar o seleccionar arte, audio, fuentes, atlas o texto traducido.

Conserva el modelo/generador elegido por el usuario. La receta no autoriza sustituirlo,
iniciar servicios pausados, gastar o publicar. Separa uso privado y redistribución de los recursos.

| Necesito | Comando o contrato |
|---|---|
| **Necesito el sprite FINAL, animado y de producción** | La cadena de `07/23 §5 bis`, en este orden: **el generador y modelo de imagen elegidos por el usuario** genera cualquier asset (hoja, iconset, con fondo o sin él) → **`puerta-pixel-art.py`** dictamina → **`pixel-art-fixer`** (MIT) lo devuelve a una rejilla real, solo si la puerta determina que necesita reparación; parecer pixel art no acredita una rejilla correcta → **`sprite-gen`** (Apache-2.0) anima desde **UNA base con la identidad bloqueada** y entrega atlas + `manifest.json` con rectángulos y fps por estado → `python3 "$BIB/_indice/atlas-a-gamemaker.py" <run> --salida <carpeta>` lo registra. Pedirle «una hoja de sprites» a un modelo en crudo sigue sin servir, y `07/23 §2` dice por qué |
| Tengo un dibujo y necesito la hoja de sprites animada | `sprite-gen` (Apache-2.0, skill de Codex/Claude + CLI) monta el atlas y su `manifest.json`; el paso a GameMaker, que él no trae, lo hace `python3 "$BIB/_indice/atlas-a-gamemaker.py" <run> --salida <carpeta>` → `gm-cli resourcetool script`. Receta en `12/09 §5.2` peldaño 2 ter |
| ¿Este PNG hay que repararlo, o repararlo lo destruye? | `python3 "$BIB/_indice/puerta-pixel-art.py" <carpeta de PNG>` — **antes** de pasarle `pixel-art-fixer` a nada |
| **El usuario me dice dónde tiene sus assets** | `python3 "$BIB/_indice/auditar-biblioteca-assets.py" "<la RAÍZ de su biblioteca>" [--profundidad 3] [--json informe.json] [--solo-fuentes]` — **antes de copiar nada**. Es de solo lectura. Busca cinco señales estructurales, no corazonadas: medios sin licencia (ni heredada ni dentro del `.zip`), varias **familias** de licencia bajo un solo nombre, el **runtime del motor** (un pack no trae `UnityEngine.*.dll`: eso es un juego descompilado), un **extractor guardado junto a los medios**, y el binario de cada tipografía (`fsType`, licencia embebida y los glifos `áéíóúüñ¿¡`, que si faltan **no dan error**: miden cero). **Un bloqueo suyo no es un veredicto y su silencio no es un aprobado**, y apúntala a la RAÍZ: si le das una subcarpeta no puede ver el `.zip` con la licencia que está en otra. Criterio y casos medidos en `07/09 §10 bis.9` |
| **¿Cabe el texto traducido?** | `python3 "$BIB/_indice/medir-caja-de-texto.py" idiomas/*.json --hoja fuente.png --celda 8x11 --mapa-archivo mapa.txt --caja 356 --sep 1 [--espacio 4] [--escala 1.5]` — reproduce `font_add_sprite_ext` y mide **cadena a cadena**. «Diseña con el idioma más largo» NO se aplica en bloque: medido, el español era un 9,1 % más largo en total y aun así **el inglés ganaba en 23 de 79 cadenas**. Caza además los caracteres que faltan en el mapa —**miden cero**, así que mutilan la palabra Y falsean la cuenta— y el espacio sin celda, que GameMaker sustituye por **la anchura del carácter más ancho**. Criterio en `04/21 §4 bis` |
| **Texto en otro idioma que NINGÚN linter caza** | Una **función** que devuelve el texto ya hecho no es un literal, así que el `grep` de «cero cadenas en `draw_text`» no la ve. Medido: `InputVerbGetBindingName()` devuelve «arrow left», «space» y «escape» **en inglés**, en medio de una frase en español — y se descubrió mirando una captura del juego, no el código. `auditar-juego-completo.py` lista ahora las funciones cuyo valor se dibuja tal cual, saltándose `txt()`, las `txt_*` propias y las de número. Criterio en `04/21 §4 ter` |
| Voy a pedirle un sprite a **Retro Diffusion** y cuesta dinero | `python3 "$BIB/_indice/validar-peticion-retrodiffusion.py" peticion.json [--imagen inicio.png] [--presupuesto 0.50]` — **antes de mandarla**. Comprueba el estilo contra el catálogo, el tamaño contra los límites de ese estilo concreto (no los de la API), el lote, las referencias, los prefijos `data:`, y mide el fotograma de partida **en disco**. No usa red ni clave: no puede gastar. Las nueve trampas caras, en `07/23 §1 bis.1` — la primera es que **el POST de v2 no devuelve la imagen** y quien lea `base64_images` de esa respuesta se queda sin nada y con el cargo hecho |

- El código de los juegos comerciales de `11 - Código descargado/juegos_y_motores/` (Pizza
  Tower, Deltarune, AM2R, Hotline Miami, Kirby) se lee, no se copia.

- **Un rectángulo de color no es un sprite.** Ni un cuadrado, ni un círculo liso, ni un SVG
  improvisado: si entregas eso como personaje, enemigo u objeto, el juego parece un prototipo por
  mucho que el código sea bueno. La escalera de `12/09 §5.2` da la salida digna —silueta por
  código con paleta coherente, assets libres, o generación por IA— y para el sonido está
  `13/09 §8 bis`. **Baja un peldaño antes de rendirte, nunca entregues el rectángulo.**

## Biblioteca personal de assets

**Si el usuario te dice dónde tiene SUS assets, hay un método y no es «buscar
   lo que encaje».** Es el encargo real —«tengo packs en este disco, úsalos»— y tiene una
   trampa: los assets libres traen su licencia declarada, pero una biblioteca personal es
   una mezcla de packs comprados, bundles y carpetas sin origen. Todo está en
   `07 - Ecosistema/09 - Asset packs y recursos gráficos.md` §10 bis.
   El resumen que no puedes saltarte:

   - **Licencia primero, encaje después.** Si buscas por lo que te gusta, acabas
     enamorado de un pack que no puedes tocar. Y **el índice de la biblioteca NO es la
     licencia**: hay que abrirla pack a pack.
   - **Tres filtros, no uno**: licencia · **estilo** (¿se dibuja como mi juego?) ·
     **encaje** (¿mi tema y mi resolución?). Los dos últimos se subestiman siempre y son
     los que hacen que un juego con arte comprado se vea peor que uno con arte propio:
     un pack CC0 impecable de «naves» resultó ser aviones de la Segunda Guerra Mundial.
   - **«Usarlo» y «redistribuirlo» no son lo mismo.** Muchas licencias permiten meterlo en
     tu juego compilado y prohíben subir el archivo suelto a un repositorio público.
   - **Tipografías: dos comprobaciones.** Que tenga `á é í ó ú ñ ¿ ¡` —GameMaker omite en
     silencio el glifo que falta— y qué dice **el binario**, que puede contradecir al pack.
   - **Si no encuentras la licencia, no entra — y lo dices.** Separando «lo prohíbe» de
     «no la he encontrado»: lo segundo el usuario sí puede resolver buscando su factura, y
     callarlo puede costarle el mejor arte de su juego.
