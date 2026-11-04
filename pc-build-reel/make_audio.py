#!/usr/bin/env python3
"""Synthesizes the reel's soundtrack (music + sound effects) from the cue list
exported by reel.html (node render.js cues cues.json).

    python3 make_audio.py cues.json out.wav

Everything is generated from scratch with numpy, so there are no licensing
issues with the audio. 120 BPM, A minor (Am - F - C - G).
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
rng = np.random.default_rng(7)

BEAT = 60.0 / cues["bpm"]
BAR = BEAT * 4


def tarr(n):
    return np.arange(n) / SR


def fft_filter(x, resp):
    n = len(x)
    X = np.fft.rfft(x, axis=0)
    g = resp(np.fft.rfftfreq(n, 1 / SR))
    if X.ndim == 2:
        g = g[:, None]
    return np.fft.irfft(X * g, n=n, axis=0)


def lp(x, fc, order=2):
    return fft_filter(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))


def hp(x, fc, order=2):
    return fft_filter(x, lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order)))


def bp(x, f1, f2):
    return hp(lp(x, f2), f1)


def onepole_var(x, fc):
    a = 1 - np.exp(-2 * np.pi * np.asarray(fc) / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s)
        y[i] = s
    return y


def stereo(sig, pan=0.0):
    if sig.ndim == 2:
        return sig
    l, r = np.cos((pan + 1) * np.pi / 4) * 1.4142, np.sin((pan + 1) * np.pi / 4) * 1.4142
    return np.stack([sig * l, sig * r], axis=1)


def add(buf, sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    s = stereo(sig, pan) * gain
    if i < 0:
        s, i = s[-i:], 0
    if i >= len(buf):
        return
    j = min(len(buf), i + len(s))
    buf[i:j] += s[: j - i]


def saw(f, n, phase=0.0):
    return 2 * ((f * tarr(n) + phase) % 1.0) - 1


def note(name):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    n, octv = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (octv - 4)) / 12)


# ------------------------------------------------------------------ instruments
def kick(punch=1.0):
    n = int(0.45 * SR); t = tarr(n)
    f = 54 + 130 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.17)
    click = hp(rng.standard_normal(n), 1800) * np.exp(-t / 0.003) * 0.5
    return np.tanh((body + click) * 1.7 * punch) * 0.85


def clap(bright=1.0):
    n = int(0.4 * SR); t = tarr(n)
    nz = bp(rng.standard_normal(n), 900, 5200 * bright)
    e = np.zeros(n)
    for d in (0.0, 0.010, 0.021):
        m = t >= d
        e[m] += np.exp(-(t[m] - d) / 0.007)
    m = t >= 0.024
    e[m] += 0.7 * np.exp(-(t[m] - 0.024) / 0.10)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.045) * 0.35
    return (nz * e * 0.55 + tone) * 0.9


def hat(open_=False):
    n = int((0.3 if open_ else 0.07) * SR); t = tarr(n)
    return hp(rng.standard_normal(n), 7500) * np.exp(-t / (0.10 if open_ else 0.017)) * 0.32


def bass_note(f, dur, vel=1.0):
    n = int(dur * SR); t = tarr(n)
    x = 0.65 * np.sin(2 * np.pi * f * t) + 0.75 * lp(saw(f, n) + saw(f * 1.005, n, .4), 900)
    env = np.minimum(1, t / 0.005) * (0.55 + 0.45 * np.exp(-t / 0.12))
    rel = np.clip((dur - t) / 0.025, 0, 1)
    return np.tanh(x * 1.4) * env * rel * 0.4 * vel


def pad_chord(freqs, dur, cutoff=1900):
    n = int(dur * SR); t = tarr(n)
    L = np.zeros(n); R = np.zeros(n)
    for f in freqs:
        L += saw(f * 2 ** (-8 / 1200), n, rng.random()) + saw(f * 2 ** (5 / 1200), n, rng.random())
        R += saw(f * 2 ** (8 / 1200), n, rng.random()) + saw(f * 2 ** (-5 / 1200), n, rng.random())
    env = np.minimum(1, t / 0.18) * np.clip((dur - t) / 0.3, 0, 1)
    return np.stack([lp(L, cutoff) * env, lp(R, cutoff) * env], 1) * 0.05


def pluck(f, dur=0.22, cutoff=3200):
    n = int(dur * SR); t = tarr(n)
    x = 0.5 * np.sign(np.sin(2 * np.pi * f * t)) + 0.5 * saw(f * 1.004, n)
    return lp(x, cutoff) * np.exp(-t / 0.075) * np.minimum(1, t / 0.002) * 0.16


def lead_note(f, dur):
    n = int(dur * SR); t = tarr(n)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.25)
    ph = np.cumsum(f * vib) / SR
    x = (2 * (ph % 1) - 1) * 0.6 + 0.4 * (2 * ((ph * 1.006 + .3) % 1) - 1)
    env = np.minimum(1, t / 0.01) * (0.7 + 0.3 * np.exp(-t / 0.2)) * np.clip((dur - t) / 0.05, 0, 1)
    return lp(x, 2600) * env * 0.11


# ------------------------------------------------------------------ sfx
def boom(size=1.0):
    n = int(1.8 * SR); t = tarr(n)
    f = 31 + 70 * np.exp(-t / 0.07)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.5 * size))
    nz = lp(rng.standard_normal(n), 2200) * np.exp(-t / 0.10) * 0.55
    crack = hp(rng.standard_normal(n), 3500) * np.exp(-t / 0.015) * 0.35
    return np.tanh((body * 1.3 + nz + crack) * 1.4) * 0.75


def whoosh(dur=0.42):
    n = int(dur * SR); t = tarr(n)
    fc = 300 + 5200 * np.sin(np.pi * t / dur) ** 2
    y = onepole_var(rng.standard_normal(n), fc)
    y = y - onepole_var(y, np.full(n, 180.0))
    return y * np.sin(np.pi * t / dur) ** 1.6 * 0.55


def pop(pitch=1.0):
    n = int(0.09 * SR); t = tarr(n)
    f = 850 * pitch * np.exp(-t / 0.025) + 320 * pitch
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.03) * np.minimum(1, t / 0.001) * 0.2


def snap():
    n = int(0.16 * SR); t = tarr(n)
    tr = hp(rng.standard_normal(n), 2500) * np.exp(-t / 0.004)
    ping = (np.sin(2 * np.pi * 2350 * t) + 0.6 * np.sin(2 * np.pi * 3520 * t)) * np.exp(-t / 0.028) * 0.35
    thud = np.sin(2 * np.pi * 150 * t) * np.exp(-t / 0.035) * 0.7
    return (tr * 0.8 + ping + thud) * 0.55


def tick(f=3200.0, g=0.11):
    n = int(0.012 * SR); t = tarr(n)
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.0028) * g


def plink(f):
    n = int(0.35 * SR); t = tarr(n)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.05)
    return x * np.exp(-t / 0.12) * np.minimum(1, t / 0.002) * 0.12


def power_on():
    n = int(1.3 * SR); t = tarr(n)
    f = np.minimum(130 * 2 ** (t / 0.16), 1500)
    sweep = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.03) * np.exp(-np.maximum(t - 0.42, 0) / 0.2)
    shimmer = hp(rng.standard_normal(n), 6000) * np.exp(-np.maximum(t - 0.4, 0) / 0.3) * (t > 0.38) * 0.25
    chord = sum(np.sin(2 * np.pi * note(nm) * t) for nm in ("A4", "C#5", "E5", "A5")) * (t > 0.42) * np.exp(-np.maximum(t - 0.42, 0) / 0.4) * 0.12
    return (sweep * 0.22 + shimmer + chord) * 0.9


def bell(f):
    n = int(2.0 * SR); t = tarr(n)
    parts = [(1, 1.0, 1.3), (2.76, 0.45, 0.6), (5.4, 0.22, 0.32), (8.93, 0.1, 0.18)]
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / d) for m, a, d in parts)
    return x * np.minimum(1, t / 0.002) * 0.17


def riser(dur):
    n = int(dur * SR); t = tarr(n)
    fc = 250 * (40 ** (t / dur))
    nz = onepole_var(rng.standard_normal(n), np.minimum(fc, 16000))
    nz = nz - onepole_var(nz, np.minimum(fc * 0.35, 8000))
    tone_f = 110 * 2 ** (2 * t / dur)
    tone = np.sin(2 * np.pi * np.cumsum(tone_f) / SR) * 0.25
    return (nz * 1.6 + tone) * (t / dur) ** 2 * 0.45


# ------------------------------------------------------------------ arrangement
music = np.zeros((N, 2))
drums = np.zeros((N, 2))
sfx = np.zeros((N, 2))
send = np.zeros((N, 2))      # reverb send

CHORDS = [  # (bass root, pad voicing, arp tones)
    ("A1", ("A3", "C4", "E4", "A4"), ("A4", "C5", "E5", "A5")),
    ("F1", ("F3", "A3", "C4", "F4"), ("F4", "A4", "C5", "F5")),
    ("C2", ("G3", "C4", "E4", "G4"), ("C5", "E5", "G5", "C6")),
    ("G1", ("G3", "B3", "D4", "G4"), ("G4", "B4", "D5", "G5")),
]
brk0, brk1 = cues["breakdown"]
rise0, rise1 = cues["riser"]
drop0, drop1 = cues["dropOut"]
blink0, blink1 = cues["blinkTicks"][0] - 0.1, cues["blinkTicks"][-1] + 0.3


def section(t):
    if brk0 <= t < brk1:
        return "break"
    if rise0 <= t < drop0:
        return "build"
    if drop0 <= t < drop1:
        return "gap"
    if drop1 <= t < drop1 + 4.5:
        return "drop"
    return "groove"


kicks = []
nbars = int(np.ceil(DUR / BAR))
for b in range(nbars):
    t0 = b * BAR
    root, pad, arp = CHORDS[b % 4]
    # pads, per half bar so sections can change mid-bar
    for h in range(2):
        th = t0 + h * BAR / 2
        if th >= DUR:
            break
        sec = section(th + 0.01)
        if sec == "gap":
            continue
        cutoff = {"break": 850, "build": 900 + 2600 * (th - rise0) / max(1e-3, rise1 - rise0), "drop": 2600}.get(sec, 1800)
        seg = pad_chord([note(n) for n in pad], BAR / 2 + 0.25, cutoff)
        add(music, seg, th, gain=1.9 if sec != "break" else 1.4)
        add(send, seg, th, gain=0.6)
    for s16 in range(16):
        t = t0 + s16 * BEAT / 4
        if t >= DUR:
            break
        sec = section(t + 1e-4)
        beat_pos = s16 % 4
        # ---- drums
        if sec in ("groove", "drop"):
            if s16 in (0, 8) or (s16 in (10,) and b % 2 == 1) or (s16 == 14 and b % 4 == 3):
                add(drums, kick(1.1 if sec == "drop" else 1.0), t, gain=0.72); kicks.append(t)
            if s16 in (4, 12):
                add(drums, clap(), t, gain=0.55); add(send, clap(), t, gain=0.15)
            if beat_pos in (0, 2):
                add(drums, hat(open_=(s16 % 8 == 6)), t, gain=0.5 if beat_pos == 0 else 0.75, pan=0.25)
            elif sec == "drop" or b % 2 == 1:
                add(drums, hat(), t, gain=0.3, pan=0.25)
        elif sec == "break":
            if beat_pos == 2:
                add(drums, hat(), t, gain=0.35, pan=0.25)
        elif sec == "build":
            p = (t - rise0) / max(1e-3, drop0 - rise0)
            step = 4 if p < 0.33 else 2 if p < 0.7 else 1
            if s16 % step == 0:
                add(drums, clap(bright=0.7 + 0.5 * p), t, gain=0.18 + 0.32 * p)
            if beat_pos == 0:
                add(drums, kick(0.9), t, gain=0.7); kicks.append(t)
        # ---- bass
        f = note(root)
        if sec in ("groove", "drop") and s16 % 2 == 0:
            add(music, bass_note(f * (2 if s16 in (6, 14) else 1), BEAT / 2 - 0.02, 1.15 if sec == "drop" else 1.0), t)
        elif sec == "break" and s16 == 0:
            add(music, bass_note(f, BAR - 0.05, 0.6), t)
        elif sec == "build" and s16 % 4 == 0:
            add(music, bass_note(f, BEAT - 0.02, 0.8), t)
        # ---- arp
        if sec != "gap" and (b >= 1 or sec == "break"):
            tone = arp[[0, 1, 2, 3, 2, 1, 2, 3][s16 % 8]]
            g = {"break": 0.9, "build": 0.7, "drop": 1.0}.get(sec, 0.75)
            pl = pluck(note(tone), cutoff=2200 if sec == "break" else 3400)
            add(music, pl, t, gain=g * 1.4, pan=-0.3 if s16 % 2 else 0.3)
            add(send, pl, t, gain=0.5)

# lead hook in the drop + a short echo of it in the CTA
LEAD = [("E5", 0, 1), ("D5", 1, 1), ("C5", 2, 1), ("A4", 3, 3), ("C5", 6, 1), ("D5", 7, 1),
        ("E5", 8, 2), ("G5", 10, 2), ("E5", 12, 3), ("D5", 15, 1)]
for start in (drop1, drop1 + 2 * BAR):
    for nm, pos, ln in LEAD:
        t = start + pos * BEAT / 2
        if t < DUR - 0.3:
            ld = lead_note(note(nm), ln * BEAT / 2 - 0.02)
            add(music, ld, t, gain=1.2 if start == drop1 else 0.8)
            add(send, ld, t, gain=0.5)

# sidechain pump from kicks on the music bus
duck = np.ones(N)
for kt in kicks:
    i = int(kt * SR); n = int(0.3 * SR)
    if i >= N:
        continue
    j = min(N, i + n)
    env = 1 - 0.55 * np.exp(-tarr(j - i) / 0.09)
    duck[i:j] = np.minimum(duck[i:j], env)
music *= duck[:, None]

# blink: music dips so the frame plinks read
tt = tarr(N)
dip = 1 - 0.65 * np.clip(np.minimum((tt - blink0) / 0.08, (blink1 - tt) / 0.15), 0, 1)
music *= dip[:, None]; drums *= dip[:, None]

# ------------------------------------------------------------------ sfx placement
for i, t in enumerate(cues["impacts"]):
    big = t in (0, cues["clicks"][-1], cues["ding"])
    add(sfx, boom(1.3 if big else 0.9), t, gain=0.85 if big else 0.6)
    add(send, boom(), t, gain=0.15)
for i, t in enumerate(cues["whooshes"]):
    w = whoosh(0.38 + 0.08 * (i % 3))
    add(sfx, w, t - 0.18, gain=0.55, pan=-0.4 if i % 2 else 0.4)
for i, t in enumerate(cues["pops"]):
    add(sfx, pop(1.0 + 0.12 * ((i * 5) % 4)), t, gain=0.55, pan=(i % 3 - 1) * 0.25)
for t in cues["clicks"]:
    add(sfx, snap(), t, gain=1.0)
    add(send, snap(), t, gain=0.25)
for a, b, dt in cues["tickRuns"]:
    t = a; k = 0
    while t < b:
        add(sfx, tick(2600 + 900 * (t - a) / (b - a)), t, gain=1.0)
        # ticks speed up then slow down like a slot counter
        p = (t - a) / (b - a)
        t += dt * (0.7 + 1.4 * p * p); k += 1
for a, b, n in cues["frameTicks"]:
    for k in range(int(n)):
        t = a + (b - a) * k / n
        add(sfx, tick(1800 + 2600 * k / n, 0.07), t, gain=1.0, pan=-0.6 + 1.2 * k / n)
scale = ["C6", "D6", "E6", "G6", "A6", "C7", "D7", "E7", "G7", "A7", "C8", "D8"]
for k, t in enumerate(cues["blinkTicks"]):
    pl = plink(note(scale[k]) / 2)
    add(sfx, pl, t, gain=1.0, pan=-0.5 + k / 11)
    add(send, pl, t, gain=0.4)
add(sfx, power_on(), cues["power"], gain=1.0); add(send, power_on(), cues["power"], gain=0.4)
for k, f in enumerate((note("E6"), note("A6"))):
    add(sfx, bell(f), cues["ding"] + k * 0.12, gain=1.0); add(send, bell(f), cues["ding"] + k * 0.12, gain=0.5)
add(sfx, riser(rise1 - rise0), rise0, gain=0.9)

# ------------------------------------------------------------------ reverb + master
ir_n = int(1.6 * SR)
ti = tarr(ir_n)
ir = np.stack([lp(rng.standard_normal(ir_n), 5000), lp(rng.standard_normal(ir_n), 5000)], 1) * np.exp(-ti / 0.42)[:, None]
ir[: int(0.012 * SR)] = 0
ir /= np.sqrt((ir ** 2).sum(0))
L = N + ir_n
nfft = 1 << int(np.ceil(np.log2(L)))
wet = np.fft.irfft(np.fft.rfft(send, nfft, axis=0) * np.fft.rfft(ir, nfft, axis=0), nfft, axis=0)[:N]

mix = music * 0.62 + drums * 0.7 + sfx * 0.95 + wet * 0.22
# gentle low cut + fade out
mix = hp(mix, 30, order=1)
mix = fft_filter(mix, lambda f: (1 - 0.45 / (1 + (f / 95.0) ** 4)) * (1 + 0.3 * np.exp(-((np.log2(np.maximum(f, 1) / 3200.0)) ** 2) / 0.5)))
fade = np.clip((DUR - tt) / 0.45, 0, 1)
mix *= fade[:, None]
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
mix /= np.max(np.abs(mix)) / 0.89

with wave.open(OUT, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print(f"wrote {OUT}: {DUR:.2f}s, {len(kicks)} kicks")
