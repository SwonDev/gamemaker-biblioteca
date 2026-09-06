#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Añade pares EN→ES a la memoria de traducción. Lee JSON por stdin."""
import os, sys, json
SC = os.path.dirname(os.path.abspath(__file__))
TM = os.path.join(SC, "tm_es.json")
tm = json.load(open(TM, encoding="utf-8")) if os.path.exists(TM) else {}
nuevos = json.load(sys.stdin)
antes = len(tm)
tm.update(nuevos)
json.dump(tm, open(TM, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print(f"memoria: {antes} → {len(tm)} unidades (+{len(tm)-antes})")
