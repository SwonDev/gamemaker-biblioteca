#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sincronizar-skill.py — mantiene la skill `gamemaker-biblioteca` pegada al disco.

La skill (en `_indice/skills/gamemaker-biblioteca/`) es lo que los CLI de IA cargan cuando
desarrollan con GameMaker desde CUALQUIER proyecto. Si cita un documento que se renombró, el
agente sigue una pista falsa sin enterarse. Este script lo impide:

  1. Regenera `references/indice-documentos.md` a partir de MAPA.json: todas las carpetas
     con su criterio de uso y todos los documentos con su título. Nunca se edita a mano.
  2. Comprueba que cada ruta de la biblioteca citada en SKILL.md y en references/*.md
     existe de verdad.
  3. Regenera `AGENTS.md` (mismo directorio que SKILL.md) derivándolo del cuerpo real de
     SKILL.md. Existe para los CLI de IA que no soportan un directorio de skills en formato
     `SKILL.md` y solo leen `AGENTS.md` en la raíz de un proyecto (ver `instalar.sh`). Nunca
     se edita a mano: si SKILL.md cambia, este archivo cambia solo en el siguiente `actualizar.py`.
  4. Informa de si los enlaces simbólicos de ~/.claude/skills, ~/.codex/skills, ~/.agents/skills,
     ~/.qwen/skills, ~/.kimi-code/skills y ~/.config/opencode/skills apuntan a esta carpeta
     (informativo: no falla, pero lo dice).

Lo llama actualizar.py e instalar.sh (antes de copiar la skill, para que la copia ya incluya
el AGENTS.md al día). Sale con 0 si no hay rutas rotas.
"""
import os, re, sys, json

IND = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(IND)
SKILL = os.path.join(IND, "skills", "gamemaker-biblioteca")
REFS = os.path.join(SKILL, "references")
GENERADO = os.path.join(REFS, "indice-documentos.md")
AGENTS_GENERADO = os.path.join(SKILL, "AGENTS.md")

# Una ruta de la biblioteca citada entre acentos graves: empieza por «NN - », por un
# archivo de la raíz o por _indice/. Se admite «NN/…» abreviado solo en prosa, no aquí.
RUTA = re.compile(r"`((?:\d\d - |_indice/|README\.md|RUTA\.md|AGENTS\.md|CLAUDE\.md)[^`]*)`")

# «09 - Manual oficial» y «11 - Código descargado» son opcionales por diseño (ver
# verificar-enlaces.py): una ruta de la skill que cae dentro de una de las dos y no está
# instalada en esta máquina no es una ruta rota, es contenido pendiente de reconstruir.
CARPETAS_OPCIONALES = ("09 - Manual oficial", "11 - Código descargado")


def _carpeta_instalada(nombre):
    ruta = os.path.join(RAIZ, nombre)
    if not os.path.isdir(ruta):
        return False
    return bool([e for e in os.listdir(ruta) if e not in ("_RUTAS.json", "_CATALOGO.md")])


def generar_indice():
    m = json.load(open(os.path.join(IND, "MAPA.json"), encoding="utf-8"))
    v = m.get("version_referencia", {})
    out = []
    out.append("# Índice de documentos de la biblioteca\n")
    out.append("> **Generado por `_indice/sincronizar-skill.py` desde `MAPA.json`. No lo edites a mano:**\n"
               "> se reescribe en cada `python3 _indice/actualizar.py`.\n")
    out.append(f"Versión de referencia: LTS {v.get('lts', '?')} · Beta {v.get('beta', '?')} · "
               f"GMRT {v.get('gmrt', '?')}.\n")
    # La raíz NO se escribe a fuego: este archivo viaja a otros CLI y a quien clone el
    # repositorio, donde esa ruta no existe. Se usa la misma convención que la skill.
    out.append("Todas las rutas son relativas a la raíz de la biblioteca, la que resuelve "
               "`$BIB` (ver la cabecera de la skill).\n")
    if m.get("puntos_de_entrada"):
        out.append("\n## Puntos de entrada\n")
        for k, val in m["puntos_de_entrada"].items():
            # `val` es un dict con titulo/proposito/usar_cuando/nota_para_agentes. Sin
            # formatearlo salía el repr() de Python —legible a duras penas y feo— en un
            # archivo pensado para que lo lea un agente. Se compone como prosa.
            if isinstance(val, dict):
                linea = f"- `{k}` — **{val.get('titulo', '')}**"
                if val.get("proposito"):
                    linea += f"\n  {val['proposito']}"
                if val.get("usar_cuando"):
                    casos = "; ".join(val["usar_cuando"])
                    linea += f"\n  *Úsalo cuando:* {casos}."
                if val.get("nota_para_agentes"):
                    linea += f"\n  *Para el agente:* {val['nota_para_agentes']}"
                out.append(linea)
            else:
                out.append(f"- `{k}` — {val}")
        out.append("")
    for c in m.get("carpetas", []):
        out.append(f"\n## `{c.get('ruta')}` — {c.get('titulo', '')}\n")
        if c.get("proposito"):
            out.append(c["proposito"] + "\n")
        if c.get("usar_cuando"):
            out.append("**Usar cuando:** " + " · ".join(c["usar_cuando"]) + "\n")
        if c.get("no_usar_para"):
            out.append("**No usar para:** " + " · ".join(c["no_usar_para"]) + "\n")
        docs = c.get("documentos", [])
        if docs:
            for d in docs:
                out.append(f"- `{d['ruta']}` — {d.get('titulo', '')}")
        elif c.get("nota"):
            out.append(c["nota"])
        out.append("")
    os.makedirs(REFS, exist_ok=True)
    open(GENERADO, "w", encoding="utf-8").write("\n".join(out).rstrip() + "\n")
    return sum(len(c.get("documentos", [])) for c in m.get("carpetas", []))


def _anclar_enlaces_relativos(cuerpo):
    """Corrige, SOLO en la copia que recibe AGENTS.md, las rutas que se rompen al viajar solas.

    La cabecera de AGENTS.md invita a copiarlo o enlazarlo **suelto** como `AGENTS.md` en la
    raíz de cualquier proyecto de GameMaker — sin la carpeta `references/` al lado. Pero el
    cuerpo de SKILL.md cita `references/mapa-disciplinas.md` y `references/indice-
    documentos.md` con rutas relativas a la propia carpeta de la skill (como enlace Markdown
    `[...](...)` dos veces, y suelta entre comillas simples una tercera, en la tabla «Qué leer
    según la tarea»): correctas ahí (siempre viajan junto a `references/`), rotas en cuanto
    AGENTS.md se copia solo. Se ancla aquí a `$BIB` — la misma variable que ya resuelve el
    resto del documento —, con una única pasada por regex que coge las tres formas (y
    cualquier otra que se añada más adelante) para no depender de una lista cerrada de
    nombres. Se añade además una frase que explica el patrón `NN/MM` que el resto del texto
    usa en forma abreviada (`13/28`, `04/00`, `12/09`…), para que un agente que solo tenga
    este archivo delante sepa completar esas rutas él mismo.
    """
    ruta_skill_desde_raiz = os.path.relpath(SKILL, RAIZ).replace(os.sep, "/")
    base = f"$BIB/{ruta_skill_desde_raiz}/references"

    # 1) Enlace Markdown: [`references/x.md`](references/x.md) → `$BIB/.../references/x.md`
    cuerpo, n_enlaces = re.subn(
        r"\[`references/([\w.-]+\.md)`\]\(references/\1\)",
        lambda m: f"`{base}/{m.group(1)}`",
        cuerpo,
    )
    # 2) Mención suelta entre comillas simples: `references/x.md` → `$BIB/.../references/x.md`
    #    (se aplica DESPUÉS del paso 1: si fuera antes, rompería el enlace Markdown a medias,
    #    porque `references/x.md` es también una subcadena literal de ese enlace).
    cuerpo, n_sueltas = re.subn(
        r"`references/([\w.-]+\.md)`",
        lambda m: f"`{base}/{m.group(1)}`",
        cuerpo,
    )
    if n_enlaces == 0 and n_sueltas == 0:
        print("  ⚠ generar_agents_md: no encuentro ninguna cita a references/*.md en SKILL.md "
              "(¿cambió el texto?); AGENTS.md se genera sin corregir rutas.")

    nota_anclada = f"`{base}/indice-documentos.md`."
    if nota_anclada in cuerpo:
        nota = (" Las rutas abreviadas de este documento (`13/28`, `04/00`, `12/09`…) siguen "
                "el mismo patrón: `$BIB/NN - <carpeta>/MM - <archivo>.md` — primero la carpeta "
                "por su número, luego el archivo dentro de ella por el suyo.")
        cuerpo = cuerpo.replace(nota_anclada, nota_anclada + nota, 1)
    return cuerpo


def generar_agents_md():
    """Deriva AGENTS.md del cuerpo real de SKILL.md — nunca se escribe a mano.

    Existe para los CLI de IA que solo entienden AGENTS.md en la raíz de un proyecto y no
    tienen un directorio de skills en formato SKILL.md (ver la investigación citada en
    `instalar.sh`). El contenido es el mismo: se copia el cuerpo tal cual, sin reescribirlo,
    con UNA excepción deliberada — ver `_anclar_enlaces_relativos()` — para que no pueda
    desincronizarse de lo que ya dice la skill.
    """
    ruta_skill = os.path.join(SKILL, "SKILL.md")
    txt = open(ruta_skill, encoding="utf-8").read()
    # SKILL.md empieza por "---\n<frontmatter YAML>\n---\n<cuerpo>". Se separa por el
    # delimitador de cierre del frontmatter, no por el primero (que abre el bloque).
    partes = txt.split("---", 2)
    if len(partes) < 3:
        return None  # SKILL.md sin frontmatter: no debería pasar, no se genera nada falso
    frontmatter, cuerpo = partes[1], partes[2]
    cuerpo = _anclar_enlaces_relativos(cuerpo)

    # El frontmatter tiene que ser YAML VÁLIDO SEGÚN LA ESPECIFICACIÓN, no solo «válido para
    # Claude Code». Kimi Code usa un parser estricto y rechazaba la skill entera —sin cargarla—
    # porque la descripción sin comillas contenía «: » en mitad del valor, que en YAML abre un
    # mapa. Claude Code y opencode lo toleran; kimi no. Como el fallo es silencioso en unos CLI
    # y fatal en otro, se comprueba aquí: es el único punto por el que pasa toda edición.
    try:
        import yaml  # PyYAML viene con el sistema en este entorno
        datos = yaml.safe_load(frontmatter)
        if not isinstance(datos, dict) or "description" not in datos:
            print("  ✗ El frontmatter de SKILL.md no tiene 'description'.")
            return None
        descripcion = str(datos["description"])
    except ImportError:
        # Sin PyYAML no se puede validar; se avisa y se sigue con el método simple.
        print("  ⚠ Sin PyYAML: no se ha podido validar el frontmatter de SKILL.md.")
        descripcion = ""
        for linea in frontmatter.splitlines():
            if linea.strip().startswith("description:"):
                descripcion = linea.split(":", 1)[1].strip().strip('"')
                break
    except Exception as e:
        print(f"  ✗ El frontmatter de SKILL.md NO es YAML válido: {e}")
        print("    Kimi Code y otros parsers estrictos rechazarán la skill entera.")
        print("    Suele ser una descripción sin comillas que contiene «: ». Entrecomíllala.")
        return None
    out = [
        "# AGENTS.md — Biblioteca GameMaker (generado desde la skill)\n",
        "> **Generado por `_indice/sincronizar-skill.py` a partir del cuerpo real de**\n"
        "> **`SKILL.md`. No lo edites a mano:** se reescribe en cada "
        "`python3 _indice/actualizar.py`\n"
        "> o `./instalar.sh`. Existe para los CLI de IA que solo leen `AGENTS.md` en la raíz\n"
        "> de un proyecto y no tienen un directorio de skills en formato `SKILL.md` — copia\n"
        "> este archivo (o enlázalo) como `AGENTS.md` en la raíz de tu proyecto de GameMaker.\n"
        "> Si tu CLI sí lee skills, usa directamente la carpeta\n"
        "> `_indice/skills/gamemaker-biblioteca/` — no hace falta este archivo.\n",
    ]
    if descripcion:
        out.append(f"**Cuándo aplica esto:** {descripcion}\n")
    out.append(cuerpo.strip() + "\n")
    with open(AGENTS_GENERADO, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return AGENTS_GENERADO


def rutas_rotas():
    rotas = []
    archivos = [os.path.join(SKILL, "SKILL.md")]
    if os.path.isdir(REFS):
        archivos += [os.path.join(REFS, f) for f in sorted(os.listdir(REFS))
                     if f.endswith(".md") and f != os.path.basename(GENERADO)]
    for fp in archivos:
        if not os.path.isfile(fp):
            continue
        txt = open(fp, encoding="utf-8").read()
        for m in RUTA.finditer(txt):
            r = m.group(1).split("#")[0].rstrip("/")
            if r.endswith("…") or "…" in r:
                continue                      # una ruta abreviada a propósito en prosa
            if os.path.exists(os.path.join(RAIZ, r)):
                continue
            carpeta = next((c for c in CARPETAS_OPCIONALES
                            if r == c or r.startswith(c + "/")), None)
            if carpeta and not _carpeta_instalada(carpeta):
                continue                      # carpeta opcional no instalada: no es un roto
            rotas.append((os.path.relpath(fp, RAIZ), r))
    return rotas


def estado_enlaces():
    """¿Qué CLI ven esta skill ahora mismo? Solo informa (ver instalar.sh para la instalación)."""
    sitios = {
        "Claude Code": os.path.expanduser("~/.claude/skills/gamemaker-biblioteca"),
        "Codex (pool)": os.path.expanduser("~/.codex/skills-pool/gamemaker-biblioteca"),
        "Codex (activa)": os.path.expanduser("~/.codex/skills/gamemaker-biblioteca"),
        "Genérico ~/.agents (Codex canónico · Copilot CLI · Gemini CLI · Cursor CLI · Kimi Code)":
            os.path.expanduser("~/.agents/skills/gamemaker-biblioteca"),
        "opencode": os.path.expanduser("~/.config/opencode/skills/gamemaker-biblioteca"),
        "Qwen Code": os.path.expanduser("~/.qwen/skills/gamemaker-biblioteca"),
        "Kimi Code CLI": os.path.expanduser("~/.kimi-code/skills/gamemaker-biblioteca"),
        "Gemini CLI": os.path.expanduser("~/.gemini/skills/gamemaker-biblioteca"),
        "GitHub Copilot CLI": os.path.expanduser("~/.copilot/skills/gamemaker-biblioteca"),
        "Cursor CLI": os.path.expanduser("~/.cursor/skills/gamemaker-biblioteca"),
        "Cline": os.path.expanduser("~/.cline/skills/gamemaker-biblioteca"),
    }
    propio = os.path.join(SKILL, "SKILL.md")
    txt_propio = open(propio, encoding="utf-8").read() if os.path.isfile(propio) else None
    lineas = []
    for nombre, ruta in sitios.items():
        if not os.path.lexists(ruta):
            lineas.append(f"  ✗ {nombre}: falta {ruta}")
            continue
        real = os.path.realpath(ruta)
        skill_md = os.path.join(real, "SKILL.md")
        if not os.path.isfile(skill_md):
            lineas.append(f"  ⚠ {nombre}: {ruta} existe pero no tiene SKILL.md")
            continue
        # Symlink → identidad de ruta. Copia (cp -R) → mismo contenido. Ambas cuentan como
        # "al día"; solo se avisa si de verdad es otra cosa (una skill distinta con ese nombre).
        es_symlink = os.path.islink(ruta)
        al_dia = os.path.samefile(real, SKILL) if es_symlink else (
            txt_propio is not None and open(skill_md, encoding="utf-8").read() == txt_propio)
        if al_dia:
            modo = "enlace →" if es_symlink else "copia al día,"
            lineas.append(f"  ✓ {nombre}: {ruta} ({modo} esta carpeta)")
        else:
            lineas.append(f"  ⚠ {nombre}: {ruta} no coincide con esta carpeta (reinstala con ./instalar.sh)")
    return lineas


def main():
    if not os.path.isfile(os.path.join(SKILL, "SKILL.md")):
        print(f"No hay skill en {SKILL}: nada que sincronizar.")
        return 0
    n = generar_indice()
    print(f"references/indice-documentos.md regenerado: {n} documentos.")
    agents = generar_agents_md()
    if agents:
        print(f"AGENTS.md regenerado desde SKILL.md: {os.path.relpath(agents, RAIZ)}")
    rotas = rutas_rotas()
    if rotas:
        print(f"✗ {len(rotas)} rutas citadas por la skill no existen:")
        for doc, r in rotas:
            print(f"    {doc}\n        → {r}")
    else:
        print("Todas las rutas que cita la skill existen.")
    for l in estado_enlaces():
        print(l)
    return 1 if rotas else 0


if __name__ == "__main__":
    sys.exit(main())
