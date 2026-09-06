#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sincronizar-skill.py — mantiene la skill `gamemaker-biblioteca` pegada al disco.

La skill (en `_indice/skills/gamemaker-biblioteca/`) es lo que Claude Code y Codex cargan
cuando desarrollan con GameMaker desde CUALQUIER proyecto. Si cita un documento que se
renombró, el agente sigue una pista falsa sin enterarse. Este script lo impide:

  1. Regenera `references/indice-documentos.md` a partir de MAPA.json: todas las carpetas
     con su criterio de uso y todos los documentos con su título. Nunca se edita a mano.
  2. Comprueba que cada ruta de la biblioteca citada en SKILL.md y en references/*.md
     existe de verdad.
  3. Informa de si los enlaces simbólicos de ~/.claude/skills y ~/.codex/skills apuntan
     a esta carpeta (informativo: no falla, pero lo dice).

Lo llama actualizar.py. Sale con 0 si no hay rutas rotas.
"""
import os, re, sys, json

IND = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(IND)
SKILL = os.path.join(IND, "skills", "gamemaker-biblioteca")
REFS = os.path.join(SKILL, "references")
GENERADO = os.path.join(REFS, "indice-documentos.md")

# Una ruta de la biblioteca citada entre acentos graves: empieza por «NN - », por un
# archivo de la raíz o por _indice/. Se admite «NN/…» abreviado solo en prosa, no aquí.
RUTA = re.compile(r"`((?:\d\d - |_indice/|README\.md|RUTA\.md|AGENTS\.md|CLAUDE\.md)[^`]*)`")


def generar_indice():
    m = json.load(open(os.path.join(IND, "MAPA.json"), encoding="utf-8"))
    v = m.get("version_referencia", {})
    out = []
    out.append("# Índice de documentos de la biblioteca\n")
    out.append("> **Generado por `_indice/sincronizar-skill.py` desde `MAPA.json`. No lo edites a mano:**\n"
               "> se reescribe en cada `python3 _indice/actualizar.py`.\n")
    out.append(f"Versión de referencia: LTS {v.get('lts', '?')} · Beta {v.get('beta', '?')} · "
               f"GMRT {v.get('gmrt', '?')}.\n")
    out.append("Todas las rutas son relativas a la raíz de la biblioteca "
               "(`/Users/adrianpereradelgado/Documents/GameMaker_Aprendizaje`).\n")
    if m.get("puntos_de_entrada"):
        out.append("\n## Puntos de entrada\n")
        for k, val in m["puntos_de_entrada"].items():
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
            if not os.path.exists(os.path.join(RAIZ, r)):
                rotas.append((os.path.relpath(fp, RAIZ), r))
    return rotas


def estado_enlaces():
    """¿Claude Code y Codex ven esta skill? Solo informa."""
    sitios = {
        "Claude Code": os.path.expanduser("~/.claude/skills/gamemaker-biblioteca"),
        "Codex (pool)": os.path.expanduser("~/.codex/skills-pool/gamemaker-biblioteca"),
        "Codex (activa)": os.path.expanduser("~/.codex/skills/gamemaker-biblioteca"),
    }
    lineas = []
    for nombre, ruta in sitios.items():
        if not os.path.lexists(ruta):
            lineas.append(f"  ✗ {nombre}: falta {ruta}")
            continue
        real = os.path.realpath(ruta)
        if os.path.isfile(os.path.join(real, "SKILL.md")) and os.path.samefile(real, SKILL):
            lineas.append(f"  ✓ {nombre}: {ruta} → esta carpeta")
        else:
            lineas.append(f"  ⚠ {nombre}: {ruta} apunta a {real}, no a la skill de la biblioteca")
    return lineas


def main():
    if not os.path.isfile(os.path.join(SKILL, "SKILL.md")):
        print(f"No hay skill en {SKILL}: nada que sincronizar.")
        return 0
    n = generar_indice()
    print(f"references/indice-documentos.md regenerado: {n} documentos.")
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
