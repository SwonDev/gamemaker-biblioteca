# r22 · Carga nativa de la skill en Pi y OMP

Fecha de consulta y pruebas: **11-10-2026**. Investigación primaria y pruebas aisladas de
lectura, descubrimiento y análisis de instrucciones. El proyecto fuente permanece pausado
y fuera de las entradas. No se instalaron harnesses ni se modificaron proveedores, modelos,
configuraciones globales, el instalador o la skill. No se abrió una sesión de modelo.

## 1. Identidad y versiones observadas

| Componente | Identidad verificada | Entorno observado | Requisito del manifiesto instalado |
|---|---|---|---|
| Pi nativo | `@earendil-works/pi-coding-agent` **1.1.0** | Node **26.7.0**, macOS | Node `>=22.19.0` |
| OMP nativo | `@oh-my-pi/pi-coding-agent` **18.8.7** | Bun **1.3.14**, macOS | Bun `>=1.3.14` |

Se ejecutaron las entradas nativas con `--version`: devolvieron `1.1.0` y
`omp/18.8.7`. También se leyeron sus manifiestos instalados. La versión de compatibilidad
Node que declara Bun, `v24.3.0`, no es la versión del ejecutable Node probado.

Un comando llamado `pi` puede ser un envoltorio de Gentle Shell; un comando `omp` también
puede ejecutar mantenimiento antes de delegar. En el entorno observado existían esos
envoltorios. La prueba importó directamente los módulos instalados y evitó los envoltorios.
Detectar un nombre en `PATH` no identifica el directorio efectivo de una sesión. Pi
actual usa el paquete de Earendil Works; una instalación antigua puede conservar otro
nombre de paquete. Estas versiones no certifican otras distribuciones.

## 2. Destinos, variables y alias

La carpeta de la skill debe llamarse `gamemaker-biblioteca` y conservar el paquete entero:
`SKILL.md`, `AGENTS.md` y todos los archivos de `references/`. El paquete r47 probado
contiene 12 archivos, incluidas diez referencias.

| Harness | Usuario, sin personalización | Proyecto | Fuente compartida |
|---|---|---|---|
| Pi | `~/.pi/agent/skills/gamemaker-biblioteca/` | `.pi/skills/gamemaker-biblioteca/` en el directorio de trabajo | `~/.agents/skills/` y `.agents/skills/` en ancestros hasta la raíz Git, si existe |
| OMP | `~/.omp/agent/skills/gamemaker-biblioteca/` | `.omp/skills/gamemaker-biblioteca/` en el directorio y sus ancestros hasta la raíz del repositorio | `.agents/skills/` y alias `.agent/skills/`, de usuario y proyecto |

Pi exige confianza para habilitar recursos del proyecto en su gestor de recursos,
incluidas las carpetas `.agents`. Su API básica `loadSkills` solo consulta `.pi` del
directorio recibido; el recorrido de `.agents` corresponde al gestor superior. La
prueba confirmó la API básica y la lectura explícita de `.agents`; el recorrido y la
confianza del gestor superior se comprobaron por lectura de código, sin abrir una sesión.
Fuente: [gestor de paquetes de Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/core/package-manager.ts).

OMP descubre las carpetas de proyecto desde el directorio más cercano. Su provider
`native` tiene prioridad 100 y `agents` prioridad 70. El escaneo convencional mira un
solo nivel bajo `skills/`; Pi admite recursividad. Fuentes:
[provider nativo OMP](https://github.com/can1357/oh-my-pi/blob/main/packages/coding-agent/src/discovery/builtin.ts),
[provider agents OMP](https://github.com/can1357/oh-my-pi/blob/main/packages/coding-agent/src/discovery/agents.ts).

Las variables se interpretan dentro del proceso que las recibe; no deben exportarse
globalmente para dirigir varios harnesses que comparten el nombre `PI_CODING_AGENT_DIR`.

| Variable | Pi 1.1.0 | OMP 18.8.7 |
|---|---|---|
| `PI_CODING_AGENT_DIR` | Sustituye el directorio de agente de usuario; admite expansión de `~` | Sustituye el agente del perfil predeterminado mediante `path.resolve`; no expande un `~` literal |
| `PI_CONFIG_DIR` | No es el selector usado por `getAgentDir` de este paquete | Cambia el segmento de configuración bajo el directorio de usuario; predeterminado `.omp` |
| `OMP_PROFILE` | No es un selector del resolver de Pi probado | Perfil principal: `<raíz>/profiles/<perfil>/agent`; prevalece sobre el alias y sobre el override de agente |
| `PI_PROFILE` | No es un selector del resolver de Pi probado | Alias de perfil consultado únicamente si `OMP_PROFILE` está ausente |

**`OMP_PROFILE` presente pero vacío selecciona el perfil predeterminado**, aunque
`PI_PROFILE` tenga un nombre. No equivale a `OMP_PROFILE or PI_PROFILE`. Los nombres
de perfil se validan en OMP; un instalador no debe concatenar un nombre arbitrario.
El código instalado de utilidades, `src/dirs.ts` líneas 42–79, recorta el nombre,
trata `default`, vacío y espacios como perfil implícito, y exige
`^[a-z0-9][a-z0-9._-]{0,63}$`. Excluye punto final y los nombres Windows
`CON`, `PRN`, `AUX`, `NUL`, `COM0`–`COM9`, `LPT0`–`LPT9`, también con extensión.
La validación del CLI está en `src/cli.ts` línea 453; un import aislado del resolver
puede ocultar un perfil inválido y volver al predeterminado.
Fuente: [resolver de directorios OMP](https://github.com/can1357/oh-my-pi/blob/main/packages/utils/src/dirs.ts).

Diez probes del resolver instalado confirmaron: defaults Pi/OMP, override absoluto en
ambos, `PI_CONFIG_DIR=.r22-config`, alias de perfil, prioridad del perfil principal,
principal vacío, `~` literal en override OMP y raíz absoluta OMP. El último caso importa:
`PI_CONFIG_DIR=/tmp/r22-config` se une bajo el directorio de usuario; Python
`Path(home) / valor_absoluto` no reproduce esa operación. Para seleccionar un agente
absoluto de OMP se usa `PI_CODING_AGENT_DIR`, con el perfil predeterminado.

El resolver nativo no consulta `XDG_CONFIG_HOME`: conserva la raíz construida con
`PI_CONFIG_DIR` (`src/dirs.ts` líneas 115–121 y 307–308). XDG afecta categorías
de datos, estado y caché, no `getAgentDir` ni el destino nativo de skills
(`src/dirs.ts` líneas 366–418 y 619–620; provider `src/discovery/builtin.ts` línea 313).
El código instalado contempla XDG en macOS y Linux cuando existen las carpetas
correspondientes; no convierte por ello el default de skills en `~/.omp/skills`.
Las pruebas no migraron XDG ni ejecutaron `omp config init-xdg`. Linux, Windows, WSL y
perfiles XDG se revisaron como ramas de código; carecen aquí de prueba nativa.
Fuente Pi: [configuración](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/config.ts).

## 3. Frontmatter y activación

El formato portable usa YAML válido, `name` de 1–64 caracteres en minúsculas ASCII,
dígitos o guiones, sin guiones al principio/final ni dobles; coincide con la carpeta.
`description` es una cadena no vacía de hasta 1024 caracteres. Las referencias se
resuelven desde la carpeta de la skill. Fuente:
[especificación Agent Skills](https://agentskills.io/specification).

Pi excluye una skill declarada sin descripción o con YAML mal formado; otras
infracciones del nombre pueden producir avisos sin excluirla. No exige coincidencia
entre nombre y carpeta. `disable-model-invocation: true` la oculta del catálogo para
selección automática y conserva su comando explícito. Los nombres en colisión conservan
la primera entrada y generan diagnóstico. Fuente:
[loader de Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/core/skills.ts).

OMP nativo exige descripción y rechaza nombres con separadores de ruta. El scanner de
`agents` es más permisivo. `enabled: false` excluye entradas convencionales; el parser
normaliza `disable-model-invocation` a `disableModelInvocation`. **El caso
`description: [sin cierre` se cargó en OMP como texto recuperado y se rechazó en Pi**.
Por tanto, cargar en OMP no sustituye una validación independiente de YAML. Fuentes:
[scanner OMP](https://github.com/can1357/oh-my-pi/blob/main/packages/coding-agent/src/discovery/helpers.ts),
[parser de frontmatter OMP](https://github.com/can1357/oh-my-pi/blob/main/packages/utils/src/frontmatter.ts).

Ambos anuncian metadatos y leen las instrucciones cuando se necesitan. Pi ofrece
`/skill:gamemaker-biblioteca`; OMP también ofrece comandos explícitos y acceso
`skill://gamemaker-biblioteca`. La activación automática depende del agente y de sus
ajustes; no garantiza que un modelo obedezca la metodología. No se probaron estos
comandos dentro de una conversación. Fuentes:
[guía de skills Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md),
[guía de skills OMP](https://github.com/can1357/oh-my-pi/blob/main/docs/skills.md).

## 4. Recibo de carga ejecutado y reproducible

**Resultado final sobre r47: Pi 76 comprobaciones, OMP 74, cero fallos.**

El probe coteja por recorrido todos los archivos del paquete en cada destino temporal.
Se repitió después de la sincronización del paquete final, de 12 archivos.

Se copió el paquete completo a fixtures temporales privados. Se compararon los 12
archivos byte a byte por SHA-256 en los cinco destinos, junto con sus listas completas.
Se ejercitaron directorios nativos de usuario y
proyecto, enlaces, controles sin descripción, YAML roto, una skill anidada y controles
de ocultación/desactivación. Pi comprobó también la ausencia de recorrido `.pi` en
su loader básico. OMP ejercitó los providers nativos y `agents` registrados de verdad,
incluido el alias singular y el recorrido desde un subdirectorio.

OMP devuelve las dos entradas de un enlace y su destino en el provider crudo; su
deduplicación superior queda fuera de esta prueba. Pi sí ejercitó deduplicación en
`loadSkills`. No se simuló un parser ni se ejecutó una sesión de agente. El primer
intento del control YAML de OMP reveló la recuperación permisiva; se corrigió la
expectativa del recibo, conservando el caso como regresión observable.

El bloque siguiente es el programa ejecutado sobre r47. Sus argumentos son configurables:
raíces **del paquete instalado del harness**, no el ejecutable ni un clon arbitrario,
y carpeta del paquete de la skill. El import OMP requiere el paquete de utilidades
contiguo que acompaña su instalación. No se descarga ni instala nada.

```sh
env -i PATH="$PATH" node prueba-loader.mjs pi "$PI_PAQUETE" "$PAQUETE_SKILL"
env -i PATH="$PATH" bun prueba-loader.mjs omp "$OMP_PAQUETE" "$PAQUETE_SKILL"
```

`PI_PAQUETE`, `OMP_PAQUETE` y `PAQUETE_SKILL` se sustituyen por las rutas comprobadas en
la máquina de prueba. `env -i` evita transmitir credenciales o perfiles heredados.
El programa fija el agente dentro del fixture sin redefinir `HOME`, importa únicamente
los loaders indicados, bloquea `fetch` y elimina exclusivamente sus propios fixtures.
Esto no constituye un sandbox universal de red; no invoca código de inferencia.

```javascript

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import assert from "node:assert/strict";
import {pathToFileURL} from "node:url";
import {createHash} from "node:crypto";
// Uso: node/bun prueba-loader.mjs pi/omp <raiz-paquete-harness> <paquete-skill>
const [harness, installation, packetInput] = process.argv.slice(2);
assert.ok(["pi","omp"].includes(harness) && installation && packetInput);
const source = fs.realpathSync(installation), packet = fs.realpathSync(packetInput);
const fixture = fs.mkdtempSync(path.join(os.tmpdir(),"gm-r22-casos-"));
fs.chmodSync(fixture,0o700);
const fixtureUser=path.join(fixture,"usuario"), agent=path.join(fixtureUser,"agent");
const project=path.join(fixtureUser,"proyecto"), cwd=path.join(project,"subdir");
const nativeUser=path.join(agent,"skills"), nativeProject=path.join(project,"."+harness,"skills");
const agentsUser=path.join(fixtureUser,".agents","skills");
const agentsProject=path.join(project,".agents","skills"), agentProject=path.join(project,".agent","skills");
process.env.PI_CODING_AGENT_DIR=agent;
delete process.env.OMP_PROFILE; delete process.env.PI_PROFILE;
globalThis.fetch=()=>{throw new Error("Red deshabilitada en esta prueba");};
fs.mkdirSync(cwd,{recursive:true}); fs.mkdirSync(path.join(project,".git"));
const roots=[nativeUser,nativeProject,agentsUser,agentsProject,agentProject];
for(const dir of roots){fs.mkdirSync(dir,{recursive:true});fs.cpSync(packet,path.join(dir,"gamemaker-biblioteca"),{recursive:true,dereference:true});}
const write=(dir,name,text)=>{const dest=path.join(dir,name);fs.mkdirSync(dest,{recursive:true});fs.writeFileSync(path.join(dest,"SKILL.md"),text);};
for(const dir of [nativeUser,nativeProject]){
  write(dir,"sin-descripcion","---\nname: sin-descripcion\n---\n# Control\n");
  write(dir,"yaml-roto","---\nname: yaml-roto\ndescription: [sin cierre\n---\n# Control\n");
  write(dir,"anidado/interno","---\nname: interno\ndescription: Control.\n---\n# Control\n");
  write(dir,"desactivado","---\nname: desactivado\ndescription: Control.\nenabled: false\n---\n# Control\n");
  write(dir,"oculto","---\nname: oculto\ndescription: Control.\ndisable-model-invocation: true\n---\n# Control\n");
  fs.symlinkSync(path.join(dir,"gamemaker-biblioteca"),path.join(dir,"alias-paquete"),"dir");
}
let checks=0;const check=value=>{assert.ok(value);checks++;};
const imported=file=>import(pathToFileURL(path.join(source,file)));
let findings, sources;
try{
  if(harness==="pi"){
    const m=await imported("dist/core/skills.js"), c=await imported("dist/config.js");
    check(c.getAgentDir()===agent);
    const r=m.loadSkills({cwd:project,agentDir:agent,skillPaths:[],includeDefaults:true});
    const onlyUser=m.loadSkills({cwd,agentDir:agent,skillPaths:[],includeDefaults:true});
    check(onlyUser.skills.filter(s=>s.name==="gamemaker-biblioteca").length===1 &&
      !onlyUser.diagnostics.some(d=>d.type==="collision"&&d.collision?.name==="gamemaker-biblioteca"));
    check(!r.skills.some(s=>["sin-descripcion","yaml-roto"].includes(s.name)));
    check(r.skills.some(s=>s.name==="interno"));
    check(r.skills.some(s=>s.name==="desactivado"));
    check(r.skills.find(s=>s.name==="oculto").disableModelInvocation===true);
    check(!m.formatSkillsForPrompt(r.skills).includes("<name>oculto</name>"));
    const p=m.loadSkills({cwd:project,agentDir:path.join(project,"vacio"),skillPaths:[],includeDefaults:true});
    check(p.skills.some(s=>s.name==="gamemaker-biblioteca"));
    const child=m.loadSkills({cwd,agentDir:path.join(project,"vacio"),skillPaths:[],includeDefaults:true});
    check(!child.skills.some(s=>s.name==="gamemaker-biblioteca"));
    for(const dir of [agentsUser,agentsProject]){check(m.loadSkillsFromDir({dir,source:"path"}).skills.some(s=>s.name==="gamemaker-biblioteca"));}
    findings={userAndProject:true,nativeAncestor:false,agentsExplicitPaths:true,recursive:true,symlinkDedup:true,enabledFieldIgnored:true,hiddenExcludedFromPrompt:true};
    sources=["dist/core/skills.js","dist/config.js","dist/core/package-manager.js"];
  }else{
    const utils=await imported("../pi-utils/src/dirs.ts");check(utils.getAgentDir()===agent);
    await imported("src/discovery/builtin.ts");await imported("src/discovery/agents.ts");
    const {getCapability}=await imported("src/capability/index.ts");
    const ctx={cwd,home:fixtureUser,repoRoot:project}, providers=getCapability("skills").providers;
    const native=await providers.find(p=>p.id==="native").load(ctx);
    check(native.items.filter(s=>s.name==="gamemaker-biblioteca"&&s.level==="user").length===2);
    check(native.items.filter(s=>s.name==="gamemaker-biblioteca"&&s.level==="project").length===2);
    check(!native.items.some(s=>["sin-descripcion","interno","desactivado"].includes(s.name)));
    check(native.items.some(s=>s.name==="oculto"));
    check(native.items.some(s=>s.name==="yaml-roto"));
    const agents=await providers.find(p=>p.id==="agents").load(ctx);
    check(agents.items.some(s=>s.name==="gamemaker-biblioteca"&&s.level==="user"));
    check(agents.items.filter(s=>s.name==="gamemaker-biblioteca"&&s.level==="project").length===2);
    check(native.items.find(s=>s.name==="gamemaker-biblioteca").content.includes("GameMaker"));
    findings={userAndProject:true,nativeAncestor:true,agentsUserAndProject:true,singularAgentAlias:true,recursive:false,symlinksFollowedBeforeDedup:true,enabledFalseExcluded:true,malformedScalarAccepted:true};
    sources=["src/discovery/builtin.ts","src/discovery/agents.ts","src/discovery/helpers.ts","../pi-utils/src/dirs.ts","../pi-utils/src/frontmatter.ts"];
  }
  const hash=file=>createHash("sha256").update(fs.readFileSync(file)).digest("hex");
  const fingerprint=Object.fromEntries(sources.map(file=>[file,hash(path.join(source,file))]));
  const walk=(dir,prefix="")=>fs.readdirSync(dir).flatMap(name=>{
    const relative=prefix?prefix+"/"+name:name;
    const absolute=path.join(dir,name),stat=fs.statSync(absolute);
    if(stat.isDirectory())return walk(absolute,relative);
    assert.ok(stat.isFile(),"Entrada no regular en el paquete: "+relative);
    return [relative];
  }).sort();
  const packetFiles=walk(packet);
  assert.ok(packetFiles.includes("SKILL.md"));
  for(const destination of roots){
    const copy=path.join(destination,"gamemaker-biblioteca");
    check(JSON.stringify(walk(copy))===JSON.stringify(packetFiles));
    for(const file of packetFiles)check(hash(path.join(packet,file))===hash(path.join(copy,file)));
  }
  console.log(JSON.stringify({harness,version:JSON.parse(fs.readFileSync(path.join(source,"package.json"))).version,platform:process.platform,runtime:harness==="omp"?{bun:process.versions.bun,nodeCompatibility:process.version}:{node:process.version},checks,findings,fingerprint,packetFiles},null,2));
}finally{fs.rmSync(fixture,{recursive:true,force:true});}
```

## 5. Huellas y límites de la evidencia

Las siguientes huellas corresponden al código **instalado y probado**, no a una
afirmación de identidad con `main` de GitHub. Las URLs primarias de este informe se
consultaron el 11-10-2026; una rama móvil puede cambiar. La consulta de metadatos del
registro devolvió las versiones indicadas, pero no un `gitHead`, por lo que no se
atribuye un commit upstream exacto a esos binarios.

| Fuente instalada | SHA-256 |
|---|---|
| Pi `dist/core/skills.js` | `0e20ec500ed9783d5b01b5399e6600134fc3fdd10e6dc46c9113bc01565c9aa5` |
| Pi `dist/config.js` | `b53418ca3bc54b70e18ccb192eb471696f5211c5aa2e80d68fe6fe3851ff23ae` |
| Pi `dist/core/package-manager.js` | `cfd718348caadc3b74df206e9af417afb9f409cdd7b508891eb7608c21fade80` |
| OMP `src/discovery/builtin.ts` | `957a5a641b602917cdb817139c3926ca9a533bd39375801f026c84bf10900ed5` |
| OMP `src/discovery/agents.ts` | `976360027cee582030f2ec4871544821d8b66c25e8687ea461f4bee56aacb92e` |
| OMP `src/discovery/helpers.ts` | `889ce596b0245d50a92ebca18deafaf6fc35e070b2de4d8cd928b7fb3ebccff4` |
| OMP utilidades `src/dirs.ts` | `2fcd846203851bbc3e52a63c93a7d6cb87e8d1e1111fcd7dec55faf41d5dbb24` |
| OMP utilidades `src/frontmatter.ts` | `f1da3fcc7d458248ec772ccc85e4f1235583fd33d01737598164e2671f1b0415` |

Estas pruebas acreditan la lectura del paquete y las entradas ejercitadas en macOS.
No certifican otros sistemas, versiones futuras, paquetes monolíticos sin esos módulos,
la selección automática por un modelo, la calidad de un juego, la integridad de una
instalación global ni una sesión real con proveedores. Las instrucciones propias de
la skill y sus herramientas GameMaker no se ejecutaron en esta investigación.
