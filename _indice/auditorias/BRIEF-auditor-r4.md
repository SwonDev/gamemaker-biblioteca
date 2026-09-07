# Brief del auditor · cuarta ronda (2026-09-07)

**El objetivo de esta ronda es distinto al de las anteriores.** Ya no basta con que la
información esté: tiene que estar de forma que **un agente de IA la ejecute sin equivocarse**.
La prueba que hay que pasar es esta:

> Un usuario le dice a una IA «hazme un juego con GameMaker». La IA carga la skill
> `gamemaker-biblioteca`. ¿Puede llevar el juego de la idea a la tienda **sin cometer ni un
> error**, sin inventarse nada y sin quedarse atascada?

Todo lo que impida eso es un hueco, aunque el tema «esté documentado».

## Qué es esto

`/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje` es una base de conocimiento en
español sobre GameMaker LTS 2026 (IDE 2026.0.0.16 · runtime GMS2 2026.0.0.23) con 256 documentos
propios, el manual oficial espejado completo en dos idiomas y 608 repositorios de GML real.

**No forman parte de la biblioteca y no se tocan ni se citan:** `Lumbre/` (juego personal) y
`GameMaker_Fuentes/` (almacén crudo de clones).

## Lo que ya se auditó — NO lo reabras sin evidencia nueva

Tres rondas anteriores dejaron sus informes en esta misma carpeta:

- **Ronda 2** (`audio.md`, `vfx.md`, `colisiones-movimiento-camara.md`, `combate-enemigos.md`,
  `feedback-ux.md`, `diseno-gdd.md`, `ingenieria.md`) — ~490 temas.
- **Ronda 3** (`r3-*.md`) — 909 temas en diez dominios, más `r3-generos-faltantes.md`.
- **Cierre de la ronda 3**: `r3-99-cierre.md`.

Cada uno trae una sección «Lo que comprobé y NO hacía falta». **Respétala.** Si crees que algo de
ahí está mal, tienes que traer evidencia nueva y decirlo explícitamente.

Tu valor está en encontrar lo que **ninguna de las tres rondas vio**, no en repasar lo hecho.

## Método (en este orden)

1. **Construye la lista canónica de tu encargo.** Mínimo 50 temas granulares, contrastados con
   fuentes reales (WebSearch/WebFetch: documentación oficial, foros del motor, GDC, repositorios).
   «Publicar en consola» no es un tema; «obtener el devkit de Nintendo y qué te exigen antes» sí.
2. **Comprueba cada tema contra el disco**, siempre:
   ```sh
   python3 _indice/buscar.py --todo "<concepto>"
   grep -rn "<término>" "04 - Recetas por género" "13 - Diseño y producción de videojuegos" ...
   ```
3. **Veredicto con evidencia**: ✅ cubierto (cita `archivo §sección`; sin cita no cuenta) ·
   🟡 parcial (di qué falta exactamente) · 🔴 falta (di dónde debería ir y por qué importa).
4. **Prueba de agente**: para los temas centrales de tu dominio, pregúntate si un agente que solo
   lea la biblioteca **sabría ejecutar el paso**, o solo sabría *hablar* de él. Documentación que
   describe pero no permite ejecutar es 🟡, no ✅.
5. **Redacta el encargo** para cada 🔴 y cada 🟡 grave: qué documento o sección, en qué archivo, con
   qué contenido y con qué símbolos verificados (`buscar.py`; si no aparece, **no existe**).

## Reglas duras

- **Nunca afirmes que existe una función de GML sin `buscar.py`.** Lo no verificado va con ⚠️.
- **Toda afirmación con fecha de caducidad va con su fecha de consulta**: versiones, precios,
  políticas de tienda, estado de un repositorio, requisitos de una plataforma.
- **No propongas duplicar.** Si el tema ya está, la propuesta es «enlazar desde X».
- Español con tildes y eñes. Identificadores de la API en inglés.
- Tabla densa, sin paja: el informe lo lee otro agente para trabajar.

## Salida

Un solo archivo: `_indice/auditorias/r4-<tu-dominio>.md`

```markdown
# Auditoría r4 · <Dominio>

> Fecha · N temas · X cubiertos · Y parciales · Z faltan

## Resumen ejecutivo
¿Podría un agente ejecutar esto de principio a fin leyendo solo la biblioteca? ¿Dónde se atasca?

## Tabla tema por tema
| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |

## Huecos por prioridad
### 🔴 Graves   ### 🟠 Medios   ### 🟡 Menores

## Encargo para el redactor
Lista numerada: documento/sección, archivo destino, contenido, símbolos verificados.

## Lo que comprobé y NO hacía falta
Para que nadie lo reabra.

## Lo que encontré desactualizado
Afirmaciones de la biblioteca que hoy ya no son ciertas, con la fuente y la fecha que lo prueba.
```
