#!/usr/bin/env python3
"""Soundtrack for the PC build story, made to sit under a voiceover.

    python3 make_audio.py cues.json full.wav sfx.wav

full.wav = soft music bed + sound effects, sfx.wav = sound effects only.
Everything is synthesized with numpy (no licensed audio). 100 BPM, D major
(Dmaj7 - A - Bm7 - Gmaj7). The bed stays out of the voice range: warm keys,
filtered pads, soft drums.
"""
import json
import sys
import wave

import numpy as np

SR = 48000
cues = json.load(open(sys.argv[1]))
OUT_FULL, OUT_SFX = sys.argv[2], sys.argv[3]
DUR = float(cues["duration"])
N = int(DUR * SR)
rng = np.random.default_rng(11)
BEAT = 60.0 / cues["bpm"]
BAR = BEAT * 4
SEC = cues["sections"]


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


def env_ad(n, a, d):
    t = tarr(n)
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


# ------------------------------------------------------------------ music
def kick(g=1.0):
    n = int(0.4 * SR); t = tarr(n)
    f = 52 + 110 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    click = hp(rng.standard_normal(n), 1800) * np.exp(-t / 0.003) * 0.35
    return np.tanh((body + click) * 1.5) * 0.8 * g


def snare():
    n = int(0.35 * SR); t = tarr(n)
    nz = lp(bp(rng.standard_normal(n), 700, 4200), 3500) * np.exp(-t / 0.07)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04) * 0.4
    return (nz * 0.6 + tone) * 0.7


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); t = tarr(n)
    return hp(rng.standard_normal(n), 8000) * np.exp(-t / (0.08 if open_ else 0.016)) * 0.22


def keys(freqs, dur):
    """Warm electric-piano chord: sines + soft 2nd harmonic, gentle tremolo."""
    n = int(dur * SR); t = tarr(n)
    x = np.zeros(n)
    for f in freqs:
        x += np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.3) + 0.08 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.15)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    env = np.minimum(1, t / 0.01) * (0.35 + 0.65 * np.exp(-t / 0.9)) * np.clip((dur - t) / 0.2, 0, 1)
    L = x * env * trem
    R = x * env * (2 - trem)
    return np.stack([L, R], 1) * 0.045


def pad(freqs, dur, cutoff=1100):
    n = int(dur * SR); t = tarr(n)
    L = np.zeros(n); R = np.zeros(n)
    for f in freqs:
        L += saw(f * 2 ** (-6 / 1200), n, rng.random())
        R += saw(f * 2 ** (6 / 1200), n, rng.random())
    env = np.minimum(1, t / 0.5) * np.clip((dur - t) / 0.5, 0, 1)
    return np.stack([lp(L, cutoff) * env, lp(R, cutoff) * env], 1) * 0.022


def bass(f, dur, g=1.0):
    n = int(dur * SR); t = tarr(n)
    x = np.sin(2 * np.pi * f * t) + 0.35 * lp(saw(f, n), 600)
    env = np.minimum(1, t / 0.006) * (0.6 + 0.4 * np.exp(-t / 0.2)) * np.clip((dur - t) / 0.03, 0, 1)
    return np.tanh(x * 1.3) * env * 0.32 * g


def pluck(f, dur=0.3):
    n = int(dur * SR); t = tarr(n)
    x = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.06)
    return x * env_ad(n, 0.002, 0.11) * 0.07


# ------------------------------------------------------------------ sfx
def whoosh(dur=0.42):
    n = int(dur * SR); t = tarr(n)
    fc = 300 + 4800 * np.sin(np.pi * t / dur) ** 2
    y = onepole_var(rng.standard_normal(n), fc)
    y = y - onepole_var(y, np.full(n, 180.0))
    return y * np.sin(np.pi * t / dur) ** 1.6 * 0.5


def pop(pitch=1.0):
    n = int(0.09 * SR); t = tarr(n)
    f = 820 * pitch * np.exp(-t / 0.025) + 320 * pitch
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.03) * np.minimum(1, t / 0.001) * 0.18


def tick(f=3000.0, g=0.1):
    n = int(0.014 * SR); t = tarr(n)
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.003) * g


def chime(notes=("D6", "F#6", "A6"), gap=0.07, g=0.11):
    n = int((0.9 + gap * len(notes)) * SR)
    out = np.zeros(n)
    for k, nm in enumerate(notes):
        i = int(k * gap * SR); m = n - i; t = tarr(m); f = note(nm)
        out[i:] += (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2.01 * f * t) * np.exp(-t / 0.1)) * env_ad(m, 0.002, 0.35)
    return out * g


def kaching():
    n = int(0.8 * SR); t = tarr(n)
    bell = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in [(2637, 1, .25), (3520, .7, .2), (5274, .4, .12)])
    rattle = bp(rng.standard_normal(n), 2500, 9000) * np.exp(-t / 0.03) * 0.6
    drawer = np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.05) * 0.5
    return (bell * 0.25 * (t > 0.06) + rattle + drawer) * 0.45


def thump():
    n = int(0.35 * SR); t = tarr(n)
    f = 70 + 90 * np.exp(-t / 0.02)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07)
    card = lp(rng.standard_normal(n), 1600) * np.exp(-t / 0.025) * 0.5
    return np.tanh((body + card) * 1.4) * 0.5


def stamp():
    n = int(0.5 * SR); t = tarr(n)
    f = 60 + 120 * np.exp(-t / 0.015)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
    slap = bp(rng.standard_normal(n), 400, 3000) * np.exp(-t / 0.02) * 0.7
    return np.tanh((body + slap) * 1.6) * 0.55


def snap():
    n = int(0.16 * SR); t = tarr(n)
    tr = hp(rng.standard_normal(n), 2500) * np.exp(-t / 0.004)
    ping = (np.sin(2 * np.pi * 2350 * t) + 0.6 * np.sin(2 * np.pi * 3520 * t)) * np.exp(-t / 0.028) * 0.35
    thud = np.sin(2 * np.pi * 150 * t) * np.exp(-t / 0.035) * 0.7
    return (tr * 0.8 + ping + thud) * 0.5


def zip_tie():
    n = int(0.22 * SR); t = tarr(n)
    rate = 140 + 260 * t / 0.22
    clicks = (np.sin(2 * np.pi * np.cumsum(rate) / SR) > 0.85).astype(float)
    x = hp(rng.standard_normal(n), 3000) * (0.25 + clicks) * np.sin(np.pi * t / 0.22)
    return x * 0.22


def glass_slide():
    n = int(0.35 * SR); t = tarr(n)
    fc = 1200 + 3000 * t / 0.35
    y = onepole_var(rng.standard_normal(n), fc)
    y = y - onepole_var(y, np.full(n, 600.0))
    clunk = np.sin(2 * np.pi * 220 * t) * np.exp(-np.maximum(t - 0.3, 0) / 0.03) * (t > 0.3) * 0.5
    return (y * np.sin(np.pi * t / 0.35) * 0.6 + clunk) * 0.6


def power_on():
    n = int(1.2 * SR); t = tarr(n)
    f = np.minimum(130 * 2 ** (t / 0.16), 1400)
    sweep = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.03) * np.exp(-np.maximum(t - 0.42, 0) / 0.2)
    chord = sum(np.sin(2 * np.pi * note(nm) * t) for nm in ("D5", "F#5", "A5")) * (t > 0.42) * np.exp(-np.maximum(t - 0.42, 0) / 0.4) * 0.1
    return (sweep * 0.18 + chord) * 0.9


def fan_hum(dur):
    n = int(dur * SR); t = tarr(n)
    nz = bp(rng.standard_normal(n), 200, 1400) * 0.5
    blade = np.sin(2 * np.pi * 118 * t) * 0.15
    env = np.minimum(1, t / 0.6) * np.clip((dur - t) / 0.4, 0, 1)
    return (nz + blade) * env * 0.12


def fan_up(dur=1.2):
    n = int(dur * SR); t = tarr(n)
    fc = 200 + 2200 * (t / dur) ** 1.5
    y = onepole_var(rng.standard_normal(n), fc)
    return y * np.minimum(1, t / dur) * np.clip((dur - t) / 0.15, 0, 1) * 0.6


def blip(f):
    n = int(0.05 * SR); t = tarr(n)
    return np.sin(2 * np.pi * f * t) * env_ad(n, 0.001, 0.012) * 0.05


def step_snd():
    n = int(0.12 * SR); t = tarr(n)
    return (lp(rng.standard_normal(n), 700) * np.exp(-t / 0.02) + np.sin(2 * np.pi * 90 * t) * np.exp(-t / 0.03)) * 0.25


def scrape(dur):
    n = int(dur * SR); t = tarr(n)
    y = bp(rng.standard_normal(n), 300, 2200) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t))
    return y * np.sin(np.pi * t / dur) * 0.16


def popper():
    n = int(1.4 * SR); t = tarr(n)
    bang = hp(rng.standard_normal(n), 1200) * np.exp(-t / 0.012) * 0.9
    crackle = hp(rng.standard_normal(n), 5000) * (rng.random(n) > 0.995) * np.exp(-t / 0.5) * 3
    low = np.sin(2 * np.pi * 80 * t) * np.exp(-t / 0.05) * 0.5
    return (bang + crackle + low) * 0.45


def ding():
    n = int(1.8 * SR); t = tarr(n)
    f = note("A5")
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / d) for m, a, d in [(1, 1, 1.1), (2.76, .45, .5), (5.4, .2, .28)])
    return x * np.minimum(1, t / 0.002) * 0.16


def boom(g=1.0):
    n = int(1.6 * SR); t = tarr(n)
    f = 32 + 60 * np.exp(-t / 0.07)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45)
    nz = lp(rng.standard_normal(n), 2000) * np.exp(-t / 0.09) * 0.45
    return np.tanh((body * 1.2 + nz) * 1.3) * 0.6 * g


def riser(dur):
    n = int(dur * SR); t = tarr(n)
    fc = 250 * (30 ** (t / dur))
    nz = onepole_var(rng.standard_normal(n), np.minimum(fc, 14000))
    nz = nz - onepole_var(nz, np.minimum(fc * 0.35, 7000))
    return nz * (t / dur) ** 2 * 0.5


# ------------------------------------------------------------------ arrangement
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
send = np.zeros((N, 2))

CH = [("D2", ("D4", "F#4", "A4", "C#5"), ("A4", "D5", "F#5")),
      ("A1", ("C#4", "E4", "A4", "E5"), ("A4", "C#5", "E5")),
      ("B1", ("D4", "F#4", "A4", "B4"), ("B4", "D5", "F#5")),
      ("G1", ("D4", "F#4", "B4", "G4"), ("G4", "B4", "D5"))]
test0, test1 = SEC["test"]
pass_t = cues["pass"][0]
kicks = []
nbars = int(np.ceil(DUR / BAR))
for b in range(nbars):
    t0 = b * BAR
    root, chord, arp = CH[b % 4]
    if t0 < DUR - 0.5:
        k = keys([note(n) for n in chord], BAR + 0.1)
        add(music, k, t0, gain=1.0); add(send, k, t0, gain=0.5)
        pd = pad([note(n) for n in chord[:3]], BAR + 0.4)
        add(music, pd, t0)
    for s16 in range(16):
        t = t0 + s16 * BEAT / 4
        if t >= DUR - 0.3:
            break
        tense = test0 <= t < pass_t
        intro = t < 1.2
        if not tense and not intro:
            if s16 in (0, 8) or (s16 == 10 and b % 2):
                add(music, kick(), t, gain=0.85); kicks.append(t)
            if s16 in (4, 12):
                add(music, snare(), t, gain=0.5)
        if s16 % 2 == 0 and not intro:
            swing = 0.03 if s16 % 4 == 2 else 0
            add(music, hat(open_=(s16 == 14 and b % 2 == 1)), t + swing, gain=0.7 if s16 % 4 == 0 else 0.45, pan=0.2)
        if s16 % 2 == 0 and not intro:
            g = 0.75 if tense else 1.0
            add(music, bass(note(root) * (2 if s16 in (6, 14) else 1), BEAT / 2 - 0.02, g), t)
        # little arp only where the story lifts (hand-off + CTA)
        if t >= SEC["yours"][0] and s16 % 2 == 0:
            add(music, pluck(note(arp[(s16 // 2) % 3])), t, gain=0.45, pan=-0.3 if s16 % 4 else 0.3)
            add(send, pluck(note(arp[(s16 // 2) % 3])), t, gain=0.4)

duck = np.ones(N)
for kt in kicks:
    i = int(kt * SR); n = int(0.28 * SR)
    if i >= N:
        continue
    j = min(N, i + n)
    duck[i:j] = np.minimum(duck[i:j], 1 - 0.35 * np.exp(-tarr(j - i) / 0.09))
music *= duck[:, None]

# ------------------------------------------------------------------ sfx placement
for i, t in enumerate(cues["whoosh"]):
    add(sfx, whoosh(0.38 + 0.06 * (i % 3)), t - 0.18, gain=0.32, pan=-0.35 if i % 2 else 0.35)
for i, t in enumerate(cues["pop"]):
    add(sfx, pop(1.0 + 0.12 * ((i * 5) % 4)), t, gain=0.42, pan=(i % 3 - 1) * 0.25)
for i, t in enumerate(cues["tick"]):
    add(sfx, tick(2600 + 120 * (i % 7)), t, gain=1.0)
for t in cues["chime"]:
    add(sfx, chime(), t); add(send, chime(), t, gain=0.4)
for t in cues["kaching"]:
    add(sfx, kaching(), t, gain=0.6)
for t in cues["thump"]:
    add(sfx, thump(), t, gain=0.6)
for i, t in enumerate(cues["check"]):
    add(sfx, tick(3400 + 150 * i, 0.08), t)
for t in cues["stamp"]:
    add(sfx, stamp(), t, gain=0.5)
for i, t in enumerate(cues["click"]):
    add(sfx, snap(), t, gain=0.85 if i == len(cues["click"]) - 1 else 0.7); add(send, snap(), t, gain=0.2)
for t in cues["zip"]:
    add(sfx, zip_tie(), t)
for t in cues["glass"]:
    add(sfx, glass_slide(), t)
for t in cues["power"]:
    add(sfx, power_on(), t); add(send, power_on(), t, gain=0.4)
for t in cues["fanUp"]:
    add(sfx, fan_up(), t, gain=0.5)
h0, h1 = cues["fanHum"]
add(sfx, fan_hum(h1 - h0), h0)
for i, t in enumerate(cues["blips"]):
    add(sfx, blip(1400 + 200 * (i % 4)), t, pan=0.3)
add(sfx, riser(2.2), pass_t - 2.2, gain=0.3)
for t in cues["pass"]:
    add(sfx, chime(("D6", "F#6", "A6", "D7"), 0.08, 0.13), t); add(send, chime(("D6", "F#6", "A6", "D7"), 0.08, 0.1), t, gain=0.5)
for i, t in enumerate(cues["steps"]):
    add(sfx, step_snd(), t, pan=-0.5 if i % 2 else -0.3)
s0, s1 = cues["slide"]
add(sfx, scrape(s1 - s0), s0)
for t in cues["popper"]:
    add(sfx, popper(), t, gain=0.5)
for t in cues["yay"]:
    add(sfx, chime(("D6", "E6", "F#6", "A6", "B6", "D7"), 0.06, 0.1), t); add(send, chime(("D6", "F#6", "A6")), t, gain=0.4)
for t in cues["ding"]:
    for k, f in enumerate((note("E6"), note("A6"))):
        n = int(1.8 * SR); tt = tarr(n)
        bell = sum(a * np.sin(2 * np.pi * f * m * tt) * np.exp(-tt / d) for m, a, d in [(1, 1, 1.1), (2.76, .45, .5), (5.4, .2, .28)]) * 0.15
        add(sfx, bell, t + k * 0.12); add(send, bell, t + k * 0.12, gain=0.5)
for t in cues["impacts"]:
    add(sfx, boom(0.8), t, gain=0.32)
for t in cues["endHit"]:
    add(sfx, boom(1.0), t, gain=0.28)

# ------------------------------------------------------------------ reverb + export
ir_n = int(1.4 * SR)
ti = tarr(ir_n)
ir = np.stack([lp(rng.standard_normal(ir_n), 5000), lp(rng.standard_normal(ir_n), 5000)], 1) * np.exp(-ti / 0.38)[:, None]
ir[: int(0.012 * SR)] = 0
ir /= np.sqrt((ir ** 2).sum(0))
L = N + ir_n
nfft = 1 << int(np.ceil(np.log2(L)))
wet = np.fft.irfft(np.fft.rfft(send, nfft, axis=0) * np.fft.rfft(ir, nfft, axis=0), nfft, axis=0)[:N]

def compress(x, thr_db=-16.0, ratio=4.0, attack=0.002, release=0.15, block=96):
    """Peak compressor so no single hit jumps out over the voice."""
    mono = np.max(np.abs(x), axis=1)
    nb = int(np.ceil(len(mono) / block))
    m = np.pad(mono, (0, nb * block - len(mono))).reshape(nb, block).max(axis=1)
    a_att, a_rel = np.exp(-block / (attack * SR)), np.exp(-block / (release * SR))
    env = np.empty(nb); e = 0.0
    for i in range(nb):
        a = a_att if m[i] > e else a_rel
        e = a * e + (1 - a) * m[i]
        env[i] = e
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
bed *= 0.55 * rms(sfx) / rms(bed)          # music sits under the effects, both sit under the voice
full = (bed + sfx) * fade
fx_only = (sfx + voice_dip(wet) * 0.06) * fade


def finish(x):
    x = hp(x, 30, order=1)
    x = fft_filter(x, lambda f: 1 - 0.4 / (1 + (f / 90.0) ** 4))
    x = np.tanh(x * 1.1) / np.tanh(1.1)
    return x / (np.max(np.abs(x)) / 0.89)


for path, x in ((OUT_FULL, finish(full)), (OUT_SFX, finish(fx_only))):
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
print(f"wrote {OUT_FULL} and {OUT_SFX}: {DUR:.1f}s")
