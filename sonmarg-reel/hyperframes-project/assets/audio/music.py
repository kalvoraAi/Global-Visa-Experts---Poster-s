"""Synthesize a 20s cinematic/uplifting travel beat (120 BPM, A minor) + transition whooshes.
Deterministic (fixed seed). Writes 16-bit stereo WAV."""
import numpy as np, wave, sys

SR = 44100
DUR = 20.0
N = int(SR * DUR)
BPM = 120
BEAT = 60 / BPM  # 0.5s
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR

def lp(x, cutoff):
    """one-pole low-pass; cutoff may be array"""
    cutoff = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y

def hp(x, cutoff):
    return x - lp(x, cutoff)

def place(buf, sig, start):
    i = int(start * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]

def note(m):  # midi -> hz
    return 440 * 2 ** ((m - 69) / 12)

def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[na:na + nd] = np.linspace(1, s, nd)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e

DROP = 2.5
END_HIT = 17.0
# chord progression per 2s bar (from DROP): Am, F, C, G  (midi roots + triads)
CHORDS = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [52, 55, 60]), (55, [55, 59, 62])]
def chord_at(tt):
    if tt < DROP: return CHORDS[0]
    k = int((tt - DROP) // 2.0) % 4
    return CHORDS[k]

L = np.zeros(N); R = np.zeros(N)
def add(sig, start, gain=1.0, pan=0.0):
    place(L, sig * gain * np.sqrt(0.5 * (1 - pan)), start)
    place(R, sig * gain * np.sqrt(0.5 * (1 + pan)), start)

# ---------- PAD (detuned saws, long) ----------
pad = np.zeros(N)
bar_starts = [0.0, 0.5] + list(np.arange(DROP, 20.0, 2.0))
segs = [(0.0, DROP, CHORDS[0])] + [(s, min(s + 2.0, 20.0), chord_at(s + 0.01)) for s in np.arange(DROP, 20.0, 2.0)]
for (s, e, (root, tri)) in segs:
    n = int((e - s) * SR); tt = np.arange(n) / SR
    sig = np.zeros(n)
    for m in tri + [tri[0] + 12]:
        for det in (-0.12, 0.0, 0.11):
            f = note(m + det)
            ph = rng.random()
            sig += 2 * ((tt * f + ph) % 1) - 1
    sig /= 12
    place(pad, sig * env_adsr(n, 0.08, 0.2, 0.9, 0.12), s)
cut = np.where(t_all < DROP, 400 + 2600 * (t_all / DROP) ** 2, 3200)
cut = np.where(t_all > END_HIT, 3200 - 2200 * np.clip((t_all - END_HIT) / 3, 0, 1), cut)
pad = lp(pad, cut)
# sidechain pump after drop
pump = np.ones(N)
for b in np.arange(DROP, END_HIT, BEAT):
    i = int(b * SR); n = int(0.35 * SR)
    pump[i:i + n] = np.minimum(pump[i:i + n], 0.25 + 0.75 * np.linspace(0, 1, n) ** 0.6)
pad *= pump
add(pad, 0, 0.55, -0.15); add(np.roll(pad, 300), 0, 0.55, 0.15)

# ---------- KICK ----------
def kick():
    n = int(0.45 * SR); tt = np.arange(n) / SR
    f = 45 + 110 * np.exp(-tt * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh(2.2 * np.sin(ph) * np.exp(-tt * 7.5))
K = kick()
for b in np.arange(DROP, END_HIT, BEAT):
    add(K, b, 0.95)
# build-up kicks in the intro (accelerating)
for b in [1.0, 1.5, 2.0, 2.25]:
    add(K, b, 0.45)

# ---------- CLAP ----------
def clap():
    n = int(0.25 * SR); tt = np.arange(n) / SR
    nz = rng.standard_normal(n)
    e = np.exp(-tt * 22)
    for d in (0.0, 0.011, 0.022):
        e += np.where(tt > d, np.exp(-(tt - d) * 140), 0) * 0.6
    return hp(lp(nz, 3500), 900) * e * 0.6
C = clap()
for b in np.arange(DROP + BEAT, END_HIT, 2 * BEAT):
    add(C, b, 0.7, 0.05)

# ---------- HATS ----------
def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR); tt = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-tt * (18 if open_ else 80))
H, HO = hat(), hat(True)
for b in np.arange(DROP, END_HIT, BEAT / 2):
    off = abs(((b - DROP) / BEAT) % 1 - 0.5) < 1e-6
    add(HO if off else H, b, 0.28 if off else 0.18, 0.3 if off else -0.3)

# ---------- SUB BASS ----------
for b in np.arange(DROP, END_HIT, BEAT / 2):
    root = chord_at(b + 0.001)[0] - 12
    n = int(0.24 * SR); tt = np.arange(n) / SR
    sig = np.sin(2 * np.pi * note(root) * tt) + 0.3 * np.sin(4 * np.pi * note(root) * tt)
    add(sig * env_adsr(n, 0.005, 0.05, 0.8, 0.08), b + 0.06, 0.42)

# ---------- PLUCK ARP (16ths, bright) ----------
def pluck(f, dur=0.22):
    n = int(dur * SR); tt = np.arange(n) / SR
    sig = sum((1 / k) * np.sin(2 * np.pi * f * k * tt) * np.exp(-tt * (9 + 6 * k)) for k in range(1, 6))
    return sig * np.minimum(1, tt * 400)
step = BEAT / 2
i = 0
for b in np.arange(0.0, 19.0, step):
    root, tri = chord_at(b + 0.001)
    seq = [tri[0] + 12, tri[1] + 12, tri[2] + 12, tri[1] + 24, tri[2] + 12, tri[0] + 24]
    m = seq[i % len(seq)]; i += 1
    g = 0.11 if b < DROP else 0.16
    add(pluck(note(m)), b, g, 0.45 if i % 2 else -0.45)

# ---------- RISER into drop ----------
n = int(DROP * SR); tt = np.arange(n) / SR
nz = rng.standard_normal(n)
riser = hp(lp(nz, 300 + 7000 * (tt / DROP) ** 2.2), 200) * (tt / DROP) ** 2.5 * 0.5
sweep = np.sin(2 * np.pi * np.cumsum(200 + 900 * (tt / DROP) ** 2) / SR) * (tt / DROP) ** 3 * 0.12
add(riser + sweep, 0, 1.0)

# ---------- IMPACTS ----------
def impact():
    n = int(2.2 * SR); tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(30 + 70 * np.exp(-tt * 6)) / SR) * np.exp(-tt * 2.2)
    crash = hp(rng.standard_normal(n), 3000) * np.exp(-tt * 2.5) * 0.25
    return np.tanh(1.6 * boom) + crash
IM = impact()
add(IM, DROP, 0.75); add(IM, END_HIT, 0.7)

# ---------- WHOOSHES on cuts ----------
CUTS = [4.5, 6.0, 7.5, 9.0, 11.0, 13.0, 15.0]
def whoosh(len_=0.45):
    n = int(len_ * SR); tt = np.arange(n) / SR; x = tt / len_
    nz = rng.standard_normal(n)
    sig = lp(nz, 500 + 6000 * np.sin(np.pi * x) ** 2) * np.sin(np.pi * x) ** 2
    return hp(sig, 250)
for k, c in enumerate(CUTS):
    w = whoosh()
    add(w, c - 0.3, 0.55, -0.6 if k % 2 else 0.6)

# ---------- simple reverb ----------
def reverb(x, sec=1.6, mix=0.22):
    n = int(sec * SR); tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * 3.2)
    ir = lp(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2))
    m = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[: len(x)]
    return x + mix * y
L, R = reverb(L), reverb(R)

# master: fade out tail, soft clip, normalize
fade = np.ones(N); fo = int(1.2 * SR); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
fi = int(0.05 * SR); fade[:fi] = np.linspace(0, 1, fi)
L *= fade; R *= fade
mx = max(np.abs(L).max(), np.abs(R).max())
L, R = np.tanh(1.3 * L / mx) , np.tanh(1.3 * R / mx)
mx = max(np.abs(L).max(), np.abs(R).max())
L, R = L / mx * 0.89, R / mx * 0.89
out = np.stack([L, R], 1)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype("<i2").tobytes())
print("ok")
