# Futuro de GameMaker: roadmap 2026–2028

> Todo lo de este documento es **planeado o en desarrollo**. Las fechas son las que YoYo Games publicó en el *GameMaker Update Spring 2026* (30/04/2026) y pueden moverse.
> Última actualización del documento: agosto de 2026.

---

## 1. Calendario LTS

| Versión | Ventana prevista | Estado |
|---|---|---|
| **2026.0** | Q2 2026 | ✅ Publicada el 21/05/2026 |
| **2026.1** | Q4 2026 | En Beta (serie 2026.100) |
| **2026.2** | Q1 2027 | Planeada |
| **2026.3** | Q4 2027 | Planeada |
| **2026.4** | Q1 2028 | Planeada |

### Betas continuas

Durante todo el ciclo LTS26 habrá una **Beta** con todos los últimos fixes, publicada **cada vez que haya cambios** y pasen los tests automáticos. Objetivo: acceso temprano a los arreglos sin esperar a las versiones programadas.

### El runtime GMS2 se congela

- **Feature complete**: todas las feature requests nuevas y pendientes **solo se consideran para GMRT**.
- Soporte del runtime GMS2 hasta **al menos Q1 2028**, pero **solo SDK updates y bugs críticos**.
- Los suscriptores **Enterprise** tienen acceso al código fuente del runtime y pueden recibir parches y SDKs al margen del ciclo LTS26.

---

## 2. Plugins de IDE (actualizables por Package Manager)

Durante LTS26 se publicarán y actualizarán varios plugins de IDE. Son **independientes de las actualizaciones de la IDE** y llegan por el Package Manager. Cada versión completa de LTS26 **consolida los plugins a su última versión**.

| Plugin | Qué se planea |
|---|---|
| **Code Editor 2** | Actualizaciones durante toda la vida de LTS26; al ser plugin, llegarán antes sin esperar a versiones LTS |
| **Start Page** | Rediseño para que sea más amigable y accesible, y para unificar en un solo hub las distintas vistas de la infraestructura y la comunidad de GameMaker |
| **ProjectTool** | Corrección de bugs en la conversión de proyectos y mejoras en el manejo de proyectos |
| **Prefab Builder** | El esperado constructor de Prefabs para crear y compartir los tuyos |

> Nota: desde la **Beta 2026.100 Release 5 (27/08/2026)** el **Prefab Builder ya está disponible**, aunque en fase temprana y con problemas de UI conocidos.

Sobre crear tus propios plugins de IDE: el equipo espera tener novedades **hacia finales de año**.

---

## 3. GMRT: salida de Beta

### Planes

- **Desktop** sale de Beta «en los próximos meses».
- **Móvil y consola** se irán haciendo disponibles «a lo largo del año».

### v0.20 (ya publicada, junio 2026)

- 99 % de funcionalidad de compatibilidad
- Target **Android**
- Target **Switch**
- Funciones **3D**
- **Código fuente abierto** para Desktop, Mobile y Web para **todos** los usuarios

### Acceso al código fuente

| Plataforma | Quién tiene acceso |
|---|---|
| **Desktop, Mobile, Web** | **Todos** los usuarios (acceder, modificar y compilar) |
| **Consola** | Usuarios **Enterprise**, de las plataformas para las que estén verificados |

La distribución comercial de juegos **sigue requiriendo licencia activa**.

### 3D en GMRT

| Área | Qué incluye |
|---|---|
| **Model loading** | Carga desde ficheros **glTF** (se añadirán otros formatos con el tiempo) |
| **Scene Graph** | Simplifica el manejo de mundos 3D: construir mundos y entornos complejos |
| **Matemáticas 3D** | Mejor soporte de **matrices, cuaterniones** y funciones útiles de 3D |
| **Animación** | De momento, animaciones simples cargadas desde los glTF; ampliarán el soporte |

Están usando **Blender** como fuente principal para creación de assets y quieren **integrar estrechamente el flujo de Blender** en el futuro.

Detalle de lo que ya hay en `03 - GMRT - El nuevo runtime.md`.

---

## 4. Expansión de lenguajes

Uno de los cambios más grandes. Se añadirán nuevos lenguajes a los proyectos GMRT:

| Lenguaje | Cuándo | Cómo se integra |
|---|---|---|
| **JavaScript** (EcmaScript 2020) | **Q2 2026** | **First class**: puedes sustituir cualquier GML por JS |
| **TypeScript** | **Q3 2026** | **First class**: igual que JS |
| **C#** | **Q4 2026** (preview) | **Interoperabilidad** con GML / JS / TS |

### JavaScript y TypeScript

Al ser lenguajes *first class*, podrás usarlos:

- en **Object Events**
- en **Timeline moments**
- en **Scripts**
- o donde quieras

Es decir: **cualquier trozo de GML puede ser JS o TS**.

### C#: modelo distinto

C# **no** sustituye a GML: **se llama desde** GML / JS / TS.

- Herramientas para **transferir argumentos fácilmente** entre lenguajes.
- El código C# podrá **acceder a un struct de GML** y **modificar el contenido de un array de GML**.
- Permite crear **callbacks**: una función C# puede ser invocada desde GML/JS/TS, y código GML/JS/TS puede ser invocado desde C#.

> ⚠️ **Importante:** al usar C#, **tanto el runtime de GMRT como el de C# estarán en memoria, y ambos recolectores de basura funcionando a la vez.** Tenlo en cuenta para el rendimiento y el consumo de memoria.

```
┌──────────────────────────────────────┐
│  GML / JS / TS   (first class)       │  ← puedes elegir en cada archivo
├──────────────────────────────────────┤
│  GMRT runtime  +  C# runtime         │  ← conviven en memoria
│  GC de GMRT    +  GC de .NET         │  ← ambos activos
└──────────────────────────────────────┘
```

### Implicación estratégica

Si vienes de JS/TS, en 2026 GameMaker se vuelve **mucho** más accesible. Y si vienes de Unity, C# te da una vía de entrada sin reescribir tu cabeza.

---

## 5. Herramientas de desarrollador: GM CLI

### Qué es

Un conjunto de **herramientas de línea de comandos** para interactuar con proyectos de GameMaker **mediante API y CLI**, sin abrir la IDE.

Dos objetivos:

1. **Continuous Integration**: construir proyectos fuera de la IDE.
2. Manipular proyectos por API en lugar de por la IDE.

### Alcance

Desde operaciones simples —`build`, `run`, `compile`— hasta complejas —`create project`, `add sprite`, `add event to object`.

### Detalles

- **Licencia**: **Apache License** (open source).
- **Disponible ya**.
- npm: https://www.npmjs.com/package/@gamemaker/gm-cli

```bash
# Instalación global con npm (el gestor con el que está instalado en este Mac)
npm install -g @gamemaker/gm-cli

# Comandos (verifica la sintaxis exacta con --help antes de usarlos)
gm-cli --help
```

> ⚠️ No he verificado uno a uno los subcomandos ni sus flags. Ejecuta `gm-cli --help` y la ayuda de cada subcomando antes de montar una pipeline de CI.

### Extension Generator

Nueva herramienta que permite a proyectos **GMS2 y GMRT** interactuar con **librerías externas**, proporcionando una interfaz consistente.

Sirve para:

- cubrir el hueco de capacidades del runtime GMS2;
- ser el **puente al futuro**: que las extensiones funcionen mucho más allá del ciclo de vida de GMS2.

Repositorio: https://github.com/YoYoGames/GM-ExtensionGenerator

También planean **revisar sus extensiones existentes** para actualizarlas a esta herramienta.

---

## 6. Extensiones oficiales

Están trabajando con socios externos para traer sistemas y librerías externas como extensiones oficiales.

### Extensiones recientes / próximas

- **ISteamParties** en Steamworks
- **Switch 2** para FMOD
- **Discord Social SDK**
- **Reddit Devvit SDK**
- **Apple y Google IAPs**
- **Opera Ads**
- **Photon Multiplayer**
- **Razer Wyvrn SDK**

### Multiplayer

Han decidido **no** construir un sistema propio y en su lugar centrarse en **varios proveedores de sistemas multiplayer**, para que elijas:

| Proveedor | Estado |
|---|---|
| **Namazu Elements** | Ya disponible — https://github.com/YoYoGames/GMEXT-Elements |
| **Colyseus** | Ya disponible — https://docs.colyseus.io/getting-started/gamemaker |
| **Steamworks** | Soporte oficial continuo — https://github.com/YoYoGames/GMEXT-Steamworks |
| **Photon** | *Coming soon* |

> ⚠️ Novedad importante: en la **Beta 2026.100 Release 2** se ha **eliminado la funcionalidad de rollback** de GmlSpec. Si tu juego depende de **rollback multiplayer**, **quédate en 2026.0** hasta tener un sistema alternativo.

---

## 7. Rediseño del Room Editor

Están **repensando completamente el Room Editor**. No hay detalles concretos todavía, pero:

- Verás movimiento en las **feature requests** en los próximos meses.
- Si hay algo que siempre has querido: **dale thumbs-up a la petición existente** o crea una nueva si nadie la ha pedido.

Repositorio de peticiones: https://github.com/YoYoGames/GameMaker-Bugs
Roadmap público: https://roadmap.gamemaker.io y https://github.com/orgs/YoYoGames/projects/17/views/48

---

## 8. Qué ya está aquí y qué falta (resumen)

### Ya disponible (LTS 2026.0)

- UI Layers y Flexpanels
- Particle Editor y asset Particle System
- Package Manager y Prefab Library
- Code Editor 2 (Beta, opt-in)
- Feather activado por defecto
- SVG, fuentes SDF, nuevos FX, formatos de superficie
- Buses y efectos de audio, Audio Loop Points
- Debug Overlay nuevo con ventanas personalizadas
- Handles en GML, template strings, arrays y tilemaps en colisiones
- Targets Nintendo Switch 2 y Reddit
- Windows ARM64

### En Beta 2026.100 (hacia 2026.1)

- Prefab Builder
- Workspaces con pestañas scrollables
- Validación y reparación de paquetes
- Split windows (infra lista, función pendiente de activar)
- Eliminación de rollback

### Pendiente (según roadmap)

- GMRT fuera de Beta en desktop, y móvil/consola después
- JavaScript (Q2), TypeScript (Q3), C# preview (Q4)
- Extensiones: FMOD Switch 2, Discord, Reddit, IAPs, Opera Ads, Photon, Razer Wyvrn
- Rediseño del Room Editor
- Nueva Start Page
- Plugins propios de IDE
- Prefab Builder completo y pulido

---

## 9. Cómo prepararte

### Ahora mismo

1. **Migra tus proyectos serios a LTS 2026.0** y resuélveles los Handles y las colisiones. Cuanto antes lo hagas, menos deuda acumulas.
2. **Aprende UI Layers y Flexpanels.** Es la forma nueva de hacer interfaces; el Draw GUI va a dejar de ser el camino por defecto.
3. **Monta un proyecto de pruebas con GMRT** y ve siguiendo sus release notes. No migres nada importante todavía.
4. **Decide qué lenguaje vas a usar a medio plazo.** Si te viene bien JS/TS, quédate atento a Q2/Q3. Si vienes de C#, espera al preview de Q4.
5. **Mira GM CLI** si quieres CI/CD para tus juegos.

### A medio plazo

6. **Cuando GMRT salga de Beta en desktop**, replantea la migración proyecto a proyecto.
7. **Sigue la Beta 2026.100** si quieres anticipar lo que viene en 2026.1.
8. **Participa en las feature requests** del Room Editor: es el momento en que te van a escuchar.

---

## Fuentes

- GameMaker Update Spring 2026 (roadmap) — https://gamemaker.io/en/blog/update-spring-2026
- GameMaker LTS 2026.0 — https://gamemaker.io/en/blog/lts-2026-release
- GM CLI en npm — https://www.npmjs.com/package/@gamemaker/gm-cli
- Extension Generator — https://github.com/YoYoGames/GM-ExtensionGenerator
- Namazu Elements — https://github.com/YoYoGames/GMEXT-Elements
- Colyseus para GameMaker — https://docs.colyseus.io/getting-started/gamemaker
- Steamworks — https://github.com/YoYoGames/GMEXT-Steamworks
- Roadmap público — https://roadmap.gamemaker.io
- Proyecto de roadmap en GitHub — https://github.com/orgs/YoYoGames/projects/17/views/48
- Issues / feature requests — https://github.com/YoYoGames/GameMaker-Bugs
- Release notes Beta 2026.100 — https://releases.gamemaker.io/release-notes/2026/100
- Release notes GMRT 0.20.0 — https://releases.gamemaker.io/release-notes/2026/GMRT_MS_20.html
- Release notes GMRT 0.21.0 — https://releases.gamemaker.io/release-notes/2026/GMRT_MS_21
