#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  BEETHOVEN'S FATE SYMPHONY No.5 — KEYGEN MUSIC EDITION          ║
║  Pure math. No samples. No libraries. Just sin() and integers.   ║
║                                                                  ║
║  Technique: Bytebeat / Demoscene synthesis                       ║
║  Engine   : Additive harmonics + ADSR + Reverb + Bitcrush        ║
║  Author   : RussellCooper  github.com/RussellCooper-DJZ          ║
╚══════════════════════════════════════════════════════════════════╝

  "Thus Fate knocks at the door." — Beethoven

  The entire symphony is encoded as integer arithmetic on a single
  time variable t. No audio files. No MIDI. Just math.
"""

import argparse, struct, math, sys, os, time, wave, array

# ─────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────
SAMPLE_RATE = 44100
CHANNELS    = 1
BIT_DEPTH   = 16
AMP_MAX     = 32767
TAU         = math.tau          # 2π

# ─────────────────────────────────────────────────────────────────
#  MUSIC THEORY ENGINE
# ─────────────────────────────────────────────────────────────────
def midi_to_hz(note: int) -> float:
    """Convert MIDI note number to frequency (Hz). A4 = 69 = 440Hz."""
    return 440.0 * (2.0 ** ((note - 69) / 12.0))

# Note name → MIDI number
NOTE = {n: i for i, n in enumerate(
    ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'], start=0)}

def note(name: str, octave: int) -> int:
    """e.g. note('G', 4) → 67"""
    return NOTE[name] + (octave + 1) * 12

# ─────────────────────────────────────────────────────────────────
#  WAVEFORM GENERATORS  (the soul of keygen music)
# ─────────────────────────────────────────────────────────────────
def sine(t: float, freq: float, phase: float = 0.0) -> float:
    return math.sin(TAU * freq * t + phase)

def square(t: float, freq: float, duty: float = 0.5) -> float:
    """PWM square wave — classic keygen sound"""
    return 1.0 if (freq * t % 1.0) < duty else -1.0

def sawtooth(t: float, freq: float) -> float:
    """Sawtooth — rich in harmonics, aggressive tone"""
    return 2.0 * (freq * t % 1.0) - 1.0

def triangle(t: float, freq: float) -> float:
    """Triangle — softer than square, warmer than sine"""
    p = freq * t % 1.0
    return 4.0 * p - 1.0 if p < 0.5 else 3.0 - 4.0 * p

def organ(t: float, freq: float) -> float:
    """Additive synthesis: fundamental + harmonics (Hammond-style)"""
    return (
        1.00 * sine(t, freq)        +
        0.50 * sine(t, freq * 2)    +
        0.25 * sine(t, freq * 3)    +
        0.12 * sine(t, freq * 4)    +
        0.06 * sine(t, freq * 5)    +
        0.03 * sine(t, freq * 6)    +
        0.015* sine(t, freq * 7)
    ) / 1.975

def strings(t: float, freq: float) -> float:
    """Detuned sawtooth pair — lush string ensemble"""
    detune = 0.003
    return (sawtooth(t, freq * (1 - detune)) +
            sawtooth(t, freq * (1 + detune)) +
            0.3 * sawtooth(t, freq * 2)) / 2.3

def brass(t: float, freq: float) -> float:
    """Square + odd harmonics — trumpet/horn character"""
    return (
        square(t, freq,      duty=0.48) * 1.0 +
        square(t, freq * 3,  duty=0.45) * 0.3 +
        square(t, freq * 5,  duty=0.42) * 0.1
    ) / 1.4

def bass(t: float, freq: float) -> float:
    """Sub-bass: sine fundamental + second harmonic"""
    return 0.7 * sine(t, freq) + 0.3 * sine(t, freq * 2)

def timpani(t: float, freq: float, age: float) -> float:
    """Pitched percussion: decaying inharmonic partials"""
    decay = math.exp(-age * 4.0)
    pitch_drop = freq * (1.0 + 0.3 * math.exp(-age * 8.0))
    return decay * (
        0.6 * sine(t, pitch_drop) +
        0.3 * sine(t, pitch_drop * 1.51) +
        0.1 * sine(t, pitch_drop * 2.0)
    )

# ─────────────────────────────────────────────────────────────────
#  ADSR ENVELOPE
# ─────────────────────────────────────────────────────────────────
def adsr(age: float, duration: float,
         attack=0.01, decay=0.05, sustain=0.75, release=0.12) -> float:
    """
    age      : seconds since note onset
    duration : total note duration (seconds)
    Returns amplitude multiplier ∈ [0, 1]
    """
    rel_start = max(0.0, duration - release)
    if age < 0:
        return 0.0
    elif age < attack:
        return age / attack
    elif age < attack + decay:
        return 1.0 - (1.0 - sustain) * (age - attack) / decay
    elif age < rel_start:
        return sustain
    elif age < duration:
        return sustain * (1.0 - (age - rel_start) / release)
    else:
        return 0.0

# ─────────────────────────────────────────────────────────────────
#  REVERB  (Schroeder allpass + comb filter approximation)
# ─────────────────────────────────────────────────────────────────
class Reverb:
    def __init__(self, room=0.6, damp=0.4, wet=0.25, sr=SAMPLE_RATE):
        self.wet  = wet
        self.dry  = 1.0 - wet
        # Four comb filters (prime-ish delay lengths)
        delays = [int(sr * d) for d in [0.0297, 0.0371, 0.0411, 0.0437]]
        self.combs  = [[0.0] * d for d in delays]
        self.comb_i = [0] * 4
        self.g      = [room * (1 - damp * i / 4) for i in range(4)]
        # Two allpass filters
        ap_delays   = [int(sr * d) for d in [0.005, 0.0017]]
        self.aps    = [[0.0] * d for d in ap_delays]
        self.ap_i   = [0] * 2

    def process(self, x: float) -> float:
        # Comb filters in parallel
        comb_out = 0.0
        for k in range(4):
            buf, idx, g = self.combs[k], self.comb_i[k], self.g[k]
            y = buf[idx]
            buf[idx] = x + g * y
            self.comb_i[k] = (idx + 1) % len(buf)
            comb_out += y
        comb_out /= 4.0
        # Allpass filters in series
        ap_out = comb_out
        for k in range(2):
            buf, idx = self.aps[k], self.ap_i[k]
            g = 0.7
            y = buf[idx]
            v = ap_out + g * y
            buf[idx] = v
            self.ap_i[k] = (idx + 1) % len(buf)
            ap_out = y - g * v
        return self.dry * x + self.wet * ap_out

# ─────────────────────────────────────────────────────────────────
#  BEETHOVEN'S FATE SYMPHONY No.5, Op.67 — SCORE DATA
#  Movement I: Allegro con brio  ♩= 108  (C minor)
#
#  Encoding: (midi_note, duration_beats, velocity, instrument)
#  REST = -1
#  Instruments: 'str'=strings, 'brass'=brass, 'bass'=bass, 'timp'=timpani
# ─────────────────────────────────────────────────────────────────

BPM      = 108
BEAT     = 60.0 / BPM          # seconds per beat
REST     = -1

# Helper: build note number
G4  = note('G', 4)   # 67
Eb4 = note('D#',4)   # 63
F4  = note('F', 4)   # 65
D4  = note('D', 4)   # 62
C4  = note('C', 4)   # 60
B3  = note('B', 3)   # 59
Bb3 = note('A#',3)   # 58
Ab3 = note('G#',3)   # 56
G3  = note('G', 3)   # 55
F3  = note('F', 3)   # 53
Eb3 = note('D#',3)   # 51
D3  = note('D', 3)   # 50
C3  = note('C', 3)   # 48
G2  = note('G', 2)   # 43
C2  = note('C', 2)   # 36
Eb5 = note('D#',5)   # 75
D5  = note('D', 5)   # 74
C5  = note('C', 5)   # 72
Bb4 = note('A#',4)   # 70
Ab4 = note('G#',4)   # 68
F5  = note('F', 5)   # 77
G5  = note('G', 5)   # 79
B4  = note('B', 4)   # 71
A4  = note('A', 4)   # 69
E4  = note('E', 4)   # 64

# ── FATE MOTIF: "da da da DAAA" ──────────────────────────────────
# Three short + one long: ♩♩♩𝅗𝅥  (G G G Eb, then F F F D)
FATE_MOTIF_STR = [
    # Bar 1-2: G G G Eb (fortissimo)
    (G4,  0.25, 1.0, 'str'),
    (G4,  0.25, 1.0, 'str'),
    (G4,  0.25, 1.0, 'str'),
    (Eb4, 2.0,  1.0, 'str'),
    (REST,0.25, 0.0, 'str'),
    # Bar 3-4: F F F D
    (F4,  0.25, 1.0, 'str'),
    (F4,  0.25, 1.0, 'str'),
    (F4,  0.25, 1.0, 'str'),
    (D4,  2.0,  1.0, 'str'),
    (REST,0.25, 0.0, 'str'),
]

FATE_MOTIF_BRASS = [
    (G4,  0.25, 0.9, 'brass'),
    (G4,  0.25, 0.9, 'brass'),
    (G4,  0.25, 0.9, 'brass'),
    (Eb4, 2.0,  0.9, 'brass'),
    (REST,0.25, 0.0, 'brass'),
    (F4,  0.25, 0.9, 'brass'),
    (F4,  0.25, 0.9, 'brass'),
    (F4,  0.25, 0.9, 'brass'),
    (D4,  2.0,  0.9, 'brass'),
    (REST,0.25, 0.0, 'brass'),
]

# ── DEVELOPMENT SECTION ──────────────────────────────────────────
DEVELOPMENT_STR = [
    # Ascending sequence
    (C4,  0.5,  0.8, 'str'), (D4,  0.5, 0.8, 'str'),
    (Eb4, 0.5,  0.9, 'str'), (F4,  0.5, 0.9, 'str'),
    (G4,  0.5,  1.0, 'str'), (Ab4, 0.5, 1.0, 'str'),
    (Bb4, 0.5,  0.9, 'str'), (C5,  0.5, 0.9, 'str'),
    # Fate motif in upper register
    (G5,  0.25, 1.0, 'str'),
    (G5,  0.25, 1.0, 'str'),
    (G5,  0.25, 1.0, 'str'),
    (Eb5, 2.0,  1.0, 'str'),
    (REST,0.25, 0.0, 'str'),
    (F5,  0.25, 0.9, 'str'),
    (F5,  0.25, 0.9, 'str'),
    (F5,  0.25, 0.9, 'str'),
    (D5,  2.0,  0.9, 'str'),
    (REST,0.25, 0.0, 'str'),
    # Descending chromatic
    (C5,  0.33, 0.8, 'str'), (B4,  0.33, 0.8, 'str'),
    (Bb4, 0.33, 0.8, 'str'), (Ab4, 0.5,  0.9, 'str'),
    (G4,  0.5,  0.9, 'str'), (F4,  0.5,  0.8, 'str'),
    (Eb4, 0.5,  0.8, 'str'), (D4,  0.5,  0.7, 'str'),
    (C4,  1.0,  0.7, 'str'),
]

# ── SECOND THEME (relative major: Eb major) ──────────────────────
SECOND_THEME = [
    (Eb4, 1.0, 0.7, 'str'), (F4,  0.5, 0.7, 'str'), (G4, 0.5, 0.7, 'str'),
    (Ab4, 1.0, 0.8, 'str'), (Bb4, 0.5, 0.8, 'str'), (C5, 0.5, 0.8, 'str'),
    (Bb4, 0.5, 0.7, 'str'), (Ab4, 0.5, 0.7, 'str'), (G4, 1.0, 0.7, 'str'),
    (F4,  0.5, 0.6, 'str'), (Eb4, 0.5, 0.6, 'str'), (D4, 1.0, 0.6, 'str'),
    (Eb4, 2.0, 0.8, 'str'), (REST,0.5, 0.0, 'str'),
    # Fate motif echo (piano)
    (G4,  0.25, 0.5, 'str'),
    (G4,  0.25, 0.5, 'str'),
    (G4,  0.25, 0.5, 'str'),
    (Eb4, 1.5,  0.5, 'str'),
    (REST,0.25, 0.0, 'str'),
]

# ── BASS LINE ─────────────────────────────────────────────────────
BASS_LINE = [
    (C2,  0.25, 0.8, 'bass'), (C2, 0.25, 0.8, 'bass'),
    (C2,  0.25, 0.8, 'bass'), (C2, 2.0,  0.9, 'bass'),
    (REST,0.25, 0.0, 'bass'),
    (G2,  0.25, 0.7, 'bass'), (G2, 0.25, 0.7, 'bass'),
    (G2,  0.25, 0.7, 'bass'), (G2, 2.0,  0.8, 'bass'),
    (REST,0.25, 0.0, 'bass'),
    # Walking bass
    (C2,  0.5,  0.7, 'bass'), (D3, 0.5, 0.7, 'bass'),
    (Eb3, 0.5,  0.7, 'bass'), (F3, 0.5, 0.7, 'bass'),
    (G3,  0.5,  0.8, 'bass'), (Ab3,0.5, 0.8, 'bass'),
    (G3,  1.0,  0.8, 'bass'),
    (C3,  2.0,  0.9, 'bass'),
]

# ── TIMPANI HITS ──────────────────────────────────────────────────
TIMP_LINE = [
    (G2,  0.25, 1.0, 'timp'), (REST,0.25, 0.0, 'timp'),
    (REST,0.25, 0.0, 'timp'), (G2,  2.0,  1.0, 'timp'),
    (REST,0.25, 0.0, 'timp'),
    (G2,  0.25, 0.9, 'timp'), (REST,0.25, 0.0, 'timp'),
    (REST,0.25, 0.0, 'timp'), (G2,  2.0,  0.9, 'timp'),
    (REST,0.25, 0.0, 'timp'),
    (C2,  0.5,  1.0, 'timp'), (REST,0.5,  0.0, 'timp'),
    (C2,  0.5,  1.0, 'timp'), (REST,0.5,  0.0, 'timp'),
    (G2,  1.0,  0.8, 'timp'),
    (C2,  2.0,  1.0, 'timp'),
]

# ── FULL SCORE: sequence of sections ─────────────────────────────
SCORE = {
    'strings': (
        FATE_MOTIF_STR * 2 +
        DEVELOPMENT_STR +
        SECOND_THEME +
        FATE_MOTIF_STR * 3
    ),
    'brass': (
        FATE_MOTIF_BRASS * 2 +
        [(REST, 0.5, 0.0, 'brass')] * 8 +   # brass rests during 2nd theme
        FATE_MOTIF_BRASS * 3
    ),
    'bass': BASS_LINE * 4,
    'timp':  TIMP_LINE * 4,
}

# ─────────────────────────────────────────────────────────────────
#  SYNTHESIS ENGINE
# ─────────────────────────────────────────────────────────────────
def render_voice(events: list, sr: int = SAMPLE_RATE, max_seconds: float | None = None) -> list:
    """Render a list of note events to a PCM sample buffer.

    ``max_seconds`` creates a deterministic preview without allocating the full
    score. It is the primary memory-control mechanism for low-resource renders.
    """
    total_beats = sum(e[1] for e in events)
    total_samples = int(total_beats * BEAT * sr) + sr  # +1s tail
    if max_seconds is not None:
        total_samples = min(total_samples, max(1, int(max_seconds * sr)))
    buf = [0.0] * total_samples

    t_sample = 0
    for (pitch, dur_beats, vel, inst) in events:
        if t_sample >= total_samples:
            break
        dur_sec = dur_beats * BEAT
        n_samples = min(int(dur_sec * sr), total_samples - t_sample)

        if pitch == REST or vel == 0.0:
            t_sample += n_samples
            continue

        freq = midi_to_hz(pitch)

        for i in range(n_samples):
            t = (t_sample + i) / sr
            age = i / sr

            # Select waveform by instrument
            if inst == 'str':
                wave_val = strings(t, freq)
                env = adsr(age, dur_sec, attack=0.04, decay=0.1,
                           sustain=0.8, release=0.15)
            elif inst == 'brass':
                wave_val = brass(t, freq)
                env = adsr(age, dur_sec, attack=0.02, decay=0.08,
                           sustain=0.85, release=0.1)
            elif inst == 'bass':
                wave_val = bass(t, freq)
                env = adsr(age, dur_sec, attack=0.01, decay=0.05,
                           sustain=0.9, release=0.08)
            elif inst == 'timp':
                wave_val = timpani(t, freq, age)
                env = 1.0  # timpani has internal decay
            else:
                wave_val = sine(t, freq)
                env = adsr(age, dur_sec)

            idx = t_sample + i
            if idx < total_samples:
                buf[idx] += wave_val * env * vel

        t_sample += n_samples

    return buf

def mix_voices(voices: dict, sr: int = SAMPLE_RATE) -> list:
    """Mix multiple voice buffers with per-instrument levels."""
    levels = {'strings': 0.45, 'brass': 0.30, 'bass': 0.20, 'timp': 0.15}
    max_len = max(len(v) for v in voices.values())
    mixed = [0.0] * max_len

    for name, buf in voices.items():
        level = levels.get(name, 0.25)
        for i, s in enumerate(buf):
            mixed[i] += s * level

    return mixed

def normalize(buf: list, headroom_db: float = -1.0) -> list:
    """Peak normalize with headroom."""
    peak = max(abs(s) for s in buf)
    if peak == 0:
        return buf
    target = 10 ** (headroom_db / 20.0)
    scale = target / peak
    return [s * scale for s in buf]

def apply_reverb(buf: list, **kwargs) -> list:
    """Apply Schroeder reverb to buffer."""
    rev = Reverb(**kwargs)
    return [rev.process(s) for s in buf]

def apply_limiter(buf: list, threshold: float = 0.95) -> list:
    """Soft-knee limiter to prevent clipping."""
    out = []
    for s in buf:
        if abs(s) > threshold:
            sign = 1.0 if s > 0 else -1.0
            excess = abs(s) - threshold
            s = sign * (threshold + excess / (1.0 + excess))
        out.append(s)
    return out

def to_pcm16(buf: list) -> bytes:
    """Convert float buffer [-1,1] to 16-bit PCM bytes."""
    samples = array.array('h')
    for s in buf:
        val = max(-AMP_MAX, min(AMP_MAX, int(s * AMP_MAX)))
        samples.append(val)
    return samples.tobytes()

# ─────────────────────────────────────────────────────────────────
#  BYTEBEAT EASTER EGG  (one-liner fate motif)
# ─────────────────────────────────────────────────────────────────
BYTEBEAT_ONELINER = r"""
# ── BYTEBEAT ONE-LINER (Fate Motif) ─────────────────────────────
# The entire fate motif encoded as a single integer expression:
#   python3 -c "import sys; [sys.stdout.buffer.write(bytes([(
#     (t>>10&1)*((t*[196,196,196,156,175,175,175,147][t>>11&7]>>8)&255)
#   )])) for t in range(1<<18)]" | aplay -r8000 -c1 -f U8
#
# Breakdown:
#   t>>10 & 1          → square wave gate (note on/off)
#   t>>11 & 7          → selects one of 8 frequencies (fate motif pitches)
#   [196,196,196,156,  → G4,G4,G4,Eb4 (da-da-da-DAA)
#    175,175,175,147]  → F4,F4,F4,D4  (da-da-da-DAA)
#   t * freq >> 8      → integer oscillator (bytebeat core)
# ────────────────────────────────────────────────────────────────
"""

# ─────────────────────────────────────────────────────────────────
#  PROGRESS BAR
# ─────────────────────────────────────────────────────────────────
def progress(label: str, done: int, total: int, width: int = 40):
    pct = done / total
    filled = int(width * pct)
    bar = '█' * filled + '░' * (width - filled)
    sys.stdout.write(f'\r  {label}  [{bar}] {pct*100:5.1f}%')
    sys.stdout.flush()

# ─────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a mathematical Fate Symphony WAV file.")
    parser.add_argument("--output", default=None, help="Output WAV path (default: fate_symphony.wav)")
    parser.add_argument("--sample-rate", type=int, default=SAMPLE_RATE, help="Output sample rate in Hz")
    parser.add_argument("--preview-seconds", type=float, default=None, help="Render only the first N seconds")
    parser.add_argument("--no-reverb", action="store_true", help="Skip the optional reverb pass")
    parser.add_argument("--lite", action="store_true", help="Use the low-memory preview profile")
    args = parser.parse_args()
    if args.sample_rate < 1000:
        parser.error("--sample-rate must be at least 1000 Hz")
    if args.preview_seconds is not None and args.preview_seconds <= 0:
        parser.error("--preview-seconds must be positive")
    if args.lite:
        args.sample_rate = min(args.sample_rate, 11025)
        args.preview_seconds = args.preview_seconds or 15.0
        args.no_reverb = True
    return args


def main():
    args = parse_args()
    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║  BEETHOVEN OP.67 — FATE SYMPHONY  [ KEYGEN EDITION ] ║")
    print("  ║  Synthesizing from pure mathematics...               ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print()
    print(BYTEBEAT_ONELINER)

    voices_raw = {}
    voice_names = list(SCORE.keys())

    for i, name in enumerate(voice_names):
        print(f"  Rendering voice: {name:<10}", end='')
        sys.stdout.flush()
        t0 = time.time()
        voices_raw[name] = render_voice(
            SCORE[name], sr=args.sample_rate, max_seconds=args.preview_seconds
        )
        elapsed = time.time() - t0
        samples = len(voices_raw[name])
        print(f"  {samples:>8,} samples  ({elapsed:.2f}s)")

    print()
    print("  Mixing voices...", end='', flush=True)
    mixed = mix_voices(voices_raw)
    print(f"  {len(mixed):,} samples total")

    if args.no_reverb:
        print("  Reverb: skipped (low-resource profile)")
    else:
        print("  Applying reverb...", end='', flush=True)
        mixed = apply_reverb(mixed, room=0.55, damp=0.45, wet=0.22)
        print("  done")

    print("  Normalizing + limiting...", end='', flush=True)
    mixed = normalize(mixed, headroom_db=-2.0)
    mixed = apply_limiter(mixed, threshold=0.92)
    print("  done")

    # Write WAV
    out_path = args.output or os.path.join(os.path.dirname(__file__), 'fate_symphony.wav')
    pcm = to_pcm16(mixed)
    with wave.open(out_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(args.sample_rate)
        wf.writeframes(pcm)

    duration = len(mixed) / SAMPLE_RATE
    size_kb  = os.path.getsize(out_path) / 1024

    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║  OUTPUT : fate_symphony.wav                          ║")
    print(f"  ║  Duration: {duration:>6.1f}s   Size: {size_kb:>7.1f} KB              ║")
    print(f"  ║  Sample rate: {args.sample_rate} Hz   Bit depth: {BIT_DEPTH}-bit         ║")
    print(f"  ║  Voices: strings + brass + bass + timpani            ║")
    print(f"  ║  Engine: additive synthesis + ADSR + Schroeder reverb║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print()
    print("  Play with:  aplay fate_symphony.wav")
    print("              ffplay fate_symphony.wav")
    print("              vlc fate_symphony.wav")
    print()

if __name__ == '__main__':
    main()
