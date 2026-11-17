"""Cinematic score for the Sonmarg film: 20 s, A minor.
Wind ambience + low drone + slow string pad + felt piano, a shimmer riser into
the title and a deep boom at the title reveal (16.4 s). Chords change with the
picture's dissolves. Deterministic (fixed seed). Usage: python3 score.py out.wav"""
import numpy as np, wave, sys

SR = 44100
DUR = 20.0
N = int(SR * DUR)
rng = np.random.default_rng(11)
T = np.arange(N) / SR

def lp(x, fc):
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y

def hp(x, fc): return x - lp(x, fc)
def hz(m): return 440 * 2 ** ((m - 69) / 12)

L = np.zeros(N); R = np.zeros(N)
def add(sig, start, g=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N: return
    j = min(N, i + len(sig)); s = sig[: j - i] * g
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))

# chord changes follow the dissolves
TITLE = 16.4
SECTIONS = [  # start, root, voicing
    (0.0,  45, [57, 64, 67, 71, 72]),   # Am(add9)
    (3.3,  41, [57, 60, 64, 67, 69]),   # Fmaj7
    (5.9,  48, [55, 60, 64, 67, 71]),   # Cmaj7
    (8.5,  43, [55, 59, 62, 66, 69]),   # G(add 6/9)
    (11.1, 45, [57, 60, 64, 67, 71]),   # Am9
    (13.6, 41, [57, 60, 64, 65, 69]),   # F(add9)
    (TITLE, 45, [57, 64, 69, 71, 72, 76]),  # Am(add9) wide — title
]
def sec_bounds(k):
    s = SECTIONS[k][0]; e = SECTIONS[k + 1][0] if k + 1 < len(SECTIONS) else DUR
    return s, e

# ---------- wind ambience ----------
wn = rng.standard_normal(N)
gust = 0.6 + 0.4 * np.sin(2 * np.pi * T / 7.3) * np.sin(2 * np.pi * T / 3.1 + 1)
wind = lp(hp(wn, 180), 600 + 500 * gust) * gust
add(wind, 0, 0.18, -0.3); add(np.roll(wind, 9000), 0, 0.18, 0.3)

# ---------- low drone ----------
drone = np.zeros(N)
for k in range(len(SECTIONS)):
    s, e = sec_bounds(k); root = SECTIONS[k][1]
    n = int((e - s + 0.6) * SR); tt = np.arange(n) / SR
    sig = np.sin(2 * np.pi * hz(root - 12) * tt) + 0.5 * np.sin(2 * np.pi * hz(root - 5) * tt)
    env = np.minimum(1, tt / 0.5) * np.minimum(1, np.maximum(0, (n / SR - tt) / 0.6))
    i = int(s * SR); j = min(N, i + n); drone[i:j] += (sig * env)[: j - i]
drone *= np.clip(T / 2.0, 0, 1)
add(drone, 0, 0.22)

# ---------- string pad (slow attack, detuned, filtered) ----------
pad = np.zeros(N)
for k in range(len(SECTIONS)):
    s, e = sec_bounds(k); voic = SECTIONS[k][2]
    n = int((e - s + 1.0) * SR); tt = np.arange(n) / SR
    sig = np.zeros(n)
    for m in voic:
        for det in (-0.08, 0.0, 0.07):
            f = hz(m + det); vib = 1 + 0.002 * np.sin(2 * np.pi * 5.2 * tt + rng.random() * 6)
            sig += 2 * ((np.cumsum(f * vib) / SR + rng.random()) % 1) - 1
    sig /= 3 * len(voic)
    env = np.minimum(1, tt / 0.9) * np.minimum(1, np.maximum(0, (n / SR - tt) / 1.0))
    i = int(s * SR); j = min(N, i + n); pad[i:j] += (sig * env)[: j - i]
swell = 0.35 + 0.65 * np.clip((T - 1.0) / 14, 0, 1)            # slowly grows
swell = np.where(T >= TITLE, 1.0, swell)
pad = lp(pad, 900 + 2600 * swell) * swell
add(pad, 0, 0.5, -0.25); add(np.roll(pad, 600), 0, 0.5, 0.25)

# ---------- felt piano ----------
def piano(f, dur=2.6, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    sig = sum((0.6 ** (k - 1)) * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * tt) * np.exp(-tt * (1.6 + 1.3 * k))
              for k in range(1, 7))
    click = np.exp(-tt * 300) * rng.standard_normal(n) * 0.02
    return lp((sig + click) * np.minimum(1, tt * 200) * vel, 3500)

# arpeggio pattern per section (time offsets in s, chord tone index, octave)
pat = [(0.0, 0, 0), (0.55, 2, 0), (1.1, 3, 0), (1.65, 1, 1), (2.2, 2, 0)]
for k in range(len(SECTIONS) - 1):
    s, e = sec_bounds(k); voic = SECTIONS[k][2]
    if k == 0: start_off = 0.6
    else: start_off = 0.0
    for (o, idx, oc) in pat:
        t0 = s + start_off + o
        if t0 > e - 0.15: break
        add(piano(hz(voic[idx % len(voic)] + 12 * oc)), t0, 0.3, (idx - 2) * 0.25)
    # bass note on each change
    add(piano(hz(SECTIONS[k][1]), 3.5, 0.9), s + start_off, 0.32)
# melody over the second half (simple, sparse)
mel = [(8.5 + 0.3, 76), (9.6, 74), (10.4, 71), (11.1 + 0.2, 72), (12.2, 71), (13.0, 69), (13.6 + 0.2, 72), (14.6, 76), (15.5, 74)]
for t0, m in mel:
    add(piano(hz(m), 2.8, 0.9), t0, 0.28, 0.1)
# title chord (spread)
for i_, m in enumerate([45, 57, 64, 69, 71, 76, 81]):
    add(piano(hz(m), 3.6, 1.0), TITLE + i_ * 0.06, 0.28, (i_ - 3) * 0.15)

# ---------- shimmer riser into the title ----------
n = int(2.4 * SR); tt = np.arange(n) / SR; x = tt / 2.4
nz = hp(lp(rng.standard_normal(n), 2000 + 9000 * x ** 2), 1500) * x ** 3 * 0.35
rev = np.zeros(n)
for m in (81, 88, 93):  # reversed bell-ish tones
    bell = np.sin(2 * np.pi * hz(m) * tt) * np.exp(-(2.4 - tt) * 2.5)
    rev += bell * 0.08
add(nz + rev, TITLE - 2.4, 1.0)

# ---------- deep boom at the title ----------
n = int(4.5 * SR); tt = np.arange(n) / SR
f = 32 + 55 * np.exp(-tt * 5)
boom = np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 1.1))
air = lp(hp(rng.standard_normal(n), 200), 1200) * np.exp(-tt * 1.5) * 0.25
add(boom + air, TITLE, 0.85)
# softer sub hit at the opening of the first dissolve
n2 = int(2.5 * SR); t2 = np.arange(n2) / SR
add(np.sin(2 * np.pi * np.cumsum(30 + 30 * np.exp(-t2 * 6)) / SR) * np.exp(-t2 * 1.6), 0.0, 0.35)

# ---------- hall reverb ----------
def reverb(x, sec=3.4, mix=0.38):
    n = int(sec * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 2.0)
    ir = lp(ir, 4200); ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR)); ir /= np.sqrt(np.sum(ir ** 2))
    m = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[: len(x)]
    return x + mix * y
L, R = reverb(L), reverb(np.roll(R, 0))

# master
fade = np.ones(N); fi = int(0.8 * SR); fade[:fi] = np.linspace(0, 1, fi) ** 2
fo = int(2.2 * SR); fade[-fo:] = np.linspace(1, 0, fo) ** 1.6
L *= fade; R *= fade
mx = max(np.abs(L).max(), np.abs(R).max())
L, R = np.tanh(1.1 * L / mx), np.tanh(1.1 * R / mx)
mx = max(np.abs(L).max(), np.abs(R).max()); L, R = L / mx * 0.9, R / mx * 0.9
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([L, R], 1) * 32767).astype("<i2").tobytes())
print("ok")
