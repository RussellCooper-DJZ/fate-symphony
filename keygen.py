#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ██████╗ ██╗   ██╗███████╗███████╗███████╗██╗     ██╗              ║
║   ██╔══██╗██║   ██║██╔════╝██╔════╝██╔════╝██║     ██║              ║
║   ██████╔╝██║   ██║███████╗███████╗█████╗  ██║     ██║              ║
║   ██╔══██╗██║   ██║╚════██║╚════██║██╔══╝  ██║     ██║              ║
║   ██║  ██║╚██████╔╝███████║███████║███████╗███████╗███████╗         ║
║   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝╚══════╝         ║
║                                                                      ║
║        C O O P E R   —   K E Y G E N   M U S I C   E D I T I O N   ║
║                  Beethoven Op.67 Fate Symphony                       ║
╚══════════════════════════════════════════════════════════════════════╝

  Keil-style keygen with Matrix rain, ASCII art, and music synthesis.
  Author: RussellCooper  |  github.com/RussellCooper-DJZ
"""

import sys, os, time, random, math, threading, struct, wave, array

# ── Terminal color codes ──────────────────────────────────────────
class C:
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    BLINK   = '\033[5m'

    BLACK   = '\033[30m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'

    BRIGHT_GREEN  = '\033[92m'
    BRIGHT_CYAN   = '\033[96m'
    BRIGHT_WHITE  = '\033[97m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_RED    = '\033[91m'
    BRIGHT_BLUE   = '\033[94m'

    BG_BLACK  = '\033[40m'
    BG_GREEN  = '\033[42m'

    @staticmethod
    def rgb(r, g, b, bg=False):
        """True-color escape code."""
        code = 48 if bg else 38
        return f'\033[{code};2;{r};{g};{b}m'

    @staticmethod
    def move(row, col):
        return f'\033[{row};{col}H'

    @staticmethod
    def clear():
        return '\033[2J\033[H'

    @staticmethod
    def hide_cursor():
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()

    @staticmethod
    def show_cursor():
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()

    @staticmethod
    def clear_screen():
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()

def term_size():
    try:
        import shutil
        s = shutil.get_terminal_size((120, 40))
        return s.columns, s.lines
    except:
        return 120, 40

# ── ASCII Art Logo ────────────────────────────────────────────────
LOGO = r"""
 ██████╗ ██╗   ██╗███████╗███████╗███████╗██╗     ██╗      ██████╗ ██████╗  ██████╗ ██████╗ ███████╗██████╗
 ██╔══██╗██║   ██║██╔════╝██╔════╝██╔════╝██║     ██║     ██╔════╝██╔═══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗
 ██████╔╝██║   ██║███████╗███████╗█████╗  ██║     ██║     ██║     ██║   ██║██║   ██║██████╔╝█████╗  ██████╔╝
 ██╔══██╗██║   ██║╚════██║╚════██║██╔══╝  ██║     ██║     ██║     ██║   ██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗
 ██║  ██║╚██████╔╝███████║███████║███████╗███████╗███████╗╚██████╗╚██████╔╝╚██████╔╝██║     ███████╗██║  ██║
 ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝
"""

LOGO_SMALL = [
    r" ____  _   _ ____ ____  _____ _     _     ",
    r"|  _ \| | | / ___/ ___|| ____| |   | |    ",
    r"| |_) | | | \___ \___ \|  _| | |   | |    ",
    r"|  _ <| |_| |___) |__) | |___| |___| |___ ",
    r"|_| \_\\___/|____/____/|_____|_____|_____|",
    r"   C O O P E R   K E Y G E N   E D I T I O N   ",
]

FATE_ASCII = [
    r"    ___       _       _                         ",
    r"   / __\ __ _| |_ ___| |                        ",
    r"  / _\ / _` | __/ _ \ |                        ",
    r" / / | (_| | ||  __/_|                        ",
    r" \/   \__,_|\__\___(_)                        ",
    r"  S y m p h o n y   N o . 5   O p . 6 7      ",
]

# ── Matrix Rain ───────────────────────────────────────────────────
MATRIX_CHARS = (
    'ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ'
    '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '!@#$%^&*()_+-=[]{}|;:,.<>?'
    '∑∏∫∂∇∆√∞≈≠≤≥±×÷'
)

class MatrixRain:
    def __init__(self, width, height):
        self.W = width
        self.H = height
        # Each column: (head_row, tail_length, speed, chars_list)
        self.cols = []
        for x in range(width):
            self.cols.append({
                'head': random.randint(-height, 0),
                'tail': random.randint(6, 20),
                'speed': random.uniform(0.3, 1.2),
                'timer': 0.0,
                'chars': [random.choice(MATRIX_CHARS) for _ in range(height)],
                'active': random.random() > 0.4,
            })
        self.frame_buf = [[(' ', 0) for _ in range(width)] for _ in range(height)]

    def step(self, dt):
        """Advance rain by dt seconds, return list of (row, col, char, intensity)."""
        changes = []
        for x, col in enumerate(self.cols):
            if not col['active']:
                col['timer'] += dt
                if col['timer'] > random.uniform(0.5, 3.0):
                    col['active'] = True
                    col['timer'] = 0
                    col['head'] = -col['tail']
                continue

            col['timer'] += dt
            if col['timer'] < 1.0 / col['speed']:
                continue
            col['timer'] = 0

            # Advance head
            col['head'] += 1

            # Randomly mutate a char in the column
            if random.random() < 0.15:
                row = random.randint(0, self.H - 1)
                col['chars'][row] = random.choice(MATRIX_CHARS)

            # Draw tail
            for dy in range(col['tail'] + 2):
                row = col['head'] - dy
                if 0 <= row < self.H:
                    if dy == 0:
                        intensity = 3   # head: bright white
                    elif dy == 1:
                        intensity = 2   # near head: bright green
                    elif dy < col['tail'] // 2:
                        intensity = 1   # mid: green
                    else:
                        intensity = 0   # tail: dim green
                    ch = col['chars'][row]
                    changes.append((row, x, ch, intensity))

            # Erase just-passed cell
            erase_row = col['head'] - col['tail'] - 1
            if 0 <= erase_row < self.H:
                changes.append((erase_row, x, ' ', -1))

            # Reset column when off screen
            if col['head'] - col['tail'] > self.H:
                col['active'] = False
                col['head'] = -col['tail']
                col['timer'] = 0

        return changes

    def render_changes(self, changes):
        """Write matrix rain changes to terminal."""
        out = []
        for (row, col, ch, intensity) in changes:
            out.append(C.move(row + 1, col + 1))
            if intensity == 3:
                out.append(C.BOLD + C.BRIGHT_WHITE)
            elif intensity == 2:
                out.append(C.BOLD + C.BRIGHT_GREEN)
            elif intensity == 1:
                out.append(C.GREEN)
            elif intensity == 0:
                out.append(C.DIM + C.GREEN)
            else:
                out.append(C.BLACK + C.BG_BLACK)
            # Encode to avoid multi-byte issues
            try:
                out.append(ch)
            except:
                out.append('?')
            out.append(C.RESET)
        sys.stdout.write(''.join(out))
        sys.stdout.flush()

# ── Progress Bar ──────────────────────────────────────────────────
def draw_progress_bar(row, col, width, pct, label='', color=C.BRIGHT_GREEN):
    filled = int(width * pct)
    empty  = width - filled
    bar = '█' * filled + '▒' * empty
    pct_str = f'{pct*100:5.1f}%'
    line = f'{color}{C.BOLD}[{bar}] {pct_str}{C.RESET}'
    if label:
        line = f'{C.BRIGHT_CYAN}{label:<28}{C.RESET} {line}'
    sys.stdout.write(C.move(row, col) + line)
    sys.stdout.flush()

# ── Hex dump scrolling effect ─────────────────────────────────────
def random_hex_line(width=60):
    addr = random.randint(0, 0xFFFF)
    hexbytes = ' '.join(f'{random.randint(0,255):02X}' for _ in range(16))
    ascii_part = ''.join(chr(random.randint(32, 126)) if random.random() > 0.3 else '.'
                         for _ in range(16))
    return f'{addr:04X}:  {hexbytes}  |{ascii_part}|'

# ── Serial number generator ───────────────────────────────────────
def gen_serial():
    """Generate a fake but plausible-looking serial number."""
    groups = []
    for _ in range(5):
        g = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=5))
        groups.append(g)
    return '-'.join(groups)

def gen_hash():
    return ''.join(random.choices('0123456789ABCDEF', k=32))

# ── Music synthesis (minimal inline version for the keygen) ──────
TAU = math.tau
SR  = 44100

def _sine(t, f): return math.sin(TAU * f * t)
def _sq(t, f):   return 1.0 if (f * t % 1.0) < 0.5 else -1.0
def _saw(t, f):  return 2.0 * (f * t % 1.0) - 1.0

def _adsr(age, dur, a=0.02, d=0.05, s=0.75, r=0.10):
    rs = max(0, dur - r)
    if age < 0: return 0.0
    if age < a: return age / a
    if age < a + d: return 1.0 - (1.0 - s) * (age - a) / d
    if age < rs: return s
    if age < dur: return s * (1.0 - (age - rs) / r)
    return 0.0

def _note(name, octave):
    names = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
    return names[name] + (octave + 1) * 12

def _hz(midi): return 440.0 * (2.0 ** ((midi - 69) / 12.0))

# Fate motif: G G G Eb  F F F D  (C minor, BPM=120)
BPM   = 120
BEAT  = 60.0 / BPM
REST  = -1

G4  = _note('G',  4)
Eb4 = _note('D#', 4)
F4  = _note('F',  4)
D4  = _note('D',  4)
C3  = _note('C',  3)
G2  = _note('G',  2)
C5  = _note('C',  5)
Eb5 = _note('D#', 5)
F5  = _note('F',  5)
D5  = _note('D',  5)
G5  = _note('G',  5)
Bb4 = _note('A#', 4)
Ab4 = _note('G#', 4)
C4  = _note('C',  4)
D3  = _note('D',  3)
Eb3 = _note('D#', 3)
G3  = _note('G',  3)

MELODY = [
    # ── Fate motif ×3 ──
    (G4,0.25,1.0),(G4,0.25,1.0),(G4,0.25,1.0),(Eb4,2.0,1.0),(REST,0.25,0),
    (F4,0.25,1.0),(F4,0.25,1.0),(F4,0.25,1.0),(D4, 2.0,1.0),(REST,0.25,0),
    (G4,0.25,1.0),(G4,0.25,1.0),(G4,0.25,1.0),(Eb4,2.0,1.0),(REST,0.25,0),
    (F4,0.25,1.0),(F4,0.25,1.0),(F4,0.25,1.0),(D4, 2.0,1.0),(REST,0.25,0),
    # ── Development ──
    (C4,0.5,0.8),(D4,0.5,0.8),(Eb4,0.5,0.9),(F4,0.5,0.9),
    (G4,0.5,1.0),(Ab4,0.5,1.0),(Bb4,0.5,0.9),(C5,0.5,0.9),
    (G5,0.25,1.0),(G5,0.25,1.0),(G5,0.25,1.0),(Eb5,2.0,1.0),(REST,0.25,0),
    (F5,0.25,0.9),(F5,0.25,0.9),(F5,0.25,0.9),(D5, 2.0,0.9),(REST,0.25,0),
    # ── Recapitulation ──
    (G4,0.25,1.0),(G4,0.25,1.0),(G4,0.25,1.0),(Eb4,2.0,1.0),(REST,0.25,0),
    (F4,0.25,1.0),(F4,0.25,1.0),(F4,0.25,1.0),(D4, 2.0,1.0),(REST,0.25,0),
    (C4,3.0,1.0),(REST,0.5,0),
]

BASS_LINE = [
    (G2,0.25,0.8),(G2,0.25,0.8),(G2,0.25,0.8),(G2,2.0,0.9),(REST,0.25,0),
    (G2,0.25,0.7),(G2,0.25,0.7),(G2,0.25,0.7),(G2,2.0,0.8),(REST,0.25,0),
    (G2,0.25,0.8),(G2,0.25,0.8),(G2,0.25,0.8),(G2,2.0,0.9),(REST,0.25,0),
    (G2,0.25,0.7),(G2,0.25,0.7),(G2,0.25,0.7),(G2,2.0,0.8),(REST,0.25,0),
    (C3,0.5,0.7),(D3,0.5,0.7),(Eb3,0.5,0.7),(F4,0.5,0.7),
    (G3,0.5,0.8),(Ab4,0.5,0.8),(Bb4,0.5,0.7),(C4,0.5,0.7),
    (G2,0.25,0.8),(G2,0.25,0.8),(G2,0.25,0.8),(G2,2.0,0.9),(REST,0.25,0),
    (G2,0.25,0.7),(G2,0.25,0.7),(G2,0.25,0.7),(G2,2.0,0.8),(REST,0.25,0),
    (G2,0.25,0.8),(G2,0.25,0.8),(G2,0.25,0.8),(G2,2.0,0.9),(REST,0.25,0),
    (G2,0.25,0.7),(G2,0.25,0.7),(G2,0.25,0.7),(G2,2.0,0.8),(REST,0.25,0),
    (C3,3.0,0.9),(REST,0.5,0),
]

def _render_voice(events, waveform='str'):
    total = int(sum(e[1] for e in events) * BEAT * SR) + SR
    buf = [0.0] * total
    ts = 0
    for (pitch, dur_b, vel) in events:
        dur_s = dur_b * BEAT
        n = int(dur_s * SR)
        if pitch == REST or vel == 0:
            ts += n; continue
        f = _hz(pitch)
        for i in range(n):
            t   = (ts + i) / SR
            age = i / SR
            if waveform == 'str':
                # Detuned sawtooth pair
                w = (_saw(t, f*1.003) + _saw(t, f*0.997)) * 0.5
            elif waveform == 'bass':
                w = 0.7*_sine(t,f) + 0.3*_sine(t,f*2)
            else:
                w = _sine(t, f)
            env = _adsr(age, dur_s)
            idx = ts + i
            if idx < total:
                buf[idx] += w * env * vel
        ts += n
    return buf

def _mix(v1, v2, l1=0.6, l2=0.35):
    n = max(len(v1), len(v2))
    out = [0.0] * n
    for i in range(len(v1)): out[i] += v1[i] * l1
    for i in range(len(v2)): out[i] += v2[i] * l2
    return out

def _norm(buf):
    pk = max(abs(s) for s in buf) or 1.0
    return [s / pk * 0.9 for s in buf]

def _to_wav(buf, path):
    pcm = array.array('h', [max(-32767, min(32767, int(s * 32767))) for s in buf])
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

def synthesize_music(out_path):
    mel  = _render_voice(MELODY,    'str')
    bass = _render_voice(BASS_LINE, 'bass')
    mixed = _mix(mel, bass)
    mixed = _norm(mixed)
    _to_wav(mixed, out_path)
    return len(mixed) / SR

# ── Main keygen animation ─────────────────────────────────────────
def run_keygen():
    W, H = term_size()
    W = min(W, 160)
    H = min(H, 50)

    C.hide_cursor()
    C.clear_screen()

    try:
        _keygen_animation(W, H)
    except KeyboardInterrupt:
        pass
    finally:
        C.show_cursor()
        sys.stdout.write(C.RESET + '\n')
        sys.stdout.flush()

def _keygen_animation(W, H):
    # ── Phase 1: Matrix rain intro (3 seconds) ────────────────────
    rain = MatrixRain(W, H)
    sys.stdout.write(C.clear())
    sys.stdout.flush()

    t_start = time.time()
    RAIN_DURATION = 3.0

    while time.time() - t_start < RAIN_DURATION:
        dt = 0.05
        changes = rain.step(dt)
        rain.render_changes(changes)
        time.sleep(dt)

    # ── Phase 2: Draw keygen UI overlay ──────────────────────────
    # Dim the rain by overwriting with a semi-transparent overlay
    # Draw centered box
    BOX_W = min(80, W - 4)
    BOX_H = 36
    BOX_X = (W - BOX_W) // 2 + 1
    BOX_Y = (H - BOX_H) // 2 + 1

    def box_line(row, content='', color=C.BRIGHT_GREEN):
        pad = BOX_W - 2 - len(content)
        line = f'║{content}{" " * pad}║'
        sys.stdout.write(C.move(BOX_Y + row, BOX_X) +
                         C.BG_BLACK + color + line + C.RESET)

    def draw_box():
        top    = '╔' + '═' * (BOX_W - 2) + '╗'
        bottom = '╚' + '═' * (BOX_W - 2) + '╝'
        sys.stdout.write(C.move(BOX_Y, BOX_X) + C.BG_BLACK + C.BRIGHT_GREEN + top + C.RESET)
        for r in range(1, BOX_H):
            box_line(r)
        sys.stdout.write(C.move(BOX_Y + BOX_H, BOX_X) +
                         C.BG_BLACK + C.BRIGHT_GREEN + bottom + C.RESET)
        sys.stdout.flush()

    draw_box()

    # ── Title ─────────────────────────────────────────────────────
    title_lines = [
        ('', C.BRIGHT_GREEN),
        (' ██████╗ ██╗   ██╗███████╗███████╗███████╗██╗     ██╗', C.BRIGHT_GREEN),
        (' ██╔══██╗██║   ██║██╔════╝██╔════╝██╔════╝██║     ██║', C.BRIGHT_GREEN),
        (' ██████╔╝██║   ██║███████╗███████╗█████╗  ██║     ██║', C.BRIGHT_GREEN),
        (' ██╔══██╗██║   ██║╚════██║╚════██║██╔══╝  ██║     ██║', C.GREEN),
        (' ██║  ██║╚██████╔╝███████║███████║███████╗███████╗███████╗', C.GREEN),
        (' ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝╚══════╝', C.DIM + C.GREEN),
        ('', C.BRIGHT_GREEN),
        ('  C O O P E R   ·   K E Y G E N   M U S I C   E D I T I O N', C.BRIGHT_CYAN),
        ('       Beethoven Symphony No.5 Op.67 — Fate', C.CYAN),
        ('', C.BRIGHT_GREEN),
    ]

    for i, (txt, color) in enumerate(title_lines):
        # Truncate to fit box
        txt = txt[:BOX_W - 3]
        pad = BOX_W - 2 - len(txt)
        line = f'║{txt}{" " * pad}║'
        sys.stdout.write(C.move(BOX_Y + 1 + i, BOX_X) +
                         C.BG_BLACK + color + C.BOLD + line + C.RESET)
    sys.stdout.flush()
    time.sleep(0.3)

    # ── System info ───────────────────────────────────────────────
    row = BOX_Y + len(title_lines) + 1
    info_lines = [
        f' Target   : Beethoven Op.67 Fate Symphony',
        f' Engine   : Additive Synthesis + ADSR + Schroeder Reverb',
        f' Waveforms: Strings / Brass / Bass / Timpani',
        f' Output   : 44100 Hz · 16-bit PCM · Mono WAV',
        f' Author   : RussellCooper  [github.com/RussellCooper-DJZ]',
        f'',
    ]
    for txt in info_lines:
        txt = txt[:BOX_W - 3]
        pad = BOX_W - 2 - len(txt)
        sys.stdout.write(C.move(row, BOX_X) +
                         C.BG_BLACK + C.BRIGHT_CYAN + f'║{txt}{" " * pad}║' + C.RESET)
        row += 1
        sys.stdout.flush()
        time.sleep(0.08)

    # ── Separator ─────────────────────────────────────────────────
    sep = '╠' + '═' * (BOX_W - 2) + '╣'
    sys.stdout.write(C.move(row, BOX_X) + C.BG_BLACK + C.BRIGHT_GREEN + sep + C.RESET)
    row += 1
    sys.stdout.flush()
    time.sleep(0.1)

    # ── Hex dump scrolling (cracking effect) ─────────────────────
    hex_label = ' Analyzing binary patterns...'
    hex_label = hex_label[:BOX_W - 3]
    pad = BOX_W - 2 - len(hex_label)
    sys.stdout.write(C.move(row, BOX_X) +
                     C.BG_BLACK + C.YELLOW + f'║{hex_label}{" " * pad}║' + C.RESET)
    row += 1
    sys.stdout.flush()
    time.sleep(0.2)

    HEX_ROWS = 5
    hex_start_row = row
    for _ in range(HEX_ROWS):
        sys.stdout.write(C.move(row, BOX_X) + C.BG_BLACK + C.GREEN + '║' +
                         ' ' * (BOX_W - 2) + '║' + C.RESET)
        row += 1

    # Scroll hex dump
    for frame in range(30):
        for hr in range(HEX_ROWS):
            hexline = random_hex_line(BOX_W - 4)[:BOX_W - 4]
            pad = BOX_W - 2 - len(hexline) - 1
            color = C.BRIGHT_GREEN if frame > 20 else C.GREEN
            sys.stdout.write(
                C.move(hex_start_row + hr, BOX_X) +
                C.BG_BLACK + color +
                f'║ {hexline}{" " * pad}║' + C.RESET
            )
        sys.stdout.flush()
        time.sleep(0.06)

    # ── Progress bars ─────────────────────────────────────────────
    sep2 = '╠' + '═' * (BOX_W - 2) + '╣'
    sys.stdout.write(C.move(row, BOX_X) + C.BG_BLACK + C.BRIGHT_GREEN + sep2 + C.RESET)
    row += 1
    sys.stdout.flush()

    stages = [
        ('Decoding score data',       C.BRIGHT_GREEN,  0.04),
        ('Synthesizing strings',      C.BRIGHT_GREEN,  0.03),
        ('Synthesizing brass',        C.BRIGHT_GREEN,  0.03),
        ('Synthesizing bass',         C.BRIGHT_GREEN,  0.03),
        ('Applying ADSR envelopes',   C.BRIGHT_CYAN,   0.02),
        ('Schroeder reverb',          C.BRIGHT_CYAN,   0.02),
        ('Mixing voices',             C.BRIGHT_YELLOW, 0.02),
        ('Peak normalize + limiter',  C.BRIGHT_YELLOW, 0.02),
        ('Encoding 16-bit PCM',       C.BRIGHT_WHITE,  0.02),
        ('Writing WAV output',        C.BRIGHT_WHITE,  0.03),
    ]

    prog_rows = []
    for label, color, _ in stages:
        txt = f' {label}'[:BOX_W - 3]
        pad = BOX_W - 2 - len(txt)
        sys.stdout.write(C.move(row, BOX_X) +
                         C.BG_BLACK + C.DIM + C.GREEN +
                         f'║{txt}{" " * pad}║' + C.RESET)
        prog_rows.append(row)
        row += 1
        sys.stdout.flush()

    # Animate each progress bar
    BAR_W = 20
    for si, (label, color, speed) in enumerate(stages):
        pct = 0.0
        while pct < 1.0:
            pct = min(1.0, pct + random.uniform(0.05, 0.18))
            filled = int(BAR_W * pct)
            bar = '█' * filled + '░' * (BAR_W - filled)
            pct_str = f'{pct*100:5.1f}%'
            txt = f' {label:<28} [{color}{bar}{C.RESET}{C.BG_BLACK}{C.BRIGHT_GREEN}] {pct_str}'
            txt_plain = f' {label:<28} [{bar}] {pct_str}'
            pad = BOX_W - 2 - len(txt_plain)
            sys.stdout.write(
                C.move(prog_rows[si], BOX_X) +
                C.BG_BLACK + C.BRIGHT_GREEN +
                f'║ {label:<28} [{color}{C.BOLD}{bar}{C.RESET}{C.BG_BLACK}{C.BRIGHT_GREEN}]'
                f' {pct_str}{" " * max(0, pad - 1)}║' + C.RESET
            )
            sys.stdout.flush()
            time.sleep(speed * random.uniform(0.5, 1.5))

        # Done checkmark
        sys.stdout.write(
            C.move(prog_rows[si], BOX_X) +
            C.BG_BLACK + C.BRIGHT_GREEN +
            f'║ {label:<28} [{color}{C.BOLD}{"█" * BAR_W}{C.RESET}{C.BG_BLACK}{C.BRIGHT_GREEN}]'
            f' 100.0% ✓{" " * max(0, BOX_W - 2 - len(label) - BAR_W - 18)}║' + C.RESET
        )
        sys.stdout.flush()
        time.sleep(0.05)

    # ── Synthesize actual music in background ─────────────────────
    wav_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fate_symphony.wav')
    music_done = threading.Event()
    music_duration = [0.0]

    def _synth():
        music_duration[0] = synthesize_music(wav_path)
        music_done.set()

    synth_thread = threading.Thread(target=_synth, daemon=True)
    synth_thread.start()

    # Wait for synthesis with spinner
    sep3 = '╠' + '═' * (BOX_W - 2) + '╣'
    sys.stdout.write(C.move(row, BOX_X) + C.BG_BLACK + C.BRIGHT_GREEN + sep3 + C.RESET)
    row += 1
    spin_row = row
    spinner = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
    si = 0
    while not music_done.is_set():
        sp = spinner[si % len(spinner)]
        txt = f' {sp} Synthesizing audio from pure mathematics...'[:BOX_W - 3]
        pad = BOX_W - 2 - len(txt)
        sys.stdout.write(C.move(spin_row, BOX_X) +
                         C.BG_BLACK + C.BRIGHT_CYAN +
                         f'║{txt}{" " * pad}║' + C.RESET)
        sys.stdout.flush()
        si += 1
        time.sleep(0.1)

    dur = music_duration[0]
    done_txt = f' ✓ Synthesis complete!  Duration: {dur:.1f}s  →  {wav_path}'
    done_txt = done_txt[:BOX_W - 3]
    pad = BOX_W - 2 - len(done_txt)
    sys.stdout.write(C.move(spin_row, BOX_X) +
                     C.BG_BLACK + C.BRIGHT_GREEN + C.BOLD +
                     f'║{done_txt}{" " * pad}║' + C.RESET)
    row += 1
    sys.stdout.flush()
    time.sleep(0.3)

    # ── Serial number reveal ──────────────────────────────────────
    sep4 = '╠' + '═' * (BOX_W - 2) + '╣'
    sys.stdout.write(C.move(row, BOX_X) + C.BG_BLACK + C.BRIGHT_GREEN + sep4 + C.RESET)
    row += 1

    serial = gen_serial()
    hash_  = gen_hash()

    serial_lines = [
        ('', C.BRIGHT_GREEN),
        (f'  Serial  :  {serial}', C.BRIGHT_YELLOW),
        (f'  Hash    :  {hash_[:16]}...', C.YELLOW),
        (f'  License :  RussellCooper — Embedded Systems Engineer', C.BRIGHT_CYAN),
        ('', C.BRIGHT_GREEN),
    ]

    # Scramble reveal effect
    for li, (txt, color) in enumerate(serial_lines):
        if not txt.strip():
            txt_disp = txt[:BOX_W - 3]
            pad = BOX_W - 2 - len(txt_disp)
            sys.stdout.write(C.move(row + li, BOX_X) +
                             C.BG_BLACK + C.BRIGHT_GREEN +
                             f'║{txt_disp}{" " * pad}║' + C.RESET)
            continue
        # Scramble animation
        for frame in range(12):
            scrambled = ''
            for ch in txt:
                if frame > 8 or ch == ' ' or ch == ':':
                    scrambled += ch
                elif random.random() < frame / 10:
                    scrambled += ch
                else:
                    scrambled += random.choice('0123456789ABCDEF!@#$%^&*')
            disp = scrambled[:BOX_W - 3]
            pad = BOX_W - 2 - len(disp)
            sys.stdout.write(C.move(row + li, BOX_X) +
                             C.BG_BLACK + color + C.BOLD +
                             f'║{disp}{" " * pad}║' + C.RESET)
            sys.stdout.flush()
            time.sleep(0.04)

    row += len(serial_lines)

    # ── REGISTERED banner ─────────────────────────────────────────
    sep5 = '╠' + '═' * (BOX_W - 2) + '╣'
    sys.stdout.write(C.move(row, BOX_X) + C.BG_BLACK + C.BRIGHT_GREEN + sep5 + C.RESET)
    row += 1

    reg_lines = [
        r"  ██████╗ ███████╗ ██████╗ ██╗███████╗████████╗███████╗██████╗ ██╗",
        r"  ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║",
        r"  ██████╔╝█████╗  ██║  ███╗██║███████╗   ██║   █████╗  ██████╔╝██║",
        r"  ██╔══██╗██╔══╝  ██║   ██║██║╚════██║   ██║   ██╔══╝  ██╔══██╗╚═╝",
        r"  ██║  ██║███████╗╚██████╔╝██║███████║   ██║   ███████╗██║  ██║██╗",
        r"  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝",
    ]

    # Flash effect
    for flash in range(4):
        color = C.BRIGHT_GREEN if flash % 2 == 0 else C.BRIGHT_YELLOW
        for li, txt in enumerate(reg_lines):
            txt = txt[:BOX_W - 3]
            pad = BOX_W - 2 - len(txt)
            sys.stdout.write(C.move(row + li, BOX_X) +
                             C.BG_BLACK + color + C.BOLD +
                             f'║{txt}{" " * pad}║' + C.RESET)
        sys.stdout.flush()
        time.sleep(0.15)

    row += len(reg_lines)

    # Bottom
    footer = f'  ♪  fate_symphony.wav  ·  Play: aplay fate_symphony.wav  ♪'
    footer = footer[:BOX_W - 3]
    pad = BOX_W - 2 - len(footer)
    sys.stdout.write(C.move(row, BOX_X) +
                     C.BG_BLACK + C.BRIGHT_CYAN + C.BOLD +
                     f'║{footer}{" " * pad}║' + C.RESET)
    row += 1

    bottom = '╚' + '═' * (BOX_W - 2) + '╝'
    sys.stdout.write(C.move(row, BOX_X) + C.BG_BLACK + C.BRIGHT_GREEN + bottom + C.RESET)
    sys.stdout.flush()

    # ── Continue matrix rain in background ────────────────────────
    sys.stdout.write(C.move(H - 1, 1))
    sys.stdout.flush()
    time.sleep(0.5)

    # Rain continues around the box for 3 more seconds
    t_end = time.time() + 3.0
    while time.time() < t_end:
        dt = 0.05
        changes = rain.step(dt)
        # Only render rain outside the box
        filtered = [
            (r, c, ch, intensity)
            for (r, c, ch, intensity) in changes
            if not (BOX_Y - 1 <= r + 1 <= BOX_Y + BOX_H + 1 and
                    BOX_X - 1 <= c + 1 <= BOX_X + BOX_W + 1)
        ]
        rain.render_changes(filtered)
        time.sleep(dt)

    sys.stdout.write(C.move(H, 1) + C.RESET + '\n')
    sys.stdout.flush()

# ── Entry point ───────────────────────────────────────────────────
if __name__ == '__main__':
    run_keygen()
