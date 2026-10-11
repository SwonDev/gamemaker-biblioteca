# r22 · Alcance y criterios de la revisión r47

Encargo: profundizar en la biblioteca y la skill para cualquier proyecto GameMaker,
mejorar el README y sus iconos propios, y publicar la actualización autorizada.
La revisión parte de la publicación r46 `11cee593d313a83013faa559a54425a47468861d`.

## 1. Resultado requerido

1. Conservar el método universal de especificación, tareas verticales, implementación,
   revisión y aceptación, con router de skills y EmbeddingGemma 2 opcional y verificable.
2. Detectar y corregir lagunas demostrables en documentación y herramientas; toda firma
   nueva debe tener fuente primaria aplicable y prueba de compilación cuando corresponda.
3. Permitir consumir la skill con solo su paquete, sin rutas personales obligatorias,
   en Bash o PowerShell, con fallback oficial y estados explícitos de verificación.
4. Instalar el paquete completo en destinos nativos de Pi, OMP, MiniMax Code, DSH,
   Hermes y Gentle Shell; conservar destinos existentes y sus copias de seguridad.
   No cambiar modelos, proveedores ni credenciales. DSH significa DeepSeek Harness.
5. Mejorar la lectura del README con iconos originales y comprobar el resultado visual.
   Ampliación solicitada: tres ilustraciones nuevas explican la aportación de la skill,
   la relación especificación/tareas/pruebas y la selección de contexto semántico;
   una guía visual conserva sus explicaciones y alternativas como texto.
6. Publicar el resultado verificado desde la historia pública y promoverlo a la biblioteca
   local sin descartar trabajo legítimo ni reanudar el proyecto fuente pausado.

## 2. Puertas de aceptación

- Regresiones negativas y positivas para selección de runtime, alcance e instalación;
  ausencia de fuentes verificables produce error, nunca un índice vacío presentado como válido.
- Mantenimiento completo en verde; compilación de los bloques GML editados y contratos
  reutilizables. Las pruebas anteriores solo se reutilizan cuando el código no ha cambiado.
- Cargadores reales de los seis harnesses nuevos leen metadatos, cuerpo y referencias
  del paquete en fixtures aislados. Distinguir instalación, descubrimiento y uso por un modelo.
- Prueba fresca de la skill sin biblioteca completa ni CLI; registrar lo leído y sus límites.
- Sondeos PowerShell ejecutados en los tres estados de disponibilidad, indicando plataforma.
- Revisión independiente de estándares y alcance, sin autoatribuir certificación universal.
- README sin imágenes rotas ni desbordamiento en escritorio y móvil, con revisión de píxeles.
- Clon público limpio con instalación reproducible; origen remoto y promoción local verificados.

## 3. Límites del contrato

La revisión combina investigación oficial, lectura de implementaciones y casos ejecutados;
no demuestra ausencia absoluta de errores futuros. No ejecuta un LLM para validar el parser
de una skill, ni certifica Windows/Linux a partir de pruebas nativas realizadas en macOS.
Los servicios Cloud requieren cuentas y entornos reales: sus límites se declaran en la receta.
No se incluye código privado, sesiones, modelos, claves ni material comercial extraído.
