# Auditoría r3 · Simulación, economía y sistemas de juego

> Fecha 2026-09-06 · 101 temas evaluados · 33 cubiertos · 38 parciales · 30 faltan

**Excluidos del barrido:** `Lumbre/`, `GameMaker_Fuentes/`. Todo símbolo de GML citado se verificó
con `python3 _indice/buscar.py <símbolo>` contra el runtime `2026.0.0.23`; lo no verificado se
marca con ⚠️.

---

## Resumen ejecutivo

La biblioteca domina la **teoría de simulación y el motor genérico**: vocabulario de economía
(Pool/Fuente/Sumidero/Convertidor/Intercambiador), curvas de crecimiento con sus cinco fórmulas,
Utility AI genérico, árbol de tecnología por grafo con validación de ciclos, paso fijo con
acumulador, spatial hash, tick escalonado y guardado versionado con migraciones — todo con código
GML real, verificado y listo para copiar. Donde se rompe sistemáticamente es en la **capa de
ensamblaje entre sistemas** y en un **género entero sin receta**: no existe ningún documento de
*colony sim / base builder con trabajadores autónomos* (RimWorld, Dwarf Fortress, Oxygen Not
Included), así que faltan a la vez el job system (cola de tareas + asignación de trabajadores),
las rutinas/horarios de NPC, la integridad estructural, las redes de energía/fluidos y la
simulación fuera de pantalla — seis piezas que se necesitan juntas y que hoy no se pueden montar
leyendo la biblioteca. El segundo hueco más caro es la **economía como sistema vivo**: hay teoría
excelente (por qué se infla, qué es un sumidero) pero cero código de precio dinámico, tienda NPC
con margen, o mercado entre jugadores. El tercero es la **granja como bucle completo**: el
crecimiento por fases y el calendario están resueltos, pero falta la propia función de
**cosechar** y todo lo de ganado — sin eso, un juego de granja no cierra su bucle central.

| Estado | Nº | % |
|---|---|---|
| ✅ `CUBIERTO` | 33 | 33 % |
| 🟡 `PARCIAL` | 38 | 38 % |
| 🔴 `FALTA` | 30 | 30 % |

---

## Tabla tema por tema

Rutas relativas a la raíz de la biblioteca.

### A · Inventario

| # | Tema | Veredicto | Evidencia (archivo §sección) | Qué falta |
|---|---|---|---|---|
| 1 | Rejilla vs lista: modelo de datos | 🟡 | `01/05 §10` «Guía de decisión: ¿qué uso?»; `13/05 §e` inventario en cuadrícula como array plano (`_i div _columnas`) | Sin comparación centrada en inventario (espacial con ancho/alto vs. lista de pilas); hay que extrapolar la guía genérica |
| 2 | Apilado de objetos (stack, split, merge) | 🟡 | `04/04 §5.2 Inventory.add()` hace merge en pila existente; `04/09 §4.2` «madera apila 99» | Sin tope de tamaño de pila aplicado en código, sin mecánica de *split* |
| 3 | Peso y capacidad de carga | 🔴 | `04/09 §4.2` «Peso (opcional...)» — única mención, sin campo ni fórmula | Todo: campo `peso` en ítems, capacidad máxima, penalización por sobrepeso |
| 4 | Equipamiento y slots | ✅ | `04/04 §5.2 Equipment()` — `weapon/armor/accessory`, `equip()` valida el slot declarado y recalcula stats | Restricciones avanzadas (dos manos, por clase) — extensión razonable, no vacío |
| 5 | Contenedores externos (cofres, baúles) | 🔴 | `04/09 §2` lista `objStorageChest` en la jerarquía, nunca implementado; `04/06 §4.4` cofre = booleano sin inventario propio | Todo: objeto contenedor con `Inventory` propia + UI de dos paneles |
| 6 | Arrastrar y soltar (drag and drop) | ✅ | `13/05 §e` máquina de 3 estados (nada→cogido→soltado), `inventario_coger()`/`inventario_soltar()`, recupera si destino inválido | Solo dentro de UN inventario; entre dos (jugador↔cofre) depende del hueco 5 |
| 7 | Ordenación, filtrado y búsqueda | 🟡 | `08/14 - Arrays.md` `array_sort`/`array_filter`/`array_map`/`array_reduce` documentados y verificados | Ladrillos genéricos sin receta anclada a inventario (ordenar por rareza, filtrar por categoría) |
| 8 | Tooltips de objeto | 🟡 | `13/05 §d` tooltip genérico con posicionamiento seguro y retardo, `pista_dibujar()` | Presentación resuelta, contenido no: sin stats/comparación/color por rareza de un ítem real |
| 9 | Persistencia de inventario | ✅ | `04/04 §5.2 Inventory.serialize()/deserialize()`; `04/09 §6 survival_save()` con `json_stringify` | — |
| 10 | Inventario tipo Tetris (formas irregulares) | 🔴 | — (0 resultados; «Tetris» solo aparece para la bolsa de 7 en `13/13`) | Todo: dimensión por ítem, colocación/rotación en rejilla, solape |

### B · Objetos y datos

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 11 | Definición de ítem como dato (JSON/struct) | ✅ | `04/04 §5.3` `datafiles/items.json` con `id/type/stackable/slot/bonuses` | — |
| 12 | Base de datos maestra de ítems por id | ✅ | `04/04 §5.3` `items_load()`/`item_get_def()`; mismo patrón en `13/06 §3.8` (Type Object, enemigos) | — |
| 13 | Herencia de plantillas / arquetipos de ítem | 🟡 | `01/04 §4.3` herencia de constructores con `:` (genérica, verificada) | Nunca aplicada a ítems: `items.json` es catálogo plano sin `hereda_de` |
| 14 | Identificadores estables (no índice de array) | ✅ | `04/04 §4.3` «Las claves son IDs de texto, no índices numéricos» — regla explícita y seguida en todo el corpus | — |
| 15 | Carga externa de datos para modding | ✅ | `04/43` completo: manifiesto, fusión segura sobre `variable_clone`, sandbox, mod.io | — |
| 16 | Generación aleatoria de propiedades (rareza, afijos) | 🟡 | `04/05 §5.7 LootTable` (selección ponderada por rareza) | Falta tirar **afijos/stats** sobre un ítem base ya elegido (estilo Diablo) |
| 17 | Serialización de instancia con estado propio | 🟡 | `04/09 §6 SurvivalState` (durabilidad de herramienta equipada); `04/34 §5.1 WeaponAmmoState` | Ambos son estado por-portador, no por-instancia-en-pila; `Inventory` agrupa por cantidad, incompatible con "dos espadas con distinta durabilidad"; «encantamiento» no existe en el corpus |
| 18 | Localización de textos de ítem | 🟡 | `04/21 §1-2` sistema `txt(clave)` genérico y sólido | `items.json` de `04/04` usa texto literal en `name/description`, nunca conectado a `txt()` |

### C · Crafting

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 19 | Recetas ingredientes → resultado | ✅ | `04/09 §5.1 Recipe()` con `ingredientes/producto/tiempo`, `puede_craftear()`/`craftear()` separados | — |
| 20 | Árbol/grafo de dependencias de recetas | 🟡 | Dependencia implícita por clave compartida (`cuerda`→`cofre`); técnica de grafo con ciclos existe en `13/16 §3.2` pero para skill tree | Trasplantar Kahn/BFS de `13/16` a recetas; hoy no hay validación ni visualización |
| 21 | Descubrimiento de recetas (unlock) | 🟡 | `04/09 §8` «blueprints» — una línea, sin diseño | `recipes_init()` carga TODAS las recetas sin filtro; falta `recetas_desbloqueadas`, UI, persistencia |
| 22 | Estaciones de crafteo | 🟡 | `04/09 §4.3/§5.1` campo `estacion` existe en `Recipe` | `craftear()`/`puede_craftear()` **nunca comprueban** proximidad a `objCraftingStation`; el objeto no tiene código |
| 23 | Tiempo de fabricación y colas | 🟡 | `04/09 §5.1` campo `_tiempo` declarado; `04/13 §5.3` cola real no-instantánea (`tiempo_restante`) para producción de unidades | El crafteo de ítems (09) es instantáneo pese a declarar tiempo; hay que conectarlo a la cola que ya existe en 13 |
| 24 | Crafteo por lotes / cola con cancelación | 🔴 | — | `cola_cancelar()` con reembolso, encolar N repeticiones de una vez |
| 25 | Subproductos, desperdicio, fallos | 🔴 | — | Probabilidad de fallo, pérdida parcial, subproductos opcionales |

### D · Economía

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 26 | Oferta y demanda dinámica | 🔴 | `04/44 §2.4.2` pool compartido de tienda (afecta disponibilidad, no precio) | Todo: precio que reacciona a stock/consumo |
| 27 | Precios dinámicos y elasticidad | 🔴 | — | Curva de demanda, coeficiente de elasticidad |
| 28 | Sumideros y fuentes de moneda | ✅ | `13/01 §4.1` vocabulario Pool/Fuente/Sumidero; `04/08 §6 TDState.ganar()/.gastar()`; `04/44 §2.4.3` | — |
| 29 | Inflación y control de masa monetaria | 🟡 | `13/01 §4.3` regla + método de diagnóstico por telemetría (forma de la curva) | Diagnóstico sí, política de control activa (banco central, degradación) no |
| 30 | Balance global (ratio faucet/sink) | 🟡 | `13/01 §4.2` realimentación positiva/negativa; `13/21 §2.4` Monte Carlo por percentiles (centrado en combate) | Sin fórmula/umbral cuantitativo de faucet-vs-sink aplicado a economía |
| 31 | Comercio con NPC (tienda) | 🟡 | `04/08 §5.2` margen real `valor_venta = coste*0.7`; `04/04 §8` «Tienda» solo idea de una línea | Sin `objNPCMerchant` con stock propio y spread compra/venta |
| 32 | Mercado entre jugadores / subasta | 🔴 | `13/20 §1.4` «Intercambiador: mercado entre jugadores, si existe» — nota de una línea | Todo: listado, pujas/precio fijo, comisión, sincronía |
| 33 | Monedas múltiples (dura/blanda) | ✅ | `13/16 §2.6 moneda_transferir_a_meta()` (un solo sentido); `13/20 §1.4` dos *pools* + patrón oscuro «premium opaca» | — |
| 34 | Regateo / negociación de precio | 🔴 | — | Todo |
| 35 | Fricción económica (impuestos, comisiones) | 🔴 | `13/11 §9.5` es fiscalidad real del desarrollador (Steamworks), no mecánica de juego | Todo: impuesto de venta, comisión de mercado, degradación de saldo |

### E · Recursos y producción

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 36 | Cadenas de producción (edificios encadenados) | 🟡 | `13/01 §4.1` vocabulario Convertidor; `13/21 §3.4 convertidor_ejecutar()` (un solo paso, probado) | Sin encadenado temporal output→input entre varias estaciones |
| 37 | Logística: cintas/tuberías de transporte | 🔴 | — (0 resultados reales; "conveyor" solo aparece en géneros ajenos) | Todo: segmentos con dirección/velocidad, inserción/extracción |
| 38 | Almacenamiento con límite y desbordamiento | 🟡 | `13/21 §2.1` vocabulario Machinations «Pool + Capacidad + Overflow»; `04/13 §5.3 poblacion_max` | Vocabulario sin traducir a GML; recursos de RTS no tienen tope ni política de overflow |
| 39 | Cuellos de botella y escasez en cadenas | 🔴 | `convertidor_ejecutar()` solo devuelve `false` sin producir | Sin detección/comunicación de qué eslabón está parado |
| 40 | Nodos de extracción (agotables/renovables) | 🟡 | `04/09 §4.1/§5.2` nodo con `respawn_frames` declarado | Campo **nunca leído** en `romper()` — stub sin implementar, riesgo de asumir que ya funciona |
| 41 | Cálculo de rendimiento/throughput | 🔴 | — | Fórmula de unidades/seg de una cadena, eslabón limitante |

### F · Agricultura y ciclos

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 42 | Crecimiento de cultivos por fases | ✅ | `04/45 §5.3` `EstadoCultivo` enum + `cultivo_avanzar_dia()` sobre array plano de celdas | Falta solo el `draw` que mapea etapa→frame (derivable, no escrito) |
| 43 | Riego y calidad/fertilidad del suelo | 🟡 | `04/45 §5.3` `regada` booleano por día | Sin fertilidad/calidad de suelo, sin abono ni degradación por monocultivo |
| 44 | Estacionalidad (qué crece cuándo) | 🟡 | `04/45 §5.2` calendario de 4 estaciones × 28 días | `tipos_semilla` no tiene campo de estación válida; `cultivo_plantar()` no lo comprueba |
| 45 | Cosecha (yield, herramienta, ventana) | 🔴 | `04/45 §5.3` solo llega a `EstadoCultivo.MADURA` | No existe `cosechar()`: sin yield al inventario, sin herramienta, sin ventana antes de pudrirse |
| 46 | Ganado (alimentación, producción, reproducción) | 🔴 | — (0 resultados de animales de granja) | Todo — `Needs` y señal `nuevo_dia` de 45 son la base reutilizable, no adaptada |
| 47 | Enfermedades de cultivo y rotación | 🔴 | — | Todo; el struct de celda no guarda histórico de qué se plantó antes |

### G · Supervivencia

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 48 | Hambre y sed con penalización escalonada | ✅ | `04/09 §5.0 Needs.multiplicador_velocidad()/daño_por_frame()` con umbrales | — |
| 49 | Temperatura y exposición (ropa, refugio) | 🟡 | `04/09 §5.0/§5.5` `Needs.update()` recibe `_temperatura` externa | Tabla menciona ropa/refugio como mitigantes, pero no hay struct de abrigo/techo que module el cálculo |
| 50 | Fatiga y sueño | 🟡 | `04/09 §5.0` `tasa_sueño`, penalización de velocidad bajo 15 | Sin rama de penalización a `sueño<=0` (visión/alucinaciones solo en tabla), sin acción «dormir en cama» |
| 51 | Salud a largo plazo, enfermedad, contagio | 🔴 | `04/32 §4.4-4.5` motor de efectos de estado (veneno/quemadura) es la base transferible, orientada a combate | Nada de enfermedad persistente ni contagio por proximidad |
| 52 | Degradación/rotura de objetos (durabilidad) | ✅ | `04/09 §6 SurvivalState.usar_herramienta()` — resta durabilidad, retira el ítem al llegar a 0 | — |
| 53 | Perecederos: caducidad de alimentos | 🔴 | — | Todo: marca de tiempo por ítem, conservación, penalización |
| 54 | Priorización de necesidades | 🟡 | `04/09 §5.0 daño_por_frame()` es **acumulativo** (todas suman), `alguna_critica()` sin decir cuál | Sin ranking de urgencia para, p. ej., decidir qué icono parpadea primero |

### H · Construcción de base

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 55 | Rejilla de colocación (snapping) | ✅ | `04/09 §5.3` ghost preview con `div CELL`; `13/13 §7.2 snap()` en `scr_math_util.gml` | Sin ejemplo isométrico aplicado a construcción |
| 56 | Validación de colocación (colisión, terreno) | 🟡 | `04/09 §4.5/§5.3` `ghost_valido` llama a `celda_construible()`/`punto_en_rango()` | **Ambas funciones se llaman pero nunca se definen**; `ghost_valido` tampoco consulta `objWorldGrid.ocupada()` pese a prometer «sin solaparse» — trampa real si se copia tal cual |
| 57 | Soporte estructural / integridad | 🔴 | — (0 resultados) | Todo: propagación de soporte, colapso en cascada |
| 58 | Detección de habitaciones cerradas | 🟡 | `04/05 §5.4 dungeon_flood_fill()` BFS de 4-vecinos, pero enmarcado como validación de mazmorra generada una vez | Sin ID de zona por región, sin recálculo incremental, sin noción interior/exterior |
| 59 | Redes de energía (power grid) | 🔴 | `04/13 §5.3` `energia` es solo un contador global plano, sin red | Todo: nodos generador/consumidor, grafo de conexión, prioridad de reparto |
| 60 | Redes de fluidos (agua/gas por tuberías) | 🟡 | `13/08 §10` autómata celular de líquido en rejilla abierta (presión y nivel gratis) | Es simulación de líquido tipo *falling sand*, no red de tuberías dirigida con válvulas/bombas; gas no existe |
| 61 | Demolición y recuperación de materiales | 🔴 | `04/09` `WorldGrid.liberar()` existe pero **nunca se invoca** desde ningún sitio | Acción de demolición en sí + devolución parcial de materiales |
| 62 | Rotación y auto-tiling de piezas | 🟡 | `13/02 §3.3` bitmask de vecinos para autotile de **tiles de nivel** | Nunca aplicado a piezas de construcción; sin rotación de pieza antes de colocar |

### I · NPC y sociedad

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 63 | Rutinas y horarios (schedules) | 🟡 | `04/45 §5.2` calendario + reloj día/noche como andamiaje | Ningún NPC con rutina por hora en toda la biblioteca |
| 64 | Sistema de necesidades tipo Sims | 🟡 | `04/09 §5.0 Needs()` motor de decaimiento reutilizable (hambre/sed/calor/sueño/cordura) | Cableado a supervivencia del jugador, no a higiene/ocio/social de una población de NPCs |
| 65 | Utility AI para selección de acción | ✅ | `04/31 §8` motor genérico completo (`OpcionUtil`, `elegir_por_utilidad`, curvas, inercia anti-oscilación), cita explícita a *The Sims* | Ejemplo dado es combate; adaptar curvas a necesidades es trivial pero no está hecho |
| 66 | Trabajos y roles asignables | 🔴 | `04/13` solo `objUnitWorker` de RTS, sin profesiones/turnos | Todo |
| 67 | Cola de tareas y asignación de trabajadores (job system) | 🔴 | `04/13 §4.5/§5.3` es cola de **producción** por edificio, no cola de tareas para trabajadores | Todo el patrón: cola global con prioridad, reserva de tarea, coste de desplazamiento — **el hueco de género más grande detectado** |
| 68 | Pathfinding multi-agente en base cambiante | ✅ | `04/38 §2.1-2.2` flow field con recálculo al colocar/destruir obstáculo | Invalidación por región (mapas muy grandes) mencionada, no desarrollada |
| 69 | Facciones: relaciones entre grupos | 🔴 | `04/31 §8` solo enlaza a IA de facción única (recolectar/defender/atacar/expandir), no diplomacia | Todo: matriz de relación, estados, transiciones |
| 70 | Reputación del jugador | 🔴 | «reputación» solo como ejemplo suelto en `13/01`, sin sistema | Todo |
| 71 | Relaciones interpersonales NPC↔NPC | 🔴 | `04/45 §5.4` es afinidad **jugador→NPC** (regalos/corazones), no NPC↔NPC | Todo el eje NPC-NPC: memoria, progresión de amistad/romance |
| 72 | Diálogo condicionado por afinidad | ✅ | `04/10 §4.4/§5.2` elecciones con `condicion: afinidad_ana>=3`; `13/12 §6.4` barks por reglas de especificidad | Barks no traen ejemplo cableado con afinidad, pero el mecanismo lo admite sin tocar el motor |

### J · Tiempo del mundo

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 73 | Reloj de juego (horas/minutos) | 🟡 | `04/09 §5.5` reloj 0..1 con `duracion_dia`; `06/scr_tiempo.gml` con `time_scale` | Ninguno representa HH:MM ni convierte para HUD |
| 74 | Calendario (días/estaciones/año) | ✅ | `04/45 §5.2` `dia_actual`, `estacion_indice`, señales `nuevo_dia`/`cambio_estacion` | Sin contador de «año» explícito (trivial de añadir) |
| 75 | Ciclo día/noche | ✅ | `04/09 §5.5`; `04/24 §6` rampa de color con paradas horarias | — |
| 76 | Eventos programados (festivales) | 🔴 | «festivales» solo mencionado una vez como contenido, sin sistema | Tabla de eventos fijos + comprobación en el oyente de `nuevo_dia` |
| 77 | Control de velocidad de simulación (pausa, x2, x4) | 🟡 | `04/41 §3.1.9` pausa (`time_scale=0` vs `instance_deactivate_all`); `04/27 §7` multiplicador acotado a 0.5-1.0 | Sin x2/x4 sostenido probado; `04/13` (el género que más lo necesita) no lo menciona |
| 78 | Simulación fuera de pantalla (offscreen) | 🔴 | El único patrón relacionado (`instance_deactivate_region`) hace lo **contrario**: apaga, no simula abstracto | Sin patrón de «simulación barata mientras la zona no está cargada» para NPCs/edificios |
| 79 | Progreso offline | ✅ | `04/45 §6.4 progreso_offline_aplicar()` con `date_second_span`, tope de horas | — |

### K · Clima y entorno

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 80 | Sistema de clima (lluvia/nieve/tormenta) | 🟡 | `04/39 §3.5-3.6` lluvia y nieve como VFX on/off manual | Sin tormenta, sin probabilidad ligada al calendario, sin máquina de estados de clima |
| 81 | Efecto de clima sobre cultivos/NPC/economía | 🔴 | `04/09 §5.0` `mult_clima` declarado pero **nunca asignado** por ningún sistema de clima | Todo el acoplamiento: lluvia→riego automático, clima→ánimo NPC, clima→precios |

### L · Simulación

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 82 | Paso fijo vs variable | ✅ | `13/08 §1.3` y `13/06 §3.9` acumulador con techo `MAX_PASOS_POR_FRAME` e interpolación `alfa` | — |
| 83 | LOD de simulación por distancia | 🟡 | `04/31 §12` «tick muy lento (cada 2s)» como alternativa a desactivar | Falta gradiente de bandas (cerca/media/lejos), solo binario activo/desactivado |
| 84 | Actualización por lotes/escalonada | ✅ | `04/31 §12` `grupo_ia = irandom(5)`, `(current_time div 100) mod 6 == grupo_ia` | Advertencia a respetar: separar decidir (escalonado) de moverse (cada frame) |
| 85 | Entidades dormidas y activación por proximidad | ✅ | `04/09 §5.4` chunking por radio; `instance_activate/deactivate_region` | Aviso: instancia desactivada no existe para `instance_nearest`/conteos globales |
| 86 | Simular miles de entidades sin caída de FPS | ✅ | `13/08 §4` spatial hash completo (`rejilla_nueva/insertar/vecinos`); `04/44 §1.4.5` pooling+culling+distancia al cuadrado | — |
| 87 | Determinismo de la simulación | ✅ | `13/13 §5.2` aviso de semilla no-portable entre plataformas; `04/44 §2.4.5` combate con semilla propia | Lockstep de red solo enunciado en tabla (`04/14 §2.1`), sin código |
| 88 | Perfil y presupuesto de tiempo por frame | ✅ | `13/08 §14` presupuesto de 16 666 µs a 60 fps; `01/15 §6` Debug Overlay modo *Stacked* | — |
| 89 | Job systems y colas de prioridad genéricas | 🟡 | `08/13` familia `ds_priority_*` completa, en uso real para A*/GOAP | Sin job system (cola de tareas + varios trabajadores); GameMaker es de un solo hilo lógico |
| 90 | Asignación óptima de trabajadores a tareas | 🔴 | — (0 resultados de «asignar», «bidding», «reservar recurso») | Todo el emparejamiento N-trabajadores↔M-tareas |
| 91 | Planificación de producción / secuenciación | 🟡 | `04/13 §5.3` cola FIFO por edificio, cobro al encolar | Sin secuenciación óptima entre varias colas (job-shop scheduling) |

### M · Colas y planificación

*(cubiertos junto a L; ver 89-91 arriba — la categoría comparte los mismos tres temas)*

### N · Progresión y meta

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 92 | Árboles de tecnología/habilidades | ✅ | `13/16 §3.1-3.2` grafo JSON→structs, Kahn/BFS para ciclos y alcanzabilidad — el documento más completo de los 101 temas | — |
| 93 | Desbloqueos progresivos | ✅ | `13/01 §5.3 contenido_permitido()`; reutilizado por `13/16 §3.4` para Keystones | — |
| 94 | Prestigio / New Game+ | ✅ | `13/16 §2.6 moneda_transferir_a_meta()`; reutilizado literalmente en `04/45 §6.4` | — |
| 95 | Matemáticas idle: coste exponencial | ✅ | `13/13 §8.1 progresion_exponencial()`; aplicada en `04/45 §6.2` | — |
| 96 | Curvas de coste/retorno (diminishing returns) | ✅ | `13/13 §8.1-8.3` cinco fórmulas con función GML cada una y tabla comparativa a 10 niveles | — |
| 97 | Números grandes en GML (límites, notación) | ✅ | `13/13 §11.4` límite `2^53`/`int64` hasta `9.2e18`; `04/45 §6.3 numero_abreviado()` mantisa+sufijo | — |
| 98 | Progreso offline con rendimientos decrecientes | 🟡 | `04/45 §6.4` progreso offline lineal con **tope duro** (100%→0% de golpe) | Sin curva de decaimiento suave; la logarítmica de `13/13 §8` no está conectada aquí |
| 99 | Escalado de dificultad ligado a progresión | ✅ | `04/44 §1.4.2 next_wave()` (verificado contra Survivor Template oficial); `13/13 §8.3` sigmoide para dificultad por oleada | — |

### O · Guardado

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 100 | Serialización de mundo simulado grande | 🟡 | `04/09 §5.4 ChunkData.serialize()/deserialize()` guarda solo el diff por chunk | Nunca conectado a `save_game()`/ficheros — vive solo en memoria |
| 101 | Guardado incremental/particionado y versión | 🟡 | Versión/migración: ✅ excelente en `13/06 §3.10` + `06/scr_save_load.gml` (escritura atómica, migraciones acumulativas). Particionado: falta | El particionado por chunk (tema 100) nunca se conecta con la infraestructura de guardado versionado |

---

## Huecos por prioridad

### 🔴 Graves

Bloquean a un agente que intente el subgénero correspondiente, o le hacen escribir algo
incorrecto si copia el código tal cual.

1. **Colony sim / base builder con trabajadores autónomos no existe como género** (temas
   **57, 59, 61, 63, 64, 66, 67, 69, 70, 71, 78, 90**). RimWorld/Dwarf Fortress/Oxygen Not
   Included agrupan seis piezas que faltan a la vez: job system con cola de prioridad y
   asignación de trabajadores (67, 90 — «el hueco de género más grande» según dos auditores
   independientes), rutinas/horarios de NPC (63), necesidades tipo Sims adaptadas a población
   (64), integridad estructural (57), redes de energía (59) y simulación fuera de pantalla (78).
   La biblioteca ya tiene los primitivos de bajo nivel (Utility AI genérico de `04/31 §8`,
   `WorldGrid`, flood fill de `04/05 §5.4`, señales de `04/16`) pero el ensamblaje no está
   documentado en ningún sitio.
2. **La granja no cierra su bucle**: falta la función de **cosechar** (45) y todo el sistema de
   **ganado** (46). Sin `cosechar()`, un agente que implemente `04/45 §5.3` se queda con
   cultivos que llegan a `MADURA` y no pasa nada más — el 50 % del género (Stardew Valley vive
   de cultivos + animales) no tiene ni una línea de animales.
3. **Logística de producción automática no existe** (37): ningún patrón de cinta transportadora
   o tubería de transporte. Bloquea por completo cualquier factory-builder (Factorio-like).
4. **Redes de energía** (59): el único «recurso energía» del corpus es un contador plano de RTS
   sin red espacial — bloquea Oxygen Not Included / Satisfactory / Factorio.
5. **Contenedores externos** (5): `objStorageChest` está nombrado pero nunca implementado —
   bloquea cualquier survival/RPG que necesite un cofre con inventario propio.
6. **`04/09` §5.3 promete «sin solaparse» y no lo cumple** (56): `ghost_valido` llama a
   `celda_construible()`/`punto_en_rango()` que no existen en el documento, y nunca consulta
   `objWorldGrid.ocupada()`. Un agente que copie el snippet tal cual permitirá construcciones
   superpuestas — es el ejemplo exacto de «escribe algo mal» que el método pide vigilar.

### 🟠 Medios

Importantes para un subgénero concreto, pero no bloquean *cualquier* juego de simulación.

- **Economía como sistema vivo** (26, 27, 30, 32, 35): teoría excelente, cero código de precio
  dinámico, mercado entre jugadores o fricción económica dentro del juego.
- **Peso/capacidad de carga** (3) y **perecederos** (53): mencionados como «opcional» en una
  línea, sin campo ni fórmula — comunes en survival serio.
- **Salud a largo plazo / enfermedad / contagio** (51): el motor de efectos de estado de combate
  (`04/32`) es la base transferible, pero no está adaptado.
- **Detección de habitaciones como zona viva** (58): el flood fill existe pero enmarcado para
  mazmorras generadas una vez, no para recalcular oxígeno/temperatura por habitación en tiempo
  real.
- **Redes de fluidos dirigidas** (60): hay simulación de líquido en rejilla abierta, pero no
  tuberías con válvulas/bombas conectando depósito↔máquina.
- **Cuellos de botella y throughput en cadenas de producción** (39, 41): sin diagnóstico ni
  fórmula.
- **Nodos de recurso renovables** (40): el campo `respawn_frames` es un *stub* que nunca se lee
  — riesgo real de que un agente asuma que ya funciona.
- **Control de velocidad de simulación sostenido x2/x4** (77): existe pausa y un multiplicador
  acotado a 0.5-1.0 para accesibilidad, pero nada probado para acelerar un tycoon.
- **Progreso offline sin curva de rendimientos decrecientes** (98) y **guardado particionado de
  mundo grande** (100, 101): cada pieza existe por separado y nunca se conectan entre sí.

### 🟡 Menores

Nicho, o se resuelve con una extensión trivial de algo que ya existe.

- Inventario tipo Tetris (10), crafteo por lotes con cancelación (24), subproductos/fallos de
  fabricación (25), regateo (34), enfermedades de cultivo/rotación (47), eventos programados de
  calendario (76 — trivial sobre la señal `nuevo_dia` que ya existe), efecto del clima sobre
  cultivos/NPC/economía (81 — el gancho `mult_clima` ya está, solo falta conectarlo), LOD de
  simulación gradual en vez de binario (83).

---

## Encargo para el redactor

Documento nuevo recomendado: **`04 - Recetas por género/46 - Colony sim y base builder con
trabajadores.md`** (o ampliar `04/45` con una sexta sección «Colony sim»). Justificación: es el
único hueco que agrupa 12 de los 30 temas 🔴/🟡-graves detectados, y ningún documento existente lo
reclama como propio.

1. **Job system: cola de tareas + asignación de trabajadores** (temas 67, 90). Archivo:
   `04/46` nuevo. Contenido: una cola global de tareas (`{ tipo, x, y, prioridad, reservada_por
   }`) usando **`ds_priority_create`/`ds_priority_add`/`ds_priority_find_max`/
   `ds_priority_delete_max`** (verificadas, ya en uso en `04/35` y `04/38` para A*/GOAP —
   enlazar, no reescribir su explicación base) + un bucle por trabajador libre que consulta la
   cola, reserva la tarea (marcarla ocupada para que dos trabajadores no vayan al mismo sitio) y
   usa **`instance_nearest`** (verificada) para elegir la más cercana entre varias candidatas.
   Combinar con las curvas de utilidad ya escritas en `04/31 §8` (`elegir_por_utilidad`,
   `OpcionUtil`) para decidir *qué* tarea vale más la pena, no solo la más cercana.
2. **Rutinas y horarios de NPC** (tema 63). Mismo archivo. Sobre el calendario/reloj ya resuelto
   en `04/45 §5.2` (señal `nuevo_dia`) y `04/09 §5.5` (`objTimeOfDay.tiempo`): una tabla de
   horario por NPC (`[{hora_inicio, hora_fin, actividad, lugar}]`) comprobada en el Step o en un
   oyente de una señal horaria nueva.
3. **Necesidades tipo Sims para población** (tema 64). Adaptar explícitamente `04/09 §5.0
   Needs()` (enlazar, no reescribir el motor de decaimiento) a higiene/ocio/social, instanciado
   por NPC en vez de una sola vez para el jugador.
4. **Integridad estructural** (tema 57). Contenido nuevo: propagación de soporte desde el suelo
   (BFS/flood fill reutilizando el patrón de `04/05 §5.4 dungeon_flood_fill`, enlazar) con un
   contador de distancia al punto de anclaje más cercano, y colapso en cascada al superar un
   umbral.
5. **Redes de energía** (tema 59). Grafo de nodos generador/consumidor sobre `WorldGrid` (enlazar
   `04/09`), propagación de producción a consumo, prioridad de reparto cuando falta energía.
6. **Simulación fuera de pantalla** (tema 78). Patrón de «simulación abstracta barata mientras el
   chunk no está cargado» — generalizar el caso ya resuelto para cultivos (`04/45 §5.3`, que
   recorre el array global sin depender de visibilidad) a NPCs/edificios con instancia.

Documento existente a ampliar — **`04 - Recetas por género/09 - Survival y crafting.md`**:

7. **Corregir §5.3**: `ghost_valido` debe llamar a `objWorldGrid.ocupada(_gx div CELL, _gy div
   CELL)` antes de dar por válida una colocación, y `celda_construible()`/`punto_en_rango()`
   deben definirse o eliminarse de la prosa (tema 56).
8. **Contenedores**: implementar `objStorageChest` con su propia instancia de `Inventory`
   (enlazar `04/04 §5.2`, no reescribir la clase) y una UI de dos paneles (tema 5).
9. **Cosecha**: añadir `cultivo_cosechar(_col, _fila)` en `04/45 §5.3` — retira la planta en
   `EstadoCultivo.MADURA`, entrega `valor_venta`/cantidad al inventario, y una ventana de tiempo
   tras la madurez antes de pasar a `MARCHITA` (tema 45).
10. **Ganado**: nueva sub-sección en `04/45 §5` — struct `Animal` reutilizando `Needs` (enlazar)
    para alimentación diaria, producción periódica enganchada a la señal `nuevo_dia` (enlazar),
    reproducción simple por umbral de felicidad/alimentación (tema 46).
11. **Peso/capacidad de carga**: campo `peso` en la definición de ítem de `04/04 §5.3
    items.json`, capacidad máxima en `Inventory`, penalización de velocidad por sobrepeso (tema
    3).

Documento existente a ampliar — **`13 - Diseño y producción de videojuegos/01 - Diseño de juego -
core loop, mecánicas, balance y dificultad.md` §4** (economía):

12. **Precio dinámico**: una fórmula mínima (`precio = precio_base * (1 + k*(demanda -
    oferta))` o similar, con clamp) que traduzca el vocabulario ya existente de Intercambiador
    (§4.1, enlazar) a código, más un ejemplo de tienda NPC con **stock propio y spread
    compra/venta** (extender el patrón de `04/08 §5.2 valor_venta()`, enlazar) (temas 26, 27,
    31).

Documento existente a ampliar — **`04 - Recetas por género/45 - ...granja y idle.md` §6** (idle):

13. **Progreso offline con rendimientos decrecientes**: conectar la curva logarítmica ya escrita
    en `13/13 §8` (enlazar, no reescribir la fórmula) con `progreso_offline_aplicar()` (§6.4) en
    vez del tope duro actual (tema 98).

Documento existente a ampliar — **`04 - Recetas por género/09 - Survival y crafting.md` §5.4**
(chunking):

14. **Conectar el guardado de chunks con `scr_save_load.gml`**: `ChunkData.serialize()` ya existe
    (enlazar); falta la llamada real a `save_game()`/`load_game()` (enlazar `06/scr_save_load.gml`
    y `13/06 §3.10`) para persistir el diff por chunk en disco, no solo en memoria (temas 100,
    101).

Todos los símbolos de GML propuestos arriba (`ds_priority_create`, `ds_priority_add`,
`ds_priority_find_max`, `ds_priority_delete_max`, `instance_nearest`) están **verificados** contra
el runtime `2026.0.0.23` por los seis auditores de esta ronda.

---

## Lo que comprobé y NO hacía falta

Temas que parecían huecos probables y resultaron cubiertos — para que otro agente no los reabra:

- **Paso fijo con acumulador** (82): completo en `13/06 §3.9` y `13/08 §1.3`, con el macro
  `MAX_PASOS_POR_FRAME` y la advertencia explícita sobre la «espiral de la muerte».
- **Spatial hash / particionado espacial para miles de entidades** (86): esto era un hueco real
  en la auditoría externa inicial (`00-auditoria-externa-inicial.md`) y **ya está cerrado** por
  `13/08 §4` — no reabrir.
- **Utility AI genérico** (65): el motor de `04/31 §8` es completo, probado y explícitamente
  citado como «lo que usa The Sims» — lo que falta no es el motor, es un ejemplo con necesidades
  civiles en vez de combate.
- **Árbol de tecnología/habilidades** (92): `13/16` es, con diferencia, el documento más completo
  de los 101 temas evaluados — grafo, ciclos, alcanzabilidad, respec, guardado versionado, UI con
  mando. No propongas un documento nuevo de «skill trees»: amplía o enlaza.
- **Números grandes e idle math** (95, 96, 97): las tres piezas (curva exponencial, cinco
  fórmulas de crecimiento, límites de `int64` + notación mantisa/sufijo) están completas y
  conectadas entre `13/13` y `04/45 §6`.
- **Guardado versionado con migraciones** (parte de 101): `13/06 §3.10` + `06/scr_save_load.gml`
  cubren escritura atómica, tres clases de estado en ficheros separados, y migraciones
  acumulativas con ejemplo real — de sobra para cualquier juego que no necesite particionar un
  mundo gigante por chunks.
- **Sumideros/fuentes y vocabulario de economía** (28, 29 parcial, 30 parcial): `13/01 §4` y
  `13/20 §1.4` dan una base conceptual sólida con método de diagnóstico por telemetría — el hueco
  real es solo la implementación de precio dinámico y mercado, no la teoría.
- **Monedas múltiples (dura/blanda)** (33): cubierto por la combinación de `13/16 §2.6` (código)
  y `13/20 §1.4` (teoría + patrón oscuro de contraejemplo) — no propongas reescribirlo, solo
  enlazar ambos si se añade un documento de monetización de un idle.
- **Determinismo de simulación** (87): cubierto, incluyendo el aviso poco conocido de que
  `random_set_seed` no garantiza el mismo resultado entre plataformas distintas.
- **Perfil de rendimiento por frame** (88): `13/08 §14` y `01/15 §6` ya dan presupuesto en
  microsegundos y la herramienta del Debug Overlay — no hace falta un documento nuevo de
  profiling para simulación.
