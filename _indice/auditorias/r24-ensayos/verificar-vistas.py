#!/usr/bin/env python3
"""Verifica vistas publicables y, con --custodia, sus originales privados."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def sha(datos):
    return hashlib.sha256(datos).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--custodia", type=Path)
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    cargar = lambda ruta: json.loads(ruta.read_text(encoding="utf-8"))
    vistas = cargar(base / "vistas-para-publicar.json")
    originales = {r["archivo"]: r for r in cargar(base / "huellas-originales.json")["archivos"]}
    privados = 0
    if args.custodia:
        custodia = cargar(args.custodia / "custodia.json")
        raiz = custodia["raiz_original"].split("/_indice/auditorias/r24-ensayos")[0]
    for r in vistas["archivos"] + vistas["nuevos"]:
        datos = (base / r["archivo"]).read_bytes()
        assert sha(datos) == r["vista_sha256"] and len(datos) == r["bytes_vista"], r["archivo"]
        if "original_sha256" not in r:
            continue
        assert originales[r["archivo"]]["original_sha256"] == r["original_sha256"], r["archivo"]
        if args.custodia:
            f = (args.custodia / "r24-ensayos-skill.md" if r["archivo"] == "../r24-ensayos-skill.md"
                 else args.custodia / "r24-ensayos" / r["archivo"])
            bruto = f.read_bytes()
            assert sha(bruto) == r["original_sha256"] and len(bruto) == r["bytes_original"], r["archivo"]
            privados += 1
            texto = bruto.decode("utf-8").replace(raiz, "<RAIZ_BIBLIOTECA>")
            texto = texto.replace(custodia["custodia"], "<CUSTODIA_PRIVADA>")
            if r["transformacion"] in ("sin cambios", "solo prefijos"):
                assert datos == texto.encode("utf-8"), r["archivo"]
            elif r["transformacion"] in ("prefijos y atribución de prompt", "control con procedencia pública"):
                actual = json.loads(datos)
                actual.pop("vista_publica" if r["transformacion"] == "prefijos y atribución de prompt" else "vistas_publicas")
                assert actual == json.loads(texto), r["archivo"]
    for meta, prompt in [("metadata-control.json", "prompt-control.txt"), ("metadata-r49.json", "prompt-r49.txt"),
                         ("metadata-r49-final.json", "prompt-r49-final.txt")]:
        m = cargar(base / meta)
        assert m["prompt_sha256"] == originales[prompt]["original_sha256"], meta
        assert m["vista_publica"]["prompt_vista_sha256"] == sha((base / prompt).read_bytes()), meta
    for ruta in [x for x in base.rglob("*") if x.is_file()] + [base.parent / "r24-ensayos-skill.md"]:
        assert not re.search(rb"/(?:Users/|var/folders/)", ruta.read_bytes()), ruta.name
    print(json.dumps({"resultado": "APTO", "vistas_de_originales": len(vistas["archivos"]),
                      "artefactos_nuevos": len(vistas["nuevos"]), "brutos_privados_contrastados": privados,
                      "rutas_personales": 0, "prompts": "huellas originales y vistas separadas",
                      "limite": "Sin --custodia se verifica la vista y su atribución; no se accede al bruto."},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
