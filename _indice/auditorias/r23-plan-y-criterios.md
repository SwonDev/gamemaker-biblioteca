# r23 · Investigación adicional e implementación r48

Fecha: **11-10-2026**. Encargo: investigar contenido actual que falte o pueda mejorarse,
evitar duplicados e implementarlo en la biblioteca y skill universales GameMaker.
La metodología, EmbeddingGemma 2, instalación multiharness y tres nuevas ilustraciones
ya incorporadas en r47 son la base; esta ronda no crea copias de esos procedimientos.

## 1 · Cobertura examinada y decisiones

| Área | Cobertura existente | Diferencia comprobada y acción |
|---|---|---|
| Spec-driven, organización, crítica, límites de recursos y evidencia | 13/29, 12/09, 13/10; paquete progresivo r47 | Conservar y reutilizar; no crear otra metodología |
| Semántica multimodal, recursos, contexto y RAG | 12/11, 13/29 §11.1; modelo/privacidad/reserva/medición | Conservar la integración existente; no reindexar proyectos pausados |
| API y búsqueda por versión | Runtime_Biblioteca, índice, fnames, skill | Corregir la inferencia absoluta de ausencia que aún quedaba en CLAUDE.md y COMO-BUSCAR |
| Versiones y herramientas | 02, 07/13 y trampas 12/09 | Contrastar notas y paquetes oficiales; actualizar GMRT 0.22, Beta R8/R9, CLI publicado 2.4.1; separar fuente/instalación/ejecución |
| Clientes HTTP | Liveops 04/52 y telemetría 13/01 §9.7 | Corregir progreso, códigos HTTP y confirmación de un volcado anterior; referencia transversal 12/12 |
| Entrada unificada | 01/12, hotplug, foco, mandos y acciones ya cubiertos | Preservar magnitud analógica en el ejemplo de movimiento; no duplicar gestión de mandos |
| Portabilidad y presentación | Recibos r19/r22, Método visual y README | Acotar las pruebas Windows históricas a sus herramientas/revisiones; conservar material visual existente |

La comparación HTTP incluyó las secciones de configuración remota y envío de telemetría,
eventos de fundamentos y catálogos de integraciones. El capítulo nuevo desarrolla los
contratos compartidos, mientras los ejemplos y sus correcciones permanecen en su disciplina.
La investigación de versiones está en [r23-investigacion-versiones.md](./r23-investigacion-versiones.md).

## 2 · Criterios de aceptación de esta ronda

1. Fuentes técnicas primarias actuales, fecha y rama; novedades publicadas separadas
   de planes y de correcciones que solo están en `main`.
2. Ninguna instalación/actualización global de CLI, modelos, runtimes o SDKs implícita.
   Cryalis sigue pausado; los tests usan proyectos temporales propios.
3. HTTP: progreso conserva el intento, ID ajeno no tiene efecto, códigos negativos/
   ausentes/no 2xx no acreditan éxito, JSON inválido no se aplica y una confirmación
   anterior no borra un volcado nuevo. Pruebas del GML documental y eventos reales.
4. Controles negativos para progreso, éxito HTTP demasiado amplio y borrado incondicional:
   cada uno debe causar un fallo del banco, sin cambiar las fuentes documentales.
5. Entrada: cero, inclinación 0.4, diagonal digital y vector analógico de longitud 0.5;
   extracción del fragmento real. No se atribuye prueba de hardware físico.
6. Paquete r48 coherente, referencias descubribles y fallback sin biblioteca completa;
   mantenimiento de enlaces, secciones, API, código, ortografía e índices en Python mínimo.
7. Revisión independiente de normas y requisitos; resolver hallazgos confirmados antes
   de publicar. Promoción a raíz con copias y comprobación de huellas; instalaciones completas.
8. Publicación desde historia pública autorizada, clon/archivos/skill comprobados;
   conservar WIP e historia privada de raíz y estado de pausa del juego.

## 3 · Qué evidencia no se atribuye

El servidor local no acredita TLS, CORS, backend remoto, tiendas, deduplicación del servidor
ni recuperación de varios lotes al reiniciar. El helper clasifica, no implementa esa cola.
Las novedades GMRT/Beta se contrastan documentalmente, sin instalar ni ejecutar sus demos.
Una muestra de pruebas y fuentes no certifica ausencia absoluta de errores en toda la
biblioteca. Cada resultado conserva su alcance y necesita refrescarse al cambiar sus entradas.
