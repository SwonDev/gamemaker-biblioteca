# Brief del auditor · tercera ronda (2026-09-06)

Auditas **un dominio del oficio de hacer videojuegos** contra esta biblioteca. No escribes
documentación: escribes el **informe** que usará después un redactor. Tu valor está en decir la
verdad sobre lo que falta, con evidencia, no en tranquilizar.

## Qué es esto

`/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje` es una base de conocimiento en
español sobre GameMaker LTS 2026 (IDE 2026.0.0.16 · runtime GMS2 2026.0.0.23), pensada para que
un agente de IA desarrolle **cualquier videojuego** con GameMaker sin inventarse nada.
245 documentos propios + el manual oficial espejado + 608 repos de GML real.

**No forman parte de la biblioteca y no se tocan ni se citan:** `Lumbre/` (juego personal del
usuario) y `GameMaker_Fuentes/` (almacén crudo de clones).

## Método (en este orden)

1. **Construye la lista canónica de tu dominio.** Qué temas domina un profesional de ese campo:
   sácalo de tu conocimiento del oficio y contrástalo con fuentes reales (WebSearch/WebFetch:
   GDC, Game Programming Patterns, Red Blob Games, el manual de GameMaker, foros del motor,
   libros de referencia del campo). **Mínimo 60 temas**, granulares y accionables — «cámara» no
   es un tema; «cámara con look-ahead por velocidad» sí.
2. **Comprueba cada tema contra el disco.** No vale la intuición:
   ```sh
   python3 _indice/buscar.py --todo "<concepto>"      # símbolos + docs + manual + código
   python3 _indice/buscar.py --texto "<concepto>"     # prosa de la biblioteca
   grep -rn "<término>" "04 - Recetas por género" "13 - Diseño y producción de videojuegos" ...
   ```
   Lee los índices `_INDICE-*.md` de cada carpeta y `_indice/MAPA.json` para saber qué hay.
3. **Veredicto por tema, con evidencia:**
   - ✅ **Cubierto** — cita `archivo.md §sección` donde está. Sin cita, no es cubierto.
   - 🟡 **Parcial** — se menciona pero no se puede implementar leyéndolo. Di qué falta exactamente.
   - 🔴 **Falta** — no está. Di dónde debería ir y por qué importa.
4. **Prioriza.** Un hueco es grave si un agente que intente hacer un juego se queda bloqueado o
   escribe algo mal. Es leve si es nicho o si se resuelve leyendo el manual.
5. **Redacta el encargo.** Para cada hueco 🔴 y los 🟡 graves: qué documento nuevo o qué sección
   ampliada, en qué archivo, con qué contenido y con qué símbolos de GML (verificados con
   `buscar.py`; si no aparece, **no existe** y no se propone).

## Reglas duras

- **Nunca afirmes que existe una función de GML sin `buscar.py`.** Lo no verificado va con ⚠️.
- **No propongas duplicar.** Si el tema ya está en otro documento, la propuesta es «enlazar desde
  X», no «escribir otra vez».
- Español con tildes y eñes. Los identificadores de la API, en inglés.
- Sé concreto y breve: tabla densa, sin paja. El informe lo lee otro agente para trabajar.

## Salida

Un solo archivo: `_indice/auditorias/r3-<tu-dominio>.md`

```markdown
# Auditoría r3 · <Dominio>

> Fecha · N temas evaluados · X cubiertos · Y parciales · Z faltan

## Resumen ejecutivo
Tres o cuatro frases: qué tan preparada está la biblioteca en este dominio y cuál es el hueco
que más duele.

## Tabla tema por tema
| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |

## Huecos por prioridad
### 🔴 Graves
### 🟠 Medios
### 🟡 Menores

## Encargo para el redactor
Lista numerada: documento/sección, archivo destino, contenido, símbolos verificados.

## Lo que comprobé y NO hacía falta
Temas que parecían huecos y resultaron cubiertos (evita que otro los reabra).
```
