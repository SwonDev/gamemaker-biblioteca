# Procedencia de las vistas para publicar

Estos datos son **vistas anonimizadas**, no una transcripción literal del entorno privado. Antes de preparar estas vistas se conservaron íntegros los 69 archivos originales de datos y el informe en custodia privada, con contraste byte por byte. La custodia no forma parte del repositorio público.

Solo se sustituyen los prefijos de ubicación por `<RAIZ_BIBLIOTECA>` y `<CUSTODIA_PRIVADA>`. Se añaden notas de procedencia a los metadatos, al control y al informe. No se cambian escenario, rúbrica, respuestas, puntuaciones ni bytes de los dos paquetes conservados. Las rutas de las lecturas publicadas son representaciones del lugar original; sus huellas siguen identificando los bytes realmente leídos.

Los prompts publicados contienen marcadores y **no son los textos literales que recibieron los agentes** cuando había una ruta privada. En cada metadato, `prompt_sha256` conserva la huella del prompt bruto que se utilizó; `vista_publica.prompt_vista_sha256` identifica por separado el texto público actual. No se atribuye esta segunda huella al prompt leído. El control sin guía no contenía esos prefijos: sus dos huellas coinciden.

[Huellas originales](./huellas-originales.json) conserva nombres, tamaños y SHA-256 anteriores a la anonimización. [Vistas y derivaciones](./vistas-para-publicar.json) relaciona para cada archivo la huella original, la huella pública, sus tamaños y la transformación admitida. Incluye el informe y los nuevos artefactos de procedencia; excluye su propia huella para evitar una dependencia circular. Un recibo externo puede fijar tanto este manifiesto como el control final.

Los mensajes `LECTURAS_R49` y `LECTURAS_R49_FINAL` son también vistas cuando contienen un marcador. Su texto bruto se conserva en la custodia indicada por el manifiesto. Los recibos históricos del ensayo siguen siendo históricos: anonimizar rutas no vuelve a ejecutar agentes, GameMaker ni comprobaciones del juego.

Para comprobar la coherencia pública:

```sh
python3 _indice/auditorias/r24-ensayos/verificar-vistas.py
```

La comprobación privada adicional requiere acceso a la custodia original. El marcador siguiente debe sustituirse por su ubicación local; no se guarda esa ubicación en el informe público:

```sh
python3 _indice/auditorias/r24-ensayos/verificar-vistas.py --custodia "<CUSTODIA_PRIVADA>"
```

La comprobación pública verifica los archivos disponibles y la atribución de huellas. Solo el segundo modo contrasta además los brutos privados y reproduce las sustituciones de prefijos. Ninguno demuestra eficacia causal de la skill ni ejecución de un juego.
