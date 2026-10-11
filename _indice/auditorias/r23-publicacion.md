# r23 · Publicación e instalación desde GitHub

Fecha: **11-10-2026**. Paquete r48 publicado mediante push normal en `main`, commit
[`998f6f851b4b6a302e3f27d731f583d981afd048`](https://github.com/SwonDev/gamemaker-biblioteca/commit/998f6f851b4b6a302e3f27d731f583d981afd048).
Autor y committer usan la identidad pública `SwonDev` con correo noreply de GitHub.
La publicación sale del checkout público; no se publica la historia privada de la raíz.

## 1 · Clon e instalación real

Después del push se creó un clon nuevo desde la URL pública, con profundidad 1.
Su HEAD coincide con el publicado. En un entorno aislado **Python 3.10.21**, se ejecutó
la instalación de las dependencias fijadas, el instalador de la skill, la construcción
de índices y una consulta de símbolo. Todos los pasos terminaron con **0**.

| Comprobación | Resultado observado |
|---|---|
| Dependencias | `PyYAML==6.0.3` y `Pillow==12.2.0`, manifiesto del repositorio; entorno separado de los intérpretes globales |
| Destino explícito de instalación | **12** archivos, manifiesto SHA-256 idéntico al paquete del clon |
| Destino DSH configurable | `DSH_HOME` propio del fixture; **12** archivos idénticos, sin escribir en el home real |
| Índices y consulta | Fuente de API GMS2 **2026.0.0.23**, caché local seleccionada explícitamente; `gpu_get_blendequation_sepalpha` consultable |
| Derivados versionados | `git diff --exit-code`: **0** después de construir los índices |
| Material visual | Guía y **3** ilustraciones de la metodología idénticas entre clon, checkout público y biblioteca completa |

El [manifiesto de lectores](./r23-loaders-recibos.json) corresponde al mismo paquete.
Los detalles de [validación](./r23-validacion.md) y [HTTP/input](./r23-http-ejecucion.md)
conservan sus denominadores y límites. El [plan](./r23-plan-y-criterios.md) queda cubierto
por estas comprobaciones y la revisión independiente previa.

## 2 · Qué acredita este recibo

La reproducción verifica el paquete descargado de GitHub, la instalación y los derivados
ejercitados. El manual y el código de terceros opcionales no se reconstruyeron en el clon;
la cobertura completa del manual corresponde a la pasada separada de la biblioteca local.
Sin runtime disponible, la skill conserva su vía al manual oficial y declara la fuente
ausente; esta prueba usa una caché disponible, no demuestra instalar GameMaker desde cero.

No hubo conversación LLM, actualización de herramientas globales, ejecución de juegos
ni reanudación del proyecto fuente. Este recibo describe el commit indicado; su publicación
posterior añade únicamente el cierre documental, sin cambiar el paquete probado.
