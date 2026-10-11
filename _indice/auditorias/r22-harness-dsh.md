# r22 · Carga nativa en DeepSeek Harness (DSH)

Consulta y ejecución: **11-10-2026**, macOS arm64, Node `26.7.0`.
DSH significa [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness),
un programa distinto de un alias de Codex con un proveedor DeepSeek.

## 1. Fuente y destino

Se leyó el checkout instalado en la revisión
`639ed015397290b3745d163aafe02ffee4aa3f84`, paquete
`@deepseek-ai/dsh-skill-filesystem` `0.2.0-rc.2`. La implementación de su provider
admite `DSH_HOME` y `DSH_AGENTS_HOME`; sus defaults son `~/.dsh` y `~/.agents`.
Consulta skills en el subdirectorio `skills/`. Las fuentes de proyecto `.dsh/skills`
y `.agents/skills` tienen prioridad frente a las de usuario; los directorios
personalizados y bundled también participan según la configuración del provider.
Fuente: [provider filesystem y configuración](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/skill/skill-filesystem/README.md).

El instalador usa `./instalar.sh --harness dsh` y respeta `DSH_HOME` del proceso.
Conserva el paquete entero, no solo `SKILL.md`. No modifica perfiles ni proveedores.
Una sesión puede deshabilitar el provider o sus raíces: la copia no demuestra activación.

## 2. Recibo ejecutado

La prueba importó el **provider real compilado**, invocó `list` y `get` en un fixture
temporal, sin watcher ni raíces globales. Recibió un candidato `gamemaker-biblioteca`;
su cuerpo coincidió exactamente con el cuerpo del frontmatter de r47.
El manifest de **12 archivos** y los bytes de cada archivo copiado coincidieron con
el paquete fuente; todas sus referencias permanecieron accesibles. **Cero avisos**
del parser y **cero peticiones LLM**.

Programa reproducible: [`probar-dsh.mjs`](../pruebas/probar-dsh.mjs).

```sh
node _indice/pruebas/probar-dsh.mjs "$CHECKOUT_DSH_COMPILADO" \
  _indice/skills/gamemaker-biblioteca
```

`CHECKOUT_DSH_COMPILADO` identifica la instalación comprobada que contiene
`packages/skill/skill-filesystem/lib/index.js` y sus dependencias. El comando no
descarga, instala ni arranca DSH en modo agente. Borra únicamente su propio fixture.

## 3. Qué acredita

La evidencia demuestra discovery, parseo y acceso al paquete en la versión y plataforma
indicadas. No certifica una conversación, la selección automática por un modelo,
Windows/Linux ni futuras versiones. La revisión y compilación de las herramientas
GameMaker se registran por separado.
