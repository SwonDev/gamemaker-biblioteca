# Contribuir a la biblioteca

Gracias por ayudar a que GameMaker y GML sean más accesibles en español.

## Proponer una mejora

[Abre un issue](https://github.com/SwonDev/gamemaker-biblioteca/issues) para un error,
una laguna o una mejora del método. Incluye la ruta, el requisito y una fuente primaria.
Para fallos de herramientas: sistema, versiones, comando, salida y un caso mínimo propio.
Retira rutas personales, credenciales y contenido privado antes de enviarlo.

## Cambiar documentación o herramientas

Busca lo existente, lee [AGENTS.md](AGENTS.md) y conserva las fuentes y licencias.
La prosa va en español; los símbolos de la API conservan su nombre real. Evita
recuentos escritos a mano cuando se puedan derivar del índice.

Prepara el entorno de [instalación](INSTALACION.md). Para cambios de herramientas,
reproduce primero el fallo con un caso mínimo y añade una regresión en la frontera
que fallaba. Comprueba el paquete completo:

```bash
python _indice/pruebas/probar-instalacion.py
python _indice/pruebas/probar-sincronizacion.py
python _indice/actualizar.py
```

El mantenimiento usa el runtime instalado y puede compilar ejemplos en un proyecto
desechable. No ejecutes proyectos personales o pausados como parte de estas pruebas.

## Antes de publicar

Con GameMaker disponible, ejecuta también:

```bash
bash _indice/validar-compilacion.sh
bash _indice/validar-ejecucion.sh
bash _indice/verificar-trampas.sh
```

Conserva salida y estado de cada puerta. Un fallo o un caso omitido se declara.
Revisa el conjunto exacto de archivos y **todos los commits salientes**: un dato borrado
en la punta sigue presente si se publica en un commit anterior. Conserva avisos legales;
no redistribuyas manuales, código o assets ajenos fuera de su licencia.

El README debe funcionar en móvil y escritorio, claro y oscuro, con enlaces válidos
y texto alternativo. No presentes ilustraciones como capturas o la compilación como
certificación de calidad de un juego.
