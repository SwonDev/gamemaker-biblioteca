#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sintetiza los WAV de «Enjambre». Sin descargar nada, sin dependencias.

Un sonido vacío es peor que ninguno: `13 · 09` lo dice y el validador de la biblioteca
lo comprueba. Aquí cada WAV lleva muestras de verdad —envolvente, ruido y armónicos—,
no medio segundo de silencio con nombre bonito.
"""
import math
import os
import random
import struct
import sys
import wave

SALIDA = sys.argv[1] if len(sys.argv) > 1 else "sonido"
os.makedirs(SALIDA, exist_ok=True)
SR = 44100


def escribir(nombre, muestras):
    ruta = os.path.join(SALIDA, nombre + ".wav")
    with wave.open(ruta, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, int(m * 32767))))
                              for m in muestras))
    return ruta


def env(i, n, ataque=0.01, caida=0.9):
    """Envolvente: sin ella, un tono empieza y acaba con un chasquido."""
    a = int(n * ataque)
    if i < a:
        return i / max(a, 1)
    return max(0.0, (1 - (i - a) / max(n - a, 1)) ** (1 / max(caida, 0.05)))


def disparo():
    n = int(SR * 0.10)
    out = []
    for i in range(n):
        t = i / SR
        f = 900 * math.exp(-14 * t) + 180
        s = math.sin(2 * math.pi * f * t) * 0.55
        s += math.sin(2 * math.pi * f * 2.01 * t) * 0.18
        s += (random.random() * 2 - 1) * 0.10 * math.exp(-30 * t)
        out.append(s * env(i, n, 0.004, 0.55))
    return out


def impacto():
    n = int(SR * 0.14)
    out = []
    for i in range(n):
        t = i / SR
        s = (random.random() * 2 - 1) * 0.7
        s += math.sin(2 * math.pi * (220 * math.exp(-9 * t) + 60) * t) * 0.5
        out.append(s * env(i, n, 0.002, 0.35))
    return out


def estallido():
    n = int(SR * 0.55)
    out = []
    for i in range(n):
        t = i / SR
        ruido = (random.random() * 2 - 1)
        grave = math.sin(2 * math.pi * (110 * math.exp(-3.5 * t) + 32) * t)
        s = ruido * 0.55 * math.exp(-4.5 * t) + grave * 0.65 * math.exp(-2.2 * t)
        out.append(s * env(i, n, 0.002, 0.30))
    return out


def recoger():
    """Dos notas ascendentes: la señal universal de «esto es bueno»."""
    n = int(SR * 0.22)
    out = []
    for i in range(n):
        t = i / SR
        f = 660 if t < 0.08 else 990
        s = math.sin(2 * math.pi * f * t) * 0.5 + math.sin(2 * math.pi * f * 2 * t) * 0.15
        out.append(s * env(i, n, 0.01, 0.6))
    return out


def herido():
    n = int(SR * 0.45)
    out = []
    for i in range(n):
        t = i / SR
        f = 400 * math.exp(-2.5 * t) + 70
        s = math.sin(2 * math.pi * f * t) * 0.6
        s += (random.random() * 2 - 1) * 0.25 * math.exp(-6 * t)
        out.append(s * env(i, n, 0.003, 0.4))
    return out


def oleada():
    n = int(SR * 0.7)
    out = []
    notas = [392.0, 523.25, 659.25]
    for i in range(n):
        t = i / SR
        k = min(int(t / 0.2), 2)
        s = 0.0
        for h, amp in ((1, 0.5), (2, 0.2), (3, 0.08)):
            s += math.sin(2 * math.pi * notas[k] * h * t) * amp
        out.append(s * env(i, n, 0.01, 0.5))
    return out


def clic():
    n = int(SR * 0.05)
    return [math.sin(2 * math.pi * 1200 * (i / SR)) * 0.35 * env(i, n, 0.002, 0.3)
            for i in range(n)]


def musica():
    """Un bucle de 8 s: bajo, arpegio y pulso. No es una banda sonora, pero es música
    de verdad y el juego deja de sonar a vacío."""
    dur = 8.0
    n = int(SR * dur)
    bajo = [110.0, 110.0, 146.83, 130.81]
    arp = [440.0, 523.25, 659.25, 523.25, 587.33, 493.88, 440.0, 392.0]
    out = []
    for i in range(n):
        t = i / SR
        compas = int(t / 2.0) % 4
        s = math.sin(2 * math.pi * bajo[compas] * t) * 0.22
        s += math.sin(2 * math.pi * bajo[compas] * 0.5 * t) * 0.10
        paso = int(t / 0.25) % 8
        tp = (t % 0.25) / 0.25
        s += math.sin(2 * math.pi * arp[paso] * t) * 0.13 * (1 - tp) ** 1.5
        if (t % 0.5) < 0.06:                       # pulso
            s += (random.random() * 2 - 1) * 0.18 * (1 - (t % 0.5) / 0.06)
        # entrada y salida suaves para que el bucle no chasque al empalmar
        borde = min(1.0, t / 0.05, (dur - t) / 0.05)
        out.append(s * borde)
    return out


if __name__ == "__main__":
    piezas = {"snd_disparo": disparo(), "snd_impacto": impacto(), "snd_estallido": estallido(),
              "snd_recoger": recoger(), "snd_herido": herido(), "snd_oleada": oleada(),
              "snd_clic": clic(), "snd_musica": musica()}
    for nombre, m in piezas.items():
        r = escribir(nombre, m)
        print("  %-16s %6.2f s  %8d bytes" % (nombre, len(m) / SR, os.path.getsize(r)))
    print("%d WAV generados en %s/" % (len(piezas), SALIDA))
