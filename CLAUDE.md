# CLAUDE.md

Este repositorio es una **base de conocimiento sobre GameMaker en español**, no un proyecto
de GameMaker.

👉 **Las instrucciones completas están en [`AGENTS.md`](./AGENTS.md). Léelo antes de actuar.**
👉 **Si no sabes dónde buscar algo:** [`_indice/COMO-BUSCAR.md`](./_indice/COMO-BUSCAR.md)
   (o [`_indice/MAPA.json`](./_indice/MAPA.json), la misma información legible por máquina).

Resumen de lo imprescindible:

1. **Nunca inventes una función de GML.** Compruébala primero:
   `python3 "_indice/buscar.py" <símbolo>`. Si no aparece, no existe.
2. **Nunca edites `.yy` ni `.yyp` a mano.** Usa `gm-cli resourcetool eval` o el MCP
   `gamemaker-resource-tool`.
3. **Versión de referencia:** GameMaker LTS 2026.0 (IDE `2026.0.0.16`, runtime `2026.0.0.23`).
4. **Todo el texto que escribas va en español** con tildes y eñes. Los identificadores de la
   API se quedan en inglés.
5. **Verifica antes de decir que está hecho:** `gm-cli compile` y reporta la salida real.
6. **Si tocas el contenido, un solo comando lo deja todo al día:**

   ```
   python3 _indice/actualizar.py
   ```

   Verifica los enlaces, regenera los índices, sincroniza `MAPA.json` con el disco y revisa
   la ortografía. **No añadas documentos a `MAPA.json` a mano**: los descubre él. Sale con 0
   solo si no queda nada pendiente.
