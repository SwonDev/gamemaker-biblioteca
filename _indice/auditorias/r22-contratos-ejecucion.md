# r22 · Ejecución de contratos de plural, replay y snapshot

Fecha: **11-10-2026**. Prueba funcional dirigida sobre las correcciones documentales
posteriores a r46. **214 comprobaciones correctas, 0 fallidas**, ejecutadas dentro
del runner; no solo compiladas. Este recibo amplía la evidencia de
[r22 · Lagunas](./r22-lagunas.md), sin convertir sus planes restantes en resultados.

## 1 · Fuente, entorno y repetición

Se ejecutó el GML real de [04 · 21 — Localización](<../../04 - Recetas por género/21 - Localización e idiomas (con traducción por IA).md>)
§2 y [13 · 10 — QA](<../../13 - Diseño y producción de videojuegos/10 - Testing y QA.md>)
§§2.2 y 14.3, además de [04 · 14 — Multijugador](<../../04 - Recetas por género/14 - Multijugador.md>)
§§5.0–5.1 y 5.5–5.8. El orquestador extrae nueve bloques completos, sin modificar sus funciones,
y compara las huellas de los bloques otra vez al terminar. No hay una implementación
alternativa de los plurales, del verificador ni del parser en Python.

```sh
python3 _indice/pruebas/probar-contratos-r47.py
# Solo extracción y huellas, sin ejecutar el motor:
python3 _indice/pruebas/probar-contratos-r47.py --solo-extraer
```

Requiere Python **3.10 o posterior**, `gm-cli` **2.4.0** y runtime **GMS2 2026.0.0.23**.
Entorno observado: **macOS arm64**, VM, target `mac`, Python **3.12**. Se creó un proyecto
temporal propio con plantilla `blank`; objetos, scripts e instancia por ResourceTool.
Se validó el banco antes de ejecutarlo: **5 archivos GML, 397 llamadas**, sin nombres
inexistentes ni aridades incorrectas. La compilación sin `--errors-only` terminó con
salida **0**, sin líneas `WARNING`; después el runner emitió el resultado y terminó.

Los artefactos privados de cada pasada quedan en la carpeta temporal impresa: logs de
versión, creación, recursos, validación, compilación y ejecución, más `recibo.json` con
huellas y recuentos. No se publican rutas personales. Hay un tope de 240 segundos por
comando; si se agota, se termina solo el grupo de procesos creado por ese comando.
La regresión inerte [probar-topes.py](../pruebas/probar-topes.py) reproduce un hijo
que ignora SIGTERM después de salir el padre: falló antes de la corrección y pasa
con SIGKILL al grupo también en ese caso. Sus tres casos pasan en macOS; en Windows
se omiten explícitamente porque este runner requiere grupos POSIX.
Cero comprobaciones o un resultado ausente no se consideran verde.

| Bloque bajo prueba | SHA-256 del bloque |
|---|---|
| `txt`, `categoria_plural_entero`, `txt_n` | `95b0a341c9b4eccd058961a5a0ef35af4e5d6c5d4d3f74ef00f7d35e938e66b6` |
| `AzarReproducible`, `generar_botin` | `e481dffd61f2e15b87e2742561c787cc2eb745e4632534e694efa47583c64fdb` |
| Grabación y verificación del replay | `b2c27b4c996164ab57380fe8b723b7ab3f74bbd0f427b4146523b4a43851e801` |
| `recibir_snapshot` | `fab632cbb5d5685e3d5f096df66d2b65cd65880d5720fa0820d0926943615b1a` |
| `reconciliar` | `6e1eb735d311c5708f2733510452c97bed7def700697c02f48ee3d13a3e8c0ef` |
| `servidor_consumir_inputs` | `2c1a417db6720a34ba6d796712f94d9a385c8b2036df2f5701e5a1db710d75f7` |
| Constantes de red | `944e5f8e964535487b0dcbe326c686c0f2b2e1cddf58a79772a82567730263b2` |
| Create de `objNetManager` | `c796baa3ac87b01747e0bcdaca51abf0ee78fa237266a1d5f7b231f24b4c38c4` |
| Create de `objNetEntity` | `8b08509c2313b915ee1b0cd4560b3111775161c95400520f98156b157455d5cf` |

El banco es [banco_contratos_r47.gml](../pruebas/banco_contratos_r47.gml); su orquestador
es [probar-contratos-r47.py](../pruebas/probar-contratos-r47.py). Las huellas vinculan
este resultado a los bloques indicados; un cambio posterior necesita una nueva pasada.

## 2 · Plural e interpolación: 112 comprobaciones

Expectativas independientes del helper, tomadas del contrato entero y de las categorías
cardinales de [CLDR 48](https://www.unicode.org/cldr/charts/48/supplemental/language_plural_rules.html),
consultado el 11-10-2026. Se cubren los **13 identificadores de idioma** implementados,
incluidas las variantes regionales de portugués.

- Cero, uno y otros enteros; negativos como cantidades absolutas; transición alrededor
  de un millón y límite de mil millones. `pt`/`pt-BR` y `pt-PT` distinguen el cero.
- Ruso: categorías alrededor de 11–14, 21–24 y centenas. Árabe: seis categorías,
  incluidos 100–103 y repetición por centenas. Japonés, coreano y chino conservan `other`.
- Decimales, cantidades sobre el límite, string, `undefined`, struct y array se rechazan;
  un idioma fuera del subconjunto no recibe una categoría adivinada.
- `txt_n` selecciona la cadena por categoría; se interpolan dos variables. Falta de clave,
  falta de categoría y plural no admitido producen sus marcadores visibles.

No se ejecutó la carga de Included Files ni un renderer. Esta batería no demuestra
fallback de archivos, glifos, grafemas, bidi, decimales visibles, ordinales ni todo CLDR.

## 3 · Replay: 73 comprobaciones

El fixture aporta una regla pequeña: un punto por tick, dos por acción A y cinco por B.
Contadores causales y el registro del orden de acciones observan el uso del simulador;
no son otra copia de `replay_verificar`.

| Escenario observado | Resultado del runner |
|---|---|
| Dos acciones grabadas en el mismo tick | Un tick; ambas acciones en orden `AB` |
| Acciones en 0 y 600 | 601 ticks, dos acciones, puntuación 608 |
| Diez ticks sin acciones; duración cero sin eventos | Diez avances y cero avances, respectivamente |
| Presupuestos exactamente iguales a bytes, frames y eventos | Acepta |
| Un byte, frame o evento por encima del presupuesto | Rechaza sin iniciar la simulación |
| Paquete/tipos/campos ausentes; JSON malformado con checksum correcto | Rechaza sin iniciar la simulación |
| Semilla o versión distintas de la sesión | Rechaza sin iniciar la simulación |
| Eventos negativos, fraccionarios, fuera de duración o desordenados | Rechaza sin iniciar la simulación |
| Puntuación falsa y checksum recalculado | Re-simula y rechaza por la puntuación |
| Otro replay consistente y checksum recalculado | Acepta: el checksum público no acredita autoría |
| JSON con otro orden de propiedades y checksum de sus bytes exactos | Acepta sin depender de una reserialización |

La parte de plural y replay ejecuta nueve funciones de los bloques extraídos. `generar_botin` se compila
porque comparte bloque con el constructor; no se atribuye aquí una prueba de su distribución.
La regla del fixture no consume azar, así que tampoco demuestra calidad del generador ni
paridad numérica con un backend en otro lenguaje.

## 4 · Snapshot, ACK y callback: 29 comprobaciones

Los buffers del fixture siguen el formato publicado: cabecera de seis bytes, registros
de 19 bytes y ACK final de cuatro. El fixture construye entradas y llama al parser real;
no sustituye `recibir_snapshot`, `reconciliar` ni `servidor_consumir_inputs`. Los Create
documentados inicializan las instancias reales de manager y entidad. Los buffers son
propios del fixture y se liberan; no son buffers del evento Async Networking.

| Escenario observado | Resultado del runner |
|---|---|
| Snapshot de dos registros | Longitud 48 bytes; lectura válida de posición, velocidad y vida |
| ACK 2 con historial 1–4 | Retira 1 y 2; conserva 3 y 4 |
| Misma alianza y propietarios 42/43; cliente 42 | Propia reconcilia; remota conserva posición actual y recibe destino de interpolación |
| Primer snapshot y siguiente snapshot vacío válido | Inicializa el anterior; rota ticks y confirma el resto del historial |
| Tick repetido o anterior; ACK superior o regresivo | Rechaza; conserva snapshot, ACK, longitud del historial y número de entidades |
| Cabecera/registro/ACK truncados; contador sobre el máximo | Rechaza; conserva esos mismos observables de estado |
| Callback ausente o pendiente | No adelanta la secuencia confirmada de cada cliente |
| Callback aplicado con dos clientes | Confirma las secuencias 3 y 6 por separado; recibe IDs asignados y omite cliente sin input |

Esto ejecuta los tres helpers de red y los dos Create. No ejecuta el evento asíncrono,
el emisor de snapshots, la interpolación en Step, framing TCP raw ni sockets. La prueba
de propietario observa la ruta de aplicación del snapshot; no acredita predicción ni
reconciliación completa con colisiones y re-simulación de inputs.

La revisión independiente detectó que el caso del máximo también podía rechazarse
por truncamiento. Se sustituyó por un paquete completo de 1025 registros, con tick
y ACK válidos, para aislar el límite. El banco corregido se recompiló y volvió a
ejecutar: **214 correctas, 0 fallidas**.
Como control negativo se compiló y ejecutó una copia desechable del fixture retirando
solo la guarda `NET_MAX_ENTIDADES`: produjo **210 correctas, 4 fallidas**, empezando
por el rechazo del máximo y la conservación de estado. El original permaneció intacto.

## 5 · Límites de esta evidencia

No se ejecutaron Cryalis, servicios, modelos, cuentas ni configuración global. No se
probaron Steam Cloud ni sockets loopback. Los escenarios de transporte, gameplay y servicios
no cubiertos aquí siguen siendo planes hasta que otro recibo registre una ejecución.

La validez del replay para el juego real requiere su estado inicial, repertorio de acciones,
reloj, colisiones, azar y servidor autenticado. Aquí se acredita el contrato de transporte
y re-simulación del ejemplo con la regla del fixture: no quién jugó, ni protección contra
bots, ni equivalencia entre lenguajes, ni todos los targets de GameMaker.
