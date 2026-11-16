#!/usr/bin/env python3
"""Soundtrack for the RTX 3080 vs RTX 5070 reel: a soft music bed + sound effects,
made to sit under a voiceover. Everything is synthesized with numpy (no licensed audio).

    python3 make_audio.py cues.json full.wav

100 BPM, D major (Dmaj7 - A - Bm7 - Gmaj7). The bed stays out of the voice range;
build.sh sets the final loudness.
"""
import json
import sys
import wave

import numpy as np

SR = 48000
cues = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
DUR = float(cues["duration"])
N = int(DUR * SR)
SEC = cues["sections"]
rng = np.random.default_rng(23)
BEAT = 60.0 / cues["bpm"]
BAR = BEAT * 4


def tarr(n):
    return np.arange(n) / SR


def fft_filter(x, resp):
    X = np.fft.rfft(x, axis=0)
    g = resp(np.fft.rfftfreq(len(x), 1 / SR))
    return np.fft.irfft(X * (g[:, None] if X.ndim == 2 else g), n=len(x), axis=0)


def lp(x, fc, order=2):
    return fft_filter(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))


def hp(x, fc, order=2):
    return fft_filter(x, lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order)))


def onepole_var(x, fc):
    a = 1 - np.exp(-2 * np.pi * np.asarray(fc) / SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s); y[i] = s
    return y


def add(buf, sig, t, gain=1.0, pan=0.0):
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4) * 1.4142, np.sin((pan + 1) * np.pi / 4) * 1.4142
        sig = np.stack([sig * l, sig * r], axis=1)
    i = int(round(t * SR)); s = sig * gain
    if i < 0:
        s, i = s[-i:], 0
    if i >= len(buf):
        return
    j = min(len(buf), i + len(s)); buf[i:j] += s[: j - i]


def saw(f, n, phase=0.0):
    return 2 * ((f * tarr(n) + phase) % 1.0) - 1


def note(name):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    return 440.0 * 2 ** ((names[name[:-1]] + 12 * (int(name[-1]) - 4)) / 12)


def env_ad(n, a, d):
    t = tarr(n); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


# ------------------------------------------------------------------ music
def kick():
    n = int(0.4 * SR); t = tarr(n)
    body = np.sin(2 * np.pi * np.cumsum(52 + 110 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.16)
    return np.tanh((body + hp(rng.standard_normal(n), 1800) * np.exp(-t / 0.003) * 0.35) * 1.5) * 0.8


def snare():
    n = int(0.35 * SR); t = tarr(n)
    nz = lp(hp(lp(rng.standard_normal(n), 4200), 700), 3500) * np.exp(-t / 0.07)
    return (nz * 0.6 + np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04) * 0.4) * 0.7


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); t = tarr(n)
    return hp(rng.standard_normal(n), 8000) * np.exp(-t / (0.08 if open_ else 0.016)) * 0.22


def keys(freqs, dur):
    n = int(dur * SR); t = tarr(n); x = np.zeros(n)
    for f in freqs:
        x += np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.3)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    env = np.minimum(1, t / 0.01) * (0.35 + 0.65 * np.exp(-t / 0.9)) * np.clip((dur - t) / 0.2, 0, 1)
    return np.stack([x * env * trem, x * env * (2 - trem)], 1) * 0.045


def pad(freqs, dur):
    n = int(dur * SR); t = tarr(n); L = np.zeros(n); R = np.zeros(n)
    for f in freqs:
        L += saw(f * 2 ** (-6 / 1200), n, rng.random()); R += saw(f * 2 ** (6 / 1200), n, rng.random())
    env = np.minimum(1, t / 0.5) * np.clip((dur - t) / 0.5, 0, 1)
    return np.stack([lp(L, 1100) * env, lp(R, 1100) * env], 1) * 0.022


def bass(f, dur):
    n = int(dur * SR); t = tarr(n)
    x = np.sin(2 * np.pi * f * t) + 0.35 * lp(saw(f, n), 600)
    env = np.minimum(1, t / 0.006) * (0.6 + 0.4 * np.exp(-t / 0.2)) * np.clip((dur - t) / 0.03, 0, 1)
    return np.tanh(x * 1.3) * env * 0.32


def pluck(f):
    n = int(0.3 * SR); t = tarr(n)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.06)) * env_ad(n, 0.002, 0.11) * 0.07


# ------------------------------------------------------------------ sfx
def whoosh(dur=0.42):
    n = int(dur * SR); t = tarr(n)
    y = onepole_var(rng.standard_normal(n), 300 + 4800 * np.sin(np.pi * t / dur) ** 2)
    y = y - onepole_var(y, np.full(n, 180.0))
    return y * np.sin(np.pi * t / dur) ** 1.6 * 0.5


def pop(pitch=1.0):
    n = int(0.09 * SR); t = tarr(n)
    f = 820 * pitch * np.exp(-t / 0.025) + 320 * pitch
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.03) * np.minimum(1, t / 0.001) * 0.18


def tick(f=3000.0, g=0.1):
    n = int(0.014 * SR); t = tarr(n)
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.003) * g


def blip(f):
    n = int(0.05 * SR)
    return np.sin(2 * np.pi * f * tarr(n)) * env_ad(n, 0.001, 0.012) * 0.06


def chime(notes=("D6", "F#6", "A6"), gap=0.07, g=0.11):
    n = int((0.9 + gap * len(notes)) * SR); out = np.zeros(n)
    for k, nm in enumerate(notes):
        i = int(k * gap * SR); m = n - i; t = tarr(m); f = note(nm)
        out[i:] += (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2.01 * f * t) * np.exp(-t / 0.1)) * env_ad(m, 0.002, 0.35)
    return out * g


def bell(f):
    n = int(1.8 * SR); t = tarr(n)
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / d) for m, a, d in [(1, 1, 1.1), (2.76, .45, .5), (5.4, .2, .28)])
    return x * np.minimum(1, t / 0.002) * 0.15


def boom(g=1.0):
    n = int(1.6 * SR); t = tarr(n)
    body = np.sin(2 * np.pi * np.cumsum(32 + 60 * np.exp(-t / 0.07)) / SR) * np.exp(-t / 0.45)
    return np.tanh((body * 1.2 + lp(rng.standard_normal(n), 2000) * np.exp(-t / 0.09) * 0.45) * 1.3) * 0.6 * g


# ------------------------------------------------------------------ arrangement
music = np.zeros((N, 2)); sfx = np.zeros((N, 2)); send = np.zeros((N, 2))
CH = [("D2", ("D4", "F#4", "A4", "C#5"), ("A4", "D5", "F#5")),
      ("A1", ("C#4", "E4", "A4", "E5"), ("A4", "C#5", "E5")),
      ("B1", ("D4", "F#4", "A4", "B4"), ("B4", "D5", "F#5")),
      ("G1", ("D4", "F#4", "B4", "G4"), ("G4", "B4", "D5"))]
lift = SEC["wins"][0]
kicks = []
for b in range(int(np.ceil(DUR / BAR))):
    t0 = b * BAR
    root, chord, arp = CH[b % 4]
    if t0 < DUR - 0.5:
        k = keys([note(n) for n in chord], BAR + 0.1)
        add(music, k, t0); add(send, k, t0, gain=0.5)
        add(music, pad([note(n) for n in chord[:3]], BAR + 0.4), t0)
    for s16 in range(16):
        t = t0 + s16 * BEAT / 4
        if t >= DUR - 0.3 or t < 1.2:
            continue
        if s16 in (0, 8) or (s16 == 10 and b % 2):
            add(music, kick(), t, gain=0.85); kicks.append(t)
        if s16 in (4, 12):
            add(music, snare(), t, gain=0.5)
        if s16 % 2 == 0:
            add(music, hat(open_=(s16 == 14 and b % 2 == 1)), t + (0.03 if s16 % 4 == 2 else 0), gain=0.7 if s16 % 4 == 0 else 0.45, pan=0.2)
            add(music, bass(note(root) * (2 if s16 in (6, 14) else 1), BEAT / 2 - 0.02), t)
        if t >= lift and s16 % 2 == 0:      # a little lift for "where it pulls ahead" + the CTA
            p = pluck(note(arp[(s16 // 2) % 3]))
            add(music, p, t, gain=0.45, pan=-0.3 if s16 % 4 else 0.3); add(send, p, t, gain=0.4)
duck = np.ones(N)
for kt in kicks:
    i = int(kt * SR); j = min(N, i + int(0.28 * SR))
    if i < N:
        duck[i:j] = np.minimum(duck[i:j], 1 - 0.35 * np.exp(-tarr(j - i) / 0.09))
music *= duck[:, None]

for i, t in enumerate(cues["whoosh"]):
    add(sfx, whoosh(0.38 + 0.06 * (i % 3)), t - 0.18, gain=0.32, pan=-0.35 if i % 2 else 0.35)
for i, t in enumerate(sorted(set(round(x, 2) for x in cues["pop"]))):
    add(sfx, pop(1.0 + 0.12 * ((i * 5) % 4)), t, gain=0.42, pan=(i % 3 - 1) * 0.25)
for i, t in enumerate(cues["tick"]):
    add(sfx, tick(2600 + 90 * (i % 9)), t, gain=0.9)
for i, t in enumerate(cues["blips"]):
    add(sfx, blip(1200 + 120 * (i % 6)), t, pan=-0.4 if i < 12 else 0.4)
for t in cues["chime"]:
    add(sfx, chime(), t); add(send, chime(), t, gain=0.4)
for t in cues["ding"]:
    for k, f in enumerate((note("E6"), note("A6"))):
        add(sfx, bell(f), t + k * 0.12); add(send, bell(f), t + k * 0.12, gain=0.5)
for t in cues["impacts"]:
    add(sfx, boom(0.8), t, gain=0.32)
for t in cues["endHit"]:
    add(sfx, boom(1.0), t, gain=0.28)

# ------------------------------------------------------------------ reverb + mix
ir_n = int(1.4 * SR); ti = tarr(ir_n)
ir = np.stack([lp(rng.standard_normal(ir_n), 5000), lp(rng.standard_normal(ir_n), 5000)], 1) * np.exp(-ti / 0.38)[:, None]
ir[: int(0.012 * SR)] = 0; ir /= np.sqrt((ir ** 2).sum(0))
nfft = 1 << int(np.ceil(np.log2(N + ir_n)))
wet = np.fft.irfft(np.fft.rfft(send, nfft, axis=0) * np.fft.rfft(ir, nfft, axis=0), nfft, axis=0)[:N]


def compress(x, thr_db=-16.0, ratio=4.0, attack=0.002, release=0.15, block=96):
    """Peak compressor so no single hit jumps out over the voice."""
    mono = np.max(np.abs(x), axis=1); nb = int(np.ceil(len(mono) / block))
    m = np.pad(mono, (0, nb * block - len(mono))).reshape(nb, block).max(axis=1)
    a_att, a_rel = np.exp(-block / (attack * SR)), np.exp(-block / (release * SR))
    env = np.empty(nb); e = 0.0
    for i in range(nb):
        a = a_att if m[i] > e else a_rel; e = a * e + (1 - a) * m[i]; env[i] = e
    thr = 10 ** (thr_db / 20)
    gr = np.where(env > thr, (thr / np.maximum(env, 1e-9)) ** (1 - 1 / ratio), 1.0)
    g = np.convolve(np.repeat(gr, block)[:len(mono)], np.ones(64) / 64, mode="same")
    return x * g[:, None]


def voice_dip(x):
    """Wide ~5 dB dip around 2 kHz, where speech intelligibility lives."""
    return fft_filter(x, lambda f: 1 - 0.45 * np.exp(-(np.log2(np.maximum(f, 1) / 2000.0) ** 2) / (2 * 0.9 ** 2)))


tt = tarr(N)
fade = np.clip((DUR - tt) / 0.6, 0, 1)[:, None]
sfx = compress(sfx / np.max(np.abs(sfx)))
rms = lambda x: np.sqrt(np.mean(x ** 2))
bed = voice_dip(music + wet * 0.5)
bed *= 0.55 * rms(sfx) / rms(bed)
mix = (bed + sfx) * fade
mix = hp(mix, 30, order=1)
mix = fft_filter(mix, lambda f: 1 - 0.4 / (1 + (f / 90.0) ** 4))
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.max(np.abs(mix)) / 0.89
with wave.open(OUT, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print(f"wrote {OUT}: {DUR:.1f}s")
