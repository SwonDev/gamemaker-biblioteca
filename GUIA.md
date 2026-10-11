# Guía de la biblioteca GameMaker

[Portada](README.md) · [Instalar](INSTALACION.md) · [Aprender](RUTA.md)

No necesitas leerla de principio a fin ni usar una IA. Consulta el material según lo que estés construyendo.

## Rutas de aprendizaje

| Tu objetivo | Empieza por |
|---|---|
| Nunca he programado | [RUTA.md](RUTA.md): sitúate por una prueba concreta y sigue tu nivel |
| Vengo de otro motor | [Fundamentos](<01 - Fundamentos>) y [convenciones GML](<05 - Referencia/04 - Convenciones y estilo GML.md>) |
| Vengo de GameMaker antiguo | [Novedades](<02 - Novedades 2026>) y el índice de símbolos de tu runtime |
| Quiero construir un juego | [Especificación](<13 - Diseño y producción de videojuegos/28 - De hazme un juego a una especificación - el protocolo de elicitación del agente.md>) → [receta](<04 - Recetas por género>) → [juego completo](<04 - Recetas por género/00 - Anatomía de un juego completo.md>) |
| Quiero trabajar con IA | [Método universal](<13 - Diseño y producción de videojuegos/29 - Desarrollo con IA - orquestación, crítica y evidencia.md>) y [skill](./_indice/skills/gamemaker-biblioteca/SKILL.md) |

## Mapa de la biblioteca

| Carpeta | Para qué sirve |
|---|---|
| [01 · Fundamentos](<01 - Fundamentos>) | Lenguaje, objetos, eventos y principios del motor |
| [02 · Novedades](<02 - Novedades 2026>) | Cambios de versión, con fuente y fecha |
| [03 · Cursos](<03 - Cursos (YouTube)>) | Material de cursos; contrasta sus API con tu runtime |
| [04 · Recetas](<04 - Recetas por género>) | Sistemas por género y componentes del juego completo |
| [05 · Referencia](<05 - Referencia>) | Convenciones, glosario y publicación |
| [06 · Assets y scripts](<06 - Assets y Scripts>) | Código propio reutilizable |
| [07 · Ecosistema](<07 - Ecosistema>) | Librerías, extensiones, assets y sus licencias |
| [08 · API GML](<08 - Referencia GML completa>) | Referencia por familias |
| [10 · Cursos en español](<10 - Cursos en español>) | Rutas y recursos para aprender en español |
| [12 · Utilidades](<12 - Utilidades e integraciones/_INDICE-UTILIDADES.md>) | gm-cli, integraciones y búsqueda multimodal |
| [13 · Diseño y producción](<13 - Diseño y producción de videojuegos/_INDICE-DISENO.md>) | GDD, arte, animación, sonido, QA, negocio y método con IA |
| [14 · Juego de referencia](<14 - Juego de referencia/README.md>) | Ejemplo propio con especificación y herramientas |

El espejo del manual (`09`) y los repositorios de terceros (`11`) son corpus opcionales. [Reconstrucción y derechos](PUBLICAR.md). Los recuentos se generan en los `meta` de los índices; no significan que hayas instalado todo ese corpus.

## El buscador

Desde la raíz, con el entorno Python activado y los índices generados:

```bash
python _indice/buscar.py draw_sprite_ext
python _indice/buscar.py --todo "coyote time"
python _indice/buscar.py --listar audio_
python _indice/validar-proyecto.py /ruta/a/MiJuego
python _indice/auditar-juego-completo.py /ruta/a/MiJuego
```

`buscar.py` distingue encontrado, ausente y búsqueda imposible. Un índice ausente o caducado requiere diagnóstico antes de concluir que una función no existe. [Todos los modos de búsqueda](./_indice/COMO-BUSCAR.md).

EmbeddingGemma 2 complementa la búsqueda literal cuando sabes qué necesitas pero no cómo se llama. La [guía semántica](<12 - Utilidades e integraciones/11 - Búsqueda multimodal con EmbeddingGemma 2 - contexto y recursos para agentes.md>) cubre consultas, clasificación, privacidad, modalidades y evaluación. No se instala ni se arranca con la skill.

## Cómo se desarrolla con IA

**Requisitos → especificación → tareas → implementación → revisión → aceptación.** Selecciona las skills por fase y motor. Si no están disponibles, el procedimiento sigue siendo ejecutable leyendo la biblioteca.

Verifica firmas completas y obsolescencia antes de escribir GML. Crea recursos mediante GameMaker o sus herramientas; conserva el trabajo existente. Cierra tareas con evidencia del comportamiento y entregas con las puertas del juego completo.

Un resultado histórico pertenece a sus entradas. Una prueba de una herramienta no acredita el juego; un build correcto no acredita arte, sonido, guardado o rendimiento. [Protocolo completo](<13 - Diseño y producción de videojuegos/29 - Desarrollo con IA - orquestación, crítica y evidencia.md>).

## Mantener el conocimiento al día

```bash
python _indice/actualizar.py
```

El mantenimiento deriva símbolos, regenera índices y comprueba documentación y skill. Puede compilar ejemplos en un proyecto desechable. Las pruebas dinámicas de publicación viven aparte: [contribuir](CONTRIBUTING.md).

LTS, Beta y GMRT tienen estados y fechas diferentes. Consulta [las novedades](<02 - Novedades 2026>) y las fuentes primarias antes de aplicar un cambio; la biblioteca no actualiza automáticamente tu motor.

## Fuentes y derechos

Para una API, manda el runtime que usas, contrastado con [el manual oficial](https://manual.gamemaker.io/). Las notas de versión explican cuándo cambió. Los ejemplos de terceros muestran práctica y conservan sus licencias.

Comprueba derechos de código, imágenes, audio y fuentes antes de distribuir un juego. [Licencias](LICENSE) · [Contenido excluido](PUBLICAR.md).
