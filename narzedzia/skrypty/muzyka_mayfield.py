# Podkład + efekty + miks z lektorem do filmu "Zacisk Mayfielda" (120 BPM, a-moll, napięcie)
# Użycie: python muzyka_mayfield.py  (uruchamiać z katalogu my-video) -> public/mayfield/mix.wav
import numpy as np, wave, json

SR = 48000
DUR = 29.6
N = int(SR * DUR)
rng = np.random.default_rng(11)
BEAT = 0.5  # 120 BPM


def load(path):
    with wave.open(path) as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64) / 32768
    x = x.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        t = np.arange(int(len(x) * SR / sr)) * sr / SR
        x = np.interp(t, np.arange(len(x)), x)
    return x


def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


class Bus:
    def __init__(self):
        self.x = np.zeros((N, 2))

    def add(self, sig, t, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i >= N:
            return
        s = sig[: N - i] * gain
        self.x[i : i + len(s), 0] += s * (1 - max(0, pan))
        self.x[i : i + len(s), 1] += s * (1 + min(0, pan))


# ---------- instrumenty ----------
def kick(g=1.0):
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = 42 + 120 * np.exp(-t * 30)
    return np.tanh(2.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)) * g


def tick():  # "zegarowy" hi-hat – precyzja
    n = int(0.06 * SR); x = rng.standard_normal(n)
    x = np.diff(np.concatenate([[0], x]))
    return x * env(n, 0.0005, 0.012) * 0.35


def bass(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(4 * np.pi * freq * t) + 0.2 * np.sin(6 * np.pi * freq * t)
    return np.tanh(1.6 * s) * env(n, 0.004, 0.16) * 0.42


def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for d, p in ((-0.003, 0), (0, 1.3), (0.004, 2.1)):
            s += np.sin(2 * np.pi * f * (1 + d) * t + p) + 0.3 * np.sin(4 * np.pi * f * (1 + d) * t + p)
    a = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return s / (len(freqs) * 3) * a * 0.22


def pulse(freq, dur):  # arpeggio-pluck
    n = int(dur * SR); t = np.arange(n) / SR
    s = 0.6 * np.sign(np.sin(2 * np.pi * freq * t)) + np.sin(2 * np.pi * freq * t)
    return s * env(n, 0.002, 0.07) * 0.07


def sub_boom(g=1.0):
    n = int(1.6 * SR); t = np.arange(n) / SR
    f = 30 + 70 * np.exp(-t * 8)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    nz = rng.standard_normal(n) * np.exp(-t * 14) * 0.25
    return np.tanh(2 * (s + nz)) * g


def metal_hit(g=1.0, base=1800):  # uderzenie stali – nieharmoniczne alikwoty
    n = int(0.7 * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for k, r in enumerate((1.0, 1.47, 2.09, 2.56, 3.21)):
        s += np.sin(2 * np.pi * base * r * t) * np.exp(-t * (9 + 5 * k)) / (1 + k * 0.6)
    cl = rng.standard_normal(n) * env(n, 0.0003, 0.006)
    body = np.sin(2 * np.pi * 140 * t) * np.exp(-t * 30)
    return (0.35 * s + 0.6 * cl + 0.5 * body) * g


def ratchet(count=6, spacing=0.07, g=1.0):  # zaciskanie śruby
    out = np.zeros(int((count * spacing + 0.1) * SR))
    for k in range(count):
        n = int(0.03 * SR)
        c = rng.standard_normal(n) * env(n, 0.0002, 0.004)
        c += np.sin(2 * np.pi * 3200 * np.arange(n) / SR) * env(n, 0.0002, 0.006) * 0.5
        i = int(k * spacing * SR)
        out[i : i + n] += c * (0.7 + 0.3 * k / count)
    return out * g


def beep(freq=1000, dur=0.13, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * np.minimum(1, t / 0.004) * np.minimum(1, (dur - t) / 0.02) * 0.25 * g


def heartbeat(g=1.0):
    return np.concatenate([kick(0.6), np.zeros(0)])[: int(0.18 * SR)] * g


def riser(dur, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    # prosty filtr górnoprzepustowy rosnący w czasie
    y = np.zeros(n); a = 0.0
    for i in range(0, n, 256):
        k = 0.02 + 0.5 * (i / n) ** 2
        seg = x[i : i + 256]
        y[i : i + 256] = seg - np.convolve(seg, np.ones(8) / 8, "same") * (1 - k)
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / dur) ** 2) / SR) * 0.15
    return (y * 0.3 + sweep) * (t / dur) ** 2 * g


def sparkle(g=1.0):
    s = np.zeros(int(0.8 * SR))
    for k, m in enumerate((81, 84, 88)):
        n = int(0.6 * SR); t = np.arange(n) / SR
        tone = np.sin(2 * np.pi * hz(m) * t) * env(n, 0.002, 0.25)
        i = int(k * 0.05 * SR); s[i : i + n] += tone * 0.25
    return s * g


music = Bus()
sfx = Bus()

# ---------- muzyka ----------
# progresja a-moll: Am  F  Dm  E  (po 2 takty = 4 s)
CHORDS = [(57, [57, 60, 64]), (53, [53, 57, 60]), (50, [50, 53, 57]), (52, [52, 56, 59])]
BREAK = (19.55, 20.80)   # "Ale czy to boli?" – cisza w muzyce
SOFT = (20.80, 27.00)    # łagodniej przy uspokojeniu
END = 28.10

t = 0.0
bar = 0
while t < END:
    root, notes = CHORDS[(bar // 2) % 4]
    for b in range(4):  # 4 bity na takt
        tb = t + b * BEAT
        if tb >= END:
            break
        in_break = BREAK[0] <= tb < BREAK[1]
        soft = SOFT[0] <= tb < SOFT[1]
        if in_break:
            continue
        if not soft and tb >= 0.9:
            music.add(kick(0.8), tb)
        elif soft and b in (0, 2):
            music.add(kick(0.45), tb)
        for s16 in range(4):
            ts = tb + s16 * BEAT / 4
            if BREAK[0] <= ts < BREAK[1] or ts >= END:
                continue
            music.add(tick(), ts, gain=(1.0 if s16 == 2 else 0.55), pan=0.25 if s16 % 2 else -0.25)
        for e in range(2):
            te = tb + e * BEAT / 2
            if BREAK[0] <= te < BREAK[1] or te >= END or te < 0.9:
                continue
            music.add(bass(hz(root - 12), BEAT / 2), te, gain=0.55 if soft else 1.0)
        arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[1] + 12]
        for e in range(4):
            te = tb + e * BEAT / 4
            if BREAK[0] <= te < BREAK[1] or te >= END or te < 2.9:
                continue
            music.add(pulse(hz(arp[e]), 0.2), te, pan=0.35 if e % 2 else -0.35)
    if t < BREAK[0] - 0.1 or t >= BREAK[1]:
        d = min(2 * 4 * BEAT, END - t) if bar % 2 == 0 else 0
        if d > 0.5:
            s = t if not (t < BREAK[0] < t + d) else t
            dd = min(d, BREAK[0] - t) if t < BREAK[0] < t + d else d
            music.add(pad([hz(n) for n in notes], dd), s, gain=1.0)
    t += 4 * BEAT
    bar += 1

# drone pod całym filmem (bez przerwy)
n = int(END * SR); tt = np.arange(n) / SR
drone = (np.sin(2 * np.pi * hz(33) * tt) + 0.4 * np.sin(2 * np.pi * hz(45) * tt)) * 0.06
drone *= np.minimum(1, tt / 0.05) * np.minimum(1, (END - tt) / 1.2)
music.add(drone, 0)

music.add(pad([hz(n) for n in CHORDS[1][1]], 3.2), 20.8)
# finałowy akord
music.add(pad([hz(57), hz(60), hz(64), hz(69)], 1.5), END, gain=1.3)
music.add(kick(1.0), END)

# ---------- efekty (czasy z lektor.json) ----------
SFX = "public/sfx/"
whoosh = load(SFX + "whoosh.wav")
boom = load(SFX + "boom.wav")

sfx.add(sub_boom(0.9), 0.0)
sfx.add(metal_hit(0.9, 1500), 0.02)
sfx.add(ratchet(7, 0.065, 0.8), 0.92)
for tw in (2.93, 4.40, 8.05, 12.03, 16.27, 23.68, 26.98):
    sfx.add(whoosh, tw - 0.12, gain=0.55)
sfx.add(metal_hit(0.9, 1100), 4.42)
sfx.add(sub_boom(0.45), 4.42)
sfx.add(ratchet(8, 0.08, 0.6), 5.28)
sfx.add(metal_hit(0.8, 1200), 3.52)
sfx.add(boom, 3.52, gain=0.5)
for k, tp in enumerate((5.38, 5.62, 5.86)):
    sfx.add(metal_hit(0.75, 1900 + 150 * k), tp, pan=(-0.4, 0.4, 0.4)[k])
sfx.add(ratchet(5, 0.05, 0.7), 6.60)
sfx.add(metal_hit(1.0, 900), 7.30)
sfx.add(sub_boom(0.5), 7.30)
sfx.add(beep(1400, 0.07, 0.8), 9.17)
sfx.add(beep(1400, 0.07, 0.8), 9.53)
sfx.add(sparkle(0.9), 11.18)
sfx.add(riser(2.6, 0.6), 12.15)
sfx.add(sub_boom(0.8), 14.74)
for k in range(3):
    sfx.add(beep(880, 0.11, 1.0), 14.76 + k * 0.16)
sfx.add(ratchet(6, 0.06, 0.8), 16.35)
sfx.add(metal_hit(1.0, 800), 18.62)
sfx.add(boom, 18.62, gain=0.6)
for k in range(3):
    sfx.add(heartbeat(0.8), 19.62 + k * 0.42)
for k in range(8):
    sfx.add(beep(1046, 0.1, 0.55), 20.95 + k * 0.78)
for k, tp in enumerate((24.51, 24.78, 25.05)):
    sfx.add(beep(1600 + 200 * k, 0.05, 0.6), tp)
sfx.add(sparkle(0.8), 25.93)
sfx.add(sub_boom(0.7), END)
sfx.add(sparkle(0.7), END + 0.05)

# ---------- lektor + ducking ----------
voice = load("public/mayfield/lektor.wav")
v = np.zeros(N); v[: min(N, len(voice))] = voice[:N]
# obwiednia głosu (RMS 30 ms) -> ducking muzyki do ~ -18 dB pod głosem
win = int(0.03 * SR)
rms = np.sqrt(np.convolve(v ** 2, np.ones(win) / win, "same"))
active = (rms > 0.01).astype(float)
k = int(0.15 * SR)
active = np.convolve(active, np.ones(k) / k, "same").clip(0, 1)
active = np.maximum(active, np.convolve(active, np.ones(int(0.25 * SR)) / int(0.25 * SR), "same"))
duck = 10 ** (-12 / 20) * active + 1.0 * (1 - active)  # muzyka jest już cicha: razem ok. -18 dB względem głosu

m = music.x / max(1e-9, np.abs(music.x).max()) * 0.5
m *= duck[:, None]
s = sfx.x / max(1e-9, np.abs(sfx.x).max()) * 0.55
vv = v / max(1e-9, np.abs(v).max()) * 0.95
mix = m * 0.55 + s + vv[:, None]
mix = np.tanh(mix * 0.95) / np.tanh(0.95 * 1.05)
mix /= max(1.0, np.abs(mix).max() / 0.97)

with wave.open("public/mayfield/mix.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("ok", DUR)
